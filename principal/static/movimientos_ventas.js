$(document).ready(function() {
	$("#fecha_hasta").hide();
	$("#id_lote").keydown(validateLotePre);
	$("#id_lote").keyup(validateLotePost);
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

	
	//autocomplete para cliente
	var cliente_id;
	$("#id_name_cliente").empty();
	base_url = "/ajax/get_cliente_id_by_name/";
	params = "value";
	$("#id_name_cliente").autocomplete({
		source : base_url,
		minLength : 1,
		select : function(event, ui) {
			id_cliente = ui.item.id;
			cedula_cliente= ui.item.cedula;
			$("#id_cliente").val(id_cliente);
			$("#id_cedula_cliente").val(cedula_cliente);

		}
	});
		
	//autocomplete para cedula
	var cliente_id;
	$("#id_cedula_cliente").empty();
	base_url = "/ajax/get_cliente_name_id_by_cedula/";
	params = "value";
	$("#id_cedula_cliente").autocomplete({
		source : base_url,
		minLength : 1,
		select : function(event, ui) {
			id_cliente = ui.item.id;
			name_cliente= ui.item.label;
			cedula_cliente= ui.item.cedula;
			ui.item.value = ui.item.cedula;
			$("#id_cliente").val(id_cliente);
			$("#id_name_cliente").val(name_cliente);
			$("#id_cedula_cliente").val(cedula_cliente);
				
		}
	});
		

//autocomplete para vendedor
	var vendedor_id;
	$("#id_name_vendedor").empty();
	base_url = "/ajax/get_vendedor_id_by_name/";
	params = "value";
	$("#id_name_vendedor").autocomplete({
		source : base_url,
		minLength : 1,
		select : function(event, ui) {
			id_vendedor = ui.item.id;
			cedula_vendedor= ui.item.cedula;
			$("#id_vendedor").val(id_vendedor);
			$("#id_cedula_vendedor").val(cedula_vendedor);

		}
	});
		
	//autocomplete para cedula
	var cliente_vendedor;
	$("#id_cedula_vendedor").empty();
	base_url = "/ajax/get_vendedor_name_id_by_cedula/";
	params = "value";
	$("#id_cedula_vendedor").autocomplete({
		source : base_url,
		minLength : 1,
		select : function(event, ui) {
			id_vendedor = ui.item.id;
			name_vendedor= ui.item.label;
			cedula_vendedor= ui.item.cedula;
			ui.item.value = ui.item.cedula;
			$("#id_vendedor").val(id_vendedor);
			$("#id_name_vendedor").val(name_vendedor);
			$("#id_cedula_vendedor").val(cedula_vendedor);
				
		}
	});
	

	var id_plan_pago;
	$("#id_plan_pago").empty();
	var get_all_planes = $.ajax({
		url : '/datos/7/',
		type : "GET",
		data : {
			id_plan_pago : id_plan_pago
		},
		dataType : "json"
	});
	get_all_planes.done(function(data) {
		$("#id_plan_pago").append('<option value="0">Elija un plan de pago</option>');
		$.each(data, function(index, value) {

			$("#id_plan_pago").append('<option value="' + value.id + '">' + 'Plan ' + value.label + '</option>');
		});
	});
	$("#id_plan_pago").attr('readonly', true);

	var id_plan_pago_vendedores;
	$("#id_plan_pago_vendedores").empty();
	var get_all_planes_vendedores = $.ajax({
		url : '/datos/13/',
		type : "GET",
		data : {
			id_plan_pago_vendedores : id_plan_pago_vendedores
		},
		dataType : "json"
	});
	get_all_planes_vendedores.done(function(data) {
		$("#id_plan_pago_vendedores").append('<option value="0">Elija un plan de pago</option>');
		$.each(data, function(index, value) {

			$("#id_plan_pago_vendedores").append('<option value="' + value.id + '">' + 'Plan ' + value.label + '</option>');
		});
	});
	$("#id_plan_pago_vendedores").attr('readonly', true);

	function solo_numeros_puntos_precio_venta() {
		$('#id_precio_venta').val($('#id_precio_venta').val().replace(/[^\d.]+/g, ''));
	}

	function solo_numeros_puntos_entrega_inicial() {
		$('#id_entrega_inicial ').val($('#id_entrega_inicial ').val().replace(/[^\d.]+/g, ''));
	}

	function solo_numeros_puntos_monto_cuota() {
		$('#id_monto_cuota ').val($('#id_monto_cuota ').val().replace(/[^\d.]+/g, ''));
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
		//} else {
		//	numeric = numeric.substr(0,numeric.length-1);
		//}

		return numeric + decimal;
	}

});

