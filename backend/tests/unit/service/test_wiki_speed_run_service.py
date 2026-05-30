"""Wiki Speed Run service tests (Sub-1 play / resume)."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from leap.games.wiki.service import WikiSpeedRunService
from leap.service.exceptions import (
    WikiBackButtonDisabledException,
    WikiNoPreviousPageException,
)
from leap.types.game import GameSessionDTO, GameSessionStatus
from leap.types.wiki import (
    WikiNavigateActiveDTO,
    WikiNavigatePuzzleCompletedDTO,
    WikiPlayActiveDTO,
    WikiPlayTerminalDTO,
    WikiPuzzleAttemptStatus,
    WikiRoundDTO,
)
from tests.fakes import (
    FakeContextManager,
    FakeGameSessionDAO,
    FakeWikiHtmlRewriter,
    FakeWikipediaClient,
    FakeWikiPuzzleAttemptDAO,
    FakeWikiRoundDAO,
)


def _sample_round() -> WikiRoundDTO:
    return WikiRoundDTO(
        id="r1",
        sequence_index=1,
        start_title="Alpha",
        start_url="https://en.wikipedia.org/wiki/Alpha",
        target_title="Omega",
        target_url="https://en.wikipedia.org/wiki/Omega",
        clue="What comes after?",
        optimal_click_count=2,
        solution_path=["Alpha", "Omega"],
        time_limit_ms=120_000,
    )


def _wiki_round(i: int, *, tid: str | None = None) -> WikiRoundDTO:
    target = tid or f"T{i}"
    return WikiRoundDTO(
        id=f"r{i}",
        sequence_index=i,
        start_title=f"S{i}",
        start_url="u",
        target_title=target,
        target_url="u",
        clue=f"Round {i}",
        optimal_click_count=1,
        solution_path=[],
        time_limit_ms=120_000,
    )


def _wiki_html_client_for_targets(max_index: int) -> FakeWikipediaClient:
    return FakeWikipediaClient(
        {f"T{i}": f"<section><p>p{i}</p></section>" for i in range(1, max_index + 1)}
    )


def _build_svc(
    *,
    rounds: list[WikiRoundDTO] | None = None,
    wikipedia: FakeWikipediaClient | None = None,
    back_button_enabled: bool = False,
) -> WikiSpeedRunService:
    ctx = FakeContextManager()
    gdao = FakeGameSessionDAO()
    rdao = FakeWikiRoundDAO(rounds or [_sample_round()])
    adao = FakeWikiPuzzleAttemptDAO()
    client = wikipedia or FakeWikipediaClient(
        {"Alpha": '<section id="bodyContent"><p>Body</p></section>'}
    )
    rew = FakeWikiHtmlRewriter()
    return WikiSpeedRunService(
        ctx,
        gdao,
        rdao,
        adao,
        client,
        rew,
        back_button_enabled=back_button_enabled,
    )


@pytest.mark.asyncio
async def test_play_creates_wiki_session_and_first_attempt() -> None:
    t0 = datetime(2026, 5, 17, 12, 0, 0, tzinfo=timezone.utc)
    svc = _build_svc()
    with patch("leap.core.common.time.utc_now", return_value=t0):
        async with svc.ctx.session() as session:
            await svc.initialize(session)
        out = await svc.play("emp001")

    assert isinstance(out, WikiPlayActiveDTO)
    assert out.state == "active"
    assert out.current.clue == "What comes after?"
    assert out.current.puzzle_index == 1
    assert out.current.puzzle_count == 1
    assert out.current.article_html == '<section id="bodyContent"><p>Body</p></section>'
    assert out.current.time_remaining_ms == 120_000
    assert out.current.steps_taken == 0
    assert out.completed_attempts == []

    sessions = svc.game_session_dao._sessions  # noqa: SLF001
    assert len(sessions) == 1
    assert sessions[0].game_id == "wiki"
    assert sessions[0].player_id == "emp001"

    assert len(svc.wiki_puzzle_attempt_dao._attempts) == 1  # noqa: SLF001
    att = svc.wiki_puzzle_attempt_dao._attempts[0]  # noqa: SLF001
    assert att.round_id == "r1"
    assert att.current_title == "Alpha"


@pytest.mark.asyncio
async def test_play_resume_preserves_started_at_and_reduces_time_remaining() -> None:
    t0 = datetime(2026, 5, 17, 12, 0, 0, tzinfo=timezone.utc)
    svc = _build_svc()
    with patch("leap.core.common.time.utc_now", return_value=t0):
        async with svc.ctx.session() as session:
            await svc.initialize(session)
        first = await svc.play("emp001")

    assert first.current.time_remaining_ms == 120_000

    t1 = t0 + timedelta(seconds=30)
    with patch("leap.core.common.time.utc_now", return_value=t1):
        second = await svc.play("emp001")

    assert isinstance(second, WikiPlayActiveDTO)
    assert second.current.attempt_id == first.current.attempt_id
    assert second.current.time_remaining_ms == 120_000 - 30_000


@pytest.mark.asyncio
async def test_play_completed_session_returns_terminal_payload() -> None:
    t0 = datetime(2026, 5, 17, 12, 0, 0, tzinfo=timezone.utc)
    existing = GameSessionDTO(
        id="gs-done",
        player_id="emp001",
        game_id="wiki",
        status=GameSessionStatus.COMPLETED,
        score=500,
        started_at=t0,
        completed_at=t0 + timedelta(minutes=5),
    )
    ctx = FakeContextManager()
    gdao = FakeGameSessionDAO(sessions=[existing])
    rdao = FakeWikiRoundDAO([_sample_round()])
    adao = FakeWikiPuzzleAttemptDAO()
    svc = WikiSpeedRunService(
        ctx,
        gdao,
        rdao,
        adao,
        FakeWikipediaClient(),
        FakeWikiHtmlRewriter(),
    )
    async with svc.ctx.session() as session:
        await svc.initialize(session)
    out = await svc.play("emp001")
    assert out.state == "completed"
    assert out.total_score == 500
    assert out.results == []


@pytest.mark.asyncio
async def test_puzzle_count_follows_round_list_length() -> None:
    r1 = _sample_round()
    r2 = WikiRoundDTO(
        id="r2",
        sequence_index=2,
        start_title="Beta",
        start_url="u",
        target_title="T",
        target_url="u2",
        clue="x",
        optimal_click_count=1,
        solution_path=[],
        time_limit_ms=60_000,
    )
    svc = _build_svc(rounds=[r1, r2])
    async with svc.ctx.session() as session:
        await svc.initialize(session)
    out = await svc.play("x")
    assert isinstance(out, WikiPlayActiveDTO)
    assert out.current.puzzle_count == 2


@pytest.mark.asyncio
async def test_navigate_increments_steps_and_appends_canonical_title() -> None:
    t0 = datetime(2026, 5, 17, 12, 0, 0, tzinfo=timezone.utc)
    wiki = FakeWikipediaClient(
        {
            "Beta": "<section><p>p2</p></section>",
            "Gamma": "<section><p>p3</p></section>",
        },
        canonical_by_requested={"Beta": "Beta canon"},
    )
    svc = _build_svc(wikipedia=wiki)
    with patch("leap.core.common.time.utc_now", return_value=t0):
        async with svc.ctx.session() as session:
            await svc.initialize(session)
        await svc.play("emp001")
        nav = await svc.navigate("emp001", "Beta")
    assert isinstance(nav, WikiNavigateActiveDTO)
    assert nav.current.steps_taken == 1
    assert nav.current.click_path == ["Beta canon"]
    assert nav.current.current_title == "Beta canon"


@pytest.mark.asyncio
async def test_navigate_completes_on_target_and_returns_puzzle_completed() -> None:
    t0 = datetime(2026, 5, 17, 12, 0, 0, tzinfo=timezone.utc)
    rnd = WikiRoundDTO(
        id="r1",
        sequence_index=1,
        start_title="Alpha",
        start_url="u",
        target_title="Omega",
        target_url="u2",
        clue="What comes after?",
        optimal_click_count=1,
        solution_path=[],
        time_limit_ms=120_000,
    )
    wiki = FakeWikipediaClient(
        {"Omega": "<section><p>win</p></section>"},
    )
    svc = WikiSpeedRunService(
        FakeContextManager(),
        FakeGameSessionDAO(),
        FakeWikiRoundDAO([rnd]),
        FakeWikiPuzzleAttemptDAO(),
        wiki,
        FakeWikiHtmlRewriter(),
        back_button_enabled=False,
    )
    with patch("leap.core.common.time.utc_now", return_value=t0):
        async with svc.ctx.session() as session:
            await svc.initialize(session)
        await svc.play("emp001")
        out = await svc.navigate("emp001", "Omega")
    assert isinstance(out, WikiNavigatePuzzleCompletedDTO)
    assert out.puzzle_result.steps_taken == 1
    assert out.puzzle_result.target_title == "Omega"
    assert out.puzzle_result.status.value == "completed"
    assert out.next_puzzle_available is False
    assert out.total_score == out.puzzle_result.score
    assert out.puzzle_result.score == 200


@pytest.mark.asyncio
async def test_navigate_non_final_puzzle_signals_next_and_play_opens_next_round() -> None:
    t0 = datetime(2026, 5, 17, 12, 0, 0, tzinfo=timezone.utc)
    wiki = _wiki_html_client_for_targets(2)
    svc = WikiSpeedRunService(
        FakeContextManager(),
        FakeGameSessionDAO(),
        FakeWikiRoundDAO([_wiki_round(1), _wiki_round(2)]),
        FakeWikiPuzzleAttemptDAO(),
        wiki,
        FakeWikiHtmlRewriter(),
    )
    with patch("leap.core.common.time.utc_now", return_value=t0):
        async with svc.ctx.session() as session:
            await svc.initialize(session)
        await svc.play("emp001")
        done_one = await svc.navigate("emp001", "T1")

    assert isinstance(done_one, WikiNavigatePuzzleCompletedDTO)
    assert done_one.next_puzzle_available is True
    assert done_one.puzzle_result.puzzle_index == 1

    with patch("leap.core.common.time.utc_now", return_value=t0):
        second = await svc.play("emp001")

    assert isinstance(second, WikiPlayActiveDTO)
    assert second.current.puzzle_index == 2
    assert second.current.round_id == "r2"
    assert second.completed_count == 1
    assert len(second.completed_attempts) == 1


@pytest.mark.asyncio
async def test_five_puzzles_completes_session_aggregate_score_and_terminal_play_payload() -> None:
    t0 = datetime(2026, 5, 17, 12, 0, 0, tzinfo=timezone.utc)
    rounds = [_wiki_round(i) for i in range(1, 6)]
    wiki = _wiki_html_client_for_targets(5)
    gdao = FakeGameSessionDAO()
    svc = WikiSpeedRunService(
        FakeContextManager(),
        gdao,
        FakeWikiRoundDAO(rounds),
        FakeWikiPuzzleAttemptDAO(),
        wiki,
        FakeWikiHtmlRewriter(),
    )
    with patch("leap.core.common.time.utc_now", return_value=t0):
        async with svc.ctx.session() as session:
            await svc.initialize(session)
        await svc.play("emp777")
        for i in range(1, 6):
            nav_out = await svc.navigate("emp777", f"T{i}")
            assert isinstance(nav_out, WikiNavigatePuzzleCompletedDTO)
            assert nav_out.next_puzzle_available == (i < 5)
            if i < 5:
                nxt = await svc.play("emp777")
                assert isinstance(nxt, WikiPlayActiveDTO)
                assert nxt.current.puzzle_index == i + 1

        final_play = await svc.play("emp777")

    assert isinstance(final_play, WikiPlayTerminalDTO)
    assert final_play.state == "completed"
    assert len(final_play.results) == 5
    assert final_play.total_score == sum(r.score for r in final_play.results)

    wiki_session = await gdao.get_by_player_and_game(None, "emp777", "wiki")
    assert wiki_session is not None
    assert wiki_session.status.value == "completed"
    assert wiki_session.score == final_play.total_score


@pytest.mark.asyncio
async def test_play_auto_times_out_stale_active_attempt_and_opens_next_puzzle() -> None:
    t0 = datetime(2026, 5, 17, 12, 0, 0, tzinfo=timezone.utc)
    wiki = _wiki_html_client_for_targets(2)
    svc = WikiSpeedRunService(
        FakeContextManager(),
        FakeGameSessionDAO(),
        FakeWikiRoundDAO([_wiki_round(1), _wiki_round(2)]),
        FakeWikiPuzzleAttemptDAO(),
        wiki,
        FakeWikiHtmlRewriter(),
    )
    with patch("leap.core.common.time.utc_now", return_value=t0):
        async with svc.ctx.session() as session:
            await svc.initialize(session)
        first = await svc.play("emp-stale")
    assert isinstance(first, WikiPlayActiveDTO)
    att0 = svc.wiki_puzzle_attempt_dao._attempts[0]  # noqa: SLF001
    stale_start = t0 - timedelta(minutes=5)
    svc.wiki_puzzle_attempt_dao._attempts[0] = att0.model_copy(update={"started_at": stale_start})  # noqa: SLF001

    with patch("leap.core.common.time.utc_now", return_value=t0):
        second = await svc.play("emp-stale")

    assert isinstance(second, WikiPlayActiveDTO)
    assert second.current.puzzle_index == 2
    assert second.current.time_remaining_ms == 120_000
    updated_r1 = svc.wiki_puzzle_attempt_dao._attempts[0]  # noqa: SLF001
    assert updated_r1.status == WikiPuzzleAttemptStatus.TIMED_OUT
    assert updated_r1.score == 0


@pytest.mark.asyncio
async def test_timeout_early_leaves_attempt_active_with_server_remaining_time() -> None:
    t0 = datetime(2026, 5, 17, 12, 0, 0, tzinfo=timezone.utc)
    svc = _build_svc()
    with patch("leap.core.common.time.utc_now", return_value=t0):
        async with svc.ctx.session() as session:
            await svc.initialize(session)
        _ = await svc.play("emp001")
    t1 = t0 + timedelta(seconds=10)
    with patch("leap.core.common.time.utc_now", return_value=t1):
        out = await svc.timeout("emp001")
    assert isinstance(out, WikiPlayActiveDTO)
    assert out.current.time_remaining_ms == 120_000 - 10_000


@pytest.mark.asyncio
async def test_timeout_when_server_expired_advances_like_play() -> None:
    t0 = datetime(2026, 5, 17, 12, 0, 0, tzinfo=timezone.utc)
    wiki = _wiki_html_client_for_targets(2)
    svc = WikiSpeedRunService(
        FakeContextManager(),
        FakeGameSessionDAO(),
        FakeWikiRoundDAO([_wiki_round(1), _wiki_round(2)]),
        FakeWikiPuzzleAttemptDAO(),
        wiki,
        FakeWikiHtmlRewriter(),
    )
    with patch("leap.core.common.time.utc_now", return_value=t0):
        async with svc.ctx.session() as session:
            await svc.initialize(session)
        _ = await svc.play("emp-to")
    att0 = svc.wiki_puzzle_attempt_dao._attempts[0]  # noqa: SLF001
    svc.wiki_puzzle_attempt_dao._attempts[0] = att0.model_copy(  # noqa: SLF001
        update={"started_at": t0 - timedelta(minutes=5)}
    )

    with patch("leap.core.common.time.utc_now", return_value=t0):
        out = await svc.timeout("emp-to")

    assert isinstance(out, WikiPlayActiveDTO)
    assert out.current.puzzle_index == 2


@pytest.mark.asyncio
async def test_timeout_on_final_puzzle_completes_session() -> None:
    t0 = datetime(2026, 5, 17, 12, 0, 0, tzinfo=timezone.utc)
    wiki = FakeWikipediaClient({"OnlyStart": "<section><p>x</p></section>"})
    gdao = FakeGameSessionDAO()
    svc = WikiSpeedRunService(
        FakeContextManager(),
        gdao,
        FakeWikiRoundDAO([_wiki_round(1)]),
        FakeWikiPuzzleAttemptDAO(),
        wiki,
        FakeWikiHtmlRewriter(),
    )
    with patch("leap.core.common.time.utc_now", return_value=t0):
        async with svc.ctx.session() as session:
            await svc.initialize(session)
        _ = await svc.play("emp-final")
    att0 = svc.wiki_puzzle_attempt_dao._attempts[0]  # noqa: SLF001
    svc.wiki_puzzle_attempt_dao._attempts[0] = att0.model_copy(  # noqa: SLF001
        update={"started_at": t0 - timedelta(minutes=5)}
    )

    with patch("leap.core.common.time.utc_now", return_value=t0):
        out = await svc.timeout("emp-final")

    assert isinstance(out, WikiPlayTerminalDTO)
    assert out.state == "completed"
    assert len(out.results) == 1
    assert out.results[0].status == WikiPuzzleAttemptStatus.TIMED_OUT
    assert out.results[0].score == 0

    wiki_session = await gdao.get_by_player_and_game(None, "emp-final", "wiki")
    assert wiki_session is not None
    assert wiki_session.status.value == "completed"


@pytest.mark.asyncio
async def test_back_disabled_raises() -> None:
    t0 = datetime(2026, 5, 17, 12, 0, 0, tzinfo=timezone.utc)
    wiki = FakeWikipediaClient({"Beta": "<section><p>z</p></section>"})
    svc = _build_svc(wikipedia=wiki, back_button_enabled=False)
    with patch("leap.core.common.time.utc_now", return_value=t0):
        async with svc.ctx.session() as session:
            await svc.initialize(session)
        await svc.play("p1")
        await svc.navigate("p1", "Beta")
    with pytest.raises(WikiBackButtonDisabledException):
        await svc.back("p1")


@pytest.mark.asyncio
async def test_back_rejects_when_no_previous_page() -> None:
    t0 = datetime(2026, 5, 17, 12, 0, 0, tzinfo=timezone.utc)
    svc = _build_svc(back_button_enabled=True)
    with patch("leap.core.common.time.utc_now", return_value=t0):
        async with svc.ctx.session() as session:
            await svc.initialize(session)
        await svc.play("p1")
        with pytest.raises(WikiNoPreviousPageException):
            await svc.back("p1")


@pytest.mark.asyncio
async def test_back_counts_one_step_and_returns_previous_html() -> None:
    t0 = datetime(2026, 5, 17, 12, 0, 0, tzinfo=timezone.utc)
    wiki = FakeWikipediaClient(
        {
            "Alpha": "<section><p>on alpha</p></section>",
            "Beta": "<section><p>on beta</p></section>",
        },
    )
    svc = _build_svc(wikipedia=wiki, back_button_enabled=True)
    with patch("leap.core.common.time.utc_now", return_value=t0):
        async with svc.ctx.session() as session:
            await svc.initialize(session)
        await svc.play("p1")
        nav_fwd = await svc.navigate("p1", "Beta")
        assert isinstance(nav_fwd, WikiNavigateActiveDTO)
        assert nav_fwd.current.steps_taken == 1
        back_out = await svc.back("p1")
    assert isinstance(back_out, WikiNavigateActiveDTO)
    assert back_out.current.steps_taken == 2
    assert back_out.current.click_path == ["Beta", "Alpha"]
    assert "on alpha" in back_out.current.article_html


@pytest.mark.asyncio
async def test_abandon_preserves_completed_scores_and_zeroes_rest() -> None:
    t0 = datetime(2026, 5, 17, 12, 0, 0, tzinfo=timezone.utc)
    wiki = _wiki_html_client_for_targets(3)
    gdao = FakeGameSessionDAO()
    svc = WikiSpeedRunService(
        FakeContextManager(),
        gdao,
        FakeWikiRoundDAO([_wiki_round(1), _wiki_round(2), _wiki_round(3)]),
        FakeWikiPuzzleAttemptDAO(),
        wiki,
        FakeWikiHtmlRewriter(),
    )
    with patch("leap.core.common.time.utc_now", return_value=t0):
        async with svc.ctx.session() as session:
            await svc.initialize(session)
        await svc.play("ab1")
        await svc.navigate("ab1", "T1")
        _ = await svc.play("ab1")

    terminal = await svc.abandon("ab1")
    assert terminal.state == "abandoned"
    assert len(terminal.results) == 3
    assert terminal.results[0].status == WikiPuzzleAttemptStatus.COMPLETED
    assert terminal.results[0].score > 0
    assert terminal.results[1].status == WikiPuzzleAttemptStatus.ABANDONED
    assert terminal.results[1].score == 0
    assert terminal.results[2].status == WikiPuzzleAttemptStatus.ABANDONED
    wiki_session = await gdao.get_by_player_and_game(None, "ab1", "wiki")
    assert wiki_session is not None
    assert wiki_session.status == GameSessionStatus.ABANDONED
    assert terminal.total_score == wiki_session.score


@pytest.mark.asyncio
async def test_play_after_abandon_returns_abandon_terminal_with_results() -> None:
    t0 = datetime(2026, 5, 17, 12, 0, 0, tzinfo=timezone.utc)
    wiki = FakeWikipediaClient({"T1": "<section><p>x</p></section>"})
    gdao = FakeGameSessionDAO()
    svc = WikiSpeedRunService(
        FakeContextManager(),
        gdao,
        FakeWikiRoundDAO([_wiki_round(1), _wiki_round(2)]),
        FakeWikiPuzzleAttemptDAO(),
        wiki,
        FakeWikiHtmlRewriter(),
    )
    with patch("leap.core.common.time.utc_now", return_value=t0):
        async with svc.ctx.session() as session:
            await svc.initialize(session)
        await svc.play("x1")
        await svc.navigate("x1", "T1")
    await svc.abandon("x1")
    again = await svc.play("x1")
    assert again.state == "abandoned"
    assert len(again.results) == 2
    assert again.results[0].status == WikiPuzzleAttemptStatus.COMPLETED
