import { MuteButton } from "./MuteButton";

interface WelcomeScreenProps {
  onStart: () => void;
}

export function WelcomeScreen({ onStart }: WelcomeScreenProps) {
  return (
    <div className="flex h-screen flex-col items-center overflow-hidden px-6 py-6 text-center">
      <div className="flex w-full max-w-sm shrink-0 items-center justify-center gap-2">
        <span className="font-mono text-xs tracking-widest text-accent">HUMAN PROTOCOL</span>
        <MuteButton />
      </div>

      {/* Header y footer quedan pegados a los bordes; este bloque absorbe
          todo el espacio del medio y centra su contenido ahí adentro. */}
      <div className="flex min-h-0 flex-1 flex-col items-center justify-center gap-6">
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
      </div>

      <footer className="flex w-full max-w-sm shrink-0 justify-between font-mono text-[0.625rem] tracking-widest text-muted">
        <span>v4.02 // ALGORITHMIC_GOVERNANCE_SYSTEM</span>
        <span>PROTOCOL_ISO_9001</span>
      </footer>
    </div>
  );
}
