from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Permission(Base):
    __tablename__ = "permissions"

    permission_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.user_id"), nullable=False, index=True
    )
    node_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("org_nodes.node_id"), nullable=False, index=True
    )
    role_template: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # Data visibility
    is_viewer: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_data_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # User management
    is_user_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_role_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Project management
    is_project_creator: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_project_editor: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_project_viewer: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_project_cost_viewer: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Time card
    is_timecard_submitter: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_timecard_approver: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_timecard_editor: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_timecard_viewer: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Expenses
    is_expense_submitter: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_expense_approver: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_expense_viewer: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_expense_cost_viewer: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Reporting
    is_report_viewer: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_report_exporter: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_payroll_exporter: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Estimation
    is_estimator: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_estimate_viewer: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_estimate_importer: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Admin
    is_node_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_workflow_admin: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_ot_rule_admin: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_payroll_admin: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Audit
    granted_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    granted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="permissions")
    node = relationship("OrgNode")
