# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pandas as pd

from pathlib import Path

from constants import PALE_GREEN, YELLOW, RED, LIGHT_GRAY
# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
HR_NORMAL_KEY = 'Normal'
HR_POTENTIALLY_ELEVATED_KEY = 'Ligeiramente elevado'
HR_ELEVATED_KEY = 'Elevado'
NO_DATA = 'no data'

HEART_RATE_CLASS_ORDER = [HR_NORMAL_KEY, HR_POTENTIALLY_ELEVATED_KEY, HR_ELEVATED_KEY, NO_DATA]


HR_CLASS_COLORS = {
    HR_NORMAL_KEY: PALE_GREEN,                # green
    HR_POTENTIALLY_ELEVATED_KEY: YELLOW,  # orange
    HR_ELEVATED_KEY: RED,              # red
    NO_DATA: LIGHT_GRAY                 # light gray
}
# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def plot_hr_circular_distribution_by_worktype(metrics_df: pd.DataFrame, save_path: str | Path, show:bool = True) -> None:
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
    relevant_col_idx = [num for num, col in enumerate(metrics_df.columns) if col.startswith("HR_distributions")]

    # clean the column names
    metrics_df.columns = [col.split(".")[1] if col.startswith('HR_distributions') else col for col in
                          metrics_df.columns]

    # get the relevant cols
    relevant_cols = [metrics_df.columns[idx] for idx in relevant_col_idx]

    # cycle over the work_type
    for work_type, group_df in metrics_df.groupby("work_type", sort=False, observed=False):

        print('test')

        # calculate the mean per session
# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #