# Meridian — Testing Guidelines

Reference for both [deep-design](../deep-design/SKILL.md) (writing the failing tests during the jam) and [builder](../builder/SKILL.md) (turning red to green during execution). Stack assumed: **Python + pytest**. Adapt naming idioms if the project uses a different stack — the principles are stack-agnostic.

> Read this file when: writing or modifying tests during the jam, filling in TODO edge-case tests during execution, adding any kind of test double (mock / fake / stub), or tempted to add a test-only method to production code.

## Core Principle

Tests verify **observable behavior**, not implementation details and not whether mocks were called. Mocks are a means to isolate, not the thing under test.

If a test would still pass after you delete the function it claims to test and replace it with `raise NotImplementedError`, the test is testing the mock, not the function.

## Test-Writing Principles (apply to every test in Meridian)

1. **One behavior per test.** If the test name has "and" in it, split it. `test_validates_email_and_domain_and_whitespace` is three tests.
2. **Behavioral name.** `test_raises_when_slot_taken_between_check_and_hold` not `test_booking_2`. The name is half the documentation.
3. **Test real behavior, not mock behavior.** Assert on observable outcomes — return values, state changes in fakes, raised exceptions. Not on `mock.call_count` or `mock.assert_called_with(...)` unless the call itself is the contract (e.g. "must emit this event").
4. **Prefer fakes over mocks.** A `FakeSlotRepository` with real-ish in-memory behavior is more honest than `MagicMock` with hardcoded return values. Stubs and tests written against fakes survive refactoring; mock-call assertions don't.
5. **Show the wished-for API.** The test is the first consumer of the function. If the test is awkward to write, the function signature is wrong — fix the signature now (in the jam) while it is cheap.
6. **Dependency injection.** The function takes its collaborators as arguments (or via a constructor) — never reaches out to module-level singletons or imports the database directly. If a test needs to mock half the world, the design is too coupled. Listen to the test.
7. **Arrange / Act / Assert structure.** One clear setup block, one call to the unit under test, one or more focused assertions. Even when implicit, the shape should be obvious.
8. **Cover the contract from the docstring.** Every behaviour, failure mode, and dependency mentioned in the Design Doc entry should map to at least one test (or an explicit edge-case TODO).
9. **Deterministic.** No real network, no real DB, no `time.sleep`, no flaky timing. Inject the clock, use fakes, and seed any randomness.

## The Stub Convention

Stubs use `raise NotImplementedError`, not `pass`:

```python
def process_booking(patient_id: str, slot_id: str) -> BookingResult:
    """Books a slot for a patient. Soft locks before writing. Notification is fire-and-forget."""
    raise NotImplementedError
```

Why: an accidental call surfaces loudly during execution rather than silently returning `None`. It also means tests written against the stub structurally fail for the right reason — the contract is not yet satisfied — rather than passing because `None == None`.

## Pytest Patterns

### Class-grouped tests with fakes

```python
import pytest

class TestProcessBooking:
    def test_books_available_slot_successfully(self):
        """Happy path: available slot is held and booking record is created."""
        slot_repo = FakeSlotRepository(available={"slot_456"})
        booking_repo = FakeBookingRepository()
        notifier = FakeNotifier()

        result = process_booking(
            "patient_123",
            "slot_456",
            slot_repo=slot_repo,
            booking_repo=booking_repo,
            notifier=notifier,
        )

        assert result.status == BookingStatus.CONFIRMED
        assert result.booking_id is not None
        assert booking_repo.has_booking(result.booking_id)
        assert "slot_456" in slot_repo.held_slots

    def test_raises_when_slot_taken_between_check_and_hold(self):
        slot_repo = FakeSlotRepository(available={"slot_456"}, race_on_hold=True)
        with pytest.raises(SlotUnavailableError):
            process_booking("patient_123", "slot_456", slot_repo=slot_repo, ...)

    def test_booking_succeeds_even_when_notification_fails(self):
        notifier = FakeNotifier(should_fail=True)
        result = process_booking("patient_123", "slot_456", notifier=notifier, ...)
        assert result.status == BookingStatus.CONFIRMED
```

### Parametrize for variations of the same behavior

```python
@pytest.mark.parametrize("invalid_email", ["", "   ", "not-an-email", "no@dot"])
def test_rejects_invalid_email(invalid_email):
    with pytest.raises(ValidationError):
        validate_email(invalid_email)
```

### Async tests

```python
@pytest.mark.asyncio
async def test_handles_concurrent_booking_attempts():
    ...
```

### Fixtures for shared fakes (when the same setup repeats across tests)

```python
@pytest.fixture
def slot_repo():
    return FakeSlotRepository(available={"slot_456", "slot_789"})

def test_books_slot(slot_repo):
    ...
```

Don't reach for fixtures prematurely — inline setup is fine and often clearer for one-off tests. Promote to fixture when you copy-paste setup more than twice.

## Anti-Patterns

### 1. Asserting on Mock Behavior

```python
# Bad: verifies the mock exists, tells you nothing about the real function
def test_books_slot():
    mock_repo = MagicMock()
    mock_repo.create.return_value = "booking_123"
    result = process_booking("patient_1", "slot_1", booking_repo=mock_repo)
    assert mock_repo.create.called  # tests the mock, not process_booking
```

```python
# Good: assert on observable outcome via a fake
def test_books_slot():
    booking_repo = FakeBookingRepository()
    result = process_booking("patient_1", "slot_1", booking_repo=booking_repo)
    assert booking_repo.has_booking(result.booking_id)
```

