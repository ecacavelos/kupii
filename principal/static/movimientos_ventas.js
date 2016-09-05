$(document).ready(function() {
	//var deshabilitar = true;
	$("#fecha_hasta").hide();
	$("#id_lote").keydown(validateLotePre);
	$("#id_lote").focus();
	$("#id_lote").keyup(validateLotePost);
	$("#id_monto_cuota_refuerzo").val("0");
	$("#main_venta_form").submit(validateVenta);

	$('.grid_6').hide();
	$('#id_fecha').mask('##/##/####');
	$("#id_fecha").datepicker({
		dateFormat : 'dd/mm/yy'
	});
	$('#id_fecha_venta2').mask('##/##/####');
	$("#id_fecha_venta2").datepicker({
		dateFormat : 'dd/mm/yy'
	});
	
	$("#enviar_venta").hide();
	$("#enviar_venta_factura").hide();
	
	$(function($){
		    $.datepicker.regional['es'] = {
		        closeText: 'Cerrar',
		        prevText: '<Ant',
		        nextText: 'Sig>',
		        currentText: 'Hoy',
		        monthNames: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
		        monthNamesShort: ['Ene','Feb','Mar','Abr', 'May','Jun','Jul','Ago','Sep', 'Oct','Nov','Dic'],
		        dayNames: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
		        dayNamesShort: ['Dom','Lun','Mar','Mié','Juv','Vie','Sáb'],
		        dayNamesMin: ['Do','Lu','Ma','Mi','Ju','Vi','Sá'],
		        weekHeader: 'Sm',
		        dateFormat: 'dd/mm/yy',
		        firstDay: 1,
		        isRTL: false,
		        showMonthAfterYear: false,
		        yearSuffix: ''
		    };
		    $.datepicker.setDefaults($.datepicker.regional['es']);
		});

	
	//autocomplete para cliente
	var cliente_id;
	$("#id_name_cliente").empty();
	base_url = base_context + "/ajax/get_cliente_id_by_name/";
	params = "value";
	$("#id_name_cliente").autocomplete({
		source : base_url,
		minLength : 1,
		create : function(){
			$(this).data('ui-autocomplete')._renderItem = function(ul,item){
				return $('<li>').append('<a>'+item.cedula +" - "+item.nombres + " "+ item.apellidos+'</a>').appendTo(ul);
				};
		},
		select : function(event, ui) {
			event.preventDefault();
			id_cliente = ui.item.id;
			cedula_cliente= ui.item.cedula;
			$("#id_cliente").val(id_cliente);
			$("#id_cedula_cliente").val(cedula_cliente);
			name_cliente=ui.item.nombres+" "+ui.item.apellidos;
			$("#id_name_cliente").val(name_cliente);

		}
	});
		
	//autocomplete para cedula
	var cliente_id;
	$("#id_cedula_cliente").empty();
	base_url = base_context + "/ajax/get_cliente_name_id_by_cedula/";
	params = "value";
	$("#id_cedula_cliente").autocomplete({
		source : base_url,
		minLength : 1,
		create : function(){
			$(this).data('ui-autocomplete')._renderItem = function(ul,item){
				return $('<li>').append('<a>'+item.cedula +" - "+item.nombres + " "+ item.apellidos+'</a>').appendTo(ul);
				};
		},
		select : function(event, ui) {
			event.preventDefault();
			id_cliente = ui.item.id;
			cedula_cliente= ui.item.cedula;
			$("#id_cliente").val(id_cliente);
			$("#id_cedula_cliente").val(cedula_cliente);
			name_cliente=ui.item.nombres+" "+ui.item.apellidos;
			$("#id_name_cliente").val(name_cliente);

		}
	});
		

//autocomplete para vendedor
	var vendedor_id;
	$("#id_name_vendedor").empty();
	base_url = base_context + "/ajax/get_vendedor_id_by_name/";
	params = "value";
	$("#id_name_vendedor").autocomplete({
		source : base_url,
		minLength : 1,
		create : function(){
			$(this).data('ui-autocomplete')._renderItem = function(ul,item){
				return $('<li>').append('<a>'+item.cedula +" - "+item.nombres + " "+ item.apellidos+'</a>').appendTo(ul);
				};
		},
		select : function(event, ui) {
			event.preventDefault();
			id_vendedor = ui.item.id;
			cedula_vendedor= ui.item.cedula;
			$("#id_vendedor").val(id_vendedor);
			$("#id_cedula_vendedor").val(cedula_vendedor);
			name_vendedor=ui.item.nombres+" "+ui.item.apellidos;
			$("#id_name_vendedor").val(name_vendedor);
		}
	});
		
	//autocomplete para cedula
	var cliente_vendedor;
	$("#id_cedula_vendedor").empty();
	base_url = base_context + "/ajax/get_vendedor_name_id_by_cedula/";
	params = "value";
	$("#id_cedula_vendedor").autocomplete({
		source : base_url,
		minLength : 1,
		create : function(){
			$(this).data('ui-autocomplete')._renderItem = function(ul,item){
				return $('<li>').append('<a>'+item.cedula +" - "+item.nombres + " "+ item.apellidos+'</a>').appendTo(ul);
				};
		},
		select : function(event, ui) {
			event.preventDefault();
			id_vendedor = ui.item.id;
			cedula_vendedor= ui.item.cedula;
			$("#id_vendedor").val(id_vendedor);
			$("#id_cedula_vendedor").val(cedula_vendedor);
			name_vendedor=ui.item.nombres+" "+ui.item.apellidos;
			$("#id_name_vendedor").val(name_vendedor);
		}
	});
	

	//autocomplete para planes de pago
	var id_plan_pago;
	$("#id_plan_pago").empty();
	base_url= base_context + "/ajax/get_plan_pago/";
	params="value";
	$("#id_plan_p").autocomplete({
		source : base_url,
		minLenght : 1,
		select : function(event, ui) {
			id_plan = ui.item.id;
			name_plan= ui.item.label;
			ui.item.value = ui.item.label;
			$("#id_plan_p").val(name_plan);
			$("#id_plan_pago").val(id_plan);
			$("#id_cant_cuotas_ref").val(ui.item.cuotas_de_refuerzo);
			retrievePlanPago();				
		}
	});
	
	//autocomplete para planes de pago de vendedores
	var id_plan_pago_vendedores;
	$("#id_plan_pago_vendedores").empty();
	base_url= base_context + "/ajax/get_plan_pago_vendedor/";
	params="value";
	$("#id_plan_pv").autocomplete({
		source : base_url,
		minLenght : 1,
		select : function(event, ui) {
			id_plan = ui.item.id;
			name_plan= ui.item.label;
			ui.item.value = ui.item.label;
			$("#id_plan_pv").val(name_plan);
			$("#id_plan_pago_vendedores").val(id_plan);
		}
	});
	
	

});

