"""Pure scoring for Rapid Fire — no DB or I/O."""

from typing import Dict, List

from leap.types.rapid_fire import RapidFireAnswerDTO, RapidFireQuestionDTO

_MIN_RAPID_FIRE_TIME_MS = 500


def clamp_rapid_fire_time_ms(time_ms: int, time_limit_ms: int) -> int:
    """Clamp a client-reported answer time to the scoring window."""
    return max(_MIN_RAPID_FIRE_TIME_MS, min(time_ms, time_limit_ms))


def compute_rapid_fire_score(
    answers: List[RapidFireAnswerDTO],
    questions: Dict[str, RapidFireQuestionDTO],
) -> int:
    """Sum per-answer points.

    Wrong and skipped answers score 0. Correct answers score 50–100 from response time:
    effective time at the anti-cheat floor (500 ms) maps to 100 pts; effective time at
    ``time_limit_ms`` maps to 50 pts (linear interpolation).
    Raises ``KeyError`` if ``answer.question_id`` is missing from ``questions``.
    """
    total = 0
    for answer in answers:
        question = questions[answer.question_id]
        if answer.skipped or not answer.correct:
            continue

        limit_ms = question.time_limit_ms
        effective_time_ms = clamp_rapid_fire_time_ms(answer.time_ms, limit_ms)
        span = max(limit_ms - _MIN_RAPID_FIRE_TIME_MS, 1)
        ratio = max(
            0.0,
            min(1.0, (effective_time_ms - _MIN_RAPID_FIRE_TIME_MS) / span),
        )
        total += round(100 - ratio * 50)

    return max(0, total)
