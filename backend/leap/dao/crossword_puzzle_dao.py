"""Read-only DAO for crossword puzzles (startup cache warm)."""

from typing import List, NoReturn, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from leap.dao.base_pg_dao import BaseReadPgDAO
from leap.dao.models.crossword import CrosswordPuzzle, CrosswordEntry
from leap.types.crossword import CrosswordPuzzleDTO, CrosswordEntryDTO


class CrosswordPuzzleDAO(BaseReadPgDAO[CrosswordPuzzle]):
    """Loads all crossword puzzles with their entries for cache warm."""

    def __init__(self) -> None:
        super().__init__(model_class=CrosswordPuzzle)

    def _apply_filters(self, *_args: Any, **_kwargs: Any) -> NoReturn:
        raise NotImplementedError

    def _entry_to_dto(self, orm: CrosswordEntry) -> CrosswordEntryDTO:
        return CrosswordEntryDTO(
            id=orm.id,
            puzzle_id=orm.puzzle_id,
            number=orm.number,
            direction=orm.direction,
            start_row=orm.start_row,
            start_col=orm.start_col,
            answer=orm.answer,
            clue=orm.clue,
        )

    def _to_dto(self, orm: CrosswordPuzzle) -> CrosswordPuzzleDTO:
        return CrosswordPuzzleDTO(
            id=orm.id,
            rows=orm.rows,
            cols=orm.cols,
            grid=orm.grid,
            entries=[self._entry_to_dto(e) for e in orm.entries],
        )

    async def get_all_with_entries(self, session: AsyncSession) -> List[CrosswordPuzzleDTO]:
        stmt = (
            select(CrosswordPuzzle)
            .options(selectinload(CrosswordPuzzle.entries))
            .order_by(CrosswordPuzzle.id)
        )
        result = await session.execute(stmt)
        puzzles = result.scalars().unique().all()
        return [self._to_dto(puzzle) for puzzle in puzzles]
