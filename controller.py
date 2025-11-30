import asyncio
import time

from logger import get_logger
from openweathermap_adapter.weather_adapter import WeatherAdapter
from settings import CONTROLLER_TIMEOUT, TEMPERATURE_DELTA, TEMPERATURE_THRESHOLD
from tapo_plug_adapter.tapo_plug_adapter import PlugAdapter
from util import is_temperature_above_threshold, is_temperature_below_threshold

logger = get_logger(__name__)


async def init():
    await PlugAdapter().turn_off()


async def control():
    """
    Checks temperature against its thresholds every 10 minutes and changes the power status if needed.
    """
    await init()
    weather_adapter = WeatherAdapter()

    while True:
        # Create a new smart plug adapter each time. This is a hack. #techdebt
        # Maybe fix in the future. See #24 for more info.
        plug_adapter = PlugAdapter()
        logger.info("Checking threshold temperature.")
        current_temp = weather_adapter.get_current_temp()
        if is_temperature_above_threshold(current_temp):
            await plug_adapter.turn_on()
        elif is_temperature_below_threshold(current_temp):
            await plug_adapter.turn_off()
        else:
            logger.info(
                f"Controller is in an idle state. The temperature is between {TEMPERATURE_THRESHOLD - TEMPERATURE_DELTA} °C and {TEMPERATURE_THRESHOLD} °C"
            )

        time.sleep(CONTROLLER_TIMEOUT)


if __name__ == "__main__":
    asyncio.run(control())
