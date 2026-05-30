"""Wikipedia Speed Run — session and puzzle-attempt orchestration."""

from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from leap.core.common import time as leap_time
from leap.core.context_manager import ContextManager
from leap.dao.game_session_dao import GameSessionDAO
from leap.dao.wiki_puzzle_attempt_dao import WikiPuzzleAttemptDAO
from leap.dao.wiki_round_dao import WikiRoundDAO
from leap.games.wiki.html_rewriter import WikiHtmlRewriter
from leap.games.wiki.scoring import compute_puzzle_score
from leap.games.wiki.wikipedia_client import WikipediaClient
from leap.service.exceptions import (
    NoWikiRoundsAvailableException,
    SessionAlreadyCompletedException,
    SessionNotFoundException,
    WikiBackButtonDisabledException,
    WikiNoPreviousPageException,
    WikiPuzzleNotActiveException,
    WikiPuzzleTimerExpiredException,
)
from leap.types.game import GameSessionDTO, GameSessionStatus
from leap.types.wiki import (
    WikiActivePuzzleDTO,
    WikiNavigateActiveDTO,
    WikiNavigatePayload,
    WikiNavigatePuzzleCompletedDTO,
    WikiPlayActiveDTO,
    WikiPlayPayload,
    WikiPlayTerminalDTO,
    WikiPuzzleAttemptDTO,
    WikiPuzzleAttemptStatus,
    WikiPuzzleResultDTO,
    WikiRoundDTO,
)


def _time_remaining_ms(started_at, time_limit_ms: int, now) -> int:
    elapsed_ms = int((now - started_at).total_seconds() * 1000)
    return max(0, time_limit_ms - elapsed_ms)


def _wiki_targets_match(canonical_title: str, target_title: str) -> bool:
    a = canonical_title.replace("_", " ").strip().casefold()
    b = target_title.replace("_", " ").strip().casefold()
    return a == b


def _previous_page_title(attempt: WikiPuzzleAttemptDTO, round_start_title: str) -> Optional[str]:
    path = attempt.click_path
    if not path:
        return None
    if len(path) == 1:
        return round_start_title
    return path[-2]


