# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd

# internal imports
from constants import RISK_DATES_KEY, NUM_INSTANCES_KEY, RECOMMENDATIONS_KEY, RULE_KEY, NO_RECOMMENDATIONS, USER
from recommender.utils import dates_to_weekdays

# external imports
project_path = Path(f"C:/Users/{USER}/PycharmProjects/OH_Toolkit")
sys.path.append(str(project_path))
from oh_parser import load_profiles, extract_nested

# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
POSTURE_CSV_FILENAME = "posture_subject_metrics.csv"

POSTURE_MIN_ELLIPSE_AREA_THRESHOLD = 0.6 # square meters
# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def generate_posture_csv(posture_data_csv_path: str | Path, oh_profile_path: str) -> pd.DataFrame:
    """

    :param posture_data_csv_path:
    :param oh_profile_path:
    :return:
    """

    if not (Path(posture_data_csv_path) / POSTURE_CSV_FILENAME).exists():
        # load the profiles
        profiles = load_profiles(oh_profile_path)

        # parse the noise metrics
        df_sessions = extract_nested(
            profiles,
            base_path="sensor_metrics.posture",
            level_names=["date", "session"],
            value_paths=[
                "posture_95_confidence_ellipse_area",
                "posture_ap_range",
                "posture_ml_range"

            ],
            exclude_patterns=[],
        )

        # save the DataFrame
        df_sessions.to_csv(POSTURE_CSV_FILENAME, index=False)

    else:
        df_sessions = pd.read_csv(POSTURE_CSV_FILENAME)

    return df_sessions

def assess_low_postural_variability(
    df: pd.DataFrame,
    subject_col: str,
    ellipse_area_col: str,
    percentile: float = 0.05,
    flag_daily: bool = True
) -> Tuple[pd.DataFrame, float]:
    """
    Assess low postural variability during seated office work using the
    95% confidence ellipse area of postural sway.

    The procedure consists of the following steps:

    1. Aggregate ellipse area metrics per subject (median, mean, standard deviation).
    2. Define a low-variability threshold using a percentile-based approach.
    3. Flag subjects whose median postural variability falls below this threshold.
    4. Optionally flag individual recording days using the same threshold.

    This approach explicitly accounts for repeated measurements (multiple days
    per subject) and is appropriate when no absolute clinical threshold for
    postural variability is available.

    :param df: Input ``pandas.DataFrame`` containing posture metrics.
    :param subject_col: Column name identifying the subject (e.g., participant ID).
    :param ellipse_area_col:Column name containing the 95% confidence ellipse area of postural sway.
    :param percentile: Percentile used to define the low-variability threshold (default is ``0.05``, corresponding to the 5th percentile).
    :param flag_daily: Whether to flag individual daily recordings whose ellipse area falls below the low-variability threshold.

    :returns:A tuple containing:
        - subject_level_df:
          Subject-level DataFrame with aggregated ellipse area metrics and a
          boolean flag indicating low postural variability.
        - low_variability_threshold:
          The ellipse area threshold below which postural variability is
          considered low.

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

    :param posture_subject_metrics_df:
    :param subject_id:
    :param full_recommender_dict:
    :param language:
    :return:
    """

    # init the recommendations dict with the rule
    recommendations_dict = {
        RULE_KEY: full_recommender_dict['sensors']['posture']['rule'][language]}

    # filter the DataFrame according to the rule
    posture_risk_subject_df = posture_subject_metrics_df[posture_subject_metrics_df['posture_95_confidence_ellipse_area'] < POSTURE_MIN_ELLIPSE_AREA_THRESHOLD]

    # get the unique subject IDs
    risk_subjects = posture_risk_subject_df['subject_id'].unique().tolist()


    if subject_id in risk_subjects:

        # get rows that belong to subject
        subject_data = posture_subject_metrics_df[posture_subject_metrics_df['subject_id'] == subject_id]

        # get the number of instances
        num_instances =len(subject_data)

        # get the dates
        risk_dates = subject_data['date'].tolist()

        # transform dates to strings
        risk_dates = dates_to_weekdays(risk_dates, date_format="%d-%m-%Y", locale=language)

        # generate dict
        recommendations_dict[RISK_DATES_KEY] = risk_dates
        recommendations_dict[NUM_INSTANCES_KEY] = num_instances
        recommendations_dict[RECOMMENDATIONS_KEY] = \
        full_recommender_dict['sensors']['posture']['recommendation'][language]


    else:

        # add that there are no recommendations needed
        recommendations_dict[RECOMMENDATIONS_KEY] = [NO_RECOMMENDATIONS[language]]


    return recommendations_dict

# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #