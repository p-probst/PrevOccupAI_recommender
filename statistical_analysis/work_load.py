# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pingouin as pg
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# internal imports
from constants import SUBJECT_ID_COL, WORKTYPE_COL, WEEKDAY_COL, FILE_FORMAT
from statistical_analysis.models import lmm
# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
ALL_ITEMS = [
    "focus_and_mental_strain",
    "rushed_and_under_pressure",
    "frequent_interruptions",
    "more_effort_than_resources",
    "heavy_workload",
]

COMPOSITE_ITEMS = [
    "focus_and_mental_strain",
    "rushed_and_under_pressure",
    "more_effort_than_resources",
    "heavy_workload",
]

COMPOSITE_COL = "workload_composite"
WORKLOAD_MEAN = "workload_mean_subj"
WORKLOAD_DEV = "workload_dev"
# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def perform_workload_analysis(df: pd.DataFrame, save_path: str | Path, show: bool=False) -> pd.DataFrame:
    """
    Run the full workload analysis.

    Pipeline
    --------
    1. Pre-processing (log-transform).
    2. Precondition checks: ICC.
    3. Fixed-effect model selection: compare base model:
                                     ``b ~ work_type + (1|subject_id)``
                                     against the weekday-adjusted models
                                     ``b ~ work_type + C(weekday) + (1|subject_id)``
                                     via AIC/BIC and LRT on ML fits.
    4. Refit selected model with REML for final inference.
    5. Diagnostic plots: residuals vs fitted, Q-Q residuals, Q-Q BLUPs.
    6. Effect size: Cohen's d (marginal SD denominator).
    :param df: Raw workload_subject_metrics DataFrame as loaded from hr_subject_metrics.csv.
    :param save_path: Path to save the figure and result tables to.
    :param show: If True, show the Diagnostics plots
    :return: pandas.DataFrame containing the workload subject mean and deviation for each subject and weekday
    """

    print("\nPerforming EMG workload analysis")

    # (1) preprocessing
    analysis_data_df = _pre_process_workload(df)

    # add workload mean and deviation (this is needed for analyses where the workload is used as a co-variate in other models)
    workload_composite_df = _add_workload_centring(analysis_data_df)

    # (2) precondition checks
    icc = lmm.compute_icc(analysis_data_df, outcome=COMPOSITE_COL, subject_col=SUBJECT_ID_COL)

    # (3) fixed-effects model selection
    best_formula, model_comparison_df = lmm.select_fixed_effects(analysis_data_df, outcome=COMPOSITE_COL,
                                                                 group_col=WORKTYPE_COL, subject_col=SUBJECT_ID_COL,
                                                                 optional_covariates=[WEEKDAY_COL])

    # (4) fit the selected model
    results_df, fig = lmm.fit_lmm(analysis_data_df, formula=best_formula, subject_col=SUBJECT_ID_COL, icc=icc)

    # show plot
    if show:
        plt.show()

    # save the results and the plot
    if save_path:
        # create folder
        folder_path = Path(save_path) / 'workload'

        # make sure the directory exists
        folder_path.mkdir(parents=True, exist_ok=True)

        # store the plot
        fig.savefig(folder_path / f'workload_diagnostics{FILE_FORMAT}')

        # store the dataframes
        model_comparison_df.to_csv(folder_path / f'workload_model_comparison.csv', index=False)
        results_df.to_csv(folder_path / f'workload_llm_results.csv', index=False)

    # close the figure
    plt.close(fig)

    return workload_composite_df



# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #
def _pre_process_workload(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full pre-processing pipeline for the daily workload questionnaire.

    Steps
    -----
    1. Print Pearson correlation matrix for all five items (stdout).
    2. Compute and print Cronbach's α with 95% CI for the four-item subset.
    3. Build the composite score (row mean of the four coherent items).
    4. Return a tidy DataFrame ready for the LMM.

    The ``open_question`` column is not expected in the input; caller should drop it before passing the DataFrame.

    :param df: DataFrame with columns ``subject_id``, ``date``, ``weekday``,
        ``work_type``, and the five Likert item columns.
    :returns: DataFrame with columns
        ``[subject_id, date, weekday, work_type, workload_composite]``.
        Rows with missing composite days retain NaN in ``workload_composite``.
    """
    # check correlation and item reliability
    _check_item_correlations(df, ALL_ITEMS)
    _check_reliability(df, COMPOSITE_ITEMS)

    df = df.copy()

    df[COMPOSITE_COL] = df[COMPOSITE_ITEMS].mean(axis=1)

    return df[[SUBJECT_ID_COL, WORKTYPE_COL, WEEKDAY_COL, COMPOSITE_COL]].dropna().reset_index(drop=True)


def _check_item_correlations(df: pd.DataFrame, items: list[str]) -> None:
    """
    Print the Pearson correlation matrix for the given Likert items.

    Computed on complete rows only (listwise deletion).  The purpose is to display the item-level structure before
    composite construction, so that the coherence of the four-item subset can be visually confirmed and reported.

    :param df: DataFrame containing the item columns.
    :param items: List of column names to include in the correlation matrix.

    Reference:
        Carifio, J., & Perla, R. (2008). Resolving the 50-year debate around
        using and misusing Likert scales. Medical Education, 42(12), 1150–1152.
        https://doi.org/10.1111/j.1365-2923.2008.03172.x
    """

    df = df.copy()
    complete = df.dropna(subset=items)
    n_complete = len(complete)
    n_dropped = len(df) - n_complete

    corr = complete[items].corr(method="pearson")

    print("=" * 60)
    print("WORKLOAD ITEMS – Pearson Correlation Matrix")
    print(f"  N = {n_complete} complete rows  ({n_dropped} missing days excluded)")
    print("=" * 60)
    print(corr.round(2).to_string())
    print()


def _check_reliability(df: pd.DataFrame, items: list[str]) -> None:
    """
    Compute and print Cronbach's alpha with a 95% CI for a set of Likert items.

    Uses ``pingouin.cronbach_alpha`` with listwise deletion (consistent with the correlation step).  The 95% CI is
    computed via Feldt's method (Feldt, Woodruff & Salih, 1987).

    Note: alpha is computed on pooled rows (within- and between-subject variance combined).  With repeated measures this
    inflates alpha relative to a purely between-subject estimate; treat the value as an upper bound (Geldhof, Preacher & Zyphur, 2014).

    :param df: DataFrame containing the item columns.
    :param items: List of column names forming the composite.

    References:
        Cronbach, L. J. (1951). Coefficient alpha and the internal structure
            of tests. Psychometrika, 16(3), 297–334.
            https://doi.org/10.1007/BF02310555

        Feldt, L. S., Woodruff, D. J., & Salih, F. A. (1987). Statistical
            inference for coefficient alpha. Applied Psychological Measurement,
            11(1), 93–103. https://doi.org/10.1177/014662168701100107

        Geldhof, G. J., Preacher, K. J., & Zyphur, M. J. (2014). Reliability
            estimation in a multilevel confirmatory factor analysis framework.
            Psychological Methods, 19(1), 72–91.
            https://doi.org/10.1037/a0032138
    """
    threshold = 0.70  # conventional minimum (Nunnally, 1978)

    alpha, ci = pg.cronbach_alpha(data=df[items], nan_policy="listwise")
    verdict = "acceptable (≥ 0.70)" if alpha >= threshold else "below threshold (< 0.70)"

    print("=" * 60)
    print("COMPOSITE ITEMS – Internal Consistency (Cronbach's α)")
    print(f"  Items  : {', '.join(items)}")
    print(f"  α      : {alpha:.3f}  [{verdict}]")
    print(f"  95% CI : [{ci[0]:.3f}, {ci[1]:.3f}]")
    print("  Note   : pooled across levels; likely inflated for repeated-")
    print("           measures data (Geldhof et al., 2014).")
    print("=" * 60)
    print()


def _add_workload_centring(analysis_data_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add within-person centring columns.

    Three columns are added to the dataframe:

    - ``workload_mean_subj``: each subject's mean composite across all their
      valid days (between-person component).
    - ``workload_dev``: daily deviation from the subject mean (within-person component); ``workload_composite - workload_mean_subj``.

    Person-mean centring decomposes the composite into orthogonal between- and within-person components, ensuring that
    the coefficient of ``workload_dev`` in a subsequent LMM estimates the within-person workload-EMG association without
    confounding by stable between-subject differences in workload perception (Curran & Bauer, 2011).

    :param analysis_data_df: pre-processed workload data. Already contains the composite workload item
    :returns: Copy of ``df`` with the new columns appended.

    :reference: Curran, P. J., & Bauer, D. J. (2011). The disaggregation of within-person and between-person effects in
                longitudinal models of change. *Annual Review of Psychology*, *62*, 583–619.
                https://doi.org/10.1146/annurev.psych.093008.100356
    """
    analysis_data_df = analysis_data_df.copy()

    subj_mean = analysis_data_df.groupby(SUBJECT_ID_COL)[COMPOSITE_COL].transform("mean")

    analysis_data_df[WORKLOAD_MEAN] = subj_mean
    analysis_data_df[WORKLOAD_DEV] = analysis_data_df[COMPOSITE_COL] - subj_mean

    return analysis_data_df[[SUBJECT_ID_COL, WEEKDAY_COL, COMPOSITE_COL, WORKLOAD_MEAN, WORKLOAD_DEV]]