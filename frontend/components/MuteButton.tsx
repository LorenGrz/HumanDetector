"use client";

import { useMute } from "@/contexts/MuteContext";

export function MuteButton() {
  const { muted, toggleMuted } = useMute();

  return (
    <button
      onClick={toggleMuted}
      aria-label={muted ? "Activar sonido" : "Silenciar"}
      className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-accent text-accent transition hover:bg-accent hover:text-background"
    >
      {muted ? <MutedIcon /> : <SoundIcon />}
    </button>
  );
}

function SoundIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-3 w-3" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M4 9v6h4l5 4V5L8 9H4Z" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M17 8.5a5 5 0 0 1 0 7" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M19.5 6a8.5 8.5 0 0 1 0 12" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function MutedIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-3 w-3" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M4 9v6h4l5 4V5L8 9H4Z" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M16 9l5 6M21 9l-5 6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
