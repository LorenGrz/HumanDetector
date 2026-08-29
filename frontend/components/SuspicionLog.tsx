import type { SuspicionEntry } from "@/types/protocol";

const MAX_ENTRIES = 3;

interface SuspicionLogProps {
  lines: SuspicionEntry[];
}

const FADE_MASK = "linear-gradient(to bottom, transparent, black 24px)";

/** Lo que "va sospechando" el sistema en vivo, tipo log de consola.
 *
 * Altura fija (para que el resto del layout no se mueva), pero el texto
 * ya no se corta con "...": envuelve completo. Si no entran las 3 líneas
 * más recientes, las de arriba se desvanecen con un degradado en vez de
 * cortarse a la mitad. Cada entrada tiene un id estable (no el texto, que
 * se repite; no el índice, que se reutiliza al desplazar la lista) para
 * que la animación de entrada dispare solo en mensajes realmente nuevos. */
export function SuspicionLog({ lines }: SuspicionLogProps) {
  const visible = lines.slice(-MAX_ENTRIES);

  return (
    <div
      className="h-16 w-full max-w-sm overflow-hidden"
      style={{ maskImage: FADE_MASK, WebkitMaskImage: FADE_MASK }}
    >
      <div className="flex flex-col justify-end gap-1 font-mono text-sm font-semibold tracking-wide text-danger">
        {visible.map((entry, i) => (
          <p
            key={entry.id}
            className="animate-suspicion-in"
            style={{ opacity: 0.5 + (0.5 * (i + 1)) / visible.length }}
          >
            {"> "}
            {entry.text}
          </p>
        ))}
      </div>
    </div>
  );
}
