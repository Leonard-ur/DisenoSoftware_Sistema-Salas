document.addEventListener('DOMContentLoaded', () => {

    // URL base de nuestra API en FastAPI (Backend)
    const API_URL = 'http://localhost:8000/api';

    // ==========================================
    // LÓGICA DE NAVEGACIÓN (SPA) - Sin cambios
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

            if(headerTitle) {
                headerTitle.innerText = link.innerText.trim();
            }
        });
    });

    // ==========================================
    // LÓGICA VISTA PROFESOR (Simulada para el MVP)
    // ==========================================
    const formulario = document.getElementById('formularioSala');
    const mensajeDiv = document.getElementById('mensajeResultado');
    const btnEnviar = document.getElementById('btnEnviar');

    if(formulario) {
        formulario.addEventListener('submit', (e) => {
            e.preventDefault(); 
            const textoOriginal = btnEnviar.innerHTML;
            btnEnviar.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Procesando...';
            btnEnviar.disabled = true;

            // Simulamos el envío para enfocarnos en el motor del coordinador
            setTimeout(() => {
                mostrarMensaje('¡Solicitud enviada con éxito! (Simulación)', 'success');
                formulario.reset(); 
                btnEnviar.innerHTML = textoOriginal;
                btnEnviar.disabled = false;
            }, 1000);
        });
    }

    // ==========================================
    // LÓGICA VISTA COORDINADOR (CONECTADA A LA API REAL)
    // ==========================================
    const btnSugerir = document.querySelector('.btn-sugerir');
    const modal = document.getElementById('modalSugerencia');
    const loaderMotor = document.getElementById('loaderMotor');
    const resultadoMotor = document.getElementById('resultadoMotor');
    const btnCerrarX = document.getElementById('btnCerrarX');
    const btnCancelarModal = document.getElementById('btnCancelarModal');
    const btnConfirmarAsignacion = document.getElementById('btnConfirmarAsignacion');
    
    // Variable global para guardar el ID de la sala que sugiera el backend
    let salaSugeridaId = null;

    if (btnSugerir) {
        btnSugerir.addEventListener('click', async () => {
            // 1. Mostrar el modal en estado de "Cargando"
            modal.classList.remove('hidden');
            resultadoMotor.classList.add('hidden');
            btnConfirmarAsignacion.classList.add('hidden');
            loaderMotor.classList.remove('hidden');

            // 2. Preparar los datos de la solicitud (Hardcodeados para el prototipo)
            // En la vida real, estos datos saldrían de la fila de la tabla HTML
            const payloadSugerencia = {
                bloque_id: 1,
                aforo_esperado: 45,
                necesita_proyector: true,
                necesita_enchufes: false
            };

            try {
                // 3. Llamada REAL a la API de FastAPI (El trabajo de Leonardo y Camilo)
                const response = await fetch(`${API_URL}/sugerir-salas`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payloadSugerencia)
                });

                const data = await response.json();

                if (response.ok && data.salas_sugeridas.length > 0) {
                    // Tomamos la mejor sala (la primera de la lista)
                    const mejorSala = data.salas_sugeridas[0];
                    salaSugeridaId = mejorSala.id;

                    // Actualizamos el HTML del modal con los datos reales de la BD
                    resultadoMotor.innerHTML = `
                        <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                            <p class="text-sm text-green-800 font-semibold mb-1">¡Sala óptima encontrada!</p>
                            <h4 class="text-2xl font-bold text-green-900 flex items-center gap-2">
                                <i class="fa-solid fa-door-open"></i> Sala ${mejorSala.codigo}
                            </h4>
                        </div>
                        <ul class="text-sm text-gray-600 space-y-2 border-t pt-3 mt-3">
                            <li><i class="fa-solid fa-check text-green-500 mr-2"></i> <strong>Capacidad:</strong> ${mejorSala.capacidad} cupos</li>
                            <li><i class="fa-solid fa-check text-green-500 mr-2"></i> <strong>Proyector:</strong> ${mejorSala.proyector_ok ? 'Sí' : 'No'}</li>
                            <li><i class="fa-solid fa-check text-green-500 mr-2"></i> <strong>Estado:</strong> ${mejorSala.estado}</li>
                        </ul>
                    `;
                    
                    // Ocultar loader y mostrar resultados
                    loaderMotor.classList.add('hidden');
                    resultadoMotor.classList.remove('hidden');
                    btnConfirmarAsignacion.classList.remove('hidden');
                } else {
                    // Si no hay salas o hubo error
                    loaderMotor.classList.add('hidden');
                    resultadoMotor.innerHTML = `<p class="text-red-600 font-bold">No se encontraron salas disponibles para estos requisitos.</p>`;
                    resultadoMotor.classList.remove('hidden');
                }

            } catch (error) {
                console.error("Error al conectar con la API:", error);
                loaderMotor.classList.add('hidden');
                resultadoMotor.innerHTML = `<p class="text-red-600 font-bold">Error de conexión con el servidor.</p>`;
                resultadoMotor.classList.remove('hidden');
            }
        });

        // Lógica para cerrar el modal
        const cerrarModal = () => {
            modal.classList.add('hidden');
            salaSugeridaId = null; // Limpiamos la variable
        };
        btnCerrarX.addEventListener('click', cerrarModal);
        btnCancelarModal.addEventListener('click', cerrarModal);

        // 4. Confirmar la Asignación (Llamada al segundo Endpoint)
        btnConfirmarAsignacion.addEventListener('click', async () => {
            btnConfirmarAsignacion.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Asignando...';
            btnConfirmarAsignacion.disabled = true;

            const payloadAsignacion = {
                seccion_id: 1,
                sala_id: salaSugeridaId,
                bloque_id: 1,
                coordinador_id: 1 // ID del usuario coordinador
            };

            try {
                const response = await fetch(`${API_URL}/asignar`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payloadAsignacion)
                });

                if (response.ok) {
                    cerrarModal();
                    alert("¡Sala asignada exitosamente en la Base de Datos!");
                    location.reload(); 
                } else {
                    const errorData = await response.json();
                    alert(`Error al asignar: ${errorData.detail}`);
                    btnConfirmarAsignacion.innerHTML = '<i class="fa-solid fa-check"></i> Asignar Sala';
                    btnConfirmarAsignacion.disabled = false;
                }
            } catch (error) {
                console.error("Error:", error);
                alert("Error de conexión al intentar asignar la sala.");
            }
        });
    }

    // ==========================================
    // FUNCIONES DE UTILIDAD
    // ==========================================
    function mostrarMensaje(texto, tipo) {
        mensajeDiv.classList.remove('hidden', 'bg-green-100', 'text-green-800', 'bg-red-100', 'text-red-800');
        if(tipo === 'success') {
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