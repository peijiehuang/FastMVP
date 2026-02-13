"""Data scope filtering for role-based data permissions."""

from sqlalchemy import Select, or_, select

from app.core.constants import DataScope
from app.models.associations import sys_role_dept
from app.models.sys_dept import SysDept
from app.models.sys_user import SysUser


def apply_data_scope(
    query: Select,
    user: dict,
    dept_alias=None,
    user_alias=None,
) -> Select:
    """Apply data permission filter based on user's role data_scope.

    Args:
        query: The base SQLAlchemy select query
        user: The current user dict (from Redis LoginUser)
        dept_alias: Optional dept model alias for filtering
        user_alias: Optional user model alias for filtering
    """
    roles = user.get("roles_info", [])
    if not roles:
        # If no roles_info, check if user is admin
        if "admin" in user.get("roles", []):
            return query
        # Default: self only
        user_col = user_alias or SysUser
        return query.where(user_col.user_id == user["user_id"])

    conditions = []
    for role in roles:
        scope = role.get("data_scope", DataScope.SELF)

        if scope == DataScope.ALL:
            return query  # No filter needed

        dept_col = dept_alias or SysDept
        user_col = user_alias or SysUser
        user_dept_id = user.get("dept_id")

        if scope == DataScope.CUSTOM:
            conditions.append(
                dept_col.dept_id.in_(
                    select(sys_role_dept.c.dept_id).where(
                        sys_role_dept.c.role_id == role["role_id"]
                    )
                )
            )
        elif scope == DataScope.DEPT:
            if user_dept_id:
                conditions.append(dept_col.dept_id == user_dept_id)
        elif scope == DataScope.DEPT_AND_CHILD:
            if user_dept_id:
                conditions.append(
                    or_(
                        dept_col.dept_id == user_dept_id,
                        dept_col.ancestors.like(f"%,{user_dept_id},%"),
                        dept_col.ancestors.like(f"%,{user_dept_id}"),
                    )
                )
        elif scope == DataScope.SELF:
            conditions.append(user_col.user_id == user["user_id"])

    if conditions:
        query = query.where(or_(*conditions))

    return query
