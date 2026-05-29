# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pandas as pd
import matplotlib.pyplot as plt
import math
import os
import numpy as np

from pathlib import Path
from matplotlib.lines import Line2D

# internal imports
from constants import FILE_FORMAT, WORK_TYPE_COLORS, WEEKDAY_COL, WORKTYPE_COL, SUBJECT_ID_COL, DATE_COL

# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
# Likert scale (5-point)

LIKERT_SCALE = {
    1: "Strongly disagree",
    2: "Disagree",
    3: "Neutral",
    4: "Agree",
    5: "Strongly agree"
}

LIKERT_VALUES = list(LIKERT_SCALE.keys())


# Language mapping
LANG_MAPPING = {
    "eng": {
        "likert": LIKERT_SCALE,
        "locale": "en_US"
    },
    "pt": {
        "likert": {
            1: "Discordo total",
            2: "Discordo",
            3: "Neutro",
            4: "Concordo",
            5: "Concordo total"
        },
        "locale": "pt_PT"
    }
}

QUESTION_LABEL_MAPPING = {
    "pt": {
        "focus_and_mental_strain": "Concentração e esforço mental",
        "rushed_and_under_pressure": "Apressado e sobre pressão",
        "frequent_interruptions": "Interrupções frequentes",
        "more_effort_than_resources": "Mais esforço do que recursos",
        "heavy_workload": "Carga de trabalho elevada"
    },
    "eng": {
        # optional, if you want cleaner English labels
        "focus_and_mental_strain": "Focus and mental strain",
        "rushed_and_under_pressure": "Rushed and under pressure",
        "frequent_interruptions": "Frequent interruptions",
        "more_effort_than_resources": "More effort than resources",
        "heavy_workload": "Heavy workload"
    }
}

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def plot_workload_by_worktype(metrics_df: pd.DataFrame, save_path: str | Path, language: str = "pt", add_error_bars: bool = True) -> None:
    """

    :param metrics_df:
    :param save_path:
    :param language:
    :param color:
    :param add_error_bars:
    :return:
    """

    # check for work_type column
    if WORKTYPE_COL not in metrics_df.columns:
        raise KeyError(f"Input CSV must contain a {WORKTYPE_COL} column.")

    # get the labels according to the language
    lang_cfg = LANG_MAPPING.get(language, LANG_MAPPING["eng"])
    locale = lang_cfg["locale"]
    likert_labels = lang_cfg["likert"]

    # remove the "open_answer" column
    metrics_df = metrics_df.drop(columns=["open_question"])

    # filter out columns that are not part of the workload questionnaire
    relevant_cols = [c for c in metrics_df.columns if c not in (SUBJECT_ID_COL, DATE_COL, WORKTYPE_COL, WEEKDAY_COL)]

    # cycle over the work_type
    for work_type, group_df in metrics_df.groupby(WORKTYPE_COL):

        # generate the plot
        fig, axes = plt.subplots(1, len(metrics_df[WEEKDAY_COL].unique()), figsize=(18, 6), sharey=True)

        # flatten axes for easier
        axes = axes.flatten()
        x_labels = []

        for ax, (weekday, day_df) in zip(axes, group_df.groupby(WEEKDAY_COL, sort=False, observed=False)):

            # calculate the mean of the work type
            work_type_mean = day_df[relevant_cols].mean(axis=0).round(2)
            work_type_std = day_df[relevant_cols].std(axis=0).round(2)

            # Remove spines (keep only bottom)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_visible(False)

            # init lists for holding labels and positions
            x_positions = []
            x_labels = []

            # cycle over the column names
            for pos, (q_item, value) in enumerate(work_type_mean.items()):

                x_positions.append(pos)
                x_labels.append(q_item)

                # Thick horizontal line instead of bar
                ax.hlines(
                    y=value,
                    xmin=pos - 0.3,
                    xmax=pos + 0.3,
                    linewidth=7,
                    color=WORK_TYPE_COLORS[str(work_type)]
                )

                # Add error bar (whiskers)
                if add_error_bars:

                    # get the corresponding std value
                    std_value = work_type_std[q_item]
                    ax.errorbar(
                        x=pos,
                        y=value,
                        yerr=std_value,
                        fmt='none',  # no marker
                        ecolor=WORK_TYPE_COLORS[str(work_type)],
                        elinewidth=2,
                        capsize=5,
                        capthick=2
                    )


            ax.set_xticks(x_positions)
            ax.set_xticklabels([str(i + 1) for i in x_positions], fontsize=18)
            ax.set_title(weekday, fontsize=18)

            ax.set_ylim(0.5, 5.5)
            ax.set_yticks(LIKERT_VALUES)
            ax.set_yticklabels([likert_labels[v] for v in LIKERT_VALUES], fontsize=18)

            ax.grid(
                axis="y",
                linestyle="--",
                linewidth=0.8,
                alpha=0.7
            )

            # transform legend labels
        if x_labels:
            x_labels = [_format_question_key(label, language) for label in x_labels]

        legend_handles = [
            Line2D(
                [], [],
                linestyle=None,
                label=rf"$\bf{{{i + 1}}}$ – {key}"
            )
            for i, key in enumerate(x_labels)
        ]

        # define number of columns
        n_col = 3

        # reorder the legends to be read from left to right
        legend_handles_rowwise = _reorder_legend_rowwise(legend_handles, n_col)

        fig.legend(
            handles=legend_handles_rowwise,
            loc="lower center",
            ncols=3,
            frameon=False,
            handlelength=0,
            handletextpad=0.4,
            columnspacing=1.5,
            fontsize=16,
            bbox_to_anchor=(0.5, -0.01)
        )

        # add suptitle
        # fig.suptitle("Resultados dos Questionários da Carga de Trabalho")
        fig.subplots_adjust(
            left=0.125,
            right=0.99,
            top=0.90,
            bottom=0.22,
            wspace=0.10
        )

        # create file name
        file_name = f'carga_de_trabalho_{work_type}{FILE_FORMAT}'

        # save the plot
        handle_plot(save_dir=save_path, filename=file_name, save=True)



# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #
def _format_question_key(key: str, language: str) -> str:
    """
    Convert a question key to a human-readable label:
    - replace underscores with spaces
    - apply language translation if available

    :param key: Original dictionary key
    :param language: 'pt' or 'eng'
    :return: Formatted question label
    """
    if key in QUESTION_LABEL_MAPPING.get(language, {}):
        return QUESTION_LABEL_MAPPING[language][key]

    # fallback: replace underscores and capitalize first letter
    return key.replace("_", " ").capitalize()

def _reorder_legend_rowwise(handles, ncol):
    """
    reorders legends so that they can be read from left to right.
    :param handles:
    :param ncol:
    :return:
    """
    n = len(handles)
    nrow = int(math.ceil(n / ncol))

    # Pad with None so reshape works
    padded = handles + [None] * (nrow * ncol - n)

    arr = np.array(padded, dtype=object).reshape(nrow, ncol)

    # Matplotlib fills column-wise → undo that
    rowwise = arr.T.flatten()

    # Remove padding
    return [h for h in rowwise if h is not None]

def handle_plot(save_dir:str, save=True, filename="plot.png")-> None:
    """
    Handles the display and saving of matplotlib plots based on user-defined options.

    This utility function centralizes logic for whether a plot should be shown on screen,
    saved to disk, or both. If saving is enabled, the function ensures the output directory exists
    and stores the plot using the specified filename.

    :param save_dir: String specifying the directory path where the plot should be saved
                     if `save=True`. The directory is created if it doesn't exist.

    :param save: Boolean indicating whether to save the plot as an image file. Default is False.


    :param filename: String specifying the name of the image file to save, including the extension
                     (e.g., "my_plot.png"). Only relevant if `save=True`.
                     Default is "plot.png".
    :return: None
    """
    if save:
        print(f"Saving plot to: {os.path.join(save_dir, filename)}")  # <--- debug

        # Create the output directory if it doesn't exist
        os.makedirs(save_dir, exist_ok=True)
        # Save the current figure to the specified path
        plt.savefig(os.path.join(save_dir, filename))

        plt.close()