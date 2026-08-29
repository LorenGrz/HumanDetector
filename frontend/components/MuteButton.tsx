"use client";

import { useMute } from "@/contexts/MuteContext";

export function MuteButton() {
  const { muted, toggleMuted } = useMute();

  return (
    <button
      onClick={toggleMuted}
      aria-label={muted ? "Activar sonido" : "Silenciar"}
      className="fixed top-4 right-4 z-50 flex h-9 w-9 items-center justify-center rounded-full border border-accent bg-background/80 text-accent backdrop-blur transition hover:bg-accent hover:text-background"
    >
      {muted ? <MutedIcon /> : <SoundIcon />}
    </button>
  );
}

function SoundIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path
        d="M4 9v6h4l5 4V5L8 9H4Z"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path d="M17 8.5a5 5 0 0 1 0 7" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M19.5 6a8.5 8.5 0 0 1 0 12" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function MutedIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M4 9v6h4l5 4V5L8 9H4Z" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M16 9l5 6M21 9l-5 6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
