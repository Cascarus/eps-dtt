import json
import iso_utils


@auth.requires(auth.has_membership("Super-Administratos") or auth.has_membership("DSI"))
@request.restful()
def pregunta():
    response.view = "generic.json"
    response.headers["Content-Type"] = "application/json"

    def POST(*args, **vars):
        datos = {
            "descripcion": vars["descripcion"],
            "valor": vars["valor"],
            "iso_tipo_pregunta_id": vars["iso_tipo_pregunta_id"],
            "id_ev_rendimiento": vars["id_ev_rendimiento"],
        }
        id_pregunta = dict(db.iso_pregunta.validate_and_insert(**datos))

        return id_pregunta

    def GET(*args, **vars):
        datos = None
        data = len(args)
        if data == 0:
            raise HTTP(404)
        elif data == 1:
            datos = db((db.iso_pregunta.id_ev_rendimiento == args[0])).select(
                db.iso_pregunta.id,
                db.iso_pregunta.descripcion,
                db.iso_pregunta.valor,
                db.iso_pregunta.iso_tipo_pregunta_id,
            )
        elif data == 2:
            datos = db(
                (db.iso_pregunta.id_ev_rendimiento == args[0])
                & (db.iso_pregunta.id == args[1])
            ).select(
                db.iso_pregunta.id,
                db.iso_pregunta.descripcion,
                db.iso_pregunta.valor,
                db.iso_pregunta.iso_tipo_pregunta_id,
            )
        else:
            raise HTTP(400)

        rst = [
            {
                "id": x.id,
                "descripcion": x.descripcion,
                "valor": x.valor,
                "tipo_pregunta": x.iso_tipo_pregunta_id,
            }
            for x in datos
        ]
        return json.dumps(rst)

    def PUT(*args, **vars):
        resultado = db(db.iso_pregunta.id == vars["id"]).update(
            descripcion=vars["descripcion"], valor=vars["valor"]
        )

        return {"resultado": resultado}

    def DELETE(*args, **vars):
        pregunta = db(db.iso_pregunta.id == vars["id"]).select().first()

        if pregunta is None:
            raise HTTP(400)

        if pregunta.iso_tipo_pregunta_id == 2:
            db(db.iso_pregunta_seleccion.iso_pregunta_id == vars["id"]).delete()

        resultado = db(db.iso_pregunta.id == vars["id"]).delete()
        return resultado

    return locals()


@auth.requires(auth.has_membership("Super-Administratos") or auth.has_membership("DSI"))
@request.restful()
def respuesta():
    response.view = "generic.json"
    response.headers["Content-Type"] = "application/json"

    def POST(*args, **vars):
        datos = {
            "descripcion": vars["descripcion"],
            "punteo": vars["punteo"],
            "iso_pregunta_id": vars["iso_pregunta_id"],
        }

        id_resp = dict(db.iso_pregunta_seleccion.validate_and_insert(**datos))

        return id_resp

    def GET(*args, **vars):
        datos = None

        if len(args) == 0:
            raise HTTP(400)

        datos = db((db.iso_pregunta_seleccion.iso_pregunta_id == args[0])).select()

        rst = [
            {
                "id": x.id,
                "idp": x.iso_pregunta_id,
                "descripcion": x.descripcion,
                "punteo": x.punteo,
            }
            for x in datos
        ]

        return json.dumps(rst)

    def PUT(*args, **vars):
        resultado = db(db.iso_pregunta_seleccion.id == vars["id"]).update(
            descripcion=vars["descripcion"], punteo=vars["punteo"]
        )

        return {"resultado": resultado}

    def DELETE(*args, **vars):
        resultado = db(db.iso_pregunta_seleccion.id == vars["id"]).delete()
        return {"resultado": resultado}

    return locals()


@auth.requires(auth.has_membership("Academic"))
@request.restful()
def pregunta_estudiante():
    response.view = "generic.json"
    response.headers["Content-Type"] = "application/json"

    def GET(*args, **vars):
        if len(args) != 2:
            raise HTTP(404)

        query = iso_utils.get_pregunta(args[0], args[1], auth.user.id)
        datos = db.executesql(query)
        rst = [
            {"id": x[0], "descripcion": x[1] + "", "valor": x[2], "tipo_pregunta": x[3]}
            for x in datos
        ]

        return json.dumps(rst)

    return locals()


@auth.requires(auth.has_membership("Academic"))
@request.restful()
def respuesta_estudiante():
    response.view = "generic.json"
    response.headers["Content-Type"] = "application/json"

    def GET(*args, **vars):
        datos = None

        if len(args) == 0:
            raise HTTP(400)

        valores = ",".join(args)
        query = (
            """
            SELECT * 
            FROM iso_pregunta_seleccion ips 
            WHERE ips.iso_pregunta_id in (%s)"""
            % valores
        )

        datos = db.executesql(query)

        rst = [
            {"id": x[0], "idp": x[3], "descripcion": x[1], "punteo": x[2]}
            for x in datos
        ]

        return json.dumps(rst)

    def POST(*args, **vars):
        resultado = []
        preguntas = vars["preguntas"]

        for i in range(int(preguntas)):
            resp_est = {
                "id_pregunta": int(vars["id_pregunta" + str(i)]),
                "id_auth_user": auth.user.id,
                "id_evr_curso": int(vars["id_evr_curso" + str(i)]),
            }

            id_resp_rest = None
            try:
                id_resp_rest = dict(
                    db.iso_respuesta_estudiante.validate_and_insert(**resp_est)
                )
            except:
                rst = {"id_iso_respuesta": 0, "id_iso_respuesta_estudiante": 0}
                resultado.append(rst)
                continue

            comentario = None
            id_respuesta = None
            if vars["respuesta" + str(i)]:
                comentario = vars["respuesta" + str(i)]

            if vars["id_respuesta" + str(i)]:
                id_respuesta = int(vars["id_respuesta" + str(i)])

            iso_resp = {
                "valor": int(vars["valor" + str(i)]),
                "respuesta": comentario,
                "iso_encuesta_curso_id": int(vars["id_evr_curso" + str(i)]),
                "iso_pregunta_id": int(vars["id_pregunta" + str(i)]),
                "iso_pregunta_seleccion_id": id_respuesta,
            }

            id_iso_resp = 0
            try:
                id_iso_resp = dict(db.iso_respuesta.validate_and_insert(**iso_resp))
            except:
                rst = {"id_iso_respuesta": 0, "id_iso_respuesta_estudiante": 0}
                continue

            rst = {
                "id_iso_respuesta": id_resp_rest["id"],
                "id_iso_respuesta_estudiante": id_iso_resp["id"],
            }

            resultado.append(rst)

        return json.dumps({"estado": "hecho", "resultado": resultado})

    return locals()
