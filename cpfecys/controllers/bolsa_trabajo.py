import json
import math
import csv
import os
import base64

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def edit():
    new_dict = {}
    params = request.get_vars
    id = 0

    # Si viene el id de la empresa muestra los datos, sino lo redirije a la lista de empresas
    if 'id' in params:
        id = params["id"]
    else:
        redirect(URL('cpfecys', 'bolsa_trabajo', 'suscripciones'))

    try:
        query = '''
            SELECT
                e.*,
                s.estado_registro 
            FROM bt_empresa AS e
                INNER JOIN bt_estado_registro AS s ON e.id_estado_registro = s.id_estado_registro
            WHERE id_empresa = %(id)s
        '''
        result = db.executesql(query, {'id': id}, as_dict=True)
        new_dict["empresa"] = result

        query = 'SELECT * FROM bt_estado_registro'
        result = db.executesql(query, as_dict=True)
        new_dict["estados_registro"] = result
    except:
        redirect(URL('cpfecys', 'bolsa_trabajo', 'suscripciones'))

    if len(new_dict["empresa"]) == 0 :
        redirect(URL('cpfecys', 'bolsa_trabajo', 'suscripciones'))
    else:
        new_dict["empresa"] = new_dict["empresa"][0]
    
    return dict(new_dict=new_dict)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def editar_trabajo():
    new_dict = {}
    params = request.get_vars
    id = 0

    # Si viene el id de la empresa muestra los datos, sino lo redirije a la lista de empresas
    if 'id' in params:
        id = params["id"]
    else:
        redirect(URL('cpfecys', 'bolsa_trabajo', 'trabajos'))

    try:
        query = f'''
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
                WHERE id_oferta_laboral = {id}
        '''
        result = db.executesql(query, as_dict=True)
        new_dict["trabajo"] = result

        query = 'SELECT * FROM bt_area_especialidad'
        result = db.executesql(query, as_dict=True)
        new_dict["area_especialidad"] = result

        query = 'SELECT * FROM bt_estado_oferta_laboral'
        result = db.executesql(query, as_dict=True)
        new_dict["estados_registro"] = result
    except:
        redirect(URL('cpfecys', 'bolsa_trabajo', 'trabajos'))

    if len(new_dict["trabajo"]) == 0:
        redirect(URL('cpfecys', 'bolsa_trabajo', 'trabajos'))
    else:
        new_dict["trabajo"] = new_dict["trabajo"][0]
    return dict(new_dict=new_dict)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def editor():
    new_dict = {'selected': False, 'tabla': "", 'values': ""}
    params = request.get_vars
    
    
    offset = 0
    limit = 50
    orderby = "id"
    ordertype = "asc"
    
    if 'tabla' in params:
        new_dict["tabla"] = params["tabla"]
        new_dict["selected"] = True

    # Obtener parametros para poder manejar paginacion y busqueda si es que la hace
    page = 1
    if 'page' in params:
        page = int(params["page"])
        offset = (page - 1) * limit
    
    value = f"%{params['value']}%" if 'value' in params else '%%'
    espe = params["espe"] if 'espe' in params else '%%' #Para conservar el dato de a que especialidad debemos de guardarlo
    nombre_espe = f"%{params['nombre_espe']}%" if 'nombre_espe' in params else '%%' #Para conservar el nombre de la especialidad a agregar
        
    if 'orderby' in params:
        if params['orderby'].lower() in ['id', 'value']:
            orderby = params["orderby"].lower()
    if 'ordertype' in params:
        if params['ordertype'].lower() in ['asc','desc']:
            ordertype = params["ordertype"].lower()
   
    try:
        if request.env.request_method == "POST":
            new_value = request.post_vars["new"]
            new_value2 = request.post_vars["new2"]

            params = {'new_value': new_value, 'new_value2': new_value2}
            if new_dict["tabla"] == 'registro':
                query = "INSERT INTO bt_estado_registro(estado_registro) VALUES (%(new_value)s);"
                db.executesql(query, params)

            if new_dict["tabla"] == "Habilidad":
                query = "INSERT INTO bt_habilidad(habilidad, id_area_especialidad) VALUES (%(new_value)s, %(new_value2)s);"
                db.executesql(query, params)
            
            if new_dict["tabla"] == "especialidad":
                query = "INSERT INTO bt_area_especialidad(area_especialidad) VALUES (%(new_value)s);"
                db.executesql(query, params)
                
            if new_dict["tabla"] == "Especialidad":
                query = "INSERT INTO bt_area_especialidad(area_especialidad) VALUES (%(new_value)s);"
                db.executesql(query, params)

            if new_dict["tabla"] == "oferta":
                query = "INSERT INTO bt_estado_oferta_laboral(estado_oferta_laboral) VALUES (%(new_value)s);"
                db.executesql(query, params)
    except:
        ...

    try:
        query = ''
        query_cantidad = ''
        if new_dict["tabla"] == "registro":
            query = f"""
                SELECT
                    id_estado_registro AS id,
                    estado_registro AS value 
                FROM bt_estado_registro
                WHERE estado_registro LIKE %(value)s
                ORDER BY {orderby} {ordertype} 
                LIMIT %(offset)s, %(limit)s
            """
            query_cantidad = "SELECT COUNT(*) AS cantidad FROM bt_estado_registro WHERE estado_registro LIKE %(value)s"

        if new_dict["tabla"] == "especialidad":
            query = f"""
                SELECT
                    id_area_especialidad AS id,
                    area_especialidad AS value 
                FROM bt_area_especialidad
                WHERE area_especialidad LIKE %(value)s
                ORDER BY {orderby} {ordertype}
                LIMIT %(offset)s, %(limit)s
            """
            query_cantidad = "SELECT COUNT(*) AS cantidad FROM bt_area_especialidad WHERE area_especialidad LIKE %(value)s"
        
        if new_dict["tabla"] == "oferta":
            query = f"""
                SELECT
                    id_estado_oferta_laboral AS id,
                    estado_oferta_laboral AS value
                FROM bt_estado_oferta_laboral
                WHERE estado_oferta_laboral LIKE %(value)s 
                ORDER BY {orderby} {ordertype}
                LIMIT %(offset)s, %(limit)s
            """
            query_cantidad = "SELECT COUNT(*) AS cantidad FROM bt_estado_oferta_laboral WHERE estado_oferta_laboral LIKE %(value)s"

        ############################ AGREGADO PARA NUEVO MANEJO DE AGREGAR HABILIDAD ###############################################
        if new_dict["tabla"] == "Especialidad":
            query = f"""
                SELECT 
                    id_area_especialidad AS id, 
                    area_especialidad AS value
                FROM bt_area_especialidad 
                WHERE area_especialidad LIKE %(value)s
                ORDER BY {orderby} {ordertype}
                LIMIT %(offset)s, %(limit)s
            """
            query_cantidad = "SELECT COUNT(*) AS cantidad FROM bt_area_especialidad WHERE area_especialidad LIKE %(value)s"
        
        if new_dict["tabla"] == "Habilidad": # para desplegar habilidades de una especialidad en especifico 
            value = espe
            query = f"""
                SELECT 
                    id_habilidad AS id,
                    habilidad AS value 
                FROM bt_habilidad
                WHERE id_area_especialidad = %(value)s 
                ORDER BY {orderby} {ordertype}
                LIMIT %(offset)s, %(limit)s
            """
            query_cantidad = "SELECT COUNT(*) AS cantidad FROM bt_habilidad WHERE id_area_especialidad = %(value)s"
            
        ############################################################################################################################
        # PARA MODIFICAR TABLAS DE TAMANIO PARA BANNER Y PARA CERTIFICADO DE CURSOS APROBADOS]

        if new_dict["tabla"] == "Tamanio-Archivos":
            query = """
                SELECT 
                    id_tamanio_archivo AS id,
                    round(tamanio_curriculum / (1048576), 0) AS value, 
                    round(tamanio_banner / (1048576), 0) AS value2 
                FROM bt_tamanio_archivo
            """
            query_cantidad = "SELECT COUNT(*) AS cantidad FROM bt_tamanio_archivo"

        ############################################################################################################################

        if new_dict["selected"]:
            values = db.executesql(query, {'value': value, 'offset': offset, 'limit': limit}, as_dict=True)
            new_dict["values"] = values

            result = db.executesql(query_cantidad, {'value': value}, as_dict=True)
            new_dict["cantidad_valores"] = result[0]["cantidad"]
            new_dict["cantidad_paginas"]  = int(math.ceil(float(result[0]["cantidad"]) / limit))
            new_dict["inicio_valores"] = int(offset) + 1
            fin = int(offset) + limit
            if fin > new_dict["cantidad_valores"]:
                new_dict["fin_valores"] = new_dict["cantidad_valores"]
            else:
                new_dict["fin_valores"] = int(offset) + limit
            #Enviamos los parametros para utilizarlos al cambiar de pagina
            new_dict["next_page"] = page + 1
            new_dict["prev_page"] = page - 1
            new_dict["page"] = page
            new_dict["orderby"] = orderby
            new_dict["ordertype"] = ordertype
            new_dict["value"] = value.replace("%","")
            new_dict["espe"] = espe.replace("%","")
            new_dict["nombre_espe"] = nombre_espe.replace("%","")
    except:
        ...
    
    return dict(new_dict=new_dict)

def exportar_reportes():
    return dict()

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def reportes():
    return dict()

def suscripcion():
    # Si el metodo es post significa que es un registro
    if request.ajax:
        respuesta = {}
        db.executesql("START TRANSACTION;")
        try:
            #Obtener el body del request
            data = json.loads(request.post_vars.array)

            # Verificar que no exista ya una empresa registrada
            result = db.executesql(f"SELECT * FROM bt_empresa WHERE correo = '{data['correo']}'", as_dict=True)
            if len(result) > 0:
                respuesta["success"] = False
                respuesta["msg"] = "Correo ya registrado"
                db.executesql("ROLLBACK")
                return json.dumps(respuesta)

            #Verificar que no exista un usuario con ese correo
            result = db.executesql(f"SELECT * FROM auth_user WHERE email = '{data['correo']}'", as_dict=True)
            if len(result) > 0:
                respuesta["success"] = False
                respuesta["msg"] = "Correo ya registrado"
                db.executesql("ROLLBACK")
                return json.dumps(respuesta)

            hash = CRYPT()(str(data["password"]).encode('utf8'))[0]
            #Insertar los datos de la empresa con su relacion de usuario y el estado en progreso
            
            #Obener el id del perido en que fue registrada la empresa
            id_period_year = db.executesql('SELECT MAX(id) AS id FROM period_year;', as_dict=True)[0]['id']

            query = """
                INSERT INTO 
                    bt_empresa(
                        nombre_empresa,
                        direccion,
                        telefono,
                        correo,
                        descripcion,
                        pagina_web,
                        persona_encargada,
                        fecha_registro,
                        id_estado_registro,
                        id_period_year, 
                        password
                    ) 
                    VALUE (
                        %(nombre_empresa)s,
                        %(direccion)s,
                        %(telefono)s,
                        %(correo)s,
                        %(descripcion)s,
                        %(pagina_web)s,
                        %(persona_encargada)s,
                        NOW(),
                        1,
                        %(id_period_year)s,
                        %(password)s
                    );
            """
            params = {
                'nombre_empresa': data['nombre_empresa'],
                'direccion': data['direccion'],
                'telefono': data['telefono'],
                'correo': data['correo'],
                'descripcion': data['descripcion'],
                'pagina_web': data['pagina_web'],
                'persona_encargada': data['persona_encargada'],
                'id_period_year': str(id_period_year), 
                'password': str(hash)
            }
            result = db.executesql(query, params)

            query1 = f"SELECT * FROM bt_empresa WHERE correo = '{data['correo']}';"
            result = db.executesql(query1, as_dict=True)

            # Verificar que si se haya insertado el usuairo de empresa nueva
            # si no es de logitud 1, ocurrió problema de concurrencia o no lo insertó
            if len(result) != 1:
                db.executesql("ROLLBACK")
                respuesta["success"] = False
                respuesta["msg"] = "No se pudo registrar el usuario"
                return respuesta

            #Si el usuario se registro retorna mensaje que de success
            respuesta["success"] = True
            respuesta["msg"] = "Usuario registrado, espere a ser aceptado por un administrador para iniciar sesión"
            db.executesql("COMMIT")
            return json.dumps(respuesta)
        except Exception as e:
            db.executesql("ROLLBACK")
            respuesta["success"] = False
            respuesta["msg"] = "Sucedió un problema intentelo mas tarde"
            return respuesta
    else:
        new_dict = {'empresa': {'id_empresa': 0, 'id':0, 'correo': ''}, 'continue': False}
        # Si es metodo get se ve si envia como parametro el continuar un formulario
        try:
            id = 0
            if "continue" in request.args:
                #Obtenemos el id que se desea continuar
                if "id" in request.get_vars:
                    id = int(request.get_vars["id"])
                else:
                    #Si no viene un id se redirije al formulario de registro normal
                    redirect(URL('cpfecys', 'bolsa_trabajo', 'suscripcion'))
            else:
                return dict(new_dict=new_dict)

            #Obtenemos la informacion de la empresa registrada anteriormente
            query = """
                SELECT
                    e.*,
                    au.password,
                    au.id
                FROM bt_empresa AS e
                    INNER JOIN auth_user AS au ON e.id_usuario = au.id
                WHERE e.id_empresa = %(id)s
            """
            empresa = db.executesql(query, {'id': id},as_dict=True)

            #Verificamos que si exista la empresa
            if len(empresa) == 0:
                #Si no existe lo redirijimos al registro normal
                redirect(URL('cpfecys', 'bolsa_trabajo', 'suscripcion'))

            #Vemos que se encuentre en el estado de corregir informacion
            if empresa[0]["id_estado_registro"] != 5:
                #Si no esta en ese estado se redirije al registro normal
                redirect(URL('cpfecys', 'bolsa_trabajo', 'suscripcion'))

            #Si cumple lo enviamos para llenar el formulario
            new_dict["empresa"] = empresa[0]

            #indicamos que es un completacion de formulario
            new_dict["continue"] = True
        except:
            redirect(URL('cpfecys', 'bolsa_trabajo', 'suscripcion'))

        return dict(new_dict=new_dict)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def suscripciones():
    new_dict = {}
    params = request.get_vars

    offset = 0
    limit = 50
    
    orderby = "id_empresa"
    ordertype = "ASC"
    periodo = 0

    if 'periodo' in params: 
        periodo = int(params["periodo"])
    else:
        try:
            periodo = db.executesql('SELECT MAX(id) AS id FROM period_year;', as_dict=True)[0]['id']
        except:
            ...
    
    # Obtener parametros para poder manejar paginacion y busqueda si es que la hace
    page = 1
    if 'page' in params:
        page = int(params["page"])
        offset = (page - 1) * limit
        
    name = f'%{params["name"].lower()}%' if 'name' in params else '%%'
    email = f'%{params["email"].lower()}%' if 'email' in params else '%%'
    incharge = f'%{params["incharge"].lower()}%' if 'incharge' in params else '%%'
    status = int(params["status"]) if 'status' in params else 0
    
    if 'orderby' in params:
        if params["orderby"].lower() in ['nombre_empresa', 'correo', 'persona_encargada', 'id_estado_registro']:
            orderby = params["orderby"].lower()

    if 'ordertype' in params:
        if params["ordertype"].lower() in ['desc', 'asc']:
            ordertype = params["ordertype"].upper()

    try:
        query = '''
            SELECT 
                e.*,
                py.*,
                s.estado_registro
            FROM bt_empresa AS e
                INNER JOIN bt_estado_registro AS s ON e.id_estado_registro = s.id_estado_registro
                JOIN period_year AS py on e.id_period_year = py.id
            WHERE 
                nombre_empresa LIKE %(name)s
                AND correo LIKE %(email)s
                AND persona_encargada LIKE %(incharge)s
        '''

        query_cantidad = '''
            SELECT COUNT(*) AS cantidad
            FROM bt_empresa AS e
            WHERE 
                nombre_empresa LIKE %(name)s 
                AND correo LIKE %(email)s
                AND persona_encargada LIKE %(incharge)s
        '''

        if status > 0:
            query += ' AND e.id_estado_registro = %(status)s'
            query_cantidad += ' AND e.id_estado_registro = %(status)s'

        if periodo > 0:
            query += ' AND e.id_period_year = %(periodo)s'
            query_cantidad += ' AND e.id_period_year = %(periodo)s'

        query += f' ORDER BY e.id_empresa DESC, {orderby} {ordertype} LIMIT %(offset)s, %(limit)s'

        params = {'name': name, 'email': email, 'periodo': periodo, 'incharge': incharge, 'status': status, 'offset': offset, 'limit': limit}
        result = db.executesql(query, params, as_dict=True)
        new_dict["empresas"] = result

        query = 'SELECT * FROM bt_estado_registro'
        result = db.executesql(query, as_dict=True)
        new_dict["estados_registro"] = result

        query = 'SELECT * FROM period_year ORDER BY id DESC'
        result = db.executesql(query, as_dict=True)
        new_dict["periodos"] = result

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
        new_dict["name"] = name.replace("%","")
        new_dict["email"] = email.replace("%","")
        new_dict["incharge"] = incharge.replace("%","")
        new_dict["orderby"] = orderby
        new_dict["ordertype"] = ordertype
        new_dict["status"] = status
        new_dict["periodo"] = periodo
    except:
        new_dict["empresas"] = []
        new_dict["estados_registro"] = []

    return dict(new_dict=new_dict)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def trabajos():
    new_dict = {}
    params = request.get_vars

    offset = 0
    limit = 50

    if 'periodo' in params:
        periodo = int(params["periodo"])
    else:
        try:
            periodo = db.executesql('SELECT MAX(id) AS id FROM period_year;', as_dict=True)[0]['id']
        except:
            periodo = 0

    # Obtener parametros para poder manejar paginacion y busqueda si es que la hace
    page = 1
    if 'page' in params:
        page = int(params["page"])
        offset = (page - 1) * limit

    id_empresa = int(params["id_empresa"]) if 'id_empresa' in params else 0
    area = int(params["area"]) if 'area' in params else 0
    status = int(params["status"]) if 'status' in params else 0
    puesto = f'%{params["puesto"].lower()}%' if 'puesto' in params else '%%'    
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
                INNER JOIN period_year AS py ON ol.id_period_year = py.id
                INNER JOIN bt_empresa AS e ON ol.id_empresa = e.id_empresa
                INNER JOIN bt_estado_oferta_laboral AS eol ON ol.id_estado_oferta_laboral = eol.id_estado_oferta_laboral
                INNER JOIN bt_area_especialidad AS ae ON ol.id_area_especialidad = ae.id_area_especialidad
            WHERE ol.puesto LIKE %(puesto)s
        '''
        query_cantidad = '''
            SELECT COUNT(*) AS cantidad
            FROM bt_oferta_laboral
            WHERE puesto LIKE %(puesto)s
        '''

        # Si filtra por empresa
        if id_empresa != 0:
            query += ' AND ol.id_empresa = %(id_empresa)s'
            query_cantidad += ' AND id_empresa = %(id_empresa)s'

        # Si filtra por area
        if area != 0:
            query += ' AND ol.id_area_especialidad = %(area)s'
            query_cantidad += ' AND id_area_especialidad = %(area)s'

        # Si filtra por periodo
        if periodo != 0:
            query += ' AND ol.id_period_year = %(periodo)s'
            query_cantidad += ' AND id_period_year = %(periodo)s'

        # Si filtra por Estado de Oferta Laboral
        if status != 0:
            query += ' AND ol.id_estado_oferta_laboral = %(status)s'
            query_cantidad += ' AND id_estado_oferta_laboral = %(status)s'

        query += ' ORDER BY ol.id_oferta_laboral DESC, %(orderby)s LIMIT %(offset)s, %(limit)s'

        params = {
            'id_empresa': id_empresa,
            'area': area,
            'periodo': periodo,
            'status': status,
            'puesto': puesto,
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
        if(fin > new_dict["cantidad_empresas"]):
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

def ver_cvs_admin():
    new_dict = {}

    params = request.get_vars
    page = 1
    offset = 0
    limit = 50
    valoor = 0
    carnet = ""
    orderby = "id_estudiante_cv"

    # Obtener parametros para poder manejar paginacion y busqueda si es que la hace
    if 'page' in params:
        page = int(params["page"])
        offset = (page - 1) * limit
    if 'valoor' in params:
        valoor = params["valoor"]
    if 'carnet' in params:
        carnet = str(params["carnet"])
    if 'orderby' in params:
        orderby = params["orderby"]

    try:
        query = '''
            SELECT
                cv.id_estudiante_cv,
                au.username,
                au.username AS carnet, 
                CONCAT(CONCAT(au.first_name," "), au.last_name) AS nombre,
                cv.correo,
                cv.creditos_aprobados
            FROM bt_estudiante_cv AS cv
                INNER JOIN auth_user AS au ON au.id = cv.id_usuario
            WHERE id_estudiante_cv > 0
        '''

        # Si filtra por carnet del estudiante
        if carnet != "":
            query += f' AND username LIKE "%{carnet}%" '

        query_cantidad = f'SELECT COUNT(*) AS cantidad FROM ({query}) sub;'

        query += f' ORDER BY {orderby} LIMIT {offset}, {limit}'

        result = db.executesql(query, as_dict=True)
        new_dict["cvs"] = result
        result = db.executesql(query_cantidad, as_dict=True)
        new_dict["cantidad_cvs"] = result[0]["cantidad"]
        new_dict["cantidad_paginas"]  = int(math.ceil(float(result[0]["cantidad"]) / limit))
        new_dict["inicio_cvs"] = int(offset) + 1
        fin = int(offset) + limit
        if fin > new_dict["cantidad_cvs"]:
            new_dict["fin_cvs"] = new_dict["cantidad_cvs"]
        else:
            new_dict["fin_cvs"] = int(offset) + limit

        #Enviamos los parametros para utilizarlos al cambiar de pagina
        new_dict["next_page"] = page + 1
        new_dict["prev_page"] = page - 1
        new_dict["page"] = page
        new_dict["carnet"] = carnet
        new_dict["valoor"] = valoor
        new_dict["orderby"] = orderby

    except:
        ...

    return dict(new_dict=new_dict)

def ver_un_cv_admin():
    try:       
        data = request.vars
        id_usuario_cv = data['id_usuario']

        qs = f'SELECT id_usuario, creditos_aprobados FROM bt_estudiante_cv WHERE id_estudiante_cv = {id_usuario_cv};'
        id_user = db.executesql(qs, as_dict=True)[0]['id_usuario']
        datos_user = db.executesql(f'SELECT first_name, last_name, email, phone FROM auth_user as a INNER JOIN bt_estudiante_cv as cv ON cv.id_usuario = a.id WHERE a.id = {id_user};', as_dict=True)
        datos_cv = db.executesql(f'SELECT cv.*, TIMESTAMPDIFF(YEAR, fecha_nacimiento,CURDATE()) AS edad FROM bt_estudiante_cv AS cv where id_estudiante_cv = {id_usuario_cv};', as_dict=True)
        query_areas = f'''
            SELECT
                est.id_area_especialidad,
                area.area_especialidad
            FROM bt_area_especialidad AS area
                INNER JOIN bt_estudiante_especialidad AS est ON area.id_area_especialidad = est.id_area_especialidad
                INNER JOIN bt_estudiante_cv AS cv ON est.id_estudiante_cv = cv.id_estudiante_cv
            WHERE cv.id_estudiante_cv = {id_usuario_cv};
        '''
        areas_est = db.executesql(query_areas, as_dict=True)
        certificaciones = db.executesql(f"SELECT id_certificacion, nombre_certificacion, enlace, fecha_expedicion, tipo FROM bt_certificacion WHERE id_estudiante_cv = {id_usuario_cv};", as_dict=True)
        habilidades_usuario = db.executesql(f"SELECT hab.id_habilidad, hab.habilidad FROM bt_estudiante_habilidad as est INNER JOIN  bt_habilidad as hab ON est.id_habilidad = hab.id_habilidad WHERE est.id_estudiante_cv = {id_usuario_cv};", as_dict=True)
        experiencia_lab = db.executesql(f'SELECT id_experiencia,puesto, empresa,fecha_inicio,IFNULL(fecha_fin, "Presente") AS fecha_fin,descripcion FROM bt_experiencia_laboral as ex INNER JOIN bt_estudiante_cv as es ON ex.id_estudiante_cv = es.id_estudiante_cv WHERE es.id_estudiante_cv = {id_usuario_cv};',as_dict=True)
        creditos = db.executesql(qs,as_dict=True)[0]['creditos_aprobados']

        ## para saber la visibilidad
        publico = f'SELECT * FROM bt_estudiante_especialidad WHERE id_estudiante_cv = {id_usuario_cv};'
        visibilidad = db.executesql(publico, as_dict=True)
        resp_visibilidad = "Privado"
        if len(visibilidad) > 0:
            if(visibilidad[0]['id_estado_visibilidad'] == 2):
                resp_visibilidad = 'Público'
            else:
                resp_visibilidad = 'Privado'
        else:
            resp_visibilidad = 'Privado'
        
        return dict(
            experiencia_lab=experiencia_lab,
            datos_user=datos_user[0],
            datos_cv=datos_cv[0],
            areas_est=areas_est,
            activo=1,
            certificaciones=certificaciones,
            habilidades_usuario=habilidades_usuario,
            creditos_aprobados=creditos,
            visibility=resp_visibilidad
        )
    except:
        return dict(datos_user={},datos_cv={},areas_est=[],activo=1,certificaciones=[],habilidades_usuario=[], creditos_aprobados=0) 
 
@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def view():
    new_dict = {}
    params = request.get_vars
    id = 0

    # Si viene el id de la empresa muestra los datos, sino lo redirije a la lista de empresas
    if 'id' in params:
        id = params["id"]
    else:
        redirect(URL('cpfecys', 'bolsa_trabajo', 'suscripciones'))

    try:
        query = f'''
            SELECT
                e.*,
                s.estado_registro 
            FROM bt_empresa AS e
                INNER JOIN bt_estado_registro AS s ON e.id_estado_registro = s.id_estado_registro
            WHERE id_empresa = %(id)s
        '''
        result = db.executesql(query, {'id': id}, as_dict=True)
        new_dict["empresa"] = result

        query = 'SELECT * FROM bt_estado_registro'
        result = db.executesql(query, as_dict=True)
        new_dict["estados_registro"] = result
    except:
        redirect(URL('cpfecys', 'bolsa_trabajo', 'suscripciones'))

    #Si no se encontro ningun resultado lo redirije a la lista de empresas
    if len(new_dict["empresa"]) == 0:
        redirect(URL('cpfecys', 'bolsa_trabajo', 'suscripciones'))
    else:
        new_dict["empresa"] = new_dict["empresa"][0]

    return dict(new_dict=new_dict)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def view_trabajo():
    new_dict={}

    params = request.get_vars
    id = 0

    # Si viene el id del trabajo muestra los datos, sino lo redirije a la lista de trabajos
    if 'id' in params:
        id = params["id"]
    else:
        redirect(URL('cpfecys', 'bolsa_trabajo', 'trabajos'))

    try:
        query = f'''
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
            WHERE id_oferta_laboral = {id} 
            ORDER BY id_oferta_laboral;
        '''
        result = db.executesql(query, as_dict=True)
        new_dict["trabajo"] = result
    except:
        redirect(URL('cpfecys', 'bolsa_trabajo', 'trabajos'))

    #Si no se encontro ningun resultado lo redirije a la lista de trabajos
    if len(new_dict["trabajo"]) == 0:
        redirect(URL('cpfecys', 'bolsa_trabajo', 'trabajos'))
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

            notificar_arreglo = False
            notificar_autorizado = False
            notificar_rechazo = False
            notificar_desactivacion = False

            if int(data["estado"]) == 2:
                notificar_autorizado = True
            elif int(data["estado"]) == 3:
                notificar_rechazo = True
            elif int(data["estado"]) == 4:
                notificar_desactivacion = True
            elif int(data["estado"]) == 5:
                notificar_arreglo = True

            if "sha512" not in data["password"]:
                data["password"] = CRYPT()(str(data["password"]).encode('utf8'))[0]

            # si fue aceptada o se le pidió actualizar datos
            if int(data["estado"]) == 2 or int(data["estado"]) == 5:
                # si no tenia un usuario creado
                if usuario is None:
                    # inserta el nuevo usuario para que la empresa pueda iniciar sesion
                    query = """
                        INSERT INTO
                            auth_user (
                                first_name,
                                email,
                                username,
                                password
                            )
                            VALUES (
                                %(nombre_empresa)s,
                                %(correo)s,
                                %(username)s,
                                %(password)s
                            );
                    """
                  
                    params = {
                        'nombre_empresa': data['nombre_empresa'], 
                        'correo': data['correo'], 
                        'username': data['correo'], 
                        'password': str(data['password'])
                    }
                    db.executesql(query, params)

                    get_id = f"SELECT id FROM auth_user WHERE email = '{data['correo']}';"
                    result = db.executesql(get_id, as_dict=True)
                    id_usuario = result[0]["id"]

                    # se actualiza el id_usuario en la tabla bt_empresa
                    query1 = "UPDATE bt_empresa SET id_usuario = %(id_usuario)s WHERE id_empresa = %(id_empresa)s;"
                    params = {'id_usuario': id_usuario, 'id_empresa': empresa['id_empresa']}
                    db.executesql(query1, params)

                    # se actualiza el id_usuario para la variable de empresa y usuario
                    empresa['id_usuario'] = id_usuario
                    usuario = id_usuario

                    #Obtener id del rol de empresa
                    result = db.executesql("SELECT * FROM auth_group WHERE role = 'Empresa'", as_dict=True)
                    id_role = result[0]["id"]
                    
                    #Agregar la relacion de rol con usuario
                    params = {'id_usuario': id_usuario, 'id_role': id_role}
                    db.executesql("INSERT INTO auth_membership(user_id, group_id) VALUES (%(id_usuario)s, %(id_role)s)", params)
                # que se actualicen los datos en el usuario asociado
                else:
                    query = f"""
                        UPDATE auth_user 
                        SET
                            email = %(correo)s,
                            username = %(username)s,
                            password = %(password)s,
                            registration_key = ''
                        WHERE id = %(usuario)s
                    """
                    params = {
                        'correo': data['correo'],
                        'username': data['correo'],
                        'password': str(data['password']),
                        'usuario': usuario
                    }
                    db.executesql(query, params)
            else:
                # se cambia de estado el usuario para que no pueda iniciar sesión
                if usuario is not None:
                    query = f"UPDATE auth_user SET registration_key = 'blocked' WHERE id = %(usuario)s"
                    db.executesql(query, {'usuario', usuario})

            # Se actualiza datos de empresa
            query = f"""
                UPDATE bt_empresa 
                SET 
                    nombre_empresa = %(nombre_empresa)s, 
                    direccion = %(direccion)s, 
                    telefono = %(telefono)s,
                    correo = %(correo)s,
                    pagina_web = %(pagina_web)s,
                    persona_encargada = %(persona_encargada)s,
                    id_estado_registro = %(registro)s,
                    motivo_rechazo = %(motivo)s,
                    password = %(password)s
                WHERE id_empresa = %(id_empresa)s
            """
            params = {
                'nombre_empresa': data["nombre_empresa"],
                'direccion': data["direccion"], 
                'telefono': data["telefono"], 
                'correo': data["correo"], 
                'pagina_web': data["pagina_web"], 
                'persona_encargada': data["persona_encargada"], 
                'registro': data["estado"], 
                'motivo': data["motivo"], 
                'id_empresa': empresa["id_empresa"], 
                'password': str(data["password"])
            }
            db.executesql(query, params)

            if int(empresa['id_estado_registro']) == int(data['estado']):
                notificar_arreglo = False
                notificar_autorizado = False
                notificar_rechazo = False
                notificar_desactivacion = False

            subject = "Registro en plataforma DTT"
            correo = f"""
                <html>
                    Saludos cordiales {empresa["nombre_empresa"]},
                    <br><br>
                    Por este medio se le informa que su usuario: <b>{data["correo"]}</b>
            """

            if notificar_autorizado:
                correo += f" ha sido autorizado en la plataforma DTT. <br><br>Puede ingresar a la plataforma por el siguiente link: {cpfecys.get_domain()}user/login?_next=/home"
            elif notificar_arreglo:
                correo += f" necesita ser verificada la informaci&oacute;n proporcionada. Siendo el motivo:<br>{data['motivo']}"
                correo += "<br><br>Puede continuar con su registro a la plataforma por el siguiente link: "
                correo +=  f"{cpfecys.get_domain()}bolsa_trabajo/suscripcion/continue?id={empresa['id_empresa']}"
            elif notificar_rechazo:
                correo += f" ha sido rechazada, por el siguiente motivo:<br>{data['motivo']}"
                correo += "<br><br>Para mas informaci&oacute;n puede contactarse con el administrador."
            elif notificar_desactivacion:
                correo += f" ha sido desactivada, por el siguiente motivo:<br>{data['motivo']}"
                correo += "<br><br>Para mas informaci&oacute;n puede contactarse con el administrador."

            correo += "<br><br>Sistema de Bolsa de Trabajo de La Escuela de Ciencias y Sistemas<br>Facultad de Ingenieria - Universidad de San Carlos de Guatemala</html>"

            if notificar_autorizado or notificar_arreglo or notificar_rechazo or notificar_desactivacion:
                enviar_correo(correo, data["correo"], subject)

            #Si el usuario se registro retorna mensaje que de success
            respuesta["success"] = True
            respuesta["msg"] = "Empresa actualizada"
            db.executesql("COMMIT")
            return json.dumps(respuesta)
        except:
            db.executesql("ROLLBACK")
            respuesta["success"] = False
            respuesta["msg"] = "Sucedió un problema intentelo mas tarde"
            return json.dumps(respuesta)
    else:
        return json.dumps({'success': False, 'msg': 'Error'})

def enviar_correo(mensaje, destinatario, subject):
    was_sent = mail.send(to=[destinatario], subject=subject, message=mensaje,encoding='utf-8')
    db.mailer_log.insert(sent_message=mensaje, destination=str(destinatario), result_log=f"{mail.error or ''}:{mail.result}", success=was_sent)

    return mensaje

def actualizar_trabajo():
    # Si el metodo es post significa que es un registro
    if request.ajax:
        respuesta = {}
        db.executesql("START TRANSACTION;")
        try:
            #Obtener el body del request
            data = json.loads(request.post_vars.array)
            # Verificar que no exista ya una oferta laboral registrada
            result = db.executesql("SELECT * FROM bt_oferta_laboral WHERE id_oferta_laboral = %(id)s", {'id': data['id_oferta']}, as_dict=True)
            if len(result) == 0:
                respuesta["success"] = False
                respuesta["msg"] = "Oferta laboral no registrada"
                db.executesql("ROLLBACK")
                return json.dumps(respuesta)

            #Guardar los datos de oferta encontrada
            trabajo = result[0]

            #obtener correo de empresa
            result = db.executesql("SELECT * FROM bt_empresa WHERE id_empresa = %(id)s", {'id': trabajo["id_empresa"]}, as_dict=True)
            empresa = result[0]

            notificar_autorizado = False
            notificar_rechazo = False

            if int(data["estado"]) == 2:
                notificar_autorizado = True
            elif int(data["estado"]) == 3:
                notificar_rechazo = True

            #Se actualiza oferta laboral
            query = """
                UPDATE bt_oferta_laboral
                SET 
                    salario_aproximado = %(salario)s,
                    fecha_inicio = %(fecha_inicio)s,
                    fecha_vigencia = %(fecha_vigencia)s,
                    id_area_especialidad = %(area)s,
                    id_estado_oferta_laboral = %(estado)s,
                    motivo_rechazo = %(motivo)s,
                    seleccionada = %(seleccionada)s 
                WHERE id_oferta_laboral = %(id_oferta)s
            """
            params = {
                'salario': data["salario"],
                'fecha_inicio': data["fecha_inicio"],
                'fecha_vigencia': data["fecha_vigencia"],
                'area': data["area"],
                'estado': data["estado"],
                'motivo': data["motivo"],
                'seleccionada': data['seleccionada'],
                'id_oferta': data["id_oferta"]
            }
            db.executesql(query, params)

            if int(trabajo['id_estado_oferta_laboral']) == data['estado']:
                notificar_autorizado = False
                notificar_rechazo = False

            subject = "Solicitud de Ofeta Laboral Registrada en DTT"
            correo = f"""
                <html>
                    Saludos cordiales {empresa['nombre_empresa']},
                    <br><br>
                    Por este medio se le informa que su oferta laboral: <b>{data['puesto']}</b>
            """

            if notificar_autorizado:
                correo += " ha sido autorizada en la plataforma DTT."
            elif notificar_rechazo:
                correo += f"""
                    ha sido rechazada, por el siguiente motivo:<br>{data['motivo']}<br><br>
                    Para mas informaci&oacute;n puede contactarse con el administrador.
                """

            correo += "<br><br>Sistema de Bolsa de Trabajo de La Escuela de Ciencias y Sistemas<br>Facultad de Ingenier&iacute;a - Universidad de San Carlos de Guatemala</html>"

            if notificar_autorizado or notificar_rechazo:
                enviar_correo(correo, empresa["correo"], subject)
            #Si la oferta laboral si se actualiza
            respuesta["success"] = True
            respuesta["msg"] = "Oferta Laboral actualizada"
            db.executesql("COMMIT")
            return json.dumps(respuesta)
        except:
            db.executesql("ROLLBACK")
            respuesta["success"] = False
            respuesta["msg"] = "Sucedió un problema intentelo mas tarde"
            return json.dumps(respuesta)
    else:
        return json.dumps({'success': False, 'msg': 'Error'})

def updatesuscripcion():
    respuesta = {}
    db.executesql("START TRANSACTION;")
    try:
        #Obtener el body del request
        data = json.loads(request.post_vars.array)

        # Verificar que si exista ya una empresa registrada
        result = db.executesql("SELECT * FROM bt_empresa WHERE id_empresa = %(id_empresa)s", {'id_empresa':data["id_empresa"]}, as_dict=True)
        if len(result) == 0:
            respuesta["success"] = False
            respuesta["msg"] = "Empresa no encontrada"
            db.executesql("ROLLBACK")
            return json.dumps(respuesta)

        # Si cambia de correo verificar que no exista
        if data['correo'] != data['correo_registrado']:
            result = db.executesql("SELECT * FROM bt_empresa WHERE correo = %(correo)s", {'correo':data["correo"]}, as_dict=True)
            if len(result) > 0:
                respuesta["success"] = False
                respuesta["msg"] = "Correo no disponible"
                db.executesql("ROLLBACK")
                return json.dumps(respuesta)

        #Verificar que no exista un usuario con ese correo
        result = db.executesql("SELECT * FROM auth_user WHERE id = %(id)s", {'id': data["id_usuario"]}, as_dict=True)
        if(len(result) == 0):
            respuesta["success"] = False
            respuesta["msg"] = "Usuario no encontrado"
            db.executesql("ROLLBACK")
            return json.dumps(respuesta)
        
        usuario = result[0]
        spplitted = usuario["password"].split('$')
        hash = CRYPT(salt=spplitted[1])(str(data["confirm"]).encode('utf8'))[0]

        #Verificar que la contraseña ingresada sea la misma que ingreso anteriormente
        if str(hash) != usuario["password"]:
            respuesta["success"] = False
            respuesta["msg"] = "Contraseña ingresada no coincide con la que ingreso anteriormente."
            db.executesql("ROLLBACK")
            return json.dumps(respuesta)

        # Se actualiza el usuario
        query = "UPDATE auth_user SET email = %(correo)s, username = %(correo)s WHERE id = %(id)s"
        params = {'correo': data["correo"], 'id': usuario["id"]}
        db.executesql(query, params)

        #Insertar los datos de la empresa con su relacion de usuario y el estado en progreso
        query = """
            UPDATE bt_empresa 
            SET
                nombre_empresa = %(nombre_empresa)s,
                direccion = %(direccion)s,
                telefono = %(telefono)s,
                correo = %(correo)s,
                descripcion = %(descripcion)s,
                pagina_web = %(pagina_web)s,
                persona_encargada = %(persona_encargada)s,
                id_estado_registro = 1 
            WHERE id_empresa = %(id_empresa)s
        """
        params = {
            'nombre_empresa': data["nombre_empresa"],
            'direccion': data["direccion"],
            'telefono': data["telefono"],
            'correo': data["correo"], 
            'descripcion': data["descripcion"],
            'pagina_web': data["pagina_web"],
            'persona_encargada': data["persona_encargada"],
            'id_empresa': data["id_empresa"]
        }
        db.executesql(query, params)
        
        #Si el usuario se registro retorna mensaje que de success
        respuesta["success"] = True
        respuesta["msg"] = "Usuario registrado, espere a ser aceptado por un administrador para iniciar sesión"
        db.executesql("COMMIT")
    except:
        respuesta["success"] = False
        respuesta["msg"] = "Hubo un problema"
        db.executesql("ROLLBACK")

    return json.dumps(respuesta)

def eliminar_empresa():
    respuesta = {}
    db.executesql("START TRANSACTION;")

    try:
        #Obtener el body del request
        data = json.loads(request.post_vars.array)

        # Verificar que si exista ya una empresa registrada
        result = db.executesql("SELECT * FROM bt_empresa WHERE id_empresa = %(id_empresa)s", {'id_empresa':data["id_empresa"]}, as_dict=True)
        if len(result) == 0:
            respuesta["success"] = False
            respuesta["msg"] = "Empresa no encontrada"
            db.executesql("ROLLBACK")
            return json.dumps(respuesta)
        empresa = result[0]

        #Eliminar el resgistro del usuario empresa
        db.executesql("DELETE FROM auth_user WHERE username = %(correo)s", {'correo': empresa["correo"]})

        # Se elimina el registro de la empresa
        query = "DELETE FROM bt_empresa WHERE id_empresa = %(id)s"
        params = {'id': data["id_empresa"]}
        db.executesql(query, params)

        #Si el usuario se registro retorna mensaje que de success
        respuesta["success"] = True
        respuesta["msg"] = "Empresa eliminada"
        db.executesql("COMMIT")
    except:
        respuesta["success"] = False
        respuesta["msg"] = "Hubo un problema"
        db.executesql("ROLLBACK")

    return json.dumps(respuesta)

def eliminar_valor():
    respuesta = {}
    db.executesql("START TRANSACTION;")

    try:
        #Obtener el body del request
        data = json.loads(request.post_vars.array)

        query = ''
        if data["tabla"] == "registro":
            query = "SELECT * FROM bt_estado_registro WHERE id_estado_registro = %(id)s"

        if data["tabla"] == "Habilidad":
            query = "SELECT * FROM bt_habilidad WHERE id_habilidad = %(id)s"

        if data["tabla"] == "especialidad":
            query = "SELECT * FROM bt_area_especialidad WHERE id_area_especialidad = %(id)s"

        if data["tabla"] == "Especialidad":
            query = "SELECT * FROM bt_area_especialidad WHERE id_area_especialidad = %(id)s"

        if data["tabla"] == "oferta":
            query = "SELECT * FROM bt_estado_oferta_laboral  WHERE id_estado_oferta_laboral = %(id)s"


        # Verificar que si exista ya una un valor registrado
        result = db.executesql(query, {'id': data["id_valor"]}, as_dict=True)
        if len(result) == 0:
            respuesta["success"] = False
            respuesta["msg"] = "Valor no encontrado"
            db.executesql("ROLLBACK")
            return json.dumps(respuesta)

        if data["tabla"] == "registro":
            query = "DELETE FROM bt_estado_registro WHERE id_estado_registro = %(id)s"

        if data["tabla"] == "Habilidad":
            query = "DELETE FROM bt_habilidad WHERE id_habilidad = %(id)s"

        if data["tabla"] == "especialidad":
            query = "DELETE FROM bt_area_especialidad WHERE id_area_especialidad = %(id)s"

        if data["tabla"] == "Especialidad":
            query = "DELETE FROM bt_area_especialidad WHERE id_area_especialidad = %(id)s"
            
        if data["tabla"] == "oferta":
            query = "DELETE FROM bt_estado_oferta_laboral  WHERE id_estado_oferta_laboral = %(id)s"

        #Eliminar el resgistro de la tabla
        db.executesql(query, {'id': data["id_valor"]}) 
        #Si el usuario se registro retorna mensaje que de success
        respuesta["success"] = True
        respuesta["msg"] = "Objeto eliminado"
        db.executesql("COMMIT")
    except:
        respuesta["success"] = False
        respuesta["msg"] = "Hubo un problema"
        db.executesql("ROLLBACK")

    return json.dumps(respuesta)

def eliminar_trabajo():
    respuesta = {}
    db.executesql("START TRANSACTION;")

    try:
        #Obtener el body del request
        data = json.loads(request.post_vars.array)

        # Verificar que si exista ya una oferta laboral registrada
        result = db.executesql("SELECT * FROM bt_oferta_laboral WHERE id_oferta_laboral = %(id)s", {'id': data["id_oferta_laboral"]}, as_dict=True)
        if(len(result) == 0):
            respuesta["success"] = False
            respuesta["msg"] = "Oferta Laboral no encontrada"
            db.executesql("ROLLBACK")
            return json.dumps(respuesta)
        trabajo = result[0]

        # Se elimina el registro de la oferta laboral
        query = "DELETE FROM bt_oferta_laboral WHERE id_oferta_laboral = %(id)s"
        params = {'id': data["id_oferta_laboral"]}
        db.executesql(query, params)

        #Si el usuario se registro retorna mensaje que de success
        respuesta["success"] = True
        respuesta["msg"] = "Oferta Laboral eliminada"
        db.executesql("COMMIT")
    except:
        respuesta["success"] = False
        respuesta["msg"] = "Hubo un problema"
        db.executesql("ROLLBACK")

    return json.dumps(respuesta)

def ver_seleccionados():
    respuesta = {}
    try:
        result = db.executesql("SELECT COUNT(*) as cantidad FROM bt_oferta_laboral as oft WHERE oft.seleccionada = 1 AND oft.id_estado_oferta_laboral = 2;", as_dict=True)
        respuesta["success"] = True
        respuesta["limite"] = result[0]['cantidad']
    except:
        respuesta["success"] = False
        respuesta["msg"] = "Hubo un problema"
        db.executesql("ROLLBACK")
    return json.dumps(respuesta)

def actualizar_valor():
    respuesta = {}
    db.executesql("START TRANSACTION;")

    try:
        #Obtener el body del request
        data = json.loads(request.post_vars.array)
    
        query = ''
        if data["tabla"] == "registro":
            query = "SELECT * FROM bt_estado_registro WHERE id_estado_registro = %(id)s"
        if data["tabla"] == "Habilidad":
            query = "SELECT * FROM bt_habilidad WHERE id_habilidad = %(id)s"
        if data["tabla"] == "especialidad":
            query = "SELECT * FROM bt_area_especialidad WHERE id_area_especialidad = %(id)s"
        if data["tabla"] == "Especialidad":
            query = "SELECT * FROM bt_area_especialidad WHERE id_area_especialidad = %(id)s"
        if data["tabla"] == "oferta":
            query = "SELECT * FROM bt_estado_oferta_laboral  WHERE id_estado_oferta_laboral = %(id)s"
        if data["tabla"] == "Tamanio-Archivos": # para tamanio de archivos
            query = "SELECT * FROM bt_tamanio_archivo  WHERE id_tamanio_archivo = %(id)s"   

        # Verificar que si exista ya una un valor registrado
        result = db.executesql(query, {'id': data["id_valor"]}, as_dict=True)
        if len(result) == 0:
            respuesta["success"] = False
            respuesta["msg"] = "Valor no encontrado"
            db.executesql("ROLLBACK")
            return json.dumps(respuesta)

        if data["tabla"] == "registro":
            query = "UPDATE bt_estado_registro SET estado_registro = %(valor)s WHERE id_estado_registro = %(id)s"
        if data["tabla"] == "Habilidad":
            query = "UPDATE bt_habilidad SET habilidad = %(valor)s WHERE id_habilidad = %(id)s"
        if data["tabla"] == "especialidad":
            query = "UPDATE bt_area_especialidad SET area_especialidad = %(valor)s WHERE id_area_especialidad = %(id)s"
        if data["tabla"] == "Especialidad":
            query = "UPDATE bt_area_especialidad SET area_especialidad = %(valor)s WHERE id_area_especialidad = %(id)s"
        if data["tabla"] == "oferta":
            query = "UPDATE bt_estado_oferta_laboral SET estado_oferta_laboral = %(valor)s  WHERE id_estado_oferta_laboral = %(id)s"
        if data["tabla"] == "Tamanio-Archivos":
            if data["tipo"] == 1:
                query = "UPDATE bt_tamanio_archivo SET tamanio_curriculum =(%(valor)s * 1048576) WHERE id_tamanio_archivo = %(id)s"
            else:
                query = "UPDATE bt_tamanio_archivo SET tamanio_banner =(%(valor)s * 1048576) WHERE id_tamanio_archivo = %(id)s"

        #Eliminar el resgistro de la tabla
        db.executesql(query, {'id': data["id_valor"], 'valor': data["valor"]}) 
        #Si el usuario se registro retorna mensaje que de success
        respuesta["success"] = True
        respuesta["msg"] = "Valor Actualizado"
        db.executesql("COMMIT")
    except:
        respuesta["success"] = False
        respuesta["msg"] = "Hubo un problema"
        db.executesql("ROLLBACK")

    return json.dumps(respuesta)

def reportes_data():
    new_dict = {
        'registroEmpresa': {
            'labels': [],
            'data': []
        },
        'registroOferta': {
            'labels': [],
            'data': []
        },
        'empresasPropuestas': {
            'labels': [],
            'data': []
        },
        'visitaPropuestas': {
            'labels': [],
            'data': []
        },
        'visitaPropuestasMenos': {
            'labels': [],
            'data': []
        },
        'promedioSalarios':{
            'labels': [],
            'data': []
        },
        'aplicantesPropuestas': {
            'labels': [],
            'data': []
        },
        'ofertasRecibidas': {
            'labels': [],
            'data': []
        },
        'ofertasRevisadas': {
            'labels': [],
            'data': []
        },
        'ofertasContactadas': {
            'labels': [],
            'data': []
        },
        'ofertasContratadas': {
            'labels': [],
            'data': []
        }
    }
    try:
        # Obtencion de informacion para reporte de registro de empresas
        query = '''
            SELECT 
                CONVERT(er.estado_registro USING UTF8) AS label,
                COUNT(e.id_estado_registro) AS value
            FROM bt_empresa AS e 
                JOIN bt_estado_registro AS er ON e.id_estado_registro = er.id_estado_registro
            GROUP BY er.estado_registro;
        '''
        result = db.executesql(query, as_dict=True)
        for dato in result:
            new_dict['registroEmpresa']['labels'].append(dato['label'])
            new_dict['registroEmpresa']['data'].append(dato['value'])

        # Obtencion de informacion para reporte de registro de ofertas laborales
        query = '''
            SELECT
                CONVERT(eol.estado_oferta_laboral USING UTF8) AS label,
                COUNT(ol.id_estado_oferta_laboral) AS value
            FROM bt_oferta_laboral AS ol 
                JOIN bt_estado_oferta_laboral AS eol ON ol.id_estado_oferta_laboral = eol.id_estado_oferta_laboral
            GROUP BY eol.estado_oferta_laboral;
        '''
        result = db.executesql(query, as_dict=True)
        for dato in result:
            new_dict['registroOferta']['labels'].append(dato['label'])
            new_dict['registroOferta']['data'].append(dato['value'])

        # Obtencion de informacion para reporte de cantidad de ofertas laborales aceptadas
        query = '''
            SELECT 
                e.nombre_empresa AS label,
                COUNT(ol.id_empresa) AS value
            FROM bt_oferta_laboral AS ol
                JOIN bt_empresa AS e ON ol.id_empresa = e.id_empresa
            GROUP BY e.nombre_empresa, ol.id_estado_oferta_laboral
            HAVING ol.id_estado_oferta_laboral = 2
            ORDER BY value DESC LIMIT 10;
        '''
        result = db.executesql(query, as_dict=True)
        for dato in result:
            new_dict['empresasPropuestas']['labels'].append(dato['label'])
            new_dict['empresasPropuestas']['data'].append(dato['value'])
        
        #Reporte top propuestas con mas vistas
        query = 'SELECT puesto AS label, visitas AS value FROM bt_oferta_laboral ORDER BY visitas DESC LIMIT 5;'
        result = db.executesql(query, as_dict=True)
        for dato in result:
            new_dict['visitaPropuestas']['labels'].append(dato['label'])
            new_dict['visitaPropuestas']['data'].append(dato['value'])

        #Reporte top propuestas con menos vistas
        query = 'SELECT puesto AS label, visitas AS value FROM bt_oferta_laboral ORDER BY visitas ASC LIMIT 5'
        result = db.executesql(query, as_dict=True)
        for dato in result:
            new_dict['visitaPropuestasMenos']['labels'].append(dato['label'])
            new_dict['visitaPropuestasMenos']['data'].append(dato['value'])

        # Obtencion de informacion para reporte de promedio de rangos salariales por area
        query = '''
            SELECT 
                a.area_especialidad AS label,
                AVG(ol.salario_aproximado) AS value
            FROM bt_oferta_laboral AS ol 
                JOIN bt_area_especialidad AS a ON ol.id_area_especialidad = a.id_area_especialidad
            WHERE ol.id_estado_oferta_laboral = 2
            GROUP BY a.area_especialidad
            ORDER BY value DESC LIMIT 10;
        '''
        result = db.executesql(query, as_dict=True)
        for dato in result:
            new_dict['promedioSalarios']['labels'].append(dato['label'])
            new_dict['promedioSalarios']['data'].append(dato['value'])        

        # Ofertas Laborales con mayor numero de aplicantes
        query = '''
            SELECT
                ef.id_oferta_laboral,
                CONCAT(CONCAT(ol.puesto," - "), emp.nombre_empresa) AS label,
                COUNT(ef.id_oferta_laboral) AS value
            FROM bt_oferta_laboral AS ol
                JOIN bt_estudiante_oferta AS ef ON ol.id_oferta_laboral = ef.id_oferta_laboral
                JOIN bt_empresa AS emp ON ol.id_empresa = emp.id_empresa
            GROUP BY ef.id_oferta_laboral
            ORDER BY value DESC LIMIT 10;
        '''
        result = db.executesql(query, as_dict=True)
        for dato in result:
            new_dict['aplicantesPropuestas']['labels'].append(dato['label'])
            new_dict['aplicantesPropuestas']['data'].append(dato['value'])   

        # Empresas con mayor cantidad de solicitudes recibidas
        query = '''
            SELECT 
                COUNT(*) AS value,
                emp.nombre_empresa AS label 
            FROM bt_estudiante_oferta AS eo 
                INNER JOIN bt_estado_aplicacion AS eof ON eo.id_estado_aplicacion = eof.id_estado_aplicacion 
                INNER JOIN bt_oferta_laboral AS ol ON eo.id_oferta_laboral = ol.id_oferta_laboral 
                INNER JOIN bt_empresa AS emp ON ol.id_empresa = emp.id_empresa
            WHERE eof.id_estado_aplicacion = 1 
            GROUP BY emp.nombre_empresa;
        '''
        result = db.executesql(query, as_dict=True)
        for dato in result:
            new_dict['ofertasRecibidas']['labels'].append(dato['label'])
            new_dict['ofertasRecibidas']['data'].append(dato['value'])  

        # Empresas con mayor cantidad de solicitudes recibidas
        query = '''
            SELECT 
                COUNT(*) AS value,
                emp.nombre_empresa AS label 
            FROM bt_estudiante_oferta AS eo 
                INNER JOIN bt_estado_aplicacion AS eof ON eo.id_estado_aplicacion = eof.id_estado_aplicacion 
                INNER JOIN bt_oferta_laboral AS ol ON eo.id_oferta_laboral = ol.id_oferta_laboral 
                INNER JOIN bt_empresa AS emp  ON ol.id_empresa = emp.id_empresa 
            WHERE eof.id_estado_aplicacion = 2 
            GROUP BY emp.nombre_empresa;
        '''
        result = db.executesql(query, as_dict=True)
        for dato in result:
            new_dict['ofertasRevisadas']['labels'].append(dato['label'])
            new_dict['ofertasRevisadas']['data'].append(dato['value'])    

        # Empresas con mayor cantidad de solicitudes recibidas
        query = '''
            SELECT 
                COUNT(*) AS value,
                emp.nombre_empresa AS label 
            FROM bt_estudiante_oferta AS eo 
                INNER JOIN bt_estado_aplicacion AS eof ON eo.id_estado_aplicacion = eof.id_estado_aplicacion 
                INNER JOIN bt_oferta_laboral AS ol ON eo.id_oferta_laboral = ol.id_oferta_laboral 
                INNER JOIN bt_empresa AS emp  ON ol.id_empresa = emp.id_empresa 
            WHERE eof.id_estado_aplicacion = 3 
            GROUP BY emp.nombre_empresa;
        '''
        result = db.executesql(query, as_dict=True)
        for dato in result:
            new_dict['ofertasContactadas']['labels'].append(dato['label'])
            new_dict['ofertasContactadas']['data'].append(dato['value'])   

        # Empresas con mayor cantidad de solicitudes recibidas
        query = '''
            SELECT 
                COUNT(*) AS value,
                emp.nombre_empresa AS label
            FROM bt_estudiante_oferta AS eo
                INNER JOIN bt_estado_aplicacion AS eof ON eo.id_estado_aplicacion = eof.id_estado_aplicacion 
                INNER JOIN bt_oferta_laboral AS ol ON eo.id_oferta_laboral = ol.id_oferta_laboral 
                INNER JOIN bt_empresa AS emp ON ol.id_empresa = emp.id_empresa
            WHERE eof.id_estado_aplicacion = 4 
            GROUP BY emp.nombre_empresa;
        '''
        result = db.executesql(query, as_dict=True)
        for dato in result:
            new_dict['ofertasContratadas']['labels'].append(dato['label'])
            new_dict['ofertasContratadas']['data'].append(dato['value'])   
    except:
        ...

    return json.dumps(new_dict)

def exportar_reporte(query, nombre):
    ruta = f"applications/cpfecys/static/bolsa_trabajo/reportes/{nombre}"
    rows = db.executesql(query)
    rows_strings = [[value if isinstance(value, str) else value.decode('utf-8') for value in row] for row in rows]
    with open(ruta, "w") as f:
        writer = csv.writer(f)
        for row_bytes in rows_strings: writer.writerow(row_bytes)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def reportes_docs():
    new_dict = {}
    values = ""
    try:
        try:
         # 1 empresas no registradas
            query = '''
                SELECT 
                    'ID DE EMPRESA' AS ID_EMPRESA,
                    'NOMBRE DE EMPRESA' AS NOMBRE_EMPRESA,
                    'DIRECCION DE EMPRESA' AS DIRECCION_EMPRESA,
                    'TELEFONO DE EMPRESA' AS TELEFONO_EMPRESA,
                    'CORREO DE EMPRESA' AS CORREO_EMPRESA,
                    'DESCRIPCION DE EMPRESA' AS DESCRIPCION_EMPRESA,
                    'PAGINA WEB DE EMPRESA' AS PAGINA_WEB_EMPRESA,
                    'MOTIVO RECHAZO DE EMPRESA' AS MOTIVO_RECHAZO_EMPRESA,
                    'PERSONA ENCARGADA DE EMPRESA' AS PERSONA_ENCARGADA_EMPRESA,
                    'FECHADE REGISTRO DE EMPRESA' AS FECHA_REGISTRO_EMPRESA,
                    'ID DE USUARIO DE EMPRESA' AS ID_USUARIO_EMPRESA,
                    'ESTADO DE EMPRESA' AS ESTADO_EMPRESA,
                    'SEMESTRE REGISTRO' AS PERIODO_OFERTA,
                    'ANIO DE REGISTRO' AS ANIO_OFERTA
                UNION
                SELECT 
                    e.id_empresa AS ID_EMPRESA,
                    e.nombre_empresa AS NOMBRE_EMPRESA,
                    e.direccion AS DIRECCION_EMPRESA,
                    e.telefono AS TELEFONO_EMPRESA,
                    e.correo AS CORREO_EMPRESA,
                    e.descripcion AS DESCRIPCION_EMPRESA,
                    e.pagina_web AS PAGINA_WEB_EMPRESA,
                    e.motivo_rechazo AS MOTIVO_RECHAZO_EMPRESA,
                    e.persona_encargada AS PERSONA_ENCARGADA_EMPRESA,
                    e.fecha_registro AS FECHA_REGISTRO_EMPRESA,
                    e.id_usuario AS ID_USUARIO_EMPRESA,
                    er.estado_registro AS ESTADO_EMPRESA,
                    py.period AS PERIODO_OFERTA,
                    py.yearp AS ANIO_OFERTA
                FROM bt_empresa AS e 
                    JOIN bt_estado_registro AS er ON e.id_estado_registro = er.id_estado_registro
                    JOIN period_year AS py on e.id_period_year = py.id
                WHERE e.id_estado_registro != 2;
            '''
            exportar_reporte(query, "Reporte_Empresas_NO_Aceptadas.csv")   
        except:
            values += " - 1"
            new_dict["error"] = values

        try:
            # 2 Obtencion de informacion para reporte de registro de empresas donde solo se muestran las empresas ya registradas
            query = '''
                SELECT 
                    'ID DE EMPRESA' AS ID_EMPRESA,
                    'NOMBRE DE EMPRESA' AS NOMBRE_EMPRESA,
                    'DIRECCION DE EMPRESA' AS DIRECCION_EMPRESA,
                    'TELEFONO DE EMPRESA' AS TELEFONO_EMPRESA,
                    'CORREO DE EMPRESA' AS CORREO_EMPRESA,
                    'DESCRIPCION DE EMPRESA' AS DESCRIPCION_EMPRESA,
                    'PAGINA WEB DE EMPRESA' AS PAGINA_WEB_EMPRESA,
                    'PERSONA ENCARGADA DE EMPRESA' AS PERSONA_ENCARGADA_EMPRESA,
                    'FECHADE REGISTRO DE EMPRESA' AS FECHA_REGISTRO_EMPRESA,
                    'ID DE USUARIO DE EMPRESA' AS ID_USUARIO_EMPRESA,
                    'ESTADO DE EMPRESA' AS ESTADO_EMPRESA,
                    'SEMESTRE REGISTRO' AS PERIODO_OFERTA,
                    'ANIO DE REGISTRO' AS ANIO_OFERTA
                UNION
                SELECT 
                    e.id_empresa AS ID_EMPRESA,
                    e.nombre_empresa AS NOMBRE_EMPRESA,
                    e.direccion AS DIRECCION_EMPRESA,
                    e.telefono AS TELEFONO_EMPRESA,
                    e.correo AS CORREO_EMPRESA,
                    e.descripcion AS DESCRIPCION_EMPRESA,
                    e.pagina_web AS PAGINA_WEB_EMPRESA,
                    e.persona_encargada AS PERSONA_ENCARGADA_EMPRESA,
                    e.fecha_registro AS FECHA_REGISTRO_EMPRESA,
                    e.id_usuario AS ID_USUARIO_EMPRESA,
                    er.estado_registro AS ESTADO_EMPRESA,
                    py.period AS PERIODO_OFERTA,
                    py.yearp AS ANIO_OFERTA
                FROM bt_empresa AS e 
                    JOIN bt_estado_registro AS er ON e.id_estado_registro = er.id_estado_registro
                    JOIN period_year AS py ON e.id_period_year = py.id
                WHERE e.id_estado_registro = 2;
            '''
            exportar_reporte(query, "Reporte_Empresas_Registradas.csv")    
        except:
            values += " - 2"
            new_dict["error"] = values   

        try:
            # 3 OFERTAS LABORIALES REGISTRADAS
            query = '''
                SELECT 
                    'NOMBRE DE EMPRESA' AS NOMBRE_EMPRESA,
                    'DIRECCION DE EMPRESA' AS DIRECCION_EMPRESA,
                    'TELEFONO DE EMPRESA' AS TELEFONO_EMPRESA,
                    'CORREO DE EMPRESA' AS CORREO_EMPRESA,
                    'PERSONA ENCARGADA DE EMPRESA' AS PERSONA_ENCARGADA_EMPRESA,
                    'PUESTO DE OFERTA' AS PUESTO_OFERTA,
                    'DESCRIPCION DE OFERTA' AS DESCRIPCION_OFERTA,
                    'REQUERIMIENTOS DE OFERTA' AS REQUERIMIENTOS_OFERTA,
                    'SALARIO DE OFERTA' AS SALARIO_OFERTA,
                    'FECHA DE PUBLICACION DE OFERTA' AS FECHA_PUBLICACION_OFERTA,
                    'FECHA DE FINALIZACION DE OFERTA' AS FECHA_FINALIZACION_OFERTA,
                    'ESTADO DE OFERTA' AS ESTADO_OFERTA,
                    'ESPECIALIDAD EN OFERTA' AS ESPECIALIDAD_OFERTA,
                    'SEMESTRE DE OFERTA' AS PERIODO_OFERTA,
                    'ANIO DE OFERTA' AS ANIO_OFERTA
                UNION
                SELECT 
                    e.nombre_empresa AS NOMBRE_EMPRESA,
                    e.direccion AS DIRECCION_EMPRESA,
                    e.telefono AS TELEFONO_EMPRESA,
                    e.correo AS CORREO_EMPRESA,
                    e.persona_encargada AS PERSONA_ENCARGADA_EMPRESA,
                    ofer.puesto AS PUESTO_OFERTA,
                    ofer.descripcion AS DESCRIPCION_OFERTA,
                    ofer.requerimientos AS REQUERIMIENTOS_OFERTA,
                    ofer.salario_aproximado AS SALARIO_OFERTA,
                    ofer.fecha_inicio AS FECHA_PUBLICACION_OFERTA,
                    ofer.fecha_vigencia AS FECHA_FINALIZACION_OFERTA,
                    estOfer.estado_oferta_laboral AS ESTADO_OFERTA,
                    bae.area_especialidad AS ESPECIALIDAD_OFERTA,
                    py.period AS PERIODO_OFERTA,
                    py.yearp AS ANIO_OFERTA
                FROM bt_empresa AS e
                    JOIN bt_estado_registro AS er ON e.id_estado_registro = er.id_estado_registro
                    JOIN bt_oferta_laboral AS ofer ON e.id_empresa = ofer.id_empresa
                    JOIN bt_estado_oferta_laboral AS estOfer ON ofer.id_estado_oferta_laboral = estOfer.id_estado_oferta_laboral
                    JOIN period_year AS py ON ofer.id_period_year = py.id
                    JOIN bt_area_especialidad AS bae ON ofer.id_area_especialidad = bae.id_area_especialidad
                WHERE e.id_estado_registro = 2;
            '''
            exportar_reporte(query, "Reporte_Ofertas_Laborales_Registradas.csv")
        except:
            values += " - 3"
            new_dict["error"] = values 

        try:
            #REPORTE 4, OFERTAS LABORIALES ACEPTADAS
            query = '''
                SELECT 
                    'NOMBRE DE EMPRESA' AS NOMBRE_EMPRESA,
                    'DIRECCION DE EMPRESA' AS DIRECCION_EMPRESA,
                    'TELEFONO DE EMPRESA' AS TELEFONO_EMPRESA,
                    'CORREO DE EMPRESA' AS CORREO_EMPRESA,
                    'ENCARGADO DE EMPRESA' AS PERSONA_ENCARGADA_EMPRESA,
                    'PUESTO DE OFERTA' AS PUESTO_OFERTA,
                    'DESCRIPCION DE OFERTA' AS DESCRIPCION_OFERTA,
                    'REQUERIMIENTOS DE OFERTA' AS REQUERIMIENTOS_OFERTA,
                    'SALARIO DE OFERTA' AS SALARIO_OFERTA,
                    'FECHA DE PUBLICACION' AS FECHA_PUBLICACION_OFERTA,
                    'FECHA DE EXPIRACION' AS FECHA_FINALIZACION_OFERTA,
                    'ESTADO DE OFERTA' AS ESTADO_OFERTA,
                    'ESPECIALIDAD EN OFERTA' AS ESPECIALIDAD_OFERTA,
                    'PERIODO DE OFERTA' AS PERIODO_OFERTA,
                    'ANIO DE OFERTA' AS ANIO_OFERTA
                UNION
                SELECT 
                    e.nombre_empresa AS NOMBRE_EMPRESA,
                    e.direccion AS DIRECCION_EMPRESA,
                    e.telefono AS TELEFONO_EMPRESA,
                    e.correo AS CORREO_EMPRESA,
                    e.persona_encargada AS PERSONA_ENCARGADA_EMPRESA,
                    ofer.puesto AS PUESTO_OFERTA,
                    ofer.descripcion AS DESCRIPCION_OFERTA,
                    ofer.requerimientos AS REQUERIMIENTOS_OFERTA,
                    ofer.salario_aproximado AS SALARIO_OFERTA,
                    ofer.fecha_inicio AS FECHA_PUBLICACION_OFERTA,
                    ofer.fecha_vigencia AS FECHA_FINALIZACION_OFERTA,
                    estOfer.estado_oferta_laboral AS ESTADO_OFERTA,
                    bae.area_especialidad AS ESPECIALIDAD_OFERTA,
                    py.period AS PERIODO_OFERTA,
                    py.yearp AS ANIO_OFERTA
                FROM bt_empresa AS e
                    JOIN bt_estado_registro er ON e.id_estado_registro = er.id_estado_registro
                    JOIN bt_oferta_laboral ofer ON e.id_empresa = ofer.id_empresa
                    JOIN bt_estado_oferta_laboral estOfer ON ofer.id_estado_oferta_laboral = estOfer.id_estado_oferta_laboral
                    JOIN period_year py on ofer.id_period_year = py.id
                    JOIN bt_area_especialidad bae on ofer.id_area_especialidad = bae.id_area_especialidad
                WHERE e.id_estado_registro = 2
                AND estOfer.id_estado_oferta_laboral = 2;
            '''
            exportar_reporte(query, "Reporte_Ofertas_Laborales_Aceptadas.csv")
        except:
            values += " - 4"
            new_dict["error"] = values 

        try:
            # REPORTE 5 PROMERIO DE SALARIO POR AREA DE ESPECIALIDAD
            query = '''
                SELECT 
                    'Especialidad' AS Especialidad,
                    'Promedio_salarial' AS Promedio_salarial ,
                    'Anio' AS anio,
                    'Periodo' AS Periodo
                UNION
                SELECT 
                    a.area_especialidad AS Especialidad, 
                    AVG(ol.salario_aproximado) AS Promedio_salarial, 
                    py.yearp AS anio, 
                    py.period AS Periodo
                FROM bt_oferta_laboral AS ol
                        JOIN bt_area_especialidad AS a ON ol.id_area_especialidad = a.id_area_especialidad
                        JOIN period_year AS py ON ol.id_period_year = py.id
                WHERE ol.id_estado_oferta_laboral = 2
                GROUP BY a.id_area_especialidad, ol.id_period_year
                ORDER BY Promedio_salarial DESC;
            '''
            exportar_reporte(query, "Reporte_Promedio_Salarial_Especialidad.csv")
        except:
            values += " - 5"
            new_dict["error"] = values 
        
        try:
            # REPORTE 6, OFERTAs CON SU NUMERO DE VISITAS
            query = '''
                SELECT 
                    'ID DE EMPRESA' AS Id_empresa,
                    'NOMBRE DE EMPRESA' AS Nombre_Empresa,
                    'CONTACTO DE EMPRESA' AS Contacto_Empresa,
                    'PUESTO EN OFERTA' AS Puesto,
                    'DESCRIPCION DE OFERTA' AS Descripcion,
                    'FECHA DE PUBLICACION' AS Fecha_Publicacion,
                    'SALARIO APROX. EN Qs' AS Salario,
                    'NUMERO DE VISITAS' AS Numero_Vistas,
                    'SEMESTRE DE OFERTA' AS Periodo,
                    'ANIO DE OFERTA' AS anio
                UNION
                SELECT
                    be.id_empresa AS Id_empresa,
                    be.nombre_empresa AS Nombre_Empresa, 
                    be.correo AS Contacto_Empresa,
                    ofl.puesto AS Puesto, 
                    ofl.descripcion AS Descripcion, 
                    ofl.fecha_inicio AS Fecha_Publicacion,
                    ofl.salario_aproximado AS Salario, 
                    ofl.visitas AS Numero_Vistas, 
                    py.period AS Periodo,
                    py.yearp AS anio
                FROM bt_oferta_laboral AS ofl
                    JOIN bt_empresa AS be ON ofl.id_empresa = be.id_empresa
                    JOIN period_year AS py ON ofl.id_period_year = py.id
                WHERE 
                    be.id_estado_registro = 2
                    AND ofl.id_estado_oferta_laboral = 2
                ORDER BY Numero_Vistas DESC;
            '''
            exportar_reporte(query, "Reporte_Visitas_Por_Oferta.csv")
        except:
            values += " - 6"
            new_dict["error"] = values 

        try:
            # REPORTE 7, OFERTAs CON SU CANTIDAD DE APLICANTES
            query = '''
                SELECT 
                    'ID OFERTA' AS idoferta,
                    'PUESTO DE TARBAJO' AS Puesto,
                    'EMPRESA' AS Empresa,
                    'CANTIDAD APLICANTES' AS CantidadAplicantes,
                    'PERIODO\' AS Periodo,
                    'ANIO\' AS Anio
                UNION
                SELECT 
                    ef.id_oferta_laboral AS idoferta,
                    ol.puesto AS Puesto,
                    emp.nombre_empresa AS Empresa,
                    COUNT(ef.id_oferta_laboral) AS CantidadAplicantes,
                    py.period AS Periodo,
                    py.yearp AS Anio
                FROM bt_oferta_laboral AS ol 
                    JOIN bt_estudiante_oferta AS ef ON ol.id_oferta_laboral = ef.id_oferta_laboral
                    JOIN bt_empresa AS emp ON ol.id_empresa = emp.id_empresa
                    JOIN period_year AS py ON ol.id_period_year = py.id
                    JOIN bt_estado_oferta_laboral AS beol ON ol.id_estado_oferta_laboral = beol.id_estado_oferta_laboral
                WHERE ol.id_estado_oferta_laboral = 2
                GROUP BY idoferta
                UNION
                SELECT 
                    ol.id_oferta_laboral AS idoferta,
                    ol.puesto AS Puesto,
                    emp.nombre_empresa AS Empresa, 
                    '0' AS CantidadAplicantes,
                    py.period AS Periodo,
                    py.yearp AS Anio
                FROM bt_oferta_laboral AS ol
                    JOIN bt_empresa AS emp ON ol.id_empresa = emp.id_empresa
                    JOIN period_year AS py ON ol.id_period_year = py.id
                    JOIN bt_estado_oferta_laboral AS beol ON ol.id_estado_oferta_laboral = beol.id_estado_oferta_laboral
                WHERE 
                    ol.id_estado_oferta_laboral = 2
                    AND ol.id_oferta_laboral NOT IN (SELECT id_oferta_laboral AS idU FROM bt_estudiante_oferta)
                ORDER BY CantidadAplicantes DESC;
            '''
            exportar_reporte(query, "Reporte_Oferta_y_Cantidad_Aplicantes.csv")
        except:
            values += " - 7"
            new_dict["error"] = values

        try:
            # REPORTE 8, SOLICITUDES RECIBIDAS POR EMPRESA
            query = '''
                SELECT 
                    'ID EMPRESA' AS idEmpresa,
                    'NOMBRE DE EMPRESA' AS Empresa,
                    'DIRECCION DE EMPRESA' AS DirecEmpresa,
                    'TELEFONO DE EMPRESA' AS Telefono,
                    'CORREO DE EMPRESA' AS Correo,
                    'ESTADO APLICACION' AS Estado,
                    'No. SOLICITUDES RECIBIDAS' AS SilicRecibidas,
                    'SEMESTRE' AS periodo,
                    'ANIO' AS anio
                UNION
                SELECT 
                    emp.id_empresa AS idEmpresa,
                    emp.nombre_empresa AS Empresa,
                    emp.direccion AS DirecEmpresa,
                    emp.telefono AS Telefono,
                    emp.correo AS Correo,
                    eof.estado_aplicacion AS Estado,
                    COUNT(*) AS SilicRecibidas,
                    py.period AS periodo,
                    py.yearp AS anio
                FROM bt_estudiante_oferta AS eo
                    INNER JOIN bt_estado_aplicacion AS eof ON eo.id_estado_aplicacion = eof.id_estado_aplicacion
                    INNER JOIN bt_oferta_laboral AS ol ON eo.id_oferta_laboral = ol.id_oferta_laboral
                    INNER JOIN bt_empresa AS emp ON ol.id_empresa = emp.id_empresa
                    JOIN period_year AS py ON ol.id_period_year = py.id
                WHERE eof.id_estado_aplicacion = 1
                GROUP BY emp.id_empresa AND py.period AND py.yearp;
            '''
            exportar_reporte(query, "Reporte_Solicitudes_RECIBIDAS_Empresa.csv")
        except:
            values += " - 8"
            new_dict["error"] = values

        try:
            # REPORTE 9, SOLICITUDES REVISADAS POR EMPRESA
            query = '''
                SELECT 
                    'ID EMPRESA' AS idEmpresa,
                    'NOMBRE DE EMPRESA' AS Empresa,
                    'DIRECCION DE EMPRESA' AS DirecEmpresa,
                    'TELEFONO DE EMPRESA' AS Telefono,
                    'CORREO DE EMPRESA' AS Correo,
                    'ESTADO APLICACION' as Estado,
                    'No. SOLICITUDES REVISADAS' AS SilicRecibidas,
                    'SEMESTRE' AS periodo,
                    'ANIO' AS anio
                UNION
                SELECT 
                    emp.id_empresa AS idEmpresa,
                    emp.nombre_empresa AS Empresa,
                    emp.direccion AS DirecEmpresa,
                    emp.telefono AS Telefono,
                    emp.correo AS Correo,
                    eof.estado_aplicacion AS Estado,
                    COUNT(*) AS SilicRecibidas,
                    py.period AS periodo,
                    py.yearp AS anio
                FROM bt_estudiante_oferta AS eo
                    INNER JOIN bt_estado_aplicacion AS eof ON eo.id_estado_aplicacion = eof.id_estado_aplicacion
                    INNER JOIN bt_oferta_laboral AS ol ON eo.id_oferta_laboral = ol.id_oferta_laboral
                    INNER JOIN bt_empresa AS emp ON ol.id_empresa = emp.id_empresa
                    JOIN period_year AS py ON ol.id_period_year = py.id
                WHERE eof.id_estado_aplicacion = 2
                GROUP BY emp.id_empresa AND py.period AND py.yearp;
            '''
            exportar_reporte(query, "Reporte_Solicitudes_REVISADAS_Empresa.csv")
        except:
            values += " - 9"
            new_dict["error"] = values

        try:
            # REPORTE 10, Estudiantes Contactados por Empresa
            query = '''
                SELECT 
                    'ID EMPRESA' AS idEmpresa,
                    'NOMBRE DE EMPRESA' AS Empresa,
                    'DIRECCION DE EMPRESA' AS DirecEmpresa,
                    'TELEFONO DE EMPRESA' AS Telefono,
                    'CORREO DE EMPRESA' AS Correo,
                    'ESTADO APLICACION' AS Estado,
                    'No. SOLICITANTES CONTACTADOS' AS SilicRecibidas,
                    'SEMESTRE' AS periodo,
                    'ANIO' AS anio
                UNION
                SELECT 
                    emp.id_empresa AS idEmpresa,
                    emp.nombre_empresa AS Empresa,
                    emp.direccion AS DirecEmpresa,
                    emp.telefono AS Telefono,
                    emp.correo AS Correo,
                    eof.estado_aplicacion AS Estado,
                    COUNT(*) AS SilicRecibidas,
                    py.period AS periodo,
                    py.yearp AS anio
                FROM bt_estudiante_oferta AS eo
                    INNER JOIN bt_estado_aplicacion AS eof ON eo.id_estado_aplicacion = eof.id_estado_aplicacion
                    INNER JOIN bt_oferta_laboral AS ol ON eo.id_oferta_laboral = ol.id_oferta_laboral
                    INNER JOIN bt_empresa AS emp ON ol.id_empresa = emp.id_empresa
                    JOIN period_year AS py ON ol.id_period_year = py.id
                WHERE eof.id_estado_aplicacion = 3
                GROUP BY emp.id_empresa AND py.period AND py.yearp;
            '''
            exportar_reporte(query, "Reporte_Solicitantes_CONTACTADOS_Empresa.csv")
        except:
            values += " - 10"
            new_dict["error"] = values

        try:
            # REPORTE 11, Estudiantes Contactados por Empresa
            query = '''
                SELECT 
                    'ID EMPRESA' AS idEmpresa,
                    'NOMBRE DE EMPRESA' AS Empresa,
                    'DIRECCION DE EMPRESA' AS DirecEmpresa,
                    'TELEFONO DE EMPRESA' AS Telefono,
                    'CORREO DE EMPRESA' AS Correo,
                    'ESTADO APLICACION' AS Estado,
                    'No. SOLICITANTES CONTRATADOS' AS SilicRecibidas,
                    'SEMESTRE' AS periodo,
                    'ANIO' AS anio
                UNION
                SELECT 
                    emp.id_empresa AS idEmpresa,
                    emp.nombre_empresa AS Empresa,
                    emp.direccion AS DirecEmpresa,
                    emp.telefono AS Telefono,
                    emp.correo AS Correo,
                    eof.estado_aplicacion AS Estado,
                    COUNT(*) AS SilicRecibidas,
                    py.period AS periodo,
                    py.yearp AS anio
                FROM bt_estudiante_oferta AS eo
                INNER JOIN bt_estado_aplicacion AS eof ON eo.id_estado_aplicacion = eof.id_estado_aplicacion
                INNER JOIN bt_oferta_laboral AS ol ON eo.id_oferta_laboral = ol.id_oferta_laboral
                INNER JOIN bt_empresa AS emp ON ol.id_empresa = emp.id_empresa
                JOIN period_year AS py ON ol.id_period_year = py.id
                WHERE eof.id_estado_aplicacion = 4
                GROUP BY emp.id_empresa AND py.period AND py.yearp;
            '''
            exportar_reporte(query, "Reporte_Solicitantes_CONTRATADOS_Empresa.csv")
        except:
            values += " - 11"
            new_dict["error"] = values
    except:
        new_dict["success"] = False
        new_dict["msg"] = "Falla en reporteria"
        new_dict["error"] = values
        return json.dumps(new_dict)
    
    new_dict["success"] = True
    new_dict["msg"] = "Reporteria creada exitosamente "
    new_dict["error"] = values
    return json.dumps(new_dict)

def obtener_cv():
    try: 
        data = request.vars
        filename = data['documento_cv']

        path = os.path.join(request.folder, "uploads/bolsa_de_trabajo/")
        pathfilename = os.path.join(path, filename)

        with open(pathfilename, "rb") as pdf_file:
            encoded_string = base64.encodebytes(pdf_file.read())

        return encoded_string
    except:
        return 'nop'
    