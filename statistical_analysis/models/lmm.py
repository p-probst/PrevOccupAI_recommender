"""
Implementation of linear mixed models (LMM)
"""
import pandas
# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pandas as pd
import statsmodels.formula.api as smf
import numpy as np
import matplotlib.pyplot as plt

from scipy import stats
from typing import Tuple, Dict, Optional
from matplotlib.pyplot import Figure
from statsmodels.regression.mixed_linear_model import MixedLMResults
from itertools import combinations

from constants import SUBJECT_ID_COL, WEEKDAY_COL

# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
FORMULA_COL = "formula"
RESTRICTED_MODEL_COL = "restricted"

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def compute_icc(df: pd.DataFrame, outcome: str, subject_col: str, vc_formula: Dict[str, str] = None) -> Tuple[float, Optional[float]]:
    """
    Estimate intraclass correlation coefficient(s) from a null (intercept-only) model, supporting both single-level and
    nested random-effects structures.

    For a subject-only random intercept ``(1 | subject_id)``, a single ICC is returned::

        ICC_subject = between_subject_var / (between_subject_var + residual_var)

    quantifying the proportion of total outcome variance attributable to stable between-subject differences; a high
    value (e.g. > 0.3) confirms that within-subject observations are meaningfully correlated and that the random
    intercept is warranted.

    When a nested structure is supplied via ``vc_formula`` (e.g.
    ``(1 | subject_id/day)``), the variance partitions into three components — subject, subject:day, and residual —
    and two conditional ICCs are returned::

        ICC_subject     = sigma2_subject /
                          (sigma2_subject + sigma2_subject_day + sigma2_resid)
        ICC_subject_day = (sigma2_subject + sigma2_subject_day) /
                          (sigma2_subject + sigma2_subject_day + sigma2_resid)

    ``ICC_subject`` is the correlation between two observations from the same subject on different days;
    ``ICC_subject_day`` is the (always larger) correlation between two observations from the same subject on the same
    day.

    Note that ``ICC_subject`` from a nested model is computed against a three-component denominator and is therefore
    not directly comparable to the single-level ``ICC_subject`` returned for a subject-only model.

    The null model is fit with REML, which gives less biased variance-component estimates than ML.

    :param df: Long-format DataFrame. Assumed to contain any grouping column referenced by ``vc_formula``
               (e.g. ``subject_day``).

    :param outcome: Column name of the continuous outcome.
    :param subject_col: Column name of the subject identifier.
    :param vc_formula: Optional variance-component specification for an additional nested random effect, as a single-entry
                       dict mapping a grouping column name to its formula (e.g. ``{"subject_day": "0 + C(subject_day)"}``).
                       Assumes a single variance-component term; only the first is read. If ``None``, only the subject-level
                       random intercept is fit.

    :returns: Tuple ``(icc_subject, icc_subject_day)``, each rounded to 4 decimals. ``icc_subject_day`` is ``None`` when
              no nested structure is supplied.

    .. rubric:: References

    Laird, N. M., & Ware, J. H. (1982). Random-effects models for longitudinal data. *Biometrics*, *38*\\(4), 963–974.
    https://doi.org/10.2307/2529876

    Nakagawa, S., Johnson, P. C. D., & Schielzeth, H. (2017). The coefficient of determination R² and intra-class
    correlation coefficient from generalized linear mixed-effects models revisited and expanded.
    *Journal of the Royal Society Interface*, *14*(134), 20170213. https://doi.org/10.1098/rsif.2017.0213
    """

    # fit null model to estimate between subject variance and residual variance
    formula = f"{outcome} ~ 1"
    null_model = smf.mixedlm(formula=formula, data=df, groups=df[subject_col],
                             re_formula="1", vc_formula=vc_formula)
    null_fit = null_model.fit(reml=True, disp=False)

    # print the model stats
    # print('\n--------')
    # print(f'model {formula}')
    # print(f'cov_re: {null_fit.cov_re}')
    # print(f'scale: {null_fit.scale}')

    # get the corresponding variances
    between_subject_var = float(null_fit.cov_re.iloc[0, 0])
    residual_var = float(null_fit.scale)


    # check whether vc formula was passed
    if vc_formula:

        # get subject_day variance
        subject_day_var = float(null_fit.vcomp[0])

        # get the total (sum of vairances)
        total = between_subject_var + residual_var + subject_day_var

        ## calculate ICC for subject_day
        icc_subject_day = round((between_subject_var + subject_day_var) / total, 4)

    # no vc formula passed
    else:

        total = between_subject_var + residual_var

        # set ICC for subject day to 0
        icc_subject_day = None

    # calculate ICC for the subject
    icc_subject = round(between_subject_var / total, 4)
    return icc_subject, icc_subject_day


