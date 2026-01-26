"""
function for creating report
"""
# imports
import os
import json
import os, shutil
import re
from pathlib import Path
from mdutils import Html
from mdutils.mdutils import MdUtils
from report_generator.report_sections.general.introduction import *
from report_generator.report_sections.questionnaires.introductory_section import *
from report_generator.report_sections.questionnaires.rosa import ROSA_DICT
from report_generator.report_sections.questionnaires.environment import ENVIRONMENT_DICT
from report_generator.report_sections.questionnaires.copsoq import COPSOQ_DICT, COPSOQ_EXPLAIN_KEY, MUEQ_EXPLAIN_KEY
from report_generator.report_sections.sensors.cml_sensors import CML_SENSORS_DICT
from report_generator.report_sections.general.common import SENSORS_INTRODUCTION
from report_generator.report_sections.sensors.sensor_timeline import SENSOR_TIMELINE_DICT
from report_generator.report_sections.sensors.noise import NOISE_DICT
from constants import PT, INTRODUCTION_KEY, RISK_RULE_KEY, PLOT_EXPLAIN_KEY
import recommender as recommender


# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #


def generate_report(report_folder_path, subject_id, plots_path, oh_profiles_path):

    # generate file with cover
    mdFile = _generate_file_and_cover(report_folder_path, subject_id)

    # introduction
    _generate_introduction_section(mdFile)

    work_type = 'CML'

    # get work type from OH profile
    for oh_profile_path in os.listdir(oh_profiles_path):

        if oh_profile_path.split('_')[0] == str(subject_id):

            #  ---------------------  OH profile -------------------------------------
            with open(os.path.join(oh_profiles_path, oh_profile_path), "r", encoding="utf-8") as json_file:
                oh_profile = json.load(json_file)

            # get work type
            work_type = oh_profile['meta_data']['work_type']

    # ------------------------------------------recommender ------------------------------------------#

    # load the OH profile and the recommendation system json
    with open(Path.cwd() / "recommender/recommendations.json", "r", encoding="utf-8") as file:

        recommendation_system = json.load(file)

    # questionnaires
    _generate_questionnaires_section(mdFile, subject_id, plots_path, work_type)
    mdFile.new_line(' \pagebreak ')
    mdFile.write("\n")

    # introduction title
    mdFile.new_header(level=1, title="Resultados das suas aquisições")

    # write paragraphs
    mdFile.new_paragraph(SENSORS_INTRODUCTION)
    mdFile.write("\n")

    # generate environmental sensors
    _generate_environmental_sensors_section(mdFile, subject_id, plots_path)

    # sensor timeline
    _generate_sensor_timeline_section(mdFile, subject_id, plots_path)

    # noise
    _generate_noise_section(mdFile, subject_id, plots_path, oh_profile, oh_profiles_path, recommendation_system)

    # generate pdf


    template_path = r"C:\Users\srale\PycharmProjects\PrevOccupAI_recommender\report_generator\eisvogel.latex"
    header_path = r"C:\Users\srale\PycharmProjects\PrevOccupAI_recommender\report_generator\header.tex"

    md_path = os.path.join(report_folder_path, f"{subject_id}_report.md")
    pdf_path = os.path.join(report_folder_path, f"{subject_id}_report.pdf")

    mdFile.create_md_file()

    os.system(f'pandoc --verbose '
        f'--template="{template_path}" '
        f'-H "{header_path}" '
        f'-V geometry:left=0.8in,right=0.8in,top=1.0in,bottom=1.0in '
        f'"{md_path}" '
        f'--pdf-engine=pdflatex '
        f'-o "{pdf_path}"'
    )
    print("report done")

    # sensors


# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #

def _generate_file_and_cover(report_folder_path, subject_id):

    # create new file
    mdFile = MdUtils(file_name=os.path.join(report_folder_path, f'{subject_id}_report'))

    return mdFile


def _generate_introduction_section(mdFile, introduction_dict=INTRO_DICT[PT]):

    # introduction title
    mdFile.new_header(level=1, title=introduction_dict[SECTION_0])

    # write paragraphs
    mdFile.new_paragraph(introduction_dict[SECTION_1])
    mdFile.write("\n")
    mdFile.new_paragraph(introduction_dict[SECTION_2])
    mdFile.write("\n")
    mdFile.new_paragraph(introduction_dict[SECTION_3])
    mdFile.write("\n")
    mdFile.new_paragraph(introduction_dict[SECTION_4])
    mdFile.write("\n")
    mdFile.new_paragraph(introduction_dict[SECTION_5])
    mdFile.write("\n")

    # bullet points
    mdFile.new_paragraph(introduction_dict[SECTION_6])
    mdFile.new_paragraph(introduction_dict[SECTION_7])
    mdFile.new_paragraph(introduction_dict[SECTION_8])
    mdFile.new_paragraph(introduction_dict[SECTION_9])
    mdFile.write("\n")

    # continue text
    mdFile.new_paragraph(introduction_dict[SECTION_10])
    mdFile.write("\n")
    mdFile.new_paragraph(introduction_dict[SECTION_11])
    mdFile.write("\n")
    mdFile.new_paragraph(introduction_dict[SECTION_12])
    mdFile.write("\n")
    mdFile.new_paragraph(introduction_dict[SECTION_13])
    mdFile.write("\n")
    mdFile.new_line(' \pagebreak ')
    mdFile.write("\n")


def _generate_noise_section(mdFile, subject_id, plots_path, oh_profile, oh_profiles_path, recommendation_system, noise_dict=NOISE_DICT[PT]):

    # get noise recommender

    # load noise risk subjects
    noise_risk_subjects_df = recommender.generate_noise_csv(Path.cwd(), oh_profiles_path)

    # ger noise recommendations
    noise_exposure_recommendations = recommender.get_noise_exposure_recommendations(noise_risk_subjects_df, subject_id, recommendation_system)
    noise_continuous_recommendations = recommender.get_continuous_noise_recommendations(oh_profile, recommendation_system, noise_level_label=['Ruído incomodativo','Ruído elevado'])

    mdFile.write("\n")
    # introduction title
    mdFile.new_header(level=1, title=noise_dict[INTRODUCTION_KEY][0])

    # write intro
    mdFile.new_paragraph(noise_dict[INTRODUCTION_KEY][1])
    mdFile.write("\n")
    mdFile.new_paragraph(noise_dict[INTRODUCTION_KEY][2])
    mdFile.new_paragraph(noise_dict[INTRODUCTION_KEY][3])
    mdFile.new_paragraph(noise_dict[INTRODUCTION_KEY][4])
    mdFile.new_paragraph(noise_dict[INTRODUCTION_KEY][5])
    mdFile.write("\n")
    # describe plot
    mdFile.new_paragraph(noise_dict[PLOT_EXPLAIN_KEY][0])

    _add_centered_image(mdFile,
                        os.path.join(plots_path, str(subject_id), 'noise_plots', f'{subject_id}_noise_timeline.png'),
                        caption=None, max_width=1, max_height=0.5)

    mdFile.write("\n")
    mdFile.new_paragraph(noise_dict[RISK_RULE_KEY][0])
    #
    # for i, rule in enumerate(noise_continuous_recommendations['rule']):
    #
    #     mdFile.new_paragraph(f"- Regra {i+1}. {noise_continuous_recommendations['rule']}")
    #     mdFile.write("\n")

    mdFile.new_paragraph(f"Foram det")


    mdFile.write("\n")

def _generate_sensor_timeline_section(mdFile, subject_id, plots_path, timeline_dict = SENSOR_TIMELINE_DICT[PT]):

    mdFile.write("\n")
    # introduction title
    mdFile.new_header(level=1, title=timeline_dict[INTRODUCTION_KEY][0])

    # write intro
    mdFile.new_paragraph(timeline_dict[INTRODUCTION_KEY][1])
    mdFile.write("\n")
    mdFile.new_paragraph(timeline_dict[INTRODUCTION_KEY][2])
    mdFile.new_paragraph(timeline_dict[INTRODUCTION_KEY][3])
    mdFile.new_paragraph(timeline_dict[INTRODUCTION_KEY][4])
    mdFile.write("\n")
    # describe plot
    mdFile.new_paragraph(timeline_dict[PLOT_EXPLAIN_KEY][0])
    mdFile.write("\n")

    _add_centered_image(mdFile,
                        os.path.join(plots_path, str(subject_id) , f'{subject_id}_sensor_timeline_plot.png'),
                        caption=None, max_width=1, max_height=0.5)


