import cpfecys
import queries

@auth.requires_login()
def notification_calculation(username):
    conteo = 0
  
    user = db((db.auth_user.username == username)).select(db.auth_user.id, db.auth_user.username).first()

    nconteo_1 = db.executesql(queries.q_notification_calculation(1).format(user.id, user.username))
    nconteo_2 = db.executesql(queries.q_notification_calculation(2).format(user.id, user.username))
    conteo += int(nconteo_1[0][0]) + int(nconteo_2[0][0])
    
    redis_db_1.set(user.username, conteo)

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Academic'))
def send_mail():        
    cperiod = cpfecys.current_year_period()
    assigned = db((db.user_project.assigned_user == auth.user.id) & ((db.user_project.period <= cperiod.id) 
                & ((db.user_project.period + db.user_project.periods + 1) > cperiod.id)) & (db.user_project.project == request.vars['project'])).select(db.user_project.ALL).first()

    try:
        if assigned is None:
            carnet_var = db(db.academic.id_auth_user == auth.user.id).select(db.academic.id).first()
            assigned_user_var = db((db.academic_course_assignation.carnet == carnet_var.id) & (db.academic_course_assignation.assignation == request.vars['project'])).select(db.academic_course_assignation.semester).first()

            if (assigned_user_var.semester != cperiod.id) and ((assigned_user_var.semester + 1) != cperiod.id):
                session.flash = T('Not authorized')
                redirect(URL('default', 'home'))
    except:
        session.flash = T('Not authorized')
        redirect(URL('default', 'home'))


    period_id = cperiod.id if (request.vars['semester_id'] is None) or (str(request.vars['semester_id']) == "None") else request.vars['semester_id']
    cperiod =  db(db.period_year.id == period_id).select().first()
    
    period_list = []
    if (request.args(0) == 'send'):
        email = request.vars['mail']
        if email != None:
            name = request.vars['name']
            message = request.vars['message']
            subject = request.vars['subject']
            remessage = request.vars['remessage']
            resub = request.vars['resub']
            retime = request.vars['retime']
            var_project_name = request.vars['var_project_name']

            if message != '' and subject != '':
                fail = reply_mail_with_email(email,message, remessage, retime, resub, subject, cperiod, var_project_name)
                if fail > 0:
                    response.flash = T('Sent Error')
                else:
                    response.flash = T('Mail Sent')                
            else:
                response.flash = T('Fill all fields of the mail')

            return dict(
                email=email,
                name=name,
                remessage=remessage,
                retime=retime,
                resub=resub,
                var_project_name=var_project_name
            )
        else:
            list_users = request.vars['list_users']
            message = request.vars['message']
            subject = request.vars['subject']
            var_course = request.vars['var_course']
            
            if list_users != None and var_course != '' and message != '' and subject != '':
                fail = send_mail_to_users(list_users, message, subject, cperiod.period.name, cperiod.yearp, var_course)
                if fail > 0:
                    response.flash = T('Sent Error')
                else:
                    response.flash = T('Mail Sent')                
            else:
                response.flash = T('Fill all fields of the mail')

            academic_var = db(db.academic.id_auth_user == auth.user.id).select(db.academic.id).first() 
            assignations = db((db.academic_course_assignation.semester == period_id) & (db.academic_course_assignation.carnet == academic_var.id)).select(db.academic_course_assignation.id, db.academic_course_assignation.assignation)
            period_list = db(db.academic_course_assignation.carnet == academic_var.id).select(db.academic_course_assignation.semester, distinct=True)
            return dict(
                email=None,
                assignations=assignations,
                cperiod=cperiod,
                period_list=period_list, 
                period_id=period_id
            )  
    else:
        if (request.args(0) == 'period'):
            period_id = subject = request.vars['semester_id']
        if request.vars['mail'] != None:
            email = request.vars['mail']          
            name = request.vars['name']       
            remessage = request.vars['remessage']
            retime = request.vars['retime']
            resub = request.vars['resub']
            project_var = db(db.project.id == request.vars['project']).select(db.project.name).first()
            var_project_name = project_var.name

            return dict(
                email=email,
                name=name,
                remessage=remessage,
                retime=retime,
                resub=resub,
                var_project_name=var_project_name
            )
        else:
            academic_var = db(db.academic.id_auth_user == auth.user.id).select(db.academic.id).first()        
            assignations = db((db.academic_course_assignation.semester == period_id) & (db.academic_course_assignation.carnet == academic_var.id)).select(db.academic_course_assignation.id, db.academic_course_assignation.assignation)
            period_list = db(db.academic_course_assignation.carnet == academic_var.id).select(db.academic_course_assignation.semester, distinct=True)
            return dict(
                email=None,
                assignations=assignations,
                cperiod=cperiod,
                period_list=period_list, 
                period_id=period_id
            )
            