class WikiSpeedRunService:
    def __init__(
        self,
        ctx: ContextManager,
        game_session_dao: GameSessionDAO,
        wiki_round_dao: WikiRoundDAO,
        wiki_puzzle_attempt_dao: WikiPuzzleAttemptDAO,
        wikipedia_client: WikipediaClient,
        html_rewriter: WikiHtmlRewriter,
        *,
        back_button_enabled: bool = False,
    ) -> None:
        self.ctx = ctx
        self.game_session_dao = game_session_dao
        self.wiki_round_dao = wiki_round_dao
        self.wiki_puzzle_attempt_dao = wiki_puzzle_attempt_dao
        self.wikipedia_client = wikipedia_client
        self.html_rewriter = html_rewriter
        self.back_button_enabled = back_button_enabled
        self._rounds: List[WikiRoundDTO] = []

    async def initialize(self, session: AsyncSession) -> None:
        self._rounds = await self.wiki_round_dao.get_all_ordered(session)

    def _first_round(self) -> WikiRoundDTO:
        if not self._rounds:
            raise NoWikiRoundsAvailableException()
        return self._rounds[0]

    def _puzzle_count(self) -> int:
        return len(self._rounds)

    def _is_last_round(self, puzzle_round: WikiRoundDTO) -> bool:
        return puzzle_round.sequence_index == self._rounds[-1].sequence_index

    async def _gather_completed_results(
        self, session: AsyncSession, game_session_id: str
    ) -> List[WikiPuzzleResultDTO]:
        out: List[WikiPuzzleResultDTO] = []
        for rnd in self._rounds:
            att = await self.wiki_puzzle_attempt_dao.get_by_game_session_and_round(
                session, game_session_id, rnd.id
            )
            if att is None:
                continue
            if att.status in (WikiPuzzleAttemptStatus.COMPLETED, WikiPuzzleAttemptStatus.TIMED_OUT):
                out.append(self._result_from_attempt(rnd, att))
        return out

    def _result_from_attempt(
        self, puzzle_round: WikiRoundDTO, attempt: WikiPuzzleAttemptDTO
    ) -> WikiPuzzleResultDTO:
        return WikiPuzzleResultDTO(
            round_id=puzzle_round.id,
            puzzle_index=puzzle_round.sequence_index,
            clue=puzzle_round.clue,
            target_title=puzzle_round.target_title,
            optimal_click_count=puzzle_round.optimal_click_count,
            steps_taken=attempt.steps_taken,
            time_ms=attempt.time_ms,
            score=attempt.score or 0,
            status=attempt.status,
        )

    async def _gather_abandon_results(
        self, session: AsyncSession, game_session_id: str
    ) -> List[WikiPuzzleResultDTO]:
        out: List[WikiPuzzleResultDTO] = []
        for rnd in self._rounds:
            att = await self.wiki_puzzle_attempt_dao.get_by_game_session_and_round(
                session, game_session_id, rnd.id
            )
            if att is not None and att.status in (
                WikiPuzzleAttemptStatus.COMPLETED,
                WikiPuzzleAttemptStatus.TIMED_OUT,
            ):
                out.append(self._result_from_attempt(rnd, att))
            else:
                out.append(
                    WikiPuzzleResultDTO(
                        round_id=rnd.id,
                        puzzle_index=rnd.sequence_index,
                        clue=rnd.clue,
                        target_title=rnd.target_title,
                        optimal_click_count=rnd.optimal_click_count,
                        steps_taken=0,
                        time_ms=None,
                        score=0,
                        status=WikiPuzzleAttemptStatus.ABANDONED,
                    )
                )
        return out

    def _should_offer_back(self, attempt: WikiPuzzleAttemptDTO) -> bool:
        return self.back_button_enabled and bool(attempt.click_path)

    async def _resolve_current_round_and_attempt(
        self, session: AsyncSession, game_session_id: str
    ) -> Optional[Tuple[WikiRoundDTO, WikiPuzzleAttemptDTO]]:
        """Active puzzle for this session, creating the next attempt when the prior round finished."""
        for rnd in self._rounds:
            att = await self.wiki_puzzle_attempt_dao.get_by_game_session_and_round(
                session, game_session_id, rnd.id
            )
            if att is None:
                created = await self.wiki_puzzle_attempt_dao.create_for_round(
                    session,
                    game_session_id,
                    rnd.id,
                    rnd.start_title,
                )
                return rnd, created
            if att.status == WikiPuzzleAttemptStatus.ACTIVE:
                return rnd, att
        return None

    async def _terminal_payload_for_non_active_session(
        self, session: AsyncSession, game_session: GameSessionDTO
    ) -> WikiPlayTerminalDTO:
        results: List[WikiPuzzleResultDTO] = []
        terminal_state: str
        if game_session.status == GameSessionStatus.COMPLETED:
            results = await self._gather_completed_results(session, game_session.id)
            terminal_state = "completed"
        elif game_session.status == GameSessionStatus.ABANDONED:
            results = await self._gather_abandon_results(session, game_session.id)
            terminal_state = "abandoned"
        else:
            terminal_state = game_session.status.value
        return WikiPlayTerminalDTO(
            state=terminal_state,  # type: ignore[arg-type]
            total_score=game_session.score or 0,
            results=results,
        )

    async def _finalize_timed_out_puzzle(
        self,
        session: AsyncSession,
        player_id: str,
        puzzle_round: WikiRoundDTO,
        attempt: WikiPuzzleAttemptDTO,
        now,
    ) -> None:
        time_ms = int((now - attempt.started_at).total_seconds() * 1000)
        await self.wiki_puzzle_attempt_dao.mark_timed_out(
            session,
            attempt.id,
            time_ms=time_ms,
            completed_at=now,
        )
        if not self._is_last_round(puzzle_round):
            return
        game_session = await self.game_session_dao.get_by_player_and_game(
            session, player_id, "wiki"
        )
        if game_session is None:
            raise SessionNotFoundException(player_id, "wiki")
        await self.game_session_dao.update_status(
            session,
            game_session.id,
            GameSessionStatus.COMPLETED,
            score=game_session.score,
        )

    async def _wiki_active_flow_with_timer_resolution(
        self, session: AsyncSession, player_id: str
    ) -> WikiPlayPayload:
        while True:
            game_session = await self.game_session_dao.get_by_player_and_game(
                session, player_id, "wiki"
            )
            if game_session is None:
                raise SessionNotFoundException(player_id, "wiki")
            if game_session.status != GameSessionStatus.ACTIVE:
                return await self._terminal_payload_for_non_active_session(session, game_session)

            resolved = await self._resolve_current_round_and_attempt(session, game_session.id)
            if resolved is None:
                return WikiPlayTerminalDTO(
                    state="completed",
                    total_score=game_session.score or 0,
                    results=await self._gather_completed_results(session, game_session.id),
                )

            puzzle_round, attempt = resolved
            now = leap_time.utc_now()
            remaining = _time_remaining_ms(attempt.started_at, puzzle_round.time_limit_ms, now)
            if remaining > 0:
                completed_attempts = await self._gather_completed_results(session, game_session.id)
                return await self._build_active_response(
                    session, game_session, puzzle_round, attempt, completed_attempts
                )

            await self._finalize_timed_out_puzzle(session, player_id, puzzle_round, attempt, now)

    async def play(self, player_id: str) -> WikiPlayPayload:
        if not self._rounds:
            _ = self._first_round()

        async with self.ctx.session() as session:
            game_session = await self.game_session_dao.get_by_player_and_game(
                session, player_id, "wiki"
            )

            if game_session is None:
                game_session = await self.game_session_dao.create(session, player_id, "wiki")

            if game_session.status != GameSessionStatus.ACTIVE:
                return await self._terminal_payload_for_non_active_session(session, game_session)

            return await self._wiki_active_flow_with_timer_resolution(session, player_id)

    async def timeout(self, player_id: str) -> WikiPlayPayload:
        if not self._rounds:
            _ = self._first_round()

        async with self.ctx.session() as session:
            game_session = await self.game_session_dao.get_by_player_and_game(
                session, player_id, "wiki"
            )
            if game_session is None:
                raise SessionNotFoundException(player_id, "wiki")
            if game_session.status != GameSessionStatus.ACTIVE:
                return await self._terminal_payload_for_non_active_session(session, game_session)
            return await self._wiki_active_flow_with_timer_resolution(session, player_id)

    async def navigate(self, player_id: str, target_title: str) -> WikiNavigatePayload:
        if not self._rounds:
            _ = self._first_round()

        now = leap_time.utc_now()

        async with self.ctx.session() as session:
            game_session = await self.game_session_dao.get_by_player_and_game(
                session, player_id, "wiki"
            )
            if game_session is None:
                raise SessionNotFoundException(player_id, "wiki")
            if game_session.status != GameSessionStatus.ACTIVE:
                raise WikiPuzzleNotActiveException()

            resolved = await self._resolve_current_round_and_attempt(session, game_session.id)
            if resolved is None:
                raise WikiPuzzleNotActiveException()
            puzzle_round, attempt = resolved

            if attempt.status != WikiPuzzleAttemptStatus.ACTIVE:
                raise WikiPuzzleNotActiveException()

            remaining = _time_remaining_ms(attempt.started_at, puzzle_round.time_limit_ms, now)
            if remaining <= 0:
                raise WikiPuzzleTimerExpiredException()

            article = await self.wikipedia_client.fetch_article_html(target_title)
            landed = article.canonical_title

            attempt = await self.wiki_puzzle_attempt_dao.record_forward_navigation(
                session, attempt.id, landed
            )

            if _wiki_targets_match(landed, puzzle_round.target_title):
                time_ms = int((now - attempt.started_at).total_seconds() * 1000)
                puzzle_score = compute_puzzle_score(
                    clicks_taken=attempt.steps_taken,
                    optimal_click_count=puzzle_round.optimal_click_count,
                    time_ms=time_ms,
                    time_limit_ms=puzzle_round.time_limit_ms,
                    timed_out=False,
                )
                attempt = await self.wiki_puzzle_attempt_dao.complete_attempt(
                    session,
                    attempt.id,
                    score=puzzle_score,
                    time_ms=time_ms,
                    completed_at=now,
                )
                game_session = await self.game_session_dao.add_to_score(
                    session, game_session.id, puzzle_score
                )
                puzzle_result = self._result_from_attempt(puzzle_round, attempt)
                last = self._is_last_round(puzzle_round)
                if last:
                    game_session = await self.game_session_dao.update_status(
                        session,
                        game_session.id,
                        GameSessionStatus.COMPLETED,
                        score=game_session.score,
                    )
                return WikiNavigatePuzzleCompletedDTO(
                    puzzle_result=puzzle_result,
                    next_puzzle_available=not last,
                    total_score=game_session.score or 0,
                )

            refreshed_game = await self.game_session_dao.get_by_player_and_game(
                session, player_id, "wiki"
            )
            if refreshed_game is None:
                raise SessionNotFoundException(player_id, "wiki")

            rewritten = self.html_rewriter.rewrite(article.html)
            remaining_after = _time_remaining_ms(
                attempt.started_at, puzzle_round.time_limit_ms, now
            )
            current = WikiActivePuzzleDTO(
                game_session_id=refreshed_game.id,
                attempt_id=attempt.id,
                round_id=puzzle_round.id,
                puzzle_index=puzzle_round.sequence_index,
                puzzle_count=self._puzzle_count(),
                clue=puzzle_round.clue,
                current_title=attempt.current_title,
                time_limit_ms=puzzle_round.time_limit_ms,
                time_remaining_ms=remaining_after,
                steps_taken=attempt.steps_taken,
                click_path=list(attempt.click_path),
                article_html=rewritten.html,
                back_enabled=self._should_offer_back(attempt),
            )
            return WikiNavigateActiveDTO(current=current)

    async def _build_active_response(
        self,
        session: AsyncSession,
        game_session: GameSessionDTO,
        puzzle_round: WikiRoundDTO,
        attempt: WikiPuzzleAttemptDTO,
        completed_attempts: List[WikiPuzzleResultDTO],
    ) -> WikiPlayActiveDTO:
        article = await self.wikipedia_client.fetch_article_html(attempt.current_title)
        rewritten = self.html_rewriter.rewrite(article.html)
        now = leap_time.utc_now()
        remaining = _time_remaining_ms(attempt.started_at, puzzle_round.time_limit_ms, now)
        current = WikiActivePuzzleDTO(
            game_session_id=game_session.id,
            attempt_id=attempt.id,
            round_id=puzzle_round.id,
            puzzle_index=puzzle_round.sequence_index,
            puzzle_count=self._puzzle_count(),
            clue=puzzle_round.clue,
            current_title=attempt.current_title,
            time_limit_ms=puzzle_round.time_limit_ms,
            time_remaining_ms=remaining,
            steps_taken=attempt.steps_taken,
            click_path=list(attempt.click_path),
            article_html=rewritten.html,
            back_enabled=self._should_offer_back(attempt),
        )
        return WikiPlayActiveDTO(
            total_score=game_session.score or 0,
            completed_count=len(completed_attempts),
            current=current,
            completed_attempts=completed_attempts,
        )

    async def back(self, player_id: str) -> WikiNavigatePayload:
        if not self._rounds:
            _ = self._first_round()

        if not self.back_button_enabled:
            raise WikiBackButtonDisabledException()

        now = leap_time.utc_now()

        async with self.ctx.session() as session:
            game_session = await self.game_session_dao.get_by_player_and_game(
                session, player_id, "wiki"
            )
            if game_session is None:
                raise SessionNotFoundException(player_id, "wiki")
            if game_session.status != GameSessionStatus.ACTIVE:
                raise WikiPuzzleNotActiveException()

            resolved = await self._resolve_current_round_and_attempt(session, game_session.id)
            if resolved is None:
                raise WikiPuzzleNotActiveException()
            puzzle_round, attempt = resolved

            if attempt.status != WikiPuzzleAttemptStatus.ACTIVE:
                raise WikiPuzzleNotActiveException()

            remaining = _time_remaining_ms(attempt.started_at, puzzle_round.time_limit_ms, now)
            if remaining <= 0:
                raise WikiPuzzleTimerExpiredException()

            prev_title = _previous_page_title(attempt, puzzle_round.start_title)
            if prev_title is None:
                raise WikiNoPreviousPageException()

            attempt = await self.wiki_puzzle_attempt_dao.record_back_navigation(
                session, attempt.id, prev_title
            )

            article = await self.wikipedia_client.fetch_article_html(attempt.current_title)
            rewritten = self.html_rewriter.rewrite(article.html)
            remaining_after = _time_remaining_ms(
                attempt.started_at, puzzle_round.time_limit_ms, now
            )

            refreshed_game = await self.game_session_dao.get_by_player_and_game(
                session, player_id, "wiki"
            )
            if refreshed_game is None:
                raise SessionNotFoundException(player_id, "wiki")

            current = WikiActivePuzzleDTO(
                game_session_id=refreshed_game.id,
                attempt_id=attempt.id,
                round_id=puzzle_round.id,
                puzzle_index=puzzle_round.sequence_index,
                puzzle_count=self._puzzle_count(),
                clue=puzzle_round.clue,
                current_title=attempt.current_title,
                time_limit_ms=puzzle_round.time_limit_ms,
                time_remaining_ms=remaining_after,
                steps_taken=attempt.steps_taken,
                click_path=list(attempt.click_path),
                article_html=rewritten.html,
                back_enabled=self._should_offer_back(attempt),
            )
            return WikiNavigateActiveDTO(current=current)

    async def abandon(self, player_id: str) -> WikiPlayTerminalDTO:
        if not self._rounds:
            _ = self._first_round()

        async with self.ctx.session() as session:
            game_session = await self.game_session_dao.get_by_player_and_game(
                session, player_id, "wiki"
            )
            if game_session is None:
                raise SessionNotFoundException(player_id, "wiki")
            if game_session.status != GameSessionStatus.ACTIVE:
                raise SessionAlreadyCompletedException(game_session.id, game_session.status.value)

            await self.game_session_dao.update_status(
                session,
                game_session.id,
                GameSessionStatus.ABANDONED,
            )
            refreshed = await self.game_session_dao.get_by_player_and_game(
                session, player_id, "wiki"
            )
            if refreshed is None:
                raise SessionNotFoundException(player_id, "wiki")

            results = await self._gather_abandon_results(session, game_session.id)
            return WikiPlayTerminalDTO(
                state="abandoned",
                total_score=refreshed.score or 0,
                results=results,
            )