def _generate_environmental_sensors_section(mdFile, subject_id, plots_path, cml_dict = CML_SENSORS_DICT[PT]):
    mdFile.write("\n")
    # introduction title
    mdFile.new_header(level=1, title=cml_dict[INTRODUCTION_KEY][0])

    # write intro
    mdFile.new_paragraph(cml_dict[INTRODUCTION_KEY][1])
    mdFile.write("\n")
    mdFile.new_paragraph(cml_dict[INTRODUCTION_KEY][2])
    mdFile.new_paragraph(cml_dict[INTRODUCTION_KEY][3])
    mdFile.new_paragraph(cml_dict[INTRODUCTION_KEY][4])
    mdFile.new_paragraph(cml_dict[INTRODUCTION_KEY][5])
    mdFile.new_paragraph(cml_dict[INTRODUCTION_KEY][6])
    mdFile.write("\n")

    # describe plot
    mdFile.new_paragraph(cml_dict[PLOT_EXPLAIN_KEY][0])
    mdFile.write("\n")

    # generate path to the folder containing the environment plots
    env_plots_path = os.path.join(plots_path, str(subject_id), 'environment')

    mdFile.write("\n")
    _add_centered_image(mdFile,
                        os.path.join(env_plots_path, f'{subject_id}_CO2_CO_COV_plot.png'),
                        caption=None, max_width=1, max_height=0.3)

    mdFile.write("\n")

    # generate subplot temperature, humidity and illuminance
    temp_path = _tex_escape_path(os.path.join(env_plots_path, f"{subject_id}_Temperature_plot.png"))
    hum_path = _tex_escape_path(os.path.join(env_plots_path, f"{subject_id}_Humidity_plot.png"))
    illu_path = _tex_escape_path(os.path.join(env_plots_path, f"{subject_id}_Illuminance_plot.png"))

    _add_three_panel_figure(mdFile, [temp_path, hum_path, illu_path])

    mdFile.write("\n")
    _add_centered_image(mdFile,
                        os.path.join(env_plots_path, f'{subject_id}_PM10_PM025_plot.png'),
                        caption=None, max_width=1, max_height=0.2)