@auth.requires_login()
def reply_mail_with_email(email, message, remessage, retime, resub ,subject, semester, project_name):  
    message = message.replace("\n","<br>")
    period = f"{T(semester.period.name)} {str(semester.yearp)}" 
    courses_admin = None

    if (auth.has_membership('Student') or auth.has_membership('Teacher')):
        project = db(db.project.name == project_name).select(db.project.id).first()
        if project == None:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        else:
            courses_admin = db((db.user_project.assigned_user == auth.user.id) & ((db.user_project.period <= semester.id) 
                            & ((db.user_project.period + db.user_project.periods) > semester.id)) & (db.user_project.project == db.project.id)).select(db.user_project.id)
    
    message_c = '<html>' + message 
    if ((courses_admin is None) and auth.has_membership('Academic')):
        message_c += f"<br><br>Estudiante: {auth.user.first_name}  {auth.user.last_name}<br>Carnet:  {auth.user.username}<br>Correo: {auth.user.email}<br>"
    elif (auth.has_membership('Student') or auth.has_membership('Teacher')) and courses_admin != None:
        message_c += f"<br><br>{auth.user.first_name} {auth.user.last_name}<br>"
    else:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    
    message_c += f"{project_name}<br>{str(period)}<br>Sistema de Seguimiento de La Escuela de Ciencias y Sistemas<br> Facultad de Ingeniería - Universidad de San Carlos de Guatemala"
    message_c += f'<br><br><hr style="width:100%;"><b><i>Respuesta al mensaje enviado el {retime}:</i></b><br><table><tr><td><i><b>Asunto:</b></td><td>{resub}</td></tr></table></i></html>'
    control = 0
    was_sent = mail.send(to='dtt.ecys@dtt-ecys.org', subject=subject, message=message_c, bcc=email)

    if ((courses_admin is None) and auth.has_membership('Academic')):
        row = db.academic_send_mail_log.insert(
            subject=subject,
            sent_message=message,
            emisor=auth.user.username,
            course=project_name,
            yearp=semester.yearp,
            period=semester.period.name,
            mail_state=str(was_sent)
        )

        email_list = str(email).split(",")
        for email_temp in email_list:
            user_var = db((db.auth_user.email == email_temp)).select(db.auth_user.username).first()
            username_var = user_var.username if user_var != None else 'None'
            db.academic_send_mail_detail.insert(academic_send_mail_log=row, username=username_var, email=email_temp)
    elif (auth.has_membership('Student') or auth.has_membership('Teacher')) and courses_admin != None:
        row = db.notification_general_log4.insert(subject=subject, sent_message=message, emisor=auth.user.username, course=project_name, yearp=semester.yearp, period=semester.period.name)
        user_var = db((db.auth_user.email == email)).select(db.auth_user.username).first()

        if user_var != None: username_var = user_var.username
        else:
            user_var = db((db.academic.email == email)).select(db.academic.carnet).first()
            username_var = user_var.carnet if user_var != None else 'None'

        db.notification_log4.insert(destination=email, result_log=str(was_sent), username=username_var, success=str(was_sent), register=row) 
    
    if not was_sent: control += 1
    
    return control

