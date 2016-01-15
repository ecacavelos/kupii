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
		$("#busqueda_label").autocomplete();
		$("#fecha_desde").hide();
		$("#fecha_hasta").hide();
		$("#busqueda_label").show();
		$("#fecha_desde").val("");
		$("#fecha_hasta").val("");	
		if ($("#tipo_busqueda").val() == 'fecha') {
			$('#busqueda_label').val("");
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
		}
		if ($("#tipo_busqueda").val() == 'lote') {
			$('#busqueda_label').val("");
			$("#busqueda_label").datepicker("destroy");
			$("#busqueda_label").removeClass("hasDatepicker");
			$('#busqueda_label').mask('###/###/####');
			$('#busqueda_label').attr("placeholder","Ej: 001/001/0001");
			$("#fecha_desde").hide();
			$("#fecha_hasta").hide();
			$("#busqueda_label").show();
			tipo_busqueda="codigo";
			busqueda_label=$("#busqueda_label").val();			
			busqueda=$("#busqueda").val();
			$("#busqueda_label").autocomplete("destroy");	
			autocompleteLotePorCodigoParalot(tipo_busqueda, busqueda_label, busqueda);
		}
		
		if ($("#tipo_busqueda").val() == 'cliente'){
			$("#busqueda_label").val("");
			$('#busqueda_label').unmask('');
			$("#busqueda_label").datepicker("destroy");
			$("#busqueda_label").removeClass("hasDatepicker");
			$("#fecha_desde").hide();
			$("#fecha_hasta").hide();
			$("#busqueda_label").show();
			$('#busqueda_label').attr("placeholder","Ej: Juan Perez");
			var id_cliente;
			$("#id_busqueda").empty();
			tipo_busqueda = "nombre";
			$("#busqueda_label").autocomplete("destroy");
			autocompleteClientePorNombreOCedula(tipo_busqueda, busqueda_label, busqueda);		
		}
	}

