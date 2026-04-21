# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import sys
from pathlib import Path
import pandas as pd
from typing import Dict, List


# internal imports
from constants import RULE_KEY, USER, SENSORS_KEY
from recommender.utils import get_language_mapper_values, load_or_generate_csv, \
                              evaluate_subject_risk_with_mental_strain, build_sensor_recommendations_dict

# external imports
project_path = Path(f"C:/Users/{USER}/PycharmProjects/OH_Toolkit")
sys.path.append(str(project_path))
from oh_parser import load_profiles, extract_nested

# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
HR_CSV_FILENAME = "hr_subject_metrics.csv"

MAX_HR_THRESHOLD = 100
NUM_INSTANCES_MAX_HR = 2
SLIGHTLY_ELEVATED_HR_THRESHOLD = 0.25  # 25 percent
NUM_INSTANCES_ELEVATED_HR = 2
ELEVATED_HR_THRESHOLD = 0.125  # 12.5 percent
MAX_THRESHOLD_WORKLOAD = 3

HEART_RATE_MAPPING = {

    "max": {"pt": "max", "eng": "max"},
    "Ligeiramente elevado": {"pt": "Ligeiramente elevado", "eng": "Slightly elevated"},
    "Elevado": {"pt": "Elevado", "eng": "Elevated"},
}

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def generate_hr_csv(hr_data_csv_path: str | Path, oh_profile_path: str, language: str='pt') -> pd.DataFrame:
    """
    Load or generate the heart rate subject-metrics CSV. This is generated based on the OH-profiles of the entire
    worker population.
    :param hr_data_csv_path: Directory in which the CSV is stored (or will be created)
    :param oh_profile_path: Path to folder containing the OH profile data of all subjects.
    :param language: the language in which the OH-profiles is written ('pt' or 'eng'). Default: 'pt'
    :return: pandas.DataFrame containing per-subject heart rate metrics
    """

    # get the values to be extracted
    values_to_extract = get_language_mapper_values(HEART_RATE_MAPPING, language)

    # load or generate the DataFrame
    df_hr_metrics = load_or_generate_csv(csv_dir=hr_data_csv_path, filename=HR_CSV_FILENAME,
                                         oh_profile_path=oh_profile_path,
                                         oh_metric_hierarchy="sensor_metrics.heart_rate",
                                         level_names=["date", "session"],
                                         value_paths=[f"HR_BPM_stats.{values_to_extract[0]}",
                                                      f"HR_distributions.{values_to_extract[1]}",
                                                      f"HR_distributions.{values_to_extract[2]}",])

    return df_hr_metrics


