def get_courses_by_tutor_id_and_period_id(tutor_id, period_id):
    return (f"""
        SELECT
            p.id,
            p.project_id,
            p.name,
            up.id
        FROM user_project AS up
            JOIN project AS p ON up.project = p.id
        WHERE up.assigned_user = {tutor_id}
            AND up.period = {period_id};
    """)

def get_tutor_schedule_by_course_id(assignation_id):
    return (f"""
        SELECT
            ds.id,
            ds.starting_hour,
            ds.ending_hour,
            ds.week_day,
            das.classroom,
            ds.assistance_type_id
        FROM dsi_assignation_schedule AS das
            JOIN dsi_schedule AS ds
        WHERE das.isEnabled = 1
            AND das.tutor_id = {assignation_id};
    """)

def get_tutors_active_in_current_period(period_id):
    return (f"""
        SELECT DISTINCT
            au.id,
            au.username,
            au.cui,
            au.first_name,
            au.last_name
        FROM user_project AS up
            JOIN auth_user AS au ON up.assigned_user = au.id
            JOIN project AS p ON up.project = p.id
            JOIN area_level AS al ON p.area_level = al.id
            JOIN auth_membership AS am ON up.assigned_user = am.user_id
            JOIN auth_group AS ag ON am.group_id = ag.id
        WHERE 
            up.period <= {period_id}
            AND (up.period + up.periods) > {period_id}
            AND al.id IN (1)
            AND ag.role = 'Student'
        GROUP BY up.assigned_user
        ORDER BY CAST(au.username AS DECIMAL) ASC;
    """)


def getTutorAssistanceScore(periodId, tutorId):
    return ("select p.name, i.score from user_project as up"
            " join item as i on (up.id = i.assignation)"
            " join project as p on(up.project = p.id)"
            " where i.item_restriction = 26"
            " and up.period = {}"
            " and up.assigned_user = {};".format(periodId, tutorId))


def get_tutor_schedule_by_period_id_and_tutor_id(period_id, id):
    return (f"""
        SELECT
            das.id,
            ds.starting_hour,
            ds.ending_hour,
            das.classroom,
            dow.name,
            dat.name,
            p.name
        FROM dsi_assignation_schedule AS das
            JOIN user_project AS up ON das.project_assignation = up.id
            JOIN project AS p ON up.project = p.id
            JOIN dsi_schedule AS ds ON das.schedule_id = ds.id
            JOIN dsi_assistance_type AS dat ON ds.assistance_type_id = dat.id
            JOIN day_of_week AS dow ON ds.week_day = dow.id
        WHERE 
            das.period = {period_id}
            AND das.tutor_id = {id}
            AND das.isEnabled = 1
    """)

def get_tutor_schedule_by_period_id_and_tutor_id_and_assignation_id(period_id, tutor_id, assignation_id):
    return (f"""
        SELECT
            das.id,
            ds.starting_hour,
            ds.ending_hour,
            das.classroom,
            dow.name,
            dat.name
        FROM dsi_assignation_schedule AS das
            JOIN dsi_schedule AS ds ON das.schedule_id = ds.id
            JOIN dsi_assistance_type AS dat ON ds.assistance_type_id = dat.id
            JOIN day_of_week AS dow ON ds.week_day = dow.id
        WHERE 
            das.period = {period_id}
            AND das.tutor_id = {tutor_id}
            AND das.project_assignation = {assignation_id}
            AND das.isEnabled = 1;
    """)

def get_assistance_type_select():
    return ("""
        SELECT
            id,
            name
        FROM dsi_assistance_type
        ORDER BY id;
    """)

def get_assistance_class():
    return ("""
        SELECT
            id,
            name
        FROM dsi_assistance_class
        ORDER BY id;
    """)

def get_day_of_week():
    return ("""
        SELECT
            id,
            name
        FROM day_of_week
        ORDER BY id;
    """)

def get_day_of_week_by_id(day_id):
    return (f"""
        SELECT
            id,
            name
        FROM day_of_week
        WHERE id = {day_id};
    """)

def get_tutor_information(tutor_id, period_id):
    return (f"""
        SELECT
            tutor.username,
            tutor.cui,
            tutor.first_name,
            tutor.last_name,
            project.project_id,
            project.name,
            assignation.id,
            assignation.period,
            tutor.id,
            project.id
        FROM auth_user AS tutor
            JOIN user_project AS assignation ON assignation.assigned_user = tutor.id
            JOIN project ON assignation.project = project.id
        WHERE 
            tutor.id = {tutor_id}
            AND assignation.period = {period_id};
    """)


