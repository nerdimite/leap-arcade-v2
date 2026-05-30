"""Word Hunt game routes."""

from fastapi import APIRouter, Depends

from leap.api.deps import get_container, get_current_player
from leap.api.schema.word_hunt import (
    ClueSchema,
    CoordinatesSchema,
    FindRequest,
    FindResponse,
    FoundWordSchema,
    PlayResponse,
    PuzzleStateSchema,
    ResultSchema,
    SubmitResponse,
)
from leap.games.word_hunt.service import WordHuntService
from leap.service.container import ServiceContainer
from leap.types.player import CurrentPlayer
from leap.types.word_hunt import (
    WordHuntClueDTO,
    WordHuntCoordinatesDTO,
    WordHuntFindPayload,
    WordHuntFoundWordDTO,
    WordHuntPlayPayload,
    WordHuntPuzzleStateDTO,
    WordHuntResultDTO,
)

router = APIRouter()


def _coordinates_schema(coords: WordHuntCoordinatesDTO) -> CoordinatesSchema:
    return CoordinatesSchema(
        start_row=coords.start_row,
        start_col=coords.start_col,
        end_row=coords.end_row,
        end_col=coords.end_col,
    )


def _clue_schema(clue: WordHuntClueDTO) -> ClueSchema:
    return ClueSchema(
        word_id=clue.word_id,
        clue=clue.clue,
        found=clue.found,
        word=clue.word,
        coordinates=_coordinates_schema(clue.coordinates) if clue.coordinates else None,
    )


def _found_word_schema(word: WordHuntFoundWordDTO) -> FoundWordSchema:
    return FoundWordSchema(
        word_id=word.word_id,
        word=word.word,
        clue=word.clue,
        coordinates=_coordinates_schema(word.coordinates),
    )


def _puzzle_schema(puzzle: WordHuntPuzzleStateDTO) -> PuzzleStateSchema:
    return PuzzleStateSchema(
        puzzle_id=puzzle.puzzle_id,
        rows=puzzle.rows,
        cols=puzzle.cols,
        grid=puzzle.grid,
        clues=[_clue_schema(c) for c in puzzle.clues],
        found_count=puzzle.found_count,
        total_words=puzzle.total_words,
        started_at=puzzle.started_at,
    )


def _result_schema(result: WordHuntResultDTO) -> ResultSchema:
    return ResultSchema(
        score=result.score,
        base_score=result.base_score,
        time_bonus=result.time_bonus,
        time_elapsed_ms=result.time_elapsed_ms,
        found_count=result.found_count,
        total_words=result.total_words,
        found_words=[_found_word_schema(w) for w in result.found_words],
    )


def _play_response(payload: WordHuntPlayPayload) -> PlayResponse:
    return PlayResponse(
        session_status=payload.session_status,
        session_score=payload.session_score,
        puzzle=_puzzle_schema(payload.puzzle) if payload.puzzle is not None else None,
        result=_result_schema(payload.result) if payload.result is not None else None,
    )


def _find_response(payload: WordHuntFindPayload) -> FindResponse:
    return FindResponse(
        matched=payload.matched,
        word=_found_word_schema(payload.word) if payload.word is not None else None,
        session_status=payload.session_status,
        session_score=payload.session_score,
        result=_result_schema(payload.result) if payload.result is not None else None,
    )


def _word_hunt_svc(container: ServiceContainer) -> WordHuntService:
    return container.word_hunt


@router.post("/play", response_model=PlayResponse, summary="Start or resume Word Hunt")
async def play(
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> PlayResponse:
    payload = await _word_hunt_svc(container).play(player.id)
    return _play_response(payload)


@router.post("/find", response_model=FindResponse, summary="Submit a word trace")
async def find_word(
    body: FindRequest,
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> FindResponse:
    payload = await _word_hunt_svc(container).submit_find(
        player.id,
        body.start_row,
        body.start_col,
        body.end_row,
        body.end_col,
    )
    return _find_response(payload)


@router.post("/submit", response_model=SubmitResponse, summary="Submit Word Hunt session")
async def submit(
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> SubmitResponse:
    result = await _word_hunt_svc(container).submit(player.id)
    return SubmitResponse(result=_result_schema(result))
