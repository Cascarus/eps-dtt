import datetime
import cpfecys 
import csv
import xml.etree.ElementTree as ET
import allowed_career as validator_career
import codecs
import chardet

#CONSUME THE WEBSERVICE
from gluon.contrib.pysimplesoap.client import SoapClient
from gluon.contrib.pysimplesoap.client import SimpleXMLElement

#Mostrar el listado de estudiantes que han sido registrados en el sistema
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator'))
def academic():
    query = db.academic

    db.academic.id.writable = False
    db.academic.id.readable = False
    db.academic.email.readable = False
    db.academic.id_auth_user.readable = False
    db.academic.id_auth_user.writable = False

    if auth.has_membership('Super-Administrator'):
        db.academic.email.readable = True
        db.academic.email.writable = True

        #Modal photo
        def get_button_clas(carnet_pa):
            review = db((db.photo_review.user_id == carnet_pa)).select(db.photo_review.accepted).first()

            if review is None:
                photo = None
                # handle when there are no students or users in the database
                try:
                    photo = db(db.auth_user.id == carnet_pa).select(db.auth_user.photo).first().photo
                except AttributeError:
                    pass

                if photo is None:
                    class_button = 'btn btn-primary'
                else:
                    class_button = 'btn btn-info'
            else:
                if review.accepted:
                    class_button = 'btn btn-success'
                else:
                    class_button = 'btn btn-danger'

            return class_button

        links = [{
                    'header': 'Foto',
                    'body':lambda row: A(IMG(_src=URL('default/download', get_auth_user(row.id_auth_user).photo), _width=50, _height=40, _id='image'))      
                }]

        links += [
            lambda row: A(
                'Ver foto',
                _role='button', 
                _class=get_button_clas(row.id_auth_user), 
                _onclick=f'set_values("{row.id_auth_user}");', 
                _title='Ver foto',
                **{"_data-toggle": "modal", "_data-target": "#picModal"}
            )
        ]

        links += [
            lambda row: A(
                'Notificar',
                _role='button', 
                _class='btn btn-inverse btn-primary', 
                _href=URL('admin', 'active_teachers/mail', vars=dict(user=row.id_auth_user, next="academic")), 
                _title='Notificar'
            )
        ]   

        if 'edit' in request.args:
            db.academic.carnet.writable = False     

        grid = SQLFORM.grid(
            query,
            oncreate=oncreate_academic,
            links=links,
            onupdate=onupdate_academic,
            ondelete=ondelete_academic,
            maxtextlength=100,
            csv=False
        )
    else:
        db.academic.email.writable = False
        db.academic.email.default = "email@email.com"
        grid = SQLFORM.grid(
            query,
            oncreate=oncreate_academic,
            onupdate=onupdate_academic,
            ondelete=ondelete_academic,
            maxtextlength=100,
            csv=False,
            editable=False,
            deletable=False,
            details=False
        )

    return dict(grid=grid)

