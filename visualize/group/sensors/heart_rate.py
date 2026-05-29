# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from pathlib import Path
from typing import Tuple, List
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from datetime import datetime, timedelta

from constants import PALE_GREEN, YELLOW, RED, LIGHT_GRAY, GRAY, LIGHT_RED, DEEP_RED, FILE_FORMAT, WEEKDAY_COL, \
    SESSION_NUM_COL, SESSION_TIME_COL, WORKTYPE_COL, NO_DATA_COL
from .plot_utils import ROMAN_NUMERALS, plot_session_trajectories_by_worktype
from recommender.load.language_mappings import HEART_RATE_MAPPING
# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
# TODO: swap these for the keys defined in OH-profile when integrating it into the project
HR_NORMAL_KEY = 'Normal'
HR_POTENTIALLY_ELEVATED_KEY = 'Ligeiramente elevado'
HR_ELEVATED_KEY = 'Elevado'


HEART_RATE_CLASS_ORDER = [HR_NORMAL_KEY, HR_POTENTIALLY_ELEVATED_KEY, HR_ELEVATED_KEY, NO_DATA_COL]


HR_CLASS_COLORS = {
    HR_NORMAL_KEY: PALE_GREEN,                # green
    HR_POTENTIALLY_ELEVATED_KEY: YELLOW,  # orange
    HR_ELEVATED_KEY: RED,              # red
    NO_DATA_COL: LIGHT_GRAY                 # light gray
}

# values for HR range plot
BAR_WIDTH_PTS = 18
PLACEHOLDER_MIN = 60
PLACEHOLDER_MAX = 100
PLACEHOLDER_COLOR = GRAY
# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def plot_hr_circular_distribution_by_worktype(metrics_df: pd.DataFrame, save_path: str | Path, show:bool = True, language: str = 'pt') -> None:
    """
    plots the circular distribution plot by work type
    :param metrics_df:
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
    relevant_col_idx = [num for num, col in enumerate(metrics_df.columns) if col.startswith("HR_distributions")]

    # clean the column names
    metrics_df.columns = [col.split(".")[1] if col.startswith('HR_distributions') else col for col in
                          metrics_df.columns]

    # get the relevant cols
    relevant_cols = [metrics_df.columns[idx] for idx in relevant_col_idx]

    # fill nan values with zero
    metrics_df[relevant_cols] = metrics_df[relevant_cols].fillna(0)

    # cycle over the work_type
    for work_type, group_df in metrics_df.groupby(WORKTYPE_COL, sort=False, observed=False):

        # calculate the mean values by day and session
        data_df = group_df.groupby([WEEKDAY_COL, SESSION_NUM_COL], observed=False)[relevant_cols].mean()

        # reinstate the index to full columns (weekday and Session)
        # this is to have the same structure as if it were single subject
        data_df = data_df.reset_index()

        # generate circular plot
        fig, ax = plot_hr_circular_distribution(data_df, show_time_legend=False, language=language)

        # save plot if necessary
        if save_path is not None:
            file_path = Path(save_path) / f'hr_distribution_{work_type}{FILE_FORMAT}'
            # Make sure the destination directory exists before writing.
            file_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(file_path, dpi=300, bbox_inches='tight')

        if show:
            plt.show()

        # ensure figure is closed
        plt.close(fig)


def plot_hr_circular_distribution(data_df: pd.DataFrame, lower_limit: int=30, upper_limit: int=70,
                                  show_time_legend:bool = True, language: str = 'pt', fontsize: int=10) -> Tuple[Figure, Axes]:
    """
    Plots a circular bar plot containing the heart rate class distribution for each recorded session.
    Sessions in which no data was recorded are shown as grey
    :param data_df: pandas.DataFrame containing the data to plot
    :param lower_limit: the lower limit to which the data should be scaled to
    :param upper_limit: the upper limit to which the data should be scaled to
    :param show_time_legend: boolean flag indicating whether the acquisition time legend should be plotted. This is only
                             possible if data_df contains the necessary columns with the acquisition times, session numbers, and weekdays.
    :param language: Output language code ('pt' or 'eng'). Default: 'pt'
    :param fontsize: the fontsize to be used
    :return: tuple of matplotlib figure and axes
    """

    # fill in missing data
    data_df, weekdays = _fill_missing_data(data_df)

    # clean column names
    data_df.columns = [col.split(".")[1] if col.startswith('HR_distributions') else col for col in
                          data_df.columns]

    # just get the distribution data in the correct order and multiply by 100 to get percentages
    distributions_df = data_df[HEART_RATE_CLASS_ORDER].mul(100)

    # Scale data to fit limits
    distributions_df = _scale_data(distributions_df, lower_limit, upper_limit)

    # create figure with polar axes
    fig, ax = plt.subplots(figsize=(14, 10), subplot_kw={"projection": "polar"})

    # Turn off axes cleanly (avoid plt.axis('off') side effects)
    ax.set_axis_off()

    # Plot circular bars
    width, angles = _plot_circ_bars(distributions_df, HR_CLASS_COLORS, lower_limit, ax, language=language)

    # Add color legend
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc="center", fontsize=fontsize + 2)

    separator_pos = _draw_day_separators(angles, width, len(weekdays), lower_limit, upper_limit, ax)

    # add session nums at the bottom of each bar
    _show_session_labels(angles, data_df[SESSION_NUM_COL].replace(ROMAN_NUMERALS), ax, lower_limit, fontsize + 4)

    # add day labels
    _show_day_labels(weekdays, np.append(separator_pos, separator_pos[0] + 2 * np.pi), 1.05, ax, fontsize=fontsize + 4)

    # plot time legend if wanted
    if show_time_legend:

        # check for weekday and session column
        if all(column in data_df.columns for column in [WEEKDAY_COL, SESSION_TIME_COL]):

            # adjust plot to accommodate label
            fig.subplots_adjust(left=0.02, right=0.78, top=0.88, bottom=0.25)
            ax.set_position([0.00, 0.09, 0.85, 0.85])

            # create and print legends onto the plot
            legends_to_print = _generate_acquisition_time_labels(data_df, language=language)
            _print_acquisition_time_labels(legends_to_print, fig, fontsize + 4)

    fig.tight_layout()

    return fig, ax


def plot_hr_ranges_by_worktype(metrics_df: pd.DataFrame, save_path: str | Path, show: bool = True) -> None:
    """
    plots the Hear Rate Range plot for the FO and BO work types
    :param metrics_df: pandas.DataFrame containing metrics to plot.
    :param save_path: Path to where the figure will be written.
    :param show: Indicates whether to show the figure.
    :return: None
    """

    # check for work_type column
    if WORKTYPE_COL not in metrics_df.columns:
        raise KeyError(f"Input CSV must contain a {WORKTYPE_COL} column.")


    # set the relevant columns
    relevant_cols = ["HR_BPM_stats.max", "HR_BPM_stats.min"]

    # cycle over the work_type
    for work_type, group_df in metrics_df.groupby(WORKTYPE_COL, sort=False, observed=False):

        # calculate the mean min and max value by session and day
        data_df = group_df.groupby([WEEKDAY_COL, SESSION_NUM_COL])[relevant_cols].mean()

        # reinstate the index to full columns (weekday and Session)
        # this is to have the same structure as if it were single subject
        data_df = data_df.reset_index()

        # plot the hr_range plot
        fig, axes = plot_hr_ranges(data_df)

        # save plot if necessary
        if save_path is not None:
            file_path = Path(save_path) / f'hr_range_{work_type}{FILE_FORMAT}'
            # Make sure the destination directory exists before writing.
            file_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(file_path, dpi=300, bbox_inches='tight')

        if show:
            plt.show()

        # ensure figure is closed
        plt.close(fig)


def plot_hr_ranges(data_df: pd.DataFrame) -> Tuple[Figure, Axes]:
    """
    Plot vertical bars representing Heart Rate (HR) ranges per session (I–IV) for each day.

    - X axis: session number (I–IV), grouped by weekday.
    - Weekday labels are shown below the sessions.
    - Y axis: BPM. Each bar spans from session min to session max.
    - Missing sessions are displayed with a 'Sem dados' placeholder.

    :param data_df: pandas.DataFrame containing the data from one subject or the mean of several subjects
    :return: The figure and axes objects
    """

    # get the weekdays
    weekdays = list(data_df[WEEKDAY_COL].cat.categories)

    # set the number of sessions
    sessions = list(range(1, 5))

    # create figure and axes
    fig, ax = plt.subplots(figsize=(max(10, len(weekdays) * 4 * 0.6), 6))

    # set the y-limits of the plot
    _set_y_limits(ax, data_df)

    # plot the range bars
    x_ticks_and_labels = _draw_range_bars(ax, data_df, weekdays, sessions)

    # style the plot
    _style_plot(ax, x_ticks_and_labels, weekdays)

    return fig, ax


def plot_elevated_hr_trajectories_by_worktype(metrics_df: pd.DataFrame, save_path: str | Path, show: bool = True) -> None:
    """
    plots the trajectories for the sum of the slightly elevated and elevated HR class
    :param metrics_df: pandas.DataFrame containing metrics to plot.
    :param save_path: Path to where the figure will be written.
    :param show: Indicates whether to show the figure.
    :return: None
    """

    # copy dataframe
    metrics_df = metrics_df.copy()

    # check for work_type column
    if WORKTYPE_COL not in metrics_df.columns:
        raise KeyError(f"Input CSV must contain a {WORKTYPE_COL} column.")

    # fill nan values
    metrics_df[['HR_distributions.Ligeiramente elevado', 'HR_distributions.Elevado']] = metrics_df[['HR_distributions.Ligeiramente elevado', 'HR_distributions.Elevado']].fillna(0)

    # calculate the sum of the elevated classes
    metrics_df['HR_above_elevado'] = (metrics_df['HR_distributions.Ligeiramente elevado'] + metrics_df['HR_distributions.Elevado']).mul(100)

    # plot the trajectories
    plot_session_trajectories_by_worktype(metrics_df, 'HR_above_elevado', save_path=save_path, show=show)




# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #
def _fill_missing_data(data_df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    fills in missing days and session by adding a "no data" column
    :param data_df: pandas.DataFrame containing the data from one subject or the mean of several subjects
    :return: pandas.DataFrame with the missing data filled in
    """

    # get the weekdays
    weekdays = list(data_df[WEEKDAY_COL].cat.categories)

    # set the number of sessions
    sessions = list(range(1, 5))

    # build the full grid of expected (weekday, Session) pairs
    full_index = pd.MultiIndex.from_product([weekdays, sessions], names=[WEEKDAY_COL, SESSION_NUM_COL])

    # reindex against it — missing rows show up as NaN
    data_df = data_df.set_index([WEEKDAY_COL, SESSION_NUM_COL]).reindex(full_index)

    # flag missing rows before filling
    data_df[NO_DATA_COL] = data_df.isna().all(axis=1).astype(int)

    # check for session column (has the session time)
    if SESSION_TIME_COL in data_df.columns:

        data_df.loc[data_df[NO_DATA_COL] == 1, SESSION_TIME_COL] = 'missing'

    # fill the numeric columns with 0
    data_df = data_df.fillna(0).reset_index()

    return data_df, weekdays


