---
name: event
description: >-
  What baton's coordinating chat does each time an implementer session of its run (named baton-<run>-<part>, or baton-<run> for a 0.2 run) ends a turn or sends a message, when the person answers a question baton asked, and when a run is picked up again after the app was closed. Reads the run's files in one batch, checks the part's work in every repo instead of taking the report's word, decides within the closed authority table, starts the next part in a new session, and says one line. Use on a side-sessions event or a message from a session named baton-…, on the person's answer to a baton question or pause, and from /baton:status continue or "sigue".
---

# /baton:event

The plugin's files: `${CLAUDE_PLUGIN_ROOT}` (below, **PLUGIN**). You are the coordinator of a run that `/baton:run` launched from this chat; the run's files and fields are described in `PLUGIN/skills/run/SKILL.md` ("Files") and `PLUGIN/templates/state.json`. Load this skill once per conversation: when its text is already above, follow it without loading it again. You never implement: the part's session does the work, you check it.

**Every event is three calls**: one message of reads, one message of writes, one line to the person; four when the next part's session starts, since its id goes into `state.json` after `start_session` returns. Each call reads this whole chat again, which is where a plan's cost goes, so calls that do not depend on each other always share a message. If your app asks for a task list and a wrap-up, send `update_plan` with the reads and `wrap_up` with the last writes, never in a message of their own. Do not run `date` alone, read a template, or Edit `state.json` piece by piece.

Rules: talk to the person in the language of the conversation, one line per event unless something needs them; one shell command per call, never chained; files changed with Write and Edit only; nothing destructive (no `--force`, no deleting branches, no removing a worktree with changes); decisions follow `PLUGIN/prompts/supervisor.md`, whose table is the only authority. **Nothing runs in the background from this chat**: every command runs in the foreground and ends inside the turn. A turn that the end of a background task opens is an automated turn, and the app does not let it start a session (plan 0.3 §2); long work belongs to a part's session. Deferred app tools (SendMessage, PushNotification, `wrap_up`, `start_session`, `dismiss_task`, `get_session`, `list_sessions`, `set_session_effort`): load the ones listed only by name with one ToolSearch, in the reads.

## State versions

`state.json` is `version` 1 (baton 0.2; a file without `version` is 1) or `version` 2 (`PLUGIN/templates/state.json`). Both are read; a run is written back in the version it has, never upgraded in flight. Where this skill names a v2 field, a v1 run reads:

| v2 | v1 |
|---|---|
| the part's `session` (`id`, `name`) | `worker` (`sessionId`, `name`), one session for every part |
| `repos.<name>` (`path`, `branch`, `base`, `baseSha`) | one repo: `worktree`, `branch`, `base`, `baseSha` at the top |
| the part's `startSha` / `endSha`, one commit per repo of the part | one commit |
| the part's `implementer`, `reviewer`, `critic` | `worker.model`/`effort` and the top-level `reviewer`; no critic |
| `coordinator.sessionId` | this chat |
| `proposal.approvedAt` | `startedAt`: a v1 run was launched by the person's own turn in 0.2, so it counts as approved; restarting its lost session uses `worker.model` and `effort` and asks for no table |

A v1 run, and a v2 run with `sessions: "per-plan"`, keep one session for the whole plan: the next part goes to it as a message, as in 0.2. A v2 run with `sessions: "per-part"` (the default) starts a new session for each part.