def select_fixed_effects(df: pd.DataFrame, outcome: str, group_col: str, subject_col: str,
                         optional_covariates: list[str], vc_formula: Dict[str, str] = None) -> tuple[str, pd.DataFrame]:
    """
    Compare a base model (outcome ~ group) against models that add each
    optional covariate in turn, using maximum-likelihood (ML) fits and Akaike Information Criterion (AIC)/
    Bayesian Information Criterion (BIC). These two are measurements of model quality that balance goodness of fit with
    model complexity. The lower the value for both, the better the model quality.

    Fixed-effect structure must be compared under ML, not REML, because REML likelihoods are not comparable across
    models with different fixed effects (Pinheiro & Bates, 2000, ch. 2).

    The covariate with the lowest AIC is added if it improves the base model; otherwise the base model is returned.
    Covariates are treated as categorical (C() wrapper applied automatically).

    :param df: Long-format DataFrame.
    :param outcome: Column name of the continuous outcome.
    :param group_col: Column name of the primary fixed effect (binary group).
    :param subject_col: Column name of the subject identifier.
    :param optional_covariates: List of column names to evaluate as optional fixed-effect covariates (each tested
                                individually against the base).
    :param vc_formula: formula to add more complex random effects (e.g., (1 | subject_id/weekday)). The dictionary defines
                       the column name and the additional formula (e.g., {"subject_day": "0 + C(subject_day)"}). It is
                       assumed that the df contains the necessary column for modelling.
    :returns: Tuple of (selected_formula_string, comparison_DataFrame).

    :reference: Pinheiro, J. C., & Bates, D. M. (2000). *Mixed-Effects Models
        in S and S-PLUS*. Springer.
    """

    # define formula for the base model: worky_type + (1 | subject_id)
    base_formula = f"{outcome} ~ {group_col}"
    base_fit = smf.mixedlm(formula=base_formula, data=df, groups=df[subject_col],
                           re_formula="1", vc_formula=vc_formula).fit(reml=False, disp=False)

    # store the evaluation criteria
    model_records = [_structure_comparative_lmm_results(base_formula, base_fit)]

    # dict to store the single-layer models
    single_fe_llms = {}

    # cycle over the list of additional covariates
    for cov in optional_covariates:

        # define the formula
        formula = f"{outcome} ~ {group_col} + C({cov})"

        # fit the model
        fit = smf.mixedlm(formula=formula, data=df, groups=df[subject_col],
                          re_formula="1", vc_formula=vc_formula).fit(reml=False, disp=False)

        # perform lrt
        lrt_result = _compute_lrt(base_fit, fit)

        # add the base formula
        lrt_result[RESTRICTED_MODEL_COL] = base_formula

        # append the evaluation criteria
        model_records.append(_structure_comparative_lmm_results(formula, fit, lrt_result))

        # store the model and formula for comparison against double-layered models
        single_fe_llms[cov] = (formula, fit)

        # print the model stats
        # print('\n--------')
        # print(f'model {formula}')
        # print(f'cov_re: {fit.cov_re}')
        # print(f'scale: {fit.scale}')


    # check whether there is more than one covariate
    if len(optional_covariates) > 1:

        # build compound formula
        covariate_terms = " + ".join(f"C({cov})" for cov in optional_covariates)
        compound_formula = f"{outcome} ~ {group_col} + {covariate_terms}"

        # fit the model
        compound_fit = smf.mixedlm(formula=compound_formula, data=df, groups=df[subject_col],
                                   re_formula="1", vc_formula=vc_formula).fit(reml=False, disp=False)

        # print the model stats
        # print('\n--------')
        # print(f'model {compound_formula}')
        # print(f'cov_re: { compound_fit.cov_re}')
        # print(f'scale: { compound_fit.scale}')

        # test compound model against single-layer models
        for cov, (single_fe_formula, single_fe_fit) in single_fe_llms.items():

            # perform lrt
            lrt_result = _compute_lrt(single_fe_fit, compound_fit)

            # add the single fe model formula
            lrt_result[RESTRICTED_MODEL_COL] = single_fe_formula

            # append the evaluation criteria
            model_records.append(_structure_comparative_lmm_results(compound_formula, compound_fit, lrt_result))

    # generate result comparison dataframe
    comparison_df = pd.DataFrame(model_records).sort_values("AIC").reset_index(drop=True)
    best_formula = comparison_df.iloc[0][FORMULA_COL]

    return best_formula, comparison_df


