---
name: plan
description: >-
  Turn the current conversation into a baton plan file, written from baton's template: a goal, an "Already decided" section with every fact settled in the conversation, parts in order with acceptance criteria a reviewer can check, pauses where a person must decide, and the baton options line. With --adapt, read an existing plan written in another format (a versioned document with its own numbering) without changing it, show what baton understands, and write a map of it that /baton:run uses while the plan stays the same. Use when the person asks to write, save or turn the discussion into a plan to run with baton, e.g. "write the plan", "escribe el plan", "conviértelo en un plan", "guárdalo como plan para baton", "haz un plan con esto"; and with --adapt to make baton run a plan it would not parse, e.g. "adapta este plan para baton", "baton, entiende este plan".
argument-hint: "[path/to/plan.md] [title] | --adapt <plan.md>"
---

# /baton:plan

Arguments: `$ARGUMENTS` (optional: the file to write, and a title). With `--adapt <plan.md>`, follow "--adapt" below instead of the steps.

The template is `${CLAUDE_PLUGIN_ROOT}/templates/plan.md`: read it now. What `/baton:run` reads from a plan is in `${CLAUDE_PLUGIN_ROOT}/skills/run/SKILL.md`, step 1.5 (part headings, criteria labels, pauses, the `baton:` line); the plan you write must parse that way.

## Steps

1. **Gather** from the conversation (and the text given with the command, if any): the goal, what has been decided (choices, constraints, names, files, preferences the person stated), the work in the order it should happen, and what is still open. Read the files the conversation names when a criterion depends on them (a test command, a file path). Do not invent requirements the conversation does not support.
2. **Where.** The path given; else the folder the repo's rules or existing plans use (`docs/plans/` when it exists or nothing says otherwise), with a short kebab-case file name from the goal. Never overwrite a file: pick another name and say so.
3. **Language.** The plan is in the language of the conversation, unless the repo's rules ask for another. Part headings and criteria labels may be in English or Spanish ("Part A —" / "Parte A —", "Acceptance" / "Aceptación"); keep one language throughout.
4. **Earlier decisions**, before anything is written. Read, whole, the `settled.md` and `decisions.md` of the repo's earlier runs (Glob `.claude/runs/*/settled.md` and `.claude/runs/*/decisions.md`; the five runs changed most recently when there are more). The person's answers are the lines "from the person" and the section `## Delegated by the person` of `settled.md`, and the rows of `decisions.md` that record a choice of theirs. A run coordinated by hand writes them in its own words, so read them for what they say. A line of the plan you are about to write that contradicts one is a clash: delegating what they kept for themselves, say, or deciding what they decided otherwise. Show each clash to the person with the earlier line quoted, and write what they choose in step 5. With no one to answer, write the clash as a pause before the part it touches.
5. **Write** it with the template's structure:
   - `# <title>` and one or two lines on the goal.
   - The `baton:` line: `mode=normal`, plus `delivery=` or `base=` only when the conversation settled them. Drop the template's HTML comment.
   - **Already decided**: one line per settled fact, concrete enough to answer a question with ("Dates are stored in UTC", "Keep the old /login route for one release"). This is what baton's supervisor answers from; anything left out comes back to the person.
   - **Parts**: one to seven, each a piece of work a reviewer can judge on its own diff, in order, `## Part A — <title>`, then what to do in plain words (files, behaviour, what is out of scope) and an **Acceptance** list of two to five checks a reviewer can run or read: a command and its expected result, a test that must exist and pass, a file that must contain something, a behaviour with its input and output. No "works well", "clean code" or criteria nobody can check.
   - **Pauses**: a `## Pause before part <X>` heading only where the conversation said a person decides or looks before going on, or where an open question blocks a part (write the question in the pause).
6. **Open questions.** At most one question to the person, with AskUserQuestion, and only when an answer changes the parts. With no one to answer (a non-interactive run), write the question as a pause before the part it blocks.
7. **Close** with one line: the plan's path, its parts and pauses, that it is not committed, and the command to run it: `/baton:run <path>`.

## --adapt <plan.md>

