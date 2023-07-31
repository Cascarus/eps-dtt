# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# Auth is for authenticaiton and access control
# -------------------------------------------------------------------------
from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
from allowed_career import validar

import redis
import config
import datetime

# variables para el acceso a la base de datos
redis_host = config.config_redis_host()
redis_port = config.config_redis_port()
redis_password = config.config_redis_password()
redis_db_1 = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, db=1)
redis_db_2 = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, db=2)
redis_db_3 = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, db=3)
redis_db_4 = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, db=4)

school = config.config_School()

if not request.env.web2py_runtime_gae:
      db = DAL(
            config.config_db_connection_string(),
            pool_size=1,
            migrate=True,
            fake_migrate_all=True,
            check_reserved=['all']
      ) 
else:
    db = DAL('google:datastore+ndb')
    session.connect(request, response, db=db)

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = ['*']
# if request.is_local and not configuration.get('app.production'):
#    response.generic_patterns.append('*')

# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
# response.formstyle = 'bootstrap4_inline'
# response.form_label_separator = ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db)

auth.settings.extra_fields['auth_user'] = [
      Field('phone', 'string', length=16, notnull=True, label=T("Phone")),
      Field('home_address', 'string', length=500, notnull=True, label=T("Home address")),
      Field('working', 'boolean', notnull=False, label=T("is Working"), writable=False, readable=False),
      Field('company_name', 'string', length=200, notnull=False, label=T("Company name")),
      Field('work_address', 'string', length=500, notnull=False, label=T("Work address")),
      Field('work_phone', 'string', length=500, notnull=False, label=T("Work phone")),
      Field('uv_token', 'string', length=64, notnull=False, writable=False, readable=False),
      Field('data_updated', 'boolean', notnull=False, writable=False, readable=False),
      Field('load_alerted', 'boolean', notnull=False, writable=False, readable=False),
      Field('photo', 'upload', notnull=False, label=T('Photo'),
            requires=[
                  IS_IMAGE(
                        extensions=('jpeg', 'png'),
                        maxsize=(200, 300),
                        error_message=T('Only files are accepted with extension') + ' png|jpg'+" "+T('with 200x300px size')+"."
                  )
            ]
      ),
      Field('cui', 'string', length=18, notnull=False, label=T('Cui'))
]

crud, service, plugins = Crud(db), Service(), PluginManager()

auth.define_tables(username=True, signature=False, migrate=True)

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = config.config_mail(auth)

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
auth.settings.actions_disabled.append('register')

# -------------------------------------------------------------------------
# maybe use the scheduler
# -------------------------------------------------------------------------
# if configuration.get('scheduler.enabled'):
#    from gluon.scheduler import Scheduler
#    scheduler = Scheduler(db, heartbeat=configuration.get('scheduler.heartbeat'))

# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
# >>> db.mytable.insert(myfield='value')
# >>> rows = db(db.mytable.myfield == 'value').select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
# -------------------------------------------------------------------------


# Table to save if we are done with setup
db.define_table('setup', Field('done', 'boolean', unique = True))

db.define_table(
      'area_level',
      Field('name', 'string', label=T('name'), unique=True, length=255),
      Field('description', 'text', label=T('description')),
      format='%(name)s'
)

db.define_table(
      'project',
      Field('project_id', 'string', unique=True, length=255, label=T('project_id')),
      Field('name', 'string', label=T('name'), notnull=True, unique=True, length=255),
      Field('area_level', 'reference area_level', label=T('area_level')),
      Field('description', 'text', label=T('description')),
      Field('physical_location', 'text', label=T('physical_location')),
      format='%(name)s'
)

db.define_table(
      'period',
      Field('name', 'string', length=255, label=T('name')),
      format='%(name)s'
)

db.define_table(
      'assignation_freeze',
      Field('pmonth', 'string', length=255, label=T('month')),
      Field('period', 'reference period', label=T('period'), unique=True),
      format='%(pmonth)s - %(period)s'
)

db.assignation_freeze.pmonth.requires = IS_IN_SET((
    T('January'),
    T('February'),
    T('March'),
    T('April'),
    T('May'),
    T('June'),
    T('July'),
    T('August'),
    T('September'),
    T('October'),
    T('November'),
    T('December')
))

db.define_table(
      'period_year',
      Field('yearp', 'integer', label=T('yearp')),
      Field('period', 'reference period', label=T('period'), notnull=True),
      format='%(yearp)s - %(period)s'
)

# The only valid assignation_status are: Failed, Successful
db.define_table(
      'assignation_status',
      Field('name', 'string', unique=True, label=T('name'), length=255),
      format='%(name)s'
)

# The relationship between a user and a subproject contains
# the history of the final practice,
# it has the starting cycle and the ending cycle
# it also is the central key for all operations with interesting data
# The None value in assignation_status means that it is currently not blocked
# any other value than None means that is locked and no further changes
# it can have.
# - (cpfecys module) method assignation_is_locked(assignation)
# - was created to check if this assignation can have modifications
db.define_table(
      'user_project',
      Field('assignation_status_comment', 'text', notnull=False, writable=False, readable=False),
      Field('assignation_comment', 'text', notnull=False, writable=False, readable=False),
      Field('assignation_ignored', 'boolean', notnull=True, default=False, writable=False, readable=False),
      Field('assignation_status', 'reference assignation_status', notnull=False,
            requires=IS_EMPTY_OR(IS_IN_DB(db, 'assignation_status.id', '%(name)s', zero=T('Active')))),
      Field('assigned_user', 'reference auth_user', label=T('assigned_user')),
      Field('project', 'reference project', label=T('project')),
      Field('period', 'reference period_year', label=T('period')),
      Field('pro_bono', 'boolean', length=255, notnull=False, label=T('pro_bono')),
      Field('hours', 'integer', label=T('Assignation Hours'), notnull=True),
      Field('periods', 'integer', notnull=True, label=T('periods')),
      format='%(project)s - %(assigned_user)s'
)

# This are the tables that store important links and uploaded
# files by admin.

# emarquez: INICIO periodos_multiples
# definicion de tablas para periodos multiples

db.define_table(
      "period_type",
      Field("description", "string", length=100, default=None, label=T("Descripcion")),
      Field("isVariable", "boolean", default=None, label=T("Variable")),
      format='%(description)s'
)

db.define_table(
      "period_detail",
      Field("description", "string", length=100, default=None, unique=True, label=T('Descripcion')),
      Field("date_start", "datetime", default=None, label=T('Fecha Inicio')),
      Field("date_finish", "datetime", default=None, label=T('Fecha Fin')),
      Field("date_start_semester", "date", default=None, label=T('Fecha Inicio Periodo')),
      Field("date_finish_semester", "date", default=None, label=T('Fecha fin Periodo')),
      Field('timeout_income_notes', 'integer', notnull=True,  label=T('timeout_income_notes')),
      Field("min_average", "integer", default=None, label=T('Minimo Average')),
      Field("max_average", "integer", default=None, label=T('Maximo Average')),
      Field("percentaje_income_activity", "integer", default=None, label=T('Porcentaje de actividad')),
      Field("period_type", "reference period_type", label=T('Tipo Periodo')),
      Field("period", "reference period", unique=True, label=T('Periodo'), writable=False),
      Field("period_active", "boolean", notnull=False),
      format='%(description)s'
)

""" Relations between tables (remove fields you don't need from requires) """
db.period_detail.period_type.requires = IS_IN_DB(db, 'period_type.id', '%(description)s')

# emarquez: FIN periodos_multiples

# emarquez: agregando relacion al tipo de periodo
db.define_table(
      'link',
      Field('url', 'text', notnull=True, label=T('url/URL')),
      Field('blank', 'boolean', label=T('blank')),
      Field('url_text', 'text', notnull=True, label=T('url_text')),
      Field('visible', 'boolean', notnull=True, label=T('visible')),
      Field('is_public', 'boolean', notnull=False, label=T('is_public')),
      Field("period_type", "reference period_type",label=T('Tipo Periodo')),
      format='%(url_text)s'
)

# Frontend notification
# emarquez: se agrega tipo d eperiodo
db.define_table(
      'front_notification',
      Field('name', 'string', notnull=True, label=T('name')),
      Field('content_text', 'text', notnull=False, label=T('content_text')),
      Field('url', 'string', notnull=False, label=T('url/URL')),
      Field('visible', 'boolean', notnull=False, label=T('visible')),
      Field('is_public', 'boolean', notnull=False, label=T('is_public')),
      Field('file_data', 'upload', uploadfolder=f'{request.folder if "/" in request.folder[len(request.folder) - 1] else request.folder + "/"}static/fn_files', default='', notnull=False, label=T('file_data')),
      Field('promoted', 'boolean', notnull=False, label=T('promoted')),
      Field("period_type", "reference period_type", label=T('Tipo Periodo')),
      Field('image_file', 'upload', uploadfolder=f'{request.folder if "/" in request.folder[len(request.folder) - 1] else request.folder + "/"}static/fn_files', default='', notnull=False, label=T('image_file')),
      format='%(name)s'
)

# Published files entity
# emarquez: se agrega tipo de periodo
db.define_table(
      'uploaded_file',
      Field('name', 'string', notnull=True, label=T('name')),
      Field('visible', 'boolean', label=T('visible')),
      Field('file_data', 'upload', default='', label=T('file_data')),
      Field('is_public', 'boolean', notnull=False, label=T('is_public')),
      Field("period_type", "reference period_type", label=T('Tipo Periodo')),
      format='%(name)s'
)

# User gruops relationships with files, notifications, links
db.define_table(
      'file_access',
      Field('user_role', 'reference auth_group', label=T('user_role')),
      Field('uploaded_file', 'reference uploaded_file', label=T('uploaded_file'))
)

db.define_table(
      'link_access',
      Field('user_role', 'reference auth_group', label=T('user_role')),
      Field('link', 'reference link', label=T('link'))
)

db.define_table(
      'notification_access',
      Field('user_role', 'reference auth_group', label=T('user_role')),
      Field('front_notification', 'reference front_notification', label=T('front_notification'))
)

# Reports and Activities structure
db.define_table(
      'report_restriction',
      Field('name', 'string', notnull=True, label=T('name'), length=50),
      Field('start_date', 'date', notnull=True, label=T('start date')),
      Field('end_date', 'date', notnull=True, label=T('end date')),
      Field('is_enabled', 'boolean', notnull=False, label=T('is enabled')),
      Field('is_final', 'boolean', notnull=False, label=T('is final'))
)

db.define_table(
      'report_requirement',
      Field('name', 'string', label=T('name')),
      format='%(name)s'
)

# Reports and Activities structure: EMARQUEZ: para periodos variables
db.define_table(
      'report_restriction_period',
      Field('name', 'string', notnull=True, label=T('name'), length=50),
      Field('period', 'reference period_detail', notnull=True, label=T('Periodo')),
      Field('start_report', 'date', notnull=True, label=T('inicio')),
      Field('end_report', 'date', notnull=True, label=T('fin')),
      Field('start_date', 'date', notnull=True, label=T('start date')),
      Field('end_date', 'date', notnull=True, label=T('end date')),
      Field('is_enabled', 'boolean', notnull=False, label=T('is enabled')),
      Field('is_final', 'boolean', notnull=False,  label=T('is final'))
)

# emarquez: se agregan los periodos
db.define_table(
      'area_report_requirement',
      Field('report_requirement', 'reference report_requirement', label=T('report requirement')),
      Field('area_level', 'reference area_level', label=T('area level')),
      Field('period_type', 'reference period_type', label=T('Tipo Periodo')),
      format='%(report_requirement)s %(area_level)s'
)

db.define_table(
      'report_status',
      Field('name', 'string', notnull=True, label=T('name')),
      Field('description', 'string', notnull=True),
      Field('order_number', 'integer', notnull=False, label=T('Order Number')),
      Field('icon', 'string', notnull=False, label=T('icon')),
      format='%(name)s'
)

db.define_table(
      'report',
      Field('created', 'date', label=T('created')),
      Field('assignation', 'reference user_project', label=T('assignation')),
      Field('report_restriction', 'reference report_restriction', label=T('report_restriction'), notnull=True),
      Field('score', 'integer', label=T('score')),
      Field('admin_score', 'integer', label=T('admin_score')),
      Field('min_score', 'integer', label=T('min_score')),
      Field('heading', 'text', label=T('heading')),
      Field('footer', 'text', label=T('footer')),
      Field('desertion_started', 'integer', label=T('started')),
      Field('desertion_gone', 'integer', label=T('gone')),
      Field('desertion_continued', 'integer', label=T('continued')),
      Field('hours', 'integer', label=T('hours')),
      Field('times_graded', 'integer', label=T('times_graded')),
      Field('status', 'reference report_status', notnull=True, label=T('status')),
      Field('teacher_comment', 'text', label=T('teacher comment')),
      Field('admin_comment', 'text', label=T('admin comment')),
      Field('score_date', 'date', label=T('score date')),
      # DTT Approval can be None, thus means that still hasn't been approved by DTT Admin
      # Approval is true when approved and false when failed
      Field('dtt_approval', 'boolean', label=T('dtt approval')),
      Field('period', 'reference period_year', label=T('period')),
      Field('never_delivered', 'boolean', label=T('Never was delivered?')),
)

db.define_table(
      'log_type',
      Field('name', 'string', notnull=True, label=T('name')),
      format='%(name)s'
)

db.define_table(
      'log_future',
      Field('entry_date', 'date', notnull=True, label=T('entry_date')),
      Field('description', 'text', notnull=True, label=T('description')),
      Field('report', 'reference report', label=T('report')),
      Field('period', 'reference period_year', label=T('period')),
      format='%(entry_date)s'
)

db.define_table(
      'log_entry',
      Field('idActivity', 'integer', notnull=False, label=T('Activity')),
      Field('tActivity', 'boolean', notnull=False, label=T('tActivity')),
      Field('log_type', 'reference log_type', label=T('log_type')),
      Field('entry_date', 'date', notnull=True, label=T('entry_date')),
      Field('description', 'text', notnull=True, label=T('description')),
      Field('report', 'reference report', label=T('report')),
      Field('period', 'reference period_year', label=T('period')),
      format='%(entry_date)s'
)

db.define_table(
      'metrics_type',
      Field('name', 'string', notnull=True, label=T('name')),
      format='%(name)s'
)

# Frontend notification
# LTZOC:Se modifico la ruta de almacenamiento
db.define_table(
      'magazine',
      Field('name', 'string', notnull=True, length=150, label=T('name')),
      Field('content_text', 'text', notnull=False, length=250, label=T('content_text')),
      Field('url', 'string', notnull=False, label=T('url/URL')),
      Field('visible', 'boolean', notnull=False, label=T('visible')),
      Field('image_file', 'upload', uploadfolder=f'{request.folder if "/" in request.folder[len(request.folder) - 1] else request.folder + "/"}static/mgz_files',
            default='', notnull=False, label=T('image_file'),
            requires=[
            #      IS_IN_DB(),
                  #IS_IMAGE(extensions=('jpeg', 'png'), maxsize=(320, 480), error_message='Sólo se aceptan archivos con extensión png|jpg y con dimensiones (320x480)px.')
            ]
      )
)

# COVALLE
db.define_table(
      'magazine_edition',
      Field('nedition', 'integer', notnull=True, label=T('No Edicion (*)')),
      Field('name', 'string', notnull=True, length=150, label=T('Nombre (*)')),
      Field('content_text', 'text', notnull=True, length=250, label=T('Descripcion (*)')),
      Field('url', 'string', notnull=True, label=T('url/URL (*)'))
)

db.magazine_edition.nedition.requires = [
    IS_NOT_EMPTY(error_message='Campo obligatorio')
]

db.magazine_edition.name.requires = [
    IS_NOT_EMPTY(error_message='Campo obligatorio')
]

db.magazine_edition.content_text.requires = [
    IS_NOT_EMPTY(error_message='Campo obligatorio')
]

db.magazine_edition.url.requires = [
    IS_NOT_EMPTY(error_message='Campo obligatorio')
]

