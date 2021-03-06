	var pdf = "";
	var total_exentas = 0;
	var total_iva_10 = 0;
	var total_iva_5 = 0;
	var detalle_valido = true;
	var cantidad_detalles = 1;
	
		item_inicial_detalle_factura = '<div class="item-detalle">'
			+ '<input type="number" id="id_detalle_cantidad_1" class= "cantidad-item item" placeholder="Cant." size="2" value="" style="width:50px;">'
			+ '<input type="text" id="id_detalle_concepto_1" class="concepto-factura item" placeholder="Concepto">'
			+ '<input type="text" id="id_detalle_precio_unitario_1" class= "precio_unitario-item item" placeholder="Precio unitario">'
			+ '<input type="text" id="id_detalle_exentas_1" class= "exentas-item item" placeholder="Exentas">'
			+ '<input type="text" id="id_detalle_iva5_1" class= "iva_5-item item" placeholder="IVA 5%">'
			+ '<input type="text" id="id_detalle_iva10_1" class= "iva_10-item item" placeholder="IVA 10%">'
			+ '<a href="#" class="add-btn">+</a>'
		    + '</div>';
	$(document).ready(function() {
		$("#imprimir_factura").hide();
		$("#submit-btn").hide();
		$('#lote').mask('###/###/####');
		$('#nro-factura').mask('###-###-#######');
		$("#id_name_cliente").focus();
		
		$("#crear_factura").prop('disabled',true);
		$("#grabar_factura").prop('disabled',true);
		$("#submit-btn").prop('disabled',true);
		
		
		
		//Configuraciones del datepicker
		$("#fecha").datepicker();
		//$("#fecha").datepicker('setDate', new Date());
		//$("#fecha").datepicker({ dateFormat: 'dd/mm/yy' });
		$('#fecha').val(getCurrentDate());
		
		
		//$('#fecha').mask('##/##/####');
		$(function($){
		    $.datepicker.regional['es'] = {
		        closeText: 'Cerrar',
		        prevText: '<Ant',
		        nextText: 'Sig>',
		        currentText: 'Hoy',
		        monthNames: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
		        monthNamesShort: ['Ene','Feb','Mar','Abr', 'May','Jun','Jul','Ago','Sep', 'Oct','Nov','Dic'],
		        dayNames: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
		        dayNamesShort: ['Dom','Lun','Mar','Mié','Juv','Vie','Sáb'],
		        dayNamesMin: ['Do','Lu','Ma','Mi','Ju','Vi','Sá'],
		        weekHeader: 'Sm',
		        dateFormat: 'dd/mm/yy',
		        firstDay: 1,
		        isRTL: false,
		        showMonthAfterYear: false,
		        yearSuffix: ''
		    };
		    $.datepicker.setDefaults($.datepicker.regional['es']);
		});
		
		// 1. Se setea el autocomplete para buscar clientes
		autocompleteClienteRucONombre('id_name_cliente', 'id_cedula_cliente', 'id_cliente');
		autocompleteTimbradoPorNumero('timbrado', 'id-timbrado');
		
				
		$("#id_cedula_cliente").autocomplete({
			source : base_context +"/ajax/get_cliente_name_id_by_cedula/",
			minLength : 1,
			create : function(){
				$(this).data('ui-autocomplete')._renderItem = function(ul,item){
					return $('<li>').append('<a>' +item.cedula+' '+item.nombres+' '+item.apellidos+'</a>').appendTo(ul);
					};
			},
			select : function(event, ui) {
				cliente_id = ui.item.id;
				$("#id_name_cliente").val (ui.item.nombres+" "+ui.item.apellidos);
				$("#id_cedula_cliente").val(ui.item.cedula);
				//name_cliente=ui.item.fields.nombres+" "+ui.item.fields.apellidos;
				//$("#id_name_cliente").val(name_cliente);
				$("#id_cliente").val(cliente_id);
				//$(this).trigger('change'); 
	    		return false; 
			}
		});
		
		$("#anulado").change(function () {
            if ($("#anulado").prop('checked') == true){
                $("#anulado").val(1);
            }else{
                $("#anulado").val(0);
            }
        });
		
		// 2. Se agrega el primer item (al menos debe existir 1).
		$('.detalle_factura').append(item_inicial_detalle_factura);
		aplicarFuncionesDetalles();
		
		
		// 3. Para agregar un item.		
		// $('.add-btn').click(function(){
			// $('.detalle_factura').append(item_detalle_factura);
		// });		
		$('.detalle_factura').on("click",".add-btn", function(e){ 
        	e.preventDefault();
        	
        	cantidad_detalles++;
        	
        	item_detalle_factura = '<div class="item-detalle">'
			+ '<input type="number" id="id_detalle_cantidad_'+cantidad_detalles+'" class= "cantidad-item item" placeholder="Cantidad" size="2" value="" style="width:50px;">'
			+ '<input type="text" id="id_detalle_concepto_'+cantidad_detalles+'" class="concepto-factura item" placeholder="Concepto">'
			+ '<input type="text" id="id_detalle_precio_unitario_'+cantidad_detalles+'" class= "precio_unitario-item item" placeholder="Precio unitario">'
			+ '<input type="text" id="id_detalle_exentas_'+cantidad_detalles+'" class= "exentas-item item" placeholder="Exentas">'
			+ '<input type="text" id="id_detalle_iva5_'+cantidad_detalles+'" class= "iva_5-item item" placeholder="IVA 5%">'
			+ '<input type="text" id="id_detalle_iva10_'+cantidad_detalles+'" class= "iva_10-item item" placeholder="IVA 10%">'
			+ '<a href="#" class="rm-btn">-</a>'
		    + '</div>';
        	         
        	$('.detalle_factura').append(item_detalle_factura); 
        	//$(this).attr('class', 'rm-btn');
        	//$(this).html('-');
        	aplicarFuncionesDetalles();
    	});
		
		//4. Para eliminar un item.
		$('.detalle_factura').on("click",".rm-btn", function(e){ 
        	e.preventDefault();
        	cantidad_detalles = cantidad_detalles-1;         
        	$(this).parent('div').remove(); 
    	});
    	
    	// 5. Control de validez del detalle
    	$('.detalle_factura').on("blur",".item", function(e){ 
        	e.preventDefault();         
        	validarDetalle();
    	});
    	
    	$('#id_nro_cuota').autocomplete({
			source: function(request, response) {
				$.getJSON(base_context+"/ajax/get_pago_cuotas_by_lote_cliente/",
				{
					lote_id: $("#lote").val(),
					cliente_id: $("#id_cedula_cliente").val(),
					nombre: request.term
				}, 
					response);
			},
			minLength: 1,
			create : function(){
				$(this).data('ui-autocomplete')._renderItem = function(ul,item){
					return $('<li>').append('<a>' +item.nro_cuota_y_total +'</a>').appendTo(ul);
					};
			},
			select : function(event, ui) {
				nro_cuota= ui.item.nro_cuota_y_total;
				$("#id_nro_cuota").val(nro_cuota);
				$(this).trigger('change');
				index = $('.item-detalle').length -1;
				if(index >1 ){
					$('.item-detalle').remove();
					$('.detalle_factura').append(item_inicial_detalle_factura);
					limpiarLiquidacion();
					$('#id_nro_cuota_hasta').blur();
				} 
	    		return false;
			}
		});
		
		$('#id_nro_cuota_hasta').autocomplete({
			source: function(request, response) {
				$.getJSON(base_context+"/ajax/get_pago_cuotas_by_lote_cliente/",
				{
					lote_id: $("#lote").val(),
					cliente_id: $("#id_cedula_cliente").val(),
					nombre: request.term
				}, 
					response);
			},
			minLength: 1,
			create : function(){
				$(this).data('ui-autocomplete')._renderItem = function(ul,item){
					return $('<li>').append('<a>' +item.nro_cuota_y_total +'</a>').appendTo(ul);
				}; 
			},
			select : function(event, ui) {
				nro_cuota= ui.item.nro_cuota_y_total;
				$("#id_nro_cuota_hasta").val(nro_cuota);
				$(this).trigger('change');
				index = $('.item-detalle').length -1;
				if(index >1 ){
					$('.item-detalle').remove();
					$('.detalle_factura').append(item_inicial_detalle_factura);
					limpiarLiquidacion();
					$('#id_nro_cuota_hasta').blur();
				}else{
					$('#id_nro_cuota_hasta').blur();
				}  
	    		return false;
			}
		});
		
		$('#id_name_cliente').blur(function(){
			validarDetalle();
		});
		
		$('#id_cedula_cliente').blur(function(){
			validarDetalle();
		});
		
		$('#lote').blur(function(){
			validarDetalle();
		});
		
		$('#id_nro_cuota_hasta').blur(function(){
			//index = $('.item-detalle').length -1;
			index = $('.item-detalle').length;
				if(index >1 ){
					$('.item-detalle').remove();
					$('.item-detalle').remove();
					$('.detalle_factura').append(item_inicial_detalle_factura);
					aplicarFuncionesDetalles();
					limpiarLiquidacion();
				}
			if($("#id_nro_cuota_hasta").val() != '' && $('#id_nro_cuota').val() != ''){
				var request = $.ajax({
					type : "GET",
					url : base_context+"/ajax/get_detalles_factura/",
					data : {
						lote_id: $("#lote").val(),
						cliente_id: $("#id_cliente").val(),
						nro_cuota_desde: $("#id_nro_cuota").val(),
						nro_cuota_hasta: $("#id_nro_cuota_hasta").val()
					},
					dataType : "json"
				});
				// Actualizamos el detalle de la factura
				request.done(function(msg) {
					index = $('.item-detalle').length;
					var inputs= $('.item-detalle')[index -1].children;
					inputs[0].value=msg[0].cantidad;
					ultimo = (msg[0].cuotas_detalles).length - 1;
					
					var monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
					fecha_1 = msg[0].cuotas_detalles[0].fecha;
					fecha_2 = msg[0].cuotas_detalles[ultimo].fecha;
					
					var parts_1 = fecha_1.split("/");
					var d1 = new Date(parseInt(parts_1[2], 10), parseInt(parts_1[1], 10) - 1, parseInt(parts_1[0], 10));
					year_1 = parts_1[2];
					
					var parts_2 = fecha_2.split("/");
					var d2 = new Date(parseInt(parts_2[2], 10), parseInt(parts_2[1], 10) - 1, parseInt(parts_2[0], 10));
					year_2 = parts_2[2];
					
					//alert("Los meses son: " + monthNames[d1.getMonth()]+ ", "+monthNames[d2.getMonth()]);
					
					mes_year_1 = monthNames[d1.getMonth()]+"/"+year_1;
					mes_year_2 =  monthNames[d2.getMonth()]+"/"+year_2;
					inputs[2].value="Pago de Cuota: "  + $("#id_nro_cuota").val() + " de "+ mes_year_1+", al " + $("#id_nro_cuota_hasta").val()+ " de "+ mes_year_2;
					inputs[3].value=msg[0].precio_unitario;
					inputs[4].value=msg[0].exentas;
					inputs[5].value=msg[0].iva5;
					inputs[6].value="0";
					aplicarFuncionesDetalles();
					ponerPuntos();
					validarDetalle();
					if (msg.length > 1){
						$('.item-detalle')[0].children[7].click();
			        	index = $('.item-detalle').length;
			        	var inputs= $('.item-detalle')[index -1].children;
						inputs[0].value=msg[1].cantidad;
						inputs[2].value="Interes Moratorio";
						inputs[3].value=msg[1].precio_unitario;
						inputs[4].value=msg[1].exentas;
						inputs[5].value=msg[1].iva5;
						inputs[6].value=msg[1].iva10;
						
						ponerPuntos();
						aplicarFuncionesDetalles();
						validarDetalle();
						if (msg.length == 3){
							$('.item-detalle')[0].children[7].click();
				        	index = $('.item-detalle').length;
				        	var inputs= $('.item-detalle')[index -1].children;
							inputs[0].value=msg[2].cantidad;
							inputs[2].value="Gestion Cobranzas";
							inputs[3].value=msg[2].precio_unitario;
							inputs[4].value=msg[2].exentas;
							inputs[5].value=msg[2].iva5;
							inputs[6].value=msg[2].iva10;
							
							ponerPuntos();
							aplicarFuncionesDetalles();
							validarDetalle();
						}
					}
					
				});
			}
		});
		//traer datos para los detalles de la factura
		
		if (tipo_venta != ''){
			$("#id_detalle_cantidad_1").val("1");
			$("#id_detalle_concepto_1").val(descripcion);
			$("#id_detalle_precio_unitario_1").val(precio_venta);
			
			var iva_5_contado = parseInt( ( (1 * precio_venta) * 31.5) / 101.5);
            var exentas_contado = parseInt( (1 * precio_venta) - iva_5_contado);
            
            //var iva_5_contado = Math.floor( ( (1 * precio_venta) * 31.5) / 101.5);
            //var exentas_contado = Math.floor( (1 * precio_venta) - iva_5_contado);
			
			$("#id_detalle_exentas_1").val(exentas_contado);
			$("#id_detalle_iva5_1").val(iva_5_contado);
			$("#id_detalle_iva10_1").val("0");
			
			ponerPuntos();
			aplicarFuncionesDetalles();
			validarDetalle();
		}
		
    	// Control del SUBMIT del FORM
    	$("#agregar-factura-form").submit(function(){
			
			//1. TODO: Hacer chequeo de que todos los valores esten correctos. 
			if (formOk()){
				//2. Obtener el JSON del detalle
				detalle = generarDetalleJSON();			
				$("#detalle").val(detalle);
				$("#submit-btn").hide();
				$("#crear_factura").hide();
				$("#grabar_factura").hide();
				$("#imprimir_factura").show();
				
				/*
				$('#total-exentas').val( sacarPuntos( $('#total-exentas').val() ) );
				$('#total-iva_10').val( sacarPuntos( $('#total-iva_10').val() ) );
				$('#total-iva_5').val( sacarPuntos( $('#total-iva_5').val() ) );
				$('#total').val( sacarPuntos( $('#total').val() ) );
				$('#liquidacion-iva_10').val( sacarPuntos( $('#liquidacion-iva_10').val() ) );
				$('#liquidacion-iva_5').val( sacarPuntos( $('#liquidacion-iva_5').val() ) );
				$('#liquidacion-iva').val( sacarPuntos( $('#liquidacion-iva').val() ) );
				*/										
				return true;		    						
			}
			else{
				return false;
			}
    	});
    	
    	$("#crear_factura").click(function(){
			$("#crear_factura").hide();
			$("#grabar_factura").hide();
			$("#submit-btn").hide();
			//1. TODO: Hacer chequeo de que todos los valores esten correctos. 
			if (formOk()){
				//2. Obtener el JSON del detalle
				detalle = generarDetalleJSON();			
				$("#detalle").val(detalle);
				
				var request = $.ajax({
					type : "POST",
					url : base_context+"/ajax/facturar/",
					async: false,
					data : {
						csrfmiddlewaretoken : $('input[name=csrfmiddlewaretoken]').val(),
						cliente: $("#id_cliente").val(),
						lote: $("#lote").val(),
						id_timbrado: $("#id-timbrado").val(),
						nro_factura : $("#nro-factura").val(),
						nro_factura_original : $("#nro-factura-original").val(),
						fecha: $("#fecha").val(),
						tipo : $("#tipo").val(),
						detalle: $("#detalle").val(),
						nro_cuota_desde : $("#id_nro_cuota").val(),
						nro_cuota_hasta : $("#id_nro_cuota_hasta").val(),
						observacion: $("#observacion").val(),
						anulado: $("#anulado").val(),
						
					},
					dataType : "json"
				});
				// devuelve el pdf
				request.done(function(msg) {
					$("#imprimir_factura").show();
					$("#id_factura").val(msg.id_factura);
					$("#imprimir_factura").trigger("click");			   
				});
				
    			return true;		    						
			}
			else{
				return false;
			}
    	});

		$("#grabar_factura").click(function(){
			$("#crear_factura").hide();
			$("#grabar_factura").hide();
			$("#submit-btn").hide();
			//1. TODO: Hacer chequeo de que todos los valores esten correctos.
			if (formOk()){
				//2. Obtener el JSON del detalle
				detalle = generarDetalleJSON();
				$("#detalle").val(detalle);

				var request = $.ajax({
					type : "POST",
					url : base_context+"/ajax/facturar/",
					async: false,
					data : {
						csrfmiddlewaretoken : $('input[name=csrfmiddlewaretoken]').val(),
						cliente: $("#id_cliente").val(),
						lote: $("#lote").val(),
						id_timbrado: $("#id-timbrado").val(),
						nro_factura : $("#nro-factura").val(),
						nro_factura_original : $("#nro-factura-original").val(),
						fecha: $("#fecha").val(),
						tipo : $("#tipo").val(),
						detalle: $("#detalle").val(),
						nro_cuota_desde : $("#id_nro_cuota").val(),
						nro_cuota_hasta : $("#id_nro_cuota_hasta").val(),
						observacion: $("#observacion").val(),
						user: $("#user").val(),
						anulado: $("#anulado").val(),
					},
					dataType : "json"
				});
				// devuelve el pdf
				request.done(function(msg) {
					alert("Factura guardada.");
					window.location = base_context + "/facturacion/listado/";
				});
    			return true;
			}
			else{
				return false;
			}
    	});
    	
    	$("#imprimir_factura").click(function(){
    		//el ajax
    		var request = $.ajax({
			type : "POST",
			url : base_context+"/ajax/imprimir_factura/",
			async: false,
			data : {
				csrfmiddlewaretoken : $('input[name=csrfmiddlewaretoken]').val(),
				lote: $("#lote").val(),
				id_factura: $("#id_factura").val(),
				},
					dataType : "aplication/pdf"
				});
				// devuelve el pdf
				// request.done(function(msg) {
				// 	pdf = msg;
				// });
				request.always(function(data) {
					console.log("Enviando json de impresion al print manager")
					// var string_json = JSON.stringify(data);
					var string_json = data.responseText;
					//var string_json = '{"paperType": "A4",  "lineas":  [  {"valor":"valorObjeto1","coord_x": 100,"coord_y": 50},{"valor":"valorObjeto2","coord_x": 200,"coord_y": 100} ]}';
					var url_print = "";
					if(window.location.protocol == "http:"){
						url_print = "http://localhost:8095/TicketService/";
					}else if(window.location.protocol == "https:"){
						url_print = "https://localhost:8443/TicketService/";
					}
					var request_print = $.ajax(
							{
								url: url_print,
								type: 'GET',
								data: {
									json_print_string: string_json,
								}
							});
					request_print.success(function(data2) {
						window.location.href = base_url + redirect;
						console.log(data2);
					});
				});
    	});
    	
    	detalles();
    	
	});
	
	function generarDetalleJSON(){
		detalle_json = '';
		objeto = {};
		$(".item-detalle").each(function(index, element ){
			// Agregamos el elemento mas externo
			i = index + 1;			
			//Se obtienen los datos.
			cantidad = sacarPuntos($(this).find(".cantidad-item").val());
			concepto = $(this).find(".concepto-factura").val();
			precio_unitario = sacarPuntos($(this).find(".precio_unitario-item").val());
			exentas = sacarPuntos($(this).find(".exentas-item").val());
			iva_10 = sacarPuntos($(this).find(".iva_10-item").val());
			iva_5 = sacarPuntos($(this).find(".iva_5-item").val());
			
			key = 'item' + i;
			value = {cantidad : cantidad, concepto : concepto, precio_unitario : precio_unitario, exentas : exentas, iva_10 : iva_10, iva_5 : iva_5 };
			objeto[key] = value; 			
			JSON.stringify(objeto);

		});
		
		detalle_json = JSON.stringify(objeto);
		return detalle_json;
	}
	
	function formOk(){
		// Realizar validaciones.
		if (detalle_valido){
			return true;	
		}
		else {
			alert('Detalle de factura incorrecto, por favor corrija y vuelva a enviar');
		}		
	}
	function validarDetalle(){
		
		console.log('validando');
		total_exentas = 0;
		total_iva_10 = 0 ;
		total_iva_5 = 0;
		detalle_valido = true;
		var len = $('.item-detalle').length;
		$(".item-detalle").each(function(index, element ){
		
			cantidad = sacarPuntos($(this).find(".cantidad-item").val());
			cantidad = parseInt(cantidad) || 0;
			concepto = $(this).find(".concepto-factura").val();
			precio_unitario = sacarPuntos($(this).find(".precio_unitario-item").val());
			precio_unitario = parseInt(precio_unitario) || 0;
			exentas = sacarPuntos($(this).find(".exentas-item").val());
			exentas = parseInt(exentas) || 0;
			iva_10 = sacarPuntos($(this).find(".iva_10-item").val());
			iva_10 = parseInt(iva_10) || 0;
			iva_5 = sacarPuntos($(this).find(".iva_5-item").val());
			iva_5 = parseInt(iva_5) || 0;
			total_exentas += exentas;
			total_iva_10 += iva_10;
			total_iva_5 += iva_5;			
			indicador_validez = '#840A0A'; // Por defecto invalido (Rojo)
			
			// Requerimieno minimo para un detalle valido
			if (cantidad != 0  && precio_unitario != 0 && /*$("#lote").val() != '' && */ $("#id_name_cliente").val() != '' && (exentas !=0 || iva_10 != 0 || iva_5 !=0)){
				if (cantidad*precio_unitario == (exentas+iva_10+iva_5)){
					// VALIDO
					console.log('Detalle VALIDO');
					indicador_validez = '#1C842D';
					$("#crear_factura").prop('disabled',false);
					$("#grabar_factura").prop('disabled',false);
					$("#submit-btn").prop('disabled',false);
				}
				else{
					detalle_valido = false;
					$("#crear_factura").prop('disabled',true);
					$("#grabar_factura").prop('disabled',true);
					$("#submit-btn").prop('disabled',true);
				}		
			}
			else{
				detalle_valido = false;
				$("#crear_factura").prop('disabled',true);
				$("#grabar_factura").prop('disabled',true);
				$("#submit-btn").prop('disabled',true);
			}
			$(this).css('background',indicador_validez);	
		});
		if (detalle_valido){
			liquidar();
		}
		else{
			limpiarLiquidacion();
		}
	}
	function liquidar(){
		
		$('#total-exentas').val(total_exentas.toString());
		$('#total-iva_10').val(total_iva_10.toString());
		$('#total-iva_5').val(total_iva_5.toString());
		total = total_iva_5 + total_iva_10 + total_exentas;
		$('#total').val( total.toString());
		//iva_10 = (Math.round(total_iva_10/11));
		iva_10 = (parseInt(total_iva_10/11));
		$('#liquidacion-iva_10').val(iva_10.toString());
		//iva_5 = (Math.round(total_iva_5/21));
		iva_5 = (parseInt(total_iva_5/21));
		$('#liquidacion-iva_5').val(iva_5.toString());
		$('#liquidacion-iva').val((iva_5 + iva_10).toString());
		
		$('#total-exentas').mask('###.###.###',{reverse: true});
		$('#total-iva_10').mask('###.###.###',{reverse: true});
		$('#total-iva_5').mask('###.###.###',{reverse: true});
		$('#total').mask('###.###.###',{reverse: true});
		$('#liquidacion-iva_10').mask('###.###.###',{reverse: true});
		$('#liquidacion-iva_5').mask('###.###.###',{reverse: true});
		$('#liquidacion-iva').mask('###.###.###',{reverse: true});		
	}
	function limpiarLiquidacion(){
		$('#total-exentas').val('');
		$('#total-iva_10').val('');
		$('#total-iva_5').val('');
		$('#total').val('');
		$('#liquidacion-iva_10').val('');
		$('#liquidacion-iva_5').val('');
		$('#liquidacion-iva').val('');		
	}
	
	function utf8_encode(argString) {
  //  discuss at: http://phpjs.org/functions/utf8_encode/
  // original by: Webtoolkit.info (http://www.webtoolkit.info/)
  //   example 1: utf8_encode('Kevin van Zonneveld');
  //   returns 1: 'Kevin van Zonneveld'

  if (argString === null || typeof argString === 'undefined') {
    return '';
  }

  var string = (argString + ''); // .replace(/\r\n/g, "\n").replace(/\r/g, "\n");
  var utftext = '',
    start, end, stringl = 0;

  start = end = 0;
  stringl = string.length;
  for (var n = 0; n < stringl; n++) {
    var c1 = string.charCodeAt(n);
    var enc = null;

    if (c1 < 128) {
      end++;
    } else if (c1 > 127 && c1 < 2048) {
      enc = String.fromCharCode(
        (c1 >> 6) | 192, (c1 & 63) | 128
      );
    } else if ((c1 & 0xF800) != 0xD800) {
      enc = String.fromCharCode(
        (c1 >> 12) | 224, ((c1 >> 6) & 63) | 128, (c1 & 63) | 128
      );
    } else { // surrogate pairs
      if ((c1 & 0xFC00) != 0xD800) {
        throw new RangeError('Unmatched trail surrogate at ' + n);
      }
      var c2 = string.charCodeAt(++n);
      if ((c2 & 0xFC00) != 0xDC00) {
        throw new RangeError('Unmatched lead surrogate at ' + (n - 1));
      }
      c1 = ((c1 & 0x3FF) << 10) + (c2 & 0x3FF) + 0x10000;
      enc = String.fromCharCode(
        (c1 >> 18) | 240, ((c1 >> 12) & 63) | 128, ((c1 >> 6) & 63) | 128, (c1 & 63) | 128
      );
    }
    if (enc !== null) {
      if (end > start) {
        utftext += string.slice(start, end);
      }
      utftext += enc;
      start = end = n + 1;
    }
  }

  if (end > start) {
    utftext += string.slice(start, stringl);
  }

  return utftext;
}

