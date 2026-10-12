# productos/models.py
"""
Modelo de datos de Producto, alineado con la tabla `productos` del informe:
id_producto (PK, auto-increment), nombre, descripcion, precio,
cantidad_stock y fecha_registro.

Se usa el ORM de Django para que el mismo código funcione con SQLite
(desarrollo) y MySQL (entrega) sin reescribir nada, y para que la BD se
versione con migraciones.
"""


from django.db import models
from django.core.validators import MinValueValidator


class Producto(models.Model):
    nombre = models.CharField(max_length=150)

    descripcion = models.TextField(blank=True)

    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    stock = models.PositiveIntegerField(default=0)

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_creacion"]
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.nombre} (${self.precio})"

