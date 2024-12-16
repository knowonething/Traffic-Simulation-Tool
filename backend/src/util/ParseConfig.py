import json
import copy


class Config:
    """
    config file info
    Characteristic: Proportion | Simulation
    """
    def __init__(self, filepath: str):
        self.filepath = filepath
        if filepath is not None:
            file = open(filepath)
            self.config_info = json.load(file)
            file.close()
        else:
            self.config_info = None

    def get_info(self):
        if self.config_info is None:
            return None
        return copy.deepcopy(self.config_info)

    def set_info(self, config_info: dict):
        if self.config_info is None:
            return
        file = open(self.filepath)
        json.dump(config_info, file)
        file.close()
        self.config_info = copy.deepcopy(config_info)
