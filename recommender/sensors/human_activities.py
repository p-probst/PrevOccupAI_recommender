# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import sys
from pathlib import Path
import pandas as pd
from typing import Dict, List


# internal imports
from constants import RISK_DATES_KEY, NUM_INSTANCES_KEY, RECOMMENDATIONS_KEY, RULE_KEY, NO_RECOMMENDATIONS, USER, \
    SENSORS_KEY
from recommender.utils import dates_to_weekdays, evaluate_continuous_timeline_risk, get_language_mapper_values, \
    load_or_generate_csv

# external imports
project_path = Path(f"C:/Users/{USER}/PycharmProjects/OH_Toolkit")
sys.path.append(str(project_path))
from oh_parser import load_profiles, extract_nested
# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
HAR_CSV_FILENAME = "har_subject_metrics.csv"
HUMAN_ACTIVITIES_KEY = 'human_activities'

HAR_RULE_MAX_SITTING_TIME_SECONDS = 5.0 * 3600 # total of 5 hours of sitting
HAR_RULE_MAX_ACTIVITY_PERCENTAGE = 0.5 # 50 percent sitting during the day
HAR_RULE_MIN_STEPS = 700
HAR_EXPOSURE_LIMIT_1H = 60.0 # 60 minutes
HAR_EXPOSURE_LIMIT_2H = 120.0

HAR_MAPPING = {

    "Sentado": {"pt": "Sentado", "eng": "Sitting"},
    "De pé": {"pt": "De pé", "eng": "Standing"},
    "Sentado_duration_sec": {"pt": "Sentado_duration_sec", "eng": "sitting_duration_sec"},
    "num_steps": {"pt": "num_steps", "eng": "num_steps"}
}

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def generate_har_csv(har_data_csv_path: str | Path, oh_profile_path: str, language: str='pt') -> pd.DataFrame:
    """
    Load or generate the har subject-metrics CSV. This is generated based on the OH profiles of the entire
    worker population.

    If the CSV does not yet exist at the specified path, the OH profiles are parsed and the resulting DataFrame is saved.
    On subsequent calls the cached file is read directly, avoiding repeated profile parsing.

    :param har_data_csv_path: Directory in which the CSV is stored (or will be created)
    :param oh_profile_path: Path to folder containing the OH profile data of all subjects.
    :param language: the language in which the OH-profiles is written ('pt' or 'eng'). Default: 'pt'
    :return: DataFrame containing per-subject har metrics.
    """

    # get the values to be extracted
    values_to_extract = get_language_mapper_values(HAR_MAPPING, language)

    df_har_metrics = load_or_generate_csv(csv_dir=har_data_csv_path, filename=HAR_CSV_FILENAME,
                                          oh_profile_path=oh_profile_path,
                                          oh_metric_hierarchy="sensor_metrics.human_activities",
                                          level_names=["date", "session"],
                                          value_paths=[f"HAR_distributions.{values_to_extract[0]}",
                                                       f"HAR_distributions.{values_to_extract[1]}",
                                                       f"HAR_durations.{values_to_extract[2]}",
                                                       f"HAR_steps.{values_to_extract[3]}"])

    return df_har_metrics


def get_sitting_proportions_recommendations(har_subject_metrics_df: pd.DataFrame, subject_id: int,
                                           full_recommender_dict: Dict, language: str = 'pt') -> Dict:
    """
    Get recommendations for the daily sitting proportion. The recommendation is triggered when the subject spends
    more than HAR_RULE_MAX_ACTIVITY_PERCENTAGE of the day seated.
    :param har_subject_metrics_df: d.DataFrame containing the (all) subject metrics as extracted from the OH-profiles
    :param subject_id: the subject ID
    :param full_recommender_dict: The full recommendations JSON loaded as a dict.
    :param language: Output language code ('pt' or 'eng'). Default: 'pt'
    :return: Dict containing the recommendations for the subject as well as some metadata. The dict has the following keys:
             RECOMMENDATIONS_KEY = 'recommendations': list of strings containing the recommendations.
             RULE_KEY = 'rule': list of strings containing the applied rule(s).

             The following keys are ONLY included in case a risk was detected:
             RISK_DATES_KEY = 'risk_dates': list of strings containing the days on which risks were detected.
             NUM_INSTANCES_KEY = 'num_instances': int indicating the number of instances a risk was detected.
    """

    # define the har dimension
    har_dimension = 'sitting'

    # init the risk days and the number of detected risk instances
    risk_dates = []
    total_num_instances = 0

    # obtain the correct metric descriptor
    sitting_descriptor = get_language_mapper_values(HAR_MAPPING, language)[0]

    # get the rule
    rule = [full_recommender_dict[SENSORS_KEY][HUMAN_ACTIVITIES_KEY][har_dimension][RULE_KEY][language][3]]

    # filter the DataFrame according to the rule
    har_risk_subjects_df = har_subject_metrics_df[har_subject_metrics_df[f'HAR_distributions.{sitting_descriptor}'] > HAR_RULE_MAX_ACTIVITY_PERCENTAGE]

    # get the unique subjects
    risk_subjects = har_risk_subjects_df['subject_id'].unique().tolist()

    if subject_id in risk_subjects:

        # get rows that belong to subject
        subject_data = har_risk_subjects_df[har_risk_subjects_df['subject_id'] == subject_id]

        # count the number of instances
        total_num_instances = len(subject_data)

        # get the dates
        risk_dates = subject_data['date'].tolist()

    # generate recommendations
    recommendations_dict = _build_har_recommendations_dict(rule, risk_dates, total_num_instances, full_recommender_dict,
                                                           har_dimension, language)

    return recommendations_dict


