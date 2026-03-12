from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.address import Address
from app.models.user import User
from app.schemas.address import AddressCreate, AddressResponse, AddressUpdate

router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.post("", response_model=AddressResponse, status_code=201)
async def create_address(
    body: AddressCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # If marking as primary, unset any existing primary for this owner
    if body.is_primary:
        result = await db.execute(
            select(Address).where(
                and_(
                    Address.owner_type == body.owner_type,
                    Address.owner_id == body.owner_id,
                    Address.is_primary == True,
                )
            )
        )
        for existing in result.scalars().all():
            existing.is_primary = False

    address = Address(
        owner_type=body.owner_type,
        owner_id=body.owner_id,
        label=body.label,
        address_line_1=body.address_line_1,
        address_line_2=body.address_line_2,
        city=body.city,
        state_code=body.state_code,
        zip_code=body.zip_code,
        county=body.county,
        country_code=body.country_code,
        geofence_radius_ft=body.geofence_radius_ft,
        is_primary=body.is_primary,
    )
    db.add(address)
    await db.commit()
    await db.refresh(address)
    return address


@router.get("", response_model=list[AddressResponse])
async def list_addresses(
    owner_type: str = Query(...),
    owner_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Address).where(
            and_(
                Address.owner_type == owner_type,
                Address.owner_id == owner_id,
                Address.is_active == True,
            )
        )
    )
    return result.scalars().all()


@router.get("/{address_id}", response_model=AddressResponse)
async def get_address(
    address_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    address = await db.get(Address, address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address


@router.patch("/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: int,
    body: AddressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    address = await db.get(Address, address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    update_data = body.model_dump(exclude_unset=True)

    # If marking as primary, unset any existing primary for this owner
    if update_data.get("is_primary"):
        result = await db.execute(
            select(Address).where(
                and_(
                    Address.owner_type == address.owner_type,
                    Address.owner_id == address.owner_id,
                    Address.is_primary == True,
                    Address.address_id != address_id,
                )
            )
        )
        for existing in result.scalars().all():
            existing.is_primary = False

    for field, value in update_data.items():
        setattr(address, field, value)

    # Reset geocode status if address fields changed
    address_fields = {"address_line_1", "address_line_2", "city", "state_code", "zip_code", "country_code"}
    if address_fields & update_data.keys():
        address.geocode_status = "PENDING"

    await db.commit()
    await db.refresh(address)
    return address
