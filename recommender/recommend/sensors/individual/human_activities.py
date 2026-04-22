# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pandas as pd
from typing import Dict, List


# internal imports
from constants import RULE_KEY, SENSORS_KEY
from recommender.load.language_mappings import HAR_MAPPING
from recommender.utils import evaluate_continuous_timeline_risk, get_language_mapper_values, \
                               evaluate_subject_risk, build_sensor_recommendations_dict

# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
HUMAN_ACTIVITIES_KEY = 'human_activities'

HAR_RULE_MAX_SITTING_TIME_SECONDS = 5.0 * 3600 # total of 5 hours of sitting
HAR_RULE_MAX_ACTIVITY_PERCENTAGE = 0.5 # 50 percent sitting during the day
HAR_RULE_MIN_STEPS = 700
HAR_EXPOSURE_LIMIT_1H = 60.0 # 60 minutes
HAR_EXPOSURE_LIMIT_2H = 120.0

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def get_sitting_proportions_recommendations(har_subject_metrics_df: pd.DataFrame, subject_id: int,
                                           full_recommender_dict: Dict, language: str = 'pt') -> Dict:
    """
    Get recommendations for the daily sitting proportion. The recommendation is triggered when the subject spends
    more than HAR_RULE_MAX_ACTIVITY_PERCENTAGE of the day seated.
    :param har_subject_metrics_df: pandas.DataFrame containing the (all) subject metrics as extracted from the OH-profiles
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

    # get the sub-dictionary containing the rule and the recommendation
    sensor_recommender_dict = full_recommender_dict[SENSORS_KEY][HUMAN_ACTIVITIES_KEY][har_dimension]

    # obtain the correct metric descriptor
    sitting_descriptor = get_language_mapper_values(HAR_MAPPING, language)[0]

    # get the rule
    rule = [sensor_recommender_dict[RULE_KEY][language][3]]

    # filter the DataFrame according to the rule
    har_risk_subjects_df = har_subject_metrics_df[har_subject_metrics_df[f'HAR_distributions.{sitting_descriptor}']
                                                  > HAR_RULE_MAX_ACTIVITY_PERCENTAGE]

    # check whether the subject is part of the risk subjects
    risk_dates, total_num_instances = evaluate_subject_risk(har_risk_subjects_df, subject_id)

    # generate recommendations
    recommendations_dict = build_sensor_recommendations_dict(rule, risk_dates, total_num_instances,
                                                             sensor_recommender_dict, language)

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

    # get the sub-dictionary containing the rule and the recommendation
    sensor_recommender_dict = full_recommender_dict[SENSORS_KEY][HUMAN_ACTIVITIES_KEY][har_dimension]

    # obtain the correct metric descriptor
    sitting_descriptor = get_language_mapper_values(HAR_MAPPING, language)[2]

    # init the recommendations dict with the rule
    rule = [sensor_recommender_dict[RULE_KEY][language][2]]

    # filter the DataFrame according to the rule
    har_risk_subjects_df = har_subject_metrics_df[har_subject_metrics_df[f'HAR_durations.{sitting_descriptor}']
                                                  > HAR_RULE_MAX_SITTING_TIME_SECONDS]

    # check whether the subject is part of the risk subjects
    risk_dates, total_num_instances = evaluate_subject_risk(har_risk_subjects_df, subject_id)

    # generate recommendations
    recommendations_dict = build_sensor_recommendations_dict(rule, risk_dates, total_num_instances,
                                                             sensor_recommender_dict, language)


    return recommendations_dict


def get_continuous_sitting_recommendations(oh_profile: Dict,
                                           full_recommender_dict: Dict, activity_class_label: List[str] = None,
                                           exposure_limit_minutes: float = 60.0, language: str ='pt') -> Dict:
    """
    Gets recommendations for continuous sitting time. The recommendation is triggered either if the subjects sits longer
    than 1h or 2h.
    The function identifies extended sections in which the subject was continuously sitting.

    :param oh_profile: the subject's OH-profile
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

    # get the sub-dictionary containing the rule and recommendations
    sensor_recommender_dict = full_recommender_dict[SENSORS_KEY][HUMAN_ACTIVITIES_KEY][har_dimension]

    # extract the rule based on which exposure limit is applied
    if exposure_limit_minutes == HAR_EXPOSURE_LIMIT_1H:
        rule = [sensor_recommender_dict[RULE_KEY][language][0]]

        # set instance threshold (for one hour exposure at least two sections i.e., > 1)
        instance_threshold = 1
    elif exposure_limit_minutes == HAR_EXPOSURE_LIMIT_2H:
        rule = [sensor_recommender_dict[RULE_KEY][language][1]]

        # set instance threshold (for one hour exposure at least one section i.e., > 0)
        instance_threshold = 0

    else:
        raise ValueError('Exposure limit must be either 60.0 min, or 120.0 min')

    # get the human activity metrics
    har_metrics = oh_profile['sensor_metrics'][HUMAN_ACTIVITIES_KEY]

    # evaluate the HAR timeline continuous risk
    risk_dates, total_num_instances = evaluate_continuous_timeline_risk(har_metrics, 'HAR_timeline',
                                                                        activity_class_label, exposure_limit_minutes,
                                                                        instance_threshold)

    # generate recommendations
    recommendations_dict = build_sensor_recommendations_dict(rule, risk_dates, total_num_instances,
                                                             sensor_recommender_dict, language)

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

    # get the sub-dictionary containing the rule and recommendations
    sensor_recommender_dict = full_recommender_dict[SENSORS_KEY][HUMAN_ACTIVITIES_KEY][har_dimension]

    # obtain the correct metric descriptor
    standing_descriptor = get_language_mapper_values(HAR_MAPPING, language)[1]

    # get the rule
    rule = sensor_recommender_dict[RULE_KEY][language]

    # filter the DataFrame according to the rule
    har_risk_subjects_df = har_subject_metrics_df[har_subject_metrics_df[f'HAR_distributions.{standing_descriptor}']
                                                  > HAR_RULE_MAX_ACTIVITY_PERCENTAGE]

    # check whether the subject is part of the risk subjects
    risk_dates, total_num_instances = evaluate_subject_risk(har_risk_subjects_df, subject_id)

    # generate recommendations
    recommendations_dict = build_sensor_recommendations_dict(rule, risk_dates, total_num_instances,
                                                             sensor_recommender_dict, language)

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

    # get the sub-dictionary containing the rule and recommendations
    sensor_recommender_dict = full_recommender_dict[SENSORS_KEY][HUMAN_ACTIVITIES_KEY][har_dimension]

    # obtain the correct metric descriptor
    step_descriptor = get_language_mapper_values(HAR_MAPPING, language)[3]

    # init the recommendations dict with the rule
    rule = sensor_recommender_dict[RULE_KEY][language]

    # filter the DataFrame according to the rule
    har_risk_subjects_df = har_subject_metrics_df[har_subject_metrics_df[f'HAR_steps.{step_descriptor}']
                                                  < HAR_RULE_MIN_STEPS]

    # check whether the subject is part of the risk subjects
    risk_dates, total_num_instances = evaluate_subject_risk(har_risk_subjects_df, subject_id)

    # generate recommendations
    recommendations_dict = build_sensor_recommendations_dict(rule, risk_dates, total_num_instances,
                                                             sensor_recommender_dict, language)

    return recommendations_dict


# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #
