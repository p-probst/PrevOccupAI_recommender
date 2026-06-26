# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
from typing import Dict, Tuple
import pandas as pd

# internal imports
from constants import RULE_KEY, SENSORS_KEY
from recommender.load.language_mappings import POSTURE_MAPPING
from recommender.utils import  get_language_mapper_values, build_sensor_recommendations_dict, evaluate_subject_risk



# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
POSTURE_MIN_ELLIPSE_AREA_THRESHOLD = 0.012 # square meters

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def assess_low_postural_variability(df: pd.DataFrame, subject_col: str, ellipse_area_col: str,
                                    percentile: float = 0.05, flag_daily: bool = True) -> Tuple[pd.DataFrame, float]:
    """
    Assess low postural variability during seated office work using the 95% confidence ellipse area of postural sway.

    The procedure consists of the following steps:

    1. Aggregate ellipse area metrics per subject (median, mean, standard deviation).
    2. Define a low-variability threshold using a percentile-based approach.
    3. Flag subjects whose median postural variability falls below this threshold.
    4. Optionally flag individual recording days using the same threshold.

    This approach explicitly accounts for repeated measurements (multiple days per subject) and is appropriate when no
    absolute clinical threshold for postural variability is available.

    :param df: Input ``pandas.DataFrame`` containing posture metrics.
    :param subject_col: Column name identifying the subject (e.g., participant ID).
    :param ellipse_area_col: Column name containing the 95% confidence ellipse area of postural sway.
    :param percentile: Percentile used to define the low-variability threshold (default is ``0.05``, corresponding to the 5th percentile).
    :param flag_daily: Whether to flag individual daily recordings whose ellipse area falls below the low-variability threshold.

    :returns:A tuple containing:
        - subject_level_df: Subject-level DataFrame with aggregated ellipse area metrics and a
                            boolean flag indicating low postural variability.
        - low_variability_threshold: The ellipse area threshold below which postural variability is considered low.

    """

    # -------------------------
    # 1. Aggregate per subject
    # -------------------------
    subject_level_df = (
        df
        .groupby(subject_col, as_index=False)
        .agg(
            ellipse_area_median=(ellipse_area_col, "median"),
            ellipse_area_mean=(ellipse_area_col, "mean"),
            ellipse_area_std=(ellipse_area_col, "std"),
            n_days=(ellipse_area_col, "count"),
        )
    )

    # -------------------------------------
    # 2. Compute low-variability threshold
    # -------------------------------------
    low_variability_threshold = subject_level_df[
        "ellipse_area_median"
    ].quantile(percentile)

    # ----------------------------
    # 3. Flag low-variability subjects
    # ----------------------------
    subject_level_df["low_variability_subject"] = (
        subject_level_df["ellipse_area_median"] < low_variability_threshold
    )

    # ----------------------------
    # 4. Optionally flag daily values
    # ----------------------------
    if flag_daily:
        df["low_variability_day"] = (
            df[ellipse_area_col] < low_variability_threshold
        )

    return subject_level_df, low_variability_threshold


def get_postural_displacement_recommendation(posture_subject_metrics_df: pd.DataFrame, subject_id: int,
                                             full_recommender_dict: Dict, language: str = 'pt') -> Dict:
    """
    Gets recommendations for the postural displacement based on the 95% confidence ellipse area. The recommendation is
    triggered when the subject falls below the low-variability threshold.
    :param posture_subject_metrics_df: pandas.DataFrame containing the (all) subject metrics as extracted from the OH-profiles
    :param subject_id: the subject ID
    :param full_recommender_dict: the full recommendation JSON loaded as a dict.
    :param language: Output language code ('pt' or 'eng'). Default: 'pt'
    :return: Dict containing the recommendations for the subject as well as some metadata. The dict has the following keys:
             RECOMMENDATIONS_KEY = 'recommendations': list of strings containing the recommendations.
             RULE_KEY = 'rule': list of strings containing the applied rule(s).

             The following keys are ONLY included in case a risk was detected:
             RISK_DATES_KEY = 'risk_dates': list of strings containing the days on which risks were detected.
             NUM_INSTANCES_KEY = 'num_instances': int indicating the number of instances a risk was detected.
    """

    # define the assessment dimension
    sensor_dimension = 'posture'

    # get the sub-dictionary containing the rule and the recommendation
    sensor_recommender_dict = full_recommender_dict[SENSORS_KEY][sensor_dimension]

    # obtain the correct metric descriptor
    posture_descriptor = get_language_mapper_values(POSTURE_MAPPING, language)[0]

    # get the rule
    rule = sensor_recommender_dict[RULE_KEY][language]

    # filter the DataFrame according to the rule
    posture_risk_subject_df = posture_subject_metrics_df[posture_subject_metrics_df[posture_descriptor] < POSTURE_MIN_ELLIPSE_AREA_THRESHOLD]

    # check whether the subject is part of the risk subjects
    risk_dates, total_num_instances = evaluate_subject_risk(posture_risk_subject_df, subject_id)

    # generate recommendations dictionary
    recommendations_dict = build_sensor_recommendations_dict(rule, risk_dates, total_num_instances,
                                                             sensor_recommender_dict, language=language)

    return recommendations_dict

# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #