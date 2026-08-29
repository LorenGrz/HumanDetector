# Deploy del backend — EC2 + Caddy (on-demand)

El backend corre como contenedor Docker en una instancia **EC2** (cuenta
`493735739644`, región `us-east-1`). Caddy hace de reverse proxy y saca
certificado TLS automático de Let's Encrypt, así que el frontend en GitHub Pages
puede abrir `wss://` sin dominio propio.

> **No es App Runner.** La cuenta es nueva y App Runner pide una activación
> manual que tarda días; EC2 se pudo levantar por CLI directo.

## Recursos AWS (creados una vez)

| Recurso | Valor |
|---|---|
| Instancia EC2 | `i-00cd99cf5a2f307eb` (`m7i-flex.large`, 2 vCPU / 8 GB, x86_64) |
| Elastic IP | `44.221.206.139` |
| Hostname | `44-221-206-139.nip.io` (respaldo: `44-221-206-139.sslip.io`) |
| Security group | `humandetector-sg` (22 desde tu IP, 80/443 público) |
| Key pair | `humandetector-ec2` → `~/.ssh/humandetector-ec2.pem` |
| Instance profile | `humandetector-ec2-profile` (ECR read + SSM) |
| ECR repo | `humandetector-backend` |
| Build en AWS | proyecto CodeBuild `humandetector-backend-build` + bucket `humandetector-build-493735739644` |

El `user-data` de arranque está en `deploy/ec2-user-data.sh` (instala Docker,
baja la imagen de ECR, levanta `backend` + `caddy` con `--restart always`).

## Por qué CodeBuild y no `docker push` local

El data plane de ECR (`*.dkr.ecr.*`) se cuelga desde la red local. `build-remote.sh`
sube `backend/` a S3 y CodeBuild construye + pushea la imagen dentro de AWS.
`push-image.sh` queda como alternativa para cuando la red lo permita.

## Uso

```sh
backend/deploy/start.sh     # prender la instancia (~2-3 min; contenedores solos)
backend/deploy/status.sh    # estado de la instancia + GET /healthz
backend/deploy/stop.sh      # apagar (frena cobro de cómputo)

backend/deploy/redeploy.sh  # imagen nueva: build en CodeBuild + recrea contenedor vía SSM
```

SSH si hace falta depurar:
`ssh -i ~/.ssh/humandetector-ec2.pem ec2-user@44.221.206.139`
(logs: `docker logs backend`, `docker logs caddy`, `/var/log/hd-bootstrap.log`)

## Costo

- Instancia encendida: ~USD 0.10/h (`m7i-flex.large`).
- Apagada: EBS ~USD 1.6/mes + Elastic IP ~USD 3.6/mes.
- ECR: ~USD 0.05/mes.
