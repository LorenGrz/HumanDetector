"use client";

import { useEffect, useRef } from "react";

const CAPTURE_INTERVAL_MS = 250;
const JPEG_QUALITY = 0.7;

interface CameraFeedProps {
  active: boolean;
  onFrame: (base64Jpeg: string) => void;
}

export function CameraFeed({ active, onFrame }: CameraFeedProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    let stream: MediaStream | null = null;

    navigator.mediaDevices
      .getUserMedia({ video: { width: 480, height: 480 }, audio: false })
      .then((s) => {
        stream = s;
        if (videoRef.current) videoRef.current.srcObject = s;
      })
      .catch((error) => console.error("No se pudo acceder a la cámara", error));

    return () => stream?.getTracks().forEach((track) => track.stop());
  }, []);

  useEffect(() => {
    if (!active) return;

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
  }, [active, onFrame]);

  return (
    <div className="relative aspect-square w-full max-w-sm overflow-hidden rounded-2xl border-2 border-accent shadow-[0_0_30px_-5px_var(--accent)]">
      <video ref={videoRef} autoPlay playsInline muted className="h-full w-full object-cover" />
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute inset-x-0 h-1 bg-accent/70 shadow-[0_0_12px_2px_var(--accent)] animate-scan-line" />
      </div>
      <span className="absolute top-2 right-2 rounded-full bg-black/60 px-2 py-1 font-mono text-[10px] tracking-widest text-accent">
        LIVE FEED
      </span>
      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
}