# End of semester details of report
db.define_table(
      'log_final',
      Field('curso_asignados_actas', 'integer', notnull=True, label='Asignados en Actas'),
      Field('curso_en_parciales', 'integer', notnull=True, label='Alumnos en Parciales'),
      Field('curso_en_final', 'integer', notnull=True, label='Alumnos en Examen Final'),
      Field('curso_en_primera_restrasada', 'integer', notnull=True, label='Alumnos en Primera Retrasada'),
      Field('curso_en_segunda_restrasada', 'integer', notnull=True, label='Alumnos en Segunda Retrasada'),
      Field('lab_aprobados', 'integer', notnull=True, label='Aprobados Laboratorio'),
      Field('lab_reprobados', 'integer', notnull=True, label='Reprobados Laboratorio'),
      Field('lab_media', 'decimal(8,2)', notnull=True, label='Media Laboratorio'),
      Field('lab_promedio', 'decimal(8,2)', notnull=True, label='Promedio Laboratorio'),
      Field('curso_media', 'decimal(8,2)', notnull=True, label='media'),
      Field('curso_error', 'decimal(8,2)', notnull=True, label='error'),
      Field('curso_mediana', 'decimal(8,2)', notnull=True, label='mediana'),
      Field('curso_moda', 'decimal(8,2)', notnull=True, label='moda'),
      Field('curso_desviacion', 'decimal(8,2)', notnull=True, label='desviacion'),
      Field('curso_varianza', 'decimal(8,2)', notnull=True, label='varianza'),
      Field('curso_curtosis', 'decimal(8,2)', notnull=True, label='curtosis'),
      Field('curso_coeficiente', 'decimal(8,2)', notnull=True, label='coeficiente'),
      Field('curso_rango', 'decimal(8,2)', notnull=True, label='rango'),
      Field('curso_minimo', 'decimal(8,2)', notnull=True, label='minimo'),
      Field('curso_maximo', 'decimal(8,2)', notnull=True, label='maximo'),
      Field('curso_total', 'integer', notnull=True, label='total'),
      Field('curso_reprobados', 'integer', notnull=True, label='reprobados'),
      Field('curso_aprobados', 'integer', notnull=True, label='aprobados'),
      Field('curso_promedio', 'decimal(8,2)', notnull=True, label='Promedio'),
      Field('curso_created', 'date', notnull=True, label=T('entry_date')),
      Field('report', 'reference report', label=T('report')),
)

db.define_table(
      'log_metrics',
      Field('description', 'text', notnull=True, label=T('description')),
      Field('media', 'decimal(8,2)', notnull=True, label=T('media')),
      Field('error', 'decimal(8,2)', notnull=True, label=T('error')),
      Field('mediana', 'decimal(8,2)', notnull=True, label=T('mediana')),
      Field('moda', 'decimal(8,2)', notnull=True, label=T('moda')),
      Field('desviacion', 'decimal(8,2)', notnull=True, label=T('desviacion')),
      Field('varianza', 'decimal(8,2)', notnull=True, label=T('varianza')),
      Field('curtosis', 'decimal(8,2)', notnull=True, label=T('curtosis')),
      Field('coeficiente', 'decimal(8,2)', notnull=True, label=T('coeficiente')),
      Field('rango', 'decimal(8,2)', notnull=True, label=T('rango')),
      Field('minimo', 'decimal(8,2)', notnull=True, label=T('minimo')),
      Field('maximo', 'decimal(8,2)', notnull=True, label=T('maximo')),
      Field('total', 'integer', notnull=True, label=T('total')),
      Field('reprobados', 'integer', notnull=True, label=T('reprobados')),
      Field('aprobados', 'integer', notnull=True, label=T('aprobados')),
      Field('created', 'date', notnull=True, label=T('entry_date')),
      Field('report', 'reference report', label=T('report')),
      Field('metrics_type', 'reference metrics_type', label=T('type')),
      format='%(created)s'
)

# Project item requirements structure
db.define_table(
      'item_type',
      Field('name', 'string', length=255, notnull=True, label=T('name')),
      format='%(name)s'
)

# emarquez: adaptacion periodos variables
db.define_table(
      'item_restriction',
      Field('name', 'string', notnull=False, label=T('Name')),
      Field('is_public', 'boolean', default=False, notnull=True, label=T('is public')),
      Field('is_enabled', 'boolean', notnull=False, label=T('is enabled')),
      Field('permanent', 'boolean', notnull=False, label=T('permanent')),
      Field('item_type', 'reference item_type', label=T('item type')),
      Field('period_type', 'reference period_type', label=T('Tipo Periodo')),
      Field('period', 'reference period_year', label=T('period')),
      Field('hidden_from_teacher', 'boolean', notnull=False, label=T('Hidden from teacher')),
      Field('optional', 'boolean', notnull=False, label=T('Optional')),
      Field('limit_days', 'integer', notnull=False, label=T('limitdays')),
      Field('min_score', 'integer', notnull=False, label=T('minscore')),
      Field('is_unique', 'boolean', notnull=False, label=T('Is unique')),
      format='%(name)s'
)

db.define_table(
      'item_restriction_area',
      Field('area_level', 'reference area_level', label=T('area_level')),
      Field('item_restriction', 'reference item_restriction', label=T('item_restriction')),
      Field('is_enabled', 'boolean', notnull=False, label=T('is_enabled'))
)

db.define_table(
      'item_restriction_exception',
      Field('project', 'reference project', label=T('project')),
      Field('item_restriction', 'reference item_restriction', label=T('item_restriction'))
)

db.define_table(
      'mail_log',
      Field('sent_message', 'text', notnull=False, label=T('sent_message')),
      Field('roles', 'text', notnull=False, label=T('roles')),
      Field('projects', 'text', notnull=False, label=T('projects')),
      Field('sent', 'date', notnull=False, label=T('sent')),
)

db.define_table(
      'mailer_log',
      Field('sent_message', 'text', notnull=True, label=T('Sent Message')),
      Field('time_date', 'datetime', notnull=True, default=datetime.datetime.now(), label=T('Sent Time')),
      Field('destination', 'text', notnull=True, label=T('Destination')),
      Field('result_log', 'text', notnull=False, label=T('Log')),
      Field('success', 'boolean', notnull=True, label=T('Success')),
      Field('emisor', 'text', notnull=True, label=T('Emisor'))
)

db.define_table(
      'item',
      # AFAIK this is_active is for disabled items, true means enabled, false means disabled
      Field('is_active', 'boolean', notnull=False, label=T('is active'), default=True),
      Field('description', 'text', notnull=False, label=T('description')),
      Field('admin_comment', 'text', notnull=False, label=T('admin_comment')),
      Field('notified_mail', 'boolean', notnull=False, label=T('notified mail')),
      Field('uploaded_file', 'upload', default='', notnull=False, label=T('uploaded_file')),
      Field('done_activity', 'boolean', notnull=False, label=T('done_activity')),
      Field('created', 'reference period_year', label=T('created')),
      Field('item_restriction', 'reference item_restriction', label=T('item restriction')),
      Field('assignation', 'reference user_project', label=T('assignation')),
      Field('score', 'integer', notnull=False, label=T('score')),
      Field('min_score', 'integer', notnull=False, label=T('minscore')),
      format='%(item_restriction)s'
)

db.define_table(
      'day_of_week',
      Field('name', 'string', notnull=True, unique=True, length=255),
      format='%(name)s'
)

db.define_table(
      'item_schedule',
      Field('item', 'reference item', notnull=True),
      Field('physical_location', 'string', notnull=True, label=T('Location')),
      Field('day_of_week', 'reference day_of_week', label=T('Day'), notnull=True),
      Field('start_time', 'time', label=T('Start Hour'), notnull=True),
      Field('end_time', 'time', label=T('End Hour'), notnull=True)
)

db.define_table(
      'custom_parameters',
      Field('min_score', 'integer', notnull=False, label=T('min_score')),
      Field('rescore_max_count', 'integer', notnull=False, label=T('rescore_max_count')),
      Field('rescore_max_days', 'integer', default='', notnull=False, label=T('rescore_max_days')),
      Field('coordinator_name', 'string', default='', notnull=False, label=T('Coordinator Name')),
      Field('coordinator_title', 'string', default='', notnull=False, label=T('Coordinator Title')),
      Field('clearance_logo', 'upload', label=T('Clearance Logo')),
      Field('email_signature', 'text', label=T('Email Signature')),
)

db.define_table(
      'public_event',
      Field('name', 'string', label=T('Event Name'), length=255, notnull=True),
      Field('semester', 'reference period_year', notnull=True),
      Field('assignation', 'reference user_project', notnull=True),
      format='%(name)s'
)

db.define_table(
      'public_event_schedule',
      Field('public_event', 'reference public_event', notnull=True),
      Field('physical_location', 'string', notnull=True, label=T('Location')),
      Field('start_date', 'datetime', label=T('Start'), notnull=True),
      Field('end_date', 'datetime', label=T('End'), notnull=True)
)

# Tabla de alumnos (no auxiliares)
db.define_table(
      'academic',
      Field('carnet', 'string', unique=True, notnull=True, label=T('carnet'), searchable=True),
      Field('email', 'string', notnull=True, requires=IS_EMAIL(error_message='El email no es valido')),
      Field('id_auth_user', 'integer', notnull=False),
      Field('sign_honor_code', 'boolean', notnull=True, default=False),
      format='%(carnet)s'
)

# Tabla de asignacion de alumnos al curso
db.define_table(
      'academic_course_assignation',
      Field('carnet', 'reference academic', notnull=True, label=T('carnet')),
      Field('semester', 'reference period_year', notnull=True),
      Field('assignation', 'reference project', notnull=True),
      Field('laboratorio', 'boolean', notnull=True)
)

# Tabla General de avisos
db.define_table(
      'notification_general_log4',
      Field('subject', 'text', notnull=True, label=T('Asunto')),
      Field('sent_message', 'text', notnull=True, label=T('Sent Message')),
      Field('time_date', 'datetime', notnull=True, default=datetime.datetime.now(), label=T('Sent Time')),
      Field('emisor', 'text', notnull=True, label=T('Emisor')),
      Field('course', 'text', notnull=True, label=T('Curso')),
      Field('yearp', 'text', notnull=True, label=T('yearp')),
      Field('period', 'text', notnull=True, label=T('Periodo'))
)

# Tabla de avisos
db.define_table(
      'notification_log4',
      Field('destination', 'text', notnull=True, label=T('Destination')),
      Field('username', 'text', notnull=True, label=T('Username')),
      Field('result_log', 'text', notnull=False, label=T('Log')),
      Field('success', 'boolean', notnull=True, label=T('Success')),
      Field('register', 'reference notification_general_log4', notnull=True, label=T('Register'))
)

db.define_table(
      'academic_log',
      Field('user_name', 'text', notnull=False, label=T('Usuario')),
      Field('roll', 'text', notnull=False, label=T('Rol')),
      Field('operation_log', 'text', notnull=False, label=T('Operacion')),
      Field('before_carnet', 'text', notnull=False, label=T('Carnet anterior')),
      Field('after_carnet', 'text', notnull=False, label=T('Carnet actual')),
      Field('before_email', 'text', notnull=False, label=T('Correo anterior')),
      Field('after_email', 'text', notnull=False, label=T('Correo actual')),
      Field('description', 'text', notnull=False, label=T('Descripcion')),
      Field('id_academic', 'text', notnull=False, label=T('id_academic')),
      Field('id_period', 'integer', notnull=False, label=T('id_period')),
      Field('date_log', 'datetime', notnull=True, default=datetime.datetime.now(), label=T('Fecha'))
)

db.define_table(
      'academic_course_assignation_log',
      Field('user_name', 'text', notnull=False, label=T('Usuario')),
      Field('roll', 'text', notnull=False, label=T('Rol')),
      Field('operation_log', 'text', notnull=False, label=T('Operacion')),
      Field('before_carnet', 'text', notnull=False, label=T('Carnet anterior')),
      Field('after_carnet', 'text', notnull=False, label=T('Carnet actual')),
      Field('before_course', 'text', notnull=False, label=T('Curso anterior')),
      Field('after_course', 'text', notnull=False, label=T('Curso actual')),
      Field('before_year', 'text', notnull=False, label=T('Año anterior')),
      Field('after_year', 'text', notnull=False, label=T('Año actual')),
      Field('before_semester', 'text', notnull=False, label=T('Semestre anterior')),
      Field('after_semester', 'text', notnull=False, label=T('Semestre actual')),
      Field('before_laboratory', 'text', notnull=False, label=T('Laboratorio anterior')),
      Field('after_laboratory', 'text', notnull=False, label=T('Laboratorio actual')),
      Field('description', 'text', notnull=False, label=T('Descripcion')),
      Field('id_academic_course_assignation', 'text', notnull=False, label=T('id_academic_course_assignation')),
      Field('id_period', 'integer', notnull=False, label=T('id_period')),
      Field('date_log', 'datetime', notnull=True, default=datetime.datetime.now(), label=T('Fecha'))
)

db.define_table(
      'library',
      Field('name', 'text', notnull=True, unique=False, label=T('Name')),
      Field('file_data', 'upload', notnull=True, label=T('File_data'), 
            requires=[
                IS_UPLOAD_FILENAME(extension='(pdf|zip|rar)', error_message='Solo se aceptan archivos con extension zip|pdf|rar'),
                IS_LENGTH(2097152, error_message='El tamaño máximo del archivo es 2MB')
            ]
      ),
      Field('description', 'text', notnull=True, unique=False, label=T('Description')),
      Field('visible', 'boolean', label=T('Visible')),
      Field('period', 'reference period_year', notnull=True, label=T('Period')),
      Field('project', 'reference project', notnull=True, label=T('Course')),
      Field('owner_file', 'reference auth_user', notnull=True, label=T('Owner_file'))
)

db.define_table(
      'activity_category',
      Field('category', 'string', notnull=True, unique=False, label=T('category')),
      Field('description', 'text', notnull=True, unique=False, label=T('description')),
      Field('hidden_academic_tutor', 'boolean', notnull=True, label=T('hidden_academic_tutor')),
      Field('timeout', 'integer', notnull=True, unique=False, label=T('timeout')),
      format='%(category)s'
)

# Table of weighting
db.define_table(
      'course_activity_category',
      Field('category', 'reference activity_category', notnull=True, label=T('category')),
      Field('grade', 'decimal(5,2)', notnull=False, label=T('grade')),
      Field('specific_grade', 'boolean', notnull=True, label=T('specific grade')),
      Field('semester', 'reference period_year', notnull=True),
      Field('assignation', 'reference project', notnull=True),
      Field('laboratory', 'boolean', notnull=True, label=T('laboratory')),
      Field('teacher_permition', 'boolean', notnull=True, label=T('teacher permition'))
)

# Table of weighting log
db.define_table(
      'course_activity_category_log',
      Field('user_name', 'string', notnull=True, label=T('User')),
      Field('roll', 'string', notnull=True, label=T('Roll')),
      Field('operation_log', 'string', notnull=True, label=T('Operation')),
      Field('before_category', 'string', notnull=False, label=T('before category')),
      Field('after_category', 'string', notnull=False, label=T('after category')),
      Field('before_grade', 'decimal(5,2)', notnull=False, label=T('before grade')),
      Field('after_grade', 'decimal(5,2)', notnull=False, label=T('after grade')),
      Field('before_specific_grade', 'boolean', notnull=False, label=T('before specific grade')),
      Field('after_specific_grade', 'boolean', notnull=False, label=T('after specific grade')),
      Field('semester', 'string', notnull=False, label=T('semester')),
      Field('yearp', 'string', notnull=False, label=T('year')),
      Field('assignation', 'string', notnull=False),
      Field('before_laboratory', 'boolean', notnull=False, label=T('before laboratory')),
      Field('after_laboratory', 'boolean', notnull=False, label=T('after laboratory')),
      Field('before_teacher_permition', 'boolean', notnull=False, label=T('before teacher permition')),
      Field('after_teacher_permition', 'boolean', notnull=False, label=T('after teacher permition')),
      Field('description', 'string', notnull=False, label=T('description'))
)

