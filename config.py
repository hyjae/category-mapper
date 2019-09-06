import os
import yaml
import logging


class ConfigManager(object):
    """Singleton pattern YAML config loader"""

    DEFAULT_CONFIG_FILE = 'C:/Developer/yjhnnn/cat-mapper/config.yml'

    _instance = None
    logger = logging.getLogger(__name__)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        config_file = self._get_config_file()
        if not os.path.isfile(config_file):
            raise FileNotFoundError('%s does not exist!' % config_file)
        with open(config_file, 'r') as r:
            self.config = yaml.load(r)

    def _get_config_file(self):
        return os.environ.get('CONFIG_FILE', self.DEFAULT_CONFIG_FILE)

    def get_setting(self, key):
        if key not in self.config.keys():
            raise KeyError('%s does not exist!' % key)
        return self.config[key]