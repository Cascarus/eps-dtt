# coding: utf8
import datetime
import cpfecys
import dsi_queries as queries


@auth.requires_login()
@auth.requires_membership('DSI')
def absence_justifications():
    period_id = cpfecys.current_year_period().id

    justification_grid_query = (
        (db.dsi_justification.period == period_id) & (db.dsi_justification.schedule_asignation_id == db.dsi_assignation_schedule.id)
        & (db.dsi_assignation_schedule.schedule_id == db.dsi_schedule.id) & (db.dsi_schedule.assistance_type_id == db.dsi_assistance_type.id)
        & (db.dsi_justification.resolution_status == db.dsi_justification_status.id) & (db.dsi_justification.project == db.user_project.id)
        & (db.user_project.project == db.project.id) & (db.user_project.assigned_user == db.auth_user.id)
        & (db.dsi_justification.justification_type == db.dsi_justification_type.id)
    )

    justification_grid_fields = [
        db.dsi_justification.id,
        db.dsi_justification.absence_date,
        db.dsi_justification_type.name,
        db.dsi_justification_status.name,
        db.dsi_justification.contexto,
        db.project.name,
        db.dsi_assistance_type.name,
        db.dsi_justification.requester_user,
        db.auth_user.username,
        db.auth_user.first_name,
        db.auth_user.last_name,
        db.dsi_justification.image,
        db.dsi_justification.description,
        db.dsi_justification.created_at,
        db.dsi_justification.resolution_date,
        db.dsi_justification.resolution_description,
        db.dsi_justification.resolver_user
    ]

    links = [dict(header='Funciones', body=lambda row: get_justification_button(row))]

    justification_grid = SQLFORM.grid(
        justification_grid_query,
        justification_grid_fields,
        csv=False,
        searchable=True,
        sortable=True,
        deletable=False,
        editable=False,
        create=False,
        user_signature=True,
        maxtextlength=255,
        paginate=50,
        details=False,
        links=links
    )
    
    justification_grid.attributes = {'_class': 'table table-bordered'}
    return dict(justification_grid=justification_grid)

@auth.requires_login()
@auth.requires_membership('DSI')
def absence_justifications_resolution():
    period_id = cpfecys.current_year_period().id

    justification_grid_query = (
        (db.dsi_justification.period == period_id) & (db.dsi_justification.schedule_asignation_id == db.dsi_assignation_schedule.id)
        & (db.dsi_assignation_schedule.schedule_id == db.dsi_schedule.id) & (db.dsi_schedule.assistance_type_id == db.dsi_assistance_type.id)
        & (db.dsi_justification.resolution_status == db.dsi_justification_status.id) & ((db.dsi_justification_status.name == 'rechazado')
        | (db.dsi_justification_status.name == 'aprobado')) & (db.dsi_justification.project == db.user_project.id)
        & (db.user_project.project == db.project.id) & (db.user_project.assigned_user == db.auth_user.id)
        & (db.dsi_justification.justification_type == db.dsi_justification_type.id)
    )

    justification_grid_fields = [
        db.dsi_justification.id,
        db.dsi_justification.absence_date,
        db.dsi_justification_type.name,
        db.dsi_justification_status.name,
        db.dsi_justification.contexto,
        db.project.name,
        db.dsi_assistance_type.name,
        db.dsi_justification.requester_user,
        db.auth_user.username,
        db.auth_user.first_name,
        db.auth_user.last_name,
        db.dsi_justification.image,
        db.dsi_justification.description,
        db.dsi_justification.created_at,
        db.dsi_justification.resolution_date,
        db.dsi_justification.resolution_description,
        db.dsi_justification.resolver_user
    ]

    justification_grid = SQLFORM.grid(
        justification_grid_query,
        justification_grid_fields,
        csv=False,
        searchable=True,
        sortable=True,
        deletable=False,
        editable=False,
        create=False,
        user_signature=True,
        maxtextlength=255,
        paginate=50,
        details=False
    )

    justification_grid.attributes = {'_class': 'table table-bordered'}
    return dict(justification_grid=justification_grid)

@auth.requires_login()
@auth.requires_membership('DSI')
def assignation_report():
    periodo_actual = cpfecys.current_year_period()
    period_id = periodo_actual.id

    periodo_seleccionado = request.vars.periodo or period_id
    periodo = db(db.period_year.id == periodo_seleccionado).select(db.period_year.id, db.period_year.yearp, db.period_year.period).first()
    if not periodo:
        periodo = periodo_actual
        period_id = periodo_actual.id
    else:
        period_id = periodo.id

    title = f"Asignación de horarios para el semestre {periodo.period} en el año {periodo.yearp}"

    assignation_grid_query = (
        (db.dsi_assignation_schedule.tutor_id == db.auth_user.id) & (db.dsi_assignation_schedule.period == period_id)
        & (db.dsi_assignation_schedule.isEnabled == 1) & (db.dsi_assignation_schedule.project_assignation == db.user_project.id)
        & (db.user_project.project == db.project.id) & (db.dsi_assignation_schedule.schedule_id == db.dsi_schedule.id)
        & (db.dsi_schedule.week_day == db.day_of_week.id) & (db.dsi_schedule.assistance_type_id == db.dsi_assistance_type.id)
    )

    assignation_grid_fields = [
        db.auth_user.username,
        db.auth_user.first_name,
        db.auth_user.last_name,
        db.dsi_schedule.starting_hour,
        db.dsi_schedule.ending_hour,
        db.day_of_week.name,
        db.dsi_assistance_type.name,
        db.project.project_id,
        db.project.name
    ]

    assignation_grid = SQLFORM.grid(
        assignation_grid_query,
        assignation_grid_fields,
        csv=True,
        searchable=True,
        sortable=True,
        deletable=False,
        editable=False,
        create=False,
        user_signature=True,
        maxtextlength=255,
        paginate=50,
        details=False
    )

    assignation_grid.attributes = {'_class': 'table table-bordered'}
    return dict(assignation_grid=assignation_grid, title=title)

@auth.requires_login()
@auth.requires_membership('DSI')
def assistance_report():
    periodo_actual = cpfecys.current_year_period()
    period_id = periodo_actual.id

    justification_grid_query = (
        (db.dsi_assistance.tutor == db.auth_user.id) & (db.dsi_assistance.period == period_id)
        & (db.dsi_assistance_type.id == db.dsi_assistance.assistance_type)
    )

    jusitifcation_grid_fields = [
        db.dsi_assistance.starting_hour,
        db.dsi_assistance.starting_score,
        db.dsi_assistance.finishing_hour,
        db.dsi_assistance.finishing_score,
        db.dsi_assistance.score,
        db.auth_user.username,
        db.auth_user.first_name,
        db.auth_user.last_name,
        db.dsi_assistance_type.name,
        db.dsi_assistance.created_at,
        db.project.project_id,
        db.project.name
    ]

    justification_grid = SQLFORM.grid(
        justification_grid_query,
        jusitifcation_grid_fields,
        csv=True,
        searchable=True,
        sortable=True,
        deletable=False,
        editable=False,
        create=False,
        user_signature=True,
        maxtextlength=255,
        paginate=20,
        details=False,
        orderby=~db.dsi_assistance.starting_hour
    )

    return dict(justification_grid=justification_grid)

@auth.requires_login()
@auth.requires_membership('DSI')
def assistance_report_now():
    now = datetime.datetime.now()
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    
    hoy = datetime.datetime.combine(now, datetime.datetime.min.time())
    manana = datetime.datetime.combine(tomorrow, datetime.datetime.min.time())
    
    periodo_actual = cpfecys.current_year_period()
    period_id = periodo_actual.id

    jusitifcation_grid_query = (
        (db.dsi_assistance.tutor == db.auth_user.id) & (db.dsi_assistance.period == period_id)
        & (db.dsi_assistance_type.id == db.dsi_assistance.assistance_type) & (db.dsi_assistance.starting_hour > hoy)
        & (db.dsi_assistance.starting_hour < manana)
    )

    jusitifcation_grid_fields = [
        db.dsi_assistance.starting_hour,
        db.dsi_assistance.starting_score,
        db.dsi_assistance.finishing_hour,
        db.dsi_assistance.finishing_score,
        db.dsi_assistance.score,
        db.auth_user.username,
        db.auth_user.first_name,
        db.auth_user.last_name,
        db.dsi_assistance_type.name,
        db.dsi_assistance.created_at,
        db.project.project_id,
        db.project.name
    ]

    justification_grid = SQLFORM.grid(
        jusitifcation_grid_query,
        jusitifcation_grid_fields,
        csv=True,
        searchable=True,
        sortable=True,
        deletable=False,
        editable=False,
        create=False,
        user_signature=True,
        maxtextlength=255,
        paginate=20,
        details=False,
        orderby=~db.dsi_assistance.starting_hour
    )

    return dict(justification_grid=justification_grid)

@auth.requires_login()
@auth.requires_membership('DSI')
def create_day_schedule():
    period_id = cpfecys.current_year_period().id

    is_enabled = None
    try:
        is_enabled = db.executesql(queries.get_system_parameter_by_name(period_id, 'habilitar_dsi_horarios'))[0][4]
    except IndexError:
        session.flash = 'No hay información'
        redirect(URL('dsi_dsi', 'schedule_assignation'))

    if is_enabled == 0:
        session.flash = 'La administracion de horarios esta deshabilitada, contacte al administrador para más inforamción.'
        redirect(URL('dsi_dsi', 'schedule_assignation'))

    back_button = A(
        I(_class='fa fa-arrow-left', _aria_hidden='true'),
        f" {T('Back')}",
        _class='btn btn-primary',
        _href=URL('dsi_dsi', 'schedule_assignation'),
    )

    create_day_schedule = FORM(
        TABLE(
            TR(
                TD('Día de la semana: '),
                TD(get_day_of_week_select())
            ),
            BR(),
            TR(
                TD('Tipo de asistencia: '),
                TD(get_assistance_type_select())
            ),
            BR(),
            TR(
                TD(LABEL('Hora de inicio')),
                TD(INPUT(_name='startingHour', _type='time'))
            ),
            BR(),
            TR(
                TD(LABEL('Hora de finalización')),
                TD(INPUT(_name='endingHour', _type='time'))
            ),
            BR(),
            TR(
                DIV(
                    I(_class='fa fa-floppy-o', _aria_hidden='true'),
                    INPUT(_type='submit', _value='Guardar', _class='btn btn-success btn-sm'),
                    _class='btn btn-success btn-sm'
                )
            )
        )
    )

    if create_day_schedule.process(formname='crate_day_schedule').accepted:
        starting_hour = request.vars.startingHour
        ending_hour = request.vars.endingHour
        day_of_week = request.vars.dayOfWeek
        assistance_type_id = request.vars.assistanceType

        db.dsi_schedule.insert(
            starting_hour=starting_hour,
            ending_hour=ending_hour,
            week_day=day_of_week,
            period=period_id,
            assistance_type_id=assistance_type_id,
            created_at=datetime.datetime.now(),
            created_by=auth.user.username
        )
        session.flash = 'Horario creado'

    return dict(create_day_schedule=create_day_schedule, back_button=back_button)

