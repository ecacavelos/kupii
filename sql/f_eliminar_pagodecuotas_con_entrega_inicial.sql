CREATE OR REPLACE FUNCTION F_ELIMINAR_PAGOS_CON_ENTREGA_INICIAL() RETURNS void AS
$$
  DECLARE 
	c_ventas CURSOR FOR
		SELECT id, lote_id, fecha_de_venta, cliente_id, vendedor_id, plan_de_pago_id,entrega_inicial, 
		precio_de_cuota, precio_final_de_venta, fecha_primer_vencimiento,pagos_realizados, importacion_paralot, 
		plan_de_pago_vendedor_id FROM principal_venta WHERE entrega_inicial > 0 order by lote_id;	
	v_cont integer :=0;
	v_id_pago integer :=0;
  BEGIN
	FOR r_venta IN c_ventas LOOP
		SELECT id INTO v_id_pago FROM principal_pagodecuotas WHERE lote_id = r_venta.lote_id AND venta_id = r_venta.id 
		AND total_de_cuotas = r_venta.entrega_inicial;
		IF FOUND THEN
			v_cont = v_cont + 1
			RAISE NOTICE 'ID PAGO A ELIMINAR: % || nro %',v_id_pago, v_cont;
			DELETE FROM principal_pagodecuotas WHERE id = v_id_pago;
		END IF;
	END LOOP;
  END;
$$ LANGUAGE plpgsql;
select F_ELIMINAR_PAGOS_CON_ENTREGA_INICIAL();