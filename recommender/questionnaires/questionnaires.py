# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import sys
from pathlib import Path
from typing import Dict, Iterable
import pandas as pd

# internal imports
from constants import RECOMMENDATIONS_KEY, RULE_KEY, NO_RECOMMENDATIONS, USER

# external imports
project_path = Path(f"C:/Users/{USER}/PycharmProjects/OH_Toolkit")
sys.path.append(str(project_path))
from oh_parser import load_profiles, extract_nested


# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
ROSA_CSV_FILENAME = 'rosa_subject_metrics.csv'
ENVIRONMENT_CSV_FILENAME = 'environment_subject_metrics.csv'

# Maps internal ROSA metric keys to human-readable dimension labels per language.
# Keys must match the value_paths extracted from the OH profile.
ROSA_MAPPING = {
    "score_a_adapted":       {"pt": "Cadeira",  "eng": "Chair"},
    "monitor_adapted_norm":  {"pt": "Monitor",  "eng": "Monitor"},
    "phone_adapted_norm":    {"pt": "Telefone", "eng": "Phone"},
    "mouse_adapted_norm":    {"pt": "Rato",     "eng": "Mouse"},
    "keyboard_adapted_norm": {"pt": "Teclado",  "eng": "Keyboard"},
}

# Maps internal environmental questionnaire keys to human-readable dimension labels per language.
# The Portuguese labels intentionally match the raw profile keys so that no translation is lost.
ENVIRONMENT_MAPPING = {
    "Nível de Iluminação":       {"pt": "Nível de Iluminação",       "eng": "Lighting Level"},
    "Ar":                        {"pt": "Ar",                        "eng": "Air"},
    "Ruído":                     {"pt": "Ruído",                     "eng": "Noise"},
    "Design do Escritório":      {"pt": "Design do Escritório",      "eng": "Office Design"},
    "Privacidade do Escritório": {"pt": "Privacidade do Escritório", "eng": "Office Privacy"},
    "Organização do Escritório": {"pt": "Organização do Escritório", "eng": "Office Organisation"}
}

# Subjects scoring at or above this normalised threshold (0–1 scale) are considered at medium risk.
MEDIUM_RISK_LEVEL = 1 / 3


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
    return _load_or_generate_csv(csv_dir=rosa_data_csv_path, filename=ROSA_CSV_FILENAME,
                                 oh_profile_path=oh_profile_path,
                                 oh_metric_hierarchy="single_instance_questionnaires.biomechanical.ROSA",
                                 level_names=[], value_paths=list(ROSA_MAPPING.keys()))


def generate_environment_csv(environment_data_csv_path: str | Path, oh_profile_path: str) -> pd.DataFrame:
    """
    Load or generate the environmental questionnaire subject-metrics CSV.

    If the CSV does not yet exist at the specified path, the OH profiles are parsed and the resulting DataFrame is
    generated and saved there. On subsequent calls the cached file is read directly, avoiding repeated profile parsing.

    :param environment_data_csv_path: Directory in which the CSV is stored (or will be created).
    :param oh_profile_path: Path to the OH profile data.
    :return: DataFrame containing per-subject environmental questionnaire metrics.

    """
    return _load_or_generate_csv(csv_dir=environment_data_csv_path, filename=ENVIRONMENT_CSV_FILENAME,
                                 oh_profile_path=oh_profile_path,
                                 oh_metric_hierarchy="single_instance_questionnaires.environmental",
                                 level_names=[],
                                 value_paths=list(ENVIRONMENT_MAPPING.keys()))


