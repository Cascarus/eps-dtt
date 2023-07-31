import json as json_parser
import cpfecys
from datetime import datetime


# Método para validar el inicio de sesion en aplicación móvil,
auth.settings.allow_basic_login = True


@auth.requires_login()
@request.restful()
def mtd_wbs_login():
    response.view = "generic.json"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"

    def GET(username, password):
        user = db(db.auth_user.username == str(username)).select().first()
        if user != None:
            if db.auth_user.password.validate(password) == (
                db(db.auth_user.id == user.id).select().first().password,
                None,
            ):
                if (
                    db(
                        (db.auth_group.role == "Student")
                        & (db.auth_membership.group_id == db.auth_group.id)
                        & (db.auth_membership.user_id == user.id)
                    )
                    .select()
                    .first()
                    is not None
                ):
                    return (
                        '{"status":"successful", "message":"", "user":"'
                        + user.username
                        + '", "first_name":"'
                        + user.first_name
                        + '", "last_name":"'
                        + user.last_name
                        + '", "email":"'
                        + user.email
                        + '"}'
                    )
                else:
                    return '{"status":"failure", "message":"Su membresía no aplica para ésta aplicación."}'
            else:
                return '{"status":"failure", "message":"Contraseña inválida."}'
        else:
            return '{"status":"failure", "message":"Usuario no válido."}'

    return locals()


auth.settings.allow_basic_login = True


@auth.requires_login()
@request.restful()
def mtd_wbs_courses():  # Devuele string con formato json, o solo [] si no encuentra cursos
    response.view = "generic.json"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"

    def GET(username):
        return get_courses_list(username)

    return locals()


# No tocar arriba!!!!!!!!!!
# ******************************METODO REST PARA SUBIR NOTAS*******************************
auth.settings.allow_basic_login = True


@auth.requires_login()
@request.restful()
def mtd_wbs_cargar_notas():
    response.view = "generic.json"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"

    def POST(*args, **vars):
        valor = sheet_to_array(str(request.vars["valor"]))
        str_valor = json_parser.dumps(valor)
        log = carga_de_notas(str_valor)
        # print sheet_to_array(str_valor)
        return log

    return locals()


# *************************************METODOS PARA CARGA DE NOTAS *******************************************
@auth.requires_login()
def carga_de_notas(actividad):
    # print "***************************OTRA SOLICITUD**********************************"
    obj_act_calificada = sheet_to_array(actividad)
    valores = ""
    if obj_act_calificada != None:
        if len(obj_act_calificada) > 0:
            # Propiedades de la actividad:  obj_act_calificada['proyectoid'], obj_act_calificada['actividadid'], obj_act_calificada['hojas_calificadas']
            # valores = 'ProyectoID= '+obj_act_calificada['proyectoid']+ '; ActividadID= '+obj_act_calificada['actividadid']
            if dame_fecha(obj_act_calificada["actividadid"]):
                if len(obj_act_calificada["hojas_calificadas"]) > 0:
                    # Iterando sobre cada hoja calificada:
                    for arr_hoja in obj_act_calificada["hojas_calificadas"]:
                        # Estos datos serán la clave en redis para la hoja
                        proyecto_id = (
                            arr_hoja["proyecto_id"]
                            .encode("ascii", "ignore")
                            .decode("ascii")
                        )
                        actividad_id = (
                            arr_hoja["actividad_id"]
                            .encode("ascii", "ignore")
                            .decode("ascii")
                        )
                        # actividad_nombre= arr_hoja['actividad_nombre'].encode('ascii', 'ignore').decode('ascii')
                        estudiante_id = (
                            arr_hoja["estudiante_id"]
                            .encode("ascii", "ignore")
                            .decode("ascii")
                        )
                        estudiante_carnet = (
                            arr_hoja["estudiante_carnet"]
                            .encode("ascii", "ignore")
                            .decode("ascii")
                        )
                        nota = (
                            arr_hoja["hoja_nota"]
                            .encode("ascii", "ignore")
                            .decode("ascii")
                        )
                        hoja_calificada = json_parser.dumps(arr_hoja["hoja"])

                        valores += (
                            guardar_nota(
                                proyecto_id,
                                actividad_id,
                                estudiante_id,
                                estudiante_carnet,
                                nota,
                                hoja_calificada,
                            )
                            + ","
                        )

                    if valores != "":
                        valores = (
                            valores[:-1]
                            if (valores[len(valores) - 1] == ",")
                            else valores
                        )
                    valores = (
                        '{"status":"successful", "message":"Se validaron las notas.", "respuesta":['
                        + valores
                        + "]}"
                    )
                    # valores+= proyecto_id+" "+actividad_id+" "+actividad_nombre+" "+estudiante_id+" "+estudiante_carnet+" "+str(arr_hoja['hoja_nota'])+"; "
                    # valores+=('---- Si está activa la actividad!!!')
                else:
                    valores = '{"status":"failure", "message":"No se encontraron hojas calificadas.", "respuesta":[]}'
            else:
                valores = (
                    ""
                    '{"status":"failure", "message":"La fecha límite de la actividad ha expirado.", "respuesta":[]}'
                )
        else:
            valores = (
                ""
                '{"status":"failure", "message":"No se encontroó información desde la aplicación.", "respuesta":[]}'
            )
    else:
        valores = '{"status":"failure", "message":"La información no se envío correctamente.", "respuesta":[]}'

    # print valores
    return valores


