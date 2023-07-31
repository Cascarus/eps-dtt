import cpfecys
import iso_utils
from gluon.tools import Crud
import json
from datetime import datetime


@auth.requires(auth.has_membership("Super-Administrator") or auth.has_membership("DSI"))
def menu():
    """
    Solo permite mostrar una vista con las opciones para la creación
    de evaluaciones y para listarlas
    """
    return dict()

@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('DSI'))
def crear_encuesta():
    """
        La evaluación de rendimiento es asignada por defecto al periódo actual
        y no es editable para el usuario
    """
    id_period = cpfecys.current_year_period()
    db.iso_ev_rendimiento.id_period_year.default = id_period
    db.iso_ev_rendimiento.id_period_year.writable = False
    db.iso_ev_rendimiento.id_period_year.readable = False

    def validar_fecha(form):
        fecha_inicio = form.vars.fecha_inicio
        fecha_fin = form.vars.fecha_fin

        if fecha_fin < fecha_inicio:
            form.errors.fecha_fin = 'La fecha de finalización no debe ser menor a la fecha de inicio'

    form = SQLFORM(db.iso_ev_rendimiento)

    if form.process(onvalidation=validar_fecha).accepted:
        id_encuesta = form.vars.id
        redirect(URL('iso_ev_rendimiento', 'editar_evaluacion', args=(id_encuesta)))

    return dict(form=form)

@auth.requires(auth.has_membership("Super-Administrator") or auth.has_membership("DSI"))
def listar_evaluaciones():
    id_periodo = None

    try:
        id_periodo = int(request.vars["periodo"])
    except:
        pass

    if not id_periodo:
        periodo_act = cpfecys.current_year_period()
        id_periodo = periodo_act.id

    evaluaciones = db((db.iso_ev_rendimiento.id_period_year == id_periodo)).select()

    periodos = db().select(db.period_year.ALL, orderby=~db.period_year.id)

    return locals()


@auth.requires(auth.has_membership("Super-Administrator") or auth.has_membership("DSI"))
def editar_evaluacion():
    id_ev = None
    try:
        id_ev = request.args[0]
    except:
        session.flash = "No se indico la encuesta a editar"
        redirect(URL("default", "home"))

    evaluacion = db((db.iso_ev_rendimiento.id == id_ev)).select().first()
    if not evaluacion:
        session.flash = "No existe la encuesta indicada"
        redirect(URL("default", "home"))

    return locals()


@auth.requires(auth.has_membership("Super-Administrator") or auth.has_membership("DSI"))
@request.restful()
def tipoPregunta():
    response.view = "generic.json"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Content-Type"] = "application/json"

    def GET():
        tipos = db(db.iso_tipo_pregunta).select()
        ltipo = [{"id": t.id, "descripcion": t.descripcion} for t in tipos]

        return json.dumps(ltipo)

    return locals()


@auth.requires(
    auth.has_membership("Super-Administrator")
    or auth.has_membership("DSI")
    or auth.has_membership("Teacher")
    or auth.has_membership("Student")
)
def resultado_evaluacion():

    id_evr_curso = request.vars["idevrcurso"]
    preguntas = db(
        (db.iso_evr_curso.id == id_evr_curso)
        & (db.iso_pregunta.id_ev_rendimiento == db.iso_evr_curso.iso_encuesta_id)
    ).select()

    tutor = (
        db(
            (db.iso_evr_curso.id == id_evr_curso)
            & (db.user_project.id == db.iso_evr_curso.user_project_id)
            & (db.auth_user.id == db.user_project.assigned_user)
        )
        .select(db.auth_user.first_name, db.auth_user.last_name, db.auth_user.username)
        .first()
    )
    lista = []
    coment = []
    promedio = 0
    sumatoria = 0

    for pregunta in preguntas:
        id_pregunta = pregunta.iso_pregunta.id
        id_tipo_pregunta = pregunta.iso_pregunta.iso_tipo_pregunta_id
        if id_tipo_pregunta == 1:
            query = iso_utils.iso_get_ev_respuesta(id_evr_curso, id_pregunta)
            resultado = db.executesql(query)

            for result in resultado:
                sumatoria = sumatoria + result[0]

            cantidad = len(resultado)
            if cantidad:
                promedio = sumatoria / cantidad

            dato = {
                "pregunta": pregunta.iso_pregunta.descripcion,
                "idpregunta": pregunta.iso_pregunta.id,
                "respuesta": resultado,
                "promedio": promedio,
                "tipo_pregunta": id_tipo_pregunta,
            }
            lista.append(dato)
        elif id_tipo_pregunta == 2:
            query_cualitativa = iso_utils.iso_get_respuesta_cualitativa(
                id_evr_curso, id_pregunta
            )
            dato_cualitativa = db.executesql(query_cualitativa)

            puntos = 0
            participantes = 0

            for dat in dato_cualitativa:
                puntos += dat[1]
                participantes += dat[2]

            promedio = 0
            if participantes:
                promedio = puntos / participantes

            dato = {
                "pregunta": pregunta.iso_pregunta.descripcion,
                "idpregunta": pregunta.iso_pregunta.id,
                "respuesta": dato_cualitativa,
                "promedio": promedio,
                "tipo_pregunta": id_tipo_pregunta,
            }
            lista.append(dato)
        else:
            query_comentario = iso_utils.iso_get_respuesta_comentario(
                id_evr_curso, id_pregunta
            )
            dato_comentario = db.executesql(query_comentario)

            dato = {
                "pregunta": pregunta.iso_pregunta.descripcion,
                "idpregunta": pregunta.iso_pregunta.id,
                "respuesta": dato_comentario,
                "tipo_pregunta": id_tipo_pregunta,
            }
            coment.append(dato)

    return {"lista": lista, "comentario": coment, "tutor": tutor}


@auth.requires(auth.has_membership("Super-Administrator") or auth.has_membership("DSI"))
def mostrar_top():
    iso_encuesta_id = None
    try:
        iso_encuesta_id = request.vars["iso_encuesta_id"]
    except:
        pass

    id_user = None
    periodo = None
    try:
        id_project = request.vars["id_project"]
        periodo = request.vars["periodo"]
    except:
        pass

    top = request.vars["top"]
    top = top if top else 10

    orden = request.vars["orden"]
    orden = orden if orden else "ASC"

    if not iso_encuesta_id and (not id_project or not periodo):
        session.flash = "Petición incorrecta"
        redirect("default", "home")

    query = iso_utils.iso_get_punteo(iso_encuesta_id, top, orden)
    resultados = db.executesql(query)
    encuesta = db(db.iso_ev_rendimiento.id == iso_encuesta_id).select(
        db.iso_ev_rendimiento.nombre
    )

    return locals()


@auth.requires(auth.has_membership("Super-Administrator") or auth.has_membership("DSI"))
def activar_evaluacion():
    """
    validando si la petición es post de ser así
    se recuperan los proyectos a los que evaluará
    """
    valores = len(request.vars)
    id_ev = 0
    try:
        id_ev = int(request.vars["id_ev"])
    except:
        ...

    query = iso_utils.iso_get_valor_encuesta(id_ev)
    resultado = db.executesql(query)

    if resultado[0][0] != 100 and valores:
        session.flash = "La evaluación debe realizarse sobre 100 puntos"
        redirect(URL("iso_ev_rendimiento", "menu"))

    duplicados = False
    if valores:
        evaluacion = int(request.vars["id_ev"])
        for d in request.vars:
            # ignorando el id de la evaluacion
            if d == "id_ev":
                continue

            datos = {
                "iso_encuesta_id": evaluacion,
                "user_project_id": request.vars[d],
                "mostrar": True,
            }

            # validando e insertando los nuevos valores
            try:
                db.iso_evr_curso.validate_and_insert(**datos)
            except Exception as e:
                duplicados = True

        msj = "Se han agregado los cursos a la evaluación"
        if duplicados:
            msj = "Se han encontrado cursos duplicados"

        # redirigiendo con mensaje de exito
        session.flash = msj
        redirect(URL("iso_ev_rendimiento", "menu"))

    """
    se procesa la peticion GET para mostrar la lista
    de los auxiliares
    """
    id_period = cpfecys.current_year_period()
    id_ev = None
    try:
        id_ev = request.args[0]
    except:
        session.flash = "No se indico la encuesta a Activar"
        redirect(URL("default", "home"))

    qcount = iso_utils.iso_get_count_cualitavivas(id_ev)
    rcount = db.executesql(qcount)

    if rcount[0][0]:
        session.flash = (
            "Todas la preguntas de tipo Cualitativo deben tener opciones de respuesta"
        )
        redirect(URL("iso_ev_rendimiento", "editar_evaluacion") + "/" + str(id_ev))

    tutores = db(
        (db.user_project.period == id_period)
        & (db.auth_user.id == db.user_project.assigned_user)
        & (db.auth_membership.user_id == db.auth_user.id)
        & (db.auth_membership.group_id == 2)
        & (db.project.id == db.user_project.project)
        & (db.project.area_level == 1)
    ).select(
        db.user_project.id,
        db.project.name,
        db.project.area_level,
        db.auth_user.username,
        db.auth_user.first_name,
        db.auth_user.last_name,
    )
    return locals()