**Gate:** before writing `mock.assert_called_with(...)` or `assert mock.called`, ask — "is this call the contract, or is it an implementation detail?" If it's implementation detail, switch to asserting on outcome via a fake.

Exception: when the call itself *is* the contract (e.g. "must publish this exact event payload to the event bus"), asserting on the call is fine — the published event is the observable behavior.

### 2. Test-Only Methods in Production Code

```python
# Bad: reset_for_test() exists only for tests, but lives on the production class
class BookingService:
    def reset_for_test(self):
        self._cache.clear()
        self._counters = defaultdict(int)
```

```python
# Good: test utility module owns test-only helpers
# in tests/helpers.py
def reset_booking_service(svc: BookingService) -> None:
    svc._cache.clear()
    svc._counters = defaultdict(int)
```

**Gate:** before adding a method to a production class, ask — "is this only used by tests?" If yes, it belongs in `tests/helpers.py` or as a fake-class method, never in production.

### 3. Mocking Without Understanding the Dependency Chain

```python
# Bad: mocks the high-level method and accidentally bypasses the side effect the test depends on
def test_detects_duplicate_server(monkeypatch):
    monkeypatch.setattr("server_manager.discover_and_register", lambda *_: None)
    add_server(config)
    add_server(config)  # should raise DuplicateError but won't, because register was mocked away
```

```python
# Good: mock at the right level — the slow/external thing, not the orchestration layer
def test_detects_duplicate_server(monkeypatch):
    monkeypatch.setattr("server_manager.start_server_process", lambda *_: FakeProcess())
    add_server(config)
    with pytest.raises(DuplicateServerError):
        add_server(config)
```

**Gate:** before mocking anything, ask the three questions:
1. What side effects does the real method have?
2. Does the test depend on any of them?
3. If yes, mock at a lower level — the actual slow/external operation — not the orchestration method itself.

Red flags: "I'll mock this just to be safe", "this might be slow, better mock it", mocking without tracing the call chain.

### 4. Incomplete Mocks (Partial Response Shapes)

```python
# Bad: only the fields you immediately use are present; downstream code breaks on .metadata
mock_response = {"status": "success", "data": {"user_id": "123"}}
```

```python
# Good: mirror the real API completeness, including fields downstream code may consume
mock_response = {
    "status": "success",
    "data": {"user_id": "123", "name": "Alice"},
    "metadata": {"request_id": "req-789", "timestamp": 1234567890},
}
```

**Gate:** if you're constructing a fake API response, mirror the actual response schema completely — not just the fields your immediate test reads. Partial mocks fail silently when downstream code accesses an omitted field. When in doubt, copy a real response from the API docs / a recorded fixture.

### 5. Tests as Afterthought

In Meridian this is structurally prevented — the jam ends with failing tests already in place, and the executor is forbidden from writing production code without a failing test first. But two specific creep-ins to watch for:

- **Skipping a TODO edge case** during execution because "it's not in the base AC". The TODO comments above test classes are part of the spec — they don't get skipped.
- **Writing the implementation first then back-filling tests** during execution. If the executor finds it needs new behaviour beyond the existing tests, it must write the failing test first, watch it fail for the right reason, then implement.

### 6. Over-Complex Mock Setup

If the mock setup is longer than the test logic, or if you find yourself mocking five things to test one, the design under test is too coupled. The test is telling you to refactor the production code's collaborator list — usually by injecting a single higher-level collaborator instead of five low-level ones.

Warning signs:
- Mock setup is >50% of the test body
- You're mocking everything just to make the test pass
- Mocks are missing methods that the real component has (and you're patching them ad-hoc as needed)
- The test breaks every time the mock library changes

When you hit this in the jam: stop and re-shape the function signature. When you hit this during execution: flag it in the implementation notes — do not paper over it.

## Mock vs Fake vs Stub — Quick Reference

| Type | What it is | When to use |
|---|---|---|
| **Fake** | Hand-written class with real-ish in-memory behavior (e.g. `FakeSlotRepository` backed by a `set`). | **Default choice in Meridian.** Survives refactors. Lets tests assert on outcomes. |
| **Stub** | Returns canned values, no logic. | Quick replacement for a dependency whose behavior the test doesn't care about. |
| **Mock** | Records calls so you can assert on them. | Only when the call itself is the contract (e.g. event publication, audit log). |

If you're reaching for `unittest.mock.MagicMock` in the jam, pause and ask whether a fake would express the contract more honestly.

## Quick Reference Table

| Anti-pattern | Fix |
|---|---|
| Asserting on mock call counts | Assert on observable outcome via a fake |
| Test-only method on production class | Move to `tests/helpers.py` or a fake class |
| Mock without tracing the dependency chain | Mock at the lowest level (the slow/external op) |
| Partial mock response | Mirror the real schema completely |
| Skipping TODO edge cases | TODOs are part of the spec, not optional |
| Over-complex mock setup | Refactor the production signature; the test is telling you something |
| `MagicMock` everywhere | Switch to a hand-written fake |
| `time.sleep` in a test | Inject the clock, use a fake clock |
| Test passes against `raise NotImplementedError` | The test isn't actually exercising the function — fix it |

## Red Flags — Stop and Fix

- Assertion is `mock.called` or `mock.call_count == N` and the call is not the contract
- Method on a production class is only ever called from `tests/`
- Mock setup is more than half the test body
- Test still passes after replacing the function under test with `raise NotImplementedError`
- "Let me just mock this to be safe"
- Test depends on real network, real DB, real wall-clock, real randomness
- New production code was written without a failing test first (executor only)
