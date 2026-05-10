# Engineering Principles (Reference)

Memory jog for the `senior-software-engineer` jam skill. Use these as lenses to push back from. Don't recite them in chat — reach for the one that's relevant and translate it into a concrete question or counterpoint about the user's idea.

These apply across backend, frontend, AI agents, and infra. They are deliberately general.

---

## 1. Product & Business First

- **Solve the actual problem, not the proxy.** A feature that satisfies the literal request but misses the underlying user job is wasted work.
- **Whose pain, whose budget, whose decision?** Engineering trade-offs are also business trade-offs. Ask who feels the cost.
- **Time-to-market vs. correctness vs. cost.** Pick consciously. Default to shipping a thin slice and learning.
- **Compliance, contracts, regulation as constraints, not afterthoughts.** Especially for healthcare, finance, PII, payments. Surface them early.
- **Reversibility is a feature.** One-way doors (data migrations, public APIs, schema-of-record decisions) deserve more design than two-way doors.

## 2. Simplicity, YAGNI, and the Cost of Code

- **The cheapest code is the code you don't write.** Every line is a future maintenance liability.
- **YAGNI ruthlessly.** If a feature isn't needed for the next concrete use case, defer it.
- **Prefer boring tech.** New tech needs to earn its place; defaults should be the team's existing stack.
- **Delete before you add.** Refactors that remove code are usually wins.
- **Beware premature abstraction.** Three concrete instances before extracting; two is often a coincidence.

## 3. Architecture Lenses

- **Coupling and cohesion.** Things that change together should live together; things that change independently should be separable.
- **Module boundaries follow ownership and change rate, not just domain nouns.**
- **Explicit data flow over hidden lifecycle magic.** Frameworks that "just work" eventually don't, and debugging hidden flow is expensive.
- **State is the enemy.** Push state to the edges; keep cores pure where you can.
- **Stable interfaces, evolvable internals.** Spend design effort on contracts; let implementations change.
- **Composition over inheritance.** Almost always.

## 4. Failure, Operations, and the Real World

- **Failure is the default state.** Networks partition, disks fill, processes crash, dependencies degrade. Design assuming this.
- **Blast radius matters more than likelihood.** A rare failure that takes down all tenants is worse than a common one that affects one.
- **Idempotency, retries, and at-least-once.** Most distributed flows want this trio.
- **Observability is a feature, not a chore.** Logs, metrics, traces, and audit are part of the design, not a follow-up.
- **Rollback paths.** If you can't roll it back, you can't ship it Friday afternoon. Migrations especially.
- **Backpressure and rate limits.** Especially for AI agents, queues, and any unbounded input.

## 5. Data

- **Schema is destiny.** Hard to change later, especially under load. Spend time here.
- **Source of truth must be unambiguous.** When two systems disagree, who wins, and how is that enforced?
- **Migrations are products.** Plan them as carefully as features. Backfills, dual-writes, cutover, rollback.
- **Privacy by design.** Minimize data collected, scope access, plan retention and deletion from day one.
- **Consistency model is a design choice, not a default.** Strong vs. eventual vs. read-your-writes — pick per use case.
- **Cache invalidation is the hard part.** Always design the invalidation path before the cache itself.

## 6. APIs and Contracts

- **Design from the consumer in.** What does the call site want to write?
- **Make the easy case easy and the dangerous case loud.** Defaults should be safe.
- **Versioning strategy on day one.** Even if it's just "we'll never break v1".
- **Errors are part of the contract.** Type them, document them, return them consistently.
- **Pagination, filtering, sorting, partial responses — pick conventions and reuse them.**

## 7. Security & Trust

- **Authn and authz are different.** Don't conflate them. ABAC/RBAC choices have long shadows.
- **Trust boundaries are explicit.** Mark where untrusted input enters and validate at the boundary.
- **Secrets, tokens, PII — least privilege, shortest lifetime, audit access.**
- **Multi-tenancy is a security property, not just a partitioning trick.**

## 8. Performance

- **Measure before optimizing.** Cold path numbers beat intuitions.
- **Latency budgets per request, not per query.** Decompose budgets across components.
- **Hot paths deserve cache, batching, or denormalization. Cold paths don't.**
- **N+1 is everywhere.** Watch for it across DB, HTTP, and LLM calls.
- **Streaming over buffering for large responses, especially LLM output.**

## 9. Frontend-Specific Lenses

- **State is layered.** URL state > server state > client state > component state. Push state up the layers, not down.
- **Server-driven where you can, client-driven where you must.**
- **Loading, empty, error, partial — all four states for every view.**
- **Optimistic UI is a contract with the server, not a UI trick.** Plan reconciliation.
- **Accessibility is correctness.** Keyboard, screen reader, contrast, focus management.
- **Bundle size is a budget.** Every dependency is a tax on every user.

## 10. AI Agents and LLM Systems

- **Determinism is a design choice.** Where do you want randomness, where do you not?
- **Evals before prompts.** A prompt without an eval is a vibe.
- **Tool design dominates prompt quality.** Good tools, clear schemas, narrow scopes.
- **Context window is a budget.** Every token competes. Progressive disclosure beats kitchen-sink prompts.
- **Failure modes are LLM-specific.** Hallucination, refusal, format drift, prompt injection. Design for them.
- **Human-in-the-loop checkpoints for irreversible actions.** Especially writes, payments, sends.
- **Cost and latency are first-class.** Model choice, caching, streaming, batching.
- **Observability for agents needs traces, not just logs.** What did it see, what did it decide, what did it call?

## 11. Testing and Confidence

- **Tests scale with risk, not with code.** High-blast-radius code earns more tests.
- **Behavior tests over implementation tests.** Refactor-friendly is the goal.
- **Integration and contract tests catch the bugs unit tests can't.**
- **Test what would actually break in prod.** Not what's easy to test.
- **Flaky tests are worse than no tests.** Fix or delete.

## 12. Team and Communication

- **Design docs are for thinking, not for showing off.** Short, opinionated, decision-oriented.
- **Running notes capture the "why we didn't" as well as the "why we did".**
- **Make the implicit explicit.** If a decision relies on tribal knowledge, write it down.
- **Reversible decisions: decide fast and move. Irreversible decisions: slow down.**
- **Disagree and commit, but write down the disagreement.**
