import math 
import json
import uuid
import base64
import os

@auth.requires_login()
@auth.requires_membership('Empresa')
def buscar_aplicantes():
    new_dict = {}
    params = request.get_vars
    
    offset = 0
    limit = 10

    # Obtener parametros para poder manejar paginacion y busqueda si es que la hace
    page = 1
    if 'page' in params:
        page = int(params["page"])
        offset = (page - 1) * limit
    
    edad = 0
    if 'edad' in params:
        try:
            edad = int(params["edad"])
        except:
            ...

    creditos = 0
    if 'creditos' in params:
        try:
            creditos = int(params["creditos"])
        except:
            ...
    
    id_oferta = int(params["id_oferta"]) if 'id_oferta' in params else 0 
    nombre = f"%{params['nombre']}%" if 'nombre' in params else ''
    orderby = params["orderby"] if 'orderby' in params else 'id_estudiante_cv'
        
    # prueba de seguridad
    try:
        consulta = f'''
            SELECT 
                ol.id_oferta_laboral,
                ol.id_empresa,
                au.id
            FROM bt_oferta_laboral AS ol
                INNER JOIN bt_empresa AS e USING(id_empresa)
                INNER JOIN auth_user AS au ON e.id_usuario = au.id
            WHERE 
                id_oferta_laboral = {id_oferta}
                AND au.id = {auth.user.id};
        '''
        result = db.executesql(consulta, as_dict=True)
        if not len(result) > 0:
            redirect(URL('cpfecys', 'oferta_laboral', 'error'))
    except:
        redirect(URL('cpfecys', 'oferta_laboral', 'error'))

    try:
        columnas = '''
            SELECT
                cv.id_estudiante_cv,
                CONCAT(CONCAT(a.first_name, " "), a.last_name) AS nombre,
                TIMESTAMPDIFF(YEAR, fecha_nacimiento, CURDATE()) AS edad,
		        cv.creditos_aprobados,
                ee.id_area_especialidad,
        '''
        resto1 = '''
                0 AS estado_aplicacion
            FROM bt_estudiante_cv AS cv
                INNER JOIN auth_user AS a ON cv.id_usuario = a.id
                INNER JOIN bt_estudiante_especialidad AS ee USING(id_estudiante_cv)
                INNER JOIN bt_oferta_laboral AS ol ON ol.id_oferta_laboral = %(id_oferta)s
                        AND ol.id_area_especialidad = ee.id_area_especialidad
                        AND ee.id_estado_visibilidad = 2
            WHERE NOT EXISTS (
                SELECT * 
                FROM bt_estudiante_oferta AS eo
                WHERE (
                    eo.id_estudiante_cv = cv.id_estudiante_cv 
                    AND eo.id_oferta_laboral = %(id_oferta)s
                )
            )
            UNION
        '''
        resto2 = '''
                eo.id_estado_aplicacion AS estado_aplicacion 
            FROM bt_estudiante_cv AS cv
                INNER JOIN auth_user AS a ON cv.id_usuario = a.id
                INNER JOIN bt_estudiante_especialidad AS ee USING(id_estudiante_cv)
                INNER JOIN bt_estudiante_oferta AS eo USING(id_estudiante_cv)
                INNER JOIN bt_oferta_laboral AS ol USING(id_oferta_laboral)
                WHERE 
                    eo.id_estado_aplicacion <> 5
                    AND eo.id_estado_aplicacion < 7
                    AND eo.id_oferta_laboral = %(id_oferta)s
                    AND ol.id_area_especialidad = ee.id_area_especialidad
                    AND ee.id_estado_visibilidad = 2
        '''
        # buscar aplicantes para una oferta especifica que no hayan aplicado a ella antes
        subquery = columnas + resto1 + columnas + resto2
        query = f'''
            SELECT * 
            FROM ({subquery}) AS sub
            WHERE id_estudiante_cv > 0
        '''
        query_cantidad = f'''
            SELECT COUNT(*) AS cantidad 
            FROM ({subquery}) AS sub
            WHERE id_estudiante_cv > 0
        '''

        # Si filtra por creditos
        if creditos != 0 and creditos != "":
            query += ' AND creditos_aprobados >= %(creditos)s '
            query_cantidad += ' AND creditos_aprobados >= %(creditos)s '

        # Si filtra por edad
        if edad != 0 and edad != "":
            query += ' AND edad >= %(edad)s '
            query_cantidad += ' AND edad >= %(edad)s '

        # Si filtra por nombre del estudiante
        if nombre != "":
            query += f' AND nombre LIKE "%{nombre}%" '
            query_cantidad += f' AND nombre LIKE "%{nombre}%" '

        params = {
            'id_oferta': id_oferta,
            'creditos': creditos,
            'edad': edad,
            'orderby': orderby,
            'offset': offset,
            'limit': limit
        }
        result = db.executesql(query, params, as_dict=True)
        new_dict["aplicantes"] = result
        result = db.executesql(query_cantidad, params, as_dict=True)
        new_dict["cantidad_aplicantes"] = result[0]["cantidad"]
        new_dict["cantidad_paginas"]  = int(math.ceil(float(result[0]["cantidad"]) / limit))
        new_dict["inicio_aplicantes"] = int(offset) + 1
        fin = int(offset) + limit
        if fin > new_dict["cantidad_aplicantes"]:
            new_dict["fin_aplicantes"] = new_dict["cantidad_aplicantes"]
        else:
            new_dict["fin_aplicantes"] = int(offset) + limit

        #Enviamos los parametros para utilizarlos al cambiar de pagina
        new_dict["next_page"] = page + 1
        new_dict["prev_page"] = page - 1
        new_dict["page"] = page
        new_dict["id_oferta"] = id_oferta
        new_dict["creditos"] = creditos
        new_dict["edad"] = edad
        new_dict["nombre"] = nombre.replace("%","")
        new_dict["orderby"] = orderby
    except:
        ...

    return dict(new_dict=new_dict)

