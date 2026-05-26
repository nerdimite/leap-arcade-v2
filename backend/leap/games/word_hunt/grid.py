"""Word Hunt grid utilities — pure functions, no I/O."""

from typing import List, Tuple


def _sign(value: int) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def direction_of(
    start_row: int,
    start_col: int,
    end_row: int,
    end_col: int,
) -> Tuple[int, int]:
    """Return normalised (dr, dc) from start to end."""
    return (_sign(end_row - start_row), _sign(end_col - start_col))


def validate_trace(
    rows: int,
    cols: int,
    start_row: int,
    start_col: int,
    end_row: int,
    end_col: int,
) -> bool:
    """Return True when the trace is in-bounds and along one of eight straight lines."""
    if not (0 <= start_row < rows and 0 <= start_col < cols):
        return False
    if not (0 <= end_row < rows and 0 <= end_col < cols):
        return False

    dr = end_row - start_row
    dc = end_col - start_col
    if dr == 0 and dc == 0:
        return False

    is_horizontal = dr == 0 and dc != 0
    is_vertical = dc == 0 and dr != 0
    is_diagonal = dr != 0 and dc != 0 and abs(dr) == abs(dc)
    return is_horizontal or is_vertical or is_diagonal


def walk_cells(
    grid: List[List[str]],
    start_row: int,
    start_col: int,
    end_row: int,
    end_col: int,
) -> str:
    """Walk from start to end inclusive and return the traced uppercase string."""
    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    if not validate_trace(rows, cols, start_row, start_col, end_row, end_col):
        raise ValueError("invalid trace")

    dr, dc = direction_of(start_row, start_col, end_row, end_col)
    letters: List[str] = []
    row, col = start_row, start_col
    while True:
        letters.append(grid[row][col].upper())
        if row == end_row and col == end_col:
            break
        row += dr
        col += dc

    return "".join(letters)


def validate_seeded_word(
    grid: List[List[str]],
    word: str,
    start_row: int,
    start_col: int,
    end_row: int,
    end_col: int,
) -> bool:
    """Return True when seeded coordinates spell the declared word."""
    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    if not validate_trace(rows, cols, start_row, start_col, end_row, end_col):
        return False
    traced = walk_cells(grid, start_row, start_col, end_row, end_col)
    return traced.upper() == word.upper()
