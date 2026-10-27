---
name: setup
description: >-
  Read this repo's rules (CLAUDE.md, AGENTS.md, CONTRIBUTING.md, .claude/rules, skills, settings, the stack) and write baton's repo profile, .claude/baton.json, with the gates, install command, branch prefix, base branch and delivery it finds. Use when the person asks to set up or configure baton for a repo, or to see what baton would detect, e.g. "set up baton here", "prepara el repo para baton", "configura baton", "¿qué detecta baton en este repo?". Optional: /baton:run does the same reading on its first run.
argument-hint: "[--show] [--template]"
---

# /baton:setup

Arguments: `$ARGUMENTS`

- `--show`: say what you find and the profile you would write; write nothing.
- `--template`: also copy the plan template to `docs/plans/TEMPLATE.md` (when the repo keeps plans elsewhere, that folder), if no file is there yet.

Talk to the person in the language of the conversation. When the conversation holds nothing from them but the command, take the language of their earlier messages or of their own CLAUDE.md (user memory or instructions in your context); if nothing says, the language of the repo's rules (D-41). Files you write are in English unless the repo's rules say otherwise.

## Steps

1. **Read the repo** as `${CLAUDE_PLUGIN_ROOT}/skills/setup/detect.md` says (read that file now). The plugin's profile template, with every key and default, is `${CLAUDE_PLUGIN_ROOT}/templates/baton.json`. The folder must be a git repository with at least one commit; if it is not, say so and stop.
2. **An existing profile.** If `.claude/baton.json` exists, read it. Keys the person set and the rules do not contradict stay as they are; say in one line each key you would change and why, and change only those.
3. **Say what you found**, in a few short lines, before writing:
   - the rule files read and the repo skills worth loading;
   - gates, install command, base branch, branch prefix, delivery and `humanBeforePublish`, each marked *found in <file>* or *default*;
   - the repo's own processes that go into `notes`, and any rule that overrides baton;
   - `permissions.deny` rules and hooks the implementer session will meet (not changed). When `.claude/settings.local.json` has `permissions.deny` or `enabledPlugins`, add one line: a plan's worktree holds only committed files, so those local rules (and a plugin enabled only there) do not reach the implementer session; commit them in `.claude/settings.json` if they must.
4. **One question at most**, only when detect.md's rules leave something ambiguous that changes a run. Ask it with AskUserQuestion with two or three options; if no one can answer (a non-interactive run), take the option the repo's precedent favours and say so.
5. **Write** `.claude/baton.json` with `version: 2` and only the keys that were detected or the person set (never the defaults), 2-space JSON, with the Write tool. With `--show`, print the JSON instead and stop.
6. **Plan template.** With `--template`, copy `${CLAUDE_PLUGIN_ROOT}/templates/plan.md` as said above, unchanged. Without it, end with one line offering it ("`/baton:setup --template` adds the plan template to docs/plans/").
7. **Close** with one line: the profile is the repo's to commit or not, and `/baton:plan` or `/baton:run <plan.md>` is next.

## Never

- Change `.claude/settings*.json`, hooks, CLAUDE.md or any rule file.
- Write anything outside `.claude/baton.json` and, with `--template`, the template.
- Run the gates or the install command: setup only reads.
