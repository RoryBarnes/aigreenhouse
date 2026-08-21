"""Quantitative tests: the contour surface obeys the analytic threshold-crossing law."""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

STEP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STEP_DIR.parent))

import aiGreenhouseAnalysis as gh


@pytest.fixture(scope="module")
def dictGrid():
    """Load the npz grid produced by the step's data command."""
    return np.load(STEP_DIR / "yearsToThresholdGrid.npz")


@pytest.fixture(scope="module")
def listMarkers():
    """Load the marker table produced by the step's data command."""
    with open(STEP_DIR / "contourMarkers.json", "r") as fileHandle:
        return json.load(fileHandle)["listMarkers"]


def testAxesAreLogarithmicallySpaced(dictGrid):
    """Both axes are geometric progressions, as the log-scaled figure assumes."""
    for sKey in ("daDoublingTimes", "daEnergiesPerToken"):
        daRatios = dictGrid[sKey][1:] / dictGrid[sKey][:-1]
        assert np.allclose(daRatios, daRatios[0], rtol=1e-9)


def testGridReproducesTheAnalyticSolution(dictGrid):
    """Every grid cell equals T_double * log2(threshold / power at that energy)."""
    daTGrid, daEGrid = np.meshgrid(dictGrid["daDoublingTimes"],
                                   dictGrid["daEnergiesPerToken"])
    daPower = gh.fdTokensPerMonthToWatts(dictGrid["dTokensAt2025"], daEGrid,
                                         dictGrid["dGoogleFraction"])
    daExpected = daTGrid * np.log2(dictGrid["dThresholdWatts"] / daPower)
    assert np.allclose(dictGrid["daaYearsToThreshold"], daExpected, rtol=1e-12)


def testLeadTimeGrowsWithDoublingTime(dictGrid):
    """Slower growth always postpones the crossing, at every energy per token."""
    daDifferences = np.diff(dictGrid["daaYearsToThreshold"], axis=1)
    assert np.all(daDifferences > 0.0)


def testLeadTimeShrinksWithEnergyPerToken(dictGrid):
    """A more expensive token always brings the crossing forward, at every doubling time."""
    daDifferences = np.diff(dictGrid["daaYearsToThreshold"], axis=0)
    assert np.all(daDifferences < 0.0)


def testContourLabelsSitOnTheirContours(dictGrid):
    """Each inline label is placed at a point whose lead time equals its level."""
    for dLevel, dDoubling, dEnergy in zip(dictGrid["daContourLevels"],
                                          dictGrid["daLabelDoublingTimes"],
                                          dictGrid["daLabelEnergies"]):
        dYears = gh.fdComputeYearsToThreshold(dDoubling, dEnergy,
                                              dictGrid["dTokensAt2025"],
                                              dictGrid["dGoogleFraction"],
                                              dictGrid["dThresholdWatts"])
        assert dYears == pytest.approx(dLevel, rel=1e-9)


def testContourLevelsAreSpannedByTheGrid(dictGrid):
    """Every plotted contour level actually crosses the parameter plane."""
    dMinimum = dictGrid["daaYearsToThreshold"].min()
    dMaximum = dictGrid["daaYearsToThreshold"].max()
    for dLevel in dictGrid["daContourLevels"]:
        assert dMinimum <= dLevel <= dMaximum, f"level {dLevel} lies off the grid"


def testMarkersLieInsideThePlottedDomain(listMarkers, dictGrid):
    """The overplotted fits fall within the axes limits rather than off-figure."""
    for dictMarker in listMarkers:
        assert (dictGrid["daDoublingTimes"][0] <= dictMarker["dDoublingTimeYears"]
                <= dictGrid["daDoublingTimes"][-1])
        assert (dictGrid["daEnergiesPerToken"][0] <= dictMarker["dEnergyPerTokenJoules"]
                <= dictGrid["daEnergiesPerToken"][-1])


def testReferenceMarkerSitsOnThePlottedSurface(listMarkers, dictGrid):
    """The marker whose fit anchors the grid must lie on the surface it is drawn over.

    Only this marker can: the grid is evaluated at a single 2025 throughput, so the
    other fit's quoted lead time comes from its own throughput and is deliberately
    off-surface.
    """
    listReference = [d for d in listMarkers if d["bContourReference"]]
    assert len(listReference) == 1
    dictMarker = listReference[0]
    dQuoted = float(dictMarker["sLabel"].split("(")[1].split(" yr")[0])
    dYears = gh.fdComputeYearsToThreshold(dictMarker["dDoublingTimeYears"],
                                          dictMarker["dEnergyPerTokenJoules"],
                                          dictGrid["dTokensAt2025"],
                                          dictGrid["dGoogleFraction"],
                                          dictGrid["dThresholdWatts"])
    assert dQuoted == pytest.approx(dYears, abs=0.05)
