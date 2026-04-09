# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd

# internal imports
from constants import RISK_DATES_KEY, NUM_INSTANCES_KEY, RECOMMENDATIONS_KEY, RULE_KEY, NO_RECOMMENDATIONS, USER
from recommender.utils import dates_to_weekdays, evaluate_continuous_timeline_risk

# external imports
project_path = Path(f"C:/Users/{USER}/PycharmProjects/OH_Toolkit")
sys.path.append(str(project_path))
from oh_parser import load_profiles, extract_nested

# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
NOISE_CSV_FILENAME = "noise_risk_subjects.csv"

LOUD_NOISE_SUM = 'sum_loud_noise'
NOISE_RULE_MAX_LOUD_NOISE_PERCENTAGE = 0.5

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def generate_noise_csv(noise_risk_csv_path: str | Path, oh_profile_path: str) -> pd.DataFrame:
    """
    :param noise_risk_csv_path:
    :param oh_profile_path:
    :return:
    """

    if not (Path(noise_risk_csv_path) / NOISE_CSV_FILENAME).exists():
        # load the profiles
        profiles = load_profiles(oh_profile_path)

        # parse the noise metrics
        df_sessions = extract_nested(
            profiles,
            base_path="sensor_metrics.noise",
            level_names=["date", "session"],
            value_paths=[
                "Noise_distributions.Ruído incomodativo",
                "Noise_distributions.Ruído elevado",

            ],
            exclude_patterns=[],
        )

        # add up disturbing and high noise
        df_sessions[LOUD_NOISE_SUM] = df_sessions['Noise_distributions.Ruído incomodativo'] + df_sessions[
            'Noise_distributions.Ruído elevado']

        # filter the DataFrame to only contain subjects that exceed the noise rule
        df_risk_subjects = df_sessions[df_sessions[LOUD_NOISE_SUM] >= NOISE_RULE_MAX_LOUD_NOISE_PERCENTAGE]

        # save the DataFrame
        df_risk_subjects.to_csv(NOISE_CSV_FILENAME, index=False)

    else:
        df_risk_subjects = pd.read_csv(NOISE_CSV_FILENAME)

    return df_risk_subjects


def get_continuous_noise_recommendations(oh_profile: Dict,
                                         full_recommender_dict: Dict,
                                         noise_level_label: List[str] = None,
                                         exposure_limit_minutes: float = 60.0, language: str ='pt') -> Dict:
    """

    :param oh_profile:
    :param exposure_limit_minutes:
    :param noise_level_label:
    :param full_recommender_dict:
    :param language:
    :return:
    """

    # get the noise metrics from the OH profile
    noise_metrics = oh_profile['sensor_metrics']['noise']

    # init the recommendations dict with the rule
    recommendations_dict = {RULE_KEY: [full_recommender_dict['sensors']['noise']['rule'][language][0]]}

    # evaluate the noise timeline continuous risk
    risk_dates, total_num_instances = evaluate_continuous_timeline_risk(noise_metrics, 'Noise_timeline_wlen-10', noise_level_label, exposure_limit_minutes, 0)


    if len(risk_dates) > 0:

        # transform dates to strings
        risk_dates = dates_to_weekdays(risk_dates, date_format="%d-%m-%Y", locale=language)

        # generate dict
        recommendations_dict[RISK_DATES_KEY] = risk_dates
        recommendations_dict[NUM_INSTANCES_KEY] = total_num_instances
        recommendations_dict[RECOMMENDATIONS_KEY] = full_recommender_dict['sensors']['noise']['recommendation'][language]

    else:

        # add that there are no recommendations needed
        recommendations_dict[RECOMMENDATIONS_KEY] = [NO_RECOMMENDATIONS[language]]

    return recommendations_dict


def get_noise_exposure_recommendations(noise_risk_subjects_df: pd.DataFrame, subject_id: int, full_recommender_dict: Dict, language: str = 'pt') -> Dict:
    """

    :param noise_risk_subjects_df:
    :param subject_id:
    :param full_recommender_dict:
    :param language:
    :return:
    """

    # TODO: move filtering to here

    # init the recommendations dict with the rule
    recommendations_dict = {RULE_KEY: [full_recommender_dict['sensors']['noise']['rule'][language][1]]}

    # get the unique subject IDs
    risk_subjects = noise_risk_subjects_df['subject_id'].unique().tolist()

    if subject_id in risk_subjects:

        # get rows that belong to subject
        subject_data = noise_risk_subjects_df[noise_risk_subjects_df['subject_id'] == subject_id]

        # count number of instances
        num_instances = len(subject_data)

        # get the dates
        risk_dates = subject_data['date'].tolist()

        # transform dates to strings
        risk_dates = dates_to_weekdays(risk_dates, date_format="%d-%m-%Y", locale=language)

        # generate dict
        recommendations_dict[RISK_DATES_KEY] = risk_dates
        recommendations_dict[NUM_INSTANCES_KEY] = num_instances
        recommendations_dict[RECOMMENDATIONS_KEY] = full_recommender_dict['sensors']['noise']['recommendation'][language]


    else:

        # add that there are no recommendations needed
        recommendations_dict[RECOMMENDATIONS_KEY] = [NO_RECOMMENDATIONS[language]]

    return recommendations_dict

# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #