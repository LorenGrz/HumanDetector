#!/usr/bin/env bash
# Construye la imagen del backend EN AWS con CodeBuild y la sube a ECR.
# Usar esto en vez de push-image.sh cuando la red local no puede pushear a ECR
# (el data plane de ECR se cuelga). Requiere que ya existan, una sola vez:
#   - repo ECR humandetector-backend
#   - bucket S3 humandetector-build-<account>
#   - rol IAM humandetector-codebuild-role
#   - proyecto CodeBuild humandetector-backend-build (source S3, privileged)
# Uso: backend/deploy/build-remote.sh
set -euo pipefail

cd "$(dirname "$0")/.."
. deploy/config.sh

BUCKET="humandetector-build-${ACCOUNT_ID}"
ZIP="/tmp/hd-src-$$.zip"

echo ">> Empaquetando backend/"
rm -f "$ZIP"
zip -r -q "$ZIP" . -x '.venv/*' -x '__pycache__/*' -x '*.pyc' -x 'deploy/service.env'

echo ">> Subiendo a s3://${BUCKET}/source/hd-src.zip"
aws s3 cp "$ZIP" "s3://${BUCKET}/source/hd-src.zip" --region "$AWS_REGION"
rm -f "$ZIP"

echo ">> Lanzando CodeBuild"
BID=$(aws codebuild start-build --region "$AWS_REGION" \
  --project-name humandetector-backend-build \
  --query 'build.id' --output text)
echo "   build id: $BID"

while true; do
  read -r PHASE STATUS < <(aws codebuild batch-get-builds --region "$AWS_REGION" \
    --ids "$BID" --query 'builds[0].[currentPhase,buildStatus]' --output text)
  echo "   $(date +%T)  $PHASE / $STATUS"
  case "$STATUS" in
    SUCCEEDED) echo ">> Imagen en ${ECR_URI}:${IMAGE_TAG}"; break ;;
    FAILED|FAULT|STOPPED|TIMED_OUT) echo ">> Build falló"; exit 1 ;;
  esac
  sleep 15
done

if [ -n "${SERVICE_ARN:-}" ]; then
  echo ">> Disparando deploy en App Runner"
  aws apprunner start-deployment --region "$AWS_REGION" --service-arn "$SERVICE_ARN" \
    --query 'OperationId' --output text
fi
