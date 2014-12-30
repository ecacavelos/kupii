	function buscar() {
		if ($("#tipo_busqueda").val() == 0) {
			alert("Debe elegir un tipo de busqueda.");
		} else {
			if ($("#id_busqueda_label").val() == "") {
				alert("Debe ingresar un valor para buscar.");
			} else {
				$("#frm_busqueda").submit();
			}
		}
	}	
	
	function desplegar_campos() {	
		if ($("#tipo_busqueda").val() == 'fecha') {
			$('#id_busqueda_label').val("");
			$('#id_busqueda_label').unmask('');
			$('#fecha_hasta').val("");
			$("#id_busqueda_label").datepicker({
				dateFormat : 'dd/mm/yy'
			});
			$('#id_busqueda_label').mask('##/##/####');
			$("#fecha_hasta").datepicker({
				dateFormat : 'dd/mm/yy'
			});
			$("#fecha_hasta").mask('##/##/####');
			$("#fecha_hasta").show();
		}
		if ($("#tipo_busqueda").val() == 'lote') {
			$('#id_busqueda_label').val("");
			$("#fecha_hasta").hide();
			$("#id_busqueda_label").datepicker("destroy");
			$("#id_busqueda_label").removeClass("hasDatepicker");
			$('#id_busqueda_label').mask('###/###/####');
		}
		if ($("#tipo_busqueda").val() == 'vendedor') {
			$("#id_busqueda_label").val("");
			$('#id_busqueda_label').unmask('');
			$("#id_busqueda_label").datepicker("destroy");
			$("#id_busqueda_label").removeClass("hasDatepicker");
			var id_vendedor;
			$("#id_busqueda").empty();
			base_url = "/ajax/get_vendedor_id_by_name/";
			params = "value";
			$("#id_busqueda_label").autocomplete({
				source : base_url,
				minLength : 1,
				select : function(event, ui) {
					id_vendedor = ui.item.id;
					$("#id_busqueda").val(id_vendedor);
					//alert(id_vendedor);
					}
				});
		}
		if ($("#tipo_busqueda").val() == 'cliente'){
			$("#id_busqueda_label").val("");
			$('#id_busqueda_label').unmask('');
			$("#id_busqueda_label").datepicker("destroy");
			$("#id_busqueda_label").removeClass("hasDatepicker");
			var id_cliente;
			$("#id_busqueda").empty();
			base_url = "/ajax/get_cliente_id_by_name/";
			params = "value";
			$("#id_busqueda_label").autocomplete({
				source : base_url,
				minLength : 1,
				select : function(event, ui) {
					id_cliente = ui.item.id;
					$("#id_busqueda").val(id_cliente);
					//alert(id_cliente);
					}
				});			
		}
	}
	

	
