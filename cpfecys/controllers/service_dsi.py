import json
import datetime
import cpfecys

import dsi_queries as queries

class TutorResponse:
    def __init__(self, id, username, cui, name, courses):
        self.id = id
        self.username = username
        self.cui = cui
        self.name = name
        self.courses = courses

class CourseResponse:
    def __init__(self, id, name, code, schedules):
        self.id = id
        self.name = name
        self.code = code
        self.schedules = schedules

class ScheduleResponse:
    def __init__(self, id, start, end, day_of_week, classroom, assignment_type):
        self.id = id
        self.start = str(start)
        self.end = str(end)
        self.dayOfWeek = day_of_week
        self.classroom = classroom
        self.assignmentType = assignment_type

class AssistanceTypeResponse:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class DayOfWeek:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class FingerPrint:
    def __init__(self, id, fingerprint):
        self.tutorId = id
        self.fingerprint = fingerprint

class TutorResponseEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, TutorResponse):
            return {
                'id': obj.id,
                'name': obj.name,
                'cui': obj.cui,
                'username': obj.username,
                'courses': obj.courses
            }
        return json.JSONEncoder.default(self, obj)

class CourseResponseEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, CourseResponse):
            return {
                'id': obj.id,
                'name': obj.name,
                'code': obj.code,
                'scheduler': obj.schedules
            }
        return json.JSONEncoder.default(self, obj)

class ScheduleResponseEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ScheduleResponse):
            return {
                'id': obj.id,
                'start': obj.start,
                'end': obj.end,
                'dayOfWeek': obj.dayOfWeek,
                'classroom': obj.classroom,
                'assignmentType': obj.assignmentType
            }
        return json.JSONEncoder.default(self, obj)

@request.restful()
def assistanceTypes():
    generic_response_values(response)
    def GET():
        assistance_types = db.executesql(queries.get_assistance_type_select())
        types_response = [AssistanceTypeResponse(asisstance_type[0], asisstance_type[1]).__dict__ for asisstance_type in assistance_types]
        return json.dumps(types_response)

    return locals()

@request.restful()
def dayOfWeek():
    generic_response_values(response)
    def GET():
        days = db.executesql(queries.get_day_of_week())
        days_response = [DayOfWeek(day[0], day[1]).__dict__ for day in days]
        return json.dumps(days_response)

    return locals()

@request.restful()
def tutors():
    generic_response_values(response)
    def GET():
        period_id = cpfecys.current_year_period().id
        tutors = db.executesql(queries.get_tutors_active_in_current_period(period_id))
        tutors_response = list()
        for tutor in tutors:
            tutor_id = tutor[0]
            username = tutor[1].strip() or ''
            cui = tutor[2].strip() or ''
            first_name = tutor[3].strip() or ''
            last_name = tutor[4] or ''

            courses = db.executesql(queries.get_courses_by_tutor_id_and_period_id(tutor_id, period_id))
            courses_response = list()
            for course in courses:
                schedules = db.executesql(queries.get_tutor_schedule_by_course_id(course[3]))
                schedules_response = [
                    ScheduleResponse(schedule[0], schedule[1], schedule[2], schedule[3], schedule[4], schedule[5]).__dict__
                    for schedule in schedules
                ]
                courses_response.append(CourseResponse(course[0], course[1], course[2], schedules_response).__dict__)
            
            tutors_response.append(TutorResponse(tutor_id, username, cui, f'{first_name} {last_name}', courses_response))
        
        return json.dumps(tutors_response, cls=TutorResponseEncoder, ensure_ascii=False)
    
    def POST(*args, **vars):
        period_id = cpfecys.current_year_period().id
        tutor_id = request.vars.tutor
        type_id = request.vars.type
        current_time_str = request.vars.time
        assistance_date_time = datetime.datetime.strptime(current_time_str, '%Y-%m-%d %I:%M%p')
        day_of_week = assistance_date_time.weekday() + 1

        return calculate_assistance(period_id, tutor_id, type_id, assistance_date_time, day_of_week)

    return locals()

@request.restful()
def assistances():
    generic_response_values(response)
    def POST(*args, **vars):
        period_id = cpfecys.current_year_period().id
        assistances = request.vars.assistances

        results = list()
        for assistance in assistances:
            tutor_id = assistance['tutor']
            type_id = assistance['type']
            current_time_str = assistance['time']
            
            assistance_date_time = datetime.datetime.strptime(current_time_str, '%Y-%m-%d %I:%M%p')
            day_of_week = assistance_date_time.weekday() + 1
            results.append(calculate_assistance(period_id, tutor_id, type_id, assistance_date_time, day_of_week))

        return dict(results=results)

    return locals()

