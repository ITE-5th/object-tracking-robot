import cv2

from controller.object_tracker.object_tracker import ObjectTracker
from controller.object_tracker.yolo_object_tracker.darknet import Darknet
from controller.object_tracker.yolo_object_tracker.utils import *
from file_path_manager import FilePathManager


class YoloObjectTracker(ObjectTracker):

    def __init__(self, video_url=0, buffer_size=64, threshold=0.5, selected_classes=None):
        super().__init__(video_url, buffer_size)
        if selected_classes is None:
            selected_classes = []
        self.selected_classes = selected_classes
        self.threshold = threshold
        self.model = Darknet(FilePathManager.resolve("cfg/yolo.cfg"))
        self.model.print_network()
        self.model.load_weights(FilePathManager.resolve("models/yolo.weights"))
        if self.model.num_classes == 20:
            namesfile = 'data/voc.names'
        elif self.model.num_classes == 80:
            namesfile = 'data/coco.names'
        else:
            namesfile = 'data/names'
        self.class_names = load_class_names(FilePathManager.resolve(namesfile))
        self.model = self.model.cuda()

    def _track(self, camera) -> bool:
        (grabbed, frame) = camera.read()
        if self.url is None and not grabbed:
            return False
        sized = cv2.resize(frame, (self.model.width, self.model.height))
        bboxes = do_detect(self.model, sized, self.threshold, 0.4, 1)
        bboxes = [box for box in bboxes if
                  self.selected_classes and self.class_names[
                      box[6] % len(self.class_names)] in self.selected_classes and box[5] >= self.threshold]
        draw_img, bboxes = plot_boxes_cv2(frame, bboxes, None, self.class_names)
        self.add_to_positions(bboxes, frame)
        cv2.imshow("Image", draw_img)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            return False
        return True

    def add_to_positions(self, bboxes, img):
        height, width, _ = img.shape
        for box in bboxes:
            x1, y1, x2, y2, prop, name = box
            x, y, width, height = (x1 + x2) // 2, (y1 + y2) // 2, abs(x2 - x1) // 2, abs(y2 - y1) // 2
            self.positions.appendleft((x, y, width, height, name))


if __name__ == '__main__':
    tracker = YoloObjectTracker(selected_classes=["teddy bear"])
    tracker.track()
