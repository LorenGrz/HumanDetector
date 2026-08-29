interface SuspicionLogProps {
  lines: string[];
}

/** Lo que "va sospechando" el sistema en vivo, tipo log de consola. */
export function SuspicionLog({ lines }: SuspicionLogProps) {
  if (lines.length === 0) return null;

  return (
    <div className="flex w-full max-w-sm flex-col gap-1.5 font-mono text-base font-semibold tracking-wide text-danger">
      {lines.map((line, i) => (
        <p key={`${i}-${line}`} style={{ opacity: 0.4 + (0.6 * (i + 1)) / lines.length }}>
          {"> "}
          {line}
        </p>
      ))}
    </div>
  );
}
