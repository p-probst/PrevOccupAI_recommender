# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #


# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def check_normality_by_group(df: pd.DataFrame, outcome: str, group_col: str) -> pd.DataFrame:
    """
    Run a Shapiro-Wilk test on the outcome separately for each group level and produce one Q-Q plot per group.

    The result is informational: the LMM is reasonably robust to mild non-normality of the outcome, but severe skew or
    multimodality should be noted.

    :param df: Long-format DataFrame.
    :param outcome: Column name of the continuous outcome.
    :param group_col: Column name of the grouping variable (e.g. work_type).
    :returns: DataFrame with columns [group, n, W_stat, p_value, normal_0.05].

    :reference: Shapiro, S. S., & Wilk, M. B. (1965). An analysis of variance
        test for normality (complete samples). *Biometrika*, 52(3–4), 591–611.
        https://doi.org/10.1093/biomet/52.3-4.591
    """

    # init list to hold the results
    stats_results = []

    # get the groups
    groups = df[group_col].unique()
    n_groups = len(groups)

    # generate figure # TODO: this potentially should be extended to work for each day
    fig, axes = plt.subplots(1, n_groups, figsize=(5 * n_groups, 4))

    # cycle over the axes
    for ax, group in zip(axes, sorted(groups)):

        # get the group data that belongs to the outcome (variable) that should be analysed
        values = df.loc[df[group_col] == group, outcome].dropna().values

        # perform normality test (shapiro-wilk)
        stat, p = stats.shapiro(values)

        # collect results in format that is transferable to a pandas.DataFrame
        stats_results.append({"group": group, "num_vals": len(values),
                              "W_stat": round(stat, 4), "p_value": round(p, 4),
                              "normal_0.05": p >= 0.05})

        # Q-Q plot
        stats.probplot(values, dist="norm", plot=ax)
        ax.set_title(f"Q-Q: {group}  (W={stat:.3f}, p={p:.3f})")

    plt.tight_layout()
    plt.show()

    return pd.DataFrame(stats_results)
# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #
