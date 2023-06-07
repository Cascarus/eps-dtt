
function getPreguntas(){
    $.ajax({
      url : `/iso_bk_ev_rendimiento/pregunta_estudiante/${id_ev}/${id_user_project}`,
      //url: "{{=URL('iso_bk_ev_rendimiento', 'pregunta')}}/{{=id_ev}}",
      method: 'GET',
      datatype: 'JSON',
      success: colocarPregunta,
      error: function(data){
      }
    })
}

let grupoPregunta=[];
let ngrupo =0;
let preguntas = new Map();
function colocarPregunta(data){
    let j= data.length;
    if (!j){
      window.location="/home";
      return;
    }

    let grupo=[];

    for (let i=0; i<j;i++){
        if(i%3==0 & i!=0){
            grupoPregunta.push(grupo);
            grupo = [];
        }
        grupo.push(data[i]);
    }

    grupoPregunta.push(grupo);
    mostrarGrupo();
}

function mostrarGrupo(){
    document.getElementById("divBtn").style.display = 'none';
    document.getElementById("preguntas").style.display = 'none';
    document.getElementById("divloader").style.display = 'block';
    let grupo= grupoPregunta[ngrupo];
    let recurso = '/iso_bk_ev_rendimiento/respuesta_estudiante/';
    grupo.forEach((element)=>{
      htmlPregunta(element.tipo_pregunta+"", element.id,
                     element.descripcion, element.valor);
      recurso += `${element.id}/`
    });

    $.ajax({
      url: recurso,
      method: 'GET',
      datatype: 'JSON',
      success: (data)=>{
      data.forEach((element)=>{
          htmlRespuesta(element.id,element.descripcion, element.idp, element.punteo);
        });
        document.getElementById("divBtn").style.display = 'block';
        document.getElementById("preguntas").style.display = 'block';
        document.getElementById("divloader").style.display = 'None';
      }
    });
}

function siguienteGrupo(){ 
    continuar = recuperarRespuesta();
    //si falta alguna respuesta mostrar modal y no continuar ngrupo --
    if(!continuar)
      return;

    ngrupo ++;
    $("#preguntas").empty();
    mostrarGrupo();
}

function asignar(id){
  let estrellas =function (){
    let val = 10 * $('#rangoPreg' + id).val();
    $('#est' + id).css("width", val + "%");
  }
  return estrellas
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
                </div>
            </div>
            <div class="card-body">
              <h5 id="hcontP${id}">${cont}</h5>
              <textarea class="form-control col-md" id="coment${id}" />
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


function htmlRespuesta(idr, cont, idPreg, val){
  let respuesta = `
    <div id="idresp${idr}">
      <div class="form-check" >
        <input class="form-check-input" style="height: 1.5em; width:1.5em;"type="radio" name="prg${idPreg}" value="${idr}"/>
        <label class="form-check-label" style="font-size:1.5em;">${cont}</label>
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

function recuperarRespuesta(){
  let pregs = grupoPregunta[ngrupo];
  let cont = 0
  let respuestas={};
  let error = false;
  pregs.forEach(function(pregunta){

    let ponderacion;
    let comentario = null;
    let id_resp = null;
    switch(pregunta.tipo_pregunta){
      case 1: //cuantitativa
        let respuesta= $(`#rangoPreg${pregunta.id}`).val()/10;
        ponderacion = Math.round(respuesta * pregunta.valor);
        break;
      case 2: //cualitativa
        id_resp= $(`input:radio[name=prg${pregunta.id}]:checked`).val();
        if ( !id_resp){
          error = true;
          ponderacion = 0;
          $("#advertencia").modal("toggle");
          return ;
        }
        prg = preguntas.get(pregunta.id);
        ponderacion = prg.resp.get(parseInt(id_resp)).punteo;
        break;
      case 3: //comentario
        ponderacion = 0;
        comentario = $(`#coment${pregunta.id}`).val();
        break;
    }
    respuestas["id_pregunta" + cont] = pregunta.id;
    respuestas["id_evr_curso" + cont] = id_evr_curso;
    respuestas["valor" + cont] = ponderacion;
    respuestas["respuesta" + cont] = comentario;
    respuestas["id_respuesta" + cont] = id_resp;
    console.log(id_resp);
    cont++;
  })

  if (error)
    return false

  respuestas['preguntas'] = cont;
  $.ajax({
    url: `/iso_bk_ev_rendimiento/respuesta_estudiante/`,
    method: 'POST',
    datatype: 'JSON',
    data: respuestas,
    success: function(data){
      let grupo= grupoPregunta[ngrupo];
      if (!grupo){
        window.location="/home";
        document.getElementById('finalizada').style.display = 'block';
        return;
      }
      console.log(data);
    },
    error: function ( data) {
      console.log(data);
    }
  });

  return true;
}