window.onload = function() {
};

// Funciones individuales
var global_lote_id = 0;
var monto_final_validado = false;
var entrega_inicial = 0;
var monto_cuota = 0;
var estado_lote = "";

function validateVenta() {
	if (monto_final_validado == true) {
		var res_venta = $("#id_precio_venta").val();
		var res_cuota = $("#id_monto_cuota").val();
		var res_entrega = $("#id_entrega_inicial").val();
		var res_refuerzo = $("#id_monto_cuota_refuerzo").val();
		//var res ="";
		for ( i = 0; i < res_venta.length; i++) {
			res_venta = res_venta.replace(".", "");
		}
		for ( i = 0; i < res_cuota.length; i++) {
			res_cuota = res_cuota.replace(".", "");
		}
		for ( i = 0; i < res_entrega.length; i++) {
			res_entrega = res_entrega.replace(".", "");
		}
		for ( i = 0; i < res_refuerzo.length; i++) {
			res_refuerzo = res_refuerzo.replace(".", "");
		}
		var cedula ="";
		if ($("#id_cliente").val() == ""){
			cedula = $('#id_cedula_cliente').val();
			$('#enviar_venta').removeAttr('disabled');
			return false;
		}
		
		if ($("#id_fecha_vencimiento").val() == ""){
			alert("Ingrese una fecha de vencimiento");
			$('#enviar_venta').removeAttr('disabled');
			return false;
		}
		var request2 = $.ajax({
			type : "POST",
			url : base_context + "/movimientos/ventas_lotes/",
			data : {
				ingresar_venta : true,
				venta_lote_id : global_lote_id,
				venta_fecha_de_venta : $("#id_fecha").val(),
				venta_cliente_id : $("#id_cliente").val(),
				venta_vendedor_id : $("#id_vendedor").val(),
				venta_plan_pago_id : $("#id_plan_pago").val(),
				venta_plan_pago_vendedor_id : $("#id_plan_pago_vendedores").val(),
				venta_entrega_inicial : res_entrega,
				venta_precio_de_cuota : res_cuota,
				venta_precio_final_de_venta : res_venta,
				venta_fecha_primer_vencimiento : $("#id_fecha_vencimiento").val(),
				venta_pagos_realizados : 0,
				estado_lote : estado_lote,
				venta_cedula_cli: cedula,
				monto_refuerzo: res_refuerzo
			}

		}).done(function (data) {
			if ( $("#facturar").val() == '' ){
				top.location.href = base_context + "/movimientos/pago_cuotas_venta/"+data[0].id;
			} else if ( $("#facturar").val() == 'SI'  ){
				top.location.href = base_context + "/facturacion/facturar_operacion/2/"+data[0].id;
			}
		});
		/*request2.done(function(msg) {
			top.location.href = "/movimientos/listado_ventas/";
		});*/
		request2.fail(function(jqXHR, textStatus) {
			alert("Error en la solicitud.");
			$('#enviar_venta').removeAttr('disabled');
			return false;
		});
		
	} else {
		alert("Por favor introduzca el monto.");
		$('#enviar_venta').removeAttr('disabled');
		return false;
	}

};

function calculatePrecioFinalVentaLote() {

	//var res ="";
	var res_venta = $("#id_precio_venta").val();
	var res_cuota = $("#id_monto_cuota").val();
	var res_entrega = $("#id_entrega_inicial").val();
	var res_refuerzo = $("#id_monto_cuota_refuerzo").val();
	
	for ( i = 0; i < res_venta.length; i++) {
		res_venta = res_venta.replace(".", "");
	}
	for ( i = 0; i < res_cuota.length; i++) {
		res_cuota = res_cuota.replace(".", "");
	}
	for ( i = 0; i < res_entrega.length; i++) {
		res_entrega = res_entrega.replace(".", "");
	}
	for ( i = 0; i < res_refuerzo.length; i++) {
		res_refuerzo = res_refuerzo.replace(".", "");
	}
	var request = $.ajax({
		type : "GET",
		url : base_context + "/movimientos/ventas_lotes/calcular_cuotas/",
		datatype : "json,",
		data : {
			calcular_cuotas : true,
			plan_pago_establecido : $("#id_plan_pago").val(),
			precio_de_venta : res_venta,
			entrega_inicial : res_entrega,
			monto_cuota : res_cuota,
			monto_refuerzo : res_refuerzo
		}
	});
	request.complete(function(msg) {
		$("#precio_final_venta").html($("#id_precio_venta").val());
		monto_final_validado = msg.responseJSON.monto_valido;
		if (msg.responseJSON.monto_valido == false) {
			$("#precio_final_venta").attr("class", "error");

			$("#enviar_venta").attr("disabled", "disabled");
		} else {
			$("#precio_final_venta").removeAttr("class");
			$("#enviar_venta").removeAttr("disabled");
		}
	});
	request.fail(function(jqXHR, textStatus) {
		$("#monto_total_error").html("Error.");
	});

};

function retrieveLoteVenta() {
	if ($("#id_lote").val().toString().length == 12) {
		// Extraemos los identificadores correspondientes a la fraccion, manzana y lote.
		splitted_id = $("#id_lote").val().split('/');
		// Hacemos un request POST AJAX para obtener los datos del lote ingresado.
		var request = $.ajax({
			type : "GET",
			url : base_context + "/datos/12/",
			data : {
				fraccion : splitted_id[0],
				manzana : splitted_id[1],
				lote : splitted_id[2]
			},
			dataType : "json"
		});
		retrieveFraccion();
		// Actualizamos el formulario con los datos obtenidos del lote.
		request.done(function(msg) {
			global_lote_id = msg.lote_id;
			var s = "<a class='boton-verde' href=\"/lotes/listado/" + msg.lote_id + "\" target=\"_blank\" \">" + msg.lote_tag + "</a>";
			if(msg.estado_lote == '1' || msg.estado_lote == '2' || msg.estado_lote =='4'){
				$("#lote_error").html("");
				sup = msg.superficie.replace(".", ",");
				$("#lote_superficie").html(sup);
				$("#lote_superficie").html(String(format.call($("#lote_superficie").html().split(' ').join(''), '.', ',')));
				$("#lote_seleccionado_detalles").html(s);
				precio_contado = msg.precio_contado;
				precio_credito = msg.precio_credito;
				estado_lote = msg.estado_lote;
				var d = new Date();
				var month = d.getMonth() + 1;
				var day = d.getDate();
				$("#id_nombre_cliente").removeAttr("disabled");
			}else if (msg.estado_lote == '3' || msg.estado_lote == '5' || msg.estado_lote == '6'){
				$("#lote_error").html("El Lote fue vendido.");
			}else{
				$("#lote_error").html("El Lote no existe.");
			}						
		});
	} else {
		if ($("#id_lote").val().toString().length > 0) {
			$("#lote_error").html("No se encuentra el Lote indicado.");
		}
	}
};

