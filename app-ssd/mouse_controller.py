import cv2


class MouseController:
    def __init__(self):
        self.drawing = False
        self.ix, self.iy = -1, -1
        self.rois = {}

    def setup_roi(self, camera_index, roi):
        self.rois[camera_index] = roi

    def mouse_event(self, event, x, y, flags, param):
        camera_index, frame_shape = param
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.ix, self.iy = x, y

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                xmin = min(self.ix, x) / frame_shape[1]
                xmax = max(self.ix, x) / frame_shape[1]
                ymin = min(self.iy, y) / frame_shape[0]
                ymax = max(self.iy, y) / frame_shape[0]
                self.rois[camera_index] = [ymin, xmin, ymax, xmax]

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            xmin = min(self.ix, x) / frame_shape[1]
            xmax = max(self.ix, x) / frame_shape[1]
            ymin = min(self.iy, y) / frame_shape[0]
            ymax = max(self.iy, y) / frame_shape[0]
            self.rois[camera_index] = [ymin, xmin, ymax, xmax]

    def get_roi(self, camera_index):
        return self.rois.get(camera_index, None)
