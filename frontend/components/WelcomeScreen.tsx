interface WelcomeScreenProps {
  onStart: () => void;
}

export function WelcomeScreen({ onStart }: WelcomeScreenProps) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 px-6 text-center">
      <span className="font-mono text-xs tracking-widest text-accent">HUMAN PROTOCOL</span>
      <h1 className="text-3xl font-bold tracking-wide">¿SOS HUMANO?</h1>
      <p className="max-w-sm text-sm leading-relaxed text-muted">
        Vas a tener que probarlo. El sistema te va a pedir gestos frente a la cámara,
        cada vez más difíciles, contra un reloj que se achica en cada intento. Necesita
        acceso a tu cámara para empezar.
      </p>
      <button
        onClick={onStart}
        className="rounded-full border border-accent px-8 py-3 font-mono text-xs tracking-widest text-accent transition hover:bg-accent hover:text-background"
      >
        COMENZAR VERIFICACIÓN
      </button>
      <footer className="mt-8 flex w-full max-w-sm justify-between font-mono text-[10px] tracking-widest text-muted">
        <span>v4.02 // ALGORITHMIC_GOVERNANCE_SYSTEM</span>
        <span>PROTOCOL_ISO_9001</span>
      </footer>
    </div>
  );
}
