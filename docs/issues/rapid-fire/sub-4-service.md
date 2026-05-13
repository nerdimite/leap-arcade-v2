# Sub-4: RapidFireService + Container + Lifespan

**Status:** pending
**Depends on:** Sub-3 (types, DAOs, and scoring module must exist)
**Blocks:** Sub-5 (routes delegate to the service)

## Tasks

### 1. Implement `leap/games/rapid_fire/service.py`

Full rewrite of the current empty shell. Implement in this order:

**`__init__`**
```python
def __init__(
    self,
    ctx: ContextManager,
    game_session_dao: GameSessionDAO,
    rapid_fire_answer_dao: RapidFireAnswerDAO,
    rapid_fire_question_dao: RapidFireQuestionDAO,
) -> None:
    self.ctx = ctx
    self.game_session_dao = game_session_dao
    self.rapid_fire_answer_dao = rapid_fire_answer_dao
    self.rapid_fire_question_dao = rapid_fire_question_dao
    self._questions: Dict[str, RapidFireQuestionDTO] = {}
```

**`initialize(session: AsyncSession) -> None`**
- Calls `rapid_fire_question_dao.get_all(session)`
- Stores result as `self._questions = {q.id: q for q in questions}`
- Called once from lifespan — not a request handler
- If the table is empty, `self._questions` is `{}` — no error raised here; `play()` will return 503

**`_pick_next_question(asked_ids: List[str]) -> Optional[RapidFireQuestionDTO]`** (private)
- `remaining = {id: q for id, q in self._questions.items() if id not in set(asked_ids)}`
- Returns `random.choice(list(remaining.values()))` if non-empty
- Returns `None` if remaining is empty (pool exhausted)

**`play(player_id: str) -> PlayResponse`**
```
1. async with self.ctx.session() as session:
2.   game_session = await self.game_session_dao.get_by_player_and_game(session, player_id, "rapid_fire")
3.   Branch on game_session:
     — None (new player):
         create session via game_session_dao.create(session, player_id, "rapid_fire")
         question = _pick_next_question([])
         if question is None: raise NoQuestionsAvailableException()
         return active PlayResponse(game_session_id, questions_answered=0, questions_total=len(self._questions), question)
     — active:
         asked_ids = await rapid_fire_answer_dao.get_asked_question_ids(session, game_session.id)
         question = _pick_next_question(asked_ids)
         if question is None: raise NoQuestionsAvailableException()
         return active PlayResponse(game_session_id, questions_answered=len(asked_ids), questions_total=len(self._questions), question)
     — completed or abandoned:
         answers = await rapid_fire_answer_dao.get_all_for_session(session, game_session.id)
         result = _build_result(game_session, answers)   # uses game_session.score — do NOT recompute
         return PlayResponse(status=game_session.status, result=result)
```

**`submit_answer(player_id, question_id, selected_option, time_ms) -> AnswerResponse`**
```
1. async with self.ctx.session() as session:
2.   game_session = await game_session_dao.get_by_player_and_game(session, player_id, "rapid_fire")
3.   if game_session is None: raise SessionNotFoundException(player_id, "rapid_fire")
4.   if game_session.status != "active": raise SessionAlreadyCompletedException(game_session.id, game_session.status)
5.   if question_id not in self._questions: raise 422 (invalid question_id)
6.   answers = await rapid_fire_answer_dao.get_all_for_session(session, game_session.id)
7.   asked_ids = {a.question_id for a in answers}
8.   if question_id in asked_ids: raise QuestionAlreadyAnsweredException(question_id)
9.   question = self._questions[question_id]
10.  skipped = selected_option is None
11.  correct = (not skipped) and (selected_option == question.correct_option_index)
12.  effective_time_ms = max(500, min(time_ms, question.time_limit_ms))
13.  await rapid_fire_answer_dao.create(session, game_session.id, question_id, correct, skipped, selected_option, effective_time_ms)
14.  # Build current answer DTO in-memory and append to answers list for scoring
     current_answer = RapidFireAnswerDTO(... fields from above ...)
     all_answers = answers + [current_answer]
15.  current_score = compute_rapid_fire_score(all_answers, self._questions)
16.  new_asked_ids = asked_ids | {question_id}
17.  game_over = len(new_asked_ids) == len(self._questions)
18.  if game_over:
         await game_session_dao.update_status(session, game_session.id, GameSessionStatus.COMPLETED, score=current_score)
         result = RapidFireResultDTO(score=current_score, ...)  # build breakdown from all_answers
         return AnswerResponse(..., next_question=None, result=result)
19.  else:
         next_q = _pick_next_question(list(new_asked_ids))
         return AnswerResponse(..., next_question=next_q, result=None)
```

