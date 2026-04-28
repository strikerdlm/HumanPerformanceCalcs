---
name: aerospace-calculators
description: |
  Validated aerospace medicine, industrial hygiene, and occupational health
  calculators (~150 functions across 28 TypeScript modules). Use when the
  user asks anything about altitude / hypoxia / TUC, Bühlmann decompression,
  nitrox / oxygen toxicity, heat / cold strain (PHS, WBGT, UTCI, PSI, sweat
  rate, wind chill, frostbite), fatigue / circadian / sleep (SAFTE, jet lag,
  KSS, Epworth, PSQI), aviation duty time (FAA Part 117, EASA ORO.FTL),
  aircrew cosmic-radiation dose, AGSM Gz tolerance, spatial disorientation,
  NVG / EO target acquisition, motion sickness (MSSQ), whole-body or
  hand-arm vibration (ISO 2631-1, ISO 5349-1), noise dose (OSHA, NIOSH),
  ACGIH TLV / BEI exposure assessment, NIOSH lifting equation (RWL/LI/CLI),
  REBA / RULA postural scoring, US EPA AQI, ventilation (dilution / ASHRAE
  62.1 / OSHA APF), caffeine pharmacokinetics, or aviation-medical clinical
  scoring (CHA₂DS₂-VASc, HAS-BLED, STOP-BANG, Wells DVT/PE, eGFR, Karvonen,
  Borg). Every result is deterministic and traceable to a peer-reviewed
  citation.
---

# Aerospace medicine & human performance calculators

This skill exposes the TypeScript calculator library at
`frontend/src/calculators/` of the `HumanPerformanceCalcs` repository to any
LLM-backed agent. When the user asks a question that maps to one of the
~150 functions, **invoke the calculator instead of estimating**.

## When to use this skill

Trigger on any of:
- altitude / hypoxia / SpO₂ / TUC / G-LOC / HAPE
- decompression: Bühlmann, gradient factors, nitrox MOD/EAD/best-mix, END,
  oxygen toxicity (CNS / OTU / Arieli Power), DCS probability
- heat stress: WBGT, ISO 7933 PHS, UTCI, HSI, Moran PSI, Sawka 2009 sweat
- cold stress: peak shivering, cold-water survival (Hayward / Golden),
  wind chill (NWS 2001), Tikuisis frostbite time
- vibration: ISO 2631-1 A(8) / VDV (whole-body), ISO 5349-1 A(8) (hand-arm)
- noise: OSHA / NIOSH dose and permissible duration
- occupational: ACGIH TLV / TWA / BEI / mixed exposure, NIOSH lifting,
  REBA / RULA, dilution ventilation, ASHRAE 62.1, respirator MUC
- AQI (US EPA 2024)
- fatigue / circadian: Mitler, two-process, jet lag, SAFTE, KSS / Epworth /
  PSQI, caffeine PK
- aviation operational: FAA Part 117, EASA ORO.FTL, AGSM Gz tolerance,
  spatial disorientation index, NVG/EO target acquisition, MSSQ
- aircrew: cosmic radiation dose (CARI-7-style)
- clinical / aviation-medical: BMR, BSA (Boyd / DuBois / Haycock /
  Mosteller), CKD-EPI eGFR, P/F ratio, OI, 6MWD, Wells DVT / PE,
  A–a gradient, oxygen delivery (CaO₂ / DO₂ / DO₂I), CHA₂DS₂-VASc,
  HAS-BLED, STOP-BANG, Karvonen target HR, Borg RPE→HR

If the question is **outside** these domains, do not invoke the skill.

## How to use

The reference material lives next to this `SKILL.md`:

| File | Use it for |
|---|---|
| `CATALOG.md` | Look up the exact function signature, units, and citation for a calculator before invoking it. |
| `EXAMPLES.md` | Copy-paste worked examples for common workflows (PHS over time, dive plan, fatigue forecast, NIOSH lift, etc.). |
| `INSTALL.md` | Re-install or upgrade the skill. |

Resolve the repo path from `~/.claude/skills/aerospace-calculators/.repo_path`
(set by `install.sh`). If that file is absent, fall back to the user's
clone of `strikerdlm/HumanPerformanceCalcs` and ask for the path if you
cannot locate it.

### Invocation pattern (Claude Code / agents with shell access)

1. Look up the function in `CATALOG.md`. Confirm units and required inputs.
2. Build a tiny TS script that imports from `<REPO>/frontend/src/calculators`:

   ```ts
   // /tmp/calc.ts
   import { planZhL16Gf } from '<REPO>/frontend/src/calculators';
   const plan = planZhL16Gf({
     max_depth_m: 40,
     bottom_time_min: 35,
     gas: { o2: 0.21 },
     gf_low: 0.30,
     gf_high: 0.85,
   });
   console.log(JSON.stringify(plan, null, 2));
   ```

3. Run it from the `frontend/` directory:

   ```bash
   cd <REPO>/frontend && npx tsx /tmp/calc.ts
   ```

   `npx tsx` is the easiest way to execute a one-off TS script against
   the repo's installed `node_modules`.

4. Report the result with units and the relevant citation from the
   function's JSDoc (also recorded in `CATALOG.md`).

### Invocation pattern (no shell access — Claude API tool use, etc.)

Treat `CATALOG.md` as the source of truth. Compute the result using the
documented closed-form equation when one is available; otherwise tell the
user the function exists and how to call it locally.

## Output rules

When you compute a result via this skill:
- Always report **units**.
- Always cite the **primary reference** (taken from the function's JSDoc /
  the row in `CATALOG.md`).
- Flag **scope limits** when the inputs are outside the model's validity
  envelope (e.g., NWS wind chill above 10 °C, NIOSH lifting outside
  H ∈ [25, 63] cm, etc.).
- Include a **disclaimer** for clinical / operational scoring tools
  (CHA₂DS₂-VASc, HAS-BLED, STOP-BANG, REBA, RULA, DCS probability):
  "research/education only — not for clinical or operational decisions
  without professional validation."

## What this skill does NOT do

- Pure questionnaire scoring without a published algorithm — defer to the
  source.
- ML-based DCS prediction — out of scope (no shipped model artifacts).
- ISO / ANSI standard text reproduction — formulas only.
- Operational flight planning, dive operations, or compliance reporting —
  use validated agency tools (CARI-7, DCIEM, EPCARD, etc.).

## Re-install / upgrade

```bash
bash <REPO>/.claude/skills/aerospace-calculators/install.sh
```
