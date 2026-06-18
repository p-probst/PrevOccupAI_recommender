# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path



# internal imports
from statistical_analysis.models import lmm as lmm
from statistical_analysis.utils import transform_time_to_shift, get_back_transform
from constants import SUBJECT_ID_COL, WORKTYPE_COL, WEEKDAY_COL, SESSION_TIME_COL, FILE_FORMAT

# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
NOISE_BALANCE_COL = "ILR_noise"
SHIFT_COL = "shift"


# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def perform_noise_exposure_analysis(df: pd.DataFrame, save_path: str | Path, show: bool=False) -> None:
    """
    Run the full FO vs BO noise-exposure analysis on the loud-vs-quiet
    ILR balance.

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

    :param df: Raw noise_subject_metrics DataFrame as loaded from noise_subject_metrics.csv.
    :param save_path: Path to save the figure to.
    :param show: If True, show the figure.
    :returns: None

    :reference: Pinheiro, J. C., & Bates, D. M. (2000). *Mixed-Effects Models in S and S-PLUS*. Springer.
    """
    # (1) preprocessing
    analysis_data_df = _compute_noise_balance_ilr(df)

    analysis_data_df[SHIFT_COL] = analysis_data_df[SESSION_TIME_COL].apply(transform_time_to_shift)

    # count the sifts per subject (this has only be done once for the entire dataset)
    shift_counts = analysis_data_df.groupby([SUBJECT_ID_COL, SHIFT_COL]).size().unstack(fill_value=0)

    # (2) precondition checks
    icc = lmm.compute_icc(analysis_data_df, outcome=NOISE_BALANCE_COL, subject_col=SUBJECT_ID_COL)

    # (3) fixed-effects model selection
    best_formula, model_comparison_df = lmm.select_fixed_effects(analysis_data_df, outcome=NOISE_BALANCE_COL,
                                                                 group_col=WORKTYPE_COL, subject_col=SUBJECT_ID_COL,
                                                                 optional_covariates=[WEEKDAY_COL, SHIFT_COL])

    # (4) fit the selected model
    results_df, fig = lmm.fit_lmm(analysis_data_df, formula=best_formula, subject_col=SUBJECT_ID_COL, icc=icc)

    # (5) perform back transform of ILR
    results_df = get_back_transform(results_df, is_ilr=True)

    # show plot
    if show:
        plt.show()

    # save the results and the plot
    if save_path:

        # create folder
        folder_path = Path(save_path) / 'noise'

        # make sure the directory exists
        folder_path.mkdir(parents=True, exist_ok=True)

        # store the plot
        fig.savefig(folder_path / f'noise_diagnostics{FILE_FORMAT}')

        # store the dataframes
        model_comparison_df.to_csv(folder_path / f'noise_model_comparison.csv', index=False)
        results_df.to_csv(folder_path / f'noise_llm_results.csv', index=False)
        shift_counts.to_csv(folder_path / f'shift_counts.csv', index=True)

    # close the figure
    plt.close(fig)


# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #
def _compute_noise_balance_ilr(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare the noise DataFrame for LMM analysis.

    Steps
    -----
    1. Recode structural zeros: NaN in the silencioso distribution column represents a genuinely zero proportion (the
    environment was never below 40 dBA on that day). Recoded to 0 per the analysis plan. After recoding, the
    amalgamated quiet part (silenc + baixo) remains strictly positive in every row, so no further zero-handling is
    needed (Martín-Fernández et al., 2003).

    2. Compute the loud-vs-quiet ILR balance:
         loud  = sum_loud_noise  (incomodativo + elevado, already in data)
         quiet = 1 − loud        (silencioso + baixo after recode)
         b     = (1 / sqrt(2)) * ln(loud / quiet)
       Positive b → more time in loud classes; negative b → more time in
       quiet classes (Egozcue et al., 2003).

    3. Retain only the columns required by the LMM.

    :param df: Raw noise_subject_metrics DataFrame.
    :returns: Tidy DataFrame with columns
        [subject_id, work_type, weekday, b_loud_quiet].

    :reference: Egozcue, J. J., Pawlowsky-Glahn, V., Mateu-Figueras, G., & Barceló-Vidal, C. (2003). Isometric logratio
                transformations for compositional data analysis. *Mathematical Geology*, 35(3), 279–300.
                https://doi.org/10.1023/A:1023818214614
    """
    df = df.copy()

    # Step 1: structural zero recode
    df["Noise_distributions.Silencioso"] = df["Noise_distributions.Silencioso"].fillna(0)

    # Step 2: balance computation
    loud = df["sum_loud_noise"]
    quiet = 1 - loud

    df[NOISE_BALANCE_COL] = (1 / np.sqrt(2)) * np.log(loud / quiet)

    # Step 3: retain only LMM-relevant columns
    return df[[SUBJECT_ID_COL, WORKTYPE_COL, WEEKDAY_COL, SESSION_TIME_COL, NOISE_BALANCE_COL]].copy()





