from datetime import datetime
import logging
from logging import Logger, FileHandler, StreamHandler, Formatter
from os import mkdir
from pathlib import Path
from sys import stdout
from ctypes import windll
message_box = windll.user32.MessageBoxW


class LogWrapper:
    logger: Logger
    log_path: Path
    directory: str

    def __init__(self, logs_directory: str, level: int | str = logging.INFO):
        self.directory = logs_directory

        logs_path = Path(logs_directory)
        if not logs_path.is_dir():
            try:
                mkdir(logs_path)
                raise IOError()
            except IOError:
                print("Could not create logs directory")
                self.alert("Mod switcher was unable to complete startup.\n"
                    + "Could not create logs directory")
                exit()

        i = 0
        get_log_path = lambda: logs_path.joinpath(
                datetime.now().strftime("%Y-%m-%d-") + str(i) + ".log"
            )
        self.log_path = get_log_path()
        while self.log_path.is_file():
            i += 1
            self.log_path = get_log_path

        logger = logging.getLogger()
        logger.setLevel(level)
        formatter = Formatter(
            "[%(asctime)s] [%(levelname)s]: %(message)s", datefmt="%H:%M:%S"
        )

        file_handler = FileHandler(self.log_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = StreamHandler(stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        self.logger = logger

    def get_logger(self) -> Logger:
        return self.logger

    def alert(self, msg: str):
        message_box(0, msg, Path(__file__).name, 16)
        self.info(f"ALERT: {msg}")

    def stop(self):
        for handler in self.logger.handlers:
            handler.close()
