# fe-de-vida — Human Protocol

Instalación satírica para una antihackathon: un "verificador de humanidad" que
pide gestos frente a la cámara, escala los pedidos hasta lo imposible, y
nunca aprueba. La moraleja: nunca hubo un test que pudieras pasar — como los
algoritmos reales que rechazan sin explicar por qué.

## Stack

- **Backend** (`backend/`): Python + FastAPI + mediapipe. WebSocket en
  `/ws/verify` que recibe frames de cámara y hace detección real de
  parpadeo y giro de cabeza para los primeros pasos.
- **Frontend** (`frontend/`): Next.js (App Router) + TypeScript + Tailwind.
  Captura la cámara del navegador y muestra la escalada de pedidos.

## Cómo correrlo (evento)

Dos terminales, un laptop con cámara:

**Backend**

```bash
cd backend
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

**Frontend**

```bash
cd frontend
pnpm install
pnpm dev
```

Abrir `http://localhost:3000` en el navegador del laptop del booth y aceptar
el permiso de cámara.

Para algo más estable en vivo (sin hot-reload de Next):

```bash
cd frontend
pnpm build && pnpm start
```

## Calibración

La detección de parpadeo (Eye Aspect Ratio) y giro de cabeza (yaw) en
`backend/detector.py` usa umbrales fijos que dependen de luz y cámara. Probar
en el ambiente real del evento antes del día — si el paso 1 o 2 no detecta
bien, ajustar `_EAR_CLOSED_THRESHOLD` en `detector.py` o `YAW_TURN_THRESHOLD`
en `challenge.py`.

A partir del paso 3 cada intento tiene un contador que se achica
(`PRESSURE_START_SECONDS` / `PRESSURE_STEP_SECONDS` / `PRESSURE_FLOOR_SECONDS`
en `challenge.py`), y el paso se aprueba de verdad si el movimiento facial
durante esa ventana supera `MOTION_PASS_THRESHOLD` — probar en el lugar real
y ajustar el umbral: si nadie logra pasar nunca (ni moviéndose mucho) está
muy alto; si pasa todo el mundo sin esfuerzo, muy bajo.

`TOTAL_STEPS` en `challenge.py` controla cuántos pasos hay en total (por
defecto 10) antes del veredicto final.

## Arquitectura

```
backend/
  main.py        # WebSocket /ws/verify, orquesta detector + sesión por conexión
  detector.py     # Señales crudas de mediapipe (parpadeos, yaw) — sin lógica de guion
  challenge.py    # Máquina de estados de la escalada de pedidos y mensajes

frontend/
  app/            # Rutas (App Router)
  components/     # UI: CameraFeed, FaceMeshOverlay, Countdown, SuspicionLog,
                  #     BackgroundAudio, VerifierPanel, RevealScreen, VerifierApp
  hooks/          # useVerifierSession: estado de la sesión de verificación
  lib/            # verifierSocket: cliente WebSocket, sin lógica de UI
  types/          # Protocolo compartido con el backend (mensajes WS)
```

Protocolo WebSocket (JSON):

- Cliente → Servidor: `{"type": "frame", "data": "<jpeg base64>"}`
- Servidor → Cliente: `{"kind": "instruction", "step": n, "text": "...", "duration": n|null}`
- Servidor → Cliente: `{"kind": "result", "step": n, "passed": bool, "message": "..."}`
- Servidor → Cliente: `{"kind": "reveal", "text": "<acusación>", "message": "..."}`
- Servidor → Cliente: `{"kind": "confirmed", "text": "HUMANO CONFIRMADO", "message": "..."}`
- Servidor → Cliente: `{"kind": "topology", "connections": [[i, j], ...]}` (una vez, al conectar)
- Servidor → Cliente: `{"kind": "landmarks", "points": [[x, y], ...]}` (por frame, mientras dura la sesión)
- Servidor → Cliente: `{"kind": "suspicion", "text": "..."}` (cada ~2s, en paralelo, todo el rato)

## Audio de fondo

Mientras dura la verificación suena un video de YouTube embebido (oculto,
solo audio), arrancando en el segundo 14 (salteando la intro) y loopeando
ahí mismo cuando el video termina — usa la API real de YouTube (no un
simple iframe) para poder seekear al loopear. Se corta al llegar al
veredicto. Configuración en `frontend/components/BackgroundAudio.tsx`
(`VIDEO_ID`, `LOOP_START_SECONDS`). Nota: los navegadores bloquean el
autoplay con sonido si no hubo interacción previa del usuario con la
página — como ya se le pide permiso de cámara antes, en general debería
sonar, pero probarlo en el navegador real del evento.
