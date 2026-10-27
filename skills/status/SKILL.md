---
name: status
description: >-
  Show where baton's plans in this repo stand (parts done, at work and pending, what waits for the person, the implementer session, the delivery), pick a plan up again after the app was closed, or stop it. Use when the person asks how a plan is going, to continue or resume it, or to stop it, e.g. "how is the plan going?", "¿cómo va el plan?", "sigue", "continúa con el plan", "retoma baton", "para el plan", "stop the plan".
argument-hint: "[run] [continue|stop]"
---

# /baton:status

Arguments: `$ARGUMENTS`: an optional run id (the folder name under `.claude/runs/`) and an optional action. "sigue", "continúa", "retoma" and "continue" mean `continue`; "para" and "stop" mean `stop`.

The app's tools named below (`get_session`, `stop_session`) often arrive deferred: when one is listed only by name, load it with ToolSearch (`select:<name>`) before deciding you do not have it. The run's files and their fields are described in `${CLAUDE_PLUGIN_ROOT}/skills/run/SKILL.md` ("Files"); `state.json` is shaped like `${CLAUDE_PLUGIN_ROOT}/templates/state.json`. Talk to the person in the language of the conversation. When the conversation holds nothing from them but the command, take the language of their earlier messages or of their own CLAUDE.md (user memory or instructions in your context); if nothing says, the plan's language (D-41).

## Which runs

Read every `.claude/runs/*/state.json` under `git rev-parse --show-toplevel`. A run is `version` 1 (baton 0.2; no `version` counts as 1) or 2: read both as "State versions" in `${CLAUDE_PLUGIN_ROOT}/skills/event/SKILL.md` says, and never rewrite a v1 run as v2. Open runs are those with `status` `running`, `waiting`, `done-not-delivered` or `dry-run`, and in v2 also `proposed`, `paused` or `closing`. With a run id, only that one; without one, an action applies to the only open run (with several, list them and ask which).

## No action: report

For each open run, and the last finished one, a few lines:

- the title, the status, the branch (with several repos, each repo's branch and base, and `workspace: checkout` when the run works in this checkout), the iteration and the mode;
- the parts: `✓ A <title> (review r2 OK)`, `● B <title> (at work)`, `○ C <title> (pause before)`;
- what waits for the person, in full, when `waiting` is set, and how to answer (reply in this chat, or the button offered);
- the implementer session as a link, `[baton · <title>](#local_<id>)`, and whether it still exists (`mcp__ccd_session_mgmt__get_session`, when you have it): v1, `worker`; v2, the `session` of each part that has one, with the part's implementer model and effort;
- `messagesSinceUser`, decisions so far, and the delivery (mode, pull request URL, worktree removed or kept) when done.

A report changes nothing: do not send messages, start sessions or deliver from it. End with what the person can say next ("sigue" to pick it up, "para" to stop it).

## continue

Follow "Resuming" in `/baton:event` (`${CLAUDE_PLUGIN_ROOT}/skills/event/SKILL.md`; load it unless its text is already in this conversation) for this run. This turn is the person's, so a lost implementer session may be started again there. For a `done-not-delivered` run, retry the delivery (`${CLAUDE_PLUGIN_ROOT}/skills/event/deliver.md`) from the step that failed. For a `dry-run` (a 0.2 run), say it was a dry run and that `/baton:run <plan>` launches it for real, reusing its worktree. For a `proposed` run, follow "Resuming" in `/baton:event` as for any other run: an approved table goes to the launch, an unapproved one is shown again with its buttons.

## stop

1. Set `status: stopped` and `waiting: null` in `state.json`, with `updatedAt`.
2. If the implementer session (v1 `worker`, v2 the current part's `session`) is working, stop its turn with `mcp__ccd_session_mgmt__stop_session` when you have it; never archive or delete it.
3. Add a row to `decisions.md`: stopped by the person (a `proposed` run may have none yet: Write it with the header `| When | Part | Stop | Decision | Why |` and its separator first).
4. Say what stays: the branch, the worktree with its path, and the commits so far (`git log --oneline <baseSha>..<branch>`, one per repo with several). To remove the worktree yourself later: `git worktree remove .claude/worktrees/baton-<run>`. A checkout run has no worktree: each repo stays on the plan's branch, and `git -C <path> switch <base>` takes it back. Nothing is deleted.
