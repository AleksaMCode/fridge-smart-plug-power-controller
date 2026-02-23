import importlib
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

FAKE_SETTINGS = types.ModuleType("settings")
FAKE_SETTINGS.OWM_API_KEY = "test-key"
FAKE_SETTINGS.OWM_LOCATION = "Paris, FR"

FAKE_PYOWM = types.ModuleType("pyowm")
FAKE_PYOWM.OWM = object

FAKE_PYOWM_COMMONS = types.ModuleType("pyowm.commons")
FAKE_EXCEPTIONS = types.SimpleNamespace(
    NotFoundError=type("NotFoundError", (Exception,), {})
)
FAKE_PYOWM_COMMONS.exceptions = FAKE_EXCEPTIONS

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
        "pyowm": FAKE_PYOWM,
        "pyowm.commons": FAKE_PYOWM_COMMONS,
        "tenacity": FAKE_TENACITY,
    },
):
    sys.modules.pop("openweathermap_adapter.weather_adapter", None)
    weather_module = importlib.import_module("openweathermap_adapter.weather_adapter")


class WeatherAdapterTests(unittest.TestCase):
    def test_get_current_temp_returns_temperature_from_owm(self):
        manager = MagicMock()
        weather = MagicMock()
        weather.temperature.return_value = {"temp": 6.8}
        manager.weather_at_place.return_value = types.SimpleNamespace(weather=weather)

        owm_client = MagicMock()
        owm_client.weather_manager.return_value = manager

        with patch.object(weather_module, "OWM", return_value=owm_client):
            adapter = weather_module.WeatherAdapter()
            current_temp = weather_module.WeatherAdapter.get_current_temp.__wrapped__(
                adapter
            )

        self.assertEqual(current_temp, 6.8)
        manager.weather_at_place.assert_called_once_with("Paris, FR")
        weather.temperature.assert_called_once_with("celsius")

    def test_get_current_temp_raises_not_found_error(self):
        manager = MagicMock()
        manager.weather_at_place.side_effect = weather_module.exceptions.NotFoundError(
            "City not found"
        )

        owm_client = MagicMock()
        owm_client.weather_manager.return_value = manager

        with patch.object(weather_module, "OWM", return_value=owm_client):
            adapter = weather_module.WeatherAdapter()
            with self.assertRaises(weather_module.exceptions.NotFoundError):
                weather_module.WeatherAdapter.get_current_temp.__wrapped__(adapter)

    def test_get_current_temp_raises_generic_error(self):
        manager = MagicMock()
        manager.weather_at_place.side_effect = RuntimeError("Temporary API issue")

        owm_client = MagicMock()
        owm_client.weather_manager.return_value = manager

        with patch.object(weather_module, "OWM", return_value=owm_client):
            adapter = weather_module.WeatherAdapter()
            with self.assertRaises(RuntimeError):
                weather_module.WeatherAdapter.get_current_temp.__wrapped__(adapter)


if __name__ == "__main__":
    unittest.main()
