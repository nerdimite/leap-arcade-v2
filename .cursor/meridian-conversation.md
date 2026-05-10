# Meridian — Design Session
**Full conversation export — Bhavesh & Claude**
**Date: May 10–11, 2026**

> Convention used in this document:
> Each turn is wrapped in a fenced block with a role header.
> Any markdown inside a turn is preserved verbatim.
> Separators (`---`) divide every turn.

---

````turn
ROLE: USER (voice note transcript)
````

Aur right? So I wanna brainstorm and new workflow. I am thinking that I want to follow for my agent. Take coding in the development environment like course or cloud code. So basically, I wanna create a new skill for backend. I mean, I mean, it could be for both front and back end.

Not really, I mean, you can keep it direct. Let's keep it generator, I guess it's more of her design principle. So like a low level design principle system design principles of think. But this is how I, basically what I work with AI. So where basically it's like a top down design, think.

So think of it like this. So, for example, if first discuss what we want at the API contract level, okay? So we are sending what data and what data be expect. I talk it and like in a General sense and you give me proposals for different API, contracts and different data formats and stuff.

So that's how we, you know, not on the screen of how what we want as the main thing. Okay, so that is stop when and that's the first level. So once you done with the API scheme, then we go one layer teeth. We go to the, you know, let's at the service there and you know, we think about, you know, what is the business logic that should be done here?

What is the business logically on a do? Yeah, so we do, we talk about that and then we talk about, you know, what is the database model? Or you know what is the database model required for this business logic? So yeah, so this is how this is the things.

So we basically go layer by layer from API layer, to service layer to data layer doing within. But it's just not, but it's not an high level. Like what I am explaining right now, it's more offer low level thing, so you Every time you are discussing anything. We are basically laying out.

What every file will do whatevery class in the file will do for ready. Function in the class will do. Right, so it's admit becomes like a low level diagram or data, flowthing, but data flow again is typically high level, but this is at a little level of at what file, what will happen when not writing code.

Just we just to be clear. That is not the intentist to define, behaviour not code because we can then use this design file where we are documenting all of this and then convert it to code. It was a coding at in the file. It's a then there is a point, right?

Any then might as well have been coding it from the starts. So

Function is just here. Just returning up thing, just a turning, the directors as it is, there is no logic to it or anything. That's a stop. That's a walk API innocence. And then we write unit tests and stuff, may be okay. Maybe we can do it like this. We create the service tab as well.

And this service tab is again a mock service and we take this mox service, and once you done with that, Video unit test, we write a unit test for the API layer, okay, I mean, okay for apnya probably doesn't really matter, so let's assume we are not really to you.

Let's think of it from her, from the service laptop. So you create a service, we define some functions, you mock, you just stop it. Like it's it doesn't do anything but you write unit test and you write these unit test. These are failing units. So this is out of like a mix of test and development, you define the terms, the define the behaviour in let's say the comments of the functions.

Okay, we wrote comments and stuff Erode may be Yahan virodh comments video, dog. Strings are something like that and we are writing unit test for them. These are feeling in my tests and we continue to do to this for every year. Down the stack. We go to the database layer, you do the same thing.

We define the class, we define the methods functions. We write the behaviour that we want in stuff and your basically discussing in code, I guess that's the reason. So basically until analyst we have a visual tool to, you know, discuss it all in one shot, we can just directly do it in code as well.

I don't mind. So, instead of writing, you know, long heaps of documentation or anything, you are just using the code itself. As the documentation to document are behaviour, we are writing and discussing the tests. And now, these tests what we are discussing, we are actually discussing a title deeper level.

I am not just asking you to, you know, come out with test or anything. I discussing what we want to test, so that these steps are essentially becoming our acceptance criteria and defining the Exact, you know, the exact thing, they exact behaviour, we want. So the tests instead of an after the fact thing, I even in your own thing like when we're doing testing development, it should be really properly.

Like the test are not supposed to be just, you know, random test to be tested just for the sake of coverage or anything. If they should be fine contract, we should define your behaviour expected. Behaviour, right. So use this as this and then what we do is we now have the acceptance critic essentially.

So now what we can do is now we can actually let the AI, you know, her and wild and you know write the code over ever to satisfy thos test. So again of course we want to eat that way. So what we do is we then create a markdown file which is which is the plan file basically or basic or may be a requirement for the and we let it figure it out.

We leave it some space to, you know. Do somethings like, Define. Of course, the tests define the acceptance criteria so that is just copy the work which is more like a checkbox. So let something like a definition of turnover acceptance criteria. We define us sample story. So actually we should have we should think of the histories.

Let's as you have to please and decides stories, the he is not on files. Also hold empty slots for the agent to right back to as memory or as notes or open questions for the end for human for me to review. So, for example, if it right, all of the cold, obviously it will be difficult for me to, you know, go through every line.

So, rather what you should do is it should give me a reading order, a reading order of all the files that I should read that and then also a section, which flags, okay. Take a look at this. This is the logic edit is this fine. Is this how you wanted?

So, anything that is out of the author. Array are not something that you would typically do, or maybe it is something that you are not sure of, if the AI is not sure of that, you know, the I personality wanted that way. So in those cases, Particular pieces, then those modular Whenever, And then the sighting, the relevant files for me to look at and give me like a quick Run through.

So it's like a thing of it like a like AI, like an in black, a General, Junior developer explaining to a senior developer, like what they did, and the sea and a, just a process. So, senior developers not directly looking at every line of code, right? The Junior developers are okay.

So I what edit is I went to this file. I so this function basically returns this. So in order for this function to work I would need a utility. So what I had it is I went and created a shared utility assuming that we would be reusing the second, is this the right way to it?

So this sort of questions These out of questions. So the AI, the implementary the agent, which is implementing all of this. So we can again create another skill for the implementation and itself. Based on these works, in this word for that. I am just defining your set. Yeah, we sort of create this thing.

There is, they are two skills, you are essentially. And that case, that means the first scale is a workflow that it's repeating. Also you will continue using the skill until you reach the point of air blast layer. In the software you waiter. It divided in League go from API to the service to the doubts, to any other utility is in everything, she sort of branch of its sort of like a mind map mind map being created of the entire philosopher, 1 API flow, your creating an entire work map.

So you like progressively going deeper in deeper and deeper and, you know, lying out what files will be needed, what functions they will have. So, this way, your sort of one sorting but, like, iteratively, like, interactively chatting with the user and, you know, one shorting but essentially at the end of the session, we kind of have the whole map.

The whole plan in design of the entire code. Bas essentially everything is stopped. We have unit test for Nahin. Everything is feeling aur, whatever. And yeah. And then, what will essentially happen is that because everything is testabling unit level created in a ways with the dependency injection, and everything, it's all unit.

Testible me, then, you know, go ahead and yeah, then we slice setup please. Slice out to the entire map in entire mind, map of the code based that we just designed at a lower level. And, you know, slic it out into junk or faces or unit level stories and every story contains the acceptance writer ho to set of unit test.

It contains what the expected behaviour is in free form language. We expect the

Implement and everything. Breaking it down into testable chunks to like it does. Some piece of work, it tests, its transfer unit test, and testes, and ensures complete, and then moves on to the next task. So it's like this stories, the upper is the top level thing under that. They are lot of task, like, Sa task, in sub tasks, or issues, and then sub issues.

Let's go with issues. Let's usually near Tetra analogy assume it is linear and bro, it that way. So every sub issue is independently testable and verify able by the AI implemented runs a new test series. If it's something is feeling and I am Run sitting and underwear or something, is consistently feeling about needs in attention than of course, it should be flat.

It should flat that thing as well. So that's what we will do.

In fact, let's keep it this way. If a linear MCB is present, it can use the lean. Yeah, I think, I think we can separate out. We can pick up this so that we will start with my down files, as 3, default place for all the issues, but

Yahan per. We should probably also have a version of this which directly integrates with the linear mcp and allows us to you know work with linear to do all these tasks. So that way we are task that tracking is actually with in your project management board as well. So I understood that.

Okay, coming back here is that So we do this. So essentially, everything at implemented a structured way and the reason why I am saying all of this is right, is that this initial fees. So this way of doing things, are you go from top to bottom? And while you are doing this process for every feature, or every code base, or anything?

And I mean, it could be like, at a feature level, of course, so Knowing this, we are mapping out all the flows and its allowing the human to think through and you know, review all the different education, all the different branches, the code execution path board, probably take. Right.

Even of the code is not in implemented, but we are at least discussing on all those things, right? So that way you are. Creating a good teapar understanding of your own code base. Because, yeah, we don't want. So this is not about bike coding. We should not be wife coding.

This we are understanding in deeper. We are we are we have we are still in control, the humanist, till in control over everything else. Happening is just that the AI is the hands while the human as the brain. I think it's that philosophy. So we help Envy still do the same thing we while we are doing this discussion of, you know, mapping it out, mapping out the low level mind map and stuff.

We are ofcourse doing all the typical approaches, you know, the ai's, you know, proposing a 2 to 3, different approaches to do the same thing. And you know, discussing how would you do? So regular super powers skills that we have, all of that principles do come in play? What is just the flow, a structured in a way that better Alliance with me.

