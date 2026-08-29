const MAX_LINES = 3;

interface SuspicionLogProps {
  lines: string[];
}

/** Lo que "va sospechando" el sistema en vivo, tipo log de consola.
 *
 * Siempre reserva la misma altura (MAX_LINES filas de una sola línea cada
 * una, truncada con "..." si no entra) para que el resto del layout no se
 * mueva cuando cambia la cantidad o el largo de los mensajes. */
export function SuspicionLog({ lines }: SuspicionLogProps) {
  const rows = Array.from({ length: MAX_LINES }, (_, i) => lines[i] ?? null);

  return (
    <div className="flex w-full max-w-sm flex-col gap-1 font-mono text-sm font-semibold tracking-wide text-danger">
      {rows.map((line, i) => (
        <p
          key={i}
          className="truncate"
          style={line ? { opacity: 0.4 + (0.6 * (i + 1)) / MAX_LINES } : { visibility: "hidden" }}
        >
          {"> "}
          {line ?? "placeholder"}
        </p>
      ))}
    </div>
  );
}
