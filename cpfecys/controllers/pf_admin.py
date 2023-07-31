ruta_iconos = "/cpfecys/static/pf_sources"
ruta_img_nvo = "/cpfecys/static/img_nvo"
ruta_fuente = "sources/"
menu_reclutamiento = DIV(
    XML(
        """
	<table id="rec_menu">
		<tr>
			<td>
				<center>
					<a class="btn btn-info"  href="""
        + '"'
        + URL("pf_admin", "abc_admin")
        + '"'
        + """>
						<i class="fa fa-plus-circle" aria-hidden="true"></i>
					</a><br>
					<a href="""
        + '"'
        + URL("pf_admin", "abc_admin")
        + '"'
        + """>
						Crear categoría
					</a>
				</center>
			</td>
			<td>
				<center>
					<a class="btn btn-info" href="""
        + '"'
        + URL("pf_admin", "edit_del_categoria")
        + '"'
        + """>
						<i class="fa fa-pencil-square" aria-hidden="true"></i>
					</a><br>
					<a href="""
        + '"'
        + URL("pf_admin", "edit_del_categoria")
        + '"'
        + """>
						Editar/Eliminar categoría
					</a>
				</center>
			</td>
			<td>
				<center>
					<a class="btn btn-info" href="""
        + '"'
        + URL("pf_admin", "crear_pregunta")
        + '"'
        + """>
						<i class="fa fa-question-circle" aria-hidden="true"></i>
					</a><br>
					<a href="""
        + '"'
        + URL("pf_admin", "crear_pregunta")
        + '"'
        + """>
						Crear pregunta
					</a>
				</center>
			</td>
			<td>
				<center>
					<a class="btn btn-info" href="""
        + '"'
        + URL("pf_admin", "edit_del_pregunta")
        + '"'
        + """>
						<i class="fa fa-clipboard" aria-hidden="true"></i>
					</a><br>
					<a href="""
        + '"'
        + URL("pf_admin", "edit_del_pregunta")
        + '"'
        + """>
						Editar/eliminar pregunta
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
def abc_admin():
    form_categoria = SQLFORM(db.pf_categoria_p, create=False)
    if form_categoria.process().accepted:
        response.flash = "Información aceptada"
    elif form_categoria.errors:
        response.flash = "El formulario contiene errores"
    else:
        pass
        # response.flash = 'please fill out the form'
    return dict(opciones=menu_reclutamiento, form_categoria=form_categoria)


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def edit_del_categoria():
    form_categoria = SQLFORM.smartgrid(db.pf_categoria_p, create=False)
    return dict(opciones=menu_reclutamiento, form_categoria=form_categoria)


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def crear_pregunta():
    form_pregunta = SQLFORM(db.pf_pregunta_p, create=False)
    if form_pregunta.process().accepted:
        response.flash = "Información aceptada"
    elif form_pregunta.errors:
        response.flash = "El formulario contiene errores"
    else:
        pass
    return dict(opciones=menu_reclutamiento, form_pregunta=form_pregunta)


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def edit_del_pregunta():
    form_pregunta = SQLFORM.smartgrid(db.pf_pregunta_p, create=False)
    return dict(opciones=menu_reclutamiento, form_pregunta=form_pregunta)


@auth.requires_login()
@auth.requires(auth.has_membership("Student") or auth.has_membership("Academic"))
def ver_preguntas():
    categorias = db(db.pf_categoria_p.id != None).select()
    categoria_id = request.vars["categoria_id"]
    str_categoria_html = ""
    preguntas_html = ""

    if categorias != None:
        str_categoria_html += '<select name="select_categoria" id="select_categoria" class="form-control">'
        for categoria in categorias:
            str_categoria_html += (
                """<option value="""
                + '"'
                + str(categoria.id)
                + '">'
                + categoria.categoria
                + "</option>"
            )
        str_categoria_html += "</select>"

    if categoria_id != None:
        preguntas_html = XML(get_acordion_preguntas(categoria_id))

    categoria_html = XML(str_categoria_html)

    return dict(categoria_html=categoria_html, preguntas_html=preguntas_html)


@auth.requires_login()
@auth.requires(auth.has_membership('Student') or auth.has_membership('Academic'))
def get_acordion_preguntas(categoria_id):
	categoria = db((db.pf_categoria_p.id!=None) & (db.pf_categoria_p.id==categoria_id)).select().first()
	preguntas = db((db.pf_pregunta_p.id!=None) & (db.pf_pregunta_p.categoria==categoria_id)).select()
	acordion = ''

	if categoria!= None:
		acordion+='<center><h2>'+categoria.categoria+'</h2></center>'

	acordion+='<div class="accordion" id="accordion2">'
	if preguntas!=None:
		i =1
		for pregunta in preguntas:
			acordion+=""" <div class="accordion-group">
										<div class="accordion-heading" style="background:#A9F5A9">
											<a class="accordion-toggle" data-toggle="collapse" data-parent="#accordion2" href="#p"""+str(pregunta.id)+'"'+""">
											<b>"""+str(i)+". "+pregunta.pregunta+"""</b>
											</a>
										</div>
										<div id="p"""+str(pregunta.id)+'"'+""" class="accordion-body collapse">
											<div class="accordion-inner">
											"""+pregunta.respuesta+"""
											</div>
										</div>
									</div> """
			i+=1
	acordion+='</div>'

	return acordion
