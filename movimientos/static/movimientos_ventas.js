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
var entrega_inicial = 0;
var monto_cuota = 0;

function validateVenta(event) {

	event.preventDefault();
	if (monto_final_validado == true) {
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
				venta_entrega_inicial : $("#id_entrega_inicial").val(),
				venta_precio_de_cuota : $("#id_monto_cuota").val(),
				venta_precio_final_de_venta : $("#id_precio_venta").val(),
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
		alert("Por favor intr");
	}

};

function calculatePrecioFinalVentaLote() {

	var request = $.ajax({
		type : "GET",
		url : "/movimientos/ventas_lotes/calcular_cuotas/",
		data : {
			calcular_cuotas : true,
			plan_pago_establecido : $("#id_plan_pago").val(),
			precio_de_venta : $("#id_precio_venta").val(),
			entrega_inicial : $("#id_entrega_inicial").val(),
			monto_cuota : $("#id_monto_cuota").val(),
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

function calculateMontoCuotas() {
	
	var entrega_inicial = ($('#id_entrega_inicial').val());
	entrega_inicial = parseInt(entrega_inicial);
	var monto_cuota = (precio_credito - entrega_inicial) / cantidad_cuotas;
	$("#id_monto_cuota").val(monto_cuota);
};
