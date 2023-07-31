ruta_iconos = "/cpfecys/static/images/iconos_reclutamiento"
KEY = "3cy5_d11"
import random
from gluon.contrib.pysimplesoap.client import SoapClient
from gluon.contrib.pysimplesoap.client import SimpleXMLElement
import cpfecys
import xml.etree.ElementTree as ET
import allowed_career as validator_career

# Primer paso para guardar la solicitud
def solicitar():
    mensaje = ''
    form = FORM(
        INPUT(
            _name="id_registro",
            _id="id_registro",
            _type="number",
            _min="0",
            _class='form-control',
            requires=IS_NOT_EMPTY(),
        ),
        P(),
        BUTTON(
            I(_class="icon-ok-sign icon-white"),
            " Enviar solicitud",
            _type="submit",
            _class="btn btn-primary",
        ),
        _class="form-search",
    )
    if form.accepts(request.vars, formname="form"):
        carnet_buscar = form.vars.id_registro
        usr_tb_user = db(db.auth_user.username == carnet_buscar).select(db.auth_user.id).first()
        usr_tb_solicitar = db(db.rec_registro.carnet == carnet_buscar).select(db.rec_registro.id).first()
        usr_webservice = check_id(carnet_buscar)

        if ((usr_tb_user is None) & (usr_tb_solicitar is None)
        & (usr_webservice["flag"])):
            redirect(
                URL(
                    "reclutamiento_registro_nuevo",
                    "confirmar_info",
                    vars=dict(
                        wb_id_register=str(carnet_buscar),
                        wb_email=str(usr_webservice["correo"]),
                        wb_firstname=str(usr_webservice["nombres"]),
                        wb_lastname=str(usr_webservice["apellidos"]),
                    ),
                    hmac_key=KEY,
                )
            )
        else:
            mensaje = "El carnet es inválido"
    elif form.errors:
        mensaje = "El formulario tiene errores"

    return dict(form=form, ruta_iconos=ruta_iconos, mensaje=mensaje)

# Segundo paso para guardar la solicitud
def confirmar_info():
    wb_id_register = request.vars.wb_id_register
    wb_email = request.vars.wb_email
    wb_firstname = request.vars.wb_firstname
    wb_lastname = request.vars.wb_lastname

    if not URL.verify(request, hmac_key=KEY):
        redirect(URL("default", "home"))

    if ((wb_id_register is not None) & (wb_email is not None)
    & (wb_firstname is not None) & (wb_lastname is not None)):
        form = FORM(
            INPUT(
                _name="inp_email",
                _id="inp_email",
                _type="email",
                _value=str(wb_email),
                _class='form-control',
                requires=IS_NOT_EMPTY(),
            ),
            P(),
            LABEL(B("Fotografia"), _style="color: #696969;"),
            P(),
            IMG(_src=ruta_iconos + "/profile.png", _height="24", _width="24"),
            INPUT(
                _name="inp_photo",
                _type="file",
                _class='form-control',
                requires=[
                    IS_NOT_EMPTY(),
                    IS_IMAGE(
                        extensions=("jpeg", "png"),
                        maxsize=(200, 300),
                        error_message=T(
                            "Only files are accepted with extension png|jpg with 200x300px size."
                        ),
                    ),
                ],
            ),
            P(),
            BUTTON(
                I(_class="icon-ok-sign icon-white"),
                " Enviar solicitud",
                _type="submit",
                _class="btn btn-primary",
            ),
            _class="form-search",
        )

        if form.accepts(request.vars, formname="form"):
            usr_tb_user = db(db.auth_user.username == wb_id_register).select(db.auth_user.id).first()
            usr_tb_solicitar = db(db.rec_registro.carnet == wb_id_register).select(db.rec_registro.id).first()

            if (usr_tb_user is None) & (usr_tb_solicitar is None):
                db.rec_registro.insert(
                    carnet=wb_id_register,
                    nombre=wb_firstname,
                    apellido=wb_lastname,
                    password=str(random.randint(10000000, 99000000)),
                    correo=form.vars.inp_email,
                    fotografia=form.vars.inp_photo,
                    estado=3,
                )
                session.flash = "Se registro la solicitud"
                redirect('/')
            else:
                session.flash = "Ocurrio un error, contacte al administrador"
                redirect('/')

        elif form.errors:
            response.flash = "El formulario tiene errores"
        return dict(form=form, ruta_iconos=ruta_iconos)
    else:
        redirect('/')

