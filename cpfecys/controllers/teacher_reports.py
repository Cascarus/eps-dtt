import cpfecys
from datetime import datetime
import queries_teacher_reports as qtr

@auth.requires_login()
@auth.requires(auth.has_membership('Teacher'))
def grades_management():
    period = cpfecys.current_year_period()
    info_level = []
    personal_query = ''
    make_redirect = False
    project = None
    month = None
    roll = None
    user_p = None
    grid = None
    if request.vars['query_search'] is not None and request.vars['query_search'] != "":
        #PERSONALIZED QUERY SURE WORK
        try:
            personal_query = int(request.vars['query_search'])
            db(db.grades_log.academic == personal_query).count()
            if request.vars['search_t'] is not None and request.vars['search_t'] == 'T':
                make_redirect = True
        except:
            response.flash = T('The query is not valid. The report is displayed without applying any query.')
            personal_query = ''
    if make_redirect:
        redirect(URL('teacher_reports', 'grades_management', vars=dict(
                                                                level=5,
                                                                project=request.vars['project'],
                                                                month=request.vars['month'],
                                                                roll=request.vars['roll'],
                                                                user_p=request.vars['user_p'],
                                                                type_l=request.vars['type_l'],
                                                                type_u=request.vars['type_u'],
                                                                query_search=request.vars['query_search']
                                                            )
                ))

    try:
        #CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars['level'] is not None and (int(request.vars['level']) < 1 or int(request.vars['level']) > 5):
            session.flash = T('Not valid Action.')
            redirect(URL('default','index'))
        
        #VERIFY THAT THE PARAMETERS OF EACH LEVEL BE VALID
        if request.vars['level'] is not None:
            #LEVEL MORE THAN 1
            if int(request.vars['level']) > 1:
                #CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars['type_l'] is None or (request.vars['type_l'] != "all" and request.vars['type_l'] != "i" and request.vars['type_l'] != "u" and request.vars['type_l'] != "d"):
                    session.flash = T('Not valid Action.')
                    redirect(URL('default','index'))

                #CHECK IF THE PROJECT IS VALID
                project = validate_project(request.vars['project'], 'grades_log')
                if project is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default','index'))
            
            #LEVEL MORE THAN 2
            if int(request.vars['level']) > 2:
                #CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars['type_u'] is None or (request.vars['type_u'] != "all" and request.vars['type_u'] != "i" and request.vars['type_u'] != "u" and request.vars['type_u'] != "d"):
                    session.flash = T('Not valid Action.')
                    redirect(URL('default','index'))

                #CHECK IF THE MONTH IS VALID
                month = validate_month(request.vars['month'])
                if month is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default','index'))

                #OBTAIN ROLES
                roles = get_roles('grades_log')
            
            #LEVEL MORE THAN 4
            if int(request.vars['level']) > 3:
                #CHECK IF THE ROLE IS VALID
                roll = validate_rol(request.vars['roll'], 'grades_log')
                if roll is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'index'))
                #OBTAIN USERS
                users_project = get_users(project, roll, 'grades_log')

            #LEVEL MORE THAN 5
            if int(request.vars['level']) > 4:
                #CHECK IF THE USER IS VALID
                user_p = validate_user(project, roll, request.vars['user_p'], 'grades_log')
                if user_p is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default','index'))
    except:
        session.flash = T('Not valid Action.')
        redirect(URL('default','index'))

    #LEVELS OF REPORT
    #ALL SEMESTERS
    if request.vars['level'] == '1' or request.vars['level'] is None:
        projects = db((db.user_project.assigned_user == auth.user.id) & ((db.user_project.period <= period.id)
                    & ((db.user_project.period.cast('integer') + db.user_project.periods) > period.id))).select(db.user_project.project)
        if projects.first() is None:
            session.flash = T('Report no visible: There are no parameters required to display the report.')
            redirect(URL('activity_control', 'courses_list'))

        for project in projects:
            infoe_level_temp = []
            #ID OF PERIOD
            infoe_level_temp.append(project.project.id)
            #NAME OF PERIOD
            infoe_level_temp.append(project.project.name)
            #COUNTS
            query_count = db.executesql(qtr.level_1_grades_management(T(period.period.name), period.yearp, project.project.name, f'%{personal_query}%'), as_dict=True)[0]
            infoe_level_temp.append(0 if query_count['insert_count'] is None else query_count['insert_count'])
            infoe_level_temp.append(0 if query_count['update_count'] is None else query_count['update_count'])
            infoe_level_temp.append(0 if query_count['delete_count'] is None else query_count['delete_count'])
            #INSERT PROJECT
            info_level.append(infoe_level_temp)
    #PER MONTH
    elif request.vars['level'] == "2":
        for month in get_month_period():
            start = str(datetime.strptime(f'{period.yearp}-{month[0]}-01', "%Y-%m-%d"))
            if month[2] == 1:
                end = str(datetime.strptime(f'{period.yearp + 1}-{month[2]}-01', "%Y-%m-%d"))
            else:
                end = str(datetime.strptime(f'{period.yearp}-{month[2]}-01', "%Y-%m-%d"))
            
            infoe_level_temp = []
            #ID OF MONTH
            infoe_level_temp.append(month[0])
            #NAME OF MONTH
            infoe_level_temp.append(f'{month[1]} {period.yearp}')
            #COUNTS
            query_count = db.executesql(qtr.level_2_grades_management(T(period.period.name), period.yearp, project.name, start, end, f'%{personal_query}%'), as_dict=True)[0]
            if request.vars['type_l'] == "all" or request.vars['type_l'] == "i":
                infoe_level_temp.append(0 if query_count['insert_count'] is None else query_count['insert_count'])
            if request.vars['type_l'] == "all" or request.vars['type_l'] == "u":
                infoe_level_temp.append(0 if query_count['update_count'] is None else query_count['update_count'])
            if request.vars['type_l'] == "all" or request.vars['type_l'] == "d":
                infoe_level_temp.append(0 if query_count['delete_count'] is None else query_count['delete_count'])
            #INSERT MONTH
            info_level.append(infoe_level_temp)
    #PER ROL
    elif request.vars['level'] == "3":
        if len(roles) == 0:
            session.flash = T('Report no visible: There are no parameters required to display the report.')
            redirect(URL('teacher_reports', 'grades_management', vars=dict(level='2', type_l=request.vars['type_u'], query_search=personal_query)))

        for roll_t in roles:
            infoe_level_temp = []
            #ID OF ROLE
            infoe_level_temp.append(roll_t)
            #NAME OF ROLE
            infoe_level_temp.append(T(f'Rol {roll_t}'))
            #COUNTS
            query_count = db.executesql(qtr.level_3_grades_management(T(period.period.name), period.yearp, project.name, str(month[1]), str(month[2]), f'%{personal_query}%', roll_t), as_dict=True)[0]
            if request.vars['type_l'] == "all" or request.vars['type_l'] == "i":
                infoe_level_temp.append(0 if query_count['insert_count'] is None else query_count['insert_count'])
            if request.vars['type_l'] == "all" or request.vars['type_l'] == "u":
                infoe_level_temp.append(0 if query_count['update_count'] is None else query_count['update_count'])
            if request.vars['type_l'] == "all" or request.vars['type_l'] == "d":
                infoe_level_temp.append(0 if query_count['delete_count'] is None else query_count['delete_count'])
            #INSERT ROLL
            info_level.append(infoe_level_temp)
    #PER USER
    elif request.vars['level'] == "4":
        if len(users_project) == 0:
            session.flash = T('Report no visible: There are no parameters required to display the report.')
            redirect(URL('teacher_reports', 'grades_management', vars=dict(level='3', month=request.vars['month'], type_l=request.vars['type_u'], type_u=request.vars['type_u'], query_search=personal_query)))

        for user_pt in users_project:
            infoe_level_temp = []
            #ID OF USER
            infoe_level_temp.append(user_pt)
            #COUNTS
            query_count = db.executesql(qtr.level_4_grades_management(T(period.period.name), period.yearp, project.name, str(month[1]), str(month[2]), f'%{personal_query}%', str(roll), user_pt), as_dict=True)[0]
            if request.vars['type_l'] == "all" or request.vars['type_l'] == "i":
                infoe_level_temp.append(0 if query_count['insert_count'] is None else query_count['insert_count'])
            if request.vars['type_l'] == "all" or request.vars['type_l'] == "u":
                infoe_level_temp.append(0 if query_count['update_count'] is None else query_count['update_count'])
            if request.vars['type_l'] == "all" or request.vars['type_l'] == "d":
                infoe_level_temp.append(0 if query_count['delete_count'] is None else query_count['delete_count'])
            #INSERT USER
            info_level.append(infoe_level_temp)
    #DATA
    elif request.vars['level'] == "5":
        #COUNTS
        if personal_query == '':
            if request.vars['type_l'] == "all":
                all_data = db((db.grades_log.period == T(period.period.name)) & (db.grades_log.yearp == period.yearp)
                            & (db.grades_log.project == project.name) & (db.grades_log.date_log >= str(month[1]))
                            & (db.grades_log.date_log < str(month[2])) & (db.grades_log.roll == str(roll))
                            & (db.grades_log.user_name == str(user_p))).select(db.grades_log.id)
            elif request.vars['type_l'] == "i":
                all_data = db((db.grades_log.period == T(period.period.name)) & (db.grades_log.yearp == period.yearp)
                            & (db.grades_log.project == project.name) & (db.grades_log.date_log >= str(month[1]))
                            & (db.grades_log.date_log < str(month[2])) & (db.grades_log.roll == str(roll))
                            & (db.grades_log.user_name == str(user_p)) & (db.grades_log.operation_log == 'insert')).select(db.grades_log.id)
            elif request.vars['type_l'] == "u":
                all_data = db((db.grades_log.period == T(period.period.name)) & (db.grades_log.yearp == period.yearp)
                            & (db.grades_log.project == project.name) & (db.grades_log.date_log >= str(month[1]))
                            & (db.grades_log.date_log < str(month[2])) & (db.grades_log.roll == str(roll))
                            & (db.grades_log.user_name == str(user_p)) & (db.grades_log.operation_log == 'update')).select(db.grades_log.id)
            elif request.vars['type_l'] == "d":
                all_data = db((db.grades_log.period == T(period.period.name)) & (db.grades_log.yearp == period.yearp)
                            & (db.grades_log.project == project.name) & (db.grades_log.date_log >= str(month[1]))
                            & (db.grades_log.date_log < str(month[2])) & (db.grades_log.roll == str(roll))
                            & (db.grades_log.user_name == str(user_p)) & (db.grades_log.operation_log == 'delete')).select(db.grades_log.id)
        else:
            if request.vars['type_l'] == "all":
                all_data = db((db.grades_log.period == T(period.period.name)) & (db.grades_log.yearp == period.yearp)
                            & (db.grades_log.project == project.name) & (db.grades_log.date_log >= str(month[1]))
                            & (db.grades_log.date_log < str(month[2])) & (db.grades_log.roll == str(roll))
                            & (db.grades_log.user_name == str(user_p)) & (db.grades_log.academic.like(f'%{personal_query}%'))).select(db.grades_log.id)
            elif request.vars['type_l'] == "i":
                all_data = db((db.grades_log.period == T(period.period.name)) & (db.grades_log.yearp == period.yearp)
                            & (db.grades_log.project == project.name) & (db.grades_log.date_log >= str(month[1]))
                            & (db.grades_log.date_log < str(month[2])) & (db.grades_log.roll == str(roll))
                            & (db.grades_log.user_name == str(user_p)) & (db.grades_log.operation_log == 'insert')
                            & (db.grades_log.academic.like(f'%{personal_query}%'))).select(db.grades_log.id)
            elif request.vars['type_l'] == "u":
                all_data = db((db.grades_log.period == T(period.period.name)) & (db.grades_log.yearp == period.yearp)
                            & (db.grades_log.project == project.name) & (db.grades_log.date_log >= str(month[1]))
                            & (db.grades_log.date_log < str(month[2])) & (db.grades_log.roll == str(roll))
                            & (db.grades_log.user_name == str(user_p)) & (db.grades_log.operation_log == 'update')
                            & (db.grades_log.academic.like(f'%{personal_query}%'))).select(db.grades_log.id)
            elif request.vars['type_l'] == "d":
                all_data = db((db.grades_log.period == T(period.period.name)) & (db.grades_log.yearp == period.yearp)
                            & (db.grades_log.project == project.name) & (db.grades_log.date_log >= str(month[1]))
                            & (db.grades_log.date_log < str(month[2])) & (db.grades_log.roll == str(roll))
                            & (db.grades_log.user_name == str(user_p)) & (db.grades_log.operation_log == 'delete')
                            & (db.grades_log.academic.like(f'%{personal_query}%'))).select(db.grades_log.id)
        grid = []
        for data in all_data:
                grid.append(data.id)
        if len(grid) == 0:
            grid.append(-1)
        #GRID
        db.grades_log.id.readable = False
        db.grades_log.id.writable = False
        db.grades_log.user_name.readable = False
        db.grades_log.user_name.writable = False
        db.grades_log.roll.readable = False
        db.grades_log.roll.writable = False
        db.grades_log.academic_assignation_id.readable = False
        db.grades_log.academic_assignation_id.writable = False
        db.grades_log.activity_id.readable = False
        db.grades_log.activity_id.writable = False
        db.grades_log.project.readable = False
        db.grades_log.project.writable = False
        db.grades_log.yearp.readable = False
        db.grades_log.yearp.writable = False
        db.grades_log.period.readable = False
        db.grades_log.period.writable = False
        grid = SQLFORM.grid(db.grades_log.id.belongs(grid), csv=False, create=False, editable=False, deletable=False, paginate=9, searchable=False)
    return dict(personal_query=personal_query, info_level=info_level, period=period, project=project, month=month, roll=roll, user_p=user_p, grid=grid)

