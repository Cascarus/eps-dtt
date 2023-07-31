import cpfecys
from gluon.tools import Crud

@auth.requires_login()
def events_list():
    cyp = cpfecys.current_year_period()
    assig = request.vars["assignation"]
    check = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.id == assig)
            & ((db.user_project.period <= cyp.id) & ((db.user_project.period.cast('integer') + db.user_project.periods) > cyp.id))).select(
                db.user_project.id,
                db.user_project.project
            ).first()

    print(assig, check)
    if check is None:
        session.flash = "No puede ver los eventos"
        redirect(URL("default", "home"))

    db.public_event.assignation.default = assig
    db.public_event.assignation.writable = False

    db.public_event.semester.default = cyp.id
    db.public_event.semester.writable = False
    events = db(db.public_event.assignation == check.id).select()
    query = (db.public_event.assignation == check.id)
    links = [dict(header='Funciones', body=lambda row: get_schedule(row))]
    grid = SQLFORM.grid(
        (db.public_event.assignation == check.id),
        csv=False,
        links=links
    )

    return dict(
        year=cyp.yearp,
        semester=cyp.period.name,
        name=check.project.name,
        events=events,
        grid=grid,
        assig=assig,
    )


@auth.requires_login()
def create_event():
    id_assig = request.args(0)
    cyp = cpfecys.current_year_period()

    if id_assig is None:
        session.flash = "No se puede crear un evento sin curso"
        redirect(URL("default", "home"))

    db.public_event.assignation.default = id_assig
    db.public_event.assignation.writable = False

    db.public_event.semester.default = cyp.id
    db.public_event.semester.writable = False

    form = crud.create(
        db.public_event,
        next=URL("eventos", "events_list", vars=dict(assignation=id_assig)),
    )

    return dict(form=form)


@auth.requires_login()
def detail_event():
    id_event = request.args(0)
    id_assig = request.args(1)

    if id_event is None or id_assig is None:
        session.flash = "Evento desconocido"
        redirect(URL("default", "home"))

    schedule = db(db.public_event_schedule.public_event == id_event).select()
    event = db.public_event(id_event)

    return dict(
        id_event=id_event, name=event.name, schedule=schedule, id_assig=id_assig
    )

@auth.requires_login()
def get_schedule(row):
    button = TR(
        TD(
            A(
                BUTTON(      
                    SPAN(_class="fa fa-clock-o"),
                    SPAN(' Horarios del evento'),
                    _class='btn btn-sm btn-secondary'
                ),
                _href=URL('eventos', 'detail_event', args=(row.id, row.assignation))
            )
        )
    )

    return TABLE(button)



@auth.requires_login()
def create_schedule():
    id_event = request.args(0)
    id_assig = request.args(1)

    if id_event is None or id_assig is None:
        session.flash = "No puede crear un Horario sin Evento"
        redirect(URL("default", "home"))

    db.public_event_schedule.public_event.default = id_event
    db.public_event_schedule.public_event.writable = False

    form = crud.create(
        db.public_event_schedule,
        next=URL("eventos", "detail_event", args=(id_event, id_assig)),
    )
    return dict(form=form)


@auth.requires_login()
def edit_schedule():
    id_sc = request.args(0)
    id_event = request.args(1)
    id_assig = request.args(2)

    if id_sc is None or id_event is None or id_assig is None:
        session.flash = "Sin paramametros"
        redirect(URL("default", "home"))

    sc = db.public_event_schedule(id_sc)

    db.public_event_schedule.public_event.writable = False

    if sc is None:
        session.flash = "No se encontro horario"
        redirect(URL("default", "home"))

    form = crud.update(
        db.public_event_schedule,
        sc,
        next=URL("eventos", "detail_event", args=(id_event, id_assig)),
    )

    return dict(form=form)
