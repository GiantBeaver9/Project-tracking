from pydantic import BaseModel


class AddressCreate(BaseModel):
    owner_type: str
    owner_id: str
    label: str | None = None
    address_line_1: str
    address_line_2: str | None = None
    city: str
    state_code: str
    zip_code: str
    county: str | None = None
    country_code: str = "US"
    geofence_radius_ft: int | None = None
    is_primary: bool = False


class AddressUpdate(BaseModel):
    label: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    state_code: str | None = None
    zip_code: str | None = None
    county: str | None = None
    country_code: str | None = None
    geofence_radius_ft: int | None = None
    is_primary: bool | None = None
    is_active: bool | None = None


class AddressResponse(BaseModel):
    address_id: int
    owner_type: str
    owner_id: str
    label: str | None
    address_line_1: str
    address_line_2: str | None
    city: str
    state_code: str
    zip_code: str
    county: str | None
    country_code: str
    latitude: float | None
    longitude: float | None
    geofence_radius_ft: int | None
    is_primary: bool
    is_active: bool
    geocode_status: str

    model_config = {"from_attributes": True}
