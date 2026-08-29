#!/usr/bin/env bash
# Construye la imagen del backend (x86_64) y la sube a ECR.
# Uso: backend/deploy/push-image.sh
set -euo pipefail

cd "$(dirname "$0")/.."
. deploy/config.sh

echo ">> Login a ECR (${AWS_REGION})"
aws ecr get-login-password --region "${AWS_REGION}" \
  | docker login --username AWS --password-stdin \
    "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo ">> Build ${ECR_URI}:${IMAGE_TAG} (linux/amd64)"
docker build --platform linux/amd64 -t "${ECR_URI}:${IMAGE_TAG}" .

echo ">> Push"
docker push "${ECR_URI}:${IMAGE_TAG}"

echo ">> Listo: ${ECR_URI}:${IMAGE_TAG}"
