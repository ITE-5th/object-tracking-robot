import os

import cv2
import lightnet
from lightnet import Image

from controller.object_tracker.object_tracker import ObjectTracker


class YoloObjectTracker(ObjectTracker):
    def __init__(self, video_url=0, buffer_size=64, selected_classes=None, tiny=False):
        super().__init__(video_url, buffer_size)
        if selected_classes is None:
            selected_classes = ["sports ball"]
        self.selected_classes = selected_classes
        self.model = lightnet.load("{}yolo".format("" if not tiny else "tiny-"))

    def _track(self, camera) -> bool:
        (grabbed, frame) = camera.read()
        if self.url is None and not grabbed:
            return False
        h, w, c = frame.shape
        cv2.imwrite("temp.jpg", frame)
        cv2.imshow("image", frame)
        boxes = self.model(Image.load("temp.jpg", w, h, c), thresh=0.5, hier_thresh=0.5, nms=0.45)
        for box in boxes:
            if box[1] in self.selected_classes:
                x, y, width, height = box[3]
                self.positions.appendleft((x, y, width // 2, height // 2, box[1]))
        key = cv2.waitKey(1) & 0xFF
        os.system("rm temp.jpg")
        if key == ord("q"):
            return False
        return True


if __name__ == '__main__':
    tracker = YoloObjectTracker()
    tracker.track()
