import { MuteButton } from "./MuteButton";

interface WelcomeScreenProps {
  onStart: () => void;
}

export function WelcomeScreen({ onStart }: WelcomeScreenProps) {
  return (
    <div className="flex h-screen flex-col items-center justify-center gap-6 overflow-hidden px-6 text-center">
      <div className="flex w-full max-w-sm items-center justify-center gap-2">
        <span className="font-mono text-xs tracking-widest text-accent">HUMAN PROTOCOL</span>
        <MuteButton />
      </div>
      <h1 className="text-3xl font-bold tracking-wide">¿SOS HUMANO?</h1>
      <p className="max-w-sm text-sm leading-relaxed text-muted">
        Vas a tener que probarlo.
        <br />
        Necesito acceso a tu cámara para empezar.
      </p>
      <button
        onClick={onStart}
        className="rounded-full border border-accent px-8 py-3 font-mono text-xs tracking-widest text-accent transition hover:bg-accent hover:text-background"
      >
        COMENZAR VERIFICACIÓN
      </button>
      <footer className="mt-8 flex w-full max-w-sm justify-between font-mono text-[0.625rem] tracking-widest text-muted">
        <span>v4.02 // ALGORITHMIC_GOVERNANCE_SYSTEM</span>
        <span>PROTOCOL_ISO_9001</span>
      </footer>
    </div>
  );
}
