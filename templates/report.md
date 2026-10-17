# <Plan title> — baton report

- **Plan:** `<plan path>` · iteration <n> · mode <mode>
- **Branch:** `<branch>` from `<base>` (<base sha>) · worktree `<path>` (removed | kept: <why>)
- **Delivery:** <branch left as is | pull request <url> (created | updated) | merged locally into <base> | none>
- **Started / finished:** <date time> → <date time>

## Parts

### Part A — <title>
- **Result:** done · review r1 NO (2 findings) → r2 OK
- **Commits:** `<sha>` <subject> · `<sha>` <subject>
- **Gates:** `npm test` → 0
- **Summary:** <the implementer's one or two lines>

### Part B — <title>
…

## Settled while the plan ran

<The lines of `settled.md`: each answer, its part, and whether it came from the plan or from you. "None." when empty.>

## Decisions by the supervisor

| When | Part | Stop | Decision | Why |
|---|---|---|---|---|
| 20:12 | A | question | answered from the plan | The plan's "Already decided" says … |
| 20:40 | B | question | passed to you | Touches delivery, which is always yours |

## Reviews

| Part | Round | Verdict | Findings | File |
|---|---|---|---|---|
| A | 1 | NO | 2 | `.claude/runs/<run>/review-A-r1.md` |
| A | 2 | OK | 0 | `.claude/runs/<run>/review-A-r2.md` |

## Repeated findings

<If a finding category appears in two or more plans of this repo (`.claude/runs/findings.jsonl`), propose here one rule for CLAUDE.md, in the repo's language, so the implementer stops failing on it. Otherwise: "None yet.">

## Cost

- Implementer session: <tokens by model, or "see the session's usage card">
- Reviewer subagents: <tokens / USD from the subagent notifications>
- Supervisor: decisions made in this chat, no extra process

## What needed you

<One line per press the person made: the launch, each pause, each escalation, each permission dialog. The count is the plan's cost in presses.>