def get_assistance_type(type_id):
    return (f"""
        SELECT
            id,
            name
        FROM dsi_assistance_type
        WHERE id = {type_id};
    """)


def get_specific_schedule(tutor_id, type_id, day_id, period_id):
    return (f"""
        SELECT
            ds.id,
            ds.week_day,
            ds.starting_hour,
            ds.ending_hour,
            ds.assistance_type_id,
            das.tutor_id,
            das.project_assignation
        FROM dsi_assignation_schedule AS das
            JOIN dsi_schedule AS ds ON das.schedule_id = ds.id
        WHERE das.tutor_id = {tutor_id}
            AND das.isEnabled = 1
            AND ds.period = {period_id}
            AND ds.assistance_type_id = {type_id}
            AND ds.week_day = {day_id};
    """)

def get_assistance_parameters_by_id(parameter_id):
    return (f"""
        SELECT
            dap.id,
            dap.name,
            dap.parameter_message,
            dap.percentage,
            dap.range_start,
            dap.range_finish,
            dap.assistance_type,
            dap.assistance_class,
            dat.name, dac.name,
            dap.image
        FROM dsi_assistance_parameter AS dap
            JOIN dsi_assistance_type AS dat ON dap.assistance_type = dat.id
            JOIN dsi_assistance_class AS dac ON dap.assistance_class = dac.id
        WHERE dap.id = {parameter_id}
    """)


def get_assistance_parameters_by_type_id_and_period(assistance_type_id, period_id):
    return (f"""
        SELECT
            dap.id,
            dap.name,
            dap.parameter_message,
            dap.percentage,
            dap.range_start,
            dap.range_finish,
            dap.assistance_type,
            dap.assistance_class,
            dat.name,
            dac.name,
            dap.image
        FROM dsi_assistance_parameter AS dap
            JOIN dsi_assistance_type AS dat ON dap.assistance_type = dat.id
            JOIN dsi_assistance_class AS dac ON dap.assistance_class = dac.id
        WHERE 
            assistance_type = {assistance_type_id}
            AND period = {period_id}
    """)

def get_starting_assistance(tutor_id, type_id, date):
    return (f"""
        SELECT
            da.id,
            da.starting_score,
            da.finishing_score,
            da.schedule,
            da.tutor
        FROM dsi_assistance AS da
            JOIN dsi_schedule AS ds ON da.schedule = ds.id
        WHERE tutor = {tutor_id}
            AND ds.assistance_type_id = {type_id}
            AND CAST(da.starting_hour AS DATE) = '{date}'
            AND finishing_score IS NULL;
    """)

def getAssistanceTypeById(assistance_type_id):
    return (f"""
        SELECT
            id,
            name
        FROM dsi_assistance_type
        WHERE id = {assistance_type_id}
    """)

def get_schedule_by_period_id_and_week_day(period_id, day_id):
    return (f"""
        SELECT
            ds.id,
            ds.week_day,
            ds.starting_hour,
            ds.ending_hour,
            ds.assistance_type_id,
            ds.period,
            dow.id,
            dow.name,
            dat.id,
            dat.name
        FROM dsi_schedule AS ds
            JOIN day_of_week AS dow ON ds.week_day = dow.id
            JOIN dsi_assistance_type AS dat ON ds.assistance_type_id = dat.id
        WHERE ds.period = {period_id}
            AND week_day = {day_id};
    """)


def getScheduleByPeriodAndWeekDayAndType(periodId, dayId, typeId):
    return ("select"
            " ds.id, ds.week_day, ds.starting_hour, ds.ending_hour, ds.assistance_type_id, ds.period, count(1) as quantity"
            " from dsi_schedule as ds"
            " left join dsi_assignation_schedule as das on(ds.id = das.schedule_id)"
            " where ds.period = {}"
            " and ds.assistance_type_id = {}"
            " and ds.week_day = {}"
            " group by ds.id"
            " having quantity < (select tutor_amount from dsi_schedule_parameter where name = 'tutorAmount')"
            "".format(periodId, typeId, dayId))


def get_tutor_quantity_by_schedule_id(schedule_id):
    return (f"""
        SELECT
            ds.id,
            COUNT(1) AS quantity
        FROM dsi_schedule AS ds
            LEFT JOIN dsi_assignation_schedule AS das ON ds.id = das.schedule_id
        WHERE 
            ds.id = {schedule_id}
            AND das.isEnabled = 1
        GROUP BY ds.id
        HAVING quantity >= (
            SELECT tutor_amount 
            FROM dsi_schedule_parameter
            WHERE name = 'tutorAmount'
        );
    """)


