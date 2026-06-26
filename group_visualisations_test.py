# file for testing group visualisations
from pathlib import Path

import recommender as recommender
from recommender.load.questionnaires import VIABLE_PAIN_DIMENSIONS
import visualize as vis
from visualize.group.questionnaires.pain import PAIN_LEVELS, DURATION_LEVELS

# set path to OH profiles
OH_PROFILES_PATH = "E:\\Backup PrevOccupAI_PLUS Data\\OH_profiles"

# define working directory
cwd_ = Path.cwd()

# path to store plots
PLOT_PATH = "E:\\Backup PrevOccupAI_PLUS Data\\group_report\\plots"


# ------- get CSV data --------- #
# define metadata to be extracted and added to the CSV data
metadata_dict = {"work_type": "meta_data.work_type",
                 "age": "meta_data.idade"}

# ------------------------------------------------------------------------------------------------------------------- #
# pain questionnaire
# ------------------------------------------------------------------------------------------------------------------- #


# ------------------------------------------------------------------------------------------------------------------- #
# pain questionnaire
# ------------------------------------------------------------------------------------------------------------------- #
# list to hold pain dataFrames
pain_metrics_dict = {}

# generate/load pain data
for pain_dimension in VIABLE_PAIN_DIMENSIONS:

    pain_metrics_dict[pain_dimension] = recommender.load.generate_pain_csv(cwd_, OH_PROFILES_PATH, pain_dimension=pain_dimension, metadata_dict=metadata_dict)

# generate pain local plot
for pain_dimension in [VIABLE_PAIN_DIMENSIONS[idx] for idx in [0, -1]]:


    vis.group.plot_pain_localization_perception_by_work_type(pain_metrics_dict[pain_dimension], q_type=pain_dimension, save_path=PLOT_PATH, show=False)

# generate plots for incapacidade, sofrimento, and intensidade
for pain_dimension in VIABLE_PAIN_DIMENSIONS[2:5]:

    vis.group.plot_pain_levels_by_work_type(pain_metrics_dict[pain_dimension], q_type=pain_dimension, eval_levels=PAIN_LEVELS,  save_path=PLOT_PATH, show=False)

# generate plot for tempo
vis.group.plot_pain_levels_by_work_type(pain_metrics_dict['tempo'], q_type='tempo', eval_levels=DURATION_LEVELS,  save_path=PLOT_PATH, show=False)

# ------------------------------------------------------------------------------------------------------------------- #
# QUESTIONNAIRES
# ------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------- #
# ROSA
# ------------------------------------------------------------------------------------------------------------------- #
# generate/load rosa data
rosa_subjects_data_df = recommender.load.generate_rosa_csv(cwd_, OH_PROFILES_PATH, metadata_dict=metadata_dict)

# generate group mean plots
vis.group.plot_rosa_environment(rosa_subjects_data_df, q_type='rosa', is_rosa=True, save_path=PLOT_PATH)

# ------------------------------------------------------------------------------------------------------------------- #
# ENVIRONMENT
# ------------------------------------------------------------------------------------------------------------------- #
# generate/load environment data
environment_data_df = recommender.load.generate_environment_csv(cwd_, OH_PROFILES_PATH, metadata_dict=metadata_dict)
# generate group mean plots
vis.group.plot_rosa_environment(environment_data_df, q_type='environment', is_rosa=False, save_path=PLOT_PATH)

# ------------------------------------------------------------------------------------------------------------------- #
# WORKLOAD
# ------------------------------------------------------------------------------------------------------------------- #
workload_data_df = recommender.load.generate_workload_csv(cwd_, OH_PROFILES_PATH, metadata_dict=metadata_dict)
# generate group mean plots
vis.group.plot_workload_by_worktype(workload_data_df, save_path=PLOT_PATH)

# ------------------------------------------------------------------------------------------------------------------- #
# SENSORS
# ------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------- #
# ENVIRONMENT (CML)
# ------------------------------------------------------------------------------------------------------------------- #
environment_sensors_data_df = recommender.load.generate_environment_sensors_csv(cwd_, OH_PROFILES_PATH, metadata_dict=metadata_dict)
vis.group.plot_environment_sensors_by_worktype(environment_sensors_data_df, save_path=PLOT_PATH)

