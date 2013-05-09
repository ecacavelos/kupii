$(document).ready(function() {
	$("#id_lote").keydown(validateLotePre);
	$("#id_lote").keyup(validateLotePost);
});

window.onload = function() {
};

// Funciones individuales
var global_lote_id = 0;
