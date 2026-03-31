import base64
import io
import logging
from datetime import datetime, timezone
from typing import Literal

from openai import OpenAI
from PIL import Image
from pydantic import BaseModel, Field

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a traffic incident analyst reviewing live road camera footage for an emergency monitoring system.
Assess whether a reported incident is visible or has visible consequences in the camera image.
Be precise and objective. Do not fabricate details. If the image is too dark, blurry, or obstructed
to make a confident assessment, set image_quality to "poor" or "unusable" and verdict to "uncertain"."""


class IncidentAnalysis(BaseModel):
    scene_description: str = Field(
        description="1-2 sentence objective description of what is visible in the image."
    )
    image_quality: Literal["good", "poor", "unusable"] = Field(
        description=(
            "'good' = clear image; 'poor' = dark/blurry but partially usable; "
            "'unusable' = too dark, obstructed, or corrupt to assess."
        )
    )
    verdict: Literal["yes", "no", "uncertain"] = Field(
        description=(
            "'yes' = incident or its effects are visible; "
            "'no' = no evidence of the incident; "
            "'uncertain' = image quality prevents a confident judgment."
        )
    )
    confidence: Literal["low", "medium", "high"] = Field(
        description="Confidence level in the verdict."
    )
    evidence: list[str] = Field(
        description=(
            "Specific visual elements supporting the verdict "
            "(e.g. 'emergency vehicles on shoulder', 'standing water on roadway'). "
            "Empty list if verdict is 'no' or 'uncertain'."
        )
    )


def _resize_image(image_bytes: bytes, max_dim: int) -> bytes:
    img = Image.open(io.BytesIO(image_bytes))
    img.thumbnail((max_dim, max_dim), Image.LANCZOS)
    out = io.BytesIO()
    fmt = img.format or "JPEG"
    if fmt not in ("JPEG", "PNG", "WEBP", "GIF"):
        fmt = "JPEG"
    img.save(out, format=fmt)
    return out.getvalue()


def _build_prompt(event: dict, camera: dict, distance_km: float, user_question: str) -> str:
    now = datetime.now(timezone.utc)
    hour = now.hour
    if 6 <= hour < 20:
        time_of_day = "daytime"
    elif 20 <= hour < 22 or 5 <= hour < 6:
        time_of_day = "dusk/dawn"
    else:
        time_of_day = "nighttime"

    return (
        f"INCIDENT REPORT\n"
        f"  Type     : {event.get('EventType', 'unknown')}\n"
        f"  Severity : {event.get('Severity', 'unknown')}\n"
        f"  Road     : {event.get('RoadwayName', 'unknown')}\n"
        f"  Direction: {event.get('DirectionOfTravel', 'unknown')}\n"
        f"  Details  : {event.get('Description', '').strip()}\n"
        f"\n"
        f"CAMERA\n"
        f"  Name     : {camera.get('Name', 'unknown')}\n"
        f"  Distance : {distance_km:.2f} km from incident coordinates\n"
        f"  Capture  : {time_of_day} ({now.strftime('%H:%M UTC')})\n"
        f"\n"
        f"{user_question}"
    )


def analyze(image_bytes: bytes, event: dict, camera: dict, distance_km: float, config: dict) -> dict:
    """
    Analyze a camera snapshot against an incident report using structured output.
    Returns {"visible": bool|None, "summary": str, "confidence": str, "image_quality": str, "evidence": list}.
    """
    max_dim = config.get("max_image_dimension", 1024)
    try:
        image_bytes = _resize_image(image_bytes, max_dim)
    except Exception as e:
        log.warning("Image resize failed: %s", e)

    b64 = base64.b64encode(image_bytes).decode()

    user_question = config.get(
        "prompt",
        "Analyze this camera image against the incident report above.",
    ).format(
        event_type=event.get("EventType", ""),
        roadway=event.get("RoadwayName", ""),
        description=event.get("Description", ""),
        camera_name=camera.get("Name", ""),
        distance_km=f"{distance_km:.2f}",
    )

    prompt = _build_prompt(event, camera, distance_km, user_question)
    client = OpenAI(api_key=config["api_key"])

    try:
        response = client.beta.chat.completions.parse(
            model=config.get("model", "gpt-4o"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                        {"type": "text", "text": prompt},
                    ],
                },
            ],
            response_format=IncidentAnalysis,
            max_tokens=500,
        )

        analysis: IncidentAnalysis = response.choices[0].message.parsed
        visible_map = {"yes": True, "no": False, "uncertain": None}
        visible = visible_map[analysis.verdict]

        evidence_str = "; ".join(analysis.evidence) if analysis.evidence else ""
        summary_parts = [analysis.scene_description]
        if evidence_str:
            summary_parts.append(f"Evidence: {evidence_str}")
        summary_parts.append(f"[{analysis.confidence} confidence, image: {analysis.image_quality}]")

        return {
            "visible": visible,
            "summary": " — ".join(summary_parts),
            "confidence": analysis.confidence,
            "image_quality": analysis.image_quality,
            "evidence": analysis.evidence,
        }

    except Exception as e:
        log.error("OpenAI analysis failed: %s", e)
        return {"visible": False, "summary": f"Analysis error: {e}", "confidence": None, "image_quality": None, "evidence": []}
