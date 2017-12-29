import cv2

from controller.object_tracker.object_tracker import ObjectTracker
from controller.object_tracker.yolo_object_tracker.darknet import Darknet
from controller.object_tracker.yolo_object_tracker.utils import *
from util.file_path_manager import FilePathManager


class YoloObjectTracker(ObjectTracker):

    def __init__(self, video_url=0, buffer_size=64, selected_classes=None):
        super().__init__(video_url, buffer_size)
        if selected_classes is None:
            selected_classes = []
        self.selected_classes = selected_classes
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
        bboxes = do_detect(self.model, sized, 0.5, 0.4, 1)
        draw_img = plot_boxes_cv2(frame, bboxes, None, self.class_names)
        self.add_to_positions(bboxes, frame)
        print(self.positions)
        cv2.imshow("Image", draw_img)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            return False
        return True

    def add_to_positions(self, bboxes, img):
        height, width, _ = img.shape
        for box in bboxes:
            x1 = int(round((box[0] - box[2] / 2.0) * width))
            y1 = int(round((box[1] - box[3] / 2.0) * height))
            x2 = int(round((box[0] + box[2] / 2.0) * width))
            y2 = int(round((box[1] + box[3] / 2.0) * height))
            x, y, width, height = (x1 + x2) // 2, (y1 + y2) // 2, abs(x2 - x1) // 2, abs(y2 - y1) // 2
            # unused
            prop = box[5]
            index = box[6]
            name = self.class_names[index % len(self.class_names)]
            if len(self.selected_classes) == 0 or name in self.selected_classes:
                self.positions.appendleft((x, y, width, height, name))


if __name__ == '__main__':
    tracker = YoloObjectTracker()
    tracker.track()
