"use client";

import { useEffect, useState } from "react";

interface CountdownProps {
  seconds: number;
}

/** Cuenta regresiva local; se resetea remontando con una key distinta por instrucción. */
export function Countdown({ seconds }: CountdownProps) {
  const [remaining, setRemaining] = useState(seconds);

  useEffect(() => {
    const start = Date.now();
    const interval = window.setInterval(() => {
      const elapsed = (Date.now() - start) / 1000;
      setRemaining(Math.max(0, seconds - elapsed));
    }, 100);
    return () => window.clearInterval(interval);
  }, [seconds]);

  const urgent = remaining <= 3;

  return (
    <div
      className={`font-mono text-2xl font-bold tabular-nums ${
        urgent ? "text-danger" : "text-danger/80"
      }`}
    >
      {remaining.toFixed(1)}s
    </div>
  );
}
