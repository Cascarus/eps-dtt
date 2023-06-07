from gluon.scheduler import Scheduler

import cpfecys
import config
import datetime

def auto_daily():
    ## Get current year period
    currentyear_period = cpfecys.current_year_period()

    ## Get all report_restriction of this period_year that end_date is beyond today
    current_date = datetime.datetime.now()
    if currentyear_period.period == cpfecys.first_period.id:
        date_min = datetime.datetime(currentyear_period.yearp, 1, 1)
        date_max = datetime.datetime(currentyear_period.yearp, 7, 1)
    else:
        date_min = datetime.datetime(currentyear_period.yearp, 7, 1)
        date_max = datetime.datetime(currentyear_period.yearp, 1, 1)

    expired_restrictions = db((db.report_restriction.end_date < current_date)&
                              (db.report_restriction.start_date >= date_min)&
                              (db.report_restriction.end_date >= date_min)&
                              (db.report_restriction.start_date < date_max)&
                              (db.report_restriction.end_date < date_max)&
                              (db.report_restriction.is_enabled == True))\
                              .select()
    ## Get all assignations for this period_year
    semester_assignations = db((db.user_project.period <= \
                                currentyear_period.id) & \
                               ((db.user_project.period + \
                                 db.user_project.periods) > \
                                currentyear_period.id)).select()
    # For every assignation and restriction
    ## This makes all missed assignations automatically not sent and set
    # to failed reports :(
    missed_reports = 0
    status_acceptance = db.report_status(db.report_status.name=='Acceptance')

    for assignation in semester_assignations:
        for restriction in expired_restrictions:
            reports = db((db.report.assignation == assignation.id)&
                         (db.report.report_restriction == restriction.id)).count()
            if not(reports > 0):
                missed_reports += 1
                db.report.insert(assignation=assignation.id,
                                 min_score=cpfecys.get_custom_parameters()\
                                             .min_score,
                                 report_restriction=restriction.id,
                                 created=current_date,
                                 score=0,
                                 status=status_acceptance,
                                 never_delivered=True,
                                 teacher_comment=T('The period of time to create the report finished and it was never completed; so automatically it is considered as failed.'))

    if currentyear_period.period == cpfecys.first_period.id:
        date_min = datetime.datetime(currentyear_period.yearp-1, 7, 1)
        date_max = datetime.datetime(currentyear_period.yearp, 1, 1)
    else:
        date_min = datetime.datetime(currentyear_period.yearp, 1, 1)
        date_max = datetime.datetime(currentyear_period.yearp, 7, 1)

    expired_restrictions = db((db.report_restriction.end_date < current_date)&
                              (db.report_restriction.start_date >= date_min)&
                              (db.report_restriction.end_date >= date_min)&
                              (db.report_restriction.start_date < date_max)&
                              (db.report_restriction.end_date < date_max)&
                              (db.report_restriction.is_enabled == True)).select()
    ## Get all assignations for this period_year
    semester_assignations = db((db.user_project.period <= currentyear_period.id-1)&
                     ((db.user_project.period + db.user_project.periods) > currentyear_period.id-1)).select()
    # For every assignation and restriction
    ## This makes all missed assignations automatically not sent and set to failed reports :(
    missed_reports = 0
    status_acceptance = db.report_status(db.report_status.name=='Acceptance')
    for assignation in semester_assignations:
        for restriction in expired_restrictions:
            reports = db((db.report.assignation == assignation.id)&
                         (db.report.report_restriction == restriction.id)).count()
            if not(reports > 0):
                missed_reports += 1
                db.report.insert(assignation=assignation.id,
                                 min_score=cpfecys.get_custom_parameters().min_score,
                                 report_restriction=restriction.id,
                                 created=current_date,
                                 score=0,
                                 status=status_acceptance,
                                 never_delivered=True,
                                 teacher_comment=T('The period of time to create the report finished and it was never completed; so automatically it is considered as failed.'))

    # *************************************************************************
    # ****************************PHASE 2 DTT**********************************
    # ALL DRAFTS FILL IF THEY HAVE ACADEMIC TUTORS AND ACTIVITIES
    drafties = db((db.report.status == db.report_status(name = 'Draft'))&
               (db.report_restriction.end_date < current_date)&
               (db.report.report_restriction == db.report_restriction.id))\
               .select()

    for d in drafties:
        if d.report.assignation.project.area_level.name == \
           'DTT Tutor Académico' and (d.report.dtt_approval is None or
                                       d.report.dtt_approval == True):
            activitiesTutor = activities_report_tutor(d.report)
            cperiod = obtainPeriodReport(d.report)
            temp_logType = db(db.log_type.name=='Activity').select().first()
            for awm in activitiesTutor['activities_WM']:
                db.log_entry.insert(log_type=temp_logType.id,
                                    entry_date=current_date,
                                    description='Nombre: "'+awm.name+'"      Descripción: "'+awm.description+'"',
                                    report=d.report.id,
                                    period=cperiod.id,
                                    tActivity='F',
                                    idActivity=awm.id
                                    )
            for awm in activitiesTutor['activities_M']:
                db.log_entry.insert(log_type=temp_logType.id,
                                    entry_date=current_date,
                                    description=awm[1],
                                    report=d.report.id,
                                    period=cperiod.id,
                                    tActivity='T',
                                    idActivity=awm[17]
                                    )
                db.log_metrics.insert(description=awm[1],
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
                                        report=d.report.id,
                                        metrics_type=awm[16]
                                    )
            for awm in activitiesTutor['activities_F']:
                db.log_future.insert(entry_date=current_date,
                                    description='Nombre: "'+awm.name+'"      Descripción: "'+awm.description+'"',
                                    report=d.report.id,
                                    period=cperiod.id
                                    )

    # ALL BETTER IF YOU HAVE COMPLETED ACADEMIC TUTORS AND HAVE ACTIVITIES
    recheckies = db((db.report_restriction.id == db.report.report_restriction)&
                    (db.report.status == db.report_status(name='Recheck'))&
                    (db.report.score_date <= (current_date - datetime.timedelta(days = cpfecys.get_custom_parameters().rescore_max_days)))).select()

    for rech in recheckies:
        if rech.report.assignation.project.area_level.name=='DTT Tutor Académico' and (rech.report.dtt_approval is None or rech.report.dtt_approval==True):
            activitiesTutor = activities_report_tutor(rech.report)
            cperiod = obtainPeriodReport(rech.report)
            temp_logType = db(db.log_type.name=='Activity').select().first()
            for awm in activitiesTutor['activities_WM']:
                db.log_entry.insert(log_type=temp_logType.id,
                                    entry_date=current_date,
                                    description='Nombre: "'+awm.name+'"      Descripción: "'+awm.description+'"',
                                    report=rech.report.id,
                                    period=cperiod.id,
                                    tActivity='F',
                                    idActivity=awm.id
                                    )
            for awm in activitiesTutor['activities_M']:
                db.log_entry.insert(log_type=temp_logType.id,
                                    entry_date=current_date,
                                    description=awm[1],
                                    report=rech.report.id,
                                    period=cperiod.id,
                                    tActivity='T',
                                    idActivity=awm[17]
                                    )
                db.log_metrics.insert(description=awm[1],
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
                                        report=rech.report.id,
                                        metrics_type=awm[16]
                                    )
            for awm in activitiesTutor['activities_F']:
                db.log_future.insert(entry_date=current_date,
                                    description='Nombre: "'+awm.name+'"      Descripción: "'+awm.description+'"',
                                    report=rech.report.id,
                                    period=cperiod.id
                                    )

    # ALL DRAFTS FILL IF THEY HAVE ACADEMIC TUTORS AND ACTIVITIES
    drafties = db((db.report.status == db.report_status(name='Draft'))&
               (db.report_restriction.end_date < current_date)&
               (db.report.report_restriction == db.report_restriction.id)).select(db.report.ALL)

    for report in drafties:
        reqs = db(db.area_report_requirement.area_level==report.assignation.project.area_level).select()
        minimal_requirements = True
        activities_count = db(db.log_entry.report==report.id).count()
        metrics_count = db(db.log_metrics.report==report.id).count()

        if report.assignation.project.area_level.name != 'DTT Tutor Académico':
            for req in reqs:
                if (req.report_requirement.name == 'Registrar Estadisticas Finales de Curso') \
                and (report.report_restriction.is_final) \
                and (final_stats == 0):
                    minimal_requirements = False
                    break
                if (req.report_requirement.name == 'Encabezado') and \
                            (report.heading is None):
                    minimal_requirements = False
                    break
                if (req.report_requirement.name == 'Pie de Reporte') and \
                            (report.footer is None):
                    minimal_requirements = False
                    break
                if (req.report_requirement.name == 'Registrar Actividad') and \
                            (activities_count == 0):
                    minimal_requirements = False
                    break
                if (req.report_requirement.name == 'Registrar Actividad con Metricas') and \
                            (metrics_count == 0):
                    minimal_requirements = False
                    break
                if (req.report_requirement.name == 'Registrar Deserciones') and \
                            (report.desertion_started is None):
                    minimal_requirements = False
                    break
                if (req.report_requirement.name == 'Registrar Horas Completadas') and \
                            (report.hours is None):
                    minimal_requirements = False
                    break
            if not minimal_requirements:
                report.score = 0
                report.status = db.report_status(name = 'Acceptance')
                report.teacher_comment =  T('The period of time to create the report finished and it was never completed; so automatically it is considered as failed.')
                report.never_delivered = True
                report.min_score = cpfecys.get_custom_parameters().min_score
                report.update_record()
    # *************************************************************************
    # ****************************PHASE 2 DTT**********************************

    ## This makes all 'Draft' reports that have no delivered anything to be set to failed!
    drafties = db((db.report.status == db.report_status(name = 'Draft'))&
               (db.report_restriction.end_date < current_date)&
               (db.report.report_restriction == db.report_restriction.id)&
               (db.report.heading == None)&
               (db.report.footer == None)&
               (db.report.desertion_started == None)&
               (db.report.desertion_gone == None)&
               (db.report.desertion_continued == None)&
               (db.report.hours == None)).select()
    total_drafties_empty = len(drafties)
    for d in drafties:
        d.report.score = 0
        d.report.status = db.report_status(name = 'Acceptance')
        d.report.teacher_comment =  T('The period of time to create the report finished and it was never completed; so automatically it is considered as failed.')
        d.report.never_delivered = True
        d.report.min_score = cpfecys.get_custom_parameters().min_score
        d.report.update_record()

    ## This makes all 'Draft' reports that expired get to 'Grading'
    drafties = db((db.report.status == db.report_status(name = 'Draft'))&
               (db.report_restriction.end_date < current_date)&
               (db.report.report_restriction == db.report_restriction.id)).select()
    total_drafties = len(drafties)

    signature = (cpfecys.get_custom_parameters().email_signature or '')
    for d in drafties:
        d.report.status = db.report_status(name = 'Grading')
        d.report.min_score = cpfecys.get_custom_parameters().min_score
        d.report.update_record()
        ## TODO: Send Email according to assignation
        # Notification Message
        me_the_user = d.report.assignation.assigned_user
        message = '<html>' + T('The report') + ' ' \
        + '<b>' + XML(d.report_restriction['name']) + '</b><br/>' \
        + T('sent by student: ') + XML(me_the_user.username) + ' ' \
        + XML(me_the_user.first_name) + ' ' + XML(me_the_user.last_name) \
        + '<br/>' \
        + T('was sent to be checked.') + '<br/>' + T('Checking can be done in:') \
        + ' ' + cpfecys.get_domain() + '<br />' + signature + '</html>'
        # send mail to teacher and student notifying change.
        mails = []
        # retrieve teacher's email
        teachers = db((db.project.id == d.report.assignation.project)&
                      (db.user_project.project == db.project.id)&
                      (db.user_project.assigned_user == db.auth_user.id)&
                      (db.auth_membership.user_id == db.auth_user.id)&
                      (db.auth_membership.group_id == db.auth_group.id)&
                      (db.auth_group.role == 'Teacher')).select()
        for teacher in teachers:
            mails.append(teacher.auth_user.email)
        # retrieve student's email
        student_mail = me_the_user.email
        mails.append(student_mail)
        was_sent = mail.send(to=mails,
                  subject=T('[DTT]Automatic Notification - Report ready to be checked.'),
                  # If reply_to is omitted, then mail.settings.sender is used
                  reply_to = student_mail,
                  message=message)
        #MAILER LOG
        db.mailer_log.insert(sent_message = message,
                             destination = ','.join(mails),
                             result_log = str(mail.error or '') + ':' + str(mail.result),
                             success = was_sent)
    ## This makes all 'Recheck' reports that expired to 'Grading'
    import datetime
    recheckies = db((db.report_restriction.id == db.report.report_restriction)&
                    (db.report.status == db.report_status(name='Recheck'))&
                    (db.report.score_date <= (current_date - datetime.timedelta(days = cpfecys.get_custom_parameters().rescore_max_days)))).select()
    total_recheckies = len(recheckies)
    import cpfecys
    signature = cpfecys.get_custom_parameters().email_signature
    for rech in recheckies:
        rech.report.status = db.report_status(name = 'Grading')
        rech.report.update_record()
        ## TODO: Send Email according to assignation
        me_the_user = rech.report.assignation.assigned_user
        message = '<html>' + T('The report') + ' ' \
        + '<b>' + XML(rech.report_restriction['name']) + '</b><br/>' \
        + T('sent by student: ') + XML(me_the_user.username) + ' ' \
        + XML(me_the_user.first_name) + ' ' + XML(me_the_user.last_name) \
        + '<br/>' \
        + T('was sent to be checked.') + '<br/>' + T('Checking can be done in:') \
        + ' ' + cpfecys.get_domain() + '<br />' + signature + '</html>'
        # send mail to teacher and student notifying change.
        mails = []
        # retrieve teacher's email
        teachers = db((db.project.id == rech.report.assignation.project)&
                      (db.user_project.project == db.project.id)&
                      (db.user_project.assigned_user == db.auth_user.id)&
                      (db.auth_membership.user_id == db.auth_user.id)&
                      (db.auth_membership.group_id == db.auth_group.id)&
                      (db.auth_group.role == 'Teacher')).select()
        for teacher in teachers:
            mails.append(teacher.auth_user.email)
        # retrieve student's email
        student_mail = me_the_user.email
        mails.append(student_mail)
        was_sent = mail.send(to=mails,
                  subject=T('[DTT]Automatic Notification - Report ready to be checked.'),
                  # If reply_to is omitted, then mail.settings.sender is used
                  reply_to = student_mail,
                  message = message)
        #MAILER LOG
        db.mailer_log.insert(sent_message = message,
                             destination = ','.join(mails),
                             result_log = str(mail.error or '') + ':' + str(mail.result),
                             success = was_sent)
    db.commit()
    #modificado para aceptar periods variables
    auto_freeze()

    # comentar el estado de los practicantes "antes de tiempo"
    validar_practicantes_finales()

    #no tiene incidencia en periodos variables
    check_exception_semester_repeat()

    #actividades de catedratico a ejecutarse un dia despues o que ya se ejecutaron para cambiar los estados
    #no tiene incidencias en periodos variables
    automation_activities_assigned()
    #emarquez: modificado una pequeña seccion para excluir periodos variables
    automation_evaluations()
    #emarquez: modificado adaptacion periodos variables
    send_evaluation_notifications()
    #envia notificaciones al administrador, acerca de las evaluaciones que inician
    send_notification_for_starting_evaluations()
    return T('Total Updated Reports: ') + str(total_recheckies + total_drafties + missed_reports) + ' ' + \
            T('Automatically Updated Draft Reports: ') + str(total_drafties) + ' ' + \
            T('Automatically Updated Recheck Reports: ') + str(total_recheckies) + ' ' + \
            T('Reports Never Delivered: ') + str(missed_reports + total_drafties_empty)

def activities_report_tutor(report):
    activities_WM=None
    activities_M=None
    activities_F=None
    if report.assignation.project.area_level.name=='DTT Tutor Académico' and (report.status.name=='Draft' or report.status.name=='Recheck'):
        #Get the minimum and maximum date of the report
        cperiod = obtainPeriodReport(report)
        parameters_period = db(db.student_control_period.period_name==(T(cperiod.period.name)+' '+str(cperiod.yearp))).select().first()
        endDateActivity=None
        initSemester=None
        if cperiod.period == 1:
            initSemester = datetime.datetime.strptime(str(cperiod.yearp) + '-' + '01-01', "%Y-%m-%d")
            if report.report_restriction.is_final==False:
                activities_F=[]
                nameReportSplit = report.report_restriction.name.upper()
                nameReportSplit = nameReportSplit.split(' ')
                for word in nameReportSplit:
                    if word=='ENERO':
                        endDateActivity = datetime.datetime.strptime(str(cperiod.yearp) + '-' + '02-01', "%Y-%m-%d")
                    elif word=='FEBRERO':
                        endDateActivity = datetime.datetime.strptime(str(cperiod.yearp) + '-' + '03-01', "%Y-%m-%d")
                    elif word=='MARZO':
                        endDateActivity = datetime.datetime.strptime(str(cperiod.yearp) + '-' + '04-01', "%Y-%m-%d")
                    elif word=='ABRIL':
                        endDateActivity = datetime.datetime.strptime(str(cperiod.yearp) + '-' + '05-01', "%Y-%m-%d")
                    elif word=='MAYO':
                        endDateActivity = datetime.datetime.strptime(str(cperiod.yearp) + '-' + '06-01', "%Y-%m-%d")
            else:
                endDateActivity = datetime.datetime.strptime(str(cperiod.yearp) + '-' + '06-01', "%Y-%m-%d")
        else:
            initSemester = datetime.datetime.strptime(str(cperiod.yearp) + '-' + '06-01', "%Y-%m-%d")
            if report.report_restriction.is_final==False:
                activities_F=[]
                nameReportSplit = report.report_restriction.name.upper()
                nameReportSplit = nameReportSplit.split(' ')
                for word in nameReportSplit:
                    if word=='JUNIO':
                        endDateActivity = datetime.datetime.strptime(str(cperiod.yearp) + '-' + '07-01', "%Y-%m-%d")
                    elif word=='JULIO':
                        endDateActivity = datetime.datetime.strptime(str(cperiod.yearp) + '-' + '08-01', "%Y-%m-%d")
                    elif word=='AGOSTO':
                        endDateActivity = datetime.datetime.strptime(str(cperiod.yearp) + '-' + '09-01', "%Y-%m-%d")
                    elif word=='SEPTIEMBRE':
                        endDateActivity = datetime.datetime.strptime(str(cperiod.yearp) + '-' + '10-01', "%Y-%m-%d")
                    elif word=='OCTUBRE':
                        endDateActivity = datetime.datetime.strptime(str(cperiod.yearp) + '-' + '11-01', "%Y-%m-%d")
                    elif word=='NOVIEMBRE':
                        endDateActivity = datetime.datetime.strptime(str(cperiod.yearp) + '-' + '12-01', "%Y-%m-%d")
                    elif word=='DICIEMBRE':
                        endDateActivity = datetime.datetime.strptime(str(cperiod.yearp+1) + '-' + '01-01', "%Y-%m-%d")
            else:
                endDateActivity = datetime.datetime.strptime(str(cperiod.yearp+1) + '-' + '01-01', "%Y-%m-%d")

        #Get the latest reports and are of this semester
        beforeReportsRestriction = db((db.report_restriction.id<report.report_restriction)&(db.report_restriction.start_date>=initSemester)).select(db.report_restriction.id)
        if beforeReportsRestriction.first() is None:
            beforeReports=[]
            beforeReports.append(-1)
        else:
            beforeReports = db((db.report.assignation==report.assignation)&(db.report.report_restriction.belongs(beforeReportsRestriction))).select(db.report.id)
            if beforeReports.first() is None:
                beforeReports=[]
                beforeReports.append(-1)

        #Check the id of the log type thtat is activity
        temp_logType = db(db.log_type.name=='Activity').select().first()

        #*******************Activities to record activities unless already recorded in previous reports
        #Activities without metric
        activitiesWMBefore = db((db.log_entry.log_type==temp_logType)&(db.log_entry.period==cperiod.id)&(db.log_entry.tActivity==False)&(db.log_entry.report.belongs(beforeReports))).select(db.log_entry.idActivity.with_alias('id'))
        if activitiesWMBefore.first() is None:
            activities_WM = db((db.course_activity_without_metric.semester == cperiod.id)&(db.course_activity_without_metric.assignation == report.assignation.project)&(db.course_activity_without_metric.date_start < endDateActivity)).select()
            #Future activities without metric
            if report.report_restriction.is_final==False:
                activities_F_temp = db((db.course_activity_without_metric.semester == cperiod.id)&(db.course_activity_without_metric.assignation == report.assignation.project)&(db.course_activity_without_metric.date_start >= endDateActivity)).select()
                for awmt in activities_F_temp:
                    activities_F.append(awmt)
        else:
            activities_WM = db((db.course_activity_without_metric.semester == cperiod.id)&(db.course_activity_without_metric.assignation == report.assignation.project)&(~db.course_activity_without_metric.id.belongs(activitiesWMBefore))&(db.course_activity_without_metric.date_start < endDateActivity)).select()
            #Future activities without metric
            if report.report_restriction.is_final==False:
                activities_F_temp = db((db.course_activity_without_metric.semester == cperiod.id)&(db.course_activity_without_metric.assignation == report.assignation.project)&(~db.course_activity_without_metric.id.belongs(activitiesWMBefore))&(db.course_activity_without_metric.date_start >= endDateActivity)).select()
                for awmt in activities_F_temp:
                    activities_F.append(awmt)

        #Activities with metric
        activitiesMBefore = db((db.log_entry.log_type==temp_logType)&(db.log_entry.period==cperiod.id)&(db.log_entry.tActivity==True)&(db.log_entry.report.belongs(beforeReports))).select(db.log_entry.idActivity.with_alias('id'))
        activitiesGrades = db((db.grades.academic_assignation==db.academic_course_assignation.id)&(db.academic_course_assignation.semester==cperiod.id)&(db.academic_course_assignation.assignation==report.assignation.project)).select(db.grades.activity.with_alias('id'), distinct=True)
        if activitiesGrades.first() is not None:
            activities_M_Real=[]
            if activitiesMBefore.first() is None:
                #Complete with measuring activities
                activities_M = db((db.course_activity.semester == cperiod.id)&(db.course_activity.assignation == report.assignation.project)&(db.course_activity.date_start < endDateActivity)&(db.course_activity.id.belongs(activitiesGrades))).select()
                for actTempo in activities_M:
                    if report.report_restriction.is_final==False:
                        #tempEndAct = actTempo.date_finish + datetime.timedelta(days=parameters_period.timeout_income_notes)
                        tempEndAct = actTempo.date_finish
                        tempEndAct = datetime.datetime(tempEndAct.year, tempEndAct.month, tempEndAct.day)
                        endDateActivityt1 = datetime.datetime(endDateActivity.year, endDateActivity.month, endDateActivity.day)
                        if tempEndAct<endDateActivityt1:
                            #Check if you have the minimum of notes recorded in the activity amount that you are worth in the report
                            if (((int(db((db.grades_log.activity_id == actTempo.id)&(db.grades_log.operation_log=='insert')&(db.grades_log.user_name==report.assignation.assigned_user.username)).count())*100)/int(db(db.grades.activity == actTempo.id).count()))>=int(parameters_period.percentage_income_activity)):
                                activities_M_Real.append(metric_statistics(actTempo,0,None))
                        else:
                            #Future activities with metric
                            activities_F.append(actTempo)
                    else:
                        #Check if you have the minimum of notes recorded in the activity amount that you are worth in the report
                        if (((int(db((db.grades_log.activity_id == actTempo.id)&(db.grades_log.operation_log=='insert')&(db.grades_log.user_name==report.assignation.assigned_user.username)).count())*100)/int(db(db.grades.activity == actTempo.id).count()))>=int(parameters_period.percentage_income_activity)):
                            activities_M_Real.append(metric_statistics(actTempo,0,None))
                activities_M = activities_M_Real
                #Complete with measuring future activities
                if report.report_restriction.is_final==False:
                    activities_F_temp = db((db.course_activity.semester == cperiod.id)&(db.course_activity.assignation == report.assignation.project)&(db.course_activity.date_start >= endDateActivity)).select()
                    for awmt in activities_F_temp:
                        activities_F.append(awmt)
            else:
                #Complete with measuring activities
                activities_M = db((db.course_activity.semester == cperiod.id)&(db.course_activity.assignation == report.assignation.project)&(db.course_activity.date_start < endDateActivity)&(~db.course_activity.id.belongs(activitiesMBefore))&(db.course_activity.id.belongs(activitiesGrades))).select()
                for actTempo in activities_M:
                    if report.report_restriction.is_final==False:
                        #tempEndAct = actTempo.date_finish + datetime.timedelta(days=parameters_period.timeout_income_notes)
                        tempEndAct = actTempo.date_finish
                        tempEndAct = datetime.datetime(tempEndAct.year, tempEndAct.month, tempEndAct.day)
                        endDateActivityt1 = datetime.datetime(endDateActivity.year, endDateActivity.month, endDateActivity.day)
                        if tempEndAct<endDateActivityt1:
                            #Check if you have the minimum of notes recorded in the activity amount that you are worth in the report
                            if (((int(db((db.grades_log.activity_id == actTempo.id)&(db.grades_log.operation_log=='insert')&(db.grades_log.user_name==report.assignation.assigned_user.username)).count())*100)/int(db(db.grades.activity == actTempo.id).count()))>=int(parameters_period.percentage_income_activity)):
                                activities_M_Real.append(metric_statistics(actTempo,0,None))
                        else:
                            #Future activities with metric
                            activities_F.append(actTempo)
                    else:
                        #Check if you have the minimum of notes recorded in the activity amount that you are worth in the report
                        if (((int(db((db.grades_log.activity_id == actTempo.id)&(db.grades_log.operation_log=='insert')&(db.grades_log.user_name==report.assignation.assigned_user.username)).count())*100)/int(db(db.grades.activity == actTempo.id).count()))>=int(parameters_period.percentage_income_activity)):
                            activities_M_Real.append(metric_statistics(actTempo,0,None))
                activities_M = activities_M_Real
                #Complete with measuring future activities
                if report.report_restriction.is_final==False:
                    activities_F_temp = db((db.course_activity.semester == cperiod.id)&(db.course_activity.assignation == report.assignation.project)&(db.course_activity.date_start >= endDateActivity)&(~db.course_activity.id.belongs(activitiesMBefore))).select()
                    for awmt in activities_F_temp:
                        activities_F.append(awmt)

        #RECOVERY 1 y 2
        if report.report_restriction.is_final==True:
            cperiod = obtainPeriodReport(report)
            #students_first_recovery
            try:
                frt = int(db((db.course_first_recovery_test.semester==cperiod.id)&(db.course_first_recovery_test.project==report.assignation.project)).count())
            except:
                frt = int(0)
            if frt>0:
                if activities_M is None:
                    activities_M=[]
                activities_M.append(metric_statistics(report,1,None))

            #students_second_recovery
            try:
                srt = int(db((db.course_second_recovery_test.semester==cperiod.id)&(db.course_second_recovery_test.project==report.assignation.project)).count())
            except:
                srt = int(0)
            if srt>0:
                if activities_M is None:
                    activities_M=[]
                activities_M.append(metric_statistics(report,2,None))

    if activities_M is None:
        activities_M=[]
    if activities_WM is None:
        activities_WM=[]
    if activities_F is None:
        activities_F=[]
    return dict(activities_F=activities_F, activities_WM=activities_WM, activities_M=activities_M)

if not request.env.web2py_runtime_gae:
    db3 = DAL(config.config_db_connection_string_scheduler(), pool_size=1, check_reserved=['all'], fake_migrate=True)
else:
    db3 = DAL('google:datastore://cpfecys_scheduler')
    session.connect(request, response, db=db2)

scheduler = Scheduler(db3, dict(auto_daily = auto_daily), heartbeat = 60)

cpfecys.setup(db, auth, scheduler, auto_daily)
cpfecys.force_student_data_update(request.env.path_info, ['/student/update_data', '/default/user/logout', '/notification/get_notification_number'])

def get_date():
    import datetime
    cur_date = datetime.datetime.now()
    return cur_date.strftime("%B"), cur_date.year


# Auto Freeze happens automatically, it FREEZES the assignation when it ends.
# Successful means all needed reports and items where delivered
# Failed means something was not good :( too bad
def auto_freeze():
    # Get the current month and year
    import cpfecys

    current_month, current_year = get_date()

    # Get every period that has to be autoasigned within current month
    periods_to_work = db(db.assignation_freeze.pmonth == current_month).select()
    # For each assignation_freeze
    for period in periods_to_work:

        current_period_year = cpfecys.current_year_period()
        # this period means that we should check the ones that end in first_semester for example
        # or the ones that end in second_semester; it always applies to current year
        # Get all the assignations still active

        assignations = get_tutor_assignations()
        #excluyendo periodos variables

        # Validate each assignation
        for assignation in assignations:
            # Obtengo el inicio de la asignacion
            ass_id = assignation.period.id
            # Obtengo la duracion
            length = assignation.periods
            # finaliza en (id de cuando finaliza en period_year)
            finish = ass_id + length
            final = db.period_year(id = finish)
            if final and current_period_year:

                if final.id == current_period_year.id:
                    validation = assignation_done_succesful(assignation)
                    if validation['check_report']:
                        if validation['status']:
                            assignation.assignation_comment = validation['message']
                            assignation.assignation_status = db.assignation_status(name = 'Successful')
                        else:
                            assignation.assignation_comment = validation['message']
                            assignation.assignation_status = db.assignation_status(name = 'Failed')
                        assignation.update_record()

    db.commit()

def validar_practicantes_finales():
    """
    This method will comment the tutor status without freezing the rol
    """
    import cpfecys
    # get the current month and year
    current_month, current_year = get_date()

    # to avoid the final comments and status this interrup the normal flow
    if current_month == 'July' or current_month == 'January':
        return None

    current_period_year = cpfecys.current_year_period()

    if current_period_year is None:
        return None

    assignations = get_current_assignations(current_period_year)

    calificados = 0
    reprobados = 0
    problemas = 0

    for assignation in assignations:
        # the code was modify and now it is similar
        # to the code used in auto_freeze
        # is the final semester?
        if assignation.periods == 2:
            continue

        calificados += 1
        validation = assignation_done_succesful(assignation)

        # is there some problem?
        if not validation["check_report"]:
            problemas += 1
            continue

        # if there no error comment the student status
        msg = 'Aprobado'
        # are all deliverables completed?
        if not validation['status']:
            reprobados += 1
            msg = 'Reprueba por: ' + validation['message']

        # it change the message and update
        assignation.assignation_status_comment = msg
        assignation.update_record()

    db.commit()
    aprobados = calificados - reprobados - problemas

    resumen = {
        'aprobados': aprobados,
        'reprobados': reprobados,
        'calificados': calificados,
        'problemas': problemas
    }

    return resumen

def get_current_assignations(cur_period):
    """
    Return all current assignations
    """
    # the period will be null
    if cur_period is None:
        return None

    # get tutors
    rst = db((db.user_project.period==cur_period.id)&\
             (db.user_project.assignation_status==None)&\
             (db.user_project.hours!=20)).select()

    return rst

def assignation_done_succesful(assignation):
    ## Validate Reports
    # Get all report restrictions that apply up to now
    # Start date to get them depends on assignation start
    # End date that apply to reports is current date
    # Check if they where delivered
    # Get all the reports of this assignation
    average_report = 0
    status = True
    check_report = True
    message = ''
    total_reports = assignation.report.count()
    min_score = db(db.custom_parameters.id>0).select().first().min_score
    sum_reports = 0.0
    validate_Report = True
    for report in assignation.report.select():
        # Check DTT Approval
        if report.dtt_approval is None:
            # I don't think status has to change since by average the student can win
            # status = False
            check_report = False
            message += T('A report was not checked by DTT Admin. Contact Admin.')
            message += ' '
        elif report.dtt_approval is False:
            # I don't think status has to change since by average the student can win
            status = False
            message += T('A report was not approved by DTT Admin. Thus considered failed.')
            message += ' '
        else:
            # Save for average grading
            if report.score is None:
                if report.admin_score is None:
                    if report.min_score is None:
                        report.admin_score = min_score
                    else:
                        report.admin_score = report.min_score
                    report.update_record()
                    sum_reports += float(report.admin_score)
                else:
                    sum_reports += float(report.admin_score)
                if report.min_score is None:
                    if report.admin_score < min_score:
                        validate_Report = False
                else:
                    if report.admin_score < report.min_score:
                        validate_Report = False
            else:
                sum_reports += float(report.score)
                if report.min_score is None:
                    if report.score < min_score:
                        validate_Report = False
                else:
                    if report.score < report.min_score:
                        validate_Report = False
    # Check the grade (average) to be beyond the expected minimal grade in current settings
    # is the total_reports 0?
    avg = 0.0
    if total_reports:
        avg = float(sum_reports) / float(total_reports)

    if avg < min_score or\
        validate_Report == False:
        #he lost the practice due to reports
        status = False
        message += T('To consider assignation to be valid, report grades should be above: ') + min_score
        message += ' '
        message += T('Reports Grade is below minimun note; that sets this assignation as lost.')
    ## Validate Items
    # Get all item restrictions that apply up to now
    # Ok, ive the assignation, it has my starting period of final practice and the length
    # assignation.period Holds the starting period, assignation.periods holds the ammount of them
    period = assignation.period
    import cpfecys
    for x in range (0, assignation.periods):
        # Get the item_restrictions for this period, for the area of the assignation,
        # removing the ones that don't belong to this assignation since are exceptions
        # and not allowing optionals
        restrictionsItem = []
        for rI in db(db.item_restriction_exception.project == assignation.project.id).select():
            restrictionsItem.append(rI.item_restriction)
        if len(restrictionsItem)==0:
            restrictionsItem.append(-1)
        rows = db(((db.item_restriction.period==period) | (db.item_restriction.permanent==True))&
                (db.item_restriction.is_enabled==True)&
                (db.item_restriction.period_type==2)&
                (db.item_restriction_area.item_restriction==db.item_restriction.id)&
                (db.item_restriction_area.area_level==assignation.project.area_level.id)&
                (~db.item_restriction.id.belongs(restrictionsItem))&
                (db.item_restriction.optional == False)).select()
        for row in rows:
            items = db((db.item.item_restriction==row.item_restriction.id)&(db.item.assignation==assignation.id)&(db.item.is_active != False)).select()
            if not items:
                status = False
                message += T('There is a missing deliverable item: ') +\
                           row.item_restriction.name + '.'
            elif len(items) == 0:
                status = False
                message += T('There is a missing deliverable item: ') +\
                           row.item_restriction.name + '.'
            elif (row.item_restriction.item_type.name == 'File'):
                #check there is an uploaded file
                if not items.first().uploaded_file:
                    status = False
                    message += T('There is not an uploaded file for: ') +\
                               row.item_restriction.name + ' item.'
            elif (row.item_restriction.item_type.name == 'Activity'):
                #check there is an activity
                if not items.first().done_activity:
                    status = False
                    message += T('Activity not completed: ') +\
                               row.item_restriction.name + '.'
            elif (row.item_restriction.item_type.name == 'Grade Activity'):
                #check there is an activity with minimun grade
                if items.first().score < items.first().min_score:
                    status = False
                    message += T('Activity: ') + row.item_restriction.name +\
                               ' ' + T('has not met minimal score of: ') +\
                               str(items.first().min_score) + '.'
            elif (row.item_restriction.item_type.name == 'Schedule'):
                #check there is an activity
                if not items.first().item_schedule.count():
                    status = False
                    message += T('Schedule is missing: ') + row.item_restriction.name + '.'
        #TODO REVISION
        # print('period')
        # print(period)
        # if (period.period == cpfecys.first_period):
        #     #this means the next one is second period of the same year
        #     period = db.period_year(yearp = period.yearp, period = cpfecys.second_period)
        # else:
        #     #this means the next one is first period of the next year
        #     period = db.period_year(yearp = period.yearp + 1, period = cpfecys.first_period)
        # if period is None:
        #     break
    # Check if they where delivered
    return {'status':status, 'message':message, 'check_report':check_report}

