from app.schemas import CamelModel


class ConfigCreate(CamelModel):
    config_name: str = ""
    config_key: str = ""
    config_value: str = ""
    config_type: str = "N"
    remark: str | None = None


class ConfigUpdate(CamelModel):
    config_id: int
    config_name: str | None = None
    config_key: str | None = None
    config_value: str | None = None
    config_type: str | None = None
    remark: str | None = None
