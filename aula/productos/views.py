# productos/views.py
"""
Vistas basadas en función (FBV) para el CRUD de Producto.

DECISIÓN TÉCNICA (FBV vs CBV):
Se usan funciones -y no Class-Based Views- porque el objetivo pedagógico
es que cada desarrollador junior vea, línea por línea, el ciclo de vida
de un 'request': cómo llega, qué método HTTP trae, cómo se valida y qué
'response' se devuelve. Las CBV ocultan este flujo detrás de herencia,
lo cual es potente en producción pero confuso para quien recién aprende.

Todas las vistas siguen el mismo esqueleto:
    1. Recuperar datos necesarios (get_object_or_404 si aplica).
    2. Distinguir el método HTTP (GET vs POST).
    3. Validar la entrada (vía ProductoForm).
    4. Ejecutar la operación en BD dentro de un manejo de excepciones.
    5. Redirigir (patrón Post/Redirect/Get) o renderizar el template.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import DatabaseError
from django.core.paginator import Paginator

from .models import Producto
from .forms import ProductoForm


def producto_list(request):
    """
    READ (listar).

    Se filtra por 'activo=True' porque el sistema usa borrado lógico
    (ver 'producto_delete'): un producto "eliminado" no debe volver
    a aparecer aquí, pero su historial sigue existiendo en la BD para
    auditoría, reportes o restauración futura.
    """
    productos_qs = Producto.objects.filter(activo=True)

    # Paginación: buena práctica de escalabilidad. Sin esto, una tabla
    # con 50.000 productos tumbaría el rendimiento del template.
    paginador = Paginator(productos_qs, 10)
    numero_pagina = request.GET.get("page")
    productos = paginador.get_page(numero_pagina)

    return render(request, "productos/producto_list.html", {
        "productos": productos,
    })


def producto_create(request):
    """
    CREATE.

    Patrón Post/Redirect/Get (PRG): tras un POST exitoso, se hace
    'redirect' en vez de 'render' directo. Esto evita que, si el usuario
    refresca el navegador (F5), el formulario se reenvíe por accidente
    y se duplique el producto.
    """
    if request.method == "POST":
        form = ProductoForm(request.POST)

        # form.is_valid() ejecuta TODAS las validaciones del modelo y
        # del formulario antes de tocar la base de datos: nunca se
        # confía en datos crudos del cliente (request.POST).
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Producto creado correctamente.")
                return redirect("producto_list")
            except DatabaseError:
                # Aislamos errores de infraestructura (BD caída, timeout)
                # de errores de validación: el usuario recibe un mensaje
                # claro en vez de un stack trace en pantalla.
                messages.error(request, "Error al guardar en la base de datos. Intenta de nuevo.")
        else:
            messages.error(request, "Revisa los campos marcados en rojo.")
    else:
        # GET: se muestra el formulario vacío
        form = ProductoForm()

    return render(request, "productos/producto_form.html", {
        "form": form,
        "titulo": "Nuevo producto",
    })


def producto_update(request, pk):
    """
    UPDATE.

    get_object_or_404 reemplaza un 'try/except Producto.DoesNotExist'
    manual: si el 'pk' no existe (por ejemplo, alguien manipuló la URL),
    Django responde automáticamente con un 404 limpio en vez de un
    error 500 no controlado.
    """
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == "POST":
        # instance=producto le indica al form que actualice el registro
        # existente en lugar de crear uno nuevo.
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Producto actualizado correctamente.")
                return redirect("producto_list")
            except DatabaseError:
                messages.error(request, "Error al actualizar. Intenta de nuevo.")
        else:
            messages.error(request, "Revisa los campos marcados en rojo.")
    else:
        form = ProductoForm(instance=producto)

    return render(request, "productos/producto_form.html", {
        "form": form,
        "titulo": f"Editar: {producto.nombre}",
    })


def producto_delete(request, pk):
    """
    DELETE (borrado lógico, no físico).

    DECISIÓN TÉCNICA:
    En un sistema de información empresarial (SST Magnus) casi nunca
    conviene un DELETE físico de la fila: se pierde trazabilidad para
    auditorías, reportes históricos y posibles reclamos de clientes.
    Por eso 'eliminar' aquí significa 'activo = False', no
    'producto.delete()'.

    Se exige confirmación explícita por POST: un GET nunca debe
    ejecutar una acción destructiva (buena práctica de seguridad web,
    evita borrados accidentales por bots, prefetch del navegador, etc.).
    """
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == "POST":
        try:
            producto.activo = False
            producto.save()
            messages.success(request, "Producto eliminado correctamente.")
        except DatabaseError:
            messages.error(request, "No se pudo eliminar el producto. Intenta de nuevo.")
        return redirect("producto_list")

    # GET: solo muestra una pantalla de confirmación, no borra nada aún.
    return render(request, "productos/producto_confirm_delete.html", {
        "producto": producto,
    })
