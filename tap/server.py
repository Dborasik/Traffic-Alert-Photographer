import json
import sqlite3
from pathlib import Path

from flask import Flask, abort, jsonify, send_from_directory

# web/ lives at the project root, one level above this package
WEB_DIR = str(Path(__file__).parent.parent / "web")

app = Flask(__name__, static_folder=WEB_DIR, static_url_path="")

_cfg = None


def init_app(cfg: dict) -> None:
    global _cfg
    _cfg = cfg


def get_config() -> dict:
    if _cfg is None:
        from .config import load
        return load()
    return _cfg


def get_db():
    conn = sqlite3.connect(get_config()["storage"]["db_path"])
    conn.row_factory = sqlite3.Row
    return conn


# ── Static ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(WEB_DIR, "index.html")


# ── API ───────────────────────────────────────────────────────────────────────

@app.route("/api/incidents")
def list_incidents():
    conn = get_db()
    rows = conn.execute(
        """
        SELECT i.id, i.event_type, i.severity, i.description,
               i.roadway, i.lat, i.lon,
               i.first_seen, i.last_updated,
               COUNT(ic.id)                                                   AS camera_count,
               SUM(CASE WHEN ic.snapshot_path IS NOT NULL THEN 1 ELSE 0 END) AS snapshot_count,
               SUM(CASE WHEN ic.ai_visible = 1 THEN 1 ELSE 0 END)            AS visible_count
        FROM incidents i
        LEFT JOIN incident_cameras ic ON ic.incident_id = i.id
        GROUP BY i.id
        ORDER BY i.first_seen DESC
        """
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/incidents/<path:incident_id>")
def get_incident(incident_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
    if not row:
        abort(404)
    incident = dict(row)

    cameras = conn.execute(
        """
        SELECT camera_id, camera_name, distance_km, snapshot_path,
               ai_visible, ai_summary, ai_confidence, ai_image_quality,
               ai_evidence, captured_at
        FROM incident_cameras WHERE incident_id = ?
        ORDER BY distance_km
        """,
        (incident_id,),
    ).fetchall()

    cam_list = []
    for c in cameras:
        cam = dict(c)
        try:
            cam["ai_evidence"] = json.loads(cam.get("ai_evidence") or "[]")
        except (ValueError, TypeError):
            cam["ai_evidence"] = []
        cam_list.append(cam)

    incident["cameras"] = cam_list
    incident["raw_json"] = json.loads(incident.get("raw_json") or "{}")
    return jsonify(incident)



# ── Incident file serving ──────────────────────────────────────────────────────

@app.route("/incidents/<path:filepath>")
def incident_file(filepath):
    return send_from_directory(get_config()["storage"]["incidents_dir"], filepath)


# ── Entry point ────────────────────────────────────────────────────────────────

def serve(cfg: dict) -> None:
    """Serve with waitress. Blocks forever."""
    from waitress import serve as waitress_serve
    init_app(cfg)
    host, port = cfg["web"]["host"], cfg["web"]["port"]
    print(f" * Serving on http://{host}:{port}")
    waitress_serve(app, host=host, port=port, threads=4)
