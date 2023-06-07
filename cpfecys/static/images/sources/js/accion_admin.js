function submitLoad(controlador, funcion, parametros) {
   pageload = `${location.protocol}//${location.hostname}:${location.port}/cpfecys/${controlador}/${funcion + parametros}`;
   var jsonResult = '{"error": "empty"}';
   $.ajax({url: pageload, 
      async: true, 
      success: function(result){
         jsonResult = result;
      }
   });

   return jsonResult;
}

function submitLoad2(form,module,op,custom_msg,notification,codex) {
   keys=$(form).serialize();
   pageload="/XXXX/"+module+'/'+op+"?"+keys;
   $.ajax({url: pageload, success: function(result){
      var jsonResult = JSON.parse(result);
      $.notifyDefaults({
         element: 'body',
         type: 'info',
         placement:{ from: 'top', align: 'center'},
         animate:{
            enter: "animated fadeInDown",
            exit: "animated fadeOutUp"
         },
         offset:{y: 50},
         delay: 2000,
         allow_dismiss: false,
         spacing: 10/*,
         showProgressbar: true*/
      });

      if(custom_msg!=null&&notification==true)
         notify=$.notify(
            custom_msg
         );
      else if(notification==true)
      {
         var msgx="";
         if(jsonResult.error==true&&jsonResult.exception!=null)
            msgx="<br>Err: "+jsonResult.exception;

         notify=$.notify(
            jsonResult.msg+msgx
         );
      }
      //alert("aca"+jsonResult);
      //this.jsonData=result;
      eval(codex);
      form.reset();
   }});
}

//********************************** FUNCIONES DE LA VISTA  *********************************
function ver_modal(titulo, nombre){
  /*$("#visor").attr("data","/cpfecys/static/pdf/"+nombre+"#toolbar=1");
  $('#myModalLabel').html(titulo);
  $("#myModal").modal('show');*/
  var new_tab=window.open("/cpfecys/static/pdf/"+nombre, "_blank");
  //new_tab.document.title = "testing";
}

function ver_modal_estado(titulo, nombre){
  /*$("#visor_estado").attr("data","/cpfecys/static/pdf/"+nombre+"#toolbar=1");
  $('#modal_label_estado').html(titulo);
  $("#modal_estado").modal('show');*/
  var new_tab=window.open('/cpfecys/static/pdf/'+nombre, "_blank");
  //new_tab.document.title = "testing";
}
function ver_modal_incorporacion(titulo, nombre){
  $("#img_incorporacion").attr("src","/cpfecys/static/img_nvo/"+nombre);
  $('#modal_label_incorporacion').html(titulo);
  $("#modal_incorporacion").modal('show');
}

