CREATE OR REPLACE FUNCTION F_INSERTAR_FRACCIONES() RETURNS void AS
$$
  DECLARE 
	c_fracciones_intermedia CURSOR FOR
	SELECT cod_fra, nom_fra, ape_due, nom_due, nro_man, nro_lot, ubicacion, 
	distrito, finca, nro_aprob, fec_aprob, superficie FROM fracciones_intermedia order by cod_fra;
	id_propietario integer :=0;
  BEGIN
	FOR r_fraccion IN c_fracciones_intermedia LOOP
		SELECT id INTO id_propietario FROM principal_propietario WHERE nombres LIKE '%' || r_fraccion.nom_due OR apellidos LIKE '%' || r_fraccion.ape_due LIMIT 1;
		INSERT INTO principal_fraccion
		VALUES(r_fraccion.cod_fra, r_fraccion.nom_fra, r_fraccion.ubicacion, id_propietario, r_fraccion.nro_man, 
		r_fraccion.nro_lot, r_fraccion.distrito, r_fraccion.finca, r_fraccion.nro_aprob, r_fraccion.fec_aprob, r_fraccion.superficie, true);
	END LOOP;
  END;
$$ LANGUAGE plpgsql;
SELECT id INTO id_propietario FROM principal_propietario WHERE nombres LIKE '%' || r_fraccion.nom_due OR apellidos LIKE '%' || r_fraccion.ape_due LIMIT 1;