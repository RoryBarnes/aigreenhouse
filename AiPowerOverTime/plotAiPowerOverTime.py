"""Plot projected global AI waste-heat power versus time against the greenhouse threshold."""

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import vplot

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import aiGreenhouseAnalysis as gh


def fdictParseArguments():
    """Parse the fit-summary input path and the figure output path."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--power-fits", required=True,
                        help="JSON fit summary produced by this step's data command.")
    parser.add_argument("sPlotPath", help="Path for the output figure.")
    return vars(parser.parse_args())


def fdaBuildProjectionYears(dictSummary):
    """Span the projection axis from just before 2025 past the latest threshold crossing."""
    dLatestOnsetYears = max(d["dYearsToThreshold"] for d in dictSummary["listFits"])
    return np.linspace(gh.REFERENCE_YEAR - 1.0,
                       gh.REFERENCE_YEAR + 1.15 * dLatestOnsetYears, 400)


def fnDrawFits(axes, dictSummary, daYearsProjection):
    """Draw one projected power curve per fitted growth rate."""
    for dictFit in dictSummary["listFits"]:
        daPowerProjection = gh.fdaProjectPower(daYearsProjection,
                                               dictFit["dTokensAt2025"],
                                               dictFit["dDoublingTimeYears"],
                                               dictSummary["dEnergyPerTokenJoules"],
                                               dictSummary["dGoogleFraction"])
        sDoubling = f"{dictFit['dDoublingTimeYears']:.2f}"
        axes.semilogy(daYearsProjection, daPowerProjection,
                      color=getattr(vplot.colors, dictFit["sColor"]), linewidth=2.0,
                      label=f"{dictFit['sLabel']} (T$_{{double}}$ = {sDoubling} yr)")


def fnDrawObservations(axes, dictSummary):
    """Overplot the observed Google throughput rescaled to a global power."""
    daObservedPower = gh.fdTokensPerMonthToWatts(
        np.array(dictSummary["daObservedTokensPerMonth"]),
        dictSummary["dEnergyPerTokenJoules"], dictSummary["dGoogleFraction"])
    axes.semilogy(dictSummary["daObservedYears"], daObservedPower, "o",
                  color=vplot.colors.red, markersize=8.0,
                  label="Observed Google throughput (rescaled)")


def fnStyleAxes(axes):
    """Apply the shared axis labelling, limits, and legend styling."""
    axes.set_xlabel("Year", fontsize=18)
    axes.set_ylabel("Global AI waste-heat power (W)", fontsize=18)
    axes.set_ylim(top=1.0e17)
    axes.tick_params(axis="both", which="major", labelsize=14)
    axes.legend(loc="lower right", fontsize=11)
    axes.grid(True, which="both", alpha=0.3)


def fnMain():
    """Render the power-over-time figure from the step's fit summary."""
    dictArgs = fdictParseArguments()
    with open(dictArgs["power_fits"], "r") as fileHandle:
        dictSummary = json.load(fileHandle)

    figure = vplot.VPLOTFigure(figsize=(8.0, 6.0))
    axes = figure.add_subplot(111)
    fnDrawFits(axes, dictSummary, fdaBuildProjectionYears(dictSummary))
    fnDrawObservations(axes, dictSummary)
    axes.axhline(dictSummary["dThresholdWatts"], color=vplot.colors.orange,
                 linestyle="--", linewidth=2.0, label="Moist-greenhouse threshold")
    fnStyleAxes(axes)
    figure.tight_layout()
    figure.savefig(dictArgs["sPlotPath"], dpi=200)
    plt.close(figure)


if __name__ == "__main__":
    fnMain()
