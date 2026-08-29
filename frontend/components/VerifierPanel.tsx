import { CameraFeed } from "./CameraFeed";
import { Countdown } from "./Countdown";
import { SuspicionLog } from "./SuspicionLog";
import { MuteButton } from "./MuteButton";
import type { SuspicionEntry } from "@/types/protocol";

const TOTAL_STEPS = 10;

interface VerifierPanelProps {
  step: number;
  instruction: string;
  instructionDuration: number | null;
  lastResult: { passed: boolean; message: string } | null;
  suspicionLog: SuspicionEntry[];
  onFrame: (base64Jpeg: string) => void;
  meshPoints: [number, number][] | null;
  meshConnections: [number, number][];
}

export function VerifierPanel({
  step,
  instruction,
  instructionDuration,
  lastResult,
  suspicionLog,
  onFrame,
  meshPoints,
  meshConnections,
}: VerifierPanelProps) {
  return (
    <div className="flex h-screen flex-col items-center gap-2 overflow-hidden px-4 py-3">
      <header className="flex w-full max-w-sm items-center justify-between font-mono text-xs tracking-widest text-accent">
        <span>HUMAN PROTOCOL</span>
        <div className="flex items-center gap-2">
          <span className="text-muted">
            {String(step).padStart(2, "0")}/{TOTAL_STEPS}
          </span>
          <MuteButton />
        </div>
      </header>

      <div className="flex w-full min-h-0 flex-1 flex-col items-center gap-2 overflow-hidden">
        <div className="flex h-8 shrink-0 items-center justify-center">
          {instructionDuration !== null && (
            <Countdown
              key={`${step}-${instruction}-${instructionDuration}`}
              seconds={instructionDuration}
            />
          )}
        </div>
        <p className="line-clamp-3 min-h-[4.5rem] w-full max-w-sm shrink-0 text-center text-2xl font-bold sm:text-3xl">
          {instruction}
        </p>
        {/* Ocupa todo el espacio vertical que sobra: la cámara se agranda o
            achica sola según cuánto lugar quede, sin porcentajes fijos. */}
        <div className="flex w-full min-h-0 flex-1 items-center justify-center">
          <CameraFeed
            active
            onFrame={onFrame}
            meshPoints={meshPoints}
            meshConnections={meshConnections}
          />
        </div>
        <div className="flex min-h-8 shrink-0 items-center justify-center">
          <StatusLine result={lastResult} />
        </div>
        <ProgressDots step={step} total={TOTAL_STEPS} />
      </div>

      <div className="flex w-full max-w-sm flex-col items-center gap-2">
        <SuspicionLog lines={suspicionLog} />
        <footer className="flex w-full justify-between font-mono text-[0.625rem] tracking-widest text-muted">
          <span>v4.02 // ALGORITHMIC_GOVERNANCE_SYSTEM</span>
          <span>PROTOCOL_ISO_9001</span>
        </footer>
      </div>
    </div>
  );
}

function StatusLine({ result }: { result: { passed: boolean; message: string } | null }) {
  if (!result) {
    return <p className="font-mono text-xs tracking-widest text-accent">ESCANEANDO...</p>;
  }
  return (
    <p
      className={`line-clamp-2 max-w-sm text-center font-mono text-xs tracking-widest ${
        result.passed ? "text-accent" : "text-danger"
      }`}
    >
      {result.passed ? "✓ " : "✕ "}
      {result.message}
    </p>
  );
}

function ProgressDots({ step, total }: { step: number; total: number }) {
  return (
    <div className="flex flex-wrap justify-center gap-2">
      {Array.from({ length: total }, (_, i) => i + 1).map((dot) => (
        <span
          key={dot}
          className={`h-1.5 w-1.5 rounded-full ${dot <= step ? "bg-accent" : "bg-muted/30"}`}
        />
      ))}
    </div>
  );
}
