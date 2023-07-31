from calendar import month
import dsa_utils
import datetime
import gluon.contenttype as contenttype
from gluon.contrib.pysimplesoap.client import SoapClient
from gluon.contrib.pysimplesoap.client import SimpleXMLElement
import cpfecys
import xml.etree.ElementTree as ET
import allowed_career as v

# Inicio - practicas finales(DSA) - Jose Carlos I Alonzo Colocho


@auth.requires_login()
@auth.requires_membership("Documents-ECYS")
def documents_view_individual():
    args = request.args
    new_dict = {}

    def set_upload_form(
        documentType,
        carnetForm,
        nombre,
        apellido,
        username,
        documentDelivered,
        correoForm,
    ):
        display = "none"
        subir = "Subir Archivo"
        extensions = get_extensions_modified(documentType)

        extensions_principal = extensions[0]
        size_principal = 0
        message_size_principal = ""

        extensions_complement = extensions[1]
        size_complement = 0
        message_size_complement = ""

        query = dsa_utils.get_complement_or_no(documentType)
        is_complement = db.executesql(query, as_dict=True)
        is_complement = is_complement[0]["complement_required"]

        query = dsa_utils.get_document_type(documentType)
        document = db.executesql(query, as_dict=True)
        message_size_principal = "El tamaño maximo del archivo es de {} MB".format(
            document[0]["max_size"]
        )
        size_principal = document[0]["max_size"] * 1024 * 1024

        upload_form = FORM(
            INPUT(
                _class="form-control",
                _name="inputDocumentType",
                _value=documentType,
                _style="display: none;",
            ),
            INPUT(
                _class="form-control",
                _name="inputStudent",
                _value=username,
                _style="display: none;",
            ),
            INPUT(
                _class="form-control",
                _name="update",
                _value="0",
                _style="display: none;",
            ),
            INPUT(
                _class="form-control",
                _name="nombreForm",
                _value=nombre,
                _style="display: none;",
            ),
            INPUT(
                _class="form-control",
                _name="apellidoForm",
                _value=apellido,
                _style="display: none;",
            ),
            INPUT(
                _class="form-control",
                _name="carnetForm",
                _value=carnetForm,
                _style="display: none;",
            ),
            INPUT(
                _class="form-control",
                _name="documentDelivered",
                _value=documentDelivered,
                _style="display: none;",
            ),
            INPUT(
                _class="form-control",
                _name="correoForm",
                _value=correoForm,
                _style="display: none;",
            ),
            DIV(
                LABEL(
                    "Principal", _for="inputPrincipal", _class="col-sm-3 col-form-label"
                ),
                DIV(
                    INPUT(
                        _type="file",
                        _class="form-control-file",
                        _name="inputPrincipal",
                        _id="inputPrincipal",
                        _style="margin-top:5px;",
                        requires=[
                            IS_NOT_EMPTY(
                                error_message="Debe seleccionar un archivo a subir."
                            ),
                            IS_UPLOAD_FILENAME(
                                extension=str(extensions_principal),
                                error_message="Tipo de archivo no permitido.",
                            ),
                            IS_LENGTH(
                                size_principal, error_message=message_size_principal
                            ),
                        ],
                    ),
                    _class="col-sm-9",
                ),
                _class="form-group row",
            ),
            BUTTON(
                SPAN(_class="fa fa-upload"),
                subir,
                _type="submit",
                _class="btn btn-primary",
            ),
        )

        if is_complement == 1:
            display = ""
            subir = "Subir Archivos"
            message_size_complement = "El tamaño maximo del archivo es de {} MB".format(
                document[0]["complement_size"]
            )
            size_complement = document[0]["complement_size"] * 1024 * 1024
            upload_form = FORM(
                INPUT(
                    _class="form-control",
                    _name="inputDocumentType",
                    _value=documentType,
                    _style="display: none;",
                ),
                INPUT(
                    _class="form-control",
                    _name="inputStudent",
                    _value=username,
                    _style="display: none;",
                ),
                INPUT(
                    _class="form-control",
                    _name="update",
                    _value="0",
                    _style="display: none;",
                ),
                INPUT(
                    _class="form-control",
                    _name="nombreForm",
                    _value=nombre,
                    _style="display: none;",
                ),
                INPUT(
                    _class="form-control",
                    _name="apellidoForm",
                    _value=apellido,
                    _style="display: none;",
                ),
                INPUT(
                    _class="form-control",
                    _name="carnetForm",
                    _value=carnetForm,
                    _style="display: none;",
                ),
                INPUT(
                    _class="form-control",
                    _name="documentDelivered",
                    _value=documentDelivered,
                    _style="display: none;",
                ),
                INPUT(
                    _class="form-control",
                    _name="correoForm",
                    _value=correoForm,
                    _style="display: none;",
                ),
                DIV(
                    LABEL(
                        "Principal",
                        _for="inputPrincipal",
                        _class="col-sm-3 col-form-label",
                    ),
                    DIV(
                        INPUT(
                            _type="file",
                            _class="form-control-file",
                            _name="inputPrincipal",
                            _id="inputPrincipal",
                            _style="margin-top:5px;",
                            requires=[
                                IS_NOT_EMPTY(
                                    error_message="Debe seleccionar un archivo a subir."
                                ),
                                IS_UPLOAD_FILENAME(
                                    extension=str(extensions_principal),
                                    error_message="Tipo de archivo no permitido.",
                                ),
                                IS_LENGTH(
                                    size_principal, error_message=message_size_principal
                                ),
                            ],
                        ),
                        _class="col-sm-9",
                    ),
                    _class="form-group row",
                ),
                DIV(
                    LABEL(
                        "Complemento",
                        _for="inputComplement",
                        _class="col-sm-3 col-form-label",
                    ),
                    DIV(
                        INPUT(
                            _type="file",
                            _class="form-control-file",
                            _name="inputComplement",
                            _id="inputComplement",
                            _style="margin-top:5px;",
                            requires=[
                                IS_NOT_EMPTY(
                                    error_message="Debe seleccionar un archivo a subir."
                                ),
                                IS_UPLOAD_FILENAME(
                                    extension=str(extensions_complement),
                                    error_message="Tipo de archivo no permitido.",
                                ),
                                IS_LENGTH(
                                    size_complement, error_message=message_size_complement
                                ),
                            ],
                        ),
                        _class="col-sm-9",
                    ),
                    _class="form-group row",
                    _style="display: " + display + ";",
                ),
                BUTTON(
                    SPAN(_class="fa fa-upload"),
                    subir,
                    _type="submit",
                    _class="btn btn-primary",
                ),
            )

        new_dict["carnet"] = carnetForm
        new_dict["nombre"] = nombre
        new_dict["apellidos"] = apellido
        new_dict["correo"] = correoForm
        new_dict["form"] = True
        query = dsa_utils.get_name_and_role_from_document(documentType)
        role_and_name = db.executesql(query, as_dict=True)
        role_and_name = role_and_name[0]
        new_dict["role"] = role_and_name["role"]
        new_dict["documentName"] = role_and_name["name"]

        # eliminar el existente
        if upload_form.accepts(request.vars, formname="upload_form"):
            name_complement = ""
            flag_complement = False
            if request.vars.inputPrincipal is not None:
                name = "linguistica-" + request.vars.carnetForm

                name_principal = dsa_utils.save_file(
                    request.vars.inputPrincipal.file,
                    request.vars.inputPrincipal.filename,
                    request.folder,
                    name,
                )
                if is_complement == 1:
                    complement_name = "linguistica-" + request.vars.carnetForm
                    name_complement = dsa_utils.save_file(
                        request.vars.inputComplement.file,
                        request.vars.inputComplement.filename,
                        request.folder,
                        complement_name,
                    )
                    if name_complement is not None:
                        flag_complement = True
                else:
                    flag_complement = True

                if name_principal is not None and flag_complement:
                    values = {
                        "principal": name_principal,
                        "complement": name_complement,
                    }
                    try:
                        delete_query = dsa_utils.get_file_and_file_complement(
                            documentDelivered
                        )
                        old_documents = db.executesql(
                            delete_query, as_dict=True)

                        if len(old_documents) > 0:
                            old_documents = old_documents[0]
                            if old_documents["file_uploaded"] != "":
                                dsa_utils.remove_file(
                                    old_documents["file_uploaded"], request.folder
                                )

                            if old_documents["complement_uploaded"] != "":
                                dsa_utils.remove_file(
                                    old_documents["complement_uploaded"], request.folder
                                )

                        query = dsa_utils.update_document_delivered(
                            values, documentDelivered
                        )
                        db.executesql(query)
                        session.flash = "Archivos actualizados correctamente"
                    except Exception as e:
                        print("********** student - stationery **********")
                        print(str(e))
                        session.flash = "No se pudo guardar el archivo"

                    redirect(
                        URL(
                            "documents_ecys",
                            "documents_view_individual",
                            args=["search"],
                            vars={"inputStudent": carnetForm},
                        )
                    )
                else:
                    new_dict["message"] = "Error al guardar el archivo principal"

            else:
                new_dict["message"] = "Debe seleccionar un archivo a subir."

        return dict(action=new_dict, form=upload_form)

    if len(args) != 0:
        option = args[0]
        if option == "search":
            vars = request.vars

            query = dsa_utils.get_documents_per_student(
                vars["inputStudent"], auth.user.id
            )
            new_dict["documents"] = db.executesql(query, as_dict=True)
            new_dict["student"] = vars["inputStudent"]
        elif option == "download_individual":
            query = dsa_utils.get_signed_file(request.vars.documentId)
            signed_file = db.executesql(query, as_dict=True)
            signed_file = signed_file[0]["signed_file"]

            try:
                file = dsa_utils.retrieve_file(signed_file, request.folder)
                query_update = dsa_utils.update_downloaded_status(
                    request.vars.documentId
                )
                db.executesql(query_update)
            except Exception as e:
                print("********** admin - download deliverable **********")
                print(str(e))
                session.flash = "No se econtro el archivo"
                redirect(URL("documents_ecys", "documents_view"))

            response.headers["Content-Type"] = contenttype.contenttype(
                signed_file)
            response.headers["Content-Disposition"] = (
                "attachment; filename=%s" % signed_file
            )
            stream = response.stream(file, request=request)

            raise HTTP(200, stream, **response.headers)
        elif option == "update":
            vars = request.vars
            if vars["update"] == "1":
                student = get_id_from_student_local(vars["username"])
                query = dsa_utils.get_id_document_type_from_document(
                    vars["documentId"])
                document_type_id = db.executesql(query, as_dict=True)

                if student is None:
                    new_dict["form"] = False
                    new_dict["message"] = "en el servidor, intentelo de nuevo"
                    return dict(action=new_dict)
                if len(student) > 0:
                    carnet = student[0]["id"]
                    nombre = student[0]["name"]
                    apellido = student[0]["last_name"]
                    carnetForm = student[0]["username"]
                    document = document_type_id[0]["document"]
                    documentDelivered = vars["documentId"]
                    correo = student[0]["email"]
            else:
                carnet = vars["inputStudent"]
                nombre = vars["nombreForm"]
                apellido = vars["apellidoForm"]
                carnetForm = vars["carnetForm"]
                document = vars["inputDocumentType"]
                documentDelivered = vars["documentDelivered"]
                correo = vars["correoForm"]

            return set_upload_form(
                document,
                carnetForm,
                nombre,
                apellido,
                carnet,
                documentDelivered,
                correo,
            )
        elif option == "download_individual_uploaded":
            query = dsa_utils.get_uploaded_documents_from_document(
                request.vars.documentId
            )
            uploaded_files = db.executesql(query, as_dict=True)

            try:
                filename = dsa_utils.retrieve_zip_file_upload(
                    request.folder, uploaded_files
                )
            except Exception as e:
                print("********** admin - create deliverable **********")
                print(str(e))
                session.flash = "No se econtro el archivo"
                redirect(URL("documents_ecys", "documents_view"))

            if filename is not None:
                try:
                    file = dsa_utils.retrieve_file(filename, request.folder)
                except Exception as e:
                    print("********** admin - create deliverable **********")
                    print(str(e))
                    session.flash = "No se econtro el archivo"
                    redirect(URL("documents_ecys", "documents_view"))

                response.headers["Content-Type"] = contenttype.contenttype(
                    filename)
                response.headers["Content-Disposition"] = (
                    "attachment; filename=%s" % filename
                )
                stream = response.stream(file, request=request)
                raise HTTP(200, stream, **response.headers)
            else:
                print("********** admin - create deliverable **********")
                print(str(e))
                session.flash = "No se econtro el archivo"
                redirect(URL("documents_ecys", "documents_view"))
        elif option == "download_report":
            vars = request.vars
            query = dsa_utils.get_documents_per_student(
                vars["student"], auth.user.id)
            documents = db.executesql(query, as_dict=True)

            file = dsa_utils.create_csv_detail(
                documents, request.folder, vars["student"]
            )

            if file is not None:
                fileStream = dsa_utils.retrieve_file(file, request.folder)
                response.headers["Content-Type"] = contenttype.contenttype(
                    file)
                response.headers["Content-Disposition"] = (
                    "attachment; filename=%s" % file
                )
                stream = response.stream(fileStream, request=request)

                raise HTTP(200, stream, **response.headers)
            else:
                session.flash = "Error al generar el reporte"

    return dict(action=new_dict)


