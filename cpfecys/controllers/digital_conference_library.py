# coding: utf8
import datetime

import cpfecys
import dsi_queries as queries

def index():
    teacher_info = ''
    if request.vars['id']:
        id_teacher = request.vars['id']
        teacher_info = db((db.perfil_catedratico.id == id_teacher) &
                          (db.perfil_catedratico.estado == 'activo')).select().first()
        lista_formacion = teacher_info.formacion.split(',')
        teacher_info.formacion = lista_formacion

    return dict(
        teacher_info = teacher_info,
        titulo = 'hola desde el index de la libreria',
    )