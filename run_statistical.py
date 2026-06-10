from pathlib import Path
import recommender as recommender
import statistical_analysis as stats
import matplotlib.pyplot as plt

# set path to OH profiles
OH_PROFILES_PATH = "E:\\Backup PrevOccupAI_PLUS Data\\OH_profiles"

# define working directory
cwd_ = Path.cwd()

# define metadata to be extracted and added to the CSV data
metadata_dict = {"work_type": "meta_data.work_type"}

# ------------------------------------------------------------------------------------------------------------------- #
# QUESTIONNAIRES
# ------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------- #
# pain questionnaire
# ------------------------------------------------------------------------------------------------------------------- #

# load pain location data
pain_locations_df = recommender.load.generate_pain_csv( cwd_, OH_PROFILES_PATH, pain_dimension="localização", metadata_dict=metadata_dict)

# perform pain location statistical analysis
stats.perform_pain_location_analysis(pain_locations_df)

# ------------------------------------------------------------------------------------------------------------------- #
# noise sensor
# ------------------------------------------------------------------------------------------------------------------- #
# load noise risk subjects
noise_data_df = recommender.load.generate_noise_csv(cwd_, OH_PROFILES_PATH, language='pt', metadata_dict=metadata_dict)

# check start times
noise_data_df['start_h'] =noise_data_df['session'].str.split('-').str[0]

# perform noise exposure statistical analysis
stats.perform_noise_exposure_analysis(noise_data_df)

#noise_data_df[['sum_loud_noise']].plot.kde()
#plt.show()
#print(noise_data_df['start_h'].value_counts())

print('test')