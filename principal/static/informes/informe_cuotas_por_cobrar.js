function retrieve_informe_cuotas_por_cobrar() {
	validar();
	$("#formato-reporte").val("excel");
	// if($('#id_tipo_busqueda').val()=='nombre'){
	// 	window.location.href = base_context + "/informes/informe_cuotas_por_cobrar?fraccion_ini=" + $('#id_frac1').val();
	// }
	//
	// if($('#id_tipo_busqueda').val()=='codigo'){
	// 	window.location.href = base_context + "/informes/informe_cuotas_por_cobrar?fraccion_ini=" +$('#id_frac1').val();
	// }
	$("#frm_busqueda").submit();
}

function validar() {
	if ($('#fraccion_ini').val() == 0 || $('#fraccion_ini').val() == "") {
		alert("Debe ingresar un rango de fracciones");
		return;
	}
	$("#frm_busqueda").submit();

}
	
function setup_inputs() {
	$("#id_tipo_busqueda").change(function() {
		$("#id_fraccion_ini").empty();
		$("#id_fraccion_ini").val("");
		$("#id_fraccion_fin").empty();
		$("#id_fraccion_fin").val("");
		autocompleteFraccion();	
	});
	autocompleteFraccion();	
}
function autocompleteFraccion(){
	$("#id_fraccion_ini").autocomplete();
	$("#id_fraccion_fin").autocomplete();

	if ($("#id_tipo_busqueda").val() == "nombre") {
		var id_fraccion;
		$("#id_busqueda_label").empty();
		base_url = base_context + "/ajax/get_fracciones_by_name/";
		params = "value";
		$("#id_fraccion_ini").autocomplete("destroy");
		$("#id_fraccion_ini").autocomplete({
			source : base_url,
			minLength : 1,
            select : function(event, ui) {
            	event.preventDefault();
				id_fraccion = ui.item.id;
				$("#id_frac1").val(id_fraccion);
				$("#id_fraccion_ini").val(ui.item.nombre);
			}
		});

		$("#id_busqueda_label").empty();
		base_url = base_context + "/ajax/get_fracciones_by_name/";
		params = "value";
		$("#id_fraccion_fin").autocomplete("destroy");
		$("#id_fraccion_fin").autocomplete({
			source : base_url,
			minLength : 1,
			select : function(event, ui) {
				event.preventDefault();
				id_fraccion = ui.item.id;
				$("#id_frac2").val(id_fraccion);
				$("#id_fraccion_fin").val(ui.item.nombre);
			}
		});
	}else if($("#id_tipo_busqueda").val() == "codigo"){
		var id_fraccion;
		$("#id_busqueda_label").empty();
		base_url = base_context + "/ajax/get_fracciones_by_id/";
		params = "value";
		$("#id_fraccion_ini").autocomplete("destroy");
		$("#id_fraccion_ini").autocomplete({
			source : base_url,
			minLength : 1,
            select : function(event, ui) {
            	event.preventDefault();
				id_fraccion = ui.item.id;
				$("#id_frac1").val(id_fraccion);
				$("#id_fraccion_ini").val(ui.item.id);
			}
		});
		$("#id_busqueda_label").empty();
		base_url = base_context + "/ajax/get_fracciones_by_id/";
		params = "value";
		$("#id_fraccion_fin").autocomplete("destroy");
		$("#id_fraccion_fin").autocomplete({
			source : base_url,
			minLength : 1,
            select : function(event, ui) {
            	event.preventDefault();
				id_fraccion = ui.item.id;
				$("#id_frac2").val(id_fraccion);
				$("#id_fraccion_fin").val(ui.item.id);
			}
		});
	}
}