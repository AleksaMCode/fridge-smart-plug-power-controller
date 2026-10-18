import os

from dotenv import load_dotenv

load_dotenv()

TAPO_EMAIL = os.environ["TAPO_EMAIL"]
TAPO_PASSWORD = os.environ["TAPO_PASSWORD"]
TAPO_PLUG_IP = os.environ["TAPO_PLUG_IP"]
TAPO_HUB_IP = os.environ["TAPO_HUB_IP"]
TAPO_TEMP_SENSOR_ID = os.environ["TAPO_TEMP_SENSOR_ID"]

USE_TEMP_SENSOR = os.environ["USE_TEMP_SENSOR"].strip().lower() == "true"

OWM_API_KEY = os.environ["OWM_API_KEY"]
OWM_LOCATION = os.environ["OWM_LOCATION"]

CONTROLLER_TIMEOUT = int(os.environ["CONTROLLER_TIMEOUT"])
TEMPERATURE_THRESHOLD = float(os.environ["TEMPERATURE_THRESHOLD"])
TEMPERATURE_DELTA = float(os.environ["TEMPERATURE_DELTA"])
