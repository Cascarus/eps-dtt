# -*- coding: utf-8 -*-
import cpfecys
import config
from gluon.contrib.pysimplesoap.client import SoapClient
from gluon.contrib.pysimplesoap.client import SimpleXMLElement
import xml.etree.ElementTree as ET
from datetime import datetime
import ds_utils
import gluon.contenttype as c        
import dsa_utils_temp as dsa_utils

def events():
    #emarquez
    period = request.vars['period'] or False
    cyearperiod = cpfecys.current_year_period()

    #emarquez
    if period:
        cyearperiod = db(db.period_year.id == int(period)).select().first()

    return dict(year = cyearperiod.yearp, semester = cyearperiod.period.name,
                thing = db((db.public_event.semester == cyearperiod.id)&
                            (db.public_event.assignation != None)&
                            (db.public_event.assignation == db.user_project.id)&
                            (db.user_project.project == db.project.id) \
                            ).select(orderby=db.project.name))

@auth.requires_login()
def event_editor():
    assignation = request.vars['assignation']
    #check assignation belongs to this user
    check =  db((db.user_project.assigned_user==auth.user.id)&\
            (db.user_project.id == assignation)&\
            ((db.user_project.period <= cpfecys.current_year_period().id) &\
            ((db.user_project.period + db.user_project.periods) >\
            cpfecys.current_year_period().id)))\
            .select(db.user_project.ALL).first()

    if check is None:
        redirect(URL('default','home'))

    cyearperiod = cpfecys.current_year_period()
    db.public_event.semester.default = cyearperiod.id
    db.public_event.semester.writable = False
    db.public_event.semester.readable = False
    db.public_event.assignation.default = check.id
    db.public_event.assignation.writable = False
    db.public_event.assignation.readable = False
    db.public_event_schedule.public_event.readable = False
    db.public_event_schedule.public_event.writable = False
    query = (db.public_event.assignation==check.id)

    datos = db(db.public_event.assignation==check.id).select()

    return dict(year=cyearperiod.yearp,
                semester=cyearperiod.period.name,
                name=check.project.name,
                grid=SQLFORM.smartgrid(db.public_event,
                                    args=request.args,
                                    constraints={'public_event': query},
                                    linked_tables=['public_event_schedule']))

def index():
    session.login_force_redirect = None
    if auth.user != None:
        groups = db((db.auth_membership.user_id==auth.user.id)& \
                        (db.auth_group.id==db.auth_membership.group_id)). \
                        select(db.auth_group.ALL)
        front_notification = \
        db(db.front_notification.is_public==True).select()| \
        db((db.front_notification.id== \
            db.notification_access.front_notification)& \
        (db.notification_access.user_role.belongs(groups))
            ).select(db.front_notification.ALL)
    else:
        front_notification = db(db.front_notification.is_public == True).select()
    return dict(front_notification=front_notification,
        markmin_settings = cpfecys.get_markmin)

def links():
    """ This url shows all important links published by admin
    user.
    """
    links = []
    if auth.user != None:
        links = db(db.link).select()
        groups = db((db.auth_membership.user_id==auth.user.id)& \
                        (db.auth_group.id==db.auth_membership.group_id)). \
                        select(db.auth_group.ALL)
        links = db((db.link.id == db.link_access.link)& \
                (db.link_access.user_role.belongs(groups))).select(db.link.ALL)
    public_links = db(db.link.is_public == True).select()
    return dict(links=links, public_links=public_links)

def files():
    """ This url shows all published files published by admin"""
    if auth.user != None:
        groups = db((db.auth_membership.user_id==auth.user.id)&\
                        (db.auth_group.id==db.auth_membership.group_id)).\
                        select(db.auth_group.ALL)
        files = db((db.uploaded_file.id == db.file_access.uploaded_file)&\
                (db.file_access.user_role.belongs(groups)))\
                    .select(db.uploaded_file.ALL)
    else:
        files = db(db.uploaded_file.is_public == True).select()
    return dict(files=files)

def files_dashboard():
    """ This url shows all published files published by admin"""
    if auth.user != None:
        groups = db((db.auth_membership.user_id==auth.user.id)&\
                        (db.auth_group.id==db.auth_membership.group_id)).\
                        select(db.auth_group.ALL)
        files = db((db.uploaded_file.id == db.file_access.uploaded_file)&\
                (db.file_access.user_role.belongs(groups)))\
                    .select(db.uploaded_file.ALL)
    else:
        files = db(db.uploaded_file.is_public == True).select()
    return dict(files=files)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    if request.args(0) == 'profile':
        if ((auth.has_membership('Super-Administrator') == False) & (auth.has_membership('Teacher') == False) & (auth.has_membership('Ecys-Administrator') == False)):
            db.auth_user.first_name.writable = False
            db.auth_user.last_name.writable = False
            db.auth_user.username.writable = False

            db.auth_user.email.writable = False

            currentyear_period = cpfecys.current_year_period()

            for date_var in db((db.student_control_period.period_name==T(str(currentyear_period.period.name))+" "+str(currentyear_period.yearp))).select():
                var_date_finish = date_var.date_finish
                if datetime.now() > date_var.date_start and datetime.now() < var_date_finish:
                    db.auth_user.email.writable = True



            db.auth_user.photo.writable = True
            review = db((db.photo_review.user_id == auth.user.id)).select().first()
            if review is not None:
                if review.accepted == True:
                    db.auth_user.photo.writable = False

        if (auth.has_membership('Teacher')):
            if str(request.vars["edit_foto"]) == "True":
                db.auth_user.photo.writable = True
            else:
                db.auth_user.photo.writable = False
            db.auth_user.username.writable = False
    
    if request.env.request_method == "GET" and \
        request.args(0) == 'login' and (session.login_force_redirect is None or request.vars['_next'] is not None):
        print('Desde login:', request.vars['_next'])
        if request.vars['_next'] is not None:
            session.login_force_redirect = request.vars['_next']
        else:
            session.login_force_redirect = URL('default','home')
        redirect(URL('user','login'))

    # AMontufar se agrego para que cuando se inicia session se redireccione a home
    auth.settings.login_next = URL('default','home')
    form=auth()
    #form['class']='table table-bordered dataTable'
    return dict(form=form)

#CERODAS 1:  Function to validated if the user has update data or not
def get_user_update_data():
    if request.vars['Username'] != '':
        row = db(db.auth_user.username==request.vars['Username']).select().first()
        if row != None:
            #obtengo el grupo del usuario: si estudiante aplica  sino  no aplica metodo
            group_id_student = db(db.auth_group.role == 'Student').select().first()
            group_id_regularstudent = db(db.auth_group.role == "Academic").select().first()
            #si no hay informacion de los grupos se devuelve -1
            if group_id_student is None:
                group_id_student = -1
            if group_id_regularstudent is None:
                group_id_regularstudent = -1
            #se verifica si el usuario pertenece a algun grupo de estudiantes
            student = db((row.id==db.auth_membership.user_id) & ((db.auth_membership.group_id==group_id_student) | (db.auth_membership.group_id==group_id_regularstudent))).select().first()
            if student is None:
                is_student = False
            else:
                is_student = True
            #si es estudiante se aplica el nuevo metodo de lo contrario si no es estudiante se pasa por el procedimiento normal
            if is_student:
                user_info = row.data_updated
                if user_info is None:
                    session.username = request.vars['Username'];
                    redirect(URL('first_request_password'))
                else:
                    session.username = request.vars['Username'];
                    session.flash = ('Usuario verificado correctamente, puede proceder a solicitar su password via email.')
                    redirect(URL('user', args=('request_reset_password'), vars=dict(message='UPDATED')))
            else:
                session.username = request.vars['Username'];
                session.flash = ('Usuario verificado correctamente, puede proceder a solicitar su password via email.')
                redirect(URL('user', args=('request_reset_password'), vars=dict(message='UPDATED')))
        else:
            session.flash = T('Invalid username')
            redirect(URL('user', args=('request_reset_password'), vars=dict(message='NOT_RESULT')))
    else:
        session.flash = T('Username') + ' ' + T('Cannot be empty')
        redirect(URL('user', args=('request_reset_password'), vars=dict(message='NOT_DATA')))

#CERODAS 1: Copy from WEBSERVICE check_user from check_user in controller student_academic
#Changes: Not valid user logon
def check_student(check_carnet):
    svp=db(db.validate_student).select().first()
    if svp is not None:
        try:
            #CONSUME THE WEBSERVICE
            client = SoapClient(
                location = svp.supplier,
                action = svp.supplier+"/"+svp.action_service,
                namespace = svp.supplier,
                soap_ns=svp.type_service, trace = True, ns = False)

            year = cpfecys.current_year_period()
            sent="<"+svp.send+">"
            for svpf in db(db.validate_student_parameters).select():
                sent +="<"+svpf.parameter_name_validate+">"+svpf.parameter_value_validate+"</"+svpf.parameter_name_validate+">"
            sent += "<CARNET>"+str(check_carnet)+"</CARNET><CICLO>"+str(year.yearp)+"</CICLO></"+svp.send+">"
            back = client.call(svp.action_service,xmlDatos=sent)

            #PREPARE FOR RETURNED XML WEB SERVICE
            xml = back.as_xml()
            xml=xml.replace('&lt;','<')
            xml=xml.replace('&gt;','>')
            inicio = xml.find("<"+svp.receive+">")
            final = xml.find("</"+svp.receive+">")
            xml = xml[inicio:(final+17)]
            root = ET.fromstring(xml)
            xml = SimpleXMLElement(xml)

            #VARIABLE TO CHECK THE CORRECT FUNCTIONING
            CARNET = xml.CARNET
            NOMBRES = xml.NOMBRES
            APELLIDOS= xml.APELLIDOS
            CORREO = xml.CORREO

            #Unicode Nombres
            try:
                str(NOMBRES)
            except:
                apellidos_var = unicode(NOMBRES).split(' ')
                appellidos_return = None
                for apellido in apellidos_var:
                    try:
                        if appellidos_return is None:
                            appellidos_return = str(apellido)
                        else:
                            appellidos_return = appellidos_return + " " + str(apellido)
                    except:
                        try:

                            temp = unicode(apellido).encode('utf-8').replace('Ã¡','á').replace('Ã©','é').replace('Ã­','í').replace('Ã³','ó').replace('Ãº','ú').replace('Ã±','ñ').replace('Ã','Á').replace('Ã‰','É').replace('Ã','Í').replace('Ã“','Ó').replace('Ãš','Ú').replace('Ã‘','Ñ').replace('Ã¼‘','ü')
                        except:
                            None

                        apellido = temp
                        if appellidos_return is None:
                            appellidos_return = str(apellido)
                        else:
                            appellidos_return = appellidos_return + " " + str(apellido)
                NOMBRES = appellidos_return
            #Unicode APELLIDOS
            try:
                str(APELLIDOS)
            except:
                apellidos_var = unicode(APELLIDOS).split(' ')
                appellidos_return = None
                for apellido in apellidos_var:
                    try:
                        if appellidos_return is None:
                            appellidos_return = str(apellido)
                        else:
                            appellidos_return = appellidos_return + " " + str(apellido)
                    except:
                        try:
                            temp = unicode(apellido).encode('utf-8').replace('Ã¡','á').replace('Ã©','é').replace('Ã­','í').replace('Ã³','ó').replace('Ãº','ú').replace('Ã±','ñ').replace('Ã','Á').replace('Ã‰','É').replace('Ã','Í').replace('Ã“','Ó').replace('Ãš','Ú').replace('Ã‘','Ñ').replace('Ã¼‘','ü')
                        except:
                            None

                        apellido = temp
                        if appellidos_return is None:
                            appellidos_return = str(apellido)
                        else:
                            appellidos_return = appellidos_return + " " + str(apellido)
                APELLIDOS = appellidos_return

            if (CARNET is None or CARNET=='') and (NOMBRES is None or NOMBRES=='') and (APELLIDOS is None or APELLIDOS=='') and (CORREO is None or CORREO==''):
                return dict(flag=False,error=False,message=T('The record was removed because the user is not registered to the academic cycle'))
            else:
                is_student=False
                for c in root.findall('CARRERA'):
                    if c.find('UNIDAD').text=="08" and c.find('EXTENSION').text=="00" and (c.find('CARRERA').text=="05" or c.find('CARRERA').text=="09" or c.find('CARRERA').text=="07"):
                        is_student=True

                if is_student==False:
                    return dict(flag=False,error=False,message=T('The record was removed because students not enrolled in career allowed to use the system'))
                else:
                    return dict(flag=True, carnet=int(str(CARNET)), nombres=(NOMBRES), apellidos=(APELLIDOS), correo=str(CORREO),error=False)
        except:
            return dict(flag=False,error=True,message=T('Error with web service validation'))
    else:
        return dict(flag=False,error=True,message=T('Error with web service validation'))