def get_total_sitting_duration_recommendation(har_subject_metrics_df: pd.DataFrame, subject_id: int,
                                              full_recommender_dict: Dict, language: str = 'pt') -> Dict:
    """
    Get recommendations for the total daily sitting duration. The recommendation is triggered if the subjects sits longer
    than the defined time (HAR_RULE_MAX_SITTING_TIME_SECONDS)
    :param har_subject_metrics_df: d.DataFrame containing the (all) subject metrics as extracted from the OH-profiles
    :param subject_id: the subject ID
    :param full_recommender_dict: The full recommendations JSON loaded as a dict.
    :param language: Output language code ('pt' or 'eng'). Default: 'pt'
    :return: Dict containing the recommendations for the subject as well as some metadata. The dict has the following keys:
             RECOMMENDATIONS_KEY = 'recommendations': list of strings containing the recommendations.
             RULE_KEY = 'rule': list of strings containing the applied rule(s).

             The following keys are ONLY included in case a risk was detected:
             RISK_DATES_KEY = 'risk_dates': list of strings containing the days on which risks were detected.
             NUM_INSTANCES_KEY = 'num_instances': int indicating the number of instances a risk was detected.
    """

    # define the har dimension
    har_dimension = 'sitting'

    # init the risk days and the number of detected risk instances
    risk_dates = []
    total_num_instances = 0

    # obtain the correct metric descriptor
    sitting_descriptor = get_language_mapper_values(HAR_MAPPING, language)[2]

    # init the recommendations dict with the rule
    rule = [full_recommender_dict[SENSORS_KEY][HUMAN_ACTIVITIES_KEY][har_dimension][RULE_KEY][language][2]]

    # filter the DataFrame according to the rule
    har_risk_subjects_df = har_subject_metrics_df[
        har_subject_metrics_df[f'HAR_durations.{sitting_descriptor}'] > HAR_RULE_MAX_SITTING_TIME_SECONDS]

    # get the unique subjects
    risk_subjects = har_risk_subjects_df['subject_id'].unique().tolist()

    if subject_id in risk_subjects:

        # get rows that belong to subject
        subject_data = har_risk_subjects_df[har_risk_subjects_df['subject_id'] == subject_id]

        # count the number of instances
        total_num_instances = len(subject_data)

        # get the dates
        risk_dates = subject_data['date'].tolist()

    # generate recommendations
    recommendations_dict = _build_har_recommendations_dict(rule, risk_dates, total_num_instances,
                                                           full_recommender_dict,
                                                           har_dimension, language)

    return recommendations_dict


