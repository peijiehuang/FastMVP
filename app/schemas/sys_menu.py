from app.schemas import CamelModel


class MenuCreate(CamelModel):
    menu_name: str
    parent_id: int = 0
    order_num: int = 0
    path: str = ""
    component: str | None = None
    query: str | None = None
    route_name: str = ""
    is_frame: int = 1
    is_cache: int = 0
    menu_type: str = ""
    visible: str = "0"
    status: str = "0"
    perms: str | None = None
    icon: str = "#"


class MenuUpdate(CamelModel):
    menu_id: int
    menu_name: str | None = None
    parent_id: int | None = None
    order_num: int | None = None
    path: str | None = None
    component: str | None = None
    query: str | None = None
    route_name: str | None = None
    is_frame: int | None = None
    is_cache: int | None = None
    menu_type: str | None = None
    visible: str | None = None
    status: str | None = None
    perms: str | None = None
    icon: str | None = None
