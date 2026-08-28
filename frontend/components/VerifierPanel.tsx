import { CameraFeed } from "./CameraFeed";

const TOTAL_STEPS = 5;

interface VerifierPanelProps {
  step: number;
  instruction: string;
  lastResult: { passed: boolean; message: string } | null;
  onFrame: (base64Jpeg: string) => void;
}

export function VerifierPanel({ step, instruction, lastResult, onFrame }: VerifierPanelProps) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-between px-6 py-8">
      <header className="flex w-full max-w-sm items-center justify-between font-mono text-xs tracking-widest text-accent">
        <span>HUMAN PROTOCOL</span>
        <span className="text-muted">
          {String(step).padStart(2, "0")}/{TOTAL_STEPS}
        </span>
      </header>

      <div className="flex flex-1 flex-col items-center justify-center gap-6">
        <p className="text-center text-xl font-semibold">{instruction}</p>
        <CameraFeed active onFrame={onFrame} />
        <StatusLine result={lastResult} />
        <ProgressDots step={step} total={TOTAL_STEPS} />
      </div>

      <footer className="flex w-full max-w-sm justify-between font-mono text-[10px] tracking-widest text-muted">
        <span>v4.02 // ALGORITHMIC_GOVERNANCE_SYSTEM</span>
        <span>PROTOCOL_ISO_9001</span>
      </footer>
    </div>
  );
}

function StatusLine({ result }: { result: { passed: boolean; message: string } | null }) {
  if (!result) {
    return <p className="font-mono text-xs tracking-widest text-accent">ESCANEANDO...</p>;
  }
  return (
    <p
      className={`max-w-sm text-center font-mono text-xs tracking-widest ${
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
    <div className="flex gap-2">
      {Array.from({ length: total }, (_, i) => i + 1).map((dot) => (
        <span
          key={dot}
          className={`h-1.5 w-1.5 rounded-full ${dot <= step ? "bg-accent" : "bg-muted/30"}`}
        />
      ))}
    </div>
  );
}
