import cv2

from controller.detectors.detector import ObjectDetector
from controller.detectors.yolo.darknet import Darknet
from controller.detectors.yolo.utils import do_detect, plot_boxes_cv2, load_class_names
from file_path_manager import FilePathManager


class YoloObjectDetector(ObjectDetector):

    def __init__(self, selected_classes=None, threshold=0.5):
        self.model = Darknet(FilePathManager.resolve("cfg/yolo.cfg")).cuda()
        self.model.load_weights(FilePathManager.resolve("models/yolo.weights"))
        if self.model.num_classes == 20:
            names_file = FilePathManager.resolve('data/voc.names')
        elif self.model.num_classes == 80:
            names_file = FilePathManager.resolve('data/coco.names')
        else:
            names_file = 'data/names'
        self.class_names = load_class_names(names_file)
        self.selected_classes = selected_classes
        self.threshold = threshold

    def _detect(self, image, window_width, window_height):

        bboxes, draw_img = self._detect_all(image, window_width, window_height)
        bboxes = [box for box in bboxes if
                  self.selected_classes and self.class_names[
                      box[6] % len(self.class_names)] in self.selected_classes and box[5] >= self.threshold]
        box = sorted(bboxes, key=lambda x: x[5])[0]

        height, width, _ = draw_img.shape
        x1, y1, x2, y2, prop, name = box
        x, y, width, height = (x1 + x2) // 2, (y1 + y2) // 2, abs(x2 - x1) // 2, abs(y2 - y1) // 2

        return x, y, width, height, box[6]

    def _detect_all(self, image, window_width, window_height):
        sized = cv2.resize(image, (self.model.width, self.model.height))
        bboxes = do_detect(self.model, sized, 0.5, 0.4, 1)
        img = cv2.resize(sized, (window_width, window_height), interpolation=cv2.INTER_CUBIC)
        draw_img, bboxes = plot_boxes_cv2(img, bboxes, None, self.class_names)

        return draw_img, bboxes

    def set_classes(self, classes):
        self.selected_classes = classes