db.define_table(
      'student_control_period',
      Field('period_name', 'string', notnull=True, unique=False, label=T('period name')),
      Field('date_start', 'datetime', notnull=True, default=datetime.datetime.now(), label=T('Date Start')),
      Field('date_finish', 'datetime', notnull=True, default=datetime.datetime.now(), label=T('Date Finish')),
      Field('timeout_income_notes', 'integer', notnull=True,  label=T('timeout_income_notes')),
      Field('percentage_income_activity', 'integer', notnull=True, default=35, label=T('Percentage income activity')),
      Field('min_average', 'decimal(5,2)', notnull=True, default=61.00, label=T('Min Average')), 
      Field('max_average', 'decimal(5,2)', notnull=True, default=85.00, label=T('Max Average')),
      Field('date_start_semester', 'date', notnull=True, label=T('Date Start Semester')),
      Field('date_finish_semester', 'date', notnull=True, label=T('Date Finish Semester'))
)

db.define_table(
      'partials',
      Field('name', 'string', notnull=True, unique=False, label=T('name')),
)

db.define_table(
      'course_activity',
      Field('course_activity_category', 'reference course_activity_category', notnull=True, label=T('category')),
      Field('name', 'string', notnull=True, unique=False, label=T('name')),
      Field('description', 'text', notnull=True, unique=False, label=T('description')),
      Field('grade', 'decimal(5,2)', notnull=False, label=T('grade')),
      Field('semester', 'reference period_year', notnull=True),
      Field('assignation', 'reference project', notnull=True),
      Field('laboratory', 'boolean', notnull=True, label=T('laboratory')),
      Field('teacher_permition', 'boolean', notnull=True, label=T('teacher permition')),
      Field('date_start', 'date', notnull=True, default=datetime.datetime.now(), label=T('Date Start')),
      Field('date_finish', 'date', notnull=True, default=datetime.datetime.now(), label=T('Date Finish'))
)

db.define_table(
      'course_activity_without_metric',
      Field('name', 'string', notnull=True, unique=False, label=T('Name')),
      Field('description', 'text', notnull=False, unique=False, label=T('Description')),
      Field('fileReport', 'upload', notnull=False, label='Reporte',
            requires=[
                  IS_NULL_OR(IS_UPLOAD_FILENAME(extension='(pdf|zip|rar)', error_message='Solo se aceptan archivos con extension zip|pdf|rar')),
                  IS_LENGTH(2097152, error_message='El tamaño máximo del archivo es 2MB')
            ]
      ),
      Field('semester', 'reference period_year', notnull=True),
      Field('assignation', 'reference project', notnull=True),
      Field('laboratory', 'boolean', notnull=True, label=T('Laboratory')),
      Field('teacher_permition', 'boolean', notnull=True, label=T('Teacher Permition')),
      Field('date_start', 'date', notnull=True, default=datetime.datetime.now(), label=T('Date'))
)

db.define_table(
      'course_activity_log',
      Field('user_name', 'string', notnull=False, label='Usuario'),
      Field('roll', 'string', notnull=False, label='Rol'),
      Field('operation_log', 'string', notnull=False, label='Operacion'),
      Field('course', 'string', notnull=False, label='Curso'),
      Field('yearp', 'string', notnull=False, label='yearp'),
      Field('period', 'string', notnull=False, label='Periodo'),
      Field('metric', 'boolean', notnull=False, label='Metrica'),
      Field('before_course_activity_category', 'string', notnull=False, label='Categoria Anterior'),
                Field('after_course_activity_category', 'string',
                      notnull=False, label='Categoria Actual'),
                Field('before_name', 'string', notnull=False,
                      label='Nombre Anterior'),
                Field('after_name', 'string',
                      notnull=False, label='Nombre Actual'),
                Field('before_description', 'text', notnull=False,
                      label='Descripcion Anterior'),
                Field('after_description', 'text',
                      notnull=False, label='Descripcion Actual'),
                Field('before_grade', 'decimal(5,2)',
                      notnull=False, label='Nota Anterior'),
                Field('after_grade', 'decimal(5,2)',
                      notnull=False, label='Nota Actual'),
                Field('before_file', 'upload', notnull=False,
                      label='Reporte Anterior'),
                Field('after_file', 'upload', notnull=False,
                      label='Reporte Actual'),
                Field('before_laboratory', 'boolean',
                      notnull=False, label='Laboratorio Anterior'),
                Field('after_laboratory', 'boolean',
                      notnull=False, label='Laboratorio Actual'),
                Field('before_teacher_permition', 'boolean',
                      notnull=False, label='permiso Catedratico Anterior'),
                Field('after_teacher_permition', 'boolean',
                      notnull=False, label='Permiso Catedratico Actual'),
                Field('before_date_start', 'date', notnull=False,
                      label='Fecha Inicio Anterior'),
                Field('after_date_start', 'date', notnull=False,
                      label='Fecha Inicio Actual'),
                Field('before_date_finish', 'date', notnull=False,
                      label='Fecha Finalizacion Anterior'),
                Field('after_date_finish', 'date', notnull=False,
                      label='Fecha Finalizacion Actual'),
                Field('date_log', 'datetime', notnull=True,
                      default=datetime.datetime.now(), label='Fecha')
                )

db.define_table('requestchange_activity',
                Field('user_id', 'reference auth_user',
                      notnull=True, label='Usuario_ID'),
                Field('roll', 'string', notnull=True, label='Rol'),
                Field('status', 'string', notnull=True, label='Estado'),
                Field('user_resolve', 'reference auth_user',
                      notnull=False, label='Usuario Resolvio'),
                Field('roll_resolve', 'string',
                      notnull=False, label='Rol Resolvio'),
                Field('description', 'string', notnull=True,
                      unique=False, label='Descripción'),
                Field('date_request', 'datetime', notnull=True,
                      default=datetime.datetime.now(), label='Fecha'),
                Field('date_request_resolve', 'datetime',
                      notnull=False, label='Fecha Resolvio'),
                Field('course_activity_category', 'reference course_activity_category',
                      notnull=True, label=T('category')),
                Field('semester', 'reference period_year',
                      notnull=True, label='Periodo'),
                Field('course', 'reference project',
                      notnull=True, label='Curso')
                )


db.define_table('requestchange_course_activity',
                Field('requestchange_activity', 'reference requestchange_activity',
                      notnull=True, label='Solicitud Cambio'),
                Field('operation_request', 'string',
                      notnull=True, label='Operacion'),
                Field('activity', 'reference course_activity',
                      notnull=False, label='Actividad'),
                Field('name', 'string', notnull=False,
                      unique=False, label=T('name')),
                Field('description', 'text', notnull=False,
                      unique=False, label=T('description')),
                Field('grade', 'decimal(5,2)', notnull=False, label=T('grade')),
                Field('date_start', 'date', notnull=False,
                      default=datetime.datetime.now(), label=T('Date Start')),
                Field('date_finish', 'date', notnull=False,
                      default=datetime.datetime.now(), label=T('Date Finish'))
                )

db.define_table('requestchange_activity_log',
                Field('user_request', 'string', notnull=True,
                      label='Usuario Solicitud'),
                Field('roll_request', 'string', notnull=True, label='Rol'),
                Field('status', 'string', notnull=True, label='Estado'),
                Field('user_resolve', 'string', notnull=False,
                      label='Usuario Resolvio'),
                Field('roll_resolve', 'string',
                      notnull=False, label='Rol Resolvio'),
                Field('description', 'text', notnull=True,
                      unique=False, label='Descripción'),
                Field('date_request', 'datetime', notnull=True,
                      default=datetime.datetime.now(), label='Fecha'),
                Field('date_request_resolve', 'datetime',
                      notnull=False, label='Fecha Resolvio'),
                Field('category_request', 'string',
                      notnull=True, label=T('category')),
                Field('semester', 'string', notnull=True, label='Periodo'),
                Field('yearp', 'integer', notnull=True, label='Año'),
                Field('course', 'string', notnull=True, label='Curso')
                )

db.define_table('requestchange_course_activity_log',
                Field('requestchange_activity', 'reference requestchange_activity_log',
                      notnull=True, label='Solicitud Cambio'),
                Field('operation_request', 'string',
                      notnull=True, label='Operacion'),
                Field('activity', 'integer', notnull=False, label='Actividad'),
                Field('name', 'string', notnull=False,
                      unique=False, label=T('name')),
                Field('description', 'text', notnull=False,
                      unique=False, label=T('description')),
                Field('grade', 'decimal(5,2)', notnull=False, label=T('grade')),
                Field('date_start', 'date', notnull=False,
                      default=datetime.datetime.now(), label=T('Date Start')),
                Field('date_finish', 'date', notnull=False,
                      default=datetime.datetime.now(), label=T('Date Finish'))
                )

db.define_table('request_change_weighting',
                Field('user_id', 'reference auth_user',
                      notnull=True, label=T('User')),
                Field('roll', 'string', notnull=False, label='Rol'),
                Field('status', 'string', notnull=True, label=T('Status')),
                Field('resolve_user', 'reference auth_user',
                      notnull=False, label=T('Resolve User')),
                Field('roll_resolve', 'string', notnull=False, label='Rol'),
                Field('description', 'text', notnull=False,
                      label=T('Description')),
                Field('date_request', 'datetime', notnull=True,
                      default=datetime.datetime.now(), label=T('Date')),
                Field('date_request_resolve', 'datetime',
                      notnull=False, label=T('Resolve Date')),
                Field('period', 'reference period_year',
                      notnull=True, label=T('Periodo')),
                Field('project', 'reference project',
                      notnull=True, label=T('Project'))
                )

db.define_table('request_change_weighting_detail',
                Field('request_change_weighting', 'reference request_change_weighting',
                      notnull=True, label=T('Request Change')),
                Field('operation_request', 'text',
                      notnull=True, label=T('Operation')),
                Field('course_category', 'reference course_activity_category',
                      notnull=False, label=T('Course Category')),
                Field('category', 'reference activity_category',
                      notnull=False, label=T('Category')),
                Field('grade', 'decimal(5,2)', notnull=False, label=T('Grade')),
                Field('specific_grade', 'boolean',
                      notnull=False, label=T('Specific Grade'))
                )

db.define_table('request_change_w_log',
                Field('r_c_w_id', 'integer', notnull=False),
                Field('username', 'string', notnull=True, label=T('User')),
                Field('roll', 'string', notnull=False, label='Rol'),
                Field('before_status', 'string',
                      notnull=True, label=T('Status')),
                Field('after_status', 'string',
                      notnull=True, label=T('Status')),
                Field('resolve_user', 'string',
                      notnull=False, label=T('Resolve User')),
                Field('roll_resolve', 'string', notnull=False, label='Rol'),
                Field('description', 'text', notnull=False,
                      label=T('Description')),
                Field('date_operation', 'datetime', notnull=True,
                      default=datetime.datetime.now(), label=T('Date')),
                Field('date_request', 'datetime', notnull=True,
                      default=datetime.datetime.now(), label=T('Date Request')),
                Field('date_request_resolve', 'datetime',
                      notnull=False, label=T('Resolve Date')),
                Field('semester', 'string', notnull=True, label=T('Semester')),
                Field('yearp', 'string', notnull=True, label=T('Year')),
                Field('project', 'string', notnull=True, label=T('Project'))
                )

db.define_table('request_change_w_detail_log',
                Field('request_change_w_log', 'reference request_change_w_log',
                      notnull=True, label=T('Request Change')),
                Field('operation_request', 'string',
                      notnull=True, label=T('Operation')),
                Field('course_category', 'string',
                      notnull=False, label=T('Course Category')),
                Field('category', 'string', notnull=False, label=T('Category')),
                Field('before_grade', 'decimal(5,2)',
                      notnull=False, label=T('Before Grade')),
                Field('after_grade', 'decimal(5,2)',
                      notnull=False, label=T('After Grade')),
                Field('before_specific_grade', 'boolean',
                      notnull=False, label=T('Before Specific Grade')),
                Field('after_specific_grade', 'boolean',
                      notnull=False, label=T('After Specific Grade'))
                )


db.define_table(
      'course_laboratory_exception',
      Field('project', 'reference project', notnull=True, unique=True, label=T('Course')),
      Field('t_edit_lab', 'boolean', notnull=True, label=T('Teacher can edit laboratory')),
      Field('s_edit_course', 'boolean', notnull=True, label=T('Student can edit course')),
      format='%(project)s'
)

db.define_table(
      'course_limit_exception',
      Field('project', 'reference project', notnull=True, unique=True, label=T('Course')),
      Field('semester_repet', 'boolean', notnull=True, label=T('Repeat Each Semester')),
      Field('date_finish', 'datetime', notnull=True, label=T('Date Finish')),
      format='%(project)s'
)

# emaquez: excepciones por periodo
db.define_table('course_limit_exception_period',
                Field('project', 'reference project', notnull=True,
                      unique=True, label=T('Course')),
                Field('period_repet', 'boolean', notnull=True,
                      label=T('Repetir periodos variables')),
                Field('period', 'reference period_detail',
                      notnull=True,  label=T('Periodo')),
                Field('date_finish', 'datetime',
                      notnull=True, label=T('Date Finish'))
                )
# emaquez: fin definicion tabla excepciones por periodo

# emarquez: excepciones course_laboratorio por period
db.define_table('course_laboratory_exception_period',
                Field('project', 'reference project', notnull=True,
                      unique=True, label=T('Course')),
                Field('period', 'reference period_detail',
                      notnull=True, label=T('Periodo')),
                Field('t_edit_lab', 'boolean', notnull=True,
                      label=T('Teacher can edit laboratory')),
                Field('s_edit_course', 'boolean', notnull=True,
                      label=T('Student can edit course'))
                )
# emarquez: excepciones course_laboratorio por period

db.define_table('grades',
                Field('academic_assignation', 'reference academic_course_assignation',
                      notnull=True, label=T('Academic Assignation')),
                Field('activity', 'reference course_activity',
                      notnull=True, label=T('Activity')),
                Field('grade', 'decimal(5,2)', notnull=False, label=T('Grade'))
                )

db.define_table('grades_log',
                Field('user_name', 'string', notnull=False,
                      label=T('User Name Before')),
                Field('roll', 'string', notnull=False, label=T('Role')),
                Field('operation_log', 'string',
                      notnull=False, label=T('Operation')),
                Field('academic_assignation_id', 'string',
                      notnull=False, label=T('Academic Assignation Id')),
                Field('academic', 'string', notnull=False, label=T('Academic')),
                Field('activity', 'string', notnull=False, label=T('Activity')),
                Field('activity_id', 'string',
                      notnull=False, label=T('Activity Id')),
                Field('category', 'string', notnull=False, label=T('Category')),
                Field('project', 'string', notnull=False, label=T('Course')),
                Field('yearp', 'string', notnull=False, label=T('Year')),
                Field('period', 'string', notnull=False, label=T('Period')),
                Field('before_grade', 'decimal(5,2)',
                      notnull=False, label=T('Grade Before')),
                Field('after_grade', 'decimal(5,2)',
                      notnull=False, label=T('Grade After')),
                Field('description', 'text', notnull=False,
                      label=T('Description')),
                Field('date_log', 'datetime', notnull=True,
                      default=datetime.datetime.now(), label=T('Date'))
                )

db.define_table('request_change_grades',
                Field('activity', 'reference course_activity',
                      notnull=True, label=T('Activity')),
                Field('user_id', 'reference auth_user',
                      notnull=True, label=T('User')),
                Field('period', 'reference period_year',
                      notnull=True, label=T('Periodo')),
                Field('project', 'reference project',
                      notnull=True, label=T('Project')),
                Field('roll', 'string', notnull=False, label='Rol'),
                Field('status', 'string', notnull=True, label=T('Status')),
                Field('resolve_user', 'reference auth_user',
                      notnull=False, label=T('Resolve User')),
                Field('roll_resolve', 'string', notnull=False, label='Rol'),
                Field('description', 'text', notnull=False,
                      label=T('Description')),
                Field('date_request', 'datetime', notnull=True,
                      default=datetime.datetime.now(), label=T('Date')),
                Field('date_request_resolve', 'datetime',
                      notnull=False, label=T('Resolve Date'))
                )

db.define_table('request_change_grades_detail',
                Field('request_change_grades', 'reference request_change_grades',
                      notnull=True, label=T('Request Change Grades')),
                Field('academic_assignation', 'reference academic_course_assignation',
                      notnull=True, label=T('Academic Assignation')),
                Field('operation_request', 'string',
                      notnull=False, label=T('Operation')),
                Field('before_grade', 'decimal(5,2)',
                      notnull=False, label=T('Before Grade')),
                Field('after_grade', 'decimal(5,2)',
                      notnull=False, label=T('After Grade'))
                )

db.define_table('request_change_g_log',
                Field('r_c_g_id', 'integer', notnull=False),
                Field('username', 'string', notnull=True, label=T('User')),
                Field('roll', 'string', notnull=False, label='Rol'),
                Field('before_status', 'string',
                      notnull=True, label=T('Status')),
                Field('after_status', 'string',
                      notnull=True, label=T('Status')),
                Field('resolve_user', 'string',
                      notnull=False, label=T('Resolve User')),
                Field('roll_resolve', 'string', notnull=False, label='Rol'),
                Field('description', 'string', notnull=False,
                      label=T('Description')),
                Field('description_log', 'string', notnull=False,
                      label=T('Description Log')),
                Field('date_operation', 'datetime', notnull=True,
                      default=datetime.datetime.now(), label=T('Date')),
                Field('date_request', 'datetime', notnull=True,
                      default=datetime.datetime.now(), label=T('Date Request')),
                Field('date_request_resolve', 'datetime',
                      notnull=False, label=T('Resolve Date')),
                Field('semester', 'string', notnull=True, label=T('Semester')),
                Field('yearp', 'string', notnull=True, label=T('Year')),
                Field('activity', 'string', notnull=True, label=T('Activity')),
                Field('category', 'string', notnull=True, label=T('Category')),
                Field('project', 'string', notnull=True, label=T('Project'))
                )

db.define_table('request_change_grade_d_log',
                Field('request_change_g_log', 'reference request_change_g_log',
                      notnull=True, label=T('Request Change')),
                Field('operation_request', 'string',
                      notnull=True, label=T('Operation')),
                Field('academic', 'string', notnull=False, label=T('Academic')),
                Field('before_grade', 'decimal(5,2)',
                      notnull=False, label=T('Before Grade')),
                Field('after_grade', 'decimal(5,2)',
                      notnull=False, label=T('After Grade'))
                )

db.define_table('academic_send_mail_log',
                Field('subject', 'text', notnull=True, label=T('Asunto')),
                Field('sent_message', 'text', notnull=True,
                      label=T('Sent Message')),
                Field('time_date', 'datetime', notnull=True,
                      default=datetime.datetime.now(), label=T('Sent Time')),
                Field('emisor', 'text', notnull=True, label=T('Emisor')),
                Field('course', 'text', notnull=True, label=T('Curso')),
                Field('yearp', 'text', notnull=True, label=T('yearp')),
                Field('period', 'text', notnull=True, label=T('Periodo')),
                Field('mail_state', 'text', notnull=True, label=T('State'))
                )

db.define_table('academic_send_mail_detail',
                Field('academic_send_mail_log', 'reference academic_send_mail_log',
                      notnull=True, label=T('academic_send_mail_log')),
                Field('username', 'string', notnull=True, label=T('username')),
                Field('email', 'string', notnull=True, label=T('Email'))
                )

db.define_table('read_mail',
                Field('id_auth_user', 'integer',
                      notnull=True, label=T('id_auth_user')),
                Field('id_mail', 'integer', notnull=True, label=T('id_mail'))
                )

db.define_table('read_mail_student',
                Field('id_auth_user', 'integer',
                      notnull=True, label=T('id_auth_user')),
                Field('id_mail', 'integer', notnull=True, label=T('id_mail'))
                )


@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator'))
def check_student(check_carnet):
    svp = db(db.validate_student).select().first()
    if svp is not None:
        try:
            # CONSUME THE WEBSERVICE
            from gluon.contrib.pysimplesoap.client import SoapClient
            from gluon.contrib.pysimplesoap.client import SimpleXMLElement
            client = SoapClient(
                location=svp.supplier,
                action=svp.supplier+"/"+svp.action_service,
                namespace=svp.supplier,
                soap_ns=svp.type_service, trace=True, ns=False)

            import cpfecys
            year = cpfecys.current_year_period()
            sent = "<"+svp.send+">"
            for svpf in db(db.validate_student_parameters).select():
                sent += "<"+svpf.parameter_name_validate+">" + \
                    svpf.parameter_value_validate+"</"+svpf.parameter_name_validate+">"
            sent += "<CARNET>" + \
                str(check_carnet)+"</CARNET><CICLO>" + \
                str(year.yearp)+"</CICLO></"+svp.send+">"
            back = client.call(svp.action_service, xmlDatos=sent)

            # PREPARE FOR RETURNED XML WEB SERVICE
            xml = back.as_xml()

            xml = xml.replace('&lt;', '<')
            xml = xml.replace('&gt;', '>')
            inicio = xml.find("<"+svp.receive+">")
            final = xml.find("</"+svp.receive+">")
            xml = xml[inicio:(final+17)]
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml)
            xml = SimpleXMLElement(xml)

            # VARIABLE TO CHECK THE CORRECT FUNCTIONING
            CARNET = xml.CARNET
            NOMBRES = xml.NOMBRES
            APELLIDOS = xml.APELLIDOS
            CORREO = xml.CORREO

            # Unicode Nombres
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
                            appellidos_return = appellidos_return + \
                                " " + str(apellido)
                    except:
                        try:
                            temp = unicode(apellido).encode('utf-8').replace('Ã¡', 'á').replace('Ã©', 'é').replace('Ã­', 'í').replace('Ã³', 'ó').replace('Ãº', 'ú').replace(
                                'Ã±', 'ñ').replace('Ã', 'Á').replace('Ã‰', 'É').replace('Ã', 'Í').replace('Ã“', 'Ó').replace('Ãš', 'Ú').replace('Ã‘', 'Ñ').replace('Ã¼‘', 'ü')
                        except:
                            None

                        apellido = temp
                        if appellidos_return is None:
                            appellidos_return = str(apellido)
                        else:
                            appellidos_return = appellidos_return + \
                                " " + str(apellido)

                NOMBRES = appellidos_return
            # Unicode APELLIDOS
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
                            appellidos_return = appellidos_return + \
                                " " + str(apellido)
                    except:
                        try:
                            temp = unicode(apellido).encode('utf-8').replace('Ã¡', 'á').replace('Ã©', 'é').replace('Ã­', 'í').replace('Ã³', 'ó').replace('Ãº', 'ú').replace(
                                'Ã±', 'ñ').replace('Ã', 'Á').replace('Ã‰', 'É').replace('Ã', 'Í').replace('Ã“', 'Ó').replace('Ãš', 'Ú').replace('Ã‘', 'Ñ').replace('Ã¼‘', 'ü')
                        except:
                            None

                        apellido = temp
                        if appellidos_return is None:
                            appellidos_return = str(apellido)
                        else:
                            appellidos_return = appellidos_return + \
                                " " + str(apellido)

                APELLIDOS = appellidos_return

            if (CARNET is None or CARNET == '') and (NOMBRES is None or NOMBRES == '') and (APELLIDOS is None or APELLIDOS == '') and (CORREO is None or CORREO == ''):
                return dict(flag=False, error=False, message=T('The record was removed because the user is not registered to the academic cycle'))
            else:
                import allowed_career as v
                val = v.validar(db)
                isStuden = False
                for c in root.findall('CARRERA'):
                    unidad = c.find('UNIDAD').text
                    extension = c.find('EXTENSION').text
                    carrera = c.find('CARRERA').text

                    isStuden = val(unidad=unidad, extension=extension,
                                   carrera=carrera)

                    if isStuden:
                        break

                if not isStuden:
                    return dict(flag=False, error=False, message=T('The record was removed because students not enrolled in career allowed to use the system'))
                else:
                    return dict(flag=True, carnet=CARNET, nombres=(NOMBRES), apellidos=(APELLIDOS), correo=str(CORREO), error=False)
        except:
            return dict(flag=False, error=True, message=T('Error with web service validation'))
    else:
        return dict(flag=False, error=True, message=T('Error with web service validation'))

db.academic._after_insert.append(lambda f, id: academic_insert(f, id))
db.academic._after_update.append(lambda s, f: academic_update(f))
db.academic._before_delete.append(lambda s: academic_delete(s))

db.auth_user._after_update.append(lambda s, f: auth_user_update(f, s))
db.auth_user._before_delete.append(lambda s: auth_user_delete(s))

def split_num(var):
    var_arg = str(var)
    (first_part, second_part) = str(var_arg).split('=')
    (result, garbage) = str(second_part).split(')')
    return result

############################## AUTH_USER TRIGGERS####################################


def auth_user_update(*args):
    try:
        try:
            review = db((db.photo_review.user_id == str(
                int(split_num(args[1]))))).select().first()
            if (review.photo != str(args[0]['photo'])):
                db(db.photo_review.id == review.id).delete()
        except:
            None

        academic_var = db.academic(
            db.academic.id_auth_user == str(int(split_num(args[1]))))
        if academic_var == None:
            academic_var = db.academic(
                db.academic.carnet == args[0]['username'])

        db(db.academic.id == academic_var.id).update(id_auth_user=str(int(split_num(args[1]))),
                                                     carnet=str(
                                                         args[0]['username']),
                                                     email=str(args[0]['email']))
        # log
        import cpfecys
        cperiod = cpfecys.current_year_period()
        db.academic_log.insert(user_name='system',
                               roll='system',
                               operation_log='update',
                               before_carnet=academic_var.carnet,
                               before_email=academic_var.email,
                               after_carnet=args[0]['username'],
                               after_email=str(args[0]['email']),
                               id_period=cperiod,
                               description=T('Registration data was update because auth_user was update'))
    except:
        None


def auth_user_delete(*args):
    try:
        auth_user_var = db.auth_user(
            db.auth_user.id == str(int(split_num(args[0]))))
        academic_var = db.academic(
            db.academic.carnet == str(auth_user_var.username))
        if academic_var != None:
            db(db.academic.id == academic_var.id).delete()
            import cpfecys
            cperiod = cpfecys.current_year_period()
            db.academic_log.insert(user_name='system',
                                   roll='system',
                                   operation_log='delete',
                                   before_carnet=academic_var.carnet,
                                   before_email=academic_var.email,
                                   id_period=cperiod,
                                   description=T('Registration data was deleted because auth_user was remove'))
    except:
        None
############################## ACADEMIC TRIGGERS####################################


def academic_delete(*args):
    try:
        academic_var = db.academic(
            db.academic.id == str(int(split_num(args[0]))))
        user_var = db.auth_user(db.auth_user.username ==
                                str(academic_var.carnet))

        if user_var != None:
            academic_var = db.auth_group(db.auth_group.role == 'Academic')
            membership_var = db.auth_membership((db.auth_membership.user_id == user_var.id) & (
                db.auth_membership.group_id == academic_var.id))
            db(db.auth_membership.id == membership_var.id).delete()
            if db(db.auth_membership.user_id == academic_var.id).select().first() is None:
                db(db.auth_user.id == user_var.id).delete()
    except:
        None


def academic_update(*args):
    try:

        auth_var = db.auth_user(
            db.auth_user.id == str(args[0]['id_auth_user']))
        db(db.auth_user.id == auth_var.id).update(email=str(args[0]['email']))
        # log
        import cpfecys
        cperiod = cpfecys.current_year_period()
        db.academic_log.insert(user_name='system',
                               roll='system',
                               operation_log='update',
                               before_carnet=args[0]['carnet'],
                               before_email=auth_var.email,
                               after_carnet=args[0]['carnet'],
                               after_email=str(args[0]['email']),
                               id_period=cperiod,
                               description=T('Registration data was update because academic was update'))
    except:
        None


def academic_insert(*args):
    academic_var = db.auth_group(db.auth_group.role == 'Academic')
    user_var = db.auth_user(db.auth_user.username == str(args[0]['carnet']))
    session.flash = T('Academic added.')
    if user_var is None:
        # WEBSERVICE
        web_service = check_student(str(args[0]['carnet']))
        if auth.has_membership('Super-Administrator'):
            id_user = db.auth_user.insert(first_name=str(args[0]['carnet']),
                                          last_name=" ",
                                          email=str(args[0]['email']),
                                          username=str(args[0]['carnet']),
                                          phone='12345678',
                                          home_address=T('Enter your address'))

            # Add the id_auth_user to academic.
            db(db.academic.id == str(args[1]['id'])).update(
                id_auth_user=id_user.id)

            # Create membership to academic
            db.auth_membership.insert(
                user_id=id_user.id, group_id=academic_var.id)

        elif web_service['flag'] == True:
            id_user = db.auth_user.insert(first_name=web_service['nombres'],
                                          last_name=web_service['apellidos'],
                                          email=web_service['correo'],
                                          username=str(args[0]['carnet']),
                                          phone='12345678',
                                          home_address=T('Enter your address'))
            # Add the id_auth_user to academic.
            db(db.academic.id == str(args[1]['id'])).update(
                id_auth_user=id_user.id, email=str(web_service['correo']))
            import cpfecys
            cperiod = cpfecys.current_year_period()
            db.academic_log.insert(user_name='system',
                                   roll='system',
                                   operation_log='update',
                                   after_carnet=str(args[0]['carnet']),
                                   after_email=str(web_service['correo']),
                                   before_carnet=str(args[0]['carnet']),
                                   before_email=str(args[0]['email']),
                                   id_academic=str(args[1]['id']),
                                   id_period=cperiod,
                                   description=T('Registration data was updated, set with the information of the web service'))
            # Create membership to academic
            db.auth_membership.insert(
                user_id=id_user.id, group_id=academic_var.id)
        else:

            if session.academic_update != None:
                if session.assignation_error is None:
                    session.assignation_error = []
                    message = []
                    message.append(str(args[0]['carnet']))
                    message.append(web_service['message'])
                    session.assignation_error.append(message)
                else:
                    message = []
                    message.append(str(args[0]['carnet']))
                    message.append(web_service['message'])
                    session.assignation_error.append(message)
            else:
                session.flash = T(
                    'The user is not registered to the academic cycle')
                db(db.academic.id == args[1]['id']).delete()

                result = db(db.auth_membership.user_id ==
                            auth.user.id).select()
                roll_var = ''
                i = 0
                for a in result:
                    if i == 0:
                        roll_var = a.group_id.role
                        i = i+1
                    else:
                        roll_var = roll_var + ',' + a.group_id.role
                import cpfecys
                currentyear_period = cpfecys.current_year_period()
                session.flash = T(
                    'The record was removed because it failed the webservice validation')
                db.academic_log.insert(user_name=auth.user.username,
                                       roll=str(roll_var),
                                       operation_log='delete',
                                       before_carnet=str(args[0]['carnet']),
                                       before_email=str(args[0]['email']),
                                       id_period=str(currentyear_period.id),
                                       description=T('The record was removed because it failed the webservice validation'))
            pass
        pass

    else:
        membership_var = db.auth_membership((db.auth_membership.user_id == user_var.id) & (
            db.auth_membership.group_id == academic_var.id))
        if membership_var is None:
            # Create membership to academic
            db.auth_membership.insert(
                user_id=user_var.id, group_id=academic_var.id)

        # Add the id_auth_user to academic. And update academic inforamtion
        db(db.academic.id == args[1]['id']).update(id_auth_user=user_var.id,
                                                   email=user_var.email,
                                                   carnet=user_var.username)
        # academic_LOG
        import cpfecys
        cperiod = cpfecys.current_year_period()
        db.academic_log.insert(user_name='system',
                               roll='system',
                               operation_log='update',
                               before_carnet=str(args[0]['carnet']),
                               before_email=str(args[0]['email']),
                               after_carnet=user_var.username,
                               after_email=user_var.email,
                               id_academic=args[1]['id'],
                               id_period=cperiod,
                               description=T('Registration data was updated, set with the information entered by the administrator'))
############################## ACADEMIC TRIGGERS####################################