Personally set is about me. I would like to understand what the flow is from the top down and I have that discussion there so its better for me to it that way to. And where am I implementing of future? Okay. So this was a long voice, not part, what my expectation right now is that?

Yeah, this is these are all just my roth hot, so to the dump. So I wanna organise these thoughts properly. So give me a proper document where whatever I just said is like properly organized, okay? So yeah.

---

````turn
ROLE: USER
````

so I wanna brainstorm a new agentic coding workflow I am thinking that I wanna follow for my AI IDEs like cursor. It's a like a top-down LLD design jam with unit tests, stories/issues and stuff like that. Here's a raw dump of my thoughts, transcribed from my voice notes.

So i want you to help me just organize my thoughts here first to understand whether you got my intent or not

---

````turn
ROLE: CLAUDE
````

Reading through your voice note now. Let me reflect back what I understood:

---

**The Core Philosophy**

You want a workflow where **the human stays the brain, AI is the hands**. Not vibe coding — you're in control, you understand the codebase deeply, you just don't want to be the one typing.

---

**The Workflow in Two Phases**

**Phase 1 — Design Jam (Top-Down LLD)**

You go layer by layer, discussing (not coding) what everything will do:

- API layer → Service layer → Data layer → Utilities
- At each layer: what files exist, what classes they have, what functions those classes have, what each function's behaviour is
- This progressively builds a "mind map" of the entire codebase
- The AI proposes 2-3 approaches at each decision point, you discuss and decide
- Output: stub code (empty functions with docstrings describing behaviour) + failing unit tests that act as **acceptance criteria**, not coverage checkboxes

The key insight: instead of a long design doc, **the stub code + tests ARE the design doc**. The tests define exact expected behaviour.

**Phase 2 — Agentic Implementation**

Once the full map is done, you slice it into stories → issues → sub-issues (Linear if MCP is available, markdown files as default). Each sub-issue is:
- Independently testable
- Has the failing unit tests attached
- Has expected behaviour in free-form language

The agent implements, runs tests, moves on. If something keeps failing → it flags it for you.

The agent also writes a **"junior dev handoff note"** at the end:
- Reading order for files
- Flags anything unusual/uncertain for your review
- Explains non-obvious decisions

---

**The Two Skills to Build**

1. **Design Skill** — the Phase 1 jam workflow
2. **Implementation Skill** — the Phase 2 agentic build workflow

---

Did I capture this right? Anything I missed or distorted?

---

````turn
ROLE: USER
````

yeah essentially yes, what do you think about this? be honest? push back if you find any problems with this?

---

````turn
ROLE: CLAUDE
````

Honestly, the core philosophy is solid. The "human as brain, AI as hands" framing with top-down LLD is genuinely better than how most people use AI coding tools. The failing-tests-as-acceptance-criteria idea is particularly good — it forces precision about behaviour before any code exists.

But here are my real pushbacks:

---

**1. The design jam might become its own form of vibe coding**

The risk is that you spend a long session "designing" at the file/function level, feel like you have a solid plan, but the design itself was AI-led. You rubber-stamped proposals without deeply thinking through edge cases because the conversation moved fast. The artefact looks rigorous (stubs, tests, mind map) but the thinking wasn't.

The antidote would need to be built into the skill — the AI should be challenging you, not just proposing. "You said the service layer handles X, but what happens when Y?" type questions.

---

**2. The stub + test as design doc breaks down for complex logic**

For CRUD-heavy features this works beautifully. But if you're doing something like the CellAssist telephony pipeline — where the real design decisions are about timing, concurrency, failure modes, latency budgets — unit tests on stubs don't capture that. You can write a test that says `translate()` returns a string, but the real question is what happens when Deepgram is 800ms late and Cartesia is already speaking.

For those cases you might need an explicit "non-functional requirements + failure modes" section in the design, not just behavioural tests.

---

**3. The agent handoff note is great in theory but hard to enforce**

Junior dev explaining to senior dev — love it. But in practice agents are bad at knowing what they don't know. The things they flag as uncertain are often not the things that will actually bite you. The subtle architectural decisions — "I put this in a shared utility assuming reuse" — they'll make confidently without flagging.

You'd need to be prescriptive in the skill prompt about *what categories* of decisions must always be flagged, not leave it to the agent's judgment.

---

**4. Phase 1 to Phase 2 handoff is the weakest link**

The mind map / design session lives in a conversation. The implementation agent works in a new context. How does the full design actually transfer? Markdown files are the answer you gestured at, but the structure of those files matters a lot. If it's just a dump of the conversation, the agent will miss things or misinterpret. This needs a defined schema — what does a "plan file" actually contain, in what format, at what level of detail.

---

**What I'd add**

A short **"constraint capture"** step before the design jam even starts — stack constraints, performance requirements, existing patterns in the codebase, things that are off-limits. Otherwise the design happens in a vacuum and Phase 2 produces code that doesn't fit the actual environment.

---

Overall: worth building. The gaps are solvable. Want to go into any of these deeper?

---

````turn
ROLE: USER
````

yeah okay, so thinking that this itself is a design session now for our skill-set, let's first outline a list of things and let's dive deeper on each

---

````turn
ROLE: CLAUDE
````

Love it. So meta — using the workflow to design the workflow.

Here's my proposed outline of things to nail down before we write a single line of the skill:

---

**1. Scope & Boundaries**
- What triggers this workflow? (new feature, new service, bug fix, refactor?)
- What's explicitly out of scope?
- Single skill or two separate skills, and where exactly does Phase 1 end and Phase 2 begin?

**2. Constraint Capture (Pre-Design)**
- What does the AI need to know before the jam starts?
- Stack, existing patterns, performance requirements, things that are off-limits

**3. The Design Jam Protocol (Phase 1)**
- Exact layer sequence and when to move between layers
- How the AI proposes options vs. challenges you
- What "done" looks like at each layer
- The stub + docstring + failing test format — exactly how structured?

**4. The Plan File Schema**
- What goes in it, in what format
- How it bridges Phase 1 → Phase 2 without losing fidelity
- Stories → Issues → Sub-issues structure

**5. The Implementation Protocol (Phase 2)**
- How the agent consumes the plan file
- Test-run-flag loop mechanics
- What categories of decisions must always be flagged (not left to agent judgment)

**6. The Handoff Note Format**
- Reading order logic
- Mandatory flag categories
- How the junior-dev-to-senior-dev explanation is structured

**7. Linear MCP Integration**
- When it kicks in, how issues map to the story structure
- Fallback to markdown when Linear isn't present

---

Which one do you want to start with?

---

````turn
ROLE: USER
````

let's start with the first one itself

so I want this to run typically on major features, major refactors ofcourse, new services, anything which benefits from a long ass design session lol

simple bug fixes might not be for this mode

Yeah I think we need one skill for the design phase (which includes creation of the mock code, stubs and unit tests).

One skill for translating our code-native design into a list of issues which includes both top level story, acceptance criteria as well as technical design guidelines as part of direct code references and stuff and also breaking it into proper task units that a typical executor subagent can take up to work on. Also what can be worked on independently and what needs dependencies. So that tasks are properly split into batches of work essentially or more like sub-issues

Then we could have an execution skill which orchestrates sub agents (again designed properly with all the engineering best practices guidelines for these little execution agents) to finish all the sub issues (which are batches of tasks that can be done independently or those which need to be done in a sequence or whatever). But ofcourse the orchestrator can do the executions itself as well if it thinks it needs to do it in a certain way.

but yeah all in all something like this

---

````turn
ROLE: CLAUDE
````

Good, this is getting cleaner. Let me reflect back the three-skill architecture:

---

**Skill 1: Design Jam**
- Triggered by: major features, new services, major refactors
- Output: stub code + docstrings + failing unit tests (code-native design)
- The "design doc" lives in the code itself, not in a separate document

**Skill 2: Issue Architect**
- Input: the stub/test codebase from Skill 1
- Output: structured issue tree
  - Top-level story (user-facing goal)
  - Sub-issues that are proper task units for an executor agent
  - Each sub-issue has: acceptance criteria, technical design guidelines, direct code references
  - Dependency mapping: what can run in parallel, what needs sequencing → batches

**Skill 3: Orchestrator + Executor**
- Input: the issue tree from Skill 2
- Orchestrates sub-agents to work through batches
- Can also execute directly if it determines that's better
- Each sub-agent works one sub-issue at a time: implement → run tests → verify → move on
- Flags and handoff note at the end

---

Two things I want to pressure test before we move on:

**On the Skill 1/2 boundary** — Skill 2 reads the stub codebase and derives the issue structure from it. But during the design jam, you're also making decisions that aren't captured in stubs — like "we chose approach B over A because of X". Does Skill 2 need access to the design conversation itself, or just the code output? Because if it's just the code, that reasoning is lost.

**On Skill 3 orchestration** — when you say sub-agents, are you thinking actual parallel Claude instances (like Claude Code worktrees in parallel), or more like a sequential orchestrator that plays the role of multiple agents one at a time?

---

````turn
ROLE: USER
````

idk but it might help if we do create a flow guide of sorts pointing to all the files and a brief summary of their behaviours not just design living in code. And also the thing you talked about with ensuring the design jam pushes back as well and challenges ideas and offers options

