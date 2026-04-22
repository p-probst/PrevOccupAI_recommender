# file for testing the recommender
import json
from pathlib import Path

import recommender as recommender
import recommender.recommend.sensors as sensor_rec
import recommender.recommend.questionnaires as questionnaire_rec

# set path to OH profiles
OH_PROFILES_PATH = "E:\\Backup PrevOccupAI_PLUS Data\\OH_profiles"
LANGUAGE = 'pt'


# define working directory
cwd_ = Path.cwd()

# define subject (for testing)
subject_id = 81

# load the OH profile and the recommendation system json
with open(cwd_ / "recommender/recommendations.json", "r", encoding="utf-8") as file:

    recommendation_system = json.load(file)

with open(Path(OH_PROFILES_PATH) /f"{subject_id}_OH_profile.json", "r", encoding="utf-8") as file:

    oh_profile = json.load(file)


# ------- get CSV data --------- #
# load noise risk subjects
noise_risk_subjects_df = recommender.load.generate_noise_csv(cwd_, OH_PROFILES_PATH, language=LANGUAGE)

# load HAR subject data
har_subject_data_df = recommender.load.generate_har_csv(cwd_, OH_PROFILES_PATH, language=LANGUAGE)

# load HR subject data
hr_subject_data_df = recommender.load.generate_hr_csv(cwd_, OH_PROFILES_PATH)

# load EMG data
emg_subject_data_df = recommender.load.generate_emg_csv(cwd_, OH_PROFILES_PATH)

# load posture data
posture_subject_data_df = recommender.load.generate_posture_csv(cwd_, OH_PROFILES_PATH)

# load rosa data
rosa_subjects_data_df = recommender.load.generate_rosa_csv(cwd_, OH_PROFILES_PATH)

# load environment data
environment_data_df = recommender.load.generate_environment_csv(cwd_, OH_PROFILES_PATH, language=LANGUAGE)



# ------- get noise exposure recommendations --------- #
noise_exposure_recommendations = sensor_rec.individual.get_noise_exposure_recommendations(noise_risk_subjects_df, subject_id, recommendation_system)
noise_continuous_recommendations = sensor_rec.individual.get_continuous_noise_recommendations(oh_profile, recommendation_system, noise_level_label=['Ruído incomodativo', 'Ruído elevado'])

# ------- get human activities recommendations --------- #
sitting_proportions_recommendations = sensor_rec.individual.get_sitting_proportions_recommendations(har_subject_data_df, subject_id, recommendation_system)
sitting_total_recommendations = sensor_rec.individual.get_total_sitting_duration_recommendation(har_subject_data_df, subject_id, recommendation_system)
sitting_continuous_recommendations_2h = sensor_rec.individual.get_continuous_sitting_recommendations(oh_profile, recommendation_system, activity_class_label=['Sentado'], exposure_limit_minutes=120.0)
sitting_continuous_recommendations_1h = sensor_rec.individual.get_continuous_sitting_recommendations(oh_profile, recommendation_system, activity_class_label=['Sentado'], exposure_limit_minutes=60.0)
standing_proportions_recommendations = sensor_rec.individual.get_standing_proportions_recommendations(har_subject_data_df, subject_id, recommendation_system)
steps_recommendations = sensor_rec.individual.get_steps_recommendations(har_subject_data_df, subject_id, recommendation_system)

# ------- get heart rate recommendations --------- #
max_hr_recommendations = sensor_rec.individual.get_max_frequency_recommendation(hr_subject_data_df, oh_profile, subject_id, recommendation_system)
slightly_elevated_hr_recommendations = sensor_rec.individual.get_elevated_hr_recommendations(hr_subject_data_df, oh_profile, subject_id, 'Ligeiramente elevado', recommendation_system)
elevated_hr_recommendations = sensor_rec.individual.get_elevated_hr_recommendations(hr_subject_data_df, oh_profile, subject_id, 'Elevado', recommendation_system)


# ------- get emg recommendations --------- #
emg_recommendations_above_high = sensor_rec.individual.get_emg_recommendations(emg_subject_data_df, oh_profile, subject_id,
                                                          'high_for_you_pct', 2,
                                                          recommendation_system)

emg_recommendations_high = sensor_rec.individual.get_emg_recommendations(emg_subject_data_df, oh_profile, subject_id,
                                                          'typical_high_pct' , 3,
                                                          recommendation_system)

# ------- get posture recommendations --------- #
low_variability_subjects_df, low_variability_threshold = sensor_rec.group.assess_low_postural_variability(posture_subject_data_df, subject_col='subject_id', ellipse_area_col='posture_95_confidence_ellipse_area')
posture_recommendations = sensor_rec.individual.get_postural_displacement_recommendation(posture_subject_data_df, subject_id, recommendation_system)

# ------- get ROSA and environment recommendations --------- #
rosa_recommendations = questionnaire_rec.individual.get_rosa_recommendations(rosa_subjects_data_df, subject_id, recommendation_system)
environment_recommendations = questionnaire_rec.individual.get_environment_recommendations(environment_data_df, subject_id, recommendation_system)

print('test')

