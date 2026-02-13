from app.schemas import CamelModel


class DictTypeCreate(CamelModel):
    dict_name: str = ""
    dict_type: str = ""
    status: str = "0"
    remark: str | None = None


class DictTypeUpdate(CamelModel):
    dict_id: int
    dict_name: str | None = None
    dict_type: str | None = None
    status: str | None = None
    remark: str | None = None


class DictDataCreate(CamelModel):
    dict_sort: int = 0
    dict_label: str = ""
    dict_value: str = ""
    dict_type: str = ""
    css_class: str | None = None
    list_class: str | None = None
    is_default: str = "N"
    status: str = "0"
    remark: str | None = None


class DictDataUpdate(CamelModel):
    dict_code: int
    dict_sort: int | None = None
    dict_label: str | None = None
    dict_value: str | None = None
    dict_type: str | None = None
    css_class: str | None = None
    list_class: str | None = None
    is_default: str | None = None
    status: str | None = None
    remark: str | None = None
