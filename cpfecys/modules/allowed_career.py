# -*- coding: utf-8 -*-

def validar(db):
    """
    Recibe como parametro el 'DAL' de w2py para realizar la consulta de que
    carreras estan permitidas retorna una función para evitar multiples
    consultas a la base de datos
    """
    datos = db(db.validate_career).select()

    def val(unidad="08", extension="00", carrera="09"):
        """
        Recibe como parametros los codigos de  unidad, extension
        y carrera del nuevo alumno retorna True si el alumno esta inscrito en
        alguna de las carreras que estan permitidas, segun el catalogo de
        allowed_career
        """
        valido = False
        for d in datos:
            valido = d.unit == unidad and d.extension == extension and carrera == carrera
            if valido:
                break

        return valido

    return val
