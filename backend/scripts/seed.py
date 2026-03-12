"""
Seed script: creates a root enterprise node and an initial admin user.
Run with: python -m scripts.seed
"""
import asyncio
from datetime import datetime, timezone

from app.core.database import async_session_factory, engine
from app.core.security import hash_password
from app.models import Base
from app.models.org import OrgNode, OrgNodeClosure, OrgNodeType
from app.models.permission import Permission
from app.models.user import User, UserNodeMembership

SYSTEM_NODE_TYPES = [
    ("ENTERPRISE", "Enterprise"),
    ("COMPANY", "Company"),
    ("DIVISION", "Division"),
    ("DEPARTMENT", "Department"),
    ("TEAM", "Team"),
    ("PERSONA", "Persona"),
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        # Seed node types
        for code, label in SYSTEM_NODE_TYPES:
            nt = OrgNodeType(node_type=code, display_label=label, is_system=True)
            db.add(nt)

        # Create root enterprise node
        root = OrgNode(
            node_type="ENTERPRISE",
            name="Default Enterprise",
            code="ENT-ROOT",
            timezone="America/New_York",
        )
        db.add(root)
        await db.flush()

        # Self-referencing closure row
        db.add(OrgNodeClosure(
            ancestor_node_id=root.node_id,
            descendant_node_id=root.node_id,
            depth=0,
        ))

        # Create admin user
        admin = User(
            username="admin",
            email="admin@projecttracker.local",
            display_name="System Admin",
            hashed_password=hash_password("admin123"),
            user_type="EMPLOYEE",
            primary_node_id=root.node_id,
        )
        db.add(admin)
        await db.flush()

        # Membership
        db.add(UserNodeMembership(
            user_id=admin.user_id,
            node_id=root.node_id,
            is_primary=True,
            joined_at=datetime.now(timezone.utc),
            created_by=admin.user_id,
            created_at=datetime.now(timezone.utc),
        ))

        # Enterprise admin permission
        db.add(Permission(
            user_id=admin.user_id,
            node_id=root.node_id,
            role_template="ENTERPRISE_ADMIN",
            is_viewer=True,
            is_data_verified=True,
            is_user_admin=True,
            is_role_admin=True,
            is_project_creator=True,
            is_project_editor=True,
            is_project_viewer=True,
            is_project_cost_viewer=True,
            is_timecard_submitter=True,
            is_timecard_approver=True,
            is_timecard_editor=True,
            is_timecard_viewer=True,
            is_expense_submitter=True,
            is_expense_approver=True,
            is_expense_viewer=True,
            is_expense_cost_viewer=True,
            is_report_viewer=True,
            is_report_exporter=True,
            is_payroll_exporter=True,
            is_estimator=True,
            is_estimate_viewer=True,
            is_estimate_importer=True,
            is_node_admin=True,
            is_workflow_admin=True,
            is_ot_rule_admin=True,
            is_payroll_admin=True,
            granted_by=admin.user_id,
            granted_at=datetime.now(timezone.utc),
            is_active=True,
        ))

        await db.commit()
        print(f"Seeded root node: {root.node_id}")
        print(f"Seeded admin user: {admin.user_id} (username: admin, password: admin123)")


if __name__ == "__main__":
    asyncio.run(seed())
