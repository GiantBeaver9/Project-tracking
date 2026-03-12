from pydantic import BaseModel


class OrgNodeCreate(BaseModel):
    parent_node_id: str | None = None
    node_type: str
    name: str
    code: str
    description: str | None = None
    timezone: str = "America/New_York"
    sort_order: int = 0
    metadata_json: str | None = None


class OrgNodeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    timezone: str | None = None
    is_active: bool | None = None
    sort_order: int | None = None
    metadata_json: str | None = None


class OrgNodeResponse(BaseModel):
    node_id: str
    parent_node_id: str | None
    node_type: str
    name: str
    code: str
    description: str | None
    timezone: str
    is_active: bool
    sort_order: int

    model_config = {"from_attributes": True}


class OrgNodeTypeCreate(BaseModel):
    node_type: str
    display_label: str
    allowed_depth_min: int | None = None
    allowed_depth_max: int | None = None
    is_system: bool = False


class OrgNodeTypeResponse(BaseModel):
    type_id: int
    node_type: str
    display_label: str
    allowed_depth_min: int | None
    allowed_depth_max: int | None
    is_system: bool

    model_config = {"from_attributes": True}
