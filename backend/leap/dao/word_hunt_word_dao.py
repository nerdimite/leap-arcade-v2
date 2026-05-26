"""Read-only DAO for word hunt words."""

from typing import List, NoReturn

from sqlalchemy.ext.asyncio import AsyncSession

from leap.dao.base_pg_dao import BaseReadPgDAO
from leap.dao.models.word_hunt import WordHuntWord
from leap.types.word_hunt import WordHuntWordDTO


class WordHuntWordDAO(BaseReadPgDAO[WordHuntWord]):
    """Loads words for a puzzle."""

    def __init__(self) -> None:
        super().__init__(model_class=WordHuntWord)

    def _to_orm(self, *_args: object, **_kwargs: object) -> NoReturn:
        raise NotImplementedError

    def _apply_filters(self, *_args: object, **_kwargs: object) -> NoReturn:
        raise NotImplementedError

    def _to_dto(self, orm: WordHuntWord) -> WordHuntWordDTO:
        return WordHuntWordDTO.model_validate(orm)

    async def get_for_puzzle(self, session: AsyncSession, puzzle_id: str) -> List[WordHuntWordDTO]:
        rows = await self._get_all(
            session,
            filters={"puzzle_id": puzzle_id},
            order_by=WordHuntWord.id,
            limit=10_000,
        )
        return [self._to_dto(row) for row in rows]
