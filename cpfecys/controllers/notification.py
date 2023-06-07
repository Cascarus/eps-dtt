from queries import q_notification_calculation
import cpfecys

# *********** EPS DANIEL COS ************
@auth.requires_login()
def get_notification_number():
    username = request.post_vars.array
    key = redis_db_1.keys(pattern=username)

    if len(key) <= 0: notification_calculation(username)

    return redis_db_1.get(str(username))

@auth.requires_login()
def notification_calculation(username):
    conteo = 0
  
    user = db((db.auth_user.username == username)).select(db.auth_user.id, db.auth_user.username).first()

    nconteo_1 = db.executesql(q_notification_calculation(1).format(user.id, user.username))
    nconteo_2 = db.executesql(q_notification_calculation(2).format(user.id, user.username))
    conteo += int(nconteo_1[0][0]) + int(nconteo_2[0][0])
    
    redis_db_1.set(user.username, conteo)
# *********** FIN EPS DANIEL COS ********

#***************************************************************
#*******************NOTIFICATIONS OF STUDENT********************
#***************************************************************
#***************************************************************
#*******************REGISTER OF NOTIFICATIONS*******************
#***************************************************************
@auth.requires_login()
@auth.requires_membership('Student')
def register_mail_notifications():
    #Obtain the current period of the system and all the register periods
    period = cpfecys.current_year_period()
    periods_temp = db(db.period_year).select(db.period_year.id, db.period_year.period, db.period_year.yearp)
    periods = []
    for period_temp in periods_temp:
        if auth.has_membership('Student'):
            try:
                if db((db.user_project.assigned_user == auth.user.id) & ((db.user_project.period <= period_temp.id) 
                & ((db.user_project.period + db.user_project.periods) > period_temp.id))).select(db.user_project.id).first() is not None:
                    periods.append(period_temp)
            except:
                None

    #Check if the period is change
    if request.vars['period'] != None:
        period = request.vars['period']
        period = db(db.period_year.id == period).select().first()

    #show the page resiter_mail_notifications.html
    response.view = 'notification/register_mail_notifications.html'

    #obtain the projects where the student is register and is of the select semester
    projects = db(((db.user_project.period <= period) & ((db.user_project.period + db.user_project.periods) > period)) 
                & (db.user_project.assigned_user == auth.user.id)).select(db.user_project.project, db.user_project.id)

    return dict(periods=periods, projects=projects)

#obtain all the registers of the send notices of the student
def teacher_register_mail():
    notices = None
    tipo_d = 0
    period = db(db.period_year.id == request.vars["period"]).select(db.period_year.period, db.period_year.yearp).first()
    
    if request.vars['userN'] != None and request.vars['project'] != None:
        tipo_d = 1
        usuario = db(db.auth_user.id == request.vars['userN']).select(db.auth_user.username).first()
        project = request.vars['project']
        userproject = db(db.user_project.id == project).select(db.user_project.project).first()

        notices = db((db.notification_general_log4.emisor == usuario.username) & (db.notification_general_log4.course == userproject.project.name)
                & (db.notification_general_log4.period == period.period.name) & (db.notification_general_log4.yearp == period.yearp)).select(
                    db.notification_general_log4.id, db.notification_general_log4.subject, db.notification_general_log4.sent_message,
                    db.notification_general_log4.time_date
                )
    else:
        if request.vars['project']!=None:
            tipo_d = 2
            project = request.vars['project']
            userproject = db(db.user_project.id == project).select(db.user_project.project).first()
            notices = db((db.notification_general_log4.emisor == auth.user.username) & (db.notification_general_log4.course == userproject.project.name)
                    & (db.notification_general_log4.period == period.period.name) & (db.notification_general_log4.yearp == period.yearp)).select(
                        db.notification_general_log4.id, db.notification_general_log4.subject, db.notification_general_log4.sent_message,
                        db.notification_general_log4.time_date
                    )
            
    return dict(notices=notices, tipo_d=tipo_d)

def teacher_register_mail_detail():
    if request.vars['notice'] != None:
        noticia = db(db.notification_general_log4.id == request.vars['notice']).select(db.notification_general_log4.subject, db.notification_general_log4.sent_message, 
                db.notification_general_log4.time_date).first()

        listado_c = db(db.notification_log4.register == request.vars['notice']).select(db.notification_log4.username, db.notification_log4.destination, db.notification_log4.success,
                    db.notification_log4.result_log, db.notification_log4.register)
        
    return dict(noticia=noticia,listado_c=listado_c, log=listado_c.first())

