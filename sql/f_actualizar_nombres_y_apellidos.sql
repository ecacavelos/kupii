-- Function: factualizar_nombres_y_apellidos()

DROP FUNCTION IF EXISTS  f_actualizar_nombres_y_apellidos();

CREATE OR REPLACE FUNCTION f_actualizar_nombres_y_apellidos()
  RETURNS void AS
$BODY$
  DECLARE 
c_clientes_dist refcursor;
v_cliente_id integer :=0;
v_contador_clientes integer :=0;
r_cedula_cliente RECORD;
r_cliente_intermedio RECORD;

  BEGIN
	RAISE NOTICE 'Arrancando actualizacion de nombres y apellidos';
	FOR r_cedula_cliente IN SELECT distinct(cedula)  FROM principal_cliente LOOP
		v_contador_clientes := v_contador_clientes + 1;
		RAISE NOTICE 'Cliente a analizar -> cedula: %. Cliente nro: %',r_cedula_cliente.cedula, v_contador_clientes;
		FOR r_cliente_intermedio IN SELECT * FROM clientes_intermedio_prueba_csv WHERE ced_id = r_cedula_cliente.cedula ORDER BY cod_cli DESC LIMIT 1 LOOP
			RAISE NOTICE 'Nombres y apellidos NUEVOS: % %',r_cliente_intermedio.nom_cli, r_cliente_intermedio.ape_cli;
			UPDATE principal_cliente set apellidos = r_cliente_intermedio.ape_cli, nombres = r_cliente_intermedio.nom_cli, direccion_particular =  r_cliente_intermedio.dir_leg, direccion_cobro = r_cliente_intermedio.dir_cob  WHERE cedula = r_cliente_intermedio.ced_id;
		END LOOP;
	END LOOP;
  END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;