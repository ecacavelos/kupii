$(document).ready(function() {
	$("#id_fecha_venta").focus();
	// Setear idioma al calendario
	$.datepicker.setDefaults($.datepicker.regional['es']);
	$("#id_fecha_venta").datepicker({
		dateFormat : 'dd/mm/yy'
	});
	$('#id_fecha_venta').mask('##/##/####');
	$("#id_fecha_venc").datepicker({
		dateFormat : 'dd/mm/yy'
	});
	$('#id_fecha_venc').mask('##/##/####');
	$('.grid_6').hide();
	// 1. Se setea el autocomplete para buscar clientes
		autocompleteClienteRucONombre('id_name_cliente', 'id_cedula_cliente', 'id_cliente');
	// 2. Se setea el autocomplete para buscar vendedor
		autocompleteVendedorNombre('id_name_vendedor', 'id_vendedor');
	// 3. Se setea el autocomplete para buscar plan de pago
		autocompletePlandePago('id_name_ppago', 'id_plan_de_pago');
	// 4. Se setea el autocomplete para buscar plan de pago vendedor
		autocompletePlandePagoVendedor('id_name_ppago_vendedor', 'id_plan_de_pago_vendedor');
	//Cambiar calendario a español
	$.datepicker.regional['es'] = {
		closeText : 'Cerrar',
		prevText : '<Ant',
		nextText : 'Sig>',
		currentText : 'Hoy',
		monthNames : ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
		monthNamesShort : ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
		dayNames : ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
		dayNamesShort : ['Dom', 'Lun', 'Mar', 'Mié', 'Juv', 'Vie', 'Sáb'],
		dayNamesMin : ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sá'],
		weekHeader : 'Sm',
		dateFormat : 'dd/mm/yy',
		firstDay : 1,
		isRTL : false,
		showMonthAfterYear : false,
		yearSuffix : ''
	};
	/*
	$('#entrega_inicial_id').mask('000.000.000.000.000.000.000', {
		byPassKeys : [ null ],
		reverse : true,
	});
	$('#id_precio_de_cuota').mask('000.000.000.000.000.000.000', {
		byPassKeys : [ null ],
		reverse : true,
	});
	$('#id_precio_f_venta').mask('000.000.000.000.000.000.000', {
		byPassKeys : [ null ],
		reverse : true,
	});*/
});

function validateVentaMod(event) {

	event.preventDefault();
	var request4 = $.ajax({
		type : "POST",
		url : "/movimientos/pago_cuotas/",
		data : {
			ingresar_pago : true,
			pago_venta_id : venta_id,
			pago_lote_id : global_lote_id,
			pago_fecha_de_pago : $("#id_fecha").val(),
			pago_nro_cuotas_a_pagar : $("#nro_cuotas_a_pagar").val(),
			pago_cliente_id : $("#id_cliente").val(),
			pago_plan_de_pago_id : $("#id_plan_pago").val(),
			pago_plan_de_pago_vendedor_id: $("#id_plan_pago_vendedores").val(),
			pago_vendedor_id : $("#id_vendedor").val(),
			pago_total_de_cuotas : $("#total_cuotas").val(),
			pago_total_de_mora : $("#total_mora").val(),
			pago_total_de_pago : $("#total_pago").val()
		}
	});
	request4.done(function(msg) {
		top.location.href = "/movimientos/pago_cuotas";
	});
	request4.fail(function(jqXHR, textStatus) {
		if (jqXHR.responseText == "La cantidad de cuotas a pagar, es mayor a la cantidad de cuotas restantes."){
			alert(jqXHR.responseText);	
		} else {
			alert("Se encontró un error en el pago, favor verifique los datos");
		}
		
	});
	
	return false;
}

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
			event.preventDefault();
			alert("Al modificar el cliente esto modificara a todos los pagos relacionados a la venta");
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
			alert("Al modificar el vendedor esto modificara a todos los pagos relacionados a la venta");
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
			alert("Al modificar el plan de pago esto modificara a todos los pagos relacionados a la venta");
			planpago_id = ui.item.id;
			$(input_id).val(ui.item.nombre_del_plan);
			$(id_plandepago_input_id).val(planpago_id);
			$(this).trigger('change'); 
    		return false; 
		}
	});
}

/*
 * AUTOCOMPLETE para Plan de Pago Vendedor
 * Busca por el nombre del plan de pago
 * parametros: 
 * 1. id del input 
 * 2. id del input donde se coloca el nombre del plan de pago
 * */
function autocompletePlandePagoVendedor(input_id,  id_plandepago_vendedor_input_id){
	
	input_id = '#' + input_id;
	id_plandepago_vendedor_input_id = '#' + id_plandepago_vendedor_input_id;
	var planpago_vendedor_id;
	$(input_id).empty();		
	base_url = base_context + "/ajax/get_plan_pago_vendedor/";
	params = "value";
	$(input_id).autocomplete({
		source : base_url,
		minLength : 1,
		create : function(){
			$(this).data('ui-autocomplete')._renderItem = function(ul,item){
				return $('<li>').append('<a>'+ item.nombre +'</a>').appendTo(ul);
				};
		},
		select : function(event, ui) {
			alert("Al modificar el plan de pago esto modificara a todos los pagos relacionados a la venta");
			planpago_vendedor_id = ui.item.id;
			$(input_id).val(ui.item.nombre);
			$(id_plandepago_input_id).val(planpago_vendedor_id);
			$(this).trigger('change'); 
    		return false; 
		}
	});
}
