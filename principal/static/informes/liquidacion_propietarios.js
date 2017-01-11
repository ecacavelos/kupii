function retrieve_liquidacion_propietarios() {
	// calcular_total_a_cobrar();
    // window.location.href = base_context + "/informes/liquidacion_propietarios_reporte_excel?fecha_ini=" + $('#fecha_ini').val() + "&fecha_fin=" + $('#fecha_fin').val() + "&tipo_busqueda=" + $('#id_tipo_busqueda').val() + "&busqueda=" + $('#id_busqueda').val()+ "&order_by="+$('[name="order_by"]:checked').val()+"&ley="+$('#ley').val()+"&impuesto_renta="+$('#impuesto_renta').val()+"&iva_comision="+$('#iva_comision').html()+"&descripcion_otros_descuentos="+$('#descripcion_otros_descuentos').val()+"&monto_otros_descuentos="+$('#monto_otros_descuentos').val()+"&total_a_cobrar="+$('#total_a_cobrar').html()+"&total_descuentos="+$('#total_descuentos').val();
	calcular_total_a_cobrar2();
	var descuentos= "";
	var descripcion_descuentos= "";
	var cont = 1;
	$('.monto_otros_descuentos_clase').each(function(index){
		descuentos = descuentos + "&monto_otros_descuentos" + cont + "="  + $(this).val();
		descripcion_descuentos = descripcion_descuentos + "&descripcion_otros_descuentos" + cont + "="
			+ $(this).parent().parent().find("#descripcion_otros_descuentos" + cont).val();cont = cont+1;
	});
	cont = "&cont="+(cont-1);
    window.location.href = base_context + "/informes/liquidacion_propietarios_reporte_excel?fecha_ini="
		+ $('#fecha_ini').val() + "&fecha_fin=" + $('#fecha_fin').val() + "&tipo_busqueda="
		+ $('#id_tipo_busqueda').val() + "&busqueda=" + $('#id_busqueda').val()
		+ "&order_by="+$('[name="order_by"]:checked').val() +"&ley1="+$('#ley1').val()
		+"&impuesto_renta1="+$('#impuesto_renta1').val()+"&iva_comision="+$('#iva_comision').html()
		+"&total_a_cobrar="+$('#total_a_cobrar').html()+"&total_descuentos="+$('#total_descuentos').val()
		+descuentos+descripcion_descuentos+cont;
}

function calcular_total_a_cobrar(){
	var ley = parseInt(sacarPuntos($("#ley").val()));
	if (isNaN(ley)){
		ley = 0;
	}
	var impuesto_renta = parseInt(sacarPuntos($("#impuesto_renta").val()));
	if (isNaN(impuesto_renta)){
		impuesto_renta= 0;
	}
	var iva_comision = parseInt(sacarPuntos($("#iva_comision").html()));
	if (isNaN(iva_comision)){
		iva_comision = 0;
	}
	var monto_otros_descuentos = parseInt(sacarPuntos($("#monto_otros_descuentos").val()));
	if (isNaN(monto_otros_descuentos)){
		monto_otros_descuentos = 0;
	}
	var total_general_propietario = parseInt(sacarPuntos($("#total_general_propietario").html()));
	
	$("#ley").val(ley);
	$("#impuesto_renta").val(impuesto_renta);
	$("#iva_comision").html(iva_comision);
	$("#monto_otros_descuentos").val(monto_otros_descuentos);
	total_descuentos = ley+impuesto_renta+iva_comision+monto_otros_descuentos;
	$("#total_descuentos").val(total_descuentos);
	resta = total_general_propietario-total_descuentos;
	
	var negativo = false;
	if (resta <0){
		negativo = true;
	}
	ponerPuntos(negativo, resta);
}

