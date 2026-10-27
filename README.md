# baton

**Run a written plan part by part from one chat in the Claude desktop app. You approve a model for each part. Each part gets its own nested session, a fresh read-only reviewer checks it until OK, and the chat checks the work itself. It answers what the plan settles and asks you the rest, then delivers across one or several repos the way they ask.**

baton 0.3 is a Claude Code plugin with no code: five skills, one agent, three prompts and some templates. It drives the app's own nested sessions, so there is no watcher, no background process and nothing to keep running.

```text
you ──/baton:run docs/plans/x.md──▶ this chat (coordinator)
                                      │ 1. proposal: a model and effort per part and role, with reasons
you ──«Sí, lanza cada parte…»───────▶ │ 2. launch: branches in each repo, one brief, state in files
                                      ├─▶ session "baton-x-a" (part A, its own model)
                                      │     commits → reviewer subagent → OK → result
                                      │◀── wakes on each turn end: checks the trees, commits, reviews
                                      │    answers from the plan, decides what you delegated, or asks you
                                      ├─▶ session "baton-x-b" (part B, a new session)
                                      │     …
                                      └─▶ delivery per repo, in order: branch, pull request or merge + report.md
```

## Requirements

- The **Claude desktop app, Code tab**: baton starts each part's session with the app's nested sessions. `/baton:setup`, `/baton:plan`, `/baton:status` and `/baton:run --dry-run` also work in a terminal.
- A git repository with at least one commit; with several repos, each one a repository of its own (submodules or folders).
- The chat in **auto** permission mode (the sessions inherit it).
- For pull requests: an `origin` remote and `gh` signed in, in each repo.

Tested on Windows 10, in the Claude desktop app for 0.2 and with the Claude Code CLI 2.1.296 for 0.3 (see "Results of the 0.3 round").

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

Then **open a new session**: a plugin loads when a session starts. To update from 0.2, run `claude plugin marketplace update baton`, then install again.

To uninstall, say "Uninstall the baton plugin" (add "at project scope" where it was installed that way), or run, with the scope you installed it at:

```bash
claude plugin uninstall baton@baton --scope user
```

```bash
claude plugin marketplace remove baton --scope user
```

## From the app, step by step

1. **Open the repo** in a Code session, in **auto** mode.
2. **Set it up (optional).** `/baton:setup` (or "configura baton") reads `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `.claude/rules`, the repo's skills and settings and the stack. It says what it found and writes `.claude/baton.json` with only what it detected. `/baton:run` does the same reading on its first run.
3. **Write the plan.** Talk it through, then `/baton:plan` (or "escribe el plan") saves it from the template. It first checks your answers in earlier runs and shows any clash. A plan written in another format stays as it is: `/baton:plan --adapt <plan>` reads it and writes a map baton uses instead (see "The plan").
4. **The proposal.** `/baton:run docs/plans/my-plan.md` (or "ejecuta el plan…") creates nothing yet. It shows a table with one row per part: the model and effort of its implementer, its reviewer and an optional Critic, a weight, and a reason that cites the plan section it rests on. Answer «Quiero cambiar algo» or your own words ("baja C a Haiku", "Critic en B") and it shows the table again. `--dry-run` shows the table and what the launch would do.
5. **The launch: your yes.** «Sí, lanza cada parte en su sesión con esta tabla». The app lets a chat start a session only in a turn you typed, so the yes is always your message. It may carry a delegation too ("…; autorizo el borrado de B.2").
6. **Follow it in the sidebar.** Each part runs in its own session `baton · <plan title> · <part>`, on the model you approved. Each time one ends a turn, your chat handles it with `/baton:event` (it loads by itself) and says one line. It does not take the session's word: it checks every repo's tree, the commits, the saved reviews and the Critic, then starts the next part. When the app will not let it start a session (a broken chain of automated turns), it leaves a card for you to click.
7. **When something needs you**, the chat asks with buttons and sends a push notification: a question the plan does not settle, a pause the plan wrote, a blocked part, or a word to go on after nine messages or wake-ups (a push warns at eight). Answer in the chat; your words reach the session verbatim.
8. **Pause and go on.** "para" (or `/baton:status pause`) pauses: the sessions at work save their state in `pause-<part>.md`. "sigue" or "continúa" picks the run up again, from this chat or from another one, which then becomes the coordinator. "stop" ends the run, keeping its branches.
9. **Delivery** follows the repos, in `deliveryOrder`. You get the branches as they are, a pull request per repo (the report as its body, the sibling pull requests linked), or a local merge. A pause can deliver some repos first (`deliver: backend`). The repo's own scripts can do the publishing (a `deliver` hook). Nothing is ever forced or deleted.
10. **Report and close.** `.claude/runs/<run>/report.md` holds the parts, commits per repo, gates, reviews, every decision with its reason, what you answered and what needed you. Once you merge, "cierra" (`/baton:status close`) runs the repo's close hooks, takes each repo back to its base and removes local exclusions.

## The plan

```markdown
# Fix login

