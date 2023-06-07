import cpfecys

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def general_information():
    info_level = []
    group_periods = None
    period = None
    project = None

    try:
        #CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars['level'] is not None and (int(request.vars['level']) < 1 or int(request.vars['level']) > 2):
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

        #CHECK THAT THE AREA EXIST
        area = db(db.area_level.name == 'DTT Tutor Académico').select(db.area_level.id).first()
        if area is None:
            session.flash = T('Report no visible: There are no parameters required to display the report.')
            redirect(URL('default', 'home'))

        #CHECK IF THE PERIOD IS CHANGE
        if request.vars['period'] is None:
            cperiod = cpfecys.current_year_period()
            period = db(db.period_year.id == cperiod.id).select(db.period_year.id, db.period_year.period, db.period_year.yearp).first()
        else:
            period = db(db.period_year.id == int(request.vars['period'])).select(db.period_year.id, db.period_year.period, db.period_year.yearp).first()
            if period is None:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))

        #CHECK PARAMETERS
        if request.vars['level'] == '1' or request.vars['level'] is None:
            group_periods = db(db.period_year).select(db.period_year.id, db.period_year.period, db.period_year.yearp, orderby=~db.period_year.id)
            if len(group_periods) == 0:
                session.flash = T('Report no visible: There are no parameters required to display the report.')
                redirect(URL('default', 'home'))

            group_projects = db(db.project.area_level == area.id).select(db.project.id, db.project.name, orderby=db.project.name)
            if len(group_projects) == 0:
                session.flash = T('Report no visible: There are no parameters required to display the report.')
                redirect(URL('default', 'home'))
        else:
            project = db((db.project.id == int(request.vars['project'])) & (db.project.area_level == area.id)).select().first()
            if project is None:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))
    except:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    #*****************************************************REPORT*****************************************************
    #ALL SEMESTERS
    if request.vars['level'] == '1' or request.vars['level'] is None:
        #ALL PROJECTS
        for project in group_projects:
            infoe_level_temp = []
            #ID OF PROJECT
            infoe_level_temp.append(project.id)
            #NAME OF PROJECT
            infoe_level_temp.append(project.name)
            #COUNT TEACHERS
            infoe_level_temp.append(get_assignations(project, period, 'Teacher').count())
            #ACADEMIC TUTORS COUNT
            infoe_level_temp.append(get_assignations(project, period, 'Student').count())
            info_level.append(infoe_level_temp)
    else:
        info_level.append(get_assignations(project, period, 'Teacher').select(db.user_project.ALL))
        info_level.append(get_assignations(project, period, 'Student').select(db.user_project.ALL))

        sc = db(db.item_restriction.name == 'Horario Clase').select(db.item_restriction.id).first()
        info_level.append([])
        if sc is not None and len(info_level[1]) > 0:       
            for assignation in info_level[1]:
                r_hl = db((db.item.item_restriction == sc.id) & (db.item.created == period.id)
                        & (db.item.assignation == assignation.id)).select().first()
                if r_hl is not None and len(info_level[2]) < r_hl.item_schedule.count():
                    info_level[2] = r_hl.item_schedule.select()

        sc = db(db.item_restriction.name == 'Horario Laboratorio').select(db.item_restriction.id).first()
        info_level.append([])
        if sc is not None and len(info_level[1]) > 0:       
            for assignation in info_level[1]:
                r_hl = db((db.item.item_restriction == sc.id) & (db.item.created == period.id)
                        & (db.item.assignation == assignation.id)).select().first()
                if r_hl is not None and len(info_level[3]) < r_hl.item_schedule.count():
                    info_level[3] = r_hl.item_schedule.select()

    return dict(group_periods=group_periods, period=period, info_level=info_level, project=project)

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def general_information_export():
    info_level = []
    period = None
    project = None
    try:
        #CHECK IF THE TYPE OF EXPORT IS VALID
        if request.vars['list_type'] is None or str(request.vars['list_type']) != "csv":
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
            
        #CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars['level'] is not None and (int(request.vars['level']) < 1 or int(request.vars['level']) > 2):
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

        #CHECK THAT THE AREA EXIST
        area = db(db.area_level.name == 'DTT Tutor Académico').select(db.area_level.id).first()
        if area is None:
            session.flash = T('Report no visible: There are no parameters required to display the report.')
            redirect(URL('default', 'home'))

        #CHECK IF THE PERIOD IS CHANGE
        if request.vars['period'] is None:
            cperiod = cpfecys.current_year_period()
            period = db(db.period_year.id == cperiod.id).select(db.period_year.id, db.period_year.period, db.period_year.yearp).first()
        else:
            period = db(db.period_year.id==int(request.vars['period'])).select(db.period_year.id, db.period_year.period, db.period_year.yearp).first()
            if period is None:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))

        #CHECK PARAMETERS
        if request.vars['level'] == '1' or request.vars['level'] is None:
            group_projects = db(db.project.area_level == area.id).select(orderby=db.project.name)
            if len(group_projects) == 0:
                session.flash = T('Report no visible: There are no parameters required to display the report.')
                redirect(URL('default', 'home'))
        else:
            project = db((db.project.id == int(request.vars['project'])) & (db.project.area_level  ==area.id)).select().first()
            if project is None:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))
    except:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    #*****************************************************REPORT*****************************************************
    #TITLE
    info_level = []
    info_level.append(['Universidad de San Carlos de Guatemala'])
    info_level.append(['Facultad de Ingeniería'])
    info_level.append(['Escuela de Ingeniería Ciencias y Sistemas'])
    info_level.append([''])
    #TYPE OF REPORT
    info_level.append(['Tipo', 'Información general'])
    #DESCRIPTION OF REPORT
    info_level.append(['Descripción', 'Reporte sobre la información general de los cursos registrados en el sistema.'])
    #PERIOD OF REPORT
    info_level.append(['Periodo', f'{T(period.period.name)} {period.yearp}'])
    #ALL SEMESTERS
    if request.vars['level'] == '1' or request.vars['level'] is None:
        #MIDDLE LINE OF REPORT
        info_level.append([])
        #LABLE DETAIL OF REPORT
        info_level.append(['Detalle'])
        #LABELS OF DATA OF REPORT
        info_level.append(['Curso', 'Catedráticos activos', 'Tutores académicos asignados', 'Estado del curso'])
        #ALL PROJECTS
        for project in group_projects:
            infoe_level_temp = []
            #NAME OF PROJECT
            infoe_level_temp.append(project.name)
            #COUNT TEACHERS
            infoe_level_temp.append(get_assignations(project, period, 'Teacher').count())
            #ACADEMIC TUTORS COUNT
            infoe_level_temp.append(get_assignations(project, period, 'Student').count())
            #STATUS OF COURSE
            if (infoe_level_temp[1] + infoe_level_temp[2]) > 0:
                infoe_level_temp.append('Activo')
            else:
                infoe_level_temp.append('Inactivo')
            info_level.append(infoe_level_temp)
    else:
        info_level_2 = []
        info_level_2.append(get_assignations(project, period, 'Teacher').select(db.user_project.ALL))
        info_level_2.append(get_assignations(project, period, 'Student').select(db.user_project.ALL))

        sc = db(db.item_restriction.name == 'Horario Clase').select(db.item_restriction.id).first()
        info_level_2.append([])
        if sc is not None and len(info_level_2[1]) > 0:       
            for assignation in info_level_2[1]:
                r_hl = db((db.item.item_restriction == sc.id) & (db.item.created == period.id)
                        & (db.item.assignation == assignation.id)).select().first()
                if r_hl is not None and len(info_level_2[2]) < r_hl.item_schedule.count():
                    info_level_2[2] = r_hl.item_schedule.select()

        sc = db(db.item_restriction.name == 'Horario Laboratorio').select(db.item_restriction.id).first()
        info_level_2.append([])
        if sc is not None and len(info_level_2[1]) > 0:       
            for assignation in info_level_2[1]:
                r_hl = db((db.item.item_restriction == sc.id) & (db.item.created == period.id)
                        & (db.item.assignation == assignation.id)).select().first()
                if r_hl is not None and len(info_level_2[3]) < r_hl.item_schedule.count():
                    info_level_2[3] = r_hl.item_schedule.select()

        #PROJECT
        info_level.append(['Curso', project.name])
        #MIDDLE LINE OF REPORT
        info_level.append([])
        #LABLE DETAIL OF REPORT
        info_level.append(['Información del curso'])

        #Current Teacher
        info_level.append(['Catedrático activo'])
        if len(info_level_2[0]) <= 0:
            info_level.append(['', 'No asignado'])
        else:
            for student in info_level_2[0]:
                info_level.append(['', 'Nombre de usuario', student.assigned_user.username])
                info_level.append(['', 'Nombre', f'{student.assigned_user.first_name} {student.assigned_user.last_name}'])
                info_level.append(['', 'Correo electrónico', student.assigned_user.email])
                info_level.append(['', 'Teléfono', student.assigned_user.phone])
                info_level.append([''])

        info_level.append([''])
        info_level.append([''])

        #Assigned Tutor
        info_level.append(['Tutor asignado'])
        if len(info_level_2[1])  <=0:
            info_level.append(['', 'No asignado'])
        else:
            for student in info_level_2[1]:
                info_level.append(['', 'Nombre de usuario', student.assigned_user.username])
                info_level.append(['', 'Nombre', f'{student.assigned_user.first_name} {student.assigned_user.last_name}'])
                info_level.append(['', 'Correo electrónico', student.assigned_user.email])
                info_level.append(['', 'Teléfono', student.assigned_user.phone])
                info_level.append([''])

        info_level.append([''])
        info_level.append([''])

        #Assigned Tutor
        info_level.append(['Horario clase:'])
        if len(info_level_2[2]) <= 0:
            info_level.append(['', 'No asigando'])
        else:
            for student in info_level_2[2]:
                info_level.append(['', 'Ubicación', student.physical_location])
                info_level.append(['', 'Día', db(db.day_of_week.id==student.day_of_week).select().first()['name']])
                info_level.append(['', 'Hora de inicio', student.start_time])
                info_level.append(['', 'Hora de finalización', student.end_time])
                info_level.append([''])
        
        info_level.append([''])
        info_level.append([''])

        #Assigned Tutor
        info_level.append(['Horario laboratorio:'])
        if len(info_level_2[3]) <= 0:
            info_level.append(['', 'No asignado'])
        else:
            for student in info_level_2[3]:
                info_level.append(['', 'Ubicación', student.physical_location])
                info_level.append(['', 'Día', db(db.day_of_week.id==student.day_of_week).select().first()['name']])
                info_level.append(['', 'Hora de inicio', student.start_time])
                info_level.append(['', 'Hora de finalización', student.end_time])
                info_level.append([''])

    return dict(csvdata=info_level)

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def general_period():
    info_level = []
    group_periods = None
    period = None

    try:
        #CHECK THAT THE AREA EXIST
        area = db(db.area_level.name == 'DTT Tutor Académico').select(db.area_level.id).first()
        if area is None:
            session.flash = T('Report no visible: There are no parameters required to display the report.')
            redirect(URL('default', 'home'))

        #CHECK IF THE PERIOD IS CHANGE
        if request.vars['period'] is None:
            cperiod = cpfecys.current_year_period()
            period = db(db.period_year.id == cperiod.id).select(db.period_year.period, db.period_year.id, db.period_year.yearp).first()
        else:
            period = db(db.period_year.id == request.vars['period']).select(db.period_year.period, db.period_year.id, db.period_year.yearp).first()
            if period is None:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))

        #CHECK PARAMETERS
        group_periods = db(db.period_year).select(db.period_year.period, db.period_year.id, db.period_year.yearp, orderby=~db.period_year.id)
        if len(group_periods) == 0:
            session.flash = T('Report no visible: There are no parameters required to display the report.')
            redirect(URL('default', 'home'))

        group_projects = db((db.project.area_level == area.id) & (db.user_project.period <= period.id) 
                        & ((db.user_project.period + db.user_project.periods) > period.id)).select(
                            db.project.name,
                            db.project.id,
                            join=[db.project.on(db.user_project.project == db.project.id)],
                            orderby=db.project.name,
                            distinct=True
                        )
        if len(group_projects) == 0:
            session.flash = T('Report no visible: There are no parameters required to display the report.')
            redirect(URL('default', 'home'))

        partials = db(db.partials).select(db.partials.name)
    except:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    #*****************************************************REPORT*****************************************************
    infoe_level_temp = ['Curso', 'Total de alumnos asignados al curso']
    infoe_level_temp.extend([f'Promedio de notas de {partial.name}' for partial in partials])
    infoe_level_temp.extend(['Promedio de notas de examen final', 'Porcentaje de alumnos que aprobaron el laboratorio', 'Porcentaje de alumnos que aprobaron el curso'])
    info_level.append(infoe_level_temp)

    #ALL PROJECTS
    control_p = db(db.student_control_period.period_name == f'{T(period.period.name)} {period.yearp}').select(
                    db.student_control_period.min_average,
                    db.student_control_period.max_average
                ).first()
    query = db((db.activity_category.category == 'Examen Final') | (db.activity_category.category == 'Laboratorio')).select(db.activity_category.id, orderby=db.activity_category.category)
    ID_EXAMEN = query[0].id
    ID_LABORATORIO = query[1].id
    if control_p is not None:
        for project in group_projects:
            infoe_level_temp = []

            #NAME OF PROJECT
            infoe_level_temp.append(project.name)

            #TOTAL STUDENTS
            students = db((db.academic_course_assignation.semester == period.id) & (db.academic_course_assignation.assignation == project.id)).select(
                            db.academic_course_assignation.id,
                            db.academic_course_assignation.laboratorio
                        )
            infoe_level_temp.append(len(students))

            #PARTIALS
            for partial in partials:
                average = 0.0
                activity_partial = db((db.course_activity.assignation == project.id) & (db.course_activity.semester == period.id)
                                    & (db.course_activity.name == partial.name) & (db.course_activity.laboratory == False)).select(db.course_activity.id).first()
                if activity_partial is not None:
                    average_a = db.executesql(f'SELECT AVG(grade) AS average FROM grades WHERE activity = {activity_partial.id};', as_dict=True)[0]
                    if average_a['average'] is not None:
                        average = f"{average_a['average']:.2f}"
                infoe_level_temp.append(average)

            #FINAL TEST
            average = 0.0
            activity_final = db((db.course_activity.assignation == project.id) & (db.course_activity.semester == period.id)
                            & (db.course_activity.name == 'Examen Final') & (db.course_activity.laboratory == False)).select(db.course_activity.id).first()
            if activity_final is not None:
                average_a = db.executesql(f'SELECT AVG(grade) AS average FROM grades WHERE activity = {activity_final.id};', as_dict=True)[0]
                if average_a['average'] is not None:
                    average = f"{average_a['average']:.2f}"
            infoe_level_temp.append(average)

            #CLASS AND LABORATORY
            total_win_laboratory = 0
            total_win_class = 0

            #LABORATORY
            categories_lab = []
            for categories in db((db.course_activity_category.assignation == project.id) & (db.course_activity_category.semester == period.id)
                            & (db.course_activity_category.laboratory == True)).select(db.course_activity_category.grade, db.course_activity_category.specific_grade, db.course_activity_category.id):
                activity_class = []
                total_a = 0
                for activity in db(db.course_activity.course_activity_category == categories.id).select(db.course_activity.id, db.course_activity.grade):
                    if db(db.grades.activity == activity.id).select(db.grades.id).first(): activity_class.append(activity)
                    total_a += 1
                
                if len(activity_class) > 0:
                    categories_lab.append([categories, activity_class, total_a])

            #CLASS
            categories_class = []
            for categories in db((db.course_activity_category.assignation == project.id) & (db.course_activity_category.semester == period.id)
                            & (db.course_activity_category.laboratory == False)).select(db.course_activity_category.category, db.course_activity_category.specific_grade, db.course_activity_category.grade, db.course_activity_category.id):
                if categories.category != ID_LABORATORIO:
                    activity_class = []
                    total_a = 0
                    for activity in db(db.course_activity.course_activity_category == categories.id).select(db.course_activity.id, db.course_activity.grade):
                        if db(db.grades.activity == activity.id).select(db.grades.id).first(): activity_class.append(activity)
                        total_a += 1

                    if len(activity_class) > 0:
                        categories_class.append([categories, activity_class, total_a])
                else:
                    categories_class.append([categories, 0])

            #Total of grades
            lab_grades_dict  = {g.carnet: g.grade for g in db((db.validate_laboratory.semester == period.id) & (db.validate_laboratory.project == project.id)
                        & (db.validate_laboratory.carnet.belongs([s.id for s in students]))).select(db.validate_laboratory.carnet, db.validate_laboratory.grade)}

            #GRADE OF STUDENT
            for student in students:
                #GRADE OF LABORATORY
                grade_laboratory = 0
                if student.id not in lab_grades_dict:
                    if student.laboratorio:
                        total_carry_lab = 0.0
                        for category_lab in categories_lab:
                            category_specific_grade = category_lab[0].specific_grade
                            total_category_lab = 0.0
                            for c_lab in category_lab[1]:
                                student_grade = db((db.grades.activity == c_lab.id) & (db.grades.academic_assignation == student.id)).select(db.grades.grade).first()
                                if student_grade is not None:
                                    if category_specific_grade:
                                        total_category_lab += float((student_grade.grade * c_lab.grade) / 100)
                                    else:
                                        total_category_lab += float(student_grade.grade)
                            if not category_specific_grade:
                                total_category_lab = float((total_category_lab * float(category_lab[0].grade)) / float(category_lab[2] * 100))
                            total_carry_lab += total_category_lab
                        grade_laboratory = int(round(total_carry_lab, 0))
                        if grade_laboratory >= 61:
                            total_win_laboratory += 1
                else:
                    grade_laboratory = int(round(lab_grades_dict[student.id].grade, 0))
                
                #GRADE OF CLASS
                total_carry = 0.0
                total_final = 0.0
                for category_class in categories_class:
                    total_category = 0.0
                    if category_class[0].category == ID_EXAMEN:
                        for c in category_class[1]:
                            student_grade = db((db.grades.activity == c.id) & (db.grades.academic_assignation == student.id)).select(db.grades.grade).first()
                            if student_grade is not None:
                                if category_class[0].specific_grade:
                                    total_final += float((student_grade.grade * c.grade) / 100)
                                else:
                                    total_final += float(student_grade.grade)
                        if not category_class[0].specific_grade:
                            total_final = float((total_final * float(category_class[0].grade)) / float(category_class[2] * 100))
                        total_final = int(round(total_final, 0))
                    elif category_class[0].category == ID_LABORATORIO:
                        grade_laboratory = float((grade_laboratory * float(category_class[0].grade)) / 100)
                    else:
                        for c in category_class[1]:
                            student_grade = db((db.grades.activity == c.id) & (db.grades.academic_assignation == student.id)).select(db.grades.grade).first()
                            if student_grade is not None:
                                if category_class[0].specific_grade:
                                    total_category += float((student_grade.grade * c.grade) / 100)
                                else:
                                    total_category += float(student_grade.grade)
                        if not category_class[0].specific_grade:
                            total_category = float((total_category * float(category_class[0].grade)) / float(category_class[2] * 100))
                        total_carry += total_category
                total_carry += int(round(grade_laboratory, 0)) + int(round(total_final, 0))

                if total_carry >= 61:
                    total_win_class += 1

            #LABORATORY
            students_lab = db((db.academic_course_assignation.semester == period.id) & (db.academic_course_assignation.assignation == project.id)
                            & (db.academic_course_assignation.laboratorio == True)).count()
            if students_lab > 0:
                total_win_laboratory = round(((total_win_laboratory * 100) / students_lab), 2)
            infoe_level_temp.append(total_win_laboratory)
            
            #CLASS
            if len(students) > 0:
                total_win_class = round(((total_win_class * 100) / len(students)), 2)
            infoe_level_temp.append(total_win_class)
            info_level.append(infoe_level_temp)

    return dict(group_periods=group_periods, period=period, info_level=info_level, control_p=control_p)

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def general_period_export():
    info_level = []
    period = None
    try:
        #CHECK IF THE TYPE OF EXPORT IS VALID
        if request.vars['list_type'] is None or str(request.vars['list_type']) != "csv":
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

        #CHECK THAT THE AREA EXIST
        area = db(db.area_level.name == 'DTT Tutor Académico').select(db.area_level.id).first()
        if area is None:
            session.flash = T('Report no visible: There are no parameters required to display the report.')
            redirect(URL('default', 'home'))

        #CHECK IF THE PERIOD IS CHANGE
        if request.vars['period'] is None:    
            cperiod = cpfecys.current_year_period()
            period = db(db.period_year.id == cperiod.id).select(db.period_year.period, db.period_year.id, db.period_year.yearp).first()
        else:
            period = db(db.period_year.id == request.vars['period']).select(db.period_year.period, db.period_year.id, db.period_year.yearp).first()
            if period is None:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))

        #CHECK PARAMETERS
        group_projects = db((db.project.area_level == area.id) & (db.user_project.period <= period.id) 
                        & ((db.user_project.period + db.user_project.periods) > period.id)).select(
                            db.project.name,
                            db.project.id,
                            join=[db.project.on(db.user_project.project == db.project.id)],
                            orderby=db.project.name,
                            distinct=True
                        )
        if len(group_projects) == 0:
            session.flash = T('Report no visible: There are no parameters required to display the report.')
            redirect(URL('default', 'home'))

        partials = db(db.partials).select(db.partials.name)
    except:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    #*****************************************************REPORT*****************************************************
    #TITLE
    info_level = []
    info_level.append(['Universidad de San Carlos de Guatemala'])
    info_level.append(['Facultad de Ingeniería'])
    info_level.append(['Escuela de Ingeniería en Ciencias y Sistemas'])

    #MIDDLE LINE OF REPORT
    info_level.append([''])

    #TYPE OF REPORT
    info_level.append(['Tipo', 'Información general de semestre'])

    #DESCRIPTION OF REPORT
    info_level.append(['Descripción', 'Reporte sobre la información general de los cursos por semestre.'])

    #PERIOD OF REPORT
    info_level.append(['Periodo', f'{period.period.name} {period.yearp}'])

    #MIDDLE LINE OF REPORT
    info_level.append([''])

    #LABLE DETAIL OF REPORT
    info_level.append(['Detalle'])

    infoe_level_temp = ['Curso', 'Total de alumnos asignados al curso']
    for partial in partials:
        infoe_level_temp.append(f'Promedio de notas de {partial.name}')

    infoe_level_temp.append('Promedio de notas de examen final')
    infoe_level_temp.append('Porcentaje de alumnos que aprobaron el laboratorio')
    infoe_level_temp.append('Porcentaje de alumnos que aprobaron el curso')
    info_level.append(infoe_level_temp)

    query = db((db.activity_category.category == 'Examen Final') | (db.activity_category.category == 'Laboratorio')).select(db.activity_category.id, orderby=db.activity_category.category)
    ID_EXAMEN = query[0].id
    ID_LABORATORIO = query[1].id

    #ALL PROJECTS
    control_p = db(db.student_control_period.period_name == f'{T(period.period.name)} {period.yearp}').select(db.student_control_period.id).first()
    if control_p is not None:
        for project in group_projects:
            infoe_level_temp = []

            #NAME OF PROJECT
            infoe_level_temp.append(project.name)

            #TOTAL STUDENTS
            students = db((db.academic_course_assignation.semester == period.id) & (db.academic_course_assignation.assignation == project.id)).select()
            infoe_level_temp.append(len(students))

            #PARTIALS
            for partial in partials:
                average = 0.0
                activity_partial = db((db.course_activity.assignation == project.id) & (db.course_activity.semester == period.id)
                                    & (db.course_activity.name == partial.name) & (db.course_activity.laboratory == False)).select(db.course_activity.id).first()
                if activity_partial is not None:
                    average_a = db.executesql(f'SELECT AVG(grade) AS average FROM grades WHERE activity = {activity_partial.id};', as_dict=True)[0]
                    if average_a['average'] is not None:
                        average = f"{average_a['average']:.2f}"

                infoe_level_temp.append(average)

            #FINAL TEST
            average = 0.0
            activity_final = db((db.course_activity.assignation == project.id) & (db.course_activity.semester == period.id)
                            & (db.course_activity.name == 'Examen Final') & (db.course_activity.laboratory == False)).select(db.course_activity.id).first()
            if activity_final is not None:
                average_a = db.executesql(f'SELECT AVG(grade) AS average FROM grades WHERE activity = {activity_final.id};', as_dict=True)[0]
                if average_a['average'] is not None:
                    average = f"{average_a['average']:.2f}"
            infoe_level_temp.append(average)

            #CLASS AND LABORATORY
            total_win_laboratory = 0.0
            total_win_class = 0.0

            #LABORATORY
            categories_lab = []
            for categories in db((db.course_activity_category.assignation == project.id) & (db.course_activity_category.semester == period.id)
                            & (db.course_activity_category.laboratory == True)).select(db.course_activity_category.id, db.course_activity_category.grade, db.course_activity_category.specific_grade):
                activity_class = []
                total_a = 0
                for activity in db(db.course_activity.course_activity_category == categories.id).select(db.course_activity.id, db.course_activity.grade):
                    if db(db.grades.activity == activity.id).select(db.grades.id).first(): activity_class.append(activity)
                    total_a += 1

                if len(activity_class) > 0:
                    categories_lab.append([categories, activity_class, total_a])

            #CLASS
            categories_class = []
            for categories in db((db.course_activity_category.assignation == project.id) & (db.course_activity_category.semester == period.id)
                            & (db.course_activity_category.laboratory == False)).select(db.course_activity_category.id, db.course_activity_category.grade, db.course_activity_category.specific_grade, db.course_activity_category.category):
                if categories.category != ID_LABORATORIO:
                    activity_class = []
                    total_a = 0
                    for activity in db(db.course_activity.course_activity_category == categories.id).select(db.course_activity.id, db.course_activity.grade):
                        if db(db.grades.activity == activity.id).select(db.grades.id).first(): activity_class.append(activity)
                        total_a += 1

                    if len(activity_class) > 0:
                        categories_class.append([categories, activity_class, total_a])
                else:
                    categories_class.append([categories, 0])

            lab_grades_dict  = {g.carnet: g.grade for g in db((db.validate_laboratory.semester == period.id) & (db.validate_laboratory.project == project.id)
                            & (db.validate_laboratory.carnet.belongs([s.id for s in students]))).select(db.validate_laboratory.carnet, db.validate_laboratory.grade)}

            #GRADE OF STUDENT
            for student in students:
                #GRADE OF LABORATORY
                grade_laboratory = 0
                if student.id not in lab_grades_dict:
                    if student.laboratorio:
                        total_carry_lab = 0.0
                        for category_lab in categories_lab:
                            total_category_lab = 0.0
                            for c_lab in category_lab[1]:
                                student_grade = db((db.grades.activity == c_lab.id) & (db.grades.academic_assignation == student.id)).select(db.grades.grade).first()
                                if student_grade is not None:
                                    if category_lab[0].specific_grade:
                                        total_category_lab += float((student_grade.grade * c_lab.grade) / 100)
                                    else:
                                        total_category_lab += float(student_grade.grade)
                            if not category_lab[0].specific_grade:
                                total_category_lab = float((total_category_lab * float(category_lab[0].grade)) / float(category_lab[2]*100))
                            total_carry_lab += total_category_lab
                        grade_laboratory = int(round(total_carry_lab, 0))
                        if grade_laboratory >= 61:
                            total_win_laboratory += 1
                else:
                    grade_laboratory = int(round(lab_grades_dict[student.id].grade, 0))
                
                #GRADE OF CLASS
                total_carry = 0.0
                total_final = 0.0

                for category_class in categories_class:
                    total_category = 0.0
                    if category_class[0].category == ID_EXAMEN:
                        for c in category_class[1]:
                            student_grade = db((db.grades.activity == c.id) & (db.grades.academic_assignation == student.id)).select(db.grades.grade).first()
                            if student_grade is not None:
                                if category_class[0].specific_grade:
                                    total_final += float((student_grade.grade * c.grade) / 100)
                                else:
                                    total_final += float(student_grade.grade)
                        if not category_class[0].specific_grade:
                            total_final = float((total_final * float(category_class[0].grade)) / float(category_class[2] * 100))
                        total_final = int(round(total_final, 0))
                    elif category_class[0].category == ID_LABORATORIO:
                        grade_laboratory = float((grade_laboratory * float(category_class[0].grade)) / 100)
                    else:
                        for c in category_class[1]:
                            student_grade = db((db.grades.activity == c.id) & (db.grades.academic_assignation == student.id)).select(db.grades.grade).first()
                            if student_grade is not None:
                                if category_class[0].specific_grade:
                                    total_category += float((student_grade.grade * c.grade) / 100)
                                else:
                                    total_category += float(student_grade.grade)
                        if not category_class[0].specific_grade:
                            total_category = float((total_category * float(category_class[0].grade)) / float(category_class[2] * 100))
                        total_carry += total_category
                total_carry += int(round(grade_laboratory, 0)) + int(round(total_final, 0))

                if total_carry >= 61:
                    total_win_class += 1
            #LABORATORY
            students_lab = db((db.academic_course_assignation.semester == period.id) & (db.academic_course_assignation.assignation == project.id)
                            & (db.academic_course_assignation.laboratorio == True)).count()
            if students_lab > 0:
                total_win_laboratory = round(((total_win_laboratory * 100) / students_lab), 2)
            infoe_level_temp.append(total_win_laboratory)
            
            #CLASS
            if len(students) > 0:
                total_win_class = round(((total_win_class * 100) / len(students)), 2)
            infoe_level_temp.append(total_win_class)
            info_level.append(infoe_level_temp)
    
    return dict(csvdata=info_level)

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def historic_course():
    info_level = []
    group_periods = None
    period = None
    project = None

    try:
        #CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars['level'] is not None and (int(request.vars['level']) < 1 or int(request.vars['level']) > 2):
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

        #CHECK THAT THE AREA EXIST
        area = db(db.area_level.name == 'DTT Tutor Académico').select(db.area_level.id).first()
        if area is None:
            session.flash = T('Report no visible: There are no parameters required to display the report.')
            redirect(URL('default', 'home'))

        #CHECK IF THE PERIOD IS CHANGE
        if request.vars['period'] is None:
            cperiod = cpfecys.current_year_period()
            period = db(db.period_year.id == cperiod.id).select(db.period_year.period, db.period_year.id, db.period_year.yearp).first()
        else:
            period = db(db.period_year.id == request.vars['period']).select(db.period_year.period, db.period_year.id, db.period_year.yearp).first()
            if period is None:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))

        #CHECK PARAMETERS
        if request.vars['level'] == '1' or request.vars['level'] is None:
            group_periods = db(db.period_year).select(db.period_year.period, db.period_year.id, db.period_year.yearp, orderby=~db.period_year.id)
            if len(group_periods) == 0:
                session.flash = T('Report no visible: There are no parameters required to display the report.')
                redirect(URL('default', 'home'))
            
            group_projects = db((db.project.area_level == area.id) & (db.user_project.period <= period.id) 
                            & ((db.user_project.period + db.user_project.periods) > period.id)).select(
                                db.project.name,
                                db.project.id,
                                join=[db.project.on(db.user_project.project == db.project.id)],
                                orderby=db.project.name,
                                distinct=True
                            )
            if len(group_projects) == 0:
                session.flash = T('Report no visible: There are no parameters required to display the report.')
                redirect(URL('default', 'home'))
        else:
            project = db((db.project.id == request.vars['project']) & (db.project.area_level == area.id)).select().first()

            if project is None:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))
    except:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    # *****************************************************REPORT*************
    #ALL SEMESTERS
    if request.vars['level'] == '1' or request.vars['level'] is None:
        name_courses = []
        #Fill all the courses once time
        for project in group_projects:
            #Get only name
            name_c = get_name(project)

            #Get unique name
            name_c = get_unique_name(name_c)

            #Fill the name of the courses
            exits = True if name_c in name_courses else False
                
            if not exits:
                name_courses.append(name_c)
        
        query = db((db.activity_category.category == 'Examen Final') | (db.activity_category.category == 'Laboratorio')).select(db.activity_category.id, orderby=db.activity_category.category)
        ID_EXAMEN = query[0].id
        ID_LABORATORIO = query[1].id

        #FOR COURSE
        for course in name_courses:
            sections = db((db.project.name.like(f'%{course}%')) & (db.user_project.project == db.project.id)
                        & (db.user_project.period == db.period_year.id) & ((db.user_project.period <= period.id)
                        & ((db.user_project.period + db.user_project.periods) > period.id))).select(db.project.id, orderby=db.project.name, distinct=True)
            
            infoe_level_temp = [sections.first().id, course, 0, 0, 0, len(sections)]
            for project in sections:
                #Total Students in section
                students = db((db.academic_course_assignation.semester == period.id) & (db.academic_course_assignation.assignation == project.id)).select(
                                db.academic_course_assignation.id,
                                db.academic_course_assignation.laboratorio
                            )
                infoe_level_temp[2] += len(students)

                #LABORATORY
                categories_lab = []
                for categories in db((db.course_activity_category.assignation == project.id) & (db.course_activity_category.semester == period.id)
                                & (db.course_activity_category.laboratory == True)).select(db.course_activity_category.specific_grade, db.course_activity_category.grade, db.course_activity_category.id):
                    activity_class = []
                    total_a = 0
                    for activity in db(db.course_activity.course_activity_category == categories.id).select(db.course_activity.id, db.course_activity.grade):
                        if db(db.grades.activity == activity.id).select(db.grades.id).first():
                            activity_class.append(activity)
                        total_a += 1

                    if len(activity_class)>0:
                        categories_lab.append([categories, activity_class, total_a])

                #CLASS
                categories_class = []
                for categories in db((db.course_activity_category.assignation == project.id) & (db.course_activity_category.semester == period.id)
                                    & (db.course_activity_category.laboratory == False)).select(db.course_activity_category.specific_grade, db.course_activity_category.grade, db.course_activity_category.id, db.course_activity_category.category):
                    if categories.category != ID_LABORATORIO:
                        activity_class = []
                        total_a = 0
                        for activity in db(db.course_activity.course_activity_category == categories.id).select(db.course_activity.id, db.course_activity.grade):
                            if db(db.grades.activity == activity.id).select(db.grades.id).first(): activity_class.append(activity)
                            total_a += 1

                        if len(activity_class) > 0:
                            categories_class.append([categories, activity_class, total_a])
                    else:
                        categories_class.append([categories, 0])

                #Total of grades
                lab_grades_dict  = {g.carnet: g.grade for g in db((db.validate_laboratory.semester == period.id) & (db.validate_laboratory.project == project.id)
                        & (db.validate_laboratory.carnet.belongs([s.id for s in students]))).select(db.validate_laboratory.carnet, db.validate_laboratory.grade)}

                #GRADE OF STUDENT
                for student in students:
                    #GRADE OF LABORATORY
                    grade_laboratory = 0
                    if student.id not in lab_grades_dict:
                        if student.laboratorio:
                            total_carry_lab = 0.0
                            for category_lab in categories_lab:
                                total_category_lab = 0.0
                                for c_lab in category_lab[1]:
                                    student_grade = db((db.grades.activity == c_lab.id) & (db.grades.academic_assignation == student.id)).select(db.grades.grade).first()
                                    if student_grade is not None:
                                        if category_lab[0].specific_grade:
                                            total_category_lab += float((student_grade.grade * c_lab.grade) / 100)
                                        else:
                                            total_category_lab += float(student_grade.grade)
                                if not category_lab[0].specific_grade:
                                    total_category_lab = float((total_category_lab * float(category_lab[0].grade)) / float(category_lab[2]*100))
                                total_carry_lab += total_category_lab
                            grade_laboratory = int(round(total_carry_lab, 0))
                    else:
                        grade_laboratory = int(round(lab_grades_dict[student.id].grade, 0))
                    
                    #GRADE OF CLASS
                    total_carry = 0.0
                    total_final = 0.0

                    for category_class in categories_class:
                        total_category = 0.0
                        if category_class[0].category == ID_EXAMEN:
                            for c in category_class[1]:
                                student_grade = db((db.grades.activity == c.id) & (db.grades.academic_assignation == student.id)).select(db.grades.grade).first()
                                if student_grade is not None:
                                    if category_class[0].specific_grade:
                                        total_final += float((student_grade.grade * c.grade) / 100)
                                    else:
                                        total_final += float(student_grade.grade)
                            if not category_class[0].specific_grade:
                                total_final = float((total_final * float(category_class[0].grade)) / float(category_class[2] * 100))
                            total_final = int(round(total_final, 0))
                        elif category_class[0].category == ID_LABORATORIO:
                            grade_laboratory = float((grade_laboratory * float(category_class[0].grade)) / 100)
                        else:
                            for c in category_class[1]:
                                student_grade = db((db.grades.activity == c.id) & (db.grades.academic_assignation == student.id)).select(db.grades.grade).first()
                                if student_grade is not None:
                                    if category_class[0].specific_grade:
                                        total_category += float((student_grade.grade * c.grade) / 100)
                                    else:
                                        total_category += float(student_grade.grade)
                            if not category_class[0].specific_grade:
                                total_category = float((total_category * float(category_class[0].grade)) / float(category_class[2] * 100))
                            total_carry += total_category

                    total_carry = int(round(grade_laboratory, 0)) + int(round(total_final, 0))
                    if total_carry >= 61:
                        infoe_level_temp[3] += 1
                    else:
                        infoe_level_temp[4] += 1
            info_level.append(infoe_level_temp)
    #PROJECT
    elif request.vars['level'] == '2':
        name_courses = []

        #Get only name
        name_c = get_name(project)

        #Get unique name
        name_c = get_unique_name(name_c)

        #Fill the name of the courses
        name_courses.append(name_c)

        query = db((db.activity_category.category == 'Examen Final') | (db.activity_category.category == 'Laboratorio')).select(db.activity_category.id, orderby=db.activity_category.category)
        ID_EXAMEN = query[0].id
        ID_LABORATORIO = query[1].id

        #FOR COURSE
        for course in name_courses:
            sections = db((db.project.name.like(f'%{course}%')) & (db.user_project.project == db.project.id)
                        & (db.user_project.period == db.period_year.id) & ((db.user_project.period <= period.id)
                        & ((db.user_project.period + db.user_project.periods) > period.id))).select(db.project.name, db.project.id, orderby=db.project.name, distinct=True)
            for project in sections:
                infoe_level_temp = [project.name, 0, 0, 0]

                #Total Students in section
                students = db((db.academic_course_assignation.semester == period.id) & (db.academic_course_assignation.assignation == project.id)).select(
                                db.academic_course_assignation.id,
                                db.academic_course_assignation.laboratorio
                            )
                infoe_level_temp[1] += len(students)

                #LABORATORY
                categories_lab = []
                for categories in db((db.course_activity_category.assignation == project.id) &(db.course_activity_category.semester == period.id)
                                    & (db.course_activity_category.laboratory == True)).select(db.course_activity_category.grade, db.course_activity_category.id, db.course_activity_category.specific_grade):
                    activity_class = []
                    total_a = 0
                    for activity in db(db.course_activity.course_activity_category == categories.id).select(db.course_activity.id, db.course_activity.grade):
                        if db(db.grades.activity == activity.id).select(db.grades.id).first():
                            activity_class.append(activity)
                        total_a += 1
                    if len(activity_class) > 0:
                        categories_lab.append([categories, activity_class, total_a])

                #CLASS
                categories_class = []
                for categories in db((db.course_activity_category.assignation == project.id) & (db.course_activity_category.semester == period.id)
                                    & (db.course_activity_category.laboratory == False)).select(db.course_activity_category.category, db.course_activity_category.id, db.course_activity_category.grade, db.course_activity_category.specific_grade):
                    if categories.category != ID_LABORATORIO:
                        activity_class = []
                        total_a = 0
                        for activity in db(db.course_activity.course_activity_category == categories.id).select(db.course_activity.id, db.course_activity.grade):
                            if db(db.grades.activity == activity.id).select(db.grades.id).first():
                                activity_class.append(activity)
                            total_a += 1
                        if len(activity_class) > 0:
                            categories_class.append([categories, activity_class, total_a])
                    else:
                        categories_class.append([categories, 0])

                #Total of grades
                lab_grades_dict  = {g.carnet: g.grade for g in db((db.validate_laboratory.semester == period.id) & (db.validate_laboratory.project == project.id)
                                & (db.validate_laboratory.carnet.belongs([s.id for s in students]))).select(db.validate_laboratory.carnet, db.validate_laboratory.grade)}

                #GRADE OF STUDENT
                for student in students:
                    #GRADE OF LABORATORY
                    grade_laboratory = 0
                    if student.id not in lab_grades_dict:
                        if student.laboratorio:
                            total_carry_lab = 0.0
                            for category_lab in categories_lab:
                                total_category_lab = 0.0
                                for c_lab in category_lab[1]:
                                    student_grade = db((db.grades.activity == c_lab.id) & (db.grades.academic_assignation == student.id)).select(db.grades.grade).first()
                                    if student_grade is not None:
                                        if category_lab[0].specific_grade:
                                            total_category_lab += float((student_grade.grade * c_lab.grade) / 100)
                                        else:
                                            total_category_lab += float(student_grade.grade)
                                if not category_lab[0].specific_grade:
                                    total_category_lab = float((total_category_lab * float(category_lab[0].grade)) / float(category_lab[2] * 100))
                                total_carry_lab += total_category_lab
                            grade_laboratory = int(round(total_carry_lab, 0))
                    else:
                        grade_laboratory = int(round(lab_grades_dict[student.id].grade, 0))
                    
                    #GRADE OF CLASS
                    total_carry = 0.0
                    total_final = 0.0

                    for category_class in categories_class:
                        total_category = 0.0
                        if category_class[0].category == ID_EXAMEN:
                            for c in category_class[1]:
                                student_grade = db((db.grades.activity == c.id) & (db.grades.academic_assignation == student.id)).select(db.grades.grade).first()
                                if student_grade is not None:
                                    if category_class[0].specific_grade:
                                        total_final += float((student_grade.grade * c.grade) / 100)
                                    else:
                                        total_final += float(student_grade.grade)
                            if not category_class[0].specific_grade:
                                total_final = float((total_final * float(category_class[0].grade)) / float(category_class[2] * 100))
                            total_final = int(round(total_final, 0))
                        elif category_class[0].category == ID_LABORATORIO:
                            grade_laboratory = float((grade_laboratory * float(category_class[0].grade)) / 100)
                        else:
                            for c in category_class[1]:
                                student_grade = db((db.grades.activity == c.id) & (db.grades.academic_assignation == student.id)).select(db.grades.grade).first()
                                if student_grade is not None:
                                    if category_class[0].specific_grade:
                                        total_category += float((student_grade.grade * c.grade) / 100)
                                    else:
                                        total_category += float(student_grade.grade)
                            if not category_class[0].specific_grade:
                                total_category = float((total_category * float(category_class[0].grade)) / float(category_class[2] * 100))
                            total_carry += total_category
                    total_carry += int(round(grade_laboratory, 0)) + int(round(total_final, 0))

                    if total_carry >= 61:
                        infoe_level_temp[2] += 1
                    else:
                        infoe_level_temp[3] += 1
                info_level.append(infoe_level_temp)
        project = name_c

    return dict(group_periods=group_periods, period=period, info_level=info_level, project=project)

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def historic_course_export():
    info_level = []
    period = None
    project = None
    try:
        #CHECK IF THE TYPE OF EXPORT IS VALID
        if request.vars['list_type'] is None or str(request.vars['list_type']) != "csv":
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

        #CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars['level'] is not None and (int(request.vars['level']) < 1 or int(request.vars['level']) > 2):
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

        #CHECK THAT THE AREA EXIST
        area = db(db.area_level.name == 'DTT Tutor Académico').select(db.area_level.id).first()
        if area is None:
            session.flash = T('Report no visible: There are no parameters required to display the report.')
            redirect(URL('default', 'home'))

        #CHECK IF THE PERIOD IS CHANGE
        if request.vars['period'] is None:
            cperiod = cpfecys.current_year_period()
            period = db(db.period_year.id == cperiod.id).select(db.period_year.period, db.period_year.id, db.period_year.yearp).first()
        else:
            period = db(db.period_year.id == int(request.vars['period'])).select(db.period_year.period, db.period_year.id, db.period_year.yearp).first()
            if period is None:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))

        #CHECK PARAMETERS
        if request.vars['level'] == '1' or request.vars['level'] is None:
            group_projects = db((db.project.area_level == area.id) & (db.user_project.period <= period.id) 
                            & ((db.user_project.period + db.user_project.periods) > period.id)).select(
                                db.project.name,
                                db.project.id,
                                join=[db.project.on(db.user_project.project == db.project.id)],
                                orderby=db.project.name,
                                distinct=True
                            )
            if len(group_projects) == 0:
                session.flash = T('Report no visible: There are no parameters required to display the report.')
                redirect(URL('default', 'home'))
        else:
            project = db((db.project.id == int(request.vars['project'])) & (db.project.area_level == area.id)).select().first()
            if project is None:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))
    except:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    #*****************************************************REPORT*****************************************************
    #TITLE
    info_level = []
    info_level.append(['Universidad de San Carlos de Guatemala'])
    info_level.append(['Facultad de Ingeniería'])
    info_level.append(['Escuela de Ingeniería en Ciencias y Sistemas'])

    info_level.append([''])

    #TYPE OF REPORT
    info_level.append(['Tipo', 'Histórico por curso'])

    #DESCRIPTION OF REPORT
    info_level.append(['Descripcion', 'Reporte sobre la información historica de los cursos.'])

    #PERIOD OF REPORT
    info_level.append(['Periodo', f'{period.period.name} {period.yearp}'])

    #ALL SEMESTERS
    if request.vars['level'] == '1' or request.vars['level'] is None:
        #MIDDLE LINE OF REPORT
        info_level.append([''])

        #LABLE DETAIL OF REPORT
        info_level.append(['Detalle'])

        #HEAD OF TABLE
        info_level.append(['Curso', 'Total de alumnos asignados al curso', 'Aprobaron el curso', 'Reprobaron el curso', 'Número de secciones'])
        
        name_courses = []
        #Fill all the courses once time
        for project in group_projects:
            #Get only name
            name_c = get_name(project)
            #Get unique name
            name_c = get_unique_name(name_c)
            #Fill the name of the courses
            exits = True if name_c in name_courses else False

            if not exits:
                name_courses.append(name_c)

        query = db((db.activity_category.category == 'Examen Final') | (db.activity_category.category == 'Laboratorio')).select(db.activity_category.id, orderby=db.activity_category.category)
        ID_EXAMEN = query[0].id
        ID_LABORATORIO = query[1].id

        #FOR COURSE
        for course in name_courses:
            sections = db((db.project.name.like(f'%{course}%')) & (db.user_project.project == db.project.id)
                        & (db.user_project.period == db.period_year.id) & ((db.user_project.period <= period.id)
                        & ((db.user_project.period + db.user_project.periods) > period.id))).select(db.project.name, db.project.id, orderby=db.project.name, distinct=True)
            
            infoe_level_temp = [course, 0, 0, 0, len(sections)]
            for project in sections:
                #Total Students in section
                students = db((db.academic_course_assignation.semester == period.id) & (db.academic_course_assignation.assignation == project.id)).select(
                                db.academic_course_assignation.id,
                                db.academic_course_assignation.laboratorio
                            )
                infoe_level_temp[1] += len(students)

                #LABORATORY
                categories_lab = []
                for categories in db((db.course_activity_category.assignation == project.id) & (db.course_activity_category.semester == period.id)
                                    & (db.course_activity_category.laboratory == True)).select(db.course_activity_category.specific_grade, db.course_activity_category.grade, db.course_activity_category.id):
                    activity_class = []
                    total_a = 0
                    for activity in db(db.course_activity.course_activity_category == categories.id).select(db.course_activity.id, db.course_activity.grade):
                        if db(db.grades.activity == activity.id).select(db.grades.id).first():
                            activity_class.append(activity)
                        total_a += 1
                    if len(activity_class) > 0:
                        categories_lab.append([categories, activity_class, total_a])

                #CLASS
                categories_class = []
                for categories in db((db.course_activity_category.assignation == project.id) & (db.course_activity_category.semester == period.id)
                                    & (db.course_activity_category.laboratory == False)).select(db.course_activity_category.specific_grade, db.course_activity_category.grade, db.course_activity_category.id, db.course_activity_category.category):
                    if categories.category != ID_LABORATORIO:
                        activity_class = []
                        total_a = 0
                        for activity in db(db.course_activity.course_activity_category == categories.id).select(db.course_activity.id, db.course_activity.grade):
                            if db(db.grades.activity == activity.id).select(db.grades.id).first():
                                activity_class.append(activity)
                            total_a += 1
                        if len(activity_class) > 0:
                            categories_class.append([categories, activity_class, total_a])
                    else:
                        categories_class.append([categories, 0])

                #Total of grades
                lab_grades_dict  = {g.carnet: g.grade for g in db((db.validate_laboratory.semester == period.id) & (db.validate_laboratory.project == project.id)
                                    & (db.validate_laboratory.carnet.belongs([s.id for s in students]))).select(db.validate_laboratory.carnet, db.validate_laboratory.grade)}

                #GRADE OF STUDENT
                for student in students:
                    #GRADE OF LABORATORY
                    grade_laboratory = 0
                    if student.id not in lab_grades_dict:
                        if student.laboratorio:
                            total_carry_lab = 0.0
                            for category_lab in categories_lab:
                                total_category_lab = 0.0
                                for c_lab in category_lab[1]:
                                    student_grade = db((db.grades.activity == c_lab.id) & (db.grades.academic_assignation == student.id)).select(db.grades.grade).first()
                                    if student_grade is not None:
                                        if category_lab[0].specific_grade:
                                            total_category_lab += float((student_grade.grade * c_lab.grade) / 100)
                                        else:
                                            total_category_lab += float(student_grade.grade)
                                if not category_lab[0].specific_grade:
                                    total_category_lab = float((total_category_lab * float(category_lab[0].grade)) / float(category_lab[2] * 100))
                                total_carry_lab += total_category_lab
                            grade_laboratory = int(round(total_carry_lab, 0))
                    else:
                        grade_laboratory = int(round(lab_grades_dict[student.id].grade, 0))
                    
                    #GRADE OF CLASS
                    total_carry = 0.0
                    total_final = 0.0
                    for category_class in categories_class:
                        total_category = 0.0
                        if category_class[0].category == ID_EXAMEN:
                            for c in category_class[1]:
                                student_grade = db((db.grades.activity  ==c.id) & (db.grades.academic_assignation == student.id)).select(db.grades.grade).first()
                                if student_grade is not None:
                                    if category_class[0].specific_grade:
                                        total_final += float((student_grade.grade * c.grade) / 100)
                                    else:
                                        total_final += float(student_grade.grade)
                            if not category_class[0].specific_grade:
                                total_final = float((total_final * float(category_class[0].grade)) / float(category_class[2] * 100))
                            total_final = int(round(total_final, 0))
                        elif category_class[0].category == ID_LABORATORIO:
                            grade_laboratory = float((grade_laboratory * float(category_class[0].grade)) / 100)
                        else:
                            for c in category_class[1]:
                                student_grade = db((db.grades.activity == c.id) & (db.grades.academic_assignation == student.id)).select(db.grades.grade).first()
                                if student_grade is not None:
                                    if category_class[0].specific_grade:
                                        total_category += float((student_grade.grade * c.grade) / 100)
                                    else:
                                        total_category += float(student_grade.grade)
                            if not category_class[0].specific_grade:
                                total_category = float((total_category * float(category_class[0].grade)) / float(category_class[2] * 100))
                            total_carry += total_category
                    total_carry += int(round(grade_laboratory, 0)) + int(round(total_final, 0))
                    if total_carry >= 61:
                        infoe_level_temp[2] += 1
                    else:
                        infoe_level_temp[3] += 1
            info_level.append(infoe_level_temp)
    #PROJECT
    elif request.vars['level']=='2':
        name_courses = []

        #Get only name
        name_c = get_name(project)

        #Get unique name
        name_c = get_unique_name(name_c)

        #Fill the name of the courses
        name_courses.append(name_c)

        #HEAD OF TABLE
        #PERIOD OF REPORT
        info_level.append(['Curso', name_c])

        #MIDDLE LINE OF REPORT
        info_level.append([''])
 
        #LABLE DETAIL OF REPORT
        info_level.append(['Detalle'])

        info_level.append(['Sección', 'Total de alumnos asignados al curso', 'Aprobaron el curso', 'Reprobaron el curso'])

        #FOR COURSE
        for course in name_courses:
            sections = db((db.project.name.like(f'%{course}%')) & (db.user_project.project == db.project.id)
                        & (db.user_project.period == db.period_year.id) & ((db.user_project.period <= period.id)
                        & ((db.user_project.period + db.user_project.periods) > period.id))).select(db.project.name, db.project.id, orderby=db.project.name, distinct=True)
            for project in sections:
                infoe_level_temp = [project.name, 0, 0, 0]

                #Total Students in section
                students = db((db.academic_course_assignation.semester == period.id) & (db.academic_course_assignation.assignation == project.id)).select(
                                db.academic_course_assignation.id,
                                db.academic_course_assignation.laboratorio
                            )
                infoe_level_temp[1] += len(students)

                #LABORATORY
                categories_lab = []
                for categories in db((db.course_activity_category.assignation == project.id) & (db.course_activity_category.semester == period.id)
                                    & (db.course_activity_category.laboratory == True)).select(db.course_activity_category.grade, db.course_activity_category.id, db.course_activity_category.specific_grade):
                    activity_class = []
                    total_a = 0
                    for activity in db(db.course_activity.course_activity_category == categories.id).select(db.course_activity.id, db.course_activity.grade):
                        if db(db.grades.activity == activity.id).select(db.grades.id).first():
                            activity_class.append(activity)
                        total_a += 1
                    if len(activity_class) > 0:
                        categories_lab.append([categories, activity_class, total_a])

                #CLASS
                categories_class = []
                for categories in db((db.course_activity_category.assignation == project.id) & (db.course_activity_category.semester == period.id)
                                    & (db.course_activity_category.laboratory == False)).select(db.course_activity_category.category, db.course_activity_category.id, db.course_activity_category.grade, db.course_activity_category.specific_grade):
                    if categories.category != ID_LABORATORIO:
                        activity_class = []
                        total_a = 0
                        for activity in db(db.course_activity.course_activity_category == categories.id).select(db.course_activity.id, db.course_activity.grade):
                            if db(db.grades.activity == activity.id).select(db.grades.id).first():
                                activity_class.append(activity)
                            total_a += 1
                        if len(activity_class) > 0:
                            categories_class.append([categories, activity_class, total_a])
                    else:
                        categories_class.append([categories, 0])

                #Total of grades
                lab_grades_dict  = {g.carnet: g.grade for g in db((db.validate_laboratory.semester == period.id) & (db.validate_laboratory.project == project.id)
                                & (db.validate_laboratory.carnet.belongs([s.id for s in students]))).select(db.validate_laboratory.carnet, db.validate_laboratory.grade)}

                #GRADE OF STUDENT
                for student in students:
                    #GRADE OF LABORATORY
                    grade_laboratory = 0
                    if student.id not in lab_grades_dict:
                        if student.laboratorio:
                            total_carry_lab = 0.0
                            for category_lab in categories_lab:
                                total_category_lab = 0.0
                                for c_Lab in category_lab[1]:
                                    student_grade = db((db.grades.activity == c_Lab.id) & (db.grades.academic_assignation == student.id)).select(db.grades.grade).first()
                                    if student_grade is not None:
                                        if category_lab[0].specific_grade:
                                            total_category_lab += float((student_grade.grade * c_Lab.grade) / 100)
                                        else:
                                            total_category_lab += float(student_grade.grade)
                                if not category_lab[0].specific_grade:
                                    total_category_lab = float((total_category_lab * float(category_lab[0].grade)) / float(category_lab[2] * 100))
                                total_carry_lab += total_category_lab
                            grade_laboratory = int(round(total_carry_lab, 0))
                    else:
                        grade_laboratory = int(round(lab_grades_dict[student.id].grade, 0))
                    
                    #GRADE OF CLASS
                    total_carry = 0.0
                    total_final = 0.0
                    
                    for category_class in categories_class:
                        total_category = 0.0
                        if category_class[0].category == ID_EXAMEN:
                            for c in category_class[1]:
                                student_grade = db((db.grades.activity == c.id) & (db.grades.academic_assignation == student.id)).select(db.grades.grade).first()
                                if student_grade is not None:
                                    if category_class[0].specific_grade:
                                        total_final += float((student_grade.grade * c.grade) / 100)
                                    else:
                                        total_final += float(student_grade.grade)
                            if not category_class[0].specific_grade:
                                total_final = float((total_final * float(category_class[0].grade)) / float(category_class[2] * 100))
                            total_final = int(round(total_final, 0))
                        elif category_class[0].category == ID_LABORATORIO:
                            grade_laboratory = float((grade_laboratory * float(category_class[0].grade)) / 100)
                        else:
                            for c in category_class[1]:
                                student_grade = db((db.grades.activity == c.id) & (db.grades.academic_assignation == student.id)).select(db.grades.grade).first()
                                if student_grade is not None:
                                    if category_class[0].specific_grade:
                                        total_category += float((student_grade.grade * c.grade) / 100)
                                    else:
                                        total_category += float(student_grade.grade)
                            if not category_class[0].specific_grade:
                                total_category = float((total_category * float(category_class[0].grade)) / float(category_class[2] * 100))
                            total_carry += total_category
                    total_carry = int(round(grade_laboratory, 0)) + int(round(total_final, 0))

                    if total_carry >= 61:
                        infoe_level_temp[2] += 1
                    else:
                        infoe_level_temp[3] += 1
                info_level.append(infoe_level_temp)
    
    return dict(csvdata=info_level)

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def percentage_change_grades():
    info_level = []
    group_periods = None
    period = None
    project = None
    roles_c = None
    try:
        #CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars['level'] is not None and (int(request.vars['level']) < 1 or int(request.vars['level']) > 2):
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

        #CHECK THAT THE AREA EXIST
        area = db(db.area_level.name == 'DTT Tutor Académico').select(db.area_level.id).first()
        if area is None:
            session.flash = T('Report no visible: There are no parameters required to display the report.')
            redirect(URL('default', 'home'))

        #CHECK IF THE PERIOD IS CHANGE
        if request.vars['period'] is None:
            cperiod = cpfecys.current_year_period()
            period = db(db.period_year.id == cperiod.id).select(db.period_year.id, db.period_year.yearp, db.period_year.period).first()
        else:
            period = db(db.period_year.id == int(request.vars['period'])).select(db.period_year.id, db.period_year.yearp, db.period_year.period).first()
            if period is None:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))

        #CHECK PARAMETERS
        if request.vars['level'] == '1' or request.vars['level'] is None:
            group_periods = db(db.period_year).select(db.period_year.id, db.period_year.yearp, db.period_year.period, orderby=~db.period_year.id)
            if len(group_periods) == 0:
                session.flash = T('Report no visible: There are no parameters required to display the report.')
                redirect(URL('default', 'home'))

            group_projects = db((db.project.area_level == area.id) & (db.user_project.period <= period.id) 
                            & ((db.user_project.period + db.user_project.periods) > period.id)).select(
                                db.project.name,
                                db.project.id,
                                join=[db.project.on(db.user_project.project == db.project.id)],
                                orderby=db.project.name,
                                distinct=True
                            )

            if len(group_projects) == 0:
                session.flash = T('Report no visible: There are no parameters required to display the report.')
                redirect(URL('default', 'home'))
        else:
            project = db((db.project.id == int(request.vars['project'])) & (db.project.area_level == area.id)).select(db.project.name).first()

            if project is None:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))
    except:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    #*****************************************************REPORT*****************************************************
    #ALL SEMESTERS
    if request.vars['level'] == '1' or request.vars['level'] is None:
        name_courses = []
        #Fill all the courses once time
        for project in group_projects:
            #Get unique name
            name_c = get_unique_name(get_name(project))

            #Fill the name of the courses
            exits = True if name_c in name_courses else False

            if not exits:
                name_courses.append(name_c)

        #TOTAL OF CHANGES
        total_changes = db((db.grades_log.yearp == period.yearp) & (db.grades_log.period == T(period.period.name))
                        & ((db.grades_log.operation_log == 'update') | (db.grades_log.operation_log == 'delete'))).count()
        #FOR COURSE
        for course in name_courses:
            sections = db((db.project.name.like(f'%{course}%')) & (db.user_project.period <= period.id)
                        & ((db.user_project.period + db.user_project.periods) > 18)).select(
                            db.project.id,
                            db.project.name,
                            join=[db.user_project.on(db.user_project.project == db.project.id)],
                            orderby=db.project.name,
                            distinct=True
                        )
            
            infoe_level_temp = [sections.first().id, 0, len(sections)]
            if total_changes > 0:
                temp_calc = db((db.grades_log.yearp == period.yearp) & (db.grades_log.period == T(period.period.name))
                            & (db.grades_log.project.belongs([project.name for project in sections])) & ((db.grades_log.operation_log == 'update')
                            | (db.grades_log.operation_log == 'delete'))).count()
                infoe_level_temp[1] = round(((float(temp_calc) * 100.0) / float(total_changes)), 2)
            info_level.append(infoe_level_temp)
    else:
        #Get only name
        name_c = get_name(project)

        #Get unique name
        name_c = get_unique_name(name_c)

        #FOR COURSE
        roles_c = db(db.grades_log).select(db.grades_log.roll, distinct=True)
        
        sections = db((db.project.name.like(f'%{name_c}%')) & (db.user_project.project == db.project.id)
                    & (db.user_project.period == db.period_year.id) & ((db.user_project.period <= period.id)
                    & ((db.user_project.period + db.user_project.periods) > period.id))).select(db.project.name, orderby=db.project.name, distinct=True)
        
        total_changes = db((db.grades_log.yearp == period.yearp) & (db.grades_log.period == T(period.period.name))
                        & (db.grades_log.project.belongs([section.name for section in sections])) & ((db.grades_log.operation_log == 'update')
                        | (db.grades_log.operation_log == 'delete'))).count()

        for section in sections:
            infoe_level_temp = [section.name]
            for rc in roles_c: infoe_level_temp.append(0)
            if total_changes > 0:
                position = 1
                for rc in roles_c:
                    infoe_level_temp[position] += db((db.grades_log.yearp == period.yearp) & (db.grades_log.period == T(period.period.name))
                                                & (db.grades_log.project == section.name) & (db.grades_log.roll == rc.roll)
                                                & ((db.grades_log.operation_log == 'update') | (db.grades_log.operation_log == 'delete'))).count()
                    infoe_level_temp[position] = round(((float(infoe_level_temp[position]) * 100.0) / float(total_changes)), 2)
                    position += 1
            info_level.append(infoe_level_temp)
        project = name_c

    return dict(group_periods=group_periods, period=period, info_level=info_level, project=project, roles_c=roles_c)

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def percentage_change_grades_export():
    info_level = []
    period = None
    project = None

    try:
        #CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars['level'] is not None and (int(request.vars['level']) < 1 or int(request.vars['level']) > 2):
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

        #CHECK THAT THE AREA EXIST
        area = db(db.area_level.name == 'DTT Tutor Académico').select(db.area_level.id).first()
        if area is None:
            session.flash = T('Report no visible: There are no parameters required to display the report.')
            redirect(URL('default', 'home'))

        #CHECK IF THE PERIOD IS CHANGE
        if request.vars['period'] is None:
            cperiod = cpfecys.current_year_period()
            period = db(db.period_year.id == cperiod.id).select(db.period_year.id, db.period_year.yearp, db.period_year.period).first()
        else:
            period = db(db.period_year.id == int(request.vars['period'])).select(db.period_year.id, db.period_year.yearp, db.period_year.period).first()
            if period is None:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))

        #CHECK PARAMETERS
        if request.vars['level'] == '1' or request.vars['level'] is None:
            group_projects = db((db.project.area_level == area.id) & (db.user_project.period <= period.id) 
                            & ((db.user_project.period + db.user_project.periods) > period.id)).select(
                                db.project.name,
                                db.project.id,
                                join=[db.project.on(db.user_project.project == db.project.id)],
                                orderby=db.project.name,
                                distinct=True
                            )
            if len(group_projects) == 0:
                session.flash = T('Report no visible: There are no parameters required to display the report.')
                redirect(URL('default', 'home'))
        else:
            project = db((db.project.id == int(request.vars['project'])) & (db.project.area_level == area.id)).select(db.project.name).first()
            if project is None:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))
    except:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    #*****************************************************REPORT*****************************************************
    #TITLE
    info_level = []
    info_level.append(['Universidad de San Carlos de Guatemala'])
    info_level.append(['Facultad de Ingeniería'])
    info_level.append(['Escuela de Ingeniería en Ciencias y Sistemas'])

    info_level.append([''])

    #TYPE OF REPORT
    info_level.append(['Tipo', 'Porcentaje de cambio de notas'])

    #DESCRIPTION OF REPORT
    info_level.append(['Descripción', 'Reporte sobre el porcentaje de cambio de notas que han realizado los distintos roles dentro los cursos.'])

    #PERIOD OF REPORT
    info_level.append(['Periodo', f'{T(period.period.name)} {period.yearp}'])

    #ALL SEMESTERS
    if request.vars['level'] == '1' or request.vars['level'] is None:
        #MIDDLE LINE OF REPORT
        info_level.append([''])

        #LABLE DETAIL OF REPORT
        info_level.append(['Detalle'])

        #HEADER
        info_level.append(['Curso', 'Porcentaje de cambio', 'Número de secciones'])

        name_courses = []
        #Fill all the courses once time
        for project in group_projects:
            #Get only name
            name_c = get_name(project)

            #Get unique name
            name_c = get_unique_name(name_c)

            #Fill the name of the courses
            exits = True if name_c in name_courses else False

            if not exits:
                name_courses.append(name_c)
        
        #TOTAL OF CHANGES
        total_changes = db((db.grades_log.yearp == period.yearp) & (db.grades_log.period == T(period.period.name))
                        & ((db.grades_log.operation_log == 'update') | (db.grades_log.operation_log == 'delete'))).count()
        
        #FOR COURSE
        for course in name_courses:
            sections = db((db.project.name.like(f'%{course}%')) & (db.user_project.project == db.project.id)
                        & (db.user_project.period == db.period_year.id) & ((db.user_project.period <= period.id)
                        & ((db.user_project.period + db.user_project.periods) > period.id))).select(db.project.id, db.project.name, orderby=db.project.name, distinct=True)
            
            info_level_temp = [course, 0, len(sections)]
            if total_changes > 0:
                info_level_temp[1] += db((db.grades_log.yearp == period.yearp) & (db.grades_log.period == T(period.period.name))
                                        & (db.grades_log.project.belongs([project.name for project in sections])) & ((db.grades_log.operation_log == 'update')
                                        | (db.grades_log.operation_log == 'delete'))).count()
                info_level_temp[1] = round(((float(info_level_temp[1]) * float(100)) / float(total_changes)), 2)
            info_level.append(info_level_temp)
    else:
        #Get only name
        name_c = get_name(project)

        #Get unique name
        name_c = get_unique_name(name_c)

        #FOR COURSE
        roles_c = db(db.grades_log).select(db.grades_log.roll, distinct=True)
        
        #PROJECT OF REPORT
        info_level.append(['Curso', name_c])

        #MIDDLE LINE OF REPORT
        info_level.append([''])

        #LABLE DETAIL OF REPORT
        info_level.append(['Detalle'])

        name_courses = []
        #HEADER
        info_level_temp = []
        info_level_temp.append('Sección')
        for rc in roles_c:
            info_level_temp.append(f'Porcentaje de cambio {T(f"Rol {rc.roll}")}')
        info_level.append(info_level_temp)
 
        sections = db((db.project.name.like(f'%{name_c}%')) & (db.user_project.project == db.project.id)
                    & (db.user_project.period == db.period_year.id) & ((db.user_project.period <= period.id)
                    & ((db.user_project.period + db.user_project.periods) > period.id))).select(db.project.name, orderby=db.project.name, distinct=True)
        
        total_changes = db((db.grades_log.yearp == period.yearp) & (db.grades_log.period == T(period.period.name))
                        & (db.grades_log.project.belongs([section.name for section in sections])) & ((db.grades_log.operation_log == 'update')
                        | (db.grades_log.operation_log == 'delete'))).count()
        
        for section in sections:
            info_level_temp = []
            info_level_temp.append(section.name)
            for rc in roles_c: info_level_temp.append(0)
            if total_changes > 0:
                position = 1
                for rc in roles_c:
                    info_level_temp[position] += db((db.grades_log.yearp == period.yearp) & (db.grades_log.period == T(period.period.name))
                                                & (db.grades_log.project == section.name) & (db.grades_log.roll == rc.roll)
                                                & ((db.grades_log.operation_log == 'update') | (db.grades_log.operation_log == 'delete'))).count()
                    info_level_temp[position] = round(((float(info_level_temp[position]) * float(100)) / float(total_changes)), 2)
                    position += 1
            info_level.append(info_level_temp)

    return dict(csvdata=info_level)

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def get_assignations(project, period, role):
    return db((db.auth_user.id == db.user_project.assigned_user) & (db.auth_user.id == db.auth_membership.user_id)
            & (db.auth_membership.group_id == db.auth_group.id) & (db.auth_group.role == role)
            & (project == False or (db.user_project.project == project)) & (db.project.area_level == db.area_level.id)
            & (db.user_project.project == db.project.id) & (db.user_project.period == db.period_year.id)
            & ((db.user_project.period <= period.id) & ((db.user_project.period + db.user_project.periods) > period.id)))

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def get_name(project):
    try:
        (name_p, _) = str(project.name).split('(')
    except:
        name_p = project.name

    white_space = 0
    for letter in reversed(range(len(name_p))):
        if name_p[letter] == ' ':
            white_space += 1
        else:
            break

    name_c = None
    for letter in range(len(name_p) - white_space):
        if name_c is None:
            name_c = name_p[letter]
        else:
            name_c += name_p[letter]

    return name_c

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def get_unique_name(project):
    name_c = db(db.project.name.like(f'%{project}%')).select().first()[db.project.name]
    try:
        (name_p, _) = str(name_c).split('(')
    except:
        name_p = name_c
    
    white_space = 0
    for letter in reversed(range(len(name_p))):
        if name_p[letter] == ' ':
            white_space += 1
        else:
            break

    name_c = None
    for letter in range(len(name_p) - white_space):
        if name_c is None:
            name_c = name_p[letter]
        else:
            name_c += name_p[letter]
    
    return name_c
