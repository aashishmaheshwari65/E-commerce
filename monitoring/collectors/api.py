"""
monitoring/collectors/api.py

FastAPI availability and performance collector for Functionality 20.

Makes minimal lightweight HTTP requests to the running API.
Does NOT generate artificial load.
Returns UNKNOWN status if the API is not running – never crashes.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from monitoring.config import API_BASE_URL, MAX_API_LATENCY_MS, API_TIMEOUT_SECONDS
from monitoring.models import ComponentResult, ComponentStatus

logger = logging.getLogger(__name__)

_ENDPOINTS: list[dict] = [
    {"name": "health", "path": "/health", "method": "GET"},
    {"name": "health_models", "path": "/health/models", "method": "GET"},
]


def _probe_endpoint(
    base_url: str,
    path: str,
    timeout: float,
) -> dict:
    """Send a single GET request, return status/latency/body."""
    try:
        import requests  # type: ignore

        url = base_url.rstrip("/") + path
        t0 = time.perf_counter()
        resp = requests.get(url, timeout=timeout)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        try:
            body = resp.json()
        except Exception:
            body = None

        return {
            "url": url,
            "status_code": resp.status_code,
            "response_ms": round(elapsed_ms, 2),
            "ok": resp.status_code < 400,
            "body": body,
        }
    except ImportError:
        return {
            "url": base_url + path,
            "error": "requests library not installed",
            "ok": False,
        }
    except Exception as exc:
        return {
            "url": base_url + path,
            "error": str(exc),
            "ok": False,
        }


def collect(
    base_url: str | None = None,
    timeout: float | None = None,
) -> ComponentResult:
    """Probe FastAPI endpoints and return a ComponentResult."""
    base_url = base_url or API_BASE_URL
    timeout = timeout or API_TIMEOUT_SECONDS
    ts = datetime.now(timezone.utc).isoformat()

    probes: list[dict] = []
    for ep in _ENDPOINTS:
        result = _probe_endpoint(base_url, ep["path"], timeout)
        result["endpoint"] = ep["name"]
        probes.append(result)

    reachable = any(p.get("ok") for p in probes)

    if not reachable:
        # API is not running – this is UNKNOWN, not CRITICAL
        errors = [p.get("error", "no response") for p in probes if not p.get("ok")]
        return ComponentResult(
            component="fastapi",
            status=ComponentStatus.UNKNOWN,
            timestamp=ts,
            metrics={"base_url": base_url, "probes": probes},
            warnings=[
                f"FastAPI at {base_url} is not reachable. "
                "Start with: python -m uvicorn api.main:app --reload"
            ],
            errors=errors[:1],  # one representative error
        )

    # Analyse successful probes
    warnings: list[str] = []
    errors: list[str] = []

    for p in probes:
        if not p.get("ok"):
            errors.append(
                f"Endpoint {p.get('endpoint')} returned "
                f"{p.get('status_code', 'error')}"
            )
        latency = p.get("response_ms")
        if latency and latency > MAX_API_LATENCY_MS:
            warnings.append(
                f"Endpoint {p.get('endpoint')} latency {latency:.0f}ms "
                f"exceeds threshold {MAX_API_LATENCY_MS}ms"
            )

    # Pull model availability from /health/models
    model_status: dict = {}
    health_models_probe = next(
        (p for p in probes if p.get("endpoint") == "health_models"), None
    )
    if health_models_probe and health_models_probe.get("ok"):
        body = health_models_probe.get("body") or {}
        model_status = body.get("models", {})

    avg_latency = None
    latencies = [p["response_ms"] for p in probes if "response_ms" in p]
    if latencies:
        avg_latency = round(sum(latencies) / len(latencies), 2)

    if errors:
        status = ComponentStatus.WARNING
    elif warnings:
        status = ComponentStatus.WARNING
    else:
        status = ComponentStatus.HEALTHY

    return ComponentResult(
        component="fastapi",
        status=status,
        timestamp=ts,
        metrics={
            "base_url": base_url,
            "reachable": True,
            "endpoints_probed": len(probes),
            "avg_response_ms": avg_latency,
            "model_availability": model_status,
            "probes": probes,
        },
        warnings=warnings,
        errors=errors,
    )