@auth.requires_login()
@auth.requires_membership('DSI')
def create_holidays_admin():
    period_id = cpfecys.current_year_period().id

    try:
        if ((False, True)[db.executesql(queries.get_system_parameter_by_name(period_id, 'habilitar_dsi_asuetos'))[0][4] == 1] == False):
            redirect(URL('dsi_dsi', 'holidays_admin'))
    except IndexError:
        session.flash = 'No hay información'
        redirect(URL('dsi_dsi', 'holidays_admin'))

    back_button = A(
        I(_class='fa fa-arrow-left', _aria_hidden='true'),
        f" {T('Back')}",
        _class='btn btn-primary',
        _href=URL('dsi_dsi', 'holidays_admin'),
    )
    form = FORM(
        TABLE(
            TR(
                TH(LABEL('Nombre de día libre')),
                TD(INPUT(_type='text', _name='name', _class="form-control"))
            ),
            TR(
                TH(LABEL('Fecha de día libre')),
                TD(INPUT(_name='holiday', _type='date', _class="form-control"))
            ),
            TR(
                INPUT(_type='submit', _value='Guardar', _class="btn btn-primary")
            )
        )
    )

    if (form.accepts(request, session)):
        if request.vars.name != '' and request.vars.holiday != '':
            db.dsi_holiday.insert(
                name=request.vars.name,
                enabled=1,
                holiday_date=request.vars.holiday,
                created_at=datetime.datetime.now(),
                created_by=auth.user.username
            )
            session.flash = 'Día de asueto almacenado.'
            redirect(URL('dsi_dsi', 'create_holidays_admin'))
        else:
            session.flash = 'Rellene todos los campos para completar esta acción'
            redirect(URL('dsi_dsi', 'create_holidays_admin'))

    return dict(form=form, back_button=back_button)

