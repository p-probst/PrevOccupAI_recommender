"""
function for creating report
"""
# imports
import os
import json
import os, shutil
import re
from typing import List, Dict, Union
from datetime import datetime
from pathlib import Path
from mdutils.mdutils import MdUtils

from report_generator.report_sections.general.references import REFS_LIST, LINKS_LIST
from report_generator.report_sections.general.conclusion import CONCLUSION_DICT
from report_generator.report_sections.general.introduction import *
from report_generator.report_sections.questionnaires.introductory_section import *
from report_generator.report_sections.questionnaires.rosa import ROSA_DICT
from report_generator.report_sections.questionnaires.environment import ENVIRONMENT_DICT
from report_generator.report_sections.questionnaires.copsoq import COPSOQ_DICT, COPSOQ_EXPLAIN_KEY, MUEQ_EXPLAIN_KEY
from report_generator.report_sections.sensors.cml_sensors import CML_SENSORS_DICT
from report_generator.report_sections.general.common import SENSORS_INTRODUCTION
from report_generator.report_sections.sensors.sensor_timeline import SENSOR_TIMELINE_DICT
from report_generator.report_sections.sensors.noise import NOISE_DICT
from report_generator.report_sections.sensors.human_activities import HAR_DICT
from report_generator.report_sections.sensors.wrist_movements import WRIST_MOVEMENT_DICT
from report_generator.report_sections.sensors.heart_rate import HEART_RATE_DICT
from report_generator.report_sections.sensors.emg import EMG_DICT
from report_generator.report_sections.questionnaires.pain import PAIN_DICT
from report_generator.report_sections.questionnaires.workload import WORKLOAD_DICT
from report_generator.report_sections.sensors.posture import POSTURE_DICT
from constants import PT, INTRODUCTION_KEY, RISK_RULE_KEY, PLOT_EXPLAIN_KEY, RECOMMENDATIONS_KEY, NO_RECOMMENDATIONS, \
    USER
import recommender as recommender


# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def generate_report(report_folder_path, subject_id, plots_path, emg_plots_path, oh_profiles_path):

    # generate file with cover
    mdFile = _generate_file_and_cover(report_folder_path, subject_id)



    # init work type
    work_type = ''

    mdFile.new_line(' \pagebreak ')
    mdFile.write("\n")

    # ------------------------ Section: Introduction ------------------------ #
    _generate_introduction_section(mdFile)
    mdFile.new_line(' \pagebreak ')
    mdFile.write("\n")

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


    # ------------------------ Section: Questionnaires ------------------------ #
    _generate_questionnaires_section(mdFile, subject_id, plots_path, oh_profiles_path, recommendation_system, work_type)

    mdFile.write("\n")
    _generate_daily_questionnaire(mdFile, subject_id, plots_path)
    mdFile.new_line(' \pagebreak ')
    mdFile.write("\n")


    # ------------------------ Section: Sensors ------------------------ #
    mdFile.new_header(level=1, title="Resultados das suas aquisições")
    mdFile.write("\n")
    # write paragraphs
    mdFile.new_paragraph(SENSORS_INTRODUCTION)
    mdFile.write("\n")

    # ------------------------ Sub-Section: Environmental Sensors (single recording) ------------------------ #
    _generate_environmental_sensors_section(mdFile, subject_id, plots_path)
    mdFile.new_line(' \pagebreak ')

    # ------------------------ Sub-Section: Sensor Timeline (daily recording) ------------------------ #
    _generate_sensor_timeline_section(mdFile, subject_id, plots_path)

    # ------------------------ Sub-Section: Noise Sensor (daily recording) ------------------------ #
    _generate_noise_section(mdFile, subject_id, plots_path, oh_profile, oh_profiles_path, recommendation_system)
    mdFile.new_line(' \pagebreak ')

    # ------------------------ Sub-Section: Movement Sensors: Human Activities (daily recording) ------------------------ #
    _generate_human_activities_section(mdFile, subject_id,oh_profile, oh_profiles_path, plots_path, recommendation_system)
    mdFile.new_line(' \pagebreak ')

    # ------------------------ Sub-Section: Movement Sensors: Posture (daily recording) ------------------------ #
    _generate_posture_section(mdFile, subject_id, oh_profiles_path, plots_path, recommendation_system)
    mdFile.new_line(' \pagebreak ')

    # ------------------------ Sub-Section: Movement Sensors: Wrist (daily recording) ------------------------ #
    _generate_wrist_section(mdFile, subject_id, plots_path)
    mdFile.new_line(' \pagebreak ')

    # ------------------------ Sub-Section: Hear Rate Sensor (daily recording) ------------------------ #
    _generate_heart_rate_section(mdFile, subject_id, oh_profile, oh_profiles_path, plots_path, recommendation_system)
    mdFile.new_line(' \pagebreak ')

    # ------------------------ Sub-Section: EMG Sensor (daily recording) ------------------------ #
    _generate_emg_sec(mdFile, subject_id, oh_profile, oh_profiles_path, emg_plots_path, recommendation_system)

    # ------------------------ Section: Summary ------------------------ #
    # TODO: generate table with all the measured metrics, the risk rules, the instances of occurrences, the days, and the recommendations

    # ------------------------ Section: Conclusion ------------------------ #
    _generate_conclusion_section(mdFile, conclusion_dict=CONCLUSION_DICT[PT])
    mdFile.new_line(' \pagebreak ')

    # ------------------------ Section: References ------------------------ #
    _generate_references(mdFile)

    # generate pdf
    template_path = fr"C:\Users\{USER}\PycharmProjects\PrevOccupAI_recommender\report_generator\eisvogel.latex"
    header_path = fr"C:\Users\{USER}\PycharmProjects\PrevOccupAI_recommender\report_generator\header.tex"

    md_path = os.path.join(report_folder_path, f"{subject_id}_report.md")
    pdf_path = os.path.join(report_folder_path, f"{subject_id}_report.pdf")

    mdFile.create_md_file()

    os.system(
        f'pandoc --verbose '
        f'--number-sections '
        f'--toc --toc-depth=2 '
        f'-V toc-title="Índice" '
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

    # YAML metadata block — MUST be first
    mdFile.write(
        "---\n"
        "titlepage: true\n"
        "titlepage-background: \"report_cover_slide.pdf\"\n"
        "titlepage-rule-height: 0\n"
        "---\n\n"
    )

    return mdFile


def _generate_introduction_section(mdFile, introduction_dict=INTRO_DICT[PT]):

    # introduction title
    mdFile.new_header(level=1, title=introduction_dict[SECTION_0])

    # write paragraphs
    mdFile.new_header(level=2, title="Agradecimentos")
    mdFile.new_paragraph(introduction_dict[SECTION_1])
    mdFile.write("\n")

    mdFile.new_header(level=2, title="Contexto")
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


def _generate_posture_section(mdFile, subject_id, oh_profiles_path, plots_path, recommendation_system, posture_dict=POSTURE_DICT[PT]):

    # load posture data
    posture_subject_data_df = recommender.generate_posture_csv(Path.cwd(), oh_profiles_path)

    # ------- get posture recommendations --------- #
    posture_recommendations = recommender.get_postural_displacement_recommendation(posture_subject_data_df, subject_id,
                                                                                   recommendation_system)

    mdFile.write("\n")
    # introduction title
    mdFile.new_header(level=2, title=posture_dict[INTRODUCTION_KEY][0])

    # write intro
    mdFile.new_paragraph(posture_dict[INTRODUCTION_KEY][1])
    mdFile.write("\n")
    mdFile.new_paragraph(posture_dict[INTRODUCTION_KEY][2])
    mdFile.write("\n")
    mdFile.new_paragraph(posture_dict[INTRODUCTION_KEY][3])
    mdFile.write("\n")
    mdFile.new_paragraph(posture_dict[INTRODUCTION_KEY][4])
    mdFile.write("\n")
    mdFile.new_paragraph(posture_dict[INTRODUCTION_KEY][5])
    mdFile.write("\n")
    mdFile.new_paragraph(posture_dict[INTRODUCTION_KEY][6])
    mdFile.write("\n")

    # explain plot
    mdFile.new_paragraph(posture_dict[PLOT_EXPLAIN_KEY][0])
    mdFile.write("\n")

    # bullet points
    mdFile.new_paragraph(posture_dict[PLOT_EXPLAIN_KEY][1])
    mdFile.new_paragraph(posture_dict[PLOT_EXPLAIN_KEY][2])
    mdFile.new_paragraph(posture_dict[PLOT_EXPLAIN_KEY][3])
    mdFile.write("\n")


    # show plot - vista de costas
    _add_centered_image(mdFile,
                        os.path.join(plots_path, str(subject_id), 'posture_plots', f'{subject_id}_posture_views_grid.png'),
                        caption=None, max_width=1, max_height=0.99)



    # # vista de lado
    # _add_centered_image(mdFile,
    #                     os.path.join(plots_path, str(subject_id), 'posture_plots', f'{subject_id}_Vista Lateral.png'),
    #                     caption=None, max_width=1, max_height=0.99)
    #
    #
    #
    #
    # # vista superior
    # _add_centered_image(mdFile,
    #                     os.path.join(plots_path, str(subject_id), 'posture_plots', f'{subject_id}_Vista Superior.png'),
    #                     caption=None, max_width=1, max_height=0.99)

    # risk section
    mdFile.new_paragraph(posture_dict[RISK_RULE_KEY][0])
    _add_rules_and_risk_occurrences(mdFile, posture_recommendations)
    mdFile.write("\n")

    # show recommendations
    _add_recommendation_section(mdFile, posture_recommendations[RECOMMENDATIONS_KEY])
    mdFile.write("\n")


def _generate_emg_sec(mdFile, subject_id, oh_profile, oh_profiles_path, plots_path, recommendation_system, emg_dict=EMG_DICT[PT]):

    # load EMG data
    emg_subject_data_df = recommender.generate_emg_csv(Path.cwd(), oh_profiles_path)

    # ------- get emg recommendations --------- #
    emg_recommendations_above_high = recommender.get_emg_recommendations(emg_subject_data_df, oh_profile, subject_id,
                                                          'high_for_you_pct', 30.0, 2,
                                                          recommendation_system)

    emg_recommendations_high = recommender.get_emg_recommendations(emg_subject_data_df, oh_profile, subject_id,
                                                                   'typical_high_pct', 25.0, 3,
                                                                   recommendation_system)

    mdFile.write("\n")
    # introduction title
    mdFile.new_header(level=2, title=emg_dict[INTRODUCTION_KEY][0])

    # write intro
    mdFile.new_paragraph(emg_dict[INTRODUCTION_KEY][1])
    mdFile.write("\n")
    mdFile.new_paragraph(emg_dict[INTRODUCTION_KEY][2])
    mdFile.write("\n")
    mdFile.new_paragraph(emg_dict[INTRODUCTION_KEY][3])
    mdFile.write("\n")
    mdFile.new_paragraph(emg_dict[INTRODUCTION_KEY][4])
    mdFile.write("\n")
    mdFile.new_paragraph(emg_dict[INTRODUCTION_KEY][5])
    mdFile.write("\n")

    # bullet points
    mdFile.new_paragraph(emg_dict[INTRODUCTION_KEY][6])
    mdFile.new_paragraph(emg_dict[INTRODUCTION_KEY][7])
    mdFile.new_paragraph(emg_dict[INTRODUCTION_KEY][8])
    mdFile.new_paragraph(emg_dict[INTRODUCTION_KEY][9])

    # explain plot
    # emg plot
    mdFile.new_paragraph(emg_dict[PLOT_EXPLAIN_KEY][0])

    # show plot
    _add_centered_image(mdFile,
                        os.path.join(plots_path, str(subject_id), 'week',
                                     f'relative_bins_sessions_week.png'),
                        caption=None, max_width=1, max_height=0.95)

    mdFile.new_line(' \pagebreak ')
    mdFile.write("\n")
    # add risk rules and detection
    mdFile.new_paragraph(emg_dict[RISK_RULE_KEY][0])
    _add_rules_and_risk_occurrences(mdFile, emg_recommendations_above_high)
    mdFile.write("\n")
    _add_rules_and_risk_occurrences(mdFile, emg_recommendations_high)
    mdFile.write("\n")

    # show recommendations
    recommendations = _get_recommendation_set([emg_recommendations_above_high, emg_recommendations_high])
    _add_recommendation_section(mdFile, recommendations)
    mdFile.write("\n")


def _generate_heart_rate_section(mdFile, subject_id, oh_profile, oh_profiles_path, plots_path, recommendation_system, hr_dict=HEART_RATE_DICT[PT]):

    # load HR subject data
    hr_subject_data_df = recommender.generate_hr_csv(Path.cwd(), oh_profiles_path)

    # ------- get heart rate recommendations --------- #
    max_hr_recommendations = recommender.get_max_frequency_recommendation(hr_subject_data_df, oh_profile, subject_id, recommendation_system)
    slightly_elevated_hr_recommendations = recommender.get_elevated_hr_recommendations(hr_subject_data_df, oh_profile,subject_id,'Ligeiramente elevado',recommendation_system)
    elevated_hr_recommendations = recommender.get_elevated_hr_recommendations(hr_subject_data_df, oh_profile,subject_id, 'Elevado',recommendation_system)

    # ----- Paragraph: Introduction and Context ----- #
    mdFile.write("\n")
    # introduction title
    mdFile.new_header(level=2, title=hr_dict[INTRODUCTION_KEY][0])

    # ----- Paragraph: heart rate BPM explanation ----- #
    mdFile.new_paragraph(hr_dict[INTRODUCTION_KEY][1])
    mdFile.write("\n")
    mdFile.new_paragraph(hr_dict[INTRODUCTION_KEY][2])
    mdFile.write("\n")

    # ----- Paragraph: heart rate BPM plot explanation + Plot: hr range plot ----- #
    mdFile.new_paragraph(hr_dict[PLOT_EXPLAIN_KEY][0])
    _add_centered_image(mdFile, os.path.join(plots_path, str(subject_id), 'HR_ranges', f'{subject_id}_HR_ranges.png'),
                        caption=None, max_width=1, max_height=0.5)

    # ----- Paragraph: RISK RULE : hr range + RISK OCCURRENCE: hr range ----- #
    mdFile.new_paragraph(hr_dict[RISK_RULE_KEY][0])
    _add_rules_and_risk_occurrences(mdFile, max_hr_recommendations)
    mdFile.write("\n")
    mdFile.write("\n\\vspace{0.9em}\n")
    mdFile.new_line(' \pagebreak ')


    # ----- Paragraph: relative hear rate explanation ----- #
    mdFile.write("\n")
    mdFile.new_paragraph(hr_dict[INTRODUCTION_KEY][3])
    mdFile.write("\n")
    # bullet points: explaining the HR ratio classes
    mdFile.new_paragraph(hr_dict[INTRODUCTION_KEY][4])
    mdFile.new_paragraph(hr_dict[INTRODUCTION_KEY][5])
    mdFile.new_paragraph(hr_dict[INTRODUCTION_KEY][6])

    # ----- Paragraph: circular relative heart rate plot explanation + Plot: circular heart rate plot ----- #
    mdFile.new_paragraph(hr_dict[PLOT_EXPLAIN_KEY][1])
    _add_centered_image(mdFile,
                        os.path.join(plots_path, str(subject_id), 'HR_distributions',
                                     f'HR_plot_circular_{subject_id}.png'),
                        caption=None, max_width=1, max_height=0.9)

    # ----- Paragraph: RISK RULES: hr ratio + RISK OCCURRENCES: hr ratio ----- #
    mdFile.new_paragraph(hr_dict[RISK_RULE_KEY][0])
    _add_rules_and_risk_occurrences(mdFile, slightly_elevated_hr_recommendations)
    mdFile.write("\n")
    _add_rules_and_risk_occurrences(mdFile, elevated_hr_recommendations)
    mdFile.write("\n")

    # ----- Paragraph: RECOMMENDATIONS: all hr recommendations ----- #
    # get unrepeated recommendation set
    recommendations = _get_recommendation_set([slightly_elevated_hr_recommendations, elevated_hr_recommendations, max_hr_recommendations])
    _add_recommendation_section(mdFile, recommendations)
    mdFile.write("\n")


def _generate_human_activities_section(mdFile, subject_id,oh_profile, oh_profiles_path, plots_path, recommendation_system, har_dict=HAR_DICT[PT]):
    # load HAR subject data
    har_subject_data_df = recommender.generate_har_csv(Path.cwd(), oh_profiles_path)

    # load recommendations
    sitting_proportions_recommendations = recommender.get_sitting_proportions_recommendations(har_subject_data_df,subject_id,recommendation_system)
    sitting_total_recommendations = recommender.get_total_sitting_duration_recommendation(har_subject_data_df,subject_id,recommendation_system)
    sitting_continuous_recommendations_2h = recommender.get_continuous_sitting_recommendations(oh_profile, recommendation_system,activity_class_label=['Sentado'],exposure_limit_minutes=120.0)
    sitting_continuous_recommendations_1h = recommender.get_continuous_sitting_recommendations(oh_profile,recommendation_system,activity_class_label=['Sentado'],exposure_limit_minutes=60.0)
    standing_proportions_recommendations = recommender.get_standing_proportions_recommendations(har_subject_data_df,subject_id,recommendation_system)
    steps_recommendations = recommender.get_steps_recommendations(har_subject_data_df, subject_id,recommendation_system)

    mdFile.write("\n")
    # introduction title
    mdFile.new_header(level=2, title=har_dict[INTRODUCTION_KEY][0])

    # write intro
    mdFile.new_paragraph(har_dict[INTRODUCTION_KEY][1])
    mdFile.write("\n")
    mdFile.new_paragraph(har_dict[INTRODUCTION_KEY][2])
    mdFile.write("\n")
    mdFile.new_paragraph(har_dict[INTRODUCTION_KEY][3])
    mdFile.write("\n")

    # describe plot - timeline
    mdFile.new_paragraph(har_dict[PLOT_EXPLAIN_KEY][0])

    activity_folder = os.path.join(
        plots_path, str(subject_id), "human_activities"
    )

    timeline_images = _get_sorted_timeline_images(activity_folder)

    for img_path in timeline_images:

        _add_centered_image(
            mdFile,
            img_path,
            caption=None,
            max_width=1,
            max_height=0.6
        )

    mdFile.new_line(' \pagebreak ')

    # timeline risks
    mdFile.new_paragraph(har_dict[RISK_RULE_KEY][0])
    _add_rules_and_risk_occurrences(mdFile, sitting_continuous_recommendations_1h)
    mdFile.write("\n")
    _add_rules_and_risk_occurrences(mdFile, sitting_continuous_recommendations_2h)
    mdFile.write("\n")
    _add_rules_and_risk_occurrences(mdFile, sitting_total_recommendations)
    mdFile.write("\n")

    mdFile.write("\n\\vspace{0.9em}\n")

    # describe plot - distributions
    mdFile.new_paragraph(har_dict[PLOT_EXPLAIN_KEY][1])

    _add_centered_image(mdFile,
                        os.path.join(plots_path, str(subject_id), 'human_activities', f'{subject_id}_ospaq_vs_real_activity_distribution.png'),
                        caption=None, max_width=1, max_height=0.5)

    # proportions risks
    mdFile.new_paragraph(har_dict[RISK_RULE_KEY][1])
    _add_rules_and_risk_occurrences(mdFile, sitting_proportions_recommendations)
    _add_rules_and_risk_occurrences(mdFile, standing_proportions_recommendations)
    mdFile.write("\n")
    mdFile.new_line(' \pagebreak ')
    # check recommendations
    recommendations = _get_recommendation_set([sitting_proportions_recommendations, sitting_total_recommendations, sitting_continuous_recommendations_1h, sitting_continuous_recommendations_2h, standing_proportions_recommendations])
    _add_recommendation_section(mdFile, recommendations)
    mdFile.write("\n\\vspace{0.9em}\n")
    mdFile.write("\n")

    # describe plot - steps
    mdFile.new_paragraph(har_dict[PLOT_EXPLAIN_KEY][2])
    _add_centered_image(mdFile,
                        os.path.join(plots_path, str(subject_id), 'human_activities',
                                     f'{subject_id}_daily_steps_distance.png'),
                        caption=None, max_width=1, max_height=0.5)

    # steps risks
    mdFile.new_paragraph(har_dict[RISK_RULE_KEY][2])
    _add_rules_and_risk_occurrences(mdFile, steps_recommendations)
    mdFile.write("\n")

    # add recommendations
    _add_recommendation_section(mdFile, steps_recommendations[RECOMMENDATIONS_KEY])


def _generate_wrist_section(mdFile, subject_id, plots_path, wrist_dict=WRIST_MOVEMENT_DICT[PT]):
    mdFile.write("\n")
    # introduction title
    mdFile.new_header(level=2, title=wrist_dict[INTRODUCTION_KEY][0])

    # write intro
    mdFile.new_paragraph(wrist_dict[INTRODUCTION_KEY][1])
    mdFile.write("\n")
    mdFile.new_paragraph(wrist_dict[INTRODUCTION_KEY][2])
    mdFile.write("\n")
    mdFile.new_paragraph(wrist_dict[INTRODUCTION_KEY][3])
    mdFile.write("\n")
    mdFile.new_paragraph(wrist_dict[INTRODUCTION_KEY][4])
    mdFile.write("\n")
    mdFile.new_paragraph(wrist_dict[PLOT_EXPLAIN_KEY][0])

    _add_centered_image(mdFile,
                        os.path.join(plots_path, str(subject_id), 'wrist_movements',
                                     f'wrist_acceleration_{subject_id}.png'),
                        caption=None, max_width=1, max_height=0.35)

    mdFile.write("\n")
    mdFile.new_paragraph(wrist_dict[RISK_RULE_KEY][0])



def _generate_noise_section(mdFile, subject_id, plots_path, oh_profile, oh_profiles_path, recommendation_system, noise_dict=NOISE_DICT[PT]):

    # get noise recommender

    # load noise risk subjects
    noise_risk_subjects_df = recommender.generate_noise_csv(Path.cwd(), oh_profiles_path)

    # ger noise recommendations
    noise_exposure_recommendations = recommender.get_noise_exposure_recommendations(noise_risk_subjects_df, subject_id, recommendation_system)
    noise_continuous_recommendations = recommender.get_continuous_noise_recommendations(oh_profile, recommendation_system, noise_level_label=['Ruído incomodativo','Ruído elevado'])

    mdFile.write("\n")
    # introduction title
    mdFile.new_header(level=2, title=noise_dict[INTRODUCTION_KEY][0])

    # write intro
    mdFile.new_paragraph(noise_dict[INTRODUCTION_KEY][1])
    mdFile.write("\n")
    mdFile.new_paragraph(noise_dict[INTRODUCTION_KEY][2])
    mdFile.new_paragraph(noise_dict[INTRODUCTION_KEY][3])
    mdFile.new_paragraph(noise_dict[INTRODUCTION_KEY][4])
    mdFile.new_paragraph(noise_dict[INTRODUCTION_KEY][5])
    mdFile.write("\n")

    # describe plot - timeline
    mdFile.new_paragraph(noise_dict[PLOT_EXPLAIN_KEY][0])

    _add_centered_image(mdFile,
                        os.path.join(plots_path, str(subject_id), 'noise_plots', f'{subject_id}_noise_timeline.png'),
                        caption=None, max_width=1, max_height=0.5)

    mdFile.write("\n")
    mdFile.new_paragraph(noise_dict[RISK_RULE_KEY][0])
    _add_rules_and_risk_occurrences(mdFile, noise_continuous_recommendations)
    mdFile.write("\n\\vspace{0.9em}\n")
    mdFile.write("\n")
    # describe plot - distributions
    mdFile.new_paragraph(noise_dict[PLOT_EXPLAIN_KEY][1])

    _add_centered_image(mdFile,
                        os.path.join(plots_path, str(subject_id), 'noise_plots', f'{subject_id}_noise_distribution.png'),
                        caption=None, max_width=1, max_height=0.5)

    mdFile.write("\n")
    mdFile.new_paragraph(noise_dict[RISK_RULE_KEY][1])
    mdFile.write("\n")
    _add_rules_and_risk_occurrences(mdFile, noise_exposure_recommendations)


    # add recommendations
    _add_recommendation_section(mdFile, noise_exposure_recommendations[RECOMMENDATIONS_KEY])


def _generate_sensor_timeline_section(mdFile, subject_id, plots_path, timeline_dict = SENSOR_TIMELINE_DICT[PT]):


    mdFile.write("\n")
    # introduction title
    mdFile.new_header(level=2, title=timeline_dict[INTRODUCTION_KEY][0])

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
                        caption=None, max_width=1, max_height=0.6)


