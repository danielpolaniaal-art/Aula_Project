# Backend – Sistema Web de Gestión de Inventario

API REST en Django (Python) con la tabla `productos`:
`id_producto`, `nombre`, `descripcion`, `precio`, `cantidad_stock`, `fecha_registro`
(+ `activo` para borrado lógico).

## Puesta en marcha
```
python -m venv venv            # crea un venv propio (no uses el del zip)
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Por defecto usa SQLite. Para MySQL (crear antes la BD vacía):
```
set DB_ENGINE=mysql
set DB_NAME=gestion_inventario
set DB_USER=root
set DB_PASSWORD=tu_clave
python manage.py migrate
python manage.py runserver
```

## Endpoints (JSON)
| Método | URL | Descripción |
|---|---|---|
| GET | /api/productos/ | Lista activos (`?q=texto` filtra por nombre) |
| POST | /api/productos/ | Crea (`nombre`, `precio`, `cantidad_stock`, `descripcion` opcional) |
| GET | /api/productos/<id>/ | Detalle |
| PUT | /api/productos/<id>/ | Actualiza (acepta campos parciales) |
| DELETE | /api/productos/<id>/ | Borrado lógico (`activo=false`) |

Errores: 400 `{"error": "...", "campos": {"precio": ["..."]}}`, 404 `{"error": "..."}`.
`precio` se devuelve como texto (`"25.50"`) para no perder decimales.

## Frontend
Puede abrirse con Live Server (`http://127.0.0.1:5500`); CORS ya está permitido
para ese origen (ver `CORS_ALLOWED_ORIGINS` en `aula/settings.py`).
```js
fetch("http://127.0.0.1:8000/api/productos/", {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({nombre: "Casco", precio: "25.50", cantidad_stock: 10})
}).then(r => r.json()).then(console.log);
```
