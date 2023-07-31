import csv
import cpfecys
import datetime
import chardet

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def course_schedule_upload():
    current_period = cpfecys.current_year_period()

    cursos_error = list()
    errors = list()
    if request.vars.csvfile is not None:
        try:
            file = request.vars.csvfile.file
        except:
            response.flash = T('Please upload a file.')
            return dict(
                success=False,
                file=False,
                periods=periods,
                current_period=current_period,
                errors=errors,
                cursos_error=cursos_error
            )
        
        columns = {
            'codigo_proyecto': 0,
            'hora_inicio': 1,
            'hora_final': 2,
            'lunes': 3,
            'martes': 4,
            'miercoles': 5,
            'jueves': 6,
            'viernes': 7,
            'sabado': 8,
            'domingo': 9,
            'codigo_docente': 10,
            'edificio': 11,
            'salon': 12
        }
        try:
            db(db.dsi_schedule_course.period == current_period.id).delete()
            db.commit()
            try:
                content_file = file.read()
                detection = chardet.detect(content_file)['encoding']
                content_file = content_file.decode(detection).splitlines()
            except:
                content_file = []
            cr = csv.reader(content_file, delimiter=',', quotechar='"')
            cont = 1
            for row in cr:
                insert = False
                course_code = row[columns['codigo_proyecto']]
                starting_hour = row[columns['hora_inicio']]
                ending_hour = row[columns['hora_final']]
                building = row[columns['edificio']]
                room = row[columns['salon']]

                course = db(db.project.project_id == course_code).select(db.project.id).first()
                teacher = db(db.auth_user.username == row[columns['codigo_docente']]).select(db.auth_user.id).first()

                if not course:
                    insert = True
                    row.insert(0, cont)
                    row.append('Error: Código de curso invalido ')
                    errors.append(row)

                if not teacher:
                    row.append('Error: Código de catedrático invalido')
                    if not insert:
                        insert = True
                        row.insert(0, cont)
                        errors.append(row)

                if course and teacher:
                    if row[columns['lunes']] == 'X':
                        save_course_schedule(course.id, current_period.id, starting_hour, ending_hour, 1, teacher.id, building, room)
                    if row[columns['martes']] == 'X':
                        save_course_schedule(course.id, current_period.id, starting_hour, ending_hour, 2, teacher.id, building, room)
                    if row[columns['miercoles']] == 'X':
                        save_course_schedule(course.id, current_period.id, starting_hour, ending_hour, 3, teacher.id, building, room)
                    if row[columns['jueves']] == 'X':
                        save_course_schedule(course.id, current_period.id, starting_hour, ending_hour, 4, teacher.id, building, room)
                    if row[columns['viernes']] == 'X':
                        save_course_schedule(course.id, current_period.id, starting_hour, ending_hour, 5, teacher.id, building, room)
                    if row[columns['sabado']] == 'X':
                        save_course_schedule(course.id, current_period.id, starting_hour, ending_hour, 6, teacher.id, building, room)
                    if row[columns['domingo']] == 'X':
                        save_course_schedule(course.id, current_period.id, starting_hour, ending_hour, 7, teacher.id, building, room)
                else:
                    cursos_error.append(course_code)
                if insert:
                    row.append('end_row')
                cont += 1
            if not cursos_error:
                response.flash = 'Carga de horario de cursos realizada con éxito.'
            else:
                response.flash = 'Algunos cursos presentaron error, porfavor revise la sección de errores'
        except Exception as e:
            print(e)
            response.flash = T('File doesn\'t seem properly encoded.') + e
            return dict(
                success=False,
                file=False,
                periods=periods,
                current_period=current_period,
                errors=errors,
                cursos_error=cursos_error
            )

    return dict(
        success=False,
        file=False,
        periods=periods,
        current_period=current_period,
        errors=errors,
        cursos_error=cursos_error
    )

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def course_schedules():
    periodo_actual = cpfecys.current_year_period()
    period_id = periodo_actual.id

    periodo_seleccionado = request.vars.periodo or period_id
    periodo = db(db.period_year.id == periodo_seleccionado).select(db.period_year.id, db.period_year.yearp, db.period_year.period).first()

    if not periodo:
        periodo = periodo_actual
        period_id = periodo_actual.id
    else:
        period_id = periodo.id

    title = f'Horario de cursos en el año {periodo.yearp} en el semestre {periodo.period}'

    course_schedule_query = (
        (db.vw_dsi_schedule.period == period_id)
    )

    course_schedule_fields = [
        db.vw_dsi_schedule.project_id,
        db.vw_dsi_schedule.course_name,
        db.vw_dsi_schedule.full_name,
        db.vw_dsi_schedule.building,
        db.vw_dsi_schedule.room,
        db.vw_dsi_schedule.week_day,
        db.vw_dsi_schedule.starting_hour,
        db.vw_dsi_schedule.finishing_hour
    ]

    db.auth_user.first_name.readable = False
    db.auth_user.last_name.readable = False

    schedules_grid = SQLFORM.grid(
        course_schedule_query,
        course_schedule_fields,
        csv=True,
        searchable=True,
        sortable=True,
        deletable=False,
        editable=False,
        create=False,
        user_signature=True,
        maxtextlength=255,
        paginate=100,
        details=False
    )

    form_select_period = FORM(
        TABLE(
            TR(
                TD(get_periods_form_select()),
                TD(INPUT(_type='submit', _value='Buscar', _class='btn btn-primary'))
            )
        ),
        _method='get'
    )


    return dict(
        title=title,
        schedules_grid=schedules_grid,
        select_period=form_select_period
    )

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def periods():
    grid = SQLFORM.grid(db.period_year)
    return dict(grid=grid)

def save_course_schedule(course_id, period_id, starting_hour, ending_hour, week_day, teacher, building, room):
    db.dsi_schedule_course.insert(
        project_id=course_id,
        period=period_id,
        starting_hour=starting_hour,
        finishing_hour=ending_hour,
        day_of_week_id=week_day,
        user_id=teacher,
        building=building,
        room=room,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )

def get_periods_form_select():
    periods = db(db.period_year).select()
    tutor_options = list()
    tutor_options.append(OPTION("Periodo Actual", _value=0))
    for period in periods:
        tutor_options.append(OPTION(f"Año {period.yearp} - semestre {period.period}", _value=period.id))

    return SELECT(tutor_options, _name='periodo', requires=IS_INT_IN_RANGE(1, None), _class='form-control')

