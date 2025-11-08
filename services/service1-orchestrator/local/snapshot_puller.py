import os
import time
import datetime as dt
from pathlib import Path

import requests
from google.cloud import storage

# Configura estos valores:
CAMERA_URL = os.getenv(
    "CAMERA_URL",
    "http://192.168.68.54:88/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr=danielpoza@gmail.com&pwd=Depper0y."
)
PROJECT_ID = os.getenv("PROJECT_ID", "mi-sandbox")
BUCKET_NAME = os.getenv("BUCKET_NAME", "pz-foscam-images")
CAMERA_ID = os.getenv("CAMERA_ID", "c2m-default")
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "10"))

storage_client = storage.Client(project=PROJECT_ID)
bucket = storage_client.bucket(BUCKET_NAME)

def build_blob_name() -> str:
    now = dt.datetime.utcnow()
    yyyy = now.strftime("%Y")
    mm = now.strftime("%m")
    dd = now.strftime("%d")
    ts_ms = int(now.timestamp() * 1000)
    return f"raw/{CAMERA_ID}/{yyyy}/{mm}/{dd}/{ts_ms}.jpg"

def main():
    print(f"[puller] Iniciando. Subiendo cada {INTERVAL_SECONDS}s a gs://{BUCKET_NAME}")
    while True:
        try:
            resp = requests.get(CAMERA_URL, timeout=5)
            if resp.status_code == 200 and resp.content:
                blob_name = build_blob_name()
                blob = bucket.blob(blob_name)
                blob.upload_from_string(resp.content, content_type="image/jpeg")
                print(f"[puller] Subida: gs://{BUCKET_NAME}/{blob_name}")
            else:
                print(f"[puller] ERROR HTTP {resp.status_code} al pedir snapshot")
        except Exception as e:
            print(f"[puller] EXCEPCIÓN: {e}")

        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
