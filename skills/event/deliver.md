# Delivering a baton run

Read by the coordinator from `/baton:event` when the last part is done, when the person answers «Stop here» at a pause, and for a **partial delivery** when a pause names repos to deliver first (its `pauseDeliver`, D5). PLUGIN is the plugin folder that skill names. Its rules hold here: batches (independent calls in one message), one shell command per call, files changed with Write and Edit only, nothing destructive. Every command runs from the checkout, with `git -C <path>` for each repo. **`<path>` is each repo's folder in the checkout**: the checkout itself for the root, `<checkout>/<its path>` for the others. In a worktree run that holds for the root too: the worktree is gone by step 4, and the branch is reached from the checkout.

**Which repos, in which order.** All the run's repos (a partial delivery: only the ones its pause names), in the profile's `deliveryOrder`; without one, the order of `repos`, with a repo that holds others of the run as submodules after them. A run with one repo delivers `root` alone, exactly as in 0.2. The order goes into `state.delivery.order` and the report.

**The snapshot.** When the root holds other repos of the run as submodules, its gitlinks must point at what they deliver before the root itself is delivered, and only after they are: after their push, for `pr`. Without a `snapshot` hook (D6), you make it, with the root still on the plan's branch. For each such submodule, compare `git -C <root> ls-tree HEAD <sub path>` with `git -C <sub> rev-parse HEAD`, taken after that submodule's own step. That HEAD is what the submodule delivers: its branch's head for `branch`, `none` and `pr`, and its base's merge commit for `merge`. `git add` records the same HEAD. When any differs, `git -C <root> add -- <the differing sub paths>`, then `git -C <root> commit -m "baton · <run>: submodules at their delivered commits"`. It is the only commit baton itself makes, and it touches nothing but those gitlinks. A partial delivery that does not include the root makes no snapshot.

## 1. Gather, in one message

- In a worktree run, copy every file of workerRunDir into runDir: `cp -r <workerRunDir>/. <runDir>/` in Bash, `Copy-Item <workerRunDir>/* <runDir>` in PowerShell. In a checkout run they are one folder: nothing to copy.
- For each repo delivered: `git -C <path> log --oneline <baseSha>..<branch>`;
- Read each part's `result-<part>.md`, `settled.md` (workerRunDir) and `decisions.md` (runDir);
- Grep, pattern `^(Verdict|Veredicto):|^### F-`, in workerRunDir with glob `review-*.md`, output `content`;
- Read `.claude/runs/findings.jsonl` (it may not exist) and `PLUGIN/templates/report.md`, unless already in this conversation;
- for `merge`, in each repo delivered: `git -C <path> status --porcelain` (the root with `--ignore-submodules=all` when it holds submodules of the run, whose gitlinks the snapshot settles) and `git -C <path> branch --show-current`; for `pr`: `gh pr list --head <branch> --state open --json number,url` in each;
- when the root is delivered and holds submodules of the run: the `ls-tree` and `rev-parse` of the snapshot, for each;
- `date -u +%Y-%m-%dT%H:%M:%SZ`.

## 2. The worktree

In a checkout run there is none: the repos stay on the plan's branch, and the report says how to go back once the person has merged (`git -C <path> switch <base>` in each repo). In a worktree run: `git worktree remove .claude/worktrees/baton-<run>`, without `--force`, after the copy. If it refuses (changes not committed) keep it and say so; if git let go of it but its folder stays because the implementer session still holds it, say so (D-35). The branch always stays. `state.delivery.worktree` records `removed`, `removed; its empty folder stays while the implementer session holds it`, `kept: <why>` (D-34), or `none: checkout`. A partial delivery leaves the worktree as it is.

## 3. Report and state, in one message

- Write `runDir/report.md` from the template (below), final except what publishing adds. A partial delivery writes no report: a row in `decisions.md` ("partial delivery: <repos>") and `state.delivery.partial` (a list of `{ "at", "repos", "outcome" }`) hold it until the final report lists it.
- Write `state.json`: `delivery` with `mode`, `why`, `order`, `worktree`. For `branch` and `none`, after the snapshot (step 4 does it for every mode): `status: delivered`, then one line with the outcome and the report's path, a push notification, and the turn ends.
- With `humanBeforePublish` and delivery `pr` or `merge` (a final delivery; a partial one asks as step 4 says): `status: waiting`, `waiting: { "kind": "publish" }`, and escalate as `/baton:event` says, with the buttons «Publish» / «Leave the branch». The answer comes back to step 4.
- Otherwise go on to step 4 in the next message.

## 4. Publish, repo by repo in the order

