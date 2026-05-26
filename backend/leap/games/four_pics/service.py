"""Four Pics, One Lie — session lifecycle and scoring orchestration."""

import random
from datetime import datetime
from typing import Callable, Dict, List, Optional, Set

from sqlalchemy.ext.asyncio import AsyncSession

from leap.core.common.time import utc_now
from leap.core.context_manager import ContextManager
from leap.dao.four_pics_question_attempt_dao import FourPicsQuestionAttemptDAO
from leap.dao.four_pics_question_dao import FourPicsQuestionDAO
from leap.dao.game_session_dao import GameSessionDAO
from leap.games.four_pics.scoring import clamp_elapsed_ms, compute_question_score
from leap.service.exceptions import (
    InvalidQuestionIdException,
    NoQuestionsAvailableException,
    QuestionAlreadyAnsweredException,
    SessionAlreadyCompletedException,
    SessionNotFoundException,
)
from leap.types.four_pics import (
    FourPicsAnswerPayload,
    FourPicsPlayPayload,
    FourPicsQuestionAttemptDTO,
    FourPicsQuestionDTO,
    FourPicsQuestionStateDTO,
    FourPicsResultDTO,
    FourPicsResultQuestionDTO,
)
from leap.types.game import GameSessionDTO, GameSessionStatus


