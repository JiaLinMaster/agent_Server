import logging

from config import settings

def set_log():
    detailed_format = (
        "%(asctime)s [%(levelname)s] [Thread: %(thread)d] "
        "%(filename)s:%(lineno)d %(funcName)s | %(message)s\n"
        "--------------------"
    )
    logging.basicConfig(
        level=settings.LOGGING_LEVEL,
        format=detailed_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="as.log"
    )