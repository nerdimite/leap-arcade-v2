"""Four Pics, One Lie game routes."""

from fastapi import APIRouter, Depends

from leap.api.deps import get_container, get_current_player
from leap.api.schema.four_pics import (
    AbandonResponse,
    AnswerRequest,
    AnswerResponse,
    PlayResponse,
    QuestionStateSchema,
    ResultQuestionSchema,
    ResultSchema,
)
from leap.games.four_pics.service import FourPicsService
from leap.service.container import ServiceContainer
from leap.types.four_pics import (
    FourPicsAnswerPayload,
    FourPicsPlayPayload,
    FourPicsQuestionStateDTO,
    FourPicsResultDTO,
)
from leap.types.player import CurrentPlayer

router = APIRouter()


def _question_schema(question: FourPicsQuestionStateDTO) -> QuestionStateSchema:
    return QuestionStateSchema(
        question_id=question.question_id,
        question_number=question.question_number,
        total_questions=question.total_questions,
        image_paths=list(question.image_paths),
        status=question.status,
        started_at=question.started_at,
    )


def _result_schema(result: FourPicsResultDTO) -> ResultSchema:
    return ResultSchema(
        score=result.score,
        questions_correct=result.questions_correct,
        questions_wrong=result.questions_wrong,
        questions_not_reached=result.questions_not_reached,
        questions=[
            ResultQuestionSchema(
                question_id=q.question_id,
                status=q.status,
                score=q.score,
                time_bonus=q.time_bonus,
            )
            for q in result.questions
        ],
    )


def _play_response(payload: FourPicsPlayPayload) -> PlayResponse:
    return PlayResponse(
        session_status=payload.session_status,
        session_score=payload.session_score,
        question=_question_schema(payload.question) if payload.question is not None else None,
        result=_result_schema(payload.result) if payload.result is not None else None,
    )


def _answer_response(payload: FourPicsAnswerPayload) -> AnswerResponse:
    return AnswerResponse(
        correct=payload.correct,
        score=payload.score,
        time_bonus=payload.time_bonus,
        session_status=payload.session_status,
        session_score=payload.session_score,
        question=_question_schema(payload.question) if payload.question is not None else None,
        result=_result_schema(payload.result) if payload.result is not None else None,
    )


def _four_pics_svc(container: ServiceContainer) -> FourPicsService:
    return container.four_pics


@router.post("/play", response_model=PlayResponse, summary="Start or resume Four Pics")
async def play(
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> PlayResponse:
    payload = await _four_pics_svc(container).play(player.id)
    return _play_response(payload)


@router.post("/answer", response_model=AnswerResponse, summary="Submit a Four Pics answer")
async def answer(
    body: AnswerRequest,
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> AnswerResponse:
    payload = await _four_pics_svc(container).submit_answer(
        player.id,
        body.question_id,
        body.selected_index,
        body.time_ms,
    )
    return _answer_response(payload)


@router.post("/abandon", response_model=AbandonResponse, summary="Abandon Four Pics session")
async def abandon(
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> AbandonResponse:
    """Forfeit with a partial result."""
    result = await _four_pics_svc(container).abandon(player.id)
    return AbandonResponse(result=_result_schema(result))
