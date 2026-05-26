"""Picture Illustration — session lifecycle, answer matching, and scoring orchestration."""

import random
from typing import Dict, List, Optional, Set

from sqlalchemy.ext.asyncio import AsyncSession

from leap.config.constants import PICTURE_TIME_LIMIT_MS
from leap.core.common.time import utc_now
from leap.core.context_manager import ContextManager
from leap.dao.game_session_dao import GameSessionDAO
from leap.dao.picture_puzzle_attempt_dao import PicturePuzzleAttemptDAO
from leap.dao.picture_puzzle_dao import PicturePuzzleDAO
from leap.games.picture.scoring import compute_time_bonus, compute_total_score, normalize_answer, score_per_puzzle
from leap.service.exceptions import (
    AlreadyResolvedException,
    InvalidPuzzleIdException,
    NoPicturePuzzlesAvailableException,
    SessionAlreadyCompletedException,
    SessionNotFoundException,
)
from leap.types.game import GameSessionStatus
from leap.types.picture import (
    PictureAnswerPayload,
    PictureDisplayedPuzzleDTO,
    PicturePlayPayload,
    PicturePuzzleAttemptDTO,
    PicturePuzzleDTO,
    PictureResultDTO,
    PictureResultPuzzleDTO,
)


class PictureService:
    """Handles Picture Illustration sessions and answer submissions."""

    def __init__(
        self,
        ctx: ContextManager,
        game_session_dao: GameSessionDAO,
        puzzle_dao: PicturePuzzleDAO,
        attempt_dao: PicturePuzzleAttemptDAO,
    ) -> None:
        self.ctx = ctx
        self.game_session_dao = game_session_dao
        self.puzzle_dao = puzzle_dao
        self.attempt_dao = attempt_dao
        self._puzzles: Dict[str, PicturePuzzleDTO] = {}

    async def initialize(self, session: AsyncSession) -> None:
        """Warm puzzle cache from the database (lifespan startup)."""
        puzzles = await self.puzzle_dao.get_all(session)
        self._puzzles = {p.id: p for p in puzzles}

    def _pool_size(self) -> int:
        return len(self._puzzles)

    def _answered_correctly_ids(self, attempts: List[PicturePuzzleAttemptDTO]) -> Set[str]:
        return {a.puzzle_id for a in attempts if a.correct}

    def _terminal_blocked_ids(self, attempts: List[PicturePuzzleAttemptDTO]) -> Set[str]:
        return {a.puzzle_id for a in attempts if a.correct or a.skipped}

    def _submission_matches(self, puzzle: PicturePuzzleDTO, submitted_answer: str) -> bool:
        normalized_submission = normalize_answer(submitted_answer)
        for accepted in puzzle.accepted_answers:
            if normalize_answer(accepted) == normalized_submission:
                return True
        return False

    def _attempt_count_for_resolution(self, attempts: List[PicturePuzzleAttemptDTO], puzzle_id: str) -> int:
        per_puzzle = [a for a in attempts if a.puzzle_id == puzzle_id]
        for i, attempt in enumerate(per_puzzle, start=1):
            if attempt.correct:
                return i
        return len(per_puzzle)

    def _score_for_puzzle_if_solved(self, attempts: List[PicturePuzzleAttemptDTO], puzzle_id: str) -> int:
        per_puzzle = [a for a in attempts if a.puzzle_id == puzzle_id]
        for i, attempt in enumerate(per_puzzle, start=1):
            if attempt.correct:
                return score_per_puzzle(i)
        return 0

    def _accuracy_total(self, attempts: List[PicturePuzzleAttemptDTO]) -> int:
        scores: List[int] = []
        for puzzle_id in self._puzzles.keys():
            earned = self._score_for_puzzle_if_solved(attempts, puzzle_id)
            if earned:
                scores.append(earned)
        return sum(scores)

    def _session_expired(self, started_at, now) -> bool:
        elapsed_ms = int((now - started_at).total_seconds() * 1000)
        return elapsed_ms > PICTURE_TIME_LIMIT_MS

    def _pick_unresolved_puzzle(self, blocked_ids: Set[str]) -> Optional[PicturePuzzleDTO]:
        remaining = [p for p in self._puzzles.values() if p.id not in blocked_ids]
        if not remaining:
            return None
        return random.choice(remaining)

    def _wrap_puzzle(self, puzzle: PicturePuzzleDTO, puzzles_answered: int) -> PictureDisplayedPuzzleDTO:
        return PictureDisplayedPuzzleDTO(
            id=puzzle.id,
            image_filename=puzzle.image_filename,
            puzzles_answered=puzzles_answered,
            puzzles_total=self._pool_size(),
        )

    def _build_result(
        self,
        attempts: List[PicturePuzzleAttemptDTO],
        *,
        accuracy_score: int,
        time_bonus: int,
        time_remaining_seconds: int,
    ) -> PictureResultDTO:
        total = compute_total_score(accuracy_score, time_bonus)
        puzzles_out: List[PictureResultPuzzleDTO] = []
        for puzzle_id in sorted(self._puzzles.keys()):
            puzzle = self._puzzles[puzzle_id]
            per_puzzle = [a for a in attempts if a.puzzle_id == puzzle_id]
            if any(a.correct for a in per_puzzle):
                status = "correct"
                earned = self._score_for_puzzle_if_solved(attempts, puzzle_id)
            elif any(a.skipped for a in per_puzzle):
                status = "skipped"
                earned = 0
            else:
                status = "not_reached"
                earned = 0
            puzzles_out.append(
                PictureResultPuzzleDTO(
                    puzzle_id=puzzle_id,
                    image_filename=puzzle.image_filename,
                    status=status,
                    score_earned=earned,
                )
            )
        return PictureResultDTO(
            score=total,
            accuracy_score=accuracy_score,
            time_bonus=time_bonus,
            time_remaining_seconds=time_remaining_seconds,
            puzzles=puzzles_out,
        )

    def _result_from_stored_session(
        self, attempts: List[PicturePuzzleAttemptDTO], stored_score: int
    ) -> PictureResultDTO:
        """Rebuild a result for completed/abandoned sessions using persisted total score."""
        accuracy_score = self._accuracy_total(attempts)
        time_bonus = max(0, stored_score - accuracy_score)
        time_remaining_seconds = time_bonus
        return self._build_result(
            attempts,
            accuracy_score=accuracy_score,
            time_bonus=time_bonus,
            time_remaining_seconds=time_remaining_seconds,
        )

    async def play(self, player_id: str) -> PicturePlayPayload:
        pool = self._pool_size()
        async with self.ctx.session() as session:
            game_session = await self.game_session_dao.get_by_player_and_game(session, player_id, "picture")

            if game_session is None:
                if pool == 0:
                    raise NoPicturePuzzlesAvailableException()
                created = await self.game_session_dao.create(session, player_id, "picture")
                pick = self._pick_unresolved_puzzle(set())
                if pick is None:
                    raise NoPicturePuzzlesAvailableException()
                return PicturePlayPayload(
                    status=GameSessionStatus.ACTIVE.value,
                    game_session_id=created.id,
                    puzzles_answered=0,
                    puzzles_total=pool,
                    session_started_at=created.started_at,
                    time_limit_ms=PICTURE_TIME_LIMIT_MS,
                    puzzle=self._wrap_puzzle(pick, 0),
                )

            if game_session.status != GameSessionStatus.ACTIVE:
                attempts = await self.attempt_dao.get_all_for_session(session, game_session.id)
                score = int(game_session.score or 0)
                result = self._result_from_stored_session(attempts, score)
                return PicturePlayPayload(status=game_session.status.value, result=result)

            now = utc_now()
            if self._session_expired(game_session.started_at, now):
                attempts = await self.attempt_dao.get_all_for_session(session, game_session.id)
                accuracy = self._accuracy_total(attempts)
                total = compute_total_score(accuracy, 0)
                await self.game_session_dao.update_status(
                    session,
                    game_session.id,
                    GameSessionStatus.COMPLETED,
                    score=total,
                )
                result = self._build_result(
                    attempts,
                    accuracy_score=accuracy,
                    time_bonus=0,
                    time_remaining_seconds=0,
                )
                return PicturePlayPayload(status=GameSessionStatus.COMPLETED.value, result=result)

            attempts = await self.attempt_dao.get_all_for_session(session, game_session.id)
            solved_count = len(self._answered_correctly_ids(attempts))
            blocked = self._terminal_blocked_ids(attempts)
            next_puzzle = self._pick_unresolved_puzzle(blocked)
            if next_puzzle is None:
                raise NoPicturePuzzlesAvailableException()
            return PicturePlayPayload(
                status=GameSessionStatus.ACTIVE.value,
                game_session_id=game_session.id,
                puzzles_answered=solved_count,
                puzzles_total=pool,
                session_started_at=game_session.started_at,
                time_limit_ms=PICTURE_TIME_LIMIT_MS,
                puzzle=self._wrap_puzzle(next_puzzle, solved_count),
            )

    async def submit_answer(
        self, player_id: str, puzzle_id: str, submitted_answer: Optional[str]
    ) -> PictureAnswerPayload:
        async with self.ctx.session() as session:
            game_session = await self.game_session_dao.get_by_player_and_game(session, player_id, "picture")
            if game_session is None:
                raise SessionNotFoundException(player_id, "picture")
            if game_session.status != GameSessionStatus.ACTIVE:
                raise SessionAlreadyCompletedException(game_session.id, game_session.status.value)

            if puzzle_id not in self._puzzles:
                raise InvalidPuzzleIdException(puzzle_id)

            puzzle = self._puzzles[puzzle_id]

            resolved_ids = await self.attempt_dao.get_resolved_puzzle_ids(session, game_session.id)
            if puzzle_id in set(resolved_ids):
                raise AlreadyResolvedException(puzzle_id)

            is_skip = submitted_answer is None
            is_correct = not is_skip and self._submission_matches(puzzle, submitted_answer)

            await self.attempt_dao.create(
                session,
                game_session.id,
                puzzle_id,
                submitted_answer=None if is_skip else submitted_answer,
                correct=is_correct,
                skipped=is_skip,
            )

            attempts = await self.attempt_dao.get_all_for_session(session, game_session.id)
            pool = self._pool_size()
            now = utc_now()

            puzzles_solved = len(self._answered_correctly_ids(attempts))
            puzzles_remaining = pool - puzzles_solved
            accuracy_running = self._accuracy_total(attempts)
            blocked_after = self._terminal_blocked_ids(attempts)
            no_remaining = self._pick_unresolved_puzzle(blocked_after) is None

            if self._session_expired(game_session.started_at, now):
                total = compute_total_score(accuracy_running, 0)
                updated_session = await self.game_session_dao.update_status(
                    session,
                    game_session.id,
                    GameSessionStatus.COMPLETED,
                    score=total,
                )
                score_final = int(updated_session.score or 0)
                result = self._build_result(
                    attempts,
                    accuracy_score=accuracy_running,
                    time_bonus=0,
                    time_remaining_seconds=0,
                )
                earned = 0
                if is_correct:
                    earned = score_per_puzzle(self._attempt_count_for_resolution(attempts, puzzle_id))
                return PictureAnswerPayload(
                    correct=is_correct,
                    score_earned=earned,
                    current_score=score_final,
                    puzzles_solved=puzzles_solved,
                    puzzles_remaining=0,
                    next_puzzle=None,
                    result=result,
                )

            if not is_correct and not is_skip:
                return PictureAnswerPayload(
                    correct=False,
                    score_earned=0,
                    current_score=accuracy_running,
                    puzzles_solved=puzzles_solved,
                    puzzles_remaining=puzzles_remaining,
                    next_puzzle=None,
                    result=None,
                )

            attempts_for_scoring = self._attempt_count_for_resolution(attempts, puzzle_id)
            score_earned_last = 0 if is_skip else score_per_puzzle(attempts_for_scoring)

            if no_remaining:
                time_bonus = compute_time_bonus(game_session.started_at, now, PICTURE_TIME_LIMIT_MS)
                total = compute_total_score(accuracy_running, time_bonus)
                updated_session = await self.game_session_dao.update_status(
                    session,
                    game_session.id,
                    GameSessionStatus.COMPLETED,
                    score=total,
                )
                score_final = int(updated_session.score or 0)
                result = self._build_result(
                    attempts,
                    accuracy_score=accuracy_running,
                    time_bonus=time_bonus,
                    time_remaining_seconds=time_bonus,
                )
                return PictureAnswerPayload(
                    correct=is_correct,
                    score_earned=score_earned_last,
                    current_score=score_final,
                    puzzles_solved=puzzles_solved,
                    puzzles_remaining=0,
                    next_puzzle=None,
                    result=result,
                )

            next_puzzle_model = self._pick_unresolved_puzzle(blocked_after)
            if next_puzzle_model is None:
                raise NoPicturePuzzlesAvailableException()

            return PictureAnswerPayload(
                correct=is_correct,
                score_earned=score_earned_last,
                current_score=accuracy_running,
                puzzles_solved=puzzles_solved,
                puzzles_remaining=puzzles_remaining,
                next_puzzle=self._wrap_puzzle(next_puzzle_model, puzzles_solved),
                result=None,
            )

    async def abandon(self, player_id: str) -> PictureResultDTO:
        async with self.ctx.session() as session:
            game_session = await self.game_session_dao.get_by_player_and_game(session, player_id, "picture")
            if game_session is None:
                raise SessionNotFoundException(player_id, "picture")
            if game_session.status != GameSessionStatus.ACTIVE:
                raise SessionAlreadyCompletedException(game_session.id, game_session.status.value)

            attempts = await self.attempt_dao.get_all_for_session(session, game_session.id)
            accuracy = self._accuracy_total(attempts)
            now = utc_now()
            time_remaining_seconds = compute_time_bonus(game_session.started_at, now, PICTURE_TIME_LIMIT_MS)
            total = compute_total_score(accuracy, 0)
            await self.game_session_dao.update_status(
                session,
                game_session.id,
                GameSessionStatus.COMPLETED,
                score=total,
            )
            return self._build_result(
                attempts,
                accuracy_score=accuracy,
                time_bonus=0,
                time_remaining_seconds=time_remaining_seconds,
            )
