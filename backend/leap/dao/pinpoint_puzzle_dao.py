"""Read-only DAO for pinpoint puzzles (startup cache warm)."""

from typing import List, NoReturn

from sqlalchemy.ext.asyncio import AsyncSession

from leap.dao.base_pg_dao import BaseReadPgDAO
from leap.dao.models.pinpoint_puzzle import PinpointPuzzle
from leap.types.pinpoint import PinpointPuzzleDTO


class PinpointPuzzleDAO(BaseReadPgDAO[PinpointPuzzle]):
    """Loads all pinpoint puzzles for cache warm."""

    def __init__(self) -> None:
        super().__init__(model_class=PinpointPuzzle)

    def _to_orm(self, *_args: object, **_kwargs: object) -> NoReturn:
        raise NotImplementedError

    def _apply_filters(self, *_args: object, **_kwargs: object) -> NoReturn:
        raise NotImplementedError

    def _to_dto(self, orm: PinpointPuzzle) -> PinpointPuzzleDTO:
        return PinpointPuzzleDTO.model_validate(orm)

    async def get_all(self, session: AsyncSession) -> List[PinpointPuzzleDTO]:
        rows = await self._get_all(session, order_by=PinpointPuzzle.id, limit=10_000)
        return [self._to_dto(row) for row in rows]
