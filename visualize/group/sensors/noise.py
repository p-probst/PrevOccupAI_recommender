# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import matplotlib.ticker as mticker

from pathlib import Path
from matplotlib.axes import Axes
from matplotlib.ticker import FuncFormatter

from constants import STRONG_GREEN, PALE_GREEN, YELLOW, RED, FILE_FORMAT
from .raincloud_plot_utils import plot_raincloud_by_day

# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
NOISE_NEAR_SILENCE_KEY = 'Silencioso'
NOISE_LOW_KEY = 'Ruído baixo'
NOISE_DISTURBING_KEY = 'Ruído incomodativo'
NOISE_HIGH_KEY = 'Ruído elevado'
NOISE_CLASS_ORDER = [NOISE_NEAR_SILENCE_KEY, NOISE_LOW_KEY, NOISE_DISTURBING_KEY, NOISE_HIGH_KEY]

CLASS_COLORS = {NOISE_NEAR_SILENCE_KEY: STRONG_GREEN,
                NOISE_LOW_KEY: PALE_GREEN,
                NOISE_DISTURBING_KEY: YELLOW,
                NOISE_HIGH_KEY: RED
                }

LEGEND_PATCHES = [
            mpatches.Patch(color=CLASS_COLORS[NOISE_NEAR_SILENCE_KEY], label=f"{NOISE_NEAR_SILENCE_KEY}  ≤ 40 dBA"),
            mpatches.Patch(color=CLASS_COLORS[NOISE_LOW_KEY], label=f"{NOISE_LOW_KEY} 40–60 dBA"),
            mpatches.Patch(color=CLASS_COLORS[NOISE_DISTURBING_KEY], label=f"{NOISE_DISTURBING_KEY} 60–80 dBA"),
            mpatches.Patch(color=CLASS_COLORS[NOISE_HIGH_KEY], label=f"{NOISE_HIGH_KEY} ≥ 80 dBA")
        ]

SUM_LOUD_NOISE_DURATION = "Exposição (hh:mm) acima de ruído incomodativo"
# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def plot_noise_distribution_by_worktype(metrics_df: pd.DataFrame, save_path: str | Path, show: bool=True) -> None:
    """
    generates group-wise plots for showing the mean distribution of all noise distribution metrics per day
    :param metrics_df: pandas.DataFrame containing noise metrics data
    :param save_path: Path to where the figure will be written.
    :param show: Indicates whether to show the figure.
    :return:
    """

    # check for work_type column
    if "work_type" not in metrics_df.columns:
        raise KeyError("Input CSV must contain a 'work_type' column.")

    # get relevant columns indices
    relevant_col_idx = [num for num, col in enumerate(metrics_df.columns) if col.startswith("Noise_distributions")]

    # clean the column names
    metrics_df.columns = [col.split(".")[1] if col.startswith('Noise_distributions') else col for col in metrics_df.columns]

    # get the relevant cols
    relevant_cols = [metrics_df.columns[idx] for idx in relevant_col_idx]


    # cycle over the work_type
    for work_type, group_df in metrics_df.groupby('work_type', sort=False, observed=False):

        # generate figure
        fig, ax = plt.subplots(figsize=(14, 8))

        # calculate the mean
        work_type_mean_df = group_df.groupby('weekday')[relevant_cols].mean().round(4).mul(100)

        # ensure correct ordering of the noise classes within the dataframe
        work_type_mean_df = work_type_mean_df[NOISE_CLASS_ORDER]

        # get the weekdays
        weekdays = work_type_mean_df.index.tolist()
        weekday_pos = list(range(len(weekdays)))

        # init the bar_bottoms
        bar_bottoms = np.zeros(len(weekdays))

        # cycle over the noise classes
        for idx, noise_class in enumerate(NOISE_CLASS_ORDER):

            # get the values to plot
            values = work_type_mean_df[noise_class].to_numpy()

            # plot the data
            ax.bar(weekday_pos, values, bottom=bar_bottoms, color=CLASS_COLORS[noise_class], label=noise_class)

            # update the bar bottoms
            bar_bottoms += values

        # add the labes
        _add_percentage_labels(ax, work_type_mean_df.to_numpy())

        # plot styling
        ax.grid(axis="y", color="lightgray", linestyle="--", linewidth=0.7)
        ax.set_axisbelow(True)

        ax.set_xticks(weekday_pos)
        ax.set_xticklabels(weekdays, rotation=0, ha="center", fontsize=12)
        ax.set_ylabel("Percentagem de Tempo (%)", fontsize=12)
        ax.set_ylim(0, 100)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0f}%"))

        for spine in ax.spines.values():
            spine.set_visible(False)

        # ax.set_title(f" Distribuição de Ruído por Dia", fontsize=14)
        ax.legend(handles=LEGEND_PATCHES, loc="upper center", bbox_to_anchor=(0.5, -0.15),
                  ncol=len(CLASS_COLORS), frameon=False, fontsize=12)
        plt.tight_layout()


        # save plot if necessary
        if save_path is not None:
            file_path = Path(save_path) / f'noise_distributions_{work_type}{FILE_FORMAT}'
            # Make sure the destination directory exists before writing.
            file_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(file_path)

        if show:
            plt.show()

        # ensure figure is closed
        plt.close(fig)

def plot_elevated_noise_duration_by_worktype(metrics_df: pd.DataFrame, save_path: str | Path, show: bool=True) -> None:
    """

    :param metrics_df:
    :param save_path:
    :param show:
    :return:
    """

    # check for work_type column
    if "work_type" not in metrics_df.columns:
        raise KeyError("Input CSV must contain a 'work_type' column.")

    # get relevant columns indices
    relevant_col_idx = [num for num, col in enumerate(metrics_df.columns) if col.startswith("Noise_durations")]

    # clean the column names
    metrics_df.columns = [col.split(".")[1] if col.startswith('Noise_durations') else col for col in
                          metrics_df.columns]

    # calculate the sum of the columns
    metrics_df[SUM_LOUD_NOISE_DURATION] = metrics_df['Ruído incomodativo_duration_sec'] + metrics_df['Ruído elevado_duration_sec']

    # collect the necessary columns
    noise_df = metrics_df[[SUM_LOUD_NOISE_DURATION, 'weekday', 'work_type']]

    fig, ax = plot_raincloud_by_day(noise_df, metric=SUM_LOUD_NOISE_DURATION)

    # format x axis labels
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(_seconds_to_hhmm))

    # save plot if necessary
    if save_path is not None:
        file_path = Path(save_path) / f'noise_durations_by_worktype{FILE_FORMAT}'
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


def _seconds_to_hhmm(x, pos):
    """

    :param x:
    :param pos:
    :return:
    """
    x = int(x)
    return f"{x //3600:02d}:{(x % 3600) // 60:02d}"












