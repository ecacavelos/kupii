$(document).ready(function() {
	$("#id_lote").keydown(validateLotePre);
	$("#id_lote").keyup(validateLotePost);
	$("#main_recuperacion_form").submit(validateRecuperacion);
	$('#monto_cuota_venta').mask('000.000.000.000.000.000.000', {
		byPassKeys : [ null ],
		reverse : true,
	});
});

window.onload = function() {
};

// Funciones individuales
var global_lote_id = 0;
var splitted_id = "";
var lote_id = 0;
var venta_id = 0;			//ID de la venta relacionada al lote
var PrecioVenta = 0;		//Precio de venta fijado para el lote
var EntregaInicial = 0;		//Entrega inicial pagada por el lote
var TotalPagado = 0;		//Sumatoria de cuotas pagadas por el lote

function validateLotePre(event) {
	// Allow: backspace, delete, tab, escape, and enter
	if (event.keyCode == 46 || event.keyCode == 8 || event.keyCode == 9 || event.keyCode == 27 || event.keyCode == 13 ||
	// Allow: Ctrl+A
	(event.keyCode == 65 && event.ctrlKey === true) ||
	// Allow: home, end, left, right
	(event.keyCode >= 35 && event.keyCode <= 39)) {
		// let it happen, don't do anything
		return;
	} else {
		// Ensure that it is a number and stop the keypress
		if (event.shiftKey || (event.keyCode < 48 || event.keyCode > 57) && (event.keyCode < 96 || event.keyCode > 105 )) {
			event.preventDefault();
		}
	}
}

function validateLotePost(event) {
	if ((event.which >= 48 && event.which <= 57) || (event.which >= 96 && event.which <= 105)) {
		if ($("#id_lote").val().toString().length == 3 || $("#id_lote").val().toString().length == 7) {
			$("#id_lote").val($("#id_lote").val() + '/');
		}
	}
}

function validateRecuperacion(event) {

	event.preventDefault();
	var request7 = $.ajax({
		type : "POST",
		url : "/movimientos/recuperacion_lotes/",
		data : {
			recuperar_lote : true,
			recuperacion_lote_id : global_lote_id,
			recuperacion_venta_id : venta_id,
			recuperacion_fecha_de_recuperacion : $("#id_fecha").val(),
			recuperacion_cliente_id : $("#id_cliente").val(),
			recuperacion_plan_de_pago_id : $("#id_plan_pago").val(),
			recuperacion_vendedor_id : $("#id_vendedor").val(),
		}
	});
	request7.done(function(msg) {
		top.location.href = "/movimientos/listado_recuperacion";
	});
	request7.fail(function(jqXHR, textStatus) {
		alert("Se encontró un error en la recuperacion, favor verifique los datos");
	});
	return false;
}

//Separador de miles y comas en escritura
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

function retrieveLote() {
	if ($("#id_lote").val().toString().length == 12) {
		// Extraemos los identificadores correspondientes a la fraccion, manzana y lote.
		splitted_id = $("#id_lote").val().split('/');
		// Hacemos un request POST AJAX para obtener los datos del lote ingresado.
		var request = $.ajax({
			type : "GET",			
			url : "/datos/10/",
			data : {
				fraccion : splitted_id[0],
				manzana : splitted_id[1],
				lote : splitted_id[2]
			},
			dataType : "json"
		});
		// Actualizamos el formulario con los datos obtenidos del lote.
		request.done(function(msg) {
			global_lote_id = msg.lote_id;
			var s = "<a class='boton-verde' href=\"/lotes/listado/" + msg.lote_id + "\" target=\"_blank\" \">" + msg.lote_tag + "</a>";

			$("#lote_error").html("");
			sup = msg.superficie.replace(".",",");
			$("#lote_superficie").html(sup);
			$("#lote_superficie").html(String(format.call($("#lote_superficie").html().split(' ').join(''),'.',',')));
			$("#lote_seleccionado_detalles").html(s);
			
			lote_id = msg.lote_id;
			var d = new Date();
			var month = d.getMonth() + 1;
			var day = d.getDate();
			retrieveVenta();
			fecha_actual = new Date().toJSON().substring(0, 10);
		});
		// En caso de no poder obtener los datos del lote, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			$("#lote_error").html("El Lote no existe o no fue vendido ni reservado.");
		});
	} else {
		if ($("#id_lote").val().toString().length > 0) {
			$("#lote_error").html("No se encuentra el Lote indicado.");
		}
	}
}

