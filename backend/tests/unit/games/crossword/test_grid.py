import pytest
from leap.games.crossword.grid import (
    entry_cells,
    walk_entry,
    validate_seeded_entry,
    validate_grid_consistency,
    build_skeleton,
)

GRID = [
    ["M", "I", "C", "R", "O", "S", "E", "R", "V", "I", "C", "E"],
    ["O", None, None, None, None, None, None, None, None, None, None, "V"],
    ["C", None, None, None, None, "D", None, None, None, None, None, "E"],
    ["K", "U", "B", "E", "R", "N", "E", "T", "E", "S", None, "N"],
    [None, None, None, None, None, "S", None, None, None, None, None, "T"],
    ["C", None, None, None, "G", None, None, None, None, None, None, "D"],
    ["A", "T", "O", "M", "I", "C", "I", "T", "Y", None, None, "R"],
    ["C", None, None, None, "T", None, None, None, None, "D", None, "I"],
    ["H", None, None, None, "O", None, None, None, None, "R", None, "V"],
    ["I", None, None, None, "P", "I", "P", "E", "L", "I", "N", "E"],
    ["N", None, None, None, "S", None, None, None, None, "F", None, "N"],
    ["G", None, None, None, None, None, None, None, None, "T", None, None],
]

ENTRIES = [
    {
        "number": 1,
        "direction": "across",
        "start_row": 0,
        "start_col": 0,
        "answer": "MICROSERVICE",
        "clue": "Small, independently deployable unit in modern cloud architecture (12)"
    },
    {
        "number": 1,
        "direction": "down",
        "start_row": 0,
        "start_col": 0,
        "answer": "MOCK",
        "clue": "Simulated object used in testing to replace a real dependency (4)"
    },
    {
        "number": 2,
        "direction": "down",
        "start_row": 0,
        "start_col": 11,
        "answer": "EVENTDRIVEN",
        "clue": "Communication style where services interact through events (11)"
    },
    {
        "number": 3,
        "direction": "down",
        "start_row": 2,
        "start_col": 5,
        "answer": "DNS",
        "clue": "Protocol that assigns a readable name (3)"
    },
    {
        "number": 4,
        "direction": "across",
        "start_row": 3,
        "start_col": 0,
        "answer": "KUBERNETES",
        "clue": "Container orchestration platform (10)"
    },
    {
        "number": 5,
        "direction": "down",
        "start_row": 5,
        "start_col": 4,
        "answer": "GITOPS",
        "clue": "Philosophy of treating infrastructure (6)"
    },
    {
        "number": 6,
        "direction": "down",
        "start_row": 5,
        "start_col": 0,
        "answer": "CACHING",
        "clue": "Technique of storing frequently accessed data (7)"
    },
    {
        "number": 7,
        "direction": "across",
        "start_row": 6,
        "start_col": 0,
        "answer": "ATOMICITY",
        "clue": "ACID property (10)"
    },
    {
        "number": 8,
        "direction": "down",
        "start_row": 7,
        "start_col": 9,
        "answer": "DRIFT",
        "clue": "When a deployed model's accuracy degrades (5)"
    },
    {
        "number": 9,
        "direction": "across",
        "start_row": 9,
        "start_col": 4,
        "answer": "PIPELINE",
        "clue": "Automated workflow from code commit to deployment (8)"
    }
]


def test_entry_cells() -> None:
    # Across
    assert entry_cells(0, 0, "across", 3) == [(0, 0), (0, 1), (0, 2)]
    # Down
    assert entry_cells(2, 5, "down", 3) == [(2, 5), (3, 5), (4, 5)]


def test_walk_entry() -> None:
    assert walk_entry(GRID, 0, 0, "across", 12) == "MICROSERVICE"
    assert walk_entry(GRID, 0, 0, "down", 4) == "MOCK"
    assert walk_entry(GRID, 2, 5, "down", 3) == "DNS"

    with pytest.raises(ValueError, match="Blocked cell in entry"):
        walk_entry(GRID, 0, 1, "down", 3)

    with pytest.raises(ValueError, match="Out of bounds"):
        walk_entry(GRID, 0, 11, "across", 5)


def test_validate_seeded_entry() -> None:
    assert validate_seeded_entry(GRID, "MICROSERVICE", 0, 0, "across") is True
    assert validate_seeded_entry(GRID, "microservice", 0, 0, "across") is True
    assert validate_seeded_entry(GRID, "MOCK", 0, 0, "down") is True
    assert validate_seeded_entry(GRID, "WRONG", 0, 0, "down") is False
    assert validate_seeded_entry(GRID, "MICROSERVICE", 0, 0, "down") is False


def test_validate_grid_consistency() -> None:
    # Happy path
    validate_grid_consistency(GRID, ENTRIES)

    # Inconsistent spelling
    bad_entries = [dict(e) for e in ENTRIES]
    bad_entries[0] = dict(bad_entries[0], answer="MICROSERVICX")
    with pytest.raises(ValueError, match="does not match the grid"):
        validate_grid_consistency(GRID, bad_entries)

    # Grid cell not covered
    bad_grid = [row[:] for row in GRID]
    bad_grid[1][1] = "X"
    with pytest.raises(ValueError, match="is non-null but not covered by any entry"):
        validate_grid_consistency(bad_grid, ENTRIES)


def test_build_skeleton() -> None:
    cells, clues = build_skeleton(GRID, ENTRIES)

    assert len(cells) == 12
    assert len(cells[0]) == 12
    assert len(clues) == 10

    # Blocked cell should be None
    assert cells[1][1] is None

    # Start cells should have correct numbers
    assert cells[0][0]["number"] == 1
    assert cells[0][0]["letter"] is None
    assert cells[0][1]["number"] is None

    # Clues list
    clue_mock = next(c for c in clues if c["number"] == 1 and c["direction"] == "down")
    assert clue_mock["clue"] == "Simulated object used in testing to replace a real dependency (4)"
    assert clue_mock["length"] == 4
    assert clue_mock["solved"] is False
    assert clue_mock["answer"] is None
