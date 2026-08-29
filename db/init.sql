-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'empleado',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Propietarios table
CREATE TABLE propietarios (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    nombre VARCHAR(255) NOT NULL,
    dni_cuit VARCHAR(20) UNIQUE NOT NULL,
    telefono VARCHAR(50),
    email VARCHAR(255),
    direccion VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Inquilinos table
CREATE TABLE inquilinos (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    nombre VARCHAR(255) NOT NULL,
    dni VARCHAR(20) UNIQUE NOT NULL,
    telefono VARCHAR(50),
    email VARCHAR(255),
    direccion VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Inmuebles table
CREATE TABLE inmuebles (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    direccion VARCHAR(500) NOT NULL,
    categoria VARCHAR(10) NOT NULL DEFAULT 'urbano',
    superficie DECIMAL(10,2),
    habitaciones INTEGER,
    banos INTEGER,
    dormitorios INTEGER,
    comodidades TEXT,
    descripcion TEXT,
    estado VARCHAR(15) NOT NULL DEFAULT 'disponible',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Copropiedad table (Propietarios-Inmuebles)
CREATE TABLE copropiedad (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    propietario_id VARCHAR(36) NOT NULL REFERENCES propietarios(id) ON DELETE RESTRICT,
    inmueble_id VARCHAR(36) NOT NULL REFERENCES inmuebles(id) ON DELETE RESTRICT,
    porcentaje_participacion DECIMAL(5,2) NOT NULL DEFAULT 100.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(propietario_id, inmueble_id)
);

-- Contratos table
CREATE TABLE contratos (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    inmueble_id VARCHAR(36) NOT NULL REFERENCES inmuebles(id) ON DELETE RESTRICT,
    inquilino_id VARCHAR(36) NOT NULL REFERENCES inquilinos(id) ON DELETE RESTRICT,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    fecha_maxima_pago INTEGER NOT NULL DEFAULT 10,
    modalidad_pago VARCHAR(30) NOT NULL,
    frecuencia VARCHAR(15) NOT NULL DEFAULT 'mensual',
    monto_base DECIMAL(12,2),
    moneda VARCHAR(3) DEFAULT 'ARS',
    indice VARCHAR(50),
    periodo_indexacion VARCHAR(50),
    tipo_producto VARCHAR(100),
    kilos DECIMAL(12,2),
    precio_kilo DECIMAL(12,2),
    fuente_precio_agro VARCHAR(255),
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Cobros table
CREATE TABLE cobros (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    contrato_id VARCHAR(36) NOT NULL REFERENCES contratos(id) ON DELETE RESTRICT,
    fecha_cobro DATE NOT NULL,
    monto DECIMAL(12,2) NOT NULL,
    moneda_original VARCHAR(3),
    monto_original DECIMAL(12,2),
    cotizacion DECIMAL(10,4),
    fuente_precio VARCHAR(255),
    precio_producto DECIMAL(12,2),
    observaciones TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Comprobantes table
CREATE TABLE comprobantes (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    cobro_id VARCHAR(36) NOT NULL REFERENCES cobros(id) ON DELETE RESTRICT,
    propietario_id VARCHAR(36) NOT NULL REFERENCES propietarios(id) ON DELETE RESTRICT,
    tipo VARCHAR(15) NOT NULL DEFAULT 'comprobante',
    numero VARCHAR(50),
    descripcion TEXT,
    monto_proporcional DECIMAL(12,2) NOT NULL,
    porcentaje_participacion DECIMAL(5,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit log table
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(36),
    old_values JSONB,
    new_values JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_propietarios_dni_cuit ON propietarios(dni_cuit);
CREATE INDEX idx_inquilinos_dni ON inquilinos(dni);
CREATE INDEX idx_inmuebles_estado ON inmuebles(estado);
CREATE INDEX idx_inmuebles_categoria ON inmuebles(categoria);
CREATE INDEX idx_inmuebles_direccion ON inmuebles(direccion);
CREATE INDEX idx_copropiedad_propietario ON copropiedad(propietario_id);
CREATE INDEX idx_copropiedad_inmueble ON copropiedad(inmueble_id);
CREATE INDEX idx_contratos_inmueble ON contratos(inmueble_id);
CREATE INDEX idx_contratos_inquilino ON contratos(inquilino_id);
CREATE INDEX idx_contratos_fechas ON contratos(fecha_inicio, fecha_fin);
CREATE INDEX idx_cobros_contrato ON cobros(contrato_id);
CREATE INDEX idx_cobros_fecha ON cobros(fecha_cobro);
CREATE INDEX idx_comprobantes_cobro ON comprobantes(cobro_id);
CREATE INDEX idx_comprobantes_propietario ON comprobantes(propietario_id);
CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_table ON audit_log(table_name);
CREATE INDEX idx_audit_log_created ON audit_log(created_at);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_propietarios_updated_at
    BEFORE UPDATE ON propietarios
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_inquilinos_updated_at
    BEFORE UPDATE ON inquilinos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_inmuebles_updated_at
    BEFORE UPDATE ON inmuebles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contratos_updated_at
    BEFORE UPDATE ON contratos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cobros_updated_at
    BEFORE UPDATE ON cobros
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
