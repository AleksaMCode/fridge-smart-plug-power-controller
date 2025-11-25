from pyowm import OWM

from settings import OMW_LOCATION, OWM_API_KEY


class WeatherAdapter:
    def __init__(self):
        self._omw = OWM(OWM_API_KEY)
        self._manager = self._omw.weather_manager()

    def get_current_temp(self):
        current_weather = self._manager.weather_at_place(OMW_LOCATION).weather
        return current_weather.temperature("celsius")["temp"]
