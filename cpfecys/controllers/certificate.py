# coding: utf8
from gluon.contrib.pyfpdf import FPDF, HTMLMixin

import cpfecys
import config
import datetime

@auth.requires_login()
def index():
    #Get the assignations of the current user!
    response.title = "Constancia de Entrega de Reportes y Cumplimiento de requisitos de Práctica Final"

    def get_body(assignation):
        assignations_html = DIV()
        report_average = 0

        if (((assignation.assignation_status == None) or (assignation.assignation_status.name == 'Failed')) and not auth.has_membership('Super-Administrator')):
            session.flash = T('Invalid Action')
            return dict()
        
        #Get the assigned user that is a teacher withing same user_project
        dude_in_charge = db((db.user_project.project == assignation.project) & (db.user_project.period == assignation.period)
                    & (db.user_project.assigned_user == db.auth_user.id) & (db.auth_membership.user_id == db.auth_user.id)
                    & (db.auth_membership.group_id == db.auth_group.id) & (db.auth_group.role == 'Teacher')).select(db.auth_user.first_name, db.auth_user.last_name).first()
        if dude_in_charge is not None:
            dude_in_charge = f'{dude_in_charge.first_name} {dude_in_charge.last_name}'
        else:
            dude_in_charge = "Sin Asignar"

        #Get the reports of the assignation
        #Get the items for the assignation
        reports = db(db.report.assignation == assignation.id).select(
            db.report.score,
            db.report.score_date,
            db.report.dtt_approval,
            db.report.admin_score, 
            db.report.report_restriction,
            db.report.created
        )
        report_body = TBODY()
        total_reports = 0
        acum_score = 0
        for report in reports:
            total_reports += 1
            score = str(report.score)
            score_date = report.score_date

            if not report.dtt_approval:
                score = (str(report.score) or '0') + ', reprobado DTT.'
            if report.dtt_approval == None:
                score = str((report.score or 0)) + ', pendiente DTT.'
            if not report.admin_score is None:
                score_date = 'Calificado por DTT'
                acum_score += ((report.admin_score) or 0)
                score = str(report.admin_score)
            else:
                acum_score += (report.score or 0)

            report_body.append(TR(
                TD(report.report_restriction.name),
                TD("  "),
                TD(report.created),                  
                TD(score_date or 'Nunca Calificado'),
                TD("     "),
                TD(score or '0')
            ))

        rows_report = [
            THEAD(
                TR(
                    TH("Reporte", _width="25%"),
                    TH("     ", _width="15%"),
                    TH("Fecha Entrega", _width="15%"),
                    TH("Fecha Calificación", _width="20%"),
                    TH("  ", _width="5%"),
                    TH("Nota", _width="5%")
                )
            ),
            report_body
        ]
        
        items_head = TBODY()
        items = db((db.item.assignation == assignation) & (db.item.is_active == True)).select(db.item.item_restriction, db.item.created)
        items_total = 0
        for item in items:
            items_total += 1
            items_head.append(TR(
                TD(item.item_restriction.name),
                TD(T(item.created.period.name) + ' - ' + str(item.created.year)),
                TD()
            ))

        rows_items = [
            THEAD(
                TR(
                    TH("Entregable",_width="33%"),
                    TH("Fecha Entrega",_width="33%"),
                    TH("Tipo Entregable",_width="33%")
                )
            ),
            items_head
        ]

        table_items = TABLE(*rows_items, _border="0", _align="center", _width="100%")
        table_reports = TABLE(*rows_report, _border="0", _align="center", _width="100%")
        if total_reports > 0:
            report_average = float(acum_score) / float(total_reports)
        
        reports = DIV(
            H3('Resumen de Reportes'),
            table_reports,
            B('Promedio: '),
            SPAN(report_average or '0')
        )
        items = DIV(
            H3('Resumen de Entregables'),
            table_items
        )

        period_year = db(db.period_year.id == assignation.period).select(db.period_year.yearp, db.period_year.period).first()
        period = db(db.period.id == period_year.period).select(db.period.name).first()
        s = f'{T(period.name)} - {period_year.yearp}'
        rows = [
            THEAD(
                TR(
                    TH("",_width="25%"),
                    TH("",_width="40%"),
                    TH("",_width="25%"),
                    TH("",_width="10%")
                )
            ),
            TBODY(
                TR(
                    TD(B("Inicio de Asignación:")),
                    TD(s),
                    TD(B("Duración de Asignación:")),
                    TD(f'{assignation.periods} Semestres')
                ),
                TR(
                    TD(B("Código Área:")),
                    TD(assignation.project.area_level.id)
                ),
                TR(
                    TD(B("Código Proyecto:")),
                    TD(assignation.project.project_id)
                ),
                TR(
                    TD(B("Área:")),
                    TD(str(assignation.project.area_level.name))
                ),
                TR(
                    TD(B("Proyecto:")),
                    TD(assignation.project.name)
                ),
                TR(
                    TD(B("Encargado(a):")),
                    TD(dude_in_charge)
                ),
                TR(
                    TD(B("Carnet:")),
                    TD(assignation.assigned_user.username)
                ),
                TR(
                    TD(B("Nombre del Practicante:")),
                    TD(f'{assignation.assigned_user.first_name} {assignation.assigned_user.last_name}')
                ),
                TR(),
                TR(
                    TD(B("Total de Reportes:")),
                    TD(total_reports),
                    TD(B("Promedio de Reportes:")),
                    TD(report_average)
                ),
                TR(
                    TD(B("Total de Entregables:")),
                    TD(items_total)
                )
            )
        ]
        table_assignation = TABLE(*rows, _border="0", _align="center", _width="100%")
        assignations_html.append(SPAN(H3('Resumen de Asignación'), table_assignation, reports))
        return DIV(H2('Asignaciones a Proyectos'), assignations_html)

    if request.extension == 'pdf':
        
        # create a custom class with the required functionalities 
        class MyFPDF(FPDF, HTMLMixin):
            def header(self):
                self.set_font('Times', 'B', 18)
                self.cell(35) # padding
                self.cell(155, 7, "UNIVERSIDAD DE SAN CARLOS DE GUATEMALA", 0, 1, 'L')
                self.set_font('Times', '', 16)
                self.cell(35) # padding
                self.cell(155, 7, "FACULTAD DE INGENIERÍA", 0, 1, 'L')
                self.cell(35) # padding
                if config.config_School() == 'ecys':
                    self.cell(155, 8, "Escuela de Ciencias y Sistemas", 0, 1, 'L')
                    self.cell(35) # padding
                    self.cell(155, 7, "Desarrollo de Transferencia Tecnológica (DTT)", 0, 1, 'L')
                elif config.config_School() == 'emi':
                    self.cell(155, 8, "Escuela de Mecanica Industrial", 0, 1, 'L')
                    self.cell(35) # padding
                    self.cell(155, 7, "Control de Practica Final (CPF - EMI)", 0, 1, 'L')
                
                self.ln(5)
                self.cell(190, 0, '', 1, 1, 'L')
                self.ln(5)
                self.ln(1)

            def footer(self):
                self.set_y(-25)
                self.set_font('Arial', 'I', 8)
                txt = f'Página {self.page_no()} de {self.alias_nb_pages()}'
                self.ln(2)
                self.cell(0, 5, 'Firma:_______________________', 0, 1, 'C')
                cparams = cpfecys.get_custom_parameters()
                self.cell(0, 4, cparams.coordinator_name, 0, 1, 'C')
                self.cell(0, 4, cparams.coordinator_title, 0, 1, 'C')
                self.cell(0, 5, 'Generado: ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), 0, 0, 'L')
                self.cell(0, 5, txt, 0, 1, 'R')
        
        pdf = MyFPDF()
        # create a page and serialize/render HTML objects
        assignations = []
        if request.vars['user'] is not None:
            assignations = db((db.user_project.assigned_user == request.vars['user']) & (db.user_project.assignation_ignored == False)).select(db.user_project.ALL)
        
        if request.vars['period'] is not None:
            assignations = db((db.user_project.period == request.vars['period']) & (db.user_project.assignation_ignored == False)).select(db.user_project.ALL)
        
        for x in assignations:
            if x.assignation_status is not None:
                pdf.add_page()
                pdf.write_html(
                    str(
                        XML(
                            SPAN(
                                B(CENTER('Solvencia de Entrega de Reportes y Cumplimiento ')),
                                B(CENTER("de")),
                                B(CENTER("Requisitos de Práctica Final")),
                                DIV(get_body(x))
                            ),
                            sanitize=False
                        )
                    )
                )
        # prepare PDF to download:
        response.headers['Content-Type'] = 'application/pdf'
        return pdf.output(dest = 'S')
    else:
        return dict(message="hello from certificate.py")
