CREATE OR REPLACE FUNCTION F_INSERTAR_VENTAS() RETURNS void AS
$$
  DECLARE 
	c_lotes_intermedio CURSOR FOR
		SELECT cod_lot, cod_cli, cod_ven, ven_cos, ven_con, ven_cre, sup_lot, est_lot, cod_ppag, cod_pven, fec_ven, cuo_ini, pre_cuo, cuo_ref,
		fec_ini, nro_cpag, saldo, nro_ven, ctactral, boleto, lineaimp, fecultpago, cod_fraccion, cod_manzana, cod_lote
		FROM lotes_intermedio_2 WHERE (est_lot = '3' OR est_lot= '4');
	v_id_cliente integer :=0;
	v_id_vendedor integer :=0;
	v_id_lote integer :=0;
	v_precio_venta integer :=0;
	v_estado varchar(2) :='3';
  BEGIN
	FOR r_lote IN c_lotes_intermedio LOOP
		SELECT id INTO v_id_lote FROM principal_lote WHERE codigo_paralot LIKE r_lote.cod_lot AND (estado = '3' or estado = '4');
		IF FOUND THEN
			IF r_lote.cod_cli ='' THEN
				SELECT id INTO v_id_cliente FROM principal_cliente WHERE id = 11217;
			ELSE
				SELECT id INTO v_id_cliente FROM principal_cliente WHERE CAST(id AS text) = r_lote.cod_cli;
				IF NOT FOUND THEN
					SELECT id INTO v_id_cliente FROM principal_cliente WHERE id = 11217;
				END IF;
			END IF;
			IF r_lote.cod_ven ='' THEN
				SELECT id INTO v_id_vendedor FROM principal_vendedor WHERE id = 103;
			ELSE
				SELECT id INTO v_id_vendedor FROM principal_vendedor WHERE CAST(id AS text) = r_lote.cod_ven;
				IF NOT FOUND THEN
					SELECT id INTO v_id_vendedor FROM principal_vendedor WHERE id = 103;
				END IF;
			END IF;
			
			IF r_lote.est_lot = v_estado THEN
				v_precio_venta =r_lote.ven_cre;
			ELSE
				v_precio_venta =r_lote.ven_con;
			END IF;
						
			IF r_lote.fec_ini = null THEN
				r_lote.fec_ini := r_lote.fec_ven;
			END IF;
			
			IF r_lote.nro_cpag = null THEN
				r_lote.nro_cpag := 0;
			END IF;
			INSERT INTO principal_venta
			(lote_id, fecha_de_venta, cliente_id, vendedor_id, plan_de_pago_id, entrega_inicial, precio_de_cuota,
			precio_final_de_venta, fecha_primer_vencimiento, pagos_realizados, importacion_paralot, plan_de_pago_vendedor_id)
			VALUES
			(v_id_lote, r_lote.fec_ven, v_id_cliente, v_id_vendedor, r_lote.cod_ppag, r_lote.cuo_ini,
			r_lote.pre_cuo, v_precio_venta, r_lote.fec_ini, r_lote.nro_cpag, true, r_lote.cod_pven)	;
		END IF;
	END LOOP;
  END;
$$ LANGUAGE plpgsql;
select f_insertar_ventas();