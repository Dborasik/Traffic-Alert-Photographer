import logging
import subprocess
import requests

TIMEOUT = 20
MJPEG_MAX_BYTES = 512 * 1024

log = logging.getLogger(__name__)


def _capture_mjpeg(url: str) -> bytes | None:
    try:
        with requests.get(url, stream=True, timeout=TIMEOUT) as resp:
            resp.raise_for_status()
            buf = b""
            for chunk in resp.iter_content(chunk_size=4096):
                buf += chunk
                end = buf.find(b"\xff\xd9")
                if end != -1:
                    start = buf.rfind(b"\xff\xd8", 0, end)
                    if start != -1:
                        return buf[start: end + 2]
                if len(buf) > MJPEG_MAX_BYTES:
                    break
    except Exception as e:
        log.debug("MJPEG capture failed for %s: %s", url, e)
    return None


def _capture_ffmpeg(url: str) -> bytes | None:
    try:
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", url, "-frames:v", "1", "-f", "image2", "-vcodec", "mjpeg", "pipe:1"],
            capture_output=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout
        log.debug("ffmpeg exited %d for %s", result.returncode, url)
    except FileNotFoundError:
        log.warning("ffmpeg not found on PATH — cannot capture HLS/video streams")
    except subprocess.TimeoutExpired:
        log.debug("ffmpeg timed out for %s", url)
    except Exception as e:
        log.debug("ffmpeg capture failed for %s: %s", url, e)
    return None


def _capture_still(url: str) -> bytes | None:
    try:
        resp = requests.get(url, timeout=TIMEOUT, headers={"Accept": "image/*"})
        resp.raise_for_status()
        ct = resp.headers.get("Content-Type", "")
        if "image" in ct:
            return resp.content
        log.debug("Still URL returned non-image content-type '%s' for %s", ct, url)
    except Exception as e:
        log.debug("Still capture failed for %s: %s", url, e)
    return None


def _is_mjpeg(url: str) -> bool:
    url_lower = (url or "").lower()
    return "mjpg" in url_lower or "mjpeg" in url_lower


def capture_snapshot(camera: dict) -> bytes | None:
    """
    Capture a live snapshot from a camera.
    Tries VideoUrl first (MJPEG or ffmpeg), falls back to still Url.
    """
    video_url = camera.get("VideoUrl")
    still_url = camera.get("Url")
    cam_id = camera.get("ID", "?")

    if video_url:
        log.debug("Capturing live frame for camera %s", cam_id)
        frame = _capture_mjpeg(video_url) if _is_mjpeg(video_url) else _capture_ffmpeg(video_url)
        if frame:
            return frame
        log.debug("Live capture failed for camera %s, trying still fallback", cam_id)

    if still_url:
        return _capture_still(still_url)

    log.debug("No usable URL for camera %s", cam_id)
    return None