@auth.requires_login()
@auth.requires_membership("Documents-ECYS")
def normalize_save_string_for_file(document, type):
    query = dsa_utils.get_name_and_rol_of_document(document)
    names = db.executesql(query, as_dict=True)
    document_name = names[0]["name"]

    document_name = document_name.replace("-", "")
    document_name = document_name.strip()
    elements = document_name.split(" ")
    new_name = ""
    for element in elements:
        new_name += element.capitalize()

    return new_name + "({})-".format(type)


@auth.requires_login()
@auth.requires_membership("Documents-ECYS")
def get_id_from_student_local(carnet):
    get_query = dsa_utils.get_id_from_student(carnet)
    print(get_query)
    try:
        student = db.executesql(get_query, as_dict=True)
        return student
    except Exception as e:
        print(e)
        return None


@auth.requires_login()
@auth.requires_membership("Documents-ECYS")
def get_months_of_period(semester, year):
    output = []
    semester = int(semester)
    year = int(year)

    current_date_time = datetime.datetime.now()
    date = current_date_time.date()
    current_year = int(date.strftime("%Y"))
    current_month = int(date.strftime("%m"))

    months = []
    if year != current_year:
        months = [1, 7] if semester == 1 else [7, 13]
    else:
        months = [1, current_month +
                  1] if semester == 1 else [7, current_month + 1]

    for i in range(months[0], months[1]):
        month_string = str(i)
        date_time_object = datetime.datetime.strptime(month_string, "%m")
        name_of_month = date_time_object.strftime("%B")

        query = dsa_utils.get_quantity_of_download(
            month_string, str(year), auth.user.id
        )
        element = db.executesql(query, as_dict=True)
        element = element[0]

        monthElement = {
            "id": month_string + "-" + str(year),
            "month": name_of_month,
            "total": element["total"],
            "descargados": element["descargados"],
            "rechazados": element["rechazados"],
            "firmados": element["firmados"],
        }
        output.append(monthElement)

    return output


