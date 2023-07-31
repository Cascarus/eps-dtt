import cpfecys
import datetime
import math
import collections

@auth.requires_login()
@auth.requires_membership('Teacher')
def courses():
    #requires parameter year_period if no one is provided then it is automatically detected
    #and shows the current period
    year_period = request.vars['year_period']
    MAX_DISPLAY = 1
    currentyear_period = db(db.period_year.id == year_period).select(db.period_year.id, db.period_year.period, db.period_year.yearp).first()
    if not currentyear_period:
        currentyear_period = cpfecys.current_year_period()
    
    current_data = db((db.user_project.period <= currentyear_period.id) & ((db.user_project.period.cast('integer') + db.user_project.periods) > currentyear_period.id)
                    & (db.user_project.assigned_user == auth.user.id)).select(db.user_project.project)
    
    current_period_name = T(cpfecys.first_period_name) if currentyear_period.period == cpfecys.first_period.id else T(cpfecys.second_period_name)
    start_index = currentyear_period.id - MAX_DISPLAY - 1
    if start_index < 1: start_index = 0  
    end_index = currentyear_period.id + MAX_DISPLAY
    periods_before = db(db.period_year).select(db.period_year.id, db.period_year.period, db.period_year.yearp, limitby=(start_index, currentyear_period.id - 1))
    periods_after = db(db.period_year).select(db.period_year.id, db.period_year.period, db.period_year.yearp, limitby=(currentyear_period.id, end_index))
    other_periods = db(db.period_year).select(db.period_year.id, db.period_year.period, db.period_year.yearp)

    return dict(
        current_data=current_data,
        currentyear_period=currentyear_period,
        current_period_name=current_period_name,
        periods_before=periods_before,
        periods_after=periods_after,
        other_periods=other_periods
    )

@auth.requires_login()
@auth.requires_membership('Teacher')
def final_practice():
    def assignation_range(assignation):
        cperiod = cpfecys.current_year_period()
        ends = assignation.user_project.period + assignation.user_project.periods
        return db((db.period_year.id >= assignation.user_project.period) & (db.period_year.id < ends)
                & (db.period_year.id <= cperiod.id)).select()

    def available_item_restriction(period_year, user_project):
        return db(((db.item_restriction.period == period_year) | (db.item_restriction.permanent == True))
                & (db.item_restriction.is_enabled == True) & (db.item_restriction.hidden_from_teacher != True)
                & (db.item_restriction_area.item_restriction == db.item_restriction.id) & (db.item_restriction_area.area_level == user_project.user_project.project.area_level))

    def restriction_project_exception(item_restriction_id, project_id):
        return db((db.item_restriction_exception.project == project_id) & (db.item_restriction_exception.item_restriction == item_restriction_id))

    def items_instance(item_restriction, assignation):
        return db((db.item.item_restriction == item_restriction) & (db.item.assignation == assignation)
                & (db.item.is_active == True))

    def get_items(period, assignation):
        restrictions = db((db.item_restriction.id == db.item_restriction_exception.item_restriction) & (db.item_restriction_exception.project == final_practice.project.id)).select(
                            db.item_restriction.ALL
                        )
        return db((db.item.created == period.id) & (db.item.assignation == assignation.id)
                & (~db.item.item_restriction.belongs(restrictions))).select(db.item.ALL)

    def compare_last_day(last_day):
        cdate = datetime.datetime.now()
        last_day = datetime.datetime.strptime(str(last_day), "%Y-%m-%d")
        if cdate > last_day:
            return True
        return False

    def get_current_reports(period):
        cperiod = cpfecys.current_year_period()
        year = str(cperiod.yearp)
        if period.period == 1:
            start = datetime.datetime.strptime(f'{year}-01-01', "%Y-%m-%d")
            end = datetime.datetime.strptime(f'{year}-06-01', "%Y-%m-%d")
        else:
            start = datetime.datetime.strptime(f'{year}-06-01', "%Y-%m-%d")
            end = datetime.datetime.strptime(f'{year}-12-31', "%Y-%m-%d")

        reports = db((db.report.assignation == final_practice.user_project.id) & (db.report.status.name != 'Grading')
                & (db.report.created >= start) & (db.report.created <= end))
        avg = reports.select((db.report.score.sum() / db.report.score.count()).with_alias('avg')).first()['avg'] or 0
        reports = reports.select(db.report.report_restriction, db.report.created, db.report.status, db.report.score, db.report.id), avg
        return reports

    assignation = request.vars['assignation']
    if not assignation: redirect(URL('courses'))

    assignation = db(db.user_project.id == assignation).select().first()
    final_practice = db((db.user_project.id == assignation) & (db.user_project.assigned_user == db.auth_user.id)
                    & (db.user_project.project == db.project.id) & (db.project.area_level == db.area_level.id)
                    & (db.user_project.period == db.period_year.id)).select(
                        db.user_project.periods,
                        db.user_project.period,
                        db.user_project.id,
                        db.user_project.project,
                        db.project.name,
                        db.auth_user.username,
                        db.auth_user.first_name,
                        db.auth_user.last_name,
                        db.area_level.name,
                        db.period_year.period,
                        db.period_year.yearp,
                        db.project.area_level
                    )
    if not final_practice: redirect(URL('courses'))

    final_practice = final_practice.first()
    available_periods = db((db.period_year.id >= final_practice.user_project.period) 
                        & (db.period_year.id < (final_practice.user_project.period + final_practice.user_project.periods))).select(
                            db.period_year.id,
                            db.period_year.yearp,
                            db.period_year.period
                        )

    items = db((db.item.created == cpfecys.current_year_period()) & (db.item.assignation == final_practice.user_project.id)).select()
    total_items = db((db.item.created == cpfecys.current_year_period())).select()

    return dict(
        final_practice=final_practice,
        available_periods=available_periods,
        items=items,
        total_items=total_items,
        get_items=get_items,
        assignation_range=assignation_range,
        available_item_restriction=available_item_restriction,
        assignation=assignation,
        restriction_project_exception=restriction_project_exception,
        items_instance=items_instance,
        get_current_reports=get_current_reports,
        compare_last_day=compare_last_day
    )

