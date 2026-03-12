from datetime import date

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    owner_node_id: str
    name: str
    code: str
    status: str = "DRAFT"
    is_billable: bool = True
    project_type: str = "INTERNAL"
    start_date: date | None = None
    end_date: date | None = None
    budget_hours: float | None = None
    budget_dollars: float | None = None
    manager_user_id: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    status: str | None = None
    is_billable: bool | None = None
    project_type: str | None = None
    health_status: str | None = None
    health_notes: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    budget_hours: float | None = None
    budget_dollars: float | None = None
    manager_user_id: str | None = None


class ProjectResponse(BaseModel):
    project_id: int
    owner_node_id: str
    is_cross_node: bool
    name: str
    code: str
    status: str
    is_billable: bool
    project_type: str
    health_status: str
    health_notes: str | None
    start_date: date | None
    end_date: date | None
    budget_hours: float | None
    budget_dollars: float | None
    manager_user_id: str | None

    model_config = {"from_attributes": True}


class TaskCreate(BaseModel):
    name: str
    description: str | None = None
    parent_task_id: int | None = None
    status: str = "TODO"
    budget_hours: float | None = None
    budget_dollars: float | None = None
    assigned_to: str | None = None
    due_date: date | None = None
    sort_order: int = 0


class TaskUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    budget_hours: float | None = None
    budget_dollars: float | None = None
    assigned_to: str | None = None
    due_date: date | None = None
    completed_date: date | None = None
    sort_order: int | None = None


class TaskResponse(BaseModel):
    task_id: int
    project_id: int
    parent_task_id: int | None
    name: str
    description: str | None
    status: str
    budget_hours: float | None
    budget_dollars: float | None
    assigned_to: str | None
    due_date: date | None
    completed_date: date | None
    sort_order: int

    model_config = {"from_attributes": True}


class MilestoneCreate(BaseModel):
    name: str
    due_date: date | None = None
    notes: str | None = None


class MilestoneUpdate(BaseModel):
    name: str | None = None
    due_date: date | None = None
    completed_date: date | None = None
    status: str | None = None
    notes: str | None = None


class MilestoneResponse(BaseModel):
    milestone_id: int
    project_id: int
    name: str
    due_date: date | None
    completed_date: date | None
    status: str
    notes: str | None

    model_config = {"from_attributes": True}
