--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: propar_db_owner; Tablespace: 
--

CREATE TABLE auth_group (
    id integer NOT NULL,
    name character varying(80) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO propar_db_owner;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: propar_db_owner
--

CREATE SEQUENCE auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_id_seq OWNER TO propar_db_owner;

--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: propar_db_owner
--

ALTER SEQUENCE auth_group_id_seq OWNED BY auth_group.id;


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: propar_db_owner; Tablespace: 
--

CREATE TABLE auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO propar_db_owner;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: propar_db_owner
--

CREATE SEQUENCE auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_permissions_id_seq OWNER TO propar_db_owner;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: propar_db_owner
--

ALTER SEQUENCE auth_group_permissions_id_seq OWNED BY auth_group_permissions.id;


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: propar_db_owner; Tablespace: 
--

CREATE TABLE auth_permission (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO propar_db_owner;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: propar_db_owner
--

CREATE SEQUENCE auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_permission_id_seq OWNER TO propar_db_owner;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: propar_db_owner
--

ALTER SEQUENCE auth_permission_id_seq OWNED BY auth_permission.id;


--
-- Name: auth_user; Type: TABLE; Schema: public; Owner: propar_db_owner; Tablespace: 
--

CREATE TABLE auth_user (
    id integer NOT NULL,
    username character varying(30) NOT NULL,
    first_name character varying(30) NOT NULL,
    last_name character varying(30) NOT NULL,
    email character varying(75) NOT NULL,
    password character varying(128) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    is_superuser boolean NOT NULL,
    last_login timestamp with time zone NOT NULL,
    date_joined timestamp with time zone NOT NULL
);


ALTER TABLE public.auth_user OWNER TO propar_db_owner;

--
-- Name: auth_user_groups; Type: TABLE; Schema: public; Owner: propar_db_owner; Tablespace: 
--

CREATE TABLE auth_user_groups (
    id integer NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.auth_user_groups OWNER TO propar_db_owner;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: propar_db_owner
--

CREATE SEQUENCE auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_user_groups_id_seq OWNER TO propar_db_owner;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: propar_db_owner
--

ALTER SEQUENCE auth_user_groups_id_seq OWNED BY auth_user_groups.id;


--
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: public; Owner: propar_db_owner
--

CREATE SEQUENCE auth_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_user_id_seq OWNER TO propar_db_owner;

--
-- Name: auth_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: propar_db_owner
--

ALTER SEQUENCE auth_user_id_seq OWNED BY auth_user.id;


--
-- Name: auth_user_user_permissions; Type: TABLE; Schema: public; Owner: propar_db_owner; Tablespace: 
--

CREATE TABLE auth_user_user_permissions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_user_user_permissions OWNER TO propar_db_owner;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: propar_db_owner
--

CREATE SEQUENCE auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_user_user_permissions_id_seq OWNER TO propar_db_owner;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: propar_db_owner
--

ALTER SEQUENCE auth_user_user_permissions_id_seq OWNED BY auth_user_user_permissions.id;


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: propar_db_owner; Tablespace: 
--

CREATE TABLE django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    user_id integer NOT NULL,
    content_type_id integer,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO propar_db_owner;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: propar_db_owner
--

CREATE SEQUENCE django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_admin_log_id_seq OWNER TO propar_db_owner;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: propar_db_owner
--

ALTER SEQUENCE django_admin_log_id_seq OWNED BY django_admin_log.id;


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: propar_db_owner; Tablespace: 
--

CREATE TABLE django_content_type (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO propar_db_owner;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: propar_db_owner
--

CREATE SEQUENCE django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_content_type_id_seq OWNER TO propar_db_owner;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: propar_db_owner
--

ALTER SEQUENCE django_content_type_id_seq OWNED BY django_content_type.id;


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: propar_db_owner; Tablespace: 
--

CREATE TABLE django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO propar_db_owner;

--
-- Name: principal_cliente; Type: TABLE; Schema: public; Owner: propar_db_owner; Tablespace: 
--

CREATE TABLE principal_cliente (
    id integer NOT NULL,
    nombres character varying(255) NOT NULL,
    apellidos character varying(255) NOT NULL,
    fecha_nacimiento date NOT NULL,
    cedula character varying(8) NOT NULL,
    ruc character varying(255) NOT NULL,
    sexo character varying(1) NOT NULL,
    estado_civil character varying(1) NOT NULL,
    direccion_particular character varying(255) NOT NULL,
    direccion_cobro character varying(255) NOT NULL,
    telefono_particular character varying(255) NOT NULL,
    telefono_laboral character varying(255) NOT NULL,
    celular_1 character varying(255) NOT NULL,
    celular_2 character varying(255) NOT NULL,
    nombre_conyuge character varying(255) NOT NULL,
    deuda_contraida bigint
);


ALTER TABLE public.principal_cliente OWNER TO propar_db_owner;

--
-- Name: principal_cliente_id_seq; Type: SEQUENCE; Schema: public; Owner: propar_db_owner
--

CREATE SEQUENCE principal_cliente_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.principal_cliente_id_seq OWNER TO propar_db_owner;

--
-- Name: principal_cliente_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: propar_db_owner
--

ALTER SEQUENCE principal_cliente_id_seq OWNED BY principal_cliente.id;


--
-- Name: principal_cobrador; Type: TABLE; Schema: public; Owner: propar_db_owner; Tablespace: 
--

CREATE TABLE principal_cobrador (
    id integer NOT NULL,
    nombres character varying(255) NOT NULL,
    apellidos character varying(255) NOT NULL,
    cedula character varying(8) NOT NULL,
    direccion character varying(255) NOT NULL,
    telefono_particular character varying(255) NOT NULL,
    celular_1 character varying(255) NOT NULL,
    fecha_ingreso date NOT NULL
);


ALTER TABLE public.principal_cobrador OWNER TO propar_db_owner;

--
-- Name: principal_cobrador_id_seq; Type: SEQUENCE; Schema: public; Owner: propar_db_owner
--

CREATE SEQUENCE principal_cobrador_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.principal_cobrador_id_seq OWNER TO propar_db_owner;

--
-- Name: principal_cobrador_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: propar_db_owner
--

ALTER SEQUENCE principal_cobrador_id_seq OWNED BY principal_cobrador.id;


--
-- Name: principal_fraccion; Type: TABLE; Schema: public; Owner: propar_db_owner; Tablespace: 
--

CREATE TABLE principal_fraccion (
    id integer NOT NULL,
    nombre character varying(255) NOT NULL,
    ubicacion character varying(255) NOT NULL,
    propietario_id integer NOT NULL,
    cantidad_manzanas integer NOT NULL,
    cantidad_lotes integer NOT NULL,
    distrito character varying(255) NOT NULL,
    finca character varying(255) NOT NULL,
    aprobacion_municipal_nro character varying(255) NOT NULL,
    fecha_aprobacion date,
    superficie_total numeric(8,2)
);


ALTER TABLE public.principal_fraccion OWNER TO propar_db_owner;

--
-- Name: principal_fraccion_id_seq; Type: SEQUENCE; Schema: public; Owner: propar_db_owner
--

CREATE SEQUENCE principal_fraccion_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.principal_fraccion_id_seq OWNER TO propar_db_owner;

--
-- Name: principal_fraccion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: propar_db_owner
--

ALTER SEQUENCE principal_fraccion_id_seq OWNED BY principal_fraccion.id;


--
-- Name: principal_lote; Type: TABLE; Schema: public; Owner: propar_db_owner; Tablespace: 
--

CREATE TABLE principal_lote (
    id integer NOT NULL,
    manzana_id integer NOT NULL,
    nro_lote integer NOT NULL,
    precio_contado integer NOT NULL,
    precio_credito integer NOT NULL,
    precio_de_cuota integer NOT NULL,
    superficie numeric(8,2) NOT NULL,
    cuenta_corriente_catastral character varying(255) NOT NULL,
    boleto_nro integer,
    estado character varying(1) NOT NULL
);


ALTER TABLE public.principal_lote OWNER TO propar_db_owner;

--
-- Name: principal_lote_id_seq; Type: SEQUENCE; Schema: public; Owner: propar_db_owner
--

CREATE SEQUENCE principal_lote_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.principal_lote_id_seq OWNER TO propar_db_owner;

--
-- Name: principal_lote_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: propar_db_owner
--

ALTER SEQUENCE principal_lote_id_seq OWNED BY principal_lote.id;


--
-- Name: principal_manzana; Type: TABLE; Schema: public; Owner: propar_db_owner; Tablespace: 
--

CREATE TABLE principal_manzana (
    id integer NOT NULL,
    nro_manzana integer NOT NULL,
    cantidad_lotes integer,
    fraccion_id integer NOT NULL
);


ALTER TABLE public.principal_manzana OWNER TO propar_db_owner;

--
-- Name: principal_manzana_id_seq; Type: SEQUENCE; Schema: public; Owner: propar_db_owner
--

CREATE SEQUENCE principal_manzana_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.principal_manzana_id_seq OWNER TO propar_db_owner;

--
-- Name: principal_manzana_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: propar_db_owner
--

ALTER SEQUENCE principal_manzana_id_seq OWNED BY principal_manzana.id;


--
-- Name: principal_plandepagos; Type: TABLE; Schema: public; Owner: propar_db_owner; Tablespace: 
--

CREATE TABLE principal_plandepagos (
    id integer NOT NULL,
    nombre_del_plan character varying(255) NOT NULL,
    tipo_de_plan boolean NOT NULL,
    cantidad_de_cuotas integer
);


ALTER TABLE public.principal_plandepagos OWNER TO propar_db_owner;

--
-- Name: principal_plandepagos_id_seq; Type: SEQUENCE; Schema: public; Owner: propar_db_owner
--

CREATE SEQUENCE principal_plandepagos_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.principal_plandepagos_id_seq OWNER TO propar_db_owner;

--
-- Name: principal_plandepagos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: propar_db_owner
--

ALTER SEQUENCE principal_plandepagos_id_seq OWNED BY principal_plandepagos.id;


--
-- Name: principal_plandevendedores; Type: TABLE; Schema: public; Owner: propar_db_owner; Tablespace: 
--

CREATE TABLE principal_plandevendedores (
    id integer NOT NULL,
    nombre_del_plan character varying(255) NOT NULL
);


ALTER TABLE public.principal_plandevendedores OWNER TO propar_db_owner;

--
-- Name: principal_plandevendedores_id_seq; Type: SEQUENCE; Schema: public; Owner: propar_db_owner
--

CREATE SEQUENCE principal_plandevendedores_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.principal_plandevendedores_id_seq OWNER TO propar_db_owner;

--
-- Name: principal_plandevendedores_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: propar_db_owner
--

ALTER SEQUENCE principal_plandevendedores_id_seq OWNED BY principal_plandevendedores.id;


--
-- Name: principal_propietario; Type: TABLE; Schema: public; Owner: propar_db_owner; Tablespace: 
--

CREATE TABLE principal_propietario (
    id integer NOT NULL,
    nombres character varying(255) NOT NULL,
    apellidos character varying(255) NOT NULL,
    fecha_nacimiento date,
    fecha_ingreso date NOT NULL,
    cedula character varying(8) NOT NULL,
    ruc character varying(255) NOT NULL,
    direccion_particular character varying(255) NOT NULL,
    telefono_particular character varying(255) NOT NULL,
    celular_1 character varying(255) NOT NULL,
    celular_2 character varying(255) NOT NULL
);


ALTER TABLE public.principal_propietario OWNER TO propar_db_owner;

--
-- Name: principal_propietario_id_seq; Type: SEQUENCE; Schema: public; Owner: propar_db_owner
--

CREATE SEQUENCE principal_propietario_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.principal_propietario_id_seq OWNER TO propar_db_owner;

--
-- Name: principal_propietario_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: propar_db_owner
--

ALTER SEQUENCE principal_propietario_id_seq OWNED BY principal_propietario.id;


--
-- Name: principal_vendedor; Type: TABLE; Schema: public; Owner: propar_db_owner; Tablespace: 
--

CREATE TABLE principal_vendedor (
    id integer NOT NULL,
    nombres character varying(255) NOT NULL,
    apellidos character varying(255) NOT NULL,
    cedula character varying(8) NOT NULL,
    direccion character varying(255) NOT NULL,
    telefono character varying(255) NOT NULL,
    celular_1 character varying(255) NOT NULL,
    fecha_ingreso date NOT NULL
);


ALTER TABLE public.principal_vendedor OWNER TO propar_db_owner;

--
-- Name: principal_vendedor_id_seq; Type: SEQUENCE; Schema: public; Owner: propar_db_owner
--

CREATE SEQUENCE principal_vendedor_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.principal_vendedor_id_seq OWNER TO propar_db_owner;

--
-- Name: principal_vendedor_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: propar_db_owner
--

ALTER SEQUENCE principal_vendedor_id_seq OWNED BY principal_vendedor.id;


--
-- Name: principal_venta; Type: TABLE; Schema: public; Owner: propar_db_owner; Tablespace: 
--

CREATE TABLE principal_venta (
    id integer NOT NULL,
    lote_id integer NOT NULL,
    fecha_de_venta date NOT NULL,
    cliente_id integer NOT NULL,
    vendedor_id integer NOT NULL,
    plan_de_vendedor_id integer NOT NULL,
    plan_de_pago_id integer NOT NULL,
    entrega_inicial bigint NOT NULL,
    precio_de_cuota bigint NOT NULL,
    cuota_de_refuerzo bigint NOT NULL,
    precio_final_de_venta bigint NOT NULL,
    fecha_primer_vencimiento date NOT NULL,
    pagos_realizados integer
);


ALTER TABLE public.principal_venta OWNER TO propar_db_owner;

--
-- Name: principal_venta_id_seq; Type: SEQUENCE; Schema: public; Owner: propar_db_owner
--

CREATE SEQUENCE principal_venta_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.principal_venta_id_seq OWNER TO propar_db_owner;

--
-- Name: principal_venta_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: propar_db_owner
--

ALTER SEQUENCE principal_venta_id_seq OWNED BY principal_venta.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY auth_group ALTER COLUMN id SET DEFAULT nextval('auth_group_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('auth_group_permissions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY auth_permission ALTER COLUMN id SET DEFAULT nextval('auth_permission_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY auth_user ALTER COLUMN id SET DEFAULT nextval('auth_user_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY auth_user_groups ALTER COLUMN id SET DEFAULT nextval('auth_user_groups_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY auth_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('auth_user_user_permissions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY django_admin_log ALTER COLUMN id SET DEFAULT nextval('django_admin_log_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY django_content_type ALTER COLUMN id SET DEFAULT nextval('django_content_type_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY principal_cliente ALTER COLUMN id SET DEFAULT nextval('principal_cliente_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY principal_cobrador ALTER COLUMN id SET DEFAULT nextval('principal_cobrador_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY principal_fraccion ALTER COLUMN id SET DEFAULT nextval('principal_fraccion_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY principal_lote ALTER COLUMN id SET DEFAULT nextval('principal_lote_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY principal_manzana ALTER COLUMN id SET DEFAULT nextval('principal_manzana_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY principal_plandepagos ALTER COLUMN id SET DEFAULT nextval('principal_plandepagos_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY principal_plandevendedores ALTER COLUMN id SET DEFAULT nextval('principal_plandevendedores_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY principal_propietario ALTER COLUMN id SET DEFAULT nextval('principal_propietario_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY principal_vendedor ALTER COLUMN id SET DEFAULT nextval('principal_vendedor_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY principal_venta ALTER COLUMN id SET DEFAULT nextval('principal_venta_id_seq'::regclass);


--
-- Name: auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions_group_id_permission_id_key; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_key UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission_content_type_id_codename_key; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_key UNIQUE (content_type_id, codename);


--
-- Name: auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups_user_id_group_id_key; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_group_id_key UNIQUE (user_id, group_id);


--
-- Name: auth_user_pkey; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions_user_id_permission_id_key; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_permission_id_key UNIQUE (user_id, permission_id);


--
-- Name: auth_user_username_key; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);


--
-- Name: django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type_app_label_model_key; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_key UNIQUE (app_label, model);


--
-- Name: django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: principal_cliente_pkey; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY principal_cliente
    ADD CONSTRAINT principal_cliente_pkey PRIMARY KEY (id);


--
-- Name: principal_cobrador_pkey; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY principal_cobrador
    ADD CONSTRAINT principal_cobrador_pkey PRIMARY KEY (id);


--
-- Name: principal_fraccion_pkey; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY principal_fraccion
    ADD CONSTRAINT principal_fraccion_pkey PRIMARY KEY (id);


--
-- Name: principal_lote_manzana_id_nro_lote_key; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY principal_lote
    ADD CONSTRAINT principal_lote_manzana_id_nro_lote_key UNIQUE (manzana_id, nro_lote);


--
-- Name: principal_lote_pkey; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY principal_lote
    ADD CONSTRAINT principal_lote_pkey PRIMARY KEY (id);


--
-- Name: principal_manzana_fraccion_id_nro_manzana_key; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY principal_manzana
    ADD CONSTRAINT principal_manzana_fraccion_id_nro_manzana_key UNIQUE (fraccion_id, nro_manzana);


--
-- Name: principal_manzana_pkey; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY principal_manzana
    ADD CONSTRAINT principal_manzana_pkey PRIMARY KEY (id);


--
-- Name: principal_plandepagos_pkey; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY principal_plandepagos
    ADD CONSTRAINT principal_plandepagos_pkey PRIMARY KEY (id);


--
-- Name: principal_plandevendedores_pkey; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY principal_plandevendedores
    ADD CONSTRAINT principal_plandevendedores_pkey PRIMARY KEY (id);


--
-- Name: principal_propietario_pkey; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY principal_propietario
    ADD CONSTRAINT principal_propietario_pkey PRIMARY KEY (id);


--
-- Name: principal_vendedor_pkey; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY principal_vendedor
    ADD CONSTRAINT principal_vendedor_pkey PRIMARY KEY (id);


--
-- Name: principal_venta_pkey; Type: CONSTRAINT; Schema: public; Owner: propar_db_owner; Tablespace: 
--

ALTER TABLE ONLY principal_venta
    ADD CONSTRAINT principal_venta_pkey PRIMARY KEY (id);


--
-- Name: principal_fraccion_propietario_id; Type: INDEX; Schema: public; Owner: propar_db_owner; Tablespace: 
--

CREATE INDEX principal_fraccion_propietario_id ON principal_fraccion USING btree (propietario_id);


--
-- Name: principal_lote_manzana_id; Type: INDEX; Schema: public; Owner: propar_db_owner; Tablespace: 
--

CREATE INDEX principal_lote_manzana_id ON principal_lote USING btree (manzana_id);


--
-- Name: principal_manzana_fraccion_id; Type: INDEX; Schema: public; Owner: propar_db_owner; Tablespace: 
--

CREATE INDEX principal_manzana_fraccion_id ON principal_manzana USING btree (fraccion_id);


--
-- Name: auth_group_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: content_type_id_refs_id_728de91f; Type: FK CONSTRAINT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT content_type_id_refs_id_728de91f FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log_content_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_fkey FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: group_id_refs_id_3cea63fe; Type: FK CONSTRAINT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT group_id_refs_id_3cea63fe FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: principal_fraccion_propietario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY principal_fraccion
    ADD CONSTRAINT principal_fraccion_propietario_id_fkey FOREIGN KEY (propietario_id) REFERENCES principal_propietario(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: principal_manzana_fraccion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY principal_manzana
    ADD CONSTRAINT principal_manzana_fraccion_id_fkey FOREIGN KEY (fraccion_id) REFERENCES principal_fraccion(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: principal_venta_cliente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY principal_venta
    ADD CONSTRAINT principal_venta_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES principal_cliente(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: principal_venta_plan_de_pago_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY principal_venta
    ADD CONSTRAINT principal_venta_plan_de_pago_id_fkey FOREIGN KEY (plan_de_pago_id) REFERENCES principal_plandepagos(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: principal_venta_plan_de_vendedor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY principal_venta
    ADD CONSTRAINT principal_venta_plan_de_vendedor_id_fkey FOREIGN KEY (plan_de_vendedor_id) REFERENCES principal_plandevendedores(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: principal_venta_vendedor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY principal_venta
    ADD CONSTRAINT principal_venta_vendedor_id_fkey FOREIGN KEY (vendedor_id) REFERENCES principal_vendedor(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: user_id_refs_id_831107f1; Type: FK CONSTRAINT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT user_id_refs_id_831107f1 FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: user_id_refs_id_f2045483; Type: FK CONSTRAINT; Schema: public; Owner: propar_db_owner
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT user_id_refs_id_f2045483 FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: public; Type: ACL; Schema: -; Owner: propar_db_owner
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM propar_db_owner;
GRANT ALL ON SCHEMA public TO propar_db_owner;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