def _generate_questionnaires_section(mdFile, subject_id, plots_path, work_type, intro_dict=QUEST_INTRO_DICT[PT], rosa_dict=ROSA_DICT[PT],
                                     env_dict=ENVIRONMENT_DICT[PT], psycho_dict=COPSOQ_DICT[PT]):

    # get work type full string
    if work_type == 'FO':
        work_type_full = "front office"

    else:
        work_type_full = "back office"

    # write introduction
    mdFile.new_header(level=1, title=intro_dict[SECTION_0])

    # write paragraphs
    mdFile.new_paragraph(intro_dict[SECTION_1])
    mdFile.write("\n")
    mdFile.new_paragraph(intro_dict[SECTION_2])
    mdFile.write("\n")

    # --------------------------------------- biomechanical questionnaire - ROSA --------------------------------------#
    # intro
    mdFile.new_header(level=2, title=rosa_dict[INTRODUCTION_KEY][0])
    mdFile.new_paragraph(rosa_dict[INTRODUCTION_KEY][1])
    mdFile.write("\n")

    # describe plots
    mdFile.new_paragraph(rosa_dict[PLOT_EXPLAIN_KEY][0])
    mdFile.write("\n")

    # add table
    items_rosa = [s for s in rosa_dict[PLOT_EXPLAIN_KEY] if re.match(r"^\d+\.\s", s)]
    _add_two_column_table(mdFile, items_rosa, header_left="Dimensão", header_right="Dimensão", text_align="left")

    mdFile.write("\n")

    # add rosa plot
    _add_centered_image(mdFile, os.path.join(plots_path, str(subject_id), 'questionnaire_plots', f'Rosa_plot_{subject_id}.png'),
                        caption='Resultados pessoais da avaliação Biomecânica .')
    # describe risk
    mdFile.new_paragraph(rosa_dict[RISK_RULE_KEY][0])
    mdFile.write("\n")

    # TODO - RECOMMENDATIONS - MAKE SET OUT OF RECOMMENDATIONS LIST
    # --------------------------------------- environmental questionnaire --------------------------------------#
    # intro
    mdFile.new_header(level=2, title=env_dict[INTRODUCTION_KEY][0])
    mdFile.new_paragraph(env_dict[INTRODUCTION_KEY][1])
    mdFile.write("\n")

    # describe plots
    mdFile.new_paragraph(env_dict[PLOT_EXPLAIN_KEY][0])
    mdFile.write("\n")

    # add table with description
    items_env = [s for s in env_dict[PLOT_EXPLAIN_KEY] if re.match(r"^\d+\.\s", s)]
    _add_two_column_table(mdFile, items_env, header_left="Dimensão", header_right="Dimensão", text_align="left")

    _add_centered_image(mdFile,os.path.join(plots_path, str(subject_id), "questionnaire_plots", f"environment_plot_{subject_id}.png"),
        caption="Resultados pessoais da avaliação ambiental."
    )

    # describe risk
    mdFile.new_paragraph(env_dict[RISK_RULE_KEY][0])
    mdFile.write("\n")

    # TODO RECOMMENDATIONS
    # --------------------------------------- PSYCHOSOCIAL (COPSOQ AND MUEQ) --------------------------------------#
    # intro
    mdFile.new_header(level=2, title=psycho_dict[INTRODUCTION_KEY][0])
    mdFile.new_paragraph(psycho_dict[INTRODUCTION_KEY][1])
    mdFile.write("\n")

    # describe plots
    mdFile.new_paragraph(psycho_dict[COPSOQ_EXPLAIN_KEY][0])
    mdFile.write("\n")

    # describe plots: only PLOT_EXPLAIN_1_1_PT ... PLOT_EXPLAIN_1_29_PT
    # --- COPSOQ (only 1_1 to 1_29) in a 2-column table ---
    items_copsoq = [s for s in psycho_dict[COPSOQ_EXPLAIN_KEY] if re.match(r"^\d+\.\s", s)]
    _add_two_column_table(mdFile, items_copsoq, header_left="Dimensão", header_right="Dimensão", text_align="left")

    mdFile.write("\n")

    # add plot --------------- COPSOQ population ------------------
    _add_centered_image(mdFile,
                        os.path.join(plots_path, str(subject_id), 'questionnaire_plots', f'copsoq_population.png'),
                        caption='Resultados do questionário COPSOQ: média de toda a população em estudo')
    # describe risk
    mdFile.write("\n")

    # show copsoq worktype plot
    # add plot -------------------COPSOQ work type -------------------------
    _add_centered_image(mdFile,
                        os.path.join(plots_path, str(subject_id), 'questionnaire_plots', f'copsoq_{work_type}.png'),
                        caption=f'Resultados do questionário COPSOQ: média de trabalhadores de {work_type_full}')
    mdFile.write("\n")
    mdFile.new_line(' \pagebreak ')

    # describe plots
    mdFile.new_paragraph(psycho_dict[MUEQ_EXPLAIN_KEY][0])
    mdFile.write("\n")

    # add description
    items_mueq = [s for s in psycho_dict[MUEQ_EXPLAIN_KEY] if re.match(r"^\d+\.\s", s)]
    _add_two_column_table(mdFile, items_mueq, header_left="Dimensão", header_right="Dimensão", text_align="left")
    mdFile.write("\n")

    # show ------------------------------ MUEQ population
    _add_centered_image(mdFile,
                        os.path.join(plots_path, str(subject_id), 'questionnaire_plots', f'mueq_population.png'),
                        caption='Resultados do questionário MUEQ: média de toda a população em estudo')
    mdFile.write("\n")

    # show  ----------------------------- MUEQ worktype
    _add_centered_image(mdFile,
                        os.path.join(plots_path, str(subject_id), 'questionnaire_plots', f'mueq_{work_type}.png'),
                        caption=f'Resultados do questionário MUEQ: média de trabalhadores de {work_type_full}')

    mdFile.write("\n")


