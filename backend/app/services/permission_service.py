from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission


class VerifiedPermission:
    """Represents a verified permission grant for a user at a specific node."""

    def __init__(self, permission: Permission):
        self._perm = permission

    @property
    def node_id(self) -> str:
        return self._perm.node_id

    @property
    def user_id(self) -> str:
        return self._perm.user_id

    def has(self, flag_name: str) -> bool:
        return getattr(self._perm, flag_name, False)


async def verify_permission(
    db: AsyncSession,
    user_id: str,
    node_id: str,
    required_flag: str | None = None,
) -> VerifiedPermission | None:
    """
    Load the Permission row for (user_id, node_id) and verify that:
    1. is_data_verified = true
    2. is_active = true
    3. The required is_* flag is true (if specified)

    Returns a VerifiedPermission object or None if verification fails.
    """
    result = await db.execute(
        select(Permission).where(
            and_(
                Permission.user_id == user_id,
                Permission.node_id == node_id,
                Permission.is_active == True,
                Permission.is_data_verified == True,
            )
        )
    )
    perm = result.scalar_one_or_none()

    if perm is None:
        return None

    if required_flag and not getattr(perm, required_flag, False):
        return None

    return VerifiedPermission(perm)


async def get_user_node_ids_with_flag(
    db: AsyncSession,
    user_id: str,
    flag_name: str,
) -> list[str]:
    """Return all node_ids where the user has the specified is_* flag set to true."""
    result = await db.execute(
        select(Permission.node_id).where(
            and_(
                Permission.user_id == user_id,
                Permission.is_active == True,
                Permission.is_data_verified == True,
                getattr(Permission, flag_name) == True,
            )
        )
    )
    return [row[0] for row in result.all()]
