var total_filas = 1;
var total_cuotas = 0;
var cancelado = false;
$(document).ready(function() {
	$("#id_lote").keydown(validateLotePre);
	$("#id_lote").keyup(validateLotePost);
	$("#main_pago_form").submit(validatePago);
	$("#nro_cuotas_a_pagar").val("1");
	$(".fecha_pago").val(fecha_actual);
	$('.grid_6').hide();
	$('.fecha_pago').mask('##/##/####');
	var detalle_interes = "";
	$("#id_lote").focus();
	if(grupo != "2"){
		$(".fecha_pago").datepicker({
			closeText : 'Cerrar',
			prevText : '<Ant',
			nextText : 'Sig>',
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
		});
	}else{
		$(".fecha_pago").prop('readonly', true);
	}
	
	if (codigo_lote != ""){
		$("#id_lote").focus();
		$("#id_lote").val(codigo_lote);
		$("#lote_seleccionado_detalles").focus();
		$("#id_lote").trigger( "blur" );
		
	}
	
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
	$( ".fecha_pago" ).change(function() {
  		refresh();
	});
	
	$(function() {
		$('#id_modal').modal();
	});

    $(".checkbox_cuota_obsequio").change(function () {
        if (document.getElementById("checkbox_cuota_obsequio").checked == true){
           $("#cuota_obsequio").val(1);
        }else{
           $("#cuota_obsequio").val(0);
        }
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

function convertDate(inputFormat) {
  function pad(s) { return (s < 10) ? '0' + s : s; }
  var d = new Date(inputFormat);
  return [pad(d.getDate()), pad(d.getMonth()+1), d.getFullYear()].join('/');
}

function validatePago() {

	var request4 = $.ajax({
		type : "POST",
		url : base_context + "/movimientos/pago_cuotas/",
		data : {
			ingresar_pago : true,
			pago_venta_id : venta_id,
			pago_lote_id : global_lote_id,
			pago_fecha_de_pago : $(".fecha_pago").val(),
			pago_nro_cuotas_a_pagar : $("#nro_cuotas_a_pagar").val(),
			pago_cliente_id : $("#id_cliente").val(),
			pago_plan_de_pago_id : $("#id_plan_pago").val(),
			pago_plan_de_pago_vendedor_id: $("#id_plan_pago_vendedores").val(),
			pago_vendedor_id : $("#id_vendedor").val(),
			pago_total_de_cuotas : $("#total_cuotas").val(),
			pago_total_de_mora : $("#total_mora").val(),
			pago_total_de_pago : $("#total_pago").val(),
			detalle : $("#detalle").val(),
			interes_original :	$("#interes_original").val(),
			resumen_cuotas : $("#resumen_cuotas").text().split("/")[0],
			cuota_obsequio : $("#cuota_obsequio").val()
		}
	});
	request4.done(function(msg) {
		if ( $("#facturar").val() == 'NO' ){
			top.location.href = base_context + "/movimientos/pago_cuotas";
		} else if ( $("#facturar").val() == 'SI' ){
			top.location.href = base_context + "/facturacion/facturar_operacion/1/"+msg[0].id;
		}
		
		
	});
	request4.fail(function(jqXHR, textStatus) {
		if (jqXHR.responseText == "La cantidad de cuotas a pagar, es mayor a la cantidad de cuotas restantes."){
			alert(jqXHR.responseText);
			$('#enviar_pago').removeAttr('disabled');
			$('#enviar_pago_factura').removeAttr('disabled');
			return false;	
		} else {
			alert("Se encontró un error en el pago, favor verifique los datos");
			$('#enviar_pago').removeAttr('disabled');
			$('#enviar_pago_factura').removeAttr('disabled');
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
			url : base_context + "/datos/1/",
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
			url : base_context + "/datos/9/",
			data : {
				fraccion : splitted_id[0],
				manzana : splitted_id[1],
				lote : splitted_id[2],

			},
			dataType : "json"		
		});
		
		// Actualizamos el formulario con los datos obtenidos del lote.
		request.done(function(msg) {
			global_lote_id = msg.lote_id;
			var s = "<a class='boton-verde' href= "+base_context+ "/informes/informe_movimientos/?lote_ini="
				+ $("#id_lote").val() +"\&lote_fin="+ $("#id_lote").val() +"\&fecha_ini=&fecha_fin="
				+ "\" target=\"_blank\" \"> Ver Pagos</a>";
			$("#lote_error").html("");
			$("#lote_superficie").html(msg.superficie);			
			$("#lote_seleccionado_detalles").html(s);
			lote_id = msg.lote_id;
			$("#id_obs_lote").html(msg.obs);
			//var d = new Date();
			//var month = d.getMonth() + 1;
			//var day = d.getDate();
			//alert(msg.obs);
			console.log('Contenido msg: '+msg.obs);


			// Get the modal
			var modal = $("#myModal");
			$("#mensaje_obs_lote").html(msg.obs);
			if (msg.obs != "" && msg.obs != null){
				modal.show();
			}

			// Get the <span> element that closes the modal
			var span = $(".close")[0];


			// When the user clicks on <span> (x), close the modal
			span.onclick = function() {
			    modal.hide();
			}

			// When the user clicks anywhere outside of the modal, close it
			window.onclick = function(event) {
			    if (event.target == modal) {
    			    modal.hide();
   				 }
			}


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
			url : base_context + "/ajax/get_ventas_by_lote/",
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
	var fecha_pago=$('.fecha_pago').val();
	var proximo_vencimiento=global_proximo_vencimiento;
	var lote_id=global_lote_id;
	var nro_cuotas_a_pagar = $('#nro_cuotas_a_pagar').val();
	 	var request = $.ajax({
			type : "POST",
			url : base_context + "/movimientos/calcular_interes/",
			data : {
				lote_id : lote_id,
				fecha_pago : fecha_pago,
				proximo_vencimiento : proximo_vencimiento,
				nro_cuotas_a_pagar : nro_cuotas_a_pagar
			},
			dataType : "json"
		});
		// Actualizamos el formulario con los datos obtenidos.
		request.success(function(msg) {
			detalle=msg;
			console.log(detalle);
			var intereses=0;
            var gestion_cobranza=0;
			if(detalle.length > 0)
			{
				var nro_cuotas_a_pagar=$('#nro_cuotas_a_pagar').val();
                var f1 = $(".fecha_pago").val().split("/");
                var fecha_pago = new Date(f1[2], f1[1] - 1, f1[0]);
                //alert(fecha_pago);
				//for(i=0;i<nro_cuotas_a_pagar;i++){
				
			for ( i = 0; i < detalle.length; i++) {
				if (detalle[i]['tipo'] == 'normal' ) {
					var f2 = (detalle[i]['vencimiento_gracia']).split("/");
					var fecha_vencimiento_pago = new Date(f2[2], f2[1] - 1, f2[0]);
					//alert(fecha_vencimiento_pago);
					if (fecha_pago > fecha_vencimiento_pago) {
						console.log("Sumando intereses");
						intereses = intereses + detalle[i]['intereses'];
					}
				} else {
					gestion_cobranza = detalle[detalle.length-1]['gestion_cobranza'];
				}
			}

                //if(detalle[detalle.length-1]['gestion_cobranza']){
                //    gestion_cobranza=detalle[detalle.length-1]['gestion_cobranza'];
                //}
			}

			detalle_interes = generarDetalleJSON();			
			$("#detalle").val(detalle_interes);	
			global_intereses=intereses+gestion_cobranza;
            //alert(global_intereses);
			$("#interes_original").val(global_intereses);

			calculateTotalPago();		
		});
		request.error(function(msg) {
			window.location.href = base_context + "/login/";
		});	
}


function dibujarDetalle() {
    //var dato = 'este es un texto que llego por ajax';
    $('#contenido_modal').empty();
    modal_html ="";
    modal_html +='<div id="listado-item-lote">';
    modal_html +='<div cellpadding="1" cellspacing="0" class="listado-ventas" align="center">';
    modal_html +="<table class='listado-cuotas-estado' style='text-align: center;'><th>Cuota Nro.</th><th>Vencimiento</th><th>Dias Atraso</th><th>Interes</th>";


    var nro_cuotas_a_pagar = $('#nro_cuotas_a_pagar').val();
    console.log(detalle);
    if (detalle.length > 0) {
        //for (i = 0; i < nro_cuotas_a_pagar; i++) {
        for (i = 0; i < detalle.length; i++) {
        	if (detalle[i]['tipo']== 'normal'){	
	            modal_html +='<tr style="text-align:center;"><td style="text-align:center;">' + detalle[i]['nro_cuota'] + '</td><td style="text-align:center;">' +
	            detalle[i]['vencimiento'] + '</td><td style="text-align:center;">' + detalle[i]['dias_atraso'] +
	            '</td><td style="text-align:center;"><input style="width: 70px;" class="interes" id="interes_' + i + '" type="text" value=' + detalle[i]['intereses'] + '></td></tr>';
	            
	            if (i == detalle.length-1) {
	            	modal_html +='</table><br>Fecha ultimo vencimiento con 5 dias de gracia: ' + detalle[i]['vencimiento_gracia'] + '</br>';
	            }
	            
	        } else {
	        	modal_html +='</table><br>Fecha ultimo vencimiento con 5 dias de gracia: ' + detalle[i-1]['vencimiento_gracia'] + '</br>';
	        	modal_html +='</tr><td>Gestion de Cobranza: </td><td><input style="width: 100px;" class="interes" id="id_gestion_cobranza" type="text" value=' + detalle[i]['gestion_cobranza'] + '></td></tr>';
	        }
        }
        
    } else {
    	$('#total_mora').val('');
    	$('#total_mora2').html('');
    }

	modal_html +='<input type="button" class="button_verde" id="modificar_mora" value="Modificar"/>';
	modal_html += '</div>';
	$('#contenido_modal').append(modal_html);
	$(".interes").mask('###.###.###',{reverse: true});
	detalle_interes = generarDetalleJSON();			
	$("#detalle").val(detalle_interes);	
	$('#modificar_mora').click(function() {
		this.style.backgroundColor = '#66A385';
		$(".interes").unmask();
		modificarMontos();
		$('.close').trigger("click");
		//return true;
	});
}


function modificarMontos(){
	var intereses =0;
	global_intereses =0;
	var gestion_cobranza = 0;
	if(detalle.length > 0)
	{
		var nro_cuotas_a_pagar=$('#nro_cuotas_a_pagar').val();
		for(i=0;i<detalle.length;i++){
			if (detalle[i]['tipo']=='normal'){
				detalle[i]['intereses']= parseInt($('#interes_' + i).val());
				intereses+=detalle[i]['intereses'];
			} else{
				detalle[i]['gestion_cobranza'] = parseInt($('#id_gestion_cobranza').val());
				gestion_cobranza = detalle[i]['gestion_cobranza'];
			}
			
		}
        
	}
	detalle_interes = generarDetalleJSON();			
	$("#detalle").val(detalle_interes);
	global_intereses=intereses+gestion_cobranza;
	//calculateTotalCuotas();
	calculateTotalPago();
}
function retrieveCliente() { 
	if ($("#id_cliente").val().toString().length > 0) {
		// Hacemos un request POST AJAX para obtener los datos del cliente ingresado.
		var request = $.ajax({
			type : "GET",
			
			url : base_context + "/datos/2/",
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
			url : base_context + "/datos/3/",
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
			url : base_context + "/datos/4/",
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
			url : base_context + "/datos/5/",
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
    var gestion_cobranza = $("#id_gestion_cobranza").val();
    if(gestion_cobranza==null){
        gestion_cobranza=0;
    }
	//var total_mora=global_intereses+parseInt(gestion_cobranza);
	var total_mora=global_intereses;
	var total_pago = parseInt( total_cuotas) + parseInt( total_mora);
	total_cuotas = parseInt(total_cuotas);
	$("#total_mora").val(total_mora);
	$("#total_mora2").html(String(total_mora));
	$("#total_mora2").html(String(format.call($("#total_mora2").html().split(' ').join(''),'.',',')));
	if(cancelado){
		$("#total_mora2").html(0);
	}

	total_pago = parseInt(total_pago);
	$("#total_pago").val(total_pago);
	$("#total_pago2").html(String(total_pago));
	$("#total_pago2").html(String(format.call($("#total_pago2").html().split(' ').join(''),'.',',')));
	if(cancelado){
		$("#total_pago2").html(0);
	}
	$("#guardar_pago").removeAttr("disabled");
}

function calculateMesPago() {
	var request = $.ajax({
			type : "GET",
			url : base_context + "/ajax/get_mes_pagado_by_id_lote/",
			data : {
				lote_id : lote_id,
				cant_cuotas : $("#nro_cuotas_a_pagar").val()
			},
			dataType : "json"
		});
		// Actualizamos el formulario con los datos obtenidos del lote.
		request.done(function(msg) {
			$("#id_cuota_pagar").empty();
			//$("#id_gestion_cobranza").val(null);
			$("#id_cuota_pagar").append('<tr><th>Nro Cuota</th><th>Fecha Vencimiento</th><th>Monto Cuota</th></tr>');
			addRow(msg);
		});
}

function addRow(msg){
	cancelado = false;
	total_cuotas=0;
	 var table = document.getElementById("id_cuota_pagar");
	 for(i =0; i < msg.cuotas_a_pagar.length; i++){
        if(msg.cuotas_a_pagar[i].pago_cancelado){
            alert("Error: ya se pagaron todas las cuotas correspondientes a este lote.");
			cancelado = true;
            $('input[type="submit"]').attr('disabled','disabled');

        }
        else if (msg.cuotas_a_pagar[i].contado){
            alert("Error: no se pueden ingresar pagos porque este lote fue vendido al contado.");
			cancelado = true;
            $('input[type="submit"]').attr('disabled','disabled');
        }
        else{
            $('input[type="submit"]').removeAttr('disabled');
            $("#id_cuota_pagar").append('<tr><td style="text-align: center;">' +msg.cuotas_a_pagar[i].nro_cuota+ '</td><td style="text-align: center;">' + msg.cuotas_a_pagar[i].fecha+'</td><td style="text-align: center;">' + ponerPuntos(msg.cuotas_a_pagar[i].monto_cuota)+ '</td></tr>');
            total_cuotas += msg.cuotas_a_pagar[i].monto_cuota;
        }

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

function getCurrentDate2(){
	$.ajax({
    	dataType: 'jsonp',
    	// url: 'http://www.timeapi.org/utc/now.json',
		//reemplazamos el UTC por nuestra zona horaria
    	url: 'https://www.timeapi.org/-4/now.json',
    	success: function (result) {
		    $('.fecha_pago').val(formatearFechaInternacional(result.dateString));
    	}
	});
}

function formatearFechaInternacional(fecha){
	//recibimos un string separado por comas, vamos a construir en nuestro formato
	// mes = fecha.dateString.substr(0,fecha.indexOf(' '));
	var today = new Date(fecha);
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

function generarDetalleJSON(){
		detalle_json = '';
		objeto = {};
		var nro_cuotas_a_pagar = $('#nro_cuotas_a_pagar').val();
		size=detalle.length;
		if (detalle.length > 0) {
			for (i = 0; i < size; i++) {
				if (detalle[i]['tipo']=='normal'){
					nro_cuota=detalle[i]['nro_cuota'];
					intereses=detalle[i]['intereses'];
					key= 'item' + i;
					value = {nro_cuota : nro_cuota, intereses : intereses};
					objeto[key] = value; 			
					JSON.stringify(objeto);
				} else {
					key= 'item' + i;
					value = {gestion_cobranza :detalle[detalle.length-1]['gestion_cobranza']};
					objeto[key] = value;
					JSON.stringify(objeto);
				}

			}
			
			detalle_json = JSON.stringify(objeto);
			return detalle_json;
		}
}

function ponerPuntos(numero){
	$("#poner_puntos").val(numero);
	$("#poner_puntos").mask('###.###.###',{reverse: true});
	numero = $("#poner_puntos").val();
	return numero;
}

function sacarPuntos(numero){
	
	numero =numero.replace(".", "");
	numero =numero.replace(".", "");
	numero =numero.replace(".", "");
	numero =numero.replace(".", "");
	numero =numero.replace(".", "");
	
	return (numero);
}