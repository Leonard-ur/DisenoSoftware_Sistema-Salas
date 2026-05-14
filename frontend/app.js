document.addEventListener('DOMContentLoaded', () => {

    const API_URL = 'http://localhost:8000/api';

    // ==========================================
    // LÓGICA DE NAVEGACIÓN (SPA)
    // ==========================================
    const navLinks = document.querySelectorAll('.nav-link');
    const viewSections = document.querySelectorAll('.view-section');
    const headerTitle = document.getElementById('header-title');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            navLinks.forEach(l => {
                l.classList.remove('bg-blue-800', 'text-white', 'font-medium', 'active-link');
                l.classList.add('text-gray-300');
            });
            link.classList.add('bg-blue-800', 'text-white', 'font-medium', 'active-link');
            link.classList.remove('text-gray-300');

            viewSections.forEach(view => {
                view.classList.add('hidden');
                view.classList.remove('block');
            });

            const targetId = link.getAttribute('data-target');
            const targetView = document.getElementById(targetId);
            if (targetView) {
                targetView.classList.remove('hidden');
                targetView.classList.add('block');
            }

            if (headerTitle) {
                headerTitle.innerText = link.innerText.trim();
            }

            // Disparar loader según la vista activada
            if (viewLoaders[targetId]) {
                viewLoaders[targetId]();
            }
        });
    });

    // ==========================================
    // MAPA DE VISTAS → FUNCIONES DE CARGA
    // ==========================================
    const viewLoaders = {
        'view-panel':           cargarPanelCoordinador,
        'view-mapa':            cargarInventarioSalas,
        'view-inicio':          cargarInicioProfesor,
        'view-mis-solicitudes': cargarMisSolicitudes,
    };

    // Cargar la vista inicial activa
    const vistaActiva = document.querySelector('.view-section.block, .view-section:not(.hidden)');
    if (vistaActiva && viewLoaders[vistaActiva.id]) {
        viewLoaders[vistaActiva.id]();
    }

    // ==========================================
    // COORDINADOR — PANEL GENERAL
    // ==========================================
    async function cargarPanelCoordinador() {
        try {
            // Cargamos stats y asignaciones en paralelo
            const [statsRes, asigRes] = await Promise.all([
                fetch(`${API_URL}/estadisticas`),
                fetch(`${API_URL}/asignaciones-detalle`),
            ]);

            if (statsRes.ok) {
                const stats = await statsRes.json();
                setTexto('stat-total',          stats.total_salas);
                setTexto('stat-disponibles',    stats.disponibles);
                setTexto('stat-asignadas',      stats.asignaciones ?? stats.asignadas);
                setTexto('stat-mantenimiento',  stats.mantenimiento);
            }

            const contenedor = document.getElementById('tabla-asignaciones-panel');
            if (contenedor && asigRes.ok) {
                const asignaciones = await asigRes.json();
                contenedor.innerHTML = renderTablaAsignaciones(asignaciones, true);
            }
        } catch (err) {
            console.error('Error cargando panel coordinador:', err);
            setTexto('stat-total', '—');
            setTexto('stat-disponibles', '—');
            setTexto('stat-asignadas', '—');
            setTexto('stat-mantenimiento', '—');
        }
    }

    // ==========================================
    // COORDINADOR — INVENTARIO DE AULAS
    // ==========================================
    let todasLasSalas = [];

    async function cargarInventarioSalas() {
        const contenedor = document.getElementById('contenedor-salas');
        if (!contenedor) return;

        try {
            const res = await fetch(`${API_URL}/salas`);
            if (!res.ok) throw new Error('Error al obtener salas');
            todasLasSalas = await res.json();
            renderTarjetasSalas('TODOS');
        } catch (err) {
            console.error('Error cargando salas:', err);
            contenedor.innerHTML = `
                <div class="col-span-full text-center py-12 text-red-400">
                    <i class="fa-solid fa-triangle-exclamation text-3xl mb-3"></i>
                    <p>No se pudo conectar con el servidor.</p>
                </div>`;
        }
    }

    function renderTarjetasSalas(filtro) {
        const contenedor = document.getElementById('contenedor-salas');
        if (!contenedor) return;

        const salas = filtro === 'TODOS'
            ? todasLasSalas
            : todasLasSalas.filter(s => s.estado === filtro);

        if (salas.length === 0) {
            contenedor.innerHTML = `
                <div class="col-span-full text-center py-12 text-gray-400">
                    <i class="fa-solid fa-magnifying-glass text-3xl mb-3"></i>
                    <p>No hay salas con este estado.</p>
                </div>`;
            return;
        }

        contenedor.innerHTML = salas.map(sala => {
            const estadoConfig = {
                'DISPONIBLE':   { badge: 'bg-green-100 text-green-700 border-green-200',  dot: 'bg-green-500',  icono: 'fa-circle-check' },
                'ASIGNADA':     { badge: 'bg-yellow-100 text-yellow-700 border-yellow-200', dot: 'bg-yellow-500', icono: 'fa-lock' },
                'MANTENIMIENTO':{ badge: 'bg-red-100 text-red-700 border-red-200',         dot: 'bg-red-500',    icono: 'fa-screwdriver-wrench' },
            };
            const cfg = estadoConfig[sala.estado] || estadoConfig['DISPONIBLE'];

            return `
            <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-5 hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start mb-3">
                    <h4 class="text-lg font-bold text-[#0A2540]">
                        <i class="fa-solid fa-door-open mr-2 text-gray-400"></i>${sala.codigo}
                    </h4>
                    <span class="flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full border ${cfg.badge}">
                        <span class="w-1.5 h-1.5 rounded-full ${cfg.dot}"></span>${sala.estado}
                    </span>
                </div>
                <div class="space-y-1.5 text-sm text-gray-600">
                    <p><i class="fa-solid fa-users w-4 mr-1 text-gray-400"></i> Capacidad: <strong>${sala.capacidad} personas</strong></p>
                    <p>
                        <i class="fa-solid fa-display w-4 mr-1 text-gray-400"></i>
                        Proyector: <strong>${sala.proyector_ok ? '<span class="text-green-600">Disponible</span>' : '<span class="text-gray-400">No disponible</span>'}</strong>
                    </p>
                    <p>
                        <i class="fa-solid fa-plug w-4 mr-1 text-gray-400"></i>
                        Enchufes: <strong>${sala.enchufes_usables > 0 ? sala.enchufes_usables + ' usables' : '<span class="text-gray-400">Sin enchufes</span>'}</strong>
                    </p>
                </div>
            </div>`;
        }).join('');
    }

    // Filtros de salas
    const filtrosBtns = document.getElementById('filtros-sala');
    if (filtrosBtns) {
        filtrosBtns.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-filtro]');
            if (!btn) return;

            filtrosBtns.querySelectorAll('.filtro-btn').forEach(b => {
                b.classList.remove('bg-[#0A2540]', 'text-white');
                b.classList.add('bg-white', 'text-gray-600');
            });
            btn.classList.add('bg-[#0A2540]', 'text-white');
            btn.classList.remove('bg-white', 'text-gray-600');

            renderTarjetasSalas(btn.dataset.filtro);
        });
    }

    // ==========================================
    // PROFESOR — INICIO
    // ==========================================
    async function cargarInicioProfesor() {
        try {
            const [statsRes, asigRes] = await Promise.all([
                fetch(`${API_URL}/estadisticas`),
                fetch(`${API_URL}/asignaciones-detalle`),
            ]);

            if (statsRes.ok) {
                const stats = await statsRes.json();
                setTexto('prof-stat-disponibles',   stats.disponibles);
                setTexto('prof-stat-mantenimiento', stats.mantenimiento);
            }
            if (asigRes.ok) {
                const asig = await asigRes.json();
                setTexto('prof-stat-asignadas', asig.length);
            }
        } catch (err) {
            console.error('Error cargando inicio profesor:', err);
        }
    }

    // ==========================================
    // PROFESOR — MIS SOLICITUDES
    // ==========================================
    async function cargarMisSolicitudes() {
        const contenedor = document.getElementById('contenedor-solicitudes');
        if (!contenedor) return;

        try {
            const res = await fetch(`${API_URL}/asignaciones-detalle`);
            if (!res.ok) throw new Error('Error al obtener asignaciones');
            const asignaciones = await res.json();
            contenedor.innerHTML = renderTablaAsignaciones(asignaciones, false);
        } catch (err) {
            console.error('Error cargando solicitudes:', err);
            contenedor.innerHTML = `
                <div class="bg-white rounded-xl border border-gray-100 p-8 text-center text-red-400">
                    <i class="fa-solid fa-triangle-exclamation text-3xl mb-3"></i>
                    <p class="font-medium">No se pudo conectar con el servidor.</p>
                </div>`;
        }
    }

    // ==========================================
    // HELPER: Tabla de asignaciones compartida
    // ==========================================
    function renderTablaAsignaciones(asignaciones, compacto) {
        if (asignaciones.length === 0) {
            return `
                <div class="text-center py-10 text-gray-400">
                    <i class="fa-solid fa-folder-open text-4xl mb-3"></i>
                    <p class="font-medium">No hay asignaciones confirmadas registradas.</p>
                </div>`;
        }

        const filas = asignaciones.map(a => `
            <tr class="hover:bg-slate-50 transition-colors">
                <td class="p-4 text-sm font-mono text-gray-500">#${a.id}</td>
                <td class="p-4 font-semibold text-[#0A2540]">
                    <i class="fa-solid fa-door-open mr-2 text-gray-300"></i>${a.sala_codigo}
                </td>
                <td class="p-4 text-sm text-gray-700">${a.bloque_dia}</td>
                <td class="p-4">
                    <span class="bg-blue-50 text-blue-700 text-xs px-2 py-1 rounded border border-blue-100 font-medium">
                        ${a.bloque_inicio} – ${a.bloque_fin}
                    </span>
                </td>
                ${compacto ? '' : `<td class="p-4 text-xs text-gray-400">${a.creado_en}</td>`}
                <td class="p-4">
                    <span class="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full font-semibold">
                        <i class="fa-solid fa-check mr-1"></i>${a.estado}
                    </span>
                </td>
            </tr>`).join('');

        return `
            <div class="overflow-x-auto rounded-xl border border-gray-100 shadow-sm">
                <table class="w-full text-left border-collapse bg-white">
                    <thead>
                        <tr class="bg-slate-50 border-b border-gray-200 text-gray-500 text-xs uppercase tracking-wider">
                            <th class="p-4 font-semibold">ID</th>
                            <th class="p-4 font-semibold">Sala</th>
                            <th class="p-4 font-semibold">Día</th>
                            <th class="p-4 font-semibold">Horario</th>
                            ${compacto ? '' : '<th class="p-4 font-semibold">Registrado</th>'}
                            <th class="p-4 font-semibold">Estado</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100 text-gray-800 text-sm">
                        ${filas}
                    </tbody>
                </table>
            </div>`;
    }

    // ==========================================
    // LÓGICA VISTA PROFESOR (Formulario simulado)
    // ==========================================
    const formulario = document.getElementById('formularioSala');
    const mensajeDiv = document.getElementById('mensajeResultado');
    const btnEnviar  = document.getElementById('btnEnviar');

    if (formulario) {
        formulario.addEventListener('submit', (e) => {
            e.preventDefault();
            const textoOriginal = btnEnviar.innerHTML;
            btnEnviar.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Procesando...';
            btnEnviar.disabled = true;

            setTimeout(() => {
                mostrarMensaje('¡Solicitud enviada con éxito! El coordinador recibirá tu requerimiento.', 'success');
                formulario.reset();
                btnEnviar.innerHTML = textoOriginal;
                btnEnviar.disabled = false;
            }, 1000);
        });
    }

    // ==========================================
    // LÓGICA MODAL COORDINADOR
    // ==========================================
    const btnSugerir           = document.querySelector('.btn-sugerir');
    const modal                = document.getElementById('modalSugerencia');
    const loaderMotor          = document.getElementById('loaderMotor');
    const resultadoMotor       = document.getElementById('resultadoMotor');
    const btnCerrarX           = document.getElementById('btnCerrarX');
    const btnCancelarModal     = document.getElementById('btnCancelarModal');
    const btnConfirmarAsignacion = document.getElementById('btnConfirmarAsignacion');

    let salaSugeridaId = null;

    if (btnSugerir) {
        btnSugerir.addEventListener('click', async () => {
            modal.classList.remove('hidden');
            resultadoMotor.classList.add('hidden');
            btnConfirmarAsignacion.classList.add('hidden');
            loaderMotor.classList.remove('hidden');

            const payloadSugerencia = {
                bloque_id: 1,
                aforo_esperado: 45,
                necesita_proyector: true,
                necesita_enchufes: false,
            };

            try {
                const response = await fetch(`${API_URL}/sugerir-salas`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payloadSugerencia),
                });

                const data = await response.json();

                if (response.ok && data.salas_sugeridas.length > 0) {
                    const mejorSala = data.salas_sugeridas[0];
                    salaSugeridaId = mejorSala.id;

                    resultadoMotor.innerHTML = `
                        <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                            <p class="text-sm text-green-800 font-semibold mb-1">¡Sala óptima encontrada!</p>
                            <h4 class="text-2xl font-bold text-green-900 flex items-center gap-2">
                                <i class="fa-solid fa-door-open"></i> Sala ${mejorSala.codigo}
                            </h4>
                        </div>
                        <ul class="text-sm text-gray-600 space-y-2 border-t pt-3 mt-3">
                            <li><i class="fa-solid fa-check text-green-500 mr-2"></i> <strong>Capacidad:</strong> ${mejorSala.capacidad} cupos</li>
                            <li><i class="fa-solid fa-check text-green-500 mr-2"></i> <strong>Proyector:</strong> ${mejorSala.proyector_ok ? 'Disponible' : 'No disponible'}</li>
                            <li><i class="fa-solid fa-check text-green-500 mr-2"></i> <strong>Estado:</strong> ${mejorSala.estado}</li>
                        </ul>`;

                    loaderMotor.classList.add('hidden');
                    resultadoMotor.classList.remove('hidden');
                    btnConfirmarAsignacion.classList.remove('hidden');
                } else {
                    loaderMotor.classList.add('hidden');
                    resultadoMotor.innerHTML = `<p class="text-red-600 font-bold">No se encontraron salas disponibles para estos requisitos.</p>`;
                    resultadoMotor.classList.remove('hidden');
                }
            } catch (error) {
                console.error('Error al conectar con la API:', error);
                loaderMotor.classList.add('hidden');
                resultadoMotor.innerHTML = `<p class="text-red-600 font-bold">Error de conexión con el servidor.</p>`;
                resultadoMotor.classList.remove('hidden');
            }
        });

        const cerrarModal = () => {
            modal.classList.add('hidden');
            salaSugeridaId = null;
        };
        btnCerrarX.addEventListener('click', cerrarModal);
        btnCancelarModal.addEventListener('click', cerrarModal);

        btnConfirmarAsignacion.addEventListener('click', async () => {
            btnConfirmarAsignacion.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Asignando...';
            btnConfirmarAsignacion.disabled = true;

            const payloadAsignacion = {
                seccion_id: 1,
                sala_id: salaSugeridaId,
                bloque_id: 1,
                coordinador_id: 1,
            };

            try {
                const response = await fetch(`${API_URL}/asignar`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payloadAsignacion),
                });

                if (response.ok) {
                    cerrarModal();
                    alert('¡Sala asignada exitosamente en la Base de Datos!');
                    location.reload();
                } else {
                    const errorData = await response.json();
                    alert(`Error al asignar: ${errorData.detail}`);
                    btnConfirmarAsignacion.innerHTML = '<i class="fa-solid fa-check"></i> Asignar Sala';
                    btnConfirmarAsignacion.disabled = false;
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error de conexión al intentar asignar la sala.');
            }
        });
    }

    // ==========================================
    // UTILIDADES
    // ==========================================
    function setTexto(id, valor) {
        const el = document.getElementById(id);
        if (el) el.textContent = valor ?? '—';
    }

    function mostrarMensaje(texto, tipo) {
        if (!mensajeDiv) return;
        mensajeDiv.classList.remove('hidden', 'bg-green-100', 'text-green-800', 'bg-red-100', 'text-red-800');
        if (tipo === 'success') {
            mensajeDiv.classList.add('bg-green-100', 'text-green-800', 'border', 'border-green-200');
            mensajeDiv.innerHTML = `<i class="fa-solid fa-circle-check mr-2"></i> ${texto}`;
        } else {
            mensajeDiv.classList.add('bg-red-100', 'text-red-800', 'border', 'border-red-200');
            mensajeDiv.innerHTML = `<i class="fa-solid fa-circle-exclamation mr-2"></i> ${texto}`;
        }
        mensajeDiv.classList.remove('hidden');
        setTimeout(() => { mensajeDiv.classList.add('hidden'); }, 5000);
    }
});
