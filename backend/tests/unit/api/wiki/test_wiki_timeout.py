"""Tests for POST /games/wiki/timeout."""

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from leap.types.wiki import WikiPuzzleAttemptStatus, WikiRoundDTO
from tests.unit.api.wiki.conftest import sample_wiki_rounds


class TestWikiTimeout:
    def test_timeout_early_returns_active_with_server_remaining(self, wiki_client) -> None:
        t0 = datetime(2026, 5, 17, 12, 0, 0, tzinfo=timezone.utc)
        with patch("leap.core.common.time.utc_now", return_value=t0):
            r1 = wiki_client.post("/games/wiki/play")
        assert r1.status_code == 200
        b1 = r1.json()
        assert b1["state"] == "active"
        aid = b1["current"]["attempt_id"]
        t1 = t0 + timedelta(seconds=15)
        with patch("leap.core.common.time.utc_now", return_value=t1):
            r2 = wiki_client.post("/games/wiki/timeout")
        assert r2.status_code == 200
        b2 = r2.json()
        assert b2["state"] == "active"
        assert b2["current"]["attempt_id"] == aid
        assert b2["current"]["time_remaining_ms"] == 90_000 - 15_000

    def test_timeout_when_server_says_expired_advances_puzzle(self, wiki_client) -> None:
        container = wiki_client.app.state.container
        t0 = datetime(2026, 5, 17, 12, 0, 0, tzinfo=timezone.utc)
        with patch("leap.core.common.time.utc_now", return_value=t0):
            r1 = wiki_client.post("/games/wiki/play")
        assert r1.status_code == 200

        rounds = sample_wiki_rounds()
        second = WikiRoundDTO(
            id="wiki-r2",
            sequence_index=2,
            start_title="S2",
            start_url="u",
            target_title="T2",
            target_url="u",
            clue="second",
            optimal_click_count=1,
            solution_path=[],
            time_limit_ms=60_000,
        )
        rdao = container.wiki_round_dao
        rdao._rounds = sorted((*rounds, second), key=lambda r: r.sequence_index)  # noqa: SLF001
        container.wikipedia_client.html_by_title["S2"] = "<section><p>s2</p></section>"  # noqa: SLF001

        async def reinit() -> None:
            async with container.context_manager.session() as session:
                await container.wiki_speed_run.initialize(session)

        asyncio.run(reinit())

        att = container.wiki_puzzle_attempt_dao._attempts[0]  # noqa: SLF001
        stale = att.model_copy(update={"started_at": t0 - timedelta(minutes=10)})
        container.wiki_puzzle_attempt_dao._attempts[0] = stale  # noqa: SLF001

        with patch("leap.core.common.time.utc_now", return_value=t0):
            r2 = wiki_client.post("/games/wiki/timeout")

        assert r2.status_code == 200
        b2 = r2.json()
        assert b2["state"] == "active"
        assert b2["current"]["puzzle_index"] == 2

        updated_first = container.wiki_puzzle_attempt_dao._attempts[0]  # noqa: SLF001
        assert updated_first.status == WikiPuzzleAttemptStatus.TIMED_OUT
