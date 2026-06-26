# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import pandas as pd
from pathlib import Path
from typing import Dict

# internal imports
from .language_mappings import NOISE_MAPPING, EMG_MAPPING, POSTURE_MAPPING, HAR_MAPPING, HEART_RATE_MAPPING
from recommender.utils import load_or_generate_csv, get_language_mapper_values
from constants import SESSION_NUM_COL, SESSION_TIME_COL, DATE_COL

# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
ENVIRONMENT_SENSORS_FILENAME = "environment_sensors_subject_metrics.csv"
NOISE_CSV_FILENAME = "noise_subject_metrics.csv"
HAR_CSV_FILENAME = "har_subject_metrics.csv"
POSTURE_CSV_FILENAME = "posture_subject_metrics.csv"
EMG_CSV_FILENAME = 'emg_subject_metrics.csv'
EMG_APDF_CSV_FILENAME = 'emg_apdf_subject_metrics.csv'
HR_CSV_FILENAME = "hr_subject_metrics.csv"
WRIST_CSV_FILENAME = "wrist_subject_metrics.csv"

LOUD_NOISE_SUM = 'sum_loud_noise'


# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def generate_environment_sensors_csv(environment_sensors_csv_path: str | Path, oh_profile_path: str | Path, language: str='pt', metadata_dict: Dict[str, str]=None) -> pd.DataFrame:
    """
    Load or generate the environment sensors subject_metrics CSV. This is generated based on the OH profiles of the entire
    worker population.

    If the CSV does not yet exist at the specified path, the OH profiles are parsed and the resulting DataFrame is saved.
    On subsequent calls the cached file is read directly, avoiding repeated profile parsing.
    :param environment_sensors_csv_path: Directory in which the CSV is stored (or will be created)
    :param oh_profile_path: Path to folder containing the OH profile data of all subjects.
    :param language: the language in which the OH-profiles is written ('pt' or 'eng'). Default: 'pt'
    :param metadata_dict: dictionary defining which metadata should be extracted and added to the DataFrame. Default: None
    :return: DataFrame containing per-subject noise metrics.
    """

    return load_or_generate_csv(csv_dir=environment_sensors_csv_path, filename=ENVIRONMENT_SENSORS_FILENAME,
                                oh_profile_path=oh_profile_path,
                                oh_metric_hierarchy="sensor_metrics.environment",
                                level_names=[],
                                value_paths=[".*"],
                                metadata_dict=metadata_dict)


def generate_noise_csv(noise_risk_csv_path: str | Path, oh_profile_path: str, language: str='pt', metadata_dict: Dict[str, str]=None) -> pd.DataFrame:
    """
    Load or generate the noise subject-metrics CSV. This is generated based on the OH profiles of the entire
    worker population. During the generation process and additional column is created, which contains the sum of time
    of exposure to disrupting and high noise

    If the CSV does not yet exist at the specified path, the OH profiles are parsed and the resulting DataFrame is saved.
    On subsequent calls the cached file is read directly, avoiding repeated profile parsing.

    :param noise_risk_csv_path: Directory in which the CSV is stored (or will be created)
    :param oh_profile_path: Path to folder containing the OH profile data of all subjects.
    :param language: the language in which the OH-profiles is written ('pt' or 'eng'). Default: 'pt'
    :param metadata_dict: dictionary defining which metadata should be extracted and added to the DataFrame. Default: None
    :return: DataFrame containing per-subject noise metrics.
    """

    # get the values to be extracted (only the first two values needed here)
    values_to_extract = get_language_mapper_values(NOISE_MAPPING, language)[0:-1]

    # load or generate the DataFrame
    df_noise_metrics = load_or_generate_csv(csv_dir=noise_risk_csv_path, filename=NOISE_CSV_FILENAME,
                                            oh_profile_path=oh_profile_path,
                                            oh_metric_hierarchy="sensor_metrics.noise",
                                            level_names=[DATE_COL, SESSION_TIME_COL],
                                            value_paths=['Noise_distributions.*',
                                                         'Noise_durations.*'],
                                            metadata_dict=metadata_dict)

    # check whether the LOUD_NOISE_SUM column exists (this is only needed if the metrics are generated for the first time
    if not LOUD_NOISE_SUM in df_noise_metrics.columns:

        # add up disrupting and high noise
        df_noise_metrics[LOUD_NOISE_SUM] = (df_noise_metrics[f'Noise_distributions.{values_to_extract[0]}']
                                            + df_noise_metrics[f'Noise_distributions.{values_to_extract[1]}'])

        # save the updated DataFrame
        df_noise_metrics.to_csv(Path(noise_risk_csv_path) / NOISE_CSV_FILENAME, index=False)


    return df_noise_metrics


