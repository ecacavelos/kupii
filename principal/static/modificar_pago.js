$(document).ready(function() {
	$("#id_fecha").focus();
	// Setear idioma al calendario
	$.datepicker.setDefaults($.datepicker.regional['es']);
	$("#id_fecha").datepicker({
		dateFormat : 'dd/mm/yy'
	});
	$('#id_fecha').mask('##/##/####');
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
	$('#id_fecha').blur(function() {
		$('#enviar_pago').attr("disabled",false);
		if($('#id_fecha').val() != ""){
			isValidDate($('#id_fecha').val());
		}
});
});

function validatePago(event) {

	event.preventDefault();
	var request4 = $.ajax({
		type : "POST",
		url : "/movimientos/modificar_pago_de_cuotas/",
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

function isValidDate(dateString)
{
    // First check for the pattern
    if(!/^\d{1,2}\/\d{1,2}\/\d{4}$/.test(dateString))
    {
        alert("Formato de fecha incorrecto");
        $('#enviar_pago').attr("disabled",true);
    	$('#id_fecha').val("");
        return false;
    }

    // Parse the date parts to integers
    var parts = dateString.split("/");
	var day = parseInt(parts[0], 10);	
    var month = parseInt(parts[1], 10);
    var year = parseInt(parts[2], 10);

    // Check the ranges of month and year
    if(year < 1000 || year > 3000 || month == 0 || month > 12){
    	alert("Formato de fecha incorrecto");
        $('#enviar_pago').attr("disabled",true);
        $('#id_fecha').val("");
        return false;
    }

    var monthLength = [ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ];

    // Adjust for leap years
    if(year % 400 == 0 || (year % 100 != 0 && year % 4 == 0))
        monthLength[1] = 29;

    // Check the range of the day
    if(!(day > 0 && day <= monthLength[month - 1]))
    {
    	alert("Formato de fecha incorrecto");
        $('#enviar_pago').attr("disabled",true);
        $('#id_fecha').val("");
        return false;
    }else
    {
    	return day > 0 && day <= monthLength[month - 1];
    }
};