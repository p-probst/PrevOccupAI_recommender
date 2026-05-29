# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pandas as pd
import ptitprince as pt
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np

from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.ticker import FuncFormatter
from matplotlib.colors import to_rgb
from typing import Tuple, List, Dict
from pathlib import Path

from constants import WORK_TYPES, FO_COLOR, BO_COLOR, FILE_FORMAT, WORK_TYPE_COLORS, SESSION_NUM_COL, WEEKDAY_COL, WORKTYPE_COL

# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
ROMAN_NUMERALS = {1: "I", 2: "II", 3: "III", 4: "IV"}

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def plot_sensor_metric_by_worktype(metrics_df: pd.DataFrame, metric_column: str, save_path: str | Path, show: bool = True,
                                   x_label: str = None, lower_outlier_limit: int = None, upper_outlier_limit: int = None) -> None:
    """
    generates a raincloud plot that displays the har_metric per day for the FO and BO populations
    :param metrics_df: pandas.DataFrame containing the noise metric data
    :param metric_column: HAR metric to plot
    :param save_path: Path to where the figure will be written.
    :param show: Indicates whether to show the figure.
    :param x_label: Label for the x-axis.
    :param lower_outlier_limit: Lower Outlier limit. Needed to remove recording of the one subject for which the acquisition stopped early on one day.
    :param upper_outlier_limit: upper outlier limit.
    :return: None
    """

    # check for work_type column
    if WORKTYPE_COL not in metrics_df.columns:
        raise KeyError(f"Input CSV must contain a {WORKTYPE_COL} column.")

    # collect the necessary columns
    metric_df = metrics_df[[metric_column, WEEKDAY_COL, WORKTYPE_COL]]

    if lower_outlier_limit:
        # remove outlier from seated data (this one happened due to the phone acquisition time being incorrectly set)
        metric_df = metric_df[metric_df[metric_column] > lower_outlier_limit]

    if upper_outlier_limit:
        metric_df = metric_df[metric_df[metric_column] < upper_outlier_limit]

    # generate plot
    fig, ax = plot_raincloud_by_day(metric_df, metric=metric_column)

    # add label
    if x_label:
        ax.set_xlabel(x_label)

    # transform x-ticks from seconds to hh:mm
    if "duration_sec" in metric_column:
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(seconds_to_hhmm))

    # save plot if necessary
    if save_path is not None:
        file_path = Path(save_path) / f'{metric_column.replace('.', '_')}_by_worktype{FILE_FORMAT}'
        # Make sure the destination directory exists before writing.
        file_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(file_path, dpi=300, bbox_inches='tight')

    if show:
        plt.show()

    # ensure figure is closed
    plt.close(fig)


def plot_raincloud_by_day(metrics_df: pd.DataFrame, metric: str, fontsize: int=12) -> Tuple[Figure, Axes]:
    """
     generates a horizontal rain-cloud plot for each day contained in metrics_df.
    :param metrics_df: pandas.DataFrame containing metrics to plot.
    :param metric: the metric to plot
    :param fontsize: the font size to be utilised for the labels
    :return: Tuple containing the figure and axes.
    """

    # set figure size
    fig, ax = plt.subplots(figsize=(16, 12))

    # generate raincloud plot
    pt.RainCloud(x=WEEKDAY_COL, y=metric, data=metrics_df, hue=WORKTYPE_COL, hue_order=WORK_TYPES, orient='h',
                 palette=[FO_COLOR, BO_COLOR], alpha=0.8, move=0.25, bw=0.2, point_size=4, dodge=True, ax=ax,
                width_box=0.25)


    # Remove spines
    for spine, obj in ax.spines.items():
        if spine != 'bottom':
            obj.set_visible(False)

    # add label and set fontsize
    ax.set_xlabel(metric, fontsize=fontsize + 2)
    ax.set_ylabel("")
    plt.setp(ax.get_xticklabels(), fontsize=fontsize)
    plt.setp(ax.get_yticklabels(), fontsize=fontsize+ 2, rotation=90, va="center")
    legend = ax.get_legend()
    legend.set_title("Tipo de trabalho")
    plt.setp(legend.get_title(), fontsize=fontsize)
    plt.setp(legend.get_texts(), fontsize=fontsize)


    return fig, ax


