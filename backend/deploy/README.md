# Deploy del backend — AWS App Runner (on-demand)

El backend corre como contenedor en **AWS App Runner** (cuenta `493735739644`,
región `us-east-1`), **pausado por defecto**. Se reanuda sólo para mostrar el
demo del portfolio y se vuelve a pausar después.

## Recursos AWS (creados una vez)

| Recurso | Nombre |
|---|---|
| ECR repo | `humandetector-backend` |
| Bucket de build | `humandetector-build-493735739644` |
| Rol CodeBuild | `humandetector-codebuild-role` |
| Proyecto CodeBuild | `humandetector-backend-build` |
| Rol acceso ECR de App Runner | `AppRunnerECRAccessRole` |
| Servicio App Runner | `humandetector-backend` |

El ARN del servicio y la URL pública se guardan en `deploy/service.env`
(gitignoreado). Formato:

```sh
SERVICE_ARN=arn:aws:apprunner:us-east-1:493735739644:service/humandetector-backend/xxxxxxxx
SERVICE_URL=xxxxxxxx.us-east-1.awsapprunner.com
```

## Por qué CodeBuild y no `docker push` local

El data plane de ECR (`*.dkr.ecr.*`) se cuelga desde la red local (el control
plane de la API AWS anda bien). `build-remote.sh` empaqueta `backend/`, lo sube
a S3 y CodeBuild construye + pushea la imagen dentro de AWS. `push-image.sh`
queda como alternativa para cuando la red lo permita.

## Uso

```sh
# Antes de una demo (~5 min antes; el cold start + pull de imagen tardan):
backend/deploy/resume.sh
backend/deploy/status.sh          # esperar Status=RUNNING

# Después de la demo:
backend/deploy/pause.sh

# Publicar una imagen nueva (build en AWS + deploy si el servicio existe):
backend/deploy/build-remote.sh
```

## Costo

- Pausado: sólo almacenamiento ECR (~USD 0.05/mes).
- Reanudado: ~USD 0.05–0.08/h (1 vCPU / 2 GB) mientras dura la demo.