@auth.requires_login()
@auth.requires_membership('Student')
def mail_notifications():
    #Obtener la asignacion del estudiante
    assignation = request.vars['assignation']
    
    #Obtener el periodo
    year = db(db.period_year.id == request.vars["period"]).select(db.period_year.id, db.period_year.yearp, db.period_year.period).first()
    year_semester = db(db.period.id == year.period).select(db.period.name).first()
    period = year.id
    
    #Obtener al tutor del proyecto
    check = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.id == assignation)
            & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
    
    fail_check = True
    if check is None: fail_check = False
    elif cpfecys.assignation_is_locked(check): fail_check = False

    if not fail_check:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    var = ""
    if request.args(0) == 'send':
        #Tipo estudiante al que se le enviara el correo
        tipoes = request.vars['tipoe']
        #Obtener listado alumnos a enviar mensaje
        listado = request.vars['listado']
        listado2 = request.vars['listado2']
        
        #Mensaje que se enviara
        message = request.vars['message']
        
        #Asunto del mensaje que se enviara
        subject = request.vars['subject']
        #Check that the user select only one group of students
        if not tipoes or count_select_items(tipoes) != 1:
            session.flash = T('You must select only one group of students')
            redirect(URL('notification', 'mail_notifications', vars=dict(period=year.id, assignation=check.id)))
            return
        
        #Obtener la lista de destinatarios en base a los usuarios presionados
        if ((tipoes == 'specific' and (listado != None or listado2 != None)) or (tipoes != 'specific')) and message != '' and subject != '':
            (user1, user2) = validate_users_for_mail(3, period, check, tipoes)
            if user1 != None or user2 != None:
                #Realizar el envio de mensajes
                fail = teacher_send_mail_to_students(user1, user2, message, subject, check, year_semester.name, year.yearp)
                if fail > 0:
                    session.flash = T(f'Avisos enviados - Existen {str(fail)} avisos fallidos, revise el registro de avisos')
                else:
                    session.flash = T('Notices Sent')
                redirect(URL('notification', 'mail_notifications', vars=dict(period=year.id, assignation=check.id)))
            else: session.flash = T('No recipient who sent the message')
            redirect(URL('notification', 'mail_notifications', vars=dict(period=year.id, assignation=check.id)))
        else:
            session.flash = T('Fill all fields of notification')
            redirect(URL('notification', 'mail_notifications',vars=dict(period=year.id, assignation=check.id)))

    def get_projects(grupo):
        #Obtener la asignacion del estudiante
        assignation = request.vars['assignation']

        #Obtener al tutor
        check = db((db.user_project.id == assignation) & (db.user_project.assigned_user == auth.user.id)).select(db.user_project.id, db.user_project.project, 
                                                                                                                db.user_project.assigned_user).first()
        if grupo == 1:       
            if check is None:
                #check if there is no assignation or if it is locked (shouldn't be touched)
                if session.last_assignation is None:
                    redirect(URL('default', 'home'))
                    return
                else:
                    check = db.user_project(id = session.last_assignation)
                    if cpfecys.assignation_is_locked(check):
                        redirect(URL('default', 'home'))
                        return
            else:
                session.last_assignation = check.id

            #Obtener los estudiantes del tutor y asignados al proyecto
            students = db((db.academic_course_assignation.semester == period) & (db.academic_course_assignation.assignation == check.project) 
                        & (db.academic_course_assignation.laboratorio == 'True')).select()
            return students
        elif grupo == 3:
            #obtain the final practice students assigned in the course where the user is the manager
            students = db((db.user_project.project == check.project) & ((db.user_project.period <= period) 
                        & ((db.user_project.period + db.user_project.periods) > period)) & (db.user_project.assigned_user != check.assigned_user)
                        & (db.auth_membership.user_id == db.user_project.assigned_user) & (db.auth_membership.group_id == 3)).select()
            return students
        else:                
            #Obtener la asignacion del estudiante
            assignation = request.vars['assignation']
            #Obtener al tutor
            check = db((db.user_project.id == assignation) & (db.user_project.assigned_user == auth.user.id)).select(db.user_project.project, db.user_project.id).first()

            if check is None:
                #check if there is no assignation or if it is locked (shouldn't be touched)
                if session.last_assignation is None:
                    redirect(URL('default', 'home'))
                    return
                else:
                    check = db(db.user_project.id == session.last_assignation).select(db.user_project.assignation_status).first()
                    if cpfecys.assignation_is_locked(check):
                        redirect(URL('default', 'home'))
                        return
            else:
                session.last_assignation = check.id
            #Obtener los estudiantes del tutor y asignados al proyecto
            students = db((db.academic_course_assignation.semester == period) & (db.academic_course_assignation.assignation == check.project)
                        & (db.academic_course_assignation.laboratorio == 'False')).select()
            return students

    #db.library.period.default = check.project
    db.library.period.writable = False
    db.library.period.readable = False

    #db.library.project.default = check.project
    db.library.project.writable = False
    db.library.project.readable = False

    #db.library.owner_file.default = check.project
    db.library.owner_file.writable = False
    db.library.owner_file.readable = False

    if session.notification_subject == None: session.notification_subject = ''
    if session.notification_message == None: session.notification_message = ''  
    if session.cc == None: session.cc = ''  

    upload_form = FORM(
                        INPUT(_name='file_name', _type='text'),
                        INPUT(_name='file_upload', _type='file', requires=[
                            IS_UPLOAD_FILENAME(extension='(pdf|rar|zip)', error_message='Solo se aceptan archivos con extension zip|pdf|rar'),
                            IS_LENGTH(2097152, error_message='El tamaño máximo del archivo es 2MB')
                        ]),
                        INPUT(_name='file_description',_type='text'),
                        INPUT(_name='file_visible',_type='checkbox')
                    )

    if upload_form.accepts(request.vars, formname='upload_form'):
        try:
            if (upload_form.vars.file_name is "") or (upload_form.vars.file_upload is "") or (upload_form.vars.file_description is ""):
                response.flash = T('You must enter all fields.')
            else:
                exists = db((db.library.name == upload_form.vars.file_name) & (db.library.project == check.project.id) 
                        & (db.library.owner_file == auth.user.id)).select(db.library.id).first()
                if exists is None:                    
                    file_var = db.library.file_data.store(upload_form.vars.file_upload.file, upload_form.vars.file_upload.filename)
                    
                    var_visible = 'True' if upload_form.vars.file_visible else 'False'

                    id = db.library.insert(
                        file_data=file_var,
                        name=upload_form.vars.file_name,
                        description=upload_form.vars.file_description,
                        visible=var_visible,
                        period=cpfecys.current_year_period(),
                        project=check.project.id,
                        owner_file=auth.user.id
                    )

                    session.attachment_list.append(db(db.library.id == id).select())
                    response.flash = T('File loaded successfully.')
                else:
                    response.flash = T('File already exists.')
        except:
            response.flash = T('Error loading file.')

    attach_form = FORM()
    if attach_form.accepts(request.vars, formname='attach_form'):
        if session.attachment_list_temp != None:
            for var in session.attachment_list_temp:
                session.attachment_list.append(var)
                session.attachment_list_temp = []
        else: session.attachment_list_temp = []        
    
    remove_form = FORM()
    if remove_form.accepts(request.vars, formname='remove_form'):
        list_tempo = []
        if session.attachment_list_temp2 != None and len(session.attachment_list_temp2) > 0:
            for var_list in session.attachment_list:                
                for tempo1 in var_list:                    
                    cambiar = False
                    for var_list_2 in session.attachment_list_temp2:
                        for tempo2 in var_list_2:
                            if tempo1.id == tempo2.id:
                                cambiar = True

                if not cambiar: list_tempo.append(var_list)

            session.attachment_list = list_tempo
            session.attachment_list_temp2 = []
        else: session.attachment_list_temp2 = []

    session.project_id = check.project.id

    return dict(
        get_projects=get_projects,
        markmin_settings = cpfecys.get_markmin,
        name = check.project.name,
        semester = year_semester.name,
        year = year.yearp,
        assignation=assignation,
        attachment_list=session.attachment_list
    )

