from loguru import logger
logger.add("cdri.log", rotation="5 MB", retention=5)
