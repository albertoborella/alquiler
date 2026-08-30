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
}

export interface InquilinoDash {
  id: string;
  nombre: string;
  cuit: string | null;
  iva: string | null;
  telefono: string | null;
  email: string | null;
}

export interface Propietario {
  id: string;
  nombre: string;
  dni_cuit: string;
  telefono: string | null;
  email: string | null;
  direccion: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface PropietarioCreateData {
  nombre: string;
  dni_cuit: string;
  telefono?: string;
  email?: string;
  direccion?: string;
}

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

export interface InquilinoPublic {
  id: string;
  nombre: string;
  cuit: string | null;
  iva: string | null;
  telefono: string | null;
  email: string | null;
  direccion: string | null;
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
  created_at: string | null;
  updated_at: string | null;
}

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
        dni_cuit?: string;
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

  // ── Inquilinos ─────────────────────────────────────────

  async getInquilinos(token: string): Promise<InquilinoPublic[]> {
    const res = await fetch(`${API_URL}/inquilinos/`, {
      headers: { 'X-Access-Token': token },
    });
    if (!res.ok) throw new Error('Error al obtener inquilinos');
    return res.json();
  },

  async createInquilino(
    token: string,
    data: {
      nombre: string;
      cuit: string;
      iva?: string;
      telefono?: string;
      email?: string;
      direccion?: string;
    }
  ): Promise<InquilinoPublic> {
    const res = await fetch(`${API_URL}/inquilinos/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Access-Token': token,
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Error al crear inquilino');
    }
    return res.json();
  },

  async updateInquilino(
    token: string,
    id: string,
    data: {
      nombre?: string;
      cuit?: string;
      iva?: string;
      telefono?: string;
      email?: string;
      direccion?: string;
    }
  ): Promise<InquilinoPublic> {
    const res = await fetch(`${API_URL}/inquilinos/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-Access-Token': token,
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Error al actualizar inquilino');
    }
    return res.json();
  },

  async deleteInquilino(token: string, id: string): Promise<void> {
    const res = await fetch(`${API_URL}/inquilinos/${id}`, {
      method: 'DELETE',
      headers: { 'X-Access-Token': token },
    });
    if (!res.ok) throw new Error('Error al eliminar inquilino');
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

  // ── Propietarios ───────────────────────────────────────

  async getPropietariosByInmueble(token: string, inmuebleId: string): Promise<PropietarioDash[]> {
    const res = await fetch(`${API_URL}/inmuebles/${inmuebleId}/propietarios`, {
      headers: { 'X-Access-Token': token },
    });
    if (!res.ok) throw new Error('Error al obtener propietarios');
    return res.json();
  },

  async getPropietarios(token: string): Promise<Propietario[]> {
    const res = await fetch(`${API_URL}/propietarios/`, {
      headers: { 'X-Access-Token': token },
    });
    if (!res.ok) throw new Error('Error al obtener propietarios');
    return res.json();
  },

  async createPropietario(token: string, data: PropietarioCreateData): Promise<Propietario> {
    const res = await fetch(`${API_URL}/propietarios/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Access-Token': token,
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Error al crear propietario');
    }
    return res.json();
  },
};
