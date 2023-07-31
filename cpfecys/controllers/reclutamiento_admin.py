from gluon.serializers import json
import json as json_parser
import datetime
import traceback


ruta_iconos = "/cpfecys/static/images/iconos_reclutamiento"
ruta_img_nvo = "/cpfecys/static/img_nvo"
ruta_fuente = "sources/"

menu_reclutamiento = DIV(
    XML(
        """
	<table id="rec_menu">
		<tr>
			<td>
				<center>
					<a class="btn btn-info btn-outline-secondary"  href="""
        + '"'
        + URL("reclutamiento_admin", "crear_proceso")
        + '"'
        + """>
						<i class="fa fa-plus-circle" aria-hidden="true"></i>
					</a><br>
					<a href="""
        + '"'
        + URL("reclutamiento_admin", "crear_proceso")
        + '"'
        + """>
						Crear proceso
					</a>
				</center>
			</td>
			<td>
				<center>
					<a class="btn btn-info btn-outline-secondary" href="""
        + '"'
        + URL("reclutamiento_admin", "editar_eliminar_proceso")
        + '"'
        + """>
						<i class="fa fa-pencil-square" aria-hidden="true"></i>
					</a><br>
					<a href="""
        + '"'
        + URL("reclutamiento_admin", "editar_eliminar_proceso")
        + '"'
        + """>
						Editar/Eliminar Proceso
					</a>
				</center>
			</td>
			<td>
				<center>
					<a class="btn btn-info btn-outline-secondary" href="""
        + '"'
        + URL("reclutamiento_admin", "activar_proceso")
        + '"'
        + """>
						<i class="fa fa-power-off" aria-hidden="true"></i>
					</a><br>
					<a href="""
        + '"'
        + URL("reclutamiento_admin", "activar_proceso")
        + '"'
        + """>
						Activar
					</a>
				</center>
			</td>
			<td>
				<center>
					<a class="btn btn-info btn-outline-secondary" href="""
        + '"'
        + URL("reclutamiento_admin", "confirmar_proceso_estudiante")
        + '"'
        + """>
						<i class="fa fa-calendar-times-o" aria-hidden="true"></i>
					</a><br>
					<a href="""
        + '"'
        + URL("reclutamiento_admin", "confirmar_proceso_estudiante")
        + '"'
        + """>
						Confirmar proceso
					</a>
				</center>
			</td>
			<td>
				<center>
					<a class="btn btn-info btn-outline-secondary" href="""
        + '"'
        + URL("reclutamiento_admin", "reporte_reclutamiento")
        + '"'
        + """>
						<i class="fa fa-file-text" aria-hidden="true"></i>
					</a><br>
					<a href="""
        + '"'
        + URL("reclutamiento_admin", "reporte_reclutamiento")
        + '"'
        + """>
						Reporte Reclutamiento
					</a>
				</center>
			</td>
			<td>
				<center>
					<a class="btn btn-info btn-outline-secondary" href="""
        + '"'
        + URL("reclutamiento_admin", "reporte_estado")
        + '"'
        + """>
						<i class="fa fa-file-text-o" aria-hidden="true"></i>
					</a><br>
					<a href="""
        + '"'
        + URL("reclutamiento_admin", "reporte_estado")
        + '"'
        + """>
						Reporte de estados
					</a>
				</center>
			</td>
			<td>
				<center>
					<a class="btn btn-info btn-outline-secondary" href="""
        + '"'
        + URL("reclutamiento_admin", "solicitud_incorporacion")
        + '"'
        + """>
						<i class="fa fa-paper-plane" aria-hidden="true"></i>
					</a><br>
					<a href="""
        + '"'
        + URL("reclutamiento_admin", "solicitud_incorporacion")
        + '"'
        + """>
						Solicitudes
					</a>
				</center>

			</td>
		</tr>
	</table>
"""
    )
)


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def get_menu_reclutamiento():
    # Contando pendientes
    sol_incorporacion = db(db.rec_registro.estado == 3).count()
    if (sol_incorporacion is not None) & (sol_incorporacion > 0):
        opc_solicitudes = (
            """<td>
							<center>
								<a  style="position: relative;" class="btn btn-info" href="""
            + '"'
            + URL("reclutamiento_admin", "solicitud_incorporacion")
            + '"'
            + """>
									<i class="fa fa-paper-plane" aria-hidden="true"></i>
									<span style="position: absolute;right: 2px;bottom: 24px;" class="badge badge-important">"""
            + str(sol_incorporacion)
            + """</span>
								</a><br>
								<a href="""
            + '"'
            + URL("reclutamiento_admin", "solicitud_incorporacion")
            + '"'
            + """>
									Solicitudes
								</a>
							</center>
						</td>
		"""
        )
    else:
        opc_solicitudes = (
            """<td>
							<center>
								<a class="btn btn-info" href="""
            + '"'
            + URL("reclutamiento_admin", "solicitud_incorporacion")
            + '"'
            + """>
									<i class="fa fa-paper-plane" aria-hidden="true"></i>
								</a><br>
								<a href="""
            + '"'
            + URL("reclutamiento_admin", "solicitud_incorporacion")
            + '"'
            + """>
									Solicitudes
								</a>
							</center>
						</td>
		"""
        )

    cadena_menu_reclutamiento = XML(
        """
		<table id="rec_menu">
			<tr>
				<td>
					<center>
						<a class="btn btn-info"  href="""
        + '"'
        + URL("reclutamiento_admin", "crear_proceso")
        + '"'
        + """>
							<i class="fa fa-plus-circle" aria-hidden="true"></i>
						</a><br>
						<a href="""
        + '"'
        + URL("reclutamiento_admin", "crear_proceso")
        + '"'
        + """>
							Crear proceso
						</a>
					</center>
				</td>
				<td>
					<center>
						<a class="btn btn-info" href="""
        + '"'
        + URL("reclutamiento_admin", "editar_eliminar_proceso")
        + '"'
        + """>
							<i class="fa fa-pencil-square" aria-hidden="true"></i>
						</a><br>
						<a href="""
        + '"'
        + URL("reclutamiento_admin", "editar_eliminar_proceso")
        + '"'
        + """>
							Editar/Eliminar Proceso
						</a>
					</center>
				</td>
				<td>
					<center>
						<a class="btn btn-info" href="""
        + '"'
        + URL("reclutamiento_admin", "activar_proceso")
        + '"'
        + """>
							<i class="fa fa-power-off" aria-hidden="true"></i>
						</a><br>
						<a href="""
        + '"'
        + URL("reclutamiento_admin", "activar_proceso")
        + '"'
        + """>
							Activar
						</a>
					</center>
				</td>
				<td>
					<center>
						<a class="btn btn-info" href="""
        + '"'
        + URL("reclutamiento_admin", "confirmar_proceso_estudiante")
        + '"'
        + """>
							<i class="fa fa-calendar-times-o" aria-hidden="true"></i>
						</a><br>
						<a href="""
        + '"'
        + URL("reclutamiento_admin", "confirmar_proceso_estudiante")
        + '"'
        + """>
							Confirmar proceso
						</a>
					</center>
				</td>
				<td>
					<center>
						<a class="btn btn-info" href="""
        + '"'
        + URL("reclutamiento_admin", "reporte_reclutamiento")
        + '"'
        + """>
							<i class="fa fa-file-text" aria-hidden="true"></i>
						</a><br>
						<a href="""
        + '"'
        + URL("reclutamiento_admin", "reporte_reclutamiento")
        + '"'
        + """>
							Reporte Reclutamiento
						</a>
					</center>
				</td>
				<td>
					<center>
						<a class="btn btn-info" href="""
        + '"'
        + URL("reclutamiento_admin", "reporte_estado")
        + '"'
        + """>
							<i class="fa fa-file-text-o" aria-hidden="true"></i>
						</a><br>
						<a href="""
        + '"'
        + URL("reclutamiento_admin", "reporte_estado")
        + '"'
        + """>
							Reporte de estados
						</a>
					</center>
				</td>
				"""
        + opc_solicitudes
        + """
			</tr>
		</table>
	"""
    )
    return cadena_menu_reclutamiento


