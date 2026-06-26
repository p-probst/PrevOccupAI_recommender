# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path


# internal imports
from constants import SUBJECT_ID_COL, WORKTYPE_COL, WEEKDAY_COL, SHIFT_COL, FILE_FORMAT, \
    SESSION_NUM_COL, DATE_COL

from statistical_analysis.utils import get_back_transform, get_shift_counts
from statistical_analysis.models import lmm

# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
MAX_BPM_COL_orig = "HR_BPM_stats.max"
LOG_MAX_BPM_COL = "log_HR_BPM_max"

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def perform_max_bpm_analysis(df: pd.DataFrame, shift_df: pd.DataFrame, save_path: str | Path, show: bool = False) -> None:
    """
    run full BO vs FO max bpm analysis via LMM

    Pipeline
    --------
    1. Compute the balance (preprocessing).
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

    :param df: Raw hr_subject_metrics DataFrame as loaded from hr_subject_metrics.csv.
    :param shift_df: DataFrame containing the shifts of each subject. This DataFrame should be extracted from a phone sensor.
    :param save_path: Path to save the figure and result tables to.
    :param show: If True, show the Diagnostics plots.
    :return: None
    """
    print("\nPerforming max BPM analysis: log(max BPM)")
    # (1) pre-process
    analysis_data_df = _pre_process_hr_data(df, shift_df)

    # count the shifts per subject
    shift_counts = get_shift_counts(analysis_data_df)

    # (2) pre-conditions check
    icc = lmm.compute_icc(analysis_data_df, outcome=LOG_MAX_BPM_COL, subject_col=SUBJECT_ID_COL)

    # (3) fixed-effects model selection
    best_formula, model_comparison_df = lmm.select_fixed_effects(analysis_data_df, outcome=LOG_MAX_BPM_COL,
                                                                 group_col=WORKTYPE_COL, subject_col=SUBJECT_ID_COL,
                                                                 optional_covariates=[WEEKDAY_COL, SHIFT_COL, SESSION_NUM_COL])

    # (4) fit the selected model
    results_df, fig = lmm.fit_lmm(analysis_data_df, formula=best_formula, subject_col=SUBJECT_ID_COL, icc=icc)

    # (5) back transform
    results_df = get_back_transform(results_df)

    # show plot
    if show:
        plt.show()

    if save_path:
        # create folder
        folder_path = Path(save_path) / 'heart_rate'

        # make sure the directory exists
        folder_path.mkdir(parents=True, exist_ok=True)

        # store the plot
        fig.savefig(folder_path / f'max_bpm_diagnostics{FILE_FORMAT}')

        # store the results
        model_comparison_df.to_csv(folder_path / f'max_bpm_model_comparison.csv', index=False)
        results_df.to_csv(folder_path / 'max_bpm_lmm_results.csv', index=False)
        shift_counts.to_csv(folder_path / f'shift_counts.csv', index=True)

    # close the figure
    plt.close(fig)


def _pre_process_hr_data(df: pd.DataFrame, shift_df: pd.DataFrame) -> pd.DataFrame:
    """
    prepare heart rate data for LMM

    The preprocessing consists of performing a log transforms and adding the shifts to the DataFrame
    :param df: pandas.DataFrame containing the heart rate data.
    :param shift_df: DataFrame containing the shifts of each subject. This DataFrame should be extracted from a phone sensor.
    :return: pre-processed heart rate data
    """

    df = df.copy()

    # merge shift onto df
    df = df.merge(shift_df, on=[SUBJECT_ID_COL, DATE_COL], how='left', validate='many_to_one')

    # rename bpm column
    df = df.rename(columns={MAX_BPM_COL_orig: LOG_MAX_BPM_COL})

    # apply log transform
    df[LOG_MAX_BPM_COL] = np.log(df[LOG_MAX_BPM_COL])

    return df[[SUBJECT_ID_COL, WORKTYPE_COL, WEEKDAY_COL, SHIFT_COL, SESSION_NUM_COL, LOG_MAX_BPM_COL]]


