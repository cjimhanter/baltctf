from django.conf import settings
from django.http import HttpResponse


def _merge_vary_header(current_value: str | None, header: str) -> str:
    if not current_value:
        return header

    parts = [part.strip() for part in current_value.split(",") if part.strip()]
    if header not in parts:
        parts.append(header)
    return ", ".join(parts)


class SimpleCorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "OPTIONS":
            response = HttpResponse(status=204)
        else:
            response = self.get_response(request)

        origin = request.headers.get("Origin")
        allowed_origins = getattr(settings, "CORS_ALLOW_ORIGINS", [])

        if not origin or not allowed_origins:
            return response

        allow_any_origin = "*" in allowed_origins
        if not allow_any_origin and origin not in allowed_origins:
            return response

        response["Access-Control-Allow-Origin"] = "*" if allow_any_origin else origin
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response["Vary"] = _merge_vary_header(response.get("Vary"), "Origin")
        return response
