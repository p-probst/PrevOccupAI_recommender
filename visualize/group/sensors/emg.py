# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from typing import Tuple, List
from pathlib import Path
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.gridspec import GridSpec, SubplotSpec

from constants import WEEKDAY_COL, SESSION_NUM_COL, WORKTYPE_COL, NO_DATA_COL, SESSION_TIME_COL, PT, ENG, PALE_GREEN, \
    GREEN, YELLOW, RED, LIGHT_GRAY, FILE_FORMAT
from visualize.group.sensors.plot_utils import ROMAN_NUMERALS, plot_session_trajectories_by_worktype

# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
# key constants
# TODO: swap these for the keys defined in OH-profile when integrating it into the project
EMG_BIN_BELOW_USUAL_PCT_KEY = 'below_usual_pct'    # active time below weekly P10
EMG_BIN_TYPICAL_LOW_PCT_KEY = 'typical_low_pct'    # active time between P10-P50
EMG_BIN_TYPICAL_HIGH_PCT_KEY = 'typical_high_pct'  # active time between P50-P90
EMG_BIN_HIGH_FOR_YOU_PCT_KEY = 'high_for_you_pct'  # active time above weekly P90
X_LABEL_KEY = 'xlabel'

# class order
EMG_CLASS_ORDER = [EMG_BIN_BELOW_USUAL_PCT_KEY, EMG_BIN_TYPICAL_LOW_PCT_KEY, EMG_BIN_TYPICAL_HIGH_PCT_KEY,
                   EMG_BIN_HIGH_FOR_YOU_PCT_KEY, NO_DATA_COL]


# color constants
EMG_CLASS_COLORS = {
    EMG_BIN_BELOW_USUAL_PCT_KEY: PALE_GREEN,
    EMG_BIN_TYPICAL_LOW_PCT_KEY: GREEN,
    EMG_BIN_TYPICAL_HIGH_PCT_KEY: YELLOW,
    EMG_BIN_HIGH_FOR_YOU_PCT_KEY: RED,
    NO_DATA_COL: LIGHT_GRAY
}

# labels
LABEL_MAPPER = {
    EMG_BIN_BELOW_USUAL_PCT_KEY: {PT: "Abaixo do habitual", ENG: "Below usual"},
    EMG_BIN_TYPICAL_LOW_PCT_KEY: {PT: "Típico-baixo", ENG: "Typical-low"},
    EMG_BIN_TYPICAL_HIGH_PCT_KEY: {PT: "Típico-alto", ENG: "Typical-high"},
    EMG_BIN_HIGH_FOR_YOU_PCT_KEY: {PT: "Alto para si", ENG: "High for you"},
    NO_DATA_COL: {PT: "Sem dados", ENG: "No Data"},
    X_LABEL_KEY: {PT: "Tempo ativo (%)", ENG: "Active time (%)"},
}

# placement
MBAN_PLACEMENT = ["left", "right"]

FIGURE_TITLE = {
    PT: "Visão Geral Semanal de Intensidade Relativa",
    ENG: "Week Relative Intensity Overview"
}

SUB_FIGURE_TITLES = {
    "left": {PT: "Ombro Esquerdo", ENG: "Left Shoulder"},
    "right": {PT: "Ombro Direito", ENG: "Right Shoulder"}
}

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def plot_emg_relative_intensity_by_worktype(metrics_df: pd.DataFrame, save_path: str | Path, show: bool = True,
                                            language: str = 'pt'):
    """
    plots the relative EMG intensity for the left and right placements, for each day and session, by calculating the
    mean over each work type.
    :param metrics_df: pandas.DataFrame containing the EMG metrics
    :param save_path: Path to where the figure will be written.
    :param show: Indicates whether to show the figure.
    :param language: Output language code ('pt' or 'eng'). Default: 'pt'
    :return: None
    """

    # check for work_type column
    if WORKTYPE_COL not in metrics_df.columns:
        raise KeyError(f"Input CSV must contain a {WORKTYPE_COL} column.")

    # copy dataframe to ensure that it is not changed
    metrics_df = metrics_df.copy()

    # get relevant columns indices
    relevant_cols = [col for col in metrics_df.columns if "EMG_" in col]

    # fill nan values with zeros for rows where a Session exists
    metrics_df = _fill_nan_classes_and_sessions(metrics_df)

    # cycle over the work_type
    for work_type, group_df in metrics_df.groupby(WORKTYPE_COL, sort=False, observed=False):
        # calculate the mean values by day and session
        data_df = group_df.groupby([WEEKDAY_COL, SESSION_NUM_COL], observed=False)[relevant_cols].mean()

        # reinstate the index to full columns (weekday and Session)
        # this is to have the same structure as if it were single subject
        data_df = data_df.reset_index()

        fig = plot_emg_relative_intensity(data_df, language=language, show_sup_title=False)

        # save plot if necessary
        if save_path is not None:
            file_path = Path(save_path) / f'emg_relative_bins_{work_type}{FILE_FORMAT}'
            # Make sure the destination directory exists before writing.
            file_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(file_path, dpi=300, bbox_inches='tight')

        if show:
            plt.show()

        # ensure figure is closed
        plt.close(fig)


