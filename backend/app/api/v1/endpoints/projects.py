from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.project import (
    Milestone,
    Project,
    ProjectAssignment,
    ProjectNodeAssignment,
    Task,
)
from app.models.user import User
from app.schemas.project import (
    MilestoneCreate,
    MilestoneResponse,
    MilestoneUpdate,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)
from app.services.audit_service import log_audit
from app.services.permission_service import get_user_node_ids_with_flag

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    body: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = Project(
        owner_node_id=body.owner_node_id,
        name=body.name,
        code=body.code,
        status=body.status,
        is_billable=body.is_billable,
        project_type=body.project_type,
        start_date=body.start_date,
        end_date=body.end_date,
        budget_hours=body.budget_hours,
        budget_dollars=body.budget_dollars,
        manager_user_id=body.manager_user_id,
        created_by=current_user.user_id,
    )
    db.add(project)
    await db.flush()

    # Create the OWNER node assignment
    owner_assignment = ProjectNodeAssignment(
        project_id=project.project_id,
        node_id=body.owner_node_id,
        role="OWNER",
        created_by=current_user.user_id,
    )
    db.add(owner_assignment)

    await log_audit(
        db,
        user_id=current_user.user_id,
        node_id=body.owner_node_id,
        action="CREATE",
        table_name="projects",
        record_id=str(project.project_id),
        new_value={"name": project.name, "code": project.code},
    )

    await db.commit()
    await db.refresh(project)
    return project


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Project)

    if status_filter:
        query = query.where(Project.status == status_filter)

    query = query.order_by(Project.name)
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/active", response_model=list[ProjectResponse])
async def list_active_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Active projects for the current user's time card dropdown.
    Enforces the filtering rules from spec Section 8.2.
    """
    today = date.today()

    # Get nodes where user has timecard_submitter permission
    submitter_nodes = await get_user_node_ids_with_flag(
        db, current_user.user_id, "is_timecard_submitter"
    )

    if not submitter_nodes:
        return []

    # Projects linked to user's permitted nodes via ProjectNodeAssignment
    node_project_query = (
        select(Project)
        .join(
            ProjectNodeAssignment,
            ProjectNodeAssignment.project_id == Project.project_id,
        )
        .where(
            and_(
                Project.status == "ACTIVE",
                Project.start_date <= today,
                or_(Project.end_date.is_(None), Project.end_date >= today),
                ProjectNodeAssignment.node_id.in_(submitter_nodes),
                ProjectNodeAssignment.role.in_(["OWNER", "PARTICIPANT"]),
            )
        )
    )

    # Projects directly assigned to the user
    direct_project_query = (
        select(Project)
        .join(
            ProjectAssignment,
            ProjectAssignment.project_id == Project.project_id,
        )
        .where(
            and_(
                Project.status == "ACTIVE",
                Project.start_date <= today,
                or_(Project.end_date.is_(None), Project.end_date >= today),
                ProjectAssignment.user_id == current_user.user_id,
                ProjectAssignment.removed_date.is_(None),
            )
        )
    )

    combined = node_project_query.union(direct_project_query).order_by(Project.name)
    result = await db.execute(combined)
    return result.scalars().all()


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    body: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = body.model_dump(exclude_unset=True)
    old_values = {}
    for field, value in update_data.items():
        old_val = getattr(project, field)
        old_values[field] = str(old_val) if old_val is not None else None
        setattr(project, field, value)

    await log_audit(
        db,
        user_id=current_user.user_id,
        node_id=project.owner_node_id,
        action="UPDATE",
        table_name="projects",
        record_id=str(project_id),
        old_value=old_values,
        new_value={k: str(v) if v is not None else None for k, v in update_data.items()},
    )

    await db.commit()
    await db.refresh(project)
    return project


# --- Tasks ---


@router.post("/{project_id}/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    project_id: int,
    body: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    task = Task(
        project_id=project_id,
        parent_task_id=body.parent_task_id,
        name=body.name,
        description=body.description,
        status=body.status,
        budget_hours=body.budget_hours,
        budget_dollars=body.budget_dollars,
        assigned_to=body.assigned_to,
        due_date=body.due_date,
        sort_order=body.sort_order,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.get("/{project_id}/tasks", response_model=list[TaskResponse])
async def list_tasks(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Task)
        .where(Task.project_id == project_id)
        .order_by(Task.sort_order, Task.name)
    )
    return result.scalars().all()


@router.patch("/{project_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    project_id: int,
    task_id: int,
    body: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Task).where(
            and_(Task.task_id == task_id, Task.project_id == project_id)
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return task


# --- Milestones ---


@router.post(
    "/{project_id}/milestones", response_model=MilestoneResponse, status_code=201
)
async def create_milestone(
    project_id: int,
    body: MilestoneCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    milestone = Milestone(
        project_id=project_id,
        name=body.name,
        due_date=body.due_date,
        notes=body.notes,
    )
    db.add(milestone)
    await db.commit()
    await db.refresh(milestone)
    return milestone


@router.get("/{project_id}/milestones", response_model=list[MilestoneResponse])
async def list_milestones(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Milestone)
        .where(Milestone.project_id == project_id)
        .order_by(Milestone.due_date)
    )
    return result.scalars().all()


@router.patch(
    "/{project_id}/milestones/{milestone_id}", response_model=MilestoneResponse
)
async def update_milestone(
    project_id: int,
    milestone_id: int,
    body: MilestoneUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Milestone).where(
            and_(
                Milestone.milestone_id == milestone_id,
                Milestone.project_id == project_id,
            )
        )
    )
    milestone = result.scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(milestone, field, value)

    await db.commit()
    await db.refresh(milestone)
    return milestone