@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def crear_proceso():
	periodos= db((db.period.id!=None) & ((db.period.name == "First Semester") | (db.period.name == "Second Semester")) ).select()
	return dict(opciones=get_menu_reclutamiento(), ruta_fuente=ruta_fuente, periodos= periodos)


@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def editar_eliminar_proceso():
    form_procesos = SQLFORM.smartgrid(db.rec_proceso, create=False)
    return dict(opciones=get_menu_reclutamiento(), ruta_fuente=ruta_fuente, form_procesos=form_procesos)


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def activar_proceso():
    qr_proceso = db.executesql(
        """SELECT pro.anio, pro.periodo, pro.activo, per.name
								FROM cpfecys.rec_proceso AS pro
								INNER JOIN cpfecys.period AS per ON pro.periodo= per.id
								ORDER BY (activo = 'T') DESC, anio DESC, periodo DESC;"""
    )
    opc_radio1 = ""
    iteraciones = 1
    act_anio = "0"
    act_periodo = "0"
    color = ""
    for i_proceso in qr_proceso:
        color = "#e3ecec" if (iteraciones % 2) == 0 else "#ffffff"

        if i_proceso[2] != "T":
            opc_radio1 += (
                """
					<div class="radio" style="background-color:"""
                + color
                + """;">
						<label>
							<input class="radio1" type="radio" name="rad_proceso" value="""
                + '"'
                + str(i_proceso[0]).strip()
                + "-"
                + str(i_proceso[1]).strip()
                + '"'
                + """>"""
                + str(i_proceso[0]).strip()
                + """ - """
                + T(str(i_proceso[3]).strip())
                + """
						</label>
					</div>"""
            )
        else:
            opc_radio1 += (
                """
					<div class="radio" style="background-color:"""
                + color
                + """;">
						<label>
							<input class="radio1" type="radio" name="rad_proceso" value="""
                + '"'
                + str(i_proceso[0]).strip()
                + "-"
                + str(i_proceso[1]).strip()
                + '"'
                + """ checked>"""
                + str(i_proceso[0]).strip()
                + """ - """
                + T(str(i_proceso[3]).strip())
                + """
						</label>
					</div>"""
            )
            act_anio = str(i_proceso[0]).strip()
            act_periodo = str(i_proceso[1]).strip()
        iteraciones += 1
    pass
    opc_radio = DIV(XML(opc_radio1))
    return dict(
        opciones=get_menu_reclutamiento(),
        ruta_fuente=ruta_fuente,
        opc_radio=opc_radio,
        act_anio=act_anio,
        act_periodo=act_periodo,
    )


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def confirmar_proceso_estudiante():
    id_proceso = request.vars["id_proceso"]
    etiqueta_proceso = request.vars["etiqueta_proceso"]
    info_proceso = None
    contador_estados = None
    num_aprobados = 0
    label_proceso = ""
    id_proceso_cont = 0

    # Consulta para el resumen
    if id_proceso != None:
        info_proceso = mtr_obtener_info_proceso(id_proceso)
        contador_estados = mtd_obtner_info_estado(id_proceso)
        if contador_estados != None:
            num_aprobados = contador_estados[0][2]
        label_proceso = (
            ": " + str(etiqueta_proceso).upper()
        )  # Es el texto del proceso que se esta cargando
        id_proceso_cont = id_proceso  # Es el id del proceso que se está cargando

    # Creando select de procesos disponibles
    lista_procesos = db.executesql(
        """SELECT pro.id, pro.anio, pro.periodo, per.name
									FROM cpfecys.rec_proceso AS pro
									INNER JOIN cpfecys.period AS per ON pro.periodo= per.id
									ORDER BY (activo = 'T') DESC, anio DESC, periodo DESC;"""
    )
    # lista_procesos = db(db.rec_proceso.id!=None).select()
    procesos_string = (
        '<select name="select_proceso" id="select_proceso" class="form-control">'
    )
    if len(lista_procesos) > 0:
        for proceso in lista_procesos:
            if (id_proceso != None) & (str(id_proceso) == str(proceso[0])):
                procesos_string += (
                    """<option value="""
                    + '"'
                    + str(proceso[0])
                    + '" selected>'
                    + T(proceso[3])
                    + " - "
                    + str(proceso[1])
                    + "</option>"
                )
            else:
                procesos_string += (
                    """<option value="""
                    + '"'
                    + str(proceso[0])
                    + '">'
                    + T(proceso[3])
                    + " - "
                    + str(proceso[1])
                    + "</option>"
                )
        pass
    procesos_string += "</select>"
    procesos_html = XML(procesos_string)

    return dict(
        opciones=get_menu_reclutamiento(),
        ruta_fuente=ruta_fuente,
        procesos_html=procesos_html,
        label_proceso=label_proceso,
        ruta_iconos=ruta_iconos,
        info_proceso=info_proceso,
        num_aprobados=num_aprobados,
        id_proceso_cont=id_proceso_cont,
    )


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def reporte_reclutamiento():
    # Obtieniendo variables
    id_proceso = request.vars["id_proceso"]
    etiqueta_proceso = request.vars["etiqueta_proceso"]
    lista_estados = None
    lista_solicitudes = None
    lista_pro_asignados = "0"
    label_proceso = ""
    bandera_cargar = 0
    id_proceso_cont = 0

    if id_proceso != None:
        lista_solicitudes = mtd_obtener_solicitudes(id_proceso)
        lista_pro_asignados = mtd_obtener_pro_asignados(id_proceso)
        lista_estados = db(
            (db.rec_estado.id != None) & (db.rec_estado.id != 5)
        ).select()
        label_proceso = str(etiqueta_proceso).upper()
        bandera_cargar = 1
        id_proceso_cont = id_proceso

    # Obteniendo los procesos existentes
    lista_procesos = db.executesql(
        """SELECT pro.id, pro.anio, pro.periodo, per.name
								FROM cpfecys.rec_proceso AS pro
								INNER JOIN cpfecys.period AS per ON pro.periodo= per.id
								ORDER BY (activo = 'T') DESC, anio DESC, periodo DESC;"""
    )
    procesos_string = (
        '<select name="select_proceso" id="select_proceso" class="form-control">'
    )
    if len(lista_procesos) > 0:
        for proceso in lista_procesos:
            if id_proceso != None and str(id_proceso) == str(proceso[0]):
                procesos_string += (
                    """<option value="""
                    + '"'
                    + str(proceso[0])
                    + '" selected>'
                    + T(proceso[3])
                    + " - "
                    + str(proceso[1])
                    + "</option>"
                )
            else:
                procesos_string += (
                    """<option value="""
                    + '"'
                    + str(proceso[0])
                    + '">'
                    + T(proceso[3])
                    + " - "
                    + str(proceso[1])
                    + "</option>"
                )
        pass
    procesos_string += "</select>"
    procesos_html = XML(procesos_string)

    return dict(
        opciones=get_menu_reclutamiento(),
        ruta_fuente=ruta_fuente,
        procesos_html=procesos_html,
        lista_solicitudes=lista_solicitudes,
        lista_estados=lista_estados,
        label_proceso=label_proceso,
        bandera_cargar=bandera_cargar,
        id_proceso_cont=id_proceso_cont,
        lista_pro_asignados=json(lista_pro_asignados),
    )


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def reporte_estado():
    # Obteniento las variables
    id_proceso = request.vars["id_proceso"]
    etiqueta_proceso = request.vars["etiqueta_proceso"]
    id_estado = request.vars["id_estado"]
    lista_solicitudes = None
    label_proceso = ""

    if (id_proceso != None) & (id_estado != None):
        lista_solicitudes = mtd_obtener_solicitudes_estado(id_proceso, id_estado)
        label_proceso = ": " + str(etiqueta_proceso).upper()

    # lista_procesos = db(db.rec_proceso.id!=None).select()
    lista_procesos = db.executesql(
        """SELECT pro.id, pro.anio, pro.periodo, per.name
								FROM cpfecys.rec_proceso AS pro
								INNER JOIN cpfecys.period AS per ON pro.periodo= per.id
								ORDER BY (activo = 'T') DESC, anio DESC, periodo DESC;"""
    )
    lista_estados = db(db.rec_estado.id != None).select()

    # Creando select de procesos disponibles
    procesos_string = (
        '<select name="select_proceso" id="select_proceso" class="form-control">'
    )
    if len(lista_procesos) > 0:
        for proceso in lista_procesos:
            if (id_proceso != None) & (str(id_proceso) == str(proceso[0])):
                procesos_string += (
                    """<option value="""
                    + '"'
                    + str(proceso[0])
                    + '" selected>'
                    + T(proceso[3])
                    + " - "
                    + str(proceso[1])
                    + "</option>"
                )
            else:
                procesos_string += (
                    """<option value="""
                    + '"'
                    + str(proceso[0])
                    + '">'
                    + T(proceso[3])
                    + " - "
                    + str(proceso[1])
                    + "</option>"
                )
        pass
    procesos_string += "</select>"

    # Creando select de estados disponibles
    estados_string = (
        '<select name="select_estado" id="select_estado" class="form-control">'
    )
    if lista_estados != None:
        for estado in lista_estados:
            if (id_estado != None) & (str(id_estado) == str(estado.id)):
                estados_string += (
                    """<option value="""
                    + '"'
                    + str(estado.id)
                    + '" selected>'
                    + str(estado.nombre)
                    + "</option>"
                )
            else:
                estados_string += (
                    """<option value="""
                    + '"'
                    + str(estado.id)
                    + '">'
                    + str(estado.nombre)
                    + "</option>"
                )
        pass
    estados_string += "</select>"

    procesos_html = XML(procesos_string)
    estados_html = XML(estados_string)

    return dict(
        opciones=get_menu_reclutamiento(),
        ruta_fuente=ruta_fuente,
        procesos_html=procesos_html,
        estados_html=estados_html,
        lista_solicitudes=lista_solicitudes,
        ruta_iconos=ruta_iconos,
        label_proceso=label_proceso,
    )


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def solicitud_incorporacion():
    id_estado = request.vars["id_estado"]
    etiqueta_estado = request.vars["etiqueta_estado"]
    lista_incorporacion = None
    lista_estados_cambiar = None
    label_estado = ""

    if id_estado != None:
        lista_incorporacion = mtd_obtener_incorporacion(id_estado)
        lista_estados_cambiar = db(
            (db.rec_registro_estado.id != None) & (db.rec_registro_estado.id != 4)
        ).select()
        label_estado = ": " + str(etiqueta_estado).upper()

    lista_estados = db(db.rec_registro_estado.id != None).select()
    estados_string = (
        '<select name="select_estado" id="select_estado" class="form-control">'
    )
    if lista_estados != None:
        for item in lista_estados:
            if (id_estado != None) & (str(id_estado) == str(item.id)):
                estados_string += (
                    """<option value="""
                    + '"'
                    + str(item.id)
                    + '" selected>'
                    + str(item.nombre)
                    + "</option>"
                )
            else:
                estados_string += (
                    """<option value="""
                    + '"'
                    + str(item.id)
                    + '">'
                    + str(item.nombre)
                    + "</option>"
                )
        pass
    estados_string += "</select>"
    estados_html = XML(estados_string)

    return dict(
        opciones=get_menu_reclutamiento(),
        ruta_fuente=ruta_fuente,
        estados_html=estados_html,
        lista_incorporacion=lista_incorporacion,
        ruta_img_nvo=ruta_img_nvo,
        ruta_iconos=ruta_iconos,
        lista_estados_cambiar=lista_estados_cambiar,
        label_estado=label_estado,
    )


