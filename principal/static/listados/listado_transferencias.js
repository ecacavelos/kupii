$(document).ready(function() {
	$("#id_lote").keydown(validateLotePre);
	$("#id_lote").keyup(validateLotePost);
	$("#id_lote").focus();
});

window.onload = function() {
};

// Funciones individuales
var global_lote_id = 0;
var splitted_id = "";
var lote_id = 0;

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

function validateLotePost(event) {
	if ((event.which >= 48 && event.which <= 57) || (event.which >= 96 && event.which <= 105)) {
		if ($("#id_lote").val().toString().length == 3 || $("#id_lote").val().toString().length == 7) {
			$("#id_lote").val($("#id_lote").val() + '/');
		}
	}
}

function validateTransferencia() {

	var request5 = $.ajax({
		type : "POST",
		url : "/movimientos/transferencias_lotes/",
		data : {
			ingresar_transferencia : true,
			transferencia_lote_id : global_lote_id,
			transferencia_fecha_de_transferencia : $("#id_fecha").val(),
			transferencia_cliente_original_id : $("#id_cliente_original").val(),
			transferencia_cliente_id : $("#id_cliente").val(),
			transferencia_cliente_cedula : $("#id_cedula_cliente").val(),
			transferencia_plan_de_pago_id : $("#id_plan_pago").val(),
			transferencia_vendedor_id : $("#id_vendedor").val(),
		}
	});
	request5.done(function(msg) {
		top.location.href = "/movimientos/listado_transferencias";
	});
	request5.fail(function(jqXHR, textStatus) {
		alert("Se encontró un error en la transferencia, favor verifique los datos");
		$('#enviar_transferencia').removeAttr('disabled');
		return false;
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
			url : "/datos/11/",
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
			$("#id_fecha").datepicker({ dateFormat: 'dd/mm/yy' });
			$("#id_cliente").removeAttr("disabled");
			$("#id_cliente").focus();
		});
		// En caso de no poder obtener los datos del lote, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			$("#lote_error").html("El Lote no existe o no fue vendido.");
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
			$("#id_cliente_original").val(msg.venta[0]['cliente_id']);
			$("#cliente_original_seleccionado").html(msg.venta[0]['cliente']);
			$("#id_vendedor").val(msg.venta[0]['vendedor_id']);
			$("#vendedor_seleccionado").html(msg.venta[0]['vendedor']);
			$("#plan_pago_seleccionado").html(msg.venta[0]['plan_de_pago']);
			$("#id_plan_pago").val(msg.venta[0]['plan_de_pago_id']);
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

			$("#guardar_transferencia").removeAttr("disabled");
			$("#guardar_transferencia").focus();
		});
		// En caso de no poder obtener los datos del cliente, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			$("#cliente_error").html("No se pueden obtener los datos del Cliente.");
			$("#cliente_seleccionado").html("");
			$("#id_cliente").select().focus();
		});
	}
}