The button does nothing on Safari.

baton: mode=normal

## Already decided

- Keep the old /login route for one release.

## Part A — Reproduce the bug in a test

**Repos:** frontend

**Acceptance**
- `npm test` fails on the new test before the fix.

## Part B — Fix the handler

Stop before B.2: B.2 resets the sample data.

**Acceptance**
- `npm test` passes.

## Pause before part C

deliver: frontend

## Part C — Document it
```

- **Parts** are headings starting with Part, Parte, Phase, Fase, Step or Paso and an id. A plan numbered its own way gives `partHeading=<regex with a group id>` on its `baton:` line, or `plan.partHeading` in the profile; for MSG, `^(?:\d+(?:\.\d+)*\s+)?(?<id>P\d+|CA)\b`. The title is never a part.
- **Acceptance** is the list under a heading or label saying Acceptance, Aceptación, Criteria, Criterios, Done when or Verification, or one line "**Aceptación P1:** …".
- **`**Repos:**`** names the repos a part works in. Without it, the proposal reads them from the paths the part names.
- **Pauses.** A heading or line starting with Pause, Pausa, Stop here or Human decision pauses before the next part; `deliver: <repos>` delivers those first. A line that stops before a step ("Parada antes de P2.8") pauses inside the part.
- **The `baton:` line** takes `mode=cheap|normal|thorough`, `models=B:opus/high`, `delivery=branch|pr|merge|none`, `branch=`, `base=`, `partHeading=` and `decided=§5,§13` (numbered sections that count as decided).
- **What the plan settles** ("Already decided", the parts, the repo's rules) is what the chat answers from. Anything else comes to you, and your answers go to `settled.md`, which the reviewer reads too.
- **`/baton:plan --adapt <plan>`** is for a plan in its own format, such as a versioned document. It never changes the plan. It shows the parts, repos, criteria, pauses and partial deliveries it understood, asks what is doubtful, and writes `.claude/runs/_maps/<plan>.json` with the plan's `git hash-object`. `/baton:run` uses the map while the hash matches, and says so when the plan changed.

## Who decides what

The sessions ask only through their result files. The chat decides within a closed table (`prompts/supervisor.md`), whose rows have ids:
- **It decides itself:** answers from the plan, the rules or the code; a choice between options the plan allows; a transient failure retried twice; a part replanned once.
- **It always asks you:** credentials, writes outside the repo, scope, publishing, destructive operations, permissions, spending, the plan's own pauses, UI design, installing software, computer use, the machine's environment, accepting a red gate, and a question asked a third time.

Every decision is a row in `decisions.md` with one sentence of reason, and one line in the chat.

- **The repo can tune it** in `authority`: `allow` hands it rows (`publish` for a repo that wants pull requests without asking), `alwaysAsk` adds its own, and `neverDelegate` keeps rows for you (`ui-design` and `install-software` by default).
- **You can delegate during the run:** «autorizo el reset de P2.8, la pausa A→B y push/PR». The chat says what it took and refuses in one line what cannot be delegated (credentials and permissions never are). It writes your words to `settled.md` under `## Delegated by the person`, and decides those stops itself with a row "decided under delegation". At your next word, it lists what it decided that way.
- **Publishing:** `humanBeforePublish: true` asks before each push, pull request or merge. `"ask-once"` asks once, with everything the run will publish listed.
- **Earlier runs:** the proposal shows where the plan contradicts something you decided in an earlier run, with your words quoted.