def plot_stacked_bar_chart(metrics_df: pd.DataFrame, relevant_cols: List[str], metric_class_order: List[str],
                           metric_class_colors: Dict[str, str], legend_patches: List[mpatches.Patch],
                           fontsize: int=12) -> Tuple[Figure, Axes]:
    """
    generates a stacked bar plot to display class percentages of the metrics contained in metrics_df.
    :param metrics_df: pandas.DataFrame containing metrics to plot.
    :param relevant_cols: the columns containing the metric classes to be plotted
    :param metric_class_order: the order of the metric classes to be plotted
    :param metric_class_colors: dict containing the colors used for each class, where the key is the class name, and the value is the color
    :param legend_patches: list of legend patches to be used to display which color belongs to which class
    :param fontsize: the font size to be utilised for the labels
    :return: a tuple containing the figure and axes.
    """

    # generate figure
    fig, ax = plt.subplots(figsize=(14, 8))

    # calculate the mean and convert to percentage
    work_type_mean_df = metrics_df.groupby(WEEKDAY_COL, observed=False)[relevant_cols].mean().round(4).mul(100)

    # ensure correct ordering of the noise classes within the dataframe
    work_type_mean_df = work_type_mean_df[metric_class_order]

    # get the weekdays
    weekdays = work_type_mean_df.index.tolist()
    weekday_pos = list(range(len(weekdays)))

    # init the bar_bottoms
    bar_bottoms = np.zeros(len(weekdays))

    # cycle over the metric classes
    for idx, metric_class in enumerate(metric_class_order):
        # get the values to plot
        values = work_type_mean_df[metric_class].to_numpy()

        # plot the data
        ax.bar(weekday_pos, values, bottom=bar_bottoms, color=metric_class_colors[metric_class], label=metric_class)

        # update the bar bottoms
        bar_bottoms += values

    # add labels to the bars
    _add_percentage_labels(ax, work_type_mean_df.to_numpy())

    # general plot styling
    ax.grid(axis="y", color="lightgray", linestyle="--", linewidth=0.7)
    ax.set_axisbelow(True)

    ax.set_xticks(weekday_pos)
    ax.set_xticklabels(weekdays, rotation=0, ha="center", fontsize=fontsize)
    ax.set_ylabel("Percentagem de Tempo (%)", fontsize=12)
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0f}%"))

    # remove spines
    for spine in ax.spines.values():
        spine.set_visible(False)

    # add legend
    ax.legend(handles=legend_patches, loc="upper center", bbox_to_anchor=(0.5, -0.15),
              ncol=len(metric_class_colors), frameon=False, fontsize=12)

    plt.tight_layout()


    return fig, ax


def plot_session_trajectories_by_worktype(metrics_df:pd.DataFrame, metric_column: str, save_path: str | Path, show: bool = True,
                                          fontsize: int=12, row_height=2.6, sup_y_label: str=None) -> None:
    """
    Generates a subplot of shape (5, 2) containing session trajectories for each day and worktype . The trajectories
    show the evolution of the chosen metric throughout the day (each session). For each subject a thin line is plotted.
    The population mean is shown with a thick line and the standard deviation is plotted as a shaded area.
    :param metrics_df: pandas.DataFrame containing metrics to plot.
    :param metric_column: the metric to be plotted
    :param save_path: Path to where the figure will be written.
    :param show: Indicates whether to show the figure.
    :param fontsize: the fontsize to use for labels and xy-ticks. Optional, default: 12
    :param row_height: the height of each individual figure row. Optional, default: 2.6
    :param sup_y_label: the overall y-label for the figure. Optional, default: None
    :return: None
    """

    # get weekdays
    weekdays = list(metrics_df[WEEKDAY_COL].cat.categories)

    # get number of rows
    n_rows = len(weekdays)

    # generate plot
    fig, axes = plt.subplots(n_rows, 2, figsize=(14, row_height * n_rows), sharex=True, sharey=True)

    # group by work_type and weekday
    grouped_df = metrics_df.groupby([WORKTYPE_COL, WEEKDAY_COL], observed=False)

    # cycle over the weekdays
    for row_idx, weekday in enumerate(weekdays):

        # cycle over the work types
        for col_idx, work_type in enumerate(WORK_TYPES):

            # get corresponding aces
            ax = axes[row_idx, col_idx]

            # get the corresponding grouped DataFrame
            key = (work_type, weekday)
            data_df = grouped_df.get_group(key) if key in grouped_df.groups else pd.DataFrame()

            # plot the data
            _plot_tracjectories(ax, data_df, metric_column, work_type)

            # add grid
            ax.grid(axis="y", linestyle="--", alpha=0.5)
            ax.set_axisbelow(True)

            # remove spines
            for spine in ax.spines.values():
                spine.set_visible(False)

            # Row label on the left, column label on the top row only.
            if col_idx == 0:
                ax.set_ylabel(weekday, fontsize=fontsize + 2, rotation=90, va="center", labelpad=15)
            if row_idx == 0:
                ax.set_title(work_type, fontsize=fontsize + 2, fontweight="bold")
            if row_idx == n_rows - 1:
                ax.set_xlabel("Aquisição", fontsize=fontsize + 2)


    if sup_y_label:
        fig.supylabel(sup_y_label, fontsize=fontsize + 4)
    fig.tight_layout()

    # save plot if necessary
    if save_path is not None:
        file_path = Path(save_path) / f'{metric_column.replace('.', '_')}_by_worktype{FILE_FORMAT}'
        # Make sure the destination directory exists before writing.
        file_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(file_path, dpi=300, bbox_inches='tight')

    if show:
        plt.show()

    # ensure figure is closed
    plt.close(fig)


