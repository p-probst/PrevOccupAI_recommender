# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pandas as pd
import ptitprince as pt
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.ticker import FuncFormatter
from typing import Tuple, List, Dict


from constants import WORK_TYPES, FO_COLOR, BO_COLOR


# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
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
    pt.RainCloud(x='weekday', y=metric, data=metrics_df, hue='work_type', hue_order=WORK_TYPES, orient='h',
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
    plt.setp(ax.get_yticklabels(), fontsize=fontsize)
    legend = ax.get_legend()
    plt.setp(legend.get_title(), fontsize=fontsize)
    plt.setp(legend.get_texts(), fontsize=fontsize)


    return fig, ax

def stacked_bar_plot(metrics_df: pd.DataFrame, relevant_cols: List[str], metric_class_order: List[str],
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
    :return:
    """

    # generate figure
    fig, ax = plt.subplots(figsize=(14, 8))

    # calculate the mean and convert to percentage
    work_type_mean_df = metrics_df.groupby('weekday', observed=False)[relevant_cols].mean().round(4).mul(100)

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


