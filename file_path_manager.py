
class FilePathManager:
    base_dir = "/home/obada/PycharmProjects/object_tracking_robot"
    @staticmethod
    def resolve(path):
        return "{}/{}".format(FilePathManager.base_dir, path)