def getAssignationStatus():
    return ("select asignation_status from dsi_schedule_parameter where name = 'asignationStatus'")


def callAssignateSchedule(scheduleId, tutorId, classroom, createdAt, createdBy):
    return ("call"
            " assignate_schedule_procedure"
            " ({}, {}, '{}', '{}', '{}')".format(scheduleId, tutorId, classroom, createdAt, createdBy))


def getAssistanceCompleted(tutorId, scheduleId):
    return ("select"
            " id"
            " from dsi_assistance"
            " where tutor = {}"
            " and schedule = {}"
            " and finishing_score is not null;".format(tutorId, scheduleId))

def get_schedule_by_id(schedule_id):
    return (f"""
        SELECT
            ds.id,
            ds.week_day,
            ds.starting_hour,
            ds.ending_hour,
            ds.assistance_type_id,
            ds.period
        FROM dsi_schedule AS ds
        WHERE id = {schedule_id};
    """)

def get_assistance_parameters_by_type_and_class_and_period(type_id, class_id, period_id):
    return (f"""
        SELECT
            dap.id,
            dap.name,
            dap.parameter_message,
            dap.percentage,
            dap.range_start,
            dap.range_finish,
            dap.assistance_type,
            dap.assistance_class,
            dap.image
        FROM dsi_assistance_parameter AS dap
        WHERE assistance_type = {type_id}
            AND assistance_class = {class_id}
            AND dap.period = {period_id};
    """)

def get_finger_prints():
    return ("""
        SELECT
            fp.tutor_id,
            fp.fingerprint
        FROM dsi_fingerprint AS fp
    """)

def get_fingerprint_parameter(parameter):
    return (f"""
        SELECT
            dfp.id,
            dfp.name,
            dfp.parameter_enable,
            dfp.parameter_date
        FROM dsi_fingerprint_parameter AS dfp
        WHERE dfp.name = '{parameter}'
    """)

####################### Deploy 2
def get_exception_courses(period):
    return (f"""
        SELECT
            dsiec.id,
            dsiec.period,
            dsiec.project,
            dsiec.single_hour,
            dsiec.evening,
            p.name,
            p.project_id
        FROM dsi_exception_course AS dsiec
            JOIN project AS p ON dsiec.project = p.id
        WHERE dsiec.period = {period}
    """)

def get_exception_course(project_id, period):
    return (f"""
        SELECT
            dsiec.id,
            dsiec.period,
            dsiec.project,
            dsiec.single_hour,
            dsiec.evening,
            p.name
        FROM dsi_exception_course AS dsiec
            JOIN project AS p ON dsiec.project = p.id
        WHERE dsiec.period = {period} and project = {project_id}
    """)

def get_projects():
    return ("""
        SELECT
            p.id,
            p.project_id,
            p.name,
            p.area_level
        FROM project AS p
    """)


def obtener_horarios_para_asignar(period_id, day_id, type_id, tutor_amount):
    return (f"""
        SELECT
            ds.id,
            ds.week_day,
            ds.starting_hour,
            ds.ending_hour
        FROM dsi_schedule AS ds
        WHERE 
            ds.period = {period_id}
            AND ds.week_day = {day_id}
            AND ds.assistance_type_id = {type_id}
            AND ds.id NOT IN (
                SELECT ds.id
                FROM dsi_assignation_schedule AS das
                    RIGHT JOIN dsi_schedule AS ds ON das.schedule_id = ds.id
                WHERE 
                    ds.period = {period_id}
                    AND ds.week_day = {day_id}
                    AND ds.assistance_type_id = {type_id}
                    AND das.isEnabled = 1
                GROUP BY ds.id
                HAVING COUNT(1) >= {tutor_amount}
            )
        ORDER BY ds.starting_hour ASC;
    """)


def obtener_horarios_para_asignar_laboratorio(period_id, day_id, type_id):
    return (f"""
        SELECT
            ds.id,
            ds.week_day,
            ds.starting_hour,
            ds.ending_hour
        FROM dsi_schedule AS ds
        WHERE 
            ds.period = {period_id}
            AND ds.week_day = {day_id}
            AND ds.assistance_type_id = {type_id}
        ORDER BY ds.starting_hour ASC;
    """)


