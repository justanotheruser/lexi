import sys

from loguru import logger


def setup_logger() -> None:
    # Configure loguru to output to stdout
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time} | {level} | {message}")
