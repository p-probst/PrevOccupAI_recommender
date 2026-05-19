# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pandas as pd
import ptitprince as pt
import matplotlib.pyplot as plt

from matplotlib.figure import Figure
from matplotlib.axes import Axes
from pathlib import Path
from typing import Tuple

from constants import WORK_TYPES, FO_COLOR, BO_COLOR


# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def plot_raincloud_by_day(metrics_df: pd.DataFrame, metric: str, fontsize: int=12) -> Tuple[Figure, Axes]:
    """

    :param metrics_df:
    :param metric:
    :param fontsize:
    :return:
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


