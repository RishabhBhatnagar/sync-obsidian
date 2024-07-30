import hashlib
import os
from typing import Iterable

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from model import File, OBSIDIAN_BASE_PATH, directory_map


def get_gdrive_svc():
    creds, _ = google.auth.load_credentials_from_file(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), 'gcloud-creds.json')
    )
    service = build("drive", "v3", credentials=creds)
    return service


def upload_file(file: File):
    fname = os.path.basename(file.path)

    try:
        # create drive api client
        file_metadata = {"name": fname, "parents": [file.gdrive_path]}
        media = MediaFileUpload(file.path)
        file = (
            get_gdrive_svc().files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None

    return file.get("id")


def list_gdrive_files() -> Iterable[File]:
    # list files in the google-drive
    for dir_name, drive_id in directory_map.items():
        get_files_response = get_gdrive_svc().files().list(
            q=f"'{drive_id}' in parents",
            fields="files({})".format(','.join(('name', 'md5Checksum')))
        ).execute()

        files = get_files_response.get("files", [])
        for file in files:
            yield File(f'{dir_name}/{file.get("name")}' if dir_name else file.get('name'), file.get("md5Checksum"))


def list_dir_files(folder_path) -> Iterable[File]:
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            abs_path = str(os.path.join(root, file))
            with open(abs_path, mode='rb') as f:
                md5_checksum = hashlib.md5(f.read()).hexdigest()
                yield File(abs_path, md5_checksum)


def sync(vault_path: str):
    """
    :param vault_path: directory path on the local system where all the files are stored
    """
    # Step 1: list all the files in the gdrive
    gdrive_files = list(list_gdrive_files())
    gdrive_hash_map = {f.md5_checksum: f for f in gdrive_files}

    # Step 2: list all the local files in the vault
    local_files = list(list_dir_files(vault_path))
    uploaded_files = [f for f in local_files if f.md5_checksum in gdrive_hash_map]
    not_uploaded_files = [f for f in local_files if f.md5_checksum not in gdrive_hash_map]
    print("Uploaded files:", uploaded_files)

    # Step 3: Upload all the not_uploaded files
    for file in not_uploaded_files:
        file_id = upload_file(file)
        print(f'{file.path} uploaded with id: {file_id}')


if __name__ == "__main__":
    sync(OBSIDIAN_BASE_PATH)
