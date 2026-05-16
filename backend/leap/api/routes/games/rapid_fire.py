"""Rapid Fire Quiz game routes."""

from fastapi import APIRouter, Depends

from leap.api.deps import get_container, get_current_player
from leap.api.schema.rapid_fire import (
    AbandonResponse,
    AnswerRequest,
    AnswerResponse,
    PlayResponse,
    QuestionSchema,
    ResultSchema,
)
from leap.games.rapid_fire.service import RapidFireService
from leap.service.container import ServiceContainer
from leap.types.player import CurrentPlayer
from leap.types.rapid_fire import RapidFirePlayPayload, RapidFireQuestionDTO, RapidFireResultDTO


router = APIRouter()


def _question_schema(question: RapidFireQuestionDTO) -> QuestionSchema:
    return QuestionSchema(
        id=question.id,
        question=question.question,
        options=list(question.options),
        time_limit_ms=question.time_limit_ms,
    )


def _result_schema(result: RapidFireResultDTO) -> ResultSchema:
    return ResultSchema(
        score=result.score,
        correct_count=result.correct_count,
        wrong_count=result.wrong_count,
        skipped_count=result.skipped_count,
        time_taken_seconds=result.time_taken_seconds,
    )


def _play_response(payload: RapidFirePlayPayload) -> PlayResponse:
    return PlayResponse(
        status=payload.status,
        game_session_id=payload.game_session_id,
        questions_answered=payload.questions_answered,
        questions_total=payload.questions_total,
        question=_question_schema(payload.question) if payload.question is not None else None,
        result=_result_schema(payload.result) if payload.result is not None else None,
    )


def _rapid_fire_svc(container: ServiceContainer) -> RapidFireService:
    return container.rapid_fire


@router.post("/play", response_model=PlayResponse, summary="Start or resume Rapid Fire Quiz")
async def play(
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> PlayResponse:
    """Unified entrypoint for starting, resuming, or viewing the final result."""
    payload = await _rapid_fire_svc(container).play(player.id)
    return _play_response(payload)


@router.post("/answer", response_model=AnswerResponse, summary="Submit an answer")
async def answer(
    body: AnswerRequest,
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> AnswerResponse:
    """Record one answer and return the running score plus the next question."""
    out = await _rapid_fire_svc(container).submit_answer(
        player.id, body.question_id, body.selected_option, body.time_ms
    )
    return AnswerResponse(
        correct=out.correct,
        correct_option=out.correct_option,
        correct_answer_text=out.correct_answer_text,
        current_score=out.current_score,
        questions_answered=out.questions_answered,
        questions_remaining=out.questions_remaining,
        next_question=_question_schema(out.next_question) if out.next_question is not None else None,
        result=_result_schema(out.result) if out.result is not None else None,
    )


@router.post("/abandon", response_model=AbandonResponse, summary="Abandon Rapid Fire Quiz")
async def abandon(
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> AbandonResponse:
    """Forfeit with a partial result."""
    result = await _rapid_fire_svc(container).abandon(player.id)
    return AbandonResponse(result=_result_schema(result))
