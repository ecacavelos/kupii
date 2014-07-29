<?php
//echo 'hola mundo';
$conn_string = "host=localhost port=5432 dbname=propar_db_2 user=postgres password=123456";
try {
    $link = pg_connect($conn_string);
    if ($link) {
        echo "se conecto<br>";
        $query = "SELECT * FROM movimientos ";
        $result = pg_query($link, $query);
    } else {
        die('No se conecto');
    }
} catch (Exception $ex) {
    die($ex);
}
?>
<html>
    <head></head>
    <body>
        <!--<table border="1">
            <th>Cod Lote</th><th>ID de Manzana</th>-->
            <?php
            /*
              $contador_lotes = 0;
              $manzana_anterior = 1;
             */
            while ($row = pg_fetch_array($result)) {
                //echo $row[0]."\n";
                //$cadena = explode("/",$row['cod_lot']);
                //print_r($cadena);
                //$fraccion = ltrim($cadena[0],"0");
                //$manzana =ltrim($cadena[1],"0");
                //$nro_lote = ltrim($cadena[2],"0");
                //$query2= "select id from principal_manzana where fraccion_id = ".$fraccion." and nro_manzana= ".$manzana;
                #BUSQUEDA DE ID DE LOTE CON CODIGO DE LOTE DE PARALOT
                $query_lote = "SELECT id FROM principal_lote WHERE codigo_paralot = '" . $row['COD_LOT'] . "' AND estado = '3'";
                //echo($query_lote);
                //die();

                $res_lote = pg_query($link, $query_lote);
                if (!$res_lote) {
                    $error = "Error query: " . $query_lote . "<br>";
                    $query_error = "INSERT INTO error_log (error) VALUES ('" . pg_escape_string($error) . "')";
                    $res_error = pg_query($query_error);
                    echo $error;
                    $file = 'error_sql.log';
                    // Open the file to get existing content
                    $current = file_get_contents($file);
                    // Append a new person to the file
                    $current .= $error."\n";
                    // Write the contents back to the file
                    file_put_contents($file, $current);
                } else {
                    $row_lote = pg_fetch_array($res_lote);
                }
                $num = pg_num_rows($res_lote);
                //echo $num;
                //die();
                if ($num != 0) {



                    $query_venta = "SELECT id, vendedor_id, plan_de_pago_id, plan_de_pago_vendedor_id FROM principal_venta WHERE lote_id = " . $row_lote['id'];
                    //echo($query_venta);
                    //die();
                    $res_venta = pg_query($link, $query_venta);
                    if (!$res_venta) {
                        $error = "Error query: " . $query_venta . "<br>";
                        $query_error = "INSERT INTO error_log (error) VALUES ('" . pg_escape_string($error) . "')";
                        $res_error = pg_query($query_error);
                        echo $error;
                        $file = 'error_sql.log';
                        // Open the file to get existing content
                        $current = file_get_contents($file);
                        // Append a new person to the file
                        $current .= $error."\n";
                        // Write the contents back to the file
                        file_put_contents($file, $current);
                    } else {
                        $row_ventas = pg_fetch_array($res_venta);
                    }

                    $num = pg_num_rows($res_venta);
                    if ($num != 0) {

                        $query_cliente = "SELECT id FROM principal_cliente WHERE id = " . $row['COD_CLI'] . ";";
                        $res_cliente = pg_query($link, $query_cliente);
                        if (!$res_cliente) {
                            $error = "Error query: " . $query_cliente . " " . $row['COD_MOV'] . " <br>";
                            $query_error = "INSERT INTO error_log (error) VALUES ('" . pg_escape_string($error) . "')";
                            $res_error = pg_query($query_error);
                            echo $error;
                            $file = 'error_sql.log';
                            // Open the file to get existing content
                            $current = file_get_contents($file);
                            // Append a new person to the file
                            $current .= $error."\n";
                            // Write the contents back to the file
                            file_put_contents($file, $current);
                        } else {
                            $row_cliente = pg_fetch_array($res_cliente);
                        }

                        $query_vendedor = "SELECT id FROM principal_vendedor WHERE id = " . $row_ventas['vendedor_id'] . ";";
                        $res_vendedor = pg_query($link, $query_vendedor);
                        if (!$res_vendedor) {
                            $error = "Error query: " . $query_vendedor . " " . $row['COD_MOV'] . "" . "Venta: " . $row_ventas['id'] . " Vendedor: " . $row_ventas['vendedor_id'] . "<br>";
                            $query_error = "INSERT INTO error_log (error) VALUES ('" . pg_escape_string($error) . "')";
                            $res_error = pg_query($query_error);
                            echo $error;
                            $file = 'error_sql.log';
                            // Open the file to get existing content
                            $current = file_get_contents($file);
                            // Append a new person to the file
                            $current .= $error."\n";
                            // Write the contents back to the file
                            file_put_contents($file, $current);
                        } else {
                            $row_vendedor = pg_fetch_array($res_vendedor);
                        }


                        $num = pg_num_rows($res_cliente);
                        if ($num == 0) {
                            $query_cliente = "INSERT INTO principal_cliente (id, nombres, apellidos, estado_civil, importacion_paralot) values (" . $row['COD_CLI'] . ",'Cliente ID" . $row['COD_CLI'] . "','Se encuentra en la tabla pagos pero no en la tabla de clientes','S', TRUE)";
                            $res_cliente = pg_query($link, $query_cliente);
                        }



                        $num = pg_num_rows($res_vendedor);
                        if ($num == 0) {
                            $query_vendedor = "INSERT INTO principal_vendedor (id, nombres, apellidos, importacion_paralot) values (" . $row_ventas['vendedor_id'] . ",'Vendedor ID" . $row_ventas['vendedor_id'] . "','Se encuentra en la tabla pagos pero no en la tabla de vendedores', TRUE)";
                            $res_vendedor = pg_query($link, $query_vendedor);
                        }

                        $query_insert = "insert into principal_pagodecuotas ("
                                . "lote_id, "
                                . "cliente_id, "
                                . "vendedor_id, "
                                . "venta_id, "
                                . "plan_de_pago_id,"
                                . "plan_de_pago_vendedores_id, "
                                . "nro_cuotas_a_pagar, "
                                . "total_de_cuotas, "
                                . "total_de_mora, "
                                . "total_de_pago, "
                                . "fecha_de_pago, "
                                . "importacion_paralot)"
                                . " values ("
                                . $row_lote['id'] . ","                              //lote_id
                                . $row['COD_CLI'] . ","                          //cliente_id
                                . $row_ventas['vendedor_id'] . ","               //vendedor_id
                                . $row_ventas['id'] . ","                        //venta_id
                                . $row_ventas['plan_de_pago_id'] . ","           //plan_de_pago_id
                                . $row_ventas['plan_de_pago_vendedor_id'] . ","  //plan_de_pago_vendedores_id
                                . "1,"                                  //nro_de_cuotas_a_pagar
                                . $row['MON_PAG'] . ","                    //total_de_cuotas
                                . $row['MOR_CUO'] . ","                    //total_de_mora
                                . ($row['MON_PAG'] + $row['MOR_CUO']) . ",'"  //total_de_pago
                                . $row['FEC_MOV'] . "',"                    //fecha_de_pago
                                . "TRUE);";                              //importacion_paralot
                        //echo $query_insert;
                        //die();
                        $res_insert = pg_query($link, $query_insert);
                        if (!$res_insert) {
                            $error = "Error query: " . $query_insert . " " . $row['COD_LOT'] . "<br>";
                            $query_error = "INSERT INTO error_log (error) VALUES ('" . pg_escape_string($error) . "')";
                            $res_error = pg_query($query_error);
                            echo $error;
                            //echo $query_error;
                            $file = 'error_sql.log';
                            // Open the file to get existing content
                            $current = file_get_contents($file);
                            // Append a new person to the file
                            $current .= $error."\n";
                            // Write the contents back to the file
                            file_put_contents($file, $current);
                            //die();
                        }
                        /*
                          if ($num == 0){
                          $row2 = pg_fetch_array($res_2);
                          if ($manzana_anterior!= $manzana){
                          $contador_lotes = 0;
                          $manzana_anterior= $manzana;
                          }
                          $contador_lotes = $contador_lotes+1;

                          echo "<tr><td>".$row['cod_lot']."</td><td>Fraccion ".ltrim($cadena[0])."</td><td>Manzana: ".$manzana."</td><td>Cantidad Lotes: ".$contador_lotes."</td></tr>";
                          }
                          /*
                          } else{
                          echo "<tr><td>".$row[0]."</td><td>".$row2[0]."</td></tr>";
                          }
                         */
                    } else {
                        $error = "No se encontro la venta del lote " . $row_lote['id'] . " Query Venta: " . $query_venta . "<br>";
                        $query_error = "INSERT INTO error_log (error) VALUES ('" . pg_escape_string($error) . "')";
                        $res_error = pg_query($query_error);
                        echo $error;
                        $file = 'error_sql.log';
                        // Open the file to get existing content
                        $current = file_get_contents($file);
                        // Append a new person to the file
                        $current .= $error."\n";
                        // Write the contents back to the file
                        file_put_contents($file, $current);
                    }
                } else {
                    //echo "No se encontro el lote, del movimiento con cod_lot: " . $row['COD_LOT'] ." con estado vendido<br>";
                    //echo "Query Lote: ".$query_lote."<br>";
                }
            }
            ?>
        <!--</table>-->
    </body>
</html>
