// frontend/src/services/coordinador.js
import { fetchStats, fetchAsignaciones, fetchSalas, fetchSolicitudes } from './api.js';

// ==========================================
// PANEL GENERAL — Estadísticas del campus
// ==========================================
export async function cargarPanelCoordinador() {
    try {
        const [stats, asignaciones] = await Promise.all([
            fetchStats(),
            fetchAsignaciones()
        ]);

        setTexto('stat-total', stats.total_rooms);
        setTexto('stat-disponibles', stats.available);
        setTexto('stat-asignadas', stats.assigned);
        setTexto('stat-mantenimiento', stats.maintenance);

    } catch (err) {
        console.error('Error cargando panel coordinador:', err);
        ['stat-total', 'stat-disponibles', 'stat-asignadas', 'stat-mantenimiento']
            .forEach(id => setTexto(id, '—'));
    }
}

// ==========================================
// RENDERIZADO DEL INVENTARIO
// ==========================================
export async function cargarInventarioSalas() {
    const contenedor = document.getElementById('contenedor-salas');
    if (!contenedor) return;

    try {
        const salas = await fetchSalas();

        contenedor.innerHTML = salas.map(sala => {
            const estadoConfig = {
                'DISPONIBLE':    { badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20', dot: 'bg-emerald-500' },
                'ASIGNADA':      { badge: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',   dot: 'bg-yellow-500' },
                'MANTENIMIENTO': { badge: 'bg-rose-500/10 text-rose-400 border-rose-500/20',         dot: 'bg-rose-500' },
            };
            const cfg = estadoConfig[sala.status] || estadoConfig['DISPONIBLE'];

            return `
            <div class="bg-zinc-900 rounded-xl border border-zinc-800 shadow-sm p-5 hover:border-zinc-700 transition-colors">
                <div class="flex justify-between items-start mb-4">
                    <h4 class="text-lg font-semibold text-zinc-100 flex items-center gap-2">
                        <i data-lucide="door-open" class="w-5 h-5 text-zinc-500"></i> ${sala.code}
                    </h4>
                    <span class="flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-md border ${cfg.badge}">
                        <span class="w-1.5 h-1.5 rounded-full ${cfg.dot}"></span> ${sala.status}
                    </span>
                </div>
                <div class="space-y-2 text-sm text-zinc-400">
                    <p class="flex items-center gap-2">
                        <i data-lucide="users" class="w-4 h-4"></i> Capacidad: <strong class="text-zinc-200">${sala.capacity} personas</strong>
                    </p>
                    <p class="flex items-center gap-2">
                        <i data-lucide="projector" class="w-4 h-4"></i> Proyector:
                        ${sala.has_projector
                            ? '<strong class="text-emerald-400">Disponible</strong>'
                            : '<strong class="text-zinc-600">No disponible</strong>'}
                    </p>
                </div>
            </div>`;
        }).join('');

        lucide.createIcons();

    } catch (err) {
        console.error(err);
        const contenedor = document.getElementById('contenedor-salas');
        if (contenedor) {
            contenedor.innerHTML = `
                <div class="col-span-full text-center py-12 text-rose-400 border border-rose-500/20 rounded-xl bg-rose-500/5">
                    <i data-lucide="alert-triangle" class="w-8 h-8 mx-auto mb-3"></i>
                    <p>No se pudo conectar con el servidor.</p>
                </div>`;
            lucide.createIcons();
        }
    }
}

// ==========================================
// SOLICITUDES PENDIENTES
// ==========================================
export async function inicializarSolicitudesPendientes() {
    await cargarSolicitudesPendientes();
    
    // El listener para los botones "Sugerir Sala" se agregará después de renderizar
}

async function cargarSolicitudesPendientes() {
    const tbody = document.getElementById('tbody-solicitudes');
    if (!tbody) return;

    try {
        const solicitudes = await fetchSolicitudes();
        
        if (solicitudes.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="px-6 py-12 text-center text-zinc-500">
                        <i data-lucide="check-circle" class="w-8 h-8 mx-auto mb-3 text-emerald-500/50"></i>
                        No hay solicitudes pendientes.
                    </td>
                </tr>
            `;
            lucide.createIcons();
            return;
        }

        tbody.innerHTML = solicitudes.map(req => `
            <tr class="hover:bg-zinc-800/50 transition-colors">
                <td class="px-6 py-4 text-sm font-mono text-zinc-500">#REQ-${req.id.toString().padStart(3, '0')}</td>
                <td class="px-6 py-4 text-sm font-medium text-zinc-200">${req.teacher_name}</td>
                <td class="px-6 py-4">
                    <p class="text-sm font-medium text-zinc-200">${req.course_name}</p>
                    <p class="text-xs text-zinc-500 mt-1 flex items-center gap-1">
                        <i data-lucide="users" class="w-3 h-3"></i> ${req.expected_attendance} est.
                        ${req.requires_accessibility ? `<span class="ml-2 flex items-center gap-1 text-emerald-400" title="Accesibilidad Universal Requerida"><i data-lucide="wheelchair" class="w-3 h-3"></i> Acc.</span>` : ''}
                        ${req.requires_projector ? `<span class="ml-2 flex items-center gap-1 text-sky-400" title="Requiere Proyector"><i data-lucide="projector" class="w-3 h-3"></i> Proy.</span>` : ''}
                    </p>
                </td>
                <td class="px-6 py-4">
                    <span class="bg-zinc-800 text-zinc-300 text-xs px-2.5 py-1 rounded-md border border-zinc-700">
                        ${req.time_block_start ? `${req.time_block_start} - ${req.time_block_end}` : 'Sin preferencia'}
                    </span>
                </td>
                <td class="px-6 py-4 text-right">
                    <button
                        data-req-id="${req.id}"
                        data-attendance="${req.expected_attendance}"
                        data-projector="${req.requires_projector}"
                        data-outlets="${req.requires_outlets}"
                        data-timeblock="${req.time_block_id || 1}"
                        class="btn-sugerir bg-zinc-100 hover:bg-white text-zinc-950 text-sm font-medium py-2 px-4 rounded-lg transition-colors flex items-center gap-2 ml-auto">
                        <i data-lucide="sparkles" class="w-4 h-4"></i> Sugerir Sala
                    </button>
                </td>
            </tr>
        `).join('');

        lucide.createIcons();
        configurarModalMotor();

    } catch (error) {
        console.error('Error cargando solicitudes:', error);
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="px-6 py-12 text-center text-rose-400">
                    <i data-lucide="alert-triangle" class="w-8 h-8 mx-auto mb-3 text-rose-500/50"></i>
                    Error al cargar las solicitudes.
                </td>
            </tr>
        `;
        lucide.createIcons();
    }
}

function configurarModalMotor() {
    const modal = document.getElementById('modalMotor');
    if (!modal) return;

    const loaderMotor        = document.getElementById('loaderMotor');
    const resultadoMotor     = document.getElementById('resultadoMotor');
    const btnCerrarX         = document.getElementById('btnCerrarX');
    const btnCancelarModal   = document.getElementById('btnCancelarModal');
    const btnConfirmar       = document.getElementById('btnConfirmarAsignacion');

    let salaSugeridaId = null;
    let currentRequestData = null;

    const API_URL = 'http://localhost:8000/api/v1';

    const cerrarModal = () => {
        modal.classList.add('hidden');
        salaSugeridaId = null;
        currentRequestData = null;
    };

    document.querySelectorAll('.btn-sugerir').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const button = e.currentTarget;
            currentRequestData = {
                req_id: button.dataset.reqId,
                time_block_id: parseInt(button.dataset.timeblock),
                expected_attendance: parseInt(button.dataset.attendance),
                requires_projector: button.dataset.projector === 'true',
                requires_outlets: button.dataset.outlets === 'true'
            };

            modal.classList.remove('hidden');
            resultadoMotor.classList.add('hidden');
            btnConfirmar.classList.add('hidden');
            loaderMotor.classList.remove('hidden');

            const payload = {
                time_block_id: currentRequestData.time_block_id,
                expected_attendance: currentRequestData.expected_attendance,
                requires_projector: currentRequestData.requires_projector,
                requires_outlets: currentRequestData.requires_outlets,
            };

            try {
                const token = localStorage.getItem('token');
                const response = await fetch(`${API_URL}/room-suggestions`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(payload),
                });

                const data = await response.json();

                if (response.ok && data.suggested_rooms?.length > 0) {
                    const mejorSala = data.suggested_rooms[0];
                    salaSugeridaId = mejorSala.id;

                    resultadoMotor.innerHTML = `
                        <div class="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-4">
                            <p class="text-sm text-emerald-400 font-semibold mb-1">¡Sala óptima encontrada!</p>
                            <h4 class="text-2xl font-bold text-emerald-300 flex items-center gap-2">
                                <i data-lucide="door-open" class="w-6 h-6"></i> Sala ${mejorSala.code}
                            </h4>
                        </div>
                        <ul class="text-sm text-zinc-400 space-y-2 border-t border-zinc-800 pt-3 mt-3">
                            <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-emerald-400"></i> <strong>Capacidad:</strong>&nbsp;${mejorSala.capacity} cupos</li>
                            <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-emerald-400"></i> <strong>Proyector:</strong>&nbsp;${mejorSala.has_projector ? 'Disponible' : 'No disponible'}</li>
                            <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-emerald-400"></i> <strong>Estado:</strong>&nbsp;${mejorSala.status}</li>
                        </ul>`;

                    loaderMotor.classList.add('hidden');
                    resultadoMotor.classList.remove('hidden');
                    btnConfirmar.classList.remove('hidden');
                    lucide.createIcons();
                } else {
                    loaderMotor.classList.add('hidden');
                    resultadoMotor.innerHTML = `<p class="text-rose-400 font-medium text-center py-4">No se encontraron salas disponibles para estos requisitos.</p>`;
                    resultadoMotor.classList.remove('hidden');
                }
            } catch (error) {
                console.error('Error al conectar con la API:', error);
                loaderMotor.classList.add('hidden');
                resultadoMotor.innerHTML = `<p class="text-rose-400 font-medium text-center py-4">Error de conexión con el servidor.</p>`;
                resultadoMotor.classList.remove('hidden');
            }
        });
    });

    btnCerrarX?.addEventListener('click', cerrarModal);
    btnCancelarModal?.addEventListener('click', cerrarModal);

    btnConfirmar?.addEventListener('click', async () => {
        btnConfirmar.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Asignando...';
        btnConfirmar.disabled = true;
        lucide.createIcons();

        const payload = {
            section_id: currentRequestData.req_id, // Usamos ID de la solicitud como section_id para el mock
            room_id: salaSugeridaId,
            time_block_id: currentRequestData.time_block_id,
            coordinator_id: parseInt(localStorage.getItem('user_id')) || 1,
        };

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/assignments`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload),
            });

            if (response.ok) {
                cerrarModal();
                alert('¡Sala asignada exitosamente!');
                location.reload();
            } else {
                const errorData = await response.json();
                alert(`Error al asignar: ${errorData.detail}`);
                btnConfirmar.innerHTML = '<i data-lucide="check" class="w-4 h-4"></i> Asignar Sala';
                btnConfirmar.disabled = false;
                lucide.createIcons();
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error de conexión al intentar asignar la sala.');
        }
    });
}

// Utilidad privada
function setTexto(id, valor) {
    const el = document.getElementById(id);
    if (el) el.textContent = valor ?? '—';
}