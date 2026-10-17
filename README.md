# baton

**Run a written plan part by part from one chat in the Claude desktop app: a nested session implements each part, a fresh read-only reviewer checks it until OK, the chat answers what the plan settles and asks you the rest, then delivers the way the repo asks.**

baton is a Claude Code plugin with no code: four skills, one agent, two prompts and some templates. It drives the app's own nested sessions, so there is no watcher, no background process and nothing to keep running.

```text
you ──/baton:run docs/plans/x.md──▶ this chat (coordinator)
                                      │ worktree + branch, state in files
                                      ├─▶ nested session "baton-x" (implementer, auto mode)
                                      │     part A → commits → reviewer subagent → OK → result
                                      │◀── wakes up on each turn end, reads the result
                                      │    answers from the plan, or asks you (buttons + push)
                                      ├─▶ "part B from <sha>: read and follow brief.md"
                                      │     …
                                      └─▶ delivery: branch, pull request or merge + report.md
```

## Requirements

- The **Claude desktop app, Code tab**: baton starts its implementer with the app's nested sessions. `/baton:setup`, `/baton:plan`, `/baton:status` and `/baton:run --dry-run` also work in a terminal.
- A git repository with at least one commit.
- The chat in **auto** permission mode (the implementer session inherits it).
- For pull requests: an `origin` remote and `gh` signed in.

Tested on Windows 10 in the Claude desktop app, whose sessions ran Claude Code 2.1.295 (a few turns 2.1.296), and with the Claude Code CLI 2.1.296.

## Install

From a chat, paste:

> Install the baton plugin from the marketplace andrey342/baton.

Claude runs these two commands, at **user** scope (every repo). Add "at project scope" for one repo only: both commands take `--scope project`, and the plugin is declared in the repo's `.claude/settings.json`. Commit that file if the plan's worktree must load the plugin too.

```bash
claude plugin marketplace add andrey342/baton
```

```bash
claude plugin install baton@baton --scope user
```

Then **open a new session**: a plugin loads when a session starts.

To uninstall, say "Uninstall the baton plugin" (add "at project scope" where it was installed that way), or run, with the scope you installed it at:

```bash
claude plugin uninstall baton@baton --scope user
```

```bash
claude plugin marketplace remove baton --scope user
```

## From the app, step by step

1. **Open the repo** in a Code session, in **auto** mode.
2. **Set it up (optional).** `/baton:setup` (or "configura baton") reads `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `.claude/rules`, the repo's skills and settings and the stack, says what it found, and writes `.claude/baton.json` with only what it detected. `--show` writes nothing; `--template` adds the plan template to `docs/plans/`. `/baton:run` does the same reading on its first run.
3. **Write the plan.** Talk it through, then `/baton:plan` (or "escribe el plan") saves it from the template: an "Already decided" section, parts with acceptance criteria a reviewer can check, pauses where you want to decide.
4. **Run it: type it yourself.** `/baton:run docs/plans/my-plan.md` (or "ejecuta el plan docs/plans/my-plan.md"). The app lets a chat start a session only in a turn you typed, so the launch is always your message; another session cannot launch it for you. `/baton:run` with no argument offers the repo's only plan. `--dry-run` prepares everything but starts no session.
5. **Follow it in the sidebar.** A nested session `baton · <plan title>` works in the plan's worktree on its own branch. Your chat says one line per event.
6. **When something needs you**, the chat asks with buttons and sends a push notification: a question the plan does not settle, a pause the plan wrote, a blocked part, or a word to go on after nine messages (see Limitations). Answer in the chat; your words reach the implementer verbatim.
7. **Delivery** follows the repo: the branch as it is, a pull request (created with the report as its body, or, if the branch already has an open one, updated by the push and commented with the report), or a local merge. Nothing is ever forced or deleted.
8. **Report.** `.claude/runs/<run>/report.md`: parts, commits, gates, reviews, every decision with its reason, what you answered, and what needed you.
9. **After closing the app**, say "sigue" or `/baton:status continue`: everything lives in files, so baton picks up from them. `/baton:status` alone reports without acting; "para" stops the plan and keeps the branch and worktree.

Running the same plan file again later goes back to its branch while that branch is unmerged or has an open pull request: the new run is iteration 2 and updates the same pull request.

## The plan

```markdown
# Fix login

