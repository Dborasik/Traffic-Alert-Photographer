import math


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in kilometres between two lat/lon points."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def cameras_within_radius(event_lat: float, event_lon: float, cameras: list, radius_km: float) -> list:
    """Return list of (camera, distance_km) tuples sorted by distance."""
    results = []
    for cam in cameras:
        if cam.get("Disabled") or cam.get("Blocked"):
            continue
        try:
            dist = haversine(event_lat, event_lon, cam["Latitude"], cam["Longitude"])
        except (KeyError, TypeError):
            continue
        if dist <= radius_km:
            results.append((cam, dist))
    results.sort(key=lambda x: x[1])
    return results