def _scale_data(data, lower_limit, upper_limit):
    """
    scales the data between the lower and upper limit
    :param data: the data (pandas data frame)
    :param lower_limit: the lower limit to which the data should be scaled to
    :param upper_limit: the upper limit to which the data should be scaled to
    :return: pandas data frame with the scaled data
    """
    # put the values between a range of [lower_limit, upper_limit (for visualization purposes)
    # 1. compute the maximum value in the entire dataset
    max_val = data.to_numpy().max()
    min_val = data.to_numpy().min()

    # 2. scale the data to fit the set upper and lower limit
    return ((data - min_val) / (max_val - min_val)) * (upper_limit - lower_limit)


def _plot_circ_bars(hr_percentage_df, color_scheme, lower_limit, ax, language: str = 'pt'):
    """
    Plots a circular stacked bar plot.
    :param hr_percentage_df: DataFrame with the percentages of each heart rate class during acquisitions
    :param color_scheme: dict (class_name -> color hex) or list of colors
    :param lower_limit: lower limit of the plot. Parameter to set the proportions of the plot.
    :param ax: matplotlib axis
    :return: (width, angles) of the bars
    """

    # initialize the bottom (where the bars should start)
    bottom = np.zeros(hr_percentage_df.shape[0]) + lower_limit

    # calculate the bar width and angles for plotting the bars
    width, angles = _get_bar_width_and_angles(hr_percentage_df)

    # if it's a list, make it iterable
    if isinstance(color_scheme, (list, tuple)):
        color_iter = iter(color_scheme)
    else:
        color_iter = None  # not needed if it's a dict

    # cycle through the columns and plot
    for column, values in hr_percentage_df.items():
        # choose the color
        if isinstance(color_scheme, dict):
            color = color_scheme.get(column, "#E0E0E0")  # fallback light gray
        else:
            color = _get_next_color(color_iter)

        # plot the bars
        ax.bar(x=angles,height=values,width=width,bottom=bottom,label=HEART_RATE_MAPPING[column][language],
               color=color,edgecolor="#FFFFFF",lw=0.8)

        # update the bottom (stacking)
        bottom = bottom + values

    return width, angles


