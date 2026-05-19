# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
from pathlib import Path
import pandas as pd
from typing import Dict, List

# internal imports
from .language_mappings import ROSA_MAPPING, ENVIRONMENT_MAPPING
from recommender.utils import load_or_generate_csv, get_language_mapper_values
from constants import VIABLE_PAIN_DIMENSIONS


# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
ROSA_CSV_FILENAME = 'rosa_subject_metrics.csv'
ENVIRONMENT_CSV_FILENAME = 'environment_subject_metrics.csv'


PAIN_CSV_FILE_SUFFIX = "pain_subject_metrics.csv"
WORKLOAD_CSV_FILENAME = 'workload_subject_metrics.csv'
# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def generate_rosa_csv(rosa_data_csv_path: str | Path, oh_profile_path: str, metadata_dict: Dict[str, str]=None) -> pd.DataFrame:
    """
    Load or generate the ROSA biomechanical subject-metrics CSV.

    If the CSV does not yet exist at the specified path, the OH profiles are parsed and the resulting DataFrame is
    generated and saved there. On subsequent calls the cached file is read directly, avoiding repeated profile parsing.

    :param rosa_data_csv_path: Directory in which the CSV is stored (or will be created).
    :param oh_profile_path: Path to folder containing the OH profile data of all subjects.
    :param metadata_dict: dictionary defining which metadata should be extracted and added to the DataFrame. Default: None
    :return: DataFrame containing per-subject ROSA metrics.
    """

    return load_or_generate_csv(csv_dir=rosa_data_csv_path, filename=ROSA_CSV_FILENAME,
                                oh_profile_path=oh_profile_path,
                                oh_metric_hierarchy="single_instance_questionnaires.biomechanical.ROSA",
                                level_names=[], value_paths=list(ROSA_MAPPING.keys()),
                                metadata_dict=metadata_dict)


def generate_environment_csv(environment_data_csv_path: str | Path, oh_profile_path: str, language: str='pt', metadata_dict: Dict[str, str]=None) -> pd.DataFrame:
    """
    Load or generate the environmental questionnaire subject-metrics CSV.

    If the CSV does not yet exist at the specified path, the OH profiles are parsed and the resulting DataFrame is
    generated and saved there. On subsequent calls the cached file is read directly, avoiding repeated profile parsing.

    :param environment_data_csv_path: Directory in which the CSV is stored (or will be created).
    :param oh_profile_path: Path to the OH profile data.
    :param language: the language in which the OH-profiles is written ('pt' or 'eng'). Default: 'pt'
    :param metadata_dict: dictionary defining which metadata should be extracted and added to the DataFrame. Default: None
    :return: DataFrame containing per-subject environmental questionnaire metrics.
    """

    # get the values to be extracted based on the language
    values_to_extract = get_language_mapper_values(ENVIRONMENT_MAPPING, language)

    return load_or_generate_csv(csv_dir=environment_data_csv_path, filename=ENVIRONMENT_CSV_FILENAME,
                                oh_profile_path=oh_profile_path,
                                oh_metric_hierarchy="single_instance_questionnaires.environmental",
                                level_names=[],
                                value_paths=values_to_extract,
                                metadata_dict=metadata_dict)

def generate_pain_csv(pain_data_csv_path: str| Path, oh_profile_path: str, pain_dimension: str,
                      metadata_dict: Dict[str, str]=None) -> pd.DataFrame:
    """
    Load or generate the pain questionnaire subject-metrics by the specified dimension.
    Possible dimensions are:
    ["localização", "tempo", "incapacidade", "sofrimento", "intensidade", "perceção"]

    If the CSV does not exist at the specified path, the OH profiles are parsed and the resulting DataFrame is genrated
    and saved there. On subsequent calls the cached file is read directly, avoiding repeated profile parsing.

    :param pain_data_csv_path: Directory in which the CSV is stored (or will be created).
    :param oh_profile_path:  Path to the OH profile data.
    :param pain_dimension: the pain dimension which should be loaded. Should be one of the following:
                           ["localização", "tempo", "incapacidade", "sofrimento", "intensidade", "perceção"]
    :param metadata_dict: dictionary defining which metadata should be extracted and added to the DataFrame. Default: None
    :return: DataFrame containing per-subject pain questionnaire metrics.
    """

    # check for input validity of pain_dimension
    if pain_dimension not in VIABLE_PAIN_DIMENSIONS:
        raise ValueError(f"The \'pain_dimension\' must be one of the following: {VIABLE_PAIN_DIMENSIONS}")

    # generate filename
    filename = f'{pain_dimension}_{PAIN_CSV_FILE_SUFFIX}'

    # TODO potentially implement language mapping

    # load the metrics
    df_metrics = load_or_generate_csv(csv_dir=pain_data_csv_path, filename=filename,
                                      oh_profile_path=oh_profile_path,
                                      oh_metric_hierarchy="single_instance_questionnaires.biomechanical",
                                      level_names=[],
                                      value_paths=[f'dor_{pain_dimension}.*'],
                                      metadata_dict=metadata_dict)

    # clean the column names
    df_metrics.columns = _clean_pain_cols(df_metrics.columns)

    # overwrite the stored DataFrame
    df_metrics.to_csv(Path(pain_data_csv_path)/filename,index=False)

    return df_metrics

def generate_workload_csv(workload_data_csv_path: str | Path, oh_profile_path: str, metadata_dict: Dict[str, str] = None) -> pd.DataFrame:
    """
    Load or generate the workload questionnaire subject-metrics CSV.

    If the CSV does not yet exist at the specified path, the OH profiles are parsed and the resulting DataFrame is
    generated and saved there. On subsequent calls the cached file is read directly, avoiding repeated profile parsing.
    :param workload_data_csv_path: Directory in which the CSV is stored (or will be created).
    :param oh_profile_path: Path to folder containing the OH profile data of all subjects.
    :param metadata_dict: dictionary defining which metadata should be extracted and added to the DataFrame. Default: None
    :return: DataFrame containing per-subject workload metrics.
    """

    return load_or_generate_csv(csv_dir=workload_data_csv_path, filename=WORKLOAD_CSV_FILENAME,
                                oh_profile_path=oh_profile_path,
                                oh_metric_hierarchy="daily_questionnaires.workload",
                                level_names=["date"],
                                value_paths=[".*"],
                                metadata_dict=metadata_dict)
# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #
def _clean_pain_cols(col_names: List[str]) -> List[str]:
    """
    cleans the pain column names by removing the path-reference from that is generated while extracting metrics from
    the OH-profile, e.g.: dor_tempo.cervical/pescoço --> cervical/pescoço
    :param col_names: list of column names.
    :return: pandas.DataFrame with cleaned column names
    """
    # list to hold the new column names
    new_col_names = []

    # cycle over the column
    for col in col_names:
        if col.startswith('dor'):

            # remove the part before the dot and replace underscores with empty spaces
            cleand_col = col.split('.')[-1]
            cleand_col = cleand_col.replace('_', ' ')

            # store the cleaned col
            new_col_names.append(cleand_col)




        else:
            new_col_names.append(col)


    return new_col_names