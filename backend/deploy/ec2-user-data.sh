#!/bin/bash
# user-data de la instancia EC2 del backend (Amazon Linux 2023).
# Instala Docker, baja la imagen desde ECR, y levanta backend + Caddy
# (TLS automático Let's Encrypt para <ip>.nip.io y <ip>.sslip.io).
# Editar HOSTS si cambia la Elastic IP.
set -euxo pipefail
exec > /var/log/hd-bootstrap.log 2>&1

REGION=us-east-1
ACCOUNT=493735739644
IMAGE="${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/humandetector-backend:latest"
IP_DASHES="44-221-206-139"
FRONTEND_ORIGIN="https://lorengrz.github.io"

dnf install -y docker
systemctl enable --now docker

for i in 1 2 3 4 5; do
  aws ecr get-login-password --region "$REGION" \
    | docker login --username AWS --password-stdin "${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com" && break
  sleep 5
done

docker pull "$IMAGE"
docker network create app || true

docker rm -f backend || true
docker run -d --restart always --name backend --network app \
  -e PORT=8080 -e FRONTEND_ORIGIN="$FRONTEND_ORIGIN" "$IMAGE"

mkdir -p /etc/caddy
cat > /etc/caddy/Caddyfile <<EOF
${IP_DASHES}.nip.io {
	reverse_proxy backend:8080
}
${IP_DASHES}.sslip.io {
	reverse_proxy backend:8080
}
EOF

docker rm -f caddy || true
docker run -d --restart always --name caddy --network app \
  -p 80:80 -p 443:443 \
  -v caddy_data:/data -v caddy_config:/config \
  -v /etc/caddy/Caddyfile:/etc/caddy/Caddyfile:ro \
  caddy:2

echo "bootstrap done"
