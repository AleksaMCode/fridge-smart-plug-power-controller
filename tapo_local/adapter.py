import logging
from abc import ABC, abstractmethod

from tapo import ApiClient
from tapo.responses import T31XResult
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_exponential

from logger import get_logger
from openweathermap.adapter import WeatherInterface
from settings import TAPO_EMAIL, TAPO_PASSWORD

logger = get_logger(__name__)


class TapoDevice(ABC):
    def __init__(self, ip: str):
        self._ip = ip
        self._api_client = ApiClient(TAPO_EMAIL, TAPO_PASSWORD)
        self._device = None
        self._state = False

    @abstractmethod
    async def _init_device(self):
        pass


class PlugAdapter(TapoDevice):
    @retry(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, min=30, max=180),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.ERROR),
        reraise=True,
    )
    async def _init_device(self):
        try:
            logger.info(f"🔌 Connecting to smart plug device at {self._ip}")
            self._device = await self._api_client.p110(self._ip)
            logger.info("Connected to smart plug device")
        except Exception as e:
            logger.error(f"Failed to connect to smart plug device: {str(e)}")
            raise

    async def _reset_device_callback(self, retry_state):
        """
        Tenacity will call this before each retry when trying to switch state of the device.
        """
        logger.warning("Reinitializing device")
        await self._init_device()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=15, max=60),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.ERROR),
        before_sleep=_reset_device_callback,
        reraise=True,
    )
    async def turn_on(self):
        if not self._device:
            await self._init_device()

        try:
            info = await self._device.get_device_info()
            if not info.device_on:
                await self._device.on()
                self._state = True
                logger.info(f"Device '{info.nickname}' turned ON")
            else:
                logger.info(f"Device '{info.nickname}' remains to be ON")
        except Exception as e:
            logger.error(f"Failed to interact with device: {str(e)}")

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=15, max=60),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.ERROR),
        before_sleep=_reset_device_callback,
        reraise=True,
    )
    async def turn_off(self):
        if not self._device:
            await self._init_device()

        try:
            if self._device:
                info = await self._device.get_device_info()
                if info.device_on:
                    await self._device.off()
                    self._state = False
                    logger.info(f"Device '{info.nickname}' turned OFF")
                else:
                    logger.info(f"Device '{info.nickname}' remains to be OFF")
        except Exception as e:
            logger.error(f"Failed to interact with device: {str(e)}")


class SensorAdapter(TapoDevice, WeatherInterface):
    @retry(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, min=30, max=180),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.ERROR),
        reraise=True,
    )
    async def _init_device(self):
        try:
            logger.info(f"🔌 Connecting to hub device at {self._ip}")
            hub = await self._api_client.h100(self._ip)
            # info = await hub.get_device_info()
            # This doesn't seem to work:
            self._device = await hub.t31x()
            # Alternative approach:
            logger.info(f"🔌 Connecting to temp. sensor device at {self._ip}")
            child_device_list = await hub.get_child_device_list()
            for child in child_device_list:
                if isinstance(child, T31XResult):
                    self._device = await hub.t31x(device_id=child.device_id)
                    logger.info("Connected to temp. sensor device")
            raise Exception(
                "Failed to connect to temp. sensor device - no sensor children in the H100 hub."
            )
        except Exception as e:
            logger.error(f"Failed to connect to temp. sensor device: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, min=30, max=180),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.ERROR),
        reraise=True,
    )
    async def get_current_temp(self):
        if not self._device:
            await self._init_device()

        records = await self._device.get_temperature_humidity_records()
        # latest reading
        latest = records.records[-1]
        return latest.temperature
