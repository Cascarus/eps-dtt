from datetime import datetime
import cpfecys


# VALIDATE REPORT
@auth.requires_login()
@auth.requires(auth.has_membership("Super-Administrator") or auth.has_membership("Ecys-Administrator"))
def get_month_period(year):
    vec_month = []

    if year.period == 1:
        vec_month = [
            (1, "Enero", 2),
            (2, "Febrero", 3),
            (3, "Marzo", 4),
            (4, "Abril", 5),
            (5, "Mayo", 6),
        ]
    else:
        vec_month = [
            (6, "Junio", 7),
            (7, "Julio", 8),
            (8, "Agosto", 9),
            (9, "Septiembre", 10),
            (10, "Octubre", 11),
            (11, "Noviembre", 12),
            (12, "Diciembre", 1),
        ]

    return vec_month

@auth.requires_login()
@auth.requires(auth.has_membership("Super-Administrator") or auth.has_membership("Ecys-Administrator"))
def validate_month(month, period):
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
@auth.requires(auth.has_membership("Super-Administrator") or auth.has_membership("Ecys-Administrator"))
def validate_period(period):
    try:
        period = db(db.period_year.id == int(period)).select().first()
        return period
    except:
        return None

@auth.requires_login()
@auth.requires(auth.has_membership("Super-Administrator") or auth.has_membership("Ecys-Administrator"))
def validate_evaluation(evaluation):
    try:
        evaluation = db(db.repository_evaluation.id == int(evaluation)).select().first()
        return evaluation
    except:
        return None

@auth.requires_login()
@auth.requires(auth.has_membership("Super-Administrator") or auth.has_membership("Ecys-Administrator"))
def validate_project(project_i, type_report):
    try:
        # CHECK IN THE LOG IF THE PROJECT EXIST
        flag = False
        if type_report == "grades_log":
            flag = True
            project = db(db.grades_log.project == project_i).select(db.grades_log.project).first()
            if project is not None:
                project = project.project
        elif type_report == "course_activity_log":
            flag = True
            project = db(db.course_activity_log.course == project_i).select(db.course_activity_log.course).first()
            if project is not None:
                project = project.course
        elif type_report == "academic_course_assignation_log":
            flag = True
            project = db((db.academic_course_assignation_log.before_course == project_i) | (db.academic_course_assignation_log.after_course == project_i)).select(
                        db.academic_course_assignation_log.after_course,
                        db.academic_course_assignation_log.before_course
                    ).first()
            if project is not None:
                if project.before_course is not None:
                    project = project.before_course
                else:
                    project = project.after_course
        elif type_report == "requestchange_activity_log":
            flag = True
            project = db(db.requestchange_activity_log.course == project_i).select(db.requestchange_activity_log.course).first()
            if project is not None:
                project = project.course
        elif type_report == "request_change_g_log":
            flag = True
            project = db(db.request_change_g_log.project == project_i).select(db.request_change_g_log.project).first()
            if project is not None:
                project = project.project
        else:
            project = None

        # TYPE OF REPORT CORRECT BUT THE PROJECT IS NOT IN THE LOG
        if project is None and flag:
            area = db(db.area_level.name == "DTT Tutor Académico").select(db.area_level.id).first()
            project = db((db.project.name == project_i) & (db.project.area_level == area.id)).select(db.project.name).first()
            if project is not None:
                project = project.name

        # RETURN PROJECT
        return project
    except:
        return None

@auth.requires_login()
@auth.requires(auth.has_membership("Super-Administrator") or auth.has_membership("Ecys-Administrator"))
def validate_role(name_role, type_report):
    try:
        # CHECK IF THE ROLE EXIST IN THE OFFICIAL ROLES
        roll = db((db.auth_group.role == name_role) & (db.auth_group.role != "Academic")
            & (db.auth_group.role != "DSI")).select(db.auth_group.role).first()   
        if roll is None:
            # CHECK IF THE ROLE EXIT IN THE LOGS OF SYSTEM
            if type_report == "grades_log":
                roll = db((db.grades_log.roll == name_role) & (db.grades_log.roll != "Academic")
                        & (db.grades_log.roll != "DSI")).select(db.grades_log.roll).first()
                if roll is not None:
                    roll = roll.roll
            elif type_report == "course_activity_log":
                roll = db((db.course_activity_log.roll == name_role) & (db.course_activity_log.roll != "Academic")
                    & (db.course_activity_log.roll != "DSI")).select(db.course_activity_log.roll).first()
                if roll is not None:
                    roll = roll.roll
            elif type_report == "academic_log":
                roll = db(db.academic_log.roll.like(f"%{name_role}%")).select(db.academic_log.roll).first()
                if roll is not None:
                    roll = roll.roll
            elif type_report == "academic_course_assignation_log":
                roll = db(db.academic_course_assignation_log.roll.like(f"%{name_role}%")).select(db.academic_course_assignation_log.roll).first()
                if roll is not None:
                    roll = roll.roll
            else:
                roll = None
        else:
            roll = roll.role

        # RETURN ROLE
        return roll
    except:
        return None

@auth.requires_login()
@auth.requires(auth.has_membership("Super-Administrator") or auth.has_membership("Ecys-Administrator"))
def validate_user(period, project, roll, id_user, type_report):
    try:
        # CHECK IF THE USER EXIST IN THE OFFICIAL USERS
        user_p = None
        roll_t = db((db.auth_group.role == roll) & (db.auth_group.role != "Academic")
                & (db.auth_group.role != "DSI")).select(db.auth_group.id).first()
        if roll_t is not None:
            if roll == "Super-Administrator" or roll == "Ecys-Administrator":
                user_p = db((db.auth_user.username == id_user) & (db.auth_user.id == db.auth_membership.user_id)
                        & (db.auth_membership.group_id == roll_t.id)).select(db.auth_user.username).first()
                if user_p is not None:
                    user_p = user_p.username
            else:
                if type_report != "academic_log":
                    project_t = db(db.project.name == project).select().first()
                    if project_t is not None:
                        user_p = db((db.auth_membership.group_id == roll_t.id) & (db.auth_membership.user_id == db.auth_user.id)
                                & (db.auth_user.username == id_user) & (db.auth_user.id == db.user_project.assigned_user)
                                & (db.user_project.project == project_t.id) & (db.user_project.period == db.period_year.id)
                                & ((db.user_project.period <= period.id) & ((db.user_project.period.cast('integer') + db.user_project.periods) > period.id))).select(db.auth_user.username).first()
                        
                        if user_p is not None:
                            user_p = user_p.username
                else:
                    user_p = db((db.auth_membership.group_id == roll_t.id) & (db.auth_membership.user_id == db.auth_user.id)
                            & (db.auth_user.username == id_user) & (db.auth_user.id == db.user_project.assigned_user)
                            & (db.user_project.period == db.period_year.id) & ((db.user_project.period <= period.id)
                            & ((db.user_project.period.cast('integer') + db.user_project.periods) > period.id))).select(db.auth_user.username).first()
                    if user_p is not None:
                        user_p = user_p.username

        # CHECK IF THE ROLE EXIT IN THE LOGS OF SYSTEM
        if user_p is None:
            if type_report == "grades_log":
                user_p = db((db.grades_log.project == project) & (db.grades_log.period == T(period.period.name))
                        & (db.grades_log.yearp == period.yearp) & (db.grades_log.roll == roll)
                        & (db.grades_log.user_name == id_user)).select(db.grades_log.user_name).first()
                if user_p is not None:
                    user_p = user_p.user_name
            elif type_report == "course_activity_log":
                user_p = db((db.course_activity_log.course == project) & (db.course_activity_log.period == T(period.period.name))
                        & (db.course_activity_log.yearp == period.yearp) & (db.course_activity_log.roll == roll)
                        & (db.course_activity_log.user_name == id_user)).select(db.course_activity_log.user_name).first()
                
                if user_p is not None:
                    user_p = user_p.user_name
            elif type_report == "academic_log":
                user_p = db((db.academic_log.id_period == period.id) & (db.academic_log.roll.like(f"%{roll}%"))
                        & (db.academic_log.user_name == id_user)).select(db.academic_log.user_name).first()
                if user_p is not None:
                    user_p = user_p.user_name
            elif type_report == "academic_course_assignation_log":
                user_p = db((db.academic_course_assignation_log.id_period == period.id) & ((db.academic_course_assignation_log.before_course == project)
                        | (db.academic_course_assignation_log.after_course == project)) & (db.academic_course_assignation_log.roll.like(f"%{roll}%"))
                        & (db.academic_course_assignation_log.user_name == id_user)).select(db.academic_course_assignation_log.user_name).first()
                if user_p is not None:
                    user_p = user_p.user_name
            elif type_report == "requestchange_activity_log":
                user_p = db((db.requestchange_activity_log.course == project) & (db.requestchange_activity_log.semester == period.period.name)
                        & (db.requestchange_activity_log.yearp == period.yearp) & (db.requestchange_activity_log.roll_request == roll)
                        & (db.requestchange_activity_log.user_request == id_user)).select(db.requestchange_activity_log.user_request).first()
                if user_p is not None:
                    user_p = user_p.user_request
            elif type_report == "request_change_g_log":
                user_p = db((db.request_change_g_log.project == project) & (db.request_change_g_log.semester == T(period.period.name))
                        & (db.request_change_g_log.yearp == period.yearp) & (db.request_change_g_log.roll == roll)
                        & (db.request_change_g_log.username == id_user)).select(db.request_change_g_log.username).first()
                if user_p is not None:
                    user_p = user_p.username
            else:
                user_p = None
        return user_p
    except:
        return None

# GROUP OF INFORMATION
@auth.requires_login()
@auth.requires(auth.has_membership("Super-Administrator") or auth.has_membership("Ecys-Administrator"))
def get_years():
    return [period.yearp for period in db(db.period_year).select(db.period_year.yearp, distinct=True)]

@auth.requires_login()
@auth.requires(auth.has_membership("Super-Administrator") or auth.has_membership("Ecys-Administrator"))
def get_projects(type_report, period):
    projects = []
    # OFFICIAL PROJECTS
    area = db(db.area_level.name == "DTT Tutor Académico").select(db.area_level.id).first()
    if area is not None:
        if period is None:
            for project in db(db.project.area_level == area.id).select(
                db.project.name.with_alias("name"),
                distinct=True,
                orderby=db.project.name,
            ):
                projects.append(project.name)
        else:
            for project in db(
                (db.project.area_level == area.id)
                & (db.user_project.project == db.project.id)
                & (db.user_project.period == db.period_year.id)
                & (
                    (db.user_project.period <= period.id)
                    & ((db.user_project.period.cast('integer') + db.user_project.periods) > period.id)
                )
            ).select(
                db.project.name.with_alias("name"),
                distinct=True,
                orderby=db.project.name,
            ):
                projects.append(project.name)

    # PROJECTS IN LOGS
    if type_report == "grades_log":
        if len(projects) == 0:
            if period is None:
                projects_temp = db(db.grades_log).select(
                    db.grades_log.project.with_alias("name"), distinct=True
                )
            else:
                projects_temp = db(
                    (db.grades_log.period == T(period.period.name))
                    & (db.grades_log.yearp == str(period.yearp))
                ).select(db.grades_log.project.with_alias("name"), distinct=True)
        else:
            if period is None:
                projects_temp = db(~db.grades_log.project.belongs(projects)).select(
                    db.grades_log.project.with_alias("name"), distinct=True
                )
            else:
                projects_temp = db(
                    (db.grades_log.period == T(period.period.name))
                    & (db.grades_log.yearp == str(period.yearp))
                    & (~db.grades_log.project.belongs(projects))
                ).select(db.grades_log.project.with_alias("name"), distinct=True)
        for project in projects_temp:
            projects.append(project.name)
    elif type_report == "course_activity_log":
        if len(projects) == 0:
            if period is None:
                projects_temp = db(db.course_activity_log).select(
                    db.course_activity_log.course.with_alias("name"), distinct=True
                )
            else:
                projects_temp = db(
                    (db.course_activity_log.period == T(period.period.name))
                    & (db.course_activity_log.yearp == str(period.yearp))
                ).select(
                    db.course_activity_log.course.with_alias("name"), distinct=True
                )
        else:
            if period is None:
                projects_temp = db(
                    ~db.course_activity_log.course.belongs(projects)
                ).select(
                    db.course_activity_log.course.with_alias("name"), distinct=True
                )
            else:
                projects_temp = db(
                    (db.course_activity_log.period == T(period.period.name))
                    & (db.course_activity_log.yearp == str(period.yearp))
                    & (~db.course_activity_log.course.belongs(projects))
                ).select(
                    db.course_activity_log.course.with_alias("name"), distinct=True
                )
        for project in projects_temp:
            projects.append(project.name)
    elif type_report == "academic_course_assignation_log":
        if len(projects) == 0:
            if period is None:
                projects_temp = db(db.academic_course_assignation_log).select(
                    db.academic_course_assignation_log.before_course.with_alias("name"),
                    distinct=True,
                )
            else:
                projects_temp = db(
                    db.academic_course_assignation_log.id_period == str(period.id)
                ).select(
                    db.academic_course_assignation_log.before_course.with_alias("name"),
                    distinct=True,
                )
        else:
            if period is None:
                projects_temp = db(
                    ~db.academic_course_assignation_log.before_course.belongs(projects)
                ).select(
                    db.academic_course_assignation_log.before_course.with_alias("name"),
                    distinct=True,
                )
            else:
                projects_temp = db(
                    (db.academic_course_assignation_log.id_period == str(period.id))
                    & (
                        ~db.academic_course_assignation_log.before_course.belongs(
                            projects
                        )
                    )
                ).select(
                    db.academic_course_assignation_log.before_course.with_alias("name"),
                    distinct=True,
                )
        for project in projects_temp:
            projects.append(project.name)

        if len(projects) == 0:
            if period is None:
                projects_temp = db(db.academic_course_assignation_log).select(
                    db.academic_course_assignation_log.after_course.with_alias("name"),
                    distinct=True,
                )
            else:
                projects_temp = db(
                    db.academic_course_assignation_log.id_period == str(period.id)
                ).select(
                    db.academic_course_assignation_log.after_course.with_alias("name"),
                    distinct=True,
                )
        else:
            if period is None:
                projects_temp = db(
                    ~db.academic_course_assignation_log.after_course.belongs(projects)
                ).select(
                    db.academic_course_assignation_log.after_course.with_alias("name"),
                    distinct=True,
                )
            else:
                projects_temp = db(
                    (db.academic_course_assignation_log.id_period == str(period.id))
                    & (
                        ~db.academic_course_assignation_log.after_course.belongs(
                            projects
                        )
                    )
                ).select(
                    db.academic_course_assignation_log.after_course.with_alias("name"),
                    distinct=True,
                )
        for project in projects_temp:
            projects.append(project.name)
    elif type_report == "requestchange_activity_log":
        if len(projects) == 0:
            if period is None:
                projects_temp = db(db.requestchange_activity_log).select(
                    db.requestchange_activity_log.course.with_alias("name"),
                    distinct=True,
                )
            else:
                projects_temp = db(
                    (db.requestchange_activity_log.semester == period.period.name)
                    & (db.requestchange_activity_log.yearp == str(period.yearp))
                ).select(
                    db.requestchange_activity_log.course.with_alias("name"),
                    distinct=True,
                )
        else:
            if period is None:
                projects_temp = db(
                    ~db.requestchange_activity_log.course.belongs(projects)
                ).select(
                    db.requestchange_activity_log.course.with_alias("name"),
                    distinct=True,
                )
            else:
                projects_temp = db(
                    (db.requestchange_activity_log.semester == period.period.name)
                    & (db.requestchange_activity_log.yearp == str(period.yearp))
                    & (~db.requestchange_activity_log.course.belongs(projects))
                ).select(
                    db.requestchange_activity_log.course.with_alias("name"),
                    distinct=True,
                )
        for project in projects_temp:
            projects.append(project.name)
    elif type_report == "request_change_g_log":
        if len(projects) == 0:
            if period is None:
                projects_temp = db(db.request_change_g_log).select(
                    db.request_change_g_log.project.with_alias("name"), distinct=True
                )
            else:
                projects_temp = db(
                    (db.request_change_g_log.semester == T(period.period.name))
                    & (db.request_change_g_log.yearp == str(period.yearp))
                ).select(
                    db.request_change_g_log.project.with_alias("name"), distinct=True
                )
        else:
            if period is None:
                projects_temp = db(
                    ~db.request_change_g_log.project.belongs(projects)
                ).select(
                    db.request_change_g_log.project.with_alias("name"), distinct=True
                )
            else:
                projects_temp = db(
                    (db.request_change_g_log.semester == T(period.period.name))
                    & (db.request_change_g_log.yearp == str(period.yearp))
                    & (~db.request_change_g_log.project.belongs(projects))
                ).select(
                    db.request_change_g_log.project.with_alias("name"), distinct=True
                )
        for project in projects_temp:
            projects.append(project.name)
    else:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))
    return projects

@auth.requires_login()
@auth.requires(auth.has_membership("Super-Administrator") or auth.has_membership("Ecys-Administrator"))
def get_roles(type_report):
    roles = []
    # OFFICIAL ROLES
    for roll in db(
        (db.auth_group.role != "Academic") & (db.auth_group.role != "DSI")
    ).select(db.auth_group.role.with_alias("roll"), distinct=True):
        roles.append(roll.roll)

    # ROLES IN LOGS
    if type_report == "grades_log":
        if len(roles) == 0:
            roles_temp = db(
                (db.grades_log.roll != "Academic") & (db.grades_log.roll != "DSI")
            ).select(db.grades_log.roll.with_alias("roll"), distinct=True)
        else:
            roles_temp = db(
                ~db.grades_log.roll.belongs(roles)
                & (db.grades_log.roll != "Academic")
                & (db.grades_log.roll != "DSI")
            ).select(db.grades_log.roll.with_alias("roll"), distinct=True)
        for roll in roles_temp:
            roles.append(roll.roll)
    elif type_report == "course_activity_log":
        if len(roles) == 0:
            roles_temp = db(
                (db.course_activity_log.roll != "Academic")
                & (db.course_activity_log.roll != "DSI")
            ).select(db.course_activity_log.roll.with_alias("roll"), distinct=True)
        else:
            roles_temp = db(
                ~db.course_activity_log.roll.belongs(roles)
                & (db.course_activity_log.roll != "Academic")
                & (db.course_activity_log.roll != "DSI")
            ).select(db.course_activity_log.roll.with_alias("roll"), distinct=True)
        for roll in roles_temp:
            roles.append(roll.roll)
    elif type_report == "academic_log":
        roles.append("system")
        roles_temp = db(
            ~db.academic_log.roll.belongs(roles)
            & (db.academic_log.roll != "Academic")
            & (db.academic_log.roll != "DSI")
        ).select(db.academic_log.roll.with_alias("roll"), distinct=True)
        for roll in roles_temp:
            roles.append(roll.roll)
    elif type_report == "academic_course_assignation_log":
        if len(roles) == 0:
            roles_temp = db(
                (db.academic_course_assignation_log.roll != "Academic")
                & (db.academic_course_assignation_log.roll != "DSI")
            ).select(
                db.academic_course_assignation_log.roll.with_alias("roll"),
                distinct=True,
            )
        else:
            roles_temp = db(
                ~db.academic_course_assignation_log.roll.belongs(roles)
                & (db.academic_course_assignation_log.roll != "Academic")
                & (db.academic_course_assignation_log.roll != "DSI")
            ).select(
                db.academic_course_assignation_log.roll.with_alias("roll"),
                distinct=True,
            )
        for roll in roles_temp:
            roles.append(roll.roll)
    else:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))
    return roles

@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator")
    or auth.has_membership("Ecys-Administrator")
)
def get_users(period, project, roll, type_report):
    users_project = []
    # OFFICIAL USERS
    roll_t = (
        db(
            (db.auth_group.role == roll)
            & (db.auth_group.role != "Academic")
            & (db.auth_group.role != "DSI")
        )
        .select()
        .first()
    )
    if roll_t is not None:
        if roll == "Super-Administrator" or roll == "Ecys-Administrator":
            for user_t in db(
                (db.auth_user.id == db.auth_membership.user_id)
                & (db.auth_membership.group_id == roll_t.id)
            ).select(db.auth_user.ALL):
                users_project.append(user_t.username)
        else:
            if type_report != "academic_log" and type_report != "evaluation_result":
                project_t = db(db.project.name == project).select().first()
                if project_t is not None:
                    for user_t in db(
                        (db.auth_membership.group_id == roll_t.id)
                        & (db.auth_membership.user_id == db.auth_user.id)
                        & (db.auth_user.id == db.user_project.assigned_user)
                        & (db.user_project.project == project_t.id)
                        & (db.user_project.period == db.period_year.id)
                        & (
                            (db.user_project.period <= period.id)
                            & (
                                (db.user_project.period.cast('integer') + db.user_project.periods)
                                > period.id
                            )
                        )
                    ).select(db.auth_user.ALL):
                        users_project.append(user_t.username)
            else:
                for user_t in db(
                    (db.auth_membership.group_id == roll_t.id)
                    & (db.auth_membership.user_id == db.auth_user.id)
                    & (db.auth_user.id == db.user_project.assigned_user)
                    & (db.user_project.period == db.period_year.id)
                    & (
                        (db.user_project.period <= period.id)
                        & (
                            (db.user_project.period.cast('integer') + db.user_project.periods)
                            > period.id
                        )
                    )
                ).select(db.auth_user.ALL, distinct=True):
                    users_project.append(user_t.username)

    # USERS IN LOGS
    if type_report == "grades_log":
        if len(users_project) == 0:
            users_project_t = db(
                (db.grades_log.project == project)
                & (db.grades_log.period == T(period.period.name))
                & (db.grades_log.yearp == period.yearp)
                & (db.grades_log.roll == roll)
            ).select(db.grades_log.user_name, distinct=True)
        else:
            users_project_t = db(
                (db.grades_log.project == project)
                & (db.grades_log.period == T(period.period.name))
                & (db.grades_log.yearp == period.yearp)
                & (db.grades_log.roll == roll)
                & (~db.grades_log.user_name.belongs(users_project))
            ).select(db.grades_log.user_name, distinct=True)
        for user_t in users_project_t:
            users_project.append(user_t.user_name)
    elif type_report == "course_activity_log":
        if len(users_project) == 0:
            users_project_t = db(
                (db.course_activity_log.course == project)
                & (db.course_activity_log.period == T(period.period.name))
                & (db.course_activity_log.yearp == period.yearp)
                & (db.course_activity_log.roll == roll)
            ).select(db.course_activity_log.user_name, distinct=True)
        else:
            users_project_t = db(
                (db.course_activity_log.course == project)
                & (db.course_activity_log.period == T(period.period.name))
                & (db.course_activity_log.yearp == period.yearp)
                & (db.course_activity_log.roll == roll)
                & (~db.course_activity_log.user_name.belongs(users_project))
            ).select(db.course_activity_log.user_name, distinct=True)
        for user_t in users_project_t:
            users_project.append(user_t.user_name)
    elif type_report == "academic_log":
        if len(users_project) == 0:
            users_project_t = db(
                (db.academic_log.id_period == period.id)
                & (db.academic_log.roll.like("%" + str(roll) + "%"))
            ).select(db.academic_log.user_name, distinct=True)
        else:
            users_project_t = db(
                (db.academic_log.id_period == period.id)
                & (db.academic_log.roll.like("%" + str(roll) + "%"))
                & (~db.academic_log.user_name.belongs(users_project))
            ).select(db.academic_log.user_name, distinct=True)
        for user_t in users_project_t:
            users_project.append(user_t.user_name)
    elif type_report == "academic_course_assignation_log":
        if len(users_project) == 0:
            users_project_t = db(
                (db.academic_course_assignation_log.id_period == period.id)
                & (
                    (db.academic_course_assignation_log.before_course == project)
                    | (db.academic_course_assignation_log.after_course == project)
                )
                & (db.academic_course_assignation_log.roll.like("%" + str(roll) + "%"))
            ).select(db.academic_course_assignation_log.user_name, distinct=True)
        else:
            users_project_t = db(
                (db.academic_course_assignation_log.id_period == period.id)
                & (
                    (db.academic_course_assignation_log.before_course == project)
                    | (db.academic_course_assignation_log.after_course == project)
                )
                & (db.academic_course_assignation_log.roll.like("%" + str(roll) + "%"))
                & (~db.academic_course_assignation_log.user_name.belongs(users_project))
            ).select(db.academic_course_assignation_log.user_name, distinct=True)
        for user_t in users_project_t:
            users_project.append(user_t.user_name)
    elif type_report == "evaluation_result":
        condition = ""
        for user_t_t in users_project:
            if condition == "":
                condition = 'and academic_log.user_name != "' + user_t_t + '"'
            else:
                condition = (
                    condition + ' and academic_log.user_name != "' + user_t_t + '"'
                )
        search_t = (
            'academic_log.id_period = "'
            + str(period.id)
            + '" and academic_log.roll contains "'
            + str(roll)
            + '" '
            + condition
        )
        for user_t in db.smart_query(db.academic_log, search_t).select(
            db.academic_log.user_name, distinct=True
        ):
            users_project.append(user_t.user_name)
    elif type_report == "requestchange_activity_log":
        if len(users_project) == 0:
            users_project_t = db(
                (db.requestchange_activity_log.course == project)
                & (db.requestchange_activity_log.semester == period.period.name)
                & (db.requestchange_activity_log.yearp == period.yearp)
                & (db.requestchange_activity_log.roll_request == roll)
            ).select(db.requestchange_activity_log.user_request, distinct=True)
        else:
            users_project_t = db(
                (db.requestchange_activity_log.course == project)
                & (db.requestchange_activity_log.semester == period.period.name)
                & (db.requestchange_activity_log.yearp == period.yearp)
                & (db.requestchange_activity_log.roll_request == roll)
                & (~db.requestchange_activity_log.user_request.belongs(users_project))
            ).select(db.requestchange_activity_log.user_request, distinct=True)
        for user_t in users_project_t:
            users_project.append(user_t.user_request)
    elif type_report == "request_change_g_log":
        if len(users_project) == 0:
            users_project_t = db(
                (db.request_change_g_log.project == project)
                & (db.request_change_g_log.semester == T(period.period.name))
                & (db.request_change_g_log.yearp == period.yearp)
                & (db.request_change_g_log.roll == roll)
            ).select(db.request_change_g_log.username, distinct=True)
        else:
            users_project_t = db(
                (db.request_change_g_log.project == project)
                & (db.request_change_g_log.semester == T(period.period.name))
                & (db.request_change_g_log.yearp == period.yearp)
                & (db.request_change_g_log.roll == roll)
                & (~db.request_change_g_log.username.belongs(users_project))
            ).select(db.request_change_g_log.username, distinct=True)
        for user_t in users_project_t:
            users_project.append(user_t.username)
    else:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))
    return users_project


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator")
    or auth.has_membership("Ecys-Administrator")
)
def get_categories(type_report):
    categories = []
    # OFFICIAL CATEGORIES
    for category in db(db.activity_category).select(
        db.activity_category.category, distinct=True
    ):
        categories.append(category.category)

    # CATEGORIES IN LOGS
    if type_report == "grades_log":
        if len(categories) == 0:
            categories_temp = db(db.grades_log).select(
                db.grades_log.category, distinct=True
            )
        else:
            categories_temp = db(~db.grades_log.category.belongs(categories)).select(
                db.grades_log.category, distinct=True
            )
        for category in categories_temp:
            categories.append(category.category)
    elif type_report == "course_activity_log":
        if len(categories) == 0:
            categories_temp = db(db.course_activity_log).select(
                db.course_activity_log.before_course_activity_category, distinct=True
            )
        else:
            categories_temp = db(
                (
                    ~db.course_activity_log.before_course_activity_category.belongs(
                        categories
                    )
                )
            ).select(
                db.course_activity_log.before_course_activity_category, distinct=True
            )
        for category in categories_temp:
            categories.append(category.before_course_activity_category)

        if len(categories) == 0:
            categories_temp = db(db.course_activity_log).select(
                db.course_activity_log.after_course_activity_category, distinct=True
            )
        else:
            categories_temp = db(
                (
                    ~db.course_activity_log.after_course_activity_category.belongs(
                        categories
                    )
                )
            ).select(
                db.course_activity_log.after_course_activity_category, distinct=True
            )
        for category in categories_temp:
            categories.append(category.after_course_activity_category)
    elif type_report == "requestchange_activity_log":
        if len(categories) == 0:
            categories_temp = db(db.requestchange_activity_log).select(
                db.requestchange_activity_log.category_request, distinct=True
            )
        else:
            categories_temp = db(
                ~db.requestchange_activity_log.category_request.belongs(categories)
            ).select(db.requestchange_activity_log.category_request, distinct=True)
        for category in categories_temp:
            categories.append(category.category_request)
    elif type_report == "request_change_g_log":
        if len(categories) == 0:
            categories_temp = db(db.request_change_g_log).select(
                db.request_change_g_log.category, distinct=True
            )
        else:
            categories_temp = db(
                ~db.request_change_g_log.category.belongs(categories)
            ).select(db.request_change_g_log.category, distinct=True)
        for category in categories_temp:
            categories.append(category.category)
    else:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))
    return categories


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator")
    or auth.has_membership("Ecys-Administrator")
)
def get_activities(type_report):
    activities = []
    # OFFICIAL CATEGORIES
    for activity in db(db.course_activity).select(
        db.course_activity.name, distinct=True
    ):
        activities.append(activity.name)

    # ACTIVITIES IN LOGS
    if type_report == "grades_log":
        if len(activities) == 0:
            activities_temp = db(db.grades_log).select(
                db.grades_log.activity, distinct=True
            )
        else:
            activities_temp = db(~db.grades_log.activity.belongs(activities)).select(
                db.grades_log.activity, distinct=True
            )
        for activity in activities_temp:
            activities.append(activity.activity)
    elif type_report == "course_activity_log":
        if len(activities) == 0:
            activities_temp = db(db.course_activity_log).select(
                db.course_activity_log.before_name, distinct=True
            )
        else:
            activities_temp = db(
                (~db.course_activity_log.before_name.belongs(activities))
            ).select(db.course_activity_log.before_name, distinct=True)
        for activity in activities_temp:
            activities.append(activity.before_name)

        if len(activities) == 0:
            activities_temp = db(db.course_activity_log).select(
                db.course_activity_log.after_name, distinct=True
            )
        else:
            activities_temp = db(
                (~db.course_activity_log.after_name.belongs(activities))
            ).select(db.course_activity_log.after_name, distinct=True)
        for activity in activities_temp:
            activities.append(activity.after_name)
    elif type_report == "request_change_g_log":
        if len(activities) == 0:
            activities_temp = db(db.request_change_g_log).select(
                db.request_change_g_log.activity, distinct=True
            )
        else:
            activities_temp = db(
                ~db.request_change_g_log.activity.belongs(activities)
            ).select(db.request_change_g_log.activity, distinct=True)
        for activity in activities_temp:
            activities.append(activity.activity)
    else:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))
    return activities


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator")
    or auth.has_membership("Ecys-Administrator")
)
def get_descriptions(type_report):
    descriptions = []
    # ROLES IN LOGS
    if type_report == "grades_log":
        for description in db(db.grades_log).select(
            db.grades_log.description, distinct=True
        ):
            descriptions.append(description.description)
    elif type_report == "academic_log":
        for description in db(db.academic_log).select(
            db.academic_log.description, distinct=True
        ):
            descriptions.append(description.description)
    elif type_report == "academic_course_assignation_log":
        for description in db(db.academic_course_assignation_log).select(
            db.academic_course_assignation_log.description, distinct=True
        ):
            descriptions.append(description.description)
    else:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))
    return descriptions


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator")
    or auth.has_membership("Ecys-Administrator")
)
def get_dates(type_report):
    dates = []
    # ROLES IN LOGS
    if type_report == "grades_log":
        for dat in db(db.grades_log).select(db.grades_log.date_log, distinct=True):
            dates.append(dat.date_log)
    elif type_report == "course_activity_log":
        for dat in db(db.course_activity_log).select(
            db.course_activity_log.date_log, distinct=True
        ):
            dates.append(dat.date_log)
    elif type_report == "academic_log":
        for dat in db(db.academic_log).select(db.academic_log.date_log, distinct=True):
            dates.append(dat.date_log)
    elif type_report == "academic_course_assignation_log":
        for dat in db(db.academic_course_assignation_log).select(
            db.academic_course_assignation_log.date_log, distinct=True
        ):
            dates.append(dat.date_log)
    elif type_report == "requestchange_activity_log":
        for dat in db(db.requestchange_activity_log).select(
            db.requestchange_activity_log.date_request, distinct=True
        ):
            dates.append(dat.date_request)
    elif type_report == "request_change_g_log":
        for dat in db(db.request_change_g_log).select(
            db.request_change_g_log.date_request, distinct=True
        ):
            dates.append(dat.date_request)
    else:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))
    return dates


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator")
    or auth.has_membership("Ecys-Administrator")
)
def get_evaluations(period):
    years = []
    for period in db(db.period_year).select(db.period_year.yearp, distinct=True):
        years.append(period.yearp)
    return years


#*************************************************************************************************************************************
#*************************************************************************************************************************************
#*****************************************************MANAGEMENT REPORT GRADES********************************************************


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def grades_management_export():
    # VERIFI THAT ACCURATE PARAMETERS
    try:
        # CHECK IF THE TYPE OF EXPORT IS VALID
        if request.vars["list_type"] is None or str(request.vars["list_type"]) != "csv":
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))

        # CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars["level"] is not None and (
            int(request.vars["level"]) < 1 or int(request.vars["level"]) > 6
        ):
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(URL("default", "home"))

        # VERIFY THAT THE PARAMETERS OF EACH LEVEL BE VALID
        if request.vars["level"] is not None:
            # LEVEL MORE THAN 1
            if int(request.vars["level"]) > 1:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_L"] is None or (
                    str(request.vars["type_L"]) != "all"
                    and str(request.vars["type_L"]) != "i"
                    and str(request.vars["type_L"]) != "u"
                    and str(request.vars["type_L"]) != "d"
                ):
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

                period = validate_period(request.vars["period"])
                if period is None:
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 2
            if int(request.vars["level"]) > 2:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_U"] is None or (
                    str(request.vars["type_U"]) != "all"
                    and str(request.vars["type_U"]) != "i"
                    and str(request.vars["type_U"]) != "u"
                    and str(request.vars["type_U"]) != "d"
                ):
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

                # CHECK IF THE MONTH IS VALID
                month = validate_month(request.vars["month"], period)
                if month is None:
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 3
            if int(request.vars["level"]) > 3:
                # CHECK IF THE PROJECT IS VALID
                project = validate_project(request.vars["project"], "grades_log")
                if project is None:
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 4
            if int(request.vars["level"]) > 4:
                # CHECK IF THE ROLE IS VALID
                roll = validate_role(request.vars["roll"], "grades_log")
                if roll is None:
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 5
            if int(request.vars["level"]) > 5:
                # CHECK IF THE USER IS VALID
                user_p = validate_user(
                    period, project, roll, request.vars["userP"], "grades_log"
                )
                if user_p is None:
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))
    except:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    # CHECK IF THERE IS A PERSONALIZED QUERY
    personal_query = ""
    if (
        request.vars["querySearch"] is not None
        and str(request.vars["querySearch"]) != ""
    ):
        # PERSONALIZED QUERY SURE WORK
        try:
            personal_query = str(request.vars["querySearch"])
            count_i = db.smart_query(db.grades_log, personal_query).count()
        except:
            personal_query = ""

    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # *****************************************************REPORT*****************************************************

    # TITLE
    info_level = []
    infoe_level_temp = []
    infoe_level_temp.append("Universidad de San Carlos de Guatemala")
    info_level.append(infoe_level_temp)
    infoe_level_temp = []
    infoe_level_temp.append("Facultad de Ingeniería")
    info_level.append(infoe_level_temp)
    infoe_level_temp = []
    infoe_level_temp.append("Escuela de Ciencias y Sistemas")
    info_level.append(infoe_level_temp)
    # TYPE OF REPORT
    infoe_level_temp = []
    infoe_level_temp.append(T("Type"))
    infoe_level_temp.append(T("Grades Management"))
    info_level.append(infoe_level_temp)
    # DESCRIPTION OF REPORT
    infoe_level_temp = []
    infoe_level_temp.append(T("Description"))
    infoe_level_temp.append(T("Report of transactions on the notes of students"))
    info_level.append(infoe_level_temp)
    # LEVELS OF REPORT
    # ALL SEMESTERS
    if (
        request.vars["level"] is None or str(request.vars["level"]) == "1"
    ):  # ALL SEMESTERS
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T("Total inserted"))
        infoe_level_temp.append(T("Total modified"))
        infoe_level_temp.append(T("Total out"))
        info_level.append(infoe_level_temp)
        for period in db(db.period_year).select(orderby=~db.period_year.id):
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # INSERT
            if personal_query == "":
                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.operation_log = "insert"'
                )
            else:
                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.operation_log = "insert" and '
                    + personal_query
                )
            count_i = db.smart_query(db.grades_log, search).count()
            infoe_level_temp.append(count_i)
            # UPDATE
            if personal_query == "":
                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.operation_log = "update"'
                )
            else:
                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.operation_log = "update" and '
                    + personal_query
                )
            count_i = db.smart_query(db.grades_log, search).count()
            infoe_level_temp.append(count_i)
            # DELETE
            if personal_query == "":
                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.operation_log = "delete"'
                )
            else:
                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.operation_log = "delete" and '
                    + personal_query
                )
            count_i = db.smart_query(db.grades_log, search).count()
            infoe_level_temp.append(count_i)
            # INSERT PERIOD
            info_level.append(infoe_level_temp)
    # PER MONTH
    elif str(request.vars["level"]) == "2":
        # PERIOD OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "i":
            infoe_level_temp.append(T("Total inserted"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "u":
            infoe_level_temp.append(T("Total modified"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "d":
            infoe_level_temp.append(T("Total out"))
        info_level.append(infoe_level_temp)

        for month in get_month_period(period):
            start = datetime.strptime(
                str(period.yearp) + "-" + str(month[0]) + "-01", "%Y-%m-%d"
            )
            if month[2] == 1:
                end = datetime.strptime(
                    str(period.yearp + 1) + "-" + str(month[2]) + "-01", "%Y-%m-%d"
                )
            else:
                end = datetime.strptime(
                    str(period.yearp) + "-" + str(month[2]) + "-01", "%Y-%m-%d"
                )
            infoe_level_temp = []
            # NAME OF MONTH
            infoe_level_temp.append(month[1] + " " + str(period.yearp))
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'grades_log.period = "'
                        + T(period.period.name)
                        + '" and grades_log.yearp = "'
                        + str(period.yearp)
                        + '" and grades_log.operation_log = "insert" and grades_log.date_log >="'
                        + str(start)
                        + '" and grades_log.date_log<"'
                        + str(end)
                        + '"'
                    )
                else:
                    search = (
                        'grades_log.period = "'
                        + T(period.period.name)
                        + '" and grades_log.yearp = "'
                        + str(period.yearp)
                        + '" and grades_log.operation_log = "insert" and grades_log.date_log >="'
                        + str(start)
                        + '" and grades_log.date_log<"'
                        + str(end)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.grades_log, search).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'grades_log.period = "'
                        + T(period.period.name)
                        + '" and grades_log.yearp = "'
                        + str(period.yearp)
                        + '" and grades_log.operation_log = "update" and grades_log.date_log>="'
                        + str(start)
                        + '" and grades_log.date_log<"'
                        + str(end)
                        + '"'
                    )
                else:
                    search = (
                        'grades_log.period = "'
                        + T(period.period.name)
                        + '" and grades_log.yearp = "'
                        + str(period.yearp)
                        + '" and grades_log.operation_log = "update" and grades_log.date_log>="'
                        + str(start)
                        + '" and grades_log.date_log<"'
                        + str(end)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.grades_log, search).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'grades_log.period = "'
                        + T(period.period.name)
                        + '" and grades_log.yearp = "'
                        + str(period.yearp)
                        + '" and grades_log.operation_log = "delete" and grades_log.date_log>="'
                        + str(start)
                        + '" and grades_log.date_log<"'
                        + str(end)
                        + '"'
                    )
                else:
                    search = (
                        'grades_log.period = "'
                        + T(period.period.name)
                        + '" and grades_log.yearp = "'
                        + str(period.yearp)
                        + '" and grades_log.operation_log = "delete" and grades_log.date_log>="'
                        + str(start)
                        + '" and grades_log.date_log<"'
                        + str(end)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.grades_log, search).count()
                infoe_level_temp.append(count_i)
            # INSERT MONTH
            info_level.append(infoe_level_temp)
    # PER PROJECT
    elif str(request.vars["level"]) == "3":
        # PROJECTS
        # projects = get_projects('grades_log')
        try:
            projects = get_projects("grades_log", period)
        except:
            projects = get_projects("grades_log", None)
        projects = sorted(projects)
        # PERIOD OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MONTH OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        infoe_level_temp.append(str(month[0]))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Project"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "i":
            infoe_level_temp.append(T("Total inserted"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "u":
            infoe_level_temp.append(T("Total modified"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "d":
            infoe_level_temp.append(T("Total out"))
        info_level.append(infoe_level_temp)

        for projectT in projects:
            project = db(db.project.name == projectT).select().first()
            if project is None:
                project = db(db.grades_log.project == projectT).select().first()
                project = project.project
            else:
                project = project.name
            infoe_level_temp = []
            # NAME OF PROJECT
            infoe_level_temp.append(project)
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'grades_log.period = "'
                        + T(period.period.name)
                        + '" and grades_log.yearp = "'
                        + str(period.yearp)
                        + '" and grades_log.operation_log = "insert" and grades_log.date_log >="'
                        + str(month[1])
                        + '" and grades_log.date_log<"'
                        + str(month[2])
                        + '" and grades_log.project ="'
                        + project
                        + '"'
                    )
                else:
                    search = (
                        'grades_log.period = "'
                        + T(period.period.name)
                        + '" and grades_log.yearp = "'
                        + str(period.yearp)
                        + '" and grades_log.operation_log = "insert" and grades_log.date_log >="'
                        + str(month[1])
                        + '" and grades_log.date_log<"'
                        + str(month[2])
                        + '" and grades_log.project ="'
                        + project
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.grades_log, search).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'grades_log.period = "'
                        + T(period.period.name)
                        + '" and grades_log.yearp = "'
                        + str(period.yearp)
                        + '" and grades_log.operation_log = "update" and grades_log.date_log>="'
                        + str(month[1])
                        + '" and grades_log.date_log<"'
                        + str(month[2])
                        + '" and grades_log.project ="'
                        + project
                        + '"'
                    )
                else:
                    search = (
                        'grades_log.period = "'
                        + T(period.period.name)
                        + '" and grades_log.yearp = "'
                        + str(period.yearp)
                        + '" and grades_log.operation_log = "update" and grades_log.date_log>="'
                        + str(month[1])
                        + '" and grades_log.date_log<"'
                        + str(month[2])
                        + '" and grades_log.project ="'
                        + project
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.grades_log, search).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'grades_log.period = "'
                        + T(period.period.name)
                        + '" and grades_log.yearp = "'
                        + str(period.yearp)
                        + '" and grades_log.operation_log = "delete" and grades_log.date_log>="'
                        + str(month[1])
                        + '" and grades_log.date_log<"'
                        + str(month[2])
                        + '" and grades_log.project ="'
                        + project
                        + '"'
                    )
                else:
                    search = (
                        'grades_log.period = "'
                        + T(period.period.name)
                        + '" and grades_log.yearp = "'
                        + str(period.yearp)
                        + '" and grades_log.operation_log = "delete" and grades_log.date_log>="'
                        + str(month[1])
                        + '" and grades_log.date_log<"'
                        + str(month[2])
                        + '" and grades_log.project ="'
                        + project
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.grades_log, search).count()
                infoe_level_temp.append(count_i)
            # INSERT PROJECT
            info_level.append(infoe_level_temp)
    # PER ROL
    elif str(request.vars["level"]) == "4":
        # ROLES
        roles = get_roles("grades_log")
        # PERIOD OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MONTH OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        infoe_level_temp.append(str(month[0]))
        info_level.append(infoe_level_temp)
        # PROJECT OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Project"))
        infoe_level_temp.append(str(project))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Role"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "i":
            infoe_level_temp.append(T("Total inserted"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "u":
            infoe_level_temp.append(T("Total modified"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "d":
            infoe_level_temp.append(T("Total out"))
        info_level.append(infoe_level_temp)

        for roll_t in roles:
            roll = db(db.auth_group.role == roll_t).select().first()
            if roll is None:
                roll = db(db.grades_log.roll == roll_t).select().first()
                roll = roll.roll
            else:
                roll = roll.role
            infoe_level_temp = []
            # NAME OF ROLE
            infoe_level_temp.append(T("Rol " + roll))
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'grades_log.period = "'
                        + T(period.period.name)
                        + '" and grades_log.yearp = "'
                        + str(period.yearp)
                        + '" and grades_log.operation_log = "insert" and grades_log.date_log >="'
                        + str(month[1])
                        + '" and grades_log.date_log<"'
                        + str(month[2])
                        + '" and grades_log.project ="'
                        + str(project)
                        + '" and grades_log.roll ="'
                        + str(roll)
                        + '"'
                    )
                else:
                    search = (
                        'grades_log.period = "'
                        + T(period.period.name)
                        + '" and grades_log.yearp = "'
                        + str(period.yearp)
                        + '" and grades_log.operation_log = "insert" and grades_log.date_log >="'
                        + str(month[1])
                        + '" and grades_log.date_log<"'
                        + str(month[2])
                        + '" and grades_log.project ="'
                        + str(project)
                        + '" and grades_log.roll ="'
                        + str(roll)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.grades_log, search).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'grades_log.period = "'
                        + T(period.period.name)
                        + '" and grades_log.yearp = "'
                        + str(period.yearp)
                        + '" and grades_log.operation_log = "update" and grades_log.date_log>="'
                        + str(month[1])
                        + '" and grades_log.date_log<"'
                        + str(month[2])
                        + '" and grades_log.project ="'
                        + str(project)
                        + '" and grades_log.roll ="'
                        + str(roll)
                        + '"'
                    )
                else:
                    search = (
                        'grades_log.period = "'
                        + T(period.period.name)
                        + '" and grades_log.yearp = "'
                        + str(period.yearp)
                        + '" and grades_log.operation_log = "update" and grades_log.date_log>="'
                        + str(month[1])
                        + '" and grades_log.date_log<"'
                        + str(month[2])
                        + '" and grades_log.project ="'
                        + str(project)
                        + '" and grades_log.roll ="'
                        + str(roll)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.grades_log, search).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'grades_log.period = "'
                        + T(period.period.name)
                        + '" and grades_log.yearp = "'
                        + str(period.yearp)
                        + '" and grades_log.operation_log = "delete" and grades_log.date_log>="'
                        + str(month[1])
                        + '" and grades_log.date_log<"'
                        + str(month[2])
                        + '" and grades_log.project ="'
                        + str(project)
                        + '" and grades_log.roll ="'
                        + str(roll)
                        + '"'
                    )
                else:
                    search = (
                        'grades_log.period = "'
                        + T(period.period.name)
                        + '" and grades_log.yearp = "'
                        + str(period.yearp)
                        + '" and grades_log.operation_log = "delete" and grades_log.date_log>="'
                        + str(month[1])
                        + '" and grades_log.date_log<"'
                        + str(month[2])
                        + '" and grades_log.project ="'
                        + str(project)
                        + '" and grades_log.roll ="'
                        + str(roll)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.grades_log, search).count()
                infoe_level_temp.append(count_i)
            # INSERT PROJECT
            info_level.append(infoe_level_temp)
    # PER USER
    elif str(request.vars["level"]) == "5":
        # USERS
        usersProject = get_users(period, project, roll, "grades_log")
        # PERIOD OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MONTH OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        infoe_level_temp.append(str(month[0]))
        info_level.append(infoe_level_temp)
        # PROJECT OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Project"))
        infoe_level_temp.append(str(project))
        info_level.append(infoe_level_temp)
        # ROL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Role"))
        infoe_level_temp.append(T("Rol " + roll))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("User"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "i":
            infoe_level_temp.append(T("Total inserted"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "u":
            infoe_level_temp.append(T("Total modified"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "d":
            infoe_level_temp.append(T("Total out"))
        info_level.append(infoe_level_temp)

        for userPT in usersProject:
            user_p = db(db.auth_user.username == userPT).select().first()
            if user_p is None:
                user_p = db(db.grades_log.user_name == userPT).select().first()
                user_p = user_p.user_name
            else:
                user_p = user_p.username
            infoe_level_temp = []
            # NAME OF USER
            infoe_level_temp.append(user_p)
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'grades_log.period = "'
                        + T(period.period.name)
                        + '" and grades_log.yearp = "'
                        + str(period.yearp)
                        + '" and grades_log.operation_log = "insert" and grades_log.date_log >="'
                        + str(month[1])
                        + '" and grades_log.date_log<"'
                        + str(month[2])
                        + '" and grades_log.project ="'
                        + str(project)
                        + '" and grades_log.roll ="'
                        + str(roll)
                        + '" and grades_log.user_name ="'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'grades_log.period = "'
                        + T(period.period.name)
                        + '" and grades_log.yearp = "'
                        + str(period.yearp)
                        + '" and grades_log.operation_log = "insert" and grades_log.date_log >="'
                        + str(month[1])
                        + '" and grades_log.date_log<"'
                        + str(month[2])
                        + '" and grades_log.project ="'
                        + str(project)
                        + '" and grades_log.roll ="'
                        + str(roll)
                        + '" and grades_log.user_name ="'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.grades_log, search).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'grades_log.period = "'
                        + T(period.period.name)
                        + '" and grades_log.yearp = "'
                        + str(period.yearp)
                        + '" and grades_log.operation_log = "update" and grades_log.date_log>="'
                        + str(month[1])
                        + '" and grades_log.date_log<"'
                        + str(month[2])
                        + '" and grades_log.project ="'
                        + str(project)
                        + '" and grades_log.roll ="'
                        + str(roll)
                        + '" and grades_log.user_name ="'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'grades_log.period = "'
                        + T(period.period.name)
                        + '" and grades_log.yearp = "'
                        + str(period.yearp)
                        + '" and grades_log.operation_log = "update" and grades_log.date_log>="'
                        + str(month[1])
                        + '" and grades_log.date_log<"'
                        + str(month[2])
                        + '" and grades_log.project ="'
                        + str(project)
                        + '" and grades_log.roll ="'
                        + str(roll)
                        + '" and grades_log.user_name ="'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.grades_log, search).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'grades_log.period = "'
                        + T(period.period.name)
                        + '" and grades_log.yearp = "'
                        + str(period.yearp)
                        + '" and grades_log.operation_log = "delete" and grades_log.date_log>="'
                        + str(month[1])
                        + '" and grades_log.date_log<"'
                        + str(month[2])
                        + '" and grades_log.project ="'
                        + str(project)
                        + '" and grades_log.roll ="'
                        + str(roll)
                        + '" and grades_log.user_name ="'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'grades_log.period = "'
                        + T(period.period.name)
                        + '" and grades_log.yearp = "'
                        + str(period.yearp)
                        + '" and grades_log.operation_log = "delete" and grades_log.date_log>="'
                        + str(month[1])
                        + '" and grades_log.date_log<"'
                        + str(month[2])
                        + '" and grades_log.project ="'
                        + str(project)
                        + '" and grades_log.roll ="'
                        + str(roll)
                        + '" and grades_log.user_name ="'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.grades_log, search).count()
                infoe_level_temp.append(count_i)
            # INSERT PROJECT
            info_level.append(infoe_level_temp)
    # DATA
    elif str(request.vars["level"]) == "6":
        # DATA
        if str(request.vars["type_L"]) == "all":
            if personal_query == "":
                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.date_log >="'
                    + str(month[1])
                    + '" and grades_log.date_log<"'
                    + str(month[2])
                    + '" and grades_log.project ="'
                    + str(project)
                    + '" and grades_log.roll ="'
                    + str(roll)
                    + '" and grades_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.date_log >="'
                    + str(month[1])
                    + '" and grades_log.date_log<"'
                    + str(month[2])
                    + '" and grades_log.project ="'
                    + str(project)
                    + '" and grades_log.roll ="'
                    + str(roll)
                    + '" and grades_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
        elif str(request.vars["type_L"]) == "i":
            if personal_query == "":
                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.operation_log = "insert" and grades_log.date_log >="'
                    + str(month[1])
                    + '" and grades_log.date_log<"'
                    + str(month[2])
                    + '" and grades_log.project ="'
                    + str(project)
                    + '" and grades_log.roll ="'
                    + str(roll)
                    + '" and grades_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.operation_log = "insert" and grades_log.date_log >="'
                    + str(month[1])
                    + '" and grades_log.date_log<"'
                    + str(month[2])
                    + '" and grades_log.project ="'
                    + str(project)
                    + '" and grades_log.roll ="'
                    + str(roll)
                    + '" and grades_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
        elif str(request.vars["type_L"]) == "u":
            if personal_query == "":
                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.operation_log = "update" and grades_log.date_log >="'
                    + str(month[1])
                    + '" and grades_log.date_log<"'
                    + str(month[2])
                    + '" and grades_log.project ="'
                    + str(project)
                    + '" and grades_log.roll ="'
                    + str(roll)
                    + '" and grades_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.operation_log = "update" and grades_log.date_log >="'
                    + str(month[1])
                    + '" and grades_log.date_log<"'
                    + str(month[2])
                    + '" and grades_log.project ="'
                    + str(project)
                    + '" and grades_log.roll ="'
                    + str(roll)
                    + '" and grades_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
        elif str(request.vars["type_L"]) == "d":
            if personal_query == "":
                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.operation_log = "delete" and grades_log.date_log >="'
                    + str(month[1])
                    + '" and grades_log.date_log<"'
                    + str(month[2])
                    + '" and grades_log.project ="'
                    + str(project)
                    + '" and grades_log.roll ="'
                    + str(roll)
                    + '" and grades_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.operation_log = "delete" and grades_log.date_log >="'
                    + str(month[1])
                    + '" and grades_log.date_log<"'
                    + str(month[2])
                    + '" and grades_log.project ="'
                    + str(project)
                    + '" and grades_log.roll ="'
                    + str(roll)
                    + '" and grades_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
        # PERIOD
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MONTH
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        infoe_level_temp.append(str(month[0]))
        info_level.append(infoe_level_temp)
        # PROJECT
        infoe_level_temp = []
        infoe_level_temp.append(T("Project"))
        infoe_level_temp.append(str(project))
        info_level.append(infoe_level_temp)
        # ROL
        infoe_level_temp = []
        infoe_level_temp.append(T("Role"))
        infoe_level_temp.append(T("Rol " + roll))
        info_level.append(infoe_level_temp)
        # USER
        infoe_level_temp = []
        infoe_level_temp.append(T("User"))
        infoe_level_temp.append(str(user_p))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE
        infoe_level_temp = []
        infoe_level_temp.append("")
        info_level.append(infoe_level_temp)
        # DETAIL
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # TITLE OF TABLE
        infoe_level_temp = []
        infoe_level_temp.append(T("Operation"))
        infoe_level_temp.append(T("Academic"))
        infoe_level_temp.append(T("Activity"))
        infoe_level_temp.append(T("Category"))
        infoe_level_temp.append(T("Grade Before"))
        infoe_level_temp.append(T("Grade After"))
        infoe_level_temp.append(T("Date"))
        infoe_level_temp.append(T("Description"))
        info_level.append(infoe_level_temp)
        for operation in db.smart_query(db.grades_log, search).select():
            infoe_level_temp = []
            infoe_level_temp.append(operation.operation_log)
            infoe_level_temp.append(operation.academic)
            infoe_level_temp.append(operation.activity)
            infoe_level_temp.append(operation.category)
            infoe_level_temp.append(operation.before_grade)
            infoe_level_temp.append(operation.after_grade)
            infoe_level_temp.append(operation.date_log)
            infoe_level_temp.append(operation.description)
            info_level.append(infoe_level_temp)
    # *****************************************************REPORT*****************************************************
    # ****************************************************************************************************************
    # ****************************************************************************************************************
    return dict(filename="ReporteGestionNotas", csvdata=info_level)


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def grades_management():
    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # ******************************************VERIFY THAT ACCURATE PARAMETERS***************************************
    try:
        # CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars["level"] is not None and (int(request.vars["level"]) < 1 or int(request.vars["level"]) > 6):
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))
        # VERIFY THAT THE PARAMETERS OF EACH LEVEL BE VALID
        if request.vars["level"] is not None:
            # LEVEL MORE THAN 1
            if int(request.vars["level"]) > 1:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_L"] is None or (request.vars["type_L"] != "all"
                and request.vars["type_L"] != "i" and request.vars["type_L"] != "u"
                and request.vars["type_L"] != "d"):
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

                period = validate_period(request.vars["period"])
                if period is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 2
            if int(request.vars["level"]) > 2:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_U"] is None or (request.vars["type_U"] != "all"
                    and request.vars["type_U"] != "i" and request.vars["type_U"] != "u"
                    and request.vars["type_U"] != "d"):
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

                # CHECK IF THE MONTH IS VALID
                month = validate_month(request.vars["month"], period)
                if month is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 3
            if int(request.vars["level"]) > 3:
                # CHECK IF THE PROJECT IS VALID
                project = validate_project(request.vars["project"], "grades_log")
                if project is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 4
            if int(request.vars["level"]) > 4:
                # CHECK IF THE ROLE IS VALID
                roll = validate_role(request.vars["roll"], "grades_log")
                if roll is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 5
            if int(request.vars["level"]) > 5:
                # CHECK IF THE USER IS VALID
                user_p = validate_user(period, project, roll, request.vars["userP"], "grades_log")
                if user_p is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))
    except:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # *****************************************************REPORT*****************************************************
    # LEVELS OF REPORT

    info_level = []
    top5 = []
    grid = None
    # ALL SEMESTERS
    if request.vars["level"] == "1" or request.vars["level"] is None:
        periods_report = db(db.period_year).select(db.period_year.id, db.period_year.yearp, db.period_year.period, orderby=~db.period_year.id)
        if len(periods_report) == 0:
            session.flash = T("Report no visible: There are no parameters required to display the report.")
            redirect(URL("default", "home"))

        for period in periods_report:
            infoe_level_temp = [period.id, f"{T(period.period.name)} {period.yearp}"]
            # INSERT
            count_i = db((db.grades_log.period == T(period.period.name)) & (db.grades_log.yearp == period.yearp) & (db.grades_log.operation_log == 'insert')).count(db.grades_log.id)
            infoe_level_temp.append(count_i)
            # UPDATE
            count_i = db((db.grades_log.period == T(period.period.name)) & (db.grades_log.yearp == period.yearp) & (db.grades_log.operation_log == 'update')).count(db.grades_log.id)
            infoe_level_temp.append(count_i)
            # DELETE
            count_i = db((db.grades_log.period == T(period.period.name)) & (db.grades_log.yearp == period.yearp) & (db.grades_log.operation_log == 'delete')).count(db.grades_log.id)
            infoe_level_temp.append(count_i)
            # INSERT PERIOD
            info_level.append(infoe_level_temp)

        # TOP 5 OF PERIOD
        top5 = db(db.grades_log).select(
            db.grades_log.period,
            db.grades_log.yearp,
            db.grades_log.id.count().with_alias('count'),
            orderby=~db.grades_log.id.count(),
            limitby=(0, 5),
            groupby=[db.grades_log.period, db.grades_log.yearp],
        )
    # PER MONTH
    elif request.vars["level"] == "2":
        for month in get_month_period(period):
            start = datetime.strptime(
                str(period.yearp) + "-" + str(month[0]) + "-01", "%Y-%m-%d"
            )
            if month[2] == 1:
                end = datetime.strptime(
                    str(period.yearp + 1) + "-" + str(month[2]) + "-01", "%Y-%m-%d"
                )
            else:
                end = datetime.strptime(
                    str(period.yearp) + "-" + str(month[2]) + "-01", "%Y-%m-%d"
                )
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # ID OF MONTH
            infoe_level_temp.append(month[0])
            # NAME OF MONTH
            infoe_level_temp.append(month[1] + " " + str(period.yearp))
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):

                search = (
                   'grades_log.period = "'
                   + T(period.period.name)
                   + '" and grades_log.yearp = "'
                   + str(period.yearp)
                   + '" and grades_log.operation_log = "insert" and grades_log.date_log >="'
                   + str(start)
                   + '" and grades_log.date_log<"'
                   + str(end)
                   + '"'
                )
                count_i = db.smart_query(db.grades_log, search).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.operation_log = "update" and grades_log.date_log>="'
                    + str(start)
                    + '" and grades_log.date_log<"'
                    + str(end)
                    + '"'
                )
                count_i = db.smart_query(db.grades_log, search).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):

                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.operation_log = "delete" and grades_log.date_log>="'
                    + str(start)
                    + '" and grades_log.date_log<"'
                    + str(end)
                    + '"'
                )
                count_i = db.smart_query(db.grades_log, search).count()
                infoe_level_temp.append(count_i)
            # INSERT MONTH
            info_level.append(infoe_level_temp)
    # PER PROJECT
    elif request.vars["level"] == "3":
        try:
            projects = get_projects('grades_log', period)
        except:
            projects = get_projects('grades_log', None)
        if len(projects) == 0:
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(
                URL(
                    "management_reports",
                    "grades_management",
                    vars=dict(
                        level="2",
                        period=str(request.vars["period"]),
                        type_L=str(request.vars["type_U"]),
                        querySearch=personal_query,
                    ),
                )
            )
        projects = sorted(projects)

        for project_t in projects:
            project = db(db.project.name == project_t).select().first()
            if project is None:
                project = db(db.grades_log.project == project_t).select().first()
                project = project.project
            else:
                project = project.name
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # NAME OF MONTH
            infoe_level_temp.append(month[0])
            # ID OF PROJECT
            infoe_level_temp.append(project)
            # NAME OF PROJECT
            infoe_level_temp.append(project)
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.operation_log = "insert" and grades_log.date_log >="'
                    + str(month[1])
                    + '" and grades_log.date_log<"'
                    + str(month[2])
                    + '" and grades_log.project ="'
                    + project
                    + '"'
                )
                count_i = db.smart_query(db.grades_log, search).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.operation_log = "update" and grades_log.date_log>="'
                    + str(month[1])
                    + '" and grades_log.date_log<"'
                    + str(month[2])
                    + '" and grades_log.project ="'
                    + project
                    + '"'
                )
                count_i = db.smart_query(db.grades_log, search).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.operation_log = "delete" and grades_log.date_log>="'
                    + str(month[1])
                    + '" and grades_log.date_log<"'
                    + str(month[2])
                    + '" and grades_log.project ="'
                    + project
                    + '"'
                )
                count_i = db.smart_query(db.grades_log, search).count()
                infoe_level_temp.append(count_i)
            # INSERT PROJECT
            info_level.append(infoe_level_temp)

        # TOP 5 OF PROJECT
        search = (
            'grades_log.period = "'
            + T(period.period.name)
            + '" and grades_log.yearp = "'
            + str(period.yearp)
            + '" and grades_log.date_log >="'
            + str(month[1])
            + '" and grades_log.date_log<"'
            + str(month[2])
            + '"'
        )
        top5 = db.smart_query(db.grades_log, search).select(
            db.grades_log.project,
            db.grades_log.id.count().with_alias('count'),
            orderby=~db.grades_log.id.count(),
            limitby=(0, 5),
            groupby=db.grades_log.project,
        )
    # PER ROL
    elif request.vars["level"] == "4":
        roles = get_roles('grades_log')
        if len(roles) == 0:
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(
                URL(
                    "management_reports",
                    "grades_management",
                    vars=dict(
                        level="3",
                        period=str(request.vars["period"]),
                        month=str(request.vars["month"]),
                        type_L=str(request.vars["type_U"]),
                        type_U=str(request.vars["type_U"]),
                        querySearch=personal_query,
                    ),
                )
            )

        for roll_t in roles:
            roll = db(db.auth_group.role == roll_t).select().first()
            if roll is None:
                roll = db(db.grades_log.roll == roll_t).select().first()
                roll = roll.roll
            else:
                roll = roll.role
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # NAME OF MONTH
            infoe_level_temp.append(month[0])
            # NAME OF PROJECT
            infoe_level_temp.append(project)
            # ID OF ROLE
            infoe_level_temp.append(roll)
            # NAME OF ROLE
            infoe_level_temp.append(T("Rol " + roll))
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.operation_log = "insert" and grades_log.date_log >="'
                    + str(month[1])
                    + '" and grades_log.date_log<"'
                    + str(month[2])
                    + '" and grades_log.project ="'
                    + str(project)
                    + '" and grades_log.roll ="'
                    + str(roll)
                    + '"'
                )
                count_i = db.smart_query(db.grades_log, search).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.operation_log = "update" and grades_log.date_log>="'
                    + str(month[1])
                    + '" and grades_log.date_log<"'
                    + str(month[2])
                    + '" and grades_log.project ="'
                    + str(project)
                    + '" and grades_log.roll ="'
                    + str(roll)
                    + '"'
                )
                count_i = db.smart_query(db.grades_log, search).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.operation_log = "delete" and grades_log.date_log>="'
                    + str(month[1])
                    + '" and grades_log.date_log<"'
                    + str(month[2])
                    + '" and grades_log.project ="'
                    + str(project)
                    + '" and grades_log.roll ="'
                    + str(roll)
                    + '"'
                )
                count_i = db.smart_query(db.grades_log, search).count()
                infoe_level_temp.append(count_i)
            # INSERT PROJECT
            info_level.append(infoe_level_temp)
    # PER USER
    elif request.vars["level"] == "5":
        # VERIFY THAT CAN SHOW THE LEVEL OF THE REPORT
        users_project = get_users(period, project, roll, "grades_log")
        if len(users_project) == 0:
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(
                URL(
                    "management_reports",
                    "grades_management",
                    vars=dict(
                        level="4",
                        period=str(request.vars["period"]),
                        month=str(request.vars["month"]),
                        project=str(request.vars["project"]),
                        type_L=str(request.vars["type_U"]),
                        type_U=str(request.vars["type_U"]),
                        querySearch=personal_query,
                    ),
                )
            )

        for user_p_t in users_project:
            user_p = db(db.auth_user.username == user_p_t).select().first()
            if user_p is None:
                user_p = db(db.grades_log.user_name == user_p_t).select().first()
                user_p = user_p.user_name
            else:
                user_p = user_p.username
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # NAME OF MONTH
            infoe_level_temp.append(month[0])
            # NAME OF PROJECT
            infoe_level_temp.append(project)
            # NAME OF ROLE
            infoe_level_temp.append(T("Rol " + roll))
            # ID OF USER
            infoe_level_temp.append(user_p)
            # NAME OF USER
            infoe_level_temp.append(user_p)
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.operation_log = "insert" and grades_log.date_log >="'
                    + str(month[1])
                    + '" and grades_log.date_log<"'
                    + str(month[2])
                    + '" and grades_log.project ="'
                    + str(project)
                    + '" and grades_log.roll ="'
                    + str(roll)
                    + '" and grades_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
                count_i = db.smart_query(db.grades_log, search).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.operation_log = "update" and grades_log.date_log>="'
                    + str(month[1])
                    + '" and grades_log.date_log<"'
                    + str(month[2])
                    + '" and grades_log.project ="'
                    + str(project)
                    + '" and grades_log.roll ="'
                    + str(roll)
                    + '" and grades_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
                count_i = db.smart_query(db.grades_log, search).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                search = (
                    'grades_log.period = "'
                    + T(period.period.name)
                    + '" and grades_log.yearp = "'
                    + str(period.yearp)
                    + '" and grades_log.operation_log = "delete" and grades_log.date_log>="'
                    + str(month[1])
                    + '" and grades_log.date_log<"'
                    + str(month[2])
                    + '" and grades_log.project ="'
                    + str(project)
                    + '" and grades_log.roll ="'
                    + str(roll)
                    + '" and grades_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
                count_i = db.smart_query(db.grades_log, search).count()
                infoe_level_temp.append(count_i)
            # INSERT PROJECT
            info_level.append(infoe_level_temp)
    # DATA
    elif request.vars["level"] == "6":
        if str(request.vars["type_L"]) == "all":
            search = (
                'grades_log.period = "'
                + T(period.period.name)
                + '" and grades_log.yearp = "'
                + str(period.yearp)
                + '" and grades_log.date_log >="'
                + str(month[1])
                + '" and grades_log.date_log<"'
                + str(month[2])
                + '" and grades_log.project ="'
                + str(project)
                + '" and grades_log.roll ="'
                + str(roll)
                + '" and grades_log.user_name ="'
                + str(user_p)
                + '"'
            )
        elif str(request.vars["type_L"]) == "i":
            search = (
                'grades_log.period = "'
                + T(period.period.name)
                + '" and grades_log.yearp = "'
                + str(period.yearp)
                + '" and grades_log.operation_log = "insert" and grades_log.date_log >="'
                + str(month[1])
                + '" and grades_log.date_log<"'
                + str(month[2])
                + '" and grades_log.project ="'
                + str(project)
                + '" and grades_log.roll ="'
                + str(roll)
                + '" and grades_log.user_name ="'
                + str(user_p)
                + '"'
            )
        elif str(request.vars["type_L"]) == "u":
            search = (
                'grades_log.period = "'
                + T(period.period.name)
                + '" and grades_log.yearp = "'
                + str(period.yearp)
                + '" and grades_log.operation_log = "update" and grades_log.date_log >="'
                + str(month[1])
                + '" and grades_log.date_log<"'
                + str(month[2])
                + '" and grades_log.project ="'
                + str(project)
                + '" and grades_log.roll ="'
                + str(roll)
                + '" and grades_log.user_name ="'
                + str(user_p)
                + '"'
            )
        elif str(request.vars["type_L"]) == "d":
            search = (
                'grades_log.period = "'
                + T(period.period.name)
                + '" and grades_log.yearp = "'
                + str(period.yearp)
                + '" and grades_log.operation_log = "delete" and grades_log.date_log >="'
                + str(month[1])
                + '" and grades_log.date_log<"'
                + str(month[2])
                + '" and grades_log.project ="'
                + str(project)
                + '" and grades_log.roll ="'
                + str(roll)
                + '" and grades_log.user_name ="'
                + str(user_p)
                + '"'
            )
        grid = []
        for data in db.smart_query(db.grades_log, search).select():
            grid.append(data.id)
        if len(grid) == 0:
            grid.append(-1)

        infoe_level_temp = []
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        infoe_level_temp.append(str(month[0]))
        infoe_level_temp.append(str(project))
        infoe_level_temp.append(T("Rol " + roll))
        infoe_level_temp.append(str(user_p))
        info_level.append(infoe_level_temp)
        # GRID
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
        grid = SQLFORM.grid(
            db.grades_log.id.belongs(grid),
            csv=False,
            create=False,
            editable=False,
            deletable=False,
            paginate=9,
            searchable=False,
        )
    
    return dict(
        infoLevel=info_level,
        top5=top5,
        grid=grid,
    )

#*************************************************************************************************************************************
#*************************************************************************************************************************************
#*****************************************************MANAGEMENT REPORT GRADES********************************************************


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator")
    or auth.has_membership("Ecys-Administrator")
)
def evaluation_result_export():
    # VERIFI THAT ACCURATE PARAMETERS
    try:
        # CHECK IF THE TYPE OF EXPORT IS VALID
        if request.vars["list_type"] is None or str(request.vars["list_type"]) != "csv":
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))

        # CHECK THAT THE LEVEL OF REPORT IS VALID
        if (request.vars["level"] is not None) and (
            int(request.vars["level"]) < 1 or int(request.vars["level"]) > 5
        ):
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(URL("default", "home"))

        # Check if the period is change
        if request.vars["period"] is None:

            cperiod = cpfecys.current_year_period()
            period = db(db.period_year.id == cperiod.id).select().first()
        else:
            if request.vars["period"] != "":
                period = request.vars["period"]
                period = db(db.period_year.id == period).select().first()
            else:
                session.flash = T("Not valid Action.")
                redirect(URL("default", "home"))

        # VERIFY THAT THE PARAMETERS OF EACH LEVEL BE VALID
        if request.vars["level"] is not None:
            # LEVEL MORE THAN 1
            if int(request.vars["level"]) > 1:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_L"] is None or (
                    str(request.vars["type_L"]) != "all"
                    and str(request.vars["type_L"]) != "a"
                    and str(request.vars["type_L"]) != "r"
                ):
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

                evaluation = validate_evaluation(request.vars["evaluation"])
                if evaluation is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 2
            if int(request.vars["level"]) > 2:
                # CHECK IF THE TYPE OF REPORT IS VALID
                project = db(db.project.id == request.vars["project"]).select().first()
                if project is None:
                    session.flash = T("Not valid Action.")
                    redi * rect(URL("default", "index"))
                if request.vars["type_U"] is None or (
                    str(request.vars["type_U"]) != "all"
                    and str(request.vars["type_U"]) != "a"
                    and str(request.vars["type_U"]) != "r"
                ):
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            if int(request.vars["level"]) > 3:
                # CHECK THE USER
                user_p = db(db.auth_user.id == request.vars["user"]).select().first()
                if user_p is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 4
            if int(request.vars["level"]) > 4:
                # CHECK IF THE CATEGORY IS VALID
                category = db(
                    (
                        db.question_repository.repository_evaluation
                        == request.vars["evaluation"]
                    )
                    & (
                        db.question_repository.question_type_name
                        == request.vars["category"]
                    )
                ).select()
                if category is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

    except:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # *****************************************************REPORT*****************************************************

    # TITLE
    info_level = []
    infoe_level_temp = []
    infoe_level_temp.append("Universidad de San Carlos de Guatemala")
    info_level.append(infoe_level_temp)
    infoe_level_temp = []
    infoe_level_temp.append("Facultad de Ingeniería")
    info_level.append(infoe_level_temp)
    infoe_level_temp = []
    infoe_level_temp.append("Escuela de Ciencias y Sistemas")
    info_level.append(infoe_level_temp)
    # LEVELS OF REPORT
    if request.vars["level"] == "1" or request.vars["level"] is None:
        infoe_level_temp = []
        infoe_level_temp.append(T("Evaluations"))
        infoe_level_temp.append(T("Rol"))
        infoe_level_temp.append(T("Approveds"))
        infoe_level_temp.append(T("Reprobates"))
        infoe_level_temp.append(T("Total"))
        info_level.append(infoe_level_temp)
        # aqui for evaluation in db(db.evaluation_result.period==period.id).select():
        for evaluation in db(db.evaluation_result.period == period.id).select(
            groupby=db.evaluation_result.repository_evaluation
        ):
            infoe_level_temp = []
            # ID OF evaluation
            infoe_level_temp.append(evaluation.repository_evaluation)
            # NAME OF EVALUATION
            infoe_level_temp.append((evaluation.repository_evaluation.name))
            # NAME OF ROLS
            infoe_level_temp.append(
                (evaluation.repository_evaluation.user_type_evaluated.role)
            )

            count_r = 0
            count_a = 0
            for evaluation_result in db(
                db.evaluation_result.repository_evaluation
                == evaluation.repository_evaluation
            ).select():
                result_cat = 0
                count_cat = 0
                for quetions_rep in db(
                    db.question_repository.repository_evaluation
                    == evaluation_result.repository_evaluation
                ).select(groupby=db.question_repository.question_type_name):
                    count_question = 0
                    count_result = 0
                    for quetions_rep_2 in db(
                        (
                            db.question_repository.repository_evaluation
                            == evaluation_result.repository_evaluation
                        )
                        & (
                            db.question_repository.question_type_name
                            == quetions_rep.question_type_name
                        )
                    ).select():
                        count_answers = 0
                        result_answers = 0
                        for var_evaluation_solve_detail in db(
                            (
                                db.evaluation_solve_detail.evaluation_result
                                == evaluation_result.id
                            )
                            & (
                                db.evaluation_solve_detail.question_repository
                                == quetions_rep_2.id
                            )
                        ).select():
                            result_answers = int(
                                result_answers
                                + (
                                    var_evaluation_solve_detail.repository_answer.grade
                                    * var_evaluation_solve_detail.total_count
                                )
                                / 100
                            )
                            count_answers = count_answers + 1

                        if count_answers != 0:
                            result_answers = int(result_answers / count_answers)

                            count_question = count_question + 1
                            count_result = count_result + (result_answers)
                    try:
                        count_cat = count_cat + 1
                        result_cat_temp = int(count_result * 100 / count_question)
                        result_cat = result_cat + result_cat_temp
                    except:
                        None
                result_temp = int(result_cat / count_cat)
                if result_temp < 61:
                    count_r = count_r + 1
                else:
                    count_a = count_a + 1

            infoe_level_temp.append(count_a)
            infoe_level_temp.append(count_r)

            infoe_level_temp.append(
                db(
                    db.evaluation_result.repository_evaluation
                    == evaluation.repository_evaluation
                ).count()
            )
            info_level.append(infoe_level_temp)

    elif str(request.vars["level"]) == "2":
        infoe_level_temp = []
        infoe_level_temp.append(T("Project"))

        if (str(request.vars["type_L"]) == "all") or (
            str(request.vars["type_L"]) == "a"
        ):
            infoe_level_temp.append(T("Approveds"))
        pass
        if (str(request.vars["type_L"]) == "all") or (
            str(request.vars["type_L"]) == "r"
        ):
            infoe_level_temp.append(T("Reprobates"))
        pass
        if str(request.vars["type_L"]) == "all":
            infoe_level_temp.append(T("Total"))
        pass
        info_level.append(infoe_level_temp)

        evaluations = db(
            (db.evaluation_result.repository_evaluation == request.vars["evaluation"])
            & (db.evaluation_result.period == period.id)
        ).select(groupby=db.evaluation_result.project)

        for evaluation in evaluations:
            infoe_level_temp = []
            infoe_level_temp.append(evaluation.project.name)

            count_r = 0
            count_a = 0

            for evaluation_result in db(
                (
                    db.evaluation_result.repository_evaluation
                    == request.vars["evaluation"]
                )
                & (db.evaluation_result.period == period.id)
                & (db.evaluation_result.project == evaluation.project)
            ).select():
                result_cat = 0
                count_cat = 0
                for quetions_rep in db(
                    db.question_repository.repository_evaluation
                    == evaluation_result.repository_evaluation
                ).select(groupby=db.question_repository.question_type_name):
                    count_question = 0
                    count_result = 0
                    for quetions_rep_2 in db(
                        (
                            db.question_repository.repository_evaluation
                            == evaluation_result.repository_evaluation
                        )
                        & (
                            db.question_repository.question_type_name
                            == quetions_rep.question_type_name
                        )
                    ).select():
                        count_answers = 0
                        result_answers = 0
                        for var_evaluation_solve_detail in db(
                            (
                                db.evaluation_solve_detail.evaluation_result
                                == evaluation_result.id
                            )
                            & (
                                db.evaluation_solve_detail.question_repository
                                == quetions_rep_2.id
                            )
                        ).select():
                            result_answers = int(
                                result_answers
                                + (
                                    var_evaluation_solve_detail.repository_answer.grade
                                    * var_evaluation_solve_detail.total_count
                                )
                                / 100
                            )
                            count_answers = count_answers + 1

                        if count_answers != 0:
                            result_answers = int(result_answers / count_answers)

                            count_question = count_question + 1
                            count_result = count_result + (result_answers)
                    try:
                        count_cat = count_cat + 1
                        result_cat_temp = int(count_result * 100 / count_question)
                        result_cat = result_cat + result_cat_temp
                    except:
                        None
                result_temp = int(result_cat / count_cat)

                if result_temp < 61:
                    count_r = count_r + 1
                else:
                    count_a = count_a + 1

            infoe_level_temp.append(count_a)
            infoe_level_temp.append(count_r)
            infoe_level_temp.append(count_a + count_r)

            info_level.append(infoe_level_temp)

    elif str(request.vars["level"]) == "3":
        infoe_level_temp = []
        infoe_level_temp.append(T("User name"))
        infoe_level_temp.append(T("Name"))
        infoe_level_temp.append(T("Evaluation Result"))
        info_level.append(infoe_level_temp)
        evaluations = db(
            (db.evaluation_result.repository_evaluation == request.vars["evaluation"])
            & (db.evaluation_result.project == request.vars["project"])
            & (db.evaluation_result.period == period.id)
        ).select()

        for evaluation in evaluations:

            result_cat = 0
            count_cat = 0
            for quetions_rep in db(
                db.question_repository.repository_evaluation
                == evaluation.repository_evaluation
            ).select(groupby=db.question_repository.question_type_name):
                count_question = 0
                count_result = 0
                for quetions_rep_2 in db(
                    (
                        db.question_repository.repository_evaluation
                        == evaluation.repository_evaluation
                    )
                    & (
                        db.question_repository.question_type_name
                        == quetions_rep.question_type_name
                    )
                ).select():
                    count_answers = 0
                    result_answers = 0
                    for var_evaluation_solve_detail in db(
                        (db.evaluation_solve_detail.evaluation_result == evaluation.id)
                        & (
                            db.evaluation_solve_detail.question_repository
                            == quetions_rep_2.id
                        )
                    ).select():
                        result_answers = int(
                            result_answers
                            + (
                                var_evaluation_solve_detail.repository_answer.grade
                                * var_evaluation_solve_detail.total_count
                            )
                            / 100
                        )
                        count_answers = count_answers + 1

                    if count_answers != 0:
                        result_answers = int(result_answers / count_answers)

                        count_question = count_question + 1
                        count_result = count_result + (result_answers)
                try:
                    count_cat = count_cat + 1
                    result_cat_temp = int(count_result * 100 / count_question)
                    result_cat = result_cat + result_cat_temp
                except:
                    None

            result_temp = int(result_cat / count_cat)

            add_user = False
            if str(request.vars["type_U"]) == "all":
                add_user = True
            if str(request.vars["type_U"]) == "r":
                if result_temp < 61:
                    add_user = True
            if str(request.vars["type_U"]) == "a":
                if result_temp >= 61:
                    add_user = True
            if add_user == True:
                infoe_level_temp = []
                infoe_level_temp.append(evaluation.evaluated.username)
                infoe_level_temp.append(
                    evaluation.evaluated.first_name
                    + " "
                    + evaluation.evaluated.last_name
                )
                infoe_level_temp.append(result_temp)

                info_level.append(infoe_level_temp)

    elif str(request.vars["level"]) == "4":
        infoe_level_temp = []
        infoe_level_temp.append(T("Category"))
        infoe_level_temp.append(T("Result"))
        info_level.append(infoe_level_temp)
        evaluation = (
            db(
                (
                    db.evaluation_result.repository_evaluation
                    == request.vars["evaluation"]
                )
                & (db.evaluation_result.project == request.vars["project"])
                & (db.evaluation_result.period == period.id)
                & (db.evaluation_result.evaluated == str(request.vars["user"]))
            )
            .select()
            .first()
        )

        for quetions_rep in db(
            db.question_repository.repository_evaluation
            == evaluation.repository_evaluation
        ).select(groupby=db.question_repository.question_type_name):
            count_question = 0
            count_result = 0
            for quetions_rep_2 in db(
                (
                    db.question_repository.repository_evaluation
                    == evaluation.repository_evaluation
                )
                & (
                    db.question_repository.question_type_name
                    == quetions_rep.question_type_name
                )
            ).select():
                count_answers = 0
                result_answers = 0
                for var_evaluation_solve_detail in db(
                    (db.evaluation_solve_detail.evaluation_result == evaluation.id)
                    & (
                        db.evaluation_solve_detail.question_repository
                        == quetions_rep_2.id
                    )
                ).select():
                    result_answers = int(
                        result_answers
                        + (
                            var_evaluation_solve_detail.repository_answer.grade
                            * var_evaluation_solve_detail.total_count
                        )
                        / 100
                    )
                    count_answers = count_answers + 1

                if count_answers != 0:
                    result_answers = int(result_answers / count_answers)

                    count_question = count_question + 1
                    count_result = count_result + (result_answers)

            try:
                result_temp = int(count_result * 100 / count_question)
                infoe_level_temp = []
                infoe_level_temp.append(quetions_rep.question_type_name)
                infoe_level_temp.append(result_temp)

                info_level.append(infoe_level_temp)

            except:
                result_temp = int(-1)
                infoe_level_temp = []
                infoe_level_temp.append(quetions_rep.question_type_name)
                infoe_level_temp.append(result_temp)

                info_level.append(infoe_level_temp)

    elif str(request.vars["level"]) == "5":
        infoe_level_temp = []
        infoe_level_temp.append(T("Question"))
        infoe_level_temp.append(T("Result"))
        info_level.append(infoe_level_temp)
        evaluation = (
            db(
                (
                    db.evaluation_result.repository_evaluation
                    == request.vars["evaluation"]
                )
                & (db.evaluation_result.project == request.vars["project"])
                & (db.evaluation_result.period == period.id)
                & (db.evaluation_result.evaluated == str(request.vars["user"]))
            )
            .select()
            .first()
        )

        count_question = 0
        count_result = 0
        for quetions_rep_2 in db(
            (
                db.question_repository.repository_evaluation
                == evaluation.repository_evaluation
            )
            & (db.question_repository.question_type_name == request.vars["category"])
        ).select():
            count_answers = 0
            result_answers = 0
            for var_evaluation_solve_detail in db(
                (db.evaluation_solve_detail.evaluation_result == evaluation.id)
                & (db.evaluation_solve_detail.question_repository == quetions_rep_2.id)
            ).select():
                result_answers = int(
                    result_answers
                    + (
                        var_evaluation_solve_detail.repository_answer.grade
                        * var_evaluation_solve_detail.total_count
                    )
                    / 100
                )
                count_answers = count_answers + 1

            if count_answers != 0:
                result_answers = int(result_answers / count_answers)

                result_temp = int(result_answers * 100)
                count_question = count_question + 1
                count_result = count_result + (result_answers)

            try:
                infoe_level_temp = []
                infoe_level_temp.append(quetions_rep_2.question)
                infoe_level_temp.append(result_temp)

                info_level.append(infoe_level_temp)
            except:
                infoe_level_temp = []
                infoe_level_temp.append(quetions_rep_2.question)
                infoe_level_temp.append(-1)

                info_level.append(infoe_level_temp)

    # *****************************************************REPORT*****************************************************
    # ****************************************************************************************************************
    # ****************************************************************************************************************
    return dict(filename="ResultadoDeEvaluaciones", csvdata=info_level)


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator")
    or auth.has_membership("Ecys-Administrator")
)
def evaluation_result():
    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # ******************************************VERIFY THAT ACCURATE PARAMETERS***************************************
    try:
        # CHECK THAT THE LEVEL OF REPORT IS VALID
        if (request.vars["level"] is not None) and (
            int(request.vars["level"]) < 1 or int(request.vars["level"]) > 5
        ):
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))

        # Check if the period is change
        if request.vars["period"] is None:

            cperiod = cpfecys.current_year_period()
            period = db(db.period_year.id == cperiod.id).select().first()
        else:
            if request.vars["period"] != "":
                period = request.vars["period"]
                period = db(db.period_year.id == period).select().first()
            else:
                session.flash = T("Not valid Action.")
                redirect(URL("default", "home"))

        # VERIFY THAT THE PARAMETERS OF EACH LEVEL BE VALID
        if request.vars["level"] is not None:
            # LEVEL MORE THAN 1
            if int(request.vars["level"]) > 1:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_L"] is None or (
                    str(request.vars["type_L"]) != "all"
                    and str(request.vars["type_L"]) != "a"
                    and str(request.vars["type_L"]) != "r"
                ):
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

                evaluation = validate_evaluation(request.vars["evaluation"])
                if evaluation is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 2
            if int(request.vars["level"]) > 2:
                # CHECK IF THE TYPE OF REPORT IS VALID
                project = db(db.project.id == request.vars["project"]).select().first()
                if project is None:
                    session.flash = T("Not valid Action.")
                    redi * rect(URL("default", "index"))
                if request.vars["type_U"] is None or (
                    str(request.vars["type_U"]) != "all"
                    and str(request.vars["type_U"]) != "a"
                    and str(request.vars["type_U"]) != "r"
                ):
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            if int(request.vars["level"]) > 3:
                # CHECK THE USER
                user_p = db(db.auth_user.id == request.vars["user"]).select().first()
                if user_p is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 4
            if int(request.vars["level"]) > 4:
                # CHECK IF THE CATEGORY IS VALID
                category = db(
                    (
                        db.question_repository.repository_evaluation
                        == request.vars["evaluation"]
                    )
                    & (
                        db.question_repository.question_type_name
                        == request.vars["category"]
                    )
                ).select()
                if category is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

    except:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # *****************************************************REPORT*****************************************************
    # LEVELS OF REPORT

    info_level = []
    top5 = []
    grid = None
    # ALL SEMESTERS
    personal_query = ""

    if request.vars["level"] == "1" or request.vars["level"] is None:

        # aqui for evaluation in db(db.evaluation_result.period==period.id).select():
        for evaluation in db(db.evaluation_result.period == period.id).select(
            groupby=db.evaluation_result.repository_evaluation
        ):
            infoe_level_temp = []
            # ID OF evaluation
            infoe_level_temp.append(evaluation.repository_evaluation)
            # NAME OF EVALUATION
            infoe_level_temp.append((evaluation.repository_evaluation.name))
            # NAME OF ROLS
            infoe_level_temp.append(
                (evaluation.repository_evaluation.user_type_evaluated.role)
            )

            count_r = 0
            count_a = 0
            for evaluation_result in db(
                db.evaluation_result.repository_evaluation
                == evaluation.repository_evaluation
            ).select():
                result_cat = 0
                count_cat = 0
                for quetions_rep in db(
                    db.question_repository.repository_evaluation
                    == evaluation_result.repository_evaluation
                ).select(groupby=db.question_repository.question_type_name):
                    count_question = 0
                    count_result = 0
                    for quetions_rep_2 in db(
                        (
                            db.question_repository.repository_evaluation
                            == evaluation_result.repository_evaluation
                        )
                        & (
                            db.question_repository.question_type_name
                            == quetions_rep.question_type_name
                        )
                    ).select():
                        count_answers = 0
                        result_answers = 0
                        for var_evaluation_solve_detail in db(
                            (
                                db.evaluation_solve_detail.evaluation_result
                                == evaluation_result.id
                            )
                            & (
                                db.evaluation_solve_detail.question_repository
                                == quetions_rep_2.id
                            )
                        ).select():
                            result_answers = int(
                                result_answers
                                + (
                                    var_evaluation_solve_detail.repository_answer.grade
                                    * var_evaluation_solve_detail.total_count
                                )
                            )
                            count_answers = (
                                count_answers + var_evaluation_solve_detail.total_count
                            )

                        if count_answers != 0:
                            result_answers = int(result_answers / count_answers)

                            count_question = count_question + 1
                            count_result = count_result + (result_answers)
                    try:
                        count_cat = count_cat + 1
                        result_cat_temp = int(count_result / count_question)
                        result_cat = result_cat + result_cat_temp
                    except:
                        None
                result_temp = int(result_cat / count_cat)
                if result_temp < 61:
                    count_r = count_r + 1
                else:
                    count_a = count_a + 1

            infoe_level_temp.append(count_a)
            infoe_level_temp.append(count_r)

            infoe_level_temp.append(
                db(
                    db.evaluation_result.repository_evaluation
                    == evaluation.repository_evaluation
                ).count()
            )
            info_level.append(infoe_level_temp)

    elif str(request.vars["level"]) == "2":
        evaluations = db(
            (db.evaluation_result.repository_evaluation == request.vars["evaluation"])
            & (db.evaluation_result.period == period.id)
        ).select(groupby=db.evaluation_result.project)

        for evaluation in evaluations:
            infoe_level_temp = []
            infoe_level_temp.append(evaluation.project)
            infoe_level_temp.append(evaluation.project.name)

            count_r = 0
            count_a = 0

            for evaluation_result in db(
                (
                    db.evaluation_result.repository_evaluation
                    == request.vars["evaluation"]
                )
                & (db.evaluation_result.period == period.id)
                & (db.evaluation_result.project == evaluation.project)
            ).select():
                result_cat = 0
                count_cat = 0
                for quetions_rep in db(
                    db.question_repository.repository_evaluation
                    == evaluation_result.repository_evaluation
                ).select(groupby=db.question_repository.question_type_name):
                    count_question = 0
                    count_result = 0
                    for quetions_rep_2 in db(
                        (
                            db.question_repository.repository_evaluation
                            == evaluation_result.repository_evaluation
                        )
                        & (
                            db.question_repository.question_type_name
                            == quetions_rep.question_type_name
                        )
                    ).select():
                        count_answers = 0
                        result_answers = 0
                        for var_evaluation_solve_detail in db(
                            (
                                db.evaluation_solve_detail.evaluation_result
                                == evaluation_result.id
                            )
                            & (
                                db.evaluation_solve_detail.question_repository
                                == quetions_rep_2.id
                            )
                        ).select():
                            result_answers = int(
                                result_answers
                                + (
                                    var_evaluation_solve_detail.repository_answer.grade
                                    * var_evaluation_solve_detail.total_count
                                )
                            )
                            count_answers = (
                                count_answers + var_evaluation_solve_detail.total_count
                            )

                        if count_answers != 0:
                            result_answers = int(result_answers / count_answers)

                            count_question = count_question + 1
                            count_result = count_result + (result_answers)
                    try:
                        count_cat = count_cat + 1
                        result_cat_temp = int(count_result / count_question)
                        result_cat = result_cat + result_cat_temp
                    except:
                        None
                result_temp = int(result_cat / count_cat)

                if result_temp < 61:
                    count_r = count_r + 1
                else:
                    count_a = count_a + 1

            infoe_level_temp.append(count_a)
            infoe_level_temp.append(count_r)

            info_level.append(infoe_level_temp)
    elif str(request.vars["level"]) == "3":
        evaluations = db(
            (db.evaluation_result.repository_evaluation == request.vars["evaluation"])
            & (db.evaluation_result.project == request.vars["project"])
            & (db.evaluation_result.period == period.id)
        ).select()

        for evaluation in evaluations:

            result_cat = 0
            count_cat = 0
            for quetions_rep in db(
                db.question_repository.repository_evaluation
                == evaluation.repository_evaluation
            ).select(groupby=db.question_repository.question_type_name):
                count_question = 0
                count_result = 0
                for quetions_rep_2 in db(
                    (
                        db.question_repository.repository_evaluation
                        == evaluation.repository_evaluation
                    )
                    & (
                        db.question_repository.question_type_name
                        == quetions_rep.question_type_name
                    )
                ).select():
                    count_answers = 0
                    result_answers = 0
                    for var_evaluation_solve_detail in db(
                        (db.evaluation_solve_detail.evaluation_result == evaluation.id)
                        & (
                            db.evaluation_solve_detail.question_repository
                            == quetions_rep_2.id
                        )
                    ).select():
                        result_answers = int(
                            result_answers
                            + (
                                var_evaluation_solve_detail.repository_answer.grade
                                * var_evaluation_solve_detail.total_count
                            )
                        )
                        count_answers = (
                            count_answers + var_evaluation_solve_detail.total_count
                        )

                    if count_answers != 0:
                        result_answers = int(result_answers / count_answers)

                        count_question = count_question + 1
                        count_result = count_result + (result_answers)
                try:
                    count_cat = count_cat + 1
                    result_cat_temp = int(count_result / count_question)
                    result_cat = result_cat + result_cat_temp
                except:
                    None

            result_temp = int(result_cat / count_cat)

            add_user = False
            if str(request.vars["type_U"]) == "all":
                add_user = True
            if str(request.vars["type_U"]) == "r":
                if result_temp < 61:
                    add_user = True
            if str(request.vars["type_U"]) == "a":
                if result_temp >= 61:
                    add_user = True
            if add_user == True:
                infoe_level_temp = []
                infoe_level_temp.append(evaluation.evaluated)
                infoe_level_temp.append(evaluation.evaluated.username)
                infoe_level_temp.append(
                    evaluation.evaluated.first_name
                    + " "
                    + evaluation.evaluated.last_name
                )
                infoe_level_temp.append(result_temp)

                info_level.append(infoe_level_temp)

    # PER PROJECT
    elif str(request.vars["level"]) == "4":
        evaluation = (
            db(
                (
                    db.evaluation_result.repository_evaluation
                    == request.vars["evaluation"]
                )
                & (db.evaluation_result.project == request.vars["project"])
                & (db.evaluation_result.period == period.id)
                & (db.evaluation_result.evaluated == str(request.vars["user"]))
            )
            .select()
            .first()
        )

        for quetions_rep in db(
            db.question_repository.repository_evaluation
            == evaluation.repository_evaluation
        ).select(groupby=db.question_repository.question_type_name):
            count_question = 0
            count_result = 0
            for quetions_rep_2 in db(
                (
                    db.question_repository.repository_evaluation
                    == evaluation.repository_evaluation
                )
                & (
                    db.question_repository.question_type_name
                    == quetions_rep.question_type_name
                )
            ).select():
                count_answers = 0
                result_answers = 0
                for var_evaluation_solve_detail in db(
                    (db.evaluation_solve_detail.evaluation_result == evaluation.id)
                    & (
                        db.evaluation_solve_detail.question_repository
                        == quetions_rep_2.id
                    )
                ).select():
                    result_answers = int(
                        result_answers
                        + (
                            var_evaluation_solve_detail.repository_answer.grade
                            * var_evaluation_solve_detail.total_count
                        )
                    )
                    count_answers = (
                        count_answers + var_evaluation_solve_detail.total_count
                    )

                if count_answers != 0:
                    result_answers = int(result_answers / count_answers)

                    count_question = count_question + 1
                    count_result = count_result + (result_answers)

            try:
                result_temp = int(count_result / count_question)
                infoe_level_temp = []
                infoe_level_temp.append(quetions_rep.question_type_name)
                infoe_level_temp.append(result_temp)

                info_level.append(infoe_level_temp)

            except:
                result_temp = int(-1)
                infoe_level_temp = []
                infoe_level_temp.append(quetions_rep.question_type_name)
                infoe_level_temp.append(result_temp)

                info_level.append(infoe_level_temp)

    elif str(request.vars["level"]) == "5":
        evaluation = (
            db(
                (
                    db.evaluation_result.repository_evaluation
                    == request.vars["evaluation"]
                )
                & (db.evaluation_result.project == request.vars["project"])
                & (db.evaluation_result.period == period.id)
                & (db.evaluation_result.evaluated == str(request.vars["user"]))
            )
            .select()
            .first()
        )

        count_question = 0
        count_result = 0

        for quetions_rep_2 in db(
            (
                db.question_repository.repository_evaluation
                == evaluation.repository_evaluation
            )
            & (db.question_repository.question_type_name == request.vars["category"])
        ).select():
            count_answers = 0
            result_answers = 0
            result_temp = -1
            text_show = None
            answer_detail = db(
                (db.evaluation_solve_detail.evaluation_result == evaluation.id)
                & (db.evaluation_solve_detail.question_repository == quetions_rep_2.id)
            ).select()

            if answer_detail.first() is None:
                text_show = db(
                    (db.evaluation_solve_text.evaluation_result == evaluation.id)
                    & (
                        db.evaluation_solve_text.question_repository
                        == quetions_rep_2.id
                    )
                ).select()
                if text_show.first() is None:
                    text_show = None

            for var_evaluation_solve_detail in answer_detail:
                result_answers = int(
                    result_answers
                    + (
                        var_evaluation_solve_detail.repository_answer.grade
                        * var_evaluation_solve_detail.total_count
                    )
                )
                count_answers = count_answers + var_evaluation_solve_detail.total_count

            if count_answers != 0:
                result_answers = int(result_answers / count_answers)

                result_temp = int(result_answers)
                count_question = count_question + 1
                count_result = count_result + (result_answers)

            try:
                infoe_level_temp = []
                infoe_level_temp.append(quetions_rep_2.question)
                infoe_level_temp.append(result_temp)
                infoe_level_temp.append(text_show)

                info_level.append(infoe_level_temp)
            except:
                infoe_level_temp = []
                infoe_level_temp.append(quetions_rep_2.question)
                infoe_level_temp.append(-1)

                info_level.append(infoe_level_temp)

    return dict(infoLevel=info_level, top5=top5, grid=grid, period_var=period)


#*************************************************************************************************************************************
#*************************************************************************************************************************************
#*****************************************************MANAGEMENT REPORT ACTIVITIES WITH METRIC****************************************


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def activities_with_metric_management_export():
    # VERIFI THAT ACCURATE PARAMETERS
    try:
        # CHECK IF THE TYPE OF EXPORT IS VALID
        if request.vars["list_type"] is None or str(request.vars["list_type"]) != "csv":
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))

        # CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars["level"] is not None and (
            int(request.vars["level"]) < 1 or int(request.vars["level"]) > 6
        ):
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))

        # VERIFY THAT THE PARAMETERS OF EACH LEVEL BE VALID
        if request.vars["level"] is not None:
            # LEVEL MORE THAN 1
            if int(request.vars["level"]) > 1:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_L"] is None or (
                    str(request.vars["type_L"]) != "all"
                    and str(request.vars["type_L"]) != "i"
                    and str(request.vars["type_L"]) != "u"
                    and str(request.vars["type_L"]) != "d"
                ):
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

                period = validate_period(request.vars["period"])
                if period is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 2
            if int(request.vars["level"]) > 2:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_U"] is None or (
                    str(request.vars["type_U"]) != "all"
                    and str(request.vars["type_U"]) != "i"
                    and str(request.vars["type_U"]) != "u"
                    and str(request.vars["type_U"]) != "d"
                ):
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

                # CHECK IF THE MONTH IS VALID
                month = validate_month(request.vars["month"], period)
                if month is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 3
            if int(request.vars["level"]) > 3:
                # CHECK IF THE PROJECT IS VALID
                project = validate_project(
                    request.vars["project"], "course_activity_log"
                )
                if project is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 4
            if int(request.vars["level"]) > 4:
                # CHECK IF THE ROLE IS VALID
                roll = validate_role(request.vars["roll"], "course_activity_log")
                if roll is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 5
            if int(request.vars["level"]) > 5:
                # CHECK IF THE USER IS VALID
                user_p = validate_user(
                    period, project, roll, request.vars["userP"], "course_activity_log"
                )
                if user_p is None:
                    session.flash = T("Not valid Action.")
                    redi * rect(URL("default", "home"))
    except:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    # CHECK IF THERE IS A PERSONALIZED QUERY
    personal_query = ""
    if (
        request.vars["querySearch"] is not None
        and str(request.vars["querySearch"]) != ""
    ):
        # PERSONALIZED QUERY SURE WORK
        try:
            personal_query = str(request.vars["querySearch"])
            count_i = db.smart_query(db.course_activity_log, personal_query).count()
        except:
            personal_query = ""

    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # *****************************************************REPORT*****************************************************

    # TITLE
    info_level = []
    infoe_level_temp = []
    infoe_level_temp.append("Universidad de San Carlos de Guatemala")
    info_level.append(infoe_level_temp)
    infoe_level_temp = []
    infoe_level_temp.append("Facultad de Ingeniería")
    info_level.append(infoe_level_temp)
    infoe_level_temp = []
    infoe_level_temp.append("Escuela de Ciencias y Sistemas")
    info_level.append(infoe_level_temp)
    # TYPE OF REPORT
    infoe_level_temp = []
    infoe_level_temp.append(T("Type"))
    infoe_level_temp.append(T("Metrics Management Course Activities"))
    info_level.append(infoe_level_temp)
    # DESCRIPTION OF REPORT
    infoe_level_temp = []
    infoe_level_temp.append(T("Description"))
    infoe_level_temp.append(T("Report of operations management activities metric course"))
    info_level.append(infoe_level_temp)
    # LEVELS OF REPORT
    # ALL SEMESTERS
    if request.vars["level"] is None or str(request.vars["level"]) == "1":
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T("Total inserted"))
        infoe_level_temp.append(T("Total modified"))
        infoe_level_temp.append(T("Total out"))
        info_level.append(infoe_level_temp)
        for period in db(db.period_year).select(orderby=~db.period_year.id):
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # INSERT
            if personal_query == "":
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.operation_log = "insert"'
                )
            else:
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.operation_log = "insert" and '
                    + personal_query
                )
            count_i = db.smart_query(db.course_activity_log, search).count()
            infoe_level_temp.append(count_i)
            # UPDATE
            if personal_query == "":
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.operation_log = "update"'
                )
            else:
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.operation_log = "update" and '
                    + personal_query
                )
            count_i = db.smart_query(db.course_activity_log, search).count()
            infoe_level_temp.append(count_i)
            # DELETE
            if personal_query == "":
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.operation_log = "delete"'
                )
            else:
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.operation_log = "delete" and '
                    + personal_query
                )
            count_i = db.smart_query(db.course_activity_log, search).count()
            infoe_level_temp.append(count_i)
            # INSERT PERIOD
            info_level.append(infoe_level_temp)
    # PER MONTH
    elif str(request.vars["level"]) == "2":
        # PERIOD OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "i":
            infoe_level_temp.append(T("Total inserted"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "u":
            infoe_level_temp.append(T("Total modified"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "d":
            infoe_level_temp.append(T("Total out"))
        info_level.append(infoe_level_temp)

        for month in get_month_period(period):
            start = datetime.strptime(
                str(period.yearp) + "-" + str(month[0]) + "-01", "%Y-%m-%d"
            )
            if month[2] == 1:
                end = datetime.strptime(
                    str(period.yearp + 1) + "-" + str(month[2]) + "-01", "%Y-%m-%d"
                )
            else:
                end = datetime.strptime(
                    str(period.yearp) + "-" + str(month[2]) + "-01", "%Y-%m-%d"
                )
            infoe_level_temp = []
            # NAME OF MONTH
            infoe_level_temp.append(month[1] + " " + str(period.yearp))
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "insert" and course_activity_log.date_log >="'
                        + str(start)
                        + '" and course_activity_log.date_log<"'
                        + str(end)
                        + '"'
                    )
                else:
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "insert" and course_activity_log.date_log >="'
                        + str(start)
                        + '" and course_activity_log.date_log<"'
                        + str(end)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.course_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "update" and course_activity_log.date_log>="'
                        + str(start)
                        + '" and course_activity_log.date_log<"'
                        + str(end)
                        + '"'
                    )
                else:
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "update" and course_activity_log.date_log>="'
                        + str(start)
                        + '" and course_activity_log.date_log<"'
                        + str(end)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.course_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "delete" and course_activity_log.date_log>="'
                        + str(start)
                        + '" and course_activity_log.date_log<"'
                        + str(end)
                        + '"'
                    )
                else:
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "delete" and course_activity_log.date_log>="'
                        + str(start)
                        + '" and course_activity_log.date_log<"'
                        + str(end)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.course_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # INSERT MONTH
            info_level.append(infoe_level_temp)
    # PER PROJECT
    elif str(request.vars["level"]) == "3":
        # PROJECTS
        # projects = get_projects('course_activity_log')
        try:
            projects = get_projects("course_activity_log", period)
        except:
            projects = get_projects("course_activity_log", None)
        projects = sorted(projects)
        # PERIOD OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MONTH OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        infoe_level_temp.append(str(month[0]))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Project"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "i":
            infoe_level_temp.append(T("Total inserted"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "u":
            infoe_level_temp.append(T("Total modified"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "d":
            infoe_level_temp.append(T("Total out"))
        info_level.append(infoe_level_temp)

        for projectT in projects:
            project = db(db.project.name == projectT).select().first()
            if project is None:
                project = db(db.course_activity_log.course == projectT).select().first()
                project = project.project
            else:
                project = project.name
            infoe_level_temp = []
            # NAME OF PROJECT
            infoe_level_temp.append(project)
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "insert" and course_activity_log.date_log >="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + project
                        + '"'
                    )
                else:
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "insert" and course_activity_log.date_log >="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + project
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.course_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "update" and course_activity_log.date_log>="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + project
                        + '"'
                    )
                else:
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "update" and course_activity_log.date_log>="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + project
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.course_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "delete" and course_activity_log.date_log>="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + project
                        + '"'
                    )
                else:
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "delete" and course_activity_log.date_log>="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + project
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.course_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # INSERT PROJECT
            info_level.append(infoe_level_temp)
    # PER ROL
    elif str(request.vars["level"]) == "4":
        # ROLES
        roles = get_roles("course_activity_log")
        # PERIOD OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MONTH OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        infoe_level_temp.append(str(month[0]))
        info_level.append(infoe_level_temp)
        # PROJECT OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Project"))
        infoe_level_temp.append(str(project))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Role"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "i":
            infoe_level_temp.append(T("Total inserted"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "u":
            infoe_level_temp.append(T("Total modified"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "d":
            infoe_level_temp.append(T("Total out"))
        info_level.append(infoe_level_temp)

        for roll_t in roles:
            roll = db(db.auth_group.role == roll_t).select().first()
            if roll is None:
                roll = db(db.course_activity_log.roll == roll_t).select().first()
                roll = roll.roll
            else:
                roll = roll.role
            infoe_level_temp = []
            # NAME OF ROLE
            infoe_level_temp.append(T("Rol " + roll))
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "insert" and course_activity_log.date_log >="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + str(project)
                        + '" and course_activity_log.roll ="'
                        + str(roll)
                        + '"'
                    )
                else:
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "insert" and course_activity_log.date_log >="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + str(project)
                        + '" and course_activity_log.roll ="'
                        + str(roll)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.course_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "update" and course_activity_log.date_log>="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + str(project)
                        + '" and course_activity_log.roll ="'
                        + str(roll)
                        + '"'
                    )
                else:
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "update" and course_activity_log.date_log>="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + str(project)
                        + '" and course_activity_log.roll ="'
                        + str(roll)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.course_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "delete" and course_activity_log.date_log>="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + str(project)
                        + '" and course_activity_log.roll ="'
                        + str(roll)
                        + '"'
                    )
                else:
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "delete" and course_activity_log.date_log>="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + str(project)
                        + '" and course_activity_log.roll ="'
                        + str(roll)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.course_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # INSERT PROJECT
            info_level.append(infoe_level_temp)
    # PER USER
    elif str(request.vars["level"]) == "5":
        # USERS
        usersProject = get_users(period, project, roll, "course_activity_log")
        # PERIOD OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MONTH OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        infoe_level_temp.append(str(month[0]))
        info_level.append(infoe_level_temp)
        # PROJECT OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Project"))
        infoe_level_temp.append(str(project))
        info_level.append(infoe_level_temp)
        # ROL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Role"))
        infoe_level_temp.append(T("Rol " + roll))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("User"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "i":
            infoe_level_temp.append(T("Total inserted"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "u":
            infoe_level_temp.append(T("Total modified"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "d":
            infoe_level_temp.append(T("Total out"))
        info_level.append(infoe_level_temp)

        for user_p_t in usersProject:
            user_p = db(db.auth_user.username == user_p_t).select().first()
            if user_p is None:
                user_p = db(db.course_activity_log.user_name == user_p_t).select().first()
                user_p = user_p.user_name
            else:
                user_p = user_p.username
            infoe_level_temp = []
            # NAME OF USER
            infoe_level_temp.append(user_p)
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "insert" and course_activity_log.date_log >="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + str(project)
                        + '" and course_activity_log.roll ="'
                        + str(roll)
                        + '" and course_activity_log.user_name ="'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "insert" and course_activity_log.date_log >="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + str(project)
                        + '" and course_activity_log.roll ="'
                        + str(roll)
                        + '" and course_activity_log.user_name ="'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.course_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "update" and course_activity_log.date_log>="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + str(project)
                        + '" and course_activity_log.roll ="'
                        + str(roll)
                        + '" and course_activity_log.user_name ="'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "update" and course_activity_log.date_log>="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + str(project)
                        + '" and course_activity_log.roll ="'
                        + str(roll)
                        + '" and course_activity_log.user_name ="'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.course_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "delete" and course_activity_log.date_log>="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + str(project)
                        + '" and course_activity_log.roll ="'
                        + str(roll)
                        + '" and course_activity_log.user_name ="'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "delete" and course_activity_log.date_log>="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + str(project)
                        + '" and course_activity_log.roll ="'
                        + str(roll)
                        + '" and course_activity_log.user_name ="'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.course_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # INSERT PROJECT
            info_level.append(infoe_level_temp)
    # DATA
    elif str(request.vars["level"]) == "6":
        if str(request.vars["type_L"]) == "all":
            if personal_query == "":
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.date_log >="'
                    + str(month[1])
                    + '" and course_activity_log.date_log<"'
                    + str(month[2])
                    + '" and course_activity_log.course ="'
                    + str(project)
                    + '" and course_activity_log.roll ="'
                    + str(roll)
                    + '" and course_activity_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.date_log >="'
                    + str(month[1])
                    + '" and course_activity_log.date_log<"'
                    + str(month[2])
                    + '" and course_activity_log.course ="'
                    + str(project)
                    + '" and course_activity_log.roll ="'
                    + str(roll)
                    + '" and course_activity_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
        elif str(request.vars["type_L"]) == "i":
            if personal_query == "":
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.operation_log = "insert" and course_activity_log.date_log >="'
                    + str(month[1])
                    + '" and course_activity_log.date_log<"'
                    + str(month[2])
                    + '" and course_activity_log.course ="'
                    + str(project)
                    + '" and course_activity_log.roll ="'
                    + str(roll)
                    + '" and course_activity_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.operation_log = "insert" and course_activity_log.date_log >="'
                    + str(month[1])
                    + '" and course_activity_log.date_log<"'
                    + str(month[2])
                    + '" and course_activity_log.course ="'
                    + str(project)
                    + '" and course_activity_log.roll ="'
                    + str(roll)
                    + '" and course_activity_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
        elif str(request.vars["type_L"]) == "u":
            if personal_query == "":
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.operation_log = "update" and course_activity_log.date_log >="'
                    + str(month[1])
                    + '" and course_activity_log.date_log<"'
                    + str(month[2])
                    + '" and course_activity_log.course ="'
                    + str(project)
                    + '" and course_activity_log.roll ="'
                    + str(roll)
                    + '" and course_activity_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.operation_log = "update" and course_activity_log.date_log >="'
                    + str(month[1])
                    + '" and course_activity_log.date_log<"'
                    + str(month[2])
                    + '" and course_activity_log.course ="'
                    + str(project)
                    + '" and course_activity_log.roll ="'
                    + str(roll)
                    + '" and course_activity_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
        elif str(request.vars["type_L"]) == "d":
            if personal_query == "":
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.operation_log = "delete" and course_activity_log.date_log >="'
                    + str(month[1])
                    + '" and course_activity_log.date_log<"'
                    + str(month[2])
                    + '" and course_activity_log.course ="'
                    + str(project)
                    + '" and course_activity_log.roll ="'
                    + str(roll)
                    + '" and course_activity_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.operation_log = "delete" and course_activity_log.date_log >="'
                    + str(month[1])
                    + '" and course_activity_log.date_log<"'
                    + str(month[2])
                    + '" and course_activity_log.course ="'
                    + str(project)
                    + '" and course_activity_log.roll ="'
                    + str(roll)
                    + '" and course_activity_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
        # PERIOD
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MONTH
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        infoe_level_temp.append(str(month[0]))
        info_level.append(infoe_level_temp)
        # PROJECT
        infoe_level_temp = []
        infoe_level_temp.append(T("Project"))
        infoe_level_temp.append(str(project))
        info_level.append(infoe_level_temp)
        # ROL
        infoe_level_temp = []
        infoe_level_temp.append(T("Role"))
        infoe_level_temp.append(T("Rol " + roll))
        info_level.append(infoe_level_temp)
        # USER
        infoe_level_temp = []
        infoe_level_temp.append(T("User"))
        infoe_level_temp.append(str(user_p))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE
        infoe_level_temp = []
        infoe_level_temp.append("")
        info_level.append(infoe_level_temp)
        # DETAIL
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # TITLE OF TABLE
        infoe_level_temp = []
        infoe_level_temp.append("Operación")
        infoe_level_temp.append("Categoria Anterior")
        infoe_level_temp.append("Categoria Actual")
        infoe_level_temp.append("Nombre Anterior")
        infoe_level_temp.append("Nombre Actual")
        infoe_level_temp.append("Descripcion Anterior")
        infoe_level_temp.append("Descripcion Actual")
        infoe_level_temp.append("Nota Anterior")
        infoe_level_temp.append("Nota Actual")
        infoe_level_temp.append("Laboratorio Anterior")
        infoe_level_temp.append("Laboratorio Actual")
        infoe_level_temp.append("Permiso Catedratico Anterior")
        infoe_level_temp.append("Permiso Catedratico Actual")
        infoe_level_temp.append("Fecha Inicio Anterior")
        infoe_level_temp.append("Fecha Inicio Actual")
        infoe_level_temp.append("Fecha Finalizacion Anterior")
        infoe_level_temp.append("Fecha Finalizacion Actual")
        infoe_level_temp.append("Fecha")
        info_level.append(infoe_level_temp)
        for operation in db.smart_query(db.course_activity_log, search).select():
            infoe_level_temp = []
            infoe_level_temp.append(operation.operation_log)
            infoe_level_temp.append(operation.before_course_activity_category)
            infoe_level_temp.append(operation.after_course_activity_category)
            infoe_level_temp.append(operation.before_name)
            infoe_level_temp.append(operation.after_name)
            infoe_level_temp.append(operation.before_description)
            infoe_level_temp.append(operation.after_description)
            infoe_level_temp.append(operation.before_grade)
            infoe_level_temp.append(operation.after_grade)
            infoe_level_temp.append(operation.before_laboratory)
            infoe_level_temp.append(operation.after_laboratory)
            infoe_level_temp.append(operation.before_teacher_permition)
            infoe_level_temp.append(operation.after_teacher_permition)
            infoe_level_temp.append(operation.before_date_start)
            infoe_level_temp.append(operation.after_date_start)
            infoe_level_temp.append(operation.before_date_finish)
            infoe_level_temp.append(operation.after_date_finish)
            infoe_level_temp.append(operation.date_log)
            info_level.append(infoe_level_temp)
    # *****************************************************REPORT*****************************************************
    # ****************************************************************************************************************
    # ****************************************************************************************************************
    return dict(filename="ReporteGestionActividadesConMetrica", csvdata=info_level)


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def activities_with_metric_management():
    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # ***************************************CHECK IF THERE IS A PERSONALIZED QUERY***********************************
    personal_query = ""
    make_redirect = False
    if (
        request.vars["querySearch"] is not None
        and str(request.vars["querySearch"]) != ""
    ):
        # PERSONALIZED QUERY SURE WORK
        try:
            personal_query = str(request.vars["querySearch"])
            count_i = db.smart_query(db.course_activity_log, personal_query).count()
            if (
                request.vars["searchT"] is not None
                and str(request.vars["searchT"]) == "T"
            ):
                make_redirect = True
        except:
            response.flash = T(
                "The query is not valid. The report is displayed without applying any query."
            )
            personal_query = ""
    if make_redirect == True:
        redirect(
            URL(
                "management_reports",
                "activities_with_metric_management",
                vars=dict(
                    level=6,
                    period=request.vars["period"],
                    month=str(request.vars["month"]),
                    project=str(request.vars["project"]),
                    roll=str(request.vars["roll"]),
                    userP=str(request.vars["userP"]),
                    type_L=request.vars["type_L"],
                    type_U=request.vars["type_U"],
                    querySearch=request.vars["querySearch"],
                ),
            )
        )

    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # ******************************************VERIFY THAT ACCURATE PARAMETERS***************************************
    try:
        # CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars["level"] is not None and (
            int(request.vars["level"]) < 1 or int(request.vars["level"]) > 6
        ):
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))

        # VERIFY THAT THE PARAMETERS OF EACH LEVEL BE VALID
        if request.vars["level"] is not None:
            # LEVEL MORE THAN 1
            if int(request.vars["level"]) > 1:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_L"] is None or (
                    str(request.vars["type_L"]) != "all"
                    and str(request.vars["type_L"]) != "i"
                    and str(request.vars["type_L"]) != "u"
                    and str(request.vars["type_L"]) != "d"
                ):
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

                period = validate_period(request.vars["period"])
                if period is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 2
            if int(request.vars["level"]) > 2:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_U"] is None or (
                    str(request.vars["type_U"]) != "all"
                    and str(request.vars["type_U"]) != "i"
                    and str(request.vars["type_U"]) != "u"
                    and str(request.vars["type_U"]) != "d"
                ):
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

                # CHECK IF THE MONTH IS VALID
                month = validate_month(request.vars["month"], period)
                if month is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 3
            if int(request.vars["level"]) > 3:
                # CHECK IF THE PROJECT IS VALID
                project = validate_project(
                    request.vars["project"], "course_activity_log"
                )
                if project is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 4
            if int(request.vars["level"]) > 4:
                # CHECK IF THE ROLE IS VALID
                roll = validate_role(request.vars["roll"], "course_activity_log")
                if roll is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 5
            if int(request.vars["level"]) > 5:
                # CHECK IF THE USER IS VALID
                user_p = validate_user(
                    period, project, roll, request.vars["userP"], "course_activity_log"
                )
                if user_p is None:
                    session.flash = T("Not valid Action.")
                    redi * rect(URL("default", "index"))
    except:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # **************************************************SEARCH REPORT*************************************************
    def filtered_by(flag):
        fsearch_option = []
        fsearch_option.append("=")
        fsearch_option.append("!=")
        fsearch_option.append("<")
        fsearch_option.append(">")
        fsearch_option.append("<=")
        fsearch_option.append(">=")
        if flag == True:
            fsearch_option.append("starts with")
            fsearch_option.append("contains")
            fsearch_option.append("in")
            fsearch_option.append("not in")
        return fsearch_option

    fsearch = []
    # ******************************COMBOS INFORMATION******************************
    # YEARS
    if request.vars["level"] == "1" or request.vars["level"] is None:
        group_years = get_years()
        if len(group_years) != 0:
            fsearch.append(["yearp", "Año", False, [3, sorted(group_years)]])
    # PROJECTS
    if request.vars["level"] is None or int(request.vars["level"]) <= 3:
        # projects = get_projects('course_activity_log')
        try:
            projects = get_projects("course_activity_log", period)
        except:
            projects = get_projects("course_activity_log", None)
        if len(projects) != 0:
            fsearch_values = []
            fsearch_values.append(4)
            for project_t in projects:
                project = db(db.project.name == project_t).select().first()
                if project is None:
                    project = (
                        db(db.course_activity_log.course == project_t).select().first()
                    )
                    project = project.course
                else:
                    project = project.name
                fsearch_values.append(project)
            fsearch.append(["course", "Curso", False, fsearch_values])
    # ROLES
    if request.vars["level"] is None or int(request.vars["level"]) <= 4:
        roles = get_roles("course_activity_log")
        if len(roles) != 0:
            fsearch.append(["roll", "Rol", False, [5, sorted(roles)]])
    # CATEGORIES BEFORE
    group_categories = get_categories("course_activity_log")
    if len(group_categories) != 0:
        fsearch.append(
            [
                "before_course_activity_category",
                "Categoria Anterior",
                False,
                [3, sorted(group_categories)],
            ]
        )
    # CATEGORIES AFTER
    if len(group_categories) != 0:
        fsearch.append(
            [
                "after_course_activity_category",
                "Categoria Actual",
                False,
                [3, sorted(group_categories)],
            ]
        )
    # ACTIVITIES BEFORE
    group_activities = get_activities("course_activity_log")
    if len(group_activities) != 0:
        fsearch.append(
            ["before_name", "Nombre Anterior", False, [3, sorted(group_activities)]]
        )
    # ACTIVITIES AFTER
    if len(group_activities) != 0:
        fsearch.append(
            ["after_name", "Nombre Actual", False, [3, sorted(group_activities)]]
        )
    # DATE
    group_dates = get_dates("course_activity_log")
    if len(group_dates) != 0:
        fsearch.append(["date_log", "Fecha", False, [3, sorted(group_dates)]])
    # OPERATION LOG
    fsearch.append(
        ["operation_log", "Operación", False, [3, ["insert", "update", "delete"]]]
    )
    # ******************************ENTERING USER******************************
    if request.vars["level"] is None or int(request.vars["level"]) <= 5:
        # ID OF PERSON WHO REGISTER THE GRADE
        fsearch.append(["user_name", "Usuario Registro", True, [1]])
    # BEFORE DESCRIPTION OF ACTIVITY
    fsearch.append(["before_description", "Descripción Anterior", True, [1]])
    # OFFICIAL DESCRIPTION OF ACTIVITY
    fsearch.append(["after_description", "Descripción Actual", True, [1]])
    # BEFORE GRADE
    fsearch.append(["before_grade", "Nota Anterior", False, [1]])
    # OFFICIAL GRADE
    fsearch.append(["after_grade", "Nota Actual", False, [1]])
    # BEFORE DATE START
    fsearch.append(["before_date_start", "Fecha Inicio Anterior", False, [2]])
    # OFFICIAL DATE START
    fsearch.append(["after_date_start", "Fecha Inicio Actual", False, [2]])
    # BEFORE DATE FINISH
    fsearch.append(["before_date_finish", "Fecha Finalizacion Anterior", False, [2]])
    # OFFICIAL DATE FINISH
    fsearch.append(["after_date_finish", "Fecha Finalizacion Actual", False, [2]])
    # LABORATORY BEFORE
    fsearch.append(
        ["before_laboratory", "Laboratorio Anterior", False, [6, ["True", "False"]]]
    )
    # LABORATORY AFTER
    fsearch.append(
        ["after_laboratory", "Laboratorio Actual", False, [6, ["True", "False"]]]
    )
    # PERMITION TEACHER BEFORE
    fsearch.append(
        [
            "before_teacher_permition",
            "Permiso Catedratico Anterior",
            False,
            [6, ["True", "False"]],
        ]
    )
    # PERMITION TEACHER AFTER
    fsearch.append(
        [
            "after_teacher_permition",
            "Permiso Catedratico Actual",
            False,
            [6, ["True", "False"]],
        ]
    )

    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # *****************************************************REPORT*****************************************************
    # LEVELS OF REPORT
    
    info_level = []
    top5 = []
    grid = None
    # ALL SEMESTERS
    if request.vars["level"] is None or str(request.vars["level"]) == "1":
        if db(db.period_year).select().first() is None:
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(URL("default", "home"))

        for period in db(db.period_year).select(orderby=~db.period_year.id):
            infoe_level_temp = []
            # ID OF PERIOD
            infoe_level_temp.append(period.id)
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # INSERT
            if personal_query == "":
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.operation_log = "insert"'
                )
            else:
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.operation_log = "insert" and '
                    + personal_query
                )
            count_i = db.smart_query(db.course_activity_log, search).count()
            infoe_level_temp.append(count_i)
            # UPDATE
            if personal_query == "":
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.operation_log = "update"'
                )
            else:
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.operation_log = "update" and '
                    + personal_query
                )
            count_i = db.smart_query(db.course_activity_log, search).count()
            infoe_level_temp.append(count_i)
            # DELETE
            if personal_query == "":
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.operation_log = "delete"'
                )
            else:
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.operation_log = "delete" and '
                    + personal_query
                )
            count_i = db.smart_query(db.course_activity_log, search).count()
            infoe_level_temp.append(count_i)
            # INSERT PERIOD
            info_level.append(infoe_level_temp)

        # TOP 5 OF PERIOD
        if personal_query == "":
            search = 'course_activity_log.id != "-1"'
        else:
            search = personal_query
        top5 = db.smart_query(db.course_activity_log, search).select(
            db.course_activity_log.period,
            db.course_activity_log.yearp,
            db.course_activity_log.id.count().with_alias('count'),
            orderby=~db.course_activity_log.id.count(),
            limitby=(0, 5),
            groupby=[db.course_activity_log.period, db.course_activity_log.yearp],
        )
    # PER MONTH
    elif str(request.vars["level"]) == "2":
        for month in get_month_period(period):
            start = datetime.strptime(
                str(period.yearp) + "-" + str(month[0]) + "-01", "%Y-%m-%d"
            )
            if month[2] == 1:
                end = datetime.strptime(
                    str(period.yearp + 1) + "-" + str(month[2]) + "-01", "%Y-%m-%d"
                )
            else:
                end = datetime.strptime(
                    str(period.yearp) + "-" + str(month[2]) + "-01", "%Y-%m-%d"
                )
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # ID OF MONTH
            infoe_level_temp.append(month[0])
            # NAME OF MONTH
            infoe_level_temp.append(month[1] + " " + str(period.yearp))
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "insert" and course_activity_log.date_log >="'
                        + str(start)
                        + '" and course_activity_log.date_log<"'
                        + str(end)
                        + '"'
                    )
                else:
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "insert" and course_activity_log.date_log >="'
                        + str(start)
                        + '" and course_activity_log.date_log<"'
                        + str(end)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.course_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "update" and course_activity_log.date_log>="'
                        + str(start)
                        + '" and course_activity_log.date_log<"'
                        + str(end)
                        + '"'
                    )
                else:
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "update" and course_activity_log.date_log>="'
                        + str(start)
                        + '" and course_activity_log.date_log<"'
                        + str(end)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.course_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "delete" and course_activity_log.date_log>="'
                        + str(start)
                        + '" and course_activity_log.date_log<"'
                        + str(end)
                        + '"'
                    )
                else:
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "delete" and course_activity_log.date_log>="'
                        + str(start)
                        + '" and course_activity_log.date_log<"'
                        + str(end)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.course_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # INSERT MONTH
            info_level.append(infoe_level_temp)
    # PER PROJECT
    elif str(request.vars["level"]) == "3":
        if len(projects) == 0:
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(
                URL(
                    "management_reports",
                    "activities_with_metric_management",
                    vars=dict(
                        level="2",
                        period=str(request.vars["period"]),
                        type_L=str(request.vars["type_U"]),
                        querySearch=personal_query,
                    ),
                )
            )
        projects = sorted(projects)

        for project_t in projects:
            project = db(db.project.name == project_t).select().first()
            if project is None:
                project = db(db.course_activity_log.course == project_t).select().first()
                project = project.project
            else:
                project = project.name
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # NAME OF MONTH
            infoe_level_temp.append(month[0])
            # ID OF PROJECT
            infoe_level_temp.append(project)
            # NAME OF PROJECT
            infoe_level_temp.append(project)
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "insert" and course_activity_log.date_log >="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + project
                        + '"'
                    )
                else:
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "insert" and course_activity_log.date_log >="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + project
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.course_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "update" and course_activity_log.date_log>="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + project
                        + '"'
                    )
                else:
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "update" and course_activity_log.date_log>="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + project
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.course_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "delete" and course_activity_log.date_log>="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + project
                        + '"'
                    )
                else:
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "delete" and course_activity_log.date_log>="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + project
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.course_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # INSERT PROJECT
            info_level.append(infoe_level_temp)

        # TOP 5 OF PROJECT
        if personal_query == "":
            search = (
                'course_activity_log.period = "'
                + T(period.period.name)
                + '" and course_activity_log.yearp = "'
                + str(period.yearp)
                + '" and course_activity_log.date_log >="'
                + str(month[1])
                + '" and course_activity_log.date_log<"'
                + str(month[2])
                + '"'
            )
        else:
            search = (
                'course_activity_log.period = "'
                + T(period.period.name)
                + '" and course_activity_log.yearp = "'
                + str(period.yearp)
                + '" and course_activity_log.date_log >="'
                + str(month[1])
                + '" and course_activity_log.date_log<"'
                + str(month[2])
                + '" and '
                + personal_query
            )
        top5 = db.smart_query(db.course_activity_log, search).select(
            db.course_activity_log.course,
            db.course_activity_log.id.count().with_alias('count'),
            orderby=~db.course_activity_log.id.count(),
            limitby=(0, 5),
            groupby=db.course_activity_log.course,
        )
    # PER ROL
    elif str(request.vars["level"]) == "4":
        if len(roles) == 0:
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(
                URL(
                    "management_reports",
                    "activities_with_metric_management",
                    vars=dict(
                        level="3",
                        period=str(request.vars["period"]),
                        month=str(request.vars["month"]),
                        type_L=str(request.vars["type_U"]),
                        type_U=str(request.vars["type_U"]),
                        querySearch=personal_query,
                    ),
                )
            )

        for roll_t in roles:
            roll = db(db.auth_group.role == roll_t).select().first()
            if roll is None:
                roll = db(db.course_activity_log.roll == roll_t).select().first()
                roll = roll.roll
            else:
                roll = roll.role
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # NAME OF MONTH
            infoe_level_temp.append(month[0])
            # NAME OF PROJECT
            infoe_level_temp.append(project)
            # ID OF ROLE
            infoe_level_temp.append(roll)
            # NAME OF ROLE
            infoe_level_temp.append(T("Rol " + roll))
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "insert" and course_activity_log.date_log >="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + str(project)
                        + '" and course_activity_log.roll ="'
                        + str(roll)
                        + '"'
                    )
                else:
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "insert" and course_activity_log.date_log >="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + str(project)
                        + '" and course_activity_log.roll ="'
                        + str(roll)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.course_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "update" and course_activity_log.date_log>="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + str(project)
                        + '" and course_activity_log.roll ="'
                        + str(roll)
                        + '"'
                    )
                else:
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "update" and course_activity_log.date_log>="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + str(project)
                        + '" and course_activity_log.roll ="'
                        + str(roll)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.course_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "delete" and course_activity_log.date_log>="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + str(project)
                        + '" and course_activity_log.roll ="'
                        + str(roll)
                        + '"'
                    )
                else:
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "delete" and course_activity_log.date_log>="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + str(project)
                        + '" and course_activity_log.roll ="'
                        + str(roll)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.course_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # INSERT PROJECT
            info_level.append(infoe_level_temp)
    # PER USER
    elif str(request.vars["level"]) == "5":
        # VERIFY THAT CAN SHOW THE LEVEL OF THE REPORT
        users_project = get_users(period, project, roll, "course_activity_log")
        if len(users_project) == 0:
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(
                URL(
                    "management_reports",
                    "activities_with_metric_management",
                    vars=dict(
                        level="4",
                        period=str(request.vars["period"]),
                        month=str(request.vars["month"]),
                        project=str(request.vars["project"]),
                        type_L=str(request.vars["type_U"]),
                        type_U=str(request.vars["type_U"]),
                        querySearch=personal_query,
                    ),
                )
            )

        for user_p_t in users_project:
            user_p = db(db.auth_user.username == user_p_t).select().first()
            if user_p is None:
                user_p = db(db.course_activity_log.user_name == user_p_t).select().first()
                user_p = user_p.user_name
            else:
                user_p = user_p.username
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # NAME OF MONTH
            infoe_level_temp.append(month[0])
            # NAME OF PROJECT
            infoe_level_temp.append(project)
            # NAME OF ROLE
            infoe_level_temp.append(T("Rol " + roll))
            # ID OF USER
            infoe_level_temp.append(user_p)
            # NAME OF USER
            infoe_level_temp.append(user_p)
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "insert" and course_activity_log.date_log >="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + str(project)
                        + '" and course_activity_log.roll ="'
                        + str(roll)
                        + '" and course_activity_log.user_name ="'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "insert" and course_activity_log.date_log >="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + str(project)
                        + '" and course_activity_log.roll ="'
                        + str(roll)
                        + '" and course_activity_log.user_name ="'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.course_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "update" and course_activity_log.date_log>="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + str(project)
                        + '" and course_activity_log.roll ="'
                        + str(roll)
                        + '" and course_activity_log.user_name ="'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "update" and course_activity_log.date_log>="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + str(project)
                        + '" and course_activity_log.roll ="'
                        + str(roll)
                        + '" and course_activity_log.user_name ="'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.course_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "delete" and course_activity_log.date_log>="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + str(project)
                        + '" and course_activity_log.roll ="'
                        + str(roll)
                        + '" and course_activity_log.user_name ="'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'course_activity_log.period = "'
                        + T(period.period.name)
                        + '" and course_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and course_activity_log.operation_log = "delete" and course_activity_log.date_log>="'
                        + str(month[1])
                        + '" and course_activity_log.date_log<"'
                        + str(month[2])
                        + '" and course_activity_log.course ="'
                        + str(project)
                        + '" and course_activity_log.roll ="'
                        + str(roll)
                        + '" and course_activity_log.user_name ="'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.course_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # INSERT PROJECT
            info_level.append(infoe_level_temp)
    # DATA
    elif str(request.vars["level"]) == "6":
        if str(request.vars["type_L"]) == "all":
            if personal_query == "":
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.date_log >="'
                    + str(month[1])
                    + '" and course_activity_log.date_log<"'
                    + str(month[2])
                    + '" and course_activity_log.course ="'
                    + str(project)
                    + '" and course_activity_log.roll ="'
                    + str(roll)
                    + '" and course_activity_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.date_log >="'
                    + str(month[1])
                    + '" and course_activity_log.date_log<"'
                    + str(month[2])
                    + '" and course_activity_log.course ="'
                    + str(project)
                    + '" and course_activity_log.roll ="'
                    + str(roll)
                    + '" and course_activity_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
        elif str(request.vars["type_L"]) == "i":
            if personal_query == "":
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.operation_log = "insert" and course_activity_log.date_log >="'
                    + str(month[1])
                    + '" and course_activity_log.date_log<"'
                    + str(month[2])
                    + '" and course_activity_log.course ="'
                    + str(project)
                    + '" and course_activity_log.roll ="'
                    + str(roll)
                    + '" and course_activity_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.operation_log = "insert" and course_activity_log.date_log >="'
                    + str(month[1])
                    + '" and course_activity_log.date_log<"'
                    + str(month[2])
                    + '" and course_activity_log.course ="'
                    + str(project)
                    + '" and course_activity_log.roll ="'
                    + str(roll)
                    + '" and course_activity_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
        elif str(request.vars["type_L"]) == "u":
            if personal_query == "":
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.operation_log = "update" and course_activity_log.date_log >="'
                    + str(month[1])
                    + '" and course_activity_log.date_log<"'
                    + str(month[2])
                    + '" and course_activity_log.course ="'
                    + str(project)
                    + '" and course_activity_log.roll ="'
                    + str(roll)
                    + '" and course_activity_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.operation_log = "update" and course_activity_log.date_log >="'
                    + str(month[1])
                    + '" and course_activity_log.date_log<"'
                    + str(month[2])
                    + '" and course_activity_log.course ="'
                    + str(project)
                    + '" and course_activity_log.roll ="'
                    + str(roll)
                    + '" and course_activity_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
        elif str(request.vars["type_L"]) == "d":
            if personal_query == "":
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.operation_log = "delete" and course_activity_log.date_log >="'
                    + str(month[1])
                    + '" and course_activity_log.date_log<"'
                    + str(month[2])
                    + '" and course_activity_log.course ="'
                    + str(project)
                    + '" and course_activity_log.roll ="'
                    + str(roll)
                    + '" and course_activity_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'course_activity_log.period = "'
                    + T(period.period.name)
                    + '" and course_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and course_activity_log.operation_log = "delete" and course_activity_log.date_log >="'
                    + str(month[1])
                    + '" and course_activity_log.date_log<"'
                    + str(month[2])
                    + '" and course_activity_log.course ="'
                    + str(project)
                    + '" and course_activity_log.roll ="'
                    + str(roll)
                    + '" and course_activity_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
        grid = []
        for data in db.smart_query(db.course_activity_log, search).select():
            grid.append(data.id)
        # REPORT
        if len(grid) == 0:
            grid.append(-1)

        infoe_level_temp = []
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        infoe_level_temp.append(str(month[0]))
        infoe_level_temp.append(str(project))
        infoe_level_temp.append(T("Rol " + roll))
        infoe_level_temp.append(str(user_p))
        info_level.append(infoe_level_temp)
        # GRID
        db.course_activity_log.id.readable = False
        db.course_activity_log.id.writable = False
        db.course_activity_log.user_name.readable = False
        db.course_activity_log.user_name.writable = False
        db.course_activity_log.roll.readable = False
        db.course_activity_log.roll.writable = False
        db.course_activity_log.course.readable = False
        db.course_activity_log.course.writable = False
        db.course_activity_log.yearp.readable = False
        db.course_activity_log.yearp.writable = False
        db.course_activity_log.period.readable = False
        db.course_activity_log.period.writable = False
        db.course_activity_log.metric.readable = False
        db.course_activity_log.metric.writable = False
        db.course_activity_log.before_file.readable = False
        db.course_activity_log.before_file.writable = False
        db.course_activity_log.after_file.readable = False
        db.course_activity_log.after_file.writable = False
        grid = SQLFORM.grid(
            db.course_activity_log.id.belongs(grid),
            csv=False,
            create=False,
            editable=False,
            deletable=False,
            paginate=9,
            searchable=False,
        )
    return dict(
        fsearch=fsearch,
        filtered_by=filtered_by,
        personal_query=personal_query,
        infoLevel=info_level,
        top5=top5,
        grid=grid,
    )


#*************************************************************************************************************************************
#*************************************************************************************************************************************
#*****************************************************MANAGEMENT REPORT STUDENTS******************************************************


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def student_management_export():
    # VERIFI THAT ACCURATE PARAMETERS
    try:
        # CHECK IF THE TYPE OF EXPORT IS VALID
        if request.vars["list_type"] is None or str(request.vars["list_type"]) != "csv":
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))

        # CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars["level"] is not None and (
            int(request.vars["level"]) < 1 or int(request.vars["level"]) > 5
        ):
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(URL("default", "home"))

        # VERIFY THAT THE PARAMETERS OF EACH LEVEL BE VALID
        if request.vars["level"] is not None:
            # LEVEL MORE THAN 1
            if int(request.vars["level"]) > 1:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_L"] is None or (
                    str(request.vars["type_L"]) != "all"
                    and str(request.vars["type_L"]) != "i"
                    and str(request.vars["type_L"]) != "u"
                    and str(request.vars["type_L"]) != "d"
                ):
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

                period = validate_period(request.vars["period"])
                if period is None:
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 2
            if int(request.vars["level"]) > 2:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_U"] is None or (
                    str(request.vars["type_U"]) != "all"
                    and str(request.vars["type_U"]) != "i"
                    and str(request.vars["type_U"]) != "u"
                    and str(request.vars["type_U"]) != "d"
                ):
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

                # CHECK IF THE MONTH IS VALID
                month = validate_month(request.vars["month"], period)
                if month is None:
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 3
            if int(request.vars["level"]) > 3:
                # CHECK IF THE ROLE IS VALID
                roll = validate_role(request.vars["roll"], "academic_log")
                if roll is None:
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 4
            if int(request.vars["level"]) > 4:
                # CHECK IF THE USER IS VALID
                user_p = validate_user(
                    period, None, roll, request.vars["userP"], "academic_log"
                )
                if user_p is None:
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))
    except:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    # CHECK IF THERE IS A PERSONALIZED QUERY
    personal_query = ""
    if (
        request.vars["querySearch"] is not None
        and str(request.vars["querySearch"]) != ""
    ):
        # PERSONALIZED QUERY SURE WORK
        try:
            personal_query = str(request.vars["querySearch"])
            count_i = db.smart_query(db.academic_log, personal_query).count()
        except:
            personal_query = ""

    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # *****************************************************REPORT*****************************************************

    # TITLE
    info_level = []
    infoe_level_temp = []
    infoe_level_temp.append("Universidad de San Carlos de Guatemala")
    info_level.append(infoe_level_temp)
    infoe_level_temp = []
    infoe_level_temp.append("Facultad de Ingeniería")
    info_level.append(infoe_level_temp)
    infoe_level_temp = []
    infoe_level_temp.append("Escuela de Ciencias y Sistemas")
    info_level.append(infoe_level_temp)
    # TYPE OF REPORT
    infoe_level_temp = []
    infoe_level_temp.append(T("Type"))
    infoe_level_temp.append(T("Management Students"))
    info_level.append(infoe_level_temp)
    # DESCRIPTION OF REPORT
    infoe_level_temp = []
    infoe_level_temp.append(T("Description"))
    infoe_level_temp.append(T("Report of operations management students"))
    info_level.append(infoe_level_temp)
    # LEVELS OF REPORT
    # ALL SEMESTERS
    if request.vars["level"] is None or str(request.vars["level"]) == "1":
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T("Total inserted"))
        infoe_level_temp.append(T("Total modified"))
        infoe_level_temp.append(T("Total out"))
        info_level.append(infoe_level_temp)
        for period in db(db.period_year).select(orderby=~db.period_year.id):
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # INSERT
            if personal_query == "":
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.operation_log = "insert"'
                )
            else:
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.operation_log = "insert" and '
                    + personal_query
                )
            count_i = db.smart_query(db.academic_log, search).count()
            infoe_level_temp.append(count_i)
            # UPDATE
            if personal_query == "":
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.operation_log = "update"'
                )
            else:
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.operation_log = "update" and '
                    + personal_query
                )
            count_i = db.smart_query(db.academic_log, search).count()
            infoe_level_temp.append(count_i)
            # DELETE
            if personal_query == "":
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.operation_log = "delete"'
                )
            else:
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.operation_log = "delete" and '
                    + personal_query
                )
            count_i = db.smart_query(db.academic_log, search).count()
            infoe_level_temp.append(count_i)
            # INSERT PERIOD
            info_level.append(infoe_level_temp)
    # PER MONTH
    elif str(request.vars["level"]) == "2":
        # PERIOD OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "i":
            infoe_level_temp.append(T("Total inserted"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "u":
            infoe_level_temp.append(T("Total modified"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "d":
            infoe_level_temp.append(T("Total out"))
        info_level.append(infoe_level_temp)

        for month in get_month_period(period):
            start = datetime.strptime(
                str(period.yearp) + "-" + str(month[0]) + "-01", "%Y-%m-%d"
            )
            if month[2] == 1:
                end = datetime.strptime(
                    str(period.yearp + 1) + "-" + str(month[2]) + "-01", "%Y-%m-%d"
                )
            else:
                end = datetime.strptime(
                    str(period.yearp) + "-" + str(month[2]) + "-01", "%Y-%m-%d"
                )
            infoe_level_temp = []
            # NAME OF MONTH
            infoe_level_temp.append(month[1] + " " + str(period.yearp))
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "insert" and academic_log.date_log >="'
                        + str(start)
                        + '" and academic_log.date_log<"'
                        + str(end)
                        + '"'
                    )
                else:
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "insert" and academic_log.date_log >="'
                        + str(start)
                        + '" and academic_log.date_log<"'
                        + str(end)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.academic_log, search).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "update" and academic_log.date_log>="'
                        + str(start)
                        + '" and academic_log.date_log<"'
                        + str(end)
                        + '"'
                    )
                else:
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "update" and academic_log.date_log>="'
                        + str(start)
                        + '" and academic_log.date_log<"'
                        + str(end)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.academic_log, search).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "delete" and academic_log.date_log>="'
                        + str(start)
                        + '" and academic_log.date_log<"'
                        + str(end)
                        + '"'
                    )
                else:
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "delete" and academic_log.date_log>="'
                        + str(start)
                        + '" and academic_log.date_log<"'
                        + str(end)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.academic_log, search).count()
                infoe_level_temp.append(count_i)
            # INSERT MONTH
            info_level.append(infoe_level_temp)
    # PER ROL
    elif str(request.vars["level"]) == "3":

        # ROLES
        roles = get_roles("academic_log")
        # PERIOD OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MONTH OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        infoe_level_temp.append(str(month[0]))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Role"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "i":
            infoe_level_temp.append(T("Total inserted"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "u":
            infoe_level_temp.append(T("Total modified"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "d":
            infoe_level_temp.append(T("Total out"))
        info_level.append(infoe_level_temp)

        for rollT in roles:
            roll = db(db.auth_group.role == rollT).select().first()
            if roll is None:
                roll = db(db.academic_log.roll == rollT).select().first()
                roll = roll.roll
            else:
                roll = roll.role
            infoe_level_temp = []
            # NAME OF ROLE
            infoe_level_temp.append(T("Rol " + roll))
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "insert" and academic_log.date_log >="'
                        + str(month[1])
                        + '" and academic_log.date_log<"'
                        + str(month[2])
                        + '" and academic_log.roll contains "'
                        + str(roll)
                        + '"'
                    )
                else:
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "insert" and academic_log.date_log >="'
                        + str(month[1])
                        + '" and academic_log.date_log<"'
                        + str(month[2])
                        + '" and academic_log.roll contains "'
                        + str(roll)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.academic_log, search).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "update" and academic_log.date_log >="'
                        + str(month[1])
                        + '" and academic_log.date_log<"'
                        + str(month[2])
                        + '" and academic_log.roll contains "'
                        + str(roll)
                        + '"'
                    )
                else:
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "update" and academic_log.date_log >="'
                        + str(month[1])
                        + '" and academic_log.date_log<"'
                        + str(month[2])
                        + '" and academic_log.roll contains "'
                        + str(roll)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.academic_log, search).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "delete" and academic_log.date_log >="'
                        + str(month[1])
                        + '" and academic_log.date_log<"'
                        + str(month[2])
                        + '" and academic_log.roll contains "'
                        + str(roll)
                        + '"'
                    )
                else:
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "delete" and academic_log.date_log >="'
                        + str(month[1])
                        + '" and academic_log.date_log<"'
                        + str(month[2])
                        + '" and academic_log.roll contains "'
                        + str(roll)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.academic_log, search).count()
                infoe_level_temp.append(count_i)
            # INSERT PROJECT
            info_level.append(infoe_level_temp)
    # PER USER
    elif str(request.vars["level"]) == "4":
        # VERIFY THAT CAN SHOW THE LEVEL OF THE REPORT
        users_project = get_users(period, None, roll, "academic_log")
        # PERIOD OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MONTH OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        infoe_level_temp.append(str(month[0]))
        info_level.append(infoe_level_temp)
        # ROL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Role"))
        infoe_level_temp.append(T("Rol " + roll))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("User"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "i":
            infoe_level_temp.append(T("Total inserted"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "u":
            infoe_level_temp.append(T("Total modified"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "d":
            infoe_level_temp.append(T("Total out"))
        info_level.append(infoe_level_temp)

        for user_p_t in users_project:
            user_p = db(db.auth_user.username == user_p_t).select().first()
            if user_p is None:
                user_p = db(db.academic_log.user_name == user_p_t).select().first()
                user_p = user_p.user_name
            else:
                user_p = user_p.username
            infoe_level_temp = []
            # NAME OF USER
            infoe_level_temp.append(user_p)
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "insert" and academic_log.date_log >="'
                        + str(month[1])
                        + '" and academic_log.date_log<"'
                        + str(month[2])
                        + '" and academic_log.roll contains "'
                        + str(roll)
                        + '" and academic_log.user_name ="'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "insert" and academic_log.date_log >="'
                        + str(month[1])
                        + '" and academic_log.date_log<"'
                        + str(month[2])
                        + '" and academic_log.roll contains "'
                        + str(roll)
                        + '" and academic_log.user_name ="'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.academic_log, search).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "update" and academic_log.date_log >="'
                        + str(month[1])
                        + '" and academic_log.date_log<"'
                        + str(month[2])
                        + '" and academic_log.roll contains "'
                        + str(roll)
                        + '" and academic_log.user_name ="'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "update" and academic_log.date_log >="'
                        + str(month[1])
                        + '" and academic_log.date_log<"'
                        + str(month[2])
                        + '" and academic_log.roll contains "'
                        + str(roll)
                        + '" and academic_log.user_name ="'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.academic_log, search).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "delete" and academic_log.date_log >="'
                        + str(month[1])
                        + '" and academic_log.date_log<"'
                        + str(month[2])
                        + '" and academic_log.roll contains "'
                        + str(roll)
                        + '" and academic_log.user_name ="'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "delete" and academic_log.date_log >="'
                        + str(month[1])
                        + '" and academic_log.date_log<"'
                        + str(month[2])
                        + '" and academic_log.roll contains "'
                        + str(roll)
                        + '" and academic_log.user_name ="'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.academic_log, search).count()
                infoe_level_temp.append(count_i)
            # INSERT PROJECT
            info_level.append(infoe_level_temp)
    # DATA
    elif str(request.vars["level"]) == "5":
        if str(request.vars["type_L"]) == "all":
            if personal_query == "":
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.date_log >="'
                    + str(month[1])
                    + '" and academic_log.date_log<"'
                    + str(month[2])
                    + '" and academic_log.roll contains "'
                    + str(roll)
                    + '" and academic_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.date_log >="'
                    + str(month[1])
                    + '" and academic_log.date_log<"'
                    + str(month[2])
                    + '" and academic_log.roll contains "'
                    + str(roll)
                    + '" and academic_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
        elif str(request.vars["type_L"]) == "i":
            if personal_query == "":
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.operation_log = "insert" and academic_log.date_log >="'
                    + str(month[1])
                    + '" and academic_log.date_log<"'
                    + str(month[2])
                    + '" and academic_log.roll contains "'
                    + str(roll)
                    + '" and academic_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.operation_log = "insert" and academic_log.date_log >="'
                    + str(month[1])
                    + '" and academic_log.date_log<"'
                    + str(month[2])
                    + '" and academic_log.roll contains "'
                    + str(roll)
                    + '" and academic_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
        elif str(request.vars["type_L"]) == "u":
            if personal_query == "":
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.operation_log = "update" and academic_log.date_log >="'
                    + str(month[1])
                    + '" and academic_log.date_log<"'
                    + str(month[2])
                    + '" and academic_log.roll contains "'
                    + str(roll)
                    + '" and academic_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.operation_log = "update" and academic_log.date_log >="'
                    + str(month[1])
                    + '" and academic_log.date_log<"'
                    + str(month[2])
                    + '" and academic_log.roll contains "'
                    + str(roll)
                    + '" and academic_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
        elif str(request.vars["type_L"]) == "d":
            if personal_query == "":
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.operation_log = "delete" and academic_log.date_log >="'
                    + str(month[1])
                    + '" and academic_log.date_log<"'
                    + str(month[2])
                    + '" and academic_log.roll contains "'
                    + str(roll)
                    + '" and academic_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.operation_log = "delete" and academic_log.date_log >="'
                    + str(month[1])
                    + '" and academic_log.date_log<"'
                    + str(month[2])
                    + '" and academic_log.roll contains "'
                    + str(roll)
                    + '" and academic_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
        # PERIOD
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MONTH
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        infoe_level_temp.append(str(month[0]))
        info_level.append(infoe_level_temp)
        # ROL
        infoe_level_temp = []
        infoe_level_temp.append(T("Role"))
        infoe_level_temp.append(T("Rol " + roll))
        info_level.append(infoe_level_temp)
        # USER
        infoe_level_temp = []
        infoe_level_temp.append(T("User"))
        infoe_level_temp.append(str(user_p))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE
        infoe_level_temp = []
        infoe_level_temp.append("")
        info_level.append(infoe_level_temp)
        # DETAIL
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # TITLE OF TABLE
        infoe_level_temp = []
        infoe_level_temp.append(T("Operacion"))
        infoe_level_temp.append(T("Carnet anterior"))
        infoe_level_temp.append(T("Carnet actual"))
        infoe_level_temp.append(T("Correo anterior"))
        infoe_level_temp.append(T("Correo actual"))
        infoe_level_temp.append(T("Descripcion"))
        infoe_level_temp.append(T("Fecha"))
        info_level.append(infoe_level_temp)
        for operation in db.smart_query(db.academic_log, search).select():
            infoe_level_temp = []
            infoe_level_temp.append(operation.operation_log)
            infoe_level_temp.append(operation.before_carnet)
            infoe_level_temp.append(operation.after_carnet)
            infoe_level_temp.append(operation.before_email)
            infoe_level_temp.append(operation.after_email)
            infoe_level_temp.append(operation.description)
            infoe_level_temp.append(operation.date_log)
            info_level.append(infoe_level_temp)
    # *****************************************************REPORT*****************************************************
    # ****************************************************************************************************************
    # ****************************************************************************************************************
    return dict(filename="ReporteGestionEstudiantes", csvdata=info_level)


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def student_management():
    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # ***************************************CHECK IF THERE IS A PERSONALIZED QUERY***********************************
    personal_query = ""

    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # ******************************************VERIFY THAT ACCURATE PARAMETERS***************************************
    try:
        # CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars["level"] is not None and (int(request.vars["level"]) < 1 or int(request.vars["level"]) > 5):
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))

        # VERIFY THAT THE PARAMETERS OF EACH LEVEL BE VALID
        if request.vars["level"] is not None:
            # LEVEL MORE THAN 1
            if int(request.vars["level"]) > 1:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_L"] is None or (
                    str(request.vars["type_L"]) != "all"
                    and str(request.vars["type_L"]) != "i"
                    and str(request.vars["type_L"]) != "u"
                    and str(request.vars["type_L"]) != "d"
                ):
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

                period = validate_period(request.vars["period"])
                if period is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))
            # LEVEL MORE THAN 2
            if int(request.vars["level"]) > 2:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_U"] is None or (
                    str(request.vars["type_U"]) != "all"
                    and str(request.vars["type_U"]) != "i"
                    and str(request.vars["type_U"]) != "u"
                    and str(request.vars["type_U"]) != "d"
                ):
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

                # CHECK IF THE MONTH IS VALID
                month = validate_month(request.vars["month"], period)
                if month is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))
            # LEVEL MORE THAN 3
            if int(request.vars["level"]) > 3:
                # CHECK IF THE ROLE IS VALID
                roll = validate_role(request.vars["roll"], "academic_log")
                if roll is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 4
            if int(request.vars["level"]) > 4:
                # CHECK IF THE USER IS VALID
                user_p = validate_user(
                    period, None, roll, request.vars["userP"], "academic_log"
                )
                if user_p is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))
    except:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # *****************************************************REPORT*****************************************************
    # LEVELS OF REPORT
    
    info_level = []
    top5 = []
    grid = None
    # ALL SEMESTERS
    if request.vars["level"] == "1" or request.vars["level"] is None:
        group_periods = db(db.period_year).select(orderby=~db.period_year.id)
        if len(group_periods) == 0:
            session.flash = T("Report no visible: There are no parameters required to display the report.")
            redirect(URL("default", "home"))

        for period in group_periods:
            infoe_level_temp = []
            # ID OF PERIOD
            infoe_level_temp.append(period.id)
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # INSERT
            count_i = db((db.academic_log.id_period == period.id) & (db.academic_log.operation_log == 'insert')).count()
            infoe_level_temp.append(count_i)
            # UPDATE
            count_i = count_i = db((db.academic_log.id_period == period.id) & (db.academic_log.operation_log == 'update')).count()
            infoe_level_temp.append(count_i)
            # DELETE
            count_i = count_i = db((db.academic_log.id_period == period.id) & (db.academic_log.operation_log == 'delete')).count()
            infoe_level_temp.append(count_i)
            # INSERT PERIOD
            info_level.append(infoe_level_temp)

        # TOP 5 OF PERIOD
        top5 = db(db.academic_log).select(
            db.academic_log.id_period,
            db.academic_log.id.count().with_alias('count'),
            orderby=~db.academic_log.id.count(),
            limitby=(0, 5),
            groupby=db.academic_log.id_period,
        )
        top5_t = []
        for top in top5:
            period_top = db(db.period_year.id == top["academic_log.id_period"]).select(db.period_year.yearp, db.period_year.period).first()
            top5_t.append([f"{T(period_top.period.name)} {period_top.yearp}", top["count"]])
        top5 = top5_t
    # PER MONTH
    elif request.vars["level"] == "2":
        for month in get_month_period(period):
            start = datetime.strptime(
                str(period.yearp) + "-" + str(month[0]) + "-01", "%Y-%m-%d"
            )
            if month[2] == 1:
                end = datetime.strptime(
                    str(period.yearp + 1) + "-" + str(month[2]) + "-01", "%Y-%m-%d"
                )
            else:
                end = datetime.strptime(
                    str(period.yearp) + "-" + str(month[2]) + "-01", "%Y-%m-%d"
                )
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # ID OF MONTH
            infoe_level_temp.append(month[0])
            # NAME OF MONTH
            infoe_level_temp.append(month[1] + " " + str(period.yearp))
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.operation_log = "insert" and academic_log.date_log >="'
                    + str(start)
                    + '" and academic_log.date_log<"'
                    + str(end)
                    + '"'
                )
                count_i = db.smart_query(db.academic_log, search).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.operation_log = "update" and academic_log.date_log>="'
                    + str(start)
                    + '" and academic_log.date_log<"'
                    + str(end)
                    + '"'
                )
                count_i = db.smart_query(db.academic_log, search).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "delete" and academic_log.date_log>="'
                        + str(start)
                        + '" and academic_log.date_log<"'
                        + str(end)
                        + '"'
                    )
                else:
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "delete" and academic_log.date_log>="'
                        + str(start)
                        + '" and academic_log.date_log<"'
                        + str(end)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.academic_log, search).count()
                infoe_level_temp.append(count_i)
            # INSERT MONTH
            info_level.append(infoe_level_temp)
    # PER ROL
    elif request.vars["level"] == "3":
        roles = get_roles("academic_log")
        if len(roles) == 0:
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(
                URL(
                    "management_reports",
                    "student_management",
                    vars=dict(
                        level="2",
                        period=str(request.vars["period"]),
                        month=str(request.vars["month"]),
                        type_L=str(request.vars["type_U"]),
                        type_U=str(request.vars["type_U"]),
                    ),
                )
            )

        for roll_t in roles:
            roll = db(db.auth_group.role == roll_t).select().first()
            if roll is None:
                roll = db(db.academic_log.roll.like("%" + roll_t + "%")).select().first()
                roll = roll.roll
            else:
                roll = roll.role
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # NAME OF MONTH
            infoe_level_temp.append(month[0])
            # ID OF ROLE
            infoe_level_temp.append(roll)
            # NAME OF ROLE
            infoe_level_temp.append(T("Rol " + roll))
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.operation_log = "insert" and academic_log.date_log >="'
                    + str(month[1])
                    + '" and academic_log.date_log<"'
                    + str(month[2])
                    + '" and academic_log.roll contains "'
                    + str(roll)
                    + '"'
                )
                count_i = db.smart_query(db.academic_log, search).count()
                print(count_i, search, db._lastsql)
                infoe_level_temp.append(count_i)
            # UPDATE  
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "update" and academic_log.date_log >="'
                        + str(month[1])
                        + '" and academic_log.date_log<"'
                        + str(month[2])
                        + '" and academic_log.roll contains "'
                        + str(roll)
                        + '"'
                    )
                else:
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "update" and academic_log.date_log >="'
                        + str(month[1])
                        + '" and academic_log.date_log<"'
                        + str(month[2])    
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.academic_log, search).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "delete" and academic_log.date_log >="'
                        + str(month[1])
                        + '" and academic_log.date_log<"'
                        + str(month[2])
                        + '" and academic_log.roll contains "'
                        + str(roll)
                        + '"'
                    )
                else:
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "delete" and academic_log.date_log >="'
                        + str(month[1])
                        + '" and academic_log.date_log<"'
                        + str(month[2])
                        + '" and academic_log.roll contains "'
                        + str(roll)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.academic_log, search).count()
                infoe_level_temp.append(count_i)
            # INSERT PROJECT
            info_level.append(infoe_level_temp)
    # PER USER
    elif request.vars["level"] == "4":
        # VERIFY THAT CAN SHOW THE LEVEL OF THE REPORT
        users_project = get_users(period, None, roll, "academic_log")
        if len(users_project) == 0:
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(
                URL(
                    "management_reports",
                    "student_management",
                    vars=dict(
                        level="3",
                        period=str(request.vars["period"]),
                        month=str(request.vars["month"]),
                        type_L=str(request.vars["type_U"]),
                        type_U=str(request.vars["type_U"]),
                    ),
                )
            )

        for user_p_t in users_project:
            user_p = db(db.auth_user.username == user_p_t).select().first()
            if user_p is None:
                user_p = db(db.academic_log.user_name == user_p_t).select().first()
                user_p = user_p.user_name
            else:
                user_p = user_p.username
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # NAME OF MONTH
            infoe_level_temp.append(month[0])
            # NAME OF ROLE
            infoe_level_temp.append(T("Rol " + roll))
            # ID OF USER
            infoe_level_temp.append(user_p)
            # NAME OF USER
            infoe_level_temp.append(user_p)
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "insert" and academic_log.date_log >="'
                        + str(month[1])
                        + '" and academic_log.date_log<"'
                        + str(month[2])
                        + '" and academic_log.roll contains "'
                        + str(roll)
                        + '" and academic_log.user_name ="'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "insert" and academic_log.date_log >="'
                        + str(month[1])
                        + '" and academic_log.date_log<"'
                        + str(month[2])
                        + '" and academic_log.roll contains "'
                        + str(roll)
                        + '" and academic_log.user_name ="'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.academic_log, search).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "update" and academic_log.date_log >="'
                        + str(month[1])
                        + '" and academic_log.date_log<"'
                        + str(month[2])
                        + '" and academic_log.roll contains "'
                        + str(roll)
                        + '" and academic_log.user_name ="'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "update" and academic_log.date_log >="'
                        + str(month[1])
                        + '" and academic_log.date_log<"'
                        + str(month[2])
                        + '" and academic_log.roll contains "'
                        + str(roll)
                        + '" and academic_log.user_name ="'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.academic_log, search).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "delete" and academic_log.date_log >="'
                        + str(month[1])
                        + '" and academic_log.date_log<"'
                        + str(month[2])
                        + '" and academic_log.roll contains "'
                        + str(roll)
                        + '" and academic_log.user_name ="'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'academic_log.id_period = "'
                        + str(period.id)
                        + '" and academic_log.operation_log = "delete" and academic_log.date_log >="'
                        + str(month[1])
                        + '" and academic_log.date_log<"'
                        + str(month[2])
                        + '" and academic_log.roll contains "'
                        + str(roll)
                        + '" and academic_log.user_name ="'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.academic_log, search).count()
                infoe_level_temp.append(count_i)
            # INSERT PROJECT
            info_level.append(infoe_level_temp)

        # TOP 5 OF USERS
        if personal_query == "":
            search = (
                'academic_log.id_period = "'
                + str(period.id)
                + '" and academic_log.date_log >="'
                + str(month[1])
                + '" and academic_log.date_log<"'
                + str(month[2])
                + '" and academic_log.roll contains "'
                + str(roll)
                + '"'
            )
        else:
            search = (
                'academic_log.id_period = "'
                + str(period.id)
                + '" and academic_log.date_log >="'
                + str(month[1])
                + '" and academic_log.date_log<"'
                + str(month[2])
                + '" and academic_log.roll contains "'
                + str(roll)
                + '" and '
                + personal_query
            )
        top5 = db.smart_query(db.academic_log, search).select(
            db.academic_log.user_name,
            db.academic_log.id.count().with_alias('count'),
            orderby=~db.academic_log.id.count(),
            limitby=(0, 5),
            groupby=db.academic_log.user_name,
        )
    # DATA
    elif request.vars["level"] == "5":
        if str(request.vars["type_L"]) == "all":
            if personal_query == "":
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.date_log >="'
                    + str(month[1])
                    + '" and academic_log.date_log<"'
                    + str(month[2])
                    + '" and academic_log.roll LIKE "%'
                    + str(roll)
                    + '%" and academic_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.date_log >="'
                    + str(month[1])
                    + '" and academic_log.date_log<"'
                    + str(month[2])
                    + '" and academic_log.roll LIKE "%'
                    + str(roll)
                    + '%" and academic_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
        elif str(request.vars["type_L"]) == "i":
            if personal_query == "":
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.operation_log = "insert" and academic_log.date_log >="'
                    + str(month[1])
                    + '" and academic_log.date_log<"'
                    + str(month[2])
                    + '" and academic_log.roll LIKE "%'
                    + str(roll)
                    + '%" and academic_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.operation_log = "insert" and academic_log.date_log >="'
                    + str(month[1])
                    + '" and academic_log.date_log<"'
                    + str(month[2])
                    + '" and academic_log.roll LIKE "%'
                    + str(roll)
                    + '%" and academic_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
        elif str(request.vars["type_L"]) == "u":
            if personal_query == "":
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.operation_log = "update" and academic_log.date_log >="'
                    + str(month[1])
                    + '" and academic_log.date_log<"'
                    + str(month[2])
                    + '" and academic_log.roll LIKE "%'
                    + str(roll)
                    + '%" and academic_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.operation_log = "update" and academic_log.date_log >="'
                    + str(month[1])
                    + '" and academic_log.date_log<"'
                    + str(month[2])
                    + '" and academic_log.roll LIKE "%'
                    + str(roll)
                    + '%" and academic_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
        elif str(request.vars["type_L"]) == "d":
            if personal_query == "":
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.operation_log = "delete" and academic_log.date_log >="'
                    + str(month[1])
                    + '" and academic_log.date_log<"'
                    + str(month[2])
                    + '" and academic_log.roll LIKE "%'
                    + str(roll)
                    + '%" and academic_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'academic_log.id_period = "'
                    + str(period.id)
                    + '" and academic_log.operation_log = "delete" and academic_log.date_log >="'
                    + str(month[1])
                    + '" and academic_log.date_log<"'
                    + str(month[2])
                    + '" and academic_log.roll LIKE "%'
                    + str(roll)
                    + '%" and academic_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
        grid = []
        for data in db.smart_query(db.academic_log, search).select():
            grid.append(data.id)
        # REPORT
        if len(grid) == 0:
            grid.append(-1)
        infoe_level_temp = []
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        infoe_level_temp.append(str(month[0]))
        infoe_level_temp.append(T("Rol " + roll))
        infoe_level_temp.append(str(user_p))
        info_level.append(infoe_level_temp)
        # GRID
        db.academic_log.id.readable = False
        db.academic_log.id.writable = False
        db.academic_log.user_name.readable = False
        db.academic_log.user_name.writable = False
        db.academic_log.roll.readable = False
        db.academic_log.roll.writable = False
        db.academic_log.id_academic.readable = False
        db.academic_log.id_academic.writable = False
        db.academic_log.id_period.readable = False
        db.academic_log.id_period.writable = False
        grid = SQLFORM.grid(
            db.academic_log.id.belongs(grid),
            csv=False,
            create=False,
            editable=False,
            deletable=False,
            paginate=9,
            searchable=False,
        )
    return dict(
        infoLevel=info_level,
        top5=top5,
        grid=grid,
    )


#*************************************************************************************************************************************
#*************************************************************************************************************************************
#*****************************************************MANAGEMENT REPORT STUDENTS ASSIGNMENT*******************************************


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def student_assignment_management_export():
    # VERIFI THAT ACCURATE PARAMETERS
    try:
        # CHECK IF THE TYPE OF EXPORT IS VALID
        if request.vars["list_type"] is None or str(request.vars["list_type"]) != "csv":
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))

        # CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars["level"] is not None and (
            int(request.vars["level"]) < 1 or int(request.vars["level"]) > 6
        ):
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(URL("default", "home"))

        # VERIFY THAT THE PARAMETERS OF EACH LEVEL BE VALID
        if request.vars["level"] is not None:
            # LEVEL MORE THAN 1
            if int(request.vars["level"]) > 1:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_L"] is None or (
                    str(request.vars["type_L"]) != "all"
                    and str(request.vars["type_L"]) != "i"
                    and str(request.vars["type_L"]) != "u"
                    and str(request.vars["type_L"]) != "d"
                ):
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

                period = validate_period(request.vars["period"])
                if period is None:
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 2
            if int(request.vars["level"]) > 2:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_U"] is None or (
                    str(request.vars["type_U"]) != "all"
                    and str(request.vars["type_U"]) != "i"
                    and str(request.vars["type_U"]) != "u"
                    and str(request.vars["type_U"]) != "d"
                ):
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

                # CHECK IF THE MONTH IS VALID
                month = validate_month(request.vars["month"], period)
                if month is None:
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 3
            if int(request.vars["level"]) > 3:
                # CHECK IF THE PROJECT IS VALID
                project = validate_project(
                    request.vars["project"], "academic_course_assignation_log"
                )
                if project is None:
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))
            # LEVEL MORE THAN 4
            if int(request.vars["level"]) > 4:
                # CHECK IF THE ROLE IS VALID
                roll = validate_role(
                    request.vars["roll"], "academic_course_assignation_log"
                )
                if roll is None:
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 5
            if int(request.vars["level"]) > 5:
                # CHECK IF THE USER IS VALID
                user_p = validate_user(
                    period,
                    project,
                    roll,
                    request.vars["userP"],
                    "academic_course_assignation_log",
                )
                if user_p is None:
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redi * rect(URL("default", "index"))
    except:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    # CHECK IF THERE IS A PERSONALIZED QUERY
    personal_query = ""
    if (
        request.vars["querySearch"] is not None
        and str(request.vars["querySearch"]) != ""
    ):
        # PERSONALIZED QUERY SURE WORK
        try:
            personal_query = str(request.vars["querySearch"])
            count_i = db.smart_query(
                db.academic_course_assignation_log, personal_query
            ).count()
        except:
            personal_query = ""

    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # *****************************************************REPORT*****************************************************
    
    # TITLE
    info_level = []
    infoe_level_temp = []
    infoe_level_temp.append("Universidad de San Carlos de Guatemala")
    info_level.append(infoe_level_temp)
    infoe_level_temp = []
    infoe_level_temp.append("Facultad de Ingeniería")
    info_level.append(infoe_level_temp)
    infoe_level_temp = []
    infoe_level_temp.append("Escuela de Ciencias y Sistemas")
    info_level.append(infoe_level_temp)
    # TYPE OF REPORT
    infoe_level_temp = []
    infoe_level_temp.append(T("Type"))
    infoe_level_temp.append(T("Student Assignment Management"))
    info_level.append(infoe_level_temp)
    # DESCRIPTION OF REPORT
    infoe_level_temp = []
    infoe_level_temp.append(T("Description"))
    infoe_level_temp.append(T("Report of operations management assignment of students"))
    info_level.append(infoe_level_temp)
    # LEVELS OF REPORT
    # ALL SEMESTERS
    if request.vars["level"] is None or str(request.vars["level"]) == "1":
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T("Total inserted"))
        infoe_level_temp.append(T("Total modified"))
        infoe_level_temp.append(T("Total out"))
        info_level.append(infoe_level_temp)
        for period in db(db.period_year).select(orderby=~db.period_year.id):
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # INSERT
            if personal_query == "":
                search = (
                    'academic_course_assignation_log.id_period = "'
                    + str(period.id)
                    + '" and academic_course_assignation_log.operation_log = "insert"'
                )
            else:
                search = (
                    'academic_course_assignation_log.id_period = "'
                    + str(period.id)
                    + '" and academic_course_assignation_log.operation_log = "insert" and '
                    + personal_query
                )
            count_i = db.smart_query(db.academic_course_assignation_log, search).count()
            infoe_level_temp.append(count_i)
            # UPDATE
            if personal_query == "":
                search = (
                    'academic_course_assignation_log.id_period = "'
                    + str(period.id)
                    + '" and academic_course_assignation_log.operation_log = "update"'
                )
            else:
                search = (
                    'academic_course_assignation_log.id_period = "'
                    + str(period.id)
                    + '" and academic_course_assignation_log.operation_log = "update" and '
                    + personal_query
                )
            count_i = db.smart_query(db.academic_course_assignation_log, search).count()
            infoe_level_temp.append(count_i)
            # DELETE
            if personal_query == "":
                search = (
                    'academic_course_assignation_log.id_period = "'
                    + str(period.id)
                    + '" and academic_course_assignation_log.operation_log = "delete"'
                )
            else:
                search = (
                    'academic_course_assignation_log.id_period = "'
                    + str(period.id)
                    + '" and academic_course_assignation_log.operation_log = "delete" and '
                    + personal_query
                )
            count_i = db.smart_query(db.academic_course_assignation_log, search).count()
            infoe_level_temp.append(count_i)
            # INSERT PERIOD
            info_level.append(infoe_level_temp)
    # PER MONTH
    elif str(request.vars["level"]) == "2":
        # PERIOD OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "i":
            infoe_level_temp.append(T("Total inserted"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "u":
            infoe_level_temp.append(T("Total modified"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "d":
            infoe_level_temp.append(T("Total out"))
        info_level.append(infoe_level_temp)

        for month in get_month_period(period):
            start = datetime.strptime(
                str(period.yearp) + "-" + str(month[0]) + "-01", "%Y-%m-%d"
            )
            if month[2] == 1:
                end = datetime.strptime(
                    str(period.yearp + 1) + "-" + str(month[2]) + "-01", "%Y-%m-%d"
                )
            else:
                end = datetime.strptime(
                    str(period.yearp) + "-" + str(month[2]) + "-01", "%Y-%m-%d"
                )
            infoe_level_temp = []
            # NAME OF MONTH
            infoe_level_temp.append(month[1] + " " + str(period.yearp))
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "insert" and academic_course_assignation_log.date_log >="'
                        + str(start)
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(end)
                        + '"'
                    )
                else:
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "insert" and academic_course_assignation_log.date_log >="'
                        + str(start)
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(end)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(
                    db.academic_course_assignation_log, search
                ).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "update" and academic_course_assignation_log.date_log>="'
                        + str(start)
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(end)
                        + '"'
                    )
                else:
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "update" and academic_course_assignation_log.date_log>="'
                        + str(start)
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(end)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(
                    db.academic_course_assignation_log, search
                ).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "delete" and academic_course_assignation_log.date_log>="'
                        + str(start)
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(end)
                        + '"'
                    )
                else:
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "delete" and academic_course_assignation_log.date_log>="'
                        + str(start)
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(end)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(
                    db.academic_course_assignation_log, search
                ).count()
                infoe_level_temp.append(count_i)
            # INSERT MONTH
            info_level.append(infoe_level_temp)
    # PER PROJECT
    elif str(request.vars["level"]) == "3":
        # PROJECTS
        # projects = get_projects('academic_course_assignation_log')
        try:
            projects = get_projects("academic_course_assignation_log", period)
        except:
            projects = get_projects("academic_course_assignation_log", None)
        projects = sorted(projects)
        # PERIOD OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MONTH OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        infoe_level_temp.append(str(month[0]))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Project"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "i":
            infoe_level_temp.append(T("Total inserted"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "u":
            infoe_level_temp.append(T("Total modified"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "d":
            infoe_level_temp.append(T("Total out"))
        info_level.append(infoe_level_temp)

        for project_t in projects:
            project = db(db.project.name == project_t).select().first()
            if project is None:
                project = (
                    db(
                        (db.course_activity_log.before_course == project_t)
                        | (db.course_activity_log.after_course == project_t)
                    )
                    .select()
                    .first()
                )
                if project.before_course is not None:
                    project = project.before_course
                else:
                    project = project.after_course
            else:
                project = project.name
            infoe_level_temp = []
            # NAME OF PROJECT
            infoe_level_temp.append(project)
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "insert" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.after_course = "'
                        + str(project)
                        + '"'
                    )
                else:
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "insert" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.after_course = "'
                        + str(project)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(
                    db.academic_course_assignation_log, search
                ).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "update" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.after_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.before_course = "'
                        + str(project)
                        + '"'
                    )
                else:
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "update" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.after_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.before_course = "'
                        + str(project)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(
                    db.academic_course_assignation_log, search
                ).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "delete" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.before_course = "'
                        + str(project)
                        + '"'
                    )
                else:
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "delete" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.before_course = "'
                        + str(project)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(
                    db.academic_course_assignation_log, search
                ).count()
                infoe_level_temp.append(count_i)
            # INSERT PROJECT
            info_level.append(infoe_level_temp)
    # PER ROL
    elif str(request.vars["level"]) == "4":
        # ROLES
        roles = get_roles("academic_course_assignation_log")
        # PERIOD OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MONTH OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        infoe_level_temp.append(str(month[0]))
        info_level.append(infoe_level_temp)
        # PROJECT OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Project"))
        infoe_level_temp.append(str(project))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Role"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "i":
            infoe_level_temp.append(T("Total inserted"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "u":
            infoe_level_temp.append(T("Total modified"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "d":
            infoe_level_temp.append(T("Total out"))
        info_level.append(infoe_level_temp)

        for roll_t in roles:
            roll = db(db.auth_group.role == roll_t).select().first()
            if roll is None:
                roll = (
                    db(db.academic_course_assignation_log.roll.like("%" + roll_t + "%"))
                    .select()
                    .first()
                )
                roll = roll.roll
            else:
                roll = roll.role
            infoe_level_temp = []
            # NAME OF ROLE
            infoe_level_temp.append(T("Rol " + roll))
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "insert" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.after_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.roll contains "'
                        + str(roll)
                        + '"'
                    )
                else:
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "insert" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.after_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.roll contains "'
                        + str(roll)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(
                    db.academic_course_assignation_log, search
                ).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "update" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.before_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.after_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.roll contains "'
                        + str(roll)
                        + '"'
                    )
                else:
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "update" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.before_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.after_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.roll contains "'
                        + str(roll)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(
                    db.academic_course_assignation_log, search
                ).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "delete" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.before_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.roll contains "'
                        + str(roll)
                        + '"'
                    )
                else:
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "delete" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.before_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.roll contains "'
                        + str(roll)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(
                    db.academic_course_assignation_log, search
                ).count()
                infoe_level_temp.append(count_i)
            # INSERT ROLE
            info_level.append(infoe_level_temp)
    # PER USER
    elif str(request.vars["level"]) == "5":
        # USERS
        users_project = get_users(
            period, project, roll, "academic_course_assignation_log"
        )
        # PERIOD OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MONTH OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        infoe_level_temp.append(str(month[0]))
        info_level.append(infoe_level_temp)
        # PROJECT OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Project"))
        infoe_level_temp.append(str(project))
        info_level.append(infoe_level_temp)
        # ROL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Role"))
        infoe_level_temp.append(T("Rol " + roll))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("User"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "i":
            infoe_level_temp.append(T("Total inserted"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "u":
            infoe_level_temp.append(T("Total modified"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "d":
            infoe_level_temp.append(T("Total out"))
        info_level.append(infoe_level_temp)

        for user_p_t in users_project:
            user_p = db(db.auth_user.username == user_p_t).select().first()
            if user_p is None:
                user_p = (
                    db(db.academic_course_assignation_log.user_name == user_p_t)
                    .select()
                    .first()
                )
                user_p = user_p.user_name
            else:
                user_p = user_p.username
            infoe_level_temp = []
            # NAME OF USER
            infoe_level_temp.append(user_p)
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "insert" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.after_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.roll contains "'
                        + str(roll)
                        + '" and academic_course_assignation_log.user_name ="'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "insert" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.after_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.roll contains "'
                        + str(roll)
                        + '" and academic_course_assignation_log.user_name ="'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(
                    db.academic_course_assignation_log, search
                ).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "update" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.before_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.after_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.roll contains "'
                        + str(roll)
                        + '" and academic_course_assignation_log.user_name ="'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "update" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.before_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.after_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.roll contains "'
                        + str(roll)
                        + '" and academic_course_assignation_log.user_name ="'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(
                    db.academic_course_assignation_log, search
                ).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "delete" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.before_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.roll contains "'
                        + str(roll)
                        + '" and academic_course_assignation_log.user_name ="'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "delete" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.before_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.roll contains "'
                        + str(roll)
                        + '" and academic_course_assignation_log.user_name ="'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(
                    db.academic_course_assignation_log, search
                ).count()
                infoe_level_temp.append(count_i)
            # INSERT USER
            info_level.append(infoe_level_temp)
    # DATA
    elif str(request.vars["level"]) == "6":
        # DATA
        grid = []
        if str(request.vars["type_L"]) == "i" or str(request.vars["type_L"]) == "all":
            if personal_query == "":
                search = (
                    'academic_course_assignation_log.id_period = "'
                    + str(period.id)
                    + '" and academic_course_assignation_log.operation_log = "insert" and academic_course_assignation_log.date_log >="'
                    + str(month[1])
                    + '" and academic_course_assignation_log.date_log<"'
                    + str(month[2])
                    + '" and academic_course_assignation_log.after_course = "'
                    + str(project)
                    + '" and academic_course_assignation_log.roll LIKE "%'
                    + str(roll)
                    + '%" and academic_course_assignation_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'academic_course_assignation_log.id_period = "'
                    + str(period.id)
                    + '" and academic_course_assignation_log.operation_log = "insert" and academic_course_assignation_log.date_log >="'
                    + str(month[1])
                    + '" and academic_course_assignation_log.date_log<"'
                    + str(month[2])
                    + '" and academic_course_assignation_log.after_course = "'
                    + str(project)
                    + '" and academic_course_assignation_log.roll LIKE "%'
                    + str(roll)
                    + '%" and academic_course_assignation_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
            grid.append(
                db.smart_query(db.academic_course_assignation_log, search).select()
            )
        if str(request.vars["type_L"]) == "u" or str(request.vars["type_L"]) == "all":
            if personal_query == "":
                search = (
                    'academic_course_assignation_log.id_period = "'
                    + str(period.id)
                    + '" and academic_course_assignation_log.operation_log = "update" and academic_course_assignation_log.date_log >="'
                    + str(month[1])
                    + '" and academic_course_assignation_log.date_log<"'
                    + str(month[2])
                    + '" and academic_course_assignation_log.before_course = "'
                    + str(project)
                    + '" and academic_course_assignation_log.after_course = "'
                    + str(project)
                    + '" and academic_course_assignation_log.roll LIKE "%'
                    + str(roll)
                    + '%" and academic_course_assignation_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'academic_course_assignation_log.id_period = "'
                    + str(period.id)
                    + '" and academic_course_assignation_log.operation_log = "update" and academic_course_assignation_log.date_log >="'
                    + str(month[1])
                    + '" and academic_course_assignation_log.date_log<"'
                    + str(month[2])
                    + '" and academic_course_assignation_log.before_course = "'
                    + str(project)
                    + '" and academic_course_assignation_log.after_course = "'
                    + str(project)
                    + '" and academic_course_assignation_log.roll LIKE "%'
                    + str(roll)
                    + '%" and academic_course_assignation_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
            grid.append(
                db.smart_query(db.academic_course_assignation_log, search).select()
            )
        if str(request.vars["type_L"]) == "d" or str(request.vars["type_L"]) == "all":
            if personal_query == "":
                search = (
                    'academic_course_assignation_log.id_period = "'
                    + str(period.id)
                    + '" and academic_course_assignation_log.operation_log = "delete" and academic_course_assignation_log.date_log >="'
                    + str(month[1])
                    + '" and academic_course_assignation_log.date_log<"'
                    + str(month[2])
                    + '" and academic_course_assignation_log.before_course = "'
                    + str(project)
                    + '" and academic_course_assignation_log.roll LIKE "%'
                    + str(roll)
                    + '%" and academic_course_assignation_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'academic_course_assignation_log.id_period = "'
                    + str(period.id)
                    + '" and academic_course_assignation_log.operation_log = "delete" and academic_course_assignation_log.date_log >="'
                    + str(month[1])
                    + '" and academic_course_assignation_log.date_log<"'
                    + str(month[2])
                    + '" and academic_course_assignation_log.before_course = "'
                    + str(project)
                    + '" and academic_course_assignation_log.roll LIKE "%'
                    + str(roll)
                    + '%" and academic_course_assignation_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
            grid.append(
                db.smart_query(db.academic_course_assignation_log, search).select()
            )
        # PERIOD
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MONTH
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        infoe_level_temp.append(str(month[0]))
        info_level.append(infoe_level_temp)
        # PROJECT
        infoe_level_temp = []
        infoe_level_temp.append(T("Project"))
        infoe_level_temp.append(str(project))
        info_level.append(infoe_level_temp)
        # ROL
        infoe_level_temp = []
        infoe_level_temp.append(T("Role"))
        infoe_level_temp.append(T("Rol " + roll))
        info_level.append(infoe_level_temp)
        # USER
        infoe_level_temp = []
        infoe_level_temp.append(T("User"))
        infoe_level_temp.append(str(user_p))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE
        infoe_level_temp = []
        infoe_level_temp.append("")
        info_level.append(infoe_level_temp)
        # DETAIL
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # TITLE OF TABLE
        infoe_level_temp = []
        infoe_level_temp.append("Operación")
        infoe_level_temp.append("Carnet anterior")
        infoe_level_temp.append("Carnet actual")
        infoe_level_temp.append("Laboratorio anterior")
        infoe_level_temp.append("Laboratorio actual")
        infoe_level_temp.append("Descripción")
        infoe_level_temp.append("Fecha")
        info_level.append(infoe_level_temp)
        for data in grid:
            for row in data:
                infoe_level_temp = []
                infoe_level_temp.append(row.operation_log)
                infoe_level_temp.append(row.before_carnet)
                infoe_level_temp.append(row.after_carnet)
                infoe_level_temp.append(row.before_laboratory)
                infoe_level_temp.append(row.after_laboratory)
                infoe_level_temp.append(row.description)
                infoe_level_temp.append(row.date_log)
                info_level.append(infoe_level_temp)
    # *****************************************************REPORT*****************************************************
    # ****************************************************************************************************************
    # ****************************************************************************************************************
    return dict(filename="ReporteGestionAsignaciones", csvdata=info_level)


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def student_assignment_management():
    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # ***************************************CHECK IF THERE IS A PERSONALIZED QUERY***********************************
    personal_query = ""
    make_redirect = False
    if (
        request.vars["querySearch"] is not None
        and str(request.vars["querySearch"]) != ""
    ):
        # PERSONALIZED QUERY SURE WORK
        try:
            personal_query = str(request.vars["querySearch"])
            count_i = db.smart_query(
                db.academic_course_assignation_log, personal_query
            ).count()
            if (
                request.vars["searchT"] is not None
                and str(request.vars["searchT"]) == "T"
            ):
                make_redirect = True
        except:
            response.flash = T(
                "The query is not valid. The report is displayed without applying any query."
            )
            personal_query = ""
    if make_redirect == True:
        redirect(
            URL(
                "management_reports",
                "student_assignment_management",
                vars=dict(
                    level=6,
                    period=request.vars["period"],
                    month=str(request.vars["month"]),
                    project=str(request.vars["project"]),
                    roll=str(request.vars["roll"]),
                    userP=str(request.vars["userP"]),
                    type_L=request.vars["type_L"],
                    type_U=request.vars["type_U"],
                    querySearch=request.vars["querySearch"],
                ),
            )
        )

    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # ******************************************VERIFY THAT ACCURATE PARAMETERS***************************************
    try:
        # CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars["level"] is not None and (
            int(request.vars["level"]) < 1 or int(request.vars["level"]) > 6
        ):
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))

        # VERIFY THAT THE PARAMETERS OF EACH LEVEL BE VALID
        if request.vars["level"] is not None:
            # LEVEL MORE THAN 1
            if int(request.vars["level"]) > 1:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_L"] is None or (
                    str(request.vars["type_L"]) != "all"
                    and str(request.vars["type_L"]) != "i"
                    and str(request.vars["type_L"]) != "u"
                    and str(request.vars["type_L"]) != "d"
                ):
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

                period = validate_period(request.vars["period"])
                if period is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 2
            if int(request.vars["level"]) > 2:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_U"] is None or (
                    str(request.vars["type_U"]) != "all"
                    and str(request.vars["type_U"]) != "i"
                    and str(request.vars["type_U"]) != "u"
                    and str(request.vars["type_U"]) != "d"
                ):
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

                # CHECK IF THE MONTH IS VALID
                month = validate_month(request.vars["month"], period)
                if month is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 3
            if int(request.vars["level"]) > 3:
                # CHECK IF THE PROJECT IS VALID
                project = validate_project(
                    request.vars["project"], "academic_course_assignation_log"
                )
                if project is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))
            # LEVEL MORE THAN 4
            if int(request.vars["level"]) > 4:
                # CHECK IF THE ROLE IS VALID
                roll = validate_role(
                    request.vars["roll"], "academic_course_assignation_log"
                )
                if roll is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 5
            if int(request.vars["level"]) > 5:
                # CHECK IF THE USER IS VALID
                user_p = validate_user(
                    period,
                    project,
                    roll,
                    request.vars["userP"],
                    "academic_course_assignation_log",
                )
                if user_p is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))
    except:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # **************************************************SEARCH REPORT*************************************************
    def filtered_by(flag):
        fsearch_option = []
        fsearch_option.append("=")
        fsearch_option.append("!=")
        fsearch_option.append("<")
        fsearch_option.append(">")
        fsearch_option.append("<=")
        fsearch_option.append(">=")
        if flag == True:
            fsearch_option.append("starts with")
            fsearch_option.append("contains")
            fsearch_option.append("in")
            fsearch_option.append("not in")
        return fsearch_option

    fsearch = []
    # ******************************COMBOS INFORMATION******************************
    # PROJECTS
    if request.vars["level"] is None or int(request.vars["level"]) <= 3:
        # projects = get_projects('academic_course_assignation_log')
        try:
            projects = get_projects("academic_course_assignation_log", period)
        except:
            projects = get_projects("academic_course_assignation_log", None)
        if len(projects) != 0:
            projects = sorted(projects)
            fsearch.append(["before_course", "Curso anterior", False, [3, projects]])
            fsearch.append(["after_course", "Curso actual", False, [3, projects]])
    # ROLES
    if request.vars["level"] is None or int(request.vars["level"]) <= 4:
        roles = get_roles("academic_course_assignation_log")
        if len(roles) != 0:
            fsearch.append(["roll", T("Rol"), False, [4, sorted(roles)]])
    # PERIODS
    if request.vars["level"] == "1" or request.vars["level"] is None:
        group_periods = db(db.period_year).select(orderby=~db.period_year.id)
        if len(group_periods) != 0:
            fsearch.append(["id_period", "Periodo", False, [2, group_periods]])
    # DESCRIPTION
    group_description = get_descriptions("academic_course_assignation_log")
    if len(group_description) != 0:
        fsearch.append(
            ["description", "Descripción", False, [3, sorted(group_description)]]
        )
    # DATE
    group_dates = get_dates("academic_course_assignation_log")
    if len(group_dates) != 0:
        fsearch.append(["date_log", "Fecha", False, [3, sorted(group_dates)]])
    # OPERATION LOG
    fsearch.append(
        ["operation_log", T("Operacion"), False, [3, ["insert", "update", "delete"]]]
    )
    # ******************************ENTERING USER******************************
    if request.vars["level"] is None or int(request.vars["level"]) <= 5:
        # ID OF PERSON WHO REGISTER THE GRADE
        fsearch.append(["user_name", T("Usuario"), True, [1]])
    # BEFORE LABORATORY
    fsearch.append(
        ["before_laboratory", "Laboratorio anterior", False, [3, ["True", "False"]]]
    )
    # AFTER LABORATORY
    fsearch.append(
        ["after_laboratory", "Laboratorio actual", False, [3, ["True", "False"]]]
    )
    # BEFORE CARNET
    fsearch.append(["before_carnet", "Carnet anterior", True, [1]])
    # AFTER CARNET
    fsearch.append(["after_carnet", "Carnet actual", True, [1]])

    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # *****************************************************REPORT*****************************************************
    # LEVELS OF REPORT
    
    info_level = []
    top5 = []
    grid = []
    # ALL SEMESTERS
    if request.vars["level"] == "1" or request.vars["level"] is None:
        if len(group_periods) == 0:
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(URL("default", "home"))

        for period in group_periods:
            infoe_level_temp = []
            # ID OF PERIOD
            infoe_level_temp.append(period.id)
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # INSERT
            if personal_query == "":
                search = (
                    'academic_course_assignation_log.id_period = "'
                    + str(period.id)
                    + '" and academic_course_assignation_log.operation_log = "insert"'
                )
            else:
                search = (
                    'academic_course_assignation_log.id_period = "'
                    + str(period.id)
                    + '" and academic_course_assignation_log.operation_log = "insert" and '
                    + personal_query
                )
            count_i = db.smart_query(db.academic_course_assignation_log, search).count()
            infoe_level_temp.append(count_i)
            # UPDATE
            if personal_query == "":
                search = (
                    'academic_course_assignation_log.id_period = "'
                    + str(period.id)
                    + '" and academic_course_assignation_log.operation_log = "update"'
                )
            else:
                search = (
                    'academic_course_assignation_log.id_period = "'
                    + str(period.id)
                    + '" and academic_course_assignation_log.operation_log = "update" and '
                    + personal_query
                )
            count_i = db.smart_query(db.academic_course_assignation_log, search).count()
            infoe_level_temp.append(count_i)
            # DELETE
            if personal_query == "":
                search = (
                    'academic_course_assignation_log.id_period = "'
                    + str(period.id)
                    + '" and academic_course_assignation_log.operation_log = "delete"'
                )
            else:
                search = (
                    'academic_course_assignation_log.id_period = "'
                    + str(period.id)
                    + '" and academic_course_assignation_log.operation_log = "delete" and '
                    + personal_query
                )
            count_i = db.smart_query(db.academic_course_assignation_log, search).count()
            infoe_level_temp.append(count_i)
            # INSERT PERIOD
            info_level.append(infoe_level_temp)

        # TOP 5 OF PERIOD
        if personal_query == "":
            search = 'academic_course_assignation_log.id != "-1"'
        else:
            search = personal_query
        top5 = db.smart_query(db.academic_course_assignation_log, search).select(
            db.academic_course_assignation_log.id_period,
            db.academic_course_assignation_log.id.count().with_alias('count'),
            orderby=~db.academic_course_assignation_log.id.count(),
            limitby=(0, 5),
            groupby=db.academic_course_assignation_log.id_period,
        )
        top5_t = []
        for top in top5:
            periodTop = (
                db(
                    db.period_year.id
                    == top["academic_course_assignation_log.id_period"]
                )
                .select()
                .first()
            )
            top5_t.append(
                [
                    T(periodTop.period.name) + " " + str(periodTop.yearp),
                    top["count"],
                ]
            )
        top5 = top5_t
    # PER MONTH
    elif str(request.vars["level"]) == "2":
        for month in get_month_period(period):
            start = datetime.strptime(
                str(period.yearp) + "-" + str(month[0]) + "-01", "%Y-%m-%d"
            )
            if month[2] == 1:
                end = datetime.strptime(
                    str(period.yearp + 1) + "-" + str(month[2]) + "-01", "%Y-%m-%d"
                )
            else:
                end = datetime.strptime(
                    str(period.yearp) + "-" + str(month[2]) + "-01", "%Y-%m-%d"
                )
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # ID OF MONTH
            infoe_level_temp.append(month[0])
            # NAME OF MONTH
            infoe_level_temp.append(month[1] + " " + str(period.yearp))
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "insert" and academic_course_assignation_log.date_log >="'
                        + str(start)
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(end)
                        + '"'
                    )
                else:
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "insert" and academic_course_assignation_log.date_log >="'
                        + str(start)
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(end)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(
                    db.academic_course_assignation_log, search
                ).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "update" and academic_course_assignation_log.date_log>="'
                        + str(start)
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(end)
                        + '"'
                    )
                else:
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "update" and academic_course_assignation_log.date_log>="'
                        + str(start)
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(end)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(
                    db.academic_course_assignation_log, search
                ).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "delete" and academic_course_assignation_log.date_log>="'
                        + str(start)
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(end)
                        + '"'
                    )
                else:
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "delete" and academic_course_assignation_log.date_log>="'
                        + str(start)
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(end)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(
                    db.academic_course_assignation_log, search
                ).count()
                infoe_level_temp.append(count_i)
            # INSERT MONTH
            info_level.append(infoe_level_temp)
    # PER PROJECT
    elif str(request.vars["level"]) == "3":
        if len(projects) == 0:
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(
                URL(
                    "management_reports",
                    "student_assignment_management",
                    vars=dict(
                        level="2",
                        period=str(request.vars["period"]),
                        type_L=str(request.vars["type_U"]),
                        querySearch=personal_query,
                    ),
                )
            )

        # TOP 5 OF PROJECT
        top5_tempo = []
        for project_t in projects:
            project = db(db.project.name == project_t).select().first()
            if project is None:
                project = (
                    db(
                        (db.course_activity_log.before_course == project_t)
                        | (db.course_activity_log.after_course == project_t)
                    )
                    .select()
                    .first()
                )
                if project.before_course is not None:
                    project = project.before_course
                else:
                    project = project.after_course
            else:
                project = project.name
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # NAME OF MONTH
            infoe_level_temp.append(month[0])
            # ID OF PROJECT
            infoe_level_temp.append(project)
            # NAME OF PROJECT
            infoe_level_temp.append(project)
            # TOP 5 OF PROJECT
            total_temp = 0
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "insert" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.after_course = "'
                        + str(project)
                        + '"'
                    )
                else:
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "insert" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.after_course = "'
                        + str(project)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(
                    db.academic_course_assignation_log, search
                ).count()
                infoe_level_temp.append(count_i)
                # TOP 5 OF PROJECT
                total_temp = total_temp + count_i
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "update" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.after_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.before_course = "'
                        + str(project)
                        + '"'
                    )
                else:
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "update" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.after_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.before_course = "'
                        + str(project)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(
                    db.academic_course_assignation_log, search
                ).count()
                infoe_level_temp.append(count_i)
                # TOP 5 OF PROJECT
                total_temp = total_temp + count_i
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "delete" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.before_course = "'
                        + str(project)
                        + '"'
                    )
                else:
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "delete" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.before_course = "'
                        + str(project)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(
                    db.academic_course_assignation_log, search
                ).count()
                infoe_level_temp.append(count_i)
                # TOP 5 OF PROJECT
                total_temp = total_temp + count_i
            # INSERT PROJECT
            info_level.append(infoe_level_temp)
            # TOP 5 OF PROJECT
            if total_temp > 0:
                top5_tempo.append([total_temp, project])
        # TOP 5 OF PROJECT
        top5_tempo = sorted(top5_tempo, reverse=True)
        count_top = 0
        for top in top5_tempo:
            if count_top < 5:
                top5.append(top)
            count_top = count_top + 1
    # PER ROL
    elif str(request.vars["level"]) == "4":
        if len(roles) == 0:
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(
                URL(
                    "management_reports",
                    "student_assignment_management",
                    vars=dict(
                        level="3",
                        period=str(request.vars["period"]),
                        month=str(request.vars["month"]),
                        type_L=str(request.vars["type_U"]),
                        type_U=str(request.vars["type_U"]),
                        querySearch=personal_query,
                    ),
                )
            )

        for roll_t in roles:
            roll = db(db.auth_group.role == roll_t).select().first()
            if roll is None:
                roll = (
                    db(db.academic_course_assignation_log.roll.like("%" + roll_t + "%"))
                    .select()
                    .first()
                )
                roll = roll.roll
            else:
                roll = roll.role
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # NAME OF MONTH
            infoe_level_temp.append(month[0])
            # NAME OF PROJECT
            infoe_level_temp.append(project)
            # ID OF ROLE
            infoe_level_temp.append(roll)
            # NAME OF ROLE
            infoe_level_temp.append(T("Rol " + roll))
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "insert" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.after_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.roll contains "'
                        + str(roll)
                        + '"'
                    )
                else:
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "insert" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.after_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.roll contains "'
                        + str(roll)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(
                    db.academic_course_assignation_log, search
                ).count()
                infoe_level_temp.append(count_i)
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "update" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.before_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.after_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.roll contains "'
                        + str(roll)
                        + '"'
                    )
                else:
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "update" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.before_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.after_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.roll contains "'
                        + str(roll)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(
                    db.academic_course_assignation_log, search
                ).count()
                infoe_level_temp.append(count_i)
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "delete" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.before_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.roll contains "'
                        + str(roll)
                        + '"'
                    )
                else:
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "delete" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.before_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.roll contains "'
                        + str(roll)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(
                    db.academic_course_assignation_log, search
                ).count()
                infoe_level_temp.append(count_i)
            # INSERT ROLE
            info_level.append(infoe_level_temp)
    # PER USER
    elif str(request.vars["level"]) == "5":
        # VERIFY THAT CAN SHOW THE LEVEL OF THE REPORT
        users_project = get_users(
            period, project, roll, "academic_course_assignation_log"
        )
        if len(users_project) == 0:
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(
                URL(
                    "management_reports",
                    "student_assignment_management",
                    vars=dict(
                        level="4",
                        period=str(request.vars["period"]),
                        month=str(request.vars["month"]),
                        project=str(request.vars["project"]),
                        type_L=str(request.vars["type_U"]),
                        type_U=str(request.vars["type_U"]),
                        querySearch=personal_query,
                    ),
                )
            )

        # TOP 5 OF PROJECT
        top5_tempo = []
        for user_p_t in users_project:
            user_p = db(db.auth_user.username == user_p_t).select().first()
            if user_p is None:
                user_p = (
                    db(db.academic_course_assignation_log.user_name == user_p_t)
                    .select()
                    .first()
                )
                user_p = user_p.user_name
            else:
                user_p = user_p.username
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # NAME OF MONTH
            infoe_level_temp.append(month[0])
            # NAME OF PROJECT
            infoe_level_temp.append(project)
            # NAME OF ROLE
            infoe_level_temp.append(T("Rol " + roll))
            # ID OF USER
            infoe_level_temp.append(user_p)
            # NAME OF USER
            infoe_level_temp.append(user_p)
            # TOP 5 OF USER
            total_temp = 0
            # INSERT
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "insert" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.after_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.roll contains "'
                        + str(roll)
                        + '" and academic_course_assignation_log.user_name ="'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "insert" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.after_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.roll contains "'
                        + str(roll)
                        + '" and academic_course_assignation_log.user_name ="'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(
                    db.academic_course_assignation_log, search
                ).count()
                infoe_level_temp.append(count_i)
                # TOP 5 OF USER
                total_temp = total_temp + count_i
            # UPDATE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "update" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.before_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.after_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.roll contains "'
                        + str(roll)
                        + '" and academic_course_assignation_log.user_name ="'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "update" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.before_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.after_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.roll contains "'
                        + str(roll)
                        + '" and academic_course_assignation_log.user_name ="'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(
                    db.academic_course_assignation_log, search
                ).count()
                infoe_level_temp.append(count_i)
                # TOP 5 OF USER
                total_temp = total_temp + count_i
            # DELETE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "delete" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.before_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.roll contains "'
                        + str(roll)
                        + '" and academic_course_assignation_log.user_name ="'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'academic_course_assignation_log.id_period = "'
                        + str(period.id)
                        + '" and academic_course_assignation_log.operation_log = "delete" and academic_course_assignation_log.date_log >="'
                        + str(month[1])
                        + '" and academic_course_assignation_log.date_log<"'
                        + str(month[2])
                        + '" and academic_course_assignation_log.before_course = "'
                        + str(project)
                        + '" and academic_course_assignation_log.roll contains "'
                        + str(roll)
                        + '" and academic_course_assignation_log.user_name ="'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(
                    db.academic_course_assignation_log, search
                ).count()
                infoe_level_temp.append(count_i)
                # TOP 5 OF USER
                total_temp = total_temp + count_i
            # INSERT USER
            info_level.append(infoe_level_temp)
            # TOP 5 OF USER
            top5_tempo.append([total_temp, user_p])
        # TOP 5 OF USER
        top5_tempo = sorted(top5_tempo, reverse=True)
        count_top = 0
        for top in top5_tempo:
            if count_top < 5:
                top5.append(top)
            count_top = count_top + 1
    # DATA
    elif str(request.vars["level"]) == "6":
        grid = []
        if str(request.vars["type_L"]) == "i" or str(request.vars["type_L"]) == "all":
            if personal_query == "":
                search = (
                    'academic_course_assignation_log.id_period = "'
                    + str(period.id)
                    + '" and academic_course_assignation_log.operation_log = "insert" and academic_course_assignation_log.date_log >="'
                    + str(month[1])
                    + '" and academic_course_assignation_log.date_log<"'
                    + str(month[2])
                    + '" and academic_course_assignation_log.after_course = "'
                    + str(project)
                    + '" and academic_course_assignation_log.roll LIKE "%'
                    + str(roll)
                    + '%" and academic_course_assignation_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'academic_course_assignation_log.id_period = "'
                    + str(period.id)
                    + '" and academic_course_assignation_log.operation_log = "insert" and academic_course_assignation_log.date_log >="'
                    + str(month[1])
                    + '" and academic_course_assignation_log.date_log<"'
                    + str(month[2])
                    + '" and academic_course_assignation_log.after_course = "'
                    + str(project)
                    + '" and academic_course_assignation_log.roll LIKE "%'
                    + str(roll)
                    + '%" and academic_course_assignation_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
            for data in db.smart_query(
                db.academic_course_assignation_log, search
            ).select():
                grid.append(data.id)
        if str(request.vars["type_L"]) == "u" or str(request.vars["type_L"]) == "all":
            if personal_query == "":
                search = (
                    'academic_course_assignation_log.id_period = "'
                    + str(period.id)
                    + '" and academic_course_assignation_log.operation_log = "update" and academic_course_assignation_log.date_log >="'
                    + str(month[1])
                    + '" and academic_course_assignation_log.date_log<"'
                    + str(month[2])
                    + '" and academic_course_assignation_log.before_course = "'
                    + str(project)
                    + '" and academic_course_assignation_log.after_course = "'
                    + str(project)
                    + '" and academic_course_assignation_log.roll LIKE "%'
                    + str(roll)
                    + '%" and academic_course_assignation_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'academic_course_assignation_log.id_period = "'
                    + str(period.id)
                    + '" and academic_course_assignation_log.operation_log = "update" and academic_course_assignation_log.date_log >="'
                    + str(month[1])
                    + '" and academic_course_assignation_log.date_log<"'
                    + str(month[2])
                    + '" and academic_course_assignation_log.before_course = "'
                    + str(project)
                    + '" and academic_course_assignation_log.after_course = "'
                    + str(project)
                    + '" and academic_course_assignation_log.roll LIKE "%'
                    + str(roll)
                    + '%" and academic_course_assignation_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
            for data in db.smart_query(
                db.academic_course_assignation_log, search
            ).select():
                grid.append(data.id)
        if str(request.vars["type_L"]) == "d" or str(request.vars["type_L"]) == "all":
            if personal_query == "":
                search = (
                    'academic_course_assignation_log.id_period = "'
                    + str(period.id)
                    + '" and academic_course_assignation_log.operation_log = "delete" and academic_course_assignation_log.date_log >="'
                    + str(month[1])
                    + '" and academic_course_assignation_log.date_log<"'
                    + str(month[2])
                    + '" and academic_course_assignation_log.before_course = "'
                    + str(project)
                    + '" and academic_course_assignation_log.roll LIKE "%'
                    + str(roll)
                    + '%" and academic_course_assignation_log.user_name ="'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'academic_course_assignation_log.id_period = "'
                    + str(period.id)
                    + '" and academic_course_assignation_log.operation_log = "delete" and academic_course_assignation_log.date_log >="'
                    + str(month[1])
                    + '" and academic_course_assignation_log.date_log<"'
                    + str(month[2])
                    + '" and academic_course_assignation_log.before_course = "'
                    + str(project)
                    + '" and academic_course_assignation_log.roll LIKE "%'
                    + str(roll)
                    + '%" and academic_course_assignation_log.user_name ="'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
            for data in db.smart_query(
                db.academic_course_assignation_log, search
            ).select():
                grid.append(data.id)
        # TITLE
        infoe_level_temp = []
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        infoe_level_temp.append(str(month[0]))
        infoe_level_temp.append(project)
        infoe_level_temp.append(T("Rol " + roll))
        infoe_level_temp.append(str(user_p))
        info_level.append(infoe_level_temp)
        # REPORT
        if len(grid) == 0:
            grid.append(-1)
        # GRID
        db.academic_course_assignation_log.id.readable = False
        db.academic_course_assignation_log.id.writable = False
        db.academic_course_assignation_log.user_name.readable = False
        db.academic_course_assignation_log.user_name.writable = False
        db.academic_course_assignation_log.roll.readable = False
        db.academic_course_assignation_log.roll.writable = False
        db.academic_course_assignation_log.before_course.readable = False
        db.academic_course_assignation_log.before_course.writable = False
        db.academic_course_assignation_log.after_course.readable = False
        db.academic_course_assignation_log.after_course.writable = False
        db.academic_course_assignation_log.before_year.readable = False
        db.academic_course_assignation_log.before_year.writable = False
        db.academic_course_assignation_log.after_year.readable = False
        db.academic_course_assignation_log.after_year.writable = False
        db.academic_course_assignation_log.before_semester.readable = False
        db.academic_course_assignation_log.before_semester.writable = False
        db.academic_course_assignation_log.after_semester.readable = False
        db.academic_course_assignation_log.after_semester.writable = False
        db.academic_course_assignation_log.id_academic_course_assignation.readable = (
            False
        )
        db.academic_course_assignation_log.id_academic_course_assignation.writable = (
            False
        )
        db.academic_course_assignation_log.id_period.readable = False
        db.academic_course_assignation_log.id_period.writable = False
        grid = SQLFORM.grid(
            db.academic_course_assignation_log.id.belongs(grid),
            csv=False,
            create=False,
            editable=False,
            deletable=False,
            paginate=9,
            searchable=False,
        )
    return dict(
        fsearch=fsearch,
        filtered_by=filtered_by,
        personal_query=personal_query,
        infoLevel=info_level,
        top5=top5,
        grid=grid,
    )


#*************************************************************************************************************************************
#*************************************************************************************************************************************
#********************************************MANAGEMENT REPORT CHANGE REQUEST ACTIVITIES WITH METRIC**********************************


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def change_request_activities_with_metric_management_export():
    # VERIFI THAT ACCURATE PARAMETERS
    try:
        # CHECK IF THE TYPE OF EXPORT IS VALID
        if request.vars["list_type"] is None or str(request.vars["list_type"]) != "csv":
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))

        # CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars["level"] is not None and (
            int(request.vars["level"]) < 1 or int(request.vars["level"]) > 5
        ):
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(URL("default", "home"))

        # VERIFY THAT THE PARAMETERS OF EACH LEVEL BE VALID
        if request.vars["level"] is not None:
            # LEVEL MORE THAN 1
            if int(request.vars["level"]) > 1:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_L"] is None or (
                    str(request.vars["type_L"]) != "all"
                    and str(request.vars["type_L"]) != "i"
                    and str(request.vars["type_L"]) != "u"
                    and str(request.vars["type_L"]) != "d"
                    and str(request.vars["type_L"]) != "p"
                ):
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

                period = validate_period(request.vars["period"])
                if period is None:
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 2
            if int(request.vars["level"]) > 2:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_U"] is None or (
                    str(request.vars["type_U"]) != "all"
                    and str(request.vars["type_U"]) != "i"
                    and str(request.vars["type_U"]) != "u"
                    and str(request.vars["type_U"]) != "d"
                    and str(request.vars["type_L"]) != "p"
                ):
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

                # CHECK IF THE MONTH IS VALID
                month = validate_month(request.vars["month"], period)
                if month is None:
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 3
            if int(request.vars["level"]) > 3:
                # CHECK IF THE PROJECT IS VALID
                project = validate_project(
                    request.vars["project"], "requestchange_activity_log"
                )
                if project is None:
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 4
            if int(request.vars["level"]) > 4:
                # CHECK IF THE USER IS VALID
                user_p = validate_user(
                    period,
                    project,
                    "Student",
                    request.vars["userP"],
                    "academic_course_assignation_log",
                )
                if user_p is None:
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))
    except:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    # CHECK IF THERE IS A PERSONALIZED QUERY
    personal_query = ""
    if (
        request.vars["querySearch"] is not None
        and str(request.vars["querySearch"]) != ""
    ):
        # PERSONALIZED QUERY SURE WORK
        try:
            personal_query = str(request.vars["querySearch"])
            count_i = db.smart_query(
                db.requestchange_activity_log, personal_query
            ).count()
        except:
            personal_query = ""

    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # *****************************************************REPORT*****************************************************
    
    # TITLE
    info_level = []
    infoe_level_temp = []
    infoe_level_temp.append("Universidad de San Carlos de Guatemala")
    info_level.append(infoe_level_temp)
    infoe_level_temp = []
    infoe_level_temp.append("Facultad de Ingeniería")
    info_level.append(infoe_level_temp)
    infoe_level_temp = []
    infoe_level_temp.append("Escuela de Ciencias y Sistemas")
    info_level.append(infoe_level_temp)
    # TYPE OF REPORT
    infoe_level_temp = []
    infoe_level_temp.append(T("Type"))
    infoe_level_temp.append(T("Change Request Management Activity with Metric"))
    info_level.append(infoe_level_temp)
    # DESCRIPTION OF REPORT
    infoe_level_temp = []
    infoe_level_temp.append(T("Description"))
    infoe_level_temp.append(
        T("Report of operations for managing change requests metric activities")
    )
    info_level.append(infoe_level_temp)
    # LEVELS OF REPORT
    # ALL SEMESTERS
    if request.vars["level"] is None or str(request.vars["level"]) == "1":
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T("Total Made Requests"))
        infoe_level_temp.append(T("Total Accepted request"))
        infoe_level_temp.append(T("Total Rejected request"))
        infoe_level_temp.append(T("Total Pending Requests"))
        info_level.append(infoe_level_temp)
        for period in db(db.period_year).select(orderby=~db.period_year.id):
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # MADE
            if personal_query == "":
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.status = "Pending"'
                )
            else:
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.status = "Pending" and '
                    + personal_query
                )
            count_i = db.smart_query(db.requestchange_activity_log, search).count()
            infoe_level_temp.append(count_i)
            # ACCEPTED
            if personal_query == "":
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.status = "Accepted"'
                )
            else:
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.status = "Accepted" and '
                    + personal_query
                )
            count_i = db.smart_query(db.requestchange_activity_log, search).count()
            infoe_level_temp.append(count_i)
            # REJECTED
            if personal_query == "":
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.status = "Rejected"'
                )
            else:
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.status = "Rejected" and '
                    + personal_query
                )
            count_i = db.smart_query(db.requestchange_activity_log, search).count()
            infoe_level_temp.append(count_i)
            # PENDING
            infoe_level_temp.append(
                infoe_level_temp[1] - infoe_level_temp[2] - infoe_level_temp[3]
            )
            # INSERT PERIOD
            info_level.append(infoe_level_temp)
    # PER MONTH
    elif str(request.vars["level"]) == "2":
        # PERIOD OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "d":
            infoe_level_temp.append(T("Total Made Requests"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "i":
            infoe_level_temp.append(T("Total Accepted request"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "u":
            infoe_level_temp.append(T("Total Rejected request"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "p":
            infoe_level_temp.append(T("Total Pending Requests"))
        info_level.append(infoe_level_temp)

        for month in get_month_period(period):
            start = datetime.strptime(
                str(period.yearp) + "-" + str(month[0]) + "-01", "%Y-%m-%d"
            )
            if month[2] == 1:
                end = datetime.strptime(
                    str(period.yearp + 1) + "-" + str(month[2]) + "-01", "%Y-%m-%d"
                )
            else:
                end = datetime.strptime(
                    str(period.yearp) + "-" + str(month[2]) + "-01", "%Y-%m-%d"
                )
            infoe_level_temp = []
            # NAME OF MONTH
            infoe_level_temp.append(month[1] + " " + str(period.yearp))
            # MADE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(start)
                        + '" and requestchange_activity_log.date_request<"'
                        + str(end)
                        + '" and requestchange_activity_log.status = "Pending"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(start)
                        + '" and requestchange_activity_log.date_request<"'
                        + str(end)
                        + '" and requestchange_activity_log.status = "Pending" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.requestchange_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # ACCEPTED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request_resolve >="'
                        + str(start)
                        + '" and requestchange_activity_log.date_request_resolve<"'
                        + str(end)
                        + '" and requestchange_activity_log.status = "Accepted"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request_resolve >="'
                        + str(start)
                        + '" and requestchange_activity_log.date_request_resolve<"'
                        + str(end)
                        + '" and requestchange_activity_log.status = "Accepted" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.requestchange_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # REJECTED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request_resolve >="'
                        + str(start)
                        + '" and requestchange_activity_log.date_request_resolve<"'
                        + str(end)
                        + '" and requestchange_activity_log.status = "Rejected"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request_resolve >="'
                        + str(start)
                        + '" and requestchange_activity_log.date_request_resolve<"'
                        + str(end)
                        + '" and requestchange_activity_log.status = "Rejected" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.requestchange_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # PENDING
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "p"
            ):
                if period.period == 1:
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request<"'
                            + str(end)
                            + '" and requestchange_activity_log.status = "Pending"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request<"'
                            + str(end)
                            + '" and requestchange_activity_log.status = "Pending" and '
                            + personal_query
                        )
                    count_p = db.smart_query(
                        db.requestchange_activity_log, search
                    ).count()
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(end)
                            + '" and requestchange_activity_log.status != "Pending"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(end)
                            + '" and requestchange_activity_log.status != "Pending" and '
                            + personal_query
                        )
                    count_n_p = db.smart_query(
                        db.requestchange_activity_log, search
                    ).count()
                else:
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request<"'
                            + str(end)
                            + '" and requestchange_activity_log.status = "Pending"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request<"'
                            + str(end)
                            + '" and requestchange_activity_log.status = "Pending" and '
                            + personal_query
                        )
                    count_p = db.smart_query(
                        db.requestchange_activity_log, search
                    ).count()
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(end)
                            + '" and requestchange_activity_log.status != "Pending"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(end)
                            + '" and requestchange_activity_log.status != "Pending" and '
                            + personal_query
                        )
                    count_n_p = db.smart_query(
                        db.requestchange_activity_log, search
                    ).count()
                infoe_level_temp.append(count_p - count_n_p)
            # INSERT MONTH
            info_level.append(infoe_level_temp)
    # PER PROJECT
    elif str(request.vars["level"]) == "3":
        # PROJECTS
        # projects = get_projects('requestchange_activity_log')
        try:
            projects = get_projects("requestchange_activity_log", period)
        except:
            projects = get_projects("requestchange_activity_log", None)
        projects = sorted(projects)
        # PERIOD OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MONTH OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        infoe_level_temp.append(str(month[0]))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Project"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "d":
            infoe_level_temp.append(T("Total Made Requests"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "i":
            infoe_level_temp.append(T("Total Accepted request"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "u":
            infoe_level_temp.append(T("Total Rejected request"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "p":
            infoe_level_temp.append(T("Total Pending Requests"))
        info_level.append(infoe_level_temp)

        for project_t in projects:
            project = db(db.project.name == project_t).select().first()
            if project is None:
                project = (
                    db(
                        (db.course_activity_log.before_course == project_t)
                        | (db.course_activity_log.after_course == project_t)
                    )
                    .select()
                    .first()
                )
                if project.before_course is not None:
                    project = project.before_course
                else:
                    project = project.after_course
            else:
                project = project.name
            infoe_level_temp = []
            # NAME OF PROJECT
            infoe_level_temp.append(project)
            # MADE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(month[1])
                        + '" and requestchange_activity_log.date_request<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                        + str(project)
                        + '"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(month[1])
                        + '" and requestchange_activity_log.date_request<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.requestchange_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # ACCEPTED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request_resolve >="'
                        + str(month[1])
                        + '" and requestchange_activity_log.date_request_resolve<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Accepted" and requestchange_activity_log.course = "'
                        + str(project)
                        + '"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request_resolve >="'
                        + str(month[1])
                        + '" and requestchange_activity_log.date_request_resolve<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Accepted" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.requestchange_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # REJECTED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request_resolve >="'
                        + str(month[1])
                        + '" and requestchange_activity_log.date_request_resolve<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Rejected" and requestchange_activity_log.course = "'
                        + str(project)
                        + '"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request_resolve >="'
                        + str(month[1])
                        + '" and requestchange_activity_log.date_request_resolve<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Rejected" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.requestchange_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # PENDING
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "p"
            ):
                if period.period == 1:
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and '
                            + personal_query
                        )
                    count_p = db.smart_query(
                        db.requestchange_activity_log, search
                    ).count()
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and '
                            + personal_query
                        )
                    count_n_p = db.smart_query(
                        db.requestchange_activity_log, search
                    ).count()
                else:
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and '
                            + personal_query
                        )
                    count_p = db.smart_query(
                        db.requestchange_activity_log, search
                    ).count()
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and '
                            + personal_query
                        )
                    count_n_p = db.smart_query(
                        db.requestchange_activity_log, search
                    ).count()
                infoe_level_temp.append(count_p - count_n_p)
            # INSERT PROJECT
            info_level.append(infoe_level_temp)
    # PER USER
    elif str(request.vars["level"]) == "4":
        # USERS
        users_project = get_users(
            period, project, "Student", "requestchange_activity_log"
        )
        # PERIOD OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MONTH OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        infoe_level_temp.append(str(month[0]))
        info_level.append(infoe_level_temp)
        # PROJECT OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Project"))
        infoe_level_temp.append(str(project))
        info_level.append(infoe_level_temp)
        # ROL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Role"))
        infoe_level_temp.append(T("Rol Student"))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("User"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "d":
            infoe_level_temp.append(T("Total Made Requests"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "i":
            infoe_level_temp.append(T("Total Accepted request"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "u":
            infoe_level_temp.append(T("Total Rejected request"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "p":
            infoe_level_temp.append(T("Total Pending Requests"))
        info_level.append(infoe_level_temp)

        for user_p_t in users_project:
            user_p = db(db.auth_user.username == user_p_t).select().first()
            if user_p is None:
                user_p = (
                    db(db.requestchange_activity_log.user_request == user_p_t)
                    .select()
                    .first()
                )
                user_p = user_p.user_request
            else:
                user_p = user_p.username
            infoe_level_temp = []
            # NAME OF USER
            infoe_level_temp.append(user_p)
            # MADE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                count_i = 0
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(month[1])
                        + '" and requestchange_activity_log.date_request<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(month[1])
                        + '" and requestchange_activity_log.date_request<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.requestchange_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # ACCEPTED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request_resolve >="'
                        + str(month[1])
                        + '" and requestchange_activity_log.date_request_resolve<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Accepted" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request_resolve >="'
                        + str(month[1])
                        + '" and requestchange_activity_log.date_request_resolve<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Accepted" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.requestchange_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # REJECTED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request_resolve >="'
                        + str(month[1])
                        + '" and requestchange_activity_log.date_request_resolve<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Rejected" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request_resolve >="'
                        + str(month[1])
                        + '" and requestchange_activity_log.date_request_resolve<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Rejected" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.requestchange_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # PENDING
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "p"
            ):
                if period.period == 1:
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '" and '
                            + personal_query
                        )
                    count_p = db.smart_query(
                        db.requestchange_activity_log, search
                    ).count()
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '" and '
                            + personal_query
                        )
                    count_n_p = db.smart_query(
                        db.requestchange_activity_log, search
                    ).count()
                else:
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '" and '
                            + personal_query
                        )
                    count_p = db.smart_query(
                        db.requestchange_activity_log, search
                    ).count()
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '" and '
                            + personal_query
                        )
                    count_n_p = db.smart_query(
                        db.requestchange_activity_log, search
                    ).count()
                infoe_level_temp.append(count_p - count_n_p)
            # INSERT USER
            info_level.append(infoe_level_temp)
    # DATA
    elif str(request.vars["level"]) == "5":
        # PERIOD
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MONTH
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        infoe_level_temp.append(str(month[0]))
        info_level.append(infoe_level_temp)
        # PROJECT
        infoe_level_temp = []
        infoe_level_temp.append(T("Project"))
        infoe_level_temp.append(str(project))
        info_level.append(infoe_level_temp)
        # ROL
        infoe_level_temp = []
        infoe_level_temp.append(T("Role"))
        infoe_level_temp.append(T("Rol Student"))
        info_level.append(infoe_level_temp)
        # USER
        infoe_level_temp = []
        infoe_level_temp.append(T("User"))
        infoe_level_temp.append(str(user_p))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE
        infoe_level_temp = []
        infoe_level_temp.append("")
        info_level.append(infoe_level_temp)
        # DETAIL
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # TITLE OF TABLE
        infoe_level_temp = []
        infoe_level_temp.append("Estado")
        infoe_level_temp.append("Usuario Resolvio")
        infoe_level_temp.append("Rol Resolvio")
        infoe_level_temp.append("Descripción")
        infoe_level_temp.append("Fecha")
        infoe_level_temp.append("Fecha Resolvio")
        infoe_level_temp.append("Categoria")
        info_level.append(infoe_level_temp)

        # MADE
        if str(request.vars["type_L"]) == "d":
            if personal_query == "":
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.date_request >="'
                    + str(month[1])
                    + '" and requestchange_activity_log.date_request<"'
                    + str(month[2])
                    + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                    + str(project)
                    + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.date_request >="'
                    + str(month[1])
                    + '" and requestchange_activity_log.date_request<"'
                    + str(month[2])
                    + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                    + str(project)
                    + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
            for data in db.smart_query(db.requestchange_activity_log, search).select():
                infoe_level_temp = []
                infoe_level_temp.append(data.status)
                infoe_level_temp.append(data.user_resolve)
                infoe_level_temp.append(data.roll_resolve)
                infoe_level_temp.append(data.description)
                infoe_level_temp.append(data.date_request)
                infoe_level_temp.append(data.date_request_resolve)
                infoe_level_temp.append(data.category_request)
                info_level.append(infoe_level_temp)
                infoe_level_temp = []
                infoe_level_temp.append("")
                infoe_level_temp.append("")
                infoe_level_temp.append(T("Operation"))
                infoe_level_temp.append(T("Name Activity"))
                infoe_level_temp.append(T("Description of Activity"))
                infoe_level_temp.append(T("Grade of Activity"))
                infoe_level_temp.append(T("Start Date"))
                infoe_level_temp.append(T("End Date"))
                info_level.append(infoe_level_temp)
                for details in db(
                    db.requestchange_course_activity_log.requestchange_activity
                    == data.id
                ).select():
                    infoe_level_temp = []
                    infoe_level_temp.append("")
                    infoe_level_temp.append("")
                    infoe_level_temp.append(details.operation_request)
                    infoe_level_temp.append(details.name)
                    infoe_level_temp.append(details.description)
                    infoe_level_temp.append(details.grade)
                    infoe_level_temp.append(details.date_start)
                    infoe_level_temp.append(details.date_finish)
                    info_level.append(infoe_level_temp)
                infoe_level_temp = []
                infoe_level_temp.append("")
                info_level.append(infoe_level_temp)
        # ACCEPTED
        elif str(request.vars["type_L"]) == "i":
            if personal_query == "":
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.date_request_resolve >="'
                    + str(month[1])
                    + '" and requestchange_activity_log.date_request_resolve<"'
                    + str(month[2])
                    + '" and requestchange_activity_log.status = "Accepted" and requestchange_activity_log.course = "'
                    + str(project)
                    + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.date_request_resolve >="'
                    + str(month[1])
                    + '" and requestchange_activity_log.date_request_resolve<"'
                    + str(month[2])
                    + '" and requestchange_activity_log.status = "Accepted" and requestchange_activity_log.course = "'
                    + str(project)
                    + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
            for data in db.smart_query(db.requestchange_activity_log, search).select():
                infoe_level_temp = []
                infoe_level_temp.append(data.status)
                infoe_level_temp.append(data.user_resolve)
                infoe_level_temp.append(data.roll_resolve)
                infoe_level_temp.append(data.description)
                infoe_level_temp.append(data.date_request)
                infoe_level_temp.append(data.date_request_resolve)
                infoe_level_temp.append(data.category_request)
                info_level.append(infoe_level_temp)
                infoe_level_temp = []
                infoe_level_temp.append("")
                infoe_level_temp.append("")
                infoe_level_temp.append(T("Operation"))
                infoe_level_temp.append(T("Name Activity"))
                infoe_level_temp.append(T("Description of Activity"))
                infoe_level_temp.append(T("Grade of Activity"))
                infoe_level_temp.append(T("Start Date"))
                infoe_level_temp.append(T("End Date"))
                info_level.append(infoe_level_temp)
                for details in db(
                    db.requestchange_course_activity_log.requestchange_activity
                    == data.id
                ).select():
                    infoe_level_temp = []
                    infoe_level_temp.append("")
                    infoe_level_temp.append("")
                    infoe_level_temp.append(details.operation_request)
                    infoe_level_temp.append(details.name)
                    infoe_level_temp.append(details.description)
                    infoe_level_temp.append(details.grade)
                    infoe_level_temp.append(details.date_start)
                    infoe_level_temp.append(details.date_finish)
                    info_level.append(infoe_level_temp)
                infoe_level_temp = []
                infoe_level_temp.append("")
                info_level.append(infoe_level_temp)
        # REJECTED
        elif str(request.vars["type_L"]) == "u":
            if personal_query == "":
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.date_request_resolve >="'
                    + str(month[1])
                    + '" and requestchange_activity_log.date_request_resolve<"'
                    + str(month[2])
                    + '" and requestchange_activity_log.status = "Rejected" and requestchange_activity_log.course = "'
                    + str(project)
                    + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.date_request_resolve >="'
                    + str(month[1])
                    + '" and requestchange_activity_log.date_request_resolve<"'
                    + str(month[2])
                    + '" and requestchange_activity_log.status = "Rejected" and requestchange_activity_log.course = "'
                    + str(project)
                    + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
            for data in db.smart_query(db.requestchange_activity_log, search).select():
                infoe_level_temp = []
                infoe_level_temp.append(data.status)
                infoe_level_temp.append(data.user_resolve)
                infoe_level_temp.append(data.roll_resolve)
                infoe_level_temp.append(data.description)
                infoe_level_temp.append(data.date_request)
                infoe_level_temp.append(data.date_request_resolve)
                infoe_level_temp.append(data.category_request)
                info_level.append(infoe_level_temp)
                infoe_level_temp = []
                infoe_level_temp.append("")
                infoe_level_temp.append("")
                infoe_level_temp.append(T("Operation"))
                infoe_level_temp.append(T("Name Activity"))
                infoe_level_temp.append(T("Description of Activity"))
                infoe_level_temp.append(T("Grade of Activity"))
                infoe_level_temp.append(T("Start Date"))
                infoe_level_temp.append(T("End Date"))
                info_level.append(infoe_level_temp)
                for details in db(
                    db.requestchange_course_activity_log.requestchange_activity
                    == data.id
                ).select():
                    infoe_level_temp = []
                    infoe_level_temp.append("")
                    infoe_level_temp.append("")
                    infoe_level_temp.append(details.operation_request)
                    infoe_level_temp.append(details.name)
                    infoe_level_temp.append(details.description)
                    infoe_level_temp.append(details.grade)
                    infoe_level_temp.append(details.date_start)
                    infoe_level_temp.append(details.date_finish)
                    info_level.append(infoe_level_temp)
                infoe_level_temp = []
                infoe_level_temp.append("")
                info_level.append(infoe_level_temp)
        # PENDING
        elif str(request.vars["type_L"]) == "p":
            if period.period == 1:
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(period.yearp)
                        + '-01-01" and requestchange_activity_log.date_request<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(period.yearp)
                        + '-01-01" and requestchange_activity_log.date_request<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                for pending in db.smart_query(
                    db.requestchange_activity_log, search
                ).select():
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '" and requestchange_activity_log.description = "'
                            + pending.description
                            + '" and requestchange_activity_log.date_request = "'
                            + str(pending.date_request)
                            + '" and requestchange_activity_log.category_request = "'
                            + pending.category_request
                            + '"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '" and requestchange_activity_log.description = "'
                            + pending.description
                            + '" and requestchange_activity_log.date_request = "'
                            + str(pending.date_request)
                            + '" and requestchange_activity_log.category_request = "'
                            + pending.category_request
                            + '" and '
                            + personal_query
                        )
                    if (
                        db.smart_query(db.requestchange_activity_log, search)
                        .select()
                        .first()
                        is None
                    ):
                        infoe_level_temp = []
                        infoe_level_temp.append(pending.status)
                        infoe_level_temp.append(pending.user_resolve)
                        infoe_level_temp.append(pending.roll_resolve)
                        infoe_level_temp.append(pending.description)
                        infoe_level_temp.append(pending.date_request)
                        infoe_level_temp.append(pending.date_request_resolve)
                        infoe_level_temp.append(pending.category_request)
                        info_level.append(infoe_level_temp)
                        infoe_level_temp = []
                        infoe_level_temp.append("")
                        infoe_level_temp.append("")
                        infoe_level_temp.append(T("Operation"))
                        infoe_level_temp.append(T("Name Activity"))
                        infoe_level_temp.append(T("Description of Activity"))
                        infoe_level_temp.append(T("Grade of Activity"))
                        infoe_level_temp.append(T("Start Date"))
                        infoe_level_temp.append(T("End Date"))
                        info_level.append(infoe_level_temp)
                        for details in db(
                            db.requestchange_course_activity_log.requestchange_activity
                            == pending.id
                        ).select():
                            infoe_level_temp = []
                            infoe_level_temp.append("")
                            infoe_level_temp.append("")
                            infoe_level_temp.append(details.operation_request)
                            infoe_level_temp.append(details.name)
                            infoe_level_temp.append(details.description)
                            infoe_level_temp.append(details.grade)
                            infoe_level_temp.append(details.date_start)
                            infoe_level_temp.append(details.date_finish)
                            info_level.append(infoe_level_temp)
                        infoe_level_temp = []
                        infoe_level_temp.append("")
                        info_level.append(infoe_level_temp)
            else:
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(period.yearp)
                        + '-06-01" and requestchange_activity_log.date_request<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(period.yearp)
                        + '-06-01" and requestchange_activity_log.date_request<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                for pending in db.smart_query(
                    db.requestchange_activity_log, search
                ).select():
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '" and requestchange_activity_log.description = "'
                            + pending.description
                            + '" and requestchange_activity_log.date_request = "'
                            + str(pending.date_request)
                            + '" and requestchange_activity_log.category_request = "'
                            + pending.category_request
                            + '"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '" and requestchange_activity_log.description = "'
                            + pending.description
                            + '" and requestchange_activity_log.date_request = "'
                            + str(pending.date_request)
                            + '" and requestchange_activity_log.category_request = "'
                            + pending.category_request
                            + '" and '
                            + personal_query
                        )
                    if (
                        db.smart_query(db.requestchange_activity_log, search)
                        .select()
                        .first()
                        is None
                    ):
                        infoe_level_temp = []
                        infoe_level_temp.append(pending.status)
                        infoe_level_temp.append(pending.user_resolve)
                        infoe_level_temp.append(pending.roll_resolve)
                        infoe_level_temp.append(pending.description)
                        infoe_level_temp.append(pending.date_request)
                        infoe_level_temp.append(pending.date_request_resolve)
                        infoe_level_temp.append(pending.category_request)
                        info_level.append(infoe_level_temp)
                        infoe_level_temp = []
                        infoe_level_temp.append("")
                        infoe_level_temp.append("")
                        infoe_level_temp.append(T("Operation"))
                        infoe_level_temp.append(T("Name Activity"))
                        infoe_level_temp.append(T("Description of Activity"))
                        infoe_level_temp.append(T("Grade of Activity"))
                        infoe_level_temp.append(T("Start Date"))
                        infoe_level_temp.append(T("End Date"))
                        info_level.append(infoe_level_temp)
                        for details in db(
                            db.requestchange_course_activity_log.requestchange_activity
                            == pending.id
                        ).select():
                            infoe_level_temp = []
                            infoe_level_temp.append("")
                            infoe_level_temp.append("")
                            infoe_level_temp.append(details.operation_request)
                            infoe_level_temp.append(details.name)
                            infoe_level_temp.append(details.description)
                            infoe_level_temp.append(details.grade)
                            infoe_level_temp.append(details.date_start)
                            infoe_level_temp.append(details.date_finish)
                            info_level.append(infoe_level_temp)
                        infoe_level_temp = []
                        infoe_level_temp.append("")
                        info_level.append(infoe_level_temp)
        # ALL
        elif str(request.vars["type_L"]) == "all":
            # MADE AND PENDING
            if period.period == 1:
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(period.yearp)
                        + '-01-01" and requestchange_activity_log.date_request<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(period.yearp)
                        + '-01-01" and requestchange_activity_log.date_request<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                for pending in db.smart_query(
                    db.requestchange_activity_log, search
                ).select():
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '" and requestchange_activity_log.description = "'
                            + pending.description
                            + '" and requestchange_activity_log.date_request = "'
                            + str(pending.date_request)
                            + '" and requestchange_activity_log.category_request = "'
                            + pending.category_request
                            + '"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '" and requestchange_activity_log.description = "'
                            + pending.description
                            + '" and requestchange_activity_log.date_request = "'
                            + str(pending.date_request)
                            + '" and requestchange_activity_log.category_request = "'
                            + pending.category_request
                            + '" and '
                            + personal_query
                        )
                    if (
                        db.smart_query(db.requestchange_activity_log, search)
                        .select()
                        .first()
                        is None
                    ):
                        infoe_level_temp = []
                        infoe_level_temp.append(pending.status)
                        infoe_level_temp.append(pending.user_resolve)
                        infoe_level_temp.append(pending.roll_resolve)
                        infoe_level_temp.append(pending.description)
                        infoe_level_temp.append(pending.date_request)
                        infoe_level_temp.append(pending.date_request_resolve)
                        infoe_level_temp.append(pending.category_request)
                        info_level.append(infoe_level_temp)
                        infoe_level_temp = []
                        infoe_level_temp.append("")
                        infoe_level_temp.append("")
                        infoe_level_temp.append(T("Operation"))
                        infoe_level_temp.append(T("Name Activity"))
                        infoe_level_temp.append(T("Description of Activity"))
                        infoe_level_temp.append(T("Grade of Activity"))
                        infoe_level_temp.append(T("Start Date"))
                        infoe_level_temp.append(T("End Date"))
                        info_level.append(infoe_level_temp)
                        for details in db(
                            db.requestchange_course_activity_log.requestchange_activity
                            == pending.id
                        ).select():
                            infoe_level_temp = []
                            infoe_level_temp.append("")
                            infoe_level_temp.append("")
                            infoe_level_temp.append(details.operation_request)
                            infoe_level_temp.append(details.name)
                            infoe_level_temp.append(details.description)
                            infoe_level_temp.append(details.grade)
                            infoe_level_temp.append(details.date_start)
                            infoe_level_temp.append(details.date_finish)
                            info_level.append(infoe_level_temp)
                        infoe_level_temp = []
                        infoe_level_temp.append("")
                        info_level.append(infoe_level_temp)
            else:
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(period.yearp)
                        + '-06-01" and requestchange_activity_log.date_request<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(period.yearp)
                        + '-06-01" and requestchange_activity_log.date_request<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                for pending in db.smart_query(
                    db.requestchange_activity_log, search
                ).select():
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '" and requestchange_activity_log.description = "'
                            + pending.description
                            + '" and requestchange_activity_log.date_request = "'
                            + str(pending.date_request)
                            + '" and requestchange_activity_log.category_request = "'
                            + pending.category_request
                            + '"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '" and requestchange_activity_log.description = "'
                            + pending.description
                            + '" and requestchange_activity_log.date_request = "'
                            + str(pending.date_request)
                            + '" and requestchange_activity_log.category_request = "'
                            + pending.category_request
                            + '" and '
                            + personal_query
                        )
                    if (
                        db.smart_query(db.requestchange_activity_log, search)
                        .select()
                        .first()
                        is None
                    ):
                        infoe_level_temp = []
                        infoe_level_temp.append(pending.status)
                        infoe_level_temp.append(pending.user_resolve)
                        infoe_level_temp.append(pending.roll_resolve)
                        infoe_level_temp.append(pending.description)
                        infoe_level_temp.append(pending.date_request)
                        infoe_level_temp.append(pending.date_request_resolve)
                        infoe_level_temp.append(pending.category_request)
                        info_level.append(infoe_level_temp)
                        infoe_level_temp = []
                        infoe_level_temp.append("")
                        infoe_level_temp.append("")
                        infoe_level_temp.append(T("Operation"))
                        infoe_level_temp.append(T("Name Activity"))
                        infoe_level_temp.append(T("Description of Activity"))
                        infoe_level_temp.append(T("Grade of Activity"))
                        infoe_level_temp.append(T("Start Date"))
                        infoe_level_temp.append(T("End Date"))
                        info_level.append(infoe_level_temp)
                        for details in db(
                            db.requestchange_course_activity_log.requestchange_activity
                            == pending.id
                        ).select():
                            infoe_level_temp = []
                            infoe_level_temp.append("")
                            infoe_level_temp.append("")
                            infoe_level_temp.append(details.operation_request)
                            infoe_level_temp.append(details.name)
                            infoe_level_temp.append(details.description)
                            infoe_level_temp.append(details.grade)
                            infoe_level_temp.append(details.date_start)
                            infoe_level_temp.append(details.date_finish)
                            info_level.append(infoe_level_temp)
                        infoe_level_temp = []
                        infoe_level_temp.append("")
                        info_level.append(infoe_level_temp)
            # ACCEPTED
            if personal_query == "":
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.date_request_resolve >="'
                    + str(month[1])
                    + '" and requestchange_activity_log.date_request_resolve<"'
                    + str(month[2])
                    + '" and requestchange_activity_log.status = "Accepted" and requestchange_activity_log.course = "'
                    + str(project)
                    + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.date_request_resolve >="'
                    + str(month[1])
                    + '" and requestchange_activity_log.date_request_resolve<"'
                    + str(month[2])
                    + '" and requestchange_activity_log.status = "Accepted" and requestchange_activity_log.course = "'
                    + str(project)
                    + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
            for data in db.smart_query(db.requestchange_activity_log, search).select():
                infoe_level_temp = []
                infoe_level_temp.append(data.status)
                infoe_level_temp.append(data.user_resolve)
                infoe_level_temp.append(data.roll_resolve)
                infoe_level_temp.append(data.description)
                infoe_level_temp.append(data.date_request)
                infoe_level_temp.append(data.date_request_resolve)
                infoe_level_temp.append(data.category_request)
                info_level.append(infoe_level_temp)
                infoe_level_temp = []
                infoe_level_temp.append("")
                infoe_level_temp.append("")
                infoe_level_temp.append(T("Operation"))
                infoe_level_temp.append(T("Name Activity"))
                infoe_level_temp.append(T("Description of Activity"))
                infoe_level_temp.append(T("Grade of Activity"))
                infoe_level_temp.append(T("Start Date"))
                infoe_level_temp.append(T("End Date"))
                info_level.append(infoe_level_temp)
                for details in db(
                    db.requestchange_course_activity_log.requestchange_activity
                    == data.id
                ).select():
                    infoe_level_temp = []
                    infoe_level_temp.append("")
                    infoe_level_temp.append("")
                    infoe_level_temp.append(details.operation_request)
                    infoe_level_temp.append(details.name)
                    infoe_level_temp.append(details.description)
                    infoe_level_temp.append(details.grade)
                    infoe_level_temp.append(details.date_start)
                    infoe_level_temp.append(details.date_finish)
                    info_level.append(infoe_level_temp)
                infoe_level_temp = []
                infoe_level_temp.append("")
                info_level.append(infoe_level_temp)
            # REJECTED
            if personal_query == "":
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.date_request_resolve >="'
                    + str(month[1])
                    + '" and requestchange_activity_log.date_request_resolve<"'
                    + str(month[2])
                    + '" and requestchange_activity_log.status = "Rejected" and requestchange_activity_log.course = "'
                    + str(project)
                    + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.date_request_resolve >="'
                    + str(month[1])
                    + '" and requestchange_activity_log.date_request_resolve<"'
                    + str(month[2])
                    + '" and requestchange_activity_log.status = "Rejected" and requestchange_activity_log.course = "'
                    + str(project)
                    + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
            for data in db.smart_query(db.requestchange_activity_log, search).select():
                infoe_level_temp = []
                infoe_level_temp.append(data.status)
                infoe_level_temp.append(data.user_resolve)
                infoe_level_temp.append(data.roll_resolve)
                infoe_level_temp.append(data.description)
                infoe_level_temp.append(data.date_request)
                infoe_level_temp.append(data.date_request_resolve)
                infoe_level_temp.append(data.category_request)
                info_level.append(infoe_level_temp)
                infoe_level_temp = []
                infoe_level_temp.append("")
                infoe_level_temp.append("")
                infoe_level_temp.append(T("Operation"))
                infoe_level_temp.append(T("Name Activity"))
                infoe_level_temp.append(T("Description of Activity"))
                infoe_level_temp.append(T("Grade of Activity"))
                infoe_level_temp.append(T("Start Date"))
                infoe_level_temp.append(T("End Date"))
                info_level.append(infoe_level_temp)
                for details in db(
                    db.requestchange_course_activity_log.requestchange_activity
                    == data.id
                ).select():
                    infoe_level_temp = []
                    infoe_level_temp.append("")
                    infoe_level_temp.append("")
                    infoe_level_temp.append(details.operation_request)
                    infoe_level_temp.append(details.name)
                    infoe_level_temp.append(details.description)
                    infoe_level_temp.append(details.grade)
                    infoe_level_temp.append(details.date_start)
                    infoe_level_temp.append(details.date_finish)
                    info_level.append(infoe_level_temp)
                infoe_level_temp = []
                infoe_level_temp.append("")
                info_level.append(infoe_level_temp)
    # *****************************************************REPORT*****************************************************
    # ****************************************************************************************************************
    # ****************************************************************************************************************
    return dict(
        filename="ReporteGestionSolicitudesCambioActividadesConMetrica",
        csvdata=info_level,
    )


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def crawm_load():
    request_c = None
    request_d = None
    show_level = False
    try:
        request_c = (
            db(db.requestchange_activity_log.id == int(request.vars["id"]))
            .select()
            .first()
        )
        if request_c is not None:
            show_level = True
            request_d = db(
                db.requestchange_course_activity_log.requestchange_activity
                == int(request.vars["id"])
            ).select()
    except:
        show_level = False
    return dict(showLevel=show_level, requestC=request_c, requestD=request_d)


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def change_request_activities_with_metric_management():
    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # ***************************************CHECK IF THERE IS A PERSONALIZED QUERY***********************************
    personal_query = ""
    make_redirect = False
    if (
        request.vars["querySearch"] is not None
        and str(request.vars["querySearch"]) != ""
    ):
        # PERSONALIZED QUERY SURE WORK
        try:
            personal_query = str(request.vars["querySearch"])
            count_i = db.smart_query(
                db.requestchange_activity_log, personal_query
            ).count()
            if (
                request.vars["searchT"] is not None
                and str(request.vars["searchT"]) == "T"
            ):
                make_redirect = True
        except:
            response.flash = T(
                "The query is not valid. The report is displayed without applying any query."
            )
            personal_query = ""
    if make_redirect == True:
        redirect(
            URL(
                "management_reports",
                "change_request_activities_with_metric_management",
                vars=dict(
                    level="5",
                    period=request.vars["period"],
                    month=str(request.vars["month"]),
                    project=str(request.vars["project"]),
                    userP=str(request.vars["userP"]),
                    type_L=request.vars["type_L"],
                    type_U=request.vars["type_U"],
                    querySearch=request.vars["querySearch"],
                ),
            )
        )

    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # ******************************************VERIFY THAT ACCURATE PARAMETERS***************************************
    try:
        # CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars["level"] is not None and (
            int(request.vars["level"]) < 1 or int(request.vars["level"]) > 5
        ):
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))

        # VERIFY THAT THE PARAMETERS OF EACH LEVEL BE VALID
        if request.vars["level"] is not None:
            # LEVEL MORE THAN 1
            if int(request.vars["level"]) > 1:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_L"] is None or (
                    str(request.vars["type_L"]) != "all"
                    and str(request.vars["type_L"]) != "i"
                    and str(request.vars["type_L"]) != "u"
                    and str(request.vars["type_L"]) != "d"
                    and str(request.vars["type_L"]) != "p"
                ):
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

                period = validate_period(request.vars["period"])
                if period is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 2
            if int(request.vars["level"]) > 2:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_U"] is None or (
                    str(request.vars["type_U"]) != "all"
                    and str(request.vars["type_U"]) != "i"
                    and str(request.vars["type_U"]) != "u"
                    and str(request.vars["type_U"]) != "d"
                    and str(request.vars["type_L"]) != "p"
                ):
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

                # CHECK IF THE MONTH IS VALID
                month = validate_month(request.vars["month"], period)
                if month is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 3
            if int(request.vars["level"]) > 3:
                # CHECK IF THE PROJECT IS VALID
                project = validate_project(
                    request.vars["project"], "requestchange_activity_log"
                )
                if project is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 4
            if int(request.vars["level"]) > 4:
                # CHECK IF THE USER IS VALID
                user_p = validate_user(
                    period,
                    project,
                    "Student",
                    request.vars["userP"],
                    "requestchange_activity_log",
                )
                if user_p is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))
    except:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # **************************************************SEARCH REPORT*************************************************
    def filtered_by(flag):
        fsearch_option = []
        fsearch_option.append("=")
        fsearch_option.append("!=")
        fsearch_option.append("<")
        fsearch_option.append(">")
        fsearch_option.append("<=")
        fsearch_option.append(">=")
        if flag == True:
            fsearch_option.append("starts with")
            fsearch_option.append("contains")
            fsearch_option.append("in")
            fsearch_option.append("not in")
        return fsearch_option

    fsearch = []
    # ******************************COMBOS INFORMATION******************************
    # YEARS
    if request.vars["level"] == "1" or request.vars["level"] is None:
        group_years = get_years()
        if len(group_years) != 0:
            fsearch.append(["yearp", "Año", False, [3, sorted(group_years)]])
    # PROJECTS
    if request.vars["level"] is None or int(request.vars["level"]) <= 3:
        # projects = get_projects('requestchange_activity_log')
        try:
            projects = get_projects("requestchange_activity_log", period)
        except:
            projects = get_projects("requestchange_activity_log", None)
        if len(projects) != 0:
            fsearch_values = []
            fsearch_values.append(2)
            for project_t in projects:
                project = db(db.project.name == project_t).select().first()
                if project is None:
                    project = (
                        db(db.requestchange_activity_log.course == project_t)
                        .select()
                        .first()
                    )
                    project = project.course
                else:
                    project = project.name
                fsearch_values.append(project)
            fsearch.append(["course", "Curso", False, fsearch_values])
    # OPERATION LOG
    fsearch.append(
        ["status", "Estado", False, [3, ["Accepted", "Rejected", "Pending"]]]
    )
    # CATEGORIES
    group_categories = get_categories("requestchange_activity_log")
    if len(group_categories) != 0:
        fsearch.append(
            ["category_request", "Categoria", False, [3, sorted(group_categories)]]
        )
    # DATES
    dates = get_dates("requestchange_activity_log")
    if len(dates) != 0:
        fsearch.append(["date_request", "Fecha", False, [3, sorted(dates)]])
    # ******************************ENTERING USER******************************
    # USER REQUEST
    if request.vars["level"] is None or int(request.vars["level"]) <= 4:
        fsearch.append(["user_request", "Usuario Solicitud", False, [1]])
    fsearch.append(["description", "Descripción", True, [1]])

    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # *****************************************************REPORT*****************************************************
    # LEVELS OF REPORT
    
    info_level = []
    grid = []
    # ALL SEMESTERS
    if request.vars["level"] == "1" or request.vars["level"] is None:
        group_periods = db(db.period_year).select(orderby=~db.period_year.id)
        if len(group_periods) == 0:
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(URL("default", "home"))
        for period in group_periods:
            infoe_level_temp = []
            # ID OF PERIOD
            infoe_level_temp.append(period.id)
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # MADE
            if personal_query == "":
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.status = "Pending"'
                )
            else:
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.status = "Pending" and '
                    + personal_query
                )
            count_i = db.smart_query(db.requestchange_activity_log, search).count()
            infoe_level_temp.append(count_i)
            # ACCEPTED
            if personal_query == "":
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.status = "Accepted"'
                )
            else:
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.status = "Accepted" and '
                    + personal_query
                )
            count_i = db.smart_query(db.requestchange_activity_log, search).count()
            infoe_level_temp.append(count_i)
            # REJECTED
            if personal_query == "":
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.status = "Rejected"'
                )
            else:
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.status = "Rejected" and '
                    + personal_query
                )
            count_i = db.smart_query(db.requestchange_activity_log, search).count()
            infoe_level_temp.append(count_i)
            # PENDING
            infoe_level_temp.append(
                infoe_level_temp[2] - infoe_level_temp[3] - infoe_level_temp[4]
            )
            # INSERT PERIOD
            info_level.append(infoe_level_temp)
    # PER MONTH
    elif str(request.vars["level"]) == "2":
        for month in get_month_period(period):
            start = datetime.strptime(
                str(period.yearp) + "-" + str(month[0]) + "-01", "%Y-%m-%d"
            )
            if month[2] == 1:
                end = datetime.strptime(
                    str(period.yearp + 1) + "-" + str(month[2]) + "-01", "%Y-%m-%d"
                )
            else:
                end = datetime.strptime(
                    str(period.yearp) + "-" + str(month[2]) + "-01", "%Y-%m-%d"
                )
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # ID OF MONTH
            infoe_level_temp.append(month[0])
            # NAME OF MONTH
            infoe_level_temp.append(month[1] + " " + str(period.yearp))
            # MADE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(start)
                        + '" and requestchange_activity_log.date_request<"'
                        + str(end)
                        + '" and requestchange_activity_log.status = "Pending"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(start)
                        + '" and requestchange_activity_log.date_request<"'
                        + str(end)
                        + '" and requestchange_activity_log.status = "Pending" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.requestchange_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # ACCEPTED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request_resolve >="'
                        + str(start)
                        + '" and requestchange_activity_log.date_request_resolve<"'
                        + str(end)
                        + '" and requestchange_activity_log.status = "Accepted"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request_resolve >="'
                        + str(start)
                        + '" and requestchange_activity_log.date_request_resolve<"'
                        + str(end)
                        + '" and requestchange_activity_log.status = "Accepted" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.requestchange_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # REJECTED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request_resolve >="'
                        + str(start)
                        + '" and requestchange_activity_log.date_request_resolve<"'
                        + str(end)
                        + '" and requestchange_activity_log.status = "Rejected"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request_resolve >="'
                        + str(start)
                        + '" and requestchange_activity_log.date_request_resolve<"'
                        + str(end)
                        + '" and requestchange_activity_log.status = "Rejected" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.requestchange_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # PENDING
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "p"
            ):
                if period.period == 1:
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request<"'
                            + str(end)
                            + '" and requestchange_activity_log.status = "Pending"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request<"'
                            + str(end)
                            + '" and requestchange_activity_log.status = "Pending" and '
                            + personal_query
                        )
                    count_p = db.smart_query(
                        db.requestchange_activity_log, search
                    ).count()
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(end)
                            + '" and requestchange_activity_log.status != "Pending"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(end)
                            + '" and requestchange_activity_log.status != "Pending" and '
                            + personal_query
                        )
                    count_n_p = db.smart_query(
                        db.requestchange_activity_log, search
                    ).count()
                else:
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request<"'
                            + str(end)
                            + '" and requestchange_activity_log.status = "Pending"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request<"'
                            + str(end)
                            + '" and requestchange_activity_log.status = "Pending" and '
                            + personal_query
                        )
                    count_p = db.smart_query(
                        db.requestchange_activity_log, search
                    ).count()
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(end)
                            + '" and requestchange_activity_log.status != "Pending"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(end)
                            + '" and requestchange_activity_log.status != "Pending" and '
                            + personal_query
                        )
                    count_n_p = db.smart_query(
                        db.requestchange_activity_log, search
                    ).count()
                infoe_level_temp.append(count_p - count_n_p)
            # INSERT MONTH
            info_level.append(infoe_level_temp)
    # PER PROJECT
    elif str(request.vars["level"]) == "3":
        if len(projects) == 0:
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(
                URL(
                    "management_reports",
                    "change_request_activities_with_metric_management",
                    vars=dict(
                        level="2",
                        period=str(request.vars["period"]),
                        type_L=str(request.vars["type_U"]),
                        querySearch=personal_query,
                    ),
                )
            )

        for project_t in projects:
            project = db(db.project.name == project_t).select().first()
            if project is None:
                project = (
                    db(
                        (db.course_activity_log.before_course == project_t)
                        | (db.course_activity_log.after_course == project_t)
                    )
                    .select()
                    .first()
                )
                if project.before_course is not None:
                    project = project.before_course
                else:
                    project = project.after_course
            else:
                project = project.name
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # NAME OF MONTH
            infoe_level_temp.append(month[0])
            # ID OF PROJECT
            infoe_level_temp.append(project)
            # NAME OF PROJECT
            infoe_level_temp.append(project)
            # MADE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(month[1])
                        + '" and requestchange_activity_log.date_request<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                        + str(project)
                        + '"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(month[1])
                        + '" and requestchange_activity_log.date_request<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.requestchange_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # ACCEPTED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request_resolve >="'
                        + str(month[1])
                        + '" and requestchange_activity_log.date_request_resolve<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Accepted" and requestchange_activity_log.course = "'
                        + str(project)
                        + '"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request_resolve >="'
                        + str(month[1])
                        + '" and requestchange_activity_log.date_request_resolve<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Accepted" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.requestchange_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # REJECTED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request_resolve >="'
                        + str(month[1])
                        + '" and requestchange_activity_log.date_request_resolve<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Rejected" and requestchange_activity_log.course = "'
                        + str(project)
                        + '"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request_resolve >="'
                        + str(month[1])
                        + '" and requestchange_activity_log.date_request_resolve<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Rejected" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.requestchange_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # PENDING
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "p"
            ):
                if period.period == 1:
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and '
                            + personal_query
                        )
                    count_p = db.smart_query(
                        db.requestchange_activity_log, search
                    ).count()
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and '
                            + personal_query
                        )
                    count_n_p = db.smart_query(
                        db.requestchange_activity_log, search
                    ).count()
                else:
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and '
                            + personal_query
                        )
                    count_p = db.smart_query(
                        db.requestchange_activity_log, search
                    ).count()
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and '
                            + personal_query
                        )
                    count_n_p = db.smart_query(
                        db.requestchange_activity_log, search
                    ).count()
                infoe_level_temp.append(count_p - count_n_p)
            # INSERT PROJECT
            info_level.append(infoe_level_temp)
    # PER USER
    elif str(request.vars["level"]) == "4":
        # VERIFY THAT CAN SHOW THE LEVEL OF THE REPORT
        users_project = get_users(
            period, project, "Student", "requestchange_activity_log"
        )
        if len(users_project) == 0:
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(
                URL(
                    "management_reports",
                    "change_request_activities_with_metric_management",
                    vars=dict(
                        level="3",
                        period=str(request.vars["period"]),
                        month=str(request.vars["month"]),
                        type_L=str(request.vars["type_U"]),
                        type_U=str(request.vars["type_U"]),
                        querySearch=personal_query,
                    ),
                )
            )

        for user_p_t in users_project:
            user_p = db(db.auth_user.username == user_p_t).select().first()
            if user_p is None:
                user_p = (
                    db(db.requestchange_activity_log.user_request == user_p_t)
                    .select()
                    .first()
                )
                user_p = user_p.user_request
            else:
                user_p = user_p.username
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # NAME OF MONTH
            infoe_level_temp.append(month[0])
            # NAME OF PROJECT
            infoe_level_temp.append(project)
            # ID OF USER
            infoe_level_temp.append(user_p)
            # NAME OF USER
            infoe_level_temp.append(user_p)
            # MADE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                count_i = 0
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(month[1])
                        + '" and requestchange_activity_log.date_request<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(month[1])
                        + '" and requestchange_activity_log.date_request<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.requestchange_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # ACCEPTED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request_resolve >="'
                        + str(month[1])
                        + '" and requestchange_activity_log.date_request_resolve<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Accepted" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request_resolve >="'
                        + str(month[1])
                        + '" and requestchange_activity_log.date_request_resolve<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Accepted" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.requestchange_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # REJECTED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request_resolve >="'
                        + str(month[1])
                        + '" and requestchange_activity_log.date_request_resolve<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Rejected" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request_resolve >="'
                        + str(month[1])
                        + '" and requestchange_activity_log.date_request_resolve<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Rejected" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.requestchange_activity_log, search).count()
                infoe_level_temp.append(count_i)
            # PENDING
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "p"
            ):
                if period.period == 1:
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '" and '
                            + personal_query
                        )
                    count_p = db.smart_query(
                        db.requestchange_activity_log, search
                    ).count()
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '" and '
                            + personal_query
                        )
                    count_n_p = db.smart_query(
                        db.requestchange_activity_log, search
                    ).count()
                else:
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '" and '
                            + personal_query
                        )
                    count_p = db.smart_query(
                        db.requestchange_activity_log, search
                    ).count()
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '" and '
                            + personal_query
                        )
                    count_n_p = db.smart_query(
                        db.requestchange_activity_log, search
                    ).count()
                infoe_level_temp.append(count_p - count_n_p)
            # INSERT USER
            info_level.append(infoe_level_temp)
    # DATA
    elif str(request.vars["level"]) == "5":
        # MADE
        if str(request.vars["type_L"]) == "d":
            if personal_query == "":
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.date_request >="'
                    + str(month[1])
                    + '" and requestchange_activity_log.date_request<"'
                    + str(month[2])
                    + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                    + str(project)
                    + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.date_request >="'
                    + str(month[1])
                    + '" and requestchange_activity_log.date_request<"'
                    + str(month[2])
                    + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                    + str(project)
                    + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
            for data in db.smart_query(db.requestchange_activity_log, search).select():
                grid.append(data.id)
        # ACCEPTED
        elif str(request.vars["type_L"]) == "i":
            if personal_query == "":
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.date_request_resolve >="'
                    + str(month[1])
                    + '" and requestchange_activity_log.date_request_resolve<"'
                    + str(month[2])
                    + '" and requestchange_activity_log.status = "Accepted" and requestchange_activity_log.course = "'
                    + str(project)
                    + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.date_request_resolve >="'
                    + str(month[1])
                    + '" and requestchange_activity_log.date_request_resolve<"'
                    + str(month[2])
                    + '" and requestchange_activity_log.status = "Accepted" and requestchange_activity_log.course = "'
                    + str(project)
                    + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
            for data in db.smart_query(db.requestchange_activity_log, search).select():
                grid.append(data.id)
        # REJECTED
        elif str(request.vars["type_L"]) == "u":
            if personal_query == "":
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.date_request_resolve >="'
                    + str(month[1])
                    + '" and requestchange_activity_log.date_request_resolve<"'
                    + str(month[2])
                    + '" and requestchange_activity_log.status = "Rejected" and requestchange_activity_log.course = "'
                    + str(project)
                    + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.date_request_resolve >="'
                    + str(month[1])
                    + '" and requestchange_activity_log.date_request_resolve<"'
                    + str(month[2])
                    + '" and requestchange_activity_log.status = "Rejected" and requestchange_activity_log.course = "'
                    + str(project)
                    + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
            for data in db.smart_query(db.requestchange_activity_log, search).select():
                grid.append(data.id)
        # PENDING
        elif str(request.vars["type_L"]) == "p":
            if period.period == 1:
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(period.yearp)
                        + '-01-01" and requestchange_activity_log.date_request<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(period.yearp)
                        + '-01-01" and requestchange_activity_log.date_request<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                for pending in db.smart_query(
                    db.requestchange_activity_log, search
                ).select():
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '" and requestchange_activity_log.description = "'
                            + pending.description
                            + '" and requestchange_activity_log.date_request = "'
                            + str(pending.date_request)
                            + '" and requestchange_activity_log.category_request = "'
                            + pending.category_request
                            + '"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '" and requestchange_activity_log.description = "'
                            + pending.description
                            + '" and requestchange_activity_log.date_request = "'
                            + str(pending.date_request)
                            + '" and requestchange_activity_log.category_request = "'
                            + pending.category_request
                            + '" and '
                            + personal_query
                        )
                    if (
                        db.smart_query(db.requestchange_activity_log, search)
                        .select()
                        .first()
                        is None
                    ):
                        grid.append(pending.id)
            else:
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(period.yearp)
                        + '-06-01" and requestchange_activity_log.date_request<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(period.yearp)
                        + '-06-01" and requestchange_activity_log.date_request<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                for pending in db.smart_query(
                    db.requestchange_activity_log, search
                ).select():
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '" and requestchange_activity_log.description = "'
                            + pending.description
                            + '" and requestchange_activity_log.date_request = "'
                            + str(pending.date_request)
                            + '" and requestchange_activity_log.category_request = "'
                            + pending.category_request
                            + '"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '" and requestchange_activity_log.description = "'
                            + pending.description
                            + '" and requestchange_activity_log.date_request = "'
                            + str(pending.date_request)
                            + '" and requestchange_activity_log.category_request = "'
                            + pending.category_request
                            + '" and '
                            + personal_query
                        )
                    if (
                        db.smart_query(db.requestchange_activity_log, search)
                        .select()
                        .first()
                        is None
                    ):
                        grid.append(pending.id)
        # ALL
        elif str(request.vars["type_L"]) == "all":
            # MADE AND PENDING
            if period.period == 1:
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(period.yearp)
                        + '-01-01" and requestchange_activity_log.date_request<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(period.yearp)
                        + '-01-01" and requestchange_activity_log.date_request<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                for pending in db.smart_query(
                    db.requestchange_activity_log, search
                ).select():
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '" and requestchange_activity_log.description = "'
                            + pending.description
                            + '" and requestchange_activity_log.date_request = "'
                            + str(pending.date_request)
                            + '" and requestchange_activity_log.category_request = "'
                            + pending.category_request
                            + '"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-01-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '" and requestchange_activity_log.description = "'
                            + pending.description
                            + '" and requestchange_activity_log.date_request = "'
                            + str(pending.date_request)
                            + '" and requestchange_activity_log.category_request = "'
                            + pending.category_request
                            + '" and '
                            + personal_query
                        )
                    if (
                        db.smart_query(db.requestchange_activity_log, search)
                        .select()
                        .first()
                        is None
                    ):
                        grid.append(pending.id)
            else:
                if personal_query == "":
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(period.yearp)
                        + '-06-01" and requestchange_activity_log.date_request<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '"'
                    )
                else:
                    search = (
                        'requestchange_activity_log.semester = "'
                        + period.period.name
                        + '" and requestchange_activity_log.yearp = "'
                        + str(period.yearp)
                        + '" and requestchange_activity_log.date_request >="'
                        + str(period.yearp)
                        + '-06-01" and requestchange_activity_log.date_request<"'
                        + str(month[2])
                        + '" and requestchange_activity_log.status = "Pending" and requestchange_activity_log.course = "'
                        + str(project)
                        + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                        + str(user_p)
                        + '" and '
                        + personal_query
                    )
                for pending in db.smart_query(
                    db.requestchange_activity_log, search
                ).select():
                    if personal_query == "":
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '" and requestchange_activity_log.description = "'
                            + pending.description
                            + '" and requestchange_activity_log.date_request = "'
                            + str(pending.date_request)
                            + '" and requestchange_activity_log.category_request = "'
                            + pending.category_request
                            + '"'
                        )
                    else:
                        search = (
                            'requestchange_activity_log.semester = "'
                            + period.period.name
                            + '" and requestchange_activity_log.yearp = "'
                            + str(period.yearp)
                            + '" and requestchange_activity_log.date_request_resolve >="'
                            + str(period.yearp)
                            + '-06-01" and requestchange_activity_log.date_request_resolve<"'
                            + str(month[2])
                            + '" and requestchange_activity_log.status != "Pending" and requestchange_activity_log.course = "'
                            + str(project)
                            + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                            + str(user_p)
                            + '" and requestchange_activity_log.description = "'
                            + pending.description
                            + '" and requestchange_activity_log.date_request = "'
                            + str(pending.date_request)
                            + '" and requestchange_activity_log.category_request = "'
                            + pending.category_request
                            + '" and '
                            + personal_query
                        )
                    if (
                        db.smart_query(db.requestchange_activity_log, search)
                        .select()
                        .first()
                        is None
                    ):
                        grid.append(pending.id)
            # ACCEPTED
            if personal_query == "":
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.date_request_resolve >="'
                    + str(month[1])
                    + '" and requestchange_activity_log.date_request_resolve<"'
                    + str(month[2])
                    + '" and requestchange_activity_log.status = "Accepted" and requestchange_activity_log.course = "'
                    + str(project)
                    + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.date_request_resolve >="'
                    + str(month[1])
                    + '" and requestchange_activity_log.date_request_resolve<"'
                    + str(month[2])
                    + '" and requestchange_activity_log.status = "Accepted" and requestchange_activity_log.course = "'
                    + str(project)
                    + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
            for data in db.smart_query(db.requestchange_activity_log, search).select():
                grid.append(data.id)
            # REJECTED
            if personal_query == "":
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.date_request_resolve >="'
                    + str(month[1])
                    + '" and requestchange_activity_log.date_request_resolve<"'
                    + str(month[2])
                    + '" and requestchange_activity_log.status = "Rejected" and requestchange_activity_log.course = "'
                    + str(project)
                    + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                    + str(user_p)
                    + '"'
                )
            else:
                search = (
                    'requestchange_activity_log.semester = "'
                    + period.period.name
                    + '" and requestchange_activity_log.yearp = "'
                    + str(period.yearp)
                    + '" and requestchange_activity_log.date_request_resolve >="'
                    + str(month[1])
                    + '" and requestchange_activity_log.date_request_resolve<"'
                    + str(month[2])
                    + '" and requestchange_activity_log.status = "Rejected" and requestchange_activity_log.course = "'
                    + str(project)
                    + '" and requestchange_activity_log.roll_request = "Student" and requestchange_activity_log.user_request = "'
                    + str(user_p)
                    + '" and '
                    + personal_query
                )
            for data in db.smart_query(db.requestchange_activity_log, search).select():
                grid.append(data.id)

        # TITLE
        infoe_level_temp = []
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        infoe_level_temp.append(str(month[0]))
        infoe_level_temp.append(project)
        infoe_level_temp.append(T("Rol Student"))
        infoe_level_temp.append(str(user_p))
        info_level.append(infoe_level_temp)
        # REPORT
        if len(grid) == 0:
            grid.append(-1)
        db.requestchange_activity_log.id.readable = False
        db.requestchange_activity_log.id.writable = False
        db.requestchange_activity_log.user_request.readable = False
        db.requestchange_activity_log.user_request.writable = False
        db.requestchange_activity_log.roll_request.readable = False
        db.requestchange_activity_log.roll_request.writable = False
        db.requestchange_activity_log.semester.readable = False
        db.requestchange_activity_log.semester.writable = False
        db.requestchange_activity_log.yearp.readable = False
        db.requestchange_activity_log.yearp.writable = False
        db.requestchange_activity_log.course.readable = False
        db.requestchange_activity_log.course.writable = False
        links = [
            lambda row: A(
                T("Detail"),
                _role="button",
                _class="btn btn-info",
                _onclick='set_values("' + str(row.id) + '");',
                _title=T("View Detail"),
                **{"_data-toggle": "modal", "_data-target": "#detailModal"},
            )
        ]
        grid = SQLFORM.grid(
            db.requestchange_activity_log.id.belongs(grid),
            links=links,
            csv=False,
            create=False,
            editable=False,
            deletable=False,
            details=False,
            paginate=9,
            searchable=False,
        )
    return dict(
        fsearch=fsearch,
        filtered_by=filtered_by,
        personal_query=personal_query,
        infoLevel=info_level,
        grid=grid,
    )


#*************************************************************************************************************************************
#*************************************************************************************************************************************
#**************************************************MANAGEMENT REPORT CHANGE REQUEST GRADES********************************************


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator")
    or auth.has_membership("Ecys-Administrator")
)
def change_request_grades_management_export():
    # VERIFI THAT ACCURATE PARAMETERS
    try:
        # CHECK IF THE TYPE OF EXPORT IS VALID
        if request.vars["list_type"] is None or str(request.vars["list_type"]) != "csv":
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))

        # CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars["level"] is not None and (
            int(request.vars["level"]) < 1 or int(request.vars["level"]) > 5
        ):
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(URL("default", "home"))

        # VERIFY THAT THE PARAMETERS OF EACH LEVEL BE VALID
        if request.vars["level"] is not None:
            # LEVEL MORE THAN 1
            if int(request.vars["level"]) > 1:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_L"] is None or (
                    str(request.vars["type_L"]) != "all"
                    and str(request.vars["type_L"]) != "i"
                    and str(request.vars["type_L"]) != "u"
                    and str(request.vars["type_L"]) != "d"
                    and str(request.vars["type_L"]) != "p"
                    and str(request.vars["type_L"]) != "c"
                ):
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

                period = validate_period(request.vars["period"])
                if period is None:
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 2
            if int(request.vars["level"]) > 2:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_U"] is None or (
                    str(request.vars["type_U"]) != "all"
                    and str(request.vars["type_U"]) != "i"
                    and str(request.vars["type_U"]) != "u"
                    and str(request.vars["type_U"]) != "d"
                    and str(request.vars["type_L"]) != "p"
                    and str(request.vars["type_L"]) != "c"
                ):
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

                # CHECK IF THE MONTH IS VALID
                month = validate_month(request.vars["month"], period)
                if month is None:
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 3
            if int(request.vars["level"]) > 3:
                # CHECK IF THE PROJECT IS VALID
                project = validate_project(
                    request.vars["project"], "request_change_g_log"
                )
                if project is None:
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 4
            if int(request.vars["level"]) > 4:
                # CHECK IF THE USER IS VALID
                user_p = validate_user(
                    period,
                    project,
                    "Student",
                    request.vars["userP"],
                    "request_change_g_log",
                )
                if user_p is None:
                    session.flash = T(
                        "Report no visible: There are no parameters required to display the report."
                    )
                    redirect(URL("default", "home"))
    except:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    # CHECK IF THERE IS A PERSONALIZED QUERY
    personal_query = ""
    if (
        request.vars["querySearch"] is not None
        and str(request.vars["querySearch"]) != ""
    ):
        # PERSONALIZED QUERY SURE WORK
        try:
            personal_query = str(request.vars["querySearch"])
            count_i = db.smart_query(db.request_change_g_log, personal_query).count()
        except:
            personal_query = ""

    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # *****************************************************REPORT*****************************************************
    
    # TITLE
    info_level = []
    infoe_level_temp = []
    infoe_level_temp.append("Universidad de San Carlos de Guatemala")
    info_level.append(infoe_level_temp)
    infoe_level_temp = []
    infoe_level_temp.append("Facultad de Ingeniería")
    info_level.append(infoe_level_temp)
    infoe_level_temp = []
    infoe_level_temp.append("Escuela de Ciencias y Sistemas")
    info_level.append(infoe_level_temp)
    # TYPE OF REPORT
    infoe_level_temp = []
    infoe_level_temp.append(T("Type"))
    infoe_level_temp.append(T("Change Request Management Grades"))
    info_level.append(infoe_level_temp)
    # DESCRIPTION OF REPORT
    infoe_level_temp = []
    infoe_level_temp.append(T("Description"))
    infoe_level_temp.append(T("Report of operations for managing change requests grades"))
    info_level.append(infoe_level_temp)
    # LEVELS OF REPORT
    # ALL SEMESTERS
    if request.vars["level"] is None or str(request.vars["level"]) == "1":
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T("Total Made Requests"))
        infoe_level_temp.append(T("Total Accepted request"))
        infoe_level_temp.append(T("Total Rejected request"))
        infoe_level_temp.append(T("Total Canceled request"))
        infoe_level_temp.append(T("Total Pending Requests"))
        info_level.append(infoe_level_temp)
        for period in groupPeriods:
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # MADE
            if personal_query == "":
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.after_status = "pending"'
                )
            else:
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.after_status = "pending" and '
                    + personal_query
                )
            count_i = db.smart_query(db.request_change_g_log, search).count()
            infoe_level_temp.append(count_i)
            # ACCEPTED
            if personal_query == "":
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.after_status = "accepted"'
                )
            else:
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.after_status = "accepted" and '
                    + personal_query
                )
            count_i = db.smart_query(db.request_change_g_log, search).count()
            infoe_level_temp.append(count_i)
            # REJECTED
            if personal_query == "":
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.after_status = "rejected"'
                )
            else:
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.after_status = "rejected" and '
                    + personal_query
                )
            count_i = db.smart_query(db.request_change_g_log, search).count()
            infoe_level_temp.append(count_i)
            # CANCELED
            if personal_query == "":
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.after_status = "canceled"'
                )
            else:
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.after_status = "canceled" and '
                    + personal_query
                )
            count_i = db.smart_query(db.request_change_g_log, search).count()
            infoe_level_temp.append(count_i)
            # PENDING
            infoe_level_temp.append(
                infoe_level_temp[2]
                - infoe_level_temp[3]
                - infoe_level_temp[4]
                - infoe_level_temp[5]
            )
            # INSERT PERIOD
            info_level.append(infoe_level_temp)
    # PER MONTH
    elif str(request.vars["level"]) == "2":
        # PERIOD OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "d":
            infoe_level_temp.append(T("Total Made Requests"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "i":
            infoe_level_temp.append(T("Total Accepted request"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "u":
            infoe_level_temp.append(T("Total Rejected request"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "c":
            infoe_level_temp.append(T("Total Canceled request"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "p":
            infoe_level_temp.append(T("Total Pending Requests"))
        info_level.append(infoe_level_temp)

        for month in get_month_period(period):
            start = datetime.strptime(
                str(period.yearp) + "-" + str(month[0]) + "-01", "%Y-%m-%d"
            )
            if month[2] == 1:
                end = datetime.strptime(
                    str(period.yearp + 1) + "-" + str(month[2]) + "-01", "%Y-%m-%d"
                )
            else:
                end = datetime.strptime(
                    str(period.yearp) + "-" + str(month[2]) + "-01", "%Y-%m-%d"
                )
            infoe_level_temp = []
            # NAME OF MONTH
            infoe_level_temp.append(month[1] + " " + str(period.yearp))
            # MADE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(start)
                        + '" and request_change_g_log.date_request<"'
                        + str(end)
                        + '" and request_change_g_log.after_status = "pending"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(start)
                        + '" and request_change_g_log.date_request<"'
                        + str(end)
                        + '" and request_change_g_log.after_status = "pending" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_i)
            # ACCEPTED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(start)
                        + '" and request_change_g_log.date_operation<"'
                        + str(end)
                        + '" and request_change_g_log.after_status = "accepted"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(start)
                        + '" and request_change_g_log.date_operation<"'
                        + str(end)
                        + '" and request_change_g_log.after_status = "accepted" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_i)
            # REJECTED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(start)
                        + '" and request_change_g_log.date_operation<"'
                        + str(end)
                        + '" and request_change_g_log.after_status = "rejected"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(start)
                        + '" and request_change_g_log.date_operation<"'
                        + str(end)
                        + '" and request_change_g_log.after_status = "rejected" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_i)
            ##CANCELED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "c"
            ):
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(start)
                        + '" and request_change_g_log.date_operation<"'
                        + str(end)
                        + '" and request_change_g_log.after_status = "canceled"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(start)
                        + '" and request_change_g_log.date_operation<"'
                        + str(end)
                        + '" and request_change_g_log.after_status = "canceled" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_i)
            # PENDING
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "p"
            ):
                if period.period == 1:
                    if personal_query == "":
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_request >="'
                            + str(period.yearp)
                            + '-01-01" and request_change_g_log.date_request<"'
                            + str(end)
                            + '" and request_change_g_log.after_status = "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_request >="'
                            + str(period.yearp)
                            + '-01-01" and request_change_g_log.date_request<"'
                            + str(end)
                            + '" and request_change_g_log.after_status = "pending" and '
                            + personal_query
                        )
                    count_p = db.smart_query(db.request_change_g_log, search).count()
                    if personal_query == "":
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_operation >="'
                            + str(period.yearp)
                            + '-01-01" and request_change_g_log.date_operation<"'
                            + str(end)
                            + '" and request_change_g_log.after_status != "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_operation >="'
                            + str(period.yearp)
                            + '-01-01" and request_change_g_log.date_operation<"'
                            + str(end)
                            + '" and request_change_g_log.after_status != "pending" and '
                            + personal_query
                        )
                    count_n_p = db.smart_query(db.request_change_g_log, search).count()
                else:
                    if personal_query == "":
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_request >="'
                            + str(period.yearp)
                            + '-06-01" and request_change_g_log.date_request<"'
                            + str(end)
                            + '" and request_change_g_log.after_status = "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_request >="'
                            + str(period.yearp)
                            + '-06-01" and request_change_g_log.date_request<"'
                            + str(end)
                            + '" and request_change_g_log.after_status = "pending" and '
                            + personal_query
                        )
                    count_p = db.smart_query(db.request_change_g_log, search).count()
                    if personal_query == "":
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_operation >="'
                            + str(period.yearp)
                            + '-06-01" and request_change_g_log.date_operation<"'
                            + str(end)
                            + '" and request_change_g_log.after_status != "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_operation >="'
                            + str(period.yearp)
                            + '-06-01" and request_change_g_log.date_operation<"'
                            + str(end)
                            + '" and request_change_g_log.after_status != "pending" and '
                            + personal_query
                        )
                    count_n_p = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_p - count_n_p)
            # INSERT MONTH
            info_level.append(infoe_level_temp)
    # PER PROJECT
    elif str(request.vars["level"]) == "3":
        # PROJECTS
        # projects = get_projects('request_change_g_log')
        try:
            projects = get_projects("request_change_g_log", period)
        except:
            projects = get_projects("request_change_g_log", None)
        projects = sorted(projects)
        # PERIOD OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MONTH OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        infoe_level_temp.append(str(month[0]))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Project"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "d":
            infoe_level_temp.append(T("Total Made Requests"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "i":
            infoe_level_temp.append(T("Total Accepted request"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "u":
            infoe_level_temp.append(T("Total Rejected request"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "c":
            infoe_level_temp.append(T("Total Canceled request"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "p":
            infoe_level_temp.append(T("Total Pending Requests"))
        info_level.append(infoe_level_temp)

        for project_t in projects:
            project = db(db.project.name == project_t).select().first()
            if project is None:
                project = (
                    db(
                        (db.course_activity_log.before_course == project_t)
                        | (db.course_activity_log.after_course == project_t)
                    )
                    .select()
                    .first()
                )
                if project.before_course is not None:
                    project = project.before_course
                else:
                    project = project.after_course
            else:
                project = project.name
            infoe_level_temp = []
            # NAME OF PROJECT
            infoe_level_temp.append(project)
            # MADE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_request<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.after_status = "pending"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_request<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.after_status = "pending" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_i)
            # ACCEPTED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_operation<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.after_status = "accepted"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_operation<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.after_status = "accepted" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_i)
            # REJECTED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_operation<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.after_status = "rejected"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_operation<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.after_status = "rejected" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_i)
            ##CANCELED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "c"
            ):
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_operation<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.after_status = "canceled"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_operation<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.after_status = "canceled" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_i)
            # PENDING
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "p"
            ):
                if period.period == 1:
                    if personal_query == "":
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_request >="'
                            + str(period.yearp)
                            + '-01-01" and request_change_g_log.date_request<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.after_status = "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_request >="'
                            + str(period.yearp)
                            + '-01-01" and request_change_g_log.date_request<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.after_status = "pending" and '
                            + personal_query
                        )
                    count_p = db.smart_query(db.request_change_g_log, search).count()
                    if personal_query == "":
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_operation >="'
                            + str(period.yearp)
                            + '-01-01" and request_change_g_log.date_operation<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.after_status != "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_operation >="'
                            + str(period.yearp)
                            + '-01-01" and request_change_g_log.date_operation<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.after_status != "pending" and '
                            + personal_query
                        )
                    count_n_p = db.smart_query(db.request_change_g_log, search).count()
                else:
                    if personal_query == "":
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_request >="'
                            + str(period.yearp)
                            + '-06-01" and request_change_g_log.date_request<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.after_status = "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_request >="'
                            + str(period.yearp)
                            + '-06-01" and request_change_g_log.date_request<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.after_status = "pending" and '
                            + personal_query
                        )
                    count_p = db.smart_query(db.request_change_g_log, search).count()
                    if personal_query == "":
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_operation >="'
                            + str(period.yearp)
                            + '-06-01" and request_change_g_log.date_operation<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.after_status != "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_operation >="'
                            + str(period.yearp)
                            + '-06-01" and request_change_g_log.date_operation<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.after_status != "pending" and '
                            + personal_query
                        )
                    count_n_p = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_p - count_n_p)
            # INSERT PROJECT
            info_level.append(infoe_level_temp)
    # PER USER
    elif str(request.vars["level"]) == "4":
        # USERS
        users_project = get_users(
            period, project, "Student", "requestchange_activity_log"
        )
        # PERIOD OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MONTH OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        infoe_level_temp.append(str(month[0]))
        info_level.append(infoe_level_temp)
        # PROJECT OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Project"))
        infoe_level_temp.append(str(project))
        info_level.append(infoe_level_temp)
        # ROL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Role"))
        infoe_level_temp.append(T("Rol Student"))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # LABELS OF DATA OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("User"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "d":
            infoe_level_temp.append(T("Total Made Requests"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "i":
            infoe_level_temp.append(T("Total Accepted request"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "u":
            infoe_level_temp.append(T("Total Rejected request"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "c":
            infoe_level_temp.append(T("Total Canceled request"))
        if str(request.vars["type_L"]) == "all" or str(request.vars["type_L"]) == "p":
            infoe_level_temp.append(T("Total Pending Requests"))
        info_level.append(infoe_level_temp)

        for user_p_t in users_project:
            user_p = db(db.auth_user.username == user_p_t).select().first()
            if user_p is None:
                user_p = (
                    db(db.request_change_g_log.user_request == user_p_t).select().first()
                )
                user_p = user_p.user_request
            else:
                user_p = user_p.username
            infoe_level_temp = []
            # NAME OF USER
            infoe_level_temp.append(user_p)
            # MADE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_request<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "pending"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_request<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "pending" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_i)
            # ACCEPTED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_operation<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "accepted"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_operation<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "accepted" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_i)
            # REJECTED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_operation<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "rejected"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_operation<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "rejected" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_i)
            ##CANCELED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "c"
            ):
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_operation<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "canceled"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_operation<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "canceled" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_i)
            # PENDING
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "p"
            ):
                if period.period == 1:
                    if personal_query == "":
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_request >="'
                            + str(period.yearp)
                            + '-01-01" and request_change_g_log.date_request<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                            + str(user_p)
                            + '" and request_change_g_log.after_status = "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_request >="'
                            + str(period.yearp)
                            + '-01-01" and request_change_g_log.date_request<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                            + str(user_p)
                            + '" and request_change_g_log.after_status = "pending" and '
                            + personal_query
                        )
                    count_p = db.smart_query(db.request_change_g_log, search).count()
                    if personal_query == "":
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_operation >="'
                            + str(period.yearp)
                            + '-01-01" and request_change_g_log.date_operation<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                            + str(user_p)
                            + '" and request_change_g_log.after_status != "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_operation >="'
                            + str(period.yearp)
                            + '-01-01" and request_change_g_log.date_operation<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                            + str(user_p)
                            + '" and request_change_g_log.after_status != "pending" and '
                            + personal_query
                        )
                    count_n_p = db.smart_query(db.request_change_g_log, search).count()
                else:
                    if personal_query == "":
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_request >="'
                            + str(period.yearp)
                            + '-06-01" and request_change_g_log.date_request<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                            + str(user_p)
                            + '" and request_change_g_log.after_status = "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_request >="'
                            + str(period.yearp)
                            + '-06-01" and request_change_g_log.date_request<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                            + str(user_p)
                            + '" and request_change_g_log.after_status = "pending" and '
                            + personal_query
                        )
                    count_p = db.smart_query(db.request_change_g_log, search).count()
                    if personal_query == "":
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_operation >="'
                            + str(period.yearp)
                            + '-06-01" and request_change_g_log.date_operation<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                            + str(user_p)
                            + '" and request_change_g_log.after_status != "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_operation >="'
                            + str(period.yearp)
                            + '-06-01" and request_change_g_log.date_operation<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                            + str(user_p)
                            + '" and request_change_g_log.after_status != "pending" and '
                            + personal_query
                        )
                    count_n_p = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_p - count_n_p)
            # INSERT USER
            info_level.append(infoe_level_temp)
    # DATA
    elif str(request.vars["level"]) == "5":
        # PERIOD
        infoe_level_temp = []
        infoe_level_temp.append(T("Period"))
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        info_level.append(infoe_level_temp)
        # MONTH
        infoe_level_temp = []
        infoe_level_temp.append(T("Month"))
        infoe_level_temp.append(str(month[0]))
        info_level.append(infoe_level_temp)
        # PROJECT
        infoe_level_temp = []
        infoe_level_temp.append(T("Project"))
        infoe_level_temp.append(str(project))
        info_level.append(infoe_level_temp)
        # ROL
        infoe_level_temp = []
        infoe_level_temp.append(T("Role"))
        infoe_level_temp.append(T("Rol Student"))
        info_level.append(infoe_level_temp)
        # USER
        infoe_level_temp = []
        infoe_level_temp.append(T("User"))
        infoe_level_temp.append(str(user_p))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE
        infoe_level_temp = []
        infoe_level_temp.append("")
        info_level.append(infoe_level_temp)
        # DETAIL
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # TITLE OF TABLE
        infoe_level_temp = []
        infoe_level_temp.append("Estado")
        infoe_level_temp.append("Estado")
        infoe_level_temp.append("Usuario Resolvio")
        infoe_level_temp.append("Rol Resolvio")
        infoe_level_temp.append("Descripción")
        infoe_level_temp.append("Descripción LOG")
        infoe_level_temp.append("Fecha")
        infoe_level_temp.append("Fecha Solicitud")
        infoe_level_temp.append("Fecha Resolvio")
        infoe_level_temp.append("Actividad")
        infoe_level_temp.append("Categoria")
        info_level.append(infoe_level_temp)

        # MADE
        if str(request.vars["type_L"]) == "d":
            if personal_query == "":
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_request >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_request<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "pending"'
                )
            else:
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_request >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_request<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "pending" and '
                    + personal_query
                )
            for data in db.smart_query(db.request_change_g_log, search).select():
                infoe_level_temp = []
                infoe_level_temp.append(data.before_status)
                infoe_level_temp.append(data.after_status)
                infoe_level_temp.append(data.resolve_user)
                infoe_level_temp.append(data.roll_resolve)
                infoe_level_temp.append(data.description)
                infoe_level_temp.append(data.description_log)
                infoe_level_temp.append(data.date_operation)
                infoe_level_temp.append(data.date_request)
                infoe_level_temp.append(data.date_request_resolve)
                infoe_level_temp.append(data.activity)
                infoe_level_temp.append(data.category)
                info_level.append(infoe_level_temp)
                infoe_level_temp = []
                infoe_level_temp.append("")
                infoe_level_temp.append("")
                infoe_level_temp.append(T("Operation"))
                infoe_level_temp.append(T("Academic"))
                infoe_level_temp.append(T("Before Grade"))
                infoe_level_temp.append(T("After Grade"))
                info_level.append(infoe_level_temp)
                for details in db(
                    db.request_change_grade_d_log.request_change_g_log == data.id
                ).select():
                    infoe_level_temp = []
                    infoe_level_temp.append("")
                    infoe_level_temp.append("")
                    infoe_level_temp.append(details.operation_request)
                    infoe_level_temp.append(details.academic)
                    infoe_level_temp.append(details.before_grade)
                    infoe_level_temp.append(details.after_grade)
                    info_level.append(infoe_level_temp)
                infoe_level_temp = []
                infoe_level_temp.append("")
                info_level.append(infoe_level_temp)
        # ACCEPTED
        elif str(request.vars["type_L"]) == "i":
            if personal_query == "":
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_operation >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_operation<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "accepted"'
                )
            else:
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_operation >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_operation<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "accepted" and '
                    + personal_query
                )
            for data in db.smart_query(db.request_change_g_log, search).select():
                infoe_level_temp = []
                infoe_level_temp.append(data.before_status)
                infoe_level_temp.append(data.after_status)
                infoe_level_temp.append(data.resolve_user)
                infoe_level_temp.append(data.roll_resolve)
                infoe_level_temp.append(data.description)
                infoe_level_temp.append(data.description_log)
                infoe_level_temp.append(data.date_operation)
                infoe_level_temp.append(data.date_request)
                infoe_level_temp.append(data.date_request_resolve)
                infoe_level_temp.append(data.activity)
                infoe_level_temp.append(data.category)
                info_level.append(infoe_level_temp)
                infoe_level_temp = []
                infoe_level_temp.append("")
                infoe_level_temp.append("")
                infoe_level_temp.append(T("Operation"))
                infoe_level_temp.append(T("Academic"))
                infoe_level_temp.append(T("Before Grade"))
                infoe_level_temp.append(T("After Grade"))
                info_level.append(infoe_level_temp)
                for details in db(
                    db.request_change_grade_d_log.request_change_g_log == data.id
                ).select():
                    infoe_level_temp = []
                    infoe_level_temp.append("")
                    infoe_level_temp.append("")
                    infoe_level_temp.append(details.operation_request)
                    infoe_level_temp.append(details.academic)
                    infoe_level_temp.append(details.before_grade)
                    infoe_level_temp.append(details.after_grade)
                    info_level.append(infoe_level_temp)
                infoe_level_temp = []
                infoe_level_temp.append("")
                info_level.append(infoe_level_temp)
        # REJECTED
        elif str(request.vars["type_L"]) == "u":
            if personal_query == "":
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_operation >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_operation<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "rejected"'
                )
            else:
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_operation >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_operation<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "rejected" and '
                    + personal_query
                )
            for data in db.smart_query(db.request_change_g_log, search).select():
                infoe_level_temp = []
                infoe_level_temp.append(data.before_status)
                infoe_level_temp.append(data.after_status)
                infoe_level_temp.append(data.resolve_user)
                infoe_level_temp.append(data.roll_resolve)
                infoe_level_temp.append(data.description)
                infoe_level_temp.append(data.description_log)
                infoe_level_temp.append(data.date_operation)
                infoe_level_temp.append(data.date_request)
                infoe_level_temp.append(data.date_request_resolve)
                infoe_level_temp.append(data.activity)
                infoe_level_temp.append(data.category)
                info_level.append(infoe_level_temp)
                infoe_level_temp = []
                infoe_level_temp.append("")
                infoe_level_temp.append("")
                infoe_level_temp.append(T("Operation"))
                infoe_level_temp.append(T("Academic"))
                infoe_level_temp.append(T("Before Grade"))
                infoe_level_temp.append(T("After Grade"))
                info_level.append(infoe_level_temp)
                for details in db(
                    db.request_change_grade_d_log.request_change_g_log == data.id
                ).select():
                    infoe_level_temp = []
                    infoe_level_temp.append("")
                    infoe_level_temp.append("")
                    infoe_level_temp.append(details.operation_request)
                    infoe_level_temp.append(details.academic)
                    infoe_level_temp.append(details.before_grade)
                    infoe_level_temp.append(details.after_grade)
                    info_level.append(infoe_level_temp)
                infoe_level_temp = []
                infoe_level_temp.append("")
                info_level.append(infoe_level_temp)
        ##CANCELED
        elif str(request.vars["type_L"]) == "c":
            if personal_query == "":
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_operation >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_operation<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "canceled"'
                )
            else:
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_operation >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_operation<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "canceled" and '
                    + personal_query
                )
            for data in db.smart_query(db.request_change_g_log, search).select():
                infoe_level_temp = []
                infoe_level_temp.append(data.before_status)
                infoe_level_temp.append(data.after_status)
                infoe_level_temp.append(data.resolve_user)
                infoe_level_temp.append(data.roll_resolve)
                infoe_level_temp.append(data.description)
                infoe_level_temp.append(data.description_log)
                infoe_level_temp.append(data.date_operation)
                infoe_level_temp.append(data.date_request)
                infoe_level_temp.append(data.date_request_resolve)
                infoe_level_temp.append(data.activity)
                infoe_level_temp.append(data.category)
                info_level.append(infoe_level_temp)
                infoe_level_temp = []
                infoe_level_temp.append("")
                infoe_level_temp.append("")
                infoe_level_temp.append(T("Operation"))
                infoe_level_temp.append(T("Academic"))
                infoe_level_temp.append(T("Before Grade"))
                infoe_level_temp.append(T("After Grade"))
                info_level.append(infoe_level_temp)
                for details in db(
                    db.request_change_grade_d_log.request_change_g_log == data.id
                ).select():
                    infoe_level_temp = []
                    infoe_level_temp.append("")
                    infoe_level_temp.append("")
                    infoe_level_temp.append(details.operation_request)
                    infoe_level_temp.append(details.academic)
                    infoe_level_temp.append(details.before_grade)
                    infoe_level_temp.append(details.after_grade)
                    info_level.append(infoe_level_temp)
                infoe_level_temp = []
                infoe_level_temp.append("")
                info_level.append(infoe_level_temp)
        # PENDING
        elif str(request.vars["type_L"]) == "p":
            if period.period == 1:
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(period.yearp)
                        + '-01-01" and request_change_g_log.date_request<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "pending"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(period.yearp)
                        + '-01-01" and request_change_g_log.date_request<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "pending" and '
                        + personal_query
                    )
                for pending in db.smart_query(db.request_change_g_log, search).select():
                    if personal_query == "":
                        search = (
                            'request_change_g_log.r_c_g_id = "'
                            + str(pending.r_c_g_id)
                            + '" and request_change_g_log.after_status != "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.r_c_g_id = "'
                            + str(pending.r_c_g_id)
                            + '" and request_change_g_log.after_status != "pending" and '
                            + personal_query
                        )
                    if (
                        db.smart_query(db.request_change_g_log, search).select().first()
                        is None
                    ):
                        infoe_level_temp = []
                        infoe_level_temp.append(pending.before_status)
                        infoe_level_temp.append(pending.after_status)
                        infoe_level_temp.append(pending.resolve_user)
                        infoe_level_temp.append(pending.roll_resolve)
                        infoe_level_temp.append(pending.description)
                        infoe_level_temp.append(pending.description_log)
                        infoe_level_temp.append(pending.date_operation)
                        infoe_level_temp.append(pending.date_request)
                        infoe_level_temp.append(pending.date_request_resolve)
                        infoe_level_temp.append(pending.activity)
                        infoe_level_temp.append(pending.category)
                        info_level.append(infoe_level_temp)
                        infoe_level_temp = []
                        infoe_level_temp.append("")
                        infoe_level_temp.append("")
                        infoe_level_temp.append(T("Operation"))
                        infoe_level_temp.append(T("Academic"))
                        infoe_level_temp.append(T("Before Grade"))
                        infoe_level_temp.append(T("After Grade"))
                        info_level.append(infoe_level_temp)
                        for details in db(
                            db.request_change_grade_d_log.request_change_g_log
                            == pending.id
                        ).select():
                            infoe_level_temp = []
                            infoe_level_temp.append("")
                            infoe_level_temp.append("")
                            infoe_level_temp.append(details.operation_request)
                            infoe_level_temp.append(details.academic)
                            infoe_level_temp.append(details.before_grade)
                            infoe_level_temp.append(details.after_grade)
                            info_level.append(infoe_level_temp)
                        infoe_level_temp = []
                        infoe_level_temp.append("")
                        info_level.append(infoe_level_temp)
            else:
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(period.yearp)
                        + '-06-01" and request_change_g_log.date_request<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "pending"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(period.yearp)
                        + '-06-01" and request_change_g_log.date_request<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "pending" and '
                        + personal_query
                    )
                for pending in db.smart_query(db.request_change_g_log, search).select():
                    if personal_query == "":
                        search = (
                            'request_change_g_log.r_c_g_id = "'
                            + str(pending.r_c_g_id)
                            + '" and request_change_g_log.after_status != "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.r_c_g_id = "'
                            + str(pending.r_c_g_id)
                            + '" and request_change_g_log.after_status != "pending" and '
                            + personal_query
                        )
                    if (
                        db.smart_query(db.request_change_g_log, search).select().first()
                        is None
                    ):
                        infoe_level_temp = []
                        infoe_level_temp.append(pending.before_status)
                        infoe_level_temp.append(pending.after_status)
                        infoe_level_temp.append(pending.resolve_user)
                        infoe_level_temp.append(pending.roll_resolve)
                        infoe_level_temp.append(pending.description)
                        infoe_level_temp.append(pending.description_log)
                        infoe_level_temp.append(pending.date_operation)
                        infoe_level_temp.append(pending.date_request)
                        infoe_level_temp.append(pending.date_request_resolve)
                        infoe_level_temp.append(pending.activity)
                        infoe_level_temp.append(pending.category)
                        info_level.append(infoe_level_temp)
                        infoe_level_temp = []
                        infoe_level_temp.append("")
                        infoe_level_temp.append("")
                        infoe_level_temp.append(T("Operation"))
                        infoe_level_temp.append(T("Academic"))
                        infoe_level_temp.append(T("Before Grade"))
                        infoe_level_temp.append(T("After Grade"))
                        info_level.append(infoe_level_temp)
                        for details in db(
                            db.request_change_grade_d_log.request_change_g_log
                            == pending.id
                        ).select():
                            infoe_level_temp = []
                            infoe_level_temp.append("")
                            infoe_level_temp.append("")
                            infoe_level_temp.append(details.operation_request)
                            infoe_level_temp.append(details.academic)
                            infoe_level_temp.append(details.before_grade)
                            infoe_level_temp.append(details.after_grade)
                            info_level.append(infoe_level_temp)
                        infoe_level_temp = []
                        infoe_level_temp.append("")
                        info_level.append(infoe_level_temp)
        # ALL
        elif str(request.vars["type_L"]) == "all":
            # MADE AND PENDING
            if period.period == 1:
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(period.yearp)
                        + '-01-01" and request_change_g_log.date_request<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "pending"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(period.yearp)
                        + '-01-01" and request_change_g_log.date_request<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "pending" and '
                        + personal_query
                    )
                for pending in db.smart_query(db.request_change_g_log, search).select():
                    if personal_query == "":
                        search = (
                            'request_change_g_log.r_c_g_id = "'
                            + str(pending.r_c_g_id)
                            + '" and request_change_g_log.after_status != "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.r_c_g_id = "'
                            + str(pending.r_c_g_id)
                            + '" and request_change_g_log.after_status != "pending" and '
                            + personal_query
                        )
                    if (
                        db.smart_query(db.request_change_g_log, search).select().first()
                        is None
                    ):
                        infoe_level_temp = []
                        infoe_level_temp.append(pending.before_status)
                        infoe_level_temp.append(pending.after_status)
                        infoe_level_temp.append(pending.resolve_user)
                        infoe_level_temp.append(pending.roll_resolve)
                        infoe_level_temp.append(pending.description)
                        infoe_level_temp.append(pending.description_log)
                        infoe_level_temp.append(pending.date_operation)
                        infoe_level_temp.append(pending.date_request)
                        infoe_level_temp.append(pending.date_request_resolve)
                        infoe_level_temp.append(pending.activity)
                        infoe_level_temp.append(pending.category)
                        info_level.append(infoe_level_temp)
                        infoe_level_temp = []
                        infoe_level_temp.append("")
                        infoe_level_temp.append("")
                        infoe_level_temp.append(T("Operation"))
                        infoe_level_temp.append(T("Academic"))
                        infoe_level_temp.append(T("Before Grade"))
                        infoe_level_temp.append(T("After Grade"))
                        info_level.append(infoe_level_temp)
                        for details in db(
                            db.request_change_grade_d_log.request_change_g_log
                            == pending.id
                        ).select():
                            infoe_level_temp = []
                            infoe_level_temp.append("")
                            infoe_level_temp.append("")
                            infoe_level_temp.append(details.operation_request)
                            infoe_level_temp.append(details.academic)
                            infoe_level_temp.append(details.before_grade)
                            infoe_level_temp.append(details.after_grade)
                            info_level.append(infoe_level_temp)
                        infoe_level_temp = []
                        infoe_level_temp.append("")
                        info_level.append(infoe_level_temp)
            else:
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(period.yearp)
                        + '-06-01" and request_change_g_log.date_request<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "pending"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(period.yearp)
                        + '-06-01" and request_change_g_log.date_request<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "pending" and '
                        + personal_query
                    )
                for pending in db.smart_query(db.request_change_g_log, search).select():
                    if personal_query == "":
                        search = (
                            'request_change_g_log.r_c_g_id = "'
                            + str(pending.r_c_g_id)
                            + '" and request_change_g_log.after_status != "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.r_c_g_id = "'
                            + str(pending.r_c_g_id)
                            + '" and request_change_g_log.after_status != "pending" and '
                            + personal_query
                        )
                    if (
                        db.smart_query(db.request_change_g_log, search).select().first()
                        is None
                    ):
                        infoe_level_temp = []
                        infoe_level_temp.append(pending.before_status)
                        infoe_level_temp.append(pending.after_status)
                        infoe_level_temp.append(pending.resolve_user)
                        infoe_level_temp.append(pending.roll_resolve)
                        infoe_level_temp.append(pending.description)
                        infoe_level_temp.append(pending.description_log)
                        infoe_level_temp.append(pending.date_operation)
                        infoe_level_temp.append(pending.date_request)
                        infoe_level_temp.append(pending.date_request_resolve)
                        infoe_level_temp.append(pending.activity)
                        infoe_level_temp.append(pending.category)
                        info_level.append(infoe_level_temp)
                        infoe_level_temp = []
                        infoe_level_temp.append("")
                        infoe_level_temp.append("")
                        infoe_level_temp.append(T("Operation"))
                        infoe_level_temp.append(T("Academic"))
                        infoe_level_temp.append(T("Before Grade"))
                        infoe_level_temp.append(T("After Grade"))
                        info_level.append(infoe_level_temp)
                        for details in db(
                            db.request_change_grade_d_log.request_change_g_log
                            == pending.id
                        ).select():
                            infoe_level_temp = []
                            infoe_level_temp.append("")
                            infoe_level_temp.append("")
                            infoe_level_temp.append(details.operation_request)
                            infoe_level_temp.append(details.academic)
                            infoe_level_temp.append(details.before_grade)
                            infoe_level_temp.append(details.after_grade)
                            info_level.append(infoe_level_temp)
                        infoe_level_temp = []
                        infoe_level_temp.append("")
                        info_level.append(infoe_level_temp)
            # ACCEPTED
            if personal_query == "":
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_operation >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_operation<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "accepted"'
                )
            else:
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_operation >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_operation<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "accepted" and '
                    + personal_query
                )
            for data in db.smart_query(db.request_change_g_log, search).select():
                infoe_level_temp = []
                infoe_level_temp.append(data.before_status)
                infoe_level_temp.append(data.after_status)
                infoe_level_temp.append(data.resolve_user)
                infoe_level_temp.append(data.roll_resolve)
                infoe_level_temp.append(data.description)
                infoe_level_temp.append(data.description_log)
                infoe_level_temp.append(data.date_operation)
                infoe_level_temp.append(data.date_request)
                infoe_level_temp.append(data.date_request_resolve)
                infoe_level_temp.append(data.activity)
                infoe_level_temp.append(data.category)
                info_level.append(infoe_level_temp)
                infoe_level_temp = []
                infoe_level_temp.append("")
                infoe_level_temp.append("")
                infoe_level_temp.append(T("Operation"))
                infoe_level_temp.append(T("Academic"))
                infoe_level_temp.append(T("Before Grade"))
                infoe_level_temp.append(T("After Grade"))
                info_level.append(infoe_level_temp)
                for details in db(
                    db.request_change_grade_d_log.request_change_g_log == data.id
                ).select():
                    infoe_level_temp = []
                    infoe_level_temp.append("")
                    infoe_level_temp.append("")
                    infoe_level_temp.append(details.operation_request)
                    infoe_level_temp.append(details.academic)
                    infoe_level_temp.append(details.before_grade)
                    infoe_level_temp.append(details.after_grade)
                    info_level.append(infoe_level_temp)
                infoe_level_temp = []
                infoe_level_temp.append("")
                info_level.append(infoe_level_temp)
            # REJECTED
            if personal_query == "":
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_operation >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_operation<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "rejected"'
                )
            else:
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_operation >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_operation<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "rejected" and '
                    + personal_query
                )
            for data in db.smart_query(db.request_change_g_log, search).select():
                infoe_level_temp = []
                infoe_level_temp.append(data.before_status)
                infoe_level_temp.append(data.after_status)
                infoe_level_temp.append(data.resolve_user)
                infoe_level_temp.append(data.roll_resolve)
                infoe_level_temp.append(data.description)
                infoe_level_temp.append(data.description_log)
                infoe_level_temp.append(data.date_operation)
                infoe_level_temp.append(data.date_request)
                infoe_level_temp.append(data.date_request_resolve)
                infoe_level_temp.append(data.activity)
                infoe_level_temp.append(data.category)
                info_level.append(infoe_level_temp)
                infoe_level_temp = []
                infoe_level_temp.append("")
                infoe_level_temp.append("")
                infoe_level_temp.append(T("Operation"))
                infoe_level_temp.append(T("Academic"))
                infoe_level_temp.append(T("Before Grade"))
                infoe_level_temp.append(T("After Grade"))
                info_level.append(infoe_level_temp)
                for details in db(
                    db.request_change_grade_d_log.request_change_g_log == data.id
                ).select():
                    infoe_level_temp = []
                    infoe_level_temp.append("")
                    infoe_level_temp.append("")
                    infoe_level_temp.append(details.operation_request)
                    infoe_level_temp.append(details.academic)
                    infoe_level_temp.append(details.before_grade)
                    infoe_level_temp.append(details.after_grade)
                    info_level.append(infoe_level_temp)
                infoe_level_temp = []
                infoe_level_temp.append("")
                info_level.append(infoe_level_temp)
            ##CANCELED
            if personal_query == "":
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_operation >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_operation<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "canceled"'
                )
            else:
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_operation >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_operation<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "canceled" and '
                    + personal_query
                )
            for data in db.smart_query(db.request_change_g_log, search).select():
                infoe_level_temp = []
                infoe_level_temp.append(data.before_status)
                infoe_level_temp.append(data.after_status)
                infoe_level_temp.append(data.resolve_user)
                infoe_level_temp.append(data.roll_resolve)
                infoe_level_temp.append(data.description)
                infoe_level_temp.append(data.description_log)
                infoe_level_temp.append(data.date_operation)
                infoe_level_temp.append(data.date_request)
                infoe_level_temp.append(data.date_request_resolve)
                infoe_level_temp.append(data.activity)
                infoe_level_temp.append(data.category)
                info_level.append(infoe_level_temp)
                infoe_level_temp = []
                infoe_level_temp.append("")
                infoe_level_temp.append("")
                infoe_level_temp.append(T("Operation"))
                infoe_level_temp.append(T("Academic"))
                infoe_level_temp.append(T("Before Grade"))
                infoe_level_temp.append(T("After Grade"))
                info_level.append(infoe_level_temp)
                for details in db(
                    db.request_change_grade_d_log.request_change_g_log == data.id
                ).select():
                    infoe_level_temp = []
                    infoe_level_temp.append("")
                    infoe_level_temp.append("")
                    infoe_level_temp.append(details.operation_request)
                    infoe_level_temp.append(details.academic)
                    infoe_level_temp.append(details.before_grade)
                    infoe_level_temp.append(details.after_grade)
                    info_level.append(infoe_level_temp)
                infoe_level_temp = []
                infoe_level_temp.append("")
                info_level.append(infoe_level_temp)
    # *****************************************************REPORT*****************************************************
    # ****************************************************************************************************************
    # ****************************************************************************************************************
    return dict(filename="ReporteGestionSolicitudesCambioNotas", csvdata=info_level)


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator")
    or auth.has_membership("Ecys-Administrator")
)
def crg_load():
    request_c = None
    request_d = None
    show_level = False
    try:
        request_c = (
            db(db.request_change_g_log.id == int(request.vars["id"])).select().first()
        )
        if request_c is not None:
            show_level = True
            request_d = db(
                db.request_change_grade_d_log.request_change_g_log
                == int(request.vars["id"])
            ).select()
    except:
        show_level = False
    return dict(showLevel=show_level, requestC=request_c, requestD=request_d)


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator")
    or auth.has_membership("Ecys-Administrator")
)
def change_request_grades_management():
    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # ***************************************CHECK IF THERE IS A PERSONALIZED QUERY***********************************
    personal_query = ""
    make_redirect = False
    if (
        request.vars["querySearch"] is not None
        and str(request.vars["querySearch"]) != ""
    ):
        # PERSONALIZED QUERY SURE WORK
        try:
            personal_query = str(request.vars["querySearch"])
            count_i = db.smart_query(db.request_change_g_log, personal_query).count()
            if (
                request.vars["searchT"] is not None
                and str(request.vars["searchT"]) == "T"
            ):
                make_redirect = True
        except:
            response.flash = T(
                "The query is not valid. The report is displayed without applying any query."
            )
            personal_query = ""
    if make_redirect == True:
        redirect(
            URL(
                "management_reports",
                "change_request_grades_management",
                vars=dict(
                    level="5",
                    period=request.vars["period"],
                    month=str(request.vars["month"]),
                    project=str(request.vars["project"]),
                    userP=str(request.vars["userP"]),
                    type_L=request.vars["type_L"],
                    type_U=request.vars["type_U"],
                    querySearch=request.vars["querySearch"],
                ),
            )
        )

    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # ******************************************VERIFY THAT ACCURATE PARAMETERS***************************************
    try:
        # CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars["level"] is not None and (
            int(request.vars["level"]) < 1 or int(request.vars["level"]) > 5
        ):
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))

        # VERIFY THAT THE PARAMETERS OF EACH LEVEL BE VALID
        if request.vars["level"] is not None:
            # LEVEL MORE THAN 1
            if int(request.vars["level"]) > 1:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_L"] is None or (
                    str(request.vars["type_L"]) != "all"
                    and str(request.vars["type_L"]) != "i"
                    and str(request.vars["type_L"]) != "u"
                    and str(request.vars["type_L"]) != "d"
                    and str(request.vars["type_L"]) != "p"
                    and str(request.vars["type_L"]) != "c"
                ):
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

                period = validate_period(request.vars["period"])
                if period is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 2
            if int(request.vars["level"]) > 2:
                # CHECK IF THE TYPE OF REPORT IS VALID
                if request.vars["type_U"] is None or (
                    str(request.vars["type_U"]) != "all"
                    and str(request.vars["type_U"]) != "i"
                    and str(request.vars["type_U"]) != "u"
                    and str(request.vars["type_U"]) != "d"
                    and str(request.vars["type_L"]) != "p"
                    and str(request.vars["type_L"]) != "c"
                ):
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

                # CHECK IF THE MONTH IS VALID
                month = validate_month(request.vars["month"], period)
                if month is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 3
            if int(request.vars["level"]) > 3:
                # CHECK IF THE PROJECT IS VALID
                project = validate_project(
                    request.vars["project"], "request_change_g_log"
                )
                if project is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

            # LEVEL MORE THAN 4
            if int(request.vars["level"]) > 4:
                # CHECK IF THE USER IS VALID
                user_p = validate_user(
                    period,
                    project,
                    "Student",
                    request.vars["userP"],
                    "request_change_g_log",
                )
                if user_p is None:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))
    except:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # **************************************************SEARCH REPORT*************************************************
    def filtered_by(flag):
        fsearch_option = []
        fsearch_option.append("=")
        fsearch_option.append("!=")
        fsearch_option.append("<")
        fsearch_option.append(">")
        fsearch_option.append("<=")
        fsearch_option.append(">=")
        if flag == True:
            fsearch_option.append("starts with")
            fsearch_option.append("contains")
            fsearch_option.append("in")
            fsearch_option.append("not in")
        return fsearch_option

    fsearch = []
    # ******************************COMBOS INFORMATION******************************
    # YEARS
    if request.vars["level"] == "1" or request.vars["level"] is None:
        group_years = get_years()
        if len(group_years) != 0:
            fsearch.append(["yearp", "Año", False, [3, sorted(group_years)]])
    # PROJECTS
    if request.vars["level"] is None or int(request.vars["level"]) <= 3:
        # projects = get_projects('request_change_g_log')
        try:
            projects = get_projects("request_change_g_log", period)
        except:
            projects = get_projects("request_change_g_log", None)
        if len(projects) != 0:
            fsearch_Values = []
            fsearch_Values.append(2)
            for project_t in projects:
                project = db(db.project.name == project_t).select().first()
                if project is None:
                    project = (
                        db(db.request_change_g_log.project == project_t).select().first()
                    )
                    project = project.project
                else:
                    project = project.name
                fsearch_Values.append(project)
            fsearch.append(["project", "Curso", False, fsearch_Values])
    # OPERATION LOG
    fsearch.append(
        [
            "after_status",
            "Estado",
            False,
            [3, ["accepted", "rejected", "pending", "canceled"]],
        ]
    )
    # CATEGORIES
    group_categories = get_categories("request_change_g_log")
    if len(group_categories) != 0:
        fsearch.append(["category", "Categoria", False, [3, sorted(group_categories)]])
    # ACTIVITIES
    group_activities = get_activities("request_change_g_log")
    if len(group_activities) != 0:
        fsearch.append(["activity", "Actividad", False, [3, sorted(group_activities)]])
    # DATES
    dates = get_dates("request_change_g_log")
    if len(dates) != 0:
        fsearch.append(["date_request", "Fecha", False, [3, sorted(dates)]])
    # ******************************ENTERING USER******************************
    # USER REQUEST
    if request.vars["level"] is None or int(request.vars["level"]) <= 4:
        fsearch.append(["user_request", "Usuario Solicitud", False, [1]])

    # ****************************************************************************************************************
    # ****************************************************************************************************************
    # *****************************************************REPORT*****************************************************
    # LEVELS OF REPORT
    
    info_level = []
    grid = []
    # ALL SEMESTERS
    if request.vars["level"] == "1" or request.vars["level"] is None:
        group_periods = db(db.period_year).select(orderby=~db.period_year.id)
        if len(group_periods) == 0:
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(URL("default", "home"))
        for period in group_periods:
            infoe_level_temp = []
            # ID OF PERIOD
            infoe_level_temp.append(period.id)
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # MADE
            if personal_query == "":
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.after_status = "pending"'
                )
            else:
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.after_status = "pending" and '
                    + personal_query
                )
            count_i = db.smart_query(db.request_change_g_log, search).count()
            infoe_level_temp.append(count_i)
            # ACCEPTED
            if personal_query == "":
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.after_status = "accepted"'
                )
            else:
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.after_status = "accepted" and '
                    + personal_query
                )
            count_i = db.smart_query(db.request_change_g_log, search).count()
            infoe_level_temp.append(count_i)
            # REJECTED
            if personal_query == "":
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.after_status = "rejected"'
                )
            else:
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.after_status = "rejected" and '
                    + personal_query
                )
            count_i = db.smart_query(db.request_change_g_log, search).count()
            infoe_level_temp.append(count_i)
            # CANCELED
            if personal_query == "":
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.after_status = "canceled"'
                )
            else:
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.after_status = "canceled" and '
                    + personal_query
                )
            count_i = db.smart_query(db.request_change_g_log, search).count()
            infoe_level_temp.append(count_i)
            # PENDING
            infoe_level_temp.append(
                infoe_level_temp[2]
                - infoe_level_temp[3]
                - infoe_level_temp[4]
                - infoe_level_temp[5]
            )
            # INSERT PERIOD
            info_level.append(infoe_level_temp)
    # PER MONTH
    elif str(request.vars["level"]) == "2":
        for month in get_month_period(period):
            start = datetime.strptime(
                str(period.yearp) + "-" + str(month[0]) + "-01", "%Y-%m-%d"
            )
            if month[2] == 1:
                end = datetime.strptime(
                    str(period.yearp + 1) + "-" + str(month[2]) + "-01", "%Y-%m-%d"
                )
            else:
                end = datetime.strptime(
                    str(period.yearp) + "-" + str(month[2]) + "-01", "%Y-%m-%d"
                )
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # ID OF MONTH
            infoe_level_temp.append(month[0])
            # NAME OF MONTH
            infoe_level_temp.append(month[1] + " " + str(period.yearp))
            # MADE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(start)
                        + '" and request_change_g_log.date_request<"'
                        + str(end)
                        + '" and request_change_g_log.after_status = "pending"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(start)
                        + '" and request_change_g_log.date_request<"'
                        + str(end)
                        + '" and request_change_g_log.after_status = "pending" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_i)
            # ACCEPTED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(start)
                        + '" and request_change_g_log.date_operation<"'
                        + str(end)
                        + '" and request_change_g_log.after_status = "accepted"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(start)
                        + '" and request_change_g_log.date_operation<"'
                        + str(end)
                        + '" and request_change_g_log.after_status = "accepted" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_i)
            # REJECTED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(start)
                        + '" and request_change_g_log.date_operation<"'
                        + str(end)
                        + '" and request_change_g_log.after_status = "rejected"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(start)
                        + '" and request_change_g_log.date_operation<"'
                        + str(end)
                        + '" and request_change_g_log.after_status = "rejected" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_i)
            ##CANCELED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "c"
            ):
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(start)
                        + '" and request_change_g_log.date_operation<"'
                        + str(end)
                        + '" and request_change_g_log.after_status = "canceled"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(start)
                        + '" and request_change_g_log.date_operation<"'
                        + str(end)
                        + '" and request_change_g_log.after_status = "canceled" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_i)
            # PENDING
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "p"
            ):
                if period.period == 1:
                    if personal_query == "":
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_request >="'
                            + str(period.yearp)
                            + '-01-01" and request_change_g_log.date_request<"'
                            + str(end)
                            + '" and request_change_g_log.after_status = "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_request >="'
                            + str(period.yearp)
                            + '-01-01" and request_change_g_log.date_request<"'
                            + str(end)
                            + '" and request_change_g_log.after_status = "pending" and '
                            + personal_query
                        )
                    count_p = db.smart_query(db.request_change_g_log, search).count()
                    if personal_query == "":
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_operation >="'
                            + str(period.yearp)
                            + '-01-01" and request_change_g_log.date_operation<"'
                            + str(end)
                            + '" and request_change_g_log.after_status != "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_operation >="'
                            + str(period.yearp)
                            + '-01-01" and request_change_g_log.date_operation<"'
                            + str(end)
                            + '" and request_change_g_log.after_status != "pending" and '
                            + personal_query
                        )
                    count_n_p = db.smart_query(db.request_change_g_log, search).count()
                else:
                    if personal_query == "":
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_request >="'
                            + str(period.yearp)
                            + '-06-01" and request_change_g_log.date_request<"'
                            + str(end)
                            + '" and request_change_g_log.after_status = "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_request >="'
                            + str(period.yearp)
                            + '-06-01" and request_change_g_log.date_request<"'
                            + str(end)
                            + '" and request_change_g_log.after_status = "pending" and '
                            + personal_query
                        )
                    count_p = db.smart_query(db.request_change_g_log, search).count()
                    if personal_query == "":
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_operation >="'
                            + str(period.yearp)
                            + '-06-01" and request_change_g_log.date_operation<"'
                            + str(end)
                            + '" and request_change_g_log.after_status != "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_operation >="'
                            + str(period.yearp)
                            + '-06-01" and request_change_g_log.date_operation<"'
                            + str(end)
                            + '" and request_change_g_log.after_status != "pending" and '
                            + personal_query
                        )
                    count_n_p = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_p - count_n_p)
            # INSERT MONTH
            info_level.append(infoe_level_temp)
    # PER PROJECT
    elif str(request.vars["level"]) == "3":
        if len(projects) == 0:
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(
                URL(
                    "management_reports",
                    "change_request_grades_management",
                    vars=dict(
                        level="2",
                        period=str(request.vars["period"]),
                        type_L=str(request.vars["type_U"]),
                        querySearch=personal_query,
                    ),
                )
            )

        for project_t in projects:
            project = db(db.project.name == project_t).select().first()
            if project is None:
                project = (
                    db(
                        (db.course_activity_log.before_course == project_t)
                        | (db.course_activity_log.after_course == project_t)
                    )
                    .select()
                    .first()
                )
                if project.before_course is not None:
                    project = project.before_course
                else:
                    project = project.after_course
            else:
                project = project.name
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # NAME OF MONTH
            infoe_level_temp.append(month[0])
            # ID OF PROJECT
            infoe_level_temp.append(project)
            # NAME OF PROJECT
            infoe_level_temp.append(project)
            # MADE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_request<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.after_status = "pending"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_request<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.after_status = "pending" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_i)
            # ACCEPTED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_operation<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.after_status = "accepted"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_operation<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.after_status = "accepted" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_i)
            # REJECTED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_operation<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.after_status = "rejected"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_operation<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.after_status = "rejected" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_i)
            ##CANCELED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "c"
            ):
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_operation<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.after_status = "canceled"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_operation<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.after_status = "canceled" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_i)
            # PENDING
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "p"
            ):
                if period.period == 1:
                    if personal_query == "":
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_request >="'
                            + str(period.yearp)
                            + '-01-01" and request_change_g_log.date_request<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.after_status = "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_request >="'
                            + str(period.yearp)
                            + '-01-01" and request_change_g_log.date_request<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.after_status = "pending" and '
                            + personal_query
                        )
                    count_p = db.smart_query(db.request_change_g_log, search).count()
                    if personal_query == "":
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_operation >="'
                            + str(period.yearp)
                            + '-01-01" and request_change_g_log.date_operation<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.after_status != "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_operation >="'
                            + str(period.yearp)
                            + '-01-01" and request_change_g_log.date_operation<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.after_status != "pending" and '
                            + personal_query
                        )
                    count_n_p = db.smart_query(db.request_change_g_log, search).count()
                else:
                    if personal_query == "":
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_request >="'
                            + str(period.yearp)
                            + '-06-01" and request_change_g_log.date_request<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.after_status = "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_request >="'
                            + str(period.yearp)
                            + '-06-01" and request_change_g_log.date_request<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.after_status = "pending" and '
                            + personal_query
                        )
                    count_p = db.smart_query(db.request_change_g_log, search).count()
                    if personal_query == "":
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_operation >="'
                            + str(period.yearp)
                            + '-06-01" and request_change_g_log.date_operation<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.after_status != "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_operation >="'
                            + str(period.yearp)
                            + '-06-01" and request_change_g_log.date_operation<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.after_status != "pending" and '
                            + personal_query
                        )
                    count_n_p = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_p - count_n_p)
            # INSERT PROJECT
            info_level.append(infoe_level_temp)
    # PER USER
    elif str(request.vars["level"]) == "4":
        # VERIFY THAT CAN SHOW THE LEVEL OF THE REPORT
        users_project = get_users(period, project, "Student", "request_change_g_log")
        if len(users_project) == 0:
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(
                URL(
                    "management_reports",
                    "change_request_grades_management",
                    vars=dict(
                        level="3",
                        period=str(request.vars["period"]),
                        month=str(request.vars["month"]),
                        type_L=str(request.vars["type_U"]),
                        type_U=str(request.vars["type_U"]),
                        querySearch=personal_query,
                    ),
                )
            )

        for user_p_t in users_project:
            user_p = db(db.auth_user.username == user_p_t).select().first()
            if user_p is None:
                user_p = (
                    db(db.request_change_g_log.user_request == user_p_t).select().first()
                )
                user_p = user_p.user_request
            else:
                user_p = user_p.username
            infoe_level_temp = []
            # NAME OF PERIOD
            infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
            # NAME OF MONTH
            infoe_level_temp.append(month[0])
            # NAME OF PROJECT
            infoe_level_temp.append(project)
            # ID OF USER
            infoe_level_temp.append(user_p)
            # NAME OF USER
            infoe_level_temp.append(user_p)
            # MADE
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "d"
            ):
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_request<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "pending"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_request<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "pending" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_i)
            # ACCEPTED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "i"
            ):
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_operation<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "accepted"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_operation<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "accepted" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_i)
            # REJECTED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "u"
            ):
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_operation<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "rejected"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_operation<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "rejected" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_i)
            ##CANCELED
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "c"
            ):
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_operation<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "canceled"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_operation >="'
                        + str(month[1])
                        + '" and request_change_g_log.date_operation<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "canceled" and '
                        + personal_query
                    )
                count_i = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_i)
            # PENDING
            if (
                str(request.vars["type_L"]) == "all"
                or str(request.vars["type_L"]) == "p"
            ):
                if period.period == 1:
                    if personal_query == "":
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_request >="'
                            + str(period.yearp)
                            + '-01-01" and request_change_g_log.date_request<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                            + str(user_p)
                            + '" and request_change_g_log.after_status = "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_request >="'
                            + str(period.yearp)
                            + '-01-01" and request_change_g_log.date_request<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                            + str(user_p)
                            + '" and request_change_g_log.after_status = "pending" and '
                            + personal_query
                        )
                    count_p = db.smart_query(db.request_change_g_log, search).count()
                    if personal_query == "":
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_operation >="'
                            + str(period.yearp)
                            + '-01-01" and request_change_g_log.date_operation<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                            + str(user_p)
                            + '" and request_change_g_log.after_status != "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_operation >="'
                            + str(period.yearp)
                            + '-01-01" and request_change_g_log.date_operation<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                            + str(user_p)
                            + '" and request_change_g_log.after_status != "pending" and '
                            + personal_query
                        )
                    count_n_p = db.smart_query(db.request_change_g_log, search).count()
                else:
                    if personal_query == "":
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_request >="'
                            + str(period.yearp)
                            + '-06-01" and request_change_g_log.date_request<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                            + str(user_p)
                            + '" and request_change_g_log.after_status = "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_request >="'
                            + str(period.yearp)
                            + '-06-01" and request_change_g_log.date_request<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                            + str(user_p)
                            + '" and request_change_g_log.after_status = "pending" and '
                            + personal_query
                        )
                    count_p = db.smart_query(db.request_change_g_log, search).count()
                    if personal_query == "":
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_operation >="'
                            + str(period.yearp)
                            + '-06-01" and request_change_g_log.date_operation<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                            + str(user_p)
                            + '" and request_change_g_log.after_status != "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.semester = "'
                            + T(period.period.name)
                            + '" and request_change_g_log.yearp = "'
                            + str(period.yearp)
                            + '" and request_change_g_log.date_operation >="'
                            + str(period.yearp)
                            + '-06-01" and request_change_g_log.date_operation<"'
                            + str(month[2])
                            + '" and request_change_g_log.project = "'
                            + str(project)
                            + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                            + str(user_p)
                            + '" and request_change_g_log.after_status != "pending" and '
                            + personal_query
                        )
                    count_n_p = db.smart_query(db.request_change_g_log, search).count()
                infoe_level_temp.append(count_p - count_n_p)
            # INSERT USER
            info_level.append(infoe_level_temp)
    # DATA
    elif str(request.vars["level"]) == "5":
        # MADE
        if str(request.vars["type_L"]) == "d":
            if personal_query == "":
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_request >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_request<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "pending"'
                )
            else:
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_request >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_request<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "pending" and '
                    + personal_query
                )
            for data in db.smart_query(db.request_change_g_log, search).select():
                grid.append(data.id)
        # ACCEPTED
        elif str(request.vars["type_L"]) == "i":
            if personal_query == "":
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_operation >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_operation<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "accepted"'
                )
            else:
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_operation >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_operation<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "accepted" and '
                    + personal_query
                )
            for data in db.smart_query(db.request_change_g_log, search).select():
                grid.append(data.id)
        # REJECTED
        elif str(request.vars["type_L"]) == "u":
            if personal_query == "":
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_operation >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_operation<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "rejected"'
                )
            else:
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_operation >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_operation<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "rejected" and '
                    + personal_query
                )
            for data in db.smart_query(db.request_change_g_log, search).select():
                grid.append(data.id)
        ##CANCELED
        elif str(request.vars["type_L"]) == "c":
            if personal_query == "":
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_operation >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_operation<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "canceled"'
                )
            else:
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_operation >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_operation<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "canceled" and '
                    + personal_query
                )
            for data in db.smart_query(db.request_change_g_log, search).select():
                grid.append(data.id)
        # PENDING
        elif str(request.vars["type_L"]) == "p":
            if period.period == 1:
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(period.yearp)
                        + '-01-01" and request_change_g_log.date_request<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "pending"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(period.yearp)
                        + '-01-01" and request_change_g_log.date_request<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "pending" and '
                        + personal_query
                    )
                for pending in db.smart_query(db.request_change_g_log, search).select():
                    if personal_query == "":
                        search = (
                            'request_change_g_log.r_c_g_id = "'
                            + str(pending.r_c_g_id)
                            + '" and request_change_g_log.after_status != "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.r_c_g_id = "'
                            + str(pending.r_c_g_id)
                            + '" and request_change_g_log.after_status != "pending" and '
                            + personal_query
                        )
                    if (
                        db.smart_query(db.request_change_g_log, search).select().first()
                        is None
                    ):
                        grid.append(pending.id)
            else:
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(period.yearp)
                        + '-06-01" and request_change_g_log.date_request<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "pending"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(period.yearp)
                        + '-06-01" and request_change_g_log.date_request<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "pending" and '
                        + personal_query
                    )
                for pending in db.smart_query(db.request_change_g_log, search).select():
                    if personal_query == "":
                        search = (
                            'request_change_g_log.r_c_g_id = "'
                            + str(pending.r_c_g_id)
                            + '" and request_change_g_log.after_status != "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.r_c_g_id = "'
                            + str(pending.r_c_g_id)
                            + '" and request_change_g_log.after_status != "pending" and '
                            + personal_query
                        )
                    if (
                        db.smart_query(db.request_change_g_log, search).select().first()
                        is None
                    ):
                        grid.append(pending.id)
        # ALL
        elif str(request.vars["type_L"]) == "all":
            # MADE AND PENDING
            if period.period == 1:
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(period.yearp)
                        + '-01-01" and request_change_g_log.date_request<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "pending"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(period.yearp)
                        + '-01-01" and request_change_g_log.date_request<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "pending" and '
                        + personal_query
                    )
                for pending in db.smart_query(db.request_change_g_log, search).select():
                    if personal_query == "":
                        search = (
                            'request_change_g_log.r_c_g_id = "'
                            + str(pending.r_c_g_id)
                            + '" and request_change_g_log.after_status != "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.r_c_g_id = "'
                            + str(pending.r_c_g_id)
                            + '" and request_change_g_log.after_status != "pending" and '
                            + personal_query
                        )
                    if (
                        db.smart_query(db.request_change_g_log, search).select().first()
                        is None
                    ):
                        grid.append(pending.id)
            else:
                if personal_query == "":
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(period.yearp)
                        + '-06-01" and request_change_g_log.date_request<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "pending"'
                    )
                else:
                    search = (
                        'request_change_g_log.semester = "'
                        + T(period.period.name)
                        + '" and request_change_g_log.yearp = "'
                        + str(period.yearp)
                        + '" and request_change_g_log.date_request >="'
                        + str(period.yearp)
                        + '-06-01" and request_change_g_log.date_request<"'
                        + str(month[2])
                        + '" and request_change_g_log.project = "'
                        + str(project)
                        + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                        + str(user_p)
                        + '" and request_change_g_log.after_status = "pending" and '
                        + personal_query
                    )
                for pending in db.smart_query(db.request_change_g_log, search).select():
                    if personal_query == "":
                        search = (
                            'request_change_g_log.r_c_g_id = "'
                            + str(pending.r_c_g_id)
                            + '" and request_change_g_log.after_status != "pending"'
                        )
                    else:
                        search = (
                            'request_change_g_log.r_c_g_id = "'
                            + str(pending.r_c_g_id)
                            + '" and request_change_g_log.after_status != "pending" and '
                            + personal_query
                        )
                    if (
                        db.smart_query(db.request_change_g_log, search).select().first()
                        is None
                    ):
                        grid.append(pending.id)
            # ACCEPTED
            if personal_query == "":
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_operation >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_operation<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "accepted"'
                )
            else:
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_operation >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_operation<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "accepted" and '
                    + personal_query
                )
            for data in db.smart_query(db.request_change_g_log, search).select():
                grid.append(data.id)
            # REJECTED
            if personal_query == "":
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_operation >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_operation<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "rejected"'
                )
            else:
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_operation >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_operation<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "rejected" and '
                    + personal_query
                )
            for data in db.smart_query(db.request_change_g_log, search).select():
                grid.append(data.id)
            ##CANCELED
            if personal_query == "":
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_operation >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_operation<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "canceled"'
                )
            else:
                search = (
                    'request_change_g_log.semester = "'
                    + T(period.period.name)
                    + '" and request_change_g_log.yearp = "'
                    + str(period.yearp)
                    + '" and request_change_g_log.date_operation >="'
                    + str(month[1])
                    + '" and request_change_g_log.date_operation<"'
                    + str(month[2])
                    + '" and request_change_g_log.project = "'
                    + str(project)
                    + '" and request_change_g_log.roll = "Student" and request_change_g_log.username = "'
                    + str(user_p)
                    + '" and request_change_g_log.after_status = "canceled" and '
                    + personal_query
                )
            for data in db.smart_query(db.request_change_g_log, search).select():
                grid.append(data.id)

        # TITLE
        infoe_level_temp = []
        infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
        infoe_level_temp.append(str(month[0]))
        infoe_level_temp.append(project)
        infoe_level_temp.append(T("Rol Student"))
        infoe_level_temp.append(str(user_p))
        info_level.append(infoe_level_temp)
        # REPORT
        if len(grid) == 0:
            grid.append(-1)
        db.request_change_g_log.id.readable = False
        db.request_change_g_log.id.writable = False
        db.request_change_g_log.username.readable = False
        db.request_change_g_log.username.writable = False
        db.request_change_g_log.roll.readable = False
        db.request_change_g_log.roll.writable = False
        db.request_change_g_log.semester.readable = False
        db.request_change_g_log.semester.writable = False
        db.request_change_g_log.yearp.readable = False
        db.request_change_g_log.yearp.writable = False
        db.request_change_g_log.project.readable = False
        db.request_change_g_log.project.writable = False
        db.request_change_g_log.r_c_g_id.readable = False
        db.request_change_g_log.r_c_g_id.writable = False
        links = [
            lambda row: A(
                T("Detail"),
                _role="button",
                _class="btn btn-info",
                _onclick='set_values("' + str(row.id) + '");',
                _title=T("View Detail"),
                **{"_data-toggle": "modal", "_data-target": "#detailModal"},
            )
        ]
        grid = SQLFORM.grid(
            db.request_change_g_log.id.belongs(grid),
            links=links,
            csv=False,
            create=False,
            editable=False,
            deletable=False,
            details=False,
            paginate=9,
            searchable=False,
        )
    return dict(
        fsearch=fsearch,
        filtered_by=filtered_by,
        personal_query=personal_query,
        infoLevel=info_level,
        grid=grid,
    )


# *************************************************************************************************************************************
# *************************************************************************************************************************************
# **************************************************MANAGEMENT REPORT PERFORMANCE OF STUDENTS******************************************
@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator")
    or auth.has_membership("Ecys-Administrator")
)
def performance_students_export():
    # ************************************************PARAMETERS AND VALIDATION***************************************
    info_level = []
    project = None
    period = None
    type_level = None
    control_p = None
    categories_level = []
    try:
        # CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars["level"] is not None and (
            int(request.vars["level"]) < 1 or int(request.vars["level"]) > 3
        ):
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))

        # CHECK THAT THE AREA EXIST
        area = db(db.area_level.name == "DTT Tutor Académico").select().first()
        if area is None:
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(URL("default", "home"))

        # CHECK IF THE PERIOD IS CHANGE
        if request.vars["period"] is None:

            cperiod = cpfecys.current_year_period()
            period = db(db.period_year.id == cperiod.id).select().first()
        else:
            period = validate_period(request.vars["period"])
            if period is None:
                session.flash = T("Not valid Action.")
                redirect(URL("default", "home"))

        # CHECK PARAMETERS
        if request.vars["level"] == "1" or request.vars["level"] is None:
            group_projects = db(
                (db.project.area_level == area.id)
                & (db.user_project.project == db.project.id)
                & (db.user_project.period == db.period_year.id)
                & (
                    (db.user_project.period <= period.id)
                    & ((db.user_project.period.cast('integer') + db.user_project.periods) > period.id)
                )
            ).select(db.project.ALL, orderby=db.project.name, distinct=True)
            if len(group_projects) == 0:
                session.flash = T(
                    "Report no visible: There are no parameters required to display the report."
                )
                redirect(URL("default", "home"))
        else:
            project = (
                db(
                    (db.project.id == request.vars["project"])
                    & (db.project.area_level == area.id)
                )
                .select()
                .first()
            )
            if project is None:
                session.flash = T("Not valid Action.")
                redirect(URL("default", "home"))

            if request.vars["level"] == "2":
                # CHECK IF THE TYPE OF REPORT IS VALID
                if (
                    str(request.vars["type_L"]) != "all"
                    and str(request.vars["type_L"]) != "i"
                    and str(request.vars["type_L"]) != "u"
                    and str(request.vars["type_L"]) != "d"
                ):
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))
            elif request.vars["level"] == "3":
                # CHECK IF THE TYPE OF THE LEVEL UP OF REPORT IS VALID
                if (
                    str(request.vars["type_U"]) != "all"
                    and str(request.vars["type_U"]) != "i"
                    and str(request.vars["type_U"]) != "u"
                    and str(request.vars["type_U"]) != "d"
                ):
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

                # CHECK IF THE TYPE OF REPORT IS VALID
                if (
                    str(request.vars["type_L"]) != "l_all"
                    and str(request.vars["type_L"]) != "l_i"
                    and str(request.vars["type_L"]) != "l_u"
                    and str(request.vars["type_L"]) != "l_d"
                    and str(request.vars["type_L"]) != "c_all"
                    and str(request.vars["type_L"]) != "c_i"
                    and str(request.vars["type_L"]) != "c_u"
                    and str(request.vars["type_L"]) != "c_d"
                ):
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))
    except:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    # *****************************************************REPORT*****************************************************
    # TITLE
    info_level = []
    infoe_level_temp = []
    infoe_level_temp.append("Universidad de San Carlos de Guatemala")
    info_level.append(infoe_level_temp)
    infoe_level_temp = []
    infoe_level_temp.append("Facultad de Ingeniería")
    info_level.append(infoe_level_temp)
    infoe_level_temp = []
    infoe_level_temp.append("Escuela de Ciencias y Sistemas")
    info_level.append(infoe_level_temp)
    # TYPE OF REPORT
    infoe_level_temp = []
    infoe_level_temp.append(T("Type"))
    infoe_level_temp.append(T("Performance of students"))
    info_level.append(infoe_level_temp)
    # DESCRIPTION OF REPORT
    infoe_level_temp = []
    infoe_level_temp.append(T("Description"))
    infoe_level_temp.append(T("Report on the performance of students in the courses."))
    info_level.append(infoe_level_temp)
    # PERIOD OF REPORT
    infoe_level_temp = []
    infoe_level_temp.append(T("Period"))
    infoe_level_temp.append(T(period.period.name) + " " + str(period.yearp))
    info_level.append(infoe_level_temp)
    # ALL SEMESTERS
    if request.vars["level"] == "1" or request.vars["level"] is None:
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # PERIOD OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Course"))
        infoe_level_temp.append(T("Students above average"))
        infoe_level_temp.append(T("Students on the average"))
        infoe_level_temp.append(T("Students Below Average"))
        info_level.append(infoe_level_temp)
        # CHECK FOR THE PARAMETERS
        control_p = (
            db(
                db.student_control_period.period_name
                == (T(period.period.name) + " " + str(period.yearp))
            )
            .select()
            .first()
        )
        if control_p is not None:
            # ALL PROJECTS
            for project in group_projects:
                infoe_level_temp = []
                # NAME OF PROJECT
                infoe_level_temp.append(project.name)
                # GRADES ABOVE AVERAGE
                infoe_level_temp.append(0)
                # GRADES ON THE AVERAGE
                infoe_level_temp.append(0)
                # GRADES BELOW AVERAGE
                infoe_level_temp.append(0)

                course_category = db(
                    (db.course_activity_category.semester == period.id)
                    & (db.course_activity_category.assignation == project.id)
                    & (db.course_activity_category.laboratory == False)
                ).select()
                if course_category.first() is not None:
                    categories_class = []
                    for categories in course_category:
                        if categories.category.category != "Laboratorio":
                            activity_class = []
                            total_a = 0
                            for activity in db(
                                db.course_activity.course_activity_category
                                == categories.id
                            ).select():
                                if (
                                    db(db.grades.activity == activity.id)
                                    .select()
                                    .first()
                                ):
                                    activity_class.append(activity)
                                total_a = total_a + 1
                            if len(activity_class) > 0:
                                categories_class.append(
                                    [categories, activity_class, total_a]
                                )
                        else:
                            categories_class.append([categories, 0])

                    categories_lab = []
                    for categories in db(
                        (db.course_activity_category.assignation == project.id)
                        & (db.course_activity_category.semester == period.id)
                        & (db.course_activity_category.laboratory == True)
                    ).select():
                        activity_class = []
                        total_a = 0
                        for activity in db(
                            db.course_activity.course_activity_category == categories.id
                        ).select():
                            if db(db.grades.activity == activity.id).select().first():
                                activity_class.append(activity)
                            total_a = total_a + 1
                        if len(activity_class) > 0:
                            categories_lab.append([categories, activity_class, total_a])

                    for student in db(
                        (db.academic_course_assignation.semester == period.id)
                        & (db.academic_course_assignation.assignation == project.id)
                    ).select():
                        total_carry = float(0)
                        total_final = float(0)
                        grade_laboratory = int(0)
                        for category_class in categories_class:
                            total_category = float(0)
                            if category_class[0].category.category == "Examen Final":
                                for c in category_class[1]:
                                    student_grade = (
                                        db(
                                            (db.grades.activity == c.id)
                                            & (
                                                db.grades.academic_assignation
                                                == student.id
                                            )
                                        )
                                        .select()
                                        .first()
                                    )
                                    if student_grade is not None:
                                        if category_class[0].specific_grade == True:
                                            total_final = total_final + float(
                                                (student_grade.grade * c.grade) / 100
                                            )
                                        else:
                                            total_final = total_final + float(
                                                student_grade.grade
                                            )

                                if category_class[0].specific_grade == False:
                                    total_activities = category_class[2] * 100
                                    total_final = float(
                                        (total_final * float(category_class[0].grade))
                                        / float(total_activities)
                                    )
                                total_final = int(round(total_final, 0))
                            elif category_class[0].category.category == "Laboratorio":
                                validate_laboratory = (
                                    db(
                                        (db.validate_laboratory.semester == period.id)
                                        & (db.validate_laboratory.project == project.id)
                                        & (db.validate_laboratory.carnet == student.id)
                                    )
                                    .select()
                                    .first()
                                )
                                if validate_laboratory is not None:
                                    grade_laboratory = float(
                                        (
                                            int(round(validate_laboratory.grade, 0))
                                            * category_class[0].grade
                                        )
                                        / 100
                                    )
                                else:
                                    total_carry_lab = float(0)
                                    if student.laboratorio == True:
                                        for category_lab in categories_lab:
                                            total_category_lab = float(0)
                                            for c_Lab in category_lab[1]:
                                                student_grade = (
                                                    db(
                                                        (db.grades.activity == c_Lab.id)
                                                        & (
                                                            db.grades.academic_assignation
                                                            == student.id
                                                        )
                                                    )
                                                    .select()
                                                    .first()
                                                )
                                                if student_grade is not None:
                                                    if (
                                                        category_lab[0].specific_grade
                                                        == True
                                                    ):
                                                        total_category_lab = (
                                                            total_category_lab
                                                            + float(
                                                                (
                                                                    student_grade.grade
                                                                    * c_Lab.grade
                                                                )
                                                                / 100
                                                            )
                                                        )
                                                    else:
                                                        total_category_lab = (
                                                            total_category_lab
                                                            + float(student_grade.grade)
                                                        )

                                            if category_lab[0].specific_grade == False:
                                                total_activities_lab = (
                                                    category_lab[2] * 100
                                                )
                                                total_category_lab = float(
                                                    (
                                                        total_category_lab
                                                        * float(category_lab[0].grade)
                                                    )
                                                    / float(total_activities_lab)
                                                )
                                            total_carry_lab = (
                                                total_carry_lab + total_category_lab
                                            )
                                    grade_laboratory = float(
                                        (
                                            int(round(total_carry_lab, 0))
                                            * category_class[0].grade
                                        )
                                        / 100
                                    )
                            else:
                                for c in category_class[1]:
                                    student_grade = (
                                        db(
                                            (db.grades.activity == c.id)
                                            & (
                                                db.grades.academic_assignation
                                                == student.id
                                            )
                                        )
                                        .select()
                                        .first()
                                    )
                                    if student_grade is not None:
                                        if category_class[0].specific_grade == True:
                                            total_category = total_category + float(
                                                (student_grade.grade * c.grade) / 100
                                            )
                                        else:
                                            total_category = total_category + float(
                                                student_grade.grade
                                            )

                                if category_class[0].specific_grade == False:
                                    total_activities = category_class[2] * 100
                                    total_category = float(
                                        (total_category * float(category_class[0].grade))
                                        / float(total_activities)
                                    )

                                total_carry = total_carry + total_category
                        total_carry = (
                            int(round(total_carry, 0))
                            + int(round(grade_laboratory, 0))
                            + total_final
                        )
                        total_carry = int(round(total_carry, 0))
                        if total_carry < int(control_p.min_average):
                            infoe_level_temp[3] = infoe_level_temp[3] + 1
                        elif total_carry >= int(
                            control_p.min_average
                        ) and total_carry <= int(control_p.max_average):
                            infoe_level_temp[2] = infoe_level_temp[2] + 1
                        else:
                            infoe_level_temp[1] = infoe_level_temp[1] + 1
                info_level.append(infoe_level_temp)
    # PROJECT
    elif request.vars["level"] == "2":
        # PROJECT OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Course"))
        infoe_level_temp.append(project.name)
        info_level.append(infoe_level_temp)
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # HEADER OF TABLE OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Type"))
        if (str(request.vars["type_L"]) == "all") or (
            str(request.vars["type_L"]) == "i"
        ):
            infoe_level_temp.append(T("Students above average"))
        if (str(request.vars["type_L"]) == "all") or (
            str(request.vars["type_L"]) == "u"
        ):
            infoe_level_temp.append(T("Students on the average"))
        if (str(request.vars["type_L"]) == "all") or (
            str(request.vars["type_L"]) == "d"
        ):
            infoe_level_temp.append(T("Students Below Average"))
        info_level.append(infoe_level_temp)
        # CHECK FOR THE PARAMETERS
        control_p = (
            db(
                db.student_control_period.period_name
                == (T(period.period.name) + " " + str(period.yearp))
            )
            .select()
            .first()
        )
        if control_p is not None:
            if str(request.vars["type_L"]) == "all":
                info_level.append(["Clase", 0, 0, 0])
                info_level.append(["Laboratorio", 0, 0, 0])
            else:
                info_level.append(["Clase", 0])
                info_level.append(["Laboratorio", 0])

            # LABORATORY
            categories_lab = []
            for categories in db(
                (db.course_activity_category.assignation == project.id)
                & (db.course_activity_category.semester == period.id)
                & (db.course_activity_category.laboratory == True)
            ).select():
                activity_class = []
                total_a = 0
                for activity in db(
                    db.course_activity.course_activity_category == categories.id
                ).select():
                    if db(db.grades.activity == activity.id).select().first():
                        activity_class.append(activity)
                    total_a = total_a + 1
                if len(activity_class) > 0:
                    categories_lab.append([categories, activity_class, total_a])

            # CLASS
            categories_class = []
            for categories in db(
                (db.course_activity_category.assignation == project.id)
                & (db.course_activity_category.semester == period.id)
                & (db.course_activity_category.laboratory == False)
            ).select():
                if categories.category.category != "Laboratorio":
                    activity_class = []
                    total_a = 0
                    for activity in db(
                        db.course_activity.course_activity_category == categories.id
                    ).select():
                        if db(db.grades.activity == activity.id).select().first():
                            activity_class.append(activity)
                        total_a = total_a + 1
                    if len(activity_class) > 0:
                        categories_class.append([categories, activity_class, total_a])
                else:
                    exist_laboratory = True
                    categories_class.append([categories, 0])

            # GRADE OF STUDENT
            for student in db(
                (db.academic_course_assignation.semester == period.id)
                & (db.academic_course_assignation.assignation == project.id)
            ).select():
                # GRADE OF LABORATORY
                grade_laboratory = int(0)
                validate_laboratory = (
                    db(
                        (db.validate_laboratory.semester == period.id)
                        & (db.validate_laboratory.project == project.id)
                        & (db.validate_laboratory.carnet == student.id)
                    )
                    .select()
                    .first()
                )
                if validate_laboratory is None:
                    if student.laboratorio == True:
                        if len(categories_lab) > 0:
                            total_carry_lab = float(0)
                            for category_lab in categories_lab:
                                total_category_lab = float(0)
                                for c_Lab in category_lab[1]:
                                    student_grade = (
                                        db(
                                            (db.grades.activity == c_Lab.id)
                                            & (
                                                db.grades.academic_assignation
                                                == student.id
                                            )
                                        )
                                        .select()
                                        .first()
                                    )
                                    if student_grade is not None:
                                        if category_lab[0].specific_grade == True:
                                            total_category_lab = (
                                                total_category_lab
                                                + float(
                                                    (student_grade.grade * c_Lab.grade)
                                                    / 100
                                                )
                                            )
                                        else:
                                            total_category_lab = (
                                                total_category_lab
                                                + float(student_grade.grade)
                                            )

                                if category_lab[0].specific_grade == False:
                                    total_activities_lab = category_lab[2] * 100
                                    total_category_lab = float(
                                        (
                                            total_category_lab
                                            * float(category_lab[0].grade)
                                        )
                                        / float(total_activities_lab)
                                    )
                                total_carry_lab = total_carry_lab + total_category_lab
                            grade_laboratory = int(round(total_carry_lab, 0))
                            if grade_laboratory < int(control_p.min_average):
                                if str(request.vars["type_L"]) == "all":
                                    info_level[11][3] = info_level[11][3] + 1
                                elif str(request.vars["type_L"]) == "d":
                                    info_level[11][1] = info_level[11][1] + 1
                            elif grade_laboratory >= int(
                                control_p.min_average
                            ) and grade_laboratory <= int(control_p.max_average):
                                if str(request.vars["type_L"]) == "all":
                                    info_level[11][2] = info_level[11][2] + 1
                                elif str(request.vars["type_L"]) == "u":
                                    info_level[11][1] = info_level[11][1] + 1
                            else:
                                if (
                                    str(request.vars["type_L"]) == "all"
                                    or str(request.vars["type_L"]) == "i"
                                ):
                                    info_level[11][1] = info_level[11][1] + 1
                else:
                    grade_laboratory = int(round(validate_laboratory.grade, 0))

                # GRADE OF CLASS
                total_carry = float(0)
                total_final = float(0)
                if len(categories_class) > 0:
                    for category_class in categories_class:
                        total_category = float(0)
                        if category_class[0].category.category == "Examen Final":
                            for c in category_class[1]:
                                student_grade = (
                                    db(
                                        (db.grades.activity == c.id)
                                        & (db.grades.academic_assignation == student.id)
                                    )
                                    .select()
                                    .first()
                                )
                                if student_grade is not None:
                                    if category_class[0].specific_grade == True:
                                        total_final = total_final + float(
                                            (student_grade.grade * c.grade) / 100
                                        )
                                    else:
                                        total_final = total_final + float(
                                            student_grade.grade
                                        )

                            if category_class[0].specific_grade == False:
                                total_activities = category_class[2] * 100
                                total_final = float(
                                    (total_final * float(category_class[0].grade))
                                    / float(total_activities)
                                )
                            total_final = int(round(total_final, 0))
                        elif category_class[0].category.category == "Laboratorio":
                            grade_laboratory = float(
                                (grade_laboratory * float(category_class[0].grade)) / 100
                            )
                        else:
                            for c in category_class[1]:
                                student_grade = (
                                    db(
                                        (db.grades.activity == c.id)
                                        & (db.grades.academic_assignation == student.id)
                                    )
                                    .select()
                                    .first()
                                )
                                if student_grade is not None:
                                    if category_class[0].specific_grade == True:
                                        total_category = total_category + float(
                                            (student_grade.grade * c.grade) / 100
                                        )
                                    else:
                                        total_category = total_category + float(
                                            student_grade.grade
                                        )

                            if category_class[0].specific_grade == False:
                                total_activities = category_class[2] * 100
                                total_category = float(
                                    (total_category * float(category_class[0].grade))
                                    / float(total_activities)
                                )
                            total_carry = total_carry + total_category
                    total_carry = (
                        int(round(total_carry, 0))
                        + int(round(grade_laboratory, 0))
                        + total_final
                    )
                    total_carry = int(round(total_carry, 0))
                    if total_carry < int(control_p.min_average):
                        if str(request.vars["type_L"]) == "all":
                            info_level[10][3] = info_level[10][3] + 1
                        elif str(request.vars["type_L"]) == "d":
                            info_level[10][1] = info_level[10][1] + 1
                    elif total_carry >= int(control_p.min_average) and total_carry <= int(
                        control_p.max_average
                    ):
                        if str(request.vars["type_L"]) == "all":
                            info_level[10][2] = info_level[10][2] + 1
                        elif str(request.vars["type_L"]) == "u":
                            info_level[10][1] = info_level[10][1] + 1
                    else:
                        if (
                            str(request.vars["type_L"]) == "all"
                            or str(request.vars["type_L"]) == "i"
                        ):
                            info_level[10][1] = info_level[10][1] + 1
    # TYPE
    elif request.vars["level"] == "3":
        type_level = str(request.vars["type_L"]).split("_")
        # PROJECT OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Course"))
        infoe_level_temp.append(project.name)
        info_level.append(infoe_level_temp)
        # TYPE OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Type"))
        if type_level[0] == "c":
            infoe_level_temp.append(T("Course"))
        else:
            infoe_level_temp.append(T("Laboratory"))
        info_level.append(infoe_level_temp)
        # MIDDLE LINE OF REPORT
        infoe_level_temp = []
        info_level.append(infoe_level_temp)
        # LABLE DETAIL OF REPORT
        infoe_level_temp = []
        infoe_level_temp.append(T("Detail"))
        info_level.append(infoe_level_temp)
        # CHECK FOR THE PARAMETERS
        control_p = (
            db(
                db.student_control_period.period_name
                == (T(period.period.name) + " " + str(period.yearp))
            )
            .select()
            .first()
        )
        if control_p is not None:
            # LABORATORY
            if type_level[0] == "l" or type_level[0] == "c":
                categories_lab = []
                for categories in db(
                    (db.course_activity_category.assignation == project.id)
                    & (db.course_activity_category.semester == period.id)
                    & (db.course_activity_category.laboratory == True)
                ).select():
                    activity_class = []
                    total_a = 0
                    for activity in db(
                        db.course_activity.course_activity_category == categories.id
                    ).select():
                        activity_class.append(activity)
                        total_a = total_a + 1
                    if total_a < 1:
                        total_a = 1
                    categories_lab.append([categories, activity_class, total_a])

            # CLASS
            if type_level[0] == "c":
                categories_class = []
                for categories in db(
                    (db.course_activity_category.assignation == project.id)
                    & (db.course_activity_category.semester == period.id)
                    & (db.course_activity_category.laboratory == False)
                ).select():
                    if categories.category.category != "Laboratorio":
                        activity_class = []
                        total_a = 0
                        for activity in db(
                            db.course_activity.course_activity_category == categories.id
                        ).select():
                            activity_class.append(activity)
                            total_a = total_a + 1
                        if total_a < 1:
                            total_a = 1
                        categories_class.append([categories, activity_class, total_a])
                    else:
                        categories_class.append([categories, 0])
                categories_level = categories_class
            else:
                categories_level = categories_lab

            infoe_level_temp = []
            infoe_level_temp.append(T("Rol Academic"))
            for category_h in categories_level:
                infoe_level_temp.append(str(category_h[0].category.category) + "\n100 pts")
            infoe_level_temp.append(T("Final Grade") + "\n100 pts")
            info_level.append(infoe_level_temp)

            # GRADE OF STUDENT
            for student in db(
                (db.academic.id == db.academic_course_assignation.carnet)
                & (db.academic_course_assignation.semester == period.id)
                & (db.academic_course_assignation.assignation == project.id)
            ).select(db.academic_course_assignation.ALL, orderby=db.academic.carnet):
                student_temp = []
                grade_laboratory = int(0)
                total_carry = float(0)
                total_final = float(0)
                student_temp.append(student.carnet.carnet)

                # GRADE OF LABORATORY
                validate_laboratory = (
                    db(
                        (db.validate_laboratory.semester == period.id)
                        & (db.validate_laboratory.project == project.id)
                        & (db.validate_laboratory.carnet == student.id)
                    )
                    .select()
                    .first()
                )
                if validate_laboratory is None:
                    if student.laboratorio == True:
                        if len(categories_lab) > 0:
                            total_carry_lab = float(0)
                            for category_lab in categories_lab:
                                total_category_lab = float(0)
                                for c_Lab in category_lab[1]:
                                    student_grade = (
                                        db(
                                            (db.grades.activity == c_Lab.id)
                                            & (
                                                db.grades.academic_assignation
                                                == student.id
                                            )
                                        )
                                        .select()
                                        .first()
                                    )
                                    if student_grade is not None:
                                        if category_lab[0].specific_grade == True:
                                            total_category_lab = (
                                                total_category_lab
                                                + float(
                                                    (student_grade.grade * c_Lab.grade)
                                                    / 100
                                                )
                                            )
                                        else:
                                            total_category_lab = (
                                                total_category_lab
                                                + float(student_grade.grade)
                                            )

                                if category_lab[0].specific_grade == False:
                                    total_activities_lab = category_lab[2] * 100
                                    total_category_lab = float(
                                        (
                                            total_category_lab
                                            * float(category_lab[0].grade)
                                        )
                                        / float(total_activities_lab)
                                    )
                                total_carry_lab = total_carry_lab + total_category_lab
                                if type_level[0] == "l":
                                    check_grade = float(
                                        (total_category_lab * float(100))
                                        / float(category_lab[0].grade)
                                    )
                                    student_temp.append(check_grade)
                            grade_laboratory = int(round(total_carry_lab, 0))
                            if type_level[0] == "l":
                                student_temp.append(grade_laboratory)
                                if grade_laboratory < int(control_p.min_average):
                                    if (
                                        str(type_level[1]) == "all"
                                        or str(type_level[1]) == "d"
                                    ):
                                        info_level.append(student_temp)
                                elif grade_laboratory >= int(
                                    control_p.min_average
                                ) and grade_laboratory <= int(control_p.max_average):
                                    if (
                                        str(type_level[1]) == "all"
                                        or str(type_level[1]) == "u"
                                    ):
                                        info_level.append(student_temp)
                                else:
                                    if (
                                        str(type_level[1]) == "all"
                                        or str(type_level[1]) == "i"
                                    ):
                                        info_level.append(student_temp)
                else:
                    grade_laboratory = int(round(validate_laboratory.grade, 0))

                # GRADE OF CLASS
                if type_level[0] == "c":
                    if len(categories_class) > 0:
                        for category_class in categories_class:
                            total_category = float(0)
                            if category_class[0].category.category == "Examen Final":
                                for c in category_class[1]:
                                    student_grade = (
                                        db(
                                            (db.grades.activity == c.id)
                                            & (
                                                db.grades.academic_assignation
                                                == student.id
                                            )
                                        )
                                        .select()
                                        .first()
                                    )
                                    if student_grade is not None:
                                        if category_class[0].specific_grade == True:
                                            total_final = total_final + float(
                                                (student_grade.grade * c.grade) / 100
                                            )
                                        else:
                                            total_final = total_final + float(
                                                student_grade.grade
                                            )

                                if category_class[0].specific_grade == False:
                                    total_activities = category_class[2] * 100
                                    total_final = float(
                                        (total_final * float(category_class[0].grade))
                                        / float(total_activities)
                                    )
                                total_final = int(round(total_final, 0))
                                check_grade = float(
                                    (total_final * float(100))
                                    / float(category_class[0].grade)
                                )
                                student_temp.append(check_grade)
                            elif category_class[0].category.category == "Laboratorio":
                                student_temp.append(grade_laboratory)
                                grade_laboratory = float(
                                    (grade_laboratory * float(category_class[0].grade))
                                    / 100
                                )
                            else:
                                for c in category_class[1]:
                                    student_grade = (
                                        db(
                                            (db.grades.activity == c.id)
                                            & (
                                                db.grades.academic_assignation
                                                == student.id
                                            )
                                        )
                                        .select()
                                        .first()
                                    )
                                    if student_grade is not None:
                                        if category_class[0].specific_grade == True:
                                            total_category = total_category + float(
                                                (student_grade.grade * c.grade) / 100
                                            )
                                        else:
                                            total_category = total_category + float(
                                                student_grade.grade
                                            )

                                if category_class[0].specific_grade == False:
                                    total_activities = category_class[2] * 100
                                    total_category = float(
                                        (total_category * float(category_class[0].grade))
                                        / float(total_activities)
                                    )
                                total_carry = total_carry + total_category
                                check_grade = float(
                                    (total_category * float(100))
                                    / float(category_class[0].grade)
                                )
                                student_temp.append(check_grade)
                        total_carry = (
                            int(round(total_carry, 0))
                            + int(round(grade_laboratory, 0))
                            + total_final
                        )
                        total_carry = int(round(total_carry, 0))
                        student_temp.append(total_carry)
                        if total_carry < int(control_p.min_average):
                            if str(type_level[1]) == "all" or str(type_level[1]) == "d":
                                info_level.append(student_temp)
                        elif total_carry >= int(
                            control_p.min_average
                        ) and total_carry <= int(control_p.max_average):
                            if str(type_level[1]) == "all" or str(type_level[1]) == "u":
                                info_level.append(student_temp)
                        else:
                            if str(type_level[1]) == "all" or str(type_level[1]) == "i":
                                info_level.append(student_temp)
    return dict(filename="ReporteDesempeno", csvdata=info_level)


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator")
    or auth.has_membership("Ecys-Administrator")
)
def performance_students():
    # ************************************************PARAMETERS AND VALIDATION***************************************
    info_level = []
    exist_laboratory = False
    group_periods = None
    project = None
    period = None
    type_level = None
    control_p = None
    categories_level = []
    try:
        # CHECK THAT THE LEVEL OF REPORT IS VALID
        if request.vars["level"] is not None and (
            int(request.vars["level"]) < 1 or int(request.vars["level"]) > 3
        ):
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))

        # CHECK THAT THE AREA EXIST
        area = db(db.area_level.name == "DTT Tutor Académico").select().first()
        if area is None:
            session.flash = T(
                "Report no visible: There are no parameters required to display the report."
            )
            redirect(URL("default", "home"))

        # CHECK IF THE PERIOD IS CHANGE
        if request.vars["period"] is None:

            cperiod = cpfecys.current_year_period()
            period = db(db.period_year.id == cperiod.id).select().first()
        else:
            period = validate_period(request.vars["period"])
            if period is None:
                session.flash = T("Not valid Action.")
                redirect(URL("default", "home"))

        # CHECK PARAMETERS
        if request.vars["level"] == "1" or request.vars["level"] is None:
            group_periods = db(db.period_year).select(orderby=~db.period_year.id)
            if len(group_periods) == 0:
                session.flash = T(
                    "Report no visible: There are no parameters\
                 required to display the report."
                )
                redirect(URL("default", "home"))

            group_projects = db(
                (db.project.area_level == area.id)
                & (db.user_project.project == db.project.id)
                & (db.user_project.period == db.period_year.id)
                & (
                    (db.user_project.period <= period.id)
                    & ((db.user_project.period.cast('integer') + db.user_project.periods) > period.id)
                )
            ).select(db.project.ALL, orderby=db.project.name, distinct=True)

            if len(group_projects) == 0:
                # TODO corregir este error 403
                session.flash = T(
                    "Report no visible: There are no parameters\
                 required to display the report."
                )
                redirect(URL("default", "home"))

        else:
            project = (
                db(
                    (db.project.id == request.vars["project"])
                    & (db.project.area_level == area.id)
                )
                .select()
                .first()
            )
            if project is None:
                session.flash = T("Not valid Action.")
                redirect(URL("default", "home"))

            if request.vars["level"] == "2":
                # CHECK IF THE TYPE OF REPORT IS VALID
                if (
                    str(request.vars["type_L"]) != "all"
                    and str(request.vars["type_L"]) != "i"
                    and str(request.vars["type_L"]) != "u"
                    and str(request.vars["type_L"]) != "d"
                ):
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))
            elif request.vars["level"] == "3":
                # CHECK IF THE TYPE OF THE LEVEL UP OF REPORT IS VALID
                if (
                    str(request.vars["type_U"]) != "all"
                    and str(request.vars["type_U"]) != "i"
                    and str(request.vars["type_U"]) != "u"
                    and str(request.vars["type_U"]) != "d"
                ):
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

                # CHECK IF THE TYPE OF REPORT IS VALID
                if (
                    str(request.vars["type_L"]) != "l_all"
                    and str(request.vars["type_L"]) != "l_i"
                    and str(request.vars["type_L"]) != "l_u"
                    and str(request.vars["type_L"]) != "l_d"
                    and str(request.vars["type_L"]) != "c_all"
                    and str(request.vars["type_L"]) != "c_i"
                    and str(request.vars["type_L"]) != "c_u"
                    and str(request.vars["type_L"]) != "c_d"
                ):
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))

    except:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    # *****************************************************REPORT*****************************************************
    # ALL SEMESTERS
    if request.vars["level"] == "1" or request.vars["level"] is None:
        # CHECK FOR THE PARAMETERS
        control_p = (
            db(
                db.student_control_period.period_name
                == (T(period.period.name) + " " + str(period.yearp))
            )
            .select()
            .first()
        )
        if control_p is not None:
            # ALL PROJECTS
            for project in group_projects:
                infoe_level_temp = []
                # ID OF PROJECT
                infoe_level_temp.append(project.id)
                # NAME OF PROJECT
                infoe_level_temp.append(project.name)
                # GRADES ABOVE AVERAGE
                infoe_level_temp.append(0)
                # GRADES ON THE AVERAGE
                infoe_level_temp.append(0)
                # GRADES BELOW AVERAGE
                infoe_level_temp.append(0)

                course_category = db(
                    (db.course_activity_category.semester == period.id)
                    & (db.course_activity_category.assignation == project.id)
                    & (db.course_activity_category.laboratory == False)
                ).select()
                if course_category.first() is not None:
                    categories_class = []
                    for categories in course_category:
                        if categories.category.category != "Laboratorio":
                            activity_class = []
                            total_a = 0
                            for activity in db(
                                db.course_activity.course_activity_category
                                == categories.id
                            ).select():
                                if (
                                    db(db.grades.activity == activity.id)
                                    .select()
                                    .first()
                                ):
                                    activity_class.append(activity)
                                total_a = total_a + 1
                            if len(activity_class) > 0:
                                categories_class.append(
                                    [categories, activity_class, total_a]
                                )
                        else:
                            categories_class.append([categories, 0])

                    categories_lab = []
                    for categories in db(
                        (db.course_activity_category.assignation == project.id)
                        & (db.course_activity_category.semester == period.id)
                        & (db.course_activity_category.laboratory == True)
                    ).select():
                        activity_class = []
                        total_a = 0
                        for activity in db(
                            db.course_activity.course_activity_category == categories.id
                        ).select():
                            if db(db.grades.activity == activity.id).select().first():
                                activity_class.append(activity)
                            total_a = total_a + 1
                        if len(activity_class) > 0:
                            categories_lab.append([categories, activity_class, total_a])

                    for student in db(
                        (db.academic_course_assignation.semester == period.id)
                        & (db.academic_course_assignation.assignation == project.id)
                    ).select():
                        total_carry = float(0)
                        total_final = float(0)
                        grade_laboratory = int(0)
                        for category_class in categories_class:
                            total_category = float(0)
                            if category_class[0].category.category == "Examen Final":
                                for c in category_class[1]:
                                    student_grade = (
                                        db(
                                            (db.grades.activity == c.id)
                                            & (
                                                db.grades.academic_assignation
                                                == student.id
                                            )
                                        )
                                        .select()
                                        .first()
                                    )
                                    if student_grade is not None:
                                        if category_class[0].specific_grade == True:
                                            total_final = total_final + float(
                                                (student_grade.grade * c.grade) / 100
                                            )
                                        else:
                                            total_final = total_final + float(
                                                student_grade.grade
                                            )

                                if category_class[0].specific_grade == False:
                                    total_activities = category_class[2] * 100
                                    total_final = float(
                                        (total_final * float(category_class[0].grade))
                                        / float(total_activities)
                                    )
                                total_final = int(round(total_final, 0))
                            elif category_class[0].category.category == "Laboratorio":
                                validate_laboratory = (
                                    db(
                                        (db.validate_laboratory.semester == period.id)
                                        & (db.validate_laboratory.project == project.id)
                                        & (db.validate_laboratory.carnet == student.id)
                                    )
                                    .select()
                                    .first()
                                )
                                if validate_laboratory is not None:
                                    grade_laboratory = float(
                                        (
                                            int(round(validate_laboratory.grade, 0))
                                            * category_class[0].grade
                                        )
                                        / 100
                                    )
                                else:
                                    total_carry_lab = float(0)
                                    if student.laboratorio == True:
                                        for category_lab in categories_lab:
                                            total_category_lab = float(0)
                                            for c_Lab in category_lab[1]:
                                                student_grade = (
                                                    db(
                                                        (db.grades.activity == c_Lab.id)
                                                        & (
                                                            db.grades.academic_assignation
                                                            == student.id
                                                        )
                                                    )
                                                    .select()
                                                    .first()
                                                )
                                                if student_grade is not None:
                                                    if (
                                                        category_lab[0].specific_grade
                                                        == True
                                                    ):
                                                        total_category_lab = (
                                                            total_category_lab
                                                            + float(
                                                                (
                                                                    student_grade.grade
                                                                    * c_Lab.grade
                                                                )
                                                                / 100
                                                            )
                                                        )
                                                    else:
                                                        total_category_lab = (
                                                            total_category_lab
                                                            + float(student_grade.grade)
                                                        )

                                            if category_lab[0].specific_grade == False:
                                                total_activities_lab = (
                                                    category_lab[2] * 100
                                                )
                                                total_category_lab = float(
                                                    (
                                                        total_category_lab
                                                        * float(category_lab[0].grade)
                                                    )
                                                    / float(total_activities_lab)
                                                )
                                            total_carry_lab = (
                                                total_carry_lab + total_category_lab
                                            )
                                    grade_laboratory = float(
                                        (
                                            int(round(total_carry_lab, 0))
                                            * category_class[0].grade
                                        )
                                        / 100
                                    )
                            else:
                                for c in category_class[1]:
                                    student_grade = (
                                        db(
                                            (db.grades.activity == c.id)
                                            & (
                                                db.grades.academic_assignation
                                                == student.id
                                            )
                                        )
                                        .select()
                                        .first()
                                    )
                                    if student_grade is not None:
                                        if category_class[0].specific_grade == True:
                                            total_category = total_category + float(
                                                (student_grade.grade * c.grade) / 100
                                            )
                                        else:
                                            total_category = total_category + float(
                                                student_grade.grade
                                            )

                                if category_class[0].specific_grade == False:
                                    total_activities = category_class[2] * 100
                                    total_category = float(
                                        (total_category * float(category_class[0].grade))
                                        / float(total_activities)
                                    )

                                total_carry = total_carry + total_category
                        total_carry = (
                            int(round(total_carry, 0))
                            + int(round(grade_laboratory, 0))
                            + total_final
                        )
                        total_carry = int(round(total_carry, 0))
                        if total_carry < int(control_p.min_average):
                            infoe_level_temp[4] = infoe_level_temp[4] + 1
                        elif total_carry >= int(
                            control_p.min_average
                        ) and total_carry <= int(control_p.max_average):
                            infoe_level_temp[3] = infoe_level_temp[3] + 1
                        else:
                            infoe_level_temp[2] = infoe_level_temp[2] + 1
                info_level.append(infoe_level_temp)
    # PROJECT
    elif request.vars["level"] == "2":
        # CHECK FOR THE PARAMETERS
        control_p = (
            db(
                db.student_control_period.period_name
                == (T(period.period.name) + " " + str(period.yearp))
            )
            .select()
            .first()
        )
        if control_p is not None:
            if str(request.vars["type_L"]) == "all":
                info_level.append(["c", "Clase", 0, 0, 0])
                info_level.append(["l", "Laboratorio", 0, 0, 0])
            else:
                info_level.append(["c", "Clase", 0])
                info_level.append(["l", "Laboratorio", 0])

            # LABORATORY
            categories_lab = []
            for categories in db(
                (db.course_activity_category.assignation == project.id)
                & (db.course_activity_category.semester == period.id)
                & (db.course_activity_category.laboratory == True)
            ).select():
                activity_class = []
                total_a = 0
                for activity in db(
                    db.course_activity.course_activity_category == categories.id
                ).select():
                    if db(db.grades.activity == activity.id).select().first():
                        activity_class.append(activity)
                    total_a = total_a + 1
                if len(activity_class) > 0:
                    categories_lab.append([categories, activity_class, total_a])

            # CLASS
            categories_class = []
            for categories in db(
                (db.course_activity_category.assignation == project.id)
                & (db.course_activity_category.semester == period.id)
                & (db.course_activity_category.laboratory == False)
            ).select():
                if categories.category.category != "Laboratorio":
                    activity_class = []
                    total_a = 0
                    for activity in db(
                        db.course_activity.course_activity_category == categories.id
                    ).select():
                        if db(db.grades.activity == activity.id).select().first():
                            activity_class.append(activity)
                        total_a = total_a + 1
                    if len(activity_class) > 0:
                        categories_class.append([categories, activity_class, total_a])
                else:
                    exist_laboratory = True
                    categories_class.append([categories, 0])

            # GRADE OF STUDENT
            for student in db(
                (db.academic_course_assignation.semester == period.id)
                & (db.academic_course_assignation.assignation == project.id)
            ).select():
                # GRADE OF LABORATORY
                grade_laboratory = int(0)
                validate_laboratory = (
                    db(
                        (db.validate_laboratory.semester == period.id)
                        & (db.validate_laboratory.project == project.id)
                        & (db.validate_laboratory.carnet == student.id)
                    )
                    .select()
                    .first()
                )
                if validate_laboratory is None:
                    if student.laboratorio == True:
                        if len(categories_lab) > 0:
                            total_carry_lab = float(0)
                            for category_lab in categories_lab:
                                total_category_lab = float(0)
                                for c_Lab in category_lab[1]:
                                    student_grade = (
                                        db(
                                            (db.grades.activity == c_Lab.id)
                                            & (
                                                db.grades.academic_assignation
                                                == student.id
                                            )
                                        )
                                        .select()
                                        .first()
                                    )
                                    if student_grade is not None:
                                        if category_lab[0].specific_grade == True:
                                            total_category_lab = (
                                                total_category_lab
                                                + float(
                                                    (student_grade.grade * c_Lab.grade)
                                                    / 100
                                                )
                                            )
                                        else:
                                            total_category_lab = (
                                                total_category_lab
                                                + float(student_grade.grade)
                                            )

                                if category_lab[0].specific_grade == False:
                                    total_activities_lab = category_lab[2] * 100
                                    total_category_lab = float(
                                        (
                                            total_category_lab
                                            * float(category_lab[0].grade)
                                        )
                                        / float(total_activities_lab)
                                    )
                                total_carry_lab = total_carry_lab + total_category_lab
                            grade_laboratory = int(round(total_carry_lab, 0))
                            if grade_laboratory < int(control_p.min_average):
                                if str(request.vars["type_L"]) == "all":
                                    info_level[1][4] = info_level[1][4] + 1
                                elif str(request.vars["type_L"]) == "d":
                                    info_level[1][2] = info_level[1][2] + 1
                            elif grade_laboratory >= int(
                                control_p.min_average
                            ) and grade_laboratory <= int(control_p.max_average):
                                if str(request.vars["type_L"]) == "all":
                                    info_level[1][3] = info_level[1][3] + 1
                                elif str(request.vars["type_L"]) == "u":
                                    info_level[1][2] = info_level[1][2] + 1
                            else:
                                if (
                                    str(request.vars["type_L"]) == "all"
                                    or str(request.vars["type_L"]) == "i"
                                ):
                                    info_level[1][2] = info_level[1][2] + 1
                else:
                    grade_laboratory = int(round(validate_laboratory.grade, 0))

                # GRADE OF CLASS
                total_carry = float(0)
                total_final = float(0)
                if len(categories_class) > 0:
                    for category_class in categories_class:
                        total_category = float(0)
                        if category_class[0].category.category == "Examen Final":
                            for c in category_class[1]:
                                student_grade = (
                                    db(
                                        (db.grades.activity == c.id)
                                        & (db.grades.academic_assignation == student.id)
                                    )
                                    .select()
                                    .first()
                                )
                                if student_grade is not None:
                                    if category_class[0].specific_grade == True:
                                        total_final = total_final + float(
                                            (student_grade.grade * c.grade) / 100
                                        )
                                    else:
                                        total_final = total_final + float(
                                            student_grade.grade
                                        )

                            if category_class[0].specific_grade == False:
                                total_activities = category_class[2] * 100
                                total_final = float(
                                    (total_final * float(category_class[0].grade))
                                    / float(total_activities)
                                )
                            total_final = int(round(total_final, 0))
                        elif category_class[0].category.category == "Laboratorio":
                            grade_laboratory = float(
                                (grade_laboratory * float(category_class[0].grade)) / 100
                            )
                        else:
                            for c in category_class[1]:
                                student_grade = (
                                    db(
                                        (db.grades.activity == c.id)
                                        & (db.grades.academic_assignation == student.id)
                                    )
                                    .select()
                                    .first()
                                )
                                if student_grade is not None:
                                    if category_class[0].specific_grade == True:
                                        total_category = total_category + float(
                                            (student_grade.grade * c.grade) / 100
                                        )
                                    else:
                                        total_category = total_category + float(
                                            student_grade.grade
                                        )

                            if category_class[0].specific_grade == False:
                                total_activities = category_class[2] * 100
                                total_category = float(
                                    (total_category * float(category_class[0].grade))
                                    / float(total_activities)
                                )
                            total_carry = total_carry + total_category
                    total_carry = (
                        int(round(total_carry, 0))
                        + int(round(grade_laboratory, 0))
                        + total_final
                    )
                    total_carry = int(round(total_carry, 0))
                    if total_carry < int(control_p.min_average):
                        if str(request.vars["type_L"]) == "all":
                            info_level[0][4] = info_level[0][4] + 1
                        elif str(request.vars["type_L"]) == "d":
                            info_level[0][2] = info_level[0][2] + 1
                    elif total_carry >= int(control_p.min_average) and total_carry <= int(
                        control_p.max_average
                    ):
                        if str(request.vars["type_L"]) == "all":
                            info_level[0][3] = info_level[0][3] + 1
                        elif str(request.vars["type_L"]) == "u":
                            info_level[0][2] = info_level[0][2] + 1
                    else:
                        if (
                            str(request.vars["type_L"]) == "all"
                            or str(request.vars["type_L"]) == "i"
                        ):
                            info_level[0][2] = info_level[0][2] + 1
    # TYPE FOR PROJECT
    elif request.vars["level"] == "3":
        # CHECK FOR THE PARAMETERS
        control_p = (
            db(
                db.student_control_period.period_name
                == (T(period.period.name) + " " + str(period.yearp))
            )
            .select()
            .first()
        )
        if control_p is not None:
            type_level = str(request.vars["type_L"]).split("_")
            # LABORATORY
            if type_level[0] == "l" or type_level[0] == "c":
                categories_lab = []
                for categories in db(
                    (db.course_activity_category.assignation == project.id)
                    & (db.course_activity_category.semester == period.id)
                    & (db.course_activity_category.laboratory == True)
                ).select():
                    activity_class = []
                    total_a = 0
                    for activity in db(
                        db.course_activity.course_activity_category == categories.id
                    ).select():
                        activity_class.append(activity)
                        total_a = total_a + 1
                    if total_a < 1:
                        total_a = 1
                    categories_lab.append([categories, activity_class, total_a])

            # CLASS
            if type_level[0] == "c":
                categories_class = []
                for categories in db(
                    (db.course_activity_category.assignation == project.id)
                    & (db.course_activity_category.semester == period.id)
                    & (db.course_activity_category.laboratory == False)
                ).select():
                    if categories.category.category != "Laboratorio":
                        activity_class = []
                        total_a = 0
                        for activity in db(
                            db.course_activity.course_activity_category == categories.id
                        ).select():
                            activity_class.append(activity)
                            total_a = total_a + 1
                        if total_a < 1:
                            total_a = 1
                        categories_class.append([categories, activity_class, total_a])
                    else:
                        categories_class.append([categories, 0])
                categories_level = categories_class
            else:
                categories_level = categories_lab

            # GRADE OF STUDENT
            for student in db(
                (db.academic.id == db.academic_course_assignation.carnet)
                & (db.academic_course_assignation.semester == period.id)
                & (db.academic_course_assignation.assignation == project.id)
            ).select(db.academic_course_assignation.ALL, orderby=db.academic.carnet):
                student_Temp = []
                grade_laboratory = int(0)
                total_carry = float(0)
                total_final = float(0)
                student_Temp.append(student.carnet.carnet)

                # GRADE OF LABORATORY
                validate_laboratory = (
                    db(
                        (db.validate_laboratory.semester == period.id)
                        & (db.validate_laboratory.project == project.id)
                        & (db.validate_laboratory.carnet == student.id)
                    )
                    .select()
                    .first()
                )
                if validate_laboratory is None:
                    if student.laboratorio == True:
                        if len(categories_lab) > 0:
                            total_carry_lab = float(0)
                            for category_lab in categories_lab:
                                total_category_lab = float(0)
                                for c_Lab in category_lab[1]:
                                    student_grade = (
                                        db(
                                            (db.grades.activity == c_Lab.id)
                                            & (
                                                db.grades.academic_assignation
                                                == student.id
                                            )
                                        )
                                        .select()
                                        .first()
                                    )
                                    if student_grade is not None:
                                        if category_lab[0].specific_grade == True:
                                            total_category_lab = (
                                                total_category_lab
                                                + float(
                                                    (student_grade.grade * c_Lab.grade)
                                                    / 100
                                                )
                                            )
                                        else:
                                            total_category_lab = (
                                                total_category_lab
                                                + float(student_grade.grade)
                                            )

                                if category_lab[0].specific_grade == False:
                                    total_activities_lab = category_lab[2] * 100
                                    total_category_lab = float(
                                        (
                                            total_category_lab
                                            * float(category_lab[0].grade)
                                        )
                                        / float(total_activities_lab)
                                    )
                                total_carry_lab = total_carry_lab + total_category_lab
                                if type_level[0] == "l":
                                    check_grade = float(
                                        (total_category_lab * float(100))
                                        / float(category_lab[0].grade)
                                    )
                                    student_Temp.append(check_grade)
                            grade_laboratory = int(round(total_carry_lab, 0))
                            if type_level[0] == "l":
                                student_Temp.append(grade_laboratory)
                                if grade_laboratory < int(control_p.min_average):
                                    if (
                                        str(type_level[1]) == "all"
                                        or str(type_level[1]) == "d"
                                    ):
                                        info_level.append(student_Temp)
                                elif grade_laboratory >= int(
                                    control_p.min_average
                                ) and grade_laboratory <= int(control_p.max_average):
                                    if (
                                        str(type_level[1]) == "all"
                                        or str(type_level[1]) == "u"
                                    ):
                                        info_level.append(student_Temp)
                                else:
                                    if (
                                        str(type_level[1]) == "all"
                                        or str(type_level[1]) == "i"
                                    ):
                                        info_level.append(student_Temp)
                else:
                    grade_laboratory = int(round(validate_laboratory.grade, 0))

                # GRADE OF CLASS
                if type_level[0] == "c":
                    if len(categories_class) > 0:
                        for category_class in categories_class:
                            total_category = float(0)
                            if category_class[0].category.category == "Examen Final":
                                for c in category_class[1]:
                                    student_grade = (
                                        db(
                                            (db.grades.activity == c.id)
                                            & (
                                                db.grades.academic_assignation
                                                == student.id
                                            )
                                        )
                                        .select()
                                        .first()
                                    )
                                    if student_grade is not None:
                                        if category_class[0].specific_grade == True:
                                            total_final = total_final + float(
                                                (student_grade.grade * c.grade) / 100
                                            )
                                        else:
                                            total_final = total_final + float(
                                                student_grade.grade
                                            )

                                if category_class[0].specific_grade == False:
                                    total_activities = category_class[2] * 100
                                    total_final = float(
                                        (total_final * float(category_class[0].grade))
                                        / float(total_activities)
                                    )
                                total_final = int(round(total_final, 0))
                                check_grade = float(
                                    (total_final * float(100))
                                    / float(category_class[0].grade)
                                )
                                student_Temp.append(check_grade)
                            elif category_class[0].category.category == "Laboratorio":
                                student_Temp.append(grade_laboratory)
                                grade_laboratory = float(
                                    (grade_laboratory * float(category_class[0].grade))
                                    / 100
                                )
                            else:
                                for c in category_class[1]:
                                    student_grade = (
                                        db(
                                            (db.grades.activity == c.id)
                                            & (
                                                db.grades.academic_assignation
                                                == student.id
                                            )
                                        )
                                        .select()
                                        .first()
                                    )
                                    if student_grade is not None:
                                        if category_class[0].specific_grade == True:
                                            total_category = total_category + float(
                                                (student_grade.grade * c.grade) / 100
                                            )
                                        else:
                                            total_category = total_category + float(
                                                student_grade.grade
                                            )

                                if category_class[0].specific_grade == False:
                                    total_activities = category_class[2] * 100
                                    total_category = float(
                                        (total_category * float(category_class[0].grade))
                                        / float(total_activities)
                                    )
                                total_carry = total_carry + total_category
                                check_grade = float(
                                    (total_category * float(100))
                                    / float(category_class[0].grade)
                                )
                                student_Temp.append(check_grade)
                        total_carry = (
                            int(round(total_carry, 0))
                            + int(round(grade_laboratory, 0))
                            + total_final
                        )
                        total_carry = int(round(total_carry, 0))
                        student_Temp.append(total_carry)
                        if total_carry < int(control_p.min_average):
                            if str(type_level[1]) == "all" or str(type_level[1]) == "d":
                                info_level.append(student_Temp)
                        elif total_carry >= int(
                            control_p.min_average
                        ) and total_carry <= int(control_p.max_average):
                            if str(type_level[1]) == "all" or str(type_level[1]) == "u":
                                info_level.append(student_Temp)
                        else:
                            if str(type_level[1]) == "all" or str(type_level[1]) == "i":
                                info_level.append(student_Temp)
    return dict(
        groupPeriods=group_periods,
        period=period,
        project=project,
        infoLevel=info_level,
        exist_Laboratory=exist_laboratory,
        type_Level=type_level,
        categoriesLevel=categories_level,
        controlP=control_p,
    )