@auth.requires_login()
def send_mail_to_users(users, message, subject, semester,year, project_name):  
    message = message.replace("\n", "<br>")
    period = f"{T(semester)} {str(year)}"

    messageC = f'<html>{message}<br><br>Estudiante: {auth.user.first_name} {auth.user.last_name}<br>Carnet: {auth.user.username}<br>Correo: {auth.user.email}'
    messageC += f'<br>{str(period)}<br>Sistema de Seguimiento de La Escuela de Ciencias y Sistemas<br> Facultad de Ingeniería - Universidad de San Carlos de Guatemala </html>'    
    control = 0

    dest = []
    students = users
    try:
        students.append(-1)
        students.remove(-1)
        for student in students:
            dest.append(student)
        #consultar a la base de datos para obtener a los usuarios a los que enviaremos
        user1 = db(db.auth_user.id.belongs(dest)).select(db.auth_user.email)
    except:
        #consultar a la base de datos para obtener a los usuarios a los que enviaremos
        user1 = db(db.auth_user.id == users).select(db.auth_user.email)
    
    email_list = None
    email_list_log = ""

    if user1 != None:
        for user in user1:
            if user.email != None and user.email != '':
                if email_list == None:
                    email_list = []
                    email_list.append(user.email)
                    email_list_log = str(user.email)
                else:
                    email_list.append(user.email)
                    email_list_log = f"{email_list_log},{str(user.email)}"

    was_sent = mail.send(to='dtt.ecys@dtt-ecys.org', subject=subject, message=messageC, bcc=email_list)
    row = db.academic_send_mail_log.insert(
        subject=subject,
        sent_message=message,
        emisor=auth.user.username,
        course=project_name,
        yearp=year,
        period=semester,
        mail_state=str(was_sent)
    )

    email_list = str(email_list_log).split(",")
    for email_temp in email_list:
        user_var = db((db.auth_user.email == email_temp)).select(db.auth_user.username).first()

        username_var = user_var.username if user_var != None else 'None'
        db.academic_send_mail_detail.insert(academic_send_mail_log=row, username=username_var, email=email_temp)

    return control

@auth.requires_login()
@auth.requires_membership('Academic')
def sent_mails():        
    all_course = True

    if request.vars['period'] is None:
        cperiod = cpfecys.current_year_period()
    else:
        all_course = False
        cperiod = db(db.period_year.id == request.vars['period']).select(db.period_year.id).first()

    academic_var = db(db.academic.id_auth_user == auth.user.id).select(db.academic.id).first()       
    period_list = db(db.academic_course_assignation.carnet == academic_var.id).select(db.academic_course_assignation.semester, distinct=True)

    select_form = FORM(INPUT(_name='semester_id', _type='text'))

    if select_form.accepts(request.vars, formname='select_form'):
        assignations = db((db.academic_course_assignation.semester == str(select_form.vars.semester_id)) & (db.academic_course_assignation.carnet == academic_var.id)).select(db.academic_course_assignation.assignation)
        period_id = str(select_form.vars.semester_id)
        all_course = True
    else:
        assignations = db((db.academic_course_assignation.semester == cperiod.id) & (db.academic_course_assignation.carnet == academic_var.id)).select(db.academic_course_assignation.assignation)
        period_id = str(cperiod.id)

    return dict(
        assignations=assignations,
        email=auth.user.email,
        period_id=period_id,
        period_list=period_list,
        cperiod=cperiod.id,
        all_course=all_course
    )

