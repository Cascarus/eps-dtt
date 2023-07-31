from gluon.contrib.pyfpdf import FPDF, HTMLMixin
import datetime
import config
import cpfecys


# ----------------------------- DB de Sanciones --------------------------------
# -------------------------------- Sanciones -----------------------------------

db.define_table(
    "fys_sanction_type",
    Field("name", "string", notnull=True, label=T("Sanction type"), unique=True),
)


db.define_table(
    "fys_sanction",
    Field("type_", "reference fys_sanction_type", notnull=True, label="Tipo"),
    Field("activity", "reference activity_category", notnull=True, label="Activity"),
    Field("semester", "reference period_year", notnull=True, label="Semester"),
    Field(
        "date_", "datetime", notnull=True, label="Date", default=datetime.datetime.now()
    ),
    Field("reporter", "reference auth_user", notnull=True, label="Reporter"),
    Field("description", "string", notnull=True, length=255, label="Description"),
    Field("cause", "string", length=100, label="Cause"),
    Field("course", "reference project", notnull=True, label="Course"),
    Field("professor", "reference auth_user", notnull=True, label="Teacher"),
    Field("status", "integer", notnull=True, label="Status", default=0),
)


db.define_table(
    "fys_sanction_involved",
    Field("sanction", "reference fys_sanction", notnull=True, label="Sanction"),
    Field("academic", "reference academic", notnull=True, label="Academic"),
)


db.define_table(
    "fys_sanction_penalty_type",
    Field("name", "string", notnull=True, label="Penalty type", unique=True),
)


db.define_table(
    "fys_sanction_penalty",
    Field("sanction", "reference fys_sanction", notnull=True, label="Sanction"),
    Field("type_", "reference fys_sanction_penalty_type", notnull=True, label="Type"),
    Field("academic", "reference academic", notnull=True, label="Academic"),
    Field(
        "date_", "datetime", notnull=True, label="Date", default=datetime.datetime.now()
    ),
    Field(
        "penalty_signed",
        "upload",
        label="Penaly Signed",
        requires=[
            IS_UPLOAD_FILENAME(
                extension="pdf",
                error_message="Solo se aceptan archivos con extension PDF",
            ),
            IS_LENGTH(2097152, error_message="El tamaño máximo del archivo es 2MB"),
        ],
    ),
)


# ---------------------------------- Faltas -------------------------------------
# ----------------------- De DSI -----------------------------


db.define_table(
    "fys_infringement_dsi_type",
    Field("name", "string", notnull=True, label="Infringement Type", unique=True),
)


db.define_table(
    "fys_infringement_admin_type",
    Field("name", "string", notnull=True, label="Infringement Type", unique=True),
)


db.define_table(
    "fys_infringement_dsi",
    Field("type_", "reference fys_infringement_dsi_type", notnull=True, label="Type"),
    Field(
        "date_", "datetime", notnull=True, label="Date", default=datetime.datetime.now()
    ),
    Field("description", "string", notnull=True, length=255, label="Description"),
    Field("course", "reference project", notnull=True, label="Course"),
    Field("semester", "reference period_year", notnull=True, label="Semester"),
    Field("student", "reference auth_user", notnull=True, label="Student"),
)


db.define_table(
    "fys_infringement_admin",
    Field("penalty", "integer", notnull=True, label="Penalty"),
    Field("type_", "reference fys_infringement_admin_type", notnull=True, label="Type"),
    Field(
        "date_", "datetime", notnull=True, label="Date", default=datetime.datetime.now()
    ),
    Field("description", "string", notnull=True, length=255, label="Description"),
    Field("course", "reference project", notnull=True, label="Course"),
    Field("semester", "reference period_year", notnull=True, label="Semester"),
    Field("student", "reference auth_user", notnull=True, label="Student"),
    Field(
        "assignation_id",
        "reference user_project",
        notnull=True,
        label="User Project Asiggnation",
    ),
)


# ---------------------------------- Codigo de honor -------------------------------------


db.define_table(
    "fys_honor_code",
    Field(
        "date_", "datetime", notnull=True, label="Date", default=datetime.datetime.now()
    ),
    Field("code", "string", notnull=True, label="Honor Code"),
)


class pdf_santion(FPDF, HTMLMixin):
    def __init__(self, teacher, involved, student_aux=None):
        self.student_aux = student_aux
        self.teacher = teacher
        self.involved = involved
        FPDF.__init__(self)

    def header(self):
        "hook to draw custom page header (logo and title)"
        self.set_font("Times", "B", 18)
        self.cell(155, 7, "UNIVERSIDAD DE SAN CARLOS DE GUATEMALA", 0, 1, "L")
        self.set_font("Times", "", 16)
        self.cell(155, 7, "FACULTAD DE INGENIERIA", 0, 1, "L")

        if config.config_School() == "ecys":
            self.cell(155, 8, "Escuela de Ciencias y Sistemas", 0, 1, "L")
        elif config.config_School() == "emi":
            self.cell(155, 8, "Escuela de Mecanica Industrial", 0, 1, "L")
        pass
        self.ln(5)
        self.cell(190, 0, "", 1, 1, "L")
        self.ln(5)
        self.ln(1)

    def footer(self):
        "hook to draw custom page footer (printing page numbers)"
        self.set_y(-40)
        self.set_font("Arial", "I", 8)
        self.ln(2)
        # Firmas
        if self.student_aux is None:
            self.cell(0, 5, "Firma:_______________________", 0, 0, "L")
            self.cell(0, 5, "Firma:_______________________", 0, 1, "R")
            self.cell(0, 4, self.involved, 0, 0, "L")
            self.cell(0, 4, self.teacher, 0, 1, "R")
            self.cell(0, 4, "Estudiante", 0, 0, "L")
            self.cell(0, 4, "Catedratico", 0, 1, "R")
        else:
            self.cell(0, 5, "Firma:_______________________", 0, 0, "L")
            self.set_x(0)
            self.cell(0, 5, "Firma:_______________________", 0, 0, "C")
            self.cell(0, 5, "Firma:_______________________", 0, 1, "R")
            self.cell(0, 4, self.involved, 0, 0, "L")
            self.set_x(0)
            self.cell(0, 4, self.teacher, 0, 0, "C")
            self.cell(0, 4, self.student_aux, 0, 1, "R")
            self.cell(0, 4, "Estudiante", 0, 0, "L")
            self.set_x(0)
            self.cell(0, 4, "Catedratico", 0, 0, "C")
            self.cell(0, 4, "Auxiliar", 0, 1, "R")
        self.ln(2)
        # Generando hora
        self.cell(
            0,
            5,
            "Generado: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            0,
            0,
            "L",
        )


# Faltas de Administrador


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def report_infringement_admin():
    if request.env.request_method == "POST":
        if (
            request.vars["tipo"] is not None
            and request.vars["descripcion"] is not None
            and request.vars["curso"] is not None
            and request.vars["practicante"] is not None
            and request.vars["periodo"] is not None
            and request.vars["penalizacion"] is not None
        ):
            try:
                course_info = request.vars["curso"].split("-")
                db.fys_infringement_admin.insert(
                    type_=request.vars["tipo"],
                    description=request.vars["descripcion"],
                    course=course_info[0],
                    student=request.vars["practicante"],
                    penalty=request.vars["penalizacion"],
                    semester=request.vars["periodo"],
                    assignation_id=course_info[1],
                )

                if request.vars["penalizacion"] == "1":
                    db(db.user_project.id == course_info[1]).update(
                        assignation_status=2,
                        assignation_status_comment=request.vars["descripcion"],
                    )
            except Exception as err:
                print(err)
            session.flash = "Se ha efectuado la falta con exito"
        else:
            session.flash = "No se pudo efectuar la falta"
        redirect(URL("infringements_and_sanctions", "report_infringement_admin"))

    infringment_type = db.executesql(
        ("SELECT * FROM fys_infringement_admin_type;"), as_dict=True
    )

    period = cpfecys.current_year_period()
    students = []
    students = db.executesql(
        " SELECT DISTINCT "
        " auth_user.id AS id, "
        " auth_user.username AS carnet, "
        " CONCAT(auth_user.first_name, ' ', auth_user.last_name) AS nombre "
        " FROM auth_user "
        " INNER JOIN auth_membership ON auth_membership.user_id = auth_user.id "
        " INNER JOIN auth_group ON auth_group.id = auth_membership.group_id "
        " INNER JOIN user_project ON user_project.assigned_user = auth_user.id "
        " INNER JOIN project ON project.id = user_project.project "
        " WHERE user_project.period <= {} "
        " AND (user_project.period + user_project.periods) > {} "
        " AND auth_group.role = 'Student' "
        " ORDER BY auth_user.username;".format(period.id, period.id),
        as_dict=True,
    )

    courses = []
    student = []
    # Obtener cursos
    if request.vars["estudiante"] is not None:
        student = db.executesql(
            (
                " SELECT "
                " id AS id, "
                " username AS carnet, "
                " CONCAT(first_name, ' ', last_name) AS nombre "
                " FROM auth_user "
                " WHERE id = {};".format(request.vars["estudiante"])
            ),
            as_dict=True,
        )
        if len(student) > 0:
            student = student[0]
            courses = db.executesql(
                (
                    " SELECT "
                    " project.id AS id, "
                    " user_project.id AS asignacion, "
                    " project.name AS name, "
                    " auth_user.id AS user"
                    " FROM auth_user "
                    " INNER JOIN user_project ON user_project.assigned_user = auth_user.id "
                    " INNER JOIN project ON project.id = user_project.project "
                    " WHERE user_project.period <= {} "
                    " AND (user_project.period + user_project.periods) > {} "
                    " AND user_project.assignation_status IS NULL "
                    " AND auth_user.id = {};".format(
                        period.id, period.id, request.vars["estudiante"]
                    )
                ),
                as_dict=True,
            )

    return dict(
        periodo=period,
        estudiantes=students,
        cursos=courses,
        tipos_infracciones=infringment_type,
        estudiante_actual=student,
    )


# Faltas de DSI


@auth.requires_login()
@auth.requires(
    auth.has_membership("Student")
    or auth.has_membership("DSI")
    or auth.has_membership("Super-Administrator")
)
def infringement_list():
    type_view = request.args(0)
    student_search = request.vars["carnet"]

    period = cpfecys.current_year_period()

    if type_view not in ["admin", "student", "dsi"]:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))
    elif type_view == "student":
        if not auth.has_membership("Student"):
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))
    elif type_view == "dsi":
        if not auth.has_membership("DSI"):
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))
    elif type_view == "admin":
        if not auth.has_membership("Super-Administrator"):
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))
    elif type_view is None:
        if auth.has_membership("Student") and not auth.has_membership("DSI"):
            type_view = "student"
    else:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    if request.env.request_method == "POST" and type_view == "admin":
        action = request.args(1)
        id_sanction = request.args(2)
        if action == "delete":
            db(db.fys_infringement_dsi.id == id_sanction).delete()
        elif action == "delete_heavy":
            info_sanction = db(db.fys_infringement_admin.id == id_sanction)
            selected_sanction = info_sanction.select().first()
            if selected_sanction.penalty == 1:
                db(db.user_project.id == selected_sanction.assignation_id).update(
                    assignation_status=None, assignation_status_comment=None
                )
            info_sanction.delete()
        redirect(URL("infringements_and_sanctions", "infringement_list", "admin"))

    periods = []
    if type_view == "admin":
        if request.vars["periodo"]:
            periodo_parametro = request.vars["periodo"]
            period = db(db.period_year.id == periodo_parametro).select().first()
        periods_temp = db(db.period_year).select(orderby=~db.period_year.id)
        for period_temp in periods_temp:
            added = False
            if (
                db((db.fys_infringement_dsi.semester == period_temp.id))
                .select()
                .first()
                is not None
            ):
                periods.append(period_temp)
                added = True
            if (
                db((db.fys_infringement_admin.semester == period_temp.id))
                .select()
                .first()
                is not None
                and not added
            ):
                periods.append(period_temp)

    infringements = []
    heavy_infringements = []
    if type_view == "student":
        infringements = db.executesql(
            (
                " SELECT  "
                " fys_infringement_dsi.id AS id, "
                " project.name AS curso, "
                " fys_infringement_dsi.date_ AS fecha, "
                " fys_infringement_dsi_type.name AS tipo "
                " FROM fys_infringement_dsi "
                " INNER JOIN project ON project.id = fys_infringement_dsi.course "
                " INNER JOIN fys_infringement_dsi_type ON fys_infringement_dsi_type.id = fys_infringement_dsi.type_ "
                " WHERE fys_infringement_dsi.student = {};".format(auth.user.id)
            ),
            as_dict=True,
        )
        heavy_infringements = db.executesql(
            (
                " SELECT "
                " fys_infringement_admin.id AS id, "
                " project.name AS curso, "
                " fys_infringement_admin.date_ AS fecha, "
                " fys_infringement_admin_type.name AS tipo, "
                " fys_infringement_admin.penalty AS penalizacion "
                " FROM fys_infringement_admin "
                " INNER JOIN project ON project.id = fys_infringement_admin.course "
                " INNER JOIN fys_infringement_admin_type ON fys_infringement_admin_type.id = fys_infringement_admin.type_ "
                " WHERE fys_infringement_admin.student = {};".format(auth.user.id)
            ),
            as_dict=True,
        )
    elif type_view == "admin":
        infringements = db.executesql(
            (
                " SELECT "
                " fys_infringement_dsi.id AS id, "
                " auth_user.username AS carnet, "
                " project.name AS curso, "
                " fys_infringement_dsi.date_ AS fecha, "
                " fys_infringement_dsi_type.name AS tipo "
                " FROM fys_infringement_dsi "
                " INNER JOIN project ON project.id = fys_infringement_dsi.course "
                " INNER JOIN fys_infringement_dsi_type ON fys_infringement_dsi_type.id = fys_infringement_dsi.type_ "
                " INNER JOIN auth_user ON auth_user.id = fys_infringement_dsi.student "
                " WHERE fys_infringement_dsi.semester = {};".format(period.id)
            ),
            as_dict=True,
        )
        heavy_infringements = db.executesql(
            (
                " SELECT "
                " fys_infringement_admin.id AS id, "
                " auth_user.username AS carnet, "
                " project.name AS curso, "
                " fys_infringement_admin.date_ AS fecha, "
                " fys_infringement_admin.penalty AS penalizacion, "
                " fys_infringement_admin_type.name AS tipo "
                " FROM fys_infringement_admin "
                " INNER JOIN project ON project.id = fys_infringement_admin.course "
                " INNER JOIN fys_infringement_admin_type ON fys_infringement_admin_type.id = fys_infringement_admin.type_ "
                " INNER JOIN auth_user ON auth_user.id = fys_infringement_admin.student "
                " WHERE fys_infringement_admin.semester = {};".format(period.id)
            ),
            as_dict=True,
        )
    elif student_search is not None:
        infringements = db.executesql(
            (
                " SELECT "
                " fys_infringement_dsi.id AS id, "
                " project.name AS curso, "
                " fys_infringement_dsi.date_ AS fecha, "
                " fys_infringement_dsi_type.name AS tipo "
                " FROM fys_infringement_dsi "
                " INNER JOIN project ON project.id = fys_infringement_dsi.course "
                " INNER JOIN fys_infringement_dsi_type ON fys_infringement_dsi_type.id = fys_infringement_dsi.type_ "
                " INNER JOIN auth_user ON auth_user.id = fys_infringement_dsi.student "
                " WHERE auth_user.username = {};".format(student_search)
            ),
            as_dict=True,
        )
    else:
        infringements = db.executesql(
            (
                " SELECT "
                " fys_infringement_dsi.id AS id, "
                " auth_user.username AS carnet, "
                " project.name AS curso, "
                " fys_infringement_dsi.date_ AS fecha, "
                " fys_infringement_dsi_type.name AS tipo "
                " FROM fys_infringement_dsi "
                " INNER JOIN project ON project.id = fys_infringement_dsi.course "
                " INNER JOIN fys_infringement_dsi_type ON fys_infringement_dsi_type.id = fys_infringement_dsi.type_ "
                " INNER JOIN auth_user ON auth_user.id = fys_infringement_dsi.student "
                " WHERE fys_infringement_dsi.semester = {};".format(period.id)
            ),
            as_dict=True,
        )

    return dict(
        vista=type_view,
        faltas=infringements,
        faltas_graves=heavy_infringements,
        busqueda=student_search,
        periodo=period,
        periodos=periods,
    )


@auth.requires_login()
@auth.requires_membership("DSI")
def report_infringement():
    if request.env.request_method == "POST":
        if (
            request.vars["tipo"] is not None
            and request.vars["descripcion"] is not None
            and request.vars["curso"] is not None
            and request.vars["practicante"] is not None
            and request.vars["periodo"] is not None
        ):
            db.fys_infringement_dsi.insert(
                type_=request.vars["tipo"],
                description=request.vars["descripcion"],
                course=request.vars["curso"],
                student=request.vars["practicante"],
                semester=request.vars["periodo"],
            )
            session.flash = "Se ha realizado el reporte con exito"
        else:
            session.flash = "No se pudo realizar el reporte"
        redirect(URL("infringements_and_sanctions", "report_infringement"))

    period = cpfecys.current_year_period()
    infringment_type = []
    students = []

    infringment_type = db.executesql(
        ("SELECT * FROM fys_infringement_dsi_type;"), as_dict=True
    )

    # Obtener a los practicantes en este momento
    if auth.has_membership("Student"):
        students = db.executesql(
            " SELECT DISTINCT "
            " auth_user.id AS id, "
            " auth_user.username AS carnet, "
            " CONCAT(auth_user.first_name, ' ', auth_user.last_name) AS nombre "
            " FROM auth_user "
            " INNER JOIN auth_membership ON auth_membership.user_id = auth_user.id "
            " INNER JOIN auth_group ON auth_group.id = auth_membership.group_id "
            " INNER JOIN user_project ON user_project.assigned_user = auth_user.id "
            " INNER JOIN project ON project.id = user_project.project "
            " WHERE user_project.period <= {} "
            " AND (user_project.period + user_project.periods) > {} "
            " AND auth_group.role = 'Student'"
            " AND auth_user.id != {} "
            " AND user_project.assignation_status IS NULL "
            " ORDER BY auth_user.username;".format(period.id, period.id, auth.user.id),
            as_dict=True,
        )
    else:
        students = db.executesql(
            " SELECT DISTINCT "
            " auth_user.id AS id, "
            " auth_user.username AS carnet, "
            " CONCAT(auth_user.first_name, ' ', auth_user.last_name) AS nombre "
            " FROM auth_user "
            " INNER JOIN auth_membership ON auth_membership.user_id = auth_user.id "
            " INNER JOIN auth_group ON auth_group.id = auth_membership.group_id "
            " INNER JOIN user_project ON user_project.assigned_user = auth_user.id "
            " INNER JOIN project ON project.id = user_project.project "
            " WHERE user_project.period <= {} "
            " AND (user_project.period + user_project.periods) > {} "
            " AND auth_group.role = 'Student' "
            " AND user_project.assignation_status IS NULL "
            " ORDER BY auth_user.username;".format(period.id, period.id),
            as_dict=True,
        )

    courses = []
    student = []
    # Obtener cursos
    if request.vars["estudiante"] is not None:
        student = db.executesql(
            (
                " SELECT "
                " id AS id, "
                " username AS carnet, "
                " CONCAT(first_name, ' ', last_name) AS nombre "
                " FROM auth_user "
                " WHERE id = {};".format(request.vars["estudiante"])
            ),
            as_dict=True,
        )
        if len(student) > 0:
            student = student[0]
            courses = db.executesql(
                (
                    " SELECT DISTINCT "
                    " project.id AS id, "
                    " project.name AS name, "
                    " auth_user.id AS user"
                    " FROM auth_user "
                    " INNER JOIN user_project ON user_project.assigned_user = auth_user.id "
                    " INNER JOIN project ON project.id = user_project.project "
                    " WHERE user_project.period <= {} "
                    " AND (user_project.period + user_project.periods) > {} "
                    " AND auth_user.id = {};".format(
                        period.id, period.id, request.vars["estudiante"]
                    )
                ),
                as_dict=True,
            )

    return dict(
        periodo=period,
        estudiantes=students,
        tipos_infracciones=infringment_type,
        cursos=courses,
        estudiante_actual=student,
    )


