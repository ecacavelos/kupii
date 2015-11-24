	function buscar() {
		if ($("#tipo_busqueda").val() == "") {
			alert("Debe elegir un tipo de busqueda.");
		} else {
			if ($("#tipo_busqueda").val() == "fecha") {
				if ($("#fecha_desde").val() == "" && $("#fecha_hasta").val() == "" ) {
					alert("Debe ingresar un valor para buscar.");
				} else {
					$("#frm_busqueda").submit();
				}
			} else {
				if ($("#busqueda_label").val() == "") {
					alert("Debe ingresar un valor para buscar.");
				} else {
					$("#frm_busqueda").submit();
				}	
			}
				
			
		}
	}	
	
	function desplegar_campos() {
		$("#fecha_desde").hide();
		$("#fecha_hasta").hide();
		$("#contado").hide();
		$("#label_contado").hide();
		$("#busqueda_label").show();
		$("#fecha_desde").val("");
		$("#fecha_hasta").val("");	
		if ($("#tipo_busqueda").val() == 'fecha') {
			//$('#busqueda_label').val("");
			$('#busqueda_label').unmask('');
			$('#fecha_hasta').val("");
			$("#fecha_desde").datepicker({
				dateFormat : 'dd/mm/yy'
			});
			$('#fecha_desde').mask('##/##/####');
			$("#fecha_hasta").datepicker({
				dateFormat : 'dd/mm/yy'
			});
			$("#fecha_desde").mask('##/##/####');
			$("#fecha_hasta").mask('##/##/####');
			$('#fecha_desde').attr("placeholder","Ej: 01/01/2015");
			$('#fecha_hasta').attr("placeholder","Ej: 01/01/2015");
			$("#fecha_desde").show();
			$("#fecha_hasta").show();
			$("#busqueda_label").hide();
			$("#contado").show();
			$("#label_contado").show();
		}
		if ($("#tipo_busqueda").val() == 'lote') {
			//$('#busqueda_label').val("");
			$("#busqueda_label").datepicker("destroy");
			$("#busqueda_label").removeClass("hasDatepicker");
			$('#busqueda_label').mask('###/###/####');
			$('#busqueda_label').attr("placeholder","Ej: 001/001/0001");
			$("#fecha_desde").hide();
			$("#fecha_hasta").hide();
			$("#contado").hide();
			$("#label_contado").hide();
			$("#busqueda_label").show();
			tipo_busqueda="codigo";
			busqueda_label=$("#busqueda_label").val();			
			busqueda=$("#busqueda").val();	
			autocompleteLotePorCodigoParalot(tipo_busqueda, busqueda_label, busqueda);
		}
		if ($("#tipo_busqueda").val() == 'vendedor') {
			//$("#busqueda_label").val("");
			$('#busqueda_label').unmask('');
			$("#busqueda_label").datepicker("destroy");
			$("#busqueda_label").removeClass("hasDatepicker");
			$("#fecha_desde").hide();
			$("#fecha_hasta").hide();
			$("#busqueda_label").show();
			$('#busqueda_label').attr("placeholder","Ej: Juan Perez");
			$("#contado").show();
			$("#label_contado").show();
			var id_vendedor;
			$("#id_busqueda").empty();
			base_url = base_context + "/ajax/get_vendedor_id_by_name/";
			params = "value";
			$("#busqueda_label").autocomplete({
				source : base_url,
				minLength : 1,
				select : function(event, ui) {
					id_vendedor = ui.item.id;
					$("#id_busqueda").val(id_vendedor);
					//alert(id_vendedor);
					}
				});
		}
		if ($("#tipo_busqueda").val() == 'cliente'){
			//$("#busqueda_label").val("");
			$('#busqueda_label').unmask('');
			$("#busqueda_label").datepicker("destroy");
			$("#busqueda_label").removeClass("hasDatepicker");
			$("#fecha_desde").hide();
			$("#fecha_hasta").hide();
			$("#contado").show();
			$("#label_contado").show();
			$("#busqueda_label").show();
			$('#busqueda_label').attr("placeholder","Ej: Juan Perez");
			var id_cliente;
			$("#id_busqueda").empty();
			base_url = base_context + "/ajax/get_cliente_id_by_name/";
			params = "value";
			$("#busqueda_label").autocomplete({
				source : base_url,
				minLength : 1,
                create : function() {
								$(this).data('ui-autocomplete')._renderItem = function (ul, item){
									return $('<li>')
										.append('<a>'+ item.nombres+" "+item.apellidos+ '</a>')
										.appendTo(ul);
									};
								},
				select : function(event, ui) {
					id_cliente = ui.item.id;
					$("#id_busqueda").val(id_cliente);
					//alert(id_cliente);
					}
				});			
		}
		
		if ($("#tipo_busqueda").val() == 'fraccion'){
			console.log("Por Fraccion");
			//$("#busqueda_label").val("");
			$('#busqueda_label').unmask('');
			$("#busqueda_label").datepicker("destroy");
			$("#busqueda_label").removeClass("hasDatepicker");
			$("#fecha_desde").hide();
			$("#fecha_hasta").hide();
			$("#contado").show();
			$("#label_contado").show();
			$("#busqueda_label").show();
			$('#busqueda_label').attr("placeholder","Ej: Fraccion Prueba");
			var id_cliente;
			$("#id_busqueda").empty();
			base_url = base_context + "/ajax/get_fracciones_by_name/";
			params = "value";
			$("#busqueda_label").autocomplete({
				source : base_url,
				minLength : 1,
                create : function() {
								$(this).data('ui-autocomplete')._renderItem = function (ul, item){
									return $('<li>')
										.append('<a>'+ item.nombre+'</a>')
										.appendTo(ul);
									};
								},
				select : function(event, ui) {
					id_fraccion = ui.item.id;
					$("#id_busqueda").val(id_fraccion);
					//alert(id_cliente);
					}
				});			
		}
	}
	

	