@auth.requires_login()
@auth.requires_membership('Teacher')
def graphs():
    #A helper to display this code within js stuff
    def values_display(values):
        result = "["
        old_user = None
        for item in values:
            if old_user != item.user_project.assigned_user.username:
                if old_user is not None:
                    result += "]}, "
                old_user = item.user_project.assigned_user.username
                result += "{name: '" + item.user_project.assigned_user.username + " - " + item.user_project.assigned_user.first_name + "', "
                result += "data: ["
            #categories.add(item.report.report_restriction)
            result += f'{item.report.desertion_continued or 0}, '
        result += "]}]"
        return XML(result)
    
    #A helper to display this code within js stuff
    def values_display_activities(values):
        result = "["
        old_user = None
        for item in values:
            if old_user != item.user_project.assigned_user.username:
                if old_user is not None:
                    result += "]},"
                old_user = item.user_project.assigned_user.username
                result += "{name: '" + item.user_project.assigned_user.username + " - " + item.user_project.assigned_user.first_name + "', "
                result += "data: ["
            result += f'{item.log_metrics.mediana or 0}, '
        result += "]}]"
        return XML(result)
    
    #Requires parameter of project if none is provided then redirected to courses
    #this also validates the current user is assigned in the project
    project_id = request.vars['project']
    if not project_id: redirect(URL('courses'))
    
    current_project = db((db.user_project.assigned_user == auth.user.id) & (db.project.id == project_id)).select(
                            db.project.id,
                            db.project.name,
                        ).first()
    if not current_project: redirect(URL('courses'))

    #Requires parameter year_period if no one is provided then it is automatically detected and shows the current period
    year_period = request.vars['year_period']
    MAX_DISPLAY = 1
    currentyear_period = db(db.period_year.id == year_period).select(db.period_year.id, db.period_year.yearp, db.period_year.period).first()
    if not currentyear_period:
        currentyear_period = cpfecys.current_year_period()

    current_data = db((db.user_project.period <= currentyear_period.id) & ((db.user_project.period.cast('integer') + db.user_project.periods) > currentyear_period.id)
                & (db.user_project.project == current_project.id) & (db.auth_group.role == 'Student')
                & (db.auth_membership.group_id == db.auth_group.id) & (db.user_project.assigned_user == db.auth_membership.user_id)).select()
    current_period_name = T(cpfecys.second_period_name)
    #if we are second semester then start is 1st july
    start_date = datetime.datetime(currentyear_period.yearp, 7, 7)
    end_date = datetime.datetime(currentyear_period.yearp, 12, 31)
    if currentyear_period.period == cpfecys.first_period.id:
        current_period_name = T(cpfecys.first_period_name)
        #else we are on first semester, start jan 1st
        start_date = datetime.datetime(currentyear_period.yearp, 1, 1)
        end_date = datetime.datetime(currentyear_period.yearp, 6, 30)
    
    # i need all reports delivered by students for this semester
    reports = db((db.user_project.period <= currentyear_period.id) & ((db.user_project.period.cast('integer') + db.user_project.periods) > currentyear_period.id)
            & (db.user_project.project == current_project.id) & (db.auth_group.role == 'Student')
            & (db.auth_membership.group_id == db.auth_group.id) & (db.user_project.assigned_user == db.auth_membership.user_id)
            & (db.report_restriction.start_date >= start_date) & (db.report_restriction.start_date <= end_date)).select(
                db.report.report_restriction,
                db.report.desertion_continued,
                db.user_project.assigned_user,
                orderby=db.user_project.assigned_user | db.report_restriction.start_date | db.report_restriction.name,
                left=[
                    db.report.on(db.user_project.id == db.report.assignation),
                    db.report_restriction.on(db.report.report_restriction == db.report_restriction.id)
                ]
            )
    
    report_activities = db((db.user_project.period <= currentyear_period.id) & ((db.user_project.period.cast('integer') + db.user_project.periods) > currentyear_period.id)
                        & (db.user_project.project == current_project.id) & (db.auth_group.role == 'Student')
                        & (db.auth_membership.group_id == db.auth_group.id) & (db.user_project.assigned_user == db.auth_membership.user_id)
                        & (db.report_restriction.start_date >= start_date) & (db.report_restriction.start_date <= end_date)
                        & (db.report.id == db.log_metrics.report)).select(
                            db.log_metrics.mediana,
                            db.log_metrics.metrics_type,
                            db.log_metrics.created,
                            db.user_project.assigned_user,
                            orderby=db.user_project.assigned_user | db.report_restriction.start_date | db.report_restriction.name | db.log_metrics.created,
                            left=[
                                db.report.on(db.user_project.id == db.report.assignation),
                                db.report_restriction.on(db.report.report_restriction == db.report_restriction.id)
                            ]
                        )
    
    #Average of laboratory and period
    query_lab = f"select obtenerPromedio('T', {current_project.id}, {currentyear_period.id}) as promedio;"
    query_curso = f"select obtenerPromedio('F', {current_project.id}, {currentyear_period.id}) as promedio;"
    avg_lab = db.executesql(query_lab, as_dict=True)
    avg_curso = db.executesql(query_curso, as_dict=True)
    var_avg_lab = avg_lab[0]['promedio'] or 0
    var_avg_curso = avg_curso[0]['promedio'] or 0
    avg_l = ["Laboratorio", var_avg_lab]
    avg_c = ["Curso", var_avg_curso]

    avg = []
    avg.append(avg_c)
    avg.append(avg_l)
    
    start_index = currentyear_period.id - MAX_DISPLAY - 1
    if start_index < 1:
        start_index = 0
    end_index = currentyear_period.id + MAX_DISPLAY

    if cpfecys.is_semestre(request.vars['year_period']):
        periods_before = db((db.period_year.period == 1) | (db.period_year.period == 2)).select(
                            db.period_year.id,
                            db.period_year.yearp,
                            db.period_year.period,
                            limitby=(start_index,  currentyear_period.id - 1)
                        )
        periods_after = db((db.period_year.period == 1) | (db.period_year.period == 2)).select(
                            db.period_year.id,
                            db.period_year.yearp,
                            db.period_year.period,
                            limitby=(currentyear_period.id,  end_index)
                        )
        other_periods = db((db.period_year.period == 1) | (db.period_year.period == 2)).select(db.period_year.id, db.period_year.yearp, db.period_year.period)
    else:    
        periods_before = db(db.period_year).select(
                            db.period_year.id,
                            db.period_year.yearp,
                            db.period_year.period,
                            limitby=(start_index, currentyear_period.id - 1)
                        )
        periods_after = db(db.period_year).select(
                            db.period_year.id,
                            db.period_year.yearp,
                            db.period_year.period,
                            limitby=(currentyear_period.id, end_index)
                        )
        other_periods = db(db.period_year).select(db.period_year.id, db.period_year.yearp, db.period_year.period)

    return dict(
        current_project=current_project,
        current_data=current_data,
        currentyear_period=currentyear_period,
        current_period_name=current_period_name,
        current_reports=reports,
        values_display=values_display,
        values_display_activities=values_display_activities,
        report_activities=report_activities,
        periods_before=periods_before,
        periods_after=periods_after,
        other_periods=other_periods,
        avg=avg
    )