def seconds_to_hhmm(x, pos):
    """
    converts seconds to hh:mm format. This function is used to format x-tick labels when plotting
    :param x: x-value given as seconds
    :param pos: x-tick position
    :return: the formatted x-tick label
    """
    x = int(x)
    return f"{x //3600:02d}:{(x % 3600) // 60:02d}"


# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #
def _add_percentage_labels(ax: Axes, values: np.ndarray, min_display_percentage: float=2) -> None:
    """
    Adds percentage labels to the stacked bar plot.
    The labels are added to the center of each bar under the condition that the bar has enough height to display the
    label.
    :param ax: matplotlib.axes object containing the stacked bar plot
    :param values: values of all bars, with each row containing the values for a day and each column containing the noise classes.
    :param min_display_percentage: minimum percentage displayed for the bar
    :return: None
    """
    # round values
    display_vals = np.round(values)

    # ensure that the values sum up to 100
    display_vals[:, -1] = 100 - np.sum(display_vals[:, :-1], axis=1)

    # check whether the values fall below the display limit
    display_mask = values >= min_display_percentage

    # cycle over the days
    for day_idx, day_arr in enumerate(values):

        # init bottom position
        bottom_pos = 0

        # cycle over the classes
        for class_idx, value in enumerate(day_arr):

            # check if the value can be displayed
            if display_mask[day_idx, class_idx]:

                # calculate vertical positioning
                y_pos = bottom_pos + value / 2

                # add the label using the rounded values
                ax.text(day_idx, y_pos, f"{int(display_vals[day_idx, class_idx])}%", ha='center', va='center', fontsize=14)

            # update the bottom position
            bottom_pos += value


def _plot_tracjectories(ax: Axes, data_df: pd.DataFrame, metric_column: str, work_type: str, fontsize: int=12) -> None:
    """

    :param ax:
    :param data_df:
    :param metric_column:
    :param color:
    :param work_type:
    :return:
    """

    # check for data
    if data_df.empty:
        ax.set_title(f"{work_type} - sem dados")
        return

    # get the color
    color = WORK_TYPE_COLORS[work_type]

    # get the lighter color shade
    light_color = _lighten(color, amount=0.55)

    # plot line per subject
    for _, subject_df in data_df.groupby("subject_id"):

        # sort the dataFrame by session to ensure correct order
        subject_df = subject_df.sort_values(SESSION_NUM_COL)

        # plot the session data as a line
        ax.plot(subject_df[SESSION_NUM_COL], subject_df[metric_column], color=light_color, alpha=0.5, linewidth=1)

    # calculate mean and std for each session (over all subjects)
    stats = data_df.groupby(SESSION_NUM_COL)[metric_column].agg(["mean", "std", "count"])

    # retrieve values to plot
    x_vals = stats.index.to_numpy()
    mean_vals = stats["mean"].to_numpy()
    std_vals = stats["std"].fillna(0).to_numpy() # ensuring stats returns value in case only one subject is present

    # plot the mean and the stad (as band)
    ax.fill_between(x_vals, mean_vals - std_vals, mean_vals + std_vals, color=color, alpha=0.2, edgecolor="none")
    ax.plot(x_vals, mean_vals, color=color, marker="o", linewidth=2.2, markersize=6, label="Média ± desvio padrão")

    # overwrite x-ticks to only show the sessions
    ax.set_xticks(x_vals)
    ax.set_xticklabels([ROMAN_NUMERALS.get(x_val, str(x_val)) for x_val in x_vals])
    plt.setp(ax.get_xticklabels(), fontsize=fontsize)
    plt.setp(ax.get_yticklabels(), fontsize=fontsize)


def _lighten(hex_color: str, amount: float = 0.55) -> tuple:
    """
    Return a lighter shade of ``hex_color`` by blending it toward white.

    :param hex_color: Hex color string, e.g. ``"#4d92d0"``.
    :param amount: Blend factor in ``[0, 1]``. ``0`` returns the original color;
        ``1`` returns pure white. Defaults to ``0.55``.
    :return: An RGB tuple suitable for matplotlib.
    """
    r, g, b = to_rgb(hex_color)
    return (r + (1 - r) * amount,
            g + (1 - g) * amount,
            b + (1 - b) * amount)


