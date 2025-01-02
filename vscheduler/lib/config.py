import yaml

class Config:
    def __init__(self, config_file):
        self.file = config_file
        self.loadConfigs()
        self.parseConfigs()
        
    def loadConfigs(self):
        with open(self.file, 'r') as file:
            self.config = yaml.safe_load(file)
        print (self.config)
        print (self)
        
    def parseConfigs(self):
        self.database = self.config['database']
        self.ssh = self.config['ssh']
        self.time = self.config['time']
        self.partition = self.config['partition']
        self.email = self.config['email']
        self.log = self.config['log']
        self.load = self.config['load']
        self.asyncs = self.config['async']
        
config = Config("config.yml")