def datos_aplicante():
    try:       
        data = request.vars
        id_usuario_cv = data['id_usuario']
        id_oferta = data['id_oferta']
        
        # prueba de seguridad
        try:
            consulta = f'''
                SELECT 
                    ol.id_oferta_laboral,
                    ol.id_empresa,
                    au.id
                FROM bt_oferta_laboral AS ol
                    INNER JOIN bt_empresa AS e USING(id_empresa)
                    INNER JOIN auth_user AS au ON e.id_usuario = au.id
                WHERE 
                    id_oferta_laboral = {id_oferta}
                    AND au.id = {auth.user.id};
            '''
            result = db.executesql(consulta, as_dict=True)
            if not len(result) > 0:
                redirect(URL('cpfecys', 'oferta_laboral', 'error'))
        except:
            redirect(URL('cpfecys', 'oferta_laboral', 'error'))

        qs = f'SELECT id_usuario, creditos_aprobados FROM bt_estudiante_cv WHERE id_estudiante_cv = {id_usuario_cv};'
        id_user = db.executesql(qs, as_dict=True)[0]['id_usuario']
        query_estado = f'''
            SELECT 
                eo.id_estado_aplicacion,
                eof.estado_aplicacion
            FROM bt_estudiante_oferta AS eo 
                INNER JOIN bt_estado_aplicacion AS eof ON eo.id_estado_aplicacion = eof.id_estado_aplicacion 
            WHERE 
                id_estudiante_cv = {id_usuario_cv} 
                AND eo.id_oferta_laboral = {id_oferta};
        '''
        query_datos = f'''
            SELECT
                first_name,
                last_name,
                email,
                phone
            FROM auth_user AS a
                INNER JOIN bt_estudiante_cv AS cv ON cv.id_usuario = a.id
            WHERE a.id = {id_user};
        '''
        query_cv = f'''
            SELECT 
                cv.*,
                TIMESTAMPDIFF(YEAR, fecha_nacimiento, CURDATE()) AS edad
            FROM bt_estudiante_cv AS cv 
            WHERE id_estudiante_cv = {id_usuario_cv};
        '''
        query_areas = f'''
            SELECT
                est.id_area_especialidad,
                area.area_especialidad
            FROM bt_area_especialidad AS area
                INNER JOIN bt_estudiante_especialidad AS est ON area.id_area_especialidad = est.id_area_especialidad
                INNER JOIN bt_estudiante_cv AS cv ON est.id_estudiante_cv = cv.id_estudiante_cv
            WHERE cv.id_estudiante_cv = {id_usuario_cv};
        '''
        query_certificaciones = f'''
            SELECT 
                id_certificacion,
                nombre_certificacion,
                enlace,
                fecha_expedicion,
                tipo
            FROM bt_certificacion 
            WHERE id_estudiante_cv = {id_usuario_cv};
        '''
        query_habilidades = f'''
            SELECT
                hab.id_habilidad,
                hab.habilidad
            FROM bt_estudiante_habilidad AS est
                INNER JOIN bt_habilidad AS hab ON est.id_habilidad = hab.id_habilidad
            WHERE est.id_estudiante_cv = {id_usuario_cv};
        '''
        query_experiencia = f'''
            SELECT
                id_experiencia,
                puesto,
                empresa,
                fecha_inicio,
                IFNULL(fecha_fin, "Presente") AS fecha_fin,
                descripcion
            FROM bt_experiencia_laboral AS ex 
                INNER JOIN bt_estudiante_cv AS es ON ex.id_estudiante_cv = es.id_estudiante_cv 
            WHERE es.id_estudiante_cv = {id_usuario_cv};
        '''
        estado_aplicacion = db.executesql(query_estado, as_dict=True)
        datos_user = db.executesql(query_datos, as_dict=True)
        datos_cv = db.executesql(query_cv, as_dict=True)
        areas_est = db.executesql(query_areas, as_dict=True)
        certificaciones = db.executesql(query_certificaciones, as_dict=True)
        habilidades_usuario = db.executesql(query_habilidades, as_dict=True)
        experiencia_lab = db.executesql(query_experiencia, as_dict=True)
        creditos = db.executesql(qs, as_dict=True)[0]['creditos_aprobados']
        return dict(
            experiencia_lab=experiencia_lab,
            datos_user=datos_user[0],
            datos_cv=datos_cv[0],
            areas_est=areas_est,
            activo=1,
            certificaciones=certificaciones,
            habilidades_usuario=habilidades_usuario,
            estado_aplicacion=estado_aplicacion[0],
            id_oferta=id_oferta,
            creditos_aprobados=creditos
        )
    except:
        return dict(
            datos_user={},
            datos_cv={},
            areas_est=[],
            activo=1,
            certificaciones=[],
            habilidades_usuario=[],
            estado_aplicacion={},
            creditos_aprobados=0
        ) 

def datos_aplicante_b():
    try:       
        data = request.vars
        id_usuario_cv = data['id_usuario']
        id_oferta = data['id_oferta']

        # prueba de seguridad
        try:
            # para no ver ofertas de otras empresas
            consulta = f'''
                SELECT
                    ol.id_oferta_laboral,
                    ol.id_empresa,
                    au.id
                FROM bt_oferta_laboral AS ol
                    INNER JOIN bt_empresa AS e USING(id_empresa)
                    INNER JOIN auth_user AS au ON e.id_usuario = au.id
                WHERE 
                    id_oferta_laboral = {id_oferta}
                    AND au.id = {auth.user.id};
            '''
            result = db.executesql(consulta, as_dict=True)
            if not len(result) > 0:
                redirect(URL('cpfecys', 'oferta_laboral', 'error'))

            # para no ver cvs de estudiantes que prefieren tenerlo privado a esas especialidades
            consulta = f'''
                SELECT 
                    ol.id_oferta_laboral,
                    ol.id_area_especialidad
                FROM bt_oferta_laboral AS ol
                    INNER JOIN bt_estudiante_especialidad AS ee USING(id_area_especialidad)
                    INNER JOIN bt_estudiante_cv AS cv USING(id_estudiante_cv)
                WHERE 
                    ee.id_estado_visibilidad = 2
                    AND cv.id_estudiante_cv  = {id_usuario_cv}
                    AND ol.id_oferta_laboral = {id_oferta};
            '''
            result = db.executesql(consulta, as_dict=True)
            if not len(result) > 0:
                redirect(URL('cpfecys', 'oferta_laboral', 'error'))
            
        except:
            redirect(URL('cpfecys', 'oferta_laboral', 'error'))

        qs = f'SELECT id_usuario, creditos_aprobados FROM bt_estudiante_cv WHERE id_estudiante_cv = {id_usuario_cv};'
        id_user = db.executesql(qs,as_dict=True)[0]['id_usuario']
        query_user = f'''
            SELECT
                first_name,
                last_name,
                email,
                phone 
            FROM auth_user AS a 
                INNER JOIN bt_estudiante_cv AS cv ON cv.id_usuario = a.id 
            WHERE a.id = {id_user};
        '''
        query_cv = f'''
            SELECT
                cv.*,
                TIMESTAMPDIFF(YEAR, fecha_nacimiento, CURDATE()) AS edad 
            FROM bt_estudiante_cv AS cv 
            WHERE id_estudiante_cv = {id_usuario_cv};
        '''
        query_areas = f'''
            SELECT 
                est.id_area_especialidad,
                area.area_especialidad
            FROM bt_area_especialidad AS area
                INNER JOIN bt_estudiante_especialidad AS est ON area.id_area_especialidad = est.id_area_especialidad
                INNER JOIN bt_estudiante_cv AS cv ON est.id_estudiante_cv = cv.id_estudiante_cv 
            WHERE cv.id_estudiante_cv = {id_usuario_cv};
        '''
        query_certificaciones = f'''
            SELECT 
                id_certificacion,
                nombre_certificacion,
                enlace,
                fecha_expedicion,
                tipo
            FROM bt_certificacion
            WHERE id_estudiante_cv = {id_usuario_cv};
        '''
        query_habilidades = f'''
            SELECT 
                hab.id_habilidad,
                hab.habilidad
            FROM bt_estudiante_habilidad AS est
                INNER JOIN  bt_habilidad AS hab ON est.id_habilidad = hab.id_habilidad
            WHERE est.id_estudiante_cv = {id_usuario_cv};
        '''
        query_experiencia = f'''
            SELECT 
                id_experiencia,
                puesto,
                empresa,
                fecha_inicio,
                IFNULL(fecha_fin, "Presente") AS fecha_fin,
                descripcion
            FROM bt_experiencia_laboral AS ex
                INNER JOIN bt_estudiante_cv AS es ON ex.id_estudiante_cv = es.id_estudiante_cv
            WHERE es.id_estudiante_cv = {id_usuario_cv};
        '''
        datos_user = db.executesql(query_user, as_dict=True)
        datos_cv = db.executesql(query_cv, as_dict=True)
        areas_est = db.executesql(query_areas, as_dict=True)
        certificaciones = db.executesql(query_certificaciones, as_dict=True)
        habilidades_usuario = db.executesql(query_habilidades, as_dict=True)
        experiencia_lab = db.executesql(query_experiencia, as_dict=True)
        creditos = db.executesql(qs, as_dict=True)[0]['creditos_aprobados']
        return dict(
            experiencia_lab=experiencia_lab,
            datos_user=datos_user[0],
            datos_cv=datos_cv[0],
            areas_est=areas_est,
            activo=1,
            certificaciones=certificaciones,
            habilidades_usuario=habilidades_usuario,
            id_oferta=id_oferta,
            creditos_aprobados=creditos
        )
    except:
        return dict(
            datos_user={},
            datos_cv={},
            areas_est=[],
            activo=1,
            certificaciones=[],
            habilidades_usuario=[],
            creditos_aprobados=0
        ) 