def generate_har_csv(har_data_csv_path: str | Path, oh_profile_path: str, language: str='pt', metadata_dict: Dict[str, str]=None) -> pd.DataFrame:
    """
    Load or generate the har subject-metrics CSV. This is generated based on the OH profiles of the entire
    worker population.

    If the CSV does not yet exist at the specified path, the OH profiles are parsed and the resulting DataFrame is saved.
    On subsequent calls the cached file is read directly, avoiding repeated profile parsing.

    :param har_data_csv_path: Directory in which the CSV is stored (or will be created)
    :param oh_profile_path: Path to folder containing the OH profile data of all subjects.
    :param language: the language in which the OH-profiles is written ('pt' or 'eng'). Default: 'pt'
    :param metadata_dict: dictionary defining which metadata should be extracted and added to the DataFrame. Default: None
    :return: DataFrame containing per-subject har metrics.
    """

    # get the values to be extracted
    values_to_extract = get_language_mapper_values(HAR_MAPPING, language)

    df_har_metrics = load_or_generate_csv(csv_dir=har_data_csv_path, filename=HAR_CSV_FILENAME,
                                          oh_profile_path=oh_profile_path,
                                          oh_metric_hierarchy="sensor_metrics.human_activities",
                                          level_names=[DATE_COL, SESSION_TIME_COL],
                                          value_paths=[f"HAR_distributions.{values_to_extract[0]}",
                                                       f"HAR_distributions.{values_to_extract[1]}",
                                                       f"HAR_distributions.{values_to_extract[4]}",
                                                       f"HAR_durations.{values_to_extract[2]}",
                                                       f"HAR_steps.{values_to_extract[3]}"],
                                          metadata_dict=metadata_dict)

    return df_har_metrics


def generate_posture_csv(posture_data_csv_path: str | Path, oh_profile_path: str, language: str='pt', metadata_dict: Dict[str, str]=None) -> pd.DataFrame:
    """
    Load or generate the posture subject-metrics CSV. This is generated based on the OH-profiles of the entire worker
    population.

    If the CSV does not yet exist at the specified path, the OH profiles are parsed and the resulting DataFrame is saved.
    On subsequent calls the cached file is read directly, avoiding repeated profile parsing.
    :param posture_data_csv_path: Directory in which the CSV is stored (or will be created)
    :param oh_profile_path: Path to folder containing the OH profile data of all subjects.
    :param language: the language in which the OH-profiles is written ('pt' or 'eng'). Default: 'pt'
    :param metadata_dict: dictionary defining which metadata should be extracted and added to the DataFrame. Default: None
    :return: DataFrame containing per-subject posture metrics.
    """

    # get the values to be extracted
    values_to_extract = get_language_mapper_values(POSTURE_MAPPING, language)

    # extract the metrics
    df_posture_metrics = load_or_generate_csv(csv_dir=posture_data_csv_path, filename=POSTURE_CSV_FILENAME,
                                              oh_profile_path=oh_profile_path,
                                              oh_metric_hierarchy="sensor_metrics.posture",
                                              level_names=[DATE_COL, SESSION_TIME_COL],
                                              value_paths=values_to_extract,
                                              metadata_dict=metadata_dict)

    return df_posture_metrics


def generate_emg_csv(emg_data_csv_path: str | Path, oh_profile_path: str, language: str='pt', metadata_dict: Dict[str, str]=None) -> pd.DataFrame:
    """
    Load or generate the EMG subject-metrics CSV. This is generated based on the OH-profiles of the entire worker
    population. The metrics are extracted for the left and the right positioning of the muscleBAN

    If the CSV does not yet exist at the specified path, the OH profiles are parsed and the resulting DataFrame is saved.
    On subsequent calls the cached file is read directly, avoiding repeated profile parsing.
    :param emg_data_csv_path: Directory in which the CSV is stored (or will be created)
    :param oh_profile_path: Path to folder containing the OH profile data of all subjects.
    :param language: the language in which the OH-profiles is written ('pt' or 'eng'). Default: 'pt'
    :param metadata_dict: dictionary defining which metadata should be extracted and added to the DataFrame. Default: None
    :return: pandas.DataFrame containing per-subject EMG metrics.
    """

    # get the values to be extracted
    values_to_extract = get_language_mapper_values(EMG_MAPPING, language)

    # extract the metric
    df_emg_metrics = load_or_generate_csv(csv_dir=emg_data_csv_path, filename=EMG_CSV_FILENAME,
                                          oh_profile_path=oh_profile_path,
                                          oh_metric_hierarchy="sensor_metrics.emg",
                                          level_names=[DATE_COL, SESSION_TIME_COL],
                                          value_paths=[f"left.EMG_relative_bins.{values_to_extract[0]}",
                                                       f"right.EMG_relative_bins.{values_to_extract[0]}",
                                                       f"left.EMG_relative_bins.{values_to_extract[1]}",
                                                       f"right.EMG_relative_bins.{values_to_extract[1]}",
                                                       f"left.EMG_relative_bins.{values_to_extract[2]}",
                                                       f"right.EMG_relative_bins.{values_to_extract[2]}",
                                                       f"left.EMG_relative_bins.{values_to_extract[3]}",
                                                       f"right.EMG_relative_bins.{values_to_extract[3]}",
                                                       f"left.{SESSION_NUM_COL}",
                                                       f"right.{SESSION_NUM_COL}"],
                                          exclude_patterns=["EMG_daily_metrics", "EMG_weekly_metrics"],
                                          metadata_dict=metadata_dict)

    return df_emg_metrics

