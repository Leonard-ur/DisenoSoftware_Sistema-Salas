document.addEventListener('DOMContentLoaded', () => {
    
    // ==========================================
    // LÓGICA VISTA PROFESOR (SOLICITANTE)
    // ==========================================
    const formulario = document.getElementById('formularioSala');
    const mensajeDiv = document.getElementById('mensajeResultado');
    const btnEnviar = document.getElementById('btnEnviar');

    if(formulario) {
        formulario.addEventListener('submit', async (e) => {
            e.preventDefault(); 

            // 1. Recopilar datos ('tipoEspacio' según el PDF)
            const formData = new FormData(formulario);
            const datosSolicitud = {
                curso: formData.get('curso'),
                aforo: parseInt(formData.get('aforo')),
                horario: formData.get('horario'),
                tipoEspacio: formData.get('tipoEspacio'), // Nuevo campo
                accesibilidad: formData.get('accesibilidad') === 'on' 
            };

            const textoOriginal = btnEnviar.innerHTML;
            btnEnviar.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Procesando...';
            btnEnviar.disabled = true;
            btnEnviar.classList.add('opacity-70');

            try {
                // Mockup: Simula envío al backend (FastAPI)
                await simularPeticionBackend(datosSolicitud);

                mostrarMensaje('¡Solicitud enviada con éxito! El coordinador la revisará pronto.', 'success');
                formulario.reset(); 

            } catch (error) {
                mostrarMensaje('Hubo un error al enviar la solicitud. Intente nuevamente.', 'error');
            } finally {
                btnEnviar.innerHTML = textoOriginal;
                btnEnviar.disabled = false;
                btnEnviar.classList.remove('opacity-70');
            }
        });
    }

    // ==========================================
    // LÓGICA VISTA COORDINADOR (RESOLUTOR)
    // ==========================================
    const btnSugerir = document.querySelector('.btn-sugerir');
    const modal = document.getElementById('modalSugerencia');
    const loaderMotor = document.getElementById('loaderMotor');
    const resultadoMotor = document.getElementById('resultadoMotor');
    const btnCerrarX = document.getElementById('btnCerrarX');
    const btnCancelarModal = document.getElementById('btnCancelarModal');
    const btnConfirmarAsignacion = document.getElementById('btnConfirmarAsignacion');

    if (btnSugerir) {
        // Abrir modal y simular motor de reglas (FR-02)
        btnSugerir.addEventListener('click', () => {
            modal.classList.remove('hidden');
            resultadoMotor.classList.add('hidden');
            btnConfirmarAsignacion.classList.add('hidden');
            loaderMotor.classList.remove('hidden');

            // Simular el tiempo de procesamiento del "Cruce Automático" en Python
            setTimeout(() => {
                loaderMotor.classList.add('hidden');
                resultadoMotor.classList.remove('hidden');
                btnConfirmarAsignacion.classList.remove('hidden');
            }, 2000); // 2 segundos de evaluación
        });

        // Eventos para cerrar el modal
        const cerrarModal = () => {
            modal.classList.add('hidden');
        };

        btnCerrarX.addEventListener('click', cerrarModal);
        btnCancelarModal.addEventListener('click', cerrarModal);

        // Evento para asignar (Confirmar)
        btnConfirmarAsignacion.addEventListener('click', () => {
            btnConfirmarAsignacion.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Asignando...';
            
            setTimeout(() => {
                cerrarModal();
                alert("¡Sala asignada exitosamente! El sistema ha notificado al Dr. Roberto Silva.");
                // En un proyecto real, aquí se recargaría la tabla eliminando la solicitud
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
        return new Promise((resolve) => {
            setTimeout(() => {
                console.log("Datos recibidos en backend:", datos);
                resolve({ status: 200, message: "OK" });
            }, 1000);
        });
    }
});
