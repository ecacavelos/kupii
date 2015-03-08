function retrieve_informe_general() {
		if($('#id_tipo_busqueda').val()=='nombre'){
			window.location.href = base_context + "/informes/informe_general_reporte_excel?fecha_ini=" + $('#fecha_ini').val() + "&fecha_fin=" + $('#fecha_fin').val() + "&fraccion_ini=" + $('#id_frac1').val() + "&fraccion_fin=" + $('#id_frac2').val();
		}
		
		if($('#id_tipo_busqueda').val()=='codigo'){
			window.location.href = base_context + "/informes/informe_general_reporte_excel?fecha_ini=" + $('#fecha_ini').val() + "&fecha_fin=" + $('#fecha_fin').val() + "&fraccion_ini=" + $('#id_fraccion_ini').val() + "&fraccion_fin=" + $('#id_fraccion_fin').val();
		}
		
	}

	function validar() {

		if ($('#fraccion_ini').val() == 0 || $('#fraccion_fin').val() == 0 || $('#fraccion_ini').val() == "" || $('#fraccion_fin').val() == "") {
			alert("Debe ingresar un rango de fracciones");
			return;
		}
		$("#frm_busqueda").submit();

	}
	
function setup_inputs() {
	$("#id_tipo_busqueda").change(function() {
		autocompleteFraccion();	
	});
	$("#id_fraccion_ini").change(function() {
		autocompleteFraccion();		
	});
	$("#id_fraccion_fin").change(function() {
		autocompleteFraccion();		
	});
function autocompleteFraccion(){
	$("#id_fraccion_ini").empty();
		$("#id_fraccion_ini").val("");
		$("#id_fraccion_fin").empty();
		$("#id_fraccion_fin").val("");
		if ($("#id_tipo_busqueda").val() == "nombre") {
			var id_fraccion;
			$("#id_busqueda_label").empty();
			base_url = base_context + "/ajax/get_fracciones_by_name/";
			params = "value";
			$("#id_fraccion_ini").autocomplete({
				source : base_url,
				minLength : 1,
				create : function(){
			        $(this).data('ui-autocomplete')._renderItem = function(ul,item){
				    return $('<li>').append('<a>' +item.fields.nombre+'</a>').appendTo(ul);
				    };
		        },
                select : function(event, ui) {
					id_fraccion = ui.item.pk;
					$("#id_frac1").val(id_fraccion);
					//alert(id_fraccion);
				}
			});

			$("#id_busqueda_label").empty();
			base_url = base_context + "/ajax/get_fracciones_by_name/";
			params = "value";
			$("#id_fraccion_fin").autocomplete({
				source : base_url,
				minLength : 1,
				 create : function(){
			        $(this).data('ui-autocomplete')._renderItem = function(ul,item){
				    return $('<li>').append('<a>' +item.fields.nombre+'</a>').appendTo(ul);
				    };
		        },
				select : function(event, ui) {
					id_fraccion = ui.item.pk;
					$("#id_frac2").val(id_fraccion);
					//alert(id_fraccion);
				}
			});
		}else if($("#id_tipo_busqueda").val() == "codigo"){
			var id_fraccion;
			$("#id_busqueda_label").empty();
			base_url = base_context + "/ajax/get_fracciones_by_id/";
			params = "value";
			$("#id_fraccion_ini").autocomplete({
				source : base_url,
				minLength : 1,
				create : function(){
			        $(this).data('ui-autocomplete')._renderItem = function(ul,item){
				    return $('<li>').append('<a>' +item.fields.nombre+'</a>').appendTo(ul);
				    };
		        },
                select : function(event, ui) {
					id_fraccion = ui.item.pk;
					$("#id_frac1").val(id_fraccion);
					//alert(id_fraccion);
				}
			});
			$("#id_busqueda_label").empty();
			base_url = base_context + "/ajax/get_fracciones_by_id/";
			params = "value";
			$("#id_fraccion_fin").autocomplete({
				source : base_url,
				minLength : 1,
				create : function(){
			        $(this).data('ui-autocomplete')._renderItem = function(ul,item){
				    return $('<li>').append('<a>' +item.fields.nombre+'</a>').appendTo(ul);
				    };
		        },
                select : function(event, ui) {
					id_fraccion = ui.item.pk;
					$("#id_frac2").val(id_fraccion);
					//alert(id_fraccion);
				}
			});
		}
}
}