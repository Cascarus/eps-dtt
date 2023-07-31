function eliminar_area(valor) {
  let flag = false;
  let idx;
  // Verificar si el elemento ya existe en la bd
  areas.forEach((element, idx) => {
    if (element.id_area_especialidad === valor) {
      flag = true;
      idx = idx;
    }
  });

  // Ejecutar el query y eliminar el elemento del array en memoria
  if (flag) {
    $.ajax({
      url: "/curriculum/eliminar_area",
      type: "post",
      async: false,
      data: {
        id_area: valor,
      },
      success: function (data, status) {
        areas.splice(idx, 1)
      },
      error: function (error) {
        return;
      },
    });
  }

  // Eliminar elemento del array con todos los objetos en memoria
  all_areas.forEach((element, idx) => {
    if (element.id_area_especialidad === valor) {
      all_areas.splice(idx, 1)
    }
  });

  // Remover fila de la tabla
  $('#tb_areas_esp tr[id="' + valor + '"]').remove();
}

function eliminar_experiencia(valor) {
  let flag = false;
  let idx;

  // Verificar si el elemento a eliminar esta registrado en la bd
  experiencia_lab.forEach((element, idx) => {
    if (element.id_experiencia === valor) {
      flag = true;
      idx = idx;
    }
  });

  // Si esta registrado, ejecutar query y eliminar elemento del array en memoria
  if (flag) {
    $.ajax({
      url: "/curriculum/eliminar_experiencia",
      type: "post",
      async: false,
      data: {
        id_experiencia: valor,
      },
      success: function (data, status) {
        experiencia_lab.splice(idx, 1)
      },
      error: function (error) {
        return;
      },
    });
  }

  // Eliminar elemento del array con todos los objetos en memoria
  all_exp.forEach((element, idx) => {
    if (element.id_experiencia === valor) {
      all_exp.splice(idx, 1)
    }
  });

  // Eliminar fila de la tabla
  $('#tb_experiencia tr[id="' + valor + '"]').remove();
}


function guardarCambios(id_exp) {
  let flag = false;
  let indx = 0;

  // Obtener nuevos valores de los inputs
  let puesto = $("#inp_puesto").val();
  var empresa = $("#inp_empresa").val();
  var fecha_inicio = $("#inp_fecha_in").val();
  var fecha_fin = $("#inp_fecha_fin").val();
  var descripcion = $("#inp_descripcion").val();

  // Crear el nuevo objeto a almacenar
  let new_exp = {
    id_experiencia: id_exp,
    puesto: puesto,
    empresa: empresa,
    fecha_inicio: fecha_inicio,
    fecha_fin: fecha_fin,
    descripcion: descripcion
  };

  experiencia_lab.forEach((exp, idx) => {
    if (exp.id_experiencia == id_exp) {
      flag = true;
      indx = idx;
    }
  });

  // Ejecutar query de actualizacion y actualizar array en memoria
  if (flag) {
    $.ajax({
      url: "/curriculum/actualizar_experiencia",
      type: "post",
      async: false,
      data: {
        id_experiencia: id_exp,
        puesto,
        empresa,
        fecha_inicio,
        fecha_fin,
        descripcion
      },
      success: function (data, status) {
        experiencia_lab[indx] = new_exp;
        all_exp[indx] = new_exp;

        // Actualizar valores en la tabla
        $('#tb_experiencia tr[id="' + id_exp + '"]').find("td").eq(0).html(puesto);
        $('#tb_experiencia tr[id="' + id_exp + '"]').find("td").eq(1).html(empresa);
        $('#tb_experiencia tr[id="' + id_exp + '"]').find("td").eq(2).html(fecha_inicio);
        $('#tb_experiencia tr[id="' + id_exp + '"]').find("td").eq(3).html(fecha_fin);
      },
      error: function (error) {
        return;
      },
    });

    document.getElementById("agregarExp").innerHTML = '<i class="fa fa-plus"></i> Agregar';
    // Reiniciar bandera e index
    editFlag = false;
    edit_indx = -1;

    return;
  }

  all_exp.forEach((exp, idx) => {
    if (exp.id_experiencia == id_exp) {
      indx = idx;
    }
  });

  // Actualizar arrays
  all_exp[indx] = new_exp;

  // Actualizar valores en la tabla
  $('#tb_experiencia tr[id="' + id_exp + '"]').find("td").eq(0).html(puesto);
  $('#tb_experiencia tr[id="' + id_exp + '"]').find("td").eq(1).html(empresa);
  $('#tb_experiencia tr[id="' + id_exp + '"]').find("td").eq(2).html(fecha_inicio);
  $('#tb_experiencia tr[id="' + id_exp + '"]').find("td").eq(3).html(fecha_fin);

  document.getElementById("agregarExp").innerHTML = '<i class="fa fa-plus"></i> Agregar';
  // Reiniciar bandera e index
  editFlag = false;
  edit_indx = -1;

}



