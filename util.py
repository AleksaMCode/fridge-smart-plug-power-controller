from settings import TEMPERATURE_DELTA, TEMPERATURE_THRESHOLD


def is_temperature_above_threshold(temp: float) -> bool:
    """
    Used to determine if the fridge should be turned on.
    :param temp: Current temperature outside.
    :return: True if the temperature is above the threshold otherwise False.
    """
    return temp > TEMPERATURE_THRESHOLD


def is_temperature_below_threshold(temp: float) -> bool:
    """
    Used to determine if the fridge should be turned off.
    :param temp: Current temperature outside.
    :return: True if the temperature is below the threshold otherwise False.
    """
    return temp < TEMPERATURE_THRESHOLD - TEMPERATURE_DELTA
