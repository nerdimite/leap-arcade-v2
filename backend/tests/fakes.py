"""Shared test fakes.

Hand-written in-memory fakes used across unit tests.  No MagicMock — fakes
express the contract honestly and survive internal refactors.
"""

import uuid
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List, Optional

from leap.core.common.time import utc_now
from leap.types.game import GameSessionDTO, GameSessionStatus
from leap.types.player import PlayerDTO
from leap.types.rapid_fire import RapidFireAnswerDTO, RapidFireQuestionDTO


class FakeAsyncSession:
    """Minimal async session that satisfies type contracts but does nothing."""

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass


class FakeContextManager:
    """Fake ContextManager that yields a FakeAsyncSession.

    The session is ignored by fake DAOs — this just satisfies the
    ``async with ctx.session() as session:`` pattern used in services.
    """

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[FakeAsyncSession, None]:
        yield FakeAsyncSession()


class FakePlayerDAO:
    """In-memory player store keyed by corp_id (normalised).

    Args:
        players: mapping of corp_id → PlayerDTO. Defaults to empty.
    """

    def __init__(self, players: Optional[Dict[str, PlayerDTO]] = None) -> None:
        self._players: Dict[str, PlayerDTO] = players or {}

    async def get_by_id(self, session: Any, corp_id: str) -> Optional[PlayerDTO]:
        return self._players.get(corp_id)


class FakeGameSessionDAO:
    """In-memory game session store."""

    def __init__(self, sessions: Optional[List[GameSessionDTO]] = None) -> None:
        self._sessions: List[GameSessionDTO] = sessions or []

    async def get_by_player_and_game(
        self, session: Any, player_id: str, game_id: str
    ) -> Optional[GameSessionDTO]:
        for s in self._sessions:
            if s.player_id == player_id and s.game_id == game_id:
                return s
        return None

    async def create(
        self, session: Any, player_id: str, game_id: str
    ) -> GameSessionDTO:
        dto = GameSessionDTO(
            id=str(uuid.uuid4()),
            player_id=player_id,
            game_id=game_id,
            status=GameSessionStatus.ACTIVE,
            score=None,
            started_at=utc_now(),
            completed_at=None,
        )
        self._sessions.append(dto)
        return dto

    async def update_status(
        self,
        session: Any,
        game_session_id: str,
        status: GameSessionStatus,
        score: Optional[int] = None,
    ) -> GameSessionDTO:
        for s in self._sessions:
            if s.id == game_session_id:
                updated = s.model_copy(
                    update={"status": status, "score": score if score is not None else s.score}
                )
                self._sessions[self._sessions.index(s)] = updated
                return updated
        raise KeyError(f"session not found: {game_session_id}")

    async def get_all_for_player(
        self, session: Any, player_id: str
    ) -> List[GameSessionDTO]:
        return [s for s in self._sessions if s.player_id == player_id]

    async def get_leaderboard(self, session: Any) -> List[GameSessionDTO]:
        return []


class FakeRapidFireQuestionDAO:
    """In-memory rapid fire question store."""

    def __init__(self, questions: Optional[List[RapidFireQuestionDTO]] = None) -> None:
        self._questions: List[RapidFireQuestionDTO] = questions or []

    async def get_random_excluding(
        self, session: Any, exclude_ids: List[str]
    ) -> Optional[RapidFireQuestionDTO]:
        available = [q for q in self._questions if q.id not in exclude_ids]
        return available[0] if available else None

    async def get_question_count(self, session: Any) -> int:
        return len(self._questions)


class FakeRapidFireAnswerDAO:
    """In-memory rapid fire answer store."""

    def __init__(self) -> None:
        self._answers: List[RapidFireAnswerDTO] = []

    async def create(
        self,
        session: Any,
        game_session_id: str,
        question_id: str,
        correct: bool,
        skipped: bool,
        time_ms: int,
    ) -> RapidFireAnswerDTO:
        dto = RapidFireAnswerDTO(
            id=str(uuid.uuid4()),
            game_session_id=game_session_id,
            question_id=question_id,
            correct=correct,
            skipped=skipped,
            time_ms=time_ms,
            answered_at=utc_now(),
        )
        self._answers.append(dto)
        return dto

    async def get_asked_question_ids(
        self, session: Any, game_session_id: str
    ) -> List[str]:
        return [
            a.question_id
            for a in self._answers
            if a.game_session_id == game_session_id
        ]

    async def get_all_for_session(
        self, session: Any, game_session_id: str
    ) -> List[RapidFireAnswerDTO]:
        return [a for a in self._answers if a.game_session_id == game_session_id]