@auth.requires_login()
@auth.requires(
    auth.has_membership("Student")
    or auth.has_membership("DSI")
    or auth.has_membership("Super-Administrator")
)
def infringement_detail():
    if len(request.args) != 2:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    type_view = request.args(0)
    if type_view not in ["student", "dsi", "admin"]:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))
    elif type_view == "student":
        if not auth.has_membership("Student"):
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))
    elif type_view == "dsi":
        if not auth.has_membership("DSI"):
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))
    elif type_view == "admin":
        if not auth.has_membership("Super-Administrator"):
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))
    else:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    sanction_id = request.args(1)
    infringement = db.executesql(
        (
            " SELECT  "
            " 	fys_infringement_dsi.date_ AS fecha, "
            "     fys_infringement_dsi.description AS descripcion, "
            "     CONCAT(auth_user.first_name, ' ', auth_user.last_name) AS estudiante, "
            "     auth_user.username AS carnet,"
            "     fys_infringement_dsi_type.name AS tipo,"
            "     auth_user.id AS reportado, "
            "     project.name AS curso "
            " FROM fys_infringement_dsi "
            " INNER JOIN fys_infringement_dsi_type ON fys_infringement_dsi_type.id = fys_infringement_dsi.type_ "
            " INNER JOIN project ON project.id = fys_infringement_dsi.course "
            " INNER JOIN auth_user ON auth_user.id = fys_infringement_dsi.student "
            " WHERE "
            " 	fys_infringement_dsi.id = {}; ".format(sanction_id)
        ),
        as_dict=True,
    )

    if len(infringement) != 1:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))
    infringement = infringement[0]

    if type_view == "student" and infringement["reportado"] != auth.user.id:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    return dict(falta=infringement, id_sancion=sanction_id, vista=type_view)


@auth.requires_login()
@auth.requires(
    auth.has_membership("Student")
    or auth.has_membership("DSI")
    or auth.has_membership("Super-Administrator")
)
def infringement_process_detail():
    if len(request.args) != 2:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    type_view = request.args(0)
    if type_view not in ["admin", "student"]:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))
    elif type_view == "student":
        if not auth.has_membership("Student"):
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))
    elif type_view == "admin":
        if not auth.has_membership("Super-Administrator"):
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))
    else:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    sanction_id = request.args(1)
    infringement = db.executesql(
        (
            " SELECT  "
            " 	fys_infringement_admin.date_ AS fecha, "
            "     fys_infringement_admin.description AS descripcion, "
            "     CONCAT(auth_user.first_name, ' ', auth_user.last_name) AS estudiante, "
            "     auth_user.username AS carnet,"
            "     fys_infringement_admin_type.name AS tipo,"
            "     fys_infringement_admin.penalty AS penalizacion,"
            "     auth_user.id AS reportado, "
            "     project.name AS curso "
            " FROM fys_infringement_admin "
            " INNER JOIN fys_infringement_admin_type ON fys_infringement_admin_type.id = fys_infringement_admin.type_ "
            " INNER JOIN project ON project.id = fys_infringement_admin.course "
            " INNER JOIN auth_user ON auth_user.id = fys_infringement_admin.student "
            " WHERE "
            " 	fys_infringement_admin.id = {};".format(sanction_id)
        ),
        as_dict=True,
    )

    if len(infringement) != 1:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))
    infringement = infringement[0]

    if type_view == "student" and infringement["reportado"] != auth.user.id:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    return dict(falta=infringement, id_sancion=sanction_id, vista=type_view)


# Sanciones por copia o plagio


@auth.requires_login()
@auth.requires(auth.has_membership('Student')
               or auth.has_membership('Teacher')
               or auth.has_membership('Academic')
               or auth.has_membership('Super-Administrator')
               or auth.has_membership('Ecys-Administrator'))
def sanction_list():
    periodo = cpfecys.current_year_period()
    periodo_parametro = 0
    cursos = []
    sanciones = []
    academic_var = db.academic(db.academic.id_auth_user == auth.user.id)
    type_list = None

    # Validacion de argumento de lista
    if len(request.args) > 0:
        if request.args(0) in ['admin', 'teacher', 'student']:
            type_list = request.args(0)
        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))

    # Validacion de tipo de lista
    if type_list is not None:
        if type_list == 'admin' and not (auth.has_membership('Super-Administrator') or auth.has_membership('Ecys-Administrator')):
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        elif type_list == 'teacher' and not (auth.has_membership('Teacher') or auth.has_membership('Student')):
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
        elif type_list == 'student' and not auth.has_membership('Academic'):
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
    elif not auth.has_membership('Academic'):
        session.flash = T('Not valid Action.')
        redirect(URL('default', 'home'))
    else:
        type_list = 'student'

    # Validacion de periodo
    if request.vars['periodo']:
        periodo_parametro = request.vars['periodo']
        periodo = db(db.period_year.id == periodo_parametro).select().first()
    # Validación de carnet para admin
    if request.vars['carnet']:
        if type_list == 'admin':
            try:
                academic_var = int(request.vars['carnet'])
            except:
                session.flash = T('Not valid Action.')
                redirect(URL('default', 'home'))
            academic_var = db.academic(db.academic.carnet == academic_var)
        else:
            session.flash = T('Not valid Action.')
            redirect(URL('default', 'home'))
    else:
        if type_list == 'admin':
            academic_var = None

    periods_temp = db(db.period_year).select(orderby=~db.period_year.id)
    periods = []
    for period_temp in periods_temp:

        added = False
        if type_list == 'student':
            try:
                if db((db.fys_sanction_involved.academic == academic_var.id) &
                      (db.fys_sanction_involved.sanction == db.fys_sanction.id) &
                        (db.fys_sanction.semester == period_temp.id)).select().first() is not None:
                    if added == False:
                        periods.append(period_temp)
            except:
                pass
        elif type_list == 'teacher':
            try:
                if auth.has_membership('Teacher'):
                    if db((db.user_project.assigned_user == auth.user.id) &
                          (db.user_project.project == db.fys_sanction.course) &
                          (db.fys_sanction.semester == db.user_project.period) &
                          (db.fys_sanction.semester == period_temp.id)).select().first() is not None:
                        periods.append(period_temp)
                else:
                    if db((db.user_project.assigned_user == auth.user.id) &
                          (db.user_project.project == db.fys_sanction.course) &
                          ((db.user_project.assignation_status == 1) | (db.user_project.assignation_status == None)) &
                          ((db.user_project.period <= period_temp.id) &
                          ((db.user_project.period.cast('integer') + db.user_project.periods) > period_temp.id)) &
                          (db.fys_sanction.semester == period_temp.id)).select().first() is not None:
                        periods.append(period_temp)
            except:
                pass
        elif auth.has_membership('Super-Administrator'):
            if db((db.fys_sanction.semester == period_temp.id)).select().first() is not None:
                periods.append(period_temp)
        else:
            break

    print(periodo)
    if type_list == 'student':
        cursos = db.executesql((" SELECT DISTINCT  "
                                " project.name, "
                                " project.id "
                                " FROM fys_sanction "
                                " INNER JOIN fys_sanction_involved ON fys_sanction.id = fys_sanction_involved.sanction "
                                " INNER JOIN project ON project.id = fys_sanction.course "
                                " WHERE fys_sanction_involved.academic = {} "
                                " AND fys_sanction.semester = {};".format(academic_var.id, periodo.id)))
    elif type_list == 'teacher':
        if auth.has_membership('Teacher'):
            try:
                cursos = db.executesql((" SELECT DISTINCT  "
                                        " project.name, "
                                        " project.id "
                                        " FROM fys_sanction "
                                        " INNER JOIN project ON project.id = fys_sanction.course"
                                        ## " INNER JOIN user_project ON user_project.project = project.id AND project.period = fys_sanction.semester"
                                        " INNER JOIN user_project ON user_project.project = project.id"
                                        " WHERE fys_sanction.semester = {} "
                                        " AND user_project.assigned_user = {}; ".format(periodo.id, auth.user.id)))
            except Exception as e:
                print("error")
                print(e)
        else:
            cursos = db.executesql((" SELECT DISTINCT  "
                                    " project.name, "
                                    " project.id "
                                    " FROM fys_sanction "
                                    " INNER JOIN project ON project.id = fys_sanction.course "
                                    " INNER JOIN user_project ON user_project.project = project.id "
                                    " WHERE user_project.period <= fys_sanction.semester "
                                    " 	 AND (user_project.period + user_project.periods) > fys_sanction.semester "
                                    "    AND (user_project.assignation_status IS NULL OR user_project.assignation_status = 1)"
                                    "    AND fys_sanction.semester = {} "
                                    "    AND user_project.assigned_user = {}; ".format(periodo.id, auth.user.id)))
    elif auth.has_membership('Super-Administrator'):
        cursos = db.executesql((" SELECT DISTINCT  "
                                " project.name, "
                                " project.id "
                                " FROM fys_sanction "
                                " INNER JOIN project ON project.id = fys_sanction.course "
                                " WHERE fys_sanction.semester = {};".format(periodo.id)))

    for curso in cursos:
        temp_sanciones = []
        if type_list == 'student':
            temp_sanciones = db.executesql((" SELECT  "
                                            " fys_sanction.id, "
                                            " fys_sanction.cause, "
                                            " fys_sanction_type.name, "
                                            " activity_category.category, "
                                            " fys_sanction.status "
                                            " FROM fys_sanction "
                                            " INNER JOIN fys_sanction_type ON fys_sanction.type_ = fys_sanction_type.id "
                                            " INNER JOIN activity_category ON fys_sanction.activity = activity_category.id "
                                            " INNER JOIN fys_sanction_involved ON fys_sanction.id = fys_sanction_involved.sanction "
                                            " WHERE fys_sanction.course = {} "
                                            " AND fys_sanction_involved.academic = {} "
                                            " AND fys_sanction.semester = {};".format(curso[1], academic_var.id, periodo.id)))
        elif type_list == 'teacher':
            temp_sanciones = db.executesql((" SELECT  "
                                            " fys_sanction.id, "
                                            " fys_sanction.cause, "
                                            " fys_sanction_type.name, "
                                            " activity_category.category, "
                                            " fys_sanction.status "
                                            " FROM fys_sanction "
                                            " INNER JOIN fys_sanction_type ON fys_sanction.type_ = fys_sanction_type.id "
                                            " INNER JOIN activity_category ON fys_sanction.activity = activity_category.id "
                                            " WHERE fys_sanction.course = {} "
                                            " AND fys_sanction.semester = {};".format(curso[1], periodo.id)))
        else:
            temp_sanciones = db.executesql((" SELECT  "
                                            " fys_sanction.id, "
                                            " fys_sanction.cause, "
                                            " fys_sanction_type.name, "
                                            " activity_category.category, "
                                            " fys_sanction.status "
                                            " FROM fys_sanction "
                                            " INNER JOIN fys_sanction_type ON fys_sanction.type_ = fys_sanction_type.id "
                                            " INNER JOIN activity_category ON fys_sanction.activity = activity_category.id "
                                            " WHERE fys_sanction.course = {} "
                                            " AND fys_sanction.semester = {};".format(curso[1], periodo.id)))
        sanciones.append(temp_sanciones)

    if auth.has_membership('Ecys-Administrator'):
        if academic_var is not None:
            sanciones = db.executesql((" SELECT   "
                                       " fys_sanction.id, "
                                       " fys_sanction.cause,  "
                                       " fys_sanction_type.name,  "
                                       " activity_category.category,  "
                                       " project.name, "
                                       " fys_sanction.status  "
                                       " FROM fys_sanction  "
                                       " INNER JOIN fys_sanction_type ON fys_sanction.type_ = fys_sanction_type.id  "
                                       " INNER JOIN activity_category ON fys_sanction.activity = activity_category.id  "
                                       " INNER JOIN fys_sanction_involved ON fys_sanction.id = fys_sanction_involved.sanction "
                                       " INNER JOIN project ON fys_sanction.course = project.id "
                                       " WHERE fys_sanction_involved.academic = {};" .format(academic_var.id)))

    help_status = [['Reportado', 'secondary'], ['Recibido', 'primary'], [
        'Reunión agendada', 'info'], ['Aplicando sanción', 'warning'], ['Sanción aplicada', 'danger']]

    return dict(periodos=periods, periodo=periodo,
                count_periodos=len(periods), cursos=cursos, sanciones=sanciones,
                type_list=type_list, carnet_buscado=request.vars['carnet'], help_status=help_status)