@auth.requires_login()
@auth.requires_membership('DSI')
def create_schedule_assignation():
    period_id = cpfecys.current_year_period().id

    is_enabled = None
    try:
        is_enabled = db.executesql(queries.get_system_parameter_by_name(period_id, 'habilitar_dsi_horarios'))[0][4]
    except IndexError:
        session.flash = 'No hay información en la base de datos'
        redirect(URL('dsi_dsi', 'schedule_assignation'))

    if is_enabled == 0:
        session.flash = 'La administracion de horarios esta deshabilitada, contacte al administrador para más inforamción.'
        redirect(URL('dsi_dsi', 'schedule_assignation'))

    schedule_options = ''
    day_of_week_select = get_day_of_week_select()
    assistance_type_select = get_assistance_type_select()

    tutor_select = None
    if not request.args:
        tutor_select = get_tutor_form_select(period_id)
    else:
        tutor_select = get_tutor_form_select(period_id, request.args[0])

    back_button = A(
        I(_class='fa fa-arrow-left', _aria_hidden='true'),
        f" {T('Back')}",
        _class='btn btn-primary',
        _href=URL('dsi_dsi', 'schedule_assignation'),
    )

    form_search_schedule = FORM(
        TABLE(
            TR(
                TH("Tutor"),
                TD(tutor_select)
            ),
            TR(
                TH("Dia de la semana"),
                TD(day_of_week_select)
            ),
            TR(
                TH("Tipo"),
                TD(assistance_type_select)
            ),
            TR(
                INPUT(_value=T('Search'), _type='submit', _class='btn btn-secondary')
            )
        )
    )

    datos = TABLE()
    curso_select = ''
    tutor_id = 0
    if form_search_schedule.process(formname='form_search_schedule').accepted:
        day_of_week_id = request.vars.dayOfWeek
        type_id = request.vars.assistanceType
        tutor_id = request.vars.tutor

        tutor_informations = get_tutor_information(tutor_id, period_id)
        tutor_information = tutor_informations[0]

        curso_select = get_curso_select(tutor_informations, None)

        assignation_schedule = db.executesql(queries.get_schedule_by_period_and_week_day_and_type_admin(period_id, type_id, day_of_week_id))
        if assignation_schedule:
            schedule_options = list()
            schedule_options.append(TR(
                TH('Inicio'),
                TH('Fin'),
                TH('Asignar')
            ))
            for schedule in assignation_schedule:
                schedule_options.append(
                    TR(
                        TD(schedule[2]),
                        TD(schedule[3]),
                        TD(INPUT(_type='radio', _value=schedule[0], _name='schedule'))
                    )
                )  
        else:
            schedule_options = TR(TD('Sin horarios disponibles', _colspan=2))

        dia = db.executesql(queries.get_day_of_week_by_id(request.vars.dayOfWeek))
        dia = dia[0]

        tipo = db.executesql(queries.get_assistance_type(request.vars.assistanceType))
        tipo = tipo[0]

        first_name = ' '.join(list(map(lambda x: x.capitalize(), tutor_information[2].split(' '))))
        last_name = ' '.join(list(map(lambda x: x.capitalize(), tutor_information[3].split(' '))))
        datos = TABLE(
            TR(
                TH("Dia"),
                TD(dia[1])
            ),
            TR(
                TH("Tipo"),
                TD(tipo[1].upper())
            ),
            TR(
                TH("Tutor"),
                TD(f"{tutor_information[0].strip()} - {first_name.strip()} {last_name.strip()}")
            ),
            TR(
                INPUT(_TYPE='hidden', _name='scheduleType', _value=tipo[0])
            )
        )

    form_create_schedule = FORM(
        datos,
        TABLE(
            TR(
                TH("Curso"),
                TD(curso_select)
            ),
            TR(
                TH("Salon"),
                TD(INPUT(_type='text', _name='classroom', _class='form-control'))
            ),
            TR(
                INPUT(_type="hidden", _value=tutor_id, _name="tutorId")
            )
        ),
        TABLE(schedule_options, _class="table table-striped table-bordered"),
        TD(
            DIV(
                I(_class='fa fa-floppy-o', _aria_hidden='true'),
                INPUT(_type='submit', _value='Guardar', _class='btn btn-success btn-sm'),
                _class='btn btn-success btn-sm'
            )
        )
    )

    if form_create_schedule.process(formname='form_create_schedule').accepted:
        if request.vars.tutorId != "0":
            session.flash = validate_assignation_schedule(period_id, request.vars.tutorId, request.vars.scheduleType, request.vars.schedule, request.vars.classroom, request.vars.c)
        else:
            session.flash = 'Debe seleccionar un tutor academico para asignarle un horario'
        redirect(URL('dsi_dsi', 'create_schedule_assignation'))

    return dict(form_create_schedule=form_create_schedule, back_button=back_button, form_search_schedule=form_search_schedule)

@auth.requires_login()
@auth.requires_membership('DSI')
def creation_absence_justifications():
    period_id = cpfecys.current_year_period().id

    if not can_create_justification(period_id):
        session.flash = 'No puede crear una nueva justificación porque excede la cantidad permitida.'
        redirect(URL('dsi_dsi', 'absence_justifications'))

    justification_types = db(db.dsi_justification_type).select(db.dsi_justification_type.name, db.dsi_justification_type.id)
    back_button = A(
        I(_class='fa fa-arrow-left', _aria_hidden='true'),
        f" {T('Back')}",
        _class='btn btn-primary',
        _href=URL('dsi_dsi', 'absence_justifications'),
    )
    
    type_options = list()
    type_options.append(OPTION("Elija un tipo", _value=0))
    for justification_type in justification_types:
        type_options.append(OPTION(justification_type.name.capitalize(), _value=justification_type.id))

    create_justification = FORM(
        TABLE(
            TR(
                TD(LABEL(f"{T('Description')}:")),
                TD(INPUT(_name='description', requires=IS_NOT_EMPTY()))
            ),
            BR(),
            TR(
                TD(LABEL(f"{T('Document')}:")),
                TD(INPUT(_name='document', _type="file", _accept="application/pdf", requires=[
                    IS_NOT_EMPTY(),
                    IS_LENGTH(2097152, 0, error_message='El documento debe poseer un tamaño desde 1KB hasta 2 MB.')
                ]))
            ),
            BR(),
            TR(
                TD('El tipo de documento ha seleccionar debe ser de tipo PDF y con un tamaño entre 1KB y 2MB.', _colspan=2)
            ),
            BR(),
            TR(
                TD(BUTTON(T('Send'), _type='submit', _class='btn btn-secondary'))
            )
        )
    )

    if (create_justification.accepts(request, session)):
        tutor_id = auth.user.id

        if not can_create_justification(period_id):
            session.flash = 'Error: Usted excede la cantidad de justificaciónes permitida para el role dsi.'
            redirect(URL('dsi_dsi', 'absence_justifications'))

        status = None
        try:
            status = db.executesql(queries.get_justification_status_id('justificado_dsi'))[0][0]
            db(db.dsi_justification.id == request.args[0]).update(
                description=request.vars.description,
                image=request.vars.document,
                resolution_status=status,
                requester_user=tutor_id,
                created_by=session.auth.user.username
            )

            session.flash = T('Justificación creada')
        except IndexError:
            sesion.flash = "No hay información"
        
        redirect(URL('dsi_dsi', 'absence_justifications'))
    elif create_justification.errors:
        response.flash = T('form has errors')
    else:
        response.flash = T('please fill the form')

    return dict(create_justification=create_justification, back_button=back_button)

