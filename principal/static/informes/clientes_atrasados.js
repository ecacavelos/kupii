function retrieve_clientes_atrasados() {
	var filter_get_parameters = "?";
	filter_get_parameters += "meses_atraso=" + $('#meses_atraso').val();
	filter_get_parameters += "&" + "fraccion=" + $('#id_fraccion').val();
	window.location.href = base_context + "/informes/clientes_atrasados_reporte_excel" + filter_get_parameters;
}

function validar() {
	var filter_get_parameters = "?";
	filter_get_parameters += "meses_atraso=" + $('#meses_atraso').val();
	filter_get_parameters += "&" + "fraccion=" + $('#fraccion').val();
	window.location.href = base_context + "/informes/clientes_atrasados_reporte_excel" + filter_get_parameters;
	$("#frm_busqueda").submit();
}

function setup_inputs() {
	$("#id_tipo_busqueda").change(function() {
		autocompleteFraccion();		
	});
	$("#fraccion").change(function() {
		autocompleteFraccion();		
	});
	autocompleteFraccion();	
}
function autocompleteFraccion(){
	//$("#fraccion").empty();
	//$("#fraccion").val("");
	if ($("#id_tipo_busqueda").val() == "nombre") {
		var id_fraccion;
		$("#fraccion").empty();
		base_url = "/ajax/get_fracciones_by_name/";
		params = "value";
		$("#fraccion").autocomplete({
			source : base_url,
			minLength : 1,
			select : function(event, ui) {
				id_fraccion = ui.item.id;
				$("#id_fraccion").val(id_fraccion);
			}
		});
	}else{
		$("#id_busqueda_label").empty();
		base_url = "/ajax/get_fracciones_by_id/";
		params = "value";
		$("#fraccion").autocomplete({
			source : base_url,
			minLength : 1,
			select : function(event, ui) {
				id_fraccion = ui.item.id;
				$("#id_fraccion").val(id_fraccion);
			}
		});
	}
}

