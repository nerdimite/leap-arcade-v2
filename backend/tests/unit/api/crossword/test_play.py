"""Crossword route tests."""

from http import HTTPStatus
from fastapi.testclient import TestClient


def test_play_route(crossword_client: TestClient) -> None:
    # 1. POST /games/crossword/play
    resp = crossword_client.post("/games/crossword/play")
    assert resp.status_code == HTTPStatus.OK

    data = resp.json()
    assert data["session_status"] == "active"
    assert data["session_score"] == 0
    assert data["puzzle"] is not None
    assert data["result"] is None

    puz = data["puzzle"]
    assert puz["puzzle_id"] == "22222222-2222-2222-2222-222222222222"
    assert puz["rows"] == 12
    assert puz["cols"] == 12
    assert len(puz["cells"]) == 12
    assert len(puz["clues"]) == 10


def test_check_route_correct_and_incorrect(crossword_client: TestClient) -> None:
    # Start play
    crossword_client.post("/games/crossword/play")

    # 1. Correct answer check
    resp = crossword_client.post(
        "/games/crossword/check",
        json={"entry_id": "e2", "letters": "mock"}
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["correct"] is True
    assert data["entry"] is not None
    assert data["entry"]["answer"] == "MOCK"
    assert data["session_score"] == 100

    # 2. Incorrect answer check
    resp = crossword_client.post(
        "/games/crossword/check",
        json={"entry_id": "e2", "letters": "wrong"}
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["correct"] is False
    assert data["entry"] is None


def test_submit_route(crossword_client: TestClient) -> None:
    # Start play
    crossword_client.post("/games/crossword/play")

    # Solve one word
    crossword_client.post(
        "/games/crossword/check",
        json={"entry_id": "e2", "letters": "mock"}
    )

    # 3. POST /games/crossword/submit
    resp = crossword_client.post("/games/crossword/submit")
    assert resp.status_code == HTTPStatus.OK

    data = resp.json()
    assert "result" in data
    res = data["result"]
    assert res["score"] >= 100
    assert res["solved_count"] == 1
    assert len(res["solved_entries"]) == 1
    assert res["solved_entries"][0]["entry_id"] == "e2"
