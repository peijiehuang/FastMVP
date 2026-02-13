"""IP address utilities."""


def get_real_ip(request) -> str:
    """Extract real client IP from request headers."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    if request.client:
        return request.client.host
    return "127.0.0.1"


def get_ip_location(ip: str) -> str:
    """Get location description for an IP address.

    This is a simplified implementation. In production,
    integrate with an IP geolocation database or API.
    """
    if ip in ("127.0.0.1", "0:0:0:0:0:0:0:1", "::1", "localhost"):
        return "内网IP"
    if ip.startswith("10.") or ip.startswith("172.") or ip.startswith("192.168."):
        return "内网IP"
    return "未知"
