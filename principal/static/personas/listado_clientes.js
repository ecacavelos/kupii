$(document).ready(function() {
	if ($("#tipo_busqueda").val() == 'nombre') {
	$("#busqueda_label").val("");
	var id_cliente;
	$("#busqueda").empty();
	base_url = base_context + "/ajax/get_cliente_id_by_name/";
	params = "value";
	$("#busqueda_label").autocomplete({
		source : base_url,
		minLength : 1,
		select : function(event, ui) {
			id_cliente = ui.item.id;
			$("#busqueda").val(id_cliente);
			//alert(id_cliente);
		}
	});
	}
	if ($("#tipo_busqueda").val() == 'cedula') {
	$("#busqueda_label").val("");
	var id_cliente;
	$("#busqueda").empty();
	base_url = base_context + "/ajax/get_cliente_name_id_by_cedula/";
	params = "value";
	$("#busqueda_label").autocomplete({
		source : base_url,
		minLength : 1,
		select : function(event, ui) {
			id_cliente = ui.item.id;
			$("#busqueda").val(id_cliente);
			//alert(id_cliente);
		}
	});
	}
});