on the sub issues, I think let's keep every sub issue basically be that batch of tasks rather. so that if its assigned on linear it can have some tangible output. So the sub-issue itself contains all the tasks that can be done coeherently. If sub-issues have dependencies that are flagged as well so that a sub issue isnt picked up by another agent session without the completion of the previous one or so

yeah and the orchestrator and executors are basically checking the issue statuses as done or whatever as well

well does it need that decision for implementation? we could just refer to the full transcript for skill 2 to use as additional context if necessary for the issue planning. basically this step is a mix of tech lead + scrum master + product manager in a sense

i mean to begin with sequential spawning of sub agents or running them in parallel (without worktrees for now, tbh I am not very comfortable with the concept of worktrees yet so i mean we can circle back to this in a bit maybe)

---

````turn
ROLE: CLAUDE
````

Good, this is much cleaner. Let me re-reflect the full picture with these updates:

---

**Skill 1: Design Jam**

Triggered by: major features, new services, major refactors

The jam itself:
- Top-down layer by layer (API → Service → Data → Utilities)
- AI proposes 2-3 options at each decision point AND actively challenges your choices
- Produces stub code + docstrings + failing unit tests as the code-native design

Outputs two things:
- The stub codebase itself
- A **Flow Guide** — a markdown file with file-by-file summary, reading order, key design decisions made and why (captures the reasoning that doesn't live in stubs)

---

**Skill 2: Issue Architect**

Role: Tech Lead + Scrum Master + PM combined

Inputs:
- Stub codebase from Skill 1
- Flow Guide from Skill 1
- Full design jam conversation transcript (as additional context for reasoning)

Output: Issue tree
- Top-level story (user-facing goal + overall acceptance criteria)
- Sub-issues, where each sub-issue is a **coherent batch of tasks** with tangible output
  - Contains: all tasks in the batch, acceptance criteria, technical guidelines, direct code references
  - Dependency flags: "blocked by sub-issue X" so no agent picks it up prematurely
- Default: markdown files. If Linear MCP present: creates actual Linear issues

---

**Skill 3: Orchestrator + Executor**

- Reads the issue tree
- Sequentially spawns sub-agents (parallel later, worktrees deferred)
- Respects dependency ordering — doesn't pick up a blocked sub-issue
- Each sub-agent: implement → run tests → verify → mark sub-issue done → next
- Handoff note at the end: reading order, flagged decisions, junior-dev-to-senior-dev explanation

---

**One thing I want to nail down before we move on:**

The Flow Guide — who writes it and when? Two options:

**Option A:** The AI writes it progressively during the design jam as decisions get made, you review it at the end of the session before moving to Skill 2.

**Option B:** It's generated at the end of the jam as a summary pass over everything that was decided.

Option A means it's more accurate but adds friction during the jam. Option B is cleaner flow but risks missing nuance.

Which feels right?

---

````turn
ROLE: USER
````

we can do option A and to reduce friction we can use a background subagent so it doesnt block the flow maybe

---

````turn
ROLE: CLAUDE
````

Smart. Background sub-agent running in parallel, silently maintaining the Flow Guide as decisions get made — doesn't interrupt the jam at all.

Though one practical concern: in the context of a skill running in Cursor or Claude Code, "background sub-agent" means the orchestrating agent explicitly spawns a separate context that maintains the doc. The main jam conversation would need to periodically emit structured decision snapshots that the background agent picks up and appends to the Flow Guide. Otherwise the background agent has no way to know what was decided.

So the mechanism would be something like:

- At each layer completion, the jam agent emits a structured **decision checkpoint** (not visible to you, just part of its output protocol)
- Background agent consumes checkpoints → updates Flow Guide
- At end of jam, you do one review pass of the Flow Guide before moving to Skill 2

Does that feel right? Or do you want the checkpoints to be visible to you as well — like a running sidebar of decisions being logged?

Also before we move on — two remaining open questions from Item 1 that we haven't fully closed:

**Explicit out-of-scope triggers** — we said simple bug fixes are out. What about small features, like a new endpoint that's basically CRUD with no real design decisions? Do you want the skill to recognize that and push back with "this doesn't warrant a full jam", or do you always want the human to make that call?

**Entry point** — does the jam always start from scratch, or can it also be invoked on an existing codebase where stubs already exist and you're extending it?

---

````turn
ROLE: USER
````

so in cursor the way it works is that, it can just spawn a sub agent with a prompt and then let it run in the background

---

````turn
ROLE: CLAUDE
````

Got it, so it's just a `run_background_agent(prompt)` call essentially — Cursor handles the parallelism, you don't need to engineer the mechanism. Clean.

So the checkpoint emission is simpler then — jam agent just periodically calls that with a structured summary of what was just decided, background agent appends to Flow Guide. No complex coordination needed.

---

On your two open questions:

**Out-of-scope recognition** — I'd say the skill itself should make the call and push back. Something like a quick triage at the start: "describe what you're building" → if it pattern-matches to simple CRUD / small isolated change → skill responds "this doesn't warrant a full jam, here's a simpler path". Keeps you from having to context-switch into "is this jam-worthy" mode every time.

**Entry point** — this one actually matters a lot for the skill design. Two distinct modes:

- **Greenfield** — no existing code, full jam from scratch
- **Extension** — existing codebase, you're adding a feature or refactoring. The skill needs to first read and understand the existing stubs/structure before designing, otherwise it'll propose things that conflict with what's already there

These probably need different opening prompts in the skill. The extension mode especially needs a "codebase orientation" step before the jam starts.

---

So closing out Item 1 fully, here's the final shape:

**Triggers:** Major features, new services, major refactors. Skill self-triages at start and pushes back if it doesn't warrant a jam.

**Two entry modes:** Greenfield vs Extension (different opening flows)

**Out of scope:** Simple bugs, small isolated CRUD additions

**Three skills confirmed:** Design Jam → Issue Architect → Orchestrator/Executor

Ready to move to Item 2 — Constraint Capture?

---

````turn
ROLE: USER
````

i mean realistically we dont need to do any triage or checks, its at the discretion of the user to use a skill anyway on demand so why add unnecessary friction or guardrails. it should be able to take a user's request, figure out the extension, greenfield whatever as well and not like actively stop the user from using it for simple CRUD, coz I might just want to do it for CRUD as well lol

yeah we can move ahead to contraint capture

---

````turn
ROLE: CLAUDE
````

Fair point, totally agree — the skill should just read the situation and adapt, not gatekeep. Greenfield vs extension it figures out on its own by looking at what's there.

---

**Item 2: Constraint Capture**

This is the very first thing that happens before the jam starts. The skill needs to orient itself. Two sources of constraints:

**A) It reads itself (automatic)**
- Scans the existing codebase structure if present
- Picks up existing patterns, conventions, tech stack, folder structure
- Identifies any existing stubs or tests already written

**B) It asks you (minimal, targeted)**
The key question is — what does it actually need to ask vs. what can it infer? I'd say it should only ask what it genuinely cannot figure out from the codebase. Things like:
- Performance/latency requirements if relevant
- Any hard constraints ("we're not adding any new dependencies")
- External systems it needs to be aware of
- Anything product/business context it can't infer from code

The risk here is it asks too many questions upfront and kills momentum before the jam even starts. So I'd lean toward: it makes its best inference from the codebase, states its assumptions explicitly, and you correct only what's wrong. Rather than a questionnaire.

---

One open question here: what about **cross-cutting constraints** that apply to everything — like your general engineering principles, preferred patterns, things you never do?

These arguably shouldn't be captured per-session at all. They should live in a **persistent context file** — like a `ENGINEERING_PRINCIPLES.md` or cursor rules file — that the skill always reads at the start. So you define it once and it's always in play.

Does that match how you already work, or is this something we'd need to create as part of this workflow?

---

````turn
ROLE: USER
````

yes I do have a separate patterns folder or whatever format in the codebase

---

````turn
ROLE: CLAUDE
````

Perfect, so that's already solved. The skill just reads that at the start as part of its automatic orientation — no need to ask you anything about principles or patterns.

So Constraint Capture is actually pretty lean:

---

**Constraint Capture (automatic, no friction)**

The skill reads on its own:
- Your patterns/principles folder
- Existing codebase structure, conventions, stack
- Any existing stubs or tests if extension mode

Then states its assumptions in a brief oriented summary — something like "here's what I understand about the stack, here's what I think we're building, here's any hard constraints I picked up — correct me if wrong" — and then the jam starts immediately after your confirmation or corrections.

The only time it asks a direct question is if there's something genuinely ambiguous that it cannot infer and that would materially affect the design. Performance requirements, external system integrations, that kind of thing. And even then, just one focused question, not a list.

---

That's Item 2 closed pretty cleanly. Minimal friction, no questionnaire, reads what it can, states assumptions, moves fast.

Ready for Item 3 — The Design Jam Protocol itself? This is the meatiest one — layer sequencing, how it challenges you, option proposals, and what "done" looks like at each layer.

---

````turn
ROLE: USER
````

Yea we can start,

So read my D:\CellStrat\Utilities\agent-skills-collection\.cursor\skills folder where I typically put in my existing agent skill collection. So I typically used to use a combination of superpowers/brainstorming and senior-software-engineer prior to this new workflow or more like currently. Take them as reference and get the points relevant for our workflow here first

---

````turn
ROLE: CLAUDE
````

