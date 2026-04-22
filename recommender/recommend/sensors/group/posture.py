# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pandas as pd
from typing import Tuple
# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #

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