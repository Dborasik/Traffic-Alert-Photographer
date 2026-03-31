import json
import logging
import os
import re
import sqlite3
from datetime import datetime, timezone

log = logging.getLogger(__name__)


def _safe_id(incident_id: str) -> str:
    return re.sub(r"[^\w\-]", "_", incident_id)


def init_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS incidents (
            id           TEXT PRIMARY KEY,
            event_type   TEXT,
            severity     TEXT,
            description  TEXT,
            roadway      TEXT,
            lat          REAL,
            lon          REAL,
            last_updated TEXT,
            first_seen   TEXT,
            updated_at   TEXT,
            raw_json     TEXT
        );

        CREATE TABLE IF NOT EXISTS incident_cameras (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id      TEXT NOT NULL,
            camera_id        TEXT NOT NULL,
            camera_name      TEXT,
            distance_km      REAL,
            snapshot_path    TEXT,
            ai_visible       INTEGER,
            ai_summary       TEXT,
            ai_confidence    TEXT,
            ai_image_quality TEXT,
            ai_evidence      TEXT,
            captured_at      TEXT,
            UNIQUE(incident_id, camera_id)
        );

        CREATE TABLE IF NOT EXISTS alerts (
            id         TEXT PRIMARY KEY,
            message    TEXT,
            notes      TEXT,
            area_names TEXT,
            fetched_at TEXT
        );
        """
    )
    conn.commit()

    for col, typedef in [
        ("ai_confidence", "TEXT"),
        ("ai_image_quality", "TEXT"),
        ("ai_evidence", "TEXT"),
    ]:
        try:
            conn.execute(f"ALTER TABLE incident_cameras ADD COLUMN {col} {typedef}")
            conn.commit()
        except sqlite3.OperationalError:
            pass

    return conn


def is_known(conn: sqlite3.Connection, incident_id: str, last_updated: str) -> bool:
    row = conn.execute(
        "SELECT last_updated FROM incidents WHERE id = ?", (incident_id,)
    ).fetchone()
    return row is not None and row["last_updated"] == last_updated


def save_incident(conn: sqlite3.Connection, incidents_dir: str, event: dict, camera_results: list) -> None:
    now = datetime.now(timezone.utc).isoformat()
    inc_id = event.get("ID", "unknown")
    inc_dir = os.path.join(incidents_dir, _safe_id(inc_id))
    os.makedirs(inc_dir, exist_ok=True)

    existing = conn.execute("SELECT first_seen FROM incidents WHERE id = ?", (inc_id,)).fetchone()
    first_seen = existing["first_seen"] if existing else now

    conn.execute(
        """
        INSERT INTO incidents (id, event_type, severity, description, roadway,
            lat, lon, last_updated, first_seen, updated_at, raw_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            event_type=excluded.event_type, severity=excluded.severity,
            description=excluded.description, roadway=excluded.roadway,
            lat=excluded.lat, lon=excluded.lon,
            last_updated=excluded.last_updated, updated_at=excluded.updated_at,
            raw_json=excluded.raw_json
        """,
        (
            inc_id, event.get("EventType"), event.get("Severity"),
            event.get("Description"), event.get("RoadwayName"),
            event.get("Latitude"), event.get("Longitude"),
            event.get("LastUpdated"), first_seen, now, json.dumps(event),
        ),
    )

    cameras_report = []
    for cr in camera_results:
        cam = cr["camera"]
        cam_id = cam.get("ID", "unknown")
        snap_bytes = cr.get("snapshot_bytes")
        ai = cr.get("ai_result", {})
        dist = cr.get("distance_km", 0.0)

        snap_filename = None
        if snap_bytes:
            snap_filename = f"snap_{_safe_id(cam_id)}.jpg"
            with open(os.path.join(inc_dir, snap_filename), "wb") as f:
                f.write(snap_bytes)

        visible = ai.get("visible")
        conn.execute(
            """
            INSERT INTO incident_cameras
                (incident_id, camera_id, camera_name, distance_km, snapshot_path,
                 ai_visible, ai_summary, ai_confidence, ai_image_quality, ai_evidence, captured_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(incident_id, camera_id) DO UPDATE SET
                distance_km=excluded.distance_km, snapshot_path=excluded.snapshot_path,
                ai_visible=excluded.ai_visible, ai_summary=excluded.ai_summary,
                ai_confidence=excluded.ai_confidence, ai_image_quality=excluded.ai_image_quality,
                ai_evidence=excluded.ai_evidence, captured_at=excluded.captured_at
            """,
            (
                inc_id, cam_id, cam.get("Name"), dist, snap_filename,
                1 if visible is True else (0 if visible is False else None),
                ai.get("summary"), ai.get("confidence"), ai.get("image_quality"),
                json.dumps(ai.get("evidence") or []), now,
            ),
        )

        cameras_report.append({
            "camera_id": cam_id,
            "name": cam.get("Name"),
            "distance_km": round(dist, 3),
            "snapshot": snap_filename,
            "ai_visible": ai.get("visible"),
            "ai_confidence": ai.get("confidence"),
            "ai_image_quality": ai.get("image_quality"),
            "ai_evidence": ai.get("evidence") or [],
            "ai_summary": ai.get("summary"),
        })

    conn.commit()

    report = {
        "incident_id": inc_id,
        "event_type": event.get("EventType"),
        "severity": event.get("Severity"),
        "description": event.get("Description"),
        "location": event.get("Location"),
        "roadway": event.get("RoadwayName"),
        "lat": event.get("Latitude"),
        "lon": event.get("Longitude"),
        "direction": event.get("DirectionOfTravel"),
        "first_seen": first_seen,
        "last_updated": event.get("LastUpdated"),
        "cameras": cameras_report,
    }
    with open(os.path.join(inc_dir, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    log.info(
        "Saved incident %s | cameras: %d | snapshots: %d",
        inc_id, len(camera_results),
        sum(1 for cr in camera_results if cr.get("snapshot_bytes")),
    )


def save_alerts(conn: sqlite3.Connection, alerts: list) -> None:
    now = datetime.now(timezone.utc).isoformat()
    for alert in alerts:
        area_names = alert.get("AreaNames", [])
        conn.execute(
            """
            INSERT INTO alerts (id, message, notes, area_names, fetched_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                message=excluded.message, notes=excluded.notes,
                area_names=excluded.area_names, fetched_at=excluded.fetched_at
            """,
            (
                alert.get("Id", "unknown"), alert.get("Message"), alert.get("Notes"),
                json.dumps(area_names) if isinstance(area_names, list) else area_names,
                now,
            ),
        )
    conn.commit()
