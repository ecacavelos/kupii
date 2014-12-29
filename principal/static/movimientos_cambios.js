$(document).ready(function() {
	$('.grid_6').hide();
	$("#id_lote").keydown(validateLotePre);
	$("#id_lote").keyup(validateLotePost);
	$("#id_lote2").keydown(validateLotePre);
	$("#id_lote2").keyup(validateLotePost);

	$("#main_cambios_form").submit(validateCambio);
	$('#id_fecha').mask('##/##/####');
	$("#id_fecha").datepicker({ dateFormat: 'dd/mm/yy' });
});

window.onload = function() {
};

// Funciones individuales
var global_lote_id = 0;
var splitted_id = "";
var cliente_id = 0;
var venta_id = 0;
var cliente_venta = 0;
var lote_precio = 0;
var lote2_precio = 0;

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
		if ($("#id_lote2").val().toString().length == 3 || $("#id_lote2").val().toString().length == 7) {
			$("#id_lote2").val($("#id_lote2").val() + '/');
		}
	}
}

function validateCambio(event) {

	event.preventDefault();
	var request6 = $.ajax({
		type : "POST",
		url : "/movimientos/cambio_lotes/",
		data : {
			realizar_cambio : true,
			cambio_cliente_id : $("#id_cliente").val(),
			cambio_fecha_de_cambio : $("#id_fecha").val(),
			cambio_lote_original_id : global_lote_id,
			cambio_lote2_id : global_lote2_id,
			cambio_venta_id : venta_id,
		}
	});
	request6.done(function(msg) {
		top.location.href = "/movimientos/listado_cambios";
	});
	request6.fail(function(jqXHR, textStatus) {
		alert("Se encontró un error en el cambio, favor verifique los datos");
	});
	return false;
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
			var cliente_id = parseInt($("#id_cliente").val());
			var d = new Date();
			var month = d.getMonth() + 1;
			var day = d.getDate();
			fecha_actual = new Date().toJSON().substring(0, 10);
			
			$("#id_lote").removeAttr("disabled");
		});
		// En caso de no poder obtener los datos del cliente, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			$("#cliente_error").html("No se pueden obtener los datos del Cliente.");
			$("#cliente_seleccionado").html("");
			$("#id_cliente").select().focus();
		});
	}
}

function retrieveLoteCambio() {
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
			sup = msg.superficie.replace(".",",");
			$("#lote_superficie").html(sup);
			$("#lote_superficie").html(String(format.call($("#lote_superficie").html().split(' ').join(''),'.',',')));
			$("#lote_seleccionado_detalles").html(s);
			$('#id_fecha').mask('##/##/####');
			$("#id_fecha").datepicker({ dateFormat: 'dd/mm/yy' });
			lote_id = msg.lote_id;
			lote_precio = msg.precio_credito;
			retrieveVenta();
			
		});
		// En caso de no poder obtener los datos del lote, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			$("#lote_error").html("El Lote no existe o fue vendido.");
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
			var cliente_venta = parseInt(msg.venta[0]['cliente_id']);
			var venta_id = msg.venta[0]['venta_id'];
			$("#id_cliente").val(msg.venta[0]['cliente_id']);
			retrieveCliente();
		});
		if (cliente_id == cliente_venta) {
			$("#id_lote2").removeAttr("disabled");
		}
		else {
			$("#lote_error").html("El lote no pertenece al cliente seleccionado.");
			$("#id_lote").focus();
		}
}

function retrievePagos() {
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
		});
}

function retrieveLote2() {
	if ($("#id_lote2").val().toString().length == 12) {
		// Extraemos los identificadores correspondientes a la fraccion, manzana y lote.
		splitted_id = $("#id_lote2").val().split('/');
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
			global_lote2_id = msg.lote_id;
			var s = "<a class='boton-verde' href=\"/lotes/listado/" + msg.lote_id + "\" target=\"_blank\" \">" + msg.lote_tag + "</a>";

			$("#lote2_error").html("");
			sup = msg.superficie.replace(".",",");
			$("#lote2_superficie").html(sup);
			$("#lote2_superficie").html(String(format.call($("#lote2_superficie").html().split(' ').join(''),'.',',')));
			$("#lote2_seleccionado_detalles").html(s);
			lote2_id = msg.lote_id;
			lote2_precio = msg.precio_credito;
			$("#cambiar_lotes").removeAttr("disabled");
			cambiable();
		});
		// En caso de no poder obtener los datos del lote, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			$("#lote2_error").html("El Lote no existe o fue vendido.");
			cambiable();
		});
		
	} else {
		if ($("#id_lote2").val().toString().length > 0) {
			$("#lote2_error").html("No se encuentra el Lote indicado.");
			$("#id_lote2").focus();
			cambiable();
		}
	}
}

function cambiable() {
	if (lote_precio == lote2_precio) {
		alert("Ambos lotes tienen el mismo precio");
	}
	if (lote_precio > lote2_precio) {
		alert("El lote nuevo tiene un precio inferior al lote original");
	}
	if (lote_precio < lote2_precio) {
		alert ("El lote nuevo tiene un precio superior al lote original");
	}
}
