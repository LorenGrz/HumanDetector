#!/usr/bin/env bash
# Reanuda el servicio App Runner (on-demand). Correr ~5 min antes de una demo.
# Uso: backend/deploy/resume.sh
set -euo pipefail

cd "$(dirname "$0")/.."
. deploy/config.sh

: "${SERVICE_ARN:?Falta SERVICE_ARN (backend/deploy/service.env)}"

aws apprunner resume-service --region "${AWS_REGION}" \
  --service-arn "${SERVICE_ARN}" \
  --query 'Service.Status' --output text

echo ">> Reanudando. Seguí el estado con: backend/deploy/status.sh"
