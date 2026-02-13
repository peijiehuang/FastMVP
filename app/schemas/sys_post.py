from app.schemas import CamelModel


class PostCreate(CamelModel):
    post_code: str
    post_name: str
    post_sort: int = 0
    status: str = "0"
    remark: str | None = None


class PostUpdate(CamelModel):
    post_id: int
    post_code: str | None = None
    post_name: str | None = None
    post_sort: int | None = None
    status: str | None = None
    remark: str | None = None
