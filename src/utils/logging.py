import sys
from loguru import logger
from config.settings import get_settings

settings = get_settings()

logger.remove()
logger.add(sys.stderr, level=settings.log_level)