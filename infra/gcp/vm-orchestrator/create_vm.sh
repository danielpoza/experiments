#!/usr/bin/env bash
set -e

PROJECT_ID=${PROJECT_ID:-mi-sandbox}
ZONE=${ZONE:-europe-southwest1-b}
VM_NAME=${VM_NAME:-pz-foscam-gateway}

gcloud config set project "$PROJECT_ID"

gcloud compute instances create "$VM_NAME" \
  --zone="$ZONE" \
  --machine-type=e2-micro \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --tags=foscam-ftp \
  --scopes=https://www.googleapis.com/auth/devstorage.read_write