#CERODAS 1: new method from password recovery
def first_request_password():
    web_service = check_student(session.username)
    if web_service['flag'] == True:
        nombres = web_service['nombres']
        if nombres is None:
            nombres = ''
        apellidos = web_service['apellidos']
        if apellidos is None:
            apellidos = ''
        email = web_service['correo']
        #Email = 'Carlos8_r@hotmail.com'
        if email is None:
            email = ''
        carnet = web_service['carnet']
        if carnet is None:
            carnet = ''

        full_name = str(nombres) + " " + str(apellidos)

        if email == '':
            message_head = "Lastimosamente no existe informacion de tu email en nuestras bases de datos, por lo que debes actualizar tu informacion en Registro y Estadistica."
        else:
            #Obtengo la informacion del usuario
            usua = db(db.auth_user.username==session.username).select().first()
            #Seteo el valor del Email obtenido por el webservices
            if usua.email is None:
                usua.email = email
            else:
                email = usua.email
            #Mando el email para recuperacion
            auth.email_reset_password(usua)
            #Construyo el mensaje
            message_head = "Te hemos enviado un email a "
            message_middle = str(email)
            message_final = " , el cual está registrado en el sistema de Registro y Estadística.  Si esta cuenta ya no está activa procede a solicitar tu cambio de correo en Registro y Estadística."
        return dict(FullName = full_name, MessageHead = message_head, MessageMiddle = message_middle,MessageFinal=message_final )
    else:
        session.flash = 'Upss!!! Ocurrio un problema con el sistema de Registro y Estadística, intenta nuevamente.'
        redirect(URL('user', args=('request_reset_password')))

@auth.requires_login()
def home():
    if auth.has_membership('Empresa'):
        qs = f"SELECT * FROM bt_empresa WHERE id_usuario = {auth.user.id};"
        res = db.executesql(qs, as_dict=True)
        return dict(empresa=res[0])
    return dict()

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

def download_file():
    the_file = db(db.uploaded_file.file_data==request.args[0]).select().first()
    if the_file != None and the_file.visible == True and the_file.is_public == True:
        return response.download(request, db)
    else:
        session.flash = T('Access Forbidden')
        redirect(URL('default', 'home'))

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
    A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
    LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())

def zip():
    files = ['item.uploaded_file.bd4592bbb798c7c6.3235363035372e706466.pdf']
    return response.zip(request, files, db)

