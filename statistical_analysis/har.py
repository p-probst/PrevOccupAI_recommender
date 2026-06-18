# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path


# internal imports
from constants import SUBJECT_ID_COL, WORKTYPE_COL, WEEKDAY_COL, SESSION_TIME_COL, SHIFT_COL, FILE_FORMAT
from statistical_analysis.utils import transform_time_to_shift, get_back_transform, drop_short_recordings
from statistical_analysis.models import lmm
# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
TOTAL_DURATION_COL = "total_duration_hour"
STEP_RATE_HOURS_COL = "step_rate"
LOG_STEP_RATE_HOURS_COL = "log_step_rate"
NUM_STEPS_COL = "HAR_steps.num_steps"

SITTING_COL = "HAR_distributions.Sentado"
STANDING_COL = "HAR_distributions.De pé"
WALKING_COL = "HAR_distributions.Andar"

ACTIVE_SUM_COL = "sum_active"
ILR_COL  = "ILR_sitting_vs_active"



MIN_DURATION_H = 1
# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def perform_step_count_analysis(df: pd.DataFrame, save_path: str | Path, show: bool = False) -> None:
    """
    Run the full FO vs BO step-count analysis via a Poisson GEE with a recording-duration offset.

    Pipeline
    --------
    1. Preprocessing: derive total recording duration, drop short recordings, build log(steps/hour).
    2. Fit Poisson LMM: ``num_steps ~ work_type``, grouped by ``subject_id``, exchangeable working correlation,
                        offset = log(total_duration_sec).

    3. Diagnostics: Pearson dispersion statistic and residuals-vs-fitted plot.
    4. Results summary: coefficient, robust SE, z, p-value, incidence rate ratio (IRR) and 95% CI per term.

    :param df: Raw har_subject_metrics DataFrame as loaded from har_subject_metrics.csv.
    :param save_path: Path to save the figure and result tables to.
    :param show: If True, show the figure.
    :returns: None

    :reference: Liang, K.-Y., & Zeger, S. L. (1986). Longitudinal data analysis using generalized linear models.
                Biometrika, 73(1), 13-22. https://doi.org/10.1093/biomet/73.1.13
    """

    # (1) preprocessing
    analysis_data_df = _pre_process_step_count_data(df)

    # (2) preconditions check
    icc = lmm.compute_icc(analysis_data_df, outcome=LOG_STEP_RATE_HOURS_COL, subject_col=SUBJECT_ID_COL)

    # (3) fixed-effects model selection
    best_formula, model_comparison_df = lmm.select_fixed_effects(analysis_data_df, outcome=LOG_STEP_RATE_HOURS_COL,
                                                                 group_col=WORKTYPE_COL, subject_col=SUBJECT_ID_COL,
                                                                 optional_covariates=[WEEKDAY_COL, SHIFT_COL])

    # (4) fit the selected model
    results_df, fig = lmm.fit_lmm(analysis_data_df, formula=best_formula, subject_col=SUBJECT_ID_COL, icc=icc)

    # (5) perform back transform of log transform
    results_df = get_back_transform(results_df)


    # show plot
    if show:
        plt.show()

    if save_path:

        # create folder
        folder_path = Path(save_path) / 'har'

        # make sure the directory exists
        folder_path.mkdir(parents=True, exist_ok=True)

        # store the plot
        fig.savefig(folder_path / f'log_step_count_diagnostics{FILE_FORMAT}')

        # store the results
        model_comparison_df.to_csv(folder_path / f'log_step_count_model_comparison.csv', index=False)
        results_df.to_csv(folder_path / 'log_step_count_lmm_results.csv', index=False)

    # close the figure
    plt.close(fig)



