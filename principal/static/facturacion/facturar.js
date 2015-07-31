	var total_exentas = 0;
	var total_iva_10 = 0;
	var total_iva_5 = 0;
	var detalle_valido = true;
	item_detalle_factura = '<div class="item-detalle">'
			+ '<input type="text" class= "cantidad-item item" placeholder="Cantidad" size="2" value="">'
			+ '<input type="text" class="concepto-factura item" placeholder="Concepto">'
			+ '<input type="text" class= "precio_unitario-item item" placeholder="Precio unitario">'
			+ '<input type="text" class= "exentas-item item" placeholder="Exentas">'
			+ '<input type="text" class= "iva_5-item item" placeholder="IVA 5%">'
			+ '<input type="text" class= "iva_10-item item" placeholder="IVA 10%">'
			+ '<a href="#" class="add-btn">+</a>'
		    + '</div>';
		item_inicial_detalle_factura = '<div class="item-detalle">'
			+ '<input type="text" class= "cantidad-item item" placeholder="Cantidad" size="2" value="">'
			+ '<input type="text" class="concepto-factura item" placeholder="Concepto">'
			+ '<input type="text" class= "precio_unitario-item item" placeholder="Precio unitario">'
			+ '<input type="text" class= "exentas-item item" placeholder="Exentas">'
			+ '<input type="text" class= "iva_5-item item" placeholder="IVA 5%">'
			+ '<input type="text" class= "iva_10-item item" placeholder="IVA 10%">'
			+ '<a href="#" class="add-btn">+</a>'
		    + '</div>';
	$(document).ready(function() {
		$('#lote').mask('###/###/####');
		$("#id_name_cliente").focus();
		// 1. Se setea el autocomplete para buscar clientes
		autocompleteClienteRucONombre('id_name_cliente', 'id_cedula_cliente', 'id_cliente');
		autocompleteTimbradoPorNumero('timbrado', 'id-timbrado');
		
		// 2. Se agrega el primer item (al menos debe existir 1).
		$('.detalle_factura').append(item_inicial_detalle_factura);
		
		// 3. Para agregar un item.		
		// $('.add-btn').click(function(){
			// $('.detalle_factura').append(item_detalle_factura);
		// });		
		$('.detalle_factura').on("click",".add-btn", function(e){ 
        	e.preventDefault();         
        	$('.detalle_factura').append(item_detalle_factura); 
        	$(this).attr('class', 'rm-btn');
        	$(this).html('-');
    	});
		
		//4. Para eliminar un item.
		$('.detalle_factura').on("click",".rm-btn", function(e){ 
        	e.preventDefault();         
        	$(this).parent('div').remove(); 
    	});
    	
    	// 5. Control de validez del detalle
    	$('.detalle_factura').on("blur",".item", function(e){ 
        	e.preventDefault();         
        	validarDetalle();
    	});
    	
    	$('#id_nro_cuota').autocomplete({
			source: function(request, response) {
				$.getJSON("/ajax/get_pago_cuotas_by_lote_cliente/", 
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
	    		return false;
			}
		});
		
		$('#id_nro_cuota_hasta').autocomplete({
			source: function(request, response) {
				$.getJSON("/ajax/get_pago_cuotas_by_lote_cliente/", 
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
	    		return false;
			}
		});
		$('#id_nro_cuota_hasta').blur(function(){
			if($("#id_nro_cuota_hasta").val() != '' && $('#id_nro_cuota').val() != ''){
				var request = $.ajax({
					type : "GET",
					url : "/ajax/get_detalles_factura/",
					data : {
						lote_id: $("#lote").val(),
						cliente_id: $("#id_cedula_cliente").val(),
						nro_cuota_desde: $("#id_nro_cuota").val(),
						nro_cuota_hasta: $("#id_nro_cuota_hasta").val()
					},
					dataType : "json"
				});
				// Actualizamos el detalle de la factura
				request.done(function(msg) {
					index = $('.item-detalle').length;
					var inputs= $('.item-detalle')[index -1].children
					inputs[0].value=msg[0].cantidad;
					inputs[1].value="Cuota Nro: "  + $("#id_nro_cuota").val() + " a " + $("#id_nro_cuota_hasta").val();
					inputs[2].value=msg[0].precio_unitario;
					inputs[3].value=msg[0].exentas;
					inputs[4].value=msg[0].iva5;
					inputs[5].value="0";
					validarDetalle();
				});
			}
		});
		//traer datos para los detalles de la factura
		
    	// Control del SUBMIT del FORM
    	$("#agregar-factura-form").submit(function(){
			
			//1. TODO: Hacer chequeo de que todos los valores esten correctos. 
			if (formOk()){
				//2. Obtener el JSON del detalle
				detalle = generarDetalleJSON();			
				$("#detalle").val(detalle);										
				return true;		    						
			}
			else{
				return false;
			}
    	});
	});
	
	function generarDetalleJSON(){
		detalle_json = '';
		objeto = {};
		$(".item-detalle").each(function(index, element ){
			// Agregamos el elemento mas externo
			i = index + 1;			
			//Se obtienen los datos.
			cantidad = $(this).find(".cantidad-item").val();
			concepto = $(this).find(".concepto-factura").val();
			precio_unitario = $(this).find(".precio_unitario-item").val();
			exentas = $(this).find(".exentas-item").val();
			iva_10 = $(this).find(".iva_10-item").val();
			iva_5 = $(this).find(".iva_5-item").val();
			
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
		
			cantidad = $(this).find(".cantidad-item").val();
			cantidad = parseInt(cantidad) || 0;
			concepto = $(this).find(".concepto-factura").val();
			precio_unitario = $(this).find(".precio_unitario-item").val();
			precio_unitario = parseInt(precio_unitario) || 0;
			exentas = $(this).find(".exentas-item").val();
			exentas = parseInt(exentas) || 0;
			iva_10 = $(this).find(".iva_10-item").val();
			iva_10 = parseInt(iva_10) || 0;
			iva_5 = $(this).find(".iva_5-item").val();
			iva_5 = parseInt(iva_5) || 0;
			total_exentas += exentas;
			total_iva_10 += iva_10;
			total_iva_5 += iva_5;			
			indicador_validez = '#840A0A'; // Por defecto invalido (Rojo)
			
			// Requerimieno minimo para un detalle valido
			if (cantidad != 0  && precio_unitario != 0 && (exentas !=0 || iva_10 != 0 || iva_5 !=0)){
				if (cantidad*precio_unitario == (exentas+iva_10+iva_5)){
					// VALIDO
					console.log('Detalle VALIDO');
					indicador_validez = '#1C842D';
				}
				else{
					detalle_valido = false;
				}		
			}
			else{
				detalle_valido = false;
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
		total = total_iva_5 + total_iva_10 + exentas;
		$('#total').val( total.toString());
		iva_10 = (Math.round(total_iva_10/11));
		$('#liquidacion-iva_10').val(iva_10.toString());
		iva_5 = (Math.round(total_iva_5/11));
		$('#liquidacion-iva_5').val(iva_5.toString());
		$('#liquidacion-iva').val((iva_5 + iva_10).toString());		
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
