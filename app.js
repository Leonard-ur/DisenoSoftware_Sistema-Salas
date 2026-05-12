document.addEventListener('DOMContentLoaded', () => {

    // ==========================================
    // LÓGICA DE NAVEGACIÓN (SIMULACIÓN SPA)
    // ==========================================
    const navLinks = document.querySelectorAll('.nav-link');
    const viewSections = document.querySelectorAll('.view-section');
    const headerTitle = document.getElementById('header-title');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // 1. Quitar estilos activos de todos los links
            navLinks.forEach(l => {
                l.classList.remove('bg-blue-800', 'text-white', 'font-medium', 'active-link');
                l.classList.add('text-gray-300');
            });

            // 2. Añadir estilo activo al link clickeado
            link.classList.add('bg-blue-800', 'text-white', 'font-medium', 'active-link');
            link.classList.remove('text-gray-300');

            // 3. Ocultar todas las vistas
            viewSections.forEach(view => {
                view.classList.add('hidden');
                view.classList.remove('block');
            });

            // 4. Mostrar la vista objetivo
            const targetId = link.getAttribute('data-target');
            const targetView = document.getElementById(targetId);
            if (targetView) {
                targetView.classList.remove('hidden');
                targetView.classList.add('block');
            }

            // 5. Cambiar el título del Header (Opcional para que se vea más real)
            if(headerTitle) {
                headerTitle.innerText = link.innerText.trim();
            }
        });
    });

    
    // ==========================================
    // LÓGICA VISTA PROFESOR (FORMULARIO)
    // ==========================================
    const formulario = document.getElementById('formularioSala');
    const mensajeDiv = document.getElementById('mensajeResultado');
    const btnEnviar = document.getElementById('btnEnviar');

    if(formulario) {
        formulario.addEventListener('submit', async (e) => {
            e.preventDefault(); 
            const formData = new FormData(formulario);
            const datosSolicitud = {
                curso: formData.get('curso'),
                aforo: parseInt(formData.get('aforo')),
                horario: formData.get('horario'),
                tipoEspacio: formData.get('tipoEspacio'),
                accesibilidad: formData.get('accesibilidad') === 'on' 
            };

            const textoOriginal = btnEnviar.innerHTML;
            btnEnviar.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Procesando...';
            btnEnviar.disabled = true;
            btnEnviar.classList.add('opacity-70');

            try {
                await simularPeticionBackend(datosSolicitud);
                mostrarMensaje('¡Solicitud enviada con éxito!', 'success');
                formulario.reset(); 
            } catch (error) {
                mostrarMensaje('Hubo un error al enviar la solicitud.', 'error');
            } finally {
                btnEnviar.innerHTML = textoOriginal;
                btnEnviar.disabled = false;
                btnEnviar.classList.remove('opacity-70');
            }
        });
    }

    // ==========================================
    // LÓGICA VISTA COORDINADOR (MOTOR DE REGLAS)
    // ==========================================
    const btnSugerir = document.querySelector('.btn-sugerir');
    const modal = document.getElementById('modalSugerencia');
    const loaderMotor = document.getElementById('loaderMotor');
    const resultadoMotor = document.getElementById('resultadoMotor');
    const btnCerrarX = document.getElementById('btnCerrarX');
    const btnCancelarModal = document.getElementById('btnCancelarModal');
    const btnConfirmarAsignacion = document.getElementById('btnConfirmarAsignacion');

    if (btnSugerir) {
        btnSugerir.addEventListener('click', () => {
            modal.classList.remove('hidden');
            resultadoMotor.classList.add('hidden');
            btnConfirmarAsignacion.classList.add('hidden');
            loaderMotor.classList.remove('hidden');

            setTimeout(() => {
                loaderMotor.classList.add('hidden');
                resultadoMotor.classList.remove('hidden');
                btnConfirmarAsignacion.classList.remove('hidden');
            }, 2000); 
        });

        const cerrarModal = () => modal.classList.add('hidden');
        btnCerrarX.addEventListener('click', cerrarModal);
        btnCancelarModal.addEventListener('click', cerrarModal);

        btnConfirmarAsignacion.addEventListener('click', () => {
            btnConfirmarAsignacion.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Asignando...';
            setTimeout(() => {
                cerrarModal();
                alert("¡Sala asignada exitosamente!");
                location.reload(); 
            }, 1000);
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

    function simularPeticionBackend(datos) {
        return new Promise((resolve) => setTimeout(() => resolve({ status: 200 }), 1000));
    }
});
