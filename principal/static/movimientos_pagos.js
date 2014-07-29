$(document).ready(function() {
	$("#fecha_hasta").hide();
	$("#id_lote").keydown(validateLotePre);
	$("#id_lote").keyup(validateLotePost);
	
	//$("#enviar_reserva").click(validateReserva);

	$("#main_pago_form").submit(validatePago);
});

window.onload = function() {
	//document.getElementById("id_lote").onblur = retrieveLote;
	//document.getElementById("id_cliente").onblur = retrieveCliente;
};

// Funciones individuales
var global_lote_id = 0;
var splitted_id = "";
var lote_id = 0;
var pagos_realizados = 0;
var venta_id = 0;

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
		//} else {
		//	numeric = numeric.substr(0,numeric.length-1);
		//}
		
		return numeric + decimal;
	}

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

function validatePago(event) {

	event.preventDefault();
	var request4 = $.ajax({
		type : "POST",
		url : "/movimientos/pago_cuotas/",
		data : {
			ingresar_pago : true,
			pago_venta_id : venta_id,
			pago_lote_id : global_lote_id,
			pago_fecha_de_pago : $("#id_fecha").val(),
			pago_nro_cuotas_a_pagar : $("#nro_cuotas_a_pagar").val(),
			pago_cliente_id : $("#id_cliente").val(),
			pago_plan_de_pago_id : $("#id_plan_pago").val(),
			pago_plan_de_pago_vendedor_id: $("#id_plan_pago_vendedores").val(),
			pago_vendedor_id : $("#id_vendedor").val(),
			pago_total_de_cuotas : $("#total_cuotas").val(),
			pago_total_de_mora : $("#total_mora").val(),
			pago_total_de_pago : $("#total_pago").val(),
		}
	});
	request4.done(function(msg) {
		alert("Se procesó el pago exitosamente.");
		top.location.href = "/movimientos/pago_cuotas";
	});
	request4.fail(function(jqXHR, textStatus) {
		//console.log(request4);
		if (jqXHR.responseText == "La cantidad de cuotas a pagar, es mayor a la cantidad de cuotas restantes."){
			alert(jqXHR.responseText);	
		} else {
			alert("Se encontró un error en el pago, favor verifique los datos");
		}
		
	});
	
	return false;
}

function retrieveLote() {
	if ($("#id_lote").val().toString().length == 12) {
		// Extraemos los identificadores correspondientes a la fraccion, manzana y lote.
		splitted_id = $("#id_lote").val().split('/');
		// Hacemos un request POST AJAX para obtener los datos del lote ingresado.
		var request = $.ajax({
			type : "GET",
			url : "/datos/1/",
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
			$("#lote_superficie").html(msg.superficie);
			$("#lote_seleccionado_detalles").html(s);
			lote_id = msg.lote_id;
			var d = new Date();
			var month = d.getMonth() + 1;
			var day = d.getDate();
			retrieveVenta();
			//fecha_actual = (day < 10 ? '0' : '') + day + '/' + (month < 10 ? '0' : '') + month + '/' + d.getFullYear();
			fecha_actual = new Date().toJSON().substring(0, 10);

			$("#id_fecha").val(fecha_actual);
			$("#id_cliente").removeAttr("disabled");
			//$("#id_cliente").focus();
			$("#id_vendedor").removeAttr("disabled");
			//$("#id_vendedor").focus();
			$("#id_plan_pago").removeAttr("disabled");
			//$("#id_plan_pago").focus();
			$("#id_monto").removeAttr("disabled");
			//$("#nro_cuotas_a_pagar").focus();
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
}

function retrieveLotePago() {
	if ($("#id_lote").val().toString().length == 12) {
		// Extraemos los identificadores correspondientes a la fraccion, manzana y lote.
		splitted_id = $("#id_lote").val().split('/');
		// Hacemos un request POST AJAX para obtener los datos del lote ingresado.
		var request = $.ajax({
			type : "GET",
			url : "/datos/9/",
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
			$("#lote_superficie").html(msg.superficie);
			$("#lote_seleccionado_detalles").html(s);
			lote_id = msg.lote_id;
			var d = new Date();
			var month = d.getMonth() + 1;
			var day = d.getDate();
			retrieveVenta();
			//alert("llegue");
			
			//fecha_actual = (day < 10 ? '0' : '') + day + '/' + (month < 10 ? '0' : '') + month + '/' + d.getFullYear();
			fecha_actual = new Date().toJSON().substring(0, 10);

			//$("#id_fecha").val(fecha_actual);
			$("#id_cliente").removeAttr("disabled");
			//$("#id_cliente").focus();
			$("#id_vendedor").removeAttr("disabled");
			//$("#id_vendedor").focus();
			$("#id_plan_pago").removeAttr("disabled");
			$("#id_plan_pago_vendedores").removeAttr("disabled");
			//$("#id_plan_pago").focus();
			$("#id_monto").removeAttr("disabled");
			//$("#nro_cuotas_a_pagar").focus();
		});
		// En caso de no poder obtener los datos del lote, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			//alert("Request failed: " + jqXHR);
			$("#lote_error").html("Lote inválido.");
		});
	} else {
		if ($("#id_lote").val().toString().length > 0) {
			$("#lote_error").html("No se encuentra el Lote indicado.");
		}
	}
}

function retrieveVenta() {
	//if ($("#lote_id").val().toString().length > 0) {
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
			msgaux = msg;
			msg = msg.venta;
			venta_id = (msg[0]['venta_id']);
			$("#id_venta_pagos").val(venta_id);
			$("#id_cliente").val(msg[0]['cliente_id']);
			$("#cliente_seleccionado").val(msg[0]['cliente']);
			$("#id_vendedor").val(msg[0]['vendedor_id']);
			$("#vendedor_seleccionado").val(msg[0]['vendedor']);
			$("#plan_pago").val(msg[0]['plan_de_pago']);
			$("#id_plan_pago").val(msg[0]['plan_de_pago_id']);
			$("#plan_pago_vendedores").val(msg[0]['plan_de_pago_vendedor']);
			$("#id_plan_pago_vendedores").val(msg[0]['plan_de_pago_vendedor_id']);
			$("#precio_de_cuota").val(msg[0]['precio_de_cuota']);
			$("#monto_cuota").val(msg[0]['precio_de_cuota']);
			$("#monto_cuota2").html(String(msg[0]['precio_de_cuota']));
			$("#monto_cuota2").html(String(format.call($("#monto_cuota2").html().split(' ').join(''),'.',',')));
			$("#id_fecha_venta").val(msg[0]['fecha_de_venta']);
			//$("#id_fecha_venta2").val(msg[0]['fecha_de_venta']);
			
			var fechita = String(msg[0]['fecha_de_venta']);
			console.log(fechita);
			fechita = $.datepicker.parseDate('yy-mm-dd', fechita);
			$("#id_fecha_venta2").datepicker("setDate", fechita);
			$("#id_fecha_venta2").datepicker({ dateFormat: 'dd/mm/yy' });
			$("#id_fecha_venta2").datepicker('disable');
			
			$("#resumen_cuotas").empty();
			$("#resumen_cuotas").append(msgaux.cuotas_details.cant_cuotas_pagadas + '/' + msgaux.cuotas_details.cantidad_total_cuotas);
			
			$("#proximo_vencimiento").empty();
			$("#proximo_vencimiento").append(msgaux.cuotas_details.proximo_vencimiento);
						
			retrieveCliente();
			retrieveVendedor();
			retrievePlanPago();
			
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
			//alert("Response: " + msg);
			$("#cliente_error").html("");
			$("#cliente_seleccionado").html(msg);

		});
		// En caso de no poder obtener los datos del cliente, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			//alert("Request failed: " + jqXHR);
			$("#cliente_error").html("No se pueden obtener los datos del Cliente.");
			$("#cliente_seleccionado").html("");
			//$("#id_cliente").select().focus();
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
			//alert("Response: " + msg);
			$("#vendedor_error").html("");
			$("#vendedor_seleccionado").html(msg);

		});
		// En caso de no poder obtener los datos del vendedor, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			//alert("Request failed: " + jqXHR);
			$("#vendedor_error").html("No se pueden obtener los datos del Vendedor.");
			$("#vendedor_seleccionado").html("");
			//$("#id_vendedor").select().focus();
		});
	}
}

