function retrieve_proximos_vencimientos() {
	if ($('#fecha_ini').val() == "" || $('#fecha_fin').val() == "") {
		alert("Debe ingresar un rango de fechas");
		$('#reporte').val("busqueda");
		return;
	}else if($('#id_fraccion').val() == ""){
		alert("Debe ingresar la Fracción");
		return;
	}else {
        var filter_get_parameters = "?";
        filter_get_parameters += "fecha_inicio=" + $('#fecha_ini').val();
        filter_get_parameters += "&" + "fecha_fin=" + $('#fecha_fin').val();
        filter_get_parameters += "&" + "fraccion=" + $('#id_fraccion').val();
        window.location.href = base_context + "/informes/proximos_vencimientos_reporte_excel" + filter_get_parameters;
    }
}
function validar() {
	if ($('#fecha_ini').val() == "" || $('#fecha_fin').val() == "") {
		alert("Debe ingresar un rango de fechas");
		$('#reporte').val("busqueda");
		return;
	}else if($('#id_fraccion').val() == ""){
		alert("Debe ingresar la Fracción");
		return;
	}else {
		$('#reporte').val("busqueda");
        var filter_get_parameters = "?";
        filter_get_parameters += "&" + "fraccion=" + $('#fraccion').val();
        window.location.href = base_context + "/informes/proximos_vencimientos/";
        $("#frm_busqueda").submit();
    }
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
		base_url = base_context + "/ajax/get_fracciones_by_name/";
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
		base_url = base_context + "/ajax/get_fracciones_by_id/";
		params = "value";
		$("#fraccion").autocomplete({
			source : base_url,
			minLength : 1,
			select : function(event, ui) {
				event.preventDefault();
				id_fraccion = ui.item.id;
				$("#id_fraccion").val(id_fraccion);
				$("#fraccion").val(id_fraccion);
			}
		});
	}
}


