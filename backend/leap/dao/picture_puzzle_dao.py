"""Read-only DAO for picture puzzles (startup cache warm)."""

from typing import List, NoReturn

from sqlalchemy.ext.asyncio import AsyncSession

from leap.dao.base_pg_dao import BaseReadPgDAO
from leap.dao.models.picture_puzzle import PicturePuzzle
from leap.types.picture import PicturePuzzleDTO


class PicturePuzzleDAO(BaseReadPgDAO[PicturePuzzle]):
    """Loads all picture puzzles for cache warm — no filters or ORM round-trips beyond reads."""

    def __init__(self) -> None:
        super().__init__(model_class=PicturePuzzle)

    def _to_orm(self, *_args: object, **_kwargs: object) -> NoReturn:
        raise NotImplementedError

    def _apply_filters(self, *_args: object, **_kwargs: object) -> NoReturn:
        raise NotImplementedError

    def _to_dto(self, orm: PicturePuzzle) -> PicturePuzzleDTO:
        return PicturePuzzleDTO.model_validate(orm)

    async def get_all(self, session: AsyncSession) -> List[PicturePuzzleDTO]:
        rows = await self._get_all(session, order_by=PicturePuzzle.id, limit=10_000)
        return [self._to_dto(row) for row in rows]