def compare_fixed_effects(df: pd.DataFrame, base_formula: str, subject_col: str,
                          covariate_col: str, vc_formula: Dict[str, str] = None) -> tuple[str, pd.DataFrame]:
    """
    Compares fixed effects for a given outcome and base formula to the passed co-variate. This is a straigfoward
    two model comparison. The models are fitted under ML and then compared to each other.
    :param df: Long-format DataFrame.
    :param base_formula: the base formula as a string.
    Column name of the continuous outcome.
    :param group_col: Column name of the primary fixed effect (binary group).
    :param subject_col: Column name of the subject identifier.
    :param covariate_col: Column name of the additional co-variate to be tested
    :param vc_formula: formula to add more complex random effects (e.g., (1 | subject_id/weekday)). The dictionary defines
                       the column name and the additional formula (e.g., {"subject_day": "0 + C(subject_day)"}). It is
                       assumed that the df contains the necessary column for modelling.
    :return: Tuple of (selected_formula_string, comparison_DataFrame).
    """

    # fit base model
    base_fit = smf.mixedlm(formula=base_formula, data=df, groups=df[subject_col],
                           re_formula="1", vc_formula=vc_formula).fit(reml=False, disp=False)

    # extend base formula and fit extended model
    extended_formula = f"{base_formula} + {covariate_col}"
    extended_fit = smf.mixedlm(formula=extended_formula, data=df, groups=df[subject_col],
                           re_formula="1", vc_formula=vc_formula).fit(reml=False, disp=False)

    # compute LRT
    lrt_result = _compute_lrt(base_fit, extended_fit)

    # structure the outputs
    model_records = [_structure_comparative_lmm_results(base_formula, base_fit), _structure_comparative_lmm_results(extended_formula, extended_fit, lrt_result)]

    # generate result comparison dataframe
    comparison_df = pd.DataFrame(model_records).sort_values("AIC").reset_index(drop=True)
    best_formula = comparison_df.iloc[0][FORMULA_COL]

    return best_formula, comparison_df





