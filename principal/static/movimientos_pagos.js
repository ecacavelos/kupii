var total_filas = 1;
var total_cuotas = 0;
$(document).ready(function() {
	$("#id_lote").keydown(validateLotePre);
	$("#id_lote").keyup(validateLotePost);
	$("#main_pago_form").submit(validatePago);
	$("#nro_cuotas_a_pagar").val("1");
	
	$("#id_fecha").val(getCurrentDate());
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
		// Setear idioma al calendario
		$.datepicker.setDefaults($.datepicker.regional['es']);
		$('#id_fecha').mask('##/##/####');
		$("#id_fecha").datepicker({
			dateFormat : 'dd/mm/yy'
		});
		
		$("#id_fecha_venta2").datepicker({
			dateFormat : 'dd/mm/yy'
		});
		$('#id_fecha_venta2').mask('##/##/####');
		$("#id_fecha_venta2").datepicker({
			dateFormat : 'dd/mm/yy'
		});
	
	
	$( "#nro_cuotas_a_pagar" ).change(function() {
  		refresh();
	});
	$( "#id_fecha" ).change(function() {
  		refresh();
	});
	
	$(function() {
		$('#id_modal').modal();
	});

});

window.onload = function() {
};

// Funciones individuales
var global_lote_id = 0;
var splitted_id = "";
var lote_id = 0;
var pagos_realizados = 0;
var venta_id = 0;
var global_proximo_vencimiento;
var global_intereses;
var detalle = "";
var detalles_modificados =new Array();

//Separador de miles y comas en escritura
	function format(comma, period) {
		
		var comma = comma || ',';
		var period = period || '.';
		var split = this.toString().split(',');
		var numeric = split[0];
		var decimal = split.length > 1 ? period + split[1] : '';
		var reg = /(\d+)(\d{3})/;
		for (var i = 1; i < numeric.length; i++) {
			numeric = numeric.replace(".", "");
		}
		while (reg.test(numeric)) {

			numeric = numeric.replace(reg, '$1' + comma + '$2');
		}
		return numeric + decimal;
	}


function refresh(){
	
	calculateMesPago();
	calcularInteres();
}


//Separador de miles que recibe un numero como parametro 
function f(n) {
return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");

}

function validateLotePre(event) {
	// Allow: backspace, delete, tab, escape, and enter
	if (event.keyCode == 46 || event.keyCode == 8 || event.keyCode == 9 || event.keyCode == 27 || event.keyCode == 13 ||
	// Allow: Ctrl+A
	(event.keyCode == 65 && event.ctrlKey === true) ||
	// Allow: home, end, left, right
	(event.keyCode >= 35 && event.keyCode <= 39)) {
		// let it happen, don't do anything
		return;
	} else {
		// Ensure that it is a number and stop the keypress
		if (event.shiftKey || (event.keyCode < 48 || event.keyCode > 57) && (event.keyCode < 96 || event.keyCode > 105 )) {
			event.preventDefault();
		}
	}
}

function validateLotePost(event) {
	if ((event.which >= 48 && event.which <= 57) || (event.which >= 96 && event.which <= 105)) {
		if ($("#id_lote").val().toString().length == 3 || $("#id_lote").val().toString().length == 7) {
			$("#id_lote").val($("#id_lote").val() + '/');
		}
	}
}

function validatePago() {

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
			$('#enviar_pago').removeAttr('disabled');
			return false;	
		} else {
			alert("Se encontró un error en el pago, favor verifique los datos");
			$('#enviar_pago').removeAttr('disabled');
			return false;	
		}
		
	});
	
	return false;
}

function retrieveLote() {
	if ($("#id_lote").val().toString().length == 12) {
		// Extraemos los identificadores correspondientes a la fraccion, manzana y lote.
		splitted_id = $("#id_lote").val().split('/');
		// Hacemos un request POST AJAX para obtener los datos del lote ingresado.
		var request = $.ajax({
			type : "GET",
			url : "/datos/1/",
			data : {
				fraccion : splitted_id[0],
				manzana : splitted_id[1],
				lote : splitted_id[2]
			},
			dataType : "json"
		});
		// Actualizamos el formulario con los datos obtenidos del lote.
		request.done(function(msg) {
			global_lote_id = msg.lote_id;
			//alert(msg);
			var s = "<a class='boton-verde' href=\"/lotes/listado/" + msg.lote_id + "\" target=\"_blank\" \">" + msg.lote_tag + "</a>";

			$("#lote_error").html("");
			$("#lote_superficie").html(msg.superficie);
			$("#lote_seleccionado_detalles").html(s);			
			lote_id = msg.lote_id;
			//var d = new Date();
			//var month = d.getMonth() + 1;
			//var day = d.getDate();
			retrieveVenta();
			fecha_actual = new Date().toJSON().substring(0, 10);

			//$("#id_fecha").val(fecha_actual);
			$("#id_cliente").removeAttr("disabled");
			
			$("#id_vendedor").removeAttr("disabled");
			$("#id_plan_pago").removeAttr("disabled");
			$("#id_monto").removeAttr("disabled");
		});
		// En caso de no poder obtener los datos del lote, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			$("#lote_error").html("El Lote no existe o fue vendido.");
		});
	} else {
		if ($("#id_lote").val().toString().length > 0) {
			$("#lote_error").html("No se encuentra el Lote indicado.");
		}
	}
}

