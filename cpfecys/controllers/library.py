import cpfecys

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Academic'))
def file_managers():
    #The list of periods
    def obtain_periods(func):
        if func == 1:
            try:
                academic_var = db.academic(db.academic.id_auth_user == auth.user.id)        
                period_list = db(db.academic_course_assignation.carnet == academic_var.id).select(db.academic_course_assignation.semester, distinct=True)
                periods = period_list
            except:
                periods = []
        else:
            #hacer distincion entre periodos variables y semestres   
            periods = db(((db.user_project.period <= db.period_year.id) & ((db.user_project.period.cast('integer') + db.user_project.periods) > db.period_year.id)) 
                        & (db.user_project.assigned_user == auth.user.id)).select(db.period_year.id, db.period_year.yearp, db.period_year.period, distinct=True)

        return periods
    
    #The list of the projects
    def obtain_projects(func, period):
        if func == 1:
            try:
                academic_var = db.academic(db.academic.id_auth_user == auth.user.id)
                rproject = db((db.academic_course_assignation.carnet == academic_var.id) & (db.academic_course_assignation.semester == period)).select(db.academic_course_assignation.assignation)
            except:
                rproject = []
        else:
            rproject = db((db.user_project.assigned_user == auth.user.id) & ((db.user_project.period <= period) 
                        & ((db.user_project.period.cast('integer') + db.user_project.periods) > period))).select(db.user_project.id, db.user_project.project, db.user_project.period)

        return rproject
    
    #The list of the final students
    def obtain_students(project):
        persons = db((db.user_project.project == project.project) & ((db.user_project.period <= project.period) 
                    & ((db.user_project.period.cast('integer') + db.user_project.periods) > project.period)) & (db.auth_membership.user_id == db.user_project.assigned_user)
                    & (db.auth_membership.group_id == 2)).select(db.user_project.id, db.user_project.assigned_user)

        return persons
    
    #Existe alguna accion
    def existe_registro():
        return True if (session.library_tipo_vars != '0' and session.library_pro_vars != '0') else False

    tipo = None
    pro = None
    grid = None
    
    if request.vars['tipo'] == None:
        if session.library_tipo_vars != None:
            tipo = session.library_tipo_vars
    else:
        tipo = request.vars['tipo']
        session.library_tipo_vars = tipo

    if request.vars['pro'] == None:
        if session.library_pro_vars != None:
            pro = session.library_pro_vars
    else:
        pro = request.vars['pro']
        session.library_pro_vars = pro

    if tipo != None and pro != None:
        if tipo == '5':
            if request.vars['semester'] is not None:
                session.library_semester = request.vars['semester']

            academic_var = db.academic(db.academic.id_auth_user == auth.user.id) 
            project = db((db.academic_course_assignation.carnet == academic_var.id) & (db.academic_course_assignation.assignation == session.library_pro_vars)
                        & (db.academic_course_assignation.semester == session.library_semester)).select(db.academic_course_assignation.assignation, db.academic_course_assignation.semester).first()

            if project is None:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))
            else:
                query = ((db.library.project == project.assignation) & (db.library.period == project.semester)
                        & (db.library.visible == True))
                db.library.period.readable = False
                db.library.project.readable = False
                db.library.visible.readable = False
                db.library.owner_file.readable = False
                grid = SQLFORM.grid(query, csv=False, create=False, editable=False, deletable=False, paginate=9, searchable=False)
                name_project = project.assignation.name
                name_semester = project.semester.period.name
                name_year = project.semester.yearp
                user_nombre = ''
        elif tipo != '0':
            project = int(pro)
            check = db.user_project(id=project)
            year = db.period_year(id=request.vars["semester"])
            year_semester = db.period(id=year.period)
            
            #Obtain the current period of year
            period = cpfecys.current_year_period()

            #Check the fields
            db.library.id.readable = False
            db.library.id.writable = False
            db.library.project.readable = False
            db.library.project.writable = False
            db.library.project.default = check.project
            db.library.period.readable = False
            db.library.period.writable = False
            db.library.period.default = year.id
            db.library.owner_file.writable = False
            db.library.owner_file.readable = False
            db.library.owner_file.default = check.assigned_user

            name_project = check.project.name
            name_semester = T(year_semester.name)
            name_year = year.yearp
            
            rproject = db((db.user_project.assigned_user == auth.user.id) & ((db.user_project.period <= year.id) 
                        & ((db.user_project.period.cast('integer') + db.user_project.periods) > year.id))).select(db.user_project.project)
            this_project = db((db.user_project.id == pro)).select().first()
            none_access = False
            for var_project in rproject:
                if var_project.project.id == this_project.project.id:
                    none_access = True
                    break

            if not none_access:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))

            if tipo == '1':
                user_nombre = check.assigned_user.first_name
                query = ((db.library.owner_file == check.assigned_user) & (db.library.project == check.project)
                        & (db.library.period == year.id))
                if period.id == year.id:
                    grid = SQLFORM.grid(query, csv=False, paginate=9, searchable=False)
                else:
                    links = [lambda row: A('Enlazar Semestre Actual', _href=URL("library", "change_period", vars=dict(semester=request.vars["semester"]), args=[row.id]))]
                    grid = SQLFORM.grid(query, links=links, create=False, editable=False, csv=False, paginate=9, searchable=False)
            elif tipo == '2':
                db.library.owner_file.readable = True
                query = ((db.library.visible == True) & (db.library.owner_file != check.assigned_user)
                        & (db.library.project == check.project) & (db.library.period == year.id))
                grid = SQLFORM.grid(query, csv=False, create=False, editable=False, deletable=False, paginate=9, searchable=False)
                user_nombre = T('Share')
            elif tipo == '3':
                user_nombre = check.assigned_user.first_name
                query = ((db.library.owner_file == check.assigned_user) & (db.library.project == check.project)
                        & (db.library.period == year.id))
                if period.id == year.id:
                    grid = SQLFORM.grid(query, csv=False, paginate=9, searchable=False)
                else:
                    links = [lambda row: A('Enlazar Semestre Actual', _href=URL("library", "change_period", vars=dict(semester=request.vars["semester"]), args=[row.id]))]
                    grid = SQLFORM.grid(query, links=links, create=False, editable=False, csv=False, paginate=9, searchable=False)
            elif tipo == '4':
                user_nombre=check.assigned_user.first_name
                query = ((db.library.owner_file == check.assigned_user) & (db.library.project == check.project)
                        & (db.library.period == year.id))
                grid = SQLFORM.grid(query, csv=False, create=False, editable=False, deletable=False, paginate=9, searchable=False)
            else:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))
        else:
            name_project = ''
            name_semester = ''
            name_year = ''
            user_nombre = ''
    else:
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))

    return dict(
        obtain_periods=obtain_periods, 
        obtain_projects=obtain_projects, 
        obtain_students=obtain_students, 
        existe_registro=existe_registro, 
        grid=grid, 
        name=name_project,
        semester=name_semester,
        year=name_year,
        user_nombre=user_nombre
    )