def _generate_environmental_sensors_section(mdFile, subject_id, plots_path, cml_dict = CML_SENSORS_DICT[PT]):
    mdFile.write("\n")
    # introduction title
    mdFile.new_header(level=2, title=cml_dict[INTRODUCTION_KEY][0])

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



def _generate_questionnaires_section(mdFile, subject_id, plots_path, oh_profiles_path, recommendation_system,
                                     work_type, intro_dict=QUEST_INTRO_DICT[PT], rosa_dict=ROSA_DICT[PT],
                                     env_dict=ENVIRONMENT_DICT[PT], psycho_dict=COPSOQ_DICT[PT]):

    # get work type full string
    if work_type == 'FO':
        work_type_full = "front office"

    else:
        work_type_full = "back office"

    mdFile.write("\n")
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
    mdFile.new_paragraph(rosa_dict[INTRODUCTION_KEY][2])
    mdFile.write("\n")

    # describe plots
    mdFile.new_paragraph(rosa_dict[PLOT_EXPLAIN_KEY][0])
    mdFile.write("\n")
    mdFile.new_line(' \pagebreak ')
    mdFile.write("\n")

    # add table
    items_rosa = [s for s in rosa_dict[PLOT_EXPLAIN_KEY] if re.match(r"^\d+\.\s", s)]
    _add_two_column_table(mdFile, items_rosa, header_left="Equipamento", header_right="Equipamento", text_align="left")

    mdFile.write("\n")

    # add rosa plot
    _add_centered_image(mdFile, os.path.join(plots_path, str(subject_id), 'questionnaire_plots', f'Rosa_plot_{subject_id}.png'),
                        caption='Resultados pessoais da avaliação Biomecânica .')
    # describe risk
    mdFile.new_paragraph(rosa_dict[RISK_RULE_KEY][0])
    mdFile.write("\n")

    # get the subjects df
    rosa_subjects_data_df = recommender.generate_rosa_csv(Path.cwd(), oh_profiles_path)

    # generate recommendations
    rosa_recommendations = recommender.get_rosa_recommendations(rosa_subjects_data_df, subject_id,
                                                                recommendation_system)
    # add rules
    mdFile.write("\n")
    _add_rules(mdFile, rosa_recommendations)

    # add recommendations
    _add_questionnaire_recommendations(mdFile, rosa_recommendations[RECOMMENDATIONS_KEY])
    # --------------------------------------- environmental questionnaire --------------------------------------#


    # intro
    mdFile.write("\n")
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

    # get the subjects df
    environment_data_df = recommender.generate_environment_csv(Path.cwd(), oh_profiles_path)

    # generate recommendations
    environment_recommendations = recommender.get_environment_recommendations(environment_data_df, subject_id,
                                                                              recommendation_system)
    # add rules
    mdFile.write("\n")
    _add_rules(mdFile, environment_recommendations)

    # add recommendations
    _add_questionnaire_recommendations(mdFile, environment_recommendations[RECOMMENDATIONS_KEY])
    # --------------------------------------- PSYCHOSOCIAL (COPSOQ AND MUEQ) --------------------------------------#
    mdFile.write("\n")
    mdFile.new_line(' \pagebreak ')
    mdFile.write("\n")

    # intro
    mdFile.new_header(level=2, title=psycho_dict[INTRODUCTION_KEY][0])
    mdFile.new_paragraph(psycho_dict[INTRODUCTION_KEY][1])
    mdFile.write("\n")
    mdFile.new_paragraph(psycho_dict[INTRODUCTION_KEY][2])
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