@auth.requires_login()
def photo():
    return dict(var="")

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator'))
def academic_assignation():
    #requires parameter year_period if no one is provided then it is 
    #automatically detected
    #and shows the current period
    assignation = request.vars['assignation']
    year_period = request.vars['year_period']
    project = request.vars['project']
    user = None
    max_display = 1

    currentyear_period = db.period_year(db.period_year.id == year_period)
    if auth.has_membership('Super-Administrator'):
        check = db(db.user_project.project == project).select(db.user_project.ALL).first()
        user = db(db.auth_user.id == check.assigned_user).select(db.auth_user.ALL).first()
        assignation = check.id
    else:
        if auth.has_membership('Super-Administrator'):
            check = db(db.user_project.project == project).select(db.user_project.ALL).first()
            user = db(db.auth_user.id == check.assigned_user).select(db.auth_user.ALL).first()
            assignation = check.id
        else:
            user = auth.user
            check = db.user_project(id=assignation, assigned_user=user.id)

    if not currentyear_period:
        currentyear_period = cpfecys.current_year_period()

    if check is None:
        #check if there is no assignation or if it is locked (shouldn't be touched)
        if session.last_assignation is None:
            redirect(URL('default', 'home'))
            return
        else:
            check = db.user_project(id=session.last_assignation)
            if cpfecys.assignation_is_locked(check):
                redirect(URL('default', 'home'))
                return
    else:
        session.last_assignation = check.id

    #Temporal---------------------------------------------------------------------------------------------
    if request.vars['listado'] == 'True':
        redirect(URL('student_academic', 'attendance_list', vars=dict(usuario_proyecto=str(check.id), project=project)))

    #Temporal---------------------------------------------------------------------------------------------
    if request.vars['search_var'] is None:
        query = ((db.academic_course_assignation.semester == currentyear_period.id) & (db.academic_course_assignation.assignation == check.project))
    else:
        query2 = db((db.academic_course_assignation.carnet == db.academic.id) & (db.academic_course_assignation.semester == currentyear_period.id) 
                    & (db.academic_course_assignation.assignation == check.project) & (db.academic.carnet.like(f"%{request.vars['search_var']}%"))).select(db.academic.id)
        #consultar a la base de datos para obtener a los usuarios a los que enviaremos
        query = (db.academic_course_assignation.carnet.belongs([element.id for element in query2]) & (db.academic_course_assignation.semester == currentyear_period.id) 
                & (db.academic_course_assignation.assignation == check.project))
    
    fields = (db.academic_course_assignation.carnet, db.academic_course_assignation.laboratorio)

    db.academic_course_assignation.assignation.default = check.project
    db.academic_course_assignation.assignation.writable = False
    db.academic_course_assignation.assignation.readable = False
    db.academic_course_assignation.semester.default = currentyear_period.id
    db.academic_course_assignation.semester.writable = False
    db.academic_course_assignation.semester.readable = False
    db.academic_course_assignation.carnet.readable = False
    db.academic_course_assignation.laboratorio.readable = False

    #update form start
    update_form = FORM(
        INPUT(_name='academic_carnet',_type='text'),
        INPUT(_name='laboratory_check',_type='checkbox'),
        INPUT(_name='assignation_id',_type='text'),
        INPUT(_name='laboratory_before',_type='text'),                        
        INPUT(_name='delete_check',_type='checkbox')
    )

    if update_form.accepts(request.vars, formname='update_form'):
        try:
            #Search for user roles
            results = db(db.auth_membership.user_id == user.id).select(db.auth_membership.group_id)
            roll_var = ','.join([result.group_id.role for result in results])
            var_labo = True if update_form.vars.laboratory_check == 'on' else False

            if update_form.vars.delete_check:
                var_aca = db(db.academic_course_assignation.id == update_form.vars.assignation_id).select(
                                db.academic_course_assignation.assignation,
                                db.academic_course_assignation.semester
                            ).first()
                if db(db.grades.academic_assignation == update_form.vars.assignation_id).select().first() is None:
                    db(db.academic_course_assignation.id == update_form.vars.assignation_id).delete()
                    db.academic_course_assignation_log.insert(
                        user_name=user.username, 
                        roll=roll_var, 
                        operation_log='delete', 
                        before_carnet=update_form.vars.academic_carnet, 
                        before_course=var_aca.assignation.name,
                        before_year=var_aca.semester.yearp,
                        before_semester=var_aca.semester.period.name,
                        before_laboratory=str(var_labo),
                        id_period=str(currentyear_period.id),
                        description=T('Registration is removed from the page students')
                    )
                    response.flash = T('Deleted register.')
                else:
                    response.flash = T('Can not be deleted because it has grades associated')
            else:
                if update_form.vars.laboratory_before != str(var_labo):
                    var_aca = db(db.academic_course_assignation.id == update_form.vars.assignation_id).select(
                                    db.academic_course_assignation.id,
                                    db.academic_course_assignation.carnet,
                                    db.academic_course_assignation.assignation,
                                    db.academic_course_assignation.semester
                                ).first()
                    dont_delete = False
                    if not var_labo:
                        grades = db(db.grades.academic_assignation == var_aca.id).select(db.grades.activity)
                        for g in grades:
                            if g.activity.laboratory:
                                dont_delete = True

                    if not dont_delete:
                        db(db.academic_course_assignation.id == update_form.vars.assignation_id).update(laboratorio=var_labo)
                        var_aca_carnet = str(var_aca.carnet.carnet)
                        var_aca_assignation = var_aca.assignation.name
                        var_aca_semester_yearp = str(var_aca.semester.yearp)
                        var_aca_semester_period = var_aca.semester.period.name
                        db.academic_course_assignation_log.insert(
                            user_name=user.username, 
                            roll=roll_var, 
                            operation_log='update', 
                            before_carnet=var_aca_carnet, 
                            before_course=var_aca_assignation,
                            before_year=var_aca_semester_yearp,
                            before_semester=var_aca_semester_period,
                            before_laboratory=update_form.vars.laboratory_before,
                            after_carnet=var_aca_carnet, 
                            after_course=var_aca_assignation,
                            after_year=var_aca_semester_yearp,
                            after_semester=var_aca_semester_period,
                            after_laboratory=str(var_labo),
                            id_academic_course_assignation=update_form.vars.assignation_id,
                            id_period=str(currentyear_period.id),
                            description=T('Registration modified from the page from students')
                        ) 
    
                        response.flash = T('Updated register.')
                    else:
                        response.flash = T('Can not be modify because it has grades associated')
        except:
            response.flash = T('Error.')
    #update form finish

    def get_photo_state(id_auth):
        review = db((db.photo_review.user_id == id_auth)).select(db.photo_review.accepted).first()
        if review is None:
            class temp:
                result = T('Pending')
                color = 'blue'
            return temp
        else:
            if review.accepted:
                class temp:
                    result = T('Accepted')
                    color = 'green'
                return temp
            else:
                class temp:
                    result = T('rejected')
                    color = 'red'
                return temp

    def has_foto(id_auth):
        var_return = db(db.auth_user.id == id_auth).select(db.auth_user.photo).first()
        if var_return is None:
            return -1
        else:
            if var_return.photo is None:
                return -1
            else:
                return id_auth

    current_period_var = False
    if (request.vars['year_period'] is None) or (request.vars['year_period'] == str(cpfecys.current_year_period().id)):
        current_period_var = True

    if current_period_var:
        links = [
            {
                'header': 'Foto', 
                'body': lambda row: A(
                    IMG(
                        _src=URL('default/download', get_auth_user((db(db.academic.id == int(row.carnet)).select(db.academic.id_auth_user).first().id_auth_user)).photo), 
                        _width=50, _height=40, _id='image'
                    ), 
                    _style="cursor: pointer;",
                    _onclick=f'set_photo("{db(db.academic.id == int(row.carnet)).select(db.academic.id_auth_user).first().id_auth_user}");', 
                    _title='Ver foto',
                    **{"_data-toggle": "modal", "_data-target": "#picModal"}
                ) 
            }
        ]
    else:
        links = [
            {
                'header': 'Foto', 
                'body': lambda row: A(
                    IMG(
                        _src=URL('default/download', get_auth_user((db(db.academic.id == int(row.carnet)).select(db.academic.id_auth_user).first().id_auth_user)).photo), 
                        _width=50, _height=40, _id='image'
                    )
                )      
            }
        ]

    links += [{
        'header': 'Carnet', 
        'body':lambda row: str(db(db.academic.id == int(row.carnet)).select(db.academic.carnet).first().carnet)
    }]

    links += [{
        'header': 'Nombre', 
        'body':lambda row: f"{get_auth_user((db(db.academic.id == int(row.carnet)).select(db.academic.id_auth_user).first().id_auth_user)).first_name} {get_auth_user((db(db.academic.id == int(row.carnet)).select(db.academic.id_auth_user).first().id_auth_user)).last_name}"
    }]

    links += [{
        'header': 'Email', 
        'body': lambda row: (str(db(db.academic.id == int(row.carnet)).select(db.academic.email).first().email))
    }]

    links += [{
        'header': 'Laboratorio', 
        'body':lambda row: T(str(row.laboratorio))
    }] 

    if current_period_var:
        links += [{
            'header': 'Estado de la foto', 
            'body':lambda row: A(
                get_photo_state((db(db.academic.id == int(row.carnet)).select(db.academic.id_auth_user).first().id_auth_user)).result,
                _id=f"label_{db(db.academic.id == int(row.carnet)).select(db.academic.id_auth_user).first().id_auth_user}",
                _style=f"cursor:pointer; color: {get_photo_state((db(db.academic.id == int(row.carnet)).select(db.academic.id_auth_user).first().id_auth_user)).color};",
                _onclick=f'set_photo("{db(db.academic.id == int(row.carnet)).select(db.academic.id_auth_user).first().id_auth_user}");',
                **{"_data-toggle": "modal", "_data-target": "#picModal"}
            )
        }] 

        links += [{
            'header': 'Asignación', 
            'body': lambda row: A(
                'Editar', 
                _role='button', 
                _class='btn btn-primary', 
                _onclick=f'set_values({row.id}, {db(db.academic.id == int(row.carnet)).select(db.academic.carnet).first().carnet}, '\
                        + f'"{db(db.academic.id == int(row.carnet)).select(db.academic.email).first().email}", "{row.laboratorio}")', 
                _title=f'Editar asignación {db(db.academic.id == int(row.carnet)).select(db.academic.carnet).first().carnet}',
                **{"_data-toggle":"modal", "_data-target": "#attachModal"}
            )
        }]
    
        links += [
            lambda row: A(
                'Aceptar foto',
                _class="btn btn-success",
                _onclick=f"click_acept_photo({has_foto(db(db.academic.id == int(row.carnet)).select(db.academic.id_auth_user).first().id_auth_user)})"
            )
        ]

        links += [
            lambda row: A(
                'Rechazar foto',
                _class="btn btn-danger",
                _onclick=f"click_reject_photo({has_foto(db(db.academic.id == int(row.carnet)).select(db.academic.id_auth_user).first().id_auth_user)})"
            )
        ]

    permition_var = True
    date_finish = None
    if auth.has_membership('Student'):
        control_period = db((db.student_control_period.period_name == f"{T(str(cpfecys.current_year_period().period.name))} {cpfecys.current_year_period().yearp}")).select(
                                db.student_control_period.date_finish,
                                db.student_control_period.date_start
                            ).first()
        try:
            date_finish = control_period.date_finish
            if ((datetime.datetime.now() < control_period.date_start) | (datetime.datetime.now() > control_period.date_finish)):
                except_var = False            
                for course_exception in db(db.course_limit_exception.project == check.project).select(db.course_limit_exception.date_finish):
                    if (datetime.datetime.now() < course_exception.date_finish):
                        date_finish = course_exception.date_finish
                        except_var = True

                if not except_var:
                    date_finish = None
                    permition_var = False
        except:
            permition_var = False

    if ((currentyear_period.id == cpfecys.current_year_period().id) & (permition_var)):
        grid = SQLFORM.grid(
                query,
                orderby=db.academic_course_assignation.carnet,
                details=False,
                fields=fields,
                links=links,
                oncreate=oncreate_academic_assignation,
                onupdate=onupdate_academic_assignation,
                ondelete=ondelete_academic_assignation,
                csv=False,
                deletable=False,
                editable=False,
                paginate=100,
                advanced_search=True
            )
    else:
        check_project = db((db.user_project.assigned_user == user.id) & (db.user_project.project == check.project)
                        & ((db.user_project.period <= currentyear_period.id) & ((db.user_project.period.cast('integer') + db.user_project.periods) > currentyear_period.id))).count()
        if check_project != 0:
            grid = SQLFORM.grid(query, details=False, fields=fields, links=links, deletable=False, editable=False, create=False, csv=False, paginate=100)
        else:
            session.flash = T('Not authorized')
            redirect(URL('default','home'))

    current_period_name = T(cpfecys.second_period.name)
    if currentyear_period.period == cpfecys.first_period.id:
        current_period_name = T(cpfecys.first_period.name)
    start_index = currentyear_period.id - max_display - 1
    if start_index < 1:
        start_index = 0
    end_index = currentyear_period.id + max_display
    #emarquez: 06sept, adaptacion periodos variables
    if cpfecys.is_semestre(request.vars['year_period']):
        periods_before = db((db.period_year.period == '1') | (db.period_year.period == '2')).select(limitby=(start_index,  currentyear_period.id - 1))
        periods_after = db((db.period_year.period == '1') | (db.period_year.period == '2')).select(limitby=(currentyear_period.id, end_index))
        other_periods = db((db.period_year.period == '1') | (db.period_year.period == '2')).select()
    else:
        periods_before = db(db.period_year).select(limitby=(start_index, currentyear_period.id - 1))
        periods_after = db(db.period_year).select(limitby=(currentyear_period.id, end_index))
        other_periods = db(db.period_year).select()

    #verificacion si es periodo variable para cambiar el current period name
    if not cpfecys.is_semestre(request.vars['year_period']):
        var_period = db((db.period.id == db.period_year.period) & (db.period_year.id == request.vars['year_period'])).select(db.period.period).first()
        current_period_name = var_period.period.name

    return dict(
        grid=grid,
        currentyear_period=currentyear_period,
        current_period_name=current_period_name,
        periods_before=periods_before,
        periods_after=periods_after,
        other_periods=other_periods,
        name=check.project.name,
        check=check,
        assignation=check.id,
        date_finish=date_finish,
        cperiod=cpfecys.current_year_period(),
        project=project
    )

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator'))
def academic_assignation_upload():
    def files():
        f = db(db.uploaded_file.name == 'CargaEstudiantes_TutoresAcademicos').select(db.uploaded_file.file_data)
        nameP = ''
        for p2 in f:
            nameP = p2.file_data
        return nameP

    assignation = request.vars['assignation']
    project = request.vars['project']
    if auth.has_membership('Super-Administrator'):
        check = db(db.user_project.project == project).select(
                    db.user_project.assigned_user,
                    db.user_project.id,
                    db.user_project.project
                ).first()
        user = db(db.auth_user.id == check.assigned_user).select(db.auth_user.id, db.auth_user.username).first()
        assignation = check.id
    else:
        user = auth.user
        check = db((db.user_project.id == assignation) & (db.user_project.assigned_user == user.id)).select(
                    db.user_project.assigned_user,
                    db.user_project.id,
                    db.user_project.project
                ).first()

    name = check.project.name
    error_users = []
    aviso_users = []
    success = False
    current_period = cpfecys.current_year_period()

    #Emarquez: enviando parametro de periodo, para que soporte periodos variables
    date_finish = None
    set_periodo = request.vars['year_period'] or False
    if set_periodo:
        current_period = db(db.period_year.id == set_periodo).select().first()
       #Emarquez: fin.s

    if request.vars.csvfile is not None:
        try:
            file = request.vars.csvfile.file
        except AttributeError:
            response.flash = T('Please upload a file.')
            return dict(
                success=False,
                file=False,
                periods=periods,
                current_period=current_period,
                name=name,
                files=files,
                date_finish=date_finish
            )
        try:
            try:
                content_file = file.read()
                detection = chardet.detect(content_file)['encoding']
                content_file = content_file.decode(detection).splitlines()
            except:
                content_file = []

            cr = csv.reader(content_file, dialect=csv.excel_tab, delimiter=',', quotechar='"')
            try:
                success = True
                next(cr) #Evita leer la cabecera del archivo
            except:
                response.flash = T('File doesn\'t seem properly encoded.'+ AttributeError)
                return dict(
                    success=False,
                    file=False,
                    periods=periods,
                    current_period=current_period,
                    name=name,
                    files=files,
                    date_finish=date_finish
                )
            for row in cr:
                ## parameters
                rcarnet = row[0]
                rlaboratorio = row[1].upper()

                ## check if user exists                
                if auth.has_membership('Super-Administrator'):
                    check = db(db.user_project.project == project).select(db.user_project.project).first()
                else:
                    check = db((db.user_project.id == assignation) & (db.user_project.assigned_user == user.id)).select(db.user_project.project).first()
                usr = db(db.academic.carnet == rcarnet).select(db.academic.id).first()        
                if usr is None:
                    #Email validation        
                    if rcarnet == '':
                        row.append('Error: El carnet es un campo obligatorio.')
                        error_users.append(row)
                    else:            
                        #T o F validation
                        if rlaboratorio == 'TRUE':
                            rlaboratorio = 'T'
                        elif rlaboratorio == 'FALSE':
                            rlaboratorio = 'F'

                        if rlaboratorio != 'T' and rlaboratorio != 'F':
                            row.append('Error: El tipo de laboratorio ingresado no es correcto. Este debe ser T o F.')
                            error_users.append(row)
                        else:
                            #insert a new user with csv data
                            session.academic_update = True
                            usr = db.academic.insert(carnet=rcarnet, email="email@email.com")
                            #Add log
                            db.academic_log.insert(
                                user_name=user.username, 
                                roll='Student', 
                                operation_log='insert', 
                                after_carnet=rcarnet, 
                                after_email="email@email.com", 
                                id_academic=usr.id,
                                id_period=current_period.id,
                                description='Inserted from CSV file.'
                            )
                            #add user to the course
                            ingresado = db.academic_course_assignation.insert(
                                            carnet=usr.id,
                                            semester=current_period,
                                            assignation=check.project,
                                            laboratorio=rlaboratorio
                                        )
                            #Add to log
                            lab_var = 'True' if rlaboratorio == 'T' else 'False'
                            #Search for user roles
                            results = db(db.auth_membership.user_id == user.id).select(db.auth_membership.group_id)
                            roll_var = ','.join([result.group_id.role for result in results])
                            db.academic_course_assignation_log.insert(
                                user_name=user.username,
                                roll=roll_var, 
                                operation_log='insert', 
                                after_carnet=rcarnet, 
                                after_course=str(check.project.name), 
                                after_year=str(current_period.yearp) ,
                                after_semester=str(current_period.period),
                                after_laboratory=lab_var,
                                id_academic_course_assignation=str(ingresado.id),
                                id_period=current_period.id,
                                description='Inserted from CSV file.'
                            )

                            try:
                                for var_error in session.assignation_error:
                                    var_ac = db(db.academic.carnet == var_error[0]).select(db.academic.email).first()
                                    db(db.academic.carnet == var_error[0]).delete()
                                    results = db(db.auth_membership.user_id == user.id).select(db.auth_membership.group_id)
                                    roll_var = ','.join([result.group_id.role for result in results])

                                    db.academic_log.insert(
                                        user_name=user.username, 
                                        roll=roll_var, 
                                        operation_log='delete', 
                                        before_carnet=str(var_error[0]), 
                                        before_email=str(var_ac.email), 
                                        id_period=str(current_period.id),
                                        description='Se eliminó el registro debido a que no paso la validacion con webservice'
                                    )
                            except:
                                None
                            if session.assignation_error is None:
                                #Agregar la advertencia que el usuario ya se encuentra registrado en el sistema
                                row.append('Aviso: Asignación exitosa al curso')
                                aviso_users.append(row)
                            else:
                                for var_error in session.assignation_error:
                                    row.append(f'Error: {var_error[1]}')
                                    error_users.append(row)
                            session.academic_update = None
                            session.assignation_error = None                                
                else:
                    usr2 = db((db.academic_course_assignation.semester == current_period) & (db.academic_course_assignation.assignation == check.project) 
                            & (db.academic_course_assignation.carnet == usr.id)).select().first()
                    if usr2 is None:
                        #T o F validation
                        if rlaboratorio == 'TRUE':
                            rlaboratorio = 'T'
                        elif rlaboratorio == 'FALSE':
                            rlaboratorio = 'F'

                        if rlaboratorio != 'T' and rlaboratorio != 'F':
                            row.append('Error: El tipo de laboratorio ingresado no es correcto. Este debe ser T o F.')
                            error_users.append(row)
                        else:
                            lab_var = ''
                            if rlaboratorio == 'T':
                                lab_var = 'True'
                            else:
                                lab_var = 'False'

                            #Search for user roles
                            results = db(db.auth_membership.user_id == user.id).select(db.auth_membership.group_id)
                            roll_var = ','.join([result.group_id.role for result in results])

                            #Agregar la advertencia que el usuario ya se encuentra registrado en el sistema
                            row.append('Aviso: Asignación exitosa al curso, el estudiante ya se encuentra registrado en el sistema')

                            ingresado = db.academic_course_assignation.insert(
                                            carnet=usr.id,
                                            semester=current_period,
                                            assignation=check.project,
                                            laboratorio=rlaboratorio
                                        )
                            db.academic_course_assignation_log.insert(
                                user_name=user.username,
                                roll=roll_var, 
                                operation_log='insert', 
                                after_carnet=rcarnet, 
                                after_course=str(check.project.name), 
                                after_year=str(current_period.yearp) ,
                                after_semester=str(current_period.period),
                                after_laboratory=lab_var,
                                id_academic_course_assignation=str(ingresado.id),
                                id_period=current_period.id,
                                description='Inserted from CSV file.'
                            )
                            aviso_users.append(row)
                    else:
                        try:
                            row.remove('Aviso: El estudiante ya se encuentra registrado en el sistema')
                        except:
                            None
                        row.append('Error: El estudiante ya se encuentra registrado en el sistema y asignado al curso')
                        error_users.append(row)
                    continue
        except AttributeError:
            response.flash = T('File doesn\'t seem properly encoded.'+ AttributeError)
            return dict(
                success=False,
                file=False,
                periods=periods,
                current_period=current_period,
                name=name,
                files=files,
                date_finish=date_finish
            )
        response.flash = T('Data uploaded')
        return dict(
            success=success,
            errors=error_users,
            avisos=aviso_users,
            periods=periods,
            current_period=current_period,
            name=name,
            files=files
        )

    permition_var = True
    date_finish = None
    if auth.has_membership('Student'):
        if cpfecys.is_semestre(request.vars['year_period']):
            control_period = db((db.student_control_period.period_name == f'{T(cpfecys.current_year_period().period.name)} {cpfecys.current_year_period().yearp}')).select().first()
            try:
                date_finish = control_period.date_finish
                if ((datetime.datetime.now() < control_period.date_start) | (datetime.datetime.now() > control_period.date_finish)):
                    except_var = False
                    for course_exception in db(db.course_limit_exception.project == check.project).select():
                        if (datetime.datetime.now() < course_exception.date_finish):
                            date_finish = course_exception.date_finish
                            except_var = True
                    if not except_var:
                        permition_var = False
            except:
                permition_var = False
        else:
            control_period = db(db.period_detail.period == current_period.period).select(db.period_detail.date_finish, db.period_detail.date_start).first()
            try:
                date_finish = control_period.date_finish
                if ((datetime.datetime.now() < control_period.date_start) | (datetime.datetime.now() > control_period.date_finish)):
                    except_var = False
                    for course_exception in db(db.course_limit_exception_period.project == check.project).select():
                        if (datetime.datetime.now() < course_exception.date_finish):
                            date_finish = course_exception.date_finish
                            except_var = True
                    if not except_var:
                        permition_var = False
            except:
                permition_var = False

    return dict(
        success=False,
        file=False,
        periods=periods,
        current_period=current_period,
        name=name,
        files=files,
        permition_var=permition_var,
        date_finish=date_finish
    )

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher'))
def attendance_list():
    if request.vars['list'] is not None:
        academic_var = db(db.auth_group.role == 'Academic').select(db.auth_group.id).first()
        academic_list = db((db.academic_course_assignation.semester == request.vars['period']) & (db.academic_course_assignation.assignation == request.vars['project'])).select(
                            db.academic_course_assignation.carnet
                        )
        for academic_temp in academic_list:
            user_var = db(db.auth_user.username == academic_temp.carnet.carnet).select(
                            db.auth_user.id,
                            db.auth_user.email,
                            db.auth_user.username
                        ).first()
            if user_var is None:
                #WEBSERVICE
                web_service = check_student(academic_temp.carnet.carnet)
                if web_service['flag']:
                    id_user = db.auth_user.insert(
                                first_name=web_service['nombres'],
                                last_name=web_service['apellidos'],
                                email=web_service['correo'],
                                username=academic_temp.carnet.carnet,
                                phone='12345678',
                                home_address=T('Enter your address')
                            )
                    #Add the id_auth_user to academic.
                    db(db.academic.id == academic_temp.carnet.id).update(id_auth_user=id_user.id)
                    #Create membership to academic
                    db.auth_membership.insert(user_id=id_user.id, group_id=academic_var.id)
                    message = [] 
                    message.append(academic_temp.carnet.carnet)
                    message.append(T('Profile was created successfully'))
                    if session.assignation_message is None:
                        session.assignation_message = []
                        session.assignation_message.append(message)
                    else:
                        session.assignation_message.append(message)  
                else:
                    message = [] 
                    message.append(academic_temp.carnet.carnet)
                    message.append(web_service['message'])
                    if session.assignation_error is None:
                        session.assignation_error = []
                        session.assignation_error.append(message)
                    else:
                        session.assignation_error.append(message)

                    if not web_service['error']:
                        db(db.academic.id == academic_temp.carnet.id).delete()

                        results = db(db.auth_membership.user_id == auth.user.id).select()
                        roll_var = ','.join([result.group_id.role for result in results])
                        currentyear_period = cpfecys.current_year_period()
                        db.academic_log.insert(
                            user_name=auth.user.username, 
                            roll=roll_var, 
                            operation_log='delete', 
                            before_carnet=academic_temp.carnet.carnet, 
                            before_email=academic_temp.carnet.email, 
                            id_period=str(currentyear_period.id),
                            description=T('The record was removed because it failed the webservice validation')
                        )
            else:
                message = [] 
                message.append(academic_temp.carnet.carnet)
                message.append(T('The student profile was already created'))
                if session.assignation_message is None:
                    session.assignation_message = []
                    session.assignation_message.append(message)
                else:
                    session.assignation_message.append(message)

                membership_var = db((db.auth_membership.user_id == user_var.id) & (db.auth_membership.group_id == academic_var.id)).select(db.auth_membership.id).first()
                if membership_var is None:
                    #Create membership to academic
                    db.auth_membership.insert(user_id=user_var.id, group_id=academic_var.id) 

                #Add the id_auth_user to academic. And update academic inforamtion  
                db(db.academic.id == academic_temp.carnet.id).update(
                    id_auth_user=user_var.id,
                    email=user_var.email,
                    carnet=user_var.username
                )
                
                #academic_LOG 
                cperiod = cpfecys.current_year_period()
                db.academic_log.insert(
                    user_name='system',
                    roll='system',
                    operation_log='update', 
                    before_carnet=academic_temp.carnet.carnet, 
                    before_email=academic_temp.carnet.email, 
                    after_carnet=user_var.username, 
                    after_email=user_var.email, 
                    id_academic=academic_temp.carnet.id, 
                    id_period=cperiod,
                    description=f"{T('Registration data was updated, set with the information entered by ')}{auth.user.username}"
                )
        session.flash = T('Profiles created')
        redirect(URL('student_academic', 'academic_assignation',  vars=dict(assignation=str(request.vars['project']))))
    else:
        if request.vars['usuario_proyecto'] is not None:
            check = db((db.user_project.id == request.vars['usuario_proyecto']) & (db.user_project.assigned_user == auth.user.id)).select(
                        db.user_project.project,
                        db.user_project.period
                    ).first()
            project = db(db.project.id == check.project).select(db.project.id, db.project.project_id, db.project.name).first()
            periodo = db(db.period_year.id == check.period).select(db.period_year.id, db.period_year.period, db.period_year.yearp).first()
            alumnos = db((db.academic.id == db.academic_course_assignation.carnet) & (db.academic_course_assignation.assignation == project.id)
                    & (db.academic_course_assignation.semester == periodo.id) &(db.auth_user.id == db.academic.id_auth_user)).select(
                        db.academic_course_assignation.laboratorio,
                        db.auth_user.first_name,
                        db.auth_user.last_name,
                        db.academic.carnet,
                        db.academic.email
                    )

            listado = []
            listado.append(['Lista de asistencia'])
            listado.append([project.project_id, project.name, f'{T(periodo.period.name)} {periodo.yearp}'])
            listado.append([None])
            listado.append(['Carnet', 'Nombre', 'Email', 'Laboratorio'])

            for alumno in alumnos:
                lab = 'No' if not alumno.academic_course_assignation.laboratorio else 'Si'
                nombre = f'{alumno.auth_user.first_name} {alumno.auth_user.last_name}'
                listado.append([alumno.academic.carnet, nombre, alumno.academic.email, lab])

            return dict(csvdata=listado)
        else:
            redirect(URL('default', 'home'))

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher'))
def student_courses():
    def split_name(project):
        try:
            (name_p, _) = str(project).split('(')
        except:
            name_p = project
        return name_p

    def split_section(project):
        try:
            project_section = None
            name_s = None
            (_, project_section) = str(project).split('(')
            (name_s, _) = str(project_section).split(')')
        except:
            name_s = '--------'
        return name_s
    
    year = cpfecys.current_year_period()
    assignation = db((db.user_project.assigned_user == auth.user.id) & ((db.user_project.period <= year.id) 
                    & ((db.user_project.period.cast('integer') + db.user_project.periods) > year.id))).select(db.user_project.ALL).first()
    
    return dict(assignations=assignation, split_name=split_name, split_section=split_section)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def student_validation_parameters():
    svp = db(db.validate_student).select(db.validate_student.id).first()
    db.validate_student.id.writable = False
    db.validate_student.id.readable = False
    if svp is None:
        grid = SQLFORM.grid(db.validate_student, csv=False, paginate=1, searchable=False)
    else:
        links = [lambda row: A(
            T('Web Service Parameters'),
            _role='label',
            _href=URL('student_academic', 'student_validation_parameters_fields'),
            _title=T('Web Service Parameters')
        )]
        grid = SQLFORM.grid(db.validate_student, csv=False, paginate=1, create=False, searchable=False, links=links)
    
    return dict(grid=grid)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def student_validation_parameters_fields():
    svp = db(db.validate_student).select(db.validate_student.id).first()
    if svp is not None:
        db.validate_student_parameters.validate_student.default = svp.id
        db.validate_student_parameters.validate_student.writable = False
        db.validate_student_parameters.validate_student.readable = False
        grid = SQLFORM.grid(db.validate_student_parameters, csv=False)
        return dict(grid=grid)
    else:
        session.flash = T('Not valid Action.')
        redirect(URL('default','home'))

def oncreate_academic(form):
    currentyear_period = cpfecys.current_year_period()

    #Search for user roles
    results = db(db.auth_membership.user_id == auth.user.id).select(db.auth_membership.group_id)
    roll_var = ','.join([result.group_id.role for result in results])
    
    db.academic_log.insert(
        user_name=auth.user.username, 
        roll=roll_var, 
        operation_log='insert', 
        after_carnet=form.vars.carnet, 
        after_email="email@email.com", 
        id_academic=form.vars.id, 
        id_period=str(currentyear_period.id),
        description='Se agrego registro desde la pagina agregar estudiantes.'
    )

def onupdate_academic(form):
    currentyear_period = cpfecys.current_year_period()
    
    #Search for user roles
    results = db(db.auth_membership.user_id == auth.user.id).select(db.auth_membership.group_id)
    roll_var = ','.join([result.group_id.role for result in results])

    student_var = db(db.academic_log.id_academic == form.vars.id).select(db.academic_log.after_carnet, db.academic_log.after_email, orderby=db.academic_log.id)
    carnet_var = ''
    email_var = ''
    for a in student_var:
        carnet_var = a.after_carnet
        email_var = a.after_email
    
    if form.vars.delete_this_record is None:
        db.academic_log.insert(
            user_name=auth.user.username, 
            roll=roll_var, 
            operation_log='update', 
            before_carnet=carnet_var, 
            before_email=email_var, 
            after_carnet=form.vars.carnet, 
            after_email=form.vars.email, 
            id_academic=form.vars.id, 
            id_period=str(currentyear_period.id),
            description='Se modificó registro desde la página estudiantes'
        )
    else:
        db.academic_log.insert(
            user_name=auth.user.username, 
            roll=roll_var, 
            operation_log='delete', 
            before_carnet=carnet_var, 
            before_email=email_var, 
            after_email='',
            after_carnet='',
            id_period=str(currentyear_period.id),
            description='Se modificó registro desde la página estudiantes'
        )