@auth.requires_login()
@auth.requires(
    auth.has_membership("Student")
    or auth.has_membership("Teacher")
    or auth.has_membership("Academic")
    or auth.has_membership("Super-Administrator")
    or auth.has_membership("Ecys-Administrator")
)
def sanction_detail():
    if not len(request.args) == 2:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    # Mostrar sancion o comprobar si esta involucrado
    academic_var = db.academic(db.academic.id_auth_user == auth.user.id)
    fys_sanction_penalty = None
    # Permiso para administrar la sancion
    admin_sanction = False

    # Validar tipo de vista
    type_view = request.args(0)
    if not type_view in ["admin", "teacher", "student"]:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    if type_view is not None:
        if type_view == "admin" and not (
            auth.has_membership("Super-Administrator")
            or auth.has_membership("Ecys-Administrator")
        ):
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))
        elif type_view == "teacher" and not (
            auth.has_membership("Teacher") or auth.has_membership("Student")
        ):
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))
        elif type_view == "student" and not auth.has_membership("Academic"):
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))
    elif not auth.has_membership("Academic"):
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))
    else:
        type_view = "student"

    sanction_id = request.args(1)
    try:
        int(sanction_id)
    except:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    sanction = []

    sanction = db.executesql(
        (
            " SELECT  "
            " project.name, "
            " fys_sanction_type.name, "
            " activity_category.category, "
            " fys_sanction.date_, "
            " fys_sanction.cause, "
            " fys_sanction.description, "
            " CONCAT(professor.first_name, ' ', professor.last_name), "
            " CONCAT(reporter.first_name, ' ', reporter.last_name), "
            " fys_sanction.status, "
            " professor.id, "
            " fys_sanction.semester, "
            " fys_sanction.reporter "
            " FROM fys_sanction  "
            " INNER JOIN project ON project.id = fys_sanction.course "
            " INNER JOIN auth_user professor ON professor.id = fys_sanction.professor "
            " INNER JOIN auth_user reporter ON reporter.id = fys_sanction.reporter "
            " INNER JOIN fys_sanction_type ON fys_sanction_type.id = fys_sanction.type_ "
            " INNER JOIN activity_category ON activity_category.id = fys_sanction.activity "
            " WHERE fys_sanction.id = {} ;".format(sanction_id)
        )
    )

    if len(sanction) != 1:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))
    else:
        sanction = sanction[0]

    involved = db.executesql(
        (
            " SELECT  "
            " academic.carnet, "
            " CONCAT(auth_user.first_name, ' ', auth_user.last_name), "
            " fys_sanction_penalty_type.name, "
            " academic.id, "
            " fys_sanction_penalty.penalty_signed "
            " FROM fys_sanction  "
            " INNER JOIN fys_sanction_involved ON fys_sanction.id = fys_sanction_involved.sanction  "
            " INNER JOIN academic ON academic.id = fys_sanction_involved.academic  "
            " INNER JOIN auth_user ON auth_user.id = academic.id_auth_user  "
            " LEFT JOIN fys_sanction_penalty ON fys_sanction.id = fys_sanction_penalty.sanction AND fys_sanction_involved.academic = fys_sanction_penalty.academic  "
            " LEFT JOIN fys_sanction_penalty_type ON fys_sanction_penalty_type.id = fys_sanction_penalty.type_ "
            " WHERE fys_sanction_involved.sanction = {} "
            " ORDER BY academic.carnet; ".format(sanction_id)
        )
    )

    period = cpfecys.current_year_period()
    # Generar PDF
    genrate_PDF = False
    # Verificar auxiliar
    if auth.has_membership("Student") and type_view == "teacher":
        auxiliar_info = db.executesql(
            (
                " SELECT "
                " 	CONCAT(auth_user.first_name, ' ', auth_user.last_name) AS nombre, "
                "    user_project.assignation_status AS estado"
                " FROM fys_sanction "
                " INNER JOIN user_project ON user_project.project = fys_sanction.course "
                " INNER JOIN auth_user ON auth_user.id = user_project.assigned_user "
                " WHERE fys_sanction.id = {} "
                " 	AND auth_user.id = {} "
                "    AND user_project.period <= fys_sanction.semester "
                " 	AND (user_project.period + user_project.periods) > fys_sanction.semester; ".format(
                    sanction_id, auth.user.id
                )
            ),
            as_dict=True,
        )

        if len(auxiliar_info) != 1:
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))
        auxiliar_info = auxiliar_info[0]
        if auxiliar_info["estado"] is None and sanction[10] == period.id:
            genrate_PDF = True
        elif auxiliar_info["estado"] == 2:
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))
        # Puede administrar las fases de correos y sanciones
        if sanction[8] in [1, 3] and sanction[11] == auth.user.id:
            admin_sanction = True
    # Verificar catedratico
    elif auth.has_membership("Teacher") and type_view == "teacher":
        if sanction[9] != auth.user.id:
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))
        elif sanction[10] == period.id:
            genrate_PDF = True
    # Verificar estudiante
    elif auth.has_membership("Academic") and type_view == "student":
        temp_involve = False
        for student in involved:
            if student[3] == academic_var.id:
                temp_involve = True
                break

        if temp_involve is not True:
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))

    if type_view == "student":
        temp_sanction_penalty = db.executesql(
            (
                " SELECT "
                " 	fys_sanction_penalty_type.name AS penalizacion, "
                "    fys_sanction_penalty.penalty_signed AS documento "
                " FROM fys_sanction_penalty "
                " INNER JOIN fys_sanction_penalty_type ON fys_sanction_penalty.type_ = fys_sanction_penalty_type.id "
                " WHERE fys_sanction_penalty.sanction = {} "
                " AND fys_sanction_penalty.academic = {}; ".format(
                    sanction_id, academic_var.id
                )
            ),
            as_dict=True,
        )
        if len(temp_sanction_penalty) == 1:
            fys_sanction_penalty = temp_sanction_penalty[0]

    # Permitir administrar sancion
    if (
        auth.has_membership("Teacher") and type_view == "teacher"
    ) or auth.has_membership("Super-Administrator"):
        admin_sanction = True

    if request.env.request_method == "POST":
        if admin_sanction is True:
            temp_estado = int(request.vars["estado"]) - 29
            if temp_estado < 4 and temp_estado >= 0:
                if temp_estado == 1:
                    session.fys_debug_error = None
                    involved_mails = db.executesql(
                        (
                            " SELECT  "
                            " 	auth_user.email AS email"
                            " FROM auth_user "
                            " INNER JOIN academic ON academic.id_auth_user = auth_user.id "
                            " INNER JOIN fys_sanction_involved ON fys_sanction_involved.academic = academic.id "
                            " WHERE fys_sanction_involved.sanction = {};".format(
                                sanction_id
                            )
                        ),
                        as_dict=True,
                    )

                    other_mails = db.executesql(
                        (
                            " SELECT "
                            " 	au_p.email AS email_professor, "
                            "  au_r.email AS email_reporter"
                            " FROM fys_sanction "
                            " INNER JOIN auth_user au_p ON au_p.id = fys_sanction.professor "
                            " INNER JOIN auth_user au_r ON au_r.id = fys_sanction.reporter "
                            " WHERE fys_sanction.id = {}; ".format(sanction_id)
                        ),
                        as_dict=True,
                    )
                    other_mails = other_mails[0]

                    admin_email = db.executesql(
                        (
                            " SELECT "
                            " 	email "
                            " FROM auth_user "
                            " 	WHERE username = 'admin'; "
                        ),
                        as_dict=True,
                    )
                    admin_email = admin_email[0]
                    mails = [admin_email["email"]]
                    for mail in involved_mails:
                        if mail["email"] is not None:
                            mails.append(mail["email"])

                    mails.append(other_mails["email_professor"])

                    if other_mails["email_professor"] != other_mails["email_reporter"]:
                        mails.append(other_mails["email_reporter"])

                    was_sent = False
                    if not (
                        request.vars["fechaReunion"] is None
                        or request.vars["horaReunion"] is None
                        or request.vars["mensajeReunion"] is None
                    ):
                        temp_date = str(
                            request.vars["fechaReunion"]
                            + " a las "
                            + request.vars["horaReunion"]
                            + " hrs"
                        )
                        temp_message = str(request.vars["mensajeReunion"]).replace(
                            "\r\n", "<br>"
                        )
                        temp_reason = (
                            str(request.vars["razonReunion"])
                            + " en "
                            + XML(sanction[0])
                        )

                        b_was_sent = send_cite_sanction(
                            temp_reason, temp_date, temp_message, mails
                        )

                        if b_was_sent is None:
                            was_sent = True
                        else:
                            session.fys_debug_error = b_was_sent
                        was_sent = True

                    if was_sent is True:
                        session.flash = "Reunión agendada con exito"
                        db(db.fys_sanction.id == sanction_id).update(
                            status=temp_estado + 1
                        )
                    else:
                        if session.fys_debug_error is None:
                            session.fys_debug_error = str(
                                request.vars["fechaReunion"]
                                + "|"
                                + request.vars["horaReunion"]
                                + "|"
                                + request.vars["mensajeReunion"]
                            )
                        session.flash = "No se pudo agendar la reunión"

                else:
                    db(db.fys_sanction.id == sanction_id).update(status=temp_estado + 1)
                    session.flash = "Ha cambiado de estado"
            else:
                session.flash = "El caso está cerrado"
            redirect(
                URL(
                    "infringements_and_sanctions",
                    "sanction_detail",
                    type_view + "/" + sanction_id,
                )
            )
        else:
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))

    help_status = [
        ["Reportado", "secondary", "Reportado"],
        ["Recibido", "primary", "Marcar como recibido"],
        ["Reunión agendada", "info", "Agendar reunión"],
        ["Aplicando sanción", "warning", "Proceder a aplicar sanciones"],
        ["Sanción aplicada", "danger", "Cerrar caso"],
    ]
    return dict(
        id_sancion=sanction_id,
        sancion=sanction,
        implicados=involved,
        penalizacion=fys_sanction_penalty,
        help_status=help_status,
        type_view=type_view,
        administrar=admin_sanction,
        generar_PDF=genrate_PDF,
    )


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator")
    or auth.has_membership("Teacher")
    or auth.has_membership("Student")
)
def sanction_penalty():
    if len(request.args) != 2:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    type_view = request.args(0)
    if type_view not in ["admin", "teacher"]:
        redirect(URL("default", "home"))
    elif type_view == "admin" and not auth.has_membership("Super-Administrator"):
        redirect(URL("default", "home"))
    elif type_view == "teacher" and not (
        auth.has_membership("Teacher") or auth.has_membership("Student")
    ):
        redirect(URL("default", "home"))

    sanction_id = request.args(1)

    info_sanction = []

    # Obtenemos toda la info de la sancion
    info_sanction = db.executesql(
        (
            " SELECT "
            " project.name AS curso, "
            " fys_sanction_type.name AS tipo, "
            " activity_category.category AS actividad, "
            " fys_sanction.date_ AS fecha, "
            " fys_sanction.cause AS causa, "
            " fys_sanction.professor AS catedratico, "
            " fys_sanction.status AS estado "
            " FROM fys_sanction "
            " INNER JOIN project ON project.id = fys_sanction.course "
            " INNER JOIN fys_sanction_type ON fys_sanction_type.id = fys_sanction.type_ "
            " INNER JOIN activity_category ON activity_category.id = fys_sanction.activity "
            " WHERE fys_sanction.id = {};".format(sanction_id)
        ),
        as_dict=True,
    )

    if len(info_sanction) != 1:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))
    else:
        info_sanction = info_sanction[0]
    if info_sanction["estado"] != 3:
        if info_sanction["estado"] < 3:
            session.flash = "Aún no puedes asignar sanciones"
            redirect(
                URL(
                    "infringements_and_sanctions",
                    "sanction_detail",
                    type_view + "/" + sanction_id,
                )
            )
        if info_sanction["estado"] > 3 and type_view == "teacher":
            session.flash = "El caso está cerrado, no puedes asignar más "
            redirect(
                URL(
                    "infringements_and_sanctions",
                    "sanction_detail",
                    type_view + "/" + sanction_id,
                )
            )

    # Validar profesor
    if type_view == "teacher" and auth.has_membership("Teacher"):
        if info_sanction["catedratico"] != auth.user.id:
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))
    elif type_view == "teacher" and auth.has_membership("Student"):
        auxiliar_info = db.executesql(
            (
                " SELECT "
                " 	CONCAT(auth_user.first_name, ' ', auth_user.last_name) AS nombre, "
                "    user_project.assignation_status AS estado"
                " FROM fys_sanction "
                " INNER JOIN user_project ON user_project.project = fys_sanction.course "
                " INNER JOIN auth_user ON auth_user.id = user_project.assigned_user "
                " WHERE fys_sanction.id = {} "
                " 	AND auth_user.id = {} "
                "     AND user_project.period <= fys_sanction.semester "
                " 	AND (user_project.period + user_project.periods) > fys_sanction.semester; ".format(
                    sanction_id, auth.user.id
                )
            ),
            as_dict=True,
        )

        if len(auxiliar_info) != 1:
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))
        auxiliar_info = auxiliar_info[0]
        if auxiliar_info["estado"] is not None:
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))

    if request.env.request_method == "POST":
        if info_sanction["estado"] == 3:
            if type(request.vars["estudiantes"]) is list:
                for estudiante in request.vars["estudiantes"]:
                    db.fys_sanction_penalty.insert(
                        type_=request.vars["penalizacion"],
                        academic=estudiante,
                        sanction=sanction_id,
                    )
            else:
                db.fys_sanction_penalty.insert(
                    type_=request.vars["penalizacion"],
                    academic=request.vars["estudiantes"],
                    sanction=sanction_id,
                )
            count_not_proccessed = db.executesql(
                (
                    " SELECT  "
                    " COUNT(*) as conteo "
                    " FROM fys_sanction "
                    " INNER JOIN fys_sanction_involved ON fys_sanction.id = fys_sanction_involved.sanction "
                    " INNER JOIN academic ON academic.id = fys_sanction_involved.academic "
                    " INNER JOIN auth_user ON auth_user.id = academic.id_auth_user "
                    " LEFT JOIN fys_sanction_penalty ON fys_sanction.id = fys_sanction_penalty.sanction AND fys_sanction_involved.academic = fys_sanction_penalty.academic "
                    " WHERE fys_sanction_involved.sanction = {}"
                    " AND fys_sanction_penalty.id IS NULL;".format(sanction_id)
                ),
                as_dict=True,
            )
            count_not_proccessed = count_not_proccessed[0]["conteo"]
            if count_not_proccessed == 0:
                db(db.fys_sanction.id == sanction_id).update(status=4)
                redirect(
                    URL(
                        "infringements_and_sanctions",
                        "sanction_detail",
                        type_view + "/" + sanction_id,
                    )
                )
                session.flash = "Caso cerrado"
            else:
                redirect(
                    URL(
                        "infringements_and_sanctions",
                        "sanction_penalty",
                        type_view + "/" + sanction_id,
                    )
                )
                session.flash = "Sanciones aplicadas"
        else:
            if type(request.vars["estudiantes"]) is list:
                for estudiante in request.vars["estudiantes"]:
                    already_penalty = (
                        db(
                            (db.fys_sanction_penalty.sanction == sanction_id)
                            & (db.fys_sanction_penalty.academic == estudiante)
                        )
                        .select()
                        .first()
                    )
                    if already_penalty is not None:
                        db(db.fys_sanction_penalty.id == already_penalty.id).update(
                            type_=request.vars["penalizacion"]
                        )
                    else:
                        db.fys_sanction_penalty.insert(
                            type_=request.vars["penalizacion"],
                            academic=estudiante,
                            sanction=sanction_id,
                        )
                session.flash = "Penalizaciones actualizadas"
            else:
                try:
                    already_penalty = (
                        db(
                            (db.fys_sanction_penalty.sanction == sanction_id)
                            & (
                                db.fys_sanction_penalty.academic
                                == request.vars["estudiantes"]
                            )
                        )
                        .select()
                        .first()
                    )
                    print(already_penalty)
                    if already_penalty is not None:
                        db(db.fys_sanction_penalty.id == already_penalty.id).update(
                            type_=request.vars["penalizacion"]
                        )
                    else:
                        db.fys_sanction_penalty.insert(
                            type_=request.vars["penalizacion"],
                            academic=request.vars["estudiantes"],
                            sanction=sanction_id,
                        )
                except Exception as err:
                    print(err)
                session.flash = "Penalizacion actualizada"
            redirect(
                URL(
                    "infringements_and_sanctions",
                    "sanction_penalty",
                    "/admin/" + sanction_id,
                )
            )

    # Despues de verificar los datos
    involved_not_processed = []
    involved_processed = []
    penalty_types = []

    # Obtener tipos de penalizaciones
    penalty_types = db.executesql(
        ("SELECT * FROM fys_sanction_penalty_type;"), as_dict=True
    )

    # Consulta para procesados
    involved_processed = db.executesql(
        (
            " SELECT "
            " academic.carnet AS carnet, "
            " CONCAT(auth_user.first_name, ' ', auth_user.last_name) AS nombre, "
            " fys_sanction_penalty_type.name AS sancion "
            " FROM fys_sanction "
            " INNER JOIN fys_sanction_involved ON fys_sanction.id = fys_sanction_involved.sanction "
            " INNER JOIN academic ON academic.id = fys_sanction_involved.academic "
            " INNER JOIN auth_user ON auth_user.id = academic.id_auth_user "
            " INNER JOIN fys_sanction_penalty ON fys_sanction.id = fys_sanction_penalty.sanction "
            " INNER JOIN fys_sanction_penalty_type ON fys_sanction_penalty.type_ = fys_sanction_penalty_type.id AND fys_sanction_involved.academic = fys_sanction_penalty.academic "
            " WHERE fys_sanction_involved.sanction = {} "
            " ORDER BY academic.carnet; ".format(sanction_id)
        ),
        as_dict=True,
    )

    if info_sanction["estado"] == 3:
        # Consulta para no procesados
        involved_not_processed = db.executesql(
            (
                "SELECT "
                " academic.id AS id, "
                " academic.carnet AS carnet, "
                " CONCAT(auth_user.first_name, ' ', auth_user.last_name) AS nombre "
                " FROM fys_sanction "
                " INNER JOIN fys_sanction_involved ON fys_sanction.id = fys_sanction_involved.sanction "
                " INNER JOIN academic ON academic.id = fys_sanction_involved.academic "
                " INNER JOIN auth_user ON auth_user.id = academic.id_auth_user "
                " LEFT JOIN fys_sanction_penalty ON fys_sanction.id = fys_sanction_penalty.sanction AND fys_sanction_involved.academic = fys_sanction_penalty.academic "
                " WHERE fys_sanction_involved.sanction = {} "
                " AND fys_sanction_penalty.id IS NULL"
                " ORDER BY academic.carnet; ".format(sanction_id)
            ),
            as_dict=True,
        )
    else:
        involved_not_processed = db.executesql(
            (
                "SELECT "
                " academic.id AS id, "
                " academic.carnet AS carnet, "
                " CONCAT(auth_user.first_name, ' ', auth_user.last_name) AS nombre "
                " FROM fys_sanction "
                " INNER JOIN fys_sanction_involved ON fys_sanction.id = fys_sanction_involved.sanction "
                " INNER JOIN academic ON academic.id = fys_sanction_involved.academic "
                " INNER JOIN auth_user ON auth_user.id = academic.id_auth_user "
                " LEFT JOIN fys_sanction_penalty ON fys_sanction.id = fys_sanction_penalty.sanction AND fys_sanction_involved.academic = fys_sanction_penalty.academic "
                " WHERE fys_sanction_involved.sanction = {} "
                " ORDER BY academic.carnet; ".format(sanction_id)
            ),
            as_dict=True,
        )

    return dict(
        procesados=involved_processed,
        no_procesados=involved_not_processed,
        tipos_penalidad=penalty_types,
        sancion=info_sanction,
        id_sancion=sanction_id,
        vista=type_view,
    )