def _tex_escape_path(p: str) -> str:
    p = p.replace("\\", "/")
    return p


def _add_centered_image(mdFile, img_path, max_width=1, max_height=0.1, caption=None):
    img_path = _tex_escape_path(img_path)

    mdFile.write("\n")
    mdFile.write(r"\begin{center}" + "\n")
    mdFile.write(
        rf"\includegraphics[width={max_width}\linewidth,height={max_height}\textheight,keepaspectratio]{{{img_path}}}" + "\n"
    )
    if caption:
        mdFile.write(rf"\par\vspace{{0.3em}}\small {caption}" + "\n")
    mdFile.write(r"\end{center}" + "\n\n")


def _add_two_column_table(mdFile, items, header_left="Dimensão", header_right="Dimensão", text_align="left"):
    """
    Create a 2-column mdutils table from a list of strings, splitting items into two columns
    (left column first, then right column). Pads with "" if needed.

    Parameters
    ----------
    mdFile : MdUtils instance
        Your mdutils file object.
    items : list[str]
        Items to place in the table.
    header_left : str
        Header for column 1.
    header_right : str
        Header for column 2.
    text_align : str
        mdutils text alignment (e.g., 'left', 'center', 'right').
    """
    cols = 2
    data_rows = (len(items) + cols - 1) // cols  # ceil(len/2)
    rows = data_rows + 1  # +1 header row

    # flat list with exactly cols*rows cells
    table_text = [header_left, header_right]

    for r in range(data_rows):
        left_idx = r
        right_idx = r + data_rows

        left = items[left_idx] if left_idx < len(items) else ""
        right = items[right_idx] if right_idx < len(items) else ""

        table_text.extend([left, right])

    mdFile.new_table(columns=cols, rows=rows, text=table_text, text_align=text_align)


def _add_three_panel_figure(mdFile, img_paths, caption=None, subcaptions=None, height="4.5 cm"):
    """
    3-panel LaTeX figure with consistent panel height and centered subcaptions.
    height: string with LaTeX unit (e.g., "4cm", "45mm", "0.25\\textheight")
    """
    assert len(img_paths) == 3
    if subcaptions is not None:
        assert len(subcaptions) == 3

    p1, p2, p3 = [p.replace("\\", "/") for p in img_paths]
    sc1, sc2, sc3 = (subcaptions if subcaptions else ("", "", ""))

    mdFile.write("\n")
    mdFile.write(r"\begin{figure}[!ht]" + "\n")
    mdFile.write(r"\centering" + "\n")
    mdFile.write(r"\captionsetup[subfigure]{justification=centering}" + "\n")  # center subcaptions

    widths = ["0.3025\\linewidth", "0.315\\linewidth", "0.3025\\linewidth"]

    for i, ((p, sc), w) in enumerate(zip([(p1, sc1), (p2, sc2), (p3, sc3)], widths)):
        mdFile.write(rf"\begin{{subfigure}}[t]{{{w}}}" + "\n")
        mdFile.write(r"\centering" + "\n")
        mdFile.write(rf"\includegraphics[width=\linewidth,height={height},keepaspectratio]{{{p}}}" + "\n")
        if sc:
            mdFile.write(rf"\caption{{{sc}}}" + "\n")
        mdFile.write(r"\end{subfigure}" + "\n")
        if i < 2:
            mdFile.write(r"\hfill" + "\n")

    if caption:
        mdFile.write(rf"\caption{{{caption}}}" + "\n")

    mdFile.write(r"\end{figure}" + "\n")
    mdFile.write("\n")