function rollback() {

  // Si el elemento esta registrado, ejecutar query
  $.ajax({
    url: "/curriculum/rollback",
    type: "post",
    async: true,
    data: {},
    success: function (data, status) { },
    error: function (error) {
      return;
    },
  });

}


function setEditarExperiencia(id_exp) {
  // Setear en inputs los valores del elemento qu ese quiere editar
  all_exp.forEach((exp, idx) => {
    if (exp.id_experiencia === id_exp) {
      $("#inp_puesto").val(exp.puesto);
      $("#inp_empresa").val(exp.empresa);
      $("#inp_fecha_in").val(exp.fecha_inicio);
      $("#inp_fecha_fin").val(exp.fecha_fin);
      $("#inp_descripcion").val(exp.descripcion);
    }
  });
  document.getElementById("agregarExp").innerHTML = '<i class="fa fa-save"></i> Guardar';
  document.getElementById("cancelarExp").classList.remove("d-none");
  // Setear a true para que la accion del boton llame a la funcion de editar
  editFlag = true;
  edit_indx = id_exp;
}





function editarCertificacion(id_cert) {
  let flag = false;
  let indx = 0;

  // Obtener valores de los input
  const nombre_certificacion = $("#inp_nombre_cert").val();
  const fecha_expedicion = $("#inp_fecha_cert").val();
  const enlace = $("#inp_enlace_cert").val();

  // Declarar nuevo objeto
  let new_cert = {
    id_certificacion: id_cert,
    nombre_certificacion,
    fecha_expedicion,
    enlace
  };

  // Verificar si el elemento a editar ya existe en la bd
  certificaciones.forEach((cert, idx) => {
    if (cert.id_certificacion == id_cert) {
      flag = true;
      indx = idx;
    }
  });

  // Si el elemento esta registrado, ejecutar query
  if (flag) {
    $.ajax({
      url: "/curriculum/actualizar_certificacion",
      type: "post",
      async: false,
      data: {
        ...new_cert
      },
      success: function (data, status) {

        // Actualizar array en memoria
        certificaciones[indx] = new_cert;
        // Actualizar fila en la tabla
        $('#tb_certificaciones tr[id="' + id_cert + '"]').find("td").eq(0).html(nombre_certificacion);
        $('#tb_certificaciones tr[id="' + id_cert + '"]').find("td").eq(1).html(fecha_expedicion);
        $('#tb_certificaciones tr[id="' + id_cert + '"]').find("td").eq(2).html(
          `   
              <button class="btn btn-primary btn-sm" type="button"  onclick="setEditarCertificacion(${id_cert})"><i class="fa fa-fw fa fa-edit" ></i></button>
              <button class="btn btn-danger btn-sm" type="button" onclick="eliminar_certificacion(${id_cert})"><i class="fa fa-fw fa fa-trash" ></i></button>                        
              `
        );
      },
      error: function (error) {
        return;
      },
    });

    document.getElementById("agregarCurso").innerHTML = '<i class="fa fa-plus"></i> Agregar';

    // Reiniciar banderas
    editFlag = false;
    edit_indx = -1;
    return;
  }
  // Elemento no existe en la bd

  // Actualizar array en memoria
  all_certificaciones[indx] = new_cert;
  // Actualizar fila en la tabla
  $('#tb_certificaciones tr[id="' + id_cert + '"]').find("td").eq(0).html(nombre_certificacion);
  $('#tb_certificaciones tr[id="' + id_cert + '"]').find("td").eq(1).html(fecha_expedicion);
  $('#tb_certificaciones tr[id="' + id_cert + '"]').find("td").eq(2).html(
    `   
    <a class="btn btn-primary btn-sm" href="${enlace}"><i class="fa fa-fw fa fa-eye" ></i></a>
        <button class="btn btn-primary btn-sm" type="button"  onclick="setEditarCertificacion(${id_cert})"><i class="fa fa-fw fa fa-edit" ></i></button>
        <button class="btn btn-danger btn-sm" type="button" onclick="eliminar_certificacion(${id_cert})"><i class="fa fa-fw fa fa-trash" ></i></button>                        
        `
  );

  document.getElementById("agregarCurso").innerHTML = '<i class="fa fa-plus"></i> Agregar';
  // Resetear banderas
  editFlag = false;
  edit_indx = -1;
}


