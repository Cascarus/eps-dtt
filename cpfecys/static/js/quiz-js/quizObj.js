quizObj = {
	var itemNum:0,//conteo de todos los items ingresados en el formulario
	var objForm: new Array(),//miniformularios incluidos en el formulario
	var objItems: new Array(),//preguntas y respuestas del formulario
	register:function()
	{

	},
	callback:function()
	{

	},
	function GuardarPregunta(e)
	{
	   //Declaracion de valirbales
	   var id = objeto.substr(16,objeto.length);
	   var valor = document.getElementById("Campo_Pregunta"+id).value;
	   var cabecera = document.getElementById("Respuestas_P"+id);
	   var tipo = cabecera.getAttribute("name");
	   var respuestas = cabecera.childNodes.length ;
	   var jsonPregunta = '{"id_pregunta":"pregunta_'+id+'", "value":"'+valor+'", "tipo":"'+tipo+'","respuesta":';
	   var tmprespuesta = "";

	   if (valor != "")
	   {

	    switch(tipo)
	    {
	        case "multiple":
	            jsonPregunta += '[';
	            var vacias = 0
	            
	            for (var i = 0; i < respuestas; i++) 
	            {
	                if (cabecera.childNodes[i].childNodes[0].value=="")
	                vacias++;
	            }

	            if(vacias!=0)
	            {
	                alert("Llene todas las casilla de preguntas");
	            }
	            else
	            {
	                for (var i = 0; i < respuestas; i++) 
	                {
	                    if (cabecera.childNodes[i].childNodes[0].value!="")
	                    {
	                        /*
	                        Sintaxis respuesta a armar
	                        {
	                        "value": "respuesta1",
	                        "correcta": "true"
	                         }
	                        */
	                        var prefijo="";
	                        if (tmprespuesta!="")
	                            prefijo=", "
	                        
	                        tmprespuesta = prefijo + '{"value":"'+cabecera.childNodes[i].childNodes[0].value+'", "correcta":"'+cabecera.childNodes[i].childNodes[1].checked+'"}';
	                        DeshabilitarRespuesta(i,cabecera);
	                    }
	                     jsonPregunta += tmprespuesta; 
	                }
	                jsonPregunta += ']}';
	                preguntas.push(jsonPregunta);     
	            }
	            DeshabilitarPregunta(id);
	            document.getElementById("btAddRespuesta"+id).setAttribute("disabled", true);
	            break;

	        case "directa":
	            //alert("directa");
	            if (cabecera.childNodes[2].value!="")
	            {
	                tmprespuesta = '"'+cabecera.childNodes[2].value+'"';
	                jsonPregunta += tmprespuesta;
	                jsonPregunta += '}';
	                preguntas.push(jsonPregunta);
	                DeshabilitarPregunta(id);
	                cabecera.childNodes[2].setAttribute("disabled", true);
	            }
	            else
	            {
	                alert("Debe ingresar la respuesta antes de guardar");
	            }
	            break;

	        case "veracidad":
	            //alert("veracidad");
	            if(cabecera.childNodes[2].childNodes[0].checked)
	            {
	                tmprespuesta = '"true"';
	            }
	            else
	            {
	                tmprespuesta = '"false"';
	            }
	            jsonPregunta += tmprespuesta;
	            jsonPregunta += '}';
	            preguntas.push(jsonPregunta);
	            DeshabilitarPregunta(id);
	            cabecera.childNodes[2].childNodes[0].setAttribute("disabled", true);
	            cabecera.childNodes[3].childNodes[0].setAttribute("disabled", true);
	            break;
	    }
	    //alert("La pregunta es: "+jsonPregunta);
	    //alert("Todas sus respuestas estan ingresadas");
	    //alert("Hay "+preguntas.length+" registradas");
	     
	   }
	   else
	   {   
	     alert("Debe ingresar la informacion de la pregunta para poder guardarla");
	   }
	},

	getFormulary:function()
	{

	},
};