function quitarCerosFraccion(fraccion) {
	centena = fraccion.substr(0,1);
	decena = fraccion.substr(1,1);
	//si la centena es cero, quito la decena y unidad
	if (centena == 0){
		fraccion = fraccion.substr(1,2)
		//si la decena tb es cero, dejo solo la unidad, y como ya recorte mi fraccion, los limites de start y lenght tb cambian para la funcion del substr
		if (decena == 0){
			fraccion = fraccion.substr(1,1)
		}
	}
	return fraccion;
}

function quitarCerosLote(lote) {
	unidadMil = lote.substr(0,1);
	centena = lote.substr(1,1);
	decena = lote.substr(2,1);
	//si la unidad de mil es cero, quito la centena, decena y unidad
	if (unidadMil == 0){
		lote = lote.substr(1,3)
		//si la centena es cero, quito la decena y unida
		if (centena == 0){
			lote = lote.substr(1,3)
			//si la decena tb es cero, dejo solo la unidad, y como ya recorte mi lote, los limites de start y lenght tb cambian para la funcion del substr
			if (decena == 0){
				lote = lote.substr(1,1)
			}
		}
	}
	return lote;
}

function calculateMontoCuotas() {
	var res_entrega = $("#id_entrega_inicial").val();
	var res_cuota = $("#id_monto_cuota").val();
	var precio_venta = $("#id_precio_venta").val();
	var res_refuerzo = $("#id_monto_cuota_refuerzo").val();
	var cantidad_cuotas_ref = $("#id_cant_cuotas_ref").val();
	for ( i = 0; i < precio_venta.length; i++) {
		precio_venta = precio_venta.replace(".", "");
	}
	for ( i = 0; i < res_entrega.length; i++) {
		res_entrega = res_entrega.replace(".", "");
	}
	for ( i = 0; i < res_cuota.length; i++) {
		res_cuota = res_cuota.replace(".", "");
	}
	for ( i = 0; i < res_refuerzo.length; i++) {
		res_refuerzo = res_refuerzo.replace(".", "");
	}
	var entrega_inicial = res_entrega;
	entrega_inicial = parseInt(entrega_inicial);
	precio_venta = parseInt(precio_venta);
	var monto_ref = parseInt(res_refuerzo) * parseInt(cantidad_cuotas_ref);
	var cuotas_restantes = cantidad_cuotas - cantidad_cuotas_ref
	console.log("precio_credito: " + precio_credito);
	console.log("entrega_inicial: " + entrega_inicial);
	console.log("cantidad_credito: " + cantidad_cuotas);
	var monto_cuota = Math.ceil((precio_venta - (entrega_inicial + monto_ref)) / cuotas_restantes);
	if (precio_venta < entrega_inicial) {
		alert("La entrega inicial debe ser menor al precio de venta.");
		$("#id_monto_cuota").val("");
		$("#precio_final_venta").html("");

	} else {
		console.log("monto_cuota: " + monto_cuota);
		$("#id_monto_cuota").val(monto_cuota);
		$("#id_monto_cuota").val(format.call($('#id_monto_cuota').val().split(' ').join(''), '.', ','));
		$("#monto_total_error").html("");
	}
};

function solo_numeros_puntos_precio_venta() {
		$('#id_precio_venta').val($('#id_precio_venta').val().replace(/[^\d.]+/g, ''));
	}

	function solo_numeros_puntos_entrega_inicial() {
		$('#id_entrega_inicial ').val($('#id_entrega_inicial ').val().replace(/[^\d.]+/g, ''));
	}

	function solo_numeros_puntos_monto_cuota() {
		$('#id_monto_cuota ').val($('#id_monto_cuota ').val().replace(/[^\d.]+/g, ''));
	}
	
	function solo_numeros_puntos_monto_refuerzo() {
		$('#id_monto_cuota_refuerzo ').val($('#id_monto_cuota_refuerzo ').val().replace(/[^\d.]+/g, ''));
	}
	function format(comma, period) {

		var comma = comma || ',';
		var period = period || '.';
		var split = this.toString().split(',');
		var numeric = split[0];
		var decimal = split.length > 1 ? period + split[1] : '';
		var reg = /(\d+)(\d{3})/;
		for (var i = 1; i < numeric.length; i++) {
			numeric = numeric.replace(".", "");
		}
		while (reg.test(numeric)) {

			numeric = numeric.replace(reg, '$1' + comma + '$2');
		}
		return numeric + decimal;
	}
