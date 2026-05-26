"""Pinpoint game routes."""

from fastapi import APIRouter, Depends

from leap.api.deps import get_container, get_current_player
from leap.api.schema.pinpoint import (
    AbandonResponse,
    GuessRequest,
    GuessResponse,
    PlayResponse,
    PuzzleStateSchema,
    ResultPuzzleSchema,
    ResultSchema,
)
from leap.games.pinpoint.service import PinpointService
from leap.service.container import ServiceContainer
from leap.types.pinpoint import (
    PinpointGuessPayload,
    PinpointPlayPayload,
    PinpointPuzzleStateDTO,
    PinpointResultDTO,
)
from leap.types.player import CurrentPlayer


router = APIRouter()


def _puzzle_schema(puzzle: PinpointPuzzleStateDTO) -> PuzzleStateSchema:
    return PuzzleStateSchema(
        puzzle_id=puzzle.puzzle_id,
        puzzle_number=puzzle.puzzle_number,
        total_puzzles=puzzle.total_puzzles,
        clues_revealed=puzzle.clues_revealed,
        clues=list(puzzle.clues),
        status=puzzle.status,
        score=puzzle.score,
        time_bonus=puzzle.time_bonus,
        started_at=puzzle.started_at,
    )


def _result_schema(result: PinpointResultDTO) -> ResultSchema:
    return ResultSchema(
        score=result.score,
        puzzles_solved=result.puzzles_solved,
        puzzles_failed=result.puzzles_failed,
        puzzles_not_reached=result.puzzles_not_reached,
        puzzles=[
            ResultPuzzleSchema(
                puzzle_id=p.puzzle_id,
                status=p.status,
                clues_used=p.clues_used,
                score=p.score,
                time_bonus=p.time_bonus,
            )
            for p in result.puzzles
        ],
    )


def _play_response(payload: PinpointPlayPayload) -> PlayResponse:
    return PlayResponse(
        session_status=payload.session_status,
        session_score=payload.session_score,
        puzzle=_puzzle_schema(payload.puzzle) if payload.puzzle is not None else None,
        result=_result_schema(payload.result) if payload.result is not None else None,
    )


def _guess_response(payload: PinpointGuessPayload) -> GuessResponse:
    return GuessResponse(
        correct=payload.correct,
        puzzle=_puzzle_schema(payload.puzzle),
        session_status=payload.session_status,
        session_score=payload.session_score,
        result=_result_schema(payload.result) if payload.result is not None else None,
    )


def _pinpoint_svc(container: ServiceContainer) -> PinpointService:
    return container.pinpoint


@router.post("/play", response_model=PlayResponse, summary="Start or resume Pinpoint")
async def play(
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> PlayResponse:
    payload = await _pinpoint_svc(container).play(player.id)
    return _play_response(payload)


@router.post("/guess", response_model=GuessResponse, summary="Submit a Pinpoint guess")
async def guess(
    body: GuessRequest,
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> GuessResponse:
    payload = await _pinpoint_svc(container).submit_guess(player.id, body.puzzle_id, body.guess)
    return _guess_response(payload)


@router.post("/abandon", response_model=AbandonResponse, summary="Abandon Pinpoint session")
async def abandon(
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> AbandonResponse:
    """Forfeit with a partial result."""
    result = await _pinpoint_svc(container).abandon(player.id)
    return AbandonResponse(result=_result_schema(result))
