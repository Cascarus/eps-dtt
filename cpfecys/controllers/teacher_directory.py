# coding: utf8
import datetime

import cpfecys
import dsi_queries as queries

def home_teacher_directory():
    catedraticos = db(db.perfil_catedratico.estado == 'activo').select()

    cursos_temp = db.executesql("""
        SELECT DISTINCT	
            TRIM(BOTH ' ' FROM 
                CASE 
                    WHEN LOCATE('(', p.name) > 0 AND LOCATE(')', p.name) > 0
                        THEN CONCAT(SUBSTRING(p.name, 1, LOCATE('(', p.name) - 1), SUBSTRING(p.name, LOCATE(')', p.name) + 1))
                    ELSE p.name
                END
            ) AS name
        FROM project p 
        WHERE p.project_id NOT LIKE 'PV%';
    """)

    cursos = []

    for c in cursos_temp:
        if ((c[0] != 'Analisis y Diseño de Sistems 1') & (c[0] != 'Arquitectura de Computadores y Ensambladores 2')):
            curso_temp = {
                'nombre': c[0],
                'cheked': 'false',
            }
            objeto = type('Objeto', (object,), curso_temp)
            cursos.append(objeto)
    
    
    if request.post_vars.filtros:  #aqui se realiza el filtrado
        filtros_parametro = request.post_vars.filtros
        for fil in filtros_parametro:
            for cur in cursos:
                if(cur.nombre == fil):
                    cur.cheked = 'true'

    
    return dict(
        catedraticos = catedraticos,
        cursos = cursos,
    )