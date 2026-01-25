# file for testing the recommender
import json
from pathlib import Path
import pandas as pd

from recommender.noise import generate_noise_csv, get_noise_exposure_recommendations, get_continuous_noise_recommendations


# set path to OH profiles
OH_PROFILES_PATH = "E:\\Backup PrevOccupAI_PLUS Data\\OH_profiles"


# define working directory
cwd_ = Path.cwd()

# define subject (for testing)
subject_id = 80

# load the OH profile and the recommendation system json
with open(cwd_ / "recommender/recommendations.json", "r", encoding="utf-8") as file:

    recommendation_system = json.load(file)

with open(Path(OH_PROFILES_PATH) /f"{subject_id}_OH_profile.json", "r", encoding="utf-8") as file:

    oh_profile = json.load(file)


# load noise risk subjects
noise_risk_subjects_df = generate_noise_csv(cwd_, OH_PROFILES_PATH)


# get noise exposure recommendations
noise_exposure_recommendations = get_noise_exposure_recommendations(noise_risk_subjects_df, subject_id, recommendation_system)
noise_continuous_recommendations = get_continuous_noise_recommendations(oh_profile, recommendation_system)

print(noise_exposure_recommendations)

