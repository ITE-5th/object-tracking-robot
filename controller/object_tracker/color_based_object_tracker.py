import cv2
import numpy as np

from controller.object_tracker.object_tracker import ObjectTracker


class ColorBasedObjectTracker(ObjectTracker):

    def __init__(self, video_url=0, buffer_size=64, color_lower=(29, 86, 6), color_upper= (64, 255, 255)) -> None:
        super().__init__(video_url, buffer_size)
        self.color_lower = color_lower
        self.color_upper = color_upper

    def _track(self, camera):

        # grab the current frame
        (grabbed, frame) = camera.read()

        # if we are viewing a video and we did not grab a frame,
        # then we have reached the end of the video
        if self.url is None and not grabbed:
            return False

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
        center = None
        radius = None
        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # only proceed if the radius meets a minimum size
            if radius > 10:
                values = "x ={} ,y = {}, r = {} ".format(int(x), int(y), round(radius, 2))
                cv2.putText(frame, values, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1000)

                # draw the circle and centroid on the frame,
                # then update the list of tracked points

                cv2.circle(frame, (int(x), int(y)), int(radius),
                           (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)

        # update the points queue
        self.positions.appendleft([center, radius])

        # loop over the set of tracked points
        for i in range(1, len(self.positions)):
            # if either of the tracked points are None, ignore
            # them
            if self.positions[i - 1] is None or self.positions[i] is None:
                continue

            # otherwise, compqute the thickness of the line and
            # draw the connecting lines
            thickness = int(np.sqrt(self.buffer_size / float(i + 1)) * 2.5)
            cv2.line(frame, self.positions[i - 1][0], self.positions[i][0], (0, 0, 255), thickness)

        # show the frame to our screen
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            return False
        return True
