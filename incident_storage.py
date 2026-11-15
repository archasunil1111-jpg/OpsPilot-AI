
import json
import os
from datetime import datetime

HISTORY_FILE = "incident_history.json"


def load_incidents():
    """Load previously saved incident records."""
    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


def save_incident(
    title,
    affected_service,
    severity,
    category,
    retrieved_count,
    report
):
    """Save one completed incident analysis."""

    incidents = load_incidents()

    incident = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "title": title,
        "affected_service": affected_service,
        "severity": severity,
        "category": category,
        "retrieved_count": retrieved_count,
        "report": report,
        "created_at": datetime.now().isoformat(
            timespec="seconds"
        )
    }

    incidents.append(incident)

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(incidents, file, indent=4)

    return incident


def get_incident_statistics():
    """Calculate dashboard statistics from saved incidents."""

    incidents = load_incidents()

    total = len(incidents)

    severity_counts = {
        "Low": 0,
        "Medium": 0,
        "High": 0,
        "Critical": 0
    }

    category_counts = {}

    for incident in incidents:
        severity = incident.get("severity", "Low")
        category = incident.get(
            "affected_service", "Other"
        )

        if severity in severity_counts:
            severity_counts[severity] += 1

        category_counts[category] = (
            category_counts.get(category, 0) + 1
        )

    return {
        "total": total,
        "severity": severity_counts,
        "categories": category_counts,
        "incidents": incidents
    }
