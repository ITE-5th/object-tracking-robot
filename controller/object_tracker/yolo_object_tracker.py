import os
import cv2
from config_reader import ConfigReader
from controller.object_tracker.object_tracker import ObjectTracker
from file_path_manager import FilePathManager

darknet_base_dir = ConfigReader.get("darknet_base_dir")


class YoloObjectTracker(ObjectTracker):
    def __init__(self, video_url=0, buffer_size=64, selected_classes=None):
        super().__init__(video_url, buffer_size)
        if selected_classes is None:
            selected_classes = ["sports ball"]
        self.selected_classes = selected_classes
        self.temp_path = FilePathManager.resolve("temp.jpg")
        self.command = "./darknet detect cfg/yolo.cfg yolo.weights {1}".format(darknet_base_dir,
                                                                                          self.temp_path)

    def _track(self, camera) -> bool:
        (grabbed, frame) = camera.read()
        if self.url is None and not grabbed:
            return False
        cv2.imwrite(self.temp_path, frame)
        os.system("cd {};{}".format(darknet_base_dir, self.command))
        prediction = self.read_prediction()
        if prediction is None:
            return True
        self.positions.appendleft(prediction)
        (x, y), radius = prediction
        cv2.rectangle(frame, (x - radius, y - radius), (x + radius, y + radius), (255, 0, 0), 2)
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            return False
        return True

    def read_prediction(self):
        with open("{}/prediction_details.txt".format(darknet_base_dir)) as f:
            for line in f:
                temp = line.split("_")
                left, right, top, bottom, classes = int(temp[0]), int(temp[1]), int(temp[2]), int(temp[3]), temp[4]
                contain_class = False
                for clz in self.selected_classes:
                    if clz in classes:
                        contain_class = True
                if not contain_class:
                    continue
                x = (left + right) // 2
                y = (top + bottom) // 2
                # the correct implementation
                # radius = (left - right) * (top - bottom)
                # wrong impl
                radius = (left - right) // 2
                return (x, y), radius
        return None


if __name__ == '__main__':
    tracker = YoloObjectTracker()
    tracker.track()