@auth.requires_login()
@auth.requires(auth.has_membership('Teacher'))
def grades_management_export():
    period = cpfecys.current_year_period()
    info_level = []
    personal_query = ''
    if request.vars['query_search'] is not None and request.vars['query_search'] != "":
        #PERSONALIZED QUERY SURE WORK
        try:
            personal_query = int(request.vars['query_search'])
            db(db.grades_log.academic == personal_query).count()
        except:
            personal_query = ''

    try:
        #CHECK IF THE TYPE OF EXPORT IS VALID
        if request.vars['list_type'] is None or request.vars['list_type'] != "csv":
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'index'))

        #CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars['level'] is not None and (int(request.vars['level']) < 1 or int(request.vars['level']) > 5):
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'index'))
        
        #VERIFY THAT THE PARAMETERS OF EACH LEVEL BE VALID
        if request.vars['level'] is not None:
            #LEVEL MORE THAN 1
            if int(request.vars['level']) > 1:
                #CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars['type_l'] is None or (request.vars['type_l'] != "all" and request.vars['type_l'] != "i" and request.vars['type_l'] != "u" and request.vars['type_l'] != "d"):
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'index'))

                #CHECK IF THE PROJECT IS VALID
                project = validate_project(request.vars['project'], 'grades_log')
                if project is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'index'))
            
            #LEVEL MORE THAN 2
            if int(request.vars['level']) > 2:
                #CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars['type_u'] is None or (request.vars['type_u'] != "all" and request.vars['type_u'] != "i" and request.vars['type_u'] != "u" and request.vars['type_u'] != "d"):
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'index'))

                #CHECK IF THE MONTH IS VALID
                month = validate_month(request.vars['month'])
                if month is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'index'))
                #OBTAIN ROLES
                roles = get_roles('grades_log')
            
            #LEVEL MORE THAN 4
            if int(request.vars['level']) > 3:
                #CHECK IF THE ROLE IS VALID
                roll = validate_rol(request.vars['roll'], 'grades_log')
                if roll is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'index'))
                #OBTAIN USERS
                users_project = get_users(project, roll, 'grades_log')

            #LEVEL MORE THAN 5
            if int(request.vars['level']) > 4:
                #CHECK IF THE USER IS VALID
                user_p = validate_user(project, roll, request.vars['user_p'], 'grades_log')
                if user_p is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'index'))
    except:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'index'))
    
    #TITLE
    info_level = []
    info_level.append(['Universidad de San Carlos de Guatemala'])
    info_level.append(['Facultad de Ingeniería'])
    info_level.append(['Escuela de Ingeniería en Ciencias y Sistemas'])
    info_level.append([])
    #TYPE OF REPORT
    info_level.append(['Tipo', 'Gestión de notas'])
    #DESCRIPTION OF REPORT
    info_level.append(['Descripción', 'Reporte de las operaciones de gestión de notas'])
    #PERIOD OF REPORT
    info_level.append(['Periodo', f'{T(period.period.name)} {period.yearp}'])
    #ALL SEMESTERS
    if request.vars['level'] == '1' or request.vars['level'] is None:
        #MIDDLE LINE OF REPORT
        info_level.append([])
        #LABLE DETAIL OF REPORT
        info_level.append(['Detalle'])
        #LABELS OF DATA OF REPORT
        info_level.append(['Curso', 'Total inserciones', 'Total actualizaciones', 'Total eliminados'])
        for project in db((db.user_project.assigned_user == auth.user.id) & ((db.user_project.period <= period.id) 
                        & ((db.user_project.period.cast('integer') + db.user_project.periods) > period.id))).select(db.user_project.project):
            infoe_level_temp = []
            #NAME OF PERIOD
            infoe_level_temp.append(project.project.name)
            #COUNTS
            query_count = db.executesql(qtr.level_1_grades_management(T(period.period.name), period.yearp, project.project.name, f'%{personal_query}%'), as_dict=True)[0]
            infoe_level_temp.append(0 if query_count['insert_count'] is None else query_count['insert_count'])
            infoe_level_temp.append(0 if query_count['update_count'] is None else query_count['update_count'])
            infoe_level_temp.append(0 if query_count['delete_count'] is None else query_count['delete_count'])
            #INSERT PROJECT
            info_level.append(infoe_level_temp)
    #PER MONTH
    elif request.vars['level'] == "2":
        #PROJECT OF REPORT
        info_level.append(['Curso', project.name])
        #MIDDLE LINE OF REPORT
        info_level.append([])
        #LABLE DETAIL OF REPORT
        info_level.append(['Detalle'])

        #LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append('Mes')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "i":
            infoe_level_temp.append('Total inserciones')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "u":
            infoe_level_temp.append('Total actualizaciones')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "d":
            infoe_level_temp.append('Total eliminadoos')
        info_level.append(infoe_level_temp)

        for month in get_month_period():
            start = str(datetime.strptime(f'{period.yearp}-{month[0]}-01', "%Y-%m-%d"))
            if month[2] == 1:
                end = str(datetime.strptime(f'{period.yearp + 1}-{month[2]}-01', "%Y-%m-%d"))
            else:
                end = str(datetime.strptime(f'{period.yearp}-{month[2]}-01', "%Y-%m-%d"))
            
            infoe_level_temp = []
            #NAME OF MONTH
            infoe_level_temp.append(f'{month[1]} {period.yearp}')
            #COUNTS
            query_count = db.executesql(qtr.level_2_grades_management(T(period.period.name), period.yearp, project.name, start, end, f'%{personal_query}%'), as_dict=True)[0]
            if request.vars['type_l'] == "all" or request.vars['type_l'] == "i":
                infoe_level_temp.append(0 if query_count['insert_count'] is None else query_count['insert_count'])
            if request.vars['type_l'] == "all" or request.vars['type_l'] == "u":
                infoe_level_temp.append(0 if query_count['update_count'] is None else query_count['update_count'])
            if request.vars['type_l'] == "all" or request.vars['type_l'] == "d":
                infoe_level_temp.append(0 if query_count['delete_count'] is None else query_count['delete_count'])
            #INSERT MONTH
            info_level.append(infoe_level_temp)
    #PER ROL
    elif request.vars['level'] == "3":
        #PROJECT OF REPORT
        info_level.append(['Curso', project.name])
        #MONTH OF REPORT
        info_level.append(['Mes', month[0]])
        #MIDDLE LINE OF REPORT
        info_level.append([])
        #LABLE DETAIL OF REPORT
        info_level.append(['Detalle'])
        #LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append('Mes')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "i":
            infoe_level_temp.append('Total inserciones')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "u":
            infoe_level_temp.append('Total actualizaciones')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "d":
            infoe_level_temp.append('Total eliminados')
        info_level.append(infoe_level_temp)

        for roll_t in roles:
            infoe_level_temp = []
            #NAME OF ROLE
            infoe_level_temp.append(T(f'Rol {roll_t}'))
            #COUNTS
            query_count = db.executesql(qtr.level_3_grades_management(T(period.period.name), period.yearp, project.name, str(month[1]), str(month[2]), f'%{personal_query}%', roll_t), as_dict=True)[0]
            if request.vars['type_l'] == "all" or request.vars['type_l'] == "i":
                infoe_level_temp.append(0 if query_count['insert_count'] is None else query_count['insert_count'])
            if request.vars['type_l'] == "all" or request.vars['type_l'] == "u":
                infoe_level_temp.append(0 if query_count['update_count'] is None else query_count['update_count'])
            if request.vars['type_l'] == "all" or request.vars['type_l'] == "d":
                infoe_level_temp.append(0 if query_count['delete_count'] is None else query_count['delete_count'])
            #INSERT ROLL
            info_level.append(infoe_level_temp)
    #PER USER
    elif request.vars['level'] == "4":
        #PROJECT OF REPORT
        info_level.append(['Curso', project.name])
        #MONTH OF REPORT
        info_level.append(['Mes', month[0]])
        #ROLE OF REPORT
        info_level.append(['Rol', T(f'Rol {roll}')])
        #MIDDLE LINE OF REPORT
        info_level.append([])
        #LABLE DETAIL OF REPORT
        info_level.append(['Detalle'])
        #LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append('Usuario')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "i":
            infoe_level_temp.append('Total inserciones')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "u":
            infoe_level_temp.append('Total actualizaciones')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "d":
            infoe_level_temp.append('Total eliminados')
        info_level.append(infoe_level_temp)

        for user_pt in users_project:
            infoe_level_temp = []
            #NAME OF USER
            infoe_level_temp.append(user_pt)
            #COUNTS
            query_count = db.executesql(qtr.level_4_grades_management(T(period.period.name), period.yearp, project.name, str(month[1]), str(month[2]), f'%{personal_query}%', str(roll), user_pt), as_dict=True)[0]
            if request.vars['type_l'] == "all" or request.vars['type_l'] == "i":
                infoe_level_temp.append(0 if query_count['insert_count'] is None else query_count['insert_count'])
            if request.vars['type_l'] == "all" or request.vars['type_l'] == "u":
                infoe_level_temp.append(0 if query_count['update_count'] is None else query_count['update_count'])
            if request.vars['type_l'] == "all" or request.vars['type_l'] == "d":
                infoe_level_temp.append(0 if query_count['delete_count'] is None else query_count['delete_count'])
            #INSERT USER
            info_level.append(infoe_level_temp)
    #DATA
    elif request.vars['level'] == "5":
        #PROJECT OF REPORT
        info_level.append(['Curso', project.name])
        #MONTH OF REPORT
        info_level.append(['Mes', month[0]])
        #ROLE OF REPORT
        info_level.append(['Rol', T(f'Rol {roll}')])
        #ROLE OF REPORT
        info_level.append(['Usuario', user_p])
        #MIDDLE LINE OF REPORT
        info_level.append([])
        #LABLE DETAIL OF REPORT
        info_level.append(['Detalle'])
        #COUNTS
        month_1 = str(month[1])
        month_2 = str(month[2])
        if personal_query == '':
            if request.vars['type_l'] == "all":
                all_data = db((db.grades_log.period == T(period.period.name)) & (db.grades_log.yearp == period.yearp)
                            & (db.grades_log.project == project.name) & (db.grades_log.date_log >= month_1)
                            & (db.grades_log.date_log < month_2) & (db.grades_log.roll == roll)
                            & (db.grades_log.user_name == user_p)).select(
                                db.grades_log.operation_log,
                                db.grades_log.academic,
                                db.grades_log.activity,
                                db.grades_log.category,
                                db.grades_log.before_grade,
                                db.grades_log.after_grade,
                                db.grades_log.date_log,
                                db.grades_log.description
                            )
            elif request.vars['type_l'] == "i":
                all_data = db((db.grades_log.period == T(period.period.name)) & (db.grades_log.yearp == period.yearp)
                            & (db.grades_log.project == project.name) & (db.grades_log.date_log >= month_1)
                            & (db.grades_log.date_log < month_2) & (db.grades_log.roll == roll)
                            & (db.grades_log.user_name == user_p) & (db.grades_log.operation_log == 'insert')).select(
                                db.grades_log.operation_log,
                                db.grades_log.academic,
                                db.grades_log.activity,
                                db.grades_log.category,
                                db.grades_log.before_grade,
                                db.grades_log.after_grade,
                                db.grades_log.date_log,
                                db.grades_log.description
                            )
            elif request.vars['type_l'] == "u":
                all_data = db((db.grades_log.period == T(period.period.name)) & (db.grades_log.yearp == period.yearp)
                            & (db.grades_log.project == project.name) & (db.grades_log.date_log >= month_1)
                            & (db.grades_log.date_log < month_2) & (db.grades_log.roll == roll)
                            & (db.grades_log.user_name == user_p) & (db.grades_log.operation_log == 'update')).select(
                                db.grades_log.operation_log,
                                db.grades_log.academic,
                                db.grades_log.activity,
                                db.grades_log.category,
                                db.grades_log.before_grade,
                                db.grades_log.after_grade,
                                db.grades_log.date_log,
                                db.grades_log.description
                            )
            elif request.vars['type_l'] == "d":
                all_data = db((db.grades_log.period == T(period.period.name)) & (db.grades_log.yearp == period.yearp)
                            & (db.grades_log.project == project.name) & (db.grades_log.date_log >= month_1)
                            & (db.grades_log.date_log < month_2) & (db.grades_log.roll == roll)
                            & (db.grades_log.user_name == user_p) & (db.grades_log.operation_log == 'delete')).select(
                                db.grades_log.operation_log,
                                db.grades_log.academic,
                                db.grades_log.activity,
                                db.grades_log.category,
                                db.grades_log.before_grade,
                                db.grades_log.after_grade,
                                db.grades_log.date_log,
                                db.grades_log.description
                            )
        else:
            if request.vars['type_l'] == "all":
                all_data = db((db.grades_log.period == T(period.period.name)) & (db.grades_log.yearp == period.yearp)
                            & (db.grades_log.project == project.name) & (db.grades_log.date_log >= month_1)
                            & (db.grades_log.date_log < month_2) & (db.grades_log.roll == roll)
                            & (db.grades_log.user_name == user_p) & (db.grades_log.academic.like(f'%{personal_query}%'))).select(
                                db.grades_log.operation_log,
                                db.grades_log.academic,
                                db.grades_log.activity,
                                db.grades_log.category,
                                db.grades_log.before_grade,
                                db.grades_log.after_grade,
                                db.grades_log.date_log,
                                db.grades_log.description
                            )
            elif request.vars['type_l'] == "i":
                all_data = db((db.grades_log.period == T(period.period.name)) & (db.grades_log.yearp == period.yearp)
                            & (db.grades_log.project == project.name) & (db.grades_log.date_log >= month_1)
                            & (db.grades_log.date_log < month_2) & (db.grades_log.roll == roll)
                            & (db.grades_log.user_name == user_p) & (db.grades_log.operation_log == 'insert')
                            & (db.grades_log.academic.like(f'%{personal_query}%'))).select(
                                db.grades_log.operation_log,
                                db.grades_log.academic,
                                db.grades_log.activity,
                                db.grades_log.category,
                                db.grades_log.before_grade,
                                db.grades_log.after_grade,
                                db.grades_log.date_log,
                                db.grades_log.description
                            )
            elif request.vars['type_l'] == "u":
                all_data = db((db.grades_log.period == T(period.period.name)) & (db.grades_log.yearp == period.yearp)
                            & (db.grades_log.project == project.name) & (db.grades_log.date_log >= month_1)
                            & (db.grades_log.date_log < month_2) & (db.grades_log.roll == roll)
                            & (db.grades_log.user_name == user_p) & (db.grades_log.operation_log == 'update')
                            & (db.grades_log.academic.like(f'%{personal_query}%'))).select(
                                db.grades_log.operation_log,
                                db.grades_log.academic,
                                db.grades_log.activity,
                                db.grades_log.category,
                                db.grades_log.before_grade,
                                db.grades_log.after_grade,
                                db.grades_log.date_log,
                                db.grades_log.description
                            )
            elif request.vars['type_l'] == "d":
                all_data = db((db.grades_log.period == T(period.period.name)) & (db.grades_log.yearp == period.yearp)
                            & (db.grades_log.project == project.name) & (db.grades_log.date_log >= month_1)
                            & (db.grades_log.date_log < month_2) & (db.grades_log.roll == roll)
                            & (db.grades_log.user_name == user_p) & (db.grades_log.operation_log == 'delete')
                            & (db.grades_log.academic.like(f'%{personal_query}%'))).select(
                                db.grades_log.operation_log,
                                db.grades_log.academic,
                                db.grades_log.activity,
                                db.grades_log.category,
                                db.grades_log.before_grade,
                                db.grades_log.after_grade,
                                db.grades_log.date_log,
                                db.grades_log.description
                            )
        #TITLE OF TABLE
        info_level.append(['Operación', 'Estudiantes', 'Actividad', 'Categoria', 'Nota histórica', 'Nota oficial', 'Descripción', 'Fecha'])
        for operation in all_data:
            infoe_level_temp = []
            infoe_level_temp.append(operation.operation_log)
            infoe_level_temp.append(operation.academic)
            infoe_level_temp.append(operation.activity)
            infoe_level_temp.append(operation.category)
            infoe_level_temp.append(operation.before_grade)
            infoe_level_temp.append(operation.after_grade)
            infoe_level_temp.append(operation.description)
            infoe_level_temp.append(operation.date_log)
            info_level.append(infoe_level_temp)
    return dict(csvdata=info_level)

