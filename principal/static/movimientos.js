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

var splitted_id = "";
var precio_contado = 0;
var precio_credito = 0;
var cantidad_cuotas = 0;

function retrieveLote() {
	if ($("#id_lote").val().toString().length == 12) {
		// Extraemos los identificadores correspondientes a la fraccion, manzana y lote.
		splitted_id = $("#id_lote").val().split('/');
		// Hacemos un request POST AJAX para obtener los datos del lote ingresado.
		var request = $.ajax({
			type : "GET",			
			url : base_context + "/datos/1/",
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
			precio_contado = msg.precio_contado;
			precio_credito = msg.precio_credito;
			var d = new Date();
			var month = d.getMonth() + 1;
			var day = d.getDate();
			$("#id_nombre_cliente").removeAttr("disabled");
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
};

function retrieveCliente() {
	if ($("#id_cliente").val().toString().length > 0) {
		// Hacemos un request POST AJAX para obtener los datos del cliente ingresado.
		var request = $.ajax({
			type : "GET",
			url : base_context + "/datos/2/",
			data : {
				cliente : $("#id_cliente").val()
			}
		});
		// Actualizamos el formulario con los datos obtenidos del cliente.
		request.done(function(msg) {
			$("#cliente_error").html("");
			$("#cliente_seleccionado").html(msg);

			$("#id_nombre_vendedor").removeAttr("disabled");
			$("#id_nombre_vendedor").focus();
			$("#enviar_reserva").removeAttr("disabled");
		});
						
		// En caso de no poder obtener los datos del cliente, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			$("#cliente_error").html("No se pueden obtener los datos del Cliente.");
			$("#cliente_seleccionado").html("");
		});
	}
};

function retrieveVendedor() {
	if ($("#id_vendedor").val().toString().length > 0) {
		// Hacemos un request POST AJAX para obtener los datos del vendedor ingresado.
		var request = $.ajax({
			type : "GET",
			url : base_context + "/datos/3/",
			data : {
				vendedor : $("#id_vendedor").val()
			}
		});
		// Actualizamos el formulario con los datos obtenidos del vendedor.
		request.done(function(msg) {
			$("#vendedor_error").html("");
			$("#vendedor_seleccionado").html(msg);

			$("#id_plan_pago").removeAttr("disabled");
		});
		// En caso de no poder obtener los datos del vendedor, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			$("#vendedor_error").html("No se pueden obtener los datos del Vendedor.");
			$("#vendedor_seleccionado").html("");
		});
	}
};

function retrieveFraccion() {
	if ($("#id_lote").val().toString().length == 12) {
		// Extraemos los identificadores correspondientes a la fraccion, manzana y lote.
		splitted_id = $("#id_lote").val().split('/');
		// Hacemos un request POST AJAX para obtener los datos del lote ingresado.
		var request = $.ajax({
			type : "GET",
			url : base_context + "/datos/15/",
			data : {
				fraccion : splitted_id[0],
				manzana : splitted_id[1],
				lote : splitted_id[2]
			},
			dataType : "json",
			async: false
		});
		request.success(function(msg) {
			$("#lote_seleccionado_fraccion").html(msg.nombre);
		});
		request.error(function(msg) {
			window.location.href = base_context + "/login/";
		});	
	}
}

