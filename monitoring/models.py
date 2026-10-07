"""
monitoring/models.py

Pydantic-free dataclasses representing monitoring status and results.
Kept dependency-free to avoid requiring FastAPI/Pydantic at runtime.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ComponentStatus(str, Enum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"
    NOT_CONFIGURED = "NOT_CONFIGURED"


@dataclass
class ComponentResult:
    """Result for a single monitored component."""

    component: str
    status: ComponentStatus
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metrics: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "component": self.component,
            "status": self.status.value,
            "timestamp": self.timestamp,
            "metrics": self.metrics,
            "warnings": self.warnings,
            "errors": self.errors,
        }


@dataclass
class Alert:
    """Single threshold-violation alert."""

    timestamp: str
    severity: str  # WARNING | CRITICAL
    component: str
    metric: str
    value: Any
    threshold: Any
    message: str

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "severity": self.severity,
            "component": self.component,
            "metric": self.metric,
            "value": self.value,
            "threshold": self.threshold,
            "message": self.message,
        }


@dataclass
class MonitoringSnapshot:
    """Full platform snapshot produced by one monitoring run."""

    run_id: str
    timestamp: str
    overall_status: ComponentStatus
    components: dict[str, ComponentResult]
    alerts: list[Alert] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "overall_status": self.overall_status.value,
            "components": {
                k: v.to_dict() for k, v in self.components.items()
            },
            "alerts": [a.to_dict() for a in self.alerts],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)