def get_continuous_sitting_recommendations(oh_profile: Dict,
                                           full_recommender_dict: Dict, activity_class_label: List[str] = None,
                                           exposure_limit_minutes: float = 60.0, language: str ='pt') -> Dict:
    """
    Gets recommendations for continuous sitting time. The recommendation is triggered either if the subjects sits longer
    than 1h or 2h.
    The function identifies extended sections in which the subject was continuously sitting.

    :param oh_profile: the subject OH-profile
    :param full_recommender_dict: The full recommendations JSON loaded as a dict.
    :param activity_class_label: the activity class for which the extended section should be evaluated.
    :param exposure_limit_minutes: the exposure limit in minutes
    :param language: Output language code ('pt' or 'eng'). Default: 'pt'
    :return: Dict containing the recommendations for the subject as well as some metadata. The dict has the following keys:
             RECOMMENDATIONS_KEY = 'recommendations': list of strings containing the recommendations.
             RULE_KEY = 'rule': list of strings containing the applied rule(s).

             The following keys are ONLY included in case a risk was detected:
             RISK_DATES_KEY = 'risk_dates': list of strings containing the days on which risks were detected.
             NUM_INSTANCES_KEY = 'num_instances': int indicating the number of instances a risk was detected.
    """

    # define HAR dimension
    har_dimension = 'sitting'

    # extract the rule based on which exposure limit is applied
    if exposure_limit_minutes == HAR_EXPOSURE_LIMIT_1H:
        rule = [full_recommender_dict[SENSORS_KEY][HUMAN_ACTIVITIES_KEY][har_dimension][RULE_KEY][language][0]]

        # set instance threshold (for one hour exposure at least two sections i.e., > 1)
        instance_threshold = 1
    elif exposure_limit_minutes == HAR_EXPOSURE_LIMIT_2H:
        rule = [full_recommender_dict[SENSORS_KEY][HUMAN_ACTIVITIES_KEY][har_dimension][RULE_KEY][language][1]]

        # set instance threshold (for one hour exposure at least one section i.e., > 0)
        instance_threshold = 0

    else:
        raise ValueError('Exposure limit must be either 60.0 min, or 120.0 min')

    # get the human activity metrics
    har_metrics = oh_profile['sensor_metrics'][HUMAN_ACTIVITIES_KEY]

    # evaluate the HAR timeline continuous risk
    risk_dates, total_num_instances = evaluate_continuous_timeline_risk(har_metrics, 'HAR_timeline', activity_class_label, exposure_limit_minutes, instance_threshold)

    # generate recommendations
    recommendations_dict = _build_har_recommendations_dict(rule, risk_dates, total_num_instances,
                                                           full_recommender_dict,
                                                           har_dimension, language)

    return recommendations_dict

def get_standing_proportions_recommendations(har_subject_metrics_df: pd.DataFrame, subject_id: int,
                                           full_recommender_dict: Dict, language: str = 'pt') -> Dict:
    """
    Get recommendations for the daily standing proportion. The recommendation is triggered when the subject spends
    more than HAR_RULE_MAX_ACTIVITY_PERCENTAGE of the day standing.
    :param har_subject_metrics_df: d.DataFrame containing the (all) subject metrics as extracted from the OH-profiles
    :param subject_id: the subject ID
    :param full_recommender_dict: The full recommendations JSON loaded as a dict.
    :param language: Output language code ('pt' or 'eng'). Default: 'pt'
    :return: Dict containing the recommendations for the subject as well as some metadata. The dict has the following keys:
             RECOMMENDATIONS_KEY = 'recommendations': list of strings containing the recommendations.
             RULE_KEY = 'rule': list of strings containing the applied rule(s).

             The following keys are ONLY included in case a risk was detected:
             RISK_DATES_KEY = 'risk_dates': list of strings containing the days on which risks were detected.
             NUM_INSTANCES_KEY = 'num_instances': int indicating the number of instances a risk was detected.
    """

    # define the har dimension
    har_dimension = 'standing'

    # init the risk days and the number of detected risk instances
    risk_dates = []
    total_num_instances = 0

    # obtain the correct metric descriptor
    standing_descriptor = get_language_mapper_values(HAR_MAPPING, language)[1]

    # get the rule
    rule = [full_recommender_dict[SENSORS_KEY][HUMAN_ACTIVITIES_KEY][har_dimension][RULE_KEY][language]]

    # filter the DataFrame according to the rule
    har_risk_subjects_df = har_subject_metrics_df[har_subject_metrics_df[f'HAR_distributions.{standing_descriptor}'] > HAR_RULE_MAX_ACTIVITY_PERCENTAGE]

    # get the unique subjects
    risk_subjects = har_risk_subjects_df['subject_id'].unique().tolist()

    if subject_id in risk_subjects:

        # get rows that belong to subject
        subject_data = har_risk_subjects_df[har_risk_subjects_df['subject_id'] == subject_id]

        # count the number of instances
        total_num_instances = len(subject_data)

        # get the dates
        risk_dates = subject_data['date'].tolist()

    # generate recommendations
    recommendations_dict = _build_har_recommendations_dict(rule, risk_dates, total_num_instances,
                                                           full_recommender_dict,
                                                           har_dimension, language)

    return recommendations_dict


