from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import require_internal_token
from app.core.config import get_settings
from app.db.session import get_db
from app.schemas import AlertEvaluationResponse
from app.services.account_service import AccountService
from app.services.life_service import LifeService

router = APIRouter()


def get_account_service() -> AccountService:
    return AccountService()


def get_life_service() -> LifeService:
    return LifeService(get_settings())


@router.post("/alerts/evaluate", response_model=AlertEvaluationResponse)
async def evaluate_alerts(
    force_refresh: bool = Query(False),
    _: None = Depends(require_internal_token),
    db: Session = Depends(get_db),
    account_service: AccountService = Depends(get_account_service),
    life_service: LifeService = Depends(get_life_service),
):
    domains = await life_service.get_domain_signals(db, force_refresh=force_refresh)
    return account_service.evaluate_all_users(db, domains)