# ------------------------------------------------------------------------------------------------------------------- #
# NOISE
# ------------------------------------------------------------------------------------------------------------------- #
# load noise risk subjects
noise_data_df = recommender.load.generate_noise_csv(cwd_, OH_PROFILES_PATH, language='pt', metadata_dict=metadata_dict)
vis.group.plot_noise_distribution_by_worktype(noise_data_df, save_path=PLOT_PATH, show=False)
vis.group.plot_elevated_noise_duration_by_worktype(noise_data_df, save_path=PLOT_PATH, show=False)


# ------------------------------------------------------------------------------------------------------------------- #
# HAR
# ------------------------------------------------------------------------------------------------------------------- #
har_data_df = recommender.load.generate_har_csv(cwd_, OH_PROFILES_PATH, language='pt', metadata_dict=metadata_dict)
vis.group.plot_activity_distributuions_by_worktype(har_data_df, save_path=PLOT_PATH, show=False)
vis.group.plot_sensor_metric_by_worktype(har_data_df, 'HAR_steps.num_steps', save_path=PLOT_PATH, x_label="Número de passos", lower_outlier_limit= 30, show=False)
vis.group.plot_sensor_metric_by_worktype(har_data_df, 'HAR_durations.Sentado_duration_sec', save_path=PLOT_PATH, x_label="Tempo passado em atividade sedentária (hh:mm)",
                                         lower_outlier_limit= 5000, show=False)

# ------------------------------------------------------------------------------------------------------------------- #
# Posture
# ------------------------------------------------------------------------------------------------------------------- #
# load posture data
posture_data_df = recommender.load.generate_posture_csv(cwd_, OH_PROFILES_PATH, metadata_dict=metadata_dict)
vis.group.plot_sensor_metric_by_worktype(posture_data_df, 'posture_95_confidence_ellipse_area', save_path=PLOT_PATH, x_label="Area de 95% confiança (m²)", upper_outlier_limit=2, show=False)


# ------------------------------------------------------------------------------------------------------------------- #
# Wrist movements
# ------------------------------------------------------------------------------------------------------------------- #
wrist_data_df = recommender.load.generate_wrist_csv(cwd_, OH_PROFILES_PATH, metadata_dict=metadata_dict)
vis.group.plot_session_trajectories_by_worktype(wrist_data_df, metric_column='WRIST_significant_acceleration_percentage', save_path=PLOT_PATH, show=False)

# ------------------------------------------------------------------------------------------------------------------- #
# Heart rate
# ------------------------------------------------------------------------------------------------------------------- #
hr_data_df = recommender.load.generate_hr_csv(cwd_, OH_PROFILES_PATH, metadata_dict=metadata_dict)
vis.group.plot_hr_ranges_by_worktype(hr_data_df, save_path=PLOT_PATH, show=False)
vis.group.plot_hr_circular_distribution_by_worktype(hr_data_df, save_path=PLOT_PATH, show=False, language='pt')
vis.group.plot_elevated_hr_trajectories_by_worktype(hr_data_df, save_path=PLOT_PATH, show=False)
# vis.group.plot_hr_circular_distribution(hr_data_df[hr_data_df['subject_id'] == 81], language='pt', show_time_legend=True)


# ------------------------------------------------------------------------------------------------------------------- #
# EMG
# ------------------------------------------------------------------------------------------------------------------- #
emg_data_df = recommender.load.generate_emg_csv(cwd_, OH_PROFILES_PATH, metadata_dict=metadata_dict)
vis.group.plot_emg_relative_intensity_by_worktype(emg_data_df, save_path=PLOT_PATH, show=False)
vis.group.plot_elevated_emg_trajectories_by_worktype(emg_data_df, save_path=PLOT_PATH, show=False)
#vis.group.plot_emg_relative_intensity(emg_data_df[emg_data_df['subject_id'] == 81], language='eng')


