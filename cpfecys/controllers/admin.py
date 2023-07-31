#***********************************************************************************************************************
#******************************************************PHASE 2 DTT******************************************************
from calendar import c
from shutil import ExecError
from wsgiref import validate

# *********** Inicio - Prácticas Finales (Digital Signature) - Fernando Reyes *************
import ds_utils
# *********** Fin - Prácticas Finales (Digital Signature) - Fernando Reyes *************

import math
import time # correccion Rome
from datetime import datetime, timedelta, date
import queries
import dsa_utils
import re
import cpfecys
import csv
import os
import gluon.contenttype as c
import dsa_utils_temp
import base64
import zipfile
import chardet
import io
from gluon.contenttype import contenttype

def obtain_period_report(report):
    #Get the minimum and maximum date of the report
    tmp_period=1
    tmp_year=report.report_restriction.start_date.year
    if report.report_restriction.start_date.month >= 6:
        tmp_period=2
    return db((db.period_year.yearp==tmp_year)&(db.period_year.period==tmp_period)).select().first()

def metric_statistics(act_tempo, recovery, data_incoming):
    activity=[]
    if data_incoming is None:
        if recovery==1 or recovery==2:
            if recovery==1:
                #Description of Activity
                description = 'Nombre: "PRIMERA RETRASADA"'
                temp_data = db((db.course_first_recovery_test.semester==obtain_period_report(act_tempo).id)&(db.course_first_recovery_test.project==act_tempo.assignation.project)).select(db.course_first_recovery_test.grade, orderby=db.course_first_recovery_test.grade)
            else:
                #Description of Activity
                description = 'Nombre: "SEGUNDA RETRASADA"'
                temp_data = db((db.course_second_recovery_test.semester==obtain_period_report(act_tempo).id)&(db.course_second_recovery_test.project==act_tempo.assignation.project)).select(db.course_second_recovery_test.grade, orderby=db.course_second_recovery_test.grade)
            data=[]
            sum_data=float(0)
            sum_data_squared=float(0)
            total_reprobate=0
            total_approved=0
            for d1 in temp_data:
                if d1.grade is None:
                    data.append(float(0))
                    total_reprobate+=1
                else:
                    data.append(float(d1.grade))
                    sum_data+=float(d1.grade)
                    sum_data_squared+=(float(d1.grade)*float(d1.grade))
                    if float(d1.grade)>=float(61):
                        total_approved+=1
                    else:
                        total_reprobate+=1
        else:
            #Description of Activity
            description = 'Nombre: "'+act_tempo.name+'" Descripción: "'+act_tempo.description+'"'

            #*********************************************Statistics Activity*********************************************
            #Get the data
            temp_data = db(db.grades.activity == act_tempo.id).select(db.grades.grade, orderby=db.grades.grade)
            #temp_data=[40,60,75,75,75,75,80,80,85,85,85,85,85,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100]
            data=[]
            sum_data=float(0)
            sum_data_squared=float(0)
            total_reprobate=0
            total_approved=0
            for d1 in temp_data:
                if d1.grade is None:
                    data.append(float(0))
                    total_reprobate+=1
                else:
                    data.append(float(d1.grade))
                    sum_data+=float(d1.grade)
                    sum_data_squared+=(float(d1.grade)*float(d1.grade))
                    if float(d1.grade)>=float(61):
                        total_approved+=1
                    else:
                        total_reprobate+=1
    else:
        data=[]
        sum_data=float(0)
        sum_data_squared=float(0)
        total_reprobate=0
        total_approved=0
        for d1 in data_incoming:
            if d1 is None:
                data.append(float(0))
                total_reprobate+=1
            else:
                data.append(float(d1))
                sum_data+=float(d1)
                sum_data_squared+=(float(d1)*float(d1))
                if float(d1)>=float(61):
                    total_approved+=1
                else:
                    total_reprobate+=1



    #*********************************************
    #Total Students
    total_students = int(len(data))



    #*********************************************
    #Mean
    mean = float(sum_data/total_students)
    #Variance
    try:
        variance=((sum_data_squared/total_students)-(mean*mean))
    except:
        variance=float(0)
    #Standard Deviation
    try:
        standard_deviation=math.sqrt(variance)
    except:
        standard_deviation=float(0)
    #Standard Error
    try:
        standard_error=standard_deviation/math.sqrt(total_students)
    except:
        standard_error=float(0)
    #Kurtosis
    try:
        #Numerator
        numerator=0
        for i in data:
            numerator+=(i-mean)*(i-mean)*(i-mean)*(i-mean)
        numerator=numerator*total_students
        #Denominator
        denominator=0
        for i in data:
            denominator+=(i-mean)*(i-mean)
        denominator=denominator*denominator
        #Fraction
        kurtosis=(numerator/denominator)-3
    except:
        kurtosis=float(0)
    #Minimum
    minimum=float(data[0])
    if total_students==1:
        #Maximum
        maximum=float(data[0])
        #Rank
        rank=float(0)
        #Median
        median=float(sum_data)
        #Mode
        mode=float(sum_data)
    else:
        #Maximum
        maximum=float(data[total_students-1])
        #Rank
        rank=float(data[total_students-1] - data[0])
        #Median
        if total_students%2 == 1:
            median = float(data[total_students//2])
        else:
            i = total_students//2
            median = float((data[i - 1] + data[i])/2)
        #Mode
        try:
            table = collections.Counter(iter(data)).most_common()
            maxfreq = table[0][1]
            for i in range(1, len(table)):
                if table[i][1] != maxfreq:
                    table = table[:i]
                    break
            mode=float(table[0][0])
        except:
            mode=minimum
    #Skewness
    try:
        skewness=float((3*(mean-median))/standard_error)
    except:
        skewness=float(0)



    #**********************************************
    #Metric Type
    if data_incoming is None:
        if recovery==1 or recovery==2:
            if recovery==1:
                metric_type=db(db.metrics_type.name=='PRIMERA RETRASADA').select(db.metrics_type.id).first()[db.metrics_type.id]
            else:
                metric_type=db(db.metrics_type.name=='SEGUNDA RETRASADA').select(db.metrics_type.id).first()[db.metrics_type.id]
        else:
            category = act_tempo.course_activity_category.category.category.upper()
            metric_type=None
            if category=='TAREAS':
                metric_type=db(db.metrics_type.name=='TAREA').select(db.metrics_type.id).first()[db.metrics_type.id]
            elif category=='EXAMEN CORTO':
                metric_type=db(db.metrics_type.name=='EXAMEN CORTO').select(db.metrics_type.id).first()[db.metrics_type.id]
            elif category=='HOJAS DE TRABAJO':
                metric_type=db(db.metrics_type.name=='HOJA DE TRABAJO').select(db.metrics_type.id).first()[db.metrics_type.id]
            elif category=='PARCIALES':
                metric_type=db(db.metrics_type.name==act_tempo.name.upper()).select(db.metrics_type.id).first()[db.metrics_type.id]
            elif category=='EXAMEN FINAL':
                metric_type=db(db.metrics_type.name=='EXAMEN FINAL').select(db.metrics_type.id).first()[db.metrics_type.id]
            elif category=='PRACTICAS':
                metric_type=db(db.metrics_type.name=='PRACTICA').select(db.metrics_type.id).first()[db.metrics_type.id]
            elif category=='PROYECTOS':
                name_search = act_tempo.name.upper()
                if "FASE FINAL" in name_search:
                    metric_type=db(db.metrics_type.name=='FASE FINAL').select(db.metrics_type.id).first()[db.metrics_type.id]
                elif "FASE" in name_search:
                    metric_type=db(db.metrics_type.name=='FASE DE PROYECTO').select(db.metrics_type.id).first()[db.metrics_type.id]
                elif "PRIMER PROYECTO" in name_search or "1ER PROYECTO" in name_search  or "1ER. PROYECTO" in name_search or "PROYECTO1" in name_search or "PROYECTO 1" in name_search or "PROYECTO NO.1" in name_search or "PROYECTO NO1" in name_search   or "PROYECTO NUMERO 1" in name_search or "PROYECTO NUMERO1" in name_search or "PROYECTO #1" in name_search or "PROYECTO#1" in name_search:
                    metric_type=db(db.metrics_type.name=='PROYECTO 1').select(db.metrics_type.id).first()[db.metrics_type.id]
                elif "SEGUNDO PROYECTO" in name_search or "1DO PROYECTO" in name_search  or "2DO. PROYECTO" in name_search or "PROYECTO2" in name_search or "PROYECTO 2" in name_search or "PROYECTO NO.2" in name_search or "PROYECTO NO2" in name_search   or "PROYECTO NUMERO 2" in name_search or "PROYECTO NUMERO2" in name_search or "PROYECTO #2" in name_search or "PROYECTO#2" in name_search:
                    metric_type=db(db.metrics_type.name=='PROYECTO 2').select(db.metrics_type.id).first()[db.metrics_type.id]
            if metric_type is None:
                metric_type=db(db.metrics_type.name=='OTRA ACTIVIDAD').select(db.metrics_type.id).first()[db.metrics_type.id]



    #******************************************************
    #Fill the activity
    if data_incoming is None:
        if recovery==1 or recovery==2:
            activity.append(datetime.now().date())
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
        if recovery==1:
            activity.append(-1)
        elif recovery==2:
            activity.append(-2)
        else:
            activity.append(act_tempo.id)

    #Activity to return
    return activity

def activities_report_tutor(report):
    activities_wm=None
    activities_m=None
    activities_f=None
    if report.assignation.project.area_level.name=='DTT Tutor Académico' and (report.status.name=='Draft' or report.status.name=='Recheck'):
        #Get the minimum and maximum date of the report
        cperiod = obtain_period_report(report)
        parameters_period = db(db.student_control_period.period_name==(T(cperiod.period.name)+' '+str(cperiod.yearp))).select().first()
        end_date_activity=None
        init_semester=None
        if cperiod.period == 1:
            init_semester = datetime.strptime(str(cperiod.yearp) + '-' + '01-01', "%Y-%m-%d")
            if report.report_restriction.is_final==False:
                activities_f=[]
                name_report_split = report.report_restriction.name.upper()
                name_report_split = name_report_split.split(' ')
                for word in name_report_split:
                    if word=='ENERO':
                        end_date_activity = datetime.strptime(str(cperiod.yearp) + '-' + '02-01', "%Y-%m-%d")
                    elif word=='FEBRERO':
                        end_date_activity = datetime.strptime(str(cperiod.yearp) + '-' + '03-01', "%Y-%m-%d")
                    elif word=='MARZO':
                        end_date_activity = datetime.strptime(str(cperiod.yearp) + '-' + '04-01', "%Y-%m-%d")
                    elif word=='ABRIL':
                        end_date_activity = datetime.strptime(str(cperiod.yearp) + '-' + '05-01', "%Y-%m-%d")
                    elif word=='MAYO':
                        end_date_activity = datetime.strptime(str(cperiod.yearp) + '-' + '06-01', "%Y-%m-%d")
            else:
                end_date_activity = datetime.strptime(str(cperiod.yearp) + '-' + '06-01', "%Y-%m-%d")
        else:
            init_semester = datetime.strptime(str(cperiod.yearp) + '-' + '06-01', "%Y-%m-%d")
            if report.report_restriction.is_final==False:
                activities_f=[]
                name_report_split = report.report_restriction.name.upper()
                name_report_split = name_report_split.split(' ')
                for word in name_report_split:
                    if word=='JUNIO':
                        end_date_activity = datetime.strptime(str(cperiod.yearp) + '-' + '07-01', "%Y-%m-%d")
                    elif word=='JULIO':
                        end_date_activity = datetime.strptime(str(cperiod.yearp) + '-' + '08-01', "%Y-%m-%d")
                    elif word=='AGOSTO':
                        end_date_activity = datetime.strptime(str(cperiod.yearp) + '-' + '09-01', "%Y-%m-%d")
                    elif word=='SEPTIEMBRE':
                        end_date_activity = datetime.strptime(str(cperiod.yearp) + '-' + '10-01', "%Y-%m-%d")
                    elif word=='OCTUBRE':
                        end_date_activity = datetime.strptime(str(cperiod.yearp) + '-' + '11-01', "%Y-%m-%d")
                    elif word=='NOVIEMBRE':
                        end_date_activity = datetime.strptime(str(cperiod.yearp) + '-' + '12-01', "%Y-%m-%d")
                    elif word=='DICIEMBRE':
                        end_date_activity = datetime.strptime(str(cperiod.yearp+1) + '-' + '01-01', "%Y-%m-%d")
            else:
                end_date_activity = datetime.strptime(str(cperiod.yearp+1) + '-' + '01-01', "%Y-%m-%d")

        #Get the latest reports and are of this semester
        before_reports_restriction = db((db.report_restriction.id<report.report_restriction)&(db.report_restriction.start_date>=init_semester)).select(db.report_restriction.id)
        if before_reports_restriction.first() is None:
            before_reports=[]
            before_reports.append(-1)
        else:
            before_reports = db((db.report.assignation==report.assignation)&(db.report.report_restriction.belongs(before_reports_restriction))).select(db.report.id)
            if before_reports.first() is None:
                before_reports=[]
                before_reports.append(-1)

        #Check the id of the log type thtat is activity
        temp_log_type = db(db.log_type.name=='Activity').select().first()

        #*******************Activities to record activities unless already recorded in previous reports
        #Activities without metric
        activities_wm_before = db((db.log_entry.log_type==temp_log_type)&(db.log_entry.period==cperiod.id)&(db.log_entry.tActivity==False)&(db.log_entry.report.belongs(before_reports))).select(db.log_entry.idActivity.with_alias('id'))
        if activities_wm_before.first() is None:
            activities_wm = db((db.course_activity_without_metric.semester == cperiod.id)&(db.course_activity_without_metric.assignation == report.assignation.project)&(db.course_activity_without_metric.date_start < end_date_activity)).select()
            #Future activities without metric
            if report.report_restriction.is_final==False:
                activities_f_temp = db((db.course_activity_without_metric.semester == cperiod.id)&(db.course_activity_without_metric.assignation == report.assignation.project)&(db.course_activity_without_metric.date_start >= end_date_activity)).select()
                for awmt in activities_f_temp:
                    activities_f.append(awmt)
        else:
            activities_wm = db((db.course_activity_without_metric.semester == cperiod.id)&(db.course_activity_without_metric.assignation == report.assignation.project)&(~db.course_activity_without_metric.id.belongs(activities_wm_before))&(db.course_activity_without_metric.date_start < end_date_activity)).select()
            #Future activities without metric
            if report.report_restriction.is_final==False:
                activities_f_temp = db((db.course_activity_without_metric.semester == cperiod.id)&(db.course_activity_without_metric.assignation == report.assignation.project)&(~db.course_activity_without_metric.id.belongs(activities_wm_before))&(db.course_activity_without_metric.date_start >= end_date_activity)).select()
                for awmt in activities_f_temp:
                    activities_f.append(awmt)

        #Activities with metric
        activities_m_before = db((db.log_entry.log_type==temp_log_type)&(db.log_entry.period==cperiod.id)&(db.log_entry.tActivity==True)&(db.log_entry.report.belongs(before_reports))).select(db.log_entry.idActivity.with_alias('id'))
        activities_grades = db((db.grades.academic_assignation==db.academic_course_assignation.id)&(db.academic_course_assignation.semester==cperiod.id)&(db.academic_course_assignation.assignation==report.assignation.project)).select(db.grades.activity.with_alias('id'), distinct=True)
        # cambio rome ## activities_grades = db(db.grades).select(db.grades.activity.with_alias('id'), distinct=True)
        if activities_grades.first() is not None:
            activities_m_real=[]
            if activities_m_before.first() is None:
                #Complete with measuring activities
                activities_m = db((db.course_activity.semester == cperiod.id)&(db.course_activity.assignation == report.assignation.project)&(db.course_activity.date_start < end_date_activity)&(db.course_activity.id.belongs(activities_grades))).select()
                for act_tempo in activities_m:
                    if report.report_restriction.is_final==False:
                        #temp_end_act = act_tempo.date_finish + datetime.timedelta(days=parameters_period.timeout_income_notes)
                        temp_end_act = act_tempo.date_finish
                        temp_end_act = datetime(temp_end_act.year, temp_end_act.month, temp_end_act.day)
                        end_date_activityt1 = datetime(end_date_activity.year, end_date_activity.month, end_date_activity.day)
                        if temp_end_act<end_date_activityt1:
                            #Check if you have the minimum of notes recorded in the activity amount that you are worth in the report
                            if (((int(db((db.grades_log.activity_id == act_tempo.id)&(db.grades_log.operation_log=='insert')&(db.grades_log.user_name==report.assignation.assigned_user.username)).count())*100)/int(db(db.grades.activity == act_tempo.id).count()))>=int(parameters_period.percentage_income_activity)):
                                activities_m_real.append(metric_statistics(act_tempo,0,None))
                        else:
                            #Future activities with metric
                            activities_f.append(act_tempo)
                    else:
                        #Check if you have the minimum of notes recorded in the activity amount that you are worth in the report
                        if (((int(db((db.grades_log.activity_id == act_tempo.id)&(db.grades_log.operation_log=='insert')&(db.grades_log.user_name==report.assignation.assigned_user.username)).count())*100)/int(db(db.grades.activity == act_tempo.id).count()))>=int(parameters_period.percentage_income_activity)):
                            activities_m_real.append(metric_statistics(act_tempo,0,None))
                activities_m = activities_m_real
                #Complete with measuring future activities
                if report.report_restriction.is_final==False:
                    activities_f_temp = db((db.course_activity.semester == cperiod.id)&(db.course_activity.assignation == report.assignation.project)&(db.course_activity.date_start >= end_date_activity)).select()
                    for awmt in activities_f_temp:
                        activities_f.append(awmt)
            else:
                #Complete with measuring activities
                activities_m = db((db.course_activity.semester == cperiod.id)&(db.course_activity.assignation == report.assignation.project)&(db.course_activity.date_start < end_date_activity)&(~db.course_activity.id.belongs(activities_m_before))&(db.course_activity.id.belongs(activities_grades))).select()
                for act_tempo in activities_m:
                    if report.report_restriction.is_final==False:
                        #temp_end_act = act_tempo.date_finish + datetime.timedelta(days=parameters_period.timeout_income_notes)
                        temp_end_act = act_tempo.date_finish
                        temp_end_act = datetime(temp_end_act.year, temp_end_act.month, temp_end_act.day)
                        end_date_activityt1 = datetime(end_date_activity.year, end_date_activity.month, end_date_activity.day)
                        if temp_end_act<end_date_activityt1:
                            #Check if you have the minimum of notes recorded in the activity amount that you are worth in the report
                            if (((int(db((db.grades_log.activity_id == act_tempo.id)&(db.grades_log.operation_log=='insert')&(db.grades_log.user_name==report.assignation.assigned_user.username)).count())*100)/int(db(db.grades.activity == act_tempo.id).count()))>=int(parameters_period.percentage_income_activity)):
                                activities_m_real.append(metric_statistics(act_tempo,0,None))
                        else:
                            #Future activities with metric
                            activities_f.append(act_tempo)
                    else:
                        #Check if you have the minimum of notes recorded in the activity amount that you are worth in the report
                        if (((int(db((db.grades_log.activity_id == act_tempo.id)&(db.grades_log.operation_log=='insert')&(db.grades_log.user_name==report.assignation.assigned_user.username)).count())*100)/int(db(db.grades.activity == act_tempo.id).count()))>=int(parameters_period.percentage_income_activity)):
                            activities_m_real.append(metric_statistics(act_tempo,0,None))
                activities_m = activities_m_real
                #Complete with measuring future activities
                if report.report_restriction.is_final==False:
                    activities_f_temp = db((db.course_activity.semester == cperiod.id)&(db.course_activity.assignation == report.assignation.project)&(db.course_activity.date_start >= end_date_activity)&(~db.course_activity.id.belongs(activities_m_before))).select()
                    for awmt in activities_f_temp:
                        activities_f.append(awmt)


        #RECOVERY 1 y 2
        if report.report_restriction.is_final==True:
            #students_first_recovery
            try:
                frt = int(db((db.course_first_recovery_test.semester==cperiod.id)&(db.course_first_recovery_test.project==report.assignation.project)).count())
            except:
                frt = int(0)
            if frt>0:
                if activities_m_real is None:
                    activities_m_real=[]
                activities_m_real.append(metric_statistics(report,1,None))


            #students_second_recovery
            try:
                srt = int(db((db.course_second_recovery_test.semester==cperiod.id)&(db.course_second_recovery_test.project==report.assignation.project)).count())
            except:
                srt = int(0)
            if srt>0:
                if activities_m_real is None:
                    activities_m_real=[]
                activities_m_real.append(metric_statistics(report,2,None))

    if activities_m is None:
        activities_m=[]
    if activities_wm is None:
        activities_wm=[]
    if activities_f is None:
        activities_f=[]
    return dict(activities_f=activities_f, activities_wm=activities_wm, activities_m=activities_m)

def final_metric(cperiod, report):
    final_stats_vec=[]

    #***********************************************************************************************
    #********************************Attendance and dropout in exams********************************
    #students_minutes
    try:
        final_stats_vec.append(int(db((db.academic_course_assignation.semester==cperiod.id)&(db.academic_course_assignation.assignation==report.assignation.project)).count()))
    except:
        final_stats_vec.append(int(0))

    #students_partial
    try:
        partials = db(db.activity_category.category=='Parciales').select().first()
        cat_partials = db((db.course_activity_category.category==partials.id)&(db.course_activity_category.semester==cperiod.id)&(db.course_activity_category.assignation==report.assignation.project)&(db.course_activity_category.laboratory==False)).select().first()
        partials = db((db.course_activity.course_activity_category==cat_partials.id)&(db.course_activity.semester==cperiod.id)&(db.course_activity.assignation==report.assignation.project)&(db.course_activity.laboratory==False)).select(db.course_activity.id)
        final_stats_vec.append(int(db(db.grades.activity.belongs(partials)).count()/db((db.course_activity.course_activity_category==cat_partials.id)&(db.course_activity.semester==cperiod.id)&(db.course_activity.assignation==report.assignation.project)&(db.course_activity.laboratory==False)).count()))
    except:
        final_stats_vec.append(int(0))

    #students_final
    try:
        final = db(db.activity_category.category=='Examen Final').select().first()
        cat_final = db((db.course_activity_category.category==final.id)&(db.course_activity_category.semester==cperiod.id)&(db.course_activity_category.assignation==report.assignation.project)&(db.course_activity_category.laboratory==False)).select().first()
        final = db((db.course_activity.course_activity_category==cat_final.id)&(db.course_activity.semester==cperiod.id)&(db.course_activity.assignation==report.assignation.project)&(db.course_activity.laboratory==False)).select(db.course_activity.id)
        final_stats_vec.append(int(db(db.grades.activity.belongs(final)).count()))
    except:
        final_stats_vec.append(int(0))

    #students_first_recovery
    try:
        final_stats_vec.append(int(db((db.course_first_recovery_test.semester==cperiod.id)&(db.course_first_recovery_test.project==report.assignation.project)).count()))
    except:
        final_stats_vec.append(int(0))

    #students_second_recovery
    try:
        final_stats_vec.append(int(db((db.course_second_recovery_test.semester==cperiod.id)&(db.course_second_recovery_test.project==report.assignation.project)).count()))
    except:
        final_stats_vec.append(int(0))


    #Students
    students = db((db.academic_course_assignation.semester == cperiod.id) & (db.academic_course_assignation.assignation==report.assignation.project)).select()


    #***********************************************************************************************
    #********************************FINAL RESULTS OF LABORATORY************************************
    #students_in_lab
    exist_lab=False
    total_class=float(0)
    total_lab=float(0)
    total_final_lab=float(0)
    total_w=float(0)
    try:
        course_category = db((db.course_activity_category.semester==cperiod.id)&(db.course_activity_category.assignation==report.assignation.project)&(db.course_activity_category.laboratory==False)).select()
        cat_course_temp=None
        cat_vec_course_temp=[]
        course_activities = []
        for category_c in course_category:
            total_w=total_w+float(category_c.grade)
            if category_c.category.category=="Laboratorio":
                exist_lab=True
                total_lab=float(category_c.grade)
                cat_vec_course_temp.append(category_c)
            elif category_c.category.category=="Examen Final":
                var_final_grade = category_c.grade
                cat_course_temp=category_c
            else:
                cat_vec_course_temp.append(category_c)
                course_activities.append(db((db.course_activity.semester==cperiod.id)&(db.course_activity.assignation==report.assignation.project)&(db.course_activity.laboratory==False)&(db.course_activity.course_activity_category==category_c.id)).select())
        if cat_course_temp != None:
            cat_vec_course_temp.append(cat_course_temp)
            course_activities.append(db((db.course_activity.semester==cperiod.id)&(db.course_activity.assignation==report.assignation.project)&(db.course_activity.laboratory==False)&(db.course_activity.course_activity_category==cat_course_temp.id)).select())
        course_category=cat_vec_course_temp
        total_class=total_w


        total_w=float(0)
        lab_category=None
        cat_lab_temp=None
        cat_vec_lab_temp=[]
        lab_activities = None
        validate_laboratory=None
        lab_category = db((db.course_activity_category.semester==cperiod.id)&(db.course_activity_category.assignation==report.assignation.project)&(db.course_activity_category.laboratory==True)).select()
        if lab_category.first() is not None:
            validate_laboratory = db((db.validate_laboratory.semester==cperiod.id)&(db.validate_laboratory.project==report.assignation.project)).select()
            lab_category = db((db.course_activity_category.semester==cperiod.id)&(db.course_activity_category.assignation==report.assignation.project)&(db.course_activity_category.laboratory==True)).select()
            lab_activities = []
            for category_l in lab_category:
                if category_l.category.category=="Examen Final":
                    total_w=total_w+float(category_l.grade)
                    cat_lab_temp=category_l
                else:
                    cat_vec_lab_temp.append(category_l)
                    total_w=total_w+float(category_l.grade)
                    lab_activities.append(db((db.course_activity.semester==cperiod.id)&(db.course_activity.assignation==report.assignation.project)&(db.course_activity.laboratory==True)&(db.course_activity.course_activity_category==category_l.id)).select())
            if cat_lab_temp != None:
                cat_vec_lab_temp.append(cat_lab_temp)
                lab_activities.append(db((db.course_activity.semester==cperiod.id)&(db.course_activity.assignation==report.assignation.project)&(db.course_activity.laboratory==True)&(db.course_activity.course_activity_category==cat_lab_temp.id)).select())
            lab_category=cat_vec_lab_temp
            total_final_lab=total_w


        requirement = db((db.course_requirement.semester==cperiod.id)&(db.course_requirement.project==report.assignation.project)).select().first()
    except:
        total_class=float(0)
        total_final_lab=float(0)

    #COMPUTING LABORATORY NOTES
    students_in_lab=[]
    temp_students_in_lab=[]
    approved=0
    reprobate=0
    sum_laboratory_grades=0
    try:
        if total_final_lab==float(100):
            for t1 in students:
                temp_data=[]
                total_category=float(0)
                is_validate=False
                #<!--Revalidation of laboratory-->
                for validate in validate_laboratory:
                    if validate.carnet==t1.carnet:
                        is_validate=True
                        temp_data.append(t1.carnet.carnet)
                        temp_data.append(int(round(validate.grade,0)))
                        students_in_lab.append(temp_data)


                #<!--Doesnt has a revalidation-->
                if is_validate==False:
                    #<!--Position in the vector of activities-->
                    pos_vcc_lab=0
                    #<!--Vars to the control of grade of the student-->
                    total_category_lab=float(0)
                    total_activities_lab=0
                    total_carry_lab=float(0)

                    #<!--****************************************FILL THE GRADES OF THE STUDENT****************************************-->
                    #<!--LAB ACTIVITIES-->
                    for category_Lab in lab_category:
                        total_category_lab=float(0)
                        total_activities_lab=0
                        for c_Lab in lab_activities[pos_vcc_lab]:
                            student_grade = db((db.grades.activity==c_Lab.id)&(db.grades.academic_assignation==t1.id)).select().first()
                            if student_grade is None or student_grade.grade is None:
                                total_category_lab=total_category_lab+float(0)
                            else:
                                if category_Lab.specific_grade==True:
                                    total_category_lab=total_category_lab+float((student_grade.grade*c_Lab.grade)/100)
                                else:
                                    total_category_lab=total_category_lab+float(student_grade.grade)
                            total_activities_lab=total_activities_lab+1


                        if category_Lab.specific_grade==False:
                            if total_activities_lab==0:
                                total_activities_lab=1
                            total_activities_lab=total_activities_lab*100
                            total_category_lab=float((total_category_lab*float(category_Lab.grade))/float(total_activities_lab))
                        total_carry_lab=total_carry_lab+total_category_lab
                        pos_vcc_lab=pos_vcc_lab+1
                    temp_data.append(t1.carnet.carnet)
                    temp_data.append(int(round(total_carry_lab,0)))
                    students_in_lab.append(temp_data)
                    temp_students_in_lab.append(temp_data)
                    sum_laboratory_grades+=int(round(total_carry_lab,0))
                    if int(round(total_carry_lab,0))<61:
                        reprobate+=1
                    else:
                        approved+=1

            #APPROVED
            final_stats_vec.append(approved)
            #FAILED
            final_stats_vec.append(reprobate)
            #MEAN
            final_stats_vec.append(float(sum_laboratory_grades)/float(len(temp_students_in_lab)))
            #AVERAGE
            final_stats_vec.append(float((float(approved)/float(len(temp_students_in_lab)))*float(100)))
        else:
            #APPROVED
            final_stats_vec.append(int(0))
            #FAILED
            final_stats_vec.append(int(0))
            #MEAN
            final_stats_vec.append(int(0))
            #AVERAGE
            final_stats_vec.append(int(0))
    except:
        count_fail=int(len(final_stats_vec))
        for count_fail in range(9):
            final_stats_vec.append(int(0))


    #Class Final Results
    data_final_class=[]
    try:
        if total_class==100:
            for t1 in students:
                pos_student=0
                pos_vcc=0
                total_category=float(0)
                total_activities=0
                total_carry=float(0)
                for category in course_category:
                    if category.category.category!="Laboratorio" and category.category.category!="Examen Final":
                        total_category=float(0)
                        total_activities=0
                        for c in course_activities[pos_vcc]:
                            student_grade = db((db.grades.activity==c.id)&(db.grades.academic_assignation==t1.id)).select().first()
                            if student_grade is None or student_grade.grade is None:
                                total_category=total_category+float(0)
                            else:
                                if category.specific_grade==True:
                                    total_category=total_category+float((student_grade.grade*c.grade)/100)
                                else:
                                    total_category=total_category+float(student_grade.grade)
                            total_activities=total_activities+1

                        if category.specific_grade==True:
                            None
                        else:
                            if total_activities==0:
                                total_activities=1
                            total_activities=total_activities*100
                            total_category=float((total_category*float(category.grade))/float(total_activities))
                        total_carry=total_carry+total_category
                        pos_vcc=pos_vcc+1
                    elif category.category.category=="Examen Final":
                        total_carry=int(round(total_carry,0))
                        total_category=float(0)
                        total_activities=0
                        for c in course_activities[pos_vcc]:
                            student_grade = db((db.grades.activity==c.id)&(db.grades.academic_assignation==t1.id)).select().first()
                            if student_grade is None or student_grade.grade is None:
                                total_category=total_category+float(0)
                            else:
                                if category.specific_grade==True:
                                    total_category=total_category+float((student_grade.grade*c.grade)/100)
                                else:
                                    total_category=total_category+float(student_grade.grade)
                            total_activities=total_activities+1

                        if category.specific_grade==True:
                            None
                        else:
                            if total_activities==0:
                                total_activities=1
                            total_activities=total_activities*100
                            total_category=float((total_category*float(category.grade))/float(total_activities))
                        total_category=int(round(total_category,0))
                        total_carry=total_carry+total_category
                        pos_vcc=pos_vcc+1

                #Make
                if exist_lab==True:
                    total_category=float((int(students_in_lab[pos_student][1])*total_lab)/100)
                    total_carry=total_carry+total_category

                if requirement is not None:
                    if db((db.course_requirement_student.carnet==t1.carnet)&(db.course_requirement_student.requirement==requirement.id)).select().first() is not None:
                        data_final_class.append(int(round(total_carry,0)))
                    else:
                        data_final_class.append(int(0))
                else:
                    data_final_class.append(int(round(total_carry,0)))
                pos_student+=1

            #Calculate metric_statistics
            data_final_class=sorted(data_final_class)
            data_final_class = metric_statistics(None, 0, data_final_class)
            for pos_final in data_final_class:
                final_stats_vec.append(pos_final)
        else:
            count_fail_final=int(len(final_stats_vec))
            for count_fail_final in range(23):
                final_stats_vec.append(int(0))
    except:
        count_fail_final=int(len(final_stats_vec))
        for count_fail_final in range(23):
                final_stats_vec.append(int(0))

    return final_stats_vec

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def course_report_exception():
    query = db.course_report_exception
    grid = SQLFORM.grid(query, maxtextlength=100,csv=False)
    return dict(grid=grid)
#***********************************************************************************************************************
#******************************************************PHASE 2 DTT******************************************************

# coding: utf8
# intente algo como
@auth.requires_membership('Super-Administrator')
def scheduler_activity():
    auto_daily()
    return dict(data = db3(db3.scheduler_run.id>0).select(orderby = ~ db3.scheduler_run.id))

@auth.requires_membership('Super-Administrator')
def calificar_practicantes():
    resumen = validar_practicantes_finales()
    return dict(resumen=resumen)

@auth.requires_membership('Super-Administrator')
def dtt_general_approval():
    status = request.vars['status']
    period = request.vars['period']
    approve = request.vars['approve']
    cperiod = db(db.period_year.id==period).select().first()
    if cperiod.period == 1:
        start = datetime.strptime(str(cperiod.yearp) + '-01-01', "%Y-%m-%d")
        end = datetime.strptime(str(cperiod.yearp) + '-06-01', "%Y-%m-%d")
    else:
        start = datetime.strptime(str(cperiod.yearp) + '-06-01', "%Y-%m-%d")
        end = datetime.strptime(str(cperiod.yearp+1) + '-01-01', "%Y-%m-%d")
    # Get the coincident reports
    if status == 'None':
        reports = db((db.report.created>start)&
                     (db.report.created<end)).select()
        for report in reports:
            entries = count_log_entries(report)
            metrics = count_metrics_report(report)
            #TODO cambio
            #anomalies = count_anomalies(report)[0]['COUNT(log_entry.id)']
            anomalies = count_anomalies(report)[0]['_extra']['COUNT(`log_entry`.`id`)']
            if entries != 0 or metrics!= 0 or anomalies != 0:
                report.update_record(dtt_approval = approve)
    elif int(status) == -1:
        reports = db((db.report.created>start)&
            (db.report.created<end)&
            (db.report.score>=db.report.min_score)&
            (db.report.min_score!=None)&
            (db.report.min_score!=0)).select()
        for report in reports:
            entries = count_log_entries(report)
            metrics = count_metrics_report(report)
            #TODO 
            #anomalies = count_anomalies(report)[0]['COUNT(log_entry.id)']
            anomalies = count_anomalies(report)[0]['_extra']['COUNT(`log_entry`.`id`)']
            if entries != 0 or metrics!= 0 or anomalies != 0:
                report.update_record(dtt_approval = approve)
    else:
        reports = db((db.report.created>start)&
            (db.report.created<end)&
            (db.report.status==status)).select()
        for report in reports:
            entries = count_log_entries(report)
            metrics = count_metrics_report(report)
            anomalies = count_anomalies(report)[0]['COUNNT(log_entry.id)']
            #anomalies = count_anomalies(report)[0]['_extra']['COUNT(`log_entry`.`id`)']
            if entries != 0 or metrics!= 0 or anomalies != 0:
                report.update_record(dtt_approval = approve)
    if request.env.http_referer is None:
        redirect(URL('admin','report_filter'))
    else:
        redirect(request.env.http_referer)
    return

def dtt_general_approval_dcos():
    status = request.vars['status']
    period = request.vars['period']
    approve = request.vars['approve'] or None

    if(int(status)>=0): #Estados
        reports = db.executesql(queries.q_report_filter(1).format(period,status), as_dict=True)
    elif(status=="-1"): #APROBADOS
        reports = db.executesql(queries.q_report_filter(2).format(period), as_dict=True)        
    elif(status=="-2"): #REPROBADOS
        reports = db.executesql(queries.q_report_filter(3).format(period), as_dict=True)
    elif(status=="-3"): #APROBADO DTT
        reports = db.executesql(queries.q_report_filter(4).format(period), as_dict=True)
    elif(status=="-4"): #PENDIENTE DTT
        reports = db.executesql(queries.q_report_filter(5).format(period), as_dict=True)
    elif(status=="-5"): #ENTREGADOS
        reports = db.executesql(queries.q_report_filter(6).format(period), as_dict=True)
    elif(status=="-6"): #NO ENTREGADOS
        reports = db.executesql(queries.q_report_filter(7).format(period), as_dict=True)
    elif(status=="-7"): #PENDIENTES
        reports = db.executesql(queries.q_report_filter(8).format(period), as_dict=True)
    else:
        reports=[]

    for repo in reports:
        report = db(db.report.id == repo['id']).select().first()
        entries = count_log_entries(report)
        metrics = count_metrics_report(report)
        #TODO
        #anomalies = count_anomalies(report)[0]['COUNT(log_entry.id)']
        anomalies = count_anomalies(report)[0]['_extra']['COUNT(`log_entry`.`id`)']
        if entries != 0 or metrics!= 0 or anomalies != 0:
            report.update_record(dtt_approval = approve)
        else:
            session.flash = 'Las metricas del reporte son invalidas'

    if request.env.http_referer is None:
        redirect(URL('admin','report_filter'))
    else:
        redirect(request.env.http_referer)
    return

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def roles():
    grid = SQLFORM.smartgrid(db.auth_group, linked_tables=['auth_membership'])
    return dict(grid=grid)

# Inicio - Practicas Finales(DSA) - Jose Carlos I Alonzo Colocho
@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def documents_roles():
    args = request.args
    new_dict = {}

    def get_users_for_dsa_roles_local():
        query = dsa_utils.get_users_for_dsa_roles()
        return db.executesql(query, as_dict=True)

    def get_users_form_select(type=None):
        users = get_users_for_dsa_roles_local()

        users_list = list()
        users_list.append(OPTION("", _value=0))
        for user in users:
            content = "{} - {} {}".format(user['username'], user['first_name'], user['last_name'])
            users_list.append(OPTION(content, _value=str(user['id']), _selected=(True if type == str(user['id']) else False)))

        return SELECT(users_list, _name='inputUsers', _id='inputUsers', _class="form-control")

    if len(args) == 0:
        new_dict['type'] = 'list'
        query = dsa_utils.get_roles()
        new_dict['list'] = db.executesql(query, as_dict=True)
    elif len(args) == 1:
        option = args[0]
        new_dict['type'] = option

        if option == "new":
            if request.env.request_method == "POST":
                vars = request.vars
                role = {
                    'name': vars['inputName'],
                    'description': vars['inputDescription']
                }
                try:
                    insert_query = dsa_utils.create_role(role)
                    db.executesql(insert_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)

                session.flash = 'Registro creado exitosamente'
                redirect(URL('admin', 'documents_roles'))
        elif option == "show":
            vars = request.vars
            try:
                query = dsa_utils.get_role(vars['id'])
                role = db.executesql(query, as_dict=True)
            except Exception as e:
                new_dict['message'] = str(e)
                return dict(action=new_dict)

            if len(role) < 1:
                session.flash = "No existe el rol"
                redirect(URL('admin', 'documents_roles'))

            new_dict['item'] = role[0]
            return dict(action=new_dict)
        elif option == "delete":
            vars = request.vars 
            try:
                query = dsa_utils.delete_role(vars['id'])
                db.executesql(query)
            except Exception as e:
                new_dict['message'] = str(e)
                return dict(action=new_dict)
            
            session.flash = "Registro eliminado exitosamente"
            redirect(URL('admin', 'documents_roles'))
        elif option == "edit":
            vars = request.vars
            query = dsa_utils.get_role(vars['id'])
            role = db.executesql(query, as_dict=True)

            if request.env.request_method == "POST":
                role = {
                    'id': vars['id'],
                    'name': vars['name'],
                    'description': vars['description']
                }
                try:
                    query = dsa_utils.update_role(role)
                    db.executesql(query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)
                
                session.flash = 'Registro actualiado exitosamente'
                redirect(URL('admin', 'documents_roles'))
            else:
                new_dict['item'] = role[0]
        elif option == "members":
            vars = request.vars

            try:
                query = dsa_utils.get_role(vars['id'])
                get_query = dsa_utils.get_users_per_dsa_role(vars['id'])
                role = db.executesql(query, as_dict=True)
                users = db.executesql(get_query, as_dict=True)
                new_dict['item'] = role[0]
                new_dict['users'] = users
            except Exception as e:
                new_dict['message'] = str(e)
                return dict(action=new_dict)
        elif option == "members_new":
            vars = request.vars
            query = dsa_utils.get_role(vars['id'])
            role = db.executesql(query, as_dict=True)
        
            new_dict['item'] = role[0]
            new_dict['users_form'] = get_users_form_select()

            if request.env.request_method == "POST":
                if vars['inputUsers'] != "0":
                    try:
                        insert_query = dsa_utils.insert_user_assign_role(vars['inputUsers'], vars['id'])
                        db.executesql(insert_query)
                    except Exception as e:
                        e = str(e)
                        if "1062" in e:
                            e = "El usuario ya esta asociado a ese rol"
                        new_dict['message'] = e
                        return dict(action=new_dict)
                    
                    session.flash = 'Usuario asignado correctamente'
                    redirect(URL('admin', 'documents_roles', args=['members'], vars={'id': vars['id']}))
                else:
                    new_dict['message'] = "Debe seleccionar un usuario para realizar esta accion"
            else:
                return dict(action=new_dict)
        elif option == "members_delete":
            vars = request.vars
            try:
                query = dsa_utils.remove_user_from_role(vars['user'], vars['role'])
                db.executesql(query)
            except Exception as e:
                new_dict['message'] = str(e)
                return dict(action=new_dict)
            
            session.flash = "Registro eliminado exitosamente"
            redirect(URL('admin', 'documents_roles', args=["members"], vars={'id': vars['role']}))

    return dict(action=new_dict)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def dsa_manage_type_file():
    args = request.args
    new_dict = {}

    def validate_extension_format(extensionString):
        pattern = re.compile("^[a-zA-Z]+(,[a-zA-Z]+)*")
        validation = pattern.search(extensionString)
        if validation is None:
            return False

        return len(extensionString) == validation.span()[1]

    if len(args) == 0:
        new_dict['type'] = 'list'
        query = dsa_utils.get_all_file_types()
        new_dict['list'] = db.executesql(query, as_dict=True)
    elif len(args) == 1:
        option = args[0]
        new_dict['type'] = option

        if option == 'new':
            if request.env.request_method == "POST":
                vars = request.vars
                item = {
                    'inputName': vars['inputName'],
                    'inputExtension': vars['inputExtension']
                }

                if not validate_extension_format(vars['inputExtension']):
                    new_dict['message'] = "El patron de las extensiones no es correcto"
                    new_dict['item'] = item
                    return dict(action=new_dict)

                file_type = {
                    'name': vars['inputName'].strip(),
                    'extension': vars['inputExtension'].strip()
                }
                try:
                    insert_query = dsa_utils.create_file_type(file_type)
                    db.executesql(insert_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)
                
                session.flash = 'Registro creado exitosamente'
                redirect(URL('admin', 'dsa_manage_type_file'))
        elif option == "show":
            vars = request.vars
            try:
                query = dsa_utils.get_file_type(vars['id'])
                item = db.executesql(query, as_dict=True)
                new_dict['item'] = item[0]
            except Exception as e:
                new_dict['message'] = str(e)
                return dict(action=new_dict)
        elif option == "delete":
            vars = request.vars
            try:
                query = dsa_utils.delete_file_type(vars['id'])
                db.executesql(query)
            except Exception as e:
                new_dict['message'] = str(e)
                return dict(action=new_dict)
            
            session.flash = "Registro eliminado exitosamente"
            redirect(URL('admin', 'dsa_manage_type_file'))
        elif option == "edit":
            vars = request.vars
            query = dsa_utils.get_file_type(vars['id'])
            item = db.executesql(query, as_dict=True)
            item = item[0]
            item = {
                'inputNameE': item['name'],
                'inputExtensionE': item['extension'],
                'id': vars['id']
            }
            new_dict['item'] = item

            if request.env.request_method == "POST":
                item = {
                    'inputNameE': vars['inputNameE'],
                    'inputExtensionE': vars['inputExtensionE'],
                    'id': vars['id']
                }
                
                if not validate_extension_format(vars['inputExtensionE']):
                    new_dict['message'] = "El patron de las extensiones no es correcto"
                    new_dict['item'] = item
                    return dict(action=new_dict)

                file_type = {
                    'name': vars['inputNameE'].strip(),
                    'extension': vars['inputExtensionE'].strip(),
                    'id': vars['id']
                }
                try:
                    update_query = dsa_utils.update_file_type(file_type)
                    db.executesql(update_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)
                
                session.flash = 'Registro actualizado exitosamente'
                redirect(URL('admin', 'dsa_manage_type_file'))
        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
    else:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    return dict(action=new_dict)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def manage_document_ecys():
    args = request.args
    new_dict = {}

    def get_file_types_form_select(type=None, complement_type=None):
        file_types = list()
        file_types_complement = list()

        file_types.append(OPTION("", _value=0))
        file_types_complement.append(OPTION("", _value=0))

        query = dsa_utils.get_all_file_types()
        file_types = db.executesql(query, as_dict=True)
        for file_type in file_types:
            file_types.append(OPTION(file_type['name'], _value=str(file_type['id']), _selected=(True if type == str(file_type['id']) else False)))
            file_types_complement.append(OPTION(file_type['name'], _value=str(file_type['id']), _selected=(True if complement_type == str(file_type['id']) else False)))

        result = {
            'selectPrincipal': SELECT(file_types, _name='inputFileTypes', _id='inputFileTypes', _class="form-control"),
            'selectComplement': SELECT(file_types_complement, _name='inputFileTypesComplement', _id='inputFileTypesComplement', _class="form-control")
        }
        return result

    def get_roles_form_select(type=None):
        roles = list()
        roles.append(OPTION("", _value=0))
        query = dsa_utils.get_roles()
        roles_result = db.executesql(query, as_dict=True)
        for role in roles_result:
            roles.append(OPTION(role['name'], _value=str(role['id']), _selected=(True if type == str(role['id']) else False)))

        return SELECT(roles, _name='inputRole', _id='inputRole', _class="form-control")

    def get_max_size_form_select_local(size="0", complement_size="0"):
        size_options = list()
        size_options_complement = list()

        size_options.append(OPTION("", _value=0))
        size_options_complement.append(OPTION("", _value=0))

        for contador in range(1,11):
            size_options.append(OPTION(str(contador), _value=str(contador), _selected=(True if int(size) == contador else False)))
            size_options_complement.append(OPTION(str(contador), _value=str(contador), _selected=(True if int(complement_size) == contador else False)))

        result = {
            'sizePrincipal': SELECT(size_options, _name='inputSize', _id='inputSize', _class="form-control"),
            'sizeComplement': SELECT(size_options_complement, _name='inputComplementSize', _id='inputComplementSize', _class="form-control")
        }
        return result

    def get_checkbox_form(complement=False, signature=False, validation=False):
        result = {
            'checkSignature':  INPUT(_type='checkbox', _name='inputSignature', _id='inputSignature',
                                     _class="form-check-input", _value='1', value=signature),
            'checkComplement': INPUT(_type='checkbox', _name='inputComplement', _id='inputComplement',
                                      _class="form-check-input", _value='1', value=complement),
            'checkValidation': INPUT(_type='checkbox', _name='inputValidation', _id='inputValidation',
                                      _class="form-check-input", _value='1', value=validation)
        }
        return result

    def validate_form(vars, message, id="0"):
        new_dict['item'] = {
            'inputName': vars['inputName'],
            'inputDescription': vars['inputDescription']
        }
        
        if id != "0":
            new_dict['item']['id'] = id

        checkbox = get_checkbox_form(vars['inputComplement'], vars['inputSignature'], vars['inputValidation'])
        select = get_file_types_form_select(vars['inputFileTypes'], vars['inputFileTypesComplement'])
        selectSize = get_max_size_form_select_local(vars['inputSize'], vars['inputComplementSize'])
        new_dict['roles'] = get_roles_form_select(vars['inputRole'])
    
        new_dict['show'] = "display: ;" if vars['inputComplement'] == "1" else "display: none;"
        new_dict['checkComplement'] = checkbox['checkComplement']
        new_dict['checkSignature'] = checkbox['checkSignature']
        new_dict['checkValidation'] = checkbox['checkValidation']
        new_dict['file_types'] = select['selectPrincipal']
        new_dict['file_types_complement'] = select['selectComplement']
        new_dict['sizePrincipal'] = selectSize['sizePrincipal']
        new_dict['sizeComplement'] = selectSize['sizeComplement']
        
        if message != "":
            new_dict['message'] = message

    if len(args) == 0:
        new_dict['type'] = 'list'
        query = dsa_utils.get_all_document_types_admin()
        new_dict['list'] = db.executesql(query, as_dict=True)
    elif len(args) == 1:
        option = args[0]
        new_dict['type'] = option
        if option == "new":
            if request.env.request_method == "POST":
                vars = request.vars
                if vars['inputSize'] == "0" or vars['inputFileTypes'] == "0" or vars['inputRole'] == "0":
                    validate_form(vars, "Rellene todos los campos necesarios para esta accion")
                    return dict(action=new_dict)
                
                if vars['inputComplement'] == "1" and (vars['inputComplementSize'] == "0" or vars['inputFileTypesComplement'] == "0"):
                    validate_form(vars, "Rellene todos los campos necesarios para esta accion")
                    return dict(action=new_dict)

                signature = "true" if vars['inputSignature'] == "1" else "false"
                validation = "true" if vars['inputValidation'] == "1" else "false"
                complement = "true" 

                if not 'imputComplement' in vars:
                    complement = "false"
                    vars['inputComplementSize'] = "0"
                    vars['inputFileTypesComplement'] = "NULL"

                document = {
                    'name': vars['inputName'],
                    'description': vars['inputDescription'],
                    'max_size': vars['inputSize'],
                    'complement_size': vars['inputComplementSize'],
                    'signature_required': signature,
                    'complement_required': complement,
                    'validation_required': validation,
                    'type_file': vars['inputFileTypes'],
                    'complement_type_file': vars['inputFileTypesComplement']
                }            
                result = None
                try:
                    query = dsa_utils.create_document_type(document)
                    db.executesql(query)
                    get_query = dsa_utils.get_last_id_from_document_type()
                    result = db.executesql(get_query, as_dict=True)
                    result = result[0]
                except Exception as e:
                    validate_form(vars, str(e))
                    print(str(e))
                    return dict(action=new_dict)
                
                assign = {
                    'document': result['id'],
                    'role': vars['inputRole']
                }
                try:
                    insert_query = dsa_utils.create_document_assign_role(assign)
                    db.executesql(insert_query)
                except Exception as e:
                    condition = {'id': int(result['id'])}
                    delete_query = ds_utils.create_script_string('dsa_document_type', 'D', condition ,condition)
                    db.executesql(delete_query)
                    validate_form(vars, str(e))
                    print(str(e))
                    return dict(action=new_dict)
                
                session.flash = "Documento creado exitosamente"
                redirect(URL('admin', 'manage_document_ecys'))
            else:
                checkbox = get_checkbox_form()
                select = get_file_types_form_select()
                selectSize = get_max_size_form_select_local()
                
                new_dict['roles'] = get_roles_form_select()
                new_dict['show'] = "display: none;"
                new_dict['checkComplement'] = checkbox['checkComplement']
                new_dict['checkSignature'] = checkbox['checkSignature']
                new_dict['checkValidation'] = checkbox['checkValidation']
                new_dict['file_types'] = select['selectPrincipal']
                new_dict['file_types_complement'] = select['selectComplement']
                new_dict['sizePrincipal'] = selectSize['sizePrincipal']
                new_dict['sizeComplement'] = selectSize['sizeComplement']         
    elif len(args) == 2:
        option = args[0]
        id = args[1]
        new_dict['type'] = option
        query = dsa_utils.get_document_type_admin(id)
        item = db.executesql(query, as_dict=True)

        if len(item) < 1:
            session.flash = 'No existe el registro'
            redirect(URL('admin', 'manage_documents_ecys'))

        if option == 'show':
            new_dict['item'] = item
        elif option == "delete":
            condition = {'id': int(id)}
            try:
                delete_query = ds_utils.create_script_string('dsa_document_type', 'D', condition ,condition)
                db.executesql(delete_query)
            except Exception as e:
                new_dict['message'] = str(e)
                return dict(action=new_dict)
            
            session.flash = 'Registro eliminado exitosamente'
            redirect(URL('admin', 'manage_document_ecys'))
        elif option == "edit":
            if request.env.request_method == "POST":
                vars = request.vars
                if vars['inputSize'] == "0" or vars['inputFileTypes'] == "0" or vars['inputRole'] == "0":
                    validate_form(vars, "Rellene todos los campos necesarios para esta accion", id)
                    return dict(action=new_dict)

                if vars['inputComplement'] == "1" and (vars['inputComplementSize'] == "0" or vars['inputFileTypesComplement'] == "0"):
                    validate_form(vars, "Rellene todos los campos necesarios para esta accion", id)
                    return dict(action=new_dict)

                signature = "true" if vars['inputSignature'] == "1" else "false"
                validation = "true" if vars['inputValidation'] == "1" else "false"
                complement = "true" 
                #if not vars.has_key('inputComplement'):
                if not 'inputComplement' in vars:
                    complement = "false"
                    vars['inputComplementSize'] = "0"
                    vars['inputFileTypesComplement'] = "NULL"

                document = {
                    'name': vars['inputName'], 'description': vars['inputDescription'],
                    'max_size': vars['inputSize'], 'complement_size': vars['inputComplementSize'],
                    'signature_required': signature, 'complement_required': complement,
                    'validation_required': validation, 'type_file': vars['inputFileTypes'],
                    'complement_type_file': vars['inputFileTypesComplement'], 'id': id
                }            
                try:
                    query = dsa_utils.update_document_type(document)
                    db.executesql(query)
                except Exception as e:
                    validate_form(vars, str(e))
                    print(str(e))
                    return dict(action=new_dict)

                try:
                    insert_query = dsa_utils.update_document_assign_role(vars['inputRole'], id)
                    db.executesql(insert_query)
                except Exception as e:
                    condition = {'id': int(result['id'])}
                    delete_query = ds_utils.create_script_string('dsa_document_type', 'D', condition ,condition)
                    db.executesql(delete_query)
                    validate_form(vars, str(e))
                    print(str(e))
                    return dict(action=new_dict)
                
                session.flash = "Documento actualizado exitosamente"
                redirect(URL('admin', 'manage_document_ecys'))
            else:
                query = dsa_utils.get_document_type_admin_edit(id)
                item = db.executesql(query, as_dict=True)
                item = item[0]
                
                item['complement_extension'] = 0 if item['complement_extension'] is None else item['complement_extension']
                vars = {
                    'inputName': item['name'], 'inputDescription': item['description'],
                    'inputComplement': str(item['complement_required']), 'inputSignature': str(item['signature_required']),
                    'inputValidation': str(item['validation_required']), 'inputFileTypes': str(item['extension']),
                    'inputFileTypesComplement': str(item['complement_extension']), 'inputSize': str(item['max_size']),
                    'inputComplementSize': str(item['complement_size']), 'inputRole': str(item['role'])
                }
                validate_form(vars, "", id)
    return dict(action=new_dict)
# Fin - Practicas Finales(DSA) - Jose Carlos I Alonzo Colocho  

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def general_report():
    period = cpfecys.current_year_period()
    if request.vars['period'] != None:
        period = request.vars['period']
        period = db(db.period_year.id==period).select().first()
        if not period:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
    periods = db(db.period_year).select()
    areas = db(db.area_level).select()    
    area = areas.first()
    if request.vars['area'] != None:
        area = request.vars['area']
        area = db(db.area_level.id==area).select().first()
        if not area:
            session.flash = T('Not valid Action')
            redirect(URL('default','home'))

    projects = db.executesql(queries.q_general_report().format(period.id,area.id))


    def get_projects(area):
        projects = db(db.project.area_level==area).select()
        return projects
    def get_teacher(project):
        assignations = get_assignations(project, period, 'Teacher' \
                ).select(db.user_project.ALL)
        return assignations
    def get_final_report(project_id,period):
        log_final = None
        parcial_1 = None
        parcial_2 = None
        parcial_3 = None
        cperiod = period
        year = str(cperiod.yearp)
        start = datetime.strptime(year + '-06-01', "%Y-%m-%d")
        end = datetime.strptime(year + '-12-31', "%Y-%m-%d")
        if cperiod.period == 1:
            start = datetime.strptime(year + '-01-01', "%Y-%m-%d")
            end = datetime.strptime(year + '-06-01', "%Y-%m-%d")

        final_report = db((db.report.created>start)&
                     (db.report.created<end)&
                     ((db.report_restriction.is_enabled!=None) &
                        (db.report_restriction.is_enabled!=False))&
                     (db.report.assignation==db.user_project.id)&
                     (db.user_project.project==int(project_id))&
                     (db.report.report_restriction==db.report_restriction.id)&
                     ((db.report_restriction.is_final!=None)&
                        (db.report_restriction.is_final!=False)&
                        ((db.report.never_delivered==None)|(db.report.never_delivered==False)))
                      ).select(db.report.ALL).first()

        project_reports = db((db.report.created>start)&
                     (db.report.created<end)&
                     ((db.report_restriction.is_enabled!=None) &
                        (db.report_restriction.is_enabled!=False))&
                     (db.report.assignation==db.user_project.id)&
                     (db.user_project.project==int(project_id))
                      )._select(db.report.id)

        parcial_1 = db((db.log_metrics.metrics_type== \
                        db.metrics_type(name='PRIMER PARCIAL'))&
                        (db.log_metrics.report.belongs(project_reports))
                        ).select(db.log_metrics.ALL).first()
        parcial_2 = db((db.log_metrics.metrics_type== \
                        db.metrics_type(name='SEGUNDO PARCIAL'))&
                        (db.log_metrics.report.belongs(project_reports))
                        ).select(db.log_metrics.ALL).first()
        parcial_3 = db((db.log_metrics.metrics_type== \
                        db.metrics_type(name='TERCER PARCIAL'))&
                        (db.log_metrics.report.belongs(project_reports))
                        ).select(db.log_metrics.ALL).first()
        final = db((db.log_metrics.metrics_type== \
                        db.metrics_type(name='EXAMEN FINAL'))&
                        (db.log_metrics.report.belongs(project_reports))
                        ).select(db.log_metrics.ALL).first()
        primera_r = db((db.log_metrics.metrics_type== \
                        db.metrics_type(name='PRIMERA RETRASADA'))&
                        (db.log_metrics.report.belongs(project_reports))
                        ).select(db.log_metrics.ALL).first()
        segunda_r = db((db.log_metrics.metrics_type== \
                        db.metrics_type(name='SEGUNDA RETRASADA'))&
                        (db.log_metrics.report.belongs(project_reports))
                        ).select(db.log_metrics.ALL).first()
        if final_report != None:
            log_final = db(db.log_final.report== \
                final_report.id).select().first()

        return final_report, log_final, parcial_1, parcial_2, parcial_3, \
                final, primera_r, segunda_r

    periods = db(db.period_year).select()
    return dict(areas=areas, projects=projects, get_projects=get_projects, 
        get_teacher=get_teacher,get_final_report=get_final_report,
        actual_period=period, actual_area=area, periods=periods)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def count_log_entries(report):
    #***********************************************************************************************************************
    #******************************************************PHASE 2 DTT******************************************************
    if report.assignation.project.area_level.name=='DTT Tutor Académico' and (report.status.name=='Draft' or report.status.name=='Recheck'):
        activities_tutor = activities_report_tutor(report)
        log_entries=len(activities_tutor['activities_wm'])+len(activities_tutor['activities_m'])
    else:
        #log_entries = db((db.log_entry.report==report.id)).select(db.log_entry.id.count())[0]['COUNT(log_entry.id)']
        log_entries = db((db.log_entry.report == report.id)).select(db.log_entry.id.count())[0]['_extra']['COUNT(`log_entry`.`id`)']
    return log_entries
    #***********************************************************************************************************************
    #******************************************************PHASE 2 DTT******************************************************

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def count_metrics_report(report):
    #***********************************************************************************************************************
    #******************************************************PHASE 2 DTT******************************************************
    if report.assignation.project.area_level.name=='DTT Tutor Académico' and (report.status.name=='Draft' or report.status.name=='Recheck'):
        activitiesTutor = activities_report_tutor(report)
        log_metrics=len(activitiesTutor['activities_m'])
    else:
        log_metrics = db((db.log_metrics.report== report.id)).select(db.log_metrics.id.count())[0]['COUNT(log_metrics.id)']
    return log_metrics
    #***********************************************************************************************************************
    #******************************************************PHASE 2 DTT******************************************************

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def count_anomalies(report):
    log_entries = db((db.log_entry.report== \
        report)&
    (db.log_entry.log_type==db.log_type(name='Anomaly')) \
    ).select(db.log_entry.id.count())
    return log_entries

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def delivered():
    periods = db(db.period_year).select()
    period = cpfecys.current_year_period()
    area_list = []
    if request.vars['period'] != None:
        period = request.vars['period']
        period = db.period_year(db.period_year.id==period)
    admin = False
    restrictions = db(
       (db.item_restriction.item_type==db.item_type(name='Activity'))& \
       ((db.item_restriction.period==period.id) |
        ((db.item_restriction.permanent==True)&
            (db.item_restriction.period <= period.id)))&
        (db.item_restriction.is_enabled==True)).select()| \
    db((db.item_restriction.item_type==db.item_type(name='Grade Activity'))& \
       ((db.item_restriction.period==period.id) |
        ((db.item_restriction.permanent==True)&
            (db.item_restriction.period <= period.id)))&
        (db.item_restriction.is_enabled==True)).select()
    def calculate_by_restriction(restriction):
        pending = 0
        graded = 0
        total = 0
        approved = 0
        failed = 0
        restriction_instance = db(
           (db.item_restriction.item_type==db.item_type(name='Activity'))& \
           (db.item_restriction.id==restriction)&
           (db.item_restriction.is_enabled==True)).select() | \
            db((db.item_restriction.item_type==db.item_type( \
                name='Grade Activity'))& \
           (db.item_restriction.id==restriction)&
           (db.item_restriction.is_enabled==True)
                ).select(db.item_restriction.ALL)

        areas = db((db.item_restriction_area.item_restriction== \
            restriction_instance[0].id)&
            (db.area_level.id==db.item_restriction_area.area_level)
                ).select(db.area_level.ALL)
        for area in areas:
            area_list.append(area.id)
        projects = db((db.project.area_level==db.area_level.id)&
         (db.item_restriction.id==restriction)&
         (db.item_restriction_area.area_level.belongs(area_list))&
         (db.item_restriction_area.item_restriction==restriction)&
         (db.item_restriction_area.item_restriction==db.item_restriction.id)&
         (db.item_restriction_area.area_level==db.area_level.id)&
         (db.item_restriction_area.is_enabled==True)).select(db.project.ALL)

        for project in projects:
            exception = db((db.item_restriction_exception.project== \
                project.id)&
                (db.item_restriction_exception.item_restriction== \
                restriction))
            if exception.count() == 0:
                assignations = db(
                    (db.auth_user.id==db.user_project.assigned_user)&
                    (db.auth_user.id==db.auth_membership.user_id)&
                    (db.auth_membership.group_id==db.auth_group.id)&
                    (db.auth_group.role=='Student')&
                    (db.user_project.project==project.id)&
                    (db.user_project.period == db.period_year.id)&
                    ((db.user_project.period <= period.id)&
                 ((db.user_project.period.cast('integer') + db.user_project.periods) > \
                  period.id))
                    ).select(db.user_project.ALL)
                for assignation in assignations:
                    item = db((db.item.assignation==assignation.id)&
                     (db.item.item_restriction==restriction)&
                     (db.item.item_restriction==db.item_restriction.id)&
                     (db.item_restriction.is_enabled==True)&
                     (db.item.is_active==True)&
                     (db.item.created==period.id)).select(db.item.ALL).first()
                    if item == None:
                        pending += 1
                        total += 1
                    elif item.item_restriction.item_type.name=='Grade Activity':
                        if item.min_score == None:
                            pending += 1
                            total += 1
                        elif item.score >= item.min_score:
                            graded += 1
                            approved += 1
                            total += 1
                    elif item.item_restriction.item_type.name=='Activity':
                        if item.done_activity == None:
                            pending += 1
                            total += 1
                        elif item.done_activity == True:
                            graded += 1
                            approved += 1
                            total += 1
                        elif item.done_activity == False:
                            graded += 1
                            failed += 1
                            total += 1
        return pending, graded, total, approved, failed
    return dict(restrictions=restrictions, periods=periods,
        calculate_by_restriction=calculate_by_restriction,
        period=period)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def dtt_approval():
    # get report id
    report = request.vars['report']
    # get the approval value
    approve = request.vars['approve']
    # get the report
    report = db.report(id = report)
    # toggle report dtt_approval flag
    report.dtt_approval = approve
    report.update_record()
    if request.env.http_referer is None:
        redirect(URL('admin','report_filter'))
    else:
        redirect(request.env.http_referer)
    return

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def assignation_freeze():
    grid = SQLFORM.grid(db.assignation_freeze)
    return dict(grid = grid)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def assignation_ignore_toggle():
    # get assignation id
    assignation = request.vars['id']
    # get the assignation
    assignation = db.user_project(id = assignation)
    # toggle assignation_ignored flag
    assignation.assignation_ignored = not assignation.assignation_ignored
    assignation.update_record()
    if request.env.http_referer:
        redirect(request.env.http_referer)
    else:
        redirect(URL('admin','assignations'))
    return

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def force_assignation_active():
    # get assignation id
    assignation = request.vars['id']
    # get assignation comment
    comment = request.vars['comment']
    # get the assignation
    assignation = db.user_project(id = assignation)
    # set the assignation as active
    assignation.assignation_status = None
    assignation.assignation_status_comment = comment
    assignation.update_record()
    if request.env.http_referer:
        redirect(request.env.http_referer)
    else:
        redirect(URL('admin','assignations'))
    return

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def force_assignation_failed():
    # get assignation id
    assignation = request.vars['id']
    # get assignation comment
    comment = request.vars['comment']
    # get the assignation
    assignation = db.user_project(id = assignation)
    # set the assignation as failed
    assignation.assignation_status = db.assignation_status(name="Failed")
    assignation.assignation_status_comment = comment
    assignation.update_record()
    if request.env.http_referer:
        redirect(request.env.http_referer)
    else:
        redirect(URL('admin','assignations'))
    return

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def force_assignation_successful():
    # get assignation id
    assignation = request.vars['id']
    # get assignation comment
    comment = request.vars['comment']
    # get the assignation
    assignation = db.user_project(id = assignation)
    # set the assignation as successful
    assignation.assignation_status = db.assignation_status(name="Successful")
    assignation.assignation_status_comment = comment
    assignation.update_record()
    if request.env.http_referer:
        redirect(request.env.http_referer)
    else:
        redirect(URL('admin','assignations'))
    return

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def assignations():
    #requires parameter year_period if no one is provided then it is automatically detected
    #and shows the current period
    year_period = request.vars['year_period'] or False
    max_display = 1
    currentyear_period = db(db.period_year.id == cpfecys.current_year_period()).select(db.period_year.id).first()

    if year_period:
        currentyear_period = db(db.period_year.id == year_period).select(db.period_year.id).first()
        if int(year_period) == 0:
            currentyear_period = db(db.period_year.id == cpfecys.current_year_period()).select(db.period_year.id).first()

    #emarquez
    #type=2, periodo variable.  si type=1, periodo semestre
    tipo_periodo = request.vars['type'] or False
    if not tipo_periodo:
        tipo_periodo = 1

    q_selected_period_assignations = ((db.user_project.period == 1))
    if year_period:
        q_selected_period_assignations = ((db.user_project.period == year_period))

    #emarquez: si es semestre la funcionalidad se queda intacta, enero 2017    
    if int(tipo_periodo) == 1:
        q_selected_period_assignations = ((db.user_project.period <= currentyear_period.id) & ((db.user_project.period.cast('integer') + db.user_project.periods) > currentyear_period.id))

    data = db(q_selected_period_assignations & (db.user_project.assigned_user == db.auth_user.id)
            & (db.user_project.project == db.project.id) & (db.user_project.period == db.period_year.id)
            & (db.project.area_level == db.area_level.id) & (db.auth_user.id == db.user_project.assigned_user)
            & (db.auth_user.id == db.auth_membership.user_id) & (db.auth_membership.group_id == db.auth_group.id) 
            & (db.auth_group.role != 'Teacher')).select(
                db.auth_user.registration_key,
                db.auth_user.id,
                db.auth_user.last_name,
                db.auth_user.first_name,
                db.auth_user.username,
                db.auth_user.cui,
                db.auth_user.email,
                db.auth_user.phone,
                db.auth_user.work_address,
                db.auth_user.company_name,
                db.auth_user.work_phone,
                db.auth_user.home_address,
                db.project.area_level,
                db.project.name,
                db.period_year.yearp,
                db.period_year.period,
                db.user_project.periods,
                db.user_project.assignation_status,
                db.user_project.assignation_status_comment,
                db.user_project.assignation_ignored,
                db.user_project.id,
                orderby=db.area_level.name | db.project.name 
                        | db.auth_user.username | db.auth_user.first_name,
                groupby=db.user_project.id
            )

    start_index = currentyear_period.id - max_display - 1
    if start_index < 1:
        start_index = 0
    end_index = currentyear_period.id + max_display

    #emarquez: periodos dinamicos
    if request.args(0) == 'toggle':
        enabled = ''
        user = request.vars['user']
        user = db(db.auth_user.id == user).select(db.auth_user.id, db.auth_user.registration_key).first()
        if user is None:
            session.flash = T("No existing user")
            redirect(URL('admin', 'assignations', vars=dict(year_period=currentyear_period)))
        if user.registration_key != 'blocked':
            enabled = 'blocked'
        
        user.update_record(registration_key=enabled)
        redirect(URL('admin', 'assignations', vars=dict(year_period=currentyear_period.id)))

    #emarquez nueva formula de periodos dinamicos
    listperios = db(db.period_detail.period)._select(db.period_detail.period)
    if int(tipo_periodo) == 1:
        periods_before = db((~db.period.id.belongs(listperios)) & (db.period_year.period == db.period.id)).select(
            db.period_year.id,
            db.period_year.period,
            db.period_year.yearp,
            orderby=~db.period_year.id
        )
    else:
        periods_before = db((db.period.id == db.period_detail.period) & (db.period_year.period == db.period.id)).select(
            db.period_year.id,
            db.period_year.period,
            db.period_year.yearp,
        )

    #fintest
    return dict(
        data=data,
        currentyear_period=currentyear_period,
        periods_before=periods_before,
        type=tipo_periodo,
    )

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def periods():
    grid = SQLFORM.grid(db.period_year)
    return locals()

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def report_requirements():
    grid = SQLFORM.grid(db.area_report_requirement)
    return locals()

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def report_restrictions():
    grid = SQLFORM.grid(db.report_restriction)
    return locals()

#emarquez: periodos variables, restricciones de reportes periodos
@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def report_restrictions_period():
    grid = SQLFORM.grid(db.report_restriction_period)
    return locals()

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def projects():
    grid = SQLFORM.grid(db.project)
    return locals()

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def parameters():
    grid = SQLFORM.grid(db.custom_parameters)
    return dict(grid=grid)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def report():
    cdate = datetime.now()
    report = request.vars['report']
    report = db.report(db.report.id == report)
    parameters = cpfecys.get_custom_parameters()
    valid = not(report is None)
    next_date = None
    if (request.args(0) == 'view'):
        report = request.vars['report']
        report = db.report(db.report.id == report)
        valid = not(report is None)
        if valid:
            semester = cpfecys.first_period.id
            if report.created.month >= 7:
                semester = cpfecys.second_period.id

            period = db((db.period_year.yearp==int(report.created.year))&
                (db.period_year.period==semester)).select().first()
            teacher = db(
                        (db.auth_user.id==db.user_project.assigned_user)&
                        (db.auth_user.id==db.auth_membership.user_id)&
                        (db.auth_membership.group_id==db.auth_group.id)&
                        (db.auth_group.role=='Teacher')&
                        (db.user_project.project==report.assignation.project)&
                        (db.user_project.period==db.period_year.id)&
                        ((db.user_project.period <= period.id)&
                       ((db.user_project.period.cast('integer') + db.user_project.periods) > \
                        period.id))
                        ).select(db.auth_user.ALL).first()
            def add_timing(status):
                if status == 'Acceptance':
                    return status
                elif status == 'Recheck':
                    return status + ' (' + str(parameters.rescore_max_days) + \
                        ' days)'
                else:
                    return status + ' (24 hours)'
            if report.score_date:
                next_date = report.score_date + timedelta(
                    days=parameters.rescore_max_days)
            response.view = 'admin/report_view.html'
            assignation_reports = db(db.report.assignation== \
                report.assignation).select()
            #***********************************************************************************************************************
            #******************************************************PHASE 2 DTT******************************************************
            activitiesTutor=None
            if report.assignation.project.area_level.name=='DTT Tutor Académico' and (report.status.name=='Draft' or report.status.name=='Recheck'):
                activitiesTutor = activities_report_tutor(report)
            return dict(
                log_types=db(db.log_type.id > 0).select(),
                assignation_reports = assignation_reports,
                logs=db((db.log_entry.report == report.id)).select(),
                parameters=parameters,
                metrics=db((db.log_metrics.report == report.id)).select(),
                final_r = db(db.log_final.report == report.id).select(),
                anomalies=db((db.log_type.name == 'Anomaly')&
                           (db.log_entry.log_type == db.log_type.id)&
                           (db.log_entry.report == report.id)).count(),
                markmin_settings=cpfecys.get_markmin,
                report=report,
                next_date=next_date,
                status_list=db(db.report_status).select(),
                add_timing=add_timing,
                teacher=teacher,
                activitiesTutor=activitiesTutor)
            #***********************************************************************************************************************
            #******************************************************PHASE 2 DTT******************************************************
        else:
            session.flash = T('Selected report can\'t be viewed. \
                                Select a valid report.')
            redirect(URL('admin', 'index'))
    elif (request.args(0) == 'approve'):
        report.update_record(dtt_approval=True)
        session.flash = T('The report has been approved')
        redirect(URL('admin', 'report/view', \
            vars=dict(report=report.id)))
    elif (request.args(0) == 'fail'):
        report.update_record(dtt_approval=False)
        session.flash = T('The report has been failed')
        redirect(URL('admin', 'report/view', \
            vars=dict(report=report.id)))
    elif (request.args(0) == 'pending'):
        report.update_record(dtt_approval=None)
        session.flash = T('The report has been set to pending')
        redirect(URL('admin', 'report/view', \
            vars=dict(report=report.id)))
    elif (request.args(0) == 'grade'):
        if valid:
            score = request.vars['score']
            comment = request.vars['comment']
            status = request.vars['status']
            sendmail = request.vars['send_mail']
            if sendmail != None: sendmail = True
            else: sendmail = False
            if score != '': score = int(score)
            else: score = report.score
            if comment == '': comment = report.teacher_comment
            status =db.report_status(id=status)
            if status.id != report.status:
                #***********************************************************************************************************************
                #******************************************************PHASE 2 DTT******************************************************
                if report.assignation.project.area_level.name=='DTT Tutor Académico' and (status.name=='Draft' or status.name=='Recheck'):
                    try:
                        temp_logType = db(db.log_type.name=='Activity').select().first()
                        db((db.log_entry.report==report.id)&(db.log_entry.log_type==temp_logType.id)).delete()
                    except:
                        db(db.log_entry.report==report.id).delete()
                    db(db.log_metrics.report==report.id).delete()
                    db(db.log_future.report==report.id).delete()

                    if report.report_restriction.is_final==True:
                        if db(db.log_final.report==report.id).select().first() is None:
                            #CREATE THE FINAL METRICS
                            cperiod = obtainPeriodReport(report)
                            final_metrics = final_metric(cperiod,report)
                            try:
                                average=float((final_metrics[22]*100)/final_metrics[20])
                            except:
                                average=float(0)
                            db.log_final.insert(curso_asignados_actas=int(final_metrics[0]),
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
                #***********************************************************************************************************************
                #******************************************************PHASE 2 DTT******************************************************
                report.update_record(
                    admin_score=score,
                    min_score=cpfecys.get_custom_parameters().min_score,
                    admin_comment=comment,
                    score_date=cdate,
                    status=status.id,
                    dtt_approval=True,
                    never_delivered=False)
            elif score >= 0  and score <= 100:
                report.update_record(
                    admin_score=score,
                    min_score=cpfecys.get_custom_parameters().min_score,
                    admin_comment=comment,
                    score_date=cdate,
                    status=db.report_status(name='Acceptance'),
                    dtt_approval=True,
                    never_delivered=False)

            if sendmail:
                user = report.assignation.assigned_user
                subject = T('[DTT]Automatic Notification - Report graded ') \
                +T('BY ADMIN USER')
                signat = cpfecys.get_custom_parameters().email_signature or ''
                cstatus = db(db.report_status.id==report.status).select().first()
                message = '<html>' + T('The report') + ' ' \
                + '<b>' + XML(report.report_restriction.name) + '</b><br/>' \
                + T('sent by student: ') + XML(user.username) + ' ' \
                + XML(user.first_name) + ' ' \
                + XML(user.last_name) \
                + '<br/>' \
                + T('Score: ') + XML(report.admin_score) + ' ' \
                + '<br/>' \
                + T('Scored by: ') + XML('Admin User') + ' ' \
                + '<br/>' \
                + T('Comment: ') + XML(comment) + ' ' \
                + '<br/>' \
                + T('Current status is: ') \
                + XML(T(cstatus.name)) +'<br/>' \
                + T('DTT-ECYS') \
                + ' ' + cpfecys.get_domain() + '<br />' + signat + '</html>'
                was_sent = mail.send(to=user.email,
                  subject=subject,
                  message=message)
                #MAILER LOG
                db.mailer_log.insert(sent_message = message,
                             destination = str(user.email),
                             result_log = str(mail.error or '') + ':' + str(mail.result),
                             success = was_sent)
            session.flash = T('The report has been scored \
                successfully')
            redirect(URL('admin', 'report/view', \
                vars=dict(report=report.id)))

        session.flash = T('Not valid Action.')
        redirect(URL('admin', 'report/view', \
                    vars=dict(report=report.id)))

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def courses_report():
    period = cpfecys.current_year_period()
    periods = db(db.period_year).select()
    area = None
    if request.vars['period'] is not None:
        period = request.vars['period']
        period = db(db.period_year.id == period).select().first()
        if not period:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
    
    if request.args(0) == 'areas':
        areas = db(db.area_level).select()
        return dict(areas=areas)
    elif request.args(0) == 'list':
        area = request.vars['area']
        response.view = 'admin/courses_list.html'
        projects = db(db.project.area_level==area).select()
        def count_assigned(project):
            assignations = get_assignations(project, period, 'Student' \
                ).count()
            return assignations
        def obtain_period_report(report):
            #Get the minimum and maximum date of the report
            tmp_period=1
            tmp_year=report.report_restriction.start_date.year
            if report.report_restriction.start_date.month >= 6:
               tmp_period=2
            return db((db.period_year.yearp==tmp_year)&(db.period_year.period==tmp_period)).select().first()
        
        def count_assigned_students(project):
            assigned = []
            desertion = []
            assignations = get_assignations(project, period, 'Student').select(db.user_project.ALL)
            for assignation in assignations:
                reports = db(db.report.assignation == assignation.id).select()
                for report in reports:
                    if obtain_period_report(report) == period:
                        assigned.append(report.desertion_started)
            
            if assignations.first() is not None:
                desertion_assignation = assignations.first()
                desertion_reports = db(db.report.assignation == desertion_assignation.id).select()
                for report in desertion_reports:
                    if obtain_period_report(report) == period:
                        if report.desertion_gone is not None:
                            if report.desertion_gone:
                                desertion.append(report.desertion_gone)
            
            assigned = [element_assigned for element_assigned in assigned if element_assigned is not None]
            if len(assigned) > 0:
                assigned = max(assigned)
            else:
                assigned = T('Pending')

            desertion = [element_desertion for element_desertion in desertion if element_desertion is not None]
            if len(desertion) > 0:
                desertion = sum(desertion)
            else:
                desertion = T('Pending')

            return desertion, assigned
        
        def count_student_hours(project):
            resp = []
            assignations = get_assignations(project, period, 'Student' \
                ).select(db.user_project.ALL)
            for assignation in assignations:
                hours = 0
                reports = db(db.report.assignation==assignation.id
                    ).select()
                for report in reports:
                    if report.hours != None:
                        hours += report.hours
                sub_response = [assignation.assigned_user.first_name +\
                    ' ' + assignation.assigned_user.last_name + \
                    ', ' + assignation.assigned_user.username, hours]
                resp.append(sub_response)
            return resp

        def current_teacher(project):
            teacher = get_assignations(project, period, 'Teacher'
                ).select(db.auth_user.ALL).first()
            name = T('Pending')
            if teacher != None:
                name = teacher.first_name + ' ' + teacher.last_name
            return name

        return dict(projects=projects, count_assigned=count_assigned,
            current_teacher=current_teacher,
            count_assigned_students=count_assigned_students,
            count_student_hours=count_student_hours,
            periods=periods,
            area=area, period=period)
    else:
        session.flash = "Action not allowed"
        redirect(URL('default','home'))

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def active_teachers():
    period = cpfecys.current_year_period()

    if request.vars['period'] is not None:
        period = request.vars['period']
        period = db(db.period_year.id == period).select().first()
        if not period:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
    
    if request.args(0) == 'toggle':
        enabled = ''
        user = request.vars['user']
        user = db(db.auth_user.id == user).select(db.auth_user.registration_key, db.auth_user.id).first()
        if user is None:
            session.flash = T("No existing user")
            redirect(URL('admin', 'active_teachers'))
        
        if user.registration_key != 'blocked':
            enabled = 'blocked'
        user.update_record(registration_key=enabled)
        redirect(URL('admin', 'active_teachers'))
    elif request.args(0) == 'mail':
        user = request.vars['user']
        if user is None:
            session.flash = T("No existing user")
            redirect(URL('admin','active_teachers'))
        
        user = db(db.auth_user.id == user).select(
                db.auth_user.id,
                db.auth_user.email,
                db.auth_user.username
            ).first()
        if user is None:
            session.flash = T("No existing user")
            redirect(URL('admin','active_teachers'))

        recovery = f'{cpfecys.get_domain()}default/user/request_reset_password?_next=/cpfecys/default/index'
        message = f"""
            Bienvenido a CPFECYS, su usuario es {user.username} 
            para generar su contraseña puede visitar el siguiente enlace e 
            ingresar su usuario {recovery}
        """
        subject = 'DTT-ECYS Bienvenido'
        send_mail_to_users([user], message, None, None, subject, None)
        user.update_record(load_alerted=True)
    elif request.args(0) == 'notifyall':
        users = get_assignations(False, period, 'Teacher').select(
                    db.auth_user.id,
                    db.auth_user.email,
                    db.auth_user.username,
                    distinct=True
                )
        recovery = f'{cpfecys.get_domain()}default/user/request_reset_password?_next=/cpfecys/default/index'
        subject = 'DTT-ECYS Bienvenido'
        for user in users:
            message = f"""
                Bienvenido a CPFECYS, su usuario es {user.username}
                para generar su contraseña puede visitar el siguiente enlace e 
                ingresar su usuario {recovery}
            """
            send_mail_to_users([user], message, None, None, subject, None)
            user.update_record(load_alerted=True)
    elif request.args(0) == 'notifypending':
        project = False
        users = db((db.auth_user.id == db.user_project.assigned_user) & (db.auth_user.id == db.auth_membership.user_id)
                & (db.auth_user.load_alerted == None) & (db.auth_membership.group_id == db.auth_group.id)
                & (db.auth_group.role == 'Teacher') & (project==False or (db.user_project.project == project))
                & (db.project.area_level == db.area_level.id) & (db.user_project.project == db.project.id)
                & (db.user_project.period == db.period_year.id) & ((db.user_project.period <= period.id)
                & ((db.user_project.period.cast('integer') + db.user_project.periods) > period.id))).select(
                    db.auth_user.id,
                    db.auth_user.email,
                    db.auth_user.username,
                    distinct=True
                )
        recovery = f'{cpfecys.get_domain()}default/user/retrieve_username?_next=/cpfecys/default/index'
        subject = 'DTT-ECYS Bienvenido'
        for user in users:
            message = f"""
                Bienvenido a CPFECYS, su usuario es {user.username} 
                para generar su contraseña puede visitar el siguiente enlace e 
                ingresar su usuario {recovery}
            """
            send_mail_to_users([user], message, None, None, subject, None)
            user.update_record(load_alerted=True)

    assignations = get_assignations(False, period, 'Teacher').select(
        db.user_project.ALL,
        orderby=db.area_level.name | db.project.name
                | db.auth_user.last_name | db.auth_user.first_name
    )

    periods = db(db.period_year).select(orderby=~db.period_year.id)
    go_to_academic = False
    try:
        if request.vars['next'] == "academic" :
            go_to_academic = True
    except:
        ...

    if go_to_academic:
        redirect(URL('student_academic','academic'))
    
    return dict(periods=periods, assignations=assignations, actual_period=period)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def get_assignations(project, period, role):
    assignations = db(
                    (db.auth_user.id==db.user_project.assigned_user)&
                    (db.auth_user.id==db.auth_membership.user_id)&
                    (db.auth_membership.group_id==db.auth_group.id)&
                    (db.auth_group.role==role)&
                    (project==False or (db.user_project.project==project))&
                    (db.project.area_level==db.area_level.id)&
                    (db.user_project.project==db.project.id)&
                    (db.user_project.period == db.period_year.id)&
                    ((db.user_project.period <= period.id)&
                 ((db.user_project.period.cast('integer') + db.user_project.periods) > \
                  period.id))
                    )
    return assignations

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def courses_report_detail():
    period = cpfecys.current_year_period()
    periods = db(db.period_year).select()
    if request.vars['period'] != None:
        period = request.vars['period']
        period = db(db.year_period.id==period).select().first()
    if request.vars['project'] == None:
        session.flash = "Action not allowed"
        redirect(URL('admin','courses_report/areas'))
    project = request.vars['project']
    assignations = db(
                    (db.auth_user.id==db.user_project.assigned_user)&
                    (db.auth_user.id==db.auth_membership.user_id)&
                    (db.auth_membership.group_id==db.auth_group.id)&
                    (db.auth_group.role=='Student')&
                    (db.user_project.project==project)&
                    (db.user_project.period == db.period_year.id)&
                    ((db.user_project.period <= period)&
                 ((db.user_project.period.cast('integer') + db.user_project.periods) > \
                  period))
                    )._select()
    return assignations
    return dict(periods=periods, project=project,
        period=period)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def mail_notifications():
    period = cpfecys.current_year_period()
    attachment_list = request.vars['attachment_list']
    message = request.vars['message']
    subject = request.vars['subject']
    cc = request.vars['cc']

    files_attach = []
    if attachment_list is not None:
        if isinstance(attachment_list, str):
            attachment_list = [attachment_list]
        for file_var in attachment_list:
            files_attach.append(file_var)

    #emarquez: logica de periodos
    period_param = request.vars['period'] or False
    if period_param:
        if period_param != '0':
            period = db(db.period_year.id ==  int(period_param)).select().first()

    #emarquez: verificar si es periodo variable
    is_variable = False

    #emarquez: busca registros de periodo variable, asociado a period asociado a period_detail, si lo encuentra es variable
    if db((db.period.id==period.period)&(db.period_detail.period==db.period.id)).select():
        is_variable= True


    #lastsql = db._lastsql
    lastsql = is_variable


    if (request.args(0) == 'send'):
        roles = request.vars['role']
        projects = request.vars['project']        

        if isinstance(roles, str):
            roles = [roles]

        if projects != None and isinstance(projects, str):
            projects = [projects]

        if projects  != None  and roles != None:
            for role in request.vars['role']:
                role = db(db.auth_group.id==role).select().first()

                if role.role == 'DSI':
                    users = db(
                        (db.auth_user.id==db.auth_membership.user_id)&
                        (db.auth_membership.group_id==db.auth_group.id)&
                        (db.auth_group.role=='DSI'))
                    group_id = users.select().first().auth_group.id
                    dsi_role = [group_id]
                    send_mail_to_users(users.select(db.auth_user.ALL),
                        message, dsi_role, projects,
                        subject,files_attach)
                else:
                    if role.role == 'Academic':
                        users = db(
                            (db.auth_user.id==db.auth_membership.user_id)&
                            (db.auth_membership.group_id==db.auth_group.id)&
                            (db.auth_group.id.belongs(roles))&
                            #Until here we get users from role
                            (db.academic_course_assignation.assignation.belongs(projects))&
                            (db.academic.id==db.academic_course_assignation.carnet)&
                            (db.auth_user.id==db.academic.id_auth_user)&
                            #Until here we get users from role assigned to projects
                            (db.academic_course_assignation.semester==period.id)
                            )

                    elif role.role == 'Student':

                        users = db(
                            (db.auth_user.id==db.auth_membership.user_id)&
                            (db.auth_membership.group_id==db.auth_group.id)&
                            (db.auth_group.id == role.id)&
                            #Until here we get users from role
                            (db.user_project.project.belongs(projects))&
                            (db.auth_user.id==db.user_project.assigned_user)&
                            #Until here we get users from role assigned to projects
                            (db.user_project.period==db.period_year.id)&
                            ( (db.user_project.assignation_status==None)|
                              ((db.user_project.period <= period.id)&
                              ((db.user_project.period.cast('integer') + db.user_project.periods) > \
                              period.id)) )
                            )

                        #emarquez: verificando si es variable para cambiar el query
                        if is_variable:
                            users = db(
                                (db.auth_user.id==db.auth_membership.user_id)&
                                (db.auth_membership.group_id==db.auth_group.id)&
                                (db.auth_group.id == role.id)&
                                #Until here we get users from role
                                (db.user_project.project.belongs(projects))&
                                (db.auth_user.id==db.user_project.assigned_user)&
                                #Until here we get users from role assigned to projects
                                (db.user_project.period==db.period_year.id)&
                                ( (db.user_project.assignation_status==None) | ((db.user_project.period == period.id) ) )
                                )

                    elif role.role == 'Teacher':
                        users = db(
                            (db.auth_user.id==db.auth_membership.user_id)&
                            (db.auth_membership.group_id==db.auth_group.id)&
                            (db.auth_group.id == role.id)&
                            #Until here we get users from role
                            (db.user_project.project.belongs(projects))&
                            (db.auth_user.id==db.user_project.assigned_user)&
                            #Until here we get users from role assigned to projects
                            (db.user_project.period==db.period_year.id)&
                            ( ((db.user_project.period <= period.id)&
                              ((db.user_project.period.cast('integer') + db.user_project.periods) > \
                              period.id)) )
                            )

                        #emarquez: verificando si es variable para cambiar el query
                        if is_variable:
                            users = db(
                                (db.auth_user.id==db.auth_membership.user_id)&
                                (db.auth_membership.group_id==db.auth_group.id)&
                                (db.auth_group.id == role.id)&
                                #Until here we get users from role
                                (db.user_project.project.belongs(projects))&
                                (db.auth_user.id==db.user_project.assigned_user)&
                                #Until here we get users from role assigned to projects
                                (db.user_project.period==db.period_year.id)&
                                ( (db.user_project.assignation_status==None) | ((db.user_project.period == period.id) ) )
                                )


                    #return users._select(db.auth_user.ALL, distinct=True)
                    users = users.select(db.auth_user.ALL, distinct=True)
                    #return users
                    send_mail_to_users(users, message, \
                        roles, projects, subject,files_attach, True, cc)

            session.flash = T('Mail successfully sent')
            redirect(URL('admin', 'mail_notifications'))
        elif (roles != None) and (len(roles) == 1):
            for role in roles:
                role = db(db.auth_group.id==role).select().first()
                if role.role == 'DSI':
                    users = db(
                        (db.auth_user.id==db.auth_membership.user_id)&
                        (db.auth_membership.group_id==db.auth_group.id)&
                        (db.auth_group.role=='DSI'))
                    group_id = users.select().first().auth_group.id
                    dsi_role = [group_id]
                    send_mail_to_users(users.select(db.auth_user.ALL),
                        message, dsi_role, projects,
                        subject,files_attach, False, cc)
        else:
            session.flash = T('At least a project and a role must be selected')
            redirect(URL('admin', 'mail_notifications'))

    upload_form = FORM(INPUT(_name='file_name',_type='text'),
                        INPUT(_name='file_upload',_type='file'),
                        INPUT(_name='file_visible',_type='checkbox'),
                        INPUT(_name='file_public',_type='checkbox'))
    if upload_form.accepts(request.vars,formname='upload_form'):
        try:
            if ( upload_form.vars.file_name is "" ) or ( upload_form.vars.file_upload is "") or ( upload_form.vars.file_description is ""):
                response.flash = T('You must enter all fields.')
            else:
                exists = db.uploaded_file((db.uploaded_file.name == upload_form.vars.file_name))
                if exists is None:
                    file_var = db.uploaded_file.file_data.store(upload_form.vars.file_upload.file, upload_form.vars.file_upload.filename)

                    var_visible = False
                    if upload_form.vars.file_visible:
                        var_visible = True
                    var_public = False
                    if upload_form.vars.file_public:
                        var_public = True

                    upload_file = db.uploaded_file.insert(file_data=file_var,
                                            name=upload_form.vars.file_name,
                                            visible=var_visible,
                                            is_public=var_public
                                            )
                    files_attach.append(upload_file)
                    response.flash = T('File loaded successfully.')
                else:
                    response.flash = T('File already exists.')
        except:
            response.flash = T('Error loading file.')


    attach_form = FORM(INPUT(_name='check_files',_type='checkbox'))

    if attach_form.accepts(request.vars,formname='attach_form'):
        check_files = attach_form.vars.check_files
        if isinstance(check_files, str):
            check_files = [check_files]
        for file_var in check_files:
            files_attach.append(file_var)


    groups = db(db.auth_group.role!='Super-Administrator').select()
    areas = db(db.area_level).select()
    def get_projects(area):
        courses = db(db.project.area_level==area.id)
        return courses
    def prepare_name(name):
        name = name.lower()
        name = name.replace(' ', '-')
        return name

    if subject is None:
        subject = ""
    if message is None:
        message = ""
    if cc is None:
        cc = ""
    return dict(groups=groups,
        areas=areas,
        get_projects=get_projects,
        prepare_name=prepare_name,
        markmin_settings = cpfecys.get_markmin,
        attachment_list = files_attach,
        subject=subject,
        message=message, last=lastsql, cc=cc)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def mail_log():
    logs = db(db.mail_log).select()
    return dict(logs=logs)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def send_mail_to_users(users, message, roles, projects, subject, attachment_list, log=False, cc=''):
    if log:
        cdate = datetime.now()
        roles = db(db.auth_group.id.belongs(roles)).select()
        projects = db(db.project.id.belongs(projects)).select()
        roles_text = ''
        projects_text = ''
        for role in roles:
            roles_text = roles_text + ',' + role.role
            pass
        for project in projects:
            projects_text = projects_text + ', ' + project.name
            pass
        db.mail_log.insert(sent_message=message,
            roles=roles_text[1:],
            projects=projects_text[1:],
            sent=cdate)
    attachment_m = ''
    try:
        attachment_m = '<br><br><b>' + T('Attachments') +":</b><br>"
        if attachment_list != []:
            for attachment_var in db(db.uploaded_file.id.belongs(attachment_list)).select():
                attachment_m = attachment_m + '<a href="' + cpfecys.get_domain() + URL('default/download', attachment_var.file_data) +'" target="blank"> '+ attachment_var.name + '</a> <br>'
        else:
            attachment_m = ''
    except:
        attachment_m = ''

    message = message.replace("\n","<br>")
    message = '<html>' + message + '<br>'+ (cpfecys.get_custom_parameters().email_signature or '') + attachment_m + '</html>'

    user_list= []
    for user in users:
        if user.email != None and user.email != '':
            user_list.append(user.email)

    #agrego los correos de cc
    if cc != '':
        arr_cc = cc.split(";")
        for item_cc in arr_cc:
            user_list.append(item_cc)
        pass
    pass

    if user_list != '':
        was_sent = mail.send(to='dtt.ecys@dtt-dev.site',
          subject=subject,
          message=message,
          bcc=user_list)
        #MAILER LOG
        db.mailer_log.insert(sent_message = message,
                     destination = str(user_list),
                     result_log = str(mail.error or '') + ':' + \
                     str(mail.result),
                     success = was_sent)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def anomalies_list():
    cperiod = cpfecys.current_year_period()
    year = str(cperiod.yearp)
    if cperiod.period == 1:
        start = datetime.strptime(year + '-01-01', "%Y-%m-%d")
        end = datetime.strptime(year + '-06-01', "%Y-%m-%d")
    else:
        start = datetime.strptime(year + '-06-01', "%Y-%m-%d")
        end = datetime.strptime(year + '-12-31', "%Y-%m-%d")

    def get_month_name(date):
        if date==0:
            return "Invalid"
        fecha = datetime.strptime('2000-'+str(date)+'-01',"%Y-%m-%d")
        return fecha.strftime("%B")
    
    count = db.log_entry.id.count()

    if (request.args(0) == 'view'):
        period = request.vars['period']
        valid = period != None
        if not valid:
            session.flash = T('Incomplete Information')
            redirect(URL('default', 'home'))
        anomalies = db.executesql(queries.q_anomalies_list_view().format(str(period)))
        return dict(anomalies=anomalies,
            get_month_name=get_month_name,
            period=period)

    elif (request.args(0) == 'periods'):
        response.view = 'admin/anomaly_periods_dcos.html'
        resultado =  db.executesql(queries.q_anomalies_list())
        return dict(periods=resultado)

    elif (request.args(0) == 'show'):
        project = request.vars['project']
        period = request.vars['period']
        month = request.vars['month']
        valid = project != None and period != None and month != None        
        if not valid:
            session.flash = T('Incomplete Information')
            redirect(URL('default', 'home'))
        anomalies = db.executesql(queries.q_anomalies_list_show().format(str(period),str(project),str(month)))
        response.view = 'admin/anomaly_show.html'
        return dict(anomalies=anomalies)

#EPS DANIEL COS
@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def report_list_dcos():
    response.view = 'admin/report_list_dcos.html'
    
    periods = db.executesql(queries.q_report_list(), as_dict=True)
    count = db.report.id.count()
    report_total = db().select(
        db.report_status.ALL, count,
        left=db.report.on((db.report.status==db.report_status.id)),
        groupby=db.report_status.name,
        orderby=db.report_status.order_number)

    return dict(periods=periods,
        report_total=report_total)

#ESTE METODO FUE REEMPLAZADO POR EL METODO report_list_dcos
#NO SE ELIMINO POR POSIBLES USOS EN OTRAS PARTES DEL CODIGO
@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def report_list():
    response.view = 'admin/report_list.html'
    period_year = db(db.period_year).select(orderby=~db.period_year.id)
    def count_reproved(pyear):
        year = str(pyear.yearp)
        if pyear.period == 1:
            start = datetime.strptime(year + '-01-01', "%Y-%m-%d")
            end = datetime.strptime(year + '-06-01', "%Y-%m-%d")
        else:
            start = datetime.strptime(year + '-06-01', "%Y-%m-%d")
            end = datetime.strptime(year + '-12-31', "%Y-%m-%d")
        reports = db((db.report.created>start)&
            (db.report.created<end)&
            (db.report.score < db.report.min_score)&
            (db.report.never_delivered==None
                or db.report.never_delivered==False))
        return reports.count()

    def count_approved(pyear):
        year = str(pyear.yearp)
        if pyear.period == 1:
            start = datetime.strptime(year + '-01-01', "%Y-%m-%d")
            end = datetime.strptime(year + '-06-01', "%Y-%m-%d")
        else:
            start = datetime.strptime(year + '-06-01', "%Y-%m-%d")
            end = datetime.strptime(year + '-12-31', "%Y-%m-%d")
        reports = db((db.report.created<end)&
            (db.report.created>start)&
            ((db.report.score>=db.report.min_score) |
                (db.report.admin_score>=db.report.min_score))&
            (db.report.min_score!=None)&
            (db.report.min_score!=0))
        return reports.count()

    def count_approved_pendingDTT(pyear):
        year = str(pyear.yearp)
        if pyear.period == 1:
            start = datetime.strptime(year + '-01-01', "%Y-%m-%d")
            end = datetime.strptime(year + '-06-01', "%Y-%m-%d")
        else:
            start = datetime.strptime(year + '-06-01', "%Y-%m-%d")
            end = datetime.strptime(year + '-12-31', "%Y-%m-%d")
        reports = db((db.report.created<end)&
            (db.report.created>start)&
            (db.report.score!=None)&
            ((db.report.score>=db.report.min_score) |
                (db.report.admin_score>=db.report.min_score))&
            (db.report.min_score!=None)&
            (db.report.min_score!=0)&
            (db.report.dtt_approval == None))
        return reports.count()
    
    def count_no_created(pyear):
        year = str(pyear.yearp)
        if pyear.period == 1:
            start = datetime.strptime(year + '-01-01', "%Y-%m-%d")
            end = datetime.strptime(year + '-06-01', "%Y-%m-%d")
        else:
            start = datetime.strptime(year + '-06-01', "%Y-%m-%d")
            end = datetime.strptime(year + '-12-31', "%Y-%m-%d")
        cperiod = cpfecys.current_year_period()
        restrictions = db((db.report_restriction.start_date>=start)&
            (db.report_restriction.end_date<=end)&
            (db.report_restriction.is_enabled==True)).select()
        pending = 0
        assignations = get_assignations(False, pyear, 'Student').select()
        for assignation in assignations:
            for restriction in restrictions:
                report = db(
                    (db.report.assignation==assignation.user_project.id)&
                    (db.report.report_restriction==restriction.id)&
                    (db.report.report_restriction==db.report_restriction.id)
                    ).select(db.report.ALL).first()
                if report == None:
                    pending += 1
                #esto es para no ver drafts en no_created del report_filter
                #else:
                #    hours = report.hours
                #    entries = count_log_entries(\
                #        report.id)[0]['COUNT(log_entry.id)']
                #    metrics = count_metrics_report(\
                #        report.id)[0]['COUNT(log_metrics.id)']
                #    anomalies = count_anomalies(\
                #        report)[0]['COUNT(log_entry.id)']
                #    if assignation.user_project.project.area_level.name == \
                #            'DTT Tutor Académico':
                #        if entries == 0 and metrics == 0 and anomalies == 0:
                #            pending += 1
                #    else:
                #        if hours == None and hours == 0:
                #            pending += 1

        return pending

    def count_acceptance(pyear):
        year = str(pyear.yearp)
        total = 0
        string = ''
        if pyear.period == 1:
            start = datetime.strptime(year + '-01-01', "%Y-%m-%d")
            end = datetime.strptime(year + '-06-01', "%Y-%m-%d")
        else:
            start = datetime.strptime(year + '-06-01', "%Y-%m-%d")
            end = datetime.strptime(year + '-12-31', "%Y-%m-%d")
        reports = db((db.report.created>= start)&
            (db.report.created<=end)&
            (db.report.status==db.report_status(name='Acceptance'))).select()
        array = []
        for report in reports:
            hours = report.hours
            entries = count_log_entries(report)
            metrics = count_metrics_report(report)
            anomalies = count_anomalies(report)[0]['_extra']['COUNT(`log_entry`.`id`']
            string = string + str(entries) + ' ' + str(metrics) + ' ' +str(anomalies) + '<br/>'
            if report.assignation.project.area_level.name == \
                    'DTT Tutor Académico':
                if entries != 0 or metrics != 0 or anomalies != 0:
                    total += 1
            else:
                if hours != None:
                    total += 1
        return total

    def count_draft(pyear):
        year = str(pyear.yearp)
        total = 0
        string = ''
        if pyear.period == 1:
            start = datetime.strptime(year + '-01-01', "%Y-%m-%d")
            end = datetime.strptime(year + '-06-01', "%Y-%m-%d")
        else:
            start = datetime.strptime(year + '-06-01', "%Y-%m-%d")
            end = datetime.strptime(year + '-12-31', "%Y-%m-%d")
        reports = db((db.report.created>= start)&
            (db.report.created<=end)&
            (db.report.status==db.report_status(name='Draft'))).select()
        for report in reports:
            hours = report.hours
            #***********************************************************************************************************************
            #******************************************************PHASE 2 DTT******************************************************
            entries = count_log_entries(report)
            metrics = count_metrics_report(report)
            anomalies = count_anomalies(report)[0]['_extra']['COUNT(`log_entry`.`id`)']
            string = string + str(entries) + ' ' + str(metrics) + ' ' +str(anomalies) + '<br/>'
            if report.assignation.project.area_level.name == \
                    'DTT Tutor Académico':
                if entries != 0 or metrics != 0 or anomalies != 0:
                            total += 1
            #***********************************************************************************************************************
            #******************************************************PHASE 2 DTT******************************************************
            else:
                if hours != None and hours != 0:
                    total += 1
        return total

    def count_no_delivered(pyear):
        year = str(pyear.yearp)
        if pyear.period == 1:
            start = datetime.strptime(year + '-01-01', "%Y-%m-%d")
            end = datetime.strptime(year + '-06-01', "%Y-%m-%d")
        else:
            start = datetime.strptime(year + '-06-01', "%Y-%m-%d")
            end = datetime.strptime(year + '-12-31', "%Y-%m-%d")
        reports = db((db.report_restriction.start_date>=start)&
            (db.report_restriction.end_date<=end)&
            (db.report.report_restriction==db.report_restriction.id)&
            (db.report.never_delivered == True)&
            (db.user_project.id==db.report.assignation)&
            (db.auth_user.id==db.user_project.assigned_user)&
            (db.auth_membership.user_id==db.auth_user.id)&
            (db.auth_group.id==db.auth_membership.group_id)&
            (db.auth_group.role=='Student'))
        return reports.count()
    
    def count_reports(pyear, status, exclude):
        year = str(pyear.yearp)
        if pyear.period == 1:
            start = datetime.strptime(year + '-01-01', "%Y-%m-%d")
            end = datetime.strptime(year + '-06-01', "%Y-%m-%d")
        else:
            start = datetime.strptime(year + '-06-01', "%Y-%m-%d")
            end = datetime.strptime(year + '-12-31', "%Y-%m-%d")
        count = db.report.id.count()
        report_total = db().select(
            db.report_status.ALL, count,
            left=db.report.on((db.report.status==db.report_status.id)&
                (db.report.created < end)&
                (db.report.created > start)&
                ((status==False) or (db.report_status.name==status))),
            groupby=db.report_status.name,
            orderby=db.report_status.order_number)
        return report_total

    count = db.report.id.count()
    report_total = db().select(
        db.report_status.ALL, count,
        left=db.report.on((db.report.status==db.report_status.id)),
        groupby=db.report_status.name,
        orderby=db.report_status.order_number)
    return dict(period_year=period_year,
        report_total=report_total,
        count_reproved=count_reproved,
        count_approved=count_approved,
        count_no_created=count_no_created,
        count_reports=count_reports,
        count_draft=count_draft,
        count_no_delivered=count_no_delivered,
        count_acceptance=count_acceptance,
        count_approved_pendingDTT=count_approved_pendingDTT)

#EPS DANIEL COS
@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def report_filter_dcos():
    period = request.vars['period']
    status = request.vars['status']
    name = request.vars['name']
    try:
        if(period!=None and status==None): #REPORTE POR PERIODO
            reports = db.executesql(queries.q_report_filter(0).format(period), as_dict=True)
        elif (period!=None and status!=None):
            if(int(status)>=0): #Estados
                reports = db.executesql(queries.q_report_filter(1).format(period,status), as_dict=True)
            elif(status=="-1"): #APROBADOS
                reports = db.executesql(queries.q_report_filter(2).format(period), as_dict=True)        
            elif(status=="-2"): #REPROBADOS
                reports = db.executesql(queries.q_report_filter(3).format(period), as_dict=True)
            elif(status=="-3"): #APROBADO DTT
                reports = db.executesql(queries.q_report_filter(4).format(period), as_dict=True)
            elif(status=="-4"): #PENDIENTE DTT
                reports = db.executesql(queries.q_report_filter(5).format(period), as_dict=True)
            elif(status=="-5"): #ENTREGADOS
                reports = db.executesql(queries.q_report_filter(6).format(period), as_dict=True)
            elif(status=="-6"): #NO ENTREGADOS
                reports = db.executesql(queries.q_report_filter(7).format(period), as_dict=True)
            elif(status=="-7"): #PENDIENTES
                reports = db.executesql(queries.q_report_filter(8).format(period), as_dict=True)
                #INIT Check if there is a pending report has created
                cperiod = db(db.period_year.id==request.vars['period']).select().first()

                if request.vars['report'] != None and request.vars['assignation'] != None:
                    #Check for restriction exists and is valid
                    rr_id = db((db.report_restriction.is_enabled==True)&
                        (db.report_restriction.id==int(request.vars['report']))).select().first()
                    if rr_id is None:
                        session.flash = T('Incomplete Information')
                        print('uno')
                        redirect(URL('admin', 'report_filter_dcos',vars=dict(status = request.vars['status'], period = request.vars['period'])))
                    #Verify that the user exists and is student specific period
                    assignations_id = db(
                            (db.auth_user.id==db.user_project.assigned_user)&
                            (db.auth_user.id==db.auth_membership.user_id)&
                            (db.auth_membership.group_id==db.auth_group.id)&
                            (db.auth_group.role=='Student')&
                            (db.user_project.id==int(request.vars['assignation']))&
                            (db.user_project.period == db.period_year.id)&
                            ((db.user_project.period <= cperiod.id)
                            )).select().first()
                    if assignations_id is None:
                        session.flash = T('Incomplete Information')
                        print('dos')
                        redirect(URL('admin', 'report_filter_dcos',vars=dict(status = request.vars['status'], period = request.vars['period'])))

                    #Verify that the specified user does not have a report from the constraint specified
                    report_delivered = db((db.report.report_restriction==int(request.vars['report']))&(db.report.assignation==int(request.vars['assignation']))).select().first()
                    if report_delivered is not None:
                        session.flash = T('Incomplete Information')
                        print('tres')
                        redirect(URL('admin', 'report_filter_dcos',vars=dict(status = request.vars['status'], period = request.vars['period'])))

                    #Create the report and place it in draft status so that you can edit the student
                    status_draft = db.report_status(db.report_status.name == 'Draft')
                    current_date = datetime.now().date()
                    new_report = db.report.insert(created = rr_id.end_date,
                                         assignation = int(request.vars['assignation']),
                                         report_restriction = rr_id.id,
                                         admin_score = cpfecys.get_custom_parameters().min_score,
                                         min_score = cpfecys.get_custom_parameters().min_score,
                                         status = status_draft,
                                         admin_comment =  T('Created by admin'),
                                         score_date=current_date,
                                         dtt_approval=True,
                                         never_delivered=False)
                    if new_report.assignation.project.area_level.name=='DTT Tutor Académico' and new_report.report_restriction.is_final==True:
                        #CREATE THE FINAL METRICS
                        cperiod = obtainPeriodReport(new_report)
                        final_metrics = final_metric(cperiod,new_report)
                        try:
                            average=float((final_metrics[22]*100)/final_metrics[20])
                        except:
                            average=float(0)
                        db.log_final.insert(curso_asignados_actas=int(final_metrics[0]),
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
                                            report=new_report.id
                                            )

                    #Report by email to the academic tutor who can edit your report
                    user = new_report.assignation.assigned_user
                    subject = T('[DTT]Automatic Notification - Report created ') \
                    +T('BY ADMIN USER')
                    signat = cpfecys.get_custom_parameters().email_signature or ''
                    cstatus = db(db.report_status.id==new_report.status).select().first()
                    message = '<html>' + T('You have created the report') + ' ' \
                    + '<b>' + XML(new_report.report_restriction.name) + '</b>.<br/>' \
                    + T('The report is set to Draft status. You can proceed to edit the report.') \
                    +'<br/>' \
                    + T('DTT-ECYS') \
                    + ' ' + cpfecys.get_domain() + '<br />' + signat + '</html>'
                    was_sent = mail.send(to=user.email,
                      subject=subject,
                      message=message)
                    #MAILER LOG
                    db.mailer_log.insert(sent_message = message,
                                 destination = str(user.email),
                                 result_log = str(mail.error or '') + ':' + str(mail.result),
                                 success = was_sent)



                    session.flash = T('You have created the report and has notified the academic tutor by email')
                    redirect(URL('admin', 'report/view',vars=dict(report = new_report.id)))
                elif request.vars['report'] != None or request.vars['assignation'] != None:
                    session.flash = T('Incomplete Information')
                    print('cuatro')
                    redirect(URL('admin', 'report_filter_dcos',vars=dict(status = request.vars['status'], period = request.vars['period'])))
                #END Check if there is a pending report has created
            else:
                reports=[]
        else:
            session.flash = T('Incomplete Information')
            redirect(URL('default', 'home'))
    except ValueError:
        reports = []

    def count_log_entries(report_id): #CONTEO DE ACTIVIDADES
        report = db(db.report.id == report_id).select().first()
        if report.assignation.project.area_level.name=='DTT Tutor Académico' and (report.status.name=='Draft' or report.status.name=='Recheck'):
            activities_tutor = activities_report_tutor(report)
            print(activities_tutor)
            log_entries=len(activities_tutor['activities_wm'])+len(activities_tutor['activities_m'])
        else:
            #TODO PREGUNTAR
            #print(db((db.log_entry.report == report.id)).select(db.log_entry.id.count())[0]['_extra']['COUNT(`log_entry`.`id`)'])
            #log_entries = db((db.log_entry.report==report.id)).select(db.log_entry.id.count())[0]['COUNT(log_entry.id)']
            log_entries = db((db.log_entry.report == report.id)).select(db.log_entry.id.count())[0]['_extra']['COUNT(`log_entry`.`id`)']
        return
        return log_entries
    def count_metrics_report(report_id): #CONTEO DE METRICAS
        report = db(db.report.id == report_id).select().first()
        if report.assignation.project.area_level.name=='DTT Tutor Académico' and (report.status.name=='Draft' or report.status.name=='Recheck'):
            activities_tutor = activities_report_tutor(report)
            log_metrics=len(activities_tutor['activities_m'])
        else:
            #TODO PREGUNTAR
            #print(db((db.log_metrics.report == report.id)).select(db.log_metrics.id.count())[0]['_extra']['COUNT(`log_metrics`.`id`)'])
            #log_metrics = db((db.log_metrics.report== report.id)).select(db.log_metrics.id.count())[0]['COUNT(log_metrics.id)']
            log_metrics = db((db.log_metrics.report == report.id)).select(db.log_metrics.id.count())[0]['_extra']['COUNT(`log_metrics`.`id`)']
        return log_metrics
    def count_anomalies(report_id): #CONTEO DE ANOMALIAS
        report = db(db.report.id == report_id).select().first()
        log_entries = db((db.log_entry.report== \
            report.id)&
        (db.log_entry.log_type==db.log_type(name='Anomaly')) \
        ).select(db.log_entry.id.count())
        return log_entries
    return dict(reports=reports,name=name,status=status,period=period,
        count_log_entries=count_log_entries,
        count_metrics_report=count_metrics_report,
        count_anomalies=count_anomalies)

#ESTE METODO FUE REEMPLAZADO POR EL METODO report_list_dcos
#NO SE ELIMINO POR POSIBLES USOS EN OTRAS PARTES DEL CODIGO
@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def report_filter():
    cperiod = cpfecys.current_year_period()
    if request.vars['period'] != None:
        cperiod = db(db.period_year.id==\
            request.vars['period']).select().first()
    year = str(cperiod.yearp)
    if cperiod.period == 1:
        start = datetime.strptime(year + '-01-01', "%Y-%m-%d")
        end = datetime.strptime(year + '-06-01', "%Y-%m-%d")
    else:
        start = datetime.strptime(year + '-06-01', "%Y-%m-%d")
        end = datetime.strptime(year + '-12-31', "%Y-%m-%d")
    status = request.vars['status']
    period = request.vars['period']
    valid = period != None
    def count_log_entries(report):
        #***********************************************************************************************************************
        #******************************************************PHASE 2 DTT******************************************************
        if report.assignation.project.area_level.name=='DTT Tutor Académico' and (report.status.name=='Draft' or report.status.name=='Recheck'):
            activitiesTutor = activities_report_tutor(report)
            log_entries=len(activitiesTutor['activities_wm'])+len(activitiesTutor['activities_m'])
        else:
            #TODO CAMBIO
            #log_entries = db((db.log_entry.report==report.id)).select(db.log_entry.id.count())[0]['COUNT(log_entry.id)']
            log_entries = db((db.log_entry.report == report.id)).select(db.log_entry.id.count())[0]['_extra']['COUNT(`log_entry`.`id`)']
        return log_entries
        #***********************************************************************************************************************
        #******************************************************PHASE 2 DTT******************************************************
    def count_metrics_report(report):
        #***********************************************************************************************************************
        #******************************************************PHASE 2 DTT******************************************************
        if report.assignation.project.area_level.name=='DTT Tutor Académico' and (report.status.name=='Draft' or report.status.name=='Recheck'):
            activitiesTutor = activities_report_tutor(report)
            log_metrics=len(activitiesTutor['activities_m'])
        else:
            log_metrics = db((db.log_metrics.report== report.id)).select(db.log_metrics.id.count())[0]['COUNT(log_metrics.id)']
        return log_metrics
        #***********************************************************************************************************************
        #******************************************************PHASE 2 DTT******************************************************
    def count_anomalies(report):
        log_entries = db((db.log_entry.report== \
            report.id)&
        (db.log_entry.log_type==db.log_type(name='Anomaly')) \
        ).select(db.log_entry.id.count())
        return log_entries
    def calculate_ending_date(report):
        someday = date.today()
        otherday = someday + timedelta(days=8)
        date = datetime.strptime(str(report.assignation.period.yearp) + \
                '-01-01', "%Y-%m-%d")
        date += timedelta(days=(30*6)*report.assignation.periods)
        semester =''
        fecha = ''
        if report.assignation.period.period.id == 1:
            if report.assignation.periods % 2 == 0:
                semester = T('Second Semester')
            else:
                semester = T('First Semester')
            fecha = str(date.year) + '-' + str(semester)
        else:
            if report.assignation.periods % 2 == 0:
                semester = T('First Semester')
                fecha = str(date.year+1) + '-' + str(semester)
            else:
                semester = T('Second Semester')
                fecha = str(date.year) + '-' + str(semester)
        return fecha
    if not valid:
        session.flash = T('Incomplete Information')
        redirect(URL('default', 'home'))
    if not status:
        reports = db((db.report.created>start)&
            (db.report.created<end)).select(db.report.ALL)
        status_instance = False
    elif int(status) == -1:#Aprobados
        reports = db((db.report.created>start)&
            (db.report.created<end)&
            ((db.report.admin_score>=db.report.min_score) |\
             (db.report.score>=db.report.min_score))&
            (db.report.min_score!=None)&
            (db.report.min_score!=0)).select()
        status_instance = db(db.report_status.id==status).select().first()
    elif int(status) == -2:#Reprobados
        reports = db((db.report.created>start)&
            (db.report.created<end)&
            (db.report.score<db.report.min_score)&
            (db.report.min_score!=None)&
            (db.report.min_score!=0)&
            (db.report.never_delivered==None or
                db.report.never_delivered==False)).select()
        status_instance = db(db.report_status.id==status).select().first()
    elif int(status) == -3:#Pendientes
        

        result = []
        existing = []
        restrictions = db((db.report_restriction.start_date>=start)&
            (db.report_restriction.end_date<=end)&
            (db.report_restriction.is_enabled==True)).select()
        pending = 0
        assignations = get_assignations(False, cperiod, 'Student').select()
        for assignation in assignations:
            for restriction in restrictions:
                report = db(
                    (db.report.assignation==assignation.user_project.id)&
                    (db.report.report_restriction==restriction.id)&
                    (db.report.report_restriction==db.report_restriction.id)
                    ).select(db.report.ALL).first()
                if report == None:
                    temp = dict(assignation=assignation,
                        restriction=restriction)
                    result.append(temp)
                else:
                    hours = report.hours
                    entries = count_log_entries(report)
                    metrics = count_metrics_report(report)
                    anomalies = count_anomalies(report)[0]['_extra']['COUNT(`log_entry`.`id`)']
                    temp = dict(assignation=assignation,
                            restriction=restriction,
                            report=report)
                    if assignation.user_project.project.area_level.name == \
                            'DTT Tutor Académico':
                        if entries == 0 and metrics == 0 and anomalies == 0:
                            existing.append(temp)
                    else:
                        if hours == None:
                            existing.append(temp)
        response.view = 'admin/report_filter_pending.html'
        return dict(result=result, existing=existing,
            count_log_entries=count_log_entries,
            count_metrics_report=count_metrics_report,
            count_anomalies=count_anomalies,)


    elif int(status) == -4:#No entregados
        reports = db((db.report_restriction.start_date>=start)&
            (db.report_restriction.end_date<=end)&
            (db.report.report_restriction==db.report_restriction.id)&
            (db.user_project.id==db.report.assignation)&
            (db.auth_user.id==db.user_project.assigned_user)&
            (db.auth_membership.user_id==db.auth_user.id)&
            (db.auth_group.id==db.auth_membership.group_id)&
            (db.auth_group.role=='Student')&
            (db.project.id==db.user_project.project)&
            (db.report.never_delivered == True))
        status_instance = reports.select()
        response.view = 'admin/report_filter_never_delivered.html'
        return dict(status_instance=status_instance,
            count_log_entries=count_log_entries,
            count_metrics_report=count_metrics_report,
            count_anomalies=count_anomalies,
            status=status,
            period=period)
    elif int(status) == -5:#Pendientes DTT
        reports = db((db.report.created<end)&
            (db.report.created>start)&
            (db.report.score!=None)&
            ((db.report.score>=db.report.min_score) |
                (db.report.admin_score>=db.report.min_score))&
            (db.report.min_score!=None)&
            (db.report.min_score!=0)&
            (db.report.dtt_approval == None)).select()
        print(db._lastsql)
        status_instance = db(db.report_status.id==status).select().first()
    else:
        reports = db((db.report.created>start)&
            (db.report.created<end)&
            (db.report.status==status)).select(db.report.ALL)
        status_instance = db(db.report_status.id==status).select().first()
    return dict(reports=reports,
        count_log_entries=count_log_entries,
        count_metrics_report=count_metrics_report,
        count_anomalies=count_anomalies,
        calculate_ending_date=calculate_ending_date,
        status = status,
        status_instance = status_instance,
        period = period)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def links():
    user = db(db.auth_membership.user_id== \
        auth.user.id).select(db.auth_group.ALL)
    grid = SQLFORM.smartgrid(db.link, linked_tables=['link_access'])
    return locals()

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def areas():
    grid = SQLFORM.grid(db.area_level)
    return locals()

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def files_manager():
    user = db(db.auth_membership.user_id==auth.user.id \
        ).select(db.auth_group.ALL)
    grid = SQLFORM.smartgrid(db.uploaded_file, linked_tables=['file_access'])
    return locals()

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def notifications_manager():
    user = db(db.auth_membership.user_id == auth.user.id \
        ).select(db.auth_group.ALL)
    grid = SQLFORM.smartgrid(db.front_notification,  \
        linked_tables=['notification_access'])
    return locals()

#LTZOC: Este metodo eliminara los menus existentes en db=3 redis, para crearlos nuevamente
@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def actualizar_menu():
    resultado = redis_db_3.flushdb()
    mensaje = 'Se actualizo el menu para todos los roles.' if resultado else\
              'Error al actualizar menu, verifique conexion en db(3) de redis.'
    session.flash = mensaje
    redirect(URL('default', 'home'))

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def items_manager():
    #LTZOC: Intruccion para limpiar menus almacenados en db=3 en redis
    redis_db_3.flushdb()
    periods_var = []

    #emarquez   
    periodo = cpfecys.current_year_period()
    periodo_parametro='off'
    period_list = []
    if request.vars['tipo_periodo']:
        periodo_parametro=request.vars['tipo_periodo']

    #busco los periodos normales
    print(periodo_parametro)
    if periodo_parametro == 'off':
        sub_query = db(db.period_detail.period)._select(db.period_detail.period)
        period_list = db((~db.period.id.belongs(sub_query))&(db.period_year.period==db.period.id)).select(orderby=~db.period_year.id)
    else:
        period_list = db((db.period.id==db.period_detail.period)&(db.period_year.period==db.period.id)).select()
        
    
    
    #if(auth.has_membership('Super-Administrator') or (auth.has_membership('Ecys-Administrator') & (ecys_var == True)) ):
    #    periods = db(db.period_year).select()

    cperiod = cpfecys.current_year_period()
    year = str(cperiod.yearp)

    if request.function == 'new':
        db.item.created.writable=db.item.created.readable=False

    periods = []
    for period in period_list:
        periods.append(period.period_year.id)

    grid = SQLFORM.smartgrid(db.item_restriction,
                             constraints={'item_restriction': (db.item_restriction.period.belongs(periods))},
                             linked_tables=['item_restriction_area', 'item_restriction_exception'])


    # *********** Inicio - Prácticas Finales (Digital Signature) - Fernando Reyes *************
    # *********** Se agrega link para asignación de firmas cuando se edita el entregable
    new_dict = {}
    if len(request.args) == 4:
        action_item = request.args[1]

        if action_item.strip() == 'edit':
            item_id = request.args[3]
            query = ds_utils.get_document_item(item_id.strip())
            document = db.executesql(query, as_dict=True)

            # validando que exista documento
            if len(document) < 1:
                session.flash = 'No existe entregable'
                redirect(URL('admin', 'items_manager'))

            if document[0]['item_type'] == 'File':
                new_dict['item_id'] = item_id.strip()

    # print db._lastsql
    return dict(grid=grid, year=year, action=new_dict)

    # *********** Fin - Prácticas Finales(DS) - Fernando Reyes *************

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def manage_items():
    if (request.args(0) == 'periods'):
        response.view = 'admin/manage_items_periods.html'
        #emarquez: orden de periodos
        periods = db(db.period_year).select(orderby=~db.period_year.id)
        return dict(periods=periods)
    elif (request.args(0) == 'area'):
        def count_items(area, period, disabled=False, enabled=False):
            if not(area and period):
                assignations = db(
                    (db.auth_user.id==db.user_project.assigned_user)&
                    (db.auth_user.id==db.auth_membership.user_id)&
                    (db.auth_membership.group_id==db.auth_group.id)&
                    (db.auth_group.role!='Teacher')).select(db.user_project.ALL)
                items = db((db.item.assignation.belongs(assignations))&
                    ((disabled==False)or(db.item.is_active==False))&
                    ((enabled==False)or(db.item.is_active==True)))
                return items
            else:
                projects = db(db.project.area_level==area).select()
                assignations = db((db.user_project.project.belongs(projects))&
                    (db.auth_user.id==db.user_project.assigned_user)&
                    (db.auth_user.id==db.auth_membership.user_id)&
                    (db.auth_membership.group_id==db.auth_group.id)&
                    (db.auth_group.role!='Teacher')).select(db.user_project.ALL)
                items = db((db.item.assignation.belongs(assignations))&
                    (db.item.created==period)&
                    ((disabled==False)or(db.item.is_active==False))&
                    ((enabled==False)or(db.item.is_active==True)))
                return items
        period = request.vars['period']
        areas = db(db.area_level).select()
        response.view = 'admin/manage_items_areas.html'
        return dict(areas=areas,
            period=period,
            count_items=count_items)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def delivered_download_button():
    if (request.args(0) == 'type'):
        response.view = 'admin/delivered_download.html'
        periods = db(db.period_year).select()
        return dict(periods=periods)

    elif (request.args(0) == 'zip'):
        def count_items(restriction, period, disabled=False, enabled=False):
            period = request.vars['period']
            cdate = datetime.now().date()
            restriction = request.vars['restriction']
            r_instance = db(db.item_restriction.id==1
                ).select(db.item_restriction.ALL)
            file_name = cdate + T('Deliverable Items')
            items = db((db.item.item_restriction==restriction)&
                (db.item.created==period)&
                (db.item.uploaded_file!=None)&
                (db.item.uploaded_file!='')).select()
            files = []
            for item in items:
                files.append(item.uploaded_file)
            if len(files) > 0:
                session.flash = T(str(item))
                return response.zip(request, files, db)
            session.flash = T('No files to download.')
            redirect(URL('admin', 'delivered_download/type',
                vars=dict(period=period)))

        period = request.vars['period']
        restrictions = db((db.item_restriction.is_enabled==True)&
            (db.item_restriction.name!='')&
            (db.item_restriction.id!=0)&
            (db.item_restriction.item_type==db.item_type(name='File')))
        restrictions = restrictions.select(db.item_restriction.ALL)
        response.view = 'admin/delivered_download_restrictions.html'
        return dict(restrictions=restrictions,period=period,count_items=count_items)

    elif (request.args(0) == 'dl'):
        period = request.vars['period']
        cdate = datetime.now().date()
        restriction = request.vars['restriction']
        r_instance = db(db.item_restriction.id==1
            ).select(db.item_restriction.ALL)
        file_name = cdate + T('Deliverable Items')
        items = db((db.item.item_restriction==restriction)&
            (db.item.created==period)&
            (db.item.uploaded_file!=None)&
            (db.item.uploaded_file!='')).select()
        files = []
        for item in items:
            files.append(item.uploaded_file)
        if len(files) > 0:
            response.headers['Content-Type'] = 'application/zip'
            response.headers['Content-Disposition'] = 'attachment; filename="files.zip"'
            ruta_uploads = os.path.join(request.folder, 'uploads')
            archivos = obtener_archivos_uploads(ruta_uploads, files)
            archivo_zip = os.path.join(request.folder, 'files.zip')
            with zipfile.ZipFile(archivo_zip, 'w') as zip_file:
                for archivo in archivos:
                    zip_file.write(archivo, os.path.basename(archivo))
            return response.stream(open(archivo_zip, 'rb'), attachment=True, filename='files.zip')
    return dict(restriction=restriction,period=period)

def obtener_archivos_uploads(ruta_uploads, files):
    archivos = []
    
    for archivo in files:
        ruta_completa = os.path.join(ruta_uploads, archivo)
        
        if os.path.isfile(ruta_completa):
            archivos.append(ruta_completa)
    
    return archivos

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def send_item_mail():
    user = request.vars['user']
    item = request.vars['item']
    success = False
    if not (not item and not user):
        user = db(db.auth_user.id==user).select().first()
        item = db(db.item.id==item).select().first()
        comment = item.admin_comment or T('No comment')
        subject = T('Item rejected by admin, please take action.')
        message = T('An item you created has been rejected by admin,') \
            + T('the reason is ') + comment \
            + T('please proceed to replace the item, if you don\'t take\
                any action the item will remain disabled.')
        message += (cpfecys.get_custom_parameters().email_signature or '')
        was_sent = mail.send(to=user.email,
                  subject=subject,
                  message=message)
        #MAILER LOG
        db.mailer_log.insert(sent_message = message,
                             destination = str(user.email),
                             result_log = str(mail.error or '') + ':' + str(mail.result),
                             success = was_sent)
        item.update_record(
            notified_mail = True)
        success = True

        # *********** Inicio - Prácticas Finales (Digital Signature) - Fernando Reyes *************
        query_item = ds_utils.get_item_delivered_by_item(item.id)
        item_delivered = db.executesql(query_item, as_dict=True)

        if len(item_delivered) > 0:
            item_res = db(db.item_restriction.id == item.item_restriction).select().first()

            values_log = {
                'document_name': item_res.name,
                'status': 'Rejected',
                'comment': item.admin_comment if item.admin_comment is not None else 'Sin comentario',
                'ref_delivered': item_delivered[0]['id'],
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'created_by': auth.user.username
            }

            try:
                insert_query = ds_utils.create_script_string('ds_item_delivered_log', 'I', values_log)
                db.executesql(insert_query)
            except Exception as e:
                print('********** admin - send item mail **********')
                print(str(e))

            values = {
                'status': 'Rejected'
            }

            condition = {'id': item_delivered[0]['id']}

            try:
                update_query = ds_utils.create_script_string('ds_item_delivered', 'U', values, condition)
                db.executesql(update_query)
            except Exception as e:
                print('********** admin - send item mail **********')
                print(str(e))

            # *********** Fin - Prácticas Finales (Digital Signature) - Fernando Reyes *************

    return success

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def items_grid():
    cdate = datetime.now().date()
    period = request.vars['period']
    area = request.vars['area']
    context_string = T('All')
    period_entity = db(db.period_year.id==period).select().first()
    if period_entity:
        period_name = period_entity.period.name
        period_year = period_entity.yearp
        context_string = T(str(period_name)) + ' ' + str(period_entity.yearp)
    school_id = request.vars['school_id']
    if not(area=='' or area==None):
        projects = db(db.project.area_level==area).select()
    else:
        projects = db(db.project).select()
    assignations = db((db.user_project.project.belongs(projects))&
            (db.auth_user.id==db.user_project.assigned_user)&
            (db.auth_user.id==db.auth_membership.user_id)&
            ((school_id=='' or school_id==None) or \
                (db.auth_user.username==school_id))&
            (db.auth_membership.group_id==db.auth_group.id)&
            (db.auth_group.role!='Teacher')).select(db.user_project.ALL)
    items = db((db.item.assignation.belongs(assignations))&
        ((period=='' or period==None) or (db.item.created==period))
        ).select(orderby=db.item.item_restriction.name)
    if request.args(0) == 'zip':
        files = []
        for item in items:
            files.append(item.uploaded_file)
        if len(files) > 0:
            return response.zip(request, files, db)
        response.flash = T('No files to download.')

    # *********** Inicio - Prácticas Finales (Digital Signature) - Fernando Reyes *************
    def get_signed_file(id_item):
        query_signed_file = ds_utils.get_item_delivered_by_item(id_item)
        item_delivered = db.executesql(query_signed_file, as_dict=True)

        if len(item_delivered) > 0:
            if item_delivered[0]['signed_file'] is not None and item_delivered[0]['status'] == 'Signed':
                return item_delivered[0]['signed_file']
        return None

    return dict(items=items,
        area=area,
        period=period,
        context_string=context_string,
        cdate=str(cdate),
        get_signed_file=get_signed_file)
    # *********** Fin - Prácticas Finales (Digital Signature) - Fernando Reyes *************

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def toggle_active_item():
    item = request.vars['item']
    comment = request.vars['comment'] or None
    if item != None:
        item = db(db.item.id==item).select().first()
    if item != None:
        item.update_record(
            is_active = not item.is_active,
            admin_comment=comment)
    return True

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def assign_items():
    filter = 1
    if request.vars['filter'] != None:
        filter = int(request.vars['filter'])
    if filter == 1:
        pass
    dct = {}
    items = db((db.item.is_active==True)).select()
    rows=db().select(db.item.ALL, db.item_project.ALL,
         left=db.item_project.on(db.item.id==db.item_project.item))
    for item in items:
        dct.update({item.name:[]})
    for row in rows:
        dct[row.item.name].append(row)
    return locals()

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def teacher_assignation_upload():
    error_users = []
    warning_users = []

    #emarquez: por default true el chek ya que no se verifica mas en UV
    #uv_off = request.vars['uv_off'] or False
    uv_off = True

    success = False
    current_period = cpfecys.current_year_period()

    #emarquez:  soporte de carga para periodos variables.
    #se envia 0  para  tomar el semestre actual, y el codigo para periodos variables
    cmb_period = request.vars['cmbPeriod'] or False
    periodo_variable = False
    if cmb_period:
        if cmb_period != '0':
            periodo_variable = True
            period_var = db.period(id = cmb_period)
            current_period = db((db.period_year.period==cmb_period)&
                                  (db.period_year.period == period_var)).select().first()
    #emarquez: fin cambio.

    if request.vars.csvfile is not None:
        try:
            file = request.vars.csvfile.file
        except AttributeError:
            response.flash = T('Please upload a file.')
            return dict(success = False,
                file = False,
                periods = periods)
        try:
            try:
                content_file = file.read()
                detection = chardet.detect(content_file)['encoding']
                content_file = content_file.decode(detection).splitlines()
            except:
                content_file = []

            cr = csv.reader(content_file, delimiter=',', quotechar='"')
            try:
                success = True
                header = next(cr)
            except:
                response.flash = T('File doesn\'t seem properly encoded.')
                return dict(success = False,
                    file = False,
                    periods = periods,
                    current_period = current_period)
            for row in cr:
                ## parameters
                rusername = row[2] or ''
                rproject = row[0]
                rassignation_length = row[7]
                rpro_bono = (row[8] == 'Si') or (row[8] == 'si')
                rhours = row[9]
                remail = row[5]
                rphone = row[6] or ''
                rlast_name = row[3]
                rfirst_name = row[4]
                #VALIDATE EMAIL
                if IS_EMAIL()(remail)[1]:
                    row.append('Error: ' + T('The email entered is incorrect.'))
                    error_users.append(row)
                    continue
                else:
                    ## check if user exists
                    usr = db.auth_user(db.auth_user.username == rusername)
                    project = db.project(db.project.project_id == rproject)
                    if usr is None:
                        ## find it on chamilo (db2)
                        if not uv_off:
                            """
                            delete chamilo
                            usr = db2.user_user(db2.user_user.username == rusername)
                            if usr is None:
                            """
                            # report error and get on to next row
                            row.append(T('Error: ') + T('User is not valid. \
                                User doesn\'t exist in UV.'))
                            error_users.append(row)
                            continue
                            """
                            else:
                                # insert the new user
                                usr = db.auth_user.insert(username = usr.username,
                                                        password = usr.password,
                                                        phone = usr.phone,
                                                        last_name = usr.lastname,
                                                        first_name = usr.firstname,
                                                        email = usr.email)
                                #add user to role 'Teacher'
                                auth.add_membership('Teacher', usr)
                            """
                        else:
                            #insert a new user with csv data
                            usr = db.auth_user.insert(username = rusername,
                                                      email = remail,
                                                      first_name=rfirst_name,
                                                      last_name=rlast_name,
                                                      phone=rphone)
                            #add user to role 'Teacher'
                            auth.add_membership('Teacher', usr)
                    else:

                        #emarquez: verificacion de asignacion de periodos variables
                        assignation = db.user_project(
                            (db.user_project.assigned_user == usr.id)&
                            (db.user_project.project == project)&
                            (db.user_project.period == current_period)&
                            (db.user_project.assignation_status == None))

                        if assignation != None:
                            row.append(T('Error: ') + T('User \
                             was already assigned, Please Manually Assign Him.'))
                            error_users.append(row)
                            continue
                    if project != None:
                        db.user_project.insert(assigned_user = usr,
                                                project = project,
                                                period = current_period,
                                                periods = rassignation_length,
                                                pro_bono = rpro_bono,
                                                hours = rhours)
                    else:
                        # project_id is not valid
                        row.append('Error: ' + T('Project code is not valid. \
                         Check please.'))
                        error_users.append(row)
                        continue
        except csv.Error:
            response.flash = T('File doesn\'t seem properly encoded.')
            return dict(success = False,
                file = False,
                periods = periods,
                current_period = current_period)
        response.flash = T('Data uploaded')
        return dict(success = success,
                    errors = error_users,
                    warnings = warning_users,
                    periods = periods,
                    current_period = current_period)
    return dict(success = False,
                file = False,
                periods = periods,
                current_period = current_period)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def assignation_upload():
    error_users = []
    warning_users = []

    #emarquez: se pone por default el check
    uv_off = True

    success = False
    current_period = cpfecys.current_year_period()

    #emarquez:  soporte de carga para periodos variables.
    #se envia 0  para  tomar el semestre actual, y el codigo para periodos variables
    cmb_period = request.vars['cmbPeriod'] or False
    periodo_variable = False
    if cmb_period:
        if cmb_period != '0':
            periodo_variable = True
            period_var = db.period(id = cmb_period)
            current_period = db((db.period_year.period == cmb_period) & (db.period_year.period == period_var)).select().first()
    #emarquez: fin cambio.

    if request.vars.csvfile is not None:
        try:
            file = request.vars.csvfile.file
        except AttributeError:
            response.flash = T('Please upload a file.')
            return dict(success=False, file=False, periods=periods)

        try:
            try:
                content_file = file.read()
                detection = chardet.detect(content_file)['encoding']
                content_file = content_file.decode(detection).splitlines()
            except:
                content_file = []
            cr = csv.reader(content_file, delimiter=',', quotechar='"')
            try:
                success = True
                header = next(cr)
            except:
                response.flash = T('File doesn\'t seem properly encoded.')
                return dict(success = False,
                file = False,
                periods = periods,
                current_period = current_period)
            for row in cr:
                ## parameters
                rusername = row[1]
                rproject = row[3]
                rassignation_length = row[4]
                rpro_bono = (row[5] == 'Si') or (row[5] == 'si')
                rhours = row[6]
                remail = row[7]
                #VALIDATE EMAIL
                if IS_EMAIL()(remail)[1]:
                    row.append('Error: ' + T('The email entered is incorrect.'))
                    error_users.append(row)
                    continue
                else:
                    ## check if user exists
                    usr = db.auth_user(db.auth_user.username == rusername)
                    project = db.project(db.project.project_id == rproject)
                    if usr is None:
                        ## find it on chamilo (db2)
                        if not uv_off:
                            """
                            delete chamilo
                            usr = db2.user_user(db2.user_user.username == rusername)
                            if usr is None:
                            """
                            # report error and get on to next row
                            row.append(T('Error: ') + T('User is not valid. User doesn\'t exist in UV.'))
                            error_users.append(row)
                            continue
                            """
                            delete chamilo
                            else:
                                # insert the new user
                                usr = db.auth_user.insert(username = usr.username,
                                                        password = usr.password,
                                                        phone = usr.phone,
                                                        last_name = usr.lastname,
                                                        first_name = usr.firstname,
                                                        email = usr.email)
                                #add user to role 'student'
                                auth.add_membership('Student', usr)
                            """
                        else:
                            #insert a new user with csv data
                            usr = db.auth_user.insert(username=rusername, email=remail)
                            #add user to role 'student'
                            auth.add_membership('Student', usr)
                    else:
                        if db((db.auth_group.role == "Student")&(db.auth_membership.group_id == db.auth_group.id)&(db.auth_membership.user_id == usr.id)).select().first() is None:
                            auth.add_membership('Student', usr)

                        #emarquez: agregando verificacion especial para periodos variables
                        if periodo_variable:
                            assignation = db.user_project(
                                (db.user_project.assigned_user == usr.id)&
                                (db.user_project.project == project)&
                                (db.user_project.period == current_period))
                        else:
                        #emaquez: fin cambio
                        #excluir periodos variables si no se estan ingresando estos ( (db.user_project.period != db.period_detail.period)&)
                            listperios = db(db.period_detail.period)._select(db.period_detail.period)                           
 
                            assignation = db.user_project(
                                (db.user_project.assigned_user == usr.id)&
                                ((~db.period.id.belongs(listperios))&(db.period_year.period==db.period.id))&
                                (db.user_project.period == db.period_year.id)&
                                (db.user_project.project == project)&
                                (db.user_project.assignation_status == None))


                        if assignation != None:
                            row.append(T('Error: ') + T('User was already assigned, Please Manually Assign Him.'))
                            error_users.append(row)
                            #assignation.update_record(periods = \
                                #rassignation_length, pro_bono = \
                                #rpro_bono)
                            continue
                    if project != None:
                        db.user_project.insert(assigned_user = usr,
                                                project = project,
                                                period = current_period,
                                                periods = rassignation_length,
                                                pro_bono = rpro_bono,
                                                hours = rhours)
                    else:
                        # project_id is not valid
                        row.append('Error: ' + T('Project code is not valid. Check please.'))
                        error_users.append(row)
                        continue
        except csv.Error:
            response.flash = T('File doesn\'t seem properly encoded.')
            return dict(success = False,
                file = False,
                periods = periods,
                current_period = current_period)
        response.flash = T('Data uploaded')
        return dict(success = success,
                    errors = error_users,
                    warnings = warning_users,
                    periods = periods,
                    current_period = current_period)
    return dict(success = False,
                file = False,
                periods = periods,
                current_period = current_period)

@cache.action()
@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def download():
    item = db(db.item.uploaded_file==request.args[0]).select().first()
    project =  item.assignation.project
    t_assignation = db((db.user_project.project==project.id)&
        (db.user_project.assigned_user==auth.user.id))
    if item != None and t_assignation != None:
        return response.download(request, db)
    else:
        session.flash = T('Access Forbidden')
        redirect(URL('default', 'home'))

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def final_practice():
    #emarquez
    #type=2, periodo variable.  si type=1, periodo semestre
    tipo_periodo = request.vars['type'] or False
    if not tipo_periodo:
        tipo_periodo = 1

    #requires parameter year_period if no one is provided then it is
    #automatically detected
    #and shows the current period
    year_period = request.vars['year_period']
    max_display = 1
    currentyear_period = db.period_year(db.period_year.id == year_period)
    if not currentyear_period:
        currentyear_period = cpfecys.current_year_period()
        changid = currentyear_period.id
        #emarquez: si el periodo no es 0( periodo) o no trae periodo( actual), entonces setea al periodo actual,
        if year_period:
            if int(year_period) != 0:
                year_period = changid
        else:
            year_period = changid


    #emarquez: grid enlazado al periodo
    grid = SQLFORM.grid((db.user_project.period == year_period))

    #emarquez: cambiando la logica de las pestañas, para tratamiento de periodos
    list_periods = db(db.period_detail.period)._select(db.period_detail.period)
    if int(tipo_periodo) == 1:
        periods_before = db((~db.period.id.belongs(list_periods)) & (db.period_year.period == db.period.id)).select(orderby=~db.period_year.id)
    else:
        periods_before = db((db.period.id == db.period_detail.period) & (db.period_year.period == db.period.id)).select()


   #emarquez: fin cambio de logica de pestañas

    #emarquez: periodos dinamicos
    other_periods = db(db.period).select()

    #emarquez:agrego parametro type, para retorno de tipo de periodo
    return dict(
        grid=grid,
        currentyear_period=currentyear_period,
        periods_before=periods_before,
        other_periods=other_periods,
        type=tipo_periodo
    )

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def users():
    orderby = dict(auth_user=[db.auth_user.first_name, db.auth_user.username])
    db.auth_user.photo.writable = False
    grid = SQLFORM.smartgrid(
        db.auth_user,
        linked_tables=['auth_membership', 'auth_event', 'auth_cas', 'user_project', 'period_year', 'period', 'report'],
        orderby=orderby
    )
    return dict(grid = grid)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def user_mail_update():
    teachers = db((db.auth_membership.group_id == db.auth_group.id) & (db.auth_group.role == 'Teacher')).select(db.auth_membership.user_id, distinct=True)
    group_teacher = [teacher.user_id for teacher in teachers]

    if len(group_teacher) <= 0:
        group_teacher.append(-1)

    db.auth_user.first_name.writable = False
    db.auth_user.last_name.writable = False
    db.auth_user.phone.writable = False
    db.auth_user.phone.readable = False
    db.auth_user.home_address.writable = False
    db.auth_user.home_address.readable = False
    db.auth_user.work_address.writable = False
    db.auth_user.work_address.readable = False
    db.auth_user.company_name.writable = False
    db.auth_user.company_name.readable = False
    db.auth_user.work_phone.writable = False
    db.auth_user.work_phone.readable = False
    db.auth_user.password.writable = False
    db.auth_user.password.readable = False
    db.auth_user.photo.writable = False
    db.auth_user.photo.readable = False
    grid = SQLFORM.grid(db.auth_user.id.belongs(group_teacher), oncreate=oncreate_user_mail_update)
    
    return dict(grid=grid)

def oncreate_user_mail_update(form):
    new_teacher = db(db.auth_user.id == form.vars.id).select(db.auth_user.id).first()
    rol_teacher = db(db.auth_group.role == 'Teacher').select(db.auth_group.id).first()
    
    if rol_teacher is None:
        db(db.auth_user.id == new_teacher.id).delete()
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        db.auth_membership.insert(user_id=new_teacher.id, group_id=rol_teacher.id)

def get_periodos_variables():
    return response.json(db((db.period.id==db.period_detail.period) & (db.period_year.period==db.period.id)).select())

def get_periodos_semestre():
    list_periods = db(db.period_detail.period)._select(db.period_detail.period)

    return response.json(db((~db.period.id.belongs(list_periods))&(db.period_year.period==db.period.id)).select(orderby=~db.period_year.id))

#*********************EPS DANIEL COS

@auth.requires_membership('Super-Administrator')
def reset_notification_numbers():
    redis_db_1.flushdb()
    session.flash = T('Numeros de notificaciones reiniciados')
    redirect(URL('default','home'))

@auth.requires_membership('Super-Administrator')
def backup_configuration():
    bk_fecha=datetime.now().date() + timedelta(days=1)
    bk_estado="I"
    bk_ruta=''
    bk_tipo=''
    bk_cantidad=1
    bk_bandera=True
    bk_servidor=''
    bk_puerto=''
    bk_usuario=''
    bk_clave=''
    bk_backups=[]
    try:
        bk_config=db(db.backup_configuration.id==1).select()

        if len(bk_config)!=0:
            bk_estado=bk_config[0].estado
            if bk_estado=="A":
                bk_fecha=bk_config[0].fecha_proximo
                bk_ruta=bk_config[0].ruta
                bk_tipo=bk_config[0].tipo
                bk_cantidad=bk_config[0].cantidad
                bk_servidor=bk_config[0].servidor
                bk_puerto=bk_config[0].puerto
                bk_usuario=bk_config[0].usuario
                bk_clave=bk_config[0].clave
        else:
            response.flash = 'No existe configuración en la base de datos'
            bk_bandera=False

        bk_backups=db().select(db.backup_history.ALL,groupby=db.backup_history.servidor|db.backup_history.ruta,distinct=True,orderby=~db.backup_history.id)
    except:
        response.flash = 'Ocurrio un error al leer la configuracion'
        bk_bandera=False

    def backup_list(ruta,servidor):
        bk_list=db(db.backup_history.ruta==ruta,db.backup_history.servidor==servidor).select(orderby=~db.backup_history.fecha)
        return bk_list

    return dict(
            estado=bk_estado,
            fecha=bk_fecha,
            ruta=bk_ruta,
            tipo=bk_tipo,
            cantidad=bk_cantidad,
            servidor=bk_servidor,
            puerto=bk_puerto,
            usuario=bk_usuario,
            clave=bk_clave,
            bandera=bk_bandera,
            backups=bk_backups,
            backup_list=backup_list
            )

@auth.requires_membership('Super-Administrator')
def backup_configuration_save():
    error=""
    
    bk_fecha=""
    bk_ruta=""
    bk_tipo=""
    bk_cantidad=""

    try:
        bk_estado=request.post_vars.bk_estado
        bk_fecha=request.post_vars.bk_fecha
        bk_ruta=request.post_vars.bk_ruta
        bk_tipo=request.post_vars.bk_tipo
        bk_cantidad=request.post_vars.bk_cantidad

        if bk_estado=="":
            error+="- Existen campos vacios"
        elif bk_estado=="A":
            if bk_fecha=="" or bk_ruta=="" or bk_tipo=="" or bk_cantidad=="":
                error+="- Existen campos vacios"
            else:

                if datetime.strptime(bk_fecha, "%Y-%m-%d").date() <= datetime.now().date():
                    error="- La fecha debe ser mayor a hoy </br>"

                if int(bk_cantidad) < 1 or int(bk_cantidad) > 10:
                    error+="- La cantidad de copias de seguridad almacenadas debe ser como minimo 1 y como maximo 10</br>"

        if error=="":
            bk_config=db(db.backup_configuration.id==1).select().first()

            if bk_estado=="I":
                bk_ruta=""
                bk_tipo=""
                bk_config.update_record(estado=bk_estado,fecha_proximo=None,ruta=bk_ruta,tipo=bk_tipo,cantidad=bk_cantidad)
            else:
                bk_config.update_record(estado=bk_estado,fecha_proximo=datetime.strptime(bk_fecha, "%Y-%m-%d"),ruta=bk_ruta,tipo=bk_tipo,cantidad=bk_cantidad)

    except exception as e:
        error=str(e)

    return response.json(error)

@auth.requires_membership('Super-Administrator')
def backup_configuration_save_server():

    error=""
    
    bk_servidor=""
    bk_puerto=""
    bk_usuario=""
    bk_clave=""

    try:
        bk_servidor=request.post_vars.bk_servidor
        bk_puerto=request.post_vars.bk_puerto
        bk_usuario=request.post_vars.bk_usuario
        bk_clave=request.post_vars.bk_clave

        if bk_servidor=="" or bk_puerto=="" or bk_usuario=="" or bk_clave=="":
            error+="- Existen campos vacios"
        else:

            if not int(bk_puerto):
                error+="- El puerto debe ser un numero</br>"

        if error=="":
            bk_config=db(db.backup_configuration.id==1).select().first()
            bk_config.update_record(servidor=bk_servidor,puerto=bk_puerto,usuario=bk_usuario,clave=bk_clave)

    except exception as e:
        error=str(e)

    return response.json(error)

#************* FIN EPS DANIEL COS *****


#*********** Inicio - Prácticas Finales (Digital Signature) - Fernando Reyes *************

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def manage_type_file():
    args = request.args
    new_dict = {}

    if len(args) == 0:
        new_dict['type'] = 'list'
        #Obteniendo listado
        query = ds_utils.get_all_file_types()
        new_dict['list'] = db.executesql(query, as_dict=True)
    elif len(args) == 1:
        option = args[0]
        new_dict['type'] = option

        if option == 'new':
            if request.env.request_method == "POST":
                is_valid, resultado = ds_utils.validate_form_file_types(request.vars)
                new_dict['item'] = resultado

                if not is_valid:
                    new_dict['message'] = resultado['message']
                    return dict(action=new_dict)

                values = {
                    'name': resultado['inputName'],
                    'extension': resultado['inputExtension']
                }
                try:
                    insert_query = ds_utils.create_script_string('ds_type_file', 'I', values)
                    db.executesql(insert_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)

                session.flash = 'Registro creado exitosamente'
                redirect(URL('admin', 'manage_type_file'))
        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
    elif len(args) == 2:
        option = args[0]
        id = args[1]
        new_dict['type'] = option

        query = ds_utils.get_file_type(id)
        item = db.executesql(query, as_dict=True)

        if len(item) < 1:
            session.flash = 'No existe el registro'
            redirect(URL('admin', 'manage_type_file'))

        if option == 'show' or option == 'delete':
            new_dict['item'] = item
            if option == 'delete' and request.env.request_method == "POST":
                condition = {'id': int(id)}
                try:
                    delete_query = ds_utils.create_script_string('ds_type_file', 'D', condition, condition)
                    db.executesql(delete_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)

                session.flash = 'Registro eliminado exitosamente'
                redirect(URL('admin', 'manage_type_file'))
        elif option == 'edit':
            if request.env.request_method == "GET":
                result = {
                    'id': item[0]['id'],
                    'inputName': item[0]['name'],
                    'inputExtension': item[0]['extension']
                }
                new_dict['item'] = result
            else:
                is_valid, resultado = ds_utils.validate_form_file_types(request.vars)
                resultado['id'] = id
                new_dict['item'] = resultado

                if not is_valid:
                    new_dict['message'] = resultado['message']
                    return dict(action=new_dict)

                values = {
                    'name': resultado['inputName'],
                    'extension': resultado['inputExtension']
                }
                condition = {'id': int(id)}
                try:
                    update_query = ds_utils.create_script_string('ds_type_file', 'U', values, condition)
                    db.executesql(update_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)

                session.flash = 'Registro actualizado exitosamente'
                redirect(URL('admin', 'manage_type_file'))
        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
    else:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    return dict(action=new_dict)

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def manage_signature():
    args = request.args
    new_dict = {}

    if len(args) == 0:
        new_dict['type'] = 'list'
        # Obteniendo listado
        query = ds_utils.get_all_signatures(auth.user.username, auth.has_membership('Super-Administrator'))
        new_dict['list'] = db.executesql(query, as_dict=True)
    elif len(args) == 1:
        option = args[0]
        new_dict['type'] = option

        if option == 'new':
            if request.env.request_method == "POST":
                is_valid, resultado = ds_utils.validate_form_signature(request.vars)
                new_dict['item'] = resultado
                new_dict['select'] = get_signature_type_form_select(resultado['inputType'])

                if not is_valid:
                    new_dict['message'] = resultado['message']
                    return dict(action=new_dict)

                values = {
                    'name': resultado['inputName'],
                    'signature_type': resultado['inputType'],
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'created_by': auth.user.username
                }

                try:
                    insert_query = ds_utils.create_script_string('ds_signature', 'I', values)
                    db.executesql(insert_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)

                session.flash = 'Registro creado exitosamente'
                redirect(URL('admin', 'manage_signature'))

            else:
                new_dict['select'] = get_signature_type_form_select()

        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    elif len(args) == 2:
        option = args[0]
        id = args[1]
        new_dict['type'] = option

        query = ds_utils.get_signature(id, auth.user.username, auth.has_membership('Super-Administrator'))
        item = db.executesql(query, as_dict=True)
        if len(item) < 1:
            session.flash = 'No existe el registro'
            redirect(URL('admin', 'manage_signature'))

        # verificando que solo el usuario que creo el registro lo pueda modificar o eliminar
        has_access = auth.user.username == item[0]['created_by']

        if option == 'show' or option == 'delete':
            new_dict['item'] = item

            if option == 'delete' and request.env.request_method == "POST" and not has_access:
                new_dict['message'] = 'Operación no permitida'
                return dict(action=new_dict)
            elif option == 'delete' and request.env.request_method == "POST":
                # eliminando imagen asociada
                if item[0]['image'] is not None:
                    rm_file = ds_utils.remove_file(item[0]['image'], request.folder)
                    if not rm_file:
                        new_dict['message'] = 'No se puede borrar imagen de firma'
                        return dict(action=new_dict)

                condition = {'id': int(id)}
                try:
                    delete_query = ds_utils.create_script_string('ds_signature', 'D', condition, condition)
                    db.executesql(delete_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)

                session.flash = 'Registro eliminado exitosamente'
                redirect(URL('admin', 'manage_signature'))
        elif option == 'edit':
            if request.env.request_method == "GET":
                result = {
                    'id': item[0]['id'],
                    'inputName': item[0]['name'],
                    'inputImage': item[0]['image'],
                    'inputType': item[0]['signature_type']
                }
                new_dict['item'] = result
                new_dict['select'] = get_signature_type_form_select(item[0]['signature_type'])
            else:
                is_valid, resultado = ds_utils.validate_form_signature(request.vars)
                resultado['id'] = id
                resultado['inputImage'] = item[0]['image']
                new_dict['item'] = resultado
                new_dict['select'] = get_signature_type_form_select(resultado['inputType'])
                if not is_valid:
                    new_dict['message'] = resultado['message']
                    return dict(action=new_dict)

                if not has_access:
                    new_dict['message'] = 'Operación no permitida'
                    return dict(action=new_dict)

                values = {
                    'name': resultado['inputName'],
                    'signature_type': resultado['inputType'],
                    'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                if item[0]['signature_type'] != resultado['inputType']:
                    # eliminando imagen asociada
                    if item[0]['image'] is not None:
                        rm_file = ds_utils.remove_file(item[0]['image'], request.folder)
                        if not rm_file:
                            new_dict['message'] = 'No se puede borrar imagen de firma'
                            return dict(action=new_dict)

                        values['image'] = None

                condition = {'id': int(id)}
                try:
                    update_query = ds_utils.create_script_string('ds_signature', 'U', values, condition)
                    db.executesql(update_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)

                session.flash = 'Registro actualizado exitosamente'
                redirect(URL('admin', 'manage_signature'))
        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    elif len(args) == 3:
        if not (args[0] == 'edit' and args[1] == 'image' and args[2] == 'upload'):
            session.flash = T('Not valid Action.')
            redirect(URL('admin', 'manage_signature'))

        #if not request.vars.has_key('signature'):
        if not 'signature' in request.vars:
            session.flash = T('Not valid Action.')
            redirect(URL('admin', 'manage_signature'))

        signature = request.vars.signature.strip()
        query = ds_utils.get_signature(signature, auth.user.username, auth.has_membership('Super-Administrator'))
        item = db.executesql(query, as_dict=True)

        if len(item) < 1:
            session.flash = 'No existe el registro'
            redirect(URL('admin', 'manage_signature'))

        if item[0]['signature_type'] == 'QR Code':
            session.flash = T('Not valid Action.')
            redirect(URL('admin', 'manage_signature'))

        new_dict['type'] = args[1]
        new_dict['item'] = item

        # verificando que solo el usuario que creo el registro lo pueda modificar o eliminar
        has_access = auth.user.username == item[0]['created_by']

        # pasando megabytes a bytes (MB * kB * B)
        size_file = 2
        max_size = size_file * 1024 * 1024
        message = ("Tamaño máximo del archivo es de {} MB.").format(size_file)

        upload_form = FORM(
            DIV(
                LABEL('Seleccione archivo a subir', _for='fileToUpload', _class='col-sm-3 col-form-label'),
                DIV(
                    INPUT(_type='file', _class='form-control-file', _name='fileToUpload', _id='fileToUpload',
                          _style='margin-top:5px;',
                          requires=[IS_NOT_EMPTY(error_message='Debe seleccionar un archivo a subir.'),
                                    IS_UPLOAD_FILENAME(extension='(png|jpg|jpeg)',
                                                       error_message='Tipo de archivo no permitido.'),
                                    IS_LENGTH(max_size, error_message=message)]
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
            if not has_access:
                new_dict['message'] = 'Operación no permitida'
            elif request.vars.fileToUpload is not None:
                name = 'signature'
                result = ds_utils.save_file(request.vars.fileToUpload.file, request.vars.fileToUpload.filename,
                                             request.folder, name, item[0]['image'])

                if result is not None:
                    values = {
                        'image': result,
                        'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    condition = {'id': int(signature)}
                    try:
                        update_query = ds_utils.create_script_string('ds_signature', 'U', values, condition)
                        db.executesql(update_query)
                        session.flash = 'Archivo guardado exitosamente'
                    except Exception as e:
                        session.flash = 'No se pudo guardar el archivo'

                    redirect(URL('admin', 'manage_signature', args=['edit', signature]))
                else:
                    new_dict['message'] = 'Error al guardar el archivo'
            else:
                new_dict['message'] = 'Debe seleccionar un archivo a subir.'

        return dict(action=new_dict, form=upload_form)

    else:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    return dict(action=new_dict)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def manage_document():
    args = request.args
    new_dict = {}

    if len(args) == 0:
        new_dict['type'] = 'list'
        # Obteniendo listado
        query = ds_utils.get_all_documents()
        new_dict['list'] = db.executesql(query, as_dict=True)
    elif len(args) == 1:
        option = args[0]
        new_dict['type'] = option

        if option == 'new':
            if request.env.request_method == "POST":
                is_valid, resultado = ds_utils.validate_form_document(request.vars)
                new_dict['select'] = get_file_type_form_select(resultado['inputTypeFile'])
                new_dict['selectDoc'] = get_document_type_form_select(resultado['inputDocumentType'])
                new_dict['selectSize'] = get_max_size_form_select(resultado['inputSize'])
                new_dict['item'] = resultado
                checkbox = get_document_checkbox_form(resultado['inputActivate'], resultado['inputSignature'])
                new_dict['checkActivate'] = checkbox['checkActivate']
                new_dict['checkSignature'] = checkbox['checkSignature']

                if not is_valid:
                    new_dict['message'] = resultado['message']
                    return dict(action=new_dict)

                query_file = ds_utils.get_file_type(resultado['inputTypeFile'])
                type_file_temp = db.executesql(query_file, as_dict=True)

                if len(type_file_temp) < 1:
                    new_dict['message'] = 'No existe tipo de archivo seleccionado'
                    return dict(action=new_dict)

                if resultado['inputSignature']:
                    if not ds_utils.is_valid_extension(type_file_temp[0]['extension']):
                        new_dict[
                            'message'] = 'No es posible activar la opción de firma, extensión del tipo de archivo no es PDF'
                        return dict(action=new_dict)

                values = {
                    'name': resultado['inputName'],
                    'description': resultado['inputDescription'],
                    'max_size': resultado['inputSize'],
                    'is_active': 'T' if resultado['inputActivate'] else 'F',
                    'signature_required': 'T' if resultado['inputSignature'] else 'F',
                    'type_file': resultado['inputTypeFile'],
                    'doc_type': resultado['inputDocumentType'],
                    'date_start': resultado['inputStart'],
                    'date_finish': resultado['inputFinish']
                }

                try:
                    insert_query = ds_utils.create_script_string('ds_document', 'I', values)
                    db.executesql(insert_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)

                query_last_doc = ds_utils.get_last_document()
                last_doc = db.executesql(query_last_doc, as_dict=True)

                if len(last_doc) < 1:
                    session.flash = 'No se encontro entregable actual'
                    redirect(URL('admin', 'manage_document'))

                # Verificando si hay que actualizar período de control
                current_year_period = db.period_year(db.period_year.id == cpfecys.current_year_period())

                # validando si existe periodo
                query = ds_utils.get_period(current_year_period.id)
                item = db.executesql(query, as_dict=True)

                if len(item) < 1:
                    print('********** admin - manage_document **********')
                    print('El periodo actual no es primer o segundo semestre')
                    session.flash = 'Registro creado exitosamente'
                    redirect(URL('admin', 'manage_document'))

                if item[0]['control_period'] != 0:
                    # validando que exista control para el periodo
                    query_control = ds_utils.get_document_control_period_by_period(item[0]['id'])
                    item_control = db.executesql(query_control, as_dict=True)

                    if len(item_control) < 1:
                        session.flash = 'No existe gestión de entregables'
                        redirect(URL('admin', 'manage_document'))

                    current_period = item[0]['id']

                    # obteniendo estado de asignacion
                    status = db.assignation_status(name="Successful")
                    id_status = status['id']

                    # obteniendo periodo anterior
                    query_previous = ds_utils.get_previous_period(item[0]['id'])
                    item_previous = db.executesql(query_previous, as_dict=True)
                    if len(item_previous) < 1:
                        previous_period = 0
                    else:
                        previous_period = item_previous[0]['id']

                    doc_period = resultado['inputDocumentType']

                    # Generando registros
                    query_call_proc_1 = ds_utils.get_call_document_delivered_procedure(item_control[0]['id'],
                                                                                       current_period,
                                                                                       previous_period, id_status,
                                                                                       doc_period)

                    try:
                        db.executesql(query_call_proc_1)
                    except Exception as e:
                        print(str(e))
                        session.flash = 'Error al generar registros'
                        redirect(URL('admin', 'manage_document'))

                    # Actualizando control period
                    values = {
                        'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'updated_by': auth.user.username
                    }

                    condition = {'id': item_control[0]['id']}
                    try:
                        update_query = ds_utils.create_script_string('ds_document_control_period', 'U', values,
                                                                     condition)
                        db.executesql(update_query)
                    except Exception as e:
                        session.flash = str(e)
                        redirect(URL('admin', 'manage_document'))

                session.flash = 'Registro creado exitosamente'
                redirect(URL('admin', 'manage_document'))

            else:
                new_dict['select'] = get_file_type_form_select()
                new_dict['selectDoc'] = get_document_type_form_select()
                new_dict['selectSize'] = get_max_size_form_select()
                resultado = get_document_checkbox_form()
                new_dict['checkActivate'] = resultado['checkActivate']
                new_dict['checkSignature'] = resultado['checkSignature']
        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    elif len(args) == 2:
        option = args[0]
        id = args[1]
        new_dict['type'] = option

        query = ds_utils.get_document(id)
        item = db.executesql(query, as_dict=True)

        if len(item) < 1:
            session.flash = 'No existe el registro'
            redirect(URL('admin', 'manage_document'))

        if option == 'show' or option == 'delete':
            new_dict['item'] = item

            if option == 'delete' and request.env.request_method == "POST":
                condition = {'id': int(id)}
                try:
                    delete_query = ds_utils.create_script_string('ds_document', 'D', condition, condition)
                    db.executesql(delete_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)

                session.flash = 'Registro eliminado exitosamente'
                redirect(URL('admin', 'manage_document'))

        elif option == 'edit':
            if request.env.request_method == "GET":
                result = {
                    'id': item[0]['id'],
                    'inputName': item[0]['name'],
                    'inputDescription': item[0]['description'],
                    'inputSize': item[0]['max_size'],
                    'inputStart': item[0]['date_start'],
                    'inputFinish': item[0]['date_finish']
                }
                new_dict['item'] = result
                new_dict['select'] = get_file_type_form_select(str(item[0]['type_file']))
                new_dict['selectDoc'] = get_document_type_form_select(item[0]['doc_type'])
                new_dict['selectSize'] = get_max_size_form_select(item[0]['max_size'])
                checkbox = get_document_checkbox_form(True if item[0]['is_active'] == 'T' else False,
                                                   True if item[0]['signature_required'] == 'T' else False)
                new_dict['checkActivate'] = checkbox['checkActivate']
                new_dict['checkSignature'] = checkbox['checkSignature']
            else:
                is_valid, resultado = ds_utils.validate_form_document(request.vars)
                new_dict['select'] = get_file_type_form_select(resultado['inputTypeFile'])
                new_dict['selectDoc'] = get_document_type_form_select(resultado['inputDocumentType'])
                new_dict['selectSize'] = get_max_size_form_select(resultado['inputSize'])
                resultado['id'] = id
                new_dict['item'] = resultado
                checkbox = get_document_checkbox_form(resultado['inputActivate'], resultado['inputSignature'])
                new_dict['checkActivate'] = checkbox['checkActivate']
                new_dict['checkSignature'] = checkbox['checkSignature']

                if not is_valid:
                    new_dict['message'] = resultado['message']
                    return dict(action=new_dict)

                if resultado['inputSignature']:
                    query_file = ds_utils.get_file_type(resultado['inputTypeFile'])
                    type_file_temp = db.executesql(query_file, as_dict=True)
                    if len(type_file_temp) < 1:
                        new_dict['message'] = 'No existe tipo de archivo seleccionado'
                        return dict(action=new_dict)

                    if not ds_utils.is_valid_extension(type_file_temp[0]['extension']):
                        new_dict[
                            'message'] = 'No es posible activar la opción de firma, extensión del tipo de archivo no es PDF'
                        return dict(action=new_dict)

                values = {
                    'name': resultado['inputName'],
                    'description': resultado['inputDescription'],
                    'max_size': resultado['inputSize'],
                    'is_active': 'T' if resultado['inputActivate'] else 'F',
                    'signature_required': 'T' if resultado['inputSignature'] else 'F',
                    'type_file': resultado['inputTypeFile'],
                    'doc_type': resultado['inputDocumentType'],
                    'date_start': resultado['inputStart'],
                    'date_finish': resultado['inputFinish']
                }

                condition = {'id': int(id)}

                was_change_date = ds_utils.change_dates_form_document(str(item[0]['date_start']), str(item[0]['date_finish']),
                                                                 resultado['inputStart'], resultado['inputFinish'])
                print(was_change_date)
                try:
                    update_query = ds_utils.create_script_string('ds_document', 'U', values, condition)
                    db.executesql(update_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)

                if was_change_date:
                    # Verificando si hay que actualizar período de control
                    current_year_period = db.period_year(db.period_year.id == cpfecys.current_year_period())

                    # validando si existe periodo
                    query = ds_utils.get_period(current_year_period.id)
                    item = db.executesql(query, as_dict=True)

                    if len(item) < 1:
                        print('********** admin - manage_document **********')
                        print('El periodo actual no es primer o segundo semestre')
                        session.flash = 'Registro actualizado exitosamente'
                        redirect(URL('admin', 'manage_document'))

                    if item[0]['control_period'] != 0:

                        current_period = item[0]['control_period']
                        current_document = int(id)
                        year_p = item[0]['yearp']
                        p_name = item[0]['name']

                        query_dates = ds_utils.get_new_dates(current_document, year_p, p_name)
                        item_dates = db.executesql(query_dates, as_dict=True)

                        if len(item_dates) != 0:
                            values = {
                                'date_start': str(item_dates[0]['start_date']),
                                'date_finish': str(item_dates[0]['finish_date'])
                            }
                            condition = { 'document': current_document, 'control_period': current_period }

                            try:
                                update_query = ds_utils.create_script_string('ds_document_delivered', 'U',
                                                                             values, condition)
                                db.executesql(update_query)
                            except Exception as e:
                                new_dict['message'] = str(e)
                                return dict(action=new_dict)

                session.flash = 'Registro actualizado exitosamente'
                redirect(URL('admin', 'manage_document'))
        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    else:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    return dict(action=new_dict)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def signature_assignment():
    args = request.args
    new_dict = {}

    # validando que venga el parametro documento
    #if not request.vars.has_key('document'):
    if not 'document' in vars:
        session.flash = 'No existe documento'
        redirect(URL('default', 'home'))

    # validando que venga el parametro referencia
    #if not request.vars.has_key('reference'):
    if not 'reference' in request.vars:
        session.flash = 'No existe referencia'
        redirect(URL('default', 'home'))

    doc = request.vars.document.strip()
    ref = request.vars.reference.strip()

    if not (ref == 'doc' or ref == 'item'):
        session.flash = 'No existe referencia'
        redirect(URL('default', 'home'))

    new_dict['reference'] = ref
    if ref == 'doc':
        query = ds_utils.get_document(doc)
        redirect_page = 'manage_document'
        ref = 'D'
    else:
        query = ds_utils.get_document_item(doc)
        redirect_page = 'items_manager'
        ref = 'I'

    document = db.executesql(query, as_dict=True)

    # validando que exista documento
    if len(document) < 1:
        session.flash = 'No existe entregable'
        redirect(URL('admin', redirect_page))

    new_dict['document'] = document[0]['id']
    new_dict['doc_name'] = document[0]['name']

    if (ref == 'D' and document[0]['signature_required'] == 'F') or (ref == 'I' and document[0]['item_type'] != 'File'):
        session.flash = 'Entregable no requiere firma'
        redirect(URL('admin', redirect_page))

    if len(args) == 0:
        new_dict['type'] = 'list'
        # Obteniendo listado
        query = ds_utils.get_all_signature_assignments(document[0]['id'], ref)
        new_dict['list'] = db.executesql(query, as_dict=True)
    elif len(args) == 1:
        option = args[0]
        new_dict['type'] = option

        if option == 'new':
            if request.env.request_method == "POST":
                is_valid, resultado = ds_utils.validate_form_signature_assignment(request.vars)
                new_dict['item'] = resultado
                new_dict['select'] = get_signature_form_select(resultado['inputSignature'])
                new_dict['checkActivate'] = get_signature_assignment_checkbox_form(resultado['inputActivate'])

                if not is_valid:
                    new_dict['message'] = resultado['message']
                    return dict(action=new_dict)

                # validando si existe firma
                signature = ds_utils.get_signature(resultado['inputSignature'], auth.user.username, True)
                item = db.executesql(signature, as_dict=True)

                if len(item) < 1:
                    session.flash = 'No existe firma'
                    redirect(URL('admin', 'signature_assignment', vars=dict(document=str(document[0]['id']), reference=new_dict['reference'])))

                if item[0]['signature_type'] == 'Digital Signature':
                    if item[0]['image'] is None:
                        new_dict['message'] = 'Firma seleccionada no tiene imagen asociada'
                        return dict(action=new_dict)

                values = {
                    'signature': resultado['inputSignature'],
                    'is_active': 'T' if resultado['inputActivate'] else 'F',
                    'signature_position_x': resultado['inputPositionX'],
                    'signature_position_y': resultado['inputPositionY'],
                    'signature_height': resultado['inputHeight'],
                    'signature_width': resultado['inputWidth'],
                    'signature_page': resultado['inputPage'],
                    'reference_document': ref
                }
                if ref == 'D':
                    values['document'] = document[0]['id']
                else:
                    values['item_restriction'] = document[0]['id']

                try:
                    insert_query = ds_utils.create_script_string('ds_document_signature', 'I', values)
                    db.executesql(insert_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)

                # Cuando es firma para entregables de proceso existente actualizar el periodo de control
                if ref == 'I':
                    current_year_period = db.period_year(db.period_year.id == cpfecys.current_year_period())

                    # validando si existe periodo
                    query = ds_utils.get_item_period(current_year_period.id)
                    item = db.executesql(query, as_dict=True)

                    if len(item) < 1:
                        print('********** admin - signature_assignment **********')
                        print('El periodo actual no es primer o segundo semestre')
                        session.flash = 'Registro creado exitosamente'
                        redirect(URL('admin', 'signature_assignment', vars=dict(document=str(document[0]['id']), reference=new_dict['reference'])))

                    if item[0]['control_period'] != 0:
                        # validando que exista control para el periodo
                        query_control = ds_utils.get_item_control_period_by_period(item[0]['id'])
                        item_control = db.executesql(query_control, as_dict=True)

                        if len(item_control) > 0:
                            query_proc = ds_utils.get_call_item_delivered_procedure(item_control[0]['id'], item[0]['id'])

                            try:
                                db.executesql(query_proc)
                            except Exception as e:
                                print(str(e))
                                session.flash = 'Error al generar registros'
                                redirect(URL('admin', 'signature_assignment', vars=dict(document=str(document[0]['id']), reference=new_dict['reference'])))

                            values = {
                                'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'updated_by': auth.user.username
                            }

                            condition = {'id': item_control[0]['id']}
                            try:
                                update_query = ds_utils.create_script_string('ds_item_control_period', 'U', values,
                                                                             condition)
                                db.executesql(update_query)
                            except Exception as e:
                                session.flash = str(e)
                                redirect(URL('admin', 'signature_assignment', vars=dict(document=str(document[0]['id']), reference=new_dict['reference'])))


                session.flash = 'Registro creado exitosamente'
                redirect(URL('admin', 'signature_assignment', vars=dict(document=str(document[0]['id']), reference=new_dict['reference'])))
            else:
                new_dict['select'] = get_signature_form_select()
                new_dict['checkActivate'] = get_signature_assignment_checkbox_form()
        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    elif len(args) == 2:
        option = args[0]
        id = args[1]
        new_dict['type'] = option

        query = ds_utils.get_signature_assignment(id, document[0]['id'], ref)
        item = db.executesql(query, as_dict=True)

        if len(item) < 1:
            session.flash = 'No existe el registro'
            redirect(URL('admin', 'signature_assignment', vars=dict(document=str(document[0]['id']), reference=new_dict['reference'])))

        if option == 'show' or option == 'delete':
            new_dict['item'] = item

            if option == 'delete' and request.env.request_method == "POST":

                condition = {'id': int(id)}
                try:
                    delete_query = ds_utils.create_script_string('ds_document_signature', 'D', condition, condition)
                    db.executesql(delete_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)

                session.flash = 'Registro eliminado exitosamente'
                redirect(URL('admin', 'signature_assignment', vars=dict(document=str(document[0]['id']), reference=new_dict['reference'])))
        elif option == 'edit':
            if request.env.request_method == "GET":
                result = {
                    'id': item[0]['id'],
                    'inputPositionX': item[0]['x'],
                    'inputPositionY': item[0]['y'],
                    'inputHeight': item[0]['h'],
                    'inputWidth': item[0]['w'],
                    'inputPage': item[0]['page']
                }

                new_dict['item'] = result
                new_dict['select'] = get_signature_form_select(str(item[0]['id_signature']))
                new_dict['checkActivate'] = get_signature_assignment_checkbox_form(True if item[0]['is_active'] == 'T' else False)
            else:
                is_valid, resultado = ds_utils.validate_form_signature_assignment(request.vars)
                resultado['id'] = id
                new_dict['item'] = resultado
                new_dict['select'] = get_signature_form_select(resultado['inputSignature'])
                new_dict['checkActivate'] = get_signature_assignment_checkbox_form(resultado['inputActivate'])

                if not is_valid:
                    new_dict['message'] = resultado['message']
                    return dict(action=new_dict)

                # validando si existe firma
                signature = ds_utils.get_signature(resultado['inputSignature'],  auth.user.username, True)
                item = db.executesql(signature, as_dict=True)

                if len(item) < 1:
                    session.flash = 'No existe firma'
                    redirect(URL('admin', 'signature_assignment', vars=dict(document=str(document[0]['id']), reference=new_dict['reference'])))

                if item[0]['signature_type'] == 'Digital Signature':
                    if item[0]['image'] is None:
                        new_dict['message'] = 'Firma seleccionada no tiene imagen asociada'
                        return dict(action=new_dict)

                values = {
                    'signature': resultado['inputSignature'],
                    'is_active': 'T' if resultado['inputActivate'] else 'F',
                    'signature_position_x': resultado['inputPositionX'],
                    'signature_position_y': resultado['inputPositionY'],
                    'signature_height': resultado['inputHeight'],
                    'signature_width': resultado['inputWidth'],
                    'signature_page': resultado['inputPage']
                }

                condition = {'id': int(id)}
                try:
                    update_query = ds_utils.create_script_string('ds_document_signature', 'U', values, condition)
                    db.executesql(update_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)

                session.flash = 'Registro actualizado exitosamente'
                redirect(URL('admin', 'signature_assignment', vars=dict(document=str(document[0]['id']), reference=new_dict['reference'])))
        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
    else:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    return dict(action=new_dict)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def document_restrictions():
    args = request.args
    new_dict = {}

    # validando que venga el parametro documento
    #if not request.vars.has_key('document'):
    if not 'document' in request.vars:
        session.flash = 'No existe documento'
        redirect(URL('admin', 'manage_document'))

    doc = request.vars.document.strip()

    query = ds_utils.get_document(doc)
    document = db.executesql(query, as_dict=True)

    # validando que exista documento
    if len(document) < 1:
        session.flash = 'No existe entregable'
        redirect(URL('admin', 'manage_document'))

    new_dict['document'] = document[0]['id']
    new_dict['doc_name'] = document[0]['name']

    if len(args) == 0:
        new_dict['type'] = 'list'
        # Obteniendo listado
        query = ds_utils.get_all_document_restrictions(document[0]['id'])
        new_dict['list'] = db.executesql(query, as_dict=True)
    elif len(args) == 1:
        option = args[0]
        new_dict['type'] = option

        if option == 'new':
            if request.env.request_method == "POST":
                is_valid, resultado = ds_utils.validate_form_document_restrictions(request.vars)
                new_dict['item'] = resultado
                new_dict['select'] = get_area_level_form_select(resultado['inputArea'])
                new_dict['checkEnabled'] = get_document_restrictions_checkbox_form(resultado['inputEnabled'])

                if not is_valid:
                    new_dict['message'] = resultado['message']
                    return dict(action=new_dict)

                # validando si existe area_level
                signature = ds_utils.get_area_level(resultado['inputArea'])
                item = db.executesql(signature, as_dict=True)

                if len(item) < 1:
                    session.flash = 'No existe área'
                    redirect(URL('admin', 'document_restrictions', vars=dict(document=str(document[0]['id']))))

                values = {
                    'area_level': item[0]['id'],
                    'document': document[0]['id'],
                    'is_enabled': 'T' if resultado['inputEnabled'] else 'F'
                }

                try:
                    insert_query = ds_utils.create_script_string('ds_document_restriction_area', 'I', values)
                    db.executesql(insert_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)

                session.flash = 'Registro creado exitosamente'
                redirect(URL('admin', 'document_restrictions', vars=dict(document=str(document[0]['id']))))
            else:
                new_dict['select'] = get_area_level_form_select()
                new_dict['checkEnabled'] = get_document_restrictions_checkbox_form()
        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    elif len(args) == 2:
        option = args[0]
        id = args[1]
        new_dict['type'] = option

        query = ds_utils.get_document_restriction(id, document[0]['id'])
        item = db.executesql(query, as_dict=True)

        if len(item) < 1:
            session.flash = 'No existe el registro'
            redirect(URL('admin', 'document_restrictions', vars=dict(document=str(document[0]['id']))))

        if option == 'show' or option == 'delete':
            new_dict['item'] = item

            if option == 'delete' and request.env.request_method == "POST":

                condition = {'id': int(id)}
                try:
                    delete_query = ds_utils.create_script_string('ds_document_restriction_area', 'D', condition, condition)
                    db.executesql(delete_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)

                session.flash = 'Registro eliminado exitosamente'
                redirect(URL('admin', 'document_restrictions', vars=dict(document=str(document[0]['id']))))
        elif option == 'edit':
            if request.env.request_method == "GET":
                result = {
                    'id': item[0]['id']
                }

                new_dict['item'] = result
                new_dict['select'] = get_area_level_form_select(str(item[0]['area_level']))
                new_dict['checkEnabled'] = get_document_restrictions_checkbox_form(True if item[0]['is_enabled'] == 'T' else False)
            else:
                is_valid, resultado = ds_utils.validate_form_document_restrictions(request.vars)
                resultado['id'] = id
                new_dict['item'] = resultado
                new_dict['select'] = get_area_level_form_select(resultado['inputArea'])
                new_dict['checkEnabled'] = get_document_restrictions_checkbox_form(resultado['inputEnabled'])

                if not is_valid:
                    new_dict['message'] = resultado['message']
                    return dict(action=new_dict)

                # validando si existe area_level
                area_level = ds_utils.get_area_level(resultado['inputArea'])
                item = db.executesql(area_level, as_dict=True)

                if len(item) < 1:
                    session.flash = 'No existe área'
                    redirect(URL('admin', 'document_restrictions', vars=dict(document=str(document[0]['id']))))

                values = {
                    'area_level': item[0]['id'],
                    'document': document[0]['id'],
                    'is_enabled': 'T' if resultado['inputEnabled'] else 'F'
                }

                condition = {'id': int(id)}
                try:
                    update_query = ds_utils.create_script_string('ds_document_restriction_area', 'U', values, condition)
                    db.executesql(update_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)

                session.flash = 'Registro actualizado exitosamente'
                redirect(URL('admin', 'document_restrictions', vars=dict(document=str(document[0]['id']))))

        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    else:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    return dict(action=new_dict)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def restriction_exceptions():
    args = request.args
    new_dict = {}

    # validando que venga el parametro documento
    #if not request.vars.has_key('document'):
    if not 'document' in request.vars:
        session.flash = 'No existe documento'
        redirect(URL('admin', 'manage_document'))

    # validando que venga el parametro restricción
    #if not request.vars.has_key('restriction'):
    if not 'restriction' in request.vars:
        session.flash = 'No existe restricción'
        redirect(URL('admin', 'manage_document'))

    doc = request.vars.document.strip()
    res = request.vars.restriction.strip()

    query = ds_utils.get_document(doc)
    document = db.executesql(query, as_dict=True)

    # validando que exista documento
    if len(document) < 1:
        session.flash = 'No existe entregable'
        redirect(URL('admin', 'manage_document'))

    query_res = ds_utils.get_document_restriction(res, doc)
    restriction = db.executesql(query_res, as_dict=True)

    # validando que exista restricción
    if len(restriction) < 1:
        session.flash = 'No existe área de restricción'
        redirect(URL('admin', 'manage_document'))

    new_dict['document'] = document[0]['id']
    new_dict['doc_name'] = document[0]['name']
    new_dict['restriction'] = restriction[0]['id']
    new_dict['res_name'] = restriction[0]['name']

    if len(args) == 0:
        new_dict['type'] = 'list'
        # Obteniendo listado
        query = ds_utils.get_all_restriction_exceptions(restriction[0]['id'], document[0]['id'])
        new_dict['list'] = db.executesql(query, as_dict=True)
    elif len(args) == 1:
        option = args[0]
        new_dict['type'] = option

        if option == 'new':
            if request.env.request_method == "POST":
                is_valid, resultado = ds_utils.validate_form_restriction_exceptions(request.vars)
                new_dict['item'] = resultado
                new_dict['select'] = get_project_form_select(restriction[0]['area_level'], resultado['inputProject'])

                if not is_valid:
                    new_dict['message'] = resultado['message']
                    return dict(action=new_dict)

                # validando si existe proyecto
                project = ds_utils.get_project(resultado['inputProject'], restriction[0]['area_level'])
                item = db.executesql(project, as_dict=True)

                if len(item) < 1:
                    session.flash = 'No existe proyecto'
                    redirect(URL('admin', 'restriction_exceptions', vars=dict(document=str(document[0]['id']), restriction=restriction[0]['id'])))

                values = {
                    'project': item[0]['id'],
                    'document_restriction': restriction[0]['id']
                }

                try:
                    insert_query = ds_utils.create_script_string('ds_document_restriction_exception', 'I', values)
                    db.executesql(insert_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)

                session.flash = 'Registro creado exitosamente'
                redirect(URL('admin', 'restriction_exceptions', vars=dict(document=str(document[0]['id']), restriction=restriction[0]['id'])))
            else:
                new_dict['select'] = get_project_form_select(restriction[0]['area_level'])
        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    elif len(args) == 2:
        option = args[0]
        id = args[1]
        new_dict['type'] = option

        query = ds_utils.get_restriction_exception(id, restriction[0]['id'], document[0]['id'])
        item = db.executesql(query, as_dict=True)

        if len(item) < 1:
            session.flash = 'No existe el registro'
            redirect(URL('admin', 'restriction_exceptions', vars=dict(document=str(document[0]['id']), restriction=restriction[0]['id'])))

        if option == 'show' or option == 'delete':
            new_dict['item'] = item

            if option == 'delete' and request.env.request_method == "POST":

                condition = {'id': int(id)}
                try:
                    delete_query = ds_utils.create_script_string('ds_document_restriction_exception', 'D', condition, condition)
                    db.executesql(delete_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)

                session.flash = 'Registro eliminado exitosamente'
                redirect(URL('admin', 'restriction_exceptions', vars=dict(document=str(document[0]['id']), restriction=restriction[0]['id'])))
        elif option == 'edit':
            if request.env.request_method == "GET":
                result = {
                    'id': item[0]['id']
                }
                new_dict['item'] = result
                new_dict['select'] = get_project_form_select(restriction[0]['area_level'], str(item[0]['project']))
            else:
                is_valid, resultado = ds_utils.validate_form_restriction_exceptions(request.vars)
                resultado['id'] = id
                new_dict['item'] = resultado
                new_dict['select'] = get_project_form_select(restriction[0]['area_level'], resultado['inputProject'])

                if not is_valid:
                    new_dict['message'] = resultado['message']
                    return dict(action=new_dict)

                # validando si existe proyecto
                project = ds_utils.get_project(resultado['inputProject'], restriction[0]['area_level'])
                item = db.executesql(project, as_dict=True)

                if len(item) < 1:
                    session.flash = 'No existe proyecto'
                    redirect(URL('admin', 'restriction_exceptions',
                                 vars=dict(document=str(document[0]['id']), restriction=restriction[0]['id'])))

                values = {
                    'project': item[0]['id']
                }

                condition = {'id': int(id)}
                try:
                    update_query = ds_utils.create_script_string('ds_document_restriction_exception', 'U', values, condition)
                    db.executesql(update_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)

                session.flash = 'Registro actualizado exitosamente'
                redirect(URL('admin', 'restriction_exceptions', vars=dict(document=str(document[0]['id']), restriction=restriction[0]['id'])))

        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    else:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    return dict(action=new_dict)

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def manage_deliverables():
    args = request.args
    new_dict = {}

    if len(args) == 0:
        new_dict['type'] = 'list'
        # Obteniendo listado
        query = ds_utils.get_all_document_control_periods()
        new_dict['list'] = db.executesql(query, as_dict=True)
        new_dict['is_admin'] = auth.has_membership('Super-Administrator')

        if new_dict['is_admin']:
            new_dict['select'], load_label = get_period_form_select()
            new_dict['label_button'] = XML(load_label)

    elif len(args) == 1:
        option = args[0]
        new_dict['type'] = option
        new_dict['is_admin'] = auth.has_membership('Super-Administrator')

        if option == 'control_period':
            input_action = None
            if request.env.request_method == "POST":
                is_valid, resultado = ds_utils.validate_form_document_control_period(request.vars)

                if not is_valid:
                    session.flash = resultado['message']
                    redirect(URL('admin', 'manage_deliverables'))

                input_period = resultado['inputPeriod']

            else:
                # validando que venga el parametro period
                #if not request.vars.has_key('period'):
                if not 'period' in request.vars:
                    session.flash = 'No existe período'
                    redirect(URL('admin', 'manage_deliverables'))

                # validando que venga el parametro action
                #if not request.vars.has_key('action'):
                if not 'action' in request.vars:
                    session.flash = 'No existe acción'
                    redirect(URL('admin', 'manage_deliverables'))

                input_period = request.vars.period.strip()
                input_action = request.vars.action.strip()
                
                if not (input_action == '0' or input_action == '1' or input_action == '2'):
                    session.flash = 'No existe acción'
                    redirect(URL('admin', 'manage_deliverables'))


            # validando si existe periodo
            query = ds_utils.get_period(input_period)
            item = db.executesql(query, as_dict=True)

            if len(item) < 1:
                session.flash = 'No existe período'
                redirect(URL('admin', 'manage_deliverables'))

            if item[0]['control_period'] == 0:
                values = {
                    'period_year': input_period,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'created_by': auth.user.username
                }

                try:
                    insert_query = ds_utils.create_script_string('ds_document_control_period', 'I', values)
                    db.executesql(insert_query)
                except Exception as e:
                    session.flash = str(e)
                    redirect(URL('admin', 'manage_deliverables'))

                session.flash = 'Registro creado exitosamente'
                redirect(URL('admin', 'manage_deliverables'))


            # validando que exista control para el periodo
            query_control = ds_utils.get_document_control_period_by_period(item[0]['id'])
            item_control = db.executesql(query_control, as_dict=True)

            if len(item_control) < 1:
                session.flash = 'No existe gestión de entregables'
                redirect(URL('admin', 'manage_deliverables'))

            current_period = item[0]['id']

            # obteniendo estado de asignacion
            status = db.assignation_status(name="Successful")
            id_status = status['id']

            # obteniendo periodo anterior
            query_previous = ds_utils.get_previous_period(item[0]['id'])
            item_previous = db.executesql(query_previous, as_dict=True)
            if len(item_previous) < 1:
                previous_period = 0
            else:
                previous_period = item_previous[0]['id']

            # si es practica inicia o es ambos
            if input_action == '0' or input_action == '2':
                doc_period = 'Practice Start'
                query_call_proc_1 = ds_utils.get_call_document_delivered_procedure(item_control[0]['id'], current_period,
                                                                                   previous_period, id_status,
                                                                                   doc_period)

                try:
                    db.executesql(query_call_proc_1)
                except Exception as e:
                    print(str(e))
                    session.flash = 'Error al generar registros'
                    redirect(URL('admin', 'manage_deliverables'))

            # si es practica finaliza o es ambos
            if input_action == '1' or input_action == '2':
                doc_period = 'Practice Finished'
                query_call_proc_2 = ds_utils.get_call_document_delivered_procedure(item_control[0]['id'], current_period,
                                                                                   previous_period, id_status,
                                                                                   doc_period)

                try:
                    db.executesql(query_call_proc_2)
                except Exception as e:
                    print(str(e))
                    session.flash = 'Error al generar registros'
                    redirect(URL('admin', 'manage_deliverables'))


            values = {
                'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'updated_by': auth.user.username
            }

            condition = {'id': item_control[0]['id']}
            try:
                update_query = ds_utils.create_script_string('ds_document_control_period', 'U', values, condition)
                db.executesql(update_query)
            except Exception as e:
                session.flash = str(e)
                redirect(URL('admin', 'manage_deliverables'))

            session.flash = 'Registro actualizado exitosamente'
            redirect(URL('admin', 'manage_deliverables'))

        elif  option == 'deliverable_type' or option == 'deliverables' or option == 'items':
            # validando que venga el parametro control period
            #if not request.vars.has_key('control_period'):
            if not 'control_period' in request.vars:
                session.flash = 'No existe gestión de entregables'
                redirect(URL('admin', 'manage_deliverables'))

            # validando que exista control period
            query = ds_utils.get_document_control_period(request.vars.control_period.strip())
            control_period = db.executesql(query, as_dict=True)

            if len(control_period) < 1:
                session.flash = 'No existe gestión de entregables'
                redirect(URL('admin', 'manage_deliverables'))

            new_dict['control_period'] = control_period[0]['id']

            if option == 'deliverable_type':
                new_dict['control_period_name'] = T(control_period[0]['name']) + ' - ' + str(control_period[0]['yearp'])
            elif option == 'deliverables' or option == 'items':
                # validando que venga el parametro tipo entregable
                #if not request.vars.has_key('type'):
                if not 'type' in request.vars:
                    session.flash = 'No existe tipo de entregable'
                    redirect(URL('admin', 'manage_deliverables'))

                deliverable_type =request.vars.type.strip()
                if not (deliverable_type == '0' or deliverable_type == '1'):
                    session.flash = 'No existe tipo de entregable'
                    redirect(URL('admin', 'manage_deliverables'))

                new_dict['deliverable_type'] = deliverable_type
                type_d = ds_utils.get_deliverable_type(deliverable_type)
                new_dict['type_name'] = type_d[1]

                new_dict['control_period_name'] = T(control_period[0]['name']) + ' - ' + str(control_period[0]['yearp']) + ' (' + type_d[1] + ')'

                if option == 'deliverables':
                    # Obteniendo listado
                    query = ds_utils.get_report_document_delivered(control_period[0]['id'], type_d[2],
                                                                   auth.has_membership('Ecys-Administrator'),
                                                                   auth.user.username)

                    new_dict['list'] = db.executesql(query, as_dict=True)
                else:
                    new_dict['document'] = 0
                    new_dict['doc_name'] = 'Todos'

                    # validando si viene el parametro document
                    #if request.vars.has_key('document'):
                    if 'document' in request.vars:
                        # validando que exista document
                        query = ds_utils.get_document(request.vars.document.strip())
                        document = db.executesql(query, as_dict=True)

                        if len(document) < 1:
                            session.flash = 'No existe entregable'
                            redirect(URL('admin', 'manage_deliverables'))

                        new_dict['document'] = document[0]['id']
                        new_dict['doc_name'] = document[0]['name']

                        query = ds_utils.get_all_document_delivered(control_period[0]['id'],
                                                                    auth.has_membership('Ecys-Administrator'),
                                                                    auth.user.username, document[0]['id'])
                    else:
                        query = ds_utils.get_all_document_delivered(control_period[0]['id'],
                                                                    auth.has_membership('Ecys-Administrator'),
                                                                    auth.user.username)

                    # Obteniendo listado
                    new_dict['list'] = db.executesql(query, as_dict=True)
        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
    else:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    return dict(action=new_dict)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def manage_items_signature():
    args = request.args
    new_dict = {}

    if len(args) == 0:
        new_dict['type'] = 'list'
        # Obteniendo listado
        query = ds_utils.get_all_item_control_periods()
        new_dict['list'] = db.executesql(query, as_dict=True)

        new_dict['select'], load_label = get_item_period_form_select()
        new_dict['label_button'] = XML(load_label)
        
    elif len(args) == 1:
        option = args[0]
        new_dict['type'] = option

        if option == 'control_period':
            input_period = 0

            if request.env.request_method == "POST":
                is_valid, resultado = ds_utils.validate_form_document_control_period(request.vars)

                if not is_valid:
                    session.flash = resultado['message']
                    redirect(URL('admin', 'manage_items_signature'))

                input_period = resultado['inputPeriod']

            else:
                # validando que venga el parametro period
                #if not request.vars.has_key('period'):
                if not 'period' in request.vars:
                    session.flash = 'No existe período'
                    redirect(URL('admin', 'manage_items_signature'))

                input_period = request.vars.period.strip()

            # validando si existe periodo
            query = ds_utils.get_item_period(input_period)
            item = db.executesql(query, as_dict=True)

            if len(item) < 1:
                session.flash = 'No existe período'
                redirect(URL('admin', 'manage_items_signature'))

            if item[0]['control_period'] == 0:
                m = 'Registro creado exitosamente'

                values = {
                    'period_year': input_period,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'created_by': auth.user.username
                }

                try:
                    insert_query = ds_utils.create_script_string('ds_item_control_period', 'I', values)
                    db.executesql(insert_query)
                except Exception as e:
                    session.flash = str(e)
                    redirect(URL('admin', 'manage_items_signature'))

            # validando que exista control para el periodo
            query_control = ds_utils.get_item_control_period_by_period(item[0]['id'])
            item_control = db.executesql(query_control, as_dict=True)

            if len(item_control) < 1:
                session.flash = 'No existe periodo de firma de entregables'
                redirect(URL('admin', 'manage_items_signature'))

            query_proc = ds_utils.get_call_item_delivered_procedure(item_control[0]['id'], item[0]['id'])

            try:
                db.executesql(query_proc)
            except Exception as e:
                print(str(e))
                session.flash = 'Error al generar registros'
                redirect(URL('admin', 'manage_items_signature'))

            if item[0]['control_period'] != 0:
                m = 'Registro actualizado exitosamente'
                values = {
                    'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'updated_by': auth.user.username
                }

                condition = {'id': item_control[0]['id']}
                try:
                    update_query = ds_utils.create_script_string('ds_item_control_period', 'U', values, condition)
                    db.executesql(update_query)
                except Exception as e:
                    session.flash = str(e)
                    redirect(URL('admin', 'manage_items_signature'))

            session.flash = m
            redirect(URL('admin', 'manage_items_signature'))

        elif option == 'deliverables' or option == 'items':
            # validando que venga el parametro control period
            #TODO CAMBIO DE  if not request.vars.has_key('control_period')
            if not 'control_period' in request.vars:
                session.flash = 'No existe periodo de firma de entregables'
                redirect(URL('admin', 'manage_items_signature'))

            # validando que exista control period
            query = ds_utils.get_item_control_period(request.vars.control_period.strip())
            control_period = db.executesql(query, as_dict=True)

            if len(control_period) < 1:
                session.flash = 'No existe periodo de firma de entregables'
                redirect(URL('admin', 'manage_items_signature'))

            new_dict['control_period'] = control_period[0]['id']
            new_dict['control_period_name'] = T(control_period[0]['name']) + ' - ' + str(control_period[0]['yearp'])

            if option == 'deliverables':
                # Obteniendo listado
                query = ds_utils.get_report_item_delivered(control_period[0]['id'])

                new_dict['list'] = db.executesql(query, as_dict=True)
            else:
                new_dict['document'] = 0
                new_dict['doc_name'] = 'Todos'

                # validando si viene el parametro document
                #TODO CAMBIO DE if request.vars.has_key('document') 
                if 'document' in request.vars:
                    # validando que exista document
                    query = ds_utils.get_item_restriction(request.vars.document.strip())
                    document = db.executesql(query, as_dict=True)

                    if len(document) < 1:
                        session.flash = 'No existe entregable'
                        redirect(URL('admin', 'manage_items_signature'))

                    new_dict['document'] = document[0]['id']
                    new_dict['doc_name'] = document[0]['name']

                    query = ds_utils.get_all_item_delivered(control_period[0]['id'], document[0]['id'])
                else:
                    query = ds_utils.get_all_item_delivered(control_period[0]['id'])

                # Obteniendo listado
                new_dict['list'] = db.executesql(query, as_dict=True)

        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    else:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))


    return dict(action=new_dict)

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def sent_notification_mail(status, delivered, username, user, user_mail, comment=None):
    email_signature = cpfecys.get_custom_parameters().email_signature or ''

    subject = '[DTT]Notificación Automática - Documento ' + ('firmado' if status == 'Signed' else 'rechazado')
    message = '<html>'
    message += 'El documento <b>' + str(delivered.encode('utf8'))  + '</b>'
    message += '<br/>'
    message += 'enviado por el estudiante: ' + str(username.encode('utf8')) + ' - ' + str(user.encode('utf8'))
    message += '<br/>'

    if status == 'Signed':
        message += 'ya se encuentra firmado.'
        message += '<br/><br/>'
        message += 'Puede proceder a descargar el documento.'
        message += '<br/>'
        message += T('DTT-ECYS') + ' ' + cpfecys.get_domain()
    else:
        message += 'ha sido rechazado, la razón es: ' + ('' if comment is None else comment) + '.'
        message += '<br/><br/>'
        message += 'Tome medidas para que no afecte su proceso de finalización de prácticas finales.'
        message += '<br/>'
        message += T('DTT-ECYS') + ' ' + cpfecys.get_domain()

    message += '<br/>'
    message += email_signature + '</html>'

    print(message)
    message = 'Este es un ejemplo'
    if user_mail is not None or len(user_mail) != 0:
        was_sent = mail.send(to=user_mail, subject=subject, message=message, encoding='utf-8')

        # MAILER LOG
        db.mailer_log.insert(sent_message=message, destination=str(user_mail),
                             result_log=str(mail.error or '') + ':' + str(mail.result), success=was_sent)

        return was_sent

    return False

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def change_date_delivered():
    args = request.args

    #validando que exista entregable
    query = ds_utils.get_document_delivered(args[0])
    document = db.executesql(query, as_dict=True)

    if len(document) < 1:
        session.flash = 'No existe entregable'
    else:
        is_valid, resultado = ds_utils.validate_form_dates_delivered(request.vars)

        if is_valid:
            values = {
                'date_start': resultado['inputStart'],
                'date_finish': resultado['inputFinish']
            }

            condition = {'id': document[0]['id']}
            try:
                update_query = ds_utils.create_script_string('ds_document_delivered', 'U', values, condition)
                db.executesql(update_query)
                session.flash = 'Fecha de entrega actualizada'
            except Exception as e:
                print('********** admin - change deliverable status **********')
                print(str(e))
                session.flash = 'Error al actualizar fecha de entrega'
        else:
            session.flash = resultado['message']

    # validando si viene el parametro document
    #if request.vars.has_key('document'):
    if 'document' in request.vars:
        redirect(URL('admin', 'manage_deliverables', args=['items'],
                     vars=dict(control_period=request.vars.control_period.strip(), type=request.vars.type.strip(), document=request.vars.document.strip())))
    else:
        redirect(URL('admin', 'manage_deliverables', args=['items'],
                     vars=dict(control_period=request.vars.control_period.strip(), type=request.vars.type.strip())))

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def change_deliverable_status():
    #if not request.vars.has_key('item'):
    if not 'item' in request.vars:
        return response.json({'ok': 0, 'message': 'No existe entregable'})

    #if not request.vars.has_key('action'):
    if not 'action' in request.vars:
        return response.json({'ok': 0, 'message': 'No existe acción'})

    id_doc = request.vars.item.strip()
    comment = request.vars.comment.strip()
    action = request.vars.action.strip()
    comment = None if (comment == "" or len(comment) == 0) else comment

    if not (action == '3' or action == '4' or action  == '5'):
        return response.json({'ok': 0, 'message': 'No existe acción'})

    # validando que exista document delivered
    if action == '5':
        query = ds_utils.get_document_delivered(id_doc)
    else:
        query = ds_utils.get_document_delivered_to_sign(id_doc)

    document = db.executesql(query, as_dict=True)
    print('documento', document)

    if len(document) < 1:
        return response.json({'ok': 0, 'message': 'No existe entregable'})

    if document[0]['status'] == 'Pending':
        return response.json({'ok': 0, 'message': 'Entregable pendiente de entrega'})

    if document[0]['file_uploaded'] is None:
        return response.json({'ok': 0, 'message': 'No se encontro el archivo'})

    if action != '5':
        if document[0]['is_enabled'] == 'F':
            return response.json({'ok': 0, 'message': 'Entregable no está habilitado'})

        if document[0]['is_active'] == 'F':
            return response.json({'ok': 0, 'message': 'Entregable no está activo'})

        if document[0]['signature_required'] == 'F':
            return response.json({'ok': 0, 'message': 'Entregable no requiere firma'})

        if document[0]['doc_type'] == 'Practice Finished' and document[0]['assignation_status'] != 'Successful':
            return response.json({'ok': 0, 'message': 'Estado de asignación no es exitosa'})
    else:
        if comment is None:
            return response.json({'ok': 0, 'message': 'Debe ingresar un comentario para rechazar el documento'})

    if action == '3':  # pendiente de firma
        stat = 'Revised'
        message = '<span class="badge badge-warning">Revisado</span>'
        alert = 'Documento revisado'
    elif action == '4':  # firmado
        if not (document[0]['status'] == 'Revised' or document[0]['status'] == 'Signed'):
            return response.json({'ok': 0, 'message': 'Entregable pendiente de revision'})

        stat = 'Signed'
        message = '<span class="badge badge-info">Firmado</span>'
        alert = 'Documento firmado'
    else:  # rechazado
        stat = 'Rejected'
        message = '<span class="badge badge-danger">Rechazado</span>'
        alert = 'Documento rechazado'

    if action == '4':
        query_sig = ds_utils.get_signatures_by_document(document[0]['document'])
        signatures = db.executesql(query_sig, as_dict=True)
        print('signatures', signatures)

        if len(signatures) < 1:
            return response.json({'ok': 0, 'message': 'Documento no tiene firmas asociadas'})

        document_base = ds_utils.encode_delivered_id(document[0]['id'])
        print(document_base)

        url = f"{request.env.wsgi_url_scheme}://{request.env.http_host}{URL('default', 'file_validation', args=['document', document_base])}"
        print('url', url)
        try:
            result_sign, status_sign = ds_utils.sign_file(request.folder, document[0]['file_uploaded'], url, signatures, auth.user.username, document[0]['signed_file'])
        except Exception as e:
            print('a ver', e)
        print(result_sign, status_sign)

        if status_sign == 0:
            return response.json({'ok': 0, 'message': result_sign})

        doc_signed = result_sign
        values = {
            'comment': comment,
            'status': stat,
            'signed_file': result_sign
        }
        #was_sent = sent_notification_mail(stat, document[0]['deliverable'], document[0]['username'],
        #                                  document[0]['user'], document[0]['email'])
        #print(was_sent)
        # values['notified_mail'] = 'T' if was_sent else 'F'
    else:
        doc_signed = document[0]['file_uploaded']
        values = {
            'comment': comment,
            'status': stat
        }
        # if action == '5':
        #     was_sent = sent_notification_mail(stat, document[0]['deliverable'], document[0]['username'],
        #                                       document[0]['user'], document[0]['email'], comment)
        #     values['notified_mail'] = 'T' if was_sent else 'F'

    condition = {'id': int(id_doc)}
    try:
        update_query = ds_utils.create_script_string('ds_document_delivered', 'U', values, condition)
        db.executesql(update_query)
    except Exception as e:
        print('********** admin - change deliverable status **********')
        print(str(e))
        return response.json({'ok': 0, 'message': str(e)})

    # agregando bitacora de rechazos
    if action == '5':
        values_log = {
            'document_name': document[0]['deliverable'],
            'status': stat,
            'comment': comment,
            'ref_delivered': document[0]['id'],
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'created_by': auth.user.username
        }

        try:
            insert_query = ds_utils.create_script_string('ds_document_delivered_log', 'I', values_log)
            db.executesql(insert_query)
        except Exception as e:
            print('********** admin - change deliverable status **********')
            print(str(e))
            return response.json({'ok': 0, 'message': str(e)})

    return response.json(
        {'ok': 1, 'message': message, 'uploaded': document[0]['file_uploaded'], 'signed': doc_signed, 'alert': alert})

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def change_item_status():
    #if not request.vars.has_key('item'):
    if  not 'item' in request.vars:
        return response.json({'ok': 0, 'message': 'No existe item'})

    #if not request.vars.has_key('action'):
    if not 'action' in request.vars:
        return response.json({'ok': 0, 'message': 'No existe acción'})

    id_item = request.vars.item.strip()
    comment = request.vars.comment.strip()
    action = request.vars.action.strip()
    comment = None if (comment == "" or len(comment) == 0) else comment

    if not (action == '3' or action == '4' or action  == '5'):
        return response.json({'ok': 0, 'message': 'No existe acción'})

    # validando que exista item delivered
    query = ds_utils.get_item_delivered(id_item)
    document = db.executesql(query, as_dict=True)

    if len(document) < 1:
        return response.json({'ok': 0, 'message': 'No existe entregable'})

    if document[0]['status'] == 'Pending':
        return response.json({'ok': 0, 'message': 'Entregable pendiente de entrega'})

    if document[0]['uploaded_file'] is None:
        return response.json({'ok': 0, 'message': 'No se encontro el archivo'})

    if action != '5':
        if document[0]['is_enabled'] == 'F':
            return response.json({'ok': 0, 'message': 'Entregable no está habilitado'})

        if document[0]['is_active'] == 'F':
            return response.json({'ok': 0, 'message': 'Entregable no está activo'})
    else:
        if comment is None:
            return response.json({'ok': 0, 'message': 'Debe ingresar un comentario para rechazar el documento'})

    if action == '3':  # pendiente de firma
        stat = 'Revised'
        message = '<span class="badge badge-warning">Revisado</span>'
        alert = 'Documento revisado'
    elif action == '4':  # firmado
        if not (document[0]['status'] == 'Revised' or document[0]['status'] == 'Signed'):
            return response.json({'ok': 0, 'message': 'Entregable pendiente de revision'})

        stat = 'Signed'
        message = '<span class="badge badge-info">Firmado</span>'
        alert = 'Documento firmado'
    else:  # rechazado
        stat = 'Rejected'
        message = '<span class="badge badge-danger">Rechazado</span>'
        alert = 'Documento rechazado'

    if action == '4':
        query_sig = ds_utils.get_signatures_by_item(document[0]['item_restriction'])
        signatures = db.executesql(query_sig, as_dict=True)

        if len(signatures) < 1:
            return response.json({'ok': 0, 'message': 'Documento no tiene firmas asociadas'})

        document_base = ds_utils.encode_delivered_id(document[0]['id'])

        url = "%s://%s%s" % (request.env.wsgi_url_scheme, request.env.http_host,
                             URL('default', 'file_validation', args=['document', document_base],
                                 vars=dict(ref='item')))
        #print(url)
        result_sign, status_sign = ds_utils.sign_file(request.folder, document[0]['uploaded_file'], url, signatures,
                                                      auth.user.username, document[0]['signed_file'],
                                                      document[0]['username'])

        if status_sign == 0:
            return response.json({'ok': 0, 'message': result_sign})

        doc_signed = URL('admin', 'download_item', args=[result_sign])
        values = {
            'status': stat,
            'signed_file': result_sign
        }

        values2 = {
            'admin_comment': comment
        }

        #was_sent = sent_notification_mail(stat, document[0]['deliverable'], document[0]['username'],
        #                                  document[0]['user'], document[0]['email'])
        #print(was_sent)
        # values['notified_mail'] = 'T' if was_sent else 'F'

    else:
        doc_signed = URL('admin', 'download', args=[document[0]['uploaded_file']])
        values = {
            'status': stat
        }

        values2 = {
            'admin_comment': comment
        }

        # if action == '5':
        #     was_sent = sent_notification_mail(stat, document[0]['deliverable'], document[0]['username'],
        #                                       document[0]['user'], document[0]['email'], comment)
        #     values['notified_mail'] = 'T' if was_sent else 'F'

    condition = {'id': int(id_item)}
    try:
        update_query = ds_utils.create_script_string('ds_item_delivered', 'U', values, condition)
        db.executesql(update_query)
    except Exception as e:
        print('********** admin - change item status **********')
        print(str(e))
        return response.json({'ok': 0, 'message': str(e)})

    condition = {'id': document[0]['item']}
    try:
        update_query = ds_utils.create_script_string('item', 'U', values2, condition)
        db.executesql(update_query)
    except Exception as e:
        print('********** admin - change item status **********')
        print(str(e))
        return response.json({'ok': 0, 'message': str(e)})

    # agregando bitacora de rechazos
    if action == '5':
        values_log = {
            'document_name': document[0]['deliverable'],
            'status': stat,
            'comment': comment,
            'ref_delivered': document[0]['id'],
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'created_by': auth.user.username
        }

        try:
            insert_query = ds_utils.create_script_string('ds_item_delivered_log', 'I', values_log)
            db.executesql(insert_query)
        except Exception as e:
            print('********** admin - change item status **********')
            print(str(e))
            return response.json({'ok': 0, 'message': str(e)})

    return response.json({'ok': 1, 'message': message, 'signed': doc_signed, 'alert': alert})

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def enable_disable_delivered():
    #if not request.vars.has_key('item'):
    if not 'item' in request.vars:
        return response.json({'ok': 0, 'message': 'No existe entregable'})

    id = request.vars.item.strip()
    # validando que exista document delivered
    query = ds_utils.get_document_delivered(id)
    document = db.executesql(query, as_dict=True)

    if len(document) < 1:
        return response.json({ 'ok' : 0, 'message' : 'No existe entregable' })

    comment = request.vars.comment.strip()
    comment = None if comment == "" or len(comment) == 0 else comment
    values = {
        'comment': comment,
        'is_enabled': 'F' if document[0]['is_enabled'] == 'T' else 'T'
    }

    condition = {'id': int(id)}
    try:
        update_query = ds_utils.create_script_string('ds_document_delivered', 'U', values, condition)
        db.executesql(update_query)
    except Exception as e:
        print('********** admin - enable disable delivered **********')
        print(str(e))
        return response.json({ 'ok' : 0, 'message' : str(e) })

    return response.json({ 'ok' : 1, 'message' : 'exitoso' })

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def enable_disable_item():
    #if not request.vars.has_key('item'):
    if not 'item' in request.vars:
        return response.json({'ok': 0, 'message': 'No existe item'})

    id_item = request.vars.item.strip()
    # validando que exista item delivered
    query = ds_utils.get_item_delivered(id_item)
    document = db.executesql(query, as_dict=True)

    if len(document) < 1:
        return response.json({ 'ok' : 0, 'message' : 'No existe item' })

    comment = request.vars.comment.strip()
    comment = None if comment == "" or len(comment) == 0 else comment
    values = {
        'admin_comment': comment,
        'is_active': 'F' if document[0]['is_active'] == 'T' else 'T'
    }

    condition = {'id': document[0]['item']}
    try:
        update_query = ds_utils.create_script_string('item', 'U', values, condition)
        db.executesql(update_query)
    except Exception as e:
        print('********** admin - enable disable item **********')
        print(str(e))
        return response.json({'ok': 0, 'message': str(e)})

    return response.json({'ok': 1, 'message': 'exitoso'})

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def update_all_deliverables():
    #if not request.vars.has_key('control_period'):
    if not 'control_period' in request.vars:
        session.flash = 'No existe gestión de entregables'
        redirect(URL('admin', 'manage_deliverables'))
    #elif not request.vars.has_key('type'):
    elif not 'type' in request.vars:
        session.flash = 'No existe tipo de entregable'
        redirect(URL('admin', 'manage_deliverables'))
    #elif not request.vars.has_key('status') and not request.vars.has_key('enable'):
    elif not 'status' in request.vars and not 'enable' in request.vars:
        session.flash = 'Acción no disponible'
        redirect(URL('admin', 'manage_deliverables'))

    deliverable_type = request.vars.type.strip()
    if not (deliverable_type == '0' or deliverable_type == '1'):
        session.flash = 'No existe tipo de entregable'
        redirect(URL('admin', 'manage_deliverables'))

    control_period = request.vars.control_period.strip()
    type_d = ds_utils.get_deliverable_type(deliverable_type)
    document = request.vars.document.strip() if 'document' in request.vars else None
    status = request.vars.status.strip() if 'status' in request.vars else None
    enable = request.vars.enable.strip() if 'enable' in request.vars else None

    operator = ' IN '
    # verificando si habilitar o deshabilitar entregable
    if enable is not None and (enable == '0' or enable == '1'):
        select_query = ds_utils.get_all_document_delivered_to_change(control_period, type_d[2], document)
        elements = db.executesql(select_query, as_dict=True)

        if len(elements) < 1:
            values_in = '(0)'
        else:
            values_in = '(' + ds_utils.get_string_separated(elements) + ')'

        values = {
            'is_enabled': 'F' if enable == '0' else 'T'
        }

    elif enable is not None and not (enable == '0' or enable == '1'):
        session.flash = 'Acción no disponible'
        redirect(URL('admin', 'manage_deliverables'))

    if status is not None:
        if not (status == '3' or status == '4'):
            session.flash = 'Acción no disponible'
            redirect(URL('admin', 'manage_deliverables'))

        # obteniendo los registros que requieren firma
        if status == '3':
            stat = 'Delivered'
            status = 'Revised'
        else:
            stat = 'Revised'
            status = 'Signed'

        select_query = ds_utils.get_all_document_delivered_to_sign(control_period, stat, type_d[2],
                                                                   auth.has_membership('Ecys-Administrator'),
                                                                   auth.user.username, document)

        elements = db.executesql(select_query, as_dict=True)

        if status == 'Revised':
            if len(elements) < 1:
                values_in = '(0)'
            else:
                values_in = '(' + ds_utils.get_string_separated(elements) + ')'

            values = {
                'status': status
            }
        else:
            for doc in elements:
                query_sig = ds_utils.get_signatures_by_document(doc['document'])
                signatures = db.executesql(query_sig, as_dict=True)

                if len(signatures) < 1:
                    session.flash = 'Documento no tiene firmas asociadas'
                    redirect(URL('admin', 'manage_deliverables', args=['deliverables'],
                                 vars=dict(control_period=control_period, type=deliverable_type)))

                document_base = ds_utils.encode_delivered_id(doc['id'])

                url = "%s://%s%s" % (request.env.wsgi_url_scheme, request.env.http_host,
                                     URL('default', 'file_validation', args=['document', document_base]))

                result_sign, status_sign = ds_utils.sign_file(request.folder, doc['file_uploaded'], url,
                                                              signatures, auth.user.username, doc['signed_file'])

                if status_sign == 0:
                    # ===== Modificación Documentos Rechazados (Juan Pablo Ardón López - Prácticas Finales) =====
                    values = {
                        'status': 'Rejected',
                        'notified_mail': 'F',
                        'comment': 'No se pudo firmar el documento. Utilice una herramienta para desbloquearlo y vuelva a subirlo.'
                    }
                    condition = {'id': doc['id']}
                    try:
                        update_query = ds_utils.create_script_string('ds_document_delivered', 'U', values, condition)
                        db.executesql(update_query)
                    except Exception as e:
                        print('********** admin - update all deliverables **********')
                        print(str(e))
                        session.flash = 'Error al firmar documentos'
                        redirect(URL('admin', 'manage_deliverables', args=['deliverables'],
                                    vars=dict(control_period=control_period, type=deliverable_type)))
                    # ===== Termina Modificación Documentos Rechazados (Juan Pablo Ardón López - Prácticas Finales) =====
                    #print(result_sign)
                    continue

                # was_sent = sent_notification_mail(status, doc['name'], doc['username'], doc['user'], doc['email'])
                was_sent = 'F'
                values = {
                    'status': status,
                    'signed_file': result_sign,
                    'notified_mail': was_sent
                }

                condition = {'id': doc['id']}
                try:
                    update_query = ds_utils.create_script_string('ds_document_delivered', 'U', values, condition)
                    db.executesql(update_query)
                except Exception as e:
                    print('********** admin - update all deliverables **********')
                    print(str(e))
                    session.flash = 'Error al firmar documentos'
                    redirect(URL('admin', 'manage_deliverables', args=['deliverables'],
                                 vars=dict(control_period=control_period, type=deliverable_type)))

            session.flash = 'Archivos firmados exitosamente'
            redirect(URL('admin', 'manage_deliverables', args=['deliverables'], vars=dict(control_period=control_period, type=deliverable_type)))

    condition = {'id': values_in}
    try:
        update_query = ds_utils.create_script_string('ds_document_delivered', 'U', values, condition, operator)
        db.executesql(update_query)
        session.flash = 'Registros actualizados exitosamente'
    except Exception as e:
        session.flash = 'Error al realizar actualización'
        print('********** admin - update all deliverables **********')
        print(str(e))

    redirect(URL('admin', 'manage_deliverables', args=['deliverables'], vars=dict(control_period=control_period, type=deliverable_type)))

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def update_all_items():
    #if not request.vars.has_key('control_period'):
    if not 'control_preiod' in request.vars:
        session.flash = 'No se encontro parámetro control_period'
        redirect(URL('admin', 'manage_items_signature'))
    #elif not request.vars.has_key('status') and not request.vars.has_key('enable'):
    elif not 'status' in request.vars and not 'enable' in request.vars:
        session.flash = 'Acción no disponible'
        redirect(URL('admin', 'manage_items_signature'))

    control_period = request.vars.control_period.strip()
    document = request.vars.document.strip() if 'document' in request.vars else None
    status = request.vars.status.strip() if 'status' in request.vars else None
    enable = request.vars.enable.strip() if 'enable' in request.vars else None

    operator = ' IN '
    # verificando si habilitar o deshabilitar entregable
    if enable is not None and (enable == '0' or enable == '1'):
        select_query = ds_utils.get_all_items_delivered_to_change(control_period, document)
        elements = db.executesql(select_query, as_dict=True)

        if len(elements) < 1:
            values_in = '(0)'
        else:
            values_in = '(' + ds_utils.get_string_separated(elements) + ')'

        values = {
            'is_active': 'F' if enable == '0' else 'T'
        }

        condition = {'id': values_in}
        try:
            update_query = ds_utils.create_script_string('item', 'U', values, condition, operator)
            db.executesql(update_query)
            session.flash = 'Registros actualizados exitosamente'
        except Exception as e:
            session.flash = 'Error al realizar actualización'
            print('********** admin - update all items **********')
            print(str(e))

    elif enable is not None and not (enable == '0' or enable == '1'):
        session.flash = 'Acción no disponible'
        redirect(URL('admin', 'manage_items_signature'))

    if status is not None:
        if not (status == '3' or status == '4'):
            session.flash = 'Acción no disponible'
            redirect(URL('admin', 'manage_items_signature'))

        # obteniendo los registros que requieren firma
        if status == '3':
            stat = 'Delivered'
            status = 'Revised'
        else:
            stat = 'Revised'
            status = 'Signed'

        select_query = ds_utils.get_all_items_delivered_to_sign(control_period, stat, document)
        elements = db.executesql(select_query, as_dict=True)

        if status == 'Revised':
            if len(elements) < 1:
                values_in = '(0)'
            else:
                values_in = '(' + ds_utils.get_string_separated(elements) + ')'

            values = {
                'status': status
            }

            condition = {'id': values_in}
            try:
                update_query = ds_utils.create_script_string('ds_item_delivered', 'U', values, condition, operator)
                db.executesql(update_query)
                session.flash = 'Registros actualizados exitosamente'
            except Exception as e:
                session.flash = 'Error al realizar actualización'
                print('********** admin - update all items **********')
                print(str(e))
        else:
            for doc in elements:
                query_sig = ds_utils.get_signatures_by_item(doc['item_restriction'])
                signatures = db.executesql(query_sig, as_dict=True)

                if len(signatures) < 1:
                    session.flash = 'Documento no tiene firmas asociadas'
                    redirect(URL('admin', 'manage_items_signature', args=['deliverables'],
                                 vars=dict(control_period=control_period)))

                document_base = ds_utils.encode_delivered_id(doc['id'])

                url = "%s://%s%s" % (request.env.wsgi_url_scheme, request.env.http_host,
                                     URL('default', 'file_validation', args=['document', document_base],
                                         vars=dict(ref='item')))

                result_sign, status_sign = ds_utils.sign_file(request.folder, doc['uploaded_file'], url,
                                                              signatures, auth.user.username, doc['signed_file'],
                                                              doc['username'])

                if status_sign == 0:
                    continue

                # was_sent = sent_notification_mail(status, doc['name'], doc['username'], doc['user'], doc['email'])
                was_sent = 'F'
                values = {
                    'status': status,
                    'signed_file': result_sign
                }

                condition = {'id': doc['id']}
                try:
                    update_query = ds_utils.create_script_string('ds_item_delivered', 'U', values, condition)
                    db.executesql(update_query)
                except Exception as e:
                    print('********** admin - update all items **********')
                    print(str(e))

            session.flash = 'Archivos firmados exitosamente'

    redirect(URL('admin', 'manage_items_signature', args=['deliverables'], vars=dict(control_period=control_period)))

@cache.action()
@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def download_deliverable():
    args = request.args

    if len(args) == 0:
        #if not request.vars.has_key('control_period'):
        if not 'control_period' in request.vars:
            print('********** admin - download deliverable **********')
            print('No se encontro parámetro control_period')
            raise HTTP(404)

        #if not request.vars.has_key('type'):
        if not 'type' in request.vars:
            print('********** admin - download deliverable **********')
            print('No se encontro parámetro type')
            raise HTTP(404)

        #if not request.vars.has_key('delivered'):
        if not 'delivered' in request.vars:
            print('********** admin - download deliverable **********')
            print('No se encontro parámetro delivered')
            raise HTTP(404)

        type_p = request.vars.type.strip()
        delivered_p = request.vars.delivered.strip()

        if not (type_p == '0' or type_p == '1'):
            print('********** admin - download deliverable **********')
            print('No se encontro parámetro type')
            raise HTTP(404)
        elif not (delivered_p == '0' or delivered_p == '1'):
            print('********** admin - download deliverable **********')
            print('No se encontro parámetro delivered')
            raise HTTP(404)

        type_d = ds_utils.get_deliverable_type(type_p)

        #if request.vars.has_key('document'):
        if 'document' in request.vars:
            query = ds_utils.get_all_document_delivered_filename(request.vars.control_period.strip(), type_d[2],
                                                                 delivered_p,
                                                                 auth.has_membership('Ecys-Administrator'),
                                                                 auth.user.username,
                                                                 request.vars.document.strip())
        else:
            query = ds_utils.get_all_document_delivered_filename(request.vars.control_period.strip(), type_d[2],
                                                                 delivered_p,
                                                                 auth.has_membership('Ecys-Administrator'),
                                                                 auth.user.username)

        list_files = db.executesql(query, as_dict=True)
        if len(list_files) == 0:
            redirect(URL('admin', 'manage_deliverables', args=['deliverables'],
                         vars=dict(control_period=request.vars.control_period.strip(), type=type_p)))

        filename = ds_utils.retrieve_zip_file(request.folder, list_files, auth.user.username)
        if filename is None:
            session.flash = 'No se encontro el archivo'
            redirect(URL('admin', 'manage_deliverables', args=['deliverables'],
                         vars=dict(control_period=request.vars.control_period.strip(), type=type_p)))

    elif len(args) == 1:
        filename = args[0].strip()
    else:
        raise HTTP(404)

    try:
        file = ds_utils.retrieve_file(filename, request.folder)
    except Exception as e:
        print('********** admin - download deliverable **********')
        print(str(e))
        session.flash = 'No se encontro el archivo'
        redirect(URL('admin', 'manage_deliverables', args=['deliverables'],
                     vars=dict(control_period=request.vars.control_period.strip(), type=type_p)))

    response.headers["Content-Type"] = c.contenttype(filename)
    response.headers["Content-Disposition"] = "attachment; filename=%s" % filename
    stream = response.stream(file, request=request)

    raise HTTP(200, stream, **response.headers)

@cache.action()
@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def download_item():
    args = request.args

    if len(args) == 0:
        #if not request.vars.has_key('control_period'):
        if not 'control_period' in request.vars:
            print('********** admin - download item **********')
            print('No se encontro parámetro control_period')
            raise HTTP(404)

        #if not request.vars.has_key('delivered'):
        if not 'delivered' in request.vars:
            print('********** admin - download item **********')
            print('No se encontro parámetro delivered')
            raise HTTP(404)

        delivered_p = request.vars.delivered.strip()

        if not (delivered_p == '0' or delivered_p == '1'):
            print('********** admin - download item **********')
            print('No se encontro parámetro delivered')
            raise HTTP(404)

        #if request.vars.has_key('document'):
        if 'document' in request.vars:
            query = ds_utils.get_all_item_delivered_filename(request.vars.control_period.strip(),
                                                                 delivered_p,
                                                                 request.vars.document.strip())
        else:
            query = ds_utils.get_all_item_delivered_filename(request.vars.control_period.strip(),
                                                                 delivered_p)

        list_files = db.executesql(query, as_dict=True)
        if len(list_files) == 0:
            redirect(URL('admin', 'manage_items_signature', args=['deliverables'],
                         vars=dict(control_period=request.vars.control_period.strip())))

        filename = ds_utils.retrieve_zip_file(request.folder, list_files, auth.user.username)
        if filename is None:
            session.flash = 'No se encontro el archivo'
            redirect(URL('admin', 'manage_items_signature', args=['deliverables'],
                         vars=dict(control_period=request.vars.control_period.strip())))

    elif len(args) == 1:
        filename = args[0].strip()
    else:
        raise HTTP(404)

    try:
        file = ds_utils.retrieve_file(filename, request.folder)
    except Exception as e:
        print('********** admin - download deliverable **********')
        print(str(e))
        session.flash = 'No se encontro el archivo'
        redirect(URL('admin', 'manage_items_signature', args=['deliverables'],
                     vars=dict(control_period=request.vars.control_period.strip())))

    response.headers["Content-Type"] = c.contenttype(filename)
    response.headers["Content-Disposition"] = "attachment; filename=%s" % filename
    stream = response.stream(file, request=request)

    raise HTTP(200, stream, **response.headers)

@cache.action()
@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def download_signature():
    filename = request.args[0].strip()
    fullpath = ds_utils.get_signature_path(request.folder, filename)
    response.stream(fullpath)

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def get_period_form_select(actual_period=None):
    query = ds_utils.get_all_periods()
    periods = db.executesql(query, as_dict=True)

    period_options = list()
    period_options.append(OPTION("", _value=0))
    contador = 1
    load_label = ''
    for period in periods:
        period_options.append(OPTION((T(period['name']) + ' - ' + str(period['yearp'])), _value=period['id'],
                                    _selected=(True if (actual_period == str(period['id'])) else False)))

        if contador == 15: break
        contador = contador + 1

    load_label += '<button id="btn_control" type="submit" class="btn btn-primary">'
    load_label += '<span class="icon plus icon-plus glyphicon glyphicon-plus"></span>'
    load_label += '&nbsp;Crear</button>'

    return SELECT(period_options, _name='inputPeriod', _id='inputPeriod', _class="form-control"), load_label

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def get_item_period_form_select(actual_period=None):
    query = ds_utils.get_all_item_periods()
    periods = db.executesql(query, as_dict=True)

    periodOptions = list()
    periodOptions.append(OPTION("", _value=0))
    contador = 1
    load_label = ''
    for period in periods:
        periodOptions.append(OPTION((T(period['name']) + ' - ' + str(period['yearp'])), _value=period['id'],
                                    _selected=(True if (actual_period == str(period['id'])) else False)))

        if contador == 15: break
        contador = contador + 1

    load_label += '<button id="btn_control" type="submit" class="btn btn-primary">'
    load_label += '<span class="icon plus icon-plus glyphicon glyphicon-plus"></span>'
    load_label += '&nbsp;Crear</button>'
 
    return SELECT(periodOptions, _name='inputPeriod', _id='inputPeriod', _class="form-control"), load_label

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def get_project_form_select(area_level, sig=None):
    query = ds_utils.get_all_projects(area_level)
    all_projects = db.executesql(query, as_dict=True)

    projects_options = list()
    projects_options.append(OPTION("", _value=0))
    for project in all_projects:
        projects_options.append(
            OPTION(project['name'], _value=project['id'], _selected=(True if sig == str(project['id']) else False)))

    return SELECT(projects_options, _name='inputProject', _id='inputProject', _class="form-control")

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def get_area_level_form_select(sig=None):
    query = ds_utils.get_all_area_level()
    all_areas = db.executesql(query, as_dict=True)

    areas_options = list()
    areas_options.append(OPTION("", _value=0))
    for area in all_areas:
        areas_options.append(OPTION(area['name'], _value=area['id'], _selected=(True if sig == str(area['id']) else False)))

    return SELECT(areas_options, _name='inputArea', _id='inputArea', _class="form-control")

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def get_signature_form_select(sig=None):
    query = ds_utils.get_all_signatures(auth.user.username, True)
    signatures = db.executesql(query, as_dict=True)

    signature_options = list()
    signature_options.append(OPTION("", _value=0))
    for signature in signatures:
        signature_options.append(OPTION(signature['name'], _value=signature['id'], _selected=(True if sig == str(signature['id']) else False)))

    return SELECT(signature_options, _name='inputSignature', _id='inputSignature', _class="form-control")

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def get_signature_type_form_select(type_signature=None):
    type_options = list()
    type_options.append(OPTION("", _value=0))
    type_options.append(OPTION("Código QR", _value="QR", _selected=(True if type_signature=="QR Code" else False)))
    type_options.append(OPTION("Firma Digital", _value="DS", _selected=(True if type_signature=="Digital Signature" else False)))

    return SELECT(type_options, _name='inputType', _id='inputType', _class="form-control")

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def get_file_type_form_select(type=None):
    query = ds_utils.get_all_file_types()
    fileTypes = db.executesql(query, as_dict=True)

    type_options = list()
    type_options.append(OPTION("", _value=0))
    for fileType in fileTypes:
        type_options.append(OPTION(fileType['name'], _value=fileType['id'], _selected=(True if type == str(fileType['id']) else False)))

    return SELECT(type_options, _name='inputTypeFile', _id='inputTypeFile', _class="form-control")

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def get_document_type_form_select(type=None):
    type_options = list()
    type_options.append(OPTION("", _value=0))
    type_options.append(OPTION("Práctica inicia", _value="PS", _selected=(True if type=="Practice Start" else False)))
    type_options.append(OPTION("Práctica finaliza", _value="PE", _selected=(True if type=="Practice Finished" else False)))

    return SELECT(type_options, _name='inputDocumentType', _id='inputDocumentType', _class="form-control")

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def get_max_size_form_select(size="0"):
    size_options = list()
    size_options.append(OPTION("", _value=0))

    for contador in range(1,11):
        size_options.append(OPTION(str(contador), _value=str(contador), _selected=(True if int(size) == contador else False)))

    return SELECT(size_options, _name='inputSize', _id='inputSize', _class="form-control")

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def get_signature_assignment_checkbox_form(active=False):
    return INPUT(_type='checkbox', _name='inputActivate', _id='inputActivate', _class="form-check-input", value=active)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def get_document_restrictions_checkbox_form(enabled=False):
    return INPUT(_type='checkbox', _name='inputEnabled', _id='inputEnabled', _class="form-check-input",
                 _value='1', value=enabled)

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def get_document_checkbox_form(optional=False, signature=False):
    result = {'checkActivate': INPUT(_type='checkbox', _name='inputActivate', _id='inputActivate',
                                     _class="form-check-input", _value='1', value=optional),
              'checkSignature': INPUT(_type='checkbox', _name='inputSignature', _id='inputSignature',
                                      _class="form-check-input", _value='1', value=signature)}
    return result

#*********** Fin - Prácticas Finales(DS) - Fernando Reyes *************

#*********** Inicio - Practicas Finales (Firma Digital Lingüistica) - Juan Pablo Ardón ************

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def manage_signature_linguistica():
    args = request.args
    new_dict = {}

    if len(args) == 0:
        new_dict['type'] = 'list'
        # Obteniendo listado
        query = ds_utils.get_all_signatures(auth.user.username, auth.has_membership('Super-Administrator'))
        new_dict['list'] = db.executesql(query, as_dict=True)
    
    elif len(args) == 1:
        option = args[0]
        new_dict['type'] = option
        
        if option == 'new':
            if request.env.request_method == "POST":
                is_valid, resultado = ds_utils.validate_form_signature(request.vars)
                new_dict['item'] = resultado
                new_dict['select'] = get_signature_type_form_select(resultado['inputType'])

                if not is_valid:
                    new_dict['message'] = resultado['message']
                    return dict(action=new_dict)

                values = {
                    'name': resultado['inputName'],
                    'signature_type': resultado['inputType'],
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'created_by': auth.user.username
                }

                try:
                    insert_query = ds_utils.create_script_string('ds_signature', 'I', values)
                    db.executesql(insert_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)

                session.flash = 'Registro creado exitosamente'
                redirect(URL('admin', 'manage_signature'))

            else:
                new_dict['select'] = get_signature_type_form_select()

        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    return dict(action=new_dict)

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def manage_deliverables_ecys():

    args = request.args
    new_dict = {}

    if len(args) == 0:
        new_dict['type'] = 'list'
        # Obtener listado de semestres
        query = dsa_utils_temp.get_delivered_document_period()
        new_dict['list'] = db.executesql(query, as_dict=True)
        new_dict['is_admin'] = auth.has_membership('Super-Administrator')
    
    elif len(args) ==1:

        #if not request.vars.has_key('period') or not request.vars.has_key('year'):
        if not 'period' in request.vars or not 'year' in request.vars:
                session.flash = 'No existe periodo'
                redirect(URL('admin','manage_deliverables_ecys'))

        option = args[0]
        new_dict['type'] = option
        new_dict['is_admin'] = auth.has_membership('Super-Administrator')
        new_dict['period'] = request.vars.period.strip()
        new_dict['year'] = request.vars.year.strip()

        year = request.vars.year.strip()
        symbol = ''
        if request.vars.period.strip() == 'Primer Semestre':
            symbol = '<='
        else:
            symbol = '>'

        if option == 'deliverable_role':
            
            query = dsa_utils_temp.get_document_roles(symbol, year)
            new_dict['list'] = db.executesql(query, as_dict=True)


        if option == 'deliverable_type':
            
            #if not request.vars.has_key('idrole') or not request.vars.has_key('rolename'):
            if not 'idrole' in request.vars or not 'rolename' in request.vars:
                session.flash = 'No existe rol'
                redirect(URL('admin','manage_deliverables_ecys'))
            
            new_dict['rolename'] = request.vars.rolename.strip()
            role = request.vars.idrole.strip()
            new_dict['idrole'] = role
            query = dsa_utils_temp.get_documents_type_by_period(role,symbol,year)
            new_dict['list'] = db.executesql(query,as_dict=True)

        
        if option == 'deliverables':

            #if not request.vars.has_key('name') or not request.vars.has_key('document') or not request.vars.has_key('rolename') or not request.vars.has_key('idrole'):
            if not 'name' in request.vars or not 'document' in request.vars or not 'rolename' in request.vars or not 'idrole' in request.vars:
                session.flash = 'No existe entregable'
                redirect(URL('admin','manage_deliverables_ecys'))

            new_dict['idrole'] = request.vars.idrole.strip()
            new_dict['rolename'] = request.vars.rolename.strip()
            doc_name = request.vars.name.strip()
            doc_id = request.vars.document.strip()
            new_dict['name'] = doc_name
            new_dict['document'] = doc_id

            condition = None
            #if request.vars.has_key('estado'):
            if 'estado' in request.vars:
                condition = request.vars.estado.strip()

            query = dsa_utils_temp.get_all_documents_from_period(symbol,year,doc_id,condition)
            #print(query)
            new_dict['list'] = db.executesql(query,as_dict=True)
    return dict(action=new_dict)

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def change_deliverable_status_linguistica():
    
    #if not request.vars.has_key('item'):
    if not 'item' in request.vars:
        return response.json({'ok': 0, 'message': 'No existe entregable'})
    
    #if not request.vars.has_key('action'):
    if 'action' not  in request.vars:
        return response.json({'ok': 0, 'message': 'No existe acción'})
    
    id_doc = request.vars.item.strip()
    comment = request.vars.comment
    action = request.vars.action.strip()
    comment = None if (comment == "" or len(comment) == 0) else comment
    
    # Obtener datos del documento
    query = dsa_utils_temp.get_document_delivered_to_sign(id_doc)
    document = db.executesql(query, as_dict=True)

    
    if action == '1':  # firmado
        stat = 'firmado'
        message = '<span class="badge badge-success">Firmado</span>'
        alert = 'Documento firmado'
        name = '<span class="fa fa-search"></span> Firmado'
        btn_class = 'btn-success'
    else:  # rechazado
        stat = 'rechazado'
        message = '<span class="badge badge-danger">Rechazado</span>'
        alert = 'Documento rechazado'
        name = '<span class="fa fa-search"></span> Entregado'
        btn_class = 'btn-secondary'

    if action == '1':
        # Obtener datos de firma
        query = dsa_utils_temp.get_document_delivered_sign_info(id_doc)
        signatures = db.executesql(query, as_dict=True)

        if len(signatures) < 1:
            return response.json({'ok': 0, 'message': 'Documento no tiene firmas asociadas'})
        
        document_base = dsa_utils_temp.encode_delivered_id(document[0]['id'])
        print(document_base)
        url = "%s://%s%s" % (request.env.wsgi_url_scheme, request.env.http_host,
                             URL('default', 'file_validation_ecys', args=['document', document_base]))
        result_sign, status_sign = dsa_utils_temp.sign_file(request.folder, document[0]['file_uploaded'], url, signatures,
                                                            auth.user.username, document[0]['signed_file'])
        print('Termina Firmado')
        print(result_sign)
        print(status_sign)

        if status_sign == 0:
            return response.json({'ok': 0, 'message': result_sign})

        doc_signed = result_sign
        values = {
            'comment': comment,
            'status': stat,
            'signed_file': result_sign,
            'signed_at': str(datetime.utcnow())
        }

        condition = {'id': int(id_doc)}
        try:
            update_query = ds_utils.create_script_string('dsa_document_delivered', 'U', values, condition)
            db.executesql(update_query)
        except Exception as e:
            print('********** admin - change deliverable status **********')
            print(str(e))
            return response.json({'ok': 0, 'message': str(e)})
        
        return response.json(
        {'ok': 1, 'message': message, 'uploaded': document[0]['file_uploaded'], 'signed': doc_signed, 'alert': alert, 'btn_class': btn_class, 'name': name})
    
    elif action == '2': #Rechazar
        values = {
            'comment': comment,
            'status': stat,
            'signed_file': None,
            'signed_at': None
        }
        condition = {'id': int(id_doc)}
        try:
            update_query = dsa_utils_temp.create_script_string('dsa_document_delivered', 'U', values, condition)
            db.executesql(update_query)
        except Exception as e:
            print('********** admin - change deliverable status **********')
            print(str(e))
            return response.json({'ok': 0, 'message': str(e)})
        
        return response.json(
            {'ok': 1, 'message': message, 'uploaded': document[0]['signed_file'], 'signed': document[0]['file_uploaded'], 'alert': alert, 'btn_class': btn_class, 'name': name})

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def update_all_deliverables_linguistica():

    #if not request.vars.has_key('period'):
    if 'period' not in request.vars:
        session.flash = 'No existe gestión de entregables'
        redirect(URL('admin', 'manage_deliverables_ecys'))
    #elif not request.vars.has_key('year'):
    elif 'year' not in request.vars:
        session.flash = 'No existe tipo de entregable'
        redirect(URL('admin', 'manage_deliverables_ecys'))
    #elif not request.vars.has_key('document'):
    elif 'document' not in request.vars:
        session.flash = 'No existe tipo de entregable'
        redirect(URL('admin', 'manage_deliverables_ecys'))
    #elif not request.vars.has_key('idrole') or not ('rolename'):
    elif 'idrole' not in request.vars or 'rolename' not in request.vars:
        session.flash = 'No existe rol'
        redirect(URL('admin', 'manage_deliverables_ecys'))
    
    period = request.vars.period.strip()
    year = request.vars.year.strip()
    idrole = request.vars.idrole.strip()
    rolename = request.vars.rolename.strip()
    id_type = request.vars.document.strip()
    status = 'entregado'

    if request.vars.period.strip() == 'Primer Semestre':
        symbol = '<='
    else:
        symbol = '>'

    query = dsa_utils_temp.get_all_document_delivered(id_type, symbol, year, status)
    documents = db.executesql(query, as_dict = True)

    for doc in documents:
        
        query_sig = dsa_utils_temp.get_document_delivered_sign_info(str(doc['id']))
        signatures = db.executesql(query_sig, as_dict=True)
        
        if len(signatures) < 1:
            session.flash = "Documento sin firmas asociadas"
            redirect((URL('admin', 'manage_deliverables_ecys', args=['deliverable_type'],
                        vars=dict(idrole=idrole, rolename=rolename, period = period, year = year))))
        
        document_base = dsa_utils_temp.encode_delivered_id(doc['id'])
        url = "%s://%s%s" % (request.env.wsgi_url_scheme, request.env.http_host,
                             URL('default', 'file_validation_ecys', args=['document', document_base]))
        
        result_sign, status_sign = dsa_utils_temp.sign_file(request.folder, doc['file_uploaded'], url,
                                                        signatures, auth.user.username, doc['signed_file'])

        if status_sign == 0:
            values = {
                'status': 'rechazado',
                'comment': 'El documento no se pudo firmar. Use una herramienta para desbloquear el documento y vuelva a subirlo.',
                'signed_file': None,
                'signed_at': None
            }
            condition = {'id': doc['id']}
            try:
                reject_query = dsa_utils_temp.create_script_string('dsa_document_delivered', 'U', values, condition)
                db.executesql(reject_query)
            except Exception as e:
                print('********** admin - update all deliverables ecys **********')
                print(str(e))
                session.flash = 'Error al firmar documentos'
                redirect(URL('admin', 'deliverable_type', args=['deliverable_type'],
                                    vars=dict(idrole=idrole, rolename=rolename, period=period, year=year)))
            continue

        values = {
            'status': 'firmado',
            'signed_file': result_sign,
            'signed_at': str(datetime.utcnow())
        }

        condition = {'id': doc['id']}

        try:
            update_query = dsa_utils_temp.create_script_string('dsa_document_delivered', 'U', values, condition)
            db.executesql(update_query)
        except Exception as e:
            print('********** admin - update all deliverables ecys **********')
            print(str(e))
            session.flash = 'Error al firmar documentos'
            redirect(URL('admin', 'deliverable_type', args=['deliverable_type'],
                                 vars=dict(idrole=idrole, rolename=rolename, period=period, year=year)))
    
    session.flash = 'Archivos firmados exitosamente'
    redirect(URL('admin', 'manage_deliverables_ecys', args=['deliverable_type'], vars=dict(idrole=idrole, rolename=rolename, period=period, year=year)))

@cache.action()
@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def download_deliverable_linguistica():
    args = request.args

    #if not request.vars.has_key('idrole') or not ('rolename'):
    if 'idrole' not in request.vars or 'rolename' not in request.vars:
            print('********** admin - download deliverable **********')
            print('No existe rol')
            raise HTTP(404)
    
    #if not request.vars.has_key('period'):
    if not 'period' in request.vars:
            print('********** admin - download deliverable **********')
            print('No se encontro parámetro period')
            raise HTTP(404)
    #if not request.vars.has_key('year'):
    if not 'year' in request.vars:
        print('********** admin - download deliverable **********')
        print('No se encontro parámetro year')
        raise HTTP(404)
    
    idrole = request.vars.idrole.strip()
    rolename = request.vars.rolename.strip()

    period = request.vars.period.strip()
    year = request.vars.year.strip()

    if len(args) == 0:
    
        #if not request.vars.has_key('delivered_type_id'):
        if not 'delivered_type_id' in request.vars:
            print('********** admin - download deliverable **********')
            print('No se encontro parámetro delivered_type_id')
            raise HTTP(404)
        #if not request.vars.has_key('delivered_status'):
        if not 'delivered_status' in request.vars:
            print('********** admin - download deliverable **********')
            print('No se encontro parámetro delivered_status')
            raise HTTP(404)

        delivered_type_id = request.vars.delivered_type_id.strip()
        delivered_status = 'True' if request.vars.delivered_status == '1' else 'False'
        
        if period == "Primer Semestre":
            symbol = "<="
        else:
            symbol = ">"

        #Obtener todos los documentos de un tipo
        query = dsa_utils_temp.get_all_document_delivered_filename(delivered_type_id, symbol, year, delivered_status, request.vars.delivered_status)
        print(query)
        list_files = db.executesql(query, as_dict=True)

        if len(list_files) == 1 and list_files[0]['filename'] == '' or len(list_files) == 0:
            session.flash = 'No hay documentos para descargar'
            redirect(URL('admin', 'manage_deliverables_ecys', args=['deliverable_type'],
                            vars=dict(idrole=idrole, rolename=rolename, period=period, year=year)))
        
        filename = dsa_utils_temp.retrieve_zip_file(request.folder, list_files, auth.user.username)
        if filename is None:
            session.flash = 'No se encontro el archivo'
            redirect(URL('admin', 'manage_deliverables_ecys', args=['deliverable_type'],
                    vars=dict(idrole=idrole, rolename=rolename, period=period, year=year)))

    elif len(args) == 1:
        if request.vars.delivered_status.strip() == "2":
            tipo = "complement_uploaded"
        elif request.vars.delivered_status.strip() == "1":
            tipo = "signed_file"
        else:
            tipo = "file_uploaded"
        query = dsa_utils_temp.get_document_download(tipo, request.vars.id.strip())
        filename = db.executesql(query, as_dict=True)[0]['filename']
    else:
        raise HTTP(404)

    try:
        file = dsa_utils_temp.retrieve_file(filename, request.folder)
    except Exception as e:
        print('********** admin - download deliverable **********')
        print(str(e))
        session.flash = 'No se econtro el archivo'
        redirect(URL('admin', 'manage_deliverables_ecys', args=['deliverable_type'],
                    vars=dict(idrole=idrole, rolename=rolename, period=period, year=year)))
        
    response.headers["Content-Type"] = c.contenttype(filename)
    response.headers["Content-Disposition"] = "attachment; filename=%s" % filename
    stream = response.stream(file, request=request)

    raise HTTP(200, stream, **response.headers)

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def retrieve_pdf_file():
    #if not request.vars.has_key('filename'):
    if not 'filename' in request.vars:
        return response.json({'ok': 0, 'message': 'No existe entregable'})

    filename = request.vars.filename.strip()
    print(filename)
    #filename = 'dsa_complemento-201700450.pdf'
    uploads_path = os.path.join(request.folder, 'uploads')
    file_path = os.path.join(uploads_path, filename)
    with open(file_path, 'rb') as pdf_file:
        encoded_string = base64.b64encode(pdf_file.read())
        return response.json({'ok': 1, 'encoded':encoded_string})

# **** Administrador

def signature_assignment_ecys():
    args = request.args
    new_dict = {}

    #if not request.vars.has_key('document'):
    if not 'document' in request.vars:
        session.flash = 'No existe documento'
        redirect(URL('default', 'home'))
    
    doc = request.vars.document.strip()

    # Info del tipo de documento
    query = dsa_utils_temp.get_document(doc)
    document = db.executesql(query, as_dict=True)

    if len(document) < 1:
        session.flash = 'No existe entregable'
        redirect(URL('default', 'home'))

    new_dict['document'] = document[0]['id']
    new_dict['doc_name'] = document[0]['name']

    if len(args) == 0:
        new_dict['type'] = 'list'
        query = dsa_utils_temp.get_document_signatures(doc)
        new_dict['list'] = db.executesql(query, as_dict=True)
    elif len(args) == 1:
        option = args[0]
        new_dict['type'] = option

        if option == 'new':
            if request.env.request_method == "POST":
                is_valid, resultado = dsa_utils_temp.validate_form_signature_assignment(request.vars)
                new_dict['item'] = resultado
                new_dict['select'] = get_all_signatures_available_form_select(resultado['inputSignature'])
            
                if not is_valid:
                    new_dict['message'] = resultado['message']
                    return dict(action=new_dict)
                
                signature = ds_utils.get_signature(resultado['inputSignature'], auth.user.username, True)
                item = db.executesql(signature, as_dict=True)

                if len(item) < 1:
                    session.flash = 'No existe firma'
                    redirect(URL('admin', 'signature_assignment_ecys', vars=dict(document=doc)))

                if item[0]['signature_type'] == 'Digital Signature':
                    if item[0]['image'] is None:
                        new_dict['message'] = 'Firma seleccionada no tiene imagen asociada'
                        return dict(action=new_dict)
                
                values = {
                    'signature': resultado['inputSignature'],
                    'position_x': resultado['inputPositionX'],
                    'position_y': resultado['inputPositionY'],
                    'height': resultado['inputHeight'],
                    'width': resultado['inputWidth'],
                    'page': resultado['inputPage'],
                    'document': doc
                }

                try:
                    insert_query = ds_utils.create_script_string('dsa_document_signature', 'I', values)
                    db.executesql(insert_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)

                session.flash = 'Registro creado exitosamente'
                redirect(URL('admin', 'signature_assignment_ecys', vars=dict(document=str(doc))))


            else:
                new_dict['select'] = get_all_signatures_available_form_select()

        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
    
    elif len(args) == 2:
        option = args[0]
        id = args[1]
        new_dict['type'] = option
        
        query = dsa_utils_temp.get_document_signature(id)
        item = db.executesql(query, as_dict = True)

        if len(item) < 1:
            session.flash = 'No existe el registro'
            redirect(URL('admin', 'signature_assignment_ecys', vars=dict(document=str(document[0]['id']))))
    
        if option == 'show' or option == 'delete':
            new_dict['item'] = item

            if option == 'delete' and request.env.request_method == 'POST':

                condition = {'id': int(id)}
                try:
                    delete_query = ds_utils.create_script_string('dsa_document_signature', 'D', condition, condition)
                    db.executesql(delete_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)
                
                session.flash = 'Registro eliminado exitosamente'
                redirect(URL('admin', 'signature_assignment_ecys', vars=dict(document=str(document[0]['id']))))
        
        elif option == 'edit':
            if request.env.request_method == "GET":
                result = {
                    'id': item[0]['id'],
                    'inputPositionX': item[0]['position_x'],
                    'inputPositionY': item[0]['position_y'],
                    'inputHeight': item[0]['height'],
                    'inputWidth': item[0]['width'],
                    'inputPage': item[0]['page']
                }

                new_dict['item'] = result
                new_dict['select'] = get_all_signatures_available_form_select(str(item[0]['id_signature']))

            else:
                is_valid, resultado = dsa_utils_temp.validate_form_signature_assignment(request.vars)
                resultado['id'] = id
                new_dict['item'] = resultado
                new_dict['select'] = get_signature_form_select(resultado['inputSignature'])

                if not is_valid:
                    new_dict['message'] = resultado['message']
                    return dict(action=new_dict)
                
                signature = ds_utils.get_signature(resultado['inputSignature'], auth.user.username, True)
                item = db.executesql(signature, as_dict=True)

                if len(item) < 1:
                    session.flash = 'No existe firma'
                    redirect(URL('admin', 'signature_assignment_ecys', vars=dict(document=document[0]['id'])))

                if item[0]['signature_type'] == 'Digital Signature':
                    if item[0]['image'] is None:
                        new_dict['message'] = 'Firma seleccionada no tiene imagen asociada'
                        return dict(action=new_dict)
                
                values = {
                    'signature': resultado['inputSignature'],
                    'position_x': resultado['inputPositionX'],
                    'position_y': resultado['inputPositionY'],
                    'height': resultado['inputHeight'],
                    'width': resultado['inputWidth'],
                    'page': resultado['inputPage'],
                    'document': doc
                }
                
                condition = {'id': int(id)}
                try:
                    update_query = ds_utils.create_script_string('dsa_document_signature', 'U', values, condition)
                    db.executesql(update_query)
                except Exception as e:
                    new_dict['message'] = str(e)
                    return dict(action=new_dict)
                
                
                session.flash = 'Registro actualizado exitosamente'
                redirect(URL('admin', 'signature_assignment_ecys', vars=dict(document=str(document[0]['id']))))

        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
    else:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    return dict(action=new_dict)

def upload_sample_signed_file():
    file_ = request.vars.file.strip()
    try:
        file = base64.b64decode(file_)
    except Exception as e:
        return response.json({'ok':0, 'message': str(e)})
    uploads_path = os.path.join(request.folder,'uploads')
    file_name = 'type_sample_sign.pdf'
    file_path = os.path.join(uploads_path, file_name)
    
    try:
        f = open(file_path,'wb')
        print(file_path)
        f.write(file)
        f.close()
        #shutil.copyfileobj(file, d_file)
    except Exception as e:
        print('Error al cargar archivo')
        print(e)
        return response.json({'ok':0, 'message': str(e)})
    return response.json({'ok':1, 'message': 'Archivo subido correctamente'})

def sign_sample_document():
    id_sign = request.vars.sign.strip()
    x = request.vars.x.strip()
    y = request.vars.y.strip()
    h = request.vars.h.strip()
    w = request.vars.w.strip()
    page = request.vars.page.strip()

    # Obtener datos de firma
    query = dsa_utils_temp.get_sign_info(id_sign)
    signature = db.executesql(query, as_dict=True)

    if len(signature) < 1:
        return response.json({'ok':0, 'message': 'No existe firma'})

    values = {
        'x': float(x),
        'y': float(y),
        'h': int(h),
        'w': int(w),
        'page': page
    }

    result_sign, status_sign = dsa_utils_temp.sign_sample(request.folder,signature[0],values)


    if status_sign == 0:
        return response.json({'ok':0, 'message': result_sign})
    return response.json({'ok':1, 'message': result_sign})

def get_all_signatures_available_form_select(sig=None):
    query = dsa_utils_temp.get_signatures_available()
    signatures = db.executesql(query, as_dict=True)

    signature_options = list()
    signature_options.append(OPTION("",_value=0))
    for signature in signatures:
        signature_options.append(OPTION(signature['name'], _value=signature['id'],_selected=(True if sig == str(signature['id']) else False)))
    return SELECT(signature_options, _name='inputSignature', _id='inputSignature', _class='form-control')

#*********** Fin - Practicas Finales - Juan Pablo Ardón ************

def get_periods_on_change():
    period_type = request.vars['period_type']
    period_id = request.vars['period_id'] or 0
    period_id = int(period_id)

    query = db(db.period_year)
    if period_type != '1':
        query = db(db.period_year.period == db.period_detail.period)
        
    periods_array = query.select(
                        db.period_year.id,
                        db.period_year.yearp,
                        db.period_year.period,
                        orderby=~db.period_year.id
                    )

    options = []
    for period in periods_array:
        selected_var = False
        if period_id == period.id:
            selected_var = True
            
        options.append(OPTION(f"{T(period.period.name)} - {period.yearp}", _value=period.id, _selected=selected_var))

    return response.json(options)