db.define_table('validate_laboratory',
                Field('carnet', 'reference academic',
                      notnull=True, label=T('Carnet')),
                Field('semester', 'reference period_year',
                      notnull=True, label=T('Period')),
                Field('project', 'reference project',
                      notnull=True, label=T('Course')),
                Field('grade', 'integer', notnull=True, label=T(
                    'Grade'), requires=IS_DECIMAL_IN_RANGE(61, 100)),
                Field('validation_type', 'boolean',
                      notnull=True, label=T('Validation Type'))
                )

db.define_table('validate_laboratory_log',
                Field('user_name', 'string', notnull=False,
                      label=T('User Name Before')),
                Field('roll', 'string', notnull=False, label=T('Role')),
                Field('operation_log', 'string',
                      notnull=False, label=T('Operation')),
                Field('academic_id', 'string', notnull=False,
                      label=T('Academic Assignation Id')),
                Field('academic', 'string', notnull=False, label=T('Academic')),
                Field('project', 'string', notnull=False, label=T('Course')),
                Field('yearp', 'string', notnull=False, label=T('Year')),
                Field('period', 'string', notnull=False, label=T('Period')),
                Field('before_grade', 'integer',
                      notnull=False, label=T('Grade Before')),
                Field('after_grade', 'integer',
                      notnull=False, label=T('Grade After')),
                Field('description', 'text', notnull=False,
                      label=T('Description')),
                Field('id_validate_laboratory', 'text', notnull=False,
                      label=T('id_validate_laboratory')),
                Field('date_log', 'datetime', notnull=True,
                      default=datetime.datetime.now(), label=T('Date')),
                Field('validation_type', 'boolean',
                      notnull=True, label=T('Validation Type'))
                )

db.define_table('course_first_recovery_test',
                Field('carnet', 'reference academic',
                      notnull=True, label=T('Carnet')),
                Field('semester', 'reference period_year',
                      notnull=True, label=T('Period')),
                Field('project', 'reference project',
                      notnull=True, label=T('Course')),
                Field('grade', 'integer', notnull=True, label=T(
                    'Grade'), requires=IS_DECIMAL_IN_RANGE(0, 100))
                )

db.define_table('course_first_recovery_test_log',
                Field('user_name', 'string',
                      notnull=False, label=T('User Name')),
                Field('roll', 'string', notnull=False, label=T('Role')),
                Field('operation_log', 'string',
                      notnull=False, label=T('Operation')),
                Field('academic_id', 'string', notnull=False,
                      label=T('Academic Assignation Id')),
                Field('academic', 'string', notnull=False, label=T('Academic')),
                Field('project', 'string', notnull=False, label=T('Course')),
                Field('yearp', 'string', notnull=False, label=T('Year')),
                Field('period', 'string', notnull=False, label=T('Period')),
                Field('before_grade', 'integer',
                      notnull=False, label=T('Grade Before')),
                Field('after_grade', 'integer',
                      notnull=False, label=T('Grade After')),
                Field('description', 'text', notnull=False,
                      label=T('Description')),
                Field('id_course_first_recovery_test', 'text', notnull=False,
                      label=T('id_course_first_recovery_test')),
                Field('date_log', 'datetime', notnull=True,
                      default=datetime.datetime.now(), label=T('Date'))
                )

db.define_table('course_second_recovery_test',
                Field('carnet', 'reference academic',
                      notnull=True, label=T('Carnet')),
                Field('semester', 'reference period_year',
                      notnull=True, label=T('Period')),
                Field('project', 'reference project',
                      notnull=True, label=T('Course')),
                Field('grade', 'integer', notnull=True, label=T(
                    'Grade'), requires=IS_DECIMAL_IN_RANGE(0, 100))
                )

db.define_table('course_second_recovery_test_log',
                Field('user_name', 'string',
                      notnull=False, label=T('User Name')),
                Field('roll', 'string', notnull=False, label=T('Role')),
                Field('operation_log', 'string',
                      notnull=False, label=T('Operation')),
                Field('academic_id', 'string', notnull=False,
                      label=T('Academic Assignation Id')),
                Field('academic', 'string', notnull=False, label=T('Academic')),
                Field('project', 'string', notnull=False, label=T('Course')),
                Field('yearp', 'string', notnull=False, label=T('Year')),
                Field('period', 'string', notnull=False, label=T('Period')),
                Field('before_grade', 'integer',
                      notnull=False, label=T('Grade Before')),
                Field('after_grade', 'integer',
                      notnull=False, label=T('Grade After')),
                Field('description', 'text', notnull=False,
                      label=T('Description')),
                Field('id_course_second_recovery_test', 'text', notnull=False,
                      label=T('id_course_second_recovery_test')),
                Field('date_log', 'datetime', notnull=True,
                      default=datetime.datetime.now(), label=T('Date'))
                )

db.define_table('course_requirement',
                Field('name', 'string', label=T('name')),
                Field('semester', 'reference period_year',
                      notnull=True, label=T('Period')),
                Field('project', 'reference project',
                      notnull=True, label=T('Course')),
                Field('teacher_permition', 'boolean',
                      notnull=True, label=T('Teacher Permition'))
                )


db.define_table('course_requirement_student',
                Field('carnet', 'reference academic',
                      notnull=True, label=T('Carnet')),
                Field('requirement', 'reference course_requirement',
                      notnull=True, label=T('Requirement'))
                )

db.define_table('course_ended',
                Field('project', 'reference project',
                      notnull=True, label=T('Course')),
                Field('period', 'string', notnull=False, label=T('Period')),
                Field('finish', 'boolean', notnull=True, label=T('Finish'))
                )

db.define_table('validate_student',
                Field('supplier', 'string', notnull=True, label=T('Supplier')),
                Field('action_service', 'string',
                      notnull=True, label=T('Action')),
                Field('type_service', 'string',
                      notnull=True, label=T('Type Service')),
                Field('send', 'string', notnull=True, label=T('Send')),
                Field('receive', 'string', notnull=True, label=T('Receive'))
                )

db.define_table('validate_student_parameters',
                Field('validate_student', 'reference validate_student',
                      notnull=True, label=T('Student Validation Parameters')),
                Field('parameter_name_validate', 'string',
                      notnull=True, label=T('Parameter Name')),
                Field('parameter_value_validate', 'string',
                      notnull=True, label=T('Parameter_Value'))
                )

db.define_table('page_visited',
                Field('user_id', 'integer', notnull=True, label=T('username')),
                Field('page_name', 'string', notnull=True, label=T('Page'))
                )

db.define_table('photo_review',
                Field('user_id', 'integer', notnull=True, label=T('username')),
                Field('photo', 'text', notnull=True, label=T('photo')),
                Field('accepted', 'boolean', notnull=True, label=T('accepted'))
                )

db.define_table('evaluation_type',
                Field('name', 'string', length=255, notnull=True,
                      unique=True, label=T('Name')),
                Field('description', 'text', notnull=True,
                      label=T('Description')),
                Field('user_type_evaluated', 'reference auth_group',
                      notnull=True, label=T('Evaluated')),
                Field('user_type_evaluator', 'reference auth_group',
                      notnull=True, label=T('Evaluator')),
                format='%(name)s'
                )

db.define_table('evaluation_template',
                Field('name', 'string', length=255, notnull=True,
                      unique=True, label=T('Name')),
                Field('date_created', 'date', default=datetime.datetime.now(),
                      notnull=True, label=T('Date created')),
                Field('description', 'text', notnull=True,
                      label=T('Description')),
                Field('evaluation_type', 'reference evaluation_type',
                      notnull=True, label=T('Evaluation type'))
                )

db.define_table('answer_type',
                Field('name', 'string', length=255, notnull=True,
                      unique=True, label=T('Name')),
                Field('exclusive_one_answer', 'boolean',
                      notnull=True, label=T('Exclusive one answer')),
                Field('description', 'text', notnull=True,
                      label=T('Description')),
                format='%(name)s'
                )

db.define_table('answer',
                Field('answer', 'string', length=255,
                      notnull=True, label=T('Answer')),
                Field('grade', 'integer', notnull=True, label=T(
                    'Grade'), requires=IS_DECIMAL_IN_RANGE(0, 100)),
                Field('answer_type', 'reference answer_type',
                      notnull=True, label=T('Answer type'))
                )

db.define_table('evaluation_question',
                Field('question', 'string', length=255, notnull=True,
                      unique=True, label=T('Question')),
                )

db.define_table('question_type',
                Field('name', 'string', length=255, notnull=True,
                      unique=True, label=T('Name')),
                Field('description', 'text', notnull=True,
                      label=T('Description')),
                format='%(name)s'
                )

db.define_table('evaluation_template_detail',
                Field('evaluation_template', 'reference evaluation_template',
                      notnull=True, label=T('Evaluation template')),
                Field('evaluation_question', 'reference evaluation_question',
                      notnull=True, label=T('Evaluation question')),
                Field('obligatory', 'boolean', notnull=True,
                      label=T('Answer is required')),
                Field('answer_type', 'reference answer_type',
                      notnull=True, label=T('Evaluation question')),
                Field('question_type', 'reference question_type',
                      notnull=True, label=T('Question type'))
                )

db.define_table('repository_evaluation',
                Field('name', 'string', length=255, notnull=True,
                      unique=True, label=T('Name')),
                Field('template_name', 'string', length=255,
                      notnull=True, label=T('Template')),
                Field('evaluation_type_name', 'string',
                      notnull=True, label=T('Evaluation Type')),
                Field('date_created', 'date', default=datetime.datetime.now(),
                      notnull=True, label=T('Date created')),
                Field('user_type_evaluated', 'reference auth_group',
                      notnull=True, label=T('Evaluated')),
                Field('user_type_evaluator', 'reference auth_group',
                      notnull=True, label=T('Evaluator')),
                format='%(name)s'
                )

db.define_table('question_repository',
                Field('question', 'string', notnull=True, label=T('Question')),
                Field('obligatory', 'boolean', notnull=True,
                      label=T('Answer is required')),
                Field('question_type_name', 'string',
                      notnull=True, label=T('Question Type')),
                Field('repository_evaluation', 'reference repository_evaluation',
                      notnull=True, label=T('Repository Evaluation')),
                format='%(question)s'
                )

db.define_table('repository_answer',
                Field('answer', 'string', notnull=True, label=T('Answer')),
                Field('grade', 'integer', notnull=True, label=T(
                    'Grade'), requires=IS_DECIMAL_IN_RANGE(0, 100)),
                Field('answer_type_name', 'string',
                      notnull=True, label=T('Answer Type')),
                Field('exclusive_one_answer', 'boolean',
                      notnull=True, label=T('Exclusive one answer')),
                Field('question_repository', 'reference question_repository',
                      notnull=True, label=T('Repository Question')),
                format='%(answer)s'
                )

db.define_table('evaluation',
                Field('date_start', 'date', notnull=True, label=T('Date start')),
                Field('date_finish', 'date', notnull=True,
                      label=T('Date finish')),
                Field('semester_repeat', 'boolean',
                      notnull=True, label=T('Repeat')),
                Field('description', 'text', notnull=False,
                      label=T('Description')),
                Field('period', 'reference period_year',
                      notnull=True, label=T('Period')),
                Field('repository_evaluation', 'reference repository_evaluation',
                      notnull=True, label=T('Repository Evaluation'))
                )

# emarquez: evaluacion para periodos
db.define_table('evaluation_period',
                Field('date_start', 'date', notnull=True, label=T('Date start')),
                Field('date_finish', 'date', notnull=True,
                      label=T('Date finish')),
                Field('period_repeat', 'boolean', notnull=True,
                      label=T('Repetir cada periodo')),
                Field('description', 'text', notnull=False,
                      label=T('Description')),
                Field('period', 'reference period_detail',
                      notnull=True, label=T('Period')),
                Field('repository_evaluation', 'reference repository_evaluation',
                      notnull=True, label=T('Repository Evaluation'))
                )


db.define_table('course_assigned_activity',
                Field('name', 'string', notnull=True,
                      unique=False, label=T('Name')),
                Field('description', 'text', notnull=True,
                      unique=False, label=T('Description')),
                Field('report_required', 'boolean',
                      notnull=True, label=T('Report Required')),
                Field('status', 'string', label=T('Status')),
                Field('automatic_approval', 'boolean',
                      notnull=True, label=T('Automatic Approval')),
                Field('fileReport', 'upload', notnull=False, label='Reporte', requires=[IS_NULL_OR(IS_UPLOAD_FILENAME(
                    extension='(pdf|zip|rar)', error_message='Solo se aceptan archivos con extension zip|pdf|rar')), IS_LENGTH(2097152, error_message='El tamaño máximo del archivo es 2MB')]),
                Field('semester', 'reference period_year', notnull=True),
                Field('assignation', 'reference project', notnull=True),
                Field('date_start', 'date', notnull=True,
                      default=datetime.datetime.now(), label=T('Date'))
                )

db.define_table('evaluation_result',
                Field('repository_evaluation', 'reference repository_evaluation',
                      notnull=True, label=T('Repository Evaluation')),
                Field('evaluated', 'reference auth_user',
                      notnull=True, label=T('Evaluated')),
                Field('period', 'reference period_year',
                      notnull=True, label=T('Period')),
                Field('project', 'reference project',
                      notnull=True, label=T('Project'))
                )

db.define_table('evaluation_auth_user',
                Field('evaluation_result', 'reference evaluation_result',
                      notnull=True, label=T('Evaluation Result')),
                Field('evaluator', 'reference auth_user',
                      notnull=True, label=T('Evaluator'))
                )

db.define_table('evaluation_solve_detail',
                Field('evaluation_result', 'reference evaluation_result',
                      notnull=True, label=T('Evaluation Result')),
                Field('question_repository', 'reference question_repository',
                      notnull=True, label=T('Question Repository')),
                Field('repository_answer', 'reference repository_answer',
                      notnull=True, label=T('Answer Repository')),
                Field('total_count', 'integer', notnull=True, label=T('Count'))
                )

db.define_table('evaluation_solve_text',
                Field('evaluation_result', 'reference evaluation_result',
                      notnull=True, label=T('Evaluation Result')),
                Field('question_repository', 'reference question_repository',
                      notnull=True, label=T('Question Repository')),
                Field('answer', 'text', notnull=True, label=T('Answer'))
                )

db.define_table('course_assigned_activity_log',
                Field('before_name', 'string', notnull=False,
                      label=T('Historical Name')),
                Field('after_name', 'string', notnull=False,
                      label=T('Official Name')),
                Field('before_description', 'text', notnull=False,
                      label=T('Historical Description')),
                Field('after_description', 'text', notnull=False,
                      label=T('Official Description')),
                Field('before_report_required', 'boolean', notnull=False,
                      label=T('Historical Report Required')),
                Field('after_report_required', 'boolean', notnull=False,
                      label=T('Official Report Required')),
                Field('before_status', 'string', notnull=False,
                      label=T('Historical Status')),
                Field('after_status', 'string', notnull=False,
                      label=T('Official Status')),
                Field('before_automatic_approval', 'boolean', notnull=False,
                      label=T('Historical Automatic Approval')),
                Field('after_automatic_approval', 'boolean', notnull=False,
                      label=T('Official Automatic Approval')),
                Field('before_fileReport', 'upload',
                      notnull=False, label=T('Historical Report')),
                Field('after_fileReport', 'upload',
                      notnull=False, label=T('Official Report')),
                Field('before_date_start', 'date',
                      notnull=False, label=T('Historical Date')),
                Field('after_date_start', 'date',
                      notnull=False, label=T('Official Date')),
                Field('id_course_assigned_activity', 'text',
                      notnull=False, label='id_course_assigned_activity'),
                Field('user_name', 'string', notnull=True, label=T('User')),
                Field('roll', 'string', notnull=False, label='Rol'),
                Field('operation_log', 'string',
                      notnull=False, label=T('Operation')),
                Field('description_log', 'text', notnull=True,
                      label=T('Detail of Request')),
                Field('date_log', 'datetime', notnull=True,
                      default=datetime.datetime.now(), label=T('Date Request')),
                Field('project', 'string', notnull=True, label=T('Course')),
                Field('yearp', 'string', notnull=True, label=T('Year')),
                Field('period', 'string', notnull=True, label=T('Period'))
                )

# emarquez: se agrega referencia a periodo
db.define_table('course_report_exception',
                Field('project', 'reference project', notnull=True,
                      unique=True, label=T('Course')),
                Field('period_type', 'reference period_type',
                      notnull=True,  label=T('Tipo Periodo'))
                )

# --------------------------------------------------------------------------------
# CERODAS:
# -----------------------------DSET STUDENT-----------------------------------------

DSstudents = db((db.auth_user.id == db.auth_membership.user_id) & (
    db.auth_membership.group_id == 5)).select(db.auth_user.username, orderby=db.auth_user.username)
ValueStudents = [e.username for e in DSstudents]


# --------------------------------------------------------------------------------
# CERODAS:
# -----------------------------TESIS TABLES-----------------------------------------

# tablas para catalogos del EPS
db.define_table('tesis_status',
                Field('name', 'string', unique=True, notnull=True,
                      required=True, label=T('Name'), length=255),
                Field('description', 'text', notnull=False,
                      required=False, unique=False, label=T('Description')),
                format='%(name)s')

db.define_table('tesis_modality',
                Field('name', 'string', length=255,  notnull=True, required=True, unique=True,
                      label=T('Name')),
                Field('description', 'text', notnull=False,
                      required=False, unique=False, label=T('Description')),
                Field('filenormative', 'upload', notnull=False, required=False, unique=False, label='Adjunto', requires=[IS_NULL_OR(IS_UPLOAD_FILENAME(extension='(pdf|zip|rar|doc|docx)', error_message='Solo se aceptan archivos con extension zip|pdf|rar|doc|docx')), IS_LENGTH(2097152, error_message='El tamaño máximo del archivo es 2MB')]), format='%(name)s')


def recursive_parent(FILA):
    DsParent = db(db.tesis_research_areas.id == FILA['parent_research_area']).select(
        db.tesis_research_areas.ALL).first()
    if (DsParent):
        if (DsParent['parent_research_area']):
            retornocadena = ''
            retornocadena = recursive_parent(
                DsParent) + retornocadena + '[' + str(FILA['name']) + '] '
        else:
            retornocadena = '[' + str(DsParent['name']) + '] ' + \
                '[' + str(FILA['name']) + '] '
    else:
        retornocadena = ""
    return retornocadena


def rsa_represent(parent_research_area, row):
    record = db((db.tesis_research_areas.id == parent_research_area)
                ).select(db.tesis_research_areas.ALL).first()
    if record:
        if (record['parent_research_area']):
            return '%s' % (recursive_parent(record))
            pass
        else:
            return '%s' % ('[' + str(record['name']) + '] ')
        pass
    else:
        return ''


def rsa_format(row):
    if (row):
        if (row['parent_research_area']):
            retorno = recursive_parent(row)
            pass
        else:
            retorno = '[' + str(row['name']) + '] '
        pass
    else:
        retorno = ""
    return retorno


db.define_table('tesis_research_areas',
                Field('parent_research_area', 'reference tesis_research_areas', notnull=False,
                      required=False, ondelete='CASCADE', label=T('Categoria Superior')),
                Field('name', 'string', length=255,  notnull=True,
                      required=True, unique=False, label=T('Name')),
                Field('description', 'text', notnull=False,
                      required=False, unique=False, label=T('Description')),
                Field('file1', 'upload', notnull=False, required=False, unique=False, label=T('Archivo'), requires=[IS_NULL_OR(IS_UPLOAD_FILENAME(
                    extension='(pdf|zip|rar|doc|docx)', error_message='Solo se aceptan archivos con extension zip|pdf|rar|doc|docx')), IS_LENGTH(2097152, error_message='El tamaño máximo del archivo es 2MB')]),
                format=rsa_format
                )
db.tesis_research_areas.parent_research_area.requires = IS_EMPTY_OR(IS_IN_DB(
    db, db.tesis_research_areas.id, db.tesis_research_areas._format, zero=T('<Seleccione>')))
db.tesis_research_areas.parent_research_area.represent = rsa_represent

db.define_table('tesis_tutor',
                Field('firstname', 'string', length=255,  notnull=True,
                      required=True, unique=False, label=T('Nombres')),
                Field('lastname', 'string', length=255,  notnull=False,
                      required=True, unique=False, label=T('Apellidos')),
                Field('Professionalid', 'integer', length=15, notnull=False,
                      required=False, unique=False, label=T('No. de Colegiado')),
                Field('Profession', 'string', length=255, notnull=False,
                      required=False, unique=False, label=T('Profesión')),
                Field('specialty', 'text', notnull=False,  required=False,
                      unique=False, label=T('Especialidad')),
                Field('address', 'text', notnull=False,  required=False,
                      unique=False, label=T('Dirección')),
                Field('phone', 'integer', length=15,  notnull=False,
                      required=False, unique=False, label=T('Phone')),
                Field('email', 'string', length=50,  notnull=False, requires=IS_EMAIL(
                    error_message='El email no es valido'), unique=False, label='Email'),
                Field('cv', 'upload', notnull=False, required=False, unique=False, label='Curriculum vitae', requires=[IS_NULL_OR(IS_UPLOAD_FILENAME(
                    extension='(pdf|zip|rar|doc|docx)', error_message='Solo se aceptan archivos con extension zip|pdf|rar|doc|docx')), IS_LENGTH(2097152, error_message='El tamaño máximo del archivo es 2MB')]),
                Field('file1', 'upload', notnull=False, required=False, unique=False, label='Adjunto', requires=[IS_NULL_OR(IS_UPLOAD_FILENAME(extension='(pdf|zip|rar|doc|docx)', error_message='Solo se aceptan archivos con extension zip|pdf|rar|doc|docx')), IS_LENGTH(2097152, error_message='El tamaño máximo del archivo es 2MB')]), format='%(firstname)s %(lastname)s ')


db.define_table('tesis_adviser',
                Field('firstname', 'string', length=255,  notnull=True,
                      required=True, unique=False, label=T('Nombres')),
                Field('lastname', 'string', length=255,  notnull=False,
                      required=True, unique=False, label=T('Apellidos')),
                Field('Professionalid', 'integer', length=15, notnull=False,
                      required=False, unique=False, label=T('No. de Colegiado')),
                Field('Profession', 'string', length=255, notnull=False,
                      required=False, unique=False, label=T('Profesión')),
                Field('specialty', 'text', notnull=False,  required=False,
                      unique=False, label=T('Especialidad')),
                Field('address', 'text', notnull=False,  required=False,
                      unique=False, label=T('Dirección')),
                Field('phone', 'integer', length=15,  notnull=False,
                      required=False, unique=False, label=T('Phone')),
                Field('email', 'string', length=50,  notnull=False, requires=IS_EMAIL(
                    error_message='El email no es valido'), unique=False, label='Email'),
                Field('cv', 'upload', notnull=False, required=False, unique=False, label='Curriculum vitae', requires=[IS_NULL_OR(IS_UPLOAD_FILENAME(
                    extension='(pdf|zip|rar|doc|docx)', error_message='Solo se aceptan archivos con extension zip|pdf|rar|doc|docx')), IS_LENGTH(2097152, error_message='El tamaño máximo del archivo es 2MB')]),
                Field('file1', 'upload', notnull=False, required=False, unique=False, label='Adjunto', requires=[IS_NULL_OR(IS_UPLOAD_FILENAME(extension='(pdf|zip|rar|doc|docx)', error_message='Solo se aceptan archivos con extension zip|pdf|rar|doc|docx')), IS_LENGTH(2097152, error_message='El tamaño máximo del archivo es 2MB')]), format='%(firstname)s %(lastname)s ')

db.define_table('tesis_asigned_topics',
                Field('student', 'string', length=50,  notnull=True,
                      required=True, unique=False, label=T('Estudiante')),
                Field('tutor', 'reference tesis_tutor', length=100,
                      notnull=False, required=False, unique=False, label=T('Tutor')),
                Field('adviser', 'reference tesis_adviser', length=100,
                      notnull=False, required=False, unique=False, label=T('Asesor')),
                Field('topic_name', 'text', notnull=True,
                      required=True, unique=False, label=T('Tema')),
                Field('topic_modality', 'reference tesis_modality', length=100,
                      notnull=True, required=True, unique=False, label=T('Modalidad')),
                Field('topic_area', 'reference tesis_research_areas', length=255,
                      notnull=True, required=True, unique=False, label=T('Area')),
                Field('topic_description', 'text', notnull=False,
                      required=False, unique=False, label=T('Descripción')),
                Field('topic_protocol', 'upload', notnull=False, required=False, unique=False, label=T('Protocolo'), requires=[IS_NULL_OR(IS_UPLOAD_FILENAME(
                    extension='(pdf|zip|rar|doc|docx)', error_message='Solo se aceptan archivos con extension zip|pdf|rar|doc|docx')), IS_LENGTH(10485760, error_message='El tamaño máximo del archivo es 10MB')]),
                Field('file1', 'upload', notnull=False, required=False, unique=False, label='Adjunto', requires=[IS_NULL_OR(IS_UPLOAD_FILENAME(
                    extension='(pdf|zip|rar|doc|docx)', error_message='Solo se aceptan archivos con extension zip|pdf|rar|doc|docx')), IS_LENGTH(2097152, error_message='El tamaño máximo del archivo es 2MB')]),
                Field('topic_date_approval', 'date', notnull=False,
                      required=False, label=T('Fecha de Aprobación')),
                Field('topic_date_validity', 'date', notnull=False,
                      required=False, label=T('Vigencia')),
                Field('topic_date_reactivation', 'date', notnull=False,
                      required=False, label=T('Fecha de Reactivación')),
                Field('status', 'reference tesis_status',
                      notnull=False, required=True, label=T('Estado')),
                format='%(student)s - %(topic_name)s')

# se agrego el autocomplete para que muestre solo estudiantes
#revisar db.tesis_asigned_topics.student.widget = SQLFORM.widgets.autocomplete(request, db.auth_user.username, db=db((db.auth_user.id == db.auth_membership.user_id) & (db.auth_membership.group_id == 5)), limitby=(0, 5), min_length=4)

#revisar db.tesis_asigned_topics.student.requires = [IS_IN_SET(ValueStudents, error_message='Estudiante no existe en base de datos', zero=None)]


# --------------------------------------------------------------------------------
# CERODAS:
# ---------------------------FIN TESIS TABLES-----------------------------------------

# --------------------------------------------------------------------------------
# CERODAS:
# -----------------------------EPS TABLES-----------------------------------------


# tablas para catalogos del EPS
db.define_table('eps_status',
                Field('name', 'string', unique=True, notnull=True,
                      required=True, label=T('Name'), length=255),
                Field('description', 'text', notnull=False,
                      required=False, unique=False, label=T('Description')),
                format='%(name)s')

db.define_table('eps_period',
                Field('name', 'string', length=255,  notnull=True, required=True, unique=True,
                      label=T('Name')),
                format='%(name)s')

db.define_table('eps_period_year',
                Field('period', 'reference eps_period',
                      notnull=True, required=True, label=T('Ciclo')),
                Field('yearp', 'integer', notnull=True,
                      required=True, label=T('yearp')),
                Field('start_date', 'date', notnull=True,
                      required=True, label=T('start date')),
                Field('end_date', 'date', notnull=True,
                      required=True, label=T('end date')),
                # format = '%(yearp)s - %(period)s'
                format=lambda r: '%s - %s' % (r.yearp,
                                              db.eps_period[r.period].name)
                )

db.define_table('eps_modality',
                Field('name', 'string', length=255,  notnull=True, required=True, unique=True,
                      label=T('Name')),
                Field('description', 'text', notnull=False,
                      required=False, unique=False, label=T('Description')),
                Field('filenormative', 'upload', notnull=False, required=False, unique=False, label='Normativo', requires=[IS_NULL_OR(IS_UPLOAD_FILENAME(extension='(pdf|zip|rar|doc|docx)', error_message='Solo se aceptan archivos con extension zip|pdf|rar|doc|docx')), IS_LENGTH(2097152, error_message='El tamaño máximo del archivo es 2MB')]), format='%(name)s')

db.define_table('eps_activity',
                Field('modality', 'reference eps_modality',
                      notnull=True, required=True, label=T('Modalidad')),
                Field('orden', 'integer', notnull=True,
                      required=True, label=T('Orden')),
                Field('name', 'string', length=255,  notnull=True, required=True, unique=True,
                      label=T('Name')),
                Field('description', 'text', notnull=False,
                      required=False, unique=False, label=T('Description')),
                Field('enable_virtual', 'boolean', notnull=False,
                      label=T('Permite entrega digital')),
                Field('file1', 'upload', notnull=False, required=False, unique=False, label='Archivo 1', requires=[IS_NULL_OR(IS_UPLOAD_FILENAME(
                    extension='(pdf|zip|rar|doc|docx)', error_message='Solo se aceptan archivos con extension zip|pdf|rar|doc|docx')), IS_LENGTH(2097152, error_message='El tamaño máximo del archivo es 2MB')]),
                Field('file2', 'upload', notnull=False, required=False, unique=False, label='Archivo 2', requires=[IS_NULL_OR(IS_UPLOAD_FILENAME(
                    extension='(pdf|zip|rar|doc|docx)', error_message='Solo se aceptan archivos con extension zip|pdf|rar|doc|docx')), IS_LENGTH(2097152, error_message='El tamaño máximo del archivo es 2MB')]),
                Field('file3', 'upload', notnull=False, required=False, unique=False, label='Archivo 3', requires=[IS_NULL_OR(IS_UPLOAD_FILENAME(extension='(pdf|zip|rar|doc|docx)', error_message='Solo se aceptan archivos con extension zip|pdf|rar|doc|docx')), IS_LENGTH(2097152, error_message='El tamaño máximo del archivo es 2MB')]), format='%(name)s')


db.define_table('eps_institution',
                Field('name', 'string', length=255,  notnull=True,
                      required=True, unique=False, label=T('Name')),
                Field('unit', 'string', length=255,  notnull=False,
                      required=False, unique=False, label=T('Unidad')),
                Field('description', 'text', notnull=False,
                      required=False, unique=False, label=T('Description')),
                Field('address', 'text', notnull=False,  required=False,
                      unique=False, label=T('Dirección')),
                Field('phone', 'integer', length=15,  notnull=False,
                      required=False, unique=False, label=T('Phone')),
                Field('email', 'string', length=50,  notnull=False, requires=IS_EMAIL(
                    error_message='El email no es valido'), unique=False, label='Email'),
                Field('owner_name', 'string', length=255,  notnull=True,
                      required=True, unique=False, label=T('Nombre del Responsable')),
                Field('owner_phone', 'integer', length=15,  notnull=False,
                      required=False, unique=False, label=T('Telefono del Responsable')),
                Field('owner_email', 'string', length=50,  notnull=False, requires=IS_EMAIL(
                    error_message='El email no es valido'), unique=False, label=T('Email del Responsable')),
                Field('file1', 'upload', notnull=False, required=False, unique=False, label='Archivo 1', requires=[IS_NULL_OR(IS_UPLOAD_FILENAME(
                    extension='(pdf|zip|rar|doc|docx)', error_message='Solo se aceptan archivos con extension zip|pdf|rar|doc|docx')), IS_LENGTH(2097152, error_message='El tamaño máximo del archivo es 2MB')]),
                Field('file2', 'upload', notnull=False, required=False, unique=False, label='Archivo 2', requires=[IS_NULL_OR(IS_UPLOAD_FILENAME(
                    extension='(pdf|zip|rar|doc|docx)', error_message='Solo se aceptan archivos con extension zip|pdf|rar|doc|docx')), IS_LENGTH(2097152, error_message='El tamaño máximo del archivo es 2MB')]),
                Field('file3', 'upload', notnull=False, required=False, unique=False, label='Archivo 3', requires=[IS_NULL_OR(IS_UPLOAD_FILENAME(extension='(pdf|zip|rar|doc|docx)', error_message='Solo se aceptan archivos con extension zip|pdf|rar|doc|docx')), IS_LENGTH(2097152, error_message='El tamaño máximo del archivo es 2MB')]), format='[%(name)s] %(unit)s ')

