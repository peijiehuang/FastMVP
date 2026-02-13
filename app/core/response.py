from typing import Any

from pydantic import BaseModel


class AjaxResult(BaseModel):
    """Standard response compatible with RuoYi frontend.

    RuoYi frontend checks `res.code !== 200` to determine errors.
    """

    code: int = 200
    msg: str = "操作成功"
    data: Any = None

    model_config = {"extra": "allow"}

    @classmethod
    def success(cls, msg: str = "操作成功", data: Any = None, **kwargs) -> dict:
        result = {"code": 200, "msg": msg}
        if data is not None:
            result["data"] = data
        result.update(kwargs)
        return result

    @classmethod
    def error(cls, msg: str = "操作失败", code: int = 500) -> dict:
        return {"code": code, "msg": msg}


class TableDataInfo(BaseModel):
    """Paginated list response compatible with RuoYi frontend."""

    code: int = 200
    msg: str = "查询成功"
    total: int = 0
    rows: list[Any] = []
