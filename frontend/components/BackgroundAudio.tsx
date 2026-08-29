"use client";

import { useYouTubeAudio } from "@/hooks/useYouTubeAudio";
import { useMute } from "@/contexts/MuteContext";

interface BackgroundAudioProps {
  active: boolean;
  videoId: string;
  startSeconds?: number;
}

/** Música de fondo en loop mientras `active` sea true. */
export function BackgroundAudio({ active, videoId, startSeconds = 0 }: BackgroundAudioProps) {
  const { muted } = useMute();
  const wrapperRef = useYouTubeAudio({ active, videoId, loop: true, startSeconds, muted });

  if (!active) return null;
  return <div ref={wrapperRef} className="hidden" />;
}
