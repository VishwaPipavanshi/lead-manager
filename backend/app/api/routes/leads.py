from typing import Literal

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.dependencies import get_current_user, get_lead_service
from app.schemas.lead import (
    LeadInput,
    LeadPage,
    LeadResponse,
    LeadStatus,
    LeadStatusUpdate,
    LeadUpdate,
)
from app.utils.object_id import parse_object_id

router = APIRouter(prefix="/leads", tags=["leads"])
SortField = Literal["created_at", "updated_at", "name", "company", "status"]
SortOrder = Literal["asc", "desc"]


def serialize_lead(document: dict) -> dict:
    return {**document, "id": str(document["_id"])}


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    payload: LeadInput,
    user=Depends(get_current_user),
    service=Depends(get_lead_service),
):
    document = await service.create(str(user["_id"]), payload.model_dump(mode="json"))
    return serialize_lead(document)


@router.get("", response_model=LeadPage)
async def list_leads(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    search: str | None = Query(default=None, max_length=100),
    status_filter: LeadStatus | None = Query(default=None, alias="status"),
    sort_by: SortField = "created_at",
    order: SortOrder = "desc",
    user=Depends(get_current_user),
    service=Depends(get_lead_service),
):
    result = await service.list(
        str(user["_id"]),
        page,
        limit,
        search.strip() if search else None,
        status_filter,
        sort_by,
        order,
    )
    result["items"] = [serialize_lead(item) for item in result["items"]]
    return result


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    user=Depends(get_current_user),
    service=Depends(get_lead_service),
):
    document = await service.get(str(user["_id"]), parse_object_id(lead_id))
    return serialize_lead(document)


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    payload: LeadUpdate,
    user=Depends(get_current_user),
    service=Depends(get_lead_service),
):
    document = await service.update(
        str(user["_id"]),
        parse_object_id(lead_id),
        payload.model_dump(exclude_unset=True, mode="json"),
    )
    return serialize_lead(document)


@router.patch("/{lead_id}/status", response_model=LeadResponse)
async def update_lead_status(
    lead_id: str,
    payload: LeadStatusUpdate,
    user=Depends(get_current_user),
    service=Depends(get_lead_service),
):
    document = await service.set_status(str(user["_id"]), parse_object_id(lead_id), payload.status)
    return serialize_lead(document)


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: str,
    user=Depends(get_current_user),
    service=Depends(get_lead_service),
):
    await service.delete(str(user["_id"]), parse_object_id(lead_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