window.onload = function() {
	//document.getElementById("id_lote").onblur = retrieveLote;
	//document.getElementById("id_cliente").onblur = retrieveCliente;
};

// Funciones individuales
var global_lote_id = 0;
var monto_final_validado = false;
var entrega_inicial = 0;
var monto_cuota = 0;
var estado_lote = "";

function validateVenta(event) {

	event.preventDefault();
	if (monto_final_validado == true) {
		var res_venta = $("#id_precio_venta").val();
		var res_cuota = $("#id_monto_cuota").val();
		var res_entrega = $("#id_entrega_inicial").val();
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
		var request2 = $.ajax({
			type : "POST",
			url : "/movimientos/ventas_lotes/",
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
				estado_lote : estado_lote

			}

		});
		request2.done(function(msg) {
			alert("Se procesó la venta satisfactoriamente.");
			top.location.href = "/movimientos/listado_ventas/";
		});
		request2.fail(function(jqXHR, textStatus) {
			alert("Error en la solicitud.");
		});
	} else {
		alert("Por favor introduzca el monto.");
	}

};

function calculatePrecioFinalVentaLote() {

	//var res ="";
	var res_venta = $("#id_precio_venta").val();
	var res_cuota = $("#id_monto_cuota").val();
	var res_entrega = $("#id_entrega_inicial").val();
	for ( i = 0; i < res_venta.length; i++) {
		res_venta = res_venta.replace(".", "");
	}
	for ( i = 0; i < res_cuota.length; i++) {
		res_cuota = res_cuota.replace(".", "");
	}
	for ( i = 0; i < res_entrega.length; i++) {
		res_entrega = res_entrega.replace(".", "");
	}
	var request = $.ajax({
		type : "GET",
		url : "/movimientos/ventas_lotes/calcular_cuotas/",
		datatype : "json,",
		data : {
			calcular_cuotas : true,
			plan_pago_establecido : $("#id_plan_pago").val(),
			precio_de_venta : res_venta,
			entrega_inicial : res_entrega,
			monto_cuota : res_cuota ,
		}
	});
	request.complete(function(msg) {
		//$("#precio_final_venta").html(msg.responseJSON.monto_total);
		//$("#precio_final_venta").html(format.call($('#precio_final_venta').html().split(' ').join(''),'.',','));
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
			url : "/datos/12/",
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

			$("#lote_error").html("");
			sup = msg.superficie.replace(".", ",");
			$("#lote_superficie").html(sup);
			//alert("hola");
			$("#lote_superficie").html(String(format.call($("#lote_superficie").html().split(' ').join(''), '.', ',')));
			$("#lote_seleccionado_detalles").html(s);
			precio_contado = msg.precio_contado;
			precio_credito = msg.precio_credito;
			estado_lote = msg.estado_lote;
			var d = new Date();
			var month = d.getMonth() + 1;
			var day = d.getDate();

			//fecha_actual = (day < 10 ? '0' : '') + day + '/' + (month < 10 ? '0' : '') + month + '/' + d.getFullYear();
			//fecha_actual = new Date().toJSON().substring(0, 10);

			//$("#id_fecha").val(fecha_actual);

			$("#id_nombre_cliente").removeAttr("disabled");
			//$("#id_cliente").focus();
		});
		// En caso de no poder obtener los datos del lote, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			//alert("Request failed: " + jqXHR);
			$("#lote_error").html("El Lote no existe o fue vendido.");
		});
	} else {
		if ($("#id_lote").val().toString().length > 0) {
			$("#lote_error").html("No se encuentra el Lote indicado.");
		}
	}
};

function calculateMontoCuotas() {
	var res_entrega = $("#id_entrega_inicial").val();
	var res_cuota = $("#id_monto_cuota").val();
	var precio_venta = $("#id_precio_venta").val();

	for ( i = 0; i < precio_venta.length; i++) {
		precio_venta = precio_venta.replace(".", "");
	}
	for ( i = 0; i < res_entrega.length; i++) {
		res_entrega = res_entrega.replace(".", "");
	}
	for ( i = 0; i < res_cuota.length; i++) {
		res_cuota = res_cuota.replace(".", "");
	}
	var entrega_inicial = res_entrega;
	entrega_inicial = parseInt(entrega_inicial);
	precio_venta = parseInt(precio_venta);
	console.log("precio_credito: " + precio_credito);
	console.log("entrega_inicial: " + entrega_inicial);
	console.log("cantidad_credito: " + cantidad_cuotas);
	var monto_cuota = Math.ceil((precio_venta - entrega_inicial) / cantidad_cuotas);
	//monto_cuota = Math.round(monto_cuota);
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
