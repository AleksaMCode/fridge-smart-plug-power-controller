import logging

from tapo import ApiClient
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_exponential

from logger import get_logger
from settings import TAPO_EMAIL, TAPO_PASSWORD, TAPO_PLUG_IP

logger = get_logger(__name__)


class PlugAdapter:
    def __init__(self):
        self._ip = TAPO_PLUG_IP
        self._api_client = ApiClient(TAPO_EMAIL, TAPO_PASSWORD)
        self._device = None
        self._state = False

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=15, max=60),
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
