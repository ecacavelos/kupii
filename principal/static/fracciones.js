$(document).ready(function() {
		$("#id_fecha_aprobacion").datepicker({ dateFormat: 'dd/mm/yy' });
		$('.date').mask('##/##/####');
		$( "#boton_cantidad_lotes" ).hide();
		$( ".grid_6" ).hide();
		$("#id_id").focus();

		var propietario_id;
		$("#id_name_propietario").empty();
		base_url = base_context + "/ajax/get_propietario_id_by_name/";
		params = "value";
		$("#id_name_propietario").autocomplete({
			source : base_url,
			minLength : 1,
			select : function(event, ui) {
				id_propietario = ui.item.id;
				cedula_propietario= ui.item.cedula;
				$("#id_propietario").val(id_propietario);
				$("#id_cedula_propietario").val(cedula_propietario);

			}
		});
		
		//autocomplete para cedula
		var propietario_id;
		$("#id_cedula_propietario").empty();

		base_url = base_context + "/ajax/get_propietario_name_id_by_cedula/";
		params = "value";
		$("#id_cedula_propietario").autocomplete({
			source : base_url,
			minLength : 1,
			select : function(event, ui) {
				id_propietario = ui.item.id;
				name_propietario= ui.item.label;
				cedula_propietario= ui.item.cedula;
				ui.item.value = ui.item.cedula;
				$("#id_propietario").val(id_propietario);
				$("#id_name_propietario").val(name_propietario);
				$("#id_cedula_propietario").val(cedula_propietario);
				
			}
		});
		
	});
	function crear_form(){
		var cantidad_manzanas = parseInt($("#id_cantidad_manzanas").val());
		for (i=1;i<cantidad_manzanas+1;i++){
			if (i == cantidad_manzanas){
				$("#manzanas").val($("#manzanas").val()+i);
			}else{
				$("#manzanas").val($("#manzanas").val()+i+",");
			}
				
		}
		
	}
	

	function validar_id_propietario() {
		if ($('#id_propietario').val() == '' || $('#id_propietario').val() == null) {
			var request_propietario_id = $.ajax({
				url : '/ajax/get_propietario_lastId/',
				type : "GET",
				success : function(data) {
					$.each(data, function(index, value) {
						$("#id_propietario").val(value.id);
						var res = $("#id_superficie_total").val();
						//var res ="";
						for ( i = 0; i < res.length; i++) {
							res = res.replace(".", "");
						}
						res = res.replace(",", ".");
						//console.log("\n"+str);
						//console.log("\n"+res);
						$("#id_superficie_total").val(res);
						var dateTypeVar = $('#id_fecha_aprobacion').datepicker('getDate');
						$("#id_fecha_aprobacion").val($.datepicker.formatDate('yy-mm-dd', dateTypeVar));
						//$("#id_cantidad_lotes").prop('disabled', false);
						$("#id_cantidad_lotes").removeAttr('disabled');
						$("#form_add_fraccion").submit();
					});
				}
			});
		} else {
			var res = $("#id_superficie_total").val();
			//var res ="";
			for ( i = 0; i < res.length; i++) {
				res = res.replace(".", "");
			}
			res = res.replace(",", ".");
			//console.log("\n"+str);
			//console.log("\n"+res);
			$("#id_superficie_total").val(res);
			var dateTypeVar = $('#id_fecha_aprobacion').datepicker('getDate');
			$("#id_fecha_aprobacion").val($.datepicker.formatDate('yy-mm-dd', dateTypeVar));
			$("#id_cantidad_lotes").prop('disabled', false);
			$("#form_add_fraccion").submit();
		}
	}

	function activar_boton(){
		solo_numeros();
	if ($("#id_cantidad_manzanas").val() == "" || $("#id_cantidad_manzanas").val() == null || $("#id_cantidad_manzanas").val() == "0"){
		$( "#boton_cantidad_lotes" ).hide();
		$("#id_cantidad_manzanas").val("");
	}else{
		$( "#boton_cantidad_lotes" ).show();
	}  	
		
	}
	
	function solo_numeros () {
		
	  	$('#id_cantidad_manzanas').val($('#id_cantidad_manzanas').val().replace(/\D/g,''));
	}
	
	function solo_numeros () {
		
	  	$('#id_cedula_propietario').val($('#id_cedula_propietario').val().replace(/\D/g,''));
	}
	
	function solo_numeros_comas_puntos () {
		
	  	$('#id_superficie_total').val($('#id_superficie_total').val().replace(/[^\d,.]+/g, ''));
	}
	
	

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
		//} else {
		//	numeric = numeric.substr(0,numeric.length-1);
		//}
		
		return numeric + decimal;
	}

	/*
	 $('#id_superficie_total').on('keyup', function(){
	 $(this).val(format.call($(this).val().split(' ').join(''),' ','.'));
	 solo_numeros_comas();
	 });
	 */