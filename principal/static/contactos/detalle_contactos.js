function inicializarFormulario() {
    /* Inicializacion de variables */

    /* Se agrega el campo texto para el autocomplete de lote*/
    var html_input_text = '<input id="id_lote_texto" maxlength="10" name="lote_texto" placeholder="Ej: 001/001/0001" size="15" maxlength="12" type="text" value="'+codigo_lote+'">';
    $("#id_lote").after(html_input_text);


    /* Se agrega el campo texto para el autocomplete de cliente*/
    html_input_text = '<input id="id_cliente_texto" maxlength="10" name="cliente_texto" placeholder="Nombre del Cliente al que se está contactando" size="100" maxlength="100" type="text"  value="'+nombre_cliente+'">';
    $("#id_cliente").after(html_input_text);

    /* Se agrega el texto SI al lado del checkbox */
    $("#id_respondido").after("<b id='si'>SI</b>");

    /* Se aplicanb masks */
    $("#id_lote_texto").mask('###/###/####');

    $("#id_fecha_contacto").mask('##/##/#### ##:##:##');

    $("#id_fecha_respuesta").mask('##/##/#### ##:##:##');

    $("#id_proximo_contacto").mask('##/##/#### ##:##:##');

    /* Validacion de fecha en blur (por el momento no funciona bien)
    $('#id_fecha_contacto').blur(function() {
		//$('#agregar_contacto').attr("disabled",false);
		if($('#id_fecha_contacto').val() != ""){
			isValidDate($('#id_fecha_contacto').val());
			alert("Fecha Inválida");
		}
    });

    $('#id_fecha_respuesta').blur(function() {
		//$('#agregar_contacto').attr("disabled",false);
		if($('#id_fecha_contacto').val() != ""){
			isValidDate($('#id_fecha_respuesta').val());
			alert("Fecha Inválida");
		}
    });

    $('#id_proximo_contacto').blur(function() {
		//$('#agregar_contacto').attr("disabled",false);
		if($('#id_fecha_contacto').val() != ""){
			isValidDate($('#id_proximo_contacto').val());
			alert("Fecha Inválida");
		}
    });
    */

    spanishDateTimePicker();

    var d = new Date();
    var day = padDiaMesHorasMinutosSegundos( d.getDate() );
    var mes = d.getMonth() + 1
	var month = padDiaMesHorasMinutosSegundos( mes );
	var year = d.getFullYear() ;

	var h = padDiaMesHorasMinutosSegundos( d.getHours() );
	var m = padDiaMesHorasMinutosSegundos( d.getMinutes() );
	var s = padDiaMesHorasMinutosSegundos( d.getSeconds() );

	var datetime = day+ "/" + month + "/" + year + " " + h + ":" + m + ":" + s;
	console.log(datetime);
	$('#id_fecha_respuesta').val(datetime);

    /* Se agregan datepickers */
    $("#id_fecha_respuesta").datetimepicker({
  		format:'dd/mm/yyyy hh:ii:ss',
  		lang:'es',
		autoclose: true,
		language: 'es'
	});

    $("#id_proximo_contacto").datetimepicker({
  		format:'dd/mm/yyyy hh:ii:ss',
  		lang:'es',
		autoclose: true,
		language: 'es'
	});

}

/* Por el momento no se usa, porque validamos a traves del form del Django */
function validarContacto() {
    $("#form_edit_contacto").submit();
}