@auth.requires_login()
@auth.requires(auth.has_membership('Teacher'))
def laboratory_replacing_management():
    period = cpfecys.current_year_period()
    info_level = []
    personal_query = ''
    make_redirect = False
    project = None
    month = None
    roll = None
    user_p = None
    grid = None
    if request.vars['query_search'] is not None and request.vars['query_search'] != "":
        #PERSONALIZED QUERY SURE WORK
        try:
            personal_query = int(request.vars['query_search'])
            db(db.validate_laboratory_log.academic == personal_query).count()
            if request.vars['search_t'] is not None and str(request.vars['search_t']) == 'T':
                make_redirect = True
        except:
            response.flash = T('The query is not valid. The report is displayed without applying any query.')
            personal_query = ''
    if make_redirect:
        redirect(URL('teacher_reports', 'laboratory_replacing_management', vars=dict(
                                                                                level=5,
                                                                                project=request.vars['project'],
                                                                                month=request.vars['month'],
                                                                                roll=request.vars['roll'],
                                                                                user_p=request.vars['user_p'],
                                                                                type_l=request.vars['type_l'],
                                                                                type_u=request.vars['type_u'],
                                                                                query_search=request.vars['query_search']
                                                                            )
        ))

    try:
        #CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars['level'] is not None and (int(request.vars['level']) < 1 or int(request.vars['level']) > 5):
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'index'))
        
        #VERIFY THAT THE PARAMETERS OF EACH LEVEL BE VALID
        if request.vars['level'] is not None:
            #LEVEL MORE THAN 1
            if int(request.vars['level']) > 1:
                #CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars['type_l'] is None or (request.vars['type_l'] != "all" and request.vars['type_l'] != "i" and request.vars['type_l'] != "u" and request.vars['type_l'] != "d"):
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'index'))

                #CHECK IF THE PROJECT IS VALID
                project = validate_project(request.vars['project'], 'validate_laboratory_log')
                if project is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'index'))
            
            #LEVEL MORE THAN 2
            if int(request.vars['level']) > 2:
                #CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars['type_u'] is None or (request.vars['type_u'] != "all" and request.vars['type_u'] != "i" and request.vars['type_u'] != "u" and request.vars['type_u'] != "d"):
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'index'))

                #CHECK IF THE MONTH IS VALID
                month = validate_month(request.vars['month'])
                if month is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'index'))
                #OBTAIN ROLES
                roles = get_roles('validate_laboratory_log')
            
            #LEVEL MORE THAN 4
            if int(request.vars['level']) > 3:
                #CHECK IF THE ROLE IS VALID
                roll = validate_rol(request.vars['roll'], 'validate_laboratory_log')
                if roll is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'index'))
                #OBTAIN USERS
                users_project = get_users(project, roll, 'validate_laboratory_log')

            #LEVEL MORE THAN 5
            if int(request.vars['level']) > 4:
                #CHECK IF THE USER IS VALID
                user_p = validate_user(project, roll, request.vars['user_p'], 'validate_laboratory_log')
                if user_p is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'index'))
    except:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'index'))

    #LEVELS OF REPORT

    #ALL SEMESTERS
    if request.vars['level'] == '1' or request.vars['level'] is None:
        projects = db((db.user_project.assigned_user == auth.user.id) & ((db.user_project.period <= period.id) 
                    & ((db.user_project.period.cast('integer') + db.user_project.periods) > period.id))).select(db.user_project.project)
        if projects.first() is None:
            session.flash = T('Report no visible: There are no parameters required to display the report.')
            redirect(URL('activity_control','courses_list'))

        for project in projects:
            infoe_level_temp = []
            #ID OF PERIOD
            infoe_level_temp.append(project.project.id)
            #NAME OF PERIOD
            infoe_level_temp.append(project.project.name)
            #COUNTS
            query_count = db.executesql(qtr.level_1_laboratory_management('F', T(period.period.name), period.yearp, project.project.name, f'%{personal_query}%'), as_dict=True)[0]
            infoe_level_temp.append(0 if query_count['insert_count'] is None else query_count['insert_count'])
            infoe_level_temp.append(0 if query_count['update_count'] is None else query_count['update_count'])
            infoe_level_temp.append(0 if query_count['delete_count'] is None else query_count['delete_count'])
            #INSERT PROJECT
            info_level.append(infoe_level_temp)
    #PER MONTH
    elif request.vars['level'] == "2":
        for month in get_month_period():
            start = str(datetime.strptime(f'{period.yearp}-{month[0]}-01', "%Y-%m-%d"))
            if month[2] == 1:
                end = str(datetime.strptime(f'{period.yearp + 1}-{month[2]}-01', "%Y-%m-%d"))
            else:
                end = str(datetime.strptime(f'{period.yearp}-{month[2]}-01', "%Y-%m-%d"))
            infoe_level_temp = []
            #ID OF MONTH
            infoe_level_temp.append(month[0])
            #NAME OF MONTH
            infoe_level_temp.append(f'{month[1]} {period.yearp}')
            #COUNTS
            query_count = db.executesql(qtr.level_2_laboratory_management('F', T(period.period.name), period.yearp, project.name, start, end, f'%{personal_query}%'), as_dict=True)[0]
            infoe_level_temp.append(0 if query_count['insert_count'] is None else query_count['insert_count'])
            infoe_level_temp.append(0 if query_count['update_count'] is None else query_count['update_count'])
            infoe_level_temp.append(0 if query_count['delete_count'] is None else query_count['delete_count'])
            info_level.append(infoe_level_temp)
    #PER ROL
    elif request.vars['level'] == "3":
        if len(roles) == 0:
            session.flash = T('Report no visible: There are no parameters required to display the report.')
            redirect(URL('teacher_reports', 'laboratory_replacing_management',vars=dict(level='2', type_l=request.vars['type_u'], query_search=personal_query)))

        for roll_t in roles:
            infoe_level_temp = []
            #ID OF ROLE
            infoe_level_temp.append(roll_t)
            #NAME OF ROLE
            infoe_level_temp.append(T(f'Rol {roll_t}'))
            #COUNTS
            query_count = db.executesql(qtr.level_3_laboratory_management('F', T(period.period.name), period.yearp, project.name, str(month[1]), str(month[2]), f'%{personal_query}%', str(roll_t)), as_dict=True)[0]
            infoe_level_temp.append(0 if query_count['insert_count'] is None else query_count['insert_count'])
            infoe_level_temp.append(0 if query_count['update_count'] is None else query_count['update_count'])
            infoe_level_temp.append(0 if query_count['delete_count'] is None else query_count['delete_count'])
            #INSERT ROLL
            info_level.append(infoe_level_temp)
    #PER USER
    elif request.vars['level'] == "4":
        if len(users_project) == 0:
            session.flash = T('Report no visible: There are no parameters required to display the report.')
            redirect(URL('teacher_reports', 'laboratory_replacing_management',vars=dict(level='3', month = str(request.vars['month']), type_l = str(request.vars['type_u']), type_u = str(request.vars['type_u']), query_search=personal_query)))

        for user_pt in users_project:
            infoe_level_temp = []
            #ID OF USER
            infoe_level_temp.append(user_pt)
            #COUNTS
            query_count = db.executesql(qtr.level_4_laboratory_management('F', T(period.period.name), period.yearp, project.name, str(month[1]), str(month[2]), f'%{personal_query}%', roll, user_pt), as_dict=True)[0]
            infoe_level_temp.append(0 if query_count['insert_count'] is None else query_count['insert_count'])
            infoe_level_temp.append(0 if query_count['update_count'] is None else query_count['update_count'])
            infoe_level_temp.append(0 if query_count['delete_count'] is None else query_count['delete_count'])
            #INSERT USER
            info_level.append(infoe_level_temp)
    #DATA
    elif request.vars['level'] == "5":
        #COUNTS
        if personal_query == '':
            if request.vars['type_l'] == "all":
                all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.validation_type == False)).select(db.validate_laboratory_log.id)
            elif request.vars['type_l'] == "i":
                all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.operation_log == 'insert')
                            & (db.validate_laboratory_log.validation_type == False)).select(db.validate_laboratory_log.id)
            elif request.vars['type_l'] == "u":
                all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.operation_log == 'update')
                            & (db.validate_laboratory_log.validation_type == False)).select(db.validate_laboratory_log.id)
            elif request.vars['type_l'] == "d":
                all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.operation_log == 'delete')
                            & (db.validate_laboratory_log.validation_type == False)).select(db.validate_laboratory_log.id)
        else:
            if request.vars['type_l'] == "all":
                all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.validation_type == False)
                            & (db.validate_laboratory_log.academic.like(f'%{personal_query}%'))).select(db.validate_laboratory_log.id)
            elif request.vars['type_l'] == "i":
                all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.operation_log == 'insert')
                            & (db.validate_laboratory_log.validation_type == False) & (db.validate_laboratory_log.academic.like(f'%{personal_query}%'))).select(db.validate_laboratory_log.id)
            elif request.vars['type_l'] == "u":
                    all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.operation_log == 'update')
                            & (db.validate_laboratory_log.validation_type == False) & (db.validate_laboratory_log.academic.like(f'%{personal_query}%'))).select(db.validate_laboratory_log.id)
            elif request.vars['type_l'] == "d":
                    all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.operation_log == 'delete')
                            & (db.validate_laboratory_log.validation_type == False) & (db.validate_laboratory_log.academic.like(f'%{personal_query}%'))).select(db.validate_laboratory_log.id)
        grid = []
        for data in all_data:
                grid.append(data.id)
        if len(grid) == 0:
            grid.append(-1)
        #GRID
        db.validate_laboratory_log.id.readable = False
        db.validate_laboratory_log.id.writable = False
        db.validate_laboratory_log.user_name.readable = False
        db.validate_laboratory_log.user_name.writable = False
        db.validate_laboratory_log.roll.readable = False
        db.validate_laboratory_log.roll.writable = False
        db.validate_laboratory_log.academic_id.readable = False
        db.validate_laboratory_log.academic_id.writable = False
        db.validate_laboratory_log.project.readable = False
        db.validate_laboratory_log.project.writable = False
        db.validate_laboratory_log.yearp.readable = False
        db.validate_laboratory_log.yearp.writable = False
        db.validate_laboratory_log.period.readable = False
        db.validate_laboratory_log.period.writable = False
        db.validate_laboratory_log.validation_type.readable = False
        db.validate_laboratory_log.validation_type.writable = False
        db.validate_laboratory_log.id_validate_laboratory.readable = False
        db.validate_laboratory_log.id_validate_laboratory.writable = False
        grid = SQLFORM.grid(db.validate_laboratory_log.id.belongs(grid), csv=False, create=False, editable=False, deletable=False, paginate=9, searchable=False)
    return dict(personal_query=personal_query, info_level=info_level, period=period, project=project, month=month, roll=roll, user_p=user_p, grid=grid)

