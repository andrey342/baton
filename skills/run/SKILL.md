---
name: run
description: >-
  Launch a written plan from this chat. Creates the plan's worktree and branch, writes one brief for all its parts and starts one nested implementer session in auto mode; from then on /baton:event handles every turn end of that session (review OK, questions within a closed authority table, delivery as branch, pull request or merge, with a report). Use when the person asks to run, launch or execute a plan file, e.g. "run docs/plans/x.md", "ejecuta el plan", "lanza el plan docs/plans/x.md", "baton, run this plan"; and to test a launch without sessions with --dry-run.
argument-hint: "<plan.md> [--dry-run]"
---

# /baton:run

Arguments: `$ARGUMENTS`

The plugin's files: `${CLAUDE_PLUGIN_ROOT}` (below, **PLUGIN**). You are the **coordinator**: you prepare and launch here; the implementer session does the work, and `/baton:event` (`PLUGIN/skills/event/SKILL.md`) says what you do each time it ends a turn. Nobody else watches the plan: what you do not write to the run's files is lost when this chat compacts.

- With a plan path: launch it (steps 1–4).
- With `--dry-run`: steps 1–3 in full, then say what step 4 would do; never call `start_session`.
- With no arguments and a run `running` or `waiting` in `.claude/runs/*/state.json`: follow "Resuming" in `/baton:event`.
- With no arguments and no active run: look for plans (`docs/plans/*.md`, or the folder the repo's rules name, leaving out `TEMPLATE.md`). Exactly one: offer it in one line ("Run docs/plans/x.md?", with a button when you have `wrap_up`) and launch it on the person's yes. Several: list them and ask which. None: say how to write one (`/baton:plan`).

Rules for every step:

- **Work in batches.** Every call costs a full reading of this chat, so calls that do not depend on each other go in one message: the batches below are one message each. If your app asks for a task list and a wrap-up, send `update_plan` inside the first batch and `wrap_up` inside the last, never in a message of their own.
- Talk to the person in the language of the conversation. When the conversation holds nothing from them but the command, take the language of their earlier messages or of their own CLAUDE.md (user memory or instructions in your context); if nothing says, the plan's language (D-41). One line per event unless something needs them. The plan, the brief and the reviews stay in the plan's language; baton's own files in English.
- One shell command per call, never chained with `&&`, `||` or `;`. Write and change files with Write and Edit, never with shell redirections. Use forward slashes in paths.
- Nothing destructive: never `--force`, `-f`, `--force-with-lease`, `-D`, `--delete`, `--mirror`, `reset --hard`, never delete a branch, never remove a worktree with changes, never change the repo's or the person's settings. When a step would need one of these, stop and say so.
- Every state change goes to `state.json` before you end the turn (D-09).
- The app's tools baton uses (`start_session`, `get_session`, `stop_session`, `bind_pr`, `wrap_up`, SendMessage, PushNotification) often arrive deferred: load every one that is listed only by name with a single ToolSearch (`select:<name>,<name>,…`) in the first batch, before deciding you do not have one.

## Files

| Path | Written by | Holds |
|---|---|---|
| `<checkout>/.claude/baton.json` | setup, or step 1 | the repo profile |
| `<checkout>/.claude/runs/<run>/state.json` (**runDir**) | you | the run's state, shaped like `PLUGIN/templates/state.json` |
| `runDir/decisions.md` | you | one table row per supervisor decision or escalation |
| `runDir/report.md` | you, at the end | from `PLUGIN/templates/report.md` |
| `<checkout>/.claude/runs/findings.jsonl` | you | one JSON line per finding of a `NO` review, across plans |
| `<worktree>/.claude/runs/<run>/` (**workerRunDir**) | you: `plan.md`, `implementer.md`, `reviewer.md`, `brief.md`, `settled.md`, a `brief-<part>-replan.md` when a part is replanned; the implementer: `result-<part>.md`, `review-<part>-r<n>.md` | everything the implementer session reads and writes, inside its own folder (D-04, D-15) |

`<checkout>` is `git rev-parse --show-toplevel` of this chat's folder. The worktree is `<checkout>/.claude/worktrees/baton-<run>`.

## 1. Preflight

**Batch 1**, one message: the ToolSearch above; `git rev-parse --show-toplevel`; `git rev-parse --verify HEAD`; `git status --porcelain`; `git branch --show-current`; Read `.claude/baton.json`; Read the plan file; Glob `.claude/runs/*/state.json`; `date -u +%Y-%m-%dT%H:%M:%SZ`.

1. **Repo.** The two `rev-parse` must pass; otherwise say "baton needs a git repository with at least one commit" and stop. Changes in the checkout are said in one line, never block (the plan works in its own worktree).
2. **Mode.** This chat must run in **auto** permission mode: the implementer session inherits it, and in any other mode it would stop on every dialog. Check it with `mcp__ccd_session_mgmt__get_session` for this session (its `permissionMode`) in batch 2; without that tool, from your context. If it is not auto, say so in one line ("switch this chat to auto mode, then run it again") and stop; with `--dry-run`, warn and go on.
3. **Sessions.** Without the app's `start_session` tool (`mcp__ccd_session__start_session`) baton cannot launch: say it needs the Claude desktop app's Code tab and stop; `--dry-run` goes on.
4. **Profile.** If `.claude/baton.json` is missing, read the repo as `PLUGIN/skills/setup/detect.md` says (its reads go in batch 2), write the profile with the detected keys only (no question, D-08; `roles` only when a repo skill was detected, holding only `skills`, never a default `model` or `effort`, D-39), and say what you found in one line. Defaults for absent keys: detect.md's table and `PLUGIN/templates/baton.json`.
5. **The plan.** From the file:
   - **Title**: the first `#` heading when it is the only level-1 heading; else the file name.
   - **Options**: the line that starts with `baton:` outside HTML comments, `key=value` pairs: `mode` (`cheap|normal|thorough`), `delivery` (`branch|pr|merge|none`), `branch`, `base`. Unknown keys: say them, ignore them.
   - **Already decided**: the section whose heading reads "Already decided", "Ya decidido", "Decided" or "Decisiones".
   - **Parts**: headings that start with `Part`, `Parte`, `Phase`, `Fase`, `Step` or `Paso` followed by an id (a letter or a number) and an optional title after `—`, `-`, `:` or `·`. A heading whose section holds deeper part headings is a container, not a part. Ids must be unique; a plan with no part headings is one part `A`, its whole text.
   - **Criteria** of each part: the list under a heading, bold line or label ending in a colon that says Acceptance, Aceptación, Criteria, Criterios, Done when, Verification or Verificación. A part with none: say it; the reviewer then checks the part's text.
   - **Pauses**: a heading or a line that starts with Pause, Pausa, Stop here, Para aquí, Human decision or Decisión humana marks `pauseBefore` on the next part.
6. **Run id.** The plan's file name without extension, lowercased, every run of other characters turned into `-`, cut to 18 characters. The plan's **earlier runs** are the `state.json` files from the Glob whose `plan` is this plan's path (read the latest in batch 2). `running`, `waiting` or `done-not-delivered`: the plan is still open (say so, point to `/baton:status`, stop). `dry-run` with no commits on its branch beyond its `baseSha`: reuse its id, branch and worktree. Anything else (`delivered`, `stopped`, a dry run whose branch got commits): a new run, id suffixed `-2`, `-3`… (the folder is new; the branch is chosen in step 2).
7. **Roles.** Mode `normal` takes `roles` from the profile; `cheap` and `thorough` overlay `modes.<mode>` on them. Implementer model `inherit` means the coordinator's own model.
8. **Delivery.** The plan's `delivery=` or the profile's. `pr` becomes `branch` when there is no `origin` remote or `gh auth status` fails (both in batch 2, only for `pr`); say why.

**Batch 2**, one message: `get_session`; Read `PLUGIN/templates/state.json` and `PLUGIN/templates/brief.md`; the latest earlier `state.json` of this plan, if any; detect.md and its reads when there is no profile; `git rev-parse --git-common-dir`; `git worktree list --porcelain`; for each candidate branch of step 2.2, `git branch --list <branch>` (and `git branch --list <branch> --merged <base>`, `gh pr list --head <branch> --state open --json number,url` when an earlier run had it); for `pr`, `git remote get-url origin` and `gh auth status`.

9. **Say it**, in one line, then go on without asking (D-08): parts and pauses, branch and base, gates, delivery, models. Example: "3 parts (pause before C) on feat/login from main · gates npm test · delivery pr · implementer inherit/high, reviewer sonnet/medium."

## 2. Branch and worktree

1. **Base**: the plan's `base=`, else the profile's, else the checkout's current branch. It must resolve (`git rev-parse --verify <base>`); failing, say and stop. `baseSha` is that commit for a new branch, and `git merge-base <base> <branch>` for an existing one (step 2 decides which), so the run's commits are the branch's own (D-34).
2. **Branch**, the first that applies (D-28):
   - the plan's `branch=`: that branch, which must exist locally or as `origin/<branch>`;
   - the latest earlier run of this plan had a branch that still exists (locally or as `origin/<branch>`) and is **not done with**: not merged into the base (`--merged` prints nothing) or with an open pull request. Then the same plan goes back to its same branch, so an open pull request is updated, never doubled;
   - else `<branchPrefix><run>`. When that branch exists already: if `git rev-list --count <base>..<branch>` is 0 reuse it; otherwise stop and say "the branch has work: rename the plan or continue it with `baton: branch=<branch>`".
3. **Iteration**: 1 + the number of earlier `runDir`s with the same `branch`. From iteration 2, say it in step 1.9's line with the pull request when there is one ("iteration 2 on feat/x, PR #4 open").

**Batch 3**, one message: the profile's Write when step 1.4 wrote one; Read `<common-dir>/info/exclude`; `git rev-parse --verify <base>`, and `git merge-base <base> <branch>` for an existing branch; the worktree:

4. **Worktree**: when the branch is already checked out in an earlier baton worktree (`git worktree list` shows it under `.claude/worktrees/baton-…`), use that worktree as it is. Otherwise, from the checkout: `git worktree add -b <branch> .claude/worktrees/baton-<run> <base>` for a new branch, `git worktree add .claude/worktrees/baton-<run> <branch>` for an existing one. A failure (the branch checked out elsewhere, a path in use) stops the launch with git's message.
5. **Install**: the profile's `install` runs inside the implementer session as the first step of part A (the brief says so), not here: that keeps the launch in this turn, where the session may be started (D-16).

## 3. State and brief

**Batch 4**, one message, all with Write and Edit (Write creates the folders):

1. **Exclude**: make sure `<common-dir>/info/exclude` holds the lines `/.claude/worktrees/` and `/.claude/runs/` (Edit to add what is missing, or Write it if absent).
2. **settled.md** in workerRunDir (`<worktree>/.claude/runs/<run>/`), with the line `# Settled while the plan ran` (D-37).
3. **brief.md** in workerRunDir, from `PLUGIN/templates/brief.md` with every `{{…}}` replaced ("Filling the brief" below), one brief for the whole plan. Check your text before writing it: no `{{` may be left.
4. **state.json** in runDir, as `PLUGIN/templates/state.json` shows: `status` `running` (or `dry-run`), parts with `pauseBefore`, the first part `working` with `startSha` = `baseSha` (or the worktree's `HEAD` for an existing branch), `current` the first part, `messagesSinceUser` 0, `presses` with the launch (`{ "at": <now>, "what": "launch" }`), and the roles, gates, delivery and install settled above.
5. **decisions.md** in runDir: the header `| When | Part | Stop | Decision | Why |` and its separator line.

**Batch 5**, one message: copy into workerRunDir, one command each, `PLUGIN/prompts/implementer.md` as `implementer.md`, `PLUGIN/agents/reviewer.md` as `reviewer.md`, and the plan file as `plan.md` (the reviewer reads this copy, so an uncommitted plan works too).

**Filling the brief**: `{{title}}`; `{{plan}}` (repo-relative path) and `{{planCopy}}` (`workerRunDir/plan.md`); `{{worktree}}`, `{{branch}}`, `{{base}}`, `{{baseSha}}`, `{{workerRunDir}}`; `{{iteration}}` and `{{iterationNote}}` (empty, or " — continuing branch <branch> from an earlier run" for iteration 2+); `{{rules}}`: the profile's rule files as a list plus its `notes`, ending "Where a rule of this repo and this brief disagree, the rule wins."; `{{implementerSkills}}` and `{{reviewerSkills}}` (comma-separated, or "none"); `{{gates}}` (each in backticks, or "none declared"); `{{install}}` (the command in backticks, or "none"); `{{alreadyDecided}}` copied from the plan as written; `{{parts}}`: for each part, `### Part <id> — <title>`, its text as the plan writes it, and `**Acceptance**` with its criteria (or "none written: the reviewer checks the part's text"); `{{reviewRounds}}`, `{{reviewerModel}}`, `{{reviewerEffort}}`; `{{extra}}`: anything else the plan needs (empty when nothing).

## 4. The implementer session

**Batch 6**: call `start_session` with:

- `initiation: "user_asked"` (this turn is the person's request), `context: "fresh"`, `cwd`: the worktree's absolute path, `use_worktree: false`, `wake_when_done: true`;
- `name: "baton-<run>"`, `title: "baton · <plan title>"` (under 60 characters);
- `model`: the implementer's model, omitted when `inherit`; `effort`: the implementer's effort; no `permission_mode` (it inherits auto);
- `prompt`, with `<workerRunDir>`, `<part>`, `<startSha>` and the title replaced by their values: "You are baton's implementer for the plan «<title>». Read `<workerRunDir>/implementer.md`, then do part <part> from <startSha>: read and follow `<workerRunDir>/brief.md`. End every turn with the baton-result block it describes.";
- `background`: "baton runs a written plan part by part. A coordinating chat started this session in the plan's worktree on branch <branch>; it names one part at a time, reads your result files and answers your questions. Do not push, open pull requests, merge or change branches."

**Batch 7**, one message: Edit `state.json` with the returned session id (`local_…`) and name in `state.worker` and `updatedAt`, and the `wrap_up` if your app asks for one. Then say one line with a link to the session: "Part A at work in [baton · <title>](#local_<id>). I'll follow it from here and write when something needs you." End the turn: never poll, never wait. Each turn end of that session wakes this chat: handle it with `/baton:event`.

With `--dry-run`: write the call you would make (cwd, name, title, model, effort, the prompt with its paths filled in), leave `status: dry-run`, and say how to clean up: `git worktree remove .claude/worktrees/baton-<run>` (the branch stays; a later `/baton:run` of the same plan reuses both).
