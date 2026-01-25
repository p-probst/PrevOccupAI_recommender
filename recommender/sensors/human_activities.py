# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import sys
from pathlib import Path
import pandas as pd


# external imports
project_path = Path("C:/Users/phill/PycharmProjects/OH_Toolkit")
sys.path.append(str(project_path))
from oh_parser import load_profiles, extract_nested


# internal imports
from constants import RISK_DATES_KEY, NUM_INSTANCES_KEY, RECOMMENDATIONS_KEY, RULE_KEY, NO_RECOMMENDATIONS
# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
HAR_CSV_FILENAME = "har_risk_subjects.csv"

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def generate_har_csv(noise_risk_csv_path: str | Path, oh_profile_path: str) -> pd.DataFrame:
    """

    :param noise_risk_csv_path:
    :param oh_profile_path:
    :return:
    """

    if not (Path(noise_risk_csv_path) / HAR_CSV_FILENAME).exists():
        # load the profiles
        profiles = load_profiles(oh_profile_path)

        # parse the noise metrics
        df_sessions = extract_nested(
            profiles,
            base_path="sensor_metrics.human_activities",
            level_names=["date", "session"],
            value_paths=[
                "HAR_distributions.Sentado",
                "HAR_distributions.De pé",
                "HAR_durations.Sentado_duration_sec",
                "HAR_steps.num_steps"

            ],
            exclude_patterns=[],
        )

        # save the DataFrame
        df_sessions.to_csv(HAR_CSV_FILENAME, index=False)

    else:
        df_sessions = pd.read_csv(HAR_CSV_FILENAME)

    return df_sessions
# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #