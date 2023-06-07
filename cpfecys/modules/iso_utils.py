# -*- coding: utf-8 -*-
"""
retorna un string para realizar una consulta donde obtenemos
el id del proyecto, codigo del proyecto, nombre y la cantidad de
incidentes por cada curso
"""
def iso_get_incidentes_curso(id_periodo):
    query = """
        SELECT up.project,
	    au.username as carnet,
	    au.first_name,
	    au.last_name,
	    p.id as id_project,
	    p.name as curso,
	    (
		    SELECT COUNT(*) 
		    FROM iso_incidente ii
		    WHERE ii.id_project = up.project
		    	AND ii.id_period = up.period
				AND ii.id_tutor = au.id
	    ) as incidentes,
		au.id as id_tutor
        FROM user_project up,
	    auth_membership am,
	    project p,
	    auth_user au
	    WHERE up.period = %s 
		    AND p.id = up.project 
		    AND am.user_id = up.assigned_user 
		    AND am.group_id = 5 
		    AND au.id = am.user_id 
		    ORDER BY project """%(id_periodo)

    return query


"""
Crea el query para consultar si un estudiante ya lleno la evaluación de
rendimiento del curso que se especifíca en el parametro
"""
def iso_get_encuesta(id_user, id_project, id_period):
    query = """SELECT ier.id, ier.fecha_inicio, ier.fecha_fin,
        iec.id AS id_evrc,
        au.id AS id_aux,
        au.first_name,
        au.last_name,
        ( SELECT COUNT(1) 
        FROM iso_pregunta ip
        WHERE ip.id_ev_rendimiento = ier.id 
        GROUP BY ip.id_ev_rendimiento) as 'preguntas',
        ( SELECT COUNT(1)
          FROM iso_respuesta_estudiante ire
          WHERE ire.id_evr_curso = iec.id 
          AND ire.id_auth_user = %s
          GROUP BY ire.id_auth_user) as 'respuestas'
    FROM user_project up,
        auth_user au,
        auth_membership am,
        iso_evr_curso iec,
        iso_ev_rendimiento ier
    WHERE up.project = %s
        AND up.period = %s
        AND au.id = up.assigned_user
        AND am.user_id = au.id
        AND am.group_id = 2
        AND iec.user_project_id = up.id
        AND ier.id = iec.iso_encuesta_id
        AND ier.fecha_inicio <= NOW()
        AND ier.fecha_fin >= NOW()"""%(id_user, id_project, id_period)
    return query


def get_pregunta(id_evr, id_uproject, id_user):
    query = """SELECT ip.*
    FROM iso_pregunta ip,
    iso_evr_curso iec
    WHERE ip.id_ev_rendimiento = %s
        AND iec.iso_encuesta_id = ip.id_ev_rendimiento
        AND iec.user_project_id = %s
        AND ip.id NOT IN (
            SELECT ire.id_pregunta
            FROM iso_respuesta_estudiante ire
            WHERE ire.id_auth_user = %s
                AND ire.id_evr_curso = iec.id
        )
    """%(id_evr, id_uproject, id_user)
    return query


def iso_get_ev_respuesta(id_ev_rendimiento, id_pregunta):
    query = """SELECT Sum(valor) as suma, valor from iso_respuesta 
    where iso_encuesta_curso_id = %s and iso_pregunta_id=%s group by valor"""%(id_ev_rendimiento,id_pregunta)

    return query


def iso_get_respuesta_cualitativa(id_ev_rendimiento, id_pregunta):
    query = """SELECT ips.descripcion,
		ir.valor,
		count(1) as cantidad,
		ir.iso_pregunta_seleccion_id
		from iso_respuesta ir
   			INNER JOIN iso_pregunta_seleccion ips  ON ips.id = ir.iso_pregunta_seleccion_id 
		WHERE ir.iso_encuesta_curso_id = %s AND ir.iso_pregunta_id = %s GROUP BY ir.valor"""%(id_ev_rendimiento, id_pregunta)

    return query


def iso_get_respuesta_comentario(id_ev_rendimiento, id_pregunta):
    query= """SELECT respuesta from iso_respuesta 
    where iso_encuesta_curso_id =%s and iso_pregunta_id=%s"""%(id_ev_rendimiento,id_pregunta)

    return query


