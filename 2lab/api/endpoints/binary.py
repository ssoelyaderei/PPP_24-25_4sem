from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import base64
from io import BytesIO
from PIL import Image
import cv2
import numpy as np

from app.core.security import verify_token
from app.schemas.binary import BinaryRequest, BinaryResponse
from app.services.image_processing import binarize_image

router = APIRouter()
security = HTTPBearer()


@router.post("/binary_image")
async def binary_image(
        request: BinaryRequest,
        credentials: HTTPAuthorizationCredentials = Depends(security)
):
    email = verify_token(credentials.credentials)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        image_data = base64.b64decode(request.image)
        image = Image.open(BytesIO(image_data))
        img_array = np.array(image)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")

    try:
        binarized = binarize_image(img_array, request.algorithm)
        _, buffer = cv2.imencode('.png', binarized)
        binarized_base64 = base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Binarization error: {str(e)}")

    return BinaryResponse(binarized_image=binarized_base64)