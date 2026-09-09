from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_admin
from app.models.user import User
from app.schemas.analytics import FarmTrendsResponse, SystemHealthResponse
from app.services import analytics_service
from app.services.authz import assert_farm_access

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/farm-trends", response_model=FarmTrendsResponse)
def farm_trends(
    farm_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FarmTrendsResponse:
    assert_farm_access(db, user=current_user, farm_id=farm_id)
    return analytics_service.build_farm_trends(db, farm_id)


@router.get("/system-health", response_model=SystemHealthResponse)
def system_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> SystemHealthResponse:
    return analytics_service.build_system_health(db)