function calcular_total_a_cobrar2(){

	var ley = parseInt(sacarPuntos($("#ley1").val()));
	if (isNaN(ley)){
		ley = 0;
	}
	var impuesto_renta = parseInt(sacarPuntos($("#impuesto_renta1").val()));
	if (isNaN(impuesto_renta)){
		impuesto_renta= 0;
	}
	var iva_comision = parseInt(sacarPuntos($("#iva_comision").html()));
	if (isNaN(iva_comision)){
		iva_comision = 0;
	}

	var monto_otros_descuentos = 0
	$('.monto_otros_descuentos_clase').each(function(index){
		// $(this).children().each(function(index){
		// 	if ($(this).children().attr('title') == null){
		// 		if ($(this).children().val() == ""){
		// monto_otros_descuentos = monto_otros_descuentos + parseInt(sacarPuntos($("#monto_otros_descuentos").val()));
		monto_otros_descuentos = monto_otros_descuentos + parseInt(sacarPuntos($(this).val()));
		if (isNaN(monto_otros_descuentos)){
			monto_otros_descuentos = 0;
		}
		// 		}
		// 	}
		// });
	});


	// var monto_otros_descuentos = parseInt(sacarPuntos($("#monto_otros_descuentos1").val()));
	// if (isNaN(monto_otros_descuentos)){
	// 	monto_otros_descuentos = 0;
	// }

	var total_general_propietario = parseInt(sacarPuntos($("#total_general_propietario").html()));

	$("#ley1").val(ley);
	$("#impuesto_renta1").val(impuesto_renta);
	$("#iva_comision1").html(iva_comision);
	// $("#monto_otros_descuentos1").val(monto_otros_descuentos);
	total_descuentos = ley+impuesto_renta+iva_comision+monto_otros_descuentos;
	$("#total_descuentos").val(total_descuentos);
	resta = total_general_propietario-total_descuentos;

	var negativo = false;
	if (resta <0){
		negativo = true;
	}
	ponerPuntos(negativo, resta);
}

function sacarPuntos(numero){
	
	numero =numero.replace(".", "");
	numero =numero.replace(".", "");
	numero =numero.replace(".", "");
	numero =numero.replace(".", "");
	numero =numero.replace(".", "");
	
	return (numero);
}

function ponerPuntos(negativo, resta){
	$("#ley").mask('###.###.###',{reverse: true});
	$("#total_descuentos").mask('###.###.###',{reverse: true});
	$("#impuesto_renta").mask('###.###.###',{reverse: true});
	$("#monto_otros_descuentos").mask('###.###.###',{reverse: true});
	$("#iva_comision").mask('###.###.###',{reverse: true});
	valor = Math.abs(resta);
	$("#total_a_cobrar").html("");
	$("#total_a_cobrar").unmask();
	$("#total_a_cobrar").html(valor);
	$("#total_a_cobrar").mask('###.###.###',{reverse: true});
	
	if (negativo){
		total = "-"+$("#total_a_cobrar").html();
		$("#total_a_cobrar").unmask('###.###.###',{reverse: true});
		$("#total_a_cobrar").html(total);
	} else {
		total = $("#total_a_cobrar").html();
		$("#total_a_cobrar").unmask('###.###.###',{reverse: true});
		$("#total_a_cobrar").html(total);
	}
	
}

function validar() {
    if ($('#fecha_ini').val() == "" || $('#fecha_fin').val() == "") {
        alert("Debe ingresar un rango de fechas");
        return;
    }
    if ($('#fraccion_ini').val() == 0 || $('#fraccion_fin').val() == 0 || $('#fraccion_ini').val() == "" || $('#fraccion_fin').val() == "") {
        alert("Debe ingresar un rango de fracciones");
        return;
    }
    $("#frm_busqueda").submit();
}

function setup_inputs() {
	$("#id_tipo_busqueda").change(function() {
	    $("#id_busqueda_label").empty();
        $("#id_busqueda_label").val("");
        $("#id_busqueda").empty();
		autocompletes();		
	});
	$("#id_busqueda_label").change(function() {
		autocompletes();		
	});
	$("#id_fraccion_fin").change(function() {
		autocompletes();		
	});
	autocompletes();
}

function autocompletes(){
	$("#id_busqueda_label").autocomplete();
    if ($("#id_busqueda").val() == "") {
        $("#fecha_ini").prop('disabled', true);
        $("#fecha_fin").prop('disabled', true);
        $("#id_busqueda_label").prop('disabled', true);
        $("#boton_buscar").prop('disabled', true);
        $("#id_boton").attr("disabled", "disabled");
    }
    if ($("#id_tipo_busqueda").val() == "fraccion") {

        $("#fecha_ini").prop('disabled', false);
        $("#fecha_fin").prop('disabled', false);
        $("#id_busqueda_label").prop('disabled', false);
        $("#boton_buscar").prop('disabled', false);
        $("#id_boton").prop('disabled', false);
        $("#id_boton").removeAttr("disabled");

        var id_fraccion;
        $("#id_busqueda_label").empty();
        base_url = base_context + "/ajax/get_fracciones_by_name/";
        params = "value";
        $("#id_busqueda_label").autocomplete("destroy");
        $("#id_busqueda_label").autocomplete({
            source: base_url,
            minLength: 1,
            select: function (event, ui) {
                id_fraccion = ui.item.id;
                $("#id_busqueda").val(id_fraccion);
            }
        });
    }
    else if ($("#id_tipo_busqueda").val() == "propietario") {

        $("#fecha_ini").prop('disabled', false);
        $("#fecha_fin").prop('disabled', false);
        $("#id_busqueda_label").prop('disabled', false);
        $("#boton_buscar").prop('disabled', false);
        $("#id_boton").prop('disabled', false);
        $("#id_boton").removeAttr("disabled");

        var id_propietario;
        $("#id_busqueda_label").empty();
        $("#id_busqueda_label").empty('OLA');
        base_url = base_context + "/ajax/get_propietario_id_by_name/";
        params = "value";
        $("#id_busqueda_label").autocomplete("destroy");
        $("#id_busqueda_label").autocomplete({
            source: base_url,
            minLength: 1,
            create : function(){
			$(this).data('ui-autocomplete')._renderItem = function(ul,item){
				return $('<li>').append('<a>'+item.cedula +" - "+item.nombres + " "+ item.apellidos+'</a>').appendTo(ul);
				};
			},
			select : function(event, ui) {
				event.preventDefault();
                //alert('hola');
                id_propietario = ui.item.id;
                name_propietario=ui.item.nombres+" "+ui.item.apellidos;
                //alert(id_propietario);
                $('#id_busqueda').val(id_propietario);
                $('#id_busqueda_label').val(name_propietario);
            }
        });
    }
    else {
        $("#id_busqueda_label").empty();
        $("#fecha_ini").prop('disabled', true);
        $("#fecha_fin").prop('disabled', true);
        $("#id_busqueda_label").prop('disabled', true);
        $("#boton_buscar").prop('disabled', true);
        $("#id_boton").prop('disabled', true);
    }

}

var cantidad_detalles = 1;
	$(document).ready(function() {

		if (cantidad_detalles == 1){
			if ($('#monto_otros_descuentos').val() == '') {
					$('#listado-table tr:last').find('input:text').attr('id', function(i, val) {
					return val + cantidad_detalles;
				});
			}
		}

            // $('#listado-item-lote').on("click",".add-btn", function(e){
            // e.preventDefault();
            // cantidad_detalles++;
            // item_detalle_factura = '<tr>'
            // +	'<td><input type="text" id="ley-"+cantidad_detalles name="ley" style="text-align: center" value="0" /></td>'
            // +	'<td><input type="text" id="impuesto_renta" name="impuesto_renta" style="text-align: center" value="0" /></td>'
            // +	'<td><input type="text" id="iva_comision" style="text-align: center" value="0"></td>'
            // +	'<td colspan="4"><input type="text" id="descripcion_otros_descuentos" name="descripcion_otros_descuentos" style="width: 300px; text-align: center" /></td>'
            // +	'<td>'
            // +		'<input type="text" id="monto_otros_descuentos" name="monto_otros_descuentos" class="monto_otros_descuentos_clase" style="text-align: center" />'
            // +		'<input type="hidden" id="total_descuentos" name="total_descuentos" />'
            // +	'</td>'
            // +	'<td><input type="text" id="total_a_cobrar"></td>'
            // +   '<td href="#" class="add-btn">+</td>'
		    // + '</tr>';
        	 //
            // $('#listado-table').append(item_detalle_factura);
            // $(this).attr('class', 'rm-btn');
            // $(this).html('-');
            // aplicarFuncionDescuento();
	    	// });

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

			$('#listado-item-lote').on("click",".add-btn", function(e){
        	e.preventDefault();
        	cantidad_detalles++;

			$(nuevo_detalle).clone().appendTo('#listado-table');
			$('#listado-table tr:last').find('input:text').attr('id',function(i, val) { return val + cantidad_detalles;});
			$('#listado-table tr:last').find('input:text').attr('name', function(i, val) {return val + cantidad_detalles;});

        	// $('#listado-table').append(item_detalle_factura);
        	$(this).attr('class', 'rm-btn');
        	$(this).html('-');
        	aplicarFuncionDescuento();
    	});

		//4. Para eliminar un item.
		$('#listado-item-lote').on("click",".rm-btn", function(e){
        	e.preventDefault();
        	// cantidad_detalles = cantidad_detalles-1;
        	// $(this).parent('div').remove();
        	$(this).parent().remove();
			calcular_total_a_cobrar2();
    	});

	});

function aplicarFuncionDescuento(){
	$('.monto_otros_descuentos_clase').keyup(function(){
		calcular_total_a_cobrar2();
	});
}