[Claude read the following skill files from the filesystem:]

- `senior-software-engineer/SKILL.md`
- `superpowers/brainstorming/SKILL.md`
- `superpowers/writing-plans/SKILL.md`
- `superpowers/subagent-driven-development/SKILL.md`
- `superpowers/executing-plans/SKILL.md`
- `superpowers/test-driven-development/SKILL.md`
- `superpowers/fast-subagent-driven-development/SKILL.md`
- `superpowers/dispatching-parallel-agents/SKILL.md`

---

Okay, this is gold. You already have a sophisticated skill ecosystem. Here's what's directly relevant to extract for our new workflow:

---

**What already exists that we should absorb or reference, not rebuild:**

**From `senior-software-engineer`:**
- The push-back lenses (product, ops, scale, simplicity, cross-cutting) — bring these directly into the Design Jam skill's challenge protocol
- The "one thread at a time" conversational discipline
- The running notes pattern → this becomes our Flow Guide

**From `brainstorming`:**
- The hard gate (no implementation until design approved) — we want this but lighter, not a formal approval ceremony
- 2-3 options with trade-offs and a recommendation — carry this forward

**From `writing-plans`:**
- The plan doc header format (Goal, Architecture, Tech Stack) — useful for our Issue Architect output
- Bite-sized task granularity — directly maps to our sub-issue structure

**From `subagent-driven-development` + `fast-subagent-driven-development`:**
- The spec compliance review → code quality review two-stage loop — bring this into Skill 3's executor
- The bail-out rule when too many issues — smart, keep it
- The implementer prompt / spec-reviewer / code-quality-reviewer template pattern — our Skill 3 executors follow the same pattern

**From `dispatching-parallel-agents`:**
- The independent domain identification logic — our Issue Architect (Skill 2) uses this exact thinking when deciding what can be parallelized vs. sequenced
- The focused agent prompt structure — directly applies to how our Orchestrator writes sub-agent prompts

**From `test-driven-development`:**
- The Iron Law (no production code without a failing test first) — the Design Jam's stub + failing test output enforces this structurally before Phase 2 even starts
- The rationalizations table — useful to embed in the executor skill

---

**What's genuinely new in your workflow vs. what exists:**

The existing skills go: `brainstorming → writing-plans → subagent-driven-development`. Yours replaces that chain with something fundamentally different:

- **Design lives in code** (stubs + tests) not in prose design docs — this is new
- **Failing tests as acceptance criteria defined before planning** — the existing TDD skill does this per-task, yours does it at the whole-system design level before any implementation begins
- **Flow Guide as background-agent-maintained living artifact** — new
- **Issue Architect as a distinct "translation" step** between design and execution — new, the existing chain goes directly from writing-plans to execution
- **Linear MCP as first-class output** — new

---

So concretely for Item 3 (Design Jam Protocol), we're building on the `senior-software-engineer` jam style + TDD iron law, but adding:
- Structured layer sequencing (API → Service → Data → Utilities)
- Background Flow Guide agent
- Stub + failing test as the output format per layer
- Explicit challenge protocol at each decision point

Ready to go deep on Item 3?

---

````turn
ROLE: USER
````

Alright. So my main issues with this approach with the superpowers were that, you know, um, the design doc is fine, but it's too verbose and everything that at this point, it just becomes difficult for me to review it, and the same goes with the plan. My approach with, you know, designing as we are going and stuff and getting... being more involved in the step process, the API flow process, and the unit testing is is for me to become more involved than what superpowers let's me be. And, yeah, the executions are fine. Subvision driven is good, but here's the thing. This of each interim deployment is so slow. It, like, takes hours and hours to really get something really useful. I mean, so... yeah. And it's, like, unnecessary, like, that comp... that level of complexity unnecessary. It needs to be more smarter than that. So, yeah, that's why the spec review compliance and all these things, you know, takes a lot more time than it needs to be taken because any of you are gonna do your PR review and everything. So might as well skip those sort of things. And... yeah. And the end plus, I also do want this junior dev to senior dev sort of hand off note where it's, like, a reading order of how to review those files because I just don't wanna approve all of the... I mean, after the coding is done, I don't wanna, you know, let... they just be committed as this. Firstly, I wanna stop to this... stop the automatic commit, but I want to be able to, you know, go through the modified code in a way that is tractable for me as a human to go through. Yeah. So... yeah. Yeah. We can go dive deeper into the... into this process. And the reason I also shared this is another reason is that there are a lot of good things, of course. It's just that the way that it's structured is not something that I am comfortable with, really. I wanna be more involved into the process in a humanly tractable way. The brainstorming is good but after that it becomes a difficult thing to review and keep track of

---

````turn
ROLE: CLAUDE
````

This is the clearest articulation of the core problem yet. Let me reflect it back precisely:

---

**The fundamental complaint with superpowers:**

- Design doc → too verbose, hard to review
- Plan → same problem, too much prose to track
- Spec compliance + code quality review loops → unnecessary overhead since *you're* doing the PR review anyway, the agent reviewing itself is redundant ceremony
- Auto-commits → you lose control of what lands
- After execution you have no tractable way to walk through what changed
- The whole thing moves slowly and you feel like a spectator, not a participant

**What you actually want:**

- Be deeply involved during design (that's the jam)
- Have a tractable human review path after execution — not "approve everything blindly" but a guided reading order + flagged decision points
- Skip the agent-reviewing-itself loops since your eyes are the final gate anyway
- No auto-commits — you commit when you're satisfied

---

**This reframes Skill 3 significantly:**

The executor doesn't need a spec reviewer or code quality reviewer subagent. What it needs instead is:

- Implement → run tests → if green move on, if consistently failing flag it
- No self-review ceremony
- At the end, produce the **junior dev handoff note** with:
  - Reading order of modified files
  - Flagged decisions with "I did X, is this what you wanted?"
  - Anything non-obvious or uncertain
- Then **stop and wait** — no commits until you've reviewed and said go

The handoff note IS the review mechanism. That's actually smarter than agent-self-review because it leverages the right reviewer — you.

---

**This also reframes the overall philosophy:**

The superpowers chain optimizes for the agent being autonomous and self-correcting. Your workflow optimizes for **you staying in the loop at the right moments** — deep during design, lightweight during execution, deliberate at review/commit.

Three control points, not constant oversight:
1. **Design Jam** — you're fully in it
2. **Execution** — agent runs, you're hands off
3. **Handoff review** — you review tractably, then commit

---

Ready to go deep on Item 3 with this philosophy fully in mind?

---

````turn
ROLE: USER
````

yes

---

````turn
ROLE: CLAUDE
````

Let's dig into the Design Jam Protocol. Here's what we need to nail down:

1. How the jam opens (orientation + constraint capture)
2. The layer sequence and transition rules
3. The challenge + options protocol
4. The stub + docstring + failing test format
5. The background Flow Guide agent mechanics
6. What "done" looks like for the whole jam

Let me start with a specific question on **layer sequencing** since that's the structural backbone:

You said API → Service → Data → Utilities. But in practice a feature might not touch all layers, or might have multiple parallel branches at the same layer (e.g. two different services).

So two things to nail down:

**A) Layer skipping** — does the jam always walk all four layers, or does it assess upfront which layers this feature actually touches and only go through those? My instinct is the latter — assess first, then only traverse relevant layers. But that assessment itself could miss something.

**B) Branching** — when one API endpoint fans out into multiple services, do you go wide first (map all the branches at service layer) then deep (go into each branch fully), or do you go deep on one branch at a time?

Wide-first gives you a better map but might feel scattered. Deep-first feels more natural conversationally but risks the branches being inconsistent with each other.

What's your instinct here?

---

````turn
ROLE: USER
````

Yeah. So, um, yeah. Of course. I mean, this example of going layer by layer is more so in practice, not really about the layer, but rather about what are all the files we are gonna touch. Right? What are all the classes we're gonna create, what are all the functions we're gonna create. They can span any layer if they could skip layers. If they could go to some panel layer, they could do anything. That's not the point. The point is that, uh, we walk as if we are doing the implementation. But from a top down approach, um, we are going from intent to execution or, like, from here. I don't know what the word is, but you... I hope you get the point. And, yeah, and, of course, in branching also, I'm fine with going white, really. So I think it should be more of... so, like, recommendation from the agent if we should go wide or deep first depending on the task at hand. And, of course, we create different rules. Like, uh, we bake in this knowledge in the skill, like, when we should go wide and when we should go deep.

---

````turn
ROLE: CLAUDE
````

Got it. So the "layers" framing was just a mental model — what you actually want is **intent-to-execution traversal**. You're walking the call graph essentially. Starting from the entry point (what triggers this feature — an API call, an event, a cron, whatever) and following the execution path all the way down, touching whatever files and functions that path actually visits. Layers are just where those files happen to live.

So the jam is really: **"if I were implementing this right now, what would I touch first, then next, then next"** — but instead of writing code, you're defining the shape of each thing you'd touch.

---

**On wide vs deep — here's my proposed baked-in rules:**

**Go wide first when:**
- The feature has multiple independent entry points (e.g. REST + webhook + cron all triggering related logic)
- The branching happens early in the call graph and the branches don't share much
- You need to spot cross-cutting concerns before going deep (auth, multi-tenancy, shared utilities)
- It's a refactor — you need the full map before touching anything