@auth.requires_login()
@auth.requires_membership('Teacher')
def index():
    return dict()

@auth.requires_login()
@auth.requires_membership('Teacher')
def students():
    #requires parameter of project if none is provided then redirected to courses
    project_id = request.vars['project']
    if not project_id: redirect(URL('courses'))

    #This also validates the current user is assigned in the project
    current_project = db((db.user_project.assigned_user == auth.user.id) & (db.project.id == project_id)).select(db.project.id, db.project.name).first()
    if not current_project: redirect(URL('courses'))

    #Requires parameter year_period if no one is provided then it is automatically detected and shows the current period
    year_period = request.vars['year_period']
    MAX_DISPLAY = 1
    currentyear_period = db.period_year(db.period_year.id == year_period)
    if not currentyear_period:
        currentyear_period = current_year_period()

    current_data = db((db.user_project.period <= currentyear_period.id) & ((db.user_project.period.cast('integer') + db.user_project.periods) > currentyear_period.id)
                & (db.user_project.project == current_project.id) & (db.auth_group.role == 'Student')
                & (db.auth_membership.group_id == db.auth_group.id) & (db.user_project.assigned_user == db.auth_membership.user_id)).select(
                    db.user_project.id,
                    db.user_project.assigned_user
                )
    current_period_name = T(cpfecys.second_period_name)

    # A helper to display this code within js stuff
    start_index = currentyear_period.id - MAX_DISPLAY - 1
    if start_index < 1:
        start_index = 0
    end_index = currentyear_period.id + MAX_DISPLAY

    #emarquez: 06sept, adaptacion periodos variables
    if cpfecys.is_semestre(request.vars['year_period']):
        periods_before = db((db.period_year.period == '1') | (db.period_year.period == '2')).select(
                            db.period_year.id,
                            db.period_year.yearp,
                            db.period_year.period,
                            limitby=(start_index,  currentyear_period.id - 1)
                        )
        periods_after = db((db.period_year.period == '1') | (db.period_year.period == '2')).select(
                            db.period_year.id,
                            db.period_year.yearp,
                            db.period_year.period,
                            limitby=(currentyear_period.id,  end_index)
                        )
        other_periods = db((db.period_year.period == '1') | (db.period_year.period == '2')).select(
                            db.period_year.id,
                            db.period_year.yearp,
                            db.period_year.period
                        )
    else:    
        periods_before = db(db.period_year).select(   
                            db.period_year.id,
                            db.period_year.yearp,
                            db.period_year.period,
                            limitby=(start_index, currentyear_period.id - 1)
                        )
        periods_after = db(db.period_year).select(    
                            db.period_year.id,
                            db.period_year.yearp,
                            db.period_year.period,
                            limitby=(currentyear_period.id, end_index)
                        )
        other_periods = db(db.period_year).select(    
                            db.period_year.id,
                            db.period_year.yearp,
                            db.period_year.period
                        )
    
    return dict(
        current_project=current_project,
        current_data=current_data,
        currentyear_period=currentyear_period,
        current_period_name=current_period_name,
        periods_before=periods_before,
        periods_after=periods_after,
        other_periods=other_periods
    )

