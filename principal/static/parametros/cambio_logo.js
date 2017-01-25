/**
 * Created by Andres on 15/01/2017.
 */
$(document).ready(function() {
    $('#cambio_logo').submit(function () {
       if ($('#imagen').val() == '' || $('#imagen').val() == null) {
           window.alert('No se cargo ninguna imagen');
           return false;
       }
    })
});

$(document).ready(function() {
    $('#listar_logo').submit(function () {
       if ($('#seleccion').val() == '' || $('#seleccion').val() == null) {
           window.alert('No se selecciono ninguna imagen');
           return false;
       }
    })
});

/*
function mostrarOcultarTablas(id){
		mostrado=0;
		elem = document.getElementById(id);
		if(elem.style.display=='block')mostrado=1;
			elem.style.display='none';
		if(mostrado!=1)elem.style.display='block';
}*/
/*
var cantidad_detalles = 1;
	$(document).ready(function() {
        $('#Listar').attr('disabled', false);
		if (cantidad_detalles == 1){
			if ($('#monto_otros_descuentos').val() == '') {
					$('#listado-table tr:last').find('input:text').attr('id', function(i, val) {
					return val + cantidad_detalles;
				});
			}
		}

 			nuevo_detalle = '<tr>'
			+	'<td><input type="text" id="ley" name="ley" style="text-align: center" value="0" readonly/></td>'
			+	'<td><input type="text" id="impuesto_renta" name="impuesto_renta" style="text-align: center" value="0" readonly /></td>'
			+	'<td><input type="text" id="iva_comision" style="text-align: center" value="0" readonly></td>'
			+	'<td colspan="4"><input type="text" id="descripcion_otros_descuentos" name="descripcion_otros_descuentos" style="width: 300px; text-align: center" /></td>'
			+	'<td>'
			+		'<input type="text" id="monto_otros_descuentos" name="monto_otros_descuentos" class="monto_otros_descuentos_clase" style="text-align: center" />'
			+		'<input type="hidden" id="total_descuentos" name="total_descuentos" readonly/>'
			+	'</td>'
			+	'<td><input type="text" id="total_a_cobrar" readonly></td>'
			+   '<td href="#" class="add-btn">+</td>'
		    + '</tr>';

            $('#listado-item-logo').on("click",".boton-verde", function(e){
        	    e.preventDefault();
        	    cantidad_detalles++;

			$(nuevo_detalle).clone().appendTo('#listado-table');
			$('#listado-logo tr:last').find('input:text').attr('id',function(i, val) { return val + cantidad_detalles;});
			$('#listado-logo tr:last').find('input:text').attr('name', function(i, val) {return val + cantidad_detalles;});

        	// $('#listado-table').append(item_detalle_factura);
        	$(this).attr('class', 'rm-btn');
        	$(this).html('-');
        	//aplicarFuncionDescuento();
    	});

	});

*/