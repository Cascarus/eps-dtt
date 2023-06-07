

function getPreguntas(){
    $.ajax({
      url : `/iso_bk_ev_rendimiento/pregunta/${id_ev}`,
      //url: "{{=URL('iso_bk_ev_rendimiento', 'pregunta')}}/{{=id_ev}}",
      method: 'GET',
      datatype: 'JSON',
      success: colocarPregunta,
      error: function(data){
      }
    })
}

function colocarPregunta(data){
    data.forEach((element)=>{
      htmlPregunta(element.tipo_pregunta+"", element.id,
                   element.descripcion, element.valor);
      let recurso = `/iso_bk_ev_rendimiento/respuesta/${element.id}`
      $.ajax({
        url: recurso,
        method: 'GET',
        datatype: 'JSON',
        success: (data)=>{
          data.forEach((element)=>{
            htmlRespuesta(element.id,element.descripcion, element.idp, element.punteo);
          });
        }
      });
    });
    actualizar_punteo();
}

function agregarPregunta(){
    $("#dPregunta").modal();
  }

  function getTipoPregunta(){
    $.ajax({
      url: "/iso_ev_rendimiento/tipoPregunta",
      method: 'GET',
      datatype: 'JSON',
      success: function(data){
        let sTipos = $("#tipoP");
        sTipos.empty();
        sTipos.append("<option value='0' selected>Seleccione un tipo</option>");
        data.forEach(function(x){
          sTipos.append("<option value='"+ x.id +"'>" + x.descripcion+"</option>");
        });
      },
      error: function(data){
        console.log(data);
      }
    });
  }
function asignar(id){
  let estrellas =function (){
    let val = 10 * $('#rangoPreg' + id).val();
    $('#est' + id).css("width", val + "%");
  }
  return estrellas
}

let preguntas = new Map();
function selecTipo(){
  let tipo = $("#tipoP").val();
    if (tipo == '0' || tipo== '3'){
      $('#divPunteo').hide();
    }else{
      $('#divPunteo').show();
    }
  }

  function actualizarPregunta(){
    let cont = $('#modtxtPregunta').val();
    let punteo = $('#modtxtPunteo').val();
    let idp = parseInt($('#modactIdPreg').val());
    actPregunta(idp, cont, punteo);
    $('#modPregunta').modal('toggle');
  }

  function guardarPregunta(){
    $("#dPregunta").modal("toggle");
    let tipo = $('#tipoP').val();
    let cont = $('#txtPregunta').val();
    $('#txtPregunta').val('');
    let punteo = tipo=='3'?0:parseInt($('#txtPunteo').val());
    $('#txtPunteo').val(0);

    datos = {
      'descripcion': cont,
      'valor': punteo,
      'iso_tipo_pregunta_id': parseInt(tipo),
      'id_ev_rendimiento': parseInt(id_ev)
    };

    $.ajax({
      url: `/iso_bk_ev_rendimiento/pregunta`,
      method: 'POST',
      data: datos,
      success: function(data){
        for (let key in data.errors){
          return;
        }
        htmlPregunta(tipo, data.id, cont, punteo);
        actualizar_punteo();
      },
      error:(data)=>{
        console.log(datos);
      }
    });

    //TODO colocar la acción para refrescar la estrellas de rango
  }

function htmlPregunta(tipo, id, cont, punteo){
  let pregunta;
  switch(tipo){
    case "0":{
      return;
    }
    case "1":{
      pregunta = `
        <div class="card text-center" style="margin: .8em 3.8em .8em .8em" id="divP${id}">
          <div class="card-header alert-success" >
            <div class="text-right">
              <button class="btn btn-success boton" onclick="editarPregunta(${id})"><span class="fa fa-pencil-square-o" aria-hidden="true"/></button>
              <button class="btn btn-danger boton" onclick="borrarPregunta(${id})"><span class="fa fa-trash" aria-hidden="true"/></button>
            </div>
          </div>
          <div class="card-body">
            <h5 id="hcontP${id}">${cont}</h5>
            <div>
              <div class="stars-outer">
                <div class="stars-inner" id="est${id}"></div>
              </div>
            </div>
            <input id="rangoPreg${id}" type="range" min="0" max="10" step="1" value="0"/>
          </div>
        </div>`;
      break;
    }
    case "2":
    {
      pregunta = `<div class="card text-center" style="margin: .8em 3.8em .8em .8em;" id="divP${id}">
                      <div class="card-header alert-primary">
                        <div class="text-right">
                          <button class="btn btn-success boton" onclick="editarPregunta(${id})"><span class="fa fa-pencil-square-o" aria-hidden="true"/></button>
                          <button class="btn btn-danger boton" onclick="borrarPregunta(${id})"><span class="fa fa-trash" aria-hidden="true"/></button>
                          <button class="btn btn-primary boton" onclick="agregarRespuesta(${id})"><span class="fa fa-plus" aria-hidden="true"/></button>
                        </div>
                      </div>
                      <div class="card-body">
                        <h5 id="hcontP${id}">${cont}</h5>
                        <div id="formResp${id}" class="text-left"></div>
                      </div>
                    </div>`;
      break;
    }
    case "3":{
      pregunta = `
          <div class="card text-center" style="margin: .8em 3.8em .8em .8em;" id="divP${id}">
            <div class="card-header alert-dark">
              <div class="text-right">
                <button class="btn btn-success boton" onclick="editarPregunta(${id})"><span class="fa fa-pencil-square-o" /></button>
                <button class="btn btn-danger boton" onclick="borrarPregunta(${id})"><span class="fa fa-trash"></button>
              </div>
            </div>
            <div class="card-body">
              <h5 id="hcontP${id}">${cont}</h5>
              <textarea class="form-control col-md" />
            </div>
          </div>
        `;
    }
  }
  let p = {
    id: id,
    punteo: punteo,
    tipo: tipo,
    contenido: cont,
    resp: new Map()
  };

  preguntas.set(id, p);
  $('#preguntas').append(pregunta);
  if (tipo == '1'){
    $('#rangoPreg' + id).on('change', asignar(id));
  }
}

