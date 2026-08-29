#!/usr/bin/env bash
# Estado de la instancia + health del backend.
set -euo pipefail
cd "$(dirname "$0")/.."
. deploy/config.sh

aws ec2 describe-instances --region "$AWS_REGION" --instance-ids "$INSTANCE_ID" \
  --query 'Reservations[0].Instances[0].{state:State.Name,ip:PublicIpAddress,type:InstanceType}' \
  --output table

echo ">> https://${BACKEND_HOST}/healthz"
curl -sS -m 8 "https://${BACKEND_HOST}/healthz" || echo "(sin respuesta)"
echo
