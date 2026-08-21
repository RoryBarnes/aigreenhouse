"""Integrity tests: the AiPowerOverTime step's declared outputs exist and are well formed."""

import json
from pathlib import Path

import pytest


STEP_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def dictFits():
    """Load the fit summary produced by the step's data command."""
    with open(STEP_DIR / "aiPowerFits.json", "r") as fileHandle:
        return json.load(fileHandle)


def testFitSummaryExists():
    """The declared data output is present and non-empty."""
    sPath = STEP_DIR / "aiPowerFits.json"
    assert sPath.is_file(), f"{sPath} is missing"
    assert sPath.stat().st_size > 0


def testFitSummaryHasTopLevelKeys(dictFits):
    """Every field the downstream step and plot script read is present."""
    for sKey in ("dThresholdWatts", "dReferenceYear", "dGoogleFraction",
                 "dEnergyPerTokenJoules", "daObservedYears",
                 "daObservedTokensPerMonth", "listFits"):
        assert sKey in dictFits, f"missing key {sKey}"


def testObservationArraysAlign(dictFits):
    """The observed years and token counts are aligned and non-trivial."""
    assert len(dictFits["daObservedYears"]) == len(dictFits["daObservedTokensPerMonth"])
    assert len(dictFits["daObservedYears"]) >= 3


def testEveryFitRecordIsComplete(dictFits):
    """Each fit carries the full set of derived quantities the plots consume."""
    assert len(dictFits["listFits"]) == 2
    for dictFit in dictFits["listFits"]:
        for sKey in ("sLabel", "sColor", "bContourReference", "dDoublingTimeYears",
                     "dTokensAt2025", "dPowerAt2025Watts", "dYearsToThreshold",
                     "dOnsetYear"):
            assert sKey in dictFit, f"fit {dictFit.get('sLabel')} missing {sKey}"


def testExactlyOneContourReference(dictFits):
    """The downstream contour step needs exactly one anchor fit."""
    iCount = sum(1 for d in dictFits["listFits"] if d["bContourReference"])
    assert iCount == 1
