"""Fit the token-throughput growth curve and the moist-greenhouse power threshold."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import aiGreenhouseAnalysis as gh


def fdictParseArguments():
    """Parse the raw-data input path and the output path for the fit summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-file", required=True,
                        help="Raw sourced observational inputs (aiWasteHeatData.json).")
    parser.add_argument("--output", required=True,
                        help="Path for the JSON fit summary this step produces.")
    return vars(parser.parse_args())


def fdictBuildFitRecord(sLabel, daYears, daTokens, dThresholdWatts, sColor,
                        bContourReference):
    """Fit one subset of the observations and package every derived quantity."""
    dDoublingTimeYears, dTokensAt2025 = gh.ftFitDoublingTime(daYears, daTokens)
    dPowerAt2025 = gh.fdTokensPerMonthToWatts(dTokensAt2025,
                                              gh.ENERGY_PER_TOKEN_DEFAULT_JOULES,
                                              gh.GOOGLE_FRACTION_DEFAULT)
    dYearsToThreshold = gh.fdComputeYearsToThreshold(
        dDoublingTimeYears, gh.ENERGY_PER_TOKEN_DEFAULT_JOULES,
        dTokensAt2025, gh.GOOGLE_FRACTION_DEFAULT, dThresholdWatts)
    return {"sLabel": sLabel,
            "sColor": sColor,
            "bContourReference": bContourReference,
            "dDoublingTimeYears": float(dDoublingTimeYears),
            "dTokensAt2025": float(dTokensAt2025),
            "dPowerAt2025Watts": float(dPowerAt2025),
            "dYearsToThreshold": float(dYearsToThreshold),
            "dOnsetYear": float(gh.REFERENCE_YEAR + dYearsToThreshold)}


def flistBuildFits(daAllYears, daAllTokens, dThresholdWatts):
    """Build the all-points fit and the fit with the earliest observation dropped."""
    daTrimmedYears, daTrimmedTokens = gh.ftDropEarliestObservation(daAllYears, daAllTokens)
    return [fdictBuildFitRecord("All points", daAllYears, daAllTokens,
                                dThresholdWatts, "dark_blue", False),
            fdictBuildFitRecord("2024-05 dropped", daTrimmedYears, daTrimmedTokens,
                                dThresholdWatts, "purple", True)]


def fdictBuildSummary(dictData):
    """Assemble the complete fit summary written by this step."""
    daAllYears, daAllTokens = gh.ftGetTokenObservations(dictData)
    dThresholdWatts = gh.fdComputeThresholdWatts(dictData)
    return {"dThresholdWatts": float(dThresholdWatts),
            "dReferenceYear": gh.REFERENCE_YEAR,
            "dGoogleFraction": gh.GOOGLE_FRACTION_DEFAULT,
            "dEnergyPerTokenJoules": gh.ENERGY_PER_TOKEN_DEFAULT_JOULES,
            "daObservedYears": [float(d) for d in daAllYears],
            "daObservedTokensPerMonth": [float(d) for d in daAllTokens],
            "listFits": flistBuildFits(daAllYears, daAllTokens, dThresholdWatts)}


def fnPrintSummary(dictSummary):
    """Report the fitted parameters and headline extrapolation to the terminal."""
    print(f"  Moist-greenhouse threshold:    {dictSummary['dThresholdWatts']:.3e} W")
    for dictFit in dictSummary["listFits"]:
        print(f"[{dictFit['sLabel']}]")
        print(f"  Fitted doubling time:          {dictFit['dDoublingTimeYears']:.3f} years")
        print(f"  Google tokens/month at 2025.0: {dictFit['dTokensAt2025']:.3e}")
        print(f"  Global power at 2025.0:        {dictFit['dPowerAt2025Watts']:.3e} W")
        print(f"  Years from 2025 to threshold:  {dictFit['dYearsToThreshold']:.2f}")
        print(f"  Onset calendar year:           {dictFit['dOnsetYear']:.1f}")


def fnMain():
    """Load the raw observations, fit them, and write the JSON summary."""
    dictArgs = fdictParseArguments()
    dictData = gh.fdictLoadObservations(dictArgs["data_file"])
    dictSummary = fdictBuildSummary(dictData)
    fnPrintSummary(dictSummary)
    with open(dictArgs["output"], "w") as fileHandle:
        json.dump(dictSummary, fileHandle, indent=2, sort_keys=True)
        fileHandle.write("\n")


if __name__ == "__main__":
    fnMain()
