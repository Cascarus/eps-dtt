# -*- coding: utf-8 -*-
import cpfecys
import iso_utils
import csv

from datetime import datetime, date
import time

@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator') or auth.has_membership('Academic') or auth.has_membership('Ecys-Administrator'))
def courses_list():
    session.attachment_list = []
    session.attachment_list_temp = []
    session.attachment_list_temp2 = []
    session.notification_subject = ''
    session.notification_message = ''

    area = db(db.area_level.name == 'DTT Tutor Académico').select(db.area_level.id).first()
    courses_admin = None
    courses_student = None
    count_courses_admin_t = 0
    count_courses_student = db.academic_course_assignation.id.count()
    courses_student_t = 0

    #emarquez - adaptacion periodos variables
    courses_admin_anterior = None
    periods_var = []

    ecys_var = True if request.vars['ecys'] == "True" else False

    #emarquez
    periodo = cpfecys.current_year_period()
    periodo_parametro = 0
    if request.vars['period']:
        periodo_parametro = request.vars['period']
        periodo = db(db.period_year.id == periodo_parametro).select().first()

    if auth.has_membership('Academic'):
        academic_var = db.academic(db.academic.id_auth_user == auth.user.id)

    if(auth.has_membership('Super-Administrator') or (auth.has_membership('Ecys-Administrator') & (ecys_var))):
        periods = db(db.period_year).select()
    else:
        periods_temp = db(db.period_year).select(orderby=~db.period_year.id)
        periods = []

        #emarquez
        periods_var = []
        for period_temp in periods_temp:
            added = False
            if auth.has_membership('Student') or auth.has_membership('Teacher'):
                try:
                    #emarquez: se modifica el if para exluir periodos variables
                    if db((db.user_project.assigned_user == auth.user.id) & (db.user_project.period == db.period_year.id) 
                    & (db.user_project.period != db.period_detail.period) & ((db.user_project.period <= period_temp.id) 
                    & ((db.user_project.period + db.user_project.periods) > period_temp.id))).select(db.user_project.id).first() is not None:
                        periods.append(periodo)
                        added = True

                    #emarquez: se agregan los periodos variables
                    if db((db.user_project.assigned_user == auth.user.id) & (db.user_project.period == db.period_year.id) 
                    & (db.user_project.period == period_temp.id) & (db.user_project.period == db.period_detail.period)).select(db.user_project.id).first() is not None:
                        periods_var.append(period_temp)
                except:
                    None

            if auth.has_membership('Academic'):
                try:
                    if db((db.academic_course_assignation.carnet == academic_var.id) & (db.academic_course_assignation.semester == period_temp.id)).select(db.academic_course_assignation.id).first() is not None:
                        if not added:
                            periods.append(period_temp)
                except:
                    None

    def consultar_evaluacion(curso):
        proyecto = curso.project
        asignacion = curso.academic_course_assignation

        query = iso_utils.iso_get_encuesta(auth.user.id, proyecto.id, asignacion.semester)

        encuesta = db.executesql(query)
        completada = True

        for ev in encuesta:
            if ev[8] < ev[7]:
                completada = False

        return {'encuesta': encuesta, 'completada': completada}

    #Check if the period is change
    if request.vars['period'] is not None:
        if request.vars['period'] != '':
            period = request.vars['period']
            period = db(db.period_year.id == period).select().first()
        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    response.view = 'activity_control/courses_list.html'
    if (auth.has_membership('Super-Administrator') or (auth.has_membership('Ecys-Administrator') & (ecys_var))):
        courses_admin = []

        courses = db((db.project.area_level == area.id) & (db.user_project.project == db.project.id)
                & (db.user_project.period == db.period_year.id) & ((db.user_project.period <= periodo.id)
                & ((db.user_project.period + db.user_project.periods) > periodo.id))).select(db.project.ALL, orderby=db.project.name, distinct=True)
    
        for course in courses:
            average_laboratory = float(0)
            average_class = float(0)

            # Average of laboratory and period
            query_lab = "SELECT obtenerPromedio(\'T\', {}, {}) AS promedio;".format(str(course.id), str(periodo.id))
            query_curso = "SELECT obtenerPromedio(\'F\', {}, {}) AS promedio;".format(str(course.id), str(periodo.id))

            avg_lab = db.executesql(query_lab, as_dict=True)
            avg_curso = db.executesql(query_curso, as_dict=True)
            average_laboratory = avg_lab[0]['promedio']
            average_class = avg_curso[0]['promedio']

            if average_laboratory is None: average_laboratory = 0
            if average_class is None: average_class = 0

            courses_admin.append([course.id, course.name, average_class, average_laboratory])
    elif auth.has_membership('Teacher'):
        #emarquez: si es periodo variable
        if (db(db.period_detail.period == periodo.id).select(db.period_detail.id)):
            courses_admin = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.period == db.period_year.id)
                            & (db.user_project.period == period.id) & (db.user_project.project == db.project.id)
                            & (db.project.area_level == area.id)).select()
        else:
            courses_admin = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.period == db.period_year.id)
                            & (db.user_project.period == periodo.id) & (db.user_project.project == db.project.id)
                            & (db.project.area_level == area.id)).select()

            #emarquez: añadir los cursos del semestre anterior que tienen 2 periodos
            #emarquez : paso 1, buscar el curso de semestre anterior
            query_semestre_anterior = "SELECT MAX(id) AS max FROM period_year WHERE id < {} AND id NOT IN (SELECT period FROM period_detail);".format(str(periodo.id))
            semestre_anterior = db.executesql(query_semestre_anterior)

            #Ahora obtener el semestre anterior, seleccionando los que tengan 2 periodos
            courses_admin_anterior =  db((db.user_project.assigned_user == auth.user.id) & (db.user_project.period == db.period_year.id)
                                    & (db.user_project.period == semestre_anterior[0][0]) & (db.user_project.periods == 2) 
                                    & (db.user_project.project == db.project.id) & (db.project.area_level == area.id)).select()

            courses_admin = ((courses_admin) + (courses_admin_anterior)) if len(courses_admin) > 0 else courses_admin_anterior
        #emarquez_ fin nueva forma de obtener cursos tomando en cuenta los periodos variables
    elif auth.has_membership('Student'):
        courses_admin = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.period == db.period_year.id)
                        & ((db.user_project.period <= periodo.id) & ((db.user_project.period + db.user_project.periods) > periodo.id))
                        & (db.user_project.project == db.project.id) & (db.project.area_level == area.id)).select()
        count_courses_admin_t = len(courses_admin)

        (courses_student, courses_student_t) = academic_and_student_courses(periodo, count_courses_student, area)
    elif auth.has_membership('Academic'):
        (courses_student, courses_student_t) = academic_and_student_courses(periodo, count_courses_student, area)
    else:
        session.flash = T('Not valid Action.')
        redirect(URL('default','home'))

    visited = db((db.page_visited.user_id == auth.user.id) & (db.page_visited.page_name == 'courses_list')).select().first()

    return dict(
        visited=visited, 
        coursesAdmin=courses_admin,
        countcoursesAdminT=count_courses_admin_t,
        coursesStudent=courses_student,
        coursesStudentT=courses_student_t,
        split_name=split_name, 
        split_section=split_section,
        consultar_evaluacion=consultar_evaluacion,
        periods=periods, 
        period=periodo, 
        periodo=periodo,
        periodo_year=db(db.period_year).select(),
        currentyear_period=cpfecys.current_year_period(),
        ecys_var=ecys_var,
        periods_var=periods_var,
        period_all=db(db.period).select(),
        coursesAdminAnterior=courses_admin_anterior,
        period_detail=db(db.period_detail).select(),
        periodo_parametro=periodo_parametro
    )