# ***************************************** METODOS PARA INTERACCION ***********************************************
@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def mtd_periodo_letras(periodo):
    periodo_letras = ""
    if periodo == 100:
        periodo_letras = "Primer semestre"
    elif periodo == 101:
        periodo_letras = "Vacaciones primer semestre"
    elif periodo == 200:
        periodo_letras = "Segundo semestre"
    elif periodo == 201:
        periodo_letras = "Vacaciones segundo semestre"
    else:
        periodo_letras = "N/A"

    return periodo_letras


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def mtd_crear_proceso():
    anio = request.vars["anio"]
    periodo = request.vars["periodo"]
    inicio = request.vars["inicio"]
    fin = request.vars["fin"]

    if (anio != None) & (periodo != None) & (inicio != None) & (fin != None):
        permanente = str(request.vars["permanente"]).strip()
        es_permanente = True if int(permanente) == 1 else False
        # Verificando si ya existe un proceso para el año y periodo requerido.
        proceso_existente = (
            db((db.rec_proceso.anio == anio) & (db.rec_proceso.periodo == periodo))
            .select()
            .first()
        )
        if proceso_existente == None:
            # db.rec_proceso.insert(anio=anio, periodo=periodo, fecha_inicio=inicio, fecha_fin=fin, permanente=es_permanente, activo=False)
            db.rec_proceso.insert(
                anio=anio,
                fecha_inicio=inicio,
                fecha_fin=fin,
                activo=False,
                periodo=periodo,
            )
            db.commit()
            respuesta = '{"value":"1"}'
            session.flash = "Se ha creado el proceso"
        else:
            respuesta = '{"value":"0"}'
            session.flash = "Error: ya existe el proceso"
    # response.flash = 'Anio: '+anio+' Periodo: '+ periodo+' Inicio: '+inicio+' Fin: '+fin+' Permanente: '+permanente
    # print "Anio: "+anio+" Periodo: "+ periodo+" Inicio: "+inicio+" Fin: "+fin+" Permanente: %s" % es_permanente
    # print "Anio: "+anio+" Periodo: "+ periodo+" Inicio: "+inicio+" Fin: "+fin+" Permanente: "+permanente
    # return respuesta
    redirect(URL("reclutamiento_admin", "crear_proceso"))


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def mtd_activar_proceso():
    respuesta = ""
    act_anio = request.vars["act_anio"]
    act_periodo = request.vars["act_periodo"]
    nvo_anio = request.vars["nvo_anio"]
    nvo_periodo = request.vars["nvo_periodo"]

    if act_anio != "0" and act_periodo != "0":  # Cuanto hay un proceso activo
        row_activo = (
            db(
                (db.rec_proceso.anio == act_anio)
                & (db.rec_proceso.periodo == act_periodo)
            )
            .select()
            .first()
        )
        if row_activo != None:
            row_activo.activo = "F"
            row_activo.update_record()
            # response.flash = 'Proceso activado'

            row_cambio = (
                db(
                    (db.rec_proceso.anio == nvo_anio)
                    & (db.rec_proceso.periodo == nvo_periodo)
                )
                .select()
                .first()
            )
            if row_cambio != None:
                row_cambio.activo = "T"
                row_cambio.update_record()
                # respuesta= '{"value":"Proceso_activado"}'
                session.flash = T("Proceso activado")
                redirect(URL("reclutamiento_admin", "activar_proceso"))
            else:
                session.flash = T("Error al activar el proceso seleccionado")
                redirect(URL("reclutamiento_admin", "activar_proceso"))
        else:
            session.flash = T("Error al desactivar el proceso actual")
            redirect(URL("reclutamiento_admin", "activar_proceso"))
    else:  # cuando todos están desactivados
        row_cambio = (
            db(
                (db.rec_proceso.anio == nvo_anio)
                & (db.rec_proceso.periodo == nvo_periodo)
            )
            .select()
            .first()
        )
        if row_cambio != None:
            row_cambio.activo = "T"
            row_cambio.update_record()
            # respuesta= '{"value":"Proceso_activado"}'
            session.flash = T("Proceso activado")
            redirect(URL("reclutamiento_admin", "activar_proceso"))
        else:
            session.flash = T("Error al activar el proceso seleccionado")
            redirect(URL("reclutamiento_admin", "activar_proceso"))

    return respuesta


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def mtd_activar_proceso():
    respuesta = ""
    act_anio = request.vars["act_anio"]
    act_periodo = request.vars["act_periodo"]
    nvo_anio = request.vars["nvo_anio"]
    nvo_periodo = request.vars["nvo_periodo"]

    if act_anio != "0" and act_periodo != "0":  # Cuanto hay un proceso activo
        row_activo = (
            db(
                (db.rec_proceso.anio == act_anio)
                & (db.rec_proceso.periodo == act_periodo)
            )
            .select()
            .first()
        )
        if row_activo != None:
            row_activo.activo = "F"
            row_activo.update_record()
            # response.flash = 'Proceso activado'

            row_cambio = (
                db(
                    (db.rec_proceso.anio == nvo_anio)
                    & (db.rec_proceso.periodo == nvo_periodo)
                )
                .select()
                .first()
            )
            if row_cambio != None:
                row_cambio.activo = "T"
                row_cambio.update_record()
                # respuesta= '{"value":"Proceso_activado"}'
                session.flash = T("Proceso activado")
                redirect(URL("reclutamiento_admin", "activar_proceso"))
            else:
                session.flash = T("Error al activar el proceso seleccionado")
                redirect(URL("reclutamiento_admin", "activar_proceso"))
        else:
            session.flash = T("Error al desactivar el proceso actual")
            redirect(URL("reclutamiento_admin", "activar_proceso"))
    else:  # cuando todos están desactivados
        row_cambio = (
            db(
                (db.rec_proceso.anio == nvo_anio)
                & (db.rec_proceso.periodo == nvo_periodo)
            )
            .select()
            .first()
        )
        if row_cambio != None:
            row_cambio.activo = "T"
            row_cambio.update_record()
            # respuesta= '{"value":"Proceso_activado"}'
            session.flash = T("Proceso activado")
            redirect(URL("reclutamiento_admin", "activar_proceso"))
        else:
            session.flash = T("Error al activar el proceso seleccionado")
            redirect(URL("reclutamiento_admin", "activar_proceso"))

    return respuesta


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def mtd_obtener_solicitudes(id_proceso):
    lista_solicitudes = db.executesql(
        """SELECT user.username AS carnet, user.first_name AS nombre,
												user.last_name AS apellido, user.working AS trabaja,
												user.company_name as trabajo_nombre,
												sol.curriculum, sol.listado_cursos,
												area.name AS nombre_area,
										        GROUP_CONCAT(pro.project_id ORDER BY pro.project_id) AS secciones,
										        det.id, det.id_proyecto, det.nombre_proyecto, det.anio_aprobacion,
										        det.semestre_aprobacion, det.nota_aprobacion, det.solicitud,
										        det.area, det.catedratico, det.seccion_proyecto,
										        det.estado, det.nota_oposicion, det.periodos,
										        det.horas, user.cui as cui
										FROM cpfecys.rec_detalle_solicitud AS det
										INNER JOIN cpfecys.rec_solicitud AS sol ON det.solicitud = sol.id
										INNER JOIN cpfecys.auth_user AS user ON sol.id_usuario = user.id
										INNER JOIN cpfecys.area_level AS area ON det.area = area.id
										INNER JOIN cpfecys.project AS pro ON pro.name LIKE CONCAT(det.nombre_proyecto, '%')
										WHERE sol.proceso ={0}
										AND sol.asignado='F'
										GROUP BY det.id;""".format(
            str(id_proceso)
        )
    )

    if lista_solicitudes is not None:
        matriz_nueva = [None] * len(lista_solicitudes)
        i = 0
        for item in lista_solicitudes:
            matriz_nueva[i] = [None] * len(item)
            contador = 0
            for sub_item in item:
                if contador != 13 and contador != 3 and contador != 8:
                    matriz_nueva[i][contador] = sub_item
                elif contador == 13:
                    matriz_nueva[i][contador] = mtd_periodo_letras(sub_item)
                elif contador == 3:
                    matriz_nueva[i][contador] = "Si" if sub_item == "T" else "No"
                elif contador == 8:
                    matriz_nueva[i][contador] = str(sub_item).split(",")
                contador += 1
            pass
            i += 1
        pass

        return matriz_nueva
    else:
        return None


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def mtd_obtener_pro_asignados(id_proceso):
    json_asignados = "0"
    consulta = db.executesql(f"""
        SELECT
            det.id,
            usr.username,
            det.nombre_proyecto,
            det.seccion_proyecto
		FROM cpfecys.rec_detalle_solicitud AS det
			INNER JOIN cpfecys.rec_solicitud AS sol ON det.solicitud = sol.id
			INNER JOIN cpfecys.auth_user AS usr ON sol.id_usuario = usr.id
		WHERE 
            sol.proceso = {id_proceso}
			AND sol.asignado = 'T'
			AND det.estado = 5;
    """)

    if len(consulta) == 0:
        return json_asignados
    
    tamanio_consulta = len(consulta)
    i_consulta = 1
    json_asignados = "["
    for item in consulta:
        json_asignados += (
            '{"id_detalle":"'
            + f'{item[0]}'
            + '", "carnet":"'
            + f'{item[1].strip()}'
            + '", "nombre_pro":"'
            + f'{item[2].strip()}'
            + '", "seccion":"'
            + f'{item[3].strip()}'
            + '"}'
        )
        if i_consulta < tamanio_consulta:
            json_asignados += ","

        i_consulta += 1
    
    json_asignados += "]"
    return json_asignados