The button does nothing on Safari.

baton: mode=normal

## Already decided

- Keep the old /login route for one release.

## Part A — Reproduce the bug in a test

**Acceptance**
- `npm test` fails on the new test before the fix.

## Part B — Fix the handler

**Acceptance**
- `npm test` passes.

## Pause before part C

## Part C — Document it
```

- **Parts** are headings starting with Part, Parte, Phase, Fase, Step or Paso and an id. A plan without them is one part.
- **Acceptance** is the list under a heading or label saying Acceptance, Aceptación, Criteria, Criterios, Done when or Verification.
- **A pause** is a heading or line starting with Pause, Pausa, Stop here or Human decision: baton asks you before the next part.
- **The `baton:` line** takes `mode=cheap|normal|thorough`, `delivery=branch|pr|merge|none`, `branch=<existing branch>`, `base=<ref>`.
- **What the plan settles** ("Already decided", the parts, the repo's rules) is what the chat answers from; anything else comes to you. Answers given during the run are written to the run folder's `settled.md`, which the reviewer reads too.

## Who decides what

The implementer asks only through its result file. The chat decides within a closed table (`prompts/supervisor.md`): it answers from the plan, the rules or the code, picks between options the plan allows, retries a transient failure twice, replans a part once. Credentials, writes outside the repo, scope, publishing, destructive operations, permissions, spending, the plan's own pauses and a question asked a third time always come to you, whatever the plan says. Every decision is a row in `decisions.md` with one sentence of reason, and one line in the chat.

## The profile

`.claude/baton.json`, every key optional:

| Key | Default | Meaning |
|---|---|---|
| `base` | the checkout's branch | Base of the plan's branch and pull request. |
| `branchPrefix` | `baton/` | The plan's branch is `<prefix><plan file name>`. |
| `delivery` | `branch` | `branch`, `pr`, `merge` or `none`. `pr` falls back to `branch` without `origin` or `gh`. |
| `humanBeforePublish` | `false` | Ask before a push or merge. |
| `gates` | by stack | Commands the implementer and the reviewer run, exactly as written. |
| `install` | by lockfile | Run once in the new worktree by the implementer (`npm ci`…). |
| `reviewRounds` | `3` | Review rounds per part. |
| `roles.implementer` / `roles.reviewer` | `inherit`/`high`, `sonnet`/`medium` | `model`, `effort`, and repo `skills` to load. |
| `modes.cheap` / `modes.thorough` | see `templates/baton.json` | Overlays on `roles`, chosen by `baton: mode=…`. |
| `rules`, `notes` | detected | Rule files and the repo's own processes, passed to every brief. |

## Cost, and which model where

Measured over five test plans of one to three parts, at API prices: **1.6 to 4.2 USD per plan**, of which about **73 % is the coordinating chat**, 24 % the implementer session and 3 % the reviewer (0.04–0.06 USD per review round with Sonnet). The chat is the expensive role: every turn end of the implementer wakes it with its whole context, mostly cache reads.

- **Run the chat you launch from in Sonnet** unless the plan needs an Opus implementer. Cache reads cost the same on both, but writes and output cost half: about −24 % on the coordinator in the test plans.
- **Fix the implementer's model in the profile** (`roles.implementer.model`) instead of inheriting the chat's. The app never starts a session on a model pricier than the chat's own (it ignores the request), so an Opus implementer needs an Opus chat.
- **The reviewer** defaults to Sonnet/medium; `modes.cheap` in the profile can lower the implementer (even to Haiku/low) without weakening the reviewer.

Prices: the official per-token table (Opus 5.5, Sonnet 5.5, Haiku 5.5; cache writes 1.25×/2× input), applied to the usage recorded in each session's transcript.

## Results of the v0.1 tests

Five plans in two throwaway repos (one without rules; one with `CLAUDE.md`, a repo skill, a `deny` rule and pull requests):

| Plan | Parts | Presses by the person | Cost (USD) |
|---|---|---|---|
| demo | 3, a pause before the last | 3: launch, one answer, continue | 4.24 |
| demo-fix | 1, second iteration on the same branch | 1: launch | 1.63 |
| lab | 2 | 2: launch, one answer | 3.09 |
| lab-2 | 1, same plan file edited, same branch and pull request | 1: launch | 1.57 |
| lab-edge | 1, new branch and pull request | 2: launch, one answer | 2.29 |

- **Presses:** one to three per plan: the launch, each question the plan does not settle, each pause it asks for. No permission dialog stopped an implementer session and no folder-trust dialog appeared.
- **Cost by role:** coordinator 73 %, implementer 24 %, reviewer 3 % (0.04–0.06 USD per round).
- **Seen working live:** answers from the plan and escalations with buttons; parts chaining without a word from the person; the plan's pause; the repo's rules, skill and commit convention followed; both gates run by the reviewer in the worktree; a pull request created with the report as its body, updated and commented by a second run of the same plan, and a new one whose body is the final report; answers in `settled.md` checked by the reviewer; a per-repo `modes.cheap`; the repo's `deny` applied in auto mode (probe).
- **Not seen live:** a NO review (all ten live reviews were OK in round 1; a scripted probe showed round 1 NO, the fix and round 2 OK), and the rest listed under Limitations.

## Files

- In your checkout, `.claude/runs/<run>/`: `state.json`, `decisions.md`, `report.md`, and at the end a copy of the implementer's files. `.claude/runs/findings.jsonl` collects review findings across plans; a category that repeats becomes a proposed rule in the report.
- In the plan's worktree, `.claude/worktrees/baton-<run>/.claude/runs/<run>/`: the briefs, `settled.md`, `result-<part>.md` and `review-<part>-r<n>.md`. The implementer writes only inside its own folder.
- `/.claude/worktrees/` and `/.claude/runs/` are added to `.git/info/exclude`. The profile is the repo's to commit or not.

## Limitations

- **The launch is yours to type.** A session started by another session, or a turn opened by another session's message, cannot start sessions.
- **Ten messages per word from you.** The app delivers at most 10 messages from a chat to other sessions per message you write in it, and wake-ups from other sessions do not reset that. baton stops before the tenth and asks for a word; a plan uses one message per part plus one per answer or retry.
- **Empty worktree folders.** On Windows, `git worktree remove` cannot delete a folder the implementer session still uses as its working folder: git forgets the worktree, an empty folder stays under `.claude/worktrees/` until that session ends, and the report says so. It is safe to delete.
- **`settings.local.json` does not reach the worktree.** The worktree holds only committed files, so `deny` rules or plugins enabled only in `.claude/settings.local.json` do not apply to the implementer session. `/baton:setup` warns about it. The repo's committed `deny` rules do apply in auto mode.
- **Permission dialogs in the implementer session** are seen only in the sidebar ("needs you"); baton never answers them. The implementer runs commands one at a time and edits with Edit/Write to keep them rare.
- **Designed but not yet tested live.** Every live review said OK in round 1, so the review loop's NO path (a finding, the fix, round 2) was exercised by a scripted probe only, and the coordinator's side of it (`findings.jsonl`, rules proposed from repeated findings) not at all. Also written but never run live: resuming after closing the app, replanning a part, retries after a transient failure, the stop after nine messages, `humanBeforePublish`, and `merge` delivery.
- **Installed from a folder** (development), the plugin runs from a cache copy that a new session does not refresh while the version stays the same: uninstall and install again after a change.

## Contributing

```bash
claude plugin validate . --strict
```

Skill frontmatter is not checked by `validate`; keep descriptions as YAML block scalars (`description: >-`). Design decisions are in [`docs/DECISIONS.md`](docs/DECISIONS.md); the design, in Spanish, in [`docs/DESIGN.es.md`](docs/DESIGN.es.md).

## License

MIT, see [LICENSE](LICENSE).
