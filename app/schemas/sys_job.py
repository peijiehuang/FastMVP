from typing import Annotated

from pydantic import BeforeValidator

from app.schemas import CamelModel

# Frontend sends these as int, DB stores as str
StrOrInt = Annotated[str, BeforeValidator(lambda v: str(v))]


class JobCreate(CamelModel):
    job_name: str
    job_group: str = "DEFAULT"
    invoke_target: str
    cron_expression: str
    misfire_policy: StrOrInt = "3"
    concurrent: StrOrInt = "1"
    status: StrOrInt = "0"
    remark: str | None = None


class JobUpdate(CamelModel):
    job_id: int
    job_name: str | None = None
    job_group: str | None = None
    invoke_target: str | None = None
    cron_expression: str | None = None
    misfire_policy: StrOrInt | None = None
    concurrent: StrOrInt | None = None
    status: StrOrInt | None = None
    remark: str | None = None


class JobStatusChange(CamelModel):
    job_id: int
    status: StrOrInt


class JobRun(CamelModel):
    job_id: int
    job_group: str
