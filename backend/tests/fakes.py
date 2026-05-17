"""Shared test fakes.

Hand-written in-memory fakes used across unit tests.  No MagicMock — fakes
express the contract honestly and survive internal refactors.
"""

import datetime
import uuid
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List, Optional

import pytz

from leap.core.common import time as leap_time
from leap.games.rapid_fire.service import RapidFireService
from leap.games.wiki.service import WikiSpeedRunService
from leap.service.auth_service import AuthService
from leap.service.leaderboard_service import LeaderboardService
from leap.service.lobby_service import LobbyService
from leap.service.player_session_service import PlayerSessionService
from leap.types.game import (
    GameSessionDTO,
    GameSessionStatus,
    LeaderboardEntryDTO,
)
from leap.types.player import PlayerDTO
from leap.types.rapid_fire import RapidFireAnswerDTO, RapidFireQuestionDTO
from leap.types.wiki import WikiArticleDTO, WikiPuzzleAttemptDTO, WikiRoundDTO


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

    def list_players(self) -> List[PlayerDTO]:
        """All registered players — used by ``FakeGameSessionDAO.get_leaderboard``."""
        return list(self._players.values())


class FakeGameSessionDAO:
    """In-memory game session store."""

    def __init__(
        self,
        sessions: Optional[List[GameSessionDTO]] = None,
        player_dao: Optional["FakePlayerDAO"] = None,
    ) -> None:
        self._sessions: List[GameSessionDTO] = sessions or []
        self._player_dao: Optional[FakePlayerDAO] = player_dao

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
            started_at=leap_time.utc_now(),
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
                new_completed_at = s.completed_at
                if status in (GameSessionStatus.COMPLETED, GameSessionStatus.ABANDONED):
                    new_completed_at = leap_time.utc_now()
                updated = s.model_copy(
                    update={
                        "status": status,
                        "score": score if score is not None else s.score,
                        "completed_at": new_completed_at,
                    }
                )
                self._sessions[self._sessions.index(s)] = updated
                return updated
        raise KeyError(f"session not found: {game_session_id}")

    async def add_to_score(
        self, session: Any, game_session_id: str, delta: int
    ) -> GameSessionDTO:
        _ = session
        for i, s in enumerate(self._sessions):
            if s.id == game_session_id:
                new_score = (s.score or 0) + delta
                updated = s.model_copy(update={"score": new_score})
                self._sessions[i] = updated
                return updated
        raise KeyError(f"session not found: {game_session_id}")

    async def get_all_for_player(
        self, session: Any, player_id: str
    ) -> List[GameSessionDTO]:
        return [s for s in self._sessions if s.player_id == player_id]

    def _aggregate_for_player(self, player_id: str) -> Dict[str, Any]:
        relevant = [
            s
            for s in self._sessions
            if s.player_id == player_id
            and s.status in (GameSessionStatus.COMPLETED, GameSessionStatus.ABANDONED)
        ]
        total_score = sum(s.score or 0 for s in relevant)
        games_completed = sum(1 for s in relevant if s.status == GameSessionStatus.COMPLETED)
        completion_times = [
            s.completed_at
            for s in relevant
            if s.status == GameSessionStatus.COMPLETED and s.completed_at is not None
        ]
        first_completion: Optional[datetime.datetime] = (
            min(completion_times) if completion_times else None
        )
        return {
            "total_score": total_score,
            "games_completed": games_completed,
            "first_completion": first_completion,
        }

    @staticmethod
    def _leaderboard_sort_key(entry: LeaderboardEntryDTO) -> tuple:
        # ORDER BY total_score DESC, games_completed DESC,
        # first_completion ASC NULLS LAST, display_name ASC
        fc_part: tuple[int, datetime.datetime]
        if entry.first_completion is not None:
            fc_part = (0, entry.first_completion)
        else:
            fc_part = (
                1,
                datetime.datetime.min.replace(tzinfo=pytz.UTC),
            )
        return (-entry.total_score, -entry.games_completed, fc_part, entry.display_name)

    async def get_leaderboard(self, session: Any) -> List[LeaderboardEntryDTO]:
        if self._player_dao is not None:
            players = self._player_dao.list_players()
        else:
            ordered_ids = sorted({s.player_id for s in self._sessions})
            players = [PlayerDTO(id=pid, display_name=pid) for pid in ordered_ids]

        entries: List[LeaderboardEntryDTO] = []
        for p in players:
            agg = self._aggregate_for_player(p.id)
            entries.append(
                LeaderboardEntryDTO(
                    player_id=p.id,
                    display_name=p.display_name,
                    total_score=agg["total_score"],
                    games_completed=agg["games_completed"],
                    first_completion=agg["first_completion"],
                )
            )
        entries.sort(key=self._leaderboard_sort_key)
        return entries