def resources():
    #Get the selected item_restriction id from parameter
    item_restriction_id = request.vars['r']
    #Get the items that belong to current semester

    #emarquez: por default, sigue igual, si envia  parametro d periodo, se cambia
    parameter_period = request.vars['period'] or False

    period = cpfecys.current_year_period()
    #emarquez
    if parameter_period:
        period = db(db.period_year.id == parameter_period).select().first()

    def teachers_on_project(project_id):
        #period = cpfecys.current_year_period()
        if cpfecys.is_semestre(period.id):
            data = db((db.project.id == project_id)&\
                    (db.user_project.project == db.project.id)&\
                    (db.auth_user.id == db.user_project.assigned_user)&\
                    ((db.user_project.period <= period.id) & ((db.user_project.period + db.user_project.periods) > period.id))&\
                    (db.auth_membership.user_id == db.auth_user.id)&\
                    (db.auth_membership.group_id == db.auth_group.id)&\
                    (db.auth_group.role == 'Teacher')).select()
            #print db._lastsql
            return data
        else:
            return db((db.project.id == project_id)&\
                    (db.user_project.project == db.project.id)&\
                    (db.auth_user.id == db.user_project.assigned_user)&\
                    (db.user_project.period == period.id) &\
                    (db.auth_membership.user_id == db.auth_user.id)&\
                    (db.auth_membership.group_id == db.auth_group.id)&\
                    (db.auth_group.role == 'Teacher')).select()

    def aux_in_courses(project_id):
        rowsi = db((db.period.id==db.period_detail.period)&(db.period_year.period==db.period.id)).select()

        lst = []
        for r in rowsi:
            lst.append(r.period_year.id)


        return db((db.project.id == project_id)&\
                (db.user_project.project == db.project.id)&\
                (db.auth_user.id == db.user_project.assigned_user)&\
                ((~db.user_project.period.belongs(lst))&(db.user_project.period <= period.id) & ((db.user_project.period + db.user_project.periods) > period.id))&\
                (db.auth_membership.user_id == db.auth_user.id)&\
	        	(db.auth_membership.group_id == db.auth_group.id)&\
                (db.auth_group.role == 'Student')).select()


    return dict(teachers_on_project = teachers_on_project,
                aux_in_courses = aux_in_courses,
                semester = period,
                data = db((db.item.created == period)&
                        (db.item.item_restriction == item_restriction_id)&
                        (db.item.item_restriction == db.item_restriction.id)&
                        (db.item_restriction.is_public == True)&
                        ((db.item_restriction.period == period)|(db.item_restriction.permanent == True))&
                        (db.item.assignation == db.user_project.id)&
                        (db.user_project.project == db.project.id)&
                        (db.user_project.project == db.project.id)&\
                        (db.auth_user.id == db.user_project.assigned_user)&\
                        #(db.user_project.assignation_status == None)&\
                        (db.auth_membership.user_id == db.auth_user.id)&\
                        (db.auth_membership.group_id == db.auth_group.id)&\
                        (db.auth_group.role == 'Student')&
                        (db.item.id > 0)).select(orderby=db.project.name),
                period =parameter_period)

def notification():
    notification = request.vars['notification']
    
    front_notification = db((db.front_notification.is_public == True)&\
                            (db.front_notification.id == notification)).select().first()
        
    return dict(front_notification=front_notification,markmin_settings = cpfecys.get_markmin)

def about_us():
    return dict(message="about us")

def autorities():
    return dict()

@auth.requires_login()
def myprofile():
    auth.settings.profile_next = URL('default','home')
    if ((auth.has_membership('Super-Administrator') == False) & (auth.has_membership('Teacher') == False) & (auth.has_membership('Ecys-Administrator') == False)):
        db.auth_user.first_name.writable = False
        db.auth_user.last_name.writable = False
        db.auth_user.username.writable = False

        db.auth_user.email.writable = False

        currentyear_period = cpfecys.current_year_period()

        for date_var in db((db.student_control_period.period_name==T(str(currentyear_period.period.name))+" "+str(currentyear_period.yearp))).select():
            var_date_finish = date_var.date_finish
            if datetime.now() > date_var.date_start and datetime.now() < var_date_finish:
                db.auth_user.email.writable = True

        db.auth_user.photo.writable = True
        review = db((db.photo_review.user_id == auth.user.id)).select().first()
        if review is not None:
            if review.accepted == True:
                db.auth_user.photo.writable = False

    if (auth.has_membership('Teacher')):
        if str(request.vars["edit_foto"]) == "True":
            db.auth_user.photo.writable = True
        else:
            db.auth_user.photo.writable = False
        db.auth_user.username.writable = False

    form=auth.profile()
    #auth.settings.profile_next = URL('default','home')
    
    print (auth.settings)
    return dict(form=form)

