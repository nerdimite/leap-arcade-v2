"""Crossword game routes."""

from fastapi import APIRouter, Depends

from leap.api.deps import get_container, get_current_player
from leap.api.schema.crossword import (
    CellCoordinateSchema,
    CellSkeletonSchema,
    CheckRequest,
    CheckResponse,
    ClueSchema,
    PlayResponse,
    PuzzleStateSchema,
    ResultSchema,
    SolvedEntrySchema,
    SubmitResponse,
)
from leap.games.crossword.service import CrosswordService
from leap.service.container import ServiceContainer
from leap.types.crossword import (
    CellSkeleton,
    ClueSkeleton,
    CrosswordCheckPayload,
    CrosswordPlayPayload,
    CrosswordPuzzleStateDTO,
    CrosswordResultDTO,
    CrosswordSolvedEntryDTO,
)
from leap.types.player import CurrentPlayer

router = APIRouter()


def _cell_coordinate_schema(cell: dict[str, int]) -> CellCoordinateSchema:
    return CellCoordinateSchema(row=cell["row"], col=cell["col"])


def _cell_skeleton_schema(cell: CellSkeleton) -> CellSkeletonSchema:
    return CellSkeletonSchema(
        row=cell.row,
        col=cell.col,
        number=cell.number,
        letter=cell.letter,
    )


def _clue_schema(clue: ClueSkeleton) -> ClueSchema:
    return ClueSchema(
        entry_id=clue.entry_id,
        number=clue.number,
        direction=clue.direction,
        clue=clue.clue,
        length=clue.length,
        start_row=clue.start_row,
        start_col=clue.start_col,
        solved=clue.solved,
        answer=clue.answer,
        cells=[_cell_coordinate_schema(c) for c in clue.cells] if clue.cells else None,
    )


def _solved_entry_schema(entry: CrosswordSolvedEntryDTO) -> SolvedEntrySchema:
    return SolvedEntrySchema(
        entry_id=entry.entry_id,
        number=entry.number,
        direction=entry.direction,
        clue=entry.clue,
        answer=entry.answer,
        cells=[_cell_coordinate_schema(c) for c in entry.cells],
    )


def _puzzle_schema(puzzle: CrosswordPuzzleStateDTO) -> PuzzleStateSchema:
    return PuzzleStateSchema(
        puzzle_id=puzzle.puzzle_id,
        rows=puzzle.rows,
        cols=puzzle.cols,
        cells=[
            [_cell_skeleton_schema(c) if c is not None else None for c in row]
            for row in puzzle.cells
        ],
        clues=[_clue_schema(c) for c in puzzle.clues],
        solved_count=puzzle.solved_count,
        total_entries=puzzle.total_entries,
        started_at=puzzle.started_at,
    )


def _result_schema(result: CrosswordResultDTO) -> ResultSchema:
    return ResultSchema(
        score=result.score,
        base_score=result.base_score,
        time_bonus=result.time_bonus,
        time_elapsed_ms=result.time_elapsed_ms,
        solved_count=result.solved_count,
        total_entries=result.total_entries,
        solved_entries=[_solved_entry_schema(e) for e in result.solved_entries],
    )


def _play_response(payload: CrosswordPlayPayload) -> PlayResponse:
    return PlayResponse(
        session_status=payload.session_status,
        session_score=payload.session_score,
        puzzle=_puzzle_schema(payload.puzzle) if payload.puzzle is not None else None,
        result=_result_schema(payload.result) if payload.result is not None else None,
    )


def _check_response(payload: CrosswordCheckPayload) -> CheckResponse:
    return CheckResponse(
        correct=payload.correct,
        entry=_solved_entry_schema(payload.entry) if payload.entry is not None else None,
        session_status=payload.session_status,
        session_score=payload.session_score,
        result=_result_schema(payload.result) if payload.result is not None else None,
    )


def _crossword_svc(container: ServiceContainer) -> CrosswordService:
    return container.crossword


@router.post("/play", response_model=PlayResponse, summary="Start or resume Crossword")
async def play(
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> PlayResponse:
    payload = await _crossword_svc(container).play(player.id)
    return _play_response(payload)


@router.post("/check", response_model=CheckResponse, summary="Check a filled entry")
async def check_entry(
    body: CheckRequest,
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> CheckResponse:
    payload = await _crossword_svc(container).submit_check(
        player.id,
        body,
    )
    return _check_response(payload)


@router.post("/submit", response_model=SubmitResponse, summary="Submit Crossword session")
async def submit(
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> SubmitResponse:
    result = await _crossword_svc(container).submit(player.id)
    return SubmitResponse(result=_result_schema(result))
