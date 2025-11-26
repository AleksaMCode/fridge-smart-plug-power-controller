import asyncio
import time

from logger import get_logger
from openweathermap_adapter.weather_adapter import WeatherAdapter
from settings import CONTROLLER_TIMEOUT
from tapo_plug_adapter.tapo_plug_adapter import PlugAdapter
from util import is_temperature_above_threshold, is_temperature_below_threshold

plug_adapter = PlugAdapter()
weather_adapter = WeatherAdapter()


logger = get_logger(__name__)


async def control():
    """
    Checks temperature against its thresholds every 10 minutes and changes the power status if needed.
    """
    while True:
        logger.info("Checking threshold temperature.")
        current_temp = weather_adapter.get_current_temp()
        if is_temperature_above_threshold(current_temp):
            await plug_adapter.turn_on()
        elif is_temperature_below_threshold(current_temp):
            await plug_adapter.turn_off()
        time.sleep(CONTROLLER_TIMEOUT)


if __name__ == "__main__":
    asyncio.run(control())