def ondelete_academic(_, id_of_the_deleted_record):
    currentyear_period = cpfecys.current_year_period()
    student_var = db(db.academic.id == id_of_the_deleted_record).select(db.academic.carnet, db.academic.email).first()    

    #Search for user roles
    results = db(db.auth_membership.user_id == auth.user.id).select(db.auth_membership.group_id)
    roll_var = ','.join([result.group_id.role for result in results])   

    db.academic_log.insert(
        user_name=auth.user.username, 
        roll=roll_var, 
        operation_log='delete', 
        before_carnet=student_var.carnet, 
        before_email=student_var.email, 
        after_email='',
        after_carnet='',
        id_period=str(currentyear_period.id),
        description='Se modificó registro desde la página estudiantes'
    )

def get_auth_user(id_auth):
    var_return = db(db.auth_user.id == id_auth).select(db.auth_user.photo, db.auth_user.first_name, db.auth_user.last_name).first()
    if var_return is None:
        class temp:
            photo = ''
            first_name = ''
            last_name = ''
        return temp
    else:
        return var_return

def oncreate_academic_assignation(form):
    assignation = request.vars['assignation']
    currentyear_period = cpfecys.current_year_period()

    check = db((db.user_project.id == assignation) & (db.user_project.assigned_user == auth.user.id)).select(db.user_project.id, db.user_project.project).first()
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

    #Search for user roles
    results = db(db.auth_membership.user_id == auth.user.id).select(db.auth_membership.group_id)
    roll_var = ','.join([result.group_id.role for result in results])

    student_var = db(db.academic.id == form.vars.carnet).select(db.academic.carnet)
    carnet_var = ''
    for a in student_var:
        carnet_var = a.carnet

    #Check that there is not an assignation
    usr2 = db((db.academic_course_assignation.id != form.vars.id) & (db.academic_course_assignation.semester == currentyear_period.id)
            & (db.academic_course_assignation.assignation == check.project) & (db.academic_course_assignation.carnet == form.vars.carnet)).count()
    if usr2 == 0: 
        #If there is not an assignation update the log
        session.flash = T('Se realizó la asignación')
        db.academic_course_assignation_log.insert(
            user_name=auth.user.username, 
            roll=roll_var, 
            operation_log='insert', 
            after_carnet=carnet_var, 
            after_course=check.project.name,
            after_year=str(currentyear_period.yearp),
            after_semester=str(currentyear_period.period),
            after_laboratory=form.vars.laboratorio,
            id_academic_course_assignation=form.vars.id,
            id_period=str(currentyear_period.id),
            description='Se creo el registro desde la pagina Asignar Estudiantes'
        )
    else:
        #If there is an assignation delete the last record
        db(db.academic_course_assignation.id == form.vars.id).delete()
        session.flash = T('Error: Ya existe la asignacion')

