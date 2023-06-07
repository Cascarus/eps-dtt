function submitLoad(controlador, funcion, params) {
  var retorno = "";
  pageload = `https://${location.hostname}/${controlador}/${funcion + params}`;
  $.ajax({
    url: pageload, 
    async: false,
    success: function(result) {
      retorno = (result); 
    }
  });

  return(retorno);
}

function LlamarControlador(controlador, funcion, params) {
  var retorno = "";
  pageload = `https://${location.hostname}/${controlador}/${funcion + params}`;
  alert(pageload);
  $.ajax({
    url: pageload, 
    async: false,
    success: function(result) {
      retorno = (result); 
    }
  });

  return(retorno);
}

function SendPost(controlador, funcion, params, datas) {
  var retorno = "";
  pageload = `https://${location.hostname}/${controlador}/${funcion + params}`;
  $.ajax({
    type: "POST",
    url: pageload,
    data: datas,
    dataType: 'json', 
  	success: function(result) {
      retorno = (result); 
    }
  });

  return(retorno);
}

function SendPostSinc(controlador, funcion, params, datas) {
  var retorno = "";
  pageload = `https://${location.hostname}/${controlador}/${funcion + params}`;
  $.ajax({
    type: "POST",
    url: pageload,
    data: datas,
    dataType: 'json', 
    async: false,
  	success: function(result) {
      retorno = (result); 
    }
  });
 
  return(retorno);
}
