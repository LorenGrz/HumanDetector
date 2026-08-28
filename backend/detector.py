"""Extracción de señales crudas de landmarks faciales (mediapipe Tasks API).

No conoce el guion de la verificación: solo expone parpadeos contados y el
yaw (giro horizontal) estimado. La interpretación de esas señales como
"pasa" o "no pasa" vive en challenge.py.
"""

import math
import time
from pathlib import Path
from typing import Optional

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import FaceLandmarker, FaceLandmarkerOptions, RunningMode

_MODEL_PATH = Path(__file__).parent / "models" / "face_landmarker.task"

_LEFT_EYE = [33, 160, 158, 133, 153, 144]
_RIGHT_EYE = [362, 385, 387, 263, 373, 380]
_NOSE_TIP = 1
_LEFT_EYE_OUTER = 33
_RIGHT_EYE_OUTER = 263

_EAR_CLOSED_THRESHOLD = 0.21


def _eye_aspect_ratio(landmarks, indices: list[int]) -> float:
    p = [landmarks[i] for i in indices]
    vertical_1 = math.dist((p[1].x, p[1].y), (p[5].x, p[5].y))
    vertical_2 = math.dist((p[2].x, p[2].y), (p[4].x, p[4].y))
    horizontal = math.dist((p[0].x, p[0].y), (p[3].x, p[3].y))
    if horizontal == 0:
        return 0.0
    return (vertical_1 + vertical_2) / (2.0 * horizontal)


class FaceGestureDetector:
    def __init__(self) -> None:
        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(_MODEL_PATH)),
            running_mode=RunningMode.VIDEO,
            num_faces=1,
        )
        self._landmarker = FaceLandmarker.create_from_options(options)
        self._start_time = time.monotonic()
        self._last_timestamp_ms = -1
        self._eye_closed = False
        self._blink_count = 0

    def _landmarks(self, frame_bgr: np.ndarray):
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        timestamp_ms = max(
            int((time.monotonic() - self._start_time) * 1000), self._last_timestamp_ms + 1
        )
        self._last_timestamp_ms = timestamp_ms

        result = self._landmarker.detect_for_video(mp_image, timestamp_ms)
        if not result.face_landmarks:
            return None
        return result.face_landmarks[0]

    def count_blinks(self, frame_bgr: np.ndarray) -> int:
        """Cuenta transiciones ojo-abierto -> ojo-cerrado -> ojo-abierto."""
        landmarks = self._landmarks(frame_bgr)
        if landmarks is None:
            return self._blink_count

        ear = (
            _eye_aspect_ratio(landmarks, _LEFT_EYE)
            + _eye_aspect_ratio(landmarks, _RIGHT_EYE)
        ) / 2.0

        if ear < _EAR_CLOSED_THRESHOLD and not self._eye_closed:
            self._eye_closed = True
        elif ear >= _EAR_CLOSED_THRESHOLD and self._eye_closed:
            self._eye_closed = False
            self._blink_count += 1

        return self._blink_count

    def detect_yaw(self, frame_bgr: np.ndarray) -> Optional[float]:
        """Offset horizontal de la nariz relativo al ancho de cara, en [-1, 1].

        La cámara mira de frente al usuario y el frame NO está espejado
        (es el feed crudo de getUserMedia, no el preview con scaleX(-1) que
        ve el usuario). Con esa convención, un yaw positivo corresponde a
        que el usuario giró hacia SU propia izquierda.
        """
        landmarks = self._landmarks(frame_bgr)
        if landmarks is None:
            return None

        nose = landmarks[_NOSE_TIP]
        left = landmarks[_LEFT_EYE_OUTER]
        right = landmarks[_RIGHT_EYE_OUTER]

        face_center_x = (left.x + right.x) / 2.0
        face_width = abs(right.x - left.x)
        if face_width == 0:
            return None

        return (nose.x - face_center_x) / face_width

    def close(self) -> None:
        self._landmarker.close()
