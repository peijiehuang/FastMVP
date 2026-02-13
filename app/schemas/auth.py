from pydantic import BaseModel, ConfigDict

from app.schemas import CamelModel


class LoginBody(BaseModel):
    username: str
    password: str
    code: str = ""
    uuid: str = ""


class LoginUser(CamelModel):
    """User info cached in Redis after login."""
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    dept_id: int | None = None
    user_name: str
    nick_name: str
    user_type: str = "00"
    email: str = ""
    phonenumber: str = ""
    sex: str = "0"
    avatar: str = ""
    status: str = "0"

    # Runtime info
    login_ip: str = ""
    login_time: str = ""
    token_key: str = ""  # UUID key for Redis

    # Permissions and roles
    permissions: list[str] = []
    roles: list[str] = []  # role keys

    # Department info
    dept_name: str = ""
