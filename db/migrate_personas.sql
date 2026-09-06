-- Migration: Merge propietarios and inquilinos into unified personas table
-- Run after backing up existing data!

BEGIN;

-- Step 1: Create personas table
CREATE TABLE personas (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    nombre VARCHAR(255) NOT NULL,
    cuit VARCHAR(20) UNIQUE NOT NULL,
    iva VARCHAR(50),
    telefono VARCHAR(50),
    email VARCHAR(255),
    direccion VARCHAR(500),
    rol VARCHAR(20) NOT NULL DEFAULT 'propietario',  -- propietario, inquilino, ambos
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Step 2: Insert propietarios (rol='propietario')
INSERT INTO personas (id, nombre, cuit, iva, telefono, email, direccion, rol, created_at, updated_at)
SELECT id, nombre, dni_cuit, NULL, telefono, email, direccion, 'propietario', created_at, updated_at
FROM propietarios;

-- Step 3: Insert or merge inquilinos
-- 3a: If cuit already exists (person is both propietario and inquilino), update to 'ambos' and merge iva
UPDATE personas p
SET rol = 'ambos',
    iva = COALESCE(i.iva, p.iva),
    updated_at = NOW()
FROM inquilinos i
WHERE i.cuit = p.cuit;

-- 3b: Insert inquilinos whose cuit does NOT exist in personas yet
INSERT INTO personas (id, nombre, cuit, iva, telefono, email, direccion, rol, created_at, updated_at)
SELECT i.id, i.nombre, i.cuit, i.iva, i.telefono, i.email, i.direccion, 'inquilino', i.created_at, i.updated_at
FROM inquilinos i
WHERE i.cuit NOT IN (SELECT cuit FROM personas);

-- Step 4: Add propietario_id FK column to copropiedad pointing to personas(id)
ALTER TABLE copropiedad ADD COLUMN propietario_id_new VARCHAR(36) REFERENCES personas(id) ON DELETE RESTRICT;

-- Step 5: Update copropiedad FK references using cuit-based mapping
UPDATE copropiedad c
SET propietario_id_new = p.id
FROM propietarios pr, personas p
WHERE c.propietario_id = pr.id AND pr.dni_cuit = p.cuit;

-- Step 6: Add inquilino_id FK column to contratos pointing to personas(id)
ALTER TABLE contratos ADD COLUMN inquilino_id_new VARCHAR(36) REFERENCES personas(id) ON DELETE RESTRICT;

-- Step 7: Update contratos FK references
UPDATE contratos c
SET inquilino_id_new = p.id
FROM inquilinos i, personas p
WHERE c.inquilino_id = i.id AND i.cuit = p.cuit;

-- Step 8: Add propietario_id FK column to comprobantes pointing to personas(id)
ALTER TABLE comprobantes ADD COLUMN propietario_id_new VARCHAR(36) REFERENCES personas(id) ON DELETE RESTRICT;

-- Step 9: Update comprobantes FK references
UPDATE comprobantes c
SET propietario_id_new = p.id
FROM propietarios pr, personas p
WHERE c.propietario_id = pr.id AND pr.dni_cuit = p.cuit;

-- Step 10: Drop old FK constraints
ALTER TABLE copropiedad DROP CONSTRAINT IF EXISTS copropiedad_propietario_id_fkey;
ALTER TABLE contratos DROP CONSTRAINT IF EXISTS contratos_inquilino_id_fkey;
ALTER TABLE comprobantes DROP CONSTRAINT IF EXISTS comprobantes_propietario_id_fkey;

-- Step 11: Drop old columns and rename new ones
ALTER TABLE copropiedad DROP COLUMN propietario_id;
ALTER TABLE copropiedad RENAME COLUMN propietario_id_new TO propietario_id;

ALTER TABLE contratos DROP COLUMN inquilino_id;
ALTER TABLE contratos RENAME COLUMN inquilino_id_new TO inquilino_id;

ALTER TABLE comprobantes DROP COLUMN propietario_id;
ALTER TABLE comprobantes RENAME COLUMN propietario_id_new TO propietario_id;

-- Step 12: Drop old tables
DROP TABLE IF EXISTS propietarios CASCADE;
DROP TABLE IF EXISTS inquilinos CASCADE;

-- Step 13: Create indexes
CREATE INDEX idx_personas_cuit ON personas(cuit);
CREATE INDEX idx_personas_rol ON personas(rol);
CREATE INDEX idx_copropiedad_propietario ON copropiedad(propietario_id);
CREATE INDEX idx_contratos_inquilino ON contratos(inquilino_id);
CREATE INDEX idx_comprobantes_propietario ON comprobantes(propietario_id);

-- Step 14: Add updated_at trigger for personas
CREATE TRIGGER update_personas_updated_at
    BEFORE UPDATE ON personas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMIT;
