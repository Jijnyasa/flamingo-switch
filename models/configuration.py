import json

class Configuration:

    def __init__(self, config_path=None):
        self.config_path = config_path
        self.components = self.get_components()

    def get_components(self):
        with open(self.config_path) as json_file:
            data = json.load(json_file)
            print (data.keys())

