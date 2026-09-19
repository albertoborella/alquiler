const API_URL = 'http://localhost:8000/api';

interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

interface User {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
  created_at: string | null;
}

export interface PropietarioDash {
  id: string;
  nombre: string;
  dni_cuit: string;
  porcentaje_participacion: number;
}

export interface ContratoDash {
  id: string;
  inmueble_id: string;
  inquilino_id: string;
  fecha_inicio: string;
  fecha_fin: string;
  fecha_maxima_pago: number;
  modalidad_pago: string;
  frecuencia: string;
  monto_base: number | null;
  moneda: string | null;
  indice: string | null;
  periodo_indexacion: string | null;
  tipo_producto: string | null;
  kilos: number | null;
  precio_kilo: number | null;
  activo: boolean;
}

export interface InquilinoDash {
  id: string;
  nombre: string;
  cuit: string | null;
  iva: string | null;
  telefono: string | null;
  email: string | null;
}

export interface Persona {
  id: string;
  nombre: string;
  cuit: string;
  iva: string | null;
  telefono: string | null;
  email: string | null;
  direccion: string | null;
  rol: string;
  created_at: string | null;
  updated_at: string | null;
}

/** @deprecated Use Persona instead */
export type Propietario = Persona;
/** @deprecated Use Persona instead */
export type InquilinoPublic = Persona;

export interface CopropiedadPublic {
  id: string;
  propietario_id: string;
  inmueble_id: string;
  porcentaje_participacion: number;
  created_at: string | null;
}

export interface PersonaCreateData {
  nombre: string;
  cuit: string;
  iva?: string;
  telefono?: string;
  email?: string;
  direccion?: string;
  rol: string;
}

/** @deprecated Use PersonaCreateData instead */
export type PropietarioCreateData = PersonaCreateData;

export interface InmuebleDashboard {
  id: string;
  direccion: string;
  categoria: string;
  superficie: number | null;
  habitaciones: number | null;
  banos: number | null;
  dormitorios: number | null;
  comodidades: string | null;
  descripcion: string | null;
  estado: string;
  created_at: string | null;
  propietarios: PropietarioDash[];
  contrato: ContratoDash | null;
  inquilino: InquilinoDash | null;
  moroso: boolean;
}

export interface DashboardFilters {
  estado?: string;
  categoria?: string;
  propietario?: string;
  inmueble?: string;
  morosos?: boolean;
}

export interface InmueblePublic {
  id: string;
  direccion: string;
  categoria: string;
  superficie: number | null;
  habitaciones: number | null;
  banos: number | null;
  dormitorios: number | null;
  comodidades: string | null;
  descripcion: string | null;
  estado: string;
  created_at: string | null;
  updated_at: string | null;
}

