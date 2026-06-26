// frontend/src/services/api.js
import { authService } from './authService.js';

const API_URL = 'http://localhost:8000/api/v1';

// Función de ayuda para no repetir el código del header en cada petición
async function fetchConSeguridad(endpoint, opciones = {}) {
    const token = authService.getToken();

    // Si no hay token, lo pateamos al login por seguridad
    if (!token) {
        authService.logout();
        throw new Error('No autorizado');
    }

    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...opciones.headers
    };

    const response = await fetch(`${API_URL}${endpoint}`, { ...opciones, headers });

    // Si el token expiró (código 401), cerramos sesión automáticamente
    if (response.status === 401) {
        authService.logout();
    }

    return response;
}

// === PETICIONES DE NEGOCIO ===

export async function fetchSalas() {
    const res = await fetchConSeguridad('/rooms');
    return res.json();
}

export async function fetchAsignaciones() {
    const res = await fetchConSeguridad('/assignments');
    return res.json();
}

// FIX: fetchStats estaba siendo importada en coordinador.js y docente.js pero no existía
export async function fetchStats() {
    const res = await fetchConSeguridad('/statistics');
    return res.json();
}

export async function fetchSolicitudes() {
    const res = await fetchConSeguridad('/requests');
    return res.json();
}