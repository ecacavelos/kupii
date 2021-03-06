/*
 * AUTOCOMPLETE para CLIENTES
 * Busca por RUC o NOMBRE
 * parametros: 
 * 1. id del input 
 * 2. id del input donde se coloca el valor de la cedula
 * 3. id del input donde se coloca el id del cliente
 * */
function autocompleteClienteRucONombre(input_id, cedula_input_id, id_cliente_input_id) {

    input_id = '#' + input_id;
    cedula_input_id = '#' + cedula_input_id;
    id_cliente_input_id = '#' + id_cliente_input_id;
    var cliente_id;
    $(input_id).empty();
    base_url = base_context + "/ajax/get_cliente_id_by_name_or_ruc/";
    params = "value";
    $(input_id).autocomplete({
        source: base_url,
        minLength: 1,
        create: function () {
            $(this).data('ui-autocomplete')._renderItem = function (ul, item) {
                return $('<li>').append('<a>' + item.cedula + " - " + item.nombres + " " + item.apellidos + '</a>').appendTo(ul);
            };
        },
        select: function (event, ui) {
            event.preventDefault();
            cliente_id = ui.item.id;
            cedula_cliente = ui.item.cedula;
            $(input_id).val(ui.item.nombres + " " + ui.item.apellidos);
            //name_cliente=ui.item.fields.nombres+" "+ui.item.fields.apellidos;
            //$("#id_name_cliente").val(name_cliente);
            $(id_cliente_input_id).val(cliente_id);
            $(cedula_input_id).val(cedula_cliente);
            $(this).trigger('change');
            return false;
        }
    });
}

/*
 * AUTOCOMPLETE para PROPIETARIOS
 * Busca por RUC o NOMBRE
 * parametros: 
 * 1. id del input 
 * 2. id del input donde se coloca el valor de la cedula
 * 3. id del input donde se coloca el id del propietario
 * */
function autocompletePropietarioRucONombre(input_id, cedula_input_id, id_propietario_input_id) {

    input_id = '#' + input_id;
    cedula_input_id = '#' + cedula_input_id;
    id_propietario_input_id = '#' + id_propietario_input_id;
    var propietario_id;
    $(input_id).empty();
    base_url = base_context + "/ajax/get_propietario_id_by_name_or_ruc/";
    params = "value";
    $(input_id).autocomplete({
        source: base_url,
        minLength: 1,
        create: function () {
            $(this).data('ui-autocomplete')._renderItem = function (ul, item) {
                return $('<li>').append('<a>' + item.cedula + " - " + item.nombres + " " + item.apellidos + '</a>').appendTo(ul);
            };
        },
        select: function (event, ui) {
            event.preventDefault();
            propietario_id = ui.item.id;
            cedula_cliente = ui.item.cedula;
            $(input_id).val(ui.item.item.nombres + " " + ui.item.apellidos);
            //name_cliente=ui.item.fields.nombres+" "+ui.item.fields.apellidos;
            //$("#id_name_cliente").val(name_cliente);
            $(id_propietario_input_id).val(propietario_id);
            $(cedula_input_id).val(cedula_cliente);
            $(this).trigger('change');
            return false;
        }
    });
}

/*
 * AUTOCOMPLETE para TIMBRADO
 * Busca por NUMERO de Timbrado
 * parametros: 
 * 1. id del input 
 * 2. id del input donde se coloca el valor del numero del timbrado
 * 3. id del input donde se coloca el id del timbrado
 * */
function autocompleteTimbradoPorNumero(input_id, id_timbrado_input_id) {

    input_id = '#' + input_id;
    id_timbrado_input_id = '#' + id_timbrado_input_id;
    $(input_id).empty();
    base_url = base_context + "/ajax/get_timbrado_by_numero/";
    $(input_id).autocomplete({
        source: base_url,
        minLength: 1,
        create: function () {
            $(this).data('ui-autocomplete')._renderItem = function (ul, item) {
                return $('<li>').append('<a>' + item.fields.numero + '</a>').appendTo(ul);
            };
        },
        select: function (event, ui) {
            event.preventDefault();
            id_timbrado = ui.item.pk;
            numero_timbrado = ui.item.fields.numero;
            $(timbrado).val(numero_timbrado);
            $(id_timbrado_input_id).val(id_timbrado);
        }
    });
}

function autocompleteClientePorNombreOCedula(tipo_busqueda, busqueda_label, busqueda) {
    if (tipo_busqueda == 'nombre') {
        console.log("por nombre");
        $("#busqueda_label").val("");
        var id_cliente;
        $("#busqueda").empty();
        base_url = base_context + "/ajax/get_cliente_id_by_name/";
        params = "value";
        $("#busqueda_label").autocomplete({
            source: base_url,
            minLength: 1,
            dataType: "json",
            create: function () {
                $(this).data('ui-autocomplete')._renderItem = function (ul, item) {
                    return $('<li>').append('<a>' + item.cedula + " - " + item.nombres + " " + item.apellidos + '</a>').appendTo(ul);
                    console.log(item);
                };
            },
            select: function (event, ui) {
                event.preventDefault();
                id_cliente = ui.item.id;
                $("#busqueda").val(id_cliente);
                $("#busqueda_label").val(ui.item.nombres + " " + ui.item.apellidos);
                //alert(id_cliente);
            }
        });
    }
    if (tipo_busqueda == 'cedula') {
        console.log("por cedula");
        $("#busqueda_label").val("");
        var id_cliente;
        $("#busqueda").empty();
        base_url = base_context + "/ajax/get_cliente_name_id_by_cedula/";
        params = "value";
        $("#busqueda_label").autocomplete({
            source: base_url,
            minLength: 1,
            create: function () {
                $(this).data('ui-autocomplete')._renderItem = function (ul, item) {
                    return $('<li>').append('<a>' + item.cedula + " - " + item.nombres + " " + item.apellidos + '</a>').appendTo(ul);
                    console.log(item);
                };
            },
            select: function (event, ui) {
                id_cliente = ui.item.id;
                event.preventDefault();
                $("#busqueda").val(id_cliente);
                //alert(id_cliente);
                $("#busqueda_label").val(ui.item.cedula);

            }
        });
    }
}

function autocompletePropietarioPorNombreOCedula(tipo_busqueda, busqueda_label, busqueda) {
    if (tipo_busqueda == 'nombre') {
        console.log("por nombre");
        $("#busqueda_label").val("");
        var id_propietario;
        $("#busqueda").empty();
        base_url = base_context + "/ajax/get_propietario_id_by_name/";
        params = "value";
        $("#busqueda_label").autocomplete({
            source: base_url,
            minLength: 1,
            create: function () {
                $(this).data('ui-autocomplete')._renderItem = function (ul, item) {
                    return $('<li>').append('<a>' + item.cedula + " - " + item.nombres + " " + item.apellidos + '</a>').appendTo(ul);
                };
            },
            select: function (event, ui) {
                event.preventDefault();
                $("#busqueda_label").val(ui.item.nombres + " " + ui.item.apellidos);
                id_propietario = ui.item.id;
                $("#busqueda").val(id_propietario);
                //alert(id_cliente);
            }
        });
    }

    if (tipo_busqueda == 'cedula') {
        console.log("por cedula");
        $("#busqueda_label").val("");
        var id_propietario;
        $("#busqueda").empty();
        base_url = base_context + "/ajax/get_propietario_name_id_by_cedula/";
        params = "value";
        $("#busqueda_label").autocomplete({
            source: base_url,
            minLength: 1,
            create: function () {
                $(this).data('ui-autocomplete')._renderItem = function (ul, item) {
                    return $('<li>').append('<a>' + item.cedula + " - " + item.nombres + " " + item.apellidos + '</a>').appendTo(ul);
                };
            },
            select: function (event, ui) {
                event.preventDefault();
                id_propietario = ui.item.id;
                $("#busqueda").val(id_propietario);
                $("#busqueda_label").val(ui.item.cedula);
                //alert(id_cliente);
            }
        });
    }
}

function autocompleteFraccionPorNombreOId(tipo_busqueda, busqueda_label, busqueda) {
    if (tipo_busqueda == 'nombre_fraccion') {
        console.log("por nombre fraccion");
        $("#busqueda_label").val("");
        var id_fraccion;
        $("#busqueda").empty();
        base_url = base_context + "/ajax/get_fracciones_by_name/";
        params = "value";
        $("#busqueda_label").autocomplete({
            source: base_url,
            minLength: 1,
            select: function (event, ui) {
                id_fraccion = ui.item.id;
                $("#busqueda").val(id_fraccion);
                //alert(id_cliente);
            }
        });
    }

    if (tipo_busqueda == 'numero') {
        console.log("por numero fraccion");
        $("#busqueda_label").val("");
        var id_fraccion;
        $("#busqueda").empty();
        base_url = base_context + "/ajax/get_fracciones_by_id/";
        params = "value";
        $("#busqueda_label").autocomplete({
            source: base_url,
            minLength: 1,

            select: function (event, ui) {
                event.preventDefault();
                id_fraccion = ui.item.id;
                $("#busqueda").val(id_fraccion);
                $("#busqueda_label").val(ui.item.id);
                //alert(id_cliente);
            }
        });
    }
}

function autocompleteLotePorCodigoParalot(tipo_busqueda, busqueda_label, busqueda) {
    if (tipo_busqueda == 'codigo') {
        //console.log("por codigo");
        $("#busqueda_label").val("");
        var id_lote;
        $("#busqueda").empty();
        base_url = base_context + "/ajax/get_lote_by_codigo_paralot/";
        params = "value";
        $("#busqueda_label").autocomplete({
            source: base_url,
            minLength: 1,
            select: function (event, ui) {
                event.preventDefault();
                id_lote = ui.item.id;
                $("#busqueda").val(id_lote);
                $("#busqueda_label").val(ui.item.codigo_paralot);
                //alert(id_cliente);
            }
        });
    }
}

function autocompleteEstadosLotes(tipo_busqueda, busqueda_label, busqueda) {
    if (tipo_busqueda == 'estado') {
        //console.log("por estado");
        $("#busqueda_label").val("");
        var id_lote;
        $("#busqueda").empty();
        base_url = base_context + "/ajax/get_lotes_by_estado/";
        params = "value";
        $("#busqueda_label").autocomplete({
            source: base_url,
            minLength: 1,
            select: function (event, ui) {
                event.preventDefault();
                id_estado = ui.item.id;
                $("#busqueda").val(id_estado);
                // $("#busqueda_label").val(ui.item.id_estado);
                //alert(id_cliente);
            }
        });
    }
}

function autocompleteFacturaPorNumero(tipo_busqueda, busqueda_label, busqueda) {
    if (tipo_busqueda == 'nro_factura') {
        //console.log("por codigo");
        $("#busqueda_label").val("");
        var id_factura;
        $("#busqueda").empty();
        base_url = base_context + "/ajax/get_factura_by_numero/";
        params = "value";
        $("#busqueda_label").autocomplete({
            source: base_url,
            minLength: 1,
            select: function (event, ui) {
                event.preventDefault();
                id_factura = ui.item.id;
                $("#busqueda").val(id_factura);
                $("#busqueda_label").val(ui.item.numero);
                //alert(id_cliente);
            }
        });
    }
}

function autocompleteVendedorPorNombreOCedula(tipo_busqueda, busqueda_label, busqueda) {
    if (tipo_busqueda == 'nombre') {
        console.log("por nombre");
        $("#busqueda_label").val("");
        var id_vendedor;
        $("#busqueda").empty();
        base_url = base_context + "/ajax/get_vendedor_id_by_name/";
        params = "value";
        $("#busqueda_label").autocomplete({
            source: base_url,
            minLength: 1,
            create: function () {
                $(this).data('ui-autocomplete')._renderItem = function (ul, item) {
                    return $('<li>').append('<a>' + item.cedula + " - " + item.nombres + " " + item.apellidos + '</a>').appendTo(ul);
                };
            },
            select: function (event, ui) {
                event.preventDefault();
                id_vendedor = ui.item.id;
                $("#busqueda").val(id_vendedor);
                $("#busqueda_label").val(ui.item.nombres + " " + ui.item.apellidos);
                //alert(id_cliente);
            }
        });
    }

    if (tipo_busqueda == 'cedula') {
        console.log("por cedula");
        $("#busqueda_label").val("");
        var id_vendedor;
        $("#busqueda").empty();
        base_url = base_context + "/ajax/get_vendedor_name_id_by_cedula/";
        params = "value";
        $("#busqueda_label").autocomplete({
            source: base_url,
            minLength: 1,

            select: function (event, ui) {
                event.preventDefault();
                id_vendedor = ui.item.id;
                $("#busqueda").val(id_vendedor);
                $("#busqueda_label").val(ui.item.cedula);
                //alert(id_cliente);
            }
        });
    }
}

/*
 * AUTOCOMPLETE para Vendedor
 * Busca por el nombre del vendedor
 * parametros: 
 * 1. id del input 
 * 2. id del input donde se coloca el nombre del vendedor
 * */
function autocompleteVendedorNombre(input_id, id_vendedor_input_id) {

    input_id = '#' + input_id;
    id_vendedor_input_id = '#' + id_vendedor_input_id;
    var vendedor_id;
    $(input_id).empty();
    base_url = base_context + "/ajax/get_vendedor_id_by_name/";
    params = "value";
    $(input_id).autocomplete({
        source: base_url,
        minLength: 1,
        create: function () {
            $(this).data('ui-autocomplete')._renderItem = function (ul, item) {
                return $('<li>').append('<a>' + item.cedula + " - " + item.nombres + " " + item.apellidos + '</a>').appendTo(ul);
            };
        },
        select: function (event, ui) {
            vendedor_id = ui.item.id;
            $(input_id).val(ui.item.nombres + " " + ui.item.apellidos);
            $(id_vendedor_input_id).val(vendedor_id);
            $(this).trigger('change');
            return false;
        }
    });
}

/*
 * AUTOCOMPLETE para Plan de Pago
 * Busca por el nombre del plan de pago
 * parametros: 
 * 1. id del input 
 * 2. id del input donde se coloca el nombre del plan de pago
 * */
