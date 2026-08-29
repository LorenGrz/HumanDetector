import type { RevealVariant } from "@/types/protocol";
import { RevealSound } from "./RevealSound";

interface RevealScreenProps {
  variant: RevealVariant;
  label: string;
  message: string;
  onRestart: () => void;
}

export function RevealScreen({ variant, label, message, onRestart }: RevealScreenProps) {
  const isConfirmed = variant === "confirmed";
  const toneColor = isConfirmed ? "text-accent" : "text-danger";

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 px-6 text-center">
      <RevealSound variant={variant} />
      <span className="font-mono text-xs tracking-widest text-accent">HUMAN PROTOCOL</span>
      {isConfirmed ? <CheckIcon /> : <WarningIcon />}
      <h1 className={`text-2xl font-bold tracking-wide ${toneColor}`}>{label}</h1>
      <p className="max-w-sm text-sm leading-relaxed text-muted">{message}</p>
      <button
        onClick={onRestart}
        className="rounded-full border border-accent px-6 py-2 font-mono text-xs tracking-widest text-accent transition hover:bg-accent hover:text-background"
      >
        REINICIAR
      </button>
      <footer className="mt-8 flex w-full max-w-sm justify-between font-mono text-[10px] tracking-widest text-muted">
        <span>v4.02 // ALGORITHMIC_GOVERNANCE_SYSTEM</span>
        <span>PROTOCOL_ISO_9001</span>
      </footer>
    </div>
  );
}

function WarningIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-10 w-10 text-danger"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
    >
      <path
        d="M12 9v4m0 4h.01M10.29 3.86l-8.18 14.18A1 1 0 0 0 3 19.5h18a1 1 0 0 0 .89-1.46L13.71 3.86a1 1 0 0 0-1.72 0Z"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-10 w-10 text-accent"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
    >
      <path d="M4.5 12.75l6 6 9-13.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