@auth.requires_login()
@auth.requires_membership('Empresa')
def editar_oferta():
    new_dict={}
    params = request.get_vars
    id = 0

    # Si viene el id de la empresa muestra los datos, sino lo redirije a la lista de empresas
    if 'id' in params:
        id = params["id"]
    else:
        redirect(URL('cpfecys', 'oferta_laboral', 'seguimiento_ofertas'))

    # Verificacion de seguridad
    # para no ver ofertas de otras empresas
    consulta = f'''
        SELECT id_empresa 
        FROM bt_empresa
            INNER JOIN bt_oferta_laboral USING(id_empresa)
        WHERE 
            id_usuario = {auth.user.id}
            AND id_oferta_laboral = {id};
    '''
    resultado = db.executesql(consulta, as_dict=True)
    if not len(resultado) > 0:
        redirect(URL('cpfecys', 'oferta_laboral', 'error'))  

    try:
        query = '''
            SELECT 
                ol.*,
                py.*,
                e.nombre_empresa,
                e.telefono,
                eol.estado_oferta_laboral,
                ae.area_especialidad
            FROM bt_oferta_laboral AS ol
                INNER JOIN period_year AS py ON ol.id_period_year = py.id
                INNER JOIN bt_empresa AS e ON ol.id_empresa = e.id_empresa
                INNER JOIN bt_estado_oferta_laboral AS eol ON ol.id_estado_oferta_laboral = eol.id_estado_oferta_laboral
                INNER JOIN bt_area_especialidad AS ae ON ol.id_area_especialidad = ae.id_area_especialidad
            WHERE id_oferta_laboral = %(id)s;
        '''
        result = db.executesql(query, {'id':id}, as_dict=True)
        new_dict["trabajo"] = result

        result = db.executesql('SELECT * FROM bt_area_especialidad', as_dict=True)
        new_dict["area_especialidad"] = result

        result = db.executesql('SELECT * FROM bt_estado_oferta_laboral', as_dict=True)
        new_dict["estados_registro"] = result

        tamanio_imagen = db.executesql('SELECT tamanio_banner FROM bt_tamanio_archivo LIMIT 1;', as_dict=True)[0]['tamanio_banner']
        new_dict["tamanio_imagen"] = tamanio_imagen
    except:
        redirect(URL('cpfecys', 'oferta_laboral', 'seguimiento_ofertas'))

    if len(new_dict["trabajo"]) == 0:
        redirect(URL('cpfecys', 'oferta_laboral', 'seguimiento_ofertas'))
    else:
        new_dict["trabajo"] = new_dict["trabajo"][0]
    
    return dict(new_dict=new_dict)

@auth.requires_login()
@auth.requires_membership('Empresa')
def editar_empresa():
    new_dict={}
    id = 0
    try:
        id = str(auth.user.id)
        emp = f'SELECT id_empresa FROM bt_empresa WHERE id_usuario = {id}'
        resultado = db.executesql(emp, as_dict=True)
        id = resultado[0]['id_empresa']

        query = '''
            SELECT 
                e.*,
                s.estado_registro
            FROM bt_empresa AS e
                INNER JOIN bt_estado_registro AS s ON e.id_estado_registro = s.id_estado_registro
            WHERE id_empresa = %(id)s;
        '''
        result = db.executesql(query, {'id':id}, as_dict=True)
        new_dict["empresa"] = result

        query = 'SELECT * FROM bt_estado_registro'
        result = db.executesql(query, as_dict=True)
        new_dict["estados_registro"] = result
    except:
        redirect(URL('default','home'))

    if len(new_dict["empresa"]) == 0:
        redirect(URL('default','home'))
    else:
        new_dict["empresa"] = new_dict["empresa"][0]
    
    return dict(new_dict=new_dict)

@auth.requires_login()
@auth.requires_membership('Empresa')
def oferta_laboral():
    try:
        areas_es = db.executesql('SELECT * FROM bt_area_especialidad;', as_dict=True)
        query_habilidades = '''
            SELECT * 
            FROM bt_habilidad 
            WHERE id_area_especialidad = (
                SELECT MIN(id_area_especialidad) 
                FROM bt_area_especialidad
            );
        '''
        habilidades = db.executesql(query_habilidades, as_dict=True)
        todas_habilidades = db.executesql("SELECT * FROM bt_habilidad;", as_dict=True)
        tamanio_imagen = db.executesql('SELECT tamanio_banner FROM bt_tamanio_archivo LIMIT 1;', as_dict=True)[0]['tamanio_banner']
    except:
        areas_es = []
        habilidades = []
        todas_habilidades = []
        tamanio_imagen = 3048576

    return dict(
        areas_es=areas_es,
        habilidades=habilidades,
        todas_habilidades=todas_habilidades,
        tamanio_imagen=tamanio_imagen
    )        