function retrieveLotePago() {
	if ($("#id_lote").val().toString().length == 12) {
		// Extraemos los identificadores correspondientes a la fraccion, manzana y lote.
		splitted_id = $("#id_lote").val().split('/');
		// Hacemos un request POST AJAX para obtener los datos del lote ingresado.
		var request = $.ajax({
			type : "GET",
			url : "/datos/9/",
			data : {
				fraccion : splitted_id[0],
				manzana : splitted_id[1],
				lote : splitted_id[2]
			},
			dataType : "json"		
		});
		
		// Actualizamos el formulario con los datos obtenidos del lote.
		request.done(function(msg) {
			global_lote_id = msg.lote_id;
			//var s = "<a class='boton-verde' href=\"/lotes/listado/" + msg.lote_id + "\" target=\"_blank\" \">" + msg.lote_tag + "</a>";
			var s = "<a class='boton-verde' href=\"/informes/informe_movimientos/?lote_id=" + $("#id_lote").val() + "\&fecha_ini=&fecha_fin="  + "\" target=\"_blank\" \"> Ver Pagos</a>";
			$("#lote_error").html("");
			$("#lote_superficie").html(msg.superficie);			
			$("#lote_seleccionado_detalles").html(s);
			lote_id = msg.lote_id;
			//var d = new Date();
			//var month = d.getMonth() + 1;
			//var day = d.getDate();
			retrieveVenta();			
			//fecha_actual = new Date().toJSON().substring(0, 10);
			
			$("#id_cliente").removeAttr("disabled");
			$("#id_vendedor").removeAttr("disabled");
			$("#id_plan_pago").removeAttr("disabled");
			$("#id_plan_pago_vendedores").removeAttr("disabled");
			$("#id_monto").removeAttr("disabled");
		});
		// En caso de no poder obtener los datos del lote, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			if (jqXHR.responseText.indexOf("Multiple") > -1){
				$("#lote_error").html("existe mas de un lote con el codigo introducido");
			}
			else{
				$("#lote_error").html("Error al obtener el lote");
			}
		});
	} else {
		if ($("#id_lote").val().toString().length > 0) {
			$("#lote_error").html("No se encuentra el Lote indicado.");
		}
	}
}

function retrieveVenta() {
		var request = $.ajax({
			type : "GET",
			url : "/ajax/get_ventas_by_lote/",
			data : {
				lote_id : lote_id
			},
			dataType : "json"
		});
		// Actualizamos el formulario con los datos obtenidos del lote.
		request.done(function(msg) {
			msgaux = msg;
			msg = msg['venta'];
			//alert(msg);
			venta_id = (msg[0]['venta_id']);
			$("#id_venta_pagos").val(venta_id);
			$("#id_cliente").val(msg[0]['cliente_id']);
			$("#cliente_seleccionado").val(msg[0]['cliente']);
			$("#id_vendedor").val(msg[0]['vendedor_id']);
			$("#vendedor_seleccionado").val(msg[0]['vendedor']);
			$("#plan_pago").val(msg[0]['plan_de_pago']);
			$("#id_plan_pago").val(msg[0]['plan_de_pago_id']);
			$("#plan_pago_vendedores").val(msg[0]['plan_de_pago_vendedor']);
			$("#id_plan_pago_vendedores").val(msg[0]['plan_de_pago_vendedor_id']);
			$("#precio_de_cuota").val(msg[0]['precio_de_cuota']);
			//$("#monto_cuota").val(msg[0]['precio_de_cuota']);
			//$("#monto_cuota2").html(String(msg[0]['precio_de_cuota']));
			//$("#monto_cuota2").html(String(format.call($("#monto_cuota2").html().split(' ').join(''),'.',',')));
			$("#id_fecha_venta").val(msg[0]['fecha_de_venta']);
			
			var fechita = String(msg[0]['fecha_de_venta']);
			console.log(fechita);
			fechita = $.datepicker.parseDate('yy-mm-dd', fechita);
			$("#id_fecha_venta2").datepicker("setDate", fechita);
			$("#id_fecha_venta2").datepicker({ dateFormat: 'dd/mm/yy' });
			$("#id_fecha_venta2").datepicker('disable');
			
			$("#resumen_cuotas").empty();
			$("#resumen_cuotas").append(msgaux.cuotas_details.cant_cuotas_pagadas + '/' + msgaux.cuotas_details.cantidad_total_cuotas);
			//$("#resumen_cuotas").empty();
			
			$("#proximo_vencimiento").empty();
			$("#proximo_vencimiento").append(msgaux.cuotas_details.proximo_vencimiento);
			global_proximo_vencimiento=msgaux.cuotas_details.proximo_vencimiento;
						
			refresh();
			//calculateTotalCuotas();			
			//calculateTotalPago();

			retrieveCliente();
			retrieveVendedor();
			retrievePlanPago();
			retrievePlanPagoVendedor();
	
		});
		request.done(function(msg) {
			console.log(msg);
		});
}

