"""Integrity tests: the YearsToThresholdContour step's declared outputs exist and are well formed."""

import json
from pathlib import Path

import numpy as np
import pytest


STEP_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def dictGrid():
    """Load the npz grid produced by the step's data command."""
    return np.load(STEP_DIR / "yearsToThresholdGrid.npz")


@pytest.fixture(scope="module")
def listMarkers():
    """Load the marker table produced by the step's data command."""
    with open(STEP_DIR / "contourMarkers.json", "r") as fileHandle:
        return json.load(fileHandle)["listMarkers"]


def testDeclaredOutputsExist():
    """Both declared data outputs are present and non-empty."""
    for sName in ("yearsToThresholdGrid.npz", "contourMarkers.json"):
        sPath = STEP_DIR / sName
        assert sPath.is_file(), f"{sPath} is missing"
        assert sPath.stat().st_size > 0


def testGridArchiveHasEveryArray(dictGrid):
    """Every array the plot script reads is present in the archive."""
    for sKey in ("daDoublingTimes", "daEnergiesPerToken", "daaYearsToThreshold",
                 "daContourLevels", "daLabelDoublingTimes", "daLabelEnergies",
                 "dTokensAt2025", "dGoogleFraction", "dThresholdWatts"):
        assert sKey in dictGrid.files, f"missing array {sKey}"


def testGridShapesAgree(dictGrid):
    """The years grid is indexed (energy, doubling time) as the contour call expects."""
    assert dictGrid["daaYearsToThreshold"].shape == (len(dictGrid["daEnergiesPerToken"]),
                                                     len(dictGrid["daDoublingTimes"]))


def testContourLabelArraysMatchLevels(dictGrid):
    """There is one label position per contour level."""
    iLevels = len(dictGrid["daContourLevels"])
    assert len(dictGrid["daLabelDoublingTimes"]) == iLevels
    assert len(dictGrid["daLabelEnergies"]) == iLevels


def testGridIsEverywhereFinite(dictGrid):
    """No NaN or infinite lead times leaked into the plotted surface."""
    assert np.all(np.isfinite(dictGrid["daaYearsToThreshold"]))


def testMarkersAreComplete(listMarkers):
    """Each marker carries the fields the plot script reads."""
    assert len(listMarkers) == 2
    for dictMarker in listMarkers:
        for sKey in ("sLabel", "dDoublingTimeYears", "dEnergyPerTokenJoules",
                     "bContourReference", "sColor"):
            assert sKey in dictMarker, f"marker missing {sKey}"
