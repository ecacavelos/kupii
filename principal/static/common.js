/*
 * AUTOCOMPLETE para CLIENTES
 * Busca por RUC o NOMBRE
 * parametros: 
 * 1. id del input 
 * 2. id del input donde se coloca el valor de la cedula
 * 3. id del input donde se coloca el id del cliente
 * */
function autocompleteClienteRucONombre(input_id, cedula_input_id, id_cliente_input_id){
	
	input_id = '#' + input_id;
	cedula_input_id = '#' + cedula_input_id;
	id_cliente_input_id = '#' + id_cliente_input_id;
	var cliente_id;
	$(input_id).empty();		
	base_url = base_context + "/ajax/get_cliente_id_by_name_or_ruc/";
	params = "value";
	$(input_id).autocomplete({
		source : base_url,
		minLength : 1,
		create: function () {
                $(this).data('ui-autocomplete')._renderItem = function (ul, item) {
                    return $('<li>')
                        .append('<a>' + item.fields.nombres +" "+ item.fields.apellidos +  '</a>')
                        .appendTo(ul);
                };
         },
		select : function(event, ui) {
			id_cliente = ui.item.fields.id;
			cedula_cliente= ui.item.fields.cedula;
			$(id_cliente_input_id).val(id_cliente);
			$(cedula_input_id).val(cedula_cliente);
		}
	})
	;
}

/*
 * AUTOCOMPLETE para TIMBRADO
 * Busca por NUMERO de Timbrado
 * parametros: 
 * 1. id del input 
 * 2. id del input donde se coloca el valor del numero del timbrado
 * 3. id del input donde se coloca el id del timbrado
 * */
function autocompleteTimbradoPorNumero(input_id, id_timbrado_input_id){
	
	input_id = '#' + input_id;
	id_timbrado_input_id = '#' + id_timbrado_input_id;
	$(input_id).empty();		
	base_url = base_context + "/ajax/get_timbrado_by_numero/";
	$(input_id).autocomplete({
		source : base_url,
		minLength : 1,
		create: function () {
                $(this).data('ui-autocomplete')._renderItem = function (ul, item) {
                    return $('<li>')
                        .append('<a>' + item.fields.numero +  '</a>')
                        .appendTo(ul);
                };
         },
		select : function(event, ui) {
			id_timbrado= ui.item.fields.id;
			numero_timbrado= ui.item.fields.numero;
			$(id_timbrado_input_id).val(id_timbrado);
		}
	});
}