@auth.requires_login()
@auth.requires(auth.has_membership("Student") or auth.has_membership("Teacher"))
def report_sanction():
    # Antes de operar revisamos si es el metodo POST
    if request.env.request_method == "POST":
        if len(request.vars) != 0:
            report_inserted = 0
            if auth.has_membership("Student"):
                report_inserted = db.fys_sanction.insert(
                    type_=request.vars["tipo"],
                    activity=request.vars["actividad"],
                    semester=request.vars["semestre"],
                    reporter=request.vars["reportante"],
                    description=request.vars["descripcion"],
                    cause=request.vars["causa"],
                    course=request.vars["curso"],
                    professor=request.vars["catedratico"],
                )
            else:
                report_inserted = db.fys_sanction.insert(
                    type_=request.vars["tipo"],
                    activity=request.vars["actividad"],
                    semester=request.vars["semestre"],
                    reporter=request.vars["reportante"],
                    description=request.vars["descripcion"],
                    cause=request.vars["causa"],
                    course=request.vars["curso"],
                    professor=request.vars["catedratico"],
                    status=1,
                )
            if type(request.vars["estudiantes"]) is list:
                for estudiante in request.vars["estudiantes"]:
                    db.fys_sanction_involved.insert(
                        sanction=report_inserted, academic=estudiante
                    )
            else:
                db.fys_sanction_involved.insert(
                    sanction=report_inserted, academic=request.vars["estudiantes"]
                )

            session.flash = "Reporte realizado correctamente"
            redirect(URL("infringements_and_sanctions", "report_sanction"))
        else:
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))

    periodo = cpfecys.current_year_period()
    courses = None
    count_courses = 0
    tipo_reportes = db.executesql(("SELECT * FROM fys_sanction_type;"))
    tipo_actividades = db.executesql(("SELECT id,category FROM activity_category;"))

    if auth.has_membership("Teacher"):
        query = f"""
            SELECT
                CONCAT(auth_user.first_name, ' ', auth_user.last_name) AS teacher_name,
                auth_user.id AS teacher_id,
                project.id AS course_id,
                project.name AS course_name
            FROM auth_user
                INNER JOIN user_project ON auth_user.id = user_project.assigned_user
                INNER JOIN project ON project.id = user_project.project
                INNER JOIN area_level ON project.area_level = area_level.id
            WHERE user_project.assigned_user = {auth.user.id}
                AND user_project.period = {periodo.id}
                AND area_level.name = 'DTT Tutor Académico';
        """            
        courses = db.executesql(query)
        count_courses = len(courses)

    elif auth.has_membership("Student"):
        courses = db.executesql(
            (
                " SELECT   "
                " 	concat(auth_user.first_name, ' ', auth_user.last_name) as teacher_name,  "
                " 	auth_user.id as teacher_id,  "
                " 	project.id as course_id,  "
                " 	project.name as course_name  "
                " FROM auth_user  "
                " INNER JOIN user_project on(auth_user.id = user_project.assigned_user)  "
                " INNER JOIN project on(project.id = user_project.project) "
                " INNER JOIN (select   "
                " project.id  "
                " from auth_user  "
                " inner join user_project on(auth_user.id = user_project.assigned_user)  "
                " inner join project on(project.id = user_project.project)  "
                " inner join area_level on(project.area_level = area_level.id)  "
                " where user_project.assigned_user = {}  "
                " and area_level.name = 'DTT Tutor Académico'   "
                " and user_project.period <= {} "
                " and (user_project.period + user_project.periods) > {} "
                " AND user_project.assignation_status IS NULL ) temp_p on temp_p.id = project.id "
                " INNER JOIN auth_membership on(auth_membership.user_id = auth_user.id) "
                " INNER JOIN auth_group on(auth_membership.group_id = auth_group.id) "
                " WHERE user_project.period = {} "
                " AND auth_group.role = 'Teacher';".format(
                    auth.user.id, periodo.id, periodo.id, periodo.id
                )
            )
        )
        count_courses = len(courses)

    if count_courses == 0:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    print(courses)
    students = []
    for course in courses:
        temp_student = db.executesql(
            (
                " SELECT  "
                " academic.id, "
                " CONCAT(auth_user.first_name, ' ', auth_user.last_name), "
                " academic.carnet "
                " FROM auth_user "
                " INNER JOIN academic ON academic.id_auth_user = auth_user.id "
                " INNER JOIN academic_course_assignation ON academic_course_assignation.carnet = academic.id "
                " WHERE academic_course_assignation.semester = {} "
                " AND academic_course_assignation.assignation = {}"
                " ORDER BY academic.carnet;".format(periodo.id, course[2])
            )
        )
        students.append(temp_student)

    return dict(
        titulo="Reportar copia o plagio",
        tipo_actividades=tipo_actividades,
        tipo_reportes=tipo_reportes,
        periodo=periodo,
        courses=courses,
        count_courses=count_courses,
        estudiantes=students,
        user=auth.user,
    )


@auth.requires_login()
def send_cite_sanction(reason, date, message, emails):
    print("envio de correo")
    print(emails)
    was_sent = ""

    try:
        msg = (
            str(message)
            .replace("á", "&#225;")
            .replace("é", "&#233;")
            .replace("í", "&#237;")
            .replace("ó", "&#243;")
            .replace("ú", "&#250;")
            .replace("ñ", "&#241;")
            .replace("ü", "&#252;")
        )
        subjectS = "Reunión para sanción de " + reason
        mensajeS = (
            "<html><b>Fecha: "
            + date
            + "</b><br/><br/>"
            + msg
            + "<br/><br/><b><small>Mensaje generado por el sistema de sanciones</small></b></html>"
        )
        b_was_sent = mail.send(
            to="dtt.ecys@dtt-dev.site",
            subject=subjectS,
            message=mensajeS,
            bcc=emails,
            encoding="utf-8",
        )

        if not b_was_sent:
            was_sent = mail.error or "No se envio"
        else:
            was_sent = None

        db.mailer_log.insert(
            sent_message=mensajeS,
            destination=str("dtt.ecys@dtt-dev.site"),
            result_log=str(mail.error or "") + ":" + str(mail.result),
            success=b_was_sent,
        )
    except Exception as err:
        was_sent = str(err)
    return was_sent

