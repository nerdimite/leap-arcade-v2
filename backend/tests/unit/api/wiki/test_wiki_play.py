"""Tests for POST /games/wiki/play."""

from leap.types.player import CurrentPlayer
from tests.unit.api.wiki.conftest import sample_wiki_rounds


class TestWikiPlay:
    def test_play_twice_returns_same_attempt_id(self, wiki_client, auth_player: CurrentPlayer) -> None:
        r1 = wiki_client.post("/games/wiki/play")
        assert r1.status_code == 200
        body1 = r1.json()
        assert body1["state"] == "active"
        assert body1["current"]["clue"] == "API clue line"
        assert body1["current"]["attempt_id"]
        assert "TestStart" in body1["current"]["article_html"]

        r2 = wiki_client.post("/games/wiki/play")
        assert r2.status_code == 200
        body2 = r2.json()
        assert body2["current"]["attempt_id"] == body1["current"]["attempt_id"]
        assert body2["current"]["puzzle_index"] == 1
        assert body2["current"]["puzzle_count"] == len(sample_wiki_rounds())

        container = wiki_client.app.state.container
        sessions = [s for s in container.game_session_dao._sessions if s.game_id == "wiki"]  # noqa: SLF001
        assert len(sessions) == 1
        assert sessions[0].player_id == auth_player.id
