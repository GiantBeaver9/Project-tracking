from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_guid


class User(Base, TimestampMixin):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_guid
    )
    primary_node_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("org_nodes.node_id"), nullable=True
    )
    username: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="EMPLOYEE"
    )
    employment_state: Mapped[str | None] = mapped_column(String(2), nullable=True)
    standard_hours_per_week: Mapped[float] = mapped_column(
        Numeric(5, 2), nullable=False, default=40.0
    )
    loaded_rate: Mapped[float | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sso_subject: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    primary_node = relationship("OrgNode", foreign_keys=[primary_node_id])
    memberships = relationship("UserNodeMembership", back_populates="user")
    permissions = relationship("Permission", back_populates="user")


class UserNodeMembership(Base):
    __tablename__ = "user_node_memberships"

    membership_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.user_id"), nullable=False, index=True
    )
    node_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("org_nodes.node_id"), nullable=False, index=True
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    removed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    user = relationship("User", back_populates="memberships")
    node = relationship("OrgNode")