def plot_emg_relative_intensity(data_df: pd.DataFrame, language: str='pt', show_sup_title: bool=True, fontsize: int=12)-> Figure:
    """
    plots the relative EMG intensity for the left and right placements, for each day and session.
    :param data_df: pandas.DataFrame containing the EMG related metrics
    :param language: Output language code ('pt' or 'eng'). Default: 'pt'
    :param show_sup_title: controls whether to show the figure sup-title or not
    :param fontsize: the fontsize to be used in the plot
    :return: figure containing the plot
    """

    # fill in missing data
    data_df, weekdays = _fill_missing_data(data_df)

    # create figure to hold plot
    fig = plt.figure(figsize=(12, 10))

    # add title
    if show_sup_title:
        fig.suptitle(FIGURE_TITLE[language], fontsize=fontsize + 2, fontweight='bold')

    # generate gridspec for flexible plot alignment (centering in the last line of the plot)
    # 4 columns needed to then center in the last row. For each day plot two columns are used
    # these columns are then later overwritten by a subgridspec spanning these two columns
    num_rows = 3
    num_plots_per_col = 2
    outer_grid = fig.add_gridspec(num_rows, num_plots_per_col * 2, wspace=0.35, hspace=0.6)

    # dict to capture legend handles - these will be later added to the fig
    legend_handles = {}

    # cycle over the weekdays
    for idx, weekday in enumerate(weekdays):

        # get the data from the day
        day_df = data_df[data_df[WEEKDAY_COL] == weekday]

        # generate the axes for plotting the day plot
        left_ax, label_ax, right_ax = _create_day_plot_grid(outer_grid, fig, len(weekdays), num_plots_per_col, idx)

        # get the number of sessions
        num_sessions = day_df.shape[0]

        # get the y-position
        y_pos = np.arange(num_sessions)

        # plot the data for the day
        for ax, side in ((left_ax, "left"), (right_ax, "right")):

            # get corresponding columns
            side_columns = [col for col in day_df if col.startswith(side)]

            # get the data frame
            side_df = day_df[side_columns].copy()

            # overwrite the column names (for easier processing)
            side_df.columns = [col.split('.')[-1] for col in side_columns]

            # order the columns in the correct order
            side_df = side_df[EMG_CLASS_ORDER]

            # init the bar left position (for stacking)
            bar_left_pos = np.zeros(num_sessions)

            # cycle over through the columns
            for column, values in side_df.items():

                # get the label
                label = LABEL_MAPPER[column][language]

                # plot the bars
                ax.barh(y=y_pos, width=values, left=bar_left_pos, label=label,
                        color=EMG_CLASS_COLORS[column], height=0.6)

                # collect the legend handles
                if label not in legend_handles:
                    legend_handles[label] = ax.patches[-1] # this gets the last plotted bar color


                # update the bar pos for stacking
                bar_left_pos += values

            # style session axis
            _style_session_axis(ax, side, y_pos, language=language, fontsize=fontsize)

        # add session labels
        _add_session_labels(day_df, label_ax, y_pos, fontsize=fontsize-2)

        # style day plot
        _style_day_plot(left_ax, label_ax, right_ax, weekday, fontsize=fontsize-2)

    # add the legends
    fig.legend(handles=legend_handles.values(), labels=legend_handles.keys(), loc="lower center",
               bbox_to_anchor=(0.5, 0.02), ncol=len(legend_handles.keys()), prop={"size": fontsize - 2})

    return fig

