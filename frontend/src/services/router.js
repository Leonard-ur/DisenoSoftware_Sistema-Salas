// frontend/src/services/router.js

/**
 * Inicializa el enrutador de la SPA.
 * @param {Object} rutas      - Mapa de data-target → nombre del archivo HTML parcial.
 * @param {Object} callbacks  - Mapa de data-target → función a ejecutar tras cargar la vista.
 */
export function initRouter(rutas = {}, callbacks = {}) {
    const navLinks = document.querySelectorAll('a[data-target]');
    const contenedorPrincipal = document.getElementById('contenedor-principal');
    const headerTitle = document.getElementById('header-title');

    if (!contenedorPrincipal) {
        console.error('[Router] No se encontró el elemento #contenedor-principal en el DOM.');
        return;
    }

    navLinks.forEach(link => {
        link.addEventListener('click', async (e) => {
            e.preventDefault();

            // === 1. CAMBIO DE ESTILOS VISUALES DEL MENÚ ===
            navLinks.forEach(l => l.className = 'flex items-center gap-3 px-3 py-2 text-zinc-400 hover:bg-zinc-900 hover:text-zinc-200 rounded-lg transition-colors');
            link.className = 'flex items-center gap-3 px-3 py-2 bg-zinc-800 text-zinc-100 rounded-lg font-medium transition-colors';

            if (headerTitle) {
                headerTitle.textContent = link.textContent.trim();
            }

            // === 2. SABER QUÉ ARCHIVO CARGAR ===
            const targetId = link.getAttribute('data-target');
            const archivoHtml = rutas[targetId];

            if (!archivoHtml) {
                console.error(`[Router] No se encontró ruta para el target: ${targetId}`);
                return;
            }

            // === 3. INYECTAR EL HTML (FETCH) ===
            try {
                // Mostrar spinner de carga
                contenedorPrincipal.innerHTML = `
                    <div class="flex justify-center items-center h-64 text-zinc-500">
                        <i data-lucide="loader-2" class="animate-spin w-8 h-8"></i>
                    </div>
                `;
                lucide.createIcons();

                // Ir a buscar el archivo físico (la ruta es relativa al HTML que cargó este script)
                const response = await fetch(archivoHtml);
                if (!response.ok) throw new Error(`No se encontró el archivo: ${archivoHtml}`);

                const htmlText = await response.text();
                contenedorPrincipal.innerHTML = htmlText;

                // === 4. EJECUTAR LÓGICA DESPUÉS DE INYECTAR ===
                lucide.createIcons();

                if (callbacks[targetId]) {
                    callbacks[targetId]();
                }

            } catch (error) {
                console.error('[Router] Error al cargar vista:', error);
                contenedorPrincipal.innerHTML = `
                    <div class="text-rose-400 p-6 bg-rose-500/10 rounded-xl border border-rose-500/20 text-center">
                        <i data-lucide="alert-triangle" class="w-8 h-8 mx-auto mb-2"></i>
                        <p>Error al cargar la vista. Verifica que el archivo <code>${archivoHtml}</code> exista.</p>
                    </div>
                `;
                lucide.createIcons();
            }
        });
    });

    // === 5. CARGAR LA PRIMERA PÁGINA POR DEFECTO ===
    const primerEnlace = document.querySelector('a[data-target]');
    if (primerEnlace) primerEnlace.click();
}