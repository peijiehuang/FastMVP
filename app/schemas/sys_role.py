from app.schemas import CamelModel


class RoleCreate(CamelModel):
    role_name: str
    role_key: str
    role_sort: int = 0
    data_scope: str = "1"
    menu_check_strictly: bool = True
    dept_check_strictly: bool = True
    status: str = "0"
    remark: str | None = None
    menu_ids: list[int] = []


class RoleUpdate(CamelModel):
    role_id: int
    role_name: str | None = None
    role_key: str | None = None
    role_sort: int | None = None
    status: str | None = None
    remark: str | None = None
    menu_check_strictly: bool | None = None
    dept_check_strictly: bool | None = None
    menu_ids: list[int] = []


class RoleDataScope(CamelModel):
    role_id: int
    data_scope: str
    dept_ids: list[int] = []


class RoleChangeStatus(CamelModel):
    role_id: int
    status: str


class RoleQuery(CamelModel):
    role_name: str | None = None
    role_key: str | None = None
    status: str | None = None
    begin_time: str | None = None
    end_time: str | None = None


class AuthUserBody(CamelModel):
    user_id: int
    role_id: int


class AuthUserCancelAll(CamelModel):
    role_id: int
    user_ids: str = ""  # comma-separated
