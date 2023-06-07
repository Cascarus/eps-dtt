function EliminarPregunta(objeto) {
    var id = objeto.substr(17, objeto.length);
    var liaeliminar = `Pregunta_${id}`;
    $(`#${liaeliminar}`).remove();
    for(var i = 0; i <= preguntasObj.length-1; i++) {
        if(preguntasObj[i].id == id) {
            preguntasObj.splice(i, 1);
        }
    }
}

function DeshabilitarPregunta(id) {
    document.getElementById(`Guardar_Pregunta${id}`).setAttribute("disabled", true);
    document.getElementById(`Campo_Pregunta${id}`).setAttribute("disabled", true);
}

function HabilitarPregunta(id) {
    var attr_id = $(`#${id}`).attr("attr-id");
    $(`#Guardar_Pregunta${attr_id}`).removeAttr("disabled");
    $(`#Campo_Pregunta${attr_id}`).removeAttr("disabled");
    $(`#btAddRespuesta${attr_id}`).removeAttr("disabled");
    if($(`#Respuestas_P${attr_id}`).attr('name') != 'directa') $(`#Respuestas_P${attr_id}`).children().children().removeAttr("disabled");
    else $(`#Respuestas_P${attr_id}`).children().removeAttr("disabled");
}

function GruardarQuiz() {
    if(preguntasObj.length > 0) {
        var corr_quiz = submitLoad("quiz", "obtener_quiz", "");
        JsonCorretaltivo = JSON.parse(corr_quiz)
        var JsonQuiz = `{${JSON.stringify(preguntasObj)}}`;

        userid = document.getElementById("userid").name;
        projectid = document.getElementById("project_id").name;
        periodo_id = document.getElementById("period_id").name;
        idproject = document.getElementById("id_project").name;
        title = document.getElementById("txtTitulo").value;
        console.log(preguntasObj)
        var parametros = `?id=${JsonCorretaltivo.value}&uid=${userid}&project=${idproject}&title=${title}`;
        SendPost("quiz", "guardar_quiz_post", parametros, JsonQuiz);
        
        alert("Se ha guardado el cuestionario con id: "+ JsonCorretaltivo.value);
        var par = `?period=${periodo_id}&project=${idproject}`;
        
        window.location.href = `https://${location.hostname}/quiz/home_quiz${par}`;
    } else {
        alert("No hay preguntas");
        $('#popup').fadeIn('slow');
        $('.popup-overlay').fadeIn('slow');
        $('.popup-overlay').height($(window).height());
    }
}

function DeshabilitarRespuesta(id, cabecera) {
    document.getElementById(`Guardar_Pregunta${id}`).setAttribute("disabled", true);
    document.getElementById(`Campo_Pregunta${id}`).setAttribute("disabled", true);
}