def get_rosa_recommendations(rosa_subject_metrics_df: pd.DataFrame, subject_id: int,
                             full_recommender_dict: Dict, language: str = 'pt') -> Dict:
    """
    gets the ROSA-based recommendations dictionary for a single subject.
    The function identifies which ROSA risk dimensions (chair, monitor, phone, mouse, keyboard) the subject falls into
    and returns recommendations for each.

    :param rosa_subject_metrics_df: pd.DataFrame containing the subject metrics.
    :param subject_id: Identifier of the subject to evaluate.
    :param full_recommender_dict: The full recommendations JSON loaded as a dict.
    :param language: Output language code ('pt' or 'eng'). Default: 'pt'
    :return: Dict containing the recommendations for the dimensions for which a risk was detected and the corresponding rule.
             The dictionary contains two keys:
             RECOMMENDATIONS_KEY = 'recommendations'
             RULE_KEY = 'rule'

             Depending on whether risks are detected or not, the RECOMMENDATIONS_KEY contains either a sub-dictionary,
             indicating the recommendations for each detected risk dimension, or just a list containing the message
             that no risks were detected.
             Example outputs (Portuguese example):
             (1) risks detected:
             {'recommendations': {'monitor': ['Ajustar o monitor...', '...'],
                                  'rato': ['Posicionar o rato...', '...']},
              'rule': ['Se a cor for **amarela ou vermelha** para essa dimensão do questionário.']}

              (2) no risks detected:
             {'recommendations': ['Boas notícias: Não se detetaram situações de risco.'],
              'rule': ['Se a cor for **amarela ou vermelha** para essa dimensão do questionário.']}
    """

    # obtain ROSA sub-dictionary
    rosa_dict = full_recommender_dict['questionnaires']['biomechanical']['ROSA']

    # obtain the risk rule
    # NOTE: for the questionnaires the risk rule is always the same, thus simply the rule of the first dimension is
    # extracted.
    rule = rosa_dict[list(ROSA_MAPPING.keys())[0]][RULE_KEY][language]

    # evaluate the occupational risks for the subject
    detected_risks_dict = _evaluate_questionnaire_risks(df=rosa_subject_metrics_df, subject_id=subject_id,
                                                        risk_metrics=ROSA_MAPPING.keys(), recommender_sub_dict=rosa_dict,
                                                        language=language, risk_metric_mapping=ROSA_MAPPING)

    # generate recommendations according to the found risks
    recommendations_dict = _build_recommendations_dict(rule, detected_risks_dict, language)

    return recommendations_dict


def get_environment_recommendations(environmental_subject_metrics_df: pd.DataFrame, subject_id: int,
                                    full_recommender_dict: Dict, language: str = 'pt') -> Dict:
    """
    gets the environmental-questionnaire recommendations dictionary for a single subject.

    The function identifies which environmental risk dimensions (lighting, air, noise, office design, office privacy,
    office organisation) the subject falls into and returns recommendations for each.

    :param environmental_subject_metrics_df: pd.DataFrame containing the subject metrics.
    :param subject_id: Identifier of the subject to evaluate.
    :param full_recommender_dict: The full recommendations JSON loaded as a dict.
    :param language: Output language code ('pt' or 'eng'). Default: 'pt'
    :return: Dict containing the recommendations for the dimensions for which a risk was detected and the corresponding rule.
             The dictionary contains two keys:
             RECOMMENDATIONS_KEY = 'recommendations'
             RULE_KEY = 'rule'

             Depending on whether risks are detected or not, the RECOMMENDATIONS_KEY contains either a sub-dictionary,
             indicating the recommendations for each detected risk dimension, or just a list containing the message
             that no risks were detected.
             Example outputs (Portuguese example):
             (1) risks detected:
             {'recommendations': {'Ruído': ['A exposição durante longos períodos de tempo a ruído...'],
                                  'Nível de Iluminação': ['Ajustar persiana por...', '...']},
              'rule': ['Se a cor for **amarela ou vermelha** para essa dimensão do questionário.']}

              (2) no risks detected:
             {'recommendations': ['Boas notícias: Não se detetaram situações de risco.'],
              'rule': ['Se a cor for **amarela ou vermelha** para essa dimensão do questionário.']}

    """
    # Navigate to the environmental sub-dictionary once to avoid repeated key traversal.
    env_dict = full_recommender_dict['questionnaires']['environmental']

    # obtain the risk rule
    # NOTE: for the questionnaires the risk rule is always the same, thus simply the rule of the first dimension is
    # extracted.
    rule = env_dict[list(ENVIRONMENT_MAPPING.keys())[0]][RULE_KEY][language]

    # evaluate the occupational risks for the subject
    detected_risks_dict = _evaluate_questionnaire_risks(df=environmental_subject_metrics_df, subject_id=subject_id,
                                                        risk_metrics=ENVIRONMENT_MAPPING.keys(), recommender_sub_dict=env_dict,
                                                        language=language, risk_metric_mapping=ENVIRONMENT_MAPPING)

    # generate recommendations according to the found risks
    recommendations_dict = _build_recommendations_dict(rule, detected_risks_dict, language)

    return recommendations_dict


# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #

def _load_or_generate_csv(csv_dir: str | Path, filename: str, oh_profile_path: str, oh_metric_hierarchy: str,
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


def _evaluate_questionnaire_risks(df: pd.DataFrame, subject_id: int, risk_metrics: Iterable[str], recommender_sub_dict: Dict,
                                  language: str, risk_metric_mapping: Dict | None = None) -> Dict:
    """
    Evaluates the occupational health risks for the questionnaire data contained in df according to the set risk
    thresholds and fetches the corresponding recommendations if risks were detected.

    For each metric in risk_metrics the function filters the DataFrame to subjects whose score meets or exceeds the set
    threshold.  After this the DataFrame is filtered for the subject_id. If the subject surpasses the threshold for any
    risk_metric, the corresponding recommendation is fetched from the recommender_sub dict.

    :param df: pd.DataFrame containing the data of all subjects to be evaluated.
    :param subject_id: Identifier of the subject to evaluate.
    :param risk_metrics: list containing the names of the risk metrics to be evaluated. These should be the same as the
                         column names in df.
    :param recommender_sub_dict: The sub-dictionary containing the recommendation corresponding to the metrics to be
                                 evaluated. This sub-dictionary is obtained by reading in recommendations.json and calling
                                 the corresponding dimension.

    :param language: Output language ('pt' or 'eng'). Default: 'pt'.
    :param risk_metric_mapping: dictionary containing mappings of the risk_metrics to human-readable text in either
                                Portuguese ('pt') or English ('eng'). Optional: if not passed the risk_metric string
                                itself is used.
    :return: dictionary containing the recommendations (as list of strings) for each identified occupational risk dimension.
             If there were no risks detected, the dictionary is empty.
             The format of the dictionary is:
             {risk_dimension_label: recommendations_list}
    """
    risk_recommendations = {}

    for risk_metric in risk_metrics:
        # Filter to subjects whose normalised score is at or above the medium-risk threshold.
        at_risk_df = df[df[risk_metric] >= MEDIUM_RISK_LEVEL]

        if subject_id in at_risk_df['subject_id'].tolist():
            # Translate the metric key to a human-readable label in the requested language.
            # If no mapping is provided, fall back to the raw risk_metric string.
            oh_risk_dimension_label = risk_metric_mapping[risk_metric][language] if risk_metric_mapping else risk_metric

            # store the risk dimension label together with the corresponding recommendation in to the dict
            risk_recommendations[oh_risk_dimension_label] = recommender_sub_dict[risk_metric]['recommendation'][language]

    return risk_recommendations


def _build_recommendations_dict(rule: str | list, risk_recommendations: list | dict, language: str) -> Dict:
    """
    function to build the full recommendation dictionary. The recommendation dictionary consists of the recommendations
    and the rule that was applied to obtain the recommendations.
    The recommendations are either:
    (1) a sub-dictionary: contains for each questionnaire dimension (for which a risk was detected) the corresponding recommendation.
    (2) a list: contains the list of recommendations for the sensor-related metrics (only for metrics for which a risk was detected).
    (3) a list: contains a single string indicating that no risks were detected (in case no risks were detected).

    :param rule: the rules as extracted from recommendations.json. The data type changes based on whether the
                 recommendations are questionnaire- or sensor-based.
                 (1) Questionnaire-based: dictionary with recommendations for each questionnaire dimension. The key is
                                          the dimension, while the recommendation is the value (type: str)
                 (2) Sensor-based: List with one more rules
    :param risk_recommendations: Output of
    :type risk_recommendations: recommendations for the identified risks
    :param language: Output language ('pt' or 'eng'). Default: 'pt' (used to obtain language specific message if there
                     are no recommendations to give.
    :return: dict containing the recommendations and the corresponding rule that was applied to identify risks
    """
    recommendations_dict = {RULE_KEY: rule}

    if risk_recommendations:
        recommendations_dict[RECOMMENDATIONS_KEY] = risk_recommendations
    else:
        # Subject is not at risk in any dimension — return the standard no-risk message.
        recommendations_dict[RECOMMENDATIONS_KEY] = [NO_RECOMMENDATIONS[language]]

    return recommendations_dict
