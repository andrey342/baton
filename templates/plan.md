# <What this plan does>

One or two lines on the goal. baton proposes a model for each part and waits for your yes, then runs the parts below in order, each reviewed by a fresh read-only reviewer until OK, and delivers the way this repo asks.

baton: mode=normal

<!--
Options on the `baton:` line, all optional, space-separated `key=value`:
  mode=cheap|normal|thorough   where baton's model proposal starts (the profile's models.start otherwise); you approve the table
  models=B:opus/high,C:sonnet  starting points for the implementer of the parts named; you approve the table
  delivery=branch|pr|merge|none   overrides the profile for this plan
  branch=<name>   work on this branch (an existing one, for a second iteration on an open pull request)
  base=<ref>      base branch for the worktree and the pull request (default: the profile's, else the current branch)
  partHeading=<regex>   headings that are parts, with a named group id, for a plan numbered its own way (e.g. ^(?:\d+(?:\.\d+)*\s+)?(?<id>P\d+|CA)\b)
  decided=§5,§13   numbered sections that count as "Already decided"
A plan in another format can stay as it is: /baton:plan --adapt <plan> writes a map baton uses instead.
-->

## Already decided

Facts the implementer may need and should not ask about. baton's supervisor answers questions from this section, the parts and the repo's rules; anything not written here comes to you.

- …

## Part A — <first piece of work>

What to do, in plain words: the files, the behaviour, what is already decided.

**Acceptance**
- A check a reviewer can run or read (a test passes, a command prints something).
- Another one.

## Part B — <next piece>

What to do.

**Acceptance**
- …

## Pause before part C

A heading or a line that starts with "Pause" makes baton stop there and ask you to continue, once. Delete it if you want the plan to run through.

## Part C — <last piece>

What to do.

**Acceptance**
- …
