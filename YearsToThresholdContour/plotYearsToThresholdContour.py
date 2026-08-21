"""Plot contours of years from 2025 to the moist-greenhouse threshold."""

import argparse
import json

import matplotlib.pyplot as plt
import numpy as np
import vplot


def fdictParseArguments():
    """Parse the grid and marker inputs and the figure output path."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--years-grid", required=True,
                        help="npz grid produced by this step's data command.")
    parser.add_argument("--contour-markers", required=True,
                        help="JSON marker table produced by this step's data command.")
    parser.add_argument("sPlotPath", help="Path for the output figure.")
    return vars(parser.parse_args())


def fnDrawContours(axes, dictGrid):
    """Draw the years-to-threshold contours and their inline numeric labels."""
    axes.contour(dictGrid["daDoublingTimes"], dictGrid["daEnergiesPerToken"],
                 dictGrid["daaYearsToThreshold"], levels=dictGrid["daContourLevels"],
                 colors="k", linewidths=1.2)
    for dLevel, dTPosition, dEPosition in zip(dictGrid["daContourLevels"],
                                              dictGrid["daLabelDoublingTimes"],
                                              dictGrid["daLabelEnergies"]):
        axes.text(dTPosition, dEPosition, f"{int(dLevel)}", fontsize=14,
                  ha="center", va="center", rotation=0,
                  bbox=dict(facecolor="white", edgecolor="none", pad=0.5))


def fnDrawMarkers(axes, listMarkers):
    """Overplot each fitted growth scenario as a discrete point."""
    for dictMarker in listMarkers:
        axes.plot(dictMarker["dDoublingTimeYears"],
                  dictMarker["dEnergyPerTokenJoules"], "o",
                  color=getattr(vplot.colors, dictMarker["sColor"]),
                  markersize=10.0, markeredgecolor="k", markeredgewidth=0.8,
                  label=dictMarker["sLabel"], zorder=5)


def fnStyleAxes(axes, dictGrid):
    """Apply the logarithmic scaling, limits, and labelling of the parameter plane."""
    axes.legend(loc="upper left", fontsize=11)
    axes.set_xscale("log")
    axes.set_yscale("log")
    axes.set_xlim(dictGrid["daDoublingTimes"][0], dictGrid["daDoublingTimes"][-1])
    axes.set_ylim(dictGrid["daEnergiesPerToken"][0], dictGrid["daEnergiesPerToken"][-1])
    axes.set_xlabel("Token-throughput doubling time (years)", fontsize=18)
    axes.set_ylabel("Energy per token (J)", fontsize=18)
    axes.tick_params(axis="both", which="major", labelsize=14)


def fnMain():
    """Render the years-to-threshold contour figure from the step's data outputs."""
    dictArgs = fdictParseArguments()
    dictGrid = np.load(dictArgs["years_grid"])
    with open(dictArgs["contour_markers"], "r") as fileHandle:
        listMarkers = json.load(fileHandle)["listMarkers"]

    figure = vplot.VPLOTFigure(figsize=(8.0, 6.0))
    axes = figure.add_subplot(111)
    fnDrawContours(axes, dictGrid)
    fnDrawMarkers(axes, listMarkers)
    fnStyleAxes(axes, dictGrid)
    figure.tight_layout()
    figure.savefig(dictArgs["sPlotPath"], dpi=200)
    plt.close(figure)


if __name__ == "__main__":
    fnMain()
