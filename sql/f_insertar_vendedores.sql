CREATE OR REPLACE FUNCTION F_INSERTAR_VENDEDORES() RETURNS void AS
$$
  DECLARE 
	c_vendedores_intermedio CURSOR FOR
	   SELECT id, apellidos, nombres, cedula, celular_1, sucursal, fecha_ingreso
	   FROM vendedores_intermedio;
  BEGIN
	FOR r_vendedor IN c_vendedores_intermedio LOOP
		INSERT INTO principal_vendedor
		VALUES(r_vendedor.id, r_vendedor.nombres, r_vendedor.apellidos, r_vendedor.cedula, '', '',r_vendedor.celular_1,
		r_vendedor.fecha_ingreso, r_vendedor.sucursal, true);
	END LOOP;
  END;
$$ LANGUAGE plpgsql;