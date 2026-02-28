import logging
import os
from logging.handlers import TimedRotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)


LOG_FILE = os.path.join(LOG_DIR, "fsppc-info.log")
FILE_HANDLER = TimedRotatingFileHandler(
    LOG_FILE,
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8",
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[FILE_HANDLER, logging.StreamHandler()],
)


def get_logger(name: str):
    """Returns a namespaced logger for any module."""
    return logging.getLogger(name)
