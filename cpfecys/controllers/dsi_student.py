# coding: utf8
import datetime
import dsi_queries as queries

@auth.requires_login()
@auth.requires_membership('Student')
def absence_justifications():
    period_id = cpfecys.current_year_period().id
    loged_user_id = auth.user.id

    justification_grid_query = (
        (db.dsi_justification.period == period_id) & (db.dsi_justification.resolution_status == db.dsi_justification_status.id)
        & (db.dsi_justification.project == db.user_project.id) & (db.user_project.project == db.project.id)
        & (db.user_project.assigned_user == db.auth_user.id) & (db.dsi_justification.justification_type == db.dsi_justification_type.id)
        & (db.auth_user.id == loged_user_id)
    )

    justification_grid_fields = [
        db.dsi_justification.id,
        db.dsi_justification_status.name,
        db.dsi_justification_type.name,
        db.dsi_justification.contexto,
        db.dsi_justification.absence_date,
        db.dsi_justification.description,
        db.dsi_justification.image,
        db.project.name,
        db.dsi_justification.requester_user,
        db.dsi_justification.resolution_description,
        db.dsi_justification.resolution_date,
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
        paginate=20,
        details=False,
        links=links
    )

    return dict(justification_grid=justification_grid)

@auth.requires_login()
@auth.requires_membership('Student')
def assistance_report():
    loged_user = auth.user
    period_id = cpfecys.current_year_period().id

    justification_grid_query = (
        (db.dsi_assistance.tutor == db.auth_user.id) & (db.dsi_assistance.tutor == loged_user.id)
        & (db.dsi_assistance.asignation_id == db.user_project.id) & (db.dsi_assistance_type.id == db.dsi_assistance.assistance_type)
        & (db.dsi_assistance.period == period_id) & (db.user_project.project == db.project.id)
    )

    justification_grid_fields = [
        db.dsi_assistance.starting_hour,
        db.dsi_assistance.starting_score,
        db.dsi_assistance.finishing_hour,
        db.dsi_assistance.finishing_score,
        db.dsi_assistance.score,
        db.auth_user.username,
        db.dsi_assistance_type.name,
        db.dsi_assistance.created_at,
        db.project.project_id,
        db.project.name
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

    return dict(justification_grid=justification_grid)

@auth.requires_login()
@auth.requires_membership('Student')
def creation_absence_justifications():
    period_id = cpfecys.current_year_period().id
    loged_user_id = auth.user.id

    if not can_create_justification(loged_user_id, period_id):
        session.flash = 'No puede crear una nueva justificación porque excede la cantidad permitida.'
        redirect(URL('dsi_student', 'absence_justifications'))

    back_button = A(
        I(_class='fa fa-arrow-left', _aria_hidden='true'),
        f" {T('Back')}",
        _class='btn btn-primary',
        _href=URL('dsi_student', 'absence_justifications'),
    )

    justification_types = db().select(db.dsi_justification_type.ALL)
    type_options = list()
    type_options.append(OPTION("Elija un tipo", _value=0))
    for justification_type in justification_types:
        type_options.append(OPTION(justification_type.name.capitalize(), _value=justification_type.id))

    create_justification = FORM(
        TABLE(
            TR(
                TD(LABEL(T('Description'))),
                TD(INPUT(_name='description', requires=IS_NOT_EMPTY()))
            ),
            TR(
                TD(LABEL(T('Document'))),
                TD(INPUT(_name='document', _type="file", _accept="application/pdf", requires=[
                    IS_NOT_EMPTY(), IS_LENGTH(2097152, 0, error_message='El documento debe poseer un tamaño desde 1KB hasta 2 MB.')
                ]))
            ),
            TR(
                TD('El tipo de documento ha seleccionar debe ser de tipo PDF y con un tamaño entre 1KB y 2MB.', _colspan=2)
            ),
            TR(
                TD(INPUT(_type='submit', _value=T('Send')))
            )
        )
    )

    if create_justification.accepts(request, session):
        tutor_id = auth.user.id
        project = db((db.user_project.period == period_id) & (db.user_project.assigned_user == loged_user_id)).select(db.user_project.id).first()

        if project == None:
            response.flash = T('You are not an academic tutor')
        else:
            if not can_create_justification(loged_user_id, period_id):
                session.flash = 'Error: Ustede excede la cantidad de justificaciónes permitida.'
                redirect(URL('dsi_student', 'absence_justifications'))

            status = db.executesql(queries.get_justification_status_id('justificado'))[0][0]
            db(db.dsi_justification.id == request.args[0]).update(
                description=request.vars.description,
                image=request.vars.document,
                resolution_status=status,
                requester_user=tutor_id,
                created_by=session.auth.user.username
            )
            session.flash = T('Request has been sent')
            redirect(URL('dsi_student', 'absence_justifications'))
    elif create_justification.errors:
        response.flash = T('form has errors')
    else:
        response.flash = T('please fill the form')

    return dict(create_justification=create_justification, back_button=back_button)

@auth.requires_login()
@auth.requires_membership('Student')
def notifications():
    period_id = cpfecys.current_year_period().id
    loged_user_id = auth.user.id

    justification_grid_query = (
        (db.dsi_notification.sender == db.auth_user.id) & (db.dsi_notification.period == period_id)
        & (db.dsi_notification.destination == loged_user_id)
    )

    justification_grid_fields = [
        db.dsi_notification.id,
        db.dsi_notification.created_at,
        db.dsi_notification.notification_message,
        db.auth_user.username
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
        paginate=20,
        details=False
    )

    return dict(justification_grid=justification_grid)

@auth.requires_login()
@auth.requires_membership('Student')
def schedule_assignation():
    assignation_schedule_table = ''
    period_id = cpfecys.current_year_period().id
    loged_user_id = auth.user.id

    tutor_informations = get_tutor_information(loged_user_id, period_id)
    selected_curse_id = request.vars.c
    if selected_curse_id is not None:
        for curso in tutor_informations:
            if int(curso[6]) == int(selected_curse_id):
                tutor_information = curso
                break
    else:
        try:
            tutor_information = tutor_informations[0]
            selected_curse_id = tutor_information[6]
        except IndexError:
            tutor_information = None
            selected_curse_id = None
    
    if tutor_information is not None:
        curse_select = get_curso_select(tutor_informations, selected_curse_id)
        tutor_information_table = FORM(
            TABLE(
                TR(
                    TH('Carnet'),
                    TD(tutor_information[0])
                ),
                TR(
                    TH('CUI'),
                    TD(tutor_information[1])
                ),
                TR(
                    TH('Nombre'),
                    TD(f'{tutor_information[2]} {tutor_information[3]}')
                ),
                TR(
                    TH('Curso'),
                    TD(curse_select)
                ),
                TR(
                    TD(INPUT(_value='Seleccionar', _type='submit', _class="btn btn-primary"))
                )
            ),
            _method='GET',
            _action=URL('dsi_student', 'schedule_assignation')
        )

        
        schedules = list()
        schedules.append(TR(
            TH('Hora Inicio'),
            TH('Hora Fin'),
            TH('Dia'),
            TH('Salon'),
            TH('Tipo')
        ))
        assignation_schedule = db.executesql(queries.get_tutor_schedule_by_period_id_and_tutor_id_and_assignation_id(period_id, loged_user_id, selected_curse_id))
        for schedule in assignation_schedule:
            schedules.append(TR(
                TD(schedule[1]),
                TD(schedule[2]),
                TD((schedule[4], "--")[schedule[4] is None]),
                TD(schedule[3]),
                TD(schedule[5])
            ))

        assignation_schedule_table = TABLE(schedules, _class="table table-striped table-bordered")
    else:
        tutor_information_table = ''
        assignation_schedule_table = ''

    # Asignacion de horarios
    assignation_form = FORM()
    select_assistance_type = FORM()
    if validate_schedule_parameter():
        select_assistance_type = FORM(
            H2('Asignación de horarios'),
            TABLE(
                TR(
                    TD(get_assistance_type_select()),
                    TD(INPUT(_type='submit', _value='Buscar', _class="btn btn-primary"))
                )
            )
        )

        if select_assistance_type.process(formname='select_schedule_type').accepted:
            assitance_type = request.vars.assistanceType
            horarios_disponibles = list()
            for day in db.executesql(queries.get_day_of_week()):
                query = None
                if int(assitance_type) == 2:
                    tutor_amount = db.executesql(queries.get_tutor_amount_restriction())[0][0]
                    query = queries.obtener_horarios_para_asignar(period_id, day[0], assitance_type, tutor_amount)
                else:
                    query = queries.obtener_horarios_para_asignar_laboratorio(period_id, day[0], assitance_type)

                horarios = list()
                available_schedules = db.executesql(query)
                if available_schedules:
                    horarios.append(TH(day[1]))
                    for available_schedule in available_schedules:
                        horarios.append(TD(
                            TABLE(
                                TR(
                                    TD(f"de: {available_schedule[2]} a: {available_schedule[3]}"),
                                    TD(INPUT(_name='horarios', _type='radio', _value=available_schedule[0]))
                                )
                            )
                        ))
                    horarios_disponibles.append(TR(horarios))

            assignation_form = FORM(
                INPUT(_type='hidden', _name='tipoAsistencia', _value=assitance_type),
                H2("Horarios de {} disponibles".format(db.executesql(queries.get_assistance_type(assitance_type))[0][1])),
                TABLE(horarios_disponibles, _class="table table-striped table-bordered"),
                INPUT(_type='submit', _value='Asignar', _class='btn btn-primary')
            )

        if assignation_form.process(formname='formulario_de_asignacion').accepted:
            assitance_type = int(request.vars.tipoAsistencia)
            horarios = request.vars.horarios
            if horarios is not None and len(horarios) > 1:
                mensaje = validate_assignation_schedule(period_id, loged_user_id, assitance_type, horarios, '', selected_curse_id)
                session.flash = mensaje
                redirect(URL('dsi_student', 'schedule_assignation', vars=dict(c=selected_curse_id)))
            else:
                session.flash = 'Debe seleccionar un horario para ser asignado'
                redirect(URL('dsi_student', 'schedule_assignation', vars=dict(c=selected_curse_id)))

    return dict(
        tutor_information_table=tutor_information_table,
        assignation_schedule_table=assignation_schedule_table,
        assignation_form=assignation_form,
        select_assistance_type=select_assistance_type
    )

@auth.requires_login()
@auth.requires_membership('Student')
def get_justification_button(row):
    button = ''

    if not row.dsi_justification.resolution_date:
        button = TR(
            TD(
                A(
                    BUTTON(
                        SPAN(_class="icon ok icon-ok glyphicon glyphicon-ok"),
                        SPAN('Justificar')
                    ),
                    _href=URL('dsi_student', 'creation_absence_justifications', args=[row.dsi_justification.id])
                )
            )
        )

    return  TABLE(button)

@auth.requires_login()
@auth.requires_membership('Student')
def can_create_justification(loged_user_id, period_id):
    parametros = db.executesql(queries.get_system_parameter_by_name(period_id, 'cantidad_justificaciones_tutores'))
    cantidad_justificaciones_tutores = parametros[0][2]
    cantidad_justificaciones = db.executesql(queries.get_quantity_justifications_by_tutor_and_period(loged_user_id, period_id))

    if len(cantidad_justificaciones) != 0 and cantidad_justificaciones[0][0] < cantidad_justificaciones_tutores:
        return True
    return False

def get_tutor_information(tutor_id, period_id):
    return db.executesql(queries.get_tutor_information(tutor_id, period_id))

def get_curso_select(tutor_informations, selected):
    type_options = list()
    for information in tutor_informations:
        if selected is not None and int(information[6]) == int(selected):
            type_options.append(OPTION(information[5].encode('utf-8'), _value=information[6], _selected='true'))
        else:
            type_options.append(OPTION(information[5].encode('utf-8'), _value=int(information[6])))

    return SELECT(type_options, _name='c', requires=IS_INT_IN_RANGE(1, None), _class="form-control")

def validate_schedule_parameter():
    schedule_parameters = db(db.dsi_schedule_parameter).select()

    until_date = None
    assignation_status = False
    for schedule_parameter in schedule_parameters:
        if schedule_parameter.name == 'asignationUntilDate':
            until_date = schedule_parameter.until_date
        if schedule_parameter.name == 'asignationStatus':
            assignation_status = schedule_parameter.asignation_status

    now = datetime.datetime.now()
    if until_date is not None and until_date and now < until_date:
        if assignation_status == 1:
            return True
    return False

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

def validate_assignation_schedule(period_id, tutor_id, type_id, schedule_id, class_room, asignacion_id):
    dsi_type = 2
    ENABLED = 1

    project = get_user_project(tutor_id, period_id, asignacion_id)
    horario = get_selected_schedule(schedule_id)
    horarios_por_periodo = get_period_schedules(tutor_id, period_id, type_id, ENABLED, asignacion_id)
    horario_mismo_dia = get_same_day_schedule(tutor_id, period_id, horario, ENABLED)

    if horario_mismo_dia:
        return 'Error, usted ya posee un horario el día seleccionado'

    horario_compatible = validate_schedule_with_course_schedule(tutor_id, horario.week_day, period_id, horario.starting_hour)
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

def get_user_project(tutor_id, period_id, asignacion_id):
    return db((db.user_project.assigned_user == tutor_id) & (db.user_project.period == period_id)
            & (db.user_project.id == asignacion_id)).select(db.user_project.project).first()

def get_selected_schedule(schedule_id):
    return db(db.dsi_schedule.id == schedule_id).select(db.dsi_schedule.week_day, db.dsi_schedule.id, db.dsi_schedule.starting_hour, db.dsi_schedule.assistance_type_id).first()

def get_period_schedules(tutor_id, period_id, type_id, ENABLED, asignacion_id):
    return db((db.dsi_assignation_schedule.schedule_id == db.dsi_schedule.id) & (db.dsi_assignation_schedule.tutor_id == tutor_id)
        & (db.dsi_assignation_schedule.isEnabled == ENABLED) & (db.dsi_assignation_schedule.project_assignation == asignacion_id)
        & (db.dsi_schedule.period == period_id) & (db.dsi_schedule.assistance_type_id == type_id)).select().as_list()

def get_same_day_schedule(tutor_id, period_id, horario, ENABLED):
    return db((db.dsi_assignation_schedule.schedule_id == db.dsi_schedule.id) & (db.dsi_assignation_schedule.tutor_id == tutor_id)
        & (db.dsi_assignation_schedule.isEnabled == ENABLED) & (db.dsi_schedule.period == period_id)
        & (db.dsi_schedule.week_day == horario.week_day)).select().as_list()

def validate_schedule_with_course_schedule(tutor_id, day_id, period_id, hora_inicio):
    schedules = db.executesql(queries.get_course_schedule_by_tutor_id_and_day_id(tutor_id, day_id, period_id))
    resultado = True

    for schedule in schedules:
        if schedule[0] <= hora_inicio <= schedule[1]:
            resultado = False

    return resultado

def validate_tutors_amount_in_schedule(schedule_id):
    limite_cantidad_tutores = db(db.dsi_schedule_parameter.name == 'tutorAmount').select().first()
    limite_cantidad_tutores = limite_cantidad_tutores.tutor_amount

    cantidad_tutores_en_horario = db.executesql(queries.get_tutor_quantity_by_schedule_id(schedule_id))

    cantidad_tutores_en_horario_numero = 0
    if cantidad_tutores_en_horario:
        cantidad_tutores_en_horario_numero = cantidad_tutores_en_horario[0][1]

    if limite_cantidad_tutores < cantidad_tutores_en_horario_numero:
        return False
    return True

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
