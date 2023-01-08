import logging
from sys import stdout
from pathlib import Path
import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
import ctypes
from datetime import datetime
import time
import json
import re

os.chdir(Path(__file__).parent)
logs = Path('logs')
if not logs.is_dir():
    try:
        os.mkdir(logs)
    except IOError:
        print('Could not create logs directory')
        exit()

i = 0
logfile = logs.joinpath(datetime.now().strftime('%Y-%m-%d-') + str(i) + '.log')
while logfile.is_file():
    i += 1
    logfile = logs.joinpath(datetime.now().strftime('%Y-%m-%d-') + str(i) + '.log')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s]: %(message)s',
                                datefmt='%H:%M:%S')

file_handler = logging.FileHandler(logfile)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler(stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Get .minecraft directory
root = None
appdata = os.getenv('APPDATA')
if appdata != None:
    root = Path(appdata).joinpath('.minecraft')
    if not root.is_dir():
        root = None
if root == None:
    logger.fatal('Could not find minecraft game directory')
    exit()
logger.info(f'Found .minecraft at "{root}"')
# Get mods directory
mods_dir = Path(root).joinpath('mods')
if not mods_dir.is_dir():
    logger.fatal('mods folder does not exist, no point in running')
    exit()
logger.info(f'Found mods folder at "{mods_dir}"')
# Get config
config_path = mods_dir.joinpath('.modswitcher.json')
if not config_path.exists():
    try:
        # Create default config
        logger.info(f'"{config_path}" does not exist, creating default config')
        with open(config_path, "x") as f:
            json.dump({
                    "selected_profile": "default",
                    "profiles": {}
                }, f, indent=2)
    except:
        logger.fatal(f'Could not create default config {config_path}')
        exit()


# Get launcher profiles file
launcher_profiles_path = Path(root).joinpath('launcher_profiles.json')

if not launcher_profiles_path.is_file():
    logger.fatal(f'"{launcher_profiles_path}" does not exist')
    exit()

launcher_profiles_old_path = Path(root).joinpath('launcher_profiles.json_old')
with open(launcher_profiles_path, 'r') as f:
    with open(launcher_profiles_old_path, 'w+') as old:
        old.write(f.read())

# Change mod profiles
def move_jars(src: Path, dest: Path, contents: list[str]):
    if len(contents) == 0:
        logger.info(f'"{src}" is empty')
        return
    for mod in contents:
        src_path = src.joinpath(mod).absolute()
        name = src_path.name
        if src_path.is_file():
            if name.endswith(".jar"):
                dest_path = dest.joinpath(name)
                logging.debug(f'Attempting to move "{src_path}" to "{dest_path}"')  
                try:
                    shutil.move(src_path, dest_path)
                    logging.info(f'Moved "{name}" to "{dest}"')
                except:
                    logging.error(f'Could not move "{name}" to "{dest}"')
            else:
                logging.info(f'"{name}" is not a .jar file, ignoring')
        else:
            logging.debug(f'"{name}" is a directory, ignoring')

def load_profile(profile: str, contents: list[str]):
    # Move all .jar files from profile directory to mods directory and update selected_profile
    logger.info(f'Loading "{profile}"')
    profile_dir = mods_dir.joinpath(profile)
    move_jars(profile_dir, mods_dir, contents)
    # Update selected profile
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            config['selected_profile'] = profile
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            logger.info('Updated selected profile')
    except:
        logger.fatal('Could not update selected profile')
        raise IOError

def unload_profile(profile: str, contents: list[str]):
    # Move all .jar files from mods directory to profile directory
    logger.info(f'Unloading "{profile}"')
    profile_dir = mods_dir.joinpath(profile)
    if not profile_dir.is_dir():
        logger.info(f'"{profile_dir}" does not exist, attempting to create')
        try:
            os.mkdir(profile_dir)
        except IOError:
            logger.error(f'Could not create "{profile_dir}"')
            raise IOError
    move_jars(mods_dir, profile_dir, contents)

def launch(profile_name: str):
    logger.info(f'Minecraft profile launched: "{profile_name}"')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except:
        logger.error('Could not get config')
        return
    selected_profile = config['selected_profile']
    logger.info(f'Previous profile: "{selected_profile}"')
    profiles = config['profiles']
    new_profile = "default"
    for pattern in profiles:
        logger.debug(f'Matching "{profile_name}" against "{pattern}"')
        match = re.match(pattern, profile_name)
        if match:
            profile = profiles[pattern]
            logger.info(f'Found match against "{pattern}" for profile "{profile}"')
            new_profile = profile
            break
    logger.info(f'Mods profile being launched is "{new_profile}"')
    if new_profile == selected_profile:
        logger.info('Profile is already loaded, doing nothing')
        return
    if not mods_dir.joinpath(new_profile).is_dir():
        logging.error(f'"{new_profile}" does not exist, unable to load')
        return
    try:
        mods_to_unload = os.listdir(Path(mods_dir))
        mods_to_load = os.listdir(Path(mods_dir).joinpath(new_profile))
        unload_profile(selected_profile, mods_to_unload)
        load_profile(new_profile, mods_to_load)
    except IOError:
        pass
    return

# Watchdog
class EventHandler(FileSystemEventHandler):
    def on_modified(self, event: FileModifiedEvent):
        logger.debug(f'Modified: {event.src_path}')
        if not event.is_directory and Path(event.src_path) == launcher_profiles_path:
            with open(launcher_profiles_path, 'r') as f:
                text = f.read()
            with open(launcher_profiles_old_path, 'r') as f:
                if f.read() == text:
                    logger.debug('Launcher profiles file content has not changed')
                    return
            logger.info('Launch profiles file has been modified')
            logger.debug(f'Updating "{launcher_profiles_old_path}"')
            with open(launcher_profiles_old_path, 'w') as f:
                f.write(text)
            profiles = json.loads(text)['profiles']
            logger.info('Finding latest profile')
            def parse_time(last_used: str) -> int:
                logging.debug(f'Parsing lastUsed time "{last_used}"')
                lengths = [4, 2, 2, 2, 2, 2, 3]
                params = [int(last_used[sum(lengths[:i])+i:sum(lengths[:i+1])+i]) for i in range(len(lengths))]
                logging.debug(f'Extracted params "{params}"')
                params[6] *= 1000
                dt = datetime(*params)
                if dt == datetime(1970, 1, 1, 0, 0, 0, 0):
                    logging.debug(f'Profile has never been launched')
                    return 0
                timestamp = int(time.mktime(dt.timetuple()))
                logging.debug(f'"{last_used}" as a unix timestamp is {timestamp}')
                return timestamp
            # Find latest profile
            latest_profile: str|None = None
            latest_time = 0.0
            for profile in profiles:
                if 'gameDir' in profiles[profile]:
                    logging.debug(f'"{profile}" is not in the default directory, ignoring')
                    continue
                logging.debug(f'Checking lastUsed time for {profile}')
                last_used = parse_time(profiles[profile]["lastUsed"])
                if last_used == latest_time:
                    logging.error(f'Profiles "{latest_profile}" and "{profile}" have the same lastUsed time')
                    return
                if last_used > latest_time:
                    latest_profile = profile
                    latest_time = parse_time(profiles[profile]["lastUsed"])
            if latest_profile == None:
                logging.error("Could not find the latest profile")
                return
            logging.info(f'Found latest profile "{latest_profile}" AKA "{profiles[latest_profile]["name"]}"')
            launch(profiles[latest_profile]["name"])

event_handler = EventHandler()
observer = Observer()
observer.schedule(event_handler, root, recursive=False)
logger.info(f'Starting watch of launcher profiles at "{launcher_profiles_path}"')
observer.start()

try:
    while True:
        time.sleep(1)
except BaseException as e:
    logging.fatal(e)
finally:
    ctypes.windll.user32.MessageBoxW(0, "Mod switcher has stopped.", Path(__file__).name, 16)
    observer.stop()
    observer.join()