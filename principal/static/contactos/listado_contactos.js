function inicializarFormularioBusqueda() {
    /* Inicializacion de variables */
    var tabla;
    var input_texto;
    var input_id;

    /* Autocomplete Lote */
    tabla = "lote";
    input_texto = $("#codigo_lote");
    input_id = $("#lote_id");
    autocompletePorTabla(input_texto, input_id, tabla);

    /* Autocomplete Cliente */
    tabla = "cliente";
    input_texto = $("#nombre_cliente");
    input_id = $("#cliente_id");
    autocompletePorTabla(input_texto, input_id, tabla);

    /* Autocomplete Usuario */
    tabla = "usuario";
    input_texto = $("#nombre_usuario");
    input_id = $("#usuario_id");
    autocompletePorTabla(input_texto, input_id, tabla);

    /* Se aplican masks */
    $("#codigo_lote").mask('###/###/####');

    $("#fecha_ini").mask('##/##/#### ##:##:##');

    $("#fecha_fin").mask('##/##/#### ##:##:##');

    spanishDateTimePicker();

    /* Se agregan datepickers */
    $("#fecha_ini").datetimepicker({
  		format:'dd/mm/yyyy hh:ii:ss',
  		lang:'es',
		autoclose: true,
		language: 'es'
	});

    $("#fecha_fin").datetimepicker({
  		format:'dd/mm/yyyy hh:ii:ss',
  		lang:'es',
		autoclose: true,
		language: 'es'
	});

    //$("#fecha_ini").focus();

}

// TODO: Hacer este envío y validacion correctamente por el form, de hecho crear el form de busqueda
function descargar_excel() {
    $('#formato_reporte').val("excel");
    $("#frm_busqueda").submit();
}

function validar() {
    if ($('#fecha_ini').val() == "" || $('#fecha_fin').val() == "") {
        $('#fecha_ini').val("");
        $('#fecha_fin').val("");
    }
    //nos aseguramos que elinar cosas de los hiddens si su input de autocomplete está vacío
    /* Lote */
    if ($("#codigo_lote").val() == '') {
        $("#lote_id").val("");
    }

    /* Cliente */
    if ($("#nombre_cliente").val() == '') {
        $("#cliente_id").val("");
    }

    /* Usuario */
    if ($("#nombre_usuario").val() == '') {
        $("#usuario_id").val("");
    }

    $('#formato_reporte').val("pantalla");

    $("#frm_busqueda").submit();
}
