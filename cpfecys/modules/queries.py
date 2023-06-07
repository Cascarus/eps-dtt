# ********************************************* REPORTE ANOMALIES_LIST
def q_anomalies_list():
	return ("select py.id id, py.yearp yearp, p.name name, count(le.id) total"
	" from period p" 
	" inner join period_year py ON p.id = py.period "
	" left join ("
	" select id, period "
	" from log_entry "
	" where log_entry.log_type = '2' "
	" ) le ON py.id = le.period"
	" group by py.id, p.id"
	" order by py.id desc;")

def q_anomalies_list_view():     
	return ("select MONTH(le.entry_date), pr.name, pr.id, count(le.id) from log_entry le"
	" inner join log_type lt on le.log_type = lt.id"
	" inner join report r on le.report = r.id"
	" inner join user_project up on r.assignation = up.id"
	" inner join project pr on up.project = pr.id"
	" where lt.name = 'Anomaly' and le.period = {0}"
	" group by MONTH(le.entry_date), pr.name"
	" order by MONTH(le.entry_date) desc;")

def q_anomalies_list_show():
	return ("select le.entry_date, p.name, le.description, au.first_name, au.last_name from log_entry le"
	" inner join log_type lt on le.log_type = lt.id"
	" inner join report r on le.report = r.id"
	" inner join user_project up on r.assignation = up.id"
	" inner join auth_user au on up.assigned_user = au.id"
	" inner join project p on up.project = p.id"
	" where lt.name = 'Anomaly' and le.period = {0}"
	" and p.id = {1} and month(le.entry_date)= {2}"
	" order by le.entry_date desc;")

#*********************************************** REPORTE GENERAL_REPORT
def q_general_report():
	return ("select p.id, p.name, au.first_name, au.last_name "
	" from project p"
	" inner join area_level al on p.area_level = al.id"
	" inner join user_project up on up.project = p.id"
	" inner join auth_user au on up.assigned_user = au.id"
	" inner join auth_membership am on au.id = am.user_id"
	" inner join auth_group ag on am.group_id = ag.id"
	" where role = 'Teacher'"
	" and up.period= {0}"
	" and al.id = {1}"
	" order by p.name;")

#*********************************************** REPORTE REPORTE_POR_ESTADOS
def q_report_list():
	return (		
		"select r1.*, case when r2.conteo is null then 0 else r2.conteo end pendientes"
		" from "
		" ("
		" select py.id, py.yearp anio, py.period periodo, pe.name,"
		" count(r.id) total, "
		" sum(case r.status when 1 then 1 else 0 end) 'Borrador',"
		" sum(case r.status when 2 then 1 else 0 end) 'Calificar',"
		" sum(case r.status when 3 then 1 else 0 end) 'Re-hacer',"
		" sum(case r.status when 5 then 1 else 0 end) 'Recalificar maestro',"
		" sum(case r.status when 4 then 1 else 0 end) 'Calificado',"
		" sum(case when !isnull(r.min_score) and !isnull(r.score) and r.status = 4 and r.score >= r.min_score then 1 else 0 end) aprobado,"
		" sum(case when !isnull(r.min_score)  and r.status = 4 and r.score < r.min_score then 1 when (isnull(r.score) or isnull(r.min_score)) and r.status = 4 then 1 else 0 end) reprobado,"
		" sum(case when !isnull(r.dtt_approval) then 1 else 0 end) condtt,"
		" sum(case when isnull(r.dtt_approval) and !isnull(r.id) and !isnull(r.min_score) and !isnull(r.score) and r.status = 4 and r.score >= r.min_score then 1 else 0 end) sindtt,"
		" sum(case when r.never_delivered = 'F' then 1 when isnull(r.never_delivered) and !isnull(r.id) then 1 else 0 end) entregado,"
		" sum(case when r.never_delivered = 'T' then 1 else 0 end) noentregado"
		" from ("
		" select Right(rr.name,4) anio, Month(r.created) mes,"
		" case"
		" when rr.name like('%Enero%') then 1 "
		" when rr.name like('%Febrero%') then 1 "
		" when rr.name like('%Marzo%') then 1 "
		" when rr.name like('%Abril%') then 1 "
		" when rr.name like('%Mayo%') then 1 "
		" when rr.name like('%Primer%') then 1 "
		" when rr.name like('%Junio%') then 2 "
		" when rr.name like('%Julio%') then 2 "
		" when rr.name like('%Agosto%') then 2 "
		" when rr.name like('%Septiembre%') then 2 "
		" when rr.name like('%Octubre%') then 2 "
		" when rr.name like('%Noviembre%') then 2 "
		" when rr.name like('%Diciembre%') then 2 "
		" when rr.name like('%Segundo%') then 2 "
		" end periodo,"
        " rr.name restriction,"
        " r.*, py.id identificador"
		" from report r"
		" inner join user_project up on r.assignation = up.id"
		" inner join period_year py on up.period = py.id"
		" inner join project p on up.project = p.id"
		" inner join auth_user au on up.assigned_user = au.id"
		" inner join report_status rs on r.status = rs.id"
		" inner join auth_membership am on am.user_id = au.id"
		" inner join auth_group ag on ag.id = am.group_id"
		" inner join report_restriction rr on r.report_restriction = rr.id"
		" where ag.role = 'Student'"
		" ) r "
		" right join period_year py on py.yearp = r.anio and py.period = r.periodo"
		" inner join period pe on pe.id = py.period"
		" where py.period <= 2"
		" group by r.anio, r.periodo"
		" ) r1 "
		" left join "
		" ("
		" select re.anio, re.periodo, count(*) conteo"
		" from"
		" (select "
		" case"
		" when rr.name like('%Enero%') then 1 "
		" when rr.name like('%Febrero%') then 1 "
		" when rr.name like('%Marzo%') then 1 "
		" when rr.name like('%Abril%') then 1 "
		" when rr.name like('%Mayo%') then 1 "
		" when rr.name like('%Primer%') then 1 "
		" when rr.name like('%Junio%') then 2 "
		" when rr.name like('%Julio%') then 2 "
		" when rr.name like('%Agosto%') then 2 "
		" when rr.name like('%Septiembre%') then 2 "
		" when rr.name like('%Octubre%') then 2 "
		" when rr.name like('%Noviembre%') then 2 "
		" when rr.name like('%Diciembre%') then 2 "
		" when rr.name like('%Segundo%') then 2 "
		" end periodo,"
		" Right(rr.name,4) anio,"
		" rr.id rr_id, rr.name rr_name, rr.start_date, "
		" rr.end_date , up.id up_id, up.period up_period, up.periods, au.username"
		" from report_restriction rr, user_project up"
		" inner join auth_user au on up.assigned_user = au.id"
		" inner join auth_membership am on am.user_id = au.id"
		" inner join auth_group ag on ag.id = am.group_id"
		" where ag.role = 'Student'"
		" ) re"
		" left join report r on re.rr_id = r.report_restriction and re.up_id = r.assignation"
		" left join period_year py on re.up_period = py.id"
		" where "
		" case py.period"
		" when 1 then Year(re.start_date)>= py.yearp  "
		" when 2 then re.start_date >= concat(py.yearp,'-06-01')"
		" end"
		" and case re.periods"
		" when 1 then"
		" case py.period"
		" when 1 then Year(re.end_date) <= py.yearp and Month(re.end_date) <= 6"
		" when 2 then Year(re.end_date) <= py.yearp and Month(re.end_date) <= 12"
		" end"
		" when 2 then"
		" case py.period"
		" when 1 then Year(re.end_date) <= py.yearp and Month(re.end_date) <= 12"
		" when 2 then  "
		" (Year(re.end_date) <= py.yearp and Month(re.end_date) <= 12)"
		" or (Year(re.end_date) <= (py.yearp + 1) and Month(re.end_date) <= 6) "
		" end"
		" end"
		" and r.id is null"
		" and py.id is not null"
		" group by re.anio, re.periodo"
		" ) r2 on r1.anio = r2.anio and r1.periodo = r2.periodo"
		" order by r1.anio desc, r1.periodo desc;"
		)

