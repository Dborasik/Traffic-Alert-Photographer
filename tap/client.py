import logging
import time

import requests

BASE_URL = "https://511ny.org/api"
TIMEOUT = 30
_RETRY_DELAYS = (1, 2, 4)

log = logging.getLogger(__name__)


def _get(endpoint: str, api_key: str) -> list:
    url = f"{BASE_URL}/{endpoint}?key={api_key}&format=json"
    last_exc = None
    for attempt in range(len(_RETRY_DELAYS) + 1):
        if attempt:
            wait = _RETRY_DELAYS[attempt - 1]
            log.warning("Retry %d/%d for %s in %ds...", attempt, len(_RETRY_DELAYS), endpoint, wait)
            time.sleep(wait)
        try:
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
        except Exception as e:
            last_exc = e
            log.warning("%s request failed: %s", endpoint, e)
    raise last_exc


def get_events(api_key: str) -> list:
    return _get("getevents", api_key)



def get_cameras(api_key: str) -> list:
    return _get("getcameras", api_key)


def get_winter_road_conditions(api_key: str) -> list:
    return _get("getwinterroadconditions", api_key)