def onupdate_academic_assignation(form):
    assignation = request.vars['assignation']
    currentyear_period = cpfecys.current_year_period()

    check = db((db.user_project.id == assignation) & (db.user_project.assigned_user == auth.user.id)).select(
                db.user_project.id,
                db.user_project.project
            ).first()
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

    #Search for user roles
    results = db(db.auth_membership.user_id == auth.user.id).select(db.auth_membership.group_id)
    roll_var = ','.join([result.group_id.role for result in results])

    #Search for carnet
    student_var = db(db.academic.id == form.vars.carnet).select(db.academic.carnet)
    carnet_var = ''
    for a in student_var:
        carnet_var = a.carnet

    #Search for before values
    student_var2 = db(db.academic_course_assignation_log.id_academic_course_assignation == form.vars.id).select(
                        db.academic_course_assignation_log.after_carnet,
                        db.academic_course_assignation_log.after_course,
                        db.academic_course_assignation_log.after_year,
                        db.academic_course_assignation_log.after_semester,
                        db.academic_course_assignation_log.after_laboratory,
                        orderby=db.academic_course_assignation_log.id
                    )
    bef_carnet_var = ''
    course_var = ''
    year_var = ''
    semester_var = ''
    laboratory_var = ''
    for a in student_var2:
        bef_carnet_var = a.after_carnet
        course_var = a.after_course
        year_var = a.after_year
        semester_var = a.after_semester
        laboratory_var = a.after_laboratory
    if form.vars.delete_this_record is not None:
        db.academic_course_assignation_log.insert(
            user_name=auth.user.username, 
            roll=roll_var, 
            operation_log='delete', 
            before_carnet=bef_carnet_var, 
            before_course=course_var,
            before_year=year_var,
            before_semester=semester_var,
            before_laboratory=laboratory_var,
            id_period=str(currentyear_period.id),
            description='Se elimino el registro desde la pagina Asignar Estudiantes'
        )
    else:
        #Check that there is not an assignation
        usr2 = db((db.academic_course_assignation.id != form.vars.id) & (db.academic_course_assignation.semester == currentyear_period.id) 
                & (db.academic_course_assignation.assignation == check.project) & (db.academic_course_assignation.carnet == form.vars.carnet)).count()
        if usr2 == 0: 
            #If there is not an assignation update the log
            session.flash = T('Se realizó la modificacion')
            db.academic_course_assignation_log.insert(
                user_name=auth.user.username, 
                roll=roll_var, 
                operation_log='update', 
                before_carnet=bef_carnet_var, 
                before_course=course_var,
                before_year=year_var,
                before_semester=semester_var,
                before_laboratory=laboratory_var,
                after_carnet=carnet_var, 
                after_course=check.project.name,
                after_year=str(currentyear_period.yearp) ,
                after_semester=str(currentyear_period.period),
                after_laboratory=form.vars.laboratorio,
                id_academic_course_assignation=form.vars.id,
                id_period=str(currentyear_period.id),
                description='Se modifico el registro desde la pagina Asignar Estudiantes'
            )
        else:
            #If there is an assignation delete the last record
            temp_academic = db(db.academic.carnet == bef_carnet_var).select(db.academic.id)
            id_academic = ''
            for a in temp_academic:
                id_academic = a.id
            db(db.academic_course_assignation.id == form.vars.id).update(carnet=id_academic, laboratorio=laboratory_var)
            session.flash = T('Error: Ya existe la asignacion, no se modifico el estudiante')

