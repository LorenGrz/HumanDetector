# Repository Context

## Purpose

"Human Protocol" — instalación satírica para una antihackathon. Un
"verificador de humanidad" pide gestos frente a la cámara del usuario,
escala los pedidos hasta lo imposible, y casi siempre rechaza. La
moraleja: los algoritmos reales rechazan sin explicar por qué, y acá
literalmente no hay forma justa de pasar (aunque técnicamente sí hay una
chance remota — ver más abajo).

Pensado para correr en vivo en un booth/evento, con cámara real.

## Stack

- **Backend** (`backend/`): Python 3.12+, FastAPI, mediapipe (Tasks API,
  no la `solutions` legacy), OpenCV headless, gestionado con `uv`.
- **Frontend** (`frontend/`): Next.js 16 (App Router, Turbopack),
  TypeScript, Tailwind CSS v4, React 19. Gestionado con `pnpm`.
- Sin base de datos ni backend persistente: todo el estado vive en memoria
  por conexión de WebSocket.

## Project Structure

```
backend/
  main.py        # WebSocket /ws/verify: orquesta detector + sesión por conexión
  detector.py     # FaceGestureDetector: señales crudas de mediapipe (sin lógica de guion)
  challenge.py    # ChallengeSession: máquina de estados de la escalada de pedidos
  models/         # face_landmarker.task (modelo de mediapipe, committeado en el repo)

frontend/
  app/            # Rutas (App Router) — básicamente un layout + page.tsx
  components/     # UI: VerifierApp (orquestador), WelcomeScreen, VerifierPanel,
                  #     RevealScreen, CameraFeed, FaceMeshOverlay, Countdown,
                  #     SuspicionLog, MuteButton, BackgroundAudio, RevealSound
  hooks/          # useVerifierSession (estado de sesión), useYouTubeAudio
  lib/            # verifierSocket.ts (cliente WS), youtubePlayer.ts (IFrame API)
  contexts/       # MuteContext (mute compartido por los reproductores de audio)
  types/          # protocol.ts — tipos del protocolo WS compartido con el backend
```

## Package Manager And Scripts

Backend (desde `backend/`, con `uv`):

```bash
uv run uvicorn main:app --reload --port 8000
```

Frontend (desde `frontend/`, con `pnpm`):

```bash
pnpm install
pnpm dev            # dev server (Turbopack)
pnpm build           # build de producción
pnpm exec tsc --noEmit
pnpm exec eslint .
```

No hay script de test automatizado en ninguno de los dos lados.

## Architecture Rules

- **Protocolo WebSocket** (`/ws/verify`, JSON) — definido en
  `backend/challenge.py` (`StepResult`) y `frontend/types/protocol.ts`
  (`ServerMessage`). Mensajes: `instruction`, `result`, `reveal`,
  `confirmed`, `topology` (malla facial, una vez), `landmarks` (por
  frame), `suspicion` (cada ~2s, en paralelo).
- **`detector.py` no conoce el guion**: solo expone señales crudas
  (parpadeos, yaw, roll, pitch, mouth_aspect_ratio, face_width, puntos de
  malla). Toda la interpretación "pasa/no pasa" vive en `challenge.py`.
- **`main.py`** despacha por tipo de paso usando `spec.kind not in
  ("auto_pass", "reject")` para decidir si es un paso real — NO uses una
  lista explícita de nombres ahí, ya causó un bug real al sumar gestos
  nuevos y olvidar actualizarla.
- **Plan de sesión**: cada `ChallengeSession` sortea un plan de 10 pasos:
  3 reales (de families: blink, yaw, mouth_open, tilt lateral,
  tilt_forward, look_up, move_closer — sampleadas sin reemplazo), 1-2
  teatrales (auto_pass, siempre pasan), y el resto de rechazo (reject, en
  3 secciones de dificultad crecientes con instrucción random dentro de
  cada sección).
