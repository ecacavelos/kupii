<?php
//echo 'hola mundo       ';
$conn_string = "host=localhost port=5432 dbname=propar_db_nueva user=postgres";
try{
    $link = pg_connect($conn_string);
    if ($link){
         echo "se conecto\n";
        $query= "SELECT * FROM principal_lotep order by cod_lot"; 
        $result = pg_query($link, $query);
    } else{
        die ('No se conecto');
    }
    
    
} catch (Exception $ex) {
    die ($ex);
}
?>
<html>
<head></head>
<body>
<table border="1">
    <th>Cod Lote</th><th>ID de Manzana</th>
<?php
    $contador_lotes = 0;
    $manzana = 1;
    while ($row = pg_fetch_row($result)) {
        //echo $row[0]."\n";
         $cadena = explode("/",$row[0]);
        //print_r($cadena);
        
        $query2= "select id from principal_manzana where fraccion_id = ".ltrim($cadena[0],"0")." and nro_manzana= ".ltrim($cadena[1],"0");
        //echo($query);
        //die();
        $res_2 = pg_query($link, $query2);
        $num = pg_num_rows($res_2);
        $row2 = pg_fetch_row($res_2);
        if ($num == 0){
            $row2 = pg_fetch_row($res_2);
            if ($manzana!= ltrim($cadena[1],"0")){
                $contador_lotes = 0;
                $manzana= ltrim($cadena[1],"0");
            }
            $contador_lotes = $contador_lotes+1; 
            
            echo "<tr><td>".$row[0]."</td><td>Fraccion ".ltrim($cadena[0])."</td><td>Manzana: ".$manzana."</td><td>Cantidad Lotes: ".$contador_lotes."</td></tr>";
        }
        /*
        } else{
            echo "<tr><td>".$row[0]."</td><td>".$row2[0]."</td></tr>";
        }
        */
         
       
    }
?>
</table>
</body>
</html>