**Go deep first when:**
- There's one clear critical path and branches are edge cases
- The feature is a single flow end-to-end (e.g. one API endpoint → one service → one DB operation)
- Dependencies between branches are tight (deep on one informs how you design the next)
- The feature is exploratory and you're not sure what branches even exist yet

**The agent calls this explicitly** at the start after orientation — "this looks like a wide-first situation because X, going deep first because Y" — and you can override it.

---

Does that feel right? And one follow-up: when the agent is traversing the call graph and discovers something unexpected mid-jam — like a function that needs a shared utility that doesn't exist yet — does it pause and surface that, or does it just branch into designing that utility inline and flag it in the Flow Guide?

---

````turn
ROLE: USER
````

Weiner depends. Right? If a shared utility... I think it should be part of our designing. I mean, if it doesn't exist yet, of course, it should be part of the design, and it should, of course, also check what the existing utilities are and if any of those existing things fit in or maybe there's a way to, you know, cleanly refactor this and all these things. So that's also part of it. Yeah. So it's it's it's more of a case or a case to case basis, right, with... where, like, there's no one fair... one solution fit all case. Like, if it is a utility, you know, which is only... if we have to extract it is... or maybe we don't necessarily have a use case for it to be a shared functionality. We can keep it in past part of the flow, but if it does need to become shared, we can keep it shared as well. I mean, it depends, I guess. I mean, of course, you should pause and surface that, um, and think about that. But act... but pausing and surfacing, I'm not sure what that really means because as part of the call stack, it's not even, like, it's not essentially just part of the jam. Right? But, yeah, of course. Yeah. Uh, it's a a judgment call needs to be taken. I mean, as a human, I'm also there to, you know, see that, okay, this logic, we could probably be a bit... could become a utility, so I can also flag that, of course. But, yeah, the AI should also have that judgment. from... because the AI is not just a design partner. Right? It's about being a senior engineer and, you know, being deliberate and intentional about every line of code and every functionality that's out there.

---

````turn
ROLE: CLAUDE
````

Exactly. It's not a special case to handle — it's just part of being a good senior engineer in the jam. A senior engineer doesn't pause and formally declare "I have discovered a shared utility situation." They just... think about it naturally as part of the design conversation. Check what exists, assess whether it warrants extraction, recommend, move on.

So the rule baked into the skill is simply: **the AI operates with senior engineer judgment throughout**. That means:

- Checks existing code before proposing anything new
- Notices when something could/should be shared vs kept local
- Recommends with reasoning, doesn't just ask "what do you want to do?"
- You can override, redirect, or flag things yourself too — it's a conversation

No special handling needed. It's just good engineering instinct applied continuously.

---

Now let me move to the **challenge + options protocol** — this is the piece we said was missing from the existing superpowers jam.

The risk we identified earlier: the jam moves fast, you rubber-stamp AI proposals, and the design is AI-led without you realizing it.

My proposal for how the skill handles this:

**Two distinct modes of AI output during the jam:**

**Proposing** — "here's what I think this function should do and why, here's an alternative if you want X instead" — your job is to react, redirect, or approve

**Challenging** — the AI actively pokes at something you just said or agreed to. "Wait — you said X, but what happens when Y? Have you thought about Z edge case?" — not proposing a solution, just making sure you've thought it through

The skill should rotate between these naturally. Propose when moving forward, challenge when something feels underexamined. And specifically, the skill should **always challenge before moving to the next layer/branch** — a lightweight "are we sure about this before we go deeper?" gate.

The challenge lenses pulled from your senior-software-engineer skill that are relevant here:
- Does this function actually need to exist or are we over-engineering?
- What's the failure mode if this returns null / throws / times out?
- Are we creating a dependency we'll regret?
- Does this fight existing patterns in the codebase?

**One thing I want your input on:** how aggressive should the challenges be? The senior-software-engineer skill is quite assertive — "I'd push back on that because..." Your jam is more collaborative and fast-moving. Do you want the same assertiveness, or a lighter touch where it surfaces the question and lets you decide without a strong opinion?

---

````turn
ROLE: USER
````

Yeah. I think I think, again, that is dynamically decided. Right? If it is a very tiny decision, you know, it could be a lighter touch. But if it is something like a bigger decision, it could be assertive in nature as well. Right? So it depends. Like, there are different severity levels to when something should be more pushed back strongly versus something that should be pushed back lightly or casually. But... yeah.

---

````turn
ROLE: CLAUDE
````

Makes sense. Severity-proportional challenge. Small decisions get a light nudge, architectural decisions get a hard stop and a strong opinion.

We can bake in rough severity tiers:

**Light touch** — "just flagging this, happy to move on" — for things like naming choices, minor implementation details, which utility to use

**Moderate** — surfaces the concern, gives a recommendation, waits for your call — for things like function boundary decisions, data format choices, where something lives

**Hard stop** — assertive, doesn't move forward until resolved — for things like architectural decisions that are hard to reverse, anything that creates cross-cutting impact, anything that fights existing patterns significantly, failure modes that could cascade

The skill judges severity based on: reversibility, blast radius, and how deep in the call graph the decision is (earlier decisions have more downstream impact).

---

Okay I think we have enough on the challenge protocol. Let me now move to the **stub + docstring + failing test format** — this is the actual output artifact of the jam per function.

My starting proposal for what each stub looks like:

```python
def process_appointment_booking(patient_id: str, slot_id: str) -> BookingResult:
    """
    Books an appointment slot for a patient.
    
    Behaviour:
    - Validates slot is still available before booking
    - Marks slot as held (soft lock) before writing booking record
    - Sends confirmation event to notification service
    - Returns BookingResult with status and booking_id
    
    Failure modes:
    - Raises SlotUnavailableError if slot taken between check and hold
    - Raises PatientNotFoundError if patient_id invalid
    - If notification fails, booking still succeeds (fire and forget)
    
    Dependencies:
    - SlotRepository.hold_slot()
    - BookingRepository.create()
    - NotificationService.send_confirmation()
    """
    pass
```

And the paired failing test:

```python
def test_process_appointment_booking_slot_unavailable():
    """Slot taken between availability check and hold raises SlotUnavailableError"""
    # arrange
    slot_repo = MockSlotRepository(slot_state="taken_on_hold")
    
    # act + assert
    with pytest.raises(SlotUnavailableError):
        process_appointment_booking("patient_123", "slot_456")
```

A few things to nail down here:

**A)** Should every function get a full set of tests covering all failure modes during the jam, or just the tests that represent the most important acceptance criteria — leaving edge case tests to the executor agent to fill in?

**B)** The docstring format — is this level of detail right, or too verbose? You said the design doc in superpowers was too verbose. Does the same complaint apply here or is this acceptable since it's in code not a separate doc?

---

````turn
ROLE: USER
````

Okay. Realistically, I think, um, the base acceptance criteria should always be done anyway in the test. The edge cases, I think it should be... it dep... it depends, actually. For example, sometimes I would want to nail down the edge cases and how they're handled because it's a big piece of the puzzle. Right? It's big piece of the problem. But sometimes if there are, like, a... it's a very small utility function, which which is fine if we don't really look at the edge cases right away, that's also fine. But I would still leave at least some comments during the design session for these edge cases here. And if not full tests, so that when the executor agent takes... picks it up, it actually acts those edge cases as well and fills them in additionally. So it's like, yeah, it's both. Okay. This case is both. Like, some... for some bigger important things, we do all edge cases as well as just the acceptance right here. For some smaller little things, we just do acceptance right here and come back to the edge cases as part of the execution. And the doc string is good. Um, I mean, this is his part of the code, and so I think this is fine for doc string. I don't have a big problem, but... yeah. Though, realistically, uh, these doc strings would essentially turn out to be proper function doc strings during execution. So that is something to be noted. So even if they are, um, like, design, like, doc strings in the beginning, they will be translated. So I think these doc strings can also be stored in the flow guide or the design guide that we will be creating additionally as part of the process.

---

````turn
ROLE: CLAUDE
````

Good. So the format is:

**Every function gets:**
- Full docstring (behaviour, failure modes, dependencies)
- Base acceptance criteria tests — always

**Edge cases — severity dependent:**
- Important/complex functions → full edge case tests during the jam
- Smaller utilities → commented edge case stubs, written in plain language so the executor knows what to fill in

Like:
```python
def process_appointment_booking(...):
    """..."""
    pass

# TODO: executor to add edge case tests for:
# - concurrent booking attempts on same slot (race condition)
# - patient with existing conflicting booking
# - slot hold timeout before booking record written
```

**And on the Flow Guide** — good catch. The docstrings serve double duty:
- In the stub file → become real function docstrings after execution rewrites the function
- In the Flow Guide → captured as the canonical behaviour description for that function, so Skill 2 (Issue Architect) has a clean reference without having to parse code

So the Flow Guide entry per function is essentially the docstring pulled out into a readable index. Reading order + function behaviour summaries + key design decisions. Clean separation — code has the stubs and tests, Flow Guide has the human-readable map.

---

That's the stub format nailed. One more thing to close out Item 3 — **what does "done" look like for the whole jam?**