@auth.requires_login()
@auth.requires(auth.has_membership('Teacher'))
def laboratory_replacing_management_export():
    period = cpfecys.current_year_period()
    info_level = []
    personal_query = ''
    if request.vars['query_search'] is not None and request.vars['query_search'] != "":
        #PERSONALIZED QUERY SURE WORK
        try:
            personal_query = int(request.vars['query_search'])
            db(db.validate_laboratory_log.academic == personal_query).count()
        except:
            personal_query = ''

    try:
        #CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars['level'] is not None and (int(request.vars['level']) < 1 or int(request.vars['level']) > 5):
            session.flash = T('Not valid Action.')
            redirect(URL('default','index'))
        
        #VERIFY THAT THE PARAMETERS OF EACH LEVEL BE VALID
        if request.vars['level'] is not None:
            #LEVEL MORE THAN 1
            if int(request.vars['level']) > 1:
                #CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars['type_l'] is None or (request.vars['type_l'] != "all" and request.vars['type_l'] != "i" and request.vars['type_l'] != "u" and request.vars['type_l'] != "d"):
                    session.flash = T('Not valid Action.')
                    redirect(URL('default','index'))

                #CHECK IF THE PROJECT IS VALID
                project = validate_project(request.vars['project'], 'validate_laboratory_log')
                if project is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default','index'))
            
            #LEVEL MORE THAN 2
            if int(request.vars['level']) > 2:
                #CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars['type_u'] is None or (request.vars['type_u'] != "all" and request.vars['type_u'] != "i" and request.vars['type_u'] != "u" and request.vars['type_u'] != "d"):
                    session.flash = T('Not valid Action.')
                    redirect(URL('default','index'))

                #CHECK IF THE MONTH IS VALID
                month = validate_month(request.vars['month'])
                if month is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default','index'))
                
                #OBTAIN ROLES
                roles = get_roles('validate_laboratory_log')
            
            #LEVEL MORE THAN 4
            if int(request.vars['level']) > 3:
                #CHECK IF THE ROLE IS VALID
                roll = validate_rol(request.vars['roll'], 'validate_laboratory_log')
                if roll is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'index'))
                #OBTAIN USERS
                users_project = get_users(project, roll, 'validate_laboratory_log')

            #LEVEL MORE THAN 5
            if int(request.vars['level']) > 4:
                #CHECK IF THE USER IS VALID
                user_p = validate_user(project, roll, request.vars['user_p'], 'validate_laboratory_log')
                if user_p is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default','index'))
                    session.flash = 'a'
    except:
        session.flash = T('Not valid Action.')
        redirect(URL('default','index'))
    
    #****************************************************************************************************************
    #****************************************************************************************************************
    #*****************************************************REPORT*****************************************************
    #TITLE
    info_level = []
    info_level.append(['Universidad de San Carlos de Guatemala'])
    info_level.append(['Facultad de Ingeniería'])
    info_level.append(['Escuela de Ingeniería en Ciencias y Sistemas'])
    #TYPE OF REPORT
    info_level.append([''])
    info_level.append(['Tipo', 'Reporte de gestión de equivalencias de laboratorio'])
    #PERIOD OF REPORT
    info_level.append(['Periodo', f'{T(period.period.name)} {period.yearp}'])
    #ALL SEMESTERS
    if request.vars['level'] == '1' or request.vars['level'] is None:
        #MIDDLE LINE OF REPORT
        info_level.append([''])
        #LABLE DETAIL OF REPORT
        info_level.append(['Detalle'])
        #LABELS OF DATA OF REPORT
        info_level.append(['Curso', 'Total inserciones', 'Total actualizaciones', 'Total eliminaciones'])
        for project in db((db.user_project.assigned_user == auth.user.id) & ((db.user_project.period <= period.id)
                        & ((db.user_project.period.cast('integer') + db.user_project.periods) > period.id))).select(db.user_project.project):
            infoe_level_temp = []
            #NAME OF PROJECT
            infoe_level_temp.append(project.project.name)
            query_count = db.executesql(qtr.level_1_laboratory_management('F', T(period.period.name), period.yearp, project.project.name, f'%{personal_query}%'), as_dict=True)[0]
            infoe_level_temp.append(0 if query_count['insert_count'] is None else query_count['insert_count'])
            infoe_level_temp.append(0 if query_count['update_count'] is None else query_count['update_count'])
            infoe_level_temp.append(0 if query_count['delete_count'] is None else query_count['delete_count'])
            info_level.append(infoe_level_temp)
    #PER MONTH
    elif request.vars['level'] == "2":
        #PROJECT OF REPORT
        info_level.append(['Curso', project.name])
        #MIDDLE LINE OF REPORT
        info_level.append([''])
        #LABLE DETAIL OF REPORT
        info_level.append(['Detalle'])
        #LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append('Mes')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "i":
            infoe_level_temp.append('Total inserciones')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "u":
            infoe_level_temp.append('Total actualizaciones')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "d":
            infoe_level_temp.append('Total eliminaciones')
        info_level.append(infoe_level_temp)

        for month in get_month_period():
            start = str(datetime.strptime(f'{period.yearp}-{month[0]}-01', "%Y-%m-%d"))
            if month[2] == 1:
                end = str(datetime.strptime(f'{period.yearp + 1}-{month[2]}-01', "%Y-%m-%d"))
            else:
                end = str(datetime.strptime(f'{period.yearp}-{month[2]}-01', "%Y-%m-%d"))

            infoe_level_temp = []
            #NAME OF MONTH
            infoe_level_temp.append(f'{month[1]} {period.yearp}')
            #COUNTS
            query_count = db.executesql(qtr.level_2_laboratory_management('F', T(period.period.name), period.yearp, project.name, start, end, f'%{personal_query}%'), as_dict=True)[0]
            infoe_level_temp.append(0 if query_count['insert_count'] is None else query_count['insert_count'])
            infoe_level_temp.append(0 if query_count['update_count'] is None else query_count['update_count'])
            infoe_level_temp.append(0 if query_count['delete_count'] is None else query_count['delete_count'])
            #INSERT MONTH
            info_level.append(infoe_level_temp)
    #PER ROL
    elif request.vars['level'] == "3":
        #PROJECT OF REPORT
        info_level.append(['Curso', project.name])
        #MONTH OF REPORT
        info_level.append(['Mes', month[0]])
        #MIDDLE LINE OF REPORT
        info_level.append([''])
        #LABLE DETAIL OF REPORT
        info_level.append(['Detalle'])
        #LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append('Rol')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "i":
            infoe_level_temp.append('Total inserciones')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "u":
            infoe_level_temp.append('Total actualizaciones')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "d":
            infoe_level_temp.append('Total eliminaciones')
        info_level.append(infoe_level_temp)

        for roll_t in roles:
            infoe_level_temp = []
            #NAME OF ROLE
            infoe_level_temp.append(T(f'Rol {roll_t}'))
            #COUNTS
            query_count = db.executesql(qtr.level_3_laboratory_management('F', T(period.period.name), period.yearp, project.name, str(month[1]), str(month[2]), f'%{personal_query}%', str(roll_t)), as_dict=True)[0]
            infoe_level_temp.append(0 if query_count['insert_count'] is None else query_count['insert_count'])
            infoe_level_temp.append(0 if query_count['update_count'] is None else query_count['update_count'])
            infoe_level_temp.append(0 if query_count['delete_count'] is None else query_count['delete_count'])
            #INSERT ROLL
            info_level.append(infoe_level_temp)
    #PER USER
    elif request.vars['level'] == "4":
        #PROJECT OF REPORT
        info_level.append(['Curso', project.name])
        #MONTH OF REPORT
        info_level.append(['Mes', month[0]])
        #ROLE OF REPORT
        info_level.append(['Rol', T(f'Rol {roll}')])
        #MIDDLE LINE OF REPORT
        info_level.append([''])
        #LABLE DETAIL OF REPORT
        info_level.append(['Detalle'])
        #LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append('Usuario')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "i":
            infoe_level_temp.append('Total inserciones')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "u":
            infoe_level_temp.append('Total actualizaciones')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "d":
            infoe_level_temp.append('Total eliminaciones')
        info_level.append(infoe_level_temp)

        for user_pt in users_project:
            infoe_level_temp = []
            #NAME OF USER
            infoe_level_temp.append(user_pt)
            #COUNTS
            query_count = db.executesql(qtr.level_4_laboratory_management('F', T(period.period.name), period.yearp, project.name, str(month[1]), str(month[2]), f'%{personal_query}%', roll, user_pt), as_dict=True)[0]
            infoe_level_temp.append(0 if query_count['insert_count'] is None else query_count['insert_count'])
            infoe_level_temp.append(0 if query_count['update_count'] is None else query_count['update_count'])
            infoe_level_temp.append(0 if query_count['delete_count'] is None else query_count['delete_count'])
            #INSERT USER
            info_level.append(infoe_level_temp)
    #DATA
    elif request.vars['level'] == "5":
        #PROJECT OF REPORT
        info_level.append(['Curso', project.name])
        #MONTH OF REPORT
        info_level.append(['Mes', month[0]])
        #ROLE OF REPORT
        info_level.append(['Rol', T(f'Rol {roll}')])
        #ROLE OF REPORT
        info_level.append(['Usuario', user_p])
        #MIDDLE LINE OF REPORT
        info_level.append([''])
        #LABLE DETAIL OF REPORT
        info_level.append(['Detalle'])
        #COUNTS
        if personal_query == '':
            if request.vars['type_l'] == "all":
                all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.validation_type == False)).select(
                                db.validate_laboratory_log.operation_log,
                                db.validate_laboratory_log.academic,
                                db.validate_laboratory_log.before_grade,
                                db.validate_laboratory_log.after_grade,
                                db.validate_laboratory_log.date_log,
                                db.validate_laboratory_log.description
                            )
            elif request.vars['type_l'] == "i":
                all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.operation_log == 'insert')
                            & (db.validate_laboratory_log.validation_type == False)).select(                                
                                db.validate_laboratory_log.operation_log,
                                db.validate_laboratory_log.academic,
                                db.validate_laboratory_log.before_grade,
                                db.validate_laboratory_log.after_grade,
                                db.validate_laboratory_log.date_log,
                                db.validate_laboratory_log.description
                            )
            elif request.vars['type_l'] == "u":
                all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.operation_log == 'update')
                            & (db.validate_laboratory_log.validation_type == False)).select(                                
                                db.validate_laboratory_log.operation_log,
                                db.validate_laboratory_log.academic,
                                db.validate_laboratory_log.before_grade,
                                db.validate_laboratory_log.after_grade,
                                db.validate_laboratory_log.date_log,
                                db.validate_laboratory_log.description
                            )
            elif request.vars['type_l'] == "d":
                all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.operation_log == 'delete')
                            & (db.validate_laboratory_log.validation_type == False)).select(                                
                                db.validate_laboratory_log.operation_log,
                                db.validate_laboratory_log.academic,
                                db.validate_laboratory_log.before_grade,
                                db.validate_laboratory_log.after_grade,
                                db.validate_laboratory_log.date_log,
                                db.validate_laboratory_log.description
                            )
        else:
            if request.vars['type_l'] == "all":
                all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.validation_type == False)
                            & (db.validate_laboratory_log.academic.like(f'%{personal_query}%'))).select(                                
                                db.validate_laboratory_log.operation_log,
                                db.validate_laboratory_log.academic,
                                db.validate_laboratory_log.before_grade,
                                db.validate_laboratory_log.after_grade,
                                db.validate_laboratory_log.date_log,
                                db.validate_laboratory_log.description
                            )
            elif request.vars['type_l'] == "i":
                all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.operation_log == 'insert')
                            & (db.validate_laboratory_log.validation_type == False) & (db.validate_laboratory_log.academic.like(f'%{personal_query}%'))).select(
                                db.validate_laboratory_log.operation_log,
                                db.validate_laboratory_log.academic,
                                db.validate_laboratory_log.before_grade,
                                db.validate_laboratory_log.after_grade,
                                db.validate_laboratory_log.date_log,
                                db.validate_laboratory_log.description
                            )
            elif request.vars['type_l'] == "u":
                    all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.operation_log == 'update')
                            & (db.validate_laboratory_log.validation_type == False) & (db.validate_laboratory_log.academic.like(f'%{personal_query}%'))).select(
                                db.validate_laboratory_log.operation_log,
                                db.validate_laboratory_log.academic,
                                db.validate_laboratory_log.before_grade,
                                db.validate_laboratory_log.after_grade,
                                db.validate_laboratory_log.date_log,
                                db.validate_laboratory_log.description
                            )
            elif request.vars['type_l'] == "d":
                    all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.operation_log == 'delete')
                            & (db.validate_laboratory_log.validation_type == False) & (db.validate_laboratory_log.academic.like(f'%{personal_query}%'))).select(
                                db.validate_laboratory_log.operation_log,
                                db.validate_laboratory_log.academic,
                                db.validate_laboratory_log.before_grade,
                                db.validate_laboratory_log.after_grade,
                                db.validate_laboratory_log.date_log,
                                db.validate_laboratory_log.description
                            )
        #TITLE OF TABLE
        info_level.append(['Operación', 'Estudiante', 'Nota histórica', 'Nota oficial', 'Fecha', 'Descripción'])
        for operation in all_data:
            infoe_level_temp = []
            infoe_level_temp.append(operation.operation_log)
            infoe_level_temp.append(operation.academic)
            infoe_level_temp.append(operation.before_grade)
            infoe_level_temp.append(operation.after_grade)
            infoe_level_temp.append(operation.date_log)
            infoe_level_temp.append(operation.description)
            info_level.append(infoe_level_temp)
    return dict(csvdata=info_level)