@auth.requires_login()
def register_mail():
    notices = None

    if request.vars['project'] != None:
        project = request.vars['project']
        semester = request.vars['period_id']        
        yearp_var = db(db.period_year.id == semester).select(db.period_year.period, db.period_year.yearp).first()
        project_name = db(db.project.id == project).select(db.project.name).first()
        notices = db((db.academic_send_mail_log.emisor == auth.user.username) & (db.academic_send_mail_log.course == project_name.name)
                & (db.academic_send_mail_log.period == yearp_var.period.name) & (db.academic_send_mail_log.yearp == yearp_var.yearp)
                ).select(db.academic_send_mail_log.id, db.academic_send_mail_log.subject, db.academic_send_mail_log.sent_message, db.academic_send_mail_log.time_date)
    
    return dict(notices=notices)

@auth.requires_login()
def register_mail_detail():
    if request.vars['notice'] != None:
        mail_var = db(db.academic_send_mail_log.id == request.vars['notice']
                    ).select(db.academic_send_mail_log.id, db.academic_send_mail_log.subject, db.academic_send_mail_log.sent_message, db.academic_send_mail_log.time_date,
                            db.academic_send_mail_log.mail_state).first()         
        listado_c = db((db.academic_send_mail_detail.academic_send_mail_log == mail_var.id)).select(db.academic_send_mail_detail.username, db.academic_send_mail_detail.email)
    
    return dict(mail_var=mail_var, listado_c=listado_c)

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Academic'))
def inbox():
    cperiod = cpfecys.current_year_period()
    assignations = []
    courses_admin = []

    #actualizando las notificaciones Redis
    notification_calculation(auth.user.username)
    
    select_form = FORM(INPUT(_name='semester_id', _type='text'))
    show_error = False
    
    if select_form.accepts(request.vars, formname='select_form'):
        if (auth.has_membership('Academic') and not auth.has_membership('Teacher')):
            #RGUARAN:se agregó academic_var
            academic_var = db.academic(db.academic.id_auth_user == auth.user.id)        
            assignations = db((db.academic_course_assignation.semester == str(select_form.vars.semester_id)) & (db.academic_course_assignation.carnet == academic_var.id)).select(db.academic_course_assignation.semester, db.academic_course_assignation.assignation)
        period_id = str(select_form.vars.semester_id)
    else:
        if (auth.has_membership('Academic') and not auth.has_membership('Teacher')):
            #se agregó academic_var
            academic_var = db.academic(db.academic.id_auth_user == auth.user.id)
            try:
                assignations = db((db.academic_course_assignation.semester == cperiod.id) & (db.academic_course_assignation.carnet == academic_var.id)).select(db.academic_course_assignation.semester, db.academic_course_assignation.assignation)
            except AttributeError:
                show_error = True
            
        period_id = str(cperiod.id)

    if (auth.has_membership('Student') or auth.has_membership('Teacher')):
        courses_admin = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == db.project.id)
                        & ((db.user_project.period <= period_id) & ((db.user_project.period + db.user_project.periods) > period_id))).select(db.user_project.project)          

        years = db(db.period_year).select(db.period_year.id)
        t = years[len(years) - 1]

    periods_temp = db(db.period_year).select(orderby=~db.period_year.id)
    periods = []
    for period_temp in periods_temp:
        added = False
        if auth.has_membership('Student') or auth.has_membership('Teacher'):
            try:
                if db((db.user_project.assigned_user == auth.user.id) & (db.user_project.period == db.period_year.id)
                    & ((db.user_project.period <= t.id) & ((db.user_project.period + db.user_project.periods) > period_temp.id))).select(db.user_project.id).first() is not None:
                    periods.append(period_temp)
                    added = True
            except:
                None
        if auth.has_membership('Academic'):
            try:
                if db((db.academic_course_assignation.carnet == academic_var.id) & (db.academic_course_assignation.semester == period_temp.id)).select(db.academic_course_assignation.id).first() is not None and not added:
                    periods.append(period_temp)
            except:
                None

    period_var = db(db.period_year.id == period_id).select(db.period_year.yearp, db.period_year.period).first()
    if not show_error:
        return dict(
            assignations=assignations,
            email=auth.user.email,
            period_var=period_var,
            period_id=period_id,
            period_list=periods,
            cperiod=cperiod.id,
            courses_admin=courses_admin
        )
    else:
        return response.render('notification_student/inbox_error.html')
    
