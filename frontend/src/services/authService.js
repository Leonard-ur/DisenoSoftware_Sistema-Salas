// frontend/src/services/authService.js

const API_URL = 'http://localhost:8000/api/v1';

export const authService = {
    // 1. Iniciar sesión
    async login(username, password) {
        try {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) throw new Error('Credenciales inválidas');

            const data = await response.json();

            // Guardamos el token y el rol del usuario en el navegador
            localStorage.setItem('token', data.token);
            localStorage.setItem('userRole', data.role); // ej: 'DOCENTE' o 'COORDINADOR'
            localStorage.setItem('userName', data.name);
            localStorage.setItem('user_id', data.user_id);

            return data;
        } catch (error) {
            console.error('Error en login:', error);
            throw error;
        }
    },

    // 2. Cerrar sesión
    logout() {
        // Borramos todo rastro del usuario
        localStorage.removeItem('token');
        localStorage.removeItem('userRole');
        localStorage.removeItem('userName');
        localStorage.removeItem('user_id');

        // Lo mandamos de vuelta a la página de login
        window.location.href = '../../../index.html'; // Usando ruta relativa para que funcione sin importar desde dónde se levante el Live Server
    },

    // 3. Obtener el token (para usarlo en otras peticiones)
    getToken() {
        return localStorage.getItem('token');
    },

    // 4. Saber si está logueado
    isAuthenticated() {
        return !!localStorage.getItem('token');
    },

    // 5. Saber qué rol tiene (para no dejar entrar a profes a la vista de admin)
    getRole() {
        return localStorage.getItem('userRole');
    }
};