function retrieveVenta() {
		var request = $.ajax({
			type : "GET",
			url : "/ajax/get_ventas_by_lote/",
			data : {
				lote_id : lote_id,
			},
			dataType : "json"
		});
		// Actualizamos el formulario con los datos obtenidos del lote.
		request.done(function(msg) {
			$("#cant_cuotas_venta").html(msg.venta[0]['pagos_realizados']);
			$("#monto_cuota_venta").html(msg.venta[0]['precio_de_cuota']);
			$("#id_cliente").val(msg.venta[0]['cliente_id']);
			$("#cliente_seleccionado").val(msg.venta[0]['cliente']);
			$("#id_vendedor").val(msg.venta[0]['vendedor_id']);
			$("#vendedor_seleccionado").val(msg.venta[0]['vendedor']);
			$("#plan_pago").val(msg.venta[0]['plan_de_pago']);
			$("#id_plan_pago").val(msg.venta[0]['plan_de_pago_id']);
			venta_id = (msg.venta[0]['venta_id']);
			PrecioVenta = (msg.venta[0]['precio_de_venta']);
			EntregaInicial = (msg.venta[0]['entrega_inicial']);
			$('#monto_cuota_venta').mask('000.000.000.000.000.000.000', {
				byPassKeys : [ null ],
				reverse : true,
			});
			retrievePagos();
		});
		request.fail(function(jqXHR, textStatus) {
			alert("El lote no está vendido");
			$("#id_lote").select().focus();
		});
//	}
}

function retrieveCliente() {
	if ($("#id_cliente").val().toString().length > 0) {
		// Hacemos un request POST AJAX para obtener los datos del cliente ingresado.
		var request = $.ajax({
			type : "GET",
			url : "/datos/2/",
			data : {
				cliente : $("#id_cliente").val()
			}
		});
		// Actualizamos el formulario con los datos obtenidos del cliente.
		request.done(function(msg) {
			$("#cliente_error").html("");
			$("#cliente_seleccionado").html(msg);
			retrieveVendedor();

		});
		// En caso de no poder obtener los datos del cliente, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			$("#cliente_error").html("No se pueden obtener los datos del Cliente.");
			$("#cliente_seleccionado").html("");
			$("#id_cliente").select().focus();
		});
	}
}

function retrieveVendedor() {
	if ($("#id_vendedor").val().toString().length > 0) {
		// Hacemos un request POST AJAX para obtener los datos del vendedor ingresado.
		var request = $.ajax({
			type : "GET",
			url : "/datos/3/",
			data : {
				vendedor : $("#id_vendedor").val()
			}
		});
		// Actualizamos el formulario con los datos obtenidos del vendedor.
		request.done(function(msg) {
			$("#vendedor_error").html("");
			$("#vendedor_seleccionado").html(msg);
			retrievePlanPago();

		});
		// En caso de no poder obtener los datos del vendedor, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			$("#vendedor_error").html("No se pueden obtener los datos del Vendedor.");
			$("#vendedor_seleccionado").html("");
			$("#id_vendedor").select().focus();
		});
	}
}

function retrievePlanPago() {
	if ($("#id_plan_pago").val().toString().length > 0) {
		// Hacemos un request POST AJAX para obtener los datos del plan de pagos ingresado.
		var request = $.ajax({
			type : "GET",
			url : "/datos/5/",
			data : {
				plan_pago : $("#id_plan_pago").val(),
			}
		});
		// Actualizamos el formulario con los datos obtenidos del plan de pagos.
		request.done(function(msg) {
			$("#plan_pago_error").html("");
			$("#plan_pago_seleccionado").html(msg.nombre_del_plan);

		});
		// En caso de no poder obtener los datos del plan de pagos, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			$("#plan_pago_error").html("No se pueden obtener los datos del Plan de Pago.");
			$("#plan_pago_seleccionado").html("");
			$("#id_plan_pago").select().focus();
		});
	}
}

function retrievePagos() {
	//if ($("#lote_id").val().toString().length > 0) {
		var request = $.ajax({
			type : "GET",
			url : "/ajax/get_pagos_by_venta/",
			data : {
				venta_id : venta_id,
			},
			dataType : "json"
		});
		// Actualizamos el formulario con los datos obtenidos del lote.
		request.done(function(msg) {
			var length = msg.length;
			var TotalPagado = 0;
			for(var i=0; i < length; i++){
    			TotalPagado += msg[i]['total_de_cuotas'];  
			}
			//alert(TotalPagado);
			retrieveCliente();
		});
		recuperable();
//	}	
}

function recuperable() {
	if (TotalPagado <= ((PrecioVenta/4) - EntregaInicial) ) {
		$("#recuperar_lote").removeAttr("disabled");
		$("#recuperar_lote").focus();
	}
	else {
		$("#recuperar_lote").attr("disabled", "disabled");
		alert("Lote no recuperable, se pagó más del 25% del valor del mismo");
	}
}
