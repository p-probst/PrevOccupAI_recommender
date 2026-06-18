# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pandas as pd
import numpy as np
from typing import Dict
from scipy.stats import fisher_exact
from scipy.stats.contingency import odds_ratio
from pathlib import Path


# internal imports
from constants import SUBJECT_ID_COL, WORKTYPE_COL

# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
BODY_REGIONS = {
    "neck_shoulder": ["cervical/pescoço","ombros"],
    "upper_limb": ["braços(cotovelo/antebraço)","punhos/mãos/dedos"],
    "lower_back": ["região dorsal inferior/Lombar"],
}

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def perform_pain_location_analysis(pain_locations_df: pd.DataFrame, save_path: str | Path) -> None:
    """
    perform pain location comparative analysis using Fisher's exact test with Benjamini-Hochberg FDR correction.
    :param pain_locations_df: pandas.DataFrame containing pain locations
    :param save_path: path to save the result
    :return: None
    """

    # transform raw pain locations data into body regions
    pain_regions_df = _transform_body_locations_to_regions(pain_locations_df)

    # get the number of subjects in FO and BO
    total_num_FO = pain_regions_df[pain_regions_df[WORKTYPE_COL] == 'FO'].shape[0]
    total_num_BO = pain_regions_df[pain_regions_df[WORKTYPE_COL] == 'BO'].shape[0]

    # get the number of instances there exists for each pain region for FO and BO
    # and print them to the console
    grouped_pain_regions = pain_regions_df.groupby(WORKTYPE_COL)[list(BODY_REGIONS.keys())].sum()
    print(f"Instances per pain region FO vs. BO: \n{grouped_pain_regions}")

    # init list for holding result dictionaries
    result_rows = []

    # cycle over the body regions
    for region, instances in grouped_pain_regions.items():

        # get the number of people with pain
        num_pain_FO = instances['FO']
        num_pain_BO = instances['BO']

        # build contingency table
        contingency_table = np.array([[num_pain_FO, total_num_FO - num_pain_FO],
                                     [num_pain_BO, total_num_BO - num_pain_BO]])

        # calculate fisher's exact together with CI
        stats = _fisher_with_ci(contingency_table)

        # append results
        result_rows.append({"region": region,
                            "n_FO": total_num_FO,
                            "n_BO": total_num_BO,
                            "n_pain_FO": num_pain_FO,
                            "n_pain_BO": num_pain_BO,
                            "odds_ratio": stats["odds_ratio"],
                            "ci_lower": stats["ci_lower"],
                            "ci_upper": stats["ci_upper"],
                            "fisher_odds_ratio": stats["fisher_odds_ratio"],
                            "fisher_p_value": stats["fisher_p_value"]})


    # transform rows list to dataframe
    results_df = pd.DataFrame(result_rows)

    # apply FDR correction
    results_df["fisher_p_adj"] = _bh_adjust(results_df["fisher_p_value"].to_list())

    # save the results and the plot
    if save_path:
        # create folder
        folder_path = Path(save_path) / 'pain'

        # make sure the directory exists
        folder_path.mkdir(parents=True, exist_ok=True)

        # store the dataframe
        results_df.to_csv(folder_path / f'pain_models_result.csv', index=False)

# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #
def _transform_body_locations_to_regions(pain_locations_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms body locations into specified body regions. Pain is considered in a body region if at least one

    The following regions are created:
    *"neck_shoulder": ["cervical/pescoço","ombros"]
    *"upper_limb": ["braços(cotovelo/antebraço)","punhos/mãos/dedos"]
    *"lower_back": ["região dorsal inferior/Lombar"]

    Other body regions are not considered and there dropped
    :param pain_locations_df: pandas.DataFrame containing the pain body locations data.
    :return: pandas.DataFrame containing the body regions.
    """

    pain_regions_df = pain_locations_df.copy()

    # cycle over the regions
    for region, body_locations_cols in BODY_REGIONS.items():

        pain_regions_df[region] = pain_regions_df[body_locations_cols].apply(_is_yes).any(axis=1).astype(int)

    # keep only the relevant columns
    relevant_cols = [SUBJECT_ID_COL, WORKTYPE_COL] + list(BODY_REGIONS.keys())

    return pain_regions_df[relevant_cols]


def _is_yes(series: pd.Series) -> bool:
    """
    Normalises a string to a boolean.
    "Y" (case-insensitive, leading/trailing whitespace stripped) → True.
    Everything else, including NaN, → False.

    :param series: Raw string column from any pain-questionnaire file.
    :return: pd.Series of bool
    """

    return series.str.strip().str.upper() == "Y"


def _fisher_with_ci(contingency_table: np.ndarray) -> Dict[str, float]:
    """
    Runs fisher's exact test and computes the confidence interval

    Fisher, R. A. (1922). On the interpretation of χ² from contingency tables,
    and the calculation of P. Journal of the Royal Statistical Society, 85(1),
    87–94.
    :param contingency_table: 2x2 table with the following entries: [[FO_yes, FO_no], [BO_yes, BO_no]]
    :return: dictionary containing the results. The dict has the following keys:
             * odds_ratio
             * ci_lower
             * ci_upper
             * p_value
    """

    # perform fisher's exact
    fisher_result = fisher_exact(contingency_table, alternative="less")

    # calculate the odds ratio
    or_result = odds_ratio(contingency_table, kind="conditional")

    # calculate the confidence interval
    ci = or_result.confidence_interval(confidence_level=0.95, alternative="less")

    return {"odds_ratio": or_result.statistic, "ci_lower": ci.low, "ci_upper": ci.high, "fisher_odds_ratio": fisher_result.statistic, "fisher_p_value": fisher_result.pvalue}


def _bh_adjust(p_values: list[float]) -> np.ndarray:
    """
    Applies Benjamini–Hochberg (1995) false discovery rate correction.

    Returns adjusted p-values in the same order as the input, capped at 1.
    The step-up procedure is applied by enforcing monotonicity from right to
    left on the sorted sequence, so p_adj[k] = min(m/k * p_(k), p_adj[k+1]).

    Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery
    rate: a practical and powerful approach to multiple testing. Journal of
    the Royal Statistical Society: Series B, 57(1), 289–300.
    https://doi.org/10.1111/j.2517-6161.1995.tb02031.x
    :param p_values: Raw p-values in any order.
    :return: BH-adjusted p-values, in the same order as the input.
    """

    # ensure p-values are an array
    p = np.asarray(p_values, dtype=float)

    m = len(p)
    order = np.argsort(p)  # ascending rank indices
    adj = np.clip(p[order] * m / np.arange(1, m + 1), 0.0, 1.0)
    adj = np.minimum.accumulate(adj[::-1])[::-1]  # enforce monotonicity

    result = np.empty(m)
    result[order] = adj  # restore original order

    return result

