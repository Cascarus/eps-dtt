function EliminarPregunta(objeto) {
    var id = objeto.substr(17,objeto.length);
    var liaeliminar = `Pregunta_${id}`;
    $(`#${liaeliminar}`).remove();

    //itero y busco la pregunta a eliminar
    for(var i = 0; i <= preguntasObj.length-1; i++) {
        if(preguntasObj[i].id == id) { preguntasObj.splice(i, 1); }
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
    if($(`#Respuestas_P${attr_id}`).attr('name') != 'directa') { $(`#Respuestas_P${attr_id}`).children().children().removeAttr("disabled"); }
    else { $(`#Respuestas_P${attr_id}`).children().removeAttr("disabled"); }
}

function GuardarQuiz() {
    if(preguntasObj.length > 0) {
        var JsonQuiz = `{${JSON.stringify(preguntasObj)}}`;
           
        userid = document.getElementById("userid").name;
        projectid = document.getElementById("project_id").name;
        periodo_id = document.getElementById("period_id").name;
        idproject = document.getElementById("id_project").name;
        title = document.getElementById("txtTitulo").value;
        quiz_id = $("#id").val();

        console.log(preguntasObj)
        var parametros = `?id=${$("#id_quiz").val()}&uid=${userid}&project=${idproject}&title=${title}&quiz_id=${quiz_id}`;
        SendPost("quiz", "actualizar_quiz_post", parametros, JsonQuiz);
        
        alert(`Se ha guardado el cuestionario con id: ${$("#id_quiz").val()}`);
        var par = `?period=${periodo_id}&project=${idproject}`;
        
        window.location.href = `https://${location.hostname}/quiz/home_quiz${par}`;
    } else {
        alert("No hay preguntas");
        $('#popup').fadeIn('slow');
        $('.popup-overlay').fadeIn('slow');
        $('.popup-overlay').height($(window).height());
    }
}

function DeshabilitarRespuesta(i, cabecera) {
    cabecera.childNodes[i].childNodes[0].setAttribute("disabled", true);
    cabecera.childNodes[i].childNodes[1].setAttribute("disabled", true);
    cabecera.childNodes[i].childNodes[3].setAttribute("disabled", true);
}

function GuardarPregunta(objeto) {
    //Declaracion de valirbales
    var id = objeto.substr(16, objeto.length);//obtener el id numerico de la pregunta
    var valor = document.getElementById(`Campo_Pregunta${id}`).value;//obtener la pregunta
    var cabecera = document.getElementById(`Respuestas_P${id}`);//obtiene el set de respuestas
    var tipo = cabecera.getAttribute("name");//obtiene el tipo de pregunta
    var jsonPregunta = `{"id_pregunta":"pregunta_${id}", "value":"${valor}", "tipo":"${tipo}","respuesta":`;
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
                } else if (correctas == 0) {
                    alert("Debe haber como mínimo una respuesta correcta");
                } else {
                    $(`#Respuestas_P${id}`).children('li').each(function(_, value){
                        if($(value).children().first().val() != "") {
                            var objTemp = new Object();
                            objTemp.value = $(value).children().first().val();
                            objTemp.correcta = $(value).children(':checkbox').is(':checked');
                            tmpRespuestaArr.push(objTemp);
                        }
                    });
                    
                    objRespuesta.respuesta = tmpRespuestaArr;
                    preguntas.push(JSON.stringify(objRespuesta));

                    /*busco si el id ya existe, si existe actualizo el registro y sino lo creo*/
                    var index = -1;
                    for (var j = 0; j <= preguntasObj.length - 1; j++) {
                        if(preguntasObj[j].id == id) { index = j; }
                    }
                    
                    if(index >= 0) {
                        preguntasObj[index] = objRespuesta;
                    } else {
                        preguntasObj.push(objRespuesta);
                    }
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

                    /*busco si el id ya existe, si existe actualizo el registro y sino lo creo*/
                    var index = -1;
                    for (var j = 0; j <= preguntasObj.length - 1; j++) {
                        if(preguntasObj[j].id == id) { index = j; }
                    }

                    if(index >= 0) { preguntasObj[index] = objRespuesta; }
                    else { preguntasObj.push(objRespuesta); }
                    DeshabilitarPregunta(id);
                    $(`#Respuestas_P${id}`).children('input').attr('disabled', true);
                } else { alert("Debe ingresar la respuesta antes de guardar"); }
                break;
            case "veracidad":
            tmprespuesta = false;
            if($(`#Respuestas_P${id}`).find('label').children('input').first().is(':checked')) { tmprespuesta = true; }
            jsonPregunta += tmprespuesta;
            jsonPregunta += '}';
            objRespuesta.respuesta = tmprespuesta;
            preguntas.push(JSON.stringify(objRespuesta));

            /*busco si el id ya existe, si existe actualizo el registro y sino lo creo*/
            var index = -1;
            for (var j = 0; j <= preguntasObj.length - 1; j++) {
                if(preguntasObj[j].id == id) { 
                    index = j; 
                    break;
                }
            }

            if(index >= 0) { preguntasObj[index] = objRespuesta; }
            else { preguntasObj.push(objRespuesta); }
            DeshabilitarPregunta(id);
            $(`#Respuestas_P${id}`).find('label').children('input').attr('disabled', true);
            break;
        }
    } else { alert("Debe ingresar la informacion de la pregunta para poder guardarla"); }
}

function EliminarRespuesta(objeto) {
    var id = objeto.substr(18, objeto.length);
    var liaeliminar = `Respuesta_${id}`;
    $(`#${liaeliminar}`).remove();
}

function AgregarRespuesta(objeto) {
    var id = objeto.substr(14, objeto.length);
    var idlo = `Respuestas_P${id}`;
    respuesta = `
        <li id="Respuesta_${idr}"><input type="text">
            <input type="checkbox"> Correcta
            <button id="Eliminar_Respuesta${idr}" type="button" class="btn btn-danger" onclick="EliminarRespuesta(this.id)">X</button>
        </li>`;

    $(`#${idlo}`).append(respuesta);
    GetIDR();
}

function CabeceraPregunta(){
    return `
        <form id="Formulario_P${idp}" class="form-dtt-quiz pt-3 pb-3">
            <div class="form-group">
                <h5>Pregunta:</h5>
            </div>
            <div class="form-group">
                <textarea id="Campo_Pregunta${idp}" class="estilotextarea2 form-control" cols="1" rows="1"></textarea>
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

$(document).ready(
    function() {
        var Pregunta;
        function CrearRespuesta() {
            respuesta = `
                <li id="Respuesta_${idr}"><input type="text">
                    <input type="checkbox"> Correcta
                    <button id="Eliminar_Respuesta${idr}" type="button" class="btn btn-danger" onclick="EliminarRespuesta(this.id)">X</button>
                </li>`;
        }

        function CrearPregunta(tipo) {
            //Creamos la función que recoje los dos parámetros
            if (tipo == 1) {
                var encabezado = CabeceraPregunta();

                pregunta = `
                    <li id="Pregunta_${idp}" name="tipo1" class="list-group-item">
                        <div class="navbar" data-intro="Pregunta de opcion multiple">
                            <div class="navbar-inner">
                                ${encabezado}
                                </br>
                            </div>
                            <div class="well" id="div_repuestas">
                                <fieldset name="multiple">
                                    <a style="cursor: pointer;">Respuestas:</a><br>
                                    <ol id="Respuestas_P${idp}" type="A" name="multiple"></ol>
                                </fieldset>
                                <button id="btAddRespuesta${idp}" type="button" class="btn btn-primary" onclick="AgregarRespuesta(this.id)">+ Agregar una nueva respuesta</button>
                            </div>
                        </div>
                    </li>`;
            } else if (tipo == 2) {
                var encabezado = CabeceraPregunta();

                pregunta = `
                    <li id="Pregunta_${idp}" name="tipo2" class="list-group-item">
                        <div class="navbar" data-intro="Pregunta de respuesta corta">
                        <div class="navbar-inner">
                            ${encabezado}
                            <br>
                        </div>
                        <div class="well" id="div_repuestas">
                            <fieldset id="Respuestas_P${idp}" name="directa">
                                <a style="cursor:pointer;">Ingrese respuesta corta:</a><br><br>
                                <input type="text">
                            </fieldset>
                        </div>
                    </li>`;
            } else {
                var encabezado = CabeceraPregunta();

                pregunta = `
                    <li id="Pregunta_${idp}" name="tipo3" class="list-group-item">
                        <div class="navbar" data-intro="Pregunta falso o verdadero">
                            <div class="navbar-inner">
                                ${encabezado}
                                <br>
                            </div>
                            <div class="well" id="div_repuestas">
                                <fieldset id="Respuestas_P${idp}" name="veracidad">
                                    <a style="cursor:pointer;">Seleccione la respuesta:</a><br><br>
                                    <label>
                                        <input type="radio" name="Opcion${idp}" value="verdadero" checked>
                                            Verdadero
                                        </input>
                                    </label>
                                    &nbsp;
                                    <label>
                                        <input type="radio" name="Opcion${idp}" value="falso">
                                            Falso
                                        </input>
                                    </label>
                                </fieldset>
                            </div>
                        </div>
                    </li>`;
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

        $("#btAddTipo2").click(function() {
            CrearPregunta(3);
            $("#contenedorDePreguntas").append(pregunta);
            GetID();
        });

        $("#btAddTipo3").click(function() {
            CrearPregunta(2);
            $("#contenedorDePreguntas").append(pregunta);
            GetID();
        });

        $("#btnContinuar").click(function() {
            if($("#txtTitulo").val() == "") { alert("Debe ingresar un nombre para la prueba"); }
            else { GuardarQuiz(); }
        });
    }
);