class FourPicsService:
    """Handles Four Pics sessions, answers, and question progression."""

    def __init__(
        self,
        ctx: ContextManager,
        game_session_dao: GameSessionDAO,
        attempt_dao: FourPicsQuestionAttemptDAO,
        question_dao: FourPicsQuestionDAO,
        *,
        clock: Optional[Callable[[], datetime]] = None,
    ) -> None:
        self.ctx = ctx
        self.game_session_dao = game_session_dao
        self.attempt_dao = attempt_dao
        self.question_dao = question_dao
        self._clock = clock or utc_now
        self._questions: Dict[str, FourPicsQuestionDTO] = {}

    async def initialize(self, session: AsyncSession) -> None:
        """Warm the in-memory question cache from the database."""
        questions = await self.question_dao.get_all(session)
        self._questions = {q.id: q for q in questions}

    def _now(self) -> datetime:
        return self._clock()

    def _pool_size(self) -> int:
        return len(self._questions)

    def _terminal_question_ids(self, attempts: List[FourPicsQuestionAttemptDTO]) -> Set[str]:
        return {a.question_id for a in attempts if a.status in ("correct", "wrong")}

    def _session_score(self, attempts: List[FourPicsQuestionAttemptDTO]) -> int:
        return sum(a.score or 0 for a in attempts if a.status in ("correct", "wrong"))

    def _pick_next_question(self, attempted_ids: Set[str]) -> Optional[FourPicsQuestionDTO]:
        remaining = [q for q in self._questions.values() if q.id not in attempted_ids]
        if not remaining:
            return None
        return random.choice(remaining)

    def _question_state(
        self,
        question: FourPicsQuestionDTO,
        *,
        question_number: int,
        started_at: datetime,
    ) -> FourPicsQuestionStateDTO:
        return FourPicsQuestionStateDTO(
            question_id=question.id,
            question_number=question_number,
            total_questions=self._pool_size(),
            image_paths=list(question.image_paths),
            status="active",
            started_at=started_at,
        )

    def _build_result(
        self,
        attempts: List[FourPicsQuestionAttemptDTO],
        *,
        session_score: int,
    ) -> FourPicsResultDTO:
        terminal = [a for a in attempts if a.status in ("correct", "wrong")]
        questions_out: List[FourPicsResultQuestionDTO] = []
        for attempt in terminal:
            questions_out.append(
                FourPicsResultQuestionDTO(
                    question_id=attempt.question_id,
                    status=attempt.status,
                    score=attempt.score or 0,
                    time_bonus=attempt.time_bonus or 0,
                )
            )
        correct_count = sum(1 for a in terminal if a.status == "correct")
        wrong_count = sum(1 for a in terminal if a.status == "wrong")
        return FourPicsResultDTO(
            score=session_score,
            questions_correct=correct_count,
            questions_wrong=wrong_count,
            questions_not_reached=0,
            questions=questions_out,
        )

    def _build_abandon_result(
        self,
        attempts: List[FourPicsQuestionAttemptDTO],
        *,
        session_score: int,
    ) -> FourPicsResultDTO:
        attempt_by_question = {a.question_id: a for a in attempts}
        questions_out: List[FourPicsResultQuestionDTO] = []
        correct_count = 0
        wrong_count = 0
        not_reached_count = 0

        for question_id in sorted(self._questions.keys()):
            attempt = attempt_by_question.get(question_id)
            if attempt is None:
                status = "not_reached"
                score = 0
                time_bonus = 0
                not_reached_count += 1
            elif attempt.status == "correct":
                status = "correct"
                score = attempt.score or 0
                time_bonus = attempt.time_bonus or 0
                correct_count += 1
            else:
                status = "wrong"
                score = attempt.score or 0
                time_bonus = attempt.time_bonus or 0
                wrong_count += 1

            questions_out.append(
                FourPicsResultQuestionDTO(
                    question_id=question_id,
                    status=status,
                    score=score,
                    time_bonus=time_bonus,
                )
            )

        return FourPicsResultDTO(
            score=session_score,
            questions_correct=correct_count,
            questions_wrong=wrong_count,
            questions_not_reached=not_reached_count,
            questions=questions_out,
        )

    async def _serve_next_question(
        self,
        session: AsyncSession,
        game_session: GameSessionDTO,
        attempts: List[FourPicsQuestionAttemptDTO],
    ) -> FourPicsPlayPayload:
        attempted_ids = self._terminal_question_ids(attempts)
        active = await self.attempt_dao.get_active_for_session(session, game_session.id)
        if active is not None:
            question = self._questions[active.question_id]
            question_number = len(attempted_ids) + 1
            return FourPicsPlayPayload(
                session_status=GameSessionStatus.ACTIVE.value,
                session_score=self._session_score(attempts),
                question=self._question_state(
                    question,
                    question_number=question_number,
                    started_at=active.started_at,
                ),
            )

        if len(attempted_ids) >= self._pool_size():
            score = self._session_score(attempts)
            return FourPicsPlayPayload(
                session_status=GameSessionStatus.COMPLETED.value,
                session_score=score,
                question=None,
                result=self._build_result(attempts, session_score=score),
            )

        next_q = self._pick_next_question(attempted_ids)
        if next_q is None:
            raise NoQuestionsAvailableException()

        started_at = self._now()
        await self.attempt_dao.create(
            session,
            game_session.id,
            next_q.id,
            started_at,
        )
        question_number = len(attempted_ids) + 1
        return FourPicsPlayPayload(
            session_status=GameSessionStatus.ACTIVE.value,
            session_score=self._session_score(attempts),
            question=self._question_state(
                next_q,
                question_number=question_number,
                started_at=started_at,
            ),
        )

    async def play(self, player_id: str) -> FourPicsPlayPayload:
        async with self.ctx.session() as session:
            pool_size = self._pool_size()
            game_session = await self.game_session_dao.get_by_player_and_game(
                session, player_id, "four_pics"
            )

            if game_session is None:
                if pool_size == 0:
                    raise NoQuestionsAvailableException()
                created = await self.game_session_dao.create(session, player_id, "four_pics")
                return await self._serve_next_question(session, created, [])

            if game_session.status != GameSessionStatus.ACTIVE:
                attempts = await self.attempt_dao.get_all_for_session(session, game_session.id)
                score = int(game_session.score or self._session_score(attempts))
                return FourPicsPlayPayload(
                    session_status=game_session.status.value,
                    session_score=score,
                    question=None,
                    result=self._build_result(attempts, session_score=score),
                )

            attempts = await self.attempt_dao.get_all_for_session(session, game_session.id)
            return await self._serve_next_question(session, game_session, attempts)

    async def submit_answer(
        self,
        player_id: str,
        question_id: str,
        selected_index: int,
        time_ms: int,
    ) -> FourPicsAnswerPayload:
        async with self.ctx.session() as session:
            game_session = await self.game_session_dao.get_by_player_and_game(
                session, player_id, "four_pics"
            )
            if game_session is None:
                raise SessionNotFoundException(player_id, "four_pics")
            if game_session.status != GameSessionStatus.ACTIVE:
                raise SessionAlreadyCompletedException(game_session.id, game_session.status.value)

            if question_id not in self._questions:
                raise InvalidQuestionIdException(question_id)

            attempts = await self.attempt_dao.get_all_for_session(session, game_session.id)
            for attempt in attempts:
                if attempt.question_id == question_id and attempt.status in ("correct", "wrong"):
                    raise QuestionAlreadyAnsweredException(question_id)

            active = await self.attempt_dao.get_active_for_session(session, game_session.id)
            if active is None or active.question_id != question_id:
                raise InvalidQuestionIdException(question_id)

            question = self._questions[question_id]
            now = self._now()
            server_elapsed_ms = int((now - active.started_at).total_seconds() * 1000)
            elapsed_ms = clamp_elapsed_ms(time_ms, server_elapsed_ms)
            correct = selected_index == question.odd_one_out_index
            score, time_bonus = compute_question_score(correct, elapsed_ms)
            terminal_status = "correct" if correct else "wrong"

            await self.attempt_dao.update_status_and_score(
                session,
                active.id,
                status=terminal_status,
                selected_index=selected_index,
                score=score,
                time_bonus=time_bonus,
                time_ms=elapsed_ms,
                completed_at=now,
            )

            updated_attempts = await self.attempt_dao.get_all_for_session(session, game_session.id)
            session_score = self._session_score(updated_attempts)
            attempted_ids = self._terminal_question_ids(updated_attempts)

            if len(attempted_ids) >= self._pool_size():
                updated_session = await self.game_session_dao.update_status(
                    session,
                    game_session.id,
                    GameSessionStatus.COMPLETED,
                    score=session_score,
                )
                final_score = int(updated_session.score or session_score)
                result = self._build_result(updated_attempts, session_score=final_score)
                return FourPicsAnswerPayload(
                    correct=correct,
                    score=score,
                    time_bonus=time_bonus,
                    session_status=GameSessionStatus.COMPLETED.value,
                    session_score=final_score,
                    question=None,
                    result=result,
                )

            next_q = self._pick_next_question(attempted_ids)
            if next_q is None:
                raise NoQuestionsAvailableException()

            started_at = self._now()
            await self.attempt_dao.create(
                session,
                game_session.id,
                next_q.id,
                started_at,
            )
            question_number = len(attempted_ids) + 1
            return FourPicsAnswerPayload(
                correct=correct,
                score=score,
                time_bonus=time_bonus,
                session_status=GameSessionStatus.ACTIVE.value,
                session_score=session_score,
                question=self._question_state(
                    next_q,
                    question_number=question_number,
                    started_at=started_at,
                ),
                result=None,
            )

    async def abandon(self, player_id: str) -> FourPicsResultDTO:
        async with self.ctx.session() as session:
            game_session = await self.game_session_dao.get_by_player_and_game(
                session, player_id, "four_pics"
            )
            if game_session is None:
                raise SessionNotFoundException(player_id, "four_pics")
            if game_session.status != GameSessionStatus.ACTIVE:
                raise SessionAlreadyCompletedException(game_session.id, game_session.status.value)

            now = self._now()
            active = await self.attempt_dao.get_active_for_session(session, game_session.id)
            if active is not None:
                await self.attempt_dao.close_active_on_abandon(
                    session,
                    active.id,
                    completed_at=now,
                )

            attempts = await self.attempt_dao.get_all_for_session(session, game_session.id)
            session_score = self._session_score(attempts)
            updated = await self.game_session_dao.update_status(
                session,
                game_session.id,
                GameSessionStatus.ABANDONED,
                score=session_score,
            )
            final_score = int(updated.score or session_score)
            return self._build_abandon_result(attempts, session_score=final_score)