@auth.requires_login()
@auth.requires_membership('Teacher')
def report():
    cdate = datetime.datetime.now()
    report = request.vars['report']
    report = db(db.report.id == report).select(
                db.report.id,
                db.report.score_date,
                db.report.assignation,
                db.report.status,
                db.report.report_restriction,
                db.report.score,
                db.report.teacher_comment,
                db.report.heading,
                db.report.hours,
                db.report.desertion_started,
                db.report.desertion_gone,
                db.report.desertion_continued,
                db.report.footer,
                db.report.times_graded
            ).first()
    report.times_graded = report.times_graded or 0
    parameters = cpfecys.get_custom_parameters()
    valid = report is not None
    next_date = None
    if valid:
        valid = cpfecys.teacher_validation_report_access(report.id)

    if request.args(0) == 'view':
        if valid:
            if report.score_date:
                next_date = report.score_date + datetime.timedelta(days=parameters.rescore_max_days)
            response.view = 'teacher/report_view.html'
            assignation_reports = db(db.report.assignation == report.assignation).select()
            teacher = db(db.auth_user.id == auth.user.id).select().first()

            #***********************************************************************************************************************
            #******************************************************PHASE 2 DTT******************************************************
            activities_wm = None
            activities_m = None
            activities_f = None
            if report.assignation.project.area_level.name == 'DTT Tutor Académico' and (report.status.name == 'Draft' or report.status.name == 'Recheck'):
                #Get the minimum and maximum date of the report
                cperiod = obtain_period_report(report)
                parameters_period = db(db.student_control_period.period_name == f'{T(cperiod.period.name)} {cperiod.yearp}').select(db.student_control_period.percentage_income_activity).first()
                end_date_activity = None
                init_semester = None
                if cperiod.period == 1:
                    init_semester = datetime.datetime.strptime(f'{cperiod.yearp}-01-01', "%Y-%m-%d")
                    if not report.report_restriction.is_final:
                        activities_f = []
                        name_report_split = report.report_restriction.name.upper()
                        name_report_split = name_report_split.split(' ')
                        for word in name_report_split:
                            if word == 'ENERO':
                                end_date_activity = datetime.datetime.strptime(f'{cperiod.yearp}-02-01', "%Y-%m-%d")
                            elif word == 'FEBRERO':
                                end_date_activity = datetime.datetime.strptime(f'{cperiod.yearp}-03-01', "%Y-%m-%d")
                            elif word == 'MARZO':
                                end_date_activity = datetime.datetime.strptime(f'{cperiod.yearp}-04-01', "%Y-%m-%d")
                            elif word == 'ABRIL':
                                end_date_activity = datetime.datetime.strptime(f'{cperiod.yearp}-05-01', "%Y-%m-%d")
                            elif word == 'MAYO':
                                end_date_activity = datetime.datetime.strptime(f'{cperiod.yearp}-06-01', "%Y-%m-%d")
                    else:
                        end_date_activity = datetime.datetime.strptime(f'{cperiod.yearp}-06-01', "%Y-%m-%d")
                else:
                    init_semester = datetime.datetime.strptime(f'{cperiod.yearp}-06-01', "%Y-%m-%d")
                    if not report.report_restriction.is_final:
                        activities_f = []
                        name_report_split = report.report_restriction.name.upper()
                        name_report_split = name_report_split.split(' ')
                        for word in name_report_split:
                            if word == 'JUNIO':
                                end_date_activity = datetime.datetime.strptime(f'{cperiod.yearp}-07-01', "%Y-%m-%d")
                            elif word == 'JULIO':
                                end_date_activity = datetime.datetime.strptime(f'{cperiod.yearp}-08-01', "%Y-%m-%d")
                            elif word == 'AGOSTO':
                                end_date_activity = datetime.datetime.strptime(f'{cperiod.yearp}-09-01', "%Y-%m-%d")
                            elif word == 'SEPTIEMBRE':
                                end_date_activity = datetime.datetime.strptime(f'{cperiod.yearp}-10-01', "%Y-%m-%d")
                            elif word == 'OCTUBRE':
                                end_date_activity = datetime.datetime.strptime(f'{cperiod.yearp}-11-01', "%Y-%m-%d")
                            elif word == 'NOVIEMBRE':
                                end_date_activity = datetime.datetime.strptime(f'{cperiod.yearp}-12-01', "%Y-%m-%d")
                            elif word == 'DICIEMBRE':
                                end_date_activity = datetime.datetime.strptime(f'{cperiod.yearp + 1}-01-01', "%Y-%m-%d")
                    else:
                        end_date_activity = datetime.datetime.strptime(f'{cperiod.yearp + 1}-01-01', "%Y-%m-%d")

                #Verify that the date range of the period and the parameters are defined
                if init_semester is  None or end_date_activity is None or parameters_period is None:
                    session.flash = T('Error. Is not defined date range of the report or do not have the required parameters. --- Contact the system administrator.')
                    redirect(URL('teacher', 'index'))
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
                    redirect(URL('teacher','index'))
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
                                            & (db.course_activity.date_start < end_date_activity) & (db.course_activity.id.belongs(activities_grades))).select()
                            for act_tempo in activities_m:
                                if not report.report_restriction.is_final:
                                    temp_end_act = act_tempo.date_finish 
                                    temp_end_act = datetime.datetime(temp_end_act.year, temp_end_act.month, temp_end_act.day)
                                    end_date_activityt1 = datetime.datetime(end_date_activity.year, end_date_activity.month, end_date_activity.day)
                                    if temp_end_act < end_date_activityt1:
                                        grades_log_count = db((db.grades_log.activity_id == act_tempo.id) & (db.grades_log.operation_log == 'insert')
                                                            & (db.grades_log.user_name == report.assignation.assigned_user.username)).count()
                                        grades_count = db(db.grades.activity == act_tempo.id).count()
                                        #Check if you have the minimum of notes recorded in the activity amount that you are worth in the report
                                        if ((grades_log_count * 100) / grades_count) >= int(parameters_period.percentage_income_activity):
                                            activities_m_real.append(metric_statistics(act_tempo, 0, None))
                                    else:
                                        #Future activities with metric
                                        activities_f.append(act_tempo)
                                else:
                                    grades_log_count = db((db.grades_log.activity_id == act_tempo.id) & (db.grades_log.operation_log == 'insert')
                                                        & (db.grades_log.user_name == report.assignation.assigned_user.username)).count()
                                    grades_count = db(db.grades.activity == act_tempo.id).count()
                                    #Check if you have the minimum of notes recorded in the activity amount that you are worth in the report
                                    if ((grades_log_count * 100) / grades_count) >= int(parameters_period.percentage_income_activity):
                                        activities_m_real.append(metric_statistics(act_tempo,0,None))
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
                                            & (db.course_activity.id.belongs(activities_grades))).select()
                            for act_tempo in activities_m:
                                if not report.report_restriction.is_final:
                                    temp_end_act = act_tempo.date_finish 
                                    temp_end_act = datetime.datetime(temp_end_act.year, temp_end_act.month, temp_end_act.day)
                                    end_date_activityt1 = datetime.datetime(end_date_activity.year, end_date_activity.month, end_date_activity.day)
                                    if temp_end_act < end_date_activityt1:
                                        grades_log_count = db((db.grades_log.activity_id == act_tempo.id) & (db.grades_log.operation_log == 'insert')
                                                            & (db.grades_log.user_name == report.assignation.assigned_user.username)).count()
                                        grades_count = db(db.grades.activity == act_tempo.id).count()
                                        #Check if you have the minimum of notes recorded in the activity amount that you are worth in the report
                                        if ((grades_log_count * 100) / grades_count) >= int(parameters_period.percentage_income_activity):
                                            activities_m_real.append(metric_statistics(act_tempo, 0, None))
                                    else:
                                        #Future activities with metric
                                        activities_f.append(act_tempo)
                                else:
                                    grades_log_count = db((db.grades_log.activity_id == act_tempo.id) & (db.grades_log.operation_log == 'insert')
                                                        & (db.grades_log.user_name == report.assignation.assigned_user.username)).count()
                                    grades_count = db(db.grades.activity == act_tempo.id).count()
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
                        frt = db((db.course_first_recovery_test.semester == cperiod.id) & (db.course_first_recovery_test.project == report.assignation.project)).count()
                    except:
                        frt = 0
                    if frt > 0:
                        if activities_m is None:
                            activities_m = []
                        activities_m.append(metric_statistics(report, 1, None))

                    #students_second_recovery
                    try:
                        srt = db((db.course_second_recovery_test.semester == cperiod.id) & (db.course_second_recovery_test.project == report.assignation.project)).count()
                    except:
                        srt = 0
                    if srt > 0:
                        if activities_m is None:
                            activities_m = []
                        activities_m.append(metric_statistics(report, 2, None))

            if activities_m is None: activities_m = []
            if activities_wm is None: activities_wm = []
            if activities_f is None: activities_f = []

            return dict(
                log_types=db(db.log_type.id > 0).select(),
                assignation_reports = assignation_reports,
                logs=db((db.log_entry.report == report.id)).select(),
                parameters=parameters,
                metrics=db((db.log_metrics.report == report.id)).select(),
                final_r=db(db.log_final.report == report.id).select(),
                anomalies=db((db.log_type.name == 'Anomaly') & (db.log_entry.log_type == db.log_type.id)
                        & (db.log_entry.report == report.id)).count(),
                markmin_settings=cpfecys.get_markmin,
                report=report,
                next_date=next_date,
                teacher=teacher,
                activities_m=activities_m,
                activities_wm=activities_wm,
                activities_f=activities_f
            )
        else:
            session.flash = 'El reporte seleccionado no puede visualizarse, seleccione uno valido.'
            redirect(URL('teacher', 'index'))
    elif request.args(0) == 'grade':
        if valid:
            score = request.vars['score']
            comment = request.vars['comment']
            if score is not None:
                score = int(score)
                if request.vars['improve'] is not None:
                    if report.times_graded >= parameters.rescore_max_count and report.status.name != 'EnabledForTeacher':
                        session.flash = 'Este reporte ha excedido la cantidad de mejoras disponibles'
                        redirect(URL('teacher', 'report/view', vars=dict(report=report.id)))

                    if comment is not None:
                        if report.assignation.project.area_level.name == 'DTT Tutor Académico':
                            try:
                                temp_log_type = db(db.log_type.name == 'Activity').select(db.log_type.id).first()
                                db((db.log_entry.report == report.id) & (db.log_entry.log_type == temp_log_type.id)).delete()
                            except:
                                db(db.log_entry.report == report.id).delete()
                            
                            db(db.log_metrics.report == report.id).delete()
                            db(db.log_future.report == report.id).delete()
                            if report.report_restriction.is_final:
                                if db(db.log_final.report == report.id).select(db.log_final.id).first() is None:
                                    #CREATE THE FINAL METRICS
                                    cperiod = obtain_period_report(report)
                                    final_metrics = final_metric(cperiod, report)
                                    try:
                                        average = float((final_metrics[22] * 100) / final_metrics[20])
                                    except:
                                        average = 0.0
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
                                        curso_created=report.created,
                                        report=report.id
                                    )

                        report.update_record(
                            score=score,
                            min_score=cpfecys.get_custom_parameters().min_score,
                            teacher_comment=comment,
                            status=db.report_status(name='Recheck'),
                            score_date=cdate,
                            times_graded=(report.times_graded or 0)+1
                        )
                        session.flash = 'El reporte ha sido enviado para revisión, será notificado por email cuando este proceso haya finalizado.'
                        # Notification Message
                        signature = (cpfecys.get_custom_parameters().email_signature or '')
                        me_the_user = db(db.auth_user.id == auth.user.id).select(db.auth_user.username, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.email).first()
                        row = db(db.user_project.id == report.assignation).select(db.user_project.assigned_user).first()
                        message = f"""
                            <html>
                                El reporte <b>{XML(report.report_restriction['name'])}</b><br/>
                                enviado por el estudiante: {XML(row.assigned_user['username'])} - {XML(row.assigned_user['first_name'])} {XML(row.assigned_user['last_name'])}<br/>
                                con nota: {XML(report.score)} <br/>
                                calificado por: {XML(me_the_user.username)} - {XML(me_the_user.first_name)} {XML(me_the_user.last_name)}<br/>
                                y con comentario: {XML(comment)}<br/>
                                fue revisado, pero se reenvió para ser mejorado<br/>
                                tienes: {db(db.custom_parameters.id > 0).select(db.custom_parameters.rescore_max_days).first().rescore_max_days} dia(s), para mejorar el report<br/>
                                si el reporte no es reenviado en el tiempo estipulado, se tomara la nota actual<br/><br/>
                                Mejora tu reporte en {cpfecys.get_domain()}<br/>
                                {signature}
                            </html>
                        """
                        # send mail to teacher and student notifying change.
                        mails = []
                        # retrieve teacher's email
                        teacher = me_the_user.email
                        mails.append(teacher)
                        # retrieve student's email
                        student_mail = row.assigned_user['email']
                        mails.append(student_mail)
                        was_sent = mail.send(
                                    to=mails,
                                    subject=T('[DTT]Automatic Notification - Report needs improvement.'),
                                    reply_to=teacher,
                                    message=message
                                )
                        #MAILER LOG
                        db.mailer_log.insert(
                            sent_message=message,
                            destination=','.join(mails),
                            result_log=f"{mail.error or ''}:{mail.result}",
                            success=was_sent
                        )
                        redirect(URL('teacher', 'report/view', vars=dict(report=report.id)))
                else:
                    if score >= 0 and score <= 100:
                        report.update_record(
                            score=score,
                            min_score=cpfecys.get_custom_parameters().min_score,
                            teacher_comment=comment,
                            status=db.report_status(name='Acceptance'),
                            score_date=cdate,
                            times_graded=(report.times_graded or 0)+1
                        )
                        session.flash = T('The report has been scored successfully')
                        # Notification Message
                        signature = (cpfecys.get_custom_parameters().email_signature or '')
                        me_the_user = db(db.auth_user.id == auth.user.id).select(db.auth_user.last_name, db.auth_user.first_name, db.auth_user.email, db.auth_user.username).first()
                        row = db(db.user_project.id == report.assignation).select(db.user_project.assigned_user).first()
                        message = f"""
                            <html>
                                El reporte <b>{XML(report.report_restriction['name'])}</b><br/>
                                enviado por el estudiante: {XML(row.assigned_user['username'])} - {XML(row.assigned_user['first_name'])} {XML(row.assigned_user['last_name'])}<br/>
                                con nota: {XML(report.score)}<br/>
                                calificado por: {XML(me_the_user.username)} - {XML(me_the_user.first_name)} {XML(me_the_user.last_name)}<br/>
                                y comentario: {XML(comment)}<br/>
                                fue revisado, no se necesita realizar ninguna acción adicional<br/>
                                DTT-ECYS {cpfecys.get_domain()}<br/>
                                {signature}
                            </html>
                        """
                        # send mail to teacher and student notifying change.
                        mails = []
                        # retrieve teacher's email
                        teacher = me_the_user.email
                        mails.append(teacher)
                        # retrieve student's email
                        student_mail = row.assigned_user['email']
                        mails.append(student_mail)
                        was_sent = mail.send(
                            to=mails,
                            subject=T('[DTT]Automatic Notification - Report Done.'),
                            reply_to=teacher,
                            message=message
                        )
                        #MAILER LOG
                        db.mailer_log.insert(
                            sent_message=message,
                            destination=','.join(mails),
                            result_log=f"{mail.error or ''}:{mail.result}",
                            success=was_sent
                        )
                        redirect(URL('teacher', 'report/view', vars=dict(report=report.id)))

        session.flash = T('Selected report can\'t be viewed. Select a valid report.')
        redirect(URL('teacher', 'index'))