def test_interaction(df: pd.DataFrame, comparison_df: pd.DataFrame, best_formula: str, group_col: str,
                     interaction_cov: str, subject_col: str) -> tuple[str, pd.DataFrame]:
    """
    Test whether adding a group x covariate interaction term improves the selected additive model, and append the
    result to the existing model comparison table.

    The interaction model is built by extending the best additive model (as selected by :func:`select_fixed_effects`)
    with an interaction term between ``group_col`` and ``interaction_cov``:

        * additive:    outcome ~ group + C(interaction_cov) [+ other covariates]
        * interaction: additive + group:C(interaction_cov)

    Both models are fit with ML and compared via LRT, since REML likelihoods are not comparable across models with
    different fixed-effect structures (Pinheiro & Bates, 2000, ch. 2). The interaction model is nested in the additive
    model, so the LRT directly tests whether the effect of ``interaction_cov`` differs by ``group_col`` (i.e. effect
    modification), rather than whether ``interaction_cov`` matters at all.

    :param df: Long-format DataFrame.
    :param comparison_df: Model comparison DataFrame as returned by :func:`select_fixed_effects`. The interaction
                          model's row is appended to this table.
    :param best_formula: Selected additive formula string as returned by :func:`select_fixed_effects`
                         (without the random-effects term).
    :param outcome: Column name of the continuous outcome.
    :param group_col: Column name of the primary fixed effect (binary group).
    :param interaction_cov: Column name of the covariate to interact with ``group_col``. Must already be present as a
                            C() term in ``best_formula``.
    :param subject_col: Column name of the subject identifier.
    :returns: ``comparison_df`` with one additional row for the interaction model, including its LRT against the additive model.

    :reference: Pinheiro, J. C., & Bates, D. M. (2000). *Mixed-Effects Models in S and S-PLUS*. Springer.
    """
    # refit the selected additive model with ML, as a basis for the LRT
    additive_fit = smf.mixedlm(formula=best_formula, data=df, groups=df[subject_col]).fit(reml=False, disp=False)

    # extend the additive formula with the group x covariate interaction term
    interaction_formula = f"{best_formula} + {group_col}:C({interaction_cov})"

    # fit the interaction model
    interaction_fit = smf.mixedlm(formula=interaction_formula, data=df, groups=df[subject_col]).fit(reml=False,
                                                                                                    disp=False)

    # perform lrt: interaction model (full) vs additive model (restricted)
    lrt_result = _compute_lrt(additive_fit, interaction_fit)

    # add the restricted model formula
    lrt_result[RESTRICTED_MODEL_COL] = best_formula

    # append the evaluation criteria
    new_row = _structure_comparative_lmm_results(interaction_formula, interaction_fit, lrt_result)

    # append to the existing comparison dataframe and re-sort by AIC
    comparison_df = pd.concat([comparison_df, pd.DataFrame([new_row])], ignore_index=True)
    comparison_df = comparison_df.sort_values("AIC").reset_index(drop=True)

    best_formula = comparison_df.iloc[0][FORMULA_COL]

    # add the grouping to the formula (only doing it here as the formula in python has to be without it)
    # comparison_df[FORMULA_COL] = comparison_df[FORMULA_COL] + f' + (1 | {subject_col})'

    return best_formula, comparison_df


def fit_lmm(df: pd.DataFrame, formula: str, subject_col: str, icc: Tuple[float, float], vc_formula: Dict[str, str] = None) -> Tuple[pd.DataFrame, Figure]:
    """
    Fit the selected linear mixed-effects model with REML.

    REML is used for final inference because it corrects the downward bias that ML introduces in variance-component
    estimates when fixed effects consume degrees of freedom (Pinheiro & Bates, 2000, ch. 2).

    Note: statsmodels MixedLM reports Wald z-statistics rather than t with Satterthwaite degrees of freedom
    (as in R's lmerTest). With 38 subjects this is a slight overstatement of precision and should be noted in reporting.

    :param df: Long-format DataFrame.
    :param formula: Patsy-style formula string (e.g. "b ~ work_type").
    :param subject_col: Column name of the subject identifier.
    :param icc: Inter class correlation coefficient.
    :param vc_formula: formula to add more complex random effects (e.g., (1 | subject_id/weekday)). The dictionary defines
                       the column name and the additional formula (e.g., {"subject_day": "0 + C(subject_day)"}). It is
                       assumed that the df contains the necessary column for modelling.
    :returns: results of the model as a pandas.DataFrame and a figure object displaying the residuals of the model.

    :reference: Pinheiro, J. C., & Bates, D. M. (2000). *Mixed-Effects Models
        in S and S-PLUS*. Springer.
    """

    # define the model
    model = smf.mixedlm(formula=formula, data=df, groups=df[subject_col], re_formula="1", vc_formula=vc_formula)

    # fit the model
    lmm_fit = model.fit(reml=True, disp=False)

    # calculate cohen's d
    cohens_d = _cohens_d_lmm(lmm_fit)

    # plot qq-plot
    fig = _plot_lmm_diagnostics(lmm_fit, formula=formula)

    # collect all results in a single DataFrame
    results_df = _summarise_lmm_results(lmm_fit, icc, cohens_d)

    # print outliers
    _print_outliers(df, lmm_fit, formula)

    return results_df, fig

# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #
def _compute_lrt(fit_restricted: MixedLMResults, fit_full: MixedLMResults) -> dict:
    """
    Likelihood ratio test between two nested ML-fitted LMM models.

    The test statistic is:

        λ = −2 · (llf_restricted − llf_full)

    which under H₀ follows a χ² distribution with degrees of freedom equal to the difference in the number of
    fixed-effect parameters. The variance components (random intercept variance and residual variance) are identical
    across all candidate models in this pipeline and therefore cancel out of the df calculation.

    Both models must have been fitted with ML (reml=False). Passing REML fits produces invalid results because REML
    likelihoods are not comparable across models with different fixed-effect structures (Pinheiro & Bates, 2000, ch. 2).

    :param fit_restricted: ML-fitted MixedLMResults object for the simpler (nested) model.
    :param fit_full: ML-fitted MixedLMResults object for the more complex model. Must contain all terms present in
                     fit_restricted plus at least one additional fixed-effect term.
    :returns: Dictionary with keys lambda_stat (float), df (int), p_value (float).

    :reference: Pinheiro, J. C., & Bates, D. M. (2000). *Mixed-Effects Models
        in S and S-PLUS*. Springer, ch. 2.
    """

    # calculate the statistic
    lambda_stat = 2 * (fit_full.llf - fit_restricted.llf)

    # get the degrees of freedom (number of fixed effect parameters)
    df = len(fit_full.fe_params) - len(fit_restricted.fe_params)

    # apply chi-sqaured distribution
    p_value = stats.chi2.sf(lambda_stat, df)

    return {"lrt_stat": round(lambda_stat, 4),
            "delta_lrt_df": df,
            "lrt_p_value": round(p_value, 4)}


def _cohens_d_lmm(fit) -> float:
    """
    Compute Cohen's d for the primary fixed effect using the total marginal standard deviation as the denominator.

    total_SD = sqrt(between_subject_var + residual_var)
    d = fixed_effect_estimate / total_SD

    The marginal SD is used so that d reflects the effect relative to the full variability in the outcome, making it
    comparable to d values from single-level designs (Nakagawa & Schielzeth, 2013).

    :param fit: Fitted MixedLMResults object. The first non-intercept coefficient is taken as the primary fixed-effect
                estimate.
    :returns: Cohen's d as a float.

    :reference: Nakagawa, S., & Schielzeth, H. (2013). A general and simple
        method for obtaining R² from generalized linear mixed-effects models.
        *Methods in Ecology and Evolution*, 4(2), 133–142.
        https://doi.org/10.1111/j.2041-210x.2012.00261.x
    """

    # First non-intercept coefficient is the group effect
    primary_coef = fit.fe_params.drop("Intercept").iloc[0]

    # calculate total standard deviation
    between_var = float(fit.cov_re.iloc[0, 0])
    residual_var = float(fit.scale)
    total_sd = np.sqrt(between_var + residual_var)

    return round(float(primary_coef) / total_sd, 4)


def _plot_lmm_diagnostics(fit: MixedLMResults, formula: str) -> Figure:
    """
    Produce three diagnostic plots for the fitted LMM:
      1. Residuals vs fitted values — checks homoscedasticity.
      2. Q-Q plot of residuals — checks normality of residuals.
      3. Q-Q plot of BLUPs (random intercepts) — checks normality of
         random effects.

    :param fit: Fitted MixedLMResults object.
    :param formula: Label string used in plot titles.
    :return: figure containing the plots

    :reference: Pinheiro, J. C., & Bates, D. M. (2000). *Mixed-Effects Models
        in S and S-PLUS*. Springer, ch. 4.
    """
    residuals = fit.resid
    fitted = fit.fittedvalues
    random_effects = np.array([effect_value.iloc[0] for effect_value in fit.random_effects.values()])

    fig, axes = plt.subplots(1, 3, figsize=(15, 6))

    # add super title
    fig.suptitle(f"{formula}")

    # 1. Residuals vs fitted
    axes[0].scatter(fitted, residuals, alpha=0.6, edgecolors="k", linewidths=0.4)
    axes[0].axhline(0, color="red", linewidth=1)
    axes[0].set_xlabel("Fitted values")
    axes[0].set_ylabel("Residuals")
    axes[0].set_title("Residuals vs Fitted")

    # 2. Q-Q of residuals
    stats.probplot(residuals, dist="norm", plot=axes[1])
    axes[1].set_title("Q-Q Residuals")

    # 3. Q-Q of BLUPs
    stats.probplot(random_effects, dist="norm", plot=axes[2])
    axes[2].set_title("Q-Q Random Intercepts (BLUPs)")

    plt.tight_layout()

    return fig


