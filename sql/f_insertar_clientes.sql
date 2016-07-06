CREATE OR REPLACE FUNCTION F_INSERTAR_CLIENTES() RETURNS BOOLEAN AS
$$
  DECLARE 
	c_clientes_intermedio CURSOR FOR
	SELECT cod_cli, nom_cli, ape_cli, nac_cli, ced_id, sex_cli, est_civ, dir_leg, dir_cob, tel_pa,
	tel_of, nom_con, deu_cli FROM clientes_intermedio;
  BEGIN
	FOR r_cliente IN c_clientes_intermedio LOOP
		INSERT INTO principal_cliente
		VALUES(r_cliente.cod_cli, r_cliente.nom_cli, r_cliente.ape_cli, r_cliente.nac_cli, r_cliente.ced_id,
			null, r_cliente.sex_cli, r_cliente.est_civ,  r_cliente.dir_leg, r_cliente.dir_cob, r_cliente.tel_pa,
			r_cliente.tel_of, null, null, r_cliente.nom_con, r_cliente.deu_cli, true);
	END LOOP;
	RETURN TRUE;
  END;
$$ LANGUAGE plpgsql;


EXCEPTION
     WHEN NO_DATA_FOUND THEN
          RETURN FALSE;
	 WHEN unique_violation THEN
		 RAISE NOTICE 'Claves repetidas';
		  RETURN FALSE;
	 WHEN OTHERS THEN
		 RAISE NOTICE 'Algo esta mal :(';
		 RETURN FALSE;