# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pandas as pd
import statsmodels.formula.api as smf
import numpy as np
import matplotlib.pyplot as plt

from scipy import stats
from typing import Tuple
from matplotlib.pyplot import Figure
from statsmodels.regression.mixed_linear_model import MixedLMResults



# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def compute_icc(df: pd.DataFrame, outcome: str, subject_col: str) -> float:
    """
    Estimate the intraclass correlation coefficient (ICC) from a null
    (intercept-only) random-intercept model.

    ICC = between_subject_var / (between_subject_var + residual_var)

    Quantifies what proportion of total outcome variance is attributable to
    stable between-subject differences. A high ICC (e.g. > 0.3) confirms
    that observations within the same subject are meaningfully correlated and
    that the random intercept is essential, i.e., usage of (1 | subject_id).

    :param df: Long-format DataFrame.
    :param outcome: Column name of the continuous outcome.
    :param subject_col: Column name of the subject identifier.
    :returns: ICC as a float in [0, 1].

    :reference: Laird, N. M., & Ware, J. H. (1982). Random-effects models for longitudinal data.
                *Biometrics*, 38(4), 963–974. https://doi.org/10.2307/2529876
    """

    # fit null model to estimate between subject variance and residual variance
    null_model = smf.mixedlm(formula=f"{outcome} ~ 1", data=df, groups=df[subject_col])
    null_fit = null_model.fit(reml=True, disp=False)

    # get the corresponding variances
    between_subject_var = float(null_fit.cov_re.iloc[0, 0])
    residual_var = float(null_fit.scale)
    icc = between_subject_var / (between_subject_var + residual_var)
    return round(icc, 4)


def select_fixed_effects(df: pd.DataFrame, outcome: str, group_col: str, subject_col: str,
                         optional_covariates: list[str]) -> tuple[str, pd.DataFrame]:
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
    :returns: Tuple of (selected_formula_string, comparison_DataFrame).

    :reference: Pinheiro, J. C., & Bates, D. M. (2000). *Mixed-Effects Models
        in S and S-PLUS*. Springer.
    """

    # define formula for the base model: worky_type + (1 | subject_id)
    base_formula = f"{outcome} ~ {group_col}"
    base_fit = smf.mixedlm(formula=base_formula, data=df, groups=df[subject_col]).fit(reml=False, disp=False)

    # store the evaluation criteria
    model_records = [_structure_comparative_lmm_results(base_formula, base_fit)]

    # dict to store the single-layer models
    single_fe_llms = {}

    # cycle over the list of additional covariates
    for cov in optional_covariates:

        # define the formula
        formula = f"{outcome} ~ {group_col} + C({cov})"

        # fit the model
        fit = smf.mixedlm(formula=formula, data=df, groups=df[subject_col]).fit(reml=False, disp=False)

        # perform lrt
        lrt_result = _compute_lrt(base_fit, fit)

        # add the base formula
        lrt_result['restricted'] = base_formula

        # append the evaluation criteria
        model_records.append(_structure_comparative_lmm_results(formula, fit, lrt_result))

        # store the model and formula for comparison against double-layered models
        single_fe_llms[cov] = (formula, fit)


    # check whether there is more than one covariate
    if len(optional_covariates) > 1:

        # build compound formula
        covariate_terms = " + ".join(f"C({cov})" for cov in optional_covariates)
        compound_formula = f"{outcome} ~ {group_col} + {covariate_terms}"

        # fit the model
        compound_fit = smf.mixedlm(formula=compound_formula, data=df, groups=df[subject_col]).fit(reml=False, disp=False)

        # test compound model against single-layer models
        for cov, (single_fe_formula, single_fe_fit) in single_fe_llms.items():

            # perfrom lrt
            lrt_result = _compute_lrt(single_fe_fit, compound_fit)

            # add the single fe model formula
            lrt_result['restricted'] = single_fe_formula

            # append the evaluation criteria
            model_records.append(_structure_comparative_lmm_results(compound_formula, compound_fit, lrt_result))


    # generate result comparison dataframe
    comparison_df = pd.DataFrame(model_records).sort_values("AIC").reset_index(drop=True)
    best_formula = comparison_df.iloc[0]["formula"]

    return best_formula, comparison_df


def fit_lmm(df: pd.DataFrame, formula: str, subject_col: str, icc: float) -> Tuple[pd.DataFrame, Figure]:
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
    :returns: Fitted MixedLMResults object.

    :reference: Pinheiro, J. C., & Bates, D. M. (2000). *Mixed-Effects Models
        in S and S-PLUS*. Springer.
    """

    # define the model
    model = smf.mixedlm(formula=formula, data=df, groups=df[subject_col])

    # fit the model
    lmm_fit = model.fit(reml=True, disp=False)

    # calculate cohen's d
    cohens_d = _cohens_d_lmm(lmm_fit)

    # plot qq-plot
    fig = _plot_lmm_diagnostics(lmm_fit, formula=formula)

    # collect all results in a single DataFrame
    results_df = _summarise_lmm_results(lmm_fit, icc, cohens_d)

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

    :reference: Pinheiro, J. C., & Bates, D. M. (2000). *Mixed-Effects Models
        in S and S-PLUS*. Springer, ch. 4.
    """
    residuals = fit.resid
    fitted = fit.fittedvalues
    random_effects = np.array([v[0] for v in fit.random_effects.values()])

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

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
        return {"formula": formula, "n_fe_params": len(fit.fe_params), "llf": round(fit.llf, 4),
                "AIC": round(fit.aic, 2), "BIC": round(fit.bic, 2),
                **lrt_result}

    else:
        return {"formula": formula, "n_fe_params": len(fit.fe_params), "llf": round(fit.llf, 4),
                "AIC": round(fit.aic, 2), "BIC": round(fit.bic, 2),
                "restricted": "None", "lrt_stat": np.nan, "delta_lrt_df": np.nan, "lrt_p_value": np.nan}


def _summarise_lmm_results(fit: MixedLMResults, icc: float, d: float) -> pd.DataFrame:
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
            "estimate": round(fit.fe_params[param], 4),
            "SE": round(fit.bse[param], 4),
            "CI_lower_95": round(ci.loc[param, 0], 4),
            "CI_upper_95": round(ci.loc[param, 1], 4),
            "z": round(fit.tvalues[param], 3),
            "p_value": round(fit.pvalues[param], 4),
        })

    summary = pd.DataFrame(records)

    # Append model-level quantities as separate rows for readability
    meta = pd.DataFrame([
        {"term": "ICC", "estimate": icc,
         "SE": None, "CI_lower_95": None, "CI_upper_95": None,
         "z": None, "p_value": None},
        {"term": f"Cohen's d (work_type)", "estimate": d,
         "SE": None, "CI_lower_95": None, "CI_upper_95": None,
         "z": None, "p_value": None},
    ])

    return pd.concat([summary, meta], ignore_index=True)