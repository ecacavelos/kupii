function validar() {
	if ($('#fraccion_ini').val() == 0 || $('#fraccion_fin').val() == 0 || $('#fraccion_ini').val() == "" || $('#fraccion_fin').val() == "") {
		alert("Debe ingresar un rango de fracciones");
		return;
	}
	$("#frm_busqueda").submit();
}

function retrieve_lotes_libres() {
	if($('#id_tipo_busqueda').val()=='nombre'){
		window.location.href = "/informes/lotes_libres_reporte_excel?fraccion_ini=" + $('#id_frac1').val() + "&fraccion_fin=" + $('#id_frac2').val();
	}
	if($('#id_tipo_busqueda').val()=='codigo'){
		window.location.href = "/informes/lotes_libres_reporte_excel?fraccion_ini=" + $('#id_fraccion_ini').val() + "&fraccion_fin=" + $('#id_fraccion_fin').val();
	}
	
}

function setup_inputs() {
	/*
	if ($("#id_tipo_busqueda").val() == ""){
			$("#id_fraccion_ini").prop('disabled', true);
			$("#id_fraccion_fin").prop('disabled', true);
			$("#boton_buscar").prop('disabled', true);
			$("#id_boton").prop('disabled', true);
	}
	else{
		$("#id_fraccion_ini").prop('disabled', false);
		$("#id_fraccion_fin").prop('disabled', false);
		$("#boton_buscar").prop('disabled', false);
		$("#id_boton").prop('disabled', false);
	}*/
	$("#id_tipo_busqueda").change(function() {
		$("#id_fraccion_ini").empty();
		$("#id_fraccion_ini").val("");
		$("#id_fraccion_fin").empty();
		$("#id_fraccion_fin").val("");
		if ($("#id_tipo_busqueda").val() == "nombre") {
			var id_fraccion;
			$("#id_busqueda_label").empty();
			base_url = "/ajax/get_fracciones_by_name/";
			params = "value";
			$("#id_fraccion_ini").autocomplete({
				source : base_url,
				minLength : 1,
				select : function(event, ui) {
					id_fraccion = ui.item.id;
					$("#id_frac1").val(id_fraccion);
					//alert(id_fraccion);
				}
			});

			$("#id_busqueda_label").empty();
			base_url = "/ajax/get_fracciones_by_name/";
			params = "value";
			$("#id_fraccion_fin").autocomplete({
				source : base_url,
				minLength : 1,
				select : function(event, ui) {
					id_fraccion = ui.item.id;
					$("#id_frac2").val(id_fraccion);					
					//alert(id_fraccion);
				}
			});
		}
		 
		
	});

}

