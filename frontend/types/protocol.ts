export type ServerMessage =
  | { kind: "instruction"; step: number; text: string; passed: null; message: null; duration: number | null }
  | { kind: "result"; step: number; text: null; passed: boolean; message: string }
  | { kind: "reveal"; step: null; text: string; passed: null; message: string }
  | { kind: "confirmed"; step: null; text: string; passed: null; message: string }
  | { kind: "topology"; connections: [number, number][] }
  | { kind: "landmarks"; points: [number, number][] }
  | { kind: "suspicion"; text: string };

export interface FrameMessage {
  type: "frame";
  data: string;
}

export type VerifierPhase = "connecting" | "verifying" | "reveal" | "disconnected";
export type RevealVariant = "reject" | "confirmed";

export interface VerifierState {
  phase: VerifierPhase;
  step: number | null;
  instruction: string | null;
  instructionDuration: number | null;
  lastResult: { passed: boolean; message: string } | null;
  revealVariant: RevealVariant;
  revealLabel: string | null;
  revealMessage: string | null;
  suspicionLog: string[];
}

export interface MeshState {
  connections: [number, number][];
  points: [number, number][] | null;
}
