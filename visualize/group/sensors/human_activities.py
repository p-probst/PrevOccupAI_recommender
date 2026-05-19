# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pandas as pd
from pathlib import Path
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from .plot_utils import plot_raincloud_by_day, seconds_to_hhmm, stacked_bar_plot
from constants import BLUE_STATE, PALE_GREEN, SALMON, FILE_FORMAT
# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
WALKING_KEY = 'Andar'
STANDING_KEY = 'De pé'
SITTING_KEY = 'Sentado'

ACTIVITY_CLASS_ORDER = [WALKING_KEY, STANDING_KEY, SITTING_KEY]

ACTIVITY_CLASS_COLORS = {WALKING_KEY: BLUE_STATE,
                         STANDING_KEY: SALMON,
                         SITTING_KEY: PALE_GREEN}

LEGEND_PATCHES = [
            mpatches.Patch(color=ACTIVITY_CLASS_COLORS[WALKING_KEY], label=WALKING_KEY),
            mpatches.Patch(color=ACTIVITY_CLASS_COLORS[STANDING_KEY], label=STANDING_KEY),
            mpatches.Patch(color=ACTIVITY_CLASS_COLORS[SITTING_KEY], label=SITTING_KEY)
        ]
# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def plot_activity_distributuions_by_worktype(metrics_df: pd.DataFrame, save_path: str | Path, show: bool=True) -> None:
    """
    generates group-wise plots for showing the mean distribution of all activity distribution metrics per day
    :param metrics_df: pandas.DataFrame containing the noise metric data
    :param save_path: Path to where the figure will be written.
    :param show: Indicates whether to show the figure.
    :return: None
    """

    # check for work_type column
    if "work_type" not in metrics_df.columns:
        raise KeyError("Input CSV must contain a 'work_type' column.")

    # get relevant columns indices
    relevant_col_idx = [num for num, col in enumerate(metrics_df.columns) if col.startswith("HAR_distributions")]

    # clean the column names
    metrics_df.columns = [col.split(".")[1] if col.startswith('HAR_distributions') else col for col in
                          metrics_df.columns]

    # get the relevant cols
    relevant_cols = [metrics_df.columns[idx] for idx in relevant_col_idx]

    # cycle over the work_type
    for work_type, group_df in metrics_df.groupby('work_type', sort=False, observed=False):

        # generate figure
        fig, ax = stacked_bar_plot(group_df, relevant_cols, ACTIVITY_CLASS_ORDER, ACTIVITY_CLASS_COLORS, LEGEND_PATCHES)

        # save plot if necessary
        if save_path is not None:
            file_path = Path(save_path) / f'har_distributions_{work_type}{FILE_FORMAT}'
            # Make sure the destination directory exists before writing.
            file_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(file_path)

        if show:
            plt.show()

        # ensure figure is closed
        plt.close(fig)


def plot_har_metric_by_worktype(metrics_df: pd.DataFrame, har_metric_column: str, save_path: str | Path, show: bool=True,
                                x_label: str = None, outlier_limit: int = 0) -> None:
    """
    generates a raincloud plot that displays the har_metric per day for the FO and BO populations
    :param metrics_df: pandas.DataFrame containing the noise metric data
    :param har_metric_column: HAR metric to plot
    :param save_path: Path to where the figure will be written.
    :param show: Indicates whether to show the figure.
    :param x_label: Label for the x-axis.
    :param outlier_limit: Outlier limit. Needed to remove recording of the one subject for which the acquisition stopped early on one day.
    :return: None
    """

    # check for work_type column
    if "work_type" not in metrics_df.columns:
        raise KeyError("Input CSV must contain a 'work_type' column.")

    # split har metric into dimension and metric
    dimension, metric = har_metric_column.split(".")

    # clean the column names
    metrics_df.columns = [col.split(".")[1] if col.startswith(dimension) else col for col in
                          metrics_df.columns]

    # collect the necessary columns
    metric_df = metrics_df[[metric, 'weekday', 'work_type']]

    # remove outlier from seated data (this one happened due to the phone acquisition time being incorrectly set)
    metric_df = metric_df[metric_df[metric] > outlier_limit]

    fig, ax = plot_raincloud_by_day(metric_df, metric=metric)

    # add label
    if x_label:
        ax.set_xlabel(x_label)

    # transform x-ticks from seconds to hh:mm
    if "duration_sec" in metric:
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(seconds_to_hhmm))

    # save plot if necessary
    if save_path is not None:
        file_path = Path(save_path) / f'HAR_{metric}_by_worktype{FILE_FORMAT}'
        # Make sure the destination directory exists before writing.
        file_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(file_path)

    if show:
        plt.show()

    # ensure figure is closed
    plt.close(fig)

# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #