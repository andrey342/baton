---
name: run
description: >-
  Launch a written plan from this chat, in two turns of the person. First a proposal: baton reads the plan, proposes a model and effort for the implementer, reviewer and Critic of each part with the reason and the plan section behind it, and waits for the person's yes or changes; nothing is created. Then, on the yes, the launch: the plan's worktree and branch, one brief, and the implementer session in auto mode; from then on /baton:event handles every turn end (review OK, questions within a closed authority table, delivery as branch, pull request or merge, with a report). Use when the person asks to run, launch or execute a plan file, e.g. "run docs/plans/x.md", "ejecuta el plan", "lanza el plan docs/plans/x.md", "baton, run this plan"; when they answer baton's model table ("sí, lanza", "baja P3 a Sonnet"); and to see the table without creating anything with --dry-run.
argument-hint: "<plan.md> [--dry-run]"
---

# /baton:run

Arguments: `$ARGUMENTS`

The plugin's files: `${CLAUDE_PLUGIN_ROOT}` (below, **PLUGIN**). You are the **coordinator**: you propose, and on the person's yes you launch here; the implementer session does the work, and `/baton:event` (`PLUGIN/skills/event/SKILL.md`) says what you do each time it ends a turn. Nobody else watches the plan: what you do not write to the run's files is lost when this chat compacts.

