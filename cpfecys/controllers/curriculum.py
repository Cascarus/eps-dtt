import json
import base64
import uuid
import os

# Cargando info extra
def curriculum():
    ruta_iconos = "/cpfecys/static/images/iconos_reclutamiento"
    #TODO enviar valores vacios al no cargar info de bd
    try:
        id_usuario_cv = db.executesql(f'SELECT id_estudiante_cv FROM bt_estudiante_cv WHERE id_usuario = {auth.user.id};',as_dict=True)[0]['id_estudiante_cv']
    except:
        id_usuario_cv = -1
    
    try:    
        if id_usuario_cv == -1:
            return dict(
                ruta_iconos=ruta_iconos,
                areas_es=[],
                datos_user={},
                datos_cv={},
                areas_est=[],
                activo=1,
                certificaciones=[],
                habilidades=[],
                habilidades_usuario=[]
            ) 
        areas_es = db.executesql('SELECT area_especialidad, id_area_especialidad FROM bt_area_especialidad;', as_dict=True)
        query_user = f'''
            SELECT 
                first_name,
                last_name,
                email,
                phone 
            FROM auth_user AS a 
                INNER JOIN bt_estudiante_cv AS cv ON cv.id_usuario = a.id 
            WHERE a.id = {auth.user.id};
        '''
        query_cv = f'''
            SELECT 
                cv.correo,
                cv.telefono,
                cv.creditos_aprobados,
                cv.cursos_aprobados,
                cv.fecha_nacimiento AS edad 
            FROM bt_estudiante_cv AS cv 
            WHERE id_estudiante_cv = {id_usuario_cv};
        '''
        query_areas = f'''
            SELECT 
                est.id_area_especialidad,
                est.id_estado_visibilidad,
                area.area_especialidad 
            FROM bt_area_especialidad AS area 
                INNER JOIN bt_estudiante_especialidad AS est ON area.id_area_especialidad = est.id_area_especialidad 
                INNER JOIN bt_estudiante_cv AS cv ON est.id_estudiante_cv = cv.id_estudiante_cv 
            WHERE cv.id_estudiante_cv = {id_usuario_cv};
        '''
        query_certificaciones = f"""
            SELECT 
                id_certificacion,
                nombre_certificacion,
                enlace,
                fecha_expedicion,
                tipo, 
                '0' AS paraEditar, 
                '0' AS esNueva 
            FROM bt_certificacion 
            WHERE id_estudiante_cv = {id_usuario_cv};
        """
        query_habilidades = f"""
            SELECT 
                hab.id_habilidad,
                hab.habilidad 
            FROM bt_estudiante_habilidad AS est 
                INNER JOIN bt_habilidad AS hab ON est.id_habilidad = hab.id_habilidad
            WHERE est.id_estudiante_cv = {id_usuario_cv};
        """
        datos_user = db.executesql(query_user,as_dict=True)
        datos_cv = db.executesql(query_cv, as_dict=True)
        areas_est = db.executesql(query_areas, as_dict=True)
        certificaciones = db.executesql(query_certificaciones, as_dict=True)
        habilidades = db.executesql("SELECT * FROM bt_habilidad;", as_dict=True)
        habilidades_usuario = db.executesql(query_habilidades, as_dict=True)
        tamanios = db.executesql('SELECT id_tamanio_archivo, tamanio_curriculum FROM bt_tamanio_archivo;',as_dict=True)
        
        return dict(
            ruta_iconos=ruta_iconos,
            areas_es=areas_es,
            datos_user=datos_user[0],
            datos_cv=datos_cv[0],
            areas_est=areas_est,
            activo=1,
            certificaciones=certificaciones,
            habilidades=habilidades,
            habilidades_usuario=habilidades_usuario,
            tamanios=tamanios[0]
        )
    except:
        return dict(
            ruta_iconos=ruta_iconos,
            areas_es=[],
            datos_user={},
            datos_cv={},
            areas_est=[],
            activo=1,
            certificaciones=[],
            habilidades=[],
            habilidades_usuario=[]
        ) 

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Academic'))
def mi_cv():
    try:
        id_usuario_cv = db.executesql(f'SELECT id_estudiante_cv FROM bt_estudiante_cv WHERE id_usuario = {auth.user.id};', as_dict=True)[0]['id_estudiante_cv']
    except:
        id_usuario_cv = -1    
    
    if id_usuario_cv == -1:
        redirect(URL('cpfecys', 'curriculum', 'previa'))        
    
    try:
        query_user = f'''
            SELECT 
                first_name,
                last_name,
                email,
                phone
            FROM auth_user AS a
                INNER JOIN bt_estudiante_cv AS cv ON cv.id_usuario = a.id 
            WHERE a.id = {auth.user.id};
        '''
        query_cv = f'''
            SELECT 
                cv.creditos_aprobados,
                cv.cursos_aprobados,
                cv.correo,
                cv.telefono,
                fecha_nacimiento AS edad 
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
        query_habilidades = f"""
            SELECT
                hab.id_habilidad,
                hab.habilidad
            FROM bt_estudiante_habilidad AS est
                INNER JOIN  bt_habilidad AS hab ON est.id_habilidad = hab.id_habilidad 
            WHERE est.id_estudiante_cv = {id_usuario_cv};
        """
        query_experiencias = f'''
            SELECT 
                id_experiencia,puesto,
                empresa,
                fecha_inicio,
                fecha_fin,
                descripcion
            FROM bt_experiencia_laboral AS ex 
                INNER JOIN bt_estudiante_cv AS es ON ex.id_estudiante_cv = es.id_estudiante_cv 
            WHERE es.id_estudiante_cv = {id_usuario_cv};
        '''
        datos_user = db.executesql(query_user, as_dict=True)
        datos_cv = db.executesql(query_cv, as_dict=True)
        areas_est = db.executesql(query_areas, as_dict=True)
        certificaciones = db.executesql(f'SELECT id_certificacion, nombre_certificacion, enlace, fecha_expedicion, tipo FROM bt_certificacion WHERE id_estudiante_cv = {id_usuario_cv};', as_dict=True)
        habilidades_usuario = db.executesql(query_habilidades, as_dict=True)
        experiencia_lab = db.executesql(query_experiencias, as_dict=True)
        tamanios = db.executesql('SELECT id_tamanio_archivo, tamanio_curriculum FROM bt_tamanio_archivo;', as_dict=True)

        ## para saber la visibilidad
        visibilidad = db.executesql(f'SELECT * FROM bt_estudiante_especialidad WHERE id_estudiante_cv = {id_usuario_cv};', as_dict=True)
        resp_visibilidad = "Privado"
        if len(visibilidad) > 0:
            if visibilidad[0]['id_estado_visibilidad'] == 2:
                resp_visibilidad = 'Público'

        return dict(
            experiencia_lab=experiencia_lab,
            datos_user=datos_user[0],
            datos_cv=datos_cv[0],
            areas_est=areas_est,
            activo=1,
            certificaciones=certificaciones,
            habilidades_usuario=habilidades_usuario,
            tamanios=tamanios,
            visibility=resp_visibilidad
        )
    except:
        return dict(datos_user={},datos_cv={},areas_est=[],activo=1,certificaciones=[],habilidades_usuario=[]) 

def previa():
    try:
        id_usuario_cv = db.executesql(f'SELECT id_estudiante_cv FROM bt_estudiante_cv WHERE id_usuario = {auth.user.id};',as_dict=True)[0]['id_estudiante_cv']        
    except:
        id_usuario_cv = -1    
    
    if id_usuario_cv != -1:
        redirect(URL('cpfecys', 'curriculum', 'curriculum'))
    
    return dict()

def crear_cv(): 
    query_insert = f'''
        INSERT INTO 
            bt_estudiante_cv(
                correo,
                fecha_nacimiento,
                telefono,
                creditos_aprobados,
                cursos_aprobados,
                id_usuario
            ) 
        VALUES (
            "{auth.user.email}",
            "1990-01-01",
            "{auth.user.phone}",
            0,
            "",
            {auth.user.id}
        );
    '''
    try:
        db.executesql(query_insert)
        redirect(URL('cpfecys', 'curriculum', 'curriculum'))
    except Exception as ex:
        redirect(URL('default', 'home'))
    
    return dict()

def eliminar_area():
    try:
        data = request.vars
        id_area = data['id_area']
        db.executesql(f'DELETE FROM bt_estudiante_especialidad WHERE id_area_especialidad = {id_area};')
    except:
        return json.dumps({'success': False, 'msg': 'Error al eliminar'})    
    
    return 'ok'

def user_cv_id():
    try:
        id_usuario_cv = db.executesql(f'SELECT id_estudiante_cv FROM bt_estudiante_cv WHERE id_usuario = {auth.user.id};',as_dict=True)[0]['id_estudiante_cv']  
        query_areas = f'''
            SELECT 
                est.id_area_especialidad,
                est.id_estado_visibilidad,
                area.area_especialidad 
            FROM bt_area_especialidad AS area 
                INNER JOIN bt_estudiante_especialidad AS est ON area.id_area_especialidad = est.id_area_especialidad 
                INNER JOIN bt_estudiante_cv AS cv ON est.id_estudiante_cv = cv.id_estudiante_cv 
            WHERE cv.id_estudiante_cv = {id_usuario_cv};'''
        areas_est = db.executesql(query_areas, as_dict=True) 
        return json.dumps(areas_est)    
    except:
        ...  

    return '' 

def obtener_experiencia_lab():
    try:
        id_usuario_cv = db.executesql(f'SELECT id_estudiante_cv FROM bt_estudiante_cv WHERE id_usuario = {auth.user.id};',as_dict=True)[0]['id_estudiante_cv']        
    except:
        id_usuario_cv = -1    
    try:
        query_experiencia = f'''
            SELECT 
                id_experiencia,
                puesto,
                empresa,
                fecha_inicio,
                fecha_fin,
                descripcion
            FROM bt_experiencia_laboral AS ex 
                INNER JOIN bt_estudiante_cv AS es ON ex.id_estudiante_cv = es.id_estudiante_cv 
            WHERE es.id_estudiante_cv = {id_usuario_cv};
        '''
        experiencia_lab = db.executesql(query_experiencia, as_dict=True)
    except:
        experiencia_lab = []

    return json.dumps(experiencia_lab, default=default)

def obtener_certificaciones():
    try:
        id_usuario_cv = db.executesql(f'SELECT id_estudiante_cv FROM bt_estudiante_cv WHERE id_usuario = {auth.user.id};',as_dict=True)[0]['id_estudiante_cv']        
    except:
        id_usuario_cv = -1    

    try:
        query_certificaciones = f'''
            SELECT 
                id_certificacion,
                nombre_certificacion,
                enlace,
                fecha_expedicion,
                tipo,
                '0' AS paraEditar,
                '0' AS esNueva 
            FROM bt_certificacion 
            WHERE id_estudiante_cv = {id_usuario_cv};
        '''
        certificaciones = db.executesql(query_certificaciones, as_dict=True)
    except:
        certificaciones = []

    return json.dumps(certificaciones,default=default) 

def obtener_certificacion():
    try: 
        data = request.vars
        filename = data['ceritificacion']
        path = os.path.join(request.folder, "uploads/bolsa_de_trabajo/")
        pathfilename = os.path.join(path, filename)

        with open(pathfilename, "rb") as pdf_file:
            encoded_string = base64.b64encode(pdf_file.read())

        return encoded_string
    except:
        return 'nop'

def obtener_max_id_cert(): 
    try:
        max_id_cert = db.executesql("SELECT IFNULL(MAX(id_certificacion), 0) AS maxIdCert FROM bt_certificacion LIMIT 1;", as_dict=True)[0]['maxIdCert']
    except:
        max_id_cert = 0

    return json.dumps(max_id_cert, default=default) 

def obtener_habilidades():
    try:
        id_usuario_cv = db.executesql(f'SELECT id_estudiante_cv FROM bt_estudiante_cv WHERE id_usuario = {auth.user.id};',as_dict=True)[0]['id_estudiante_cv']      
    except:
        id_usuario_cv = -1    
    try:
        query_habilidades = f'''
            SELECT
                hab.id_habilidad,
                hab.habilidad
            FROM bt_estudiante_habilidad AS est
                INNER JOIN bt_habilidad AS hab ON est.id_habilidad = hab.id_habilidad
            WHERE est.id_estudiante_cv = {id_usuario_cv};
        '''
        habilidades_usuario = db.executesql(query_habilidades, as_dict=True)
    except:
        habilidades_usuario = []

    return json.dumps(habilidades_usuario)

def registrar_cv():
    try:
        id_usuario_cv = db.executesql(f'SELECT id_estudiante_cv FROM bt_estudiante_cv WHERE id_usuario = {auth.user.id};',as_dict=True)[0]['id_estudiante_cv']
    except:    
        return json.dumps({'success': False, 'msg': 'Error al actualizar primero'}) 
    
    try:
        db.executesql("START TRANSACTION;")
        
        data = request.vars
        edad = data['edad']
        correo = data['correo']
        telefono = data['telefono']
        creditos = data['creditos']
        nombre_cv = data['nombre_cv']
        cursos = data['documento_cv']
        privacidad = data['privacidad']

        areas_especialidad = json.loads(data['areas_especialidad'])
        experiencia_laboral = json.loads(data['experiencia_laboral'])
        habilidades_tecnicas = json.loads(data['habilidades_tecnicas'])

        for area in areas_especialidad:
            id = area['id_area_especialidad']
            qs = f'INSERT INTO bt_estudiante_especialidad VALUES({id_usuario_cv}, {id}, {privacidad});'
            db.executesql(qs)

        qs = f'UPDATE bt_estudiante_especialidad SET id_estado_visibilidad= {privacidad} WHERE id_estudiante_cv = {id_usuario_cv};'
        db.executesql(qs)

        for exp in experiencia_laboral:
            puesto = exp['puesto']
            empresa = exp['empresa']
            fecha_in = exp['fecha_inicio']
            descripcion = exp['descripcion']
            fecha_fin = f"\"{exp['fecha_fin']}\"" if exp['fecha_fin'] != "" else 'null'
            qs = f'''
                INSERT INTO 
                    bt_experiencia_laboral (
                        puesto,
                        empresa,
                        fecha_inicio,
                        fecha_fin,
                        descripcion,
                        id_estudiante_cv
                    ) 
                VALUES (
                    "{puesto}",
                    "{empresa}", 
                    "{fecha_in}", 
                    {fecha_fin},
                    "{descripcion}",
                    {id_usuario_cv}
                );
            '''
            db.executesql(qs)

        for hab in habilidades_tecnicas:
            id = hab['id_habilidad']
            qs = f'INSERT INTO bt_estudiante_habilidad VALUES({id_usuario_cv}, {id});'
            db.executesql(qs)    
        
        qs = f'''
            UPDATE bt_estudiante_cv 
            SET 
                correo = "{correo}",
                fecha_nacimiento = "{edad}",
                telefono = "{telefono}",
                creditos_aprobados = {creditos}
            WHERE id_estudiante_cv = {id_usuario_cv};
        '''
        if nombre_cv != "undefined":
            if cursos == "":
                qs = f'''
                    UPDATE bt_estudiante_cv
                    SET 
                        correo = "{correo}",
                        fecha_nacimiento = "{edad}",
                        telefono = "{telefono}",
                        creditos_aprobados = {creditos} 
                    WHERE id_estudiante_cv = {id_usuario_cv};
                '''
            else:
                uid = str(uuid.uuid4())
                documento = str(cursos).partition(",")[2]
                filename = bt_store_file(documento, uid)
                qs = f'''
                    UPDATE bt_estudiante_cv 
                    SET
                        correo = "{correo}",
                        fecha_nacimiento = "{edad}",
                        telefono = "{telefono}",
                        creditos_aprobados = {creditos},
                        cursos_aprobados = "{filename}"
                    WHERE id_estudiante_cv = {id_usuario_cv};
                '''
        db.executesql(qs)
        db.executesql("COMMIT;")
        return 'ok'
    except Exception as ex:
        db.executesql("ROLLBACK;")
        return json.dumps({'success': False, 'msg': 'Error al actualizar', 'err': ex})    

def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()

def bt_store_file(base64_param, filename=None, path=None):
    bytes = base64.b64decode(base64_param)
    path = os.path.join(request.folder, "uploads/bolsa_de_trabajo/")
    if not os.path.exists(path):
        os.makedirs(path)
    
    filename = f'{filename}.pdf'
    pathfilename = os.path.join(path, filename)
    dest_file = open(pathfilename, 'wb')
    try:
        dest_file.write(bytes)
    finally:
        dest_file.close()
    
    return filename

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
    
def actualizar_experiencia():
    try:
        db.executesql(f'SELECT id_estudiante_cv FROM bt_estudiante_cv WHERE id_usuario = {auth.user.id};',as_dict=True)[0]['id_estudiante_cv']        
    except:
        ...    
    
    try:
        data = request.vars
        query = f"""
            UPDATE bt_experiencia_laboral 
            SET 
                puesto = '{data['puesto']}',
                empresa = '{data['empresa']}',
                fecha_inicio = '{data['fecha_inicio']}',
                fecha_fin = '{data['fecha_fin']}',
                descripcion = '{data['descripcion']}'
            WHERE id_experiencia = {data['id_experiencia']};
        """
        db.executesql(query)
    except:
        return json.dumps({'success': False, 'msg': 'Error al actualizar'})
    
    return json.dumps({'success': True, 'msg': 'Actualizacion correcta'})

def actualizar_certificaciones():
    nuevo_enlace = ""
    nuevo_tipo = 0
    try:
        id_usuario_cv = db.executesql(f'SELECT id_estudiante_cv FROM bt_estudiante_cv WHERE id_usuario = {auth.user.id};',as_dict=True)[0]['id_estudiante_cv']        
    except:  
        return json.dumps({'success': False, 'msg': 'No actualizo CV'})
    try:
        db.executesql("START TRANSACTION;")
        data = request.vars
        cert = json.loads(data['certificacion'])
        nombre = cert['nombre_certificacion']
        fecha = cert['fecha_expedicion']
        enlace = cert['enlace']
        id_certificacion = cert['id_certificacion']
        nuevo_enlace = enlace
        nuevo_tipo = cert['tipo']
        if cert['tipo'] == 1:
            if cert['esNueva'] == '1':
                ## si o si tuvo que ingresar un archivo
                archivoo = cert['pdf_certificacion']
                uid = str(uuid.uuid4())
                documento = str(archivoo).partition(",")[2]
                filename = bt_store_file(documento, uid)
                qs = f'''
                    INSERT INTO 
                        bt_certificacion (
                            id_certificacion,
                            nombre_certificacion,
                            enlace,
                            fecha_expedicion,
                            id_estudiante_cv,
                            tipo
                        ) 
                    VALUES ( 
                        {id_certificacion},
                        "{nombre}",
                        "{filename}",
                        "{fecha}",
                        {id_usuario_cv},
                        1
                    );
                '''
                db.executesql(qs) 
                nuevo_enlace = str(filename)
            elif cert['paraEditar'] == '1':
                ## el archivo es opcional
                filename = enlace
                if 'pdf_certificacion' in cert:
                    if not (cert['pdf_certificacion'] == ""):
                        archivoo = cert['pdf_certificacion']
                        uid = str(uuid.uuid4())
                        documento = str(archivoo).partition(",")[2]
                        filename = bt_store_file(documento, uid)

                query = f"""
                    UPDATE 
                        bt_certificacion 
                    SET 
                        nombre_certificacion = '{nombre}',
                        fecha_expedicion = '{fecha}',
                        enlace = '{filename}'
                    WHERE id_certificacion = {id_certificacion};
                """
                db.executesql(query)
                nuevo_enlace = str(filename)
        else:
            if cert['esNueva'] == '1':
                qs = f'''
                    INSERT INTO
                        bt_certificacion (
                            id_certificacion,
                            nombre_certificacion,
                            enlace,
                            fecha_expedicion,
                            id_estudiante_cv,
                            tipo
                        ) 
                    VALUES (
                        {id_certificacion},
                        "{nombre}",
                        "{enlace}",
                        "{fecha}",
                        {id_usuario_cv},
                        0
                    );
                '''
            elif cert['paraEditar'] == '1':
                ## un update
                query = f"""
                    UPDATE bt_certificacion 
                    SET 
                        nombre_certificacion = '{nombre}',
                        fecha_expedicion = '{fecha}',
                        enlace = '{enlace}'
                    WHERE id_certificacion = {id_certificacion};
                """
            db.executesql(qs) 
    except:
        return json.dumps({'success': False, 'msg': 'Error al actualizar'})
    
    respuesta = {}
    respuesta["success"] = True
    respuesta["msg"] = "Actualizado"
    respuesta["enlace"] = nuevo_enlace
    respuesta["tipo"] = nuevo_tipo
    return json.dumps(respuesta)

def eliminar_experiencia():
    try:
        data = request.vars
        id_exp = data['id_experiencia']
        qs = f'DELETE FROM bt_experiencia_laboral WHERE id_experiencia = {id_exp};'
        db.executesql(qs)
    except:
        return json.dumps({'success': False, 'msg': 'Error al eliminar'})    
    
    return 'ok'

def eliminar_certificacion():
    try:
        data = request.vars
        id_cert = data['id_certificacion']
        qs = f'DELETE FROM bt_certificacion WHERE id_certificacion = {id_cert};'
        db.executesql(qs)
    except:
        return json.dumps({'success': False, 'msg': 'Error al eliminar'})    
    
    return 'ok'

def eliminar_habilidad():
    try:
        data = request.vars
        id_hab = data['id_habilidad']
        qs = f'DELETE FROM bt_estudiante_habilidad WHERE id_habilidad = {id_hab};'
        db.executesql(qs)
    except:
        return json.dumps({'success': False, 'msg': 'Error al eliminar'})    
    return 'ok'

def rollback():
    db.executesql('ROLLBACK;')