def generate_emg_apdf_csv(emg_data_csv_path: str | Path, oh_profile_path: str, language: str='pt', metadata_dict: Dict[str, str]=None) -> pd.DataFrame:
    """
    Load or generate the EMG subject-metrics CSV. This is generated based on the OH-profiles of the entire worker
    population. The metrics are extracted for the left and the right positioning of the muscleBAN

    If the CSV does not yet exist at the specified path, the OH profiles are parsed and the resulting DataFrame is saved.
    On subsequent calls the cached file is read directly, avoiding repeated profile parsing.
    :param emg_data_csv_path: Directory in which the CSV is stored (or will be created)
    :param oh_profile_path: Path to folder containing the OH profile data of all subjects.
    :param language: the language in which the OH-profiles is written ('pt' or 'eng'). Default: 'pt'
    :param metadata_dict: dictionary defining which metadata should be extracted and added to the DataFrame. Default: None
    :return: pandas.DataFrame containing per-subject EMG metrics.
    """

    # extract the metric
    df_emg_metrics = load_or_generate_csv(csv_dir=emg_data_csv_path, filename=EMG_APDF_CSV_FILENAME,
                                          oh_profile_path=oh_profile_path,
                                          oh_metric_hierarchy="sensor_metrics.emg",
                                          level_names=[DATE_COL, SESSION_TIME_COL],
                                          value_paths=[f"left.EMG_apdf.active.p10",
                                                       f"right.EMG_apdf.active.p10",
                                                       f"left.EMG_apdf.active.p50",
                                                       f"right.EMG_apdf.active.p50",
                                                       f"left.EMG_apdf.active.p90",
                                                       f"right.EMG_apdf.active.p90",
                                                       f"left.{SESSION_NUM_COL}",
                                                       f"right.{SESSION_NUM_COL}"],
                                          exclude_patterns=["EMG_daily_metrics", "EMG_weekly_metrics"],
                                          metadata_dict=metadata_dict)

    return df_emg_metrics

def generate_hr_csv(hr_data_csv_path: str | Path, oh_profile_path: str, language: str='pt', metadata_dict: Dict[str, str]=None) -> pd.DataFrame:
    """
    Load or generate the heart rate subject-metrics CSV. This is generated based on the OH-profiles of the entire
    worker population.
    :param hr_data_csv_path: Directory in which the CSV is stored (or will be created)
    :param oh_profile_path: Path to folder containing the OH profile data of all subjects.
    :param language: the language in which the OH-profiles is written ('pt' or 'eng'). Default: 'pt'
    :param metadata_dict: dictionary defining which metadata should be extracted and added to the DataFrame. Default: None
    :return: pandas.DataFrame containing per-subject heart rate metrics
    """

    # get the values to be extracted
    values_to_extract = get_language_mapper_values(HEART_RATE_MAPPING, language)

    # load or generate the DataFrame
    df_hr_metrics = load_or_generate_csv(csv_dir=hr_data_csv_path, filename=HR_CSV_FILENAME,
                                         oh_profile_path=oh_profile_path,
                                         oh_metric_hierarchy="sensor_metrics.heart_rate",
                                         level_names=[DATE_COL, SESSION_TIME_COL],
                                         value_paths=[f"HR_BPM_stats.{values_to_extract[0]}",
                                                      f"HR_BPM_stats.{values_to_extract[4]}",
                                                      f"HR_distributions.{values_to_extract[1]}",
                                                      f"HR_distributions.{values_to_extract[2]}",
                                                      f"HR_distributions.{values_to_extract[3]}",
                                                      SESSION_NUM_COL],
                                         metadata_dict=metadata_dict)

    return df_hr_metrics

def generate_wrist_csv(wrist_data_csv_path: str | Path, oh_profile_path: str, language: str='pt', metadata_dict: Dict[str, str]=None) -> pd.DataFrame:
    """
    Load or
    :param wrist_data_csv_path:
    :param oh_profile_path:
    :param language:
    :param metadata_dict:
    :return:
    """

    return load_or_generate_csv(csv_dir=wrist_data_csv_path, filename=WRIST_CSV_FILENAME,
                                oh_profile_path=oh_profile_path,
                                oh_metric_hierarchy="sensor_metrics.wrist_activities",
                                level_names=[DATE_COL, SESSION_TIME_COL],
                                value_paths=[".*"],
                                metadata_dict=metadata_dict)

