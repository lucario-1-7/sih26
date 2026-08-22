from fastapi import APIRouter, HTTPException, Query, status

from app.services import otp_dev_store

# Mounted only when settings.ENVIRONMENT == "development" — see
# app/main.py::create_app. `otp_dev_store.get_dev_otp` also independently
# returns None outside development, so this 404s even if ever mounted
# elsewhere by mistake.
router = APIRouter(prefix="/auth/dev", tags=["auth-dev"])

NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail={"detail": "No OTP on record for this phone", "code": "NOT_FOUND"},
)


@router.get("/otp", summary="Development only: retrieve the latest requested OTP for a phone number")
async def get_dev_otp(phone: str = Query(..., min_length=8, max_length=20)) -> dict:
    code = otp_dev_store.get_dev_otp(phone)
    if code is None:
        raise NOT_FOUND
    return {"phone": phone, "code": code}