My proposal: the jam is done when you've walked the entire call graph, every file that will be touched has been identified, every function in those files has a stub + docstring + at minimum base acceptance tests, and the Flow Guide has a complete entry for each.

But there's a practical question: **how do you and the agent both know the call graph is complete?** It's easy to miss a branch mid-jam and only realize it during execution when the executor hits something undesigned.

Two options:

**A)** At the end of the jam, the agent does an explicit "completeness check" — reads back the full map, checks for any dangling dependencies (a function calls something that hasn't been stubbed), surfaces any branches that were mentioned but not fully walked

**B)** The Flow Guide itself is the completeness signal — if every dependency listed in every docstring has a corresponding stub entry, the graph is closed. The background agent maintains this and flags open ends in real time during the jam

Option B is more elegant but requires the background agent to be tracking dependency closure actively, not just logging decisions. Is that the right level of intelligence for the background agent, or too much?

---

````turn
ROLE: USER
````

I mean, let's not depend too much on the background agent. So, yeah, I think let's let's do option a. I mean, the background agent is just a utility so that we don't, uh, pollute the context with those tool calls for, you know, writing the file and all those things. So just that. So... yeah. I mean, it's like, probably, we don't even need a background agent. Actually, we don't need a background agent. I think we can just write it in line. It's just a simple file writing to the console. Should be okay along... so while while, anyway, we are writing these stuffs and unit tests, might as well just write them along in the file as well. Right? I mean... so why do we need a separate background agent, I guess? Yeah.

---

````turn
ROLE: CLAUDE
````

Yeah, you're right. The background agent was over-engineered for what it needs to do. Writing to a file is just a tool call — do it inline as each function gets designed, no separate agent needed. The context pollution concern is minimal compared to the coordination overhead of a background agent.

So the Flow Guide just gets written incrementally during the jam — every time a function is stubbed and its docstring is written, the agent also writes that entry to the Flow Guide file. Same moment, same context, one tool call. Simple.

---

So closing out Item 3 fully:

**Design Jam Protocol — complete picture:**

**Opening:**
- Reads patterns folder + existing codebase automatically
- States assumptions briefly, you correct if wrong
- Identifies entry point(s) for the feature
- Calls wide vs deep first with reasoning, you can override

**During the jam:**
- Traverses the call graph from intent to execution
- At each function: proposes shape, challenges with severity-proportional pushback, lands on stub + docstring + tests
- Base acceptance tests always, edge cases fully written or commented depending on importance
- Writes stub to code file + entry to Flow Guide inline as each function is done
- Senior engineer judgment throughout — checks existing code, flags extraction opportunities, notices cross-cutting concerns

**Closing:**
- Explicit completeness check — reads back full map, finds dangling dependencies, surfaces unwalked branches
- You confirm the map is complete
- Flow Guide is finalized

**Output:**
- Stub codebase (stubs + docstrings + failing tests)
- Flow Guide (file index + function behaviour summaries + key design decisions)

---

That's Item 3 done. Ready to move to Item 4 — the Plan File Schema? This is the bridge between the jam output and the Issue Architect. The key question there is exactly what format Skill 2 consumes and what it produces.

---

````turn
ROLE: USER
````

yes

---

````turn
ROLE: CLAUDE
````

Okay so the Plan File Schema is really about what Skill 2 (Issue Architect) takes as input and what it produces as output. Let me frame the two sides:

**Inputs to Skill 2:**
- Stub codebase (stubs + docstrings + failing tests)
- Flow Guide
- Full jam conversation transcript (for reasoning context)

**Output — the Issue Tree:**
- Top level story
- Sub-issues (coherent batches)
- Each sub-issue has tasks, acceptance criteria, code references, dependency flags

The key design question here is **how does Skill 2 actually read the stub codebase?** Two options:

**A)** It reads the actual stub files directly — parses the docstrings and tests to derive the issue structure

**B)** It reads the Flow Guide primarily and uses the stub files only for reference when it needs detail

My instinct is B. The Flow Guide was specifically built to be the human-readable map — it's already organized the way a tech lead would think about the work. The stubs are the ground truth for exact function signatures and test cases. So Flow Guide drives the structure, stubs provide the detail.

But before we go further — I want to nail down what the **Flow Guide's actual format** looks like, because Skill 2's entire output quality depends on how well structured it is.

My proposal:

```markdown
# Flow Guide — [Feature Name]
Generated: [date]

## Entry Points
- `POST /appointments/book` → `AppointmentController.book()`

## File Map
### src/controllers/appointment_controller.py
**Purpose:** HTTP layer for appointment booking flow
**Functions:**
- `book(request)` — validates request, delegates to AppointmentService.process_booking()

### src/services/appointment_service.py
**Purpose:** Core booking business logic
**Functions:**
- `process_booking(patient_id, slot_id)` — orchestrates slot hold, booking creation, notification
- `validate_slot_availability(slot_id)` — checks slot state before hold attempt

## Key Design Decisions
- Soft lock pattern chosen over DB transaction lock — reason: [x]
- Notification is fire-and-forget — reason: [x]

## Open Edge Cases (executor to handle)
- Concurrent booking race condition on same slot
- Patient with conflicting existing booking
```

Two questions before we go deeper:

**A)** Does this structure feel right as the primary artifact Skill 2 reads? Or is there something missing that would make the Issue Architect's job harder?

**B)** The "Key Design Decisions" section — should this also capture the *rejected* approaches and why? So the executor agent doesn't re-propose something you already ruled out during the jam?

---

````turn
ROLE: USER
````

yes flow guides purpose is to sorta be the index such that the AI can directly reads the files if needed.
So I agree with your format pretty much just a nuance, the flow guide could potentially be more detailed than the docstrings maybe.

[file ref]
summary or design note
function name - same behaviour docstring kinda thing (infact we can consider putting the actual doctstring minimal and being more dertailed here instead of long docstrings in the files for now. 

Idk let's discuss if you have any concerns about this. So its like flow guide essentially becomes a new design doc but because we are writing to it as we go instead of at one shot like earlier, its human readable more and our general goal is to be detailed but less verbose, as if we are jotting down quick notes. We don't wanna miss anything but we wanna use less words to express the same things as this flow guide (or we can call it the design doc itself to be honest) is essentially like running notes really in its tone.

yeah so I think what we could do is the main design doc itself can around the main things, any rejected approaches or reasoning can be offloaded to an appendix section and the main body just says things like other approaches rejected are in Appendix 1.2 or something like that

_also top level story is actually the parent issue, just a tiny note_

---

````turn
ROLE: CLAUDE
````

Good nuances. Let me consolidate:

**On docstring vs Flow Guide detail:**

Keep function docstrings minimal in the actual code — just enough to be a real docstring. The Flow Guide carries the richer design note. So:

In code:
```python
def process_booking(patient_id: str, slot_id: str) -> BookingResult:
    """Books a slot for a patient. Soft locks before writing. Notification is fire-and-forget."""
    pass
```

In Flow Guide:
```markdown
### src/services/appointment_service.py
Owns all booking business logic. Nothing else should touch slot state directly.

- `process_booking(patient_id, slot_id)` — orchestrates the full booking sequence. Holds slot first, then writes booking record, then fires notification. If notification fails booking still succeeds. SlotUnavailableError if race condition on hold.
- `validate_slot_availability(slot_id)` — pre-check before attempting hold. Not a guarantee — slot can still be taken between this and hold attempt.
```

Detailed but note-like. No prose padding. Just what someone needs to understand the file without opening it, with enough to know when to open it.

---

**On structure:**

```markdown
# Design Doc — [Feature Name]

## Entry Points
## File Map
## Key Design Decisions
## Open Edge Cases

## Appendix
### A1 — Rejected Approaches
### A2 — [anything else that clutters main body]
```

Main body references appendix inline — "soft lock chosen over DB transaction, see A1.1" — reader only goes there if they care about the reasoning.

---

**On parent issue:**

Noted — top level = parent issue, not "story" in our terminology going forward.

---

One thing I want to flag before we move to the Issue Architect output format: **who writes the parent issue?**

The parent issue is essentially the feature intent + overall acceptance criteria. That context lives most clearly in the jam conversation — it's what you stated at the start before the traversal began. The Design Doc captures the *how*, but the parent issue needs to capture the *what and why* at a product level.

So either:
- **Skill 2 derives it** from the jam transcript + Design Doc opening
- **You write it** as a one-liner at the start of the jam that gets captured verbatim as the parent issue title + description

My instinct is the latter — you state intent at the start of the jam, that becomes the parent issue. Skill 2 just formalizes it. Cleaner than having the AI infer product intent from a technical conversation.

Does that feel right?

---

````turn
ROLE: USER
````

yeah alright

---

````turn
ROLE: CLAUDE
````

Good. So the parent issue is anchored to your stated intent at the jam opening — Skill 2 just formalizes it into the right structure.

---

Now the output side of Skill 2 — the actual issue structure. Let me propose the format for a sub-issue since that's the most detailed piece:

```markdown
## Sub-Issue 2: Booking Service Layer
**Depends on:** Sub-issue 1 (Controller stubs must exist)
**Blocks:** Sub-issue 3 (Notification service needs BookingResult type)

### Tasks
- Implement `process_booking()` per design doc
- Implement `validate_slot_availability()` per design doc
- Fill in edge case tests marked TODO in stubs

### Acceptance Criteria
- All base acceptance tests passing
- SlotUnavailableError raised on race condition
- Notification failure does not fail booking

### Code References
- `src/services/appointment_service.py` — primary file
- `src/repositories/slot_repository.py` — dependency, must exist first
- Design Doc §File Map — appointment_service section

### Technical Guidelines
- Soft lock pattern, not DB transaction lock (see Design Doc A1.1)
- No direct slot state mutation outside this service
```

A few things to nail down:

**A)** The dependency flagging — "depends on" and "blocks" — is this enough for the orchestrator to figure out execution order, or does it need something more explicit like a dependency graph or batch groupings already decided by Skill 2?