@auth.requires_login()
@auth.requires_membership('Empresa')
def seguimiento_ofertas():
    new_dict = {}

    params = request.get_vars


    offset = 0
    limit = 10
    qs = f'SELECT id_empresa FROM bt_empresa WHERE id_usuario = {auth.user.id};'
    id_empresa = db.executesql(qs,as_dict=True)[0]['id_empresa']

    if 'periodo' in params:
        periodo = int(params["periodo"])
    else:
        try:
            periodo = db.executesql('SELECT MAX(id) AS id FROM period_year;', as_dict=True)[0]['id']
        except Exception as e:
            periodo = 0

    # Obtener parametros para poder manejar paginacion y busqueda si es que la hace
    page = 1
    if 'page' in params:
        page = int(params["page"])
        offset = (page - 1) * limit
        
    area = int(params["area"]) if 'area' in params else 0
    status = int(params["status"]) if 'status' in params else 0
    puesto = f"%{params['puesto']}%" if 'puesto' in params else ''
    orderby = params["orderby"] if 'orderby' in params else 'id_oferta_laboral'
        

    try:
        # si es busqueda por status se agrega al query
        query = '''
            SELECT
                ol.*,
                py.*,
                e.nombre_empresa,
                eol.estado_oferta_laboral,
                ae.area_especialidad
            FROM bt_oferta_laboral AS ol
                INNER JOIN period_year py ON ol.id_period_year = py.id
                INNER JOIN bt_empresa e ON ol.id_empresa = e.id_empresa
                INNER JOIN bt_estado_oferta_laboral eol ON ol.id_estado_oferta_laboral = eol.id_estado_oferta_laboral
                INNER JOIN bt_area_especialidad ae ON ol.id_area_especialidad = ae.id_area_especialidad
        '''
        query_cantidad = 'SELECT COUNT(*) AS cantidad FROM bt_oferta_laboral'

        # Si filtra por empresa
        if id_empresa != 0:
            query += ' WHERE ol.id_empresa = %(id_empresa)s '
            query_cantidad += ' WHERE id_empresa = %(id_empresa)s '

        # Si filtra por area
        if area != 0:
            query += ' AND ol.id_area_especialidad = %(area)s '
            query_cantidad += ' AND id_area_especialidad = %(area)s '

        # Si filtra por periodo
        if periodo != 0:
            query += ' AND ol.id_period_year = %(periodo)s '
            query_cantidad += ' AND id_period_year = %(periodo)s '

        # Si filtra por Estado de Oferta Laboral
        if status != 0:
            query += ' AND ol.id_estado_oferta_laboral = %(status)s '
            query_cantidad += ' AND id_estado_oferta_laboral = %(status)s '
        
        # Si filtra por nombre del puesto
        if puesto != "":
            query += f' AND ol.puesto LIKE "%{puesto}%"'
            query_cantidad += f' AND puesto LIKE "%{puesto}%"'

        query += 'ORDER BY %(orderby)s LIMIT %(offset)s, %(limit)s'
        params = {
            'id_empresa': id_empresa,
            'area': area,
            'periodo': periodo,
            'status': status,
            'orderby': orderby,
            'offset': offset,
            'limit': limit
        }
        result = db.executesql(query, params, as_dict=True)
        new_dict["trabajos"] = result

        query = 'SELECT id_empresa, nombre_empresa FROM bt_empresa WHERE id_estado_registro = 2'
        result = db.executesql(query, as_dict=True)
        new_dict["empresas"] = result

        query = 'SELECT * FROM bt_area_especialidad'
        result = db.executesql(query, as_dict=True)
        new_dict["area_especialidad"] = result
        
        query = 'SELECT * FROM period_year ORDER BY id DESC'
        result = db.executesql(query, as_dict=True)
        new_dict["periodos"] = result
    
        query = 'SELECT * FROM bt_estado_oferta_laboral'
        result = db.executesql(query, as_dict=True)
        new_dict["estados_registro"] = result

        result = db.executesql(query_cantidad, params, as_dict=True)
        new_dict["cantidad_empresas"] = result[0]["cantidad"]
        new_dict["cantidad_paginas"]  = int(math.ceil(float(result[0]["cantidad"]) / limit))
        new_dict["inicio_empresas"] = int(offset) + 1
        fin = int(offset) + limit
        if fin > new_dict["cantidad_empresas"]:
            new_dict["fin_empresas"] = new_dict["cantidad_empresas"]
        else:
            new_dict["fin_empresas"] = int(offset) + limit

        #Enviamos los parametros para utilizarlos al cambiar de pagina
        new_dict["next_page"] = page + 1
        new_dict["prev_page"] = page - 1
        new_dict["page"] = page
        new_dict["id_empresa"] = id_empresa
        new_dict["area"] = area
        new_dict["periodo"] = periodo
        new_dict["puesto"] = puesto.replace("%","")
        new_dict["orderby"] = orderby
        new_dict["status"] = status
    except:
        new_dict["empresas"] = []
        new_dict["estados_registro"] = []

    return dict(new_dict=new_dict)

@auth.requires_login()
@auth.requires_membership('Empresa')
def view_aplicantes():
    new_dict = {}

    params = request.get_vars

    # Obtener parametros para poder manejar paginacion y busqueda si es que la hace
    page = 1
    offset = 0
    limit = 10
    if 'page' in params:
        page = int(params["page"])
        offset = (page - 1) * limit

    id_oferta = int(params["id_oferta"]) if 'id_oferta' in params else 0
    nombre = f"%{params['nombre']}%" if 'nombre' in params else ''
    orderby = params["orderby"] if 'orderby' in params else 'id_estudiante_cv'    

    edad = 0
    if 'edad' in params:
        try:
            edad = int(params["edad"])
        except:
            ...

    creditos = 0
    if 'creditos' in params:
        try:
            creditos = int(params["creditos"])
        except:
            ...        
    
    # prueba de seguridad
    try:
        consulta = f'''
            SELECT 
                ol.id_oferta_laboral,
                ol.id_empresa,
                au.id
            FROM bt_oferta_laboral AS ol
                INNER JOIN bt_empresa AS e USING(id_empresa)
                INNER JOIN auth_user AS au ON e.id_usuario = au.id
            WHERE 
                id_oferta_laboral = {id_oferta}
                AND au.id = {auth.user.id};
        '''
        result = db.executesql(consulta, as_dict=True)
        if not len(result) > 0:
            redirect(URL('cpfecys', 'oferta_laboral', 'error'))
    except:
        redirect(URL('cpfecys', 'oferta_laboral', 'error'))

    try:
        # si es busqueda por status se agrega al query
        query = '''
            SELECT 
                cv.*,
                TIMESTAMPDIFF(YEAR, fecha_nacimiento, CURDATE()) AS edad,
                CONCAT(CONCAT(first_name, " "), last_name) AS nombre,
                ea.estado_aplicacion AS estado_aplicacion,
                ef.id_estado_aplicacion AS id_estado_aplicacion
            FROM bt_estudiante_cv AS cv
                INNER JOIN bt_estudiante_oferta AS ef ON cv.id_estudiante_cv = ef.id_estudiante_cv 
                INNER JOIN auth_user AS a ON cv.id_usuario = a.id 
                INNER JOIN bt_estado_aplicacion AS ea ON ef.id_estado_aplicacion = ea.id_estado_aplicacion
            WHERE ea.id_estado_aplicacion <> 6
        '''
        query_cantidad = '''
            SELECT COUNT(*) AS cantidad 
            FROM bt_estudiante_cv AS cv
                INNER JOIN bt_estudiante_oferta AS ef ON cv.id_estudiante_cv = ef.id_estudiante_cv 
                INNER JOIN auth_user AS a ON cv.id_usuario = a.id 
                INNER JOIN bt_estado_aplicacion AS ea ON ef.id_estado_aplicacion = ea.id_estado_aplicacion
            WHERE ea.id_estado_aplicacion <> 6
        '''

        # Si filtra por oferta
        if id_oferta != 0 and id_oferta != "":
            query += ' AND ef.id_oferta_laboral = %(id_oferta)s '
            query_cantidad += ' AND ef.id_oferta_laboral = %(id_oferta)s '

        # Si filtra por creditos
        if creditos != 0 and creditos != "":
            query += ' AND cv.creditos_aprobados >= %(creditos)s '
            query_cantidad += ' AND cv.creditos_aprobados >= %(creditos)s '

        # Si filtra por edad
        if edad != 0 and edad != "":
            query += ' AND TIMESTAMPDIFF(YEAR, fecha_nacimiento, CURDATE()) >= %(edad)s '
            query_cantidad += ' AND TIMESTAMPDIFF(YEAR, fecha_nacimiento, CURDATE()) >= %(edad)s '

        # Si filtra por nombre del estudiante
        if nombre != "":
            query += f' AND CONCAT(CONCAT(first_name, " "), last_name) LIKE "%{nombre}%" '
            query_cantidad += f' AND CONCAT(CONCAT(first_name, " "), last_name) LIKE "%{nombre}%" '

        params = {
            'id_oferta': id_oferta,
            'creditos': creditos,
            'edad': edad,
            'orderby': orderby,
            'offset': offset,
            'limit': limit
        }
        result = db.executesql(query, params, as_dict=True)
        new_dict["aplicantes"] = result
        result = db.executesql(query_cantidad, params, as_dict=True)
        new_dict["cantidad_aplicantes"] = result[0]["cantidad"]
        new_dict["cantidad_paginas"]  = int(math.ceil(float(result[0]["cantidad"]) / limit))
        new_dict["inicio_aplicantes"] = int(offset) + 1
        fin = int(offset) + limit
        if fin > new_dict["cantidad_aplicantes"]:
            new_dict["fin_aplicantes"] = new_dict["cantidad_aplicantes"]
        else:
            new_dict["fin_aplicantes"] = int(offset) + limit

        #Enviamos los parametros para utilizarlos al cambiar de pagina
        new_dict["next_page"] = page + 1
        new_dict["prev_page"] = page - 1
        new_dict["page"] = page
        new_dict["id_oferta"] = id_oferta
        new_dict["creditos"] = creditos
        new_dict["edad"] = edad
        new_dict["nombre"] = nombre.replace("%","")
        new_dict["orderby"] = orderby
    except:
        ...

    return dict(new_dict=new_dict)

@auth.requires_login()
@auth.requires_membership('Empresa')
def view_oferta():
    new_dict = {}

    params = request.get_vars
    id = 0

    # Si viene el id del trabajo muestra los datos, sino lo redirije a la lista de trabajos
    if 'id' in params:
        id = params["id"]
    else:
        redirect(URL('cpfecys', 'oferta_laboral', 'seguimiento_ofertas'))

    # Verificacion de seguridad
    # para no ver ofertas de otras empresas
    consulta = f'''
        SELECT id_empresa 
        FROM bt_empresa
            INNER JOIN bt_oferta_laboral USING(id_empresa)
        WHERE 
            id_usuario = {auth.user.id}
            AND id_oferta_laboral = {id};
    '''
    resultado = db.executesql(consulta, as_dict=True)
    if not len(resultado) > 0:
        redirect(URL('cpfecys', 'oferta_laboral', 'error'))            

    try:
        query = '''
            SELECT 
                ol.*,
                py.*,
                e.nombre_empresa,
                e.telefono,
                eol.estado_oferta_laboral,
                ae.area_especialidad
            FROM bt_oferta_laboral AS ol
                INNER JOIN period_year AS py ON ol.id_period_year = py.id 
                INNER JOIN bt_empresa AS e ON ol.id_empresa = e.id_empresa
                INNER JOIN bt_estado_oferta_laboral AS eol ON ol.id_estado_oferta_laboral = eol.id_estado_oferta_laboral
                INNER JOIN bt_area_especialidad AS ae ON ol.id_area_especialidad = ae.id_area_especialidad
            WHERE id_oferta_laboral = %(id)s
            ORDER BY id_oferta_laboral;
        '''
        result = db.executesql(query, {'id':id}, as_dict=True)
        new_dict["trabajo"] = result
    except:
        redirect(URL('cpfecys', 'oferta_laboral', 'seguimiento_ofertas'))

    #Si no se encontro ningun resultado lo redirije a la lista de trabajos
    if len(new_dict["trabajo"]) == 0:
        redirect(URL('cpfecys', 'oferta_laboral', 'seguimiento_ofertas'))
    else:
        new_dict["trabajo"] = new_dict["trabajo"][0]

    return dict(new_dict=new_dict)

def actualizar_empresa():
    # Si el metodo es post significa que es un registro
    if request.ajax:
        respuesta = {}
        db.executesql("START TRANSACTION;")
        try:
            #Obtener el body del request
            data = json.loads(request.post_vars.array)
            # Verificar que no exista ya una empresa registrada
            result = db.executesql(f"SELECT * FROM bt_empresa WHERE id_empresa = '{data['id_empresa']}'", as_dict=True)

            if len(result) == 0:
                respuesta["success"] = False
                respuesta["msg"] = "Empresa no registrada"
                db.executesql("ROLLBACK")
                return json.dumps(respuesta)

            #Guardar los datos de empresa encontrada
            empresa = result[0]
            
            #Si le actualizaron el correo
            if result[0]["correo"] != data["correo"]:
                #Verificar que no exista un usuario con ese correo
                result1 = db.executesql(f"SELECT * FROM auth_user WHERE email = '{data['correo']}'", as_dict=True)
                if len(result1) > 0:
                    respuesta["success"] = False
                    respuesta["msg"] = "Este correo ya está en uso"
                    db.executesql("ROLLBACK")
                    return json.dumps(respuesta)

            #Guardar datos del usuario
            usuario = empresa["id_usuario"]

            if "sha512" not in data["password"]:
                data["password"] = CRYPT()(str(data["password"]).encode('utf8'))[0]

            # Se actualiza datos de usuario
            query = """
                UPDATE auth_user 
                SET
                    first_name = %(nombre_empresa)s,
                    email = %(correo)s,
                    username = %(username)s,
                    password = %(password)s 
                WHERE id = %(id)s
            """
            params = {
                'nombre_empresa': data["nombre_empresa"],
                'correo': data["correo"],
                'username': data["correo"],
                'password': str(data["password"]),
                'id': usuario
            }
            db.executesql(query, params)

            # Se actualiza datos de empresa
            query = f"""
                UPDATE bt_empresa 
                SET 
                    nombre_empresa = '{data['nombre_empresa']}',
                    direccion = '{data['direccion']}',
                    telefono = '{data['telefono']}',
                    correo = %(correo)s, 
                    descripcion = '{data['descripcion']}',
                    pagina_web = '{data['pagina_web']}',
                    persona_encargada = %(persona_encargada)s, 
                    password = %(password)s 
                WHERE id_empresa = %(id_empresa)s;
            """
            params = {
                'correo': data["correo"],
                'persona_encargada': data["persona_encargada"],
                'id_empresa': empresa["id_empresa"],
                'password':  str(data["password"])
            }
            db.executesql(query, params)

            #Si el usuario se registro retorna mensaje que de success
            respuesta["success"] = True
            respuesta["msg"] = "Empresa actualizada"
            db.executesql("COMMIT")
            return json.dumps(respuesta)
        except Exception as e:
            db.executesql("ROLLBACK")
            respuesta["success"] = False
            respuesta["msg"] = e
            return json.dumps(respuesta)
    else:
        return json.dumps({'success': False, 'msg': 'Error'})

def guardar_oferta():
    data = request.vars
    puesto = data['puesto']
    descripcion = data['descripcion']
    requerimientos = data['requerimientos']
    salario = data['salario']
    fecha_inicio = data['fecha_inicio']
    fecha_fin = data['fecha_fin']
    area = data['area_especialidad']
    nombre_banner = str(data['nombre_banner']).replace(" ", "_")
    banner = data['documento_banner']

    try:
        uid = str(uuid.uuid4())
        db.executesql("START TRANSACTION;")
        id_empresa = db.executesql(f'SELECT id_empresa FROM bt_empresa WHERE id_usuario = {auth.user.id};', as_dict=True)[0]['id_empresa']
        id_period_year = db.executesql('SELECT MAX(id) AS id FROM period_year;', as_dict=True)[0]['id']
        qs = f'''
            INSERT INTO 
                bt_oferta_laboral (
                    puesto,
                    descripcion,
                    requerimientos,
                    salario_aproximado,
                    fecha_inicio,
                    fecha_vigencia,
                    banner,
                    id_period_year,
                    id_empresa,
                    id_estado_oferta_laboral,
                    id_area_especialidad
                ) 
            VALUES (
                "{puesto}",
                "{descripcion}",
                "{requerimientos}",
                {salario},
                "{fecha_inicio}",
                "{fecha_fin}",
                "{uid + nombre_banner}",
                {id_period_year},
                {id_empresa},
                1,
                {area});
        '''
        db.executesql(qs)
        
        documento = str(banner).partition(",")[2]
        bt_store_file(documento, uid + nombre_banner)
        db.executesql("COMMIT;")
    except Exception as ex:
        db.executesql("ROLLBACK;")
        return json.dumps({'success': False, 'msg': ex})
    
    return json.dumps({'success': True, 'msg': 'Oferta registrada'})

def bt_store_file(base64_param, filename=None, path=None):
    bytes = base64.b64decode(base64_param)
    path = os.path.join(request.folder, "static/bolsa_trabajo/ofertas/")
    if not os.path.exists(path): os.makedirs(path)

    pathfilename = os.path.join(path, filename)
    dest_file = open(pathfilename, 'wb')
    try:
         dest_file.write(bytes)
    finally:
        dest_file.close()
    
    return filename

def actualizar_trabajo():
    # Si el metodo es post significa que es un registro
    if request.ajax:
        respuesta = {}
        db.executesql("START TRANSACTION;")
        try:
            data = request.vars
            # Verificar que no exista ya una oferta laboral registrada
            result = db.executesql("SELECT * FROM bt_oferta_laboral WHERE id_oferta_laboral = %(id)s", {'id': data['id_oferta']}, as_dict=True)
            if len(result) == 0:
                respuesta["success"] = False
                respuesta["msg"] = "Oferta laboral no registrada"
                db.executesql("ROLLBACK")
                return json.dumps(respuesta)

            if 'banner' in data:
                documento = str(data['banner']).partition(",")[2]
                filename = data['archivo']
                bt_store_file(documento, filename)

            #obtener correo de empresa
            result = db.executesql("SELECT * FROM bt_empresa WHERE id_empresa = %(id)s", {'id': data['empresa']}, as_dict=True)

            #Se actualiza oferta laboral
            query = f"""
                UPDATE bt_oferta_laboral
                SET 
                    puesto = '{data['puesto']}',
                    salario_aproximado = %(salario)s,
                    descripcion = '{data['descripcion']}',
                    requerimientos = '{data['requerimientos']}',
                    fecha_inicio = %(fecha_inicio)s,
                    fecha_vigencia = %(fecha_vigencia)s,
                    id_area_especialidad = %(area)s,
                    id_estado_oferta_laboral = %(estado)s,
                    motivo_rechazo = '{data['motivo']}'
                WHERE id_oferta_laboral = %(id_oferta)s;
            """
            params = {
                'salario': data["salario"],
                'fecha_inicio': data["fecha_inicio"],
                'fecha_vigencia': data["fecha_vigencia"],
                'area': data["area"],
                'estado': 1, 
                'id_oferta': data["id_oferta"]
            }
            db.executesql(query, params)

            #Si la oferta laboral si se actualiza
            respuesta["success"] = True
            respuesta["msg"] = "Oferta Laboral actualizada"
            db.executesql("COMMIT")
            return json.dumps(respuesta)
        except Exception as e:
            db.executesql("ROLLBACK")
            respuesta["success"] = False
            respuesta["msg"] = e
            return json.dumps(respuesta)
    else:
        return json.dumps({'success': False, 'msg': 'Error'})

