import importlib
import sys
import types
import unittest
from unittest.mock import patch

FAKE_SETTINGS = types.ModuleType("settings")
FAKE_SETTINGS.TEMPERATURE_THRESHOLD = 5.0
FAKE_SETTINGS.TEMPERATURE_DELTA = 2.0


with patch.dict(sys.modules, {"settings": FAKE_SETTINGS}):
    util = importlib.import_module("util")


class TemperatureHelpersTests(unittest.TestCase):
    def test_is_temperature_above_threshold_true_on_boundary(self):
        self.assertTrue(util.is_temperature_above_threshold(5.0))
        self.assertTrue(util.is_temperature_above_threshold(8.5))

    def test_is_temperature_below_threshold_true_on_boundary(self):
        self.assertTrue(util.is_temperature_below_threshold(3.0))
        self.assertTrue(util.is_temperature_below_threshold(-2.0))

    def test_temperature_in_hysteresis_window_returns_false_for_both_checks(self):
        self.assertFalse(util.is_temperature_above_threshold(4.2))
        self.assertFalse(util.is_temperature_below_threshold(4.2))


if __name__ == "__main__":
    unittest.main()
