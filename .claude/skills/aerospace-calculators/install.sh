#!/usr/bin/env bash
# Install the aerospace-calculators Claude skill at the user level.
#
# Usage:
#   bash .claude/skills/aerospace-calculators/install.sh
#
# The script is idempotent — re-running it overwrites the installed copy
# of the skill manifest and refreshes the recorded repo path.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
TARGET_DIR="${HOME}/.claude/skills/aerospace-calculators"

bold() { printf "\033[1m%s\033[0m\n" "$*"; }
green() { printf "\033[32m%s\033[0m\n" "$*"; }
yellow() { printf "\033[33m%s\033[0m\n" "$*"; }
red() { printf "\033[31m%s\033[0m\n" "$*"; }

bold "Installing the aerospace-calculators Claude skill"
echo "  source repo  : $REPO_ROOT"
echo "  install path : $TARGET_DIR"
echo

# 1. Sanity-check tools.
if ! command -v node >/dev/null 2>&1; then
  red "Node.js is required but was not found on PATH."
  echo "Install Node 18+ from https://nodejs.org or via your package manager."
  exit 1
fi
if ! command -v npx >/dev/null 2>&1; then
  red "npx is required but was not found on PATH."
  exit 1
fi

# 2. Make sure the calculator library is installable from the repo.
if [ ! -d "$REPO_ROOT/frontend/node_modules" ]; then
  yellow "frontend/node_modules not present — running 'npm install' (≈ 10s)."
  (cd "$REPO_ROOT/frontend" && npm install --no-audit --no-fund --loglevel=error)
fi

# 3. Copy skill files to ~/.claude/skills/aerospace-calculators/.
mkdir -p "$TARGET_DIR"
for f in SKILL.md CATALOG.md EXAMPLES.md INSTALL.md; do
  if [ -f "$SCRIPT_DIR/$f" ]; then
    cp "$SCRIPT_DIR/$f" "$TARGET_DIR/$f"
    echo "  copied $f"
  else
    yellow "  WARN: missing $f in source skill folder"
  fi
done

# 4. Record the repo path so the skill can resolve absolute imports.
echo "$REPO_ROOT" > "$TARGET_DIR/.repo_path"
echo "  wrote .repo_path → $REPO_ROOT"

# 5. Smoke test: invoke a calculator via tsx.
SMOKE_FILE="$(mktemp -t aerocalc-XXXXX.ts)"
trap 'rm -f "$SMOKE_FILE"' EXIT
cat > "$SMOKE_FILE" <<EOF
import { predictedHeatStrain, planZhL16Gf, niermeyerSpo2 } from '$REPO_ROOT/frontend/src/calculators';

const phs = predictedHeatStrain(200, 35, 35, 50, 0.3, 0.5, 60);
const dive = planZhL16Gf({ max_depth_m: 30, bottom_time_min: 25, gas: { o2: 0.21 } });
const sp   = niermeyerSpo2(3000, 'male');

console.log('PHS predictedCoreTemp_C  =', phs.predictedCoreTemp_C.toFixed(2));
console.log('Bühlmann stops           =', dive.stops.length);
console.log('Niermeyer SpO2 @ 3000 m  =', sp.predicted_spo2);
EOF

echo
bold "Smoke-testing the calculator import …"
if (cd "$REPO_ROOT/frontend" && npx --no-install tsx "$SMOKE_FILE" 2>&1); then
  green "✓ skill installed and verified"
else
  red "✗ skill files copied, but the smoke test failed."
  red "  Check that 'cd \"$REPO_ROOT/frontend\" && npx tsx -e \"console.log(1)\"' works."
  exit 1
fi

cat <<EOF

Next steps:
  • Restart Claude Code (or any agent that reads ~/.claude/skills/) so it
    picks up the new skill.
  • Try a prompt like:
      "Plan a 40 m / 35 min air dive using ZH-L16-C with 30/85 GF."
    The agent should invoke the planZhL16Gf calculator from
    $REPO_ROOT/frontend/src/calculators.

  • Update later by re-running:
      bash $SCRIPT_DIR/install.sh
EOF