def _get_next_color(cs_iterator):
    """
    returns the next color from an iterator if the iterator exists
    :param cs_iterator: the color scheme iterator
    :return: next color of iterator or None when no color scheme was provided
    """

    if cs_iterator:

        return next(cs_iterator)

    else:
        return None


def _get_bar_width_and_angles(hr_percentage_df):
    """
    calculates the bar widths and angles for circular plot
    :param hr_percentage_df: the data frame with the percentages of each heart rate class during the acquisitions
    :return: the bar width and angles for plotting the bars
    """

    # compute the width of each bar
    width = 2 * np.pi / hr_percentage_df.shape[0]

    # set the indexes for calculating the angles
    indexes = list(range(1, hr_percentage_df.shape[0] + 1))

    # the x position of the bar is set at its center, therefore half of the width needs to be
    # subtracted to get a correct positioning
    angles = [(element * width) - width / 2 for element in indexes]

    # add pi/2 for the plot to start at the top center of the circle (12 o-clock position)
    angles = [angle + np.pi / 2 for angle in angles]

    # reverse the angles to have the bars ordered clock-wise
    angles.reverse()

    return width, angles


def _draw_day_separators(angles: List[float], bar_width: float, num_weekdays: int, lower_limit: int, upper_limit: int, ax):
    """
    Draws white vertical separators between each acquisition day to make the plot easier to read
    :param angles: the angles of the bars that were plotted
    :param bar_width: the bar width that was used in the plot
    :param num_weekdays: the number of weekdays that were plotted
    :param lower_limit: lower limit of the plot.
    :param upper_limit: upper limit of the plot.
    :param ax: axes object in which the plot is drawn
    :return: None
    """

    # get the positions of the angles (four acquisitions per day)
    angle_pos = np.arange(0, num_weekdays * 4, 4)

    # get the corresponding angles
    angles_pos = [angles[pos] for pos in angle_pos]

    # shift the positions by half a bar
    separator_positions = [angle_pos + bar_width / 2 for angle_pos in angles_pos]

    # draw the separators (ensure the separator covers the whole plot
    ax.vlines(separator_positions, lower_limit, upper_limit + 5, color="#FFFFFF", linewidth=6.5)

    return separator_positions


def _show_session_labels(angles: List[float], labels: List[str], ax: Axes, lower_limit: int, fontsize: int=14) -> None:
    """
    adds acquisition labels to the bottom of the bars
    :param angles: the angles at which the center of the bar is located
    :param labels: the labels to add
    :param ax: the plot axis
    :param lower_limit: lower limit of the plot. Parameter to set the proportions of the plot.
    :param fontsize: the font size for the session labels
    :return: None
    """

    for angle, label in zip(angles, labels):

        ax.text(x=angle, y=lower_limit - 3, s=label, va='center', ha='center', fontsize=fontsize)


def _show_day_labels(weekdays: List[str], sep_pos: np.ndarray, y_pos: float, ax: Axes, fontweight: str='semibold', fontsize: int=16) -> None:
    """
    adds day labels to the plot that are centered between the day separation lines
    :param weekdays: weekdays of the acquisition
    :param sep_pos: the positions of the lines that visually separate the days on the plot
    :param ax: plot axes
    :return: None
    """

    # add the day labels to the plot
    for weekday, pos_start, pos_end in zip(weekdays, sep_pos[:-1], sep_pos[1:]):
        ax.text((pos_start + pos_end) / 2, y_pos, weekday.split('-')[0], ha='center',
                clip_on=False, transform=ax.get_xaxis_transform(), fontweight=fontweight, fontsize=fontsize)


def _generate_acquisition_time_labels(data_df: pd.DataFrame, language: str = 'pt') -> List[List[str]]:
    """
    generates acquisition time labels to be used as labels in a plot
    :param data_df: pandas.DataFrame containing the information on the "weekday", "session" (session time), and
    "Session" (session number). It is assumed that the DataFrame is already correctly sorted.
    :return: List of list containing the acquisition time labels
    """

    # copy the needed columns into a sub_df
    sub_df = data_df[[WEEKDAY_COL, SESSION_TIME_COL, SESSION_NUM_COL]].copy()

    # transform session times to HH:MM — HH:MM (start time - end time)
    sub_df[SESSION_TIME_COL] = sub_df[SESSION_TIME_COL].apply(_generate_start_end_time_string, args=(language,))

    # transform session num to Roman numerals
    sub_df[SESSION_NUM_COL] = sub_df[SESSION_NUM_COL].replace(ROMAN_NUMERALS)

    # list for holding the final labels
    labels = []

    # cycle over the weekdays
    for weekday, session_time_df in sub_df.groupby(WEEKDAY_COL, sort=False, observed=False):

        label_string = [f"{weekday}:"]

        # get the session and time
        session_times = session_time_df[SESSION_TIME_COL].to_list()
        session_nums = session_time_df[SESSION_NUM_COL].to_list()

        for session_num, session_time in zip(session_nums, session_times):

            label_string.append(f"  {session_num} - {session_time}")

        labels.append(label_string)

    return labels

def _generate_start_end_time_string(acq_time: str, language: str = 'pt')-> str:
    """
    Generates a start-end time string from the acq_time. It is assumed that the time is in the format `%H-%M-%S`.
    The resulting string is of the format `%H:%M — %H:%M` (start time — end time).
    :param acq_time: string containing the start time of an acquisition
    :return: tring containing the start and end time of an acquisition.
    """

    # check whether there is a time (in case there isn't, the string is 'missing')
    if acq_time.startswith("missing"):

        return HEART_RATE_MAPPING[NO_DATA_COL][language]

    else:

        # start time in format H
        # HH:MM - string
        start_str = acq_time[:5].replace("-", ":")

        # parse start time
        start_time = datetime.strptime(start_str, "%H:%M")

        # add 20 minutes
        end_time = start_time + timedelta(minutes=20)

        # format back to HH:MM
        end_str = end_time.strftime("%H:%M")

        # final label
        return f"{start_str} — {end_str}"


def _print_acquisition_time_labels(legends_to_print: List[List[str]], fig: Figure, fontsize: int=14) -> None:
    """
    prints the acquisition time labels contained in legends_to_print onto the figure
    :param legends_to_print: List containing the acquisition time labels
    :param fig: the figure onto which the labels should be printed
    :param fontsize: the font size
    :return: None
    """

    # set label positions
    x_text = 0.80
    y_pos = 0.95
    paragraph_offset = 0.03
    line_offset = 0.03

    for day_labels_list in legends_to_print:
        for label in day_labels_list:
            fig.text(
                x_text,
                y_pos,
                label,
                fontsize=fontsize,
                va="top",
                ha="left",
                fontweight="bold" if label.endswith(":") else "normal")

            # update y_pos
            y_pos -= line_offset

        # update y_pos
        y_pos -= paragraph_offset


def _set_y_limits(ax: Axes, data_df: pd.DataFrame) -> None:
    """
    Sets the y-axis limits based on the min/max values of the HR in data_df
    :param ax: matplotlib axes in which to set the y-axis limits
    :param data_df: pandas.DataFrame containing the HR data
    :return: None
    """

    # get the min and max values
    y_min = data_df["HR_BPM_stats.min"].min()
    y_max = data_df["HR_BPM_stats.max"].max()

    # check if there were min and max values registered
    if y_min and y_max:

        # Calculate padding: 15% of the range or minimum of 1.0
        y_pad = max(1.0, 0.15 * (y_max - y_min)) if y_max > y_min else 1.0

        # Set Y-axis limits with padding, ensuring lower limit is not negative
        ax.set_ylim(max(0, y_min - y_pad), y_max + y_pad)
    else:
        # If no valid data is available, set default limits from 0 to 100 BPM
        ax.set_ylim(0, 100)


def _draw_range_bars(ax: Axes, data_df: pd.DataFrame, weekdays: List[str], sessions: List[int]) -> List[Tuple[float, str]]:
    """
    draws HR range bars for each session contained in data_df. If no data was acquired for the session, a placeholder
    is drawn.
    :param ax: matplotlib axis
    :param data_df: pandas.DataFrame containing the HR data
    :param weekdays: the days on which the data was acquired
    :param sessions: the number of sessions performed for each day
    :return: list of tuples containing the (x-tick, label)
    """

    # init x-position to draw the bars
    x_pos = 1

    # init list to hold x-ticks and labels
    x_ticks_and_labels = []

    # cycle over the weekdays
    for day_num, weekday in enumerate(weekdays, start=1):

        # add displacement after the first day
        day_displacement = 0.8 if day_num > 1 else 0.0

        # update displacement
        x_pos += day_displacement

        # cycle over the sessions
        for session in sessions:

            # get the row
            plot_data = data_df[(data_df[WEEKDAY_COL] == weekday) & (data_df[SESSION_NUM_COL] == session)]

            if plot_data.empty:

                mn_plot = PLACEHOLDER_MIN
                mx_plot = PLACEHOLDER_MAX
                bar_col = PLACEHOLDER_COLOR
                circle_face = LIGHT_GRAY
                circle_edge = PLACEHOLDER_COLOR
                draw_values = False
            else:

                # get the values
                max_val = plot_data["HR_BPM_stats.max"].iloc[0]
                min_val = plot_data["HR_BPM_stats.min"].iloc[0]

                mn_plot = min_val
                mx_plot = max_val if max_val > min_val else min_val + 0.5
                bar_col = DEEP_RED
                circle_face = LIGHT_RED
                circle_edge = DEEP_RED
                draw_values = True

            # Bar
            ax.plot([x_pos, x_pos], [mn_plot, mx_plot], color=bar_col, linewidth=BAR_WIDTH_PTS, solid_capstyle='round',
                    zorder=2)

            # Circles
            ax.scatter([x_pos, x_pos], [mn_plot, mx_plot], s=BAR_WIDTH_PTS ** 2, facecolors=circle_face, edgecolors=circle_edge,
                       linewidths=0, zorder=3)

            if draw_values:
                # Numeric labels
                for y, value in [(mn_plot, mn_plot), (mx_plot, mx_plot)]:
                    ax.text(x_pos, y, f"{value:.0f}", ha='center', va='center', fontsize=9, fontweight='bold', zorder=4)
            else:
                # Vertical "Sem dados" label
                ax.text(x_pos, (mn_plot + mx_plot) / 2, "Sem dados", rotation=90, ha='center', va='center', fontsize=9,
                        fontweight=600,
                        color='white', zorder=4)

            # add the ticks and labels to the list
            x_ticks_and_labels.append((x_pos, ROMAN_NUMERALS[session]))

            # update x-position
            x_pos += 1



    return x_ticks_and_labels


def _style_plot(ax: Axes, xticks_and_labels: List[Tuple[float, str]], weekdays: List[str]) -> None:
    """
    apply styling to plot
    (1) adjust x-ticks and labels
    (2) add day labels
    (3) remove spines and add a grid
    :param ax: matplotlib axis
    :param xticks_and_labels:
    :return: list of tuples containing the (x-tick, label)
    """

    # get the ticks and the labels
    x_ticks, labels = zip(*xticks_and_labels)

    # set the x_ticks and labels
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(labels)

    # add weekday labels
    # calculate the center of the bars for each day
    day_centers = [(day_start + day_end) / 2 for day_start, day_end in zip(x_ticks[::4], x_ticks[3::4])]

    # calculate the y-position
    y_text = ax.get_ylim()[0] - 0.08 * (ax.get_ylim()[1] - ax.get_ylim()[0])

    # loop through the days and centers
    for x_text, weekday in zip(day_centers, weekdays):
        ax.text(x_text, y_text, weekday, ha='center', va='top', fontsize=14,)

    # set y label
    ax.set_ylabel("Ritmo Cardíaco (BPM)")

    # Enable horizontal grid lines for Y-axis
    ax.yaxis.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

    # Hide all spines
    for spine in ax.spines.values():
        spine.set_visible(False)
