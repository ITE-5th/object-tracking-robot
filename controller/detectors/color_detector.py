import cv2

from controller.detectors.detector import ObjectDetector


class ColorObjectDetector(ObjectDetector):

    def _detect_all(self, image):
        frame = image

        # resize the frame, blur it, and convert it to the HSV
        # color space
        # frame = imutils.resize(frame, width=600)
        # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # construct a mask for the color "green", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, self.color_lower, self.color_upper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)[-2]
        if len(cnts) < 1:
            return None, [0, 0, 0, 0, self.NO_OBJECT]

        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        if radius < 15:
            return None, [0, 0, 0, 0, self.NO_OBJECT]

        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        cv2.circle(frame, (int(x), int(y)), int(radius),
                   (0, 255, 255), 2)
        cv2.circle(frame, center, 5, (0, 0, 255), -1)

        return image, [center[0], center[1], radius, radius, "Colored"]

    def __init__(self, color_lower=(29, 86, 6), color_upper=(64, 255, 255)) -> None:
        super().__init__()
        self.color_lower = color_lower
        self.color_upper = color_upper

    def _detect(self, image):
        return self._detect_all(image)[1]


    def get_default_color(self):
        return self.color_lower