# Delivering a baton run

Read by the coordinator from `/baton:event` when the last part is done, or when the person answers «Stop here» at a pause. PLUGIN is the plugin folder that skill names. Its rules hold here: batches (independent calls in one message), one shell command per call, files changed with Write and Edit only, nothing destructive. Every command runs from the checkout.

## 1. Gather, in one message

- Copy every file of workerRunDir into runDir: `cp -r <workerRunDir>/. <runDir>/` in Bash, `Copy-Item <workerRunDir>/* <runDir>` in PowerShell;
- `git log --oneline <baseSha>..<branch>`;
- Read each part's `result-<part>.md`, `settled.md` (workerRunDir) and `decisions.md` (runDir);
- Grep, pattern `^(Verdict|Veredicto):|^### F-`, in workerRunDir with glob `review-*.md`, output `content`;
- Read `.claude/runs/findings.jsonl` (it may not exist) and `PLUGIN/templates/report.md`, unless already in this conversation;
- for `merge`: `git status --porcelain` and `git branch --show-current`; for `pr`: `gh pr list --head <branch> --state open --json number,url`;
- `date -u +%Y-%m-%dT%H:%M:%SZ`.

## 2. The worktree

`git worktree remove .claude/worktrees/baton-<run>`, without `--force`, after the copy. If it refuses (changes not committed) keep it and say so; if git let go of it but its folder stays because the implementer session still holds it, say so (D-35). The branch always stays. `state.delivery.worktree` records `removed`, `removed; its empty folder stays while the implementer session holds it` or `kept: <why>` (D-34).

## 3. Report and state, in one message

- Write `runDir/report.md` from the template (below), final except what publishing adds.
- Write `state.json`: `delivery` with `mode`, `why`, `worktree`. For `branch` and `none`: `status: delivered`, then one line with the outcome and the report's path, a push notification, and the turn ends.
- With `humanBeforePublish` and delivery `pr` or `merge`: `status: waiting`, `waiting: { "kind": "publish" }`, and escalate as `/baton:event` says, with the buttons «Publish» / «Leave the branch». The answer comes back to step 4.
- Otherwise go on to step 4 in the next message.

## 4. Publish

- `pr`: `git push -u origin <branch>`. An open pull request from step 1: put its URL in the report, then `gh pr comment <number> --body-file <runDir>/report.md` (the push already updated it). None: `gh pr create --base <base> --head <branch> --title "<plan title>" --body-file <runDir>/report.md`, then put the new URL in the report and `gh pr edit <number> --body-file <runDir>/report.md`, so the body is the final report (D-38). Then bind it with `mcp__ccd_pr__bind_pr` when you have it ("already bound" is fine).
- `merge`: only when step 1's `git status --porcelain` printed nothing and the current branch is the base; otherwise deliver as `branch` and say why. `git merge --no-ff --no-edit <branch>`. If it fails and `git rev-parse -q --verify MERGE_HEAD` passes, `git merge --abort`, and say "the branch does not merge cleanly: your checkout is as it was, the branch stays".
- After a pull request is created or updated, check it rather than trust it (D4), in one message: `gh pr view <number> --json state,headRefOid,mergeable,body` and `git rev-parse <branch>`. The `headRefOid` must be the branch's HEAD, and every commit the body cites must be on the branch, the newest of them its HEAD (`git merge-base --is-ancestor <sha> <branch>`, one call per commit, in the next message). A mismatch: rewrite the body once from the report (`gh pr edit <number> --body-file <runDir>/report.md`) and check again; still wrong, say so in the line and in a `decisions.md` row.
- A step that fails stops the delivery: say which and its message, `status: done-not-delivered` (the branch has the work; `/baton:status continue` retries from that step).

## 5. Close, in one message

Edit the report's delivery line (the URL, "merged locally into <base>", or why not) and, after a publish question, add the person's answer to "What needed you"; Write `state.json` with `status: delivered` and `delivery` complete (`url`, `comment` when one was posted), a push notification, and one line in the chat with the outcome and the report's path.

## The report

Fill `PLUGIN/templates/report.md`:

- the parts with their results (status, commits, gates, summary, from the result files); parts not done are said as pending;
- the lines of `settled.md`; the decisions table from `decisions.md`;
- commits from `git log --oneline <baseSha>..<branch>`, those before the first part's `startSha` marked "(earlier iteration)";
- the reviews table from the Grep: one row per review file, its verdict and the number of `### F-` headings;
- repeated findings: a `category` that appears in two or more plans of `findings.jsonl` gets one proposed rule for the repo's CLAUDE.md, in the repo's language; otherwise "None yet.";
- cost: the results' `reviewer_usage`, and "see the session's usage" for the implementer;
- "What needed you": one line per `presses` entry.
