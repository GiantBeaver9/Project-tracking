from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Address(Base, TimestampMixin):
    __tablename__ = "addresses"

    address_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    owner_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # USER | WORKPLACE | NODE
    owner_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address_line_1: Mapped[str] = mapped_column(String(255), nullable=False)
    address_line_2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state_code: Mapped[str] = mapped_column(String(2), nullable=False)
    zip_code: Mapped[str] = mapped_column(String(10), nullable=False)
    county: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country_code: Mapped[str] = mapped_column(
        String(2), nullable=False, default="US"
    )
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    geofence_radius_ft: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    geocode_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="PENDING"
    )


class Workplace(Base, TimestampMixin):
    __tablename__ = "workplaces"

    workplace_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    node_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("org_nodes.node_id"), nullable=False, index=True
    )
    project_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("projects.project_id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    node = relationship("OrgNode")