def ondelete_academic_assignation(_, id_of_the_deleted_record):
    student_assignation_var = db.academic_course_assignation(id_of_the_deleted_record)  
    currentyear_period = cpfecys.current_year_period()

    #Search for user roles
    results = db(db.auth_membership.user_id == auth.user.id).select(db.auth_membership.group_id)
    roll_var = ','.join([result.group_id.role for result in results])

    db.academic_course_assignation_log.insert(
        user_name=auth.user.username, 
        roll=roll_var, 
        operation_log='delete', 
        before_carnet=student_assignation_var.carnet.carnet, 
        before_course=student_assignation_var.assignation.name,
        before_year=str(student_assignation_var.semester.yearp) ,
        before_semester=str(student_assignation_var.semester.period),
        before_laboratory=student_assignation_var.laboratorio,
        id_period=str(currentyear_period.id),
        description='Se elimino el registro desde la pagina Asignar Estudiantes'
    )

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher'))
def periods():
    grid = SQLFORM.grid(db.period_year)
    return locals()

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher'))
def example_upload():
    #FILE
    info_level = []

    #HEADER OF FILE
    info_level.append(['Carnet', 'Laboratorio'])

    #BODY OF FILE
    info_level.append(['200000001', 'T'])
    info_level.append(['200000002', 'F'])

    return dict(csvdata=info_level)

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def check_student(check_carnet):
    svp = db(db.validate_student).select(
                db.validate_student.supplier,
                db.validate_student.action_service,
                db.validate_student.type_service,
                db.validate_student.send,
                db.validate_student.receive
            ).first()
    if svp is not None:
        try:
            client = SoapClient(
                location=svp.supplier,
                action=f'{svp.supplier}/{svp.action_service}',
                namespace=svp.supplier,
                soap_ns=svp.type_service,
                trace=True,
                ns=False
            )

            year = cpfecys.current_year_period()
            sent = f"<{svp.send}>"
            svpfs = db(db.validate_student_parameters).select(
                        db.validate_student_parameters.parameter_name_validate,
                        db.validate_student_parameters.parameter_value_validate,
                    )
            for svpf in svpfs:
                sent += f"<{svpf.parameter_name_validate}>{svpf.parameter_value_validate}</{svpf.parameter_name_validate}>"
            sent += f"<CARNET>{check_carnet}</CARNET><CICLO>{year.yearp}</CICLO></{svp.send}>"

            back = client.call(svp.action_service, xmlDatos=sent)
            #PREPARE FOR RETURNED XML WEB SERVICE
            xml = back.as_xml()
            xml = xml.decode('utf-8')
            xml = xml.replace('&lt;', '<')
            xml = xml.replace('&gt;', '>')
            inicio = xml.find(f"<{svp.receive}>")
            final = xml.find(f"</{svp.receive}>")
            xml = xml[inicio : (final + len(f'</{svp.receive}>'))]

            root = ET.fromstring(xml)
            xml = SimpleXMLElement(xml)

            #VARIABLE TO CHECK THE CORRECT FUNCTIONING
            CARNET = xml.CARNET
            NOMBRES = xml.NOMBRES
            APELLIDOS = xml.APELLIDOS
            CORREO = xml.CORREO

            #Unicode Nombres
            def get_real_values(text):
                text_return = ''
                try:
                    for word in str(text).split(' '):
                        word = word.replace('Ã¡','á').replace('Ã©','é').replace('Ã­','í').replace('Ã³','ó').replace('Ãº','ú').replace('Ã±','ñ').replace('Ã','Á').replace('Ã‰','É').replace('Ã','Í').replace('Ã“','Ó').replace('Ãš','Ú').replace('Ã‘','Ñ').replace('Ã¼‘','ü')
                        text_return += f'{word} '
                    return text_return.strip()
                except:
                    return text_return
            
            NOMBRES = get_real_values(NOMBRES)
            APELLIDOS = get_real_values(APELLIDOS)

            if (CARNET is None or CARNET == '') and (NOMBRES is None or NOMBRES == '') and (APELLIDOS is None or APELLIDOS == '') and (CORREO is None or CORREO == ''):
                return dict(flag=False, error=False, message=T('The record was removed because the user is not registered to the academic cycle'))
            else:
                val = validator_career.validar(db)
                is_student = False
                for c in root.findall('CARRERA'):
                    unidad = c.find('UNIDAD').text
                    extension = c.find('EXTENSION').text
                    carrera = c.find('CARRERA').text
                    is_student = val(unidad=unidad, extension=extension, carrera=carrera)
                    if is_student:
                        break

                if not is_student:
                    return dict(flag=False, error=False, message=T('The record was removed because students not enrolled in career allowed to use the system'))
                else:
                    return dict(flag=True, carnet=int(str(CARNET)), nombres=NOMBRES, apellidos=APELLIDOS, correo=str(CORREO), error=False)
        except Exception as e:
            return dict(flag=False, error=True, message=T('Error with web service validation'))
    else:
        return dict(flag=False, error=True, message=T('Error with web service validation 2'))