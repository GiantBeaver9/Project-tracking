from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.org import OrgNode, OrgNodeClosure, OrgNodeType
from app.models.user import User
from app.schemas.org import (
    OrgNodeCreate,
    OrgNodeResponse,
    OrgNodeTypeCreate,
    OrgNodeTypeResponse,
    OrgNodeUpdate,
)
from app.services.audit_service import log_audit

router = APIRouter(prefix="/org", tags=["org"])


async def _rebuild_closure_for_node(
    db: AsyncSession, node_id: str, parent_node_id: str | None
) -> None:
    """Insert closure table rows for a newly created node."""
    # Self-reference at depth 0
    db.add(OrgNodeClosure(
        ancestor_node_id=node_id,
        descendant_node_id=node_id,
        depth=0,
    ))

    if parent_node_id:
        # Copy all ancestors of the parent, incrementing depth by 1
        result = await db.execute(
            select(OrgNodeClosure).where(
                OrgNodeClosure.descendant_node_id == parent_node_id
            )
        )
        for ancestor_row in result.scalars().all():
            db.add(OrgNodeClosure(
                ancestor_node_id=ancestor_row.ancestor_node_id,
                descendant_node_id=node_id,
                depth=ancestor_row.depth + 1,
            ))


@router.post("/nodes", response_model=OrgNodeResponse, status_code=201)
async def create_node(
    body: OrgNodeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.parent_node_id:
        parent = await db.get(OrgNode, body.parent_node_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent node not found",
            )

    node = OrgNode(
        parent_node_id=body.parent_node_id,
        node_type=body.node_type,
        name=body.name,
        code=body.code,
        description=body.description,
        timezone=body.timezone,
        sort_order=body.sort_order,
        metadata_json=body.metadata_json,
        created_by=current_user.user_id,
    )
    db.add(node)
    await db.flush()  # get the node_id

    await _rebuild_closure_for_node(db, node.node_id, body.parent_node_id)

    await log_audit(
        db,
        user_id=current_user.user_id,
        node_id=node.node_id,
        action="CREATE",
        table_name="org_nodes",
        record_id=node.node_id,
        new_value={"name": node.name, "code": node.code, "node_type": node.node_type},
    )

    await db.commit()
    await db.refresh(node)
    return node


@router.get("/nodes", response_model=list[OrgNodeResponse])
async def list_nodes(
    parent_node_id: str | None = None,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(OrgNode)

    if parent_node_id:
        query = query.where(OrgNode.parent_node_id == parent_node_id)
    else:
        query = query.where(OrgNode.parent_node_id.is_(None))

    if not include_inactive:
        query = query.where(OrgNode.is_active == True)

    query = query.order_by(OrgNode.sort_order, OrgNode.name)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/nodes/{node_id}", response_model=OrgNodeResponse)
async def get_node(
    node_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    node = await db.get(OrgNode, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


@router.patch("/nodes/{node_id}", response_model=OrgNodeResponse)
async def update_node(
    node_id: str,
    body: OrgNodeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    node = await db.get(OrgNode, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    update_data = body.model_dump(exclude_unset=True)
    old_values = {}
    for field, value in update_data.items():
        old_values[field] = getattr(node, field)
        setattr(node, field, value)

    await log_audit(
        db,
        user_id=current_user.user_id,
        node_id=node_id,
        action="UPDATE",
        table_name="org_nodes",
        record_id=node_id,
        old_value=old_values,
        new_value=update_data,
    )

    await db.commit()
    await db.refresh(node)
    return node


@router.get("/nodes/{node_id}/subtree", response_model=list[OrgNodeResponse])
async def get_subtree(
    node_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all nodes in the subtree rooted at node_id (including itself)."""
    result = await db.execute(
        select(OrgNode)
        .join(
            OrgNodeClosure,
            OrgNodeClosure.descendant_node_id == OrgNode.node_id,
        )
        .where(
            and_(
                OrgNodeClosure.ancestor_node_id == node_id,
                OrgNode.is_active == True,
            )
        )
        .order_by(OrgNodeClosure.depth, OrgNode.sort_order)
    )
    return result.scalars().all()


@router.get("/nodes/{node_id}/ancestors", response_model=list[OrgNodeResponse])
async def get_ancestors(
    node_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all ancestors of node_id (for breadcrumb / permission walk)."""
    result = await db.execute(
        select(OrgNode)
        .join(
            OrgNodeClosure,
            OrgNodeClosure.ancestor_node_id == OrgNode.node_id,
        )
        .where(OrgNodeClosure.descendant_node_id == node_id)
        .order_by(OrgNodeClosure.depth.desc())
    )
    return result.scalars().all()


# --- Node Types ---


@router.post("/node-types", response_model=OrgNodeTypeResponse, status_code=201)
async def create_node_type(
    body: OrgNodeTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    node_type = OrgNodeType(
        node_type=body.node_type,
        display_label=body.display_label,
        allowed_depth_min=body.allowed_depth_min,
        allowed_depth_max=body.allowed_depth_max,
        is_system=body.is_system,
    )
    db.add(node_type)
    await db.commit()
    await db.refresh(node_type)
    return node_type


@router.get("/node-types", response_model=list[OrgNodeTypeResponse])
async def list_node_types(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(OrgNodeType).order_by(OrgNodeType.node_type))
    return result.scalars().all()
