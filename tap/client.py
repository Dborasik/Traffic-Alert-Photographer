import logging
import requests

BASE_URL = "https://511ny.org/api"
TIMEOUT = 30

log = logging.getLogger(__name__)


def _get(endpoint: str, api_key: str) -> list:
    url = f"{BASE_URL}/{endpoint}?key={api_key}&format=json"
    resp = requests.get(url, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        values = list(data.values())
        if len(values) == 1 and isinstance(values[0], list):
            return values[0]
    return data


def get_events(api_key: str) -> list:
    try:
        return _get("getevents", api_key)
    except Exception as e:
        log.error("get_events failed: %s", e)
        return []


def get_alerts(api_key: str) -> list:
    try:
        return _get("getalerts", api_key)
    except Exception as e:
        log.error("get_alerts failed: %s", e)
        return []


def get_cameras(api_key: str) -> list:
    try:
        return _get("getcameras", api_key)
    except Exception as e:
        log.error("get_cameras failed: %s", e)
        return []


def get_winter_road_conditions(api_key: str) -> list:
    try:
        return _get("getwinterroadconditions", api_key)
    except Exception as e:
        log.error("get_winter_road_conditions failed: %s", e)
        return []