"""
0. id ->detalle
1. username
2. nombre_proyecto
3. seccion_proyecto
"""


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def mtd_guardar_reporte():
    tabla_cadena = request.vars["tabla"]

    if tabla_cadena != "no":
        try:
            tabla_json = json_parser.loads(tabla_cadena)
            for fila_tb in tabla_json:
                id_detalle = int(fila_tb["id"].encode("utf-8").strip())
                detalle = db(db.rec_detalle_solicitud.id == id_detalle).select().first()

                if detalle != None:
                    detalle.nota_oposicion = fila_tb["nota_oposicion"]
                    detalle.seccion_proyecto = fila_tb["seccion_proyecto"]
                    detalle.estado = fila_tb["estado"]
                    detalle.periodos = int(fila_tb["periodos"])
                    detalle.horas = int(fila_tb["horas"])
                    detalle.update_record()
                pass
                print(
                    fila_tb["id"]
                    + " "
                    + fila_tb["nota_oposicion"]
                    + " "
                    + fila_tb["seccion_proyecto"]
                    + " "
                    + fila_tb["estado"]
                )
            pass
        except Exception:
            pass
    else:
        print(tabla_cadena)


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def mtd_guardar_rep_btn():
    tabla_cadena = request.vars["tabla"]
    id_proceso = request.vars["id_proceso"]
    etiqueta_proceso = request.vars["etiqueta_proceso"]

    if tabla_cadena != "no":
        tabla_json = json_parser.loads(tabla_cadena)
        for fila_tb in tabla_json:
            id_detalle = int(fila_tb["id"].encode("utf-8").strip())
            detalle = db(db.rec_detalle_solicitud.id == id_detalle).select().first()

            if detalle != None:
                detalle.nota_oposicion = fila_tb["nota_oposicion"]
                detalle.seccion_proyecto = fila_tb["seccion_proyecto"]
                detalle.estado = fila_tb["estado"]
                detalle.periodos = int(fila_tb["periodos"])
                detalle.horas = int(fila_tb["horas"])
                detalle.update_record()
        pass
        if len(tabla_json) > 0:
            session.flash = "Se han guardado los cambios"
        else:
            session.flash = "No hay registros que actualizar"
    # import json
    # x = {"result": "ok"}
    # y = json.dumps(x)
    return "ok"
    # parametros = '?id_proceso='+id_proceso+'&etiqueta_proceso='+etiqueta_proceso
    # redirect(URL('reclutamiento_admin', 'reporte_reclutamiento',str(parametros)))


