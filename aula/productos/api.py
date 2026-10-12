# productos/api.py
"""
API REST (JSON) de Producto. La consume el frontend con fetch().

    GET    /api/productos/          lista productos activos (?q=texto filtra por nombre)
    POST   /api/productos/          crea un producto
    GET    /api/productos/<id>/     detalle
    PUT    /api/productos/<id>/     actualiza (acepta campos parciales)
    DELETE /api/productos/<id>/     borrado lógico (activo = False)

La validación se delega a ProductoForm, así que las reglas del modelo
(precio >= 0, stock no negativo, nombre no vacío) viven en un solo lugar.
"""

import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .forms import ProductoForm
from .models import Producto

CAMPOS = ["nombre", "descripcion", "precio", "cantidad_stock", "activo"]


def _a_dict(p):
    return {
        "id_producto": p.pk,
        "nombre": p.nombre,
        "descripcion": p.descripcion,
        "precio": str(p.precio),  # string: conserva los decimales exactos
        "cantidad_stock": p.cantidad_stock,
        "activo": p.activo,
        "fecha_registro": p.fecha_registro.isoformat(),
    }


def _leer_json(request):
    """Devuelve (dict, None) o (None, JsonResponse de error 400)."""
    try:
        datos = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return None, JsonResponse({"error": "JSON inválido."}, status=400)
    if not isinstance(datos, dict):
        return None, JsonResponse({"error": "Se esperaba un objeto JSON."}, status=400)
    return datos, None


def _errores(form):
    return JsonResponse(
        {"error": "Datos inválidos.", "campos": {k: list(v) for k, v in form.errors.items()}},
        status=400,
    )


@csrf_exempt  # API consumida por un frontend aparte; CSRF aplica a formularios con sesión
@require_http_methods(["GET", "POST"])
def productos_collection(request):
    if request.method == "GET":
        qs = Producto.objects.filter(activo=True)
        q = request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(nombre__icontains=q)
        return JsonResponse({"count": qs.count(), "resultados": [_a_dict(p) for p in qs]})

    datos, error = _leer_json(request)
    if error:
        return error
    datos.setdefault("activo", True)  # un producto nuevo nace activo
    form = ProductoForm(datos)
    if not form.is_valid():
        return _errores(form)
    return JsonResponse(_a_dict(form.save()), status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def producto_detalle(request, pk):
    producto = Producto.objects.filter(pk=pk, activo=True).first()
    if producto is None:
        return JsonResponse({"error": "Producto no encontrado."}, status=404)

    if request.method == "GET":
        return JsonResponse(_a_dict(producto))

    if request.method == "DELETE":
        producto.activo = False
        producto.save()
        return JsonResponse({"mensaje": "Producto eliminado correctamente."})

    datos, error = _leer_json(request)
    if error:
        return error
    # PUT parcial: lo que no venga en el JSON conserva su valor actual.
    actual = {c: getattr(producto, c) for c in CAMPOS}
    form = ProductoForm({**actual, **datos}, instance=producto)
    if not form.is_valid():
        return _errores(form)
    return JsonResponse(_a_dict(form.save()))
