function retrieve_liquidacion_gerentes() {
	window.location.href = base_context + "/informes/liquidacion_gerentes_reporte_excel?fecha_ini=" + $('#fecha_ini').val() + "&fecha_fin=" + $('#fecha_fin').val() + "&tipo_liquidacion=" + $('#id_tipo_liquidacion').val();

}

function validar() {
	if ($('#fecha_ini').val() == "" || $('#fecha_fin').val() == "") {
		alert("Debe ingresar un rango de fechas");
		return;
	}
	if ($('#id_busqueda_label').val() == "") {
		alert("Debe ingresar una fraccion");
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

	var id_fraccion;
	$("#id_busqueda_label").empty();
	base_url = base_context + "/ajax/get_fracciones_by_name/";
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
			id_fraccion = ui.item.pk;
			$("#id_busqueda").val(id_fraccion);
			//alert(id_fraccion);
		}
	});
	//}
	//}
}