def q_report_filter(filtro):
	retorno = (
		" select"
		" r.*"
		" from "
		" ( "

		" select Right(rr.name,4) anio, Month(r.created) mes,"
		" p.name project_name,r.created, au.username, au.email, au.first_name, au.last_name, rr.name restriction_name, rr.start_date, rr.end_date, r.score, rs.name status_name,"
		" r.id, r.dtt_approval,"
		" r.hours, (up.hours - r.hours) hours_left,"
		" r.never_delivered, r.min_score,"
		" case"
		" when rr.name like('%Enero%') then 1 "
		" when rr.name like('%Febrero%') then 1 "
		" when rr.name like('%Marzo%') then 1 "
		" when rr.name like('%Abril%') then 1 "
		" when rr.name like('%Mayo%') then 1 "
		" when rr.name like('%Primer%') then 1 "
		" when rr.name like('%Junio%') then 2 "
		" when rr.name like('%Julio%') then 2 "
		" when rr.name like('%Agosto%') then 2 "
		" when rr.name like('%Septiembre%') then 2 "
		" when rr.name like('%Octubre%') then 2 "
		" when rr.name like('%Noviembre%') then 2 "
		" when rr.name like('%Diciembre%') then 2 "
		" when rr.name like('%Segundo%') then 2 "
		" end periodo"
		" from report r"
		" inner join user_project up on r.assignation = up.id"
		" inner join period_year py on up.period = py.id"
		" inner join project p on up.project = p.id"
		" inner join auth_user au on up.assigned_user = au.id"
		" inner join report_status rs on r.status = rs.id"
		" inner join auth_membership am on am.user_id = au.id"
		" inner join auth_group ag on ag.id = am.group_id"
		" inner join report_restriction rr on r.report_restriction = rr.id"
		" where ag.role = 'Student'"
		)

	if(filtro==1):   #	ESTADOS
		retorno += " and r.status = {1}"
	elif (filtro==2):#  APROBADOS
		retorno += " and !isnull(r.min_score) and !isnull(r.score) and r.status = 4 and r.score >= r.min_score"
	elif (filtro==3):#  REPROBADOS
		retorno += " and((!isnull(r.min_score) and r.status = 4 and r.score < r.min_score)or((isnull(r.score) or isnull(r.min_score)) and r.status = 4))"
	elif (filtro==4):#  DTT APROBADOS
		retorno += " and !isnull(r.dtt_approval)"
	elif (filtro==5):#  DTT PENDIENTES CON APROBACION CATEDRATICO
		retorno += " and isnull(r.dtt_approval) and !isnull(r.id) and !isnull(r.min_score) and !isnull(r.score) and r.status = 4 and r.score >= r.min_score"
	elif (filtro==6):#  ENTREGADOS
		retorno += " and((r.never_delivered = 'F') or (isnull(r.never_delivered) and !isnull(r.id)))"
	elif (filtro==7):#  NO ENTREGADOS
		retorno += " and r.never_delivered = 'T'"
	elif (filtro==8):#  PENDIENTES
		retorno = (
			" select r.*"
			" from"
			" ("
			" select re.*"
			" from"
			" (select "
			" case"
			" when rr.name like('%Enero%') then 1 "
			" when rr.name like('%Febrero%') then 1 "
			" when rr.name like('%Marzo%') then 1 "
			" when rr.name like('%Abril%') then 1 "
			" when rr.name like('%Mayo%') then 1 "
			" when rr.name like('%Primer%') then 1 "
			" when rr.name like('%Junio%') then 2 "
			" when rr.name like('%Julio%') then 2 "
			" when rr.name like('%Agosto%') then 2 "
			" when rr.name like('%Septiembre%') then 2 "
			" when rr.name like('%Octubre%') then 2 "
			" when rr.name like('%Noviembre%') then 2 "
			" when rr.name like('%Diciembre%') then 2 "
			" when rr.name like('%Segundo%') then 2 "
			" end periodo,"
			" Right(rr.name,4) anio,"
			" rr.id rr_id, rr.name restriction_name, rr.start_date, "
			" rr.end_date , up.id up_id, up.period up_period, up.periods, au.username,"
			" 'Pendiente' status_name, 'Pendiente' score,"
			" au.last_name, au.first_name, au.email, 'Pendiente' created, p.name project_name"
			" from report_restriction rr, user_project up"
			" inner join auth_user au on up.assigned_user = au.id"
			" inner join auth_membership am on am.user_id = au.id"
			" inner join auth_group ag on ag.id = am.group_id"
			" inner join project p on up.project = p.id"
			" where ag.role = 'Student'"
			" ) re"
			" left join report r on re.rr_id = r.report_restriction and re.up_id = r.assignation"
			" left join period_year py on re.up_period = py.id"
			" where "
			" case py.period"
			" when 1 then Year(re.start_date)>= py.yearp  "
			" when 2 then re.start_date >= concat(py.yearp,'-06-01')"
			" end"
			" and case re.periods"
			" when 1 then"
			" case py.period"
			" when 1 then Year(re.end_date) <= py.yearp and Month(re.end_date) <= 6"
			" when 2 then Year(re.end_date) <= py.yearp and Month(re.end_date) <= 12"
			" end"
			" when 2 then"
			" case py.period"
			" when 1 then Year(re.end_date) <= py.yearp and Month(re.end_date) <= 12"
			" when 2 then  "
			" (Year(re.end_date) <= py.yearp and Month(re.end_date) <= 12)"
			" or (Year(re.end_date) <= (py.yearp + 1) and Month(re.end_date) <= 6)"
			" end"
			" end"
			" and r.id is null"
			" and py.id is not null"
			)

	retorno += (" ) r"
		" inner join period_year py on py.yearp = r.anio and py.period = r.periodo"
		" inner join period pe on pe.id = py.period"
		" where py.period <= 2"
		" and py.id = {0}")

	return retorno +" ;";