function validar_seccion(id_fila, obj){
   var fila_verificar = $("#"+id_fila);
   var seccion_verificar = fila_verificar.find('td').eq(12).find('select').val();
   var pro_verificar= fila_verificar.find('td').eq(3).text();
   var cantidad_permitidas= 2;
   //alert("Id de la fila, ya es objeto: "+ fila.attr('id')+" Seccion: "+ cod_seccion);

   if(seccion_verificar.localeCompare("-1")==0 && fila_verificar.find('td').eq(13).find('select').val()==1){
      $('#h2_modal_msj').html('Debe seleccionar una sección valida y luego volver a cambiar el estado a "Aprobado"');
      $("#modal_info").modal('show');
      fila_verificar.find('td').eq(13).find('select').val('4'); //Regresan a Sin Puesto ya que eligio proyecto -1
   }else if(seccion_verificar.localeCompare("-1")!=0 && fila_verificar.find('td').eq(13).find('select').val()==1){ //Selecciona cualquier otro proyecto repetido cuando ya tiene estado aprobado
      var i_permitidas=1;
      
      /*if (lista_pro_asignados.localeCompare("0")!=0 && ya_esta_asignado(id_fila.split("-")[0], pro_verificar, seccion_verificar)){
            i_permitidas++;
      }*/
      if (lista_pro_asignados.localeCompare("0")!=0){
        i_permitidas+=ya_esta_asignado(id_fila.split("-")[0], pro_verificar, seccion_verificar);
      }

      $("#tb_reclutamiento >tbody >tr").each(function(){
         var fila_tabla = $(this);
         var seccion_tabla = fila_tabla.find('td').eq(12).find('select').val();
         var pro_tabla = fila_tabla.find('td').eq(3).text();
         
         if (fila_verificar.attr('id')!= fila_tabla.attr('id') && pro_verificar.localeCompare(pro_tabla)==0 && seccion_verificar.localeCompare(seccion_tabla)==0 && seccion_verificar.localeCompare('-1')!=0){ // 0: son iguales
            i_permitidas++;
         }
      });
      if (i_permitidas>cantidad_permitidas){
         $('#h2_modal_msj').html('Solo puede asignar 2 veces un mismo proyecto. Ya se encuentra seleccionada la sección "'+ seccion_verificar + '" | Proyecto: '+ pro_verificar);
         $("#modal_info").modal('show');
         fila_verificar.find('td').eq(12).find('select').val(obj.oldvalue);   
      }
   }
   else{
      var i_permitidas=1;
      /*if (lista_pro_asignados.localeCompare("0")!=0 && ya_esta_asignado(id_fila.split("-")[0], pro_verificar, seccion_verificar)){
        i_permitidas++;
      }*/
      if (lista_pro_asignados.localeCompare("0")!=0){
        i_permitidas+=ya_esta_asignado(id_fila.split("-")[0], pro_verificar, seccion_verificar);
      }

      $("#tb_reclutamiento >tbody >tr").each(function(){
         var fila_tabla = $(this);
         var seccion_tabla = fila_tabla.find('td').eq(12).find('select').val();
         var pro_tabla = fila_tabla.find('td').eq(3).text();

         if (fila_verificar.attr('id')!= fila_tabla.attr('id') && pro_verificar.localeCompare(pro_tabla)==0 && seccion_verificar.localeCompare(seccion_tabla)==0 && seccion_verificar.localeCompare('-1')!=0){ // 0: son iguales
            i_permitidas++;
         }
      });
      
      if (i_permitidas>cantidad_permitidas){
         $('#h2_modal_msj').html('Solo puede asignar 2 veces un mismo proyecto. Ya se encuentra seleccionada la sección "'+ seccion_verificar +'" | Proyecto: '+ pro_verificar);
         $("#modal_info").modal('show');
         fila_verificar.find('td').eq(12).find('select').val("-1");
      }
   }
}

function ya_esta_asignado(carnet_verificar, pro_verificar, seccion_verificar){
   var json_lista_asignados= JSON.parse(lista_pro_asignados);
   var respuesta = false;
   var veces = 0;
   
   $.each(json_lista_asignados, function(i, detalle) {
    //use obj.id and obj.name here, for example:
      if (pro_verificar.localeCompare(String(detalle.nombre_pro))==0 && seccion_verificar.localeCompare(String(detalle.seccion))==0){
         respuesta = true;
         veces++;
         //alert("Soy true:"+ detalle.seccion);   
      }
      
   });

   return veces;
}

