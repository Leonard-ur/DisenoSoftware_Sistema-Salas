"""
Entrypoint web del Sistema de Asignación de Salas.

Usa exclusivamente el módulo nativo ``http.server`` de Python (stdlib) para:
    - Servir el archivo estático ``frontend/index.html`` en la ruta raíz ("/").
    - Exponer la ruta ``/api/asignar`` (POST) que ejecuta el caso de uso
      ``AsignarSala`` con los adaptadores en memoria.

No requiere instalar ningún framework web externo.

Uso:
    python -m backend.app          # puerto 8000 (predeterminado)
    python -m backend.app 9000     # puerto personalizado
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict

# ---------------------------------------------------------------------------
# Ajuste de PYTHONPATH: permite ejecutar con "python backend/app.py"
# desde la raíz del repositorio aunque no se use "python -m".
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from backend.adapters.memory_repository import MemoryLockService, MemorySalaRepository  # noqa: E402
from backend.domain.models import SolicitudAsignacion  # noqa: E402
from backend.use_cases.asignar_sala import AsignarSala, SalaNoDisponibleError  # noqa: E402

# ---------------------------------------------------------------------------
# Inicialización de dependencias (singleton de proceso)
# ---------------------------------------------------------------------------

_repo         = MemorySalaRepository()
_lock_service = MemoryLockService()
_caso_uso     = AsignarSala(sala_repo=_repo, lock_service=_lock_service)

# Ruta al archivo estático index.html
_FRONTEND_DIR = _ROOT / "frontend"
_INDEX_HTML   = _FRONTEND_DIR / "index.html"


# ---------------------------------------------------------------------------
# Handler HTTP
# ---------------------------------------------------------------------------

class SalasHandler(BaseHTTPRequestHandler):
    """Maneja todas las peticiones HTTP del servidor."""

    # ── GET ──────────────────────────────────────────────────────────────

    def do_GET(self) -> None:  # noqa: N802
        """
        Sirve archivos estáticos desde /frontend.

        Rutas:
            /          → frontend/index.html
            /api/salas → JSON con el catálogo de salas (útil para debug)
        """
        if self.path in ("/", "/index.html"):
            self._serve_file(_INDEX_HTML, "text/html; charset=utf-8")

        elif self.path == "/api/salas":
            salas = [
                {
                    "id": s.id,
                    "nombre": s.nombre,
                    "capacidad": s.capacidad,
                    "equipamiento": s.equipamiento,
                }
                for s in _repo.listar_todas()
            ]
            self._json_response(200, salas)

        elif self.path == "/api/reservas":
            self._json_response(200, _repo.listar_reservas())

        else:
            self._json_response(404, {"error": "Recurso no encontrado."})

    # ── POST ─────────────────────────────────────────────────────────────

    def do_POST(self) -> None:  # noqa: N802
        """
        Procesa solicitudes de asignación.

        Ruta:
            /api/asignar  → ejecuta el caso de uso AsignarSala
        """
        if self.path == "/api/asignar":
            self._handle_asignar()
        else:
            self._json_response(404, {"error": "Ruta no encontrada."})

    # ── Lógica de negocio ─────────────────────────────────────────────

    def _handle_asignar(self) -> None:
        """Lee el cuerpo JSON, construye la solicitud y ejecuta el caso de uso."""
        body = self._read_body()
        if body is None:
            return  # la respuesta de error ya fue enviada

        # Validar campos obligatorios
        campos_requeridos = ["alumnos_inscritos", "inicio", "fin"]
        for campo in campos_requeridos:
            if campo not in body:
                self._json_response(
                    400, {"error": f"Campo obligatorio faltante: '{campo}'."}
                )
                return

        # Parsear fechas
        try:
            inicio = datetime.fromisoformat(body["inicio"])
            fin    = datetime.fromisoformat(body["fin"])
        except (ValueError, TypeError) as exc:
            self._json_response(
                400,
                {"error": f"Formato de fecha inválido: {exc}. "
                           "Use ISO 8601 (YYYY-MM-DDTHH:MM)."},
            )
            return

        if inicio >= fin:
            self._json_response(
                400, {"error": "La fecha de inicio debe ser anterior a la de fin."}
            )
            return

        # Construir la solicitud de dominio
        solicitud = SolicitudAsignacion(
            id=str(uuid.uuid4()),
            alumnos_inscritos=int(body["alumnos_inscritos"]),
            inicio=inicio,
            fin=fin,
            equipamiento_requerido=body.get("equipamiento_requerido", []),
            solicitante=body.get("solicitante", ""),
        )

        # Ejecutar el caso de uso
        try:
            asignacion = _caso_uso.ejecutar(solicitud)
        except SalaNoDisponibleError as exc:
            self._json_response(409, {"error": str(exc)})
            return
        except Exception as exc:  # noqa: BLE001
            self._json_response(500, {"error": f"Error interno: {exc}"})
            return

        # Respuesta exitosa
        self._json_response(
            200,
            {
                "sala_id":     asignacion.sala.id,
                "sala_nombre": asignacion.sala.nombre,
                "capacidad":   asignacion.sala.capacidad,
                "equipamiento": asignacion.sala.equipamiento,
                "solicitud_id": asignacion.solicitud.id,
            },
        )

    # ── Utilidades ────────────────────────────────────────────────────

    def _read_body(self) -> Dict[str, Any] | None:
        """Lee y parsea el cuerpo de la petición como JSON."""
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            self._json_response(400, {"error": "Cuerpo de la petición vacío."})
            return None
        try:
            raw = self.rfile.read(length)
            return json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            self._json_response(400, {"error": f"JSON inválido: {exc}"})
            return None

    def _serve_file(self, path: Path, content_type: str) -> None:
        """Envía un archivo estático al cliente."""
        if not path.exists():
            self._json_response(404, {"error": f"Archivo no encontrado: {path.name}"})
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json_response(self, status: int, payload: Any) -> None:
        """Serializa payload como JSON y lo envía con el status code indicado."""
        data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        """Sobreescribe el log para mostrar un formato más limpio."""
        print(f"  [{self.log_date_time_string()}]  {format % args}")


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

def run(port: int = 8000) -> None:
    """Inicia el servidor HTTP en el puerto indicado."""
    server = HTTPServer(("", port), SalasHandler)
    base_url = f"http://localhost:{port}"
    print("=" * 60)
    print("  Sistema de Asignación de Salas – Servidor HTTP")
    print("=" * 60)
    print(f"  🌐  Interfaz web : {base_url}/")
    print(f"  📡  API asignar  : {base_url}/api/asignar  (POST)")
    print(f"  📋  API catálogo : {base_url}/api/salas    (GET)")
    print(f"  📌  API reservas : {base_url}/api/reservas (GET)")
    print("  Presiona Ctrl+C para detener.")
    print("=" * 60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Servidor detenido.")
    finally:
        server.server_close()


if __name__ == "__main__":
    _port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run(_port)