@auth.requires(auth.has_membership('Student') or auth.has_membership('Academic') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def students_control():
    #vars
    year = None
    project_var = None

    #Check if the period is correct
    if request.vars['period'] is None or request.vars['period'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        year = request.vars['period']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    project_var = request.vars['project']
    project_select = db(db.project.id == project_var).select().first()

    assigned_to_project = False
    assigantion = None

    if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator'):
        try:
            assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project_var)
                            & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
            if assigantion is None:
                academic_var = db(db.academic.carnet==auth.user.username).select().first()
                try:
                    academic_assig = db((db.academic_course_assignation.carnet == academic_var.id) & (db.academic_course_assignation.semester == year.id) 
                                        & (db.academic_course_assignation.assignation==project_var) ).select().first()

                    if academic_assig is None:
                        session.flash = T('Not valid Action.')
                        redirect(URL('default','home'))
                except:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default','home'))
            else:
                assigned_to_project = True
        except:
            session.flash=T('Not valid Action.')
            redirect(URL('default','home'))

    visited = db((db.page_visited.user_id == auth.user.id) & (db.page_visited.page_name == 'students_control')).select().first()

    return dict(
        project = project_var, 
        year = year.id , 
        name = project_select.name, 
        nameP = (T(year.period.name) + " " + str(year.yearp)),
        assigned_to_project = assigned_to_project, 
        visited = visited
    )

@auth.requires_login()
def control_weighting():
    year = db(db.period_year.id == request.vars['year']).select().first()
    year_semester = year.period

    #emarquez: adaptacion periodos variables
    if cpfecys.is_semestre(request.vars['year']):
        assigantion = db((db.user_project.assigned_user==auth.user.id) & (db.user_project.project == request.vars['project'])
                        & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
    else:
        assigantion = db((db.user_project.assigned_user==auth.user.id) & (db.user_project.project == request.vars['project'])).select(db.user_project.ALL).first()
    #emarquez
    
    assigned_to_project = False if assigantion is None else True    
    check = db(db.project.id == request.vars['project']).select().first()

    return dict(
        name = check.name,
        semester = year_semester.name,
        year = year.yearp,
        semestre2 = year,
        project = request.vars['project'],
        assigned_to_project = assigned_to_project
    )

@auth.requires_login()
def control_activity():
    year = db(db.period_year.id == request.vars['year']).select().first()
    year_semester = year.period
    project = db(db.project.id == request.vars['project']).select().first()

    if cpfecys.is_semestre(request.vars['year']):
        assigantion = db((db.user_project.assigned_user==auth.user.id) & (db.user_project.project == project.id)
                        & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
    else:
        assigantion = db((db.user_project.assigned_user==auth.user.id) & (db.user_project.project == request.vars['project'])).select(db.user_project.ALL).first()

    assigned_to_project = False if assigantion is None else True

    return dict(
        semester = year_semester.name,
        year = year.yearp,
        semestre2 = year,
        project = project,
        type = request.vars['type'],
        assigned_to_project = assigned_to_project
    )

@auth.requires_login()
def activity():
    #Obteners la asignacion del estudiante
    project = request.vars['project']
    typ = request.vars['type']

    #emarquez: adaptacion periodos variables
    year = db(db.period_year.id == request.vars['year']).select().first()

    if cpfecys.is_semestre(request.vars['year']):        
        assigantion = db((db.user_project.assigned_user==auth.user.id) & (db.user_project.project == project)
                        & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
    else:
        assigantion = db((db.user_project.assigned_user==auth.user.id) & (db.user_project.project == request.vars['project'])).select(db.user_project.ALL).first()

    #emarquez: fin adaptacion
    assigned_to_project = False if assigantion is None else True

    return dict(
        semestre2 = year, 
        project = project, 
        type = typ, 
        assigned_to_project = assigned_to_project
    )

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator') or auth.has_membership('Academic') or auth.has_membership('Ecys-Administrator'))
def general_report_activities():
    #vars
    action_export = False
    year = None
    project_var = None

    #Check if the period is correct
    if request.vars['period'] is None or request.vars['period'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default','home'))
    else:
        year = request.vars['period']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default','home'))

    #Check if the period is correct
    if request.vars['project'] is None or request.vars['project'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default','home'))
    else:
        project_var = request.vars['project']
        project_var = db(db.project.id == project_var).select().first()
        if project_var is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default','home'))

    #Check the correct parameters
    if (request.vars['type'] != 'class' and request.vars['type'] != 'lab'):
        session.flash = T('Not valid Action.')
        redirect(URL('default','home'))

    tutor_access = False
    if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator'):
        if cpfecys.is_semestre(request.vars['period']):
            assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project_var.id)
                            & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
        else:
            assigantion = db((db.user_project.assigned_user==auth.user.id) & (db.user_project.project == project_var.id)
                            & (db.user_project.period == year.id)).select(db.user_project.ALL).first()

        if assigantion is None:
            try:
                academic_var = db(db.academic.carnet==auth.user.username).select().first()
                academic_assig = db((db.academic_course_assignation.carnet == academic_var.id) & (db.academic_course_assignation.semester == year.id) 
                                    & (db.academic_course_assignation.assignation == project_var.id)).select().first()
                if academic_assig is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default','home'))
            except:
                session.flash = T('Not valid Action.')
                redirect(URL('default','home'))
        else:
            tutor_access = True

    exception_query = db(db.course_laboratory_exception.project == project_var.id).select().first()
    exception_s_var = False
    exception_t_var = False
    if exception_query is not None:
        exception_t_var = exception_query.t_edit_lab
        exception_s_var = exception_query.s_edit_course

    if cpfecys.is_semestre(request.vars['period']):
        teacher = db(((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))
                    & (db.user_project.project == project_var.id) & (db.user_project.assigned_user==db.auth_user.id)
                    & (db.auth_user.id==db.auth_membership.user_id) & (db.auth_membership.group_id==3)).select(db.auth_user.first_name, db.auth_user.last_name).first()    

        practice = db(((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))
                    & (db.user_project.project == project_var.id) & (db.user_project.assigned_user == db.auth_user.id)
                    & (db.auth_user.id == db.auth_membership.user_id) & (db.auth_membership.group_id == 2)).select(db.auth_user.first_name, db.auth_user.last_name)
    else:
        teacher = db((db.user_project.period == year.id) & (db.user_project.project == project_var.id) 
                    & (db.user_project.assigned_user==db.auth_user.id) & (db.auth_user.id==db.auth_membership.user_id)
                    & (db.auth_membership.group_id==3)).select(db.auth_user.first_name, db.auth_user.last_name).first()    
        
        practice = db((db.user_project.period == year.id) & (db.user_project.project == project_var.id) 
                    & (db.user_project.assigned_user==db.auth_user.id) & (db.auth_user.id==db.auth_membership.user_id)
                    & (db.auth_membership.group_id==2)).select(db.auth_user.first_name, db.auth_user.last_name)

    if request.vars['type'] == 'class':
        academic_assig = db((db.academic.id==db.academic_course_assignation.carnet) & (db.academic_course_assignation.semester == year.id) 
                            & (db.academic_course_assignation.assignation == project_var.id)).select(orderby = db.academic.carnet)
    else:
        academic_assig = db((db.academic.id==db.academic_course_assignation.carnet) & (db.academic_course_assignation.semester == year.id) 
                            & (db.academic_course_assignation.assignation == project_var.id) & (db.academic_course_assignation.laboratorio == True)).select(orderby=db.academic.carnet)

    students = []
    for aca_t in academic_assig:
        students.append(aca_t.academic_course_assignation)

    var_final_grade = 0.00
    exist_lab = False
    total_lab = float(0)
    total_w = float(0)
    cat_course_temp = None
    cat_vec_course_temp = []
    course_activities = []
    course_category = db((db.course_activity_category.semester==year.id) & (db.course_activity_category.assignation==project_var.id)
                        & (db.course_activity_category.laboratory==False)).select()

    for category_c in course_category:
        total_w = total_w + float(category_c.grade)
        if category_c.category.category == "Laboratorio":
            exist_lab = True
            total_lab = float(category_c.grade)
            cat_vec_course_temp.append(category_c)
        elif category_c.category.category == "Examen Final":
            var_final_grade = category_c.grade
            if (request.vars['op'] != '2' and request.vars['op'] != '3'):
                cat_course_temp = category_c
        else:
            cat_vec_course_temp.append(category_c)
            course_activities.append(db((db.course_activity.semester == year.id) & (db.course_activity.assignation == project_var.id)
                                        & (db.course_activity.laboratory == False) & (db.course_activity.course_activity_category == category_c.id)).select())
    if cat_course_temp != None:
        cat_vec_course_temp.append(cat_course_temp)
        course_activities.append(db((db.course_activity.semester == year.id) & (db.course_activity.assignation == project_var.id)
                                    & (db.course_activity.laboratory == False) & (db.course_activity.course_activity_category == cat_course_temp.id)).select())
    course_category = cat_vec_course_temp

    if request.vars['type'] == 'class':
        if total_w != float(100):
            session.flash = T('Can not find the correct weighting defined in the course. You can not use this function')
            redirect(URL('activity_control','students_control', vars = dict(period=request.vars['period'], project=request.vars['project'])))

    total_w = float(0)
    lab_category = None
    cat_lab_temp = None
    cat_vec_lab_temp = []
    lab_activities = None
    validate_laboratory = None
    if exist_lab or request.vars['type'] == 'lab':
        lab_activities = []
        validate_laboratory = db((db.validate_laboratory.semester == year.id) & (db.validate_laboratory.project == project_var.id)).select()
        lab_category = db((db.course_activity_category.semester == year.id) & (db.course_activity_category.assignation == project_var.id)
                          & (db.course_activity_category.laboratory == True)).select()
        
        for category_l in lab_category:
            if category_l.category.category == "Examen Final":
                total_w = total_w + float(category_l.grade)
                cat_lab_temp = category_l
            else:
                cat_vec_lab_temp.append(category_l)
                total_w = total_w + float(category_l.grade)
                lab_activities.append(db((db.course_activity.semester == year.id) & (db.course_activity.assignation==project_var.id)
                                         & (db.course_activity.laboratory==True) & (db.course_activity.course_activity_category == category_l.id)).select())
        if cat_lab_temp != None:
            cat_vec_lab_temp.append(cat_lab_temp)
            lab_activities.append(db((db.course_activity.semester == year.id) & (db.course_activity.assignation == project_var.id)
                                     & (db.course_activity.laboratory == True) & (db.course_activity.course_activity_category == cat_lab_temp.id)).select())
        lab_category = cat_vec_lab_temp

        if total_w != float(100):
            session.flash = T('Can not find the correct weighting defined in the laboratory. You can not use this function')
            redirect(URL('activity_control','students_control', vars = dict(period=request.vars['period'], project=request.vars['project'])))

    #Enable the course
    if request.vars['list'] == 'cancel':
        if (auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator')):
            course_ended_var = db((db.course_ended.project == project_var.id) & (db.course_ended.period == year.id)).select().first()
            if course_ended_var != None:
                if course_ended_var.finish:
                    db((db.course_ended.project == project_var.id) & (db.course_ended.period == year.id)).delete()
                    response.flash= T('Course has been enabled')

    #Export to CSV general activity report
    if request.vars['list'] == 'True':
        if (request.vars['op'] is None) or (request.vars['op'] == '') or (request.vars['op']  == '1') or (request.vars['op']  == '0'):
            redirect(URL('activity_control', 'general_report_activities_export', vars=dict(project=project_var.id, period=year.id, type=request.vars['type'], op=1)))
        elif request.vars['op'] == '2':
            redirect(URL('activity_control','general_report_activities_export', vars=dict(project=project_var.id, period=year.id, type=request.vars['type'], op=2)))
        elif request.vars['op'] == '3':
            redirect(URL('activity_control','general_report_activities_export', vars=dict(project=project_var.id, period=year.id, type=request.vars['type'], op=3)))
        else:
            redirect(URL('activity_control','general_report_activities', vars=dict(project=project_var.id, period=year.id, type=request.vars['type'])))

    #Finish the course and generate the csv file format technical school
    if request.vars['list'] == 'False':
        if request.vars['type'] == 'class' and (auth.has_membership('Ecys-Administrator') or auth.has_membership('Super-Administrator') or auth.has_membership('Teacher') or (auth.has_membership('Student') and exception_s_var and tutor_access)):
            course_ended_var = db((db.course_ended.project == project_var.id) & (db.course_ended.period == year.id)).select().first()
            if course_ended_var is None:

                #ROL FOR LOG
                nombre_rol = get_rol()

                #GRADES CHANGE REQUEST
                request_change = db((db.request_change_grades.status == 'pending') & (db.request_change_grades.period == int(year.id)) 
                                    & (db.request_change_grades.project == int(project_var.id))).select()
                
                for change in request_change:
                    db(db.request_change_grades.id == change.id).update(
                        status = 'rejected',
                        resolve_user = auth.user.id,
                        roll_resolve =  nombre_rol,
                        date_request_resolve = str(datetime.now())
                    )

                    #---------------------------------LOG-----------------------------------------------
                    temp2 = db(db.request_change_g_log.r_c_g_id == change.id).select().first()

                    temp3 = db.request_change_g_log.insert(
                                r_c_g_id=change.id,
                                username=temp2.username,
                                roll=temp2.roll,
                                before_status='pending',
                                after_status='rejected',
                                description=temp2.description,
                                semester=temp2.semester,
                                yearp=temp2.yearp,
                                project=temp2.project,
                                category=temp2.activity,
                                activity=temp2.category,
                                resolve_user=auth.user.username,
                                roll_resolve=nombre_rol,
                                date_request=temp2.date_request,
                                date_request_resolve=str(datetime.now())
                            )
                    for var_chang_ins in db((db.request_change_grades_detail.request_change_grades == change.id)).select():
                        db.request_change_grade_d_log.insert(
                            request_change_g_log=temp3,
                            operation_request=var_chang_ins.operation_request,
                            academic=var_chang_ins.academic_assignation.carnet.carnet,
                            after_grade=var_chang_ins.after_grade,
                            before_grade=var_chang_ins.before_grade
                        )

                #Weighting CHANGE REQUEST
                request_change = db((db.request_change_weighting.status == 'pending') & (db.request_change_weighting.period == int(year.id))
                                    & (db.request_change_weighting.project == int(project_var.id))).select()
                for change in request_change:
                    db(db.request_change_weighting.id == change.id).update(
                        status = 'rejected',
                        resolve_user = auth.user.id,
                        roll_resolve =  nombre_rol,
                        date_request_resolve = str(datetime.now())
                    )
                    temp2 = db(db.request_change_w_log.r_c_w_id == change.id).select().first()
                    temp3 = db.request_change_w_log.insert(
                        r_c_w_id=change.id,
                        username=temp2.username,
                        roll=temp2.roll,
                        before_status='pending',
                        after_status='rejected',
                        description=temp2.description,
                        semester=temp2.semester,
                        yearp=temp2.yearp,
                        project=temp2.project,
                        resolve_user=auth.user.username,
                        roll_resolve=nombre_rol,
                        date_request=temp2.date_request,
                        date_request_resolve=str(datetime.now())
                    )
                    temp4 = db(db.request_change_weighting.id == change.id).select().first()

                    for var_chang_ins in db((db.request_change_weighting_detail.request_change_weighting ==  temp4.id) & (db.request_change_weighting_detail.operation_request == 'insert')).select():
                        if var_chang_ins.operation_request == 'insert':
                            db.request_change_w_detail_log.insert(
                                request_change_w_log=temp3,
                                operation_request=var_chang_ins.operation_request,
                                category=var_chang_ins.category.category,
                                after_grade=var_chang_ins.grade,
                                after_specific_grade=var_chang_ins.specific_grade
                            )

                    for categories in db((db.course_activity_category.semester == int(temp4.period)) & (db.course_activity_category.assignation == temp4.project) 
                                         & (db.course_activity_category.laboratory==True)).select():
                        var_chang = db(db.request_change_weighting_detail.course_category == str(categories.id)).select().first()
                        if var_chang != None:
                            if var_chang.operation_request == 'delete':
                                cat_temp = db(db.course_activity_category.id == var_chang.course_category).select().first()

                                temp44 = db(db.request_change_w_log.id == str(temp3) ).select().first()
                                db.request_change_w_detail_log.insert(
                                    request_change_w_log = str(temp3),
                                    operation_request = str(var_chang.operation_request),
                                    course_category = str(cat_temp.category.category),
                                    before_grade = str(cat_temp.grade),
                                    before_specific_grade = str(cat_temp.specific_grade) 
                                )
                            if var_chang.operation_request == 'update':
                                cat_temp = db(db.course_activity_category.id == var_chang.course_category).select().first()
                                cat_temp2 = db(db.activity_category.id == var_chang.category).select().first()

                                db.request_change_w_detail_log.insert(
                                    request_change_w_log=temp3,
                                    operation_request=var_chang.operation_request,
                                    course_category=cat_temp.category.category,
                                    category=cat_temp2.category,
                                    before_grade=cat_temp.grade,
                                    after_specific_grade=var_chang.specific_grade,
                                    after_grade=var_chang.grade,
                                    before_specific_grade=cat_temp.specific_grade
                                )
                            db(db.request_change_weighting_detail.id == var_chang.id).update(course_category = None)
                        else:
                            add_to_log = True
                            for req_c_w_d_l in db(db.request_change_w_detail_log.request_change_w_log == temp3).select():
                                if categories.category.category == req_c_w_d_l.category:
                                    add_to_log = False

                            if add_to_log:
                                db.request_change_w_detail_log.insert(
                                    request_change_w_log=temp3,
                                    operation_request='none',
                                    category=categories.category.category,
                                    after_grade=categories.grade,
                                    after_specific_grade=categories.specific_grade
                                )

                #Weighting CHANGE REQUEST
                request_change = db((db.requestchange_activity.status == 'Pending') & (db.requestchange_activity.semester == int(year.id))
                                    & (db.requestchange_activity.course == int(project_var.id))).select()
                for change in request_change:
                    rol_temp = nombre_rol

                    db(db.requestchange_activity.id == int(change.id)).update(status='Rejected', user_resolve=auth.user.id, roll_resolve=rol_temp, date_request_resolve=datetime.now())
                    #Log of request change activity
                    rejected = db(db.requestchange_activity.id == int(change.id)).select().first()
                    if rejected is not None:
                        id_rejected = db.requestchange_activity_log.insert(
                                    user_request=rejected.user_id.username,
                                    roll_request=rejected.roll, status='Rejected',
                                    user_resolve=rejected.user_resolve.username,
                                    roll_resolve=rejected.roll_resolve,
                                    description=rejected.description,
                                    date_request=rejected.date_request,
                                    date_request_resolve=rejected.date_request_resolve,
                                    category_request=rejected.course_activity_category.category.category,
                                    semester=rejected.semester.period.name,
                                    yearp=rejected.semester.yearp,
                                    course=rejected.course.name
                                )
                        activities_change = db(db.requestchange_course_activity.requestchange_activity == rejected.id).select()
                        for act_chang in activities_change:
                            db.requestchange_course_activity_log.insert(
                                requestchange_activity=id_rejected,
                                operation_request=act_chang.operation_request,
                                activity=act_chang.activity,
                                name=act_chang.name,
                                description=act_chang.description,
                                grade=act_chang.grade,
                                date_start=act_chang.date_start,
                                date_finish=act_chang.date_finish
                            )

                #Insert to course_ended
                db.course_ended.insert(project=project_var.id, period=year.id, finish=True)

                #Generate csv file format technical school
                action_export = True
            else:
                #Generate csv file format technical school
                if (request.vars['op'] is None) or (request.vars['op'] == '') or (request.vars['op'] == '1') or (request.vars['op'] == '0'):
                    redirect(URL('activity_control','course_format_technical_school',vars=dict(project = project_var.id, period = year.id, type=request.vars['type'], op=1)))
                elif request.vars['op']  == '2':
                    redirect(URL('activity_control','course_format_technical_school',vars=dict(project = project_var.id, period = year.id, type=request.vars['type'], op=2)))
                elif request.vars['op']  == '3':
                    redirect(URL('activity_control','course_format_technical_school',vars=dict(project = project_var.id, period = year.id, type=request.vars['type'], op=3)))
                else:
                    redirect(URL('activity_control','general_report_activites',vars=dict(project = project_var.id, period = year.id, type=request.vars['type'])))
        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default','home'))

    if cpfecys.is_semestre(request.vars['period']):             
        control_p = db((db.student_control_period.period_name == (T(year.period.name) + " " + str(year.yearp)))).select().first()
    else:
        actual_semester = db(db.period_year.id == year.id).select().first()
        control_p = db((db.period_detail.period == actual_semester.period)).select().first()

    requirement = db((db.course_requirement.semester == year.id) & (db.course_requirement.project == project_var.id)).select().first()

    course_ended = False
    course_ended_var = db((db.course_ended.project == project_var.id) & (db.course_ended.period == year.id)).select().first()
    if course_ended_var != None:
        if course_ended_var.finish:
            course_ended = True

    if request.vars['op'] == '0':
        response.flash = T('Course hasn’t finalized.')

    return dict(
                project = project_var,
                year = year,
                teacher=teacher,
                practice=practice,
                students=students,
                CourseCategory=course_category,
                CourseActivities=course_activities,
                existLab=exist_lab,
                LabCategory=lab_category,
                LabActivities=lab_activities,
                validateLaboratory=validate_laboratory,
                totalLab=total_lab,
                controlP=control_p,
                var_final_grade = var_final_grade,
                requirement=requirement,
                course_ended = course_ended,
                exception_s_var=exception_s_var,
                exception_t_var=exception_t_var,
                tutor_access = tutor_access,
                action_Export=action_export
            )

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def course_format_technical_school():
    #vars
    year = None
    project_var = None

    #Check if the period is correct
    if request.vars['period'] is None or request.vars['period'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default','home'))
    else:
        year = request.vars['period']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default','home'))

    #Check if the period is correct
    if request.vars['project'] is None or request.vars['project'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default','home'))
    else:
        project_var = request.vars['project']
        project_var = db(db.project.id == project_var).select().first()
        if project_var is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default','home'))

    if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator'):
        assigantion = db((db.user_project.assigned_user==auth.user.id) & (db.user_project.project == project_var.id)
                        & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
        if assigantion is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default','home'))
        else:
            if auth.has_membership('Student'):
                exception_query = db(db.course_laboratory_exception.project == project_var.id).select().first()
                if exception_query is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default','home'))
                else:
                    if not exception_query.s_edit_course:
                        session.flash = T('Not valid Action.')
                        redirect(URL('default','home'))

    #Check the correct parameters
    if (request.vars['op'] != '1' and request.vars['op'] != '2' and request.vars['op'] != '3'):
        session.flash = T('Not valid Action.')
        redirect(URL('default','home'))

    #Students
    academic_assig3 = db((db.academic.id == db.academic_course_assignation.carnet) & (db.academic_course_assignation.semester == year.id) 
                        & (db.academic_course_assignation.assignation == project_var.id)).select(orderby=db.academic.carnet)
    students = []
    for aca_t in academic_assig3:
        students.append(aca_t.academic_course_assignation)

    var_final_grade = 0.00
    exist_lab = False
    total_lab = float(0)
    total_w = float(0)
    cat_course_temp = None 
    cat_vec_course_temp = []
    course_activities = []
    course_category = db((db.course_activity_category.semester == year.id) & (db.course_activity_category.assignation == project_var.id)
                        & (db.course_activity_category.laboratory == False)).select()

    for category_c in course_category:
        total_w = total_w + float(category_c.grade)
        if category_c.category.category == "Laboratorio":
            exist_lab = True
            total_lab = float(category_c.grade)
            cat_vec_course_temp.append(category_c)
        elif category_c.category.category == "Examen Final":
            var_final_grade = category_c.grade
            if (request.vars['op'] != '2' and request.vars['op'] != '3'):
                cat_course_temp = category_c
        else:
            cat_vec_course_temp.append(category_c)
            course_activities.append(db((db.course_activity.semester == year.id) & (db.course_activity.assignation == project_var.id)
                                        & (db.course_activity.laboratory == False) & (db.course_activity.course_activity_category == category_c.id)).select())
    if cat_course_temp != None:
        cat_vec_course_temp.append(cat_course_temp)
        course_activities.append(db((db.course_activity.semester == year.id) & (db.course_activity.assignation == project_var.id)
                                    & (db.course_activity.laboratory == False) & (db.course_activity.course_activity_category == cat_course_temp.id)).select())
    course_category = cat_vec_course_temp

    if total_w != float(100):
        session.flash= T('Can not find the correct weighting defined in the course. You can not use this function')
        redirect(URL('activity_control','students_control', vars=dict(period=request.vars['period'], project=request.vars['project']) ))

    total_w = float(0)
    lab_category = None
    cat_lab_temp = None
    cat_vec_lab_temp = []
    lab_activities = None
    validate_laboratory = None
    if exist_lab:
        lab_activities = []
        validate_laboratory = db((db.validate_laboratory.semester == year.id) & (db.validate_laboratory.project == project_var.id)).select()
        lab_category = db((db.course_activity_category.semester == year.id) & (db.course_activity_category.assignation == project_var.id)
                          & (db.course_activity_category.laboratory == True)).select()
        for category_l in lab_category:
            if category_l.category.category == "Examen Final":
                total_w = total_w + float(category_l.grade)
                cat_lab_temp = category_l
            else:
                cat_vec_lab_temp.append(category_l)
                total_w = total_w + float(category_l.grade)
                lab_activities.append(db((db.course_activity.semester == year.id) & (db.course_activity.assignation == project_var.id)
                                         & (db.course_activity.laboratory == True) & (db.course_activity.course_activity_category == category_l.id)).select())
        if cat_lab_temp != None:
            cat_vec_lab_temp.append(cat_lab_temp)
            lab_activities.append(db((db.course_activity.semester == year.id) & (db.course_activity.assignation == project_var.id)
                                     & (db.course_activity.laboratory == True) & (db.course_activity.course_activity_category == cat_lab_temp.id)).select())
        lab_category = cat_vec_lab_temp

        if total_w != float(100):
            session.flash= T('Can not find the correct weighting defined in the laboratory. You can not use this function')
            redirect(URL('activity_control','students_control', vars = dict(period=request.vars['period'], project=request.vars['project'])))

    requirement = db((db.course_requirement.semester == year.id) & (db.course_requirement.project == project_var.id)).select().first()

    l = []
    t = []
    t.append(T('Carnet'))
    t.append(T('Name'))
    t.append(T('Laboratory'))
    t.append('Zona')
    if request.vars['op'] == '1':
        t.append('Final')
    elif request.vars['op'] == '2':
        t.append(T("First recovery test"))
    elif request.vars['op'] == '3':
        t.append(T("Second recovery test"))
    l.append(t)

    t = []
    for t1 in students:
        t = []
        t.append(str(t1.carnet.carnet))
        try:
            var_auth_user = db((db.auth_user.id == t1.carnet.id_auth_user)).select().first()
            t.append(str(var_auth_user.first_name) + " " + str(var_auth_user.last_name))
        except:
            t.append("")
            
        #Position in the vector of activities-
        pos_vcc = 0

        #Vars to the control of grade of the student
        total_category = float(0)
        total_activities = 0
        total_lab_final = 0
        total_final_clase = 0
        total_carry = float(0)
        #<!--****************************************FILL THE GRADES OF THE STUDENT****************************************-->
        #<!--LABORATORY ACTIVITIES-->
        if exist_lab:
            total_category = float(0)
            is_validate = False
            #<!--Revalidation of laboratory-->
            for validate in validate_laboratory:
                if validate.carnet == t1.carnet:
                    is_validate = True
                    #<!--Show grade of laboratory-->
                    total_lab_final = int(round(validate.grade, 0))
                    if not validate.validation_type:
                        t.append(str(total_lab_final))
                    else:
                        t.append('')

                    total_category = float((total_lab_final * total_lab) / 100)

            #<!--Doesnt has a revalidation-->
            if not is_validate:
                #<!--Position in the vector of activities-->
                pos_vcc_lab = 0

                #<!--Vars to the control of grade of the student-->
                total_category_lab = float(0)
                total_activities_lab = 0
                total_carry_lab = float(0)

                #<!--****************************************FILL THE GRADES OF THE STUDENT****************************************-->
                #<!--LAB ACTIVITIES-->
                for category_Lab in lab_category:
                    total_category_lab = float(0)
                    total_activities_lab = 0
                    for c_Lab in lab_activities[pos_vcc_lab]:
                        student_grade = db((db.grades.activity == c_Lab.id) & (db.grades.academic_assignation == t1.id)).select().first()
                        if student_grade is None:
                            total_category_lab = total_category_lab + float(0)
                        else:
                            if category_Lab.specific_grade:
                                total_category_lab = total_category_lab + float((student_grade.grade * c_Lab.grade) / 100)
                            else:
                                total_category_lab = total_category_lab + float(student_grade.grade)
                        total_activities_lab = total_activities_lab + 1

                    if not category_Lab.specific_grade:
                        if total_activities_lab == 0:
                            total_activities_lab = 1
                        
                        total_activities_lab = total_activities_lab * 100
                        total_category_lab = float((total_category_lab * float(category_Lab.grade)) / float(total_activities_lab))
                    
                    total_carry_lab = total_carry_lab + total_category_lab
                    pos_vcc_lab = pos_vcc_lab + 1
                #<!--Show grade of laboratory-->
                total_lab_final = int(round(total_carry_lab, 0))
                t.append(str(total_lab_final))
                total_category = float((total_lab_final * total_lab) / 100)

            #<!--Plus the laboratory to the carry-->
            total_carry = total_carry + total_category
        else:
            #<!--Show grade of laboratory-->
            t.append('0')

        #<!--COURSE ACTIVITIES-->
        for category in course_category:
            if category.category.category != "Laboratorio" and category.category.category != "Examen Final":
                total_category = float(0)
                total_activities = 0
                for c in course_activities[pos_vcc]:
                    student_grade = db((db.grades.activity == c.id) & (db.grades.academic_assignation == t1.id)).select().first()
                    if student_grade is None:
                        total_category = total_category + float(0)
                    else:
                        if category.specific_grade:
                            total_category = total_category + float((student_grade.grade * c.grade) / 100)
                        else:
                            total_category = total_category + float(student_grade.grade)
                    total_activities = total_activities + 1

                if not category.specific_grade:
                    if total_activities == 0:
                        total_activities = 1
                
                    total_activities = total_activities * 100
                    total_category = float((total_category * float(category.grade)) / float(total_activities))
                
                total_carry = total_carry + total_category
                pos_vcc = pos_vcc + 1
            elif category.category.category == "Examen Final":
                total_category = float(0)
                total_activities = 0
                for c in course_activities[pos_vcc]:
                    student_grade = db((db.grades.activity == c.id) & (db.grades.academic_assignation == t1.id)).select().first()
                    if student_grade is None:
                        total_category = total_category + float(0)
                    else:
                        if category.specific_grade:
                            total_category = total_category + float((student_grade.grade * c.grade) / 100)
                        else:
                            total_category = total_category + float(student_grade.grade)
                    total_activities = total_activities + 1

                if not category.specific_grade:
                    if total_activities == 0:
                        total_activities = 1
                    total_activities = total_activities * 100
                    total_category = float((total_category * float(category.grade)) / float(total_activities))
                total_final_clase = int(round(total_category, 0))
                pos_vcc = pos_vcc + 1
        total_carry = int(round(total_carry, 0))

        if request.vars['type'] == 'class' and request.vars['op'] == '2':
                var_first_recovery_test = db((db.course_first_recovery_test.carnet == t1.carnet) & (db.course_first_recovery_test.semester == year.id)
                                            & (db.course_first_recovery_test.project == project_var.id)).select().first()
                if var_first_recovery_test is not None:
                    total_final_clase = int(round((var_first_recovery_test.grade) * var_final_grade / 100, 0))
                else:
                    total_final_clase = int(0)

        if request.vars['type'] == 'class' and request.vars['op'] == '3':
                var_second_recovery_test = db((db.course_second_recovery_test.carnet == t1.carnet) & (db.course_second_recovery_test.semester == year.id)
                                            & (db.course_second_recovery_test.project == project_var.id)).select().first()
                if var_second_recovery_test is not None:
                    total_final_clase = int(round((var_second_recovery_test.grade) * var_final_grade / 100, 0))
                else:
                    total_final_clase = int(0)

        if requirement is not None:
            if db((db.course_requirement_student.carnet == t1.carnet) & (db.course_requirement_student.requirement == requirement.id)).select().first() is not None:
                if exist_lab:
                    if total_lab_final >= 61:
                        t.append(str(total_carry))
                        t.append(str(total_final_clase))
                    else:
                        t.append('0')
                        t.append('0')
                else:
                    t.append(str(total_carry))
                    t.append(str(total_final_clase))
            else:
                t.append('0')
                t.append('0')
        else:
            if exist_lab:
                if total_lab_final >= 61:
                    t.append(str(total_carry))
                    t.append(str(total_final_clase))
                else:
                    t.append('0')
                    t.append('0')
            else:
                t.append(str(total_carry))
                t.append(str(total_final_clase))

        l.append(t)

    nombre = project_var.name.replace(' ','_') + '_' + T(year.period.name).replace(' ','_') + str(year.yearp)
    return dict(
        filename=nombre, 
        csvdata=l
    )

@auth.requires_login()
@auth.requires(auth.has_membership('Academic') or auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def general_report_activities_export():
    #vars
    year = None
    project_var = None

    #Check if the period is correct
    if request.vars['period'] is None or request.vars['period'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        year = request.vars['period']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default','home'))

    #Check if the period is correct
    if request.vars['project'] is None or request.vars['project'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        project_var = request.vars['project']
        project_var = db(db.project.id == project_var).select().first()
        if project_var is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator'):
        assigantion = db((db.user_project.assigned_user==auth.user.id) & (db.user_project.project == project_var.id)
                        & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
        if assigantion is None:
            try:
                academic_var = db(db.academic.carnet==auth.user.username).select().first()
                academic_assig = db((db.academic_course_assignation.carnet == academic_var.id) & (db.academic_course_assignation.semester == year.id) 
                                    & (db.academic_course_assignation.assignation==project_var.id)).select().first()
                if academic_assig is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'home'))
            except:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))

    #Check the correct parameters
    if (request.vars['type'] != 'class' and request.vars['type'] != 'lab'):
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    #Check the correct parameters
    if (request.vars['op'] != '1' and request.vars['op'] != '2' and request.vars['op'] != '3'):
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    teacher = db(((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))
                & (db.user_project.project == project_var.id) & (db.user_project.assigned_user == db.auth_user.id)
                & (db.auth_user.id == db.auth_membership.user_id) & (db.auth_membership.group_id == 3)).select().first()

    practice = db(((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))
                & (db.user_project.project == project_var.id) & (db.user_project.assigned_user == db.auth_user.id)
                & (db.auth_user.id == db.auth_membership.user_id) & (db.auth_membership.group_id == 2)).select()
    
    if request.vars['type'] == 'class':
        academic_assig2 = db((db.academic.id == db.academic_course_assignation.carnet) & (db.academic_course_assignation.semester == year.id) 
                            & (db.academic_course_assignation.assignation == project_var.id)).select(orderby=db.academic.carnet)
    else:
        academic_assig2 = db((db.academic.id == db.academic_course_assignation.carnet) & (db.academic_course_assignation.semester == year.id) 
                            & (db.academic_course_assignation.assignation == project_var.id) & (db.academic_course_assignation.laboratorio == True)).select(orderby=db.academic.carnet)

    students = []
    for aca_t in academic_assig2:
        students.append(aca_t.academic_course_assignation)

    var_final_grade = 0.00
    exist_lab = False
    total_lab = float(0)
    total_w = float(0)
    course_category = db((db.course_activity_category.semester == year.id) & (db.course_activity_category.assignation == project_var.id) & 
                        (db.course_activity_category.laboratory == False)).select()
    cat_course_temp = None
    cat_vec_course_temp = []
    course_activities = []
    for category_c in course_category:
        total_w = total_w + float(category_c.grade)
        if category_c.category.category == "Laboratorio":
            exist_lab = True
            total_lab = float(category_c.grade)
            cat_vec_course_temp.append(category_c)
        elif category_c.category.category == "Examen Final":
            var_final_grade = category_c.grade
            if request.vars['op'] != '2' and request.vars['op'] != '3':
                cat_course_temp = category_c
        else:
            cat_vec_course_temp.append(category_c)
            course_activities.append(db((db.course_activity.semester == year.id) & (db.course_activity.assignation == project_var.id)
                                        & (db.course_activity.laboratory == False) & (db.course_activity.course_activity_category == category_c.id)).select())
    if cat_course_temp != None:
        cat_vec_course_temp.append(cat_course_temp)
        course_activities.append(db((db.course_activity.semester == year.id) & (db.course_activity.assignation == project_var.id)
                                    & (db.course_activity.laboratory == False) & (db.course_activity.course_activity_category == cat_course_temp.id)).select())
    course_category = cat_vec_course_temp

    if request.vars['type'] == 'class':
        if total_w != float(100):
            session.flash = T('Can not find the correct weighting defined in the course. You can not use this function')
            redirect(URL('activity_control', 'students_control', vars=dict(period=request.vars['period'], project=request.vars['project'])))

    total_w = float(0)
    lab_category = None
    cat_lab_temp = None
    cat_vec_lab_temp = []
    lab_activities = None
    validate_laboratory = None
    if exist_lab or request.vars['type'] == 'lab':
        validate_laboratory = db((db.validate_laboratory.semester == year.id) & (db.validate_laboratory.project == project_var.id)).select()
        lab_category = db((db.course_activity_category.semester == year.id) & (db.course_activity_category.assignation == project_var.id)
                        & (db.course_activity_category.laboratory == True)).select()
        lab_activities = []
        for category_l in lab_category:
            if category_l.category.category == "Examen Final":
                total_w = total_w + float(category_l.grade)
                cat_lab_temp = category_l
            else:
                cat_vec_lab_temp.append(category_l)
                total_w = total_w + float(category_l.grade)
                lab_activities.append(db((db.course_activity.semester == year.id) & (db.course_activity.assignation == project_var.id)
                                        & (db.course_activity.laboratory == True) & (db.course_activity.course_activity_category == category_l.id)).select())
        if cat_lab_temp != None:
            cat_vec_lab_temp.append(cat_lab_temp)
            lab_activities.append(db((db.course_activity.semester == year.id) & (db.course_activity.assignation == project_var.id)
                                    & (db.course_activity.laboratory == True) & (db.course_activity.course_activity_category == cat_lab_temp.id)).select())
        lab_category = cat_vec_lab_temp

        if total_w != float(100):
            session.flash = T('Can not find the correct weighting defined in the laboratory. You can not use this function')
            redirect(URL('activity_control', 'students_control', vars=dict(period=request.vars['period'], project=request.vars['project']) ))

    requirement = db((db.course_requirement.semester == year.id) & (db.course_requirement.project == project_var.id)).select().first()

    l = []
    t = []
    temp_cont = T('General Report of Activities')
    if request.vars['type'] == 'class':
        temp_cont += ' - ' + T('Course')
    else:
        temp_cont += ' - ' + T('Laboratory')
    t.append(temp_cont)
    l.append(t)

    t = []
    t.append(T('General Course Data'))
    l.append(t)

    t = []
    t.append(T('Course'))
    t.append(project_var.name)
    t.append(T('Semester'))
    t.append(T(year.period.name) + ' ' + str(year.yearp))
    l.append(t)

    t = []
    t.append(T('Teacher'))
    if teacher is not None:
        t.append(teacher.auth_user.first_name + ' ' + teacher.auth_user.last_name)
    else:
        t.append(T('Not Assigned'))
    t.append(T('Rol Student'))
    temp_cont = None
    for t1 in practice:
        if temp_cont is None:
            temp_cont = t1.auth_user.first_name + ' ' + t1.auth_user.last_name
        else:
            temp_cont = temp_cont + '\n' + t1.auth_user.first_name + ' ' + t1.auth_user.last_name
    t.append(temp_cont)
    l.append(t)

    t = []
    t.append(T('Carnet'))
    pos_vcc = 0
    t.append(T('Name'))
    if request.vars['type'] == 'class':
        for category in course_category:
            if category.category.category != "Laboratorio":
                for c in course_activities[pos_vcc]:
                    t.append(c.name)
                t.append(category.category.category + '\n(' + str(category.grade) + 'pts)')
                pos_vcc = pos_vcc + 1
    else:
        for category in lab_category:
            if category.category.category != "Laboratorio":
                for c in lab_activities[pos_vcc]:
                    t.append(c.name)
                t.append(category.category.category + '\n(' + str(category.grade) + 'pts)')
                pos_vcc = pos_vcc + 1
    if request.vars['type'] == 'class' and exist_lab:
        t.append(T('Laboratory') + '\n(' + str(total_lab) + 'pts)')
    if request.vars['type'] == 'class' and requirement is not None:
        t.append(T('Course Requeriment') + '\n(' + requirement.name + 'pts)')
    if request.vars['op'] is not None and request.vars['op'] == '2':
        t.append(T("First recovery test") + '\n(100 pts)')
        t.append(T("First recovery test") + '\n(' + str(var_final_grade) + ' pts)')
    if request.vars['op'] is not None and request.vars['op'] == '3':
        t.append(T("Second recovery test") + '\n(100 pts)')
        t.append(T("Second recovery test") + '\n(' + str(var_final_grade) + ' pts)')

    t.append(T('Final Grade') + '\n(100 pts)')
    l.append(t)

    t = []
    for t1 in students:
        t = []
        if request.vars['type'] == 'class':
            t.append(str(t1.carnet.carnet))

            try:
                var_auth_user = db((db.auth_user.id == t1.carnet.id_auth_user)).select().first()
                t.append(str(var_auth_user.first_name) + " " + str(var_auth_user.last_name))
            except:
                t.append("")
            
            #Position in the vector of activities-
            pos_vcc = 0
            #Vars to the control of grade of the student
            total_category = float(0)
            total_activities = 0
            total_carry=float(0)

            #<!--****************************************FILL THE GRADES OF THE STUDENT****************************************-->
            #<!--COURSE ACTIVITIES-->
            for category in course_category:
                if category.category.category != "Laboratorio" and category.category.category != "Examen Final":
                    total_category = float(0)
                    total_activities = 0
                    for c in course_activities[pos_vcc]:
                        student_grade = db((db.grades.activity == c.id) & (db.grades.academic_assignation == t1.id)).select().first()
                        if student_grade is None:
                            total_category = total_category + float(0)
                            t.append('')
                        else:
                            if category.specific_grade:
                                t.append(str(student_grade.grade))
                                total_category = total_category + float((student_grade.grade * c.grade) / 100)
                            else:
                                t.append(str(student_grade.grade))
                                total_category = total_category + float(student_grade.grade)
                        total_activities = total_activities + 1

                    if category.specific_grade:
                        t.append(str(round(total_category, 2)))
                    else:
                        if total_activities == 0:
                            total_activities = 1
                        total_activities = total_activities * 100
                        total_category = float((total_category * float(category.grade)) / float(total_activities))
                        t.append(str(round(total_category, 2)))
                    total_carry = total_carry + total_category
                    pos_vcc = pos_vcc + 1
                elif category.category.category == "Examen Final":
                    total_carry = int(round(total_carry, 0))
                    total_category = float(0)
                    total_activities = 0
                    for c in course_activities[pos_vcc]:
                        student_grade = db((db.grades.activity == c.id) & (db.grades.academic_assignation == t1.id)).select().first()
                        if student_grade is None:
                            total_category = total_category + float(0)
                            t.append('')
                        else:
                            if category.specific_grade:
                                t.append(str(student_grade.grade))
                                total_category = total_category + float((student_grade.grade * c.grade) / 100)
                            else:
                                t.append(str(student_grade.grade))
                                total_category = total_category + float(student_grade.grade)
                        total_activities = total_activities + 1

                    if category.specific_grade:
                        t.append(str(round(total_category, 2)))
                    else:
                        if total_activities == 0:
                            total_activities = 1
                        total_activities = total_activities * 100
                        total_category = float((total_category * float(category.grade)) / float(total_activities))
                        t.append(str(round(total_category, 2)))
                    total_category = int(round(total_category, 0))
                    total_carry = total_carry + total_category
                    pos_vcc = pos_vcc + 1

            if request.vars['type'] == 'class' and exist_lab:
                total_category = float(0)
                is_validate = False
                #<!--Revalidation of laboratory-->
                for validate in validate_laboratory:
                    if validate.carnet == t1.carnet:
                        is_validate = True
                        total_category = float((int(round(validate.grade, 0)) * total_lab) / 100)

                #<!--Doesnt has a revalidation-->
                if not is_validate:
                    #<!--Position in the vector of activities-->
                    pos_vcc_lab = 0
                    #<!--Vars to the control of grade of the student-->
                    total_category_lab = float(0)
                    total_activities_lab = 0
                    total_carry_lab = float(0)

                    #<!--****************************************FILL THE GRADES OF THE STUDENT****************************************-->
                    #<!--LAB ACTIVITIES-->
                    for category_Lab in lab_category:
                        total_category_lab = float(0)
                        total_activities_lab = 0
                        for c_Lab in lab_activities[pos_vcc_lab]:
                            student_grade = db((db.grades.activity == c_Lab.id) & (db.grades.academic_assignation == t1.id)).select().first()
                            if student_grade is None:
                                total_category_lab = total_category_lab + float(0)
                            else:
                                if category_Lab.specific_grade:
                                    total_category_lab = total_category_lab + float((student_grade.grade * c_Lab.grade) / 100)
                                else:
                                    total_category_lab = total_category_lab + float(student_grade.grade)
                            total_activities_lab = total_activities_lab + 1

                        if not category_Lab.specific_grade:
                            if total_activities_lab == 0:
                                total_activities_lab = 1
                            total_activities_lab = total_activities_lab * 100
                            total_category_lab = float((total_category_lab * float(category_Lab.grade)) / float(total_activities_lab))
                        total_carry_lab = total_carry_lab + total_category_lab
                        pos_vcc_lab = pos_vcc_lab + 1
                    total_category = float((int(round(total_carry_lab, 0)) * total_lab) / 100)

                #<!--Show grade of laboratory-->
                t.append(str(round(total_category, 2)))
                #<!--Plus the laboratory to the carry-->
                total_carry = total_carry + total_category

            if request.vars['type'] == 'class' and requirement is not None:
                if db((db.course_requirement_student.carnet == t1.carnet) & (db.course_requirement_student.requirement == requirement.id)).select().first() is not None:
                    t.append(T('True'))
                else:
                    t.append(T('False'))

            if request.vars['type'] == 'class' and request.vars['op'] == '2':
                var_first_recovery_test = db((db.course_first_recovery_test.carnet == t1.carnet) & (db.course_first_recovery_test.semester == year.id)
                                            & (db.course_first_recovery_test.project == project_var.id)).select().first()
                if var_first_recovery_test is not None:
                    t.append(str(round((var_first_recovery_test.grade), 2)))
                    t.append(str(round((var_first_recovery_test.grade) * var_final_grade / 100, 2)))
                    total_carry = total_carry + round((var_first_recovery_test.grade) * var_final_grade / 100, 0)
                else:
                    t.append('')
                    t.append('')

            if request.vars['type'] == 'class' and request.vars['op'] =='3':
                var_second_recovery_test = db((db.course_second_recovery_test.carnet == t1.carnet) & (db.course_second_recovery_test.semester == year.id)
                                            & (db.course_second_recovery_test.project == project_var.id)).select().first()
                if var_second_recovery_test is not None:
                    t.append(str(round((var_second_recovery_test.grade), 2)))
                    t.append(str(round((var_second_recovery_test.grade) * var_final_grade / 100, 2)))
                    total_carry = total_carry + round((var_second_recovery_test.grade) * var_final_grade / 100, 0)
                else:
                    t.append('')
                    t.append('')

            if request.vars['type'] == 'class' and requirement is not None:
                if db((db.course_requirement_student.carnet == t1.carnet) & (db.course_requirement_student.requirement == requirement.id)).select().first() is not None:
                    if request.vars['type'] == 'class' and exist_lab:
                        if total_category >= float((61 * total_lab) / 100):
                            t.append(str(int(round(total_carry, 0))))
                        else:
                            t.append('0')
                    else:
                        t.append(str(int(round(total_carry, 0))))
                else:
                    t.append('0')
            else:
                if request.vars['type'] == 'class' and exist_lab:
                    if total_category >= float((61 * total_lab) / 100):
                        t.append(str(int(round(total_carry, 0))))
                    else:
                        t.append('0')
                else:
                    t.append(str(int(round(total_carry, 0))))
            pos_vcc = 0
            total_category = float(0)
            total_activities = 0
            total_carry = float(0)
            l.append(t)
            t = []
        else:
            t.append(str(t1.carnet.carnet))
            try:
                var_auth_user = db((db.auth_user.id == t1.carnet.id_auth_user)).select().first()
                t.append(str(var_auth_user.first_name) + " " + str(var_auth_user.last_name))
            except:
                t.append("")

            #<!--Position in the vector of activities-->
            pos_vcc = 0
            #<!--Vars to the control of grade of the student-->
            total_category = float(0)
            total_activities = 0
            total_carry = float(0)
            #<!--****************************************FILL THE GRADES OF THE STUDENT****************************************-->
            #<!--COURSE ACTIVITIES-->
            for category in lab_category:
                total_category = float(0)
                total_activities = 0
                for c in lab_activities[pos_vcc]:
                    student_grade = db((db.grades.activity == c.id) & (db.grades.academic_assignation == t1.id)).select().first()
                    if student_grade is None:
                        total_category = total_category + float(0)
                        t.append('')
                    else:
                        if category.specific_grade:
                            t.append(str(student_grade.grade))
                            total_category = total_category + float((student_grade.grade * c.grade) / 100)
                        else:
                            t.append(str(student_grade.grade))
                            total_category = total_category + float(student_grade.grade)
                    total_activities = total_activities + 1

                if category.specific_grade:
                    t.append(str(round(total_category, 2)))
                else:
                    if total_activities == 0:
                        total_activities = 1
                    total_activities = total_activities*100
                    total_category = float((total_category * float(category.grade)) / float(total_activities))
                    t.append(str(round(total_category, 2)))
                total_carry = total_carry + total_category
                pos_vcc = pos_vcc + 1

            t.append(str(int(round(total_carry, 0))))
            l.append(t)
            t = []
            pos_vcc = 0
            total_category = float(0)
            total_activities = 0
            total_carry = float(0)

    nombre = 'ReporteGeneralActividades ' + project_var.name
    return dict(
        filename=nombre, 
        csvdata=l
    )

@auth.requires_login()
def control_activity_without_metric():
    year = db(db.period_year.id == request.vars['year']).select().first()
    year_semester = year.period
    project = db(db.project.id==request.vars['project']).select().first()

    #emarquez: adaptacion periodos variables
    if cpfecys.is_semestre(request.vars['year']):
        assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project.id)
                        & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
    else:
        assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == request.vars['project'])).select(db.user_project.ALL).first()

    assigned_to_project = False if assigantion is None else True

    return dict(
        semester=year_semester.name,
        year=year.yearp,
        semestre2=year,
        project=project,
        assigned_to_project=assigned_to_project
    )

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Academic'))
def graphs():
    #requires parameter of project if none is provided then redirected to courses
    project_id = request.vars['project']
    year_period = request.vars['year_period']
    
    es_student = db((db.user_project.assigned_user == auth.user.id) & (db.project.id == project_id)
                & (db.user_project.project == db.project.id)).select().first()
    es_academic = db((db.academic_course_assignation.carnet == db.academic.id) & (db.academic_course_assignation.assignation == project_id)
                & (db.academic.id_auth_user == auth.user.id)).select().first()
    
    if (es_academic is not None) or (es_student is not None) :
        current_project = db((db.project.id == project_id)).select(db.project.ALL).first()
        currentyear_period = db.period_year(db.period_year.id == year_period)
        current_period_name = currentyear_period.period.name
        
        # Average of laboratory and period
        query_lab = "SELECT obtenerPromedio(\'T\', {}, {}) AS promedio;".format(str(current_project.id), str(currentyear_period.id) )
        query_curso = "SELECT obtenerPromedio(\'F\', {}, {}) AS promedio;".format(str(current_project.id) , str(currentyear_period.id) )
        avg_lab = db.executesql(query_lab, as_dict=True)
        avg_curso = db.executesql(query_curso, as_dict=True)
        var_avg_lab = avg_lab[0]['promedio']
        var_avg_curso = avg_curso[0]['promedio']
        
        if var_avg_lab is None:
            var_avg_lab = 0

        if var_avg_curso is None:
            var_avg_curso = 0
        
        avg_l = [T("Laboratorio"), var_avg_lab]
        avg_c = [T("Curso"), var_avg_curso]
    
        avg = []
        avg.append(avg_c)
        avg.append(avg_l)
    else:
        session.flash = T('Not valid Action.')
        redirect(URL('default','home'))
    
    return dict(
        current_project=current_project,
        currentyear_period=currentyear_period,
        current_period_name=current_period_name,
        avg=avg
    )

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator') or auth.has_membership('Teacher'))
def courses_list_request():
    #emarquez : seteando por id
    set_periodo = request.vars['period'] or False
    
    period_param = cpfecys.current_year_period()
    if set_periodo:
        period_param = db(db.period_year.id == set_periodo).select().first()

    area = db(db.area_level.name == 'DTT Tutor Académico').select(db.area_level.id).first()
    courses_request = None
    if auth.has_membership('Teacher'):
        courses_request = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == db.project.id)
                            & (db.project.area_level == area.id) & ((db.user_project.period <= cpfecys.current_year_period().id) 
                            & ((db.user_project.period + db.user_project.periods) > cpfecys.current_year_period().id))).select()

        if tipo_periodo:
            courses_request = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == db.project.id)
                                & (db.project.area_level == area.id) & (db.user_project.period == set_periodo)).select()

    if auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'):
        courses_request = db(db.project.area_level == area.id).select()

    #emarquez: se cambio semestre_id --> semester_id=cpfecys.current_year_period())
    return dict(
        courses_request=courses_request,
        split_name=split_name,
        split_section=split_section,
        semester_id=period_param
    )

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator') or auth.has_membership('Teacher'))
def solve_request_change_weighting():
    #Obtain the course that want to view the request
    course_check = request.vars['course']

    #Check that the request vars contain something
    if course_check is None:
        redirect(URL('default', 'home'))
    else:
        #Check if teacher or other role
        course = None
        if auth.has_membership('Teacher'):
            course = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == course_check)
                    & ((db.user_project.period <= cpfecys.current_year_period().id) & ((db.user_project.period + db.user_project.periods) > cpfecys.current_year_period().id))).select(db.user_project.ALL).first()

            if course is None:
                session.flash = T('You do not have permission to view course requests')
                redirect(URL('default', 'home'))
        else:
            course = db.project(id=course_check)

        #Check that the course exist
        name = None
        if course is None:
            redirect(URL('default', 'home'))
        else:
            if auth.has_membership('Teacher'):
                name = course.project.name
            else:
                name = course.name

        current_year_period = cpfecys.current_year_period()
        return dict(
            name=name,
            semester=current_year_period.period.name,
            semestre2=current_year_period,
            year=current_year_period.yearp,
            course=course_check
        )

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator') or auth.has_membership('Teacher'))
def solve_request_change_activity():
    #Cancel the request made
    if request.args(0) == 'reject':
        pending = db((db.requestchange_activity.id == int(request.vars['requestID'])) & (db.requestchange_activity.status == 'Pending')
                    & (db.requestchange_activity.semester == cpfecys.current_year_period().id) & (db.requestchange_activity.course == int(request.vars['course']))).select().first()
        if pending is None:
            session.flash = T('The plan change request has been answered by another user or is there a problem with the request')
        else:
            rol_temp = get_rol()
            db(db.requestchange_activity.id == int(request.vars['requestID'])).update(
                status='Rejected', 
                user_resolve=auth.user.id, 
                roll_resolve=rol_temp, 
                date_request_resolve= datetime.datetime.now()
            )
            
            #Log of request change activity
            rejected = db(db.requestchange_activity.id==int(request.vars['requestID'])).select().first()
            if rejected is not None:
                id_rejected = db.requestchange_activity_log.insert(
                    user_request=rejected.user_id.username,
                    roll_request=rejected.roll,
                    status='Rejected',
                    user_resolve=rejected.user_resolve.username,
                    roll_resolve=rejected.roll_resolve,
                    description=rejected.description,
                    date_request=rejected.date_request,
                    date_request_resolve=rejected.date_request_resolve,
                    category_request=rejected.course_activity_category.category.category,
                    semester=rejected.semester.period.name,
                    yearp=rejected.semester.yearp,
                    course=rejected.course.name
                )
                activities_change = db(db.requestchange_course_activity.requestchange_activity == rejected.id).select()
                for act_change in activities_change:
                    db.requestchange_course_activity_log.insert(
                        requestchange_activity=id_rejected,
                        operation_request=act_change.operation_request,
                        activity=act_change.activity,
                        name=act_change.name,
                        description=act_change.description,
                        grade=act_change.grade,
                        date_start=act_change.date_start,
                        date_finish=act_change.date_finish
                    )
            session.flash = T('The plan change request has been canceled')
        redirect(URL('activity_control', 'solve_request_change_activity', vars=dict(course=request.vars['course'])))

    #Solve the request made
    if request.args(0) == 'solve':
        pending = db((db.requestchange_activity.id == int(request.vars['requestID'])) & (db.requestchange_activity.status == 'Pending')
                    & (db.requestchange_activity.semester == cpfecys.current_year_period().id) & (db.requestchange_activity.course == int(request.vars['course']))).select().first()
        if pending is None:
            session.flash = T('The plan change request has been answered by another user or is there a problem with the request')
        else:
            rol_temp = get_rol()
            db(db.requestchange_activity.id == int(request.vars['requestID'])).update(
                status='Accepted',
                user_resolve=auth.user.id,
                roll_resolve=rol_temp,
                date_request_resolve=datetime.datetime.now()
            )
            #Log of request change activity
            accepted = db(db.requestchange_activity.id == int(request.vars['requestID'])).select().first()
            if accepted is not None:
                id_rejected = db.requestchange_activity_log.insert(
                    user_request=accepted.user_id.username,
                    roll_request=accepted.roll,
                    status='Accepted',
                    user_resolve=accepted.user_resolve.username,
                    roll_resolve=accepted.roll_resolve,
                    description=accepted.description,
                    date_request=accepted.date_request,
                    date_request_resolve=accepted.date_request_resolve,
                    category_request=accepted.course_activity_category.category.category,
                    semester=accepted.semester.period.name,
                    yearp=accepted.semester.yearp,
                    course=accepted.course.name
                )
                activities_change = db(db.requestchange_course_activity.requestchange_activity == accepted.id).select()
                for act_change in activities_change:
                    #Log request change activity
                    db.requestchange_course_activity_log.insert(
                        requestchange_activity=id_rejected,
                        operation_request=act_change.operation_request,
                        activity=act_change.activity,
                        name=act_change.name,
                        description=act_change.description,
                        grade=act_change.grade,
                        date_start=act_change.date_start,
                        date_finish=act_change.date_finish
                    )
                    
                    #Log and changes in activities
                    if act_change.operation_request == 'insert':
                        #Change in activities
                        db.course_activity_log.insert(
                            user_name=auth.user.username,
                            roll=rol_temp,
                            operation_log='insert',
                            course=accepted.course.name,
                            yearp=cpfecys.current_year_period().yearp,
                            period=T(cpfecys.current_year_period().period.name),
                            metric='T',
                            after_course_activity_category=accepted.course_activity_category.category.category,
                            after_name=act_change.name,
                            after_description=act_change.description,
                            after_grade=act_change.grade,
                            after_laboratory='T',
                            after_teacher_permition='F',
                            after_date_start=act_change.date_start,
                            after_date_finish=act_change.date_finish
                        )
                        db.course_activity.insert(
                            course_activity_category=accepted.course_activity_category,
                            name=act_change.name,
                            description=act_change.description,
                            grade=act_change.grade,
                            semester=cpfecys.current_year_period().id,
                            assignation=accepted.course,
                            laboratory='T',
                            teacher_permition='F',
                            date_start=act_change.date_start,
                            date_finish=act_change.date_finish
                        )
                    elif act_change.operation_request == 'delete':
                        db.course_activity_log.insert(
                            user_name=auth.user.username,
                            roll=rol_temp,
                            operation_log='delete',
                            course=accepted.course.name,
                            yearp=cpfecys.current_year_period().yearp,
                            period=T(cpfecys.current_year_period().period.name),
                            metric='T',
                            before_course_activity_category=accepted.course_activity_category.category.category,
                            before_name=act_change.name,
                            before_description=act_change.description,
                            before_grade=act_change.grade,
                            before_laboratory='T',
                            before_teacher_permition='F',
                            before_date_start=act_change.date_start,
                            before_date_finish=act_change.date_finish
                        )
                        db(db.course_activity.id == act_change.activity).delete()
                    elif act_change.operation_request == 'update':
                        activity_old_r = db(db.course_activity.id == act_change.activity).select().first()
                        db.course_activity_log.insert(
                            user_name=auth.user.username,
                            roll=rol_temp,
                            operation_log='update',
                            course=accepted.course.name,
                            yearp=cpfecys.current_year_period().yearp,
                            period=T(cpfecys.current_year_period().period.name),
                            metric='T',
                            before_course_activity_category=activity_old_r.course_activity_category.category.category,
                            before_name=activity_old_r.name,
                            before_description=activity_old_r.description,
                            before_grade=activity_old_r.grade,
                            before_laboratory=activity_old_r.laboratory,
                            before_teacher_permition=activity_old_r.teacher_permition,
                            before_date_start=activity_old_r.date_start,
                            before_date_finish=activity_old_r.date_finish,
                            after_course_activity_category=accepted.course_activity_category.category.category,
                            after_name=act_change.name,
                            after_description=act_change.description,
                            after_grade=act_change.grade,
                            after_laboratory='T',
                            after_teacher_permition='F',
                            after_date_start=act_change.date_start,
                            after_date_finish=act_change.date_finish
                        )
                        db(db.course_activity.id == act_change.activity).update(
                            name=act_change.name,
                            description=act_change.description,
                            grade=act_change.grade,
                            date_start=act_change.date_start,
                            date_finish=act_change.date_finish
                        )
            session.flash = T('The plan change request has been accepted')
        redirect(URL('activity_control', 'solve_request_change_activity', vars=dict(course=request.vars['course'])))

    #Obtain the course that want to view the request
    course_check = request.vars['course']

    #Check that the request vars contain something
    if course_check is None:
        redirect(URL('default', 'home'))
    else:
        #Check if teacher or other role
        course = None
        if auth.has_membership('Teacher'):
            course = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == course_check)
                    & ((db.user_project.period <= cpfecys.current_year_period().id) & ((db.user_project.period + db.user_project.periods) > cpfecys.current_year_period().id))).select(db.user_project.ALL).first()
            if course is None:
                session.flash = T('You do not have permission to view course requests')
                redirect(URL('default', 'home'))
        else:
            course = db.project(id = course_check)

        #Check that the course exist
        name = None
        if course is None:
            redirect(URL('default', 'home'))
        else:
            if auth.has_membership('Teacher'):
                name = course.project.name
            else:
                name = course.name

        current_year_period = cpfecys.current_year_period()
        return dict(
            name=name,
            semester=current_year_period.period.name,
            semestre2=current_year_period,
            year=current_year_period.yearp,
            course=course_check
        )

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator') or auth.has_membership('Teacher'))
def solve_request_change_grades():
    #Obtain the course that want to view the request
    course_check = request.vars['course']

    #Check that the request vars contain something
    if course_check is None:
        redirect(URL('default', 'home'))
    else:
        #Check if teacher or other role
        course = None
        if auth.has_membership('Teacher'):
            course = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == course_check)
                    & ((db.user_project.period <= cpfecys.current_year_period().id) & ((db.user_project.period + db.user_project.periods) > cpfecys.current_year_period().id))).select(db.user_project.ALL).first()

            if course is None:
                session.flash = T('You do not have permission to view course requests')
                redirect(URL('default', 'home'))
        else:
            course = db.project(id=course_check)

        #Check that the course exist
        name = None
        if course is None:
            redirect(URL('default', 'home'))
        else:
            if auth.has_membership('Teacher'):
                name = course.project.name
            else:
                name = course.name

        current_year_period = cpfecys.current_year_period()
        return dict(
            name=name,
            semester=current_year_period.period.name,
            semestre2=current_year_period,
            year=current_year_period.yearp,
            course=course_check
        )

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator') or auth.has_membership('Teacher'))
def grades_request():
    current_year_period = cpfecys.current_year_period()
    rol_log = get_rol()

    if request.vars['op'] == "acceptRequestChange":
        request_change_var = db(db.request_change_grades.id == request.vars['Idrequest']).select().first()
        if request_change_var.status != 'pending':
            return T('Request Change has been resolved.')

    return dict(
        semestre2=current_year_period,
        rol_log=rol_log
    )

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator') or auth.has_membership('Teacher'))
def weighting_request():
    current_year_period = cpfecys.current_year_period()
    rol_log = get_rol()
    
    return dict(
        semestre2=current_year_period,
        rol_log=rol_log
    )

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator') or auth.has_membership('Teacher'))
def activity_request():
    current_year_period = cpfecys.current_year_period()
    return dict(semestre2=current_year_period)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def course_laboratory_exception():
    query = db.course_laboratory_exception
    grid = SQLFORM.grid(query, maxtextlength=100, csv=False)
    return dict(grid=grid)

