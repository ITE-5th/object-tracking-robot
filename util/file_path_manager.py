import json

config = json.load("../config.json")


class FilePathManager:
    base_dir = config["base_dir"]

    @staticmethod
    def resolve(path):
        return "{}/{}".format(FilePathManager.base_dir, path)
