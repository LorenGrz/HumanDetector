interface FaceMeshOverlayProps {
  points: [number, number][];
  connections: [number, number][];
}

/** Dibuja la malla de landmarks como líneas, tipo escáner biométrico. */
export function FaceMeshOverlay({ points, connections }: FaceMeshOverlayProps) {
  return (
    <svg
      viewBox="0 0 1 1"
      preserveAspectRatio="none"
      className="pointer-events-none absolute inset-0 h-full w-full"
    >
      {connections.map(([a, b], i) => {
        const p1 = points[a];
        const p2 = points[b];
        if (!p1 || !p2) return null;
        return (
          <line
            key={i}
            x1={p1[0]}
            y1={p1[1]}
            x2={p2[0]}
            y2={p2[1]}
            stroke="var(--accent)"
            strokeOpacity={0.85}
            strokeWidth={1}
            vectorEffect="non-scaling-stroke"
          />
        );
      })}
    </svg>
  );
}
