from app.schemas import CamelModel


class NoticeCreate(CamelModel):
    notice_title: str
    notice_type: str
    notice_content: str | None = None
    status: str = "0"
    remark: str | None = None


class NoticeUpdate(CamelModel):
    notice_id: int
    notice_title: str | None = None
    notice_type: str | None = None
    notice_content: str | None = None
    status: str | None = None
    remark: str | None = None
