#!/usr/bin/env bash
set -e

PROJECT_ID=${PROJECT_ID:-mi-sandbox}
BUCKET_NAME=${BUCKET_NAME:-pz-foscam-images}
REGION=${REGION:-europe-southwest1}

gcloud config set project "$PROJECT_ID"
gsutil mb -p "$PROJECT_ID" -l "$REGION" "gs://${BUCKET_NAME}"