@auth.requires_login()
@auth.requires(auth.has_membership('Teacher'))
def validate_laboratory_management():
    period = cpfecys.current_year_period()
    info_level = []
    personal_query = ''
    make_redirect = False
    project = None
    month = None
    roll = None
    user_p = None
    grid = None
    if request.vars['query_search'] is not None and str(request.vars['query_search']) != "":
        #PERSONALIZED QUERY SURE WORK
        try:
            personal_query = int(request.vars['query_search'])
            db(db.validate_laboratory_log.academic == personal_query).count()
            if request.vars['search_t'] is not None and request.vars['search_t'] == 'T':
                make_redirect = True
        except:
            response.flash = T('The query is not valid. The report is displayed without applying any query.')
            personal_query = ''
    
    if make_redirect:
        redirect(URL('teacher_reports', 'validate_laboratory_management', vars=dict(
                                                                            level=5,
                                                                            project=request.vars['project'],
                                                                            month=request.vars['month'],
                                                                            roll=request.vars['roll'],
                                                                            user_p=request.vars['user_p'],
                                                                            type_l=request.vars['type_l'],
                                                                            type_u=request.vars['type_u'],
                                                                            query_search=request.vars['query_search']
                                                                        )
        ))

    try:
        #CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars['level'] is not None and (int(request.vars['level']) < 1 or int(request.vars['level']) > 5):
            session.flash = T('Not valid Action.')
            redirect(URL('default','index'))
        
        #VERIFY THAT THE PARAMETERS OF EACH LEVEL BE VALID
        if request.vars['level'] is not None:
            #LEVEL MORE THAN 1
            if int(request.vars['level']) > 1:
                #CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars['type_l'] is None or (request.vars['type_l'] != "all" and request.vars['type_l'] != "i" and request.vars['type_l'] != "u" and request.vars['type_l'] != "d"):
                    session.flash = T('Not valid Action.')
                    redirect(URL('default','index'))

                #CHECK IF THE PROJECT IS VALID
                project = validate_project(request.vars['project'], 'validate_laboratory_log')
                if project is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default','index'))
            
            #LEVEL MORE THAN 2
            if int(request.vars['level']) > 2:
                #CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars['type_u'] is None or (request.vars['type_u'] != "all" and request.vars['type_u'] != "i" and request.vars['type_u'] != "u" and request.vars['type_u'] != "d"):
                    session.flash = T('Not valid Action.')
                    redirect(URL('default','index'))

                #CHECK IF THE MONTH IS VALID
                month = validate_month(request.vars['month'])
                if month is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default','index'))
                #OBTAIN ROLES
                roles = get_roles('validate_laboratory_log')
            
            #LEVEL MORE THAN 4
            if int(request.vars['level']) > 3:
                #CHECK IF THE ROLE IS VALID
                roll = validate_rol(request.vars['roll'], 'validate_laboratory_log')
                if roll is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default','index'))
                
                #OBTAIN USERS
                users_project = get_users(project, roll, 'validate_laboratory_log')

            #LEVEL MORE THAN 5
            if int(request.vars['level']) > 4:
                #CHECK IF THE USER IS VALID
                user_p = validate_user(project, roll, request.vars['user_p'], 'validate_laboratory_log')
                if user_p is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default','index'))
    except:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'index'))
    
    #LEVELS OF REPORT
    #ALL SEMESTERS
    if request.vars['level'] == '1' or request.vars['level'] is None:
        projects = db((db.user_project.assigned_user == auth.user.id) & ((db.user_project.period <= period.id)
                    & ((db.user_project.period.cast('integer') + db.user_project.periods) > period.id))).select(db.user_project.project)
        if projects.first() is None:
            session.flash = T('Report no visible: There are no parameters required to display the report.')
            redirect(URL('activity_control', 'courses_list'))

        for project in projects:
            infoe_level_temp = []
            #ID OF PERIOD
            infoe_level_temp.append(project.project.id)
            #NAME OF PERIOD
            infoe_level_temp.append(project.project.name)
            #COUNTS
            query_count = db.executesql(qtr.level_1_laboratory_management('T', T(period.period.name), period.yearp, project.project.name, f'%{personal_query}%'), as_dict=True)[0]
            infoe_level_temp.append(0 if query_count['insert_count'] is None else query_count['insert_count'])
            infoe_level_temp.append(0 if query_count['update_count'] is None else query_count['update_count'])
            infoe_level_temp.append(0 if query_count['delete_count'] is None else query_count['delete_count'])
            #INSERT PROJECT
            info_level.append(infoe_level_temp)
    #PER MONTH
    elif request.vars['level'] == "2":
        for month in get_month_period():
            start = str(datetime.strptime(f'{period.yearp}-{month[0]}-01', "%Y-%m-%d"))
            if month[2] == 1:
                end = str(datetime.strptime(f'{period.yearp + 1}-{month[2]}-01', "%Y-%m-%d"))
            else:
                end = str(datetime.strptime(f'{period.yearp}-{month[2]}-01', "%Y-%m-%d"))
            infoe_level_temp = []
            #ID OF MONTH
            infoe_level_temp.append(month[0])
            #NAME OF MONTH
            infoe_level_temp.append(f'{month[1]} {period.yearp}')
            #COUNTS
            query_count = db.executesql(qtr.level_2_laboratory_management('T', T(period.period.name), period.yearp, project.name, start, end, f'%{personal_query}%'), as_dict=True)[0]
            infoe_level_temp.append(0 if query_count['insert_count'] is None else query_count['insert_count'])
            infoe_level_temp.append(0 if query_count['update_count'] is None else query_count['update_count'])
            infoe_level_temp.append(0 if query_count['delete_count'] is None else query_count['delete_count'])
            #INSERT MONTH
            info_level.append(infoe_level_temp)
    #PER ROL
    elif request.vars['level'] == "3":
        if len(roles) == 0:
            session.flash = T('Report no visible: There are no parameters required to display the report.')
            redirect(URL('teacher_reports', 'validate_laboratory_management',vars=dict(level='2', type_l=request.vars['type_u'], query_search=personal_query)))

        for roll_t in roles:
            infoe_level_temp = []
            #ID OF ROLE
            infoe_level_temp.append(roll_t)
            #NAME OF ROLE
            infoe_level_temp.append(T(f'Rol {roll_t}'))
            #COUNTS
            query_count = db.executesql(qtr.level_3_laboratory_management('T', T(period.period.name), period.yearp, project.name, str(month[1]), str(month[2]), f'%{personal_query}%', str(roll_t)), as_dict=True)[0]
            infoe_level_temp.append(0 if query_count['insert_count'] is None else query_count['insert_count'])
            infoe_level_temp.append(0 if query_count['update_count'] is None else query_count['update_count'])
            infoe_level_temp.append(0 if query_count['delete_count'] is None else query_count['delete_count'])
            #INSERT ROLL
            info_level.append(infoe_level_temp)
    #PER USER
    elif request.vars['level'] == "4":
        if len(users_project) == 0:
            session.flash = T('Report no visible: There are no parameters required to display the report.')
            redirect(URL('teacher_reports', 'validate_laboratory_management',vars=dict(level='3', month=request.vars['month'], type_l=request.vars['type_u'], type_u=request.vars['type_u'], query_search=personal_query)))

        for user_pt in users_project:
            infoe_level_temp = []
            #NAME OF USER
            infoe_level_temp.append(user_pt)
            #COUNTS
            query_count = db.executesql(qtr.level_4_laboratory_management('T', T(period.period.name), period.yearp, project.name, str(month[1]), str(month[2]), f'%{personal_query}%', roll, user_pt), as_dict=True)[0]
            infoe_level_temp.append(0 if query_count['insert_count'] is None else query_count['insert_count'])
            infoe_level_temp.append(0 if query_count['update_count'] is None else query_count['update_count'])
            infoe_level_temp.append(0 if query_count['delete_count'] is None else query_count['delete_count'])
            #INSERT USER
            info_level.append(infoe_level_temp)
    #DATA
    elif request.vars['level'] == "5":
        #COUNTS
        if personal_query == '':
            if request.vars['type_l'] == "all":
                all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.validation_type == True)).select(db.validate_laboratory_log.id)
            elif request.vars['type_l'] == "i":
                all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.operation_log == 'insert')
                            & (db.validate_laboratory_log.validation_type == True)).select(db.validate_laboratory_log.id)
            elif request.vars['type_l'] == "u":
                all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.operation_log == 'update')
                            & (db.validate_laboratory_log.validation_type == True)).select(db.validate_laboratory_log.id)
            elif request.vars['type_l'] == "d":
                all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.operation_log == 'delete')
                            & (db.validate_laboratory_log.validation_type == True)).select(db.validate_laboratory_log.id)
        else:
            if request.vars['type_l'] == "all":
                all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.validation_type == True)
                            & (db.validate_laboratory_log.academic.like(f'%{personal_query}%'))).select(db.validate_laboratory_log.id)
            elif request.vars['type_l'] == "i":
                all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.operation_log == 'insert')
                            & (db.validate_laboratory_log.validation_type == True) & (db.validate_laboratory_log.academic.like(f'%{personal_query}%'))).select(db.validate_laboratory_log.id)
            elif request.vars['type_l'] == "u":
                    all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.operation_log == 'update')
                            & (db.validate_laboratory_log.validation_type == True) & (db.validate_laboratory_log.academic.like(f'%{personal_query}%'))).select(db.validate_laboratory_log.id)
            elif request.vars['type_l'] == "d":
                    all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.operation_log == 'delete')
                            & (db.validate_laboratory_log.validation_type == True) & (db.validate_laboratory_log.academic.like(f'%{personal_query}%'))).select(db.validate_laboratory_log.id)
        grid = []
        for data in all_data:
                grid.append(data.id)
        if len(grid) == 0:
            grid.append(-1)
        #GRID
        db.validate_laboratory_log.id.readable = False
        db.validate_laboratory_log.id.writable = False
        db.validate_laboratory_log.user_name.readable = False
        db.validate_laboratory_log.user_name.writable = False
        db.validate_laboratory_log.roll.readable = False
        db.validate_laboratory_log.roll.writable = False
        db.validate_laboratory_log.academic_id.readable = False
        db.validate_laboratory_log.academic_id.writable = False
        db.validate_laboratory_log.project.readable = False
        db.validate_laboratory_log.project.writable = False
        db.validate_laboratory_log.yearp.readable = False
        db.validate_laboratory_log.yearp.writable = False
        db.validate_laboratory_log.period.readable = False
        db.validate_laboratory_log.period.writable = False
        db.validate_laboratory_log.validation_type.readable = False
        db.validate_laboratory_log.validation_type.writable = False
        db.validate_laboratory_log.id_validate_laboratory.readable = False
        db.validate_laboratory_log.id_validate_laboratory.writable = False
        grid = SQLFORM.grid(db.validate_laboratory_log.id.belongs(grid), csv=False, create=False, editable=False, deletable=False, paginate=9, searchable=False)

    return dict(personal_query=personal_query, info_level=info_level, period=period, project=project, month=month, roll=roll, user_p=user_p, grid=grid)