def plot_elevated_emg_trajectories_by_worktype(metrics_df: pd.DataFrame, save_path: str | Path, show: bool = True) -> None:
    """
    Generates a subplot of shape (5, 2) containing session trajectories for each day and worktype . The trajectories
    show the evolution of the chosen metric throughout the day (each session). For each subject a thin line is plotted.
    The population mean is shown with a thick line and the standard deviation is plotted as a shaded area.
    :param metrics_df: pandas.DataFrame containing the EMG related metrics
    :param save_path: Path to where the figure will be written.
    :param show: Indicates whether to show the figure.
    :return: None
    """

    # copy dataframe
    metrics_df = metrics_df.copy()

    # check for work_type column
    if WORKTYPE_COL not in metrics_df.columns:
        raise KeyError(f"Input CSV must contain a {WORKTYPE_COL} column.")

    # cycle over left and right
    for side in ['left', 'right']:

        # fill nan values
        metrics_df[[f'{side}.EMG_relative_bins.typical_high_pct', f'{side}.EMG_relative_bins.high_for_you_pct',]] = metrics_df[[f'{side}.EMG_relative_bins.typical_high_pct', f'{side}.EMG_relative_bins.high_for_you_pct',]].fillna(0)

        # calculate the sum of the elevated classes
        metrics_df[f'{side}_EMG_sum_high'] = metrics_df[f'{side}.EMG_relative_bins.typical_high_pct'] + metrics_df[f'{side}.EMG_relative_bins.high_for_you_pct']
        # fill missing session numbers
        metrics_df[SESSION_NUM_COL] = metrics_df[f'left.{SESSION_NUM_COL}'].combine_first(
            metrics_df[f'right.{SESSION_NUM_COL}']).astype(int)


        # plot the trajectories
        plot_session_trajectories_by_worktype(metrics_df, f'{side}_EMG_sum_high', save_path=save_path, show=show)


# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #
def _fill_nan_classes_and_sessions(metrics_df: pd.DataFrame) -> pd.DataFrame:
    """
    Fills classes that have a nan value with zero for those rows where a session number exists
    :param metrics_df: pandas.DataFrame containing the EMG metrics
    :return: pandas.DataFrame with the nan classes filled with zero
    """

    # check whether the session number column has not been generated yet
    if SESSION_NUM_COL not in metrics_df.columns:

        # cycle over left and right
        for side in MBAN_PLACEMENT:
            # get the relevant cols
            relevant_cols = [col for col in metrics_df.columns if col.startswith(f"{side}.EMG")]

            # get the rows where Session is not nan
            mask = metrics_df[f"{side}.Session"].notna()

            # fill the missing class values with zero
            metrics_df.loc[mask, relevant_cols] = metrics_df.loc[mask, relevant_cols].fillna(0)

        # fill missing session numbers
        metrics_df[SESSION_NUM_COL] = metrics_df[f'left.{SESSION_NUM_COL}'].combine_first(
            metrics_df[f'right.{SESSION_NUM_COL}']).astype(int)

        # drop the left and right session number columns as they are not needed anymore
        metrics_df = metrics_df.drop(columns=[f"left.{SESSION_NUM_COL}", f"right.{SESSION_NUM_COL}"])


    return metrics_df


def _fill_missing_data(data_df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Fills in missing days and sessions, as well as filling missing classes for already existing acquisitions.
    Additionally, two columns are generated which indicate whether there is no data for either the left or the right
    :param data_df: pandas.DataFrame containing the data from one subject or the mean of several subjects
    :return: pandas.DataFrame with the missing data filled in and the weekdays
    """

    # get the weekdays
    weekdays = list(data_df[WEEKDAY_COL].cat.categories)

    # set the number of sessions
    sessions = list(range(1, 5))

    # fill in the missing classes for session where data is present. This is so that the values add up to 100 %
    data_df = _fill_nan_classes_and_sessions(data_df)

    # build the full grid of expected (weekday, Session) pairs
    full_index = pd.MultiIndex.from_product([weekdays, sessions], names=[WEEKDAY_COL, SESSION_NUM_COL])

    # reindex against it — missing rows show up as NaN
    data_df = data_df.set_index([WEEKDAY_COL, SESSION_NUM_COL]).reindex(full_index)

    for side in MBAN_PLACEMENT:

        # get the relevant cols
        relevant_cols = [col for col in data_df.columns if col.startswith(f"{side}.EMG")]

        # flag missing rows before filling
        data_df[f'{side}.{NO_DATA_COL}'] = data_df[relevant_cols].isna().all(axis=1).astype(int).mul(100)

    # check for session column (has the session time)
    if SESSION_TIME_COL in data_df.columns:

        data_df.loc[(data_df[f'{MBAN_PLACEMENT[0]}.{NO_DATA_COL}'] == 100) & (data_df[f'{MBAN_PLACEMENT[1]}.{NO_DATA_COL}'] == 100), SESSION_TIME_COL] = 'missing'

    # fill the numeric columns with 0
    data_df = data_df.fillna(0).reset_index()

    return data_df, weekdays


def _create_day_plot_grid(outer_grid: GridSpec, fig: Figure, num_weekdays: int, num_cols_outer_grid: int, idx: int) -> Tuple[Axes, Axes, Axes]:
    """
    generates a subgrid to hold the day plot
    :param outer_grid: the outer grid holding the grids for each day plot
    :param fig: the figure
    :param num_weekdays: the number of weekdays to plot
    :param num_cols_outer_grid: the number of columns in the outer grid
    :param idx: the index of the current day, obtained through enumerate(weekdays)
    :return: tuple containing the axis of the day plot in the order left_ax, label_ax, right_ax
    """

    # calculate the row and col position
    row_num = idx // num_cols_outer_grid
    col_num = idx % num_cols_outer_grid

    # calculate offset for centering
    offset = 1 if idx == num_weekdays - 1 else 0

    # calculate the start and end of the column for slicing
    col_start = offset + col_num * 2
    col_end = col_start + 2

    # create subgridspec that spans two columns within the outer grid
    # the subgrid has three columns left_ax, right_ax, and label_ax for displaying the left data, right data, and the corresponding labels
    # the label_ax sits in between the left and right to show the acquisition times
    inner_grid = outer_grid[row_num, col_start:col_end].subgridspec(1, 3, width_ratios=(1, 0.32, 1),
                                                                    wspace=0.08)

    # add the plots the columns
    left_ax = fig.add_subplot(inner_grid[0, 0])
    label_ax = fig.add_subplot(inner_grid[0, 1])
    right_ax = fig.add_subplot(inner_grid[0, 2])

    return left_ax, label_ax, right_ax


def _style_session_axis(ax: Axes, side: str, y_positions: np.ndarray, language: str = 'pt', fontsize: int = 12) -> None:
    """
    Styles the session subplot
    :param ax: the axis containing the session subplot
    :param side: the muscleBAN placement side, either 'left' or 'right'
    :param y_positions: the y-positions of the bars
    :param language: Output language code ('pt' or 'eng'). Default: 'pt'
    :return: None
    """

    # set axis title
    ax.set_title(SUB_FIGURE_TITLES[side][language], fontsize=fontsize)

    # set x-label
    ax.set_xlabel(LABEL_MAPPER[X_LABEL_KEY][language], fontsize=fontsize - 2)

    # set ticks
    ax.set_yticks(y_positions)
    ax.set_yticklabels([])
    ax.set_xlim(0, 100)

    # set grid
    ax.set_axisbelow(True)
    ax.grid(axis="x", alpha=0.3, linestyle="--", linewidth=1.5)

    # remove all spines except bottom
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _add_session_labels(day_df: pd.DataFrame, label_ax, y_positions:np.ndarray, fontsize: int=12) -> None:
    """
    adds the session time labels to the label_ax.
    :param day_df: pandas.DataFrame containing the day data
    :param label_ax: the for displaying the labels
    :param y_positions: the y-positions of the bars
    :param fontsize: the fontsize of the labels
    :return: None
    """


    # set the label axis
    label_ax.set_ylim(-0.5, day_df.shape[0] - 0.5)

    # check whether the dataframe has the session time column
    if SESSION_TIME_COL in day_df.columns:

        session_labels = day_df[SESSION_TIME_COL].copy().apply(_generate_acquisition_time_labels).to_list()

    else:

        # grab the session num column
        session_labels = day_df[SESSION_NUM_COL].copy().apply(_to_roman_numerals).to_list()

    # place the session labels
    for y_pos, label in zip(y_positions, session_labels):

        label_ax.text(0.5, float(y_pos), label, va="center", ha="center", fontsize=fontsize, fontweight="bold")


def _generate_acquisition_time_labels(acq_time: str) -> str:
    """
    transforms an acquisition time label from the format HH-MM-SS into a format HH:MM.
    :param acq_time: the acquisition time label:
    :return: the formatted acquisition time label
    """

    if acq_time.startswith("missing"):

        return "-:-"

    else:

        return acq_time[:5].replace("-", ":")


def _to_roman_numerals(session_num: int) -> str:
    """
    Transforms a session number to roman numerals.
    :param session_num: the session number
    :return: the roman numeral
    """

    return ROMAN_NUMERALS[session_num]



def _style_day_plot(left_ax, label_ax, right_ax, weekday: str, fontsize: int = 12) -> None:
    """
    styles the day plot
    :param left_ax: left axis of the day plot
    :param label_ax: label axis of the day plot
    :param right_ax: right axis of the day plot
    :param weekday: the weekday corresponding to the plot
    :param fontsize: the font size of the labels
    :return: None
    """

    # style day plot
    # add plot title
    label_ax.set_title(weekday.split('-')[0], fontsize=fontsize, fontweight='bold')
    label_ax.axis('off')

    # invert the y-axis
    label_ax.invert_yaxis()
    left_ax.invert_yaxis()
    right_ax.invert_yaxis()

    # invert the x-axis for the left plot
    left_ax.invert_xaxis()
    left_ax.yaxis.tick_right()