function retrievePlanPago() {
	if ($("#id_plan_pago").val().toString().length > 0) {
		// Hacemos un request POST AJAX para obtener los datos del plan de pagos ingresado.
		var request = $.ajax({
			type : "GET",
			url : base_context + "/datos/5/",
			data : {
				plan_pago : $("#id_plan_pago").val()
			}
		});
		// Actualizamos el formulario con los datos obtenidos del plan de pagos.
		request.done(function(msg) {
			$("#plan_pago_error").html("");
			$("#plan_pago_seleccionado").html(msg.nombre_del_plan);

			// El plan es a credito.
			if (msg.credito == "credito") {
				$("#id_precio_venta").removeAttr("disabled").val(precio_credito);
				$('#id_precio_venta').val(format.call($('#id_precio_venta').val().split(' ').join(''),'.',','));

				$("#tipo_pago_contado").removeAttr("checked").attr("disabled", "disabled");
				$("#tipo_pago_credito").prop("checked", true).removeAttr("disabled");
				
				$("#enviar_venta").show();
				$("#enviar_venta_factura").hide();

				$("#cantidad_cuotas_venta").html(msg.cantidad_cuotas + " cuotas.");

				$("#id_entrega_inicial").val(0).removeAttr("disabled");
				$("#id_monto_cuota").val(0).removeAttr("disabled");
				$("#id_entrega_inicial").select().focus();
				cantidad_cuotas = msg.cantidad_cuotas;
				// El plan es al contado.
			} else {
				$("#id_precio_venta").removeAttr("disabled").val(precio_contado);
				$('#id_precio_venta').val(format.call($('#id_precio_venta').val().split(' ').join(''),'.',','));

				$("#tipo_pago_credito").removeAttr("checked").attr("disabled", "disabled");
				$("#tipo_pago_contado").prop("checked", true).removeAttr("disabled");
				
				$("#enviar_venta").hide();
				$("#enviar_venta_factura").show();
				
				//$("#id_monto_cuota_refuerzo").prop("readonly", true);
				$("#id_monto_cuota_refuerzo").val(0).attr("disabled", "disabled");

				$("#cantidad_cuotas_venta").html("");
				$("#precio_final_venta").html(precio_contado);
				$("#id_entrega_inicial").val(0).attr("disabled", "disabled");
				$("#id_monto_cuota").val(0).attr("disabled", "disabled");
				calculatePrecioFinalVentaLote();
			}
			
			$("#id_fecha_vencimiento").datepicker({ dateFormat: 'dd/mm/yy' });
			
			$("#id_fecha_vencimiento").datepicker("setDate", $('#id_fecha').val()).removeAttr("disabled");
			$("#id_fecha_vencimiento").mask('##/##/####');
			$("#id_plan_pv").focus();
		});
		// En caso de no poder obtener los datos del plan de pagos, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			$("#plan_pago_error").html("No se pueden obtener los datos del Plan de Pago.");
			$("#plan_pago_seleccionado").html("");
		});
	}
};

function retrievePlanPagoVendedor() {
	if ($("#id_plan_pago_vendedores").val().toString().length > 0) {
		// Hacemos un request POST AJAX para obtener los datos del plan de pagos ingresado.
		var request = $.ajax({
			type : "GET",
			url : base_context + "/datos/4/",
			data : {
				plan_pago : $("#id_plan_pago_vendedores").val()
			}
		});
		// Actualizamos el formulario con los datos obtenidos del plan de pagos.
		request.done(function(msg) {
			//alert("Response: " + msg);
			$("#plan_pago_error_vendedor").html("");
			$("#plan_pago_vendedor_seleccionado").html(msg.nombre_del_plan);

			// El plan es a credito.
			if (msg.credito == "credito") {
				$("#id_precio_venta").removeAttr("disabled").val(precio_credito);
				$('#id_precio_venta').val(format.call($('#id_precio_venta').val().split(' ').join(''),'.',','));
				//$("#id_precio_venta").select().focus();

				$("#tipo_pago_contado").removeAttr("checked").attr("disabled", "disabled");
				$("#tipo_pago_credito").prop("checked", true).removeAttr("disabled");

				$("#cantidad_cuotas_venta").html(msg.cantidad_cuotas + " cuotas.");

				$("#id_entrega_inicial").val(0).removeAttr("disabled");
				$("#id_monto_cuota").val(0).removeAttr("disabled");
				$("#id_entrega_inicial").select().focus();
				cantidad_cuotas = msg.cantidad_cuotas;
				// El plan es al contado.
			} else {
				$("#id_precio_venta").removeAttr("disabled").val(precio_contado);
				$('#id_precio_venta').val(format.call($('#id_precio_venta').val().split(' ').join(''),'.',','));
				//$("#id_precio_venta").select().focus();

				$("#tipo_pago_credito").removeAttr("checked").attr("disabled", "disabled");
				$("#tipo_pago_contado").prop("checked", true).removeAttr("disabled");

				$("#cantidad_cuotas_venta").html("");
				//alert(precio_contado);
				$("#precio_final_venta").html(precio_contado);
				$("#id_entrega_inicial").val(0).attr("disabled", "disabled");
				$("#id_monto_cuota").val(0).attr("disabled", "disabled");
				//alert("hola");
				calculatePrecioFinalVentaLote();
			}
			//fecha_actual = new Date().toJSON().substring(0, 10);
			$("#id_fecha_vencimiento").datepicker({ dateFormat: 'dd/mm/yy' });
			$("#id_fecha_vencimiento").datepicker("setDate", new Date()).removeAttr("disabled");
			//$("#precio_final_venta").html("");
		});
		// En caso de no poder obtener los datos del plan de pagos, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			$("#plan_pago_error").html("No se pueden obtener los datos del Plan de Pago.");
			$("#plan_pago_seleccionado").html("");
			//$("#id_plan_pago").select().focus();
		});
	}
};
