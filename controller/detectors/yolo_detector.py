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

    def _detect(self, image):

        draw_img, bboxes = self._detect_all(image)
        bboxes = [box for box in bboxes if
                  self.selected_classes and
                  box[5] in self.selected_classes and box[4] >= self.threshold]

        if len(bboxes) < 1:
            return image, [0, 0, 0, 0, self.NO_OBJECT]

        box = sorted(bboxes, key=lambda x: x[5])[0]

        height, width, _ = draw_img.shape
        x1, y1, x2, y2, prop, name = box
        x, y, width, height = (x1 + x2) // 2, (y1 + y2) // 2, abs(x2 - x1) // 2, abs(y2 - y1) // 2

        return draw_img, [x, y, width, height, box[5]]

    def _detect_all(self, image):
        width, height = image.shape[1], image.shape[0]
        sized = cv2.resize(image, (self.model.width, self.model.height))
        bboxes = do_detect(self.model, sized, 0.5, 0.4, 1)
        img = cv2.resize(sized, (width, height), interpolation=cv2.INTER_CUBIC)
        draw_img, bboxes = plot_boxes_cv2(img, bboxes, None, self.class_names, None, self.selected_classes)

        return draw_img, bboxes

    def set_classes(self, classes):
        self.selected_classes = classes
