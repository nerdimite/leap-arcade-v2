# Sub-2: Seed Data — Real Questions

**Status:** pending
**Depends on:** nothing (pure data, no code dependency)
**Blocks:** nothing at the code layer (but required for end-to-end testing)

## Tasks

- **Convert `docs/rapid-fire.json`** (15 real questions in raw `option1..4` + `correct_ans` format) to the canonical seed format and replace `backend/leap/seeds/data/rapid_fire.json`

  Conversion rules (apply to each question):
  - `"question"` → keep as-is
  - `"options"` → `[q["option1"], q["option2"], q["option3"], q["option4"]]`
  - `"correct_option_index"` → `q["correct_ans"]` — **already 1-indexed in raw data, keep as-is**
  - `"category"` → `"Technology"` for all 15 questions (raw data has no category field)
  - `"time_limit_ms"` → `15000` for all 15 questions

  Example of one converted entry:
  ```json
  {
    "question": "In AI-assisted software development, what best describes an "agentic workflow"?",
    "options": [
      "A CI/CD pipeline triggered by Git commits",
      "A system where models autonomously plan and execute multi-step tasks",
      "A distributed tracing mechanism for APIs",
      "A runtime optimization layer for container orchestration"
    ],
    "correct_option_index": 2,
    "category": "Technology",
    "time_limit_ms": 15000
  }
  ```

- **Verify the seed loader** (`leap/seeds/loader.py`) already handles this format — it does (`_seed_rapid_fire` reads `question`, `options`, `correct_option_index`, `category`, `time_limit_ms`). No code change needed in the loader.

- **Replace the 10 placeholder questions** in `rapid_fire.json` entirely with the 15 real questions. Do not keep the old ones.

## Acceptance Criteria

- `backend/leap/seeds/data/rapid_fire.json` contains exactly 15 entries
- Each entry has: `question`, `options` (4-element list), `correct_option_index` (1-indexed int), `category`, `time_limit_ms`
- `correct_option_index` values match the correct answers from `docs/rapid-fire.json` — spot check at least 3 questions manually
- Running `seed_all()` against a clean DB inserts all 15 rows into `rapid_fire_questions` with no errors

## Code References

- `docs/rapid-fire.json` — source (raw format, do not modify this file)
- `backend/leap/seeds/data/rapid_fire.json` — target (replace entirely)
- `backend/leap/seeds/loader.py` — verify only, no changes

## Technical Guidelines

- `correct_option_index` is **1-indexed** — `correct_ans: 2` in raw data means option2 is correct, which maps directly to `correct_option_index: 2`. Do not subtract 1.
- The seed uses `ON CONFLICT DO NOTHING` — running it twice is safe; the second run is a no-op
- All 15 questions are from the Technology/Software Engineering domain — using `"Technology"` as category for all is intentional and consistent
