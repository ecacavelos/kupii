	$(document).ready(function() {
		$("#busqueda_label").focus();
		$("#busqueda_label").autocomplete();
		var busqueda_label_text = busqueda_label;

		$("#tipo_busqueda").val(tipo_busqueda);
		// se pone busqueda label mas abajo porque se borra al inicializarse
		$("#busqueda").val(busqueda);
		$("#nombre_frac2_label_value").val(fraccion_segun_estado);
		if(formato_reporte == ""){
			$("#formato-reporte").val("pantalla");
		} else {
			$("#formato-reporte").val(formato_reporte);
		}



		if ($("#tipo_busqueda").val() == "codigo"){
			$("#label_busqueda").html("Codigo Lote:");
			console.log("Por codigo");
			$('#busqueda_label').mask('###/###/####');
			$("#busqueda_label").attr("placeholder", "Ej: 001/001/0001");
			tipo_busqueda=$("#tipo_busqueda").val();
			busqueda_label=$("#busqueda_label").val();			
			busqueda=$("#busqueda").val();
			$("#busqueda_label").autocomplete("destroy");
			autocompleteLotePorCodigoParalot(tipo_busqueda, busqueda_label, busqueda);
		}
		if($("#tipo_busqueda").val() == "nombre"){
			$("#label_busqueda").html("Nombre de Cliente:");
			console.log("Por nombre cliente");
			$('#busqueda_label').unmask();
			$("#busqueda_label").attr("placeholder", "Ej: Juan Perez");
			tipo_busqueda=$("#tipo_busqueda").val();
			busqueda_label=$("#busqueda_label").val();			
			busqueda=$("#busqueda").val();
			$("#busqueda_label").autocomplete("destroy");
			autocompleteClientePorNombreOCedula(tipo_busqueda, busqueda_label, busqueda);
		}
		if($("#tipo_busqueda").val() == "cedula"){
			$("#label_busqueda").html("Cedula de Cliente:");
			console.log("Por cedula cliente");
			$('#busqueda_label').unmask();
			$("#busqueda_label").attr("placeholder", "Ej: 3497322");
			tipo_busqueda=$("#tipo_busqueda").val();
			busqueda_label=$("#busqueda_label").val();			
			busqueda=$("#busqueda").val();
			$("#busqueda_label").autocomplete("destroy");
			autocompleteClientePorNombreOCedula(tipo_busqueda, busqueda_label, busqueda);
		}
		
		
		//autocomplete para concepto factura
		var id_concepto;
		$("#id_concepto_factura").empty();
		base_url= base_context + "/ajax/get_concepto_factura_by_name/";
		params="value";
		$("#id_nombre_concepto").autocomplete({
			source : base_url,
			minLenght : 1,
			select : function(event, ui) {
				id_concepto = ui.item.id;
				name_concepto= ui.item.descripcion;
				ui.item.value = ui.item.descripcion;
				$("#id_nombre_concepto").val(name_concepto);
				$("#id_concepto_factura").val(id_concepto);			
			}
		});
		
		$("#tipo_busqueda").change(function(){
			if ($("#tipo_busqueda").val() == "codigo"){
                $("#busqueda_label").val('');
                $("#busqueda").val('');
   			    $('#estado_lote_label').hide();
    		    $('#estado_lote_label_value').hide();
			    $('#nombre_frac2').hide();
    		    $('#nombre_frac2_label_value').hide();
				$("#label_busqueda").html("Codigo Lote:");
				console.log("Por codigo");
				$('#busqueda_label').mask('###/###/####');
				$("#busqueda_label").attr("placeholder", "Ej: 001/001/0001");
				tipo_busqueda=$("#tipo_busqueda").val();
				busqueda_label=$("#busqueda_label").val();			
				busqueda=$("#busqueda").val();
				$("#busqueda_label").autocomplete("destroy");
				autocompleteLotePorCodigoParalot(tipo_busqueda, busqueda_label, busqueda);
			}
			if($("#tipo_busqueda").val() == "nombre"){
                $("#busqueda_label").val('');
                $("#busqueda").val('');
   			    $('#estado_lote_label').hide();
    		    $('#estado_lote_label_value').hide();
			    $('#nombre_frac2').hide();
    		    $('#nombre_frac2_label_value').hide();
				$("#label_busqueda").html("Nombre de Cliente:");
				console.log("Por nombre cliente");
				$('#busqueda_label').unmask();
				$("#busqueda_label").attr("placeholder", "Ej: Juan Perez");
				tipo_busqueda=$("#tipo_busqueda").val();
				busqueda_label=$("#busqueda_label").val();			
				busqueda=$("#busqueda").val();
			    $("#busqueda_label").autocomplete("destroy");
				autocompleteClientePorNombreOCedula(tipo_busqueda, busqueda_label, busqueda);
			}
			if($("#tipo_busqueda").val() == "cedula"){
                $("#busqueda_label").val('');
                $("#busqueda").val('');
   			    $('#estado_lote_label').hide();
    		    $('#estado_lote_label_value').hide();
				$('#nombre_frac2').hide();
    		    $('#nombre_frac2_label_value').hide();
				$("#label_busqueda").html("Cedula de Cliente:");
				console.log("Por cedula cliente");
				$('#busqueda_label').unmask();
				$("#busqueda_label").attr("placeholder", "Ej: 3497322");
				tipo_busqueda=$("#tipo_busqueda").val();
				busqueda_label=$("#busqueda_label").val();			
				busqueda=$("#busqueda").val();
				$("#busqueda_label").autocomplete("destroy");
				autocompleteClientePorNombreOCedula(tipo_busqueda, busqueda_label, busqueda);
			}
			if($("#tipo_busqueda").val() == "nombre_fraccion"){
                $("#busqueda_label").val('');
                $("#busqueda").val('');
  			    $('#estado_lote_label').hide();
    		    $('#estado_lote_label_value').hide();
			    $('#nombre_frac2').hide();
    		    $('#nombre_frac2_label_value').hide();
				$("#label_busqueda").html("Nombre de Fraccion:");
				console.log("Por nombre de fraccion");
				$('#busqueda_label').unmask();
				$("#busqueda_label").attr("placeholder", "Ej: El Manantial");
				tipo_busqueda=$("#tipo_busqueda").val();
				busqueda_label=$("#busqueda_label").val();
				busqueda=$("#busqueda").val();
				$("#busqueda_label").autocomplete("destroy");
				autocompleteFraccionPorNombreOId(tipo_busqueda, busqueda_label, busqueda);
			}
			if($("#tipo_busqueda").val() == "estado"){
				$("#label_busqueda").html("Estado del Lote:");
				console.log("Por estado del lote");
				$('#busqueda_label').unmask();
// {#                $("#busqueda_label").attr("placeholder", "Ej: 1");#}
                $("#busqueda_label").val($('#estado_lote').val());
                //los otros se completa este campo con el autocomplete, este le seteamos al momento
                $("#busqueda").val($('#estado_lote').val());
			    $('#estado_lote_label').show();
    		    $('#estado_lote_label_value').show();
			    $('#nombre_frac2').show();
    		    $("#nombre_frac2_label_value").show();
				$("#nombre_frac2_label_value").attr("placeholder", "Ej: El Manantial");
				tipo_busqueda=$("#tipo_busqueda").val();
				busqueda_label=$("#busqueda_label").val();
				busqueda=$("#busqueda").val();
				$("#busqueda_label").autocomplete("destroy");
				autocompleteFraccionPorNombre(tipo_busqueda, busqueda_label, busqueda);
			}


		});
		
		
		$(document).on('change','#estado_lote_label_value',function(){
			$("#busqueda_label").val($('#estado_lote').val());
			//los otros se completa este campo con el autocomplete, este le seteamos al momento
			$("#busqueda").val($('#estado_lote').val());
		});
		$("#busqueda_label").val(busqueda_label_text);
	});
	
function autocompleteFraccionPorNombre(tipo_busqueda, busqueda_label, busqueda){
	$("#nombre_frac2_label_value").val("");
	var id_fraccion;
	$("#nombre_frac2_label_value").empty();
	base_url = base_context + "/ajax/get_fracciones_by_name/";
	params = "value";
	$("#nombre_frac2_label_value").autocomplete({
		source : base_url,
		minLength : 1,
		select : function(event, ui) {
			id_fraccion = ui.item.id;
			$("#nombre_frac2_label_value").val(id_fraccion);
		}
	});
}
	
function buscar() {
		if ($("#busqueda_label").val() == "" && $("#busqueda").val() == "" ) {
			alert("Debe seleccionar una busqueda.");
		} else {
			$("#frm_busqueda").submit();
		}
}
	
	function listar_lotes_reservados() {
		$("#frm_busqueda").submit();
		
}
	
	function descargar_excel(){
		$("#formato-reporte").val("excel");
		$("#frm_busqueda").submit();
	}


