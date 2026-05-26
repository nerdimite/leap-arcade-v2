"""Read-only DAO for Four Pics questions (startup cache warm)."""

from typing import List, NoReturn

from sqlalchemy.ext.asyncio import AsyncSession

from leap.dao.base_pg_dao import BaseReadPgDAO
from leap.dao.models.four_pics_question import FourPicsQuestion
from leap.types.four_pics import FourPicsQuestionDTO


class FourPicsQuestionDAO(BaseReadPgDAO[FourPicsQuestion]):
    """Loads all Four Pics questions for cache warm — no writes."""

    def __init__(self) -> None:
        super().__init__(model_class=FourPicsQuestion)

    def _to_orm(self, *_args: object, **_kwargs: object) -> NoReturn:
        raise NotImplementedError

    def _apply_filters(self, *_args: object, **_kwargs: object) -> NoReturn:
        raise NotImplementedError

    def _to_dto(self, orm: FourPicsQuestion) -> FourPicsQuestionDTO:
        return FourPicsQuestionDTO.model_validate(orm)

    async def get_all(self, session: AsyncSession) -> List[FourPicsQuestionDTO]:
        rows = await self._get_all(session, order_by=FourPicsQuestion.id, limit=10_000)
        return [self._to_dto(row) for row in rows]
