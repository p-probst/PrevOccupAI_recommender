# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Tuple, List

# internal imports
from constants import SUBJECT_ID_COL, WORK_TYPES, DATE_COL, SESSION_NUM_COL, WORKTYPE_COL, WEEKDAY_COL, SHIFT_COL, FILE_FORMAT
from statistical_analysis.utils import get_shift_counts, get_back_transform
from statistical_analysis.models import lmm
# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
P_10 = "p10"
P_50 = "p50"
P_90 = "p90"

# placement
LEFT = "left"
RIGHT = "right"

MAX_NUM_SESSIONS_SUBJECT = 20 # (4 sessions per day, five days in a week)
# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def perform_emg_apdf_analysis(df: pd.DataFrame, shift_df: pd.DataFrame, save_path: str | Path, show: bool=False) -> None:
    """
    Run the full EMG APDF analysis. The analysis is performed for the left and right separately.
    IMPORTANT: Due to different data loss rates for left and right EMG, the two analyses use different cohorts of data.
    Thus, these are not directly comparable.

    Pipeline
    --------
    1. Pre-processing (log-transform).
    2. Precondition checks: ICC.
    3. Fixed-effect model selection: compare base model:
                                     ``b ~ work_type + (1|subject_id)``
                                     against the weekday-adjusted models
                                     ``b ~ work_type + C(weekday) + (1|subject_id)``
                                     ``b ~ work_type + C(shift) + (1|subject_id)``
                                     ``b ~ work_type + C(Session) + (1|subject_id)``
                                     and weekday-adjusted models against a compound model
                                     ``b ~ work_type + C(weekday) + C(shift) + C(Session) + (1|subject_id)``
                                     via AIC/BIC and LRT on ML fits.
    4. Refit selected model with REML for final inference.
    5. Diagnostic plots: residuals vs fitted, Q-Q residuals, Q-Q BLUPs.
    6. Effect size: Cohen's d (marginal SD denominator).
    :param df: Raw emg_apdf_subject_metrics DataFrame as loaded from hr_subject_metrics.csv.
    :param shift_df: DataFrame containing the shifts of each subject. This DataFrame should be extracted from a phone sensor.
    :param save_path: Path to save the figure and result tables to.
    :param show: If True, show the Diagnostics plots
    :return: None
    """
    print("Performing EMG APDF analysis")

    # (0) check data availability
    _summarise_emg_availability(df)

    # (1) pre-process
    analysis_data_df, var_cols = _pre_process_emg_data(df, shift_df)

    print(analysis_data_df[["log_left_p10", "log_right_p10"]].min())

    # cycle over the positions
    for placement, opp_placement in [(LEFT, RIGHT), (RIGHT, LEFT)]:

        print(f"\n---- Analysis for MBAN placement: {placement} ---- ")
        # get the columns
        placement_cols = [col for col in analysis_data_df.columns if opp_placement not in col]

        # get the data that belongs to the placement
        placement_data_df = analysis_data_df[placement_cols].dropna().reset_index(drop=True)

        shift_counts = get_shift_counts(placement_data_df)

        for outcome in [P_10, P_50, P_90]:

            # generate outcome based on placement
            placement_outcome = f"log_{placement}_{outcome}"

            # (2) pre-conditions check
            icc = lmm.compute_icc(placement_data_df, outcome=placement_outcome, subject_col=SUBJECT_ID_COL)

            # (3) fixed-effects model selection
            best_formula, model_comparison_df = lmm.select_fixed_effects(placement_data_df, outcome=placement_outcome,
                                                                         group_col=WORKTYPE_COL,
                                                                         subject_col=SUBJECT_ID_COL,
                                                                         optional_covariates=[WEEKDAY_COL, SHIFT_COL,
                                                                                              SESSION_NUM_COL])

            # for left the shift model was chosen as best, however it is not significant and BIC and AIC are only marginally better
            # thus the simple model that just differentiates based on the work type is chosen
            if placement == LEFT and outcome in[P_50, P_90]:
                best_formula = model_comparison_df['formula'].loc[1]

            # (4) fit the selected model
            results_df, fig = lmm.fit_lmm(placement_data_df, formula=best_formula, subject_col=SUBJECT_ID_COL, icc=icc)

            # (5) potential back transform
            # (5) back transform
            results_df = get_back_transform(results_df)

            # show plot
            if show:
                plt.show()

            if save_path:
                # create folder
                folder_path = Path(save_path) / 'emg'

                # make sure the directory exists
                folder_path.mkdir(parents=True, exist_ok=True)

                # store the plot
                fig.savefig(folder_path / f'{placement_outcome}_diagnostics{FILE_FORMAT}')

                # store the results
                model_comparison_df.to_csv(folder_path / f'{placement_outcome}_model_comparison.csv', index=False)
                results_df.to_csv(folder_path / f'{placement_outcome}_lmm_results.csv', index=False)
                shift_counts.to_csv(folder_path / f'{placement}_shift_counts.csv', index=True)

    print('test')
# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #
def _summarise_emg_availability(df: pd.DataFrame) -> None:
    """
    Print session-level availability tables for bilateral EMG data.

    Builds boolean masks from the session indicator columns (``left.Session`` and ``right.Session``), which are the
    canonical presence flags: a NaN session means all variables for that side/session are absent.
    Three tables are printed:

    1. **Session totals** — counts under each mask, split by work_type.
    2. **Option 3 contamination** — per-subject breakdown of bilateral vs
       unilateral sessions, showing how impure a left/right mean would be.
    3. **Per-subject coverage** — min / median / max sessions available
       under left, right, and both masks; flags subjects with zero sessions
       on either side.

    :param df: Raw EMG APDF dataframe with columns ``left.Session``, ``right.Session``, ``subject_id``, and ``work_type``.
    :type df: pd.DataFrame

    note::
        Session indicator columns are read as float by pandas due to NaN
        values; notna() is used directly rather than casting to int.

    reference:
    Laird, N. M., & Ware, J. H. (1982). Random-effects models for longitudinal data. *Biometrics*, *38*\(4), 963–974.
    https://doi.org/10.2307/2529876
    """

    # copy DataFrame
    availability_df = df.copy()

    # get non-nan mask for left and right
    L = availability_df[f"{LEFT}.Session"].notna()
    R = availability_df[f"{RIGHT}.Session"].notna()

    # built masks
    masks = {
        "left":       L,
        "right":      R,
        "both":       L & R,
        "either":     L | R,
        "left_only":  L & ~R,
        "right_only": R & ~L,
    }

    # ------------------------------------------------------------------
    # Table 1: session-level totals
    # ------------------------------------------------------------------
    print("=" * 60)
    print("TABLE 1 — Session-level totals")
    print("=" * 60)

    rows = []
    for name, mask in masks.items():
        sub = availability_df.loc[mask, "work_type"].value_counts().to_dict()
        rows.append({
            "mask":  name,
            "total": int(mask.sum()),
            "FO":    sub.get("FO", 0),
            "BO":    sub.get("BO", 0),
        })

    print(pd.DataFrame(rows).to_string(index=False))

    # ------------------------------------------------------------------
    # Table 2: per-subject coverage
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("TABLE 2 — per subject coverage in FO and BO groups")
    print("=" * 60)

    # add columns to availability df
    availability_df = availability_df.assign(left=masks["left"], right=masks["right"], both=masks["both"],
                  left_only=masks["left_only"],right_only=masks["right_only"])

    # cycle over the work types
    for work_type in WORK_TYPES:

        print(f"\n----- {work_type} -----")

        # get the data that corresponds to the work_type
        sub_df = availability_df[availability_df["work_type"] == work_type]


        acquisition_coverage = sub_df.groupby("subject_id")[["left", "right","both", "left_only", "right_only"]].sum().astype(int)

        acquisition_coverage["left_pct"] = ((acquisition_coverage["left"] / MAX_NUM_SESSIONS_SUBJECT) * 100).round(1)
        acquisition_coverage["right_pct"] = ((acquisition_coverage["right"] / MAX_NUM_SESSIONS_SUBJECT) * 100).round(1)
        acquisition_coverage["both_pct"] = ((acquisition_coverage["both"] / MAX_NUM_SESSIONS_SUBJECT) * 100).round(1)

        print(acquisition_coverage.to_string())
        print(f"\nOverall left : {acquisition_coverage['left'].sum()} / {len(acquisition_coverage) * MAX_NUM_SESSIONS_SUBJECT} ({(acquisition_coverage['left'].sum() / (len(acquisition_coverage) * MAX_NUM_SESSIONS_SUBJECT)) * 100:.1f}%)")
        print(f"Overall right : {acquisition_coverage['right'].sum()} / {len(acquisition_coverage) * MAX_NUM_SESSIONS_SUBJECT} ({(acquisition_coverage['right'].sum() / (len(acquisition_coverage) * MAX_NUM_SESSIONS_SUBJECT)) * 100:.1f}%)")
        print(f"Overall both : {acquisition_coverage['both'].sum()} / {len(acquisition_coverage) * MAX_NUM_SESSIONS_SUBJECT} ({(acquisition_coverage['both'].sum() / (len(acquisition_coverage) * MAX_NUM_SESSIONS_SUBJECT)) * 100:.1f}%)")


def _pre_process_emg_data(df: pd.DataFrame, shift_df: pd.DataFrame ) -> Tuple[pd.DataFrame, List[str]]:
    """
    pre-processes the EMG data, by
    (1) adding shift column
    (2) rename columns for easier handling
    (3) unifying session column (left and right)
    (4) apply log-transform
    :param df: pandas.DataFrame containing the EMF APDF data
    :param shift_df: pandas.DataFrame containing the shifts of each subject. This DataFrame should be extracted from a phone sensor.
    :return: pre-processed EMG data
    """

    df = df.copy()

    # merge shift onto df
    df = df.merge(shift_df, on=[SUBJECT_ID_COL, DATE_COL], how='left', validate='many_to_one')

    # rename columns
    df_cols = df.columns.tolist()
    df_cols = [f"{col.split('.')[0]}_{col.split('.')[-1]}" if ".EMG" in col else col for col in df_cols]
    df.columns = df_cols

    # unify session num col
    df[SESSION_NUM_COL] = df[f'{LEFT}.{SESSION_NUM_COL}'].combine_first(df[f'{RIGHT}.{SESSION_NUM_COL}']).astype(int)
    # drop the left and right session number columns as they are not needed anymore
    df = df.drop(columns=[f"{LEFT}.{SESSION_NUM_COL}", f"{RIGHT}.{SESSION_NUM_COL}"])

    # get column names that start with left or right
    var_cols = [col for col in df.columns if col.startswith((f"{LEFT}_", f"{RIGHT}_"))]

    log_var_cols = []
    # apply log transform
    for col in var_cols:

        # create new column name
        log_col = f'log_{col}'

        df[log_col] = np.log(df[col])
        log_var_cols.append(log_col)

    # define columns to keep
    cols_to_keep = [SUBJECT_ID_COL, WORKTYPE_COL, WEEKDAY_COL, SHIFT_COL, SESSION_NUM_COL]
    cols_to_keep.extend(log_var_cols)

    return df[cols_to_keep], log_var_cols
