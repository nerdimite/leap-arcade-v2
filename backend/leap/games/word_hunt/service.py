"""Word Hunt — session lifecycle and find resolution."""

from datetime import datetime
from typing import Callable, Dict, List, Optional, Set

from sqlalchemy.ext.asyncio import AsyncSession

from leap.core.common.time import utc_now
from leap.core.context_manager import ContextManager
from leap.dao.game_session_dao import GameSessionDAO
from leap.dao.word_hunt_find_dao import WordHuntFindDAO
from leap.dao.word_hunt_puzzle_dao import WordHuntPuzzleDAO
from leap.games.word_hunt.grid import validate_trace, walk_cells
from leap.games.word_hunt.scoring import compute_base_score, compute_final_score, compute_time_bonus
from leap.service.exceptions import (
    NoWordHuntPuzzleAvailableException,
    WordHuntSessionAlreadyCompletedException,
)
from leap.types.game import GameSessionDTO, GameSessionStatus
from leap.types.word_hunt import (
    WordHuntClueDTO,
    WordHuntCoordinatesDTO,
    WordHuntFindDTO,
    WordHuntFindPayload,
    WordHuntFoundWordDTO,
    WordHuntPlayPayload,
    WordHuntPuzzleDTO,
    WordHuntPuzzleStateDTO,
    WordHuntResultDTO,
    WordHuntWordDTO,
)