@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Teacher') or auth.has_membership('Academic'))
def change_period():
    id_file = request.args(0)
    period = cpfecys.current_year_period()

    new_file = db(db.library.id == id_file).select(db.library.project, db.library.owner_file, db.library.name, db.library.file_data, db.library.description, db.library.visible)
    for file in new_file:
        count = db.library.id.count()
        notices  = db((db.library.name == file.name) & (db.library.file_data == file.file_data)
                    & (db.library.description == file.description) & (db.library.visible == file.visible)
                    & (db.library.period == period) & (db.library.project == file.project)
                    & (db.library.owner_file == file.owner_file)).select(count)
        total = 0
        for s in notices:
            total = s[count]

        if total == 0:
            count2 = db.user_project.id.count()
            project2 = db((db.user_project.project == file.project) & (db.user_project.assigned_user == file.owner_file)
                        & ((db.user_project.period <= period) & ((db.user_project.period.cast('integer') + db.user_project.periods) > period))).select(count2)
            total2 = 2
            for s2 in project2:
                total2 = s2[count2]

            if total2 == 1:
                db.library.insert(name=file.name, file_data=file.file_data, description=file.description, visible=file.visible, period=period, project=file.project, owner_file=file.owner_file)
                session.flash = T('The file was copy to the actual semester')
            else:
                session.flash = 'El archivo no se puede copiar, ya que no tiene asignado el curso en el semestre actual'
            redirect(URL('library', 'file_managers', vars=dict(semester=request.vars["semester"])))
        else:
            session.flash = T('The file already exists')
            redirect(URL('library', 'file_managers', vars=dict(semester=request.vars["semester"])))