# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import os
import numpy as np
import math
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import matplotlib.colors as clr

from pathlib import Path
from typing import Dict
from matplotlib.axes import Axes

from constants import FILE_FORMAT, FO_COLOR, BO_COLOR, EDGE_COLOR, WORK_TYPES, GREEN, YELLOW, RED

# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
MAX_KEY = "max"
MIN_KEY = "min"


REFERENCE_VALUES = {

    "CO2": {MAX_KEY: 1250, MIN_KEY: 0},
    "CO": {MAX_KEY: 9, MIN_KEY: 0},
    "COV": {MAX_KEY: 0.16, MIN_KEY: 0},
    "Iluminância": {MAX_KEY: 500, MIN_KEY: 300},
    "Temperatura": {MAX_KEY: 23, MIN_KEY: 19},
    "Humidade": {MAX_KEY: 60, MIN_KEY: 40},
    "PM10": {MAX_KEY: 50, MIN_KEY: 0},
    "PM2.5": {MAX_KEY: 25, MIN_KEY: 0}
}

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def plot_rosa_environment(metrics_df: pd.DataFrame, q_type: str, is_rosa: bool, save_path: str | Path = None ) -> None:
    """
    Generates group plots for metrics in df. The plots are generated for:
    1. entire population
    2. front-office workers
    3. back-office workers

    This function is implemented for visualisation of the ROSA and the environment questionnaires.

    :param metrics_df: pandas.DataFrame containing either ROSA or environment data
    :param save_path: Path to where the figure will be written.
    :param q_type: Type of questionnaire.
    :param is_rosa: if True, handle the ROSA_final_normalized column specially (default=False)
    :return: None
    """

    # check for work_type column
    if "work_type" not in metrics_df.columns:
        raise KeyError("Input CSV must contain a 'work_type' column.")

    # filter out columns that are not body regions
    relevant_cols = [c for c in metrics_df.columns if c not in ("subject_id", "work_type")]

    # calculate the mean for the entire population
    population_mean = metrics_df[relevant_cols].mean(axis=0).to_frame().T

    # generate population level visualisation
    _generate_heatmap(population_mean, save_path, q_type, population_level="population", is_rosa=is_rosa)

    # group by work-type
    for work_type, group_df in metrics_df.groupby("work_type"):

        # calculate the work type mean
        work_type_mean = group_df[relevant_cols].mean(axis=0).to_frame().T

        # generate population level visualisation
        _generate_heatmap(work_type_mean, save_path, q_type, population_level=work_type, is_rosa=is_rosa)


def plot_environment_sensors_by_worktype(metrics_df: pd.DataFrame, save_path: str | Path = None, show: bool = False,
                                         fontsize: int = 12) -> None:
    """
    Generates group-wise box-plots for metrics in metrics_df.
    :param metrics_df: pandas.DataFrame containing either ROSA or environment data
    :param save_path: Path to where the figure will be written.
    :param show: Indicates whether to show the figure.
    :param fontsize: Font size for labels
    :return: None
    """

    # check for work_type column
    if "work_type" not in metrics_df.columns:
        raise KeyError("Input CSV must contain a 'work_type' column.")

    # clean column names
    metrics_df.columns = [col.split("_")[0] if col not in ("subject_id", "work_type") else col for col in metrics_df.columns]

    # filter out columns that are not body regions
    relevant_cols = [c for c in metrics_df.columns if c not in ("subject_id", "work_type")]

    # define indices of list with plots that should be plotted together
    plot_indices = [[6, 0, 7], [1, 2, 3], [4, 5]]

    # cycle over the relevant columns
    for plot_idx in plot_indices:

        # get sensor columns
        cols = [relevant_cols[idx] for idx in plot_idx]

        # generate subplot
        fig, axes = plt.subplots(nrows=1, ncols=len(cols), figsize=(12, 6))
        axes = axes.flatten()

        # cycle over the columns
        for col, ax in zip(cols, axes):

            # draw reference values
            _plot_reference_values(ax, REFERENCE_VALUES[col])

            # get sub-dataframe
            sub_df = metrics_df[[col, "work_type"]]

            # keep only unique values. For these sensors the measurement was only done once in the entire office
            # meaning that all workers within the same office have the same value
            if col != "Temperatura":
                sub_df = sub_df.drop_duplicates()

            # get median line color
            med_line_color = EDGE_COLOR if sub_df[col].sum() == 0 else "white"

            # generate box plot
            sns.boxplot(x="work_type", y=col, hue="work_type", data=sub_df, ax=ax, palette=[FO_COLOR, BO_COLOR],
                        hue_order=WORK_TYPES, linecolor=EDGE_COLOR, medianprops={"color": med_line_color,"linewidth": 1.5},
                        legend=False)


            # set title of axis
            ax.set_title(col, fontsize=fontsize + 2)
            ax.set(xlabel=None)
            ax.yaxis.label.set_fontsize(fontsize)

            plt.setp(ax.get_xticklabels(), fontsize=fontsize)
            plt.setp(ax.get_yticklabels(), fontsize=fontsize)

        fig.tight_layout()

        # save plot if necessary
        if save_path is not None:
            file_path = Path(save_path) / f'{"_".join(cols)}_by_work_type{FILE_FORMAT}'
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
def _generate_heatmap(df: pd.DataFrame, save_path: str, q_type: str, population_level: str, is_rosa: bool) -> None:
    """

    :param df:
    :param save_path:
    :param q_type:
    :param population_level:
    :param is_rosa:
    :return:
    """

    # substitute the scores in the df with a discrete scale (0,1,2) depending on the interval. This is used for the colormap
    # Map score to 0/1/2 based on range: 0–1/3 → 0, 1/3–2/3 → 1, 2/3–1 → 2, NaN -> -1
    # cycle over the columns
    for i, col in enumerate(df.columns):

        # get the value
        score = df.iloc[0, i]

        # if NaN -> -1
        if score is None or (isinstance(score, float) and math.isnan(score)):
            df.iloc[0, i] = -1

        # if 0–1/3 → 0
        elif score <= 1 / 3:
            df.iloc[0, i] = 0

        # if 1/3–2/3 → 1
        elif score <= 2 / 3:
            df.iloc[0, i] = 1

        # it's 2/3–1 → 2
        else:
            df.iloc[0, i] = 2

    # create colormap: gray for missing, then green, yellow, red
    cmap = clr.LinearSegmentedColormap.from_list('name', ['gray', GREEN, YELLOW, RED], N=4)

    # generate heat map
    _create_heat_map(df, save_path, f"{q_type}_plot_{population_level}{FILE_FORMAT}", color_map=cmap, vmin=-1,
                     vmax=2, is_rosa=is_rosa)


