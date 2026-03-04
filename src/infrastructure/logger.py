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
        sys.stdout,
        level=slevel,
        enqueue=True,
        colorize=True,
        format="<d>{time:HH:mm:ss}</d> <fg #6B7280>|</fg #6B7280> <fg #3B82F6>{level}</fg #3B82F6> <fg #6B7280>|</fg #6B7280> <fg #4B5563>{name}.{function}:{line}</fg #4B5563> <fg #6B7280>|</fg #6B7280> <fg #E5E7EB>{message}</fg #E5E7EB>"
    )

    logger.add(
        "data/logs/log.txt",
        enqueue=True,
        level=flevel,
        rotation="1 week",
        format="{time:HH:mm:ss} | {level} | {name}.{function}:{line} | {message}"
    )

    return logger

log = setup_logger()
