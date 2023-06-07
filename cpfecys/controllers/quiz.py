import cpfecys
import json
import datetime

##Tesis 2.0
def consult_quiz():
    ecys_var = True if request.vars['ecys'] == "True" else False
    period = cpfecys.current_year_period()
    id_periodo_c = request.vars['period']
    id_project = request.vars['project']
    if request.vars['period']:
        period = db(db.period_year.id == id_periodo_c).select().first()

    project = db(db.project.id == id_project).select().first() 
    lista = db(db.project.id == id_project).select(
        db.tb_metadata_quiz.id_quiz,
        db.tb_metadata_quiz.nombre,
        db.tb_metadata_quiz.fecha_creacion,
        db.tb_metadata_quiz.creador, 
        db.auth_user.first_name, 
        db.auth_user.last_name, 
        db.project.name,
        db.tb_quiz_actividad.id, 
        join=[
                db.auth_user.on(db.tb_metadata_quiz.creador == db.auth_user.id), 
                db.project.on(db.project.id == db.tb_metadata_quiz.curso)
            ],
        left=db.tb_quiz_actividad.on(db.tb_quiz_actividad.id_quiz == db.tb_metadata_quiz.id_quiz),
        groupby=[db.tb_metadata_quiz.id,db.auth_user.first_name, db.auth_user.last_name, db.project.name],
        orderby=db.tb_metadata_quiz.id_quiz 
    )

    back_button = A(
        I(_class="fa fa-arrow-left", _aria_hiden='true'),
        " Atras",
        _class='btn btn-primary',
        _href=URL('quiz', 'home_quiz', vars=dict(period=id_periodo_c, project=id_project))
    )

    return dict(
        ecys_var=ecys_var,
        periodo=period,
        project=project,
        id_periodo_c=id_periodo_c,
        id_project=id_project,
        lista=lista,
        back_button=back_button
    )

def create_quiz():
    ecys_var = True if request.vars['ecys'] == "True" else False
    period = cpfecys.current_year_period()
    id_periodo_c = request.vars['period']
    id_project = request.vars['project']
    project = db(db.project.id == id_project).select(db.project.project_id).first()  

    back_button = A(
        I(_class="fa fa-arrow-left", _aria_hiden='true'),
        " Atras",
        _class='btn btn-primary',
        _href=URL('quiz', 'home_quiz', vars=dict(period=id_periodo_c, project=id_project))
    )

    return dict(
        ecys_var=ecys_var,
        periodo=period,
        project=project,
        id_periodo_c=id_periodo_c,
        id_project=id_project,
        back_button=back_button
    )

@auth.requires_login()
def edit_quiz():    
    periodo = request.vars['period']
    project = request.vars['project']

    back_button = A(
        I(_class="fa fa-arrow-left", _aria_hiden='true'),
        " Atras",
        _class='btn btn-primary',
        _href=URL('quiz', 'consult_quiz', vars=dict(period=periodo, project=project))
    )

    user_id = auth.user.id
    my_where = (db.user_project.assigned_user == user_id) & (db.user_project.project == project)
    asignacion = db(my_where).select().first()

    permiso = True if asignacion != None else False

    x = tuple(request.args) #Obtiene los argumentos que vienen sin un descriptor
    y = str(''.join(x)) #Une los argumentos, porque al final de la cadena siempre viene uno en blanco
    
    r = redis_db_4
    ide = int(y) #id de quiz
    lista = db((db.tb_metadata_quiz.id_quiz == ide) & (db.tb_metadata_quiz.curso == project)).select(
                db.tb_metadata_quiz.creador, 
                db.tb_metadata_quiz.curso
            )
    creador = 0
    curso = 0
    #OBTENGO LA ESTRUCTUA JSON DEL QUIZ
    for quiz in lista:
        creador = quiz.creador
        curso = quiz.curso
    cadena_redis = f'uid:{creador}:curso:{curso}:quiz:{ide}'
    datos = r.hget(cadena_redis, 'preguntas')
    
    vacio = True if datos is None else False
    
    #OBTENGO LA METADA DEL QUIZ
    lista = db((db.tb_metadata_quiz.id_quiz == ide) & (db.tb_metadata_quiz.curso == project)).select(
                db.tb_metadata_quiz.nombre,
                db.tb_metadata_quiz.id,
                db.tb_metadata_quiz.id_quiz,
                db.auth_user.first_name, 
                db.auth_user.last_name, 
                join=[
                    db.auth_user.on(db.tb_metadata_quiz.creador == db.auth_user.id), 
                    db.project.on(db.project.id == db.tb_metadata_quiz.curso)
                ]
            )
    if not vacio:
        datos = datos.decode()
        quiz = datos.replace('{[','{"PREGUNTAS" : [')
    
    objProject = db(db.project.id == project).select().first()

    return dict(
        quiz=quiz,
        metadata=lista.first(),
        vacio=vacio,
        permiso=permiso,
        project=objProject,
        idperiodoc=periodo,
        idproject=project,
        back_button=back_button
    )