"""
0 carnet
1 nombre
2 apellido
3 trabaja
4 trabajo_nombre
5 curriculum
6 listado_cursos
7 nombre_area
8 secciones
9 id -> (del detalle solicitud)
10 id_proyecto
11 nombre_proyecto
12 anio_aprobacion
13 semestre_aprobacion
14 nota_aprobacion
15 solicitud
16 area -> (codigo del area)
17 catedratico
18 seccion_proyecto
19 estado
20 nota_oposicion
21 periodos
22 horas
"""


# ---------------------- METODOS PARA REPORTE DE ESTADOS ---------------------------------
@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def mtd_obtener_solicitudes_estado(id_proceso, id_estado):
    if (id_estado != "1") & (id_estado != "5"):
        lista_solicitudes = db.executesql(
            """SELECT user.username AS carnet, user.first_name AS nombre,
												user.last_name AS apellido, user.working AS trabaja,
												user.company_name as trabajo_nombre,
												sol.curriculum, sol.listado_cursos,
												area.name AS nombre_area, est.nombre as nombre_estado,
												det.id, det.id_proyecto, det.nombre_proyecto,
												det.anio_aprobacion, det.semestre_aprobacion, det.nota_aprobacion,
												det.solicitud, det.area, det.catedratico,
												det.seccion_proyecto, det.estado, det.nota_oposicion,
												det.periodos, det.horas
										FROM cpfecys.rec_detalle_solicitud AS det
										INNER JOIN cpfecys.rec_solicitud AS sol ON det.solicitud = sol.id
										INNER JOIN cpfecys.auth_user AS user ON sol.id_usuario = user.id
										INNER JOIN cpfecys.area_level AS area ON det.area = area.id
										INNER JOIN cpfecys.rec_estado as est ON det.estado = est.id
										WHERE sol.proceso ={0}
										AND sol.asignado='F'
										AND det.estado={1}
										AND sol.id NOT IN(
											SELECT sol.id FROM cpfecys.rec_detalle_solicitud AS det
											INNER JOIN cpfecys.rec_solicitud AS sol ON det.solicitud=sol.id
											WHERE sol.proceso={0}
											AND det.estado=1
										);""".format(
                str(id_proceso), str(id_estado)
            )
        )
    elif id_estado == "1":
        lista_solicitudes = db.executesql(
            """SELECT user.username AS carnet, user.first_name AS nombre,
												user.last_name AS apellido, user.working AS trabaja,
												user.company_name as trabajo_nombre,
												sol.curriculum, sol.listado_cursos,
												area.name AS nombre_area, est.nombre as nombre_estado,
												det.id, det.id_proyecto, det.nombre_proyecto,
												det.anio_aprobacion, det.semestre_aprobacion, det.nota_aprobacion,
												det.solicitud, det.area, det.catedratico,
												det.seccion_proyecto, det.estado, det.nota_oposicion,
												det.periodos, det.horas
										FROM cpfecys.rec_detalle_solicitud AS det
										INNER JOIN cpfecys.rec_solicitud AS sol ON det.solicitud = sol.id
										INNER JOIN cpfecys.auth_user AS user ON sol.id_usuario = user.id
										INNER JOIN cpfecys.area_level AS area ON det.area = area.id
										INNER JOIN cpfecys.rec_estado as est ON det.estado = est.id
										WHERE sol.proceso ={0}
										AND sol.asignado='F'
										AND det.estado={1};""".format(
                str(id_proceso), str(id_estado)
            )
        )
    elif id_estado == "5":
        lista_solicitudes = db.executesql(
            """SELECT user.username AS carnet, user.first_name AS nombre,
												user.last_name AS apellido, user.working AS trabaja,
												user.company_name as trabajo_nombre,
												sol.curriculum, sol.listado_cursos,
												area.name AS nombre_area, est.nombre as nombre_estado,
												det.id, det.id_proyecto, det.nombre_proyecto,
												det.anio_aprobacion, det.semestre_aprobacion, det.nota_aprobacion,
												det.solicitud, det.area, det.catedratico,
												det.seccion_proyecto, det.estado, det.nota_oposicion,
												det.periodos, det.horas
										FROM cpfecys.rec_detalle_solicitud AS det
										INNER JOIN cpfecys.rec_solicitud AS sol ON det.solicitud = sol.id
										INNER JOIN cpfecys.auth_user AS user ON sol.id_usuario = user.id
										INNER JOIN cpfecys.area_level AS area ON det.area = area.id
										INNER JOIN cpfecys.rec_estado as est ON det.estado = est.id
										WHERE sol.proceso ={0}
										AND sol.asignado='T'
										AND det.estado={1};""".format(
                str(id_proceso), str(id_estado)
            )
        )
    pass

    return lista_solicitudes


