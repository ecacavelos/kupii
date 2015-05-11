$(document).ready(function() {
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