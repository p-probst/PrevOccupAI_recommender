# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
from pathlib import Path
import pandas as pd

# internal imports
from .language_mappings import ROSA_MAPPING, ENVIRONMENT_MAPPING
from recommender.utils import load_or_generate_csv, get_language_mapper_values


# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
ROSA_CSV_FILENAME = 'rosa_subject_metrics.csv'
ENVIRONMENT_CSV_FILENAME = 'environment_subject_metrics.csv'

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def generate_rosa_csv(rosa_data_csv_path: str | Path, oh_profile_path: str) -> pd.DataFrame:
    """
    Load or generate the ROSA biomechanical subject-metrics CSV.

    If the CSV does not yet exist at the specified path, the OH profiles are parsed and the resulting DataFrame is
    generated and saved there. On subsequent calls the cached file is read directly, avoiding repeated profile parsing.

    :param rosa_data_csv_path: Directory in which the CSV is stored (or will be created).
    :param oh_profile_path: Path to folder containing the OH profile data of all subjects.
    :return: DataFrame containing per-subject ROSA metrics.
    """

    return load_or_generate_csv(csv_dir=rosa_data_csv_path, filename=ROSA_CSV_FILENAME,
                                oh_profile_path=oh_profile_path,
                                oh_metric_hierarchy="single_instance_questionnaires.biomechanical.ROSA",
                                level_names=[], value_paths=list(ROSA_MAPPING.keys()))


def generate_environment_csv(environment_data_csv_path: str | Path, oh_profile_path: str, language: str='pt') -> pd.DataFrame:
    """
    Load or generate the environmental questionnaire subject-metrics CSV.

    If the CSV does not yet exist at the specified path, the OH profiles are parsed and the resulting DataFrame is
    generated and saved there. On subsequent calls the cached file is read directly, avoiding repeated profile parsing.

    :param environment_data_csv_path: Directory in which the CSV is stored (or will be created).
    :param oh_profile_path: Path to the OH profile data.
    :param language: the language in which the OH-profiles is written ('pt' or 'eng'). Default: 'pt'
    :return: DataFrame containing per-subject environmental questionnaire metrics.
    """

    # get the values to be extracted based on the language
    values_to_extract = get_language_mapper_values(ENVIRONMENT_MAPPING, language)

    return load_or_generate_csv(csv_dir=environment_data_csv_path, filename=ENVIRONMENT_CSV_FILENAME,
                                oh_profile_path=oh_profile_path,
                                oh_metric_hierarchy="single_instance_questionnaires.environmental",
                                level_names=[],
                                value_paths=values_to_extract)