def _generate_daily_questionnaire(mdFile, subject_id, plots_path, pain_dict=PAIN_DICT[PT], workload_dict=WORKLOAD_DICT[PT]):
    # --------------------------------------- workload --------------------------------------------#
    mdFile.new_header(level=2, title=workload_dict[INTRODUCTION_KEY][0])

    mdFile.new_paragraph(workload_dict[INTRODUCTION_KEY][1])
    mdFile.write("\n")
    mdFile.new_paragraph(workload_dict[INTRODUCTION_KEY][2])
    mdFile.write("\n")

    # add plot explanation
    # explain pain plot
    mdFile.new_paragraph(workload_dict[PLOT_EXPLAIN_KEY][0])
    mdFile.write("\n")
    _add_centered_image(mdFile, os.path.join(plots_path, str(subject_id), 'questionnaire_plots' ,f"{subject_id}_carga_de_trabalho.png"), max_width=1,
                        max_height=0.9)
    mdFile.write("\n")

    # --------------------------------------- PAIN --------------------------------------------#
    mdFile.new_header(level=2, title=pain_dict[INTRODUCTION_KEY][0])

    mdFile.new_paragraph(pain_dict[INTRODUCTION_KEY][1])
    mdFile.write("\n")
    mdFile.new_paragraph(pain_dict[INTRODUCTION_KEY][2])
    mdFile.write("\n")
    mdFile.new_paragraph(pain_dict[INTRODUCTION_KEY][3])
    mdFile.write("\n")
    mdFile.new_paragraph(pain_dict[INTRODUCTION_KEY][4])
    mdFile.write("\n")

    # explain pain plot
    mdFile.new_paragraph(pain_dict[PLOT_EXPLAIN_KEY][0])
    mdFile.write("\n")

    _add_centered_image(mdFile, os.path.join(plots_path, str(subject_id), f"{subject_id}_pain_plot.png"), max_width=1,
                        max_height=0.5)
    mdFile.write("\n")