`correct_answer_text` in `AnswerResponse` = `question.options[question.correct_option_index - 1]` (options is 0-indexed list, correct_option_index is 1-indexed).

**`abandon(player_id: str) -> AbandonResponse`**
```
1. async with self.ctx.session() as session:
2.   game_session = get_by_player_and_game(session, player_id, "rapid_fire")
3.   404 / 409 guards (same as submit_answer)
4.   answers = get_all_for_session(session, game_session.id)
5.   score = compute_rapid_fire_score(answers, self._questions)
6.   await game_session_dao.update_status(session, game_session.id, GameSessionStatus.ABANDONED, score=score)
7.   return AbandonResponse(result=_build_partial_result(game_session, answers, score))
```

**`_build_result(game_session, answers)` (private helper)**
- Uses `game_session.score` for the score value (already stored — do not recompute)
- `correct_count = sum(1 for a in answers if a.correct)`
- `wrong_count = sum(1 for a in answers if not a.correct and not a.skipped)`
- `skipped_count = sum(1 for a in answers if a.skipped)`
- `time_taken_seconds = (game_session.completed_at - game_session.started_at).total_seconds()`
- Returns `RapidFireResultDTO`

### 2. Update `leap/service/container.py`

- Instantiate `RapidFireAnswerDAO` and `RapidFireQuestionDAO`
- Pass all three DAOs into `RapidFireService.__init__`
- Remove the existing `# TODO: wire leaderboard` comment — keep as pending, it's out of scope

### 3. Update `leap/api/main.py` lifespan

After seed loading, open a session and call `container.rapid_fire.initialize(session)`:
```python
async with context_manager.session() as session:
    await container.rapid_fire.initialize(session)
```
This must run after `seed_all()` so the `rapid_fire_questions` table is populated before the cache load.

## Acceptance Criteria

- `play()` returns a question for a new player, a different unanswered question on resume, and the stored result for a completed player
- `submit_answer()` returns `current_score` on every call (not just game over)
- `submit_answer()` returns `next_question=None` and an inline `result` block when all questions answered
- `abandon()` returns the partial result including score computed from submitted answers
- On replay (`question_id` already in `asked_ids`), `submit_answer()` raises `QuestionAlreadyAnsweredException`
- `_questions` dict is populated with all 15 entries after `initialize()` runs
- `correct_answer_text` correctly maps `correct_option_index - 1` into the `options` list

## Code References

- `leap/games/rapid_fire/service.py` — primary (full rewrite)
- `leap/service/container.py` — update wiring
- `leap/api/main.py` — lifespan update
- `leap/service/exceptions.py` — reference; all exception types already defined
- `leap/games/rapid_fire/scoring.py` — imported by service (must exist from Sub-3)

## Technical Guidelines

- Service owns the session lifecycle — one `async with self.ctx.session()` per method, never nested
- `_questions` is a private attribute (underscore prefix) — this is a lazy-init internal cache, which is the correct exception to the no-underscore-prefix rule for injected dependencies
- `correct_option_index` is **1-indexed** in the DTO — when deriving `correct_answer_text` use `options[correct_option_index - 1]`
- The in-memory `RapidFireAnswerDTO` constructed in step 14 of `submit_answer` does not need a real `id` or `answered_at` — it only needs the fields that `compute_rapid_fire_score` reads (`question_id`, `correct`, `skipped`, `time_ms`). Use placeholder values for the rest.
- `NoQuestionsAvailableException` (503) is raised if `_pick_next_question` returns None — this should only happen if the cache was empty at startup
- Do not import from `leap/api/` in the service layer