@auth.requires(auth.has_membership("Academic"))
def responder_evaluacion():
    id_ev_curso = request.args[0]
    iso_evr_curso = db((db.iso_evr_curso.id == id_ev_curso)).select().first()
    user_project = (
        db(
            (db.user_project.id == iso_evr_curso.user_project_id)
            & (db.project.id == db.user_project.project)
        )
        .select(db.project.name, db.user_project.assigned_user)
        .first()
    )
    auth_user = (
        db((db.auth_user.id == user_project.user_project.assigned_user))
        .select()
        .first()
    )

    nombre_curso = user_project.project.name
    nombre_tutor = auth_user.first_name
    apellido_tutor = auth_user.last_name
    id_ev = iso_evr_curso.iso_encuesta_id
    id_user_project = iso_evr_curso.user_project_id
    return locals()


@auth.requires(auth.has_membership("Super-Administrator") or auth.has_membership("DSI"))
def descargar_resultado():
    iso_encuesta_id = None
    contenido = [("Carnet", "Puntos")]
    try:
        iso_encuesta_id = request.vars["iso_encuesta_id"]
    except:
        pass

    if not iso_encuesta_id:
        session.flash = "Petición incorrecta"
        redirect("default", "home")

    resultado = db(
        (db.iso_resultado_evr.iso_encuesta_id == iso_encuesta_id)
        & (db.iso_resultado_evr.puntos != None)
    ).select(db.iso_resultado_evr.username, db.iso_resultado_evr.puntos)

    for rst in resultado:
        row = (rst.username, rst.puntos)
        contenido.append(row)

    return dict(filename="resultados", csvdata=contenido)


@auth.requires(
    auth.has_membership("Super-Administrator")
    or auth.has_membership("DSI")
    or auth.has_membership("Teacher")
)
def mostrar_resultados():
    iso_encuesta_id = None
    try:
        iso_encuesta_id = request.vars["iso_encuesta_id"]
    except:
        pass

    id_user = None
    periodo = None
    try:
        id_project = request.vars["id_project"]
        periodo = request.vars["periodo"]
    except:
        pass

    if not iso_encuesta_id and (not id_project or not periodo):
        session.flash = "Petición incorrecta"
        redirect("default", "home")

    query = iso_utils.iso_resultado_evr(iso_encuesta_id, id_project, periodo)
    resultados = db.executesql(query)
    id_encuesta = 0
    if len(resultados):
        id_encuesta = resultados[0][7]

    encuesta = db(db.iso_ev_rendimiento.id == id_encuesta).select(
        db.iso_ev_rendimiento.nombre
    )

    return locals()


@auth.requires(auth.has_membership("Super-Administrator") or auth.has_membership("DSI"))
def copiar_evaluacion():
    id_evr = None

    try:
        id_evr = request.args[0]
    except Exception:
        session.flash = "No se indicó la encuesta a copiar"
        redirect(URL("default", "home"))

    preguntas = db(db.iso_pregunta.id_ev_rendimiento == id_evr).select(
        db.iso_pregunta.id, db.iso_pregunta.descripcion, orderby=db.iso_pregunta.id
    )

    return locals()


@auth.requires(auth.has_membership("Super-Administrador") or auth.has_membership("DSI"))
def procesar_copia():
    c_datos = len(request.vars)

    if c_datos == 0:
        session.flash = "No se recibio información"
        redirect(URL("default", "home"))

    datos = request.vars
    fecha_inicio = datos["finicio"]
    fecha_fin = datos["ffin"]
    nombre = datos["nombre"]

    dt_f_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d %H:%M:%S")
    dt_f_fin = datetime.strptime(fecha_fin, "%Y-%m-%d %H:%M:%S")
    if dt_f_fin < dt_f_inicio:
        session.flash = (
            "La fecha de finalización no debe ser menor a la fecha de inicio"
        )
        redirect(URL("iso_ev_rendimiento", "copiar_evaluacion") + "/" + datos["id_evr"])

    periodo_act = cpfecys.current_year_period()
    id_periodo = periodo_act.id
    nueva_ev = {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "nombre": nombre,
        "id_period_year": id_periodo,
    }

    id_resp = dict(db.iso_ev_rendimiento.validate_and_insert(**nueva_ev))
    errores = id_resp["errors"].__dict__
    if len(errores):
        session.flash = "No se realizo la copia"
        redirect(URL("default", "home"))

    id_ev_nvo = id_resp["id"]
    lst_id = []

    for dato in datos:
        if dato == "finicio" or dato == "ffin" or dato == "nombre" or dato == "id_evr":
            continue

        idp = int(dato[4:])
        lst_id.append(idp)

    lst_id.sort()

    for idp in lst_id:
        pregunta = db(db.iso_pregunta.id == idp).select().first()

        if not pregunta:
            continue

        nueva_pregunta = {
            "descripcion": pregunta.descripcion,
            "valor": pregunta.valor,
            "iso_tipo_pregunta_id": pregunta.iso_tipo_pregunta_id,
            "id_ev_rendimiento": id_ev_nvo,
        }

        resp = dict(db.iso_pregunta.validate_and_insert(**nueva_pregunta))

        errs = resp["errors"].__dict__
        if len(errs):
            continue

        if pregunta.iso_tipo_pregunta_id != 2:
            continue

        id_pregunta = resp["id"]
        opciones = db(db.iso_pregunta_seleccion.iso_pregunta_id == pregunta.id).select()

        for opcion in opciones:
            nva_opcion = {
                "descripcion": opcion.descripcion,
                "punteo": opcion.punteo,
                "iso_pregunta_id": id_pregunta,
            }

            r2 = dict(db.iso_pregunta_seleccion.validate_and_insert(**nva_opcion))
            pass

    session.flash = "Se realizó la copia exitosamente"
    redirect(URL("iso_ev_rendimiento", "editar_evaluacion", args=[id_ev_nvo]))


@auth.requires(auth.has_membership("Super-Administrador") or auth.has_membership("DSI"))
def resultados_dinamicos():
    db.iso_resultado_evr.id_evr.readable = False
    grid = SQLFORM.grid(db.iso_resultado_evr, editable=False, deletable=False)
    return locals()


@auth.requires(auth.has_membership("Super-Administrator") or auth.has_membership("DSI"))
def mostrar_participantes():
    iso_encuesta_id = None
    try:
        iso_encuesta_id = request.vars["iso_encuesta_id"]
    except:
        pass

    if not iso_encuesta_id and (not id_project or not periodo):
        session.flash = "Petición incorrecta"
        redirect("default", "home")

    query = iso_utils.iso_get_count_completas(iso_encuesta_id)
    completada = db.executesql(query)

    encuesta = db(db.iso_ev_rendimiento.id == iso_encuesta_id).select(
        db.iso_ev_rendimiento.nombre
    )

    return locals()


@auth.requires(auth.has_membership("Super-Administrator") or auth.has_membership("DSI"))
def editar_fecha():
    id_ev = request.vars["id_ev"]
    evaluacion = db.iso_ev_rendimiento(id_ev)
    db.iso_ev_rendimiento.id_period_year.writable = False
    db.iso_ev_rendimiento.id.readable = False
    crud.settings.update_deletable = False

    def validar_fecha(form):
        f_inicio = form.vars.fecha_inicio
        f_fin = form.vars.fecha_fin
        if f_fin < f_inicio:
            form.errors.fecha_fin = (
                "La fecha de finalización no debe ser menor a la fecha de inicio"
            )

    form = SQLFORM(db.iso_ev_rendimiento, evaluacion)
    if form.process(onvalidation=validar_fecha).accepted:
        session.flash = "Se ha actualizado la evaluación"
        redirect(URL("iso_ev_rendimiento", "listar_evaluaciones"))

    return dict(form=form)