@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def sanction_manage_involve():
    # Validar sancion
    sanction_id = request.args(0)
    try:
        int(sanction_id)
    except:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    if request.env.request_method == "POST":
        action = request.args(1)
        if action == "delete" and request.vars["caso"] is not None:
            temp_involve = (
                db(db.fys_sanction_involved.id == request.vars["caso"]).select().first()
            )
            db(db.fys_sanction_involved.id == request.vars["caso"]).delete()
            try:
                print(temp_involve)
                already_penalty = db(
                    (db.fys_sanction_penalty.sanction == int(sanction_id))
                    & (db.fys_sanction_penalty.academic == temp_involve.academic)
                )
                if already_penalty is not None:
                    already_penalty.delete()
            except Exception as err:
                print(err)
            session.flash = "Se ha desvinculado al estudiante del caso"
        elif action == "add" and request.vars["involucrados"] is not None:
            try:
                if type(request.vars["involucrados"]) is list:
                    for estudiante in request.vars["involucrados"]:
                        db.fys_sanction_involved.insert(
                            sanction=sanction_id, academic=estudiante
                        )
                    session.flash = "Se han vinculado estudiantes del caso"
                else:
                    db.fys_sanction_involved.insert(
                        sanction=sanction_id, academic=request.vars["involucrados"]
                    )
                    session.flash = "Se ha vinculado a un estudiante del caso"
            except Exception as err:
                print(err)
        redirect(
            URL("infringements_and_sanctions", "sanction_manage_involve", sanction_id)
        )

    not_involved = db.executesql(
        (
            " SELECT "
            " 	academic.id AS id, "
            "     auth_user.username AS carnet, "
            "     CONCAT(auth_user.first_name, ' ', auth_user.last_name) AS nombre "
            " FROM auth_user "
            " INNER JOIN academic ON academic.id_auth_user = auth_user.id "
            " INNER JOIN academic_course_assignation ON academic_course_assignation.carnet = academic.id "
            " INNER JOIN fys_sanction ON fys_sanction.course = academic_course_assignation.assignation  "
            " 	AND fys_sanction.semester = academic_course_assignation.semester "
            " LEFT JOIN fys_sanction_involved ON fys_sanction_involved.sanction = fys_sanction.id "
            " 	AND fys_sanction_involved.academic = academic.id "
            " WHERE "
            " 	fys_sanction.id = {}  "
            "     AND fys_sanction_involved.id IS NULL "
            " ORDER BY academic.CARNET; ".format(sanction_id)
        ),
        as_dict=True,
    )

    involved = db.executesql(
        (
            " SELECT "
            " 	fys_sanction_involved.id AS id, "
            "     auth_user.username AS carnet, "
            "     CONCAT(auth_user.first_name, ' ', auth_user.last_name) AS nombre "
            " FROM auth_user "
            " INNER JOIN academic ON academic.id_auth_user = auth_user.id "
            " INNER JOIN academic_course_assignation ON academic_course_assignation.carnet = academic.id "
            " INNER JOIN fys_sanction ON fys_sanction.course = academic_course_assignation.assignation  "
            " 	AND fys_sanction.semester = academic_course_assignation.semester "
            " LEFT JOIN fys_sanction_involved ON fys_sanction_involved.sanction = fys_sanction.id "
            " 	AND fys_sanction_involved.academic = academic.id "
            " WHERE "
            " 	fys_sanction.id = {}  "
            "     AND fys_sanction_involved.id IS NOT NULL "
            " ORDER BY academic.CARNET; ".format(sanction_id)
        ),
        as_dict=True,
    )

    return dict(
        no_involucrados=not_involved, involucrados=involved, id_sancion=sanction_id
    )


@auth.requires_login()
@auth.requires(auth.has_membership("Student") or auth.has_membership("Teacher"))
def generate_sanction_sign():
    type_view = "student"
    if auth.has_membership("Teacher"):
        type_view = "teacher"

    if request.vars["sanction"] is None or request.vars["student"] is None:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    sanction_id = request.vars["sanction"]
    academic_id = request.vars["student"]
    try:
        int(sanction_id)
        int(academic_id)
    except:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    sanction_info = db.executesql(
        (
            " SELECT "
            " 	CONCAT(au_p.first_name, ' ', au_p.last_name) AS catedratico, "
            "     CONCAT(au_s.first_name, ' ', au_s.last_name) AS estudiante, "
            "     au_s.cui AS cui_estudiante, "
            "     academic.carnet AS carnet, "
            "     fys_sanction_penalty_type.name AS penalizacion, "
            "     CONCAT(fys_sanction_type.name, ' en ', activity_category.category) AS razon, "
            " 	 fys_sanction.description AS descripcion, "
            " 	 fys_sanction.cause AS causa, "
            "     DATE_FORMAT(fys_sanction.date_, '%d/%m/%Y') AS fecha, "
            "     DATE_FORMAT(fys_sanction_penalty.date_, '%d/%m/%Y') AS fecha_penal, "
            "     MONTHNAME(fys_sanction_penalty.date_) AS mes_penal, "
            "     project.name AS curso, "
            "     project.project_id AS id_curso, "
            "     fys_sanction.professor AS validar_catedratico, "
            "     fys_sanction.reporter AS validar_reporte "
            " FROM fys_sanction "
            " 	INNER JOIN fys_sanction_type ON fys_sanction_type.id = fys_sanction.type_ "
            "     INNER JOIN activity_category ON activity_category.id = fys_sanction.activity "
            "     INNER JOIN auth_user au_p ON au_p.id = fys_sanction.professor "
            "     INNER JOIN fys_sanction_involved ON fys_sanction_involved.sanction = fys_sanction.id "
            " 	INNER JOIN academic ON academic.id = fys_sanction_involved.academic "
            " 	INNER JOIN fys_sanction_penalty ON fys_sanction_penalty.sanction = fys_sanction.id "
            " 		AND fys_sanction_penalty.academic = academic.id "
            " 	INNER JOIN fys_sanction_penalty_type ON fys_sanction_penalty_type.id = fys_sanction_penalty.type_ "
            "     INNER JOIN auth_user au_s ON au_s.id = academic.id_auth_user "
            "     INNER JOIN project ON project.id = fys_sanction.course "
            " WHERE fys_sanction.id = {} "
            " 	AND fys_sanction_involved.academic = {}; ".format(
                sanction_id, academic_id
            )
        ),
        as_dict=True,
    )
    if len(sanction_info) != 1:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))
    sanction_info = sanction_info[0]

    sanction_pdf = None
    if type_view == "student":
        auxiliar_info = db.executesql(
            (
                " SELECT "
                " 	CONCAT(auth_user.first_name, ' ', auth_user.last_name) AS nombre, "
                "    user_project.assignation_status AS estado"
                " FROM fys_sanction "
                " INNER JOIN user_project ON user_project.project = fys_sanction.course "
                " INNER JOIN auth_user ON auth_user.id = user_project.assigned_user "
                " WHERE fys_sanction.id = {} "
                " 	AND auth_user.id = {} "
                "     AND user_project.period <= fys_sanction.semester "
                " 	AND (user_project.period + user_project.periods) > fys_sanction.semester; ".format(
                    sanction_id, auth.user.id
                )
            ),
            as_dict=True,
        )

        if len(auxiliar_info) != 1:
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))
        auxiliar_info = auxiliar_info[0]
        sanction_pdf = pdf_santion(
            sanction_info["catedratico"],
            sanction_info["estudiante"],
            auxiliar_info["nombre"],
        )
    else:
        sanction_pdf = pdf_santion(
            sanction_info["catedratico"], sanction_info["estudiante"]
        )

    # Fecha de la penalizacion
    penalty_date = sanction_info["fecha_penal"].split("/")

    # CUI
    cui_estudiante = " - "
    if sanction_info["cui_estudiante"] is not None:
        cui_estudiante = sanction_info["cui_estudiante"]

    subpredicate = ["catedrático", "curso"]
    if sanction_info["validar_catedratico"] != sanction_info["validar_reporte"]:
        subpredicate = ["tutor académico", "laboratorio"]

    sanction_predicate = (
        "El día <b>{} del mes de {} del año {}</b>. El estudiante de nombre: <b>{}</b> identificado con el código unico de Identificación (CUI): <b>{}</b> "
        "e identificado dentro de la Universidad con el registro académico (No. Carné): <b>{}</b>"
        " ha recibido una sanción del tipo <b>{}</b> en el curso de <b>{}</b> por la siguiente razón: \n\n{}"
        "\n\nEl alumno, siendo consciente que infringiendo código de honor que fue firmado al inicio del semestre,"
        " acepta la sanción impuesta por el {} y de manera profesional acepta no volver a cometer otra falta que pueda afectar su permanencia dentro del {}.".format(
            penalty_date[0],
            T(sanction_info["mes_penal"]),
            penalty_date[2],
            XML(sanction_info["estudiante"]),
            cui_estudiante,
            sanction_info["carnet"],
            XML(sanction_info["penalizacion"]),
            XML(sanction_info["curso"]),
            XML(sanction_info["descripcion"]),
            subpredicate[0],
            subpredicate[1],
        )
    )
    sanction_predicate = P(XML(sanction_predicate.replace("\n", "<br/>")))

    sanction_html = DIV()

    sanction_html.append(SPAN(H2("Sanción"), sanction_predicate))

    sanction_pdf.add_page()
    sanction_pdf.write_html(str(XML(sanction_html)))

    response.headers["Content-Type"] = "application/pdf"
    return sanction_pdf.output(dest="S")