def _generate_conclusion_section(mdFile, conclusion_dict=INTRO_DICT[PT]):
    """

    :param mdFile:
    :param subject_id:
    :param introduction_dict:
    :return:
    """
    # introduction title
    mdFile.new_header(level=1, title=conclusion_dict[SECTION_0])

    # write paragraphs
    mdFile.new_paragraph(conclusion_dict[SECTION_1])
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

def _add_questionnaire_recommendations(mdFile, recommendations: Union[Dict, List[str]]):
    """

    :param mdFile:
    :param recommendations:
    :return:
    """

    mdFile.write("\n")
    mdFile.new_paragraph("De acordo com os seus resultados, são-lhe sugeridas as seguintes recomendações:")
    mdFile.write("\n")

    # check if the recommendations are of type dictionary --> there are recommendations per dimension
    if isinstance(recommendations, dict):

        # cycle over the key value pairs
        for dimension, recommendations_list in recommendations.items():

            mdFile.write("\n")
            mdFile.new_paragraph(f"**{dimension}**:")
            mdFile.write("\n")

            if len(recommendations_list) == 1:
                mdFile.new_paragraph(f"- **Recomendação**: {recommendations_list[0]}")

            else:
                # write the recommendations
                for i, recommendation in enumerate(recommendations_list):
                    mdFile.new_paragraph(f"- **Recomendação {i + 1}**: {recommendation}")

    # no recommendations (in this case it is a list(
    else:
        mdFile.new_paragraph(f"- **Recomendação**: {recommendations[0]}")


