-- Function: f_insertar_pagodecuotas()

-- DROP FUNCTION f_insertar_pagodecuotas();

CREATE OR REPLACE FUNCTION f_insertar_pagodecuotas()
  RETURNS void AS
$BODY$
  DECLARE 
c_movimientos_intermedio CURSOR FOR
SELECT cod_mov, cod_lot, cod_cli, cod_cob, tip_mov, fec_mov, nro_cuo, mon_pag, mor_cuo
FROM movimientos_intermedio WHERE cod_lot != '' AND mon_pag > 0 order by fec_mov desc;
v_id_cliente integer :=0;
v_id_vendedor integer :=0;
v_id_lote integer :=0;
v_plan_de_pago_id integer;
v_plan_de_pago_vendedor_id integer;
v_monto_pagado_total integer :=0;
v_id_venta integer :=0;
v_fecha_ultima_recuperacion date;
v_contador_mvtos integer :=0;
v_contador_mvtos_insertados integer :=0;

  BEGIN
FOR r_movimiento IN c_movimientos_intermedio LOOP

	v_contador_mvtos := v_contador_mvtos + 1;
	RAISE NOTICE 'Movimiento nro: %. LOTE: %',  v_contador_mvtos, r_movimiento.cod_lot;

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
	-- Antes de insertar el movimiento (pagodecuota), chequeamos si existe un registro con 
	-- Se trae la fecha de la ultima recuperacion. Si la fecha del movimiento es mayor a la ultima fecha de recuperacion, entonces insertamos.
	select fec_mov into v_fecha_ultima_recuperacion from movimientos_intermedio where (tip_mov = '6' or tip_mov = '8') and cod_lot = r_movimiento.cod_lot order by fec_mov desc LIMIT 1;
	IF NOT FOUND THEN
		select fec_mov into v_fecha_ultima_recuperacion from movimientos_intermedio order by fec_mov limit 1;
		RAISE notice'No se encontro ninguna recuperacion para este lote %. Se establece fecha minima',r_movimiento.cod_lot;
	END IF;

	RAISE notice 'ultima recuperacion: %, fecha del mvto: %',r_movimiento.fec_mov, v_fecha_ultima_recuperacion;
	IF r_movimiento.fec_mov > v_fecha_ultima_recuperacion THEN
		v_contador_mvtos_insertados := v_contador_mvtos_insertados + 1;
		RAISE notice 'INSERCION NRO: % ', v_contador_mvtos_insertados;
		INSERT INTO principal_pagodecuotas
		(lote_id, cliente_id, vendedor_id, venta_id, plan_de_pago_id, plan_de_pago_vendedores_id, nro_cuotas_a_pagar, total_de_cuotas, 
		 total_de_mora, total_de_pago, fecha_de_pago, importacion_paralot)
		VALUES
		(v_id_lote, v_id_cliente,  v_id_vendedor, v_id_venta, v_plan_de_pago_id, v_plan_de_pago_vendedor_id, 1,
		r_movimiento.mon_pag, r_movimiento.mor_cuo, v_monto_pagado_total, r_movimiento.fec_mov, true);
	ELSE
		RAISE notice 'NO SE INSERTA movimiento.Se excluye cuota del lote %, en fecha %', r_movimiento.cod_lot,r_movimiento.fec_mov;
	END IF;
	END IF;
	END IF;
END LOOP;
  END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION f_insertar_pagodecuotas()
  OWNER TO postgres;
