-- DEJAR SIEMPRE ESTO EN LA PARTE DE ARRIBA COMO EJEMPLO PARA REEMPLAZAR!!! ORDEN DESCENDENTE POR FECHA --
/* INSTANCIAS DE BASES DE DATOS DE KUPII:
  1- CBI-DEV: Base de datos ubicada en el servidor de desarrollo de CBI.
  2- PROPAR: Base de datos de produccion, del sistema de lotes de PROPAR.
  3- KUPII-DEMO:  Base de datos demo en azure del sistema de lotes KUPII.

 IMPORTANTE: El que hace el deploy, debe acualizar los estados, de las cabeceras de los querys a EJECUTADO, de las respectivas instacias de BD
 */

-- EJEMPLO: ##/##/#### ##:## - Desarrollador - BD: EJECUTADO O NO - BD: EJECUTADO O NO  - BD: EJECUTADO O NO
/* Breve descripcion de lo que hace el query */
-- query en cuestion --
-- agregar siempre despues de este ejemplo el siguiente cambio --

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