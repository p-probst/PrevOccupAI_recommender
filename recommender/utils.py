"""
Available Functions
-------------------
[Public]

-------------------
"""
# ------------------------------------------------------------------------------------------------------------------- #
# imports
# ------------------------------------------------------------------------------------------------------------------- #
from datetime import datetime
from babel.dates import format_date
from typing import List
from datetime import datetime, timedelta
from typing import Tuple

# ------------------------------------------------------------------------------------------------------------------- #
# file constants
# ------------------------------------------------------------------------------------------------------------------- #
TIME_FMT = "%H:%M:%S.%f"


# ------------------------------------------------------------------------------------------------------------------- #
# public functions
# ------------------------------------------------------------------------------------------------------------------- #
def dates_to_weekdays(
    dates: List[str],
    date_format: str,
    locale: str = "en"
) -> List[str]:
    """
    Convert a list of date strings to localized weekday names.

    :param dates: List of date strings
    :param date_format: Format used to parse the input dates
    :param locale: Locale code (e.g. 'en', 'pt', 'pt_PT')
    :return: List of weekday names
    """
    return [
        format_date(
            datetime.strptime(d, date_format),
            format="EEEE",
            locale=locale
        )
        for d in dates
    ]

def get_timeline_risk_durations(noise_dict, risk_labels: Tuple[str, str], min_duration_minutes=60 ) -> int:
    """
    Count continuous instances of specified risk_labels in OH profile timeline metrics that last at least a given duration.
    :param noise_dict: Dictionary with time intervals as keys and noise labels as values.
    :param risk_labels: tuple of risk label, according to the labels of the respective timeline
    :param min_duration_minutes: Minimum duration (in minutes) required to count an instance.
    :return:  Number of instances lasting at least min_duration_minutes.
    """

    # Parse and sort intervals by start time
    intervals = []
    for time_range, label in noise_dict.items():
        start_str, end_str = time_range.split("_")
        start = datetime.strptime(start_str, TIME_FMT)
        end = datetime.strptime(end_str, TIME_FMT)
        intervals.append((start, end, label))

    intervals.sort(key=lambda x: x[0])

    count = 0
    current_duration = timedelta(0)
    previous_end = None

    for start, end, label in intervals:
        duration = end - start

        if label in risk_labels:
            if previous_end == start:
                current_duration += duration
            else:
                current_duration = duration
        else:
            if current_duration >= timedelta(minutes=min_duration_minutes):
                count += 1
            current_duration = timedelta(0)

        previous_end = end

    # Final check (in case the last segment qualifies)
    if current_duration >= timedelta(minutes=min_duration_minutes):
        count += 1

    return count