"""Picture Illustration game routes."""

from fastapi import APIRouter, Depends

from leap.api.deps import get_container, get_current_player
from leap.api.schema.picture import (
    AbandonResponse,
    AnswerRequest,
    AnswerResponse,
    PlayResponse,
    PuzzleSchema,
    ResultPuzzleSchema,
    ResultSchema,
)
from leap.games.picture.service import PictureService
from leap.service.container import ServiceContainer
from leap.types.picture import (
    PictureAnswerPayload,
    PictureDisplayedPuzzleDTO,
    PicturePlayPayload,
    PictureResultDTO,
)
from leap.types.player import CurrentPlayer

router = APIRouter()


def _puzzle_schema(puzzle: PictureDisplayedPuzzleDTO) -> PuzzleSchema:
    return PuzzleSchema(
        id=puzzle.id,
        image_filename=puzzle.image_filename,
        puzzles_answered=puzzle.puzzles_answered,
        puzzles_total=puzzle.puzzles_total,
    )


def _result_schema(result: PictureResultDTO) -> ResultSchema:
    return ResultSchema(
        score=result.score,
        accuracy_score=result.accuracy_score,
        time_bonus=result.time_bonus,
        time_remaining_seconds=result.time_remaining_seconds,
        puzzles=[
            ResultPuzzleSchema(
                puzzle_id=p.puzzle_id,
                image_filename=p.image_filename,
                status=p.status,
                score_earned=p.score_earned,
            )
            for p in result.puzzles
        ],
    )


def _play_response(payload: PicturePlayPayload) -> PlayResponse:
    return PlayResponse(
        status=payload.status,
        game_session_id=payload.game_session_id,
        puzzles_answered=payload.puzzles_answered,
        puzzles_total=payload.puzzles_total,
        session_started_at=payload.session_started_at,
        time_limit_ms=payload.time_limit_ms,
        puzzle=_puzzle_schema(payload.puzzle) if payload.puzzle is not None else None,
        result=_result_schema(payload.result) if payload.result is not None else None,
    )


def _answer_response(payload: PictureAnswerPayload) -> AnswerResponse:
    return AnswerResponse(
        correct=payload.correct,
        score_earned=payload.score_earned,
        current_score=payload.current_score,
        puzzles_solved=payload.puzzles_solved,
        puzzles_remaining=payload.puzzles_remaining,
        next_puzzle=_puzzle_schema(payload.next_puzzle)
        if payload.next_puzzle is not None
        else None,
        result=_result_schema(payload.result) if payload.result is not None else None,
    )


def _picture_svc(container: ServiceContainer) -> PictureService:
    return container.picture


@router.post("/play", response_model=PlayResponse, summary="Start or resume Picture Illustration")
async def play(
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> PlayResponse:
    payload = await _picture_svc(container).play(player.id)
    return _play_response(payload)


@router.post("/answer", response_model=AnswerResponse, summary="Submit a picture puzzle answer")
async def answer(
    body: AnswerRequest,
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> AnswerResponse:
    out = await _picture_svc(container).submit_answer(
        player.id, body.puzzle_id, body.submitted_answer
    )
    return _answer_response(out)


@router.post(
    "/abandon",
    response_model=AbandonResponse,
    summary="End Picture Illustration session (timer or nav)",
)
async def abandon(
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> AbandonResponse:
    result = await _picture_svc(container).abandon(player.id)
    return AbandonResponse(result=_result_schema(result))
