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
		create : function(){
			$(this).data('ui-autocomplete')._renderItem = function(ul,item){
				return $('<li>').append('<a>' +item.fields.nombres + " "+ item.fields.apellidos+'</a>').appendTo(ul);
				};
		},
		select : function(event, ui) {
			cliente_id = ui.item.pk;
			cedula_cliente= ui.item.fields.cedula;
			$(input_id).val(ui.item.fields.nombres+" "+ui.item.fields.apellidos);
			//name_cliente=ui.item.fields.nombres+" "+ui.item.fields.apellidos;
			//$("#id_name_cliente").val(name_cliente);
			$(id_cliente_input_id).val(cliente_id);
			$(cedula_input_id).val(cedula_cliente);
			$(this).trigger('change'); 
    		return false; 
		}
	});
}

/*
 * AUTOCOMPLETE para PROPIETARIOS
 * Busca por RUC o NOMBRE
 * parametros: 
 * 1. id del input 
 * 2. id del input donde se coloca el valor de la cedula
 * 3. id del input donde se coloca el id del propietario
 * */
function autocompletePropietarioRucONombre(input_id, cedula_input_id, id_propietario_input_id){
	
	input_id = '#' + input_id;
	cedula_input_id = '#' + cedula_input_id;
	id_propietario_input_id = '#' + id_propietario_input_id;
	var propietario_id;
	$(input_id).empty();		
	base_url = base_context + "/ajax/get_propietario_id_by_name_or_ruc/";
	params = "value";
	$(input_id).autocomplete({
		source : base_url,
		minLength : 1,
		create : function(){
			$(this).data('ui-autocomplete')._renderItem = function(ul,item){
				return $('<li>').append('<a>' +item.fields.nombres + " "+ item.fields.apellidos+'</a>').appendTo(ul);
				};
		},
		select : function(event, ui) {
			propietario_id = ui.item.pk;
			cedula_cliente= ui.item.fields.cedula;
			$(input_id).val(ui.item.fields.nombres+" "+ui.item.fields.apellidos);
			//name_cliente=ui.item.fields.nombres+" "+ui.item.fields.apellidos;
			//$("#id_name_cliente").val(name_cliente);
			$(id_propietario_input_id).val(propietario_id);
			$(cedula_input_id).val(cedula_cliente);
			$(this).trigger('change'); 
    		return false; 
		}
	});
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
		create : function(){
			$(this).data('ui-autocomplete')._renderItem = function(ul,item){
				return $('<li>').append('<a>' +item.fields.numero+'</a>').appendTo(ul);
				};
		},
		select : function(event, ui) {
			event.preventDefault();
			id_timbrado = ui.item.pk;
			numero_timbrado= ui.item.fields.numero;
			$(timbrado).val(numero_timbrado);
			$(id_timbrado_input_id).val(id_timbrado);
		}
	});
}

function autocompleteClientePorNombreOCedula(tipo_busqueda, busqueda_label, busqueda){
	if (tipo_busqueda == 'nombre') {
		console.log("por nombre");
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
	if (tipo_busqueda == 'cedula') {
		console.log("por cedula");
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
			event.preventDefault();
			$("#busqueda").val(id_cliente);
			//alert(id_cliente);
			$("#busqueda_label").val(ui.item.cedula);
			
		}
	});
	}
}

function autocompletePropietarioPorNombreOCedula(tipo_busqueda, busqueda_label, busqueda){
	if (tipo_busqueda == 'nombre') {
		console.log("por nombre");
	$("#busqueda_label").val("");
	var id_propietario;
	$("#busqueda").empty();
	base_url = base_context + "/ajax/get_propietario_id_by_name/";
	params = "value";
	$("#busqueda_label").autocomplete({
		source : base_url,
		minLength : 1,
		select : function(event, ui) {
			id_propietario = ui.item.id;
			$("#busqueda").val(id_propietario);
			//alert(id_cliente);
		}
	});
	}
	
	if (tipo_busqueda == 'cedula') {
		console.log("por cedula");
	$("#busqueda_label").val("");
	var id_propietario;
	$("#busqueda").empty();
	base_url = base_context + "/ajax/get_propietario_name_id_by_cedula/";
	params = "value";
	$("#busqueda_label").autocomplete({
		source : base_url,
		minLength : 1,
		
		select : function(event, ui) {
			event.preventDefault();
			id_propietario = ui.item.id;
			$("#busqueda").val(id_propietario);
			$("#busqueda_label").val(ui.item.cedula);
			//alert(id_cliente);
		}
	});
	}
}

function autocompleteVendedorPorNombreOCedula(tipo_busqueda, busqueda_label, busqueda){
	if (tipo_busqueda == 'nombre') {
		console.log("por nombre");
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
			//alert(id_cliente);
		}
	});
	}
	
	if (tipo_busqueda == 'cedula') {
		console.log("por cedula");
	$("#busqueda_label").val("");
	var id_vendedor;
	$("#busqueda").empty();
	base_url = base_context + "/ajax/get_vendedor_name_id_by_cedula/";
	params = "value";
	$("#busqueda_label").autocomplete({
		source : base_url,
		minLength : 1,
		
		select : function(event, ui) {
			event.preventDefault();
			id_vendedor = ui.item.id;
			$("#busqueda").val(id_vendedor);
			$("#busqueda_label").val(ui.item.cedula);
			//alert(id_cliente);
		}
	});
	}
}

/*
 * AUTOCOMPLETE para Vendedor
 * Busca por el nombre del vendedor
 * parametros: 
 * 1. id del input 
 * 2. id del input donde se coloca el nombre del vendedor
 * */
function autocompleteVendedorNombre(input_id,  id_vendedor_input_id){
	
	input_id = '#' + input_id;
	id_vendedor_input_id = '#' + id_vendedor_input_id;
	var vendedor_id;
	$(input_id).empty();		
	base_url = base_context + "/ajax/get_vendedor_id_by_name/";
	params = "value";
	$(input_id).autocomplete({
		source : base_url,
		minLength : 1,
		create : function(){
			$(this).data('ui-autocomplete')._renderItem = function(ul,item){
				return $('<li>').append('<a>' +item.nombres + " "+ item.apellidos+'</a>').appendTo(ul);
				};
		},
		select : function(event, ui) {
			vendedor_id = ui.item.id;
			$(input_id).val(ui.item.nombres+" "+ui.item.apellidos);
			$(id_vendedor_input_id).val(vendedor_id);
			$(this).trigger('change'); 
    		return false; 
		}
	});
}

/*
 * AUTOCOMPLETE para Plan de Pago
 * Busca por el nombre del plan de pago
 * parametros: 
 * 1. id del input 
 * 2. id del input donde se coloca el nombre del plan de pago
 * */
function autocompletePlandePago(input_id,  id_plandepago_input_id){
	
	input_id = '#' + input_id;
	id_plandepago_input_id = '#' + id_plandepago_input_id;
	var planpago_id;
	$(input_id).empty();		
	base_url = base_context + "/ajax/get_plan_pago/";
	params = "value";
	$(input_id).autocomplete({
		source : base_url,
		minLength : 1,
		create : function(){
			$(this).data('ui-autocomplete')._renderItem = function(ul,item){
				return $('<li>').append('<a>'+ item.nombre_del_plan +'</a>').appendTo(ul);
				};
		},
		select : function(event, ui) {
			planpago_id = ui.item.id;
			$(input_id).val(ui.item.nombre_del_plan);
			$(id_plandepago_input_id).val(planpago_id);
			$(this).trigger('change'); 
    		return false; 
		}
	});
}

