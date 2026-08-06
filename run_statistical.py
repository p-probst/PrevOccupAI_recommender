from pathlib import Path
import recommender as recommender
import statistical_analysis as stats

# set path to OH profiles
OH_PROFILES_PATH = "E:\\Backup PrevOccupAI_PLUS Data\\OH_profiles"

# set output path
STATISTICS_PATH = "E:\\Backup PrevOccupAI_PLUS Data\\statistical_analysis_ma"

# define working directory
cwd_ = Path.cwd()

# define metadata to be extracted and added to the CSV data
metadata_dict = {"work_type": "meta_data.work_type"}
USE_CML_SHIFTS = False

# ------------------------------------------------------------------------------------------------------------------- #
# QUESTIONNAIRES
# ------------------------------------------------------------------------------------------------------------------- #
stats.print_populations_statistics(OH_PROFILES_PATH, {"work_type": "meta_data.work_type",
                                                      "age":"meta_data.idade",
                                                      "weight":"meta_data.peso", "height":"meta_data.altura",
                                                      "dominant_hand": "meta_data.mao", "sex": "meta_data.sexo"})
# ------------------------------------------------------------------------------------------------------------------- #
# QUESTIONNAIRES
# ------------------------------------------------------------------------------------------------------------------- #
print("=" *60)
print("Questionnaires")
print("=" *60)
# ------------------------------------------------------------------------------------------------------------------- #
# pain questionnaire
# ------------------------------------------------------------------------------------------------------------------- #
print("\n----------- Pain -----------")
# load pain location data
pain_locations_df = recommender.load.generate_pain_csv( cwd_, OH_PROFILES_PATH, pain_dimension="localização", metadata_dict=metadata_dict)

# perform pain location statistical analysis
stats.perform_pain_location_analysis(pain_locations_df, save_path=STATISTICS_PATH)

# ------------------------------------------------------------------------------------------------------------------- #
# workload
# ------------------------------------------------------------------------------------------------------------------- #
print("\n----------- Workload -----------")
# load the workload data
workload_data_df = recommender.load.generate_workload_csv(cwd_, OH_PROFILES_PATH, metadata_dict=metadata_dict)

# perform workload composite analysis
workload_composite_df = stats.perform_workload_analysis(workload_data_df, save_path=STATISTICS_PATH, show=False)

# ------------------------------------------------------------------------------------------------------------------- #
# SENSOR DATA
# ------------------------------------------------------------------------------------------------------------------- #
print("=" *60)
print("----------- Sensor Data -----------")
print("=" *60)
# ------------------------------------------------------------------------------------------------------------------- #
# noise sensor
# ------------------------------------------------------------------------------------------------------------------- #
print("\n----------- Noise -----------")
# load noise data
noise_data_df = recommender.load.generate_noise_csv(cwd_, OH_PROFILES_PATH, language='pt', metadata_dict=metadata_dict)

# perform noise exposure statistical analysis
stats.perform_noise_exposure_analysis(noise_data_df, save_path=STATISTICS_PATH, cml_shifts=USE_CML_SHIFTS)

# ------------------------------------------------------------------------------------------------------------------- #
# HAR sensor
# ------------------------------------------------------------------------------------------------------------------- #
print("\n----------- HAR -----------")
# load HAR data
har_data_df = recommender.load.generate_har_csv(cwd_, OH_PROFILES_PATH, language='pt', metadata_dict=metadata_dict)

# perform step count statistical analysis
stats.perform_step_count_analysis(har_data_df, save_path=STATISTICS_PATH, cml_shifts=USE_CML_SHIFTS, show=False)

# perform har proportions statistical analysis
stats.perform_har_proportions_analysis(har_data_df, save_path=STATISTICS_PATH, cml_shifts=USE_CML_SHIFTS, show=False)


# ------------------------------------------------------------------------------------------------------------------- #
# Posture
# ------------------------------------------------------------------------------------------------------------------- #
print("\n----------- Posture -----------")
# load posture data
posture_data_df = recommender.load.generate_posture_csv(cwd_, OH_PROFILES_PATH, metadata_dict=metadata_dict)

# perform posture statistical analysis
stats.perform_posture_ellipse_analysis(posture_data_df, save_path=STATISTICS_PATH, cml_shifts=USE_CML_SHIFTS, show=False)


# ------------------------------------------------------------------------------------------------------------------- #
# Heart rate
# ------------------------------------------------------------------------------------------------------------------- #
print("\n----------- Heart Rate -----------")
hr_data_df = recommender.load.generate_hr_csv(cwd_, OH_PROFILES_PATH, metadata_dict=metadata_dict)

# extract shift information from a dataframe that contains phone sensor data
shift_df = stats.get_shifts_from_phone_df(posture_data_df, cml_shifts=USE_CML_SHIFTS)

# perform max BPM analysis
stats.perform_max_bpm_analysis(hr_data_df, shift_df, save_path=STATISTICS_PATH, show=False)

# ------------------------------------------------------------------------------------------------------------------- #
# EMG
# ------------------------------------------------------------------------------------------------------------------- #
print("\n----------- EMG -----------")
emg_data_df = recommender.load.generate_emg_apdf_csv(cwd_, OH_PROFILES_PATH, metadata_dict=metadata_dict)

# perform APDF EMG analysis
stats.perform_emg_apdf_analysis(emg_data_df, shift_df, save_path=STATISTICS_PATH, show=False)
stats.perform_emg_apdf_analysis(emg_data_df, shift_df, save_path=STATISTICS_PATH, show=False, nested=True)

# perform right EMG APDF with workload analysis
stats.perform_right_emg_workload_analysis(emg_data_df, workload_composite_df, save_path=STATISTICS_PATH, show=False)

stats.perform_workload_from_right_emg_analysis(emg_data_df, workload_composite_df, save_path=STATISTICS_PATH, show=False,
                                               aggregate_sessions=False)