#emarquez: nuevas excepciones por periodo
@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def course_laboratory_exception_period():
    query = db.course_laboratory_exception_period
    grid = SQLFORM.grid(query, maxtextlength=100, csv=False)
    return dict(grid=grid)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def course_limit_exception():
    query = db.course_limit_exception
    grid = SQLFORM.grid(query, maxtextlength=100, csv=False)
    return dict(grid=grid)

#emarquez: nuevas excepciones por periodo
@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def course_limit_exception_period():
    query = db.course_limit_exception_period
    grid = SQLFORM.grid(query, maxtextlength=100, csv=False)
    return dict(grid=grid)
#emarquez: excepciones por periodo

#emarquez: Funciones adaptacion periodos variables.
@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def periodo_variable():
    grid = SQLFORM.grid(db.period_detail, maxtextlength=100, csv=False)
    return dict(grid=grid)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def activity_category():
    query = db.activity_category
    grid = SQLFORM.grid(query, maxtextlength=100, csv=False)
    return dict(grid=grid)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def partials():
    grid = SQLFORM.grid(db.partials, maxtextlength=100, csv=False, deletable=False)
    return dict(grid=grid)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def student_control_period():
    year = cpfecys.current_year_period()
    year_semester = db.period(id=year.period)
    #emarquez: incluyendo orden para student control period
    grid = SQLFORM.grid(
        db.student_control_period,
        maxtextlength=100,
        csv=False,
        create=False,
        deletable=False,
        orderby=~db.student_control_period.id
    )
    return dict(grid=grid)

@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def control_students_grades():
    id_activity = role = request.vars['activity']
    id_project = role = request.vars['project']
    id_year = role = request.vars['year']

    #LTZOC: Carga masiva de notas para rol student
    log_carga_html = ''
    archivo_notas = request.vars.csvfile_notas
    if (archivo_notas != None) & (id_activity != None)& (id_project != None) & (id_year != None):
        if dame_fecha(id_activity):
            log_carga_csv = cargar_notas_csv(id_project, id_activity, id_year, archivo_notas)
            
            if log_carga_csv !=  None:
                log_carga_html = XML(array_to_html_log(log_carga_csv))
        else:
            response.flash = T('La fecha limite de la actividad ha expirado.')
    #LTZOC: Termina carga masiva de notas para rol student

    var_period = db(db.period_year.id == id_year).select().first()
    if not var_period:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    var_activity = db(db.course_activity.id == id_activity).select().first()
    if not var_activity:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    var_project = db(db.project.id == id_project).select().first()
    if not var_project:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    course_ended_var = db((db.course_ended.project == var_project.id) & (db.course_ended.period == var_period.id)).select().first()

    course_ended = False
    course_ended_var = db((db.course_ended.project == var_project.id) & (db.course_ended.period == var_period.id)).select().first()
    if course_ended_var != None:
        if course_ended_var.finish:
            course_ended = True

    if course_ended_var != None:
        if (not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator')) and (course_ended_var.finish):
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    actual_period = True
    for date_var in db((db.student_control_period.period_name == T(str(cpfecys.current_year_period().period.name)) + " " + str(cpfecys.current_year_period().yearp))).select():
        if ((var_activity.date_start < date_var.date_start_semester) or (var_activity.date_finish < date_var.date_start_semester)):
            actual_period = False
            if (not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator')) :
                session.flash = T('The activity date is out of this semester.')
                redirect(URL('default', 'home'))

    if (not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator')):
        #emarquez: periodos variables
        if cpfecys.is_semestre(request.vars['year']):
            assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == var_project)
                        & ((db.user_project.period <= var_period.id) & ((db.user_project.period + db.user_project.periods) > var_period.id))).select(db.user_project.ALL).first()

            exception_query = db(db.course_laboratory_exception.project == id_project).select().first()
        else:
            assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == var_project)).select(db.user_project.ALL).first()
            exception_query = db(db.course_laboratory_exception_period.project == id_project).select().first()

        if exception_query is None:
            exception_s_var = False
            exception_t_var = False
        else:
            exception_t_var = exception_query.t_edit_lab
            exception_s_var = exception_query.s_edit_course

        if (assigantion is None) or (auth.has_membership('Teacher') and var_activity.laboratory and not exception_t_var) or (auth.has_membership('Student') and not var_activity.laboratory and not exception_s_var and not var_activity.teacher_permition and not var_activity.course_activity_category.teacher_permition):
            session.flash = T('You do not have permission to view course requests')
            redirect(URL('default', 'home'))

    if var_activity.laboratory:
        academic_assig = db((db.academic_course_assignation.assignation == id_project) & (db.academic_course_assignation.semester == id_year) 
                        & (db.academic_course_assignation.laboratorio == True)).select()
    else:
        academic_assig = db((db.academic_course_assignation.assignation == id_project) & (db.academic_course_assignation.semester == id_year)).select()

    #Permition to add grades
    exception_query = db(db.course_laboratory_exception.project == id_project).select().first()
    request_change_var = request_change_var_method(exception_query, var_activity, request.vars['year'], var_period)

    return dict(
        academic_assig=academic_assig,
        var_period=var_period,
        var_activity=var_activity,
        var_project=var_project,
        request_change_var=request_change_var,
        actual_period=actual_period,
        course_ended=course_ended,
        log_carga_html=log_carga_html
    )

@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator'))
def cargar_notas_csv(proyecto_id, actividad_id, periodo, archivo):
    aviso_users = []
    success = False

    def agregar_mensaje(row_carnet, row_nota, mensaje):
        return [row_carnet, row_nota, mensaje]

    try:
        file = archivo.file
    except:
        response.flash = T('Please upload a file.')
        return None

    try:
        #mensajes
        failed_message = T('Failed to add grade')
        alredy_message = T('Already have an associated grade')
        success_message = T('Grade added')

        #1
        period = cpfecys.current_year_period()
        var_activity = db(db.course_activity.id == actividad_id).select().first()
        var_project = db(db.project.id == proyecto_id).select().first()

        cr = csv.reader(file.getvalue().decode('utf-8').splitlines(), dialect=csv.excel_tab, delimiter=',', quotechar='"')
        header = next(cr)
        for row in cr:
            try:
                row_carnet = row[0]
                row_nota = row[1]

                if not row_carnet.isdigit():
                    aviso_users.append(agregar_mensaje(row_carnet, row_nota, "{} | Carnet: {} no es válido.".format(failed_message, row_carnet)))
                    continue

                if not nota_valida_csv(row_nota):
                    aviso_users.append(agregar_mensaje(row_carnet, row_nota, "{} | Carnet: {} Nota: {} el formato de la nota no es válido".format(failed_message, row_carnet, row_nota)))
                    continue

                academic_var = db(db.academic.carnet == row_carnet).select().first()
                if academic_var is None:
                    aviso_users.append(agregar_mensaje(row_carnet, row_nota, "{} | Carnet: {} no es válido.".format(failed_message, row_carnet)))
                    continue
            
                assig_var = db((db.academic_course_assignation.assignation == var_project.id) & (db.academic_course_assignation.semester == period.id) 
                            & (db.academic_course_assignation.carnet == academic_var.id)).select().first()
                if assig_var is None:
                    aviso_users.append(agregar_mensaje(row_carnet, row_nota, "{} | Carnet: {} no es válido para esta actividad.".format(failed_message, row_carnet)))
                    continue

                grade_before = db((db.grades.academic_assignation == assig_var.id) & (db.grades.activity == var_activity.id)).select().first()
                if grade_before is not None:
                    aviso_users.append(agregar_mensaje(row_carnet, row_nota, "{} | Carnet: {} {}.".format(failed_message, row_carnet, alredy_message)))
                    continue

                if (var_activity.laboratory) & (assig_var.laboratorio != var_activity.laboratory):
                    aviso_users.append(agregar_mensaje(row_carnet, row_nota, "{} | Carnet: {} Nota: {}.".format(failed_message, row_carnet, row_nota)))
                    continue
            
                grade = db.grades.insert(academic_assignation=assig_var.id, activity=var_activity.id, grade=row_nota) #Insertando nota
                if grade is None: #Validando que se inserte la nota
                    aviso_users.append(agregar_mensaje(row_carnet, row_nota, "{} | Carnet: {} Nota: {}.".format(failed_message, row_carnet, row_nota)))
                    continue
                
                #Insertando en log
                db.grades_log.insert(
                    user_name=auth.user.username,
                    roll='Student',
                    operation_log='insert',
                    academic_assignation_id=assig_var.id,
                    academic=assig_var.carnet.carnet,
                    project=assig_var.assignation.name,
                    activity=var_activity.name,
                    activity_id=var_activity.id,
                    category=var_activity.course_activity_category.category.category,
                    period=T(assig_var.semester.period.name),
                    yearp=assig_var.semester.yearp,
                    after_grade=row_nota,
                    description="Insertando desde carga masiva de notas de actividades - "
                )

                aviso_users.append(agregar_mensaje(row_carnet, row_nota, "{} | Carnet: {} Nota: {}.".format(success_message, row_carnet, row_nota)))
            except IndexError:
                response.flash = "El archivo contiene errores, verifique la sintaxis. " + str(IndexError)
                return None
        
        response.flash = T('Data uploaded')
        return aviso_users    
    except AttributeError:
        response.flash = T('File doesn\'t seem properly encoded. ' + str(AttributeError))
        return None

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def grades():
    id_activity = request.vars['activity']
    id_project = request.vars['project']
    id_year = request.vars['year']
    coment = request.vars['coment']

    if coment is None:
        coment = ""

    var_period = db(db.period_year.id == id_year).select().first()
    if not var_period:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    var_activity = db(db.course_activity.id == id_activity).select().first()
    if not var_activity:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    var_project = db(db.project.id == id_project).select().first()
    if not var_project:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    if var_activity.laboratory:
        academic_assig = db((db.academic.id == db.academic_course_assignation.carnet) & (db.academic_course_assignation.assignation == id_project)
                        & (db.academic_course_assignation.semester == id_year) & (db.academic_course_assignation.laboratorio == True)).select(orderby=db.academic.carnet)
    else:
        academic_assig = db((db.academic.id == db.academic_course_assignation.carnet) & (db.academic_course_assignation.assignation == id_project) 
                        & (db.academic_course_assignation.semester == id_year)).select(orderby=db.academic.carnet)

    temp_academic = []
    for aca_t in academic_assig:
        temp_academic.append(aca_t.academic_course_assignation)

    actual_period = True
    #emarquez: periodos variables
    if cpfecys.is_semestre(id_year):
        for date_var in db((db.student_control_period.period_name == T(str(cpfecys.current_year_period().period.name)) + " " + str(cpfecys.current_year_period().yearp))).select():
            if ((var_activity.date_start < date_var.date_start_semester) or (var_activity.date_finish < date_var.date_start_semester)):
                actual_period = False
    else:
        for date_var in db((db.period_detail.period == var_period.period)).select():
            if ((var_activity.date_start < date_var.date_start_semester) or (var_activity.date_finish < date_var.date_start_semester)):
                actual_period = False

    course_ended = False
    course_ended_var = db((db.course_ended.project == var_project.id) & (db.course_ended.period == var_period.id)).select().first()
    if course_ended_var != None:
        if course_ended_var.finish:
            course_ended = True

    rol_log = get_rol()

    #Request change
    exist_request_change = False
    if db((db.request_change_grades.activity == var_activity.id) & (db.request_change_grades.status == 'pending')).select().first() != None:
        exist_request_change = True

    #Request exist_activity_request_change
    exist_activity_request_change = False
    if db((db.requestchange_course_activity.activity == var_activity.id) & (db.requestchange_activity.status == 'pending') & (db.requestchange_course_activity.requestchange_activity == db.requestchange_activity.id)).select().first() != None:
        exist_activity_request_change = True

    #Permition to add grades
    #emarquez: periodos variables
    if cpfecys.is_semestre(id_year):
        exception_query = db(db.course_laboratory_exception.project == id_project).select().first()
    else:
        exception_query = db(db.course_laboratory_exception_period.project == id_project).select().first()

    request_change_var = request_change_var_method(exception_query, var_activity, request.vars['year'], var_period)

    add_grade_flash = False
    add_grade_error = False
    message_var = ""
    message_var2 = ""
    alert_message = False

    carnet_list = str(request.vars['carnet']).split(',')
    grade_list = str(request.vars['grade']).split(',')
    cont_temp = 0

    #<!---------------------------INSERT---------------------------->
    if (request.vars['op'] == "add_grade") | (request.vars['op'] == "add_grade_list"):
        send_mail_var = False
        for carnet_id in carnet_list:
            if (request.vars['op'] == "add_grade"):
                carnet_list = request.vars['carnet']
                grade_list = request.vars['grade']
                request.vars['grade'] = grade_list
            else:
                request.vars['grade'] = grade_list[cont_temp]
                cont_temp = cont_temp + 1
            
            request.vars['carnet'] = carnet_id
            if request.vars['carnet'] != "":
                try:
                    academic_var = db(db.academic.carnet == request.vars['carnet']).select().first()
                    assig_var = db((db.academic_course_assignation.assignation == var_project.id) & (db.academic_course_assignation.semester == var_period.id) 
                                & (db.academic_course_assignation.carnet == academic_var.id)).select().first()
                    
                    #--------------------------------------------INSERT GRADE-------------------------------------
                    if not request_change_var:
                        if exist_request_change or exist_activity_request_change:
                            add_grade_error = True
                            message_var = T('Can not make operation because there is a pending request change. Please resolve it before proceeding.')
                        else:
                            grade_before = db((db.grades.academic_assignation == assig_var.id) & (db.grades.activity == var_activity.id)).select().first()
                            if grade_before is None:
                                if (var_activity.laboratory == False) | (assig_var.laboratorio == var_activity.laboratory):
                                    grade = db.grades.insert(academic_assignation=assig_var.id, activity=var_activity.id, grade=request.vars['grade'])

                                    if grade != None:
                                        #--------------------------------------------log-------------------------------------
                                        db.grades_log.insert(
                                            user_name=auth.user.username,
                                            roll=rol_log,
                                            operation_log='insert',
                                            academic_assignation_id=assig_var.id,
                                            academic=assig_var.carnet.carnet,
                                            project=assig_var.assignation.name,
                                            activity=var_activity.name,
                                            activity_id=var_activity.id,
                                            category=var_activity.course_activity_category.category.category,
                                            period=T(assig_var.semester.period.name),
                                            yearp=assig_var.semester.yearp,
                                            after_grade=request.vars['grade'],
                                            description=T('Inserted from Grades page')+" - "+coment
                                        )
                                        
                                        if request.vars['op'] == "add_grade":
                                            add_grade_flash = True
                                            message_var = '{} | Carnet: {} Nota: {}'.format(T('Grade added'), str(academic_var.carnet), str(grade.grade))
                                        pass
                                    else:
                                        add_grade_error = True
                                        message_var = '{} | Carnet: {} Nota: {}'.format(T('Failed to add grade'), str(academic_var.carnet), str(grade.grade))
                                else:
                                    add_grade_error = True
                                    message_var = '{} | Carnet: {} Nota: {}'.format(T('Failed to add grade'), str(academic_var.carnet), str(grade.grade))
                            else:
                                add_grade_error = True
                                message_var = '{} | Carnet: {} {}'.format(T('Failed to add grade'), request.vars['carnet'], T('Already have an associated grade'))
                      #--------------------------------------------INSERT REQUEST-------------------------------------
                    else:
                        if exist_activity_request_change:
                            alert_message = True
                            message_var2 = T('Can not make operation because there is a pending request change. Please resolve it before proceeding.')
                        else:
                            grade_before = db((db.grades.academic_assignation == assig_var.id) & (db.grades.activity == var_activity.id)).select().first()

                            var_grade_before = None
                            var_operation = 'insert'
                            if grade_before != None:
                                var_grade_before = grade_before.grade
                                var_operation = 'update'

                            request_change = db((db.request_change_grades.activity == var_activity.id) & (db.request_change_grades.status == 'pending')).select().first()
                            if request_change is None:
                                grade = db.request_change_grades.insert(
                                    user_id=auth.user.id,
                                    activity=var_activity.id,
                                    status='pending',
                                    roll=rol_log,
                                    period=assig_var.semester.id,
                                    project=assig_var.assignation.id,
                                    description=request.vars['description_var']
                                )

                                #-------------------------------------LOG-----------------------------------------------
                                log_id = db.request_change_g_log.insert(
                                    r_c_g_id=grade,
                                    username=auth.user.username,
                                    roll=rol_log,
                                    after_status='pending',
                                    description=request.vars['description_var'],
                                    description_log=T('Inserted from Grades page'),
                                    semester=T(assig_var.semester.period.name),
                                    yearp=assig_var.semester.yearp,
                                    activity=var_activity.name,
                                    category=var_activity.course_activity_category.category.category,
                                    project=assig_var.assignation.name
                                )
                        
                            request_change = db((db.request_change_grades.activity == var_activity.id) & (db.request_change_grades.status == 'pending')).select().first()
                            rq_grade = db.request_change_grades_detail.insert(
                                request_change_grades=request_change.id,
                                academic_assignation=assig_var.id,
                                before_grade=var_grade_before,
                                operation_request=var_operation,
                                after_grade=request.vars['grade']
                            )
                            
                            log_id = db((db.request_change_g_log.r_c_g_id == request_change.id) & (db.request_change_g_log.after_status == 'pending')).select().first()
                            db.request_change_grade_d_log.insert(
                                request_change_g_log=log_id.id,
                                operation_request=var_operation,
                                academic=academic_var.carnet,
                                before_grade=var_grade_before,
                                after_grade=request.vars['grade']
                            )

                            send_mail_var = True
                except:
                    add_grade_error = True
                    message_var = '{} | Carnet: {} {}'.format(T('Failed to add grade'), request.vars['carnet'], T('not exist')) if academic_var is None else T('Failed to add grade')
        
        if send_mail_var == True:
            #send mail
            project_name = var_project.name
            project_id = id_project

            #emarquez: periodos variables

            if cpfecys.is_semestre(id_year):
                check = db((db.user_project.assigned_user==auth.user.id)&\
                            (db.user_project.project == project_id)&\
                            ((db.user_project.period <= var_period.id) & \
                            ((db.user_project.period + db.user_project.periods) > var_period.id))).select(db.user_project.ALL).first()
            else:
                check = db((db.user_project.assigned_user==auth.user.id)&\
                            (db.user_project.project == project_id)).select(db.user_project.ALL).first()
            pass



                         #db.user_project(project = project_id, period = var_period.id, assigned_user = auth.user.id)
            #Message
            #users2 = db((db.auth_user.id==db.user_project.assigned_user)&(db.user_project.period == check.period) & (db.user_project.project==check.project)&(db.auth_membership.user_id==db.user_project.assigned_user)&(db.auth_membership.group_id==3)).select().first()
            try:
                users2 = db((db.auth_user.id==db.user_project.assigned_user)&\
                            (db.user_project.project == project_id)&\
                            ((db.user_project.period <= var_period.id) & \
                            ((db.user_project.period + db.user_project.periods) > var_period.id))&\
                            (db.auth_membership.user_id==db.user_project.assigned_user)&\
                            (db.auth_membership.group_id==3)).select().first()

                subject="Solicitud de cambio de notas - "+project_name
                message2="<br>Por este medio se le informa que el(la) practicante "+check.assigned_user.first_name+" "+check.assigned_user.last_name+" ha creado una solicitud de cambio en las notas del laboratorio del Curso de \""+project_name+"\"."
                message2=message2+"<br>Para aceptar o rechazar dicha solicitud dirigirse al control de solicitudes o al siguiente link: " +cpfecys.get_domain()+ "cpfecys/activity_control/solve_request_change_grades?course="+str(project_id)
                message2=message2+"<br>Saludos.<br><br>Sistema de Seguimiento de La Escuela de Ciencias y Sistemas<br>Facultad de Ingeniería - Universidad de San Carlos de Guatemala</html>"
                #Send Mail to the Teacher
                message="<html>Catedratico(a) "+users2.auth_user.first_name+" "+users2.auth_user.last_name+" reciba un cordial saludo.<br>"
                message3=message+message2

                fail1 = send_mail_to_students(message3,subject,users2.auth_user.email,check,var_period.period.name,var_period.yearp)
                #fail1=0#Esto hay que quitarlo****************************************************************************************************************!!!!!!!
                if fail1==1:
                    alert_message = True
                    message_var2 = T("Request has been sent") + ". " + T("Failed to send email to teacher")

                else:
                    alert_message = True
                    message_var2 = T("Request has been sent") + ". " + T("Sent email to teacher")
            except:
                message_var2 = T("Request has been sent") + ". " + T("Failed to send email to teacher")

    return dict(
        academic_assig=temp_academic,
        var_period=var_period,
        var_activity=var_activity,
        var_project=var_project,
        rol_log=rol_log,
        request_change_var=request_change_var,
        exist_request_change=exist_request_change,
        message_var=message_var,
        message_var2=message_var2,
        alert_message=alert_message,
        add_grade_error=add_grade_error,
        add_grade_flash=add_grade_flash,
        exist_activity_request_change=exist_activity_request_change,
        coment=coment,
        actual_period=actual_period,
        course_ended=course_ended
    )

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def management_activity_without_metric():
    #Check if the period is correct
    if request.vars['year'] is None or request.vars['year'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        year = request.vars['year']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            if cpfecys.current_year_period().id != year.id:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))

    #Check if the project is correct
    if request.vars['project'] is None or request.vars['project'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default','home'))
    else:
        project = request.vars['project']
        project = db(db.project.id == project).select().first()
        if project is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    #Time limit of semester
    date1 = None
    tiempo = str(datetime.now())
    date_inicial_p = db.executesql('SELECT DATE(\'{}\');'.format(tiempo), as_dict=True)
    for d0 in date_inicial_p:
        date1 = d0['DATE(\'{}\')'.format(tiempo)]
    
    date_var = db((db.student_control_period.period_name == (T(year.period.name) + " " + str(year.yearp)))).select().first()
    if date1 >= date_var.date_start_semester and date1 <= date_var.date_finish_semester:
        #Exception of permition
        exception_query = db(db.course_laboratory_exception.project == project.id).select().first()
        exception_s_var = False
        exception_t_var = False
        if exception_query is not None:
            exception_t_var = exception_query.t_edit_lab
            exception_s_var = exception_query.s_edit_course

        #Grid
        grid = None
        db.course_activity_without_metric.assignation.readable = False
        db.course_activity_without_metric.assignation.writable = False
        db.course_activity_without_metric.assignation.default = project.id
        db.course_activity_without_metric.semester.readable = False
        db.course_activity_without_metric.semester.writable = False
        db.course_activity_without_metric.semester.default = year.id
        if auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'):
            query = ((db.course_activity_without_metric.semester == year.id) & (db.course_activity_without_metric.assignation == project.id))
            grid = SQLFORM.grid(query, csv=False, paginate=10, searchable=False)
        elif auth.has_membership('Teacher'):
            assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project)
                        & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
            if assigantion is None:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))
            else:
                if exception_t_var:
                    query = ((db.course_activity_without_metric.semester == year.id) & (db.course_activity_without_metric.assignation == project.id))
                    grid = SQLFORM.grid(query, csv=False, paginate=10, searchable=False)
                else:
                    db.course_activity_without_metric.laboratory.writable = False
                    db.course_activity_without_metric.laboratory.default = False
                    query = ((db.course_activity_without_metric.semester == year.id) & (db.course_activity_without_metric.assignation == project.id)
                            & (db.course_activity_without_metric.laboratory == False))
                    grid = SQLFORM.grid(query, csv=False, paginate=10, searchable=False)
        elif auth.has_membership('Student'):
            assigantion = db((db.user_project.assigned_user==auth.user.id) & (db.user_project.project == project)
                            & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
            if assigantion is None:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))
            else:
                db.course_activity_without_metric.teacher_permition.writable = False
                if exception_s_var:
                    query = ((db.course_activity_without_metric.semester == year.id) & (db.course_activity_without_metric.assignation == project.id))
                    grid = SQLFORM.grid(query, csv=False, paginate=10, searchable=False)
                else:
                    db.course_activity_without_metric.laboratory.writable = False
                    db.course_activity_without_metric.laboratory.default = True
                    query = ((db.course_activity_without_metric.semester == year.id) & (db.course_activity_without_metric.assignation == project.id)
                            & ((db.course_activity_without_metric.laboratory == True) | ((db.course_activity_without_metric.laboratory == False)
                            & (db.course_activity_without_metric.teacher_permition == True))))
                    grid = SQLFORM.grid(query, csv=False, paginate=10, searchable=False)
        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

        return dict(year=year, project=project, grid=grid)
    else:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