def check_exception_semester_repeat():
    import datetime
    import cpfecys
    cperiod = cpfecys.current_year_period()
    year = str(cperiod.yearp)
    cdate = datetime.datetime.now()
    compareDate = datetime.datetime(cdate.year, cdate.month, cdate.day)
    #compareDate = datetime.strptime( + '-'+cdate.month+'-'+cdate.day, "%Y-%m-%d")
    if cperiod.period == 1:
        #Period
        initSemester = datetime.datetime(cdate.year, 1, 1)
        #Time exception for the courses
        extraTime = datetime.datetime(cdate.year, 3, 1)

        if compareDate==initSemester:
            db(db.course_limit_exception.semester_repet==False).delete()
            db(db.course_limit_exception.semester_repet==True).update(date_finish=extraTime)
        else:
            exceptions = db((db.course_limit_exception.date_finish<initSemester)).select()
            if exceptions.first() is not None:
                for exception in exceptions:
                    if exception.semester_repet==True:
                        db(db.course_limit_exception.id==exception.id).update(date_finish=extraTime)
                    else:
                        db(db.course_limit_exception.id==exception.id).delete()
    else:
        #Period
        #initSemester = datetime.strptime(year + '-06-01', "%Y-%m-%d")
        initSemester = datetime.datetime(cdate.year, 6, 1)
        #Time exception for the courses
        #extraTime = datetime.strptime(year + '-09-01', "%Y-%m-%d")
        extraTime = datetime.datetime(cdate.year, 9, 1)

        if compareDate==initSemester:
            db(db.course_limit_exception.semester_repet==False).delete()
            db(db.course_limit_exception.semester_repet==True).update(date_finish=extraTime)
        else:
            exceptions = db((db.course_limit_exception.date_finish<initSemester)).select()
            if exceptions.first() is not None:
                for exception in exceptions:
                    if exception.semester_repet==True:
                        db(db.course_limit_exception.id==exception.id).update(date_finish=extraTime)
                    else:
                        db(db.course_limit_exception.id==exception.id).delete()
    db.commit()

# 4 tarea automatica, no tiene indicencia en periodos variables, puesto que solo toma el perido actual, primero o seg semestre
def automation_activities_assigned():
    #ACTUAL AND FUTURE TIME
    import time
    from datetime import date, datetime, timedelta
    officialTime = date.today()
    futureTime = officialTime + timedelta(days=1)
    #CURRENT PERIOD
    import cpfecys
    year = cpfecys.current_year_period()
    #ALL ACTIVITIES OF THE CURRENT PERIOD
    for activity in db(db.course_assigned_activity.semester==year.id).select():
        if activity.status == T('Pending')\
           and activity.date_start == futureTime:
            #REMINDER
            subject = T('[DTT]Automatic Notification - Reminder activity assigned by the professor')
            message = '<html>' +T('You are reminded that tomorrow should develop the following activity:')+'<br>'
            message += T('Activity data:')+'<br>'
            message += T('Name')+': '+activity.name+'<br>'
            message += T('Description')+': '+activity.description+'<br>'
            message += T('Date')+': '+str(activity.date_start)+'<br>'
            if activity.report_required == True:
                message += T('Report Required')+': '+T('You need to enter a report of the activity to be taken as valid.')+'<br>'
            message += activity.assignation.name+'<br>'+T(activity.semester.period.name)+' '+str(activity.semester.yearp)+'<br>Sistema de Seguimiento de La Escuela de Ciencias y Sistemas<br> Facultad de Ingeniería - Universidad de San Carlos de Guatemala</html>'
            #Log General del Envio
            teacher = db((db.user_project.project == activity.assignation)&
                      ((db.user_project.period <= activity.semester) & ((db.user_project.period + db.user_project.periods) > activity.semester))&
                      (db.user_project.assigned_user == db.auth_user.id)&
                      (db.auth_membership.user_id == db.auth_user.id)&
                      (db.auth_membership.group_id == db.auth_group.id)&
                      (db.auth_group.role == 'Teacher')).select().first()
            row = db.notification_general_log4.insert(subject=subject,
                                                sent_message=message,
                                                emisor=teacher.auth_user.username,
                                                course=activity.assignation.name,
                                                yearp=activity.semester.yearp,
                                                period=(activity.semester.period.name))
            ListadoCorreos=None
            email_list_log=None
            students = db((db.user_project.project == activity.assignation)&
                      ((db.user_project.period <= activity.semester) & ((db.user_project.period + db.user_project.periods) > activity.semester))&
                      (db.user_project.assigned_user == db.auth_user.id)&
                      (db.auth_membership.user_id == db.auth_user.id)&
                      (db.auth_membership.group_id == db.auth_group.id)&
                      (db.auth_group.role == 'Student')).select()

            for usersT in students:
                if ListadoCorreos is None:
                    ListadoCorreos=[]
                    email_list_log=usersT.auth_user.email
                else:
                    email_list_log+=','+usersT.auth_user.email
                ListadoCorreos.append(usersT.auth_user.email)

            if ListadoCorreos is not None:
                was_sent = mail.send(to='dtt.ecys@dtt-ecys.org',subject=subject,message=message, bcc=ListadoCorreos)
                db.mailer_log.insert(sent_message = message, destination = email_list_log, result_log = str(mail.error or '') + ':' + str(mail.result), success = was_sent, emisor='DTT-ECYS')
                #Notification LOG
                email_list =str(email_list_log).split(",")
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
                    db.notification_log4.insert(destination = email_temp,
                                                username = username_var,
                                                result_log = str(mail.error or '') + ':' + str(mail.result),
                                                success = was_sent,
                                                register=row.id)
        elif activity.status==T('Pending') and activity.date_start==officialTime:
            db(db.course_assigned_activity.id == activity.id).update(status = T('Active'))
        elif (activity.status==T('Active') and activity.date_start<officialTime) or (activity.status==T('Pending') and activity.date_start<officialTime):
            status = T('Completed')
            #Activity requires report
            if activity.report_required==True:
                if activity.fileReport is None:
                    status = T('Pending') +' '+T('Item Delivery')
                else:
                    if activity.automatic_approval==False:
                        status = T('Grade pending')
            else:
                if activity.automatic_approval==False:
                    status = T('Grade pending')
            db(db.course_assigned_activity.id == activity.id).update(status = status)
    db.commit()