function agregarRespuesta(idPregunta){
  $('#idPregR').val(idPregunta);
  $("#dRespuesta").modal('toggle');
}

function guardarRespuesta(){
  $("#dRespuesta").modal('toggle');
  let idPreg = parseInt( $('#idPregR').val());
  $('#idPregR').val(0);
  let cont = $('#txtResp').val();
  $('#txtResp').val('');
  let val = parseInt($('#ptoResp').val());
  $('#ptoResp').val(0);

  if(cont == null || cont.len == 0)
    return;

  let pregunta = preguntas.get(idPreg);
  if(val > pregunta.punteo){
    // mostrar error
    let txt_error = document.getElementById('txt_error');
    let hijo = txt_error.children[0];
    txt_error.removeChild(hijo);
    $('#txt_error').append('<p><strong>El punteo de la respuesta no puede ser mayor al punteo de la pregunta.</stong></p>');
    $('#error_punteo').modal('toggle');
    return;
  }

  if(val < 0){
    // mostrar error
    let txt_error = document.getElementById('txt_error');
    let hijo = txt_error.children[0];
    txt_error.removeChild(hijo);
    $('#txt_error').append('<p><strong>El punteo no puede ser un número negativo.</stong></p>');
    $('#error_punteo').modal('toggle');
    return;
  }
  datos = {
    'descripcion': cont,
    'punteo': val,
    'iso_pregunta_id': idPreg
  };

  $.ajax({
    url: `/iso_bk_ev_rendimiento/respuesta`,
    method: 'POST',
    data: datos,
    success: function (data) {
      let errors = data.errors;
      for(let key in errors){
        return;
      }
      idr = data.id
      htmlRespuesta(idr, cont, idPreg, val);
    }
  });
}

function htmlRespuesta(idr, cont, idPreg, val){
  let respuesta = `
    <div id="idresp${idr}">
      <div class="form-check" >
        <input class="form-check-input" style="height: 1.5em; width:1.5em;"type="radio" name="prg${idPreg}"/>
        <label class="form-check-label" style="font-size:1.5em;">${cont}</label>
        <button class="btn btn-sm btn-success" style="border-radius: 50%" onclick="editRespuesta(${idPreg}, ${idr})"><span class="fa fa-pencil-square-o" aria-hidden="true"/></button>
        <button class="btn btn-sm btn-danger" style="border-radius: 50%" onclick="delRespuesta(${idPreg}, ${idr})"><span class="fa fa-trash" aria-hidden="true"/></button>
      </div>
    </div>
  `;

  let resp = {
    id: idr,
    punteo: parseInt(val),
    contenido: cont
  };
  
  let pregunta = preguntas.get(idPreg);
  pregunta.resp.set(idr, resp);

  $(`#formResp${idPreg}`).append(respuesta);
}

function borrarPregunta(idPregunta){
  $('#del_id_preg').val(idPregunta);
  $('#delPreg').modal('toggle');
}

function confDelPreg(){
  let idPregunta = parseInt($('#del_id_preg').val());
  datos = {
    'id': idPregunta
  }
  $.ajax({
      url: `/iso_bk_ev_rendimiento/pregunta`,
      method: 'DELETE',
      datatype: 'JSON',
      data: datos,
      success: function (data){
        let nodo = document.getElementById(`divP${idPregunta}`);
        let padre = nodo.parentNode;
        padre.removeChild(nodo);
        preguntas.delete(idPregunta);
        actualizar_punteo();
      }
  });

  $('#delPreg').modal('toggle');
}

