import configparser
import io
import os
from pathlib import Path

class AppConfig:
    def __init__(self, moveup_count=2, config_filename="config.ini"):
        self.moveup_count = moveup_count
        self.config_filename = config_filename
        self.config_path = self._get_config_path()
        self.config = configparser.ConfigParser()
        self._load_config()
        
    def get_root_dir(self):
        return Path(self.config_path).parent
    
    def _get_config_path(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        root_dir = Path(current_dir).parents[self.moveup_count - 1]
        return os.path.join(root_dir, self.config_filename)

    def _load_config(self):
        with open(self.config_path, "r") as f:
            config_content = f.read()
        self.config.read_file(io.StringIO(config_content))
    
    def get(self, section, option, full_path=False):
        # NOTE: full_path is used to return the full path of the configuration value(i.e when accessing a resource).
        # Enable(set to True) it if you want to get full path else, you get the value as is.
        if full_path:
            return os.path.join(self.get_root_dir(), self.config.get(section, option))
        return self.config.get(section, option)
    
    def set(self, section, option, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)
        with open(self.config_path, "w") as f:
            self.config.write(f)
    
    def print_config(self):
        for section in self.config.sections():
            print(f"[{section}]")
            for option in self.config.options(section):
                print(f"{option} = {self.config.get(section, option)}")