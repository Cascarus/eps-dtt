import cpfecys
from gluon.tools import Crud
from datetime import date


@auth.requires(auth.has_membership("DSI"))
def registrar_utensilio():
    form = SQLFORM.grid(db.iso_utensilio, deletable=False)

    return dict(form=form)


@auth.requires(auth.has_membership("DSI"))
def registrar_prestamo():
    periodo = cpfecys.current_year_period()
    id_user = auth.user.id
    carnet = int(request.vars["id_user"])

    db.iso_prestamo.id_periodo.writable = False
    db.iso_prestamo.id_periodo.readable = False

    db.iso_prestamo.id_encargado_dsi.writable = False
    db.iso_prestamo.id_encargado_dsi.readable = False

    db.iso_prestamo.id_periodo.default = periodo
    db.iso_prestamo.id_encargado_dsi.default = id_user

    db.iso_prestamo.id_estudiante.writable = False
    db.iso_prestamo.id_estudiante.default = carnet

    db.iso_prestamo.fecha_devolucion.writable = False
    db.iso_prestamo.fecha_devolucion.readable = False

    def validar_fecha(form):
        fecha_p = form.vars.fecha_prestamo
        fecha_d = form.vars.fecha_est_dev

        if fecha_d < fecha_p:
            form.errors.fecha_est_dev = (
                "La fecha de devolución no debe ser menor a la fecha de préstamo"
            )

    form = crud.create(
        db.iso_prestamo, next=URL("default", "home"), onvalidation=validar_fecha
    )

    return dict(form=form)

@auth.requires(auth.has_membership("DSI"))
def ingresar_estudiante():
    form = FORM(
        LABEL("Ingrese carné estudiante"),
        INPUT(_name="carne", _class='form-control', requires=IS_NOT_EMPTY()),
        P(),
        INPUT(_type="submit", _class='btn btn-primary'),
    )

    if form.process().accepted:
        estudiante = db((db.academic.carnet == form.vars.carne)).select().first()

        if not estudiante:
            session.flash = "Carné no existe"
            redirect(URL("iso_prestamo", "ingresar_estudiante"))
        else:
            dato = {"id_user": estudiante.id_auth_user}
            redirect(URL("iso_prestamo", "registrar_prestamo", vars=dato))

    return dict(form=form)

@auth.requires(auth.has_membership("DSI"))
def listar_prestamos():
    periodo_act = cpfecys.current_year_period()

    prestamos = db(
        (db.iso_prestamo.id_periodo == periodo_act.id)
        & (db.iso_prestamo.fecha_devolucion == None)
        & (db.iso_prestamo.id_utensilio == db.iso_utensilio.id)
    ).select()

    datos = {"prestamos": prestamos}

    return datos


@auth.requires(auth.has_membership("DSI"))
def registrar_devolucion():
    id_prestamo = request.args(0)

    db.iso_prestamo.id_periodo.writable = False
    db.iso_prestamo.fecha_prestamo.writable = False
    db.iso_prestamo.fecha_est_dev.writable = False
    db.iso_prestamo.id_utensilio.writable = False
    db.iso_prestamo.id_encargado_dsi.writable = False
    db.iso_prestamo.id_estudiante.writable = False

    if id_prestamo is None:
        session.flash = "Debe indicar un prestamo"
        redirect(URL("default", "home"))

    prestamo = db((db.iso_prestamo.id == id_prestamo)).select().first()

    if not prestamo:
        session.flash = "No puede editar el prestamo"
        redirect(URL("default", "home"))

    prestamo = db.iso_prestamo(id_prestamo)
    crud.settings.update_deletable = False
    crud.messages.record_updated = "Devolución Registrada"

    form = crud.update(
        db.iso_prestamo, prestamo, next=URL("iso_prestamo", "listar_prestamos")
    )

    return dict(form=form)


@auth.requires(auth.has_membership("DSI"))
def reporte_prestamo():
    grid = SQLFORM.grid(db.iso_prestamo, editable=False, deletable=False, details=False)
    return dict(grid=grid)