function validar_estado(id_fila){
   //1 Verificar tenga nota oposicion
   //2 Verificar tenga seccion diferente de -1
   //3 Verificar no tenga aprobado en otro proyecto

   var valido = true;
   var fila_verificar = $("#"+id_fila); // Es la fila donde se esta cambiando el estado a aprobado
   var nota_verificar = fila_verificar.find('td').eq(11).find('input').val();
   var seccion_verificar = fila_verificar.find('td').eq(12).find('select').val();
   var estado_verificar = fila_verificar.find('td').eq(13).find('select').val();

   if(estado_verificar==1){
      if (nota_verificar.localeCompare("")==0){
         $('#h2_modal_msj').html('Para seleccionar estado "Aprobado" debe ingresar nota de examen de oposicion');
         $("#modal_info").modal('show');
         fila_verificar.find('td').eq(13).find('select').val("4");
         valido = false;
      }else if(seccion_verificar.localeCompare("-1")==0){
         $('#h2_modal_msj').html('Para seleccionar estado "Aprobado" elegir una sección válida');
         $("#modal_info").modal('show');
         fila_verificar.find('td').eq(13).find('select').val("4");
         valido = false;
      }else{
         var carnet_verificar = id_fila.split("-")[0];
         var num_pro_apr = 0;
         $("#tb_reclutamiento >tbody >tr").each(function(){
            var fila_tabla = $(this);
            var carnet_tabla= fila_tabla.attr('id').split("-")[0];
            var estado_tabla = fila_tabla.find('td').eq(13).find('select').val();

            if(fila_verificar.attr('id')!=fila_tabla.attr('id') && carnet_verificar==carnet_tabla && estado_tabla==1){
               //$('#h2_modal_msj').html('Solo puede elegir un estado "Aprobado" para un mismo estudiante'+ carnet_verificar+carnet_tabla);
               //$('#h2_modal_msj').html('Solo puede elegir un estado "Aprobado" para un mismo estudiante'+ carnet_verificar);
               //$("#modal_info").modal('show');
               //fila_verificar.find('td').eq(13).find('select').val("4");
               //valido = false;
               num_pro_apr++;
            }
         });
         if(num_pro_apr<2){
            if(num_pro_apr>0 && !confirm("¿Desea aprobar otro proyecto para: "+carnet_verificar+" ?")){
                  fila_verificar.find('td').eq(13).find('select').val("4");
                  valido = false;
            }
         }else{
            $('#h2_modal_msj').html('Solo puede aprobar 2 proyectos para un mismo estudiante'+ carnet_verificar);
            $("#modal_info").modal('show');
            fila_verificar.find('td').eq(13).find('select').val("4");
            valido = false;
         }
      }
   }


}

function guardar_estado_proceso(){
   var envio= submitLoad('reclutamiento_admin','mtd_guardar_reporte', '?tabla='+get_items_tabla());
   //alert(envio);
}

function get_items_tabla(){
   var items = '[';
   var num_filas = $("#tb_reclutamiento >tbody >tr").length;
   var i_filas = 1;

   $("#tb_reclutamiento >tbody >tr").each(function(){
      var columnas = $(this).find('td');

      items+='{"id":"'+$(this).attr('id').split("-")[1]+'",';
      items+='"nota_oposicion":"'+columnas.eq(11).find('input').val()+'",';
      items+='"seccion_proyecto":"'+columnas.eq(12).find('select').val()+'",';
      items+='"estado":"'+ columnas.eq(13).find('select').val() +'",';
      items+='"periodos":"'+ columnas.eq(14).find('input').val() +'",';
      items+='"horas":"'+ columnas.eq(15).find('input').val() +'"';
      items+='}';
      if (i_filas<num_filas){
         items+=',';
      }

      i_filas++;
   });

   items+=']';

   if (num_filas!=0){
      items= encodeURIComponent(items);
   }else{
      items = 'no';
   }

   return items;
}

function es_numero(numero){
   return (isNaN(numero))? false : (numero % 1 === 0);
}

// ------------------------ FUNCIONES PARA INCORPORACIÓN DE ESTUDIANTES NUEVOS ----------------------
function get_items_tabla_incorporacion(){
   var items = '[';
   var num_filas = $("#tb_incorporacion >tbody >tr").length;
   var i_filas = 1;

   $("#tb_incorporacion >tbody >tr").each(function(){
      var columnas = $(this).find('td');

      items+='{"id":"'+$(this).attr('id').split("-")[0]+'",';
      items+='"password":"'+columnas.eq(3).find('input').val()+'",';
      items+='"estado":"'+ columnas.eq(5).find('select').val() +'"';
      items+='}';
      if (i_filas<num_filas){
         items+=',';
      }

      i_filas++;
   });

   items+=']';

   if (num_filas>0){
      items= encodeURIComponent(items);
   }else{
      items = 'no';
   }

   return items;
}