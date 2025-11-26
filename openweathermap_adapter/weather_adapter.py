from pyowm import OWM
from pyowm.commons import exceptions

from logger import get_logger
from settings import OWM_API_KEY, OWM_LOCATION

logger = get_logger(__name__)


class WeatherAdapter:
    def __init__(self):
        self._owm = OWM(OWM_API_KEY)
        self._manager = self._owm.weather_manager()

    def get_current_temp(self):
        logger.info("Fetching current temperature from OWM API.")
        try:
            current_weather = self._manager.weather_at_place(OWM_LOCATION).weather
            current_temperature = current_weather.temperature("celsius")["temp"]
            logger.info(f"Current temperature: {current_temperature}")
            return current_temperature
        except exceptions.NotFoundError as e:
            logger.error(f"Cannot find the city '{OWM_LOCATION}': {str(e)}")
            raise
        except Exception as e:
            logger.error(
                f"An error occurred during temperature fetching from OWM API: {str(e)}"
            )
            raise