@auth.requires_login()
def students_control_full():
    project = request.vars['project']
    assigantion = None
    year = db(db.period_year.id == request.vars['year']).select().first()

    project_var = request.vars['project']
    if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator'):
        #emarquez: adaptacion periodos variables        
        if cpfecys.is_semestre(request.vars['year']):
            assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project_var)
                            & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
        else:
            assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == request.vars['project'])).select(db.user_project.ALL).first()
        #emarquez

        if assigantion is None:
            academic_var = db(db.academic.carnet == auth.user.username).select().first()
            try:
                academic_assig = db((db.academic_course_assignation.carnet == academic_var.id) & (db.academic_course_assignation.semester == year.id) 
                                & (db.academic_course_assignation.assignation == project_var) ).select().first()
                if academic_assig is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'home'))
            except:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))

    return dict(name = '', semester=year.period.name, year=year.yearp, assigantion=assigantion)

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def validate_laboratory():
    #Check if the period is correct
    if request.vars['year'] is None or request.vars['year'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        year = request.vars['year']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator'):
                if cpfecys.current_year_period().id != year.id:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'home'))

    #Check if the project is correct
    if request.vars['project'] is None or request.vars['project'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        project = request.vars['project']
        project = db(db.project.id == project).select().first()
        if project is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator'):
                assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project)
                                & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
                if assigantion is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'home'))

    #Grid
    query = ((db.validate_laboratory.semester == year.id) & (db.validate_laboratory.project == project.id)
            & (db.validate_laboratory.validation_type == True))
    grid = None
    db.validate_laboratory.id.readable = False
    db.validate_laboratory.id.writable = False
    db.validate_laboratory.project.readable = False
    db.validate_laboratory.project.writable = False
    db.validate_laboratory.project.default = project.id
    db.validate_laboratory.semester.readable = False
    db.validate_laboratory.semester.writable = False
    db.validate_laboratory.semester.default = year.id
    db.validate_laboratory.validation_type.readable = False
    db.validate_laboratory.validation_type.writable = False
    db.validate_laboratory.validation_type.default = True
    if cpfecys.current_year_period().id != year.id:
        no_actions_all = True
        if auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'):
            if 'edit' in request.args:
                db.validate_laboratory.carnet.writable = False
                grid = SQLFORM.grid(query, csv=False, paginate=10, oncreate=oncreate_validate_laboratory, onupdate=onupdate_validate_laboratory, ondelete=ondelete_validate_laboratory, searchable=False)
            else:
                grid = SQLFORM.grid(query, csv=False, paginate=10, deletable=False, oncreate=oncreate_validate_laboratory, onupdate=onupdate_validate_laboratory, ondelete=ondelete_validate_laboratory, searchable=False)
        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
    else:
        no_actions_all=False

        #Check if the course has endend
        course_ended_var = db((db.course_ended.project == project.id) & (db.course_ended.period == year.id)).select().first()
        if course_ended_var != None:
            if course_ended_var.finish:
                no_actions_all = True

        #Check the time of the semester is not over
        if not no_actions_all:
            #Time limit of semester parameter
            date1 = None
            tiempo = str(datetime.now())
            date_inicial_p = db.executesql('SELECT DATE(\'{}\');'.format(tiempo), as_dict=True)
            for d0 in date_inicial_p:
                date1 = d0['DATE(\'{}\')'.format(tiempo)]
            
            date_var = db((db.student_control_period.period_name == (T(year.period.name) + " " + str(year.yearp)))).select().first()
            if date1 >= date_var.date_start_semester and date1 <= date_var.date_finish_semester:
                if year.period == 1:
                    (start, end) = start_end_time(year, '-01-01', '-06-01')
                    if date1 < start and date1 > end:
                        no_actions_all = True
                else:
                    (start, end) = start_end_time(year, '-06-01', '-12-31')    
                    if date1 < start and date1 > end:
                        no_actions_all = True
            else:
                no_actions_all = True

        #If is teacher, check if he has permitions
        if not no_actions_all and auth.has_membership('Teacher'):
            exception_query = db(db.course_laboratory_exception.project == project.id).select().first()
            if exception_query is not None and not exception_query.t_edit_lab:
                    no_actions_all = True
            else:
                no_actions_all = True

        #Show options
        if not no_actions_all:
            if 'edit' in request.args:
                db.validate_laboratory.carnet.writable = False
                grid = SQLFORM.grid(query, csv=False, paginate=10, oncreate=oncreate_validate_laboratory, onupdate=onupdate_validate_laboratory, ondelete=ondelete_validate_laboratory, searchable=False)
            else:
                grid = SQLFORM.grid(query, csv=False, paginate=10, oncreate=oncreate_validate_laboratory, onupdate=onupdate_validate_laboratory, ondelete=ondelete_validate_laboratory, searchable=False)
        else:
            if auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'):
                if 'edit' in request.args:
                    db.validate_laboratory.carnet.writable = False
                    grid = SQLFORM.grid(query, csv=False, paginate=10, oncreate=oncreate_validate_laboratory, onupdate=onupdate_validate_laboratory, ondelete=ondelete_validate_laboratory, searchable=False)
                else:
                    grid = SQLFORM.grid(query, csv=False, paginate=10, deletable=False, oncreate=oncreate_validate_laboratory, onupdate=onupdate_validate_laboratory, ondelete=ondelete_validate_laboratory, searchable=False)
            else:
                grid = SQLFORM.grid(query, csv=False, create=False, editable=False, deletable=False, paginate=10, searchable=False)


    academic_assig3 = db((db.academic.id == db.academic_course_assignation.carnet) & (db.academic_course_assignation.semester == request.vars['year']) 
                        & (db.academic_course_assignation.assignation == request.vars['project'])).select(orderby=db.academic.carnet)
    students = []
    for aca_t in academic_assig3:
        students.append(aca_t.academic_course_assignation)
    
    return dict(year=year, project=project, grid=grid, students=students, no_actions_all=no_actions_all)

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def laboratory_replacing():
    #Check if the period is correct
    if request.vars['year'] is None or request.vars['year'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        year = request.vars['year']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator'):
                if cpfecys.current_year_period().id != year.id:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'home'))

    #Check if the project is correct
    if request.vars['project'] is None or request.vars['project'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        project = request.vars['project']
        project = db(db.project.id == project).select().first()
        if project is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator'):
                assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project)
                                & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
                if assigantion is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'home'))

    #Grid
    query = ((db.validate_laboratory.semester == year.id) & (db.validate_laboratory.project == project.id)
            & (db.validate_laboratory.validation_type == False))
    grid = None
    db.validate_laboratory.id.readable = False
    db.validate_laboratory.id.writable = False
    db.validate_laboratory.project.readable = False
    db.validate_laboratory.project.writable = False
    db.validate_laboratory.project.default = project.id
    db.validate_laboratory.semester.readable = False
    db.validate_laboratory.semester.writable = False
    db.validate_laboratory.semester.default = year.id
    db.validate_laboratory.validation_type.readable = False
    db.validate_laboratory.validation_type.writable = False
    db.validate_laboratory.validation_type.default = False

    if cpfecys.current_year_period().id != year.id:
        no_actions_all = True
        if auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'):
            _carnet = str(db(db.academic.id == int(row.carnet)).select(db.academic.carnet).first().carnet)
            _description = str(db((db.validate_laboratory_log.period == T(year.period.name)) & (db.validate_laboratory_log.yearp == year.yearp)
                                & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.validation_type == False)
                                & (db.validate_laboratory_log.academic == str(db(db.academic.id == int(row.carnet)).select(db.academic.carnet).first().carnet))).select(db.validate_laboratory_log.description).last().description)
            on_click_string = 'set_values("{}", "{}")'.format(_carnet, _description)
            links = [lambda row: A(T('Reason'), _role='button', _class='btn btn-info', _onclick=on_click_string, _title=T('Reason for Equivalence Laboratory'),**{"_data-toggle":"modal", "_data-target": "#modaltheme"})]
            if 'edit' in request.args:
                db.validate_laboratory.carnet.writable = False
                grid = SQLFORM.grid(query, csv=False, paginate=10, oncreate=oncreate_laboratory_replacing, onupdate=onupdate_laboratory_replacing, searchable=False, links=links)
            else:
                grid = SQLFORM.grid(query, csv=False, paginate=10, deletable=False, oncreate=oncreate_laboratory_replacing, onupdate=onupdate_laboratory_replacing, searchable=False, links=links)
        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
    else:
        no_actions_all = False

        #Check if the course has endend
        course_ended_var = db((db.course_ended.project == project.id) & (db.course_ended.period == year.id)).select().first()
        if course_ended_var != None and course_ended_var.finish:
                no_actions_all = True

        #Check the time of the semester is not over
        if not no_actions_all:
            #Time limit of semester parameter
            date1 = None
            tiempo = str(datetime.now())
            date_inicial_p = db.executesql('SELECT date(\'{}\');'.format(tiempo), as_dict=True)
            for d0 in date_inicial_p:
                date1 = d0['DATE(\'{}\')'.format(tiempo)]
            
            date_var = db((db.student_control_period.period_name == (T(year.period.name) + " " + str(year.yearp)))).select().first()
            if date1 >= date_var.date_start_semester and date1 <= date_var.date_finish_semester:
                if year.period == 1:
                    (start, end) = start_end_time(year, '-01-01', '-06-01')
                    if date1 < start and date1 > end:
                        no_actions_all = True
                else:
                    (start, end) = start_end_time(year, '-06-01', '-12-31')
                    if date1 < start and date1 > end:
                        no_actions_all = True
            else:
                no_actions_all = True

        #If is teacher, check if he has permitions
        if not no_actions_all and auth.has_membership('Teacher'):
            exception_query = db(db.course_laboratory_exception.project == project.id).select().first()
            if exception_query is not None and not exception_query.t_edit_lab:
                no_actions_all = True
            else:
                no_actions_all = True

        #Show options
        if not no_actions_all:
            _carnet = str(db(db.academic.id == int(row.carnet)).select(db.academic.carnet).first().carnet)
            _description = str(db((db.validate_laboratory_log.period == T(year.period.name)) & (db.validate_laboratory_log.yearp == year.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.validation_type == False)
                            & (db.validate_laboratory_log.academic == str(db(db.academic.id == int(row.carnet)).select(db.academic.carnet).first().carnet))).select(db.validate_laboratory_log.description).last().description)
            on_click_string = 'set_values("{}", "{}")'.format(_carnet, _description)
            links = [lambda row: A(T('Reason'), _role='button', _class='btn btn-info', _onclick=on_click_string,
                    _title=T('Reason for Equivalence Laboratory'),**{"_data-toggle":"modal", "_data-target": "#modaltheme"})]
            if 'edit' in request.args:
                db.validate_laboratory.carnet.writable = False
                grid = SQLFORM.grid(query, csv=False, paginate=10, oncreate=oncreate_laboratory_replacing, onupdate=onupdate_laboratory_replacing, searchable=False, links=links)
            else:
                grid = SQLFORM.grid(query, csv=False, paginate=10, deletable=False, oncreate=oncreate_laboratory_replacing, onupdate=onupdate_laboratory_replacing, searchable=False, links=links)
        else:
            _carnet = str(db(db.academic.id == int(row.carnet)).select(db.academic.carnet).first().carnet)
            _description = str(db((db.validate_laboratory_log.period == T(year.period.name)) & (db.validate_laboratory_log.yearp == year.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.validation_type == False)
                            & (db.validate_laboratory_log.academic == str(db(db.academic.id == int(row.carnet)).select(db.academic.carnet).first().carnet))).select(db.validate_laboratory_log.description).last().description)
            on_click_string = 'set_values("{}", "{}")'.format(_carnet, _description)
            links = [lambda row: A(T('Reason'), _role='button', _class='btn btn-info', _onclick=on_click_string,
                    _title=T('Reason for Equivalence Laboratory'),**{"_data-toggle":"modal", "_data-target": "#modaltheme"})]
            if auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'):
                if 'edit' in request.args:
                    db.validate_laboratory.carnet.writable = False
                    grid = SQLFORM.grid(query, csv=False, paginate=10, oncreate=oncreate_laboratory_replacing, onupdate=onupdate_laboratory_replacing, searchable=False, links=links)
                else:
                    grid = SQLFORM.grid(query, csv=False, paginate=10, deletable=False, oncreate=oncreate_laboratory_replacing, onupdate=onupdate_laboratory_replacing, searchable=False, links=links)
            else:
                grid = SQLFORM.grid(query, csv=False, create=False, editable=False, deletable=False, paginate=10, searchable=False, links=links)


    academic_assig3 = db((db.academic.id == db.academic_course_assignation.carnet) & (db.academic_course_assignation.semester == request.vars['year']) 
                        & (db.academic_course_assignation.assignation == request.vars['project'])).select(orderby=db.academic.carnet)
    students = []
    for aca_t in academic_assig3:
        students.append(aca_t.academic_course_assignation)
    
    return dict(year=year, project=project, grid=grid, students=students)

@auth.requires_login()
@auth.requires(auth.has_membership('Student'))
def request_change_activity():
    #Obtener al tutor del proyecto
    check = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == request.vars['project'])
            & ((db.user_project.period <= int(request.vars['year'])) & ((db.user_project.period + db.user_project.periods) > int(request.vars['year'])))).select(db.user_project.ALL).first()

    if check is None:
        redirect(URL('default','home'))

    year = db.period_year(id=check.period)
    year_semester = db.period(id=year.period)

    return dict(
        name=check.project.name,
        semester=year_semester.name,
        semestre2=year,
        year=year.yearp,
        assignation=check.id
    )

@auth.requires_login()
@auth.requires(auth.has_membership('Student'))
def request_change_weighting():
    year = db(db.period_year.id == request.vars['year']).select().first()
    year_semester = year.period

    assignation = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == request.vars['project']) 
                    & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
    if assignation is None:
        session.flash = T("Action not allowed")
        redirect(URL('default', 'home'))

    check = db(db.project.id == request.vars['project']).select().first()
    try:
        if request.vars['operation'] == "cancel":
            db((db.request_change_weighting.period == year.id) & (db.request_change_weighting.project == request.vars['project']) 
            & ((db.request_change_weighting.status != 'accepted') & (db.request_change_weighting.status != 'rejected'))).delete()
            response.flash = T("Request has been canceled")
        if (request.args(0) == 'request'):
            if str(request.vars['description']) == "":
                response.flash = "Error. {}".format(T("Please enter a description"))
            else:
                total_var2 = float(0)
                if request.vars['type'] != 'course':
                    for project in db((db.course_activity_category.semester == year.id) & (db.course_activity_category.assignation == request.vars['project']) & (db.course_activity_category.laboratory == True)).select():
                        total_var2 += float(project.grade)

                select_change = db((db.request_change_weighting.status == 'edit') & (db.request_change_weighting.period == int(year.id))
                                & (db.request_change_weighting.project == request.vars['project'])).select().first()
                for detail_rc in db((db.request_change_weighting_detail.request_change_weighting == select_change.id)).select():
                    if detail_rc.operation_request == 'insert':
                        total_var2 += float(detail_rc.grade)

                    if detail_rc.operation_request == 'update':
                        total_var2 -= float(detail_rc.course_category.grade)
                        total_var2 += float(detail_rc.grade)

                    if detail_rc.operation_request == 'delete':
                        total_var2 -= float(detail_rc.course_category.grade)

                if total_var2 != float(100):
                    if total_var2 != None:
                        response.flash = "Error. {}: {}".format(T("The sum of the weighting is incorrect"), str(total_var2))
                else:
                    temp = db((db.request_change_weighting.period == year.id) & (db.request_change_weighting.project == request.vars['project']) 
                            & ((db.request_change_weighting.status != 'accepted') & (db.request_change_weighting.status != 'rejected'))).select().first()
                    db((db.request_change_weighting.id == temp.id)).update(status='pending', description=str(request.vars['description']), date_request=datetime.datetime.now())
                    
                    #LOG
                    temp2 = db.request_change_w_log.insert(
                        r_c_w_id=temp.id,
                        username=auth.user.username,
                        roll='Student',
                        before_status='edit',
                        after_status='pending',
                        description=str(request.vars['description']),
                        semester=year_semester.name,
                        yearp=str(year.yearp),
                        project=str(check.name)
                    )

                    #LOG_DETAIL
                    r_c_w_d_var = db((db.request_change_weighting_detail.request_change_weighting == temp)).select()
                    for var_temp in r_c_w_d_var:
                        if var_temp.operation_request == 'insert':
                            cat_temp = db(db.activity_category.id == var_temp.category).select().first()
                            db.request_change_w_detail_log.insert(
                                request_change_w_log=temp2,
                                operation_request=var_temp.operation_request,
                                category=cat_temp.category,
                                after_grade=var_temp.grade,
                                after_specific_grade=var_temp.specific_grade
                            )
                        elif var_temp.operation_request == 'delete':
                            cat_temp = db(db.course_activity_category.id == var_temp.course_category).select().first()
                            db.request_change_w_detail_log.insert(
                                request_change_w_log=temp2,
                                operation_request=var_temp.operation_request,
                                course_category=cat_temp.category.category,
                                before_grade=cat_temp.grade,
                                before_specific_grade=cat_temp.specific_grade
                            )
                        elif var_temp.operation_request == 'update':
                            cat_temp = db(db.course_activity_category.id == var_temp.course_category).select().first()
                            cat_temp2 = db(db.activity_category.id == var_temp.category).select().first()
                            db.request_change_w_detail_log.insert(
                                request_change_w_log=temp2,
                                operation_request=var_temp.operation_request,
                                course_category=cat_temp.category.category,
                                category=cat_temp2.category,
                                before_grade=cat_temp.grade,
                                after_specific_grade=var_temp.specific_grade,
                                after_grade=var_temp.grade,
                                before_specific_grade=cat_temp.specific_grade
                            )

                    project_name = check.name
                    project_id = check.id

                    #Message
                    try:
                        check = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == request.vars['project'])
                                & ((db.user_project.period <= int(request.vars['year'])) & ((db.user_project.period + db.user_project.periods) > int(request.vars['year']) ))).select(db.user_project.ALL).first()

                        users2 = db((db.auth_user.id == db.user_project.assigned_user) & (db.user_project.project == request.vars['project'])
                                & ((db.user_project.period <= int(request.vars['year']) ) & ((db.user_project.period + db.user_project.periods) > int(request.vars['year']) ))
                                & (db.auth_membership.user_id == db.user_project.assigned_user) & (db.auth_membership.group_id==3)).select().first()

                        subject = "Solicitud de cambio de ponderación - {}".format(project_name)
                        message2 = "<br>Por este medio se le informa que el(la) practicante {} {} ha creado una solicitud de cambio en la ponderación del laboratorio del Curso de \"{}\".".format(check.assigned_user.first_name, check.assigned_user.last_name, project_name)
                        message2 += "<br>Para aceptar o rechazar dicha solicitud dirigirse al control de solicitudes o al siguiente link: {}cpfecys/activity_control/solve_request_change_weighting?course={}".format(cpfecys.get_domain(), str(project_id))
                        message2 += "<br>Saludos.<br><br>Sistema de Seguimiento de La Escuela de Ciencias y Sistemas<br>Facultad de Ingeniería - Universidad de San Carlos de Guatemala</html>"
                        
                        #Send Mail to the Teacher
                        message = "<html>Catedratico(a) {} {} reciba un cordial saludo.<br>".format(users2.auth_user.first_name, users2.auth_user.last_name)
                        message3 = message + message2
                        fail1 = send_mail_to_students(message3, subject, users2.auth_user.email, check,year_semester.name,year.yearp)
                        
                        if fail1 == 1:
                            response.flash = "{} - {}".format(T("Request has been sent"), T("Failed to send email to teacher"))
                        else:
                            response.flash = "{} - {}".format(T("Request has been sent"), T("Sent email to teacher"))
                    except:
                        None

                    return dict(
                        name=project_name,
                        semester=year_semester.name,
                        year=year.yearp,
                        semestre2=year,
                        project=request.vars['project'],
                        assignation=assignation
                    )
    except:
        None

    return dict(
        name=check.name,
        semester=year_semester.name,
        year=year.yearp,
        semestre2=year,
        project=request.vars['project'],
        assignation=assignation
    )

@auth.requires_login()
def weighting():
    project = request.vars['project']
    rol_log = rol_log()
    project_var = db(db.project.id == project).select().first()
    year = db(db.period_year.id == request.vars['year']).select().first()

    #emarquez: adaptacion periodos variables
    if cpfecys.is_semestre(request.vars['year']):
        assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project)
                    & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
    else:
        assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == request.vars['project'])).select(db.user_project.ALL).first()

    #emarquez
    assigned_to_project = False if assigantion is None else True

    #emarquez: adaptacion periodos variables
    if cpfecys.is_semestre(request.vars['year']):
        exception_query = db(db.course_laboratory_exception.project == request.vars['project']).select().first() 
    else:
        exception_query = db(db.course_laboratory_exception_period.project == request.vars['project']).select().first()

    if exception_query is None:
        exception_s_var = False
        exception_t_var = False
    else:
        exception_t_var = exception_query.t_edit_lab
        exception_s_var = exception_query.s_edit_course

    no_menu = True
    if (auth.has_membership('Super-Administrator')) or (auth.has_membership('Ecys-Administrator')) or (auth.has_membership('Teacher') and request.vars['type'] == "course"  and assigned_to_project) or (auth.has_membership('Student') and request.vars['type'] == "lab" and assigned_to_project) or (auth.has_membership('Student') and request.vars['type'] == "course" and exception_s_var and assigned_to_project) or (auth.has_membership('Teacher')  and request.vars['type'] == "lab" and exception_t_var and assigned_to_project):
        if cpfecys.is_semestre(request.vars['year']):
            if str(request.vars['year']) == str(cpfecys.current_year_period().id):
                no_menu = False
        else:
            no_menu = False

    enddate = None
    #emarquez: adaptacion periodos variables: lo que esta dentro del if , si es semestre, quedo intacto, se agrega else para periodos variables
    if cpfecys.is_semestre(request.vars['year']):
        for date_var in db((db.student_control_period.period_name == T(str(year.period.name)) + " " + str(year.yearp))).select():
            var_exception = db((db.course_limit_exception.project == request.vars['project']) & (db.course_limit_exception.date_finish > datetime.now())).select().first()
            if var_exception != None:
                var_date_finish = var_exception.date_finish
            else:
                var_date_finish = date_var.date_finish
            
            if datetime.now() > date_var.date_start and datetime.now() < var_date_finish:
                enddate = var_date_finish
    else:   
        for date_var in db((db.period_detail.period == cpfecys.get_period_from_periodyear(year))).select():
            var_exception = db((db.course_limit_exception_period.project == request.vars['project']) & (db.course_limit_exception_period.period == cpfecys.get_period_from_periodyear(year)) 
                            & (db.course_limit_exception_period.date_finish > datetime.now())).select().first()
            if var_exception != None:
                var_date_finish = var_exception.date_finish
            else:
                var_date_finish = date_var.date_finish

            if datetime.now() > date_var.date_start and datetime.now() < var_date_finish:
                enddate = var_date_finish

    exception_query = db(db.course_laboratory_exception.project == request.vars['project']).select().first()
    if exception_query is None:
        exception_s_var = False
        exception_t_var = False
    else:
        exception_t_var = exception_query.t_edit_lab
        exception_s_var = exception_query.s_edit_course

    temp_op = request.vars['op']
    if ((not auth.has_membership('Super-Administrator')) & (not auth.has_membership('Ecys-Administrator'))) & ((((not auth.has_membership('Teacher')) & (no_menu or enddate == None) & (not exception_s_var)) or ((auth.has_membership('Teacher')) & (no_menu))) & (temp_op == "updateCategory" or temp_op == "addCategory" or temp_op == "getPreviousWeighting" or temp_op == "removeCategory")):
        return "<center> {} </center>".format(T("Action not allowed"))

    return dict(semestre2=year, project=project, project_variable=project_var,assigantion=assigantion, rol_log=rol_log)

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def course_first_recovery_test():
    #Check if the period is correct
    if request.vars['year'] is None or request.vars['year'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        year = request.vars['year']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    #Check if the project is correct
    if request.vars['project'] is None or request.vars['project'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        project = request.vars['project']
        project = db(db.project.id == project).select().first()
        if project is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    #Time limit of semester
    date1 = None
    tiempo = str(datetime.now())
    date_inicial_p = db.executesql('SELECT DATE(\'{}\');'.format(tiempo), as_dict=True)
    for d0 in date_inicial_p:
        date1=d0['DATE(\'{}\')'.format(tiempo)]

    date_var = db((db.student_control_period.period_name == (T(year.period.name) + " " + str(year.yearp)))).select().first()

    #Exception of permition
    exception_query = db(db.course_laboratory_exception.project == project.id).select().first()
    exception_s_var = False
    exception_t_var = False
    if exception_query is not None:
        exception_t_var = exception_query.t_edit_lab
        exception_s_var = exception_query.s_edit_course

    #Check if the course has endend
    no_actions_all = False
    course_ended_var = db((db.course_ended.project == project.id) & (db.course_ended.period == year.id)).select().first()
    if course_ended_var != None:
        if not course_ended_var.finish:
            session.flash = T('Course hasn’t finalized.')
            redirect(URL('default', 'home'))
    else:
        session.flash = T('Course hasn’t finalized.')
        redirect(URL('default', 'home'))

    #Grid
    grid = None
    db.course_first_recovery_test.id.readable = False
    db.course_first_recovery_test.id.writable = False
    db.course_first_recovery_test.project.readable = False
    db.course_first_recovery_test.project.writable = False
    db.course_first_recovery_test.project.default = project.id
    db.course_first_recovery_test.semester.readable = False
    db.course_first_recovery_test.semester.writable = False
    db.course_first_recovery_test.semester.default = year.id

    if auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'):
        query = ((db.course_first_recovery_test.semester == year.id) & (db.course_first_recovery_test.project == project.id))
        if cpfecys.current_year_period().id == year.id and not no_actions_all:
            if 'edit' in request.args:
                db.course_first_recovery_test.carnet.writable = False
                grid = SQLFORM.grid(query, csv=False, paginate=50, oncreate=oncreate_course_first_recovery_test, onupdate=onupdate_course_first_recovery_test, ondelete=ondelete_course_first_recovery_test, searchable=False)
            else:
                grid = SQLFORM.grid(query, csv=False, paginate=50, oncreate=oncreate_course_first_recovery_test, onupdate=onupdate_course_first_recovery_test, ondelete=ondelete_course_first_recovery_test, searchable=False)
        else:
            if 'edit' in request.args:
                db.course_first_recovery_test.carnet.writable = False
                grid = SQLFORM.grid(query, csv=False, paginate=50, oncreate=oncreate_course_first_recovery_test, onupdate=onupdate_course_first_recovery_test, ondelete=ondelete_course_first_recovery_test, searchable=False)
            else:
                grid = SQLFORM.grid(query, csv=False, paginate=50, oncreate=oncreate_course_first_recovery_test, onupdate=onupdate_course_first_recovery_test, ondelete=ondelete_course_first_recovery_test, searchable=False)
    elif auth.has_membership('Student'):
        assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project)
                    & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
        if assigantion is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            if exception_s_var and not no_actions_all:
                query = ((db.course_first_recovery_test.semester == year.id) & (db.course_first_recovery_test.project == project.id))
                if 'edit' in request.args:
                    db.course_first_recovery_test.carnet.writable = False
                    grid = SQLFORM.grid(query, csv=False, paginate=50, oncreate=oncreate_course_first_recovery_test, onupdate=onupdate_course_first_recovery_test, ondelete=ondelete_course_first_recovery_test, searchable=False)
                else:
                    grid = SQLFORM.grid(query, csv=False, paginate=50, oncreate=oncreate_course_first_recovery_test, onupdate=onupdate_course_first_recovery_test, ondelete=ondelete_course_first_recovery_test, searchable=False)
            else:
                query = ((db.course_first_recovery_test.semester == year.id) & (db.course_first_recovery_test.project == project.id))
                grid = SQLFORM.grid(query, csv=False, create=False, editable=False, deletable=False, paginate=50, searchable=False)
    elif auth.has_membership('Teacher'):
        assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project)
                    & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
        if assigantion is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            if not no_actions_all:
                query = ((db.course_first_recovery_test.semester == year.id) & (db.course_first_recovery_test.project == project.id))
                if 'edit' in request.args:
                    db.course_first_recovery_test.carnet.writable = False
                    grid = SQLFORM.grid(query, csv=False, paginate=50, oncreate=oncreate_course_first_recovery_test, onupdate=onupdate_course_first_recovery_test, ondelete=ondelete_course_first_recovery_test, searchable=False)
                else:
                    grid = SQLFORM.grid(query, csv=False, paginate=50, oncreate=oncreate_course_first_recovery_test, onupdate=onupdate_course_first_recovery_test, ondelete=ondelete_course_first_recovery_test, searchable=False)
            else:
                query = ((db.course_first_recovery_test.semester == year.id) & (db.course_first_recovery_test.project == project.id))
                grid = SQLFORM.grid(query, csv=False, create=False, editable=False, deletable=False, paginate=50, searchable=False)
    else:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    academic_assig3 = db((db.academic.id == db.academic_course_assignation.carnet) & (db.academic_course_assignation.semester == request.vars['year']) 
                    & (db.academic_course_assignation.assignation == request.vars['project'])).select(orderby=db.academic.carnet)
    students = []
    for aca_t in academic_assig3:
        students.append(aca_t.academic_course_assignation)

    return dict(year=year, project=project, grid=grid, students=students)

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def course_second_recovery_test():
    #Check if the period is correct
    if request.vars['year'] is None or request.vars['year'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        year = request.vars['year']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    #Check if the project is correct
    if request.vars['project'] is None or request.vars['project'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        project = request.vars['project']
        project = db(db.project.id == project).select().first()
        if project is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    #Time limit of semester
    date1 = None
    tiempo = str(datetime.now())
    date_inicial_p = db.executesql('SELECT DATE(\'{}\');'.format(tiempo), as_dict=True)
    for d0 in date_inicial_p:
        date1 = d0['DATE(\'{}\')'.format(tiempo)]
    date_var = db((db.student_control_period.period_name == ("{} {}".format(T(year.period.name), str(year.yearp))))).select().first()

    #Exception of permition
    exception_query = db(db.course_laboratory_exception.project == project.id).select().first()
    exception_s_var = False
    exception_t_var = False
    if exception_query is not None:
        exception_t_var = exception_query.t_edit_lab
        exception_s_var = exception_query.s_edit_course

    #Check if the course has endend
    no_actions_all = False
    course_ended_var = db((db.course_ended.project == project.id) & (db.course_ended.period == year.id)).select().first()
    if course_ended_var != None:
        if not course_ended_var.finish:
            session.flash = T('Course hasn’t finalized.')
            redirect(URL('default', 'home'))
    else:
        session.flash = T('Course hasn’t finalized.')
        redirect(URL('default', 'home'))

    #Grid
    grid = None
    db.course_second_recovery_test.id.readable = False
    db.course_second_recovery_test.id.writable = False
    db.course_second_recovery_test.project.readable = False
    db.course_second_recovery_test.project.writable = False
    db.course_second_recovery_test.project.default = project.id
    db.course_second_recovery_test.semester.readable = False
    db.course_second_recovery_test.semester.writable = False
    db.course_second_recovery_test.semester.default = year.id
    if auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'):
        query = ((db.course_second_recovery_test.semester == year.id) & (db.course_second_recovery_test.project == project.id))
        if cpfecys.current_year_period().id == year.id and not no_actions_all:
            if 'edit' in request.args:
                db.course_second_recovery_test.carnet.writable = False
                grid = SQLFORM.grid(query, csv=False, paginate=50, oncreate=oncreate_course_second_recovery_test, onupdate=onupdate_course_second_recovery_test, ondelete=ondelete_course_second_recovery_test, searchable=False)
            else:
                grid = SQLFORM.grid(query, csv=False, paginate=50, oncreate=oncreate_course_second_recovery_test, onupdate=onupdate_course_second_recovery_test, ondelete=ondelete_course_second_recovery_test, searchable=False)
        else:
            if 'edit' in request.args:
                db.course_second_recovery_test.carnet.writable = False
                grid = SQLFORM.grid(query, csv=False, paginate=50, oncreate=oncreate_course_second_recovery_test, onupdate=onupdate_course_second_recovery_test, ondelete=ondelete_course_second_recovery_test, searchable=False)
            else:
                grid = SQLFORM.grid(query, csv=False, paginate=50, oncreate=oncreate_course_second_recovery_test, onupdate=onupdate_course_second_recovery_test, ondelete=ondelete_course_second_recovery_test, searchable=False)
    elif auth.has_membership('Student'):
        assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project)
                    & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
        if assigantion is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            if exception_s_var and not no_actions_all:
                query = ((db.course_second_recovery_test.semester == year.id) & (db.course_second_recovery_test.project == project.id))
                if 'edit' in request.args:
                    db.course_second_recovery_test.carnet.writable = False
                    grid = SQLFORM.grid(query, csv=False, paginate=50, oncreate=oncreate_course_second_recovery_test, onupdate=onupdate_course_second_recovery_test, ondelete=ondelete_course_second_recovery_test, searchable=False)
                else:
                    grid = SQLFORM.grid(query, csv=False, paginate=50, oncreate=oncreate_course_second_recovery_test, onupdate=onupdate_course_second_recovery_test, ondelete=ondelete_course_second_recovery_test, searchable=False)
            else:
                query = ((db.course_second_recovery_test.semester == year.id) & (db.course_second_recovery_test.project == project.id))
                grid = SQLFORM.grid(query, csv=False, create=False, editable=False, deletable=False, paginate=50, searchable=False)
    elif auth.has_membership('Teacher'):
        assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project)
                    & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
        if assigantion is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            if not no_actions_all:
                query = ((db.course_second_recovery_test.semester == year.id) & (db.course_second_recovery_test.project == project.id))
                if 'edit' in request.args:
                    db.course_second_recovery_test.carnet.writable = False
                    grid = SQLFORM.grid(query, csv=False, paginate=50, oncreate=oncreate_course_second_recovery_test, onupdate=onupdate_course_second_recovery_test, ondelete=ondelete_course_second_recovery_test, searchable=False)
                else:
                    grid = SQLFORM.grid(query, csv=False, paginate=50, oncreate=oncreate_course_second_recovery_test, onupdate=onupdate_course_second_recovery_test, ondelete=ondelete_course_second_recovery_test, searchable=False)
            else:
                query = ((db.course_second_recovery_test.semester == year.id) & (db.course_second_recovery_test.project == project.id))
                grid = SQLFORM.grid(query, csv=False, create=False, editable=False, deletable=False, paginate=50, searchable=False)
    else:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    academic_assig3 = db((db.academic.id == db.academic_course_assignation.carnet) & (db.academic_course_assignation.semester == request.vars['year']) 
                    & (db.academic_course_assignation.assignation == request.vars['project'])).select(orderby=db.academic.carnet)
    students = []
    for aca_t in academic_assig3:
        students.append(aca_t.academic_course_assignation)

    return dict(year=year, project=project, grid=grid, students=students)

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def course_requirement():
    #vars
    year = None
    project_var = None

    #Check if the period is correct
    if request.vars['period'] is None or request.vars['period'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        year = request.vars['period']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator'):
                if cpfecys.current_year_period().id != year.id:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'home'))

    #Check if the period is correct
    if request.vars['project'] is None or request.vars['project']=='':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        project_var = request.vars['project']
        project_var = db(db.project.id == project_var).select().first()
        if project_var is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator'):
        assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project_var.id)
                    & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
        if assigantion is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    #Exception of permition
    exception_query = db(db.course_laboratory_exception.project == project_var.id).select().first()
    exception_s_var = False
    if exception_query is not None:
        exception_s_var = exception_query.s_edit_course
    #Check if the course has endend
    no_actions_all = False
    course_ended_var = db((db.course_ended.project == project_var.id) & (db.course_ended.period == year.id)).select().first()
    if course_ended_var != None and course_ended_var.finish:
            no_actions_all = True
    
    #Grid
    activityPermition = db((db.course_requirement.semester == year.id) & (db.course_requirement.project == project_var.id)).select().first()
    grid = None
    db.course_requirement.id.readable = False
    db.course_requirement.id.writable = False
    db.course_requirement.project.readable = False
    db.course_requirement.project.writable = False
    db.course_requirement.project.default = project_var.id
    db.course_requirement.semester.readable = False
    db.course_requirement.semester.writable = False
    db.course_requirement.semester.default = year.id
    
    links = [lambda row: A(T('Management approval of students'), _role='button', _class='btn btn-success',
        _href=URL('activity_control', 'management_approval_students_requirement', vars=dict(project = project_var.id, period = year.id, requirement=row.id)),
        _title=T('Edit academic information'))]
    
    if auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'):
        query = ((db.course_requirement.semester == year.id) & (db.course_requirement.project == project_var.id))
        if activityPermition is None:
            grid = SQLFORM.grid(query, csv=False, paginate=1, searchable=False, links=links)
        else:
            grid = SQLFORM.grid(query, csv=False, paginate=1, create=False, searchable=False, links=links)
    elif auth.has_membership('Teacher'):
        query = ((db.course_requirement.semester == year.id) & (db.course_requirement.project == project_var.id))
        if not no_actions_all:
            if activityPermition is None:
                grid = SQLFORM.grid(query, csv=False, paginate=1, searchable=False, links=links)
            else:
                grid = SQLFORM.grid(query, csv=False, paginate=1, create=False, searchable=False, links=links)
        else:
            grid = SQLFORM.grid(query, csv=False, create=False, editable=False, deletable=False, searchable=False, links=links)
    elif auth.has_membership('Student'):
        query = ((db.course_requirement.semester == year.id) & (db.course_requirement.project == project_var.id))
        if not no_actions_all:
            if exception_s_var or activityPermition.teacher_permition:
                db.course_requirement.teacher_permition.default = False
                db.course_requirement.teacher_permition.writable = False
                if activityPermition is None:
                    grid = SQLFORM.grid(query, csv=False, paginate=1, searchable=False, links=links)
                else:
                    grid = SQLFORM.grid(query, csv=False, paginate=1, create=False, searchable=False, links=links)
            else:
                grid = SQLFORM.grid(query, csv=False, create=False, editable=False, deletable=False, searchable=False, links=links)
        else:
            grid = SQLFORM.grid(query, csv=False, create=False, editable=False, deletable=False, searchable=False, links=links)
    else:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    return dict(project=project_var, year=year, grid=grid)

