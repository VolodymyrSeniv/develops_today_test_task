import sys

from loguru import logger

LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} | {message}"


def setup_logging() -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        format=LOG_FORMAT,
        level="INFO",
        enqueue=True,
    )
