export type ServerMessage =
  | { kind: "instruction"; step: number; text: string; passed: null; message: null }
  | { kind: "result"; step: number; text: null; passed: boolean; message: string }
  | { kind: "reveal"; step: null; text: string; passed: null; message: null };

export interface FrameMessage {
  type: "frame";
  data: string;
}

export type VerifierPhase = "connecting" | "verifying" | "reveal" | "disconnected";

export interface VerifierState {
  phase: VerifierPhase;
  step: number | null;
  instruction: string | null;
  lastResult: { passed: boolean; message: string } | null;
  revealText: string | null;
}
