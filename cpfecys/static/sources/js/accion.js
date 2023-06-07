function submitLoad(controlador,funcion, parametros)
{
   pageload = `${location.protocol}//${location.hostname}:${location.port}/cpfecys/${controlador}/${funcion + parametros}`;
   //alert(pageload);
   var jsonResult='{"error":"empty"';
   $.ajax({url: pageload, 
         async: false, 
         success: function(result){
            jsonResult = result;
            //alert(jsonResult);    
            //alert("aca"+jsonResult);
            //this.jsonData=result;
            //eval(codex);
         }
      });
   return jsonResult;
}

function submitLoad2(form,module,op,custom_msg,notification,codex)
{
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

//********************************** REGISTRO DE SOLICITUDES *********************************
function agregar_curso(code, name, type)
{
    $('#div_error_0').hide('slow');
    if (cantidad<max_seleccionados){
        $('#tb_proyectos_dis tr[id="'+code+'"]').remove();
        var cod_area=$('select[name=selectArea]').val();

        if(cod_area==1){
             $('#tb_seleccionados').append('<tr id="'+code+'">\n\
                                    <td>'+name+'</td>\n\
                                    <td>\n\
                                        <input style="width:100%" id="sel_inp_anio_'+code+'" name="sel_inp_anio'+code+'" class="cls_sel_anio">\n\
                                    </td>\n\
                                    <td>\n\
                                         <select style="width:100%" name="semestre_apr" class="selectpicker form-control">\n\
                                            <option value="100">Primer semestre</option>\n\
                                            <option value="101">Vacaciones junio</option>\n\
                                            <option value="200">Segundo semestre</option>\n\
                                            <option value="201">Vacaciones diciembre</option>\n\
                                        </select>\n\
                                    </td>\n\
                                    <td>\n\
                                        <input style="width:100%" id="sel_inp_nota_'+code+'" name="sel_inp_nota_'+code+'" class="cls_sel_nota">\n\
                                    </td>\n\
                                    <td>\n\
                                        <input style="width:100%" id="sel_inp_cat_'+code+'" name="sel_inp_cat_'+code+'" class="cls_sel_cat">\n\
                                    </td>\n\
                                    <td id="'+type+'">\n\
                                        <button title="Remover proyecto seleccionado" class="btn btn-warning y" type="button" onclick="quitar_curso(\''+code+'\', \''+name+'\')"> <i class="fa fa-trash"></i></button>\n\
                                    </td>\n\
                                </tr>');
        }else{
            $('#tb_seleccionados').append('<tr id="'+code+'">\n\
                                    <td>'+name+'</td>\n\
                                    <td>\n\
                                        - -\n\
                                    </td>\n\
                                    <td>\n\
                                         - -\n\
                                    </td>\n\
                                    <td>\n\
                                        - -\n\
                                    </td>\n\
                                    <td>\n\
                                        - -\n\
                                    </td>\n\
                                    <td id="'+type+'">\n\
                                        <button title="Remover proyecto seleccionado" class="btn btn-warning x" type="button" onclick="quitar_curso(\''+code+'\', \''+name+'\');"><i class="fa fa-trash"></i></button>\n\
                                    </td>\n\
                                </tr>');
        }
        cantidad++;
    }else{
        $('#div_info').show('slow');
    }
    
}
function quitar_curso(code, name){
    var cod_area=$('select[name=selectArea]').val();
    var val_tipo = $('#tb_seleccionados tr[id="'+code+'"]').find('td').eq(5).attr('id');
    $('#tb_seleccionados tr[id="'+code+'"]').remove();

    if(cod_area==val_tipo){
        $('#tb_proyectos_dis').append('<tr id="'+ code +'">\n\
                                    <td>'+ name +'</td>\n\
                                    <td>\n\
                                        <button title="Agregar proyecto" class="btn btn-primary" type="button" id="btn_agregar_pr" href="javascript:void(0);"" onclick="javascript:agregar_curso(\''+code+'\', \''+name+'\', \''+val_tipo+'\');"><i class="icon-arrow-right icon-white"></i></button>\n\
                                    </td>\n\
                               </tr>');
    }
    if (cantidad>0){
        cantidad--;
    }
    $('#div_info').hide('slow');
}
function esta_seleccionado(code){ //1: SI está seleccionado; 0: NO está
    var pr_seleccionados= document.getElementById('tb_seleccionados');
    var respuesta=0;
    //alert('tamaño: '+ pr_seleccionados.rows.length);
    for(var i=0; i<pr_seleccionados.rows.length;i++){
        //alert('id: '+ pr_seleccionados.rows[i].id);
        if(code.localeCompare(pr_seleccionados.rows[i].id)==0){  //0: son iguales (de acuerdo al metodo localeCompare)
            respuesta=1;
        }
        
    }
    return respuesta;
}

function get_solicitud(){
    var respuesta='';
    respuesta = '?nombre='+ encodeURIComponent($('#inp_nombre').val())+'&apellido='+encodeURIComponent($('#inp_apellido').val())+'&cui='+encodeURIComponent($('#inp_cui').val())
                +'&carnet='+encodeURIComponent(carnet)+'&direccion='+encodeURIComponent($('#inp_direccion').val())+'&telefono='+encodeURIComponent($('#inp_telefono').val())+ '&trabaja='+encodeURIComponent($('#sel_trabaja option:selected').val())
                +'&idproceso='+encodeURIComponent(id_proceso)+'&anioproceso='+encodeURIComponent(anio_proceso)+'&periodoproceso='+encodeURIComponent(periodo_proceso)+'&proyectos=';
    
    var proyectos='[';
    var num_filas = $('#tb_seleccionados >tbody >tr').length;
    var i_filas = 1;
    $("#tb_seleccionados >tbody >tr").each(function(){
        var columnas=$(this).find('td');

        if(columnas.eq(5).attr('id')==1){
            proyectos+='{"pro_area":"'+columnas.eq(5).attr('id')+'",';
            proyectos+='"pro_codigo":"'+$(this).attr('id')+'",';
            proyectos+='"pro_nombre":"'+columnas.eq(0).text()+'",';
            proyectos+='"apr_anio":"'+columnas.eq(1).find('input').val()+'",';
            proyectos+='"apr_semestre":"'+columnas.eq(2).find('select').val()+'",';
            proyectos+='"apr_nota":"'+columnas.eq(3).find('input').val()+'",';
            proyectos+='"apr_catedratico":"'+columnas.eq(4).find('input').val()+'"}';
            if (i_filas<num_filas)
                proyectos+=',';
        }else{
            proyectos+='{"pro_area":"'+columnas.eq(5).attr('id')+'",';
            proyectos+='"pro_codigo":"'+$(this).attr('id')+'",';
            proyectos+='"pro_nombre":"'+columnas.eq(0).text()+'",';
            proyectos+='"apr_anio":"0",';
            proyectos+='"apr_semestre":"0",';
            proyectos+='"apr_nota":"0",';
            proyectos+='"apr_catedratico":"N/A"}';
            if (i_filas<num_filas)
                proyectos+=',';
        }
        i_filas++;
    });
    proyectos+=']';
    respuesta+=encodeURIComponent(proyectos);

    //alert(respuesta);
    return respuesta;
}

function get_obj_table(){
    var respuesta= new Array();
    
    var num_filas = $('#tb_seleccionados >tbody >tr').length;
    var i_filas = 1;
    $("#tb_seleccionados >tbody >tr").each(function(){
        var columnas=$(this).find('td');
        var objItem = new Object();
        if(columnas.eq(5).attr('id')==1){
            objItem.pro_area = columnas.eq(5).attr('id');
            objItem.pro_codigo = $(this).attr('id');
            objItem.pro_nombre = columnas.eq(0).text();
            objItem.apr_anio = columnas.eq(1).find('input').val();
            objItem.apr_semestre = columnas.eq(2).find('select').val();
            objItem.apr_nota = columnas.eq(3).find('input').val();
            objItem.apr_catedratico = columnas.eq(4).find('input').val();
            
        }
        else{
            objItem.pro_area = columnas.eq(5).attr('id');
            objItem.pro_codigo = $(this).attr('id');
            objItem.pro_nombre = columnas.eq(0).text();
            objItem.apr_anio = 0;
            objItem.apr_semestre = 0;
            objItem.apr_nota = 0;
            objItem.apr_catedratico = "N/A";
        }
        i_filas++;
        respuesta.push(objItem);
    });

    //alert(respuesta);
    return respuesta;
}