function actPregunta(idPregunta, cont, punteo){
  let preg = preguntas.get(idPregunta);
  if(preg.contenido == cont && preg.punteo == punteo)
    return;
  datos = {
    'id': idPregunta,
    'descripcion': cont,
    'valor': punteo
  };

  $.ajax({
    url: `/iso_bk_ev_rendimiento/pregunta`,
    method: 'PUT',
    data: datos,
    success: function(data){
      preg.contenido = cont;
      preg.punteo = punteo;
      let hcont = $(`#hcontP${idPregunta}`);
      hcont.empty();
      hcont.append(cont);
      actualizar_punteo();
    }
  });

}

function editarPregunta(idPregunta){
  let pregunta = preguntas.get(idPregunta);
  $('#modactIdPreg').val(idPregunta);
  $('#modtxtPregunta').val(pregunta.contenido);
  $('#modtxtPunteo').val(pregunta.punteo);
  $('#modPregunta').modal('toggle');
}

function delRespuesta(idPregunta, idRespuesta){
  let pregunta = preguntas.get(idPregunta);
  $('#didPreg').val(idPregunta);
  $('#didResp').val(idRespuesta);
  $('#delResp').modal('toggle');
}

function confDelRespuesta(){
  let idPregunta = parseInt($('#didPreg').val());
  let idRespuesta = parseInt($('#didResp').val());
  $.ajax({
    url: `/iso_bk_ev_rendimiento/respuesta`,
    method: 'DELETE',
    data: {'id': idRespuesta},
    success: function (data){
        let pregunta = preguntas.get(idPregunta);
        pregunta.resp.delete(idRespuesta);
        let divResp = document.getElementById(`formResp${idPregunta}`);
        let hResp = document.getElementById(`idresp${idRespuesta}`);
        divResp.removeChild(hResp);
    }
  });
  $('#delResp').modal('toggle');
}

function modRespuesta(){
  let idResp = $("#midResp").val();
  let idPreg = $("#midPregR").val();
  let desc = $("#mtxtResp").val();
  let pregunta = preguntas.get(parseInt(idPreg));
  let respuesta = pregunta.resp.get(parseInt(idResp));
  let hResp = document.getElementById(`idresp${idResp}`);
  let punteo = parseInt($('#mptoResp').val())
  respuesta.punteo = punteo;
  $('#editRespuesta').modal('toggle');
  if(punteo > pregunta.punteo){
    let txt_error = document.getElementById('txt_error');
    let hijo = txt_error.children[0];
    txt_error.removeChild(hijo);
    $('#txt_error')
      .append(` <p>
                  <strong>La respuesta no debe sobrepasar el valor de ${pregunta.punteo} puntos</stong>
                </p>`);
    $('#error_punteo').modal('toggle');
    return;
  }

  let datos = {
    'id': idResp,
    'descripcion': desc,
    'punteo': punteo
  };

  $.ajax({
    url: `/iso_bk_ev_rendimiento/respuesta`,
    method: 'PUT',
    data: datos,
    datatype: 'JSON',
    success: function(data){
      let label = hResp.childNodes[1].childNodes[3];
      let text = label.childNodes[0];
      label.removeChild(text);
      let newtext = document.createTextNode(desc);
      label.appendChild(newtext);
    }
  });
}

function editRespuesta(idPregunta, idRespuesta){
  idPregunta = parseInt(idPregunta);
  idRespuesta = parseInt(idRespuesta);
  let respuesta = preguntas.get(idPregunta).resp.get(idRespuesta);
  $('#mtxtResp').val(respuesta.contenido);
  $('#mptoResp').val(respuesta.punteo);
  $('#midPregR').val(idPregunta);
  $('#midResp').val(idRespuesta);
  $('#editRespuesta').modal('toggle');
}


function actualizar_punteo(){
  let punteo = 0;
  for(let pregunta of preguntas.values()){
    punteo += parseInt(pregunta.punteo);
  }

  let divp = document.getElementById('div_punteo');
  let h = divp.children[0];
  divp.removeChild(h);
  $('#div_punteo').append(`<h4>Punteo: ${punteo}/100 puntos</h4>`);
  if(punteo > 100){
    let txt_error = document.getElementById('txt_error');
    let hijo = txt_error.children[0];
    txt_error.removeChild(hijo);
    $('#txt_error')
      .append(` <p>
                  <strong>Haz sobrepasado los 100 puntos, revisa tus punteos</stong>
                </p>`);
    $('#error_punteo').modal('toggle');
    return;
  }
}

function validarPreguntas(){
  for( let pregunta of preguntas.values()){
    if(pregunta.tipo == 2 && pregunta.resp.size == 0){
      let txt_error = document.getElementById('txt_error');
      let hijo = txt_error.children[0];
      txt_error.removeChild(hijo);
      $('#txt_error')
        .append(` <p>
                    <strong>Faltan respuestas para la pregunta: ${pregunta.contenido}</stong>
                  </p>`);
      $('#error_punteo').modal('toggle');
      return;
    }
  }
  document.location.assign(activar_ev);
}