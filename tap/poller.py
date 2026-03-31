import logging
import os
import time

from . import analyzer, capture, client, store
from .geo import cameras_within_radius

log = logging.getLogger("tap.poller")


def process_event(event: dict, cameras: list, conn, cfg: dict) -> None:
    lat = event.get("Latitude")
    lon = event.get("Longitude")
    if lat is None or lon is None:
        return

    radius = cfg["511ny"]["proximity_radius_km"]
    nearby = cameras_within_radius(lat, lon, cameras, radius)

    if not nearby:
        log.debug("No cameras within %.1f km of event %s", radius, event.get("ID"))
        return

    log.info(
        "Event %s (%s) — %d camera(s) within %.1f km",
        event.get("ID"), event.get("EventType"), len(nearby), radius,
    )

    camera_results = []
    for cam, dist_km in nearby:
        log.info("  Capturing camera %s (%.2f km)", cam.get("ID"), dist_km)
        snap = capture.capture_snapshot(cam)

        if snap and cfg["openai"].get("enabled", True):
            ai_result = analyzer.analyze(snap, event, cam, dist_km, cfg["openai"])
            log.info("  AI: visible=%s — %s", ai_result["visible"], ai_result["summary"][:80])
        elif snap:
            ai_result = {"visible": None, "summary": "AI analysis disabled"}
        else:
            log.warning("  No snapshot obtained for camera %s", cam.get("ID"))
            ai_result = {"visible": False, "summary": "No snapshot available"}

        camera_results.append({
            "camera": cam,
            "distance_km": dist_km,
            "snapshot_bytes": snap,
            "ai_result": ai_result,
        })

    store.save_incident(conn, cfg["storage"]["incidents_dir"], event, camera_results)


def poll(cfg: dict, conn) -> None:
    api_key = cfg["511ny"]["api_key"]

    log.info("Fetching cameras...")
    cameras = client.get_cameras(api_key)
    active = [c for c in cameras if not c.get("Disabled") and not c.get("Blocked")]
    log.info("Cameras: %d total, %d active", len(cameras), len(active))

    log.info("Fetching events...")
    events = client.get_events(api_key)
    log.info("Events: %d", len(events))

    filters = cfg.get("511ny_filters", {})
    allowed_types = filters.get("event_types") or []
    allowed_sevs = filters.get("severities") or []

    new_count = skipped = 0
    for event in events:
        if allowed_types and event.get("EventType") not in allowed_types:
            skipped += 1
            continue
        if allowed_sevs and event.get("Severity") not in allowed_sevs:
            skipped += 1
            continue
        if store.is_known(conn, event.get("ID", ""), event.get("LastUpdated", "")):
            continue
        new_count += 1
        process_event(event, active, conn, cfg)

    if skipped:
        log.info("Skipped %d event(s) excluded by filter", skipped)
    log.info("New/updated events processed: %d", new_count)

    log.info("Fetching alerts...")
    alerts = client.get_alerts(api_key)
    store.save_alerts(conn, alerts)
    log.info("Alerts stored: %d", len(alerts))


def run(cfg: dict) -> None:
    """Start the polling loop. Blocks forever — intended to run in a thread."""
    os.makedirs(cfg["storage"]["incidents_dir"], exist_ok=True)
    conn = store.init_db(cfg["storage"]["db_path"])
    log.info("Database ready: %s", cfg["storage"]["db_path"])

    interval = cfg["511ny"]["poll_interval_seconds"]
    log.info("Starting poll loop — interval: %ds", interval)

    while True:
        try:
            poll(cfg, conn)
        except Exception as e:
            log.exception("Poll cycle failed: %s", e)
        log.info("Sleeping %ds...", interval)
        time.sleep(interval)
