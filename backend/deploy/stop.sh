#!/usr/bin/env bash
# Apaga la instancia EC2. Frenás el cobro de cómputo (seguís pagando EBS ~USD 1.6/mes
# y la Elastic IP ~USD 3.6/mes mientras la instancia está apagada).
set -euo pipefail
cd "$(dirname "$0")/.."
. deploy/config.sh

aws ec2 stop-instances --region "$AWS_REGION" --instance-ids "$INSTANCE_ID" \
  --query 'StoppingInstances[0].CurrentState.Name' --output text
