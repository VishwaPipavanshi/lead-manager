from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_lead_service
from app.schemas.lead import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def dashboard_stats(user=Depends(get_current_user), service=Depends(get_lead_service)):
    return await service.stats(str(user["_id"]))