#*********************************************** REPORTE GESTION DE ESTUDIANTES
def q_student_management(filtro):	
	if(filtro == 1):
		return 'academic_log.id_period = "{0}" and academic_log.operation_log = "{1}"'
	elif(filtro == 2):
		return 'academic_log.id_period = "{0}" and academic_log.operation_log = "{1}" and {2}'
	elif(filtro == 3):
		return 'academic_log.id_period = "{0}" and academic_log.operation_log = "{1}" and academic_log.date_log >="{2}" and academic_log.date_log<"{3}"'
	elif(filtro == 4):
		return 'academic_log.id_period = "{0}" and academic_log.operation_log = "{1}" and academic_log.date_log >="{2}" and academic_log.date_log<"{3}" and {4}'
	elif(filtro == 5):
		return 'academic_log.id_period = "{0}" and academic_log.operation_log = "{1}" and academic_log.date_log >="{2}" and academic_log.date_log<"{3}" and academic_log.roll contains "{4}"'
	elif(filtro == 6):
		return 'academic_log.id_period = "{0}" and academic_log.operation_log = "{1}" and academic_log.date_log >="{2}" and academic_log.date_log<"{3}" and academic_log.roll contains "{4}" and {5}'
	elif(filtro == 7):
		return 'academic_log.id_period = "{0}" and academic_log.operation_log = "{1}" and academic_log.date_log >="{2}" and academic_log.date_log<"{3}" and academic_log.roll contains "{4}" and academic_log.user_name ="{5}"'
	elif(filtro == 8):
		return 'academic_log.id_period = "{0}" and academic_log.operation_log = "{1}" and academic_log.date_log >="{2}" and academic_log.date_log<"{3}" and academic_log.roll contains "{4}" and academic_log.user_name ="{5}" and {6}'
	elif(filtro == 9):
		return 'academic_log.id_period = "{0}" and academic_log.date_log >="{1}" and academic_log.date_log<"{2}" and academic_log.roll contains "{3}"'
	elif(filtro == 10):
		return 'academic_log.id_period = "{0}" and academic_log.date_log >="{1}" and academic_log.date_log<"{2}" and academic_log.roll contains "{3}" and {4}'
	elif(filtro == 11):
		return 'academic_log.id_period = "{0}" and academic_log.date_log >="{1}" and academic_log.date_log<"{2}" and academic_log.roll LIKE "%{3}%" and academic_log.user_name ="{4}"'
	elif(filtro == 12):
		return 'academic_log.id_period = "{0}" and academic_log.date_log >="{1}" and academic_log.date_log<"{2}" and academic_log.roll LIKE "%{3}%" and academic_log.user_name ="{4}" and {5}'
	elif(filtro == 13):
		return 'academic_log.id_period = "{0}" and academic_log.operation_log = "{1}" and academic_log.date_log >="{2}" and academic_log.date_log<"{3}" and academic_log.roll LIKE "%{4}%" and academic_log.user_name ="{5}"'
	elif(filtro == 14):
		return 'academic_log.id_period = "{0}" and academic_log.operation_log = "{1}" and academic_log.date_log >="{2}" and academic_log.date_log<"{3}" and academic_log.roll LIKE "%{4}%" and academic_log.user_name ="{5}" and {6}'

#*********************************************** REPORTE GESTION DE ASIGNACIONES DE ESTUDIANTES
def q_student_assignment_management(filtro):
	if(filtro==1):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}"'
	if(filtro==2):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}}" and {2}'
	if(filtro==3):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}"'
	if(filtro==4):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and {4}'
	if(filtro==5):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and academic_course_assignation_log.after_course = "{4}"'
	if(filtro==6):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and academic_course_assignation_log.after_course = "{4}" and {5}'
	if(filtro==7):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and academic_course_assignation_log.after_course = "{4}" and academic_course_assignation_log.before_course = "{4}"'
	if(filtro==8):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and academic_course_assignation_log.after_course = "{4}" and academic_course_assignation_log.before_course = "{4}" and {5}'
	if(filtro==9):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and academic_course_assignation_log.before_course = "{4}"'
	if(filtro==10):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and academic_course_assignation_log.before_course = "{4}" and {5}'
	if(filtro==11):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and academic_course_assignation_log.after_course = "{4}" and academic_course_assignation_log.roll contains "{5}"'
	if(filtro==12):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and academic_course_assignation_log.after_course = "{4}" and academic_course_assignation_log.roll contains "{5}" and {6}'
	if(filtro==13):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and academic_course_assignation_log.before_course = "{4}" and academic_course_assignation_log.after_course = "{4}" and academic_course_assignation_log.roll contains "{5}"'
	if(filtro==14):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and academic_course_assignation_log.before_course = "{4}" and academic_course_assignation_log.after_course = "{4}" and academic_course_assignation_log.roll contains "{5}" and {6}'
	if(filtro==15):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and academic_course_assignation_log.before_course = "{4}" and academic_course_assignation_log.roll contains "{5}"'
	if(filtro==16):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and academic_course_assignation_log.before_course = "{4}" and academic_course_assignation_log.roll contains "{5}" and {6}'
	if(filtro==17):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and academic_course_assignation_log.after_course = "{4}" and academic_course_assignation_log.roll contains "{5}" and academic_course_assignation_log.user_name ="{6}"'
	if(filtro==18):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and academic_course_assignation_log.after_course = "{4}" and academic_course_assignation_log.roll contains "{5}" and academic_course_assignation_log.user_name ="{6}" and {7}'
	if(filtro==19):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and academic_course_assignation_log.before_course = "{4}" and academic_course_assignation_log.after_course = "{4}" and academic_course_assignation_log.roll contains "{5}" and academic_course_assignation_log.user_name ="{6}"'
	if(filtro==20):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and academic_course_assignation_log.before_course = "{4}" and academic_course_assignation_log.after_course = "{4}" and academic_course_assignation_log.roll contains "{5}" and academic_course_assignation_log.user_name ="{6}" and {7}'
	if(filtro==21):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and academic_course_assignation_log.before_course = "{4}" and academic_course_assignation_log.roll contains "{5}" and academic_course_assignation_log.user_name ="{6}"'
	if(filtro==22):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and academic_course_assignation_log.before_course = "{4}" and academic_course_assignation_log.roll contains "{5}" and academic_course_assignation_log.user_name ="{6}" and {7}'
	if(filtro==23):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and academic_course_assignation_log.after_course = "{4}" and academic_course_assignation_log.roll LIKE "%{5}%" and academic_course_assignation_log.user_name ="{6}"'
	if(filtro==24):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and academic_course_assignation_log.after_course = "{4}" and academic_course_assignation_log.roll LIKE "%{5}%" and academic_course_assignation_log.user_name ="{6}" and {7}'
	if(filtro==25):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and academic_course_assignation_log.before_course = "{4}" and academic_course_assignation_log.after_course = "{4}" and academic_course_assignation_log.roll LIKE "%{5}%" and academic_course_assignation_log.user_name ="{6}"'
	if(filtro==26):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and academic_course_assignation_log.before_course = "{4}" and academic_course_assignation_log.after_course = "{4}" and academic_course_assignation_log.roll LIKE "%{5}%" and academic_course_assignation_log.user_name ="{6}" and {7}'
	if(filtro==27):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and academic_course_assignation_log.before_course = "{4}" and academic_course_assignation_log.roll LIKE "%{5}%" and academic_course_assignation_log.user_name ="{6}"'
	if(filtro==28):
		return 'academic_course_assignation_log.id_period = "{0}" and academic_course_assignation_log.operation_log = "{1}" and academic_course_assignation_log.date_log >="{2}" and academic_course_assignation_log.date_log<"{3}" and academic_course_assignation_log.before_course = "{4}" and academic_course_assignation_log.roll LIKE "%{5}%" and academic_course_assignation_log.user_name ="{6}" and{7}'

