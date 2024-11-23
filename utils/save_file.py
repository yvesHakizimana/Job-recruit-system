import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile, HTTPException

UPLOAD_DIR = Path('uploads')


def save_file(file: UploadFile, user_id: str, file_type: str) -> str:
    try:
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"{file_type}_{str(uuid.uuid4())}.{file_extension}"

        user_dir = UPLOAD_DIR / user_id
        user_dir.mkdir(parents=True, exist_ok=True)

        # Full path of saving the file
        file_path = user_dir / unique_filename

        # Save the file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_url = f"/files/{user_id}/{unique_filename}"
        return file_url

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Saving the file: {str(e)}")
