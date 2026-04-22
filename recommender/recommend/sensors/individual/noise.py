# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
from typing import Dict, List
import pandas as pd

# internal imports
from constants import SENSORS_KEY, RULE_KEY
from recommender.load.language_mappings import NOISE_MAPPING
from recommender.load.sensors import LOUD_NOISE_SUM
from recommender.utils import evaluate_continuous_timeline_risk, load_or_generate_csv, \
                              get_language_mapper_values, build_sensor_recommendations_dict, evaluate_subject_risk


# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
NOISE_RULE_MAX_LOUD_NOISE_PERCENTAGE = 0.5

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def get_continuous_noise_recommendations(oh_profile: Dict,
                                         full_recommender_dict: Dict,
                                         noise_level_label: List[str] = None,
                                         exposure_limit_minutes: float = 60.0, language: str ='pt') -> Dict:
    """
    Gets recommendations for continuous noise for a single subject.

    The function identifies using the subject's OH-profile, extended sections in which the subject was exposed to
    disruptive or high noise for more than 60 minutes.
    :param oh_profile: the subject's OH-profile
    :param full_recommender_dict:The full recommendations JSON loaded as a dict.
    :param noise_level_label: list of the labels of the classes for which the noise exposure should be evaluated
    :param exposure_limit_minutes: the exposure limit in minutes
    :param language: Output language code ('pt' or 'eng'). Default: 'pt'
    :return: Dict containing the recommendations for the subject as well as some metadata. The dict has the following keys:
             RECOMMENDATIONS_KEY = 'recommendations': list of strings containing the recommendations.
             RULE_KEY = 'rule': list of strings containing the applied rule(s).

             The following keys are ONLY included in case a risk was detected:
             RISK_DATES_KEY = 'risk_dates': list of strings containing the days on which risks were detected.
             NUM_INSTANCES_KEY = 'num_instances': int indicating the number of instances a risk was detected.
    """

    # define the sensor dimension
    sensor_dimension = 'noise'

    # get the sub-dictionary containing the rule and the recommendation
    sensor_recommender_dict = full_recommender_dict[SENSORS_KEY][sensor_dimension]

    # get the noise metrics from the OH profile
    noise_metrics = oh_profile['sensor_metrics'][sensor_dimension]

    # extract the rule upon which the recommendation is evaluated
    rule = [sensor_recommender_dict[RULE_KEY][language][0]]

    # get the noise timeline key
    # TODO: currently has to be extracted in english as the portuguese version of the OH-profile does not exist yet
    noise_timeline_key = get_language_mapper_values(NOISE_MAPPING, 'eng')[-1]

    # evaluate the noise timeline continuous risk
    risk_dates, total_num_instances = evaluate_continuous_timeline_risk(noise_metrics, noise_timeline_key, noise_level_label, exposure_limit_minutes, 0)

    # generate the recommendations dictionary
    recommendations_dict = build_sensor_recommendations_dict(rule, risk_dates, total_num_instances,
                                                             sensor_recommender_dict, language)

    return recommendations_dict


def get_noise_exposure_recommendations(noise_subject_metrics: pd.DataFrame, subject_id: int, full_recommender_dict: Dict, language: str = 'pt') -> Dict:
    """
    Get overall noise exposure recommendations for a single subject.
    :param noise_subject_metrics: pd.DataFrame containing the (all) subject metrics as extracted from the OH-profiles
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

    # define the sensor dimension
    sensor_dimension = 'noise'

    # get the sub-dictionary containing the rule and the recommendations
    sensor_recommender_dict = full_recommender_dict[SENSORS_KEY][sensor_dimension]

    # get the rule
    rule = [sensor_recommender_dict[RULE_KEY][language][1]]

    # filter the DataFrame to only contain subjects that exceed the noise rule
    noise_risk_subjects = noise_subject_metrics[noise_subject_metrics[LOUD_NOISE_SUM] >= NOISE_RULE_MAX_LOUD_NOISE_PERCENTAGE]

    # check whether the subject is part of the risk subjects
    risk_dates, total_num_instances = evaluate_subject_risk(noise_risk_subjects, subject_id)

    # generate the recommendations
    recommendations_dict = build_sensor_recommendations_dict(rule, risk_dates, total_num_instances,
                                                             sensor_recommender_dict, language)

    return recommendations_dict


# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #