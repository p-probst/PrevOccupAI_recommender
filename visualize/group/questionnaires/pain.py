# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
from pathlib import Path
from typing import List, Dict

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

# internal imports
from constants import BO_COLOR, FO_COLOR, EDGE_COLOR, WORK_TYPES, VIABLE_PAIN_DIMENSIONS, FILE_FORMAT, WORKTYPE_COL, \
    SUBJECT_ID_COL

# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
PAIN_LEVELS = ["leve", "moderada", "severa"]
DURATION_LEVELS = ["aguda", "crónica"]
LEVEL_COLORS = {
    "leve": "#FFDEAD",      # light yellow  -> mild
    "moderada": "#FFCC80FF",  # orange        -> moderate
    "aguda": "#FFCC80FF",
    "severa": "#EF9A9AFF",
    "crónica": "#EF9A9AFF"# red           -> severe
}


# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def plot_pain_localization_perception_by_work_type(metrics_df: pd.DataFrame, q_type: str, save_path: str | Path = None, show: bool = False,
                                                   fontsize: int=12) -> None:
    """
    Plots a grouped bar chart of the questionnaire_type, grouped by work type. The following questionnaires are
    supported:
    * localização
    * perceção

    :param metrics_df: pandas.DataFrame containing pain location data
    :param save_path: Path to where the figure will be written.
    :param q_type: Type of questionnaire.
    :param show: Indicates whether to show the figure.
    :param fontsize: Font size for labels
    :returns: None
    """

    # get the correct pain dimensions
    pain_dimensions = [VIABLE_PAIN_DIMENSIONS[idx] for idx in [0, -1]]

    # check for correct questionnaires
    if q_type not in pain_dimensions:
        raise ValueError(f"q_type must be either {pain_dimensions}. Provided value: {q_type}")

    # check for work_type column
    if WORKTYPE_COL not in metrics_df.columns:
        raise KeyError(f"Input CSV must contain a {WORKTYPE_COL} column.")

    if q_type == "localização":
        num_workers_pain = _get_num_workers_with_pain(metrics_df)

        print(f"Number of workers pain: {num_workers_pain}")

    # filter out columns that are not body regions
    relevant_cols = [c for c in metrics_df.columns if c not in (SUBJECT_ID_COL, WORKTYPE_COL)]

    # Count number of 'Y' entries for each column and work_type
    counts = (metrics_df.groupby(WORKTYPE_COL)[relevant_cols].apply(lambda g: g.eq("Y").sum()))

    # transpose counts to have work_type as columns and body region counts as rows
    # ensure the order FO, BO
    counts = counts.T[WORK_TYPES]

    # define plot and generate plot
    fig, ax = plt.subplots(figsize=(12, 6))

    counts.plot.bar(ax=ax, color=[FO_COLOR, BO_COLOR], edgecolor=EDGE_COLOR, width=0.8)
    sns.despine(left=True, ax=ax)

    ax.set_xlabel(f"{q_type.capitalize()} de dor", fontsize=fontsize+2)
    ax.set_ylabel("Número de trabalhadores", fontsize=fontsize+2)
    legend = ax.legend(title="Tipo de trabalho",fontsize=fontsize)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)  # gridlines behind the bars

    # Rotate region labels so the (long, Portuguese) names remain readable.
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize=fontsize)
    plt.setp(ax.get_yticklabels(), fontsize=fontsize)
    plt.setp(legend.get_title(), fontsize=fontsize)

    # Annotate each bar with its integer height for quick reading.
    for container in ax.containers:
        ax.bar_label(container, padding=2, fontsize=fontsize)

    fig.tight_layout()

    # save plot if necessary
    if save_path is not None:
        save_path = Path(save_path) / f'{q_type}_by_work_type{FILE_FORMAT}'
        # Make sure the destination directory exists before writing.
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches='tight')

    if show:
        plt.show()

    # ensure figure is closed
    plt.close(fig)


def plot_pain_levels_by_work_type(metrics_df: pd.DataFrame, q_type: str, eval_levels: List[str], save_path: str |Path = None,
                                   show: bool = False, fontsize: int=12) -> None:
    """
    Plot pain levels by work type as a stacked bar plot. The following questionnaires are supported:
    * incapacidade
    * intensidade
    * sofriemento
    * tempo

    :param metrics_df: pandas.DataFrame containing pain location data
    :param q_type: Type of questionnaire.
    :param eval_levels: List of evaluation levels.
    :param save_path: Path to where the figure will be written.
    :param show: Indicates whether to show the figure.
    :param fontsize: Font size for labels
    :returns: None
    """

    # get the correct pain dimensions
    pain_dimensions = VIABLE_PAIN_DIMENSIONS[1:5]

    # check for valid q_type
    if q_type not in pain_dimensions:
        raise ValueError(f"q_type must be either {pain_dimensions}. Provided value: {q_type}")

    # check for work_type column
    if WORKTYPE_COL not in metrics_df.columns:
        raise KeyError(f"Input CSV must contain a {WORKTYPE_COL} column.")

    # Body-region columns = everything except the identifier and the grouping column.
    region_cols = [c for c in metrics_df.columns if c not in (SUBJECT_ID_COL, WORKTYPE_COL)]

    # count pain level occurrences
    pain_level_counts_dict = _create_pain_level_counts_dict(metrics_df, region_cols, eval_levels)

    # get number of body regions and work_types
    n_regions = len(region_cols)
    n_groups = len(WORK_TYPES)

    x = np.arange(n_regions)  # one tick centre per region
    total_group_width = 0.8  # fraction of the slot occupied by all bars
    bar_width = total_group_width / n_groups

    fig, ax = plt.subplots(figsize=(14, 7))

    # Draw one stacked bar per (region, work_type) combination.
    for i, work_type in enumerate(WORK_TYPES):
        # Horizontal offset of this work_type's bars within each region slot.
        # Centred around 0 so the whole group is symmetric about the tick.
        offset = (i - (n_groups - 1) / 2) * bar_width
        bar_positions = x + offset

        # Stack severity segments from bottom (mild) to top (severe).
        bottoms = np.zeros(n_regions)

        # cycle over the pain levels
        for severity in eval_levels:

            # collect all bar heights in one array
            heights = np.array([pain_level_counts_dict[(work_type, region)][severity] for region in region_cols])

            # Show the severity in the legend only once (on the first work_type
            # pass) to avoid duplicate legend entries.
            label = severity if i == 0 else None

            ax.bar(bar_positions, heights, width=bar_width, bottom=bottoms, color=LEVEL_COLORS[severity],
                   edgecolor=EDGE_COLOR, linewidth=0.5, label=label)

            # update the bottom of the bar
            bottoms = bottoms + heights

        # Annotate each stacked bar with its work_type label, just above the
        # top of the stack, so the reader can tell BO from FO at a glance
        # without relying purely on position.
        for xp, total in zip(bar_positions, bottoms):
            if total > 0:
                ax.text(xp, total + 0.15, work_type,
                        ha="center", va="bottom", fontsize=fontsize, color=EDGE_COLOR)

    # set ticks, labels, and titles
    sns.despine(left=True, ax=ax)
    ax.set_xticks(x)
    ax.set_xticklabels(region_cols, rotation=30, ha="right", fontsize=fontsize)
    ax.set_xlabel("Localização de dor", fontsize=fontsize + 2)
    ax.set_ylabel("Número de trabalhadores", fontsize=fontsize + 2)

    plt.setp(ax.get_yticklabels(), fontsize=fontsize)


    legend = ax.legend(title="Nível", loc="upper right", fontsize=fontsize)
    plt.setp(legend.get_title(), fontsize=fontsize)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)  # gridlines behind the bars

    # Give the bar labels a bit of vertical headroom.
    y_max = ax.get_ylim()[1]
    ax.set_ylim(0, y_max * 1.08)

    fig.tight_layout()

    # --- Save and/or show --------------------------------------------------------
    if save_path is not None:
        save_path = Path(save_path) / f'{q_type}_by_work_type{FILE_FORMAT}'
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches='tight')

    if show:
        plt.show()

    # ensure figure is closed
    plt.close(fig)

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def _get_num_workers_with_pain(metrics_df: pd.DataFrame) -> Dict[str, int]:
    """
    Gets the count of workers that reported pain for FO and BO
    :param metrics_df:  pandas.DataFrame containing pain level data.
    :return: dictionary with the FO and BO count of workers that reported pain
    """

    # filter out columns that are not body regions
    relevant_cols = [c for c in metrics_df.columns if c not in (SUBJECT_ID_COL, WORKTYPE_COL)]

    # get columns with at leat one "Y" response
    has_pain = metrics_df[relevant_cols].eq("Y").any(axis=1)

    # tuple to hold the result
    num_workers_pain = {}

    for work_type in metrics_df[WORKTYPE_COL].unique():

        num_workers_pain[work_type] = len(metrics_df.loc[has_pain & (metrics_df[WORKTYPE_COL] == work_type), SUBJECT_ID_COL].unique())

    return num_workers_pain


def _create_pain_level_counts_dict(metrics_df: pd.DataFrame, region_cols: List[str], eval_levels: List[str]) -> dict:
    """
    creates a dictionary that hold the counts of the pain levels. The pain levels as stored as a pandas.Series object.
    :param metrics_df: pandas.DataFrame containing pain level data.
    :param region_cols: List of column names corresponding to the body regions at which the pain was evaluated.
    :param eval_levels: List of evaluation levels.
    :return: Dictionary containing pain level counts. The dictionary key is a Tuple consisting of the work_type and the
             body region. Example entry:
             {('BO','cervical/pescoço'):
             cervical/pescoço
                leve        4
                moderada    1
                severa      1
                Name: count, dtype: int64,...}
    """

    # dict to hold the result
    counts = {}

    # cycle over FO and BO
    for worky_type in WORK_TYPES:

        # obtain dataframe containing only the values for the work type
        sub = metrics_df[metrics_df[WORKTYPE_COL] == worky_type]

        # cycle over the columns
        for region in region_cols:
            # count the occurrences of each pain level
            # reindex(SEVERITY_ORDER, ...) ensures that when a level does not appear it is set to zero
            counts[(worky_type, region)] = (sub[region].value_counts().reindex(eval_levels, fill_value=0))

    return counts