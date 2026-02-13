from app.schemas import CamelModel


class UserCreate(CamelModel):
    dept_id: int | None = None
    user_name: str
    nick_name: str
    password: str = ""
    email: str = ""
    phonenumber: str = ""
    sex: str = "0"
    status: str = "0"
    remark: str | None = None
    post_ids: list[int] = []
    role_ids: list[int] = []


class UserUpdate(CamelModel):
    user_id: int
    dept_id: int | None = None
    nick_name: str | None = None
    email: str | None = None
    phonenumber: str | None = None
    sex: str | None = None
    status: str | None = None
    remark: str | None = None
    post_ids: list[int] = []
    role_ids: list[int] = []


class UserQuery(CamelModel):
    user_name: str | None = None
    phonenumber: str | None = None
    status: str | None = None
    dept_id: int | None = None
    begin_time: str | None = None
    end_time: str | None = None


class ResetPwdBody(CamelModel):
    user_id: int
    password: str


class ChangeStatusBody(CamelModel):
    user_id: int
    status: str


class UserProfileUpdate(CamelModel):
    nick_name: str | None = None
    email: str | None = None
    phonenumber: str | None = None
    sex: str | None = None


class UpdatePwdQuery(CamelModel):
    old_password: str = ""
    new_password: str = ""
