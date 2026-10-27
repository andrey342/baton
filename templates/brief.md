# Brief · `{{plan}}` · {{title}}

Your role and the rules of every part are in `{{workerRunDir}}/implementer.md`: read it first if you have not yet. This brief holds the whole plan; the message that started your session names the one part to do and its start commit in each repo. Do only that part. When yours is not the first part, read the earlier parts' `result-*.md` in the run folder and `git log` up to your start commits before anything else.

## Where you are

- Folder (the plan's worktree, or the checkout itself): `{{worktree}}`
- Branch: `{{branch}}`, from `{{base}}` at `{{baseSha}}`.
- Repos of this plan, each on that branch, and each part works only in the ones its **Repos:** line names:
{{repos}}
- Run folder for your results and the reviews: `{{workerRunDir}}` (excluded from git).
- The plan, as launched: `{{planCopy}}`.
- Iteration {{iteration}} of this plan{{iterationNote}}.

## Before the first part

Install command to run once, before anything else, from the folder: {{install}}. The first part's session runs it; a later part's session runs it again only when the folder lacks what it installs. If it fails, end with `status: blocked` and its last lines.

## The repo's rules that apply

{{rules}}

Skills of this repo to load and follow: {{implementerSkills}}

Gates of this repo, exactly as written: {{gates}}

## Already decided (from the plan)

{{alreadyDecided}}

Answers settled while the plan runs are appended to `{{workerRunDir}}/settled.md`; they count as decided too. Read it when you start your part.

## The parts, as the plan writes them

{{parts}}

## For the reviewer

Review loop: at most {{reviewRounds}} rounds per part. Reviewer subagent: `baton:reviewer` when that type is listed, else `general-purpose` with the text of `{{workerRunDir}}/reviewer.md` (without its frontmatter) at the top of the prompt. Model, effort and skills: the part's **Reviewer** line above, approved by the person with the plan's model table; `run_in_background: false` when the Agent tool takes it, and in any case wait for the verdict before you end the turn.

Prompt for each round (fill the part, its **Review from** line with the start commits of the message that started the part, the round, the previous review and the part's reviewer skills):

> Review part <part> of the plan `{{planCopy}}` in the folder `{{worktree}}`: the changes from <the part's **Review from** line: one "<repo> `<start commit>` in `<path>`" per repo of the part> to `HEAD` in each of those repos. Round <n> of {{reviewRounds}}. Gates: {{gates}}. Run folder with earlier reviews: `{{workerRunDir}}`; answers settled during the run: `{{workerRunDir}}/settled.md`; previous review of this part: <path or "none">. Skills of this repo to load first: <the part's reviewer skills, or "none">. Answer with the review text only, first line `Verdict: OK|NO|BLOCKED`, second line `Model: <your model id>`.

Save each answer verbatim as `{{workerRunDir}}/review-<part>-r<n>.md`.

**The Critic**, for a part with a **Critic** line, after its review is OK: the same subagent type with that line's model and effort, and this prompt:

> You are the Critic of part <part> of the plan `{{planCopy}}` in the folder `{{worktree}}`: the changes from <the part's **Review from** line, filled> to `HEAD` in each of those repos. Critic round <n>. Gates: {{gates}}. Run folder with the part's reviews and earlier Critic rounds: `{{workerRunDir}}`; answers settled during the run: `{{workerRunDir}}/settled.md`; previous Critic round: <path or "none">. Skills of this repo to load first: <the part's Critic skills, or "none">. Answer with the review text only, first line `Verdict: PASS|FAIL`, second line `Model: <your model id>`.

Save each answer verbatim as `{{workerRunDir}}/critic-<part>-r<n>.md`. A FAIL is closed by fixing its findings, one more review round and the Critic again, until it reads PASS: at most {{reviewRounds}} Critic rounds, and the review rounds it adds count toward the part's {{reviewRounds}}.

## How you end

Save `{{workerRunDir}}/result-<part>.md` and end the turn with the same `baton-result` block, as `implementer.md` says.

{{extra}}