# *************************************METODOS PARA CARGA DE NOTAS *******************************************
@auth.requires_login()
def carga_de_notas(actividad):
    # print "***************************OTRA SOLICITUD**********************************"
    obj_act_calificada = sheet_to_array(actividad)
    valores = ""
    if obj_act_calificada != None:
        if len(obj_act_calificada) > 0:
            # Propiedades de la actividad:  obj_act_calificada['proyectoid'], obj_act_calificada['actividadid'], obj_act_calificada['hojas_calificadas']
            # valores = 'ProyectoID= '+obj_act_calificada['proyectoid']+ '; ActividadID= '+obj_act_calificada['actividadid']
            if dame_fecha(obj_act_calificada["actividadid"]):
                if len(obj_act_calificada["hojas_calificadas"]) > 0:
                    # Iterando sobre cada hoja calificada:
                    for arr_hoja in obj_act_calificada["hojas_calificadas"]:
                        # Estos datos serán la clave en redis para la hoja
                        proyecto_id = (
                            arr_hoja["proyecto_id"]
                            .encode("ascii", "ignore")
                            .decode("ascii")
                        )
                        actividad_id = (
                            arr_hoja["actividad_id"]
                            .encode("ascii", "ignore")
                            .decode("ascii")
                        )
                        # actividad_nombre= arr_hoja['actividad_nombre'].encode('ascii', 'ignore').decode('ascii')
                        estudiante_id = (
                            arr_hoja["estudiante_id"]
                            .encode("ascii", "ignore")
                            .decode("ascii")
                        )
                        estudiante_carnet = (
                            arr_hoja["estudiante_carnet"]
                            .encode("ascii", "ignore")
                            .decode("ascii")
                        )
                        nota = (
                            arr_hoja["hoja_nota"]
                            .encode("ascii", "ignore")
                            .decode("ascii")
                        )
                        hoja_calificada = json_parser.dumps(arr_hoja["hoja"])

                        valores += (
                            guardar_nota(
                                proyecto_id,
                                actividad_id,
                                estudiante_id,
                                estudiante_carnet,
                                nota,
                                hoja_calificada,
                            )
                            + ","
                        )

                    if valores != "":
                        valores = (
                            valores[:-1]
                            if (valores[len(valores) - 1] == ",")
                            else valores
                        )
                    valores = (
                        '{"status":"successful", "message":"Se validaron las notas.", "respuesta":['
                        + valores
                        + "]}"
                    )
                    # valores+= proyecto_id+" "+actividad_id+" "+actividad_nombre+" "+estudiante_id+" "+estudiante_carnet+" "+str(arr_hoja['hoja_nota'])+"; "
                    # valores+=('---- Si está activa la actividad!!!')
                else:
                    valores = '{"status":"failure", "message":"No se encontraron hojas calificadas.", "respuesta":[]}'
            else:
                valores = (
                    ""
                    '{"status":"failure", "message":"La fecha límite de la actividad ha expirado.", "respuesta":[]}'
                )
        else:
            valores = (
                ""
                '{"status":"failure", "message":"No se encontroó información desde la aplicación.", "respuesta":[]}'
            )
    else:
        valores = '{"status":"failure", "message":"La información no se envío correctamente.", "respuesta":[]}'

    # print valores
    return valores


# *********************************TERMINA METODOS PARA CARGA DE NOTAS****************************************
@auth.requires_login()
def get_courses_list(username):
    # username= request.vars['username']
    user = db(db.auth_user.username == str(username)).select().first()
    area = db(db.area_level.name == "DTT Tutor Académico").select().first()
    period = None
    courses_tutor = None
    period = cpfecys.current_year_period()

    if user != None:
        courses_tutor = db(
            (db.user_project.assigned_user == user.id)
            & (db.user_project.period == db.period_year.id)
            & (
                (db.user_project.period <= period.id)
                & ((db.user_project.period.cast('integer') + db.user_project.periods) > period.id)
            )
            & (db.user_project.project == db.project.id)
            & (db.project.area_level == area.id)
        ).select()
        len_courses = len(courses_tutor)

        str_courses = ""

        i_course = 1
        for (
            course
        ) in (
            courses_tutor
        ):  # Si no tiene cursos no se recorre el arregla, validando que el arreglo esté vacío
            str_sheets_course = get_sheet_list(
                str(period.id), str(course.user_project.project.id)
            )
            str_sheets_course = str_sheets_course if str_sheets_course != None else ""
            str_student_list_course = get_student_list_course(
                str(period.id), str(course.user_project.project.id)
            )
            str_student_list_course = (
                str_student_list_course if str_student_list_course != None else ""
            )

            str_courses += (
                '{"idpro":"'
                + str(course.user_project.project.id)
                + '", "proyecto":"'
                + course.user_project.project.name
                + '", "hojas":['
                + str_sheets_course
                + '], "alumnos":['
                + str_student_list_course
                + "]}"
            )

            if i_course < len_courses:
                str_courses += ","
            i_course += 1

        return "[" + str_courses + "]"
    else:
        return "[]"


@auth.requires_login()
def get_student_list_course(period, project):
    alumnos = db(
        (db.academic_course_assignation.semester == period)
        & (db.academic_course_assignation.assignation == project)
        & (db.academic_course_assignation.laboratorio == "T")
        & (db.academic_course_assignation.carnet == db.academic.id)
        & (db.academic.id_auth_user == db.auth_user.id)
    ).select(orderby=db.auth_user.username)

    str_alumnos = ""
    if len(alumnos) > 0:
        len_alumnos = len(alumnos)
        i_alumnos = 1
        for alumno in alumnos:
            str_alumnos += (
                '{"id":"'
                + str(alumno.auth_user.id)
                + '", "nombre":"'
                + alumno.auth_user.first_name
                + " "
                + alumno.auth_user.last_name
                + '", "carnet":"'
                + alumno.auth_user.username
                + '", "correo":"'
                + alumno.auth_user.email
                + '", "laboratorio":"'
                + str(alumno.academic_course_assignation.laboratorio)
                + '"}'
            )
            if i_alumnos < len_alumnos:
                str_alumnos += ","
            i_alumnos += 1
        return str_alumnos
    else:
        return None


@auth.requires_login()
def get_sheet_list(period, project):
    # period = request.vars['period']
    # project = request.vars['project']

    # 1. Obtener keys
    project_sheets_keys = get_keys(period, project)
    my_sheets = ""

    # 2. Obteniendo las hojas
    if project_sheets_keys != None:
        lenkeys = len(project_sheets_keys)
        i_keys = 1
        for sheet_key in project_sheets_keys:
            tmp_sheet = None
            tmp_sheet = get_complete_sheet(sheet_key)
            if tmp_sheet != None:
                my_sheets += tmp_sheet
                if i_keys < lenkeys:
                    my_sheets += ","
            i_keys += 1

        if my_sheets != "":
            if my_sheets[len(my_sheets) - 1] == ",":
                return my_sheets[:-1]
            else:
                return my_sheets
        else:
            return None
    else:
        return None


@auth.requires_login()
def get_complete_sheet(sheet_key):
    # Validando que la definicion de los parámetros esté completa
    if mtd_get_estado_hoja(sheet_key) == True:
        # Agregando todos los atributos para la hoja de calificación si está completa
        # Obteniendo arregalo de la plantilla
        string_sheet = get_sheet_attribute(sheet_key, "hoja")
        id_activity = get_sheet_attribute(sheet_key, "idactividad")
        name_activity = get_sheet_attribute(sheet_key, "nombre")
        if dame_fecha(id_activity):
            complete_sheet = (
                '{"id_actividad":"'
                + id_activity
                + '", "nombre_actividad":"'
                + name_activity
                + '", "detalle":'
                + string_sheet
                + "}"
            )
            return complete_sheet
        return None
    else:
        return None


@auth.requires_login()
def mtd_get_estado_hoja(sheet_key):
    array_hoja = sheet_to_array(get_sheet_attribute(sheet_key, "hoja"))
    total_hoja = get_sheet_attribute(sheet_key, "total")
    if array_hoja != None:
        if len(array_hoja) > 0:
            for categoria in array_hoja:
                if categoria["estado"] == "True":
                    pass
                else:
                    return False
            if float(total_hoja) == 100:
                return True
            else:
                return False
        else:
            return False
    else:
        return False


@auth.requires_login()
def sheet_to_array(string_hoja):
    if string_hoja != None:
        json_hoja = json_parser.loads(string_hoja)
        return json_hoja
    else:
        return None


@auth.requires_login()
def get_sheet_attribute(key, attribute):
    # r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
    attribute_sheet = redis_db_2.hget(key, attribute)
    return attribute_sheet


# Regresa un arreglo, y si no existe None
@auth.requires_login()
def get_keys(period, project):
    # period = request.vars['period']
    # project = request.vars['project']
    # r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
    keys_sheet_project = redis_db_2.keys(
        "per:" + period + ":idp:" + project + ":tipo:*:ida:*"
    )

    if len(keys_sheet_project) > 0:
        return keys_sheet_project
    else:
        return None


@auth.requires_login()
def alumnos():
    period = None
    period = cpfecys.current_year_period()

    alumnos = db(
        (db.academic_course_assignation.semester == period)
        & (db.academic_course_assignation.assignation == 42)
        & (db.academic_course_assignation.laboratorio == "T")
        & (db.academic_course_assignation.carnet == db.academic.id)
        & (db.academic.id_auth_user == db.auth_user.id)
    ).select()

    str_alumnos = ""
    if len(alumnos) > 0:
        len_alumnos = len(alumnos)
        i_alumnos = 1
        for alumno in alumnos:
            str_alumnos += (
                '{"id":"'
                + str(alumno.auth_user.id)
                + '", "nombre":"'
                + alumno.auth_user.first_name
                + " "
                + alumno.auth_user.last_name
                + '", "carnet":"'
                + alumno.auth_user.username
                + '", "correo":"'
                + alumno.auth_user.email
                + '", "laboratorio":"'
                + str(alumno.academic_course_assignation.laboratorio)
                + '"}'
            )
            if i_alumnos < len_alumnos:
                str_alumnos += ","
            i_alumnos += 1
        return str_alumnos
    else:
        return None

    # return alumnos[0].auth_user.first_name


# ************************************ METODOS PARA EL INGRESO DE NOTAS *********************************

@auth.requires_login()
def dame_fecha(actividad_id):
    # actividad_id = "5647"
    period = cpfecys.current_year_period()
    control_p = (
        db(
            (
                db.student_control_period.period_name
                == (T(period.period.name) + " " + str(period.yearp))
            )
        )
        .select()
        .first()
    )
    t_act = db(db.course_activity.id == actividad_id).select().first()
    maxim_time_grade = db.executesql(
        "SELECT DATE_ADD('"
        + str(t_act.date_finish)
        + "', INTERVAL "
        + str(control_p.timeout_income_notes)
        + " Day) as fechaMaxGrade;",
        as_dict=True,
    )

    date_grade0 = ""
    var_do_grade = False
    for d0 in maxim_time_grade:
        date_grade0 = d0["fechaMaxGrade"]
    pass
    if str(datetime.now()) <= str(date_grade0):
        var_do_grade = True
    pass

    return var_do_grade


@auth.requires_login()
def guardar_nota(
    proyecto_id, actividad_id, estudiante_id, estudiante_carnet, nota, hoja_calificada
):
    log = ""

    period = cpfecys.current_year_period()
    # proyecto_id="42"
    # actividad_id = "5647"
    # estudiante_id = "2472"
    # estudiante_carnet = request.vars['carnet']
    # nota = request.vars['nota']
    # hoja_calificada = "soy una hoja calificada"
    # 1
    var_activity = db(db.course_activity.id == actividad_id).select().first()
    var_project = db(db.project.id == proyecto_id).select().first()
    academic_var = db(db.academic.carnet == estudiante_carnet).select().first()
    # 2
    assig_var = (
        db(
            (db.academic_course_assignation.assignation == var_project.id)
            & (db.academic_course_assignation.semester == period.id)
            & (db.academic_course_assignation.carnet == academic_var.id)
        )
        .select()
        .first()
    )
    # 3
    grade_before = (
        db(
            (db.grades.academic_assignation == assig_var.id)
            & (db.grades.activity == var_activity.id)
        )
        .select()
        .first()
    )
    # 4. Validando que no haya nota
    if grade_before is None:
        if (var_activity.laboratory == False) | (
            assig_var.laboratorio == var_activity.laboratory
        ):
            # Insertando nota
            grade = db.grades.insert(
                academic_assignation=assig_var.id, activity=var_activity.id, grade=nota
            )
            if grade != None:
                # Insertando en el log
                db.grades_log.insert(
                    user_name="Carnet del tutor enviar de la app",
                    roll="Student",
                    operation_log="insert",
                    academic_assignation_id=assig_var.id,
                    academic=assig_var.carnet.carnet,
                    project=assig_var.assignation.name,
                    activity=var_activity.name,
                    activity_id=var_activity.id,
                    category=var_activity.course_activity_category.category.category,
                    period=T(assig_var.semester.period.name),
                    yearp=assig_var.semester.yearp,
                    after_grade=nota,
                    description="Insertado desde app movil - ",
                )
                insert_hoja_calificada(
                    proyecto_id,
                    actividad_id,
                    estudiante_id,
                    estudiante_carnet,
                    hoja_calificada,
                    nota,
                )
                log = (
                    T("Grade added")
                    + " | Carnet: "
                    + str(estudiante_carnet)
                    + " "
                    + T("Grade")
                    + ": "
                    + str(nota)
                    + "."
                )
                log = (
                    '{"status":"successful", "message":"'
                    + log
                    + '", "estudiante_carnet":"'
                    + estudiante_carnet
                    + '", "estudiante_id":"'
                    + estudiante_id
                    + '", "actividad_id":"'
                    + actividad_id
                    + '", "proyecto_id":"'
                    + proyecto_id
                    + '"}'
                )
            else:
                log = (
                    T("Failed to add grade")
                    + " | Carnet: "
                    + str(estudiante_carnet)
                    + " "
                    + T("Grade")
                    + ": "
                    + str(nota)
                    + "."
                )
                log = (
                    '{"status":"failure", "message":"'
                    + log
                    + '", "estudiante_carnet":"'
                    + estudiante_carnet
                    + '", "estudiante_id":"'
                    + estudiante_id
                    + '", "actividad_id":"'
                    + actividad_id
                    + '", "proyecto_id":"'
                    + proyecto_id
                    + '"}'
                )
        else:
            log = (
                T("Failed to add grade")
                + " | Carnet: "
                + str(estudiante_carnet)
                + " "
                + T("Grade")
                + ": "
                + str(nota)
                + "."
            )
            log = (
                '{"status":"failure", "message":"'
                + log
                + '", "estudiante_carnet":"'
                + estudiante_carnet
                + '", "estudiante_id":"'
                + estudiante_id
                + '", "actividad_id":"'
                + actividad_id
                + '", "proyecto_id":"'
                + proyecto_id
                + '"}'
            )
    else:
        log = (
            T("Failed to add grade")
            + " | Carnet: "
            + estudiante_carnet
            + " "
            + T("Already have an associated grade")
            + "."
        )
        log = (
            '{"status":"failure", "message":"'
            + log
            + '", "estudiante_carnet":"'
            + estudiante_carnet
            + '", "estudiante_id":"'
            + estudiante_id
            + '", "actividad_id":"'
            + actividad_id
            + '", "proyecto_id":"'
            + proyecto_id
            + '"}'
        )

    return log


@auth.requires_login()
def insert_hoja_calificada(idpro, idact, idest, carnet, val_hoja_calificada, val_nota):
    # idpro:42:idact:5500:idest:1010:carnet:201213456 hoja_calificada
    # r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
    ins1 = redis_db_2.hset(
        "idpro:" + idpro + ":idact:" + idact + ":idest:" + idest + ":carnet:" + carnet,
        "hoja_calificada",
        val_hoja_calificada,
    )
    ins2 = redis_db_2.hset(
        "idpro:" + idpro + ":idact:" + idact + ":idest:" + idest + ":carnet:" + carnet,
        "nota",
        val_nota,
    )
    respuesta = True if ((ins1) & (ins2)) else False

    return respuesta
