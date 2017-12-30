import cv2

from controller.object_tracker.yolo_object_tracker.utils import load_class_names, do_detect, plot_boxes_cv2
from file_path_manager import FilePathManager


def detect(model, image, window_width, window_height):
    if model.num_classes == 20:
        namesfile = FilePathManager.resolve('data/voc.names')
    elif model.num_classes == 80:
        namesfile = FilePathManager.resolve('data/coco.names')
    else:
        namesfile = 'data/names'
    class_names = load_class_names(namesfile)

    sized = cv2.resize(image, (model.width, model.height))
    bboxes = do_detect(model, sized, 0.5, 0.4, 1)
    img = cv2.resize(sized, (window_width, window_height), interpolation=cv2.INTER_CUBIC)
    draw_img = plot_boxes_cv2(img, bboxes, None, class_names)
    return draw_img