#se realizo merge
@auth.requires_login()
def update_grade():
    activity = request.vars['activity']
    project = request.vars['project']
    year = request.vars['year']
    carnet = request.vars['carnet']
    grade = request.vars['grade']
    coment = request.vars['coment']

    if carnet != '':
        var_activity = db(db.course_activity.id == activity).select().first()
        academic_var =  db(db.academic.carnet == carnet).select().first()
        assig_var =  db((db.academic_course_assignation.assignation == project) & (db.academic_course_assignation.semester == year) 
                    & (db.academic_course_assignation.carnet == academic_var.id)).select().first()

        grade_before = db((db.grades.academic_assignation == assig_var.id) & (db.grades.activity == activity)).select().first()
        grade_new = db(db.grades.id == grade_before.id).update(grade=grade)

        #obtengo el rol del log
        rol_log = get_rol() 
        #log
        db.grades_log.insert(
            user_name=auth.user.username,
            roll=rol_log,
            operation_log='update',
            academic_assignation_id=assig_var.id,
            academic=assig_var.carnet.carnet,
            project=assig_var.assignation.name,
            activity=var_activity.name,
            activity_id=var_activity.id,
            category=var_activity.course_activity_category.category.category,
            period=T(assig_var.semester.period.name),
            yearp=assig_var.semester.yearp,
            after_grade=grade,
            before_grade=grade_before.grade,
            description=T('Edited from Grades page')+" - "+coment
        )

    return "ok"

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator') or auth.has_membership('Teacher'))
def request_change_weighting_load():
    year = db(db.period_year.id == request.vars['year']).select().first()
    year_semester = year.period
    project_id = request.vars['project']
    change_id = request.vars['change_id']
    op = request.vars['op']
    change = None

    if op != "select_change":
        if change_id is None:
            change_activity = db((db.requestchange_activity.semester == year.id) & (db.requestchange_activity.course == project_id) 
                            & (db.requestchange_activity.status == 'Pending')).select().first()
            change = db((db.request_change_weighting.period == year.id) & (db.request_change_weighting.project == project_id) 
                    & ((db.request_change_weighting.status != 'accepted') & (db.request_change_weighting.status != 'rejected'))).select().first()
            if change is None:
                if change_activity is None:
                    change = db.request_change_weighting.insert(
                        user_id=auth.user.id,
                        roll='Student',
                        status='edit',
                        period=year.id,
                        project=project_id
                    )
                else:
                    response.flash = T("Unable to send the request as long as other pending requests")
                    return '<script type="text/javascript">$("#div_request_detail").css("display", "none");</script>'
            else:
                if change_activity != None:
                    response.flash = T("Unable to send the request as long as other pending requests")
                    db(db.request_change_weighting.id == change.id).delete()
                    return '<script type="text/javascript">$("#div_request_detail").css("display", "none");</script>'
        else:
            change = db((db.request_change_weighting.id == change_id)).select().first()

    assignation = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project_id)
                & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()

    if (assignation is None) & (not auth.has_membership('Super-Administrator')) & (not auth.has_membership('Ecys-Administrator')):
        session.flash = T("Action not allowed")
        redirect(URL('default','home'))

    check = db(db.project.id == request.vars['project']).select().first()

    return dict(
        name=check.name,
        semester=year_semester.name,
        year=year.yearp,
        semestre2=year,
        project=request.vars['project'],
        assignation=assignation,
        op=op,
        change=change
    )

@auth.requires_login()
def control_students_modals():
    year = db(db.period_year.id == request.vars['year']).select().first()
    project_var = db(db.project.id == request.vars['project']).select().first()

    return dict(semestre2=year, name=project_var.name)

@auth.requires_login()
def control_assigned_activity():
    try:
        year = db(db.period_year.id == request.vars['year']).select().first()
        year_semester = year.period
        project = db(db.project.id==request.vars['project']).select().first()

        assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project.id) 
                    & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select().first()

        if assigantion is None:
            assigned_to_project = False
        else:
            assigned_to_project = True
            activities = db((db.course_assigned_activity.semester == year.id) & (db.course_assigned_activity.assignation == project.id)).select()
    except:
        assigned_to_project = False

    return dict(
        semestre2=year,
        project=project,
        assigned_to_project=assigned_to_project,
        activities=activities
    )

@auth.requires_login()
def control_students_modals2():
    #Obtener la asignacion del estudiante
    project = request.vars['project']
    year = db(db.period_year.id == request.vars['year']).select().first()
    project_var = db(db.project.id == request.vars['project']).select().first()
    return dict(semestre2=year, name=project_var.name, project_var=project_var)

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def management_approval_students_requirement():
    #vars
    year = None
    project_var = None
    requirement = None

    #Check if the period is correct
    if request.vars['period'] is None or request.vars['period'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        year = request.vars['period']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator') and cpfecys.current_year_period().id != year.id:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))

    #Check if the period is correct
    if request.vars['project'] is None or request.vars['project'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        project_var = request.vars['project']
        project_var = db(db.project.id == project_var).select().first()
        if project_var is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    #Check if the requirement is correct
    if request.vars['requirement'] is None or request.vars['requirement'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        requirement = request.vars['requirement']
        requirement = db(db.course_requirement.id == requirement).select().first()
        if requirement is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            if requirement.project != project_var.id or requirement.semester != year.id:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))

    if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator'):
        assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project_var.id)
                    & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()

        if assigantion is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    #Exception of permition
    exception_query = db(db.course_laboratory_exception.project == project_var.id).select().first()
    exception_s_var = False
    if exception_query is not None:
        exception_s_var = exception_query.s_edit_course
    
    #Check if the course has endend
    no_actions_all = False
    course_ended_var = db((db.course_ended.project == project_var.id) & (db.course_ended.period == year.id) ).select().first()
    if course_ended_var != None and course_ended_var.finish:
        no_actions_all = True
    
    #Grid
    grid = None
    db.course_requirement_student.id.readable = False
    db.course_requirement_student.id.writable = False
    db.course_requirement_student.requirement.readable = False
    db.course_requirement_student.requirement.writable = False
    db.course_requirement_student.requirement.default = requirement.id
    
    if auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'):
        query = (db.course_requirement_student.requirement == requirement.id)
        grid = SQLFORM.grid(query, csv=False, paginate=10, editable=False, searchable=False)
    elif auth.has_membership('Teacher'):
        query = (db.course_requirement_student.requirement == requirement.id)
        if not no_actions_all:
            grid = SQLFORM.grid(query, csv=False, paginate=10, editable=False, searchable=False)
        else:
            grid = SQLFORM.grid(query, csv=False, create=False, editable=False, deletable=False, searchable=False)
    elif auth.has_membership('Student'):
        query = (db.course_requirement_student.requirement == requirement.id)
        if not no_actions_all:
            if exception_s_var or requirement.teacher_permition:
                grid = SQLFORM.grid(query, csv=False, paginate=10, editable=False, details=False, searchable=False)
            else:
                grid = SQLFORM.grid(query, csv=False, create=False, editable=False, deletable=False, searchable=False)
        else:
            grid = SQLFORM.grid(query, csv=False, create=False, editable=False, deletable=False, searchable=False)
    else:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    academic_assig3 = db((db.academic.id == db.academic_course_assignation.carnet) & (db.academic_course_assignation.semester == request.vars['period']) 
                    & (db.academic_course_assignation.assignation == request.vars['project'])).select(orderby=db.academic.carnet)
    students = []
    for aca_t in academic_assig3:
        students.append(aca_t.academic_course_assignation)
    
    return dict(project=project_var, year=year, requirement=requirement, grid=grid, students=students)

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher'))
def management_assigned_activity():
    #Check if the period is correct
    if request.vars['year'] is None or request.vars['year'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        year = request.vars['year']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            if cpfecys.current_year_period().id != year.id:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))

    #Check if the project is correct
    if request.vars['project'] is None or request.vars['project'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        project = request.vars['project']
        project = db(db.project.id == project).select().first()
        if project is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project.id) 
                        & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select().first()
            if assigantion is None:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))

    if auth.has_membership('Teacher'):
        db.course_assigned_activity.assignation.readable = False
        db.course_assigned_activity.assignation.writable = False
        db.course_assigned_activity.assignation.default = project.id
        db.course_assigned_activity.semester.readable = False
        db.course_assigned_activity.semester.writable = False
        db.course_assigned_activity.semester.default = year.id
        db.course_assigned_activity.fileReport.readable = False
        db.course_assigned_activity.fileReport.writable = False
        query = ((db.course_assigned_activity.semester == year.id) & (db.course_assigned_activity.assignation == project.id))
        grid = SQLFORM.grid(query, csv=False, paginate=10, searchable=False, oncreate=oncreate_assigned_activity, onupdate=onupdate_assigned_activity, ondelete=ondelete_assigned_activity)
        return dict(year=year, project=project, grid=grid)
    else:
        if request.vars['activity'] is None or request.vars['activity'] == '':
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            activity = request.vars['activity']
            activity = db((db.course_assigned_activity.semester == year.id) & (db.course_assigned_activity.assignation == project.id)
                        & (db.course_assigned_activity.id == activity)).select().first()
            if activity is None:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))
            else:
                if not activity.report_required:
                    session.flash=T('Action invalid. The activity does not require climbing a report.')
                    redirect(URL('activity_control', 'students_control', vars=dict(project = project.id, period = year.id)))
                
                if activity.date_start >= date.today():
                    session.flash=T('Action invalid. The activity has not yet completed.')
                    redirect(URL('activity_control', 'students_control', vars=dict(project = project.id, period = year.id)))

            upload_form = FORM(
                                INPUT(_name='activity_id',_type='text'),
                                INPUT(_name='file_upload',_type='file',
                                        requires=[
                                            IS_UPLOAD_FILENAME(extension='(pdf|zip)', error_message='Solo se aceptan archivos con extension zip|pdf'),
                                            IS_LENGTH(2097152, error_message='El tamaño máximo del archivo es 2MB')
                                        ]
                                )
                            )

            if upload_form.accepts(request.vars,formname='upload_form'):
                try:
                    if (upload_form.vars.activity_id is "" ) or ( upload_form.vars.file_upload is ""):
                        response.flash = T('You must enter all fields.')
                    else:
                        #FILE UPLOAD
                        file_var = db.course_assigned_activity.fileReport.store(upload_form.vars.file_upload.file, upload_form.vars.file_upload.filename)

                        #STATUS OF ACTIVITY
                        status = T('Teacher Failed')
                        if activity.status != T('Teacher Failed'):
                            status = T('Completed')
                            if not activity.automatic_approval:
                                status = T('Grade pending')

                        #CHECK IF THE ACTIVITY HAS A REPORT OF HAS BEEN REPLACED THE REPORT
                        if activity.fileReport is None:
                            description_log = T('The academic tutor has recorded the activity report.')
                        else:
                            description_log = T('The academic tutor has replaced the activity report.')

                        #LOG OF ACTIVITY
                        db.course_assigned_activity_log.insert(
                            user_name=auth.user.username,
                            roll='Student',
                            operation_log='update',
                            description_log=description_log,
                            id_course_assigned_activity=activity.id,
                            project=project.name,
                            period=T(year.period.name),
                            yearp=year.yearp,
                            before_name=activity.name,
                            before_description=activity.description,
                            before_report_required=activity.report_required,
                            before_status=activity.status,
                            before_automatic_approval=activity.automatic_approval,
                            before_date_start=activity.date_start,
                            before_fileReport=activity.fileReport,
                            after_name=activity.name,
                            after_description=activity.description,
                            after_report_required=activity.report_required,
                            after_status=status,
                            after_automatic_approval=activity.automatic_approval,
                            after_date_start=activity.date_start,
                            after_fileReport=file_var
                        )

                        db(db.course_assigned_activity.id == int(upload_form.vars.activity_id)).update(fileReport=file_var, status=status)
                        response.flash = T('File loaded successfully.')
                        activity = db(db.course_assigned_activity.id == int(upload_form.vars.activity_id)).select().first()
                except:
                    response.flash = T('Error loading file.')

            return dict(year=year, project=project, activity=activity)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def periodo():
    grid = SQLFORM.grid(db.period, maxtextlength=100, csv=False)
    return dict(grid=grid)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def periodo_ciclo():
    grid = SQLFORM.grid(db.period_year, maxtextlength=100, csv=False)
    return dict(grid=grid)

@auth.requires_login()
@auth.requires_membership('Teacher')
def rate_assigned_activity():
    try:
        #Check if the period is correct
        if request.vars['year'] is None or request.vars['year'] == '':
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            year = request.vars['year']
            year = db(db.period_year.id == year).select().first()
            if year is None:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))
            else:
                if cpfecys.current_year_period().id != year.id:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'home'))

        #Check if the project is correct
        if request.vars['project'] is None or request.vars['project'] == '':
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            project = request.vars['project']
            project = db(db.project.id == project).select().first()
            if project is None:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))
            else:
                assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project.id)
                            & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select().first()
                if assigantion is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'home'))

        #Check if the activity is valid or the operation on the activity is valid
        if request.vars['activity'] is None or request.vars['activity'] == '' or request.vars['op'] is None or request.vars['op'] == '' or (request.vars['op'] != '1' and request.vars['op'] != '2'):
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

        activity = db((db.course_assigned_activity.semester == year.id) & (db.course_assigned_activity.assignation == project.id)
                    & (db.course_assigned_activity.id == request.vars['activity'])).select().first()
        if activity is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
    except:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    if activity.status == T('Pending') or activity.status == T('Active'):
        session.flash=T('Action invalid. The activity has not yet completed.')
        redirect(URL('activity_control', 'students_control.html', vars=dict(project=project.id, period=year.id)))

    if request.vars['op'] == '2':
        status = T('Teacher Failed')
    else:
        status = T('Accomplished')
        if activity.report_required and activity.fileReport is None:
            status = f"{T('Pending')} {T('Item Delivery')}"
    
    db(db.course_assigned_activity.id == activity.id).update(status=status)
    session.flash=T('Qualified Activity')
    redirect(URL('activity_control', 'students_control', vars=dict(project=project.id, period=year.id)))

def onupdate_assigned_activity(form):
    fail_check = 0
    message_fail = ''
    #Check if has one of this roles
    if not auth.has_membership('Teacher'):
        fail_check = 2
        message_fail = T('Not valid Action.')

    #Start the process
    #Check if the period is correct
    if request.vars['year'] is None or request.vars['year'] == '':
        fail_check = 2
        message_fail = T('Not valid Action.')
    else:
        year = request.vars['year']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            fail_check = 2
            message_fail = T('Not valid Action.')
        else:
            if cpfecys.current_year_period().id != year.id:
                fail_check = 2
                message_fail = T('Not valid Action.')

    #Check if the project is correct
    if request.vars['project'] is None or request.vars['project'] == '':
        fail_check = 2
        message_fail = T('Not valid Action.')
    else:
        project = request.vars['project']
        project = db(db.project.id == project).select().first()
        if project is None:
            fail_check = 2
            message_fail = T('Not valid Action.')
        else:
            assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project) 
                        & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select().first()
            if assigantion is None:
                fail_check = 2
                message_fail = T('Not valid Action.')

    #LOG OF ACTIVITY
    name_a = None
    description_a = None
    report_required_a = None
    status_a = None
    automatic_approval_a = None
    file_report_a = None
    date_start_a = None
    id_log_a = None
    project_a = None
    period_a = None
    year_p_a = None
    for activity_log in db(db.course_assigned_activity_log.id_course_assigned_activity == form.vars.id).select(orderby=db.course_assigned_activity_log.id):
        name_a = activity_log.after_name
        description_a = activity_log.after_description
        report_required_a = activity_log.after_report_required
        status_a = activity_log.after_status
        automatic_approval_a = activity_log.after_automatic_approval
        file_report_a = activity_log.after_fileReport
        date_start_a = activity_log.after_date_start
        id_log_a = activity_log.id_course_assigned_activity
        project_a = activity_log.project
        period_a = activity_log.period
        year_p_a = activity_log.yearp

    #Check if the activity is of the course and the period
    if project_a != project.name or year_p_a != str(year.yearp) and period_a != T(year.period.name):
        fail_check = 2
        message_fail = T('Not valid Action.')
        project = db(db.project.name == name_a).select().first()
        if period_a == 'Primer Semestre':
            year = db((db.period_year.period == 1) & (db.period_year.yearp == int(year_p_a))).select().first()
        else:
            year = db((db.period_year.period == 2) & (db.period_year.yearp == int(year_p_a))).select().first()
    else:
        #Check the periods
        if period.period.id == 1:
            start = datetime.strptime(str(period.yearp) + '-01-01', "%Y-%m-%d")
            end = datetime.strptime(str(period.yearp) + '-06-01', "%Y-%m-%d")
        else:
            start = datetime.strptime(str(period.yearp) + '-06-01', "%Y-%m-%d")
            end = datetime.strptime(str(period.yearp + 1) + '-01-01', "%Y-%m-%d")

        #Check if the date of activity is intro the valid dates
        activity_assigned = db((db.course_assigned_activity.id == form.vars.id) & (db.course_assigned_activity.semester == period.id)
                            & (db.course_assigned_activity.assignation == project.id) & (db.course_assigned_activity.date_start >= start)
                            & (db.course_assigned_activity.date_start < end)).select().first()
        if activity_assigned is None:
            fail_check = 1 
            message_fail = T('The activity date is out of this semester.')

    #Check if has to show the message or save the log
    if fail_check > 0:
        if form.vars.delete_this_record != None:
            old_activity_assigned = db.course_assigned_activity.insert(
                name=name_a,
                description=description_a,
                report_required=report_required_a,
                status=status_a,
                automatic_approval=automatic_approval_a,
                fileReport=file_report_a,
                date_start=date_start_a,
                semester=period.id,
                assigantion=project.id
            )
            db(db.course_assigned_activity.id == old_activity_assigned).update(id=id_log_a)
        else:
            db(db.course_assigned_activity.id==id_log_a).update(name=name_a,
                description=description_a,
                report_required=report_required_a,
                status=status_a,
                automatic_approval=automatic_approval_a,
                fileReport=file_report_a,
                date_start=date_start_a,
                semester=period.id,
                assigantion=project.id
                )

        session.flash = message_fail
        if fail_check == 2:
            redirect(URL('default','home'))
    else:
        if form.vars.delete_this_record != None:
            #LOG OF ACTIVITY
            db.course_assigned_activity_log.insert(
                user_name=auth.user.username,
                roll='Teacher',
                operation_log='delete',
                description_log=T('Activity has been removed from the site administration activities assigned'),
                project=project.name,
                period=T(year.period.name),
                yearp=year.yearp,
                before_name=name_a,
                before_description=description_a,
                before_report_required=report_required_a,
                before_status=status_a,
                before_automatic_approval=automatic_approval_a,
                before_date_start=date_start_a,
                before_fileReport=file_report_a
            )
        else:
            #Check the periods
            if period.period.id == 1:
                start = datetime.strptime(str(period.yearp) + '-01-01', "%Y-%m-%d")
                end = datetime.strptime(str(period.yearp) + '-06-01', "%Y-%m-%d")
            else:
                start = datetime.strptime(str(period.yearp) + '-06-01', "%Y-%m-%d")
                end = datetime.strptime(str(period.yearp+1) + '-01-01', "%Y-%m-%d")
            
            activity_assigned = db(db.course_assigned_activity.id == form.vars.id).select().first()
            if (activity_assigned.name != name_a or activity_assigned.description != description_a or activity_assigned.report_required != report_requiredA or activity_assigned.automatic_approval != automatic_approval_a or activity_assigned.fileReport != file_report_a or activity_assigned.date_start != date_start_a):

                tiempo = date.today()
                #STATUS OF ACTIVITY
                status = activity_assigned.status
                if activity_assigned.date_start >= tiempo:
                    status = T('Pending')
                    if activity_assigned.date_start == tiempo:
                        status = T('Active')
                    #REPORT OF ACTIVITY
                    db(db.course_assigned_activity.id == form.vars.id).update(fileReport=None)
                else:
                    if not activity_assigned.report_required and report_requiredA:
                        db(db.course_assigned_activity.id == form.vars.id).update(fileReport=None)
                    
                    status = activity_assigned.status
                    if activity_assigned.status != T('Teacher Failed'):
                        if activity_assigned.status == T('Accomplished'):
                            if activity_assigned.report_required and activity_assigned.fileReport is None:
                                status = f"{T('Pending')} {T('Item Delivery')}"
                        else:
                            if activity_assigned.report_required:
                                if activity_assigned.fileReport is None:
                                    status = f"{T('Pending')} {T('Item Delivery')}"
                                else:
                                    status = T('Grade pending') if not activity_assigned.automatic_approval else T('Accomplished')
                            else:
                                status = T('Grade pending') if not activity_assigned.automatic_approval else T('Accomplished')

                #STATUS OF ACTIVITY
                db(db.course_assigned_activity.id == form.vars.id).update(status=status)

                #LOG OF ACTIVITY
                db.course_assigned_activity_log.insert(
                    user_name=auth.user.username,
                    roll='Teacher',
                    operation_log='update',
                    description_log=T('Updated the activity from the site administration activities assigned'),
                    id_course_assigned_activity=form.vars.id,
                    project=project.name,
                    period=T(year.period.name),
                    yearp=year.yearp,
                    before_name=name_a,
                    before_description=description_a,
                    before_report_required=report_required_a,
                    before_status=status_a,
                    before_automatic_approval=automatic_approval_a,
                    before_date_start=date_start_a,
                    before_fileReport=file_report_a,
                    after_name=form.vars.name,
                    after_description=form.vars.description,
                    after_report_required=form.vars.report_required,
                    after_status=status,
                    after_automatic_approval=form.vars.automatic_approval,
                    after_date_start=form.vars.date_start,
                    after_fileReport=file_report_a
                )

