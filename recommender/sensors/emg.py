# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import sys
from pathlib import Path
import pandas as pd
from typing import Dict

# internal imports
from constants import RISK_DATES_KEY, NUM_INSTANCES_KEY, RECOMMENDATIONS_KEY, RULE_KEY, NO_RECOMMENDATIONS, USER
from recommender.utils import dates_to_weekdays, get_mean_workload_score

# external imports
project_path = Path(f"C:/{USER}/phill/PycharmProjects/OH_Toolkit")
sys.path.append(str(project_path))
from oh_parser import load_profiles, extract_nested


# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
EMG_CSV_FILENAME = 'emg_subject_metrics.csv'

EMG_MAX_THRESHOLD = 30.0 # 30 percent
NUM_INSTANCES_HIGH_EMG = 2
MAX_THRESHOLD_WORKLOAD = 3


# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def generate_emg_csv(har_data_csv_path: str | Path, oh_profile_path: str) -> pd.DataFrame:
    """

    :param har_data_csv_path:
    :param oh_profile_path:
    :return:
    """

    if not (Path(har_data_csv_path) / EMG_CSV_FILENAME).exists():
        # load the profiles
        profiles = load_profiles(oh_profile_path)

        # parse the noise metrics
        df_sessions = extract_nested(
            profiles,
            base_path="sensor_metrics.emg",
            level_names=["date", "session"],
            value_paths=[
                "left.EMG_relative_bins.high_for_you_pct",
                "right.EMG_relative_bins.high_for_you_pct",
            ],
            exclude_patterns=['EMG_daily_metrics', 'EMG_weekly_metrics'],
        )

        # save the DataFrame
        df_sessions.to_csv(EMG_CSV_FILENAME, index=False)

    else:
        df_sessions = pd.read_csv(EMG_CSV_FILENAME)

    return df_sessions


def get_emg_recommendations(emg_subject_metrics_df: pd.DataFrame, oh_profile: Dict, subject_id: int,
                            full_recommender_dict: Dict, language: str = 'pt') -> Dict:
    """

    :param emg_subject_metrics_df:
    :param oh_profile:
    :param subject_id:
    :param hr_class:
    :param full_recommender_dict:
    :param language:
    :return:
    """

    # init the recommendations dict with the rule
    recommendations_dict = {RULE_KEY: full_recommender_dict['sensors']['emg']['rule'][language]}

    # init list for holding the dates and counter for tracking risk instances
    risk_dates = set()
    total_num_instances = 0

    # cycle over left and right
    for emg_side in ['left', 'right']:

        # filter the DataFrame according to the rule
        hr_risk_subjects_df = emg_subject_metrics_df[emg_subject_metrics_df[f'{emg_side}.EMG_relative_bins.high_for_you_pct'] > EMG_MAX_THRESHOLD]

        # get the unique subjects
        risk_subjects = hr_risk_subjects_df['subject_id'].unique().tolist()

        if subject_id in risk_subjects:

            # get rows that belong to subject
            subject_data = hr_risk_subjects_df[hr_risk_subjects_df['subject_id'] == subject_id]

            # perform groupby by the date to check the number of instances per day
            for acquisition_date, date_df in subject_data.groupby('date'):

                # check if there are at least two instances
                if len(date_df) >= NUM_INSTANCES_HIGH_EMG:

                    # get workload dict for the day
                    day_workload_dict = oh_profile['daily_questionnaires']['workload'][acquisition_date]

                    # calculate the mean of the workload questions
                    workload_mean = get_mean_workload_score(day_workload_dict,
                                                            ['focus_and_mental_strain', 'rushed_and_under_pressure',
                                                             'heavy_workload'])

                    if workload_mean >= MAX_THRESHOLD_WORKLOAD:

                        # update total number of instances
                        total_num_instances += 1

                        # date to the set
                        risk_dates.add(acquisition_date)

    # check if there were any risk instances found
    if len(risk_dates) > 0:

        # transform dates to strings
        risk_dates = dates_to_weekdays(sorted(list(risk_dates)), date_format="%d-%m-%Y", locale=language)

        # generate dict
        recommendations_dict[RISK_DATES_KEY] = risk_dates
        recommendations_dict[NUM_INSTANCES_KEY] = total_num_instances
        recommendations_dict[RECOMMENDATIONS_KEY] = \
        full_recommender_dict['sensors']['emg']['recommendation'][language]

    else:

        # add that there are no recommendations needed
        recommendations_dict[RECOMMENDATIONS_KEY] = [NO_RECOMMENDATIONS[language]]

    return recommendations_dict





# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #