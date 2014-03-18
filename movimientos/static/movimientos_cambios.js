$(document).ready(function() {
	$("#id_lote").keydown(validateLotePre);
	$("#id_lote").keyup(validateLotePost);
	$("#id_lote2").keydown(validateLotePre);
	$("#id_lote2").keyup(validateLotePost);

	//$("#enviar_reserva").click(validateReserva);

	$("#main_cambios_form").submit(validateCambio);
});

window.onload = function() {
	//document.getElementById("id_lote").onblur = retrieveLote;
	//document.getElementById("id_cliente").onblur = retrieveCliente;
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
};

function validateLotePost(event) {
	if ((event.which >= 48 && event.which <= 57) || (event.which >= 96 && event.which <= 105)) {
		if ($("#id_lote").val().toString().length == 3 || $("#id_lote").val().toString().length == 7) {
			$("#id_lote").val($("#id_lote").val() + '/');
		}
		if ($("#id_lote2").val().toString().length == 3 || $("#id_lote2").val().toString().length == 7) {
			$("#id_lote2").val($("#id_lote2").val() + '/');
		}
	}
};

function validateCambio(event) {

	event.preventDefault();
	var request6 = $.ajax({
		type : "POST",
		url : "/movimientos/cambio_lotes/",
		data : {
			realizar_cambio : true,
			cambio_cliente_id : $("#id_cliente").val(),
			cambio_fecha_de_cambio : $("#id_fecha").val(),
			cambio_lote_id : global_lote_id,
			cambio_lote2_id : global_lote2_id,
			cambio_venta_id : a,
		}
	});
	request6.done(function(msg) {
		alert("Se procesó el cambio exitosamente.");
		top.location.href = "/";
	});
	request6.fail(function(jqXHR, textStatus) {
		alert("Se encontró un error en el cambio, favor verifique los datos");
	});
	return false;
};

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
			var cliente_id = parseInt($("#id_cliente").val());
			var d = new Date();
			var month = d.getMonth() + 1;
			var day = d.getDate();
			//fecha_actual = (day < 10 ? '0' : '') + day + '/' + (month < 10 ? '0' : '') + month + '/' + d.getFullYear();
			fecha_actual = new Date().toJSON().substring(0, 10);
			
			$("#id_fecha").val(fecha_actual);
			$("#id_lote").removeAttr("disabled");
		});
		// En caso de no poder obtener los datos del cliente, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			//alert("Request failed: " + jqXHR);
			$("#cliente_error").html("No se pueden obtener los datos del Cliente.");
			$("#cliente_seleccionado").html("");
			$("#id_cliente").select().focus();
		});
	}
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
			lote_precio = msg.precio_credito;
			retrieveVenta();
			$("#id_lote2").focus();
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
			var cliente_venta = parseInt(msg[0]['cliente_id']);
			var venta_id = msg[0]['venta_id'];
			//$("#id_cliente_original").val(msg[0]['cliente_id']);
			//$("#cliente_original_seleccionado").val(msg[0]['cliente']);
			//$("#id_vendedor").val(msg[0]['vendedor_id']);
			//$("#vendedor_seleccionado").val(msg[0]['vendedor']);
			//$("#plan_pago").val(msg[0]['plan_de_pago']);
			//$("#id_plan_pago").val(msg[0]['plan_de_pago_id']);
		});
		if (cliente_id == cliente_venta) {
			$("#id_lote2").removeAttr("disabled");
		}
		else {
			$("#lote_error").html("El lote no pertenece al cliente seleccionado.");
			$("#id_lote").focus();
		}
//	}
};

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
		});
//	}	
};

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
			var s = "<a href=\"/lotes/listado/" + msg.lote_id + "\" target=\"_blank\" \">" + msg.lote_tag + "</a>";

			$("#lote2_error").html("");
			$("#lote2_superficie").html(msg.superficie);
			$("#lote2_seleccionado_detalles").html(s);
			lote2_id = msg.lote_id;
			lote2_precio = msg.precio_credito;
			$("#cambiar_lotes").removeAttr("disabled");
			
		});
		// En caso de no poder obtener los datos del lote, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			//alert("Request failed: " + jqXHR);
			$("#lote2_error").html("El Lote no existe o fue vendido.");
		});
		cambiable();
	} else {
		if ($("#id_lote2").val().toString().length > 0) {
			$("#lote2_error").html("No se encuentra el Lote indicado.");
			$("#id_lote2").focus();
		}
	}
};

function cambiable() {
	if (lote_precio == lote2_precio) {
		alert("Ambos lotes tienen el mismo precio")
	}
	if (lote_precio > lote2_precio) {
		alert("El lote nuevo tiene un precio inferior al lote original")
	}
	if (lote_precio < lote2_precio) {
		alert ("El lote nuevo tiene un precio superior al lote original")
	}
}
