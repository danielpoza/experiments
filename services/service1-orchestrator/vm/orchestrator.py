import os
import time
import datetime as dt
from pathlib import Path

from google.cloud import storage
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Config desde entorno
PROJECT_ID = os.getenv("PROJECT_ID", "mi-sandbox")
BUCKET_NAME = os.getenv("BUCKET_NAME", "pz-foscam-images")
CAMERA_ID = os.getenv("CAMERA_ID", "c2m-default")
UPLOAD_DIR = Path(f"/home/{os.getenv('CAMERA_USER', 'foscam')}/uploads")

# Si quieres forzar ruta exacta:
if not UPLOAD_DIR.exists():
    # fallback sensato
    UPLOAD_DIR = Path("/home/foscam/uploads")

print(f"[orchestrator] Project: {PROJECT_ID}")
print(f"[orchestrator] Bucket:  {BUCKET_NAME}")
print(f"[orchestrator] Camera:  {CAMERA_ID}")
print(f"[orchestrator] Watching: {UPLOAD_DIR}")

storage_client = storage.Client(project=PROJECT_ID)
bucket = storage_client.bucket(BUCKET_NAME)


def build_blob_name(local_path: Path) -> str:
    """Convención de path en GCS:
    gs://BUCKET/raw/{camera_id}/YYYY/MM/DD/{ts_ms}_{filename}
    """
    now = dt.datetime.utcnow()
    yyyy = now.strftime("%Y")
    mm = now.strftime("%m")
    dd = now.strftime("%d")
    ts_ms = int(time.time() * 1000)
    return f"raw/{CAMERA_ID}/{yyyy}/{mm}/{dd}/{ts_ms}_{local_path.name}"


class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        path = Path(event.src_path)

        # esperamos un pelín por si la cámara sigue escribiendo
        time.sleep(0.2)

        ext = path.suffix.lower()
        if ext not in [".jpg", ".jpeg", ".png"]:
            return

        if not path.exists():
            return

        blob_name = build_blob_name(path)
        print(f"[orchestrator] New image detected: {path} -> {blob_name}")

        try:
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(str(path), content_type="image/jpeg")
            print(f"[orchestrator] Uploaded to gs://{BUCKET_NAME}/{blob_name}")

            # FUTURO: llamar a Service 2 (Cloud Run) con el evento
            # send_to_service2(
            #     image_uri=f"gs://{BUCKET_NAME}/{blob_name}",
            #     camera_id=CAMERA_ID
            # )

            # Limpieza local tras subir
            try:
                path.unlink()
            except Exception as e:
                print(f"[orchestrator] WARN: no se pudo borrar {path}: {e}")

        except Exception as e:
            print(f"[orchestrator] ERROR subiendo {path}: {e}")


def main():
    if not UPLOAD_DIR.exists():
        print(f"[orchestrator] ERROR: Upload dir {UPLOAD_DIR} no existe")
        return

    event_handler = ImageHandler()
    observer = Observer()
    observer.schedule(event_handler, str(UPLOAD_DIR), recursive=False)
    observer.start()
    print("[orchestrator] Iniciado. Esperando imágenes FTP...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
