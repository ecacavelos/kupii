$(document).ready(function() {
	$("#id_lote").keydown(validateLotePre);
	$("#id_lote").keyup(validateLotePost);
	
	//$("#enviar_reserva").click(validateReserva);

	$("#main_reserva_form").submit(validateReserva);
});

window.onload = function() {
	//document.getElementById("id_lote").onblur = retrieveLote;
	//document.getElementById("id_cliente").onblur = retrieveCliente;
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
			reserva_cliente_id : $("#id_cliente").val(),
		}
	});
	request3.done(function(msg) {
		alert("Se procesó la reserva satisfactoriamente.");
		top.location.href = "/";
	});
	request3.fail(function(jqXHR, textStatus) {
		alert("Se encontró un error en la reserva, favor verifique los datos");
	});
	return false;
};
