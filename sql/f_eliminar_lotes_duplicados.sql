-- Function: f_eliminar_lotes_duplicados

DROP FUNCTION IF EXISTS f_eliminar_lotes_duplicados();

CREATE OR REPLACE FUNCTION f_eliminar_lotes_duplicados()
  RETURNS void AS
$BODY$
  DECLARE 
c_lotes_duplicados CURSOR FOR
SELECT codigo_paralot, count(*) from principal_lote group by codigo_paralot having count(*) > 1;
v_contador_lotes_codigo integer :=0;
v_contador_lotes_analizados integer :=0;
v_contador_lotes_borrados integer :=0;
v_id_lote integer :=0;
r_lote RECORD;

BEGIN
FOR r_lote_codigo IN c_lotes_duplicados LOOP
	 RAISE NOTICE 'Arrancando el analisis..';
	 v_contador_lotes_codigo := v_contador_lotes_codigo + 1;
	 RAISE NOTICE 'Analizando lotes con codigo: % || nro %', r_lote_codigo.codigo_paralot, v_contador_lotes_codigo;
	 FOR r_lote IN SELECT *  FROM principal_lote WHERE codigo_paralot = r_lote_codigo.codigo_paralot LOOP
		-- Aqui se analiza lote por lote. Si se encuentra un lote que no tiene NINGUNA  relacion, entonces se borra.
		v_contador_lotes_analizados := v_contador_lotes_analizados + 1;
		RAISE NOTICE 'Analizando LOTE : % || nro %', r_lote.id, v_contador_lotes_analizados;
		SELECT id INTO v_id_lote FROM principal_pagodecuotas WHERE lote_id = r_lote.id;
		IF NOT FOUND THEN
			v_contador_lotes_borrados := v_contador_lotes_borrados + 1;
			RAISE NOTICE 'No se encontraron pago de cuotas para el lote, se borra el lote con ID: %',r_lote.id;			
			DELETE from principal_lote where id = r_lote.id;
			RAISE NOTICE 'Lote borrado nro: %',v_contador_lotes_borrados;
		END IF;
	 END LOOP;
	 RAISE NOTICE 'Analizando lotes con codigo: % || nro % TERMINADO..', r_lote_codigo.codigo_paralot, v_contador_lotes_codigo;
END LOOP;
  END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
