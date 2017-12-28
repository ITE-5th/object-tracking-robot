import json

from file_path_manager import FilePathManager


class ConfigReader:
    @staticmethod
    def get(key):
        with open(FilePathManager.resolve("config.json")) as f:
            content = json.load(f)
        return content[key]