"""
0. carnet
1. nombre
2. apellido
3. trabaja
4. trabajo_nombre
5. curriculum
6. listado_cursos
7. nombre_area
8. nombre_estado
9. id
10 id_proyecto
11. nombre_proyecto
12. anio_aprobacion
13. semestre_aprobacion
14. nota_aprobacion
15. solicitud
16. area
17. catedratico
18. seccion_proyecto
19. estado
20. nota_oposicion
"""


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def mtr_obtener_info_proceso(id_proceso):

    info_proceso = db.executesql(
        """SELECT id, periodo, anio, fecha_inicio, fecha_fin
									FROM cpfecys.rec_proceso AS pro
									WHERE pro.id={0}""".format(
            str(id_proceso)
        )
    )

    if len(info_proceso) > 0:
        matriz_nueva = [None] * len(info_proceso)
        i = 0
        for item in info_proceso:
            matriz_nueva[i] = [None] * len(item)
            contador = 0
            for sub_item in item:
                if contador != 1:
                    matriz_nueva[i][contador] = sub_item
                elif contador == 1:
                    matriz_nueva[i][contador] = mtd_periodo_letras(sub_item)
                contador += 1
            pass
            i += 1
        pass

        return matriz_nueva
    else:
        return None


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def mtd_obtner_info_estado(id_proceso):
    cantidad_estado = db.executesql(
        """SELECT det.estado, est.nombre, COUNT(det.estado) as cantidad
										FROM cpfecys.rec_detalle_solicitud AS det
										INNER JOIN cpfecys.rec_estado AS est ON det.estado = est.id
										INNER JOIN cpfecys.rec_solicitud AS sol ON det.solicitud= sol.id
										INNER JOIN cpfecys.rec_proceso AS pro ON sol.proceso = pro.id
										WHERE pro.id = {0}
										AND det.estado=1
										AND sol.asignado='F'
										GROUP BY det.estado
										ORDER BY det.estado;""".format(
            str(id_proceso)
        )
    )

    if len(cantidad_estado) > 0:
        return cantidad_estado
    else:
        return None


"""
0. cod_estado
1. nombre_estado
2. cantidad
"""

@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def mtd_asignar_proyecto():  # La asignación comenzará a partir del semestre actual
    # Inicializando valores
    id_proceso = request.vars["id_proceso"]
    bitacora = ""
    lista_aprobados = None
    if id_proceso is not None:
        lista_aprobados = mtd_obtener_aprobado_asignar(id_proceso)
        v_proceso = db(db.rec_proceso.id == id_proceso).select().first()

    # Verificando validez del periodo a asignar
    # import cpfecys
    # periodo_actual = cpfecys.current_year_period()
    periodo_actual = None
    if v_proceso is not None:
        v_periodo = (
            db(db.period.id == v_proceso.periodo).select().first()
        )  # Buscando el periodo del proceso: First Semester | Second Semester
        periodo_actual = (
            db(
                (db.period_year.yearp == v_proceso.anio)
                & (db.period_year.period == v_periodo)
            )
            .select()
            .first()
        )  # Buscando año y periodo que coincidan con el proceso
        fecha_sistema = datetime.datetime.now()
        per_sistema_tr = (
            "First Semester" if (fecha_sistema.month < 7) else "Second Semester"
        )  # NOTA: se debe mantener el nombre de los periodos en la tabla "period"
        v_periodo2 = db(db.period.name == per_sistema_tr).select().first()

    # Validando que existan solicitudes aprobadas para el proceso requerido
    if lista_aprobados is not None:
        if periodo_actual is not None:
            if (periodo_actual.yearp == fecha_sistema.year) & (
                periodo_actual.period == v_periodo2.id
            ):
                # session.flash='No soy None XD '+ str(periodo_actual.yearp) +' '+ str(periodo_actual.period)
                # Inicia ciclo para asignar proyectos a los usuarios
                for solicitud in lista_aprobados:
                    # obteniendo valor de cada solicitud aprobada en el periodo requerido
                    carnet = solicitud[1]
                    seccion_proyecto = solicitud[2]
                    periodos = (
                        solicitud[3]
                        if ((solicitud[3] != None) & (solicitud[3] != 0))
                        else 2
                    )
                    adhonorem = False
                    horas = (
                        solicitud[4]
                        if ((solicitud[4] != None) & (solicitud[4] != 0))
                        else 400
                    )
                    import traceback

                    try:
                        usuario = db.auth_user(db.auth_user.username == carnet)
                        if usuario is not None:  # Verificando que usuario exista

                            proyecto = db.project(
                                db.project.project_id == seccion_proyecto
                            )  # Verificar que proyecto exista
                            if proyecto is not None:
                                listperios = db(db.period_detail.period)._select(
                                    db.period_detail.period
                                )  # Periodo variable
                                # Buscando asignación
                                assignation = db.user_project(
                                    (db.user_project.assigned_user == usuario.id)
                                    & (
                                        (~db.period.id.belongs(listperios))
                                        & (db.period_year.period == db.period.id)
                                    )
                                    & (db.user_project.period == db.period_year.id)
                                    & (db.user_project.project == proyecto)
                                    & (db.user_project.assignation_status == None)
                                )

                                if (
                                    assignation is None
                                ):  # Si la asignación no existe, se realiza
                                    # Verificar si el usuario ya tiene el rol Student para asignarselo
                                    if (
                                        db(
                                            (db.auth_group.role == "Student")
                                            & (
                                                db.auth_membership.group_id
                                                == db.auth_group.id
                                            )
                                            & (db.auth_membership.user_id == usuario.id)
                                        )
                                        .select()
                                        .first()
                                        is None
                                    ):
                                        auth.add_membership("Student", usuario)
                                    else:
                                        bitacora += (
                                            "El usuario: "
                                            + str(usuario.username)
                                            + " ya tiene asignado el rol Student\n"
                                        )
                                    # Asignando proyecto:
                                    db.user_project.insert(
                                        assigned_user=usuario,
                                        project=proyecto,
                                        period=periodo_actual,
                                        periods=periodos,
                                        pro_bono=adhonorem,
                                        hours=horas,
                                    )
                                    # Cambiando estado de la solicitud del usuario
                                    solicitud_enviada = (
                                        db(db.rec_solicitud.id == solicitud[0])
                                        .select()
                                        .first()
                                    )
                                    if solicitud_enviada != None:
                                        solicitud_enviada.asignado = True
                                        solicitud_enviada.update_record()
                                    # Cambiando estado del detalle de la solicitud
                                    solicitud_detalle = (
                                        db(db.rec_detalle_solicitud.id == solicitud[8])
                                        .select()
                                        .first()
                                    )
                                    if solicitud_detalle != None:
                                        solicitud_detalle.estado = 5
                                        solicitud_detalle.update_record()

                                    # Enviando correo al usuario
                                    try:
                                        mtd_enviar_correo(
                                            mtd_contenido_correo(solicitud[6]),
                                            str(solicitud[7]),
                                            "Asignación de proyecto",
                                        )
                                    except Exception:
                                        bitacora += (
                                            "No se pudo enviar el correo usuario: "
                                            + str(usuario.username)
                                            + ", ERROR: "
                                            + traceback.format_exc()
                                            + '"\n'
                                        )
                                        pass

                                    bitacora += (
                                        "Se asignó el proyecto: "
                                        + str(seccion_proyecto)
                                        + " al usuario: "
                                        + str(usuario.username)
                                        + "\n"
                                    )
                                else:  # Cuando existe la asignación
                                    bitacora += (
                                        "El proyecto: "
                                        + str(seccion_proyecto)
                                        + " ya se encuentra asignado al usuario: "
                                        + str(usuario.username)
                                        + "\n"
                                    )
                            else:
                                bitacora += (
                                    "El proyecto: "
                                    + str(seccion_proyecto)
                                    + " no existe\n"
                                )

                        else:
                            bitacora += "No existe el usuario\n"
                        pass
                    except Exception:
                        bitacora += (
                            "Ocurrio un error en: usuario "
                            + str(carnet)
                            + " proyecto: "
                            + str(seccion_proyecto)
                            + ', ERROR: "'
                            + traceback.format_exc()
                            + '"\n'
                        )
                        pass
                pass
                # Fin de la iteración
                session.flash = "Se asignaron los proyectos"
            else:
                session.flash = 'Error: No coincide "AÑO" y/o "PERIODO" del "PROCESO SELECCIONADO" con el periodo actual del sistema DTT'
        else:
            session.flash = "Error: El periodo no existe o no ha sido creado"
    else:
        session.flash = "Error, no existen proyectos aprobados"
        bitacora += "No existen solicitudes aprobadas\n"
    print(bitacora)

    redirect(URL("reclutamiento_admin", "confirmar_proceso_estudiante"))


"""
0. id_solicitud -> es el id de solicitud por usuario
1. username
2. seccion_proyecto
3. periodos
4. horas
5. estado
6. nombre_proyecto
7. email
8. id_detalle
"""


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def mtd_obtener_aprobado_asignar(id_proceso):
    solicitudes_asignar = db.executesql(f"""
        SELECT 
            sol.id AS id_solicitud,
            user.username,
            det.seccion_proyecto,
			det.periodos,
            det.horas,
            det.estado,
            det.nombre_proyecto,
			user.email,
            det.id
		FROM cpfecys.rec_detalle_solicitud AS det
			INNER JOIN cpfecys.rec_solicitud AS sol ON det.solicitud = sol.id
			INNER JOIN cpfecys.rec_proceso AS pro ON sol.proceso = pro.id
			INNER JOIN cpfecys.auth_user AS user ON sol.id_usuario = user.id
		WHERE 
            pro.id = {id_proceso}
			AND sol.asignado = 'F'
			AND det.estado = 1;
    """)

    if len(solicitudes_asignar) > 0:
        return solicitudes_asignar
    else:
        return None


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def mtd_contenido_correo(nombre_proyecto):
    contenido = "Notificación de asignación para proyecto de prácticas finales.\n"
    contenido += "\n"
    contenido += (
        'Se le ha asignado el proyecto: "'
        + str(nombre_proyecto.encode("utf-8").strip())
        + '".\n'
    )
    contenido += (
        "Puede verificar su asignación dirigiendose a su usuario en el sistema DTT.\n"
    )
    contenido += "\nSistema de Seguimiento de La Escuela de Ciencias y Sistemas.\n"
    contenido += "Facultad de Ingeniería - Universidad de San Carlos de Guatemala.\n"
    return contenido


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def mtd_contenido_correo_registro(usuario, contrasenia):
    contenido = "Notificación de registro de incorporación al sistema dtt.\n"
    contenido += "\n"
    contenido += "Se ha aceptado su solicitud de incorporación, credenciales:\n"
    contenido += "Usuario: " + str(usuario.encode("utf-8").strip()) + "\n"
    contenido += "Contraseña: " + str(contrasenia.encode("utf-8").strip()) + "\n"
    contenido += "Se recomienda cambiar inmediatamente su contrasenia por seguridad.\n"
    contenido += "\n"
    contenido += (
        "Puede verificar su asignación dirigiendose a su usuario en el sistema DTT.\n"
    )
    contenido += "\n"
    contenido += "\nSistema de Seguimiento de La Escuela de Ciencias y Sistemas.\n"
    contenido += "Facultad de Ingeniería - Universidad de San Carlos de Guatemala.\n"
    return contenido


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def mtd_enviar_correo(mensaje, destinatario, asunto):
    was_sent = mail.send(to=[destinatario], subject=asunto, message=mensaje)

    db.mailer_log.insert(
        sent_message=mensaje,
        destination=str(destinatario),
        result_log=":",
        success=was_sent,
    )

    mensaje2 = str(was_sent)

    return mensaje2


