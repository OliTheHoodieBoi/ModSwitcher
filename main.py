import os
from pathlib import Path
from logger import LogWrapper
from tray import TrayIcon
from minecraft_freezer import Freezer

def get_minecraft() -> Path|None:
    '''Get the .minecraft directory'''
    root = os.getenv("MINECRAFT")
    if root:
        return Path(root)
    else:
        appdata = os.getenv("APPDATA")
        if appdata != None:
            root = Path(appdata).joinpath(".minecraft")
            if not root.is_dir():
                return None
        return root

class ModSwitcher:
    log: LogWrapper
    tray: TrayIcon
    game_directory: Path
    freezer: Freezer
    
    def __init__(self, title: str, log: LogWrapper):
        self.log = log

        try:
            # Find game directory
            self.game_directory = get_minecraft()
            if self.game_directory:
                self.logger.info(f'Found .minecraft at "{self.game_directory}"')
            else:
                raise SetupError("Could not find minecraft game directory")

            # Create tray icon
            self.tray = TrayIcon(self.log, title=title, icon="icon.ico")

            # Create freezer
            self.freezer = Freezer(self.game_directory)

        except Exception as e:
            # Abort startup
            if "message" in e:
                self.abort_startup(e.message)
            else:
                self.abort_startup()

    def abort_startup(self, message: str | None):
        if message:
            self.log.logger.fatal("Unable to complete startup:", message)
            self.log.logger.alert("Mod switcher was unable to complete startup:\n" + message)
        else:
            self.log.logger.fatal("Unable to complete startup")
            self.log.logger.alert("Mod switcher was unable to complete startup.")
        self.stop()

    def start(self):
        self.tray.run()

    def stop(self):
        self.log.stop()

def main():
    # Start logger
    logs_directory = "logs"
    log = LogWrapper(logs_directory)

    title = "Mod switcher"
    os.system("title " + title)
    mod_switcher = ModSwitcher(title, log=log)
    mod_switcher.start()

class SetupError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class IllegalStateException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


if __name__ == "__main__":
    main()
