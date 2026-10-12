# productos/forms.py
"""
DECISIÓN TÉCNICA:
Aunque el requisito pide vistas basadas en función para que el flujo del
'request' sea explícito, la VALIDACIÓN de datos se delega a un ModelForm.

¿Por qué no validar 'a mano' en la vista?
- Un ModelForm reutiliza las reglas ya definidas en el modelo (MinValueValidator,
  PositiveIntegerField, etc.), evitando duplicar lógica de negocio.
- Limpia y castea tipos automáticamente (str del POST -> Decimal, int, bool).
- Genera automáticamente los mensajes de error que se muestran en el HTML.
Esto es un estándar de la industria: "no repitas reglas de validación".
"""

from django import forms
from .models import Producto


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["nombre", "descripcion", "precio", "stock", "activo"]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_nombre(self):
        """
        Validación adicional específica del negocio: evita nombres
        vacíos o compuestos solo de espacios, algo que CharField
        por sí solo no detecta.
        """
        nombre = self.cleaned_data["nombre"].strip()
        if not nombre:
            raise forms.ValidationError("El nombre no puede estar vacío.")
        return nombre