# ------------------------------Metodos para solicitud de incorporación al sistema DTT------------------------------
@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def mtd_obtener_incorporacion(id_estado):
    lista_incorporacion = db.executesql(
        """SELECT nvo.id, nvo.cui, nvo.correo, nvo.fotografia, nvo.apellido, nvo.nombre,
												nvo.carnet, nvo.estado, nvo.password, nvo_est.nombre
											FROM cpfecys.rec_registro AS nvo
											INNER JOIN cpfecys.rec_registro_estado AS nvo_est ON nvo.estado= nvo_est.id
											WHERE nvo.estado= {0}""".format(
            str(id_estado)
        )
    )
    if len(lista_incorporacion) > 0:
        return lista_incorporacion
    else:
        return None


"""
0. id -> tabla registro nvo
1. cui
2. correo
3. fotografia
4. apellido
5. nombre
6. carnet
7. estado
8. password
9. nombre -> del estado
"""


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def mtd_guardar_estado_inc():
    tabla_cadena = request.vars["tabla"]
    print(tabla_cadena)

    if (tabla_cadena is not None) & (tabla_cadena != "no"):
        tabla_json = json_parser.loads(tabla_cadena)
        for fila_tb in tabla_json:
            id_detalle = int(fila_tb["id"].encode("utf-8").strip())
            detalle = db(db.rec_registro.id == id_detalle).select().first()

            if detalle != None:
                detalle.password = fila_tb["password"].encode("utf-8").strip()
                detalle.estado = fila_tb["estado"]
                detalle.update_record()
        pass
        session.flash = "Se han guardado los cambios"
    else:
        session.flash = "Ocurrio un error"
    redirect(URL("reclutamiento_admin", "solicitud_incorporacion"))


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def mtd_registrar_inc():
    lista_incorporacion = db.executesql(
        """SELECT nvo.id, nvo.cui, nvo.correo, nvo.fotografia, nvo.apellido, nvo.nombre,
												nvo.carnet, nvo.estado, nvo.password
											FROM cpfecys.rec_registro AS nvo
											WHERE nvo.estado= 1"""
    )
    if len(lista_incorporacion) > 0:
        bitacora = ""
        for item in lista_incorporacion:
            # Insertando el usuario nuevo
            db.auth_user.insert(
                username=item[6],
                first_name=item[5],
                last_name=item[4],
                email=item[2],
                password=db.auth_user.password.validate(item[8])[0],
            )
            usr_nvo = db(db.auth_user.username == item[6]).select().first()

            # Agregando usuario a lista de alumnos
            if usr_nvo != None:
                db.academic.insert(
                    carnet=item[6], email=item[2], id_auth_user=usr_nvo.id
                )

            # Actualizando estado en la solicitud de incorporación
            detalle = db(db.rec_registro.id == item[0]).select().first()
            if detalle != None:
                detalle.estado = 4
                detalle.update_record()

            # Enviando correo al usuario nuevo

            try:
                mtd_enviar_correo(
                    mtd_contenido_correo_registro((item[6]), str(item[8])),
                    str(item[2]),
                    "Solicitud registro sistema DTT",
                )
            except Exception:
                bitacora += (
                    "No se pudo enviar el correo usuario: "
                    + str(item[6])
                    + ", ERROR: "
                    + traceback.format_exc()
                    + '"\n'
                )
                pass
        pass

        session.flash = "Se crearon los usuarios"
        redirect(URL("reclutamiento_admin", "solicitud_incorporacion"))
    else:
        session.flash = "No existen solicitudes aprobadas"
        redirect(URL("reclutamiento_admin", "solicitud_incorporacion"))


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def obtener_solicitudes_export():
    id_proceso = tabla_cadena = request.vars["id_proceso"]
    lista_solicitudes = db.executesql(
        """SELECT user.username AS carnet, concat(user.first_name,' ' ,user.last_name) AS nombre,
												user.cui AS cui, user.working AS trabaja,
												user.company_name as trabajo_nombre,
												area.name AS nombre_area,
										        det.id, det.id_proyecto, det.nombre_proyecto, det.anio_aprobacion,
										        det.semestre_aprobacion, det.nota_aprobacion, det.solicitud,
										        det.area, det.catedratico, det.seccion_proyecto,
										        det.estado, det.nota_oposicion, det.periodos,
										        det.horas, stat.nombre as nombre_estado,
										        user.email AS email
										FROM cpfecys.rec_detalle_solicitud AS det
										INNER JOIN cpfecys.rec_solicitud AS sol ON det.solicitud = sol.id
										INNER JOIN cpfecys.auth_user AS user ON sol.id_usuario = user.id
										INNER JOIN cpfecys.area_level AS area ON det.area = area.id
										INNER JOIN cpfecys.project AS pro ON pro.name LIKE CONCAT(det.nombre_proyecto, '%')
										INNER JOIN cpfecys.rec_estado AS stat ON det.estado = stat.id
										WHERE sol.proceso ={0}
										AND sol.asignado='F'
										GROUP BY det.id;""".format(
            str(id_proceso)
        )
    )

    if lista_solicitudes is not None:
        report = []
        infoHeader = []
        infoHeader.append("Carnet")
        infoHeader.append("CUI")
        infoHeader.append("Nombre")
        infoHeader.append("Email")
        infoHeader.append("Area de interes")
        infoHeader.append("Proyecto solicitado")
        infoHeader.append("Trabaja")
        infoHeader.append(("Anio"))
        infoHeader.append("Periodo")
        infoHeader.append("Nota")
        infoHeader.append("Catedratico")
        infoHeader.append("Nota de oposicion")
        infoHeader.append("Seccion del proyecto")
        infoHeader.append("Estado")
        infoHeader.append("Periodos a asignar")
        infoHeader.append("Numero de horas")

        report.append(infoHeader)
        for item in lista_solicitudes:
            row = []
            row.append(item[0])
            row.append(item[2])
            row.append(item[1])
            row.append(item[21])
            row.append(item[5])
            row.append(item[8])
            row.append("Si" if item[3] == "T" else "No")
            row.append(item[9])
            row.append(mtd_periodo_letras(item[10]))
            row.append(item[11])
            row.append(item[14])
            row.append(item[17])
            row.append(item[15])
            row.append(item[20])
            row.append(item[18])
            row.append(item[19])

            report.append(row)
        pass
        return dict(filename="data", csvdata=report)

    else:
        return None

@auth.requires_login()
@auth.requires_membership('Super-Administrator')
def mtd_desactivar_proceso():
    row_activo = db(db.rec_proceso.activo == 'T').select(db.rec_proceso.id).first()
    if row_activo is not None:
        row_activo.activo = 'F'
        row_activo.update_record()
        session.flash = T('Proceso desactivado')
        redirect(URL('reclutamiento_admin', 'activar_proceso'))
    else:
        session.flash = T('Error: no existe proceso activo')
        redirect(URL('reclutamiento_admin', 'activar_proceso'))
	
    return ''
