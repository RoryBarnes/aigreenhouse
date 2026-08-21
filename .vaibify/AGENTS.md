# Project context

Standing instructions for the AI agent working on this project.
This file is versioned with the repository and is part of the
provenance record — keep it current.

## What this project is

An order-of-magnitude limit argument: if AI token throughput keeps
growing exponentially and every token dissipates its electrical energy
as waste heat, when does that waste heat alone push Earth past the
moist-greenhouse (Simpson-Nakajima) outgoing-flux limit? The pipeline
fits a single doubling time to published Google token-throughput
observations, rescales to a global total, recomputes the required
waste-heat power from radiative primitives, and reports the crossing
date. A finished result is the two figures in `Plot/`: the projected
power curve against the threshold, and the crossing date as a contour
over the two parameters the answer is actually sensitive to
(doubling time and joules per token).

The calculation is deliberately an upper-bound argument, not a
forecast. `aiWasteHeatData.json` records the caveats that limit it —
in particular that a token is not a fixed unit of work, that growth
is decelerating sharply, that Google's share of global tokens is
UNMEASURED (the 10 percent assumption is a stipulation), and that the
same waste-heat limit has been derived before (see `dictPriorArt`).

## Data provenance

All raw inputs live in the single file `aiWasteHeatData.json` at the
repository root, compiled 2026-07-27 from a literature sweep. Every
numeric entry carries `sSource`, and `sSourceConfidence` distinguishes
numbers read from the primary document from numbers seen only in an
aggregator. `listPendingActions` names the citations still owed —
most importantly a specific radiative-transfer citation for the
280-310 W/m^2 outgoing-flux limit. Nothing in the pipeline fetches
data from a remote source; there are no `listRemoteData` entries.

Derived values recorded in the data file (for example
`dRequiredWasteHeatWatts`) are reference-only. The pipeline recomputes
them from the primitives, and a quantitative test asserts the
recomputed threshold falls inside the range the data file records.

## Conventions

- Hungarian notation for variables (`d` float, `i` int, `s` string,
  `b` bool, `da` float array, `list`/`dict` containers); function
  names carry a return-type prefix (`fd`, `fda`, `fdict`, `flist`,
  `ft`, `fn`, `fb`). Functions stay under ~20 lines.
- Shared physics lives in `aiGreenhouseAnalysis.py` at the repository
  root. Step scripts import it after inserting the repo root on
  `sys.path`; it holds no I/O paths and no plotting.
- One camelCase directory per step, `data*.py` for analysis and
  `plot*.py` for visualization. Figures go to `Plot/` at the
  repository root.
- Pytest suites live in `<step>/tests/` and must keep the
  `test_integrity_` / `test_quantitative_` filename prefixes: the
  vaibify marker plugin in `<step>/tests/conftest.py` categorizes
  results by that substring in the pytest node ID.
- Every file a script reads from another step arrives as a CLI
  argument wired through a `{step:<sStepId>.<stem>}` token in
  `project.json`. Never hardcode a cross-step path.
- Units are SI throughout: watts, joules, metres, seconds. Times are
  decimal years; 2025.0 is the reference epoch.

## What the agent must never touch

- **The scientific calculation.** The fitting procedure, the
  threshold derivation, the 10 percent Google share, the 1 J/token
  default, and the choice to anchor the contour grid on the
  earliest-point-dropped fit are the researcher's decisions. Do not
  change any of them without explicit direction.
- **`aiWasteHeatData.json`.** It is the raw input record. Correcting
  or extending it is a research act, not a maintenance act.
- **Publication and sign-off.** Pushing to Overleaf or Zenodo,
  accepting plots as the reference standard, declaring the
  determinism waiver, pinning the base-image digest, and the
  per-step user verification are all reserved for the researcher.