def get_max_frequency_recommendation(hr_subject_metrics_df: pd.DataFrame, oh_profile: Dict, subject_id: int,
                                     full_recommender_dict: Dict, language: str = 'pt') -> Dict:
    """
    Gets the recommendations for the maximum frequency of the heart rate for a single subject. The recommendation is
    triggered when
    1.) The maximum heart rate is above 100 BPM during at least two sessions a day.
    AND
    2.) The mean of the workload questionnaire for the identified items 'focus_and_mental_strain', '
        rushed_and_under_pressure', and 'heavy_workload' is above three.
    :param hr_subject_metrics_df: pandas.DataFrame containing the heart rate subject metrics (of all subjects) as extracted from the OH-profiles
    :param oh_profile: the subject's OH-profile
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

    # define sensor dimension
    sensor_dimension = 'heart_rate'

    # get the sub-dictionary containing the rule and the recommendations
    sensor_recommender_dict = full_recommender_dict[SENSORS_KEY][sensor_dimension]

    # get the correct metric descriptor
    hr_descriptor = get_language_mapper_values(HEART_RATE_MAPPING, language)[0]

    # init the recommendations dict with the rule
    rule = [sensor_recommender_dict[RULE_KEY][language][0]]

    # filter the DataFrame according to the rule
    hr_risk_subjects_df = hr_subject_metrics_df[hr_subject_metrics_df[f'HR_BPM_stats.{hr_descriptor}'] > MAX_HR_THRESHOLD]

    # check whether the subject falls into the risk subject and expressed high mental strain
    risk_dates, total_num_instances = evaluate_subject_risk_with_mental_strain(hr_risk_subjects_df, subject_id,
                                                                               oh_profile,NUM_INSTANCES_MAX_HR,
                                                                               MAX_THRESHOLD_WORKLOAD)

    # generate recommendations
    recommendations_dict = build_sensor_recommendations_dict(rule, risk_dates, total_num_instances,
                                                             sensor_recommender_dict, language)

    return recommendations_dict


def get_elevated_hr_recommendations(hr_subject_metrics_df: pd.DataFrame, oh_profile: Dict, subject_id: int,
                                      hr_class: str, full_recommender_dict: Dict, language: str = 'pt') -> Dict:
    """
    Get recommendations for the elevated heart rate for single subject. The recommendation is triggered when
    1.) A set percentage of either the 'slightly elevated' (25%) or 'elevated' (12.5%) is detected for at least two recording
        session within a day.
    AND
    2.) The mean of the workload questionnaire for the identified items 'focus_and_mental_strain', '
        rushed_and_under_pressure', and 'heavy_workload' is above three.
    :param hr_subject_metrics_df: pandas.DataFrame containing the heart rate subject metrics (of all subjects) as extracted from the OH-profiles
    :param oh_profile: the subject OH-profile
    :param subject_id: the subject ID
    :param hr_class: the heart rate class for which the recommendation should be returned.
    :param full_recommender_dict: The full recommendations JSON loaded as a dict.
    :param language: Output language code ('pt' or 'eng'). Default: 'pt'
    :return: Dict containing the recommendations for the subject as well as some metadata. The dict has the following keys:
             RECOMMENDATIONS_KEY = 'recommendations': list of strings containing the recommendations.
             RULE_KEY = 'rule': list of strings containing the applied rule(s).

             The following keys are ONLY included in case a risk was detected:
             RISK_DATES_KEY = 'risk_dates': list of strings containing the days on which risks were detected.
             NUM_INSTANCES_KEY = 'num_instances': int indicating the number of instances a risk was detected.
    """

    # define sensor dimension
    sensor_dimension = 'heart_rate'

    # get the sub-dictionary containing the rule and the recommendations
    sensor_recommender_dict = full_recommender_dict[SENSORS_KEY][sensor_dimension]

    # get the correct metric descriptors (only the last two needed)
    hr_classes = get_language_mapper_values(HEART_RATE_MAPPING, language)[1:]

    # check hr class and init the recommendations dict with corresponding rule
    if hr_class == hr_classes[0]:

        # extract the rule
        rule = [sensor_recommender_dict[RULE_KEY][language][1]]

        # get the corresponding threshold
        hr_threshold = SLIGHTLY_ELEVATED_HR_THRESHOLD
    elif hr_class == hr_classes[1]:
        rule = [sensor_recommender_dict[RULE_KEY][language][2]]

        # get the corresponding threshold
        hr_threshold = ELEVATED_HR_THRESHOLD

    else:
        raise ValueError(f"hr_class must be one of the following: {hr_classes}")


    # filter the DataFrame according to the rule
    hr_risk_subjects_df = hr_subject_metrics_df[hr_subject_metrics_df[f'HR_distributions.{hr_class}'] > hr_threshold]

    # check whether the subject falls into the risk subject and expressed high mental strain
    risk_dates, total_num_instances = evaluate_subject_risk_with_mental_strain(hr_risk_subjects_df, subject_id,
                                                                               oh_profile, NUM_INSTANCES_ELEVATED_HR,
                                                                               MAX_THRESHOLD_WORKLOAD)

    # generate recommendations
    recommendations_dict = build_sensor_recommendations_dict(rule, risk_dates, total_num_instances,
                                                             sensor_recommender_dict, language)

    return recommendations_dict


# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #