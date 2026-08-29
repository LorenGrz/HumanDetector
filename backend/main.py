import asyncio
import base64
import dataclasses
import logging
import math
import random
import time

import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from challenge import TOTAL_STEPS, ChallengeSession, StepResult
from detector import MESH_CONNECTIONS, FaceGestureDetector, FrameSignals

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verifier")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SUSPICION_INTERVAL_RANGE = (1.6, 2.4)


def _decode_frame(data_url: str) -> np.ndarray | None:
    try:
        b64_data = data_url.split(",", 1)[1] if "," in data_url else data_url
        raw = base64.b64decode(b64_data)
        array = np.frombuffer(raw, dtype=np.uint8)
        return cv2.imdecode(array, cv2.IMREAD_COLOR)
    except (ValueError, IndexError):
        return None


def _motion_energy(
    previous: list[tuple[float, float]], current: list[tuple[float, float]]
) -> float:
    return sum(math.dist(p, c) for p, c in zip(previous, current))


class Sender:
    """Envoltorio del websocket: serializa los envíos (el loop principal y el
    de sospechas escriben en paralelo) y centraliza la lectura de frames."""

    def __init__(self, websocket: WebSocket) -> None:
        self._websocket = websocket
        self._lock = asyncio.Lock()

    async def send(self, payload: dict) -> None:
        async with self._lock:
            await self._websocket.send_json(payload)

    async def send_result(self, result: StepResult) -> None:
        await self.send(dataclasses.asdict(result))

    async def send_landmarks(self, signals: FrameSignals) -> None:
        await self.send({"kind": "landmarks", "points": signals.mesh_points})

    async def receive_frame(self) -> np.ndarray | None:
        message = await self._websocket.receive_json()
        if message.get("type") != "frame":
            return None
        return _decode_frame(message.get("data", ""))


async def _scan_and_measure_motion(
    sender: Sender, detector: FaceGestureDetector, seconds: float
) -> float:
    """Lee frames durante la ventana del intento, manda landmarks en vivo, y
    devuelve la energía de movimiento acumulada (para los pasos contra
    reloj: cuánto se movió la cara mientras duró la cuenta regresiva)."""
    deadline = time.monotonic() + seconds
    previous_points: list[tuple[float, float]] | None = None
    total_motion = 0.0

    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return total_motion
        try:
            frame = await asyncio.wait_for(sender.receive_frame(), timeout=remaining)
        except asyncio.TimeoutError:
            return total_motion
        if frame is None:
            continue
        signals = detector.analyze(frame)
        if signals is None:
            continue
        await sender.send_landmarks(signals)

        if previous_points is not None:
            total_motion += _motion_energy(previous_points, signals.mesh_points)
        previous_points = signals.mesh_points


async def _run_real_step(
    sender: Sender, session: ChallengeSession, detector: FaceGestureDetector, kind: str
) -> None:
    while True:
        frame = await sender.receive_frame()
        if frame is None:
            continue
        signals = detector.analyze(frame)
        if signals is None:
            continue
        await sender.send_landmarks(signals)

        result = (
            session.submit_blink_count(signals.blink_count)
            if kind == "blink"
            else session.submit_yaw(signals.yaw)
        )
        if result:
            await sender.send_result(result)
            return


async def _suspicion_loop(sender: Sender, session: ChallengeSession) -> None:
    """Manda en paralelo lo que 'va sospechando' el sistema, todo el rato."""
    while True:
        await asyncio.sleep(random.uniform(*SUSPICION_INTERVAL_RANGE))
        await sender.send({"kind": "suspicion", "text": session.suspicion_line()})


@app.websocket("/ws/verify")
async def verify(websocket: WebSocket) -> None:
    await websocket.accept()
    session = ChallengeSession()
    detector = FaceGestureDetector()
    sender = Sender(websocket)
    suspicion_task = asyncio.create_task(_suspicion_loop(sender, session))

    try:
        await sender.send({"kind": "topology", "connections": MESH_CONNECTIONS})
        await sender.send_result(session.instruction())

        while session.step <= TOTAL_STEPS:
            spec = session.current_spec()

            if spec.kind in ("blink", "yaw_left", "yaw_right"):
                await _run_real_step(sender, session, detector, spec.kind)
            elif spec.kind == "auto_pass":
                await _scan_and_measure_motion(sender, detector, session.current_duration())
                await sender.send_result(session.auto_pass())
            else:
                motion_score = await _scan_and_measure_motion(
                    sender, detector, session.current_duration()
                )
                result = session.resolve_reject(motion_score)
                await sender.send_result(result)
                if result.kind in ("reveal", "confirmed"):
                    return

            if session.step <= TOTAL_STEPS:
                await sender.send_result(session.instruction())

    except WebSocketDisconnect:
        logger.info("client disconnected")
    finally:
        suspicion_task.cancel()
        detector.close()