def _add_recommendation_section(mdFile, recommendations_list):

    if len(recommendations_list) == 1:
        mdFile.write("\n")
        mdFile.new_paragraph("De acordo com os seus resultados, é-lhe sugerida a seguinte recomendação: ")
        mdFile.new_paragraph(f"- **Recomendação**: {recommendations_list[0]}")

    else:
        mdFile.write("\n")
        mdFile.new_paragraph("De acordo com os seus resultados, são-lhe sugeridas as seguintes recomendações: ")
        # recommendations
        for i, recommendation in enumerate(recommendations_list):
            mdFile.new_paragraph(f"- **Recomendação {i+1}**: {recommendation}")

def _add_rules(mdFile, recommendations_dict: Dict) -> None:
    """

    :param mdFile:
    :param recommendations_dict:
    :return:
    """

    if len(recommendations_dict['rule']) == 1:

        mdFile.new_paragraph(f"\n**Risco**: {recommendations_dict['rule'][0]}")
        mdFile.write("\n")

    else:

        for i, rule in enumerate(recommendations_dict['rule']):
            mdFile.new_paragraph(f"\n**Risco {i + 1}**: {recommendations_dict['rule'][i]}")
            mdFile.write("\n")


def _add_rules_and_risk_occurrences(mdFile, recommendations_dict):

    if len(recommendations_dict['rule']) == 1:

        mdFile.new_paragraph(f"\n**Risco**: {recommendations_dict['rule'][0]}")
        mdFile.write("\n")

    else:

        for i, rule in enumerate(recommendations_dict['rule']):

            mdFile.new_paragraph(f"\n**Risco {i+1}**: {recommendations_dict['rule'][i]}")
            mdFile.write("\n")

    # only show risk cases if they exist
    if 'num_instances' in recommendations_dict.keys():

        # get dates where there was risk
        dates = recommendations_dict['risk_dates']

        if len(dates) == 1:
            mdFile.new_paragraph(
                fr"$\hookrightarrow$ Foi detetada **1 ocorrência** no dia: **"f"{', '.join(dates)}**")
            mdFile.write("\n")
        else:
            mdFile.new_paragraph(
                fr"$\hookrightarrow$ Foram detetadas **{recommendations_dict['num_instances']} ocorrências** nos dias: **"f"{', '.join(dates)}**")
            mdFile.write("\n")

    else:
        mdFile.new_paragraph(
            r"$\hookrightarrow$ Não foram detetados fatores de risco.")
        mdFile.write("\n")


