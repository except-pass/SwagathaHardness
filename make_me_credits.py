import logging
from dataclasses import dataclass
import ctypes   # screen info.
import time     # For pause
import datetime # for timestamps
import subprocess #to open and close the client
import mouse    # mouse, duh
import yaml
import shutil
import pathlib

logger = logging.getLogger()

class SnapClient:
    def __init__(self, executable):
        self.executable = executable
        self.process = None
    def start(self):
        logger.info("Starting Snap Client")
        self.process = subprocess.Popen(self.executable)
    def stop(self):
        logger.info("Stopping Snap Client")
        try:
            self.process.terminate()
        except AttributeError:
            logger.error("Snap was not started by this program.")

@dataclass
class Location:
    x: float
    y: float
    
    def __mul__(self, location):
        x = self.x*location.x
        y = self.y*location.y
        #return an instance of whatever class this is
        #useful if you later inherit from this
        return self.__class__(x=x, y=y)

@dataclass
class Button(Location):
    pause: float=0
    def click(self, screensize:Location, pause=None):
        '''
            Moves the mouse to the x,y Location of this button, 
            then clicks the mouse.
            Optionally, will sleep after the click.  The default
            pause length is the self.pause
        '''
        logger.debug("Clicking {}".format(self))
        loc = self * screensize
        mouse.move(loc.x, loc.y)
        mouse.click()

        pause = self.pause if pause is None else pause
        if pause:
            time.sleep(pause)


def get_users_screensize():
    user32 = ctypes.windll.user32
    screensize_x = user32.GetSystemMetrics(0)
    screensize_y = user32.GetSystemMetrics(1)
    return Location(screensize_x, screensize_y)

@dataclass
class Screen:
    play: Button=Button
    endturn: Button=Button
    next: Button=Button
    size: Location=get_users_screensize()

class Agatha:
    def __init__(self, configs=None, counter=0, end_at=None, start_client=True):
        self.counter = counter
        self.end_at = 1e12 if end_at is None else end_at
        self.configs = configs or {}
        logger.info("Loading configs {}".format(self.configs))
        self.screen = self.make_screen()

        self.client = None
        if start_client:
            self.client = SnapClient(executable=self.configs['executable'])
            self.client.start()

    def make_screen(self):
        button_defs = self.configs['buttons']
        return Screen(
                play = Button(**button_defs['play']),
                endturn = Button(**button_defs['endturn']),
                next = Button(**button_defs['next']),
                )

    def get_function_configs(self, function_name):
        return self.configs['commands'].get(function_name, {})

    def play_super_good(self):
        '''
        Run a series of clicks, then pause for "cycle_end_pause" seconds at the end
        '''
        function_configs = self.get_function_configs('play_super_good')
        cycle_end_pause = function_configs.get('cycle_end_pause', 2)

        self.screen.endturn.click(screensize=self.screen.size)
        self.screen.next.click(screensize=self.screen.size)
        self.screen.play.click(screensize=self.screen.size)

        time.sleep(cycle_end_pause)

    def save_state_files(self):
        configs = self.get_function_configs('save_state_files')
        save_every = configs.get('save_every')
        fpath = configs.get('path_to_log_files')   

        if save_every is None:
            return None

        if self.counter % save_every == 0 :
            logfiles = pathlib.Path(fpath).expanduser()
            dest = gamestates_dest_directory()
            logger.info("Saving the log files to {}".format(dest))
            shutil.copytree(logfiles, dest)

    def restart_snap(self):
        function_configs = self.get_function_configs('restart_snap')
        restart_every = function_configs.get('restart_every')
        if restart_every is None:
            return None
        if self.client is None:
            return None

        if self.counter % restart_every == 0:
            logger.info("Restarting the SNAP client")
            self.client.stop()
            time.sleep(3)
            self.client.start()

    def get_me_credits(self):
        while self.counter < self.end_at:
            self.counter += 1
            logger.info("Playing cycle {}".format(self.counter))

            self.restart_snap()
            self.play_super_good()
            self.save_state_files()

def load_config_file(config_fpath):
    with open(config_fpath, 'r') as f:
        return yaml.safe_load(f)

def gamestates_dest_directory():
    try: 
        this = pathlib.Path(__file__).parent.resolve()
    except NameError:
        #in a notebook
        this = globals()['_dh'][0]

    now = int(time.time())
    dest = this.joinpath('gamestates', str(now))
    return dest

if __name__ == '__main__':
    import argparse
    logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')        
    logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(
                    prog = 'Agatha Bot',
                    description = 'Plays more Marvel Snap than is humanly possible',
                    )

    parser.add_argument("configs", type=str, help="Filepath to yaml config file")
    parser.add_argument("-n", type=int, help="Number of cycles to run before quitting.  Default: never stop", default=None)
    parser.add_argument("--no_start_client", action='store_true', default=False)
    parser.add_argument('--testing_mode', action='store_true', default=False, help="Start in a testing mode with a debug terminal")
    args = parser.parse_args()
    configs = load_config_file(args.configs)

    my_girlfriend = Agatha(configs=configs, start_client=(not args.no_start_client))
    aga = my_girlfriend #shorter typing for testing mode
    if not args.testing_mode:
        my_girlfriend.get_me_credits()
    
