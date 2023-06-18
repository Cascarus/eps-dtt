#***********************************************************************************************************************
#******************************************************PHASE 2 DTT******************************************************
import math
import datetime
import cpfecys
import gluon.contenttype as contenttype

# *********** Inicio - Prácticas Finales (Digital Signature) - Fernando Reyes *************
import ds_utils
# *********** Fin - Prácticas Finales (Digital Signature) - Fernando Reyes *************

@auth.requires_login()
@auth.requires_membership('Student')
def index():
    #emarquez: exclusion de periodos variables
    list_periods = db(db.period_detail.period).select(db.period_detail.period)  

    current_date = datetime.datetime.now().date()
    assignations = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.assigned_user == db.auth_user.id)
                    & (db.user_project.project == db.project.id) & (db.project.area_level == db.area_level.id)
                    & ((~db.period.id.belongs([period.period for period in list_periods])) & (db.period_year.period == db.period.id))
                    & (db.user_project.period == db.period_year.id)).select(
                        db.user_project.assignation_ignored,
                        db.user_project.assignation_status,
                        db.user_project.assignation_comment,
                        db.user_project.id,
                        db.user_project.periods,
                        db.project.id,
                        db.project.name,
                        db.project.area_level,
                        db.area_level.name,
                        db.period_year.yearp,
                        db.period_year.period,
                        db.period_year.id,
                    )
    
    cyear_period = cpfecys.current_year_period()
    def available_reports(assignation_period):
        current_date = datetime.datetime.now()

        if assignation_period.period == cpfecys.first_period.id:
            date_min = datetime.datetime(assignation_period.yearp, 1, 1)
            date_max = datetime.datetime(assignation_period.yearp, 7, 1)
        else:
            the_year = assignation_period.yearp + 1
            date_min = datetime.datetime(assignation_period.yearp, 7, 1)
            date_max = datetime.datetime(the_year, 1, 1)

        return db((db.report_restriction.start_date <= current_date) & (db.report_restriction.end_date >= current_date)
                & (db.report_restriction.start_date >= date_min) & (db.report_restriction.end_date >= date_min)
                & (db.report_restriction.start_date < date_max) & (db.report_restriction.end_date < date_max)
                & (db.report_restriction.is_enabled == True))

    def available_item_restriction(period_year, user_project):
        #emarquez, revision 
        if cpfecys.is_semestre(period_year):
            return db(((db.item_restriction.period == period_year) | (db.item_restriction.permanent == True))
                    & (db.item_restriction.is_enabled == True) & (db.item_restriction_area.item_restriction == db.item_restriction.id)
                    & (db.item_restriction_area.area_level == user_project.project.area_level.id)
                    & (db.item_restriction.period_type == 2))
        else:
            return db(((db.item_restriction.period == period_year) | (db.item_restriction.permanent == True))
                    & (db.item_restriction.is_enabled == True) & (db.item_restriction_area.item_restriction == db.item_restriction.id)
                    & (db.item_restriction_area.area_level == user_project.project.area_level.id))

    def has_disabled_items(period_year, item_restriction, assignation):
        return db((db.item.created == period_year.id) & (db.item.item_restriction == item_restriction)
                & (db.item.assignation == assignation.user_project.id) & (db.item.is_active != True))

    def restriction_project_exception(item_restriction_id, project_id):
        return db((db.item_restriction_exception.project == project_id) & (db.item_restriction_exception.item_restriction == item_restriction_id))

    def items_instance(item_restriction, assignation):
        period = cpfecys.current_year_period()
        return db((db.item.item_restriction == item_restriction) & (db.item.created == period.id)
                & (db.item.assignation == assignation.user_project.id) & (db.item.is_active == True))

    def get_item(item_restriction, assignation):
        cperiod = cpfecys.current_year_period()
        if item_restriction.period.id < cperiod.id:
            item = db((db.item.item_restriction == item_restriction.id) & (db.item.assignation == assignation.user_project.id))
            return item
        return True

    def restriction_in_limit_days(item_restriction):
        cdate = datetime.datetime.now()
        cperiod = cpfecys.current_year_period()
        year = str(cperiod.yearp)
        if cperiod.period == cpfecys.first_period.id: month = '-01-01'
        else: month = '-06-01'
        
        start = datetime.datetime.strptime(year + month, "%Y-%m-%d")
        if item_restriction is not None:
            last_date = start + datetime.timedelta(days=item_restriction)
            if cdate > last_date:
                return False
            return True
        return True

    def calculate_last_day(item_restriction):
        cperiod = cpfecys.current_year_period()
        year = str(cperiod.yearp)
        month = '-06-01'
        last = '-01-01'
        if cperiod.period == cpfecys.first_period.id: 
            month = '-01-01'
            last = '-06-01'

        start = datetime.datetime.strptime(year + month, "%Y-%m-%d")
        if item_restriction is not None:
            last_date = start + datetime.timedelta(days=item_restriction - 1)
        else:
            if cperiod.period == cpfecys.first_period.id: 
                last_date = datetime.datetime.strptime(year + last, "%Y-%m-%d")
            else:
                year = str(int(year) + 1)
                last_date = datetime.datetime.strptime(year + last, "%Y-%m-%d")
                last_date = last_date-datetime.timedelta(days=1)
        return last_date.date()

    def assignation_range(assignation):
        #emarquez: exclusion periodos variables
        cperiod = cpfecys.current_year_period()
        ends = assignation.period_year.id + assignation.user_project.periods
        period_range = db((db.period_year.id >= assignation.period_year.id) & (db.period_year.id < ends)
                        & (db.period_year.id <= cperiod.id)).select(db.period_year.yearp, db.period_year.period, db.period_year.id)
        return period_range

    def is_indate_range(report):
        if report.score_date == None:
            return False

        current_date = datetime.datetime.now().date()
        next_date = report.score_date + datetime.timedelta(days=cpfecys.get_custom_parameters().rescore_max_days)
        return current_date < next_date

    def to_be_created(available_report, assignation):
        report = db((db.report.report_restriction == available_report.id) & (db.user_project.id == db.report.assignation)
                & (db.user_project.id == assignation.id) & (db.user_project.assigned_user == auth.user.id))
        return report.count() < 1

    # *********** Inicio - Prácticas Finales (Digital Signature) - Fernando Reyes *************
    def get_signed_file(id_item):
        query_signed_file = ds_utils.get_item_delivered_by_item(id_item)
        item_delivered = db.executesql(query_signed_file, as_dict=True)

        if len(item_delivered) > 0:
            if item_delivered[0]['signed_file'] is not None and item_delivered[0]['status'] == 'Signed':
                return item_delivered[0]['signed_file']
        return None

    return dict(
        assignations=assignations,
        available_reports=available_reports,
        current_date=current_date,
        cyear_period=cyear_period,
        available_item_restriction=available_item_restriction,
        items_instance=items_instance,
        restriction_project_exception=restriction_project_exception,
        is_indate_range=is_indate_range,
        restriction_in_limit_days=restriction_in_limit_days,
        assignation_range=assignation_range,
        get_item=get_item,
        calculate_last_day=calculate_last_day,
        has_disabled_items=has_disabled_items,
        to_be_created=to_be_created,
        get_signed_file=get_signed_file
    )
    # *********** Fin - Prácticas Finales (Digital Signature) - Fernando Reyes *************

@auth.requires_login()
@auth.requires_membership('Student')
def item():
    cyear_period = cpfecys.current_year_period()
    if cpfecys.is_semestre(request.vars['period']):
        cyear_period = cpfecys.current_year_period()
    else:
        cyear_period = db(db.period_year.id == request.vars['period']).select(db.period_year.id).first()
    
    item_restriction = request.vars['restriction']
    user_project = request.vars['assignation']
    period = request.vars['period']
    if period == None:
        session.flash = T('Action not allowed')
        redirect(URL('student', 'index'))

    period = int(period)
    area = request.vars['area']
    assignation = db((db.user_project.id == user_project) & (db.user_project.assigned_user == auth.user.id)).select().first()
    item_query = db((db.item.created == cyear_period) & (db.item.item_restriction == item_restriction)
                & (db.item.assignation == user_project) & (db.item.is_active == True))
    item_restriction = db(db.item_restriction.id == item_restriction).select(
                            db.item_restriction.limit_days,
                            db.item_restriction.id,
                            db.item_restriction.name,
                            db.item_restriction.item_type
                        ).first()

    #emarquez: adaptacion periodos variables
    if request.args(0) == 'create':
        if assignation is None:
            session.flash = T('This item can\'t be edited, permissions problem')
            redirect(URL('student', 'index'))

        if cpfecys.assignation_is_locked(assignation):
            session.flash = T('This item can\'t be edited, its assignation is locked')
            redirect(URL('student', 'index'))

        if cyear_period.id != period:
            session.flash = T('This item can\'t be edited, item edition for this item is out of time')
            redirect(URL('student', 'index'))

        itm_res_area = db((db.item_restriction_area.area_level == area) & (db.item_restriction_area.item_restriction == item_restriction)
                        & (db.item_restriction_area.is_enabled == True)).select(db.item_restriction_area.id)

        if itm_res_area is None:
            session.flash = T('This item can\'t be edited, doesn\'t belongs to this project')
            redirect(URL('student', 'index'))

        #emarquez: periodos, editar fechas
        if item_restriction.limit_days is not None:
            cdate = datetime.datetime.now()

            if cpfecys.is_semestre(period):
                cperiod = cpfecys.current_year_period()
                year = str(cperiod.yearp)
           
                month = '-06-01'
                if cperiod.period == cpfecys.first_period.id: month = '-01-01'            
            else:
                cperiod = cyear_period
                period = cpfecys.get_period_from_periodyear(cperiod.id)
                
                #seleccionando el periodo variable
                period_var = db(db.period_detail.period == period).select(db.period_detail.date_start_semester).first()
                #obteniendo las fechas de inicio y fin
                month = period_var.date_start_semester.strftime("-%m-%d")
                year = str(cperiod.yearp)
           
            start = datetime.datetime.strptime(year + month, "%Y-%m-%d")
            if item_restriction.limit_days is not None:
                last_date = start + datetime.timedelta(days=item_restriction.limit_days)
                if cdate > last_date:
                    session.flash = T(f'This item can\'t be edited, out of date, last date was {last_date}')
                    redirect(URL('student', 'index'))

        if item_query.select().first() is None:
            if item_restriction.item_type.name == 'File':
                form = FORM(
                    DIV(
                        LABEL(f'Subir, {item_restriction.name}'),
                        BR(), BR(),
                        INPUT(_name="upload", _type="file", _id="first_name", 
                            requires=[
                                IS_NOT_EMPTY(),
                                IS_UPLOAD_FILENAME(
                                    extension='^(pdf|doc|docx)$',
                                    error_message='Formato invalido, Subir unicamente archivos del tipo PDF, DOC or DOCX'
                                )
                            ]
                        )
                    ),
                    BR(),
                    DIV(INPUT(_type='submit', _value=T('Upload File'), _class="btn btn-primary")),
                    _class="form-horizontal"
                )
                if form.process().accepted:
                    if request.vars.upload is not None:
                        item = db.item.uploaded_file.store(request.vars.upload.file, request.vars.upload.filename)
                        db.item.insert(
                            uploaded_file=item,
                            is_active=True,
                            created=cyear_period,
                            item_restriction=item_restriction.id,
                            assignation=user_project
                        )
                        db.commit()
                        session.flash = T('Item created!')
                        redirect(URL('student', 'index'))
                    else:
                        session.flash = T('Form Errors')
                        redirect(URL('student', 'index'))
                return  dict(form=form, action='create')
            elif item_restriction.item_type.name == 'Schedule':
                item = db.item.insert(
                    is_active=True,
                    created=cyear_period,
                    item_restriction=item_restriction.id,
                    assignation=user_project
                )
                session.flash = T('Item Created')
                redirect(URL('student', 'item', args=['edit'], vars=dict(
                        restriction=item_restriction.id,
                        assignation=user_project,
                        period=period,
                        item=item.id
                    )
                ))
        else:
            session.flash = T('Action not allowed')
            redirect(URL('student', 'index'))
    elif request.args(0) == 'view':
        item_upload = request.vars['file']
        item = db((db.item.item_restriction == item_restriction.id) & (db.item.assignation == user_project)
                & (db.item.uploaded_file == item_upload)).select(db.item.is_active, db.item.assignation).first()
        if item is not None and not item_restriction.teacher_only and item.is_active and item.assignation.assigned_user == auth.user.id:
            return dict(item=item, name=item_restriction.name, action='view')
        else:
            session.flash = T('Access Forbidden')
            redirect(URL('student', 'index'))
    elif request.args(0) == 'edit':
        item_id = request.vars['item']
        if assignation is None:
            session.flash = T('This item can\'t be edited, permissions problem')
            redirect(URL('student', 'index'))

        if cpfecys.assignation_is_locked(assignation):
            session.flash = T('This item can\'t be edited, its assignation is locked')
            redirect(URL('student', 'index'))

        if cyear_period.id != period:
            session.flash = T('This item can\'t be edited, item edition for this item is out of time')
            redirect(URL('student', 'index'))

        can_edit = db((db.item_restriction.id == item_restriction.id) & (db.item.item_restriction == db.item_restriction.id)
                    & (db.item.id == item_id) & (db.item.assignation == db.user_project.id)
                    & (db.item.assignation == user_project) & (db.item.created == db.period_year.id)
                    & (db.period_year.id == period))

        if can_edit is None:
            session.flash = T('This item can\'t be edited, doesn\'t belongs to this project')
            redirect(URL('student', 'index'))

        if item_restriction.limit_days is not None:
            cdate = datetime.datetime.now()
            if cpfecys.is_semestre(period):
                cperiod = cpfecys.current_year_period()
                year = str(cperiod.yearp)
           
                month = '-06-01'
                if cperiod.period == cpfecys.first_period.id: 
                    month = '-01-01'                    
            else:
                cperiod = cyear_period
                period = cpfecys.get_period_from_periodyear(cperiod.id)

                #seleccionando el periodo variable
                period_var = db(db.period_detail.period == period).select().first()

                #obteniendo las fechas de inicio y fin
                month = period_var.date_start_semester.strftime("-%m-%d")
                year = str(cperiod.yearp)

            start = datetime.datetime.strptime(year + month, "%Y-%m-%d")
            last_date = start + datetime.timedelta(days=item_restriction.limit_days)
            if cdate > last_date:
                session.flash = f"Este entregable no se puede entregar, está fuera de fecha; la última fecha fue:  {last_date}"
                redirect(URL('student', 'index'))

        item = db(db.item.id == item_id).select().first()
        if item is None or not item.is_active:
            session.flash = ('This item can\'t be edited, doesn\'t exists or is not active')
            redirect(URL('student', 'index'))
        
        if item.item_restriction.item_type.name == 'File':
            form = FORM(
                DIV(
                    LABEL(f'Subir, {item_restriction.name}:'),
                    BR(), BR(),
                    INPUT(_name="upload", _type="file", _id="first_name", 
                        requires=[
                            IS_NOT_EMPTY(),
                            IS_UPLOAD_FILENAME(
                                extension='^(pdf|doc|docx)$',
                                error_message='Formato invalido, Subir unicamente archivos del tipo: PDF, DOC o DOCX'
                            )
                        ]
                    )
                ),
                BR(),
                DIV(INPUT(_type='submit', _value=T('Upload File'), _class="btn btn-primary")), 
                _class="form-horizontal"
            )

            if form.process().accepted:
                if request.vars.upload is not None:
                    uploaded = db.item.uploaded_file.store(request.vars.upload.file, request.vars.upload.filename)
                    item = db((db.item.created == cyear_period) & (db.item.item_restriction == item_restriction)
                            & (db.item.assignation == user_project)).select().first()
                    if item is not None:
                        item.update_record(uploaded_file=uploaded)
                        db.commit()

                        # *********** Inicio - Prácticas Finales (Digital Signature) - Fernando Reyes *************
                        values = {'status': 'Delivered'}
                        condition = {'item': int(item_id)}
                        try:
                            update_query = ds_utils.create_script_string('ds_item_delivered', 'U', values, condition)
                            db.executesql(update_query)
                        except:
                            response.flash = 'Error al momento de cargar el documento'
                        # *********** Fin - Prácticas Finales (Digital Signature) - Fernando Reyes *************

                        redirect(URL('student', 'index'))
                    elif form.errors:
                        response.flash = "Errors"
                    else:
                        response.flash = "please fill the form"

            return  dict(form=form, action='edit')
        elif item.item_restriction.item_type.name == 'Schedule':
            db.item_schedule.item.writable = False
            db.item_schedule.item.default = item.id
            response.view = 'student/schedule.html'
            grid = SQLFORM.grid((db.item_schedule.item == item.id), args=request.args)
            return dict(schedule_name = item.item_restriction.name, grid = grid)
    else:
        response.view = 'student/schedule.html'
        grid = SQLFORM.grid(db.item_schedule)
        return dict(schedule_name = 'Horario de Curso', grid = grid)

#emarquez: inclusion de periodos variables
@auth.requires_login()
@auth.requires_membership('Student')
def periods():
    current_date = datetime.datetime.now().date()
    #emarquez: unicamente periodos variables 
    assignations = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.assigned_user == db.auth_user.id)
                    & (db.user_project.project == db.project.id) & (db.project.area_level == db.area_level.id)
                    & (db.period_year.period == db.period.id) & (db.period_detail.period == db.period.id)
                    & (db.user_project.period == db.period_year.id)).select()
    
    cyear_period = cpfecys.current_year_period()

    def available_reports(assignation_period):
        current_date = datetime.datetime.now()
        #if it is the first semester then the restriction should be:
        #start date >= January 1 year 00:00:00
        #end date >= January 1 year 00:00:00
        #start date < July 1 year 00:00:00
        #end date < July 1 year 00:00:00
        #if it is the second semester then the restriction should be:
        #start date >= July 1 year 00:00:00
        #end date >= July 1 year 00:00:00
        #start date < Jan 1 year 00:00:00
        #end date < Jan 1 year 00:00:00
        if assignation_period.period == cpfecys.first_period.id:
            date_min = datetime.datetime(assignation_period.yearp, 1, 1)
            date_max = datetime.datetime(assignation_period.yearp, 7, 1)
        else:
            the_year = assignation_period.yearp + 1
            date_min = datetime.datetime(assignation_period.yearp, 7, 1)
            date_max = datetime.datetime(the_year, 1, 1)
        return db((db.report_restriction.start_date <= current_date)&
                  (db.report_restriction.end_date >= current_date)&
                  (db.report_restriction.start_date >= date_min)&
                  (db.report_restriction.end_date >= date_min)&
                  (db.report_restriction.start_date < date_max)&
                  (db.report_restriction.end_date < date_max)&
                  (db.report_restriction.is_enabled == True))

    def available_item_restriction(period_year, user_project):
         #emarquez, revision 
        if cpfecys.is_semestre(period_year):
                return db(((db.item_restriction.period==period_year) |
                        (db.item_restriction.permanent==True))&
                    (db.item_restriction.is_enabled==True)&
                    (db.item_restriction_area.item_restriction==\
                        db.item_restriction.id)&
                    (db.item_restriction_area.area_level==\
                        user_project.project.area_level.id)&(db.item_restriction.period_type==2))
            
        else:
            return db(((db.item_restriction.period==period_year) |
                        (db.item_restriction.permanent==True))&
                    (db.item_restriction.is_enabled==True)&
                    (db.item_restriction_area.item_restriction==\
                        db.item_restriction.id)&
                    (db.item_restriction_area.area_level==\
                        user_project.project.area_level.id)&(db.item_restriction.period_type==1))


    def has_disabled_items(period_year, item_restriction, assignation):
        items = db((db.item.created==period_year.id)&
            (db.item.item_restriction==item_restriction.id)&
            (db.item.assignation==assignation.user_project.id)&
            (db.item.is_active!=True))
        return items

    def restriction_project_exception(item_restriction_id, project_id):
        return db((db.item_restriction_exception.project== \
                    project_id)&
                    (db.item_restriction_exception.item_restriction \
                        ==item_restriction_id))

    def items_instance(item_restriction, assignation):
        #emarquez: adaptacion periodos variables
        #period = cpfecys.current_year_period()
        return db((db.item.item_restriction==item_restriction.id)&
                    (db.item.created==item_restriction.period)&
                    (db.item.assignation==assignation.user_project.id)&
                    (db.item.is_active==True))

    def get_item(item_restriction, assignation):
        cperiod = cpfecys.current_year_period()
        if item_restriction.period.id < cperiod.id:
            item = db((db.item.item_restriction==item_restriction.id)&
                (db.item.assignation==assignation.user_project.id))
            return item
        return True

    def restriction_in_limit_days(item_restriction):
        #emarquez: rehacer esta funcion para que soporte el periodo
        cdate = datetime.datetime.now()
        cperiod = db(db.period_year.id == item_restriction.period).select().first()
        #cperiod = cpfecys.current_year_period()
        year = str(cperiod.yearp)
        period = cpfecys.get_period_from_periodyear(cperiod.id)
        #seleccionando el periodo variable
        period_var = db(db.period_detail.period==period).select().first()
        #obteniendo las fechas de inicio y fin
        month= period_var.date_start_semester.strftime("-%m-%d")


        start = datetime.datetime.strptime(year + month, "%Y-%m-%d")
        if item_restriction.limit_days != None:
            last_date = start + datetime.timedelta( \
                days=item_restriction.limit_days)
            if cdate > last_date:
                return False
            return True
        return True

    def calculate_last_day(item_restriction):
        #emarquez: modificacion para adaptacion de periodos variables
        cperiod = db(db.period_year.id == item_restriction.period).select().first()
        year = str(cperiod.yearp)
        
        period = cpfecys.get_period_from_periodyear(cperiod.id)
        #seleccionando el periodo variable
        period_var = db(db.period_detail.period==period).select().first()
        #obteniendo las fechas de inicio y fin
        month= period_var.date_start_semester.strftime("-%m-%d")
        last =period_var.date_finish_semester.strftime("-%m-%d")

        start = datetime.datetime.strptime(year + month, "%Y-%m-%d")
        if item_restriction.limit_days != None:
            last_date = start + datetime.timedelta( \
                days=item_restriction.limit_days-1)
        else:            
            last_date = datetime.datetime.strptime(year + last, "%Y-%m-%d")

        return last_date.date()

    def assignation_range(assignation):
        #emarquez: adaptacion periodos variables
        #cperiod = cpfecys.current_year_period()
        #ends = assignation.period_year.id + assignation.user_project.periods
        
        period_range = db((db.period_year.id == assignation.period_year.id)&
            (db.period_year.id ==assignation.user_project.period)).select()
        return period_range

    def is_indate_range(report):
        if report.score_date == None:
            return False
        current_date = datetime.datetime.now().date()
        next_date = report.score_date + datetime.timedelta(
                        days=cpfecys.get_custom_parameters().rescore_max_days)
        return current_date < next_date

    def to_be_created(available_report, assignation):
        report = db((db.report.report_restriction==available_report.id)&
            (db.user_project.id==db.report.assignation)&
            (db.user_project.id==assignation.id)&
            (db.user_project.assigned_user==auth.user.id))
        return report.count() < 1


    return dict(assignations = assignations,
                available_reports = available_reports,
                current_date = current_date,
                cyear_period = cyear_period,
                available_item_restriction = available_item_restriction,
                items_instance = items_instance,
                restriction_project_exception=restriction_project_exception,
                is_indate_range=is_indate_range,
                restriction_in_limit_days=restriction_in_limit_days,
                assignation_range=assignation_range,
                get_item=get_item,
                calculate_last_day=calculate_last_day,
                has_disabled_items=has_disabled_items,
                to_be_created=to_be_created)

