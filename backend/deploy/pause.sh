#!/usr/bin/env bash
# Pausa el servicio App Runner. Sin cobro de cómputo mientras está pausado.
# Uso: backend/deploy/pause.sh
set -euo pipefail

cd "$(dirname "$0")/.."
. deploy/config.sh

: "${SERVICE_ARN:?Falta SERVICE_ARN (backend/deploy/service.env)}"

aws apprunner pause-service --region "${AWS_REGION}" \
  --service-arn "${SERVICE_ARN}" \
  --query 'Service.Status' --output text