@request.restful()
def fingerprint():
    generic_response_values(response)
    def POST(*args, **vars):
        enable_registration = db.executesql(queries.get_fingerprint_parameter('registration'))
        enable_registration = enable_registration[0]

        if enable_registration[2] == 0:
            msj = 'Actualmente no es permitido el registro de huella, comuniquese con el administrador.'
            return dict(message=msj, score=1)
        
        period_id = cpfecys.current_year_period().id
        finger_print = request.vars.fingerprint
        tutor_id = request.vars.tutorId

        query = db(db.dsi_fingerprint.tutor_id == tutor_id)
        existed_fingerprint = query.select()

        if existed_fingerprint:
            query.update(
                fingerprint=finger_print,
                updated_at=datetime.datetime.now(),
                updated_by='admin'
            )
        else:
            db.dsi_fingerprint.insert(
                tutor_id=tutor_id,
                fingerprint=finger_print,
                created_at=datetime.datetime.now(),
                created_by='admin',
                updated_at=datetime.datetime.now(),
                updated_by='admin'
            )
        
        return dict(message='Huella almacenada', score=2)
    
    def GET(*args, **vars):
        finger_prints = db.executesql(queries.get_finger_prints())
        result = [FingerPrint(finger_print[0], finger_print[1]).__dict__ for finger_print in finger_prints]
        return json.dumps(result)

    return locals()


def calculate_assistance(period_id, tutor_id, type_id, assistance_date_time, day_of_week):
    current_time = assistance_date_time.time()
    # Obtiene asistencia iniciada
    assistance = db.executesql(queries.get_starting_assistance(tutor_id, type_id, assistance_date_time.date()))

    time_to_validate = None
    score = 0
    parameters = None
    if assistance:
        # Calculando finalizacion de asistencia
        assistance = assistance[0]
        score = float(assistance[1])
        schedule_id = assistance[3]

        # Obtiene parametros de rango de penalizacion
        parameters = db.executesql(queries.get_assistance_parameters_by_type_and_class_and_period(type_id, 2, period_id))
        # Obtiene Horario por el id
        schedule = db.executesql(queries.get_schedule_by_id(schedule_id))

        schedule = schedule[0]
        time_to_validate = schedule[3]

        # Calcula la nota
        for parameter in parameters:
            starting_range_time_delta = time_to_validate + datetime.timedelta(minutes=parameter[4])
            ending_range_time_delta = time_to_validate + datetime.timedelta(minutes=parameter[5])

            starting_range = datetime.datetime.utcfromtimestamp(int(starting_range_time_delta.total_seconds()))
            ending_range = datetime.datetime.utcfromtimestamp(int(ending_range_time_delta.total_seconds()))

            # Validacion de horario
            if starting_range.time() <= current_time <= ending_range.time():
                respuesta = parameter[2]
                partial_score = float(parameter[3])
                imagen = parameter[8]
                score = (score + partial_score) / 2

                db(db.dsi_assistance.id == assistance[0]).update(
                    finishing_hour=assistance_date_time,
                    finishing_score=partial_score,
                    updated_at=datetime.datetime.now(),
                    updated_by=tutor_id,
                    score=score,
                    assistance_type=type_id
                )

                return dict(message=respuesta, score=score, image=imagen)

        msj = "Hora de asistencia no asignada, por favor verifique su horario."
        return dict(message=msj, score=0, image='HorarioNoAsignado.jpg')
    else:
        # Obtiene horario
        schedule = db.executesql(queries.get_specific_schedule(tutor_id, type_id, day_of_week, period_id))
        if schedule:
            schedule = schedule[0]
            time_to_validate = schedule[2]
            parameters = db.executesql(queries.get_assistance_parameters_by_type_and_class_and_period(type_id, 1, period_id))

            # Calcula la nota
            for parameter in parameters:
                starting_range_time_delta = time_to_validate + datetime.timedelta(minutes=parameter[4])
                ending_range_time_delta = time_to_validate + datetime.timedelta(minutes=parameter[5])

                starting_range = datetime.datetime.utcfromtimestamp(int(starting_range_time_delta.total_seconds()))
                ending_range = datetime.datetime.utcfromtimestamp(int(ending_range_time_delta.total_seconds()))

                # Validacion de horario
                if starting_range.time() <= current_time <= ending_range.time():
                    respuesta = parameter[2]
                    partial_score = float(parameter[3])
                    score = partial_score / 2

                    # Inicianando asistencia
                    db.dsi_assistance.insert(
                        starting_hour=assistance_date_time,
                        starting_score=partial_score,
                        created_at=datetime.datetime.now(),
                        created_by=tutor_id,
                        schedule=schedule[0],
                        tutor=tutor_id,
                        score=score,
                        period=period_id,
                        asignation_id=schedule[6]
                    )

                    return dict(message=respuesta, score=score, image=parameter[8])

            msj = "Hora de asistencia no asignada, por favor verifique su horario."
            return dict(message=msj, score=0, image='HorarioNoAsignado.jpg')
        else:
            msj = "Hora de asistencia no asignada, por favor verifique su horario."
            return dict(message=msj, score=0, image='HorarioNoAsignado.jpg')

def generic_response_values(response):
    response.view = 'generic.json'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Allow-Methods'] = '*'
    response.headers['Content-Type'] = 'application/json; charset=utf-8'