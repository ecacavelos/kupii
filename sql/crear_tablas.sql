#tabla cambio de lotes
CREATE TABLE principal_cambiodelotes
(
  id serial NOT NULL,
  cliente_id integer NOT NULL,
  fecha_de_cambio date NOT NULL,
  lote_a_cambiar_id integer NOT NULL,
  lote_nuevo_id integer NOT NULL,
  CONSTRAINT principal_cambiodelotes_pkey PRIMARY KEY (id),
  CONSTRAINT principal_cambiodelotes_cliente_id_fkey FOREIGN KEY (cliente_id)
      REFERENCES principal_cliente (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT principal_cambiodelotes_lote_a_cambiar_id_fkey FOREIGN KEY (lote_a_cambiar_id)
      REFERENCES principal_lote (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT principal_cambiodelotes_lote_nuevo_id_fkey FOREIGN KEY (lote_nuevo_id)
      REFERENCES principal_lote (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
);
#Tabla clientes
CREATE TABLE principal_cliente
(
  id serial NOT NULL,
  nombres character varying(255),
  apellidos character varying(255),
  fecha_nacimiento date,
  cedula character varying(10),
  ruc character varying(255),
  sexo character varying(1),
  estado_civil character varying(1),
  direccion_particular character varying(255),
  direccion_cobro character varying(255),
  telefono_particular character varying(255),
  telefono_laboral character varying(255),
  celular_1 character varying(255),
  celular_2 character varying(255),
  nombre_conyuge character varying(255),
  deuda_contraida bigint,
  importacion_paralot boolean,
  CONSTRAINT principal_cliente_pkey PRIMARY KEY (id)
);

#tabla cobrador
CREATE TABLE principal_cobrador
(
  id serial NOT NULL,
  nombres character varying(255) NOT NULL,
  apellidos character varying(255) NOT NULL,
  cedula character varying(8) NOT NULL,
  direccion character varying(255) NOT NULL,
  telefono_particular character varying(255) NOT NULL,
  celular_1 character varying(255) NOT NULL,
  fecha_ingreso date NOT NULL,
  CONSTRAINT principal_cobrador_pkey PRIMARY KEY (id)
);

#tabla factura
CREATE TABLE principal_factura
(
  id serial NOT NULL,
  fecha date NOT NULL,
  numero character varying(30) NOT NULL,
  cliente_id integer NOT NULL,
  timbrado_id integer NOT NULL,
  tipo character varying(2) NOT NULL,
  detalle text NOT NULL,
  lote_id integer,
  CONSTRAINT principal_factura_pkey PRIMARY KEY (id),
  CONSTRAINT principal_factura_cliente_id_fkey FOREIGN KEY (cliente_id)
      REFERENCES principal_cliente (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT principal_factura_lote_id_fkey FOREIGN KEY (lote_id)
      REFERENCES principal_lote (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT principal_factura_timbrado_id_fkey FOREIGN KEY (timbrado_id)
      REFERENCES principal_timbrado (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
);

#tabla fraccion
CREATE TABLE principal_fraccion
(
  id serial NOT NULL,
  nombre character varying(255) NOT NULL,
  ubicacion character varying(255),
  propietario_id integer NOT NULL,
  cantidad_manzanas integer NOT NULL,
  cantidad_lotes integer NOT NULL,
  distrito character varying(255),
  finca character varying(255),
  aprobacion_municipal_nro character varying(255),
  fecha_aprobacion date,
  superficie_total numeric(8,2),
  importacion_paralot boolean,
  CONSTRAINT principal_fraccion_pkey PRIMARY KEY (id)
);

#tabla lote
CREATE TABLE principal_lote
(
  id serial NOT NULL,
  nro_lote integer NOT NULL,
  manzana_id integer NOT NULL,
  precio_contado integer NOT NULL,
  precio_credito integer NOT NULL,
  superficie numeric(8,2) NOT NULL,
  cuenta_corriente_catastral character varying(255) NOT NULL,
  boleto_nro integer,
  estado character varying(1) NOT NULL,
  precio_costo integer,
  importacion_paralot boolean,
  codigo_paralot character varying(12) NOT NULL,
  CONSTRAINT principal_lote_pkey PRIMARY KEY (id),
  CONSTRAINT principal_lote_manzana_id_fkey FOREIGN KEY (manzana_id)
      REFERENCES principal_manzana (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
);

#tabla manzana
CREATE TABLE principal_manzana
(
  id serial NOT NULL,
  nro_manzana integer NOT NULL,
  fraccion_id integer NOT NULL,
  cantidad_lotes integer,
  importacion_paralot boolean,
  CONSTRAINT principal_manzana_pkey PRIMARY KEY (id),
  CONSTRAINT principal_manzana_fraccion_id_fkey FOREIGN KEY (fraccion_id)
      REFERENCES principal_fraccion (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
);

#tabla pago de cuotas
CREATE TABLE principal_pagodecuotas
(
  id serial NOT NULL,
  lote_id integer NOT NULL,
  fecha_de_pago date NOT NULL,
  nro_cuotas_a_pagar integer NOT NULL,
  cliente_id integer NOT NULL,
  plan_de_pago_id integer NOT NULL,
  vendedor_id integer NOT NULL,
  total_de_cuotas integer NOT NULL,
  total_de_mora integer NOT NULL,
  total_de_pago integer NOT NULL,
  venta_id integer,
  plan_de_pago_vendedores_id integer NOT NULL,
  importacion_paralot boolean,
  CONSTRAINT principal_pagodecuotas_pkey PRIMARY KEY (id),
  CONSTRAINT principal_pagodecuotas_cliente_id_fkey FOREIGN KEY (cliente_id)
      REFERENCES principal_cliente (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT principal_pagodecuotas_lote_id_fkey FOREIGN KEY (lote_id)
      REFERENCES principal_lote (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT principal_pagodecuotas_plan_de_pago_id_fkey FOREIGN KEY (plan_de_pago_id)
      REFERENCES principal_plandepago (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT principal_pagodecuotas_plan_de_pago_vendedor_id_fkey FOREIGN KEY (plan_de_pago_vendedores_id)
      REFERENCES principal_plandepagovendedor (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT principal_pagodecuotas_vendedor_id_fkey FOREIGN KEY (vendedor_id)
      REFERENCES principal_vendedor (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT principal_pagodecuotas_venta_id_fkey FOREIGN KEY (venta_id)
      REFERENCES principal_venta (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
);

#tabla plan de pago
CREATE TABLE principal_plandepago
(
  id serial NOT NULL,
  nombre_del_plan character varying(255) NOT NULL,
  tipo_de_plan character varying(7) NOT NULL,
  cantidad_de_cuotas integer,
  porcentaje_inicial_inmobiliaria integer NOT NULL,
  cantidad_cuotas_inmobiliaria integer NOT NULL,
  inicio_cuotas_inmobiliaria integer NOT NULL,
  intervalos_cuotas_inmobiliaria integer NOT NULL,
  porcentaje_cuotas_inmobiliaria integer NOT NULL,
  porcentaje_cuotas_administracion integer NOT NULL,
  porcentaje_inicial_gerente integer NOT NULL,
  cantidad_cuotas_gerente integer NOT NULL,
  inicio_cuotas_gerente integer NOT NULL,
  intervalos_cuotas_gerente integer NOT NULL,
  porcentaje_cuotas_gerente integer NOT NULL,
  monto_fijo_cuotas_gerente integer,
  importacion_paralot boolean,
  CONSTRAINT principal_plandepago_pkey PRIMARY KEY (id)
);

#tabla plan de pago vendedor
CREATE TABLE principal_plandepagovendedor
(
  id integer NOT NULL DEFAULT nextval('principal_plandepagovendedores_id_seq'::regclass),
  nombre character varying(255) NOT NULL,
  porcentaje_cuota_inicial numeric(5,2) NOT NULL,
  cantidad_cuotas integer NOT NULL,
  cuota_inicial integer NOT NULL,
  intervalos integer NOT NULL,
  porcentaje_de_cuotas numeric(5,2) NOT NULL,
  observacion text,
  importacion_paralot boolean,
  tipo character varying(20),
  CONSTRAINT principal_plandepagovendedor_pkey PRIMARY KEY (id)
);

#tabla propietario
CREATE TABLE principal_propietario
(
  id serial NOT NULL,
  nombres character varying(255) NOT NULL,
  apellidos character varying(255) NOT NULL,
  fecha_nacimiento date,
  fecha_ingreso date,
  cedula character varying(10),
  ruc character varying(255),
  direccion_particular character varying(255),
  telefono_particular character varying(255),
  celular_1 character varying(255),
  celular_2 character varying(255),
  importacion_paralot boolean,
  CONSTRAINT principal_propietario_pkey PRIMARY KEY (id)
);

#tabla recuperacion de lotes
CREATE TABLE principal_recuperaciondelotes
(
  id serial NOT NULL,
  lote_id integer NOT NULL,
  fecha_de_recuperacion date NOT NULL,
  cliente_id integer NOT NULL,
  vendedor_id integer NOT NULL,
  venta_id integer NOT NULL,
  CONSTRAINT principal_recuperaciondelotes_pkey PRIMARY KEY (id),
  CONSTRAINT principal_recuperaciondelotes_cliente_id_fkey FOREIGN KEY (cliente_id)
      REFERENCES principal_cliente (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT principal_recuperaciondelotes_vendedor_id_fkey FOREIGN KEY (vendedor_id)
      REFERENCES principal_vendedor (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT principal_recuperaciondelotes_venta_id_fkey FOREIGN KEY (venta_id)
      REFERENCES principal_venta (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
);

#tabla reserva
CREATE TABLE principal_reserva
(
  id serial NOT NULL,
  lote_id integer NOT NULL,
  fecha_de_reserva date NOT NULL,
  cliente_id integer NOT NULL,
  CONSTRAINT principal_reserva_pkey PRIMARY KEY (id),
  CONSTRAINT principal_reserva_cliente_id_fkey FOREIGN KEY (cliente_id)
      REFERENCES principal_cliente (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
);

#tabla timbrado
CREATE TABLE principal_timbrado
(
  id serial NOT NULL,
  desde date NOT NULL,
  hasta date NOT NULL,
  numero character varying(30) NOT NULL,
  CONSTRAINT principal_timbrado_pkey PRIMARY KEY (id)
);

#tabla transferencia de lotes
CREATE TABLE principal_transferenciadelotes
(
  id serial NOT NULL,
  lote_id integer NOT NULL,
  fecha_de_transferencia date NOT NULL,
  cliente_id integer NOT NULL,
  cliente_original_id integer NOT NULL,
  vendedor_id integer NOT NULL,
  plan_de_pago_id integer NOT NULL,
  CONSTRAINT principal_transferenciadelotes_pkey PRIMARY KEY (id),
  CONSTRAINT principal_transferenciadelotes_cliente_id_fkey FOREIGN KEY (cliente_id)
      REFERENCES principal_cliente (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT principal_transferenciadelotes_cliente_original_id_fkey FOREIGN KEY (cliente_original_id)
      REFERENCES principal_cliente (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT principal_transferenciadelotes_lote_id_fkey FOREIGN KEY (lote_id)
      REFERENCES principal_lote (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT principal_transferenciadelotes_plan_de_pago_id_fkey FOREIGN KEY (plan_de_pago_id)
      REFERENCES principal_plandepago (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT principal_transferenciadelotes_vendedor_id_fkey FOREIGN KEY (vendedor_id)
      REFERENCES principal_vendedor (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
);
# tabla vendedor
CREATE TABLE principal_vendedor
(
  id serial NOT NULL,
  nombres character varying(255) NOT NULL,
  apellidos character varying(255) NOT NULL,
  cedula character varying(8),
  direccion character varying(255),
  telefono character varying(255),
  celular_1 character varying(255),
  fecha_ingreso date,
  sucursal character varying(255),
  importacion_paralot boolean,
  CONSTRAINT principal_vendedor_pkey PRIMARY KEY (id)
);

#tabla ventas

CREATE TABLE principal_venta
(
  id serial NOT NULL,
  lote_id integer NOT NULL,
  fecha_de_venta date NOT NULL,
  cliente_id integer NOT NULL,
  vendedor_id integer NOT NULL,
  plan_de_pago_id integer NOT NULL,
  entrega_inicial bigint,
  precio_de_cuota bigint,
  precio_final_de_venta bigint NOT NULL,
  fecha_primer_vencimiento date,
  pagos_realizados integer,
  importacion_paralot boolean,
  plan_de_pago_vendedor_id integer NOT NULL,
  CONSTRAINT principal_venta_pkey PRIMARY KEY (id),
  CONSTRAINT principal_venta_cliente_id_fkey FOREIGN KEY (cliente_id)
      REFERENCES principal_cliente (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT principal_venta_plan_de_pago_id_fkey FOREIGN KEY (plan_de_pago_id)
      REFERENCES principal_plandepago (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT principal_venta_plan_de_pago_vendedor_id_fkey FOREIGN KEY (plan_de_pago_vendedor_id)
      REFERENCES principal_plandepagovendedor (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT principal_venta_vendedor_id_fkey FOREIGN KEY (vendedor_id)
      REFERENCES principal_vendedor (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
);
