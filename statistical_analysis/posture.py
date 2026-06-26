# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path


# internal imports
from constants import SUBJECT_ID_COL, WORKTYPE_COL, WEEKDAY_COL, SESSION_TIME_COL, SHIFT_COL, FILE_FORMAT
from statistical_analysis.utils import transform_time_to_shift, get_shift_counts, get_back_transform
from statistical_analysis.models import lmm

# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
POSTURE_ELLIPSE_COL = "posture_95_confidence_ellipse_area"
LOG_ELLIPSE_COL = "log_ellipse"

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def perform_posture_ellipse_analysis(df: pd.DataFrame, save_path: str | Path, cml_shifts: bool = True, show: bool = False) -> None:
    """
    run full BO vs FO posture analysis via LMM

    Pipeline
    --------
    1. Preprocessing: log(posture_95_confidence_ellipse_area).
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


    :param df: Raw posture_subject_metrics DataFrame as loaded from har_subject_metrics.csv.
    :param save_path: Path to save the figure and result tables to.
    :param cml_shifts: whether to use the actual CML shifts (morning, midday, afternoon) or a simplified (morning, afternoon)
    :param show: If True, show the figure.
    :returns: None

    :reference: Liang, K.-Y., & Zeger, S. L. (1986). Longitudinal data analysis using generalized linear models.
                Biometrika, 73(1), 13-22. https://doi.org/10.1093/biomet/73.1.13
    :reference: Pinheiro, J. C., & Bates, D. M. (2000). *Mixed-Effects Models in S and S-PLUS*. Springer
    """
    print("\nPerforming posture analysis: log(posture_95_confidence_ellipse_area)")
    # (1) pre-processing
    analysis_data_df = _pre_process_posture(df, cml_shifts)

    # count the sifts per subject (this has only to be done once for the phone derived sensors in the dataset)
    _ = get_shift_counts(analysis_data_df)

    # (2) pre-conditions check
    icc = lmm.compute_icc(analysis_data_df, outcome=LOG_ELLIPSE_COL, subject_col=SUBJECT_ID_COL)

    # (3) fixed-effects model selection
    best_formula, model_comparison_df = lmm.select_fixed_effects(analysis_data_df, outcome=LOG_ELLIPSE_COL,
                                                                 group_col=WORKTYPE_COL, subject_col=SUBJECT_ID_COL,
                                                                 optional_covariates=[WEEKDAY_COL, SHIFT_COL])

    # in this case the difference between the shift model is only marginally better and the p is not significant
    #best_formula = model_comparison_df.iloc[1]["formula"]

    # (4) fit the selected model
    results_df, fig = lmm.fit_lmm(analysis_data_df, formula=best_formula, subject_col=SUBJECT_ID_COL, icc=icc)

    # (5) perform back transform of log transform
    results_df = get_back_transform(results_df)

    # show plot
    if show:
        plt.show()

    if save_path:
        # create folder
        folder_path = Path(save_path) / 'posture'

        # make sure the directory exists
        folder_path.mkdir(parents=True, exist_ok=True)

        # store the plot
        fig.savefig(folder_path / f'posture_ellipse_diagnostics{FILE_FORMAT}')

        # store the results
        model_comparison_df.to_csv(folder_path / f'posture_ellipse_model_comparison.csv', index=False)
        results_df.to_csv(folder_path / 'posture_ellipse_lmm_results.csv', index=False)

    # close the figure
    plt.close(fig)


# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #
def _pre_process_posture(df: pd.DataFrame, cml_shifts: bool = True) -> pd.DataFrame:
    """
    prepare the posture data for LMM

    The preprocessing consists of performing a log transform and obtaining the shift from the start time of the
    recording.
    :param df: pandas.DataFrame containing the posture data
    :param cml_shifts: whether to use the actual CML shifts (morning, midday, afternoon) or a simplified (morning, afternoon)
    :return: pre-processed posture data
    """

    df = df.copy()

    # apply log transform
    df[LOG_ELLIPSE_COL] = np.log(df[POSTURE_ELLIPSE_COL])

    # derive shift
    df[SHIFT_COL] = df[SESSION_TIME_COL].apply(transform_time_to_shift, cml_shifts=cml_shifts)


    return df[[SUBJECT_ID_COL, WORKTYPE_COL, WEEKDAY_COL, SHIFT_COL,LOG_ELLIPSE_COL]].copy()