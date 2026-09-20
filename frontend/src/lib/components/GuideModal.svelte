<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  export let open = false;
  const dispatch = createEventDispatcher();

  function close() {
    dispatch('close');
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') close();
  }
</script>

<svelte:window on:keydown={handleKeydown} />

{#if open}
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div class="fixed inset-0 bg-black/50 z-[200] flex items-start justify-center pt-16 px-4" on:click={close}>
    <div
      class="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col"
      on:click|stopPropagation
    >
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 dark:border-gray-800">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
            <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 class="text-lg font-bold text-gray-900 dark:text-gray-100">Instructivo de Uso</h2>
        </div>
        <button on:click={close} class="p-2 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors cursor-pointer" aria-label="Cerrar">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Content -->
      <div class="overflow-y-auto px-6 py-5 space-y-6 text-sm text-gray-700 dark:text-gray-300">

        <!-- Login -->
        <section>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-2 flex items-center gap-2">
            <span class="w-6 h-6 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-[11px] font-bold text-primary-600 dark:text-primary-400">1</span>
            Iniciar Sesión
          </h3>
          <p class="ml-8">
            Ingresá tu email y contraseña en la pantalla de login. Los usuarios los crea el administrador desde la sección <strong>Usuarios</strong>. Si es tu primera vez, pedile al admin que te asigne una contraseña.
          </p>
        </section>

        <!-- Cambiar Contraseña -->
        <section>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-2 flex items-center gap-2">
            <span class="w-6 h-6 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-[11px] font-bold text-primary-600 dark:text-primary-400">2</span>
            Cambiar Contraseña
          </h3>
          <div class="ml-8 space-y-2">
            <p>Por seguridad, se recomienda que cada usuario cambie la contraseña que le asignó el administrador.</p>
            <p><strong>Pasos:</strong> Hacé clic en el ícono <strong>&#128273;</strong> (llave) en la barra superior. Poné tu contraseña actual, la nueva y confirmala. La nueva contraseña debe tener al menos 6 caracteres.</p>
            <p><strong>Nota:</strong> Solo podés cambiar tu propia contraseña. El administrador no puede ver las contraseñas de los usuarios.</p>
          </div>
        </section>

        <!-- Navegación -->
        <section>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-2 flex items-center gap-2">
            <span class="w-6 h-6 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-[11px] font-bold text-primary-600 dark:text-primary-400">3</span>
            Navegación
          </h3>
          <p class="ml-8 mb-2">
            Usá el menú lateral izquierdo para acceder a cada sección. Podés contraerlo con el botón <strong>&#9776;</strong> para tener más espacio.
          </p>
          <div class="ml-8 grid grid-cols-2 gap-2 text-xs">
            <div class="bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2">
              <span class="font-medium text-gray-900 dark:text-gray-100">Inmuebles urbanos</span>
              <p class="text-gray-500 dark:text-gray-400">Departamentos, casas, locales</p>
            </div>
            <div class="bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2">
              <span class="font-medium text-gray-900 dark:text-gray-100">Inmuebles rurales</span>
              <p class="text-gray-500 dark:text-gray-400">Campos, chacras, estancias</p>
            </div>
            <div class="bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2">
              <span class="font-medium text-gray-900 dark:text-gray-100">Personas</span>
              <p class="text-gray-500 dark:text-gray-400">Propietarios e inquilinos</p>
            </div>
            <div class="bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2">
              <span class="font-medium text-gray-900 dark:text-gray-100">Contratos</span>
              <p class="text-gray-500 dark:text-gray-400">Contratos de alquiler activos</p>
            </div>
            <div class="bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2">
              <span class="font-medium text-gray-900 dark:text-gray-100">Cobros</span>
              <p class="text-gray-500 dark:text-gray-400">Historial de pagos recibidos</p>
            </div>
            <div class="bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2">
              <span class="font-medium text-gray-900 dark:text-gray-100">Informes</span>
              <p class="text-gray-500 dark:text-gray-400">Resumen para propietarios</p>
            </div>
          </div>
        </section>

        <!-- Inmuebles -->
        <section>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-2 flex items-center gap-2">
            <span class="w-6 h-6 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-[11px] font-bold text-primary-600 dark:text-primary-400">4</span>
            Gestionar Inmuebles
          </h3>
          <div class="ml-8 space-y-2">
            <p><strong>Crear:</strong> Hacé clic en "+ Nuevo" y completá la dirección, categoría y datos del propietario. Si es copropiedad, agregá varios propietarios con su porcentaje de participación.</p>
            <p><strong>Editar:</strong> En la tabla, hacé clic en el ícono de lápiz para modificar datos, agregar/quitar copropietarios o cambiar el estado.</p>
            <p><strong>Registrar cobro (rurales):</strong> Desde la vista rural, hacé clic en el ícono de billete para registrar un pago con precio por kilo.</p>
          </div>
        </section>

        <!-- Personas -->
        <section>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-2 flex items-center gap-2">
            <span class="w-6 h-6 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-[11px] font-bold text-primary-600 dark:text-primary-400">5</span>
            Gestionar Personas
          </h3>
          <div class="ml-8 space-y-2">
            <p>Podés cargar propietarios e inquilinos desde la sección <strong>Personas</strong>.</p>
            <p><strong>Crear:</strong> Completá nombre, CUIT, teléfono, email y el tipo (propietario o inquilino).</p>
            <p><strong>Editar:</strong> Hacé clic en el ícono de lápiz para actualizar datos.</p>
            <p><strong>Filtrar:</strong> Usá la barra de búsqueda para encontrar personas por nombre.</p>
          </div>
        </section>

        <!-- Contratos -->
        <section>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-2 flex items-center gap-2">
            <span class="w-6 h-6 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-[11px] font-bold text-primary-600 dark:text-primary-400">6</span>
            Contratos de Alquiler
          </h3>
          <div class="ml-8 space-y-2">
            <p><strong>Crear:</strong> Elegí el inmueble, el inquilino, las fechas de inicio y fin, y la modalidad de pago.</p>
            <p><strong>Editar:</strong> Modificá fechas, monto, frecuencia u otros datos del contrato.</p>
            <p>Los contratos se listan con su estado actual (activo/vencido).</p>
          </div>
        </section>

        <!-- Cobros -->
        <section>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-2 flex items-center gap-2">
            <span class="w-6 h-6 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-[11px] font-bold text-primary-600 dark:text-primary-400">7</span>
            Cobros
          </h3>
          <div class="ml-8 space-y-2">
            <p>En esta sección ves el historial de todos los cobros registrados.</p>
            <p><strong>Filtrar:</strong> Podés filtrar por propietario, inmueble o rango de fechas.</p>
            <p><strong>Eliminar:</strong> Solo los administradores pueden eliminar cobros.</p>
            <p>Los cobros se ordenan automáticamente del más reciente al más antiguo.</p>
          </div>
        </section>

        <!-- Informes -->
        <section>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-2 flex items-center gap-2">
            <span class="w-6 h-6 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-[11px] font-bold text-primary-600 dark:text-primary-400">8</span>
            Informes de Propietarios
          </h3>
          <div class="ml-8 space-y-2">
            <p>Generá informes de lo que le corresponde a cada propietario, descontando el costo de administración.</p>
            <p><strong>Vista general:</strong> Resumen por propietario con desglose de cobros.</p>
            <p><strong>Vista pivot:</strong> Seleccioná un inmueble para ver la tabla mensual con montos por propietario.</p>
            <p><strong>Filtros:</strong> Podés filtrar por fechas, inmueble o propietario específico.</p>
            <p>Los porcentajes de administración se configuran en <strong>Configuración</strong> (solo admin).</p>
          </div>
        </section>

        <!-- Permisos por Rol -->
        <section>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-2 flex items-center gap-2">
            <span class="w-6 h-6 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-[11px] font-bold text-primary-600 dark:text-primary-400">9</span>
            Permisos por Rol
          </h3>
          <div class="ml-8 space-y-3">
            <div class="bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-3">
              <p class="font-semibold text-gray-900 dark:text-gray-100 mb-1">Empleado</p>
              <ul class="space-y-1 list-disc list-inside text-gray-600 dark:text-gray-400 text-xs">
                <li>Ver inmuebles urbanos y rurales</li>
                <li>Ver personas (propietarios e inquilinos)</li>
                <li>Ver contratos de alquiler</li>
                <li>Ver historial de cobros</li>
                <li>Ver informes de propietarios</li>
                <li>Cambiar su propia contraseña</li>
              </ul>
            </div>
            <div class="bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-3">
              <p class="font-semibold text-gray-900 dark:text-gray-100 mb-1">Administrador</p>
              <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">Todo lo del empleado, más:</p>
              <ul class="space-y-1 list-disc list-inside text-gray-600 dark:text-gray-400 text-xs">
                <li>Crear, editar y eliminar inmuebles</li>
                <li>Crear, editar y eliminar personas</li>
                <li>Crear, editar y eliminar contratos</li>
                <li>Registrar, editar y eliminar cobros</li>
                <li>Generar contratos desde la tabla de inmuebles</li>
                <li>Registrar cobros directo desde la tabla de inmuebles</li>
                <li>Ver propietarios y historial desde la tabla de inmuebles</li>
                <li>Gestionar usuarios (crear, editar, desactivar)</li>
                <li>Configurar la aplicación (nombre, costos de administración)</li>
              </ul>
            </div>
          </div>
        </section>

        <!-- Tips -->
        <section>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-2 flex items-center gap-2">
            <span class="w-6 h-6 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center text-[11px] font-bold text-amber-600 dark:text-amber-400">★</span>
            Tips
          </h3>
          <ul class="ml-8 space-y-1.5 list-disc list-inside text-gray-600 dark:text-gray-400">
            <li>Cambiá entre modo claro y oscuro con el ícono de sol/luna en la barra superior.</li>
            <li>Si tu sesión expira por inactividad (30 min), vas a necesitar volver a iniciar sesión.</li>
            <li>Las fechas en las tablas se muestran en formato AA/mm/dd para que se puedan ordenar correctamente.</li>
            <li>Las notificaciones de cobros aparecen arriba a la derecha para los administradores.</li>
            <li>Cambiá tu contraseña en cualquier momento desde el ícono &#128273; en la barra superior.</li>
          </ul>
        </section>

      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-gray-100 dark:border-gray-800 flex justify-end">
        <button on:click={close} class="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors cursor-pointer">
          Entendido
        </button>
      </div>
    </div>
  </div>
{/if}
