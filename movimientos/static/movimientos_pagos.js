$(document).ready(function() {
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
};

function validateLotePost(event) {
	if ((event.which >= 48 && event.which <= 57) || (event.which >= 96 && event.which <= 105)) {
		if ($("#id_lote").val().toString().length == 3 || $("#id_lote").val().toString().length == 7) {
			$("#id_lote").val($("#id_lote").val() + '/');
		}
	}
};

function validatePago(event) {

	event.preventDefault();
	var request3 = $.ajax({
		type : "POST",
		url : "/movimientos/pago_cuotas/",
		data : {
			ingresar_pago : true,
			pago_lote_id : global_lote_id,
			pago_fecha_de_pago : $("#id_fecha").val(),
			pago_nro_cuotas_a_pagar : $("#nro_cuotas_a_pagar").val(),
			pago_cliente_id : $("#id_cliente").val(),
			pago_plan_de_pago_id : $("#id_plan_pago").val(),
			pago_vendedor_id : $("#id_vendedor").val(),
			pago_total_de_cuotas : $("#total_cuotas").val(),
			pago_total_de_mora : $("#total_mora").val(),
			pago_total_de_pago : $("#total_pago").val(),
		}
	});
	request3.done(function(msg) {
		alert("Se procesó el pago exitosamente.");
		top.location.href = "/";
	});
	request3.fail(function(jqXHR, textStatus) {
		alert("Se encontró un error en el pago, favor verifique los datos");
	});
	return false;
};

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
			var s = "<a href=\"/lotes/listado/" + msg.lote_id + "\" target=\"_blank\" \">" + msg.lote_tag + "</a>";

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
			//$("#id_cliente").removeAttr("disabled");
			//$("#id_vendedor").removeAttr("disabled");
			//$("#id_plan_pago").removeAttr("disabled");
			//$("#id_monto").removeAttr("disabled");
			$("#nro_cuotas_a_pagar").focus();
		});
		// En caso de no poder obtener los datos del lote, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			//alert("Request failed: " + jqXHR);
			$("#lote_error").html("No se pueden obtener los datos de Lote.");
		});
	} else {
		if ($("#id_lote").val().toString().length > 0) {
			$("#lote_error").html("No se encuentra el Lote indicado.");
		}
	}
};

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
			$("#id_cliente").val(msg[0]['cliente_id']);
			$("#cliente_seleccionado").val(msg[0]['cliente']);
			$("#id_vendedor").val(msg[0]['vendedor_id']);
			$("#vendedor_seleccionado").val(msg[0]['vendedor']);
			$("#plan_pago").val(msg[0]['plan_de_pago']);
			$("#id_plan_pago").val(msg[0]['plan_de_pago_id']);
			$("#precio_de_cuota").val(msg[0]['precio_de_cuota']);
			$("#monto_cuota").val(msg[0]['precio_de_cuota']);
		});
//	}
};

function calculateTotalCuotas() {
	var monto_cuota = ($('#monto_cuota').val());
	var nro_cuotas_a_pagar = ($('#nro_cuotas_a_pagar').val());
	nro_cuotas_a_pagar = parseInt(nro_cuotas_a_pagar);
	var total_cuotas = (monto_cuota * nro_cuotas_a_pagar);
	$("#total_cuotas").val(total_cuotas);
	$("#total_mora").removeAttr("disabled");
	$("#total_mora").focus();
};

function calculateTotalPago() {
	var total_cuotas = $("#total_cuotas").val();
	total_cuotas = parseInt(total_cuotas);
	var total_mora = $("#total_mora").val();
	total_mora = parseInt(total_mora);
	var total_pago = (total_cuotas + total_mora);
	total_pago = parseInt(total_pago);
	$("#total_pago").val(total_pago);
	$("#guardar_pago").removeAttr("disabled");
	$("#guardar_pago").focus();
};