@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Academic'))
def inbox_mails_load():
    #If emisor username change... error of reload
    try:
        if request.vars['operation'] == "mails_list":
            year_var = db(db.period_year.id == request.vars['period_id']).select(db.period_year.yearp, db.period_year.period)[0]
            period_var = db(db.period.id == year_var.period).select(db.period.name)[0]
            project_var = db(db.project.id == request.vars['project_id']).select(db.project.name)[0]

            mails = db((db.notification_general_log4.yearp == year_var.yearp) & (db.notification_general_log4.period == period_var.name) 
                    & (db.notification_general_log4.course == project_var.name)).select(db.notification_general_log4.id, db.notification_general_log4.emisor, db.notification_general_log4.subject, db.notification_general_log4.time_date)

            return dict(
                mails=mails, 
                auth_user=auth.user.id
            )    
        elif request.vars['operation'] == "view_mail":
            if db((db.read_mail.id_auth_user == auth.user.id) & (db.read_mail.id_mail == request.vars['mail_id'])).select().first() == None:
                db.read_mail.insert(id_auth_user=auth.user.id, id_mail=request.vars['mail_id'])
            
            mail_var = db(db.notification_general_log4.id == request.vars['mail_id']).select(db.notification_general_log4.subject, db.notification_general_log4.sent_message, db.notification_general_log4.time_date, db.notification_general_log4.emisor)[0]
            user_var = db(db.auth_user.username == mail_var.emisor).select(db.auth_user.email, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.id, db.auth_user.photo)[0]
            
            return dict(
                mail=mail_var, 
                emisor=user_var
            )
    except Exception:
        return dict(
            mail="", 
            emisor=""
        )
    
@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Academic'))
def inbox_student_mails_load():
    #If emisor username change... error of reload
    try:
        if request.vars['operation'] == "mails_list":
            year_var = db(db.period_year.id == request.vars['period_id']).select(db.period_year.period, db.period_year.yearp)[0]
            period_var = db(db.period.id == year_var.period).select(db.period.name)[0]
            project_var = db(db.project.id == request.vars['project_id']).select(db.project.name)[0]

            mails = db((db.academic_send_mail_log.yearp == year_var.yearp) & (db.academic_send_mail_log.period == period_var.name) 
                    & (db.academic_send_mail_log.course == project_var.name)).select(db.academic_send_mail_log.id, db.academic_send_mail_log.subject, db.academic_send_mail_log.emisor, db.academic_send_mail_log.time_date)
            mails2 = db((db.notification_general_log4.yearp == year_var.yearp) & (db.notification_general_log4.period == period_var.name) 
                    & (db.notification_general_log4.course==project_var.name)).select(db.notification_general_log4.id, db.notification_general_log4.subject, db.notification_general_log4.emisor, db.notification_general_log4.time_date)
        
            return dict(mails=mails,  mails2=mails2, auth_user=auth.user.id)    
        elif request.vars['operation'] == "view_mail":
            if db((db.read_mail_student.id_auth_user == auth.user.id) & (db.read_mail_student.id_mail == request.vars['mail_id'])).select(db.read_mail_student.id).first() == None:
                db.read_mail_student.insert(id_auth_user=auth.user.id, id_mail=request.vars['mail_id'])

            mail_var = db.academic_send_mail_log(db.academic_send_mail_log.id == request.vars['mail_id'])
            user_var = db(db.auth_user.username == mail_var.emisor).select(db.auth_user.id, db.auth_user.photo, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.email)[0]
            return dict(mail=mail_var, emisor=user_var)
    except Exception:
        return dict(mail="", emisor="")