function calcularInteres() {
	var fecha_pago=$('#id_fecha').val();
	var proximo_vencimiento=global_proximo_vencimiento;
	var lote_id=global_lote_id;
	var nro_cuotas_a_pagar = $('#nro_cuotas_a_pagar').val();
	 	var request = $.ajax({
			type : "POST",
			url : "/movimientos/calcular_interes/",
			data : {
				lote_id : lote_id,
				fecha_pago : fecha_pago,
				proximo_vencimiento : proximo_vencimiento,
				nro_cuotas_a_pagar : nro_cuotas_a_pagar
			},
			dataType : "json"
		});
		// Actualizamos el formulario con los datos obtenidos.
		request.done(function(msg) {
			detalle=msg;
			console.log(detalle);
			var intereses=0;
			for(i=0;i<msg.length;i++){
				intereses+=msg[i]['intereses'];
			}
			global_intereses=intereses;
			//calculateTotalCuotas();
			calculateTotalPago();		
		});
}


function dibujarDetalle() {
	//var dato = 'este es un texto que llego por ajax';
	$('#contenido_modal').empty();
	$('#contenido_modal').append('<div id="listado-item-lote">');
	$('#contenido_modal').append('<div cellpadding="0" cellspacing="0" class="listado-ventas" align="center">');
	$('#contenido_modal').append("<th>Cuota Nro.</th><th>Vencimiento</th><th>Dias Atraso</th><th>Interes</th>");
	for(i=0;i<detalle.length;i++){		
		$('#contenido_modal').append('<tr><td>'+detalle[i]['nro_cuota']+'</td><td>'+
		detalle[i]['vencimiento']+'</td><td>'+detalle[i]['dias_atraso']+
		'</td><td><input style="width: 70px;" class="interes" id="interes_' + i + '" type="number" value=' + f(detalle[i]['intereses']).replace(/\./g, '')+'></td></tr>');
	}
	$('#contenido_modal').append('<button class="button_verde" id="modificar_mora" data-toggle="modal" data-target=".bs-example-modal-sm" value="Modificar">Modificar</button>');
	$('#contenido_modal').append('</div>');
	$('#modificar_mora').click(function() {
		this.style.backgroundColor = '#66A385';
		modificarMontos();
		return false;
	});
}


function modificarMontos(){
	var intereses =0;
	global_intereses =0;
	for(i=0;i<detalle.length;i++){
		detalle[i]['intereses']= parseInt($('#interes_' + i).val());
		intereses+=detalle[i]['intereses'];
	}
	global_intereses=intereses;
	//calculateTotalCuotas();
	calculateTotalPago();
}
function retrieveCliente() {
	if ($("#id_cliente").val().toString().length > 0) {
		// Hacemos un request POST AJAX para obtener los datos del cliente ingresado.
		var request = $.ajax({
			type : "GET",
			
			url : "/datos/2/",
			data : {
				cliente : $("#id_cliente").val()
			}
		});
		// Actualizamos el formulario con los datos obtenidos del cliente.
		request.done(function(msg) {
			$("#cliente_error").html("");
			$("#cliente_seleccionado").html(msg);

		});
		// En caso de no poder obtener los datos del cliente, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			$("#cliente_error").html("No se pueden obtener los datos del Cliente.");
			$("#cliente_seleccionado").html("");
		});
	}
}

function retrieveVendedor() {
	if ($("#id_vendedor").val().toString().length > 0) {
		// Hacemos un request POST AJAX para obtener los datos del vendedor ingresado.
		var request = $.ajax({
			type : "GET",
			url : "/datos/3/",
			data : {
				vendedor : $("#id_vendedor").val()
			}
		});
		// Actualizamos el formulario con los datos obtenidos del vendedor.
		request.done(function(msg) {
			$("#vendedor_error").html("");
			$("#vendedor_seleccionado").html(msg);

		});
		// En caso de no poder obtener los datos del vendedor, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			$("#vendedor_error").html("No se pueden obtener los datos del Vendedor.");
			$("#vendedor_seleccionado").html("");
		});
	}
}