# TABLAS DE FUNCIONAMIENTO DE EPS
db.define_table('eps_assignment',
                Field('status', 'reference eps_status', notnull=False,
                      required=True, label=T('Estado')),
                Field('modality', 'reference eps_modality',
                      notnull=False, required=True, label=T('Modalidad')),
                Field('period', 'reference eps_period_year',
                      notnull=False, required=True, label=T('Periodo')),
                Field('student', 'string', length=50,  notnull=True,
                      required=True, unique=False, label=T('Estudiante')),
                Field('project', 'text', notnull=True,  required=True,
                      unique=False, label=T('Proyecto')),
                Field('institution', 'reference eps_institution', notnull=True,
                      required=True, unique=False, label=T('Institución')),
                Field('adviser', 'string', length=255,  notnull=False,
                      required=True, unique=False, label=T('Asesor')),
                Field('supervisor', 'string', length=255,  notnull=False,
                      required=True, unique=False, label=T('Supervisor')),
                format='%(student)s - %(project)s')

# se agrego el autocomplete para que muestre solo estudiantes
#revisar db.eps_assignment.student.widget = SQLFORM.widgets.autocomplete(request, db.auth_user.username, db=db((db.auth_user.id == db.auth_membership.user_id) & (db.auth_membership.group_id == 5)), limitby=(0, 5), min_length=4)

#revisar db.eps_assignment.student.requires = [IS_IN_SET(ValueStudents, error_message='Estudiante no existe en base de datos', zero=None)]

# se agrego el autocomplete para que muestre informacion de institucion
# revisar db.eps_assignment.institution.widget = SQLFORM.widgets.autocomplete(request, db.eps_institution.name, id_field=db.eps_institution.id, limitby=(0,20), min_length=1)

db.define_table('eps_activity_calendar',
                Field('activity', 'reference eps_activity',
                      notnull=True, required=True, label=T('Actividad')),
                Field('period_year', 'reference eps_period_year',
                      notnull=True, required=True, label=T('Periodo')),
                Field('date_assign', 'date', notnull=False,
                      required=True, label=T('Fecha Asignada')),
                format='%(activity)s - %(period_year)s - %(date_assign)s')

# db.eps_activity_calendar.date_assign.represent = lambda v: v.strftime('%d-%m-%Y')
# db.eps_activity_calendar.date_assign.represent = lambda v, r:  datetime.date.today() if v is None else v

db.define_table('eps_files_enable_virtual',
                Field('activity', 'reference eps_activity',
                      notnull=True, required=True, label=T('Actividad')),
                Field('assign', 'reference eps_assignment', notnull=True,
                      required=True, label=T('Asignacion')),
                Field('files', 'upload', notnull=False,
                      required=False, label=T('Archivo'))
                )


db.define_table('eps_tracking_activity',
                Field('activity', 'reference eps_activity',
                      notnull=True, required=True, label=T('Actividad')),
                Field('assign', 'reference eps_assignment', notnull=True,
                      required=True, label=T('Asignacion')),
                Field('validated', 'boolean', notnull=False,
                      required=False, unique=False, label=T('Validado')),
                Field('observations', 'text', notnull=False,
                      required=False, unique=False, label=T('Observaciones'))
                )

db.define_table('eps_tracking',
                Field('activity', 'reference eps_activity',
                      notnull=True, required=True, label=T('Actividad')),
                Field('assign', 'reference eps_assignment',
                      notnull=True, required=True, label=T('Asignacion'))
                )

# ---------------------------------------------------------------------------------
# CERODAS:
# --------------------------FIN EPS TABLES-----------------------------------------

# LTZOC:
# --------------------------TABLAS RECLUTAMIENTO-----------------------------------

# MODULO RECLUTAMIENTO
db.define_table('rec_estado',
                Field('nombre', 'string', notnull=True,
                      label=T('Nombre_Estado'))
                )

db.define_table('rec_proceso',
                Field('anio', 'integer', notnull=True, label=T('Anio')),
                Field('fecha_inicio', 'date', notnull=True,
                      label=T('Fecha_de_inicio')),
                Field('fecha_fin', 'date', notnull=True,
                      label=T('Fecha_de_finalizacion')),
                Field('activo', 'boolean', notnull=True,
                      label=T('Activo'), writable=False),
                Field('periodo', 'reference period', notnull=True,
                      required=True, label=T('PeriodoForanea'))
                )

db.define_table('rec_solicitud',
                Field('id_usuario', 'integer',
                      notnull=True, label=T('IdUsuario')),
                Field('anio', 'integer', notnull=True, label=T('Anio')),
                Field('periodo', 'integer', notnull=True, label=T('Periodo')),
                Field('curriculum', 'upload', uploadfolder=f'{request.folder if "/" in request.folder[len(request.folder) - 1] else request.folder + "/"}static/pdf', notnull=True, unique=False, label='Curriculum', requires=[IS_NULL_OR(IS_UPLOAD_FILENAME(
                    extension='(pdf)', error_message='Solo se aceptan archivos con extension pdf')), IS_LENGTH(2097152, error_message='El tamaño máximo del archivo es 2MB')]),
                Field('listado_cursos', 'upload', uploadfolder=f'{request.folder if "/" in request.folder[len(request.folder) - 1] else request.folder + "/"}static/pdf', notnull=True, unique=False, label='Listado_de_cursos', requires=[IS_NULL_OR(IS_UPLOAD_FILENAME(
                    extension='(pdf)', error_message='Solo se aceptan archivos con extension pdf')), IS_LENGTH(2097152, error_message='El tamaño máximo del archivo es 2MB')]),
                Field('intentos', 'integer', notnull=True, label=T('Intentos')),
                Field('asignado', 'boolean', notnull=True, label=T('Asignado')),
                Field('proceso', 'reference rec_proceso',
                      notnull=True, required=True, label=T('Proceso'))
                )

db.define_table('rec_detalle_solicitud',
                Field('area', 'integer', notnull=True,
                      label=T('Area_Proyecto')),
                Field('id_proyecto', 'string', notnull=True,
                      label=T('Codigo_proyecto')),
                Field('nombre_proyecto', 'string',
                      notnull=True, label=T('Nombre_proyecto')),
                Field('anio_aprobacion', 'integer',
                      notnull=False, label=T('Anio_Aprobacion')),
                Field('semestre_aprobacion', 'integer', notnull=False,
                      label=T('Semestre_De_Aprobacion')),
                Field('nota_aprobacion', 'integer',
                      notnull=False, label=T('Nota_Aprobacion')),
                Field('catedratico', 'string',
                      notnull=False, label=T('Catedratico')),
                Field('nota_oposicion', 'string',
                      notnull=False, label=T('Nota_Oposicion')),
                Field('seccion_proyecto', 'string',
                      notnull=False, label=T('Seccion_Proyecto')),
                Field('periodos', 'integer', notnull=False,
                      label=T('Num_periodos')),
                Field('horas', 'integer', notnull=False, label=T('Nom_horas')),
                Field('estado', 'reference rec_estado',
                      notnull=True, label=T('Solicitud')),
                Field('solicitud', 'reference rec_solicitud',
                      notnull=True, required=True, label=T('Solicitud'))
                )

db.define_table('rec_registro_estado',
                Field('nombre', 'string', notnull=True,
                      label=T('Nombre_Estado'))
                )

db.define_table('rec_registro',
                Field('carnet', 'string', notnull=True, unique=True,
                      label=T('Registro académico'), length=255),
                Field('cui', 'string', length=18,
                      notnull=False, label=T('Cui')),
                Field('nombre', 'string', notnull=True, label=T('Nombre')),
                Field('password', 'string', notnull=False,
                      label=T('Contraseña')),
                Field('apellido', 'string', notnull=True, label=T('Apellido')),
                Field('correo', 'string', notnull=True, requires=IS_EMAIL(
                    error_message='El email no es valido')),
                Field('fotografia', 'upload', uploadfolder=f'{request.folder if "/" in request.folder[len(request.folder) - 1] else request.folder + "/"}static/img_nvo', notnull=True, label=T('Photo'),
                      requires=[IS_IMAGE(extensions=('jpeg', 'png'), maxsize=(200, 300),
                                         error_message=T('Only files are accepted with extension') +
                                         ' png|jpg'+" "+T('with 200x300px size')+".")]),
                Field('estado', 'reference rec_registro_estado',
                      notnull=True, label=T('Solicitud')),
                )

# ------------------------TERMINA TABLAS RECLUTAMIENTO-----------------------------
# ------------------- TABLAS PARA PREGUNTAS FRECUENTAS -----------------------
db.define_table('pf_categoria_p',
                Field('categoria', 'string', notnull=True, label=T('categoria')),
                Field('descripcion', 'text', notnull=False, label=T('descripcion_categoria')), format='%(categoria)s'
                )
db.define_table('pf_pregunta_p',
                Field('pregunta', 'string', notnull=True, label=T('pregunta')),
                Field('respuesta', 'text', notnull=True, label=T('respuesta')),
                Field('categoria', 'reference pf_categoria_p',
                      notnull=True, required=True, label=T('Categoria'))
                )
# --------------- TERMINA TABLAS PARA PREGUNTAS FRECUENTES-------------------

# ---------------------------------------------------------------------------------
# DANIEL COS: MODULO BACKUPS
# ------------------------------------ INICIO -------------------------------------

db.define_table('backup_configuration',
                Field('id', notnull=True),
                Field('fecha_proximo', notnull=False,
                      required=False, label='Fecha de Inicio'),
                Field('tipo', notnull=False, required=False, label='Tipo'),
                Field('estado', notnull=False, required=False, label='Estado'),
                Field('ruta', notnull=False, required=False,
                      label='Ruta en Servidor'),
                Field('cantidad', notnull=False, required=False,
                      label='Copias Almacenadas'),
                Field('servidor', notnull=False,
                      required=False, label='Servidor'),
                Field('puerto', notnull=False, label='Puerto'),
                Field('usuario', notnull=False, label='Usuario'),
                Field('clave', notnull=False, label='Contraseña')
                )

db.define_table('backup_history',
                Field('id', notnull=True),
                Field('fecha', notnull=False, label='Fecha de Creación'),
                Field('tipo', notnull=False, label='Tipo'),
                Field('tipoconf', notnull=False, label='Tipo Configuracion'),
                Field('servidor', notnull=False, label='Servidor'),
                Field('puerto', notnull=False, label='Puerto'),
                Field('usuario', notnull=False, label='Usuario'),
                Field('clave', notnull=False, label='Contraseña'),
                Field('ruta', notnull=False, label='Ruta'),
                Field('nombre', notnull=False, label='Nombre'),
                Field('estado', notnull=False, label='Estado'),
                Field('tamano', notnull=False, label='Tamaño'),
                Field('procesolog', notnull=False, label='Log')
                )

# ---------------------------------------------------------------------------------
# DANIEL COS:
# --------------------------------------- FIN -------------------------------------

# Autor Modulo de quiz: Dayton Garcia
# ----------------TABLAS PARA CONTROL DE QUIZES -----------------------------------
db.define_table('tb_metadata_quiz',
                Field('id_quiz', 'integer', notnull=True, required=True),
                Field('nombre', 'string', notnull=True, required=True),
                Field('fecha_creacion', 'date', notnull=True, required=True),
                Field('creador', 'integer', notnull=True, required=True),
                Field('curso', 'string', notnull=True, required=True)
                )

db.define_table('tb_quiz_actividad',
                Field('id_actividad', 'integer', notnull=True, required=True),
                Field('id_quiz', 'integer', notnull=True, required=True),
                Field('fecha', 'date', notnull=True, required=True),
                Field('inicio', 'time', notnull=True, required=True),
                Field('duracion', 'integer', notnull=True, required=True),
                Field('finalizado', 'integer', notnull=True, required=True),
                Field('private', 'integer', notnull=True, required=True),
                Field('keyword', 'string', notnull=True, required=False)
                )

db.define_table('equivalencia_quiz_category',
                Field('categorie', 'integer', notnull=True,
                      required=True, unique=True),
                Field('description', 'string', notnull=False, required=False)
                )
db.define_table('tb_detalle_respuestas_carnet',
                Field('id', 'integer', notnull=True,
                      required=True, unique=True),
                Field('id_actividad', 'integer', notnull=True, required=True),
                Field('id_estudiante', 'integer', notnull=True, required=True),
                Field('id_pregunta', 'integer', notnull=True, required=True),
                Field('respuesta', 'string', notnull=True, required=True),
                Field('es_correcta', 'integer', notnull=True, required=True)
                )

# --------Defino vista como tabla para facilitar la consulta -------------------
db.define_table('vw_quiz_actividad',
                Field('id'),
                Field('id_actividad'),
                Field('id_quiz'),
                Field('fecha'),
                Field('inicio'),
                Field('duracion'),
                Field('finalizado'),
                Field('private'),
                Field('keyword'),
                Field('nombre_quiz'),
                Field('creacion_quiz'),
                Field('id_creador'),
                Field('id_project'),
                Field('id_curso'),
                Field('nombre_curso'),
                Field('id_programador'),
                Field('nombre_programador'),
                Field('id_categoria'),
                Field('nombre_categoria'),
                Field('actividad_nombre'),
                Field('semestre'),
                Field('hora_actual'),
                Field('fecha_inicio'),
                Field('fecha_fin'),
                Field('Estado_actual'),
                Field('laboratorio')
                )
# -----------------FIN DE CONTROL DE QUIZES ---------------------------------------
# Autor Modulo de quiz: Dayton Garcia


##################################################################################
####################### DANIEL ALVAREZ: MODULO ASISTENCIA ########################
# ------------------------------------ INICIO -------------------------------------

db.define_table('dsi_assistance_type',
                Field('name', 'string', notnull=True,
                      unique=True, label='Nombre'),
                Field('created_at', 'datetime',
                      notnull=True, label='Creado en')
                )

db.define_table('dsi_assistance_class',
                Field('name', 'string', notnull=True,
                      unique=True, label='Nombre'),
                Field('created_at', 'datetime',
                      default=datetime.datetime.now(), label='Creado en')
                )

# System Parameters
db.define_table('dsi_assistance_parameter',
                Field('name', 'string', label="Nombre"),
                Field('parameter_message', 'string', label="Mensage"),
                Field('percentage', 'float', notnull=True, label="Nota"),
                Field('range_start', 'integer', notnull=True,
                      label="Inicio de rango de restricción"),
                Field('range_finish', 'integer', notnull=True,
                      label="Fin de rango de restricción"),
                Field('image', 'string', notnull=False, label="Imagen"),
                Field('period', 'integer', notnull=True, label="Periodo"),
                Field('assistance_class', 'reference dsi_assistance_class',
                      notnull=True, label="Clase"),
                Field('assistance_type', 'reference dsi_assistance_type',
                      notnull=True, label="Tipo"),
                Field('created_at', 'datetime',
                      default=datetime.datetime.now(), label="Hora de cracion"),
                Field('created_by', 'string', notnull=True, label="Creador"),
                Field('updated_at', 'datetime', label="Hora de actualizacion"),
                Field('updated_by', 'string', label="Actualizador")
                )

################################## Justificación ########################################

db.define_table('dsi_justification_status',
                Field('name', 'string', notnull=True,
                      unique=True, label=T('Status')),
                Field('created_at', 'datetime',
                      notnull=True, label=T('Creation date'))
                )

db.define_table('dsi_justification_type',
                Field('name', 'string', notnull=True,
                      unique=True, label=T('Type')),
                Field('created_at', 'datetime',
                      notnull=True, label=T('Creation date'))
                )

