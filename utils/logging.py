import logging
import os

def get_logger(name, filename=None, write_to_file:bool=False) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if write_to_file:
        if not os.path.exists("Logs"):
            os.makedirs("Logs")
        fh = logging.FileHandler(
            f"Logs/{filename if filename else name}.log",
            encoding="utf-8"
        )
        fh.setLevel(logging.DEBUG)
        ff = logging.Formatter(
            "[%(asctime)s] %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %I:%M:%S"
        )
        fh.setFormatter(ff)
        logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    cf = logging.Formatter(
        "[%(asctime)s] %(message)s",
        datefmt="%I:%M:%S"
    )
    ch.setFormatter(cf)
    logger.addHandler(ch)

    return logger