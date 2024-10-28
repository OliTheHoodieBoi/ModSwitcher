from datetime import datetime
import logging
from logging import Logger
from os import mkdir
from pathlib import Path
from sys import stdout
from ctypes.windll.user32 import MessageBoxW  # type: ignore


class CustomLogger:
    logger: Logger
    directory: str

    def __init__(self, logs_directory: str, level: int | str = logging.INFO):
        self.directory = logs_directory

        logs_path = Path(logs_directory)
        if not logs_path.is_dir():
            try:
                mkdir(logs_path)
            except IOError:
                print("Could not create logs directory")
                MessageBoxW(
                    0,
                    "Mod switcher was unable to complete startup.\nCould not create logs directory",
                    Path(__file__).name,
                    16,
                )
                exit()

        i = 0
        logfile = logs_path.joinpath(
            datetime.now().strftime("%Y-%m-%d-") + str(i) + ".log"
        )
        while logfile.is_file():
            i += 1
            logfile = logs_path.joinpath(
                datetime.now().strftime("%Y-%m-%d-") + str(i) + ".log"
            )

        logger = logging.getLogger()
        logger.setLevel(level)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s]: %(message)s", datefmt="%H:%M:%S"
        )

        file_handler = logging.FileHandler(logfile)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler(stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        self.logger = logger

    def get_logger(self) -> Logger:
        return self.logger

    def get_directory(self) -> str:
        return self.directory

    def debug(self, msg: str, *args: object):
        self.logger.debug(msg, *args)

    def info(self, msg: str, *args: object):
        self.logger.info(msg, *args)

    def warning(self, msg: str, *args: object):
        self.logger.warning(msg, *args)

    def critical(self, msg: str, *args: object):
        self.logger.critical(msg, *args)

    def error(self, msg: str, *args: object):
        self.logger.error(msg, *args)

    def fatal(self, msg: str, *args: object):
        self.logger.fatal(msg, *args)

    def alert(self, msg: str):
        MessageBoxW(0, msg, Path(__file__).name, 16)
        self.info(f"ALERT: {msg}")