@auth.requires_login()
@auth.requires_membership('Student')
def report():
    if request.args(0) == 'create':
        #get the data & save the report
        assignation = request.vars['assignation']
        report_restriction = request.vars['report_restriction']

        # Validate report_restriction
        report_restrict = db(db.report_restriction.id == report_restriction).select(db.report_restriction.id).first()
        valid_report = report_restrict is not None
        
        # Validate assignation belongs to this user
        assign = db((db.user_project.id == assignation) & (db.user_project.assigned_user == auth.user.id)).select(db.user_project.assignation_status).first()
        valid_assignation = assign is not None
        
        ## Validate assignation
        if valid_assignation: valid_assignation = not cpfecys.assignation_is_locked(assign)
        
        # Validate there is not an already inserted report
        valid = db.report((db.report.assignation == assignation) & (db.report.report_restriction == report_restriction)) is None
        if not(assignation and report_restriction and valid and valid_assignation and valid_report):
            session.flash = T('Invalid selected assignation and report. Select a valid one.') + 'INV001'
            redirect(URL('student','index'))
        
        current_date = datetime.datetime.now()
        report = db.report.insert(
                    created=current_date,
                    assignation=assignation,
                    report_restriction=report_restriction,
                    status=db.report_status(name = 'Draft')
                )

        #***********************************************************************************************************************
        #******************************************************PHASE 2 DTT******************************************************
        if report.assignation.project.area_level.name == 'DTT Tutor Académico' and report.report_restriction.is_final:
            #CREATE THE FINAL METRICS
            cperiod = obtain_period_report(report)
            final_metrics = final_metric(cperiod, report)
            try:
                average = float((final_metrics[22] * 100) / final_metrics[20])
            except:
                average = float(0)
            
            db.log_final.insert(
                curso_asignados_actas=int(final_metrics[0]),
                curso_en_parciales=int(final_metrics[1]),
                curso_en_final=int(final_metrics[2]),
                curso_en_primera_restrasada=int(final_metrics[3]),
                curso_en_segunda_restrasada=int(final_metrics[4]),
                lab_aprobados=int(final_metrics[5]),
                lab_reprobados=int(final_metrics[6]),
                lab_media=final_metrics[7],
                lab_promedio=final_metrics[8],
                curso_media=final_metrics[9],
                curso_error=final_metrics[10],
                curso_mediana=final_metrics[11],
                curso_moda=final_metrics[12],
                curso_desviacion=final_metrics[13],
                curso_varianza=final_metrics[14],
                curso_curtosis=final_metrics[15],
                curso_coeficiente=final_metrics[16],
                curso_rango=final_metrics[17],
                curso_minimo=final_metrics[18],
                curso_maximo=final_metrics[19],
                curso_total=int(final_metrics[20]),
                curso_reprobados=int(final_metrics[21]),
                curso_aprobados=int(final_metrics[22]),
                curso_promedio=average,
                curso_created=current_date,
                report=report.id
            )
        #***********************************************************************************************************************
        #******************************************************PHASE 2 DTT******************************************************

        session.flash = 'El reporte ahora es un borrador'
        redirect(URL('student', 'report/edit', vars=dict(report=report.id)))
    elif request.args(0) == 'edit':
        #Get the report id
        report = request.vars['report']
        
        #Retrieve report data
        report = db(db.report.id == report).select(
                    db.report.id,
                    db.report.assignation,
                    db.report.score_date,
                    db.report.report_restriction,
                    db.report.status,
                    db.report.dtt_approval,
                    db.report.heading,
                    db.report.footer,
                    db.report.desertion_started,
                    db.report.hours,
                    db.report.created,
                    db.report.desertion_gone,
                    db.report.desertion_continued
                ).first()

        if not report:
            session.flash = T('Selected report can\'t be edited. Select a valid report.')
            redirect(URL('student','index'))
        
        #Validate assignation
        if cpfecys.assignation_is_locked(report.assignation):
            session.flash = T('Selected report can\'t be edited. Select a valid report.')
            redirect(URL('student','index'))

        #Validate that the report belongs to user
        valid_report_owner = cpfecys.student_validation_report_owner(report.id)
        if not valid_report_owner:
            session.flash = T('Selected report can\'t be edited. Select a valid report.')
            redirect(URL('student','index'))
        
        #Validate that the report status is editable (it is either 'Draft' or 'Recheck')
        if not cpfecys.student_validation_report_status(report):
            session.flash = T('Selected report can\'t be edited. Is not in a editable state.')
            #redirect(URL('student','index'))
        
        #Validate that the administrator of DTT has not failed the student
        if report.dtt_approval is not None and not report.dtt_approval:
            session.flash = T('Selected report can\'t be edited. Select a valid report.')
            redirect(URL('student','index'))

        #Markmin formatting of reports
        response.view = 'student/report_edit.html'
        assignation_reports = db(db.report.assignation == report.assignation).select(
                                db.report.report_restriction,
                                db.report.desertion_continued,
                                db.report.desertion_gone,
                                db.report.desertion_started,
                                db.report.assignation,
                                db.report.hours
                            )

        # check minimun requirements
        reqs = db(db.area_report_requirement.area_level == report.assignation.project.area_level).select(db.area_report_requirement.report_requirement)
        minimal_requirements = True
        
        #***********************************************************************************************************************
        #******************************************************PHASE 2 DTT******************************************************
        activities_count = db(db.log_entry.report == report.id).count()
        metrics_count = db(db.log_metrics.report == report.id).count()
        final_stats = db(db.log_final.report == report.id).count()

        activities_wm = None
        activities_m = None
        activities_f = None
        final_stats_flag = False

        if report.assignation.project.area_level.name == 'DTT Tutor Académico':
            #Get the minimum and maximum date of the report
            cperiod = obtain_period_report(report)
            parameters_period = db(db.student_control_period.period_name == f'{T(cperiod.period.name)} {cperiod.yearp}').select(db.student_control_period.percentage_income_activity).first()
            init_semester, end_date_activity = report_month(cperiod.period, cperiod.yearp, report.report_restriction.name, report.report_restriction.is_final)
            activities_f = []

            #Verify that the date range of the period and the parameters are defined
            if init_semester is None or end_date_activity is None or parameters_period is None:
                session.flash = T('Error. Is not defined date range of the report or do not have the required parameters. --- Contact the system administrator.')
                redirect(URL('student','index'))
            else:
                #Get the latest reports and are of this semester
                before_reports_restriction = db((db.report_restriction.id < report.report_restriction) & (db.report_restriction.start_date  >= init_semester)).select(db.report_restriction.id)
                if before_reports_restriction.first() is None:
                    before_reports = []
                    before_reports.append(-1)
                else:
                    before_reports = db((db.report.assignation == report.assignation) & (db.report.report_restriction.belongs(before_reports_restriction))).select(db.report.id)
                    if before_reports.first() is None:
                        before_reports = []
                        before_reports.append(-1)

            #Check the id of the log type thtat is activity
            temp_log_type = db(db.log_type.name == 'Activity').select(db.log_type.id).first()

            #Verify that there is a category activity report
            if temp_log_type is None:
                session.flash = T('Error. Is not defined date range of the report or do not have the required parameters. --- Contact the system administrator.')
                redirect(URL('student','index'))
            else:
                #*******************Activities to record activities unless already recorded in previous reports
                #Activities without metric
                activities_wm_before = db((db.log_entry.log_type == temp_log_type.id) & (db.log_entry.period == cperiod.id)
                                        & (db.log_entry.tActivity == False) & (db.log_entry.report.belongs(before_reports))).select(db.log_entry.idActivity.with_alias('id'))
                if activities_wm_before.first() is None:
                    activities_wm = db((db.course_activity_without_metric.semester == cperiod.id) & (db.course_activity_without_metric.assignation == report.assignation.project)
                                    & (db.course_activity_without_metric.date_start < end_date_activity)).select(
                                        db.course_activity_without_metric.date_start,
                                        db.course_activity_without_metric.name,
                                        db.course_activity_without_metric.description
                                    )
                    #Future activities without metric
                    if not report.report_restriction.is_final:
                        activities_f_temp = db((db.course_activity_without_metric.semester == cperiod.id) & (db.course_activity_without_metric.assignation == report.assignation.project)
                                            & (db.course_activity_without_metric.date_start >= end_date_activity)).select(
                                                db.course_activity_without_metric.date_start,
                                                db.course_activity_without_metric.name,
                                                db.course_activity_without_metric.description
                                            )
                        for awmt in activities_f_temp:
                            activities_f.append(awmt)
                else:
                    activities_wm = db((db.course_activity_without_metric.semester == cperiod.id) & (db.course_activity_without_metric.assignation == report.assignation.project)
                                    & (~db.course_activity_without_metric.id.belongs(activities_wm_before)) & (db.course_activity_without_metric.date_start < end_date_activity)).select(
                                        db.course_activity_without_metric.date_start,
                                        db.course_activity_without_metric.name,
                                        db.course_activity_without_metric.description
                                    )
                    #Future activities without metric
                    if not report.report_restriction.is_final:
                        activities_f_temp = db((db.course_activity_without_metric.semester == cperiod.id) & (db.course_activity_without_metric.assignation == report.assignation.project)
                                            & (~db.course_activity_without_metric.id.belongs(activities_wm_before)) & (db.course_activity_without_metric.date_start >= end_date_activity)).select(
                                                db.course_activity_without_metric.date_start,
                                                db.course_activity_without_metric.name,
                                                db.course_activity_without_metric.description
                                            )
                        for awmt in activities_f_temp:
                            activities_f.append(awmt)

                #Activities with metric
                activities_m_before = db((db.log_entry.log_type == temp_log_type.id) & (db.log_entry.period == cperiod.id)
                                        & (db.log_entry.tActivity == True) & (db.log_entry.report.belongs(before_reports))).select(db.log_entry.idActivity.with_alias('id'))
                activities_grades = db((db.grades.academic_assignation == db.academic_course_assignation.id) & (db.academic_course_assignation.semester == cperiod.id)
                                    & (db.academic_course_assignation.assignation == report.assignation.project)).select(db.grades.activity.with_alias('id'), distinct=True)
                if activities_grades.first() is not None:
                    activities_m_real = []
                    if activities_m_before.first() is None:
                        #Complete with measuring activities
                        activities_m = db((db.course_activity.semester == cperiod.id) & (db.course_activity.assignation == report.assignation.project)
                                        & (db.course_activity.date_start < end_date_activity) & (db.course_activity.id.belongs(activities_grades))).select(
                                                db.course_activity.date_start,
                                                db.course_activity.name,
                                                db.course_activity.description,
                                                db.course_activity.date_finish,
                                                db.course_activity.id,
                                                db.course_activity.course_activity_category
                                        )
                        for act_tempo in activities_m:
                            if not report.report_restriction.is_final:
                                temp_end_act = act_tempo.date_finish 
                                temp_end_act = datetime.datetime(temp_end_act.year, temp_end_act.month, temp_end_act.day)
                                end_date_activityt1 = datetime.datetime(end_date_activity.year, end_date_activity.month, end_date_activity.day)
                                if temp_end_act < end_date_activityt1:
                                    grades_log_count = int(db((db.grades_log.activity_id == act_tempo.id) & (db.grades_log.operation_log == 'insert')
                                                        & (db.grades_log.user_name == auth.user.username)).count())
                                    grades_count = int(db(db.grades.activity == act_tempo.id).count())
                                    #Check if you have the minimum of notes recorded in the activity amount that you are worth in the report
                                    if ((grades_log_count * 100) / grades_count) >= int(parameters_period.percentage_income_activity):
                                        activities_m_real.append(metric_statistics(act_tempo, 0, None))
                                else:
                                    #Future activities with metric
                                    activities_f.append(act_tempo)
                            else:
                                grades_log_count = int(db((db.grades_log.activity_id == act_tempo.id) & (db.grades_log.operation_log == 'insert')
                                                    & (db.grades_log.user_name == auth.user.username)).count())
                                grades_count = int(db(db.grades.activity == act_tempo.id).count())
                                #Check if you have the minimum of notes recorded in the activity amount that you are worth in the report
                                if ((grades_log_count * 100) / grades_count) >= int(parameters_period.percentage_income_activity):
                                    activities_m_real.append(metric_statistics(act_tempo, 0, None))
                        activities_m = activities_m_real
                        #Complete with measuring future activities
                        if not report.report_restriction.is_final:
                            activities_f_temp = db((db.course_activity.semester == cperiod.id) & (db.course_activity.assignation == report.assignation.project)
                                                & (db.course_activity.date_start >= end_date_activity)).select(
                                                    db.course_activity.date_start,
                                                    db.course_activity.name,
                                                    db.course_activity.description
                                                )
                            for awmt in activities_f_temp:
                                activities_f.append(awmt)
                    else:
                        #Complete with measuring activities
                        activities_m = db((db.course_activity.semester == cperiod.id) & (db.course_activity.assignation == report.assignation.project)
                                        & (db.course_activity.date_start < end_date_activity) & (~db.course_activity.id.belongs(activities_m_before))
                                        & (db.course_activity.id.belongs(activities_grades))).select(
                                            db.course_activity.date_finish,
                                            db.course_activity.name,
                                            db.course_activity.description,
                                            db.course_activity.id,
                                            db.course_activity.course_activity_category,
                                            db.course_activity.date_start
                                        )
                        for act_tempo in activities_m:
                            if not report.report_restriction.is_final:
                                temp_end_act = act_tempo.date_finish 
                                temp_end_act = datetime.datetime(temp_end_act.year, temp_end_act.month, temp_end_act.day)
                                end_date_activityt1 = datetime.datetime(end_date_activity.year, end_date_activity.month, end_date_activity.day)
                                if temp_end_act < end_date_activityt1:
                                    grades_log_count = int(db((db.grades_log.activity_id == act_tempo.id) & (db.grades_log.operation_log == 'insert')
                                                    & (db.grades_log.user_name == auth.user.username)).count())
                                    grades_count = int(db(db.grades.activity == act_tempo.id).count())
                                    #Check if you have the minimum of notes recorded in the activity amount that you are worth in the report
                                    if ((grades_log_count * 100) / grades_count) >= int(parameters_period.percentage_income_activity):
                                        activities_m_real.append(metric_statistics(act_tempo, 0, None))
                                else:
                                    #Future activities with metric
                                    activities_f.append(act_tempo)
                            else:
                                grades_log_count = int(db((db.grades_log.activity_id == act_tempo.id) & (db.grades_log.operation_log == 'insert')
                                                    & (db.grades_log.user_name == auth.user.username)).count())
                                grades_count = int(db(db.grades.activity == act_tempo.id).count())
                                #Check if you have the minimum of notes recorded in the activity amount that you are worth in the report
                                if ((grades_log_count * 100) / grades_count) >= int(parameters_period.percentage_income_activity):
                                    activities_m_real.append(metric_statistics(act_tempo, 0, None))
                        activities_m = activities_m_real

                        #Complete with measuring future activities
                        if not report.report_restriction.is_final:
                            activities_f_temp = db((db.course_activity.semester == cperiod.id) & (db.course_activity.assignation == report.assignation.project)
                                                & (db.course_activity.date_start >= end_date_activity) & (~db.course_activity.id.belongs(activities_m_before))).select(
                                                    db.course_activity.date_start,
                                                    db.course_activity.name,
                                                    db.course_activity.description
                                                )
                            for awmt in activities_f_temp:
                                activities_f.append(awmt)

            if db(db.course_report_exception.project == report.assignation.project).select(db.course_report_exception.id).first() is not None:
                final_stats_flag = True

            #RECOVERY 1 y 2
            if report.report_restriction.is_final:
                #students_first_recovery
                try:
                    frt = int(db((db.course_first_recovery_test.semester == cperiod.id) & (db.course_first_recovery_test.project == report.assignation.project)).count())
                except:
                    frt = 0
                if frt > 0:
                    if activities_m is None:
                        activities_m = []
                    activities_m.append(metric_statistics(report, 1, None))

                #students_second_recovery
                try:
                    srt = int(db((db.course_second_recovery_test.semester == cperiod.id) & (db.course_second_recovery_test.project == report.assignation.project)).count())
                except:
                    srt = 0
                if srt > 0:
                    if activities_m is None:
                        activities_m = []
                    activities_m.append(metric_statistics(report, 2, None))
        
        if activities_m is None: activities_m = []
        if activities_wm is None: activities_wm = []
        if activities_f is None: activities_f = []

        activities_count += len(activities_wm) + len(activities_m)
        metrics_count += len(activities_m)
        #***********************************************************************************************************************
        #******************************************************PHASE 2 DTT******************************************************

        for req in reqs:
            if req.report_requirement.name == 'Registrar Estadisticas Finales de Curso' and report.report_restriction.is_final and final_stats == 0:
                minimal_requirements = False
                break
            if req.report_requirement.name == 'Encabezado' and report.heading is None:
                minimal_requirements = False
                break
            if req.report_requirement.name == 'Pie de Reporte' and report.footer is None:
                minimal_requirements = False
                break
            if req.report_requirement.name == 'Registrar Actividad' and activities_count == 0:
                minimal_requirements = False
                break
            if req.report_requirement.name == 'Registrar Actividad con Metricas' and metrics_count == 0:
                minimal_requirements = False
                break
            if req.report_requirement.name == 'Registrar Deserciones' and report.desertion_started is None:
                minimal_requirements = False
                break
            if req.report_requirement.name == 'Registrar Horas Completadas' and report.hours is None:
                minimal_requirements = False
                break
        mandatory_requirements = ''
        for req in reqs:
            mandatory_requirements += req.report_requirement.name  + ', '

        logs = db(db.log_entry.report == report.id).select(
                    db.log_entry.id,
                    db.log_entry.entry_date,
                    db.log_entry.log_type,
                    db.log_entry.description
                )

        return dict(
            log_types=db(db.log_type.id > 0).select(),
            mandatory_requirements=mandatory_requirements,
            minimal_requirements=minimal_requirements,
            assignation_reports=assignation_reports,
            logs=logs,
            metrics=db((db.log_metrics.report == report.id)).select(),
            final_r=db(db.log_final.report == report.id).select(),
            metrics_type=db(db.metrics_type).select(),
            anomalies=db((db.log_type.name == 'Anomaly') & (db.log_entry.log_type == db.log_type.id)
                        & (db.log_entry.report == report.id)).count(),
            markmin_settings=cpfecys.get_markmin,
            report=report,
            activities_wm=activities_wm,      #Phase2 DTT
            activities_m=activities_m,        #Phase2 DTT
            activities_f=activities_f,        #Phase2 DTT
            final_stats_flag=final_stats_flag #Phase2 DTT
        )
    elif request.args(0) == 'acceptance':
        #get the data & save the report
        report = request.vars['report']
        report = db(db.report.id == report).select(
                    db.report.assignation,
                    db.report.id,
                    db.report.report_restriction,
                    db.report.heading,
                    db.report.footer,
                    db.report.desertion_started,
                    db.report.hours,
                    db.report.score_date,
                    db.report.status,
                    db.report.dtt_approval
                ).first()
        # Check minimun requirements
        reqs = db(db.area_report_requirement.area_level == report.assignation.project.area_level).select(
                    db.area_report_requirement.report_requirement
                )
        minimal_requirements = True

        #***********************************************************************************************************************
        #******************************************************PHASE 2 DTT******************************************************
        activities_count = db(db.log_entry.report == report.id).count()
        metrics_count = db(db.log_metrics.report == report.id).count()
        final_stats = db(db.log_final.report == report.id).count()

        activities_wm = None
        activities_m = None
        activities_f = None
        final_stats_flag = False
        if report.assignation.project.area_level.name == 'DTT Tutor Académico':
            #Get the minimum and maximum date of the report
            cperiod = obtain_period_report(report)
            parameters_period = db(db.student_control_period.period_name == f'{T(cperiod.period.name)} {cperiod.yearp}').select(db.student_control_period.percentage_income_activity).first()
            init_semester, end_date_activity = report_month(cperiod.period, cperiod.yearp, report.report_restriction.name, report.report_restriction.is_final)
            activities_f = []

            #Verify that the date range of the period and the parameters are defined
            if init_semester is  None or end_date_activity is None or parameters_period is None:
                session.flash = T('Error. Is not defined date range of the report or do not have the required parameters. --- Contact the system administrator.')
                redirect(URL('student', 'index'))
            else:
                #Get the latest reports and are of this semester
                before_reports_restriction = db((db.report_restriction.id < report.report_restriction) & (db.report_restriction.start_date >= init_semester)).select(db.report_restriction.id)
                if before_reports_restriction.first() is None:
                    before_reports = []
                    before_reports.append(-1)
                else:
                    before_reports = db((db.report.assignation == report.assignation) & (db.report.report_restriction.belongs(before_reports_restriction))).select(db.report.id)
                    if before_reports.first() is None:
                        before_reports = []
                        before_reports.append(-1)

            #Check the id of the log type thtat is activity
            temp_log_type = db(db.log_type.name == 'Activity').select(db.log_type.id).first()

            #Verify that there is a category activity report
            if temp_log_type is None:
                session.flash = T('Error. Is not defined date range of the report or do not have the required parameters. --- Contact the system administrator.')
                redirect(URL('student','index'))
            else:
                #*******************Activities to record activities unless already recorded in previous reports
                #Activities without metric
                activities_wm_before = db((db.log_entry.log_type == temp_log_type.id) & (db.log_entry.period == cperiod.id)
                                        & (db.log_entry.tActivity == False) & (db.log_entry.report.belongs(before_reports))).select(db.log_entry.idActivity.with_alias('id'))
                if activities_wm_before.first() is None:
                    activities_wm = db((db.course_activity_without_metric.semester == cperiod.id) & (db.course_activity_without_metric.assignation == report.assignation.project)
                                    & (db.course_activity_without_metric.date_start < end_date_activity)).select(
                                        db.course_activity_without_metric.id,
                                        db.course_activity_without_metric.name,
                                        db.course_activity_without_metric.description
                                    )
                    #Future activities without metric
                    if not report.report_restriction.is_final:
                        activities_f_temp = db((db.course_activity_without_metric.semester == cperiod.id) & (db.course_activity_without_metric.assignation == report.assignation.project)
                                            & (db.course_activity_without_metric.date_start >= end_date_activity)).select(db.course_activity_without_metric.name, db.course_activity_without_metric.description)
                        for awmt in activities_f_temp:
                            activities_f.append(awmt)
                else:
                    activities_wm = db((db.course_activity_without_metric.semester == cperiod.id) & (db.course_activity_without_metric.assignation == report.assignation.project)
                                    & (~db.course_activity_without_metric.id.belongs(activities_wm_before)) & (db.course_activity_without_metric.date_start < end_date_activity)).select(
                                        db.course_activity_without_metric.name,
                                        db.course_activity_without_metric.description,
                                        db.course_activity_without_metric.id
                                    )
                    #Future activities without metric
                    if report.report_restriction.is_final:
                        activities_f_temp = db((db.course_activity_without_metric.semester == cperiod.id) & (db.course_activity_without_metric.assignation == report.assignation.project)
                                            & (~db.course_activity_without_metric.id.belongs(activities_wm_before)) & (db.course_activity_without_metric.date_start >= end_date_activity)).select(
                                                db.course_activity_without_metric.name,
                                                db.course_activity_without_metric.description
                                            )
                        for awmt in activities_f_temp:
                            activities_f.append(awmt)

                #Activities with metric
                activities_m_before = db((db.log_entry.log_type == temp_log_type.id) & (db.log_entry.period == cperiod.id)
                                    & (db.log_entry.tActivity == True) & (db.log_entry.report.belongs(before_reports))).select(db.log_entry.idActivity.with_alias('id'))
                activities_grades = db((db.grades.academic_assignation == db.academic_course_assignation.id) & (db.academic_course_assignation.semester == cperiod.id)
                                    & (db.academic_course_assignation.assignation == report.assignation.project)).select(db.grades.activity.with_alias('id'), distinct=True)
                if activities_grades.first() is not None:
                    activities_m_real = []
                    if activities_m_before.first() is None:
                        #Complete with measuring activities
                        activities_m = db((db.course_activity.semester == cperiod.id) & (db.course_activity.assignation == report.assignation.project)
                                        & (db.course_activity.date_start < end_date_activity)&(db.course_activity.id.belongs(activities_grades))).select(
                                            db.course_activity.date_start,
                                            db.course_activity.name,
                                            db.course_activity.description,
                                            db.course_activity.date_finish,
                                            db.course_activity.id,
                                            db.course_activity.course_activity_category
                                        )
                        for act_tempo in activities_m:
                            if not report.report_restriction.is_final:
                                temp_end_act = act_tempo.date_finish
                                temp_end_act = datetime.datetime(temp_end_act.year, temp_end_act.month, temp_end_act.day)
                                end_date_activityt1 = datetime.datetime(end_date_activity.year, end_date_activity.month, end_date_activity.day)
                                if temp_end_act < end_date_activityt1:
                                    grades_log_count = int(db((db.grades_log.activity_id == act_tempo.id) & (db.grades_log.operation_log == 'insert')
                                                        & (db.grades_log.user_name == auth.user.username)).count())
                                    grades_count = int(db(db.grades.activity == act_tempo.id).count())
                                    #Check if you have the minimum of notes recorded in the activity amount that you are worth in the report
                                    if ((grades_log_count * 100) / grades_count) >= int(parameters_period.percentage_income_activity):
                                        activities_m_real.append(metric_statistics(act_tempo, 0, None))
                                else:
                                    #Future activities with metric
                                    activities_f.append(act_tempo)
                            else:
                                grades_log_count = int(db((db.grades_log.activity_id == act_tempo.id) & (db.grades_log.operation_log == 'insert')
                                                    & (db.grades_log.user_name == auth.user.username)).count())
                                grades_count = int(db(db.grades.activity == act_tempo.id).count())
                                #Check if you have the minimum of notes recorded in the activity amount that you are worth in the report
                                if ((grades_log_count * 100) / grades_count) >= int(parameters_period.percentage_income_activity):
                                    activities_m_real.append(metric_statistics(act_tempo, 0, None))
                        activities_m = activities_m_real
                        #Complete with measuring future activities
                        if not report.report_restriction.is_final:
                            activities_f_temp = db((db.course_activity.semester == cperiod.id) & (db.course_activity.assignation == report.assignation.project)
                                                & (db.course_activity.date_start >= end_date_activity)).select(
                                                    db.course_activity.name,
                                                    db.course_acvitity.description
                                                )
                            for awmt in activities_f_temp:
                                activities_f.append(awmt)
                    else:
                        #Complete with measuring activities
                        activities_m = db((db.course_activity.semester == cperiod.id) & (db.course_activity.assignation == report.assignation.project)
                                        & (db.course_activity.date_start < end_date_activity) & (~db.course_activity.id.belongs(activities_m_before))
                                        & (db.course_activity.id.belongs(activities_grades))).select(
                                            db.course_activity.date_start,
                                            db.course_activity.name,
                                            db.course_activity.description,
                                            db.course_activity.date_finish,
                                            db.course_activity.id,
                                            db.course_activity.course_activity_category,
                                        )
                        for act_tempo in activities_m:
                            if not report.report_restriction.is_final:
                                temp_end_act = act_tempo.date_finish
                                temp_end_act = datetime.datetime(temp_end_act.year, temp_end_act.month, temp_end_act.day)
                                end_date_activityt1 = datetime.datetime(end_date_activity.year, end_date_activity.month, end_date_activity.day)
                                if temp_end_act < end_date_activityt1:
                                    grades_log_count = db((db.grades_log.activity_id == act_tempo.id) & (db.grades_log.operation_log == 'insert')
                                                        & (db.grades_log.user_name==auth.user.username)).count()
                                    grades_count = db(db.grades.activity == act_tempo.id).count()
                                    #Check if you have the minimum of notes recorded in the activity amount that you are worth in the report
                                    if ((grades_log_count * 100) / grades_count) >= int(parameters_period.percentage_income_activity):
                                        activities_m_real.append(metric_statistics(act_tempo, 0, None))
                                else:
                                    #Future activities with metric
                                    activities_f.append(act_tempo)
                            else:
                                grades_log_count = db((db.grades_log.activity_id == act_tempo.id) & (db.grades_log.operation_log == 'insert')
                                                    & (db.grades_log.user_name == auth.user.username)).count()
                                grades_count = db(db.grades.activity == act_tempo.id).count()
                                #Check if you have the minimum of notes recorded in the activity amount that you are worth in the report
                                if ((grades_log_count * 100) / grades_count) >= int(parameters_period.percentage_income_activity):
                                    activities_m_real.append(metric_statistics(act_tempo, 0, None))
                        activities_m = activities_m_real
                        #Complete with measuring future activities
                        if report.report_restriction.is_final:
                            activities_f_temp = db((db.course_activity.semester == cperiod.id) & (db.course_activity.assignation == report.assignation.project)
                                                & (db.course_activity.date_start >= end_date_activity) & (~db.course_activity.id.belongs(activities_m_before))).select(
                                                    db.course_activity.name,
                                                    db.course_activity.description
                                                )
                            for awmt in activities_f_temp:
                                activities_f.append(awmt)

            if db(db.course_report_exception.project == report.assignation.project).select(db.course_report_exception.id).first() is not None:
                final_stats_flag = True

            #RECOVERY 1 y 2
            if report.report_restriction.is_final:
                #students_first_recovery
                try:
                    frt = db((db.course_first_recovery_test.semester == cperiod.id) & (db.course_first_recovery_test.project == report.assignation.project)).count()
                except:
                    frt = 0
                if frt > 0:
                    if activities_m is None: activities_m = []
                    activities_m.append(metric_statistics(report, 1, None))

                #students_second_recovery
                try:
                    srt = db((db.course_second_recovery_test.semester == cperiod.id) & (db.course_second_recovery_test.project == report.assignation.project)).count()
                except:
                    srt = 0
                if srt > 0:
                    if activities_m is None: activities_m = []
                    activities_m.append(metric_statistics(report, 2, None))

        if activities_m is None: activities_m = []
        if activities_wm is None: activities_wm = []
        if activities_f is None: activities_f = []

        activities_count += len(activities_wm) + len(activities_m)
        metrics_count += len(activities_m)
        #***********************************************************************************************************************
        #******************************************************PHASE 2 DTT******************************************************

        for req in reqs:
            if req.report_requirement.name == 'Registrar Estadisticas Finales de Curso' and report.report_restriction.is_final and final_stats == 0:
                minimal_requirements = False
                break
            if req.report_requirement.name == 'Encabezado' and report.heading is None:
                minimal_requirements = False
                break
            if req.report_requirement.name == 'Pie de Reporte' and report.footer is None:
                minimal_requirements = False
                break
            if req.report_requirement.name == 'Registrar Actividad' and activities_count == 0:
                minimal_requirements = False
                break
            if req.report_requirement.name == 'Registrar Actividad con Metricas' and metrics_count == 0:
                minimal_requirements = False
                break
            if req.report_requirement.name == 'Registrar Deserciones' and report.desertion_started is None:
                minimal_requirements = False
                break
            if req.report_requirement.name == 'Registrar Horas Completadas' and report.hours is None:
                minimal_requirements = False
                break

        if not minimal_requirements:
            session.flash = T('Selected report can\'t be accepted, it lacks mandatory blocks.')
            redirect(URL('student','index'))

        ## Validate that the report status is editable (it is either 'Draft' or 'Recheck')
        if not cpfecys.student_validation_report_status(report):
            session.flash = T('Invalid selected assignation and report. Select a valid one.') + 'INV002'
            redirect(URL('student','index'))
        ## Validate assignation
        if cpfecys.assignation_is_locked(report.assignation):
            session.flash = T('Selected report can\'t be edited. Select a valid report.')
            redirect(URL('student','index'))
        # Validate assignation belongs to this user
        assign = db((db.user_project.id == report.assignation) & (db.user_project.assigned_user == auth.user.id)).select(db.user_project.project).first()
        valid_assignation = assign is not None
        if not (report and valid_assignation):
            session.flash = T('Invalid selected assignation and report. Select a valid one.') + 'INV003'
            redirect(URL('student','index'))
        current_date = datetime.datetime.now()
        if report.status.name == 'Recheck':
            dated = datetime.datetime.now().date()
            next_date = report.score_date + datetime.timedelta(days=cpfecys.get_custom_parameters().rescore_max_days)
            if not(dated < next_date):
                session.flash = T('Selected report can\'t be edited. Select a valid report.')
                redirect(URL('student','index'))

        ## Validate that the administrator of DTT has not failed the student
        if report.dtt_approval is not None and not report.dtt_approval:
            session.flash = T('Selected report can\'t be edited. Select a valid report.')
            redirect(URL('student','index'))
            
        report.update_record(created=current_date, status=db.report_status(name = 'Grading'))

        #***********************************************************************************************************************
        #******************************************************PHASE 2 DTT******************************************************
        if report.assignation.project.area_level.name == 'DTT Tutor Académico':
            cperiod = obtain_period_report(report)
            for awm in activities_wm:
                db.log_entry.insert(
                    log_type=temp_log_type.id,
                    entry_date=current_date,
                    description=f'Nombre: "{awm.name}" Descripción: "{awm.description}"',
                    report=report.id,
                    period=cperiod.id,
                    tActivity='F',
                    idActivity=awm.id
                )

            for awm in activities_m:
                db.log_entry.insert(
                    log_type=temp_log_type.id,
                    entry_date=current_date,
                    description=awm[1],
                    report=report.id,
                    period=cperiod.id,
                    tActivity='T',
                    idActivity=awm[17]
                )
                db.log_metrics.insert(
                    description=awm[1],
                    media=awm[2],
                    error=awm[3],
                    mediana=awm[4],
                    moda=awm[5],
                    desviacion=awm[6],
                    varianza=awm[7],
                    curtosis=awm[8],
                    coeficiente=awm[9],
                    rango=awm[10],
                    minimo=awm[11],
                    maximo=awm[12],
                    total=awm[13],
                    reprobados=awm[14],
                    aprobados=awm[15],
                    created=awm[0],
                    report=report.id,
                    metrics_type=awm[16]
                )
            for awm in activities_f:
                db.log_future.insert(
                    entry_date=current_date,
                    description=f'Nombre: "{awm.name}" Descripción: "{awm.description}"',
                    report=report.id,
                    period=cperiod.id
                )
        #***********************************************************************************************************************
        #******************************************************PHASE 2 DTT******************************************************

        session.flash = T('Report sent to Grading.')
        # Notification Message
        signature = cpfecys.get_custom_parameters().email_signature or ''
        me_the_user = db(db.auth_user.id == auth.user.id).select(db.auth_user.username, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.email).first()
        message = f'''
            <html>
                El reporte:
                <b>{XML(report.report_restriction["name"])}</b><br/>
                Enviado por el estudiante: {XML(me_the_user.username)} - {XML(me_the_user.first_name)} {XML(me_the_user.last_name)}<br/>
                Fue enviado a revisión<br/><br/>
                La revisión se efectua en: {cpfecys.get_domain()}<br/>
                {signature}
            </html>'''
        # send mail to teacher and student notifying change.
        mails = []
        # retrieve teacher's email
        teachers = db((db.project.id == assign.project) & (db.user_project.project == db.project.id)
                    & (db.user_project.assigned_user == db.auth_user.id) & (db.auth_membership.user_id == db.auth_user.id)
                    & (db.auth_membership.group_id == db.auth_group.id) & (db.auth_group.role == 'Teacher')).select(db.auth_user.email)
        for teacher in teachers:
            mails.append(teacher.email)
        
        # retrieve student's email
        student_mail = me_the_user.email
        mails.append(student_mail)
        was_sent = mail.send(
                    to=mails,
                    subject='[DTT]Notificación Automática - Reporte listo a ser revisado.',
                    reply_to=student_mail,
                    message=message
                )
        #MAILER LOG
        db.mailer_log.insert(
            sent_message=message,
            destination=','.join(mails),
            result_log=f'{mail.error or ""}:{mail.result}',
            success=was_sent
        )
        redirect(URL('student','index'))
    elif request.args(0) == 'view':
        #Get the report id
        report = request.vars['report']
        # Validate that the report exists
        report = db(db.report.id == report).select(
                    db.report.id,
                    db.report.created,
                    db.report.assignation,
                    db.report.status,
                    db.report.report_restriction,
                    db.report.heading,
                    db.report.hours,
                    db.report.desertion_started,
                    db.report.desertion_gone,
                    db.report.desertion_continued,
                    db.report.footer
                ).first()
        valid = report is not None

        # Validate that the report belongs to user
        if valid: valid = cpfecys.student_validation_report_owner(report.id)
        if valid:
            semester = cpfecys.first_period.id
            if report.created.month >= 7:
                semester = cpfecys.second_period.id

            period = db((db.period_year.yearp == int(report.created.year)) & (db.period_year.period == semester)).select(db.period_year.id).first()
            teacher = db((db.auth_user.id == db.user_project.assigned_user) & (db.auth_user.id == db.auth_membership.user_id)
                    & (db.auth_membership.group_id == db.auth_group.id) & (db.auth_group.role == 'Teacher')
                    & (db.user_project.project == report.assignation.project) & (db.user_project.period == db.period_year.id)
                    & ((db.user_project.period <= period.id) & ((db.user_project.period + db.user_project.periods) > period.id))).select(db.auth_user.ALL).first()
            student = db(db.auth_user.id == auth.user.id).select().first()
            assignation_reports = db(db.report.assignation == report.assignation).select()
            response.view = 'student/report_view.html'

            #***********************************************************************************************************************
            #******************************************************PHASE 2 DTT******************************************************
            activities_wm = None
            activities_m = None
            activities_f = None
            if report.assignation.project.area_level.name == 'DTT Tutor Académico' and (report.status.name == 'Draft' or report.status.name == 'Recheck'):
                #Get the minimum and maximum date of the report
                cperiod = obtain_period_report(report)
                parameters_period = db(db.student_control_period.period_name == f'{T(cperiod.period.name)} {cperiod.yearp}').select(db.student_control_period.percentage_income_activity).first()
                init_semester, end_date_activity = report_month(cperiod.period, cperiod.yearp, report.report_restriction.name, report.report_restriction.is_final)
                activities_f = []

                #Verify that the date range of the period and the parameters are defined
                if init_semester is None or end_date_activity is None or parameters_period is None:
                    session.flash = T('Error. Is not defined date range of the report or do not have the required parameters. --- Contact the system administrator.')
                    redirect(URL('student', 'index'))
                else:
                    #Get the latest reports and are of this semester
                    before_reports_restriction = db((db.report_restriction.id < report.report_restriction) & (db.report_restriction.start_date >= init_semester)).select(db.report_restriction.id)
                    if before_reports_restriction.first() is None:
                        before_reports = []
                        before_reports.append(-1)
                    else:
                        before_reports = db((db.report.assignation == report.assignation) & (db.report.report_restriction.belongs(before_reports_restriction))).select(db.report.id)
                        if before_reports.first() is None:
                            before_reports = []
                            before_reports.append(-1)

                #Check the id of the log type thtat is activity
                temp_log_type = db(db.log_type.name == 'Activity').select(db.log_type.id).first()
                #Verify that there is a category activity report
                if temp_log_type is None:
                    session.flash = T('Error. Is not defined date range of the report or do not have the required parameters. --- Contact the system administrator.')
                    redirect(URL('student','index'))
                else:
                    #*******************Activities to record activities unless already recorded in previous reports
                    #Activities without metric
                    activities_wm_before = db((db.log_entry.log_type == temp_log_type.id) & (db.log_entry.period == cperiod.id)
                                            & (db.log_entry.tActivity == False) & (db.log_entry.report.belongs(before_reports))).select(db.log_entry.idActivity.with_alias('id'))
                    if activities_wm_before.first() is None:
                        activities_wm = db((db.course_activity_without_metric.semester == cperiod.id) & (db.course_activity_without_metric.assignation == report.assignation.project)
                                        & (db.course_activity_without_metric.date_start < end_date_activity)).select()
                        #Future activities without metric
                        if not report.report_restriction.is_final:
                            activities_f_temp = db((db.course_activity_without_metric.semester == cperiod.id) & (db.course_activity_without_metric.assignation == report.assignation.project)
                                                & (db.course_activity_without_metric.date_start >= end_date_activity)).select()
                            for awmt in activities_f_temp:
                                activities_f.append(awmt)
                    else:
                        activities_wm = db((db.course_activity_without_metric.semester == cperiod.id) & (db.course_activity_without_metric.assignation == report.assignation.project)
                                        & (~db.course_activity_without_metric.id.belongs(activities_wm_before)) & (db.course_activity_without_metric.date_start < end_date_activity)).select()
                        #Future activities without metric
                        if not report.report_restriction.is_final:
                            activities_f_temp = db((db.course_activity_without_metric.semester == cperiod.id) & (db.course_activity_without_metric.assignation == report.assignation.project)
                                                & (~db.course_activity_without_metric.id.belongs(activities_wm_before)) & (db.course_activity_without_metric.date_start >= end_date_activity)).select()
                            for awmt in activities_f_temp:
                                activities_f.append(awmt)

                    #Activities with metric
                    activities_m_before = db((db.log_entry.log_type == temp_log_type.id) & (db.log_entry.period == cperiod.id)
                                        & (db.log_entry.tActivity == True) & (db.log_entry.report.belongs(before_reports))).select(db.log_entry.idActivity.with_alias('id'))
                    activities_grades = db((db.grades.academic_assignation == db.academic_course_assignation.id) & (db.academic_course_assignation.semester == cperiod.id)
                                        & (db.academic_course_assignation.assignation == report.assignation.project)).select(db.grades.activity.with_alias('id'), distinct=True)
                    if activities_grades.first() is not None:
                        activities_m_real = []
                        if activities_m_before.first() is None:
                            #Complete with measuring activities
                            activities_m = db((db.course_activity.semester == cperiod.id) & (db.course_activity.assignation == report.assignation.project)
                                            & (db.course_activity.date_start < end_date_activity) & (db.course_activity.id.belongs(activities_grades))).select(
                                                db.course_activity.date_finish,
                                                db.course_activity.id,
                                                db.course_activity.name,
                                                db.course_activity.report_restriction,
                                                db.course_activity.description,
                                                db.course_activity.assignation
                                            )
                            for act_tempo in activities_m:
                                if not report.report_restriction.is_final:
                                    temp_end_act = act_tempo.date_finish 
                                    temp_end_act = datetime.datetime(temp_end_act.year, temp_end_act.month, temp_end_act.day)
                                    end_date_activityt1 = datetime.datetime(end_date_activity.year, end_date_activity.month, end_date_activity.day)
                                    if temp_end_act < end_date_activityt1:
                                        grades_log_count = int(db((db.grades_log.activity_id == act_tempo.id) & (db.grades_log.operation_log == 'insert')
                                                            & (db.grades_log.user_name == auth.user.username)).count())
                                        grades_count = int(db(db.grades.activity == act_tempo.id).count())
                                        #Check if you have the minimum of notes recorded in the activity amount that you are worth in the report
                                        if ((grades_log_count * 100) / grades_count) >= int(parameters_period.percentage_income_activity):
                                            activities_m_real.append(metric_statistics(act_tempo, 0, None))
                                    else:
                                        #Future activities with metric
                                        activities_f.append(act_tempo)
                                else:
                                    grades_log_count = int(db((db.grades_log.activity_id == act_tempo.id) & (db.grades_log.operation_log == 'insert') 
                                                        & (db.grades_log.user_name == auth.user.username)).count())
                                    
                                    grades_count = int(db(db.grades.activity == act_tempo.id).count())
                                    #Check if you have the minimum of notes recorded in the activity amount that you are worth in the report
                                    if ((grades_log_count * 100) / grades_count) >= int(parameters_period.percentage_income_activity):
                                        activities_m_real.append(metric_statistics(act_tempo, 0, None))
                            activities_m = activities_m_real
                            #Complete with measuring future activities
                            if not report.report_restriction.is_final:
                                activities_f_temp = db((db.course_activity.semester == cperiod.id) & (db.course_activity.assignation == report.assignation.project)
                                                    & (db.course_activity.date_start >= end_date_activity)).select()
                                for awmt in activities_f_temp:
                                    activities_f.append(awmt)
                        else:
                            #Complete with measuring activities
                            activities_m = db((db.course_activity.semester == cperiod.id) & (db.course_activity.assignation == report.assignation.project)
                                            & (db.course_activity.date_start < end_date_activity) & (~db.course_activity.id.belongs(activities_m_before))
                                            & (db.course_activity.id.belongs(activities_grades))).select(
                                                db.course_activity.date_finish,
                                                db.course_activity.id,
                                                db.course_activity.name,
                                                db.course_activity.description,
                                                db.course_activity.course_activity_category,
                                                db.course_activity.date_start
                                            )
                            for act_tempo in activities_m:
                                if not report.report_restriction.is_final:
                                    temp_end_act = act_tempo.date_finish
                                    temp_end_act = datetime.datetime(temp_end_act.year, temp_end_act.month, temp_end_act.day)
                                    end_date_activityt1 = datetime.datetime(end_date_activity.year, end_date_activity.month, end_date_activity.day)
                                    if temp_end_act < end_date_activityt1:
                                        grades_log_count = int(db((db.grades_log.activity_id == act_tempo.id) & (db.grades_log.operation_log == 'insert')
                                                            & (db.grades_log.user_name == auth.user.username)).count())
                                        grades_count = int(db(db.grades.activity == act_tempo.id).count())
                                        #Check if you have the minimum of notes recorded in the activity amount that you are worth in the report
                                        if ((grades_log_count * 100) / grades_count) >= int(parameters_period.percentage_income_activity):
                                            activities_m_real.append(metric_statistics(act_tempo, 0, None))
                                    else:
                                        #Future activities with metric
                                        activities_f.append(act_tempo)
                                else:
                                    grades_log_count = int(db((db.grades_log.activity_id == act_tempo.id) & (db.grades_log.operation_log == 'insert')
                                                        & (db.grades_log.user_name == auth.user.username)).count())
                                    grades_count = int(db(db.grades.activity == act_tempo.id).count())
                                    #Check if you have the minimum of notes recorded in the activity amount that you are worth in the report
                                    if ((grades_log_count * 100) / grades_count) >= int(parameters_period.percentage_income_activity):
                                        activities_m_real.append(metric_statistics(act_tempo, 0, None))
                            activities_m = activities_m_real
                            #Complete with measuring future activities
                            if not report.report_restriction.is_final:
                                activities_f_temp = db((db.course_activity.semester == cperiod.id) & (db.course_activity.assignation == report.assignation.project)
                                                    & (db.course_activity.date_start >= end_date_activity) & (~db.course_activity.id.belongs(activities_m_before))).select()
                                for awmt in activities_f_temp:
                                    activities_f.append(awmt)

                #RECOVERY 1 y 2
                if report.report_restriction.is_final:
                    #students_first_recovery
                    try:
                        frt = int(db((db.course_first_recovery_test.semester == cperiod.id) & (db.course_first_recovery_test.project == report.assignation.project)).count())
                    except:
                        frt = int(0)
                    if frt > 0:
                        if activities_m is None:
                            activities_m = []
                        activities_m.append(metric_statistics(report, 1, None))

                    #students_second_recovery
                    try:
                        srt = int(db((db.course_second_recovery_test.semester == cperiod.id) & (db.course_second_recovery_test.project == report.assignation.project)).count())
                    except:
                        srt = int(0)
                    if srt > 0:
                        if activities_m is None:
                            activities_m = []
                        activities_m.append(metric_statistics(report, 2, None))

            if activities_m is None: activities_m = []
            if activities_wm is None: activities_wm = []
            if activities_f is None: activities_f = []
            #***********************************************************************************************************************
            #******************************************************PHASE 2 DTT******************************************************
            return dict(
                log_types=db(db.log_type.id > 0).select(),
                assignation_reports=assignation_reports,
                logs=db((db.log_entry.report == report.id)).select(),
                activities_wm=activities_wm,
                metrics=db((db.log_metrics.report == report.id)).select(),
                activities_m=activities_m,
                final_r=db(db.log_final.report == report.id).select(),
                anomalies=db((db.log_type.name == 'Anomaly') & (db.log_entry.log_type == db.log_type.id)
                        & (db.log_entry.report == report.id)).count(),
                activities_f=activities_f,
                markmin_settings=cpfecys.get_markmin,
                report=report,
                student=student,
                teacher=teacher
            )
        else:
            session.flash = T('Selected report can\'t be viewed. Select a valid report.')
            redirect(URL('student', 'index'))
    else:
        redirect(URL('student', 'index'))
    raise HTTP(404)

