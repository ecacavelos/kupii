function informe_facturacion() {
    window.location.href = base_context + "/informes/informe_facturacion_reporte_excel?fecha_ini=" + $('#fecha_ini').val() + "&fecha_fin=" + $('#fecha_fin').val()+"&busqueda="+$('#busqueda').val()+"&busqueda_label="+$('#busqueda_label').val();
}

function validar() {
    if ($('#fecha_ini').val() == "" || $('#fecha_fin').val() == "") {
        alert("Debe ingresar un rango de fechas");
        return;
    }
    
    $("#frm_busqueda").submit();
}
