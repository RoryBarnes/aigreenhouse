"""Compute years-to-threshold over the (doubling time, energy per token) parameter plane."""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import aiGreenhouseAnalysis as gh


DOUBLING_TIME_RANGE_YEARS = (0.2, 5.0)
ENERGY_PER_TOKEN_RANGE_JOULES = (0.1, 20.0)
GRID_POINTS_PER_AXIS = 200
CONTOUR_LEVELS_YEARS = (10, 20, 30, 50, 75, 100)
LABEL_ENERGY_JOULES = 1.4


def fdictParseArguments():
    """Parse the upstream fit summary and the two output paths for this step."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--power-fits", required=True,
                        help="JSON fit summary produced by the AiPowerOverTime step.")
    parser.add_argument("--output-grid", required=True,
                        help="Path for the npz grid of years-to-threshold.")
    parser.add_argument("--output-markers", required=True,
                        help="Path for the JSON description of the overplotted fit markers.")
    return vars(parser.parse_args())


def fdictSelectContourReference(dictSummary):
    """Return the fit whose 2025 throughput anchors the contour grid."""
    for dictFit in dictSummary["listFits"]:
        if dictFit["bContourReference"]:
            return dictFit
    raise ValueError("No fit in the summary is flagged bContourReference.")


def flistBuildMarkers(dictSummary):
    """Describe each fit as a marker at its doubling time and the default energy."""
    dEnergy = dictSummary["dEnergyPerTokenJoules"]
    return [{"sLabel": f"{d['sLabel']} ({d['dYearsToThreshold']:.1f} yr)",
             "dDoublingTimeYears": d["dDoublingTimeYears"],
             "dEnergyPerTokenJoules": dEnergy,
             "bContourReference": d["bContourReference"],
             "sColor": d["sColor"]}
            for d in dictSummary["listFits"]]


def fdictBuildGrid(dictSummary):
    """Evaluate years-to-threshold across the logarithmic parameter grid."""
    dictReference = fdictSelectContourReference(dictSummary)
    daDoublingTimes = np.logspace(np.log10(DOUBLING_TIME_RANGE_YEARS[0]),
                                  np.log10(DOUBLING_TIME_RANGE_YEARS[1]),
                                  GRID_POINTS_PER_AXIS)
    daEnergiesPerToken = np.logspace(np.log10(ENERGY_PER_TOKEN_RANGE_JOULES[0]),
                                     np.log10(ENERGY_PER_TOKEN_RANGE_JOULES[1]),
                                     GRID_POINTS_PER_AXIS)
    daContourLevels = np.array(CONTOUR_LEVELS_YEARS, dtype=float)
    daaYears = gh.fdaComputeYearsGrid(daDoublingTimes, daEnergiesPerToken,
                                      dictReference["dTokensAt2025"],
                                      dictSummary["dGoogleFraction"],
                                      dictSummary["dThresholdWatts"])
    listPositions = gh.ftBuildContourLabelPositions(
        daContourLevels, dictReference["dTokensAt2025"],
        dictSummary["dGoogleFraction"], dictSummary["dThresholdWatts"],
        dLabelEnergyJoules=LABEL_ENERGY_JOULES)
    return {"daDoublingTimes": daDoublingTimes,
            "daEnergiesPerToken": daEnergiesPerToken,
            "daaYearsToThreshold": daaYears,
            "daContourLevels": daContourLevels,
            "daLabelDoublingTimes": np.array([t[0] for t in listPositions]),
            "daLabelEnergies": np.array([t[1] for t in listPositions]),
            "dTokensAt2025": np.array(dictReference["dTokensAt2025"]),
            "dGoogleFraction": np.array(dictSummary["dGoogleFraction"]),
            "dThresholdWatts": np.array(dictSummary["dThresholdWatts"])}


def fnMain():
    """Build the contour grid and marker table from the upstream fit summary."""
    dictArgs = fdictParseArguments()
    with open(dictArgs["power_fits"], "r") as fileHandle:
        dictSummary = json.load(fileHandle)

    dictGrid = fdictBuildGrid(dictSummary)
    np.savez(dictArgs["output_grid"], **dictGrid)
    print(f"  Grid shape:                    {dictGrid['daaYearsToThreshold'].shape}")
    print(f"  Years-to-threshold range:      "
          f"{dictGrid['daaYearsToThreshold'].min():.2f} to "
          f"{dictGrid['daaYearsToThreshold'].max():.2f}")

    listMarkers = flistBuildMarkers(dictSummary)
    with open(dictArgs["output_markers"], "w") as fileHandle:
        json.dump({"listMarkers": listMarkers}, fileHandle, indent=2, sort_keys=True)
        fileHandle.write("\n")


if __name__ == "__main__":
    fnMain()
