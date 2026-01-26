
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


# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #