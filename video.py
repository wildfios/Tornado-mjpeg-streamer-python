#!/usr/bin/env python
import cv2


class UsbCamera(object):
    """ Init camera """
    def __init__(self):
        # select first video device in system
        self.cam = cv2.VideoCapture(-1)
        # set camera resolution
        self.cam.set(3, 480)
        self.cam.set(4, 640)

    def set_resolution(self, new_w, new_h):
        """
        functionality: Change camera resolution
        inputs: new_w, new_h - with and height of picture, must be int
        returns: None ore raise exception
        """
        if isinstance(new_h, int) and isinstance(new_w, int):
            # check if args are int
            self.cam.set(3, new_h)
            self.cam.set(4, new_w)
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
        # encoding picture to jpeg
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tostring()
