import { CameraFeed } from "./CameraFeed";
import { Countdown } from "./Countdown";
import { SuspicionLog } from "./SuspicionLog";

const TOTAL_STEPS = 10;

interface VerifierPanelProps {
  step: number;
  instruction: string;
  instructionDuration: number | null;
  lastResult: { passed: boolean; message: string } | null;
  suspicionLog: string[];
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
    <div className="flex min-h-screen flex-col items-center gap-4 overflow-y-auto px-6 py-8">
      <header className="flex w-full max-w-sm items-center justify-between font-mono text-xs tracking-widest text-accent">
        <span>HUMAN PROTOCOL</span>
        <span className="text-muted">
          {String(step).padStart(2, "0")}/{TOTAL_STEPS}
        </span>
      </header>

      <div className="flex w-full max-w-sm flex-1 flex-col items-center gap-3">
        <div className="flex h-9 items-center justify-center">
          {instructionDuration !== null && (
            <Countdown
              key={`${step}-${instruction}-${instructionDuration}`}
              seconds={instructionDuration}
            />
          )}
        </div>
        <p className="line-clamp-2 min-h-14 text-center text-xl font-semibold">{instruction}</p>
        <CameraFeed
          active
          onFrame={onFrame}
          meshPoints={meshPoints}
          meshConnections={meshConnections}
        />
        <div className="flex min-h-10 items-center justify-center">
          <StatusLine result={lastResult} />
        </div>
        <ProgressDots step={step} total={TOTAL_STEPS} />
      </div>

      <div className="flex w-full max-w-sm flex-col items-center gap-3">
        <SuspicionLog lines={suspicionLog} />
        <footer className="flex w-full justify-between font-mono text-[10px] tracking-widest text-muted">
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