@auth.requires_login()
@auth.requires_membership("Documents-ECYS")
def check_student(check_carnet):
    svp = db(db.validate_student).select(
                db.validate_student.supplier,
                db.validate_student.action_service,
                db.validate_student.type_service,
                db.validate_student.send,
                db.validate_student.receive
            ).first()
    if svp is not None:
        try:
            # CONSUME THE WEBSERVICE
            client = SoapClient(
                location=svp.supplier,
                action=f'{svp.supplier}/{svp.action_service}',
                namespace=svp.supplier,
                soap_ns=svp.type_service,
                trace=True,
                ns=False,
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
            # PREPARE FOR RETURNED XML WEB SERVICE
            xml = back.as_xml()
            xml = xml.replace("&lt;", "<")
            xml = xml.replace("&gt;", ">")
            inicio = xml.find(f"<{svp.receive}>")
            final = xml.find(f"</{svp.receive}>")
            xml = xml[inicio : (final + len(f'</{svp.receive}>'))]

            root = ET.fromstring(xml)
            xml = SimpleXMLElement(xml)

            # VARIABLE TO CHECK THE CORRECT FUNCTIONING
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

            if ((CARNET is None or CARNET == "") and (NOMBRES is None or NOMBRES == "")
                and (APELLIDOS is None or APELLIDOS == "") and (CORREO is None or CORREO == "")):
                return {
                    "state": False,
                    "message": "El estudiante no se encuentra inscrito en el ciclo academico actual",
                }
            else:
                val = v.validar(db)
                is_student = False
                for c in root.findall("CARRERA"):
                    unidad = c.find("UNIDAD").text
                    extension = c.find("EXTENSION").text
                    carrera = c.find("CARRERA").text
                    is_student = val(unidad=unidad, extension=extension, carrera=carrera)
                    if is_student:
                        break

                if not is_student:
                    return {
                        "state": False,
                        "message": "El estudiante no se encuentra inscrito en la carrera necesaria para este servicio",
                    }
                else:
                    return {
                        "state": True,
                        "carnet": str(CARNET).strip(),
                        "nombre": NOMBRES,
                        "apellidos": APELLIDOS,
                        "correo": str(CORREO),
                    }
        except:
            return {"state": False, "message": "con el servicio"}
    else:
        return {"state": False, "message": "con el servicio"}


@auth.requires_login()
@auth.requires_membership("Documents-ECYS")
def get_periods_form_select(type=None):
    current_date_time = datetime.datetime.now()
    date = current_date_time.date()
    year = int(date.strftime("%Y"))
    query_year = dsa_utils.get_init_period_from_delivered_docuemnts()
    init = db.executesql(query_year, as_dict=True)
    init = 2022 if len(init) == 0 else init[0]["year"]
    periods = list()
    last = ""
    periods.append(OPTION("", _value=0))
    while True:
        diferencia = int(year) - init
        periods.append(
            OPTION(
                ("Primer semestre - " + str(init)),
                _value="1-" + str(init),
                _selected=(True if type == ("1-" + str(init)) else False),
            )
        )
        if diferencia == 0:
            if int(date.strftime("%m")) > 6:
                last = "2-" + str(init)
                periods.append(
                    OPTION(
                        ("Segundo semestre - " + str(init)),
                        _value="2-" + str(init),
                        _selected=(True if type == (
                            "2-" + str(init)) else False),
                    )
                )
            last = "1-" + str(init)
            break
        else:
            periods.append(
                OPTION(
                    ("Segundo semestre - " + str(init)),
                    _value="2-" + str(init),
                    _selected=(True if type == ("2-" + str(init)) else False),
                )
            )
            init += 1

    return (
        SELECT(
            periods, _name="periodSearch", _id="periodSearch", _class="form-control"
        ),
        last,
    )


@auth.requires_login()
@auth.requires_membership("Documents-ECYS")
def documents_view():
    args = request.args
    new_dict = {}

    def set_upload_form(
        documentType,
        carnetForm,
        nombre,
        apellido,
        username,
        documentDelivered,
        backUrl,
        correoForm,
    ):
        subir = "Subir Archivo"
        extensions = get_extensions_modified(documentType)

        extensions_principal = extensions[0]
        size_principal = 0
        message_size_principal = ""

        extensions_complement = extensions[1]
        size_complement = 0
        message_size_complement = ""

        query = dsa_utils.get_complement_or_no(documentType)
        is_complement = db.executesql(query, as_dict=True)
        is_complement = is_complement[0]["complement_required"]

        query = dsa_utils.get_document_type(documentType)
        document = db.executesql(query, as_dict=True)
        message_size_principal = "El tamaño maximo del archivo es de {} MB".format(
            document[0]["max_size"]
        )
        size_principal = document[0]["max_size"] * 1024 * 1024

        upload_form = FORM(
            INPUT(
                _class="form-control",
                _name="inputDocumentType",
                _value=documentType,
                _style="display: none;",
            ),
            INPUT(
                _class="form-control",
                _name="inputStudent",
                _value=username,
                _style="display: none;",
            ),
            INPUT(
                _class="form-control",
                _name="update",
                _value="0",
                _style="display: none;",
            ),
            INPUT(
                _class="form-control",
                _name="nombreForm",
                _value=nombre,
                _style="display: none;",
            ),
            INPUT(
                _class="form-control",
                _name="apellidoForm",
                _value=apellido,
                _style="display: none;",
            ),
            INPUT(
                _class="form-control",
                _name="carnetForm",
                _value=carnetForm,
                _style="display: none;",
            ),
            INPUT(
                _class="form-control",
                _name="documentDelivered",
                _value=documentDelivered,
                _style="display: none;",
            ),
            INPUT(
                _class="form-control",
                _name="backUrl",
                _value=backUrl,
                _style="display: none;",
            ),
            INPUT(
                _class="form-control",
                _name="correoForm",
                _value=correoForm,
                _style="display: none;",
            ),
            DIV(
                LABEL(
                    "Principal " + str(extensions_principal),
                    _for="inputPrincipal",
                    _class="col-sm-3 col-form-label",
                ),
                DIV(
                    INPUT(
                        _type="file",
                        _class="form-control-file",
                        _name="inputPrincipal",
                        _id="inputPrincipal",
                        _style="margin-top:5px;",
                        requires=[
                            IS_NOT_EMPTY(
                                error_message="Debe seleccionar un archivo a subir."
                            ),
                            IS_UPLOAD_FILENAME(
                                extension=str(extensions_principal),
                                error_message="Tipo de archivo no permitido.",
                            ),
                            IS_LENGTH(
                                size_principal, error_message=message_size_principal
                            ),
                        ],
                    ),
                    _class="col-sm-9",
                ),
                _class="form-group row",
            ),
            BUTTON(
                SPAN(_class="fa fa-upload"),
                subir,
                _type="submit",
                _class="btn btn-primary",
            ),
        )

        if is_complement == 1:
            subir = "Subir Archivos"
            message_size_complement = "El tamaño maximo del archivo es de {} MB".format(
                document[0]["complement_size"]
            )
            size_complement = document[0]["complement_size"] * 1024 * 1024
            upload_form = FORM(
                INPUT(
                    _class="form-control",
                    _name="inputDocumentType",
                    _value=documentType,
                    _style="display: none;",
                ),
                INPUT(
                    _class="form-control",
                    _name="inputStudent",
                    _value=username,
                    _style="display: none;",
                ),
                INPUT(
                    _class="form-control",
                    _name="update",
                    _value="0",
                    _style="display: none;",
                ),
                INPUT(
                    _class="form-control",
                    _name="nombreForm",
                    _value=nombre,
                    _style="display: none;",
                ),
                INPUT(
                    _class="form-control",
                    _name="apellidoForm",
                    _value=apellido,
                    _style="display: none;",
                ),
                INPUT(
                    _class="form-control",
                    _name="carnetForm",
                    _value=carnetForm,
                    _style="display: none;",
                ),
                INPUT(
                    _class="form-control",
                    _name="documentDelivered",
                    _value=documentDelivered,
                    _style="display: none;",
                ),
                INPUT(
                    _class="form-control",
                    _name="backUrl",
                    _value=backUrl,
                    _style="display: none;",
                ),
                INPUT(
                    _class="form-control",
                    _name="correoForm",
                    _value=correoForm,
                    _style="display: none;",
                ),
                DIV(
                    LABEL(
                        "Principal " + str(extensions_principal),
                        _for="inputPrincipal",
                        _class="col-sm-3 col-form-label",
                    ),
                    DIV(
                        INPUT(
                            _type="file",
                            _class="form-control-file",
                            _name="inputPrincipal",
                            _id="inputPrincipal",
                            _style="margin-top:5px;",
                            requires=[
                                IS_NOT_EMPTY(
                                    error_message="Debe seleccionar un archivo a subir."
                                ),
                                IS_UPLOAD_FILENAME(
                                    extension=str(extensions_principal),
                                    error_message="Tipo de archivo no permitido.",
                                ),
                                IS_LENGTH(
                                    size_principal, error_message=message_size_principal
                                ),
                            ],
                        ),
                        _class="col-sm-9",
                    ),
                    _class="form-group row",
                ),
                DIV(
                    LABEL(
                        "Complemento " + str(extensions_complement),
                        _for="inputComplement",
                        _class="col-sm-3 col-form-label",
                    ),
                    DIV(
                        INPUT(
                            _type="file",
                            _class="form-control-file",
                            _name="inputComplement",
                            _id="inputComplement",
                            _style="margin-top:5px;",
                            requires=[
                                IS_NOT_EMPTY(
                                    error_message="Debe seleccionar un archivo a subir."
                                ),
                                IS_UPLOAD_FILENAME(
                                    extension=str(extensions_complement),
                                    error_message="Tipo de archivo no permitido.",
                                ),
                                IS_LENGTH(
                                    size_complement,
                                    error_message=message_size_complement,
                                ),
                            ],
                        ),
                        _class="col-sm-9",
                    ),
                    _class="form-group row",
                ),
                BUTTON(
                    SPAN(_class="fa fa-upload"),
                    subir,
                    _type="submit",
                    _class="btn btn-primary",
                ),
            )

        new_dict["carnet"] = carnetForm
        new_dict["nombre"] = nombre
        new_dict["apellidos"] = apellido
        new_dict["correo"] = correoForm
        new_dict["form"] = True
        query = dsa_utils.get_name_and_role_from_document(documentType)
        role_and_name = db.executesql(query, as_dict=True)
        role_and_name = role_and_name[0]
        new_dict["role"] = role_and_name["role"]
        new_dict["documentName"] = role_and_name["name"]

        # eliminar el existente y hacerle un update a los campos del entregado
        if upload_form.accepts(request.vars, formname="upload_form"):
            name_complement = ""
            flag_complement = False
            if request.vars.inputPrincipal is not None:
                name = (
                    normalize_save_string_for_file(
                        request.vars.inputDocumentType, "Principal"
                    )
                    + request.vars.carnetForm
                )

                name_principal = dsa_utils.save_file(
                    request.vars.inputPrincipal.file,
                    request.vars.inputPrincipal.filename,
                    request.folder,
                    name,
                )
                if is_complement == 1:
                    complement_name = (
                        normalize_save_string_for_file(
                            request.vars.inputDocumentType, "Complemento"
                        )
                        + request.vars.carnetForm
                    )
                    name_complement = dsa_utils.save_file(
                        request.vars.inputComplement.file,
                        request.vars.inputComplement.filename,
                        request.folder,
                        complement_name,
                    )
                    if name_complement is not None:
                        flag_complement = True
                else:
                    flag_complement = True

                if name_principal is not None and flag_complement:
                    values = {
                        "principal": name_principal,
                        "complement": name_complement,
                    }
                    try:
                        delete_query = dsa_utils.get_file_and_file_complement(
                            documentDelivered
                        )
                        old_documents = db.executesql(
                            delete_query, as_dict=True)

                        if len(old_documents) > 0:
                            old_documents = old_documents[0]
                            if old_documents["file_uploaded"] != "":
                                dsa_utils.remove_file(
                                    old_documents["file_uploaded"], request.folder
                                )

                            if old_documents["complement_uploaded"] != "":
                                dsa_utils.remove_file(
                                    old_documents["complement_uploaded"], request.folder
                                )

                        query = dsa_utils.update_document_delivered(
                            values, documentDelivered
                        )
                        db.executesql(query)
                        session.flash = "Archivos actualizados correctamente"
                    except Exception as e:
                        print("********** student - stationery **********")
                        print(str(e))
                        session.flash = "No se pudo guardar el archivo"

                    redirect(
                        URL(
                            "documents_ecys",
                            "documents_view",
                            args=["detail"],
                            vars={"period": backUrl},
                        )
                    )
                else:
                    new_dict["message"] = "Error al guardar alguno de los archivos"

            else:
                new_dict["message"] = "Debe seleccionar un archivo a subir."

        return dict(action=new_dict, form=upload_form)

    new_dict["periods"], last = get_periods_form_select()
    if len(args) != 0:
        option = args[0]
        if option == "search":
            if request.vars.periodSearch != "0":
                period = request.vars.periodSearch
                period = period.split("-")
                months = get_months_of_period(period[0], period[1])

                new_dict["months"] = months
                month_string = (
                    "Primer semestre" if period[0] == "1" else "Segundo semestre"
                )
                new_dict["period"] = month_string + " - " + period[1]
                new_dict["period_report"] = month_string + "-" + period[1]
            else:
                session.flash = "Debe seleccionar un periodo para buscar"
                redirect(URL("documents_ecys", "documents_view"))
        elif option == "detail":
            period = request.vars.period.split("-")

            date_time_object = datetime.datetime.strptime(period[0], "%m")
            name_of_month = date_time_object.strftime("%B")
            new_dict["period"] = T(name_of_month) + " - " + period[1]
            new_dict["period_report"] = period[0] + "-" + period[1]

            query = dsa_utils.get_documents_per_month(
                period[0], period[1], auth.user.id
            )
            documents = db.executesql(query, as_dict=True)

            new_dict["documents"] = documents
            new_dict["periodBack"] = request.vars.period
        elif option == "download_individual":
            query = dsa_utils.get_signed_file(request.vars.documentId)
            signed_file = db.executesql(query, as_dict=True)
            signed_file = signed_file[0]["signed_file"]

            try:
                file = dsa_utils.retrieve_file(signed_file, request.folder)
                query_update = dsa_utils.update_downloaded_status(
                    request.vars.documentId
                )
                db.executesql(query_update)
            except Exception as e:
                print("********** admin - download deliverable **********")
                print(str(e))
                session.flash = "No se econtro el archivo"
                redirect(URL("documents_ecys", "documents_view"))

            response.headers["Content-Type"] = contenttype.contenttype(
                signed_file)
            response.headers["Content-Disposition"] = (
                "attachment; filename=%s" % signed_file
            )
            stream = response.stream(file, request=request)

            raise HTTP(200, stream, **response.headers)
        elif option == "download_partial":
            period = request.vars.period.split("-")
            query = dsa_utils.get_signed_files_partial(period[0], period[1])
            signed_files = db.executesql(query, as_dict=True)

            if len(signed_files) > 0:
                date_time_object = datetime.datetime.strptime(period[0], "%m")
                name_of_month = date_time_object.strftime("%B")
                name_of_month = T(name_of_month)

                try:
                    filename = dsa_utils.retrieve_zip_file(
                        request.folder, signed_files, name_of_month, period[1]
                    )
                    print(filename)

                except Exception as e:
                    print("********** admin - create deliverable **********")
                    print(str(e))
                    session.flash = "No se econtro el archivo"
                    redirect(URL("documents_ecys", "documents_view"))

                if filename is not None:
                    try:
                        file = dsa_utils.retrieve_file(
                            filename, request.folder)
                        for signed_file in signed_files:
                            query_update = dsa_utils.update_downloaded_status(
                                signed_file["id"]
                            )
                            db.executesql(query_update)
                    except Exception as e:
                        print("********** admin - create deliverable **********")
                        print(str(e))
                        session.flash = "No se econtro el archivo"
                        redirect(URL("documents_ecys", "documents_view"))

                    response.headers["Content-Type"] = contenttype.contenttype(
                        filename)
                    response.headers["Content-Disposition"] = (
                        "attachment; filename=%s" % filename
                    )
                    stream = response.stream(file, request=request)
                    raise HTTP(200, stream, **response.headers)
            else:
                session.flash = "No existen documentos pendientes"
                redirect(
                    URL(
                        "documents_ecys",
                        "documents_view",
                        args=["search"],
                        vars={"periodSearch": request.vars.period},
                    )
                )
        elif option == "download_full":
            period = request.vars.period.split("-")
            query = dsa_utils.get_signed_files_total(period[0], period[1])
            signed_files = db.executesql(query, as_dict=True)

            if len(signed_files) > 0:
                date_time_object = datetime.datetime.strptime(period[0], "%m")
                name_of_month = date_time_object.strftime("%B")
                name_of_month = T(name_of_month)

                try:
                    filename = dsa_utils.retrieve_zip_file(
                        request.folder, signed_files, name_of_month, period[1]
                    )
                    print(filename)

                except Exception as e:
                    print("********** admin - create deliverable **********")
                    print(str(e))
                    session.flash = "No se econtro el archivo"
                    redirect(URL("documents_ecys", "documents_view"))

                if filename is not None:
                    try:
                        file = dsa_utils.retrieve_file(
                            filename, request.folder)
                        for signed_file in signed_files:
                            query_update = dsa_utils.update_downloaded_status(
                                signed_file["id"]
                            )
                            db.executesql(query_update)
                    except Exception as e:
                        print("********** admin - create deliverable **********")
                        print(str(e))
                        session.flash = "No se econtro el archivo"
                        redirect(URL("documents_ecys", "documents_view"))

                    response.headers["Content-Type"] = contenttype.contenttype(
                        filename)
                    response.headers["Content-Disposition"] = (
                        "attachment; filename=%s" % filename
                    )
                    stream = response.stream(file, request=request)
                    raise HTTP(200, stream, **response.headers)
            else:
                session.flash = "No existen documentos pendientes"
                redirect(
                    URL(
                        "documents_ecys",
                        "documents_view",
                        args=["search"],
                        vars={"periodSearch": request.vars.period},
                    )
                )
        elif option == "update":
            vars = request.vars
            if vars["update"] == "1":
                student = get_id_from_student_local(vars["username"])
                query = dsa_utils.get_id_document_type_from_document(
                    vars["documentId"])
                documentTypeId = db.executesql(query, as_dict=True)

                if student is None:
                    new_dict["form"] = False
                    new_dict["message"] = "en el servidor, intentelo de nuevo"
                    return dict(action=new_dict)
                if len(student) > 0:
                    carnet = student[0]["id"]
                    nombre = student[0]["name"]
                    apellido = student[0]["last_name"]
                    correo = student[0]["email"]
                    carnetForm = student[0]["username"]
                    document = documentTypeId[0]["document"]
                    documentDelivered = vars["documentId"]
                    backUrl = vars["periodBack"]
            else:
                carnet = vars["inputStudent"]
                nombre = vars["nombreForm"]
                apellido = vars["apellidoForm"]
                carnetForm = vars["carnetForm"]
                document = vars["inputDocumentType"]
                documentDelivered = vars["documentDelivered"]
                backUrl = vars["backUrl"]
                correo = vars["correoForm"]

            return set_upload_form(
                document,
                carnetForm,
                nombre,
                apellido,
                carnet,
                documentDelivered,
                backUrl,
                correo,
            )
        elif option == "download_individual_uploaded":
            query = dsa_utils.get_uploaded_documents_from_document(
                request.vars.documentId
            )
            uploaded_files = db.executesql(query, as_dict=True)

            try:
                filename = dsa_utils.retrieve_zip_file_upload(
                    request.folder, uploaded_files
                )
            except Exception as e:
                print("********** admin - create deliverable **********")
                print(str(e))
                session.flash = "No se econtro el archivo"
                redirect(URL("documents_ecys", "documents_view"))

            if filename is not None:
                try:
                    file = dsa_utils.retrieve_file(filename, request.folder)
                except Exception as e:
                    print("********** admin - create deliverable **********")
                    print(str(e))
                    session.flash = "No se econtro el archivo"
                    redirect(URL("documents_ecys", "documents_view"))

                response.headers["Content-Type"] = contenttype.contenttype(
                    filename)
                response.headers["Content-Disposition"] = (
                    "attachment; filename=%s" % filename
                )
                stream = response.stream(file, request=request)
                raise HTTP(200, stream, **response.headers)
            else:
                print("********** admin - create deliverable **********")
                print(str(e))
                session.flash = "No se econtro el archivo"
                redirect(URL("documents_ecys", "documents_view"))
        elif option == "download_report":
            vars = request.vars
            period = vars["period"]
            file = ""
            period = period.split("-")
            period[0] = period[0].strip()
            period[1] = period[1].strip()

            if "Primer semestre" in period[0] or "Segundo semestre" in period[0]:
                name = period[0] + "_" + period[1]

                period[0] = "1" if period[0] == "Primer semestre" else "2"
                months = get_months_of_period(period[0], period[1])
                file = dsa_utils.create_csv_period(
                    months, request.folder, name)
            else:
                date_time_object = datetime.datetime.strptime(period[0], "%m")
                name_of_month = date_time_object.strftime("%B")
                name_of_month = T(name_of_month)
                name = name_of_month + "_" + period[1]

                query = dsa_utils.get_documents_per_month(
                    period[0], period[1], auth.user.id
                )
                documents = db.executesql(query, as_dict=True)
                file = dsa_utils.create_csv_detail(
                    documents, request.folder, name)
            if file is not None:
                fileStream = dsa_utils.retrieve_file(file, request.folder)
                response.headers["Content-Type"] = contenttype.contenttype(
                    file)
                response.headers["Content-Disposition"] = (
                    "attachment; filename=%s" % file
                )
                stream = response.stream(fileStream, request=request)

                raise HTTP(200, stream, **response.headers)
            else:
                session.flash = "Error al generar el reporte"
    else:
        period = last.split("-")
        months = get_months_of_period(period[0], period[1])

        new_dict["months"] = months
        month_string = "Primer semestre" if period[0] == "1" else "Segundo semestre"
        new_dict["period"] = month_string + " - " + period[1]
        new_dict["period_report"] = month_string + "-" + period[1]

    return dict(action=new_dict)


@auth.requires_login()
@auth.requires_membership("Documents-ECYS")
def get_document_types_form_select(type=None):
    query = dsa_utils.get_all_document_types(auth.user.id)
    document_types = db.executesql(query, as_dict=True)

    type_options = list()
    type_options.append(OPTION("", _value=0))
    for type in document_types:
        type_options.append(
            OPTION(
                type["name"],
                _value=type["id"],
                _selected=(True if type == str(type["id"]) else False),
            )
        )

    return SELECT(
        type_options,
        _name="inputDocumentType",
        _id="inputDocumentType",
        _class="form-control",
    )


@auth.requires_login()
@auth.requires_membership("Documents-ECYS")
def get_extensions_modified(id):
    query = dsa_utils.get_extensions_of_file(id)
    extensions = db.executesql(query, as_dict=True)

    extensions = db.executesql(query, as_dict=True)
    extensions_principal = extensions[0]["extension"].split(",")
    extensions_complement = (
        extensions[0]["complement_extension"].split(",")
        if extensions[0]["complement_extension"] is not None
        else []
    )

    salida = ""
    for ext in extensions_principal:
        salida += ext.strip() if salida == "" else "|" + ext.strip()

    salida_complement = ""
    for ext in extensions_complement:
        salida_complement += (
            ext.strip() if salida_complement == "" else "|" + ext.strip()
        )

    return "(" + salida + ")", "(" + salida_complement + ")"


@auth.requires_login()
@auth.requires_membership("Documents-ECYS")
def documents():
    args = request.args
    new_dict = {}

    def set_upload_form(documentType, carnetForm, username):
        new_dict["form"] = True
        student = get_id_from_student_local(carnetForm)
        nombre = student[0]["name"]
        apellido = student[0]["last_name"]
        correo = (
            "" if student[0]["email"] is None else student[0]["email"]
        )

        subir = "Subir Archivo"
        extensions = get_extensions_modified(documentType)

        extensions_principal = extensions[0]
        size_principal = 0
        message_size_principal = ""

        extensions_complement = extensions[1]
        size_complement = 0
        message_size_complement = ""

        query = dsa_utils.get_complement_or_no(documentType)
        is_complement = db.executesql(query, as_dict=True)
        is_complement = is_complement[0]["complement_required"]

        query = dsa_utils.get_document_type(documentType)
        document = db.executesql(query, as_dict=True)
        message_size_principal = "El tamaño maximo del archivo es de {} MB".format(
            document[0]["max_size"]
        )
        size_principal = document[0]["max_size"] * 1024 * 1024

        upload_form = FORM(
            INPUT(
                _class="form-control",
                _name="inputDocumentType",
                _value=documentType,
                _style="display: none;",
            ),
            INPUT(
                _class="form-control",
                _name="inputStudent",
                _value=username,
                _style="display: none;",
            ),
            INPUT(
                _class="form-control",
                _name="insert",
                _value="0",
                _style="display: none;",
            ),
            INPUT(
                _class="form-control",
                _name="carnetForm",
                _value=carnetForm,
                _style="display: none;",
            ),
            INPUT(
                _class="form-control",
                _name="inputSearch",
                _value="0",
                _style="display: none;",
            ),
            DIV(
                LABEL(
                    "Principal " + str(extensions_principal),
                    _for="inputPrincipal",
                    _class="col-sm-3 col-form-label",
                ),
                DIV(
                    INPUT(
                        _type="file",
                        _class="form-control-file",
                        _name="inputPrincipal",
                        _id="inputPrincipal",
                        _style="margin-top:5px;",
                        requires=[
                            IS_NOT_EMPTY(
                                error_message="Debe seleccionar un archivo a subir."
                            ),
                            IS_UPLOAD_FILENAME(
                                extension=str(extensions_principal),
                                error_message="Tipo de archivo no permitido.",
                            ),
                            IS_LENGTH(
                                size_principal, error_message=message_size_principal
                            ),
                        ],
                    ),
                    _class="col-sm-9",
                ),
                _class="form-group row",
            ),
            BUTTON(
                SPAN(_class="fa fa-upload"),
                subir,
                _type="submit",
                _class="btn btn-primary",
            ),
        )

        if is_complement == 1:
            subir = "Subir Archivos"
            message_size_complement = "El tamaño maximo del archivo es de {} MB".format(
                document[0]["complement_size"]
            )
            size_complement = document[0]["complement_size"] * 1024 * 1024
            upload_form = FORM(
                INPUT(
                    _class="form-control",
                    _name="inputDocumentType",
                    _value=documentType,
                    _style="display: none;",
                ),
                INPUT(
                    _class="form-control",
                    _name="inputStudent",
                    _value=username,
                    _style="display: none;",
                ),
                INPUT(
                    _class="form-control",
                    _name="insert",
                    _value="0",
                    _style="display: none;",
                ),
                INPUT(
                    _class="form-control",
                    _name="carnetForm",
                    _value=carnetForm,
                    _style="display: none;",
                ),
                INPUT(
                    _class="form-control",
                    _name="inputSearch",
                    _value="0",
                    _style="display: none;",
                ),
                DIV(
                    LABEL(
                        "Principal " + str(extensions_principal),
                        _for="inputPrincipal",
                        _class="col-sm-3 col-form-label",
                    ),
                    DIV(
                        INPUT(
                            _type="file",
                            _class="form-control-file",
                            _name="inputPrincipal",
                            _id="inputPrincipal",
                            _style="margin-top:5px;",
                            requires=[
                                IS_NOT_EMPTY(
                                    error_message="Debe seleccionar un archivo a subir."
                                ),
                                IS_UPLOAD_FILENAME(
                                    extension=str(extensions_principal),
                                    error_message="Tipo de archivo no permitido.",
                                ),
                                IS_LENGTH(
                                    size_principal, error_message=message_size_principal
                                ),
                            ],
                        ),
                        _class="col-sm-9",
                    ),
                    _class="form-group row",
                ),
                DIV(
                    LABEL(
                        "Complemento " + str(extensions_complement),
                        _for="inputComplement",
                        _class="col-sm-3 col-form-label",
                    ),
                    DIV(
                        INPUT(
                            _type="file",
                            _class="form-control-file",
                            _name="inputComplement",
                            _id="inputComplement",
                            _style="margin-top:5px;",
                            requires=[
                                IS_NOT_EMPTY(
                                    error_message="Debe seleccionar un archivo a subir."
                                ),
                                IS_UPLOAD_FILENAME(
                                    extension=str(extensions_complement),
                                    error_message="Tipo de archivo no permitido.",
                                ),
                                IS_LENGTH(
                                    size_complement,
                                    error_message=message_size_complement,
                                ),
                            ],
                        ),
                        _class="col-sm-9",
                    ),
                    _class="form-group row",
                ),
                BUTTON(
                    SPAN(_class="fa fa-upload"),
                    subir,
                    _type="submit",
                    _class="btn btn-primary",
                ),
            )

        new_dict["carnet"] = carnetForm
        new_dict["nombre"] = nombre
        new_dict["apellidos"] = apellido
        new_dict["correo"] = correo
        query = dsa_utils.get_name_and_role_from_document(documentType)
        role_and_name = db.executesql(query, as_dict=True)
        role_and_name = role_and_name[0]
        new_dict["role"] = role_and_name["role"]
        new_dict["documentName"] = role_and_name["name"]

        if upload_form.accepts(request.vars, formname="upload_form"):
            name_complement = ""
            flag_complement = False
            if request.vars.inputPrincipal is not None:
                name = (
                    normalize_save_string_for_file(
                        request.vars.inputDocumentType, "Principal"
                    )
                    + request.vars.carnetForm
                )
                name_principal = dsa_utils.save_file(
                    request.vars.inputPrincipal.file,
                    request.vars.inputPrincipal.filename,
                    request.folder,
                    name,
                )
                if is_complement == 1:
                    complement_name = (
                        normalize_save_string_for_file(
                            request.vars.inputDocumentType, "Complemento"
                        )
                        + request.vars.carnetForm
                    )
                    name_complement = dsa_utils.save_file(
                        request.vars.inputComplement.file,
                        request.vars.inputComplement.filename,
                        request.folder,
                        complement_name,
                    )
                    if name_complement is not None:
                        flag_complement = True
                else:
                    flag_complement = True

                if name_principal is not None and flag_complement:
                    values = {
                        "file_uploaded": name_principal,
                        "complement_uploaded": name_complement,
                        "user_file": request.vars.inputStudent,
                        "document": request.vars.inputDocumentType,
                    }
                    try:
                        query = dsa_utils.create_delivered_document(values)
                        db.executesql(query)
                        session.flash = "Archivos cargados correctamente"
                    except Exception as e:
                        print("********** student - stationery **********")
                        print(str(e))
                        # 'No se pudo guardar el archivo'
                        session.flash = str(e)

                    redirect(URL("documents_ecys", "documents"))
                else:
                    new_dict["message"] = "Error al guardar el o los archivos"
            else:
                new_dict["message"] = "Debe seleccionar un archivo a subir."

        return dict(action=new_dict, form=upload_form)

    if len(args) == 0:
        new_dict["documentTypes"] = get_document_types_form_select()
        new_dict["form"] = False
    else:
        option = args[0]
        if option == "validate":
            if request.vars.inputDocumentType != "0":
                if isinstance(request.vars.inputStudent, list):
                    request.vars.inputStudent = request.vars.inputStudent[0]
                if isinstance(request.vars.inputSearch, list):
                    request.vars.inputSearch = request.vars.inputSearch[0]
                if isinstance(request.vars.carnetForm, list):
                    request.vars.carnetForm = request.vars.carnetForm[0]
                if isinstance(request.vars.inputDocumentType, list):
                    request.vars.inputDocumentType = request.vars.inputDocumentType[0]

                carnet = request.vars.inputStudent.strip()
                carnetForm = ""

                if request.vars.inputSearch == "1":
                    try:
                        # validando la existencia del usuario en la tabla de usuarios del modulo actual / dsa_user
                        student = get_id_from_student_local(carnet)
                        print(student)
                        if student is None:
                            new_dict["form"] = False
                            new_dict["message"] = "en el servidor, intentelo de nuevo"
                            return dict(action=new_dict)
                        
                        if len(student) > 0:
                            print(student)
                            carnet = student[0]["id"]
                            carnetForm = student[0]["username"]
                        else:
                            # validando la existencia del usuario en la tabla de usuarios del dtt / auth_user
                            query = dsa_utils.search_student(carnet)
                            student = db.executesql(query, as_dict=True)
                            print(student)

                            if len(student) > 0:
                                student = student[0]
                                student["name"] = student["first_name"]
                                student["first_name"] = (
                                    student["first_name"]
                                    if student["first_name"] is not None
                                    else ""
                                )
                                student["last_name"] = (
                                    student["last_name"]
                                    if student["last_name"] is not None
                                    else ""
                                )
                                student["first_name"] = (
                                    student["first_name"]
                                    if student["first_name"] is not None
                                    else ""
                                )
                                student["username"] = (
                                    student["username"]
                                    if student["username"] is not None
                                    else ""
                                )
                                student["cui"] = (
                                    student["cui"] if student["cui"] is not None else ""
                                )
                                print(student)
                                insert_query = dsa_utils.create_student(student, False)
                                print(insert_query)
                                try:
                                    db.executesql(insert_query)
                                    student = get_id_from_student_local(carnet)

                                    if student is None:
                                        new_dict["form"] = False
                                        new_dict[
                                            "message"
                                        ] = "en el servidor, intentelo de nuevo"
                                        new_dict[
                                            "documentTypes"
                                        ] = get_document_types_form_select()
                                        return dict(action=new_dict)

                                    carnet = student[0]["id"]
                                    carnetForm = student[0]["username"]
                                except Exception as e:
                                    print(e)
                                    new_dict["form"] = False
                                    new_dict[
                                        "message"
                                    ] = "en el servidor, intentelo de nuevo"
                                    new_dict[
                                        "documentTypes"
                                    ] = get_document_types_form_select()
                                    return dict(action=new_dict)
                            else:
                                web_service_response = check_student(carnet)
                                if web_service_response["state"]:
                                    student = {
                                        "name": web_service_response["nombre"],
                                        "last_name": web_service_response["apellidos"],
                                        "cui": "",
                                        "email": web_service_response["correo"],
                                        "username": web_service_response["carnet"],
                                    }
                                    insert_query = dsa_utils.create_student(
                                        student, True
                                    )
                                    try:
                                        db.executesql(insert_query)
                                        student = get_id_from_student_local(
                                            carnet)

                                        if student is None:
                                            new_dict["form"] = False
                                            new_dict[
                                                "message"
                                            ] = "en el servidor, intentelo de nuevo"
                                            new_dict[
                                                "documentTypes"
                                            ] = get_document_types_form_select()
                                            return dict(action=new_dict)

                                        carnet = student[0]["id"]
                                        carnetForm = student[0]["username"]
                                    except Exception as e:
                                        print(e)
                                        new_dict["form"] = False
                                        new_dict[
                                            "message"
                                        ] = "en el servidor, intentelo de nuevo"
                                        new_dict[
                                            "documentTypes"
                                        ] = get_document_types_form_select()
                                        return dict(action=new_dict)
                                else:
                                    new_dict["register"] = ""
                                    new_dict[
                                        "inputDocumentType"
                                    ] = request.vars.inputDocumentType
                                    new_dict["form"] = True
                                    return dict(action=new_dict)

                        query = dsa_utils.get_value_document_is_unique(
                            request.vars.inputDocumentType
                        )
                        print('a', query)
                        validation = db.executesql(query, as_dict=True)
                        validation = validation[0]["validation_required"]
                        if validation == 1:
                            query_full = dsa_utils.get_full_validation(
                                request.vars.inputDocumentType, carnet
                            )
                            full_validation = db.executesql(
                                query_full, as_dict=True)

                            if len(full_validation) > 0:
                                new_dict[
                                    "message"
                                ] = "El estudiante ya cuenta con un documento asociado de este tipo, si desea subirlo, debe solicitar su rechazo al director ECYS"
                                new_dict["form"] = False
                                new_dict[
                                    "documentTypes"
                                ] = get_document_types_form_select()
                                return dict(action=new_dict)
                        else:
                            current_date_time = datetime.datetime.now()
                            date = current_date_time.date()
                            year = int(date.strftime("%Y"))
                            months = ([1, 6], [7, 12])[
                                int(date.strftime("%m")) > 6]
                            query_partial = dsa_utils.get_partial_validation(
                                request.vars.inputDocumentType, carnet, months, year
                            )
                            partial_validation = db.executesql(
                                query_partial, as_dict=True
                            )
                            if len(partial_validation) > 0:
                                new_dict[
                                    "message"
                                ] = "El estudiante ya cuenta con un documento asociado en el semestre en curso, si desea subirlo, debe solicitar su rechazo al director ECYS"
                                new_dict["form"] = False
                                new_dict[
                                    "documentTypes"
                                ] = get_document_types_form_select()
                                return dict(action=new_dict)

                            query_quantity = (
                                dsa_utils.get_documents_per_type_and_student(
                                    request.vars.inputDocumentType, carnet
                                )
                            )
                            quantity_of_document = db.executesql(
                                query_quantity, as_dict=True
                            )
                            quantity_of_document = quantity_of_document[0]["quantity"]
                            if quantity_of_document > 0:
                                new_dict["inputStudent"] = str(carnet)
                                new_dict["carnetForm"] = carnetForm
                                new_dict["inputSearch"] = "0"
                                new_dict[
                                    "inputDocumentType"
                                ] = request.vars.inputDocumentType
                                new_dict["form"] = False
                                new_dict["quantity"] = str(
                                    quantity_of_document)
                                query = dsa_utils.get_documents_per_student_by_document_type(
                                    carnetForm, request.vars.inputDocumentType
                                )
                                documents = db.executesql(query, as_dict=True)
                                new_dict["documents"] = documents
                                return dict(action=new_dict)
                    except Exception as e:
                        print(e)
                        new_dict["form"] = False
                        new_dict["message"] = "en el servidor, intentelo de nuevo"
                        new_dict["documentTypes"] = get_document_types_form_select()
                        return dict(action=new_dict)
                else:
                    carnetForm = request.vars.carnetForm

                return set_upload_form(
                    request.vars.inputDocumentType, carnetForm, carnet
                )
            else:
                new_dict["message"] = "Complete todos los campos"
                new_dict["documentTypes"] = get_document_types_form_select()
                new_dict["form"] = False
        elif option == "new":
            username = ""
            carnetForm = ""

            if request.vars.insert == "1":
                student = {
                    "cui": request.vars.inputCui.strip(),
                    "name": request.vars.inputName.strip(),
                    "last_name": request.vars.inputLastName.strip(),
                    "username": request.vars.inputStudent.strip(),
                    "email": request.vars.inputCorreo.strip(),
                }
                insert_query = dsa_utils.create_student(student, True)
                try:
                    db.executesql(insert_query)
                    student = get_id_from_student_local(
                        request.vars.inputStudent.strip()
                    )
                    if student is None:
                        new_dict["form"] = False
                        new_dict["message"] = "en el servidor, intentelo de nuevo"
                        new_dict["documentTypes"] = get_document_types_form_select()
                        return dict(action=new_dict)

                    username = student[0]["id"]
                    carnetForm = student[0]["username"]
                except Exception as e:
                    e = str(e)
                    print(e)
                    new_dict["form"] = False
                    new_dict["message"] = (
                        "El estudiante ya existe en el sistema"
                        if "1062" in e
                        else "en el servidor, intentelo de nuevo"
                    )
                    new_dict["documentTypes"] = get_document_types_form_select()
                    return dict(action=new_dict)
            else:
                username = request.vars.inputStudent
                carnetForm = request.vars.carnetForm

            return set_upload_form(request.vars.inputDocumentType, carnetForm, username)
        elif option == "return":
            redirect(URL("documents_ecys", "documents"))

    return dict(action=new_dict)
