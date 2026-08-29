# Config compartida por los scripts de deploy. Se sourcea, no se ejecuta.
AWS_REGION="${AWS_REGION:-us-east-1}"
ECR_REPO="${ECR_REPO:-humandetector-backend}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

# Instancia EC2 del backend (creada una vez, ver deploy/README.md).
INSTANCE_ID="${INSTANCE_ID:-i-00cd99cf5a2f307eb}"
ELASTIC_IP="${ELASTIC_IP:-44.221.206.139}"
BACKEND_HOST="${BACKEND_HOST:-44-221-206-139.nip.io}"

ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}"
