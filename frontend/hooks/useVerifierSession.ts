"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { VerifierSocket } from "@/lib/verifierSocket";
import type { MeshState, ServerMessage, VerifierState } from "@/types/protocol";

const WS_URL = process.env.NEXT_PUBLIC_VERIFIER_WS_URL ?? "ws://localhost:8000/ws/verify";

const INITIAL_STATE: VerifierState = {
  phase: "connecting",
  step: null,
  instruction: null,
  lastResult: null,
  revealLabel: null,
  revealMessage: null,
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
        lastResult: null,
      };
    case "result":
      return { ...state, lastResult: { passed: message.passed, message: message.message } };
    case "reveal":
      return {
        ...state,
        phase: "reveal",
        revealLabel: message.text,
        revealMessage: message.message,
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
