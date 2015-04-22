-- Function: f_insertar_pagodecuotas()

-- DROP FUNCTION f_insertar_pagodecuotas();

CREATE OR REPLACE FUNCTION f_borrar_cuotas_de_entrega_inicial()
  RETURNS void AS
$BODY$
DECLARE c_ventas CURSOR FOR select * from principal_venta where entrega_inicial > 0 ;

v_contador_ventas integer :=0;
v_contador_deletes integer :=0;
v_id_pagodecuota integer :=0;

BEGIN

	FOR r_venta IN c_ventas LOOP
		v_contador_ventas := v_contador_ventas + 1;
		RAISE NOTICE 'Venta : %. v_contador_ventas: %',  r_venta.id, v_contador_ventas;
		select id INTO v_id_pagodecuota from principal_pagodecuotas where venta_id = r_venta.id and total_de_pago = r_venta.entrega_inicial order by fecha_de_pago asc limit 1;
		IF FOUND THEN
			v_contador_deletes := v_contador_deletes + 1;
			RAISE NOTICE 'pago de cuota a eliminar : %. v_contador_deletes: %',  v_id_pagodecuota, v_contador_deletes;
			--delete from principal_pagodecuotas where id = v_id_pagodecuota;
		ELSE
			RAISE NOTICE 'No se encontro registro de pago de cuota para venta: %. No se borra nada',  r_venta.id;
		END IF;
	END LOOP;
		
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;