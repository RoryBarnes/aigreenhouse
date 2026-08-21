"""
Shared physics for the AI waste heat and moist-greenhouse threshold pipeline.

Extrapolates published Google token throughput to global AI power draw and
computes the year in which cumulative waste heat pushes Earth past the
moist-greenhouse (Simpson-Nakajima) outgoing-flux limit.

Assumptions (fixed here, but easily changed at the call site):
  * Google's share of global token traffic is 10 percent.
  * Growth in token throughput is characterised by a single doubling time.
  * Each token dissipates 1 J of electrical energy (system-level waste heat).
"""

import json

import numpy as np


SECONDS_PER_MONTH = 365.25 * 86400.0 / 12.0
REFERENCE_YEAR = 2025.0
GOOGLE_FRACTION_DEFAULT = 0.10
ENERGY_PER_TOKEN_DEFAULT_JOULES = 1.0


def fdIsoStringToDecimalYear(sIso):
    """Convert an ISO date string (YYYY, YYYY-MM, or YYYY-MM-DD) to a decimal year."""
    listParts = sIso.split("-")
    iYear = int(listParts[0])
    iMonth = int(listParts[1]) if len(listParts) > 1 else 1
    iDay = int(listParts[2]) if len(listParts) > 2 else 1
    dDayOfYear = (iMonth - 1) * 30.4375 + (iDay - 1)
    return iYear + dDayOfYear / 365.25


def fdictLoadObservations(sPath):
    """Load the AI waste-heat data file into a dictionary."""
    with open(sPath, "r") as fileHandle:
        return json.load(fileHandle)


def ftGetTokenObservations(dictData):
    """Extract token-throughput observations as two aligned numpy arrays."""
    listRecords = dictData["dictTokenThroughput"]["listObservations"]
    daYears = np.array([fdIsoStringToDecimalYear(d["sIso"]) for d in listRecords])
    daTokensPerMonth = np.array([d["dTokensPerMonth"] for d in listRecords])
    return daYears, daTokensPerMonth


def ftFitDoublingTime(daYears, daTokensPerMonth):
    """Fit a single exponential to the observations. Returns (T_double_years, N_at_2025_google)."""
    daLog2Tokens = np.log2(daTokensPerMonth)
    daSlope, daIntercept = np.polyfit(daYears, daLog2Tokens, 1)
    dDoublingTimeYears = 1.0 / daSlope
    dTokensAt2025 = 2.0 ** (daSlope * REFERENCE_YEAR + daIntercept)
    return dDoublingTimeYears, dTokensAt2025


def ftDropEarliestObservation(daYears, daTokensPerMonth):
    """Return the observation arrays with the earliest-year point removed."""
    iEarliest = int(np.argmin(daYears))
    daMask = np.ones(len(daYears), dtype=bool)
    daMask[iEarliest] = False
    return daYears[daMask], daTokensPerMonth[daMask]


def fdComputeThresholdWatts(dictData):
    """Recompute the moist-greenhouse waste-heat requirement from primitives."""
    dConstants = dictData["dictPhysicalConstants"]
    dSolar = dConstants["dSolarConstantWattsPerSquareMetre"]["dValue"]
    dAlbedo = dConstants["dEarthBondAlbedo"]["dValue"]
    dRadius = dConstants["dEarthRadiusMetres"]["dValue"]
    dOlrLimit = dictData["dictMoistGreenhouseThreshold"]["dOutgoingFluxLimitWattsPerSquareMetre"]["dValue"]
    dAbsorbedFlux = dSolar * (1.0 - dAlbedo) / 4.0
    dExcessFlux = dOlrLimit - dAbsorbedFlux
    dSurfaceArea = 4.0 * np.pi * dRadius * dRadius
    return dExcessFlux * dSurfaceArea


def fdTokensPerMonthToWatts(dTokensPerMonth, dEnergyPerToken, dGoogleFraction):
    """Convert a Google token/month rate into a global waste-heat power in watts."""
    dGlobalTokensPerMonth = dTokensPerMonth / dGoogleFraction
    return dGlobalTokensPerMonth * dEnergyPerToken / SECONDS_PER_MONTH


def fdaProjectPower(daYears, dTokensAt2025, dDoublingTimeYears, dEnergyPerToken, dGoogleFraction):
    """Project global AI power draw over an array of years."""
    daTokens = dTokensAt2025 * 2.0 ** ((daYears - REFERENCE_YEAR) / dDoublingTimeYears)
    return fdTokensPerMonthToWatts(daTokens, dEnergyPerToken, dGoogleFraction)


def fdComputeYearsToThreshold(dDoublingTimeYears, dEnergyPerToken,
                              dTokensAt2025, dGoogleFraction, dThresholdWatts):
    """Solve analytically for the number of years from 2025 until threshold is reached."""
    dPowerAtReference = fdTokensPerMonthToWatts(dTokensAt2025, dEnergyPerToken, dGoogleFraction)
    if dPowerAtReference <= 0.0:
        return np.inf
    return dDoublingTimeYears * np.log2(dThresholdWatts / dPowerAtReference)


def fdaComputeYearsGrid(daDoublingTimes, daEnergiesPerToken, dTokensAt2025,
                        dGoogleFraction, dThresholdWatts):
    """Compute a 2D grid of years-to-threshold over (doubling time, energy per token)."""
    daaGrid = np.zeros((len(daEnergiesPerToken), len(daDoublingTimes)))
    for iRow, dEnergy in enumerate(daEnergiesPerToken):
        for iCol, dDoubling in enumerate(daDoublingTimes):
            daaGrid[iRow, iCol] = fdComputeYearsToThreshold(
                dDoubling, dEnergy, dTokensAt2025, dGoogleFraction, dThresholdWatts)
    return daaGrid


def ftBuildContourLabelPositions(daContourLevels, dTokensAt2025,
                                 dGoogleFraction, dThresholdWatts,
                                 dLabelEnergyJoules):
    """Return (T, E) positions on each contour at a chosen interior energy value."""
    dReferenceLog2 = np.log2(dThresholdWatts * dGoogleFraction * SECONDS_PER_MONTH
                             / dTokensAt2025)
    dLog2LabelEnergy = np.log2(dLabelEnergyJoules)
    listPositions = []
    for dLevel in daContourLevels:
        dDoublingAtLabel = dLevel / (dReferenceLog2 - dLog2LabelEnergy)
        listPositions.append((dDoublingAtLabel, dLabelEnergyJoules))
    return listPositions
