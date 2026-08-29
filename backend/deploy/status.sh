#!/usr/bin/env bash
# Muestra estado y URL pública del servicio App Runner.
# Uso: backend/deploy/status.sh
set -euo pipefail

cd "$(dirname "$0")/.."
. deploy/config.sh

: "${SERVICE_ARN:?Falta SERVICE_ARN (backend/deploy/service.env)}"

aws apprunner describe-service --region "${AWS_REGION}" \
  --service-arn "${SERVICE_ARN}" \
  --query 'Service.{Status:Status,Url:ServiceUrl,Updated:UpdatedAt}' \
  --output table