class FakeWikiRoundDAO:
    """In-memory wiki rounds — ordered by ``sequence_index``."""

    def __init__(self, rounds: Optional[List[WikiRoundDTO]] = None) -> None:
        self._rounds: List[WikiRoundDTO] = sorted(
            rounds or [],
            key=lambda r: r.sequence_index,
        )

    async def get_all_ordered(self, session: Any) -> List[WikiRoundDTO]:
        _ = session
        return list(self._rounds)


class FakeWikiPuzzleAttemptDAO:
    """In-memory wiki puzzle attempts."""

    def __init__(self, attempts: Optional[List[WikiPuzzleAttemptDTO]] = None) -> None:
        self._attempts: List[WikiPuzzleAttemptDTO] = list(attempts or [])

    async def get_by_game_session_and_round(
        self, session: Any, game_session_id: str, round_id: str
    ) -> Optional[WikiPuzzleAttemptDTO]:
        _ = session
        for a in self._attempts:
            if a.game_session_id == game_session_id and a.round_id == round_id:
                return a
        return None

    async def create_for_round(
        self,
        session: Any,
        game_session_id: str,
        round_id: str,
        start_title: str,
    ) -> WikiPuzzleAttemptDTO:
        _ = session
        from leap.types.wiki import WikiPuzzleAttemptStatus

        dto = WikiPuzzleAttemptDTO(
            id=str(uuid.uuid4()),
            game_session_id=game_session_id,
            round_id=round_id,
            status=WikiPuzzleAttemptStatus.ACTIVE,
            current_title=start_title,
            click_path=[],
            steps_taken=0,
            started_at=leap_time.utc_now(),
        )
        self._attempts.append(dto)
        return dto

    async def record_forward_navigation(
        self,
        session: Any,
        attempt_id: str,
        landed_canonical_title: str,
    ) -> WikiPuzzleAttemptDTO:
        _ = session

        for i, a in enumerate(self._attempts):
            if a.id != attempt_id:
                continue
            new_path = list(a.click_path) + [landed_canonical_title]
            updated = a.model_copy(
                update={
                    "steps_taken": a.steps_taken + 1,
                    "click_path": new_path,
                    "current_title": landed_canonical_title,
                }
            )
            self._attempts[i] = updated
            return updated
        raise KeyError(attempt_id)

    async def mark_timed_out(
        self,
        session: Any,
        attempt_id: str,
        *,
        time_ms: int,
        completed_at,
    ) -> WikiPuzzleAttemptDTO:
        _ = session
        from leap.types.wiki import WikiPuzzleAttemptStatus

        for i, a in enumerate(self._attempts):
            if a.id != attempt_id:
                continue
            updated = a.model_copy(
                update={
                    "status": WikiPuzzleAttemptStatus.TIMED_OUT,
                    "score": 0,
                    "time_ms": time_ms,
                    "completed_at": completed_at,
                }
            )
            self._attempts[i] = updated
            return updated
        raise KeyError(attempt_id)

    async def record_back_navigation(
        self,
        session: Any,
        attempt_id: str,
        previous_title: str,
    ) -> WikiPuzzleAttemptDTO:
        _ = session

        for i, a in enumerate(self._attempts):
            if a.id != attempt_id:
                continue
            new_path = list(a.click_path) + [previous_title]
            updated = a.model_copy(
                update={
                    "steps_taken": a.steps_taken + 1,
                    "click_path": new_path,
                    "current_title": previous_title,
                }
            )
            self._attempts[i] = updated
            return updated
        raise KeyError(attempt_id)

    async def complete_attempt(
        self,
        session: Any,
        attempt_id: str,
        *,
        score: int,
        time_ms: int,
        completed_at,
    ) -> WikiPuzzleAttemptDTO:
        _ = session
        from leap.types.wiki import WikiPuzzleAttemptStatus

        for i, a in enumerate(self._attempts):
            if a.id != attempt_id:
                continue
            updated = a.model_copy(
                update={
                    "status": WikiPuzzleAttemptStatus.COMPLETED,
                    "score": score,
                    "time_ms": time_ms,
                    "completed_at": completed_at,
                }
            )
            self._attempts[i] = updated
            return updated
        raise KeyError(attempt_id)


