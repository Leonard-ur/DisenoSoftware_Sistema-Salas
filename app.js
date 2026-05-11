document.addEventListener('DOMContentLoaded', () => {
    
    const formulario = document.getElementById('formularioSala');
    const mensajeDiv = document.getElementById('mensajeResultado');
    const btnEnviar = document.getElementById('btnEnviar');

    if(formulario) {
        formulario.addEventListener('submit', async (e) => {
            e.preventDefault(); // Evita que la página se recargue

            // 1. Recopilar datos del formulario
            const formData = new FormData(formulario);
            const datosSolicitud = {
                curso: formData.get('curso'),
                aforo: parseInt(formData.get('aforo')),
                horario: formData.get('horario'),
                accesibilidad: formData.get('accesibilidad') === 'on' 
            };

            // Cambio de estado del botón (Feedback visual)
            const textoOriginal = btnEnviar.innerHTML;
            btnEnviar.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Procesando...';
            btnEnviar.disabled = true;
            btnEnviar.classList.add('opacity-70');

            try {
                // 2. Enviar datos al Backend 
                // Reemplaza '/api/solicitudes' por la URL real de tu backend (Node, Python, PHP, etc.)
                
                /* DESCOMENTAR PARA USO REAL:
                const respuesta = await fetch('https://tu-backend.com/api/solicitudes', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(datosSolicitud)
                });

                if (!respuesta.ok) throw new Error('Error al conectar con el servidor');
                const resultado = await respuesta.json();
                */

                // SIMULACIÓN DE RESPUESTA DEL BACKEND (Borrar en producción):
                const resultado = await simularRespuestaBackend(datosSolicitud);

                // 3. Mostrar resultado exitoso
                mostrarMensaje('¡Solicitud enviada con éxito! El coordinador la revisará pronto.', 'success');
                formulario.reset(); // Limpiar formulario

            } catch (error) {
                // 4. Manejo de errores
                console.error('Error:', error);
                mostrarMensaje('Hubo un error al enviar la solicitud. Intente nuevamente.', 'error');
            } finally {
                // Restaurar botón
                btnEnviar.innerHTML = textoOriginal;
                btnEnviar.disabled = false;
                btnEnviar.classList.remove('opacity-70');
            }
        });
    }

    // --- Funciones de utilidad ---

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

        // Ocultar mensaje después de 5 segundos
        setTimeout(() => {
            mensajeDiv.classList.add('hidden');
        }, 5000);
    }

    // Función Mockup para simular el delay de internet (Borrar en producción)
    function simularRespuestaBackend(datos) {
        return new Promise((resolve) => {
            setTimeout(() => {
                console.log("Datos recibidos en backend:", datos);
                resolve({ status: 200, message: "Guardado en DB" });
            }, 1500); // 1.5 segundos de retraso
        });
    }
});