function retrieve_liquidacion_propietarios() {
    window.location.href = base_context + "/informes/liquidacion_propietarios_reporte_excel?fecha_ini=" + $('#fecha_ini').val() + "&fecha_fin=" + $('#fecha_fin').val() + "&tipo_busqueda=" + $('#id_tipo_busqueda').val() + "&busqueda=" + $('#id_busqueda').val();
}

function calcular_total_a_cobrar(){
	var ley = parseInt(sacarPuntos($("#ley").val()));
	if (isNaN(ley)){
		ley = 0;
	}
	var impuesto_renta = parseInt(sacarPuntos($("#impuesto_renta").val()));
	if (isNaN(impuesto_renta)){
		impuesto_renta= 0;
	}
	var iva_comision = parseInt(sacarPuntos($("#iva_comision").html()));
	if (isNaN(iva_comision)){
		iva_comision = 0;
	}
	var monto_otros_descuentos = parseInt(sacarPuntos($("#monto_otros_descuentos").val()));
	if (isNaN(monto_otros_descuentos)){
		monto_otros_descuentos = 0;
	}
	var total_general_propietario = parseInt(sacarPuntos($("#total_general_propietario").html()));
	
	$("#ley").val(ley);
	$("#impuesto_renta").val(impuesto_renta);
	$("#iva_comision").html(iva_comision);
	$("#monto_otros_descuentos").val(monto_otros_descuentos);
	resta = total_general_propietario-(ley+impuesto_renta+iva_comision+monto_otros_descuentos);
	
	var negativo = false;
	if (resta <0){
		negativo = true;
	}
	ponerPuntos(negativo, resta);
}

function sacarPuntos(numero){
	
	numero =numero.replace(".", "");
	numero =numero.replace(".", "");
	numero =numero.replace(".", "");
	numero =numero.replace(".", "");
	numero =numero.replace(".", "");
	
	return (numero);
}

function ponerPuntos(negativo, resta){
	$("#ley").mask('###.###.###',{reverse: true});
	$("#impuesto_renta").mask('###.###.###',{reverse: true});
	$("#monto_otros_descuentos").mask('###.###.###',{reverse: true});
	$("#iva_comision").mask('###.###.###',{reverse: true});
	valor = Math.abs(resta);
	$("#total_a_cobrar").html("");
	$("#total_a_cobrar").unmask();
	$("#total_a_cobrar").html(valor);
	$("#total_a_cobrar").mask('###.###.###',{reverse: true});
	
	if (negativo){
		total = "-"+$("#total_a_cobrar").html();
		$("#total_a_cobrar").unmask('###.###.###',{reverse: true});
		$("#total_a_cobrar").html(total);
	} else {
		total = $("#total_a_cobrar").html();
		$("#total_a_cobrar").unmask('###.###.###',{reverse: true});
		$("#total_a_cobrar").html(total);
	}
	
}

function validar() {
    if ($('#fecha_ini').val() == "" || $('#fecha_fin').val() == "") {
        alert("Debe ingresar un rango de fechas");
        return;
    }
    if ($('#fraccion_ini').val() == 0 || $('#fraccion_fin').val() == 0 || $('#fraccion_ini').val() == "" || $('#fraccion_fin').val() == "") {
        alert("Debe ingresar un rango de fracciones");
        return;
    }
    $("#frm_busqueda").submit();
}

function setup_inputs() {
	$("#id_tipo_busqueda").change(function() {
	    $("#id_busqueda_label").empty();
        $("#id_busqueda_label").val("");
        $("#id_busqueda").empty();
		autocompletes();		
	});
	$("#id_busqueda_label").change(function() {
		autocompletes();		
	});
	$("#id_fraccion_fin").change(function() {
		autocompletes();		
	});
	autocompletes();
}

function autocompletes(){
	$("#id_busqueda_label").autocomplete();
    if ($("#id_busqueda").val() == "") {
        $("#fecha_ini").prop('disabled', true);
        $("#fecha_fin").prop('disabled', true);
        $("#id_busqueda_label").prop('disabled', true);
        $("#boton_buscar").prop('disabled', true);
        $("#id_boton").attr("disabled", "disabled");
    }
    if ($("#id_tipo_busqueda").val() == "fraccion") {

        $("#fecha_ini").prop('disabled', false);
        $("#fecha_fin").prop('disabled', false);
        $("#id_busqueda_label").prop('disabled', false);
        $("#boton_buscar").prop('disabled', false);
        $("#id_boton").prop('disabled', false);
        $("#id_boton").removeAttr("disabled");

        var id_fraccion;
        $("#id_busqueda_label").empty();
        base_url = base_context + "/ajax/get_fracciones_by_name/";
        params = "value";
        $("#id_busqueda_label").autocomplete("destroy");
        $("#id_busqueda_label").autocomplete({
            source: base_url,
            minLength: 1,
            select: function (event, ui) {
                id_fraccion = ui.item.id;
                $("#id_busqueda").val(id_fraccion);
            }
        });
    }
    else if ($("#id_tipo_busqueda").val() == "propietario") {

        $("#fecha_ini").prop('disabled', false);
        $("#fecha_fin").prop('disabled', false);
        $("#id_busqueda_label").prop('disabled', false);
        $("#boton_buscar").prop('disabled', false);
        $("#id_boton").prop('disabled', false);
        $("#id_boton").removeAttr("disabled");

        var id_propietario;
        $("#id_busqueda_label").empty();
        $("#id_busqueda_label").empty('OLA');
        base_url = base_context + "/ajax/get_propietario_id_by_name/";
        params = "value";
        $("#id_busqueda_label").autocomplete("destroy");
        $("#id_busqueda_label").autocomplete({
            source: base_url,
            minLength: 1,
            create : function(){
			$(this).data('ui-autocomplete')._renderItem = function(ul,item){
				return $('<li>').append('<a>'+item.cedula +" - "+item.nombres + " "+ item.apellidos+'</a>').appendTo(ul);
				};
			},
			select : function(event, ui) {
				event.preventDefault();
                //alert('hola');
                id_propietario = ui.item.id;
                name_propietario=ui.item.nombres+" "+ui.item.apellidos;
                //alert(id_propietario);
                $('#id_busqueda').val(id_propietario);
                $('#id_busqueda_label').val(name_propietario);
            }
        });
    }
    else {
        $("#id_busqueda_label").empty();
        $("#fecha_ini").prop('disabled', true);
        $("#fecha_fin").prop('disabled', true);
        $("#id_busqueda_label").prop('disabled', true);
        $("#boton_buscar").prop('disabled', true);
        $("#id_boton").prop('disabled', true);
    }

}
