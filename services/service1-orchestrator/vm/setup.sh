#!/usr/bin/env bash
set -e

########################################
# Configuración
########################################

PROJECT_ID="${PROJECT_ID:-mi-sandbox}"
BUCKET_NAME="${BUCKET_NAME:-pz-foscam-images}"
CAMERA_USER="${CAMERA_USER:-foscam}"
CAMERA_PASSWORD="${CAMERA_PASSWORD:-Foscam123!}"  # cámbialo luego
UPLOAD_DIR="/home/${CAMERA_USER}/uploads"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

echo "[setup] Project:      ${PROJECT_ID}"
echo "[setup] Bucket:       ${BUCKET_NAME}"
echo "[setup] Camera user:  ${CAMERA_USER}"
echo "[setup] Repo dir:     ${REPO_DIR}"

########################################
# Paquetes base
########################################

echo "[setup] Instalando paquetes..."
apt-get update -y
apt-get install -y vsftpd python3 python3-pip

########################################
# Usuario y carpeta para la cámara
########################################

if ! id "${CAMERA_USER}" &>/dev/null; then
  echo "[setup] Creando usuario ${CAMERA_USER}..."
  useradd -m "${CAMERA_USER}"
  echo "${CAMERA_USER}:${CAMERA_PASSWORD}" | chpasswd
fi

mkdir -p "${UPLOAD_DIR}"
chown -R "${CAMERA_USER}:${CAMERA_USER}" "${UPLOAD_DIR}"

########################################
# Configuración vsftpd
########################################

echo "[setup] Configurando vsftpd..."

cat >/etc/vsftpd.conf <<EOF
listen=YES
listen_ipv6=NO
anonymous_enable=NO
local_enable=YES
write_enable=YES
chroot_local_user=YES
allow_writeable_chroot=YES
local_umask=022

# Solo este usuario (cámara)
user_sub_token=\$USER
local_root=/home/\$USER/uploads

# Modo pasivo para NAT
pasv_enable=YES
pasv_min_port=30000
pasv_max_port=30010

ftpd_banner=Foscam FTP Server ready.
EOF

systemctl restart vsftpd
systemctl enable vsftpd

echo "[setup] vsftpd listo. Recibirá archivos en ${UPLOAD_DIR}"

########################################
# Dependencias Python
########################################

echo "[setup] Instalando librerías Python..."
pip3 install --upgrade pip
pip3 install google-cloud-storage watchdog

########################################
# systemd service para orchestrator
########################################

echo "[setup] Configurando servicio foscam-orchestrator..."

cat >/etc/systemd/system/foscam-orchestrator.service <<EOF
[Unit]
Description=Foscam Orchestrator - FTP -> GCS
After=network-online.target

[Service]
User=${CAMERA_USER}
Environment=PROJECT_ID=${PROJECT_ID}
Environment=BUCKET_NAME=${BUCKET_NAME}
Environment=CAMERA_ID=c2m-default
WorkingDirectory=${REPO_DIR}/services/service1-orchestrator/vm
ExecStart=/usr/bin/python3 ${REPO_DIR}/services/service1-orchestrator/vm/orchestrator.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable foscam-orchestrator
systemctl start foscam-orchestrator

echo "[setup] Servicio foscam-orchestrator activo."
echo "[setup] Setup completo."
