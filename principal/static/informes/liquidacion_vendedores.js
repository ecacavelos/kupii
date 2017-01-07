function retrieve_liquidacion_vendedores() {
	window.location.href = base_context + "/informes/liquidacion_vendedores_reporte_excel?fecha_ini=" + $('#fecha_ini').val() + "&fecha_fin=" + $('#fecha_fin').val() + "&busqueda=" + $('#id_busqueda').val()+"&busqueda_label="+$('#id_busqueda_label').val();
}

function retrieve_liquidacion_general_vendedores() {
	window.location.href = base_context + "/informes/liquidacion_general_vendedores_reporte_excel?fecha_ini=" + $('#fecha_ini').val() + "&fecha_fin=" + $('#fecha_fin').val();
}

function validar() {
	if ($('#fecha_ini').val() == "" || $('#fecha_fin').val() == "") {
		alert("Debe ingresar un rango de fechas");
		return;
	}
	$("#frm_busqueda").submit();
}

function sacarPuntos(numero){
	
	numero =numero.replace(".", "");
	numero =numero.replace(".", "");
	numero =numero.replace(".", "");
	numero =numero.replace(".", "");
	numero =numero.replace(".", "");
	
	return (numero);
}

function ponerPuntos(negativo, resta){
	$("#ley").mask('###.###.###',{reverse: true});
	$("#impuesto_renta").mask('###.###.###',{reverse: true});
	$("#monto_otros_descuentos").mask('###.###.###',{reverse: true});
	$("#iva_comision").mask('###.###.###',{reverse: true});
	valor = Math.abs(resta);
	$("#total_a_cobrar").html("");
	$("#total_a_cobrar").unmask();
	$("#total_a_cobrar").html(valor);
	$("#total_a_cobrar").mask('###.###.###',{reverse: true});
	
	if (negativo){
		total = "-"+$("#total_a_cobrar").html();
		$("#total_a_cobrar").unmask('###.###.###',{reverse: true});
		$("#total_a_cobrar").html(total);
	} else {
		total = $("#total_a_cobrar").html();
		$("#total_a_cobrar").unmask('###.###.###',{reverse: true});
		$("#total_a_cobrar").html(total);
	}
	
}

function setup_inputs() {
	/*
	if ($("#id_busqueda").val() == "") {
		$("#fecha_ini").prop('disabled', true);
		$("#fecha_fin").prop('disabled', true);
		$("#id_busqueda_label").prop('disabled', true);
		$("#boton_buscar").prop('disabled', true);
		$("#id_boton").attr("disabled", "disabled");

	} else {	
		$("#fecha_ini").prop('disabled', false);
		$("#fecha_fin").prop('disabled', false);
		$("#id_busqueda_label").prop('disabled', false);
		$("#boton_buscar").prop('disabled', false);
		$("#id_boton").prop('disabled', false);
		$("#id_boton").removeAttr("disabled");
		*/
		
		var id_vendedor;
		$("#id_busqueda_label").empty();
		base_url = base_context + "/ajax/get_vendedor_id_by_name/";
		params = "value";
		$("#id_busqueda_label").autocomplete({
			source : base_url,
			minLength : 1,
			create : function(){
			$(this).data('ui-autocomplete')._renderItem = function(ul,item){
				return $('<li>').append('<a>'+item.cedula +" - "+item.nombres + " "+ item.apellidos+'</a>').appendTo(ul);
				};
			},
			select : function(event, ui) {
				event.preventDefault();
			id_vendedor = ui.item.id;
			$("#id_busqueda").val(id_vendedor);
			$("#id_busqueda_label").val(ui.item.nombres + " "+ ui.item.apellidos);
			//alert(id_vendedor);
			}
		});
	//}
	//}
}