function GuardarPregunta(objeto) {
   //Declaracion de valirbales
   var id = objeto.substr(16, objeto.length);//obtener el id numerico de la pregunta
   var valor = document.getElementById(`Campo_Pregunta${id}`).value;//obtener la pregunta
   var cabecera = document.getElementById(`Respuestas_P${id}`);//obtiene el set de respuestas
   var tipo = cabecera.getAttribute("name");//obtiene el tipo de pregunta
   var respuestas = cabecera.childNodes.length ;//obtiene el numero de hijos de la forma
   var jsonPregunta = `{"id_pregunta": "pregunta_${id}", "value": "${valor}", "tipo": "${tipo}", "respuesta":`;
   var objRespuesta = new Object();
   objRespuesta.id_pregunta = `pregunta_${id}`;
   objRespuesta.id = id;
   objRespuesta.value = valor;
   objRespuesta.tipo = tipo;
   var tmprespuesta = "";
   var tmpRespuestaArr = new Array();

    if (valor != "") {
        switch(tipo) {
            case "multiple":
                jsonPregunta += '[';
                var vacias = 0
                var correctas = 0
                $(`#Respuestas_P${id}`).children('li').each(function(_, value){
                    if($(value).children().first().val() == "") { vacias++; }
                    if($(value).children()[1].checked) { correctas++; }
                });

                if(vacias != 0) {
                    alert("Llene todas las casilla de preguntas");
                } else if (correctas < 1) {
                    alert("Debe de seleccionar almenos una respuesta como correcta")
                }
                else {
                    $(`#Respuestas_P${id}`).children('li').each(function(index, value){
                        if($(value).children().first().val() != "") {
                            /*
                            Sintaxis respuesta a armar
                                {
                                "value": "respuesta1",
                                "correcta": "true"
                                }
                            */
                            var prefijo = "";
                            if (tmprespuesta != "") prefijo = ", "
                            
                            tmprespuesta = `${prefijo} {"value":"${$(value).children().first().val()}", "correcta":"${$(value).children(':checkbox').is(':checked')}"}`;
                            var objTemp = new Object();
                            objTemp.value = $(value).children().first().val();
                            objTemp.correcta = $(value).children(':checkbox').is(':checked');
                            tmpRespuestaArr.push(objTemp);     
                        }
                    });

                    for (var i = 0; i < respuestas; i++) {
                        jsonPregunta += tmprespuesta; 
                    }
                    jsonPregunta += ']}';
                    objRespuesta.respuesta = tmpRespuestaArr;
                    preguntas.push(JSON.stringify(objRespuesta));

                    /*busco si el id ya existe, si existe actualizo el registro y sino lo creo*/
                    var index = -1;
                    for (var j = 0; j <= preguntasObj.length - 1;j++) {
                        if(preguntasObj[j].id == id) {
                            index = j;
                        }
                    }
                    if(index >= 0) { preguntasObj[index] = objRespuesta; } 
                    else { preguntasObj.push(objRespuesta); }
                    $(`#Respuestas_P${id}`).children('li').children().attr('disabled', true);
                    DeshabilitarPregunta(id);
                    document.getElementById(`btAddRespuesta${id}`).setAttribute("disabled", true);
                }

                break;
            case "directa":
                if ($(`#Respuestas_P${id}`).children('input').first().val() != "") {
                    tmprespuesta = `"${$("#Respuestas_P"+id).children('input').first().val()}"`;
                    jsonPregunta += tmprespuesta;
                    jsonPregunta += '}';
                    objRespuesta.respuesta = $(`#Respuestas_P${id}`).children('input').first().val();
                    preguntas.push(JSON.stringify(objRespuesta));
                    /*busco si el id ya existe, si existe actualizo el registro y sino lo creo*/
                    var index = -1;
                    for (var j = 0; j <= preguntasObj.length - 1;j++) {
                        if(preguntasObj[j].id == id) { index = j; }
                    }
                    if(index >= 0) { preguntasObj[index] = objRespuesta; }
                    else { preguntasObj.push(objRespuesta); }
                    DeshabilitarPregunta(id);
                    $(`#Respuestas_P${id}`).children('input').attr('disabled', true);
                } else {
                    alert("Debe ingresar la respuesta antes de guardar");
                }
                break;
            case "veracidad":
                jsonPregunta += cabecera.childNodes[4].childNodes[0].checked;
                jsonPregunta += '}';
                objRespuesta.respuesta = cabecera.childNodes[4].childNodes[0].checked;
                preguntas.push(JSON.stringify(objRespuesta));
                /*busco si el id ya existe, si existe actualizo el registro y sino lo creo*/
                var index = -1;
                for (var j = 0; j <= preguntasObj.length - 1;j++) {
                    if(preguntasObj[j].id == id) { index = j; }
                }
                if(index >= 0) { preguntasObj[index] = objRespuesta; }
                else { preguntasObj.push(objRespuesta); }
                DeshabilitarPregunta(id);
                cabecera.childNodes[4].childNodes[0].disabled = true;
                cabecera.childNodes[6].childNodes[0].disabled = true;
                break;
        }
    } else {   
     alert("Debe ingresar la informacion de la pregunta para poder guardarla");
    }
}

function EliminarRespuesta(objeto) {
    var id = objeto.substr(18, objeto.length);
    var liaeliminar = `Respuesta_${id}`;
    $(`#${liaeliminar}`).remove();
}

function AgregarRespuesta(objeto) {
    var id = objeto.substr(14, objeto.length);
    var idlo = `Respuestas_P${id}`;
    respuesta = `<li id="Respuesta_${idr}">
                    <input type="text">
                    <input type="checkbox"> Correcta
                    <button id="Eliminar_Respuesta${idr}" type="button" class="btn btn-danger" onclick="EliminarRespuesta(this.id)">X</button>
                </li>`;
    $(`#${idlo}`).append(respuesta);
    GetIDR();
}

