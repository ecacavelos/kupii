CREATE OR REPLACE FUNCTION F_INSERTAR_LOTES() RETURNS void AS
$$
  DECLARE 
	c_lotes_intermedio CURSOR FOR
		SELECT cod_lot, cod_cli, cod_ven, ven_cos, ven_con, ven_cre, sup_lot, est_lot, cod_ppag, cod_pven, fec_ven, cuo_ini, pre_cuo, cuo_ref,
		fec_ini, nro_cpag, saldo, nro_ven, ctactral, boleto, lineaimp, fecultpago, cod_fraccion, cod_manzana, cod_lote
		FROM lotes_intermedio_2;
		id_manzana integer;
  BEGIN
	FOR r_lote IN c_lotes_intermedio LOOP
		SELECT id INTO id_manzana FROM principal_manzana where nro_manzana = r_lote.cod_manzana AND fraccion_id = r_lote.cod_fraccion;
		IF NOT FOUND THEN
			id_manzana := 0;
		END IF;
		INSERT INTO principal_lote
		(nro_lote, manzana_id, precio_contado, precio_credito, superficie, cuenta_corriente_catastral, boleto_nro,
		estado, precio_costo, codigo_paralot)
		VALUES(r_lote.cod_lote, id_manzana, r_lote.ven_con, r_lote.ven_cre, r_lote.sup_lot, r_lote.ctactral, r_lote.boleto,
		r_lote.est_lot, r_lote.ven_cos, r_lote.cod_lot);
	END LOOP;
  END;
$$ LANGUAGE plpgsql;