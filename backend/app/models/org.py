from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_guid, utcnow


class OrgNode(Base, TimestampMixin):
    __tablename__ = "org_nodes"

    node_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_guid
    )
    parent_node_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("org_nodes.node_id"), nullable=True, index=True
    )
    node_type: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    timezone: Mapped[str] = mapped_column(
        String(100), nullable=False, default="America/New_York"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON stored as text for MSSQL compat
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # Relationships
    parent = relationship("OrgNode", remote_side=[node_id], back_populates="children")
    children = relationship("OrgNode", back_populates="parent", cascade="all")

    __table_args__ = (
        UniqueConstraint("parent_node_id", "code", name="uq_org_node_parent_code"),
    )


class OrgNodeType(Base):
    __tablename__ = "org_node_types"

    type_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    node_type: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    display_label: Mapped[str] = mapped_column(String(100), nullable=False)
    allowed_depth_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    allowed_depth_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=True
    )


class OrgNodeClosure(Base):
    __tablename__ = "org_node_closure"

    ancestor_node_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("org_nodes.node_id"),
        primary_key=True,
    )
    descendant_node_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("org_nodes.node_id"),
        primary_key=True,
    )
    depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
