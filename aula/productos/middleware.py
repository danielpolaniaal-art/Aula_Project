# productos/middleware.py
"""
CORS mínimo: permite que un frontend servido desde otro origen
(p. ej. Live Server en http://127.0.0.1:5500) llame a /api/.
Los orígenes permitidos se definen en settings.CORS_ALLOWED_ORIGINS.
"""

from django.conf import settings
from django.http import HttpResponse


class SimpleCORSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origen = request.headers.get("Origin")
        permitido = (
            request.path.startswith("/api/")
            and origen in getattr(settings, "CORS_ALLOWED_ORIGINS", [])
        )
        # Preflight: el navegador pregunta antes de enviar PUT/DELETE/JSON.
        if permitido and request.method == "OPTIONS":
            respuesta = HttpResponse(status=204)
        else:
            respuesta = self.get_response(request)
        if permitido:
            respuesta["Access-Control-Allow-Origin"] = origen
            respuesta["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            respuesta["Access-Control-Allow-Headers"] = "Content-Type"
            respuesta["Vary"] = "Origin"
        return respuesta
