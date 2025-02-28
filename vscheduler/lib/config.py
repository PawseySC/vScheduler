import os, yaml

# class Config:
#     with open(os.path.join(os.path.dirname(__file__), '.', 'config.yml'), 'r') as file:
#         config = yaml.safe_load(file)

class Config:
    """Singleton class to load and access configuration from a YAML file"""
    _instance = None
    _config = None

    def __new__(cls, config_file=os.path.join(os.path.dirname(__file__), 'config.yml')):
        # Ensure that only one instance of the Singleton is created
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            # Load the YAML configuration file only once
            cls._instance.load_config(cls, config_file)
        return cls._instance

    def load_config(self, cls, config_file):
        """Load configuration from a YAML file"""
        with open(config_file, "r") as file:
            cls._config = yaml.safe_load(file)

    def get_config(self):
        """Return the loaded configuration in whole"""
        return self._config

    def get(self, key):
        """Get a specific configuration value by key"""
        keys = key.split(".")
        value = self._config
        for k in keys:
            value = value.get(k, None)
            if value is None:
                break
        return value