## The profile

`.claude/baton.json`, version 2, every key optional (`templates/baton.json` has them all):

| Key | Default | Meaning |
|---|---|---|
| `workspace` | `worktree` | `worktree`: the plan works in its own worktree (one repo). `checkout`: in the folder you use, needed with several repos; one open run per checkout. |
| `sessions` | `per-part` | `per-plan` keeps 0.2's single session for the whole plan. |
| `repos` | `root` at `.` | `name`, `path`, `base`, `rules` and `reviewSkills` per repo. |
| `base`, `branchPrefix`, `branch` | the checkout's branch, `baton/` | The plan's branch (the same name in every repo); `branch.createdBy`: `baton`, `hook` or `part:<id>`. |
| `delivery`, `deliveryOrder`, `merge` | `branch`, the repos' order, `never` | `branch`, `pr`, `merge` or `none`, repo by repo in that order. |
| `humanBeforePublish` | `false` | `true` asks before each publication, `"ask-once"` once for the run. |
| `authority` | see above | `allow`, `alwaysAsk`, `neverDelegate`. |
| `hooks` | none | `onStart`, `beforePart`, `afterPart`, `snapshot`, `deliver`, `onClose`, `afterMerge`: the repo's own scripts, run by the chat or by the part's session, with markers such as `{{repoRunId}}` and `{{repo}}`. |
| `untrackedPolicy` | `stop` | Untracked files at the start of a checkout run: `stop`, `ignore` or `exclude-local` (excluded in `info/exclude` until the close). |
| `gates`, `install`, `reviewRounds` | by stack, by lockfile, `3` | As in 0.2. |
| `models.start`, `modes` | `inherit`/`high`, `sonnet`/`medium` | Where the proposal starts. You always approve the table. |
| `plan.partHeading`, `plan.decided` | none | See "The plan". |
| `rules`, `notes` | detected | Rule files and the repo's own processes, passed to every brief. |

## Cost, and which model where

- **0.3 round** (four parts, CLI, Sonnet coordinator): 3.51 USD. Coordinator 2.88 USD (82 %), implementers 0.48 (14 %), reviewers 0.16 (4.5 %, about 0.04 per round). In v0.1 the split was 73 / 24 / 3 %, with the coordinator in the app. B's and C's reviewers are estimated from their tokens, since they share the implementer's model. Its cost grows with its own conversation, since each event reads it again: 0.09 to 0.32 USD per turn in this round, and 0.75 for the delivery of three pull requests.
- **0.2:** a part's event went from 8.3 calls and 0.39 USD to 3.1 calls and 0.20 USD with an Opus chat.

How to choose:
- **Run the chat you launch from in Sonnet** unless a part needs an Opus implementer: the app never starts a session on a model above the chat's, and the proposal marks such rows.
- **Cheap parts on Haiku.** The proposal puts each part where its risk is, and you can lower a row ("C en Haiku") without weakening its reviewer.

## Results of the 0.3 round

One plan of four parts in a three-repo lab (root, backend and frontend as repos of their own, local bare remotes, a stand-in `gh`). The coordinator was a `claude -p` chat with the app's session tools replaced by a stub. Each part's session was a real `claude -p` session, run with the prompt the coordinator gave the stub's `start_session` and resumed with each message it wrote.

| Part | Model | Turns | What it exercised |
|---|---|---|---|
| A · `count()` | Haiku medium | 1 | reviewed OK in round 1; checked by the chat |
| B · `add()` and clean data | Sonnet medium | 2 | the pause before B.2, decided under the delegation given with the yes |
| C · the total on the page | Sonnet medium | 2 | a question only you could answer (UI text), escalated and forwarded verbatim |
| D · the README | Haiku medium | 2 | «para» while at work; its `done` arrived during the pause, and the queued pausa came after |

