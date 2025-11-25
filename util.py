from settings import TEMPERATURE_THRESHOLD


def is_temperature_above_threshold(temp: float) -> bool:
    return temp > TEMPERATURE_THRESHOLD
