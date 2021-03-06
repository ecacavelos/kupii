-- DEJAR SIEMPRE ESTO EN LA PARTE DE ARRIBA COMO EJEMPLO PARA REEMPLAZAR!!! ORDEN DESCENDENTE POR FECHA --
/* INSTANCIAS DE BASES DE DATOS DE KUPII:
  1- CBI-DEV: Base de datos ubicada en el servidor de desarrollo de CBI.
  2- PROPAR: Base de datos de produccion, del sistema de lotes de PROPAR.
  3- KUPII-DEMO:  Base de datos demo en azure del sistema de lotes KUPII.
  4- GRUPO-MV: Base de datos en amazon del grupo MV
 IMPORTANTE: El que hace el deploy, debe acualizar los estados, de las cabeceras de los querys a EJECUTADO, de las respectivas instacias de BD
 */


-- EJEMPLO: ##/##/#### ##:## - Desarrollador - BD: EJECUTADO O NO - BD: EJECUTADO O NO  - BD: EJECUTADO O NO
/* Breve descripcion de lo que hace el query */
-- query en cuestion --
-- agregar siempre despues de este ejemplo el siguiente cambio --

--################################### Hasta acá proximo tag ##########################################################--
-- 31/07/2017 15:00 - Jose Duarte
-- BASE DE DATOS:        ESTADO:
-- CBI-DEV:           NO EJECUTADO
-- GRUPO-MV:          NO EJECUTADO
-- Propar:            EJECUTADO

--actualizacion de la descripcion de tipo de mejora
update table principal_tipomejora set descripcion = 'BALDIO' WHERE id = 3;
--agreggamos demanda a los lotes
ALTER TABLE principal_lote ADD COLUMN demanda character varying(2);

--################################### Hasta acá proximo tag ##########################################################--
-- 21/07/2017 15:00 - Franco Albertini
-- BASE DE DATOS:        ESTADO:
-- CBI-DEV:           NO EJECUTADO
-- GRUPO-MV:          NO EJECUTADO
-- Propar:            EJECUTADO
ALTER TABLE principal_transaccion ADD COLUMN lote_id integer;

--################################### Hasta Acá TAG v_0.1.454 ########################################################--

-- 18/07/2017 14:00 - Jose Duarte
-- BASE DE DATOS:        ESTADO:
-- CBI-DEV:           NO EJECUTADO
-- GRUPO-MV:          NO EJECUTADO
-- Propar:            EJECUTADO

 --creamos una tabla tipo de mejora
CREATE TABLE principal_tipomejora
(
  id serial NOT NULL,
  descripcion character varying(60) NOT NULL
);

 --agregamos una clave primaria
ALTER TABLE principal_tipomejora ADD PRIMARY KEY(id);