@auth.requires_login()
@auth.requires(auth.has_membership('Teacher'))
def validate_laboratory_management_export():
    period = cpfecys.current_year_period()
    info_level = []
    personal_query = ''
    if request.vars['query_search'] is not None and request.vars['query_search'] != "":
        #PERSONALIZED QUERY SURE WORK
        try:
            personal_query = int(request.vars['query_search'])
            db(db.validate_laboratory_log.academic == personal_query).count()
        except:
            personal_query = ''

    try:
        #CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars['level'] is not None and (int(request.vars['level']) < 1 or int(request.vars['level']) > 5):
            session.flash = T('Not valid Action.')
            redirect(URL('default','index'))
        
        #VERIFY THAT THE PARAMETERS OF EACH LEVEL BE VALID
        if request.vars['level'] is not None:
            #LEVEL MORE THAN 1
            if int(request.vars['level']) > 1:
                #CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars['type_l'] is None or (request.vars['type_l'] != "all" and request.vars['type_l'] != "i" and request.vars['type_l'] != "u" and request.vars['type_l'] != "d"):
                    session.flash = T('Not valid Action.')
                    redirect(URL('default','index'))

                #CHECK IF THE PROJECT IS VALID
                project = validate_project(request.vars['project'], 'validate_laboratory_log')
                if project is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default','index'))
            
            #LEVEL MORE THAN 2
            if int(request.vars['level']) > 2:
                #CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars['type_u'] is None or (request.vars['type_u'] != "all" and request.vars['type_u'] != "i" and request.vars['type_u'] != "u" and request.vars['type_u'] != "d"):
                    session.flash = T('Not valid Action.')
                    redirect(URL('default','index'))

                #CHECK IF THE MONTH IS VALID
                month = validate_month(request.vars['month'])
                if month is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default','index'))
                #OBTAIN ROLES
                roles = get_roles('validate_laboratory_log')
            
            #LEVEL MORE THAN 4
            if int(request.vars['level']) > 3:
                #CHECK IF THE ROLE IS VALID
                roll = validate_rol(request.vars['roll'], 'validate_laboratory_log')
                if roll is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default', 'index'))
                #OBTAIN USERS
                users_project = get_users(project, roll, 'validate_laboratory_log')

            #LEVEL MORE THAN 5
            if int(request.vars['level']) > 4:
                #CHECK IF THE USER IS VALID
                user_p = validate_user(project, roll, request.vars['user_p'], 'validate_laboratory_log')
                if user_p is None:
                    session.flash = T('Not valid Action.')
                    redirect(URL('default','index'))
    except:
        session.flash = T('Not valid Action.')
        redirect(URL('default','index'))

    #TITLE
    info_level = []
    info_level.append(['Universidad de San Carlos de Guatemala'])
    info_level.append(['Facultad de Ingeniería'])
    info_level.append(['Escuela de Ingeniería en Ciencias y Sistemas'])
    info_level.append([''])
    #TYPE OF REPORT
    info_level.append(['Tipo', 'Reporte de gestión de revalidación de laboratorio'])
    #PERIOD OF REPORT
    info_level.append(['Periodo', f'{T(period.period.name)} {period.yearp}'])
    #ALL SEMESTERS
    if request.vars['level'] == '1' or request.vars['level'] is None:
        #MIDDLE LINE OF REPORT
        info_level.append([''])
        #LABLE DETAIL OF REPORT
        info_level.append(['Detalle'])
        #LABELS OF DATA OF REPORT
        info_level.append(['Curso', 'Total inserciones', 'Total actualizaciones', 'Total eliminaciones'])
        for project in db((db.user_project.assigned_user == auth.user.id) & ((db.user_project.period <= period.id)
                        & ((db.user_project.period.cast('integer') + db.user_project.periods) > period.id))).select(db.user_project.project):
            infoe_level_temp = []
            #NAME OF PROJECT
            infoe_level_temp.append(project.project.name)
            query_count = db.executesql(qtr.level_1_laboratory_management('T', T(period.period.name), period.yearp, project.project.name, f'%{personal_query}%'), as_dict=True)[0]
            infoe_level_temp.append(0 if query_count['insert_count'] is None else query_count['insert_count'])
            infoe_level_temp.append(0 if query_count['update_count'] is None else query_count['update_count'])
            infoe_level_temp.append(0 if query_count['delete_count'] is None else query_count['delete_count'])
            info_level.append(infoe_level_temp)
    #PER MONTH
    elif request.vars['level'] == "2":
        #PROJECT OF REPORT
        info_level.append(['Curso', project.name])
        #MIDDLE LINE OF REPORT
        info_level.append([''])
        #LABLE DETAIL OF REPORT
        info_level.append(['Detalle'])
        #LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append('Mes')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "i":
            infoe_level_temp.append('Total inserciones')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "u":
            infoe_level_temp.append('Total actualizaciones')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "d":
            infoe_level_temp.append('Total eliminaciones')
        info_level.append(infoe_level_temp)

        for month in get_month_period():
            start = str(datetime.strptime(f'{period.yearp}-{month[0]}-01', "%Y-%m-%d"))
            if month[2] == 1:
                end = str(datetime.strptime(f'{period.yearp + 1}-{month[2]}-01', "%Y-%m-%d"))
            else:
                end = str(datetime.strptime(f'{period.yearp}-{month[2]}-01', "%Y-%m-%d"))
            infoe_level_temp = []
            #NAME OF MONTH
            infoe_level_temp.append(f'{month[1]} {period.yearp}')
            #COUNTS
            query_count = db.executesql(qtr.level_2_laboratory_management('T', T(period.period.name), period.yearp, project.name, start, end, f'%{personal_query}%'), as_dict=True)[0]
            infoe_level_temp.append(0 if query_count['insert_count'] is None else query_count['insert_count'])
            infoe_level_temp.append(0 if query_count['update_count'] is None else query_count['update_count'])
            infoe_level_temp.append(0 if query_count['delete_count'] is None else query_count['delete_count'])
            #INSERT MONTH
            info_level.append(infoe_level_temp)
    #PER ROL
    elif request.vars['level'] == "3":
        #PROJECT OF REPORT
        info_level.append(['Curso', project.name])
        #MONTH OF REPORT
        info_level.append(['Mes', month[0]])
        #MIDDLE LINE OF REPORT
        info_level.append([''])
        #LABLE DETAIL OF REPORT
        info_level.append(['Detalle'])
        #LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append('Rol')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "i":
            infoe_level_temp.append('Total inserciones')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "u":
            infoe_level_temp.append('Total actualizaciones')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "d":
            infoe_level_temp.append('Total eliminaciones')
        info_level.append(infoe_level_temp)

        for roll_t in roles:
            infoe_level_temp = []
            #NAME OF ROLE
            infoe_level_temp.append(T(f'Rol {roll_t}'))
            #COUNTS
            query_count = db.executesql(qtr.level_3_laboratory_management('T', T(period.period.name), period.yearp, project.name, str(month[1]), str(month[2]), f'%{personal_query}%', str(roll_t)), as_dict=True)[0]
            infoe_level_temp.append(0 if query_count['insert_count'] is None else query_count['insert_count'])
            infoe_level_temp.append(0 if query_count['update_count'] is None else query_count['update_count'])
            infoe_level_temp.append(0 if query_count['delete_count'] is None else query_count['delete_count'])
            #INSERT ROLL
            info_level.append(infoe_level_temp)
    #PER USER
    elif request.vars['level'] == "4":
        #PROJECT OF REPORT
        info_level.append(['Curso', project.name])
        #MONTH OF REPORT
        info_level.append(['Mes', month[0]])
        #ROLE OF REPORT
        info_level.append(['Rol', T(f'Rol {roll}')])
        #MIDDLE LINE OF REPORT
        info_level.append([''])
        #LABLE DETAIL OF REPORT
        info_level.append(['Detalle'])
        #LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append('Usuario')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "i":
            infoe_level_temp.append('Total inserciones')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "u":
            infoe_level_temp.append('Total actualizaciones')
        if request.vars['type_l'] == "all" or request.vars['type_l'] == "d":
            infoe_level_temp.append('Total eliminaciones')
        info_level.append(infoe_level_temp)

        for user_pt in users_project:
            infoe_level_temp = []
            #NAME OF USER
            infoe_level_temp.append(user_pt)
            #COUNTS
            query_count = db.executesql(qtr.level_4_laboratory_management('T', T(period.period.name), period.yearp, project.name, str(month[1]), str(month[2]), f'%{personal_query}%', roll, user_pt), as_dict=True)[0]
            infoe_level_temp.append(0 if query_count['insert_count'] is None else query_count['insert_count'])
            infoe_level_temp.append(0 if query_count['update_count'] is None else query_count['update_count'])
            infoe_level_temp.append(0 if query_count['delete_count'] is None else query_count['delete_count'])
            #INSERT USER
            info_level.append(infoe_level_temp)
    #DATA
    elif request.vars['level'] == "5":
        #PROJECT OF REPORT
        info_level.append(['Curso', project.name])
        #MONTH OF REPORT
        info_level.append(['Mes', month[0]])
        #ROLE OF REPORT
        info_level.append(['Rol', T(f'Rol {roll}')])
        #ROLE OF REPORT
        info_level.append(['Usuario', user_p])
        #MIDDLE LINE OF REPORT
        info_level.append([''])
        #LABLE DETAIL OF REPORT
        info_level.append(['Detalle'])
        #COUNTS
        if personal_query == '':
            if request.vars['type_l'] == "all":
                all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.validation_type == True)).select(
                                db.validate_laboratory_log.operation_log,
                                db.validate_laboratory_log.academic,
                                db.validate_laboratory_log.before_grade,
                                db.validate_laboratory_log.after_grade,
                                db.validate_laboratory_log.date_log,
                                db.validate_laboratory_log.description
                            )
            elif request.vars['type_l'] == "i":
                all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.operation_log == 'insert')
                            & (db.validate_laboratory_log.validation_type == True)).select(                                
                                db.validate_laboratory_log.operation_log,
                                db.validate_laboratory_log.academic,
                                db.validate_laboratory_log.before_grade,
                                db.validate_laboratory_log.after_grade,
                                db.validate_laboratory_log.date_log,
                                db.validate_laboratory_log.description
                            )
            elif request.vars['type_l'] == "u":
                all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.operation_log == 'update')
                            & (db.validate_laboratory_log.validation_type == True)).select(                                
                                db.validate_laboratory_log.operation_log,
                                db.validate_laboratory_log.academic,
                                db.validate_laboratory_log.before_grade,
                                db.validate_laboratory_log.after_grade,
                                db.validate_laboratory_log.date_log,
                                db.validate_laboratory_log.description
                            )
            elif request.vars['type_l'] == "d":
                all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.operation_log == 'delete')
                            & (db.validate_laboratory_log.validation_type == True)).select(                                
                                db.validate_laboratory_log.operation_log,
                                db.validate_laboratory_log.academic,
                                db.validate_laboratory_log.before_grade,
                                db.validate_laboratory_log.after_grade,
                                db.validate_laboratory_log.date_log,
                                db.validate_laboratory_log.description
                            )
        else:
            if request.vars['type_l'] == "all":
                all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.validation_type == True)
                            & (db.validate_laboratory_log.academic.like(f'%{personal_query}%'))).select(                                
                                db.validate_laboratory_log.operation_log,
                                db.validate_laboratory_log.academic,
                                db.validate_laboratory_log.before_grade,
                                db.validate_laboratory_log.after_grade,
                                db.validate_laboratory_log.date_log,
                                db.validate_laboratory_log.description
                            )
            elif request.vars['type_l'] == "i":
                all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.operation_log == 'insert')
                            & (db.validate_laboratory_log.validation_type == True) & (db.validate_laboratory_log.academic.like(f'%{personal_query}%'))).select(
                                db.validate_laboratory_log.operation_log,
                                db.validate_laboratory_log.academic,
                                db.validate_laboratory_log.before_grade,
                                db.validate_laboratory_log.after_grade,
                                db.validate_laboratory_log.date_log,
                                db.validate_laboratory_log.description
                            )
            elif request.vars['type_l'] == "u":
                    all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.operation_log == 'update')
                            & (db.validate_laboratory_log.validation_type == True) & (db.validate_laboratory_log.academic.like(f'%{personal_query}%'))).select(
                                db.validate_laboratory_log.operation_log,
                                db.validate_laboratory_log.academic,
                                db.validate_laboratory_log.before_grade,
                                db.validate_laboratory_log.after_grade,
                                db.validate_laboratory_log.date_log,
                                db.validate_laboratory_log.description
                            )
            elif request.vars['type_l'] == "d":
                    all_data = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                            & (db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.date_log >= str(month[1]))
                            & (db.validate_laboratory_log.date_log < str(month[2])) & (db.validate_laboratory_log.roll == str(roll))
                            & (db.validate_laboratory_log.user_name == str(user_p)) & (db.validate_laboratory_log.operation_log == 'delete')
                            & (db.validate_laboratory_log.validation_type == True) & (db.validate_laboratory_log.academic.like(f'%{personal_query}%'))).select(
                                db.validate_laboratory_log.operation_log,
                                db.validate_laboratory_log.academic,
                                db.validate_laboratory_log.before_grade,
                                db.validate_laboratory_log.after_grade,
                                db.validate_laboratory_log.date_log,
                                db.validate_laboratory_log.description
                            )
        #TITLE OF TABLE
        info_level.append(['Operación', 'Estudiante', 'Nota histórica', 'Nota oficial', 'Fecha', 'Descripción'])
        for operation in all_data:
            infoe_level_temp = []
            infoe_level_temp.append(operation.operation_log)
            infoe_level_temp.append(operation.academic)
            infoe_level_temp.append(operation.before_grade)
            infoe_level_temp.append(operation.after_grade)
            infoe_level_temp.append(operation.date_log)
            infoe_level_temp.append(operation.description)
            info_level.append(infoe_level_temp)
    return dict(csvdata=info_level)