@auth.requires_login()
def evaluacion():
    r = redis_db_4

    period = cpfecys.current_year_period()
    periodo = request.vars['period']
    projecto = request.vars['project']
    project = db(db.project.id == projecto).select().first()
    
    x = tuple(request.args)
    y = str(''.join(x))
    id_programacion = int(y)
    
    error = False
    msj_error = ""

    programacion = db(db.vw_quiz_actividad.id == int(id_programacion)).select(db.vw_quiz_actividad.ALL).first()
    if int(period.id) != int(periodo):
        error = True
        msj_error = "El periodo actual no corresponde al periodo de la evaluacion"

    ##Verifico si es privado
    privado = session.bloqueado

    ##Verifico si aun sigue estando activo
    activo = True if programacion.Estado_actual == 'Activo' else False

    ##Obtengo la metadata del quiz
    metadata = db(db.tb_metadata_quiz.id_quiz == programacion.id_quiz).select(
                    db.tb_metadata_quiz.creador, 
                    db.tb_metadata_quiz.curso
                ).first()

    cadena_redis = f'uid:{metadata.creador}:curso:{metadata.curso}:quiz:{programacion.id_quiz}'
    datos = r.hget(cadena_redis, 'preguntas')

    vacio = True if datos is None else False

    json_quiz = ""
    template_respuestas = ""
    if not vacio:
        datos = datos.decode()
        datos = datos.replace('\n','')
        datos = datos.replace('}]}"','}]}')
        json_quiz = datos.replace('{[','{"PREGUNTAS" : [')

        ##Si el quiz esta activo recupero el detalle
        if activo:
            template_respuestas = json.loads(json_quiz)
            for pregunta in template_respuestas["PREGUNTAS"]:
                if pregunta["tipo"] == "multiple":
                    for respuesta in pregunta["respuesta"]:
                        respuesta["correcta"] = "false"
                elif pregunta["tipo"] == "veracidad":
                    pregunta["respuesta"] = None
                else:
                    pregunta["respuesta"] = None

    return dict(
        period=period,
        project=project,
        programacion=programacion,
        error=error,
        msjError=msj_error,
        privado=privado,
        activo=activo,
        json_quiz=json_quiz,
        metadata=metadata,
        bloqueado=session.bloqueado,
        vacio=vacio
    )

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator') or auth.has_membership('Academic') or auth.has_membership('Ecys-Administrator'))
def home_quiz(): 
    period = cpfecys.current_year_period()
    periodo = request.vars['period']
    project = request.vars['project']
    
    if request.vars['period']:
        period = db(db.period_year.id == periodo).select().first()

    user_id = auth.user.id
    my_where = (db.user_project.assigned_user == user_id) & (db.user_project.project == project)
    asignacion = db(my_where).select().first()
    
    permiso = True if asignacion != None else False
    ecys_var = True if request.vars['ecys'] == "True" else False
    
    return dict(
        ecys_var=ecys_var, 
        periodo=period, 
        course=project, 
        period=periodo,
        permiso=permiso
    )

@auth.requires_login()
def nota_estudiante():
    actividad = request.vars['actividad']
    usuario = request.vars['uid']
    estado = request.vars['state']
    r = calcular_nota(actividad, usuario)
    total_preguntas = r[0][3]
    pregunta_buenas = r[0][4]
    nota = r[0][5]
    return dict(total=total_preguntas, buenas=pregunta_buenas, nota=nota, estado=estado)

@auth.requires_login()
def obtener_revision_quiz():
    x = tuple(request.args) #Obtiene los argumentos que vienen sin un descriptor
    y = str(''.join(x)) #Une los argumentos, porque al final de la cadena siempre viene uno en blanco
    project = request.vars['project']
    
    before = request.env.http_referer.split('/')
    before = before[len(before) - 1]
    back_button = A(
        I(_class="fa fa-arrow-left", _aria_hiden='true'),
        f" {T('Back')}",
        _class='btn btn-primary',
        _href=URL('quiz', before)
    )
    ide = request.vars['quid']
    user = request.vars['user']


    r = redis_db_4
    actividad = int(y) #ID de quiz

    lista = db((db.tb_metadata_quiz.id_quiz == ide) & (db.tb_metadata_quiz.curso == project)).select(
                db.tb_metadata_quiz.creador, 
                db.tb_metadata_quiz.curso
            )
    creador = 0
    curso = 0
    #OBTENGO LA ESTRUCTUA JSON DEL QUIZ
    for quiz in lista:
        creador = quiz.creador
        curso = quiz.curso

    cadena_redis = f'uid:{creador}:curso:{curso}:quiz:{ide}'
    datos = r.hget(cadena_redis, 'preguntas')
    
    vacio = False
    if datos is None:
        vacio = True

    #OBTENGO LA METADA DEL QUIZ
    lista = db((db.tb_metadata_quiz.id_quiz == ide) & (db.tb_metadata_quiz.curso == project)).select(
                db.tb_metadata_quiz.ALL, 
                db.auth_user.first_name, 
                db.auth_user.last_name, 
                db.project.name, 
                join=[
                    db.auth_user.on(db.tb_metadata_quiz.creador == db.auth_user.id), 
                    db.project.on(db.project.id == db.tb_metadata_quiz.curso)
                ]
            )
    if not vacio:
        datos = datos.decode()
        quiz = datos.replace('{[','{"PREGUNTAS" : [')

    #obtengo las respuestas del alumno
    respuestas = db((db.tb_detalle_respuestas_carnet.id_actividad == actividad) & (db.tb_detalle_respuestas_carnet.id_estudiante == user)).select(
                        db.tb_detalle_respuestas_carnet.ALL, 
                        orderby=db.tb_detalle_respuestas_carnet.id_pregunta
                    )
    usuario = db(db.auth_user.id == int(user)).select(db.auth_user.first_name, db.auth_user.last_name, db.auth_user.username).first()
    return dict(quiz=quiz, metadata=lista.first(), vacio=vacio, permiso=True, respuestas=respuestas, back_button=back_button, usuario=usuario) 

@auth.requires_login()
def programacion_test():
    project = request.vars['project']
    period = request.vars['period']
    back_button = A(
        I(_class="fa fa-arrow-left", _aria_hiden='true'),
        f" {T('Back')}",
        _class='btn btn-primary',
        _href=URL('quiz', 'consult_quiz', vars=dict(period=period, project=project))
    )
    x = tuple(request.args)
    y = str(''.join(x))
    ide = int(y)

    #OBTENGO LA METADA DEL QUIZ
    lista = db((db.tb_metadata_quiz.id_quiz == ide) & (db.tb_metadata_quiz.curso == project)).select(
                db.tb_metadata_quiz.nombre,
                db.tb_metadata_quiz.fecha_creacion,
                db.tb_metadata_quiz.id_quiz,
                db.auth_user.first_name, 
                db.auth_user.last_name, 
                db.project.name, 
                join=[
                    db.auth_user.on(db.tb_metadata_quiz.creador == db.auth_user.id), 
                    db.project.on(db.project.id == db.tb_metadata_quiz.curso)
                ]
            )

    #OBTENGO LOS CODIGOS DE ACTIVIDADES QUE PERENECEN A UN QUIZ
    categorias = db().select(
                    db.activity_category.id,
                    db.activity_category.category,
                    join=[
                        db.equivalencia_quiz_category.on(db.equivalencia_quiz_category.categorie == db.activity_category.id)
                    ] 
                )
    period = cpfecys.current_year_period()
    idproject = request.vars['project']
    project = db(db.project.id == idproject).select(db.project.id).first() 

    return dict(
        metadata=lista.first(),
        categorias=categorias,
        periodo=period,
        project=project,
        back_button=back_button
    ) 

@auth.requires_login()
def reporte():    
    periodo = request.vars['period']
    project = request.vars['project']
    back_button = A(
        I(_class="fa fa-arrow-left", _aria_hiden='true'),
        f" {T('Back')}",
        _class='btn btn-primary',
        _href=URL('quiz', 'reportes', vars=dict(period=periodo, project=project))
    )

    x = tuple(request.args)
    Id_actividad = str(''.join(x))

    user_id = auth.user.id
    my_where = (db.user_project.assigned_user == user_id) & (db.user_project.project == project)
    asignacion = db(my_where).select().first()
    
    permiso = False
    if asignacion != None :
        permiso = True

    sql = f"""
        SELECT
            tna.*,
            a.carnet,
            CAST((tna.cantidad_buenas * 100 / tna.cantidad_preguntas) AS DECIMAL(5, 2)) AS porcentaje,
            a.id_auth_user 
        FROM cpfecys.tb_nota_actividad_quiz AS tna
            INNER JOIN academic AS a ON a.id_auth_user = tna.id_estudiante 
        WHERE tna.id_actividad = {Id_actividad}
        ORDER BY a.carnet ASC;
    """
    notas = db.executesql(sql)
    vacio = False
    if notas == None:
        vacio = True
    
    qry = f"""
        SELECT
            ca.id,
            ca.name,
            tqa.fecha,
            tqa.inicio,
            tqa.duracion,
            tqa.private,
            tqa.keyword,
            tmq.nombre,
            tqa.id_quiz
        FROM course_activity AS ca
            INNER JOIN tb_quiz_actividad AS tqa ON tqa.id_actividad = ca.id
            INNER JOIN tb_metadata_quiz AS tmq ON tmq.id_quiz = tqa.id_quiz 
        WHERE ca.id = {Id_actividad};
    """
    metadata = db.executesql(qry)
    return dict(
        notas=notas,
        metadata=metadata,
        vacio=vacio,
        permiso=permiso,
        actividad=Id_actividad,
        periodo=periodo,
        project=project,
        back_button=back_button
    )

@auth.requires_login()
def reportes():
    period = cpfecys.current_year_period()
    periodo = request.vars['period']
    project = request.vars['project']
    back_button = A(
        I(_class="fa fa-arrow-left", _aria_hiden='true'),
        f" {T('Back')}",
        _class='btn btn-primary',
        _href=URL('quiz', 'home_quiz', vars=dict(period=periodo, project=project))
    )
    if request.vars['period']:
        period = db(db.period_year.id == periodo).select().first()

    user_id = auth.user.id
    my_where = (db.user_project.assigned_user == user_id) & (db.user_project.project == project)
    asignacion = db(my_where).select(db.user_project.id).first()
    
    permiso = True if asignacion != None else False
    lab = True
    if auth.has_membership('Student'):
        lab = True
    elif auth.has_membership('Teacher'):
        lab = False

    my_query = (db.project.id == project) & (db.course_activity.semester == period) & (db.course_activity.laboratory == lab)
    programaciones = db(my_query).select(
        db.tb_quiz_actividad.id,
		db.tb_quiz_actividad.id_actividad,
		db.tb_quiz_actividad.id_quiz,
		db.tb_quiz_actividad.fecha,
		db.tb_quiz_actividad.inicio,
		db.tb_quiz_actividad.duracion,
		db.tb_quiz_actividad.finalizado,
		db.tb_quiz_actividad.private,
		db.tb_quiz_actividad.keyword,
		db.tb_metadata_quiz.nombre,
		db.tb_metadata_quiz.fecha_creacion,
		db.tb_metadata_quiz.creador,
		db.tb_metadata_quiz.id,
		db.tb_metadata_quiz.curso, 
		db.project.name,
		db.auth_user.id,
		db.auth_user.first_name, 
        db.auth_user.last_name,
		db.course_activity_category.category,
		db.activity_category.description,
		db.course_activity.name,
		db.course_activity.semester,
        join=[
            db.tb_metadata_quiz.on(
                db.tb_metadata_quiz.id_quiz == db.tb_quiz_actividad.id_quiz    
            ),
            db.project.on(
                db.project.id == db.tb_metadata_quiz.curso    
            ),
            db.auth_user.on(
                db.auth_user.id == db.tb_metadata_quiz.creador    
            ),
            db.course_activity.on(
                db.course_activity.id == db.tb_quiz_actividad.id_actividad    
            ),
            db.course_activity_category.on(
                db.course_activity_category.id == db.course_activity.course_activity_category    
            ),
            db.activity_category.on(
                db.activity_category.id == db.course_activity_category.category    
            )
        ]
    )
    return dict(periodo=period, course=project, period=periodo, programaciones=programaciones, permiso=permiso, back_button=back_button)

@auth.requires_login()
def take_quiz():
    period = cpfecys.current_year_period()
    periodo = request.vars['period']
    project = request.vars['project']
    user_id = auth.user.id

    if request.vars['period']:
        period = db(db.period_year.id == periodo).select().first()

    projecto = db(db.project.id == project).select().first()
    my_query = (db.vw_quiz_actividad.id_project == int(project)) & (db.vw_quiz_actividad.semestre == int(period))
    
    programaciones = db(my_query).select(
                        db.vw_quiz_actividad.actividad_nombre,
                        db.vw_quiz_actividad.laboratorio,
                        db.vw_quiz_actividad.nombre_quiz,
                        db.vw_quiz_actividad.fecha,
                        db.vw_quiz_actividad.inicio,
                        db.vw_quiz_actividad.duracion,
                        db.vw_quiz_actividad.Estado_actual,
                        db.vw_quiz_actividad.id,
                        db.vw_quiz_actividad.id_quiz,
                        db.vw_quiz_actividad.id_actividad
                    )
    
    return dict(
        periodo=period, 
        course=project, 
        period=periodo, 
        programaciones=programaciones, 
        project=projecto, 
        user=user_id
    )

##Tesis 2.0
@auth.requires_login()
def test():
    project = request.vars['project']
    period = request.vars['period']
    back_button = A(
        I(_class="fa fa-arrow-left", _aria_hiden='true'),
        f" {T('Back')}",
        _class='btn btn-primary',
        _href=URL('quiz', 'consult_quiz', vars=dict(period=period, project=project))
    )

    user_id = auth.user.id
    my_where = (db.user_project.assigned_user == user_id) & (db.user_project.project == project)
    asignacion = db(my_where).select(db.user_project.id).first()

    permiso = True if asignacion != None else False

    x = tuple(request.args) #Obtiene los argumentos que vienen sin un descriptor
    y = str(''.join(x)) #Une los argumentos, porque al final de la cadena siempre viene uno en blanco

    r = redis_db_4
    ide = int(y) #ID de quiz
    lista = db((db.tb_metadata_quiz.id_quiz == ide) & (db.tb_metadata_quiz.curso == project)).select(
                db.tb_metadata_quiz.creador, 
                db.tb_metadata_quiz.curso
            )
    creador = 0
    curso = 0
    #Obtengo los datos del quiz
    for quiz in lista:
        creador = quiz.creador
        curso = quiz.curso

    cadena_redis = f'uid:{creador}:curso:{curso}:quiz:{ide}'
    datos = r.hget(cadena_redis, 'preguntas')

    vacio = True if datos is None else False
    
    #Obtengo la metadata del quiz
    lista = db((db.tb_metadata_quiz.id_quiz == ide) & (db.tb_metadata_quiz.curso == project)).select(
                db.tb_metadata_quiz.nombre,
                db.tb_metadata_quiz.fecha_creacion, 
                db.auth_user.first_name, 
                db.auth_user.last_name, 
                db.project.name, 
                join=[
                    db.auth_user.on(db.tb_metadata_quiz.creador == db.auth_user.id), 
                    db.project.on(db.project.id == db.tb_metadata_quiz.curso)
                ]
            )
    if not vacio:
        datos = datos.decode()
        quiz = datos.replace('{[','{"PREGUNTAS" : [')

    return dict(quiz=quiz, metadata=lista.first(), vacio=vacio, permiso=permiso, back_button=back_button) 

@auth.requires_login()
def test_programacion():
    try:
        pid_actividiad = request.vars['id_actividad']
        pid_quiz = request.vars['id_quiz']
        p_fecha = request.vars['fecha']
        p_inicio = request.vars['inicio']
        p_duracion = request.vars['duracion']
        project = request.vars['project']
        period = request.vars['period']
        back_button = A(
            I(_class="fa fa-arrow-left", _aria_hiden='true'),
            f" {T('Back')}",
            _class='btn btn-primary',
            _href=URL('quiz', 'consult_quiz', vars=dict(period=period, project=project))
        )
        db.tb_quiz_actividad.insert(
            id_actividad=pid_actividiad,
            id_quiz=pid_quiz,
            fecha=p_fecha,
            inicio=p_inicio,
            duracion=p_duracion,
            finalizado=0,
            private=0
        )
        db.commit()

        metadata = db.executesql(f"""
            SELECT 
		        p.name AS curso, 
		        ca.name AS actividad, 
                ac.category AS categoria, 
                tmq.nombre AS quiz 
            FROM course_activity AS ca
                INNER JOIN project AS p ON p.id = ca.assignation
                INNER JOIN course_activity_category AS cac ON ca.course_activity_category = cac.id
                INNER JOIN activity_category AS ac ON ac.id = cac.category
                INNER JOIN tb_quiz_actividad AS tqa ON tqa.id_actividad = ca.id
                INNER JOIN tb_metadata_quiz AS tmq ON tmq.id_quiz = tqa.id_quiz
            WHERE ca.id = {pid_actividiad}
        """)
    except Exception as error:
        curso = metadata[0][0]
        pmensaje = f"Ha ocurrido un error. Erro: {error}"
        p_resultado = "Fallida"
        p_error = f"{error}"
        p_name = metadata[0][3]
        p_activitie = metadata[0][1]
        pcategorie = metadata[0][2]
        p_fecha = p_fecha
        p_duracion = p_duracion
        phora = p_inicio
        p_estado = "Error"
        p_result = 0
    else:
        curso = metadata[0][0]
        pmensaje = "Se ha programado el la activadad correctamente"
        p_resultado = "Exitosa"
        p_error = None
        p_name = metadata[0][3]
        p_activitie = metadata[0][1]
        pcategorie = metadata[0][2]
        p_fecha = p_fecha
        p_duracion = p_duracion
        phora = p_inicio
        p_estado = "Pendiente de inicio"
        p_result = 1
    finally:
        return dict(
            mensaje=pmensaje,
            resultado=p_resultado,
            error=p_error,
            result=p_result,  
            name=p_name,
            activitie=p_activitie,
            categorie=pcategorie,
            fecha=p_fecha,
            duracion=p_duracion,
            hora=phora,
            estado=p_estado,
            curso=curso,
            back_button=back_button
        )

@auth.requires_login()
def test_programacion_protegida():
    try:
        pid_actividad = request.vars['id_actividad']
        pid_quiz = request.vars['id_quiz']
        p_fecha = request.vars['fecha']
        p_inicio = request.vars['inicio']
        p_duracion = request.vars['duracion']
        p_clave = request.vars['clave']
        project = request.vars['project']
        period = request.vars['period']
        back_button = A(
            I(_class="fa fa-arrow-left", _aria_hiden='true'),
            f" {T('Back')}",
            _class='btn btn-primary',
            _href=URL('quiz', 'consult_quiz', vars=dict(period=period, project=project))
        )
        db.tb_quiz_actividad.insert(
            id_actividad=pid_actividad,
            id_quiz=pid_quiz,
            fecha=p_fecha,
            inicio=p_inicio,
            duracion=p_duracion,
            finalizado=0,
            private=1,
            keyword=p_clave
        )
        db.commit()
        metadata = db.executesql(f"""
            SELECT 
		        p.name AS curso, 
		        ca.name AS actividad, 
                ac.category AS categoria, 
                tmq.nombre AS quiz,
                tqa.keyword AS clave 
            FROM course_activity AS ca
                INNER JOIN project AS p ON p.id = ca.assignation
                INNER JOIN course_activity_category AS cac ON ca.course_activity_category = cac.id
                INNER JOIN activity_category AS ac ON ac.id = cac.category
                INNER JOIN tb_quiz_actividad AS tqa ON tqa.id_actividad = ca.id
                INNER JOIN tb_metadata_quiz AS tmq ON tmq.id_quiz = tqa.id_quiz
            WHERE ca.id = {pid_actividad}"""
        )
    except Exception as error:
        curso = metadata[0][0]
        pmensaje = f"Ha ocurrido un error. Error: {error}"
        presultado = "Fallida"
        perror = f"{error}"
        pname = metadata[0][3]
        pactivitie = metadata[0][1]
        pcategorie = metadata[0][2]
        pkeyword = metadata[0][4]
        p_fecha = p_fecha
        p_duracion = p_duracion
        phora = p_inicio
        pestado = "Error"
        presult = 0
    else:
        curso = metadata[0][0]
        pmensaje = "Se ha programado el la activadad correctamente"
        presultado = "Exitosa"
        perror = None
        pname = metadata[0][3]
        pactivitie = metadata[0][1]
        pcategorie = metadata[0][2]
        pkeyword = metadata[0][4]
        p_fecha = p_fecha
        p_duracion = p_duracion
        phora = p_inicio
        pestado = "Pendiente de inicio"
        presult = 1
    finally:
        return dict(
            mensaje=pmensaje,
            resultado=presultado,
            error=perror,
            result=presult,  
            name=pname,
            activitie=pactivitie,
            categorie=pcategorie,
            fecha=p_fecha,
            duracion=p_duracion, 
            hora=phora,
            estado=pestado,
            curso=curso,
            keyword=pkeyword,
            back_button=back_button
        )

def calcular_nota(actividad,usuario):
    sql = f"CALL spc_obtener_nota_actividad_quiz({actividad}, {usuario});"
    r = db.executesql(sql)
    return r

@auth.requires_login()
def obtener_quiz():
    query = "SELECT MAX(id_quiz) FROM tb_metadata_quiz;"
    result = None
    try:
        result = db.executesql(query)[0][0]
        result += 1
        redis_db_4.set('idquiz', f'{result}') 
    except:
        redis_db_4.incr('idquiz') 
    
    idq = '{"value": "' + redis_db_4.get("idquiz").decode() + '"}'
    return idq

#Tesis 2.0
@auth.requires_login()
def guardar_quiz_post():
    try:
        r = redis_db_4
        preguntas = json.dumps(request.post_vars)
        preguntas = preguntas.replace('{\"','')
        preguntas = preguntas.replace('\\"','"')
        preguntas = preguntas.replace('": ""}','')
        ide = request.vars['id']
        curso = request.vars['project']
        curso = str(curso).strip()
        uid = request.vars['uid']
        title = request.vars['title']
        a = r.hset(f"uid:{uid}:curso:{curso}:quiz:{ide}", "preguntas", preguntas)

        db.tb_metadata_quiz.insert(
            id_quiz=ide, 
            nombre=title, 
            fecha_creacion=datetime.datetime.now(), 
            creador=uid, 
            curso=curso
        )
        db.commit()
 
        datos = preguntas
        datos = datos.replace('\n','')
        datos = datos.replace('}]}"','}]}')
        json_quiz = datos.replace('{[','{"PREGUNTAS" : [')
        template_respuestas = json.loads(json_quiz)

        for pregunta in template_respuestas["PREGUNTAS"]:
            ##Tipos de preguntas 1: Multiple, 2: Falso/Verdadero, 3: Directa
            if pregunta["tipo"] == "veracidad":
                sql = f"CALL spi_insert_respuestas_quiz({ide}, '{pregunta['id_pregunta']}', '{pregunta['respuesta']}', 2);"
                db.executesql(sql)
            elif pregunta["tipo"] == "directa":
                sql = f"CALL spi_insert_respuestas_quiz({ide}, '{pregunta['id_pregunta']}', '{pregunta['respuesta']}', 3);"
                db.executesql(sql)
            else:
                for respuesta in pregunta["respuesta"]:
                    if respuesta["correcta"]:
                        sql = f"CALL spi_insert_respuestas_quiz({ide}, '{pregunta['id_pregunta']}', '{respuesta['value']}', 1);"
                        db.executesql(sql)
    except:
        raise

    return a

@auth.requires_login()
def get_activities():
    periodo = request.vars['period']
    curso = request.vars['project']
    categoria = request.vars['categorie']

    lab = True
    if auth.has_membership('Student'):
        lab = True
    elif auth.has_membership('Teacher'):
        lab = False
        pass

    myquery = ((db.course_activity.assignation == curso) & (db.course_activity.semester == periodo) 
            & (db.course_activity_category.category == categoria) & (db.course_activity.laboratory == lab)
            & (db.tb_quiz_actividad.id == None))
    
    actividades = db(myquery).select(
        db.course_activity.id,
        db.course_activity.name,
        join=[
            db.course_activity_category.on(
                db.course_activity_category.id == db.course_activity.course_activity_category    
            )
        ],
        left=[
            db.tb_quiz_actividad.on(
                db.tb_quiz_actividad.id_actividad ==  db.course_activity.id 
            )
        ]
    )
    return response.json(actividades)

@auth.requires_login()
def get_date_activity():
    actividad = request.vars['activity']	
    datos = db.course_activity[actividad]
    return response.json(datos.date_start)

def get_now():
    ahora = datetime.datetime.now()
    return ahora 

def guardar_respuestas():
    #Almaceno valores recibidos en variables locales
    usuario = request.vars['uid']
    actividad = request.vars['actividad']
    data = json.loads(request.body.read())
    ##PROCEDIMIENTO PARA INSERTAR
    ##IN id_actividad int,
    ##IN id_estudiante int,
    ##IN id_pregunta varchar(100),
    ##IN respuesta varchar(500)

    ##PROCEDIMIENTO PARA BORRAR
    ##IN pId_actividad int,
    ##IN pId_estudiante int,
    ##IN pId_pregunta varchar(100)

    #Verifico de que tipo es la respuesta recibida
    if data["tipo"] == "multiple":
        sql1 = f"CALL spd_delete_respuestas_quiz_carnet({actividad}, {usuario}, '{data['id_pregunta']}');"
        db.executesql(sql1)
        for res in data["respuesta"]:
            if res["correcta"]:
                ##Si el usuario la inserto como correcta la inserto
                sql2 = f"CALL spi_insert_respuestas_quiz_carnet({actividad}, {usuario}, '{data['id_pregunta']}', '{res['value']}');"
                db.executesql(sql2)
    elif data["tipo"] == "directa":
        ##Primero borro cualquier respuesta existente para esta pregunta y este alumno
        sql = f"CALL spd_delete_respuestas_quiz_carnet({actividad}, {usuario}, '{data['id_pregunta']}');"
        db.executesql(sql)

        ##Ahora inserto la respuesta
        sql = f"CALL spi_insert_respuestas_quiz_carnet({actividad}, {usuario}, '{data['id_pregunta']}', '{data['respuesta']['value']}');"
        db.executesql(sql)       
    else :
        ##Primero borro cualquier respuesta existente para esta pregunta y este alumno
        sql = f"CALL spd_delete_respuestas_quiz_carnet({actividad}, {usuario}, '{data['id_pregunta']}');"
        db.executesql(sql) 
        ##Ahora inserto la respuesta
        sql = f"CALL spi_insert_respuestas_quiz_carnet({actividad}, {usuario}, '{data['id_pregunta']}', '{data['respuesta']['value']}');"
        db.executesql(sql)

    sqlActivo = f"SELECT Estado_actual FROM vw_quiz_actividad WHERE id_actividad = {actividad};"
    activo = db.executesql(sqlActivo)
    seguir = 1
    if activo[0][0] != "Activo":
        seguir = 0
    
    return response.json(seguir)

def verificar_privacidad_quiz():
    x = tuple(request.args)
    y = str(''.join(x))
    id_programacion = int(y)

    privado = False

    programacion = db(db.vw_quiz_actividad.id == int(id_programacion)).select(db.vw_quiz_actividad.ALL).first()
    
    ##Verifico si es privado
    if programacion.private == 1:
        privado = True

    if privado == True:
        session.bloqueado = True
    else:
        session.bloqueado = False

    return 1

@auth.requires_login()
def llave():
    #Almaceno valores recibidos en variables locales
    actividad = request.vars['actividad']

    data = json.loads(request.body.read())

    sql = f"SELECT keyword FROM tb_quiz_actividad WHERE id_actividad = {actividad};"
    keyword = db.executesql(sql)

    if data["valor"] == keyword[0][0]:
        session.bloqueado = False
    else:
        session.bloqueado = True

    return 1

@auth.requires_login()
def actualizar_quiz_post():
    r = redis_db_4
    preguntas = json.dumps(request.post_vars)
    preguntas = preguntas.replace('{\"','')
    preguntas = preguntas.replace('\\"','"')
    preguntas = preguntas.replace('": ""}','')
    ide = request.vars['id']
    curso = request.vars['project']
    curso = str(curso).strip()
    uid = request.vars['uid']
    title = request.vars['title']
    qid = request.vars['quiz_id']
    a = r.hset(f"uid:{uid}:curso:{curso}:quiz:{ide}", "preguntas", preguntas)
    
    model = db(db.tb_metadata_quiz.id == qid).select().first()
    model.nombre = title
    model.update_record()
    db.commit()
    try:
        datos = preguntas
        datos = datos.replace('\n','')
        datos = datos.replace('}]}"','}]}')
        json_quiz = datos.replace('{[','{"PREGUNTAS" : [')
        template_respuestas = json.loads(json_quiz)
        for pregunta in template_respuestas["PREGUNTAS"]:
            ##Tipos de preguntas 1: Multiple, 2: Falso/Verdadero, 3: Directa
            if pregunta["tipo"] == "veracidad":
                sql = f"CALL spi_insert_respuestas_quiz({ide}, '{pregunta['id_pregunta']}', '{pregunta['respuesta']}', 2);"
                db.executesql(sql)
            elif pregunta["tipo"] == "directa":
                sql = f"CALL spi_insert_respuestas_quiz({ide}, '{pregunta['id_pregunta']}', '{pregunta['respuesta']}', 3);"
                db.executesql(sql)
            else:
                for respuesta in pregunta["respuesta"]:
                    if respuesta["correcta"]:
                        sql = f"CALL spi_insert_respuestas_quiz({ide}, '{pregunta['id_pregunta']}', '{respuesta['value']}', 1);"
                        db.executesql(sql)
    except:
        raise
    return a

@auth.requires_login()
def eliminar_quiz():
    #elimino el detalle
    r = redis_db_4
    ide = request.vars['id']
    curso = request.vars['project']
    curso = str(curso).strip()
    uid = request.vars['uid']
    
    r.hdel(f"uid:{uid}:curso:{curso}:quiz:{ide}", "preguntas")
    #elimino el encabezado
    db(db.tb_metadata_quiz.id_quiz == ide).delete()
    session.flash = T('El quiz ha sido eliminado exitosamente')

    return "ok"