def get_course_schedule_by_tutor_id_and_day_id(tutor_id, day_id, period_id):
    return (f"""
        SELECT
            dsc.starting_hour,
            dsc.finishing_hour
        FROM dsi_schedule_course AS dsc
        WHERE project_id IN (
                SELECT up.project
                FROM user_project AS up
                WHERE up.period = {period_id}
                    AND up.assigned_user = {tutor_id}
            )
            AND dsc.day_of_week_id = {day_id}
            AND dsc.period = {period_id};
    """)

def get_system_parameter_by_name(period_id, name):
    return (f"""
        SELECT
            dsp.name,
            dsp.period,
            dsp.parameter_number,
            dsp.parameter_date,
            dsp.parameter_bool
        FROM dsi_system_parameters AS dsp
        WHERE 
            dsp.period = {period_id}
            AND dsp.name = '{name}';
    """)


def get_quantity_justifications_by_tutor_and_period(tutor_id, period_id):
    return (f"""
        SELECT
            count(1)
        FROM dsi_justification AS dj
        WHERE 
            dj.requester_user = {tutor_id}
            AND dj.period = {period_id}
            AND dj.description != '';
    """)

def get_quantity_justifications_by_DSI_and_period(period_id):
    return (f"""
        SELECT COUNT(1) 
        FROM dsi_justification AS dj
        WHERE 
            dj.period = {period_id}
            AND dj.description != ''
            AND dj.requester_user IN (
                SELECT user_id
                FROM auth_membership AS am 
                WHERE am.group_id IN (
                        SELECT id
                        FROM auth_group AS ag 
                        WHERE ag.role = 'DSI'
                    ) 
                AND user_id != 1
            );
    """)

def get_holidays(desde, hasta):
    return (f"""
        SELECT dh.holiday_date
        FROM dsi_holiday AS dh
        WHERE 
            enabled = true
            AND dh.holiday_date BETWEEN '{desde}' AND '{hasta}';
    """)


def get_inicio_periodo(period_id):
    return (f"""
        SELECT parameter_date
        FROM dsi_system_parameters
        WHERE
            name = 'inicio_periodo'
            AND period = {period_id};
    """)


def get_fin_periodo(period_id):
    return (f"""
        SELECT parameter_date
        FROM dsi_system_parameters
        WHERE 
            name = 'fin_periodo'
            AND period = {period_id};
    """)


def getAssistanceNoteByPeriodAndTutor(desde, hasta, tutorId):
    return ("select"
            " sum(score)"
            " from dsi_assistance as da"
            " where da.justification is null"
            " and da.created_at between '{}' and '{}'"
            " and da.tutor = {}"
            " and da.starting_hour is not null"
            " and da.finishing_hour is not null;".format(desde, hasta, tutorId))


def getJustificationsByPeriodAndTutor(desde, hasta, tutorId):
    return ("select"
            " count(1)"
            " from dsi_assistance as da"
            " where da.justification is not null and da.created_at between {} and {}"
            " and da.tutor = {};".format(desde, hasta, tutorId))


def getJustificationQuantityByTutor(periodId, tutorId):
    return ("select"
            " count(1)"
            " from dsi_justification as dj"
            " where dj.period = {}"
            " and dj.requester_user = {};".format(periodId, tutorId))


def getSchedulesByTutor(periodId, tutorId):
    return ("select"
            " ds.week_day"
            " from dsi_assignation_schedule as das"
            " join dsi_schedule as ds"
            " on(das.schedule_id = ds.id)"
            " where ds.period = {}"
            " and das.tutor_id = {}"
            " and das.isEnabled = 1;".format(periodId, tutorId))


def getItemAssistanceByPeriodAndTutor(periodId, tutorId):
    return ("select"
            " *"
            " from item as i"
            " join user_project as up"
            " on(i.assignation = up.id)"
            " where i.created = {}"
            " and i.item_restriction = 26"
            " and up.assigned_user = {};".format(periodId, tutorId))


def copy_system_parameters(period_id):
    return (f"""
        INSERT INTO
            dsi_system_parameters(
                name,
                parameter_number,
                parameter_date,
                parameter_bool,
                period
            )
        SELECT
            name,
            parameter_number,
            parameter_date,
            parameter_bool,
            {period_id}
        FROM dsi_system_parameters
        WHERE period = {(period_id - 1)};
    """)

def copy_assistance_parameters(period_id):
    return (f"""
        INSERT INTO
            dsi_assistance_parameter(
                name,
                parameter_message,
                percentage,
                range_start,
                range_finish,
                assistance_class,
                assistance_type,
                period,
                created_by
            )
        SELECT
            name,
            parameter_message,
            percentage,
            range_start,
            range_finish,
            assistance_class,
            assistance_type,
            {period_id},
            'admin'
        FROM dsi_assistance_parameter
        WHERE period = {(period_id - 1)};
    """)

