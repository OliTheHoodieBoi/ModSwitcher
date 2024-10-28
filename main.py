from logger import CustomLogger
from tray import TrayIcon


def main():
    logger = CustomLogger("logs")
    tray = TrayIcon(logger=logger, icon="icon.ico")

    try:
        tray.run()
    except KeyboardInterrupt:
        logger.fatal("Exited with KeyboardInterrupt")
    except BaseException as e:
        logger.fatal(str(e))
    finally:
        logger.alert("Mod switcher has stopped.")
        tray.stop()
        observer.stop()
        observer.join()


class SetupError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class IllegalStateException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


if __name__ == "__main__":
    main()
