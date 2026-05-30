"""Crossword — session lifecycle and check resolution."""

from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from leap.core.common.time import utc_now
from leap.core.context_manager import ContextManager
from leap.dao.crossword_puzzle_dao import CrosswordPuzzleDAO
from leap.dao.crossword_solve_dao import CrosswordSolveDAO
from leap.dao.game_session_dao import GameSessionDAO
from leap.games.crossword.grid import build_skeleton, entry_cells
from leap.games.crossword.scoring import (
    compute_base_score,
    compute_final_score,
    compute_time_bonus,
)
from leap.service.exceptions import (
    CrosswordSessionAlreadyCompletedException,
    NoCrosswordPuzzleAvailableException,
)
from leap.types.crossword import (
    CellSkeleton,
    ClueSkeleton,
    CrosswordCheckPayload,
    CrosswordEntryDTO,
    CrosswordPlayPayload,
    CrosswordPuzzleDTO,
    CrosswordPuzzleStateDTO,
    CrosswordResultDTO,
    CrosswordSolvedEntryDTO,
    CrosswordSolveDTO,
)
from leap.types.game import GameSessionDTO, GameSessionStatus


class CrosswordService:
    """Handles Crossword sessions, checks, and scoring."""

    def __init__(
        self,
        ctx: ContextManager,
        game_session_dao: GameSessionDAO,
        puzzle_dao: CrosswordPuzzleDAO,
        solve_dao: CrosswordSolveDAO,
        *,
        clock: Optional[Callable[[], datetime]] = None,
    ) -> None:
        self.ctx = ctx
        self.game_session_dao = game_session_dao
        self.puzzle_dao = puzzle_dao
        self.solve_dao = solve_dao
        self._clock = clock or utc_now
        self._puzzles: Dict[str, CrosswordPuzzleDTO] = {}

    def _now(self) -> datetime:
        return self._clock()

    def _elapsed_ms(self, game_session: GameSessionDTO) -> int:
        if (
            game_session.status != GameSessionStatus.ACTIVE.value
            and game_session.completed_at is not None
        ):
            end = game_session.completed_at
        else:
            end = self._now()
        return int((end - game_session.started_at).total_seconds() * 1000)

    async def initialize(self, session: AsyncSession) -> None:
        """Warm the in-memory puzzle cache from the database."""
        puzzles = await self.puzzle_dao.get_all_with_entries(session)
        self._puzzles = {p.id: p for p in puzzles}

    def _active_puzzle(self) -> CrosswordPuzzleDTO:
        if not self._puzzles:
            raise NoCrosswordPuzzleAvailableException()
        return next(iter(self._puzzles.values()))

    def _entry_by_id(self, puzzle: CrosswordPuzzleDTO) -> Dict[str, CrosswordEntryDTO]:
        return {e.id: e for e in puzzle.entries}

    def _build_solved_entry_dto(self, entry: CrosswordEntryDTO) -> CrosswordSolvedEntryDTO:
        coords = entry_cells(entry.start_row, entry.start_col, entry.direction, len(entry.answer))
        return CrosswordSolvedEntryDTO(
            entry_id=entry.id,
            number=entry.number,
            direction=entry.direction,
            clue=entry.clue,
            answer=entry.answer,
            cells=[{"row": r, "col": c} for r, c in coords],
        )

    def _build_puzzle_state(
        self,
        puzzle: CrosswordPuzzleDTO,
        solves: List[CrosswordSolveDTO],
        started_at: datetime,
    ) -> CrosswordPuzzleStateDTO:
        # 1. Build initial skeleton with grid and entries from grid.py
        entries_dicts = [
            {
                "id": e.id,
                "number": e.number,
                "direction": e.direction,
                "start_row": e.start_row,
                "start_col": e.start_col,
                "clue": e.clue,
                "answer": e.answer,
            }
            for e in puzzle.entries
        ]
        cells_skel, clues_skel = build_skeleton(puzzle.grid, entries_dicts)

        # Convert dictionaries to Pydantic objects for type safety
        cells: List[List[Optional[CellSkeleton]]] = []
        for row in cells_skel:
            row_obj = []
            for cell in row:
                if cell is None:
                    row_obj.append(None)
                else:
                    row_obj.append(CellSkeleton(**cell))
            cells.append(row_obj)

        clues = [ClueSkeleton(**clue) for clue in clues_skel]

        # 2. Populate solved entries
        solved_entry_ids = {s.entry_id for s in solves}
        clues_by_id = {c.entry_id: c for c in clues}
        entries_by_id = self._entry_by_id(puzzle)

        for solve in solves:
            entry = entries_by_id.get(solve.entry_id)
            if not entry:
                continue
            # Update Clue
            clue = clues_by_id.get(solve.entry_id)
            if clue:
                clue.solved = True
                clue.answer = entry.answer
                coords = entry_cells(
                    entry.start_row, entry.start_col, entry.direction, len(entry.answer)
                )
                clue.cells = [{"row": r, "col": c} for r, c in coords]

            # Update Cells letters
            coords = entry_cells(
                entry.start_row, entry.start_col, entry.direction, len(entry.answer)
            )
            for i, (r, c) in enumerate(coords):
                if cells[r][c]:
                    cells[r][c].letter = entry.answer[i].upper()

        return CrosswordPuzzleStateDTO(
            puzzle_id=puzzle.id,
            rows=puzzle.rows,
            cols=puzzle.cols,
            cells=cells,
            clues=clues,
            solved_count=len(solved_entry_ids),
            total_entries=len(puzzle.entries),
            started_at=started_at,
        )

    def _build_result(
        self,
        puzzle: CrosswordPuzzleDTO,
        solves: List[CrosswordSolveDTO],
        elapsed_ms: int,
    ) -> CrosswordResultDTO:
        entries_by_id = self._entry_by_id(puzzle)
        solved_entries = []
        for s in solves:
            entry = entries_by_id.get(s.entry_id)
            if entry:
                solved_entries.append(self._build_solved_entry_dto(entry))

        solved_count = len(solves)
        base_score = compute_base_score(solved_count)
        time_bonus = compute_time_bonus(elapsed_ms)

        return CrosswordResultDTO(
            score=base_score + time_bonus,
            base_score=base_score,
            time_bonus=time_bonus,
            time_elapsed_ms=elapsed_ms,
            solved_count=solved_count,
            total_entries=len(puzzle.entries),
            solved_entries=solved_entries,
        )

    async def play(self, player_id: str) -> CrosswordPlayPayload:
        """Create or resume a crossword session."""
        async with self.ctx.session() as session:
            game_session = await self.game_session_dao.get_by_player_and_game(
                session, player_id, "crossword"
            )

            if game_session is None:
                game_session = await self.game_session_dao.create(session, player_id, "crossword")
                await session.commit()

            puzzle = self._active_puzzle()

            if game_session.status == GameSessionStatus.COMPLETED.value:
                solves = await self.solve_dao.get_for_session(session, game_session.id)
                elapsed_ms = self._elapsed_ms(game_session)
                result = self._build_result(puzzle, solves, elapsed_ms)
                return CrosswordPlayPayload(
                    session_status=game_session.status,
                    session_score=game_session.score or result.score,
                    puzzle=None,
                    result=result,
                )

            # Active session
            solves = await self.solve_dao.get_for_session(session, game_session.id)
            session_score = compute_base_score(len(solves))
            puzzle_state = self._build_puzzle_state(puzzle, solves, game_session.started_at)
            return CrosswordPlayPayload(
                session_status=game_session.status,
                session_score=session_score,
                puzzle=puzzle_state,
                result=None,
            )

    async def submit_check(
        self,
        player_id: str,
        payload_or_entry_id: Any,
        letters: Optional[str] = None,
    ) -> CrosswordCheckPayload:
        """Check typed letters for an entry and award solves. Supports polymorphic signatures."""
        if letters is not None:
            entry_id = str(payload_or_entry_id)
        else:
            entry_id = str(payload_or_entry_id.entry_id)
            letters = payload_or_entry_id.letters

        async with self.ctx.session() as session:
            game_session = await self.game_session_dao.get_by_player_and_game(
                session, player_id, "crossword"
            )

            if game_session is None:
                # No session found, return correct=False gracefully
                return CrosswordCheckPayload(
                    correct=False,
                    entry=None,
                    session_status=GameSessionStatus.ACTIVE.value,
                    session_score=0,
                    result=None,
                )

            if game_session.status == GameSessionStatus.COMPLETED.value:
                raise CrosswordSessionAlreadyCompletedException()

            puzzle = self._active_puzzle()
            entries_by_id = self._entry_by_id(puzzle)

            # 1. Validate entry_id belongs to the active puzzle
            if entry_id not in entries_by_id:
                solves = await self.solve_dao.get_for_session(session, game_session.id)
                session_score = compute_base_score(len(solves))
                return CrosswordCheckPayload(
                    correct=False,
                    entry=None,
                    session_status=game_session.status,
                    session_score=session_score,
                    result=None,
                )

            entry = entries_by_id[entry_id]

            # 2. Validate letters length matches answer length
            if len(letters) != len(entry.answer):
                solves = await self.solve_dao.get_for_session(session, game_session.id)
                session_score = compute_base_score(len(solves))
                return CrosswordCheckPayload(
                    correct=False,
                    entry=None,
                    session_status=game_session.status,
                    session_score=session_score,
                    result=None,
                )

            # 3. Check duplicate-solve guard
            solves = await self.solve_dao.get_for_session(session, game_session.id)
            solved_entry_ids = {s.entry_id for s in solves}

            if entry_id in solved_entry_ids:
                session_score = compute_base_score(len(solves))
                return CrosswordCheckPayload(
                    correct=False,
                    entry=None,
                    session_status=game_session.status,
                    session_score=session_score,
                    result=None,
                )

            # 4. Case-insensitive compare
            if letters.upper() == entry.answer.upper():
                # Correct! Create solve row
                new_solve = await self.solve_dao.create(session, game_session.id, entry.id)
                solves.append(new_solve)
                solved_entry_ids.add(entry.id)

                session_score = compute_base_score(len(solves))
                solved_entry_dto = self._build_solved_entry_dto(entry)

                # Check auto-complete
                if len(solved_entry_ids) == len(puzzle.entries):
                    now = self._now()
                    elapsed_ms = int((now - game_session.started_at).total_seconds() * 1000)
                    final_score = compute_final_score(len(solves), elapsed_ms)
                    game_session = await self.game_session_dao.update_status(
                        session,
                        game_session.id,
                        GameSessionStatus.COMPLETED,
                        final_score,
                    )
                    await session.commit()
                    result = self._build_result(puzzle, solves, elapsed_ms)
                    return CrosswordCheckPayload(
                        correct=True,
                        entry=solved_entry_dto,
                        session_status=GameSessionStatus.COMPLETED.value,
                        session_score=final_score,
                        result=result,
                    )

                await session.commit()
                return CrosswordCheckPayload(
                    correct=True,
                    entry=solved_entry_dto,
                    session_status=game_session.status,
                    session_score=session_score,
                    result=None,
                )

            # Incorrect spelling
            session_score = compute_base_score(len(solves))
            return CrosswordCheckPayload(
                correct=False,
                entry=None,
                session_status=game_session.status,
                session_score=session_score,
                result=None,
            )

    async def submit(self, player_id: str) -> CrosswordResultDTO:
        """Voluntarily finalize the crossword session."""
        async with self.ctx.session() as session:
            game_session = await self.game_session_dao.get_by_player_and_game(
                session, player_id, "crossword"
            )

            if game_session is None:
                # Stub session if not exists
                game_session = await self.game_session_dao.create(session, player_id, "crossword")
                await session.commit()

            if game_session.status == GameSessionStatus.COMPLETED.value:
                raise CrosswordSessionAlreadyCompletedException()

            puzzle = self._active_puzzle()
            solves = await self.solve_dao.get_for_session(session, game_session.id)
            now = self._now()
            elapsed_ms = int((now - game_session.started_at).total_seconds() * 1000)
            final_score = compute_final_score(len(solves), elapsed_ms)

            game_session = await self.game_session_dao.update_status(
                session, game_session.id, GameSessionStatus.COMPLETED, final_score
            )
            await session.commit()

            return self._build_result(puzzle, solves, elapsed_ms)
