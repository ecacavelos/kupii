function retrieve_liquidacion_propietarios() {
    window.location.href = base_context + "/informes/liquidacion_propietarios_reporte_excel?fecha_ini=" + $('#fecha_ini').val() + "&fecha_fin=" + $('#fecha_fin').val() + "&tipo_busqueda=" + $('#id_tipo_busqueda').val() + "&busqueda=" + $('#id_busqueda').val();
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
        $("#id_busqueda_label").autocomplete({
            source: base_url,
            minLength: 1,
            select: function (event, ui) {
                //alert('hola');
                id_propietario = ui.item.id;
                //name_propietario=ui.item.label;
                //alert(id_propietario);
                $('#id_busqueda').val(id_propietario);
                //$('#id_busqueda_label').val(name_propietario);
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
