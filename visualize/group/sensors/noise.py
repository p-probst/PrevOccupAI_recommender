# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker

from pathlib import Path

from constants import STRONG_GREEN, PALE_GREEN, YELLOW, RED, FILE_FORMAT
from .plot_utils import plot_raincloud_by_day, seconds_to_hhmm, plot_stacked_bar_chart

# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
NOISE_NEAR_SILENCE_KEY = 'Silencioso'
NOISE_LOW_KEY = 'Ruído baixo'
NOISE_DISTURBING_KEY = 'Ruído incomodativo'
NOISE_HIGH_KEY = 'Ruído elevado'
NOISE_CLASS_ORDER = [NOISE_NEAR_SILENCE_KEY, NOISE_LOW_KEY, NOISE_DISTURBING_KEY, NOISE_HIGH_KEY]

NOISE_CLASS_COLORS = {NOISE_NEAR_SILENCE_KEY: STRONG_GREEN,
                      NOISE_LOW_KEY: PALE_GREEN,
                      NOISE_DISTURBING_KEY: YELLOW,
                      NOISE_HIGH_KEY: RED
                      }

LEGEND_PATCHES = [
            mpatches.Patch(color=NOISE_CLASS_COLORS[NOISE_NEAR_SILENCE_KEY], label=f"{NOISE_NEAR_SILENCE_KEY}  ≤ 40 dBA"),
            mpatches.Patch(color=NOISE_CLASS_COLORS[NOISE_LOW_KEY], label=f"{NOISE_LOW_KEY} 40–60 dBA"),
            mpatches.Patch(color=NOISE_CLASS_COLORS[NOISE_DISTURBING_KEY], label=f"{NOISE_DISTURBING_KEY} 60–80 dBA"),
            mpatches.Patch(color=NOISE_CLASS_COLORS[NOISE_HIGH_KEY], label=f"{NOISE_HIGH_KEY} ≥ 80 dBA")
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
    :return: None
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
        fig, ax = plot_stacked_bar_chart(group_df, relevant_cols, NOISE_CLASS_ORDER, NOISE_CLASS_COLORS, LEGEND_PATCHES)


        # save plot if necessary
        if save_path is not None:
            file_path = Path(save_path) / f'noise_distributions_{work_type}{FILE_FORMAT}'
            # Make sure the destination directory exists before writing.
            file_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(file_path, dpi=300, bbox_inches='tight')

        if show:
            plt.show()

        # ensure figure is closed
        plt.close(fig)


def plot_elevated_noise_duration_by_worktype(metrics_df: pd.DataFrame, save_path: str | Path, show: bool=True) -> None:
    """
    Generates a raincloud plot that displays the exposure time to disruptive noise and above for the FO and BO populations.
    :param metrics_df: pandas.DataFrame containing noise metrics data
    :param save_path: Path to where the figure will be written.
    :param show: Indicates whether to show the figure.
    :return: None
    """

    # check for work_type column
    if "work_type" not in metrics_df.columns:
        raise KeyError("Input CSV must contain a 'work_type' column.")

    # clean the column names
    metrics_df.columns = [col.split(".")[1] if col.startswith('Noise_durations') else col for col in
                          metrics_df.columns]

    # calculate the sum of the columns
    metrics_df[SUM_LOUD_NOISE_DURATION] = metrics_df['Ruído incomodativo_duration_sec'] + metrics_df['Ruído elevado_duration_sec']

    # collect the necessary columns
    noise_df = metrics_df[[SUM_LOUD_NOISE_DURATION, 'weekday', 'work_type']]

    fig, ax = plot_raincloud_by_day(noise_df, metric=SUM_LOUD_NOISE_DURATION)

    # format x axis labels
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(seconds_to_hhmm))

    # save plot if necessary
    if save_path is not None:
        file_path = Path(save_path) / f'noise_durations_by_worktype{FILE_FORMAT}'
        # Make sure the destination directory exists before writing.
        file_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(file_path, dpi=300, bbox_inches='tight')

    if show:
        plt.show()

    # ensure figure is closed
    plt.close(fig)

# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #













