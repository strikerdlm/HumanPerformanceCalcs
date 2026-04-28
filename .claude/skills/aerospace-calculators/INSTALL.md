# Installing the aerospace-calculators skill

## What gets installed

This skill lets any LLM-backed agent (Claude Code, Claude API, Claude
desktop) reason over and execute the ~150 calculators in
`frontend/src/calculators/` of this repository.

The installer copies four files to `~/.claude/skills/aerospace-calculators/`:

| File | Purpose |
|---|---|
| `SKILL.md` | Manifest the agent reads on load. |
| `CATALOG.md` | Function-by-function reference (signatures, units, citations). |
| `EXAMPLES.md` | Copy-pasteable worked examples. |
| `.repo_path` | Absolute path of the source checkout, written at install time. |

The original files in `<REPO>/.claude/skills/aerospace-calculators/` stay
in place — they're the source of truth and will be used when the agent
runs from inside the repo.

## Install (one command)

From a clone of `strikerdlm/HumanPerformanceCalcs`:

```bash
bash .claude/skills/aerospace-calculators/install.sh
```

The script:
1. Checks Node + `npx tsx` are available.
2. Verifies `frontend/node_modules/` exists; if not, runs `npm install`
   inside `frontend/`.
3. Copies `SKILL.md`, `CATALOG.md`, `EXAMPLES.md` to
   `~/.claude/skills/aerospace-calculators/`.
4. Writes the absolute repo path to
   `~/.claude/skills/aerospace-calculators/.repo_path`.
5. Runs a smoke test (PHS at 35°C / 50% RH / 60 min) to confirm the
   import path is valid.

## Per-project (no copy)

If you only want the skill active when running Claude Code from inside
the repo, do nothing. Claude Code reads `<REPO>/.claude/skills/` at
session start.

## Verify

After install, ask Claude:

> *"Plan a 30 m / 25 min air dive with the Bühlmann ZH-L16-C model."*

The agent should pick up the `aerospace-calculators` skill, look up
`planZhL16Gf` in `CATALOG.md`, build a tsx invocation, and report the
stop schedule with the citation.

You can also manually verify the catalog is reachable:

```bash
ls ~/.claude/skills/aerospace-calculators/
cat ~/.claude/skills/aerospace-calculators/.repo_path
```

## Uninstall

```bash
rm -rf ~/.claude/skills/aerospace-calculators
```

## Updating

Re-run the installer after pulling new commits. It overwrites the four
files in place.

```bash
git pull
bash .claude/skills/aerospace-calculators/install.sh
```
