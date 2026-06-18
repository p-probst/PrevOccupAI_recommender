"""
implementation of generalized estimating equations
"""

# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from typing import Tuple
from matplotlib.pyplot import Figure
from statsmodels.genmod.generalized_estimating_equations import GEE, GEEResults
from statsmodels.genmod.families import Poisson
from statsmodels.genmod.cov_struct import Exchangeable



# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #



# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def fit_poisson_gee(df: pd.DataFrame, outcome: str, group_col: str, subject_col: str, offset_col: str = None) -> Tuple[pd.DataFrame, Figure]:
    """
    fit a poisson generalized estimating equation (GEE) model with an offset.
    The poisson-based model is used for:
    * count variables (discrete, non-negative integers)
    * variables whose distribution is often right-skewed
    * variables where the variance typically increases with the mean
    * modelling events that occur over a given exposure time

    The offset allows for modelling the event rate (e.g., steps per unit time) while retaining the count nature of the
    data. The model assumes an exchangeable correlation structure (every measure is equally correlated to each other).
    This structure was chosen as the time frame of the recording (five consecutive days) should not have too much of
    an effect on the outcome. Example: the step count is most likely not higher correlated for consecutive days.

    Usage example:
    A GEE estimates the population-average (marginal) effect of work_type on the step rate, with robust (sandwich)
    standard errors that remain valid under within-subject correlation and under violations of the Poisson mean=variance
    assumption (Liang & Zeger, 1986). Validity relies on the missingness being MCAR, as established for the dropped
    short-recording days.


    These are properties that
    :param df: Long-format DataFrame.
    :param outcome: Column name of the outcome to be tested.
    :param group_col: Column name of the primary fixed effect (binary group).
    :param subject_col: Column name of the subject identifier.
    :param offset_col: Column name of the offset identifier. Default: None
    :return:

    :reference: Liang, K.-Y., & Zeger, S. L. (1986). Longitudinal data analysis using generalized linear models.
                Biometrika, 73(1), 13-22. https://doi.org/10.1093/biomet/73.1.13
    """

    # build formula
    formula = f'Q("{outcome}") ~ {group_col}'

    # define the model
    model = GEE.from_formula(formula, data=df, groups=df[subject_col], offset=offset_col,
                             family=Poisson(), cov_struct=Exchangeable())

    # fit the model
    gee_fit = model.fit()

    # calculate residuals and dispersion
    residuals, dispersion = _calc_residuals(df, gee_fit, outcome)

    # plot the residuals
    fig = _plot_gee_diagnostics(gee_fit, pearson_resid=residuals, formula=formula, offset_col=offset_col)

    # collect all results in a single DataFrame
    results_df = _summarise_gee_results(gee_fit, dispersion)

    return results_df, fig


# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #
def _calc_residuals(df: pd.DataFrame, fit: GEEResults, outcome: str) -> Tuple[np.ndarray, float]:
     """
     Calculates the pearson residuals and the dispersion statistic of the model.

     The Pearson dispersion statistic is:

         dispersion = sum(((y - mu) / sqrt(mu))^2) / (n - p)

     where mu are the fitted values and p the number of fixed-effect parameters. A value >> 1 indicates that the Poisson
     mean = variance assumption is violated. This does NOT invalidate GEE inference under robust (sandwich) standard
     errors, which are valid under arbitrary overdispersion (Liang & Zeger, 1986); it is reported as a descriptive
     diagnostic only, not as a trigger for switching families.
     :param df: Long-format DataFrame.
     :param fit: fitted GEEResult object.
     param outcome: the outcome variable (column name of pandas.DataFrame).
     :return:

     :reference: Liang, K.-Y., & Zeger, S. L. (1986). Longitudinal data analysis using generalized linear models.
                 Biometrika, 73(1), 13-22. https://doi.org/10.1093/biomet/73.1.13
     :reference: Hardin, J. W., & Hilbe, J. M. (2012). Generalized Estimating Equations (2nd ed.). Chapman & Hall/CRC.
     """

     # get coefficients
     mu = fit.fittedvalues
     y = df[outcome].to_numpy()

     # calculate residuals and dispersion
     pearson_resid = (y - mu) / np.sqrt(mu)

     n_params = len(fit.params)
     dispersion = float(np.sum(pearson_resid ** 2) / (len(y) - n_params))

     return pearson_resid, dispersion


def _plot_gee_diagnostics(fit: GEEResults, pearson_resid: np.ndarray, formula: str, offset_col: str = None) -> Figure:
     """
     residuals vs. fitted values plot for GEE.
     :param fit: fitted GEEResult object.
     :param pearson_resid: the pearson residuals of the GEE model as obtained by :function _calc_residuals.
     :param formula: Patsy-style formula string (e.g. "b ~ work_type").
     :return: figure containing the plot.
     """

     # get the mean values
     mu = fit.fittedvalues


     fig, ax = plt.subplots(figsize=(6, 5))
     ax.scatter(mu, pearson_resid, alpha=0.6, edgecolors="k", linewidths=0.4)
     ax.axhline(0, color="red", linewidth=1)
     ax.set_xlabel("Fitted values")
     ax.set_ylabel("Pearson residuals")
     ax.set_title(f"Residuals vs Fitted: Fromula: {formula}, Offset: {offset_col})")

     plt.tight_layout()

     return fig


def _summarise_gee_results(fit: GEEResults, dispersion: float) -> pd.DataFrame:
    """
    Collect the key inferential quantities from the fitted GEE into a
    tidy DataFrame.

    Reported per fixed-effect term:
      - estimate (coefficient on the log scale)
      - robust standard error
      - 95% Wald confidence interval (log scale)
      - z-statistic and p-value
      - incidence rate ratio (IRR = exp(estimate)) and its 95% CI

    The Pearson dispersion statistic is appended as a model-level summary
    row.

    :param fit: Fitted GEEResults object.
    :param dispersion: Pearson dispersion statistic from
        :func:`_gee_diagnostics`.
    :returns: DataFrame with one row per fixed-effect term plus a
        dispersion summary row.

    :reference: Liang, K.-Y., & Zeger, S. L. (1986). Longitudinal data
        analysis using generalized linear models. Biometrika, 73(1),
        13-22. https://doi.org/10.1093/biomet/73.1.13
    """
    ci = fit.conf_int()

    records = []
    for term in fit.params.index:
        records.append({
            "term": term,
            "estimate": round(fit.params[term], 4),
            "robust_SE": round(fit.bse[term], 4),
            "CI_lower_95": round(ci.loc[term, 0], 4),
            "CI_upper_95": round(ci.loc[term, 1], 4),
            "z": round(fit.tvalues[term], 3),
            "p_value": round(fit.pvalues[term], 4),
            "IRR": round(np.exp(fit.params[term]), 4),
            "IRR_CI_lower_95": round(np.exp(ci.loc[term, 0]), 4),
            "IRR_CI_upper_95": round(np.exp(ci.loc[term, 1]), 4),
        })

    summary = pd.DataFrame(records)

    meta = pd.DataFrame([{"term": "Pearson dispersion", "estimate": round(dispersion, 4)}])

    return pd.concat([summary, meta], ignore_index=True)