def _structure_comparative_lmm_results(formula: str, fit: MixedLMResults, lrt_result: dict = None) -> dict:
    """
    structures the lmm result
    :param formula: the utilised formula
    :param fit: fitted MixedLMResults object
    :param lrt_result: the results from the LRT
    :return: dictionary containing the lmm results
    """
    if lrt_result:
        return {FORMULA_COL: formula, "n_fe_params": len(fit.fe_params), "llf": round(fit.llf, 4),
                "AIC": round(fit.aic, 2), "BIC": round(fit.bic, 2),
                **lrt_result}

    else:
        return {FORMULA_COL: formula, "n_fe_params": len(fit.fe_params), "llf": round(fit.llf, 4),
                "AIC": round(fit.aic, 2), "BIC": round(fit.bic, 2),
                "restricted": "None", "lrt_stat": np.nan, "delta_lrt_df": np.nan, "lrt_p_value": np.nan}


def _summarise_lmm_results(fit: MixedLMResults, icc: Tuple[float, float], d: float) -> pd.DataFrame:
    """
    Collect the key inferential quantities from the fitted model into a
    single tidy DataFrame suitable for reporting.

    Reported quantities per fixed effect:
      - Estimate (regression coefficient)
      - Standard error
      - 95% confidence interval (Wald-based)
      - z-statistic and p-value
    Plus model-level quantities: ICC and Cohen's d for the primary effect.

    :param fit: Fitted MixedLMResults object.
    :param icc: Pre-computed ICC from :func:`compute_icc`.
    :param d: Pre-computed Cohen's d from :func:`cohens_d_lmm`.
    :returns: DataFrame with one row per fixed effect plus summary rows.
    """
    ci = fit.conf_int()
    records = []
    for param in fit.fe_params.index:
        records.append({
            "term": param,
            "estimate": round(fit.fe_params[param], 8),
            "SE": round(fit.bse[param], 4),
            "CI_lower_95": round(ci.loc[param, 0], 4),
            "CI_upper_95": round(ci.loc[param, 1], 4),
            "z": round(fit.tvalues[param], 3),
            "p_value": round(fit.pvalues[param], 4),
        })

    summary = pd.DataFrame(records)

    # Append model-level quantities as separate rows for readability
    meta = pd.DataFrame([{"term": "ICC_subject", "estimate": icc[0]},
                         {"term": "ICC_subject_day", "estimate": icc[1]},
                         {"term": f"Cohen's d (work_type)", "estimate": d}])

    return pd.concat([summary, meta], ignore_index=True)

def _print_outliers(df: pandas.DataFrame, fit: MixedLMResults, formula: str) -> None:
    """
    prints the outliers of the fitted model
    :param df:
    :param fit:
    :param formula:
    :return:
    """

    resid = fit.resid
    z = (resid - resid.mean()) / resid.std()

    # get the outcome variable
    outcome = formula.split("~")[0].strip()

    # align back to df by index, not position
    flagged_idx = z.index[z.abs() > 3]
    outliers = df.loc[flagged_idx, [SUBJECT_ID_COL, WEEKDAY_COL, outcome]].copy()
    outliers["resid"] = resid.loc[flagged_idx]
    outliers["resid_z"] = z.loc[flagged_idx]
    print("\n--Outliers:--")
    print(outliers)