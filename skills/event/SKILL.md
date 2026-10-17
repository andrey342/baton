---
name: event
description: >-
  What baton's coordinating chat does each time its implementer session (named baton-<run>) ends a turn or sends a message, when the person answers a question baton asked, and when a run is picked up again after the app was closed. Reads the run's files in one batch, decides within the closed authority table, writes in one batch and says one line. Use on a side-sessions event or a message from a session named baton-…, on the person's answer to a baton question or pause, and from /baton:status continue or "sigue".
---

# /baton:event

The plugin's files: `${CLAUDE_PLUGIN_ROOT}` (below, **PLUGIN**). You are the coordinator of a run that `/baton:run` launched from this chat; the run's files and fields are described in `PLUGIN/skills/run/SKILL.md` ("Files") and `PLUGIN/templates/state.json`. Load this skill once per conversation: when its text is already above, follow it without loading it again.

**Every event is three calls**: one message of reads, one message of writes, one line to the person. Each call reads this whole chat again, which is where a plan's cost goes, so calls that do not depend on each other always share a message. If your app asks for a task list and a wrap-up, send `update_plan` with the reads and `wrap_up` with the writes, never in a message of their own. Do not run `date` alone, read a template, or Edit `state.json` piece by piece.

Rules: talk to the person in the language of the conversation, one line per event unless something needs them; one shell command per call, never chained; files changed with Write and Edit only; nothing destructive (no `--force`, no deleting branches, no removing a worktree with changes); decisions follow `PLUGIN/prompts/supervisor.md`, whose table is the only authority. Deferred app tools (SendMessage, PushNotification, `wrap_up`, `get_session`): load the ones listed only by name with one ToolSearch, in the reads.

## 1. Read, in one message

The run is the one whose `state.json` (`status` `running` or `waiting`) names the event's session in `worker.name` or `worker.sessionId`. If this conversation does not show its paths (after a compaction, say), Glob `.claude/runs/*/state.json` from the checkout first. Then, in one message:

- Read `runDir/state.json`, and `workerRunDir/result-<current>.md`;
- `git -C <worktree> log --oneline <startSha of current>..HEAD`;
- Grep, pattern `^(Verdict|Veredicto):|^### F-`, in workerRunDir with glob `review-<current>-r*.md`, output `content`: every round's verdict and its findings' headings;
- `date -u +%Y-%m-%dT%H:%M:%SZ`;
- when the event quotes a status other than `done` and `supervisor.md` is not yet in this conversation: Read `PLUGIN/prompts/supervisor.md`;
- when `current` is the last part: Read `PLUGIN/skills/event/deliver.md` and `PLUGIN/templates/report.md`.

## 2. Decide

The event quotes the start of the session's report, `baton-result: <status> · part <X>`. When it disagrees with the file's `status` or `part`, or there is no result file, the file is stale: the message is "baton · part <X>: end your turn with the baton-result block and save it as `result-<X>.md`." The second time in a row with no result: escalate. A **message** (not an event) from the session is read as a `question` result.

By the result's `status`:

- **done**: valid when the log lists commits and the last round's first non-empty line reads `Verdict: OK` (or `Veredicto: OK`; ignore a leading code fence). Not valid: "baton · part <X> is not reviewed OK yet: run the review loop as your brief says." Valid: part X becomes `done` with `endSha` (the log's top commit), `rounds` and `verdict`, and its `NO` rounds are logged (below). Then the next part:
  - it has `pauseBefore`: `status: waiting`, `waiting: { "kind": "pause", "part": "<next>" }`, and escalate "Part <X> done. The plan pauses before part <next>: continue?" with the buttons «Continue with <next>» / «Stop here»;
  - otherwise it becomes `working` with `startSha` = X's `endSha`, `current` moves to it, and the message is "baton · part <next> from <startSha>: read and follow `<workerRunDir>/brief.md`.";
  - no part left: the delivery, as `deliver.md` says (it continues this turn).
- **question**: as `supervisor.md` says. `needs: human`, a row of its table, or unsure: escalate. Answered from the plan, the rules or the code: a line in `settled.md` (below) and the message "baton · answer from the plan for part <X>: <answer>".
- **blocked** or **failed**: as `supervisor.md` says, counted in the part's `retries`, `replanned` and `decisions`:
  - a retry, two per part at most: "baton · retry part <X>: <what to try>";
  - a replan, once per part (also when the review rounds ran out): Write `workerRunDir/brief-<X>-replan.md`, a heading "Replanned by baton's supervisor", the reason, what changes, and "Criteria and start commit as in `brief.md`, part <X>; review rounds go on from r<last+1>, with the brief's number of rounds again"; the message is "baton · part <X> replanned: read and follow `<workerRunDir>/brief-<X>-replan.md`.";
  - else escalate.

