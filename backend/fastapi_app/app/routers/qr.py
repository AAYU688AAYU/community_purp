from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import qrcode
import io
import base64
from datetime import datetime, timedelta
import jwt
from ..utils.auth import get_current_user

router = APIRouter()

class QRCodeRequest(BaseModel):
    flat_number: str
    block_number: str
    purpose: str
    expiry_hours: Optional[int] = 24
    instructions: Optional[str] = None

class QRCodeResponse(BaseModel):
    qr_code: str
    token: str
    expiry_date: datetime

@router.post("/generate", response_model=QRCodeResponse)
async def generate_qr_code(request: QRCodeRequest, current_user: dict = Depends(get_current_user)):
    try:
        # Create QR code data
        expiry_date = datetime.utcnow() + timedelta(hours=request.expiry_hours)
        qr_data = {
            "flat_number": request.flat_number,
            "block_number": request.block_number,
            "purpose": request.purpose,
            "instructions": request.instructions,
            "generated_by": current_user["email"],
            "expiry_date": expiry_date.isoformat(),
        }

        # Generate JWT token for QR data
        token = jwt.encode(qr_data, "your-secret-key", algorithm="HS256")

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(token)
        qr.make(fit=True)

        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert image to base64
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        qr_code_base64 = base64.b64encode(img_byte_arr).decode()

        return {
            "qr_code": f"data:image/png;base64,{qr_code_base64}",
            "token": token,
            "expiry_date": expiry_date
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/validate/{token}")
async def validate_qr_code(token: str):
    try:
        # Decode and verify token
        payload = jwt.decode(token, "your-secret-key", algorithms=["HS256"])
        
        # Check if QR code has expired
        expiry_date = datetime.fromisoformat(payload["expiry_date"])
        if datetime.utcnow() > expiry_date:
            raise HTTPException(status_code=400, detail="QR code has expired")

        return {
            "valid": True,
            "data": payload
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="QR code has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid QR code")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 