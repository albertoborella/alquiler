<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { auth } from '$lib/stores/auth';
  import { api } from '$lib/api';
  import type { InmuebleDashboard, CobroPublic, Persona } from '$lib/api';
  import NuevoInmuebleModal from '$lib/components/NuevoInmuebleModal.svelte';
  import EditarInmuebleModal from '$lib/components/EditarInmuebleModal.svelte';

  let inmuebles: InmuebleDashboard[] = [];
  let loading = true;
  let error = '';
  let filterEstado = '';

  // ── Delete modal ──
  let showDeleteConfirm = false;
  let deleteTarget: InmuebleDashboard | null = null;
  let deleting = false;

  // ── Cobro modal ──
  let showCobroModal = false;
  let cobroTarget: InmuebleDashboard | null = null;
  let cobroForm = {
    fecha_cobro: new Date().toISOString().split('T')[0],
    precio_kilo: '',
    observaciones: '',
  };
  let cobroSubmitting = false;
  let cobroSuccess = '';
  let cobroError = '';

  // Cálculo automático: kilos del contrato × precio/kilo
  $: cobroKilos = cobroTarget?.contrato?.kilos ?? 0;
  $: cobroMontoCalculado = cobroKilos * (parseFloat(cobroForm.precio_kilo) || 0);
  // Costo de administración
  $: cobroCostoAdmin = cobroMontoCalculado * (cobroPorcentajeAdmin / 100);
  $: cobroMontoPropietario = cobroMontoCalculado - cobroCostoAdmin;
  let cobroPorcentajeAdmin = 3;

  // ── Propietarios modal ──
  let showPropietariosModal = false;
  let propietariosTarget: InmuebleDashboard | null = null;

  // ── Historial modal ──
  let showHistorialModal = false;
  let historialTarget: InmuebleDashboard | null = null;
  let historialCobros: CobroPublic[] = [];
  let historialLoading = false;

  // ── Contrato modal ──
  let showContratoModal = false;
  let contratoTarget: InmuebleDashboard | null = null;
  let contratoForm = {
    fecha_inicio: new Date().toISOString().split('T')[0],
    fecha_fin: '',
    duracion: '1',
    inquilino_id: '',
    monto_base: '',
    moneda: 'ARS',
    periodo_indexacion: '',
    indice: '',
    tipo_producto: '',
    kilos: '',
    precio_kilo: '',
  };
  let contratoSubmitting = false;
  let contratoSuccess = '';
  let contratoError = '';
  let inquilinos: Persona[] = [];
  let inquilinosLoading = false;

  // ── Nuevo Inmueble modal ──
  let showNuevoInmuebleModal = false;

  // ── Editar Inmueble modal ──
  let showEditarInmuebleModal = false;
  let editarInmuebleTarget: InmuebleDashboard | null = null;

  // ── Edit Contrato modal ──
  let showEditContratoModal = false;
  let editContratoTarget: InmuebleDashboard | null = null;
  let editContratoForm = {
    fecha_inicio: '',
    fecha_fin: '',
    duracion: '',
    fecha_maxima_pago: '',
    modalidad_pago: '',
    frecuencia: '',
    monto_base: '',
    moneda: '',
    indice: '',
    periodo_indexacion: '',
    tipo_producto: '',
    kilos: '',
    precio_kilo: '',
    activo: true,
  };
  let editContratoSubmitting = false;
  let editContratoSuccess = '';
  let editContratoError = '';

  $: isAdmin = $auth.user?.role === 'admin';
  $: isRural = true;
  $: contratoModalidad = 'producto_agropecuario';

  function calcularFechaFin(fechaInicio: string, duracion: string): string {
    if (!fechaInicio || !duracion || duracion === 'otros') return contratoForm.fecha_fin;
    const inicio = new Date(fechaInicio + 'T00:00:00');
    const anios = parseInt(duracion);
    inicio.setFullYear(inicio.getFullYear() + anios);
    return inicio.toISOString().split('T')[0];
  }

  $: if (contratoForm.duracion && contratoForm.duracion !== 'otros' && contratoForm.fecha_inicio) {
    contratoForm.fecha_fin = calcularFechaFin(contratoForm.fecha_inicio, contratoForm.duracion);
  }

  function calcularFechaFinEdit(fechaInicio: string, duracion: string): string {
    if (!fechaInicio || !duracion || duracion === 'otros') return editContratoForm.fecha_fin;
    const inicio = new Date(fechaInicio + 'T00:00:00');
    const anios = parseInt(duracion);
    inicio.setFullYear(inicio.getFullYear() + anios);
    return inicio.toISOString().split('T')[0];
  }

  $: if (editContratoForm.duracion && editContratoForm.duracion !== 'otros' && editContratoForm.fecha_inicio) {
    editContratoForm.fecha_fin = calcularFechaFinEdit(editContratoForm.fecha_inicio, editContratoForm.duracion);
  }

  onMount(() => {
    if (!$auth.token) {
      goto('/login');
      return;
    }
    loadInmuebles();
  });

  async function loadInmuebles() {
    if (!$auth.token) return;
    loading = true;
    error = '';
    try {
      inmuebles = await api.getDashboardInmuebles($auth.token, {
        estado: filterEstado || undefined,
        categoria: 'rural',
      });
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error al cargar inmuebles';
    } finally {
      loading = false;
    }
  }

  function handleFilterChange() {
    loadInmuebles();
  }

  // ── Delete ──
  function confirmDelete(inm: InmuebleDashboard) {
    deleteTarget = inm;
    showDeleteConfirm = true;
  }

  function cancelDelete() {
    deleteTarget = null;
    showDeleteConfirm = false;
  }

  async function executeDelete() {
    if (!deleteTarget || !$auth.token) return;
    deleting = true;
    try {
      await api.deleteInmueble($auth.token, deleteTarget.id);
      inmuebles = inmuebles.filter((i) => i.id !== deleteTarget!.id);
      showDeleteConfirm = false;
      deleteTarget = null;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error al eliminar inmueble';
      showDeleteConfirm = false;
    } finally {
      deleting = false;
    }
  }

  // ── Cobro ──
  async function openCobro(inm: InmuebleDashboard) {
    if (!inm.contrato) return;
    cobroTarget = inm;
    cobroForm = {
      fecha_cobro: new Date().toISOString().split('T')[0],
      precio_kilo: '',
      observaciones: '',
    };
    // Traer porcentaje de admin desde configuración
    try {
      const configRes = await fetch('http://localhost:8000/api/configuracion', { cache: 'no-store' });
      if (configRes.ok) {
        const config = await configRes.json();
        cobroPorcentajeAdmin = parseFloat(config.costo_admin_rural) || 3;
      }
    } catch {
      cobroPorcentajeAdmin = 3;
    }
    cobroSuccess = '';
    cobroError = '';
    showCobroModal = true;
  }

  function cancelCobro() {
    showCobroModal = false;
    cobroTarget = null;
  }

  async function executeCobro() {
    if (!cobroTarget?.contrato || !$auth.token) return;
    cobroSubmitting = true;
    cobroError = '';
    cobroSuccess = '';
    try {
      const precioKilo = parseFloat(cobroForm.precio_kilo) || 0;
      const parts = [`${cobroKilos} kg × $${precioKilo}/kg`];
      if (cobroCostoAdmin > 0) parts.push(`Admin: ${cobroPorcentajeAdmin}% ($${cobroCostoAdmin.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })})`);
      const obs = [
        cobroForm.observaciones || '',
        parts.join(' — '),
      ].filter(Boolean).join(' — ');
      await api.createCobro($auth.token, {
        contrato_id: cobroTarget.contrato.id,
        fecha_cobro: cobroForm.fecha_cobro,
        monto: cobroMontoCalculado,
        observaciones: obs || undefined,
      });
      cobroSuccess = 'Cobro registrado exitosamente';
      setTimeout(() => {
        showCobroModal = false;
        cobroTarget = null;
      }, 1500);
    } catch (err) {
      cobroError = err instanceof Error ? err.message : 'Error al registrar cobro';
    } finally {
      cobroSubmitting = false;
    }
  }

  // ── Propietarios ──
  function openPropietarios(inm: InmuebleDashboard) {
    propietariosTarget = inm;
    showPropietariosModal = true;
  }

  function closePropietarios() {
    showPropietariosModal = false;
    propietariosTarget = null;
  }

  // ── Edit Contrato ──
  function openEditContrato(inm: InmuebleDashboard) {
    if (!inm.contrato) return;
    editContratoTarget = inm;
    const c = inm.contrato;
    let duracionInferida = '';
    if (c.fecha_inicio && c.fecha_fin) {
      const inicio = new Date(c.fecha_inicio + 'T00:00:00');
      const fin = new Date(c.fecha_fin + 'T00:00:00');
      const diffYears = Math.round((fin.getTime() - inicio.getTime()) / (365.25 * 24 * 60 * 60 * 1000));
      if (diffYears === 1) duracionInferida = '1';
      else if (diffYears === 2) duracionInferida = '2';
      else if (diffYears === 3) duracionInferida = '3';
      else duracionInferida = 'otros';
    }
    editContratoForm = {
      fecha_inicio: c.fecha_inicio,
      fecha_fin: c.fecha_fin,
      duracion: duracionInferida,
      fecha_maxima_pago: String(c.fecha_maxima_pago ?? 10),
      modalidad_pago: c.modalidad_pago ?? 'producto_agropecuario',
      frecuencia: c.frecuencia ?? 'mensual',
      monto_base: c.monto_base != null ? String(c.monto_base) : '',
      moneda: c.moneda || 'ARS',
      indice: c.indice ?? '',
      periodo_indexacion: c.periodo_indexacion ?? '',
      tipo_producto: c.tipo_producto ?? '',
      kilos: c.kilos != null ? String(c.kilos) : '',
      precio_kilo: c.precio_kilo != null ? String(c.precio_kilo) : '',
      activo: c.activo ?? true,
    };
    editContratoSuccess = '';
    editContratoError = '';
    showEditContratoModal = true;
  }

  async function submitEditContrato() {
    if (!$auth.token || !editContratoTarget?.contrato) return;
    editContratoSubmitting = true;
    editContratoError = '';
    editContratoSuccess = '';
    try {
      await api.updateContrato($auth.token, editContratoTarget.contrato.id, {
        fecha_inicio: editContratoForm.fecha_inicio || undefined,
        fecha_fin: editContratoForm.fecha_fin || undefined,
        fecha_maxima_pago: editContratoForm.fecha_maxima_pago ? parseInt(editContratoForm.fecha_maxima_pago) : undefined,
        modalidad_pago: editContratoForm.modalidad_pago || undefined,
        frecuencia: editContratoForm.frecuencia || undefined,
        monto_base: editContratoForm.monto_base ? parseFloat(editContratoForm.monto_base) : undefined,
        moneda: editContratoForm.moneda || undefined,
        indice: editContratoForm.indice || undefined,
        periodo_indexacion: editContratoForm.periodo_indexacion || undefined,
        tipo_producto: editContratoForm.tipo_producto || undefined,
        kilos: editContratoForm.kilos ? parseFloat(editContratoForm.kilos) : undefined,
        precio_kilo: editContratoForm.precio_kilo ? parseFloat(editContratoForm.precio_kilo) : undefined,
        activo: editContratoForm.activo,
      });
      editContratoSuccess = 'Contrato actualizado';
      await loadInmuebles();
      setTimeout(() => { showEditContratoModal = false; }, 1200);
    } catch (err) {
      editContratoError = err instanceof Error ? err.message : 'Error al actualizar contrato';
    } finally {
      editContratoSubmitting = false;
    }
  }

  // ── Historial de cobros ──
  async function openHistorial(inm: InmuebleDashboard) {
    if (!inm.contrato) return;
    historialTarget = inm;
    historialCobros = [];
    historialLoading = true;
    showHistorialModal = true;
    try {
      if ($auth.token) {
        historialCobros = await api.getCobrosByContrato($auth.token, inm.contrato.id);
      }
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error al cargar historial';
    } finally {
      historialLoading = false;
    }
  }

  function closeHistorial() {
    showHistorialModal = false;
    historialTarget = null;
    historialCobros = [];
  }

  // ── Contrato ──
  async function openContrato(inm: InmuebleDashboard) {
    contratoTarget = inm;
    contratoForm = {
      fecha_inicio: new Date().toISOString().split('T')[0],
      fecha_fin: '',
      duracion: '1',
      inquilino_id: '',
      monto_base: '',
      moneda: 'ARS',
      periodo_indexacion: '',
      indice: '',
      tipo_producto: '',
      kilos: '',
      precio_kilo: '',
    };
    contratoSuccess = '';
    contratoError = '';
    showContratoModal = true;

    // Load inquilinos for the select
    if ($auth.token && inquilinos.length === 0) {
      inquilinosLoading = true;
      try {
        inquilinos = await api.getInquilinos($auth.token);
      } catch (err) {
        console.error('Error loading inquilinos:', err);
      } finally {
        inquilinosLoading = false;
      }
    }
  }

  function cancelContrato() {
    showContratoModal = false;
    contratoTarget = null;
  }

  async function executeContrato() {
    if (!contratoTarget || !$auth.token) return;
    if (!contratoForm.fecha_fin) {
      contratoError = 'Seleccioná la duración del contrato';
      return;
    }
    contratoSubmitting = true;
    contratoError = '';
    contratoSuccess = '';
    try {
      await api.createContrato($auth.token, {
        inmueble_id: contratoTarget.id,
        inquilino_id: contratoForm.inquilino_id,
        fecha_inicio: contratoForm.fecha_inicio,
        fecha_fin: contratoForm.fecha_fin,
        modalidad_pago: contratoModalidad,
        tipo_producto: contratoForm.tipo_producto || undefined,
        kilos: contratoForm.kilos ? parseFloat(contratoForm.kilos) : undefined,
        precio_kilo: contratoForm.precio_kilo ? parseFloat(contratoForm.precio_kilo) : undefined,
      });
      contratoSuccess = 'Contrato creado exitosamente';
      await loadInmuebles();
      setTimeout(() => {
        showContratoModal = false;
        contratoTarget = null;
      }, 1500);
    } catch (err) {
      contratoError = err instanceof Error ? err.message : 'Error al crear contrato';
    } finally {
      contratoSubmitting = false;
    }
  }

  // ── Nuevo Inmueble ──
  function openNuevoInmueble() {
    showNuevoInmuebleModal = true;
  }

  function cerrarNuevoInmueble() {
    showNuevoInmuebleModal = false;
  }

  async function handleInmuebleCreated() {
    await loadInmuebles();
  }

  // ── Helpers ──
  function estadoBadgeClass(estado: string): string {
    return estado === 'alquilado'
      ? 'bg-primary-100 dark:bg-primary-900/40 text-primary-800 dark:text-primary-200'
      : 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200';
  }

  function estadoLabel(estado: string): string {
    return estado === 'alquilado' ? 'Alquilado' : 'Disponible';
  }

  function morosoBadgeClass(moroso: boolean): string {
    return moroso
      ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200'
      : 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200';
  }

  function formatSuperficie(value: number | null): string {
    if (value === null) return '-';
    return `${value.toLocaleString('es-AR')} ha`;
  }

  function formatCurrency(amount: number | null, currency: string | null): string {
    if (amount === null) return '-';
    const sym = currency === 'USD' ? 'US$' : '$';
    return `${sym} ${amount.toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}`;
  }

  function propietariosLabel(inm: InmuebleDashboard): string {
    return inm.propietarios
      .map((p) => `${p.nombre} ${p.porcentaje_participacion}%`)
      .join(', ');
  }
