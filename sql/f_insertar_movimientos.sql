CREATE OR REPLACE FUNCTION F_INSERTAR_PAGODECUOTAS() RETURNS void AS
$$
  DECLARE 
	c_movimientos_intermedio CURSOR FOR
		SELECT cod_mov, cod_lot, cod_cli, cod_cob, tip_mov, fec_mov, nro_cuo, mon_pag, mor_cuo
		FROM movimientos_intermedio_2 WHERE cod_lot != '';
	v_id_cliente integer :=0;
	v_id_vendedor integer :=0;
	v_id_lote integer :=0;
	v_plan_de_pago_id integer;
	v_plan_de_pago_vendedor_id integer;
	v_monto_pagado_total integer :=0;
	v_id_venta integer :=0;
  BEGIN
	FOR r_movimiento IN c_movimientos_intermedio LOOP
		SELECT id INTO v_id_lote FROM principal_lote WHERE codigo_paralot LIKE r_movimiento.cod_lot AND estado = '3';
		IF FOUND THEN
			SELECT id, vendedor_id, plan_de_pago_id, plan_de_pago_vendedor_id INTO v_id_venta, v_id_vendedor,
			v_plan_de_pago_id, v_plan_de_pago_vendedor_id FROM principal_venta WHERE lote_id = v_id_lote;
			IF FOUND THEN
				IF r_movimiento.cod_cli ='' THEN
					SELECT id INTO v_id_cliente FROM principal_cliente WHERE id = 11217;					
				ELSE
					SELECT id INTO v_id_cliente FROM principal_cliente WHERE CAST(id AS text) = r_movimiento.cod_cli;
					IF NOT FOUND THEN
						SELECT id INTO v_id_cliente FROM principal_cliente WHERE id = 11217;
					END IF;
				END IF;				
				v_monto_pagado_total := r_movimiento.mon_pag + r_movimiento.mor_cuo;
				INSERT INTO principal_pagodecuotas
				(lote_id, cliente_id, vendedor_id, venta_id, plan_de_pago_id, plan_de_pago_vendedores_id, nro_cuotas_a_pagar, total_de_cuotas, 
				 total_de_mora, total_de_pago, fecha_de_pago, importacion_paralot)
				VALUES
				(v_id_lote, v_id_cliente,  v_id_vendedor, v_id_venta, v_plan_de_pago_id, v_plan_de_pago_vendedor_id, 1,
				r_movimiento.mon_pag, r_movimiento.mor_cuo, v_monto_pagado_total, r_movimiento.fec_mov, true);
			END IF;			
		END IF;			
	END LOOP;
  END;
$$ LANGUAGE plpgsql;
 select F_INSERTAR_PAGODECUOTAS();