"""Rapid Fire Quiz — session lifecycle and scoring orchestration."""

import random
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from leap.core.common.time import utc_now
from leap.core.context_manager import ContextManager
from leap.dao.game_session_dao import GameSessionDAO
from leap.dao.rapid_fire_answer_dao import RapidFireAnswerDAO
from leap.dao.rapid_fire_question_dao import RapidFireQuestionDAO
from leap.games.rapid_fire.scoring import (
    clamp_rapid_fire_time_ms,
    compute_rapid_fire_score,
)
from leap.service.exceptions import (
    InvalidQuestionIdException,
    NoQuestionsAvailableException,
    QuestionAlreadyAnsweredException,
    SessionAlreadyCompletedException,
    SessionAlreadyExistsException,
    SessionNotFoundException,
)
from leap.types.game import GameSessionDTO, GameSessionStatus
from leap.types.rapid_fire import (
    RapidFireAnswerDTO,
    RapidFireAnswerPayload,
    RapidFirePlayPayload,
    RapidFireQuestionDTO,
    RapidFireResultDTO,
)


class RapidFireService:
    """Handles Rapid Fire Quiz sessions, answers, and abandon flows."""

    def __init__(
        self,
        ctx: ContextManager,
        game_session_dao: GameSessionDAO,
        rapid_fire_answer_dao: RapidFireAnswerDAO,
        rapid_fire_question_dao: RapidFireQuestionDAO,
    ) -> None:
        self.ctx = ctx
        self.game_session_dao = game_session_dao
        self.rapid_fire_answer_dao = rapid_fire_answer_dao
        self.rapid_fire_question_dao = rapid_fire_question_dao
        self._questions: Dict[str, RapidFireQuestionDTO] = {}

    async def initialize(self, session: AsyncSession) -> None:
        """Warm the in-memory cache from the database (called once from lifespan)."""
        questions = await self.rapid_fire_question_dao.get_all(session)
        self._questions = {q.id: q for q in questions}

    def _pick_next_question(self, asked_ids: List[str]) -> Optional[RapidFireQuestionDTO]:
        asked = set(asked_ids)
        remaining = [q for q in self._questions.values() if q.id not in asked]
        if not remaining:
            return None
        return random.choice(remaining)

    def _build_result(self, game_session: GameSessionDTO, answers: List[RapidFireAnswerDTO]) -> RapidFireResultDTO:
        score = game_session.score if game_session.score is not None else 0
        correct_count = sum(1 for a in answers if a.correct)
        wrong_count = sum(1 for a in answers if not a.correct and not a.skipped)
        skipped_count = sum(1 for a in answers if a.skipped)
        elapsed = 0.0
        if game_session.completed_at is not None:
            elapsed = max(
                0.0,
                (game_session.completed_at - game_session.started_at).total_seconds(),
            )
        return RapidFireResultDTO(
            score=score,
            correct_count=correct_count,
            wrong_count=wrong_count,
            skipped_count=skipped_count,
            time_taken_seconds=elapsed,
        )

    async def play(self, player_id: str) -> RapidFirePlayPayload:
        async with self.ctx.session() as session:
            game_session = await self.game_session_dao.get_by_player_and_game(
                session, player_id, "rapid_fire"
            )

            pool_size = len(self._questions)

            if game_session is None:
                if pool_size == 0:
                    raise NoQuestionsAvailableException()
                created = await self.game_session_dao.create(session, player_id, "rapid_fire")
                question = self._pick_next_question([])
                if question is None:
                    raise NoQuestionsAvailableException()
                return RapidFirePlayPayload(
                    status=GameSessionStatus.ACTIVE.value,
                    game_session_id=created.id,
                    questions_answered=0,
                    questions_total=pool_size,
                    question=question,
                )

            if game_session.status != GameSessionStatus.ACTIVE:
                answers = await self.rapid_fire_answer_dao.get_all_for_session(session, game_session.id)
                result = self._build_result(game_session, answers)
                return RapidFirePlayPayload(status=game_session.status.value, result=result)

            asked_ids = await self.rapid_fire_answer_dao.get_asked_question_ids(session, game_session.id)
            if len(asked_ids) == 0:
                raise SessionAlreadyExistsException(player_id, "rapid_fire")

            question = self._pick_next_question(asked_ids)
            if question is None:
                raise NoQuestionsAvailableException()
            return RapidFirePlayPayload(
                status=GameSessionStatus.ACTIVE.value,
                game_session_id=game_session.id,
                questions_answered=len(asked_ids),
                questions_total=pool_size,
                question=question,
            )

    async def submit_answer(
        self,
        player_id: str,
        question_id: str,
        selected_option: Optional[int],
        time_ms: int,
    ) -> RapidFireAnswerPayload:
        async with self.ctx.session() as session:
            game_session = await self.game_session_dao.get_by_player_and_game(
                session, player_id, "rapid_fire"
            )
            if game_session is None:
                raise SessionNotFoundException(player_id, "rapid_fire")
            if game_session.status != GameSessionStatus.ACTIVE:
                raise SessionAlreadyCompletedException(game_session.id, game_session.status.value)

            if question_id not in self._questions:
                raise InvalidQuestionIdException(question_id)

            question = self._questions[question_id]
            answers = await self.rapid_fire_answer_dao.get_all_for_session(session, game_session.id)
            asked_ids = {a.question_id for a in answers}
            if question_id in asked_ids:
                raise QuestionAlreadyAnsweredException(question_id)

            skipped = selected_option is None
            correct = bool(not skipped and selected_option == question.correct_option_index)
            effective_time_ms = clamp_rapid_fire_time_ms(
                time_ms, question.time_limit_ms
            )

            await self.rapid_fire_answer_dao.create(
                session,
                game_session.id,
                question_id,
                correct,
                skipped,
                selected_option,
                effective_time_ms,
            )

            current_answer = RapidFireAnswerDTO(
                id="pending",
                game_session_id=game_session.id,
                question_id=question_id,
                correct=correct,
                skipped=skipped,
                selected_option=selected_option,
                time_ms=effective_time_ms,
                answered_at=utc_now(),
            )
            all_answers = answers + [current_answer]
            current_score = compute_rapid_fire_score(all_answers, self._questions)

            new_asked_ids = asked_ids | {question_id}
            total_pool = len(self._questions)
            questions_answered = len(new_asked_ids)
            questions_remaining = total_pool - questions_answered

            correct_answer_text = question.options[question.correct_option_index - 1]

            if questions_answered == total_pool:
                updated = await self.game_session_dao.update_status(
                    session,
                    game_session.id,
                    GameSessionStatus.COMPLETED,
                    score=current_score,
                )
                result = self._build_result(updated, all_answers)
                return RapidFireAnswerPayload(
                    correct=correct,
                    correct_option=question.correct_option_index,
                    correct_answer_text=correct_answer_text,
                    current_score=current_score,
                    questions_answered=questions_answered,
                    questions_remaining=0,
                    next_question=None,
                    result=result,
                )

            next_q = self._pick_next_question(list(new_asked_ids))
            return RapidFireAnswerPayload(
                correct=correct,
                correct_option=question.correct_option_index,
                correct_answer_text=correct_answer_text,
                current_score=current_score,
                questions_answered=questions_answered,
                questions_remaining=questions_remaining,
                next_question=next_q,
                result=None,
            )

    async def abandon(self, player_id: str) -> RapidFireResultDTO:
        async with self.ctx.session() as session:
            game_session = await self.game_session_dao.get_by_player_and_game(
                session, player_id, "rapid_fire"
            )
            if game_session is None:
                raise SessionNotFoundException(player_id, "rapid_fire")
            if game_session.status != GameSessionStatus.ACTIVE:
                raise SessionAlreadyCompletedException(game_session.id, game_session.status.value)

            answers = await self.rapid_fire_answer_dao.get_all_for_session(session, game_session.id)
            partial_score = compute_rapid_fire_score(answers, self._questions)
            updated = await self.game_session_dao.update_status(
                session,
                game_session.id,
                GameSessionStatus.ABANDONED,
                score=partial_score,
            )
            return self._build_result(updated, answers)
