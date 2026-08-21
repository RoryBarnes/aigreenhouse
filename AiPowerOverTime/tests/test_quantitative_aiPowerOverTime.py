"""Quantitative tests: the fitted growth curve and threshold reproduce the raw inputs."""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

STEP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STEP_DIR.parent))

import aiGreenhouseAnalysis as gh


@pytest.fixture(scope="module")
def dictFits():
    """Load the fit summary produced by the step's data command."""
    with open(STEP_DIR / "aiPowerFits.json", "r") as fileHandle:
        return json.load(fileHandle)


@pytest.fixture(scope="module")
def dictRaw():
    """Load the raw observational inputs the step consumed."""
    return gh.fdictLoadObservations(STEP_DIR.parent / "aiWasteHeatData.json")


def testObservationsMatchRawFile(dictFits, dictRaw):
    """The recorded observations are exactly those in the raw data file."""
    daYears, daTokens = gh.ftGetTokenObservations(dictRaw)
    assert np.allclose(dictFits["daObservedYears"], daYears)
    assert np.allclose(dictFits["daObservedTokensPerMonth"], daTokens)


def testThresholdRecomputedFromConstants(dictFits, dictRaw):
    """The threshold power is the excess flux times Earth's surface area, not a copied number."""
    dExpected = gh.fdComputeThresholdWatts(dictRaw)
    assert dictFits["dThresholdWatts"] == pytest.approx(dExpected, rel=1e-12)


def testThresholdMatchesIndependentHandCalculation(dictFits, dictRaw):
    """Cross-check the threshold against the flux arithmetic written out longhand."""
    dictConstants = dictRaw["dictPhysicalConstants"]
    dAbsorbed = (dictConstants["dSolarConstantWattsPerSquareMetre"]["dValue"]
                 * (1.0 - dictConstants["dEarthBondAlbedo"]["dValue"]) / 4.0)
    dLimit = (dictRaw["dictMoistGreenhouseThreshold"]
              ["dOutgoingFluxLimitWattsPerSquareMetre"]["dValue"])
    dArea = 4.0 * np.pi * dictConstants["dEarthRadiusMetres"]["dValue"] ** 2
    assert dictFits["dThresholdWatts"] == pytest.approx((dLimit - dAbsorbed) * dArea, rel=1e-9)


def testThresholdIsWithinTheDataFilesRecordedRange(dictFits, dictRaw):
    """The recomputed threshold sits inside the range the data file records for it."""
    dictRequired = dictRaw["dictMoistGreenhouseThreshold"]["dRequiredWasteHeatWatts"]
    assert (dictRequired["dValueAtLowerLimit"] <= dictFits["dThresholdWatts"]
            <= dictRequired["dValueAtUpperLimit"])


@pytest.mark.parametrize("iFit", [0, 1])
def testDoublingTimeIsPositiveAndSubDecadal(dictFits, iFit):
    """Token throughput is observed to grow, so every doubling time is short and positive."""
    dDoubling = dictFits["listFits"][iFit]["dDoublingTimeYears"]
    assert 0.0 < dDoubling < 10.0


@pytest.mark.parametrize("iFit", [0, 1])
def testPowerAt2025FollowsFromTokens(dictFits, iFit):
    """The 2025 power is the token rate converted at the declared J/token and Google share."""
    dictFit = dictFits["listFits"][iFit]
    dExpected = gh.fdTokensPerMonthToWatts(dictFit["dTokensAt2025"],
                                           dictFits["dEnergyPerTokenJoules"],
                                           dictFits["dGoogleFraction"])
    assert dictFit["dPowerAt2025Watts"] == pytest.approx(dExpected, rel=1e-12)


@pytest.mark.parametrize("iFit", [0, 1])
def testProjectedPowerReachesThresholdAtTheStatedTime(dictFits, iFit):
    """Propagating the fit forward by dYearsToThreshold lands on the threshold power."""
    dictFit = dictFits["listFits"][iFit]
    dPower = gh.fdaProjectPower(
        gh.REFERENCE_YEAR + dictFit["dYearsToThreshold"], dictFit["dTokensAt2025"],
        dictFit["dDoublingTimeYears"], dictFits["dEnergyPerTokenJoules"],
        dictFits["dGoogleFraction"])
    assert dPower == pytest.approx(dictFits["dThresholdWatts"], rel=1e-9)


@pytest.mark.parametrize("iFit", [0, 1])
def testOnsetYearIsReferenceYearPlusLead(dictFits, iFit):
    """The reported calendar year is the reference year plus the lead time."""
    dictFit = dictFits["listFits"][iFit]
    assert dictFit["dOnsetYear"] == pytest.approx(
        dictFits["dReferenceYear"] + dictFit["dYearsToThreshold"], rel=1e-12)


def testDroppingEarliestPointSlowsTheFit(dictFits):
    """Growth is decelerating, so removing the earliest point lengthens the doubling time."""
    dictAll, dictTrimmed = dictFits["listFits"]
    assert dictTrimmed["dDoublingTimeYears"] > dictAll["dDoublingTimeYears"]
    assert dictTrimmed["dYearsToThreshold"] > dictAll["dYearsToThreshold"]


def testTrimmedFitDropsOnlyTheEarliestObservation(dictFits, dictRaw):
    """The second fit is the same regression with the first observation removed."""
    daYears, daTokens = gh.ftGetTokenObservations(dictRaw)
    daTrimmedYears, daTrimmedTokens = gh.ftDropEarliestObservation(daYears, daTokens)
    assert len(daTrimmedYears) == len(daYears) - 1
    dDoubling, dTokens = gh.ftFitDoublingTime(daTrimmedYears, daTrimmedTokens)
    dictTrimmed = dictFits["listFits"][1]
    assert dictTrimmed["dDoublingTimeYears"] == pytest.approx(dDoubling, rel=1e-12)
    assert dictTrimmed["dTokensAt2025"] == pytest.approx(dTokens, rel=1e-12)


def testFitStaysWithinAnOrderOfMagnitudeOfEveryObservation(dictFits):
    """A single exponential is only defensible if it tracks all five observations."""
    dictAll = dictFits["listFits"][0]
    daPredicted = gh.fdaProjectPower(np.array(dictFits["daObservedYears"]),
                                     dictAll["dTokensAt2025"],
                                     dictAll["dDoublingTimeYears"],
                                     dictFits["dEnergyPerTokenJoules"],
                                     dictFits["dGoogleFraction"])
    daObserved = gh.fdTokensPerMonthToWatts(
        np.array(dictFits["daObservedTokensPerMonth"]),
        dictFits["dEnergyPerTokenJoules"], dictFits["dGoogleFraction"])
    assert np.all(np.abs(np.log10(daPredicted / daObserved)) < 1.0)