class FakeWikipediaClient:
    """Returns canned HTML per title for service tests."""

    def __init__(
        self,
        html_by_title: Optional[Dict[str, str]] = None,
        canonical_by_requested: Optional[Dict[str, str]] = None,
    ) -> None:
        self.html_by_title: Dict[str, str] = html_by_title or {}
        self.canonical_by_requested: Dict[str, str] = canonical_by_requested or {}

    async def fetch_article_html(self, title: str) -> WikiArticleDTO:
        canon = self.canonical_by_requested.get(title, title)
        html = self.html_by_title.get(canon)
        if html is None:
            html = self.html_by_title.get(title, "<section><p>stub</p></section>")
        return WikiArticleDTO(
            requested_title=title,
            canonical_title=canon,
            html=html,
        )


class FakeWikiHtmlRewriter:
    """Trivial rewriter for tests — passes HTML through with stable metadata."""

    def rewrite(self, html: str):
        from leap.types.wiki import RewrittenWikiHtmlDTO

        return RewrittenWikiHtmlDTO(html=html, internal_link_titles=[], removed_link_count=0)


class FakeRapidFireQuestionDAO:
    """In-memory rapid fire question store — matches ``RapidFireQuestionDAO`` surface."""

    def __init__(self, questions: Optional[List[RapidFireQuestionDTO]] = None) -> None:
        self._questions: List[RapidFireQuestionDTO] = questions or []

    async def get_all(self, session: Any) -> List[RapidFireQuestionDTO]:
        return list(self._questions)


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
        selected_option: Optional[int],
        time_ms: int,
    ) -> RapidFireAnswerDTO:
        dto = RapidFireAnswerDTO(
            id=str(uuid.uuid4()),
            game_session_id=game_session_id,
            question_id=question_id,
            correct=correct,
            skipped=skipped,
            selected_option=selected_option,
            time_ms=time_ms,
            answered_at=leap_time.utc_now(),
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


class FakeServiceContainer:
    """Wires real services to fake DAOs for HTTP-level unit tests."""

    def __init__(
        self,
        context_manager: FakeContextManager,
        player_dao: FakePlayerDAO,
        game_session_dao: FakeGameSessionDAO,
        rapid_fire_answer_dao: FakeRapidFireAnswerDAO,
        rapid_fire_question_dao: FakeRapidFireQuestionDAO,
        wiki_round_dao: FakeWikiRoundDAO,
        wiki_puzzle_attempt_dao: FakeWikiPuzzleAttemptDAO,
        wikipedia_client: FakeWikipediaClient,
        wiki_html_rewriter: FakeWikiHtmlRewriter,
        *,
        wiki_back_button_enabled: bool = False,
    ) -> None:
        self.context_manager = context_manager
        self.player_dao = player_dao
        self.game_session_dao = game_session_dao
        self.rapid_fire_answer_dao = rapid_fire_answer_dao
        self.rapid_fire_question_dao = rapid_fire_question_dao
        self.wiki_round_dao = wiki_round_dao
        self.wiki_puzzle_attempt_dao = wiki_puzzle_attempt_dao
        self.wikipedia_client = wikipedia_client
        self.wiki_html_rewriter = wiki_html_rewriter

        self.auth = AuthService(context_manager, player_dao)
        self.lobby = LobbyService(context_manager, game_session_dao)
        self.player_sessions = PlayerSessionService(context_manager, game_session_dao)
        self.rapid_fire = RapidFireService(
            context_manager,
            game_session_dao,
            rapid_fire_answer_dao,
            rapid_fire_question_dao,
        )
        self.wiki_speed_run = WikiSpeedRunService(
            context_manager,
            game_session_dao,
            wiki_round_dao,
            wiki_puzzle_attempt_dao,
            wikipedia_client,
            wiki_html_rewriter,
            back_button_enabled=wiki_back_button_enabled,
        )
        self.leaderboard = LeaderboardService(context_manager, game_session_dao)


def _default_wiki_rounds() -> List[WikiRoundDTO]:
    return [
        WikiRoundDTO(
            id="wr1",
            sequence_index=1,
            start_title="Biology",
            start_url="https://en.wikipedia.org/wiki/Biology",
            target_title="Attention",
            target_url="https://en.wikipedia.org/wiki/Attention",
            clue="Test clue",
            optimal_click_count=3,
            solution_path=["Biology", "Target"],
            time_limit_ms=180_000,
        ),
        WikiRoundDTO(
            id="wr2",
            sequence_index=2,
            start_title="Biology",
            start_url="https://en.wikipedia.org/wiki/Biology",
            target_title="Word embedding",
            target_url="https://en.wikipedia.org/wiki/Word_embedding",
            clue="Second",
            optimal_click_count=3,
            solution_path=[],
            time_limit_ms=180_000,
        ),
    ]


def make_fake_container(
    *,
    context_manager: Optional[FakeContextManager] = None,
    players: Optional[Dict[str, PlayerDTO]] = None,
    sessions: Optional[List[GameSessionDTO]] = None,
    rapid_fire_questions: Optional[List[RapidFireQuestionDTO]] = None,
    wiki_rounds: Optional[List[WikiRoundDTO]] = None,
    player_dao: Optional[FakePlayerDAO] = None,
    game_session_dao: Optional[FakeGameSessionDAO] = None,
    rapid_fire_answer_dao: Optional[FakeRapidFireAnswerDAO] = None,
    rapid_fire_question_dao: Optional[FakeRapidFireQuestionDAO] = None,
    wiki_round_dao: Optional[FakeWikiRoundDAO] = None,
    wiki_puzzle_attempt_dao: Optional[FakeWikiPuzzleAttemptDAO] = None,
    wikipedia_client: Optional[FakeWikipediaClient] = None,
    wiki_html_rewriter: Optional[FakeWikiHtmlRewriter] = None,
    wiki_back_button_enabled: bool = False,
) -> FakeServiceContainer:
    """Build a ``FakeServiceContainer`` with sensible in-memory defaults.

    Override individual DAOs when a test needs full control. When ``player_dao``
    is auto-created, ``FakeGameSessionDAO`` receives that same instance so
    ``get_leaderboard`` can include every registered player (0-score rows).
    """
    ctx = context_manager or FakeContextManager()
    pdao = player_dao or FakePlayerDAO(players=players)
    rf_answers = rapid_fire_answer_dao or FakeRapidFireAnswerDAO()
    rf_questions = rapid_fire_question_dao or FakeRapidFireQuestionDAO(
        questions=rapid_fire_questions
    )
    gdao = game_session_dao or FakeGameSessionDAO(
        sessions=sessions,
        player_dao=pdao,
    )
    wrdao = wiki_round_dao or FakeWikiRoundDAO(
        rounds=wiki_rounds if wiki_rounds is not None else _default_wiki_rounds()
    )
    wadao = wiki_puzzle_attempt_dao or FakeWikiPuzzleAttemptDAO()
    wiki_client = wikipedia_client or FakeWikipediaClient()
    wrew = wiki_html_rewriter or FakeWikiHtmlRewriter()
    return FakeServiceContainer(
        ctx,
        pdao,
        gdao,
        rf_answers,
        rf_questions,
        wrdao,
        wadao,
        wiki_client,
        wrew,
        wiki_back_button_enabled=wiki_back_button_enabled,
    )
