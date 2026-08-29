#!/usr/bin/env bash
# Prende la instancia EC2 del backend. Correr ~3 min antes de una demo.
set -euo pipefail
cd "$(dirname "$0")/.."
. deploy/config.sh

aws ec2 start-instances --region "$AWS_REGION" --instance-ids "$INSTANCE_ID" \
  --query 'StartingInstances[0].CurrentState.Name' --output text
echo ">> Esperando estado running..."
aws ec2 wait instance-running --region "$AWS_REGION" --instance-ids "$INSTANCE_ID"
echo ">> Instancia arriba. Los contenedores levantan con --restart always."
echo ">> Probá:  curl https://${BACKEND_HOST}/healthz"
echo ">> WS:     wss://${BACKEND_HOST}/ws/verify"
