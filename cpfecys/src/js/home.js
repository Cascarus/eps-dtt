/*
emarquez: 15 septiembre 2015
comentario: script creado para funciones utiles en toda la aplicacion cpfeys
*/

//Obtiene todos los periodos variables
function getPeriodosVariables()
{

  $.ajax({
    url:_URLPERIOD_VARIABLE,
    success: function(result){
          var obj  = JSON.parse(result);
          if(obj)
          {
            PERIODOS_VARIABLES=obj;

          }
    }
  });
}

//Obtiene todos los periodos de semestre.
function getPeriodosSemestre()
{
  $.ajax({
    url:_URLPERIOD_SEMESTRE,
    async: false,
    success: function(result){
          var obj  = JSON.parse(result);
          if(obj)
          {
            PERIODOS_SEMESTRE= obj;
          }
    }
  });
}


//emarquez: llena el combo enviado, con la informacion de los periodos variables.

function llenaComboPeriodosVariables(idCombo)
{
 $("#"+idCombo).empty();

  $.each(PERIODOS_VARIABLES,function(index,data){
  	var o = new Option(data.period.name+"-"+data.period_year.yearp, data.period_year.id);
  	$("#"+idCombo).append(o);

  });

}


function llenaComboPeriodosVariablesAjax(idCombo,setId)
{
 $("#"+idCombo).empty();

 $.ajax({
    url: _URLPERIOD_VARIABLE,
    async : true,
    success: function(result){
          var obj  = JSON.parse(result);
          if(obj)
          {
              PERIODOS_VARIABLES=obj;

               $.each(PERIODOS_VARIABLES,function(index,data){
               var o = new Option(data.period.name+"-"+data.period_year.yearp, data.period_year.id);
               $("#"+idCombo).append(o);              
              });

               if(setId) $("#"+idCombo).val(setId);

          }
    }
  });

}




//emarquez: llena el combo enviado, con la informacion de periodos de semestre
function llenaComboPeriodosSemestres(idCombo)
{
  $("#"+idCombo).empty();

  $.each(PERIODOS_SEMESTRE,function(index,data){
    var o = new Option(data.period.name+"-"+data.period_year.yearp, data.period_year.id);
  	$("#"+idCombo).append(o);

  });

}


function llenaComboPeriodosSemestresAjax(idCombo,setId)
{
  $("#"+idCombo).empty();

   $.ajax({
    url:_URLPERIOD_SEMESTRE,
    async: true, //colocado true, para que no se vea el retardo del switch, ( se traen datos y el efecto al mismo tiempo)
    success: function(result){
          var obj  = JSON.parse(result);
          if(obj)
          {
            PERIODOS_SEMESTRE= obj;

             $.each(PERIODOS_SEMESTRE,function(index,data){
              var o = new Option(data.period.name+"-"+data.period_year.yearp, data.period_year.id);
              $("#"+idCombo).append(o);

              });

              if(setId) $("#"+idCombo).val(setId);
          }
    }
  });
}

$.ajax({
  url: _URLPERIOD_SEMESTRE,
  async: false,
  success: function (result) {
    if (result) {
      var obj  = JSON.parse(result);
      PERIODOS_SEMESTRE = obj;
    }

    $.ajax({
      url: _URLPERIOD_VARIABLE,
      success: function (result) {
        var obj  = JSON.parse(result);
        if (obj) {
          PERIODOS_VARIABLES = obj;
        }
      }
    });
  }
});

  $('#chkTipoCurso').change(function() {
    if($(this).prop('checked'))
    llenaComboPeriodosSemestres("period");
    else llenaComboPeriodosVariables("period")
  });


  //verificar que parametros vienen para setear el chek y el combo
  if(periodo=="None")
    {	$('#chkTipoCurso').attr('checked')
  	setTimeout(function(){ llenaComboPeriodosSemestres("period"); $("#period").val(periodo); },1000);

    }
  else
  {
  	if(tipo_periodo=="None")
  		 {
  		$('#chkTipoCurso').removeAttr('checked')
  		setTimeout(function(){	llenaComboPeriodosVariables("period"); $("#period").val(periodo); },1000);
  	   }
  	else{
  	    $('#chkTipoCurso').attr('checked')
  	   	setTimeout(function(){	llenaComboPeriodosSemestres("period"); $("#period").val(periodo); }, 1000);
  		}
  }



  var youtube = document.querySelectorAll( ".youtube" );
  
  for (var i = 0; i < youtube.length; i++) {
      
      var source = "https://img.youtube.com/vi/"+ youtube[i].dataset.embed +"/sddefault.jpg";
      
      var image = new Image();
              image.src = source;
              image.addEventListener( "load", function() {
                  youtube[ i ].appendChild( image );
              }( i ) );
      
              youtube[i].addEventListener( "click", function() {

                  var iframe = document.createElement( "iframe" );

                          iframe.setAttribute( "frameborder", "0" );
                          iframe.setAttribute( "allowfullscreen", "" );
                          iframe.setAttribute( "src", "https://www.youtube.com/embed/"+ this.dataset.embed +"?rel=0&showinfo=0&autoplay=1" );

                          this.innerHTML = "";
                          this.appendChild( iframe );
              } );    
  };