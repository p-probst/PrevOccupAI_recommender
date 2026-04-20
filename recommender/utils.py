"""
Available Functions
-------------------
[Public]

-------------------
"""
# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import sys
from pathlib import Path
from babel.dates import format_date
from typing import List
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, Tuple

# internal imports
from constants import USER, RULE_KEY, RISK_DATES_KEY, NUM_INSTANCES_KEY, RECOMMENDATIONS_KEY, NO_RECOMMENDATIONS

# external imports
project_path = Path(f"C:/Users/{USER}/PycharmProjects/OH_Toolkit")
sys.path.append(str(project_path))
from oh_parser import load_profiles, extract_nested

# ------------------------------------------------------------------------------------------------------------------- #
# file constants
# ------------------------------------------------------------------------------------------------------------------- #
TIME_FMT = "%H:%M:%S.%f"


# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def load_or_generate_csv(csv_dir: str | Path, filename: str, oh_profile_path: str, oh_metric_hierarchy: str,
                          level_names: list, value_paths: list) -> pd.DataFrame:
    """
    Load a metrics CSV from disk if it exists, otherwise parse OH profiles to generate and save it.

    :param csv_dir: Directory where the CSV is stored (or will be written to).
    :param filename: Filename of the CSV file.
    :param oh_profile_path: Path to folder containing the OH profiles of all subjects.
    :param oh_metric_hierarchy: Dot-separated path into the OH profile hierarchy to the dimension (or sub-dimension)
                                that should be extracted.
    :param level_names: OH-profile level names. Correspond to levels within metrics, such as e.g., date, session, side,
                        etc. Applies only to metrics that are extracted daily.
                        Examples:
                        "date"
                        "session"
    :param value_paths: list of metrics or metric paths that should be extracted from the OH-profile hierarchy.
                        Examples:
                        "score_adapted_a" (ROSA metric)
                        "Noise_statistics.min" (specific noise metric)
                        "Noise_statistics.*"   (all noise metrics)
    :return: DataFrame with the requested metrics for all subjects.
    """
    # Build the full absolute path so that the existence check and the save target
    # are always the same location, regardless of the current working directory.
    csv_path = Path(csv_dir) / filename

    if not csv_path.exists():
        # Parse OH profiles — this is the expensive step that is avoided on repeat runs.
        profiles = load_profiles(oh_profile_path)

        # extract the requested metrics from the OH-profiles
        df = extract_nested(profiles, base_path=oh_metric_hierarchy, level_names=level_names, value_paths=value_paths,
                            exclude_patterns=[])

        # store the dataframe to csv file
        df.to_csv(csv_path, index=False)

    else:
        df = pd.read_csv(csv_path)

    return df


def get_language_mapper_values(mapper_dict: Dict, language: str) -> List[str]:
    """
    Returns all OH-profile keys from the mapper_dict, according to the defined language.
    :param mapper_dict: A dictionary containing the OH-profile keys for different languages.
    :param language: The language. Either 'pt' or 'eng'.
    :return: list containing the OH-profile keys.
    """

    return [sub_dict[language] for sub_dict in mapper_dict.values()]


def dates_to_weekdays(dates: List[str], date_format: str, locale: str = "en") -> List[str]:
    """
    Convert a list of date strings to localized weekday names.

    :param dates: List of date strings
    :param date_format: Format used to parse the input dates
    :param locale: Locale code (e.g. 'en', 'pt', 'pt_PT')
    :return: List of weekday names
    """
    return [
        format_date(
            datetime.strptime(d, date_format),
            format="EEEE",
            locale=locale
        )
        for d in dates
    ]


