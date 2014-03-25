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
				venta_entrega_inicial : res_entrega,
				venta_precio_de_cuota : res_cuota,
				venta_precio_final_de_venta : res_venta,
				venta_fecha_primer_vencimiento : $("#id_fecha_vencimiento").val(),
				venta_pagos_realizados : 0
			}
		});
		request2.done(function(msg) {
			alert("Se procesó la venta satisfactoriamente.");
			top.location.href = "/listado_ventas/";
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
		datatype: "json,",
		data : {
			calcular_cuotas : true,
			plan_pago_establecido : $("#id_plan_pago").val(),
			precio_de_venta : res_venta,
			entrega_inicial : res_entrega,
			monto_cuota : res_cuota ,
		}
	});
	request.complete(function(msg) {
		$("#precio_final_venta").html(msg.responseJSON.monto_total);
		$("#precio_final_venta").html(format.call($('#precio_final_venta').html().split(' ').join(''),'.',','));
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

function calculateMontoCuotas() {
	var res_entrega = $("#id_entrega_inicial").val();
	var res_cuota = $("#id_monto_cuota").val();
	for ( i = 0; i < res_entrega.length; i++) {
			res_entrega = res_entrega.replace(".", "");
	}
	for ( i = 0; i < res_cuota.length; i++) {
			res_cuota = res_cuota.replace(".", "");
		}
	var entrega_inicial = res_entrega;
	entrega_inicial = parseInt(entrega_inicial);
	console.log("precio_credito: "+precio_credito);
	console.log("entrega_inicial: "+entrega_inicial);
	console.log("cantidad_credito: "+cantidad_cuotas);
	var monto_cuota = Math.ceil((precio_credito - entrega_inicial) / cantidad_cuotas);
	//monto_cuota = Math.round(monto_cuota);
	console.log("monto_cuota: "+monto_cuota);
	$("#id_monto_cuota").val(monto_cuota);
	$("#id_monto_cuota").val(format.call($('#id_monto_cuota').val().split(' ').join(''),'.',','));
};