The plan stays exactly as it is: in a repo like MSG it is a versioned document ("v0.8 LISTO PARA IMPLEMENTAR"), so `--adapt` never edits, moves or rewrites it (D8). It writes one file, the map `.claude/runs/_maps/<plan name>.json` (`<plan name>` is the file name without extension), shaped like `${CLAUDE_PLUGIN_ROOT}/templates/map.json`.

1. **Read, in one message:** the plan; `.claude/baton.json` (its `repos`, `plan.partHeading` and `plan.decided`); `git hash-object <plan>`; the map if one exists; `git rev-parse --git-common-dir`; `${CLAUDE_PLUGIN_ROOT}/templates/map.json`; `date -u +%Y-%m-%dT%H:%M:%SZ`.
2. **Analyse** with the rules of `/baton:run` step 1.5 (`partHeading`, the title that never counts, inline acceptance, `decided`, pauses between and inside parts), and with what the plan itself says where those rules fall short:
   - **Parts**: every heading the `partHeading` (or the default form) matches. A heading it does not match that the plan's own order treats as a step of its own, such as «7.4 Cierre de la Parte A» between P3 and the pause in an "Orden fijo: P0 → … → cierre de la Parte A → pausa → P4", is a part too. Give it a short id (the profile's `partHeading` alternatives first, `CA` here, else its initials), with an `idFrom` saying why.
   - For each part: its `heading` and the `lines` its text spans (from its heading to the next part's or the next heading of the same level, with the line numbers of the file as it is now); `repos` from a `**Repos:**` line, a partition table, or the paths it names, with `reposFrom`; `criteria`, from the acceptance list or line, or the part's gates and closing steps when it has none, quoted as written.
   - **Pauses between parts**: a "pausa obligatoria", "no se empieza P4 sin el OK" or the like gives `pauseBefore` on the part it holds back, with its text. A delivery the plan asks for just before it ("push del backend", "solo con autorización") is that pause's `pauseDeliver` and an entry of `deliveries`.
   - **Pauses inside a part**: a step the plan stops before ("Parada: …", "(parada b)", "antes del reset de P2.8", or a list of the plan's stops such as "Paradas cerradas: (a) el reset de P2.8, (b) la elección de diseño de P4.0") goes into that part's `pauses` with the step's id and its text. A stop between parts in such a list is the pause between them.
   - **Decided**: the "Already decided" sections and those `decided` names, each with its heading and lines. Sections that read as settled ("Decisiones … (tomadas)", "Decisiones del usuario") but are not named are a doubt, not a decision.
3. **Show what you understood**, in the person's language, in one message: a table with one row per part (id, title, the line it starts on, repos, criteria in a few words, pauses inside), then the pauses between parts with their deliveries, the decided sections, and the doubts. Propose a `baton:` line for the plan (with `partHeading=` when the profile has none, and `decided=`) as text the person may paste; it is never written into the plan.
4. **Doubts**: what the plan leaves open (an id baton gave, repos read from paths, a section that may or may not be decided, a pause whose place is unclear). Ask them with AskUserQuestion, at most four in one call, and only those that change the parts, their repos or their pauses. With no one to answer (a non-interactive run), take the reading that stops more rather than less (a pause kept, a section left undecided) and record it.
5. **Write the map**, with Write (it creates `_maps/`): `version`, `plan` (repo-relative path), `hash` (step 1's), `madeAt`, `title`, `partHeading`, `decided`, `parts`, `deliveries`, `doubts` (each with `question`, `reading` and `answeredBy`: the person's words, or "the reading (no one to ask)"), and `proposedBatonLine`. In the same message: `<common-dir>/info/exclude` holds `/.claude/runs/` (Edit to add it, or Write it if absent), so the map stays out of git; and `git hash-object <plan>` again.
6. **Close** with one line: the parts and pauses found, the map's path, that the plan's hash is the same before and after (say both; a different one means something changed the plan while you read it, so say so and write no map), and that `/baton:run <plan>` now uses the map until the plan changes.

## Never

- Start the plan, create branches or sessions, or commit: this skill only writes the plan file, or with `--adapt` only the map.
- Change a plan with `--adapt`: no Edit or Write on the plan file, ever.
- Put commands that publish or delete in a part (push, pull request, merge, release): baton delivers at the end the way the repo asks.
