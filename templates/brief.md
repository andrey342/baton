# Brief · `{{plan}}` · {{title}}

Your role and the rules of every part are in `{{workerRunDir}}/implementer.md`: read it first if you have not yet. This brief holds the whole plan; each message from the coordinating chat names the one part to do now and the commit it starts from. Do only that part.

## Where you are

- Folder (the plan's worktree): `{{worktree}}`
- Branch: `{{branch}}`, from `{{base}}` at `{{baseSha}}`.
- Run folder for your results and the reviews: `{{workerRunDir}}` (excluded from git).
- The plan, as launched: `{{planCopy}}`.
- Iteration {{iteration}} of this plan{{iterationNote}}.

## Before the first part

Install command to run once, before anything else, from the folder: {{install}}. If it fails, end with `status: blocked` and its last lines.

## The repo's rules that apply

{{rules}}

Skills of this repo to load and follow: {{implementerSkills}}

Gates of this repo, exactly as written: {{gates}}

## Already decided (from the plan)

{{alreadyDecided}}

Answers settled while the plan runs are appended to `{{workerRunDir}}/settled.md`; they count as decided too. Read it when you start each part.

## The parts, as the plan writes them

{{parts}}

## For the reviewer

Review loop: at most {{reviewRounds}} rounds per part. Reviewer subagent: `baton:reviewer` when that type is listed, else `general-purpose` with the text of `{{workerRunDir}}/reviewer.md` (without its frontmatter) at the top of the prompt. Model `{{reviewerModel}}`, effort `{{reviewerEffort}}`.

Prompt for each round (fill the part, its start commit from the coordinating chat's message, the round and the previous review):

> Review part <part> of the plan `{{planCopy}}` in the folder `{{worktree}}`: the changes from `<start commit>` to `HEAD`. Round <n> of {{reviewRounds}}. Gates: {{gates}}. Run folder with earlier reviews: `{{workerRunDir}}`; answers settled during the run: `{{workerRunDir}}/settled.md`; previous review of this part: <path or "none">. Skills of this repo to load first: {{reviewerSkills}}. Answer with the review text only, first line `Verdict: OK|NO|BLOCKED`.

Save each answer verbatim as `{{workerRunDir}}/review-<part>-r<n>.md`.

## How you end

Save `{{workerRunDir}}/result-<part>.md` and end the turn with the same `baton-result` block, as `implementer.md` says.

{{extra}}
