"""
function for creating report
"""
# imports
import os
import json
import os, shutil
from mdutils import Html
from mdutils.mdutils import MdUtils
from report_generator.report_sections.general.introduction import *
from report_generator.report_sections.questionnaires.introductory_section import *
from report_generator.report_sections.questionnaires.rosa import *
from report_generator.report_sections.questionnaires.environment import *
from report_generator.report_sections.questionnaires.copsoq import *
from constants import PT, INTRODUCTION_KEY, RISK_RULE_KEY, PLOT_EXPLAIN_KEY


# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #


def generate_report(report_folder_path, subject_id, plots_path, oh_profiles_path):

    # generate file with cover
    mdFile = _generate_file_and_cover(report_folder_path, subject_id)

    # introduction
    _generate_introduction_section(mdFile)

    # # get work type from OH profile
    # for oh_profile_path in os.listdir(oh_profiles_path):
    #
    #     if oh_profile_path.split('_')[0] == subject_id:
    #
    #         # load json
    #         with open(oh_profile_path, "r", encoding="utf-8") as json_file:
    #             oh_profile = json.load(json_file)
    #
    #         # get work type

    # questionnaires
    _generate_questionnaires_section(mdFile, subject_id, plots_path)

    print("pandoc which:", shutil.which("pandoc"))
    print("PATH:", os.environ.get("PATH", "")[:300], "...")

    mdFile.create_md_file()

    os.system('pandoc --verbose --template=eisvogel.latex -V geometry:margin=1.1in ' + report_folder_path
              + f'/Relatorio_{subject_id}.md  --pdf-engine=pdflatex -o ' + report_folder_path + '/relatorio.pdf')
    print("report done")

    # sensors


# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #

def _generate_file_and_cover(report_folder_path, subject_id):

    # create new file
    mdFile = MdUtils(file_name=os.path.join(report_folder_path, f'Relatorio_{subject_id}'))

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


def _generate_questionnaires_section(mdFile, subject_id, plots_path, intro_dict=QUEST_INTRO_DICT[PT], rosa_dict=ROSA_DICT[PT],
                                    env_dict=ENVIRONMENT_DICT[PT], psyco_dict=COPSOQ_DICT[PT]):

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

    # add rosa plot
    mdFile.new_line(mdFile.new_inline_image(text='',
                    path=os.path.join(plots_path, str(subject_id), 'questionnaire_plots', f'Rosa_plot_{subject_id}.png')))

    # describe risk
    mdFile.new_paragraph(rosa_dict[RISK_RULE_KEY][0])
    mdFile.write("\n")

    # TODO - RECOMMENDATIONS
    # --------------------------------------- environmental questionnaire --------------------------------------#
    # intro
    mdFile.new_header(level=2, title=env_dict[INTRODUCTION_KEY][0])
    mdFile.new_paragraph(env_dict[INTRODUCTION_KEY][1])
    mdFile.write("\n")

    # describe plots
    mdFile.new_paragraph(env_dict[PLOT_EXPLAIN_KEY][0])
    mdFile.write("\n")

    # add rosa plot
    mdFile.new_line(mdFile.new_inline_image(text='',
                                            path=os.path.join(plots_path, str(subject_id), 'questionnaire_plots',
                                                              f'environment_plot_{subject_id}.png')))

    # describe risk
    mdFile.new_paragraph(env_dict[RISK_RULE_KEY][0])
    mdFile.write("\n")

    # TODO RECOMMENDATIONS
    # --------------------------------------- PSYCHOSOCIAL (COPSOQ AND MUEQ) --------------------------------------#
    # intro
    mdFile.new_header(level=2, title=psyco_dict[INTRODUCTION_KEY][0])
    mdFile.new_paragraph(psyco_dict[INTRODUCTION_KEY][1])
    mdFile.write("\n")

    # describe plots
    mdFile.new_paragraph(psyco_dict[PLOT_EXPLAIN_KEY][0])
    mdFile.write("\n")

    # show copsoq population plot
    mdFile.new_header(level=2, title="COPSOQ - resultado de toda a população do estudo")

    # add plot
    mdFile.new_line(mdFile.new_inline_image(text='',
                                            path=os.path.join(plots_path, str(subject_id), 'questionnaire_plots',
                                                              f'copsoq_population.png')))

    # show copsoq worktype plot
    mdFile.new_header(level=2, title="COPSOQ - resultado de trabalhadores WORKTYPE")

    # add rosa plot
    mdFile.new_line(mdFile.new_inline_image(text='',
                                            path=os.path.join(plots_path, str(subject_id), 'questionnaire_plots',
                                                              f'copsoq_population.png')))

    # show mueq population
    mdFile.new_header(level=2, title="MUEQ - resultado de toda a população do estudo")

    # add plot
    mdFile.new_line(mdFile.new_inline_image(text='',
                                            path=os.path.join(plots_path, str(subject_id), 'questionnaire_plots',
                                                              f'mueq_population.png')))

    # show mueq worktype plot
    mdFile.new_header(level=2, title="MUEQ - resultado de trabalhadores WORKTYPE")

    # add plot
    mdFile.new_line(mdFile.new_inline_image(text='',
                                            path=os.path.join(plots_path, str(subject_id), 'questionnaire_plots',
                                                              f'mueq_population.png')))

