"use client";

import { useState } from "react";
import { useVerifierSession } from "@/hooks/useVerifierSession";
import { VerifierPanel } from "./VerifierPanel";
import { RevealScreen } from "./RevealScreen";
import { BackgroundAudio } from "./BackgroundAudio";
import { WelcomeScreen } from "./WelcomeScreen";

const ELEVATOR_VIDEO_ID = "jj0ChLVTpaA"; // Elevator Music — antes de empezar
const ALIEN_VIDEO_ID = "1RbsgMntwsQ"; // Música de extraterrestres — durante el test
const ALIEN_START_SECONDS = 14;

export function VerifierApp() {
  const [started, setStarted] = useState(false);

  if (!started) {
    return (
      <>
        <BackgroundAudio active videoId={ELEVATOR_VIDEO_ID} />
        <WelcomeScreen onStart={() => setStarted(true)} />
      </>
    );
  }

  return <ActiveVerifier />;
}

/** Solo se monta después de la bienvenida: recién ahí se conecta el
 * WebSocket y CameraFeed pide permiso de cámara. */
function ActiveVerifier() {
  const { state, mesh, sendFrame, restart } = useVerifierSession();

  return (
    <>
      <BackgroundAudio
        active={state.phase === "verifying"}
        videoId={ALIEN_VIDEO_ID}
        startSeconds={ALIEN_START_SECONDS}
      />
      {renderScreen()}
    </>
  );

  function renderScreen() {
    if (state.phase === "reveal" && state.revealLabel && state.revealMessage) {
      return (
        <RevealScreen
          variant={state.revealVariant}
          label={state.revealLabel}
          message={state.revealMessage}
          onRestart={restart}
        />
      );
    }

    if (state.phase === "verifying" && state.instruction && state.step) {
      return (
        <VerifierPanel
          step={state.step}
          instruction={state.instruction}
          instructionDuration={state.instructionDuration}
          lastResult={state.lastResult}
          suspicionLog={state.suspicionLog}
          onFrame={sendFrame}
          meshPoints={mesh.points}
          meshConnections={mesh.connections}
        />
      );
    }

    return <StatusScreen disconnected={state.phase === "disconnected"} onRetry={restart} />;
  }
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
