# Reading a repo's rules into a baton profile

Shared by `/baton:setup` and by `/baton:run` when the repo has no `.claude/baton.json`. Read only; nothing here writes. Run shell commands one at a time from the repo's top folder (`git rev-parse --show-toplevel`), never chained.

## 1. What to read, if it exists

- Rules: `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `.claude/CLAUDE.md`, every file in `.claude/rules/`.
- Repo skills: `.claude/skills/*/SKILL.md`, only the `name` and `description` of each. Repo agents: `.claude/agents/*.md`, only the names.
- Settings: `.claude/settings.json` and `.claude/settings.local.json`, for hooks, `permissions.deny`/`allow` and `enabledPlugins`. Never change them. Only `settings.json` (committed) reaches a plan's worktree; `settings.local.json` is not there.
- `.mcp.json`, only the server names.
- The stack: `package.json` (its `scripts` and `packageManager`), lockfiles (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lockb`), `*.sln`/`*.csproj`, `pyproject.toml`/`requirements*.txt`, `Cargo.toml`, `go.mod`, `Makefile`.
- Git: `git remote -v`, `git symbolic-ref --short refs/remotes/origin/HEAD` (may fail: no origin), `git branch --list main master develop`, `git branch --show-current`.
- Only when the rules ask for pull requests and there is an `origin`: `gh auth status`.

## 2. What to take from it

Each key below is **detected** only when something above says it; otherwise it keeps the default and is not written.

| Key | Detected from | Default |
|---|---|---|
| `base` | the branch the rules say work starts from or merges into; else `origin/HEAD`; else the one of `main`, `master`, `develop` that exists | the checkout's current branch |
| `branchPrefix` | the rules' lines about branches: the prefix they ask for (`feat/`, `fix/`, `feature/`, `codex/`…). When they give one per kind of work (`feat/` for features, `fix/` for fixes), take the one for features and say both | `baton/` |
| `gates` | the commands the rules name to check work (tests, lint, build, typecheck), exactly as written; else by stack: `npm test` when `package.json` has a real `test` script (not npm's default `echo "Error: no test specified" && exit 1`), plus `npm run lint` when it has `lint`; `dotnet test`; `pytest`; `cargo test`; `go test ./...`. Use the package manager the lockfile names (`pnpm test`, `yarn test`) | none |
| `install` | the rules' setup command; else by lockfile: `npm ci`, `pnpm install --frozen-lockfile`, `yarn install --frozen-lockfile`, `bun install --frozen-lockfile`; `dotnet restore` for a solution; nothing for Python, Rust, Go | none |
| `delivery` | `pr` when the rules ask for a pull request and there is an `origin` and `gh auth status` passes; `merge` when they ask for a local merge; `branch` when they say to leave the branch | `branch` |
| `humanBeforePublish` | `true` when the rules ask for explicit authorization before a push, a pull request or a merge | `false` |
| `rules` | the rule files that exist, repo-relative | none |
| `roles.implementer.skills`, `roles.reviewer.skills` | repo skills whose description says they apply to writing code, reviewing, commits or conventions; both roles get the convention skills. Write `roles` only when a skill was detected, and only `skills` under it: a role's `model` and `effort` stay out of the profile unless the person set them | `[]` |
| `notes` | in one or two lines each, the repo's own processes the implementer and the reviewer must respect: a commit convention, levels of review, files never to touch, a language for user-facing text. It goes into every brief, so baton's own reasoning (why the delivery is what it is) stays out of it | `""` |

- A rule that asks for a pull request but the repo has no `origin`, or `gh` is missing or not signed in: `delivery` stays `branch`, and say why.
- A rule that contradicts baton (for example "never use worktrees", "commit only when asked") wins: put it in `notes` in its own words, so the brief passes it to the implementer, and say it.
- At most one open question, and only when the rules are ambiguous on something that changes the run (two base branches, two delivery styles). Everything else is decided from what is written and said.

## 3. The profile

The profile is `.claude/baton.json` with `version: 1` and the detected keys only. Its full shape, with every default, is the plugin's `templates/baton.json` (the skill that sent you here gives its absolute path). A key the profile leaves out takes the default of the table above; `reviewRounds` defaults to 3, and `roles` and `modes` to the values in that template.