class WordHuntService:
    """Handles Word Hunt sessions, finds, and scoring."""

    def __init__(
        self,
        ctx: ContextManager,
        game_session_dao: GameSessionDAO,
        puzzle_dao: WordHuntPuzzleDAO,
        find_dao: WordHuntFindDAO,
        *,
        clock: Optional[Callable[[], datetime]] = None,
    ) -> None:
        self.ctx = ctx
        self.game_session_dao = game_session_dao
        self.puzzle_dao = puzzle_dao
        self.find_dao = find_dao
        self._clock = clock or utc_now
        self._puzzles: Dict[str, WordHuntPuzzleDTO] = {}

    def _now(self) -> datetime:
        return self._clock()

    def _elapsed_ms(self, game_session: GameSessionDTO) -> int:
        if (
            game_session.status != GameSessionStatus.ACTIVE
            and game_session.completed_at is not None
        ):
            end = game_session.completed_at
        else:
            end = self._now()
        return int((end - game_session.started_at).total_seconds() * 1000)

    async def initialize(self, session: AsyncSession) -> None:
        """Warm the in-memory puzzle cache from the database."""
        puzzles = await self.puzzle_dao.get_all_with_words(session)
        self._puzzles = {p.id: p for p in puzzles}

    def _active_puzzle(self) -> WordHuntPuzzleDTO:
        if not self._puzzles:
            raise NoWordHuntPuzzleAvailableException()
        return next(iter(self._puzzles.values()))

    def _found_word_ids(self, finds: List[WordHuntFindDTO]) -> Set[str]:
        return {f.word_id for f in finds}

    def _word_by_id(self, puzzle: WordHuntPuzzleDTO) -> Dict[str, WordHuntWordDTO]:
        return {w.id: w for w in puzzle.words}

    def _coordinates(self, find: WordHuntFindDTO) -> WordHuntCoordinatesDTO:
        return WordHuntCoordinatesDTO(
            start_row=find.start_row,
            start_col=find.start_col,
            end_row=find.end_row,
            end_col=find.end_col,
        )

    def _found_word_dto(
        self,
        word: WordHuntWordDTO,
        find: WordHuntFindDTO,
    ) -> WordHuntFoundWordDTO:
        return WordHuntFoundWordDTO(
            word_id=word.id,
            word=word.word,
            clue=word.clue,
            coordinates=self._coordinates(find),
        )

    def _build_clues(
        self,
        puzzle: WordHuntPuzzleDTO,
        finds: List[WordHuntFindDTO],
    ) -> List[WordHuntClueDTO]:
        find_by_word_id = {f.word_id: f for f in finds}
        clues: List[WordHuntClueDTO] = []
        for word in puzzle.words:
            find = find_by_word_id.get(word.id)
            if find is None:
                clues.append(
                    WordHuntClueDTO(
                        word_id=word.id,
                        clue=word.clue,
                        found=False,
                    )
                )
            else:
                clues.append(
                    WordHuntClueDTO(
                        word_id=word.id,
                        clue=word.clue,
                        found=True,
                        word=word.word,
                        coordinates=self._coordinates(find),
                    )
                )
        return clues

    def _build_result(
        self,
        puzzle: WordHuntPuzzleDTO,
        finds: List[WordHuntFindDTO],
        elapsed_ms: int,
    ) -> WordHuntResultDTO:
        words_by_id = self._word_by_id(puzzle)
        found_words = [
            self._found_word_dto(words_by_id[f.word_id], f)
            for f in finds
            if f.word_id in words_by_id
        ]
        found_count = len(finds)
        base_score = compute_base_score(found_count)
        time_bonus = compute_time_bonus(elapsed_ms)
        return WordHuntResultDTO(
            score=base_score + time_bonus,
            base_score=base_score,
            time_bonus=time_bonus,
            time_elapsed_ms=elapsed_ms,
            found_count=found_count,
            total_words=len(puzzle.words),
            found_words=found_words,
        )

    def _build_puzzle_state(
        self,
        puzzle: WordHuntPuzzleDTO,
        finds: List[WordHuntFindDTO],
        started_at: datetime,
    ) -> WordHuntPuzzleStateDTO:
        return WordHuntPuzzleStateDTO(
            puzzle_id=puzzle.id,
            rows=puzzle.rows,
            cols=puzzle.cols,
            grid=puzzle.grid,
            clues=self._build_clues(puzzle, finds),
            found_count=len(finds),
            total_words=len(puzzle.words),
            started_at=started_at,
        )

    def _match_word(
        self,
        puzzle: WordHuntPuzzleDTO,
        traced: str,
        found_ids: Set[str],
    ) -> Optional[WordHuntWordDTO]:
        reversed_traced = traced[::-1]
        for word in puzzle.words:
            if word.id in found_ids:
                continue
            canonical = word.word.upper()
            if traced.upper() == canonical or reversed_traced.upper() == canonical:
                return word
        return None

    async def play(self, player_id: str) -> WordHuntPlayPayload:
        async with self.ctx.session() as session:
            puzzle = self._active_puzzle()
            game_session = await self.game_session_dao.get_by_player_and_game(
                session, player_id, "word_hunt"
            )

            if game_session is None:
                created = await self.game_session_dao.create(session, player_id, "word_hunt")
                return WordHuntPlayPayload(
                    session_status=GameSessionStatus.ACTIVE.value,
                    session_score=0,
                    puzzle=self._build_puzzle_state(puzzle, [], created.started_at),
                    result=None,
                )

            finds = await self.find_dao.get_for_session(session, game_session.id)

            if game_session.status != GameSessionStatus.ACTIVE:
                elapsed_ms = self._elapsed_ms(game_session)
                result = self._build_result(puzzle, finds, elapsed_ms)
                return WordHuntPlayPayload(
                    session_status=game_session.status.value,
                    session_score=game_session.score or result.score,
                    puzzle=None,
                    result=result,
                )

            session_score = compute_base_score(len(finds))
            return WordHuntPlayPayload(
                session_status=GameSessionStatus.ACTIVE.value,
                session_score=session_score,
                puzzle=self._build_puzzle_state(puzzle, finds, game_session.started_at),
                result=None,
            )

    async def submit_find(
        self,
        player_id: str,
        start_row: int,
        start_col: int,
        end_row: int,
        end_col: int,
    ) -> WordHuntFindPayload:
        async with self.ctx.session() as session:
            puzzle = self._active_puzzle()
            game_session = await self.game_session_dao.get_by_player_and_game(
                session, player_id, "word_hunt"
            )
            if game_session is None or game_session.status != GameSessionStatus.ACTIVE:
                return WordHuntFindPayload(
                    matched=False,
                    word=None,
                    session_status=(
                        game_session.status.value
                        if game_session is not None
                        else GameSessionStatus.ACTIVE.value
                    ),
                    session_score=0,
                    result=None,
                )

            finds = await self.find_dao.get_for_session(session, game_session.id)
            found_ids = self._found_word_ids(finds)
            session_score = compute_base_score(len(finds))

            if not validate_trace(
                puzzle.rows,
                puzzle.cols,
                start_row,
                start_col,
                end_row,
                end_col,
            ):
                return WordHuntFindPayload(
                    matched=False,
                    word=None,
                    session_status=GameSessionStatus.ACTIVE.value,
                    session_score=session_score,
                    result=None,
                )

            traced = walk_cells(puzzle.grid, start_row, start_col, end_row, end_col)
            matched_word = self._match_word(puzzle, traced, found_ids)
            if matched_word is None:
                return WordHuntFindPayload(
                    matched=False,
                    word=None,
                    session_status=GameSessionStatus.ACTIVE.value,
                    session_score=session_score,
                    result=None,
                )

            find = await self.find_dao.create(
                session,
                game_session.id,
                matched_word.id,
                start_row,
                start_col,
                end_row,
                end_col,
            )
            finds = finds + [find]
            session_score = compute_base_score(len(finds))
            found_word = self._found_word_dto(matched_word, find)

            if len(finds) == len(puzzle.words):
                now = self._now()
                elapsed_ms = int((now - game_session.started_at).total_seconds() * 1000)
                final_score = compute_final_score(len(finds), elapsed_ms)
                await self.game_session_dao.update_status(
                    session,
                    game_session.id,
                    GameSessionStatus.COMPLETED,
                    score=final_score,
                )
                result = self._build_result(puzzle, finds, elapsed_ms)
                return WordHuntFindPayload(
                    matched=True,
                    word=found_word,
                    session_status=GameSessionStatus.COMPLETED.value,
                    session_score=final_score,
                    result=result,
                )

            return WordHuntFindPayload(
                matched=True,
                word=found_word,
                session_status=GameSessionStatus.ACTIVE.value,
                session_score=session_score,
                result=None,
            )

    async def submit(self, player_id: str) -> WordHuntResultDTO:
        async with self.ctx.session() as session:
            puzzle = self._active_puzzle()
            game_session = await self.game_session_dao.get_by_player_and_game(
                session, player_id, "word_hunt"
            )
            if game_session is None:
                raise WordHuntSessionAlreadyCompletedException()

            if game_session.status == GameSessionStatus.COMPLETED:
                raise WordHuntSessionAlreadyCompletedException()

            finds = await self.find_dao.get_for_session(session, game_session.id)
            now = self._now()
            elapsed_ms = int((now - game_session.started_at).total_seconds() * 1000)
            final_score = compute_final_score(len(finds), elapsed_ms)
            await self.game_session_dao.update_status(
                session,
                game_session.id,
                GameSessionStatus.COMPLETED,
                score=final_score,
            )
            return self._build_result(puzzle, finds, elapsed_ms)