function CrearEncabezado() {
    return `
        <form id="Formulario_P${idp}" class="form-dtt-quiz pt-3 pb-3">
            <div class="form-group">
                <h5>Ingrese la pregunta:</h5>
            </div>
            <div class="form-group">
                <textarea id="Campo_Pregunta${idp}"class="estilotextarea2" cols="1" rows="1"></textarea>
            </div>
            <div class="form-group">
                <button id="Guardar_Pregunta${idp}" type="button" class="btn btn-primary" onclick="GuardarPregunta(this.id)">
                    <i class="fa fa-floppy-o"></i>
                    Guardar
                </button>
                <button id="Editar_Pregunta${idp}" type="button" class="btn btn-warning" onclick="HabilitarPregunta(this.id)" attr-id="${idp}">
                    <i class="fa fa-pencil"></i>
                    Editar
                </button>
                <button id="Eliminar_Pregunta${idp}" type="button" class="btn btn-danger" onclick="EliminarPregunta(this.id)">
                    <i class="fa fa-trash"></i>
                    Borrar
                </button>
            </div>
        </form>`;
}   

$(document).ready(function() {
    function CrearRespuesta() {
        respuesta = `
            <li id="Respuesta_${idr}">
                <input type="text">
                <input type="checkbox"> Correcta
                <button id="Eliminar_Respuesta${idr}" type="button" class="btn btn-danger" onclick="EliminarRespuesta(this.id)">X</button>
            </li>`;
    }

    function CrearPregunta(tipo) {
        //Creamos la función que recoje los dos parámetros
        if (tipo == 1) {
            var encabezado = CrearEncabezado();

            pregunta = `<li id="Pregunta_${idp}" name="tipo1" class="list-group-item">
                            <div class="navbar" data-intro="Pregunta de opcion multiple">
                                <div class="navbar-inner">
                                    ${encabezado}
                                    </br>
                                </div>
                                <div class="well" id="div_repuestas">
                                    <fieldset>
                                        <a style="cursor:pointer;">Respuestas:</a><br>
                                        <ol id="Respuestas_P${idp}" type=A name="multiple"></ol>
                                    </fieldset>
                                    <button id="btAddRespuesta${idp}" type="button" class="btn btn-primary" onclick="AgregarRespuesta(this.id)">+ Agregar una nueva respuesta</button>
                                </div>
                            </div>`;
                                 
        } else if (tipo == 2) {
            var encabezado = CrearEncabezado();

            pregunta = `<li id="Pregunta_${idp}" name="tipo2" class="list-group-item"><div class="navbar" data-intro="Pregunta de respuesta corta">
                            <div class="navbar-inner">
                                ${encabezado}
                                <br>
                            </div>
                            <div class="well" id="div_repuestas">
                                <fieldset id="Respuestas_P${idp}" name="directa">
                                    <a style="cursor:pointer;">Ingrese la respuesta corta:</a><br><br>
                                    <input type="text">
                                </fieldset>
                            </div>
                        </div>`;
        } else {
            var encabezado = CrearEncabezado();

            pregunta = `<li id="Pregunta_${idp}" name="tipo3" class="list-group-item"><div class="navbar" data-intro="Pregunta falso o verdadero">
                            <div class="navbar-inner">
                                ${encabezado}
                                <br>
                            </div>
                            <div class="well" id="div_repuestas">
                                <fieldset id="Respuestas_P${idp}" name="veracidad">
                                    <a style="cursor:pointer;">Seleccione la respuesta:</a><br>
                                    <label><input type="radio" name="Opcion${idp}" value="verdadero" checked> Verdadero</input></label>
                                    <label><input type="radio" name="Opcion${idp}" value="falso" checked> Falso</input></label>
                                </fieldset>
                            </div>
                        </div>`;
        }        
    }

    $("#btAddTipo1").click(function() {
        CrearPregunta(1);
        $("#contenedorDePreguntas").append(pregunta);  
        
        var idPreg = `Respuestas_P${idp}`;
        for (var i = 0; i < 5; i++) {
            CrearRespuesta();
            $(`#${idPreg}`).append(respuesta);
            GetIDR();
        }
             
        GetID();
    });

    $("#btAddTipo2").click(function(){
        CrearPregunta(3);
        $("#contenedorDePreguntas").append(pregunta);
        GetID();
    });

    $("#btAddTipo3").click(function(){
        CrearPregunta(2);
        $("#contenedorDePreguntas").append(pregunta);
        GetID();
    });

    $("#btnContinuar").click(function(){
        if($("#txtTitulo").val() == "") { alert("Debe ingresar un nombre para la prueba"); }
        else { GruardarQuiz(); }
    });
});