# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import sys
from pathlib import Path
import pandas as pd
from typing import Dict, List

# internal imports
from constants import RISK_DATES_KEY, NUM_INSTANCES_KEY, RECOMMENDATIONS_KEY, RULE_KEY, NO_RECOMMENDATIONS, USER, \
    RISK_DIMENSIONS_KEY
from recommender.utils import dates_to_weekdays, get_mean_workload_score

# external imports
project_path = Path(f"C:/{USER}/phill/PycharmProjects/OH_Toolkit")
sys.path.append(str(project_path))
from oh_parser import load_profiles, extract_nested


# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
ROSA_CSV_FILENAME = 'rosa_subject_metrics.csv'
ENVIRONMENT_CSV_FILENAME = 'environment_subject_metrics.csv'


ROSA_MAPPING = {
    "score_a_adapted": {
        "pt": "cadeira",
        "eng": "chair",
    },
    "monitor_adapted_norm": {
        "pt": "monitor",
        "eng": "monitor",
    },
    "phone_adapted_norm": {
        "pt": "telefone",
        "eng": "phone",
    },
    "mouse_adapted_norm": {
        "pt": "rato",
        "eng": "mouse",
    },
    "keyboard_adapted_norm": {
        "pt": "teclado",
        "eng": "keyboard",
    },
}

MEDIUM_RISK_LEVEL = 0.33

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #

def generate_rosa_csv(rosa_data_csv_path: str | Path, oh_profile_path: str) -> pd.DataFrame:
    """

    :param rosa_data_csv_path:
    :param oh_profile_path:
    :return:
    """

    if not (Path(rosa_data_csv_path) / ROSA_CSV_FILENAME).exists():
        # load the profiles
        profiles = load_profiles(oh_profile_path)

        # parse the noise metrics
        df_sessions = extract_nested(
            profiles,
            base_path="single_instance_questionnaires.biomechanical.ROSA",
            level_names=[],
            value_paths=[
                "score_a_adapted",
                "monitor_adapted_norm",
                "phone_adapted_norm",
                "mouse_adapted_norm",
                "keyboard_adapted_norm"


            ],
            exclude_patterns=[],
        )

        # save the DataFrame
        df_sessions.to_csv(ROSA_CSV_FILENAME, index=False)

    else:
        df_sessions = pd.read_csv(ROSA_CSV_FILENAME)

    return df_sessions


def generate_environment_csv(environment_data_csv_path: str | Path, oh_profile_path: str) -> pd.DataFrame:
    """

    :param environment_data_csv_path:
    :param oh_profile_path:
    :return:
    """

    if not (Path(environment_data_csv_path) / ENVIRONMENT_CSV_FILENAME).exists():
        # load the profiles
        profiles = load_profiles(oh_profile_path)

        # parse the noise metrics
        df_sessions = extract_nested(
            profiles,
            base_path="single_instance_questionnaires.environmental",
            level_names=[],
            value_paths=[
                "Nível de Iluminação",
                "Ar",
                "Ruído",
                "Design do Escritório",
                "Privacidade do Escritório",
                "Organização do Escritório"

            ],
            exclude_patterns=[],
        )

        # save the DataFrame
        df_sessions.to_csv(ENVIRONMENT_CSV_FILENAME, index=False)

    else:
        df_sessions = pd.read_csv(ENVIRONMENT_CSV_FILENAME)

    return df_sessions


def get_rosa_recommendations(rosa_subject_metrics_df: pd.DataFrame, subject_id: int,
                             full_recommender_dict: Dict, language: str = 'pt') -> Dict:
    """

    :param rosa_subject_metrics_df:
    :param subject_id:
    :param full_recommender_dict:
    :param language:
    :return:
    """

    # init the recommendations dict with the rule (it is the same rule for all questions)
    recommendations_dict = {
        RULE_KEY: full_recommender_dict['questionnaires']['biomechanical']['ROSA']['score_a_adapted']['rule'][language]}

    # get the keys from the recommender
    risk_keys = full_recommender_dict['questionnaires']['biomechanical']['ROSA'].keys()

    # list for holding the risk dimensions and the corresponding recommendation
    risk_dimensions = []
    recommendations = []


    # cycle over the keys
    for risk_key in risk_keys:

        # filter the DataFrame according to the rul
        risk_subjects_df = rosa_subject_metrics_df[rosa_subject_metrics_df[risk_key] >= MEDIUM_RISK_LEVEL]

        if subject_id in risk_subjects_df['subject_id'].tolist():

            # add the mapped risk key to the risk dimensions
            risk_dimensions.append(ROSA_MAPPING[risk_key][language])

            # get the corresponding recommendation
            recommendations.extend(full_recommender_dict['questionnaires']['biomechanical']['ROSA'][risk_key]['recommendation'][language])


    if len(risk_dimensions) > 0:

        # generate the dict
        recommendations_dict[RISK_DIMENSIONS_KEY] = risk_dimensions
        recommendations_dict[RECOMMENDATIONS_KEY] = recommendations

    else:

        # add that there are no recommendations needed
        recommendations_dict[RECOMMENDATIONS_KEY] = [NO_RECOMMENDATIONS[language]]

    return recommendations_dict


def get_environment_recommendations(environmental_subject_metrics_df: pd.DataFrame, subject_id: int,
                                    full_recommender_dict: Dict, language: str = 'pt') -> Dict:
    """

    :param environmental_subject_metrics_df:
    :param subject_id:
    :param full_recommender_dict:
    :param language:
    :return:
    """

    # init the recommendations dict with the rule (it is the same rule for all questions)
    recommendations_dict = {
        RULE_KEY: full_recommender_dict['questionnaires']['environmental']['Ar']['rule'][language]}

    # get the keys from the recommender
    risk_keys = full_recommender_dict['questionnaires']['environmental'].keys()

    # list for holding the risk dimensions and the corresponding recommendation
    risk_dimensions = []
    recommendations = []


    # cycle over the keys
    for risk_key in risk_keys:

        # filter the DataFrame according to the rul
        risk_subjects_df = environmental_subject_metrics_df[environmental_subject_metrics_df[risk_key] >= MEDIUM_RISK_LEVEL]

        if subject_id in risk_subjects_df['subject_id'].tolist():

            # add the mapped risk key to the risk dimensions
            #TODO fix for english
            risk_dimensions.append(risk_key)

            # get the corresponding recommendation
            recommendations.extend(full_recommender_dict['questionnaires']['environmental'][risk_key]['recommendation'][language])


    if len(risk_dimensions) > 0:

        # generate the dict
        recommendations_dict[RISK_DIMENSIONS_KEY] = risk_dimensions
        recommendations_dict[RECOMMENDATIONS_KEY] = recommendations

    else:

        # add that there are no recommendations needed
        recommendations_dict[RECOMMENDATIONS_KEY] = [NO_RECOMMENDATIONS[language]]

    return recommendations_dict