For each repo in the order, its own steps, and the root's snapshot just before the root's:

- `branch` and `none`: nothing is pushed; only the snapshot is made, when it applies. The report lists each repo's branch and commits, in the order.
- `pr`: `git -C <path> push -u origin <branch>`. An open pull request from step 1: put its URL in the report, then `gh pr comment <number> --body-file <runDir>/report.md` (the push already updated it). None: `gh pr create --base <base> --head <branch> --title "<plan title>" --body-file <runDir>/report.md`, run in that repo (`gh` takes the repo from the folder: one command per call, from `<path>`, with `gh -R <owner/name>` when it cannot), then put the new URL in the report and `gh pr edit <number> --body-file <runDir>/report.md`, so the body is the final report (D-38). Then bind it with `mcp__ccd_pr__bind_pr` when you have it ("already bound" is fine). With several repos, once every pull request exists: each body ends with "Sibling pull requests: <the others' URLs>" (`gh pr edit` again with the report holding the line), and a pull request that existed before gets that line as a comment.
- `merge`: a repo merges only when step 1's `status --porcelain` printed nothing.
  - In a worktree run (one repo), as in 0.2: also only when the checkout's current branch is the base, since the person's checkout is never switched. Otherwise that repo is delivered as `branch`, and you say why.
  - In a checkout run, the repo is on the plan's branch: `git -C <path> switch <base>`.
  - Then `git -C <path> merge --no-ff --no-edit <branch>`.
  - A repo that is not clean is delivered as `branch` with the reason, and so are the repos after it in the order, so the root never merges a gitlink to work that did not merge.
  - If a merge fails and `git -C <path> rev-parse -q --verify MERGE_HEAD` passes, run `git -C <path> merge --abort` and say "the branch does not merge cleanly in <repo>: it is as it was, the branch stays". The repos after it are not merged either.
- After a pull request is created or updated, check it rather than trust it (D4), in one message: `gh pr view <number> --json state,headRefOid,mergeable,body` and `git -C <path> rev-parse <branch>`. The `headRefOid` must be the branch's HEAD, and every commit the body cites must be on the branch, the newest of them its HEAD (`git -C <path> merge-base --is-ancestor <sha> <branch>`, one call per commit, in the next message). A mismatch: rewrite the body once from the report (`gh pr edit <number> --body-file <runDir>/report.md`) and check again; still wrong, say so in the line and in a `decisions.md` row.
- A step that fails stops the delivery there: say which repo and step and its message, `status: done-not-delivered` (the branches have the work; `/baton:status continue` retries from that repo and step, and `state.delivery.repos` says which are done). A partial delivery is never `done-not-delivered`: the run stays `waiting` on its pause, with the failure in the pause's question.

**A partial delivery and its pause.** It delivers only the repos the pause names, makes no report, and leaves the worktree as it is.
- For `branch` and `none`, or for `pr` and `merge` without `humanBeforePublish`: deliver first, then the pause's question gives the outcome.
- With `humanBeforePublish` and `pr` or `merge`: nothing is published before the person answers, and there is one question, not two: "The plan pauses before part <next> and delivers <repos> first." The buttons are «Publish <repos> and continue» / «Continue without publishing» / «Stop here», with `waiting.kind: "pause"`. «Publish…» delivers, then starts the next part.

## 5. Close, in one message

Edit the report's delivery lines (each repo's URL, "merged locally into <base>", or why not) and, after a publish question, add the person's answer to "What needed you"; Write `state.json` with `status: delivered` and `delivery` complete (`order`, `repos` with each repo's outcome, `url` and `comment` for a single repo), a push notification, and one line in the chat with the outcome, the order and the report's path. A partial delivery closes with its `decisions.md` row and goes back to the pause's question.

## The report

Fill `PLUGIN/templates/report.md`:

- the repos, each with its branch from its base at its `baseSha`, and the delivery order, with any partial delivery made at a pause;
- the parts with their results (status, repos, commits, gates, summary, from the result files); parts not done are said as pending;
- the lines of `settled.md`; the decisions table from `decisions.md`;
- commits per repo from `git -C <path> log --oneline <baseSha>..<branch>`, the snapshot commit marked as such, those before the first part's `startSha` marked "(earlier iteration)";
- the reviews table from the Grep: one row per review file, its verdict and the number of `### F-` headings;
- repeated findings: a `category` that appears in two or more plans of `findings.jsonl` gets one proposed rule for the repo's CLAUDE.md, in the repo's language; otherwise "None yet.";
- cost: the results' `reviewer_usage`, and "see the session's usage" for the implementer;
- "What needed you": one line per `presses` entry.
