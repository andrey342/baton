---
name: plan
description: >-
  Turn the current conversation into a baton plan file, written from baton's template: a goal, an "Already decided" section with every fact settled in the conversation, parts in order with acceptance criteria a reviewer can check, pauses where a person must decide, and the baton options line. Use when the person asks to write, save or turn the discussion into a plan to run with baton, e.g. "write the plan", "escribe el plan", "conviértelo en un plan", "guárdalo como plan para baton", "haz un plan con esto".
argument-hint: "[path/to/plan.md] [title]"
---

# /baton:plan

Arguments: `$ARGUMENTS` (optional: the file to write, and a title).

The template is `${CLAUDE_PLUGIN_ROOT}/templates/plan.md`: read it now. What `/baton:run` reads from a plan is in `${CLAUDE_PLUGIN_ROOT}/skills/run/SKILL.md`, step 1.5 (part headings, criteria labels, pauses, the `baton:` line); the plan you write must parse that way.

## Steps

1. **Gather** from the conversation (and the text given with the command, if any): the goal, what has been decided (choices, constraints, names, files, preferences the person stated), the work in the order it should happen, and what is still open. Read the files the conversation names when a criterion depends on them (a test command, a file path). Do not invent requirements the conversation does not support.
2. **Where.** The path given; else the folder the repo's rules or existing plans use (`docs/plans/` when it exists or nothing says otherwise), with a short kebab-case file name from the goal. Never overwrite a file: pick another name and say so.
3. **Language.** The plan is in the language of the conversation, unless the repo's rules ask for another. Part headings and criteria labels may be in English or Spanish ("Part A —" / "Parte A —", "Acceptance" / "Aceptación"); keep one language throughout.
4. **Earlier decisions**, before anything is written. Grep the repo's earlier runs for the person's answers (`.claude/runs/*/settled.md`, lines "from the person" and the section `## Delegated by the person`). A line of the plan you are about to write that contradicts one is a clash: delegating what they kept for themselves, say, or deciding what they decided otherwise. Show each clash to the person with the earlier line quoted, and write what they choose in step 5. With no one to answer, write the clash as a pause before the part it touches.
5. **Write** it with the template's structure:
   - `# <title>` and one or two lines on the goal.
   - The `baton:` line: `mode=normal`, plus `delivery=` or `base=` only when the conversation settled them. Drop the template's HTML comment.
   - **Already decided**: one line per settled fact, concrete enough to answer a question with ("Dates are stored in UTC", "Keep the old /login route for one release"). This is what baton's supervisor answers from; anything left out comes back to the person.
   - **Parts**: one to seven, each a piece of work a reviewer can judge on its own diff, in order, `## Part A — <title>`, then what to do in plain words (files, behaviour, what is out of scope) and an **Acceptance** list of two to five checks a reviewer can run or read: a command and its expected result, a test that must exist and pass, a file that must contain something, a behaviour with its input and output. No "works well", "clean code" or criteria nobody can check.
   - **Pauses**: a `## Pause before part <X>` heading only where the conversation said a person decides or looks before going on, or where an open question blocks a part (write the question in the pause).
6. **Open questions.** At most one question to the person, with AskUserQuestion, and only when an answer changes the parts. With no one to answer (a non-interactive run), write the question as a pause before the part it blocks.
7. **Close** with one line: the plan's path, its parts and pauses, that it is not committed, and the command to run it: `/baton:run <path>`.

## Never

- Start the plan, create branches or sessions, or commit: this skill only writes the plan file.
- Put commands that publish or delete in a part (push, pull request, merge, release): baton delivers at the end the way the repo asks.