function setEditarCertificacion(id_cert) {
  let flag = true;
  // Verificar si el elemento esta registrado en la bd, para obtenerlo del array en memoria
  certificaciones.forEach((cert, idx) => {
    if (cert.id_certificacion == id_cert) {
      $("#inp_nombre_cert").val(cert.nombre_certificacion);
      $("#inp_fecha_cert").val(cert.fecha_expedicion);
      $("#inp_enlace_cert").val(cert.enlace);
      flag = false;
    }
  });
  // No esta registrado en la bd
  if (flag) {
    // Obtener los valores de la tabla
    let nombre = $('#tb_certificaciones tr[id="' + id_cert + '"]').find("td").eq(0).html();
    let fecha = $('#tb_certificaciones tr[id="' + id_cert + '"]').find("td").eq(1).html();
    let enlace = $('#tb_certificaciones tr[id="' + id_cert + '"]').find("td").eq(2).find("a").attr("href");
    // Setear valores en los input
    $("#inp_nombre_cert").val(nombre);
    $("#inp_fecha_cert").val(fecha);
    $("#inp_enlace_cert").val(enlace);
  }

  document.getElementById("agregarCurso").innerHTML = '<i class="fa fa-save"></i> Guardar';
  document.getElementById("cancelarCurso").classList.remove("d-none");
  // Setear a true para que la accion del boton llame a la funcion de editar
  editFlag = true;
  edit_indx = id_cert;
}


function eliminar_certificacion(id_cert) {
  let flag = false;
  let idx;
  // Verificar si el elemento a eliminar se encuentra en la bd
  certificaciones.forEach((element, idx) => {
    if (element.id_certificacion == id_cert) {
      flag = true;
      idx = idx;
    }
  });

  // Si esta registrado en la bd, ejecutar query
  if (flag) {
    $.ajax({
      url: "/curriculum/eliminar_certificacion",
      type: "post",
      async: false,
      data: {
        id_certificacion: id_cert,
      },
      success: function (data, status) {
        // Eliminar elemento del array en memoria
        certificaciones.splice(idx, 1)
      },
      error: function (error) {
        return;
      },
    });
  }

  // Eliminar fila de la tabla
  $('#tb_certificaciones tr[id="' + id_cert + '"]').remove();
}



function eliminar_habilidad(id_habilidad) {
  let flag = false;
  let idx;
  // Verificar si el elemento se encuentra registrado en la bd
  habilidades.forEach((element, idx) => {
    if (element.id_habilidad == id_habilidad) {
      flag = true;
      idx = idx;
    }
  });

  // Si esta registrado, ejecutar query 
  if (flag) {
    $.ajax({
      url: "/curriculum/eliminar_habilidad",
      type: "post",
      async: false,
      data: {
        id_habilidad: id_habilidad,
      },
      success: function (data, status) {
        // Eliminar elemento del array en memoria
        habilidades.splice(idx, 1)
      },
      error: function (error) {
        return;
      },
    });
  }

  // Eliminar fila de la tabla
  $('#tb_habilidades tr[id="' + id_habilidad + '"]').remove();
}