def escuela():
    return dict()

def profile_student():
    return dict()

@auth.requires_login()
def process_login():
    if auth.has_membership('Student'):
        period = cpfecys.current_year_period()
        student_course_in_charge_now = db.executesql((  " SELECT COUNT(*) AS conteo " 
                                            " FROM auth_user " 
                                            "     INNER JOIN user_project ON auth_user.id = user_project.assigned_user " 
                                            "     INNER JOIN project ON project.id = user_project.project " 
                                            "     INNER JOIN area_level ON project.area_level = area_level.id " 
                                            " WHERE user_project.assigned_user = {} "
                                            "     AND user_project.assignation_status IS NULL "
                                            "     AND user_project.period = {}"
                                            "     AND area_level.name = 'DTT Tutor Académico' " 
                                            "     AND user_project.period <= {}; " .format( auth.user.id, period.id, period.id) ), as_dict=True)
        session.student_courses_in_charge = student_course_in_charge_now[0]['conteo']

        student_courses_history = db.executesql(( " SELECT COUNT(*) AS conteo " 
                                    " FROM auth_user " 
                                    "     INNER JOIN user_project ON auth_user.id = user_project.assigned_user " 
                                    "     INNER JOIN project ON project.id = user_project.project " 
                                    "     INNER JOIN area_level ON project.area_level = area_level.id " 
                                    " WHERE user_project.assigned_user = {} "
                                    "     AND (user_project.assignation_status = 1 "
                                    "     OR user_project.assignation_status IS NULL)"
                                    "     AND area_level.name = 'DTT Tutor Académico'; ".format(auth.user.id) ), as_dict=True)
        session.student_courses_history = student_courses_history[0]['conteo']

    if auth.has_membership('Academic'):
        academic_var = db.academic(db.academic.id_auth_user == auth.user.id)
        '''
        si el usuario no tiene datos en la tabla academic que le permita ingresar
        codigo de honor
        '''
        if(academic_var == None):
            print("se cumple esto1")
            redirect(URL('default', 'home'))
        else:
            redirect(URL('default', 'sign_honor_code'))
    else:
        temp_login_force_redirect = session.login_force_redirect
        session.login_force_redirect = None
        print('Desde process:', temp_login_force_redirect)
        redirect(temp_login_force_redirect)

@auth.requires_login()
@auth.requires_membership('Academic')
def sign_honor_code():
    academic_var = db.academic(db.academic.id_auth_user == auth.user.id)

    if request.env.request_method == "POST":
        db(db.academic.id == academic_var.id).update(sign_honor_code=True)
        redirect(URL('default', 'home'))

    periodo = cpfecys.current_year_period()
    count_courses = db.executesql(( " SELECT COUNT(*) as conteo FROM academic_course_assignation  " 
                " WHERE academic_course_assignation.carnet = {} " 
                " 	AND academic_course_assignation.semester = {};".format(academic_var.id, periodo.id)), as_dict=True)
    count_courses = count_courses[0]['conteo']

    if not (count_courses > 0 and academic_var.sign_honor_code is False):
        temp_login_force_redirect = session.login_force_redirect
        session.login_force_redirect = None
        print('Desde sign:', temp_login_force_redirect)
        redirect(temp_login_force_redirect)

    honor_code = db.executesql(( " SELECT code FROM fys_honor_code " 
                " ORDER BY id DESC " 
                " LIMIT 1; "), as_dict=True)
    if len(honor_code) != 1:
        honor_code = dict(code='Codigo de honor')
    else:
        honor_code = honor_code[0]
    return dict(honor_code=honor_code)

