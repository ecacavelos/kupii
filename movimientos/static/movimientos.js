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
			type : "GET",
			url : "/datos/4/",
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
			type : "GET",
			url : "/datos/5/",
			data : {
				plan_pago : $("#id_plan_pago").val(),
				//lote : global_lote_id
				plan_pago_fraccion : splitted_id[0],
				plan_pago_manzana : splitted_id[1],
				plan_pago_lote : splitted_id[2]
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
