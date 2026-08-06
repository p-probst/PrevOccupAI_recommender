# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.special import expit
from typing import Dict

# internal imports
from constants import SUBJECT_ID_COL, SESSION_TIME_COL, SHIFT_COL, DATE_COL, WORK_TYPES, WORKTYPE_COL, SESSION_NUM_COL, \
    USER, SUBJECT_DAY_COL, WEEKDAY_COL
from statistical_analysis.work_load import COMPOSITE_COL

# external imports
project_path = Path(f"C:/Users/{USER}/PycharmProjects/OH_Toolkit")
sys.path.append(str(project_path))
from oh_parser import load_profiles, extract

# ------------------------------------------------------------------------------------------------------------------- #
# constants
# ------------------------------------------------------------------------------------------------------------------- #
TOTAL_DURATION_COL = "total_duration_hour"
MIN_DURATION_H = 1

# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def print_populations_statistics(oh_profile_path: str, metadata_dict: Dict[str, str]) -> None:
    """
    prints populations statistics, such as age, gender, etc.
    :param oh_profile_path: Path to folder containing the OH profiles of all subjects.
    :param metadata_dict: dictionary defining which metadata should be displayed.
    :return: None
    """

    # parse the OH profiles
    profiles = load_profiles(oh_profile_path)

    # extract metadata
    metadata_df = extract(profiles, paths=metadata_dict)

    # change dexterity to english
    metadata_df["dominant_hand"] = metadata_df["dominant_hand"].replace({"D": "R", "E": "L", "O": "A"})

    # calculate BMI
    metadata_df["BMI"] = metadata_df["weight"] / (metadata_df["height"] / 100)**2

    # print the metrics
    print("=" * 60)
    print("Generating population statistics")
    print("=" * 60)
    print(f"number of workers in the work types: {metadata_df[WORKTYPE_COL].value_counts()}")
    print(f"\n{metadata_df.groupby(WORKTYPE_COL)[["age", "BMI"]].agg(["mean", "std", "min", "max"]).round(2)}")
    print(f"\n{metadata_df.groupby(WORKTYPE_COL)[["sex"]].value_counts()}")
    print(f"\n{metadata_df.groupby(WORKTYPE_COL)[["dominant_hand"]].value_counts()}")
    print("\n")



def get_shifts_from_phone_df(phone_df: pd.DataFrame, cml_shifts: bool = True) -> pd.DataFrame:
    """
    extracts the shifts from a dataframe containing sensor metrics extracted from the phone.
    This function can be used to obtain shift information for watch or muscleBAN data.
    :param phone_df: pandas.DataFrame
    :param cml_shifts:
    :return:
    """

    # get the relevant columns
    shift_df = phone_df[[SUBJECT_ID_COL, DATE_COL, SESSION_TIME_COL]].copy()

    # extract the shift time
    shift_df[SHIFT_COL] = shift_df[SESSION_TIME_COL].apply(transform_time_to_shift, cml_shifts=cml_shifts)

    return shift_df

def transform_time_to_shift(acq_time, cml_shifts: bool = True) -> str:
    """
    Transforms the string to a shift. Two shift transformations are available:
    (1) cml_shifts == True: "morning" - "midday" - "afternoon"
    (2) cml_shifts == False: "morning" - "afternoon"
    :param acq_time: the acquisition time. It is assumed that the string has the format "HH-MM-SS"
    :param cml_shifts: whether to use the actual CML shifts (morning, midday, afternoon) or a simplified (morning, afternoon)
    :return: string with shift period.
    """

    if cml_shifts:
        shift = _transform_time_to_cml_shift(acq_time)

    else:
        shift = _transform_time_to_ma_shift(acq_time)

    return shift

def get_shift_counts(analysis_data_df: pd.DataFrame) -> pd.DataFrame:
    """
    gets the shift counts for each subject and also prints the total shift counts per group, as well as per session,
    if the session column is available in the DataFrame. If the DataFrame does not contain the 'shift' column, then
    an empty DataFrame is returned.
    :param analysis_data_df: pre-processed analysis data. The DataFrame should contain the 'shift' column
    :return:
    """

    if SHIFT_COL in analysis_data_df.columns:
        # count the sifts per subject (this has only to be done once for the phone derived sensors in the dataset)
        shift_counts = analysis_data_df.groupby([SUBJECT_ID_COL, SHIFT_COL]).size().unstack(fill_value=0)

        print("----")
        print(f"shift counts per group: \n{analysis_data_df.groupby([WORKTYPE_COL, SHIFT_COL]).size().unstack(fill_value=0)}")

        if SESSION_NUM_COL in analysis_data_df.columns:

            # cycle over the work types
            for work_type in WORK_TYPES:

                # get dataframe only containing the data of the corresponding work type
                sub_df = analysis_data_df[analysis_data_df[WORKTYPE_COL] == work_type]
                # check data distribution
                print(f"Crosstab of session_num and shift for {work_type}: \n{pd.crosstab(sub_df[SESSION_NUM_COL], sub_df[SHIFT_COL])}")


    else:
        print("No \'shift\' column in the analysis data frame. Returning empty DataFrame.")
        # return empty dataframe
        shift_counts = pd.DataFrame()



    return shift_counts


def drop_short_recordings(df: pd.DataFrame, duration_s_col, class_distribution_col) -> pd.DataFrame:
    """
    removes recordings that shorter than 1 hour
    :param df: Raw har_subject_metrics DataFrame.
    :param duration_s_col: column name of the duration column.
    :param class_distribution_col: column name of the class distribution column.
    :return: the dataframe with short recordings removed.
    """

    # Step 1: recover total recording duration (convert it to hours)
    df[TOTAL_DURATION_COL] = (df[duration_s_col] / df[class_distribution_col]) / 3600

    # Step 2: drop short recordings (MCAR, e.g. subject 126)
    n_before = len(df)
    df = df[df[TOTAL_DURATION_COL] >= MIN_DURATION_H].copy()
    print(f"Dropped {n_before - len(df)} subject-day(s) with recording < {MIN_DURATION_H}h "
          f"(retained {len(df)} of {n_before} rows, "
          f"{df[SUBJECT_ID_COL].nunique()} subjects).")

    return df

def generate_subject_day_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    generates a column containing a subject_day identifier. This is needed for LLMs that try to model
    (1 | subject_id/weekday) to account for within day subject data correlation. This can be used when modelling data
    that has been collected per session (e.g., heart rate, EMG)
    :param df: pandas.DataFrame containing population data that is supposed to be used as input to an LMM. It is expected
               that the df has the `subject_id` and `weekday` columns.
    :return: pandas.DataFrame with the addition subject_id/weekday column.
    """

    # generate column
    df[SUBJECT_DAY_COL] = df[SUBJECT_ID_COL].astype(str) + "_" + df[WEEKDAY_COL].astype(str)

    return df


def centring_decomposition(analysis_data_df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """
    Add within-person centring columns.

    Three columns are added to the dataframe:

    - ``{column_name}_mean_subj``: each subject's mean composite across all their valid days (between-person component).
    - ``workload_dev``: daily deviation from the subject mean (within-person component); ``workload_composite - workload_mean_subj``.

    Person-mean centring decomposes the composite into orthogonal between- and within-person components, ensuring that
    the coefficient of ``workload_dev`` in a subsequent LMM estimates the within-person workload-EMG association without
    confounding by stable between-subject differences in workload perception (Curran & Bauer, 2011).

    :param analysis_data_df: pre-processed workload data. Already contains the composite workload item
    :param column_name: column name of column to decompose
    :returns: Copy of ``df`` with the new columns appended.

    :reference: Curran, P. J., & Bauer, D. J. (2011). The disaggregation of within-person and between-person effects in
                longitudinal models of change. *Annual Review of Psychology*, *62*, 583–619.
                https://doi.org/10.1146/annurev.psych.093008.100356
    """
    analysis_data_df = analysis_data_df.copy()

    subj_mean = analysis_data_df.groupby(SUBJECT_ID_COL)[column_name].transform("mean")

    # create column names
    between_component = f"{column_name}_between"
    within_component = f"{column_name}_within"

    analysis_data_df[between_component] = subj_mean
    analysis_data_df[within_component] = analysis_data_df[column_name] - subj_mean

    return analysis_data_df


def centring_decomposition_agg_day(analysis_data_df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """
    Add within-person centring columns.

    Three columns are added to the dataframe:

    - ``{column_name}_mean_subj``: each subject's mean composite across all their valid days (between-person component).
    - ``workload_dev``: daily deviation from the subject mean (within-person component); ``workload_composite - workload_mean_subj``.

    Person-mean centring decomposes the composite into orthogonal between- and within-person components, ensuring that
    the coefficient of ``workload_dev`` in a subsequent LMM estimates the within-person workload-EMG association without
    confounding by stable between-subject differences in workload perception (Curran & Bauer, 2011).

    :param analysis_data_df: pre-processed workload data. Already contains the composite workload item
    :param column_name: column name of column to decompose
    :returns: Copy of ``df`` with the new columns appended.

    :reference: Curran, P. J., & Bauer, D. J. (2011). The disaggregation of within-person and between-person effects in
                longitudinal models of change. *Annual Review of Psychology*, *62*, 583–619.
                https://doi.org/10.1146/annurev.psych.093008.100356
    """
    analysis_data_df = analysis_data_df.copy()

    day_agg_col = f"{column_name}_day"
    # aggregate the data over the day (calculate mean for EMG, get the first entry for the workload, since they are all the same)
    day_agg_df = analysis_data_df.groupby([SUBJECT_ID_COL, WEEKDAY_COL]).agg(**{COMPOSITE_COL: (COMPOSITE_COL, "first"),
                                                                              day_agg_col: (column_name, "mean")}).reset_index()

    # calculate the mean over the week
    subj_mean = day_agg_df.groupby(SUBJECT_ID_COL)[day_agg_col].transform("mean")

    # create column names
    between_component = f"{column_name}_between"
    within_component = f"{column_name}_within"

    day_agg_df[between_component] = subj_mean
    day_agg_df[within_component] = day_agg_df[day_agg_col] - subj_mean

    return day_agg_df.dropna()


def generate_file_prefix(outcome: str, vc_formula: Dict[str, str] = None) -> str:
    """
    generates file name pre-fix based on outcome and vc_formula.
    :param outcome: outcome variable
    :param vc_formula: formula to add more complex random effects (e.g., (1 | subject_id/weekday)). The dictionary defines
                       the column name and the additional formula (e.g., {"subject_day": "0 + C(subject_day)"}). It is
                       assumed that the df contains the necessary column for modelling.
    :return: file prefix as string
    """

    if vc_formula:

        return f"{outcome}_{list(vc_formula.keys())[0]}"

    else:

        return f"{outcome}"

def get_back_transform(results_df: pd.DataFrame, is_ilr: bool = False) -> pd.DataFrame:
    """
    Transform values back to proportions and odd ratios
    :param results_df: pandas.DataFrame obtained from :function fit_lmm
    :param is_ilr: whether to calculate ILR or not.
    :return: pandas.DataFrame with transformed values added
    """

    # get the estimates
    # [0] = beta_0 (intercept), ..., [3] = beta_3 (morning)
    beta_estimates = results_df["estimate"].to_numpy()[0:-2] # remove ICC and cohen's d
    ci_lows = results_df["CI_lower_95"].to_numpy()[0:-2]
    ci_uppers = results_df["CI_upper_95"].to_numpy()[0:-2]


    # dict to hold the results
    transformed = []

    # cycle over the lmm coefficients
    for index in range(1, len(beta_estimates)):

        # calculate sum for reference shift
        if index == 1:
            bo_sum = beta_estimates[0]
            fo_sum = beta_estimates[0] + beta_estimates[index]

        else:
            bo_sum = beta_estimates[0] + beta_estimates[index]
            fo_sum =  beta_estimates[0] + beta_estimates[1] + beta_estimates[index]

        # calculate the values
        bo_val = get_absolute_rate(bo_sum, is_ilr=is_ilr)
        fo_val = get_absolute_rate(fo_sum, is_ilr=is_ilr)
        odds, ci_low, ci_upper = get_odds_ratio_and_ci(beta_estimates[index], ci_lows[index], ci_uppers[index], is_ilr=is_ilr)

        transformed.append({"BO": bo_val, "FO": fo_val, "OR_group": odds, "OR_CI_low": ci_low, "OR_CI_upper": ci_upper})

    # create DataFrame
    transformed_df = pd.DataFrame(transformed)
    transformed_df['term'] = results_df["term"].iloc[1:-2].values # only get the relevant rows

    # merge the two dataframes and return
    results_df = results_df.merge(transformed_df, on="term", how="left")

    return results_df

def get_absolute_rate(beta_sum, is_ilr: bool = False):
    """
    calculates the log absolute rate for the established log transform
    :param beta_sum: the sum of the LMM coefficients.
    :param is_ilr: whether to calculate ILR or not.
    :return:  absolute rate for log transform
    """
    # ILR transform
    if is_ilr:
        return expit(beta_sum * np.sqrt(2))

    # log transform
    return np.exp(beta_sum)


def get_odds_ratio_and_ci(beta: float, ci_low: float, ci_upper: float, is_ilr: bool = False):
    """
    calculates the odds ratio for the passed LMM coefficient
    :param beta: LLM coefficient
    :param ci_low: low confidence interval
    :param ci_upper: upper confidence interval
    :param is_ilr: whether to calculate ILR
    :return: the ods ratio and the CI interval
    """
    if is_ilr:
        return np.exp(beta * np.sqrt(2)), np.exp(ci_low * np.sqrt(2)), np.exp(ci_upper * np.sqrt(2))

    return np.exp(beta), np.exp(ci_low), np.exp(ci_upper)


# ------------------------------------------------------------------------------------------------------------------- #
# private functions
# ------------------------------------------------------------------------------------------------------------------- #
def _transform_time_to_cml_shift(acq_time: str) -> str:
    """
    Transforms the string to a shift period of either "morning", "midday", or "afternoon".
    :param acq_time: the acquisition time. It is assumed that the string has the format "HH-MM-SS"
    :return: string with shift period.
    """

    # only use the hour
    acq_hour = int(acq_time.split("-")[0])

    # check the time
    if acq_hour < 10:
        shift = "morning"

    elif acq_hour < 13:
        shift = "midday"

    else:
        shift = "afternoon"

    return shift

def _transform_time_to_ma_shift(acq_time: str) -> str:
    """
    Transforms the string to a shift period of either "morning", or "afternoon".
    :param acq_time: the acquisition time. It is assumed that the string has the format "HH-MM-SS"
    :return: string with shift period.
    """

    # only use the hour
    acq_hour = int(acq_time.split("-")[0])

    # check the time
    if acq_hour < 12:
        shift = "morning"

    else:
        shift = "afternoon"

    return shift


