"""
monitoring/checks/health.py

Aggregates individual ComponentResult objects into an overall
MonitoringSnapshot with a single overall_status.

Rules:
- CRITICAL    → any component is CRITICAL
- WARNING     → any component is WARNING (and none CRITICAL)
- HEALTHY     → all monitored components are HEALTHY
- NOT_CONFIGURED components do NOT make the system CRITICAL
- UNKNOWN     components are reported separately but not escalated
"""

from __future__ import annotations

from datetime import datetime, timezone

from monitoring.models import (
    Alert,
    ComponentResult,
    ComponentStatus,
    MonitoringSnapshot,
)


def aggregate(
    run_id: str,
    results: list[ComponentResult],
    alerts: list[Alert] | None = None,
) -> MonitoringSnapshot:
    """
    Combine a list of ComponentResults into a MonitoringSnapshot.

    Parameters
    ----------
    run_id:
        Unique identifier for this monitoring run.
    results:
        One ComponentResult per monitored component.
    alerts:
        Pre-generated alerts (from threshold evaluations).
    """
    alerts = alerts or []
    components: dict[str, ComponentResult] = {r.component: r for r in results}
    ts = datetime.now(timezone.utc).isoformat()

    # Evaluate overall status
    statuses = {r.component: r.status for r in results}
    overall = _compute_overall(statuses)

    return MonitoringSnapshot(
        run_id=run_id,
        timestamp=ts,
        overall_status=overall,
        components=components,
        alerts=alerts,
    )


def _compute_overall(
    statuses: dict[str, ComponentStatus],
) -> ComponentStatus:
    """
    Derive the platform-wide status from component statuses.
    NOT_CONFIGURED components are excluded from escalation.
    """
    relevant = [
        s
        for s in statuses.values()
        if s not in (ComponentStatus.NOT_CONFIGURED,)
    ]

    if not relevant:
        if any(s == ComponentStatus.NOT_CONFIGURED for s in statuses.values()):
            return ComponentStatus.NOT_CONFIGURED
        return ComponentStatus.UNKNOWN

    if ComponentStatus.CRITICAL in relevant:
        return ComponentStatus.CRITICAL

    if ComponentStatus.WARNING in relevant:
        return ComponentStatus.WARNING

    unknowns = [s for s in relevant if s == ComponentStatus.UNKNOWN]
    healthy = [s for s in relevant if s == ComponentStatus.HEALTHY]

    if healthy and not unknowns:
        return ComponentStatus.HEALTHY

    if unknowns and not healthy:
        return ComponentStatus.UNKNOWN

    # Mix of HEALTHY and UNKNOWN → WARNING so the user knows to investigate
    return ComponentStatus.WARNING