def ondelete_assigned_activity(table_involved, id_of_the_deleted_record):
    #Check if has one of this roles
    if not auth.has_membership('Teacher'):
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    #Start the process
    #Check if the period is correct
    if request.vars['year'] is None or request.vars['year'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        year = request.vars['year']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            if cpfecys.current_year_period().id != year.id:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))

    #Check if the project is correct
    if request.vars['project'] is None or request.vars['project'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        project = request.vars['project']
        project = db(db.project.id == project).select().first()
        if project is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project) 
                        & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select().first()
            if assigantion is None:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))

    #Check if the activity is correct
    course_assigned_activity_log_var = db.course_assigned_activity(id_of_the_deleted_record)

    #Check if the activity is of the course and the period
    if (course_assigned_activity_log_var is None) and (course_assigned_activity_log_var is not None and (course_assigned_activity_log_var.assignation != project.id or course_assigned_activity_log_var.semester != year.id)):
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    #LOG OF ACTIVITY
    db.course_assigned_activity_log.insert(
        user_name=auth.user.username,
        roll='Teacher',
        operation_log='delete',
        description_log=T('Activity has been removed from the site administration activities assigned'),
        project=project.name,
        period=T(year.period.name),
        yearp=year.yearp,
        before_name=course_assigned_activity_log_var.name,
        before_description=course_assigned_activity_log_var.description,
        before_report_required=course_assigned_activity_log_var.report_required,
        before_status=course_assigned_activity_log_var.status,
        before_automatic_approval=course_assigned_activity_log_var.automatic_approval,
        before_date_start=course_assigned_activity_log_var.date_start,
        before_fileReport=course_assigned_activity_log_var.fileReport
    )

def oncreate_assigned_activity(form):
    #Check if has one of this roles
    if not auth.has_membership('Teacher'):
        db(db.course_assigned_activity.id == form.vars.id).delete()
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    #Check if the period is correct
    if request.vars['year'] is None or request.vars['year'] == '':
        db(db.course_assigned_activity.id == form.vars.id).delete()
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        year = request.vars['year']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            db(db.course_assigned_activity.id == form.vars.id).delete()
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            if cpfecys.current_year_period().id != year.id:
                db(db.course_assigned_activity.id == form.vars.id).delete()
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))

    #Check if the project is correct
    if request.vars['project'] is None or request.vars['project'] == '':
        db(db.course_assigned_activity.id == form.vars.id).delete()
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        project = request.vars['project']
        project = db(db.project.id == project).select().first()
        if project is None:
            db(db.course_assigned_activity.id == form.vars.id).delete()
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project) & ((db.user_project.period <= year.id) 
                        & ((db.user_project.period + db.user_project.periods) > year.id))).select().first()
            if assigantion is None:
                db(db.course_assigned_activity.id == form.vars.id).delete()
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))

    #Check the periods
    if period.period.id == 1:
        start = datetime.strptime(str(period.yearp) + '-01-01', "%Y-%m-%d")
        end = datetime.strptime(str(period.yearp) + '-06-01', "%Y-%m-%d")
    else:
        start = datetime.strptime(str(period.yearp) + '-06-01', "%Y-%m-%d")
        end = datetime.strptime(str(period.yearp+1) + '-01-01', "%Y-%m-%d")

    #Check if the date of activity is intro the valid dates
    activity_assigned = db((db.course_assigned_activity.id == form.vars.id) & (db.course_assigned_activity.semester == period.id)
                        & (db.course_assigned_activity.assignation == project.id) & (db.course_assigned_activity.date_start >= start)
                        & (db.course_assigned_activity.date_start < end)).select().first()
    if activity_assigned is None:
        db(db.course_assigned_activity.id == form.vars.id).delete()
        session.flash = T('The activity date is out of this semester.')

    #Check status of activity
    tiempo = date.today()
    #STATUS OF ACTIVITY
    if activity_assigned.date_start >= tiempo:
        status = T('Active') if activity_assigned.date_start == tiempo else T('Pending')
        
        #SEND MAIL TO THE STUDENTS
        subject = T('Activity assigned by the professor')
        message = f"<html>{T('Please be advised that the Professor:')} \"{auth.user.username}\" {T('has been assigned an activity that should develop.')}<br>"
        message += f"{T('Activity data:')}<br>"
        message += f"{T('Name')}: {form.vars.name}<br>"
        message += f"{T('Description')}: {form.vars.description}<br>"
        message += f"{T('Date')}: {str(form.vars.date_start)}<br>"
        if form.vars.report_required:
            message += f"{T('Report Required')}: {T('You need to enter a report of the activity to be taken as valid.')}<br>"
        message += f"{project.name}<br>{T(period.period.name)} {str(period.yearp)}<br>Sistema de Seguimiento de La Escuela de Ciencias y Sistemas<br> Facultad de Ingeniería - Universidad de San Carlos de Guatemala</html>"

        #Log General del Envio
        row = db.notification_general_log4.insert(
            subject=subject,
            sent_message=message,
            emisor=auth.user.username,
            course=project.name,
            yearp=period.yearp,
            period=(period.period.name)
        )
        
        listado_correos = None
        email_list_log = None
        for users_t in db((db.user_project.project == project.id) & (db.user_project.assigned_user != auth.user.id) & ((db.user_project.period <= period.id) & ((db.user_project.period + db.user_project.periods) > period.id))).select():
            if listado_correos is None:
                listado_correos = []
                email_list_log = users_t.assigned_user.email
            else:
                email_list_log += f',{users_t.assigned_user.email}'
            listado_correos.append(users_t.assigned_user.email)
        
        if listado_correos is not None:
            was_sent = mail.send(to='dtt.ecys@dtt-ecys.org', subject=subject, message=message, bcc=listado_correos)
            db.mailer_log.insert(
                    sent_message=message,
                    destination=email_list_log,
                    result_log=f"{str(mail.error or '')}:{str(mail.result)}", 
                    success = was_sent, emisor=str(auth.user.username)
                )
            
            #Notification LOG
            email_list = str(email_list_log).split(",")
            for email_temp in email_list:
                user_var = db((db.auth_user.email == email_temp)).select().first()
                if user_var is not None:
                    username_var = user_var.username
                else:
                    user_var = db((db.academic.email == email_temp)).select().first()
                    if user_var is not None:
                        username_var = user_var.carnet
                    else:
                        username_var = 'None'
                db.notification_log4.insert(
                    destination=email_temp,
                    username=username_var,
                    result_log=f"{str(mail.error or '')}:{str(mail.result)}",
                    success=was_sent,
                    register=row.id
                )
    else:
        status = T('Completed')
        if activity_assigned.report_required:
            status = f"{T('Pending')} {T('Item Delivery')}"
        else:
            if not activity_assigned.automatic_approval:
                status = T('Grade pending')
    
    #LOG OF ACTIVITY
    db.course_assigned_activity_log.insert(
        id_course_assigned_activity=form.vars.id,
        user_name=auth.user.username,
        roll='Teacher',
        operation_log='insert',
        description_log=T('An activity is assigned to the academic tutor from the administration page of activities assigned'),
        project=project.name,
        period=T(year.period.name),
        yearp=year.yearp,
        after_name=form.vars.name,
        after_description=form.vars.description,
        after_report_required=form.vars.report_required,
        after_status=status,
        after_automatic_approval=form.vars.automatic_approval,
        after_date_start=form.vars.date_start
    )
    
    #STATUS OF ACTIVITY
    db(db.course_assigned_activity.id == form.vars.id).update(status=status)

def onupdate_course_second_recovery_test(form):
    #Check if the period is correct
    if request.vars['year'] is None or request.vars['year'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        year = request.vars['year']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    #Check if the project is correct
    if request.vars['project'] is None or request.vars['project'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        project = request.vars['project']
        project = db(db.project.id == project).select().first()
        if project is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    roll_var = get_rol()

    usr2 = db(db.course_second_recovery_test_log.id_course_second_recovery_test == form.vars.id).select(orderby=db.course_second_recovery_test_log.id)
    academic_log = ''
    academic_id_log = ''
    before_grade_log = ''
    for u in usr2:
        academic_log = u.academic
        academic_id_log = u.academic_id
        before_grade_log = u.after_grade
    
    if form.vars.delete_this_record != None:
        db.course_second_recovery_test_log.insert(
            user_name=auth.user.username,
            roll=roll_var,
            operation_log='delete',
            academic_id=academic_id_log,
            academic=academic_log,
            project=project.name,
            period=T(year.period.name),
            yearp=year.yearp,
            before_grade=before_grade_log,
            description=T('Delete from second recovery test page')
        )
    else:
        if before_grade_log != form.vars.grade:
            db.course_second_recovery_test_log.insert(
                user_name=auth.user.username,
                roll=roll_var,
                operation_log='update',
                academic_id=academic_id_log,
                academic=academic_log,
                project=project.name,
                period=T(year.period.name),
                yearp=year.yearp,
                before_grade=before_grade_log,
                after_grade=form.vars.grade,
                id_course_second_recovery_test=form.vars.id,
                description=T('Update from second recovery test page')
            )

def ondelete_course_second_recovery_test(table_involved, id_of_the_deleted_record):
    #Check if the period is correct
    if request.vars['year'] is None or request.vars['year'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        year = request.vars['year']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    #Check if the project is correct
    if request.vars['project'] is None or request.vars['project'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        project = request.vars['project']
        project = db(db.project.id == project).select().first()
        if project is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    roll_var = get_rol()
    course_second_recovery_test_var = db.course_second_recovery_test(id_of_the_deleted_record)
    if course_second_recovery_test_var is not None:
        academic_s = db(db.academic.id == course_second_recovery_test_var.carnet).select().first()
        db.course_second_recovery_test_log.insert(
            user_name=auth.user.username,
            roll=roll_var,
            operation_log='delete',
            academic_id=academic_s.id,
            academic=academic_s.carnet,
            project=project.name,
            period=T(year.period.name),
            yearp=year.yearp,
            before_grade=course_second_recovery_test_var.grade,
            description=T('Delete from second recovery test page')
        )

def oncreate_course_second_recovery_test(form):
    #Check if the period is correct
    if request.vars['year'] is None or request.vars['year'] == '':
        db(db.course_second_recovery_test.id == form.vars.id).delete()
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        year = request.vars['year']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            db(db.course_second_recovery_test.id == form.vars.id).delete()
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    #Check if the project is correct
    if request.vars['project'] is None or request.vars['project'] == '':
        db(db.course_second_recovery_test.id == form.vars.id).delete()
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        project = request.vars['project']
        project = db(db.project.id == project).select().first()
        if project is None:
            db(db.course_second_recovery_test.id == form.vars.id).delete()
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    roll_var = get_rol()
    usr2 = db((db.course_second_recovery_test.id != form.vars.id) & (db.course_second_recovery_test.semester == request.vars['year']) 
            & (db.course_second_recovery_test.project == request.vars['project']) & (db.course_second_recovery_test.carnet == form.vars.carnet)).select().first()
    if usr2 is not None:
        db(db.course_second_recovery_test.id == form.vars.id).delete()
        session.flash = T('Error. Exist a register of recovery test of the student in the course.')
    else:
        academic_s = db(db.academic.id == form.vars.carnet).select().first()
        var_assignation = db((db.academic_course_assignation.carnet == academic_s.id) & (db.academic_course_assignation.semester == year.id)
                        & (db.academic_course_assignation.assignation == project.id)).select().first()
        if var_assignation is None:
            db(db.course_first_recovery_test.id == form.vars.id).delete()
            session.flash = T('Error. The academic is not assigned to the course')
        else:
            db.course_second_recovery_test_log.insert(
                user_name=auth.user.username,
                roll=roll_var,
                operation_log='insert',
                academic_id=academic_s.id,
                academic=academic_s.carnet,
                project=project.name,
                period=T(year.period.name),
                yearp=year.yearp,
                after_grade=form.vars.grade,
                id_course_second_recovery_test=form.vars.id,
                description=T('Inserted from second recovery test page')
            )

def oncreate_course_first_recovery_test(form):
    #Check if the period is correct
    if request.vars['year'] is None or request.vars['year'] == '':
        db(db.course_first_recovery_test.id == form.vars.id).delete()
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        year = request.vars['year']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            db(db.course_first_recovery_test.id == form.vars.id).delete()
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    #Check if the project is correct
    if request.vars['project'] is None or request.vars['project'] == '':
        db(db.course_first_recovery_test.id == form.vars.id).delete()
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        project = request.vars['project']
        project = db(db.project.id == project).select().first()
        if project is None:
            db(db.course_first_recovery_test.id == form.vars.id).delete()
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))


    #Check if the course has endend
    roll_var = get_rol()
    usr2 = db((db.course_first_recovery_test.id != form.vars.id) & (db.course_first_recovery_test.semester == request.vars['year']) 
            & (db.course_first_recovery_test.project == request.vars['project']) & (db.course_first_recovery_test.carnet == form.vars.carnet)).select().first()
    if usr2 is not None:
        db(db.course_first_recovery_test.id == form.vars.id).delete()
        session.flash = T('Error. Exist a register of recovery test of the student in the course.')
    else:
        academic_s = db(db.academic.id == form.vars.carnet).select().first()
        var_assignation = db((db.academic_course_assignation.carnet == academic_s.id) & (db.academic_course_assignation.semester == year.id)
                        & (db.academic_course_assignation.assignation == project.id)).select().first()
        if var_assignation is None:
            db(db.course_first_recovery_test.id == form.vars.id).delete()
            session.flash = T('Error. The academic is not assigned to the course')
        else:
            db.course_first_recovery_test_log.insert(
                user_name=auth.user.username,
                roll=roll_var,
                operation_log='insert',
                academic_id=academic_s.id,
                academic=academic_s.carnet,
                project=project.name,
                period=T(year.period.name),
                yearp=year.yearp,
                after_grade=form.vars.grade,
                id_course_first_recovery_test=form.vars.id,
                description=T('Inserted from first recovery test page')
            )

def ondelete_course_first_recovery_test(table_involved, id_of_the_deleted_record):
    #Check if the period is correct
    if request.vars['year'] is None or request.vars['year'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        year = request.vars['year']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    #Check if the project is correct
    if request.vars['project'] is None or request.vars['project'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        project = request.vars['project']
        project = db(db.project.id == project).select().first()
        if project is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    roll_var = get_rol()
    course_first_recovery_test_var = db.course_first_recovery_test(id_of_the_deleted_record)
    if course_first_recovery_test_var is not None:
        academic_s = db(db.academic.id == course_first_recovery_test_var.carnet).select().first()
        db.course_first_recovery_test_log.insert(
            user_name=auth.user.username,
            roll=roll_var,
            operation_log='delete',
            academic_id=academic_s.id,
            academic=academic_s.carnet,
            project=project.name,
            period=T(year.period.name),
            yearp=year.yearp,
            before_grade=course_first_recovery_test_var.grade,
            description=T('Delete from first recovery test page')
        )

def onupdate_course_first_recovery_test(form):
    #Check if the period is correct
    if request.vars['year'] is None or request.vars['year'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        year = request.vars['year']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    #Check if the project is correct
    if request.vars['project'] is None or request.vars['project'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        project = request.vars['project']
        project = db(db.project.id == project).select().first()
        if project is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))


    #Check if the course has endend
    roll_var = get_rol()
    usr2 = db(db.course_first_recovery_test_log.id_course_first_recovery_test == form.vars.id).select(orderby=db.course_first_recovery_test_log.id)
    academic_log = ''
    academic_id_log = ''
    before_grade_log = ''
    for u in usr2:
        academic_log = u.academic
        academic_id_log = u.academic_id
        before_grade_log = u.after_grade

    if form.vars.delete_this_record != None:
        db.course_first_recovery_test_log.insert(
            user_name=auth.user.username,
            roll=roll_var,
            operation_log='delete',
            academic_id=academic_id_log,
            academic=academic_log,
            project=project.name,
            period=T(year.period.name),
            yearp=year.yearp,
            before_grade=before_grade_log,
            description=T('Delete from first recovery test page')
        )
    else:
        if before_grade_log != form.vars.grade:
            db.course_first_recovery_test_log.insert(
                user_name=auth.user.username,
                roll=roll_var,
                operation_log='update',
                academic_id=academic_id_log,
                academic=academic_log,
                project=project.name,
                period=T(year.period.name),
                yearp=year.yearp,
                before_grade=before_grade_log,
                after_grade=form.vars.grade,
                id_course_first_recovery_test=form.vars.id,
                description=T('Update from first recovery test page')
            )

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def oncreate_validate_laboratory(form):
    #Check if has one of this roles
    if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator') and not auth.has_membership('Teacher') and not auth.has_membership('Student'):
        db(db.validate_laboratory.id == form.vars.id).delete()
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    #Start the process
    #Check if the period is correct
    if request.vars['year'] is None or request.vars['year'] == '':
        db(db.validate_laboratory.id == form.vars.id).delete()
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        year = request.vars['year']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            db(db.validate_laboratory.id == form.vars.id).delete()
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator') and cpfecys.current_year_period().id != year.id:
                db(db.validate_laboratory.id == form.vars.id).delete()
                session.flash = T('Not valid Action.')
                redirect(URL('default','home'))

    #Check if the project is correct
    if request.vars['project'] is None or request.vars['project'] == '':
        db(db.validate_laboratory.id == form.vars.id).delete()
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        project = request.vars['project']
        project = db(db.project.id == project).select().first()
        if project is None:
            db(db.validate_laboratory.id == form.vars.id).delete()
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator'):
                assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project)
                            & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
                if assigantion is None:
                    db(db.validate_laboratory.id == form.vars.id).delete()
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'home'))

    no_actions_all = False
    if cpfecys.current_year_period().id != year.id:
        no_actions_all = True
    else:
        #Check if the course has endend
        course_ended_var = db((db.course_ended.project == project.id) & (db.course_ended.period == year.id)).select().first()
        if course_ended_var != None and course_ended_var.finish:
            no_actions_all = True

        #Check the time of the semester is not over
        if not no_actions_all:
            #Time limit of semester parameter
            date1 = None
            tiempo = str(datetime.now())
            date_inicial_p = db.executesql(f'SELECT DATE(\'{tiempo}\');', as_dict=True)
            for d0 in date_inicial_p:
                date1 = d0[f'DATE(\'{tiempo}\')']
            
            date_var = db((db.student_control_period.period_name == (f"{T(year.period.name)} {str(year.yearp)}"))).select().first()
            if date1 >= date_var.date_start_semester and date1 <= date_var.date_finish_semester:
                if year.period == 1:
                    (start, end) = start_end_time(year, '-01-01', '-06-01')                    
                    if not (date1 >= start and date1 < end):
                        no_actions_all = True
                else:
                    (start, end) = start_end_time(year, '-06-01', '-12-31')   
                    if not (date1 >= start and date1 <= end):
                        no_actions_all = True
            else:
                no_actions_all=True

        #If is teacher, check if he has permitions
        if not no_actions_all and auth.has_membership('Teacher'):
            exception_query = db(db.course_laboratory_exception.project == project.id).select().first()
            if exception_query is not None and not exception_query.t_edit_lab:
                    no_actions_all = True
            else:
                no_actions_all = True

    if not no_actions_all:
        roll_var = get_rol()
        if roll_var == '':
            db(db.validate_laboratory.id == form.vars.id).delete()
            session.flash = T('Not valid Action.')
            redirect(URL('default','home'))

        usr2 = db((db.validate_laboratory.id != form.vars.id) & (db.validate_laboratory.semester == request.vars['year']) 
                & (db.validate_laboratory.project == request.vars['project']) & (db.validate_laboratory.carnet == form.vars.carnet)).select().first()
        if usr2 is not None:
            db(db.validate_laboratory.id == form.vars.id).delete()
            session.flash = T('Error. There is a registration renewal or equivalence laboratory student in the course.')
        else:
            academic_s = db(db.academic.id == form.vars.carnet).select().first()
            db.validate_laboratory_log.insert(
                user_name=auth.user.username,
                roll=roll_var,
                operation_log='insert',
                academic_id=academic_s.id,
                academic=academic_s.carnet,
                project=project.name,
                period=T(year.period.name),
                yearp=year.yearp,
                after_grade=form.vars.grade,
                id_validate_laboratory=form.vars.id,
                description=T('Inserted from validation page'),
                validation_type=True
            )
    else:
        if auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'):
            if request.vars['description_request'] is None or request.vars['description_request'] == '':
                db(db.validate_laboratory.id == form.vars.id).delete()
                session.flash = T('You must enter a description of the modification.')
            else:
                roll_var = 'Super-Administrator' if auth.has_membership('Super-Administrator') else 'Ecys-Administrator'

                usr2 = db((db.validate_laboratory.id != form.vars.id) & (db.validate_laboratory.semester == request.vars['year']) 
                        & (db.validate_laboratory.project == request.vars['project']) & (db.validate_laboratory.carnet == form.vars.carnet)).select().first()
                if usr2 is not None:
                    db(db.validate_laboratory.id == form.vars.id).delete()
                    session.flash = T('Error. There is a registration renewal or equivalence laboratory student in the course.')
                else:
                    academic_s = db(db.academic.id == form.vars.carnet).select().first()
                    db.validate_laboratory_log.insert(
                        user_name=auth.user.username,
                        roll=roll_var,
                        operation_log='insert',
                        academic_id=academic_s.id,
                        academic=academic_s.carnet,
                        project=project.name,
                        period=T(year.period.name),
                        yearp=year.yearp,
                        after_grade=form.vars.grade,
                        id_validate_laboratory=form.vars.id,
                        description=str(request.vars['description_request']),
                        validation_type=True
                    )
        else:
            db(db.validate_laboratory.id == form.vars.id).delete()
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

def ondelete_validate_laboratory(table_involved, id_of_the_deleted_record):
    #Check if has one of this roles
    if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator') and not auth.has_membership('Teacher') and not auth.has_membership('Student'):
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    #Start the process
    #Check if the period is correct
    if request.vars['year'] is None or request.vars['year'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        year = request.vars['year']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            if cpfecys.current_year_period().id != year.id:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))

    #Check if the project is correct
    if request.vars['project'] is None or request.vars['project'] == '':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        project = request.vars['project']
        project = db(db.project.id == project).select().first()
        if project is None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator'):
                assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project)
                            & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
                if assigantion is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'home'))

    no_actions_all = False
    #Check if the course has endend
    course_ended_var = db((db.course_ended.project == project.id) & (db.course_ended.period == year.id)).select().first()
    if course_ended_var != None and course_ended_var.finish:
        no_actions_all = True

    #Check the time of the semester is not over
    if not no_actions_all:
        #Time limit of semester parameter
        date1 = None
        tiempo = str(datetime.now())
        date_inicial_p = db.executesql(f'SELECT DATE(\'{tiempo}\');', as_dict=True)
        for d0 in date_inicial_p:
            date1 = d0[f'DATE(\'{tiempo}\')']

        date_var = db((db.student_control_period.period_name == (f"{T(year.period.name)} {str(year.yearp)}"))).select().first()
        if date1 >= date_var.date_start_semester and date1 <= date_var.date_finish_semester:
            if year.period == 1:
                (start, end) = start_end_time(year, '-01-01', '-06-01')
                if not (date1 >= start and date1 < end):
                    no_actions_all = True
            else:
                (start, end) = start_end_time(year, '-06-01', '-12-31')
                if not (date1 >= start and date1 <= end):
                    no_actions_all = True
        else:
            no_actions_all = True

    #If is teacher, check if he has permitions
    if not no_actions_all and auth.has_membership('Teacher'):
        exception_query = db(db.course_laboratory_exception.project == project.id).select().first()
        if exception_query is not None and not exception_query.t_edit_lab:
            no_actions_all = True
        else:
            no_actions_all = True


    if no_actions_all:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        roll_var = get_rol()
        if roll_var == '':
            session.flash = T('Not valid Action.')
            redirect(URL('default','home'))

        validate_laboratory_var = db.validate_laboratory(id_of_the_deleted_record)
        if validate_laboratory_var is not None:
            academic_s = db(db.academic.id == validate_laboratory_var.carnet).select().first()
            db.validate_laboratory_log.insert(
                user_name=auth.user.username,
                roll=roll_var,
                operation_log='delete',
                academic_id=academic_s.id,
                academic=academic_s.carnet,
                project=project.name,
                period=T(year.period.name),
                yearp=year.yearp,
                before_grade=validate_laboratory_var.grade,
                description=T('Delete from validation page'),
                validation_type=True
            )