</script>

<div class="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 py-6 md:py-8">
  <div class="mb-6 md:mb-8">
    <h1 class="text-xl md:text-2xl font-bold text-gray-900 dark:text-gray-100">Inmuebles rurales</h1>
    <p class="text-gray-500 dark:text-gray-400 mt-1">Gestión de propiedades rurales</p>
  </div>

  <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800">
    <!-- Header bar -->
    <div class="px-4 md:px-6 py-3 border-b border-gray-100 dark:border-gray-800">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div class="flex flex-wrap items-center gap-3">
          <label for="filterEstado" class="text-sm font-medium text-gray-700 dark:text-gray-300">
            Estado:
          </label>
          <select
            id="filterEstado"
            bind:value={filterEstado}
            on:change={handleFilterChange}
            class="px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="">Todos</option>
            <option value="alquilado">Alquilado</option>
            <option value="disponible">Disponible</option>
          </select>
        </div>

        {#if isAdmin}
          <button
            on:click={openNuevoInmueble}
            class="inline-flex items-center gap-2 px-3.5 py-1.5 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 active:bg-primary-800 rounded-lg shadow-sm transition-colors cursor-pointer"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Nuevo inmueble
          </button>
        {/if}
      </div>
    </div>

    {#if error}
      <div class="px-4 md:px-6 py-3 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 text-sm border-b border-red-100 dark:border-red-900/30">
        {error}
      </div>
    {/if}

    {#if loading}
      <div class="p-6 space-y-3">
        {#each Array(5) as _}
          <div class="flex gap-4 animate-pulse">
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/5"></div>
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/6"></div>
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/8"></div>
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/8"></div>
          </div>
        {/each}
      </div>
    {:else if inmuebles.length === 0}
      <div class="px-6 py-16 text-center">
        <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg px-6 py-5 max-w-md mx-auto mb-6">
          <div class="flex items-center gap-3">
            <svg class="w-5 h-5 text-amber-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <p class="text-sm text-amber-700 dark:text-amber-300 font-medium">No hay inmuebles rurales cargados</p>
          </div>
          <p class="text-xs text-amber-600 dark:text-amber-400 mt-2">
            Cargá los primeros inmuebles rurales para empezar a gestionarlos.
          </p>
        </div>
        <svg class="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
        <p class="text-gray-500 dark:text-gray-400 text-sm">No se encontraron inmuebles rurales</p>
      </div>
    {:else}
      <div class="overflow-x-auto -mx-4 md:mx-0">
        <table class="w-full min-w-[640px]">
          <thead>
            <tr class="text-left text-[11px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider border-b border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-800/50">
              <th class="px-3 md:px-4 py-1">Dirección</th>
              <th class="px-3 md:px-4 py-1 hidden sm:table-cell">Propietario(s)</th>
              <th class="px-3 md:px-4 py-1">Estado</th>
              <th class="px-3 md:px-4 py-1">Superficie (ha)</th>
              <th class="px-3 md:px-4 py-1">Moroso</th>
              <th class="px-3 md:px-4 py-1 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
            {#each inmuebles as inm (inm.id)}
              <tr class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                <td class="px-3 md:px-4 py-1">
                  <div class="text-xs text-gray-900 dark:text-gray-100">{inm.direccion}</div>
                </td>
                <td class="px-3 md:px-4 py-1 text-xs text-gray-600 dark:text-gray-400 hidden sm:table-cell">
                  {#if inm.propietarios.length > 0}
                    {propietariosLabel(inm)}
                  {:else}
                    <span class="text-gray-400">-</span>
                  {/if}
                </td>
                <td class="px-3 md:px-4 py-1">
                  <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium {estadoBadgeClass(inm.estado)}">
                    {estadoLabel(inm.estado)}
                  </span>
                </td>
                <td class="px-3 md:px-4 py-1 text-xs text-gray-600 dark:text-gray-400">
                  {formatSuperficie(inm.superficie)}
                </td>
                <td class="px-3 md:px-4 py-1">
                  <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium {morosoBadgeClass(inm.moroso)}">
                    {inm.moroso ? 'Sí' : 'No'}
                  </span>
                </td>
                <td class="px-3 md:px-4 py-1 text-right">
                  <div class="flex items-center justify-end gap-0.5">
                    <!-- Cobrar (todos los usuarios) -->
                    {#if inm.contrato}
                      <button
                        on:click={() => openCobro(inm)}
                        class="p-1.5 rounded-md text-gray-400 hover:text-emerald-600 hover:bg-emerald-50 dark:hover:bg-emerald-900/20 transition-colors cursor-pointer"
                        title="Registrar cobro"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                        </svg>
                      </button>
                    {/if}

                    <!-- Historial de cobros (todos los usuarios) -->
                    {#if inm.contrato}
                      <button
                        on:click={() => openHistorial(inm)}
                        class="p-1.5 rounded-md text-gray-400 hover:text-amber-600 hover:bg-amber-50 dark:hover:bg-amber-900/20 transition-colors cursor-pointer"
                        title="Historial de cobros"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </button>
                    {/if}

                    {#if isAdmin}
                      <!-- Ver propietarios -->
                      {#if inm.propietarios.length > 0}
                        <button
                          on:click={() => openPropietarios(inm)}
                          class="p-1.5 rounded-md text-gray-400 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors cursor-pointer"
                          title="Ver propietarios"
                        >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
                          </svg>
                        </button>
                      {/if}

                      <!-- Generar contrato (solo si esta disponible) -->
                      {#if inm.estado === 'disponible'}
                        <button
                          on:click={() => openContrato(inm)}
                          class="p-1.5 rounded-md text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors cursor-pointer"
                          title="Generar contrato"
                        >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </button>
                      {/if}

                      <!-- Editar contrato -->
                      {#if inm.contrato}
                        <button
                          on:click={() => openEditContrato(inm)}
                          class="p-1.5 rounded-md text-gray-400 hover:text-violet-600 hover:bg-violet-50 dark:hover:bg-violet-900/20 transition-colors cursor-pointer"
                          title="Editar contrato"
                        >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </button>
                      {/if}

                      <!-- Editar inmueble -->
                      <button
                        on:click={() => { editarInmuebleTarget = inm; showEditarInmuebleModal = true; }}
                        class="p-1.5 rounded-md text-gray-400 hover:text-primary-600 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors cursor-pointer"
                        title="Editar inmueble"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>

                      <!-- Eliminar inmueble -->
                      <button
                        on:click={() => confirmDelete(inm)}
                        class="p-1.5 rounded-md text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors cursor-pointer"
                        title="Eliminar inmueble"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    {/if}
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
</div>

<!-- ═══════════════════════════════════════════════════════════ -->
<!-- DELETE CONFIRMATION MODAL                                  -->
<!-- ═══════════════════════════════════════════════════════════ -->
{#if showDeleteConfirm && deleteTarget}
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="absolute inset-0 bg-black/50" on:click={cancelDelete} role="presentation"></div>
    <div class="relative bg-white dark:bg-gray-900 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 w-full max-w-md mx-4 p-6">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
          <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <div>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">Eliminar inmueble</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">Esta acción no se puede deshacer</p>
        </div>
      </div>
      <p class="text-sm text-gray-700 dark:text-gray-300 mb-6">
        ¿Seguro que querés eliminar el inmueble en <strong class="font-medium">{deleteTarget.direccion}</strong>?
      </p>
      <div class="flex justify-end gap-3">
        <button on:click={cancelDelete} disabled={deleting}
          class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors cursor-pointer disabled:opacity-50">
          Cancelar
        </button>
        <button on:click={executeDelete} disabled={deleting}
          class="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 disabled:bg-red-400 rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed">
          {deleting ? 'Eliminando...' : 'Eliminar'}
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- ═══════════════════════════════════════════════════════════ -->
<!-- COBRO MODAL                                               -->
<!-- ═══════════════════════════════════════════════════════════ -->
{#if showCobroModal && cobroTarget}
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="absolute inset-0 bg-black/50" on:click={cancelCobro} role="presentation"></div>
    <div class="relative bg-white dark:bg-gray-900 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 w-full max-w-md mx-4 p-6">
      <div class="flex items-center gap-3 mb-5">
        <div class="w-10 h-10 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
          <svg class="w-5 h-5 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
        </div>
        <div>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">Registrar cobro</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">{cobroTarget.direccion}</p>
          {#if cobroTarget.propietarios && cobroTarget.propietarios.length > 0}
            <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
              Propietario{cobroTarget.propietarios.length > 1 ? 's' : ''}:
              {cobroTarget.propietarios.map((p) => p.nombre).join(', ')}
            </p>
          {/if}
        </div>
      </div>

      {#if cobroSuccess}
        <div class="bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-300 text-sm rounded-lg px-4 py-3 border border-emerald-100 dark:border-emerald-800 mb-4">
          {cobroSuccess}
        </div>
      {/if}

      {#if cobroError}
        <div class="bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 text-sm rounded-lg px-4 py-3 border border-red-100 dark:border-red-800 mb-4">
          {cobroError}
        </div>
      {/if}

      <form on:submit|preventDefault={executeCobro} class="space-y-4">
        <!-- Kilos del contrato (solo lectura) -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Kilos (del contrato)</label>
          <div class="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 text-sm text-gray-500 dark:text-gray-400">
            {cobroKilos > 0 ? `${cobroKilos} kg` : 'No configurado en contrato'}
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="cobro-fecha" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Fecha de cobro *</label>
            <input id="cobro-fecha" type="date" bind:value={cobroForm.fecha_cobro} required
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
          <div>
            <label for="cobro-precio-kilo" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Precio por kilo *</label>
            <input id="cobro-precio-kilo" type="number" step="0.01" min="0" bind:value={cobroForm.precio_kilo} required placeholder="0.00"
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
        </div>

        <!-- Importe calculado -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Importe a cobrar</label>
          <div class="w-full px-3 py-2.5 rounded-lg border border-emerald-300 dark:border-emerald-700 bg-emerald-50 dark:bg-emerald-900/20 text-lg font-semibold text-emerald-700 dark:text-emerald-300">
            {cobroMontoCalculado > 0 ? `$ ${cobroMontoCalculado.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '$ 0,00'}
          </div>
        </div>

        <!-- Desglose costo administración -->
        {#if cobroCostoAdmin > 0}
          <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg px-4 py-3">
            <p class="text-xs font-medium text-amber-700 dark:text-amber-300 mb-1.5">
              Costo de administración ({cobroPorcentajeAdmin}%)
            </p>
            <div class="flex justify-between text-sm">
              <span class="text-amber-600 dark:text-amber-400">Monto bruto:</span>
              <span class="text-amber-700 dark:text-amber-300 font-medium">$ {cobroMontoCalculado.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-amber-600 dark:text-amber-400">Desc. admin:</span>
              <span class="text-amber-700 dark:text-amber-300 font-medium">- $ {cobroCostoAdmin.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
            </div>
            <div class="border-t border-amber-300 dark:border-amber-700 mt-1.5 pt-1.5 flex justify-between text-sm">
              <span class="text-amber-700 dark:text-amber-300 font-semibold">Neto propietario:</span>
              <span class="text-amber-800 dark:text-amber-200 font-bold">$ {cobroMontoPropietario.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
            </div>
          </div>
        {/if}

        <div>
          <label for="cobro-obs" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Observaciones</label>
          <textarea id="cobro-obs" bind:value={cobroForm.observaciones} rows="2" placeholder="Notas opcionales..."
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"></textarea>
        </div>

        <div class="flex justify-end gap-3 pt-2">
          <button type="button" on:click={cancelCobro} disabled={cobroSubmitting}
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors cursor-pointer disabled:opacity-50">
            Cancelar
          </button>
          <button type="submit" disabled={cobroSubmitting || !cobroForm.precio_kilo || cobroMontoCalculado <= 0}
            class="px-4 py-2 text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-400 rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed">
            {cobroSubmitting ? 'Registrando...' : 'Registrar cobro'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- ═══════════════════════════════════════════════════════════ -->
<!-- PROPIETARIOS MODAL                                        -->
<!-- ═══════════════════════════════════════════════════════════ -->
{#if showPropietariosModal && propietariosTarget}
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="absolute inset-0 bg-black/50" on:click={closePropietarios} role="presentation"></div>
    <div class="relative bg-white dark:bg-gray-900 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 w-full max-w-md mx-4 p-6">
      <div class="flex items-center gap-3 mb-5">
        <div class="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
          <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <div>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">Propietarios</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">{propietariosTarget.direccion}</p>
        </div>
      </div>

      <div class="space-y-3">
        {#each propietariosTarget.propietarios as prop}
          <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div>
              <p class="text-sm font-medium text-gray-900 dark:text-gray-100">{prop.nombre}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400">DNI/CUIT: {prop.dni_cuit}</p>
            </div>
            <span class="text-xs font-medium text-primary-700 dark:text-primary-300 bg-primary-100 dark:bg-primary-900/40 px-2 py-0.5 rounded-full">
              {prop.porcentaje_participacion}%
            </span>
          </div>
        {/each}
      </div>

      <div class="flex justify-end mt-5">
        <button on:click={closePropietarios}
          class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors cursor-pointer">
          Cerrar
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- ═══════════════════════════════════════════════════════════ -->
<!-- HISTORIAL DE COBROS MODAL                                 -->
<!-- ═══════════════════════════════════════════════════════════ -->
{#if showHistorialModal && historialTarget}
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="absolute inset-0 bg-black/50" on:click={closeHistorial} role="presentation"></div>
    <div class="relative bg-white dark:bg-gray-900 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 w-full max-w-lg mx-4 p-6">
      <div class="flex items-center gap-3 mb-5">
        <div class="w-10 h-10 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
          <svg class="w-5 h-5 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">Historial de cobros</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">{historialTarget.direccion}</p>
        </div>
      </div>

      {#if historialLoading}
        <div class="space-y-3">
          {#each Array(3) as _}
            <div class="h-12 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse"></div>
          {/each}
        </div>
      {:else if historialCobros.length === 0}
        <div class="text-center py-8">
          <svg class="w-10 h-10 text-gray-300 dark:text-gray-600 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <p class="text-sm text-gray-500 dark:text-gray-400">No hay cobros registrados para este contrato</p>
        </div>
      {:else}
        <div class="overflow-x-auto max-h-80 overflow-y-auto">
          <table class="w-full">
            <thead>
              <tr class="text-left text-[11px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider border-b border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-800/50">
                <th class="px-3 py-2">Fecha</th>
                <th class="px-3 py-2 text-right">Monto</th>
                <th class="px-3 py-2">Moneda</th>
                <th class="px-3 py-2">Obs.</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
              {#each historialCobros as cobro (cobro.id)}
                <tr class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                  <td class="px-3 py-2 text-[13px] text-gray-900 dark:text-gray-100">{cobro.fecha_cobro}</td>
                  <td class="px-3 py-2 text-[13px] text-gray-900 dark:text-gray-100 text-right font-medium">
                    {formatCurrency(cobro.monto, cobro.moneda_original)}
                  </td>
                  <td class="px-3 py-2 text-[13px] text-gray-600 dark:text-gray-400">{cobro.moneda_original ?? 'ARS'}</td>
                  <td class="px-3 py-2 text-[12px] text-gray-500 dark:text-gray-400 max-w-[120px] truncate">{cobro.observaciones ?? '-'}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}

      <div class="flex justify-end mt-5">
        <button on:click={closeHistorial}
          class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors cursor-pointer">
          Cerrar
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- ═══════════════════════════════════════════════════════════ -->
<!-- GENERAR CONTRATO MODAL (rural)                             -->
<!-- ═══════════════════════════════════════════════════════════ -->
{#if showContratoModal && contratoTarget}
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="absolute inset-0 bg-black/50" on:click={cancelContrato} role="presentation"></div>
    <div class="relative bg-white dark:bg-gray-900 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 w-full max-w-lg mx-4 p-6">
      <div class="flex items-center gap-3 mb-5">
        <div class="w-10 h-10 rounded-full bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
          <svg class="w-5 h-5 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">Generar contrato</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">{contratoTarget.direccion}</p>
        </div>
      </div>

      {#if contratoSuccess}
        <div class="bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-300 text-sm rounded-lg px-4 py-3 border border-emerald-100 dark:border-emerald-800 mb-4">
          {contratoSuccess}
        </div>
      {/if}

      {#if contratoError}
        <div class="bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 text-sm rounded-lg px-4 py-3 border border-red-100 dark:border-red-800 mb-4">
          {contratoError}
        </div>
      {/if}

      <form on:submit|preventDefault={executeContrato} class="space-y-4">
        <!-- Inquilino -->
        <div>
          <label for="contrato-inquilino" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Inquilino *</label>
          <select id="contrato-inquilino" bind:value={contratoForm.inquilino_id} required
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent">
            <option value="">Seleccionar inquilino...</option>
            {#each inquilinos as inq}
              <option value={inq.id}>{inq.nombre} (CUIT: {inq.cuit})</option>
            {/each}
          </select>
          {#if inquilinosLoading}
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Cargando inquilinos...</p>
          {/if}
        </div>

        <!-- Fechas -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="contrato-fecha-inicio" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Fecha de inicio *</label>
            <input id="contrato-fecha-inicio" type="date" bind:value={contratoForm.fecha_inicio} required
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
          <div>
            <label for="contrato-duracion" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Duración *</label>
            <select id="contrato-duracion" bind:value={contratoForm.duracion}
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent">
              <option value="1">1 año</option>
              <option value="2">2 años</option>
              <option value="3">3 años</option>
              <option value="otros">Otros</option>
            </select>
          </div>
          {#if contratoForm.duracion === 'otros'}
          <div>
            <label for="contrato-fecha-fin" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Fecha de finalización *</label>
            <input id="contrato-fecha-fin" type="date" bind:value={contratoForm.fecha_fin} required
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
          {/if}
        </div>

        <!-- Campos rurales -->
        <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
          <p class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">Datos del alquiler rural</p>
          <div>
            <label for="contrato-tipo-producto" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Tipo de producto *</label>
            <select id="contrato-tipo-producto" bind:value={contratoForm.tipo_producto} required
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent">
              <option value="">Seleccionar producto...</option>
              <option value="soja">Soja</option>
              <option value="trigo">Trigo</option>
              <option value="maiz">Maiz</option>
              <option value="girasol">Girasol</option>
              <option value="otro">Otro</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-4 mt-4">
            <div>
              <label for="contrato-kilos" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Kilos *</label>
              <input id="contrato-kilos" type="number" step="0.01" min="0" bind:value={contratoForm.kilos} required placeholder="0.00"
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
            </div>
            <div>
              <label for="contrato-precio-kilo" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Precio por kilo *</label>
              <input id="contrato-precio-kilo" type="number" step="0.01" min="0" bind:value={contratoForm.precio_kilo} required placeholder="0.00"
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-3 pt-2">
          <button type="button" on:click={cancelContrato} disabled={contratoSubmitting}
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors cursor-pointer disabled:opacity-50">
            Cancelar
          </button>
          <button type="submit" disabled={contratoSubmitting || !contratoForm.inquilino_id || !contratoForm.fecha_fin}
            class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed">
            {contratoSubmitting ? 'Creando...' : 'Crear contrato'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- ═══ Edit Contrato Modal ═══ -->
{#if showEditContratoModal && editContratoTarget}
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="absolute inset-0 bg-black/50" on:click={() => { showEditContratoModal = false; }} role="presentation"></div>
    <div class="relative bg-white dark:bg-gray-900 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 w-full max-w-2xl mx-4 p-6 max-h-[90vh] overflow-y-auto">
      <div class="flex items-center gap-3 mb-5">
        <div class="w-10 h-10 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
          <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </div>
        <div>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">Editar contrato</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            {editContratoTarget.direccion} — {editContratoTarget.inquilino?.nombre || ''}
          </p>
        </div>
      </div>

      {#if editContratoError}
        <div class="bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 text-sm rounded-lg px-4 py-3 border border-red-100 dark:border-red-800 mb-4">{editContratoError}</div>
      {/if}
      {#if editContratoSuccess}
        <div class="bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-300 text-sm rounded-lg px-4 py-3 border border-emerald-100 dark:border-emerald-800 mb-4">{editContratoSuccess}</div>
      {/if}

      <form on:submit|preventDefault={submitEditContrato} class="space-y-4">
        <div class="grid grid-cols-3 gap-4">
          <div>
            <label for="edc-fecha-inicio" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Fecha inicio *</label>
            <input id="edc-fecha-inicio" type="date" bind:value={editContratoForm.fecha_inicio} required
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
          <div>
            <label for="edc-duracion" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Duración</label>
            <select id="edc-duracion" bind:value={editContratoForm.duracion}
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent">
              <option value="">Seleccionar...</option>
              <option value="1">1 año</option>
              <option value="2">2 años</option>
              <option value="3">3 años</option>
              <option value="otros">Otros</option>
            </select>
          </div>
          <div>
            <label for="edc-fecha-fin" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Fecha fin *</label>
            <input id="edc-fecha-fin" type="date" bind:value={editContratoForm.fecha_fin} required
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
        </div>

        <div class="grid grid-cols-3 gap-4">
          <div>
            <label for="edc-monto" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Monto base</label>
            <input id="edc-monto" type="number" step="0.01" min="0" bind:value={editContratoForm.monto_base} placeholder="0.00"
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
          <div>
            <label for="edc-moneda" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Moneda</label>
            <select id="edc-moneda" bind:value={editContratoForm.moneda}
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent">
              <option value="ARS">ARS</option>
              <option value="USD">USD</option>
            </select>
          </div>
          <div>
            <label for="edc-max-pago" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Días máx. pago</label>
            <input id="edc-max-pago" type="number" min="1" bind:value={editContratoForm.fecha_maxima_pago} placeholder="10"
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="edc-modalidad" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Modalidad</label>
            <select id="edc-modalidad" bind:value={editContratoForm.modalidad_pago}
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent">
              <option value="pesos_indice">Pesos + Índice</option>
              <option value="moneda_extranjera">Moneda extranjera</option>
              <option value="producto_agropecuario">Producto agropecuario</option>
            </select>
          </div>
          <div>
            <label for="edc-frecuencia" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Frecuencia</label>
            <select id="edc-frecuencia" bind:value={editContratoForm.frecuencia}
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent">
              <option value="mensual">Mensual</option>
              <option value="trimestral">Trimestral</option>
              <option value="anual">Anual</option>
              <option value="vencimiento">Vencimiento</option>
            </select>
          </div>
        </div>

        {#if editContratoForm.modalidad_pago === 'pesos_indice'}
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="edc-indice" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Índice</label>
              <input id="edc-indice" type="text" bind:value={editContratoForm.indice} placeholder="Ej: IPC"
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
            </div>
            <div>
              <label for="edc-periodo" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Período indexación</label>
              <input id="edc-periodo" type="text" bind:value={editContratoForm.periodo_indexacion} placeholder="Ej: trimestral"
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
            </div>
          </div>
        {/if}

        {#if editContratoForm.modalidad_pago === 'producto_agropecuario'}
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label for="edc-tipo-prod" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Tipo producto</label>
              <input id="edc-tipo-prod" type="text" bind:value={editContratoForm.tipo_producto}
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
            </div>
            <div>
              <label for="edc-kilos" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Kilos</label>
              <input id="edc-kilos" type="number" step="0.01" min="0" bind:value={editContratoForm.kilos}
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
            </div>
            <div>
              <label for="edc-precio-kilo" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Precio/kilo</label>
              <input id="edc-precio-kilo" type="number" step="0.01" min="0" bind:value={editContratoForm.precio_kilo}
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
            </div>
          </div>
        {/if}

        <div class="flex items-center gap-3">
          <label class="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer">
            <input type="checkbox" bind:checked={editContratoForm.activo}
              class="w-4 h-4 rounded border-gray-300 dark:border-gray-600 text-primary-600 focus:ring-primary-500" />
            Contrato activo
          </label>
        </div>

        <div class="flex justify-end gap-3 pt-2">
          <button type="button" on:click={() => { showEditContratoModal = false; }} disabled={editContratoSubmitting}
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors cursor-pointer disabled:opacity-50">
            Cancelar
          </button>
          <button type="submit" disabled={editContratoSubmitting || !editContratoForm.fecha_inicio || !editContratoForm.fecha_fin}
            class="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:bg-primary-400 rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed">
            {editContratoSubmitting ? 'Guardando...' : 'Guardar cambios'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- ═══════════════════════════════════════════════════════════ -->
<!-- NUEVO INMUEBLE MODAL (shared component)                    -->
<!-- ═══════════════════════════════════════════════════════════ -->
<NuevoInmuebleModal
  open={showNuevoInmuebleModal}
  defaultCategoria="rural"
  onClose={cerrarNuevoInmueble}
  onCreated={handleInmuebleCreated}
/>

<!-- ═══════════════════════════════════════════════════════════ -->
<!-- EDITAR INMUEBLE MODAL                                       -->
<!-- ═══════════════════════════════════════════════════════════ -->
<EditarInmuebleModal
  open={showEditarInmuebleModal}
  inmueble={editarInmuebleTarget}
  onClose={() => { showEditarInmuebleModal = false; editarInmuebleTarget = null; }}
  onUpdated={loadInmuebles}
/>
