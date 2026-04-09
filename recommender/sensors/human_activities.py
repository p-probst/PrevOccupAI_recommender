# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import sys
from pathlib import Path
import pandas as pd
from typing import Dict, List


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
HAR_CSV_FILENAME = "har_subject_metrics.csv"

HAR_RULE_MAX_SITTING_TIME_SECONDS = 5.0 * 3600 # total of 5 hours of sitting
HAR_RULE_MAX_ACTIVITY_PERCENTAGE = 0.5 # 50 percent sitting during the day
HAR_RULE_MIN_STEPS = 700
HAR_EXPOSURE_LIMIT_1H = 60.0 # 60 minutes
HAR_EXPOSURE_LIMIT_2H = 120.0


# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def generate_har_csv(har_data_csv_path: str | Path, oh_profile_path: str) -> pd.DataFrame:
    """

    :param har_data_csv_path:
    :param oh_profile_path:
    :return:
    """

    if not (Path(har_data_csv_path) / HAR_CSV_FILENAME).exists():
        # load the profiles
        profiles = load_profiles(oh_profile_path)

        # parse the noise metrics
        df_sessions = extract_nested(
            profiles,
            base_path="sensor_metrics.human_activities",
            level_names=["date", "session"],
            value_paths=[
                "HAR_distributions.Sentado",
                "HAR_distributions.De pé",
                "HAR_durations.Sentado_duration_sec",
                "HAR_steps.num_steps"

            ],
            exclude_patterns=[],
        )

        # save the DataFrame
        df_sessions.to_csv(HAR_CSV_FILENAME, index=False)

    else:
        df_sessions = pd.read_csv(HAR_CSV_FILENAME)

    return df_sessions


def get_sitting_proportions_recommendations(har_subject_metrics_df: pd.DataFrame, subject_id: int,
                                           full_recommender_dict: Dict, language: str = 'pt') -> Dict:
    """

    :param har_subject_metrics_df:
    :param subject_id:
    :param full_recommender_dict:
    :param language:
    :return:
    """

    # init the recommendations dict with the rule
    recommendations_dict = {RULE_KEY: [full_recommender_dict['sensors']['human_activities']['sitting']['rule'][language][3]]}

    # filter the DataFrame according to the rule
    har_risk_subjects_df = har_subject_metrics_df[har_subject_metrics_df['HAR_distributions.Sentado'] > HAR_RULE_MAX_ACTIVITY_PERCENTAGE]

    # get the unique subjects
    risk_subjects = har_risk_subjects_df['subject_id'].unique().tolist()

    if subject_id in risk_subjects:

        # get rows that belong to subject
        subject_data = har_risk_subjects_df[har_risk_subjects_df['subject_id'] == subject_id]

        # count the number of instances
        num_instances = len(subject_data)

        # get the dates
        risk_dates = subject_data['date'].tolist()

        # transform dates to strings
        risk_dates = dates_to_weekdays(risk_dates, date_format="%d-%m-%Y", locale=language)

        # generate dict
        recommendations_dict[RISK_DATES_KEY] = risk_dates
        recommendations_dict[NUM_INSTANCES_KEY] = num_instances
        recommendations_dict[RECOMMENDATIONS_KEY] = full_recommender_dict['sensors']['human_activities']['sitting']['recommendation'][language]

    else:

        # add that there are no recommendations needed
        recommendations_dict[RECOMMENDATIONS_KEY] = [NO_RECOMMENDATIONS[language]]

    return recommendations_dict


def get_total_sitting_duration_recommendation(har_subject_metrics_df: pd.DataFrame, subject_id: int,
                                              full_recommender_dict: Dict, language: str = 'pt') -> Dict:
    """

    :param har_subject_metrics_df:
    :param subject_id:
    :param full_recommender_dict:
    :param language:
    :return:
    """

    # init the recommendations dict with the rule
    recommendations_dict = {RULE_KEY: [full_recommender_dict['sensors']['human_activities']['sitting']['rule'][language][2]]}

    # filter the DataFrame according to the rule
    har_risk_subjects_df = har_subject_metrics_df[
        har_subject_metrics_df['HAR_durations.Sentado_duration_sec'] > HAR_RULE_MAX_SITTING_TIME_SECONDS]

    # get the unique subjects
    risk_subjects = har_risk_subjects_df['subject_id'].unique().tolist()

    if subject_id in risk_subjects:

        # get rows that belong to subject
        subject_data = har_risk_subjects_df[har_risk_subjects_df['subject_id'] == subject_id]

        # count the number of instances
        num_instances = len(subject_data)

        # get the dates
        risk_dates = subject_data['date'].tolist()

        # transform dates to strings
        risk_dates = dates_to_weekdays(risk_dates, date_format="%d-%m-%Y", locale=language)

        # generate dict
        recommendations_dict[RISK_DATES_KEY] = risk_dates
        recommendations_dict[NUM_INSTANCES_KEY] = num_instances
        recommendations_dict[RECOMMENDATIONS_KEY] = \
        full_recommender_dict['sensors']['human_activities']['sitting']['recommendation'][language]

    else:

        # add that there are no recommendations needed
        recommendations_dict[RECOMMENDATIONS_KEY] = [NO_RECOMMENDATIONS[language]]

    return recommendations_dict


def get_continuous_sitting_recommendations(oh_profile: Dict,
                                           full_recommender_dict: Dict, activity_class_label: List[str] = None,
                                           exposure_limit_minutes: float = 60.0, language: str ='pt') -> Dict:
    """

    :param oh_profile:
    :param full_recommender_dict:
    :param activity_class_label:
    :param exposure_limit_minutes:
    :param language:
    :return:
    """

    # init the recommendations dict with the rule based on exposure limit number of instances to track
    if exposure_limit_minutes == HAR_EXPOSURE_LIMIT_1H:
        recommendations_dict = {
            RULE_KEY: [full_recommender_dict['sensors']['human_activities']['sitting']['rule'][language][0]]}

        instance_threshold = 1
    elif exposure_limit_minutes == HAR_EXPOSURE_LIMIT_2H:
        recommendations_dict = {
            RULE_KEY: [full_recommender_dict['sensors']['human_activities']['sitting']['rule'][language][1]]}

        instance_threshold = 0

    else:
        raise ValueError('Exposure limit must be either 60.0 min, or 120.0 min')

    # get the human activity metrics
    har_metrics = oh_profile['sensor_metrics']['human_activities']

    # evaluate the HAR timeline continuous risk
    risk_dates, total_num_instances = evaluate_continuous_timeline_risk(har_metrics, 'HAR_timeline', activity_class_label, exposure_limit_minutes, instance_threshold)

    # # init list for holding the dates and counter for tracking risk instances
    # risk_dates = []
    # total_num_instances = 0
    #
    # # cycle over the noise metrics
    # for acquisition_date, session_dict in har_metrics.items():
    #
    #     for acquisition_time, metrics_dict in session_dict.items():
    #
    #         har_timeline_dict = metrics_dict['HAR_timeline']
    #
    #         # get number of instances
    #         num_risk_instances = count_continuous_timeline_risk_breach(har_timeline_dict, activity_class_label, exposure_limit_minutes=exposure_limit_minutes)
    #
    #         if num_risk_instances >= instance_threshold:
    #             # add acquisition date to the list
    #             risk_dates.append(acquisition_date)
    #             total_num_instances += 1

    if len(risk_dates) > 0:

        # transform dates to strings
        risk_dates = dates_to_weekdays(risk_dates, date_format="%d-%m-%Y", locale=language)

        # generate dict
        recommendations_dict[RISK_DATES_KEY] = risk_dates
        recommendations_dict[NUM_INSTANCES_KEY] = total_num_instances
        recommendations_dict[RECOMMENDATIONS_KEY] = full_recommender_dict['sensors']['human_activities']['sitting']['recommendation'][language]

    else:

        # add that there are no recommendations needed
        recommendations_dict[RECOMMENDATIONS_KEY] = [NO_RECOMMENDATIONS[language]]

    return recommendations_dict

def get_standing_proportions_recommendations(har_subject_metrics_df: pd.DataFrame, subject_id: int,
                                           full_recommender_dict: Dict, language: str = 'pt') -> Dict:
    """

    :param har_subject_metrics_df:
    :param subject_id:
    :param full_recommender_dict:
    :param language:
    :return:
    """

    # init the recommendations dict with the rule
    recommendations_dict = {RULE_KEY: full_recommender_dict['sensors']['human_activities']['standing']['rule'][language]}

    # filter the DataFrame according to the rule
    har_risk_subjects_df = har_subject_metrics_df[har_subject_metrics_df['HAR_distributions.De pé'] > HAR_RULE_MAX_ACTIVITY_PERCENTAGE]

    # get the unique subjects
    risk_subjects = har_risk_subjects_df['subject_id'].unique().tolist()

    if subject_id in risk_subjects:

        # get rows that belong to subject
        subject_data = har_risk_subjects_df[har_risk_subjects_df['subject_id'] == subject_id]

        # count the number of instances
        num_instances = len(subject_data)

        # get the dates
        risk_dates = subject_data['date'].tolist()

        # transform dates to strings
        risk_dates = dates_to_weekdays(risk_dates, date_format="%d-%m-%Y", locale=language)

        # generate dict
        recommendations_dict[RISK_DATES_KEY] = risk_dates
        recommendations_dict[NUM_INSTANCES_KEY] = num_instances
        recommendations_dict[RECOMMENDATIONS_KEY] = full_recommender_dict['sensors']['human_activities']['standing']['recommendation'][language]

    else:

        # add that there are no recommendations needed
        recommendations_dict[RECOMMENDATIONS_KEY] = [NO_RECOMMENDATIONS[language]]

    return recommendations_dict


def get_steps_recommendations(har_subject_metrics_df: pd.DataFrame, subject_id: int,
                              full_recommender_dict: Dict, language: str = 'pt') -> Dict:
    """

    :param har_subject_metrics_df:
    :param subject_id:
    :param full_recommender_dict:
    :param language:
    :return:
    """

    # init the recommendations dict with the rule
    recommendations_dict = {
        RULE_KEY: full_recommender_dict['sensors']['human_activities']['walking']['rule'][language]}

    # filter the DataFrame according to the rule
    har_risk_subjects_df = har_subject_metrics_df[
        har_subject_metrics_df['HAR_steps.num_steps'] < HAR_RULE_MIN_STEPS]

    # get the unique subjects
    risk_subjects = har_risk_subjects_df['subject_id'].unique().tolist()

    if subject_id in risk_subjects:

        # get rows that belong to subject
        subject_data = har_risk_subjects_df[har_risk_subjects_df['subject_id'] == subject_id]

        # count the number of instances
        num_instances = len(subject_data)

        # get the dates
        risk_dates = subject_data['date'].tolist()

        # transform dates to strings
        risk_dates = dates_to_weekdays(risk_dates, date_format="%d-%m-%Y", locale=language)

        # generate dict
        recommendations_dict[RISK_DATES_KEY] = risk_dates
        recommendations_dict[NUM_INSTANCES_KEY] = num_instances
        recommendations_dict[RECOMMENDATIONS_KEY] = \
        full_recommender_dict['sensors']['human_activities']['walking']['recommendation'][language]

    else:

        # add that there are no recommendations needed
        recommendations_dict[RECOMMENDATIONS_KEY] = [NO_RECOMMENDATIONS[language]]

    return recommendations_dict




# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #