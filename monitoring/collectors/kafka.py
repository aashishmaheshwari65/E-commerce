"""
monitoring/collectors/kafka.py

Kafka health collector for Functionality 20.

Kafka was intentionally deferred in this project.
This collector NEVER fails the monitoring system if Kafka is
unavailable.  It simply reports NOT_CONFIGURED.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from monitoring.config import KAFKA_BOOTSTRAP_SERVERS
from monitoring.models import ComponentResult, ComponentStatus

logger = logging.getLogger(__name__)

_KAFKA_NOT_CONFIGURED_MSG = (
    "Kafka is not currently configured or running. "
    "Kafka was intentionally deferred in this project."
)


def _try_connect(bootstrap_servers: str, timeout_ms: int = 3000) -> dict:
    """
    Attempt a lightweight Kafka broker connection.
    Returns a dict describing the result.
    """
    try:
        from kafka import KafkaAdminClient  # type: ignore
        from kafka.errors import NoBrokersAvailable  # type: ignore
    except Exception as err:
        return {
            "reachable": False,
            "error": f"kafka library import failed: {err}",
            "library_missing": True,
        }

    # Library is available – try to connect
    try:
        client = KafkaAdminClient(
            bootstrap_servers=bootstrap_servers,
            request_timeout_ms=timeout_ms,
            connections_max_idle_ms=timeout_ms,
        )
        try:
            topics = client.list_topics()
            client.close()
            return {
                "reachable": True,
                "topic_count": len(topics) if topics else 0,
                "topics": list(topics) if topics else [],
            }
        except Exception as inner:
            try:
                client.close()
            except Exception:
                pass
            return {"reachable": False, "error": str(inner)}
    except NoBrokersAvailable:
        return {"reachable": False, "error": "No brokers available"}
    except Exception as exc:
        return {"reachable": False, "error": str(exc)}


def collect(bootstrap_servers: str | None = None) -> ComponentResult:
    """
    Collect Kafka health status.

    If Kafka is unreachable or the library is missing the status
    is NOT_CONFIGURED – not a system-wide failure.
    """
    servers = bootstrap_servers or KAFKA_BOOTSTRAP_SERVERS
    ts = datetime.now(timezone.utc).isoformat()

    conn = _try_connect(servers)

    if conn.get("library_missing"):
        return ComponentResult(
            component="kafka",
            status=ComponentStatus.NOT_CONFIGURED,
            timestamp=ts,
            metrics={},
            warnings=[
                _KAFKA_NOT_CONFIGURED_MSG,
                "kafka-python library is not installed.",
            ],
            errors=[],
        )

    if not conn.get("reachable", False):
        return ComponentResult(
            component="kafka",
            status=ComponentStatus.NOT_CONFIGURED,
            timestamp=ts,
            metrics={
                "bootstrap_servers": servers,
                "error": conn.get("error", "unreachable"),
            },
            warnings=[_KAFKA_NOT_CONFIGURED_MSG],
            errors=[],
        )

    # Kafka IS reachable
    return ComponentResult(
        component="kafka",
        status=ComponentStatus.HEALTHY,
        timestamp=ts,
        metrics={
            "bootstrap_servers": servers,
            "topic_count": conn.get("topic_count", 0),
            "topics": conn.get("topics", []),
        },
        warnings=[],
        errors=[],
    )
