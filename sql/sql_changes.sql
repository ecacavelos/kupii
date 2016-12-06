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
  OWNER TO kupii_user; -- cambiar el owner de acuerdo a la BD --

INSERT INTO principal_configuracionintereses
(porcentaje_interes_cuota, codigo_empresa, gestion_cobranza, cuotas_dias_gracia, dias_de_gracia)
VALUES (0.03, 'VIER', false, 1, 5); -- cambiar de acuerdo a la BD --