My instinct is Skill 2 should go one step further and explicitly declare the batches — "Batch 1: sub-issues 1, 2 (parallel). Batch 2: sub-issue 3 (after batch 1)." Rather than leaving the orchestrator to re-derive it.

**B)** Code references — should Skill 2 include actual line number references to the stubs, or just file level? Line numbers feel precise but will immediately go stale once the executor starts writing real code.

What's your instinct on both?

---

````turn
ROLE: USER
````

on A, yes we can be explicit. We can mention this dependency info like parallel after batch 1 and so forth as part of the main parent issue.

on B, yeah no need of line numbers, I am guessing AI is smart enough to figure out without being too specific

---

````turn
ROLE: CLAUDE
````

Clean. So:

**Dependency/batch map lives on the parent issue** — one place to see the full execution order. Sub-issues just have their own "depends on / blocks" for reference, but the orchestrator reads the batch plan from the parent.

**Code references are file-level only** — the executor reads the stub file, understands the design doc entry for that file, figures out the rest itself.

---

So the parent issue looks something like:

```markdown
# Parent Issue: Appointment Booking Feature

## Intent
[Your stated intent from jam opening verbatim + brief formalization]

## Overall Acceptance Criteria
- Full booking flow works end to end
- All base acceptance tests passing across all layers
- Notification failure does not break booking

## Execution Plan
Batch 1 (parallel): Sub-issue 1, Sub-issue 2
Batch 2 (after Batch 1): Sub-issue 3
Batch 3 (after Batch 2): Sub-issue 4

## References
- Design Doc: `docs/design/[feature].md`
- Entry point: `POST /appointments/book`
```

And each sub-issue is self-contained with tasks, acceptance criteria, code references, technical guidelines, and its depends-on/blocks pointers.

---

That closes Item 4. The full bridge between jam and execution is:

- Design Doc (running notes format, appendix for rejected approaches)
- Stub codebase (minimal docstrings, base tests, TODO edge case comments)
- Parent issue (intent, overall AC, batch execution plan)
- Sub-issues (coherent task batches, code references, dependency pointers)

---

Ready for Item 5 — the Implementation Protocol? This is where we design exactly how the executor agent consumes all of this and runs. Given what you said earlier — no spec review loops, no auto-commits, junior dev handoff note at the end — this one should actually be leaner to design than the others.

---

````turn
ROLE: USER
````

yeah

---

````turn
ROLE: CLAUDE
````

Okay. The executor is simpler by design. Let me lay out the core loop first and then we'll poke at the details:

**Core loop per sub-issue:**
1. Read parent issue for context + batch plan
2. Read sub-issue — tasks, AC, code references, technical guidelines
3. Read referenced files from Design Doc + stubs
4. Implement — write real code replacing stubs
5. Run tests — base acceptance tests must pass, fill in TODO edge case tests as it goes
6. If tests pass → mark sub-issue done, move to next
7. If tests consistently failing → flag for you, stop, don't guess

That's it. No self-review, no spec compliance agent, no code quality agent. Just implement, test, flag if stuck.

---

Three things to nail down:

**A) "Consistently failing" threshold** — how many attempts before the executor flags and stops rather than keep trying? My instinct is two genuine attempts. First attempt it tries to fix itself, second attempt if still failing it stops and surfaces the specific failure with context. It shouldn't spiral.

**B) The handoff note** — this is produced once at the end of all batches, not per sub-issue. Format I'm proposing:

```markdown
# Handoff Note — [Feature Name]

## Reading Order
1. `src/controllers/appointment_controller.py` — start here, entry point
2. `src/services/appointment_service.py` — core logic, read second
3. `src/repositories/slot_repository.py` — dependency, skim for interface

## Decisions Made
- Extracted slot validation into separate private method 
  — felt cleaner than inline, assume this is fine?
- Used existing `BaseRepository` pattern for new repository
  — matched existing conventions, flagging in case you wanted something different

## Flags
- `process_booking()` retry logic — went with simple retry count, 
  no backoff. Is this acceptable or do you want exponential?
- Edge case: concurrent booking test is passing but the mock 
  feels fragile — worth a look
```

**C) Commits** — you said no auto-commits. So the executor stages changes but never commits. You review the handoff note, walk the reading order, then commit yourself when satisfied. The executor should explicitly say "changes staged, not committed — review handoff note before committing."

---

Does the core loop and these three feel right, or anything to adjust?

---

````turn
ROLE: USER
````

one change, I do want the handoff at every batch as default behaviour but allow to have an auto mode where it does write the hand off for every batch but doesnt stop, it continues, the handoff note is a per exeuction batch thingy in a way also, we can call it implementation notes or somerthing maybe instead of hand off notes. Also besides that, we do want a version which uses subagents as well efficiently like strategically using fast models for subagents (like composer 2 fast)

---

````turn
ROLE: CLAUDE
````

Good changes. Let me reflect:

**Implementation Notes (per batch):**
- Default mode: writes implementation notes after each batch, **stops and waits** for your review before continuing to next batch
- Auto mode: writes implementation notes after each batch, **continues automatically** to next batch without waiting
- At the very end regardless of mode: a final consolidated implementation note across all batches

This is actually a better control structure than what superpowers had — you get natural review checkpoints at batch boundaries rather than either full autonomy or per-task interruption.

---

**On subagents with fast models:**

This is smart. The orchestrator is the expensive brain, the executors doing the actual implementation work can be leaner. Proposed split:

**Orchestrator (full model):**
- Reads parent issue + full Design Doc
- Plans batch execution
- Writes implementation notes
- Makes judgment calls when executor flags something
- Handles anything requiring full context

**Executor subagents (fast model — claude-haiku or equivalent):**
- Gets a focused prompt: one sub-issue, relevant file references, technical guidelines
- Implements, runs tests, reports back
- Narrow context, narrow task — fast model is sufficient
- If it hits something beyond its judgment → escalates to orchestrator, doesn't guess

**Reviewer subagents (fast model):**
- Actually wait — you said no spec/quality review loops. So no reviewer subagents.
- The only "review" is you via the implementation notes.

So the subagent structure is just: **orchestrator spawns executor per sub-issue within a batch**, executors run, report back, orchestrator consolidates into implementation notes.

---

One thing to nail down: **how does the orchestrator spawn executors in Cursor specifically?** In Cursor composer, spawning a subagent means opening a new composer context with a crafted prompt. The orchestrator would need to:

1. Construct the executor prompt (sub-issue + relevant context)
2. Spawn it
3. Wait for result
4. Process result + write implementation notes

Is this how you're thinking about it mechanically, or did you have a different model in mind for how orchestrator → executor communication works in Cursor?

---

````turn
ROLE: USER
````

na na we are on cursor version 3 now, it can spawn subagents normally, just having our orchestrator skill file with instructions like spawn subagents (with composer 2 fast model) for implementation tasks with structured prompts for the subagents to work on, and doing things like flagging etc so the main orchestrator can make decisions or whatever. So the subagents are the hands while the orchestrator is the brain

---

````turn
ROLE: CLAUDE
````

Perfect, clean mental model. Orchestrator = brain (full model, stays in control), executor subagents = hands (fast model, narrow focused tasks).

So the orchestrator skill just needs to know:
- Spawn subagent with fast model for implementation tasks
- Give it a structured prompt: sub-issue + relevant file refs + technical guidelines + "report back with: what you did, what tests pass, anything uncertain"
- Receive result, make decisions, write implementation notes
- If subagent flags something → orchestrator decides, doesn't re-spawn blindly

The structured prompt the orchestrator writes for each subagent is actually a mini-skill in itself — it needs to be tight enough that a fast model can execute without needing full context. That's essentially the executor's "skill" baked into the prompt rather than a separate skill file.

---

So closing out Item 5:

**Implementation Protocol — complete picture:**

**Orchestrator:**
- Reads parent issue, Design Doc, full batch plan
- Spawns fast model subagents per sub-issue within a batch
- Receives results, consolidates, writes implementation notes per batch
- Default mode: stops after each batch for your review
- Auto mode: continues through batches, consolidated note at end
- Makes judgment calls when subagent flags something
- Never auto-commits — stages only, explicitly tells you to review before committing

**Executor subagents (fast model):**
- Narrow prompt: one sub-issue, relevant files, technical guidelines
- Implement → run tests → report back
- Two attempts max if failing, then escalates to orchestrator
- Fills in TODO edge case tests as it goes
- Reports: what was done, test results, anything uncertain

**Implementation Notes (per batch):**
- Reading order of modified files
- Decisions made with "is this fine?" flagging
- Anything uncertain or non-obvious
- Escalated flags from subagents

