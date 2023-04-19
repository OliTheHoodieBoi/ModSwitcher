import psutil

class Freezer:
    mc_processes: list[psutil.Process] = []

    def __init__(self, root: str):
        self.root = root

    def suspend(self):
        self.mc_processes.clear()
        for process in psutil.process_iter():
            try:
                with process.oneshot():
                    if process.name().lower() == "minecraft.exe" or (
                        process.name().lower() == "javaw.exe" and process.cwd() == str(self.root)):
                        self.mc_processes.append(process)
            except psutil.AccessDenied:
                continue
        for process in self.mc_processes:
            process.suspend()

    def resume(self):
        for process in self.mc_processes:
            process.resume()