def copy_laboratory_schedule(period_id):
    return (f"""
        INSERT INTO
            cpfecys.dsi_schedule(
                week_day,
                starting_hour,
                ending_hour,
                assistance_type_id,
                created_by,
                period
            )
        SELECT
            week_day,
            starting_hour,
            ending_hour,
            assistance_type_id,
            'admin',
            {period_id}
        FROM cpfecys.dsi_schedule
        WHERE period = {(period_id - 1)};
    """)

def copy_course_schedule(period_id):
    return (f"""
        INSERT INTO
            cpfecys.dsi_schedule_course(
                project_id,
                day_of_week_id,
                starting_hour,
                finishing_hour,
                period
            )
        SELECT
            project_id,
            day_of_week_id,
            starting_hour,
            finishing_hour,
            {period_id}
        FROM cpfecys.dsi_schedule_course
        WHERE period = {(period_id - 1)};
    """)


def get_schedule_by_period_and_week_day_and_type_admin(period_id, type_id, week_day_id):
    return (f"""
        SELECT
            ds.id,
            ds.week_day,
            ds.starting_hour,
            ds.ending_hour,
            ds.assistance_type_id,
            ds.period, 
            COUNT(1) AS quantity
        FROM dsi_schedule AS ds
            LEFT JOIN dsi_assignation_schedule AS das ON ds.id = das.schedule_id
        WHERE 
            ds.period = {period_id} 
            AND ds.assistance_type_id = {type_id}
            AND ds.week_day = {week_day_id}
        GROUP BY ds.id;
    """)


def get_tutor_amount_restriction():
    return ("""
        SELECT tutor_amount 
        FROM dsi_schedule_parameter
        WHERE name = 'tutorAmount';
    """)


def get_asignaciones_por_periodo(period_id):
    return (f"""
        SELECT 
            up.id,
            up.assigned_user,
            up.project
        FROM user_project AS up
        WHERE 
            up.period = {period_id}
            AND up.assignation_status IS NULL
            AND up.id IN (
                SELECT DISTINCT das.project_assignation
                FROM dsi_assignation_schedule AS das
                WHERE das.period = {period_id}
            )
            AND up.project IN (
                SELECT p.id
                FROM project AS p
                where p.area_level = 1
            )
            AND up.assigned_user IN (
	            SELECT user_id 
	            FROM auth_membership AS am
                WHERE am.group_id IN (
                    SELECT id 
                    FROM auth_group AS ag
                    WHERE ag.role = 'Student'
                ) 
	            AND user_id != 1
            );
    """)

def get_schedules_by_asignacion_id(period_id, assignacion_id, is_enabled):
    return (f"""
        SELECT
            ds.week_day,
            das.project_assignation,
            das.tutor_id,
            das.isEnabled,
            das.id,
            ds.id
        FROM dsi_assignation_schedule AS das
            JOIN dsi_schedule AS ds ON das.schedule_id = ds.id
        WHERE 
            das.period = {period_id}
            AND das.project_assignation = {assignacion_id}
            AND das.isEnabled = {is_enabled};
    """)

def get_assistances_by_asignacion(period_id, asignation_id, dates):
    return (f"""
        SELECT
            da.starting_hour,
            da.starting_score,
            da.finishing_hour,
            da.finishing_score,
            da.finishing_hour,
            da.score,
            da.id
        FROM dsi_assistance AS da 
        WHERE 
            da.period = {period_id}
            AND da.asignation_id = {asignation_id}
            AND DATE(da.starting_hour) IN ({dates});
    """)

def existe_justificacion(asignacion, date):
    return(f"""
        SELECT id
        FROM dsi_justification AS dj
        WHERE 
            dj.project = {asignacion}
            AND DATE(dj.absence_date) = {date};
    """)

def getItemAsistanceByAsignationId(asignacionId):
    return( "select i.id from item as i"
            " where i.item_restriction = 26"
            " and i.assignation = {};".format(asignacionId))

def get_justification_status_id(name):
    return (f"""
        SELECT id
        FROM dsi_justification_status
        WHERE name = '{name}';
    """)

def get_asistencia_by_schedule_id(schedule, tutor, asignation):
    return (f"""
        SELECT da.score
        FROM dsi_assistance AS da
        WHERE 
            da.schedule = {schedule}
            AND da.tutor = {tutor}
            AND da.asignation_id = {asignation};
    """)