function retrievePlanPagoVendedor() {
	if ($("#id_plan_pago_vendedores").val().toString().length > 0) {
		// Hacemos un request POST AJAX para obtener los datos del plan de pagos ingresado.
		var request = $.ajax({
			type : "GET",
			url : "/datos/4/",
			data : {
				plan_pago_vendedor : $("#id_plan_pago_vendedores").val()
			}
		});
		// Actualizamos el formulario con los datos obtenidos del plan de pagos.
		request.done(function(msg) {
			$("#plan_pago_vendedor_error").html("");
			$("#plan_pago_vendedor_seleccionado").html(msg.nombre_del_plan);

		});
		// En caso de no poder obtener los datos del plan de pagos, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			$("#plan_pago_vendedor_error").html("No se pueden obtener los datos del Plan de Pago.");
			$("#plan_pago_vendedor_seleccionado").html("");
		});
	}
}

function retrievePlanes(){
	//$("#id_mes_pago").val("0");
	retrieveFraccion();
	retrieveLotePago();
	retrievePlanPagoVendedor(); 
}

function retrievePlanPago() {
	if ($("#id_plan_pago").val().toString().length > 0) {
		// Hacemos un request POST AJAX para obtener los datos del plan de pagos ingresado.
		var request = $.ajax({
			type : "GET",
			url : "/datos/5/",
			data : {
				plan_pago : $("#id_plan_pago").val()
			}
		});
		// Actualizamos el formulario con los datos obtenidos del plan de pagos.
		request.done(function(msg) {
			$("#plan_pago_error").html("");
			$("#plan_pago_seleccionado").html(msg.nombre_del_plan);

		});
		// En caso de no poder obtener los datos del plan de pagos, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			$("#plan_pago_error").html("No se pueden obtener los datos del Plan de Pago.");
			$("#plan_pago_seleccionado").html("");
		});
	}
}

function calculateTotalCuotas(total_cuotas) {
	//alert('calculando total cuotas');
	$("#total_cuotas").val(total_cuotas);
	$("#total_cuotas2").html(String(total_cuotas));
	$("#total_cuotas2").html(String(format.call($("#total_cuotas2").html().split(' ').join(''),'.',',')));
	//$("#total_mora").removeAttr("disabled");
	//alert(global_intereses);
}

function calculateTotalPago() {
	//alert('calculando total pago');
	var total_cuotas = $("#total_cuotas").val();
	var total_mora=global_intereses;
	var total_pago = parseInt( total_cuotas) + parseInt( total_mora);
	total_cuotas = parseInt(total_cuotas);
	$("#total_mora").val(total_mora);
	$("#total_mora2").html(String(total_mora));
	$("#total_mora2").html(String(format.call($("#total_mora2").html().split(' ').join(''),'.',',')));
	
	total_pago = parseInt(total_pago);
	$("#total_pago").val(total_pago);
	$("#total_pago2").html(String(total_pago));
	$("#total_pago2").html(String(format.call($("#total_pago2").html().split(' ').join(''),'.',',')));
	$("#guardar_pago").removeAttr("disabled");
}

function calculateMesPago() {
	var request = $.ajax({
			type : "GET",
			url : "/ajax/get_mes_pagado_by_id_lote/",
			data : {
				lote_id : lote_id,
				cant_cuotas : $("#nro_cuotas_a_pagar").val()
			},
			dataType : "json"
		});
		// Actualizamos el formulario con los datos obtenidos del lote.
		request.done(function(msg) {
			$("#id_cuota_pagar").empty();
			$("#id_cuota_pagar").append('<tr><th>Nro Cuota</th><th>Fechas</th><th>Monto Cuota</th></tr>');
			addRow(msg);
		});
}

function addRow(msg){
	total_cuotas=0;	
	 var table = document.getElementById("id_cuota_pagar");
	 for(i =0; i < msg.cuotas_a_pagar.length; i++){
	 	$("#id_cuota_pagar").append('<tr><td>' + msg.cuotas_a_pagar[i].nro_cuota+ '</td><td>' + msg.cuotas_a_pagar[i].fecha+'</td><td>' +msg.cuotas_a_pagar[i].monto_cuota+ '</td></tr>');
	 	total_cuotas += msg.cuotas_a_pagar[i].monto_cuota;
	 }
	 calculateTotalCuotas(total_cuotas);
	 calculateTotalPago();	
}

function getCurrentDate(){
	var today = new Date();
	var dd = today.getDate();
	var mm = today.getMonth()+1; //January is 0!
	var yyyy = today.getFullYear();
	
	if(dd<10) {
	    dd='0'+dd;
	} 
	
	if(mm<10) {
	    mm='0'+mm;
	} 
	
	today = dd+ '/'+mm+'/'+yyyy;
	return today;
}
