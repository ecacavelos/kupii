function informe_facturacion() {
    if ($("#todos_excepto_pago_cuota").val() == 1) {
        window.location.href = base_context + "/informes/informe_facturacion_reporte_excel?fecha_ini=" + $('#fecha_ini').val() + "&fecha_fin=" + $('#fecha_fin').val() + "&busqueda=" + $('#busqueda').val() + "&busqueda_label=" + $('#busqueda_label').val() + "&sucursal=" + $('#sucursal').val() + "&sucursal_label=" + $('#sucursal_label').val() + "&fraccion=" + $('#fraccion').val() + "&fraccion_label=" + $('#fraccion_label').val() + "&concepto=" + $('#concepto').val() + "&concepto_label=" + $('#concepto_label').val() + "&todos_excepto_pago_cuota=1" + "&anulados=" + $('#anulados').val();
    } else {
        window.location.href = base_context + "/informes/informe_facturacion_reporte_excel?fecha_ini=" + $('#fecha_ini').val() + "&fecha_fin=" + $('#fecha_fin').val() + "&busqueda=" + $('#busqueda').val() + "&busqueda_label=" + $('#busqueda_label').val() + "&sucursal=" + $('#sucursal').val() + "&sucursal_label=" + $('#sucursal_label').val() + "&fraccion=" + $('#fraccion').val() + "&fraccion_label=" + $('#fraccion_label').val() + "&concepto=" + $('#concepto').val() + "&concepto_label=" + $('#concepto_label').val() + "&todos_excepto_pago_cuota=0" + "&anulados=" + $('#anulados').val();
    }

}

function validar() {
    if ($('#fecha_ini').val() == "" || $('#fecha_fin').val() == "") {
        alert("Debe ingresar un rango de fechas");
        return;
    }
    //nos aseguramos que elinar cosas de los hiddens si su input de autocomplete está vacío
    //usuario
    if ($("#busqueda_label").val() == '') {
        $("#busqueda").val("");
    }
    //sucursal
    if ($("#sucursal_label").val() == '') {
        $("#sucursal").val("");
    }
    //fraccion
    if ($("#fraccion_label").val() == '') {
        $("#fraccion").val("");
    }
    //concepto
    if ($("#concepto_label").val() == '') {
        $("#concepto").val("");
    }

    $("#frm_busqueda").submit();
}