A run has three moments (plan 0.3, D1): the **proposal** (steps 1–2, this turn), the **launch** (step 4, the turn of the person's yes, which is what lets the app start sessions) and the **events** (`/baton:event`).

- With a plan path: the proposal (steps 1–2), then end the turn.
- With `--dry-run`: steps 1–2 without writing anything, then say what the launch would do. A dry run creates no branch, worktree, file or session, and never calls `start_session`.
- The person's answer to a proposal (a button or their words, while a run is `proposed`): step 3.
- With no arguments and a run `proposed` in `.claude/runs/*/state.json`: when it holds `proposal.approvedAt` (approved, but the launch stopped), the launch (step 4), since this is the person's turn; otherwise show its table again and ask, as step 2 ends. With a run `running`, `waiting`, `paused` or `closing`: follow "Resuming" in `/baton:event`.
- With no arguments and no open run: look for plans (`docs/plans/*.md`, or the folder the repo's rules name, leaving out `TEMPLATE.md`). Exactly one: offer it in one line ("Run docs/plans/x.md?", with a button when you have `wrap_up`) and propose it on the person's yes. Several: list them and ask which. None: say how to write one (`/baton:plan`).

Rules for every step:

- **No session starts without an approved table.** `start_session` is called only when `state.json` holds `proposal.approvedAt`, written from the person's own yes in this chat. No option, mode, profile key or plan line skips it; the models in the plan and the profile are only where the proposal starts.
- **Work in batches.** Every call costs a full reading of this chat, so calls that do not depend on each other go in one message: the batches below are one message each. If your app asks for a task list and a wrap-up, send `update_plan` inside the first batch and `wrap_up` inside the last, never in a message of their own.
- Talk to the person in the language of the conversation. When the conversation holds nothing from them but the command, take the language of their earlier messages or of their own CLAUDE.md (user memory or instructions in your context); if nothing says, the plan's language (D-41). One line per event unless something needs them. The plan, the brief and the reviews stay in the plan's language; baton's own files in English. The model table and its buttons are in the person's language.
- One shell command per call, never chained with `&&`, `||` or `;`. Write and change files with Write and Edit, never with shell redirections. Use forward slashes in paths.
- Nothing destructive: never `--force`, `-f`, `--force-with-lease`, `-D`, `--delete`, `--mirror`, `reset --hard`, never delete a branch, never remove a worktree with changes, never change the repo's or the person's settings. When a step would need one of these, stop and say so.
- Every state change goes to `state.json` before you end the turn (D-09).
- The app's tools baton uses (`start_session`, `get_session`, `stop_session`, `bind_pr`, `wrap_up`, SendMessage, PushNotification) often arrive deferred: load every one that is listed only by name with a single ToolSearch (`select:<name>,<name>,…`) in the first batch, before deciding you do not have one.

## Files

| Path | Written by | Holds |
|---|---|---|
| `<checkout>/.claude/baton.json` | setup, or the launch | the repo profile |
| `<checkout>/.claude/runs/<run>/state.json` (**runDir**) | you, from the proposal on | the run's state, shaped like `PLUGIN/templates/state.json` (version 2; "State versions" in `/baton:event` for version 1) |
| `runDir/decisions.md` | you, from the approval on | one table row per approval, supervisor decision or escalation |
| `runDir/report.md` | you, at the end | from `PLUGIN/templates/report.md` |
| `<checkout>/.claude/runs/findings.jsonl` | you | one JSON line per finding of a `NO` review, across plans |
| `<worktree>/.claude/runs/<run>/` (**workerRunDir**) | you: `plan.md`, `implementer.md`, `reviewer.md`, `brief.md`, `settled.md`, a `brief-<part>-replan.md` when a part is replanned; the implementer: `result-<part>.md`, `review-<part>-r<n>.md` | everything the implementer session reads and writes, inside its own folder (D-04, D-15) |

`<checkout>` is `git rev-parse --show-toplevel` of this chat's folder. The worktree is `<checkout>/.claude/worktrees/baton-<run>`.

## 1. Preflight

**Batch 1**, one message: the ToolSearch above; `git rev-parse --show-toplevel`; `git rev-parse --verify HEAD`; `git status --porcelain`; `git branch --show-current`; Read `.claude/baton.json`; Read the plan file; Glob `.claude/runs/*/state.json`; `date -u +%Y-%m-%dT%H:%M:%SZ`.

1. **Repo.** The two `rev-parse` must pass; otherwise say "baton needs a git repository with at least one commit" and stop. Changes in the checkout are said in one line, never block (the plan works in its own worktree).
2. **Mode.** The launch needs this chat in **auto** permission mode: the implementer session inherits it, and in any other mode it would stop on every dialog. Check it with `mcp__ccd_session_mgmt__get_session` for this session (its `permissionMode`) in batch 2; without that tool, from your context. Not auto: the proposal goes on and says in its last line "switch this chat to auto mode before you approve"; the launch checks again.
3. **Sessions.** Without the app's `start_session` tool (`mcp__ccd_session__start_session`) baton cannot launch: the proposal goes on and says baton needs the Claude desktop app's Code tab to launch; the launch stops there.
4. **Profile.** If `.claude/baton.json` is missing, read the repo as `PLUGIN/skills/setup/detect.md` says (its reads go in batch 2) and keep the detected keys for the launch, which writes them (`roles` only when a repo skill was detected, holding only `skills`, never a default `model` or `effort`, D-39); the proposal says what you found in its options line. Defaults for absent keys: detect.md's table and `PLUGIN/templates/baton.json`.
5. **The plan.** From the file:
   - **Title**: the first `#` heading when it is the only level-1 heading; else the file name.
   - **Options**: the line that starts with `baton:` outside HTML comments, `key=value` pairs: `mode` (`cheap|normal|thorough`), `models` (starting points for implementers, `<part>:<model>[/<effort>]` separated by commas, e.g. `models=B:opus/high,C:sonnet`), `delivery` (`branch|pr|merge|none`), `branch`, `base`. Unknown keys: say them, ignore them.
   - **Already decided**: the section whose heading reads "Already decided", "Ya decidido", "Decided" or "Decisiones".
   - **Parts**: headings that start with `Part`, `Parte`, `Phase`, `Fase`, `Step` or `Paso` followed by an id (a letter or a number) and an optional title after `—`, `-`, `:` or `·`. A heading whose section holds deeper part headings is a container, not a part. Ids must be unique; a plan with no part headings is one part `A`, its whole text.
   - **Criteria** of each part: the list under a heading, bold line or label ending in a colon that says Acceptance, Aceptación, Criteria, Criterios, Done when, Verification or Verificación. A part with none: say it; the reviewer then checks the part's text.
   - **Pauses**: a heading or a line that starts with Pause, Pausa, Stop here, Para aquí, Human decision or Decisión humana marks `pauseBefore` on the next part.
6. **Run id.** The plan's file name without extension, lowercased, every run of other characters turned into `-`, cut to 18 characters. The plan's **earlier runs** are the `state.json` files from the Glob whose `plan` is this plan's path (read the latest in batch 2). `proposed`: reuse its folder and id; the new table replaces the old one, with `proposal.revisions` + 1 and `approvedAt` and `words` back to null. `running`, `waiting`, `paused`, `closing` or `done-not-delivered`: the plan is still open (say so, point to `/baton:status`, stop). `dry-run` (a 0.2 dry run, version 1) with no commits on its branch beyond its `baseSha`: reuse its id, branch and worktree. Anything else (`delivered`, `stopped`, a 0.2 dry run whose branch got commits): a new run, id suffixed `-2`, `-3`… (the folder is new; the branch is chosen below).
7. **Starting points.** For each role, the profile's `models.start` (a version 1 profile: its `roles`), with `modes.<mode>` laid over it for `cheap` and `thorough`, and the plan's `models=` over that for the parts it names. `inherit` means this chat's model. The proposal starts here and moves away with a reason.
8. **Delivery.** The plan's `delivery=` or the profile's. `pr` becomes `branch` when there is no `origin` remote or `gh auth status` fails (both in batch 2, only for `pr`); say why.
9. **Base and branch.** Decided now, created only at the launch:
   - **Base**: the plan's `base=`, else the profile's, else the checkout's current branch. It must resolve (`git rev-parse --verify <base>`, batch 2); failing, say and stop.
   - **Branch**, the first that applies (D-28): the plan's `branch=`, which must exist locally or as `origin/<branch>`; the branch of the latest earlier run of this plan when it still exists (locally or as `origin/<branch>`) and is **not done with**: not merged into the base (`--merged` prints nothing) or with an open pull request, so an open pull request is updated, never doubled; else `<branchPrefix><run>`. When that last one exists already: if `git rev-list --count <base>..<branch>` is 0 reuse it; otherwise stop and say "the branch has work: rename the plan or continue it with `baton: branch=<branch>`".
   - **Iteration**: 1 + the number of earlier `runDir`s with the same `branch`; from iteration 2 the options line says it, with the pull request when there is one ("iteration 2 on feat/x, PR #4 open").

**Batch 2**, one message: `get_session` (this chat: its `model` and `permissionMode`); Read `PLUGIN/prompts/models.md`; the latest earlier `state.json` of this plan, if any; detect.md and its reads when there is no profile; `git rev-parse --verify <base>`; for each candidate branch of step 9, `git branch --list <branch>` (and `git branch --list <branch> --merged <base>`, `gh pr list --head <branch> --state open --json number,url` when an earlier run had it); for `pr`, `git remote get-url origin` and `gh auth status`.

## 2. The proposal

Analyse every part as `PLUGIN/prompts/models.md` says: its five axes with the plan section that shows each, a row for its implementer, reviewer and Critic (model, effort, skills), a weight and one reason. `sessions: "per-plan"` in the profile keeps one implementer session for the plan: the table then has one implementer model for every row (D3).

**The ceiling.** This chat's model comes from `get_session` (without it, from your context). An implementer row on a model above it cannot be launched from this chat (the app ignores the request): mark that row "cannot be launched from this chat (<this chat's model>)", and say in the Coordinator line the two ways out, a chat on that model or a lower row. Reviewers and Critics have no ceiling (D-61).

**The table**, in the person's language, one row per part, plus a row "Closing" when the profile's `closing` is not empty:

```text
| Part | Implementer   | Reviewer (skills)       | Critic    | Weight | Reason |
| A    | Sonnet medium | Sonnet medium (—)       | —         | S      | Steps the plan prescribes; a mistake is cheap (Part A) |
| B    | Opus medium   | Opus high (repo-review) | Opus high | L      | Authorization and a public contract (§3, Part B) |
Weight: B is ~70 % of the plan; Sonnet high on B would save ~35 %.
Coordinator: this chat (Opus 5.5). It can launch every row.
Options: delivery pr · publish without asking (the repo asks for a PR) · archive verified sessions: no · iteration 1 on baton/x from main
```

Every reason cites the plan section it rests on. The options line holds the delivery (and its order when the profile has `repos`), publishing as the profile's `humanBeforePublish` says (`false`: without asking; `true`: ask before each publish; `"ask-once"`: one question listing everything; nothing to say for `branch` or `none`), archiving sessions (no unless the person says), the branch and base, and what step 1 found that the person should know (no profile yet, the mode, the app). Then the two buttons, through `wrap_up` (its question "Launch with this table?"), or as two lines of text without it: «Yes, launch each part in its session with this table» and «I want to change something», in the person's language (in Spanish, «Sí, lanza cada parte en su sesión con esta tabla» / «Quiero cambiar algo»).

**Batch 3**, one message, only without `--dry-run`, all with Write and Edit:

- `<common-dir>/info/exclude` (`git rev-parse --git-common-dir`, batch 2) holds `/.claude/worktrees/` and `/.claude/runs/` (Edit to add what is missing, or Write it if absent);
- `runDir/state.json`, version 2, `status: proposed`: the run's fields (`run`, `plan`, `title`, `mode`, `workspace`, `sessions`, `checkout`, `runDir`, `iteration`, `gates`, `install`, `reviewRounds`, `delivery`), `coordinator` (`sessionId`, `model` of this chat), `repos.root` with `branch`, `base` and `baseSha` (null until the launch), `proposal` (`revisions`: 1, or the earlier proposal's + 1; `approvedAt` and `words` null), every part with its `implementer`, `reviewer` and `critic` rows (`model`, `effort`, `skills`, `reason`), `weight`, `pauseBefore` and `status: pending`, `current` null, `messagesSinceUser` 0, `wakesSinceUser` 0, `presses` with `{ "at": <now>, "what": "proposal" }`, `startedAt` and `updatedAt`;
- the table, the buttons and the `wrap_up`.

