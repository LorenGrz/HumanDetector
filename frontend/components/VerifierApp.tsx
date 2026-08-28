"use client";

import { useVerifierSession } from "@/hooks/useVerifierSession";
import { VerifierPanel } from "./VerifierPanel";
import { RevealScreen } from "./RevealScreen";

export function VerifierApp() {
  const { state, sendFrame, restart } = useVerifierSession();

  if (state.phase === "reveal" && state.revealText) {
    return <RevealScreen text={state.revealText} onRestart={restart} />;
  }

  if (state.phase === "verifying" && state.instruction && state.step) {
    return (
      <VerifierPanel
        step={state.step}
        instruction={state.instruction}
        lastResult={state.lastResult}
        onFrame={sendFrame}
      />
    );
  }

  return <StatusScreen disconnected={state.phase === "disconnected"} onRetry={restart} />;
}

function StatusScreen({ disconnected, onRetry }: { disconnected: boolean; onRetry: () => void }) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 px-6 text-center">
      <span className="font-mono text-xs tracking-widest text-accent">HUMAN PROTOCOL</span>
      <p className="text-sm text-muted">
        {disconnected ? "Conexión perdida con el sistema." : "Conectando con el sistema..."}
      </p>
      {disconnected && (
        <button
          onClick={onRetry}
          className="rounded-full border border-accent px-6 py-2 font-mono text-xs tracking-widest text-accent"
        >
          REINTENTAR
        </button>
      )}
    </div>
  );
}
