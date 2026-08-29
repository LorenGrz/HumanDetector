"use client";

import { useEffect, useRef, useState } from "react";
import { FaceMeshOverlay } from "./FaceMeshOverlay";

const CAPTURE_INTERVAL_MS = 250;
const JPEG_QUALITY = 0.7;

const ERROR_MESSAGES: Record<string, string> = {
  NotAllowedError: "Permiso de cámara denegado. Revisá los permisos del sitio en el navegador.",
  NotFoundError: "No se encontró ninguna cámara conectada.",
  NotReadableError: "La cámara está siendo usada por otra aplicación.",
};

interface CameraFeedProps {
  active: boolean;
  onFrame: (base64Jpeg: string) => void;
  meshPoints: [number, number][] | null;
  meshConnections: [number, number][];
}

export function CameraFeed({ active, onFrame, meshPoints, meshConnections }: CameraFeedProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let stream: MediaStream | null = null;

    if (!navigator.mediaDevices?.getUserMedia) {
      queueMicrotask(() =>
        setError("Este navegador no soporta acceso a cámara (necesita HTTPS o localhost).")
      );
    } else {
      navigator.mediaDevices
        .getUserMedia({ video: { width: 480, height: 480, aspectRatio: 1 }, audio: false })
        .then((s) => {
          stream = s;
          if (videoRef.current) videoRef.current.srcObject = s;
        })
        .catch((err: DOMException) => {
          console.error("No se pudo acceder a la cámara", err);
          setError(ERROR_MESSAGES[err.name] ?? `No se pudo acceder a la cámara (${err.name}).`);
        });
    }

    return () => stream?.getTracks().forEach((track) => track.stop());
  }, []);

  useEffect(() => {
    if (!active || error) return;

    const interval = window.setInterval(() => {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      if (!video || !canvas || video.readyState < 2) return;

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      ctx.drawImage(video, 0, 0);
      onFrame(canvas.toDataURL("image/jpeg", JPEG_QUALITY));
    }, CAPTURE_INTERVAL_MS);

    return () => window.clearInterval(interval);
  }, [active, error, onFrame]);

  return (
    <div className="relative aspect-square w-[min(75vw,34vh,320px)] overflow-hidden rounded-2xl border-2 border-accent shadow-[0_0_30px_-5px_var(--accent)] sm:w-[min(60vw,44vh,440px)] lg:w-[min(45vw,50vh,520px)]">
      {error ? (
        <div className="flex h-full w-full items-center justify-center bg-surface px-6 text-center text-sm text-danger">
          {error}
        </div>
      ) : (
        <video ref={videoRef} autoPlay playsInline muted className="h-full w-full object-cover" />
      )}
      {!error && meshPoints && meshConnections.length > 0 && (
        <FaceMeshOverlay points={meshPoints} connections={meshConnections} />
      )}
      {!error && (
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute inset-x-0 h-1 bg-accent/70 shadow-[0_0_12px_2px_var(--accent)] animate-scan-line" />
        </div>
      )}
      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
}
