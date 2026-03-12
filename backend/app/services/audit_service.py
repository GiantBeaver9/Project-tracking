import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog


async def log_audit(
    db: AsyncSession,
    *,
    user_id: str | None,
    node_id: str | None,
    action: str,
    table_name: str,
    record_id: str,
    old_value: dict | None = None,
    new_value: dict | None = None,
    ip_address: str | None = None,
) -> None:
    entry = AuditLog(
        user_id=user_id,
        node_id=node_id,
        action=action,
        table_name=table_name,
        record_id=record_id,
        old_value=json.dumps(old_value) if old_value else None,
        new_value=json.dumps(new_value) if new_value else None,
        ip_address=ip_address,
    )
    db.add(entry)