def _get_sorted_timeline_images(folder_path, keyword="timeline", ext=".png"):
    """
    Returns a list of image paths sorted by date extracted from filename.

    Expected filename format:
        <subject>_DD-MM-YYYY_<anything>_timeline.png

    Parameters
    ----------
    folder_path : str or Path
        Path to the folder containing the images
    keyword : str
        Keyword that must be present in filename (default: "timeline")
    ext : str
        File extension to consider (default: ".png")

    Returns
    -------
    list[str]
        Full paths to images, sorted by date
    """

    folder_path = Path(folder_path)

    def _extract_date(fname):
        # Example: 80_23-09-2025_activity_timeline.png
        date_str = fname.split("_")[1]
        return datetime.strptime(date_str, "%d-%m-%Y").date()

    files = [
        f for f in folder_path.iterdir()
        if f.is_file()
        and keyword in f.name
        and f.suffix.lower() == ext
    ]

    files_sorted = sorted(files, key=lambda f: _extract_date(f.name))

    return [str(f) for f in files_sorted]


def _get_recommendation_set(recommender_dict_list: List[Dict], language='pt'):
    """

    :param recommender_dict_list:
    :return:
    """

    # init the set
    recommendation_set = set()

    # cycle over the list and get the recommendation
    for recommendation_dict in recommender_dict_list:

        if recommendation_dict[RECOMMENDATIONS_KEY][0] != NO_RECOMMENDATIONS[language]:

            # get the recommendations and add them to the set
            recommendation_set.update(recommendation_dict[RECOMMENDATIONS_KEY])


    if recommendation_set:

        return list(recommendation_set)

    else:

        return [NO_RECOMMENDATIONS[language]]


def _generate_references(mdFile, refs_list=REFS_LIST, links_list=LINKS_LIST):

    mdFile.write("\n")
    # generate header
    mdFile.new_header(level=1, title='Bibliografia')

    # cycle over the references and links
    for i, (ref, link) in enumerate(zip(refs_list, links_list)):

        # add ref
        mdFile.new_paragraph(ref)

        #add link
        mdFile.write(mdFile.new_reference_link(link=link,text=link,reference_tag=f'{i+1}'))
