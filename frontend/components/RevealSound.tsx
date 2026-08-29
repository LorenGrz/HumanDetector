"use client";

import type { RevealVariant } from "@/types/protocol";
import { useYouTubeAudio } from "@/hooks/useYouTubeAudio";

const ALARM_VIDEO_ID = "5nRgCabardA"; // Alarm Sound Effect
const APPLAUSE_VIDEO_ID = "PsLXAIN-fxo"; // Aplausos y gritos

interface RevealSoundProps {
  variant: RevealVariant;
}

/** Suena una sola vez (sin loop) al llegar al veredicto: alarma si rechaza,
 * aplausos si confirma humano. */
export function RevealSound({ variant }: RevealSoundProps) {
  const videoId = variant === "confirmed" ? APPLAUSE_VIDEO_ID : ALARM_VIDEO_ID;
  const wrapperRef = useYouTubeAudio({ active: true, videoId, loop: false });

  return <div ref={wrapperRef} className="hidden" />;
}
