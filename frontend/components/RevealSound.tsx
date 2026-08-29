"use client";

import { useEffect, useRef } from "react";
import type { RevealVariant } from "@/types/protocol";

type AudioContextCtor = typeof AudioContext;

interface RevealSoundProps {
  variant: RevealVariant;
}

/** Sintetiza el sonido con Web Audio (sin archivos externos): sirena tipo
 * alarma cuando rechaza, aplausos cuando confirma humano. */
export function RevealSound({ variant }: RevealSoundProps) {
  const playedRef = useRef(false);

  useEffect(() => {
    if (playedRef.current) return;
    playedRef.current = true;

    const Ctor: AudioContextCtor | undefined =
      window.AudioContext ??
      (window as typeof window & { webkitAudioContext?: AudioContextCtor }).webkitAudioContext;
    if (!Ctor) return;

    const ctx = new Ctor();
    if (variant === "confirmed") {
      playApplause(ctx);
    } else {
      playAlarm(ctx);
    }

    return () => {
      ctx.close().catch(() => undefined);
    };
  }, [variant]);

  return null;
}

function playAlarm(ctx: AudioContext): void {
  const totalDuration = 2.6;
  const cycles = 5;
  const cycleDuration = totalDuration / cycles;

  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.type = "sawtooth";
  gain.gain.value = 0.12;
  osc.connect(gain);
  gain.connect(ctx.destination);

  const now = ctx.currentTime;
  for (let i = 0; i < cycles; i++) {
    const t0 = now + i * cycleDuration;
    const mid = t0 + cycleDuration / 2;
    const t1 = t0 + cycleDuration;
    osc.frequency.setValueAtTime(650, t0);
    osc.frequency.linearRampToValueAtTime(1050, mid);
    osc.frequency.linearRampToValueAtTime(650, t1);
  }

  osc.start(now);
  osc.stop(now + totalDuration);
}

function playApplause(ctx: AudioContext): void {
  const duration = 1.8;
  const clapCount = 45;
  const now = ctx.currentTime;

  for (let i = 0; i < clapCount; i++) {
    const startTime = now + Math.random() * duration;
    const bufferSize = Math.floor(ctx.sampleRate * 0.05);
    const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let j = 0; j < bufferSize; j++) {
      data[j] = (Math.random() * 2 - 1) * Math.exp(-j / (bufferSize * 0.3));
    }

    const source = ctx.createBufferSource();
    source.buffer = buffer;

    const gain = ctx.createGain();
    gain.gain.value = 0.2 + Math.random() * 0.15;

    source.connect(gain);
    gain.connect(ctx.destination);
    source.start(startTime);
  }
}
