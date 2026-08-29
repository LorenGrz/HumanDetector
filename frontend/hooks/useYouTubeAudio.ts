"use client";

import { useEffect, useRef } from "react";
import { loadYouTubeApi, type YouTubePlayer } from "@/lib/youtubePlayer";

interface UseYouTubeAudioOptions {
  active: boolean;
  videoId: string;
  loop?: boolean;
  startSeconds?: number;
}

/** Reproduce audio de YouTube (oculto) mientras `active` sea true.
 *
 * El player apunta a un nodo creado a mano (no vía JSX): la API de YouTube
 * reemplaza ese nodo por su propio iframe por fuera de React. Si React
 * fuera dueño de ese nodo, las dos reconciliaciones del DOM chocan
 * ("Failed to execute removeChild") apenas el componente se desmonta o
 * remonta (p. ej. en Strict Mode). El wrapper que sí maneja React nunca
 * tiene hijos en su JSX, así que nunca hay conflicto. */
export function useYouTubeAudio({
  active,
  videoId,
  loop = false,
  startSeconds = 0,
}: UseYouTubeAudioOptions) {
  const wrapperRef = useRef<HTMLDivElement>(null);
  const playerRef = useRef<YouTubePlayer | null>(null);

  useEffect(() => {
    if (!active || !wrapperRef.current) return;
    let cancelled = false;

    const target = document.createElement("div");
    wrapperRef.current.appendChild(target);

    loadYouTubeApi().then(() => {
      if (cancelled || !window.YT) return;
      playerRef.current = new window.YT.Player(target, {
        videoId,
        playerVars: { autoplay: 1, start: startSeconds, controls: 0, disablekb: 1 },
        events: {
          onStateChange: (event) => {
            if (loop && event.data === window.YT?.PlayerState.ENDED) {
              playerRef.current?.seekTo(startSeconds, true);
              playerRef.current?.playVideo();
            }
          },
        },
      });
    });

    return () => {
      cancelled = true;
      try {
        playerRef.current?.destroy();
      } catch {
        // El player puede haber mutado el DOM por su cuenta; ignorar.
      }
      playerRef.current = null;
      target.remove();
    };
  }, [active, videoId, loop, startSeconds]);

  return wrapperRef;
}
