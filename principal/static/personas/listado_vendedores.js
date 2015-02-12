$(document).ready(function() {
	if ($("#tipo_busqueda").val() == 'nombre') {
	$("#busqueda_label").val("");
	var id_vendedor;
	$("#busqueda").empty();
	base_url = base_context + "/ajax/get_vendedor_id_by_name/";
	params = "value";
	$("#busqueda_label").autocomplete({
		source : base_url,
		minLength : 1,
		select : function(event, ui) {
			id_vendedor = ui.item.id;
			$("#busqueda").val(id_vendedor);
			alert(id_vendedor);
		}
	});
	}
	if ($("#tipo_busqueda").val() == 'cedula') {
	$("#busqueda_label").val("");
	var id_vendedor;
	$("#busqueda").empty();
	base_url = base_context + "/ajax/get_vendedor_name_id_by_cedula/";
	params = "value";
	$("#busqueda_label").autocomplete({
		source : base_url,
		minLength : 1,
		select : function(event, ui) {
			id_vendedor = ui.item.id;
			$("#busqueda").val(id_vendedor);
			alert(id_vendedor);
		}
	});
	}
});