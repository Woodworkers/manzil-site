#!/usr/bin/env python3
import os, io, json, sys, base64, pathlib, re
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID", "").strip()
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "public/images").strip()
SA_JSON_B64 = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
MIRROR = os.environ.get("MIRROR", "true").lower() == "true"

if not FOLDER_ID:
    print("ERROR: DRIVE_FOLDER_ID env var is required", file=sys.stderr)
    sys.exit(1)
if not SA_JSON_B64:
    print("ERROR: GOOGLE_SERVICE_ACCOUNT_JSON env var is required (base64 of service account key json)", file=sys.stderr)
    sys.exit(1)

key_bytes = base64.b64decode(SA_JSON_B64)
creds = service_account.Credentials.from_service_account_info(
    json.loads(key_bytes.decode("utf-8")),
    scopes=["https://www.googleapis.com/auth/drive.readonly"],
)

service = build("drive", "v3", credentials=creds)
pathlib.Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# List images in folder
q = f"'{FOLDER_ID}' in parents and mimeType contains 'image/' and trashed = false"
files = []
page_token = None
while True:
    resp = service.files().list(
        q=q,
        fields="nextPageToken, files(id, name, mimeType, modifiedTime)",
        pageToken=page_token,
    ).execute()
    files.extend(resp.get("files", []))
    page_token = resp.get("nextPageToken")
    if not page_token: break

def sanitize(name: str) -> str:
    name = re.sub(r'[^A-Za-z0-9._-]+', '-', name).strip('-')
    return name or "image"

wanted = set()
for f in files:
    file_id = f["id"]
    name = sanitize(f["name"])
    out_path = os.path.join(OUTPUT_DIR, name)
    wanted.add(name)

    req = service.files().get_media(fileId=file_id)
    fh = io.FileIO(out_path, "wb")
    downloader = MediaIoBaseDownload(fh, req)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.close()
    print(f"Downloaded: {name}")

# Mirror behavior: remove any local files not present in Drive
if MIRROR:
    for local in os.listdir(OUTPUT_DIR):
        if local not in wanted:
            os.remove(os.path.join(OUTPUT_DIR, local))
            print(f"Removed stale: {local}")

# Create a simple manifest
manifest = {
    "folder_id": FOLDER_ID,
    "count": len(files),
    "files": sorted(list(wanted))
}
with open(os.path.join(OUTPUT_DIR, "manifest.json"), "w", encoding="utf-8") as mf:
    json.dump(manifest, mf, indent=2, ensure_ascii=False)

print(json.dumps(manifest, indent=2, ensure_ascii=False))
