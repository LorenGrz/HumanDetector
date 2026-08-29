"use client";

import { useYouTubeAudio } from "@/hooks/useYouTubeAudio";

interface BackgroundAudioProps {
  active: boolean;
  videoId: string;
  startSeconds?: number;
}

/** Música de fondo en loop mientras `active` sea true. */
export function BackgroundAudio({ active, videoId, startSeconds = 0 }: BackgroundAudioProps) {
  const wrapperRef = useYouTubeAudio({ active, videoId, loop: true, startSeconds });

  if (!active) return null;
  return <div ref={wrapperRef} className="hidden" />;
}
