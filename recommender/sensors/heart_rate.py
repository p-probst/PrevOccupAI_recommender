# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import sys
from pathlib import Path
import pandas as pd
from typing import Dict, List


# internal imports
from constants import RISK_DATES_KEY, NUM_INSTANCES_KEY, RECOMMENDATIONS_KEY, RULE_KEY, NO_RECOMMENDATIONS, USER
from recommender.utils import dates_to_weekdays, get_mean_workload_score

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

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def generate_hr_csv(hr_data_csv_path: str | Path, oh_profile_path: str) -> pd.DataFrame:
    """

    :param hr_data_csv_path:
    :param oh_profile_path:
    :return:
    """

    if not (Path(hr_data_csv_path) / HR_CSV_FILENAME).exists():
        # load the profiles
        profiles = load_profiles(oh_profile_path)

        # parse the noise metrics
        df_sessions = extract_nested(
            profiles,
            base_path="sensor_metrics.heart_rate",
            level_names=["date", "session"],
            value_paths=[
                "HR_BPM_stats.max",
                "HR_distributions.Ligeiramente elevado",
                "HR_distributions.Elevado"

            ],
            exclude_patterns=[],
        )

        # save the DataFrame
        df_sessions.to_csv(HR_CSV_FILENAME, index=False)

    else:
        df_sessions = pd.read_csv(HR_CSV_FILENAME)

    return df_sessions


def get_max_frequency_recommendation(hr_subject_metrics_df: pd.DataFrame, oh_profile: Dict, subject_id: int,
                                     full_recommender_dict: Dict, language: str = 'pt') -> Dict:
    """

    :param hr_subject_metrics_df:
    :param oh_profile:
    :param subject_id:
    :param full_recommender_dict:
    :param language:
    :return:
    """

    # init the recommendations dict with the rule
    recommendations_dict = {RULE_KEY: [full_recommender_dict['sensors']['heart_rate']['rule'][language][0]]}

    # filter the DataFrame according to the rule
    hr_risk_subjects_df = hr_subject_metrics_df[hr_subject_metrics_df['HR_BPM_stats.max'] > MAX_HR_THRESHOLD]

    # get the unique subjects
    risk_subjects = hr_risk_subjects_df['subject_id'].unique().tolist()

    # init list for holding the dates and counter for tracking risk instances
    risk_dates = []
    total_num_instances = 0

    if subject_id in risk_subjects:

        # get rows that belong to subject
        subject_data = hr_risk_subjects_df[hr_risk_subjects_df['subject_id'] == subject_id]

        # perform groupby by date to check the number of instances per day
        for acquisition_date, date_df in subject_data.groupby('date'):

            if len(date_df) >= NUM_INSTANCES_MAX_HR:

                # get workload dict for the day
                day_workload_dict = oh_profile['daily_questionnaires']['workload'][acquisition_date]

                # calculate the mean of the workload questions
                workload_mean = get_mean_workload_score(day_workload_dict, ['focus_and_mental_strain', 'rushed_and_under_pressure', 'heavy_workload'])

                if workload_mean >= MAX_THRESHOLD_WORKLOAD:

                    # update total number of instances
                    total_num_instances += 1

                    # add the date to the list
                    risk_dates.append(acquisition_date)

    if len(risk_dates) > 0:
        # transform dates to strings
        risk_dates = dates_to_weekdays(risk_dates, date_format="%d-%m-%Y", locale=language)

        # generate dict
        recommendations_dict[RISK_DATES_KEY] = risk_dates
        recommendations_dict[NUM_INSTANCES_KEY] = total_num_instances
        recommendations_dict[RECOMMENDATIONS_KEY] = \
        full_recommender_dict['sensors']['heart_rate']['recommendation'][language]

    else:

        # add that there are no recommendations needed
        recommendations_dict[RECOMMENDATIONS_KEY] = [NO_RECOMMENDATIONS[language]]

    return recommendations_dict


def get_elevated_hr_recommendations(hr_subject_metrics_df: pd.DataFrame, oh_profile: Dict, subject_id: int,
                                      hr_class: str, full_recommender_dict: Dict, language: str = 'pt') -> Dict:
    """

    :param hr_subject_metrics_df:
    :param oh_profile:
    :param subject_id:
    :param hr_class:
    :param full_recommender_dict:
    :param language:
    :return:
    """

    # init the recommendations dict with the rule
    recommendations_dict = {RULE_KEY: full_recommender_dict['sensors']['heart_rate']['rule'][language][1:3]}

    # get threshold based on hr class
    if hr_class == 'Ligeiramente elevado':
        hr_threshold = SLIGHTLY_ELEVATED_HR_THRESHOLD
    elif hr_class == 'Elevado':
        hr_threshold = ELEVATED_HR_THRESHOLD
    else:
        raise ValueError("The hr_class must be 'Ligeiramente elevado' or 'Elevado'")

    # filter the DataFrame according to the rule
    hr_risk_subjects_df = hr_subject_metrics_df[hr_subject_metrics_df[f'HR_distributions.{hr_class}'] > hr_threshold]

    # get the unique subjects
    risk_subjects = hr_risk_subjects_df['subject_id'].unique().tolist()

    # init list for holding the dates and counter for tracking risk instances
    risk_dates = []
    total_num_instances = 0

    if subject_id in risk_subjects:

        # get rows that belong to subject
        subject_data = hr_risk_subjects_df[hr_risk_subjects_df['subject_id'] == subject_id]

        # perform groupby by date to check the number of instances per day
        for acquisition_date, date_df in subject_data.groupby('date'):

            if len(date_df) >= NUM_INSTANCES_ELEVATED_HR:

                # get workload dict for the day
                day_workload_dict = oh_profile['daily_questionnaires']['workload'][acquisition_date]

                # calculate the mean of the workload questions
                workload_mean = get_mean_workload_score(day_workload_dict,
                                                         ['focus_and_mental_strain', 'rushed_and_under_pressure',
                                                          'heavy_workload'])

                if workload_mean >= MAX_THRESHOLD_WORKLOAD:
                    # update total number of instances
                    total_num_instances += 1

                    # add the date to the list
                    risk_dates.append(acquisition_date)

    if len(risk_dates) > 0:
        # transform dates to strings
        risk_dates = dates_to_weekdays(risk_dates, date_format="%d-%m-%Y", locale=language)

        # generate dict
        recommendations_dict[RISK_DATES_KEY] = risk_dates
        recommendations_dict[NUM_INSTANCES_KEY] = total_num_instances
        recommendations_dict[RECOMMENDATIONS_KEY] = \
            full_recommender_dict['sensors']['heart_rate']['recommendation'][language]

    else:

        # add that there are no recommendations needed
        recommendations_dict[RECOMMENDATIONS_KEY] = [NO_RECOMMENDATIONS[language]]

    return recommendations_dict


# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #