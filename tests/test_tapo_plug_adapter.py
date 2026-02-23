import importlib
import sys
import types
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

FAKE_SETTINGS = types.ModuleType("settings")
FAKE_SETTINGS.TAPO_EMAIL = "test@example.com"
FAKE_SETTINGS.TAPO_PASSWORD = "secret"
FAKE_SETTINGS.TAPO_PLUG_IP = "192.168.1.50"

FAKE_TAPO = types.ModuleType("tapo")
FAKE_TAPO.ApiClient = object

FAKE_TENACITY = types.ModuleType("tenacity")


def _fake_retry(*args, **kwargs):
    def _decorator(func):
        func.__wrapped__ = func
        return func

    return _decorator


def _identity(*args, **kwargs):
    return None


FAKE_TENACITY.retry = _fake_retry
FAKE_TENACITY.after_log = _identity
FAKE_TENACITY.before_log = _identity
FAKE_TENACITY.stop_after_attempt = _identity
FAKE_TENACITY.wait_exponential = _identity


with patch.dict(
    sys.modules,
    {
        "settings": FAKE_SETTINGS,
        "tapo": FAKE_TAPO,
        "tenacity": FAKE_TENACITY,
    },
):
    sys.modules.pop("tapo_plug_adapter.tapo_plug_adapter", None)
    plug_module = importlib.import_module("tapo_plug_adapter.tapo_plug_adapter")


class PlugAdapterTests(unittest.IsolatedAsyncioTestCase):
    async def test_init_device_connects_to_configured_ip(self):
        client = MagicMock()
        device = MagicMock()
        client.p110 = AsyncMock(return_value=device)

        with patch.object(plug_module, "ApiClient", return_value=client):
            adapter = plug_module.PlugAdapter()
            await plug_module.PlugAdapter._init_device.__wrapped__(adapter)

        client.p110.assert_awaited_once_with("192.168.1.50")
        self.assertIs(adapter._device, device)

    async def test_reset_device_callback_reinitializes_device(self):
        with patch.object(plug_module, "ApiClient", return_value=MagicMock()):
            adapter = plug_module.PlugAdapter()

        adapter._init_device = AsyncMock()
        await adapter._reset_device_callback(retry_state=MagicMock())
        adapter._init_device.assert_awaited_once()

    async def test_turn_on_switches_device_when_currently_off(self):
        with patch.object(plug_module, "ApiClient", return_value=MagicMock()):
            adapter = plug_module.PlugAdapter()

        device = MagicMock()
        device.get_device_info = AsyncMock(
            return_value=types.SimpleNamespace(device_on=False, nickname="Fridge Plug")
        )
        device.on = AsyncMock()
        adapter._device = device

        await plug_module.PlugAdapter.turn_on.__wrapped__(adapter)

        device.on.assert_awaited_once()
        self.assertTrue(adapter._state)

    async def test_turn_on_does_not_switch_when_already_on(self):
        with patch.object(plug_module, "ApiClient", return_value=MagicMock()):
            adapter = plug_module.PlugAdapter()

        device = MagicMock()
        device.get_device_info = AsyncMock(
            return_value=types.SimpleNamespace(device_on=True, nickname="Fridge Plug")
        )
        device.on = AsyncMock()
        adapter._device = device

        await plug_module.PlugAdapter.turn_on.__wrapped__(adapter)

        device.on.assert_not_awaited()

    async def test_turn_off_switches_device_when_currently_on(self):
        with patch.object(plug_module, "ApiClient", return_value=MagicMock()):
            adapter = plug_module.PlugAdapter()

        device = MagicMock()
        device.get_device_info = AsyncMock(
            return_value=types.SimpleNamespace(device_on=True, nickname="Fridge Plug")
        )
        device.off = AsyncMock()
        adapter._device = device
        adapter._state = True

        await plug_module.PlugAdapter.turn_off.__wrapped__(adapter)

        device.off.assert_awaited_once()
        self.assertFalse(adapter._state)

    async def test_turn_off_does_not_switch_when_already_off(self):
        with patch.object(plug_module, "ApiClient", return_value=MagicMock()):
            adapter = plug_module.PlugAdapter()

        device = MagicMock()
        device.get_device_info = AsyncMock(
            return_value=types.SimpleNamespace(device_on=False, nickname="Fridge Plug")
        )
        device.off = AsyncMock()
        adapter._device = device

        await plug_module.PlugAdapter.turn_off.__wrapped__(adapter)

        device.off.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
