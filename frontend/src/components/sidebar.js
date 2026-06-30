<aside class="w-64 bg-zinc-950 border-r border-zinc-800 flex flex-col hidden md:flex z-20">
    <div class="p-6 flex items-center border-b border-zinc-800">
        <div class="text-xl font-semibold text-zinc-100 flex items-center gap-2">
            <i data-lucide="layers" class="w-5 h-5 text-zinc-400"></i>
            UCT<span class="font-normal text-zinc-500">Coord</span>
        </div>
    </div>
    <nav class="flex-1 px-4 py-6 space-y-1" id="nav-coordinador">
        <a href="#" data-target="view-panel"
            class="flex items-center gap-3 px-3 py-2 bg-zinc-800 text-zinc-100 rounded-lg font-medium transition-colors">
            <i data-lucide="layout-dashboard" class="w-4 h-4"></i> Panel General
        </a>
        <a href="#" data-target="view-pendientes"
            class="flex items-center gap-3 px-3 py-2 text-zinc-400 hover:bg-zinc-900 hover:text-zinc-200 rounded-lg transition-colors">
            <i data-lucide="list-todo" class="w-4 h-4"></i> Solicitudes Pendientes
        </a>
        <a href="#" data-target="view-mapa"
            class="flex items-center gap-3 px-3 py-2 text-zinc-400 hover:bg-zinc-900 hover:text-zinc-200 rounded-lg transition-colors">
            <i data-lucide="map" class="w-4 h-4"></i> Inventario de Aulas
        </a>
    </nav>
    <div class="p-4 border-t border-zinc-800">
        <a href="#" class="flex items-center gap-3 px-3 py-2 text-zinc-400 hover:text-zinc-200 transition-colors">
            <i data-lucide="log-out" class="w-4 h-4"></i> Cerrar Sesión
        </a>
    </div>
</aside>