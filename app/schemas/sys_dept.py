from app.schemas import CamelModel


class DeptCreate(CamelModel):
    parent_id: int = 0
    dept_name: str
    order_num: int = 0
    leader: str | None = None
    phone: str | None = None
    email: str | None = None
    status: str = "0"


class DeptUpdate(CamelModel):
    dept_id: int
    parent_id: int | None = None
    dept_name: str | None = None
    order_num: int | None = None
    leader: str | None = None
    phone: str | None = None
    email: str | None = None
    status: str | None = None
