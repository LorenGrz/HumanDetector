#!/usr/bin/env bash
# Publica una imagen nueva: build en CodeBuild (build-remote.sh) y luego
# recrea el contenedor en la instancia vía SSM.
set -euo pipefail
cd "$(dirname "$0")/.."
. deploy/config.sh

echo ">> Build + push a ECR (CodeBuild)"
bash deploy/build-remote.sh

echo ">> Recreando contenedor en $INSTANCE_ID vía SSM"
CID=$(aws ssm send-command --region "$AWS_REGION" --instance-ids "$INSTANCE_ID" \
  --document-name AWS-RunShellScript \
  --parameters 'commands=[
    "aws ecr get-login-password --region '"$AWS_REGION"' | docker login --username AWS --password-stdin '"$ACCOUNT_ID"'.dkr.ecr.'"$AWS_REGION"'.amazonaws.com",
    "docker pull '"$ECR_URI:$IMAGE_TAG"'",
    "docker rm -f backend",
    "docker run -d --restart always --name backend --network app -e PORT=8080 -e FRONTEND_ORIGIN=https://lorengrz.github.io '"$ECR_URI:$IMAGE_TAG"'",
    "sleep 5",
    "docker run --rm --network app curlimages/curl -sS -m5 http://backend:8080/healthz"
  ]' \
  --query 'Command.CommandId' --output text)
echo "   command id: $CID"
sleep 20
aws ssm get-command-invocation --region "$AWS_REGION" --command-id "$CID" \
  --instance-id "$INSTANCE_ID" --query 'StandardOutputContent' --output text