def eliminar_trabajo():
    respuesta = {}
    db.executesql("START TRANSACTION;")

    try:
        #Obtener el body del request
        data = json.loads(request.post_vars.array)

        # Verificar que si exista ya una oferta laboral registrada
        result = db.executesql("SELECT * FROM bt_oferta_laboral WHERE id_oferta_laboral = %(id)s", {'id':data["id_oferta_laboral"]}, as_dict=True)
        if len(result) == 0:
            respuesta["success"] = False
            respuesta["msg"] = "Oferta Laboral no encontrada"
            db.executesql("ROLLBACK")
            return json.dumps(respuesta)

        # Se elimina el registro de la oferta laboral
        query = "DELETE FROM bt_oferta_laboral WHERE id_oferta_laboral = %(id)s"
        params = {'id': data["id_oferta_laboral"]}
        db.executesql(query, params)

        #Si el usuario se registro retorna mensaje que de success
        respuesta["success"] = True
        respuesta["msg"] = "Oferta Laboral eliminada"
        db.executesql("COMMIT")
    except Exception as e:
        respuesta["success"] = False
        respuesta["msg"] = e
        db.executesql("ROLLBACK")

    return json.dumps(respuesta)

def estado_proceso():
    try:
        data = request.vars
        id_estudiante = data['id_estudiante']
        id_oferta = data['id_oferta']
        finalizar = data['finalizar']
        db.executesql("START TRANSACTION;")
        qs = f"""
            SELECT id_estado_aplicacion
            FROM bt_estudiante_oferta
            WHERE 
                id_estudiante_cv = {id_estudiante} 
                AND id_oferta_laboral = {id_oferta};
        """
        id_estado = db.executesql(qs, as_dict=True)[0]['id_estado_aplicacion']
        qcorreo = f'''
            SELECT emp.correo 
            FROM bt_oferta_laboral AS ol 
                JOIN bt_empresa AS emp ON ol.id_empresa = emp.id_empresa 
            WHERE ol.id_oferta_laboral = {id_oferta};
        '''
        correo_emp = db.executesql(qcorreo, as_dict=True)[0]['correo']
        if finalizar == "0":
            if int(id_estado) > 3:
                return json.dumps({'success': False, 'msg': 'Se ha llegado a la fase final del proceso'})
            
            qs = f'''
                UPDATE bt_estudiante_oferta 
                SET 
                    id_estado_aplicacion = {id_estado + 1}
                WHERE 
                    id_estudiante_cv = {id_estudiante}
                    AND id_oferta_laboral = {id_oferta};
            '''
            db.executesql(qs)
            query_oferta = f"""
                SELECT 
                    puesto,
                    emp.nombre_empresa
                FROM bt_oferta_laboral AS of 
                    INNER JOIN bt_empresa AS emp ON of.id_empresa = emp.id_empresa 
                WHERE id_oferta_laboral = {id_oferta};
            """
            oferta = db.executesql(query_oferta, as_dict=True)[0]
            qs = f'''
                SELECT id_estado_aplicacion 
                FROM bt_estudiante_oferta 
                WHERE 
                    id_estudiante_cv = {id_estudiante}
                    AND id_oferta_laboral = {id_oferta};
            '''
            id_estado = db.executesql(qs, as_dict=True)[0]['id_estado_aplicacion']
            estado = db.executesql(f"SELECT estado_aplicacion FROM bt_estado_aplicacion WHERE id_estado_aplicacion = {id_estado};", as_dict=True)[0]
            
            subject = "Actualizacion de Estado de Solicitud de Empleo"
            correo = f"""
                <html>
                    Saludos cordiales,<br><br>
                    Por este medio se le informa que su aplicacion a la oferta laboral: 
                    <b>{oferta['puesto']}</b> de la empresa <b>{oferta['nombre_empresa']}</b>
                    ha recibido una actualización de estado <br><br>
                    Estado actual: <b> {estado['estado_aplicacion']} </b>
                    <br><br><br><br>
                    Sistema de Bolsa de Trabajo de La Escuela de Ciencias y Sistemas<br>
                    Facultad de Ingenier&iacute;a - Universidad de San Carlos de Guatemala
                </html>
            """
            enviar_correo(correo,data["correo"], correo_emp, subject)
            db.executesql("COMMIT;")
            return json.dumps({'success': True, 'msg': 'Estado Actualizado'})
        else:
            qs = f'''
                UPDATE bt_estudiante_oferta 
                SET id_estado_aplicacion = 5 
                WHERE 
                    id_estudiante_cv = {id_estudiante}
                    AND id_oferta_laboral = {id_oferta};
            '''
            db.executesql(qs)        
            query_oferta = f"""
                SELECT
                    puesto,
                    emp.nombre_empresa
                FROM bt_oferta_laboral AS of 
                    INNER JOIN bt_empresa AS emp ON of.id_empresa = emp.id_empresa
                WHERE id_oferta_laboral = {id_oferta};
            """
            oferta = db.executesql(query_oferta, as_dict=True)[0]
            qs = f'''
                SELECT id_estado_aplicacion
                FROM bt_estudiante_oferta
                WHERE 
                    id_estudiante_cv = {id_estudiante}
                    AND id_oferta_laboral = {id_oferta};
            '''
            id_estado = db.executesql(qs, as_dict=True)[0]['id_estado_aplicacion']     
            estado = db.executesql(f"SELECT estado_aplicacion FROM bt_estado_aplicacion WHERE id_estado_aplicacion = {id_estado}", as_dict=True)[0]
            subject = "Actualizacion de Estado de Solicitud de Empleo"
            correo = f"""
                <html>
                    Saludos cordiales,<br><br>
                    Por este medio se le informa que su aplicacion a la oferta laboral: 
                    <b>{oferta['puesto']}</b> de la empresa <b>{oferta['nombre_empresa']}</b>
                    ha recibido una actualizacion de estado <br><br>
                    Estado actual: <b> {estado['estado_aplicacion']} </b>
                    <br><br><br><br>
                    Sistema de Bolsa de Trabajo de La Escuela de Ciencias y Sistemas<br>
                    Facultad de Ingenier&iacute;a - Universidad de San Carlos de Guatemala
                </html>    
            """
            enviar_correo(correo,data["correo"], correo_emp, subject)
            db.executesql("COMMIT;")
            return json.dumps({'success': True, 'msg': 'Estado Actualizado'})            
    except Exception as ex:
        db.executesql("ROLLBACK;")
        return json.dumps({'success': False, 'msg': ex})
    
def enviar_correo(mensaje, destinatario, copia, subject):
    was_sent = mail.send(
                    to=[destinatario],
                    cc=[copia],
                    subject=subject,
                    message=mensaje,encoding='utf-8'
                )
    db.mailer_log.insert(
        sent_message=mensaje,
        destination=str(destinatario),
        result_log=f"{mail.error or ''}:{mail.result}",
        success = was_sent
    )
    
    return mensaje

def enviar_solicitud():
    try:
        data = request.vars
        id_estudiante = data['id_estudiante']
        id_oferta = data['id_oferta']
        db.executesql("START TRANSACTION;")
        qs = f'''
            SELECT id_estado_aplicacion
            FROM bt_estudiante_oferta 
            WHERE 
                id_estudiante_cv = {id_estudiante} 
                AND id_oferta_laboral = {id_oferta};
        '''
        qcorreo = f'''
            SELECT 
                emp.correo,
                ol.fecha_inicio,
                ol.fecha_vigencia,
                ol.fecha_vigencia > CURDATE() AS validacion
            FROM bt_oferta_laboral AS ol
                JOIN bt_empresa AS emp ON ol.id_empresa = emp.id_empresa
            WHERE ol.id_oferta_laboral = {id_oferta};
        '''
        consulta = db.executesql(qcorreo, as_dict=True)[0]
        correo_emp = consulta['correo']
        fecha_inicio = consulta['fecha_inicio']
        fecha_vigencia = consulta['fecha_vigencia']
        validacion = consulta['validacion']
        
        if int(validacion) == 0:
            db.executesql("ROLLBACK;")
            return json.dumps({'success': False, 'msg': 'Actualice la fecha de vigencia límite para contratar nuevamente'})  
        
        res = db.executesql(qs, as_dict=True)
        if len(res) == 0:
            # insertar oferta laboral estudiante
            qs = f'INSERT INTO bt_estudiante_oferta VALUES(6, {id_estudiante}, {id_oferta}, NOW());'
            db.executesql(qs)
        else:   
            # verificar el estado
            if int(res[0]['id_estado_aplicacion']) < 6:
                db.executesql("ROLLBACK;")
                return json.dumps({'success': False, 'msg': 'El estudiante ya está en proceso de contratación'})
            else:
                # si ya se le envió solicitud
                db.executesql("ROLLBACK;")
                return json.dumps({'success': False, 'msg': 'Ya se le envió solicitud'})     
        
        query_oferta = f"""
            SELECT
                puesto,
                emp.nombre_empresa
            FROM bt_oferta_laboral AS of
                INNER JOIN bt_empresa AS emp ON of.id_empresa = emp.id_empresa
            WHERE id_oferta_laboral = {id_oferta};
        """
        oferta = db.executesql(query_oferta, as_dict=True)[0]
        subject = "Solicitud de contratación para puesto laboral"
        
        correo = f"""
            <html>
                Saludos cordiales,<br><br>
                Por este medio se le informa que la empresa <b>{oferta['nombre_empresa']}</b> 
                está interesada en contratarlo para el puesto <b>{oferta['puesto']}</b>.<br>
                Favor de verificar su CV y enviarlo en la oferta laboral correspondiente en caso de aceptar esta solicitud.<br>
                Puede aplicar desde el {fecha_inicio} hasta el {fecha_vigencia}.
                <br><br><br><br>
                Sistema de Bolsa de Trabajo de La Escuela de Ciencias y Sistemas<br>
                Facultad de Ingenier&iacute;a - Universidad de San Carlos de Guatemala
            </html>
        """
        enviar_correo(correo, data["correo"], correo_emp, subject)
        db.executesql("COMMIT;")
        return json.dumps({'success': True, 'msg': 'Estado Actualizado'})            
    except Exception as ex:
        db.executesql("ROLLBACK;")
        return json.dumps({'success': False, 'msg': ex})

def cancelar_contratacion():
    try:
        data = request.vars
        id_estudiante = data['id_estudiante']
        id_oferta = data['id_oferta']
        despedido = data['despedido']
        subject = ""
        correo = ""

        db.executesql("START TRANSACTION;")
        qcorreo = f'''
            SELECT emp.correo
            FROM bt_oferta_laboral AS ol
                JOIN bt_empresa AS emp ON ol.id_empresa = emp.id_empresa
            WHERE ol.id_oferta_laboral = {id_oferta};
        '''
        correo_emp = db.executesql(qcorreo, as_dict=True)[0]['correo']
        
        qs = f'''
            UPDATE bt_estudiante_oferta
            SET id_estado_aplicacion = 7 
            WHERE 
                id_estudiante_cv = {id_estudiante}
                AND id_oferta_laboral = {id_oferta};
        '''
        db.executesql(qs)

        query_oferta = f"""
            SELECT 
                puesto,
                emp.nombre_empresa
            FROM bt_oferta_laboral AS of 
                INNER JOIN bt_empresa AS emp ON of.id_empresa = emp.id_empresa
            WHERE id_oferta_laboral = {id_oferta};
        """
        oferta = db.executesql(query_oferta, as_dict=True)[0]
        
        qs = f'''
            SELECT id_estado_aplicacion
            FROM bt_estudiante_oferta
            WHERE 
                id_estudiante_cv = {id_estudiante}
                AND id_oferta_laboral = {id_oferta};
        '''
        if despedido == '0':
            subject = "Actualizacion de Estado de Solicitud de Empleo"
            correo = f"""
                <html>
                    Saludos cordiales,<br><br>
                    Por este medio se le informa que su aplicacion a la oferta laboral: <b>{oferta['puesto']}</b>
                    de la empresa <b>{oferta['nombre_empresa']} </b> fue cancelada por parte de la empresa
                    <br><br><br><br>
                    Sistema de Bolsa de Trabajo de La Escuela de Ciencias y Sistemas<br>
                    Facultad de Ingenier&iacute;a - Universidad de San Carlos de Guatemala
                </html>
                """
        else:
            subject = "Actualizacion de Estado de Empleo"
            correo = f"""
                <html>
                    Saludos cordiales,<br><br>
                    Por este medio se le informa que ha sido despedido del puesto de: <b>{oferta['puesto']}</b> de la empresa 
                    <b>{oferta['nombre_empresa']}</b>
                    <br><br><br><br>
                    Sistema de Bolsa de Trabajo de La Escuela de Ciencias y Sistemas<br>
                    Facultad de Ingenier&iacute;a - Universidad de San Carlos de Guatemala
                </html>
            """
        enviar_correo(correo,data["correo"], correo_emp, subject)
        db.executesql("COMMIT;")
        return json.dumps({'success': True, 'msg': 'Estado Actualizado'})            
    except Exception as ex:
        db.executesql("ROLLBACK;")
        return json.dumps({'success': False, 'msg': ex})

def obtener_cv():
    try: 
        data = request.vars
        filename = data['documento_cv']

        path = os.path.join(request.folder, "uploads/bolsa_de_trabajo/")
        pathfilename = os.path.join(path, filename)

        with open(pathfilename, "rb") as pdf_file:
            encoded_string = base64.b64encode(pdf_file.read())

        return encoded_string
    except:
        return 'nop'
    