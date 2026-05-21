from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser
from app.db.models import AlertRule, Notification, SavedItem, UserProfile, utc_now
from app.schemas import (
    AlertEvaluationResponse,
    AlertRuleCreate,
    AlertRuleResponse,
    AlertRuleUpdate,
    DomainMetric,
    DomainSignal,
    LifeOverviewResponse,
    LifePulseResponse,
    NotificationResponse,
    SavedItemCreate,
    SavedItemResponse,
    UserProfileResponse,
    UserProfileUpdate,
)


class AccountService:
    def ensure_profile(self, db: Session, user: AuthenticatedUser) -> UserProfile:
        profile = db.scalar(select(UserProfile).where(UserProfile.auth_sub == user.auth_sub))
        now = utc_now()
        if profile is None:
            profile = UserProfile(
                auth_sub=user.auth_sub,
                email=user.email,
                display_name=user.display_name,
                photo_url=user.photo_url,
                default_locale="en",
                district="Sri Lanka",
                profile="family",
                created_at=now,
                updated_at=now,
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
            return profile

        changed = False
        for attr, value in {
            "email": user.email,
            "display_name": user.display_name,
            "photo_url": user.photo_url,
        }.items():
            if value and getattr(profile, attr) != value:
                setattr(profile, attr, value)
                changed = True
        if changed:
            profile.updated_at = now
            db.commit()
            db.refresh(profile)
        return profile

    def update_profile(self, db: Session, user: AuthenticatedUser, payload: UserProfileUpdate) -> UserProfileResponse:
        profile = self.ensure_profile(db, user)
        changed = False
        for attr in ("default_locale", "district", "profile", "display_name"):
            value = getattr(payload, attr)
            if value is not None and getattr(profile, attr) != value:
                setattr(profile, attr, value)
                changed = True
        if changed:
            profile.updated_at = utc_now()
            db.commit()
            db.refresh(profile)
        return self.profile_response(profile)

    def list_saved_items(self, db: Session, user: AuthenticatedUser) -> list[SavedItemResponse]:
        rows = db.scalars(
            select(SavedItem).where(SavedItem.auth_sub == user.auth_sub).order_by(desc(SavedItem.created_at), desc(SavedItem.id))
        ).all()
        return [self.saved_item_response(row) for row in rows]

    def create_saved_item(self, db: Session, user: AuthenticatedUser, payload: SavedItemCreate) -> SavedItemResponse:
        self.ensure_profile(db, user)
        item = SavedItem(
            auth_sub=user.auth_sub,
            domain_key=payload.domain_key,
            label=payload.label,
            query=payload.query,
            href=payload.href,
            payload=payload.payload,
            created_at=utc_now(),
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return self.saved_item_response(item)

    def delete_saved_item(self, db: Session, user: AuthenticatedUser, item_id: int) -> None:
        item = db.get(SavedItem, item_id)
        if item is None or item.auth_sub != user.auth_sub:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved item not found")
        db.delete(item)
        db.commit()

    def list_alert_rules(self, db: Session, user: AuthenticatedUser) -> list[AlertRuleResponse]:
        rows = db.scalars(
            select(AlertRule).where(AlertRule.auth_sub == user.auth_sub).order_by(desc(AlertRule.created_at), desc(AlertRule.id))
        ).all()
        return [self.alert_rule_response(row) for row in rows]

    def create_alert_rule(self, db: Session, user: AuthenticatedUser, payload: AlertRuleCreate) -> AlertRuleResponse:
        self.ensure_profile(db, user)
        now = utc_now()
        rule = AlertRule(
            auth_sub=user.auth_sub,
            domain_key=payload.domain_key,
            label=payload.label,
            metric_label=payload.metric_label,
            condition=payload.condition,
            threshold_value=payload.threshold_value,
            enabled=payload.enabled,
            created_at=now,
            updated_at=now,
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return self.alert_rule_response(rule)

    def update_alert_rule(self, db: Session, user: AuthenticatedUser, rule_id: int, payload: AlertRuleUpdate) -> AlertRuleResponse:
        rule = self._owned_alert_rule(db, user, rule_id)
        for attr in ("label", "metric_label", "condition", "threshold_value", "enabled"):
            value = getattr(payload, attr)
            if value is not None:
                setattr(rule, attr, value)
        rule.updated_at = utc_now()
        db.commit()
        db.refresh(rule)
        return self.alert_rule_response(rule)

    def delete_alert_rule(self, db: Session, user: AuthenticatedUser, rule_id: int) -> None:
        rule = self._owned_alert_rule(db, user, rule_id)
        db.delete(rule)
        db.commit()

    def list_notifications(self, db: Session, user: AuthenticatedUser, *, limit: int = 30) -> list[NotificationResponse]:
        rows = db.scalars(
            select(Notification)
            .where(Notification.auth_sub == user.auth_sub)
            .order_by(desc(Notification.created_at), desc(Notification.id))
            .limit(limit)
        ).all()
        return [self.notification_response(row) for row in rows]

    def update_notification(self, db: Session, user: AuthenticatedUser, notification_id: int, *, read: bool) -> NotificationResponse:
        notification = db.get(Notification, notification_id)
        if notification is None or notification.auth_sub != user.auth_sub:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        notification.read_at = utc_now() if read else None
        db.commit()
        db.refresh(notification)
        return self.notification_response(notification)

    def life_pulse(self, db: Session, user: AuthenticatedUser, overview: LifeOverviewResponse) -> LifePulseResponse:
        profile = self.ensure_profile(db, user)
        self.evaluate_user_alerts(db, user.auth_sub, overview.domains)
        notifications = self.list_notifications(db, user, limit=12)
        unread_count = db.scalar(
            select(func.count(Notification.id)).where(Notification.auth_sub == user.auth_sub).where(Notification.read_at.is_(None))
        )
        if unread_count is None:
            unread_count = len([item for item in notifications if item.read_at is None])
        return LifePulseResponse(
            generated_at=utc_now(),
            profile=self.profile_response(profile),
            overview=overview,
            saved_items=self.list_saved_items(db, user),
            alert_rules=self.list_alert_rules(db, user),
            notifications=notifications,
            unread_count=unread_count,
        )

    def evaluate_all_users(self, db: Session, domains: list[DomainSignal]) -> AlertEvaluationResponse:
        profiles = db.scalars(select(UserProfile)).all()
        alerts_checked = 0
        notifications_created = 0
        for profile in profiles:
            created, checked = self.evaluate_user_alerts(db, profile.auth_sub, domains)
            notifications_created += created
            alerts_checked += checked
        return AlertEvaluationResponse(
            generated_at=utc_now(),
            users_checked=len(profiles),
            alerts_checked=alerts_checked,
            notifications_created=notifications_created,
        )

    def evaluate_user_alerts(self, db: Session, auth_sub: str, domains: list[DomainSignal]) -> tuple[int, int]:
        rules = db.scalars(
            select(AlertRule).where(AlertRule.auth_sub == auth_sub).where(AlertRule.enabled.is_(True)).order_by(AlertRule.id.asc())
        ).all()
        domain_map = {domain.key: domain for domain in domains}
        created = 0
        for rule in rules:
            candidates = [domain_map[rule.domain_key]] if rule.domain_key and rule.domain_key in domain_map else list(domain_map.values())
            for domain in candidates:
                trigger = self._trigger_for_rule(rule, domain)
                if trigger is None:
                    continue
                if self._create_notification(db, rule, domain, trigger):
                    created += 1
        return created, len(rules)

    def _trigger_for_rule(self, rule: AlertRule, domain: DomainSignal) -> dict | None:
        if rule.condition == "source_degraded":
            if domain.status != "healthy":
                return {
                    "title": f"{domain.label} source needs attention",
                    "message": f"{domain.label} is {domain.status}; Ariva is still showing labelled fallback or degraded data.",
                    "severity": "watch" if domain.status == "degraded" else "risk",
                    "value": domain.status,
                }
            return None

        if rule.condition == "movement_changed":
            highlight = next((item for item in domain.highlights if item.severity in {"watch", "risk", "good"}), None)
            if highlight is None:
                return None
            return {
                "title": f"{domain.label}: {highlight.label}",
                "message": highlight.value,
                "severity": highlight.severity,
                "value": highlight.value,
            }

        metric = self._rule_metric(rule, domain)
        if metric is None or rule.threshold_value is None:
            return None
        value = self._metric_number(metric)
        if value is None:
            return None
        matched = value > rule.threshold_value if rule.condition == "above" else value < rule.threshold_value
        if not matched:
            return None
        direction = "above" if rule.condition == "above" else "below"
        return {
            "title": f"{domain.label}: {metric.label} {direction} threshold",
            "message": f"{metric.label} is {value:g} {metric.unit or ''}, {direction} your {rule.threshold_value:g} threshold.".strip(),
            "severity": "risk" if rule.condition == "above" else "good",
            "value": value,
            "metric_label": metric.label,
        }

    def _create_notification(self, db: Session, rule: AlertRule, domain: DomainSignal, trigger: dict) -> bool:
        observed_day = (domain.observed_at or utc_now()).date()
        idempotency_key = self._idempotency_key(rule, domain.key, observed_day, trigger)
        existing = db.scalar(
            select(Notification)
            .where(Notification.auth_sub == rule.auth_sub)
            .where(Notification.idempotency_key == idempotency_key)
        )
        if existing is not None:
            return False
        notification = Notification(
            auth_sub=rule.auth_sub,
            alert_rule_id=rule.id,
            title=trigger["title"],
            message=trigger["message"],
            severity=trigger["severity"],
            source_domain=domain.key,
            idempotency_key=idempotency_key,
            payload={"rule_label": rule.label, "trigger": trigger},
            created_at=utc_now(),
        )
        rule.last_triggered_at = notification.created_at
        db.add(notification)
        db.commit()
        return True

    def _idempotency_key(self, rule: AlertRule, domain_key: str, observed_day: date, trigger: dict) -> str:
        value = trigger.get("metric_label") or trigger.get("value")
        return f"alert:{rule.id}:{domain_key}:{rule.condition}:{observed_day.isoformat()}:{value}"

    def _rule_metric(self, rule: AlertRule, domain: DomainSignal) -> DomainMetric | None:
        if rule.metric_label:
            return next((metric for metric in domain.metrics if metric.label.lower() == rule.metric_label.lower()), None)
        return next((metric for metric in domain.metrics if self._metric_number(metric) is not None), None)

    def _metric_number(self, metric: DomainMetric) -> float | None:
        try:
            return float(metric.value) if metric.value is not None else None
        except (TypeError, ValueError):
            return None

    def _owned_alert_rule(self, db: Session, user: AuthenticatedUser, rule_id: int) -> AlertRule:
        rule = db.get(AlertRule, rule_id)
        if rule is None or rule.auth_sub != user.auth_sub:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert rule not found")
        return rule

    def profile_response(self, row: UserProfile) -> UserProfileResponse:
        return UserProfileResponse(
            id=row.id,
            auth_sub=row.auth_sub,
            email=row.email,
            display_name=row.display_name,
            photo_url=row.photo_url,
            default_locale=row.default_locale,
            district=row.district,
            profile=row.profile,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def saved_item_response(self, row: SavedItem) -> SavedItemResponse:
        return SavedItemResponse(
            id=row.id,
            domain_key=row.domain_key,
            label=row.label,
            query=row.query,
            href=row.href,
            payload=row.payload,
            created_at=row.created_at,
        )

    def alert_rule_response(self, row: AlertRule) -> AlertRuleResponse:
        return AlertRuleResponse(
            id=row.id,
            domain_key=row.domain_key,
            label=row.label,
            metric_label=row.metric_label,
            condition=row.condition,
            threshold_value=row.threshold_value,
            enabled=row.enabled,
            created_at=row.created_at,
            updated_at=row.updated_at,
            last_triggered_at=row.last_triggered_at,
        )

    def notification_response(self, row: Notification) -> NotificationResponse:
        return NotificationResponse(
            id=row.id,
            alert_rule_id=row.alert_rule_id,
            title=row.title,
            message=row.message,
            severity=row.severity,
            source_domain=row.source_domain,
            read_at=row.read_at,
            payload=row.payload,
            created_at=row.created_at,
        )
