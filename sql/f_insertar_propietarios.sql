CREATE OR REPLACE FUNCTION F_INSERTAR_PROPIETARIOS() RETURNS void AS
$$
  DECLARE 
	c_propietarios_intermedio CURSOR FOR
	   SELECT nombres, apellidos, fecha_nacimiento, fecha_ingreso, cedula, ruc, direccion_particular, 
	   telefono_particular, celular_1, celular_2 FROM propietarios_intermedio;
  BEGIN
	FOR r_propietario IN c_propietarios_intermedio LOOP
		INSERT INTO principal_propietario
		(nombres, apellidos, fecha_nacimiento, fecha_ingreso, cedula, ruc ,direccion_particular, telefono_particular, celular_1, celular_2)
		VALUES(r_propietario.nombres, r_propietario.apellidos, r_propietario.fecha_nacimiento, 
		r_propietario.fecha_ingreso, r_propietario.cedula, r_propietario.ruc, r_propietario.direccion_particular, 
		r_propietario.telefono_particular, r_propietario.celular_1, r_propietario.celular_2);
	END LOOP;
  END;
$$ LANGUAGE plpgsql;