def get_steps_recommendations(har_subject_metrics_df: pd.DataFrame, subject_id: int,
                              full_recommender_dict: Dict, language: str = 'pt') -> Dict:
    """
    Gets recommendations based on the daily step count. The recommendation is triggered when the daily step count falls
    below HAR_RULE_MIN_STEPS.
    :param har_subject_metrics_df: d.DataFrame containing the (all) subject metrics as extracted from the OH-profiles
    :param subject_id: the subject ID
    :param full_recommender_dict: The full recommendations JSON loaded as a dict.
    :param language: Output language code ('pt' or 'eng'). Default: 'pt'
    :return: Dict containing the recommendations for the subject as well as some metadata. The dict has the following keys:
             RECOMMENDATIONS_KEY = 'recommendations': list of strings containing the recommendations.
             RULE_KEY = 'rule': list of strings containing the applied rule(s).

             The following keys are ONLY included in case a risk was detected:
             RISK_DATES_KEY = 'risk_dates': list of strings containing the days on which risks were detected.
             NUM_INSTANCES_KEY = 'num_instances': int indicating the number of instances a risk was detected.
    """

    # define the har dimension
    har_dimension = 'walking'

    # init the risk days and the number of detected risk instances
    risk_dates = []
    total_num_instances = 0

    # obtain the correct metric descriptor
    step_descriptor = get_language_mapper_values(HAR_MAPPING, language)[3]

    # init the recommendations dict with the rule
    rule = [full_recommender_dict[SENSORS_KEY][HUMAN_ACTIVITIES_KEY][har_dimension][RULE_KEY][language]]

    # filter the DataFrame according to the rule
    har_risk_subjects_df = har_subject_metrics_df[
        har_subject_metrics_df['HAR_steps.num_steps'] < HAR_RULE_MIN_STEPS]

    # get the unique subjects
    risk_subjects = har_risk_subjects_df['subject_id'].unique().tolist()

    if subject_id in risk_subjects:

        # get rows that belong to subject
        subject_data = har_risk_subjects_df[har_risk_subjects_df['subject_id'] == subject_id]

        # count the number of instances
        total_num_instances = len(subject_data)

        # get the dates
        risk_dates = subject_data['date'].tolist()

    # generate recommendations
    recommendations_dict = _build_har_recommendations_dict(rule, risk_dates, total_num_instances,
                                                           full_recommender_dict,
                                                           har_dimension, language)

    return recommendations_dict




# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #
def _build_har_recommendations_dict(rule: list, risk_dates: list, total_num_risk_instances: int,
                                    full_recommender_dict: Dict, har_dimension: str, language: str = 'pt'):
    """
    function to build the full recommendation dictionary for human activity-related recommendations..

    The recommendation dictionary contains the following keys:
    RECOMMENDATIONS_KEY = 'recommendations': list of strings containing the recommendations.
    RULE_KEY = 'rule': list of strings containing the applied rule(s).

    The following keys are ONLY included in case a risk was detected:
    RISK_DATES_KEY = 'risk_dates': list of strings containing the days on which risks were detected.
    NUM_INSTANCES_KEY = 'num_instances': int indicating the number of instances a risk was detected.

    :param rule: the rules as extracted from recommendations.json.
    :param risk_dates: list of date strings containing the days on which risks were detected.
    :param total_num_risk_instances: the total number of risk instances detected.
    :param full_recommender_dict: the full recommendations JSON loaded as a dict.
    :param har_dimension: the human activity dimension used in the recommendations.json. (e.g., sitting, standing, walking)
    :param language: Output language code ('pt' or 'eng'). Default: 'pt'
    :return: dictionary containing the recommendations and the described metadata if risks were detected.
    """

    # init the recommendations dictionary
    recommendations_dict = {RULE_KEY: rule}

    # check the length of the risk_dates. This indicates whether risks were detected or not
    if len(risk_dates) > 0:

        # transform the dates to strings
        risk_dates = dates_to_weekdays(risk_dates, date_format="%d-%m-%Y", locale=language)

        # generate the recommendation dictionary together with the metadata
        recommendations_dict[RISK_DATES_KEY] = risk_dates
        recommendations_dict[NUM_INSTANCES_KEY] = total_num_risk_instances
        recommendations_dict[RECOMMENDATIONS_KEY] = \
        full_recommender_dict['sensors']['human_activities'][har_dimension]['recommendation'][language]

    else:

        # add that there are no recommendations needed
        recommendations_dict[RECOMMENDATIONS_KEY] = [NO_RECOMMENDATIONS[language]]

    return recommendations_dict