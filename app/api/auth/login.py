from fastapi import APIRouter, Depends, Request
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.constants import CAPTCHA_CODE_KEY
from app.core.deps import get_current_user
from app.core.redis import get_redis
from app.core.response import AjaxResult
from app.core.security import parse_token
from app.db.session import get_db
from app.schemas.auth import LoginBody
from app.services import auth_service
from app.utils.captcha import generate_captcha

router = APIRouter(tags=["认证管理"])


@router.get("/captchaImage")
async def get_captcha(redis: aioredis.Redis = Depends(get_redis)):
    """Generate captcha image."""
    enabled = settings.CAPTCHA_ENABLED
    if not enabled:
        return AjaxResult.success(
            captchaEnabled=False,
        )

    captcha_uuid, code, img = generate_captcha()

    # Store code in Redis
    await redis.setex(
        f"{CAPTCHA_CODE_KEY}{captcha_uuid}",
        settings.CAPTCHA_EXPIRE_SECONDS,
        code,
    )

    return AjaxResult.success(
        captchaEnabled=True,
        uuid=captcha_uuid,
        img=img,
    )


@router.post("/login")
async def login(
    body: LoginBody,
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    """User login."""
    login_ip = request.client.host if request.client else "127.0.0.1"
    token = await auth_service.login(
        username=body.username,
        password=body.password,
        code=body.code,
        captcha_uuid=body.uuid,
        login_ip=login_ip,
        db=db,
        redis=redis,
    )
    return AjaxResult.success(token=token)


@router.post("/logout")
async def logout(
    request: Request,
    current_user: dict = Depends(get_current_user),
    redis: aioredis.Redis = Depends(get_redis),
):
    """User logout."""
    token_key = current_user.get("token_key", "")
    if token_key:
        await auth_service.logout(token_key, redis)
    return AjaxResult.success(msg="退出成功")