@auth.requires_login()
@auth.requires_membership('DSI')
def fingerprint_report():
    fingerprint_grid_query = (db.dsi_fingerprint.tutor_id == db.auth_user.id)

    fingerprint_grid_fields = [
        db.auth_user.username,
        db.auth_user.first_name,
        db.auth_user.last_name,
        db.dsi_fingerprint.created_at
    ]

    fingerprint_grid = SQLFORM.grid(
        fingerprint_grid_query,
        fingerprint_grid_fields,
        csv=False,
        searchable=True,
        sortable=True,
        deletable=False,
        editable=False,
        create=False,
        user_signature=True,
        maxtextlength=255,
        paginate=50,
        details=False
    )

    return dict(fingerprint_grid=fingerprint_grid)

@auth.requires_login()
@auth.requires_membership('DSI')
def holidays_admin():
    justification_grid_query = (db.dsi_holiday.enabled == True)

    create_button = A(
        BUTTON(
            SPAN(_class="icon plus icon-plus glyphicon glyphicon-plus"), 
            ' Crear', _class='btn btn-primary'
        ),
        _href=URL('dsi_dsi', 'create_holidays_admin')
    )

    justification_grid_fields = [
        db.dsi_holiday.name,
        db.dsi_holiday.holiday_date
    ]

    justification_grid = SQLFORM.grid(
        justification_grid_query,
        justification_grid_fields,
        csv=True,
        searchable=True,
        sortable=True,
        deletable=False,
        editable=False,
        create=False,
        user_signature=True,
        maxtextlength=255,
        paginate=20,
        details=False
    )

    return dict(justification_grid=justification_grid, create_button=create_button)

@auth.requires_login()
@auth.requires_membership('DSI')
def schedule_assignation():
    period_id = cpfecys.current_year_period().id
    session.flash = None

    parameters = db(db.dsi_schedule_parameter).select(db.dsi_schedule_parameter.until_date)
    assignation_until = parameters[1].until_date

    # ListSchedule
    day_schedule_id = request.vars['daySchedule']
    list_schedules = FORM(
        H3('Administracion de horarios'),
        TABLE(
            TR(
                TD(LABEL('Día de la semana')),
                TD(get_day_of_week_select(day_schedule_id))
            ),
            TR(
                TD(INPUT(_type='submit', _value=T('Search'), _class="btn btn-primary"))
            )
        )
    )

    create_day_schedule_button = A(
        BUTTON(SPAN(_class="icon plus icon-plus glyphicon glyphicon-plus"), T('Assign'), _class="btn btn-primary"), 
        _href=URL('dsi_dsi', 'create_day_schedule')
    )

    day_schedule_table = ''
    if list_schedules.process(formname='list_schedules').accepted:
        day_id = request.vars.dayOfWeek
        schedules = db.executesql(queries.get_schedule_by_period_id_and_week_day(period_id, day_id))

        day_info = db.executesql(queries.get_day_of_week_by_id(day_id))
        day_info = day_info[0]
        if schedules is None or not schedules:
            day_schedule_table = DIV(
                P(B('Día seleccionado: ', SPAN(day_info[1]))),
                P('Sin horarios asignados')
            )
        else:
            day_schedules = list()
            day_schedules.append(TR(
                TH('Día'),
                TH('Tipo'),
                TH('Hora de inicio'),
                TH('Hora de fin'),
                TH('Acciones', _colspan=2)
            ))
            
            for schedule in schedules:
                day_schedules.append(TR(
                    TD(schedule[7]),
                    TD(schedule[9]),
                    TD(schedule[2]),
                    TD(schedule[3]),
                    TD(
                        A(
                            BUTTON(SPAN(_class="icon trash icon-trash glyphicon glyphicon-trash"), T('Delete'), _class="btn btn-primary"),
                            _href=URL('dsi_dsi', 'delete_day_schedule', args=schedule[0])
                        )
                    )
                ))

            day_schedule_table = DIV(
                P(
                    B('Día seleccionado: ', SPAN(day_info[1]))
                ),
                DIV(TABLE(day_schedules, _class="table table-striped table-bordered"))
            )

    # Horarios asignados al tutor
    tutor_select = None
    if not request.args:
        tutor_select = get_tutor_form_select(period_id)
    else:
        tutor_select = get_tutor_form_select(period_id, request.args[0])

    create_button = A(
        BUTTON(
            SPAN(_class="icon plus icon-plus glyphicon glyphicon-plus"),
            f" {T('Assign')}",
            _class="btn btn-primary"
        ),
        _href=URL('dsi_dsi', 'create_schedule_assignation', args=request.vars['tutor'])
    )

    tutor_search_form = FORM(
        H3('Lista de horarios asignados'),
        TABLE(
            TR(
                TD(LABEL(T('Academic Tutor'))),
                TD(tutor_select)
            ),
            TR(
                TD(INPUT(_type='submit', _value=T('Search'), _class="btn btn-primary"))
            )
        )
    )
    tutor_information_table = ''
    assignation_schedule_table = ''
    if tutor_search_form.process(formname='tutor_search_form').accepted:
        tutor_information = get_tutor_information(request.vars['tutor'], period_id)

        if not tutor_information:
            tutor_information_table = 'No Hay informacion del tutor'
        else:
            tutor_information = tutor_information[0]
            tutor_information_table = TABLE(
                TR(
                    TH('Carnet'),
                    TD(tutor_information[0])
                ),
                TR(
                    TH('CUI'),
                    TD((tutor_information[1], '--')[tutor_information[1] == None])
                ),
                TR(
                    TH('Nombre'),
                    TD(tutor_information[2] + ' ' + tutor_information[3])
                ),
                TR(
                    TH('Curso'),
                    TD(tutor_information[5])
                )
            )
            assignation_schedule = db.executesql(queries.get_tutor_schedule_by_period_id_and_tutor_id(period_id, request.vars['tutor']))
            if assignation_schedule is None or not assignation_schedule:
                assignation_schedule_table = 'Sin horarios asignados'
            else:
                schedules = list()
                schedules.append(TR(
                    TH('Hora Inicio'),
                    TH('Hora Fin'),
                    TH('Día'),
                    TH('Salon'),
                    TH('Tipo'),
                    TH('Curso')
                ))
                for schedule in assignation_schedule:
                    schedules.append(TR(
                        TD(schedule[1]),
                        TD(schedule[2]),
                        TD(schedule[4]),
                        TD(schedule[3]),
                        TD(schedule[5]),
                        TD(schedule[6]),
                    ))

                assignation_schedule_table = TABLE(schedules, _class="table table-striped table-bordered")

    return dict(
        create_button=create_button,
        tutor_search_form=tutor_search_form,
        tutor_information_table=tutor_information_table,
        assignation_schedule_table=assignation_schedule_table,
        list_schedules=list_schedules,
        day_schedule_table=day_schedule_table,
        create_day_schedule_button=create_day_schedule_button,
    )

@auth.requires_login()
@auth.requires_membership('DSI')
def can_create_justification(period_id):
    parametros = db.executesql(queries.get_system_parameter_by_name(period_id, 'cantidad_justificaciones_dsi'))
    cantidad_justificaciones_tutores = parametros[0][2]
    cantidad_justificaciones = db.executesql(queries.get_quantity_justifications_by_DSI_and_period(period_id))

    return (cantidad_justificaciones[0][0] < cantidad_justificaciones_tutores)

@auth.requires_login()
@auth.requires_membership('DSI')
def get_justification_button(row):
    button = ''
    if not row.dsi_justification.resolution_date:
        button = TR(
            TD(
                A(
                    BUTTON(      
                        SPAN(_class="fa fa-check"),
                        SPAN(' Justificar'),
                        _class='btn btn-sm btn-secondary'
                    ),
                    _href=URL('dsi_dsi', 'creation_absence_justifications', args=[row.dsi_justification.id])
                )
            )
        )

    return TABLE(button)

@auth.requires_login()
@auth.requires_membership('DSI')
def get_day_of_week_select(selected=None):
    days = db.executesql(queries.get_day_of_week())
    day_options = list()
    day_options.append(OPTION("Elija un día", _value=0))
    flag = False
    
    for day in days:
        if selected is not None and int(day[0]) == int(selected): flag = True
        else: flag = False
        day_options.append(OPTION(day[1].capitalize(), _value=day[0], _selected=flag))

    return SELECT(day_options, _name='dayOfWeek', requires=IS_INT_IN_RANGE(1, None), _class="form-control")

@auth.requires_login()
@auth.requires_membership('DSI')
def get_assistance_type_select(selected=None):
    types = db.executesql(queries.get_assistance_type_select())
    type_options = list()
    type_options.append(OPTION("Elija un tipo", _value=0))
    
    for type in types:
        if selected is not None and type[0] == selected:
            type_options.append(OPTION(type[1].capitalize(), _value=type[0], _selected='true'))
        else:
            type_options.append(OPTION(type[1].capitalize(), _value=type[0]))

    return SELECT(type_options, _name='assistanceType', requires=IS_INT_IN_RANGE(1, None), _class='form-control')

@auth.requires_login()
@auth.requires_membership('DSI')
def get_tutor_form_select(period_id, selected=None):
    tutors = db.executesql(queries.get_tutors_active_in_current_period(period_id))
    tutor_options = list()
    tutor_options.append(OPTION("Elija un tutor", _value=0))
    flag = False
    
    for tutor in tutors:
        if selected is not None and int(tutor[0]) == int(selected): flag = True
        else: flag = False

        first_name = ' '.join(list(map(lambda x: x.capitalize(), tutor[3].split(' '))))
        last_name = ' '.join(list(map(lambda x: x.capitalize(), tutor[4].split(' '))))

        tutor_options.append(
            OPTION(
                f"{tutor[1]} - {first_name.strip()} {last_name.strip()}", 
                _value=tutor[0],
                _selected=flag
            )
        )

    return SELECT(tutor_options, _name='tutor', requires=IS_INT_IN_RANGE(1, None), _class="form-control")

