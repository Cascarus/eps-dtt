import cpfecys
import json

@auth.requires_login()
def lista_ofertas():
    session_id = auth.user.id
    query_ofertas = f"""
        SELECT 
            OL.PUESTO,
            OL.DESCRIPCION,
            E.nombre_empresa,
            AE.area_especialidad,
            OL.id_oferta_laboral
        FROM bt_oferta_laboral AS OL
            INNER JOIN bt_area_especialidad AS AE ON OL.id_area_especialidad = AE.id_area_especialidad
            INNER JOIN bt_estudiante_especialidad AS EE ON EE.id_area_especialidad = OL.id_area_especialidad
            INNER JOIN bt_empresa AS E ON OL.id_empresa = E.id_empresa
            INNER JOIN bt_estudiante_cv AS CV ON EE.id_estudiante_cv = CV.id_estudiante_cv
        WHERE 
            CV.id_usuario = {session_id} 
            AND OL.id_estado_oferta_laboral = 2;
    """
    ofertas = db.executesql(query_ofertas, as_dict=True)
    return dict(ofertas=ofertas)

def resumen():
    oferta_id = request.vars['num']

    # * 10324 + 13544 
    oferta_id = int(oferta_id)
    oferta_id = oferta_id - 134544
    oferta_id = oferta_id / 109324

    #consulta para resumen oferta laboral
    query_oferta = f"""
        SELECT 
            OL.puesto,
            OL.descripcion,
            OL.requerimientos,
            OL.salario_aproximado,
            E.nombre_empresa,
            AE.area_especialidad,
            E.id_empresa,
            E.telefono,
            E.correo
        FROM bt_oferta_laboral AS OL
            INNER JOIN bt_area_especialidad AS AE ON OL.id_area_especialidad = AE.id_area_especialidad
            INNER JOIN bt_empresa AS E ON OL.id_empresa = E.id_empresa
        WHERE OL.id_oferta_laboral = {oferta_id};
    """
    oferta = db.executesql(query_oferta, as_dict=True)

    return dict(
        ofe=oferta,
        markmin_settings=cpfecys.get_markmin,
        description_content=oferta[0]['descripcion'],
        requerimientos=oferta[0]['requerimientos']
    )

def seguimiento_sol():
    id_session = auth.user.id
    #consulta para obtener el seguimiento del proceso de contratacion
    query = f"""
        SELECT
            O.puesto,
            E.nombre_empresa,
            EA.estado_aplicacion,
            EO.id_estado_aplicacion,
            EO.id_oferta_laboral,
            CAST(EO.fecha_aplicacion AS varchar(20)) AS fecha,
            EO.id_estudiante_cv
        FROM bt_estudiante_oferta AS EO
            INNER JOIN bt_oferta_laboral AS O ON EO.id_oferta_laboral = O.id_oferta_laboral
            INNER JOIN bt_empresa AS E ON O.id_empresa = E.id_empresa
            INNER JOIN bt_estudiante_cv AS EC ON EO.id_estudiante_cv = EC.id_estudiante_cv
            INNER JOIN bt_estado_aplicacion AS EA ON EO.id_estado_aplicacion = EA.id_estado_aplicacion
        WHERE EC.id_usuario = {id_session}
    """
    seguimiento = db.executesql(query, as_dict=True)
    return dict(seg=seguimiento)

def vista_empresa():
    empresa_id = request.vars['num']

    #*720316 + 424686
    empresa_id = int(empresa_id)
    empresa_id = empresa_id - 424686
    empresa_id = empresa_id / 720316

    #consulta para ver informacion de la empresa
    query_empresa = f"""
        SELECT
            nombre_empresa,
            direccion,
            telefono,
            correo,
            descripcion,
            pagina_web,
            persona_encargada,
            fecha_registro
        FROM bt_empresa
        WHERE id_empresa = {empresa_id}
    """
    empresa = db.executesql(query_empresa, as_dict=True)
    return dict(emp=empresa)

def vista_oferta():
    oferta_id = request.vars['num']

    # *10324+13544 
    oferta_id = int(oferta_id)
    oferta_id = oferta_id - 134544
    oferta_id = oferta_id / 109324

    #consulta para obtener la oferta laboral seleccionada
    query = f"""
        UPDATE bt_oferta_laboral
        SET 
            visitas = (
                SELECT visitas 
                FROM bt_oferta_laboral 
                WHERE id_oferta_laboral = {oferta_id}
            ) + 1 
        WHERE id_oferta_laboral = {oferta_id}
    """
    query_oferta = f"""
        SELECT
            OL.puesto,
            OL.descripcion,
            OL.requerimientos,
            OL.salario_aproximado,
            E.nombre_empresa,
            AE.area_especialidad,
            E.id_empresa
        FROM bt_oferta_laboral AS OL
            INNER JOIN bt_area_especialidad AS AE ON OL.id_area_especialidad = AE.id_area_especialidad
            INNER JOIN bt_empresa AS E ON OL.id_empresa = E.id_empresa
        WHERE OL.id_oferta_laboral = {oferta_id};
    """
    db.executesql(query)
    oferta = db.executesql(query_oferta, as_dict=True)
    return dict(
        ofe=oferta,
        id=oferta_id,
        markmin_settings=cpfecys.get_markmin,
        description_content=oferta[0]['descripcion'],
        requerimientos=oferta[0]['requerimientos']
    )

def registro_solicitud():
    data = json.loads(request.post_vars.array)

    # *10324+13544 
    data['id'] = int(data['id'])
    data['id'] = data['id'] - 134544
    data['id'] = data['id']/ 109324

    respuesta = {}
    #conuslta para obtener el id del cv
    id_cv = db.executesql(f"SELECT id_estudiante_cv FROM bt_estudiante_cv WHERE id_usuario = {auth.user.id}", as_dict=True)
    get_id_cv = id_cv[0]['id_estudiante_cv']

    #insert para registrar cv a oferta laboral
    buscar = f"SELECT * FROM bt_estudiante_oferta WHERE id_estudiante_cv = {get_id_cv}"
    res_buscar = db.executesql(buscar, as_dict=True)
    query = f"""
        INSERT INTO 
            bt_estudiante_oferta (
                id_estudiante_cv,
                id_oferta_laboral,
                id_estado_aplicacion
            )
        VALUES (
            '{get_id_cv}',
            '{data['id']}',
            1
        );
    """
    if len(res_buscar) > 0:
        if int(res_buscar[0]['id_estado_aplicacion']) > 5:
            query = f"UPDATE bt_estudiante_oferta SET id_estado_aplicacion = 1 WHERE id_estudiante_cv = {get_id_cv}"
    try:
        db.executesql(query)
        respuesta["msg"] = "CV registrado con exito"
        respuesta["success"] = True
    except:
        respuesta["msg"] = "Ya se envió solicitud a esta oferta"
        respuesta["success"] = False

    return json.dumps(respuesta)

def eliminar_solicitud():
    data = json.loads(request.post_vars.array)
     
    respuesta = {}
    db.executesql(f"DELETE FROM bt_estudiante_oferta WHERE id_estudiante_cv = {data['id_cv']} AND id_oferta_laboral = {data['id_oferta']}")
    respuesta["msg"] = "Solicitud eliminada"
    respuesta["success"] = True
     
    return json.dumps(respuesta)   