**Logging findings.** Whenever the Grep shows `NO` rounds of the part above its `logged` round (0 at first), each of their `### F-nn · P · category · file · title` headings becomes one line of `<checkout>/.claude/runs/findings.jsonl`, `{"plan":"<run>","part":"<X>","round":<n>,"priority":"P2","category":"tests","file":"src/a.js:12","title":"…","at":"<now>"}`, and `logged` becomes the last round seen, so a round is logged once whether the part ends `done` or `blocked`.

**Every decision and escalation** is a row of `decisions.md` (time, part, what stopped, the decision, one sentence of why), counted in the part's `decisions`, and the one line you say.

**The message quota.** The app delivers at most 10 messages to other sessions per message the person writes in this chat (a button press counts), and events do not reset it (D-33). Each message to the worker adds 1 to `messagesSinceUser` and sets `lastSentAt`. A message that would make it 10 is not sent: `status: waiting`, `waiting: { "kind": "quota", "part": "<X>", "held": "<the message>" }`, and escalate "Nine messages since your last word: the app needs one from you to let baton go on." with the button «Continue».

## 3. Write, in one message

- Write `state.json` whole, with every change of step 2 and `updatedAt`;
- SendMessage to `worker.sessionId`, when there is a message;
- Edit `decisions.md` (a row), `settled.md` (a line), `findings.jsonl` (Write it when absent), Write a replan brief: whichever step 2 needs;
- escalating: PushNotification and `wrap_up` with the question and its buttons (below).

If the app refuses the message (its quota, or the session cannot be reached), the state you wrote is wrong: Write it again with the message not sent (`messagesSinceUser` and `current` as before) and escalate, `kind` `quota` with the message held, or `blocked` with the app's words. Otherwise the one line, and end the turn. Never poll, never wait.

**Escalating** (always the person's, or unsure): `status: waiting` with `waiting` (`kind`: `question`, `pause`, `blocked`, `publish` or `quota`; the part; the question). The `wrap_up` carries one sentence on what is asked and why it is theirs as its recap, the question as asked, and the likely answers as two or three buttons; without `wrap_up`, ask it as plain text. The push notification (under 200 characters) says the same sentence. Nothing runs until they answer.

**Settled answers** (D-37): every answer, from the plan or from the person, is appended to `workerRunDir/settled.md` before it is sent, as `- <time> · part <X> · from the plan|from the person · Q: <question> · A: <answer>` (the person's words verbatim).

## The person's answer

Any message the person writes in this chat, typed or a button, sets `messagesSinceUser` to 0 before anything else, whatever the run's status: the app's count starts again with it. When the run is `waiting`, their words are the answer: the same three steps (Read `state.json` and the time; Write `state.json` with a `presses` entry, `status: running`, `waiting: null`; the one line), and:

- a question: a line in `settled.md`, then forward their words **verbatim**: "baton · answer from the person for part <X>: <their words>";
- a pause: «Continue» sends the next part's message; «Stop here» delivers the parts done so far (`deliver.md`; the rest stay pending, said in the report);
- the quota: send the held message (it is the first of the new count);
- a publish question: `deliver.md` step 4 («Publish»), or delivery as `branch` («Leave the branch»).

## Resuming

When the person says "sigue" or "continue", runs `/baton:status continue`, or this chat reopens with a run `running` or `waiting`:

1. Read `state.json`; their message sets `messagesSinceUser` to 0 (above). `waiting` set: ask that question again, as an escalation.
2. Otherwise read `workerRunDir/result-<current>.md` and its time (`date -u -r <file> +%Y-%m-%dT%H:%M:%SZ`, in the same message): a result written after `lastSentAt` is an event not yet handled: act on it (steps 2 and 3).
3. Otherwise look for the worker with `mcp__ccd_session_mgmt__get_session` (`state.worker.sessionId`). Alive and idle: send "baton · continue part <X> from your brief `<workerRunDir>/brief.md` (or its replan brief); check `git log` for what is done." Missing or archived: start a new implementer session as `/baton:run` step 4 says, with the same brief and the current part (this is the person's turn, so it may be started), and store its id. Working: say so and end the turn; its next turn end wakes you.
