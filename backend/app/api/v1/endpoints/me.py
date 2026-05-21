from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser, require_user
from app.core.config import get_settings
from app.db.session import get_db
from app.schemas import (
    AlertRuleCreate,
    AlertRuleResponse,
    AlertRuleUpdate,
    LifePulseResponse,
    NotificationResponse,
    NotificationUpdate,
    SavedItemCreate,
    SavedItemResponse,
    UserProfileResponse,
    UserProfileUpdate,
)
from app.services.account_service import AccountService
from app.services.life_service import LifeService

router = APIRouter()


def get_account_service() -> AccountService:
    return AccountService()


def get_life_service() -> LifeService:
    return LifeService(get_settings())


@router.get("/profile", response_model=UserProfileResponse)
def get_profile(
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_user),
    service: AccountService = Depends(get_account_service),
):
    return service.profile_response(service.ensure_profile(db, user))


@router.put("/profile", response_model=UserProfileResponse)
def update_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_user),
    service: AccountService = Depends(get_account_service),
):
    return service.update_profile(db, user, payload)


@router.get("/saved-items", response_model=list[SavedItemResponse])
def list_saved_items(
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_user),
    service: AccountService = Depends(get_account_service),
):
    return service.list_saved_items(db, user)


@router.post("/saved-items", response_model=SavedItemResponse, status_code=status.HTTP_201_CREATED)
def create_saved_item(
    payload: SavedItemCreate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_user),
    service: AccountService = Depends(get_account_service),
):
    return service.create_saved_item(db, user, payload)


@router.delete("/saved-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_user),
    service: AccountService = Depends(get_account_service),
):
    service.delete_saved_item(db, user, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/alerts", response_model=list[AlertRuleResponse])
def list_alerts(
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_user),
    service: AccountService = Depends(get_account_service),
):
    return service.list_alert_rules(db, user)


@router.post("/alerts", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
def create_alert(
    payload: AlertRuleCreate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_user),
    service: AccountService = Depends(get_account_service),
):
    return service.create_alert_rule(db, user, payload)


@router.patch("/alerts/{rule_id}", response_model=AlertRuleResponse)
def update_alert(
    rule_id: int,
    payload: AlertRuleUpdate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_user),
    service: AccountService = Depends(get_account_service),
):
    return service.update_alert_rule(db, user, rule_id, payload)


@router.delete("/alerts/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(
    rule_id: int,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_user),
    service: AccountService = Depends(get_account_service),
):
    service.delete_alert_rule(db, user, rule_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/notifications", response_model=list[NotificationResponse])
def list_notifications(
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_user),
    service: AccountService = Depends(get_account_service),
):
    return service.list_notifications(db, user, limit=limit)


@router.patch("/notifications/{notification_id}", response_model=NotificationResponse)
def update_notification(
    notification_id: int,
    payload: NotificationUpdate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_user),
    service: AccountService = Depends(get_account_service),
):
    return service.update_notification(db, user, notification_id, read=payload.read)


@router.get("/life-pulse", response_model=LifePulseResponse)
async def get_life_pulse(
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_user),
    account_service: AccountService = Depends(get_account_service),
    life_service: LifeService = Depends(get_life_service),
):
    profile = account_service.ensure_profile(db, user)
    overview = await life_service.overview(db, district=profile.district, profile=profile.profile)
    return account_service.life_pulse(db, user, overview)