def _create_heat_map(df: pd.DataFrame, output_path: str, filename: str, color_map, vmin: int, vmax: int, is_rosa) -> None:
    """
    Create a single-row heatmap from a DataFrame with discrete values (-1 for missing, 0/1/2 for risk).
    If is_rosa=True, moves 'ROSA_final_normalized' to the last column and adds a dashed vertical
    line before it that reaches the xtick numbers without overlapping the last block.

    :param df: single-row DataFrame with columns corresponding to questionnaire items
    :param output_path: folder where the figure will be saved
    :param filename: name of the file to save
    :param is_rosa: if True, handle the ROSA_final_normalized column specially
    """
    # create copy of the original df
    df_plot = df.copy()

    # Move ROSA_final_normalized to last column if needed
    if is_rosa and "final_normalized" in df_plot.columns:
        cols = [c for c in df_plot.columns if c != "final_normalized"] + ["final_normalized"]
        df_plot = df_plot[cols]

    # Plot heatmap
    plt.figure(figsize=(15, 9))  # wider for better spacing
    ax = sns.heatmap(df_plot, cmap=color_map, linecolor='white', linewidths=3,
                     vmin=vmin, vmax=vmax, cbar=False,
                     xticklabels=np.arange(1, df_plot.shape[1] + 1))
    ax.xaxis.tick_top()
    ax.set_yticks([])

    # Adjust spacing
    plt.subplots_adjust(top=0.95,
                        bottom=0.90,
                        left=0.02,
                        right=0.014 + 0.03 * df_plot.shape[1],  # wider for thicker lines
                        hspace=0.958,
                        wspace=0.2)

    # Draw dashed vertical line before ROSA_final_normalized that reaches xtick numbers
    if is_rosa and "final_normalized" in df_plot.columns:

        # Index of last regular column (before final score)
        last_regular_col_idx = df_plot.columns.get_loc("final_normalized") - 1
        pos = ax.get_position()
        total_cols = df_plot.shape[1]

        # place line in the middle of the gap between last regular and final score
        x_fig = pos.x0 + (last_regular_col_idx + 1) / total_cols * (pos.x1 - pos.x0)

        fig = ax.get_figure()
        fig_line = plt.Line2D([x_fig, x_fig], [pos.y0, pos.y1 + 0.03], transform=fig.transFigure,
                              color='black', linewidth=1, linestyle='--')
        fig.add_artist(fig_line)

    # Save figure
    plt.savefig(os.path.join(output_path, filename), bbox_inches='tight', dpi=300)
    plt.close()

def _plot_reference_values(ax: Axes, ref_dict: Dict[str, int | float]) -> None:
    """
    plots the reference values contained in ref_dict into the axes as horizontal lines
    :param ax: matplotlib.axes.Axes - Axis object where the reference should be drawn.
    :param ref_dict: dictonary containing the maximum and minimum reference values
    :return: None
    """
    # get the maximum and minimum values
    max_val = ref_dict[MAX_KEY]
    min_val = ref_dict[MIN_KEY]

    # draw the maximum value
    ax.axhline(y=max_val, linestyle="--", color='red', linewidth=2)

    #  draw the minimum value (only if non-zero
    if min_val != 0:
        ax.axhline(y=min_val, linestyle="--", color='blue', linewidth=2)
