function retrieve_liquidacion_vendedores() {
	window.location.href = base_context + "/informes/liquidacion_vendedores_reporte_excel?fecha_ini=" + $('#fecha_ini').val() + "&fecha_fin=" + $('#fecha_fin').val() + "&busqueda=" + $('#id_busqueda').val() + "&tipo_busqueda=" + $('#id_tipo_busqueda').val();
}

function validar() {
	if ($('#fecha_ini').val() == "" || $('#fecha_fin').val() == "") {
		alert("Debe ingresar un rango de fechas");
		return;
	}
	$("#frm_busqueda").submit();
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
            create : function() {
								$(this).data('ui-autocomplete')._renderItem = function (ul, item){
									return $('<li>')
										.append('<a>'+ item.fields.nombres+" "+item.fields.apellidos+ '</a>')
										.appendTo(ul);
									};
								},
			select : function(event, ui) {
			id_vendedor = ui.item.pk;
			$("#id_busqueda").val(id_vendedor);
			//alert(id_vendedor);
			}
		});
	//}
	//}
}