Then end the turn: nothing is created until the person answers. With `--dry-run`: no batch 3; show the table, then what the launch would do (the branch from the base, the worktree path, the brief, and the `start_session` call of step 4 with the first part's row), and that `/baton:run <plan>` proposes it for real.

## 3. The person's answer

Any message the person writes while the run is `proposed` is their answer; read `state.json` and the time (`date -u +%Y-%m-%dT%H:%M:%SZ`) in one message first.

- **A yes**: the approve button, or words that accept the table as it stands ("sí", "lanza", "adelante", "yes", "go"). Write `proposal.approvedAt` (now) and `proposal.words` (their words verbatim), a `presses` entry `approve`, and `runDir/decisions.md` with the header `| When | Part | Stop | Decision | Why |`, its separator line and a row `| <now> | — | proposal | table approved (revision <n>) | <the rows in one line: A sonnet/medium, B opus/medium + critic…> |`. A row still marked as above this chat's ceiling is not approved: say so again and stop. Then the launch, in this same turn.
- **A change** ("baja P3 a Sonnet", "Critic en B", "delivery pr", "otra vez con Opus para todo"): apply it to the rows, recheck the ceiling, recompute the weight line, add 1 to `proposal.revisions`, a `presses` entry `change: <their words>`, Write `state.json` whole, and show the new table with the same buttons. Nothing starts.
- **A stop** ("para", "déjalo", "cancel"): `status: stopped`, and say nothing was created.
- **Unclear**: ask in one line which it is.

## 4. The launch

**The gate, before anything else:** `state.json` must hold `proposal.approvedAt`. Without it, stop: the table is not approved, so go back to step 2. This turn must be the person's own (their yes), auto mode must hold (`permissionMode`, step 1.2) and `start_session` must be loaded (step 1.3); failing either, say it in one line and stop, leaving the approval written.

**Batch 4**, one message: the profile's Write when step 1.4 kept one; `git rev-parse --verify <base>`, and for an existing branch `git merge-base <base> <branch>` and `git rev-parse <branch>`; Read `PLUGIN/templates/brief.md`; the worktree:

1. **Worktree**: when the branch is already checked out in an earlier baton worktree (`git worktree list --porcelain` shows it under `.claude/worktrees/baton-…`), use that worktree as it is. Otherwise, from the checkout: `git worktree add -b <branch> .claude/worktrees/baton-<run> <base>` for a new branch, `git worktree add .claude/worktrees/baton-<run> <branch>` for an existing one. A failure (the branch checked out elsewhere, a path in use) stops the launch with git's message. `baseSha` is the base's commit for a new branch, and `git merge-base <base> <branch>` for an existing one, so the run's commits are the branch's own (D-34).
2. **Install**: the profile's `install` runs inside the implementer session as the first step of the first part (the brief says so), not here: that keeps the launch in this turn, where the session may be started (D-16).

**Batch 5**, one message, all with Write and Edit (Write creates the folders):

1. **settled.md** in workerRunDir (`<worktree>/.claude/runs/<run>/`), with the line `# Settled while the plan ran` (D-37).
2. **brief.md** in workerRunDir, from `PLUGIN/templates/brief.md` with every `{{…}}` replaced ("Filling the brief" below), one brief for the whole plan. Check your text before writing it: no `{{` may be left.
3. **state.json** in runDir, written whole: `status: running`, `worktree`, `workerRunDir`, `repos.root` with its `path` (the worktree), `baseSha` and `createdBy: "baton"`, the first part `working` with `startSha` `{ "root": <baseSha for a new branch, the branch's tip for an existing one> }`, `current` the first part, a `presses` entry `launch`, and everything the proposal wrote kept as it is.

**Batch 6**, one message: copy into workerRunDir, one command each, `PLUGIN/prompts/implementer.md` as `implementer.md`, `PLUGIN/agents/reviewer.md` as `reviewer.md`, and the plan file as `plan.md` (the reviewer reads this copy, so an uncommitted plan works too).

**Filling the brief**: `{{title}}`; `{{plan}}` (repo-relative path) and `{{planCopy}}` (`workerRunDir/plan.md`); `{{worktree}}`, `{{branch}}`, `{{base}}`, `{{baseSha}}`, `{{workerRunDir}}`; `{{iteration}}` and `{{iterationNote}}` (empty, or " — continuing branch <branch> from an earlier run" for iteration 2+); `{{rules}}`: the profile's rule files as a list plus its `notes`, ending "Where a rule of this repo and this brief disagree, the rule wins."; `{{implementerSkills}}` and `{{reviewerSkills}}` (comma-separated, or "none"); `{{gates}}` (each in backticks, or "none declared"); `{{install}}` (the command in backticks, or "none"); `{{alreadyDecided}}` copied from the plan as written; `{{parts}}`: for each part, `### Part <id> — <title>`, its text as the plan writes it, `**Acceptance**` with its criteria (or "none written: the reviewer checks the part's text"), and `**Reviewer:** <model>, effort <effort>` from its approved row (with `· Critic: <model>, effort <effort>` when it has one); `{{reviewRounds}}`; `{{extra}}`: anything else the plan needs (empty when nothing).

**Batch 7**: call `start_session` with:

- `initiation: "user_asked"` (this turn is the person's yes), `context: "fresh"`, `cwd`: the worktree's absolute path, `use_worktree: false`, `wake_when_done: true`;
- `name: "baton-<run>"`, `title: "baton · <plan title>"` (under 60 characters);
- `model` and `effort`: the first part's approved implementer row, the model as its id (`claude-opus-5-5`, `claude-sonnet-5-5`, `claude-haiku-5-5`); no `permission_mode` (it inherits auto);
- `prompt`, with `<workerRunDir>`, `<part>`, `<startSha>` and the title replaced by their values: "You are baton's implementer for the plan «<title>». Read `<workerRunDir>/implementer.md`, then do part <part> from <startSha>: read and follow `<workerRunDir>/brief.md`. End every turn with the baton-result block it describes.";
- `background`: "baton runs a written plan part by part. A coordinating chat started this session in the plan's worktree on branch <branch>; it names one part at a time, reads your result files and answers your questions. Do not push, open pull requests, merge or change branches."

**Batch 8**, one message: Edit `state.json` with the returned session (`id`, `name`, `archived: false`) as the first part's `session` (with `sessions: "per-plan"`, as every part's `session`) and `updatedAt`, and the `wrap_up` if your app asks for one. Then say one line with a link to the session: "Part A at work in [baton · <title>](#local_<id>). I'll follow it from here and write when something needs you." End the turn: never poll, never wait. Each turn end of that session wakes this chat: handle it with `/baton:event`.
