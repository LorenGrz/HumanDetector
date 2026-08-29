"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { VerifierSocket } from "@/lib/verifierSocket";
import type { MeshState, ServerMessage, VerifierState } from "@/types/protocol";

const WS_URL = process.env.NEXT_PUBLIC_VERIFIER_WS_URL ?? "ws://localhost:8000/ws/verify";
const SUSPICION_LOG_MAX = 3;

const INITIAL_STATE: VerifierState = {
  phase: "connecting",
  step: null,
  instruction: null,
  instructionDuration: null,
  lastResult: null,
  revealVariant: "reject",
  revealLabel: null,
  revealMessage: null,
  suspicionLog: [],
};

const INITIAL_MESH: MeshState = { connections: [], points: null };

function applyMessage(state: VerifierState, message: ServerMessage): VerifierState {
  switch (message.kind) {
    case "instruction":
      return {
        ...state,
        phase: "verifying",
        step: message.step,
        instruction: message.text,
        instructionDuration: message.duration,
        lastResult: null,
      };
    case "result":
      return { ...state, lastResult: { passed: message.passed, message: message.message } };
    case "reveal":
      return {
        ...state,
        phase: "reveal",
        revealVariant: "reject",
        revealLabel: message.text,
        revealMessage: message.message,
      };
    case "confirmed":
      return {
        ...state,
        phase: "reveal",
        revealVariant: "confirmed",
        revealLabel: message.text,
        revealMessage: message.message,
      };
    case "suspicion":
      return {
        ...state,
        suspicionLog: [...state.suspicionLog, message.text].slice(-SUSPICION_LOG_MAX),
      };
    default:
      return state;
  }
}

/** Estado de la sesión de verificación + control del ciclo de vida del socket. */
export function useVerifierSession() {
  const [state, setState] = useState<VerifierState>(INITIAL_STATE);
  const [mesh, setMesh] = useState<MeshState>(INITIAL_MESH);
  const [sessionId, setSessionId] = useState(0);
  const socketRef = useRef<VerifierSocket | null>(null);

  useEffect(() => {
    const socket = new VerifierSocket(WS_URL, {
      onMessage: (message) => {
        if (message.kind === "topology") {
          setMesh((prev) => ({ ...prev, connections: message.connections }));
          return;
        }
        if (message.kind === "landmarks") {
          setMesh((prev) => ({ ...prev, points: message.points }));
          return;
        }
        setState((prev) => applyMessage(prev, message));
      },
      onClose: () =>
        setState((prev) => (prev.phase === "reveal" ? prev : { ...prev, phase: "disconnected" })),
    });
    socketRef.current = socket;

    return () => socket.close();
  }, [sessionId]);

  const sendFrame = useCallback((base64Jpeg: string) => {
    socketRef.current?.sendFrame(base64Jpeg);
  }, []);

  const restart = useCallback(() => {
    setState(INITIAL_STATE);
    setMesh(INITIAL_MESH);
    setSessionId((id) => id + 1);
  }, []);

  return { state, mesh, sendFrame, restart };
}
