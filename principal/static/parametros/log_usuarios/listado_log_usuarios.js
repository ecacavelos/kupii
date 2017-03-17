/* Todavía no esta implementado
 function excel_log_usuarios() {
 if($("#todos_excepto_pago_cuota").val()==1){
 window.location.href = base_context + "/informes/informe_facturacion_reporte_excel?fecha_ini=" + $('#fecha_ini').val() + "&fecha_fin=" + $('#fecha_fin').val()+"&busqueda="+$('#busqueda').val()+"&busqueda_label="+$('#busqueda_label').val()+"&sucursal="+$('#sucursal').val()+"&sucursal_label="+$('#sucursal_label').val()+"&fraccion="+$('#fraccion').val()+"&fraccion_label="+$('#fraccion_label').val()+"&concepto="+$('#concepto').val()+"&concepto_label="+$('#concepto_label').val()+"&todos_excepto_pago_cuota="+'1';
 }else{
 window.location.href = base_context + "/informes/informe_facturacion_reporte_excel?fecha_ini=" + $('#fecha_ini').val() + "&fecha_fin=" + $('#fecha_fin').val()+"&busqueda="+$('#busqueda').val()+"&busqueda_label="+$('#busqueda_label').val()+"&sucursal="+$('#sucursal').val()+"&sucursal_label="+$('#sucursal_label').val()+"&fraccion="+$('#fraccion').val()+"&fraccion_label="+$('#fraccion_label').val()+"&concepto="+$('#concepto').val()+"&concepto_label="+$('#concepto_label').val()+"&todos_excepto_pago_cuota="+'0';
 }

 }
 */

function enviar_busqueda() {
    $("#frm_busqueda").submit();
}

function validar() {
    /* Se valida la fecha */
    if ($('#fecha_ini').val() == "" || $('#fecha_fin').val() == "") {
        alert("Debe ingresar un rango de fechas");
        $('#fecha_ini').focus();
        return;
    }

    if( $("#usuario_name").val() == "" ){
        $("#usuario_id").val("");
    }

    if( $("#usuario_id").val() == "" ){
        $("#usuario_name").val("");
    }

    enviar_busqueda();
}


$(document).ready(function () {
    $("#fecha_ini").focus();

    //Cambiar calendario a español
    $.datepicker.regional['es'] = {
        closeText: 'Cerrar',
        prevText: '<Ant',
        nextText: 'Sig>',
        currentText: 'Hoy',
        monthNames: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
        monthNamesShort: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
        dayNames: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
        dayNamesShort: ['Dom', 'Lun', 'Mar', 'Mié', 'Juv', 'Vie', 'Sáb'],
        dayNamesMin: ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sá'],
        weekHeader: 'Sm',
        dateFormat: 'dd/mm/yy',
        firstDay: 1,
        isRTL: false,
        showMonthAfterYear: false,
        yearSuffix: ''
    };
    // Setear idioma al calendario
    $.datepicker.setDefaults($.datepicker.regional['es']);

    $('#fecha_ini').mask('##/##/####');
    $("#fecha_ini").datepicker({
        dateFormat: 'dd/mm/yy'
    });
    $('#fecha_fin').mask('##/##/####');
    $("#fecha_fin").datepicker({
        dateFormat: 'dd/mm/yy'
    });

    $('#lote_cod').mask('###/###/####');
    $('#nro_factura').mask('###-###-#######');

    base_url = base_context + "/ajax/get_usuario_by_username/";
    params = "value";
    $("#usuario_name").autocomplete({
        source: base_url,
        minLenght: 1,
        create: function () {
            $(this).data('ui-autocomplete')._renderItem = function (ul, item) {
                return $('<li>').append('<a>' + item.fields.username + '</a>').appendTo(ul);
            };
        },
        select: function (event, ui) {
            event.preventDefault();
            id_usuario = ui.item.pk;
            nombre_usuario = ui.item.fields.username;
            ui.item.value = ui.item.fields.username;
            $("#usuario_name").val(nombre_usuario);
            $("#usuario_id").val(id_usuario);
        },
        /* Para que al cerrar si nada fué seleccionado, borre el contenido del textfield */
        close: function (event, ui) {
            if ($("#usuario_id").val() == "") {
                $("#usuario_name").val("");
            }
        },
        change: function (ev, ui) {
            if (!ui.item) {
                $(this).val('');
            }
        }
    });

    $("#usuario_name").keyup(function(e) {
        if (e.keyCode == 27) { // escape key maps to keycode `27`
            $("#usuario_name").val("");
        }
    });

    base_url = base_context + "/ajax/get_lote_by_codigo_paralot/";
	params = "value";
	$("#lote_cod").autocomplete({
		source : base_url,
		minLength : 1,
		select : function(event, ui) {
			event.preventDefault();
			id_lote = ui.item.id;
			$("#lote_id").val(id_lote);
			$("#lote_cod").val(ui.item.codigo_paralot);
		},
        /* Para que al cerrar si nada fué seleccionado, borre el contenido del textfield */
        close: function (event, ui) {
            if ($("#lote_id").val() == "") {
                $("#lote_cod").val("");
            }
        },
        change: function (ev, ui) {
            if (!ui.item) {
                $(this).val('');
            }
        }
	});

    base_url = base_context + "/ajax/get_factura_by_numero/";
	params = "value";
	$("#nro_factura").autocomplete({
		source : base_url,
		minLength : 1,
		select : function(event, ui) {
			event.preventDefault();
			id_factura = ui.item.id;
			$("#factura_id").val(id_factura);
			$("#nro_factura").val(ui.item.numero);
			//alert(id_cliente);
		},
        /* Para que al cerrar si nada fué seleccionado, borre el contenido del textfield */
        close: function (event, ui) {
            if ($("#factura_id").val() == "") {
                $("#nro_factura").val("");
            }
        },
        change: function (ev, ui) {
            if (!ui.item) {
                $(this).val('');
            }
        }
	});

});