@auth.requires_login()
@auth.requires(auth.has_membership('Teacher'))
def validate_project(project_i, _):
    period = cpfecys.current_year_period()
    try:
        #CHECK IN THE LOG IF THE PROJECT EXIST
        project = db((db.user_project.assigned_user == auth.user.id) & (db.user_project.project == project_i)
                & ((db.user_project.period <= period.id) & ((db.user_project.period.cast('integer') + db.user_project.periods) > period.id))).select(db.user_project.project).first()
        project = db(db.project.id == project.project).select().first()
        return project
    except:
        return None

@auth.requires_login()
@auth.requires(auth.has_membership('Teacher'))
def validate_month(month):
    period = cpfecys.current_year_period()
    vec_month = None
    if month is not None:
        months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        imonth = int(month)
        m = months[imonth - 1]
        dt = datetime.strptime(f'{period.yearp}-{month}-01', "%Y-%m-%d")
        dtn = datetime.strptime(f'{period.yearp}-{imonth + 1}-01', "%Y-%m-%d") if imonth != 12 else datetime.strptime(f'{period.yearp + 1}-01-01', "%Y-%m-%d")
        vec_month = (m, dt, dtn)

    return vec_month

@auth.requires_login()
@auth.requires(auth.has_membership('Teacher'))
def get_roles(type_report):
    period = cpfecys.current_year_period()
    roles = []
    #OFFICIAL ROLES
    for roll in db((db.auth_group.role != 'Academic') & (db.auth_group.role != 'DSI')).select(db.auth_group.role.with_alias('roll'), distinct=True):
        roles.append(roll.roll)

    #ROLES IN LOGS
    if type_report == 'grades_log':
        if len(roles) == 0:
            roles_temp = db((db.grades_log.period == T(period.period.name)) & (db.grades_log.yearp == period.yearp)
                        & (db.grades_log.roll != 'Academic') & (db.grades_log.roll != 'DSI')).select(db.grades_log.roll.with_alias('roll'), distinct=True)
        else:
            roles_temp = db((db.grades_log.period == T(period.period.name)) & (db.grades_log.yearp == period.yearp)
                        & (~db.grades_log.roll.belongs(roles)) & (db.grades_log.roll != 'Academic') & (db.grades_log.roll != 'DSI')).select(db.grades_log.roll.with_alias('roll'), distinct=True)
        for roll in roles_temp:
            roles.append(roll.roll)
    elif type_report =='validate_laboratory_log':
        if len(roles) == 0:
            roles_temp = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                        & (db.validate_laboratory_log.roll != 'Academic') & (db.validate_laboratory_log.roll != 'DSI')).select(db.validate_laboratory_log.roll.with_alias('roll'), distinct=True)
        else:
            roles_temp = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                        & (~db.validate_laboratory_log.roll.belongs(roles)) & (db.validate_laboratory_log.roll != 'Academic')
                        & (db.validate_laboratory_log.roll != 'DSI')).select(db.validate_laboratory_log.roll.with_alias('roll'), distinct=True)
        for roll in roles_temp:
            roles.append(roll.roll)
    else:
        session.flash = T('Not valid Action.')
        redirect(URL('default','index'))
    
    return roles