export interface CobroPublic {
  id: string;
  contrato_id: string;
  fecha_cobro: string;
  monto: number;
  moneda_original: string | null;
  monto_original: number | null;
  cotizacion: number | null;
  fuente_precio: string | null;
  precio_producto: number | null;
  observaciones: string | null;
  registrado_por_user_id: string | null;
  registrado_por_nombre: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface CobroInforme {
  id: string;
  fecha_cobro: string;
  monto_bruto: number;
  porcentaje_participacion: number;
  porcentaje_admin: number;
  costo_admin: number;
  monto_neto: number;
  inmueble_direccion: string;
  inmueble_tipo: string;
  observaciones: string | null;
}

export interface PropietarioInforme {
  propietario_id: string;
  propietario_nombre: string;
  propietario_cuit: string;
  cobros: CobroInforme[];
  total_bruto: number;
  total_admin: number;
  total_neto: number;
}

export interface InformePropietarios {
  mode: 'general';
  costo_admin_urbano: number;
  costo_admin_rural: number;
  propietarios: PropietarioInforme[];
}

// ── Pivot mode (inmueble filter) ──────────────────────────

export interface PropietarioPivotColumn {
  propietario_id: string;
  nombre: string;
  cuit: string;
  porcentaje: number;
}

export interface MontoPropietario {
  bruto: number;
  admin: number;
  neto: number;
}

export interface MesInforme {
  mes_key: string;
  mes_label: string;
  prop_montos: Record<string, MontoPropietario>;
  total_bruto: number;
  total_admin: number;
  total_neto: number;
}

export interface InformePivot {
  mode: 'pivot';
  costo_admin_urbano: number;
  costo_admin_rural: number;
  propietarios: PropietarioPivotColumn[];
  meses: MesInforme[];
  totales: {
    prop_montos: Record<string, MontoPropietario>;
    total_bruto: number;
    total_admin: number;
    total_neto: number;
  };
}

export type InformeResponse = InformePropietarios | InformePivot;

export const api = {
  async login(data: LoginRequest): Promise<LoginResponse> {
    const res = await fetch(`${API_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Credenciales incorrectas');
    return res.json();
  },

  async getUsers(token: string, role?: string): Promise<User[]> {
    const url = role ? `${API_URL}/users?role=${role}` : `${API_URL}/users`;
    const res = await fetch(url, {
      headers: { 'X-Access-Token': token },
    });
    if (!res.ok) throw new Error('Error al obtener usuarios');
    return res.json();
  },

  async createUser(
    token: string,
    data: { email: string; password: string; full_name?: string; role: string }
  ): Promise<User> {
    const res = await fetch(`${API_URL}/users`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Access-Token': token,
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Error al crear usuario');
    }
    return res.json();
  },

  async getMe(token: string): Promise<User> {
    const res = await fetch(`${API_URL}/me`, {
      headers: { 'X-Access-Token': token },
    });
    if (!res.ok) throw new Error('No autenticado');
    return res.json();
  },

  async changePassword(
    token: string,
    data: { current_password: string; new_password: string }
  ): Promise<void> {
    const res = await fetch(`${API_URL}/change-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Access-Token': token,
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Error al cambiar contraseña');
    }
  },

  async getDashboardInmuebles(
    token: string,
    filters: DashboardFilters = {}
  ): Promise<InmuebleDashboard[]> {
    const params = new URLSearchParams();
    if (filters.estado) params.set('estado', filters.estado);
    if (filters.categoria) params.set('categoria', filters.categoria);
    if (filters.propietario) params.set('propietario', filters.propietario);
    if (filters.inmueble) params.set('inmueble', filters.inmueble);
    if (filters.morosos !== undefined) params.set('morosos', String(filters.morosos));

    const qs = params.toString();
    const url = `${API_URL}/dashboard/inmuebles${qs ? '?' + qs : ''}`;
    const res = await fetch(url, {
      headers: { 'X-Access-Token': token },
    });
    if (!res.ok) throw new Error('Error al cargar inmuebles del dashboard');
    return res.json();
  },

  // ── Configuracion ──────────────────────────────────────

  async getConfig(): Promise<Record<string, string | null>> {
    const res = await fetch(`${API_URL}/configuracion`);
    if (!res.ok) throw new Error('Error loading config');
    return res.json();
  },

  async setConfig(token: string, items: Record<string, string | null>): Promise<void> {
    const res = await fetch(`${API_URL}/configuracion`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-Access-Token': token,
      },
      body: JSON.stringify({ items }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Error saving config');
    }
  },

  // ── Inmuebles CRUD ──────────────────────────────────────

  async getInmuebles(
    token: string,
    filters: { estado?: string; categoria?: string } = {}
  ): Promise<InmueblePublic[]> {
    const params = new URLSearchParams();
    if (filters.estado) params.set('estado', filters.estado);
    if (filters.categoria) params.set('categoria', filters.categoria);
    const qs = params.toString();
    const url = `${API_URL}/inmuebles${qs ? '?' + qs : ''}`;
    const res = await fetch(url, {
      headers: { 'X-Access-Token': token },
    });
    if (!res.ok) throw new Error('Error al obtener inmuebles');
    return res.json();
  },

  async deleteInmueble(token: string, id: string): Promise<void> {
    const res = await fetch(`${API_URL}/inmuebles/${id}`, {
      method: 'DELETE',
      headers: { 'X-Access-Token': token },
    });
    if (!res.ok) throw new Error('Error al eliminar inmueble');
  },

  async createInmueble(
    token: string,
    data: {
      direccion: string;
      categoria?: string;
      superficie?: number;
      habitaciones?: number;
      banos?: number;
      dormitorios?: number;
      comodidades?: string;
      descripcion?: string;
      propietarios?: Array<{
        propietario_id?: string;
        porcentaje_participacion: number;
        nombre?: string;
        cuit?: string;
        telefono?: string;
        email?: string;
        direccion?: string;
      }>;
    }
  ): Promise<InmueblePublic> {
    const res = await fetch(`${API_URL}/inmuebles/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Access-Token': token,
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Error al crear inmueble');
    }
    return res.json();
  },

  async updateInmueble(
    token: string,
    id: string,
    data: {
      direccion?: string;
      categoria?: string;
      superficie?: number;
      habitaciones?: number;
      banos?: number;
      dormitorios?: number;
      comodidades?: string;
      descripcion?: string;
      estado?: string;
    }
  ): Promise<InmueblePublic> {
    const res = await fetch(`${API_URL}/inmuebles/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-Access-Token': token,
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Error al actualizar inmueble');
    }
    return res.json();
  },

  // ── Users CRUD (admin) ──────────────────────────────────

  async updateUser(
    token: string,
    userId: string,
    data: { full_name?: string; role?: string; is_active?: boolean }
  ): Promise<User> {
    const res = await fetch(`${API_URL}/users/${userId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-Access-Token': token,
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Error al actualizar usuario');
    }
    return res.json();
  },

  async deleteUser(token: string, userId: string): Promise<void> {
    const res = await fetch(`${API_URL}/users/${userId}`, {
      method: 'DELETE',
      headers: { 'X-Access-Token': token },
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Error al eliminar usuario');
    }
  },

  // ── Contratos ──────────────────────────────────────────

  async getContratos(
    token: string,
    filters: { activo?: boolean } = {}
  ): Promise<ContratoDash[]> {
    const params = new URLSearchParams();
    if (filters.activo !== undefined) params.set('activo', String(filters.activo));
    const qs = params.toString();
    const url = `${API_URL}/contratos${qs ? '?' + qs : ''}`;
    const res = await fetch(url, {
      headers: { 'X-Access-Token': token },
    });
    if (!res.ok) throw new Error('Error al obtener contratos');
    return res.json();
  },

  async updateContrato(
    token: string,
    id: string,
    data: {
      fecha_inicio?: string;
      fecha_fin?: string;
      fecha_maxima_pago?: number;
      modalidad_pago?: string;
      frecuencia?: string;
      monto_base?: number;
      moneda?: string;
      indice?: string;
      periodo_indexacion?: string;
      tipo_producto?: string;
      kilos?: number;
      precio_kilo?: number;
      fuente_precio_agro?: string;
      activo?: boolean;
    }
  ): Promise<ContratoDash> {
    const res = await fetch(`${API_URL}/contratos/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-Access-Token': token,
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Error al actualizar contrato');
    }
    return res.json();
  },

  async deleteContrato(token: string, id: string): Promise<void> {
    const res = await fetch(`${API_URL}/contratos/${id}`, {
      method: 'DELETE',
      headers: { 'X-Access-Token': token },
    });
    if (!res.ok) throw new Error('Error al eliminar contrato');
  },

  async getContratosByInmueble(token: string, inmuebleId: string): Promise<ContratoDash[]> {
    const res = await fetch(`${API_URL}/contratos/inmueble/${inmuebleId}`, {
      headers: { 'X-Access-Token': token },
    });
    if (!res.ok) throw new Error('Error al obtener contratos');
    return res.json();
  },

  async createContrato(
    token: string,
    data: {
      inmueble_id: string;
      inquilino_id: string;
      fecha_inicio: string;
      fecha_fin: string;
      fecha_maxima_pago?: number;
      modalidad_pago: string;
      frecuencia?: string;
      monto_base?: number;
      moneda?: string;
      indice?: string;
      periodo_indexacion?: string;
      tipo_producto?: string;
      kilos?: number;
      precio_kilo?: number;
      fuente_precio_agro?: string;
    }
  ): Promise<ContratoDash> {
    const res = await fetch(`${API_URL}/contratos`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Access-Token': token,
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Error al crear contrato');
    }
    return res.json();
  },

  // ── Cobros ─────────────────────────────────────────────

  async createCobro(
    token: string,
    data: {
      contrato_id: string;
      fecha_cobro: string;
      monto: number;
      moneda_original?: string;
      monto_original?: number;
      cotizacion?: number;
      observaciones?: string;
    }
  ): Promise<CobroPublic> {
    const res = await fetch(`${API_URL}/cobros`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Access-Token': token,
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Error al registrar cobro');
    }
    return res.json();
  },

  async getCobrosByContrato(token: string, contratoId: string): Promise<CobroPublic[]> {
    const res = await fetch(`${API_URL}/cobros/contrato/${contratoId}`, {
      headers: { 'X-Access-Token': token },
    });
    if (!res.ok) throw new Error('Error al obtener cobros');
    return res.json();
  },

  async getCobros(
    token: string,
    filters: { fecha_inicio?: string; fecha_fin?: string } = {}
  ): Promise<CobroPublic[]> {
    const params = new URLSearchParams();
    if (filters.fecha_inicio) params.set('fecha_inicio', filters.fecha_inicio);
    if (filters.fecha_fin) params.set('fecha_fin', filters.fecha_fin);
    const qs = params.toString();
    const url = `${API_URL}/cobros${qs ? '?' + qs : ''}`;
    const res = await fetch(url, {
      headers: { 'X-Access-Token': token },
    });
    if (!res.ok) throw new Error('Error al obtener cobros');
    return res.json();
  },

  async deleteCobro(token: string, id: string): Promise<void> {
    const res = await fetch(`${API_URL}/cobros/${id}`, {
      method: 'DELETE',
      headers: { 'X-Access-Token': token },
    });
    if (!res.ok) throw new Error('Error al eliminar cobro');
  },

  // ── Propietarios ───────────────────────────────────────

  async getPropietariosByInmueble(token: string, inmuebleId: string): Promise<PropietarioDash[]> {
    const res = await fetch(`${API_URL}/inmuebles/${inmuebleId}/propietarios`, {
      headers: { 'X-Access-Token': token },
    });
    if (!res.ok) throw new Error('Error al obtener propietarios');
    return res.json();
  },

  // ── Personas ──────────────────────────────────────────

  async getPersonas(token: string, filters: { rol?: string } = {}): Promise<Persona[]> {
    const params = new URLSearchParams();
    if (filters.rol) params.set('rol', filters.rol);
    const qs = params.toString();
    const url = `${API_URL}/personas${qs ? '?' + qs : ''}`;
    const res = await fetch(url, { headers: { 'X-Access-Token': token } });
    if (!res.ok) throw new Error('Error al obtener personas');
    return res.json();
  },

  async getPropietarios(token: string): Promise<Persona[]> {
    const res = await fetch(`${API_URL}/personas/propietarios`, {
      headers: { 'X-Access-Token': token },
    });
    if (!res.ok) throw new Error('Error al obtener propietarios');
    return res.json();
  },

  async getInquilinos(token: string): Promise<Persona[]> {
    const res = await fetch(`${API_URL}/personas/inquilinos`, {
      headers: { 'X-Access-Token': token },
    });
    if (!res.ok) throw new Error('Error al obtener inquilinos');
    return res.json();
  },

  async createPersona(token: string, data: PersonaCreateData): Promise<Persona> {
    const res = await fetch(`${API_URL}/personas/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Access-Token': token },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Error al crear persona');
    }
    return res.json();
  },

  async updatePersona(token: string, id: string, data: Partial<PersonaCreateData>): Promise<Persona> {
    const res = await fetch(`${API_URL}/personas/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'X-Access-Token': token },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Error al actualizar persona');
    }
    return res.json();
  },

