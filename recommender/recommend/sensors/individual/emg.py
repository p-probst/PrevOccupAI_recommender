# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pandas as pd
from typing import Dict

# internal imports
from constants import  RULE_KEY, SENSORS_KEY
from recommender.load.language_mappings import EMG_MAPPING
from recommender.utils import get_language_mapper_values, build_sensor_recommendations_dict, evaluate_subject_risk_with_mental_strain

# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
EMG_HIGH_THRESHOLD = 30.0 # 30 percent
EMG_TYPICAL_HIGH_THRESHOLD = 25.0 # 25 percent
NUM_INSTANCES_HIGH_EMG = 2
MAX_THRESHOLD_WORKLOAD = 3

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def get_emg_recommendations(emg_subject_metrics_df: pd.DataFrame, oh_profile: Dict, subject_id: int,
                            emg_class: str, max_instances: int,
                            full_recommender_dict: Dict, language: str = 'pt') -> Dict:
    """
    Gets the EMG recommendations for a given subject. The recommendation is triggered when
    1.) A set percentage of either 'typical high' (30%) or 'high for you' (25%) is detected for at leas two recording
        session within a day.
    AND
    2.) The mean of the workload questionnaire for the identified items 'focus_and_mental_strain', '
        rushed_and_under_pressure', and 'heavy_workload' is above three.
    :param emg_subject_metrics_df: pandas.DataFrame containing the EMG subject metrics (of all subjects) as extracted from the OH-profiles
    :param oh_profile: the subject OH-profile
    :param subject_id: the subject ID
    :param emg_class: the EMG class for which the recommendation should be returned.
    :param max_instances: the number of instances on that should be accumulated during a day for the recommendation to be triggered.
    :param full_recommender_dict: The full recommendations JSON loaded as a dict.
    :param language: Output language code ('pt' or 'eng'). Default: 'pt'
    :return:
    """

    # define sensor dimension
    sensor_dimension = 'emg'

    # get the sub-dictionary containing the rule and the recommendations
    sensor_recommender_dict = full_recommender_dict[SENSORS_KEY][sensor_dimension]

    # get the correct metric descriptors
    emg_classes = get_language_mapper_values(EMG_MAPPING, language)

    # check emg class and init the recommendations dict with corresponding rule
    if emg_class == emg_classes[1]:

        # get the rule
        rule = [sensor_recommender_dict[RULE_KEY][language][0]]

        # get the corresponding threshold
        emg_threshold = EMG_HIGH_THRESHOLD
    elif emg_class == emg_classes[0]:

        # get the rule
        rule = [sensor_recommender_dict[RULE_KEY][language][1]]

        # get the corresponding threshold
        emg_threshold = EMG_TYPICAL_HIGH_THRESHOLD

    else:
        raise ValueError(f"emg_class must be one of the following: {emg_classes}")

    # init list for holding the dates and counter for tracking risk instances
    risk_dates = set()
    total_num_instances = 0

    # cycle over left and right
    for emg_side in ['left', 'right']:

        # filter the DataFrame according to the rule
        emg_risk_subjects_df = emg_subject_metrics_df[emg_subject_metrics_df[f'{emg_side}.EMG_relative_bins.{emg_class}'] > emg_threshold]

        risk_dates_side, num_instances_side = evaluate_subject_risk_with_mental_strain(emg_risk_subjects_df, subject_id,
                                                                                       oh_profile, max_instances,
                                                                                       MAX_THRESHOLD_WORKLOAD)
        # update the number instances and the dates
        total_num_instances += num_instances_side
        risk_dates.update(risk_dates_side)

    # generate recommendations
    recommendations_dict = build_sensor_recommendations_dict(rule, risk_dates, total_num_instances,
                                                             sensor_recommender_dict, language)

    return recommendations_dict





# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #