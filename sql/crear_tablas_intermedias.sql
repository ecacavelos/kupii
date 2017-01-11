CREATE TABLE clientes_intermedio
(
	cod_cli varchar(20),
	ape_cli varchar(255),
	nom_cli varchar(255),
	ced_id varchar(25),
	est_civ varchar(20),
	tel_of varchar(25),
	tel_pa varchar(100),
	dir_leg varchar(255),
	dir_cob varchar(255),
	nom_con varchar(255),
	sex_cli varchar(20),
	deu_cli varchar(20),
	nac_cli varchar(30),
	nac_con varchar(30),
	CONSTRAINT principal_clientes_pkey PRIMARY KEY (cod_cli)
);

CREATE TABLE movimientos_intermedio
(
	cod_mov varchar(20),
	cod_lot varchar(20),
	cod_cli varchar(20),
	cod_cob varchar(20),
	tip_mov varchar(20),
	fec_mov varchar(20),
	nro_cuo varchar(20),
	mon_pag varchar(20),
	mor_cuo varchar(20)
);

CREATE TABLE lotes_intermedio
(
	cod_lot varchar(20),
	cod_cli varchar(20),
	cod_ven varchar(20),
	ven_cos varchar(20),
	ven_con varchar(20),
	ven_cre varchar(20),
	sup_lot varchar(20),
	est_lot varchar(20),
	cod_ppag varchar(20),
	cod_pven varchar(20),
	fec_ven varchar(20),
	cuo_ini varchar(20),
	pre_cuo varchar(20),
	cuo_ref varchar(20),
	fec_ini varchar(20),
	nro_cpag varchar(20),
	saldo varchar(20),
	nro_ven varchar(20),
	ctactral varchar(20),
	boleto varchar(20),
	lineaimp varchar(20),
	fecultpago varchar(20)
);

CREATE TABLE fracciones_intermedia
(
	cod_fra varchar(20),
	nom_fra varchar(255),
	ape_due varchar(255),
	nom_due varchar(255),
	nro_man varchar(20),
	nro_lot varchar(20),
	ubicacion varchar(255),
	distrito varchar(100),
	finca varchar(100),
	nro_aprob varchar(20),
	fec_aprob varchar(20),
	superficie varchar(100)
)

CREATE TABLE lotes_intermedio_2
(
  cod_lot character varying(20),
  cod_cli character varying(20),
  cod_ven character varying(20),
  ven_cos character varying(20),
  ven_con character varying(20),
  ven_cre character varying(20),
  sup_lot character varying(20),
  est_lot character varying(20),
  cod_ppag character varying(20),
  cod_pven character varying(20),
  fec_ven character varying(20),
  cuo_ini character varying(20),
  pre_cuo character varying(20),
  cuo_ref character varying(20),
  fec_ini character varying(20),
  nro_cpag character varying(20),
  saldo character varying(20),
  nro_ven character varying(20),
  ctactral character varying(20),
  boleto character varying(20),
  lineaimp character varying(20),
  fecultpago character varying(20),
  cod_fraccion varchar(20),
  cod_manzana varchar(20),
  cod_lote varchar(20)
)

CREATE TABLE propietarios_intermedio
(
	nombres varchar(50),
	apellidos varchar(50),
	fecha_nacimiento varchar(50),
	fecha_ingreso varchar(50),
	cedula varchar(50),
	ruc varchar(50),
	direccion_particular varchar(50),
	telefono_particular varchar(50),
	celular_1 varchar(50),
	celular_2 varchar(50) 
)

CREATE TABLE vendedores_intermedio
(
	id varchar(20),
	apellidos varchar(70),
	nombres varchar(70),
	cedula varchar(50),
	celular_1 varchar(50),
	sucursal varchar(50),
	fecha_ingreso varchar(50)
)