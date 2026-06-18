# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import numpy as np
import pandas as pd
from scipy.special import expit


# internal imports
from constants import SUBJECT_ID_COL
# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
TOTAL_DURATION_COL = "total_duration_hour"

MIN_DURATION_H = 1

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def transform_time_to_shift(acq_time: str) -> str:
    """
    Transforms the string to a shift period of either "morning", "midday2, or "afternoon".
    :param acq_time: the acquisition time. It is assumed that the string has the format "HH-MM-SS"
    :return: string with shift period.
    """

    # only use the hour
    acq_hour = int(acq_time.split("-")[0])

    # check the time
    if acq_hour < 10:
        shift = "morning"

    elif acq_hour < 13:
        shift = "midday"

    else:
        shift = "afternoon"

    return shift

def drop_short_recordings(df: pd.DataFrame, duration_s_col, class_distribution_col) -> pd.DataFrame:
    """
    removes recordings that shorter than 1 hour
    :param df: Raw har_subject_metrics DataFrame.
    :return: the dataframe with short recordings removed.
    """

    # Step 1: recover total recording duration (convert it to hours)
    df[TOTAL_DURATION_COL] = (df[duration_s_col] / df[class_distribution_col]) / 3600

    # Step 2: drop short recordings (MCAR, e.g. subject 126)
    n_before = len(df)
    df = df[df[TOTAL_DURATION_COL] >= MIN_DURATION_H].copy()
    print(f"Dropped {n_before - len(df)} subject-day(s) with recording < {MIN_DURATION_H}h "
          f"(retained {len(df)} of {n_before} rows, "
          f"{df[SUBJECT_ID_COL].nunique()} subjects).")

    return df


def get_back_transform(results_df: pd.DataFrame, is_ilr: bool = False) -> pd.DataFrame:
    """
    Transform values back to proportions and odd ratios
    :param results_df: pandas.DataFrame obtained from :function fit_lmm
    :param is_ilr: whether to calculate ILR or not.
    :return: pandas.DataFrame with transformed values added
    """

    # get the estimates
    # [0] = beta_0 (intercept), ..., [3] = beta_3 (morning)
    beta_estimates = results_df["estimate"].to_numpy()[0:-2] # remove ICC and cohen's d
    ci_lows = results_df["CI_lower_95"].to_numpy()[0:-2]
    ci_uppers = results_df["CI_upper_95"].to_numpy()[0:-2]


    # dict to hold the results
    transformed = []

    # cycle over the lmm coefficients
    for index in range(1, len(beta_estimates)):

        # calculate sum for reference shift
        if index == 1:
            bo_sum = beta_estimates[0]
            fo_sum = beta_estimates[0] + beta_estimates[index]

        else:
            bo_sum = beta_estimates[0] + beta_estimates[index]
            fo_sum =  beta_estimates[0] + beta_estimates[1] + beta_estimates[index]

        # calculate the values
        bo_val = get_absolute_rate(bo_sum, is_ilr=is_ilr)
        fo_val = get_absolute_rate(fo_sum, is_ilr=is_ilr)
        odds, ci_low, ci_upper = get_odds_ratio_and_ci(beta_estimates[index], ci_lows[index], ci_uppers[index], is_ilr=is_ilr)

        transformed.append({"BO": bo_val, "FO": fo_val, "OR_group": odds, "OR_CI_low": ci_low, "OR_CI_upper": ci_upper})

    # create DataFrame
    transformed_df = pd.DataFrame(transformed)
    transformed_df['term'] = results_df["term"].iloc[1:-2].values # only get the relevant rows

    # merge the two dataframes and return
    results_df = results_df.merge(transformed_df, on="term", how="left")

    return results_df

def get_absolute_rate(beta_sum, is_ilr: bool = False):
    """
    calculates the log absolute rate for the established log transform
    :param beta_sum: the sum of the LMM coefficients.
    :param is_ilr: whether to calculate ILR or not.
    :return:  absolute rate for log transform
    """
    if is_ilr:
        return expit(beta_sum * np.sqrt(2))

    return np.exp(beta_sum)


def get_odds_ratio_and_ci(beta: float, ci_low: float, ci_upper: float, is_ilr: bool = False):
    """
    calculates the odds ratio for the passed LMM coefficient
    :param beta: LLM coefficient
    :param ci_low: low confidence interval
    :param ci_upper: upper confidence interval
    :param is_ilr: whether to calculate ILR
    :return: the ods ratio and the CI interval
    """
    if is_ilr:
        return np.exp(beta * np.sqrt(2)), np.exp(ci_low * np.sqrt(2)), np.exp(ci_upper * np.sqrt(2))

    return np.exp(beta), np.exp(ci_low), np.exp(ci_upper)

# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #



