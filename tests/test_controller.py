import importlib
import sys
import types
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

FAKE_SETTINGS = types.ModuleType("settings")
FAKE_SETTINGS.CONTROLLER_TIMEOUT = 1
FAKE_SETTINGS.TEMPERATURE_THRESHOLD = 5.0
FAKE_SETTINGS.TEMPERATURE_DELTA = 2.0

FAKE_WEATHER_MODULE = types.ModuleType("openweathermap_adapter.weather_adapter")
FAKE_WEATHER_MODULE.WeatherAdapter = object

FAKE_PLUG_MODULE = types.ModuleType("tapo_plug_adapter.tapo_plug_adapter")
FAKE_PLUG_MODULE.PlugAdapter = object

with patch.dict(
    sys.modules,
    {
        "settings": FAKE_SETTINGS,
        "openweathermap_adapter.weather_adapter": FAKE_WEATHER_MODULE,
        "tapo_plug_adapter.tapo_plug_adapter": FAKE_PLUG_MODULE,
    },
):
    sys.modules.pop("controller", None)
    controller = importlib.import_module("controller")


class ControllerFlowTests(unittest.IsolatedAsyncioTestCase):
    async def test_init_turns_plug_off(self):
        init_adapter = MagicMock()
        init_adapter.turn_off = AsyncMock()

        with patch.object(controller, "PlugAdapter", return_value=init_adapter):
            await controller.init()

        init_adapter.turn_off.assert_awaited_once()

    async def test_control_turns_on_when_temperature_above_threshold(self):
        init_adapter = MagicMock()
        init_adapter.turn_off = AsyncMock()

        loop_adapter = MagicMock()
        loop_adapter.turn_on = AsyncMock()
        loop_adapter.turn_off = AsyncMock()

        weather_adapter = MagicMock()
        weather_adapter.get_current_temp.return_value = 7.0

        with patch.object(
            controller, "PlugAdapter", side_effect=[init_adapter, loop_adapter]
        ), patch.object(
            controller, "WeatherAdapter", return_value=weather_adapter
        ), patch.object(
            controller.time, "sleep", side_effect=RuntimeError("stop loop")
        ):
            with self.assertRaises(RuntimeError):
                await controller.control()

        loop_adapter.turn_on.assert_awaited_once()
        loop_adapter.turn_off.assert_not_awaited()

    async def test_control_turns_off_when_temperature_below_threshold(self):
        init_adapter = MagicMock()
        init_adapter.turn_off = AsyncMock()

        loop_adapter = MagicMock()
        loop_adapter.turn_on = AsyncMock()
        loop_adapter.turn_off = AsyncMock()

        weather_adapter = MagicMock()
        weather_adapter.get_current_temp.return_value = 2.5

        with patch.object(
            controller, "PlugAdapter", side_effect=[init_adapter, loop_adapter]
        ), patch.object(
            controller, "WeatherAdapter", return_value=weather_adapter
        ), patch.object(
            controller.time, "sleep", side_effect=RuntimeError("stop loop")
        ):
            with self.assertRaises(RuntimeError):
                await controller.control()

        loop_adapter.turn_off.assert_awaited_once()
        loop_adapter.turn_on.assert_not_awaited()

    async def test_control_stays_idle_when_temperature_is_in_hysteresis_window(self):
        init_adapter = MagicMock()
        init_adapter.turn_off = AsyncMock()

        loop_adapter = MagicMock()
        loop_adapter.turn_on = AsyncMock()
        loop_adapter.turn_off = AsyncMock()

        weather_adapter = MagicMock()
        weather_adapter.get_current_temp.return_value = 4.0

        with patch.object(
            controller, "PlugAdapter", side_effect=[init_adapter, loop_adapter]
        ), patch.object(
            controller, "WeatherAdapter", return_value=weather_adapter
        ), patch.object(
            controller.time, "sleep", side_effect=RuntimeError("stop loop")
        ):
            with self.assertRaises(RuntimeError):
                await controller.control()

        loop_adapter.turn_off.assert_not_awaited()
        loop_adapter.turn_on.assert_not_awaited()

    async def test_control_uses_cached_temperature_when_fetch_fails_and_cache_is_fresh(
        self,
    ):
        init_adapter = MagicMock()
        init_adapter.turn_off = AsyncMock()

        first_loop_adapter = MagicMock()
        first_loop_adapter.turn_on = AsyncMock()
        first_loop_adapter.turn_off = AsyncMock()

        second_loop_adapter = MagicMock()
        second_loop_adapter.turn_on = AsyncMock()
        second_loop_adapter.turn_off = AsyncMock()

        weather_adapter = MagicMock()
        weather_adapter.get_current_temp.side_effect = [7.0, RuntimeError("OWM down")]

        with patch.object(
            controller,
            "PlugAdapter",
            side_effect=[init_adapter, first_loop_adapter, second_loop_adapter],
        ), patch.object(
            controller, "WeatherAdapter", return_value=weather_adapter
        ), patch.object(
            controller.time, "time", side_effect=[1000.0, 1010.0]
        ), patch.object(
            controller.time, "sleep", side_effect=[None, RuntimeError("stop loop")]
        ):
            with self.assertRaises(RuntimeError):
                await controller.control()

        first_loop_adapter.turn_on.assert_awaited_once()
        second_loop_adapter.turn_on.assert_awaited_once()
        second_loop_adapter.turn_off.assert_not_awaited()

    async def test_control_enters_safe_mode_after_30_minutes_without_valid_data(self):
        init_adapter = MagicMock()
        init_adapter.turn_off = AsyncMock()

        first_loop_adapter = MagicMock()
        first_loop_adapter.turn_on = AsyncMock()
        first_loop_adapter.turn_off = AsyncMock()

        second_loop_adapter = MagicMock()
        second_loop_adapter.turn_on = AsyncMock()
        second_loop_adapter.turn_off = AsyncMock()

        weather_adapter = MagicMock()
        weather_adapter.get_current_temp.side_effect = [
            RuntimeError("OWM down"),
            RuntimeError("OWM still down"),
        ]

        with patch.object(
            controller,
            "PlugAdapter",
            side_effect=[init_adapter, first_loop_adapter, second_loop_adapter],
        ), patch.object(
            controller, "WeatherAdapter", return_value=weather_adapter
        ), patch.object(
            controller.time, "time", side_effect=[1000.0, 2801.0]
        ), patch.object(
            controller.time, "sleep", side_effect=[None, RuntimeError("stop loop")]
        ):
            with self.assertRaises(RuntimeError):
                await controller.control()

        first_loop_adapter.turn_on.assert_not_awaited()
        second_loop_adapter.turn_on.assert_awaited_once()
        second_loop_adapter.turn_off.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
