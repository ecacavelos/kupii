CREATE OR REPLACE FUNCTION F_INSERTAR_MANZANAS() RETURNS void AS
$$
  DECLARE 
	c_fracciones_intermedia CURSOR FOR
		SELECT cod_fra, nom_fra, ape_due, nom_due, nro_man, nro_lot, ubicacion, 
		distrito, finca, nro_aprob, fec_aprob, superficie
		FROM fracciones_intermedia ORDER BY cod_fra;
	v_query text;
	c_manzanas refcursor;
	v_cod_manzana INTEGER;
	v_cantidad_lotes BIGINT;
  BEGIN
	FOR r_fraccion IN c_fracciones_intermedia LOOP
		v_query := 'SELECT cod_manzana, count(cod_lote) AS cant_lotes FROM lotes_intermedio_2 where cod_fraccion =';
		v_query := v_query || r_fraccion.cod_fra || ' GROUP BY cod_manzana ORDER BY cod_manzana';
		OPEN c_manzanas FOR SELECT cod_manzana, count(cod_lote) AS cant_lotes FROM lotes_intermedio_2 where cod_fraccion = r_fraccion.cod_fra GROUP BY cod_manzana;
		LOOP
			FETCH c_manzanas INTO v_cod_manzana, v_cantidad_lotes;
			EXIT WHEN NOT FOUND;
			INSERT INTO principal_manzana (nro_manzana, fraccion_id, cantidad_lotes, importacion_paralot)
			VALUES (v_cod_manzana, r_fraccion.cod_fra, v_cantidad_lotes, true);
		END LOOP;
		CLOSE c_manzanas;
	END LOOP;
  END;
$$ LANGUAGE plpgsql;


SELECT cod_manzana, count(cod_lote) AS cant_lotes FROM lotes_intermedio_2 where cod_fraccion = r_fraccion.cod_fra GROUP BY cod_manzana ORDER BY cod_manzana;