from gluon.serializers import json
import json as json_parser
import datetime

ruta_iconos = "/cpfecys/static/images/iconos_reclutamiento"

@auth.requires_login()
@auth.requires_membership('Academic')
def registro_solicitud():
    activo = 0 # 0: desactivado; 1:Activo
    max_intentos = 3
    usuario = db(db.auth_user.id == auth.user.id).select().first()
    fecha_sistema = datetime.datetime.now()
    fecha_hoy = datetime.date(fecha_sistema.year, fecha_sistema.month, fecha_sistema.day)
    act_anio = -1
    act_periodo = 'x'
    act_periodo_numero = -1
    id_proceso = -1
    tabla_validacion = DIV(XML(""" """))
    
    #******************Validando que exista un periodo activo y se encuentre el rago de las fechas
    row_activo = db.executesql("""
        SELECT
            pro.id,
            pro.periodo,
            pro.anio,
            pro.fecha_inicio,
            pro.fecha_fin,
            pro.activo,
            per.id,
            per.name
        FROM cpfecys.rec_proceso AS pro
            INNER JOIN cpfecys.period AS per ON pro.periodo = per.id
        WHERE pro.activo = 'T';
    """)

    if len(row_activo) == 1:
        id_proceso = row_activo[0][0]
        act_periodo_numero = row_activo[0][1]
        fecha_inicio = row_activo[0][3]
        fecha_fin = row_activo[0][4]
        if fecha_hoy >= fecha_inicio and fecha_hoy <= fecha_fin:
            activo = 1
            act_anio = str(row_activo[0][2])
            act_periodo = row_activo[0][7]
            tabla_validacion = mensaje_validacion(act_anio, act_periodo, 1, 0)
        else:
            tabla_validacion = mensaje_validacion(act_anio, act_periodo, 2, 0)
    else:
        tabla_validacion = mensaje_validacion(act_anio, act_periodo, 2, 0)

    #************* Validando que tenga oportunidades para realizar el proceso
    intentos = 0
    if (activo == 1) & (len(row_activo) == 1):
        solicitud = db((db.rec_solicitud.id_usuario == auth.user.id) & (db.rec_solicitud.anio == row_activo[0][2])
                    & (db.rec_solicitud.periodo == row_activo[0][1]) & (db.rec_solicitud.proceso == row_activo[0][0])).select(db.rec_solicitud.intentos).first()
        
        if solicitud != None:
            intentos = solicitud.intentos
            tabla_validacion = mensaje_validacion(act_anio, act_periodo, 4, (max_intentos - intentos))

        if intentos >= max_intentos:
            activo = 0
            tabla_validacion = mensaje_validacion(act_anio, act_periodo, 3, 0)

    #******************************* Realiza todas las operaciones solo si el periodo está activo *******************
    if activo == 1:
        #************************OBTENIENDO AREAS Y PROYECTO DESDE LA BASE DE DATOS *********************
        area_level = db(db.area_level.id != None).select()
        tamanio_area = len(area_level)
        i_area = 1
        json_proyectos = '['
        for area_proyecto in area_level:
            if area_proyecto.id == 1:
                academico = db.executesql(f"""
                    SELECT
                        CAST(project_id AS SIGNED) AS code,
                        SUBSTRING_INDEX(SUBSTRING_INDEX(name, ' (S', 1), '(S', 1) AS name
                    FROM cpfecys.project
                    WHERE 
                        area_level = {area_proyecto.id}
                        AND project_id NOT LIKE 'PV%'
                    
                    UNION
                    
                    SELECT 
                        project_id,
                        name
                    FROM cpfecys.project
                    WHERE 
                        area_level = {area_proyecto.id}
                        AND project_id LIKE 'PV%';
                """)
                json_proyectos += '{'
                json_proyectos += f'"area_codigo": "{area_proyecto.id}", '
                json_proyectos += f'"area_nombre": "{area_proyecto.name}", '
                json_proyectos += '"proyectos": ['
                tamanio_aca = len(academico)
                i_aca = 1
                for pr_academico in academico:
                    json_proyectos += '{'
                    if i_aca < tamanio_aca:
                        json_proyectos += f'"codigo": "{pr_academico[0].encode("utf-8").strip()}", "nombre": "{pr_academico[1].encode("utf-8").strip()}' 
                        json_proyectos += '}, '
                    else:
                        json_proyectos += f'"codigo": "{pr_academico[0].encode("utf-8").strip()}", "nombre": "{pr_academico[1].encode("utf-8").strip()}"'
                        json_proyectos += '}'
                    i_aca += 1
                json_proyectos += ']'
                if i_area < tamanio_area: # se cierre el } del area académica
                    json_proyectos += '},'
                else:
                    json_proyectos += '}'
            else:
                otros_proyectos = db.executesql(f"""
                    SELECT
                        project_id AS code,
                        name
                    FROM cpfecys.project
                    WHERE area_level = {area_proyecto.id};
                """)
                json_proyectos += '{'
                json_proyectos += f'"area_codigo": "{area_proyecto.id}", '
                json_proyectos += f'"area_nombre": "{area_proyecto.name}", '
                json_proyectos += '"proyectos": ['
                tamanio_otros = len(otros_proyectos)
                i_otros = 1
                for pr_otro in otros_proyectos:
                    json_proyectos += '{'
                    if i_otros < tamanio_otros:
                        json_proyectos += f'"codigo": "{pr_otro[0].encode("utf-8").strip()}", "nombre": "{pr_otro[1].encode("utf-8").strip()}"'
                        json_proyectos += '}, '
                    else:
                        json_proyectos += f'"codigo": "{pr_otro[0].encode("utf-8").strip()}", "nombre": "{pr_otro[1].encode("utf-8").strip()}"'
                        json_proyectos += '}'

                    i_otros += 1
                json_proyectos += ']'
                if i_area < tamanio_area: # se cierre el } del area
                    json_proyectos += '},'
                else:
                    json_proyectos += '}'
            i_area += 1
        json_proyectos += ']'
        #********************* TERMINA OBTENER AREAS Y PROYECTOS DESDE LA BASE DE DATOS*****************
        
    else: #**************************** Solo devuelve las varialbes si no está activo ningún proceso *****************
        area_level = None
        json_proyectos ='[{"code": "0"}]'

    return dict(
        activo=activo,
        act_anio=act_anio,
        act_periodo_numero=act_periodo_numero,
        tabla_validacion=tabla_validacion,
        area_level=area_level,
        usuario=usuario,
        json_proyectos=json(json_proyectos),
        ruta_iconos=ruta_iconos,
        id_proceso=id_proceso
    )

@auth.requires_login()
@auth.requires_membership('Academic')
def mensaje_validacion(anio, periodo, caso, oportunidades):
    tabla = DIV(XML(""" """))
    if caso == 1:
        tabla = DIV(XML(f"""
                <table>
                    <tr>
                        <td>
                            <h4 style="color: #009933;">
                                <img src="{ruta_iconos}/success.png" height="16" width="16"> Sistema activo para solicitud de practicas finales
                            </h4>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <h4 style="color: #009933;">
                                <img src="{ruta_iconos}/success.png" height="16" width="16"> Proceso activo para {T(periodo)} del {anio}
                            </h4>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <h4 style="color: #009933;">
                                <img src="{ruta_iconos}/success.png" height="16" width="16"> Cuenta con oportunidades para realizar el proceso
                            </h4>
                        </td>
                    </tr>
                </table>
            """))
    elif caso == 2:
        tabla= DIV(XML(f"""
                <table>
                    <tr>
                        <td>
                            <h4 style="color: #ff0000;">
                                <img src="{ruta_iconos}/fail.png" height="16" width="16"> Sistema no activo para solicitud de practicas finales
                            </h4>
                        </td>
                    </tr>
                </table>
            """))
    elif caso == 3:
        tabla= DIV(XML(f"""
                <table>
                    <tr>
                        <td>
                            <h4 style="color: #009933;">
                                <img src="{ruta_iconos}/success.png" height="16" width="16"> Sistema activo para solicitud de practicas finales
                            </h4>
                        </td>
                    </tr>
                    <tr>
                        <td>
                             <h4 style="color: #009933;">
                                <img src="{ruta_iconos}/success.png" height="16" width="16"> Proceso activo para {T(periodo)} del {anio}
                            </h4>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <h4 style="color: #ff0000;">
                                <img src="{ruta_iconos}/fail.png" height="16" width="16"> No cuenta con oportunidades para realizar el proceso
                            </h4>
                        </td>
                    </tr>
                </table>
            """))
    elif caso == 4:
        tabla= DIV(XML(f"""
                <table>
                    <tr>
                        <td>
                            <h4 style="color: #009933;">
                                <img src="{ruta_iconos}/success.png" height="16" width="16"> Sistema activo para solicitud de practicas finales
                            </h4>
                        </td>
                    </tr>
                    <tr>
                        <td>
                             <h4 style="color: #009933;">
                                <img src="{ruta_iconos}/success.png" height="16" width="16"> Proceso activo para {T(periodo)} del {anio}
                            </h4>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <h4 style="color: #009933;">
                                <img src="{ruta_iconos}/success.png" height="16" width="16"> Cuenta con {oportunidades} oportunidades para realizar el proceso
                            </h4>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <h4 style="color: #ff3300;">
                                <img src="{ruta_iconos}/aviso.png" height="16" width="16"> Nota: realizar otra solicitud anula la anterior
                            </h4>
                        </td>
                    </tr>
                </table>
            """))
        
    return tabla

@auth.requires_login()
@auth.requires_membership('Academic')
def mtd_guardar():
    nombre = request.vars['nombre']
    apellido = request.vars['apellido']
    cui = request.vars['cui']
    carnet = request.vars['carnet']
    direccion = request.vars['direccion']
    telefono = request.vars['telefono']
    trabaja = request.vars['trabaja']
    id_proceso = request.vars['idproceso']
    anio_proceso = request.vars['anioproceso']
    periodo_proceso = request.vars['periodoproceso']
    str_proyectos = request.vars['proyectos']
    ar_cv = request.vars['inp_cv']
    ar_lista_cursos = request.vars['inp_lis_cursos']

    if (carnet != None) & (id_proceso != None) & (anio_proceso != None) & (periodo_proceso != None) & (ar_cv != None) & (ar_lista_cursos != None):
        # Eliminando solicitud, si existe
        intentos = eliminar_solicitud_existente(anio_proceso, periodo_proceso, id_proceso)
        intentos += 1
        
        # Insertando la solicitud
        id_solicitud = db.rec_solicitud.insert(
                            id_usuario=auth.user.id,
                            anio=anio_proceso,
                            periodo=periodo_proceso,
                            curriculum=ar_cv,
                            listado_cursos=ar_lista_cursos,
                            intentos=intentos,
                            asignado=False,
                            proceso=id_proceso
                        )

        #Insertando detalle de la solicitud
        lista = json_parser.loads(str_proyectos)
        for proyecto in lista:
            db.rec_detalle_solicitud.insert(
                area=proyecto['pro_area'],
                id_proyecto=proyecto['pro_codigo'],
                nombre_proyecto=proyecto['pro_nombre'],
                anio_aprobacion=proyecto['apr_anio'],
                semestre_aprobacion=proyecto['apr_semestre'],
                nota_aprobacion=proyecto['apr_nota'],
                catedratico=proyecto['apr_catedratico'],
                estado=4,
                solicitud=id_solicitud
            )

        #Actualizando datos personales
        usuario = db(db.auth_user.id == auth.user.id).select(
                        db.auth_user.email,
                        db.auth_user.first_name,
                        db.auth_user.last_name,
                        db.auth_user.cui,
                        db.auth_user.phone,
                        db.auth_user.home_address,
                        db.auth_user.working
                    ).first()
        destinatario = ''
        if usuario != None:
            destinatario = usuario.email
            usuario.first_name = nombre
            usuario.last_name = apellido
            usuario.cui = cui
            usuario.phone = telefono
            usuario.home_address = direccion
            usuario.working = True if int(str(trabaja)) == 1 else None
            usuario.update_record()

        #Enviando correo
        try:            
            enviar_correo(contenido_correo(lista),destinatario)
        except Exception: 
            pass
        session.flash = T('Se guardó la solicitud correctamente')
    else:
        session.flash = T('Ocurrio un error en la solicitud')

    return "ok"

@auth.requires_login()
@auth.requires_membership('Academic')
def eliminar_solicitud_existente(anio_proceso, periodo_proceso, id_proceso):
    solicitud = db((db.rec_solicitud.id_usuario == auth.user.id) & (db.rec_solicitud.anio == anio_proceso)
                & (db.rec_solicitud.periodo == periodo_proceso) & (db.rec_solicitud.proceso == id_proceso)).select(db.rec_solicitud.intentos).first()
    intentos = 0    
    if solicitud != None:
        intentos = solicitud.intentos
        #Borrando en cascada
        solicitud.delete_record()
    
    return intentos

@auth.requires_login()
@auth.requires_membership('Academic')
def enviar_correo(mensaje, destinatario):
    was_sent = mail.send(to=[destinatario], subject='DTT: Registro de solicitud de proyecto', message=mensaje)

    db.mailer_log.insert(
        sent_message=mensaje,
        destination=str(destinatario),
        result_log=':',
        success=was_sent
    )

    mensaje = str(was_sent)
    return mensaje

@auth.requires_login()
@auth.requires_membership('Academic')
def contenido_correo(lista):
    contador = 1
    contenido = "Se ha registrado su solicitud para proyecto de prácticas finales.\n\n"
    contenido += "Proyectos seleccionados:\n"

    for item in lista:
        if int(item['pro_area'].encode('utf-8').strip()) == 1:
            periodo_letras = ''
            if int(item['apr_semestre'].encode('utf-8').strip()) == 100:
                periodo_letras = 'Primer semestre'
            elif int(item['apr_semestre'].encode('utf-8').strip()) == 101:
                periodo_letras = 'Vacaciones junio'
            elif int(item['apr_semestre'].encode('utf-8').strip()) == 200:
                periodo_letras = 'Segundo semestre'
            elif int(item['apr_semestre'].encode('utf-8').strip()) == 201:
                periodo_letras = 'Vacaciones diciembre'
            contenido += f"{contador}. Nombre del proyecto: {item['pro_nombre'].encode('utf-8')}, Año aprobación: {item['apr_anio'].encode('utf-8')}, Periodo aprobación: {periodo_letras}, Nota aprobación: {item['apr_nota'].encode('utf-8')}, Catedrático: {item['apr_catedratico'].encode('utf-8')}\n"
        else:
            contenido += f"{contador}. Nombre del proyecto: {item['pro_nombre'].encode('utf-8')}\n"
        contador += 1

    contenido += "\nSistema de Seguimiento de La Escuela de Ciencias y Sistemas\n"
    contenido += "Facultad de Ingeniería - Universidad de San Carlos de Guatemala\n"
    return contenido
