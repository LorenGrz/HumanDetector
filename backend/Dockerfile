# Imagen del backend del verificador (FastAPI + mediapipe + OpenCV).
# x86_64 obligatorio: mediapipe no publica wheels confiables para Linux ARM64.
FROM python:3.12-slim

# uv (mismo gestor que en local) desde la imagen oficial de Astral.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Libs de sistema que necesitan opencv-python-headless / mediapipe.
# mediapipe 1.x carga bindings nativos que enlazan EGL/GLES y OpenMP.
RUN apt-get update && apt-get install -y --no-install-recommends \
      libgl1 libglib2.0-0 libegl1 libgles2 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Capa de dependencias (se cachea mientras no cambien pyproject/uv.lock).
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Código + modelo de face landmarks (models/face_landmarker.task).
COPY . .

# App Runner inyecta PORT (default 8080). Localmente vale el default.
ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "uv run uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
