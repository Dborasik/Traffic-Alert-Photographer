"""
All configuration loaded from environment variables / .env file.
See .env.example for the full list.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Project root is one level up from this package
BASE_DIR = Path(__file__).parent.parent.resolve()


def _list(val: str) -> list[str]:
    return [v.strip() for v in val.split(",") if v.strip()]


def _resolve(path: str) -> str:
    p = Path(path)
    return str(p if p.is_absolute() else BASE_DIR / p)


def load() -> dict:
    load_dotenv(BASE_DIR / ".env", override=False)

    event_types_raw = os.environ.get("FILTER_EVENT_TYPES", "accidentsAndIncidents,winterDrivingIndex")
    severities_raw  = os.environ.get("FILTER_SEVERITIES", "")

    return {
        "511ny": {
            "api_key":               os.environ["NY511_API_KEY"],
            "poll_interval_seconds": int(os.environ.get("NY511_POLL_INTERVAL", 120)),
            "proximity_radius_km":   float(os.environ.get("NY511_PROXIMITY_RADIUS_KM", 1.0)),
        },
        "openai": {
            "enabled":             os.environ.get("OPENAI_ENABLED", "true").lower() == "true",
            "api_key":             os.environ.get("OPENAI_API_KEY", ""),
            "model":               os.environ.get("OPENAI_MODEL", "gpt-4o"),
            "prompt":              os.environ.get("OPENAI_PROMPT", ""),
            "max_image_dimension": int(os.environ.get("OPENAI_MAX_IMAGE_DIM", 1024)),
        },
        "511ny_filters": {
            "event_types": _list(event_types_raw),
            "severities":  _list(severities_raw),
        },
        "storage": {
            "incidents_dir": _resolve(os.environ.get("STORAGE_INCIDENTS_DIR", "incidents")),
            "db_path":       _resolve(os.environ.get("STORAGE_DB_PATH", "incidents.db")),
        },
        "web": {
            "host": os.environ.get("HOST", "0.0.0.0"),
            "port": int(os.environ.get("PORT", 5000)),
        },
    }
