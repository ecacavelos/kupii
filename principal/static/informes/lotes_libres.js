function validar() {
	if ($('#fraccion_ini').val() == 0 || $('#fraccion_fin').val() == 0 || $('#fraccion_ini').val() == "" || $('#fraccion_fin').val() == "") {
		alert("Debe ingresar un rango de fracciones");
		return;
	}
	$("#frm_busqueda").submit();
}

function retrieve_lotes_libres() {
	window.location.href = "/informes/lotes_libres_reporte_excel?fraccion_ini=" + $('#fraccion_ini').val() + "&fraccion_fin=" + $('#fraccion_fin').val();
}

function setup_inputs() {
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