@cache.action()
@auth.requires_login()
@auth.requires_membership('Student')
def download():
    item = None
    try:
        item = db(db.item.uploaded_file == request.args[0]).select(db.item.assignation).first()
        if item is not None and item.assignation.assigned_user == auth.user.id:
            return response.download(request, db)
        else:
            session.flash = T('Access Forbidden')
            redirect(URL('default', 'home'))
    except IndexError:
        session.flash = "Sin datos"
        redirect(URL('default', 'home'))

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Academic'))
def update_data():
    form = None
    if auth.user is not None:
        cuser = db(db.auth_user.id == auth.user.id).select(
            db.auth_user.first_name,
            db.auth_user.last_name,
            db.auth_user.email,
            db.auth_user.password,
            db.auth_user.phone,
            db.auth_user.working,
            db.auth_user.work_address,
            db.auth_user.company_name,
            db.auth_user.work_phone,
            db.auth_user.home_address
        ).first()
        
        try:
            div_photo = DIV(
                LABEL('Foto'),
                INPUT(_name="photo", _class="upload form-control-file", _type="file", _id="photo",
                        requires=[
                            IS_IMAGE(extensions =('jpeg', 'png'), maxsize=(200, 300), 
                                     error_message='Sólo se aceptan archivos con extensión png|jpg con tamaño maximo de 200x300px')
                        ],
                        _value=cuser.photo
                )
            )
        except:
            div_photo = DIV(
                LABEL('Foto'),
                INPUT(_name="photo", _class="upload form-control-file", _type="file", _id="photo",
                        requires=[
                            IS_IMAGE(extensions =('jpeg', 'png'), maxsize=(200, 300), 
                                     error_message='Sólo se aceptan archivos con extensión png|jpg con tamaño maximo de 200x300px')
                        ],
                        _value="/cpfecys/static/images/iconos_reclutamiento/profile.png"
                )
            )

        form = FORM( 
            DIV(
                LABEL('Nombres'),
                INPUT(_name="first_name", _type="text", _id="first_name",
                    _value=cuser.first_name, _class="form-control", requires=IS_NOT_EMPTY())
            ),
            DIV(
                LABEL('Apellidos'),
                INPUT(_name="last_name", _type="text", _id="last_name",
                        _value=cuser.last_name, _class="form-control", requires=IS_NOT_EMPTY())
            ),
            DIV(
                LABEL('Correo electrónico'),
                INPUT(_name="email", _type="text", _id="email",
                        _value=cuser.email, _class="form-control", requires=IS_NOT_EMPTY())
            ),
            DIV(
                LABEL('Contraseña (deje la misma para no cambiarla)'),
                INPUT(_name="password", _type="password", _id="password",
                        _value=cuser.password, _class="form-control", requires=IS_NOT_EMPTY())
            ),
            DIV(
                LABEL('Repetir contraseña: (Deje en blanco para no cambiar)'),
                INPUT(_name="repass", _class="form-control", _type="password", _id="repass")
            ),
            DIV(
                LABEL('Teléfono'),
                INPUT(_name="phone", _type="text", _id="phone", _value=cuser.phone,
                        _class="form-control", requires=IS_LENGTH(minsize=8, maxsize=12))
            ),
            DIV(
                INPUT(_name="working", _type="checkbox", _id="working", _class="form-check-input", _value=cuser.working, _checked=cuser.working),
                LABEL('Trabaja'),
                _class="form-check form-group mt-4"
            ),
            DIV(
                LABEL('Dirección laboral'),
                INPUT(_name="work_address", _type="text", _id="work_address", _class="form-control", _value=cuser.work_address)
            ),
            DIV(
                LABEL('Nombre de la empresa'),
                INPUT(_name="company_name", _type="text", _id="company_name", _class="form-control", _value=cuser.company_name)
            ),
            DIV(
                LABEL('Teléfono de trabajo'),
                INPUT(_name="work_phone", _class="form-control", _type="text", 
                    _id="work_phone", _value=cuser.work_phone)
            ),
            DIV(
                LABEL('Dirección domiciliar'),
                INPUT(_name="home_address", _type="text", _id="home_address",
                        _class="form-control", _value=cuser.home_address)
            ),
            div_photo,
            DIV(
                INPUT(_type='submit', _id="update_data", _value='Actualizar perfil', _class="btn btn-primary"),
                _class='mt-2'
            ),
            _class="form-horizontal"
        )

        if form.process().accepted:
            first_name = request.vars['first_name']
            last_name = request.vars['last_name']
            email = request.vars['email']
            password = request.vars['password']
            repass = request.vars['repass']
            phone = request.vars['phone']
            working = request.vars['working']
            work_address = request.vars['work_address']
            company_name = request.vars['company_name']
            work_phone = request.vars['work_phone']
            home_address = request.vars['home_address']
            photo = request.vars['photo']

            #TODO analyze for aditional security steps
            cuser = db(db.auth_user.id == auth.user.id).select().first()
            if cuser is not None:
                cuser.first_name = first_name
                cuser.last_name = last_name
                cuser.email = email
                cuser.phone = phone
                cuser.home_address = home_address
                cuser.photo = photo
                cuser.data_updated = True
                if len(repass) > 0 and password == repass:
                    cuser.password = db.auth_user.password.validate(password)[0]

                if working:
                    cuser.working = working
                    cuser.work_address = work_address
                    cuser.work_phone = work_phone
                    cuser.company_name = company_name
                else:
                    cuser.working = working
                    cuser.work_address = ''
                    cuser.work_phone = ''
                    cuser.company_name = ''

                cuser.update_record()
                db.commit()
                response.flash = T('User data updated!')
                redirect(URL('default', 'home'))
            else:
                response.flash = 'Error!'
        elif form.errors:
            response.flash = T('form has errors')
        else:
            response.flash = T('please fill the form')

    return dict(form=form)

