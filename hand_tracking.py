"""Webcam hand tracking (OpenCV + MediaPipe) running in a QThread.
Gestures:  point (index only) -> rotate camera | open palm -> thumb-index spread sets distance L
           fist held ~1.2 s -> record reading
"""
import cv2
import numpy as np
import mediapipe as mp
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage


def classify(lm):
    up = lambda tip, pip: lm[tip].y < lm[pip].y
    f = [up(8, 6), up(12, 10), up(16, 14), up(20, 18)]
    palm = np.hypot(lm[0].x - lm[9].x, lm[0].y - lm[9].y) + 1e-6
    spread = np.hypot(lm[4].x - lm[8].x, lm[4].y - lm[8].y) / palm
    if all(f):
        name = "open"
    elif f == [True, False, False, False]:
        name = "point"
    elif not any(f):
        name = "fist"
    else:
        name = "other"
    return name, lm[8].x, lm[8].y, float(spread)


class HandTracker(QThread):
    frame_ready = Signal(QImage)
    gesture = Signal(str, float, float, float)
    error = Signal(str)

    def __init__(self, cam=0):
        super().__init__()
        self.cam, self._run = cam, True

    def stop(self):
        self._run = False
        self.wait(3000)

    def run(self):
        cap = cv2.VideoCapture(self.cam, cv2.CAP_DSHOW)
        if not cap.isOpened():
            self.error.emit("Cannot open webcam")
            return
        hands = mp.solutions.hands.Hands(max_num_hands=1, model_complexity=0,
                                         min_detection_confidence=0.6, min_tracking_confidence=0.5)
        draw = mp.solutions.drawing_utils
        while self._run:
            ok, frame = cap.read()
            if not ok:
                continue
            frame = cv2.flip(frame, 1)
            res = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            g, x, y, s = "none", 0.0, 0.0, 0.0
            if res.multi_hand_landmarks:
                lm = res.multi_hand_landmarks[0]
                draw.draw_landmarks(frame, lm, mp.solutions.hands.HAND_CONNECTIONS)
                g, x, y, s = classify(lm.landmark)
            cv2.putText(frame, g, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, _ = rgb.shape
            img = QImage(rgb.data, w, h, 3 * w, QImage.Format.Format_RGB888).copy()
            self.frame_ready.emit(img.scaled(320, 240))
            self.gesture.emit(g, x, y, s)
        cap.release()
        hands.close()