def perform_har_proportions_analysis(df: pd.DataFrame, save_path: str | Path, show: bool = False) -> None:
    """
    Run the full FO vs BO HAR proportions analysis on the sitting-vs-active ILR balance

    Pipeline
    --------
    1. Compute the balance (preprocessing).
    2. Precondition checks: ICC.
    3. Fixed-effect model selection: compare base model:
                                     ``b ~ work_type + (1|subject_id)``
                                     against the weekday-adjusted models
                                     ``b ~ work_type + C(weekday) + (1|subject_id)``
                                     ``b ~ work_type + C(shift) + (1|subject_id)``
                                     and weekday-adjusted models against a compound model
                                     ``b ~ work_type + C(weekday) + C(shift) + (1|subject_id)``
                                     via AIC/BIC and LRT on ML fits.
    4. Refit selected model with REML for final inference.
    5. Diagnostic plots: residuals vs fitted, Q-Q residuals, Q-Q BLUPs.
    6. Effect size: Cohen's d (marginal SD denominator).
    :param df: pandas.DataFrame containing the HAR metrics
    :param save_path: Path to save the figure to.
    :param show: If True, show the figure.
    :return: None

    :reference: Pinheiro, J. C., & Bates, D. M. (2000). *Mixed-Effects Models in S and S-PLUS*. Springer
    """

    # (1) pre-processing
    analysis_data_df = _pre_process_har_proportions_data(df)

    icc = lmm.compute_icc(analysis_data_df, outcome=ILR_COL, subject_col=SUBJECT_ID_COL)

    # (3) fixed-effects model selection
    best_formula, model_comparison_df = lmm.select_fixed_effects(analysis_data_df, outcome=ILR_COL,
                                                                 group_col=WORKTYPE_COL, subject_col=SUBJECT_ID_COL,
                                                                 optional_covariates=[WEEKDAY_COL, SHIFT_COL])

    # (4) fit the selected model
    results_df, fig = lmm.fit_lmm(analysis_data_df, formula=best_formula, subject_col=SUBJECT_ID_COL, icc=icc)

    # (5) perform back transform of log transform
    results_df = get_back_transform(results_df, is_ilr=True)

    # show plot
    if show:
        plt.show()

    if save_path:
        # create folder
        folder_path = Path(save_path) / 'har'

        # make sure the directory exists
        folder_path.mkdir(parents=True, exist_ok=True)

        # store the plot
        fig.savefig(folder_path / f'har_prop_diagnostics{FILE_FORMAT}')

        # store the results
        model_comparison_df.to_csv(folder_path / f'har_prop_model_comparison.csv', index=False)
        results_df.to_csv(folder_path / 'har_prop_lmm_results.csv', index=False)




        # close the figure
        plt.close(fig)


# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #
def _pre_process_step_count_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare the HAR DataFrame for the step-count GEE.

    Steps
    -----
    1. Recover total recording duration per subject-day from the sitting proportion/duration pair:

           total_duration_sec = Sentado_duration_sec / Sentado_proportion

       since HAR_distributions.Sentado is the fraction of total recording time spent sitting.

    2. Drop subject-days with total_duration_sec < 1 hour. These reflect short, equipment-setup or weather-disrupted
       recordings (e.g. the subject 126 day with ~20 minutes of recording) rather than a genuine full-shift exposure.
       Missingness here is treated as MCAR: it arises from external scheduling/weather disruption unrelated to the
       subject's own step-count behaviour on that day.

    3. Compute step rate as steps/hour and apply log-transform. This is done as the residuals on the raw model were
       not normally distributed.

    4. Derive shift via :func:`_transform_time_to_shift` from the session acquisition time. Retained for potential
       future use, not used in the current model.

    5. Print simple missing-data and distribution summaries.

    :param df: Raw har_subject_metrics DataFrame.
    :returns: Tidy DataFrame with columns [subject_id, work_type, weekday, shift, num_steps, log_duration].

    :reference: Liang, K.-Y., & Zeger, S. L. (1986). Longitudinal data analysis using generalized linear models.
                Biometrika, 73(1), 13-22. https://doi.org/10.1093/biomet/73.1.13
    """
    df = df.copy()

    # recover total recording duration (convert it to hours) + drop short recordings (MCAR, e.g. subject 126)
    df = drop_short_recordings(df, duration_s_col="HAR_durations.Sentado_duration_sec", class_distribution_col="HAR_distributions.Sentado")

    # calculate step rate and its log
    df[STEP_RATE_HOURS_COL] = df[NUM_STEPS_COL] / df[TOTAL_DURATION_COL]
    df[LOG_STEP_RATE_HOURS_COL] = np.log(df[STEP_RATE_HOURS_COL])

    # derive shift
    df[SHIFT_COL] = df[SESSION_TIME_COL].apply(transform_time_to_shift)

    # simple distribution checks
    print(f"step_rate_hours: "
          f"min={df[STEP_RATE_HOURS_COL].min()}, max={df[STEP_RATE_HOURS_COL].max()}, "
          f"mean={df[STEP_RATE_HOURS_COL].mean():.1f}, std={df[STEP_RATE_HOURS_COL].std():.1f}")

    return df[[SUBJECT_ID_COL, WORKTYPE_COL, WEEKDAY_COL, SHIFT_COL, LOG_STEP_RATE_HOURS_COL]].copy()


def _pre_process_har_proportions_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    pre-processes the HAR proportions data and calculates a ILR transform based on sitting vs active
    :param df: Raw har_subject_metrics DataFrame.
    :return: pre-processed HAR proportions DataFrame, containing the calculated ILR transform
    """

    df = df.copy()

    # recover total recording duration (convert it to hours) + drop short recordings (MCAR, e.g. subject 126)
    df = drop_short_recordings(df, duration_s_col="HAR_durations.Sentado_duration_sec", class_distribution_col="HAR_distributions.Sentado")

    # derive shift
    df[SHIFT_COL] = df[SESSION_TIME_COL].apply(transform_time_to_shift)

    # compute ilr
    df = _compute_ilr_har(df)

    return df[[SUBJECT_ID_COL, WORKTYPE_COL, WEEKDAY_COL, SHIFT_COL, ILR_COL]]



def _compute_ilr_har(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the two ILR coordinates for the HAR compositional triplet (Sentado, De pé, Andar) using an explicit
    Sequential Binary Partition (SBP).

    The SBP is::

        Part      b1    b2
        Sentado   +1     0
        De pé     -1    +1
        Andar     -1    -1

    This yields two orthonormal balances:

    - b1 (sedentary vs. active): contrasts Sentado against the geometric mean of {De pé, Andar}. This is the primary
      occupational health contrast — sedentary time versus all active time.

    - b2 (standing vs. walking): contrasts De pé against Andar, within the active subcomposition. This resolves the
      remaining degree of freedom.

    The coordinate formulas follow directly from the SBP (Egozcue et al., 2003, §3):

        b1 = sqrt(r*s / (r+s)) * ln(g(x+) / g(x-))

    where r and s are the number of parts in the + and - groups respectively, and g(·) denotes the geometric mean of
    that group. For b1: r=1, s=2; for b2: r=1, s=1.

    No zero-replacement is required: all three HAR proportions are observed in every row (0% missing, confirmed
    from data summary).

    :param df: DataFrame containing the three HAR proportion columns. Each row must sum to approximately 1. No NaN values expected.
    :return: Input DataFrame with two new columns appended: ilr_b1_sentado_vs_active and ilr_b2_depe_vs_andar.

    :raises ValueError: If any proportion value is zero or negative, which would make the logarithm undefined.

    :reference:  Egozcue, J. J., Pawlowsky-Glahn, V., Mateu-Figueras, G., & Barceló-Vidal, C. (2003). Isometric logratio
                 transformations for compositional data analysis. Mathematical Geology, 35(3), 279-300.
                 https://doi.org/10.1023/A:1023818214614
    """

    df = df.copy()

    # compute balance
    sitting = df[SITTING_COL]
    active = 1 - sitting

    # calculate ILR
    df[ILR_COL] = (1 / np.sqrt(2)) * np.log(sitting / active)

    return df