#*********************************************** REPORTE GESTION DE NOTAS
def q_grades_management(filtro):
	if(filtro==1):
		return 'grades_log.period = "{0}" and grades_log.yearp = "{1}" and grades_log.operation_log = "{2}"'
	if(filtro==2):
		return 'grades_log.period = "{0}" and grades_log.yearp = "{1}" and grades_log.operation_log = "{2}" and {3}'
	if(filtro==3):
		return 'grades_log.period = "{0}" and grades_log.yearp = "{1}" and grades_log.operation_log = "{2}" and grades_log.date_log >="{3}" and grades_log.date_log<"{4}"'
	if(filtro==4):
		return 'grades_log.period = "{0}" and grades_log.yearp = "{1}" and grades_log.operation_log = "{2}" and grades_log.date_log >="{3}" and grades_log.date_log<"{4}" and {5}'
	if(filtro==5):
		return 'grades_log.period = "{0}" and grades_log.yearp = "{1}" and grades_log.operation_log = "{2}" and grades_log.date_log >="{3}" and grades_log.date_log<"{4}" and grades_log.project ="{5}"'
	if(filtro==6):
		return 'grades_log.period = "{0}" and grades_log.yearp = "{1}" and grades_log.operation_log = "{2}" and grades_log.date_log >="{3}" and grades_log.date_log<"{4}" and grades_log.project ="{5}" and {6}'
	if(filtro==7):
		return 'grades_log.period = "{0}" and grades_log.yearp = "{1}" and grades_log.date_log >="{2}" and grades_log.date_log<"{3}"'
	if(filtro==8):
		return 'grades_log.period = "{0}" and grades_log.yearp = "{1}" and grades_log.date_log >="{2}" and grades_log.date_log<"{3}" and {4}'
	if(filtro==9):
		return 'grades_log.period = "{0}" and grades_log.yearp = "{1}" and grades_log.operation_log = "{2}" and grades_log.date_log >="{3}" and grades_log.date_log<"{4}" and grades_log.project ="{5}" and grades_log.roll ="{6}"'
	if(filtro==10):
		return 'grades_log.period = "{0}" and grades_log.yearp = "{1}" and grades_log.operation_log = "{2}" and grades_log.date_log >="{3}" and grades_log.date_log<"{4}" and grades_log.project ="{5}" and grades_log.roll ="{6}" and {7}'
	if(filtro==11):
		return 'grades_log.period = "{0}" and grades_log.yearp = "{1}" and grades_log.operation_log = "{2}" and grades_log.date_log >="{3}" and grades_log.date_log<"{4}" and grades_log.project ="{5}" and grades_log.roll ="{6}" and grades_log.user_name ="{7}"'
	if(filtro==12):
		return 'grades_log.period = "{0}" and grades_log.yearp = "{1}" and grades_log.operation_log = "{2}" and grades_log.date_log >="{3}" and grades_log.date_log<"{4}" and grades_log.project ="{5}" and grades_log.roll ="{6}" and grades_log.user_name ="{7}" and {8}'
	if(filtro==13):
		return 'grades_log.period = "{0}" and grades_log.yearp = "{1}" and grades_log.date_log >="{2}" and grades_log.date_log<"{3}" and grades_log.project ="{4}" and grades_log.roll ="{5}" and grades_log.user_name ="{6}"'
	if(filtro==14):
		return 'grades_log.period = "{0}" and grades_log.yearp = "{1}" and grades_log.date_log >="{2}" and grades_log.date_log<"{3}" and grades_log.project ="{4}" and grades_log.roll ="{5}" and grades_log.user_name ="{6}" and {7}'