#emarquez: exclusion periodos variables
def automation_evaluations():
    import datetime
    #from dateutil  import relativedelta
    import cpfecys
    cperiod = cpfecys.current_year_period()
    year = str(cperiod.yearp)
    cdate = datetime.datetime.now()

    initSemester = None

    if cperiod.period == 1:
        #First Semester date start
        initSemester = datetime.date(cdate.year, 1, 1)
    else:
        #Second Semester date start
        initSemester = datetime.date(cdate.year, 6, 1)

    evaluations = db((db.evaluation.date_finish<initSemester)).select()

    if evaluations.first() is None:
        return

    for evaluation in evaluations:
        if evaluation.semester_repeat:
            db(db.evaluation.id==evaluation.id)\
            .update(semester_repeat=False)

            date_start_temp = evaluation.date_start
            date_finish_temp = evaluation.date_finish

            db.evaluation.insert(date_start=date_start_temp,
                                 date_finish=date_finish_temp,
                                 semester_repeat=True,
                                 description=evaluation.description,
                                 period=cperiod.id,
                                 repository_evaluation=evaluation.repository_evaluation)
    """
    #First Semester
    if cperiod.period == 1:
        evaluations = db((db.evaluation.date_finish<initSemester)).select()
        if evaluations.first() is not None:
            for evaluation in evaluations:
                if evaluation.semester_repeat == True:
                    db(db.evaluation.id==evaluation.id)\
                    .update(semester_repeat=False)

                    if evaluation.date_start.month == 12 \
                       or evaluation.date_start.month == 11:
                        sum_month_1 = 5
                    else:
                        sum_month_1 = 6

                    if evaluation.date_finish.month == 12:
                        sum_month_2 = 5
                    else:
                        sum_month_2 = 6

                    date_start_temp = evaluation.date_start #+ relativedelta.relativedelta(months=sum_month_1)
                    date_finish_temp = evaluation.date_finish #+ relativedelta.relativedelta(months=sum_month_2)

                    db.evaluation.insert(date_start=date_start_temp,
                                            date_finish=date_finish_temp,
                                            semester_repeat=True,
                                            description=evaluation.description,
                                            period=cperiod.id,
                                            repository_evaluation=evaluation.repository_evaluation)

    #Second Semester : emarquez: modificado para exluir periodos variables
    elif cperiod.period == 2:
        evaluations = db((db.evaluation.date_finish<initSemester2)).select()
        if evaluations.first() is not None:
            for evaluation in evaluations:
                if evaluation.semester_repeat == True:
                    db(db.evaluation.id==evaluation.id)\
                    .update(semester_repeat=False)

                    sum_month_1 = 6

                    if evaluation.date_finish.month == 5:
                        sum_month_2 = 7
                    else:
                        sum_month_2 = 6

                    #from dateutil import relativedelta
                    #from dateutil.relativedelta import relativedelta
                    date_start_temp = evaluation.date_start #+ relativedelta.relativedelta(months=sum_month_1)
                    date_finish_temp = evaluation.date_finish #+ relativedelta.relativedelta(months=sum_month_2)

                    db.evaluation.insert(date_start=date_start_temp, #+ datetime.timedelta(date_start_temp),
                                         date_finish=date_finish_temp, #+ datetime.timedelta(date_finish_temp),
                                         semester_repeat=True,
                                         description=evaluation.description,
                                         period=cperiod.id,
                                         repository_evaluation=evaluation.repository_evaluation)
    """
    db.commit()

#modificar para excluir periodos variables #ANALIZANDOOO
def send_evaluation_notifications():
    import datetime
    import cpfecys
    cperiod = cpfecys.current_year_period()
    year = str(cperiod.yearp)
    cdate = datetime.datetime.now()
    date_now = datetime.date(cdate.year, cdate.month, cdate.day)

    evaluation = db((db.evaluation.period==cperiod.id)&(db.evaluation.date_start==date_now)).select().first()

    email_list = []
    if  evaluation is not None:
        for membership in db((db.auth_membership.group_id==evaluation.repository_evaluation.user_type_evaluator)).select():
            send_mail = False
            links = ""
            try:
                if db((db.user_project.assigned_user == membership.user_id) & (db.user_project.period == cperiod.id)).select().first is not None:
                   send_mail = True
                   #links = links + URL('evaluation', 'evaluation_list', vars=dict(project = user_assignation.project.name, period = cperiod.id)) + "<br>"
            except:
                None
            try:
                academic_var = db.academic(db.academic.id_auth_user==membership.user_id)
                if db((db.academic_course_assignation.carnet==academic_var.id)&(db.academic_course_assignation.semester==cperiod.id)).select().first is not None:
                    send_mail = True
                    #links = links + "<br>"
            except:
                None
            if send_mail == True:
                email_list.append(membership.user_id.email)
        try:
            subject = "EVALUACIONES DE DESEMPEÑO 360"
            message = "Por este medio le solicitamos apoyo para realizar las evaluaciones de desempeño correspondientes, las cuales se encuentran disponibles en el área de <b>Evaluaciones de desempeño 360</b>.<br><br>"+ \
                        cpfecys.get_domain() + URL('activity_control', 'courses_list')
            was_sent = mail.send(to='dtt.ecys@dtt-ecys.org',subject=subject,message=message, bcc=email_list)
            #MAILER LOG
            db.mailer_log.insert(sent_message = message,
                             destination = str(email_list),
                             result_log = str(mail.error or '') + ':' + \
                             str(mail.result),
                             success = was_sent, emisor="dtt.ecys@dtt-ecys.org")
            if was_sent==False:
                control=control+1
            return control
        except:
            None
    db.commit()

def send_notification_for_starting_evaluations():
    import datetime
    import cpfecys
    cdate = datetime.datetime.now()
    date_now = datetime.date(cdate.year, cdate.month, cdate.day)
    email_list = []
    #consulto si hay evaluaciones  que inicien el dia de hoy
    list = db(db.evaluation.date_start == date_now).select(db.evaluation.date_finish, db.evaluation.description)
    if list.first() is not None:
        #busco al administrador del sistema, a quien se debera de notificar
        admins = db(db.auth_membership.group_id == 1).select(db.auth_user.email,
            join=[
                db.auth_user.on(db.auth_membership.user_id == db.auth_user.id)])
        for admin in admins:
            email_list.append(admin.auth_user.email)
        pass
        #ahora genero el contenido del correo
        tabla = "<table><thead><th>Descripcion</th><th>Fecha de finalizacion</th></thead><tbody>"
        for row in list:
            tabla += "<tr><td>" + row.evaluation.description + "</td><td>"+ row.evaluation.date_finish+"</td></tr>"
        pass
        tabla += "</tbody></table>"
        print( "###########Tabla")
        print(tabla)
        try:
            subject = "LISTADO DE EVALUACIONES DE DESEMPEÑO QUE INICIAN HOY"
            message = "Por este medio le informamos las siguientes evaluaciones inician el dia de hoy.<br>"
            was_sent = mail.send(to='dtt.ecys@dtt-ecys.org',subject=subject,message=message, bcc=email_list)
            #MAILER LOG
            db.mailer_log.insert(sent_message = message,
                             destination = str(email_list),
                             result_log = str(mail.error or '') + ':' + \
                             str(mail.result),
                             success = was_sent, emisor="dtt.ecys@dtt-ecys.org")
            if was_sent==False:
                control=control+1
            return control
        except:
            None
        db.commit()
    pass
