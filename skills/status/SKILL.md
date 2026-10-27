---
name: status
description: >-
  Show where baton's plans in this repo stand (parts done, at work and pending, what waits for the person, the implementer session, the delivery), pause a plan so it can go on later and continue it (from this chat or another), pick it up again after the app was closed, stop it for good, or close a delivered one once the person has merged it (the repo's close hooks, back to the base, local exclusions removed). Use when the person asks how a plan is going, to pause, continue or resume it, to stop it, or says it is merged, e.g. "how is the plan going?", "¿cómo va el plan?", "para", "pausa el plan", "sigue", "continúa con el plan", "retoma baton", "stop the plan", "cancela el plan", "ya está mergeado, cierra".
argument-hint: "[run] [pause|continue|stop|close]"
---

# /baton:status

Arguments: `$ARGUMENTS`: an optional run id (the folder name under `.claude/runs/`) and an optional action. "sigue", "continúa", "retoma" and "continue" mean `continue`; "para", "pausa" and "pause" mean `pause` (D10: the run can go on later); "stop", "detén el plan", "cancela el plan" and "termina el plan aquí" mean `stop`, the end of the run; "cierra", "close", "merged" and "ya está mergeado" mean `close`. When "para" comes with words that end the run ("para el plan del todo", "no sigas nunca"), it is `stop`; unsure, it is `pause`, which loses nothing.

The app's tools named below (`get_session`, `stop_session`, SendMessage, `start_session`) often arrive deferred: when one is listed only by name, load it with ToolSearch (`select:<name>`) before deciding you do not have it. The run's files and their fields are described in `${CLAUDE_PLUGIN_ROOT}/skills/run/SKILL.md` ("Files"); `state.json` is shaped like `${CLAUDE_PLUGIN_ROOT}/templates/state.json`. Talk to the person in the language of the conversation. When the conversation holds nothing from them but the command, take the language of their earlier messages or of their own CLAUDE.md (user memory or instructions in your context); if nothing says, the plan's language (D-41).

## Which runs

Read every `.claude/runs/*/state.json` under `git rev-parse --show-toplevel`. A run is `version` 1 (baton 0.2; no `version` counts as 1) or 2: read both as "State versions" in `${CLAUDE_PLUGIN_ROOT}/skills/event/SKILL.md` says, and never rewrite a v1 run as v2. Open runs are those with `status` `running`, `waiting`, `done-not-delivered` or `dry-run`, and in v2 also `proposed`, `paused` or `closing`. With a run id, only that one; without one, an action applies to the only open run (with several, list them and ask which). For `close`, the runs it can apply to are the **closable** ones instead: `delivered` or `stopped` without `closedAt`.

## No action: report

For each open run, and the last finished one, a few lines:

