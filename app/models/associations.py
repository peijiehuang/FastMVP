from sqlalchemy import BigInteger, Column, Table, ForeignKey

from app.models.base import Base

# User-Role association
sys_user_role = Table(
    "sys_user_role",
    Base.metadata,
    Column("user_id", BigInteger, ForeignKey("sys_user.user_id"), primary_key=True),
    Column("role_id", BigInteger, ForeignKey("sys_role.role_id"), primary_key=True),
)

# User-Post association
sys_user_post = Table(
    "sys_user_post",
    Base.metadata,
    Column("user_id", BigInteger, ForeignKey("sys_user.user_id"), primary_key=True),
    Column("post_id", BigInteger, ForeignKey("sys_post.post_id"), primary_key=True),
)

# Role-Menu association
sys_role_menu = Table(
    "sys_role_menu",
    Base.metadata,
    Column("role_id", BigInteger, ForeignKey("sys_role.role_id"), primary_key=True),
    Column("menu_id", BigInteger, ForeignKey("sys_menu.menu_id"), primary_key=True),
)

# Role-Dept association
sys_role_dept = Table(
    "sys_role_dept",
    Base.metadata,
    Column("role_id", BigInteger, ForeignKey("sys_role.role_id"), primary_key=True),
    Column("dept_id", BigInteger, ForeignKey("sys_dept.dept_id"), primary_key=True),
)
