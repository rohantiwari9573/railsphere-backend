from datetime import time


def parse_running_days(day: str) -> dict:
    day = str(day).strip().lower()

    return {
        "monday": day == "monday",
        "tuesday": day == "tuesday",
        "wednesday": day == "wednesday",
        "thursday": day == "thursday",
        "friday": day == "friday",
        "saturday": day == "saturday",
        "sunday": day == "sunday",
    }


def default_start_time():
    return time(0, 0)


def default_end_time():
    return time(23, 59)