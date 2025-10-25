# backend/core/logging.py
from loguru import logger
import sys

# wipe default handlers and set our sinks
logger.remove()

# log to stdout (so `docker compose logs` shows useful info)
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | {level} | {message}",
    level="INFO",
    backtrace=False,
    diagnose=False,
)

# also keep a rotating file in the container
logger.add(
    "cdri.log",
    rotation="5 MB",
    retention=5,
    level="INFO",
    backtrace=False,
    diagnose=False,
)

def get_logger(name: str = "cdri"):
    # attach contextual info like service name
    return logger.bind(service=name)
