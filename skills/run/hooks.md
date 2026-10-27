# The repo's own process: hooks, branch creation, untracked files and the close

Read by `/baton:run` at the launch, and by `/baton:event`, `deliver.md` and `/baton:status close` when the run's profile has `hooks`, a `branch.createdBy` other than `baton`, or `untrackedPolicy: "exclude-local"` (D6). baton runs a repo's own scripts where the repo asks for them, and never invents one: a hook is only what the profile writes.

## Hooks

`hooks.<name>` is either `{ "by": "coordinator" | "session", "run": "<command>" }` or `{ "by": "session", "text": "<instruction>" }`. It may also have `repo` (the repo it acts on, `root` by default) and, for `snapshot`, `after` (the repos it waits for).

**Markers**, replaced before a hook is run or written anywhere:

| Marker | Value |
|---|---|
| `{{run}}` | the run id |
| `{{planSlug}}` | the plan's file name without extension |
| `{{yyyymmdd}}` | the launch's date, UTC |
| `{{repoRunId}}` | the profile's `repoRunId` format with its markers filled, `{{yyyymmdd}}-{{run}}` by default; kept in `state.repoRunId` |
| `{{branch}}` | the run's branch |
| `{{repo}}` | the repo the hook acts on (`deliver` runs once per repo) |
| `{{repos}}` | the run's repos, comma-separated, in `deliveryOrder` |
| `{{report}}` | `runDir/report.md` |
| `{{title}}` | the plan's title |

The text that is run, sent or written into the brief never holds a `{{`: check it before. A marker not in this table stops the launch, which names it. The profile's `branch.name` takes the same markers.

**Who runs which, and when:**

| Hook | When | `by: "coordinator"` | `by: "session"` |
|---|---|---|---|
| `onStart` | at the launch, before the first session | runs in launch batch 4, before the branches | the brief makes it the first step of the first part |
| `beforePart` | at the start of each part | runs before each part's session starts (or its message is sent) | the brief makes it every part's first step |
| `afterPart` | before each part's review | not possible (the review is inside the session): taken as `session`, and said | the brief makes it every part's last step before the review |
| `snapshot` | after the submodules' delivery, before the root's | replaces baton's own snapshot commit (`deliver.md`) | part of the session's delivery: needs a `deliver` hook |
| `deliver` | at the delivery, per repo in `deliveryOrder` | runs per repo instead of baton's own push and pull request | the session delivers on `baton · entrega: <repos>` (`deliver.md`) |
| `onClose` | at the close, after the person's merge | runs at the close | sent to the last part's session at the close |
| `afterMerge` | at the close, after `onClose` | runs at the close | sent to the last part's session at the close |

**Running a coordinator hook.** One command, in the foreground, from the checkout (the profile writes paths from there), as written once its markers are filled. It must end in about two minutes: anything longer belongs to a session (`by: "session"`), since nothing runs in the background from the coordinator. Its exact command, exit code and last lines become a `decisions.md` row. A non-zero exit stops the step it belongs to (the launch, the delivery, the close), says so, and escalates.

**Session hooks in the brief** go under its "The repo's own steps" section, filled. `beforePart` and `afterPart` hold for every part. The delivery steps (`snapshot`, and `deliver` once per repo with `{{repo}}` filled, in the order) run only on a `baton · entrega` message. Without session hooks the section says "none".

## Who creates the branches

`branch.createdBy`:
- **`baton`** (default): the launch makes them, as its batch 4 says.
- **`hook`**: `onStart` makes them. baton creates none. Right after the hook, each repo must show the branch: `git -C <path> rev-parse --verify <branch>`, and in a checkout run `git -C <path> branch --show-current`. Each repo's `repos.<name>` keeps `branch`, `branchSha` (the `rev-parse`) and `createdBy: "hook"`. A repo without it stops the launch, which names the repo.
- **`part:<id>`**: that part makes them. The brief says so as that part's first step. Until it is done, each repo's `startSha` is its base's commit. At that part's `done`, the same check runs before anything else, and fills `branchSha`.

In a worktree run, a branch made by a hook is added as `git worktree add .claude/worktrees/baton-<run> <branch>`.

## Untracked files

In a checkout run, at the launch's clean-start check (`/baton:run` step 10), the untracked files of each repo follow `untrackedPolicy`:
- **`stop`** (default): the launch stops and names each file with its repo.
- **`ignore`**: they are named in a line, and the launch goes on.
- **`exclude-local`**: before anything else in batch 4, each untracked path goes into that repo's own exclude file as one anchored line, `/<path relative to the repo>`.
  - The file is `git -C <path> rev-parse --git-path info/exclude` (a submodule has its own). Edit it, or Write it if absent.
  - Each line goes into `state.excluded` as `{ "repo", "path", "line" }`, and the clean check runs again.
  - Nothing outside those lines changes. A file the repo already ignores is left alone.

A proposal or dry run only says what would happen.

## The close

**Which runs** it closes: a run `delivered` or `stopped` without `closedAt`. It happens:
- for a `delivered` run, when the person says the work is merged ("merged", "ya está mergeado", "cierra", `/baton:status close`), or right after a `merge` delivery that baton made itself;
- for a `stopped` run, when the person asks to close it. Nothing was merged, so `onClose` and `afterMerge` do not run. Only steps 2 to 4 do: the repos back to their bases and the exclusions out.

Until then, such a run still holds a checkout: its repos may be on its branch and its lines in the exclude files, so `/baton:run` step 10 counts it as open.

In this order:
1. `onClose`, then `afterMerge`.
   - A coordinator hook runs.
   - A session hook goes as a message to the last part's session: `baton · after merge: <its text>`. When it pushes (a gitlink bump, say), it goes as `baton · entrega: <repos> · after merge: <its text>`, since only an `entrega` lets a session push. When that session no longer exists, start one for it, as `/baton:event` "The next part's session" says (this turn is the person's), named `baton-<run12>-close`.
   - With a session hook, the close waits for it. Set `status: closing` with `closing.phase: "close"`, and end the turn. Steps 2 to 4 must not run under a session that is still working in the checkout. That session's next result is an event (`/baton:event` finds the run by `closing` and the session by its name). A `done` there goes on with steps 2 to 4. A `blocked` or `failed` escalates, and the run stays `closing`.
2. In a checkout run, each repo goes back to its base, `git -C <path> switch <base>`, when its tree is clean: submodules first, then a root that holds them. The root's check is `status --porcelain --ignore-submodules=all`, as everywhere in a run, since its gitlinks follow the submodules. Otherwise say which stays on the branch.
3. Each `state.excluded` line is removed from its exclude file with Edit, exactly that line, and `state.excluded` empties.
4. `state.closedAt`, the status back to what it was (`delivered` or `stopped`), `closing.phase` cleared, a `decisions.md` row "closed", and one line.
