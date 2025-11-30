import logging

from pyowm import OWM
from pyowm.commons import exceptions
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_exponential

from logger import get_logger
from settings import OWM_API_KEY, OWM_LOCATION

logger = get_logger(__name__)


class WeatherAdapter:
    def __init__(self):
        self._owm = OWM(OWM_API_KEY)
        self._manager = self._owm.weather_manager()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=15, max=60),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.ERROR),
        reraise=True,
    )
    def get_current_temp(self):
        logger.info("🌡️ Fetching current temperature from OWM API.")
        try:
            current_weather = self._manager.weather_at_place(OWM_LOCATION).weather
            current_temperature = current_weather.temperature("celsius")["temp"]
            logger.info(f"Current temperature: {current_temperature} °C")
            return current_temperature
        except exceptions.NotFoundError as e:
            logger.error(f"Cannot find the city '{OWM_LOCATION}': {str(e)}")
            raise
        except Exception as e:
            logger.error(
                f"An error occurred during temperature fetching from OWM API: {str(e)}"
            )
            raise