@cache.action()
@auth.requires_login()
@auth.requires_membership('Student')
def download_deliverable():
    args = request.args

    if len(args) != 1:
        raise HTTP(404)

    filename = args[0].strip()
    try:
        file = ds_utils.retrieve_file(filename, request.folder)
    except:
        raise HTTP(404)

    response.headers["Content-Type"] = contenttype.contenttype(filename)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    stream = response.stream(file, request=request)

    raise HTTP(200, stream, **response.headers)

# *********** Inicio - Prácticas Finales(DS) - Fernando Reyes *************

@auth.requires_login()
@auth.requires_membership('Student')
def stationery():
    args = request.args
    new_dict = {}
    assignations = {}

    def control_documents_period(user_project):
        query_control_docs = ds_utils.get_all_assignations_document_control_period(user_project)
        return db.executesql(query_control_docs, as_dict=True)

    def doc_type_document_delivered(control_period, user_project):
        query_doc_type = ds_utils.get_doc_type_document_delivered_by_student(control_period, user_project)
        return db.executesql(query_doc_type, as_dict=True)

    def documents_delivered(control_period, user_project, doc_type):
        query_control_docs = ds_utils.get_all_documents_delivered_by_user_project(control_period, user_project, doc_type)
        return db.executesql(query_control_docs, as_dict=True)

    def is_in_range_date(start_date, finish_date, status=None):
        now_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if status is None:
            if not (start_date.strftime("%Y-%m-%d %H:%M:%S") <= now_date <= finish_date.strftime("%Y-%m-%d %H:%M:%S")):
                return False
        else:
            if status == 'Pending' and not (start_date.strftime("%Y-%m-%d %H:%M:%S") <= now_date <= finish_date.strftime("%Y-%m-%d %H:%M:%S")):
                return False
        return True

    if len(args) == 0:
        new_dict['type'] = 'list'
        # obteniendo listado de proyectos asignados
        query_assignations = ds_utils.get_all_assignations_student(auth.user.id)
        assignations = db.executesql(query_assignations, as_dict=True)
    elif len(args) == 2:
        item_action = args[0]
        option = args[1]
        new_dict['type'] = option

        if item_action == 'item' and (option == 'create' or option == 'edit'):
            # validando que venga el parametro control period
            if 'deliverable' not in request.vars:
                session.flash = 'No existe entregable'
                redirect(URL('student', 'stationery'))

            # validando que exista entregable
            query = ds_utils.get_document_delivered_by_user(request.vars.deliverable.strip(), auth.user.id)
            deliverable = db.executesql(query, as_dict=True)

            if len(deliverable) < 1:
                session.flash = 'No existe entregable'
                redirect(URL('student', 'stationery'))

            # validando que este entre el rango de fechas
            if not is_in_range_date(deliverable[0]['date_start'], deliverable[0]['date_finish']):
                session.flash = 'Fecha de entrega ya expiro, no hay acciones disponibles'
                redirect(URL('student', 'stationery'))

            new_dict['item'] = deliverable[0]

            # verificando extension del archivo
            substring_ext = deliverable[0]['extension'].split(",")
            extensiones = ''
            for ext in substring_ext:
                extensiones += ext.strip() if extensiones == '' else "|" + ext.strip()
            extensiones = "(" + extensiones + ")"

            # pasando megabytes a bytes (MB * kB * B)
            max_size = deliverable[0]['max_size'] * 1024 * 1024
            message = "Tamaño máximo del archivo es de {} MB.".format(deliverable[0]['max_size'])

            upload_form = FORM(
                DIV(
                    DIV(LABEL('Seleccione archivo a subir', _for='fileToUpload', _class='col-sm-3 col-form-label')),
                    DIV(
                        INPUT(_type='file', _class='form-control-file', _name='fileToUpload', _id='fileToUpload', _style='margin-top:5px;',
                                requires=[
                                    IS_NOT_EMPTY(error_message='Debe seleccionar un archivo a subir.'),
                                    IS_UPLOAD_FILENAME(extension=str(extensiones), error_message='Tipo de archivo no permitido.'),
                                    IS_LENGTH(max_size, error_message=message)
                                ]
                        ),
                        _class='col-sm-9'
                    ),
                    _class='form-group row'
                ),
                BUTTON(
                    SPAN(_class='fa fa-upload'),
                    ' Subir archivo',
                    _type='submit', _class='btn btn-primary'
                )
            )

            if upload_form.accepts(request.vars, formname='upload_form'):
                if request.vars.fileToUpload is not None:
                    name = f'deliverable-{auth.user.username}'

                    result = ds_utils.save_file(
                                request.vars.fileToUpload.file,
                                request.vars.fileToUpload.filename,
                                request.folder,
                                name,
                                deliverable[0]['file_uploaded']
                            )
                    if result is not None:
                        values = {
                            'file_uploaded': result,
                            'comment': None,
                            'uploaded_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'status': 'Delivered'
                        }
                        condition = {'id': int(request.vars.deliverable)}
                        try:
                            update_query = ds_utils.create_script_string('ds_document_delivered', 'U', values, condition)
                            db.executesql(update_query)
                            session.flash = 'Archivo guardado exitosamente'
                        except:
                            session.flash = 'No se pudo guardar el archivo'

                        redirect(URL('student', 'stationery'))
                    else:
                        new_dict['message'] = 'Error al guardar el archivo'
                else:
                    new_dict['message'] = 'Debe seleccionar un archivo a subir.'

            return dict(action=new_dict, form=upload_form)
        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    else:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    return dict(
        assignations=assignations,
        control_documents_period=control_documents_period,
        doc_type_document_delivered=doc_type_document_delivered,
        documents_delivered=documents_delivered,
        is_in_range_date=is_in_range_date,
        action=new_dict
    )

#*********** Fin - Prácticas Finales(DSA) - Fernando Reyes *************

def obtain_period_report(report):
    #Get the minimum and maximum date of the report
    tmp_period = 1
    tmp_year = report.report_restriction.start_date.year
    if report.report_restriction.start_date.month >= 6:
        tmp_period = 2
    return db((db.period_year.yearp == tmp_year) & (db.period_year.period == tmp_period)).select(db.period_year.yearp, db.period_year.id, db.period_year.period).first()

