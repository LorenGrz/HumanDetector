"""Extracción de señales crudas de landmarks faciales (mediapipe Tasks API).

No conoce el guion de la verificación: solo expone señales (parpadeos,
yaw, puntos de malla facial). La interpretación de esas señales como
"pasa" o "no pasa" vive en challenge.py.
"""

import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    FaceLandmarker,
    FaceLandmarkerOptions,
    FaceLandmarksConnections,
    RunningMode,
)

_MODEL_PATH = Path(__file__).parent / "models" / "face_landmarker.task"

_LEFT_EYE = [33, 160, 158, 133, 153, 144]
_RIGHT_EYE = [362, 385, 387, 263, 373, 380]
_NOSE_TIP = 1
_LEFT_EYE_OUTER = 33
_RIGHT_EYE_OUTER = 263

_EAR_CLOSED_THRESHOLD = 0.21

# Subset de landmarks usado para la malla visual (contornos: ojos, cejas,
# labios, óvalo de cara, nariz), remapeados a índices compactos 0..N-1 para
# no tener que mandar los 478 landmarks completos por frame.
_CONTOUR_CONNECTIONS = FaceLandmarksConnections.FACE_LANDMARKS_CONTOURS
_CONTOUR_INDICES = sorted({i for c in _CONTOUR_CONNECTIONS for i in (c.start, c.end)})
_INDEX_MAP = {original: compact for compact, original in enumerate(_CONTOUR_INDICES)}

MESH_CONNECTIONS = [(_INDEX_MAP[c.start], _INDEX_MAP[c.end]) for c in _CONTOUR_CONNECTIONS]


def _eye_aspect_ratio(points: list[tuple[float, float]], indices: list[int]) -> float:
    p = [points[i] for i in indices]
    vertical_1 = math.dist(p[1], p[5])
    vertical_2 = math.dist(p[2], p[4])
    horizontal = math.dist(p[0], p[3])
    if horizontal == 0:
        return 0.0
    return (vertical_1 + vertical_2) / (2.0 * horizontal)


@dataclass
class FrameSignals:
    mesh_points: list[tuple[float, float]]
    yaw: float
    blink_count: int


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

    def analyze(self, frame_bgr: np.ndarray) -> Optional[FrameSignals]:
        """Corre una única inferencia por frame y deriva todas las señales."""
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        timestamp_ms = max(
            int((time.monotonic() - self._start_time) * 1000), self._last_timestamp_ms + 1
        )
        self._last_timestamp_ms = timestamp_ms

        result = self._landmarker.detect_for_video(mp_image, timestamp_ms)
        if not result.face_landmarks:
            return None

        landmarks = result.face_landmarks[0]
        points = [(lm.x, lm.y) for lm in landmarks]

        ear = (
            _eye_aspect_ratio(points, _LEFT_EYE) + _eye_aspect_ratio(points, _RIGHT_EYE)
        ) / 2.0
        if ear < _EAR_CLOSED_THRESHOLD and not self._eye_closed:
            self._eye_closed = True
        elif ear >= _EAR_CLOSED_THRESHOLD and self._eye_closed:
            self._eye_closed = False
            self._blink_count += 1

        # Yaw positivo = usuario girado hacia SU propia izquierda (ver nota
        # de convención de cámara no espejada en challenge.py).
        left = points[_LEFT_EYE_OUTER]
        right = points[_RIGHT_EYE_OUTER]
        face_center_x = (left[0] + right[0]) / 2.0
        face_width = abs(right[0] - left[0])
        yaw = (points[_NOSE_TIP][0] - face_center_x) / face_width if face_width else 0.0

        mesh_points = [points[i] for i in _CONTOUR_INDICES]

        return FrameSignals(mesh_points=mesh_points, yaw=yaw, blink_count=self._blink_count)

    def close(self) -> None:
        self._landmarker.close()