def validate_users_for_mail(rol, period, check, tipoes):
    users1 = None
    users2 = None
    count1 = db.academic_course_assignation.id.count()
    count2 = db.auth_user.id.count()
    user1 = None
    user2 = None
    totalC1 = 0
    totalC2 = 0
    aux_laboratorio = ''
    if tipoes == 'cl': aux_laboratorio = 'True'
    elif tipoes == 'sl': aux_laboratorio = 'False'
    
    users2_query = ((db.auth_user.id == db.user_project.assigned_user) & ((db.user_project.period <= period)
                & ((db.user_project.period + db.user_project.periods) > period)) & (db.user_project.project == check.project)
                & (db.auth_membership.user_id == db.user_project.assigned_user) & (db.auth_membership.group_id == rol))
    users1_query = ((db.academic.id == db.academic_course_assignation.carnet) & (db.academic_course_assignation.semester == period) 
                    & (db.academic_course_assignation.assignation == check.project) & (db.academic_course_assignation.laboratorio == aux_laboratorio))

    if tipoes == 'all' or tipoes == 'cl' or tipoes == 'sl' or tipoes == 'fp':
        if tipoes == 'cl' or tipoes == 'sl':
            users1 = db(users1_query).select(count1)
            totalC1 = count_items(users1, count1)
        elif tipoes =='fp':
            users2 = db(users2_query).select(count2)
            totalC2 = count_items(users2, count2)
        else:
            users1 = db((db.academic.id == db.academic_course_assignation.carnet) & (db.academic_course_assignation.semester == period) 
                    & (db.academic_course_assignation.assignation == check.project)).select(count1)
            users2 = db(users2_query).select(count2)
            totalC1 = count_items(users1, count1)
            totalC2 = count_items(users2, count2)
        if tipoes == 'all' and (totalC1 > 0 or totalC2 > 0):
            if totalC1 > 0:
                user1 = []
                users1 = db((db.academic.id == db.academic_course_assignation.carnet) & (db.academic_course_assignation.semester == period) 
                        & (db.academic_course_assignation.assignation == check.project)).select()
                for user in users1: user1.append(user.academic)
            if totalC2 > 0:
                user2 = []
                users2 = db(users2_query).select()
                for user in users2: user2.append(user.auth_user)
        elif (tipoes == 'cl' or tipoes == 'sl') and totalC1 > 0:
            user1 = []
            users1 = db(users1_query).select()
            for user in users1: user1.append(user.academic)
        elif tipoes == 'fp' and totalC2 > 0:
            user2 = []
            users2 = db(users2_query).select()
            for user in users2: user2.append(user.auth_user)
    else:
        #Obtain the list of destination for the students
        if listado != None:
            dest = []
            students = request.vars['listado']
            try:
                students.append(-1)
                students.remove(-1)
                for student in students: dest.append(student)
                
                #consultar a la base de datos para obtener a los usuarios a los que enviaremos
                user1 = db(db.academic.id.belongs(dest)).select()
            except:
                #consultar a la base de datos para obtener a los usuarios a los que enviaremos
                user1 = db(db.academic.id == request.vars['listado']).select()
        
        #obtain the list of destination for the final practices students
        if listado2 != None:
            dest = []
            students = request.vars['listado2']
            try:
                students.append(-1)
                students.remove(-1)
                for student in students: dest.append(student)
                
                #consultar a la base de datos para obtener a los usuarios a los que enviaremos
                user2 = db(db.auth_user.id.belongs(dest)).select()
            except:
                #consultar a la base de datos para obtener a los usuarios a los que enviaremos
                user2 = db(db.auth_user.id == request.vars['listado2']).select()
    
    return (user1, user2)