#*********************************************** REPORTE GESTION DE ACTIVIDADES CON METRICAS
def q_activities_withmetric_management(filtro):
	if(filtro==1):
		return 'course_activity_log.period = "{0}" and course_activity_log.yearp = "{1}" and course_activity_log.operation_log = "{2}"'
	if(filtro==2):
		return 'course_activity_log.period = "{0}" and course_activity_log.yearp = "{1}" and course_activity_log.operation_log = "{2}" and {3}'
	if(filtro==3):
		return 'course_activity_log.period = "{0}" and course_activity_log.yearp = "{1}" and course_activity_log.operation_log = "{2}" and course_activity_log.date_log >="{3}" and course_activity_log.date_log<"{4}"'
	if(filtro==4):
		return 'course_activity_log.period = "{0}" and course_activity_log.yearp = "{1}" and course_activity_log.operation_log = "{2}" and course_activity_log.date_log >="{3}" and course_activity_log.date_log<"{4}" and {5}'
	if(filtro==5):
		return 'course_activity_log.period = "{0}" and course_activity_log.yearp = "{1}" and course_activity_log.operation_log = "{2}" and course_activity_log.date_log >="{3}" and course_activity_log.date_log<"{4}" and course_activity_log.course ="{5}"'
	if(filtro==6):
		return 'course_activity_log.period = "{0}" and course_activity_log.yearp = "{1}" and course_activity_log.operation_log = "{2}" and course_activity_log.date_log >="{3}" and course_activity_log.date_log<"{4}" and course_activity_log.course ="{5}" and {6}'
	if(filtro==7):
		return 'course_activity_log.period = "{0}" and course_activity_log.yearp = "{1}" and course_activity_log.date_log >="{2}" and course_activity_log.date_log<"{3}"'
	if(filtro==8):
		return 'course_activity_log.period = "{0}" and course_activity_log.yearp = "{1}" and course_activity_log.date_log >="{2}" and course_activity_log.date_log<"{3}" and {4}'
	if(filtro==9):
		return 'course_activity_log.period = "{0}" and course_activity_log.yearp = "{1}" and course_activity_log.operation_log = "{2}" and course_activity_log.date_log >="{3}" and course_activity_log.date_log<"{4}" and course_activity_log.course ="{5}" and course_activity_log.roll ="{6}"'
	if(filtro==10):
		return 'course_activity_log.period = "{0}" and course_activity_log.yearp = "{1}" and course_activity_log.operation_log = "{2}" and course_activity_log.date_log >="{3}" and course_activity_log.date_log<"{4}" and course_activity_log.course ="{5}" and course_activity_log.roll ="{6}" and {7}'
	if(filtro==11):
		return 'course_activity_log.period = "{0}" and course_activity_log.yearp = "{1}" and course_activity_log.operation_log = "{2}" and course_activity_log.date_log >="{3}" and course_activity_log.date_log<"{4}" and course_activity_log.course ="{5}" and course_activity_log.roll ="{6}" and course_activity_log.user_name ="{7}"'
	if(filtro==12):
		return 'course_activity_log.period = "{0}" and course_activity_log.yearp = "{1}" and course_activity_log.operation_log = "{2}" and course_activity_log.date_log >="{3}" and course_activity_log.date_log<"{4}" and course_activity_log.course ="{5}" and course_activity_log.roll ="{6}" and course_activity_log.user_name ="{7}" and {8}'
	if(filtro==13):
		return 'course_activity_log.period = "{0}" and course_activity_log.yearp = "{1}" and course_activity_log.date_log >="{2}" and course_activity_log.date_log<"{3}" and course_activity_log.course ="{4}" and course_activity_log.roll ="{5}" and course_activity_log.user_name ="{6}"'
	if(filtro==14):
		return 'course_activity_log.period = "{0}" and course_activity_log.yearp = "{1}" and course_activity_log.date_log >="{2}" and course_activity_log.date_log<"{3}" and course_activity_log.course ="{4}" and course_activity_log.roll ="{5}" and course_activity_log.user_name ="{6}" and {7}'

#*********************************************** REPORTE GESTION DE PETICIONES DE CAMBIO DE ACTIVIDADES CON METRICA
def q_change_request_activities_with_metric_management(filtro):
	if(filtro==1):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.status = "{2}"'
	if(filtro==2):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.status = "{2}" and {3}'
	if(filtro==3):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request >="{2}" and requestchange_activity_log.date_request<"{3}" and requestchange_activity_log.status = "{4}"'
	if(filtro==4):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request >="{2}" and requestchange_activity_log.date_request<"{3}" and requestchange_activity_log.status = "{4}" and {5}'
	if(filtro==5):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request_resolve >="{2}" and requestchange_activity_log.date_request_resolve<"{3}" and requestchange_activity_log.status = "{4}"'
	if(filtro==6):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request_resolve >="{2}" and requestchange_activity_log.date_request_resolve<"{3}" and requestchange_activity_log.status = "{4}" and {5}'
	if(filtro==7):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request >="{1}-01-01" and requestchange_activity_log.date_request<"{2}" and requestchange_activity_log.status = "{3}"'
	if(filtro==8):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request >="{1}-01-01" and requestchange_activity_log.date_request<"{2}" and requestchange_activity_log.status = "{3}" and {4}'
	if(filtro==9):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request_resolve >="{1}-01-01" and requestchange_activity_log.date_request_resolve<"{2}" and requestchange_activity_log.status != "{3}"'
	if(filtro==10):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request_resolve >="{1}-01-01" and requestchange_activity_log.date_request_resolve<"{2}" and requestchange_activity_log.status != "{3}" and {4}'
	if(filtro==11):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request >="{1}-06-01" and requestchange_activity_log.date_request<"{2}" and requestchange_activity_log.status = "{3}"'
	if(filtro==12):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request >="{1}-06-01" and requestchange_activity_log.date_request<"{2}" and requestchange_activity_log.status = "{3}" and {4}'
	if(filtro==13):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request_resolve >="{1}-06-01" and requestchange_activity_log.date_request_resolve<"{2}" and requestchange_activity_log.status != "{3}"'
	if(filtro==14):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request_resolve >="{1}-06-01" and requestchange_activity_log.date_request_resolve<"{2}" and requestchange_activity_log.status != "{3}" and {4}'
	if(filtro==15):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request >="{2}" and requestchange_activity_log.date_request<"{3}" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "{4}"'
	if(filtro==16):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request >="{2}" and requestchange_activity_log.date_request<"{3}" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "{4}" and {5}'
	if(filtro==17):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request_resolve >="{2}" and requestchange_activity_log.date_request_resolve <"{3}" and requestchange_activity_log.status = "{4}" and requestchange_activity_log.course = "{5}"'
	if(filtro==18):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request_resolve >="{2}" and requestchange_activity_log.date_request_resolve <"{3}" and requestchange_activity_log.status = "{4}" and requestchange_activity_log.course = "{5}" and {6}'
	if(filtro==19):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request >="{1}-01-01" and requestchange_activity_log.date_request<"{2}" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "{3}"'
	if(filtro==20):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request >="{1}-01-01" and requestchange_activity_log.date_request<"{2}" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "{3}" and {4}'
	if(filtro==21):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request_resolve >="{1}-01-01" and requestchange_activity_log.date_request_resolve<"{2}" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "{3}"'
	if(filtro==22):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request_resolve >="{1}-01-01" and requestchange_activity_log.date_request_resolve<"{2}" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "{3}" and {4}'
	if(filtro==23):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request >="{1}-06-01" and requestchange_activity_log.date_request<"{2}" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "{3}"'
	if(filtro==24):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request >="{1}-06-01" and requestchange_activity_log.date_request<"{2}" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "{3}" and {4}'
	if(filtro==25):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request_resolve >="{1}-06-01" and requestchange_activity_log.date_request_resolve<"{2}" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "{3}"'
	if(filtro==26):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request_resolve >="{1}-06-01" and requestchange_activity_log.date_request_resolve<"{2}" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "{3}" and {4}'
	if(filtro==27):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request >="{2}" and requestchange_activity_log.date_request<"{3}" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "{4}" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "{5}"'
	if(filtro==28):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request >="{2}" and requestchange_activity_log.date_request<"{3}" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "{4}" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "{5}" and {6}'
	if(filtro==29):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request_resolve >="{2}" and requestchange_activity_log.date_request_resolve<"{3}" and requestchange_activity_log.status = "{4}" and requestchange_activity_log.course = "{5}" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "{6}"'
	if(filtro==30):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.date_request_resolve >="{2}" and requestchange_activity_log.date_request_resolve<"{3}" and requestchange_activity_log.status = "{4}" and requestchange_activity_log.course = "{5}" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "{6}" and {7}'
	if(filtro==31):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.{2} >="{3}" and requestchange_activity_log.{2}<"{4}" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "{5}" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "{6}"'
	if(filtro==32):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.{2} >="{3}" and requestchange_activity_log.{2}<"{4}" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "{5}" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "{6}" and {7}'
	if(filtro==33):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.{2} >="{3}" and requestchange_activity_log.{2}<"{4}" and requestchange_activity_log.status = "{5}" and requestchange_activity_log.course = "{6}" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "{7}" {8}'
	if(filtro==34):
		return 'requestchange_activity_log.semester = "{0}" and requestchange_activity_log.yearp = "{1}" and requestchange_activity_log.{2} >="{3}" and requestchange_activity_log.{2}<"{4}" and requestchange_activity_log.status != "{5}" and requestchange_activity_log.course = "{6}" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "{7}" and requestchange_activity_log.description = "{8}" and requestchange_activity_log.date_request = "{9}" and requestchange_activity_log.category_request = "{10}" {11}'

