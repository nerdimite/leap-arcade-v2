"""Read-only DAO for crossword entries."""

from typing import List, NoReturn

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from leap.dao.base_pg_dao import BaseReadPgDAO
from leap.dao.models.crossword import CrosswordEntry
from leap.types.crossword import CrosswordEntryDTO


class CrosswordEntryDAO(BaseReadPgDAO[CrosswordEntry]):
    """Loads crossword entries for a puzzle."""

    def __init__(self) -> None:
        super().__init__(model_class=CrosswordEntry)

    def _to_orm(self, *_args: object, **_kwargs: object) -> NoReturn:
        raise NotImplementedError

    def _apply_filters(self, *_args: object, **_kwargs: object) -> NoReturn:
        raise NotImplementedError

    def _to_dto(self, orm: CrosswordEntry) -> CrosswordEntryDTO:
        return CrosswordEntryDTO.model_validate(orm)

    async def get_for_puzzle(
        self,
        session: AsyncSession,
        puzzle_id: str,
    ) -> List[CrosswordEntryDTO]:
        stmt = (
            select(CrosswordEntry)
            .where(CrosswordEntry.puzzle_id == puzzle_id)
            .order_by(CrosswordEntry.number, CrosswordEntry.direction)
        )
        result = await session.execute(stmt)
        return [self._to_dto(row) for row in result.scalars().all()]
