"use client";

import { useEffect, useRef } from "react";

const VIDEO_ID = "1RbsgMntwsQ";
const LOOP_START_SECONDS = 14;

interface YouTubePlayer {
  playVideo(): void;
  seekTo(seconds: number, allowSeekAhead: boolean): void;
  destroy(): void;
}

interface YouTubePlayerEvent {
  data: number;
}

declare global {
  interface Window {
    YT?: {
      Player: new (
        element: HTMLElement,
        options: {
          videoId: string;
          playerVars?: Record<string, number | string>;
          events?: {
            onStateChange?: (event: YouTubePlayerEvent) => void;
          };
        }
      ) => YouTubePlayer;
      PlayerState: { ENDED: number };
    };
    onYouTubeIframeAPIReady?: () => void;
  }
}

let apiLoadPromise: Promise<void> | null = null;

function loadYouTubeApi(): Promise<void> {
  if (window.YT?.Player) return Promise.resolve();
  if (apiLoadPromise) return apiLoadPromise;

  apiLoadPromise = new Promise((resolve) => {
    const previous = window.onYouTubeIframeAPIReady;
    window.onYouTubeIframeAPIReady = () => {
      previous?.();
      resolve();
    };
    const script = document.createElement("script");
    script.src = "https://www.youtube.com/iframe_api";
    document.body.appendChild(script);
  });
  return apiLoadPromise;
}

interface BackgroundAudioProps {
  active: boolean;
}

/** Audio de fondo (YouTube oculto), en loop desde LOOP_START_SECONDS, salteando
 * la intro. Suena solo mientras dura la detección (se destruye al salir). */
export function BackgroundAudio({ active }: BackgroundAudioProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const playerRef = useRef<YouTubePlayer | null>(null);

  useEffect(() => {
    if (!active) return;
    let cancelled = false;

    loadYouTubeApi().then(() => {
      if (cancelled || !containerRef.current || !window.YT) return;
      playerRef.current = new window.YT.Player(containerRef.current, {
        videoId: VIDEO_ID,
        playerVars: { autoplay: 1, start: LOOP_START_SECONDS, controls: 0, disablekb: 1 },
        events: {
          onStateChange: (event) => {
            if (event.data === window.YT?.PlayerState.ENDED) {
              playerRef.current?.seekTo(LOOP_START_SECONDS, true);
              playerRef.current?.playVideo();
            }
          },
        },
      });
    });

    return () => {
      cancelled = true;
      playerRef.current?.destroy();
      playerRef.current = null;
    };
  }, [active]);

  if (!active) return null;
  return <div ref={containerRef} className="hidden" />;
}
