# Propuesta — HumanDetector

> Un formulario más para probar que sos humano. Este no aprueba.

## El pitch en una línea

Escaneás un QR, le das la cámara, y un "verificador de humanidad" te pide
gestos cada vez más difíciles hasta que te rechaza con una acusación
distinta cada vez. Spoiler: nunca hubo un test que pudieras pasar.

## Por qué debería entrar

- **Funciona de verdad.** MediaPipe te lee la cara: parpadeo, giro, boca,
  inclinación. No es un video pregrabado, sos vos peleándote con el sistema.
- **Es rápido.** 60–90 segundos por persona, desde el teléfono del
  visitante. Cero fila.
- **Tiene moraleja sin bajar línea.** Los bancos ya te piden selfies y
  "girá la cabeza". Esto es lo mismo, solo que honesto sobre que no confía
  en vos.
- **Ya está deployado.** No es una promesa: `lorengrz.github.io/HumanDetector`.

## Qué van a ver en el booth

Un cartel con un QR y la frase "REQUIERE CÁMARA · NO VAS A APROBAR". La
gente lo escanea sola. El sistema los interroga, "duda" en voz alta cada 2
segundos, les pone un contador que se achica, y termina con veredicto:
casi siempre `SOSPECHOSO DE NO-HUMANIDAD`, y en 1 de cada 5 —si se movieron
lo suficiente y ganan el sorteo— un raro `HUMANO CONFIRMADO`.

## Stack

Next.js + TypeScript (GitHub Pages) · FastAPI + MediaPipe en Docker sobre
EC2 · un WebSocket que manda los frames · sin base de datos, nada se
guarda.

## Estado

Terminado y online. Falta calibrar umbrales con la luz real del venue.

---

Demo: `lorengrz.github.io/HumanDetector` · Código:
`github.com/LorenGrz/HumanDetector` · Deck: `deck/dist/humandetector.pdf`