Run statuses: `running`, `waiting`, `done-not-delivered`, `delivered`, `stopped` and `dry-run` in both; v2 adds `proposed` (the model table is out, nothing created), `paused` and `closing`. Part statuses: `pending`, `working`, `done`, and in v2 `paused`. `waiting.kind` in v2 adds `start` (a session the app would not start, with its card's `taskId`) and `resource`.

**The result block** is `baton-result`, v1 or v2 (`PLUGIN/prompts/implementer.md`); a v1 block only has fewer fields. A block fenced as `coord-result`, or a report that starts `coord-result:`, is read exactly the same way: it is the name runs coordinated by hand use, and a part done that way is checked like any other.

## 1. Read, in one message

The run is the one whose `state.json` (`status` `running`, `waiting` or `closing`) names the event's session in `worker.name` or `worker.sessionId` (v1), or in a part's `session.name` or `session.id` (v2). A session named `baton-<run12>-close` belongs to that run's close. A session named `baton-<run12>-<part>` that the state does not hold yet (a card the person started, or a start whose id was never written) belongs to that run and part: write its id into the part's `session` with this event's state and, when the run was waiting on that card (`waiting.kind: "start"`), set `status: running` and `waiting: null`. If this conversation does not show the run's paths (after a compaction, say), Glob `.claude/runs/*/state.json` from the checkout first. Then, in one message:

- Read `runDir/state.json`, and `workerRunDir/result-<current>.md`; with a `done`, also `runDir/decisions.md` (the clean-tree rule below looks at the part's last rows);
- for each repo of the part (v1: the worktree): `git -C <path> log --oneline <startSha>..HEAD` and `git -C <path> status --porcelain` (for a root that holds other repos of the run as submodules, `git -C <root> status --porcelain --ignore-submodules=all`: each submodule is checked on its own, and the root's gitlinks move as they work, until the delivery snapshots them);
- only when the part made a snapshot of submodules (a `snapshot` hook, D6, or its result's commits say so): `git -C <root> ls-tree HEAD <sub path>` and `git -C <sub> rev-parse HEAD`, for each submodule of the part. Without one, the root's gitlinks move with the submodules until the delivery snapshots them;
- Grep, pattern `^(Verdict|Veredicto):|^Model:|^### (F-|Criteria|Gates)`, in workerRunDir with glob `review-<current>-r*.md`, output `content`: every round's verdict, the model it ran on, its findings' headings, and whether its sections are there;
- when the part has a `critic` row: the same Grep with glob `critic-<current>-r*.md`;
- when a session starts next (a `done` in a `per-part` run with a part left): `git -C <path> rev-parse HEAD` for each repo of the next part that the current one does not touch, and `get_session` for this chat (`self`): its `model` and `effort`, the ceiling of the start, kept in `coordinator`;
- `date -u +%Y-%m-%dT%H:%M:%SZ`;
- when the event quotes a status other than `done` and `supervisor.md` is not yet in this conversation: Read `PLUGIN/prompts/supervisor.md`;
- when it quotes `done` in a version 2 run and `models.md` is not yet in this conversation: Read `PLUGIN/prompts/models.md`;
- when `current` is the last part, or the next part's pause has a `pauseDeliver`: Read `PLUGIN/skills/event/deliver.md` (and `PLUGIN/templates/report.md` for the last part);
- when the state has `hooks`, a `branchCreatedBy` other than `baton`, or `excluded` lines, and `PLUGIN/skills/run/hooks.md` is not yet in this conversation: Read it.

## 2. Decide

The event quotes the start of the session's report, `baton-result: <status> · part <X>` (or `coord-result: …`). When it disagrees with the file's `status` or `part`, or there is no result file, the file is stale: the message is "baton · part <X>: end your turn with the baton-result block and save it as `result-<X>.md`." The second time in a row with no result: escalate. A **message** (not an event) from the session is read as a `question` result.

By the result's `status`:

- **any result while the run is `closing`** is not a part's, and goes by `closing.phase`:
  - **`deliver`** (a `baton · entrega` was sent): it is the delivery's result, handled by "With a `deliver` hook" in `deliver.md`;
  - **`close`** (a session hook of the close was sent, to the last part's session or to `baton-<run12>-close`): a `done` goes on with steps 2 to 4 of "The close" in `hooks.md`, then `closedAt` and the status back to `delivered` or `stopped`. A `blocked` or `failed` escalates, and the run stays `closing`.
- **done**: check it; never take the report's word for it (D4). With `branchCreatedBy: "part:<X>"`, the branches are checked first, as `hooks.md` says. Every check that fails goes into one message to the part's session, and the part stays `working`:
  1. **Clean tree.** Each repo's `status --porcelain` prints nothing (files git ignores do not show). There is no other way through: a file explained in the result is still a dirty tree. Otherwise: "baton · part <X>: leave the tree clean: `git status` in <repo> shows <the files>. Commit what belongs to the part and take out what the part left behind; if a file must stay uncommitted, end with `status: question` and say why." When `decisions.md` shows this same message for the same files at the part's previous event, do not send it again: escalate, with the files and the result's words.
  2. **Commits.** Each repo of the part has commits since its `startSha`, unless the result says why a repo needed none. None at all: "baton · part <X> is not reviewed OK yet: run the review loop as your brief says."
  3. **Reviews.** The last round's first non-empty line reads `Verdict: OK` (or `Veredicto: OK`; ignore a leading code fence). Otherwise the message above. Every review file has its `### Criteria` and `### Gates` headings; one without them is not the reviewer's text as written: "baton · part <X>: `review-<X>-r<n>.md` is not the review as the reviewer wrote it (no `### Criteria` or `### Gates`): save its answer verbatim, or run that round again."
  4. **The Critic**, when the part has a `critic` row: there is a Critic file, its last round reads `Verdict: PASS`, and a `FAIL` in any round has a later round after it. A FAIL closed without a later round, or no Critic file: "baton · part <X>: the Critic's FAIL in `critic-<X>-r<n>.md` was closed but not checked again: run the Critic again (`critic-<X>-r<n+1>.md`) before you end with done." (or "run the Critic: the brief gives part <X> one").
  5. **Submodules**, only for a part that made a snapshot: each `ls-tree` commit equals the submodule's `rev-parse HEAD`. Otherwise: "baton · part <X>: the root's gitlink for <sub> is not the submodule's HEAD after your snapshot: redo it as the brief says." A part that made none is not asked for one: moved gitlinks wait for the delivery's snapshot.
  6. **Deviations.** Each entry of the result's `deviations:` names what ran instead of the gate and its evidence (a path, a command with its exit code, a count). With evidence: accepted, a `decisions.md` row "deviation accepted" with the evidence, and it goes into the report. Without: "baton · part <X>: the deviation for <gate> has no evidence: add it to `result-<X>.md`." A deviation that touches a row of the person's (a red gate accepted for the environment, say): escalate.

  Not blocking, but written down: each review's `Model:` line against the part's approved `reviewer` row (and the Critic's against `critic`). A different model, or no `Model:` line, is a `decisions.md` row ("review r<n> ran on <model>, approved <row>") and a note in the one line.

  All checks pass: part X becomes `done` with `endSha` (each repo's top commit; v1: one), `rounds`, `verdict` and `verified` (`at`, `clean: true`, `reviewerModel`, `deviations`), and its `NO` rounds are logged (below). Then the next part:
  - it has `pauseBefore`: `status: waiting`, `waiting: { "kind": "pause", "part": "<next>" }`, and escalate "Part <X> done. The plan pauses before part <next>: continue?" with the buttons «Continue with <next>» / «Stop here». When the pause has a `pauseDeliver` (the plan's `deliver: <repos>`), those repos are delivered as "A partial delivery and its pause" in `deliver.md` says. With nothing to ask, they are delivered first and the question gives the outcome. With `humanBeforePublish` and `pr` or `merge`, the question carries the publishing as well, and the delivery waits for the answer;
  - otherwise it becomes `working` with `startSha` per repo (X's `endSha` for the repos X touched, the `rev-parse` read for the others), `current` moves to it, and it starts as "The next part's session" says (a v1 or `per-plan` run: the message "baton · part <next> from <startSha>: read and follow `<workerRunDir>/brief.md`." to the same session, with `<repo> <sha>` per repo in v2);
  - no part left: the delivery, as `deliver.md` says (it continues this turn).

  In a version 2 run with parts still pending, weigh the part just done against its row, as "While the plan runs" in `PLUGIN/prompts/models.md` says: lowering a pending row is a line and a `decisions.md` row; raising one is the person's (Spending), asked after this event's start or message.
- **question**: as `supervisor.md` says. `needs: human`, a row of its table, or unsure: escalate. Answered from the plan, the rules or the code: a line in `settled.md` (below) and the message "baton · answer from the plan for part <X>: <answer>".
- **blocked** or **failed**: as `supervisor.md` says, counted in the part's `retries`, `replanned` and `decisions`. When the reason is exhausted review rounds or exhausted Critic rounds (the two are handled alike, and a replan gives the Critic its rounds again too), first read the open findings of the last review or Critic round and check each one in the code yourself (Read the lines it cites, in the reads): what you can refute goes into the replan brief with your evidence, and a finding you cannot judge is the person's. Then:
  - a retry, two per part at most: "baton · retry part <X>: <what to try>";
  - a replan, once per part (also when the review rounds ran out): Write `workerRunDir/brief-<X>-replan.md`, a heading "Replanned by baton's supervisor", the reason, what changes, and "Criteria and start commits as in `brief.md`, part <X>; review rounds (and Critic rounds) go on from r<last+1>, with the brief's number of rounds again"; the message is "baton · part <X> replanned: read and follow `<workerRunDir>/brief-<X>-replan.md`.";
  - else escalate.

**Logging findings.** Whenever the Grep shows `NO` rounds of the part above its `logged` round (0 at first), each of their `### F-nn · P · category · file · title` headings becomes one line of `<checkout>/.claude/runs/findings.jsonl`, `{"plan":"<run>","part":"<X>","round":<n>,"priority":"P2","category":"tests","file":"src/a.js:12","title":"…","at":"<now>"}`, and `logged` becomes the last round seen, so a round is logged once whether the part ends `done` or `blocked`.

**Every decision and escalation** is a row of `decisions.md` (time, part, what stopped, the decision, one sentence of why), counted in the part's `decisions`, and the one line you say.

**Messages go to the current part's session**, always: `parts[current].session.id` (v1: `worker.sessionId`), never a session of an earlier part.

**The message quota.** The app delivers at most 10 messages to other sessions per message the person writes in this chat (a button press counts), and events do not reset it (D-33). Each message to a session, and each session started (D-59), adds 1 to `messagesSinceUser` and sets `lastSentAt`. The app also wakes this chat for at most 10 turn ends of other sessions in a row without a word from the person; the 11th is never delivered and the run would stop in silence (seen live twice in 0.2). So every event adds 1 to `wakesSinceUser`, and on the 10th wake the next message or start is held the same way, whatever it is. One that would make `messagesSinceUser` 10 is not sent either: `status: waiting`, `waiting: { "kind": "quota", "part": "<X>", "held": "<the message, or the start>" }`, and escalate "Nine messages since your last word: the app needs one from you to let baton go on." with the button «Continue».

## The next part's session

In a `per-part` run each part gets a new session (D3), with `start_session`:

- `initiation: "user_asked"`: the person asked for a session per part when they approved the table («Yes, launch each part in its session with this table»), which is what lets this event start it; `context: "fresh"`; `cwd`: the worktree's absolute path (v2 `workspace: checkout`: the checkout), `use_worktree: false`, `wake_when_done: true`;
- `name: "baton-<run12>-<part>"`: the run id cut to 12 characters and the part id in lower case, at most 24 characters (D-21); `title: "baton · <plan title> · <part>"`, under 60 characters;
- `model` and `effort` of the part's approved `implementer` row, the model as its id (`opus` `claude-opus-5-5`, `sonnet` `claude-sonnet-5-5`, `haiku` `claude-haiku-5-5`). The app never starts a session above this chat's model, and takes an effort only "at or below yours": when the row's effort is above this chat's (`get_session` for this chat, read with the reads), start at this chat's effort and raise the new session to the row's with `mcp__ccd_session_mgmt__set_session_effort` right after, in the message that writes its id; the line says so;
- `prompt`: "You are baton's implementer for part <part> of the plan «<title>». Read `<workerRunDir>/implementer.md`, then do part <part> from <repo> <sha>[ · <repo> <sha>…]: read and follow `<workerRunDir>/brief.md`. Parts done before yours: <ids, or none>; read their `result-*.md` in the run folder first. End every turn with the baton-result block it describes.";
- `background`: "baton runs a written plan, one session per part. A coordinating chat started this session for part <part> in the plan's worktree on branch <branch>; it reads your result file, checks your work and answers your questions. The brief's rules and notes say what the environment needs; the earlier parts' results say what they left. Do not push or open pull requests unless a `baton · entrega` message says so; never merge or change branches."

A `beforePart` hook that is the coordinator's runs before the start, in the reads' message or its own, as `hooks.md` says; it failing stops the start and escalates. The writes go in two messages. First the start with every write that does not depend on it (`decisions.md`, `findings.jsonl`, `settled.md`). Then, with its result:

- **Started**: Write `state.json` whole, the part's `session` with the returned `id`, its `name` and `archived: false`, and `set_session_effort` in the same message when the row's effort was above this chat's.
- **Refused** because this turn is automated ("Start sessions only on the user's own words…": a broken chain of events, plan 0.3 §2): propose the same session as a card, `initiation: "own_initiative"`, with the same `title`, `name`, `model`, `effort` and `background`, `use_worktree: false`, and no `cwd` or `wake_when_done`. Its `prompt` is the same with a first and a last sentence added: first "Card for part <part>, approved to run on <model id> at effort <the row's effort>.", so the person who clicks it sees what was approved even if the app does not keep the card's model; last "Your folder is `<worktree>`: work only there, with `git -C` and absolute paths.", since a card carries no folder. Then Write `state.json` with `status: waiting`, `waiting: { "kind": "start", "part": "<part>", "taskId": "<the card's task_id>" }` and the part's `session` with its `name` and `id: null`, send a push notification "Part <part> is ready to start: one click on its card", and say the same in the one line with the model and effort the card asks for. The person's click starts it, and its turn ends wake this chat (D-60); its first event, read as above, stores its id and checks its model and effort with `get_session` against the row: a difference is a `decisions.md` row, set right with `set_session_effort` when it is the effort.
- **Refused** otherwise (the app's own error): escalate, `kind` `blocked`, with the app's words.

A card cannot be edited: to change its brief, `dismiss_task` it and propose another.

## 3. Write, in one message

- Write `state.json` whole, with every change of step 2 and `updatedAt`;
- SendMessage to the current part's session, when there is a message; or the next part's session, as above;
- Edit `decisions.md` (a row), `settled.md` (a line), `findings.jsonl` (Write it when absent), Write a replan brief: whichever step 2 needs;
- escalating: PushNotification and `wrap_up` with the question and its buttons (below).

If the app refuses the message (its quota, or the session cannot be reached), the state you wrote is wrong: Write it again with the message not sent (`messagesSinceUser` and `current` as before) and escalate, `kind` `quota` with the message held, or `blocked` with the app's words. Otherwise the one line, and end the turn. Never poll, never wait.

**Escalating** (always the person's, or unsure): `status: waiting` with `waiting` (`kind`: `question`, `pause`, `blocked`, `publish`, `quota` or `start`; the part; the question). The `wrap_up` carries one sentence on what is asked and why it is theirs as its recap, the question as asked, and the likely answers as two or three buttons; without `wrap_up`, ask it as plain text. The push notification (under 200 characters) says the same sentence. Nothing runs until they answer.

**Settled answers** (D-37): every answer, from the plan or from the person, is appended to `workerRunDir/settled.md` before it is sent, as `- <time> · part <X> · from the plan|from the person · Q: <question> · A: <answer>` (the person's words verbatim).

## The person's answer

Any message the person writes in this chat, typed or a button, sets `messagesSinceUser` and `wakesSinceUser` to 0 before anything else, whatever the run's status: the app's count starts again with it. When the run is `proposed`, their words answer the model table: follow step 3 of `/baton:run` (`PLUGIN/skills/run/SKILL.md`). When the run is `waiting`, their words are the answer: the same three steps (Read `state.json` and the time; Write `state.json` with a `presses` entry, `status: running`, `waiting: null`; the one line), and:

- a question: a line in `settled.md`, then forward their words **verbatim**: "baton · answer from the person for part <X>: <their words>";
- a pause: «Continue» starts the next part (its session, or its message in a `per-plan` run); «Publish <repos> and continue» first makes the pause's partial delivery (`deliver.md`), then starts it (a failed step keeps the pause waiting, with the failure in its question); «Continue without publishing» starts it with those repos undelivered; «Stop here» delivers the parts done so far (`deliver.md`; the rest stay pending, said in the report);
- the quota: send the held message, or make the held start (it is the first of the new count);
- a card still waiting (`waiting.kind: "start"`): the person may have clicked it already, and its session's first turn end may still be far off. So first look for that session: `mcp__ccd_session_mgmt__list_sessions` with `linked: true`, a session named as the part's `session.name`. Found: store its id, `status: running`, `waiting: null`, and say it is at work; start nothing. Not found: `dismiss_task` the card, and go by its answer:
  - **withdrawn** (the app confirms it removed a card nobody started): start the session yourself, as "The next part's session" says (this turn is the person's);
  - **already started**: start nothing, keep waiting for that session's first event (`status` and `waiting` stay as they are), and say so in the line;
  - **any other refusal or error** (the card is gone: dismissed in the app, or lost when it closed): only the person knows whether they clicked it, so escalate (`waiting.kind` stays `start`) with the buttons «I clicked it: wait» / «I did not: start it». «I did not: start it» is their turn: look at `list_sessions` once more and, still not found, start the session as "The next part's session" says; «I clicked it: wait» keeps waiting, with `status` and `waiting` as they are.
  
  Two sessions on one part would commit on the same branch, so nothing starts on a guess. When a session is found, or its first event arrives, `get_session` it and raise its effort to the row's with `set_session_effort` when it runs below (a card starts at this chat's effort);
- a publish question: `deliver.md` step 4 («Publish»), or delivery as `branch` («Leave the branch»).

## Resuming

When the person says "sigue" or "continue", runs `/baton:status continue`, or this chat reopens with a run `running` or `waiting`:

1. Read `state.json`; their message sets `messagesSinceUser` to 0 (above). `proposed`: with `proposal.approvedAt`, the launch (step 4 of `/baton:run`); without it, show its model table again with its buttons, as step 2 of `/baton:run` ends, and nothing starts until the person's yes. `waiting` set: ask that question again, as an escalation (a card not clicked: as in "The person's answer").
2. Otherwise read `workerRunDir/result-<current>.md` and its time (`date -u -r <file> +%Y-%m-%dT%H:%M:%SZ`, in the same message): a result written after `lastSentAt` is an event not yet handled: act on it (steps 2 and 3).
3. Otherwise look for the current part's session with `mcp__ccd_session_mgmt__get_session` (v1: `state.worker.sessionId`). Alive and idle: send "baton · continue part <X> from your brief `<workerRunDir>/brief.md` (or its replan brief); check `git log` for what is done." No `session.id` yet (a card): look for it by name, as in "The person's answer". Missing or archived: start a new session for the same part, as "The next part's session" says (a v1 run: `/baton:run` step 4, batch 7, with `worker.model` and `effort`), with the same brief and start commits (this is the person's turn, so it may be started), and store its id. Working: say so and end the turn; its next turn end wakes you.