@auth.requires_login()
@auth.requires_membership('Teacher')
def todo_reports():
    my_projects = db((db.user_project.assigned_user == auth.user.id) & (db.project.id == db.user_project.project)).select(db.project.id, distinct=True)
    my_students = db((db.user_project.project.belongs([my_project.id for my_project in my_projects]))).select(db.user_project.project, db.user_project.id)
    temp_reports = []
    for assignation in my_students:
        teacher_var = db((db.user_project.project == assignation.project) & (db.user_project.assigned_user == db.auth_user.id)
                    & (db.auth_membership.user_id == db.auth_user.id) & (db.auth_membership.group_id == db.auth_group.id)
                    & (db.auth_group.role == 'Teacher')).select().last()              
        if teacher_var is not None:                      
            reports = assignation.report((db.report.status == db.report_status.id) & ((db.report_status.name == 'Grading')
                | (db.report_status.name == 'EnabledForTeacher'))).select(db.report.id)
            for report in reports:
                temp_reports.append(report.id)                            

    return dict(my_pending_reports=temp_reports)

def current_year_period():
    #this should be a module's method
    cdate = datetime.now()
    cyear = cdate.year
    cmonth = cdate.month
    period = cpfecys.second_period
    #current period depends if we are in dates between jan-jun and jul-dec
    if cmonth < 7 :
        period = cpfecys.first_period
    return db.period_year((db.period_year.yearp == cyear) & (db.period_year.period == period))

