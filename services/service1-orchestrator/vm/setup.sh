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
VENV_DIR="/home/${CAMERA_USER}/venv"

echo "[setup] Project:      ${PROJECT_ID}"
echo "[setup] Bucket:       ${BUCKET_NAME}"
echo "[setup] Camera user:  ${CAMERA_USER}"
echo "[setup] Repo dir:     ${REPO_DIR}"
echo "[setup] Venv dir:     ${VENV_DIR}"

########################################
# Paquetes base
########################################

echo "[setup] Instalando paquetes..."
apt-get update -y
apt-get install -y vsftpd python3 python3-venv

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

user_sub_token=\$USER
local_root=/home/\$USER/uploads

pasv_enable=YES
pasv_min_port=30000
pasv_max_port=30010

ftpd_banner=Foscam FTP Server ready.
EOF

systemctl restart vsftpd
systemctl enable vsftpd

echo "[setup] vsftpd listo. Recibirá archivos en ${UPLOAD_DIR}"

########################################
# Virtualenv para el orchestrator
########################################

echo "[setup] Creando virtualenv para ${CAMERA_USER}..."

# Crear venv como el usuario foscam
sudo -u "${CAMERA_USER}" bash <<EOF
if [ ! -d "${VENV_DIR}" ]; then
  python3 -m venv "${VENV_DIR}"
fi
"${VENV_DIR}/bin/pip" install --upgrade pip
"${VENV_DIR}/bin/pip" install google-cloud-storage watchdog
EOF

echo "[setup] Virtualenv con dependencias instalado."

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
ExecStart=${VENV_DIR}/bin/python ${REPO_DIR}/services/service1-orchestrator/vm/orchestrator.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable foscam-orchestrator
systemctl restart foscam-orchestrator

echo "[setup] Servicio foscam-orchestrator activo."
echo "[setup] Setup completo."
