from tapo import ApiClient

from settings import TAPO_EMAIL, TAPO_PASSWORD, TAPO_PLUG_IP


class PlugAdapter:
    def __init__(self):
        self._ip = TAPO_PLUG_IP
        self._api_client = ApiClient(TAPO_EMAIL, TAPO_PASSWORD)
        self._device = None
        self._state = False

    async def _init_device(self):
        if self._device is None:
            try:
                self._device = await self._api_client.p110(self._ip)
            except Exception as e:
                print(e)

    async def turn_on(self):
        await self._init_device()
        if self._device:
            info = await self._device.get_device_info()
            if not info.device_on:
                await self._device.on()
                self._state = True
                print(f"Device at {self._ip} turned ON")
            else:
                print(f"Device at {self._ip} remains to be ON")

    async def turn_off(self):
        await self._init_device()
        if self._device:
            info = await self._device.get_device_info()
            if info.device_on:
                await self._device.off()
                self._state = False
                print(f"Device at {self._ip} turned OFF")
            else:
                print(f"Device at {self._ip} remains to be OFF")