def iso_resultado_evr(id_evr, id_project, periodo):
    query = """
        SELECT
	    up.id,
	    p.name,
	    au.username,
	    au.first_name,
	    au.last_name,
	    (
	    SELECT
    		ROUND(SUM(r2.promedio), 2) as puntos
	    FROM
	    	(
	    	SELECT
	    		r1.iso_encuesta_curso_id,
	    		r1.iso_pregunta_id,
	    		r1.puntos / r1.respuestas as promedio
	    	FROM
	    		(
	    		SELECT
	    			ir.iso_encuesta_curso_id,
	        			ir.iso_pregunta_id,
	    			SUM(ir.valor) as puntos,
	    			COUNT(1) as respuestas
	    		from
	    			iso_respuesta ir,
	        			iso_evr_curso iec
	    		WHERE
	    			ir.iso_encuesta_curso_id = iec.id
	    		GROUP by
	    			ir.iso_pregunta_id,
	    			ir.iso_encuesta_curso_id
        ) r1 ) r2
	    WHERE
	    	r2.iso_encuesta_curso_id = iec.id
	    GROUP BY
		    r2.iso_encuesta_curso_id) AS puntos,
	    iec.id as id_evr,
		iec.iso_encuesta_id """

    if id_project:
        query += ",ier.nombre as enc \n"

    query += """ FROM
	    iso_evr_curso iec,
	    user_project up,
	    project p,
	    auth_user au
     """

    if not id_project:
        query += """
        WHERE up.assigned_user = au.id
	        AND up.project = p.id
	        AND up.id = iec.user_project_id
	        AND iec.iso_encuesta_id = %s"""%(id_evr)
    else:
        query += """
         ,iso_ev_rendimiento ier
	        WHERE up.assigned_user = au.id
    		AND ier.id = iec.iso_encuesta_id
	        AND up.project = p.id
	        AND up.id = iec.user_project_id
	        AND p.id = %s
	        AND ier.id_period_year = %s"""%(id_project, periodo)

    return query


def iso_get_tutores(id_project, id_period):
    query = """
    SELECT au.id,
	    au.first_name,
	    au.last_name
    FROM user_project up,
	    auth_membership am,
	    auth_user au 
    WHERE up.project = %s 
        AND up.period = %s 
        AND am.user_id = up.assigned_user 
        AND au.id = up.assigned_user 
        AND am.group_id = 5 """%(id_project, id_period)

    return query

def iso_get_punteo(iso_encuesta_id, top, orden):
	query = """
	SELECT ire.id,
		ire.name,
		ire.username,
		ire.first_name,
		ire.last_name,
		ire.puntos
	FROM iso_resultado_evr ire 
	WHERE ire.iso_encuesta_id = %s
	ORDER BY ire.puntos %s LIMIT %s """%(iso_encuesta_id, orden, top)

	return query

def iso_get_valor_encuesta(id_ev):
	query = """
	SELECT SUM(ip.valor) 
	FROM iso_pregunta ip 
	WHERE ip.id_ev_rendimiento = %s"""%(id_ev)

	return query

def iso_get_count_completas(id_ev):
	query = """
	SELECT r3.completas, r3.id_evr_curso,p.name,
    CONCAT(au.first_name, " ", au.last_name) as Nombre, r3.iniciadas
    FROM 
    (SELECT SUM(r2.completadas) as completas, SUM(r2.iniciadas) as iniciadas, r2.id_evr_curso from (
    SELECT if(r.respuestas = r.preguntas, 1 , 0) as completadas,
	if(r.respuestas <> 0, 1, 0) as iniciadas, 
    r.id_evr_curso from (
    SELECT COUNT(1) as respuestas, id_evr_curso,
    (SELECT COUNT(1) 
	FROM iso_pregunta ip 
	WHERE ip.id_ev_rendimiento = iec.iso_encuesta_id) as preguntas
    FROM  iso_respuesta_estudiante ire, iso_evr_curso iec 
    WHERE ire.id_evr_curso = iec.id 
    AND iec.iso_encuesta_id = %s
    GROUP BY ire.id_auth_user, id_evr_curso ) r)r2 GROUP BY r2.id_evr_curso) r3,
    user_project up, iso_evr_curso ic, project p, auth_user au
	WHERE r3.id_evr_curso= ic.id AND up.id=ic.user_project_id  
	AND up.project= p.id AND up.assigned_user = au.id"""%(id_ev)

	return query


def iso_get_count_cualitavivas(id_evr):
	query = """SELECT COUNT(1) 
			from ( 
			SELECT ip.id,
			(
				SELECT COUNT(1)
				FROM iso_pregunta_seleccion ips 
				WHERE ips.iso_pregunta_id = ip.id 
			) as opciones
			FROM iso_pregunta ip
			WHERE ip.iso_tipo_pregunta_id = 2 
				AND ip.id_ev_rendimiento = %s) AS r
			WHERE r.opciones = 0"""%id_evr
	
	return query