@auth.requires_login()
def download_sanction_signed():
    return response.download(request, db)


@auth.requires_login()
@auth.requires(
    auth.has_membership("Student")
    or auth.has_membership("Super-Administrator")
    or auth.has_membership("Teacher")
)
def upload_sanction_signed():

    if request.vars["sanction"] is None or request.vars["student"] is None:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    sanction_id = request.vars["sanction"]
    academic_id = request.vars["student"]
    try:
        int(sanction_id)
        int(academic_id)
    except:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))

    sanction_info = db.executesql(
        (
            " SELECT "
            "     CONCAT(au_s.first_name, ' ', au_s.last_name) AS estudiante, "
            "     fys_sanction_penalty_type.name AS penalizacion, "
            "     CONCAT(fys_sanction_type.name, ' en ', activity_category.category) AS razon, "
            " 	 fys_sanction.cause AS causa, "
            "     DATE_FORMAT(fys_sanction.date_, '%d/%m/%Y') AS fecha, "
            "     project.name AS curso, "
            "     fys_sanction_penalty.penalty_signed AS documento,"
            "     fys_sanction_penalty.id AS id_penalizacion,"
            "     academic.CARNET as carnet, "
            "     fys_sanction.semester AS sancion_semestre, "
            "     fys_sanction.professor AS catedratico "
            " FROM fys_sanction "
            " 	INNER JOIN fys_sanction_type ON fys_sanction_type.id = fys_sanction.type_ "
            "     INNER JOIN activity_category ON activity_category.id = fys_sanction.activity "
            "     INNER JOIN fys_sanction_involved ON fys_sanction_involved.sanction = fys_sanction.id "
            " 	INNER JOIN academic ON academic.id = fys_sanction_involved.academic "
            " 	INNER JOIN fys_sanction_penalty ON fys_sanction_penalty.sanction = fys_sanction.id "
            " 		AND fys_sanction_penalty.academic = academic.id "
            " 	INNER JOIN fys_sanction_penalty_type ON fys_sanction_penalty_type.id = fys_sanction_penalty.type_ "
            "     INNER JOIN auth_user au_s ON au_s.id = academic.id_auth_user "
            "     INNER JOIN project ON project.id = fys_sanction.course "
            " WHERE fys_sanction.id = {} "
            " 	AND fys_sanction_involved.academic = {}; ".format(
                sanction_id, academic_id
            )
        ),
        as_dict=True,
    )

    if len(sanction_info) != 1:
        session.flash = T("Not valid Action.")
        redirect(URL("default", "home"))
    sanction_info = sanction_info[0]

    # Verificar auxiliar
    if auth.has_membership("Student"):
        auxiliar_info = db.executesql(
            (
                " SELECT "
                " 	CONCAT(auth_user.first_name, ' ', auth_user.last_name) AS nombre, "
                "    user_project.assignation_status AS estado"
                " FROM fys_sanction "
                " INNER JOIN user_project ON user_project.project = fys_sanction.course "
                " INNER JOIN auth_user ON auth_user.id = user_project.assigned_user "
                " WHERE fys_sanction.id = {} "
                " 	AND auth_user.id = {} "
                "     AND user_project.period <= fys_sanction.semester "
                " 	AND (user_project.period + user_project.periods) > fys_sanction.semester; ".format(
                    sanction_id, auth.user.id
                )
            ),
            as_dict=True,
        )

        if len(auxiliar_info) != 1:
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))
        auxiliar_info = auxiliar_info[0]
        if auxiliar_info["estado"] is not None:
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))
    # Verificar catedratico
    elif auth.has_membership("Teacher"):
        period = cpfecys.current_year_period()
        if auth.user.id != sanction_info["catedratico"]:
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))
        elif period.id != sanction_info["sancion_semestre"]:
            session.flash = T("Not valid Action.")
            redirect(URL("default", "home"))

    upload_doc_signed = FORM(
        INPUT(_name="id_penalizacion", _type="text"),
        INPUT(_name="estudiante", _type="text"),
        INPUT(_name="sancion", _type="text"),
        INPUT(
            _name="doc_firmado",
            _type="file",
            requires=[
                IS_UPLOAD_FILENAME(
                    extension="pdf",
                    error_message="Solo se aceptan archivos con extension PDF",
                ),
                IS_LENGTH(2097152, error_message="El tamaño máximo del archivo es 2MB"),
            ],
        ),
    )

    if upload_doc_signed.accepts(request.vars, formname="upload_doc_signed"):
        try:
            # FILE UPLOAD
            file_uploaded = db.fys_sanction_penalty.penalty_signed.store(
                upload_doc_signed.vars.doc_firmado.file,
                upload_doc_signed.vars.doc_firmado.filename,
            )
            db(
                db.fys_sanction_penalty.id == upload_doc_signed.vars.id_penalizacion
            ).update(penalty_signed=file_uploaded)
            session.flash = "Se ha subido el archivo firmado"
        except Exception as err:
            print(err)
            session.flash = "Ha ocurrido un error al subir el archivo"
        redirect(
            URL(
                "infringements_and_sanctions",
                "upload_sanction_signed"
                + "?student="
                + upload_doc_signed.vars.estudiante
                + "&sanction="
                + upload_doc_signed.vars.sancion,
            )
        )

    can_upload = sanction_info["documento"] is None
    if auth.has_membership("Super-Administrator"):
        can_upload = True

    print(type(sanction_info["documento"]))

    return dict(
        sancion=sanction_info,
        estudiante=academic_id,
        id_sancion=sanction_id,
        puede_subir=can_upload,
    )


# Codigo de honor


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def manage_honor_code():
    all_honor_codes = db.executesql(
        (" SELECT " " 	id, " "  date_ " " FROM fys_honor_code;"), as_dict=True
    )

    return dict(codigos=all_honor_codes)


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def create_honor_code():
    if request.env.request_method == "POST":
        if request.vars["codigo"] is not None:
            db.fys_honor_code.insert(code=request.vars["codigo"])
            session.flash = "Se ha actualizado el código de honor"
        redirect(URL("infringements_and_sanctions", "manage_honor_code"))

    last_honor_code = db.executesql(
        (" SELECT code FROM fys_honor_code " " ORDER BY id DESC; "), as_dict=True
    )
    if len(last_honor_code) > 0:
        last_honor_code = last_honor_code[0]
    else:
        last_honor_code = None
    return dict(previo=last_honor_code)


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def detail_honor_code():
    id_honor_code = request.args(0)
    try:
        int(id_honor_code)
    except:
        redirect(URL("infringements_and_sanctions", "manage_honor_code"))
    info_honor_code = db.executesql(
        ("SELECT * FROM fys_honor_code WHERE id = {};".format(id_honor_code)),
        as_dict=True,
    )

    if len(info_honor_code) != 1:
        redirect(URL("infringements_and_sanctions", "manage_honor_code"))
    info_honor_code = info_honor_code[0]

    return dict(codigo=info_honor_code)


# Admin
@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def create_infringement_admin_type():
    orderby = dict(fys_infringement_admin_type=[db.fys_infringement_admin_type.id])
    grid = SQLFORM.smartgrid(db.fys_infringement_admin_type, orderby=orderby)
    return dict(grid=grid)



@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def create_infringement_type():
    orderby = dict(fys_infringement_dsi_type=[db.fys_infringement_dsi_type.id])
    grid = SQLFORM.smartgrid(db.fys_infringement_dsi_type, orderby=orderby)
    return dict(grid=grid)


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def create_sanction_type():
    orderby = dict(fys_sanction_type=[db.fys_sanction_type.id])
    grid = SQLFORM.smartgrid(db.fys_sanction_type, orderby=orderby)
    return dict(grid=grid)


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def create_sanction_action_type():
    orderby = dict(fys_sanction_penalty_type=[db.fys_sanction_penalty_type.id])
    grid = SQLFORM.smartgrid(db.fys_sanction_penalty_type, orderby=orderby)
    return dict(grid=grid)


@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def admin_sanction():
    orderby = dict(fys_sanction=[db.fys_sanction.id])
    grid = SQLFORM.smartgrid(db.fys_sanction, linked_tables=[
                             'fys_sanction_type', 'activity_category', 'fys_sanction_involved', 'fys_sanction_involved'], orderby=orderby)
    return dict(grid=grid)


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def admin_infringement():
    orderby = dict(fys_infringement_dsi=[db.fys_infringement_dsi.id])
    grid = SQLFORM.smartgrid(
        db.fys_infringement_dsi,
        linked_tables=["fys_infringement_dsi_type"],
        orderby=orderby,
    )
    return dict(grid=grid)
