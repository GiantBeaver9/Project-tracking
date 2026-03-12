from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_guid


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    project_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    owner_node_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("org_nodes.node_id"), nullable=False, index=True
    )
    is_cross_node: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="DRAFT"
    )
    is_billable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    project_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="INTERNAL"
    )
    health_status: Mapped[str] = mapped_column(
        String(10), nullable=False, default="GREEN"
    )
    health_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    budget_hours: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    budget_dollars: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    manager_user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.user_id"), nullable=True
    )
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # Relationships
    owner_node = relationship("OrgNode")
    manager = relationship("User", foreign_keys=[manager_user_id])
    node_assignments = relationship("ProjectNodeAssignment", back_populates="project")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    milestones = relationship(
        "Milestone", back_populates="project", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("owner_node_id", "code", name="uq_project_node_code"),
    )


class ProjectNodeAssignment(Base):
    __tablename__ = "project_node_assignments"

    assignment_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.project_id"), nullable=False, index=True
    )
    node_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("org_nodes.node_id"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default="PARTICIPANT"
    )
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    project = relationship("Project", back_populates="node_assignments")
    node = relationship("OrgNode")


class ProjectAssignment(Base):
    __tablename__ = "project_assignments"

    assignment_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.project_id"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.user_id"), nullable=False, index=True
    )
    assigned_date: Mapped[date] = mapped_column(Date, nullable=False)
    removed_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Relationships
    project = relationship("Project")
    user = relationship("User")


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    task_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.project_id"), nullable=False, index=True
    )
    parent_task_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("tasks.task_id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="TODO")
    budget_hours: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    budget_dollars: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.user_id"), nullable=True
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    parent_task = relationship("Task", remote_side=[task_id])
    assignee = relationship("User", foreign_keys=[assigned_to])


class Milestone(Base, TimestampMixin):
    __tablename__ = "milestones"

    milestone_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.project_id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="milestones")
