from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import OtpRequestIn, OtpVerifyIn, RefreshIn, TokenPair
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/otp/request", status_code=status.HTTP_202_ACCEPTED, summary="Request a login OTP")
async def request_otp(
    payload: OtpRequestIn, request: Request, db: AsyncSession = Depends(get_db)
) -> dict:
    await auth_service.request_otp(db, phone=payload.phone, ip_address=request.client.host if request.client else None)
    return {"detail": "OTP sent"}


@router.post("/otp/verify", response_model=TokenPair, summary="Verify OTP and receive tokens")
async def verify_otp(
    payload: OtpVerifyIn, request: Request, db: AsyncSession = Depends(get_db)
) -> TokenPair:
    return await auth_service.verify_otp(
        db, phone=payload.phone, code=payload.code, ip_address=request.client.host if request.client else None
    )


@router.post("/refresh", response_model=TokenPair, summary="Exchange a refresh token for a new token pair")
async def refresh(payload: RefreshIn, db: AsyncSession = Depends(get_db)) -> TokenPair:
    return await auth_service.refresh_tokens(db, refresh_token=payload.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Revoke a refresh token")
async def logout(payload: RefreshIn, current_user: User = Depends(get_current_user)) -> None:
    await auth_service.logout(user_id=current_user.id, refresh_token=payload.refresh_token)