def evaluate_continuous_timeline_risk(oh_profile_sub_dict: Dict, oh_timeline_metric: str, class_labels: List[str], exposure_limit_minutes: float, instance_threshold: int) -> Tuple[List[str], int]:
    """
    Evaluates continuous risks regarding exposure over time (timeline metrics, e.g., noise timeline, human activity timeline)
    The function identifies continuous exposure of the defined class_labels within the oh_metric using the
    exposure_limit_minutes as threshold. Furthermore, the exposure is only considered as a risk if the number of
    instances of exposure (e.g., 1, 2, or more instances) surpasses the instance_threshold.

    This function is supposed to be executed on a subject-level, meaning that the oh_profile_sub_dict is a sub-dict that
    was extracted from a certain subject.

    :param oh_profile_sub_dict: the sub-dictionary containing the days and acquisition session of the metric that is
                                supposed to be evaluated.
    :param oh_timeline_metric: the timeline metric within the sub-dict that is supposed to be evaluated.
    :param class_labels: the label of the class which is supposed to be found within the oh_metric timeline.
    :param exposure_limit_minutes: time in minutes for the exposure to be considered as a exposure instance.
    :param instance_threshold: the threshold for how many exposure instances should be at least detected for it to be
                               considered as a risk.
    :return: Tuple containing the dates at which the risk of continuous exposure was detected as well as the total
             number of instances.
    """

    # init variables to hold the results
    risk_dates = []
    total_num_instances = 0

    # cycle over the acquisition dates and retrieve the metric dictionary for each acquisition session
    for acquisition_date, session_dict in oh_profile_sub_dict.items():

        # cycle over each session and retrieve the corresponding dictionary containing all metrics for that session
        for acquisition_time, metrics_dict in session_dict.items():

            # get the requested timeline metric
            timeline_dict = metrics_dict[oh_timeline_metric]

            # get the number of instances that surpass exposure time limit
            num_exposure_instances = _count_continuous_timeline_risk_breach(timeline_dict, class_labels, exposure_limit_minutes=exposure_limit_minutes)

            # check whether the number of instances surpasses the instance threshold
            if num_exposure_instances > instance_threshold:

                # update the risk dates list and the total number of instances
                risk_dates.append(acquisition_date)
                total_num_instances += num_exposure_instances

    return risk_dates, total_num_instances


def get_mean_workload_score(workload_answers_dict: Dict[str, int], workload_question_keys: List[str]) -> float:
    """
    Calculates the mean workload score for the defined workload question keys.
    :param workload_answers_dict: dictionary containing the workload questionnaire answers for a single day.
    :param workload_question_keys: the keys of the dictionary for which the mean should be calculated.
    :return: the mean workload score.
    """

    # check whether the workload_answers_dict is populated
    # there are instanced where a participant forgot to fill out the questionnaire on a day
    if not workload_answers_dict:

        return 0

    # init the score sum
    score_sum = 0

    # get the number of questions
    num_questions = len(workload_question_keys)

    # cycle over the workload question keys
    for question_key in workload_question_keys:

        # check whether the keys are in the dictionary
        if question_key in workload_answers_dict:

            score_sum += workload_answers_dict[question_key]

    return score_sum / num_questions


def build_sensor_recommendations_dict(rule: list, risk_dates: list, total_num_risk_instances: int, full_recommender_dict: Dict, sensor_dimension: str, language: str='pt'):
    """
    function to build the full recommendation dictionary. This function only works for recommendations with a single
    nested structure (i.e., noise, emg, heart rate, posture). The function does not work for double nested recommendations
    as it is the case with human activities.

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
    :param sensor_dimension: the sensor dimension used in the recommendations.json.
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
        recommendations_dict[RECOMMENDATIONS_KEY] = full_recommender_dict['sensors'][sensor_dimension]['recommendation'][language]

    else:

        # add that there are no recommendations needed
        recommendations_dict[RECOMMENDATIONS_KEY] = [NO_RECOMMENDATIONS[language]]

    return recommendations_dict

# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #
def _count_continuous_timeline_risk_breach(timeline_dict: Dict, class_labels: List[str], exposure_limit_minutes: float=60.0) -> int:
    """
    Counts the number of instances a continuous timeline risk has been breached (e.g., seated for too long,
    continuous noise exposure above a certain limit) using the exposure_limit_minutes as threshold.
    :param timeline_dict: dictionary containing the extracted timeline metric. The dictionary should be structured as
                          {time_interval: class_label}
                          where time_interval is formated as "%H:%M:%S.%f_%H:%M:%S.%f" indicating the start and end time
                          and class_label is a string (e.g., "Sentado", "Ruído Elevado", etc.). The class_label should
                          correspond to what is used in the OH-profile for that particular metric.
    :param class_labels: class label which is supposed to be evaluated within the timeline_dict.
    :param exposure_limit_minutes: the threshold for how long an exposure interval should be for it to be considered as
                                   a risk.
    :return: number of instances a continuous timeline risk has been breached
    """

    # init the counter
    num_risk_instances = 0

    # transform the exposure_limit_minutes to a timedelta
    exposure_limit_minutes = timedelta(minutes=exposure_limit_minutes)

    # cycle over the timeline_dict
    for time_range_str, class_label in timeline_dict.items():

        # check if the label falls into the labels that are being evaluated
        if class_label in class_labels:

            # split the time range string
            start_str, end_str = time_range_str.split('_')

            # parse times
            start_time = datetime.strptime(start_str, TIME_FMT)
            end_time = datetime.strptime(end_str, TIME_FMT)

            # calculate the duration of the exposure
            exposure_duration = end_time - start_time

            # check whether the duration exceeds the set limit
            if exposure_duration >= exposure_limit_minutes:

                # update the risk instances
                num_risk_instances += 1

    return num_risk_instances