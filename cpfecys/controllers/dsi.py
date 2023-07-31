# coding: utf8
import calendar
import datetime

import dsi_queries as queries

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def absence_justifications_admin():
    period_id = cpfecys.current_year_period().id
    if request.vars.periodo:
        periodo_seleccionado = request.vars.periodo
        periodo = db(db.period_year.id == periodo_seleccionado).select(db.period_year.id).first()
        if periodo:
            period_id = periodo.id

    form_select_period = FORM(
        TABLE(
            TR(
                TD(get_period_form_select(period_id)),
                TD(INPUT(_type='submit', _value='Buscar', _class="btn btn-primary"))
            )
        ),
        _method='get'
    )

    justification_grid_query = (
        (db.dsi_justification.period == period_id) & (db.dsi_justification.schedule_asignation_id == db.dsi_assignation_schedule.id)
        & (db.dsi_assignation_schedule.schedule_id == db.dsi_schedule.id) & (db.dsi_schedule.assistance_type_id == db.dsi_assistance_type.id)
        & (db.dsi_justification.resolution_status == db.dsi_justification_status.id) & ((db.dsi_justification_status.name == 'justificado')
        | (db.dsi_justification_status.name == 'justificado_dsi')) & (db.dsi_justification.project == db.user_project.id)
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
        db.dsi_justification.resolution_date,
        db.dsi_justification.resolution_description,
        db.dsi_justification.resolver_user
    ]


    links = [dict(header='Funciones', body=lambda row: approve_or_reject_justification(row))]

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
        paginate=75,
        details=False,
        links=links
    )

    return dict(justification_grid=justification_grid, form_select_period=form_select_period)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def assignation_report_admin():
    periodo_actual = cpfecys.current_year_period()
    period_id = periodo_actual.id

    periodo_seleccionado = request.vars.periodo or period_id
    periodo = db(db.period_year.id == periodo_seleccionado).select(db.period_year.period, db.period_year.yearp, db.period_year.id).first()
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

    form_select_period = FORM(
        TABLE(
            TR(
                TD(get_period_form_select()),
                TD(INPUT(_type='submit', _value='Buscar', _class="btn btn-primary"))
            )
        ),
        _method='get'
    )

    return dict(assignation_grid=assignation_grid, form_select_period=form_select_period, title=title)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def assistance_parameters_admin():
    period_id = cpfecys.current_year_period().id

    button_create = A(
        BUTTON(
            SPAN(_class="icon plus icon-plus glyphicon glyphicon-plus"),
            f" {T('Create')}",
            _class="btn btn-primary"
        ),
        _href=URL('dsi', 'create_assistance_parameters_admin')
    )

    assistance_parameters_form = FORM(TABLE(
        TR(
            TD('Tipo de asistencia'),
            TD(get_assistance_type_select())
        ),
        TR(
            TD(INPUT(_type='submit', _value=T('Search'), _class="btn btn-success"))
        )
    ))

    parameters_type_table = ''
    if (assistance_parameters_form.accepts(request, session)):
        parameters_by_type = db.executesql(queries.get_assistance_parameters_by_type_id_and_period(request.vars.assistanceType, 15))
        parameters = list()
        parameters.append(TR(
            TH('Nombre'),
            TH('Mensaje'),
            TH('Porcentaje'),
            TH('Inicio'),
            TH('Fin'),
            TH('Tipo'),
            TH('Clase'),
            TH('Imagen'),
            TH('Acciones', _colspan=2)
        ))

        for parameter in parameters_by_type:
            parameters.append(TR(
                TD(parameter[1]),
                TD(parameter[2]),
                TD(parameter[3]),
                TD(parameter[4]),
                TD(parameter[5]),
                TD(parameter[8]),
                TD(parameter[9]),
                TD(parameter[10] or '--'),
                TD(
                    A(
                        BUTTON(
                            SPAN(_class="icon pen icon-pencil glyphicon glyphicon-arrow-pencil"),
                            T('Edit')
                        ),
                        _href=URL('dsi', 'update_assistance_parameters_admin', args=parameter[0])
                        )
                ),
                TD(
                    A(
                        BUTTON(
                            SPAN(_class="icon trash icon-trash glyphicon glyphicon-trash"),
                            T('Delete')
                        ),
                        _href=URL('dsi', 'delete_assistance_parameters_admin', args=parameter[0])
                    )
                )
            ))

        parameters_type_table = TABLE(parameters, _class="table table-striped table-bordered")

    return dict(
        assistance_parameters_form=assistance_parameters_form,
        button_create=button_create,
        parameters_type_table=parameters_type_table
    )

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def assistance_report_admin():
    period_id = cpfecys.current_year_period().id
    if request.vars.periodo:
        periodo_seleccionado = request.vars.periodo
        periodo = db(db.period_year.id == periodo_seleccionado).select(db.period_year.id).first()
        if periodo:
            period_id = periodo.id

    form_select_period = FORM(
        TABLE(
            TR(
                TD(get_period_form_select(period_id)),
                TD(INPUT(_type='submit', _value='Buscar', _class="btn btn-primary"))
            )
        ),
        _method='get'
    )

    justification_grid_query = (
        (db.dsi_assistance.tutor == db.auth_user.id) & (db.dsi_assistance.period == period_id)
        & (db.dsi_assistance_type.id == db.dsi_assistance.assistance_type)
    )

    justification_grid_fields = [
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
        details=False,
        orderby=~db.dsi_assistance.starting_hour
    )

    return dict(justification_grid=justification_grid, form_select_period=form_select_period)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def assistance_report_now():
    now = datetime.datetime.now()
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)

    hoy = datetime.datetime.combine(now, datetime.datetime.min.time())
    manana = datetime.datetime.combine(tomorrow, datetime.datetime.min.time())

    periodo_actual = cpfecys.current_year_period()
    period_id = periodo_actual.id

    justification_grid_query = (
        (db.dsi_assistance.tutor == db.auth_user.id) & (db.dsi_assistance.period == period_id)
        & (db.dsi_assistance_type.id == db.dsi_assistance.assistance_type) & (db.dsi_assistance.starting_hour > hoy)
        & (db.dsi_assistance.starting_hour < manana)
    )

    justification_grid_fields = [
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
        details=False,
        orderby=~db.dsi_assistance.starting_hour
    )

    return dict(justification_grid=justification_grid)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def calculate_note():
    period_id = cpfecys.current_year_period().id
    assistance_percentage_parameter = db.executesql(queries.get_system_parameter_by_name(period_id, 'porcentajeAsistencia'))

    try:
        assistance_percentage = float(assistance_percentage_parameter[0][2])/100.00
    except IndexError:
        assistance_percentage = 0.00
    print(assistance_percentage)

    asignaciones = db.executesql(queries.get_asignaciones_por_periodo(period_id))

    inicio_periodo = None
    try:
        inicio_periodo = db.executesql(queries.get_inicio_periodo(period_id))[0][0]
    except IndexError:
        inicio_periodo = datetime.datetime.now()
    
    fin_periodo = None
    try:
        fin_periodo = db.executesql(queries.get_fin_periodo(period_id))[0][0]
    except IndexError:
        fin_periodo = datetime.datetime.now()

    now = datetime.datetime.now()
    hoy = datetime.datetime.combine(now, datetime.datetime.max.time())
    inicio_periodo = datetime.datetime.combine(inicio_periodo, datetime.datetime.min.time())
    fin_periodo = datetime.datetime.combine(fin_periodo, datetime.datetime.max.time())

    fecha_limite = hoy
    if(hoy > fin_periodo):
        fecha_limite = fin_periodo

    horarios_a_cumplir = dict({
        1: get_dates(inicio_periodo, fecha_limite, [0]),
        2: get_dates(inicio_periodo, fecha_limite, [1]),
        3: get_dates(inicio_periodo, fecha_limite, [2]),
        4: get_dates(inicio_periodo, fecha_limite, [3]),
        5: get_dates(inicio_periodo, fecha_limite, [4]),
        6: get_dates(inicio_periodo, fecha_limite, [5]),
        7: get_dates(inicio_periodo, fecha_limite, [6])
    })

    for asignacion in asignaciones:
        print ('************** Asignacion {}***********************'.format(asignacion[0]))
        nota_final = 0
        horarios = db.executesql(queries.get_schedules_by_asignacion_id(period_id, asignacion[0], 1))
        print ('******** horarios habilitados {}**************'.format(len(horarios)))
        nota = 0
        cantidad = 0
        for horario in horarios:
            dia_horario = horario[0]
            dates = horarios_a_cumplir[dia_horario]

            print ('/*/*/*/*/*/*')
            print (dates)
            print ('/*/*/*/*/*/*')

            if horario[3] == 1:
                cantidad += len(dates)
            for fecha in dates:
                asistencias = db.executesql(queries.get_assistances_by_asignacion(period_id, asignacion[0], fecha))
                print ('**********  {} *******************'.format(fecha))
                print (queries.get_assistances_by_asignacion(period_id, asignacion[0], fecha))
                print (asistencias)
                print ('*****************************')
                if asistencias:
                    for asistencia in asistencias:
                        if asistencia[3] and int(asistencia[3]) > 0:
                            print ("debe sumar {} de {}".format(fecha, asignacion[0]))
                            nota += asistencia[5]
                        else:
                            print ('justifico omision {} de {}'.format(fecha, asignacion[0]))
                            crear_justificacion(asignacion[1], period_id, fecha, 2, 4, asignacion[0], 'No marco fin del periodo en la fecha {}'.format(fecha), asistencia[6], horario[4])
                            enviar_notificacion('Justificación creada', 1, asignacion[1], period_id, 'No marco fin del periodo en la fecha {}'.format(fecha))
                else:
                    print ('justifico falta {} de {}'.format(fecha, asignacion[0]))
                    crear_justificacion(asignacion[1], period_id, fecha, 1, 4, asignacion[0], 'No asistio en la fecha {}'.format(fecha), None, horario[4])
                    enviar_notificacion('Justificación creada', 1, asignacion[1], period_id, 'No asistio en la fecha {}'.format(fecha))

        horarios_eliminados = db.executesql(queries.get_schedules_by_asignacion_id(period_id, asignacion[0], 0))

        print( '/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*')
        print (horarios_eliminados)
        for eliminado in horarios_eliminados:
            print ('up = {} ds.id = {} tutor = {}'.format(asignacion[0], eliminado[5], eliminado[2]))
            notas_faltantes = db.executesql(queries.get_asistencia_by_schedule_id(eliminado[2], eliminado[5], asignacion[0]))
            for notas in notas_faltantes:
                nota += int(notas)
            nota_redonda = cantidad * 100
            if nota_redonda < nota:
                nota = nota_redonda
        print( '/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*')

        if(cantidad > 0):
            print( '(nota = {} / cantidad = {} ) * porcentaje = {}'.format(nota, cantidad, assistance_percentage))
            nota_final = (nota / cantidad) * assistance_percentage
        print( '===================================Asignacion**************************')
        print ('tutor = {} curso = {} cantidad = {} nota = {} nota final = {}'.format(asignacion[1],asignacion[0], cantidad, nota, round(nota_final)))
        set_nota_in_asignacion(asignacion[0], period_id, round(nota_final), cantidad, nota)

    return dict(title='')

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def change_justification_status():
    title = f'La justificación con número de identificación: {request.args[1]} sera {request.args[0].capitalize()}'

    before = request.env.http_referer.split('/')
    before = before[len(before) - 1]
    
    back_button = A(
        I(_class="fa fa-arrow-left", _aria_hiden='true'),
        f" {T('Back')}",
        _class='btn btn-primary',
        _href=URL('dsi', before)
    )

    change_justification_status = FORM(
        TABLE(
            TR(
                TD(
                    H5(T('Reason')),
                    INPUT(_name='reason', requires=IS_NOT_EMPTY(), _class='form-control', _id='change-justification-status-input')
                ),
            ),
            BR(),
            TR(
                TD(INPUT(_type='submit', _value=T('Send'), _class='btn btn-secondary'))
            )
            
        )
    )

    if (change_justification_status.accepts(request, session)):
        status = request.args[0]
        justificacion_id = request.args[1]

        period_id = cpfecys.current_year_period().id
        loged_user = auth.user
        status = db(db.dsi_justification_status.name == status).select(db.dsi_justification_status.id).first()

        justification_query = db(db.dsi_justification.id == justificacion_id)
        justificacion = justification_query.select(db.dsi_justification.resolution_status, db.dsi_justification.absence_date, db.dsi_justification.schedule_asignation_id,
                                            db.dsi_justification.id_asistencia, db.dsi_justification.requester_user, db.dsi_justification.id, db.dsi_justification.project).first()
        if request.args[0] == 'aprobado':
            aprobar_justificacion(justificacion, period_id)
            session.flash = 'Justificacion aprobada'
        else:
            session.flash = 'Justificacion rechazada'

        justification_query.update(
            resolution_status=status.id,
            resolution_description=request.vars.reason,
            resolver_user=loged_user.id,
            resolution_date=datetime.datetime.now()
        )

        if justificacion.resolution_status.name == 'aprobado' or justificacion.resolution_status.name == 'rechazado':
            redirect(URL('dsi', 'resolutions_admin'))
        elif justificacion.resolution_status.name == 'justificado' or justificacion.resolution_status.name == 'justificado_dsi':
            redirect(URL('dsi', 'absence_justifications_admin'))
        else:
            redirect(URL('dsi', 'omissions_admin'))
    elif change_justification_status.errors:
        session.flash = T('form has errors')
    else:
        session.flash = T('please fill the form')
    return dict(change_justification_status=change_justification_status, title=title, back_button=back_button)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def create_assistance_parameters_admin():
    period_id = cpfecys.current_year_period().id

    back_button = A(
        I(_class="fa fa-arrow-left", _aria_hiden='true'),
        f" {T('Back')}",
        _class='btn btn-primary',
        _href=URL('dsi', 'assistance_parameters_admin')
    )

    type_select = get_assistance_type_select()
    class_select = get_assistance_class_select()

    create_form = FORM(
        DIV(
            LABEL('Nombre'),
            INPUT(_type='text', _name='name', _class='form-control'),
            _class='form-group row'
        ),
        DIV(
            LABEL('Mensaje'),
            INPUT(_type='text', _name='message', _class='form-control'),
            _class='form-group row'
        ),
        DIV(
            LABEL('Porcentaje'),
            INPUT(_type='number', _name='percentage', _class='form-control'),
            _class='form-group row'
        ),
        DIV(
            LABEL('Inicio'),
            INPUT(_type='number', _name='start', _class='form-control'),
            _class='form-group row'
        ),
        DIV(
            LABEL('Fin'),
            INPUT(_type='number', _name='finish', _class='form-control'),
            _class='form-group row'
        ),
        DIV(
            LABEL('Imagen'),
            INPUT(_type='text', _name='image', _class='form-control'),
            _class='form-group row'
        ),
        DIV(
            LABEL('Tipo'),
            type_select,
            _class='form-group row'
        ),
        DIV(
            LABEL('Clase'),
            class_select,
            _class='form-group row'
        ),
        DIV(
            INPUT(_value=T('Save'), _type='submit', _class='btn btn-success'),
            _class='form-group row'
        )
    )

    if (create_form.accepts(request, session)):
        db.dsi_assistance_parameter.insert(
            name=request.vars.name,
            parameter_message=request.vars.message,
            percentage=request.vars.percentage,
            range_start=request.vars.start,
            range_finish=request.vars.finish,
            period=period_id,
            image=request.vars.image,
            assistance_class=request.vars.assistanceClass,
            assistance_type=request.vars.assistanceType,
            created_at=datetime.datetime.now(),
            created_by=session.auth.user.username,
            updated_at=datetime.datetime.now(),
            updated_by=session.auth.user.username
        )
        session.flash = T('Request has been sent')
        redirect(URL('dsi', 'assistance_parameters_admin'))

    return dict(create_form=create_form, back_button=back_button)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def create_exception_courses_admin():
    back_button = A(
        I(_class="fa fa-arrow-left", _aria_hiden='true'),
        f" {T('Back')}",
        _class='btn btn-primary',
        _href=URL('dsi', 'exception_courses_admin')
    )

    form = FORM(
        TABLE(
            TR(
                TH('Curso'),
                TD(get_project_select())
            ),
            TR(
                TH('Solo una hora'),
                TD(INPUT(_name='singleHour', _type='checkbox'))
            ),
            TR(
                TH('Horario Vespertino'),
                TD(INPUT(_name='evening', _type='checkbox'))
            ),
            BR(),
            TR(INPUT(_type='submit', _value='Guardar', _class="btn btn-primary"))
        )
    )

    if form.accepts(request, session):
        fields = request.vars
        period = cpfecys.current_year_period()

        exception_course = db.executesql(queries.get_exception_course(fields.project, period.id))

        if not exception_course:
            db.dsi_exception_course.insert(
                project=fields.project,
                single_hour=(1, 0)[fields.singleHour is None],
                evening=(1, 0)[fields.evening is None],
                created_at=datetime.datetime.now(),
                period=period.id,
                created_by=auth.user.username
            )
            session.flash = 'Almacenada la configuración de excepción'
            redirect(URL('dsi', 'exception_courses_admin'))
        session.flash = 'Error excepción ya asignada para el curso seleccionado'
        redirect(URL('dsi', 'exception_courses_admin'))

    return dict(back_button=back_button, form=form)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def create_holidays_admin():
    back_button = A(
        I(_class="fa fa-arrow-left", _aria_hiden='true'),
        f" {T('Back')}",
        _class='btn btn-primary',
        _href=URL('dsi', 'holidays_admin')
    )

    form = FORM(
        DIV(
            LABEL('Nombre de día libre'),
            INPUT(_type='text', _name='name', _class='form-control'),
            _class='form-group row'
        ),
        DIV(
            LABEL('Fecha de día libre'),
            INPUT(_type='date', _name='holiday', _class='form-control'),
            _class='form-group row'
        ),
        DIV(
            INPUT(_type='submit', _value='Guardar', _class='btn btn-success'),
            _class='form-group row'
        )
    )

    if form.accepts(request, session):
        if request.vars.name != "" and request.vars.holiday != "":
            db.dsi_holiday.insert(
                name=request.vars.name,
                enabled=1,
                holiday_date=request.vars.holiday,
                created_at=datetime.datetime.now(),
                created_by=auth.user.username
            )
            session.flash = 'Día de asueto almacenado.'
            redirect(URL('dsi', 'create_holidays_admin'))
        else:
            session.flash = 'Rellene todos los campos para realizar esta acción'
            redirect(URL('dsi', 'create_holidays_admin'))


    return dict(form=form, back_button=back_button)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def create_schedule_assignation_admin():
    period_id = cpfecys.current_year_period().id

    schedule_options = ''

    day_of_week_select = get_day_of_week_select()
    assistance_type_select = get_assistance_type_select()

    if not request.args:
        tutor_select = get_tutor_form_select(period_id)
    else:
        tutor_select = get_tutor_form_select(period_id, request.args[0])

    back_button = A(
        I(_class="fa fa-arrow-left", _aria_hiden='true'),
        f" {T('Back')}",
        _class='btn btn-primary',
        _href=URL('dsi', 'schedule_assignation_admin')
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
                INPUT(_value=T('Search'), _type='submit', _class="btn btn-success")
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
                schedule_options.append(TR(
                    TD(schedule[2]),
                    TD(schedule[3]),
                    TD(INPUT(_type='radio', _value=schedule[0], _name='schedule'))
                ))
        else:
            schedule_options = TR(TD('Sin horarios disponibles', _colspan=2))

        dia = db.executesql(queries.get_day_of_week_by_id(request.vars.dayOfWeek))
        dia = dia[0]

        tipo = db.executesql(queries.get_day_of_week_by_id(request.vars.assistanceType))
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
                TD(INPUT(_type='text', _name='classroom', _class="form-control"))
            ),
            TR(
                INPUT(_type="hidden", _value=tutor_id, _name="tutorId")
            )
        ),
        TABLE(schedule_options, _class="table table-striped table-bordered"),
        TD(INPUT(_type='submit', _value='Guardar', _class="btn btn-primary"))
    )

    if form_create_schedule.process(formname='form_create_schedule').accepted:
        if request.vars.schedule is not None:
            session.flash = validate_assignation_schedule(period_id, request.vars.tutorId, request.vars.scheduleType, request.vars.schedule, request.vars.classroom, request.vars.c)
        else: 
            session.flash = 'No existen horarios para ser asignados'
        redirect(URL('dsi', 'create_schedule_assignation_admin'))

    return dict(form_create_schedule=form_create_schedule, back_button=back_button, form_search_schedule=form_search_schedule)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def exception_courses_admin():
    create_exception_button = A(
        BUTTON(
            SPAN(_class="icon plus icon-plus glyphicon glyphicon-plus"), T('Create'), _class="btn btn-primary"
        ),
        _href=URL('dsi', 'create_exception_courses_admin')
    )
    
    period = cpfecys.current_year_period()
    exception_courses = db.executesql(queries.get_exception_courses(period.id))

    table_content = list()
    table_content.append(TR(
        TH('Proyecto'),
        TH('Un horario'),
        TH('Vespertina'),
        TH('Acciones')
    ))

    if exception_courses:
        for exception_course in exception_courses:
            table_content.append(
                TR(
                    TD(f"{exception_course[6]} - {exception_course[5].strip()}"),
                    TD(("No", "Si")[exception_course[3] == 1]),
                    TD(("No", "Si")[exception_course[4] == 1]),
                    TD(
                        A(
                            BUTTON(
                                SPAN(_class="icon trash icon-trash glyphicon glyphicon-trash"),
                                T('Delete')
                            ),
                            _href=URL('dsi', 'delete_exception_courses_admin', args=exception_course[0])
                        )
                    )
                )
            )

    exception_table = TABLE(table_content, _class="table table-striped table-bordered")

    return dict(create_exception_button=create_exception_button, exception_table=exception_table)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def fingerprint_parameters_admin():
    enable_registration = db.executesql(queries.get_fingerprint_parameter('registration'))
    enable_registration = enable_registration[0]

    is_checked = (False, True)[enable_registration[2] == 1]

    configuration_form = FORM(
        TABLE(
            TR(
                TH('Habilitar registro de huella'),
                TD(INPUT(_name='enableRegistration', _type='checkbox', _checked=is_checked))
            ),
            TR(
                TH('Limpiar base de datos de huellas'),
                TD(INPUT(_name='cleanDBFingerprint', _type='checkbox'))
            ),
            TR(
                TD(INPUT(_value='Guardar', _type='submit', _class="btn btn-primary form-control"))
            )
        )
    )

    if (configuration_form.accepts(request, session)):
        db(db.dsi_fingerprint_parameter.name == 'registration').update(
            parameter_enable=(0, 1)[request.vars.enableRegistration == 'on'],
            updated_at=datetime.datetime.now()
        )
        session.flash = 'Parametros almacenados'

        if (request.vars.cleanDBFingerprint == 'on'):
            db.executesql('delete from dsi_fingerprint;')
            session.flash = 'Los registros de huellas eliminados'

        redirect(URL('dsi', 'fingerprint_parameters_admin'))

    return dict(configuration_form=configuration_form)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def fingerprint_report_admin():
    fingerprint_grid_query = ((db.dsi_fingerprint.tutor_id == db.auth_user.id))

    fingerprint_grid_fields = [
        db.dsi_fingerprint.tutor_id,
        db.auth_user.username,
        db.auth_user.first_name,
        db.auth_user.last_name,
        db.dsi_fingerprint.created_at
    ]

    links = [dict(header='Funciones', body=lambda row: remove_finger_print(row))]

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
        paginate=20,
        details=False,
        links=links
    )

    return dict(fingerprint_grid=fingerprint_grid)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def holidays_admin():
    justification_grid_query = (db.dsi_holiday.enabled == True)

    create_button = A(
        BUTTON(SPAN(_class="icon plus icon-plus glyphicon glyphicon-plus"), 'Crear', _class="btn btn-primary"),
        _href=URL('dsi', 'create_holidays_admin')
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
        deletable=True,
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
def index():
    period = cpfecys.current_year_period()
    restrictions = db((db.item_restriction.item_type == db.item_type(name='Activity')) & ((db.item_restriction.period == period.id)
                | ((db.item_restriction.permanent == True) & (db.item_restriction.period <= period.id)))
                & (db.item_restriction.is_enabled == True)).select(db.item_restriction.name, db.item_restriction.id) | db((db.item_restriction.item_type == db.item_type(name='Grade Activity')) 
                & ((db.item_restriction.period == period.id) | ((db.item_restriction.permanent == True) 
                & (db.item_restriction.period <= period.id))) & (db.item_restriction.is_enabled == True)).select(db.item_restriction.name, db.item_restriction.id)

    return dict(restrictions=restrictions)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def iniciar_semestre():
    form_iniciar = FORM(
        TABLE(
            TR(
                TH("Si esta seguro de iniciar un nuevo semestre escriba 'si'.")
            ),
            TR(
                TD(INPUT(_name='respuesta', _type='text', _class="form-control"))
            ),
            TR(
                INPUT(_value=T('Proceder'), _type='submit', _class="btn btn-primary")
            )
        )
    )

    if form_iniciar.process(formname='form_iniciar').accepted:
        if(request.vars.respuesta.lower() == 'si'):
            periodo_actual = cpfecys.current_year_period()
            period_id = periodo_actual.id
            counter = 0

            #verifico primero si ya se crearon las variables
            if db(db.dsi_system_parameters.period == period_id).count() == 0:
                db.executesql(queries.copy_system_parameters(period_id))
                counter += 1

            if db(db.dsi_assistance_parameter.period == period_id).count() == 0:
                db.executesql(queries.copy_assistance_parameters(period_id))
                counter += 1

            if db(db.dsi_schedule.period == period_id).count() == 0:  
                db.executesql(queries.copy_laboratory_schedule(period_id))
                counter += 1

            if db(db.dsi_schedule_course.period == period_id).count() == 0:    
                db.executesql(queries.copy_course_schedule(period_id))
                counter += 1

            if counter > 0:
              session.flash = 'Semestre iniciado correctamente'
            else:
              session.flash = 'Error: el semestre que esta tratando de inicializar, ya ha sido inicializado anteriormente'
            redirect(request.env.http_referer)
        else:
            session.flash = 'Palabra clave incorrecta'
            redirect(request.env.http_referer)
    return dict(formulario=form_iniciar)


@auth.requires_login()
@auth.requires_membership('DSI')
def item_detail():
    period = cpfecys.current_year_period()
    if request.vars['period'] != None:
        period = request.vars['period']
        period = db.period_year(db.period_year.id == period)
    
    admin_role = db((db.auth_user.id == auth.user.id) & (db.auth_membership.user_id == db.auth_user.id)
                & (db.auth_membership.group_id == db.auth_group.id) & (db.auth_group.role == 'Super-Administrator'))
    
    admin = admin_role.count() != 0
    periods = False
    if admin:
        periods = db(db.period_year).select()

    if request.args(0) == 'update':
        valid = False
        done = request.vars['done'] or False
        user = request.vars['user']
        project = request.vars['project']
        restriction = request.vars['restriction']
        done_activity = (done == 'on' or False)
        restriction = db(db.item_restriction.id == restriction).select(db.item_restriction.id, db.item_restriction.item_type,
                                                                       db.item_restriction.min_score).first()

        score = 0
        try:
            score = int(request.vars['score'])
        except ValueError:
            session.flash = 'El valor debe ser un número entero'
            redirect(URL('dsi', 'item_detail', vars=dict(restriction=restriction.id)))

        if restriction.item_type.name == 'Grade Activity':
            valid = not (score and user and restriction)
        else:
            valid = not (user and restriction)

        if valid:
            session.flash = T('Not permited action.')
            redirect(URL('dsi', 'index'))

        # Validate if current user assignation is active
        assignations = db((db.auth_user.id == db.user_project.assigned_user) & (db.auth_user.id == db.auth_membership.user_id)
                    & (db.auth_user.id == user) & (db.auth_membership.group_id == db.auth_group.id)
                    & (db.auth_group.role == 'Student') & (db.user_project.project == project)
                    & (db.user_project.period == db.period_year.id) & ((db.user_project.period <= period.id)
                    & ((db.user_project.period.cast('integer') + db.user_project.periods) > period.id)))

        if assignations.count() != 1:
            session.flash = T('Not permited action.')
            redirect(URL('dsi', 'index'))

        assignation = assignations.select(db.user_project.ALL).first()
        item = db((db.item.created == period.id) & (db.item.item_restriction == restriction.id)
            & (db.item.item_restriction == db.item_restriction.id) & (db.item_restriction.is_enabled == True)
            & (db.item.assignation == assignation.id)).select(db.item.ALL).first()

        if item == None:
            cdate = datetime.datetime.now()
            db.item.insert(
                is_active=True,
                done_activity=done_activity,
                created=period.id,
                item_restriction=restriction.id,
                assignation=assignation.id,
                score=score,
                min_score=restriction.min_score
            )
        else:
            item.update_record(
                is_active=True,
                done_activity=done_activity,
                created=period.id,
                item_restriction=restriction.id,
                assignation=assignation.id,
                score=score,
                min_score=restriction.min_score
            )

        redirect(URL('dsi', 'item_detail', vars=dict(restriction=restriction.id)))

    restriction = request.vars['restriction']
    valid = restriction is not None and restriction != ''
    if not valid:
        session.flash = T('Not valid item list select a valid item list.')
        redirect(URL('dsi', 'index'))
    
    restrictions = db((db.item_restriction.item_type == db.item_type(name='Activity')) & (db.item_restriction.period == period.id)
                & (db.item_restriction.id == restriction) 
                & (db.item_restriction.is_enabled == True)).select(db.item_restriction.id, db.item_restriction.name,
                db.item_restriction.item_type, db.item_restriction.min_score) | db((db.item_restriction.item_type == db.item_type(name='Grade Activity'))
                & (db.item_restriction.period == period.id) & (db.item_restriction.id == restriction)
                & (db.item_restriction.is_enabled == True)).select(db.item_restriction.id, db.item_restriction.name,
                db.item_restriction.item_type, db.item_restriction.min_score) | db((db.item_restriction.item_type == db.item_type(name='Activity'))
                & (db.item_restriction.id == restriction) & (db.item_restriction.is_enabled == True)
                & (db.item_restriction.permanent == True)).select(db.item_restriction.id, db.item_restriction.name,
                db.item_restriction.item_type, db.item_restriction.min_score) | db((db.item_restriction.item_type == db.item_type(name='Grade Activity'))
                & (db.item_restriction.id == restriction) & (db.item_restriction.is_enabled == True)
                & (db.item_restriction.permanent == True)).select(db.item_restriction.id, db.item_restriction.name, db.item_restriction.item_type, 
                db.item_restriction.min_score)

    def get_areas(restriction):
        return db((db.item_restriction_area.item_restriction == restriction.id) & (db.area_level.id == db.item_restriction_area.area_level))

    def get_projects(area, restriction):
        return db((db.project.area_level == db.area_level.id) & (db.area_level.id == area.id)
            & (db.item_restriction.id == restriction.id) & (db.item_restriction_area.area_level == area.id)
            & (db.item_restriction_area.item_restriction == restriction.id) & (db.item_restriction_area.item_restriction == db.item_restriction.id)
            & (db.item_restriction_area.area_level == db.area_level.id) & (db.item_restriction_area.is_enabled == True))

    def is_exception(project, restriction):
        exception = db((db.item_restriction_exception.project == project.id) & (db.item_restriction_exception.item_restriction == restriction.id))
        return exception.count() != 0

    def get_students(project):
        return db((db.auth_user.id == db.user_project.assigned_user) & (db.auth_user.id == db.auth_membership.user_id)
            & (db.auth_membership.group_id == db.auth_group.id) & (db.auth_group.role == 'Student')
            & (db.user_project.project == project.id) & (db.user_project.period == db.period_year.id)
            & ((db.user_project.period <= period.id) & ((db.user_project.period.cast('integer') + db.user_project.periods) > period.id))).select(db.user_project.ALL)

    def get_item(restriction, assignation):
        return db((db.item.assignation == assignation.id) & (db.item.item_restriction == restriction.id)
            & (db.item.item_restriction == db.item_restriction.id) & (db.item_restriction.is_enabled == True)
            & (db.item.is_active == True) & (db.item.created == period.id)).select(db.item.ALL).first()

    return dict(
        restrictions=restrictions,
        get_areas=get_areas,
        get_projects=get_projects,
        is_exception=is_exception,
        get_students=get_students,
        get_item=get_item,
        admin=admin,
        periods=periods,
        period=period
    )


@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def omissions_admin():
    period_id = cpfecys.current_year_period().id
    if request.vars.periodo:
        periodo_seleccionado = request.vars.periodo
        periodo = db(db.period_year.id == periodo_seleccionado).select(db.period_year.id).first()
        if periodo:
            period_id = periodo.id

    form_select_period = FORM(
        TABLE(
            TR(
                TD(get_period_form_select(period_id)),
                TD(INPUT(_type='submit', _value='Buscar', _class="btn btn-primary"))
            )
        ),
        _method='get'
    )

    justification_grid_query = (
        (db.dsi_justification.period == period_id) & (db.dsi_justification.schedule_asignation_id == db.dsi_assignation_schedule.id)
        & (db.dsi_assignation_schedule.schedule_id == db.dsi_schedule.id) & (db.dsi_schedule.assistance_type_id == db.dsi_assistance_type.id)
        & (db.dsi_justification.resolution_status == db.dsi_justification_status.id) & (db.dsi_justification_status.name == 'pendiente')
        & (db.dsi_justification.project == db.user_project.id) & (db.user_project.project == db.project.id)
        & (db.user_project.assigned_user == db.auth_user.id) & (db.dsi_justification.justification_type == db.dsi_justification_type.id)
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
        db.dsi_justification.resolution_date,
        db.dsi_justification.resolution_description,
        db.dsi_justification.resolver_user
    ]

    links = [dict(header='Funciones', body=lambda row: approve_or_reject_justification(row))]

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
        paginate=75,
        details=False,
        links=links
    )

    return dict(justification_grid=justification_grid, form_select_period=form_select_period)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def report_dsi_notas():
    period_id = cpfecys.current_year_period().id
    if request.vars.periodo:
        periodo_seleccionado = request.vars.periodo
        periodo = db(db.period_year.id == periodo_seleccionado).select(db.period_year.id).first()
        if periodo:
            period_id = periodo.id

    form_select_period = FORM(
        TABLE(
            TR(
                TD(get_period_form_select(period_id)),
                TD(INPUT(_type='submit', _value='Buscar', _class="btn btn-primary"))
            )
        ),
        _method='get'
    )

    query = ((db.dsi_nota.asignacion == db.user_project.id) & (db.user_project.assigned_user == db.auth_user.id)
        & (db.user_project.project == db.project.id) & (db.dsi_nota.period == period_id))

    grid_fields = [
        db.project.name,
        db.auth_user.username,
        db.auth_user.first_name,
        db.auth_user.last_name,
        db.dsi_nota.nota,
        db.dsi_nota.cantidad,
        db.dsi_nota.nota_final
    ]

    grid = SQLFORM.grid(
        query,
        grid_fields,
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

    return dict(grid=grid, form_select_period=form_select_period)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def resolutions_admin():
    period_id = cpfecys.current_year_period().id
    if request.vars.periodo:
        periodo_seleccionado = request.vars.periodo
        periodo = db(db.period_year.id == periodo_seleccionado).select(db.period_year.id).first()
        if periodo:
            period_id = periodo.id

    form_select_period = FORM(
        TABLE(
            TR(
                TD(get_period_form_select(period_id)),
                TD(INPUT(_type='submit', _value='Buscar', _class="btn btn-primary"))
            )
        ),
        _method='get'
    )

    justification_grid_query = ((db.dsi_justification.period == period_id) & (db.dsi_justification.schedule_asignation_id == db.dsi_assignation_schedule.id)
        & (db.dsi_assignation_schedule.schedule_id == db.dsi_schedule.id) & (db.dsi_schedule.assistance_type_id == db.dsi_assistance_type.id)
        & (db.dsi_justification.resolution_status == db.dsi_justification_status.id) & ((db.dsi_justification_status.name == 'rechazado')
        | (db.dsi_justification_status.name == 'aprobado')) & (db.dsi_justification.project == db.user_project.id)
        & (db.user_project.project == db.project.id) & (db.user_project.assigned_user == db.auth_user.id)
        & (db.dsi_justification.justification_type == db.dsi_justification_type.id))

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
        db.dsi_justification.resolution_date,
        db.dsi_justification.resolution_description,
        db.dsi_justification.resolver_user
    ]

    links = [dict(header='Funciones', body=lambda row: approve_or_reject_justification(row))]

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
        paginate=75,
        details=False,
        links=links
    )
    
    return dict(justification_grid=justification_grid, form_select_period=form_select_period)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def schedule_assignation_admin():
    # TODO componer el error por falta de datos en la db
    session.flash = None

    period_id = cpfecys.current_year_period().id
    parameters = db(db.dsi_schedule_parameter).select(db.dsi_schedule_parameter.tutor_amount,
                                                      db.dsi_schedule_parameter.until_date, db.dsi_schedule_parameter.asignation_status)

    tutor_amount = parameters[0].tutor_amount
    assignation_until = parameters[1].until_date
    assignation_status = (True, False)[parameters[2].asignation_status == 0]
    formated_assignation_until = assignation_until.strftime("%Y-%m-%dT%H:%M")

    enable_assignation_form = FORM(
        H3('Parametros de horarios'),
        TABLE(
            TR(
                TD(LABEL('Habilitar asignación')),
                TD(INPUT(_type='checkbox', _name='assignationStatus', _checked=assignation_status))
            ),
            TR(
                TD(LABEL('Habilitado hasta')),
                TD(INPUT(_type='datetime-local', _name='untilDate', _id='untilDate', _value=formated_assignation_until, _class="form-control"))
            ),
            TR(
                TD(LABEL('Cantidad de tutores por horario')),
                TD(INPUT(_type='number', _name='tutorQuantity', _value=tutor_amount, _class="form-control"))
            ),
            TR(
                TD(INPUT(_type='submit', _value=T('Save'), _class="btn btn-success"))
            )
        )
    )

    if enable_assignation_form.process(formname='enable_assignation_form').accepted:
        until_date = request.vars['untilDate']
        assignation_status = (1, 0)[request.vars['assignationStatus'] == None]
        tutor_quantity = request.vars['tutorQuantity']
        db(db.dsi_schedule_parameter.id == 1).update(
            tutor_amount=tutor_quantity,
            updated_by=auth.user.username,
            updated_at=datetime.datetime.now()
        )

        db(db.dsi_schedule_parameter.id == 2).update(
            until_date=until_date,
            updated_by=auth.user.username,
            updated_at=datetime.datetime.now()
        )

        db(db.dsi_schedule_parameter.id == 3).update(
            asignation_status=assignation_status,
            updated_by=auth.user.username,
            updated_at=datetime.datetime.now()
        )

        session.flash = 'Parametros almacenados'
        redirect(URL('dsi', 'schedule_assignation_admin'))

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
                TD(INPUT(_type='submit', _value=T('Search'), _class="btn btn-success"))
            )
        )
    )

    create_day_schedule_button = A(
        BUTTON(SPAN(_class="icon plus icon-plus glyphicon glyphicon-plus"), 'Crear horario por día', _class="btn btn-primary"),
        _href=URL('dsi', 'create_day_schedule_admin')
    )

    day_schedule_table = ''
    if list_schedules.process(formname='list_schedules').accepted:
        day_id = request.vars.dayOfWeek

        day_info = db.executesql(queries.get_day_of_week_by_id(day_id))
        day_info = day_info[0]

        schedules = db.executesql(queries.get_schedule_by_period_id_and_week_day(period_id, day_id))
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
                            BUTTON(
                                SPAN(_class="icon trash icon-trash glyphicon glyphicon-trash"), T('Delete')
                            ),
                            _href=URL('dsi', 'delete_day_schedule_admin', args=schedule[0])
                        )
                    )
                ))

            day_schedule_table = DIV(
                P(B('Día seleccionado: ', SPAN(day_info[1]))),
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
            SPAN(_class="icon plus icon-plus glyphicon glyphicon-plus"), 'Asignar horario por tutor', _class="btn btn-primary"),
            _href=URL('dsi', 'create_schedule_assignation_admin', args=request.vars['tutor']
        )
    )

    tutor_search_form = FORM(
        H3('Lista de horarios asignados'),
        TABLE(
            TR(
                TD(LABEL(T('Academic Tutor'))),
                TD(tutor_select)
            ),
            TR(
                TD(INPUT(_type='submit', _value=T('Search'), _class="btn btn-success"))
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
                    TH('Curso'),
                    TH('Acciones', _colspan=2)
                ))
                for schedule in assignation_schedule:
                    schedules.append(TR(
                        TD(schedule[1]),
                        TD(schedule[2]),
                        TD(schedule[4]),
                        TD(schedule[3]),
                        TD(schedule[5]),
                        TD(schedule[6]),
                        TD(
                            A(
                                BUTTON(SPAN(_class="icon trash icon-trash glyphicon glyphicon-trash"), T('Delete')),
                                _href=URL('dsi', 'delete_schedule_assignation_admin', args=schedule[0])
                            )
                        )
                    ))

                assignation_schedule_table = TABLE(schedules, _class="table table-striped table-bordered")

    return dict(
        create_button=create_button,
        tutor_search_form=tutor_search_form,
        tutor_information_table=tutor_information_table,
        assignation_schedule_table=assignation_schedule_table,
        enable_assignation_form=enable_assignation_form,
        list_schedules=list_schedules,
        day_schedule_table=day_schedule_table,
        create_day_schedule_button=create_day_schedule_button,
        assignation_until=formated_assignation_until
    )

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def create_day_schedule_admin():
    back_button = A(
        I(_class="fa fa-arrow-left", _aria_hiden='true'),
        f" {T('Back')}",
        _class='btn btn-primary',
        _href=URL('dsi', 'schedule_assignation_admin')
    )
    period_id = cpfecys.current_year_period().id

    session.flash = ''
    create_day_schedule = FORM(
        TABLE(
            TR(
                TD('Día de la semana: '),
                TD(get_day_of_week_select())
            ),
            TR(
                TD('Tipo de asistencia: '),
                TD(get_assistance_type_select())
            ),
            TR(
                TD(LABEL('Hora de inicio')),
                TD(INPUT(_name='starting_hour', _type='time'))
            ),
            TR(
                TD(LABEL('Hora de finalización')),
                TD(INPUT(_name='ending_hour', _type='time'))
            ),
            TR(
                INPUT(_type='submit', _value=T('Save'), _class='btn btn-primary')
            )
        )
    )

    if create_day_schedule.process(formname='crate_day_schedule').accepted:
        starting_hour = request.vars.starting_hour
        ending_hour = request.vars.ending_hour
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
@auth.requires_membership('Super-Administrator')
def update_assistance_parameters_admin():
    parameter = db.executesql(queries.get_assistance_parameters_by_id(request.args[0]))

    back_button = A(
        I(_class="fa fa-arrow-left", _aria_hiden='true'),
        f" {T('Back')}",
        _class='btn btn-primary',
        _href=URL('dsi', 'assistance_parameters_admin')
    )

    if not parameter:
        update_form = H2(T('Page not found'))
        return dict(update_form=update_form, back_button=back_button)
    else:
        parameter = parameter[0]
        type_select = get_assistance_type_select(parameter[6])
        class_select = get_assistance_class_select(parameter[7])

        update_form = FORM(TABLE(
            TR(
                TD('Nombre'),
                TD(INPUT(_type='text', _name='name', _value=parameter[1], _class='form-control'))
            ),
            TR(
                TD('Mensaje'),
                TD(INPUT(_type='text', _name='message', _value=parameter[2],  _class='form-control'))
            ),
            TR(
                TD('Porcentaje'),
                TD(INPUT(_type='number', _name='percentage', _value=parameter[3],  _class='form-control'))
            ),
            TR(
                TD('Inicio'),
                TD(INPUT(_type='number', _name='start', _value=parameter[4],  _class='form-control'))
            ),
            TR(
                TD('Fin'),
                TD(INPUT(_type='number', _name='finish', _value=parameter[5],  _class='form-control'))
            ),
            TR(
                TD('Imagen'),
                TD(INPUT(_type='text', _name='image', _value=parameter[10],  _class='form-control'))
            ),
            TR(
                TD('Tipo'),
                TD(type_select)
            ),
            TR(
                TD('Clase'),
                TD(class_select)
            ),
            TR(
                TD(INPUT(_type='submit', _value=T('Save'), _class='btn btn-success'))
            )
        ))

        if (update_form.accepts(request, session)):
            db(db.dsi_assistance_parameter.id == request.args[0]).update(
                name=request.vars.name,
                parameter_message=request.vars.message,
                percentage=request.vars.percentage,
                range_start=request.vars.start,
                range_finish=request.vars.finish,
                image=request.vars.image,
                assistance_class=request.vars.assistanceClass,
                assistance_type=request.vars.assistanceType,
                updated_at=datetime.datetime.now(),
                updated_by=session.auth.user.username
            )
            session.flash = T('Request has been sent')
            redirect(URL('dsi', 'assistance_parameters_admin'))

        return dict(update_form=update_form, back_button=back_button)

def get_assistance_type_select(selected=None):
    types = db.executesql(queries.get_assistance_type_select())
    type_options = list()
    type_options.append(OPTION("Elija un tipo", _value=0))
    for type in types:
        if selected is not None and type[0] == selected:
            type_options.append(OPTION(type[1].capitalize(), _value=type[0], _selected='true'))
        else:
            type_options.append(OPTION(type[1].capitalize(), _value=type[0]))

    return SELECT(type_options, _name='assistanceType', requires=IS_INT_IN_RANGE(1, None), _class="form-control")

def get_period_form_select(selected=None):
    periods = db(db.period_year).select(db.period_year.yearp, db.period_year.period, db.period_year.id)
    tutor_options = list()
    tutor_options.append(OPTION("Periodo Actual", _value=0))
    for period in periods:
        flag = False
        if selected is not None and int(period.id) == int(selected):
            flag = True
        tutor_options.append(OPTION(f"Año {period.yearp} - semestre {period.period}", _value=period.id, _selected=flag))

    return SELECT(tutor_options, _name='periodo', requires=IS_INT_IN_RANGE(1, None), _class="form-control")

def approve_or_reject_justification(row):
    table = TABLE(
        TR(
            TD(
                A(
                    BUTTON(
                        SPAN(_class="icon ok icon-ok glyphicon glyphicon-ok"),
                        SPAN(T('Approve')), 
                        _class="btn btn-primary"
                    ),
                    _href=URL('dsi', 'change_justification_status', args=['aprobado', row.dsi_justification.id])
                )
            ),
            TD(
                A(
                    BUTTON(
                        SPAN(_class="icon remove icon-remove glyphicon glyphicon-remove"),
                        SPAN(T('Reject')),
                        _class="btn btn-danger"
                    ),
                    _href=URL('dsi', 'change_justification_status', args=['rechazado', row.dsi_justification.id])
                )
            )
        )
    )

    return table

def get_dates(from_date, to_date, day_list):
    holidays = db.executesql(queries.get_holidays(from_date, to_date))
    tmp_list = list()
    date_list = list()
    ## Creates a list of all the dates falling between the from_date and to_date range
    for x in range((to_date - from_date).days + 1):
        tmp_list.append(from_date + datetime.timedelta(days=x))

    for date_record in tmp_list:
        if date_record.weekday() in day_list:
            fecha = date_record.strftime("'%Y-%m-%d'")
            se_agrega = True
            for holiday in holidays:
                holiday = holiday[0].strftime("'%Y-%m-%d'")
                if holiday == fecha:
                    se_agrega = False
            if se_agrega:
                date_list.append(fecha)
    return date_list

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def crear_justificacion(tutor_id, period_id, fecha_falta, tipo, status, asignacion, contexto, asistencia, schedule_asignation_id):
    if not existe_justificacion(asignacion, fecha_falta):
        db.dsi_justification.insert(
            contexto=contexto,
            description='',
            created_at=datetime.datetime.now(),
            created_by=tutor_id,
            period=period_id,
            absence_date=datetime.datetime.strptime(fecha_falta, "'%Y-%m-%d'"),
            justification_type=tipo,
            resolution_status=status,
            requester_user=tutor_id,
            project=asignacion,
            id_asistencia=asistencia,
            schedule_asignation_id=schedule_asignation_id
        )

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def existe_justificacion(asignacion, fecha):
    if db.executesql(queries.existe_justificacion(asignacion, fecha)):
        return True
    return False

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def enviar_notificacion(title, sender, destination, period, message):
    db.dsi_notification.insert(
        title=title,
        sender=sender,
        destination=destination,
        period=period,
        created_at=datetime.datetime.now(),
        notification_message=message
    )

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def set_nota_in_asignacion(asignacion_id, period_id, nota_final, cantidad, nota):
    query = db(db.dsi_nota.asignacion == asignacion_id)
    qsl = query.select(db.dsi_nota.id)
    print (qsl)
    if not qsl:
        db.dsi_nota.insert(
            period=period_id,
            cantidad=cantidad,
            nota=nota,
            nota_final=nota_final,
            asignacion=asignacion_id,
            updated_at=datetime.datetime.now()
        )
    else:
        query.update(
            cantidad=cantidad,
            nota=nota,
            nota_final=nota_final,
            updated_at=datetime.datetime.now()
        )

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def aprobar_justificacion(justificacion, period_id):
    horario_asignacion = db(db.dsi_assignation_schedule.id == justificacion.schedule_asignation_id).select(db.dsi_assignation_schedule.schedule_id).first()
    horario = db(db.dsi_schedule.id == horario_asignacion.schedule_id).select(db.dsi_schedule.starting_hour, db.dsi_schedule.ending_hour, db.dsi_schedule.id, db.dsi_schedule.assistance_type_id).first()

    horario_entrada = f"{justificacion.absence_date} {horario.starting_hour}"
    horario_salida = f"{justificacion.absence_date} {horario.ending_hour}"

    if justificacion.id_asistencia is not None:
        asistencia_query = db(db.dsi_assistance.id == justificacion.id_asistencia)
        asistencia = asistencia_query.select(db.dsi_assistance.starting_score).first()

        nota = (asistencia.starting_score + 100)/2
        asistencia_query.update(
            finishing_hour=datetime.datetime.strptime(horario_salida, "%Y-%m-%d %H:%M:%S"),
            finishing_score=100,
            score=nota,
            updated_at=datetime.datetime.now(),
            updated_by=1
        )
    else:
        db.dsi_assistance.insert(
            starting_hour=datetime.datetime.strptime(horario_entrada, "%Y-%m-%d %H:%M:%S"),
            finishing_hour=datetime.datetime.strptime(horario_salida, "%Y-%m-%d %H:%M:%S"),
            starting_score=100,
            finishing_score=100,
            score=100,
            schedule=horario.id,
            tutor=justificacion.requester_user,
            justification=justificacion.id,
            period=period_id,
            assistance_type=horario.assistance_type_id,
            created_at=datetime.datetime.now(),
            created_by=1,
            updated_at=datetime.datetime.now(),
            updated_by=1,
            asignation_id=justificacion.project
        )

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def system_parameter_admin():
    period_id = cpfecys.current_year_period().id

    try:
        cantidad_justificaciones_tutores = db.executesql(queries.get_system_parameter_by_name(period_id, 'cantidad_justificaciones_tutores'))[0][2]
    except IndexError:
        cantidad_justificaciones_tutores = 0

    try:
        cantidad_justificaciones_DSI = db.executesql(queries.get_system_parameter_by_name(period_id, 'cantidad_justificaciones_dsi'))[0][2]
    except IndexError:
        cantidad_justificaciones_DSI = 0

    try:
        inicio_periodo = db.executesql(queries.get_system_parameter_by_name(period_id, 'inicio_periodo'))[0][3].strftime("%Y-%m-%d")
    except IndexError:
        inicio_periodo = "Error al obtener la fecha"

    try:
        fin_periodo = db.executesql(queries.get_system_parameter_by_name(period_id, 'fin_periodo'))[0][3].strftime("%Y-%m-%d")
    except IndexError:
        fin_periodo = "Error al obtener la fecha"

    try:
        habilitar_DSI_creacion_justificacion = (False, True)[db.executesql(queries.get_system_parameter_by_name(period_id, 'habilitar_dsi_justificaciones'))[0][4] == 1]
    except IndexError:
        habilitar_DSI_creacion_justificacion = False

    try:
        habilitar_DSI_adminstracion_horarios = (False, True)[db.executesql(queries.get_system_parameter_by_name(period_id, 'habilitar_dsi_horarios'))[0][4] == 1]
    except IndexError:
        habilitar_DSI_adminstracion_horarios = False

    try:
        print("query", db.executesql(queries.get_system_parameter_by_name(period_id, 'habilitar_dsi_asuetos')))
        habilitar_DSI_adminstracion_asuetos = (False, True)[db.executesql(queries.get_system_parameter_by_name(period_id, 'habilitar_dsi_asuetos'))[0][4] == 1]
    except IndexError:
        habilitar_DSI_adminstracion_asuetos = False

    form = FORM(
        TABLE(
            TR(
                TD('Cantidad de justificaciones Tutores'),
                TD(INPUT(_name='cantidad_justificaciones_tutores', _type='number', _value=cantidad_justificaciones_tutores, _class='form-control'))
            ),
            TR(
                TD('Cantidad de justificaciones DSI'),
                TD(INPUT(_name='cantidad_justificaciones_DSI', _type='number', _value=cantidad_justificaciones_DSI, _class='form-control'))
            ),
            TR(
                TD('Inicio de Periodo'),
                TD(INPUT(_name='inicio_periodo', _type='date', _value=inicio_periodo, _class='form-control'))
            ),
            TR(
                TD('Fin de Periodo'),
                TD(INPUT(_name='fin_periodo', _type='date', _value=fin_periodo, _class='form-control'))
            ),
            TR(
                TD('Habilitar creación de justificaciones'),
                TD(INPUT(_name='enableDsiJustification', _type='checkbox', _checked=habilitar_DSI_creacion_justificacion))
            ),
            TR(
                TD('Habilitar administración de horarios'),
                TD(INPUT(_name='enableDsiScheduleAdmin', _type='checkbox', _checked=habilitar_DSI_adminstracion_horarios))
            ),
            TR(
                TD('Habilitar administración de asuetos'),
                TD(INPUT(_name='enableDsiHolidaysAdmin', _type='checkbox', _checked=habilitar_DSI_adminstracion_asuetos))
            ),
            TR(
                TD(INPUT(_type='submit', _value='Guardar', _class='btn btn-success'))
            )
        )
    )

    if (form.accepts(request, session)):
        db((db.dsi_system_parameters.name == "cantidad_justificaciones_tutores") & (db.dsi_system_parameters.period == period_id)).update(
            parameter_number=request.vars.cantidad_justificaciones_tutores
        )

        db((db.dsi_system_parameters.name == "cantidad_justificaciones_dsi") & (db.dsi_system_parameters.period == period_id)).update(
            parameter_number=request.vars.cantidad_justificaciones_DSI
        )

        db((db.dsi_system_parameters.name == "inicio_periodo") & (db.dsi_system_parameters.period == period_id)).update(
            parameter_date=request.vars.inicio_periodo
        )

        db((db.dsi_system_parameters.name == "fin_periodo") & (db.dsi_system_parameters.period == period_id)).update(
            parameter_date=request.vars.fin_periodo
        )

        db((db.dsi_system_parameters.name == "habilitar_dsi_justificaciones") & (db.dsi_system_parameters.period == period_id)).update(
            parameter_bool=(0, 1)[request.vars.enableDsiJustification == 'on']
        )

        db((db.dsi_system_parameters.name == "habilitar_dsi_horarios") & (db.dsi_system_parameters.period == period_id)).update(
            parameter_bool=(0, 1)[request.vars.enableDsiScheduleAdmin == 'on']
        )

        db((db.dsi_system_parameters.name == "habilitar_dsi_asuetos") & (db.dsi_system_parameters.period == period_id)).update(
            parameter_bool=(0, 1)[request.vars.enableDsiHolidaysAdmin == 'on']
        )

        session.flash = 'Parametro de systema actualizado.'
        redirect(URL('dsi', 'system_parameter_admin'))

    return dict(form=form)

def get_assistance_class_select(selected=None):
    classes = db.executesql(queries.get_assistance_class())
    type_options = list()
    type_options.append(OPTION("Elija una clase", _value=0))
    
    for clazz in classes:
        if selected is not None and clazz[0] == selected:
            type_options.append(OPTION(clazz[1].capitalize(), _value=clazz[0], _selected='true'))
        else:
            type_options.append(OPTION(clazz[1].capitalize(), _value=clazz[0]))

    return SELECT(type_options, _name='assistanceClass', requires=IS_INT_IN_RANGE(1, None),  _class='form-control')

def get_day_of_week_select(selected=None):
    days = db.executesql(queries.get_day_of_week())
    day_options = list()
    day_options.append(OPTION("Elija un día", _value=0))
    
    for day in days:
        flag = False
        if selected is not None and int(day[0]) == int(selected): flag = True
        day_options.append(OPTION(day[1].capitalize(), _value=day[0], _selected=flag))

    return SELECT(day_options, _name='dayOfWeek', requires=IS_INT_IN_RANGE(1, None), _class="form-control")

def get_tutor_form_select(period_id, selected=None):
    tutors = db.executesql(queries.get_tutors_active_in_current_period(period_id))
    tutor_options = list()
    tutor_options.append(OPTION("Elija un tutor", _value=0))

    for tutor in tutors:
        flag = False
        if selected is not None and int(tutor[0]) == int(selected): flag = True
        first_name = ' '.join(list(map(lambda x: x.capitalize(), tutor[3].split(' '))))
        last_name = ' '.join(list(map(lambda x: x.capitalize(), tutor[4].split(' '))))
        tutor_options.append(OPTION(
            f"{tutor[1].capitalize()} - {first_name.strip()} {last_name.strip()}",
            _value=tutor[0], _selected=flag
        ))

    return SELECT(tutor_options, _name='tutor', requires=IS_INT_IN_RANGE(1, None), _class="form-control")

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def get_curso_select(tutor_informations, selected):
    type_options = list()
    for information in tutor_informations:
        if selected is not None and int(information[6]) == int(selected):
            type_options.append(OPTION(information[5].encode('utf-8'), _value=information[6], _selected='true'))
        else:
            type_options.append(OPTION(information[5].encode('utf-8'), _value=int(information[6])))

    return SELECT(type_options, _name='c', requires=IS_INT_IN_RANGE(1, None), _class='form-control')

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def get_tutor_information(tutor_id, period_id):
    return db.executesql(queries.get_tutor_information(tutor_id, period_id))

def validate_assignation_schedule(period_id, tutor_id, type_id, schedule_id, class_room, assignacion_id):
    mensaje_respuesta = 'Horario asignado correctamente'
    DSITYPE = 2

    project = db((db.user_project.assigned_user == tutor_id) & (db.user_project.period == period_id)).select().first()
    horario = db(db.dsi_schedule.id == schedule_id).select(db.dsi_schedule.week_day, db.dsi_schedule.assistance_type_id,
                                                           db.dsi_schedule.id).first()
    horarios_por_periodo = db((db.dsi_assignation_schedule.schedule_id == db.dsi_schedule.id) & (db.dsi_assignation_schedule.tutor_id == tutor_id)
                        & (db.dsi_assignation_schedule.isEnabled == 1) & (db.dsi_schedule.period == period_id)
                        & (db.dsi_schedule.assistance_type_id == type_id)).select(db.dsi_assignation_schedule.id)
    horarios_mismo_dia = db((db.dsi_assignation_schedule.schedule_id == db.dsi_schedule.id) & (db.dsi_assignation_schedule.tutor_id == tutor_id)
                        & (db.dsi_assignation_schedule.isEnabled == 1) & (db.dsi_schedule.period == period_id)
                        & (db.dsi_schedule.week_day == horario.week_day)).select()

    mismo_horario_curso = validate_schedule_with_course_schedule(tutor_id, horario.week_day, period_id)

    if DSITYPE == type_id and not mismo_horario_curso:
        mensaje_respuesta += '\nAdvertencia, el horario del curso coincide con el horario elegido'

    if horarios_mismo_dia:
        mensaje_respuesta += '\nAdvertencia, el tutor ya posee un horario el día seleccionado'

    if not horarios_por_periodo:
        if horario.assistance_type_id == DSITYPE:
            mensaje_respuesta += '\nHorario almacenado correctamente'

    save_assignation_schedule(horario.id, tutor_id, class_room, assignacion_id, period_id)

    return mensaje_respuesta

def validate_schedule_with_course_schedule(tutor_id, day_id, period_id):
    schedules = db.executesql(queries.get_course_schedule_by_tutor_id_and_day_id(tutor_id, day_id, period_id))

    if not schedules:
        return True
    return False

def save_assignation_schedule(schedule_id, tutor_id, classroom, project_id, period_id):
    db.dsi_assignation_schedule.insert(
        schedule_id=schedule_id,
        tutor_id=tutor_id,
        classroom=classroom,
        created_at=datetime.datetime.now(),
        isEnabled=1,
        created_by=auth.user.username,
        updated_at=datetime.datetime.now(),
        updated_by=auth.user.username,
        project_assignation=project_id,
        period = period_id
    )

def get_project_select():
    projects = db.executesql(queries.get_projects())

    options = list()
    options.append(OPTION("Elija un curso", _value=0))
    for project in projects:
        options.append(OPTION(f"{project[1]} - {project[2].strip()}", _value=project[0]))

    return SELECT(options, _name='project', requires=IS_INT_IN_RANGE(1, None), _class="form-control")

def remove_finger_print(row):
    print(row)
    table = TABLE(
        TR(
            TD(
                A(
                    BUTTON(
                        SPAN(_class="icon remove icon-remove glyphicon glyphicon-remove"),
                        SPAN('Borrar'),
                        _class="btn btn-danger"
                    ),
                    _href=URL('dsi', 'remove_fingerprint', args=[row.dsi_fingerprint.tutor_id])
                )
            )
        )
    )

    return table

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def delete_schedule_assignation_admin():
    db(db.dsi_assignation_schedule.id == request.args[0]).update(isEnabled=0)
    session.flash = 'Asignación de horario eliminado.'
    redirect(URL('dsi', 'schedule_assignation_admin'))

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def approve_all():
    restriction = request.vars['restrictions']
    period = request.vars['period']
    grade_all(restriction, period)
    redirect(URL('item_detail', vars=dict(restriction=restriction)))

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def grade_all(restriction, period):
    areas = db((db.item_restriction_area.item_restriction == restriction) & (db.area_level.id == db.item_restriction_area.area_level)).select(db.area_level.id)
    for area in areas:
        projects = db((db.project.area_level == db.area_level.id) & (db.area_level.id == area.id) &
                      (db.item_restriction.id == restriction) & (db.item_restriction_area.area_level == area.id) &
                      (db.item_restriction_area.item_restriction == restriction) & (db.item_restriction_area.item_restriction == db.item_restriction.id) &
                      (db.item_restriction_area.area_level == db.area_level.id) & (db.item_restriction_area.is_enabled == True)).select(db.project.id)
        
        for project in projects:
            exception = db((db.item_restriction_exception.project == project.id) & (db.item_restriction_exception.item_restriction == restriction))
            if exception.count() == 0:
                assignations = db((db.auth_user.id == db.user_project.assigned_user) & (db.auth_user.id == db.auth_membership.user_id)
                            & (db.auth_membership.group_id == db.auth_group.id) & (db.auth_group.role == 'Student')
                            & (db.user_project.project == project.id) & (db.user_project.period == db.period_year.id)
                            & ((db.user_project.period <= period) & ((db.user_project.period.cast('integer') + db.user_project.periods) > period))).select(db.user_project.id)
                for assignation in assignations:
                    item = db((db.item.assignation == assignation.id) & (db.item.item_restriction == restriction)
                        & (db.item.item_restriction == db.item_restriction.id) & (db.item_restriction.is_enabled == True)
                        & (db.item.created == period)).select(db.item.score, db.item.done_activity, db.item.min_score).first()
                    if item == None:
                        restriction_instance = db(db.item_restriction.id == restriction).select().first()
                        db.item.insert(
                            is_active=True,
                            done_activity=True,
                            created=period,
                            item_restriction=restriction,
                            assignation=assignation.id,
                            score=restriction_instance.min_score,
                            min_score=restriction_instance.min_score
                        )
                    else:
                        if item.score != None: item.update_record(score=item.min_score)
                        if item.done_activity == None: item.update_record(done_activity=True)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def delete_day_schedule_admin():
    db(db.dsi_schedule.id == request.args[0]).delete()
    session.flash = 'Horario del dia seleccionado eliminado.'
    redirect(URL('dsi', 'schedule_assignation_admin'))

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def remove_fingerprint():
    db(db.dsi_fingerprint.tutor_id == request.args[0]).delete()
    redirect(URL('dsi', 'fingerprint_report_admin'))

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def delete_assistance_parameters_admin():
    db(db.dsi_assistance_parameter.id == request.args[0]).delete()
    session.flash = 'Parametro de asistencia eliminado.'
    redirect(URL('dsi', 'assistance_parameters_admin'))

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def delete_exception_courses_admin():
    db(db.dsi_exception_course.id == request.args[0]).delete()
    session.flash = 'Configuración eliminada'
    redirect(URL('dsi', 'exception_courses_admin'))