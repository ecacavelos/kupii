-- DEJAR SIEMPRE ESTO EN LA PARTE DE ARRIBA COMO EJEMPLO PARA REEMPLAZAR!!! ORDEN DESCENDENTE POR FECHA --
/* INSTANCIAS DE BASES DE DATOS DE KUPII:
  1- CBI-DEV: Base de datos ubicada en el servidor de desarrollo de CBI.
  2- PROPAR: Base de datos de produccion, del sistema de lotes de PROPAR.
  3- KUPII-DEMO:  Base de datos demo en azure del sistema de lotes KUPII.

 IMPORTANTE: El que hace el deploy, debe acualizar los estados, de las cabeceras de los querys a EJECUTADO, de las respectivas instacias de BD
 */

-- EJEMPLO: ##/##/#### ##:## - Desarrollador - BD: EJECUTADO O NO - BD: EJECUTADO O NO  - BD: EJECUTADO O NO
/* Breve descripcion de lo que hace el query */
-- query en cuestion --
-- agregar siempre despues de este ejemplo el siguiente cambio --

-- 13/12/2016 16:0 - Franco Albertini - CBI-DEV: EJECUTADO - PROPAR: EJECUTADO  - KUPII-DEMO: NO EJECUTADO
/* Se agrega la columna Cuota a la tabla Lotes */
 ALTER TABLE principal_lote ADD COLUMN cuota integer;