import subprocess
from pystray import Icon as tray_icon, Menu, MenuItem
from pystray._base import Icon
from PIL import Image

from logger import CustomLogger
from pathlib import Path


class TrayIcon:
    app: Icon
    logger: CustomLogger
    icon: Image.Image | None
    mods_dir: Path | None

    def __init__(
        self,
        logger: CustomLogger,
        name: str = "modswitcher",
        title: str = "Mod switcher",
        icon: str | Path | Image.Image | None = None,
    ):
        self.logger = logger

        # Create tray menu
        self.app = tray_icon(
            name=name,
            title=title,
            menu=Menu(
                MenuItem("Open mods folder", self.open_mods),
                MenuItem("Show logs", self.open_log),
                Menu.SEPARATOR,
                MenuItem("Exit", self.exit_app),
            ),
        )

        # Set icon
        if type(icon) is str or type(icon) is Path:
            with Image.open(icon) as img:
                self.set_icon(img)
        elif type(icon) is Image.Image:
            self.set_icon(icon)
        else:
            self.icon = None

    def set_icon(self, icon: Image.Image):
        self.app.icon = icon

    def set_mods_directory(self, directory: str | Path):
        self.mods_dir = Path(directory)

    def open_mods(self):
        if self.mods_dir is None:
            raise ExitTray("No mods directory")
        else:
            subprocess.call(f'explorer "{self.mods_dir.absolute()}"', shell=True)

    def open_log(self):
        logs = Path(self.logger.get_directory()).absolute()
        subprocess.call(f'explorer "{logs}"', shell=True)

    def exit_app(self):
        raise ExitTray("Exited with tray icon")

    def run(self):
        self.app.run()

    def stop(self):
        self.app.stop()


class ExitTray(Exception):
    def __init__(self, message: str):
        super().__init__(message)