def onupdate_validate_laboratory(form):
    fail_check = 0
    message_fail = ''
    #Check if has one of this roles
    if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator') and not auth.has_membership('Teacher') and not auth.has_membership('Student'):
        fail_check = 2
        message_fail = T('Not valid Action.')

    #Check if the period is correct
    if request.vars['year'] is None or request.vars['year'] == '':
        fail_check = 2
        message_fail = T('Not valid Action.')
    else:
        year = request.vars['year']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            fail_check = 2
            message_fail = T('Not valid Action.')
        else:
            if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator'):
                if cpfecys.current_year_period().id != year.id:
                    fail_check = 2
                    message_fail = T('Not valid Action.')

    #Check if the project is correct
    if request.vars['project'] is None or request.vars['project'] == '':
        fail_check = 2
        message_fail = T('Not valid Action.')
    else:
        project = request.vars['project']
        project = db(db.project.id == project).select().first()
        if project is None:
            fail_check = 2
            message_fail = T('Not valid Action.')
        else:
            if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator'):
                assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project)
                            & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
                if assigantion is None:
                    fail_check = 2
                    message_fail = T('Not valid Action.')

    no_actions_all = False
    if fail_check == 0:
        if cpfecys.current_year_period().id != year.id:
            no_actions_all = True
        else:
            #Check if the course has endend
            course_ended_var = db((db.course_ended.project == project.id) & (db.course_ended.period == year.id)).select().first()
            if course_ended_var != None and course_ended_var.finish:
                    no_actions_all = True

            #Check the time of the semester is not over
            if not no_actions_all:
                #Time limit of semester parameter
                date1 = None
                tiempo = str(datetime.now())
                date_inicial_p = db.executesql(f'SELECT DATE(\'{tiempo}\');', as_dict=True)
                for d0 in date_inicial_p:
                    date1 = d0[f'DATE(\'{tiempo}\')']
                
                date_var = db((db.student_control_period.period_name == (f'{T(year.period.name)} {str(year.yearp)}'))).select().first()
                if date1 >= date_var.date_start_semester and date1 <= date_var.date_finish_semester:
                    if year.period == 1:
                        (start, end) = start_end_time(year, '-01-01', '-06-01')
                        if not (date1 >= start and date1 < end):
                            no_actions_all = True
                    else:
                        (start, end) = start_end_time(year, '-06-01', '-12-31')
                        if not (date1 >= start and date1 <= end):
                            no_actions_all = True
                else:
                    no_actions_all = True

            #If is teacher, check if he has permitions
            if not no_actions_all and auth.has_membership('Teacher'):
                exception_query = db(db.course_laboratory_exception.project == project.id).select().first()
                if exception_query is not None and exception_query.t_edit_lab:
                    no_actions_all = True
                else:
                    no_actions_all = True

    if not no_actions_all and fail_check == 0:
        roll_var = get_rol()

        usr2 = db((db.validate_laboratory_log.id_validate_laboratory == form.vars.id) & (db.validate_laboratory_log.validation_type == True)).select(orderby=db.validate_laboratory_log.id)
        academic_log = ''
        academic_id_log = ''
        before_grade_log = ''
        for u in usr2:
            academic_log = u.academic
            academic_id_log = u.academic_id
            before_grade_log = u.after_grade

        if form.vars.delete_this_record != None:
            db.validate_laboratory_log.insert(
                user_name=auth.user.username,
                roll=roll_var,
                operation_log='delete',
                academic_id=academic_id_log,
                academic=academic_log,
                project=project.name,
                period=T(year.period.name),
                yearp=year.yearp,
                before_grade=before_grade_log,
                description=T('Delete from validation page'),
                validation_type=True
            )
        else:
            if before_grade_log != form.vars.grade:
                db.validate_laboratory_log.insert(
                    user_name=auth.user.username,
                    roll=roll_var,
                    operation_log='update',
                    academic_id=academic_id_log,
                    academic=academic_log,
                    project=project.name,
                    period=T(year.period.name),
                    yearp=year.yearp,
                    before_grade=before_grade_log,
                    after_grade=form.vars.grade,
                    id_validate_laboratory=form.vars.id,
                    description=T('Update from validation page'),
                    validation_type=True
                )
    else:
        if no_actions_all:
            if auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'):
                if request.vars['description_request'] is None or request.vars['description_request'] == '':
                    message_fail = T('You must enter a description of the modification.')
                    fail_check = 1
                else:
                    roll_var = 'Super-Administrator' if auth.has_membership('Super-Administrator') else 'Ecys-Administrator'

                    usr2 = db((db.validate_laboratory_log.id_validate_laboratory == form.vars.id) & (db.validate_laboratory_log.validation_type == True)).select(orderby=db.validate_laboratory_log.id)
                    academic_log = ''
                    academic_id_log = ''
                    before_grade_log = ''
                    for u in usr2:
                        academic_log = u.academic
                        academic_id_log = u.academic_id
                        before_grade_log = u.after_grade

                    if form.vars.delete_this_record != None:
                        db.validate_laboratory_log.insert(
                            user_name=auth.user.username,
                            roll=roll_var,
                            operation_log='delete',
                            academic_id=academic_id_log,
                            academic=academic_log,
                            project=project.name,
                            period=T(year.period.name),
                            yearp=year.yearp,
                            before_grade=before_grade_log,
                            description=str(request.vars['description_request']),
                            validation_type=True
                        )
                    else:
                        if before_grade_log != form.vars.grade:
                            db.validate_laboratory_log.insert(
                                user_name=auth.user.username,
                                roll=roll_var,
                                operation_log='update',
                                academic_id=academic_id_log,
                                academic=academic_log,
                                project=project.name,
                                period=T(year.period.name),
                                yearp=year.yearp,
                                before_grade=before_grade_log,
                                after_grade=form.vars.grade,
                                id_validate_laboratory=form.vars.id,
                                description=str(request.vars['description_request']),
                                validation_type=True
                            )
            else:
                fail_check = 2
                message_fail = T('Not valid Action.')

    #Check if has to show the message
    if fail_check > 0:
        usr2 = db((db.validate_laboratory_log.id_validate_laboratory == form.vars.id) & (db.validate_laboratory_log.validation_type == True)).select(orderby=db.validate_laboratory_log.id)
        academic_log = ''
        academic_id_log = ''
        before_grade_log = ''
        id_log = 0
        id_validate_laboratory = 0
        for u in usr2:
            academic_log = u.academic
            academic_id_log = u.academic_id
            before_grade_log = u.after_grade
            id_log = int(u.id)
            id_validate_laboratory = int(u.id_validate_laboratory)

        if form.vars.delete_this_record != None:
            insertDelete = db.validate_laboratory.insert(carnet=int(academic_id_log), semester=year.id, project=project.id, grade=int(before_grade_log))
            db(db.validate_laboratory_log.id == id_log).update(id_validate_laboratory=insertDelete.id)
        else:
            if before_grade_log != form.vars.grade:
                db(db.validate_laboratory.id == id_validate_laboratory).update(grade=int(before_grade_log))

        session.flash = message_fail
        if fail_check == 2:
            redirect(URL('default','home'))

def oncreate_laboratory_replacing(form):
    #Check if has one of this roles
    if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator') and not auth.has_membership('Teacher') and not auth.has_membership('Student'):
        db(db.validate_laboratory.id == form.vars.id).delete()
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    #Start the process
    #Check if the period is correct
    if request.vars['year'] is None or request.vars['year'] == '':
        db(db.validate_laboratory.id == form.vars.id).delete()
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        year = request.vars['year']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            db(db.validate_laboratory.id == form.vars.id).delete()
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator'):
                if cpfecys.current_year_period().id != year.id:
                    db(db.validate_laboratory.id == form.vars.id).delete()
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'home'))

    #Check if the project is correct
    if request.vars['project'] is None or request.vars['project'] == '':
        db(db.validate_laboratory.id == form.vars.id).delete()
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        project = request.vars['project']
        project = db(db.project.id == project).select().first()
        if project is None:
            db(db.validate_laboratory.id == form.vars.id).delete()
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator'):
                assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project)
                            & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
                if assigantion is None:
                    db(db.validate_laboratory.id == form.vars.id).delete()
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'home'))

    no_actions_all = False
    if cpfecys.current_year_period().id != year.id:
        no_actions_all = True
    else:
        #Check if the course has endend
        course_ended_var = db((db.course_ended.project == project.id) & (db.course_ended.period == year.id) ).select().first()
        if course_ended_var != None and course_ended_var.finish:
            no_actions_all = True

        #Check the time of the semester is not over
        if not no_actions_all:
            #Time limit of semester parameter
            date1 = None
            tiempo = str(datetime.now())
            date_inicial_p = db.executesql(f'SELECT DATE(\'{tiempo}\');', as_dict=True)
            for d0 in date_inicial_p:
                date1 = d0[f'DATE(\'{tiempo}\')']

            date_var = db((db.student_control_period.period_name == (f'{T(year.period.name)} {str(year.yearp)}'))).select().first()
            if date1 >= date_var.date_start_semester and date1 <= date_var.date_finish_semester:
                if year.period == 1:
                    (start, end) = start_end_time(year, '-01-01', '-06-01')
                    if not (date1 >= start and date1 < end):
                        no_actions_all = True
                else:
                    (start, end) = start_end_time(year, '-06-01', '-12-31')
                    if not (date1 >= start and date1 <= end):
                        no_actions_all = True
            else:
                no_actions_all = True

        #If is teacher, check if he has permitions
        if not no_actions_all and auth.has_membership('Teacher'):
            exception_query = db(db.course_laboratory_exception.project == project.id).select().first()
            if exception_query is not None and exception_query.t_edit_lab:
                    no_actions_all = True
            else:
                no_actions_all = True

    if not no_actions_all:
        if request.vars['description_request'] is None or request.vars['description_request'] == '':
            db(db.validate_laboratory.id == form.vars.id).delete()
            session.flash = T('You must enter a description of the modification.')
        else:
            roll_var = get_rol()
            if roll_var == '':
                db(db.validate_laboratory.id == form.vars.id).delete()
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))

            usr2 = db((db.validate_laboratory.id != form.vars.id) & (db.validate_laboratory.semester == request.vars['year']) 
                    & (db.validate_laboratory.project == request.vars['project']) & (db.validate_laboratory.carnet == form.vars.carnet)).select().first()
            if usr2 is not None:
                db(db.validate_laboratory.id == form.vars.id).delete()
                session.flash = T('Error. There is a registration renewal or equivalence laboratory student in the course.')
            else:
                academic_s = db(db.academic.id == form.vars.carnet).select().first()
                db.validate_laboratory_log.insert(
                    user_name=auth.user.username,
                    roll=roll_var,
                    operation_log='insert',
                    academic_id=academic_s.id,
                    academic=academic_s.carnet,
                    project=project.name,
                    period=T(year.period.name),
                    yearp=year.yearp,
                    after_grade=form.vars.grade,
                    id_validate_laboratory=form.vars.id,
                    description=str(request.vars['description_request']),
                    validation_type=False
                )
    else:
        if auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'):
            if request.vars['description_request'] is None or request.vars['description_request'] == '':
                db(db.validate_laboratory.id == form.vars.id).delete()
                session.flash = T('You must enter a description of the modification.')
            else:
                roll_var = 'Super-Administrator' if auth.has_membership('Super-Administrator') else 'Ecys-Administrator'
                usr2 = db((db.validate_laboratory.id != form.vars.id) & (db.validate_laboratory.semester == request.vars['year']) 
                        & (db.validate_laboratory.project == request.vars['project']) & (db.validate_laboratory.carnet == form.vars.carnet)).select().first()
                if usr2 is not None:
                    db(db.validate_laboratory.id == form.vars.id).delete()
                    session.flash = T('Error. There is a registration renewal or equivalence laboratory student in the course.')
                else:
                    academic_s = db(db.academic.id == form.vars.carnet).select().first()
                    db.validate_laboratory_log.insert(
                        user_name=auth.user.username,
                        roll=roll_var,
                        operation_log='insert',
                        academic_id=academic_s.id,
                        academic=academic_s.carnet,
                        project=project.name,
                        period=T(year.period.name),
                        yearp=year.yearp,
                        after_grade=form.vars.grade,
                        id_validate_laboratory=form.vars.id,
                        description=str(request.vars['description_request']),
                        validation_type=False
                    )
        else:
            db(db.validate_laboratory.id == form.vars.id).delete()
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

def onupdate_laboratory_replacing(form):
    fail_check = 0
    message_fail = ''
    #Check if has one of this roles
    if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator') and not auth.has_membership('Teacher') and not auth.has_membership('Student'):
        fail_check = 2
        message_fail = T('Not valid Action.')

    #Check if the period is correct
    if request.vars['year'] is None or request.vars['year'] == '':
        fail_check = 2
        message_fail = T('Not valid Action.')
    else:
        year = request.vars['year']
        year = db(db.period_year.id == year).select().first()
        if year is None:
            fail_check = 2
            message_fail = T('Not valid Action.')
        else:
            if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator'):
                if cpfecys.current_year_period().id != year.id:
                    fail_check = 2
                    message_fail = T('Not valid Action.')

    #Check if the project is correct
    if request.vars['project'] is None or request.vars['project'] == '':
        fail_check = 2
        message_fail = T('Not valid Action.')
    else:
        project = request.vars['project']
        project = db(db.project.id == project).select().first()
        if project is None:
            fail_check = 2
            message_fail = T('Not valid Action.')
        else:
            if not auth.has_membership('Super-Administrator') and not auth.has_membership('Ecys-Administrator'):
                assigantion = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project)
                            & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
                if assigantion is None:
                    fail_check = 2
                    message_fail = T('Not valid Action.')

    no_actions_all = False
    if fail_check == 0:
        if cpfecys.current_year_period().id != year.id:
            no_actions_all = True
        else:
            #Check if the course has endend
            course_ended_var = db((db.course_ended.project == project.id) & (db.course_ended.period == year.id)).select().first()
            if course_ended_var != None and course_ended_var.finish:
                no_actions_all = True

            #Check the time of the semester is not over
            if not no_actions_all:
                #Time limit of semester parameter
                date1 = None
                tiempo = str(datetime.now())
                date_inicial_p = db.executesql(f'SELECT DATE(\'{tiempo}\');', as_dict=True)
                for d0 in date_inicial_p:
                    date1 = d0[f'DATE(\'{tiempo}\')']

                date_var = db((db.student_control_period.period_name == (f'{T(year.period.name)} {str(year.yearp)}'))).select().first()
                if date1 >= date_var.date_start_semester and date1 <= date_var.date_finish_semester:
                    if year.period == 1:
                        (start, end) = start_end_time(year, '-01-01', '-06-01')
                        if not (date1 >= start and date1 < end):
                            no_actions_all = True
                    else:
                        (start, end) = start_end_time(year, '-06-01', '-12-31')
                        if not (date1 >= start and date1 <= end):
                            no_actions_all = True
                else:
                    no_actions_all = True

            #If is teacher, check if he has permitions
            if not no_actions_all and auth.has_membership('Teacher'):
                exception_query = db(db.course_laboratory_exception.project == project.id).select().first()
                if exception_query is not None and not exception_query.t_edit_lab:
                    no_actions_all = True
                else:
                    no_actions_all = True

    if not no_actions_all and fail_check == 0:
        if request.vars['description_request'] is None or request.vars['description_request'] == '':
            message_fail = T('You must enter a description of the modification.')
            fail_check = 1
        else:
            roll_var = get_rol()
            usr2 = db((db.validate_laboratory_log.id_validate_laboratory == form.vars.id) & (db.validate_laboratory_log.validation_type == False)).select(orderby=db.validate_laboratory_log.id)
            academic_log = ''
            academic_id_log = ''
            before_grade_log = ''
            for u in usr2:
                academic_log = u.academic
                academic_id_log = u.academic_id
                before_grade_log = u.after_grade

            if form.vars.delete_this_record != None:
                db.validate_laboratory_log.insert(
                    user_name=auth.user.username,
                    roll=roll_var,
                    operation_log='delete',
                    academic_id=academic_id_log,
                    academic=academic_log,
                    project=project.name,
                    period=T(year.period.name),
                    yearp=year.yearp,
                    before_grade=before_grade_log,
                    description=str(request.vars['description_request']),
                    validation_type=False
                )
            else:
                if before_grade_log != form.vars.grade:
                    db.validate_laboratory_log.insert(
                        user_name=auth.user.username,
                        roll=roll_var,
                        operation_log='update',
                        academic_id=academic_id_log,
                        academic=academic_log,
                        project=project.name,
                        period=T(year.period.name),
                        yearp=year.yearp,
                        before_grade=before_grade_log,
                        after_grade=form.vars.grade,
                        id_validate_laboratory=form.vars.id,
                        description=str(request.vars['description_request']),
                        validation_type=False
                    )
    else:
        if no_actions_all:
            if auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'):
                if request.vars['description_request'] is None or request.vars['description_request'] == '':
                    message_fail = T('You must enter a description of the modification.')
                    fail_check = 1
                else:
                    roll_var = 'Super-Administrator' if auth.has_membership('Super-Administrator') else 'Ecys-Administrator'
                    usr2 = db((db.validate_laboratory_log.id_validate_laboratory == form.vars.id)&(db.validate_laboratory_log.validation_type == False)).select(orderby=db.validate_laboratory_log.id)
                    academic_log = ''
                    academic_id_log = ''
                    before_grade_log = ''
                    for u in usr2:
                        academic_log = u.academic
                        academic_id_log = u.academic_id
                        before_grade_log = u.after_grade

                    if form.vars.delete_this_record != None:
                        db.validate_laboratory_log.insert(
                            user_name=auth.user.username,
                            roll=roll_var,
                            operation_log='delete',
                            academic_id=academic_id_log,
                            academic=academic_log,
                            project=project.name,
                            period=T(year.period.name),
                            yearp=year.yearp,
                            before_grade=before_grade_log,
                            description=str(request.vars['description_request']),
                            validation_type=False
                        )
                    else:
                        if before_grade_log != form.vars.grade:
                            db.validate_laboratory_log.insert(
                                user_name=auth.user.username,
                                roll=roll_var,
                                operation_log='update',
                                academic_id=academic_id_log,
                                academic=academic_log,
                                project=project.name,
                                period=T(year.period.name),
                                yearp=year.yearp,
                                before_grade=before_grade_log,
                                after_grade=form.vars.grade,
                                id_validate_laboratory=form.vars.id,
                                description=str(request.vars['description_request']),
                                validation_type=False
                            )
            else:
                fail_check = 2
                message_fail = T('Not valid Action.')

    #Check if has to show the message
    if fail_check > 0:
        usr2 = db((db.validate_laboratory_log.id_validate_laboratory == form.vars.id) & (db.validate_laboratory_log.validation_type == False)).select(orderby=db.validate_laboratory_log.id)
        academic_log = ''
        academic_id_log = ''
        before_grade_log = ''
        id_log = 0
        id_validate_laboratory = 0
        for u in usr2:
            academic_log = u.academic
            academic_id_log = u.academic_id
            before_grade_log = u.after_grade
            id_log = int(u.id)
            id_validate_laboratory = int(u.id_validate_laboratory)

        if form.vars.delete_this_record != None:
            insert_delete = db.validate_laboratory.insert(carnet=int(academic_id_log), semester=year.id, project=project.id, grade=int(before_grade_log))
            db(db.validate_laboratory_log.id == id_log).update(id_validate_laboratory=insert_delete.id)
        else:
            if before_grade_log != form.vars.grade:
                db(db.validate_laboratory.id == id_validate_laboratory).update(grade=int(before_grade_log))

        session.flash = message_fail
        if fail_check == 2:
            redirect(URL('default', 'home'))

@auth.requires_login()
@auth.requires_membership('Student')
def send_mail_to_students(message, subject, user, check, semester, year):
    control = 0
    was_sent = mail.send(to='dtt.ecys@dtt-ecys.org', subject=subject, message=message, bcc=user)
    #MAILER LOG
    db.mailer_log.insert(
        sent_message=message,
        destination=user,
        result_log=str(mail.error or '') + ':' + str(mail.result),
        success=was_sent,
        emisor=str(check.assigned_user.username)
    )
    if not was_sent: control += 1
    return control

def start_end_time(year, string_start, string_end):
    tiempo = str(datetime.strptime(f'{str(year.yearp)}{string_start}', "%Y-%m-%d"))
    date_inicial_p = db.executesql(f'SELECT DATE(\'{tiempo}\');', as_dict=True)
    for d0 in date_inicial_p:
        start = d0[f'DATE(\'{tiempo}\')']
    
    tiempo = str(datetime.strptime(f'{str(year.yearp)}{string_end}', "%Y-%m-%d"))
    date_inicial_p = db.executesql(f'SELECT DATE(\'{tiempo}\');', as_dict=True)
    for d0 in date_inicial_p:
        end = d0[f'DATE(\'{tiempo}\')']

    return (start, end)

@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator'))
def array_to_html_log(log_carga_csv):
    filas_log = ''
    for row in log_carga_csv:
        filas_log += """
                    <li class="error">
                        <pre>{} - </pre>
                    </li>
                    """.format(row[2])

    log_html = """<div class="accordion" id="accordion2">
                    <div class="accordion-group">
                        <div class="accordion-heading">
                            <a class="accordion-toggle" data-toggle="collapse" data-parent="#accordion2" href="#collapseTwo">
                                <span class="icon-warning-sign"></span>{}
                                <span class="pull-right">{}{}</span>
                            </a>
                        </div>
                        <div id="collapseTwo" class="accordion-body collapse">
                            <div class="accordion-inner">
                                <ul>{}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                """.format(T('Notifications'), T('Total Notifications: '), str(len(log_carga_csv)), filas_log)
    
    return log_html

def academic_and_student_courses(periodo, count_courses_student, area):
    academic_course = db(db.academic.carnet == auth.user.username).select().first()
    courses_student_t = 0
    courses_student = None
    if academic_course is not None:
        courses_student = db((db.academic_course_assignation.carnet == academic_course.id) & (db.academic_course_assignation.semester == periodo.id) 
                        & (db.academic_course_assignation.assignation == db.project.id) & (db.project.area_level == area.id)).select(count_courses_student).first()
        courses_student_t = courses_student[count_courses_student]
        courses_student = db((db.academic_course_assignation.carnet == academic_course.id) & (db.academic_course_assignation.semester == periodo.id)
                        & (db.academic_course_assignation.assignation==db.project.id) & (db.project.area_level==area.id)).select()
    
    return(courses_student, courses_student_t)

@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator'))
def nota_valida_csv(valor):
    try:
        valor_float = float(valor)
        return (valor_float >= 0) & (valor_float <= 100)
    except ValueError:
        return False

#LTZOC: Método para carga masiva de notas
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator'))
def dame_fecha(actividad_id):
    period = cpfecys.current_year_period()
    control_p = db((db.student_control_period.period_name == (T(period.period.name) + " " + str(period.yearp)))).select().first()
    t_act = db(db.course_activity.id == actividad_id).select().first()
    maxim_time_grade = db.executesql('SELECT DATE_ADD(\'{}\', INTERVAL {} Day) as fechaMaxGrade;'.format(str(t_act.date_finish), str(control_p.timeout_income_notes)), as_dict=True)

    date_grade = ""
    var_do_grade = False
    for d0 in maxim_time_grade:
        date_grade = d0['fechaMaxGrade']

    if str(datetime.now()) <= str(date_grade):
        var_do_grade = True

    return var_do_grade

def request_change_var_method(exception_query, var_activity, year_var, var_period):
    exception_s_var = False
    exception_t_var = False
    request_change_var = False

    if exception_query is not None:
        exception_t_var = exception_query.t_edit_lab
        exception_s_var = exception_query.s_edit_course

    if auth.has_membership('Student'):
        if var_activity.laboratory or exception_s_var or var_activity.teacher_permition or var_activity.course_activity_category.teacher_permition:
            if var_activity.laboratory:
                #emarquez: periodos variables
                if cpfecys.is_semestre(year_var):
                    comparacion = "{} {}".format(T(var_period.period.name), str(var_period.yearp))
                    control_p = db((db.student_control_period.period_name == comparacion)).select().first()
                else:
                    actual_semester = db(db.period_year.id == id_year).select().first()
                    control_p = db((db.period_detail.period == actual_semester.period)).select().first()

                query = 'SELECT DATE_ADD(\'{}\', INTERVAL {} Day) AS fechaMaxGrade;'.format(str(var_activity.date_finish), str(control_p.timeout_income_notes))
                maxim_time_grade = db.executesql(query ,as_dict=True)
                date_grade = ''
                for date in maxim_time_grade:
                    date_grade = date['fechaMaxGrade']

                if str(datetime.now()) <= str(dateGrade0):
                    request_change_var = True
            else:
                request_change_var = True
    elif auth.has_membership('Teacher'):
        if var_activity.laboratory and exception_t_var:
                request_change_var = True
        else:
            request_change_var = True
    elif auth.has_membership('Ecys-Administrator'):
        request_change_var = True
    elif auth.has_membership('Super-Administrator'):
        request_change_var = True

    if not request_change_var: request_change_var = True
    else: request_change_var = False

    return request_change_var

def get_rol():
    rol_temp = ''
    if auth.has_membership('Super-Administrator'):
        rol_temp = 'Super-Administrator'
    elif auth.has_membership('Ecys-Administrator'):
        rol_temp = 'Ecys-Administrator'
    elif auth.has_membership('Teacher'):
        rol_temp = 'Teacher'
    elif auth.has_membership('Student'):
        rol_temp = 'Student'

    return rol_temp

def split_name(project):
    try:
        (name_project, _) = str(project).split('(')
    except:
        name_project = project
    
    return name_project

def split_section(project):
    name_section = None
    try:
        project_section = None
        (_, project_section) = str(project).split('(')
        (name_section, _) = str(project_section).split(')')
    except:
        name_section = '--------'
    
    return name_section

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def tipo_periodo():
    grid = SQLFORM.grid(db.period_type, maxtextlength=100, csv=False)
    return dict(grid=grid)