function autocompletePlandePago(input_id, id_plandepago_input_id) {

    input_id = '#' + input_id;
    id_plandepago_input_id = '#' + id_plandepago_input_id;
    var planpago_id;
    $(input_id).empty();
    base_url = base_context + "/ajax/get_plan_pago/";
    params = "value";
    $(input_id).autocomplete({
        source: base_url,
        minLength: 1,
        create: function () {
            $(this).data('ui-autocomplete')._renderItem = function (ul, item) {
                return $('<li>').append('<a>' + item.nombre_del_plan + '</a>').appendTo(ul);
            };
        },
        select: function (event, ui) {
            planpago_id = ui.item.id;
            $(input_id).val(ui.item.nombre_del_plan);
            $(id_plandepago_input_id).val(planpago_id);
            $(this).trigger('change');
            return false;
        }
    });
}

function autocompletePorTabla(input_texto, input_id, tabla){
    if (tabla == "lote"){
        console.log("Iniciando autocomplete codigo de lote");
        input_texto.val("");
        var id_lote;
        input_id.empty();
        base_url = base_context + "/ajax/get_lote_by_codigo_paralot/";
        params = "value";
        input_texto.autocomplete({
            source: base_url,
            minLength: 1,
            select: function (event, ui) {
                event.preventDefault();
                id_lote = ui.item.id;
                input_id.val(id_lote);
                input_texto.val(ui.item.codigo_paralot);
            }
        });

    }

    if (tabla == "cliente"){
        console.log("Iniciando autocomplete cliente");
        input_texto.val("");
        var id_cliente;
        input_id.empty();
        base_url = base_context + "/ajax/get_cliente_id_by_name/";
        params = "value";
        input_texto.autocomplete({
            source: base_url,
            minLength: 1,
            dataType: "json",
            create: function () {
                $(this).data('ui-autocomplete')._renderItem = function (ul, item) {
                    return $('<li>').append('<a>' + item.cedula + " - " + item.nombres + " " + item.apellidos + '</a>').appendTo(ul);
                    console.log(item);
                };
            },
            select: function (event, ui) {
                event.preventDefault();
                id_cliente = ui.item.id;
                input_id.val(id_cliente);
                input_texto.val(ui.item.nombres + " " + ui.item.apellidos);
            }
        });
    }

    if (tabla == "usuario"){
        console.log("Iniciando autocomplete usuario");
        input_texto.val("");
        var id_usuario;
        input_id.empty();
        base_url = base_context + "/ajax/get_usuario_by_name/";
        params = "value";
        input_texto.autocomplete({
            source: base_url,
            minLength: 1,
            dataType: "json",
            create: function () {
                $(this).data('ui-autocomplete')._renderItem = function (ul, item) {
                    return $('<li>').append('<a>' + item.username + '</a>').appendTo(ul);
                    console.log(item);
                };
            },
            select: function (event, ui) {
                event.preventDefault();
                id_usuario = ui.item.id;
                input_id.val(id_usuario);
                input_texto.val(ui.item.username);
            }
        });
    }

}

/*
function isValidDate(dateString) {
    // First check for the pattern
    if(!/^\d{1,2}\/\d{1,2}\/\d{4} (\d{2}):(\d{2}):(\d{2})$/.test(dateString))
    {
        alert("Formato de fecha incorrecto");
        $('#enviar_pago').attr("disabled",true);
    	$('#id_fecha').val("");
        return false;
    }

    // Parse the date parts to integers
    var parts = dateString.split("/");
	var day = parseInt(parts[0], 10);
    var month = parseInt(parts[1], 10);
    var year = parseInt(parts[2], 10);

    // Check the ranges of month and year
    if(year < 1000 || year > 3000 || month == 0 || month > 12){
    	alert("Formato de fecha incorrecto");
        $('#enviar_pago').attr("disabled",true);
        $('#id_fecha').val("");
        return false;
    }

    var monthLength = [ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ];

    // Adjust for leap years
    if(year % 400 == 0 || (year % 100 != 0 && year % 4 == 0))
        monthLength[1] = 29;

    // Check the range of the day
    if(!(day > 0 && day <= monthLength[month - 1]))
    {
    	alert("Formato de fecha incorrecto");

        return false;
    }else
    {
    	return day > 0 && day <= monthLength[month - 1];
    }
}
*/

/* Esta funcion sirve para cambiar el datimepicker al espanhol */
function spanishDateTimePicker() {
    //Cambiar calendario a español
	$.fn.datetimepicker.dates['es'] = {
		days: ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
		daysShort: ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"],
		daysMin: ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do"],
		months: ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
		monthsShort: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
		today: "Hoy",
		suffix: [],
		meridiem: []
	};
}


function padDiaMesHorasMinutosSegundos (num) {
	max_size = 2 ;
	var s = "0" + num;
	return s.substr(s.length - max_size);
}
