import cpfecys
from gluon.tools import Crud
from datetime import date
import iso_utils


# configurando los campos de los form

db.iso_incidente.id_project.writable = False
db.iso_incidente.id_period.writable = False
db.iso_incidente.id_period.readable = False
db.iso_incidente.id_auth_user.writable = False
db.iso_incidente.id_auth_user.readable = False


@auth.requires(
    auth.has_membership("Student")
    or auth.has_membership("DSI")
    or auth.has_membership("Super-Administrator")
)
def reportar():
    periodo = 0
    project = 0
    try:
        # recuperando periodo y proyecto
        periodo = int(request.vars["periodo"])
        project = int(request.vars["project"])
    except:
        session.flash = "Debe indicar el periodo y el curso"
        redirect(URL("default", "home"))

    period = cpfecys.current_year_period()

    # validar si es curso del semestre actual
    if period.id != periodo:
        session.flash = "El curso no pertenece al semestre actual"
        redirect(URL("default", "home"))

    tipo_incidente = db(db.iso_tipo_incidente).select()
    periodo2 = periodo

    validar_asig = not (
        auth.has_membership("DSI") or auth.has_membership("Super-Administrator")
    )

    id_user = auth.user.id
    asignacion = None
    if validar_asig:
        asignacion = (
            db(
                (db.academic.id_auth_user == id_user)
                & (db.academic_course_assignation.carnet == db.academic.id)
                & (db.academic_course_assignation.semester == periodo)
                & (db.academic_course_assignation.assignation == project)
                & (db.academic_course_assignation.assignation == db.project.id)
            )
            .select()
            .first()
        )

    if not validar_asig:
        asignacion = (
            db(
                (db.user_project.period == periodo)
                & (db.user_project.project == project)
                & (db.user_project.project == db.project.id)
            )
            .select()
            .first()
        )

    curso = asignacion.project

    if validar_asig and not asignacion:
        session.flash = "No se encuentra asignado al curso"
        redirect(URL("default", "home"))

    query = iso_utils.iso_get_tutores(project, periodo)
    tutores = db.executesql(query)

    return locals()


@auth.requires(
    auth.has_membership("Student") or auth.has_membership("Super-Administrator")
)
def guardar_reporte():
    varss = request.vars
    datos = None
    fecha = varss["fecha_incidente"].split("-")
    date_incidente = date(int(fecha[0]), int(fecha[1]), int(fecha[2]))

    if date_incidente > date.today():
        session.flash = "Fecha de incidente no puede ser mayor a la fecha actual"
        redirect(URL("default", "home"))

    try:
        datos = {
            "descripcion": varss["descripcion"],
            "fecha_reporte": varss["fecha_incidente"],
            "email": varss["correo"],
            "id_project": varss["project"],
            "id_period": varss["periodo"],
            "id_auth_user": auth.user.id,
            "id_tipo_incidente": varss["tipo_incidente"],
            "id_tutor": varss["tutor"],
        }
    except:
        session.flash = "No se ha creado el incidente"
        redirect(URL("default", "home"))

    resultado = dict(db.iso_incidente.validate_and_insert(**datos))
    errores = resultado["errors"].__dict__
    if len(errores):
        session.flash = "No se ha creado el incidente"
        redirect(URL("default", "home"))

    session.flash = "Se ha reportado el incidente"
    redirect(URL("default", "home"))


@auth.requires(
    auth.has_membership("Student") or auth.has_membership("Super-Administrator")
)
def ver_mis_incidentes():
    id_user = auth.user.id
    id_periodo = 0
    periodo_act = cpfecys.current_year_period()

    try:
        id_periodo = int(request.vars["periodo"])
    except:
        id_periodo = periodo_act.id

    periodos = db().select(db.period_year.ALL, orderby=~db.period_year.id)

    incidentes = db(
        (db.iso_incidente.id_period == id_periodo)
        & (db.iso_incidente.id_auth_user == id_user)
        & (db.iso_incidente.id_project == db.project.id)
    ).select()

    variables = {
        "periodos": periodos,
        "id_periodo": id_periodo,
        "periodo_act": periodo_act,
        "incidentes": incidentes,
    }
    return variables


@auth.requires(auth.has_membership("Student"))
def editar_incidente():
    id_incidente = request.args(0)
    periodo_act = cpfecys.current_year_period()

    if id_incidente is None:
        session.flash = "Debe indicar un incidente"
        redirect(URL("default", "home"))

    incidente = (
        db(
            (db.iso_incidente.id == id_incidente)
            & (db.iso_incidente.id_auth_user == auth.user.id)
        )
        .select()
        .first()
    )

    if not incidente:
        session.flash = "No puede editar el incidente"
        redirect(URL("default", "home"))

    fecha = date.today()
    if fecha != incidente.fecha_creacion:
        session.flash = (
            "Los incidentes solo pueden ser editados el día en que se crearon"
        )
        redirect(URL("default", "home"))

    """los incidentes
    editables son los del semestre actual"""
    if incidente.id_period != periodo_act.id:
        session.flash = """No se pueden editar
        incidentes de semestres anteriores"""
        redirect(URL("default", "home"))

    db.iso_incidente.id_tutor.writable = False
    db.iso_incidente.id_tutor.readable = False
    db.iso_incidente.fecha_creacion.writable = False
    db.iso_incidente.fecha_creacion.readable = False

    tutor = (
        db((db.auth_user.id == incidente.id_tutor))
        .select(db.auth_user.first_name, db.auth_user.last_name)
        .first()
    )
    incidente = db.iso_incidente(id_incidente)
    crud.settings.update_deletable = False

    form = crud.update(
        db.iso_incidente,
        incidente,
        next=URL("iso_reporte_incidente", "ver_mis_incidentes"),
    )

    return dict(form=form, tutor=tutor)


@auth.requires(auth.has_membership("DSI") or auth.has_membership("Super-Administrator"))
def listar_incidentes():
    id_periodo = None

    try:
        id_periodo = request.vars["periodo"]
    except:
        pass

    if not id_periodo:
        periodo_act = cpfecys.current_year_period()
        id_periodo = str(periodo_act.id)

    query = iso_utils.iso_get_incidentes_curso(id_periodo)
    incidentes = db.executesql(query)
    periodos = db().select(db.period_year.ALL, orderby=~db.period_year.id)
    id_periodo = int(id_periodo)

    return dict(incidentes=incidentes, periodos=periodos, id_periodo=id_periodo)


@auth.requires(auth.has_membership("DSI") or auth.has_membership("Super-Administrator"))
def listar_incidentes_curso():
    id_period = 0
    id_project = 0
    id_tutor = 0

    try:
        id_period = request.vars["periodo"]
        id_project = request.vars["project"]
        id_tutor = request.vars["id_tutor"]
    except:
        session.flash = "Debe indicar el periodo y el curso"
        redirect(URL("iso_reporte_incidente", "listar_incidentes"))

    if id_period == 0 or id_project == 0 or id_tutor == 0:
        session.flash = "Debe indicar el periodo y el curso"
        redirect(URL("iso_reporte_incidente", "listar_incidentes"))

    incidentes = db(
        (db.iso_incidente.id_period == id_period)
        & (db.iso_incidente.id_project == id_project)
        & (db.iso_incidente.id_tutor == id_tutor)
        & (db.project.id == id_project)
        & (db.iso_tipo_incidente.id == db.iso_incidente.id_tipo_incidente)
    ).select(
        db.iso_tipo_incidente.descripcion,
        db.iso_incidente.descripcion,
        db.iso_incidente.fecha_reporte,
        db.iso_incidente.fecha_creacion,
        db.iso_incidente.email,
        db.project.name,
        orderby=~db.iso_incidente.fecha_creacion,
    )

    tutor = (
        db((db.auth_user.id == id_tutor))
        .select(db.auth_user.first_name, db.auth_user.last_name, db.auth_user.username)
        .first()
    )

    return dict(incidentes=incidentes, tutor=tutor)


@auth.requires(auth.has_membership("Super-Administrador") or auth.has_membership("DSI"))
def incidentes_dinamicos():
    db.iso_vw_incidentes.id_tutor.readable = False
    db.iso_vw_incidentes.id.readable = False
    db.iso_vw_incidentes.id_period_year.readable = False
    db.iso_vw_incidentes.project_id.readable = False
    links = [
        {
            "header": "Consultar",
            "body": lambda row: A(
                "Consulta",
                _href=URL("iso_reporte_incidente", "listar_incidentes_curso")
                + "?id_tutor="
                + str(row.id_tutor)
                + "&periodo="
                + str(row.id_period_year)
                + "&project="
                + str(row.project_id),
            )
            if row.incidentes
            else "",
        }
    ]
    print(links)

    grid = SQLFORM.grid(
        db.iso_vw_incidentes,
        editable=False,
        deletable=False,
        details=False,
        links=links,
        links_in_grid=True,
    )
    return dict(grid=grid)


@auth.requires(auth.has_membership("Super-Administrador") or auth.has_membership("DSI"))
def incidentes():
    grid = SQLFORM.grid(db.iso_tipo_incidente, deletable=False)

    return locals()