db.define_table('dsi_justification',
                Field('description', 'string', notnull=True,
                      length=512, label='Descripción'),
                Field('image', 'upload', notnull=False, label='Documento'),
                Field('resolution_description', 'string',
                      length=255, label='Razón'),
                Field('resolution_date', 'datetime',
                      notnull=False, label='Fecha de resolución'),
                Field('created_at', 'datetime', notnull=False,
                      label='Fecha de creación'),
                Field('created_by', 'string', notnull=True,
                      length=255, label='Creador'),
                Field('updated_at', 'datetime', notnull=False,
                      label='Fecha de actualización'),
                Field('updated_by', 'string', notnull=False,
                      length=255, label='Actualizado por'),
                Field('period', 'integer', notnull=True, label='Periodo'),
                Field('absence_date', 'date', notnull=True,
                      label='Fecha de Falta'),
                Field('contexto', 'string', notnull=False, label='Contexto'),
                Field('justification_type', 'reference dsi_justification_type',
                      notnull=True, label='Tipo'),
                Field('resolution_status', 'reference dsi_justification_status',
                      notnull=True, label='Estado'),
                Field('requester_user', 'reference auth_user',
                      notnull=True, label='Solicitante'),
                Field('project', 'reference user_project',
                      notnull=True, label='Proyecto'),
                Field('resolver_user', 'reference auth_user',
                      notnull=False, label='Revisor'),
                Field('id_asistencia', 'integer',
                      notnull=False, label='Asistencia'),
                Field('schedule_asignation_id', 'integer',
                      notnull=False, label='Horario')
                )

################################## Justificación ########################################
################################## Horario ########################################

db.define_table('dsi_schedule_parameter',
                Field('name', 'string', label="Nombre de parametro"),
                Field('tutor_amount', 'integer', label="Cantidad de tutores"),
                Field('until_date', 'datetime',
                      label="Fecha fin de asignación"),
                Field('asignation_status', 'integer',
                      label="Habilitar asignación"),
                Field('created_at', 'datetime',
                      default=datetime.datetime.now(), label="Hora de cracion"),
                Field('created_by', 'string', notnull=True, label="Creador"),
                Field('updated_at', 'datetime', label="Hora de actualizacion"),
                Field('updated_by', 'string', label="Actualizador")
                )

db.define_table('dsi_schedule',
                Field('starting_hour', 'string'),
                Field('ending_hour', 'string'),
                Field('week_day', 'reference day_of_week'),
                Field('period', 'integer'),
                Field('assistance_type_id', 'reference dsi_assistance_type'),
                Field('created_at', 'datetime'),
                Field('created_by', 'string'),
                Field('updated_at', 'datetime'),
                Field('updated_by', 'string')
                )

db.define_table('dsi_assignation_schedule',
                Field('schedule_id', 'reference dsi_schedule',
                      notnull=True, label='Horario'),
                Field('tutor_id', 'reference auth_user',
                      notnull=True, label='Tutor'),
                Field('classroom', 'string', notnull=False, label='Salon'),
                Field('created_at', 'datetime', notnull=True,
                      label='Hora de creación'),
                Field('created_by', 'string', notnull=True, label='Creado por'),
                Field('updated_at', 'datetime', notnull=False,
                      label='Hora de actualización'),
                Field('updated_by', 'string', notnull=False,
                      label='Actualizado por'),
                Field('isEnabled', 'integer', notnull=False, label='Habilitado'),
                Field('period', 'integer', notnull=True, label='Periodo'),
                Field('project_assignation', 'reference dsi_schedule',
                      notnull=False, label='Proyecto')

                )

################################## Horario ########################################
################################## Desacanso ########################################

db.define_table('dsi_holiday',
                Field('name', 'string', notnull=True),
                Field('enabled', 'integer', notnull=True),
                Field('holiday_date', 'date', notnull=True, label='Fecha'),
                Field('created_at', 'datetime', notnull=True,
                      label='Hora de creación'),
                Field('created_by', 'string', notnull=True, label='Creado por'),
                Field('updated_at', 'datetime', notnull=False,
                      label='Hora de actualización'),
                Field('updated_by', 'string', notnull=False,
                      label='Actualizado por')
                )

################################## Desacanso ########################################
################################## Huella ########################################

db.define_table('dsi_fingerprint_parameter',
                Field('name', 'string', notnull=True),
                Field('parameter_enable', 'integer', notnull=False),
                Field('parameter_date', 'date', notnull=False),
                Field('updated_at', 'datetime', notnull=True,
                      default=datetime.datetime.now()),
                )

db.define_table('dsi_fingerprint',
                Field('tutor_id', 'integer', notnull=True),
                Field('fingerprint', 'string', notnull=True, label='Huella'),
                Field('created_at', 'datetime', notnull=True,
                      label='Hora de creación'),
                Field('created_by', 'string', notnull=True, label='Creado por'),
                Field('updated_at', 'datetime', notnull=False,
                      label='Hora de actualización'),
                Field('updated_by', 'string', notnull=False,
                      label='Actualizado por')
                )

################################## Huella ########################################
################################## Asistencia ########################################

db.define_table('dsi_assistance',
                Field('starting_hour', 'datetime',
                      notnull=True, label='Hora de inicio'),
                Field('finishing_hour', 'datetime',
                      notnull=False, label='Hora de fin'),
                Field('starting_score', 'float', notnull=True,
                      label='Puntuacion de inicio'),
                Field('finishing_score', 'float',
                      notnull=False, label='Puntuacion de fin'),
                Field('score', 'float', notnull=False, label='Nota'),
                Field('schedule', 'reference dsi_schedule',
                      notnull=True, label='Horario'),
                Field('tutor', 'reference auth_user',
                      notnull=True, label='Tutor'),
                Field('justification', 'reference dsi_justification',
                      notnull=False, label='Justificación'),
                Field('period', 'integer', notnull=True, label='Periodo'),
                Field('assistance_type', 'reference dsi_assistance_type',
                      notnull=False, label='Tipo'),
                Field('created_at', 'datetime', notnull=True,
                      label='Hora de creación'),
                Field('created_by', 'integer',
                      notnull=True, label='Creado por'),
                Field('updated_at', 'datetime', notnull=False,
                      label='Hora de actualización'),
                Field('updated_by', 'integer', notnull=False,
                      label='Actualizado por'),
                Field('asignation_id', 'reference user_project',
                      notnull=False, label='Asignación')
                )

################################## Asistencia ########################################

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Deploy 2 $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

################################## Cursos de excepcion ########################################

db.define_table('dsi_exception_course',
                Field('period', 'reference period',
                      notnull=True, label='Periodo'),
                Field('project', 'reference project',
                      notnull=True, label='Proyecto'),
                Field('single_hour', 'integer', notnull=False,
                      label='Asignacion de una hora'),
                Field('evening', 'integer', notnull=False, label='Vespertino'),
                Field('created_at', 'datetime',
                      notnull=True, label='Creado en'),
                Field('created_by', 'string', notnull=True, label='Creado por')
                )

################################## cursos de excepcion ########################################

################################## Horario de Cursos ########################################

db.define_table('dsi_schedule_course',
                Field('project_id', 'reference project',
                      notnull=True, label='Proyecto'),
                Field('day_of_week_id', 'reference day_of_week',
                      notnull=True, label='Día'),
                Field('period', 'reference period',
                      notnull=True, label='Periodo'),
                Field('starting_hour', 'time',
                      notnull=True, label='Hora Inicio'),
                Field('finishing_hour', 'time', notnull=True,
                      label='Hora Finalización'),
                Field('user_id', 'reference auth_user',
                      notnull=True, label='Catedratico'),
                Field('building', 'string', notnull=True, label='Edificio'),
                Field('room', 'string', notnull=True, label='Salón'),
                Field('created_at', 'datetime',
                      notnull=True, label='Creación'),
                Field('updated_at', 'datetime',
                      notnull=True, label='Actualización')
                )

################################## Horario de Cursos ########################################

################################## Parametros del sistema ########################################

db.define_table('dsi_system_parameters',
                Field('name', 'string', notnull=True, label='Nombre'),
                Field('period', 'reference period',
                      notnull=True, label='Periodo'),
                Field('parameter_number', 'integer',
                      notnull=True, label='Parametro Numerico'),
                Field('parameter_date', 'date',
                      notnull=False, label='Parametro Fecha'),
                Field('parameter_bool', 'integer',
                      notnull=False, label='Parametro Bool')
                )
################################## Parametros del sistema ########################################
################################## Notificaciones #########################################

db.define_table('dsi_notification',
                Field('title', 'string', notnull=True, label='Asunto'),
                Field('notification_message', 'string',
                      notnull=True, label='Mensaje'),
                Field('sender', 'integer', notnull=True, label='Emisor'),
                Field('destination', 'integer',
                      notnull=True, label='Destinatario'),
                Field('period', 'integer', notnull=True, label='periodo'),
                Field('created_at', 'datetime',
                      notnull=True, label='Fecha de envio')
                )

db.define_table('dsi_nota',
                Field('period', 'integer', notnull=True, label='Periodo'),
                Field('cantidad', 'integer', notnull=True, label='Cantidad'),
                Field('nota', 'float', notnull=True, label='Nota'),
                Field('nota_final', 'float', notnull=True, label='Nota Final'),
                Field('asignacion', 'integer',
                      notnull=True, label='Asignación'),
                Field('updated_at', 'datetime',
                      notnull=True, label='Actualizado en')
                )

db.define_table('vw_dsi_schedule',
                Field('id', 'integer', label='ID'),
                Field('project_id', 'string', label='ID del proyecto'),
                Field('course_name', 'string', label='Nombre'),
                Field('full_name', 'string', label='Profesor'),
                Field('building', 'string', label='Edificio'),
                Field('room', 'string', label='Salón'),
                Field('week_day', 'string', label='Día'),
                Field('starting_hour', 'time', label='Hora inicio'),
                Field('finishing_hour', 'time', label='Hora Finalización'),
                Field('period', 'integer', label='Periodo'),
                )
################################## Notificaciones #########################################


# --------------------------------------- FIN -------------------------------------
####################### DANIEL ALVAREZ: MODULO ASISTENCIA ########################
##################################################################################

# --------------------ALLOWED CAREERS-------------------------------------------
db.define_table(
    'validate_career',
    Field('unit', 'string', notnull=True, label='U. Academica'),
    Field('extension', 'string', notnull=True, label='Ext.'),
    Field('career_code', 'string', notnull=True, label='Cod. Carrera'),
    Field('career_name', 'string', notnull=True, label='Nombre de la Carrera')
)

# -*- coding: utf-8 -*-
"""
ISO DSI TABLES
"""
db.define_table(
    'iso_tipo_incidente',
    Field('descripcion', 'string', notnull=True, label='descripción'),
    format = '%(descripcion)s'
)

db.define_table(
    'iso_incidente',
    Field('id_project', 'reference project', label="Curso"),
    Field('id_period', 'reference period_year', label="Periódo"),
    Field('id_tipo_incidente', 'reference iso_tipo_incidente', label="Tipo de incidente"),
    Field('fecha_reporte', 'date', notnull=True, label='Fecha del reporte'),
    Field('fecha_creacion', 'date', notnull=False),
    # Field('archivo', 'upload', notnull=False, label="Evidencia(opcional)"),
    Field('email', 'string', notnull=False, label="Correo(opcional)"),
    Field('descripcion', 'text', notnull=True, label='Descripción'),
    Field('id_auth_user', 'reference auth_user', label="Carné estudiante"),
    Field('id_tutor', 'reference auth_user',notnull=False, label="Tutor Académico")
)

db.define_table(
    'iso_tipo_pregunta',
    Field('descripcion', 'string', label='Descripción'),
    format = '%(descripcion)s'
)

db.define_table(
    'iso_utensilio',
    Field('descripcion', 'string', notnull=True, label='Nombre'),
    format = '%(descripcion)s'
)

db.define_table(
    'iso_prestamo',
    Field('fecha_prestamo', 'datetime', notnull=True, label='Fecha prestamo'),
    Field('fecha_devolucion', 'datetime', notnull=True, label = 'Fecha devolucion'),
    Field('fecha_est_dev', 'datetime', notnull=False, label= 'Fecha estimada devolucion'),
    Field('id_utensilio', 'reference iso_utensilio', label="Utensilio"),
    Field('id_periodo', 'reference period_year', label= "Periodo"),
    Field('id_estudiante', 'reference auth_user', label= "Carne estudiante"),
    Field('id_encargado_dsi', 'reference auth_user', label="Carne encargado DSI")
)

db.define_table(
    'iso_ev_rendimiento',
    Field('fecha_inicio', 'datetime', label="Fecha de inicio"),
    Field('fecha_fin', 'datetime', label="Fecha de finalización"),
    Field('nombre', 'string', label="Nombre de la Evaluación"),
    Field('id_period_year', 'reference period_year', label='Semestre')
)

db.define_table(
    'iso_pregunta',
    Field('descripcion', 'string', label="Descripción"),
    Field('valor', 'double',notnull=True, label="valor"),
    Field('iso_tipo_pregunta_id', 'reference iso_tipo_pregunta', label="Tipo de Pregunta"),
    Field('id_ev_rendimiento', 'reference iso_ev_rendimiento', label="Evaluacion")
)

db.define_table(
    'iso_pregunta_seleccion',
    Field('descripcion', 'string', label="Respuesta"),
    Field('punteo', 'double', label="Punteo"),
    Field('iso_pregunta_id', 'reference iso_pregunta'),
)

db.define_table(
    'iso_evr_curso',
    Field('mostrar', 'boolean', label="Mostrar Resultados"),
    Field('iso_encuesta_id', 'reference iso_ev_rendimiento', label="Evaluación de rendimiento"),
    Field('user_project_id', 'reference user_project', label ="Curso")
)

db.define_table(
    'iso_respuesta_estudiante',
    Field('id_pregunta', 'reference iso_pregunta', label="Pregunta"),
    Field('id_auth_user', 'reference auth_user', label="Estudiante"),
    Field('id_evr_curso', 'reference iso_evr_curso', label="Evaluación de rendimiento")
)

db.define_table(
    'iso_evr_pregunta',
    Field('id_pregunta', 'reference iso_pregunta', label="Pregunta"),
    Field('id_evr', 'reference iso_ev_rendimiento', label="Evaluación de rendimiento")
)

db.define_table(
    'iso_respuesta',
    Field('valor', 'double', notnull=True, label="Valor"),
    Field('respuesta', 'string', notnull=False, label="Respuesta"),
    Field('iso_encuesta_curso_id', 'reference iso_evr_curso', label="Curso"),
    Field('iso_pregunta_id', 'reference iso_pregunta', "pregunta"),
    Field('iso_pregunta_seleccion_id', 'reference iso_pregunta_seleccion', 'id_respuesta')
)


db.define_table('iso_resultado_evr',
    Field('name', 'string', label='Curso'),
    Field('username', 'string', label='Registro Académico'),
    Field('first_name', 'string', label='Nombres'),
    Field('last_name', 'string', label='Apellidos'),
    Field('iso_encuesta_id', 'integer', label='Encuesta'),
    Field('puntos', 'double', label='Puntos'),
    Field('id_evr', 'integer', label='Id Evaluación')
    )

db.define_table('iso_vw_incidentes',
    Field('carnet', 'string', label='Registro Académico'),
    Field('first_name', 'string', label='Nombres'),
    Field('last_name', 'string', label='Apellidos'),
    Field('curso', 'string'),
    Field('incidentes', 'integer'),
    Field('id_period_year', 'integer'),
    Field('yearp', 'integer', label='Año'),
    Field('name', 'string', label='Semestre'),
    Field('id_tutor','integer'),
    Field('project_id','integer'))

# --------------------------- tablas cascarus --------------------------------#
db.define_table('foro',
    Field('id_proyecto', 'reference project'),
    Field('id_estudiante', 'reference auth_user' ),
    Field('id_dsi', 'reference auth_user'),
    Field('nombre_foro', 'string'),
    Field('reporte', 'string'),
    Field('nota', 'decimal(5,2)'),
    Field('estado', 'string'),
    Field('fecha_creacion', 'datetime'),
    Field('fecha_calificacion', 'datetime'),
    Field('observaciones', 'string'))

db.define_table('conferencia',
    Field('id_proyecto', 'reference project'),
    Field('id_estudiante', 'reference auth_user' ),
    Field('id_dsi', 'reference auth_user'),
    Field('nombre_video', 'string'),
    Field('reporte', 'string'),
    Field('video', 'string'),
    Field('nota', 'decimal(5,2)'),
    Field('estado', 'string'),
    Field('fecha_creacion', 'datetime'),
    Field('fecha_calificacion', 'datetime'),
    Field('observaciones', 'string'),
    Field('descripcion', 'string'))

# ------------------------END---------------------------------------------------
# after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
# automatic forcing spanish language
T.force('es')