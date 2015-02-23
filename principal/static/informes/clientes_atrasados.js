function buscar() {
		if ($("#tipo_busqueda").val() == 0) {
			alert("Debe elegir un tipo de busqueda.");
		}		
	}

	function retrieve_clientes_atrasados() {
		var filter_get_parameters = "?";
		filter_get_parameters += "meses_atraso=" + $('#meses_atraso').val();
		filter_get_parameters += "&" + "fraccion=" + $('#fraccion').val();
		window.location.href = base_context + "/informes/clientes_atrasados_reporte_excel" + filter_get_parameters;
	}

	function validar() {
		var filter_get_parameters = "?";
		filter_get_parameters += "meses_atraso=" + $('#meses_atraso').val();
		filter_get_parameters += "&" + "fraccion=" + $('#fraccion').val();
		window.location.href = base_context + "/informes/clientes_atrasados_reporte_excel" + filter_get_parameters;
		$("#frm_busqueda").submit();
	}