- the title, the status, the branch (with several repos, each repo's branch and base, and `workspace: checkout` when the run works in this checkout), the iteration and the mode;
- the parts: `✓ A <title> (review r2 OK)`, `● B <title> (at work)`, `○ C <title> (pause before)`;
- what waits for the person, in full, when `waiting` is set, and how to answer (reply in this chat, or the button offered);
- the implementer session as a link, `[baton · <title>](#local_<id>)`, and whether it still exists (`mcp__ccd_session_mgmt__get_session`, when you have it): v1, `worker`; v2, the `session` of each part that has one, with the part's implementer model and effort;
- `messagesSinceUser`, decisions so far, and the delivery (mode, pull request URL, worktree removed or kept) when done.

A report changes nothing: do not send messages, start sessions or deliver from it. End with what the person can say next ("sigue" to pick it up, "para" to pause it, "stop" to end it).

## pause

For an open run that is `running` or `waiting` (D10). A `proposed` run has nothing at work: «para» there is `/baton:run`'s stop. A `closing` run finishes its delivery or close first: say so. The person's word resets the quota (`messagesSinceUser` and `wakesSinceUser` to 0), so there is room for these messages.

1. **Read, in one message:** `state.json`, `get_session` for each part whose status is `working` (its `session.id`; v1: `worker.sessionId`), and the time.
2. **Act, in one message:**
   - `mcp__ccd_session_mgmt__stop_session` for each of those sessions that is running a turn now, to stop it at once;
   - then, to each of them, SendMessage "baton · pausa: guarda tu estado en `pause-<X>.md` (qué está hecho, qué está a medias, qué toca después), no uses computer use y termina con status: paused", each adding 1 to `messagesSinceUser`;
   - Write `state.json`: `status: paused`, those parts `paused`, `paused: { "at", "from": <the status before>, "waiting": <the waiting before>, "parts": [<ids>] }` and `waiting: null`;
   - a `decisions.md` row "paused by the person: <parts>".
   
   A part with no session at work gets no message, and its line says so. A card not clicked stays as it is, and `continue` follows "a card still waiting" in `/baton:event` for it, never a new start on a guess. A session that is gone is started again on `continue`, from its brief.
3. **The one line:** what was paused, and that "sigue" or `/baton:status continue` picks it up. Each session's `paused` result then reaches `/baton:event`, which checks its `pause-<X>.md` and leaves the run paused.

The person's «para» while a turn of theirs has nothing at work (a run `waiting` on a question, say) still pauses: the waiting question is kept in `paused.waiting` and asked again on `continue`.

## continue

For a `paused` run, follow "Resuming a paused run" in `/baton:event`. Otherwise, follow "Resuming" in `/baton:event` (`${CLAUDE_PLUGIN_ROOT}/skills/event/SKILL.md`; load it unless its text is already in this conversation) for this run. This turn is the person's, so a lost implementer session may be started again there. For a `done-not-delivered` run, retry the delivery (`${CLAUDE_PLUGIN_ROOT}/skills/event/deliver.md`) from the step that failed. For a `dry-run` (a 0.2 run), say it was a dry run and that `/baton:run <plan>` launches it for real, reusing its worktree. For a `proposed` run, follow "Resuming" in `/baton:event` as for any other run: an approved table goes to the launch, an unapproved one is shown again with its buttons.

## close

For the closable run (one without a run id; with several, list them and ask which), follow "The close" in `${CLAUDE_PLUGIN_ROOT}/skills/run/hooks.md`:
- a `delivered` run, once the person says they merged: the repo's `onClose` and `afterMerge`, then each repo of a checkout run back to its base, and the `excluded` lines removed;
- a `stopped` run: nothing was merged, so no `onClose` or `afterMerge`, only the repos back to their bases and the exclusions removed.

This turn is the person's, so a session the close needs may be started. A run that is not closable: say what it waits for instead. When the person's words also ask to archive the sessions («y archiva las sesiones»), that is the yes for "Archiving sessions" in `/baton:event`. With that yes, or `archiveSessions` already true, each part's session not yet archived is archived once the close's steps are done (the last part's session runs its hooks first), with refusals handled as that section says.

## stop

`stop` is the end of the run (D10); to go on later, `pause`. A `paused` run can be stopped too.

1. Set `status: stopped` and `waiting: null` in `state.json`, with `updatedAt`. Lines the run added to an exclude file (`state.excluded`) stay until the close; say so, and that `/baton:status close` removes them.
2. If the implementer session (v1 `worker`, v2 the current part's `session`) is working, stop its turn with `mcp__ccd_session_mgmt__stop_session` when you have it; never archive or delete it.
3. Add a row to `decisions.md`: stopped by the person (a `proposed` run may have none yet: Write it with the header `| When | Part | Stop | Decision | Why |` and its separator first).
4. Say what stays: the branch, the worktree with its path, and the commits so far (`git log --oneline <baseSha>..<branch>`, one per repo with several). To remove the worktree yourself later: `git worktree remove .claude/worktrees/baton-<run>`. A checkout run has no worktree: each repo stays on the plan's branch, and `git -C <path> switch <base>` takes it back. Nothing is deleted.
