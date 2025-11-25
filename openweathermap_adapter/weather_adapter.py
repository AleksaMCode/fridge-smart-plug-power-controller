from pyowm import OWM
from pyowm.commons import exceptions

from logger import get_logger
from settings import OMW_LOCATION, OWM_API_KEY

logger = get_logger(__name__)


class WeatherAdapter:
    def __init__(self):
        self._omw = OWM(OWM_API_KEY)
        self._manager = self._omw.weather_manager()

    def get_current_temp(self):
        logger.info("Fetching current temperature from OMW API.")
        try:
            current_weather = self._manager.weather_at_place(OMW_LOCATION).weather
            current_temperature = current_weather.temperature("celsius")["temp"]
            logger.info(f"Current temperature: {current_temperature}")
            return current_temperature
        except exceptions.NotFoundError as e:
            logger.error(f"Cannot find the city '{OMW_LOCATION}': {str(e)}")
        except Exception as e:
            logger.error(
                f"An error occurred during temperature fetching from OMW API: {str(e)}"
            )
            raise
