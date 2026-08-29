"use client";

import { createContext, useContext, useState, type ReactNode } from "react";

interface MuteContextValue {
  muted: boolean;
  toggleMuted: () => void;
}

const MuteContext = createContext<MuteContextValue | null>(null);

export function MuteProvider({ children }: { children: ReactNode }) {
  const [muted, setMuted] = useState(false);
  return (
    <MuteContext.Provider value={{ muted, toggleMuted: () => setMuted((m) => !m) }}>
      {children}
    </MuteContext.Provider>
  );
}

/** Estado de mute compartido por todos los reproductores de audio de la app. */
export function useMute(): MuteContextValue {
  const ctx = useContext(MuteContext);
  if (!ctx) throw new Error("useMute debe usarse dentro de MuteProvider");
  return ctx;
}
