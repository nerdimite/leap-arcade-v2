"""Pinpoint — session lifecycle and scoring orchestration."""

import random
from datetime import datetime
from typing import Callable, Dict, List, Optional, Set

from sqlalchemy.ext.asyncio import AsyncSession

from leap.core.common.time import utc_now
from leap.core.context_manager import ContextManager
from leap.dao.game_session_dao import GameSessionDAO
from leap.dao.pinpoint_puzzle_attempt_dao import PinpointPuzzleAttemptDAO
from leap.dao.pinpoint_puzzle_dao import PinpointPuzzleDAO
from leap.games.pinpoint.scoring import base_score_for_clues, compute_time_bonus, match_answer
from leap.service.exceptions import (
    AlreadyResolvedException,
    InvalidPuzzleIdException,
    NoPinpointPuzzlesAvailableException,
    SessionAlreadyCompletedException,
    SessionNotFoundException,
)
from leap.types.game import GameSessionDTO, GameSessionStatus
from leap.types.pinpoint import (
    PinpointGuessPayload,
    PinpointPlayPayload,
    PinpointPuzzleAttemptDTO,
    PinpointPuzzleDTO,
    PinpointPuzzleStateDTO,
    PinpointResultDTO,
    PinpointResultPuzzleDTO,
)


class PinpointService:
    """Handles Pinpoint sessions, guesses, and puzzle progression."""

    def __init__(
        self,
        ctx: ContextManager,
        game_session_dao: GameSessionDAO,
        puzzle_dao: PinpointPuzzleDAO,
        attempt_dao: PinpointPuzzleAttemptDAO,
        *,
        clock: Optional[Callable[[], datetime]] = None,
    ) -> None:
        self.ctx = ctx
        self.game_session_dao = game_session_dao
        self.puzzle_dao = puzzle_dao
        self.attempt_dao = attempt_dao
        self._clock = clock or utc_now
        self._puzzles: Dict[str, PinpointPuzzleDTO] = {}

    def _now(self) -> datetime:
        return self._clock()

    async def initialize(self, session: AsyncSession) -> None:
        """Warm the in-memory puzzle cache from the database."""
        puzzles = await self.puzzle_dao.get_all(session)
        self._puzzles = {p.id: p for p in puzzles}

    def _pool_size(self) -> int:
        return len(self._puzzles)

    def _clues_for(self, puzzle: PinpointPuzzleDTO, clues_revealed: int) -> List[str]:
        all_clues = [puzzle.clue1, puzzle.clue2, puzzle.clue3, puzzle.clue4, puzzle.clue5]
        return all_clues[:clues_revealed]

    def _terminal_puzzle_ids(self, attempts: List[PinpointPuzzleAttemptDTO]) -> Set[str]:
        return {a.puzzle_id for a in attempts if a.status in ("solved", "failed")}

    def _session_score(self, attempts: List[PinpointPuzzleAttemptDTO]) -> int:
        return sum(a.score or 0 for a in attempts if a.status in ("solved", "failed"))

    def _pick_next_puzzle(self, attempted_ids: Set[str]) -> Optional[PinpointPuzzleDTO]:
        remaining = [p for p in self._puzzles.values() if p.id not in attempted_ids]
        if not remaining:
            return None
        return random.choice(remaining)

    def _puzzle_state(
        self,
        puzzle: PinpointPuzzleDTO,
        attempt: PinpointPuzzleAttemptDTO,
        *,
        puzzle_number: int,
    ) -> PinpointPuzzleStateDTO:
        time_bonus = attempt.time_bonus if attempt.status == "solved" else None
        return PinpointPuzzleStateDTO(
            puzzle_id=puzzle.id,
            puzzle_number=puzzle_number,
            total_puzzles=self._pool_size(),
            clues_revealed=attempt.clues_revealed,
            clues=self._clues_for(puzzle, attempt.clues_revealed),
            status=attempt.status,
            score=attempt.score,
            time_bonus=time_bonus,
            started_at=attempt.started_at,
        )

    def _build_result(
        self,
        attempts: List[PinpointPuzzleAttemptDTO],
        *,
        session_score: int,
    ) -> PinpointResultDTO:
        terminal = [a for a in attempts if a.status in ("solved", "failed")]
        attempted_ids = {a.puzzle_id for a in attempts}
        puzzles_out: List[PinpointResultPuzzleDTO] = []
        for attempt in terminal:
            puzzles_out.append(
                PinpointResultPuzzleDTO(
                    puzzle_id=attempt.puzzle_id,
                    status=attempt.status,
                    clues_used=attempt.clues_revealed,
                    score=attempt.score or 0,
                    time_bonus=attempt.time_bonus or 0,
                )
            )
        for puzzle in sorted(self._puzzles.values(), key=lambda p: p.id):
            if puzzle.id not in attempted_ids:
                puzzles_out.append(
                    PinpointResultPuzzleDTO(
                        puzzle_id=puzzle.id,
                        status="not_reached",
                        clues_used=None,
                        score=0,
                        time_bonus=0,
                    )
                )
        solved_count = sum(1 for a in terminal if a.status == "solved")
        failed_count = sum(1 for a in terminal if a.status == "failed")
        not_reached_count = sum(1 for p in puzzles_out if p.status == "not_reached")
        return PinpointResultDTO(
            score=session_score,
            puzzles_solved=solved_count,
            puzzles_failed=failed_count,
            puzzles_not_reached=not_reached_count,
            puzzles=puzzles_out,
        )

    async def _active_attempt(
        self,
        session: AsyncSession,
        game_session_id: str,
        attempts: List[PinpointPuzzleAttemptDTO],
    ) -> Optional[PinpointPuzzleAttemptDTO]:
        for attempt in attempts:
            if attempt.status == "active":
                return attempt
        return None

    async def _serve_next_puzzle(
        self,
        session: AsyncSession,
        game_session: GameSessionDTO,
        attempts: List[PinpointPuzzleAttemptDTO],
    ) -> PinpointPlayPayload:
        terminal_ids = self._terminal_puzzle_ids(attempts)
        active = await self._active_attempt(session, game_session.id, attempts)
        session_score = self._session_score(attempts)

        if active is not None:
            puzzle = self._puzzles[active.puzzle_id]
            puzzle_number = len(terminal_ids) + 1
            return PinpointPlayPayload(
                session_status=GameSessionStatus.ACTIVE.value,
                session_score=session_score,
                puzzle=self._puzzle_state(puzzle, active, puzzle_number=puzzle_number),
            )

        if len(terminal_ids) >= self._pool_size():
            return PinpointPlayPayload(
                session_status=GameSessionStatus.COMPLETED.value,
                session_score=session_score,
                puzzle=None,
                result=self._build_result(attempts, session_score=session_score),
            )

        next_puzzle = self._pick_next_puzzle(terminal_ids)
        if next_puzzle is None:
            raise NoPinpointPuzzlesAvailableException()

        started_at = self._now()
        created = await self.attempt_dao.create(
            session,
            game_session.id,
            next_puzzle.id,
            started_at,
        )
        puzzle_number = len(terminal_ids) + 1
        return PinpointPlayPayload(
            session_status=GameSessionStatus.ACTIVE.value,
            session_score=session_score,
            puzzle=self._puzzle_state(next_puzzle, created, puzzle_number=puzzle_number),
        )

    async def play(self, player_id: str) -> PinpointPlayPayload:
        async with self.ctx.session() as session:
            pool_size = self._pool_size()
            game_session = await self.game_session_dao.get_by_player_and_game(
                session, player_id, "pinpoint"
            )

            if game_session is None:
                if pool_size == 0:
                    raise NoPinpointPuzzlesAvailableException()
                created = await self.game_session_dao.create(session, player_id, "pinpoint")
                return await self._serve_next_puzzle(session, created, [])

            if game_session.status != GameSessionStatus.ACTIVE:
                attempts = await self.attempt_dao.get_for_session(session, game_session.id)
                score = int(game_session.score or self._session_score(attempts))
                return PinpointPlayPayload(
                    session_status=game_session.status.value,
                    session_score=score,
                    puzzle=None,
                    result=self._build_result(attempts, session_score=score),
                )

            attempts = await self.attempt_dao.get_for_session(session, game_session.id)
            return await self._serve_next_puzzle(session, game_session, attempts)

    async def submit_guess(
        self,
        player_id: str,
        puzzle_id: str,
        guess: str,
    ) -> PinpointGuessPayload:
        async with self.ctx.session() as session:
            game_session = await self.game_session_dao.get_by_player_and_game(
                session, player_id, "pinpoint"
            )
            if game_session is None:
                raise SessionNotFoundException(player_id, "pinpoint")
            if game_session.status != GameSessionStatus.ACTIVE:
                raise SessionAlreadyCompletedException(game_session.id, game_session.status.value)

            if puzzle_id not in self._puzzles:
                raise InvalidPuzzleIdException(puzzle_id)

            attempts = await self.attempt_dao.get_for_session(session, game_session.id)
            active = await self._active_attempt(session, game_session.id, attempts)
            if active is None or active.puzzle_id != puzzle_id:
                raise InvalidPuzzleIdException(puzzle_id)
            if active.status != "active":
                raise AlreadyResolvedException(puzzle_id)

            puzzle = self._puzzles[puzzle_id]
            terminal_ids = self._terminal_puzzle_ids(attempts)
            puzzle_number = len(terminal_ids) + 1
            now = self._now()

            if match_answer(guess, puzzle.answer, puzzle.answer_aliases):
                elapsed_ms = int((now - active.started_at).total_seconds() * 1000)
                base = base_score_for_clues(active.clues_revealed)
                time_bonus = compute_time_bonus(elapsed_ms)
                score = base + time_bonus
                updated = await self.attempt_dao.update_status_and_score(
                    session,
                    active.id,
                    status="solved",
                    score=score,
                    time_bonus=time_bonus,
                    completed_at=now,
                )
                attempts = [
                    updated if a.id == updated.id else a for a in attempts
                ]
                session_score = self._session_score(attempts)
                is_final = len(self._terminal_puzzle_ids(attempts)) >= self._pool_size()

                result: Optional[PinpointResultDTO] = None
                session_status = GameSessionStatus.ACTIVE.value
                if is_final:
                    await self.game_session_dao.update_status(
                        session,
                        game_session.id,
                        GameSessionStatus.COMPLETED,
                        score=session_score,
                    )
                    session_status = GameSessionStatus.COMPLETED.value
                    result = self._build_result(attempts, session_score=session_score)

                return PinpointGuessPayload(
                    correct=True,
                    puzzle=self._puzzle_state(puzzle, updated, puzzle_number=puzzle_number),
                    session_status=session_status,
                    session_score=session_score,
                    result=result,
                )

            if active.clues_revealed < 5:
                updated = await self.attempt_dao.append_guess_and_increment_clues(
                    session,
                    active.id,
                    guess,
                )
                attempts = [
                    updated if a.id == updated.id else a for a in attempts
                ]
                session_score = self._session_score(attempts)
                return PinpointGuessPayload(
                    correct=False,
                    puzzle=self._puzzle_state(puzzle, updated, puzzle_number=puzzle_number),
                    session_status=GameSessionStatus.ACTIVE.value,
                    session_score=session_score,
                    result=None,
                )

            updated = await self.attempt_dao.update_status_and_score(
                session,
                active.id,
                status="failed",
                score=0,
                time_bonus=None,
                completed_at=now,
            )
            attempts = [
                updated if a.id == updated.id else a for a in attempts
            ]
            session_score = self._session_score(attempts)
            is_final = len(self._terminal_puzzle_ids(attempts)) >= self._pool_size()

            result = None
            session_status = GameSessionStatus.ACTIVE.value
            if is_final:
                await self.game_session_dao.update_status(
                    session,
                    game_session.id,
                    GameSessionStatus.COMPLETED,
                    score=session_score,
                )
                session_status = GameSessionStatus.COMPLETED.value
                result = self._build_result(attempts, session_score=session_score)

            return PinpointGuessPayload(
                correct=False,
                puzzle=self._puzzle_state(puzzle, updated, puzzle_number=puzzle_number),
                session_status=session_status,
                session_score=session_score,
                result=result,
            )

    async def abandon(self, player_id: str) -> PinpointResultDTO:
        async with self.ctx.session() as session:
            game_session = await self.game_session_dao.get_by_player_and_game(
                session, player_id, "pinpoint"
            )
            if game_session is None:
                raise SessionNotFoundException(player_id, "pinpoint")
            if game_session.status != GameSessionStatus.ACTIVE:
                raise SessionAlreadyCompletedException(
                    game_session.id, game_session.status.value
                )

            attempts = await self.attempt_dao.get_for_session(session, game_session.id)
            active = await self._active_attempt(session, game_session.id, attempts)
            now = self._now()

            if active is not None:
                updated = await self.attempt_dao.update_status_and_score(
                    session,
                    active.id,
                    status="failed",
                    score=0,
                    time_bonus=None,
                    completed_at=now,
                )
                attempts = [
                    updated if a.id == updated.id else a for a in attempts
                ]

            session_score = self._session_score(attempts)
            await self.game_session_dao.update_status(
                session,
                game_session.id,
                GameSessionStatus.ABANDONED,
                score=session_score,
            )
            return self._build_result(attempts, session_score=session_score)
