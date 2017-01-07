var valido=false;

$(document).ready(function() {
	$('.grid_6').hide();

});	


function retrieveCedula() {
	if ($("#id_cedula").val().toString().length > 0) {
		var request_cliente = $.ajax({
			url : base_context + '/datos/16',
			type : "GET",
			data : {
				cedula : $("#id_cedula").val()
			},
			dataType : "json",
			error: function(data) {				
				$("#cedula_error").html("Ya existe un cliente con esta cedula");				
			}
			
		});
	}
}	

function asignarRUC() {
	var cedula=$("#id_cedula").val();	
	$("#id_ruc").val(cedula);

}

function asignarDireccion() {
	var direccion_cobro=$("#id_direccion_particular").val();	
	$("#id_direccion_cobro").val(direccion_cobro);	
}