function utf8_decode(str_data) {
  //  discuss at: http://phpjs.org/functions/utf8_decode/
  // original by: Webtoolkit.info (http://www.webtoolkit.info/)
  //   example 1: utf8_decode('Kevin van Zonneveld');
  //   returns 1: 'Kevin van Zonneveld'

  var tmp_arr = [],
    i = 0,
    ac = 0,
    c1 = 0,
    c2 = 0,
    c3 = 0,
    c4 = 0;

  str_data += '';

  while (i < str_data.length) {
    c1 = str_data.charCodeAt(i);
    if (c1 <= 191) {
      tmp_arr[ac++] = String.fromCharCode(c1);
      i++;
    } else if (c1 <= 223) {
      c2 = str_data.charCodeAt(i + 1);
      tmp_arr[ac++] = String.fromCharCode(((c1 & 31) << 6) | (c2 & 63));
      i += 2;
    } else if (c1 <= 239) {
      // http://en.wikipedia.org/wiki/UTF-8#Codepage_layout
      c2 = str_data.charCodeAt(i + 1);
      c3 = str_data.charCodeAt(i + 2);
      tmp_arr[ac++] = String.fromCharCode(((c1 & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
      i += 3;
    } else {
      c2 = str_data.charCodeAt(i + 1);
      c3 = str_data.charCodeAt(i + 2);
      c4 = str_data.charCodeAt(i + 3);
      c1 = ((c1 & 7) << 18) | ((c2 & 63) << 12) | ((c3 & 63) << 6) | (c4 & 63);
      c1 -= 0x10000;
      tmp_arr[ac++] = String.fromCharCode(0xD800 | ((c1 >> 10) & 0x3FF));
      tmp_arr[ac++] = String.fromCharCode(0xDC00 | (c1 & 0x3FF));
      i += 4;
    }
  }

  return tmp_arr.join('');
}

function detalles(){
	$('#id_nro_cuota_hasta').trigger("blur");
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

function aplicarFuncionesDetalles(){
	//alert("Hola");
	// Autocomplete concepto factura
		$(".concepto-factura").autocomplete({
			source : base_context+"/ajax/get_concepto_factura_by_name/",
			minLength : 1,
			create : function(){
				$(this).data('ui-autocomplete')._renderItem = function(ul,item){
					return $('<li>').append('<a>' +item.descripcion+'</a>').appendTo(ul);
					};
			},
			select : function(event, ui) {
				concepto_id = ui.item.pk;
				//obtengo el id del obejto que activo el evento
                var current_id = event.target.id;
                current_id = current_id.split("_");
                current_id = current_id[3];
				$("#id_detalle_concepto_"+current_id).val (ui.item.descripcion);
				$("#id_detalle_precio_unitario_"+current_id).val(ui.item.precio_unitario);
				//name_cliente=ui.item.fields.nombres+" "+ui.item.fields.apellidos;
				//$("#id_name_cliente").val(name_cliente);
				if (ui.item.exentas){
					$("#id_detalle_exentas_"+current_id).val(0);
					$("#id_detalle_exentas_"+current_id).val(ui.item.precio_unitario*parseInt($("#id_detalle_cantidad_"+current_id).val()));
				} else {
					$("#id_detalle_exentas_"+current_id).val(0);
				}
				if (ui.item.iva5){
					$("#id_detalle_iva5_"+current_id).val(0);
					$("#id_detalle_iva5_"+current_id).val(ui.item.precio_unitario*parseInt($("#id_detalle_cantidad_"+current_id).val()));
				} else {
					$("#id_detalle_iva5_"+current_id).val(0);
				}
				if (ui.item.iva10){
					$("#id_detalle_iva10_"+current_id).val(0);
					$("#id_detalle_iva10_"+current_id).val(ui.item.precio_unitario*parseInt($("#id_detalle_cantidad_"+current_id).val()));
				} else {
					$("#id_detalle_iva10_"+current_id).val(0);
				}	
				//$(this).trigger('change'); 
	    		return false; 
			}
		});
		
		$('.cantidad-item').change(function() {
			//obtengo el id del obejto que activo el evento
                var current_id = this.id;
                current_id = current_id.split("_");
                current_id = current_id[3];
  			if ($("#id_detalle_exentas_"+current_id).val() != 0){
  					$("#id_detalle_exentas_"+current_id).val(0);
					$("#id_detalle_exentas_"+current_id).val(parseInt($("#id_detalle_precio_unitario_"+current_id).val())*parseInt($("#id_detalle_cantidad_"+current_id).val()));
				} else {
					$("#id_detalle_exentas_"+current_id).val(0);
				}
				if ($("#id_detalle_iva5_"+current_id).val() != 0){
					$("#id_detalle_iva5_"+current_id).val(0);
					$("#id_detalle_iva5_"+current_id).val(parseInt($("#id_detalle_precio_unitario_"+current_id).val())*parseInt($("#id_detalle_cantidad_"+current_id).val()));
				} else {
					$("#id_detalle_iva5_"+current_id).val(0);
				}
				if ($("#id_detalle_iva10_"+current_id).val() != 0){
					$("#id_detalle_iva10_"+current_id).val(0);
					$("#id_detalle_iva10_"+current_id).val(parseInt($("#id_detalle_precio_unitario_"+current_id).val())*parseInt($("#id_detalle_cantidad_"+current_id).val()));
				} else {
					$("#id_detalle_iva10_"+current_id).val(0);
				}
		});
		
		
		$('.precio_unitario-item').keyup(function() {
			//obtengo el id del obejto que activo el evento
                var current_id = this.id;
                current_id = current_id.split("_");
                current_id = current_id[4];
  			if ($("#id_detalle_exentas_"+current_id).val() != 0){
  					$("#id_detalle_exentas_"+current_id).val(0);
					$("#id_detalle_exentas_"+current_id).val(parseInt($("#id_detalle_precio_unitario_"+current_id).val())*parseInt($("#id_detalle_cantidad_"+current_id).val()));
				} else {
					$("#id_detalle_exentas_"+current_id).val(0);
				}
				if ($("#id_detalle_iva5_"+current_id).val() != 0){
					$("#id_detalle_iva5_"+current_id).val(0);
					$("#id_detalle_iva5_"+current_id).val(parseInt($("#id_detalle_precio_unitario_"+current_id).val())*parseInt($("#id_detalle_cantidad_"+current_id).val()));
				} else {
					$("#id_detalle_iva5_"+current_id).val(0);
				}
				if ($("#id_detalle_iva10_"+current_id).val() != 0){
					$("#id_detalle_iva10_"+current_id).val(0);
					$("#id_detalle_iva10_"+current_id).val(parseInt(sacarPuntos($("#id_detalle_precio_unitario_"+current_id).val()))*parseInt($("#id_detalle_cantidad_"+current_id).val()));
				} else {
					$("#id_detalle_iva10_"+current_id).val(0);
				}
				
				$("#id_detalle_precio_unitario_"+current_id).mask('###.###.###',{reverse: true});
				$("#id_detalle_exentas_"+current_id).mask('###.###.###',{reverse: true});
				$("#id_detalle_iva5_"+current_id).mask('###.###.###',{reverse: true});
				$("#id_detalle_iva10_"+current_id).mask('###.###.###',{reverse: true});
				validarDetalle();
		});
		
		$("#id_detalle_precio_unitario_1").mask('###.###.###',{reverse: true});
		$("#id_detalle_exentas_1").mask('###.###.###',{reverse: true});
		$("#id_detalle_iva5_1").mask('###.###.###',{reverse: true});
		$("#id_detalle_iva10_1").mask('###.###.###',{reverse: true});
	
}

function sacarPuntos(numero){
	
	numero =numero.replace(".", "");
	numero =numero.replace(".", "");
	numero =numero.replace(".", "");
	numero =numero.replace(".", "");
	numero =numero.replace(".", "");
	
	return (numero);
}

function ponerPuntos(){
	$(".precio_unitario-item").mask('###.###.###',{reverse: true});
	$(".exentas-item").mask('###.###.###',{reverse: true});
	$(".iva_5-item").mask('###.###.###',{reverse: true});
	$(".iva_10-item").mask('###.###.###',{reverse: true});
}
