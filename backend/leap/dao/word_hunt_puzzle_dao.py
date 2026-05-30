"""Read-only DAO for word hunt puzzles (startup cache warm)."""

from typing import List, NoReturn

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from leap.dao.base_pg_dao import BaseReadPgDAO
from leap.dao.models.word_hunt import WordHuntPuzzle, WordHuntWord
from leap.types.word_hunt import WordHuntPuzzleDTO, WordHuntWordDTO


class WordHuntPuzzleDAO(BaseReadPgDAO[WordHuntPuzzle]):
    """Loads all word hunt puzzles with their words for cache warm."""

    def __init__(self) -> None:
        super().__init__(model_class=WordHuntPuzzle)

    def _to_orm(self, *_args: object, **_kwargs: object) -> NoReturn:
        raise NotImplementedError

    def _apply_filters(self, *_args: object, **_kwargs: object) -> NoReturn:
        raise NotImplementedError

    def _word_to_dto(self, orm: WordHuntWord) -> WordHuntWordDTO:
        return WordHuntWordDTO.model_validate(orm)

    def _to_dto(self, orm: WordHuntPuzzle, words: List[WordHuntWord]) -> WordHuntPuzzleDTO:
        return WordHuntPuzzleDTO(
            id=orm.id,
            rows=orm.rows,
            cols=orm.cols,
            grid=orm.grid,
            words=[self._word_to_dto(w) for w in words],
        )

    async def get_all_with_words(self, session: AsyncSession) -> List[WordHuntPuzzleDTO]:
        stmt = (
            select(WordHuntPuzzle)
            .options(selectinload(WordHuntPuzzle.words))
            .order_by(WordHuntPuzzle.id)
        )
        result = await session.execute(stmt)
        puzzles = result.scalars().unique().all()
        return [self._to_dto(puzzle, list(puzzle.words)) for puzzle in puzzles]
