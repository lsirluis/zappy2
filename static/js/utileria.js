function mage(){

	alert("iniciado");
}
function buscador(unidad, propiedad){
 		$.ajax({
 			data:{'unidad': unidad,'propiedad':propiedad},
			 url:'/Propiedad/busqueda',
			 type:'get',
			 beforeSend: function(){
     			// alert("iniciando por favor espere");
				// $.fn.blockUI;
				limpiador();
				$("#id_recibo").empty();
				$("#msgloader").show();
			},				
			 success : function(data) {
	 				$("#msgloader").hide();
			 		if (data[1][0]) {
					var Rtorre = data[0].torre;
					$("#resultado").html(Rtorre);
			 		$('#busquedProyecto').val(Rtorre);
			 		$('#id_torre').val(data[0].torre);
			 		$('#id_numero').val(data[0].numero);
			 		$('#id_unidad').val(data[2]);
			 		$('#id_recibio').val(data[0].propi +" "+ data[0].apellido);
 	   				//agregamos las facturas en el select 
					var primerid =data[1][0].costo 
					var idRecibo =data[1][0].reciboid;
					$("#resultado2").html(primerid+"id del recibo: "+ idRecibo);
					// primero obtenemos el select
    				var x = document.getElementById("id_recibo");
    				var idRec =0;
    				var fechaco ="";
    				var costo = 0;
    				var consecutivo ="";
					// por cada posicion en la lista interna agregamos 
					// una opcion al select
					for (datos in data[1]){
						// alert(data[1][datos].costo);
						idRec = 	  data[1][datos].reciboid;
						consecutivo = data[1][datos].reciboConsecutivo
						fechaco = 	  data[1][datos].fechacobrada;
						costo =       data[1][datos].costo;

			 			var option = document.createElement("option");
						// option.text = idRec+"("+consecutivo+")-"+fechaco+"-Valor: "+costo;
						option.text ="No-"+ consecutivo +" Fecha: ("+fechaco+") / Costo: "+costo;
						option.value= idRec;
						x.add(option,idRec);	
					}
					//fin agregar facturas 
					// abrimos el modal
					$('#ModalReporPago').modal('show');
					}
					else{
						alert("Esta unidad No posee recibos vencidos");
					}
					console.log(data[0].torre, data[0].numero,"Propietario: ",data[0].propi,data[0].apellido);
			 },
			 error : function(message) {
			         console.log(message);
			         alert("error! codigo:BP001");
			      },
			complete: function(){
 				$("#msgloader").hide();
			}

 		});//ajax
	};

// metodo para hacer un post del formulario reportar un pago
function ReportPagoPost(form){
 		// var form = $(this).closest("form");
 		$.ajax({
 			data:form.serialize(),
			 url:'/Propiedad/addpago/',
			 type:'POST',
			 beforeSend: function(){
     			// alert("iniciando por favor espere");
     		$("#msgloader").show();

   			},				
			 success : function(data) {
			 $("#msgloader").hide();

    			// alert("Todo ok");
    			if (data.estado) {
				alert("hay un estado");
				alert(data.estado);


    			};
    			if (data.otro) {
				alert("hay un error en tipo");
				alert(data.otro);


    			};
    			if (data.success) {
					$('#ModalReporPago').modal('hide');
    				alert("los datos de han guardado exitosamente");
					limpiador();
    			};
    			if (data.errors) {
    				alert("Se han presentado errores, por favor corregirlos!!");
    				console.log("hay errores:"+data.errors);
    				if (data.errors.concepto) {
    					console.log("error de concepto:"+data.errors.concepto);
    					$('#id_concepto').addClass('errorinput');
    				};
    				if (data.errors.suma) {
    					console.log("error de suma:"+data.errors.suma);
    					$('#id_suma').addClass('errorinput');
    				};
    				if (data.errors.enletras) {
    					console.log("error de letras:"+data.errors.enletras);
    					$('#id_aletras').addClass('errorinput');
    				};
    				if (data.errors.no_comprobante) {
    					console.log("error de comprobante:"+data.errors.no_comprobante);
    					$('#id_no_comprobante').addClass('errorinput');
    				};
    				if (data.errors.recibo) {
    					console.log("error de recibo:"+data.errors.recibo);
    					$('#id_recibo').addClass('errorinput');
    				};
    			}else{
			   		console.log(data.result);
    			}
			 },
			 error : function(message){
			 	$("#msgloader").hide();
			   console.log(message);
			     }
 		});//ajax
 	}

 	function limpiador(){
 					$('#id_torre').val("");
			 		$('#id_numero').val("");
			 		$('#id_unidad').val("");
			 		$('#id_recibio').val("");
			 		$('#id_no_comprobante').val("");
			 		$('#id_concepto').val("");
			 		$('#id_suma').val("")
			 		aletras();
			 		document.getElementById("id_suma").readOnly=false;
			 		// $('#id_aletras').val("CERO PESOS");
			 		// $('#id_ciudad').val("");
			 		$('#id_referencia1').val("");
			 		$('#id_referencia2').val("");
			 		$('#id_numero').val("");
			 		$('#id_torre').val("");
			 		$('#id_no_comprobante').removeClass('errorinput');
			 		$('#id_concepto').removeClass('errorinput');
					$('#id_suma').removeClass('errorinput');
					$('#id_aletras').removeClass('errorinput');
					$('#id_recibo').removeClass('errorinput');

 	}

 	function Verpago(id){
 		$.ajax({
 			data:{'idcomprobante': id},
			 url:'/Propiedad/verpago',
			 type:'get',
			 beforeSend: function(){
     			// alert("iniciando por favor espere");
				// $.fn.blockUI;
				// $("#id_recibo").empty();
			},				
			 success : function(data) {
			 		// $('#id_torre').val(data[0].torre);
			 		// $('#id_numero').val(data[0].numero);
			 		// $('#id_unidad').val(data[2]);
			 		$('#id_recibio').val(data[0].pagador);
			 		$('#id_dia').html(data[0].dia);
			 		$('#id_mes').html(data[0].mes);
			 		$('#id_año').html(data[0].anio);
			 		$('#id_no_comprobante').val(data[0].no_comprobante);
					$('#id_referencia1').val(data[0].referencia1);
					$('#id_referencia2').val(data[0].referencia2);
					$('#id_suma').val(data[0].suma);
					$('#id_aletras').val(data[0].enletras);
					$('#id_concepto').val(data[0].concepto);
					$("#radio"+data[0].forma_pago).prop("checked", true);
					$('#id_fact').html(data[0].recibo)
			 },
			 error : function(message){
			 	console.log(message);

			 }
			});
 	}


function Reportcuotaextra(form){
 		// var form = $(this).closest("form");
 		$.ajax({
 			data:form.serialize(),
			 url:'/Propiedad/addcextra/',
			 type:'POST',
			 beforeSend: function(){
     			// alert("iniciando por favor espere");
     		$("#msgloader").show();

   			},				
			 success : function(data) {
			 $("#msgloader").hide();
			 if (data.success) {
					$('#ModalExtraordinaria').modal('hide');
    				alert("Agregada exitosamente!");
    				console.log("guardado de cuotas exitoso");
					// limpiador();
    			};
    		if (data.errors) {
    				alert("Se han presentado errores, por favor corregirlos!!");
    				console.log("hay errores:"+data.errors);

			}else{
				 console.log(data.result);
			}

			},
			error : function(message){
			 	console.log(message);
			}
			});
 	}



	// function buscador(unidad){
	// 	// alert("undiste un numero");
 //        // var mostrardiv = document.getElementById("dum");
 // 		// consulta = $("#busquedProyecto").val();
	// 	var resultadoGlobal="";
 // 		$.ajax({
	 		
 // 			data:{'unidad': unidad},
	// 		 url:'/Propiedad/busqueda',
	// 		 type:'get',
	// 		 success : function(data) {
	// 		         console.log(data[0].torre, data[0].numero,"Propietario: ",data[0].propi);

	// 		 },
	// 		 error : function(message) {
	// 		         console.log(message);
	// 		      }
 // 		});//ajax
	// 	alert(resultadoGlobal);
 // 		// alert( a.torre);
	// };

// 	<script type="text/javascript">
// 	function buscador(unidad){
// 		// alert("undiste un numero");
//         // var mostrardiv = document.getElementById("dum");
//  		consulta = $("#busquedProyecto").val();
//  		$.ajax({
//  			data:{'unidad': unidad},
// 			 url:'{% url "Propiedad:buscador" %}',
// 			 type:'get',
// 			 success : function(data) {
//         			// mostrardiv.innerHTML=data;
// 			         console.log(data[0].torre, data[0].numero,"Propietario: ",data[0].propi);
// 			 },
// 			 error : function(message) {
// 			         console.log(message);
// 			      }
//  		});//ajax
// 	};
// </script>