--agregamos el id de mejora dentro de la tabla lote
ALTER TABLE principal_lote ADD COLUMN mejora_id integer;
--agregamos el constraint dentro de lote para la mejora
ALTER TABLE principal_lote ADD
CONSTRAINT principal_lote_mejoras_id_fkey FOREIGN KEY (mejora_id)
      REFERENCES principal_tipomejora (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;

--realizamos el insert de los tipos de mejora para los lotes
insert into principal_tipomejora values (1,'ALAMBRADO');
insert into principal_tipomejora values (2,'CASA');
insert into principal_tipomejora values (3,'VALDIO');
insert into principal_tipomejora values (4,'TINGLADO');
insert into principal_tipomejora values (5,'EDIFICIO');
insert into principal_tipomejora values (6,'MOTEL');



-- 17/07/2017 17:00 - Jose Duarte
-- BASE DE DATOS:        ESTADO:
-- CBI-DEV:           NO EJECUTADO
-- GRUPO-MV:          NO EJECUTADO
-- Propar:            EJECUTADO
ALTER TABLE principal_cliente ADD COLUMN
email character varying(100);

-- 09/06/2017 15:00 - Franco Albertini
-- BASE DE DATOS:        ESTADO:
-- CBI-DEV:           NO EJECUTADO
-- GRUPO-MV:          NO EJECUTADO
-- Propar:               EJECUTADO

/* Se crea la tabla motivos contactos y se carga la tabla */
CREATE TABLE public.motivos_contacto
(
    id SERIAL NOT NULL,
    descripcion character varying(100) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT motivos_contacto_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.motivos_contacto
    OWNER to propar_db_user;

INSERT INTO public.motivos_contacto (descripcion) VALUES ('Morosidad');
INSERT INTO public.motivos_contacto (descripcion) VALUES ('Demanda');
INSERT INTO public.motivos_contacto (descripcion) VALUES ('Oferta de Promocion');


/* Se crea la tabla tipo de contacto y se carga la table */
CREATE TABLE public.tipo_contacto
(
    id SERIAL NOT NULL,
    descripcion character varying(100) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT tipo_contacto_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.tipo_contacto
    OWNER to propar_db_user;

INSERT INTO public.tipo_contacto (descripcion) VALUES ('Llamada');
INSERT INTO public.tipo_contacto (descripcion) VALUES ('Mail');
INSERT INTO public.tipo_contacto (descripcion) VALUES ('Mensaje WhatsApp');
INSERT INTO public.tipo_contacto (descripcion) VALUES ('Mensaje Texto (SMS)');
INSERT INTO public.tipo_contacto (descripcion) VALUES ('Reunion Oficina Cliente');
INSERT INTO public.tipo_contacto (descripcion) VALUES ('Reunion Oficina Propar');
INSERT INTO public.tipo_contacto (descripcion) VALUES ('Reunion Residencia Cliente');

/* Se crea la tabla contactos */
CREATE TABLE public.contactos
(
    id SERIAL NOT NULL,
    lote_id integer NOT NULL,
    cliente_id integer NOT NULL,
    tipo_contacto_id integer NOT NULL,
    motivo_contacto_id integer NOT NULL,
    remitente_usuario_id integer NOT NULL,
    fecha_contacto timestamp without time zone NOT NULL,
    numero_direccion_contactado text COLLATE pg_catalog."default" NOT NULL,
    mensaje_enviado text COLLATE pg_catalog."default" NOT NULL,
    respondido boolean NOT NULL,
    fecha_respuesta timestamp without time zone,
    tipo_respuesta_id integer,
    mensaje_respuesta text COLLATE pg_catalog."default",
    proximo_contacto timestamp without time zone,
    comentarios_gerencia text COLLATE pg_catalog."default",
    recipiente character varying(100) COLLATE pg_catalog."default",
    CONSTRAINT contactos_pkey PRIMARY KEY (id),
    CONSTRAINT contactos_clientes_fk FOREIGN KEY (cliente_id)
        REFERENCES public.principal_cliente (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT contactos_lotes_fk FOREIGN KEY (lote_id)
        REFERENCES public.principal_lote (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT contactos_motivos_contacto_fk FOREIGN KEY (motivo_contacto_id)
        REFERENCES public.motivos_contacto (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT contactos_tipos_contacto_fk FOREIGN KEY (tipo_contacto_id)
        REFERENCES public.tipo_contacto (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT contactos_usuarios_fk FOREIGN KEY (remitente_usuario_id)
        REFERENCES public.auth_user (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.contactos
    OWNER to propar_db_user;

/* Se añade el content type para los permisos */
INSERT INTO public.django_content_type (name, app_label, model) VALUES ('tipo contacto', 'tipo_contacto', 'tipocontacto');
INSERT INTO public.django_content_type (name, app_label, model) VALUES ('contacto', 'contactos', 'contacto');
INSERT INTO public.django_content_type (name, app_label, model) VALUES ('motivo contacto', 'motivo_contacto', 'motivocontacto');

--################################### Hasta Acá TAG v_0.1.453 ########################################################--

/* Se agrega campos de coordenadas para sucursal */
ALTER TABLE principal_coordenadasfactura ADD COLUMN sucursal_1x double precision;
ALTER TABLE principal_coordenadasfactura ADD COLUMN sucursal_1y double precision;
ALTER TABLE principal_coordenadasfactura ADD COLUMN sucursal_2x double precision;
ALTER TABLE principal_coordenadasfactura ADD COLUMN sucursal_2y double precision;
/* Se agregan valores a los campos agregados */
UPDATE principal_coordenadasfactura SET sucursal_1x = 14, sucursal_1y = 1.3, sucursal_2x = 14, sucursal_2y = 15.2 ;

/* Se convierte el date de fecha de pago a timestamp */
ALTER TABLE principal_pagodecuotas
   ALTER COLUMN fecha_de_pago TYPE timestamp without time zone;

/*Se agraga pk a tabla de movimientos*/
ALTER TABLE principal_pagodecuotas
  ADD CONSTRAINT pk_pagodecuotas PRIMARY KEY(id);


/* Para borrar movimientos con id duplicados */
delete from principal_pagodecuotas
    where exists (select 1
                  from principal_pagodecuotas t2
                  where t2.id = principal_pagodecuotas.id and
                  t2.ctid > principal_pagodecuotas.ctid
                 );

/* Para encontrar los movimientos con id duplicados */
SELECT id, count(*)
from principal_pagodecuotas
group by id
HAVING count(*) > 1;

-- 24/02/2017 16:50 - Franco Albertini - CBI-DEV: NO EJECUTADO - PROPAR: EJECUTADO  - GRUPO-MV: EJECUTADO
/* Este query añade la columna seleccioanado a la tabla de logos */
ALTER TABLE principal_logdelogos ADD COLUMN seleccionado boolean;
UPDATE principal_logdelogos SET seleccionado = false;


-- 23/01/2017 18:08 - Franco Albertini - CBI-DEV: NO EJECUTADO - PROPAR: EJECUTADO  - GRUPO-MV: EJECUTADO
/* Este query añade los campos de las coordenadas para la copia nro 3 de la factura */
ALTER TABLE principal_coordenadasfactura ADD COLUMN fecha_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN fecha_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN contado_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN contado_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN credito_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN credito_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN fraccion_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN fraccion_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN nombre_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN nombre_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN manzana_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN manzana_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN lote_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN lote_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN ruc_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN ruc_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN telefono_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN telefono_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN direccion_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN direccion_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN superficie_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN superficie_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN cta_cte_ctral_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN cta_cte_ctral_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN cantidad_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN cantidad_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN descripcion_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN descripcion_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN precio_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN precio_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN exentas_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN exentas_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN iva5_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN iva5_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN iva10_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN iva10_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN sub_exentas_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN sub_exentas_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN sub_iva5_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN sub_iva5_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN sub_iva10_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN sub_iva10_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN total_venta_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN total_venta_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN total_a_pagar_letra_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN total_a_pagar_letra_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN total_a_pagar_num_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN total_a_pagar_num_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN liq_iva5_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN liq_iva5_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN liq_iva10_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN liq_iva10_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN liq_total_iva_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN liq_total_iva_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN timbrado_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN timbrado_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN numero_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN numero_3y double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN total_a_pagar_exentas_iva5_3x double precision ;
ALTER TABLE principal_coordenadasfactura ADD COLUMN total_a_pagar_exentas_iva5_3y double precision ;

/* Este query añade la tabla de configuraciones */
CREATE TABLE principal_configuraciones
(
  id serial NOT NULL,
  copias_facturas integer,
  tipo_numeracion_manzana character varying(6),
  codigo_empresa character varying(4),
  tamanho_letra NUMERIC (99,2),
  CONSTRAINT pk_configuraciones PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE principal_configuraciones
  OWNER TO postgres;

INSERT INTO principal_configuraciones (
  copias_facturas, tipo_numeracion_manzana, codigo_empresa, tamanho_letra
) VALUES (2, 'NORMAL', 'PROP', 10.00);
INSERT INTO principal_configuraciones (
  copias_facturas, tipo_numeracion_manzana, codigo_empresa, tamanho_letra
) VALUES (3, 'ROMANA', 'VIER', 8.00);

UPDATE public.principal_coordenadasfactura
SET fecha_1x = 3.3, fecha_1y = 3.3, contado_1x = 9, contado_1y = 2.9, credito_1x = 12, credito_1y = 2.9,
  fraccion_1x = 11.7, fraccion_1y = 4.3, nombre_1x = 3.5, nombre_1y = 3.8, manzana_1x = 14.9, manzana_1y = 4.3,
  lote_1x = 18.2, lote_1y = 4.3, ruc_1x = 15.2, ruc_1y = 3.8, telefono_1x = 9, telefono_1y = 4.3, direccion_1x = 2.7,
  direccion_1y = 4.3, superficie_1x = 18.9, superficie_1y = 4.3, cta_cte_ctral_1x = 3, cta_cte_ctral_1y = 2.5,
  cantidad_1x = 1.8, cantidad_1y = 5, descripcion_1x = 2.7, descripcion_1y = 5, precio_1x = 12.2, precio_1y = 5,
  exentas_1x = 14.4, exentas_1y = 5, iva5_1x = 16.2, iva5_1y = 5, iva10_1x = 18, iva10_1y = 5, sub_exentas_1x = 14.4,
  sub_exentas_1y = 8.9, sub_iva5_1x = 16.2, sub_iva5_1y = 8.9, sub_iva10_1x = 18, sub_iva10_1y = 8.9,
  total_venta_1x = 1, total_venta_1y = 1, total_a_pagar_letra_1x = 3, total_a_pagar_letra_1y = 8.9,
  total_a_pagar_num_1x = 18, total_a_pagar_num_1y = 9.3, liq_iva5_1x = 3.7, liq_iva5_1y = 9.3, liq_iva10_1x = 8,
  liq_iva10_1y = 9.3, liq_total_iva_1x = 12.8, liq_total_iva_1y = 9.3, fecha_2x = 3.3, fecha_2y = 13.1, contado_2x = 9,
  contado_2y = 12.7, credito_2x = 12, credito_2y = 12.7, fraccion_2x = 11.7, fraccion_2y = 14.1, nombre_2x = 3.5,
  nombre_2y = 13.6, manzana_2x = 14.9, manzana_2y = 14.1, lote_2x = 18.2, lote_2y = 14.1, ruc_2x = 15.2, ruc_2y = 13.6,
  telefono_2x = 9, telefono_2y = 14.1, direccion_2x = 2.7, direccion_2y = 14.1, superficie_2x = 18.9,
  superficie_2y = 14.1, cta_cte_ctral_2x = 3, cta_cte_ctral_2y = 12.1, cantidad_2x = 1.8, cantidad_2y = 14.6,
  descripcion_2x = 2.7, descripcion_2y = 14.6, precio_2x = 12.2, precio_2y = 14.6, exentas_2x = 14.4, exentas_2y = 14.6,
  iva5_2x = 16.2, iva5_2y = 14.6, iva10_2x = 18, iva10_2y = 14.6, sub_exentas_2x = 14.4, sub_exentas_2y = 18.6,
  sub_iva5_2x = 16.2, sub_iva5_2y = 18.6, sub_iva10_2x = 18, sub_iva10_2y = 18.6, total_venta_2x = 1,
  total_venta_2y = 1, total_a_pagar_letra_2x = 3, total_a_pagar_letra_2y = 18.7, total_a_pagar_num_2x = 18,
  total_a_pagar_num_2y = 18.7, liq_iva5_2x = 3.7, liq_iva5_2y = 19, liq_iva10_2x = 8, liq_iva10_2y = 19,
  liq_total_iva_2x = 12.8, liq_total_iva_2y = 19, usuario_id = 31, timbrado_1x = null, timbrado_1y = null,
  numero_1x = 16, numero_1y = 2.3, timbrado_2x = null, timbrado_2y = null, numero_2x = 16, numero_2y = 12.2,
  total_a_pagar_exentas_iva5_1x = 1, total_a_pagar_exentas_iva5_1y = 1, total_a_pagar_exentas_iva5_2x = 1,
  total_a_pagar_exentas_iva5_2y = 1, fecha_3x = 3.3, fecha_3y = 22.8, contado_3x = 9, contado_3y = 22.4,
  credito_3x = 12, credito_3y = 22.4, fraccion_3x = 11.7, fraccion_3y = 23.9, nombre_3x = 3.5, nombre_3y = 23.4,
  manzana_3x = 14.9, manzana_3y = 23.9, lote_3x = 18.2, lote_3y = 23.9, ruc_3x = 15.2, ruc_3y = 23.4, telefono_3x = 9,
  telefono_3y = 23.9, direccion_3x = 2.7, direccion_3y = 23.9, superficie_3x = 18.9, superficie_3y = 23.9,
  cta_cte_ctral_3x = 3, cta_cte_ctral_3y = 21.9, cantidad_3x = 1.8, cantidad_3y = 24.3, descripcion_3x = 2.7,
  descripcion_3y = 24.3, precio_3x = 12.2, precio_3y = 24.3, exentas_3x = 14.4, exentas_3y = 24.3, iva5_3x = 16.2,
  iva5_3y = 24.3, iva10_3x = 18, iva10_3y = 24.3, sub_exentas_3x = 14.4, sub_exentas_3y = 28.3, sub_iva5_3x = 16.2,
  sub_iva5_3y = 28.3, sub_iva10_3x = 18, sub_iva10_3y = 28.3, total_venta_3x = 1, total_venta_3y = 1,
  total_a_pagar_letra_3x = 3, total_a_pagar_letra_3y = 28.6, total_a_pagar_num_3x = 18, total_a_pagar_num_3y = 28.8,
  liq_iva5_3x = 3.7, liq_iva5_3y = 28.8, liq_iva10_3x = 8, liq_iva10_3y = 28.8, liq_total_iva_3x = 12.8,
  liq_total_iva_3y = 28.8, timbrado_3x = null, timbrado_3y = null, numero_3x = 16, numero_3y = 21.8,
  total_a_pagar_exentas_iva5_3x = 1, total_a_pagar_exentas_iva5_3y = 1 WHERE id = 20;

--  23/01/2017 08:53 - Andres Romero - CBI-DEV: NO EJECUTADO - PROPAR: EJECUTADO  - GRUPO-MV: NO EJECUTADO
/* Este query  crea la tabla para poder registrar el logo principal del sistema*/
CREATE TABLE public.principal_logdelogos
(
  id serial  NOT NULL,
  nombre_archivo character varying(80),
  imagen bytea,
  CONSTRAINT principal_logdelogos_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.principal_logdelogos
  OWNER TO postgres;


-- 27/12/2016 16:0 - Franco Albertini - CBI-DEV: EJECUTADO - PROPAR: EJECUTADO  - KUPII-DEMO: EJECUTADO
/* Se crea la tabla de configuraciones de intereses */
  CREATE TABLE principal_configuracionintereses
(
  id serial NOT NULL,
  porcentaje_interes_cuota double precision,
  codigo_empresa character varying(4),
  gestion_cobranza boolean,
  cuotas_dias_gracia integer,
  dias_de_gracia integer,
  CONSTRAINT pk_configuracion_intereses PRIMARY KEY (id),
  CONSTRAINT unique_empresa_configuracion_intereses UNIQUE (codigo_empresa)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE principal_configuracionintereses
  OWNER TO propar_db_user; -- cambiar el owner de acuerdo a la BD  ej: kupii_user --

INSERT INTO principal_configuracionintereses
(porcentaje_interes_cuota, codigo_empresa, gestion_cobranza, cuotas_dias_gracia, dias_de_gracia)
VALUES (0.001, 'PROP', true, 1, 5); -- Insertar de acuerdo a la base de dato del cliente

INSERT INTO principal_configuracionintereses
(porcentaje_interes_cuota, codigo_empresa, gestion_cobranza, cuotas_dias_gracia, dias_de_gracia)
VALUES (0.03, 'VIER', false, 1, 5); -- Insertar de acuerdo a la base de dato del cliente

-- 13/12/2016 16:0 - Franco Albertini - CBI-DEV: EJECUTADO - PROPAR: EJECUTADO  - KUPII-DEMO: NO EJECUTADO
/* Se agrega la columna Cuota a la tabla Lotes */
 ALTER TABLE principal_lote ADD COLUMN cuota integer;