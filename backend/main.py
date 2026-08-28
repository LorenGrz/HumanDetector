import asyncio
import base64
import dataclasses
import logging

import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from challenge import ChallengeSession
from detector import FaceGestureDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verifier")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

REJECTION_SCAN_SECONDS = 2.5


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


async def _send(websocket: WebSocket, result) -> None:
    await websocket.send_json(dataclasses.asdict(result))


@app.websocket("/ws/verify")
async def verify(websocket: WebSocket) -> None:
    await websocket.accept()
    session = ChallengeSession()
    detector = FaceGestureDetector()

    try:
        await _send(websocket, session.instruction())

        while session.step == 1:
            frame = await _receive_frame(websocket)
            if frame is None:
                continue
            blinks = detector.count_blinks(frame)
            result = session.submit_blink_count(blinks)
            if result:
                await _send(websocket, result)
                await _send(websocket, session.instruction())

        while session.step == 2:
            frame = await _receive_frame(websocket)
            if frame is None:
                continue
            yaw = detector.detect_yaw(frame)
            if yaw is None:
                continue
            result = session.submit_yaw(yaw)
            if result:
                await _send(websocket, result)
                await _send(websocket, session.instruction())

        while session.step in (3, 4):
            await asyncio.sleep(REJECTION_SCAN_SECONDS)
            result = session.reject_smile()
            await _send(websocket, result)
            if session.step in (3, 4):
                await _send(websocket, session.instruction())

        await _send(websocket, session.instruction())
        while True:
            await asyncio.sleep(REJECTION_SCAN_SECONDS)
            result = session.reject_final()
            await _send(websocket, result)
            if result.kind == "reveal":
                break

    except WebSocketDisconnect:
        logger.info("client disconnected")
    finally:
        detector.close()