@auth.requires_login()
@auth.requires_membership('DSI')
def get_tutor_information(tutor_id, period_id):
    return db.executesql(queries.get_tutor_information(tutor_id, period_id))

@auth.requires_login()
@auth.requires_membership('DSI')
def get_curso_select(tutor_informations, selected):
    type_options = list()
    for information in tutor_informations:
        if selected is not None and int(information[6]) == int(selected):
            type_options.append(OPTION(information[5].encode('utf-8'), _value=information[6], _selected='true'))
        else:
            type_options.append(OPTION(information[5].encode('utf-8'), _value=int(information[6])))

    return SELECT(type_options, _name='c', requires=IS_INT_IN_RANGE(1, None), _class='form-control')

def get_user_project(tutor_id, period_id, asignacion_id):
    project = db((db.user_project.assigned_user == tutor_id) & (db.user_project.period == period_id)
            & (db.user_project.id == asignacion_id)).select(db.user_project.project).first()

    return project

def get_selected_schedule(schedule_id):
    return db(db.dsi_schedule.id == schedule_id).select(db.dsi_schedule.week_day, db.dsi_schedule.assistance_type_id, db.dsi_schedule.id, db.dsi_schedule.starting_hour).first()
    
def get_period_schedules(tutor_id, period_id, type_id, ENABLED, asignacion_id):
    horarios_por_periodo = db((db.dsi_assignation_schedule.schedule_id == db.dsi_schedule.id) & (db.dsi_assignation_schedule.tutor_id == tutor_id)
                        & (db.dsi_assignation_schedule.isEnabled == ENABLED) & (db.dsi_assignation_schedule.project_assignation == asignacion_id)
                        & (db.dsi_schedule.period == period_id) & (db.dsi_schedule.assistance_type_id == type_id)).select(db.dsi_assignation_schedule.id).as_list()

    return horarios_por_periodo

def get_same_day_schedule(tutor_id, period_id, horario, ENABLED):
    horario_mismo_dia = db((db.dsi_assignation_schedule.schedule_id == db.dsi_schedule.id) & (db.dsi_assignation_schedule.tutor_id == tutor_id)
                        & (db.dsi_assignation_schedule.isEnabled == ENABLED) & (db.dsi_schedule.period == period_id)
                        & (db.dsi_schedule.week_day == horario.week_day)).select(db.dsi_assignation_schedule.id).as_list()

    return horario_mismo_dia

@auth.requires_login()
@auth.requires_membership('DSI')
def validate_schedule_with_course_schedule(tutor_id, day_id, period_id):
    schedules = db.executesql(queries.get_course_schedule_by_tutor_id_and_day_id(tutor_id, day_id, period_id))
    
    if not schedules:
        return True
    return False

def validate_tutors_amount_in_schedule(schedule_id):
    limite_cantidad_tutores = db(db.dsi_schedule_parameter.name == 'tutorAmount').select(db.dsi_schedule_parameter.tutor_amout).first()
    limite_cantidad_tutores = limite_cantidad_tutores.tutor_amount

    cantidad_tutores_en_horario = db.executesql(queries.get_tutor_quantity_by_schedule_id(schedule_id))

    cantidad_tutores_en_horario_numero = 0
    if cantidad_tutores_en_horario:
        cantidad_tutores_en_horario_numero = cantidad_tutores_en_horario[0][1]

    if limite_cantidad_tutores < cantidad_tutores_en_horario_numero:
        return False
    return True

@auth.requires_login()
@auth.requires_membership('DSI')
def save_assignation_schedule(schedule_id, tutor_id, classroom, period_id, assignation_id):
    db.dsi_assignation_schedule.insert(
        schedule_id=schedule_id,
        tutor_id=tutor_id,
        classroom=classroom,
        created_at=datetime.datetime.now(),
        isEnabled=1,
        created_by=auth.user.username,
        updated_at=datetime.datetime.now(),
        updated_by=auth.user.username,
        period=period_id,
        project_assignation=assignation_id
    )

@auth.requires_login()
@auth.requires_membership('DSI')
def validate_assignation_schedule(period_id, tutor_id, type_id, schedule_id, class_room, asignacion_id):
    dsi_type = 2
    ENABLED = 1

    project = get_user_project(tutor_id, period_id, asignacion_id)
    horario = get_selected_schedule(schedule_id)
    horarios_por_periodo = get_period_schedules(tutor_id, period_id, type_id, ENABLED, asignacion_id)
    horario_mismo_dia = get_same_day_schedule(tutor_id, period_id, horario, ENABLED)

    if horario_mismo_dia:
        return 'Error, usted ya posee un horario el día seleccionado'

    horario_compatible = validate_schedule_with_course_schedule(tutor_id, horario.week_day, period_id)
    if not horario_compatible:
        return 'Error, el día que se imparte el curso coincide con el día del horario elegido de DSI.'
    
    if type_id == dsi_type:
        hay_cupo_en_el_horario = validate_tutors_amount_in_schedule(schedule_id)
        if not hay_cupo_en_el_horario:
            return 'Error, ya no hay cupo en el horario seleccionado.'

    if not horarios_por_periodo:
        if horario.assistance_type_id != dsi_type:
            save_assignation_schedule(horario.id, tutor_id, class_room, period_id, asignacion_id)
            return 'Horario almacenado correctamente'

    if type_id == dsi_type:
        excepciones = db((db.dsi_exception_course.period == period_id) & (db.dsi_exception_course.project == project.project)).select(db.dsi_exception_course.single_hour).first()

        if excepciones:
            if excepciones.single_hour == 1:
                if len(horarios_por_periodo) < 1:
                    save_assignation_schedule(horario.id, tutor_id, class_room, period_id, asignacion_id)
                    return 'Asignación de horario realizada.'
                else:
                    return 'Error, excede la cantidad de horarios asignados permitidos.'

    if len(horarios_por_periodo) < 2:
        excepciones = db((db.dsi_exception_course.period == period_id) & (db.dsi_exception_course.project == project.project)).select(db.dsi_exception_course.evening).first()

        format = '%H:%M:%S'
        time1 = datetime.datetime.strptime(str(horario.starting_hour), format).time()
        time2 = datetime.datetime.strptime(str(datetime.time(12)), format).time()

        if time2 < time1:
            if excepciones and excepciones.evening:
                save_assignation_schedule(horario.id, tutor_id, class_room, period_id, asignacion_id)
            else:
                return 'Horario seleccionado es por la tarde y no esta permitido'
        else:
            save_assignation_schedule(horario.id, tutor_id, class_room, period_id, asignacion_id)
        return 'Asignación de horarios realizada.'

    return 'Error, excede la cantidad de horarios asignados permitidos.'

@auth.requires_login()
@auth.requires_membership('DSI')
def delete_day_schedule():
    period_id = cpfecys.current_year_period().id
    is_enabled = db.executesql(queries.get_system_parameter_by_name(period_id, 'habilitar_dsi_horarios'))[0][4]

    if is_enabled == 0:
        session.flash = 'La administracion de horarios esta deshabilitada, contacte al administrador para más inforamción.'
        redirect(URL('dsi_dsi', 'schedule_assignation'))

    db(db.dsi_schedule.id == request.args[0]).delete()
    session.flash = 'Horario eliminado.'
    redirect(URL('dsi_dsi', 'schedule_assignation'))

@auth.requires_login()
@auth.requires_membership('DSI')
def delete_schedule_assignation():
    period_id = cpfecys.current_year_period().id
    is_enabled = db.executesql(queries.get_system_parameter_by_name(period_id, 'habilitar_dsi_horarios'))[0][4]

    if is_enabled == 0:
        session.flash = 'La administracion de horarios esta deshabilitada, contacte al administrador para más inforamción.'
        redirect(URL('dsi_dsi', 'schedule_assignation'))

    db(db.dsi_assignation_schedule.id == request.args[0]).update(isEnabled=0)
    session.flash = 'Asignación de horario eliminado.'
    redirect(URL('dsi_dsi', 'schedule_assignation'))


#cascarus -- FOROS-VIEW
@auth.requires_login()
@auth.requires_membership('DSI')
def foro_view():
    periodo = cpfecys.current_year_period()
    if request.vars['period']:
        periodo_parametro = request.vars['period']
        periodo = db(db.period_year.id == periodo_parametro).select().first()

    periods_temp = db.executesql("""
        SELECT py.id, py.yearp, p.name
        FROM period_year py
        INNER JOIN period p on p.id = py.period
        ORDER BY py.id DESC;
    """.format(auth.user.id))

    periods = [];
    
    for p in periods_temp:
        period_temp = {
            'id': p[0],
            'yearp': p[1],
            'name': p[2]
        }
        objeto = type('Objeto', (object,), period_temp)()
        periods.append(objeto)

    rows = db(db.foro.estado == 'pendiente').select()

    rows_temp = db((db.user_project.assigned_user == auth.user.id) &
                   (db.user_project.period == periodo.id)).select().first()

    return dict(
        rows = rows,
        periodo = periodo,
        periods=periods,
    )


#cascarus -- CONVERENCIA-VIEW
@auth.requires_login()
@auth.requires_membership('DSI')
def conferencia_view():
    periodo = cpfecys.current_year_period()
    if request.vars['period']:
        periodo_parametro = request.vars['period']
        periodo = db(db.period_year.id == periodo_parametro).select().first()

    periods_temp = db.executesql("""
        SELECT py.id, py.yearp, p.name
        FROM period_year py
        INNER JOIN period p on p.id = py.period
        ORDER BY py.id DESC;
    """.format(auth.user.id))

    periods = [];
    
    for p in periods_temp:
        period_temp = {
            'id': p[0],
            'yearp': p[1],
            'name': p[2]
        }
        objeto = type('Objeto', (object,), period_temp)()
        periods.append(objeto)

    rows = db(db.conferencia.estado == 'pendiente').select()

    rows_temp = db((db.user_project.assigned_user == auth.user.id) &
                   (db.user_project.period == periodo.id)).select().first()

    return dict(
        rows = rows,
        periodo = periodo,
        periods=periods,
    )