def check_id(check_carnet):
    svp = db(db.validate_student).select(
                db.validate_student.supplier,
                db.validate_student.action_service,
                db.validate_student.type_service,
                db.validate_student.send,
                db.validate_student.receive
            ).first()
    if svp is not None:
        try:
            client = SoapClient(
                location=svp.supplier,
                action=f'{svp.supplier}/{svp.action_service}',
                namespace=svp.supplier,
                soap_ns=svp.type_service,
                trace=True,
                ns=False
            )

            year = cpfecys.current_year_period()
            sent = f"<{svp.send}>"
            svpfs = db(db.validate_student_parameters).select(
                        db.validate_student_parameters.parameter_name_validate,
                        db.validate_student_parameters.parameter_value_validate,
                    )
            for svpf in svpfs:
                sent += f"<{svpf.parameter_name_validate}>{svpf.parameter_value_validate}</{svpf.parameter_name_validate}>"
            sent += f"<CARNET>{check_carnet}</CARNET><CICLO>{year.yearp}</CICLO></{svp.send}>"

            back = client.call(svp.action_service, xmlDatos=sent)
            #PREPARE FOR RETURNED XML WEB SERVICE
            xml = back.as_xml()
            xml = xml.decode('utf-8')
            xml = xml.replace('&lt;', '<')
            xml = xml.replace('&gt;', '>')
            inicio = xml.find(f"<{svp.receive}>")
            final = xml.find(f"</{svp.receive}>")
            xml = xml[inicio : (final + len(f'</{svp.receive}>'))]

            root = ET.fromstring(xml)
            xml = SimpleXMLElement(xml)

            #VARIABLE TO CHECK THE CORRECT FUNCTIONING
            CARNET = xml.CARNET
            NOMBRES = xml.NOMBRES
            APELLIDOS = xml.APELLIDOS
            CORREO = xml.CORREO

            #Unicode Nombres
            def get_real_values(text):
                text_return = ''
                try:
                    for word in str(text).split(' '):
                        word = word.replace('Ã¡','á').replace('Ã©','é').replace('Ã­','í').replace('Ã³','ó').replace('Ãº','ú').replace('Ã±','ñ').replace('Ã','Á').replace('Ã‰','É').replace('Ã','Í').replace('Ã“','Ó').replace('Ãš','Ú').replace('Ã‘','Ñ').replace('Ã¼‘','ü')
                        text_return += f'{word} '
                    return text_return.strip()
                except:
                    return text_return
            
            NOMBRES = get_real_values(NOMBRES)
            APELLIDOS = get_real_values(APELLIDOS)

            if (CARNET is None or CARNET == '') and (NOMBRES is None or NOMBRES == '') and (APELLIDOS is None or APELLIDOS == '') and (CORREO is None or CORREO == ''):
                return dict(flag=False, error=False, message=T('The record was removed because the user is not registered to the academic cycle'))
            else:
                val = validator_career.validar(db)
                is_student = False
                for c in root.findall('CARRERA'):
                    unidad = c.find('UNIDAD').text
                    extension = c.find('EXTENSION').text
                    carrera = c.find('CARRERA').text
                    is_student = val(unidad=unidad, extension=extension, carrera=carrera)
                    if is_student:
                        break

                if not is_student:
                    return dict(flag=False, error=False, message=T('The record was removed because students not enrolled in career allowed to use the system'))
                else:
                    return dict(flag=True, carnet=int(str(CARNET)), nombres=NOMBRES, apellidos=APELLIDOS, correo=str(CORREO), error=False)
        except Exception as e:
            return dict(flag=False, error=True, message=T('Error with web service validation'))
    else:
        return dict(flag=False, error=True, message=T('Error with web service validation 2'))
