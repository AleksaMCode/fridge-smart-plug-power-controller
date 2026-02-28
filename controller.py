import asyncio
import time
from typing import Optional

from logger import get_logger
from openweathermap_adapter.weather_adapter import WeatherAdapter
from settings import CONTROLLER_TIMEOUT, TEMPERATURE_DELTA, TEMPERATURE_THRESHOLD
from tapo_plug_adapter.tapo_plug_adapter import PlugAdapter
from util import is_temperature_above_threshold, is_temperature_below_threshold

logger = get_logger(__name__)
TEMP_CACHE_TTL_SECONDS = 60 * 30


async def init():
    await PlugAdapter().turn_off()


async def control():
    """
    Checks temperature against its thresholds every 10 minutes and changes the power status if needed.
    """
    await init()
    weather_adapter = WeatherAdapter()
    temp_cache: dict[str, Optional[float]] = {"temp": None, "timestamp": None}
    first_fetch_failure_timestamp = None

    while True:
        # Create a new smart plug adapter each time. #techdebt
        # TODO: Maybe fix in the future. See #24 for more info.
        plug_adapter = PlugAdapter()
        logger.info("Checking threshold temperature.")
        now = time.time()
        current_temp = None
        try:
            current_temp = weather_adapter.get_current_temp()
            temp_cache["temp"] = current_temp
            temp_cache["timestamp"] = now
            first_fetch_failure_timestamp = None
        except Exception as e:
            logger.error(f"Failed to fetch current temperature: {str(e)}")
            has_cache = (
                temp_cache["temp"] is not None
                and temp_cache["timestamp"] is not None
                and now - temp_cache["timestamp"] <= TEMP_CACHE_TTL_SECONDS
            )
            if has_cache:
                current_temp = temp_cache["temp"]
                logger.warning(
                    f"Using cached temperature {current_temp} °C (valid for 30 minutes)."
                )
            else:
                if first_fetch_failure_timestamp is None:
                    first_fetch_failure_timestamp = now

                unavailable_for_seconds = now - first_fetch_failure_timestamp
                if unavailable_for_seconds >= TEMP_CACHE_TTL_SECONDS:
                    # The idea for this "safety" policy is food safety first.
                    logger.error(
                        "Weather data unavailable for over 30 minutes. Entering safe mode and forcing fridge ON."
                    )
                    await plug_adapter.turn_on()
                else:
                    minutes_left = int(
                        (TEMP_CACHE_TTL_SECONDS - unavailable_for_seconds) // 60
                    )
                    logger.warning(
                        f"No valid temperature data yet. Waiting up to 30 minutes before safe mode. Remaining: {minutes_left} minutes."
                    )
                time.sleep(CONTROLLER_TIMEOUT)
                continue

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