def obtain_period_report(report):
    #Get the minimum and maximum date of the report
    tmp_period = 1
    tmp_year = report.report_restriction.start_date.year
    if report.report_restriction.start_date.month >= 6:
        tmp_period = 2
    return db((db.period_year.yearp == tmp_year) & (db.period_year.period == tmp_period)).select(
                db.period_year.id,
                db.period_year.period,
                db.period_year.yearp
            ).first()

def metric_statistics(act_tempo, recovery, data_incoming):
    activity = []
    if data_incoming is None:
        if recovery == 1 or recovery == 2:
            if recovery == 1:
                #Description of Activity
                description = 'Nombre: "PRIMERA RETRASADA"'
                temp_data = db((db.course_first_recovery_test.semester == obtain_period_report(act_tempo).id) & (db.course_first_recovery_test.project == act_tempo.assignation.project)).select(
                                db.course_first_recovery_test.grade,
                                orderby=db.course_first_recovery_test.grade
                            )
            else:
                #Description of Activity
                description = 'Nombre: "SEGUNDA RETRASADA"'
                temp_data = db((db.course_second_recovery_test.semester == obtain_period_report(act_tempo).id) & (db.course_second_recovery_test.project == act_tempo.assignation.project)).select(
                                db.course_second_recovery_test.grade,
                                orderby=db.course_second_recovery_test.grade
                            )
            data = []
            sum_data = 0.0
            sum_data_squared = float(0)
            total_reprobate = 0
            total_approved = 0
            for d1 in temp_data:
                if d1.grade is None:
                    data.append(0.0)
                    total_reprobate += 1
                else:
                    data.append(float(d1.grade))
                    sum_data += float(d1.grade)
                    sum_data_squared += (float(d1.grade) * float(d1.grade))
                    if float(d1.grade) >= 61.0:
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
            sum_data = 0.0
            sum_data_squared = 0.0
            total_reprobate = 0
            total_approved = 0
            for d1 in temp_data:
                if d1.grade is None:
                    data.append(0.0)
                    total_reprobate += 1
                else:
                    data.append(float(d1.grade))
                    sum_data += float(d1.grade)
                    sum_data_squared += (float(d1.grade) * float(d1.grade))
                    if float(d1.grade) >= 61.0:
                        total_approved += 1
                    else:
                        total_reprobate += 1
    else:
        data = []
        sum_data = 0.0
        sum_data_squared = 0.0
        total_reprobate = 0
        total_approved = 0
        for d1 in data_incoming:
            if d1 is None:
                data.append(0.0)
                total_reprobate += 1
            else:
                data.append(float(d1))
                sum_data += float(d1)
                sum_data_squared += (float(d1) * float(d1))
                if float(d1) >= 61.0:
                    total_approved += 1
                else:
                    total_reprobate += 1

    #Total Students
    total_students = len(data)
    
    #Mean
    mean = float(sum_data / total_students)
    #Variance
    try:
        variance = ((sum_data_squared / total_students) - (mean * mean))
    except:
        variance = 0.0
    #Standard Deviation
    try:
        standard_deviation = math.sqrt(variance)
    except:
        standard_deviation = 0.0
    #Standard Error
    try:
        standard_error = standard_deviation / math.sqrt(total_students)
    except:
        standard_error = 0.0
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
        denominator *= denominator
        #Fraction
        kurtosis = (numerator / denominator) - 3
    except:
        kurtosis = 0.0
    #Minimum
    minimum = float(data[0])
    if total_students == 1:
        #Maximum
        maximum = float(data[0])
        #Rank
        rank = 0.0
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
            max_freq = table[0][1]
            for i in range(1, len(table)):
                if table[i][1] != max_freq:
                    table = table[:i]
                    break
            mode = float(table[0][0])
        except:
            mode = minimum
    #Skewness
    try:
        skewness = float((3 * (mean - median)) / standard_error)
    except:
        skewness = 0.0
    
    #Metric Type
    if data_incoming is None:
        if recovery == 1 or recovery == 2:
            if recovery == 1:
                metric_type = db(db.metrics_type.name == 'PRIMERA RETRASADA').select(db.metrics_type.id).first()[db.metrics_type.id]
            else:
                metric_type = db(db.metrics_type.name == 'SEGUNDA RETRASADA').select(db.metrics_type.id).first()[db.metrics_type.id]
        else:
            category = act_tempo.course_activity_category.category.category.upper()
            metric_type = None
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

    #Fill the activity
    if data_incoming is None:
        if recovery == 1 or recovery == 2:
            activity.append(datetime.datetime.now().date())
        else:
            activity.append(act_tempo.date_start)
        activity.append(description)
    
    activity.append(mean)
    activity.append(standard_error)
    activity.append(median)
    activity.append(mode)
    activity.append(standard_deviation)
    activity.append(variance)
    activity.append(kurtosis)
    activity.append(skewness)
    activity.append(rank)
    activity.append(minimum)
    activity.append(maximum)
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
    #students_minutes
    try:
        final_stats_vec.append(db((db.academic_course_assignation.semester == cperiod.id) & (db.academic_course_assignation.assignation == report.assignation.project)).count())
    except:
        final_stats_vec.append(0)

    #students_partial
    try:
        partials = db(db.activity_category.category == 'Parciales').select(db.activity_category.id).first()
        cat_partials = db((db.course_activity_category.category == partials.id) & (db.course_activity_category.semester == cperiod.id)
                        & (db.course_activity_category.assignation == report.assignation.project) & (db.course_activity_category.laboratory == False)).select(db.course_activity_category.id).first()
        partials = db((db.course_activity.course_activity_category == cat_partials.id) & (db.course_activity.semester == cperiod.id)
                    & (db.course_activity.assignation == report.assignation.project) & (db.course_activity.laboratory == False)).select(db.course_activity.id)
        course_activity_count = db((db.course_activity.course_activity_category == cat_partials.id) & (db.course_activity.semester == cperiod.id)
                                & (db.course_activity.assignation == report.assignation.project) & (db.course_activity.laboratory == False)).count()
        final_stats_vec.append(int(db(db.grades.activity.belongs(partials.id)).count() / course_activity_count))
    except:
        final_stats_vec.append(0)

    #students_final
    try:
        final = db(db.activity_category.category == 'Examen Final').select(db.activity_category.id).first()
        cat_final = db((db.course_activity_category.category == final.id) & (db.course_activity_category.semester == cperiod.id)
                    & (db.course_activity_category.assignation == report.assignation.project) & (db.course_activity_category.laboratory == False)).select(db.course_activity_category.id).first()
        final = db((db.course_activity.course_activity_category == cat_final.id) & (db.course_activity.semester == cperiod.id)
                & (db.course_activity.assignation == report.assignation.project) & (db.course_activity.laboratory == False)).select(db.course_activity.id)
        final_stats_vec.append(db(db.grades.activity.belongs(final.id)).count())
    except:
        final_stats_vec.append(0)

    #students_first_recovery
    try:
        final_stats_vec.append(db((db.course_first_recovery_test.semester == cperiod.id) & (db.course_first_recovery_test.project == report.assignation.project)).count())
    except:
        final_stats_vec.append(0)

    #students_second_recovery
    try:
        final_stats_vec.append(db((db.course_second_recovery_test.semester == cperiod.id) & (db.course_second_recovery_test.project  ==report.assignation.project)).count())
    except:
        final_stats_vec.append(0)

    #Students
    students = db((db.academic_course_assignation.semester == cperiod.id) & (db.academic_course_assignation.assignation == report.assignation.project)).select(
                    db.academic_course_assignation.carnet,
                    db.academic_course_assignation.id
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
                            db.course_activity_category.category,
                            db.course_activity_category.id,
                            db.course_activity_category.grade,
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
                course_activities.append(db((db.course_activity.semester == cperiod.id) & (db.course_activity.assignation == report.assignation.project)
                                        & (db.course_activity.laboratory == False) & (db.course_activity.course_activity_category == category_c.id)).select())
        if cat_course_temp is not None:
            cat_vec_course_temp.append(cat_course_temp)
            course_activities.append(db((db.course_activity.semester == cperiod.id) & (db.course_activity.assignation == report.assignation.project)
                                    & (db.course_activity.laboratory == False) & (db.course_activity.course_activity_category == cat_course_temp.id)).select())
        course_category = cat_vec_course_temp
        total_class = total_w

        total_w = 0.0
        cat_lab_temp = None
        cat_vec_lab_temp = []
        lab_activities = None
        validate_laboratory = None
        lab_category = db((db.course_activity_category.semester == cperiod.id) & (db.course_activity_category.assignation == report.assignation.project)
                        & (db.course_activity_category.laboratory == True)).select(db.course_activity_category.id)
        if lab_category.first() is not None:
            validate_laboratory = db((db.validate_laboratory.semester == cperiod.id) & (db.validate_laboratory.project == report.assignation.project)).select(
                                        db.validate_laboratory.carnet,
                                        db.validate_laboratory.grade
                                    )
            lab_category = db((db.course_activity_category.semester == cperiod.id) & (db.course_activity_category.assignation == report.assignation.project)
                            & (db.course_activity_category.laboratory == True)).select(db.course_activity_category.category, db.course_activity_category.grade, db.course_activity_category.id)
            lab_activities = []
            for category_l in lab_category:
                if category_l.category.category == "Examen Final":
                    total_w += float(category_l.grade)
                    cat_lab_temp = category_l
                else:
                    cat_vec_lab_temp.append(category_l)
                    total_w += float(category_l.grade)
                    lab_activities.append(db((db.course_activity.semester == cperiod.id) & (db.course_activity.assignation == report.assignation.project)
                                        & (db.course_activity.laboratory == True) & (db.course_activity.course_activity_category == category_l.id)).select())
            if cat_lab_temp is not None:
                cat_vec_lab_temp.append(cat_lab_temp)
                lab_activities.append(db((db.course_activity.semester == cperiod.id) & (db.course_activity.assignation == report.assignation.project)
                                    & (db.course_activity.laboratory == True) & (db.course_activity.course_activity_category == cat_lab_temp.id)).select())
            lab_category = cat_vec_lab_temp
            total_final_lab = total_w

        requirement = db((db.course_requirement.semester == cperiod.id) & (db.course_requirement.project == report.assignation.project)).select().first()
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
                    for category_lab in lab_category:
                        total_category_lab = 0.0
                        total_activities_lab = 0
                        for c_lab in lab_activities[pos_vcc_lab]:
                            student_grade = db((db.grades.activity == c_lab.id) & (db.grades.academic_assignation == t1.id)).select(db.grades.grade).first()
                            if not (student_grade is None or student_grade.grade is None):
                                if category_lab.specific_grade:
                                    total_category_lab += float((student_grade.grade * c_lab.grade) / 100)
                                else:
                                    total_category_lab += float(student_grade.grade)
                            total_activities_lab += 1

                        if not category_lab.specific_grade:
                            if total_activities_lab == 0:
                                total_activities_lab = 1
                            total_activities_lab *= 100
                            total_category_lab = float((total_category_lab * float(category_lab.grade)) / float(total_activities_lab))
                        total_carry_lab += total_category_lab
                        pos_vcc_lab += 1
                    temp_data.append(t1.carnet.carnet)
                    temp_data.append(int(round(total_carry_lab, 0)))
                    students_in_lab.append(temp_data)
                    temp_students_in_lab.append(temp_data)
                    sum_laboratory_grades += int(round(total_carry_lab, 0))
                    if int(round(total_carry_lab, 0)) < 61:
                        reprobate += 1
                    else:
                        approved += 1

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
        count_fail = int(len(final_stats_vec))
        for count_fail in range(9):
            final_stats_vec.append(0)

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
                    if category.category.category != "Laboratorio" and category.category.category  !="Examen Final":
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
                            total_category = float((total_category * float(category.grade)) / float(total_activities))
                        total_carry += total_category
                        pos_vcc += 1
                    elif category.category.category == "Examen Final":
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
                            total_category = float((total_category * float(category.grade)) / float(total_activities))
                        total_category = int(round(total_category, 0))
                        total_carry += total_category
                        pos_vcc += 1
                #Make
                if exist_lab:
                    total_category = float((int(students_in_lab[pos_student][1]) * total_lab) / 100)
                    total_carry += total_category

                if requirement is not None:
                    if db((db.course_requirement_student.carnet == t1.carnet) & (db.course_requirement_student.requirement == requirement.id)).select(db.course_requirement_student.id).first() is not None:
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
            count_fail_final = len(final_stats_vec)
            for count_fail_final in range(23):
                final_stats_vec.append(0)
    except:
        count_fail_final = len(final_stats_vec)
        for count_fail_final in range(23):
                final_stats_vec.append(0)

    return final_stats_vec

@cache.action()
@auth.requires_login()
@auth.requires_membership('Teacher')
def download():
    item = db(db.item.uploaded_file==request.args[0]).select(db.item.assignation).first()
    project = item.assignation.project
    t_assignation = db((db.user_project.project == project.id)&  (db.user_project.assigned_user==auth.user.id))
    if item is not None and t_assignation is not None:
        return response.download(request, db)
    else:
        session.flash = T('Access Forbidden')
        redirect(URL('default', 'index'))
