@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Tesis-Administrator'))
def adviser():
    grid = SQLFORM.grid(db.tesis_adviser)
    return dict(grid=grid)

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Tesis-Administrator'))
def asign_topics():
    #busco el id de un estado en proceso
    dset_ok = db(db.tesis_status.name.upper().like('%PROCESO%')).select(db.tesis_status.id).first()
    id_ok = '1'
    if dset_ok:
        id_ok = str(dset_ok.id)

    #busco el id de un estado que sea vencido
    dset_vencido = db(db.tesis_status.name.upper().like('%VENCIDO%')).select(db.tesis_status.id).first()
    id_vencido = '3'
    if dset_vencido:
        id_vencido = str(dset_vencido.id)

    #busco todos los estudiantes cuya fecha sea vencida de la actual
    ds_student_old = db((db.tesis_asigned_topics.topic_date_validity < request.now.date()) & (db.tesis_asigned_topics.status == id_ok)).select()

    #si hay estudiantes en proceso cuya fecha sea vencida automaticamente se actualiza el estado a vencido
    if ds_student_old:
        for row in ds_student_old:
            row.update_record(status=id_vencido)

    grid = SQLFORM.grid(db.tesis_asigned_topics, maxtextlength=75, searchable=False)
    return dict(grid=grid)

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Tesis-Administrator'))
def modality():
    grid = SQLFORM.grid(db.tesis_modality, maxtextlength=75)
    return dict(grid=grid)

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Tesis-Administrator'))
def reports():
    #busco el id de un estado en proceso
    dset_ok = db(db.tesis_status.name.upper().like('%PROCESO%')).select(db.tesis_status.id).first()
    id_ok = str(dset_ok.id) if dset_ok else '1'

    #busco el id de un estado que sea vencido
    dset_vencido = db(db.tesis_status.name.upper().like('%VENCIDO%')).select(db.tesis_status.id).first()
    id_vencido = str(dset_vencido.id) if dset_vencido else '3'
        
    #busco todos los estudiantes cuya fecha sea vencida de la actual
    dset_student_old = db((db.tesis_asigned_topics.topic_date_validity < request.now.date()) & (db.tesis_asigned_topics.status == id_ok)).select()

    #si hay estudiantes en proceso cuya fecha sea vencida automaticamente se actualiza el estado a vencido
    if dset_student_old:
        for row in dset_student_old:
            row.update_record(status=id_vencido)

    return dict()

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Tesis-Administrator'))
def research_areas():
    grid = SQLFORM.grid(db.tesis_research_areas, maxtextlength=75)
    return dict(grid=grid)

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Tesis-Administrator'))
def status():
    grid = SQLFORM.grid(db.tesis_status, maxtextlength = 75)
    return dict(grid=grid)

@auth.requires_login()
@auth.requires(auth.has_membership('Super-Administrator') or auth.has_membership('Tesis-Administrator'))
def tutor():
    grid = SQLFORM.grid(db.tesis_tutor)
    return dict(grid=grid)

def get_name_student():
    num_carnet = request.vars.num_carnet
    if num_carnet:
        ds_student = db(db.auth_user.username == num_carnet).select(db.auth_user.first_name, db.auth_user.last_name).first()
        if ds_student:
            return f'{ds_student.first_name} {ds_student.last_name}'

    return ''

def sqlform_grid_topics():
    #ESTUDIANTES
    query_s = (db.tesis_asigned_topics.student == db.auth_user.username)
    order_by_s = (db.auth_user.username)

    db.auth_user.username.label = 'Carnet'
    db.auth_user.first_name.label = 'Nombres'
    db.auth_user.last_name.label = 'Apellidos'

    fields_s = [
        db.auth_user.username,
        db.auth_user.first_name,
        db.auth_user.last_name,
        db.auth_user.email,
        db.auth_user.phone,
        db.tesis_asigned_topics.status,
        db.tesis_asigned_topics.tutor,
        db.tesis_asigned_topics.adviser,
        db.tesis_asigned_topics.topic_name,
        db.tesis_asigned_topics.topic_modality,
        db.tesis_asigned_topics.topic_area,
        db.tesis_asigned_topics.topic_description,
        db.tesis_asigned_topics.topic_protocol,
        db.tesis_asigned_topics.file1,
        db.tesis_asigned_topics.topic_date_approval,
        db.tesis_asigned_topics.topic_date_validity,
        db.tesis_asigned_topics.topic_date_reactivation
    ]

    return SQLFORM.grid(
        query=query_s,
        fields=fields_s,
        orderby=order_by_s,
        searchable=True,
        sortable=True,
        paginate=20,
        deletable=False,
        editable=False,
        create=False,
        details=False,
        search_widget='default',
        _class="web2py_grid",
        formname='grid1',
        maxtextlength=100
    )

def sqlform_grid_all_students():
    query_s = ((db.auth_user.id == db.auth_membership.user_id) & (db.auth_membership.group_id == 5))
    order_by_s = (db.auth_user.username)
    
    db.auth_user.username.label = 'Carnet'
    db.auth_user.first_name.label = 'Nombres'
    db.auth_user.last_name.label = 'Apellidos'
    
    fields_s = [
        db.auth_user.username,
        db.auth_user.first_name,
        db.auth_user.last_name,
        db.auth_user.email,
        db.auth_user.phone,
        db.auth_user.home_address
    ]

    return SQLFORM.grid(
        query=query_s,
        fields=fields_s,
        orderby=order_by_s,
        searchable=True,
        sortable=True,
        paginate=20,
        deletable=False,
        editable=False,
        create=False,
        details=False,
        search_widget='default',
        _class="web2py_grid",
        formname='grid2',
        maxtextlength=50
    )

def make_html():
    primer_nivel = db(db.tesis_research_areas.parent_research_area == None).select(db.tesis_research_areas.name, db.tesis_research_areas.id)
    if primer_nivel:
        html = ''
        for row in primer_nivel:
            html += f'{recursive_child(row)}</br>'
    else:
        html = '<h3>No existen datos</h3>'

    return html

def recursive_child(fila, indentation=''):
    html = f'{indentation}<b>&emsp;&#164;&emsp;{fila.name.upper()}</b><br>'
    children = db(db.tesis_research_areas.parent_research_area == fila.id).select(db.tesis_research_areas.id, db.tesis_research_areas.name)
    for child in children:
        html += recursive_child(child, f'{indentation}&emsp;&emsp;')

    return html