def q_notification_calculation(filtro):
	if(filtro == 1):
		return """
			SELECT COUNT(*) 
			FROM notification_general_log4 AS ngl 
				INNER JOIN notification_log4 AS nl ON nl.register = ngl.id
				LEFT JOIN (
					SELECT * 
					FROM read_mail AS rm 
					WHERE rm.id_auth_user = "{0}"
				) AS rm ON rm.id_mail = ngl.id 
			WHERE nl.username = "{1}" 
				AND rm.id IS NULL;
		"""
	
	return """
		SELECT COUNT(*) 
		FROM academic_send_mail_log AS ngl 
			INNER JOIN academic_send_mail_detail AS nl ON nl.academic_send_mail_log = ngl.id 
			LEFT JOIN (
				SELECT * 
				FROM read_mail_student AS rm 
				WHERE rm.id_auth_user = "{0}"
			) AS rm ON rm.id_mail = ngl.id 
		WHERE nl.username = "{1}" 
			AND rm.id IS NULL;
	"""

#********************************************** CARGA DE MENU
def q_count_request_change_weighting():
	return ("""select count(sub_rcw.id_rcw) as n_rcw from (   
	                select rcw.id as id_rcw from cpfecys.user_project as up
	                inner join cpfecys.request_change_weighting as rcw ON up.project = rcw.project
	                where rcw.status = 'pending'
	                and rcw.period = {0}
	                and up.assigned_user = {1}
	                group by rcw.id)
	            as sub_rcw;""")

def q_count_requestchange_activity():
	return ("""select count(sub_rca.id_rca) as n_rca from (
                    select rca.id as id_rca from cpfecys.user_project as up
                    inner join cpfecys.requestchange_activity as rca ON up.project = rca.course
                    where rca.status = 'pending'
                    and rca.semester = {0}
                    and up.assigned_user = {1}
                    group by rca.id)
                as sub_rca;""")

def q_count_request_change_grades():
	return ("""select count(sub_rcg.id_rcg) as n_rcg from (
                    select rcg.id as id_rcg from cpfecys.user_project as up
                    inner join cpfecys.request_change_grades as rcg ON up.project = rcg.project
                    where rcg.status = 'pending'
                    and rcg.period = {0}
                    and up.assigned_user = {1}
                    group by rcg.id)
                as sub_rcg;""")

def q_count_pending_reports():
	return ("""select count(rep.id) from (select assignation.* from (select upr.* from cpfecys.user_project as upr
                                                    inner join cpfecys.project as pro on upr.project= pro.id
                                                    where upr.assigned_user = {0})
                                as assignation
                                inner join cpfecys.user_project as upr2 on assignation.project = upr2.project
                                inner join cpfecys.auth_user as au_u on upr2.assigned_user = au_u.id
                                inner join cpfecys.auth_membership as au_m on au_u.id= au_m.user_id
                                inner join cpfecys.auth_group as au_g on au_m.group_id = au_g.id

                                where au_g.role = 'Teacher'
                                and upr2.assigned_user = {0}
                                group by assignation.project)
                as val_teacher
                inner join cpfecys.project as pro_vt on val_teacher.project = pro_vt.id
                inner join cpfecys.user_project as upr_vt on pro_vt.id = upr_vt.project
                inner join cpfecys.report as rep on rep.assignation = upr_vt.id
                inner join cpfecys.report_status as rep_s on rep.status = rep_s.id
                where rep_s.name = 'Grading'
                or rep_s.name='EnabledForTeacher';""")

def q_key_menu_user():
	return ("""select au_g.id as id_rol, substring(au_g.role, 1, 2) as rol
	            from cpfecys.auth_membership as au_m
	            inner join cpfecys.auth_group as au_g on au_m.group_id = au_g.id
	            where au_m.user_id = {0}
	            order by au_g.id""")

def q_count_membership_user():
	return ("""select count(am.group_id) from cpfecys.auth_membership as am
                                                                    where am.user_id={0}""")