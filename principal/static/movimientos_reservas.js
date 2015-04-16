$(document).ready(function() {
	$("#id_lote").keydown(validateLotePre);
	$("#id_lote").keyup(validateLotePost);

	$("#main_reserva_form").submit(validateReserva);


//autocomplete para cliente
	var cliente_id;
	$("#id_nombre_cliente").empty();
	base_url = base_context + "/ajax/get_cliente_id_by_name/";
	params = "value";
	$("#id_nombre_cliente").autocomplete({
		source : base_url,
		minLength : 1,
		select : function(event, ui) {
			id_cliente = ui.item.pk;
			cedula_cliente= ui.item.fields.cedula;
            name_cliente=ui.item.fields.label;
			$("#id_cliente").val(id_cliente);
            $("#id_nombre_cliente").val(name_cliente);
			$("#id_cedula_cliente").val(cedula_cliente);
		}
	});
		
	//autocomplete para cedula
	var cliente_id;
	$("#id_cedula_cliente").empty();
	base_url = "/ajax/get_cliente_name_id_by_cedula/";
	params = "value";
	$("#id_cedula_cliente").autocomplete({
		source : base_url,
		minLength : 1,
		select : function(event, ui) {
			id_cliente = ui.item.pk;
			name_cliente= ui.item.fields.label;
			cedula_cliente= ui.item.fields.cedula;
			ui.item.value = ui.item.fields.cedula;
			$("#id_cliente").val(id_cliente);
			$("#id_nombre_cliente").val(name_cliente);
			$("#id_cedula_cliente").val(cedula_cliente);
				
		}
	});
    });
window.onload = function() {
};

// Funciones individuales
var global_lote_id = 0;

function validateReserva(event) {

	event.preventDefault();
	var request3 = $.ajax({
		type : "POST",
		url : "/movimientos/reservas_lotes/",
		data : {
			ingresar_reserva : true,
			reserva_lote_id : global_lote_id,
			reserva_fecha_de_reserva : $("#id_fecha").val(),
			reserva_cliente_id : $("#id_cliente").val()
		}
	});
	request3.done(function(msg) {
		top.location.href = "/movimientos/listado_reservas";
	});
	request3.fail(function(jqXHR, textStatus) {
		alert("Se encontró un error en la reserva, favor verifique los datos");
	});
	return false;
};

function retrieveLoteReservas() {
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
			$("#lote_error").html("El Lote no existe o ya ha sido reservado.");
		});
	} else {
		if ($("#id_lote").val().toString().length > 0) {
			$("#lote_error").html("No se encuentra el Lote indicado.");
		}
	}
};
