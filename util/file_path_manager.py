from config_reader import ConfigReader


class FilePathManager:
    base_dir = ConfigReader.get("base_dir")
    @staticmethod
    def resolve(path):
        return "{}/{}".format(FilePathManager.base_dir, path)