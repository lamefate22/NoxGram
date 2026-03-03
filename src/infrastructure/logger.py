from loguru._logger import Logger
from loguru import logger
import sys


def setup_logger(slevel: str = "INFO", flevel: str = "DEBUG") -> Logger:
    """
    Initial logger setup function.

    :param slevel: logging level for sys.stdout.
    :param flevel: logging level for output to file.
    """
    logger.remove()

    logger.add(
        sink=sys.stdout,
        level=slevel,
        format="<cyan>{time:MMM D HH:mm:ss}</cyan> | <level>{level}</level> | <magenta>{name}.{function}():{line}</magenta> - {message}",
        colorize=True,
        enqueue=True
    )

    logger.add(
        sink="data/logs/log.nox",
        level=flevel,
        format="{time:MMM D HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        rotation="1 week",
        enqueue=True
    )

    return logger

log = setup_logger()
