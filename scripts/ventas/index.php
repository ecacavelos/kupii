<?php
//echo 'hola mundo';
$conn_string = "host=localhost port=5432 dbname=propar_db_2 user=postgres password=123456";
try {
    $link = pg_connect($conn_string);
    if ($link) {
        echo "se conecto\n";
        $query = "SELECT * FROM principal_lotep WHERE (est_lot = '3' OR est_lot= '4')";
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
                $cadena = explode("/",$row['cod_lot']);
                //print_r($cadena);
                //$fraccion = ltrim($cadena[0],"0");
                //$manzana =ltrim($cadena[1],"0");
                //$nro_lote = ltrim($cadena[2],"0");
                //$query2= "select id from principal_manzana where fraccion_id = ".$fraccion." and nro_manzana= ".$manzana;
                #BUSQUEDA DE ID DE LOTE CON CODIGO DE LOTE DE PARALOT
                $query_lote = "SELECT id FROM principal_lote WHERE codigo_paralot = '" . $row['cod_lot'] . "' AND (estado = '3' or estado = '4')";
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



                    //$query_venta = "SELECT id, vendedor_id, plan_de_pago_id, plan_de_pago_vendedor_id FROM principal_venta WHERE lote_id = " . $row_lote['id'];
                    //echo($query_venta);
                    //die();
                    /*$res_venta = pg_query($link, $query_venta);
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
					*/
                        $query_cliente = "SELECT id FROM principal_cliente WHERE id = " . $row['cod_cli'] . ";";
                        $res_cliente = pg_query($link, $query_cliente);
                        if (!$res_cliente) {
                            $error = "Error query: " . $query_cliente . " " . $row['cod_lot'] . " <br>";
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

                        $query_vendedor = "SELECT id FROM principal_vendedor WHERE id = " . $row['cod_ven'] . ";";
                        $res_vendedor = pg_query($link, $query_vendedor);
                        if (!$res_vendedor) {
                            $error = "Error query: " . $query_vendedor . " " . $row['cod_lot'] . "  Vendedor: " . $row['cod_ven'] . "<br>";
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
                            $query_cliente = "INSERT INTO principal_cliente (id, nombres, apellidos, estado_civil, importacion_paralot) values (" . $row['cod_cli'] . ",'Cliente ID" . $row['cod_cli'] . "','Se encuentra en la tabla ventas pero no en la tabla de clientes','S', TRUE)";
                            $res_cliente = pg_query($link, $query_cliente);
                        }



                        $num = pg_num_rows($res_vendedor);
                        if ($num == 0) {
                            $query_vendedor = "INSERT INTO principal_vendedor (id, nombres, apellidos, importacion_paralot) values (" . $row['cod_ven'] . ",'Vendedor ID" . $row['cod_ven'] . "','Se encuentra en la tabla ventas pero no en la tabla de vendedores', TRUE)";
                            $res_vendedor = pg_query($link, $query_vendedor);
                        }
						
						if ($row['est_lot']=="3"){
							$precio_final_de_venta =$row['ven_cre'];
						} else {
							$precio_final_de_venta =$row['ven_con'];
						}
						
						if ($row['fec_ini']==""){
							$row['fec_ini'] = $row['fec_ven'];
						}
						
						if ($row['nro_cpag']==""){
							$row['nro_cpag'] = 0;
						}

                        $query_insert = "insert into principal_venta ("
                                . "lote_id, "
                                . "fecha_de_venta, "
                                . "cliente_id, "
                                . "vendedor_id, "
                                . "plan_de_pago_id,"
                                . "entrega_inicial, "
								. "precio_de_cuota, "
								. "precio_final_de_venta, "
								. "fecha_primer_vencimiento, "
								. "pagos_realizados, "
								. "importacion_paralot, "
								. "plan_de_pago_vendedor_id)"
                                . " values ("
                                . $row_lote['id'] . ",'"					//lote_id --
								. $row['fec_ven'] . "',"				//fecha_de_venta --
                                . $row['cod_cli'] . ","                     //cliente_id --
                                . $row['cod_ven'] . ","               	//vendedor_id --
                                . $row['cod_ppag'] . ","           	//plan_de_pago_id --
                                . $row['cuo_ini'] . ","           	//entrega_inicial --
                                . $row['pre_cuo'] . ","                    //precio_de_cuota--
                                . $precio_final_de_venta. ",'"  //precio_final_de_venta
                                . $row['fec_ini'] . "',"                    //fecha_primer_vencimiento--
                                . $row['nro_cpag'] . ","                    //pagos_realizados--
                                . "TRUE" .","                             //importacion_paralot --
								. $row['cod_pven'] .");";  			//plan_de_pago_vendedor_id --
                        //echo $query_insert;
                        //die();
                        $res_insert = pg_query($link, $query_insert);
                        if (!$res_insert) {
                            $error = "Error query: " . $query_insert . " " . $row['cod_lot'] . "<br>";
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
					*/
                } else {
                    //echo "No se encontro el lote con cod_lot: " . $row['cod_lot'] ." con estado vendido<br>";
                    //echo "Query Lote: ".$query_lote."<br>";
                }
				//die("final");
            }
            ?>
        <!--</table>-->
    </body>
</html>