---

That's Item 5 done. Items 6 and 7 (Handoff Note Format and Linear MCP) are actually mostly resolved already through what we've discussed. Want to do a quick pass on both to close them out, then we can step back and look at the full picture before thinking about actually writing the skills?

---

````turn
ROLE: USER
````

yeah

---

````turn
ROLE: CLAUDE
````

**Item 6 — Implementation Notes Format:**

Already mostly defined. Just nailing the schema:

```markdown
# Implementation Notes — Batch [N]
Date: [date]

## What Was Done
- Sub-issue 1: [one line summary]
- Sub-issue 2: [one line summary]

## Reading Order
1. `path/to/file.py` — why to read this first
2. `path/to/file.py` — what to look for here

## Decisions Made
- [decision] — [one line reasoning] — okay?
- [decision] — [one line reasoning] — okay?

## Flags
- [specific thing] — [why flagging] — [what you need to decide]

## Test Status
- Sub-issue 1: X/Y tests passing
- Sub-issue 2: X/Y tests passing
- Failing: [specific test] — [why it's failing if known]

## Staged Files
[list of files with changes staged, not committed]
```

Final consolidated note at end is same format but across all batches with a "ready for your review and commit" close.

---

**Item 7 — Linear MCP Integration:**

Also mostly resolved. Just the mechanics:

- Skill 2 (Issue Architect) detects if Linear MCP is present
- If yes: creates actual Linear issues with the same structure — parent issue + sub-issues, dependency flags, batch plan in parent description
- If no: writes markdown files to `docs/issues/[feature]/` with same structure
- Skill 3 (Orchestrator) checks Linear for sub-issue status if MCP present, marks done after each batch completes
- Markdown fallback: orchestrator updates a status field in the markdown file

One nuance — when Linear MCP is present, the orchestrator should also update sub-issue status in real time as subagents complete them, not just at batch end. So your Linear board actually reflects live progress.

---

**Full picture — all 7 items closed:**

**Skill 1: Design Jam**
- Auto-orients from codebase + patterns folder
- Traverses call graph from intent to execution
- Wide vs deep called explicitly with reasoning
- Senior engineer judgment throughout — challenges with severity-proportional pushback
- Per function: minimal stub + minimal docstring + base acceptance tests + TODO edge case comments
- Writes Design Doc inline as jam progresses (running notes tone, appendix for rejected approaches)
- Closes with explicit completeness check

**Skill 2: Issue Architect**
- Reads Design Doc + stubs + jam transcript
- Produces parent issue (intent + overall AC + batch execution plan)
- Produces sub-issues (coherent task batches, code refs, AC, technical guidelines, depends-on/blocks)
- Linear MCP if present, markdown fallback

**Skill 3: Orchestrator + Executor**
- Orchestrator reads parent issue + Design Doc, drives batch execution
- Spawns fast model subagents per sub-issue
- Two attempt max per subagent before escalating
- Implementation notes per batch, default stops for review
- Auto mode available
- No auto-commits, stages only
- Linear status updates if MCP present

---

Before we start writing the actual skill files — one meta question: do you want these as three completely separate skill files that chain explicitly, or as one skill collection under a single folder (like how superpowers is structured) with a `using-[skill-name].md` entry point that explains how they connect?

---

````turn
ROLE: USER
````

yeah just one thing, let it ask and confirm even if linear is present coz I may want a specific way or something so

---

````turn
ROLE: CLAUDE
````

Good catch. Linear MCP presence doesn't mean auto-use — Skill 2 asks "Linear MCP detected, want me to create issues there or use markdown?" and you decide. Could also be project-specific — maybe one project uses Linear, another doesn't, even if MCP is connected.

Same for the orchestrator — asks at start "tracking via Linear or markdown?" rather than assuming.

---

On the folder structure question — what's your preference? Single collection like superpowers with an entry point, or three separate skill files?

My instinct is a single collection folder since the three skills are tightly coupled and share context (Design Doc format, issue schema, etc). Something like:

```
skills/
  lld-workflow/
    SKILL.md          ← entry point, explains the three skills and when to use each
    design-jam/
      SKILL.md
    issue-architect/
      SKILL.md
    orchestrator/
      SKILL.md
```

The entry point is what you'd reference in Cursor rules — "for major features use lld-workflow" — and it routes to the right sub-skill based on where you are in the process.

Does that structure feel right, or do you want them flatter?

---

````turn
ROLE: USER
````

should we call it something else? like maybe design engineering unless that word means something else altogether, also instead of issue architect ig we can call it something simpler, its not like a "technical architect" so and design-jam is actually more than just jamming it goes one step beyond and actually does the lld in code in a sense, instead of orchestrator call it something else

so give me some naming options overall for every thing here

---

````turn
ROLE: CLAUDE
````

Here are naming options across the board:

---

**Collection name** (replaces `lld-workflow`):
- `blueprint` — design then build, clean metaphor
- `forge` — you shape it, then it gets built
- `signal` — intentional, deliberate engineering
- `groundwork` — you lay it before building
- `meridian` — a bit abstract but distinctive

---

**Skill 1** (replaces `design-jam` — the LLD in code session):
- `architect` — you're literally architecting the codebase
- `blueprint` — designing the plan before building
- `scaffold` — but this has a specific coding meaning already, might confuse
- `design-session` — plain but accurate
- `lld` — literal, no ambiguity
- `deep-design` — captures that it goes beyond jamming into actual code

---

**Skill 2** (replaces `issue-architect` — translates design into issue tree):
- `planner` — simple, accurate
- `breakdown` — breaking design into executable work
- `slice` — slicing the design into issues, like story slicing
- `taskmaster` — a bit aggressive but memorable
- `decompose` — technical but accurate

---

**Skill 3** (replaces `orchestrator` — drives execution):
- `builder` — it builds what was designed
- `executor` — plain, accurate
- `forge` — forges the design into real code
- `runner` — lightweight, accurate
- `dispatch` — emphasizes the subagent spawning nature

---

My personal picks if you're asking:
- Collection: `blueprint` or `forge`
- Skill 1: `deep-design` or `architect`
- Skill 2: `slice` or `planner`
- Skill 3: `builder` or `dispatch`

What resonates?

---

````turn
ROLE: USER
````

i like deep-design for skill 1 for sure
for skill 2, what about something fun like just-planner or task-planner or issue-planner
for skill 3 builder works
for overall collection name, what does meridian mean?

---

````turn
ROLE: CLAUDE
````

**Meridian** — literally the highest point the sun reaches in the sky. Metaphorically used to mean the peak or defining moment of something. In navigation it's the reference line everything is measured from.

So in the context of this workflow it actually works well — it's the reference point, the deliberate line you draw before building anything. But it's abstract enough that someone unfamiliar won't immediately get it.

If you like it for that reason (distinctive, not overloaded with existing coding connotations) it's a good pick. If you want something more immediately legible, `forge` or `blueprint` are cleaner.

---

**On Skill 2 naming:**

- `just-planner` — fun but "just" undersells it, and could read as "only a planner"
- `task-planner` — accurate but a bit generic, sounds like a todo app
- `issue-planner` — my favourite of the three, clear about what it produces, not trying to be more than it is, no connotation baggage

`issue-planner` is direct and honest about what the skill does — it plans the issues. Simple works here since Skill 1 has the interesting name.

---

So the full set would be:

```
[collection]/
  deep-design/
  issue-planner/
  builder/
```

Collection name — you still deciding between meridian, forge, blueprint?

---

````turn
ROLE: USER
````

yeah like meridian is like kinda brandable so i could open source these skills later on once I have tested these and optimized these enough to be generally usable by others

---

````turn
ROLE: CLAUDE
````

That's a solid long term play. Open sourcing a well-designed, battle-tested skill collection with a distinctive name is a real thing — there's no good canonical "how to actually engineer with AI properly" skill set out there yet. Superpowers is close but as you identified it has real gaps.

Meridian works well for that context too — it's:
- Brandable and memorable
- Not overloaded with existing tool names
- Has a meaningful metaphor (reference point, deliberate line before building)
- Sounds like something you'd actually want to use vs a generic "ai-coding-workflow" repo

So the full collection:

```
meridian/
  SKILL.md              ← entry point + philosophy
  deep-design/
    SKILL.md
  issue-planner/
    SKILL.md
  builder/
    SKILL.md
```

And when you open source it, the entry point SKILL.md basically becomes the README — the philosophy of human-as-brain, AI-as-hands, deliberate top-down engineering, staying in control without being the one typing.

---

I think we have everything we need to actually start writing the skill files now. Suggested order:

1. `deep-design` first — it's the most detailed and sets the tone for everything downstream
2. `issue-planner` second — depends on deep-design's output format being defined first
3. `builder` third — depends on issue-planner's output format
4. `SKILL.md` entry point last — once all three are written, the philosophy doc writes itself

Want to start writing `deep-design` now?

---

````turn
ROLE: USER
````

wait

---

````turn
ROLE: CLAUDE
````

Yeah go ahead.

---

````turn
ROLE: USER
````

export all of our conversation so far into a single long markdown file (verbatim), use proper separators and syntax for every turn coz our context contains markdown so it needs to be clearly separated to avoid confusion

---

*[This document is the export.]*