# *********** Inicio - Prácticas Finales (Digital Signature) - Fernando Reyes *************
def file_validation():
    args = request.args
    new_dict = {}

    if len(args) != 2:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    if args[0] != 'document':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'index'))

    d_id = ds_utils.decode_delivered_id(args[1].strip())

    #if not request.vars.has_key('ref'):
    if not 'ref' in request.vars:
        ref = None
    else:
        ref = request.vars.ref.strip()

        if ref != 'item':
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'index'))

    query_find = ds_utils.get_information_student(d_id, ref)
    student = db.executesql(query_find, as_dict=True)

    if len(student) < 1:
        session.flash = 'No se encontro documento'
        redirect(URL('default', 'index'))

    new_dict['item'] = student
    new_dict['ref'] = ref

    def history_assignations(id_user):
        query_assignations = ds_utils.get_history_assignations(id_user)
        return db.executesql(query_assignations, as_dict=True)

    def history_rejections(id_delivered, reference):
        query_rejections = ds_utils.get_history_rejections(id_delivered, reference)
        return db.executesql(query_rejections, as_dict=True)

    return dict(action=new_dict,
                history_assignations=history_assignations,
                history_rejections=history_rejections)

@cache.action()
def download_deliverable():
    args = request.args

    if len(args) != 1:
        raise HTTP(404)

    filename = args[0].strip()
    print(request.folder)
    try:
        file = ds_utils.retrieve_file(filename, request.folder)
    except Exception as e:
        print('********** default - download content **********')
        print(str(e))
        raise HTTP(404)

    response.headers["Content-Type"] = c.contenttype(filename)
    response.headers["Content-Disposition"] = "attachment; filename=%s" % filename
    stream = response.stream(file, request=request)

    raise HTTP(200, stream, **response.headers)

# *********** Fin - Prácticas Finales (DS) - Fernando Reyes *************

#*********** Inicio - Prácticas Finales (Firma Digital Linguistica) - Juan Pablo Ardon *************

def file_validation_ecys():
    
    args = request.args
    new_dict = {}

    if len(args) != 2:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    if args[0] != 'document':
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'index'))

    d_id = dsa_utils.decode_delivered_id(args[1].strip())

    query_find = dsa_utils.get_information_student(d_id)
    student = db.executesql(query_find, as_dict=True)
    
    complement_query = dsa_utils.get_complementary_information_student(d_id)
    complement_student = db.executesql(complement_query, as_dict=True)

    student[0].update(complement_student[0])
    
    if len(student) < 1:
        session.flash = 'No se encontro documento'
        redirect(URL('default', 'index'))

    new_dict['item'] = student

    return dict(action=new_dict)

# *********** Fin - Prácticas Finales (Firma Digital Linguistica) - Juan Pablo Ardon *************

def links_dashboard():
    links = []
    if auth.user != None:
        links = db(db.link).select()
        groups = db((db.auth_membership.user_id==auth.user.id)& \
                        (db.auth_group.id==db.auth_membership.group_id)). \
                        select(db.auth_group.ALL)
        links = db((db.link.id == db.link_access.link)& \
                (db.link_access.user_role.belongs(groups))).select(db.link.ALL)
    public_links = db(db.link.is_public == True).select()
    return dict(links=links, public_links=public_links)


def handle_error():
    code = request.vars.code
    request_url = request.vars.request_url
    ticket = request.vars.ticket
    email_sender = config.config_mail_error_send()

    if code is not None and request_url != request.url:	# Make sure error url is not current url to avoid infinite loop.
        response.status = int(code) # Assign the error status code to the current response. (Must be integer to work.)
    if code == '403':
        return dict(message ="No autorizado", ticket_name=ticket, errorCode = code)
    elif code == '500':
		# Get ticket URL:
        ticket_url = "<a href='%(scheme)s://%(host)s/admin/default/ticket/%(ticket)s' target='_blank'>%(ticket)s</a>" % {'scheme':'https','host':request.env.http_host,'ticket':ticket}
		# Email a notice, etc:
        mail.send(to=[email_sender],
					subject="New Error 500",
					message="Error Ticket:  %s" % ticket_url)
		
        return dict(message ="Server error 500", ticket_name=ticket, errorCode = code)
    else:
        return dict(message ="Server Error", ticket_name=ticket, errorCode = code)

#esto estaba por defecto, habria que revisar si se puede eliminar
# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})

# ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)

# ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu() # add the wiki to the menu
    return auth.wiki() 

# ---- Action for login/register/etc (required for auth) -----
