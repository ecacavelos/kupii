function validar() {
	if ($('#fraccion_ini').val() == 0 || $('#fraccion_fin').val() == 0 || $('#fraccion_ini').val() == "" || $('#fraccion_fin').val() == "") {
		alert("Debe ingresar un rango de fracciones");
		return;
	}
	$("#frm_busqueda").submit();
}

function retrieve_lotes_libres() {

	$("#formato_reporte").val("excel");
	$("#frm_busqueda").submit();
}

function setup_inputs() {

	$("#id_tipo_busqueda").change(function() {

		autocompleteFraccion();
		$("#id_fraccion_ini").empty();
		$("#id_fraccion_ini").val("");
		$("#id_fraccion_fin").empty();
		$("#id_fraccion_fin").val("");

	});

	$("#id_fraccion_ini").change(function() {
		autocompleteFraccion();		
	});

	$("#id_fraccion_fin").change(function() {
		autocompleteFraccion();		
	});
}


function autocompleteFraccion(){
		//$("#id_fraccion_ini").empty();
		//$("#id_fraccion_ini").val("");
		//$("#id_fraccion_fin").empty();
		//$("#id_fraccion_fin").val("");
		if ($("#id_tipo_busqueda").val() == "nombre") {
			var id_fraccion;
			$("#id_busqueda_label").empty();
			base_url = base_context + "/ajax/get_fracciones_by_name/";
			params = "value";
			$("#id_fraccion_ini").autocomplete({
				source : base_url,
				minLength : 1,
                select : function(event, ui) {
					id_fraccion = ui.item.id;
					$("#id_frac1").val(id_fraccion);
					$("#id_fraccion_ini").val(ui.item.label);
					
					//alert(id_fraccion);
				}
			});
			$("#id_busqueda_label").empty();
			base_url = base_context + "/ajax/get_fracciones_by_name/";
			params = "value";
			$("#id_fraccion_fin").autocomplete({
				source : base_url,
				minLength : 1,
				select : function(event, ui) {
					id_fraccion = ui.item.id;
					$("#id_frac2").val(id_fraccion);
					$("#id_fraccion_fin").val(ui.item.label);					
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
                select : function(event, ui) {
                	event.preventDefault();
					id_fraccion = ui.item.id;
					$("#id_frac1").val(id_fraccion);
					$("#id_fraccion_ini").val(ui.item.id);
					//alert(id_fraccion);
				}
			});
			$("#id_busqueda_label").empty();
			base_url = base_context + "/ajax/get_fracciones_by_id/";
			params = "value";
			$("#id_fraccion_fin").autocomplete({
				source : base_url,
				minLength : 1,
                select : function(event, ui) {
                	event.preventDefault();
					id_fraccion = ui.item.id;
					$("#id_frac2").val(id_fraccion);
					$("#id_fraccion_fin").val(ui.item.id);
					//alert(id_fraccion);
				}
			});
		}		 
}


$(document).ready(function() {


    // Cuando se selecciona una nueva sucursal
    $("#select_sucursal").change(function(){

        $("#fracciones_por_sucursal").empty();

        obtener_fracciones_de_sucursal();

    });

    // Aca deschequeamos las fracciones que estan excluidas en el filtro que se seteo.
    fracciones_excluidas_en_filtro_array = JSON.parse(fracciones_excluidas_json)
    carga_inicial_de_fracciones_segun_filtros();


});

function obtener_fracciones_de_sucursal() {

            // Obtenemos por medio de un AJAX la lista de fracciones de una sucursal
		var request = $.ajax({
			type : "GET",
			url : "/ajax/get_fracciones_by_sucursal/",
			data : {
				sucursal : $('#select_sucursal').val(),
			},
			dataType : "json"
		});

		// Actualizamos la lista de fracciones a mostrar
		request.done(function(msg) {

            for (var i = 0; i < msg.length; i++) {
                $("#fracciones_por_sucursal").append('<tr> <td> <input type="checkbox" class="checkbox_fraccion_sucursal" value="'+ msg[i].id +'"> <span class="label_nombre_fraccion" >' + msg[i].nombre + '</span> </td> </tr>');

            }

            $(".checkbox_fraccion_sucursal").change(function () {

                $("#fracciones_excluir").empty();

                $(".checkbox_fraccion_sucursal:not(:checked)").each(function(){

                    $('<input>').attr({
                        type: 'hidden',
                        value: $(this).val(),
                        name: 'fracciones_excluir'
                    }).appendTo('#fracciones_excluir');
                });
            });

		});

		// En caso de no poder obtener los datos, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			alert('Ocurrio un error al obtener la fracciones de la sucursal');
		});
}

function carga_inicial_de_fracciones_segun_filtros(){


        // Obtenemos por medio de un AJAX la lista de fracciones de una sucursal
		var request = $.ajax({
			type : "GET",
			url : "/ajax/get_fracciones_by_sucursal/",
			data : {
				sucursal : $('#select_sucursal').val(),
			},
			dataType : "json"
		});

		// Actualizamos la lista de fracciones a mostrar
		request.done(function(msg) {

            for (var i = 0; i < msg.length; i++) {
                $("#fracciones_por_sucursal").append('<tr> <td> <input type="checkbox" class="checkbox_fraccion_sucursal" value="'+ msg[i].id +'" checked> <span class="label_nombre_fraccion" >' + msg[i].nombre + '</span> </td> </tr>');

            }

            $(".checkbox_fraccion_sucursal").each(function(){
                for (i = 0 ; i < fracciones_excluidas_en_filtro_array.length ; i++){
                    if ($(this).val() == fracciones_excluidas_en_filtro_array[i]){
                        $(this).prop('checked', false);
                    }
                }
            });

            $(".checkbox_fraccion_sucursal").change(function () {

                $("#fracciones_excluir").empty();

                $(".checkbox_fraccion_sucursal:not(:checked)").each(function(){

                    $('<input>').attr({
                        type: 'hidden',
                        value: $(this).val(),
                        name: 'fracciones_excluir'
                    }).appendTo('#fracciones_excluir');
                });
            });

		});

		// En caso de no poder obtener los datos, indicamos el error.
		request.fail(function(jqXHR, textStatus) {
			alert('Ocurrio un error al obtener la fracciones de la sucursal');
		});

}