def metric_statistics(act_tempo, recovery, data_incoming):
    activity = []
    if data_incoming is None:
        if recovery == 1 or recovery == 2:
            if recovery == 1:
                #Description of Activity
                description = 'Nombre: "PRIMERA RETRASADA"'
                temp_data = db((db.course_first_recovery_test.semester == obtain_period_report(act_tempo).id) & (db.course_first_recovery_test.project == act_tempo.assignation.project)).select(db.course_first_recovery_test.grade, orderby=db.course_first_recovery_test.grade)
            else:
                #Description of Activity
                description = 'Nombre: "SEGUNDA RETRASADA"'
                temp_data = db((db.course_second_recovery_test.semester == obtain_period_report(act_tempo).id) & (db.course_second_recovery_test.project == act_tempo.assignation.project)).select(db.course_second_recovery_test.grade, orderby=db.course_second_recovery_test.grade)
            
            data = []
            sum_data = float(0)
            sum_data_squared = float(0)
            total_reprobate = 0
            total_approved = 0
            for d1 in temp_data:
                if d1.grade is None:
                    data.append(float(0))
                    total_reprobate += 1
                else:
                    data.append(float(d1.grade))
                    sum_data += float(d1.grade)
                    sum_data_squared += (float(d1.grade) * float(d1.grade))
                    if float(d1.grade) >= float(61):
                        total_approved += 1
                    else:
                        total_reprobate += 1
        else:
            #Description of Activity
            description = f'Nombre: "{act_tempo.name}" Descripción: "{act_tempo.description}"'
            
            #*********************************************Statistics Activity*********************************************
            #Get the data
            temp_data = db(db.grades.activity == act_tempo.id).select(db.grades.grade, orderby=db.grades.grade)

            data = []
            sum_data = float(0)
            sum_data_squared = float(0)
            total_reprobate = 0
            total_approved = 0
            for d1 in temp_data:
                if d1.grade is None:
                    data.append(float(0))
                    total_reprobate += 1
                else:
                    data.append(float(d1.grade))
                    sum_data += float(d1.grade)
                    sum_data_squared += (float(d1.grade) * float(d1.grade))
                    if float(d1.grade) >= float(61):
                        total_approved += 1
                    else:
                        total_reprobate += 1
    else:
        data = []
        sum_data = float(0)
        sum_data_squared = float(0)
        total_reprobate = 0
        total_approved = 0
        for d1 in data_incoming:
            if d1 is None:
                data.append(float(0))
                total_reprobate += 1
            else:
                data.append(float(d1))
                sum_data += float(d1)
                sum_data_squared += (float(d1) * float(d1))
                if float(d1) >= float(61):
                    total_approved += 1
                else:
                    total_reprobate += 1
    
    #*********************************************
    #Total Students
    total_students = int(len(data))
    
    #*********************************************
    #Mean
    mean = float(sum_data / total_students)
    
    #Variance
    try:
        variance = ((sum_data_squared / total_students) - (mean * mean))
    except:
        variance = float(0)
    
    #Standard Deviation
    try:
        standard_deviation = math.sqrt(variance)
    except:
        standard_deviation = float(0)
    
    #Standard Error
    try:
        standard_error = standard_deviation / math.sqrt(total_students)
    except:
        standard_error = float(0)
    
    #Kurtosis
    try:
        #Numerator
        numerator = 0
        for i in data:
            numerator += (i - mean) * (i - mean) * (i - mean) * (i - mean)
        numerator *= total_students
        
        #Denominator
        denominator = 0
        for i in data:
            denominator += (i - mean) * (i - mean)
        denominator = denominator * denominator
        
        #Fraction
        kurtosis = (numerator / denominator) - 3
    except:
        kurtosis = float(0)
    
    #Minimum
    minimum = float(data[0])
    if total_students == 1:
        #Maximum
        maximum = float(data[0])
        #Rank
        rank = float(0)
        #Median
        median = float(sum_data)
        #Mode
        mode = float(sum_data)
    else:
        #Maximum
        maximum = float(data[total_students - 1])
        #Rank
        rank = float(data[total_students - 1] - data[0])
        #Median
        if total_students % 2 == 1:
            median = float(data[total_students // 2])
        else:
            i = total_students // 2
            median = float((data[i - 1] + data[i]) / 2)
        #Mode
        try:
            table = collections.Counter(iter(data)).most_common()
            maxfreq = table[0][1]
            for i in range(1, len(table)):
                if table[i][1] != maxfreq:
                    table = table[:i]
                    break
            mode = float(table[0][0])
        except:
            mode = minimum

    #Skewness
    try:
        skewness = float((3 * (mean - median)) / standard_error)
    except:
        skewness = float(0)

    #**********************************************
    #Metric Type
    if data_incoming is None:
        if recovery == 1 or recovery == 2:
            if recovery == 1:
                metric_type = db(db.metrics_type.name == 'PRIMERA RETRASADA').select(db.metrics_type.id).first()[db.metrics_type.id]
            else:
                metric_type = db(db.metrics_type.name == 'SEGUNDA RETRASADA').select(db.metrics_type.id).first()[db.metrics_type.id]
        else:
            first_proyect_alternatives = [
                "PRIMER PROYECTO", "1ER PROYECTO", "1ER. PROYECTO",
                "PROYECTO1", "PROYECTO 1", "PROYECTO NO.1",
                "PROYECTO NO1", "PROYECTO NUMERO 1", "PROYECTO NUMERO1",
                "PROYECTO #1", "PROYECTO#1"
            ]
            second_proyect_alternatives = [
                "SEGUNDO PROYECTO", "2DO PROYECTO", "2DO. PROYECTO",
                "PROYECTO2", "PROYECTO 2", "PROYECTO NO.2",
                "PROYECTO NO2", "PROYECTO NUMERO 2", "PROYECTO NUMERO2",
                "PROYECTO #2", "PROYECTO#2"
            ]
            category = act_tempo.course_activity_category.category.category.upper()
            metric_type = None
            if category == 'TAREAS':
                metric_type = db(db.metrics_type.name == 'TAREA').select(db.metrics_type.id).first()[db.metrics_type.id]
            elif category == 'EXAMEN CORTO':
                metric_type = db(db.metrics_type.name == 'EXAMEN CORTO').select(db.metrics_type.id).first()[db.metrics_type.id]
            elif category == 'HOJAS DE TRABAJO':
                metric_type = db(db.metrics_type.name == 'HOJA DE TRABAJO').select(db.metrics_type.id).first()[db.metrics_type.id]
            elif category == 'PARCIALES':
                metric_type = db(db.metrics_type.name == act_tempo.name.upper()).select(db.metrics_type.id).first()[db.metrics_type.id]
            elif category == 'EXAMEN FINAL':
                metric_type = db(db.metrics_type.name == 'EXAMEN FINAL').select(db.metrics_type.id).first()[db.metrics_type.id]
            elif category == 'PRACTICAS':
                metric_type = db(db.metrics_type.name == 'PRACTICA').select(db.metrics_type.id).first()[db.metrics_type.id]
            elif category == 'PROYECTOS':
                name_search = act_tempo.name.upper()
                if "FASE FINAL" in name_search:
                    metric_type = db(db.metrics_type.name == 'FASE FINAL').select(db.metrics_type.id).first()[db.metrics_type.id]
                elif "FASE" in name_search:
                    metric_type = db(db.metrics_type.name == 'FASE DE PROYECTO').select(db.metrics_type.id).first()[db.metrics_type.id]
                elif any(first_proyect_alternative in name_search for first_proyect_alternative in first_proyect_alternatives):
                    metric_type = db(db.metrics_type.name == 'PROYECTO 1').select(db.metrics_type.id).first()[db.metrics_type.id]
                elif any(second_proyect_alternative in name_search for second_proyect_alternative in second_proyect_alternatives):
                    metric_type = db(db.metrics_type.name == 'PROYECTO 2').select(db.metrics_type.id).first()[db.metrics_type.id]
            if metric_type is None:
                metric_type = db(db.metrics_type.name == 'OTRA ACTIVIDAD').select(db.metrics_type.id).first()[db.metrics_type.id]

    #******************************************************
    #Fill the activity
    if data_incoming is None:
        if recovery == 1 or recovery == 2:
            activity.append(datetime.datetime.now().date())
        else:
            activity.append(act_tempo.date_start)
        activity.append(description)
    
    activity.append(round(mean, 2))
    activity.append(round(standard_error, 2))
    activity.append(round(median, 2))
    activity.append(round(mode, 2))
    activity.append(round(standard_deviation, 2))
    activity.append(round(variance, 2))
    activity.append(round(kurtosis, 2))
    activity.append(round(skewness, 2))
    activity.append(round(rank, 2))
    activity.append(round(minimum, 2))
    activity.append(round(maximum, 2))
    #Total Students
    activity.append(total_students)
    #Total Reprobate
    activity.append(total_reprobate)
    #Total Approved
    activity.append(total_approved)
    #Metric Type
    if data_incoming is None:
        activity.append(int(metric_type))
        if recovery == 1:
            activity.append(-1)
        elif recovery == 2:
            activity.append(-2)
        else:
            activity.append(act_tempo.id)

    #Activity to return
    return activity

def final_metric(cperiod, report):
    final_stats_vec = []

    #***********************************************************************************************
    #********************************Attendance and dropout in exams********************************
    #students_minutes
    try:
        final_stats_vec.append(int(db((db.academic_course_assignation.semester == cperiod.id) & (db.academic_course_assignation.assignation == report.assignation.project)).count()))
    except:
        final_stats_vec.append(int(0))

    #students_partial
    try:
        partials = db(db.activity_category.category == 'Parciales').select(db.activity_category.id).first()
        cat_partials = db((db.course_activity_category.category == partials.id) & (db.course_activity_category.semester == cperiod.id)
                        & (db.course_activity_category.assignation == report.assignation.project) & (db.course_activity_category.laboratory == False)).select(db.course_activity_category.id).first()
        partials_query = db((db.course_activity.course_activity_category == cat_partials.id) & (db.course_activity.semester == cperiod.id)
                        & (db.course_activity.assignation == report.assignation.project) & (db.course_activity.laboratory == False))
        
        partials_select = partials_query.select(db.course_activity.id)
        grades_count = db(db.grades.activity.belongs(partials_select)).count()
        course_activity_count = partials_query.count()
        final_stats_vec.append(int(grades_count / course_activity_count))
    except:
        final_stats_vec.append(int(0))

    #students_final
    try:
        final = db(db.activity_category.category == 'Examen Final').select(db.activity_category.id).first()
        cat_final = db((db.course_activity_category.category == final.id) & (db.course_activity_category.semester == cperiod.id)
                    & (db.course_activity_category.assignation == report.assignation.project) & (db.course_activity_category.laboratory == False)).select(db.course_activity_category.id).first()
        final = db((db.course_activity.course_activity_category == cat_final.id)&(db.course_activity.semester == cperiod.id)
                & (db.course_activity.assignation == report.assignation.project) & (db.course_activity.laboratory == False)).select(db.course_activity.id)
        final_stats_vec.append(int(db(db.grades.activity.belongs(final)).count()))
    except:
        final_stats_vec.append(int(0))

    #students_first_recovery
    try:
        final_stats_vec.append(int(db((db.course_first_recovery_test.semester == cperiod.id) & (db.course_first_recovery_test.project == report.assignation.project)).count()))
    except:
        final_stats_vec.append(int(0))

    #students_second_recovery
    try:
        final_stats_vec.append(int(db((db.course_second_recovery_test.semester == cperiod.id) & (db.course_second_recovery_test.project == report.assignation.project)).count()))
    except:
        final_stats_vec.append(int(0))

    #Students
    students = db((db.academic_course_assignation.semester == cperiod.id) & (db.academic_course_assignation.assignation == report.assignation.project)).select(
                    db.academic_course_assignation.id,
                    db.academic_course_assignation.carnet
                )

    #***********************************************************************************************
    #********************************FINAL RESULTS OF LABORATORY************************************
    #students_in_lab
    exist_lab = False
    total_class = 0.0
    total_lab = 0.0
    total_final_lab = 0.0
    total_w = 0.0
    try:
        course_category = db((db.course_activity_category.semester == cperiod.id) & (db.course_activity_category.assignation == report.assignation.project)
                        & (db.course_activity_category.laboratory == False)).select(
                            db.course_activity_category.grade,
                            db.course_activity_category.category,
                            db.course_activity_category.id,
                            db.course_activity_category.specific_grade
                        )
        cat_course_temp = None
        cat_vec_course_temp = []
        course_activities = []
        for category_c in course_category:
            total_w += float(category_c.grade)
            if category_c.category.category == "Laboratorio":
                exist_lab = True
                total_lab = float(category_c.grade)
                cat_vec_course_temp.append(category_c)
            elif category_c.category.category == "Examen Final":
                var_final_grade = category_c.grade
                cat_course_temp = category_c
            else:
                cat_vec_course_temp.append(category_c)
                course_activity = db((db.course_activity.semester == cperiod.id) & (db.course_activity.assignation == report.assignation.project)
                                    & (db.course_activity.laboratory == False) & (db.course_activity.course_activity_category == category_c.id)).select(
                                        db.course_activity.id,
                                        db.course_activity.grade
                                    )
                course_activities.append(course_activity)
        if cat_course_temp is not None:
            cat_vec_course_temp.append(cat_course_temp)
            course_activity = db((db.course_activity.semester == cperiod.id) & (db.course_activity.assignation == report.assignation.project)
                                & (db.course_activity.laboratory == False) & (db.course_activity.course_activity_category == cat_course_temp.id)).select(
                                    db.course_activity.id,
                                    db.course_activity.grade
                                )
            course_activities.append(course_activity)
        course_category = cat_vec_course_temp
        total_class = total_w

        total_w = 0.0
        lab_category = None
        cat_lab_temp = None
        cat_vec_lab_temp = []
        lab_activities = None
        validate_laboratory = None
        lab_category = db((db.course_activity_category.semester == cperiod.id) & (db.course_activity_category.assignation == report.assignation.project)
                        & (db.course_activity_category.laboratory == True)).select(
                            db.course_activity_category.category,
                            db.course_activity_category.grade,
                            db.course_activity_category.id,
                            db.course_activity_category.specific_grade
                        )
        if lab_category.first() is not None:
            validate_laboratory = db((db.validate_laboratory.semester == cperiod.id) & (db.validate_laboratory.project == report.assignation.project)).select(
                                        db.validate_laboratory.carnet,
                                        db.validate_laboratory.grade
                                    )
            lab_activities = []
            for category_l in lab_category:
                if category_l.category.category == "Examen Final":
                    total_w += float(category_l.grade)
                    cat_lab_temp = category_l
                else:
                    cat_vec_lab_temp.append(category_l)
                    total_w += float(category_l.grade)
                    course_activity = db((db.course_activity.semester == cperiod.id) & (db.course_activity.assignation == report.assignation.project)
                                        & (db.course_activity.laboratory == True) & (db.course_activity.course_activity_category == category_l.id)).select()
                    lab_activities.append(course_activity)
            if cat_lab_temp is not None:
                cat_vec_lab_temp.append(cat_lab_temp)
                lab_activity = db((db.course_activity.semester == cperiod.id) & (db.course_activity.assignation == report.assignation.project)
                                & (db.course_activity.laboratory == True) & (db.course_activity.course_activity_category == cat_lab_temp.id)).select()
                lab_activities.append(lab_activity)
            lab_category = cat_vec_lab_temp
            total_final_lab = total_w

        requirement = db((db.course_requirement.semester == cperiod.id) & (db.course_requirement.project == report.assignation.project)).select(db.course_requirement.id).first()
    except:
        total_class = 0.0
        total_final_lab = 0.0

    #COMPUTING LABORATORY NOTES
    students_in_lab = []
    temp_students_in_lab = []
    approved = 0
    reprobate = 0
    sum_laboratory_grades = 0
    try:
        if total_final_lab == 100.0:
            for t1 in students:
                temp_data = []
                total_category = 0.0
                is_validate = False
                #<!--Revalidation of laboratory-->
                for validate in validate_laboratory:
                    if validate.carnet == t1.carnet:
                        is_validate = True
                        temp_data.append(t1.carnet.carnet)
                        temp_data.append(int(round(validate.grade, 0)))
                        students_in_lab.append(temp_data)

                #<!--Doesnt has a revalidation-->
                if not is_validate:
                    #<!--Position in the vector of activities-->
                    pos_vcc_lab = 0
                    #<!--Vars to the control of grade of the student-->
                    total_category_lab = 0.0
                    total_activities_lab = 0
                    total_carry_lab = 0.0

                    #<!--****************************************FILL THE GRADES OF THE STUDENT****************************************-->
                    #<!--LAB ACTIVITIES-->
                    for category_Lab in lab_category:
                        total_category_lab = 0.0
                        total_activities_lab = 0
                        for c_lab in lab_activities[pos_vcc_lab]:
                            student_grade = db((db.grades.activity == c_lab.id) & (db.grades.academic_assignation == t1.id)).select(db.grades.grade).first()
                            if not (student_grade is None or student_grade.grade is None):
                                if category_Lab.specific_grade:
                                    total_category_lab += float((student_grade.grade * c_lab.grade) / 100)
                                else:
                                    total_category_lab += float(student_grade.grade)
                            total_activities_lab += 1
                        
                        if not category_Lab.specific_grade:
                            if total_activities_lab == 0:
                                total_activities_lab = 1
                            total_activities_lab *= 100
                            total_category_lab = float((total_category_lab * float(category_Lab.grade)) / float(total_activities_lab))
                        total_carry_lab += total_category_lab
                        pos_vcc_lab += 1
                    
                    temp_data.append(t1.carnet.carnet)
                    temp_data.append(int(round(total_carry_lab, 0)))
                    students_in_lab.append(temp_data)
                    temp_students_in_lab.append(temp_data)
                    sum_laboratory_grades += int(round(total_carry_lab, 0))
                    if int(round(total_carry_lab, 0)) < 61: reprobate += 1
                    else: approved+=1

            #APPROVED
            final_stats_vec.append(approved)
            #FAILED
            final_stats_vec.append(reprobate)
            #MEAN
            final_stats_vec.append(float(sum_laboratory_grades) / float(len(temp_students_in_lab)))
            #AVERAGE
            final_stats_vec.append(float((float(approved) / float(len(temp_students_in_lab))) * 100.0))
        else:
            #APPROVED
            final_stats_vec.append(0)
            #FAILED
            final_stats_vec.append(0)
            #MEAN
            final_stats_vec.append(0)
            #AVERAGE
            final_stats_vec.append(0)
    except:
        final_stats_vec.extend([0] * 8)
    
    #Class Final Results
    data_final_class = []
    try:
        if total_class == 100:
            for t1 in students:
                pos_student = 0
                pos_vcc = 0
                total_category = 0.0
                total_activities = 0
                total_carry = 0.0
                for category in course_category:
                    if category.category.category == "Examen Final":
                        total_cary = int(round(total_carry, 0))

                    total_carry = int(round(total_carry, 0))
                    total_category = 0.0
                    total_activities = 0
                    for c in course_activities[pos_vcc]:
                        student_grade = db((db.grades.activity == c.id) & (db.grades.academic_assignation == t1.id)).select(db.grades.grade).first()
                        if not (student_grade is None or student_grade.grade is None):
                            if category.specific_grade:
                                total_category += float((student_grade.grade * c.grade) / 100)
                            else:
                                total_category += float(student_grade.grade)
                        total_activities += 1
                    if not category.specific_grade:
                        if total_activities == 0:
                            total_activities = 1
                        total_activities *= 100
                        total_category=float((total_category*float(category.grade))/float(total_activities))
                    total_category = int(round(total_category, 0))
                    total_carry += total_category
                    pos_vcc += 1
                
                #Make
                if exist_lab:
                    total_category = float((int(students_in_lab[pos_student][1]) * total_lab) / 100)
                    total_carry += total_category

                if requirement is not None:
                    if db((db.course_requirement_student.carnet == t1.carnet)&(db.course_requirement_student.requirement == requirement.id)).select(db.course_requirement_student.id).first() is not None:
                        data_final_class.append(int(round(total_carry, 0)))
                    else:
                        data_final_class.append(0)
                else:
                    data_final_class.append(int(round(total_carry, 0)))
                pos_student += 1

            #Calculate metric_statistics
            data_final_class = sorted(data_final_class)
            data_final_class = metric_statistics(None, 0, data_final_class)
            for pos_final in data_final_class:
                final_stats_vec.append(pos_final)
        else:
            final_stats_vec.extend([0] * 22)
    except:
        final_stats_vec.extend([0] * 22)

    return final_stats_vec

@auth.requires_login()
@auth.requires_membership('Student')
def report_header():
    if request.args(0) == 'create':
        report = request.vars['report']
        content = request.vars['report-content']
        ## Get the report id
        report = db(db.report.id == report).select(
                    db.report.id,
                    db.report.assignation,
                    db.report.score_date,
                    db.report.report_restriction,
                    db.report.status
                ).first()
        valid = report is not None and content is not None

        ## Validate assignation
        if valid: valid = not cpfecys.assignation_is_locked(report.assignation)
        ## Validate that the report belongs to user
        if valid: valid = cpfecys.student_validation_report_owner(report.id)
        ## Validate that the report status is editable (it is either 'Draft' or 'Recheck')
        if valid: valid = cpfecys.student_validation_report_status(report)
        if valid:
            report.heading = content
            report.update_record()
            session.flash = T('Report updated.')
            redirect(URL('student', 'report/edit', vars=dict(report=report.id)))
        else:
            session.flash = T('Selected report can\'t be edited. Select a valid report.')
            redirect(URL('student','index'))
    elif request.args(0) == 'update':
        report = request.vars['report']
        content = request.vars['report-content']
        report = db(db.report.id == report).select(
                    db.report.id,
                    db.report.assignation,
                    db.report.score_date,
                    db.report.report_restriction,
                    db.report.status
                ).first()
        valid = report is not None and content is not None

        ## Validate assignation
        if valid: valid = not cpfecys.assignation_is_locked(report.assignation)
        ## Validate that the report belongs to user
        if valid: valid = cpfecys.student_validation_report_owner(report.id)
        ## Validate that the report status is editable (it is either 'Draft' or 'Recheck')
        if valid: valid = cpfecys.student_validation_report_status(report)
        if valid:
            report.heading = content
            report.update_record()
            session.flash = T('Report updated.')
            redirect(URL('student','report/edit', vars=dict(report=report.id)))
        else:
            session.flash = T('Selected report can\'t be edited. Select a valid report.')
            redirect(URL('student','index'))
    elif request.args(0) == 'delete':
        report = request.vars['report']
        report = db(db.report.id == report).select(
                    db.report.id,
                    db.report.assignation,
                    db.report.score_date,
                    db.report.report_restriction,
                    db.report.status
                ).first()
        valid = report is not None

        ## Validate assignation
        if valid: valid = not cpfecys.assignation_is_locked(report.assignation)
        ## Validate that the report belongs to user
        if valid: valid = cpfecys.student_validation_report_owner(report.id)
        ## Validate that the report status is editable (it is either 'Draft' or 'Recheck')
        if valid: valid = cpfecys.student_validation_report_status(report)
        if valid:
            report.heading = None
            report.update_record()
            session.flash = T('Report updated.')
            redirect(URL('student','report/edit', vars=dict(report=report.id)))
        else:
            session.flash = T('Selected report can\'t be edited. Select a valid report.')
            redirect(URL('student','index'))
    raise HTTP(404)

@auth.requires_login()
@auth.requires_membership('Student')
def report_footer():
    if request.args(0) == 'create':
        report = request.vars['report']
        content = request.vars['report-content']
        ## Get the report id
        report = db(db.report.id == report).select(
                    db.report.id,
                    db.report.assignation,
                    db.report.score_date,
                    db.report.report_restriction,
                    db.report.status
                ).first()
        valid = report is not None and content is not None

        ## Validate assignation
        if valid: valid = not cpfecys.assignation_is_locked(report.assignation)
        ## Validate that the report belongs to user
        if valid: valid = cpfecys.student_validation_report_owner(report.id)
        ## Validate that the report status is editable (it is either 'Draft' or 'Recheck')
        if valid: valid = cpfecys.student_validation_report_status(report)
        if valid:
            report.footer = content
            report.update_record()
            session.flash = T('Report updated.')
            redirect(URL('student', 'report/edit', vars=dict(report=report.id)))
        else:
            session.flash = T('Selected report can\'t be edited. Select a valid report.')
            redirect(URL('student','index'))
    elif request.args(0) == 'update':
        report = request.vars['report']
        content = request.vars['report-content']
        report = db(db.report.id == report).select(
                    db.report.id,
                    db.report.assignation,
                    db.report.score_date,
                    db.report.report_restriction,
                    db.report.status
                ).first()
        valid = report is not None and content is not None

        ## Validate assignation
        if valid: valid = not cpfecys.assignation_is_locked(report.assignation)
        ## Validate that the report belongs to user
        if valid: valid = cpfecys.student_validation_report_owner(report.id)
        ## Validate that the report status is editable (it is either 'Draft' or 'Recheck')
        if valid: valid = cpfecys.student_validation_report_status(report)
        if valid:
            report.footer = content
            report.update_record()
            session.flash = T('Report updated.')
            redirect(URL('student', 'report/edit', vars=dict(report=report.id)))
        else:
            session.flash = T('Selected report can\'t be edited. Select a valid report.')
            redirect(URL('student','index'))
    elif request.args(0) == 'delete':
        report = request.vars['report']
        report = db(db.report.id == report).select(
                    db.report.id,
                    db.report.assignation,
                    db.report.score_date,
                    db.report.report_restriction,
                    db.report.status
                ).first()
        valid = report is not None

        ## Validate assignation
        if valid: valid = not cpfecys.assignation_is_locked(report.assignation)
        ## Validate that the report belongs to user
        if valid: valid = cpfecys.student_validation_report_owner(report.id)
        ## Validate that the report status is editable (it is either 'Draft' or 'Recheck')
        if valid: valid = cpfecys.student_validation_report_status(report)
        if valid:
            report.footer = None
            report.update_record()
            session.flash = T('Report updated.')
            redirect(URL('student', 'report/edit', vars=dict(report=report.id)))
        else:
            session.flash = T('Selected report can\'t be edited. Select a valid report.')
            redirect(URL('student','index'))
    raise HTTP(404)

@auth.requires_login()
@auth.requires_membership('Student')
def log():
    if request.args(0) == 'save':
        # validate the user owns this report
        report = request.vars['report']
        report = db(db.report.id == report).select(
                    db.report.id,
                    db.report.assignation,
                    db.report.score_date,
                    db.report.report_restriction,
                    db.report.status
                ).first()
        valid_report = report is not None
        ## Validate assignation
        if valid_report: valid_report = not cpfecys.assignation_is_locked(report.assignation)
        if valid_report: valid_report = cpfecys.student_validation_report_owner(report.id)
        # validate report is 'Draft' or 'Recheck'
        if valid_report: valid_report = cpfecys.student_validation_report_status(report)
        # validate we receive log-date, log-type, log-content
        log_type = request.vars['log-type']
        log_date = request.vars['log-date']
        log_content = request.vars['log-content']
        if valid_report: valid_report = (log_type and log_date and log_content)
        if valid_report:
            db.log_entry.insert(
                log_type=log_type,
                entry_date=log_date,
                description=log_content,
                report=report.id,
                period=cpfecys.current_year_period()
            )
            session.flash = T('Log added')
            redirect(URL('student', 'report/edit', vars=dict(report=report.id)))
        else:
            session.flash = T('Operation not allowed.')
            redirect(URL('student', 'index'))
    elif request.args(0) == 'update':
        # validate the requested log
        log_id = request.vars['log']
        log = db(db.log_entry.id == log_id).select(db.log_entry.report).first()
        valid_log = log is not None

        # validate log report owner is valid
        if valid_log: valid_log = cpfecys.student_validation_report_owner(log.report)
        ## Validate assignation
        if valid_log: valid_log = not cpfecys.assignation_is_locked(log.report.assignation)
        # validate report is 'Draft' or 'Recheck'
        if valid_log: 
            report = db(db.report.id == log.report).select(
                        db.report.assignation,
                        db.report.score_date,
                        db.report.report_restriction,
                        db.report.status
                    ).first()
            valid_log = cpfecys.student_validation_report_status(report)
        # validate we receive log-date, log-type, log-content
        log_type = request.vars['log-type']
        log_date = request.vars['log-date']
        log_content = request.vars['log-content']
        if valid_log: valid_log = (log_type and log_date and log_content)
        if valid_log:
            db(db.log_entry.id == log_id).update(
                log_type=log_type,
                entry_date=log_date,
                description=log_content
            )
            session.flash = T('Log Updated')
            redirect(URL('student', 'report/edit', vars=dict(report=log.report)))
        else:
            session.flash = T('Operation not allowed.')
            redirect(URL('student', 'index'))
    elif request.args(0) == 'delete':
        # validate the requested log
        log_id = request.vars['log']
        log = db(db.log_entry.id == log_id).select(db.log_entry.report).first()
        valid_log = log is not None
        # validate log report owner is valid
        if valid_log: valid_log = cpfecys.student_validation_report_owner(log.report)
        ## Validate assignation
        if valid_log: valid_log = not cpfecys.assignation_is_locked(log.report.assignation)
        # validate report is 'Draft' or 'Recheck'
        if valid_log: 
            report = db(db.report.id == log.report).select(
                        db.report.assignation,
                        db.report.score_date,
                        db.report.report_restriction,
                        db.report.status
                    ).first()
            valid_log = cpfecys.student_validation_report_status(report)
        if valid_log:
            report_id = log.report
            db(db.log_entry.id == log_id).delete()
            session.flash = T('Log Deleted')
            redirect(URL('student', 'report/edit', vars=dict(report=report_id)))
        else:
            session.flash = T('Operation not allowed.')
            redirect(URL('student', 'index'))
    raise HTTP(404)

@auth.requires_login()
@auth.requires_membership('Student')
def desertions():
    if request.args(0) == 'save':
        # validate the user owns this report
        report = request.vars['report']
        report = db(db.report.id == report).select(
            db.report.id,
            db.report.assignation,
            db.report.score_date,
            db.report.report_restriction,
            db.report.status
        ).first()
        valid_report = report is not None
        ## Validate assignation
        if valid_report: valid_report = not cpfecys.assignation_is_locked(report.assignation)
        if valid_report: valid_report = cpfecys.student_validation_report_owner(report.id)
        # validate report is 'Draft' or 'Recheck'
        if valid_report: valid_report = cpfecys.student_validation_report_status(report)
        # validate we receive log-date, log-type, log-content
        desertion_started = request.vars['desertion-started']
        desertion_gone = request.vars['desertion-gone']
        desertion_continued = request.vars['desertion-continued']
        if valid_report: valid_report = desertion_started and desertion_gone and desertion_continued
        if valid_report:
            report.desertion_started = desertion_started
            report.desertion_gone = desertion_gone
            report.desertion_continued = desertion_continued
            report.update_record()
            session.flash = T('Desertion log added')
            redirect(URL('student', 'report/edit', vars=dict(report=report.id)))
        else:
            session.flash = T('Operation not allowed.')
            redirect(URL('student', 'index'))
    elif request.args(0) == 'update':
        # validate the user owns this report
        report = request.vars['report']
        report = db(db.report.id == report).select(
            db.report.id,
            db.report.assignation,
            db.report.score_date,
            db.report.report_restriction,
            db.report.status
        ).first()
        valid_report = report is not None
        ## Validate assignation
        if valid_report: valid_report = not cpfecys.assignation_is_locked(report.assignation)
        if valid_report: valid_report = cpfecys.student_validation_report_owner(report.id)
        # validate report is 'Draft' or 'Recheck'
        if valid_report: valid_report = cpfecys.student_validation_report_status(report)
        # validate we receive log-date, log-type, log-content
        desertion_started = request.vars['desertion-started']
        desertion_gone = request.vars['desertion-gone']
        desertion_continued = request.vars['desertion-continued']
        if valid_report: valid_report = (desertion_started and desertion_gone and desertion_continued)
        if valid_report:
            report.desertion_started = desertion_started
            report.desertion_gone = desertion_gone
            report.desertion_continued = desertion_continued
            report.update_record()
            session.flash = T('Desertion log updated')
            redirect(URL('student', 'report/edit', vars=dict(report=report.id)))
        else:
            session.flash = T('Operation not allowed.')
            redirect(URL('student', 'index'))
    elif request.args(0) == 'delete':
        # validate the user owns this report
        report = request.vars['report']
        report = db(db.report.id == report).select(
            db.report.id,
            db.report.assignation,
            db.report.score_date,
            db.report.report_restriction,
            db.report.status
        ).first()
        valid_report = report is not None
        ## Validate assignation
        if valid_report: valid_report = not cpfecys.assignation_is_locked(report.assignation)
        if valid_report: valid_report = cpfecys.student_validation_report_owner(report.id)
        # validate report is 'Draft' or 'Recheck'
        if valid_report: valid_report = cpfecys.student_validation_report_status(report)

        if valid_report:
            report.desertion_started = None
            report.desertion_gone = None
            report.desertion_continued = None
            report.update_record()
            session.flash = 'Registro de deserción removido'
            redirect(URL('student', 'report/edit', vars=dict(report=report.id)))
        else:
            session.flash = T('Operation not allowed.')
            redirect(URL('student', 'index'))
    raise HTTP(404)

@auth.requires_login()
@auth.requires_membership('Student')
def report_hours():
    if request.args(0) == 'create':
        report = request.vars['report']
        hours = request.vars['report-hours']
        ## Get the report id
        report = db(db.report.id == report).select(
            db.report.id,
            db.report.assignation,
            db.report.score_date,
            db.report.report_restriction,
            db.report.status
        ).first()
        valid = report is not None and hours is not None
        ## Validate assignation
        if valid: valid = not cpfecys.assignation_is_locked(report.assignation)
        ## Validate that the report belongs to user
        if valid: valid = cpfecys.student_validation_report_owner(report.id)
        ## Validate that the report status is editable (it is either 'Draft' or 'Recheck')
        if valid: valid = cpfecys.student_validation_report_status(report)
        if valid:
            report.hours = hours
            report.update_record()
            session.flash = T('Report updated.')
            redirect(URL('student','report/edit', vars=dict(report=report.id)))
        else:
            session.flash = T('Selected report can\'t be edited. Select a valid report.')
            redirect(URL('student','index'))
    elif request.args(0) == 'update':
        report = request.vars['report']
        hours = request.vars['report-hours']
        report = db(db.report.id == report).select(
            db.report.id,
            db.report.assignation,
            db.report.score_date,
            db.report.report_restriction,
            db.report.status
        ).first()
        valid = report is not None and hours is not None
        ## Validate assignation
        if valid: valid = not cpfecys.assignation_is_locked(report.assignation)
        ## Validate that the report belongs to user
        if valid: valid = cpfecys.student_validation_report_owner(report.id)
        ## Validate that the report status is editable (it is either 'Draft' or 'Recheck')
        if valid: valid = cpfecys.student_validation_report_status(report)
        if valid:
            report.hours = hours
            report.update_record()
            session.flash = T('Report updated.')
            redirect(URL('student','report/edit', vars=dict(report=report.id)))
        else:
            session.flash = T('Selected report can\'t be edited. Select a valid report.')
            redirect(URL('student','index'))
    elif request.args(0) == 'delete':
        report = request.vars['report']
        report = db(db.report.id == report).select(
            db.report.id,
            db.report.assignation,
            db.report.score_date,
            db.report.report_restriction,
            db.report.status
        ).first()
        valid = report is not None
        ## Validate assignation
        if valid: valid = not cpfecys.assignation_is_locked(report.assignation)
        ## Validate that the report belongs to user
        if valid: valid = cpfecys.student_validation_report_owner(report.id)
        ## Validate that the report status is editable (it is either 'Draft' or 'Recheck')
        if valid: valid = cpfecys.student_validation_report_status(report)
        if valid:
            report.hours = None
            report.update_record()
            session.flash = T('Report updated.')
            redirect(URL('student','report/edit', vars=dict(report=report.id)))
        else:
            session.flash = T('Selected report can\'t be edited. Select a valid report.')
            redirect(URL('student','index'))
    raise HTTP(404)

@auth.requires_login()
def report_month(period_number, yearp_number, report_restriction_name, is_final):
    name_report_split = report_restriction_name.upper()
    name_report_split = name_report_split.split(' ')
    if period_number == 1:
        init_semester = datetime.datetime.strptime(f'{yearp_number}-01-01', "%Y-%m-%d")
        if not is_final:
            for word in name_report_split:
                if word == 'ENERO':
                    end_semester = datetime.datetime.strptime(f'{yearp_number}-02-01', "%Y-%m-%d")
                elif word == 'FEBRERO':
                    end_semester = datetime.datetime.strptime(f'{yearp_number}-03-01', "%Y-%m-%d")
                elif word == 'MARZO':
                    end_semester = datetime.datetime.strptime(f'{yearp_number}-04-01', "%Y-%m-%d")
                elif word == 'ABRIL':
                    end_semester = datetime.datetime.strptime(f'{yearp_number}-05-01', "%Y-%m-%d")
                elif word == 'MAYO':
                    end_semester = datetime.datetime.strptime(f'{yearp_number}-06-01', "%Y-%m-%d")
        else:
            end_semester = datetime.datetime.strptime(f'{yearp_number}-06-01', "%Y-%m-%d")
    else:
        init_semester = datetime.datetime.strptime(f'{yearp_number}-06-01', "%Y-%m-%d")
        if not is_final:
            for word in name_report_split:
                if word == 'JUNIO':
                    end_semester = datetime.datetime.strptime(f'{yearp_number}-07-01', "%Y-%m-%d")
                elif word == 'JULIO':
                    end_semester = datetime.datetime.strptime(f'{yearp_number}-08-01', "%Y-%m-%d")
                elif word == 'AGOSTO':
                    end_semester = datetime.datetime.strptime(f'{yearp_number}-09-01', "%Y-%m-%d")
                elif word == 'SEPTIEMBRE':
                    end_semester = datetime.datetime.strptime(f'{yearp_number}-10-01', "%Y-%m-%d")
                elif word == 'OCTUBRE':
                    end_semester = datetime.datetime.strptime(f'{yearp_number}-11-01', "%Y-%m-%d")
                elif word == 'NOVIEMBRE':
                    end_semester = datetime.datetime.strptime(f'{yearp_number}-12-01', "%Y-%m-%d")
                elif word == 'DICIEMBRE':
                    end_semester = datetime.datetime.strptime(f'{yearp_number + 1}-01-01', "%Y-%m-%d")
        else:
            end_semester = datetime.datetime.strptime(f'{yearp_number + 1}-01-01', "%Y-%m-%d")

    return init_semester, end_semester

@auth.requires_login()
@auth.requires_membership('Student')
def final():
    if request.args(0) == 'save':
        # validate the user owns this report
        report = request.vars['report']
        report = db(db.report.id == report).select(
            db.report.id,
            db.report.assignation,
            db.report.score_date,
            db.report.report_restriction,
            db.report.status
        ).first()
        valid_report = report is not None        
        # Validate assignation
        if valid_report: valid_report = not cpfecys.assignation_is_locked(report.assignation)
        if valid_report: valid_report = cpfecys.student_validation_report_owner(report.id)
        # validate report is 'Draft' or 'Recheck'
        if valid_report: valid_report = cpfecys.student_validation_report_status(report)

        # validate we receive log-date, log-type, log-content
        aprobados_metrics = request.vars['aprobados-metrics']
        coeficiente_metrics = request.vars['coeficiente-metrics']
        curso_asignados_actas = request.vars['curso-asignados-actas']
        curso_en_final = request.vars['curso-en-final']
        curso_en_parciales = request.vars['curso-en-parciales']
        curso_en_primera_retrasada = request.vars['curso-en-primera-retrasada']
        curso_en_segunda_retrasada = request.vars['curso-en-segunda-retrasada']
        curtosis_metrics = request.vars['curtosis-metrics']
        desviacion_estandar_metrics = request.vars['desviacion-estandar-metrics']
        error_tipico_metrics = request.vars['error-tipico-metrics']
        lab_aprobados = request.vars['lab-aprobados']
        lab_media = request.vars['lab-media']
        lab_promedios = request.vars['lab-promedio']
        lab_reprobados = request.vars['lab-reprobados']
        log_date = request.vars['log-date']
        maximo_metrics = request.vars['maximo-metrics']
        media_metrics = request.vars['media-metrics']
        mediana_metrics = request.vars['mediana-metrics']
        minimo_metrics = request.vars['minimo-metrics']
        moda_metrics = request.vars['moda-metrics']
        promedio_metrics = request.vars['promedio-metrics']
        rango_metrics = request.vars['rango-metrics']
        reprobados_metrics = request.vars['reprobados-metrics']
        total_metrics = request.vars['total-metrics']
        varianza_metrics = request.vars['varianza-metrics']

        if valid_report:
            valid_report = (
                aprobados_metrics and coeficiente_metrics
                and curso_asignados_actas and curso_en_final
                and curso_en_parciales and curso_en_primera_retrasada
                and curso_en_segunda_retrasada and curtosis_metrics
                and desviacion_estandar_metrics and error_tipico_metrics
                and lab_aprobados and lab_media 
                and lab_promedios and lab_reprobados 
                and media_metrics and mediana_metrics 
                and minimo_metrics and moda_metrics 
                and promedio_metrics and rango_metrics 
                and reprobados_metrics and total_metrics 
                and varianza_metrics and log_date 
                and maximo_metrics
            )

        if valid_report:
            db.log_final.insert(
                curso_asignados_actas=curso_asignados_actas,
                curso_en_parciales=curso_en_parciales,
                curso_en_final=curso_en_final,
                curso_en_primera_restrasada=curso_en_primera_retrasada,
                curso_en_segunda_restrasada=curso_en_segunda_retrasada,
                lab_aprobados=lab_aprobados,
                lab_reprobados=lab_reprobados,
                lab_media=lab_media,
                lab_promedio=lab_promedios,
                curso_media=media_metrics,
                curso_error=error_tipico_metrics,
                curso_mediana=mediana_metrics,
                curso_moda=moda_metrics,
                curso_desviacion=desviacion_estandar_metrics,
                curso_varianza=varianza_metrics,
                curso_curtosis=curtosis_metrics,
                curso_coeficiente=coeficiente_metrics,
                curso_rango=rango_metrics,
                curso_minimo=minimo_metrics,
                curso_maximo=maximo_metrics,
                curso_total=total_metrics,
                curso_reprobados=reprobados_metrics,
                curso_aprobados=aprobados_metrics,
                curso_promedio=promedio_metrics,
                curso_created=log_date,
                report=report.id
            )
            session.flash = T('Log added')
            redirect(URL('student', 'report/edit', vars=dict(report=report.id)))
    elif request.args(0) == 'update':
        # validate the requested metric
        final = request.vars['final']
        final = db.log_final(db.log_final.id == final)
        valid_final = final is not None
        ## Validate assignation
        if valid_final: valid_final = not cpfecys.assignation_is_locked(final.report.assignation)
        # validate metric report owner is valid
        if valid_final: valid_final = cpfecys.student_validation_report_owner(final.report)
        # validate report is 'Draft' or 'Recheck'
        if valid_final: valid_final = cpfecys.student_validation_report_status (db.report(db.report.id == final.report))
        # validate we receive log-date, log-type, log-content

        aprobados_metrics = request.vars['aprobados-metrics']
        coeficiente_metrics = request.vars['coeficiente-metrics']
        curso_asignados_actas = request.vars['curso-asignados-actas']
        curso_en_final = request.vars['curso-en-final']
        curso_en_parciales = request.vars['curso-en-parciales']
        curso_en_primera_retrasada = request.vars['curso-en-primera-retrasada']
        curso_en_segunda_retrasada = request.vars['curso-en-segunda-retrasada']
        curtosis_metrics = request.vars['curtosis-metrics']
        desviacion_estandar_metrics = request.vars['desviacion-estandar-metrics']
        error_tipico_metrics = request.vars['error-tipico-metrics']
        lab_aprobados = request.vars['lab-aprobados']
        lab_media = request.vars['lab-media']
        lab_promedios = request.vars['lab-promedio']
        lab_reprobados = request.vars['lab-reprobados']
        log_date = request.vars['log-date']
        maximo_metrics = request.vars['maximo-metrics']
        media_metrics = request.vars['media-metrics']
        mediana_metrics = request.vars['mediana-metrics']
        minimo_metrics = request.vars['minimo-metrics']
        moda_metrics = request.vars['moda-metrics']
        promedio_metrics = request.vars['promedio-metrics']
        rango_metrics = request.vars['rango-metrics']
        reprobados_metrics = request.vars['reprobados-metrics']
        total_metrics = request.vars['total-metrics']
        varianza_metrics = request.vars['varianza-metrics']
        if valid_final:
            valid_final = (
                aprobados_metrics and coeficiente_metrics
                and curso_asignados_actas and curso_en_final
                and curso_en_parciales and curso_en_primera_retrasada
                and curso_en_segunda_retrasada and curtosis_metrics
                and desviacion_estandar_metrics and error_tipico_metrics 
                and lab_aprobados and lab_media 
                and lab_promedios and lab_reprobados 
                and media_metrics and mediana_metrics 
                and minimo_metrics and moda_metrics 
                and promedio_metrics and rango_metrics 
                and reprobados_metrics and total_metrics 
                and varianza_metrics and log_date 
                and maximo_metrics
            )

        if valid_final:
            final.update_record(
                curso_asignados_actas=curso_asignados_actas,
                curso_en_parciales=curso_en_parciales,
                curso_en_final=curso_en_final,
                curso_en_primera_restrasada=curso_en_primera_retrasada,
                curso_en_segunda_restrasada=curso_en_segunda_retrasada,
                lab_aprobados=lab_aprobados,
                lab_reprobados=lab_reprobados,
                lab_media=lab_media,
                lab_promedio=lab_promedios,
                curso_media=media_metrics,
                curso_error=error_tipico_metrics,
                curso_mediana=mediana_metrics,
                curso_moda=moda_metrics,
                curso_desviacion=desviacion_estandar_metrics,
                curso_varianza=varianza_metrics,
                curso_curtosis=curtosis_metrics,
                curso_coeficiente=coeficiente_metrics,
                curso_rango=rango_metrics,
                curso_minimo=minimo_metrics,
                curso_maximo=maximo_metrics,
                curso_total=total_metrics,
                curso_reprobados=reprobados_metrics,
                curso_aprobados=aprobados_metrics,
                curso_promedio=promedio_metrics,
                curso_created=log_date
            )
            
            session.flash = T('Updated')
            redirect(URL('student', 'report/edit', vars=dict(report=final.report)))
    elif request.args(0) == 'delete':
        # validate the requested log
        final = request.vars['final']
        final = db.log_final(db.log_final.id == final)
        valid_final = final is not None
        # validate log report owner is valid
        if valid_final: valid_final = cpfecys.student_validation_report_owner(final.report)
        ## Validate assignation
        if valid_final: valid_final = not cpfecys.assignation_is_locked(final.report.assignation)
        # validate report is 'Draft' or 'Recheck'
        if valid_final: valid_final = cpfecys.student_validation_report_status(db.report(db.report.id == final.report))
        
        if valid_final:
            final.delete_record()
            session.flash = T('Log Deleted')
            redirect(URL('student', 'report/edit', vars=dict(report=final.report)))
        else:
            session.flash = T('Operation not allowed.')
            redirect(URL('student', 'index'))

    return

@auth.requires_login()
@auth.requires_membership('Student')
def log_future():
    if request.args(0) == 'save':
        # validate the user owns this report
        report = request.vars['report']
        report = db.report(db.report.id == report)
        valid_report = report is not None
        ## Validate assignation
        if valid_report: valid_report = not cpfecys.assignation_is_locked(report.assignation)
        if valid_report: valid_report = cpfecys.student_validation_report_owner(report.id)
        # validate report is 'Draft' or 'Recheck'
        if valid_report: valid_report = cpfecys.student_validation_report_status(report)
        # validate we receive log-date, log-type, log-content
        log_date = request.vars['log-date']
        log_content = request.vars['log-content']
        if valid_report: valid_report = (log_date and log_content)
        if valid_report:
            db.log_future.insert(
                entry_date=log_date,
                description=log_content,
                report=report.id,
                period=cpfecys.current_year_period()
            )
            session.flash = T('Log added')
            redirect(URL('student', 'report/edit', vars=dict(report=report.id)))
        else:
            session.flash = T('Operation not allowed.')
            redirect(URL('student', 'index'))
    elif request.args(0) == 'update':
        # validate the requested log
        log = request.vars['log']
        log = db.log_future(db.log_future.id == log)
        valid_log = log is not None
        # validate log report owner is valid
        if valid_log: valid_log = cpfecys.student_validation_report_owner(log.report)
        ## Validate assignation
        if valid_log: valid_log = not cpfecys.assignation_is_locked(log.report.assignation)
        # validate report is 'Draft' or 'Recheck'
        if valid_log: valid_log = cpfecys.student_validation_report_status(db.report(db.report.id == log.report))
        # validate we receive log-date, log-type, log-content
        log_date = request.vars['log-date']
        log_content = request.vars['log-content']
        if valid_log: valid_log = (log_date and log_content)
        if valid_log:
            log.update_record(entry_date=log_date, description=log_content)
            session.flash = T('Log Updated')
            redirect(URL('student', 'report/edit', vars=dict(report=log.report)))
        else:
            session.flash = T('Operation not allowed.')
            redirect(URL('student', 'index'))
    elif (request.args(0) == 'delete'):
        # validate the requested log
        log = request.vars['log']
        log = db.log_future(db.log_future.id == log)
        valid_log = log is not None
        # validate log report owner is valid
        if valid_log: valid_log = cpfecys.student_validation_report_owner(log.report)
        ## Validate assignation
        if valid_log: valid_log = not cpfecys.assignation_is_locked(log.report.assignation)
        # validate report is 'Draft' or 'Recheck'
        if valid_log: valid_log = cpfecys.student_validation_report_status(db.report(db.report.id == log.report))
        if valid_log:
            log.delete_record()
            session.flash = T('Log Deleted')
            redirect(URL('student', 'report/edit', vars=dict(report=log.report)))
        else:
            session.flash = T('Operation not allowed.')
            redirect(URL('student', 'index'))
    raise HTTP(404)

@auth.requires_login()
@auth.requires_membership('Student')
def conferencias():
    hola = "hola desde conferencias"
    return dict(message = hola)

@auth.requires_login()
@auth.requires_membership('Student')
def foros():
    hola = auth.user.id
    rows = db(db.foro.id_estudiante == auth.user.id).select()

    #cascarus
    periodo = cpfecys.current_year_period()
    if request.vars['period']:
        periodo_parametro = request.vars['period']
        periodo = db(db.period_year.id == periodo_parametro).select().first()

    periods_temp = db.executesql("""
        SELECT py.id, py.yearp, p.name
        FROM period_year py
        INNER JOIN user_project uspj ON uspj.period = py.id
        INNER JOIN period p on p.id = py.period
        WHERE uspj.ASSIGNED_USER = {0};
    """.format(auth.user.id))

    periods = [];
    
    for p in periods_temp:
        period_temp = {
            'id': p[0],
            'yearp': p[1],
            'name': p[2]
        }
        objeto = type('Objeto', (object,), period_temp)()
        periods.append(objeto)

    return dict(
        message = hola,
        rows = rows,
        periodo = periodo,
        periods=periods,
    )

@auth.requires_login()
@auth.requires_membership('Student')
def metrics():
    cdate = datetime.datetime.now()
    if (request.args(0) == 'save'):
        # validate the user owns this report
        report = request.vars['report']
        report = db.report(db.report.id == report)
        valid_report = report is not None
        ## Validate assignation
        if valid_report: valid_report = not cpfecys.assignation_is_locked(report.assignation)
        if valid_report: valid_report = cpfecys.student_validation_report_owner(report.id)
        # validate report is 'Draft' or 'Recheck'
        if valid_report: valid_report = cpfecys.student_validation_report_status(report)
        # validate we receive log-date, log-type, log-content
        description = request.vars['description']
        media = request.vars['media-metrics']
        error_tipico = request.vars['error-tipico-metrics']
        mediana = request.vars['mediana-metrics']
        moda = request.vars['moda-metrics']
        desviacion_estandar = request.vars['desviacion-estandar-metrics']
        varianza = request.vars['varianza-metrics']
        curtosis = request.vars['curtosis-metrics']
        coeficiente = request.vars['coeficiente-metrics']
        rango = request.vars['rango-metrics']
        minimo = request.vars['minimo-metrics']
        maximo = request.vars['maximo-metrics']
        total = request.vars['total-metrics']
        reprobados = request.vars['reprobados-metrics']
        aprobados = request.vars['aprobados-metrics']
        metric_type = request.vars['metric-type']
        log_date = request.vars['log-date']

        if valid_report: 
            valid_report = (
                media and error_tipico 
                and mediana and moda 
                and desviacion_estandar and varianza 
                and curtosis and coeficiente 
                and rango and minimo 
                and maximo and total
                and reprobados and aprobados
                and metric_type and log_date
                and description
            )

        if valid_report:
            db.log_metrics.insert(
                report=report.id,
                description=description,
                media=media,
                error=error_tipico,
                mediana=mediana,
                moda=moda,
                desviacion=desviacion_estandar,
                varianza=varianza,
                curtosis=curtosis,
                coeficiente=coeficiente,
                rango=rango,
                minimo=minimo,
                maximo=maximo,
                total=total,
                reprobados=reprobados,
                aprobados=aprobados,
                created=log_date,
                metrics_type=metric_type
            )
            session.flash = T('Log added')
            redirect(URL('student', 'report/edit', vars=dict(report=report.id)))
        else:
            session.flash = T('Operation not allowed.')
            redirect(URL('student', 'index'))
    elif request.args(0) == 'update':
        # validate the requested metric
        metric = request.vars['metric']
        metric = db.log_metrics(db.log_metrics.id == metric)
        valid_metric = metric is not None
        ## Validate assignation
        if valid_metric: valid_metric = not cpfecys.assignation_is_locked(metric.report.assignation)
        # validate metric report owner is valid
        if valid_metric: valid_metric = cpfecys.student_validation_report_owner(metric.report)
        # validate report is 'Draft' or 'Recheck'
        if valid_metric: valid_metric = cpfecys.student_validation_report_status(db.report(db.report.id == metric.report))
        # validate we receive log-date, log-type, log-content
        description = request.vars['description']
        media = request.vars['media-metrics']
        error_tipico = request.vars['error-tipico-metrics']
        mediana = request.vars['mediana-metrics']
        moda = request.vars['moda-metrics']
        desviacion_estandar = request.vars['desviacion-estandar-metrics']
        varianza = request.vars['varianza-metrics']
        curtosis = request.vars['curtosis-metrics']
        coeficiente = request.vars['coeficiente-metrics']
        rango = request.vars['rango-metrics']
        minimo = request.vars['minimo-metrics']
        maximo = request.vars['maximo-metrics']
        total = request.vars['total-metrics']
        reprobados = request.vars['reprobados-metrics']
        aprobados = request.vars['aprobados-metrics']
        metric_type = request.vars['metric-type']
        log_date = request.vars['log-date']
        if valid_metric: 
            valid_metric = (
                media and error_tipico 
                and mediana and moda 
                and desviacion_estandar and varianza
                and curtosis and coeficiente 
                and rango and minimo 
                and maximo and total
                and reprobados and aprobados
                and metric_type and log_date
                and description
            )
        if valid_metric:
            metric.update_record(
                report=metric.report.id,
                description=description,
                media=media,
                error=error_tipico,
                mediana=mediana,
                moda=moda,
                desviacion=desviacion_estandar,
                varianza=varianza,
                curtosis=curtosis,
                coeficiente=coeficiente,
                rango=rango,
                minimo=minimo,
                maximo=maximo,
                total=total,
                reprobados=reprobados,
                aprobados=aprobados,
                created=log_date,
                metrics_type=metric_type
            )
            session.flash = T('Metric Updated')
            redirect(URL('student', 'report/edit', vars=dict(report=metric.report)))
        else:
            session.flash = T('Operation not allowed.')
            redirect(URL('student', 'index'))
    elif request.args(0) == 'delete':
        # validate the requested metric
        metric = request.vars['metric']
        metric = db.log_metrics(db.log_metrics.id == metric)
        valid_metric = metric is not None
        ## Validate assignation
        if valid_metric: valid_metric = not cpfecys.assignation_is_locked(metric.report.assignation)
        # validate metric report owner is valid
        if valid_metric: valid_metric = cpfecys.student_validation_report_owner(metric.report)
        # validate report is 'Draft' or 'Recheck'
        if valid_metric: valid_metric = cpfecys.student_validation_report_status(db.report(db.report.id == metric.report))
        if valid_metric:
            metric.delete_record()
            session.flash = T('Log Deleted')
            redirect(URL('student', 'report/edit', vars=dict(report=metric.report)))
        else:
            session.flash = T('Operation not allowed.')
            redirect(URL('student', 'index'))

    raise HTTP(404)

    if request.args(0) == 'save':
        # validate the user owns this report
        report = request.vars['report']
        report = db.report(db.report.id == report)
        valid_report = report is not None
        ## Validate assignation
        if valid_report: valid_report = not cpfecys.assignation_is_locked(report.assignation)
        if valid_report: valid_report = cpfecys.student_validation_report_owner(report.id)
        # validate report is 'Draft' or 'Recheck'
        if valid_report: valid_report = cpfecys.student_validation_report_status(report)
        # validate we receive log-date, log-type, log-content
        desertion_started = request.vars['desertion-started']
        desertion_gone = request.vars['desertion-gone']
        desertion_continued = request.vars['desertion-continued']
        if valid_report: valid_report = (desertion_started and desertion_gone and desertion_continued)
        if valid_report:
            report.desertion_started = desertion_started
            report.desertion_gone = desertion_gone
            report.desertion_continued = desertion_continued
            report.update_record()
            session.flash = T('Desertion log added')
            redirect(URL('student', 'report/edit', vars=dict(report=report.id)))
        else:
            session.flash = T('Operation not allowed.')
            redirect(URL('student', 'index'))
    elif request.args(0) == 'update':
        # validate the user owns this report
        report = request.vars['report']
        report = db.report(db.report.id == report)
        valid_report = report is not None
        ## Validate assignation
        if valid_report: valid_report = not cpfecys.assignation_is_locked(report.assignation)
        if valid_report: valid_report = cpfecys.student_validation_report_owner(report.id)
        # validate report is 'Draft' or 'Recheck'
        if valid_report: valid_report = cpfecys.student_validation_report_status(report)
        # validate we receive log-date, log-type, log-content
        desertion_started = request.vars['desertion-started']
        desertion_gone = request.vars['desertion-gone']
        desertion_continued = request.vars['desertion-continued']
        if valid_report: valid_report = (desertion_started and desertion_gone and desertion_continued)
        if valid_report:
            report.desertion_started = desertion_started
            report.desertion_gone = desertion_gone
            report.desertion_continued = desertion_continued
            report.update_record()
            session.flash = T('Desertion log updated')
            redirect(URL('student', 'report/edit', vars=dict(report=report.id)))
        else:
            session.flash = T('Operation not allowed.')
            redirect(URL('student', 'index'))
    elif request.args(0) == 'delete':
        # validate the user owns this report
        report = request.vars['report']
        report = db.report(db.report.id == report)
        valid_report = report is not None
        ## Validate assignation
        if valid_report: valid_report = not cpfecys.assignation_is_locked(report.assignation)
        if valid_report: valid_report = cpfecys.student_validation_report_owner(report.id)
        # validate report is 'Draft' or 'Recheck'
        if valid_report: valid_report = cpfecys.student_validation_report_status(report)
        # validate we receive log-date, log-type, log-content
        desertion_started = request.vars['desertion-started']
        desertion_gone = request.vars['desertion-gone']
        desertion_continued = request.vars['desertion-continued']
        if valid_report: valid_report = (desertion_started and desertion_gone and desertion_continued)
        if valid_report:
            report.desertion_started = None
            report.desertion_gone = None
            report.desertion_continued = None
            report.update_record()
            session.flash = T('Desertion log removed')
            redirect(URL('student', 'report/edit', vars=dict(report=report.id)))
        else:
            session.flash = T('Operation not allowed.')
            redirect(URL('student', 'index'))

    raise HTTP(404)