# AI Usage Declaration

## Models used

- **Anthropic Claude Opus 5** (`claude-opus-5[1m]`), via Claude Code
  inside the vaibify container, 2026-08-21. This is the model that
  built the pipeline described below.

The observational data file `aiWasteHeatData.json` (compiled
2026-07-27) and the original single-file analysis script that this
pipeline was refactored from (2026-08-17) predate that session. The
researcher should record here which model, if any, assisted with
those, and extend the declared-model list accordingly.

## How AI assisted each step

**Repository-wide.** The agent refactored the pre-existing single-file
script `aiGreenhouseAnalysis.py` into a shared, path-free physics
library plus two pipeline steps. Every scientific function
(`ftFitDoublingTime`, `fdComputeThresholdWatts`,
`fdTokensPerMonthToWatts`, `fdaProjectPower`,
`fdComputeYearsToThreshold`, `fdaComputeYearsGrid`,
`ftBuildContourLabelPositions`) was moved verbatim; no calculation,
constant, or modelling assumption was altered. Only I/O paths,
argument handling, and the split between computation and plotting
were rewritten.

**A01 AiPowerOverTime.** Agent-written: `dataAiPowerOverTime.py`
(fits the two growth scenarios and the threshold power, emits
`aiPowerFits.json`), `plotAiPowerOverTime.py` (renders
`Plot/aiPowerOverTime.png`), and the integrity and quantitative test
suites under `AiPowerOverTime/tests/`.

**A02 YearsToThresholdContour.** Agent-written:
`dataYearsToThresholdContour.py` (evaluates the years-to-threshold
surface over the doubling-time / joules-per-token plane, emits
`yearsToThresholdGrid.npz` and `contourMarkers.json`),
`plotYearsToThresholdContour.py` (renders
`Plot/yearsToThresholdContour.png`), and the test suites under
`YearsToThresholdContour/tests/`.

**Project scaffolding.** The agent authored `project.json` through
the `vaibify-do` API, `.vaibify/AGENTS.md`, `.vaibify/requirements.txt`,
and this file.

## Review policy

The agent ran the full pipeline and all 34 tests through vaibify, and
compared the regenerated figures against the researcher's
pre-pipeline versions. Per-step **user verification remains
outstanding** — the researcher's sign-off on each step's outputs is
the gate that has not yet been given, and no agent can supply it.
Accepting the plots as the reference standard, and the attestation of
this declaration, are likewise reserved for the researcher.

## Anything else researchers should know

The agent surfaced, and did not act on, one substantive limitation it
found in the inputs: `dGoogleShareOfGlobalTokens` is recorded in
`aiWasteHeatData.json` as **UNMEASURED**, so the 10 percent figure
that converts Google throughput to a global total is a stipulation,
not an observation. The crossing date scales directly with it. The
same file's `listCaveats` and `dictPriorArt` record further limits —
notably that token throughput is not a fixed unit of work, that
observed growth is decelerating sharply, and that this waste-heat
limit is not a novel result.