@auth.requires_login()
@auth.requires(auth.has_membership('Teacher'))
def validate_rol(name_role, type_report):
    period = cpfecys.current_year_period()
    try:
        #CHECK IF THE ROLE EXIST IN THE OFFICIAL ROLES
        roll = db((db.auth_group.role == name_role) & (db.auth_group.role != 'Academic')
                & (db.auth_group.role != 'DSI')).select(db.auth_group.role).first()
        if roll is None:
            #CHECK IF THE ROLE EXIT IN THE LOGS OF SYSTEM 
            if type_report == 'grades_log':
                roll = db((db.grades_log.period == T(period.period.name)) & (db.grades_log.yearp == period.yearp)
                        & (db.grades_log.roll == name_role) & (db.grades_log.roll != 'Academic')
                        & (db.grades_log.roll != 'DSI')).select(db.grades_log.roll).first()
                if roll is not None:
                    roll = roll.roll
            elif type_report == 'validate_laboratory_log':
                roll = db((db.validate_laboratory_log.period == T(period.period.name)) & (db.validate_laboratory_log.yearp == period.yearp)
                        & (db.validate_laboratory_log.roll == name_role) & (db.validate_laboratory_log.roll != 'Academic')
                        & (db.validate_laboratory_log.roll != 'DSI')).select(db.validate_laboratory_log.roll).first()
                if roll is not None:
                    roll = roll.roll
            else:
                roll = None
        else:
            roll = roll.role
        #RETURN ROLE
        return roll
    except:
        return None

@auth.requires_login()
@auth.requires(auth.has_membership('Teacher'))
def get_users(project, roll, type_report):
    period = cpfecys.current_year_period()
    users_project = []
    #OFFICIAL USERS
    roll_t = db((db.auth_group.role == roll) & (db.auth_group.role != 'Academic')
            & (db.auth_group.role != 'DSI')).select(db.auth_group.id).first()
    if roll_t is not None:
        if roll == 'Super-Administrator' or roll == 'Ecys-Administrator':
            for user_t in db((db.auth_user.id == db.auth_membership.user_id) & (db.auth_membership.group_id == roll_t.id)).select(db.auth_user.username):
                users_project.append(user_t.username)
        else:
            for user_t in db((db.auth_membership.group_id == roll_t.id) & (db.auth_membership.user_id == db.auth_user.id)
                        & (db.auth_user.id == db.user_project.assigned_user) & (db.user_project.project == project.id)
                        & (db.user_project.period == db.period_year.id) & ((db.user_project.period <= period.id) 
                        & ((db.user_project.period.cast('integer') + db.user_project.periods) > period.id))).select(db.auth_user.username):
                users_project.append(user_t.username)

    #USERS IN LOGS
    if type_report == 'grades_log':
        if len(users_project) == 0:
            users_project_t = db((db.grades_log.project == project.name) & (db.grades_log.period == T(period.period.name))
                                & (db.grades_log.yearp == period.yearp) & (db.grades_log.roll == roll)).select(db.grades_log.user_name, distinct=True)
        else:
            users_project_t = db((db.grades_log.project == project.name) & (db.grades_log.period == T(period.period.name))
                                & (db.grades_log.yearp == period.yearp) & (db.grades_log.roll == roll)
                                & (~db.grades_log.user_name.belongs(users_project))).select(db.grades_log.user_name, distinct=True)
        for user_t in users_project_t:
            users_project.append(user_t.user_name)
    elif type_report == 'validate_laboratory_log':
        if len(users_project) == 0:
            users_project_t = db((db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.period == T(period.period.name))
                                & (db.validate_laboratory_log.yearp == period.yearp) & (db.validate_laboratory_log.roll == roll)).select(db.validate_laboratory_log.user_name, distinct=True)
        else:
            users_project_t = db((db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.period == T(period.period.name))
                                & (db.validate_laboratory_log.yearp == period.yearp) & (db.validate_laboratory_log.roll == roll)
                                & (~db.validate_laboratory_log.user_name.belongs(users_project))).select(db.validate_laboratory_log.user_name, distinct=True)
        for user_t in users_project_t:
            users_project.append(user_t.user_name)
    else:
        session.flash = T('Not valid Action.')
        redirect(URL('default','index'))

    return users_project

@auth.requires_login()
@auth.requires(auth.has_membership('Teacher'))
def validate_user(project, roll, id_user, type_report):
    period = cpfecys.current_year_period()
    try:
        #CHECK IF THE USER EXIST IN THE OFFICIAL USERS
        user_p = None
        roll_t = db((db.auth_group.role == roll) & (db.auth_group.role != 'Academic')
                & (db.auth_group.role!='DSI')).select(db.auth_group.id).first()
        if roll_t is not None:
            if roll == 'Super-Administrator' or roll == 'Ecys-Administrator':
                user_p = db((db.auth_user.username == id_user) & (db.auth_user.id == db.auth_membership.user_id)
                        & (db.auth_membership.group_id == roll_t.id)).select(db.auth_user.username).first()
                if user_p is not None:
                    user_p = user_p.username
            else:
                user_p = db((db.auth_membership.group_id == roll_t.id) & (db.auth_membership.user_id == db.auth_user.id)
                        & (db.auth_user.username == id_user) & (db.auth_user.id == db.user_project.assigned_user)
                        & (db.user_project.project == project.id) & (db.user_project.period == db.period_year.id)
                        & ((db.user_project.period <= period.id) & ((db.user_project.period.cast('integer') + db.user_project.periods) > period.id))).select(db.auth_user.username).first()
                if user_p is not None:
                    user_p = user_p.username

        #CHECK IF THE ROLE EXIT IN THE LOGS OF SYSTEM 
        if user_p is None:
            if type_report == 'grades_log':
                user_p = db((db.grades_log.project == project.name) & (db.grades_log.period == T(period.period.name))
                        & (db.grades_log.yearp == period.yearp) & (db.grades_log.roll == roll)
                        & (db.grades_log.user_name == id_user)).select(db.grades_log.user_name).first()
                if user_p is not None:
                    user_p = user_p.user_name
            elif type_report == 'validate_laboratory_log':
                user_p = db((db.validate_laboratory_log.project == project.name) & (db.validate_laboratory_log.period == T(period.period.name))
                        & (db.validate_laboratory_log.yearp == period.yearp) & (db.validate_laboratory_log.roll == roll)
                        & (db.validate_laboratory_log.user_name == id_user)).select(db.validate_laboratory_log.user_name).first()
                if user_p is not None:
                    user_p = user_p.user_name
            else:
                user_p = None
        return user_p
    except:
        return None

@auth.requires_login()
@auth.requires(auth.has_membership('Teacher'))
def get_month_period():
    year = cpfecys.current_year_period()
    vec_month = None
    
    if year.period == 1:
        vec_month = [
            (1, 'Enero', 2),
            (2, 'Febrero', 3),
            (3, 'Marzo', 4),
            (4, 'Abril', 5),
            (5, 'Mayo',6)
        ]
    else:
        vec_month = [
            (6, 'Junio', 7),
            (7, 'Julio', 8),
            (8, 'Agosto', 9),
            (9, 'Septiembre', 10),
            (10, 'Octubre', 11),
            (11, 'Noviembre', 12),
            (12, 'Diciembre', 1)
        ]

    return vec_month