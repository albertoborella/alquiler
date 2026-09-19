--
-- PostgreSQL database dump
--

\restrict aDlKjllu4le9ubvTEOeJLLYT8f5htBQrGYZWXRJMQUx5SSuPQ3R8dqpkmBsNfLR

-- Dumped from database version 15.19
-- Dumped by pg_dump version 15.19

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: alquiler_user
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO alquiler_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: audit_log; Type: TABLE; Schema: public; Owner: alquiler_user
--

CREATE TABLE public.audit_log (
    id integer NOT NULL,
    user_id character varying(36),
    action character varying(50) NOT NULL,
    table_name character varying(100) NOT NULL,
    record_id character varying(36),
    old_values jsonb,
    new_values jsonb,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.audit_log OWNER TO alquiler_user;

--
-- Name: audit_log_id_seq; Type: SEQUENCE; Schema: public; Owner: alquiler_user
--

CREATE SEQUENCE public.audit_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.audit_log_id_seq OWNER TO alquiler_user;

--
-- Name: audit_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: alquiler_user
--

ALTER SEQUENCE public.audit_log_id_seq OWNED BY public.audit_log.id;


--
-- Name: cobros; Type: TABLE; Schema: public; Owner: alquiler_user
--

CREATE TABLE public.cobros (
    id character varying(36) DEFAULT (public.uuid_generate_v4())::text NOT NULL,
    contrato_id character varying(36) NOT NULL,
    fecha_cobro date NOT NULL,
    monto numeric(12,2) NOT NULL,
    moneda_original character varying(3),
    monto_original numeric(12,2),
    cotizacion numeric(10,4),
    fuente_precio character varying(255),
    precio_producto numeric(12,2),
    observaciones text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.cobros OWNER TO alquiler_user;

--
-- Name: comprobantes; Type: TABLE; Schema: public; Owner: alquiler_user
--

CREATE TABLE public.comprobantes (
    id character varying(36) DEFAULT (public.uuid_generate_v4())::text NOT NULL,
    cobro_id character varying(36) NOT NULL,
    propietario_id character varying(36) NOT NULL,
    tipo character varying(15) DEFAULT 'comprobante'::character varying NOT NULL,
    numero character varying(50),
    descripcion text,
    monto_proporcional numeric(12,2) NOT NULL,
    porcentaje_participacion numeric(5,2) NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.comprobantes OWNER TO alquiler_user;

--
-- Name: contratos; Type: TABLE; Schema: public; Owner: alquiler_user
--

CREATE TABLE public.contratos (
    id character varying(36) DEFAULT (public.uuid_generate_v4())::text NOT NULL,
    inmueble_id character varying(36) NOT NULL,
    inquilino_id character varying(36) NOT NULL,
    fecha_inicio date NOT NULL,
    fecha_fin date NOT NULL,
    fecha_maxima_pago integer DEFAULT 10 NOT NULL,
    modalidad_pago character varying(30) NOT NULL,
    frecuencia character varying(15) DEFAULT 'mensual'::character varying NOT NULL,
    monto_base numeric(12,2),
    moneda character varying(3) DEFAULT 'ARS'::character varying,
    indice character varying(50),
    periodo_indexacion character varying(50),
    tipo_producto character varying(100),
    kilos numeric(12,2),
    precio_kilo numeric(12,2),
    fuente_precio_agro character varying(255),
    activo boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.contratos OWNER TO alquiler_user;

--
-- Name: copropiedad; Type: TABLE; Schema: public; Owner: alquiler_user
--

CREATE TABLE public.copropiedad (
    id character varying(36) DEFAULT (public.uuid_generate_v4())::text NOT NULL,
    propietario_id character varying(36) NOT NULL,
    inmueble_id character varying(36) NOT NULL,
    porcentaje_participacion numeric(5,2) DEFAULT 100.00 NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.copropiedad OWNER TO alquiler_user;

--
-- Name: inmuebles; Type: TABLE; Schema: public; Owner: alquiler_user
--

CREATE TABLE public.inmuebles (
    id character varying(36) DEFAULT (public.uuid_generate_v4())::text NOT NULL,
    direccion character varying(500) NOT NULL,
    categoria character varying(10) DEFAULT 'urbano'::character varying NOT NULL,
    superficie numeric(10,2),
    habitaciones integer,
    banos integer,
    dormitorios integer,
    comodidades text,
    descripcion text,
    estado character varying(15) DEFAULT 'disponible'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.inmuebles OWNER TO alquiler_user;

--
-- Name: inquilinos; Type: TABLE; Schema: public; Owner: alquiler_user
--

CREATE TABLE public.inquilinos (
    id character varying(36) DEFAULT (public.uuid_generate_v4())::text NOT NULL,
    nombre character varying(255) NOT NULL,
    cuit character varying(20),
    telefono character varying(50),
    email character varying(255),
    direccion character varying(500),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    iva character varying(50)
);


ALTER TABLE public.inquilinos OWNER TO alquiler_user;

--
-- Name: propietarios; Type: TABLE; Schema: public; Owner: alquiler_user
--

CREATE TABLE public.propietarios (
    id character varying(36) DEFAULT (public.uuid_generate_v4())::text NOT NULL,
    nombre character varying(255) NOT NULL,
    dni_cuit character varying(20) NOT NULL,
    telefono character varying(50),
    email character varying(255),
    direccion character varying(500),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.propietarios OWNER TO alquiler_user;

--
-- Name: users; Type: TABLE; Schema: public; Owner: alquiler_user
--

CREATE TABLE public.users (
    id character varying(36) DEFAULT (public.uuid_generate_v4())::text NOT NULL,
    email character varying(255) NOT NULL,
    hashed_password character varying(255) NOT NULL,
    full_name character varying(255),
    role character varying(50) DEFAULT 'empleado'::character varying NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.users OWNER TO alquiler_user;

--
-- Name: audit_log id; Type: DEFAULT; Schema: public; Owner: alquiler_user
--

ALTER TABLE ONLY public.audit_log ALTER COLUMN id SET DEFAULT nextval('public.audit_log_id_seq'::regclass);


--
-- Data for Name: audit_log; Type: TABLE DATA; Schema: public; Owner: alquiler_user
--

COPY public.audit_log (id, user_id, action, table_name, record_id, old_values, new_values, created_at) FROM stdin;
\.


--
-- Data for Name: cobros; Type: TABLE DATA; Schema: public; Owner: alquiler_user
--

COPY public.cobros (id, contrato_id, fecha_cobro, monto, moneda_original, monto_original, cotizacion, fuente_precio, precio_producto, observaciones, created_at, updated_at) FROM stdin;
be5373b7-6bd6-4b66-863f-bade280f31ca	ef47f291-2d3b-4bb4-90d2-890f2c6cf8d4	2026-09-04	100.00	ARS	100.00	\N	\N	\N	\N	2026-09-04 00:10:33.849435+00	\N
\.


--
-- Data for Name: comprobantes; Type: TABLE DATA; Schema: public; Owner: alquiler_user
--

COPY public.comprobantes (id, cobro_id, propietario_id, tipo, numero, descripcion, monto_proporcional, porcentaje_participacion, created_at) FROM stdin;
\.


--
-- Data for Name: contratos; Type: TABLE DATA; Schema: public; Owner: alquiler_user
--

COPY public.contratos (id, inmueble_id, inquilino_id, fecha_inicio, fecha_fin, fecha_maxima_pago, modalidad_pago, frecuencia, monto_base, moneda, indice, periodo_indexacion, tipo_producto, kilos, precio_kilo, fuente_precio_agro, activo, created_at, updated_at) FROM stdin;
ef47f291-2d3b-4bb4-90d2-890f2c6cf8d4	f107aafd-dbd0-46b2-aef4-e5498b359646	8c067745-5782-4788-8f47-24ff8796398e	2026-09-04	2027-09-03	10	pesos_indice	mensual	100.00	ARS	\N	\N	\N	\N	\N	\N	t	2026-09-04 00:09:34.407761+00	\N
\.


--
-- Data for Name: copropiedad; Type: TABLE DATA; Schema: public; Owner: alquiler_user
--

COPY public.copropiedad (id, propietario_id, inmueble_id, porcentaje_participacion, created_at) FROM stdin;
8e14ecc5-b718-4230-aede-8462d84a4c20	6be2fb23-45ef-4174-9ff7-ecba08562055	f107aafd-dbd0-46b2-aef4-e5498b359646	100.00	2026-09-03 23:41:16.896388+00
\.


--
-- Data for Name: inmuebles; Type: TABLE DATA; Schema: public; Owner: alquiler_user
--

COPY public.inmuebles (id, direccion, categoria, superficie, habitaciones, banos, dormitorios, comodidades, descripcion, estado, created_at, updated_at) FROM stdin;
f107aafd-dbd0-46b2-aef4-e5498b359646	Perú 345 - Santa Fe	urbano	85.00	4	1	3	Balcon y SUM	Buen estado de conservacion	disponible	2026-09-03 21:58:06.620801+00	2026-09-03 23:41:16.800224+00
\.


--
-- Data for Name: inquilinos; Type: TABLE DATA; Schema: public; Owner: alquiler_user
--

COPY public.inquilinos (id, nombre, cuit, telefono, email, direccion, created_at, updated_at, iva) FROM stdin;
8c067745-5782-4788-8f47-24ff8796398e	Juan Perez	248523699	3492654789	juan@juan.com	Blvd. G. Lehmann 3734	2026-08-29 23:30:17.738534+00	2026-09-03 22:59:39.569597+00	Resp. inscripto
\.


--
-- Data for Name: propietarios; Type: TABLE DATA; Schema: public; Owner: alquiler_user
--

COPY public.propietarios (id, nombre, dni_cuit, telefono, email, direccion, created_at, updated_at) FROM stdin;
b52d2d42-367a-490f-926e-64ec47a6e635	pepe marino	339874562	11456987	pepe@pepe.com	caseros 24	2026-08-30 13:18:21.922558+00	\N
6be2fb23-45ef-4174-9ff7-ecba08562055	Juan Faría	308521473	111222666	juan@juan.com	Calle 15 2356	2026-09-03 21:58:06.641096+00	\N
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: alquiler_user
--

COPY public.users (id, email, hashed_password, full_name, role, is_active, created_at, updated_at) FROM stdin;
c1c05742-3891-4fea-8fd5-5b0368f9c63f	admin@alquiler.com	$2b$12$.vK3D/odQ9Silei.xTtQZ.yP5fesprxRF8rpJs8uz3n.LsStxkWQi	Administrador	admin	t	2026-08-29 23:30:04.113076+00	\N
\.


--
-- Name: audit_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alquiler_user
--

SELECT pg_catalog.setval('public.audit_log_id_seq', 1, false);


--
-- Name: audit_log audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: alquiler_user
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_pkey PRIMARY KEY (id);


--
-- Name: cobros cobros_pkey; Type: CONSTRAINT; Schema: public; Owner: alquiler_user
--

ALTER TABLE ONLY public.cobros
    ADD CONSTRAINT cobros_pkey PRIMARY KEY (id);


--
-- Name: comprobantes comprobantes_pkey; Type: CONSTRAINT; Schema: public; Owner: alquiler_user
--

ALTER TABLE ONLY public.comprobantes
    ADD CONSTRAINT comprobantes_pkey PRIMARY KEY (id);


--
-- Name: contratos contratos_pkey; Type: CONSTRAINT; Schema: public; Owner: alquiler_user
--

ALTER TABLE ONLY public.contratos
    ADD CONSTRAINT contratos_pkey PRIMARY KEY (id);


--
-- Name: copropiedad copropiedad_pkey; Type: CONSTRAINT; Schema: public; Owner: alquiler_user
--

ALTER TABLE ONLY public.copropiedad
    ADD CONSTRAINT copropiedad_pkey PRIMARY KEY (id);


--
-- Name: copropiedad copropiedad_propietario_id_inmueble_id_key; Type: CONSTRAINT; Schema: public; Owner: alquiler_user
--

ALTER TABLE ONLY public.copropiedad
    ADD CONSTRAINT copropiedad_propietario_id_inmueble_id_key UNIQUE (propietario_id, inmueble_id);


--
-- Name: inmuebles inmuebles_pkey; Type: CONSTRAINT; Schema: public; Owner: alquiler_user
--

ALTER TABLE ONLY public.inmuebles
    ADD CONSTRAINT inmuebles_pkey PRIMARY KEY (id);


--
-- Name: inquilinos inquilinos_pkey; Type: CONSTRAINT; Schema: public; Owner: alquiler_user
--

ALTER TABLE ONLY public.inquilinos
    ADD CONSTRAINT inquilinos_pkey PRIMARY KEY (id);


--
-- Name: propietarios propietarios_dni_cuit_key; Type: CONSTRAINT; Schema: public; Owner: alquiler_user
--

ALTER TABLE ONLY public.propietarios
    ADD CONSTRAINT propietarios_dni_cuit_key UNIQUE (dni_cuit);


--
-- Name: propietarios propietarios_pkey; Type: CONSTRAINT; Schema: public; Owner: alquiler_user
--

ALTER TABLE ONLY public.propietarios
    ADD CONSTRAINT propietarios_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: alquiler_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: alquiler_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_audit_log_created; Type: INDEX; Schema: public; Owner: alquiler_user
--

CREATE INDEX idx_audit_log_created ON public.audit_log USING btree (created_at);


--
-- Name: idx_audit_log_table; Type: INDEX; Schema: public; Owner: alquiler_user
--

CREATE INDEX idx_audit_log_table ON public.audit_log USING btree (table_name);


--
-- Name: idx_audit_log_user; Type: INDEX; Schema: public; Owner: alquiler_user
--

CREATE INDEX idx_audit_log_user ON public.audit_log USING btree (user_id);


--
-- Name: idx_cobros_contrato; Type: INDEX; Schema: public; Owner: alquiler_user
--

CREATE INDEX idx_cobros_contrato ON public.cobros USING btree (contrato_id);


--
-- Name: idx_cobros_fecha; Type: INDEX; Schema: public; Owner: alquiler_user
--

CREATE INDEX idx_cobros_fecha ON public.cobros USING btree (fecha_cobro);


--
-- Name: idx_comprobantes_cobro; Type: INDEX; Schema: public; Owner: alquiler_user
--

CREATE INDEX idx_comprobantes_cobro ON public.comprobantes USING btree (cobro_id);


--
-- Name: idx_comprobantes_propietario; Type: INDEX; Schema: public; Owner: alquiler_user
--

CREATE INDEX idx_comprobantes_propietario ON public.comprobantes USING btree (propietario_id);


--
-- Name: idx_contratos_fechas; Type: INDEX; Schema: public; Owner: alquiler_user
--

CREATE INDEX idx_contratos_fechas ON public.contratos USING btree (fecha_inicio, fecha_fin);


--
-- Name: idx_contratos_inmueble; Type: INDEX; Schema: public; Owner: alquiler_user
--

CREATE INDEX idx_contratos_inmueble ON public.contratos USING btree (inmueble_id);


--
-- Name: idx_contratos_inquilino; Type: INDEX; Schema: public; Owner: alquiler_user
--

CREATE INDEX idx_contratos_inquilino ON public.contratos USING btree (inquilino_id);


--
-- Name: idx_copropiedad_inmueble; Type: INDEX; Schema: public; Owner: alquiler_user
--

CREATE INDEX idx_copropiedad_inmueble ON public.copropiedad USING btree (inmueble_id);


--
-- Name: idx_copropiedad_propietario; Type: INDEX; Schema: public; Owner: alquiler_user
--

CREATE INDEX idx_copropiedad_propietario ON public.copropiedad USING btree (propietario_id);


--
-- Name: idx_inmuebles_categoria; Type: INDEX; Schema: public; Owner: alquiler_user
--

CREATE INDEX idx_inmuebles_categoria ON public.inmuebles USING btree (categoria);


--
-- Name: idx_inmuebles_direccion; Type: INDEX; Schema: public; Owner: alquiler_user
--

CREATE INDEX idx_inmuebles_direccion ON public.inmuebles USING btree (direccion);


--
-- Name: idx_inmuebles_estado; Type: INDEX; Schema: public; Owner: alquiler_user
--

CREATE INDEX idx_inmuebles_estado ON public.inmuebles USING btree (estado);


--
-- Name: idx_propietarios_dni_cuit; Type: INDEX; Schema: public; Owner: alquiler_user
--

CREATE INDEX idx_propietarios_dni_cuit ON public.propietarios USING btree (dni_cuit);


--
-- Name: idx_users_email; Type: INDEX; Schema: public; Owner: alquiler_user
--

CREATE INDEX idx_users_email ON public.users USING btree (email);


--
-- Name: idx_users_role; Type: INDEX; Schema: public; Owner: alquiler_user
--

CREATE INDEX idx_users_role ON public.users USING btree (role);


--
-- Name: cobros update_cobros_updated_at; Type: TRIGGER; Schema: public; Owner: alquiler_user
--

CREATE TRIGGER update_cobros_updated_at BEFORE UPDATE ON public.cobros FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: contratos update_contratos_updated_at; Type: TRIGGER; Schema: public; Owner: alquiler_user
--

CREATE TRIGGER update_contratos_updated_at BEFORE UPDATE ON public.contratos FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: inmuebles update_inmuebles_updated_at; Type: TRIGGER; Schema: public; Owner: alquiler_user
--

CREATE TRIGGER update_inmuebles_updated_at BEFORE UPDATE ON public.inmuebles FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: inquilinos update_inquilinos_updated_at; Type: TRIGGER; Schema: public; Owner: alquiler_user
--

CREATE TRIGGER update_inquilinos_updated_at BEFORE UPDATE ON public.inquilinos FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: propietarios update_propietarios_updated_at; Type: TRIGGER; Schema: public; Owner: alquiler_user
--

CREATE TRIGGER update_propietarios_updated_at BEFORE UPDATE ON public.propietarios FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: users update_users_updated_at; Type: TRIGGER; Schema: public; Owner: alquiler_user
--

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: audit_log audit_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: alquiler_user
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: cobros cobros_contrato_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: alquiler_user
--

ALTER TABLE ONLY public.cobros
    ADD CONSTRAINT cobros_contrato_id_fkey FOREIGN KEY (contrato_id) REFERENCES public.contratos(id) ON DELETE RESTRICT;


--
-- Name: comprobantes comprobantes_cobro_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: alquiler_user
--

ALTER TABLE ONLY public.comprobantes
    ADD CONSTRAINT comprobantes_cobro_id_fkey FOREIGN KEY (cobro_id) REFERENCES public.cobros(id) ON DELETE RESTRICT;


--
-- Name: comprobantes comprobantes_propietario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: alquiler_user
--

ALTER TABLE ONLY public.comprobantes
    ADD CONSTRAINT comprobantes_propietario_id_fkey FOREIGN KEY (propietario_id) REFERENCES public.propietarios(id) ON DELETE RESTRICT;


--
-- Name: contratos contratos_inmueble_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: alquiler_user
--

ALTER TABLE ONLY public.contratos
    ADD CONSTRAINT contratos_inmueble_id_fkey FOREIGN KEY (inmueble_id) REFERENCES public.inmuebles(id) ON DELETE RESTRICT;


--
-- Name: contratos contratos_inquilino_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: alquiler_user
--

ALTER TABLE ONLY public.contratos
    ADD CONSTRAINT contratos_inquilino_id_fkey FOREIGN KEY (inquilino_id) REFERENCES public.inquilinos(id) ON DELETE RESTRICT;


--
-- Name: copropiedad copropiedad_inmueble_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: alquiler_user
--

ALTER TABLE ONLY public.copropiedad
    ADD CONSTRAINT copropiedad_inmueble_id_fkey FOREIGN KEY (inmueble_id) REFERENCES public.inmuebles(id) ON DELETE RESTRICT;


--
-- Name: copropiedad copropiedad_propietario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: alquiler_user
--

ALTER TABLE ONLY public.copropiedad
    ADD CONSTRAINT copropiedad_propietario_id_fkey FOREIGN KEY (propietario_id) REFERENCES public.propietarios(id) ON DELETE RESTRICT;


--
-- PostgreSQL database dump complete
--

\unrestrict aDlKjllu4le9ubvTEOeJLLYT8f5htBQrGYZWXRJMQUx5SSuPQ3R8dqpkmBsNfLR

