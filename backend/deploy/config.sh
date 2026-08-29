# Config compartida por los scripts de deploy. Se sourcea, no se ejecuta.
# SERVICE_ARN se guarda en service.env (gitignoreado) tras crear el servicio.

AWS_REGION="${AWS_REGION:-us-east-1}"
ECR_REPO="${ECR_REPO:-humandetector-backend}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

_here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "${_here}/service.env" ]; then
  # shellcheck disable=SC1091
  . "${_here}/service.env"
fi

ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}"
