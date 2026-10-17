---
name: run
description: >-
  Run a written plan part by part from this chat. Creates the plan's worktree and branch, starts one nested implementer session in auto mode, has each part reviewed by a fresh read-only subagent until OK, answers the session's questions within a closed authority table, and delivers the way the repo asks (branch, pull request or merge) with a report. Use when the person asks to run, launch or execute a plan file, e.g. "run docs/plans/x.md", "ejecuta el plan", "lanza el plan docs/plans/x.md", "baton, run this plan"; also when a side-sessions event or message arrives from a session named baton-<plan>, and to test a launch without sessions with --dry-run.
argument-hint: "<plan.md> [--dry-run]"
---

# /baton:run

Arguments: `$ARGUMENTS`

The plugin's files: `${CLAUDE_PLUGIN_ROOT}` (below, **PLUGIN**). You are the **coordinator**: you prepare, launch, supervise and deliver; the implementer session does the work. Nobody else watches the plan: what you do not write to the run's files is lost when this chat compacts.

- With a plan path: launch it (steps 1–4).
- With `--dry-run`: steps 1–3 in full, then say what step 4 would do; never call `start_session`.
- With no arguments, or on a `<side-sessions-event>` or a message from a session named `baton-…`: find the active run (step 5's "Which run"), then act on it (step 5, or step 8 when nothing arrived).
- With no arguments and no active run: look for plans (`docs/plans/*.md`, or the folder the repo's rules name, leaving out `TEMPLATE.md`). Exactly one: offer it in one line ("Run docs/plans/x.md?", with a button when you have `wrap_up`) and launch it on the person's yes. Several: list them and ask which. None: say how to write one (`/baton:plan`).

Rules for every step:

- Talk to the person in the language of the conversation. When the conversation holds nothing from them but the command, take the language of their earlier messages or of their own CLAUDE.md (user memory or instructions in your context); if nothing says, the plan's language (D-41). One line per event unless something needs them. The plan, briefs and reviews stay in the plan's language; baton's own files in English.
- One shell command per call, never chained with `&&`, `||` or `;`. Write and change files with Write and Edit, never with shell redirections. Use forward slashes in paths.
- Nothing destructive: never `--force`, `-f`, `--force-with-lease`, `-D`, `--delete`, `--mirror`, `reset --hard`, never delete a branch, never remove a worktree with changes, never change the repo's or the person's settings. When a step would need one of these, stop and say so.
- Every state change goes to `state.json` before you end the turn (D-09). Read `state.json` again before acting: never trust memory over the file.
- Decisions follow `PLUGIN/prompts/supervisor.md` (read it when the first stop comes). Its table is the only authority; this skill does not repeat it.
- The app's tools named below (`start_session`, `get_session`, `stop_session`, `bind_pr`, `wrap_up`, PushNotification) often arrive deferred: when one is listed only by name, load it with ToolSearch (`select:<name>`) before deciding you do not have it.

## Files

| Path | Written by | Holds |
|---|---|---|
| `<checkout>/.claude/baton.json` | setup, or step 1 | the repo profile |
| `<checkout>/.claude/runs/<run>/state.json` (**runDir**) | you | the run's state, shaped like `PLUGIN/templates/state.json` |
| `runDir/decisions.md` | you | one table row per supervisor decision or escalation |
| `runDir/report.md` | you, at the end | from `PLUGIN/templates/report.md` |
| `<checkout>/.claude/runs/findings.jsonl` | you | one JSON line per finding of a `NO` review, across plans |
| `<worktree>/.claude/runs/<run>/` (**workerRunDir**) | you: `plan.md`, `implementer.md`, `reviewer.md`, `brief-<part>.md`; the implementer: `result-<part>.md`, `review-<part>-r<n>.md` | everything the implementer session reads and writes, inside its own folder (D-04, D-15) |

`<checkout>` is `git rev-parse --show-toplevel` of this chat's folder. The worktree is `<checkout>/.claude/worktrees/baton-<run>`.

## 1. Preflight

1. **Repo.** `git rev-parse --show-toplevel` and `git rev-parse --verify HEAD` must pass; otherwise say "baton needs a git repository with at least one commit" and stop. `git status --porcelain`: changes in the checkout are said in one line, never block (the plan works in its own worktree).
2. **Mode.** This chat must run in **auto** permission mode: the implementer session inherits it, and in any other mode it would stop on every dialog. Check it with `mcp__ccd_session_mgmt__get_session` for this session (its `permissionMode`); without that tool, from your context. If it is not auto, say so in one line ("switch this chat to auto mode, then run it again") and stop; with `--dry-run`, warn and go on.
3. **Sessions.** Without the app's `start_session` tool (`mcp__ccd_session__start_session`) baton cannot launch: say it needs the Claude desktop app's Code tab and stop; `--dry-run` goes on.
4. **Profile.** Read `.claude/baton.json`. If it is missing, read the repo as `PLUGIN/skills/setup/detect.md` says, write the profile with the detected keys only (no question, D-08; `roles` only when a repo skill was detected, holding only `skills`, never a default `model` or `effort`, D-39), and say what you found in one line. Defaults for absent keys: detect.md's table and `PLUGIN/templates/baton.json`.
5. **The plan.** Read the file given. Take from it:
   - **Title**: the first `#` heading when it is the only level-1 heading; else the file name.
   - **Options**: the line that starts with `baton:` outside HTML comments, `key=value` pairs: `mode` (`cheap|normal|thorough`), `delivery` (`branch|pr|merge|none`), `branch`, `base`. Unknown keys: say them, ignore them.
   - **Already decided**: the section whose heading reads "Already decided", "Ya decidido", "Decided" or "Decisiones".
   - **Parts**: headings that start with `Part`, `Parte`, `Phase`, `Fase`, `Step` or `Paso` followed by an id (a letter or a number) and an optional title after `—`, `-`, `:` or `·`. A heading whose section holds deeper part headings is a container, not a part. Ids must be unique; a plan with no part headings is one part `A`, its whole text.
   - **Criteria** of each part: the list under a heading, bold line or label ending in a colon that says Acceptance, Aceptación, Criteria, Criterios, Done when, Verification or Verificación. A part with none: say it; the reviewer then checks the part's text.
   - **Pauses**: a heading or a line that starts with Pause, Pausa, Stop here, Para aquí, Human decision or Decisión humana marks `pauseBefore` on the next part.
6. **Run id.** The plan's file name without extension, lowercased, every run of other characters turned into `-`, cut to 18 characters. The plan's **earlier runs** are the `.claude/runs/*/state.json` whose `plan` is this plan's path; look at the latest. `running`, `waiting` or `done-not-delivered`: the plan is still open (say so, point to `/baton:status`, stop). `dry-run` with no commits on its branch beyond its `baseSha`: reuse its id, branch and worktree. Anything else (`delivered`, `stopped`, a dry run whose branch got commits): a new run, id suffixed `-2`, `-3`… (the folder is new; the branch is chosen in step 2).
7. **Roles.** Mode `normal` takes `roles` from the profile; `cheap` and `thorough` overlay `modes.<mode>` on them. Implementer model `inherit` means the coordinator's own model.
8. **Delivery.** The plan's `delivery=` or the profile's. `pr` becomes `branch` when there is no `origin` remote or `gh auth status` fails; say why.
9. **Say it**, in one line, then go on without asking (D-08): parts and pauses, branch and base, gates, delivery, models. Example: "3 parts (pause before C) on feat/login from main · gates npm test · delivery pr · implementer inherit/high, reviewer sonnet/medium."

## 2. Branch and worktree

1. **Base**: the plan's `base=`, else the profile's, else the checkout's current branch. `git rev-parse --verify <base>` must pass; failing, say and stop. `baseSha` is that commit for a new branch, and `git merge-base <base> <branch>` for an existing one (step 2 decides which), so the run's commits are the branch's own (D-34).
2. **Branch**, the first that applies (D-28):
   - the plan's `branch=`: that branch, which must exist locally or as `origin/<branch>`;
   - the latest earlier run of this plan had a branch that still exists (locally or as `origin/<branch>`) and is **not done with**: `git branch --list <branch> --merged <base>` prints nothing (not merged), or `gh pr list --head <branch> --state open --json number,url` lists an open pull request. Then the same plan goes back to its same branch, so an open pull request is updated, never doubled;
   - else `<branchPrefix><run>`. When that branch exists already: if `git rev-list --count <base>..<branch>` is 0 reuse it; otherwise stop and say "the branch has work: rename the plan or continue it with `baton: branch=<branch>`".
3. **Iteration**: 1 + the number of earlier `runDir`s in `.claude/runs/*/state.json` with the same `branch`. From iteration 2, say it in step 1.9's line with the pull request when there is one ("iteration 2 on feat/x, PR #4 open").
4. **Exclude**: `git rev-parse --git-common-dir`, then make sure `<common-dir>/info/exclude` holds the lines `/.claude/worktrees/` and `/.claude/runs/` (Read it; add what is missing with Edit, or Write it if absent).
5. **Worktree**: when the branch is already checked out in an earlier baton worktree (`git worktree list --porcelain` shows it under `.claude/worktrees/baton-…`), use that worktree as it is and record its path. Otherwise, from the checkout: `git worktree add -b <branch> .claude/worktrees/baton-<run> <base>` for a new branch, `git worktree add .claude/worktrees/baton-<run> <branch>` for an existing one. A failure (the branch checked out elsewhere, a path in use) stops the launch with git's message.
6. **Install**: the profile's `install` runs inside the implementer session as the first step of part A (the brief says so), not here: that keeps the launch in this turn, where the session may be started (D-16).

## 3. State and brief

1. **workerRunDir**: create `<worktree>/.claude/runs/<run>/` and copy into it, one command each, `PLUGIN/prompts/implementer.md` as `implementer.md`, `PLUGIN/agents/reviewer.md` as `reviewer.md`, and the plan file as `plan.md` (the reviewer reads this copy, so an uncommitted plan works too). Write `settled.md` there with the line `# Settled while the plan ran` (D-37).
2. **state.json** in `runDir`, as `PLUGIN/templates/state.json` shows: `status` `running` (or `dry-run`), parts with `pauseBefore`, `current` the first part, `messagesSinceUser` 0, `presses` with the launch (`{ "at": <now>, "what": "launch" }`), and the roles, gates, delivery and install settled above.
3. **decisions.md** in `runDir`: the header `| When | Part | Stop | Decision | Why |` and its separator line.
4. **The brief** of the first part: read `PLUGIN/templates/brief.md` and write `workerRunDir/brief-<part>.md` with every `{{…}}` replaced (step 5's "Writing a brief"). Then check that no `{{` is left in it.

## 4. The implementer session

Call `start_session` with:

- `initiation: "user_asked"` (this turn is the person's request), `context: "fresh"`, `cwd`: the worktree's absolute path, `use_worktree: false`, `wake_when_done: true`;
- `name: "baton-<run>"`, `title: "baton · <plan title>"` (under 60 characters);
- `model`: the implementer's model, omitted when `inherit`; `effort`: the implementer's effort; no `permission_mode` (it inherits auto);
- `prompt`, with `<workerRunDir>`, `<part>` and the title replaced by their values: "You are baton's implementer for the plan «<title>». Read `<workerRunDir>/implementer.md`, then read and follow `<workerRunDir>/brief-<part>.md`. End every turn with the baton-result block it describes.";
- `background`: "baton runs a written plan part by part. A coordinating chat started this session in the plan's worktree on branch <branch>; it sends one brief per part, reads your result files and answers your questions. Do not push, open pull requests, merge or change branches."

Store the returned session id (`local_…`) and name in `state.worker`, and `updatedAt`. Say one line with a link to the session: "Part A at work in [baton · <title>](#local_<id>). I'll follow it from here and write when something needs you." Then end the turn: never poll, never wait.

With `--dry-run`: write the call you would make (cwd, name, title, model, effort, the prompt with its paths filled in), leave `status: dry-run`, and say how to clean up: `git worktree remove .claude/worktrees/baton-<run>` (the branch stays; a later `/baton:run` of the same plan reuses both).

## 5. The event loop

**Which run.** Every `runDir` whose `state.json` has `status` `running` or `waiting`; the one whose `worker.name` or `worker.sessionId` matches the event's session. A message from the person resets `messagesSinceUser` to 0; if the run is `waiting` for them, their words are the answer (below).

**On each event from the worker session**:

1. Read `workerRunDir/result-<current>.md`. The event quotes the start of the session's report; if it shows a `baton-result` whose `status` or `part` differs from the file, the file is stale. With no result file, or a stale one, send "baton · part <X>: end your turn with the baton-result block and save it as `result-<X>.md`." Twice in a row with no result: escalate.
2. Act on `status`:
   - **done**: check `git -C <worktree> log --oneline <startSha>..HEAD` lists commits and the first non-empty line of the part's last review file in `workerRunDir` reads `Verdict: OK` (or `Veredicto: OK`; ignore a leading code fence); if not, send "baton · part <X> is not reviewed OK yet: run the review loop as your brief says." Otherwise mark the part done (`endSha` from `git -C <worktree> rev-parse HEAD`, rounds, verdict), and add one line to `findings.jsonl` per finding of each `NO` review of the part: `{"plan":"<run>","part":"<X>","round":<n>,"priority":"P2","category":"tests","file":"src/a.js:12","title":"…","at":"<iso time>"}` from its `### F-nn · P · category · file · title` headings. Then:
     - the next part has `pauseBefore`: set `status: waiting`, `waiting: { "kind": "pause", "part": "<next>" }` and escalate "Part <X> done. The plan pauses before part <next>: continue?" with the buttons «Continue with <next>» / «Stop here»;
     - else: write its brief (`startSha` = the worktree's `HEAD` now), set `current`, and send "baton · part <next>: read and follow `<workerRunDir>/brief-<next>.md`.";
     - no part left: step 6.
   - **question**: decide as `supervisor.md` says. A result with `needs: human` always goes to the person. Answered from the plan, the rules or the code: append it to `settled.md` (below), then send "baton · answer from the plan for part <X>: <answer>". Not yours: escalate the question.
   - **blocked** or **failed**: decide as `supervisor.md` says: a retry (two per part at most: "baton · retry part <X>: <what to try>"), a replan (once per part: write `brief-<X>-replan.md`, the original brief plus a section "Replanned by baton's supervisor" with the reason and the change, same criteria; send "baton · part <X> replanned: read and follow `<workerRunDir>/brief-<X>-replan.md`."), or escalate.
3. Record every decision and escalation as a row in `decisions.md` (time, part, what stopped, the decision, one sentence of why), count it in the part's `decisions`, and say it in one line in the chat.
4. **Counting messages.** The app delivers at most 10 messages to other sessions per message the person writes in this chat (a button press counts); events from other sessions do not reset it (D-33). Each message you send to the worker adds 1 to `messagesSinceUser` and sets `lastSentAt`. Before sending one that would make it 10, do not send it (at most 9 go out, one stays in reserve): set `waiting: { "kind": "quota" }` and ask the person for a word to go on, with the button «Continue». Their answer resets the count; then send it.
5. A **message** (not an event) from the worker session is read like a `question` result.

**Escalating** (always the person's, or unsure): set `status: waiting` and `waiting` (`kind`: `question`, `pause`, `blocked`, `publish` or `quota`; the part; the question), add a `presses` entry when the answer comes. Then say one sentence on what is asked and why it is theirs, the question as asked, and offer the likely answers as two or three buttons with `mcp__ccd_turn__wrap_up` (ask + actions) when you have it, else as a plain question. Also send a push notification (PushNotification, under 200 characters) with that sentence. End the turn.

**Settled answers** (D-37): every answer to a question, from the plan or from the person, is appended to `workerRunDir/settled.md` before it is sent, as `- <time> · part <X> · from the plan|from the person · Q: <question> · A: <answer>` (the person's words verbatim). With the plan's "Already decided" it is what the implementer and the reviewer hold as decided.

**The person's answer**: record it in `presses`, set `status: running`, `waiting: null`, and act: append a question's answer to `settled.md`, then forward it **verbatim** as "baton · answer from the person for part <X>: <their words>"; a pause's «Continue» sends the next brief; «Stop here» goes to step 6 with the parts done so far (the rest stay pending, said in the report); a quota word sends the held message.

**Writing a brief** (from `PLUGIN/templates/brief.md`): `{{part}}`, `{{partTitle}}`; `{{plan}}` (repo-relative path) and `{{planCopy}}` (`workerRunDir/plan.md`); `{{worktree}}`, `{{branch}}`, `{{base}}`, `{{baseSha}}`, `{{startSha}}`, `{{workerRunDir}}`; `{{iteration}}` and `{{iterationNote}}` (empty, or " — continuing branch <branch> from an earlier run" for iteration 2+); `{{rules}}`: the profile's rule files as a list plus its `notes`, ending "Where a rule of this repo and this brief disagree, the rule wins."; `{{implementerSkills}}` and `{{reviewerSkills}}` (comma-separated, or "none"); `{{gates}}` (each in backticks, or "none declared"); `{{install}}` (the command in backticks for part A, else "none"); `{{alreadyDecided}}`, `{{partText}}` and `{{criteria}}` copied from the plan as written; `{{reviewRounds}}`, `{{reviewerModel}}`, `{{reviewerEffort}}`; `{{extra}}`: anything else this part needs (empty when nothing). Never leave a `{{` behind.

## 6. Delivery

1. **Collect.** Copy every file of `workerRunDir` into `runDir` (one shell command: `cp -r <workerRunDir>/. <runDir>/` in Bash, `Copy-Item <workerRunDir>/* <runDir>` in PowerShell).
2. **Worktree.** `git worktree remove .claude/worktrees/baton-<run>` from the checkout, without `--force`. If it refuses (changes not committed) keep it and say so; if git let go of it but its folder stays because the implementer session still holds it, say so. The branch always stays. Record the outcome in `state.delivery.worktree`: `removed`, `removed; its empty folder stays while the implementer session holds it` or `kept: <why>` (D-34).
3. **Report.** Write `runDir/report.md` from `PLUGIN/templates/report.md` (step 7), final except a new pull request's URL: it is the pull request's body or comment.
4. **Publish**, by the delivery settled in step 1:
   - With `humanBeforePublish` and delivery `pr` or `merge`: escalate first (`waiting.kind: publish`, buttons «Publish» / «Leave the branch»).
   - `branch` or `none`: nothing.
   - `pr`, from the checkout: `git push -u origin <branch>`; then `gh pr list --head <branch> --state open --json number,url`. One: put its URL in the report, then `gh pr comment <number> --body-file <runDir>/report.md` (the push already updated it). None: `gh pr create --base <base> --head <branch> --title "<plan title>" --body-file <runDir>/report.md`, then put the new URL in the report and `gh pr edit <number> --body-file <runDir>/report.md`, so the body is the final report (D-38). Then bind the pull request to the app with `mcp__ccd_pr__bind_pr` when you have it ("already bound" is fine).
   - `merge`: only when `git status --porcelain` in the checkout is empty and `git branch --show-current` is the base; otherwise deliver as `branch` and say why. `git merge --no-ff <branch>`; if it fails and `git rev-parse -q --verify MERGE_HEAD` passes, `git merge --abort`, and say "the branch does not merge cleanly: your checkout is as it was, the branch stays".
   - A step that fails stops the delivery: say which and its message, `status: done-not-delivered` (the branch has the work; `/baton:status continue` retries from that step).
5. `status: delivered`, and `state.delivery` complete: `mode`, `url`, `comment` when one was posted, `worktree`.

## 7. Report

Fill `PLUGIN/templates/report.md`: the parts with their results, the answers of `settled.md`, review rounds and gates (from the result files); commits from `git log --oneline <baseSha>..<branch>` in the checkout, those before the first part's `startSha` marked "(earlier iteration)"; the reviews table from the review files; the decisions table from `decisions.md`; repeated findings: a category that appears in two or more plans of `findings.jsonl` gets one proposed rule for the repo's CLAUDE.md, in the repo's language; cost: the `reviewer_usage` lines, and "see the session's usage" for the implementer; "What needed you": one line per `presses` entry. After a pull request, update its delivery line with the URL. Then one line in the chat with the outcome and the report's path, and a push notification.

## 8. Resuming

When the person says "sigue", "continue" or runs `/baton:status` with a run `running` or `waiting`, or this chat reopens with work pending:

1. Read `state.json`. `waiting` set: ask that question again, as an escalation.
2. Otherwise read `workerRunDir/result-<current>.md`: a result newer than the last message you sent is an event: act on it (step 5).
3. Otherwise look for the worker with `mcp__ccd_session_mgmt__get_session` (`state.worker.sessionId`). Alive and idle: send "baton · continue part <X> from your brief `<path>`; check `git log` for what is done." Missing or archived: start a new implementer session as in step 4 with the same brief (this is the person's turn, so it may be started) and store its id. Working: say so and wait.
4. If you no longer have these instructions in context (a compaction), load this skill again before acting on any event.