function retrievePlanPagoVendedor() {
	if ($("#id_plan_pago_vendedores").val().toString().length > 0) {
		// Hacemos un request POST AJAX para obtener los datos del plan de pagos ingresado.
		var request = $.ajax({
			type : "GET",
			url : "/datos/4/",
			data : {
				plan_pago_vendedor : $("#id_plan_pago_vendedores").val(),
			}
		});
		// Actualizamos el formulario con los datos obtenidos del plan de pagos.
		request.done(function(msg) {
			//alert("Response: " + msg);
			$("#plan_pago_vendedor_error").html("");
			$("#plan_pago_vendedor_seleccionado").html(msg.nombre_del_plan);

		});
		// En caso de no poder obtener los datos del plan de pagos, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			$("#plan_pago_vendedor_error").html("No se pueden obtener los datos del Plan de Pago.");
			$("#plan_pago_vendedor_seleccionado").html("");
			//$("#id_plan_pago").select().focus();
		});
	}
}

function retrievePlanes(){
	// retrievePlanPago();
	retrieveLotePago();
	retrievePlanPagoVendedor(); 
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
			//alert("Response: " + msg);
			$("#plan_pago_error").html("");
			$("#plan_pago_seleccionado").html(msg.nombre_del_plan);

		});
		// En caso de no poder obtener los datos del plan de pagos, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			$("#plan_pago_error").html("No se pueden obtener los datos del Plan de Pago.");
			$("#plan_pago_seleccionado").html("");
			//$("#id_plan_pago").select().focus();
		});
	}
}

function calculateTotalCuotas() {
	var monto_cuota = ($('#monto_cuota').val());
	var nro_cuotas_a_pagar = ($('#nro_cuotas_a_pagar').val());
	nro_cuotas_a_pagar = parseInt(nro_cuotas_a_pagar);
	var total_cuotas = (monto_cuota * nro_cuotas_a_pagar);
	$("#total_cuotas").val(total_cuotas);
	$("#total_cuotas2").html(String(total_cuotas));
	$("#total_cuotas2").html(String(format.call($("#total_cuotas2").html().split(' ').join(''),'.',',')));
	$("#total_mora").removeAttr("disabled");
	//$("#total_mora").focus();
	$("#total_mora").val("0");
	//$("#total_mora2").html("5000");
	//$("#total_mora2").html(String(format.call($("#total_mora2").html().split(' ').join(''),'.',',')));
}

function calculateTotalPago() {
	var total_cuotas = $("#total_cuotas").val();
	total_cuotas = parseInt(total_cuotas);
	var total_mora = $("#total_mora").val();
	total_mora = parseInt(total_mora);
	var total_pago = (total_cuotas + total_mora);
	total_pago = parseInt(total_pago);
	$("#total_pago").val(total_pago);
	$("#total_pago2").html(String(total_pago));
	$("#total_pago2").html(String(format.call($("#total_pago2").html().split(' ').join(''),'.',',')));
	$("#guardar_pago").removeAttr("disabled");
	//$("#guardar_pago").focus();
}
