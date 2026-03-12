# Project Tracker — Product Requirements Document

**Version:** 1.6  
**Date:** March 2026  
**Status:** Draft  
**Stack:** Svelte + AG Grid | Python (FastAPI) | Microsoft SQL Server | React Native (Mobile)  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Goals & Objectives](#2-goals--objectives)
3. [Scope](#3-scope)
4. [Stakeholders & Roles](#4-stakeholders--roles)
5. [Technical Architecture](#5-technical-architecture)
6. [Multi-Entity & Contractor Model](#6-multi-entity--contractor-model)
7. [Address & Location Model](#7-address--location-model)
8. [Database Design](#8-database-design)
9. [Time Card Features](#9-time-card-features)
10. [Overtime Rules Engine](#10-overtime-rules-engine)
11. [Project Management Features](#11-project-management-features)
12. [Expense Tracking](#12-expense-tracking)
13. [Contractor Cost Estimation](#13-contractor-cost-estimation)
14. [Cost Accounting & Budget Tracking](#14-cost-accounting--budget-tracking)
15. [Approval Workflows](#15-approval-workflows)
16. [Notifications & Reminders](#16-notifications--reminders)
17. [Reporting & Exports](#17-reporting--exports)
18. [Integrations](#18-integrations)
19. [Mobile Application](#19-mobile-application)
20. [API Design](#20-api-design)
21. [Front End Component Plan](#21-front-end-component-plan)
22. [Security Requirements](#22-security-requirements)
23. [Non-Functional Requirements](#23-non-functional-requirements)
24. [Delivery Milestones](#24-delivery-milestones)
25. [Open Questions](#25-open-questions)
26. [Glossary](#26-glossary)
27. [Revision History](#27-revision-history)

---

## 1. Executive Summary

Project Tracker is an internal web application that gives multi-entity organizations a single source of truth for project status, time entry, resource utilization, and project cost accounting. It is purpose-built for companies that operate across multiple legal entities and engage external contractors alongside full-time employees.

The system enforces smart time code management: only **active projects** are surfaced to employees filling out time cards. Inactive or archived projects are invisible at entry time but remain fully queryable in historical reports.

Key differentiators over generic time-tracking tools:

- **Multi-entity aware** — projects, users, and cost centers belong to specific entities; cross-entity reporting is supported for parent-company visibility.
- **State-level overtime engine** — overtime thresholds are configurable per state/jurisdiction, supporting both weekly (e.g., >40h) and daily (e.g., >8h in California) overtime rules.
- **Flexible approval chains** — approval workflows are configurable per entity, department, or project, supporting single-manager, multi-level, or auto-approval flows.
- **Project cost accounting** — tracks budget vs. actuals at the task level, by week, with labor cost estimates derived from loaded rates.
- **Expense tracking** — any user (including individual project owners managing a fix-and-flip or rental rehab) can log expenses by category (labor, materials, equipment, travel, subcontractor, permits, misc), with tax auto-calculated from configurable rates or entered manually, and a tax-exempt flag per line item.
- **Contractor cost estimation** — estimate contractor costs by hours × rate or fixed bid, per task or phase, with support for importing estimate spreadsheets (e.g., from BNI or similar cost databases). Estimated costs are tracked against actuals week by week as work progresses.
- **Native mobile app** — a React Native companion app for field workers and contractors to submit progress reports with photos, clock in with GPS geolocation verification, and select worker type (contractor vs. employee) at time start.
- **Rich location model** — both users and workplace/job sites carry full structured address records (street, city, state, zip, country, coordinates), supporting jurisdiction determination, overtime rule routing, and field reporting context.

---

## 2. Goals & Objectives

### 2.1 Business Goals

- Provide accurate, real-time visibility into project status and team utilization across all entities.
- Eliminate manual spreadsheet-based time tracking and reduce data entry errors.
- Enable finance and project managers to generate billing and cost reports directly from captured time data.
- Enforce project lifecycle rules so inactive projects cannot accumulate unbilled or misallocated time.
- Support multi-jurisdiction payroll compliance through a configurable overtime rules engine.
- Give contractors a lightweight, self-service time entry experience without exposing internal project financials.

### 2.2 Success Metrics

| Metric | Target | Timeframe |
|--------|--------|-----------|
| Time card completion rate | >= 95% | Within 60 days of launch |
| Data entry errors (wrong project codes) | < 1% | Steady state |
| Report generation time | < 5 seconds (P95) | At launch |
| Overtime rule accuracy vs. manual calculation | 100% | UAT sign-off |
| System uptime (business hours) | >= 99.5% | Monthly |
| Contractor onboarding time | < 10 minutes | Per contractor |

---

## 3. Scope

### 3.1 In Scope (v1)

- Multi-entity project and user management.
- Time card entry for employees and contractors with active-only project code filtering.
- Overtime tracking with configurable state/jurisdiction rules (daily and weekly thresholds).
- PTO and leave code management as special project codes.
- Billable vs. non-billable flagging per time entry.
- Daily notes per time entry row.
- Mobile-responsive time card UI (web).
- **Native mobile app (React Native)** for field progress reporting, photo capture, and GPS clock-in.
- **Geolocation clock-in** — GPS coordinates captured and stored when a user starts their time on mobile.
- **Progress reports with photos** — field users can submit progress reports with attached photos from mobile, linked to a project and task.
- **Worker type selection at clock-in** — mobile app prompts user to confirm contractor vs. employee status at each clock-in; admin-configurable per entity.
- **Structured address records for users** — home/mailing address with full fields (street, city, state, zip, country) used for jurisdiction determination.
- **Structured address records for workplaces/job sites** — each project or entity can have one or more job site addresses, supporting multi-location operations.
- Task and subtask breakdown per project.
- Milestones and deadline tracking per project.
- Project health status (RAG: Red / Amber / Green).
- Budget hours and dollar budget per project and task.
- Weekly estimate vs. actual cost accounting.
- **Expense tracking** for all user types (employees, contractors, project owners) across categories: labor/contractor rates, materials & supplies, equipment rental, travel & mileage, subcontractor invoices, permits & fees, and miscellaneous (free-form, stored as category = OTHER).
- **Tax calculation per expense** — auto-calculated from a configurable rate, with manual override, multiple tax type support (sales tax, use tax, etc.), per-state tax rate lookup, and a tax-exempt flag per line item.
- **Contractor cost estimation** — hours × rate, fixed bid, and per-task/phase estimates with Excel import (BNI or custom format) and running estimate vs. actual comparison.
- Configurable multi-level approval workflows per entity/department — shared by both time cards and expense reports.
- Auto-approve after configurable number of days.
- Time card reminder and alert notifications.
- Excel/CSV and PDF export for all reports.
- Email notifications (submission, approval, rejection, reminders).
- Active Directory / SSO integration.
- Payroll system sync (outbound data export / webhook).
- REST API back end with JWT + SSO authentication.

### 3.2 Out of Scope (v1)

- Client-facing portal.
- Automated invoice generation.
- Real-time chat or commenting on projects.
- Built-in payroll calculation engine (sync only; payroll math stays in payroll system).
- Offline-first mobile app (mobile requires connectivity; graceful error handling for poor signal is in scope).

---

## 4. Stakeholders & Roles

### 4.1 Overview

Roles and permissions in this system are **node-scoped and explicitly granted**. There is no role inheritance down the hierarchy — a user granted a role at a Division node does not automatically have that role in child Departments or Teams unless explicitly granted there too.

The permission system is driven by a `Permissions` table with an `is_*` boolean column per capability. On every page load and API call, the system checks the user's verified permissions for the specific node being accessed **before** returning any data. Data is hidden by default until permission is confirmed.

### 4.2 Built-in Role Templates

Role templates are pre-configured sets of permissions that can be applied as a starting point. They are templates only — actual permissions live in the `Permissions` table and can be customized per user per node.

| Role Template | Typical Scope | Description |
|---------------|--------------|-------------|
| **Enterprise Admin** | Root node | Full system access across all nodes; only assignable at root |
| **Node Admin** | Any node | Manage users, projects, and settings within their assigned node and its children |
| **Project Manager** | Node or project | Create/edit projects, manage tasks, review and approve time, run reports |
| **Manager** | Node | Approve time cards and expense reports for direct reports within the node |
| **Finance** | Node | Read-only cost/budget/expense reports; payroll export |
| **Approver** | Node or project | Time card and expense approval only |
| **Employee** | Node | Submit own time cards; view own records |
| **Contractor** | Node + assigned projects | Submit own time cards and expenses; no cost/rate visibility |

### 4.3 Permission Table Structure

Each row in `Permissions` represents one user's explicit grant at one org node. The `is_*` columns define exactly what that user can do within that node.

```sql
Permissions
  permission_id,
  user_id,                  -- FK → Users
  node_id,                  -- FK → OrgNodes (the specific node this grant applies to)
  role_template,            -- optional label (ENTERPRISE_ADMIN | NODE_ADMIN | PM | MANAGER |
                            --   FINANCE | APPROVER | EMPLOYEE | CONTRACTOR | CUSTOM)

  -- Data visibility
  is_viewer,                -- can see the node and its contents exist
  is_data_verified,         -- internal flag: set to true after auth + permission check passes

  -- User management
  is_user_admin,            -- can invite/deactivate users within this node
  is_role_admin,            -- can assign/modify permissions for other users in this node

  -- Project management
  is_project_creator,       -- can create projects under this node
  is_project_editor,        -- can edit project details, status, health
  is_project_viewer,        -- can view project details (but not cost)
  is_project_cost_viewer,   -- can view budget and cost actuals

  -- Time card
  is_timecard_submitter,    -- can submit own time cards
  is_timecard_approver,     -- can approve/reject time cards within this node
  is_timecard_editor,       -- can unlock and edit submitted time cards (admin override)
  is_timecard_viewer,       -- can view others' time cards within this node

  -- Expenses
  is_expense_submitter,     -- can submit expense reports
  is_expense_approver,      -- can approve/reject expense reports
  is_expense_viewer,        -- can view all expense reports in this node
  is_expense_cost_viewer,   -- can see dollar amounts and tax detail

  -- Reporting
  is_report_viewer,         -- can access reports for this node
  is_report_exporter,       -- can export reports to xlsx/pdf/csv
  is_payroll_exporter,      -- can access payroll export

  -- Estimation
  is_estimator,             -- can create/edit contractor cost estimates
  is_estimate_viewer,       -- can view estimates (not necessarily cost detail)
  is_estimate_importer,     -- can import Excel estimate files

  -- Admin
  is_node_admin,            -- can create child nodes and manage node settings
  is_workflow_admin,        -- can configure approval workflows for this node
  is_ot_rule_admin,         -- can configure overtime rules for this node
  is_payroll_admin,         -- can configure payroll sync settings

  granted_by,               -- FK → Users (who granted this permission)
  granted_at,
  expires_at (nullable),    -- optional time-bound grant
  is_active (bool),
  notes                     -- reason for grant (audit trail)
```

### 4.4 Default-Deny & Verification Flow

The system enforces a **default-deny** posture. No data is returned to a client until the permission check has passed for the specific node and capability being requested.

```
Request arrives
    ↓
1. Authenticate JWT token → valid user identity
    ↓
2. Identify target node_id from request context
    ↓
3. Load Permissions row for (user_id, node_id)
    ↓
4. Check is_data_verified = true AND required is_* flag = true
    ↓ PASS                        ↓ FAIL
Return data                  Return 403 — no data, no hints
                             (do not reveal whether node exists)
```

This check runs **before** any DB query for business data. Repositories receive a `VerifiedPermission` object as a required parameter — they will not execute without it.

### 4.5 Role Scope Rules

- A permission grant is **local to the node** it is issued on — it does not cascade to child nodes unless explicitly granted there too
- An Enterprise Admin grant on the root node is the **only exception** — it grants read access across all nodes for administrative purposes, but write operations still require explicit node-level grants
- A user may hold different role templates at different nodes (e.g., Manager at Division A, Employee at Division B)
- A user may belong to **multiple nodes simultaneously** (e.g., a user on two teams in different departments)
- The Enterprise Admin (root-level) is the only role that can grant permissions at the root node

---

## 5. Technical Architecture

### 5.1 Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Front End | Svelte + AG Grid | Reactive SPA; AG Grid for all tabular views |
| Mobile App | React Native | iOS + Android; shared API with web |
| API | Python — FastAPI | Async, Pydantic validation, OpenAPI docs auto-generated |
| Database | Microsoft SQL Server | Enterprise RDBMS; Row-Level Security for entity isolation |
| Auth | JWT + Azure AD / SAML SSO | JWT for API sessions; SSO for browser login; biometric unlock on mobile |
| ORM / Driver | SQLAlchemy + pyodbc | MSSQL dialect; parameterized queries only |
| Task Queue | Celery + Redis | Async jobs: notifications, payroll sync, report generation, geocoding |
| File Storage | Azure Blob / S3-compatible | Progress report photo storage |
| Deployment | Docker + docker-compose | Dev/staging/prod parity |
| Email | SMTP / SendGrid | Transactional notifications |
| Push Notifications | Firebase Cloud Messaging | Mobile push alerts |
| Geocoding | Google Maps API / Azure Maps | Address → lat/lng resolution |

### 5.2 Architecture Overview

```
┌──────────────────────┐  ┌──────────────────────┐
│   Browser / Desktop  │  │  Mobile App (iOS/Android) │
│  Svelte SPA + AG Grid│  │  React Native         │
└──────────┬───────────┘  └──────────┬────────────┘
           │ HTTPS / REST + JWT       │ HTTPS / REST + JWT
           └────────────┬────────────┘
┌───────────────────────▼─────────────────────────┐
│              Python FastAPI Service             │
│  ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│  │  Auth    │ │ Business │ │    Reports     │  │
│  │  Layer   │ │  Logic   │ │    Engine      │  │
│  └──────────┘ └──────────┘ └────────────────┘  │
│  ┌─────────────────────────────────────────┐   │
│  │   Celery Task Queue                     │   │
│  │   (notifications, exports, geocoding,   │   │
│  │    payroll sync, photo processing)      │   │
│  └─────────────────────────────────────────┘   │
└──────────────┬──────────────────┬──────────────┘
               │                  │
┌──────────────▼──────┐  ┌────────▼──────────────┐
│  Microsoft SQL      │  │  Blob Storage          │
│  Server             │  │  (Progress Report      │
│  (Row-Level         │  │   Photos)              │
│   Security)         │  └───────────────────────┘
└─────────────────────┘
```

### 5.3 Key Architectural Constraints

- The front end **never** communicates directly with the database. All data access flows through the API.
- Node isolation is enforced at **both** the API layer (permission-verified scoped queries) and the database layer (Row-Level Security policies keyed on `node_id`).
- **Default deny:** No data is returned to a client until `Permissions.is_data_verified = true` and the required `is_*` flag is confirmed for the target node. This check runs before any business data query in every repository method.
- Contractors' JWT token claims include `user_type: CONTRACTOR` — any service or repository that returns cost, rate, or other users' data checks this claim and returns an empty/filtered response regardless of any other permission state.
- The overtime rules engine runs **server-side only** — never in the browser — to prevent manipulation.

---

## 6. Organizational Hierarchy & Multi-Tenancy Model

### 6.1 Overview

The org hierarchy is a **fully configurable, unlimited-depth tree**. There are no fixed levels — an enterprise with 2 tiers and a franchise with 6 tiers use the same model. Each node in the tree is an `OrgNode` record with a configurable `node_type` label (Enterprise, Company, Division, Department, Team, etc.).

The canonical example hierarchy:

```
OrgNode (type: ENTERPRISE)  ← root, one per installation tenant
  └── OrgNode (type: COMPANY)          ← legal entity / LLC / Corp
        └── OrgNode (type: DIVISION)   ← region or business unit
              └── OrgNode (type: DEPARTMENT) ← cost center / function
                    └── OrgNode (type: TEAM) ← crew, squad, union local
                          └── OrgNode (type: PERSONA) ← optional individual role node
```

Every resource in the system — users, projects, workplaces, approval workflows, overtime rules, tax rates, payroll configs — is **owned by a node**. Queries are always scoped to the requesting user's verified nodes.

### 6.2 OrgNode Schema

```sql
OrgNodes
  node_id,                  -- surrogate PK (GUID preferred for external references)
  parent_node_id (nullable),-- FK → OrgNodes self-reference; null = root node
  node_type,                -- configurable label: ENTERPRISE | COMPANY | DIVISION |
                            --   DEPARTMENT | TEAM | PERSONA | CUSTOM
  name,
  code,                     -- short unique code within the parent (e.g., 'CA-WEST', 'IBEW-11')
  description,
  timezone,                 -- IANA timezone string (e.g., 'America/Los_Angeles')
  is_active (bool),
  sort_order,               -- controls display order among siblings
  metadata (JSON),          -- extensible key-value for node-type-specific config
  created_by,
  created_at, updated_at

OrgNodeTypes               -- configurable list of valid node_type labels per installation
  type_id,
  node_type,               -- e.g., 'ENTERPRISE', 'DIVISION', 'CREW'
  display_label,           -- human-readable name shown in UI
  allowed_depth_min,       -- optional: enforce where in the tree this type can appear
  allowed_depth_max,
  is_system (bool),        -- system types cannot be deleted
  created_at
```

### 6.3 Closure Table for Efficient Tree Queries

A self-referential parent FK alone makes subtree queries expensive (`WITH RECURSIVE` CTEs). Instead, a **closure table** maintains pre-computed ancestor/descendant relationships. This enables any subtree query in a single non-recursive join.

```sql
OrgNodeClosure
  ancestor_node_id,         -- FK → OrgNodes
  descendant_node_id,       -- FK → OrgNodes
  depth,                    -- 0 = self, 1 = direct child, 2 = grandchild, etc.
  PRIMARY KEY (ancestor_node_id, descendant_node_id)
```

**How it works:** When a node is inserted, a row is written to `OrgNodeClosure` for every ancestor of the new node (including itself at depth 0). When a node is moved, all affected closure rows are recalculated.

```sql
-- Get all nodes within the subtree rooted at a Division (any depth)
SELECT n.*
FROM OrgNodes n
JOIN OrgNodeClosure c ON c.descendant_node_id = n.node_id
WHERE c.ancestor_node_id = :division_node_id
  AND n.is_active = 1

-- Get all ancestors of a Team node (for breadcrumb / permission walk)
SELECT n.*
FROM OrgNodes n
JOIN OrgNodeClosure c ON c.ancestor_node_id = n.node_id
WHERE c.descendant_node_id = :team_node_id
ORDER BY c.depth DESC
```

### 6.4 User ↔ Node Membership

Users can belong to multiple nodes simultaneously. Membership is tracked separately from permissions.

```sql
UserNodeMemberships
  membership_id,
  user_id,                  -- FK → Users
  node_id,                  -- FK → OrgNodes
  is_primary (bool),        -- user's "home" node (used for default OT jurisdiction, etc.)
  joined_at,
  removed_at (nullable),
  created_by, created_at
```

A user without a `UserNodeMembership` for a given node has **no access to that node** regardless of any other grant. Membership is the prerequisite; `Permissions` is the capability grant.

### 6.5 Project ↔ Node Assignment

Projects can be owned by any node and can span multiple nodes at the same level.

```sql
Projects
  project_id, owner_node_id, -- primary owning node
  name, code, status, ...    -- (full schema in Section 8)

ProjectNodeAssignments       -- allows a project to span multiple nodes
  assignment_id,
  project_id,                -- FK → Projects
  node_id,                   -- FK → OrgNodes (participating node)
  role,                      -- OWNER | PARTICIPANT | OBSERVER
  created_by, created_at
```

- The `owner_node_id` on `Projects` is the billing/cost node — the node whose budget the project draws from
- Additional nodes can be assigned as `PARTICIPANT` (users from that node can log time/expenses) or `OBSERVER` (view-only)
- A user from a participant node sees the project in their time card dropdown only if they also have `is_timecard_submitter` on that node



### 6.6 Cross-Node Projects & Cost Allocation

Projects may be flagged as **cross-node**, allowing time and expenses to be logged by users from multiple nodes. Each cross-node project has explicit cost allocation rules that determine which node bears the cost.

#### Cost Allocation Schema

```sql
CrossNodeAllocations
  allocation_id,
  project_id,                  -- FK → Projects (must have is_cross_node = true)
  participant_node_id,         -- FK → OrgNodes (the node supplying the labor/expense)
  owning_node_id,              -- FK → OrgNodes (the node that bears the cost)
  allocation_method,           -- FULL_TO_OWNER | SPLIT_PERCENT | BILLED_AT_RATE
  split_percent,               -- used when method = SPLIT_PERCENT (0.00–100.00)
  bill_rate_override,          -- used when method = BILLED_AT_RATE (overrides user loaded_rate)
  applies_to,                  -- ALL | LABOR | EXPENSES | LABOR_ONLY | EXPENSES_ONLY
  effective_date,
  notes,
  created_by, created_at
```

#### Allocation Methods

| Method | Description | Example |
|--------|-------------|---------|
| `FULL_TO_OWNER` | All costs from the participant node are charged 100% to the owning node | Team B staff working on Division A's project; Division A bears all cost |
| `SPLIT_PERCENT` | Costs split by a configured percentage between participant and owning node | 60% charged to Division A, 40% retained by Division B |
| `BILLED_AT_RATE` | Participant node bills the owning node at a negotiated intercompany rate, overriding the user's loaded rate | Company B bills Company A at $150/hr regardless of internal loaded rate |

#### Visibility Rules

- Users from a participant node see only their own time/expense entries on the cross-node project — governed by their `Permissions` row on that project's node
- The owning node's PM and Finance (with `is_project_cost_viewer` on the owning node) see all entries across all participant nodes
- Cost allocation breakdowns require `is_expense_cost_viewer` or `is_project_cost_viewer` on the owning node
- Enterprise Admin at the root node can see all allocation data across all nodes

### 6.7 Contractor Access Model

Contractor access is controlled by the same `Permissions` table. The `CONTRACTOR` role template pre-sets specific `is_*` flags to false that cannot be overridden by a Node Admin — they require Enterprise Admin to unlock.

| Feature | Employee | Contractor |
|---------|----------|------------|
| Time card entry | `is_timecard_submitter` | `is_timecard_submitter` |
| View project details | `is_project_viewer` | Name + code only — cost fields always hidden |
| View budget / cost data | `is_project_cost_viewer` | **Always false — system enforced** |
| View other users' time | `is_timecard_viewer` | **Always false — system enforced** |
| View expense cost amounts | `is_expense_cost_viewer` | **Always false — system enforced** |
| PTO / leave codes | Yes | Configurable per node |
| Overtime tracking | Yes | Configurable per node |
| SSO login | Yes | Optional (email+password fallback) |
| Mobile app access | Yes | Yes |
| GPS clock-in | Yes | Yes |
| Progress reports + photos | Yes | Yes |
| Worker type shown at clock-in | Read-only (Employee) | Read-only (Contractor) |
| Worker type self-modification | Never | Never |

Worker type (`EMPLOYEE` or `CONTRACTOR`) is set exclusively by a user with `is_user_admin` on the user's primary node. It is displayed on the mobile clock-in screen for the user's awareness but cannot be changed by the user. Changes are logged in `AuditLog`.

---

## 7. Address & Location Model

### 7.1 Overview

The system maintains two distinct categories of address/location data:

1. **User addresses** — where an employee or contractor lives or is domiciled. Used for overtime jurisdiction routing and payroll compliance.
2. **Workplace / job site addresses** — physical locations where work is performed. Tied to projects or entities, used for field reporting, geofencing validation, and state-level tax/labor jurisdiction determination.

Both address types use the same structured schema and support multiple addresses per record (e.g., a user may have a home address and a mailing address; a project may have multiple job sites).

### 7.2 Structured Address Schema

All address records (user and workplace) share this field set:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `address_id` | int | PK | |
| `owner_type` | enum | Yes | `USER` \| `WORKPLACE` \| `NODE` |
| `owner_id` | int | Yes | FK to Users, Workplaces, or OrgNodes |
| `label` | varchar(100) | No | e.g., "Home", "Mailing", "Job Site A", "Main Office" |
| `address_line_1` | varchar(255) | Yes | Street number and street name |
| `address_line_2` | varchar(255) | No | Suite, unit, floor, building |
| `city` | varchar(100) | Yes | |
| `state_code` | char(2) | Yes | US state abbreviation (e.g., `CA`, `TX`) |
| `zip_code` | varchar(10) | Yes | 5-digit or ZIP+4 format |
| `county` | varchar(100) | No | Used for local tax jurisdiction in some states |
| `country_code` | char(2) | Yes | ISO 3166-1 alpha-2 (default: `US`) |
| `latitude` | decimal(10,7) | No | Populated via geocoding on save |
| `longitude` | decimal(10,7) | No | Populated via geocoding on save |
| `is_primary` | bool | Yes | One primary address per owner_type per owner |
| `is_active` | bool | Yes | Soft-delete support |
| `created_at` | datetime | Yes | |
| `updated_at` | datetime | Yes | |

### 7.3 User Address

Each user (employee or contractor) may have multiple address records:

- **Home / Domicile** (`label: "Home"`) — used as the primary residence for overtime jurisdiction and payroll state determination.
- **Mailing** (`label: "Mailing"`) — separate mailing address if different from home.
- Only one address may be flagged `is_primary = true` per user at a time.
- The `state_code` of the user's primary address is used as the **default overtime jurisdiction** unless overridden in `UserOvertimeOverride`.

**User address UI fields (web and mobile):**

```
Address Line 1 *        [ 123 Main Street              ]
Address Line 2          [ Apt 4B                        ]
City *                  [ Sacramento                    ]
State *                 [ CA ▼ ]     ZIP Code * [ 95814 ]
County                  [ Sacramento                    ]
Country *               [ US ▼ ]
```

### 7.4 Workplace / Job Site Address

Workplaces are physical locations where work is performed. They are owned by either an **Entity** (permanent office) or a **Project** (construction site, client location, field site).

- An entity may have multiple workplace addresses (e.g., headquarters, regional offices).
- A project may have one or more job site addresses.
- Each workplace address has a `label` for easy reference (e.g., "Main Office", "Site Alpha", "Client HQ").
- Workplace coordinates (lat/lng) are used for **geofence validation** on mobile clock-in (see Section 17).

**Workplace address UI fields:**

```
Location Label *        [ Site Alpha                    ]
Address Line 1 *        [ 4500 Industrial Blvd          ]
Address Line 2          [ Gate 3                        ]
City *                  [ Oakland                       ]
State *                 [ CA ▼ ]     ZIP Code * [ 94601 ]
County                  [ Alameda                       ]
Country *               [ US ▼ ]
Geofence Radius (ft)    [ 500                           ]  ← for mobile clock-in validation
```

### 7.5 Geocoding

- On save of any address record, the system queues a background geocoding task (Celery) to resolve lat/lng from the street address.
- Geocoding uses a configurable provider (Google Maps Geocoding API or Azure Maps).
- If geocoding fails, the record is saved without coordinates and flagged for manual review.
- Coordinates are used for: geofence clock-in validation, jurisdiction inference, and map display in project detail.

### 7.6 Overtime Rule Resolution from Location

When a time entry's **workplace address** `state_code` differs from the **user's home address** `state_code`, the system flags the entry for potential multi-state consideration. The applicable `OvertimeRule` is resolved using the full priority chain defined in Section 10 — the workplace `state_code` is used as the `STATE`-scope lookup if no higher-priority assignment (USER, NODE ancestors walked root-to-leaf, UNION, PROJECT) applies.

---

## 8. Database Design

### 8.1 Core Tables

#### Organizational Hierarchy

```sql
-- Full schema defined in Section 6.2
-- OrgNodes, OrgNodeTypes, OrgNodeClosure are the three hierarchy tables
-- All other tables reference node_id instead of entity_id

OrgNodes             -- every level of the hierarchy (enterprise → company → division → dept → team → persona)
  node_id (GUID), parent_node_id (nullable), node_type, name, code,
  timezone, is_active, sort_order, metadata (JSON), created_by, created_at, updated_at

OrgNodeTypes         -- configurable node type labels per installation
  type_id, node_type, display_label, allowed_depth_min, allowed_depth_max,
  is_system, created_at

OrgNodeClosure       -- pre-computed ancestor/descendant pairs for efficient subtree queries
  ancestor_node_id, descendant_node_id, depth
  PRIMARY KEY (ancestor_node_id, descendant_node_id)
```

#### Permissions

```sql
-- Full schema defined in Section 4.3
-- One row per user per node; every is_* flag explicitly set; no inheritance

Permissions
  permission_id, user_id, node_id, role_template,
  is_viewer, is_data_verified,
  is_user_admin, is_role_admin,
  is_project_creator, is_project_editor, is_project_viewer, is_project_cost_viewer,
  is_timecard_submitter, is_timecard_approver, is_timecard_editor, is_timecard_viewer,
  is_expense_submitter, is_expense_approver, is_expense_viewer, is_expense_cost_viewer,
  is_report_viewer, is_report_exporter, is_payroll_exporter,
  is_estimator, is_estimate_viewer, is_estimate_importer,
  is_node_admin, is_workflow_admin, is_ot_rule_admin, is_payroll_admin,
  granted_by, granted_at, expires_at (nullable), is_active, notes
```

#### Addresses

```sql
Addresses            -- Shared address table for users, workplaces, and nodes
  address_id, owner_type (USER | WORKPLACE | NODE), owner_id,
  label,                    -- e.g., "Home", "Mailing", "Site Alpha", "Main Office"
  address_line_1, address_line_2,
  city, state_code, zip_code, county,
  country_code,             -- ISO 3166-1 alpha-2, default 'US'
  latitude, longitude,      -- populated async via geocoding
  geofence_radius_ft,       -- for workplace addresses: mobile clock-in validation radius
  is_primary (bool),
  is_active (bool),
  geocode_status,           -- PENDING | SUCCESS | FAILED
  created_at, updated_at

Workplaces           -- Named job sites owned by a node or project
  workplace_id, node_id, project_id (nullable),
  name, description, is_active, created_at
  -- One or more Addresses records link via owner_type='WORKPLACE'
```

#### Users

```sql
Users
  user_id,
  primary_node_id,          -- FK → OrgNodes (user's home node; drives default OT jurisdiction)
  username, email, display_name,
  user_type,                -- EMPLOYEE | CONTRACTOR (set by is_user_admin only)
  employment_state,         -- fallback state for OT rules if no primary address
  standard_hours_per_week,  -- e.g., 40
  loaded_rate,              -- cost per hour — visible only to is_project_cost_viewer
  is_active,
  sso_subject,              -- SSO claim subject identifier
  created_at, updated_at
  -- Role/permission grants → Permissions table
  -- Node memberships → UserNodeMemberships table (Section 6.4)
  -- Addresses → Addresses table (owner_type='USER')

UserNodeMemberships  -- which nodes a user belongs to (prerequisite for permission grants)
  membership_id, user_id, node_id, is_primary (bool),
  joined_at, removed_at (nullable), created_by, created_at
```

#### Projects & Tasks

```sql
Projects
  project_id,
  owner_node_id,            -- FK → OrgNodes (primary owning / billing node)
  is_cross_node (bool),     -- if true, ProjectNodeAssignments defines participating nodes
  name, code,               -- code unique within owner_node_id
  status,                   -- DRAFT | ACTIVE | INACTIVE | ARCHIVED
  is_billable,
  project_type,             -- EXTERNAL | INTERNAL | OVERHEAD
  health_status,            -- GREEN | AMBER | RED
  health_notes,
  start_date, end_date,
  budget_hours, budget_dollars,
  manager_user_id, created_by, created_at, updated_at

ProjectNodeAssignments   -- nodes participating in a cross-node project (Section 6.5)
  assignment_id, project_id, node_id,
  role,                     -- OWNER | PARTICIPANT | OBSERVER
  created_by, created_at

Tasks
  task_id, project_id, parent_task_id (nullable — supports subtasks),
  name, description, status,
  budget_hours, budget_dollars,
  assigned_to (user_id, nullable),
  due_date, completed_date, sort_order

Milestones
  milestone_id, project_id,
  name, due_date, completed_date, status, notes

ProjectAssignments   -- which users can log time to which projects
  assignment_id, project_id, user_id,
  assigned_date, removed_date
```

#### Time Entry

```sql
TimePeriods
  period_id, entity_id,
  start_date, end_date,   -- Mon–Sun week
  is_locked, locked_by, locked_at

TimeCards
  timecard_id, user_id, period_id, entity_id,
  status (DRAFT | SUBMITTED | IN_REVIEW | APPROVED | REJECTED | LOCKED),
  submitted_at, approved_at, approved_by,
  rejection_reason, auto_approved (bool)

TimeEntries
  entry_id, timecard_id, user_id, project_id, task_id (nullable),
  entry_date, hours_regular, hours_overtime, hours_doubletime,
  is_billable,              -- can override project default
  is_pto,                   -- true for leave codes
  notes,                    -- daily notes
  -- Clock-in geolocation (captured on mobile clock-in)
  clock_in_at,              -- datetime of clock-in
  clock_in_lat,             -- GPS latitude at clock-in
  clock_in_lng,             -- GPS longitude at clock-in
  clock_in_accuracy_m,      -- GPS accuracy in meters
  clock_in_workplace_id,    -- nearest matched workplace (nullable)
  clock_in_worker_type,     -- EMPLOYEE | CONTRACTOR (confirmed at clock-in)
  -- Clock-out
  clock_out_at,
  clock_out_lat,
  clock_out_lng,
  created_at, updated_at

ProgressReports      -- Field progress reports submitted via mobile
  report_id, project_id, task_id (nullable), user_id,
  entry_date,
  title,
  body,                     -- free text description of progress
  weather_notes,            -- optional field condition note
  location_lat, location_lng,
  workplace_id (nullable),  -- if submitted at a known job site
  submitted_at,
  created_at

ProgressReportPhotos -- Photos attached to progress reports
  photo_id, report_id,
  file_key,                 -- storage path / blob key
  file_size_bytes,
  mime_type,
  caption,                  -- optional photo caption
  taken_at,                 -- EXIF timestamp if available
  photo_lat, photo_lng,     -- EXIF GPS if available
  upload_status,            -- PENDING | UPLOADED | FAILED
  created_at
```

#### Leave / PTO Codes

```sql
LeaveCodes
  leave_code_id, node_id, name, code,
  accrual_type,             -- PTO | SICK | HOLIDAY | UNPAID | OTHER
  is_active
```

#### Cost Accounting

```sql
WeeklyBudgetSnapshots    -- PM-entered estimates per project/task per week
  snapshot_id, project_id, task_id (nullable), period_id,
  estimated_hours, estimated_cost,
  created_by, created_at

BillingRates
  rate_id, node_id, role_or_user_id, effective_date,
  rate_per_hour, rate_type  -- LOADED | BILL
```

#### Overtime Rules

```sql
OvertimeRules            -- Named, reusable overtime rule definitions
  rule_id,
  name,                     -- e.g., "Federal Standard", "California Labor Code",
                            --        "IBEW Local 11 CBA", "Acme Corp Custom"
  description,
  weekly_ot_threshold,      -- hours/week before OT kicks in (e.g., 40.0); null = no weekly OT
  weekly_dt_threshold,      -- hours/week before double-time kicks in (null = no weekly DT)
  daily_ot_threshold,       -- hours/day before OT kicks in (e.g., 8.0); null = no daily OT
  daily_dt_threshold,       -- hours/day before double-time kicks in (e.g., 12.0); null = no daily DT
  seventh_day_ot (bool),    -- all hours on 7th consecutive workday = OT
  seventh_day_dt_threshold, -- hours on 7th day before DT kicks in (null = no DT on 7th day)
  effective_date,
  is_active (bool),
  created_by, created_at, updated_at

OvertimeRuleAssignments  -- Flexible assignment of a rule to any scope
  assignment_id,
  rule_id,                  -- FK → OvertimeRules
  scope_type,               -- STATE | NODE | USER | PROJECT | UNION
                            --   STATE  → state_code (e.g., 'CA', 'TX')
                            --   NODE   → node_id (replaces ENTITY and TEAM scopes —
                            --             any node in the hierarchy: Company, Division,
                            --             Department, Team, or individual Persona node)
                            --   USER   → user_id (most specific override)
                            --   PROJECT → project_id (prevailing wage etc.)
                            --   UNION  → union_id
  scope_id,                 -- the id/code matching the scope_type above
  priority,                 -- integer; lower number = higher priority (1 wins over 10)
  effective_date,
  expiry_date (nullable),   -- supports time-bounded rules (e.g., CBA expiry)
  created_by, created_at

Unions                   -- Union or collective bargaining agreement groups
  union_id, node_id, name, code, cba_reference, is_active
  -- Union members are users; membership tracked via UserNodeMemberships
  -- where the target node is a TEAM-type node representing the union local
```

**Rule resolution priority order (lowest `priority` integer wins):**

1. `USER` — explicit per-user override; most specific
2. `NODE` at depth N (Persona / Team level) — closest node to the user in the tree
3. `NODE` at depth N-1 (Department) — next ancestor node
4. `NODE` at depth N-2, N-3 … (Division, Company) — walking up the tree
5. `UNION` — CBA-wide rule for union members
6. `PROJECT` — project-specific rule (prevailing wage, client contract)
7. `STATE` — state labor law baseline; least specific

Because `NODE` scope now covers every level of the hierarchy, the system walks the user's ancestor chain (via `OrgNodeClosure`) from most specific to most general when resolving the applicable NODE-scope rule. The first matching active assignment with the lowest `priority` integer wins.

If multiple assignments exist at the same `scope_type` and `priority`, the most recently effective one wins.

#### Approval Workflow

```sql
ApprovalWorkflows
  workflow_id, node_id, name,   -- owned by a node (replaces entity_id)
  workflow_type,                -- TIME_CARD | EXPENSE
  auto_approve_after_days (nullable),
  is_default (bool),            -- one default per node per workflow_type
  rejection_return_policy,      -- STAGE_1 | SUBMITTER_ONLY (see Section 15.4)
  created_at, updated_at

ApprovalStages
  stage_id, workflow_id, stage_order,
  stage_name,
  requires_all (bool),          -- AND vs OR logic for approvers at this stage
  escalation_after_hours (nullable)

ApprovalStageApprovers
  id, stage_id, approver_user_id

ProjectWorkflowOverrides  -- assign a non-default workflow to a project per type
  id, project_id, workflow_type, workflow_id
```

#### Audit

```sql
AuditLog
  log_id, node_id, user_id, action,
  table_name, record_id, old_value (JSON), new_value (JSON),
  ip_address, created_at
```

### 8.2 Active Project Filtering Logic

The `GET /api/v1/projects/active` endpoint applies all of the following rules server-side. **Permission is verified before any query executes** — a user with no verified `Permissions` row for the relevant node receives an empty 200 response, not a 403, to avoid leaking node existence.

1. Requesting user has `is_data_verified = true` AND `is_timecard_submitter = true` on at least one node
2. `Projects.status = 'ACTIVE'`
3. Current date is >= `start_date` (and <= `end_date` if set)
4. A valid `ProjectNodeAssignments` record exists linking the project to one of the user's verified nodes (PARTICIPANT or OWNER role), OR the user has a direct `ProjectAssignments` record
5. Leave codes (`LeaveCodes`) owned by the user's verified nodes are also returned as selectable entries

Inactive, archived, future-dated, or node-unverified projects are **never** returned. The client has no knowledge of their existence.

---

## 9. Time Card Features

### 8.1 Weekly Time Card Grid

The primary time entry UI is an AG Grid editable weekly grid:

- **Rows:** One row per project code (or leave code) the user has added for the week
- **Columns:** Mon | Tue | Wed | Thu | Fri | Sat | Sun | Total | Billable flag | Notes
- **Footer row:** Daily totals, weekly total, and overtime hours (auto-calculated)
- Users can **add a row** by selecting from the active project dropdown
- Users can **remove a row** only if no hours have been entered on it

### 8.2 Billable vs. Non-Billable

- Each time entry row has a billable toggle (checkbox or toggle switch)
- Default value is inherited from the project's `is_billable` setting
- Users may override the default on individual entries (within permission rules)
- Reports can filter and aggregate by billable status

### 8.3 PTO / Leave Codes

- Leave codes appear in the same project code dropdown as projects, clearly labeled (e.g., **[LEAVE] PTO**, **[LEAVE] Sick**)
- Leave codes are entity-configured and flagged `is_pto = true` in the time entry
- Leave entries do **not** count toward billable hours
- Leave entries **do** count toward daily/weekly hour totals for overtime threshold calculations (jurisdiction-dependent — configurable)

### 8.4 Daily Notes

- Each row has an expandable notes field, one note per day
- Notes are plain text, max 500 characters
- Notes are visible to approvers in the review UI
- Notes appear in PDF exports of time cards

### 8.5 Mobile-Friendly Entry

- Time card UI uses a responsive layout that collapses the 7-day grid to a day-picker on small screens
- On mobile, the user selects a day, then sees a vertical list of project rows for that day
- AG Grid is replaced with a native-feel card list on screens < 768px
- Core actions (add row, enter hours, add notes, submit) are fully functional on mobile
- Touch-friendly controls: large tap targets, numeric keyboard auto-invoked for hour fields

---

## 10. Overtime Rules Engine

### 10.1 Overview

Overtime rules are not one-size-fits-all. State law sets a baseline, but collective bargaining agreements (CBAs), union contracts, company policies, and project-specific requirements (e.g., prevailing wage) all introduce variations. The system uses a **named, reusable `OvertimeRules` model** with a flexible **`OvertimeRuleAssignments`** table that can assign any rule to any scope — a state, a company, a team, a union, a specific project, or an individual user.

This means:
- A California-based union crew can have a CBA rule that triggers OT after 7h/day instead of the state's 8h
- A federal prevailing wage project can have its own OT thresholds applied only to hours on that project
- A part-time employee team can have a 32h/week OT threshold instead of 40h
- All of these coexist and the engine resolves which rule applies for each time entry automatically

### 10.2 OvertimeRule Fields

Each `OvertimeRule` record defines a complete, self-contained set of thresholds:

| Field | Description | Example |
|-------|-------------|---------|
| `name` | Human-readable rule name | "California Labor Code", "IBEW Local 11 CBA" |
| `description` | Notes on source / authority | "Per CA Labor Code §510, effective 2024" |
| `weekly_ot_threshold` | Hours/week before OT (null = no weekly OT) | 40.0 |
| `weekly_dt_threshold` | Hours/week before double-time (null = none) | null |
| `daily_ot_threshold` | Hours/day before OT (null = no daily OT) | 8.0 |
| `daily_dt_threshold` | Hours/day before double-time (null = none) | 12.0 |
| `seventh_day_ot` | All hours on 7th consecutive day = OT | true |
| `seventh_day_dt_threshold` | Hours on 7th day before DT kicks in | 8.0 |
| `effective_date` | Rule version start date | 2024-01-01 |
| `is_active` | Soft-delete / version retirement | true |

Rules are **effective-dated and versioned** — when a CBA is renegotiated or a state law changes, a new rule version is created with a new `effective_date`. Historical time entries retain a reference to the rule version that was active when they were calculated.

### 10.3 Rule Assignment Scopes

A rule is assigned to a scope via `OvertimeRuleAssignments`. Supported scope types, from most specific to least:

| Scope Type | Assigned To | Use Case |
|------------|-------------|----------|
| `USER` | Individual user ID | One-off exception for a specific employee |
| `TEAM` | Team / crew / department | Union local, field crew, or department-wide CBA |
| `UNION` | Union entity | All members of a CBA union across teams |
| `PROJECT` | Project ID | Prevailing wage or client-mandated OT terms |
| `ENTITY` | Company/entity ID | Company-wide default policy |
| `STATE` | State code (e.g., `CA`) | State labor law baseline |

Multiple assignments can exist simultaneously. The engine resolves conflicts using the `priority` integer field — **lower number = higher priority**. This gives admins explicit control over which rule wins when two scopes overlap.

**Example resolution for a user:**

```
User: Maria, IBEW Local 11 member, Entity: Acme Corp, State: CA
Working on Project: Federal Highway Contract

Assignments in effect:
  priority 1  → USER:maria_id       → "Maria Custom" (e.g., medical accommodation schedule)
  priority 5  → PROJECT:highway_id  → "Federal Prevailing Wage OT"
  priority 10 → TEAM:ibew_local_11  → "IBEW Local 11 CBA"
  priority 20 → UNION:ibew_id       → "IBEW National Agreement"
  priority 30 → ENTITY:acme_id      → "Acme Corp Standard"
  priority 50 → STATE:CA            → "California Labor Code"

→ Engine applies: "Maria Custom" (priority 1 wins)
  If no USER assignment existed → "Federal Prevailing Wage OT" (priority 5)
```

### 10.4 Calculation Logic

For each time card submission the engine:

1. Identifies all `OvertimeRuleAssignments` in effect for the user, considering the time entry date, project, team memberships, union membership, entity, and state.
2. Selects the highest-priority (lowest integer) active rule.
3. Iterates over each day in the period:
   - Applies **daily thresholds first**: classifies hours as regular, OT, or DT per day.
4. Aggregates daily totals into weekly running totals.
5. Applies **weekly thresholds** to remaining regular hours (after daily OT/DT is removed).
6. Applies **seventh-day rule** if enabled and the user has worked 6 prior consecutive days in the period.
7. Writes `hours_regular`, `hours_overtime`, `hours_doubletime` to each `TimeEntries` record, along with `applied_rule_id` for audit traceability.
8. Recalculates on every edit; final authoritative calculation runs on submission.

### 10.5 Display in Time Card

- The time card footer shows: **Regular | OT | DT | Total**
- Cells where OT applies are highlighted amber; DT cells are highlighted red
- Tooltip on highlighted cells shows the rule that triggered classification (e.g., "IBEW Local 11 CBA — daily OT after 7h")
- Employees see a live preview as they type (client-side estimate); server is authoritative on save

### 10.6 Rule Management (Admin UI)

Admins and Entity Admins can:
- **Create** new `OvertimeRule` records with any combination of thresholds
- **Assign** rules to any scope (state, entity, team, union, project, or user)
- **Set effective dates** and optional expiry dates on assignments (handles CBA renewals)
- **Retire** old rule versions by setting `is_active = false`
- **Preview** how a rule change would affect a user or team before activating it
- **View assignment chain** for any user — see all active assignments and which one is currently winning

---

## 11. Project Management Features

### 11.1 Project Lifecycle

```
DRAFT → ACTIVE → INACTIVE → ARCHIVED
              ↑__________|
```

- **DRAFT:** Project is being set up; not yet visible in time card dropdowns.
- **ACTIVE:** Visible in time card dropdowns for assigned users.
- **INACTIVE:** Hidden from time card dropdowns; historical data preserved; can be reactivated.
- **ARCHIVED:** Fully read-only; hidden from all active views; accessible in historical reports only.

Status changes are logged in `AuditLog` with timestamp and user.

### 11.2 Project Health (RAG Status)

- Project Managers set health status manually: **Green | Amber | Red**
- A `health_notes` field explains the current status
- Health is displayed as a color-coded badge in the project list AG Grid
- Health history is tracked — each change is appended to a `ProjectHealthHistory` table
- Dashboard shows a RAG summary across all active projects (count per status)

### 11.3 Tasks & Subtasks

- Projects contain **Tasks**, which can contain **Subtasks** (one level of nesting for v1)
- Each task has: name, description, assigned user, status, due date, budget hours, budget dollars
- Time entries can be linked to a specific task (optional on entry, encouraged for billable projects)
- Task completion percentage is auto-calculated from logged hours vs. budget hours
- AG Grid tree view (grouped rows) used for task/subtask display

### 11.4 Milestones & Deadlines

- Milestones are date-anchored events on a project (e.g., "Design Review Complete")
- Each milestone has: name, due date, completed date, status (PENDING | COMPLETE | MISSED), notes
- Missed milestones (past due date, not completed) automatically show on the project RAG dashboard
- Project detail page includes a milestone timeline component

### 11.5 Project List View (AG Grid)

Default columns:

| Column | Notes |
|--------|-------|
| Code | Sortable, filterable |
| Name | Links to project detail |
| Entity | Visible to multi-entity admins |
| Status | Color-coded badge |
| Health | RAG badge |
| Manager | |
| Start / End Date | |
| Budget Hours | |
| Actual Hours | Auto-calculated from time entries |
| % Budget Used | Progress bar cell renderer |
| Budget $ | Configurable visibility (Finance + PM only) |
| Actual Cost $ | Configurable visibility |

---

## 12. Expense Tracking

### 12.1 Overview

Any user — from a large enterprise PM to an individual managing a fix-and-flip renovation — can log project expenses directly against a project and optional task. Expenses are categorized, tax-calculated, and routed through the same configurable approval workflow as time cards.

The expense system is deliberately simple to enter (mobile-friendly, quick single-line items) but rich enough to support formal project cost accounting, tax compliance, and reimbursement workflows.

### 12.2 Who Can Submit Expenses

| User Type | Can Submit | Scope |
|-----------|-----------|-------|
| Employee | Yes | Projects they are assigned to |
| Contractor | Yes | Projects they are assigned to |
| Project Manager / Owner | Yes | Any project they manage |
| Finance | No (view/approve only) | All projects in their entity |
| Admin | Yes | Any project |

> **Note for personal project owners:** A user without a formal "Project Manager" role title can still be the sole owner/manager of a project (e.g., a fix-and-flip investor). The system does not require enterprise structure — a single user can own a project, log all expenses, and be the sole approver or skip approval entirely if configured that way.

### 12.3 Expense Categories

| Category Code | Label | Notes |
|---------------|-------|-------|
| `LABOR` | Labor / Contractor Rates | Hours-based or flat pay; links to contractor estimates |
| `MATERIALS` | Materials & Supplies | Lumber, concrete, fixtures, consumables, etc. |
| `EQUIPMENT` | Equipment Rental | Machinery, tools, scaffolding, etc. |
| `TRAVEL` | Travel & Mileage | Gas, flights, per diem, mileage reimbursement |
| `SUBCONTRACTOR` | Subcontractor Invoice | Lump-sum payment to a subcontractor |
| `PERMITS` | Permits & Fees | Building permits, inspections, utility hookups |
| `OTHER` | Miscellaneous | Free-form; requires a description; stored with `category = OTHER` |

Additional categories can be added by an Admin. All categories (including custom ones) write to the same `Expenses` table — there is no separate table per category.

### 12.4 Expense Entry Fields

Each expense line item captures:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `expense_id` | int | PK | |
| `project_id` | int | Yes | FK → Projects |
| `task_id` | int | No | FK → Tasks (optional task linkage) |
| `submitted_by` | int | Yes | FK → Users |
| `expense_date` | date | Yes | Date incurred (not submission date) |
| `category` | enum/varchar | Yes | See category table above |
| `vendor_name` | varchar(255) | No | Supplier, contractor, or vendor name |
| `description` | varchar(1000) | Yes | What the expense is for |
| `quantity` | decimal | No | e.g., number of units, hours, miles |
| `unit_cost` | decimal(12,4) | No | Cost per unit (used with quantity) |
| `subtotal` | decimal(12,2) | Yes | Pre-tax amount (auto = quantity × unit_cost, or manual) |
| `tax_rate_id` | int | No | FK → TaxRates; drives auto-calculation |
| `tax_amount` | decimal(12,2) | No | Auto-calculated or manually overridden |
| `tax_override` | bool | No | True if tax_amount was entered manually |
| `is_tax_exempt` | bool | Yes | If true, tax_amount forced to 0 |
| `total_amount` | decimal(12,2) | Yes | subtotal + tax_amount |
| `is_billable` | bool | Yes | Whether expense is billable to a client |
| `is_reimbursable` | bool | Yes | Whether expense is reimbursable to the submitter |
| `receipt_file_key` | varchar | No | Blob storage path for attached receipt image/PDF |
| `status` | enum | Yes | `DRAFT` \| `SUBMITTED` \| `IN_REVIEW` \| `APPROVED` \| `REJECTED` \| `LOCKED` |
| `approval_workflow_id` | int | No | FK → ApprovalWorkflows (defaults to project/entity default) |
| `notes` | varchar(1000) | No | Internal notes |
| `created_at` | datetime | Yes | |
| `updated_at` | datetime | Yes | |

### 12.5 Tax Calculation

#### Tax Rate Configuration

Tax rates are managed by Admins and stored in a `TaxRates` table:

```sql
TaxRates
  tax_rate_id,
  entity_id,
  name,                   -- e.g., "California Sales Tax", "Use Tax 8.75%", "No Tax"
  tax_type,               -- SALES | USE | VAT | EXCISE | OTHER
  rate_percent,           -- e.g., 8.75 (stored as decimal, not fraction)
  state_code,             -- optional: associate with a state for auto-lookup
  is_default (bool),      -- entity-wide default applied when no rate is specified
  is_active (bool),
  effective_date,
  created_at
```

Multiple tax rates can exist per entity (e.g., a company operating in CA and TX would have separate rates for each). Rates are effective-dated so historical expenses remain accurate after a rate change.

#### Calculation Behavior

1. **Auto-calculation (default):** When a `tax_rate_id` is selected, `tax_amount = subtotal × (rate_percent / 100)`, rounded to 2 decimal places. `total_amount = subtotal + tax_amount`.
2. **Manual override:** If the user enters a specific `tax_amount` directly, `tax_override = true` and `tax_rate_id` is stored for reference but not used in calculation.
3. **Tax exempt:** If `is_tax_exempt = true`, `tax_amount` is forced to 0 regardless of rate or override. `total_amount = subtotal`.
4. **State lookup:** When a workplace address `state_code` is on the expense (inferred from project job site or entered manually), the system suggests the matching `TaxRate` for that state as the default.

#### Tax Types Supported

| Type | Description |
|------|-------------|
| `SALES` | Standard sales tax on purchased goods |
| `USE` | Use tax on goods purchased outside the state for use in-state |
| `EXCISE` | Excise tax on specific goods (fuel, equipment, etc.) |
| `VAT` | Value-added tax (for international entities) |
| `OTHER` | Custom tax with free-form description |

Multiple tax types can be applied to a single expense by entering separate line items or using a combined rate. For v1, a single `tax_rate_id` per expense line is supported; composite tax (e.g., state + county + city) is handled by creating a combined rate record (e.g., "LA County Combined 10.25%").

### 12.6 Receipt Attachment

- Users can attach a receipt image (JPEG, PNG) or PDF to any expense
- Receipts are uploaded to blob storage via the same pipeline as progress report photos
- Mobile app supports camera capture of receipts at the time of entry
- Receipts are viewable by approvers in the review UI
- Receipt thumbnails appear in expense list views

### 12.7 Expense Approval

Expense reports follow the **same configurable approval workflow** as time cards (Section 15). The workflow type is `EXPENSE` to allow entities to configure separate approval chains for expenses vs. time cards if desired, while still using the same `ApprovalWorkflows` and `ApprovalStages` tables.

- Expenses can be submitted individually or batched into an **Expense Report** (a grouping of multiple expense line items for the same period)
- `ExpenseReports` table groups line items; the approval workflow operates at the report level
- Individual ad-hoc expenses can also be submitted without a report container
- Approved expenses feed into the project's cost actuals automatically

### 12.8 Expense Report DB Schema

```sql
ExpenseReports
  report_id, entity_id, submitted_by, project_id,
  period_id (nullable),         -- optional weekly period grouping
  title,                        -- e.g., "Site Materials - Week of Mar 10"
  status,                       -- DRAFT | SUBMITTED | IN_REVIEW | APPROVED | REJECTED | LOCKED
  total_subtotal,               -- sum of line item subtotals
  total_tax,                    -- sum of line item tax_amounts
  total_amount,                 -- sum of line item total_amounts
  submitted_at, approved_at, approved_by,
  rejection_reason,
  auto_approved (bool),
  created_at, updated_at

Expenses                        -- individual line items (see Section 12.4)
  expense_id, report_id (nullable), ...  -- can belong to a report or be standalone

TaxRates                        -- see Section 12.5
  tax_rate_id, entity_id, name, tax_type, rate_percent,
  state_code, is_default, is_active, effective_date, created_at
```

---

## 13. Contractor Cost Estimation

### 13.1 Overview

The contractor cost estimation module is designed for anyone managing hired work — from a construction company dispatching subcontractors to an individual investor overseeing a fix-and-flip rehab. It allows users to build detailed cost estimates before work starts, track actuals as expenses and time entries are recorded, and compare the two week by week.

Estimates can be built manually inside the system or **imported from an Excel spreadsheet** (e.g., a BNI cost database export, a custom estimating template, or a contractor's bid sheet).

### 13.2 Estimation Methods

Three estimation methods are supported and can be mixed within the same project:

| Method | Description | Best For |
|--------|-------------|----------|
| **Hours × Rate** | Estimated hours multiplied by a contractor's hourly or daily rate | Labor-heavy scopes where hours are known |
| **Fixed Bid** | A lump-sum amount for a defined scope of work | Subcontracted work with a flat quote |
| **Unit Cost** | Quantity × unit price (e.g., 200 sq ft × $4.50/sq ft) | Materials, tiling, drywall, landscaping |

All three methods produce an `estimated_cost` that feeds into the project budget and estimate-vs-actual comparison.

### 13.3 ContractorEstimates Table

```sql
ContractorEstimates
  estimate_id,
  project_id,               -- FK → Projects
  task_id (nullable),       -- FK → Tasks; ties estimate to a task or phase
  entity_id,
  contractor_user_id (nullable),  -- FK → Users (if assigned to a known contractor)
  contractor_name,          -- free text if contractor is not a system user
  estimation_method,        -- HOURS_RATE | FIXED_BID | UNIT_COST
  description,              -- scope of work description

  -- Hours × Rate fields
  estimated_hours,
  hourly_rate,

  -- Fixed Bid fields
  bid_amount,

  -- Unit Cost fields
  quantity,
  unit_label,               -- e.g., "sq ft", "linear ft", "each"
  unit_cost,

  -- Derived
  estimated_cost,           -- computed: hours×rate, bid_amount, or quantity×unit_cost
  estimated_tax_rate_id,    -- FK → TaxRates (optional; for taxable contractor services)
  estimated_tax_amount,     -- auto-calculated or overridden
  estimated_total,          -- estimated_cost + estimated_tax_amount

  -- Tracking
  import_source,            -- NULL | 'BNI' | 'EXCEL' | 'MANUAL'
  import_batch_id,          -- groups estimates imported together
  phase_label,              -- e.g., "Foundation", "Framing", "Finish Work"
  period_id (nullable),     -- planned period/week for this work
  status,                   -- DRAFT | ACTIVE | COMPLETE | CANCELLED
  notes,
  created_by, created_at, updated_at
```

### 13.4 Excel Import

Users can import a cost estimate spreadsheet — from BNI, a contractor bid, or their own template — directly into the estimating module.

**Import flow:**

```
1. User navigates to Project → Estimates → Import
2. Uploads .xlsx or .csv file
3. System displays a column mapping UI:
     Your Column          →   System Field
     "Description"        →   description
     "Labor Hours"        →   estimated_hours
     "Rate/Hr"            →   hourly_rate
     "Material Cost"      →   bid_amount
     "Phase"              →   phase_label
     "Task"               →   task_id (matched by name)
     [Add mapping...]
4. User previews first 10 rows with mapped values
5. User selects estimation method per row (or bulk-assigns)
6. User confirms import
7. System creates ContractorEstimates records in DRAFT status
8. User can review, edit, and activate
```

**Import rules:**
- Rows with unmappable data are flagged for review, not silently dropped
- Import creates an `import_batch_id` so the entire import can be reviewed or rolled back
- Re-importing the same file warns about duplicate estimates (matched by description + task + phase)
- Supported formats: `.xlsx`, `.xls`, `.csv`
- Max import size: 5,000 rows per file

**BNI-specific notes:**
- BNI cost database exports typically include unit costs, quantities, and phase codes
- The column mapper ships with a saved "BNI Standard" mapping preset that can be selected to skip manual mapping
- Unit cost rows from BNI are imported as `estimation_method = UNIT_COST`

### 13.5 Estimate vs. Actual Tracking

As work progresses, actual costs accumulate from two sources:

1. **Time entries** — hours logged by contractors against the project/task, multiplied by their loaded rate
2. **Expenses** — approved expense line items (category `LABOR`, `SUBCONTRACTOR`, `MATERIALS`, etc.) logged against the project/task

The system computes running actuals and compares them to estimates:

| Metric | Source |
|--------|--------|
| Estimated Cost | `ContractorEstimates.estimated_total` (sum per task/phase) |
| Actual Labor Cost | `TimeEntries.hours_regular × Users.loaded_rate` (approved entries) |
| Actual Expense Cost | `Expenses.total_amount` (approved expenses) |
| Total Actual Cost | Actual Labor + Actual Expense |
| Variance $ | Estimated Cost − Total Actual Cost |
| Variance % | (Variance / Estimated Cost) × 100 |

### 13.6 Weekly Estimate vs. Actual View

The planning view allows PMs and project owners to track estimates against actuals week by week:

- Rows: tasks or phases
- Columns: Week 1 | Week 2 | ... | Week N | Total
- Each cell shows: Estimated $ / Actual $ / Variance
- Color coding: green (under budget), amber (>80% of estimate), red (over estimate)
- Drill-down: clicking a cell shows the individual time entries and expenses that make up the actual

### 13.7 Estimate Alerts

- When actuals reach **80%** of the estimate for a task, the PM receives an amber alert
- When actuals **exceed** the estimate for a task, the PM receives a red alert
- Both thresholds are configurable per entity
- Alerts appear in-app and via email, same as budget alerts

### 13.8 Estimation for Personal Project Owners (Fix & Flip / Fix to Rent)

The system does not require enterprise structure. A single user can:

- Create a project (e.g., "123 Oak St Rehab")
- Add tasks/phases (Foundation, HVAC, Electrical, Finish Work)
- Import a contractor bid sheet or BNI estimate
- Log their own expenses as work is performed
- Track estimate vs. actual solo, without a team or approval chain
- Export a full project cost report for their accountant or lender

The approval workflow for solo project owners defaults to **no approval required** (auto-approve on submit), configurable at the project level.

---

## 14. Cost Accounting & Budget Tracking

### 14.1 Overview

The system tracks project financials at two levels:
- **Budget vs. Actuals (Hours)** — available to all PM+ roles
- **Budget vs. Actuals (Cost $)** — visible to Finance and Entity Admin only

### 14.2 Loaded Rates

Each user has a `loaded_rate` (cost per hour) stored on their user record, visible only to Finance and Admin. This rate is used to calculate actual labor cost from logged hours. Rates are effective-dated to support rate changes mid-project.

### 14.3 Weekly Estimate vs. Actual

Project Managers can enter **weekly estimates** per project (and optionally per task) in advance:

- A weekly planning view shows the current and next 4 weeks
- PMs enter estimated hours and estimated cost per project/task per week
- After the week closes, actuals (from approved time cards) are pulled in automatically
- Variance (estimated vs. actual) is calculated and displayed

### 14.4 Cost Reports

| Report | Description |
|--------|-------------|
| Weekly Estimate vs. Actual | Side-by-side hours and cost, by week, per project |
| Project Cost Summary | Total budget vs. spent vs. remaining (hours + $) |
| Task-Level Cost Breakdown | Budget vs. actual per task and subtask |
| Entity Cost Roll-up | Aggregate cost across all projects in an entity |

### 14.5 Budget Alerts

- When actual hours reach **75%** of budget hours, an amber alert is shown on the project card
- When actual hours reach **90%**, a red alert is shown and the PM receives an email notification
- When actual cost reaches **90%** of budget dollars, Finance is notified
- All thresholds are configurable per entity

---

## 15. Approval Workflows

### 15.1 Overview

Approval workflows are fully configurable and shared across both **time cards** and **expense reports**. Each entity has a default workflow per document type (`TIME_CARD` or `EXPENSE`), and individual projects may override either. Workflows are composed of ordered **stages**, each stage having one or more approvers.

### 15.2 Workflow Configuration

**Single-manager (simple):**
```
Stage 1: Direct Manager (any one approver sufficient)
```

**Multi-level:**
```
Stage 1: Direct Manager (any one of [Manager A, Manager B])
Stage 2: Department Head (all of [VP Engineering] required)
Stage 3: Finance (any one of [Finance Team])
```

**Per stage settings:**
- `requires_all`: if true, all listed approvers must approve before the stage advances (AND logic); if false, any one approver is sufficient (OR logic)
- `escalation_after_hours`: if set, the time card auto-escalates to the next stage if not acted upon within N hours

### 15.3 Auto-Approval

- Workflows can be configured with `auto_approve_after_days`
- If a time card is in `SUBMITTED` or `IN_REVIEW` status and no action is taken within the configured days, it is automatically approved and flagged `auto_approved = true`
- Auto-approved cards are visible as such in reports (for audit purposes)
- Auto-approval can be disabled entirely per entity

### 15.4 Rejection & Re-submission

Rejection behavior differs between time cards and expense reports because the downstream impact and the parties involved are different. Each workflow has a `rejection_return_policy` field that governs where the document goes on rejection.

#### Time Card Rejection

- Any approver at any stage can reject with a mandatory written reason
- Rejected time cards always return to **Stage 1** (`rejection_return_policy = STAGE_1`)
- Rationale: time cards are a payroll input — any correction should be re-reviewed by all stages
- The employee is notified; they can edit and re-submit
- The full rejection reason and re-submission history are preserved in `AuditLog`

#### Expense Report Rejection

Expense rejection routing depends on **which stage** the rejection occurs at and the workflow's `rejection_return_policy`:

| Rejection Policy | Rejected at Stage 1 | Rejected at Stage 2+ | Use Case |
|-----------------|--------------------|--------------------|----------|
| `STAGE_1` | Returns to submitter | Returns to Stage 1 (PM re-approves before Finance) | High-oversight workflows |
| `SUBMITTER_ONLY` | Returns to submitter | Returns directly to submitter, skipping Stage 1 re-review | Finance rejection shouldn't re-burden PM |

- The recommended default for expense workflows is `SUBMITTER_ONLY` — if Finance rejects at Stage 2 for a receipt issue, it goes back to the submitter directly rather than forcing the PM to re-approve an already-reviewed expense
- The submitter fixes the issue, re-submits, and the document **re-enters at the stage that rejected it** (not Stage 1), unless the workflow is configured otherwise
- Rejection reason is required and visible to all approvers in the chain on re-submission

#### Rejection State Machine

```
DRAFT → SUBMITTED → IN_REVIEW (stage N) → APPROVED
                         ↓ reject
                      REJECTED
                         ↓ submitter edits & re-submits
              (TIME_CARD) → Stage 1
              (EXPENSE, SUBMITTER_ONLY) → Stage that rejected
```

### 15.5 Approval UI

- Approvers see a dedicated **Pending Approvals** inbox in the nav
- Each card shows: employee name, period, total hours, OT hours, projects, and notes
- Approvers can approve, reject (with reason), or request info (comment)
- Bulk approve is supported for straightforward cards

---

## 16. Notifications & Reminders

### 16.1 Notification Events

| Event | Recipients | Channel |
|-------|-----------|---------|
| Time card submitted | Approver(s) at Stage 1 | Email |
| Time card approved | Employee | Email |
| Time card rejected | Employee | Email + in-app |
| Time card advanced to next stage | Next stage approvers | Email |
| Auto-approval triggered | Employee + original approvers | Email |
| Missing time card (no submission by threshold day) | Employee + their manager | Email |
| **Expense report submitted** | **Approver(s) at Stage 1** | **Email** |
| **Expense report approved** | **Submitter** | **Email** |
| **Expense report rejected** | **Submitter** | **Email + in-app** |
| **Expense estimate alert (80% of task estimate reached)** | **Project Manager / Owner** | **Email + in-app** |
| **Expense estimate exceeded (actuals > estimate)** | **Project Manager / Owner** | **Email + in-app** |
| Budget alert (75% / 90%) | Project Manager | Email + in-app |
| Cost budget alert (90%) | Finance, Entity Admin | Email |
| Milestone past due | Project Manager | Email + in-app |
| Period lock imminent (48h warning) | All employees with DRAFT cards | Email |

### 16.2 Reminder Schedule

- **Monday 9am:** Reminder to employees who have not opened their time card for the prior week
- **Wednesday 9am:** Reminder if time card is still in DRAFT and not submitted
- **Friday 3pm:** Final reminder if time card is still not submitted
- All reminder times are in the entity's configured timezone
- Reminder schedule is configurable per entity (days and times)

### 16.3 In-App Notifications

- Bell icon in nav shows unread notification count
- Notification panel lists recent events with timestamp and action link
- Notifications are marked read on click or via "mark all read"

---

## 17. Reporting & Exports

### 17.1 Report Catalog

| Report | Description | Roles |
|--------|-------------|-------|
| My Time Card History | Employee's own submissions by period | Employee+ |
| Team Time Summary | Hours by employee by period (filterable) | PM, Approver, Admin |
| Project Hours Detail | Hours per project broken down by user and task | PM, Finance, Admin |
| Billable Hours Report | Billable vs. non-billable by project and user | PM, Finance, Admin |
| Overtime Report | OT and DT hours by employee, period, applied rule | Finance, Admin |
| Weekly Estimate vs. Actual | PM-entered estimates vs. approved actuals (hours + $) | PM, Finance, Admin |
| Project Cost Summary | Budget vs. actual cost (labor + expenses combined) | Finance, Admin |
| Task-Level Cost Breakdown | Labor + expense cost per task/subtask vs. estimate | PM, Finance, Admin |
| **Expense Report Detail** | **All expense line items by project, category, date, and submitter** | **PM, Finance, Admin** |
| **Expense by Category** | **Totals grouped by category (materials, labor, permits, etc.)** | **PM, Finance, Admin** |
| **Tax Summary** | **Tax amounts by tax type, rate, and state across all expenses** | **Finance, Admin** |
| **Contractor Estimate vs. Actual** | **Side-by-side estimate and actuals per contractor/task/phase by week** | **PM, Finance, Admin** |
| **Import Batch Review** | **All estimates from a specific Excel import batch with status** | **PM, Admin** |
| Entity Roll-up | Cross-project summary for an entity (labor + expenses) | Entity Admin, Finance |
| Cross-Entity Roll-up | Org-wide summary across entities | Super Admin, Finance |
| Payroll Export | Hours by employee formatted for payroll system | Finance, Admin |
| Contractor Utilization | Hours and expense totals per contractor per project | PM, Admin |

### 17.2 Export Formats

- **Excel (.xlsx):** Formatted workbook with multiple tabs (summary + detail)
- **CSV:** Raw data export for custom processing
- **PDF:** Formatted report with entity branding, suitable for distribution
- All exports are generated asynchronously via Celery task; user is notified when ready

### 17.3 AG Grid Report Features

All reports rendered in AG Grid support:
- Column sorting and filtering
- Column show/hide toggle
- Group-by (e.g., group by project, then by user)
- Pinned summary rows (totals)
- Export directly from grid toolbar

---

## 18. Integrations

### 18.1 Active Directory / SSO

- Supports **Azure AD (OIDC/OAuth2)** and **SAML 2.0** for enterprise SSO
- Users are provisioned on first SSO login (JIT provisioning); role defaults are configurable
- User attributes (name, email, department) synced from directory on each login
- Local username/password fallback available for contractors without AD accounts
- SSO configuration is per-entity (each entity can have its own IdP)

### 18.2 Payroll System Sync

- Outbound sync exports approved time card data in a configurable format
- Supports two modes:
  - **File drop (SFTP):** Generates a formatted CSV/fixed-width file on a schedule and drops it to a configured SFTP endpoint
  - **Webhook push:** POSTs a JSON payload to a configured endpoint when time cards are approved
- Sync payload includes: employee ID, period, regular hours, OT hours, DT hours, cost center, leave codes
- Sync runs automatically after period lock or can be triggered manually by Finance
- Sync status and logs visible in Admin panel

### 18.3 Email

- Transactional email via SMTP (configurable relay) or SendGrid
- Email templates are per-entity (support entity branding/logo)
- All outbound emails logged for audit purposes

---

## 19. Mobile Application

### 17.1 Overview

The Project Tracker mobile app is a **React Native** application for iOS and Android, targeting field workers, contractors, and employees who need to log time, clock in/out, and submit progress reports from job sites. It shares the same REST API as the web application.

The mobile app is purpose-built for the field — simple, fast, and focused on the three primary workflows:

1. **Clock In / Clock Out** with GPS verification and worker type confirmation
2. **Time Entry** for the current day or week
3. **Progress Reports** with photos, notes, and location context

### 17.2 Tech Stack — Mobile

| Layer | Technology | Notes |
|-------|------------|-------|
| Framework | React Native | iOS + Android from shared codebase |
| Navigation | React Navigation | Stack + bottom tab navigation |
| State | Zustand | Lightweight client state |
| API Client | Axios + React Query | Caching, background refresh, retry |
| Camera | React Native Vision Camera | Photo capture for progress reports |
| Geolocation | React Native Geolocation Service | GPS clock-in coordinates |
| Maps | React Native Maps | Job site map display |
| Storage | MMKV | Fast local key-value (tokens, draft state) |
| Push Notifications | Firebase Cloud Messaging (FCM) | Time card reminders, approval alerts |
| Auth | JWT (same tokens as web) + Biometric unlock | Face ID / fingerprint for app re-entry |

### 17.3 Clock-In Flow

Clock-in is the primary action when starting work on a job site. The flow is:

```
1. User opens app → taps "Clock In"
2. App requests GPS permission (if not already granted)
3. App captures GPS coordinates (lat, lng, accuracy in meters)
4. Clock-In Confirmation screen shown:
     ┌─────────────────────────────┐
     │  Project: [dropdown]        │
     │                             │
     │  Worker Type: Contractor    │
     │  (assigned by admin)        │
     │                             │
     │  📍 You appear to be at:    │
     │     Site Alpha              │
     │                             │
     │  [ Confirm & Clock In ]     │
     └─────────────────────────────┘
5. User selects project from active project dropdown
6. App optionally matches GPS coordinates to nearest workplace
   within geofence radius — shows "You appear to be at: Site Alpha"
7. Clock-in record saved to TimeEntries (clock_in_at, lat, lng,
   worker_type, workplace_id)
8. Running timer shown on home screen
```

**Worker type display rules:**
- Worker type is **read-only on the mobile app** — it is always pulled from the user's `user_type` field as assigned by an Admin or Manager
- The clock-in screen displays the assigned worker type as informational context only; the user cannot change it
- If a worker's classification needs to change (e.g., a contractor hired full-time), an Admin or Manager updates `Users.user_type` in the web admin UI — this takes effect on the next clock-in
- All time entries store `clock_in_worker_type` as a snapshot of the type at the time of the entry, so historical records are unaffected by future reclassifications

**GPS accuracy handling:**
- If GPS accuracy is > 100m, a warning is shown: "Low GPS accuracy — location may not be precise"
- Clock-in is still allowed; accuracy value is stored for review
- If GPS is entirely unavailable (airplane mode, denied), user may clock in without location with a mandatory acknowledgment

**Geofence validation (optional, configurable per entity):**
- If the entity has geofence enforcement enabled, a clock-in outside the configured radius of any assigned workplace triggers a warning
- Hard block (prevent clock-in) vs. soft warning (allow with flag) is configurable per entity

### 17.4 Clock-Out Flow

```
1. User taps "Clock Out" on the running timer
2. App captures GPS at clock-out
3. Elapsed time is shown: "You worked 7h 23m"
4. Optional: Add a brief note for the day
5. Clock-out saved (clock_out_at, lat, lng)
6. Hours auto-populated into the day's time card entry
```

### 17.5 Progress Reports

Progress reports allow field workers to document work status, conditions, and milestones with photos and notes, linked directly to a project and optionally to a task.

**Creating a progress report:**

```
1. User taps "+ Progress Report"
2. Selects project (active projects only) and optional task
3. Enters report title and body text (e.g., "Framing complete — north wall")
4. Optional: Weather / site condition notes
5. Photo attachment:
   - Tap camera icon → opens device camera OR photo library
   - Multiple photos supported (up to 10 per report)
   - Each photo can have an optional caption
   - EXIF GPS data extracted if available and stored
   - Photos are compressed before upload (max 2MB per photo)
6. Location is auto-tagged from current GPS
7. Submit → report and photos uploaded in background
   (drafts saved locally in MMKV if connectivity is poor)
```

**Photo upload behavior:**
- Photos are uploaded to blob storage (Azure Blob or S3-compatible) via the API
- Upload is chunked and retried automatically on failure
- User sees upload progress per photo
- Reports with pending photo uploads are shown as "Uploading..." in the history list
- Once all photos are uploaded, the report status changes to "Submitted"

**Viewing progress reports (mobile):**
- History tab shows all reports submitted by the user, with thumbnail previews
- PM and Admin roles can view all reports for their assigned projects in the web UI (Section 19)

### 17.6 Mobile Time Card

- Simplified daily view: user sees today's date with a vertical list of project rows
- Tap a row to edit hours for that day
- Add a new project row via the active project dropdown
- Week summary tab shows Mon–Sun totals and OT breakdown
- Submit button available once all required entries are complete
- Full history accessible (read-only for locked periods)

### 17.7 Mobile Navigation Structure

```
Bottom Tab Bar:
├── Home          — Clock in/out, running timer, today's hours summary
├── Time Card     — Current week entry, day picker, submit
├── Reports       — Create progress report, photo capture, history
└── Profile       — User info, address, worker type, settings, logout

Stack screens (pushed from tabs):
├── Project Select  — Active project picker for clock-in or time entry
├── Report Detail   — View submitted report + photos
├── Report Editor   — Create / edit in-progress report
└── Notifications   — Push notification inbox
```

### 17.8 Push Notifications (Mobile)

| Trigger | Notification |
|---------|-------------|
| Time card not submitted by Wednesday | "Don't forget — submit your time card for this week" |
| Time card approved | "Your time card for [week] has been approved" |
| Time card rejected | "Your time card was returned — tap to review feedback" |
| Progress report uploaded successfully | Silent confirmation (badge update) |
| New project assigned | "You've been added to project [name]" |

---

## 20. API Design

### 16.1 Conventions

- Base URL: `/api/v1/`
- Auth: `Authorization: Bearer <jwt_token>`
- Pagination: `?page=1&page_size=50`
- Filtering: `?status=ACTIVE&entity_id=2`
- All timestamps: ISO 8601 UTC

### 16.2 Key Endpoints

#### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | Username/password login → JWT |
| POST | `/auth/sso/callback` | SSO OIDC/SAML callback → JWT |
| POST | `/auth/refresh` | Refresh JWT token |
| POST | `/auth/logout` | Revoke refresh token |

#### Projects
| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | `/projects` | List projects (filtered, paginated) | PM, Admin, Finance |
| GET | `/projects/active` | Active projects for current user (time card use) | All |
| POST | `/projects` | Create project | PM, Admin |
| GET | `/projects/{id}` | Project detail | PM, Admin, Finance |
| PATCH | `/projects/{id}` | Update project (status, health, etc.) | PM, Admin |
| GET | `/projects/{id}/tasks` | List tasks for project | PM, Admin |
| POST | `/projects/{id}/tasks` | Create task | PM, Admin |
| PATCH | `/projects/{id}/tasks/{task_id}` | Update task | PM, Admin |
| GET | `/projects/{id}/milestones` | List milestones | PM, Admin |
| POST | `/projects/{id}/milestones` | Create milestone | PM, Admin |
| GET | `/projects/{id}/budget` | Budget vs. actuals summary | PM, Finance, Admin |

#### Time Cards
| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | `/timecards` | List time cards for current user | Employee |
| GET | `/timecards/{period_id}` | Get specific time card | Employee, PM, Admin |
| PUT | `/timecards/{period_id}/entries` | Save/replace all entries for a period | Employee |
| POST | `/timecards/{period_id}/submit` | Submit time card | Employee |
| POST | `/timecards/{period_id}/approve` | Approve (current stage) | Approver, Admin |
| POST | `/timecards/{period_id}/reject` | Reject with reason | Approver, Admin |
| POST | `/timecards/{period_id}/unlock` | Unlock submitted card for edit | PM, Admin |
| GET | `/timecards/pending` | Approvals inbox for current user | Approver, Admin |

#### Overtime
| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | `/overtime/jurisdictions` | List configured jurisdictions | Admin |
| POST | `/overtime/jurisdictions` | Create jurisdiction | Admin |
| PATCH | `/overtime/jurisdictions/{id}` | Update jurisdiction | Admin |
| GET | `/overtime/calculate` | Preview OT calc for a user/period | Admin, Finance |

#### Reporting
| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | `/reports/project-hours` | Project hours (filtered) | PM, Finance, Admin |
| GET | `/reports/billable-hours` | Billable vs. non-billable | PM, Finance, Admin |
| GET | `/reports/overtime` | OT report by user/period | Finance, Admin |
| GET | `/reports/cost-summary` | Project cost budget vs. actuals | Finance, Admin |
| GET | `/reports/weekly-estimates` | Estimate vs. actual by week | PM, Finance, Admin |
| GET | `/reports/payroll-export` | Payroll-formatted data | Finance, Admin |
| POST | `/reports/export` | Queue async export (xlsx/pdf/csv) | PM, Finance, Admin |
| GET | `/reports/export/{job_id}` | Check export status / download | PM, Finance, Admin |

#### Admin
| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | `/admin/users` | List users | Admin |
| POST | `/admin/users` | Create user | Admin |
| PATCH | `/admin/users/{id}` | Update user / role | Admin |
| GET | `/admin/entities` | List entities | Super Admin |
| POST | `/admin/entities` | Create entity | Super Admin |
| GET | `/admin/workflows` | List approval workflows | Admin |
| POST | `/admin/workflows` | Create workflow | Admin |
| PATCH | `/admin/workflows/{id}` | Update workflow | Admin |
| GET | `/admin/periods` | List time periods | Admin |
| POST | `/admin/periods/{id}/lock` | Lock a period | Admin, Finance |

---

## 21. Front End Component Plan

### 17.1 Application Routes

| Route | Component | Notes |
|-------|-----------|-------|
| `/login` | LoginPage | SSO redirect + local login form |
| `/dashboard` | Dashboard | RAG summary, pending approvals count, missing time card alerts |
| `/projects` | ProjectList | AG Grid with toolbar |
| `/projects/new` | ProjectForm | Create project |
| `/projects/:id` | ProjectDetail | Tabs: Overview, Tasks, Milestones, Budget, Time |
| `/timecard` | TimeCard | Current week editable grid |
| `/timecard/:periodId` | TimeCard | Historical view (read-only if locked) |
| `/approvals` | ApprovalsInbox | Pending time cards for approver |
| `/approvals/:timecardId` | ApprovalDetail | Full time card review + action |
| `/reports` | ReportCenter | Report selector, filters, AG Grid output |
| `/admin` | AdminShell | Sub-routes for users, entities, workflows, periods |
| `/admin/users` | UserManagement | AG Grid user list |
| `/admin/workflows` | WorkflowBuilder | Drag-and-drop stage configuration |
| `/admin/jurisdictions` | OvertimeAdmin | Jurisdiction table + rule editor |

### 17.2 Shared Components

- `ProjectCodeSelect` — Svelte async select, calls `/projects/active`, used in time card rows
- `StatusBadge` — Color-coded pill for project status and time card status
- `RAGBadge` — Red/Amber/Green health indicator
- `HoursCell` — AG Grid custom cell renderer with OT highlighting
- `BudgetProgressBar` — Color-transitions at 75% (amber) and 90% (red)
- `NotificationBell` — Bell icon with unread badge, notification panel
- `ApprovalTimeline` — Visual stage-by-stage workflow progress indicator
- `MilestoneTimeline` — Horizontal timeline component for project detail

### 17.3 AG Grid Strategy

| View | Row Model | Notes |
|------|-----------|-------|
| Project list | Server-Side | Sorting, filtering, pagination server-side |
| Task list | Client-Side | Tree data (tasks + subtasks) |
| Time card entry | Client-Side | Editable cells, max ~20 rows |
| Approvals inbox | Server-Side | Filtered by approver |
| All reports | Server-Side | Large datasets, grouping server-side |

---

## 22. Security Requirements

- All API endpoints require authentication. No anonymous access.
- JWT access tokens expire after **8 hours**; refresh tokens expire after **7 days**.
- Entity isolation enforced at API layer (all queries scoped by `entity_id` from token claims) and at DB layer (Row-Level Security policies).
- Contractor tokens include an explicit `is_contractor: true` claim; API enforces field-level data exclusion (no rate or cost data in any response).
- All DB queries use SQLAlchemy ORM with parameterized statements. Raw SQL is prohibited.
- Passwords (for non-SSO accounts) hashed with **bcrypt** (minimum cost factor 12).
- HTTPS enforced in all environments (TLS 1.2 minimum).
- All create/update/delete operations written to `AuditLog` with user ID, IP address, old and new values.
- MSSQL credentials stored in environment variables / secrets manager. Never in source code or config files.
- RBAC enforced at the API layer. The UI may hide elements, but the API is the authoritative access control boundary.
- Rate limiting on auth endpoints: max 10 login attempts per 15 minutes per IP.
- SSO token validation follows OIDC/SAML spec; tokens are verified against IdP public keys on every request.

---

## 23. Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| Performance | Page load < 2s on LAN; AG Grid renders 1,000 rows < 500ms; OT calculation < 200ms per time card |
| Availability | 99.5% uptime during business hours (Mon–Fri 6am–8pm, entity local time) |
| Scalability | Support 500 concurrent users across all entities without degradation |
| Browser Support | Latest two versions of Chrome, Edge, Firefox; Safari 16+ |
| Mobile | Core time card workflows functional on iOS Safari and Android Chrome (responsive web) |
| Accessibility | WCAG 2.1 AA for all primary workflows |
| Data Retention | Time entries retained 7 years (accounting / audit requirement) |
| Backup | MSSQL full backup nightly; differential every 4 hours; restore tested monthly |
| Logging | Structured JSON logs; errors forwarded to centralized log aggregator |
| Async Jobs | Celery task queue; failed jobs retry 3 times with exponential backoff; dead-letter queue for manual inspection |

---

## 24. Delivery Milestones

| Phase | Deliverable | Target |
|-------|-------------|--------|
| Phase 1 — Foundation | DB schema, multi-entity model, address tables, user auth (local + SSO), basic project CRUD, login UI | Week 4 |
| Phase 2 — Time Card Core | Time card entry, active project filtering, leave codes, billable flag, daily notes, submit flow | Week 7 |
| Phase 3 — Overtime Engine | OT rule config, assignment scopes, daily/weekly/7th-day calculation, address-based routing | Week 9 |
| Phase 4 — Project Features | Tasks/subtasks, milestones, RAG health, workplace addresses, project job site management | Week 11 |
| Phase 5 — Expense Tracking | Expense categories, tax rates, auto-calc tax, manual override, tax-exempt flag, receipt upload, expense reports | Week 14 |
| Phase 6 — Contractor Estimation | Hours×rate, fixed bid, unit cost estimates; Excel/BNI import; column mapper; estimate vs. actual tracking | Week 17 |
| Phase 7 — Cost Accounting | Budget tracking, loaded rates, combined labor+expense actuals, weekly estimate vs. actual, cost reports | Week 19 |
| Phase 8 — Approvals | Workflow builder for time cards + expense reports; multi-stage; auto-approve; rejection flow | Week 21 |
| Phase 9 — Notifications | Email + in-app notifications, reminder scheduler, expense alerts, estimate overage alerts | Week 22 |
| Phase 10 — Mobile App (Core) | React Native: clock-in/out GPS, worker type display, mobile time entry, mobile expense entry + receipt photo | Week 25 |
| Phase 11 — Mobile App (Reports) | Progress reports with photos, geolocation tagging, upload pipeline, web PM review view | Week 27 |
| Phase 12 — Reporting & Export | Full report catalog including expense + estimation reports, async xlsx/PDF/CSV export, payroll export | Week 29 |
| Phase 13 — Integrations | AD/SSO hardening, payroll sync (SFTP + webhook), geocoding pipeline, contractor access model | Week 31 |
| Phase 14 — UAT & Launch | Performance tuning, accessibility pass, mobile app store submission, UAT with pilot entity, go-live | Week 34 |

---

## 25. Open Questions

- [ ] **Contractor PTO:** Should contractors be able to log PTO/leave codes, or only billable/non-billable project hours?
- [ ] **Cross-entity billing rates:** For cross-entity projects, whose loaded rate applies — the user's home entity rate, or the project entity rate?
- [ ] **Payroll system:** Which payroll system(s) need to be supported? What is the required file format or API spec?
- [ ] **SSO:** Is Azure AD the IdP for all entities, or do some entities use a different SAML IdP?
- [ ] **Contractor login:** Will contractors use SSO (guest accounts in AD), or email + password only?
- [ ] **Period cadence:** Is the weekly Mon–Sun period standard across all entities, or do some entities need bi-weekly or semi-monthly periods?
- [ ] **Budget dollars visibility:** Should Project Managers see dollar budgets and cost actuals, or is that Finance-only?
- [ ] **Overtime for contractors:** Should OT rules apply to contractors, or are they tracked as straight-time only?
- [ ] **Historical data migration:** Is there existing time tracking data (spreadsheets, legacy system) that needs to be migrated in?
- [ ] **Seed OT rules:** Which `OvertimeRule` records should be pre-loaded at launch? Should state-level rules be pre-populated for all 50 states, or only initial operating states?
- [ ] **Union / CBA data:** Will union and CBA rule definitions be provided by HR/legal at kickoff?
- [ ] **OT rule priority conflicts:** If a user belongs to multiple teams each with different assigned rules at the same priority, should the system block and require admin resolution, or auto-pick the most recently effective?
- [ ] **Approval chain changes mid-period:** Does a workflow change apply to time cards / expense reports already in-flight?
- [ ] **Expense approval — solo project owners:** For a user managing a personal project alone, should expense auto-approval be the system default, or should the user explicitly configure it?
- [ ] **Tax rates seeding:** Should a set of default tax rates be pre-loaded per state at launch, or does each entity configure their own from scratch?
- [ ] **Composite tax:** Is a single combined tax rate per expense sufficient for v1 (e.g., "LA County Combined 10.25%"), or does the system need to break out state + county + city as separate line items?
- [ ] **Expense receipt requirement:** Should receipt attachment be mandatory for expenses over a configurable dollar threshold?
- [ ] **BNI import format:** Can a sample BNI export file be provided at kickoff to build the column-mapping preset against?
- [ ] **Estimate import re-import behavior:** If a user re-imports an updated estimate sheet, should the system update existing estimates in place (match by description + phase), create new drafts, or always append?
- [ ] **Geofence enforcement:** Should clock-in outside a job site geofence be a hard block, soft warning, or just logged?
- [ ] **Photo storage:** Azure Blob Storage or AWS S3-compatible?
- [ ] **Photo / receipt retention:** How long should photos and receipts be retained?
- [ ] **Mobile app distribution:** Public App Store / Google Play, or enterprise MDM?
- [ ] **Offline mode:** Should the mobile app queue clock-ins, time entries, and expenses when offline?
- [ ] **Geocoding provider:** Google Maps or Azure Maps?
- [ ] **International addresses:** Are any entities or job sites outside the US?

---

## 26. Glossary

| Term | Definition |
|------|------------|
| Active Project | A project with `status = ACTIVE`, within valid date range, with a user assignment |
| AG Grid | High-performance JavaScript data grid library used for all tabular UI |
| Auto-Approve | Workflow setting that approves a time card or expense report automatically after N days without action |
| Billable | A time entry or expense flagged as billable to an external client |
| BNI | Building News Inc. — a construction cost database whose export format is supported for estimate import |
| Clock-In | The act of starting a time entry via the mobile app, capturing GPS coordinates and worker type |
| ContractorEstimate | A scoped cost estimate for a contractor or phase; supports hours×rate, fixed bid, and unit cost methods |
| Cost Center | A department or budget unit within an entity used for cost allocation |
| Cross-Entity Project | A project that accepts time entries from users belonging to multiple entities |
| Double-Time (DT) | Hours paid at 2x rate, triggered by rule-specific daily thresholds |
| Entity | A distinct legal company or business unit within the parent organization |
| Expense | A non-labor cost line item logged against a project; includes tax calculation and receipt attachment |
| Expense Report | A grouped collection of expense line items submitted together for approval |
| FastAPI | Python web framework used for the REST API; generates OpenAPI docs automatically |
| Geofence | A virtual geographic boundary around a workplace address; used to validate mobile clock-in location |
| Geocoding | The process of converting a street address into GPS coordinates (lat/lng) |
| Import Batch | A group of `ContractorEstimates` created from a single Excel/CSV import; can be reviewed or rolled back together |
| JIT Provisioning | Just-In-Time user account creation on first SSO login |
| Job Site | A physical workplace location tied to a project; has its own structured address record |
| Jurisdiction | A state or region used as a `STATE`-scope target in `OvertimeRuleAssignments` |
| Leave Code | A special time entry code representing PTO, sick leave, holiday, or other absence |
| Loaded Rate | An employee's or contractor's fully-loaded cost per hour, used for project cost accounting |
| Milestone | A date-anchored deliverable or checkpoint within a project |
| OT | Overtime — hours worked beyond the regular threshold, paid at 1.5x rate |
| OvertimeRule | A named, reusable set of OT/DT thresholds (weekly, daily, 7th-day) assignable to any scope |
| OvertimeRuleAssignment | A record linking an OvertimeRule to a scope (state, entity, team, union, project, or user) with priority and effective date |
| Period | A Mon–Sun week used to group and lock time card submissions |
| Progress Report | A field report submitted via mobile app containing text notes and photos, linked to a project |
| RAG | Red / Amber / Green — a traffic-light health status indicator for projects |
| React Native | Cross-platform mobile framework used to build the iOS and Android companion app |
| Row-Level Security | MSSQL feature that restricts which rows a query can return based on the executing user context |
| SSO | Single Sign-On — federated authentication via Azure AD (OIDC) or SAML 2.0 |
| Svelte | Reactive JavaScript front-end compiler with no virtual DOM overhead |
| Tax Exempt | A flag on an expense line item that forces tax amount to zero regardless of the configured rate |
| TaxRate | A named, effective-dated tax rate record (e.g., "CA Sales Tax 8.25%") used to auto-calculate expense tax |
| Team | A named group of users within an entity (crew, department, union local) used for OT rule assignment |
| Time Card | A weekly record of hours worked by a user across one or more projects |
| Union | A labor union or collective bargaining entity; can have OT rules assigned at the union scope |
| Worker Type | Classification of a user as Employee or Contractor; assigned by Admin or Manager only; snapshotted per time entry |
| Workplace | A named physical location (office, job site) owned by an entity or project, with a full address record |

---

## 27. Revision History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 0.1 | March 2026 | Product Team | Initial draft |
| 1.0 | March 2026 | Product Team | First complete version |
| 1.1 | March 2026 | Product Team | Added multi-entity model, contractor access, overtime rules engine, cost accounting, configurable approval workflows, full notification system, SSO + payroll integration |
| 1.2 | March 2026 | Product Team | Added React Native mobile app (GPS clock-in, worker type selection, progress reports with photos), Address & Location Model, updated DB schema, milestones, and open questions |
| 1.3 | March 2026 | Product Team | Replaced fixed jurisdiction OT model with flexible OvertimeRules + OvertimeRuleAssignments. Worker type changed to admin/manager-assigned only |
| 1.4 | March 2026 | Product Team | Added Section 12 (Expense Tracking) and Section 13 (Contractor Cost Estimation). Updated DB schema, reporting, notifications, milestones, glossary |
| 1.5 | March 2026 | Product Team | Patched cross-entity cost allocation, ApprovalWorkflows workflow_type field, and rejection routing split by document type |
| 1.6 | March 2026 | Product Team | Full org hierarchy redesign. Replaced flat Organizations→Entities model with unlimited-depth OrgNodes tree (closure table). OrgNodeTypes configurable per installation. UserNodeMemberships replaces UserEntityRoles. Permissions table replaces role_flags — explicit is_* boolean per capability per node, default-deny enforced before every DB pull. Projects now own a owner_node_id and span nodes via ProjectNodeAssignments. OvertimeRuleAssignments ENTITY+TEAM scopes collapsed into single NODE scope — resolver walks ancestor chain via closure table. All entity_id FKs across schema (LeaveCodes, BillingRates, Workplaces, AuditLog, ApprovalWorkflows, Unions) updated to node_id. Contractor cost visibility flags locked at system level regardless of node admin grants |
