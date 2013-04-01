$(document).ready(function() {
	$("#id_lote").keydown(validateLotePre);
	$("#id_lote").keyup(validateLotePost);

	//$("#enviar_venta").click(validateVenta);

	$("#main_venta_form").submit(validateVenta);
});

window.onload = function() {
	//document.getElementById("id_lote").onblur = retrieveLote;
	//document.getElementById("id_cliente").onblur = retrieveCliente;
};

// Funciones individuales
var global_lote_id = 0;
var monto_final_validado = false;

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

function retrieveLote() {
	if ($("#id_lote").val().toString().length == 12) {
		// Extraemos los identificadores correspondientes a la fraccion, manzana y lote.
		var splitted_id = $("#id_lote").val().split('/');
		// Hacemos un request POST AJAX para obtener los datos del lote ingresado.
		var request = $.ajax({
			type : "POST",
			url : "/movimientos/ventas_lotes/",
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

			var d = new Date();
			var month = d.getMonth() + 1;
			var day = d.getDate();

			//fecha_actual = (day < 10 ? '0' : '') + day + '/' + (month < 10 ? '0' : '') + month + '/' + d.getFullYear();
			fecha_actual = new Date().toJSON().substring(0, 10);

			$("#id_fecha").val(fecha_actual);

			$("#id_cliente").removeAttr("disabled");
			$("#id_cliente").focus();
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

function retrieveCliente() {
	if ($("#id_cliente").val().toString().length > 0) {
		// Hacemos un request POST AJAX para obtener los datos del cliente ingresado.
		var request = $.ajax({
			type : "POST",
			url : "/movimientos/ventas_lotes/",
			data : {
				cliente : $("#id_cliente").val()
			}
		});
		// Actualizamos el formulario con los datos obtenidos del cliente.
		request.done(function(msg) {
			//alert("Response: " + msg);
			$("#cliente_error").html("");
			$("#cliente_seleccionado").html(msg);

			$("#id_vendedor").removeAttr("disabled");
			$("#id_vendedor").focus();
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

function retrieveVendedor() {
	if ($("#id_vendedor").val().toString().length > 0) {
		// Hacemos un request POST AJAX para obtener los datos del vendedor ingresado.
		var request = $.ajax({
			type : "POST",
			url : "/movimientos/ventas_lotes/",
			data : {
				vendedor : $("#id_vendedor").val()
			}
		});
		// Actualizamos el formulario con los datos obtenidos del vendedor.
		request.done(function(msg) {
			//alert("Response: " + msg);
			$("#vendedor_error").html("");
			$("#vendedor_seleccionado").html(msg);

			$("#id_plan_vendedor").removeAttr("disabled");
			$("#id_plan_vendedor").focus();
		});
		// En caso de no poder obtener los datos del vendedor, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			//alert("Request failed: " + jqXHR);
			$("#vendedor_error").html("No se pueden obtener los datos del Vendedor.");
			$("#vendedor_seleccionado").html("");
			$("#id_vendedor").select().focus();
		});
	}
};

function retrievePlanVendedor() {
	if ($("#id_plan_vendedor").val().toString().length > 0) {
		// Hacemos un request POST AJAX para obtener los datos del plan de vendedores ingresado.
		var request = $.ajax({
			type : "POST",
			url : "/movimientos/ventas_lotes/",
			data : {
				plan_vendedor : $("#id_plan_vendedor").val()
			}
		});
		// Actualizamos el formulario con los datos obtenidos del plan de vendedores.
		request.done(function(msg) {
			//alert("Response: " + msg);
			$("#plan_vendedor_error").html("");
			$("#plan_vendedor_seleccionado").html(msg);

			$("#id_plan_pago").removeAttr("disabled");
			$("#id_plan_pago").focus();
		});
		// En caso de no poder obtener los datos del plan de vendedores, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			$("#plan_vendedor_error").html("No se pueden obtener los datos del Plan de Vendedor.");
			$("#plan_vendedor_seleccionado").html("");
			$("#id_plan_vendedor").select().focus();
		});
	}
};

function retrievePlanPago() {
	if ($("#id_plan_pago").val().toString().length > 0) {
		// Hacemos un request POST AJAX para obtener los datos del plan de pagos ingresado.
		var request = $.ajax({
			type : "POST",
			url : "/movimientos/ventas_lotes/",
			data : {
				plan_pago : $("#id_plan_pago").val(),
				lote : global_lote_id
			}
		});
		// Actualizamos el formulario con los datos obtenidos del plan de pagos.
		request.done(function(msg) {
			//alert("Response: " + msg);
			$("#plan_pago_error").html("");
			$("#plan_pago_seleccionado").html(msg.nombre_del_plan);
			
			// El plan es a credito.
			if (msg.credito == true) {
				$("#tipo_pago_contado").removeAttr("checked").attr("disabled", "disabled");
				$("#tipo_pago_credito").prop("checked", true).removeAttr("disabled");

				$("#cantidad_cuotas_venta").html(msg.cantidad_cuotas + " cuotas.");

				$("#id_entrega_inicial").val(0).removeAttr("disabled");
				$("#id_monto_cuota").val(0).removeAttr("disabled");
				$("#id_cuota_refuerzo").val(0).removeAttr("disabled");
				$("#id_entrega_inicial").select().focus();
			// El plan es al contado.
			} else {
				$("#tipo_pago_credito").removeAttr("checked").attr("disabled", "disabled");
				$("#tipo_pago_contado").prop("checked", true).removeAttr("disabled");

				$("#cantidad_cuotas_venta").html("");

				$("#id_entrega_inicial").val(0).attr("disabled", "disabled");
				$("#id_monto_cuota").val(0).attr("disabled", "disabled");
				$("#id_cuota_refuerzo").val(0).attr("disabled", "disabled");
			}

			$("#id_fecha_vencimiento").val(fecha_actual).removeAttr("disabled");
			$("#precio_final_venta").html("");
			
			$("#id_precio_venta").removeAttr("disabled").val(msg.precio_del_lote);
			$("#id_precio_venta").select().focus();
		});
		// En caso de no poder obtener los datos del plan de pagos, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			$("#plan_pago_error").html("No se pueden obtener los datos del Plan de Pago.");
			$("#plan_pago_seleccionado").html("");
			$("#id_plan_pago").select().focus();
		});
	}
};

function calculatePrecioFinalVentaLote() {
	var request = $.ajax({
		type : "POST",
		url : "/movimientos/ventas_lotes/",
		data : {
			calcular_cuotas : true,
			plan_pago_establecido : $("#id_plan_pago").val(),
			//lote_establecido : global_lote_id,
			precio_de_venta : $("#id_precio_venta").val(),
			entrega_inicial : $("#id_entrega_inicial").val(),
			monto_cuota : $("#id_monto_cuota").val(),
			cuota_refuerzo : $("#id_cuota_refuerzo").val()
		}
	});
	request.done(function(msg) {
		$("#precio_final_venta").html(msg.monto_total);
		monto_final_validado = msg.monto_valido;
		if (msg.monto_valido == false) {
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

function validateVenta(event) {

	event.preventDefault();
	alert("testing");

	if (monto_final_validado == true) {
		var request2 = $.ajax({
			type : "POST",
			url : "/movimientos/ventas_lotes/",
			data : {
				ingresar_venta : true,
				venta_lote : global_lote_id,
				venta_fecha : $("#id_fecha").val(),
				venta_cliente : $("#id_cliente").val(),
				venta_vendedor : $("#id_vendedor").val(),
				venta_plan_vendedor : $("#id_plan_vendedor").val(),
				venta_plan_pago : $("#id_plan_pago").val(),
				venta_entrega_inicial : $("#id_entrega_inicial").val(),
				venta_precio_cuota : $("#id_monto_cuota").val(),
				venta_cuota_refuerzo : $("#id_cuota_refuerzo").val(),
				venta_precio_final_venta : $("#id_precio_venta").val(),
				venta_fecha_primer_vencimiento : $("#id_fecha_vencimiento").val(),
				venta_pagos_realizados : 0
			}
		});
		request2.done(function(msg) {
			alert("Se procesó la venta satisfactoriamente.");
			top.location.href = "/movimientos";
		});
		request2.fail(function(jqXHR, textStatus) {
			alert("Epic Fail.");
		});
	} else {
		alert("no");
	}

};
