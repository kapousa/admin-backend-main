import os

from fastapi import UploadFile, File, APIRouter, HTTPException
import uuid
from starlette.responses import FileResponse

router = APIRouter() #create a router

# @router.post("/admin/upload/")
# async def upload_file(file: UploadFile = File(...)):
#     file_id = str(uuid.uuid4())
#     file_path = f"uploads/{file_id}_{file.filename}"
#     with open(file_path, "wb") as buffer:
#         buffer.write(await file.read())
#
#     file_url = f"/files/{file_id}_{file.filename}"
#
#     return {"filename": file.filename, "file_url": file_url, "file_type": file.content_type}

@router.post("/admin/upload/")
async def upload_file(file: UploadFile = File(...)):
    BASE_URL = os.getenv("API_BASE_URL")
    ALLOWED_FILE_TYPES = ["image/jpeg", "image/png", "application/pdf"]  # Example.
    UPLOAD_DIR = "uploads"
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type")

    try:
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        file_url = f"{BASE_URL}/files/{file_id}_{file.filename}"

        return {"filename": file.filename, "file_url": file_url, "file_type": file.content_type}
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


@router.get("/files/{file_path:path}")
async def get_file(file_path: str):
    return FileResponse(f"uploads/{file_path}")