- **Your presses:** 6. The command, a change with the yes («…A y D en Haiku; autorizo el borrado…»), the plain yes, the answer for C, «para» and «continúa».
- **Wakes per part:** A 1, B 2, C 2, D 2.
- **Starts:** four sessions started; no start was refused, and no card was needed.
- **Delivery,** on «continúa»: backend PR #1, frontend PR #2 and root PR #3, in that order, each checked against its branch.

**Still open**, because the round could not show them with a stubbed app:
- whether a session start counts in the app's 10-message quota (baton counts it);
- whether a card keeps the model and effort it was proposed with (baton checks them at its first event);
- whether a compaction or the tenth wake-up breaks the chain of automated turns.

**Not seen live** (in the app):
- a start inside a chain of events, a refused start and its card clicked, and an effort raised by an event;
- the message and wake limits reached;
- a session stopped mid-turn with `stop_session`, a session gone at «continúa», and a session archived;
- a real `gh`, and a real `entrega` by a session's `deliver` hook;
- a delegation taken back, a profile's `allow` and `alwaysAsk`, and a `merge` under a delegated `publish`;
- `--adapt`'s questions answered by a person, a launch from a map, and its hash check at the launch.

The CLI probes of each part (`docs/DECISIONS.md`, D-58 to D-69) cover them with stubs.

## Results of the 0.2 tests

Two plans in a throwaway repo (Opus chat, Haiku/low and Opus implementers, Sonnet reviewer).
- **t1:** 2 parts and 2 presses. It saw a retry, a replan after a NO review, `humanBeforePublish` and a local `merge`.
- **t2:** 11 parts and 3 presses. It saw a second replan, a rule proposed from a finding repeated across plans, and two lost wake-ups picked up with "sigue".

v0.1's five plans cost 1.6 to 4.2 USD each.

## Files

- **In your checkout,** `.claude/runs/<run>/`: `state.json`, `decisions.md`, `report.md`, and at the end a copy of the sessions' files.
  - `.claude/runs/findings.jsonl` collects review findings across plans; a category that repeats becomes a proposed rule in the report.
  - `.claude/runs/_maps/` holds `--adapt`'s maps.
- **The sessions' folder** is the plan's worktree with `workspace: worktree`, and the run folder itself with `checkout`. It holds `brief.md` (one for the whole plan), `settled.md`, `result-<part>.md`, `review-<part>-r<n>.md`, `critic-<part>-r<n>.md` and `pause-<part>.md`.
- `/.claude/worktrees/` and `/.claude/runs/` are added to `.git/info/exclude`. The profile is the repo's to commit or not.
- **Windows:** baton writes its state files with Write and Edit only, which keep them UTF-8. A shell redirection or a script can leave cp1252 bytes, as seen in two probes, and the next `json.load` then fails. `docs/DESIGN.es.md` has the details and the shape of `state.paused`.

## Limitations

- **The launch is yours to type.** A turn opened by another session's message or a background event cannot start sessions: baton leaves a card for the next part instead, and you click it.
- **Ten messages and ten wake-ups per word from you.** The app delivers at most 10 messages from a chat to other sessions per message you write, and wakes a chat for at most 10 turn ends in a row without a word from you. baton warns with a push at 8 and stops at 9 with «Continuar».
- **A model above the chat's** cannot be launched: run the chat on that model, or lower the row.
- **Empty worktree folders** stay on Windows while a session still uses them as its working folder.
- **`settings.local.json` does not reach a worktree.** The repo's committed `deny` rules do apply in auto mode.
- **Permission dialogs** in a part's session are seen only in the sidebar; baton never answers them.
- **Installed from a folder** (development), the plugin runs from a cache copy that a new session does not refresh while the version stays the same: uninstall and install again after a change.

## Contributing

```bash
claude plugin validate . --strict
```

Skill frontmatter is not checked by `validate`; keep descriptions as YAML block scalars (`description: >-`). Design decisions are in [`docs/DECISIONS.md`](docs/DECISIONS.md); the design, in Spanish, in [`docs/DESIGN.es.md`](docs/DESIGN.es.md).

## License

MIT, see [LICENSE](LICENSE).
