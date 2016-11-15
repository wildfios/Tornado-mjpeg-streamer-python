#!/usr/bin/env python
import cv2


class UsbCamera(object):

    """ Init camera """
    def __init__(self):
        # select first video device in system
        self.cam = cv2.VideoCapture(-1)
        # set camera resolution
        self.w = 800
        self.h = 600
        # set crop factor
        self.cam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, self.h)
        self.cam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, self.w)
        # load cascade file
        self.face_cascade = cv2.CascadeClassifier('face.xml')

    def set_resolution(self, new_w, new_h):
        """
        functionality: Change camera resolution
        inputs: new_w, new_h - with and height of picture, must be int
        returns: None ore raise exception
        """
        if isinstance(new_h, int) and isinstance(new_w, int):
            # check if args are int and correct
            if (new_w <= 800) and (new_h <= 600) and \
               (new_w > 0) and (new_h > 0):
                self.h = new_h
                self.w = new_w
            else:
                # bad params
                raise Exception('Bad resolution')
        else:
            # bad params
            raise Exception('Not int value')

    def get_frame(self):
        """
        functionality: Gets frame from camera
        :return: byte array of jpeg encoded camera frame
        """
        # gets camera picture using OpenCV
        success, image = self.cam.read()
        # scale image
        image = cv2.resize(image, (self.w, self.h))
        # encoding picture to jpeg
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tostring()

    def find_face(self):
        success, image = self.cam.read()
        # scale image
        image = cv2.resize(image, (self.w, self.h))
        # resize image for speeding up recognize
        gray = cv2.resize(image, (320, 240))
        # make it grayscale
        gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
        # face cascade detector
        faces = self.face_cascade.detectMultiScale(gray)
        # draw rect on face arias
        scale = float(self.w / 320.0)
        count = 0
        for f in faces:
            font = cv2.FONT_HERSHEY_SIMPLEX
            x, y, z, t = [int(float(v) * scale) for v in f]
            cv2.putText(image, str(x) + ' ' + str(y), (0, (self.h - 10 - 25 * count)), font, 1, (0, 0, 0), 2)
            count += 1
            cv2.rectangle(image, (x, y), (x + z, y + t), (255, 255, 255), 2)

        # encoding picture to jpeg
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tostring()
