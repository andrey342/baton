# baton's model proposal: how the coordinator picks a model for each role of each part

You read the whole plan and propose, for every part, the model and effort of its implementer, its reviewer and, where it earns one, a Critic. The person approves the table before anything is created; nothing here is a default that skips that step. The plan's `mode=` and `models=`, and the profile's `models.start` and `modes`, are only where your proposal starts: you move away from them when the part's text gives a reason, and you say the reason.

## Read each part on five axes

For each axis, find the evidence in the plan itself and cite the section (`§3`, `D4`, `Part 2`, the heading's own words). A part with no evidence on an axis is low on it.

| Axis | High | Low |
|---|---|---|
| Risk | security, authorization, credentials handling, data or migrations, concurrency, a public contract (API, schema, file format others read) | internal change, reversible, no one else reads it |
| Difficulty | design decisions the plan leaves open ("decide…", "choose…", alternatives listed) | steps the plan prescribes one by one, or a script that does them |
| Size | many files or several repos, new modules | one or two files |
| Kind | domain logic, infrastructure | frontend with the design already chosen, documentation, QA, preflight, closing |
| Cost of a mistake | lost data, a broken release, a finding the reviewer may catch late | a cheap redo |

## Starting points, not rules

- High risk and an open design: implementer Opus medium.
- Mechanical or documentation work: implementer Sonnet medium.
- Haiku only for parts that are pure copying or formatting with a gate that proves them.
- The reviewer one step above the implementer on risky parts (Sonnet → Opus, or the same model with more effort); on the rest, Sonnet medium.
- A Critic (Opus high) only where the part has a contract or an acceptance that must be judged apart from the implementer's own review; else `—`.
- Effort: `medium` by default; `high` when the part is long or its acceptance is subtle; `low` only for the trivial; `xhigh` and `max` only when the plan asks for them.

Models: Opus 5.5 (`opus`), Sonnet 5.5 (`sonnet`), Haiku 5.5 (`haiku`). Efforts: `low`, `medium`, `high`, `xhigh`, `max`. A role's skills are the profile's `roles.<role>.skills`, plus a repo skill the part's text names.

## Weight

The weight compares parts with one another; it is not an amount in USD.

- Size: S 1, M 2, L 4.
- Model, from the official price per token (cached 2026-10-06: Opus 5.5 $4/$20, Sonnet 5.5 $2/$10, Haiku 5.5 $0.10/$0.50 per million input/output tokens): Opus 2, Sonnet 1, Haiku 0.05.
- Effort, baton's own estimate of tokens spent, not a price: low 0.5, medium 1, high 1.5, xhigh 2, max 3.

A part's weight is its size times the implementer's model and effort factors; the reviewer and Critic add a fifth of theirs each, since a review reads far less than an implementation writes. The table shows the size letter; the line under it says which parts carry most of the plan's weight, and what lowering the heaviest one would save, in per cent of the total.

## The ceiling

The app never starts a session on a model above the chat's own; it ignores the request (D-45; the tool's own words: "anything higher is ignored"). So an implementer row on Opus needs a coordinator on Opus. Reviewers and Critics are subagents of the part's session, and the Agent tool runs them above the session's model (D-61): the ceiling is for implementers only. When a row is above this chat's model, the table says so on that row and in its "Coordinator" line, and offers two ways out: run `/baton:run` again from a chat on that model, or lower the row. Never launch with a model other than the approved one.

## While the plan runs

When a part turns out harder than its row assumed (review rounds that ran out, a replan, a retry, a NO with P0 or P1 findings) or easier (OK in round 1 with no finding, on a part sized L), look at the rows still pending of the same kind. Raising one is spending: ask the person (the Spending row of `supervisor.md`). Lowering one is said in a line and written to `decisions.md`.