- **Gestos reales nuevos**: si agregás uno, tiene que tener detección real
  (no meterlo en `_AUTO_PASS_BANK` con la excusa de "después lo hago
  real" — ya pasó dos veces y el usuario lo notó ambas veces).
- **"Humano confirmado"** es posible pero raro a propósito: hace falta
  superar `MOTION_PASS_THRESHOLD` de movimiento Y ganar un sorteo de
  `CONFIRM_PROBABILITY` (1/5). Además, `main.py` guarda a nivel de módulo
  si la última sesión terminó confirmada; si fue así, la siguiente sesión
  nace con `allow_confirm=False` (no puede confirmar dos veces seguidas).
- **Layout sin scroll**: las pantallas usan `h-screen overflow-hidden`
  (no `min-h-screen`). Los elementos de contenido variable (contador,
  estado, log de sospechas) reservan altura fija para que agregar/cambiar
  texto no mueva el resto del layout. La cámara tiene su propio ancho
  responsive (no hereda `max-w-sm` del contenedor de texto) para
  aprovechar el ancho en desktop.
- **Audio**: todo vía YouTube IFrame Player API (`lib/youtubePlayer.ts` +
  `hooks/useYouTubeAudio.ts`), no archivos locales. El player apunta a un
  nodo creado a mano (no JSX) porque la API de YouTube reemplaza ese nodo
  por su iframe — si React fuera dueño del nodo, las reconciliaciones
  chocan (`removeChild` error) al desmontar/remontar.
- **Botón de mute**: inline en el flujo normal (NO `fixed`), vive dentro
  del header/label de cada pantalla vía `MuteContext`. Antes era `fixed`
  y se solapaba con otros elementos en viewports angostos.

## Testing And Verification

- Sin suite de tests automatizada. Verificación manual:
  - Backend: `uv run python -c "import main"` para chequear que importa,
    y simulaciones directas de `ChallengeSession` para probar lógica
    (ver ejemplos en el historial de commits).
  - Frontend: `pnpm exec tsc --noEmit`, `pnpm exec eslint .`, `pnpm build`.
  - Verificación visual/funcional real: con los dos servers corriendo,
    contra cámara real (headless/preview automatizado no tiene cámara).

## Local Development Services

- Backend en `http://localhost:8000` (WebSocket en `/ws/verify`).
- Frontend en `http://localhost:3000`.
- CORS del backend: localhost + lo que diga `FRONTEND_ORIGIN` (`main.py`).
- `.claude/launch.json` define ambos servers para `preview_start`.

## Deploy

- **Frontend**: GitHub Pages en `https://lorengrz.github.io/HumanDetector/`.
  Export estático (`next.config.ts` → `output: 'export'`, `basePath` desde
  `NEXT_PUBLIC_BASE_PATH`). Workflow `.github/workflows/deploy-frontend.yml`
  se dispara al pushear a `master` tocando `frontend/**`. La URL del backend
  se hornea en build desde la variable de repo `VERIFIER_WS_URL`.
- **Backend**: contenedor Docker en EC2 (`i-00cd99cf5a2f307eb`, us-east-1) +
  Caddy con TLS Let's Encrypt para `44-221-206-139.nip.io`. Imagen en ECR,
  construida con CodeBuild. Scripts en `backend/deploy/` (`start.sh` /
  `stop.sh` / `status.sh` / `redeploy.sh`) y detalle en `backend/deploy/README.md`.
  On-demand: se prende para el evento y se apaga después.

## Agent Notes

- Repo público en GitHub: `LorenGrz/HumanDetector` (renombrado desde
  `fe-de-vida` para servir en `lorengrz.github.io/HumanDetector`). No se
  pushea directo a `master` sin confirmación explícita del usuario.
- El usuario prueba con cámara real en su propia máquina; yo no tengo
  cámara en el entorno de preview, así que la detección de gestos
  específicos no se puede validar end-to-end de mi lado — solo la lógica
  (simulaciones) y que la app cargue/renderice bien.
- Constantes de calibración (umbrales de EAR/yaw/roll/pitch/mouth,
  `MOTION_PASS_THRESHOLD`) están en `backend/detector.py` y
  `backend/challenge.py`, marcadas como "ajustar según cámara/evento" —
  esperar feedback real del usuario antes de tocarlas a ciegas.
- Evento es pronto ("antihackathon"), priorizar fixes robustos y rápidos
  sobre refactors grandes.

## Last Reviewed

2026-08-29 — creado a partir del estado real del repo (package.json,
pyproject.toml, estructura de directorios, y el historial de esta sesión
de desarrollo) en la rama `feat/timed-escalation-and-audio`.
