"""Crossword grid utilities — pure functions, no I/O."""

from typing import Any, Dict, List, Optional, Tuple


def entry_cells(
    start_row: int, start_col: int, direction: str, length: int
) -> List[Tuple[int, int]]:
    """Return the list of (row, col) coordinates for an entry starting at (start_row, start_col) in direction."""
    cells = []
    if direction == "across":
        for i in range(length):
            cells.append((start_row, start_col + i))
    elif direction == "down":
        for i in range(length):
            cells.append((start_row + i, start_col))
    else:
        raise ValueError(f"Invalid direction: {direction}")
    return cells


def walk_entry(
    grid: List[List[Optional[str]]], start_row: int, start_col: int, direction: str, length: int
) -> str:
    """Walk from start inclusive and return the traced uppercase string."""
    coords = entry_cells(start_row, start_col, direction, length)
    letters = []
    rows = len(grid)
    cols = len(grid[0]) if grid else 0

    for r, c in coords:
        if not (0 <= r < rows and 0 <= c < cols):
            raise ValueError("Out of bounds")
        val = grid[r][c]
        if val is None:
            raise ValueError("Blocked cell in entry")
        letters.append(val.upper())

    return "".join(letters)


def validate_seeded_entry(
    grid: List[List[Optional[str]]], answer: str, start_row: int, start_col: int, direction: str
) -> bool:
    """Return True when the seeded coordinates spell the declared answer (case-insensitive)."""
    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    length = len(answer)

    # Check bounds of start
    if not (0 <= start_row < rows and 0 <= start_col < cols):
        return False

    # Check bounds of end
    if direction == "across":
        if start_col + length > cols:
            return False
    elif direction == "down":
        if start_row + length > rows:
            return False
    else:
        return False

    try:
        traced = walk_entry(grid, start_row, start_col, direction, length)
        return traced.upper() == answer.upper()
    except ValueError:
        return False


def validate_grid_consistency(
    grid: List[List[Optional[str]]], entries: List[Dict[str, Any]]
) -> None:
    """Validate that:
    1. Every entry spells its answer on the grid.
    2. Every entry's cells are non-null in the grid.
    3. Every non-null grid cell is covered by at least one entry.
    4. Intersection cells have consistent letters.
    Raises ValueError on failure.
    """
    rows = len(grid)
    cols = len(grid[0]) if grid else 0

    covered_cells = set()

    for entry in entries:
        ans = entry["answer"]
        r = entry["start_row"]
        c = entry["start_col"]
        d = entry["direction"]
        length = len(ans)

        # 1 & 2: Check spelling & non-nullness
        if not validate_seeded_entry(grid, ans, r, c, d):
            raise ValueError(
                f"Entry {ans!r} in direction {d} at ({r},{c}) does not match the grid or hits a blocked cell."
            )

        # Add to covered cells
        for cell in entry_cells(r, c, d, length):
            covered_cells.add(cell)

    # 3: Every non-null grid cell is covered by at least one entry
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] is not None:
                if (r, c) not in covered_cells:
                    raise ValueError(
                        f"Grid cell ({r}, {c}) is non-null but not covered by any entry."
                    )
            else:
                if (r, c) in covered_cells:
                    raise ValueError(f"Grid cell ({r}, {c}) is null but covered by an entry.")


def build_skeleton(
    grid: List[List[Optional[str]]], entries: List[Dict[str, Any]]
) -> Tuple[List[List[Optional[Dict[str, Any]]]], List[Dict[str, Any]]]:
    """Build the open/blocked layout of cells with corner numbering (no letters) and list of clues."""
    rows = len(grid)
    cols = len(grid[0]) if grid else 0

    # Determine cell numbering by looking at which entries start at which coordinates
    number_map = {}
    for entry in entries:
        r = entry["start_row"]
        c = entry["start_col"]
        num = entry["number"]
        number_map[(r, c)] = num

    # Build cells skeleton
    cells = []
    for r in range(rows):
        row_cells = []
        for c in range(cols):
            if grid[r][c] is None:
                row_cells.append(None)
            else:
                num = number_map.get((r, c))
                row_cells.append({"row": r, "col": c, "number": num, "letter": None})
        cells.append(row_cells)

    # Build clues skeleton
    clues = []
    for entry in entries:
        clues.append(
            {
                "entry_id": entry.get("id"),
                "number": entry["number"],
                "direction": entry["direction"],
                "clue": entry["clue"],
                "length": len(entry["answer"]),
                "start_row": entry["start_row"],
                "start_col": entry["start_col"],
                "solved": False,
                "answer": None,
                "cells": None,
            }
        )

    return cells, clues