#***************************************************************
#*******************NOTIFICATIONS OF STUDENT********************
#***************************************************************
#***************************************************************
#*******************REGISTER OF NOTIFICATIONS*******************
#***************************************************************
@auth.requires_login()
@auth.requires_membership('Teacher')
def teacher_register_mail_notifications():
    #Obtain the current period of the system and all the register periods
    period = cpfecys.current_year_period()

    periods_temp = db(db.period_year).select(db.period_year.id,  db.period_year.yearp, db.period_year.period)
    periods = []
    for period_temp in periods_temp:
        if auth.has_membership('Student') or auth.has_membership('Teacher'):
            try:
                if db((db.user_project.assigned_user == auth.user.id) & ((db.user_project.period <= period_temp.id) 
                & ((db.user_project.period + db.user_project.periods) > period_temp.id))).select(db.user_project.id).first() is not None:
                    periods.append(period_temp)
            except:
                None
        
    #Check if the period is change
    if request.vars['period'] != None:
        period = request.vars['period']
        period = db(db.period_year.id == period).select().first()

    #show the page resiter_mail_notifications.html
    response.view = 'notification/teacher_register_mail_notifications.html'

    #obtain the projects where the student is register and is of the select semester
    projects = db(((db.user_project.period <= period) & ((db.user_project.period + db.user_project.periods) > period)) 
                & (db.user_project.assigned_user == auth.user.id)).select(db.user_project.project, db.user_project.id, db.user_project.period)

    def obtain_persons(project):
        persons = db((db.user_project.assigned_user != auth.user.id) &(db.user_project.project == project.project)
                & (((db.user_project.period <= project.period) & ((db.user_project.period + db.user_project.periods) > project.period))
                & (db.auth_membership.user_id == db.user_project.assigned_user) & (db.auth_membership.group_id == 2))).select(db.user_project.assigned_user, db.user_project.id)
        return persons

    return dict(
        obtain_persons=obtain_persons,
        periods=periods,
        projects=projects,
    )

