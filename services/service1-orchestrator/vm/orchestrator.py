import os
import time
import datetime as dt
from pathlib import Path

from google.cloud import storage
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

PROJECT_ID = os.getenv("PROJECT_ID", "mi-sandbox")
BUCKET_NAME = os.getenv("BUCKET_NAME", "pz-foscam-images")
CAMERA_ID = os.getenv("CAMERA_ID", "c2m-default")

# Intentamos deducir usuario (por si cambia en el futuro)
camera_user = os.getenv("CAMERA_USER", "foscam")
UPLOAD_DIR = Path(f"/home/{camera_user}/uploads")
if not UPLOAD_DIR.exists():
    UPLOAD_DIR = Path("/home/foscam/uploads")

print(f"[orchestrator] Project: {PROJECT_ID}")
print(f"[orchestrator] Bucket:  {BUCKET_NAME}")
print(f"[orchestrator] Camera:  {CAMERA_ID}")
print(f"[orchestrator] Watching: {UPLOAD_DIR}")

storage_client = storage.Client(project=PROJECT_ID)
bucket = bucket = storage_client.bucket(BUCKET_NAME)


def build_blob_name(local_path: Path) -> str:
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
        time.sleep(0.2)  # margen mientras la cámara termina de escribir

        if not path.exists():
            return

        ext = path.suffix.lower()
        if ext not in [".jpg", ".jpeg", ".png"]:
            return

        blob_name = build_blob_name(path)
        print(f"[orchestrator] New image: {path} -> {blob_name}")

        try:
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(str(path), content_type="image/jpeg")
            print(f"[orchestrator] Uploaded: gs://{BUCKET_NAME}/{blob_name}")

            # Aquí en el futuro:
            # send_to_service2(image_uri=f"gs://{BUCKET_NAME}/{blob_name}", camera_id=CAMERA_ID)

            try:
                path.unlink()
            except Exception as e:
                print(f"[orchestrator] WARN no se pudo borrar {path}: {e}")

        except Exception as e:
            print(f"[orchestrator] ERROR subiendo {path}: {e}")


def main():
    if not UPLOAD_DIR.exists():
        print(f"[orchestrator] ERROR: Upload dir {UPLOAD_DIR} no existe")
        return

    handler = ImageHandler()
    observer = Observer()
    observer.schedule(handler, str(UPLOAD_DIR), recursive=False)
    observer.start()
    print("[orchestrator] Running. Waiting for images...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
