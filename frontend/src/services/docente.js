// frontend/src/services/docente.js
// FIX: La ruta era '../services/api.js' (incorrecta). docente.js está en src/services/ así que es './api.js'
import { fetchStats, fetchAsignaciones } from './api.js';

// ==========================================
// RENDERIZADO DEL INICIO (Métricas)
// ==========================================
export async function cargarInicioProfesor() {
    try {
        // Hacemos las peticiones en paralelo para que cargue más rápido
        const [stats, asignaciones] = await Promise.all([
            fetchStats(),
            fetchAsignaciones()
        ]);

        setTexto('prof-stat-disponibles', stats.available);
        setTexto('prof-stat-mantenimiento', stats.maintenance);
        setTexto('prof-stat-asignadas', asignaciones.length);

    } catch (err) {
        console.error('Error cargando inicio del profesor:', err);
        setTexto('prof-stat-disponibles', '—');
        setTexto('prof-stat-mantenimiento', '—');
        setTexto('prof-stat-asignadas', '—');
    }
}

// ==========================================
// RENDERIZADO DE "MIS SOLICITUDES"
// ==========================================
export async function cargarMisSolicitudes() {
    const contenedor = document.getElementById('contenedor-solicitudes');
    if (!contenedor) return;

    try {
        const asignaciones = await fetchAsignaciones();

        if (asignaciones.length === 0) {
            contenedor.innerHTML = `
                <div class="text-center py-10 text-zinc-500 bg-zinc-900 border border-zinc-800 rounded-xl">
                    <i data-lucide="folder-open" class="w-10 h-10 mx-auto mb-3 text-zinc-600"></i>
                    <p class="font-medium">No tienes asignaciones confirmadas registradas.</p>
                </div>`;
        } else {
            contenedor.innerHTML = `
                <div class="overflow-x-auto rounded-xl border border-zinc-800 shadow-sm">
                    <table class="w-full text-left border-collapse bg-zinc-900">
                        <thead>
                            <tr class="bg-zinc-950/50 border-b border-zinc-800 text-zinc-400 text-xs uppercase tracking-wider">
                                <th class="p-4 font-medium">ID</th>
                                <th class="p-4 font-medium">Sala</th>
                                <th class="p-4 font-medium">Día</th>
                                <th class="p-4 font-medium">Horario</th>
                                <th class="p-4 font-medium text-right">Estado</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-zinc-800 text-sm text-zinc-300">
                            ${asignaciones.map(a => `
                                <tr class="hover:bg-zinc-800/50 transition-colors">
                                    <td class="p-4 font-mono text-zinc-500">#${a.id}</td>
                                    <td class="p-4 font-semibold text-zinc-100 flex items-center gap-2">
                                        <i data-lucide="door-open" class="w-4 h-4 text-zinc-500"></i> ${a.room_code}
                                    </td>
                                    <td class="p-4">${a.time_block_day || 'Lunes'}</td>
                                    <td class="p-4">
                                        <span class="bg-zinc-800 text-zinc-300 text-xs px-2.5 py-1 rounded-md border border-zinc-700">
                                            ${a.time_block_start} – ${a.time_block_end}
                                        </span>
                                    </td>
                                    <td class="p-4 text-right">
                                        <span class="inline-flex items-center gap-1 bg-emerald-500/10 text-emerald-400 text-xs px-2 py-1 rounded-md border border-emerald-500/20 font-medium">
                                            <i data-lucide="check" class="w-3 h-3"></i> Confirmada
                                        </span>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>`;
        }

        lucide.createIcons();

    } catch (err) {
        console.error('Error cargando solicitudes:', err);
        contenedor.innerHTML = `
            <div class="bg-rose-500/5 border border-rose-500/20 rounded-xl p-8 text-center text-rose-400">
                <i data-lucide="alert-triangle" class="w-8 h-8 mx-auto mb-3"></i>
                <p class="font-medium">No se pudo conectar con el servidor.</p>
            </div>`;
        lucide.createIcons();
    }
}

// ==========================================
// LÓGICA DEL FORMULARIO DE SOLICITUD
// ==========================================
export function inicializarFormularioDocente() {
    const formulario  = document.getElementById('formularioSala');
    const mensajeDiv  = document.getElementById('mensajeResultado');
    const btnEnviar   = document.getElementById('btnEnviar');

    if (!formulario) return;

    formulario.addEventListener('submit', (e) => {
        e.preventDefault();

        const textoOriginal = btnEnviar.innerHTML;
        btnEnviar.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Procesando...';
        btnEnviar.disabled = true;
        lucide.createIcons();

        // Simulamos el envío a la API
        setTimeout(() => {
            mostrarMensaje(mensajeDiv, '¡Solicitud enviada con éxito! El coordinador evaluará tu requerimiento.', 'success');
            formulario.reset();
            btnEnviar.innerHTML = textoOriginal;
            btnEnviar.disabled = false;
            lucide.createIcons();
        }, 1200);
    });
}

// ==========================================
// FUNCIONES DE UTILIDAD PRIVADAS
// ==========================================
function setTexto(id, valor) {
    const el = document.getElementById(id);
    if (el) el.textContent = valor ?? '—';
}

function mostrarMensaje(elemento, texto, tipo) {
    if (!elemento) return;

    elemento.className = 'rounded-lg p-4 text-sm font-medium flex items-center gap-2 mb-4';

    if (tipo === 'success') {
        elemento.classList.add('bg-emerald-500/10', 'text-emerald-400', 'border', 'border-emerald-500/20');
        elemento.innerHTML = `<i data-lucide="check-circle" class="w-5 h-5"></i> ${texto}`;
    } else {
        elemento.classList.add('bg-rose-500/10', 'text-rose-400', 'border', 'border-rose-500/20');
        elemento.innerHTML = `<i data-lucide="alert-circle" class="w-5 h-5"></i> ${texto}`;
    }

    elemento.classList.remove('hidden');
    lucide.createIcons();

    setTimeout(() => { elemento.classList.add('hidden'); }, 5000);
}