def teacher_search_destination():
    mail_var = []
    if request.vars['notice'] != None:
        if request.vars['search_input'] != None:
            mail_var = db((db.notification_log4.register == request.vars['notice']) & (db.notification_log4.username.like('%' + request.vars['search_input'] + '%'))).select(
                db.notification_log4.destination, db.notification_log4.username
            )
        else:
            mail_var = db(db.notification_log4.register == request.vars['notice']).select(db.notification_log4.destination, db.notification_log4.username)
    
    return dict(all_n=mail_var)

@auth.requires_login()
@auth.requires_membership('Teacher')
def teacher_mail_notifications():
    #Obtener la asignacion del estudiante
    assignation = request.vars['assignation']
    
    #Obtener el periodo
    year = db(db.period_year.id == request.vars["period"]).select(db.period_year.period, db.period_year.id, db.period_year.yearp).first()
    year_semester = db(db.period.id == year.period).select(db.period.name).first()
    period = year.id

    #Obtener al tutor del proyecto
    check = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.id == assignation)
            & ((db.user_project.period <= year.id) & ((db.user_project.period + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()

    fail_check = True
    if (check is None): fail_check = False
    elif cpfecys.assignation_is_locked(check): fail_check = False

    if not fail_check:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    var = ""
    if (request.args(0) == 'send'):
        #Tipo estudiante al que se le enviara el correo
        tipoes = request.vars['tipoe']

        #Obtener listado alumnos a enviar mensaje
        listado = request.vars['listado']
        listado2 = request.vars['listado2']

        #Mensaje que se enviara
        message = request.vars['message']

        #Asunto del mensaje que se enviara
        subject = request.vars['subject']

        #Destinatarios extra, estos pueden ser solo uno o separado por ;
        cc = ""

        #Check that the user select only one group of students
        if not tipoes or count_select_items(tipoes) != 1:
            session.flash = T('You must select only one group of students')
            redirect(URL('notification', 'teacher_mail_notifications', vars=dict(period=year.id, assignation=check.id)))
            return
        
        #Obtener la lista de destinatarios en base a los usuarios presionados
        if ((tipoes == 'specific' and (listado != None or listado2 != None)) or (tipoes != 'specific')) and message != '' and subject != '':
            print("\e[40;antes")
            (user1, user2) = validate_users_for_mail(2, period, check, tipoes)
            print("\e[40;despues")
            if user1 != None or user2 != None:
                #Realizar el envio de mensajes
                fail = teacher_send_mail_to_students(user1, user2, message, subject, check, year_semester.name, year.yearp, cc)
                if fail > 0:
                    session.flash = T(f'Avisos enviados - Existen {str(fail)} avisos fallidos, revise el registro de avisos')
                else:
                    session.flash = T('Notices Sent')
                redirect(URL('notification', 'teacher_mail_notifications', vars=dict(period=year.id, assignation=check.id)))
            else:
                session.flash = T('No recipient who sent the message')
            redirect(URL('notification', 'teacher_mail_notifications', vars=dict(period=year.id, assignation=check.id)))
        else:
            session.flash = T('Fill all fields of notification')
            redirect(URL('notification', 'teacher_mail_notifications', vars=dict(period=year.id, assignation=check.id)))

    def get_projects(grupo):
        #Obtener la asignacion del estudiante
        assignation = request.vars['assignation']
        #Obtener al tutor
        check = db.user_project(id = assignation, assigned_user = auth.user.id)
        if check is None:
            #check if there is no assignation or if it is locked (shouldn't be touched)
            if session.last_assignation is None:
                redirect(URL('default', 'home'))
                return
            else:
                check = db.user_project(id = session.last_assignation)
                if cpfecys.assignation_is_locked(check):
                    redirect(URL('default', 'home'))
                    return
        else:
            session.last_assignation = check.id

        if grupo == 1:
            #Obtener los estudiantes del tutor y asignados al proyecto
            students = db((db.academic_course_assignation.semester == period) & (db.academic_course_assignation.assignation == check.project)
                    & (db.academic_course_assignation.laboratorio == 'True')).select(db.academic_course_assignation.carnet)
            return students
        elif grupo == 2:
            #Obtener los estudiantes del tutor y asignados al proyecto
            students = db((db.academic_course_assignation.semester == period) & (db.academic_course_assignation.assignation == check.project)
                    & (db.academic_course_assignation.laboratorio == 'False')).select(db.academic_course_assignation.carnet)
            return students
        else:
            #obtain the final practice students assigned in the course where the user is the manager
            students = db((db.user_project.project == check.project) & ((db.user_project.period <= period) 
                    & ((db.user_project.period + db.user_project.periods) > period)) & (db.user_project.assigned_user != check.assigned_user)
                    & (db.auth_membership.user_id == db.user_project.assigned_user) & (db.auth_membership.group_id == 2)).select()
            return students

    if session.notification_subject == None: session.notification_subject = ''
    if session.notification_message == None: session.notification_message = '' 
    if session.cc == None: session.cc = ''    

    upload_form = FORM(
                    INPUT(_name='file_name', _type='text'),
                        INPUT(_name='file_upload', _type='file', requires=[
                            IS_UPLOAD_FILENAME(extension='(pdf|rar|zip)', error_message='Solo se aceptan archivos con extension zip|pdf|rar'),
                            IS_LENGTH(2097152, error_message='El tamaño máximo del archivo es 2MB')
                        ]),
                        INPUT(_name='file_description', _type='text'),
                        INPUT(_name='file_visible', _type='checkbox')
                    )
    if upload_form.accepts(request.vars, formname='upload_form'):
        try:
            if (upload_form.vars.file_name is "" ) or (upload_form.vars.file_upload is "") or (upload_form.vars.file_description is ""):
                response.flash = T('You must enter all fields.')
            else:
                exists = db((db.library.name == upload_form.vars.file_name) & (db.library.project == check.project.id) 
                        & (db.library.owner_file == auth.user.id)).select(db.library.id).first()
                if exists is None:                    
                    file_var = db.library.file_data.store(upload_form.vars.file_upload.file, upload_form.vars.file_upload.filename)
                    
                    var_visible = 'True' if upload_form.vars.file_visible else 'False'
                    id = db.library.insert(
                        file_data=file_var,
                        name=upload_form.vars.file_name,
                        description=upload_form.vars.file_description,
                        visible=var_visible,
                        period=cpfecys.current_year_period(),
                        project=check.project.id,
                        owner_file=auth.user.id
                    )

                    session.attachment_list.append(db(db.library.id == id).select())
                    response.flash = T('File loaded successfully.')
                else:
                    response.flash = T('File already exists.')
        except:
            response.flash = T('Error loading file.')

    attach_form = FORM()
    if attach_form.accepts(request.vars, formname='attach_form'):
        if session.attachment_list_temp != None:
            for var in session.attachment_list_temp:
                session.attachment_list.append(var)
                session.attachment_list_temp = []
        else: session.attachment_list_temp = []        
    
    remove_form = FORM()
    if remove_form.accepts(request.vars, formname='remove_form'):
        list_tempo = []
        if session.attachment_list_temp2 != None and len(session.attachment_list_temp2) > 0:
            for var_list in session.attachment_list:                
                for tempo1 in var_list:                    
                    cambiar = False
                    for var_list_2 in session.attachment_list_temp2:
                        for tempo2 in var_list_2:
                            if (tempo1.id == tempo2.id):
                                cambiar = True

                if not cambiar:
                    list_tempo.append(var_list)

            session.attachment_list = list_tempo
            session.attachment_list_temp2 = []
        else: session.attachment_list_temp2 = []

    session.project_id = check.project.id
    return dict(
        get_projects=get_projects,
        markmin_settings = cpfecys.get_markmin,
        name = check.project.name,
        semester = year_semester.name,
        year = year.yearp,
        assignation=assignation,
        attachment_list=session.attachment_list
    )

@auth.requires_login()
def register_mail_detail():
    if request.vars['notice'] != None:
        notice = db(db.notification_general_log4.id == request.vars['notice']).select(db.notification_general_log4.subject, db.notification_general_log4.sent_message,
                                                                                      db.notification_general_log4.time_date).first()
        listado_c = db(db.notification_log4.register == request.vars['notice']).select(db.notification_log4.success, db.notification_log4.result_log, db.notification_log4.register,
                                                                                       db.notification_log4.username, db.notification_log4.destination)
        
    return dict(notice=notice, listado_c=listado_c, log=listado_c.first())

#obtain all the registers of the send notices of the student
@auth.requires_login()
def register_mail():
    notices = None    
    if request.vars['project'] != None:
        project = request.vars['project']
        period = db(db.period_year.id == request.vars['period']).select(db.period_year.yearp, db.period_year.period).first()
        userproject = db(db.user_project.id == project).select(db.user_project.project).first()

        notices = db((db.notification_general_log4.emisor == auth.user.username) & (db.notification_general_log4.course == userproject.project.name)
                & (db.notification_general_log4.period == period.period.name) & (db.notification_general_log4.yearp == period.yearp)).select(db.notification_general_log4.id,
                db.notification_general_log4.subject, db.notification_general_log4.sent_message, db.notification_general_log4.time_date)
    
    return dict(notices=notices)

@auth.requires_login()
def search_destination():
    if request.vars['notice'] != None:
        if request.vars['search_input'] != None:
            username_like = f"%{request.vars['search_input']}%"
            mail_var = db((db.notification_log4.register == request.vars['notice']) & (db.notification_log4.username.like(username_like))).select(
                db.notification_log4.username, db.notification_log4.destination
            )
        else:
            mail_var = db(db.notification_log4.register == request.vars['notice']).select(db.notification_log4.username, db.notification_log4.destination)

    return dict(all_n=mail_var)

def search_files():
    p = []
    if request.vars['search_input'] is None:
        all_list = db((db.library.visible == True) & (db.library.owner_file != auth.user.id)
                & (db.library.project == db.project.id) & (db.project.id == db.user_project.project)
                & (db.user_project.assigned_user == auth.user.id) & ((db.user_project.period <= cpfecys.current_year_period().id)
                & ((db.user_project.period + db.user_project.periods) > cpfecys.current_year_period().id))
                & (db.library.period == db.user_project.period)).select()
        for a in all_list: p.append(a.library)
        
        all_list = db((db.library.owner_file == auth.user.id)).select()
        for a in all_list: p.append(a)
    else:
        name_like = f"%{request.vars['search_input']}%"
        all_list = db((db.library.name.like(name_like)) & (db.library.visible == True)
                & (db.library.owner_file != auth.user.id) & (db.library.project == db.project.id)
                & (db.project.id == db.user_project.project) & (db.user_project.assigned_user == auth.user.id)
                & ((db.user_project.period <= cpfecys.current_year_period().id ) & ((db.user_project.period + db.user_project.periods) > cpfecys.current_year_period().id))
                & (db.library.period == db.user_project.period)).select()
        for a in all_list: p.append(a.library)
        
        all_list = db((db.library.name.like(name_like)) & (db.library.owner_file == auth.user.id)).select()
        for a in all_list: p.append(a)

    return dict(all_list=p)

def attachment_files():
    return dict(attachment_list=session.attachment_list)

#Function use to obtain the count of the items
def count_select_items(items):
    count = 0
    try:
        items.append(-1)
        items.remove(-1)
        count = len(items)
    except:
        count = 0 if items == None else 1

    return count

def count_items(notices, count):
    total = 0
    for s in notices: total = s[count]
    
    return total

def notification_functions():
    return dict(var='')

def files_check():
    return dict(var='')

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher'))
def teacher_send_mail_to_students(users1, users2, message, subject, check, semester, year, cc=''):
    #Obtener valores reales (no ids)
    name_s2 = f"{check.assigned_user.first_name} {check.assigned_user.last_name}"
    name_p = check.project.name

    attachment_m = f'<br><br><b>{T("Attachments")}:</b><br>'
    if session.attachment_list:
        for attachment_list_var in session.attachment_list:
            for attachment_var in attachment_list_var:
                attachment_m += f'<a href="{cpfecys.get_domain()}{URL("default/download", attachment_var.file_data)}" target="blank"> {attachment_var.name}</a><br>'
    else:
        attachment_m = ''

    try:
        (name_p, project_section) = str(name_p).split('(')
        (name_s, _) = str(project_section).split(')')
        name_p += f' - {name_s}'
    except:
        None

    period = f'{T(semester)} {str(year)}'
    message = message.replace("\n", "<br>")
    
    if auth.has_membership('Student'):
        message_c = f'<html>{message}{attachment_m}<br><br>Tutor Academico: {str(name_s2)}<br>{str(period)}<br>{str(name_p)}<br>'
        message_c += 'Sistema de Seguimiento de La Escuela de Ciencias y Sistemas<br> Facultad de Ingeniería - Universidad de San Carlos de Guatemala</html>'
    else:
        message_c = f'<html>{message}{attachment_m}<br><br>Catedrático: {str(name_s2)}<br>{str(period)}<br>{str(name_p)}<br>'
        message_c += 'Sistema de Seguimiento de La Escuela de Ciencias y Sistemas<br> Facultad de Ingeniería - Universidad de San Carlos de Guatemala</html>'
    
    #variable de control
    control = 0
    #Log General del Envio
    row = db.notification_general_log4.insert(
        subject=subject,
        sent_message=message + attachment_m,
        emisor=check.assigned_user.username,
        course=check.project.name,
        yearp=year,
        period=semester
    )

    #Ciclo para el envio de correos para estudiantes
    listado_correos = None
    email_list_log = ""
    if users1 != None:
        for user in users1:
            if user.email != None and user.email != '':
                if listado_correos == None:
                    listado_correos = []
                    listado_correos.append(user.email)
                    email_list_log = str(user.email)
                else:
                    listado_correos.append(user.email)
                    email_list_log = f'{email_list_log},{str(user.email)}'

    if users2 != None:
        for user in users2:
            if user.email != None and user.email != '':
                if listado_correos == None:
                    listado_correos = []
                    listado_correos.append(user.email)
                    email_list_log = str(user.email)
                else:
                    listado_correos.append(user.email)
                    email_list_log = f'{email_list_log},{str(user.email)}'
    
    listado_correos.append(auth.user.email)
    
    #agrego los correos de cc
    if cc != '':
        arr_cc = cc.split(";")
        for item_cc in arr_cc: listado_correos.append(item_cc)

    was_sent = mail.send(to='dtt.ecys@dtt-ecys.org', subject=subject, message=message_c, bcc=listado_correos)
    
    ##Notification LOG GENERAL
    db.mailer_log.insert(
        sent_message=message_c,
        destination=email_list_log,
        result_log=f"{str(mail.error or '')}:{str(mail.result)}",
        success=was_sent,
        emisor=str(check.assigned_user.username)
    )
    
    ##Notification LOG
    email_list = str(email_list_log).split(",")
    for email_temp in email_list:
        user_var = db((db.auth_user.email == email_temp)).select(db.auth_user.username).first()
        if user_var != None: username_var = user_var.username
        else:
            user_var = db((db.academic.email == email_temp)).select(db.academic.carnet).first()
            username_var = user_var.carnet if user_var != None else 'None'
        db.notification_log4.insert(
            destination=email_temp, 
            username=username_var,
            result_log=f"{str(mail.error or '')}:{str(mail.result)}", 
            success=was_sent, 
            register=row.id
        )
    if not was_sent: control += 1
                
    session.attachment_list = []
    session.attachment_list_temp = []
    session.attachment_list_temp2 = []
    session.notification_subject = ''
    session.notification_message = ''
    session.cc = ''
    return control
