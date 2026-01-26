from report_generator.generate_report import generate_report

report_folder_path = r"C:\Users\srale\Desktop\reports_test"
subject_id = 80
plots_path = r"E:\Backup PrevOccupAI_PLUS Data\OH_plots"
oh_profile_path = r"E:\Backup PrevOccupAI_PLUS Data\OH_profiles"

generate_report(report_folder_path, subject_id, plots_path, oh_profile_path)
# run here the recommender together with report generator

# input: the OH-profiles


# establishing text: we should improve our texts using LLMs. The instructions should state that these texts are for
# a non-scientific audience (adults), composed of office workers that for some of them it is the first time seeing
# such data.

# cycle over the OH profiles
# -> for each subject:
# (1) insert the introduction: check what we have from PrevOccupAI and improve it using LLMs

# (2) questionnaires
# (2.1) biomechanical: ROSA, etc.
# (2.2) environmental
# (3.3) COPSOQ: important state that these are population results for all FO/BO (depending on work_type) workers
# (3.4) pain

# (3) sensors
# (3.1) CML sensors (one time sensors)
# (3.2) sensor timeline (weekly sensors)
# (3.3) Noise (to keep it close to CML environment sensors
# (3.4) human activities
# (3.5) posture
# (3.6) wrist_movements
# (3.7) heart rate
# (3.8) EMG

# (4) short conclusion text (can be generic), explaining that this was a recording for one week, but now they know what
# risks they are exposed to. They should be mindful about these risks and when they observe them try to apply the recommendations.
# A big fat thank you for participating (again, as it should have been mentioned in the introduction already), and state
# that we hope that this is just the beginning of an ongoing cooperation with CML to improve worker's health

# (5) references on which we based the text and recommendation on


# How to structure the sections with recommendations
# (1) introductory text giving context and scientific background
# (2) definition of risk rule: this could be at the end of (1), i.e., the last sentence, then in a new line the rule in bold
#     e.g., Given the explained background the following risk-rule/s was/were established to define risk:
#     - If there is at least one continuous 1-hour segment of disturbing noise.
#     - If the combined exposure to disturbing noise and high noise is equal to or greater than 50% of the monitored time.
# (3) show plot
# (4) explanation of plot: how did we extract the information and what does the plot show
# (5) recommendations (here the appropriate recommender function should be called).
#     ATTENTION: We need to think about what to insert when there is no recommendation
