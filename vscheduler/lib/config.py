import os, yaml

class Config:
    with open(os.path.join(os.path.dirname(__file__), '.', 'config.yml'), 'r') as file:
        config = yaml.safe_load(file)
# --------


# class Config:
#     def __init__(self, config_file = os.path.join(os.path.dirname(__file__), '.', 'config.yml')):
#         with open(config_file, 'r') as file:
#             self._config = yaml.safe_load(file)
#         # Load the variables dynamically as class attributes
#         self._load_config()

#     def _load_config(self):
#         for section, values in self._config.items():
#             for key, value in values.items():
#                 # Setting the attribute for each config item as a class variable
#                 setattr(self, f"{section}_{key}", value)

#     def get(self, section, key):
#         """Access individual configuration items."""
#         return getattr(self, f"{section}_{key}", None)


# Usage:
# if __name__ == "__main__":
#     config = Config('config.yaml')
    
#     # Access configuration variables like class attributes
#     print(f"App Name: {config.app_name}")
#     print(f"Database Host: {config.database_host}")
#     print(f"API Base URL: {config.api_base_url}")
    
#     # You can also access using the get method
#     db_host = config.get('database', 'host')
#     print(f"Database Host via get method: {db_host}")


# -------- Singleton
# class Config:
#     _instance = None

#     def __new__(cls, config_file = os.path.join(os.path.dirname(__file__), '.', 'config.yml')):
#         if cls._instance is None:
#             cls._instance = super(Config, cls).__new__(cls)
#             with open(config_file, 'r') as file:
#                 cls._instance._config = yaml.safe_load(file)
#             # Load the variables dynamically as class attributes
#             cls._instance._load_config()

#     def _load_config(self):
#         for section, values in self._config.items():
#             for key, value in values.items():
#                 # Setting the attribute for each config item as a class variable
#                 setattr(self, f"{section}_{key}", value)


# --------
# class Config:
#     def __init__(self, config_file):
#         self.file = config_file
#         self.loadConfigs()
#         self.parseConfigs()
        
#     def loadConfigs(self):
#         with open(self.file, 'r') as file:
#             self.config = yaml.safe_load(file)
    
#     def parseConfigs(self):
#         self.database = self.config['database']
#         self.ssh = self.config['ssh']
#         self.time = self.config['time']
#         self.partition = self.config['partition']
#         self.email = self.config['email']
#         self.log = self.config['log']
#         self.load = self.config['load']
#         self.asyncs = self.config['asyncs']
    
# config = Config(os.path.join(os.path.dirname(__file__), '.', 'config.yml'))