  async deletePersona(token: string, id: string): Promise<void> {
    const res = await fetch(`${API_URL}/personas/${id}`, {
      method: 'DELETE',
      headers: { 'X-Access-Token': token },
    });
    if (!res.ok) throw new Error('Error al eliminar persona');
  },

  // ── Copropiedad (inmueble ↔ propietario) ─────────────────

  async getCopropietariosByInmueble(token: string, inmuebleId: string): Promise<CopropiedadPublic[]> {
    const res = await fetch(`${API_URL}/inmuebles/${inmuebleId}/propietarios`, {
      headers: { 'X-Access-Token': token },
    });
    if (!res.ok) throw new Error('Error al obtener copropietarios');
    return res.json();
  },

  async updateCopropietarios(
    token: string,
    inmuebleId: string,
    propietarios: Array<{ propietario_id: string; porcentaje_participacion: number }>
  ): Promise<CopropiedadPublic[]> {
    const res = await fetch(`${API_URL}/inmuebles/${inmuebleId}/propietarios`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-Access-Token': token,
      },
      body: JSON.stringify(propietarios),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Error al actualizar propietarios');
    }
    return res.json();
  },

  // ── Informes ─────────────────────────────────────────────

  async getInformePropietarios(
    token: string,
    params?: { fecha_inicio?: string; fecha_fin?: string; propietario_id?: string; inmueble_id?: string }
  ): Promise<InformeResponse> {
    const searchParams = new URLSearchParams();
    if (params?.fecha_inicio) searchParams.set('fecha_inicio', params.fecha_inicio);
    if (params?.fecha_fin) searchParams.set('fecha_fin', params.fecha_fin);
    if (params?.propietario_id) searchParams.set('propietario_id', params.propietario_id);
    if (params?.inmueble_id) searchParams.set('inmueble_id', params.inmueble_id);
    const qs = searchParams.toString();
    const res = await fetch(`${API_URL}/informes/propietarios${qs ? '?' + qs : ''}`, {
      headers: { 'X-Access-Token': token },
    });
    if (!res.ok) throw new Error('Error al obtener informe de propietarios');
    return res.json();
  },
};
