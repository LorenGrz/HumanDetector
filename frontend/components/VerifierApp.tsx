"use client";

import { useState } from "react";
import { useVerifierSession } from "@/hooks/useVerifierSession";
import { VerifierPanel } from "./VerifierPanel";
import { RevealScreen } from "./RevealScreen";
import { BackgroundAudio } from "./BackgroundAudio";
import { WelcomeScreen } from "./WelcomeScreen";
import { MuteProvider } from "@/contexts/MuteContext";

const ELEVATOR_VIDEO_ID = "jj0ChLVTpaA"; // Elevator Music — antes de empezar
const ALIEN_VIDEO_ID = "1RbsgMntwsQ"; // Música de extraterrestres — durante el test
const ALIEN_START_SECONDS = 14;

export function VerifierApp() {
  return (
    <MuteProvider>
      <VerifierFlow />
    </MuteProvider>
  );
}

function VerifierFlow() {
  const [started, setStarted] = useState(false);
  // El navegador bloquea el autoplay con sonido hasta que hay un gesto del
  // usuario en la página. Recién en el primer toque/click sobre la pantalla
  // de bienvenida montamos el player, así la música de ascensor suena de
  // verdad en vez de quedar en pausa silenciosa.
  const [audioUnlocked, setAudioUnlocked] = useState(false);

  if (!started) {
    return (
      <div className="contents" onPointerDownCapture={() => setAudioUnlocked(true)}>
        <BackgroundAudio active={audioUnlocked} videoId={ELEVATOR_VIDEO_ID} />
        <WelcomeScreen onStart={() => setStarted(true)} />
      </div>
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
      {/* Sigue sonando el ascensor mientras conecta el WebSocket, hasta que
          llega la primera instrucción y entra la música del test. */}
      <BackgroundAudio
        active={state.phase === "connecting" || state.phase === "disconnected"}
        videoId={ELEVATOR_VIDEO_ID}
      />
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
    <div className="flex h-screen flex-col items-center justify-center gap-4 overflow-hidden px-6 text-center">
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
