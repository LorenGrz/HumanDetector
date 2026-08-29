import asyncio
import base64
import dataclasses
import logging
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

AUTO_PASS_SECONDS = 10.0
REJECTION_SCAN_SECONDS = 10.0


def _decode_frame(data_url: str) -> np.ndarray | None:
    try:
        b64_data = data_url.split(",", 1)[1] if "," in data_url else data_url
        raw = base64.b64decode(b64_data)
        array = np.frombuffer(raw, dtype=np.uint8)
        return cv2.imdecode(array, cv2.IMREAD_COLOR)
    except (ValueError, IndexError):
        return None


async def _receive_frame(websocket: WebSocket) -> np.ndarray | None:
    message = await websocket.receive_json()
    if message.get("type") != "frame":
        return None
    return _decode_frame(message.get("data", ""))


async def _send(websocket: WebSocket, result: StepResult) -> None:
    await websocket.send_json(dataclasses.asdict(result))


async def _send_landmarks(websocket: WebSocket, signals: FrameSignals) -> None:
    await websocket.send_json({"kind": "landmarks", "points": signals.mesh_points})


async def _scan_for(websocket: WebSocket, detector: FaceGestureDetector, seconds: float) -> None:
    """Sigue leyendo frames y mandando landmarks durante una pausa teatral."""
    deadline = time.monotonic() + seconds
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return
        try:
            frame = await asyncio.wait_for(_receive_frame(websocket), timeout=remaining)
        except asyncio.TimeoutError:
            return
        if frame is None:
            continue
        signals = detector.analyze(frame)
        if signals is not None:
            await _send_landmarks(websocket, signals)


async def _run_real_step(
    websocket: WebSocket, session: ChallengeSession, detector: FaceGestureDetector, kind: str
) -> None:
    while True:
        frame = await _receive_frame(websocket)
        if frame is None:
            continue
        signals = detector.analyze(frame)
        if signals is None:
            continue
        await _send_landmarks(websocket, signals)

        result = (
            session.submit_blink_count(signals.blink_count)
            if kind == "blink"
            else session.submit_yaw(signals.yaw)
        )
        if result:
            await _send(websocket, result)
            return


@app.websocket("/ws/verify")
async def verify(websocket: WebSocket) -> None:
    await websocket.accept()
    session = ChallengeSession()
    detector = FaceGestureDetector()

    try:
        await websocket.send_json({"kind": "topology", "connections": MESH_CONNECTIONS})
        await _send(websocket, session.instruction())

        while session.step <= TOTAL_STEPS:
            spec = session.current_spec()

            if spec.kind in ("blink", "yaw_left", "yaw_right"):
                await _run_real_step(websocket, session, detector, spec.kind)
            elif spec.kind == "auto_pass":
                await _scan_for(websocket, detector, AUTO_PASS_SECONDS)
                await _send(websocket, session.auto_pass())
            else:
                await _scan_for(websocket, detector, REJECTION_SCAN_SECONDS)
                result = session.reject()
                await _send(websocket, result)
                if result.kind == "reveal":
                    return

            if session.step <= TOTAL_STEPS:
                await _send(websocket, session.instruction())

    except WebSocketDisconnect:
        logger.info("client disconnected")
    finally:
        detector.close()
