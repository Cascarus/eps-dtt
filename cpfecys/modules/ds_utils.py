# coding=utf-8
import os
import shutil
import uuid
import qrcode
import base64
import datetime
import zipfile
import string
import random

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from PyPDF2 import PdfWriter, PdfReader

# ************************************** FUNCTIONS **************************************
def serialize_value(value):
    if isinstance(value, str):
        return "'" + value + "'"
    elif value is None:
        return 'NULL'
    return str(value)


def is_numeric(value):
    try:
        num_int = int(value)
    except ValueError:
        num_int = None

    return num_int is not None


def is_decimal(value):
    try:
        num_float = float(value)
    except ValueError:
        num_float = None

    return num_float is not None


def is_datetime(value):
    try:
        str_datetime =  datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        str_datetime = None

    return str_datetime is not None


def create_script_string(table_name, action, values, condition=None, operator=None):
    keys = values.keys()

    query_values = map(lambda key: serialize_value(values[key]), keys)
    if action == 'U' or action == 'D':  # update or delete
        keys2 = condition.keys()
        placeholders = map(lambda key: key + '=' + "{}", keys)
        placeholders_text = ', '.join(placeholders)
        if operator is None:
            condition_ = map(lambda key: key + '=' + serialize_value(condition[key]), keys2)
        else:
            condition_ = map(lambda key: key + operator + condition[key], keys2)
        condition_text = ' AND '.join(condition_)

        if action == 'U':
            query = ('UPDATE ' + table_name + ' SET ' + placeholders_text + ' WHERE ' + condition_text).format(*query_values)
        else:
            query = ('DELETE FROM ' + table_name + ' WHERE ' + condition_text).format(*query_values)
    elif action == 'I':  # insert
        columns_text = "(" + ", ".join(keys) + ")"
        placeholders = map(lambda key: "{}", keys)
        placeholders_text = '(' + ', '.join(placeholders) + ')'
        query = ('INSERT INTO ' + table_name + ' ' + columns_text + ' VALUES ' + placeholders_text).format(*query_values)

    return query


def remove_file(filename, path):
    uploads_path = os.path.join(path, 'uploads')
    file_path = os.path.join(uploads_path, filename)

    if os.path.isfile(file_path):
        try:
            os.remove(file_path)
            return True
        except Exception as ex:
            return False
    else:
        return True


def save_file(file, filename, path, name, file_name_old=None):
    uploads_path = os.path.join(path, 'uploads')

    if file_name_old is not None:
        rm_file = remove_file(file_name_old, path)
        if not rm_file:
            return None

    ext = os.path.splitext(filename)[1]
    file_name = f'{name}-{uuid.uuid4()}{"".join(ext)}'
    file_path = os.path.join(uploads_path, file_name)
    result = file_name

    d_file = open(file_path, 'wb')
    try:
        shutil.copyfileobj(file, d_file)
    except Exception as e:
        result = None
    finally:
        d_file.close()

    return result

def get_signature_path(path, filename):
    uploads_path = os.path.join(path, 'uploads')
    full_path = os.path.join(uploads_path, filename)

    return full_path

def is_valid_extension(l_extensions):
    extensions = l_extensions.split(",")
    for ext in extensions:
        if ext.strip().upper() == 'PDF':
            return True
    return False


def retrieve_zip_file(path, list_files, user):
    
    uploads_path = os.path.join(path, 'uploads')
    file_zip_name = 'download_deliverables_' + user + '.zip'
    file_zip_path = os.path.join(uploads_path, file_zip_name)

    temp_archive = zipfile.ZipFile(file_zip_path, mode='w', compression=zipfile.ZIP_DEFLATED)
    try:
        for files in list_files:
            file_path = os.path.join(uploads_path, files['filename'])
            if os.path.isfile(file_path):
                temp_archive.write(file_path, os.path.basename(file_path))

    except Exception as e:
        file_zip_name = None
    finally:
        temp_archive.close()

    return file_zip_name


def retrieve_file(filename, path):
    uploads_path = os.path.join(path, 'uploads')
    file_path = os.path.join(uploads_path, filename)

    return open(file_path, 'rb')


def get_string_separated(elements):
    result = None
    for item in elements:
        if result is None:
            result = str(item['id'])
        else:
            result = result + ',' + str(item['id'])

    return result


def sign_file(path, filename, url_, signatures, username, signed_file=None, carnet=None):
    extension = os.path.splitext(filename)[1]
    if extension.strip().upper() != '.PDF':
        return 'Extensión del archivo no es PDF', 0

    # obteniendo el carnet de usuario
    if carnet is None:
        user = filename.split("-")[1]
    else:
        user = carnet

    name = "deliverable-" + user
    uploads_path = os.path.join(path, 'uploads')

    if signed_file is None:
        ext = ".pdf"
        dest_filename = '%s-%s%s' % (name, uuid.uuid4(), ''.join(ext))
    else:
        dest_filename = signed_file

    dest_path_file = os.path.join(uploads_path, dest_filename)
    source_path_file = os.path.join(uploads_path, filename)
    qrcode_f = 'qrcode_file_' + username + '.pdf'
    #remove_file(qrcode_f, path)
    temp_path_file = os.path.join(uploads_path, qrcode_f)

    if not os.path.isfile(source_path_file):
        return 'No existe el archivo subido por estudiante', 0

    # ===== Modificación Documentos Rechazados (Juan Pablo Ardón López - Prácticas Finales) =====
    try:
        input_file = PdfReader(open(source_path_file, "rb"))
    except Exception as ex:
        return ex,0
    # ===== Termina Modificación Documentos Rechazados (Juan Pablo Ardón López - Prácticas Finales) =====

    page_count = len(input_file.pages)

    qrcode_img = None
    actual_page = 1
    cont_signature = 0
    c = canvas.Canvas(temp_path_file, pagesize=letter)

    for signature in signatures:
        if signature['signature_page'] > page_count:
            return 'Número de página fuera de rango', 0

        if actual_page < signature['signature_page']:
            if cont_signature > 0:
                c.showPage()
                actual_page = actual_page + 1
                cont_signature = 0

            while actual_page < signature['signature_page']:
                c.showPage()
                actual_page = actual_page + 1

        if signature['signature_type'] == 'QR Code':
            if qrcode_img is None:
                qrcode_img = generate_qrcode(path, url_, username)

            c.drawImage(qrcode_img, signature['signature_position_x'] * cm, signature['signature_position_y'] * cm,
                        signature['signature_width'], signature['signature_height'], mask='auto')

        else:
            if signature['image'] is None:
                return 'Firma no tiene asociada una imagen', 0

            path_image = os.path.join(uploads_path, signature['image'])
            c.drawImage(path_image, signature['signature_position_x'] * cm, signature['signature_position_y'] * cm,
                        signature['signature_width'], signature['signature_height'], mask='auto')

        cont_signature = cont_signature + 1

    # agregando las ultimas hojas, en caso que la última firma agregada este al inicio
    c.save()

    try:
        # ===== Modificación Documentos Rechazados (Juan Pablo Ardón López - Prácticas Finales) =====
        output_file = PdfWriter()
        image_temp = PdfReader(open(temp_path_file, "rb"))
        page_count_temp = len(image_temp.pages)
        # ===== Termina Modificación Documentos Rechazados (Juan Pablo Ardón López - Prácticas Finales) =====
        for actual in range(0, page_count):
            input_page = input_file.pages[actual]
            if actual < page_count_temp:
                input_page.merge_page(image_temp.pages[actual])
            output_file.add_page(input_page)
    except Exception as ex:
        return 'No es posible firmar el documento', 0

    try:
        output_stream = open(dest_path_file, "wb")
        output_file.write(output_stream)
        output_stream.close()
    except Exception as e:
        return str(e), 0

    return dest_filename, 1


def generate_qrcode(path, url_, username):
    
    filename = 'qrcode_image_' + username + '.png'
    uploads_path = os.path.join(path, 'uploads')
    dest_path = os.path.join(uploads_path, filename)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url_)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img.save(dest_path)

    return dest_path


def encode_delivered_id(delivered):
    values = {'0': 'e5', '1': 'f0', '2': 'k4', '3': '4W', '4': 'N7', '5': 'h9', '6': 'bk',
              '7': '4G', '8': 'ld', '9': 'r4'}
    id_temp = str(delivered)
    cont_m = 1
    base_cad = ""
    for i in range(len(id_temp)):
        cad_temp = values.get(id_temp[i])
        if cont_m == 1:
            base_cad = base_cad + cad_temp[0] + random.choice(string.ascii_letters + string.digits) + cad_temp[1] + \
                       random.choice(string.ascii_letters + string.digits)
        elif cont_m == 2:
            base_cad = base_cad + random.choice(string.ascii_letters + string.digits) + cad_temp[1] + \
                       random.choice(string.ascii_letters + string.digits) + cad_temp[0]
        elif cont_m == 3:
            base_cad = base_cad + cad_temp[0] + random.choice(string.ascii_letters + string.digits) + \
                       random.choice(string.ascii_letters + string.digits) + cad_temp[1]
        elif cont_m == 4:
            base_cad = base_cad + cad_temp[1] + random.choice(string.ascii_letters + string.digits) + \
                       cad_temp[0] + random.choice(string.ascii_letters + string.digits)
        elif cont_m == 5:
            base_cad = base_cad + random.choice(string.ascii_letters + string.digits) + cad_temp[0] + \
                       random.choice(string.ascii_letters + string.digits) + cad_temp[1]
        else:
            base_cad = base_cad + cad_temp[1] + random.choice(string.ascii_letters + string.digits) + \
                       random.choice(string.ascii_letters + string.digits) + cad_temp[0]

        cont_m = 1 if cont_m == 6 else cont_m + 1

    base64_cad = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(32)) + base_cad + \
                 ''.join(random.choice(string.ascii_letters + string.digits) for x in range(32))

    return base64_cad


def decode_delivered_id(cad_base64):

    if len(cad_base64) < 68:
        

        try:
            base64_cad = base64.b64decode(cad_base64)
        except Exception as e:
            base64_cad = 'nada'
    else:
        values = {'e5': '0', 'f0': '1', 'k4': '2', '4W': '3', 'N7': '4', 'h9': '5', 'bk': '6',
                  '4G': '7', 'ld': '8', 'r4': '9'}

        base64_cad = ""
        cont_m = 1
        for i in range(32, len(cad_base64) - 32, 4):
            if cont_m == 1:
                base_temp = cad_base64[i] + cad_base64[i+2]
                base64_cad = base64_cad + values.get(base_temp)
            elif cont_m == 2:
                base_temp = cad_base64[i+3] + cad_base64[i+1]
                base64_cad = base64_cad + values.get(base_temp)
            elif cont_m == 3:
                base_temp = cad_base64[i] + cad_base64[i+3]
                base64_cad = base64_cad + values.get(base_temp)
            elif cont_m == 4:
                base_temp = cad_base64[i+2] + cad_base64[i]
                base64_cad = base64_cad + values.get(base_temp)
            elif cont_m == 5:
                base_temp = cad_base64[i+1] + cad_base64[i+3]
                base64_cad = base64_cad + values.get(base_temp)
            else:
                base_temp = cad_base64[i+3] + cad_base64[i]
                base64_cad = base64_cad + values.get(base_temp)

            cont_m = 1 if cont_m == 6 else cont_m + 1

    return base64_cad

# ************************************** FIN FUNCTIONS **************************************


# ************************************** FILE_TYPE **************************************

def get_all_file_types():
    return ("SELECT"
            " id, name, extension"
            " FROM ds_type_file"
            " ORDER BY id;")


def get_file_type(id_file):
    return ("SELECT"
            " id, name, extension"
            " FROM ds_type_file"
            " WHERE id = {};").format(id_file)


def validate_form_file_types(vars_form):
    is_valid = True
    name = vars_form.inputName.strip()
    extension = vars_form.inputExtension.strip()

    result = {'inputName': name, 'inputExtension': extension}

    if name == "" or len(name) == 0:
        result['message'] = "Debe ingresar el campo 'Nombre'"
        is_valid = False
    elif extension == "" or len(extension) == 0:
        result['message'] = "Debe ingresar el campo 'Extensiones'"
        is_valid = False

    return is_valid, result

# ************************************** FIN FILE_TYPE **************************************


# ************************************** SIGNATURE **************************************

def get_all_signatures(user, is_admin):
    query = ("SELECT"
             " id, name, created_by,"
             " (CASE WHEN signature_type = 'QR Code' THEN 'Código QR' ELSE 'Firma Digital' END) AS type,"
             " (CASE WHEN 'True' = '{}' AND created_by = '{}' THEN 'No' ELSE 'Si' END) AS signature_director"
             " FROM ds_signature").format(is_admin, user)

    if not is_admin:
        query2 = (" WHERE created_by = '{}'"
                  " ORDER BY id;").format(user)
    else:
        query2 = " ORDER BY id;"

    return query + query2


def get_signature(id_signature, user, is_admin):
    query = ("SELECT"
             " id, name, signature_type, image, created_by,"
             " (CASE WHEN signature_type = 'QR Code' THEN 'Código QR' ELSE 'Firma Digital' END) AS type,"
             " (CASE WHEN 'True' = '{}' AND created_by = '{}' THEN 'No' ELSE 'Si' END) AS signature_director"
             " FROM ds_signature"
             " WHERE id = {}").format(is_admin, user, id_signature)

    if not is_admin:
        query2 = (" AND"
                  " created_by = '{}';").format(user)
    else:
        query2 = ";"

    return query + query2


def validate_form_signature(vars_form):
    is_valid = True
    result = {}
    name = vars_form.inputName.strip()
    type_signature = vars_form.inputType.strip()

    if name == "" or len(name) == 0:
        result['message'] = "Debe ingresar el campo 'Nombre'"
        is_valid = False
    elif type_signature == "0" or len(type_signature) == 0:
        result['message'] = "Debe seleccionar un Tipo de Firma"
        is_valid = False
    elif not (type_signature == 'QR' or type_signature == 'DS'):
        result['message'] = "Tipo de firma no existe"
        is_valid = False

    if type_signature == 'QR':
        type_signature = 'QR Code'
    elif type_signature == 'DS':
        type_signature = 'Digital Signature'

    result['inputName'] = name
    result['inputType'] = type_signature

    return is_valid, result

# ************************************** FIN SIGNATURE **************************************


# ************************************** DOCUMENT **************************************

def get_all_documents():
    return ("SELECT"
            " d.id, d.name, d.description, t.name AS type, d.doc_type, d.max_size, d.signature_required, d.is_active,"
            " d.date_start, d.date_finish"
            " FROM ds_document d"
            " JOIN ds_type_file t ON t.id = d.type_file"
            " ORDER BY d.id;")


def get_document(id_document):
    return ("SELECT"
            " d.id, d.name, d.description, d.type_file, d.doc_type, t.name AS type, d.max_size, d.signature_required,"
            " d.is_active,  d.date_start, d.date_finish"
            " FROM ds_document d"
            " JOIN ds_type_file t ON t.id = d.type_file"
            " WHERE d.id = {};").format(id_document)


def get_document_item(id_item):
    return ("SELECT"
            " r.id, r.name, t.name AS item_type"
            " FROM item_restriction r"
            " JOIN item_type t ON t.id = r.item_type"
            " WHERE r.id = {};").format(id_item)


def get_last_document():
    return ("SELECT *"
            " FROM ds_document"
            " ORDER BY id DESC LIMIT 1;")


def validate_form_document(vars_form):
    is_valid = True
    name = vars_form.inputName.strip()
    description = vars_form.inputDescription.strip()
    typeFile = vars_form.inputTypeFile.strip()
    typeDoc = vars_form.inputDocumentType.strip()
    size = vars_form.inputSize.strip()
    date_start = vars_form.inputStart.strip()
    date_finish = vars_form.inputFinish.strip()

    #activate = vars_form.has_key('inputActivate')
    activate = 'inputActivate' in vars_form
    #signature = vars_form.has_key('inputSignature')
    signature = 'inputSignature' in vars_form

    result = {'inputName': name, 'inputDescription': description, 'inputTypeFile': typeFile, 'inputSize': size,
              'inputActivate': activate, 'inputSignature': signature, 'inputDocumentType': typeDoc,
              'inputStart': date_start, 'inputFinish': date_finish}

    if name == "" or len(name) == 0:
        result['message'] = "Debe ingresar el campo 'Nombre'"
        is_valid = False
    elif description == "" or len(description) == 0:
        result['message'] = "Debe ingresar el campo 'Descripción'"
        is_valid = False
    elif typeFile == "0" or len(typeFile) == 0:
        result['message'] = "Debe seleccionar 'Tipo de archivo'"
        is_valid = False
    elif typeDoc == "0" or len(typeDoc) == 0:
        result['message'] = "Debe seleccionar 'Tipo entregable'"
        is_valid = False
    elif not (typeDoc == 'PS' or typeDoc == 'PE'):
        result['message'] = "No existe Tipo de entregable"
        is_valid = False
    elif size == "" or len(size) == 0:
        result['message'] = "Debe ingresar el campo 'Tamaño máximo'"
        is_valid = False
    elif not is_numeric(size):
        result['message'] = "Debe ingresar un valor númerico para el campo 'Tamaño máximo'"
        is_valid = False
    elif is_numeric(size) and int(size) <= 0:
        result['message'] = "Debe ingresar un valor mayor a 0 para el campo 'Tamaño máximo'"
        is_valid = False
    elif is_numeric(size) and int(size) > 10:
        result['message'] = "Debe ingresar un valor menor a 10 para el campo 'Tamaño máximo'"
        is_valid = False
    elif date_start == "" or len(date_start) == 0:
        result['message'] = "Debe ingresar el campo 'Fecha inicio'"
        is_valid = False
    elif not is_datetime(date_start):
        result['message'] = "Debe ingresar una fecha valida para el campo 'Fecha inicio'"
        is_valid = False
    elif date_finish == "" or len(date_finish) == 0:
        result['message'] = "Debe ingresar el campo 'Fecha finalización'"
        is_valid = False
    elif not is_datetime(date_finish):
        result['message'] = "Debe ingresar una fecha valida para el campo 'Fecha finalización'"
        is_valid = False

    start_date = datetime.datetime.strptime(date_start, "%Y-%m-%d %H:%M:%S")
    start_finish = datetime.datetime.strptime(date_finish, "%Y-%m-%d %H:%M:%S")
    if start_date > start_finish:
        result['message'] = "Fecha inicio no puede ser mayor que fecha finalización"
        is_valid = False

    if typeDoc == 'PS':
        result['inputDocumentType'] = 'Practice Start'
    elif typeDoc == 'PE':
        result['inputDocumentType'] = 'Practice Finished'

    return is_valid, result


def change_dates_form_document(date_start_old, date_finish_old, date_start, date_finish):
    change = False

    # fechas anteriores
    dso = datetime.datetime.strptime(date_start_old, "%Y-%m-%d %H:%M:%S")
    dfo = datetime.datetime.strptime(date_finish_old, "%Y-%m-%d %H:%M:%S")
    # nuevas fechas
    so = datetime.datetime.strptime(date_start, "%Y-%m-%d %H:%M:%S")
    fo = datetime.datetime.strptime(date_finish, "%Y-%m-%d %H:%M:%S")

    if dso != so or dfo != fo:
        change = True

    return change


def get_new_dates(id_document, year_p, p_name):
    return ("SELECT"
            " CONCAT(CONVERT({} USING utf8), '-',"
            " (CASE"
            " WHEN '{}' = 'First Semester' AND MONTH(date_start) <= 6 THEN IF(MONTH(date_start) < 10,"
            " CONCAT('0', CONVERT(MONTH(date_start) USING utf8)), CONVERT(MONTH(date_start) USING utf8))"
            " WHEN '{}' = 'First Semester' AND MONTH(date_start) > 6 THEN IF((MONTH(date_start)- 6 + 1) < 10,"
            " CONCAT('0', CONVERT((MONTH(date_start)- 6 + 1) USING utf8)),"
            " CONVERT((MONTH(date_start)- 6 + 1) USING utf8))"
            " WHEN '{}' = 'Second Semester' AND MONTH(date_start) <= 6 THEN IF((MONTH(date_start)- 1 + 6) < 10,"
            " CONCAT('0', CONVERT((MONTH(date_start)- 1 + 6) USING utf8)),"
            " CONVERT((MONTH(date_start)- 1 + 6) USING utf8))"
            " WHEN '{}' = 'Second Semester' AND MONTH(date_start) > 6 THEN IF(MONTH(date_start) < 10,"
            " CONCAT('0', CONVERT(MONTH(date_start) USING utf8)), CONVERT(MONTH(date_start) USING utf8))"
            " END), '-', IF(DAY(date_start) < 10, CONCAT('0', CONVERT(DAY(date_start) USING utf8)),"
            " CONVERT(DAY(date_start) USING utf8)), ' ', CONVERT(TIME(date_start) USING utf8)"
            " ) AS start_date,"
            " CONCAT(CONVERT({} USING utf8), '-',"
            " (CASE"
            " WHEN '{}' = 'First Semester' AND MONTH(date_finish) <= 6 THEN IF(MONTH(date_finish) < 10,"
            " CONCAT('0', CONVERT(MONTH(date_finish) USING utf8)), CONVERT(MONTH(date_finish) USING utf8))"
            " WHEN '{}' = 'First Semester' AND MONTH(date_finish) > 6 THEN IF((MONTH(date_finish)- 6 + 1) < 10,"
            " CONCAT('0', CONVERT((MONTH(date_finish)- 6 + 1) USING utf8)),"
            " CONVERT((MONTH(date_finish)- 6 + 1) USING utf8))"
            " WHEN '{}' = 'Second Semester' AND MONTH(date_finish) <= 6 THEN IF((MONTH(date_finish)- 1 + 6) < 10,"
            " CONCAT('0', CONVERT((MONTH(date_finish)- 1 + 6) USING utf8)),"
            " CONVERT((MONTH(date_finish)- 1 + 6) USING utf8))"
            " WHEN '{}' = 'Second Semester' AND MONTH(date_finish) > 6 THEN IF(MONTH(date_finish) < 10,"
            " CONCAT('0', CONVERT(MONTH(date_finish) USING utf8)), CONVERT(MONTH(date_finish) USING utf8))"
            " END), '-', IF(DAY(date_finish) < 10, CONCAT('0', CONVERT(DAY(date_finish) USING utf8)),"
            " CONVERT(DAY(date_finish) USING utf8)), ' ', CONVERT(TIME(date_finish) USING utf8)"
            " ) AS finish_date"
            " FROM ds_document"
            " WHERE id = {};").format(year_p, p_name, p_name, p_name, p_name,
                                      year_p, p_name, p_name, p_name, p_name, id_document)


# ************************************** FIN DOCUMENT **************************************


# ************************************** SIGNATURE ASSIGNMENT **************************************
def get_all_signature_assignments(document, reference):

    query = ("SELECT"
             " d.id, s.name AS signature, d.is_active, d.signature_position_x AS x, d.signature_position_y AS y,"
             " d.signature_height AS h, d.signature_width AS w, d.signature_page AS page,"
             " d.reference_document AS reference"
             " FROM ds_document_signature d"
             " JOIN ds_signature s ON s.id = d.signature"
             " WHERE d.reference_document = '{}'").format(reference)

    if reference == 'D':
        query2 = (" AND d.document = {}"
                  " ORDER BY d.id;").format(document)
    else:
        query2 = (" AND d.item_restriction = {}"
                  " ORDER BY d.id;").format(document)

    return query + query2


def get_signature_assignment(id_assignment, document, reference):
    query = ("SELECT"
             " d.id, s.id AS id_signature,s.name AS signature, d.is_active, d.signature_position_x AS x,"
             " d.signature_position_y AS y, d.signature_height AS h, d.signature_width AS w,"
             " d.signature_page AS page, s.image, s.signature_type, d.reference_document AS reference"
             " FROM ds_document_signature d"
             " JOIN ds_signature s ON s.id = d.signature"
             " WHERE d.id ={} AND d.reference_document = '{}'").format(id_assignment, reference)

    if reference == 'D':
        query2 = (" AND"
                  " d.document = {};").format(document)
    else:
        query2 = (" AND"
                  " d.item_restriction = {};").format(document)

    return query + query2


def validate_form_signature_assignment(vars_form):
    is_valid = True
    signature = vars_form.inputSignature.strip()
    x = vars_form.inputPositionX.strip()
    y = vars_form.inputPositionY.strip()
    h = vars_form.inputHeight.strip()
    w = vars_form.inputWidth.strip()
    page = vars_form.inputPage.strip()

    #activate = vars_form.has_key('inputActivate')
    activate = 'inputActivate' in vars_form

    result = {'inputSignature': signature, 'inputPositionX': x, 'inputPositionY': y, 'inputHeight': h,
              'inputWidth': w, 'inputPage': page, 'inputActivate': activate}

    if signature == "0" or len(signature) == 0:
        result['message'] = "Debe seleccionar 'Firma'"
        return False, result

    if x == "" or len(x) == 0:
        result['message'] = "Debe ingresar el campo 'Posición en eje X'"
        return False, result
    elif not is_decimal(x):
        result['message'] = "Debe ingresar un valor decimal para el campo 'Posición en eje X'"
        return False, result
    elif is_decimal(x):
        if float(x) <= 0:
            result['message'] = "Debe ingresar un valor mayor a 0 para el campo 'Posición en eje X'"
            return False, result

    if y == "" or len(y) == 0:
        result['message'] = "Debe ingresar el campo 'Posición en eje Y'"
        return False, result
    elif not is_decimal(y):
        result['message'] = "Debe ingresar un valor decimal para el campo 'Posición en eje Y'"
        return False, result
    elif is_decimal(y):
        if float(y) <= 0:
            result['message'] = "Debe ingresar un valor mayor a 0 para el campo 'Posición en eje Y'"
            return False, result

    if h == "" or len(h) == 0:
        result['message'] = "Debe ingresar el campo 'Altura'"
        return False, result
    elif not is_numeric(h):
        result['message'] = "Debe ingresar un valor entero para el campo 'Altura'"
        return False, result
    elif is_numeric(h):
        if int(h) <= 0:
            result['message'] = "Debe ingresar un valor mayor a 0 para el campo 'Altura'"
            return False, result

    if w == "" or len(w) == 0:
        result['message'] = "Debe ingresar el campo 'Ancho'"
        return False, result
    elif not is_numeric(w):
        result['message'] = "Debe ingresar un valor entero para el campo 'Ancho'"
        return False, result
    elif is_numeric(w):
        if int(w) <= 0:
            result['message'] = "Debe ingresar un valor mayor a 0 para el campo 'Ancho'"
            return False, result

    if page == "" or len(page) == 0:
        result['message'] = "Debe ingresar el campo 'No. Página'"
        return False, result
    elif not is_numeric(page):
        result['message'] = "Debe ingresar un valor entero para el campo 'No. Página'"
        return False, result
    elif is_numeric(page):
        if int(page) <= 0:
            result['message'] = "Debe ingresar un valor mayor a 0 para el campo 'No. Página'"
            return False, result

    # valores en centimetros
    cm = 28.3464566929
    width_max = 612.0 / cm
    height_max = 792.0 / cm

    actual_width = float(x) + (int(w) / cm)
    actual_height = float(y) + (int(h) / cm)

    if actual_width > width_max:
        result['message'] = "El valor en el eje x es mayor al ancho de una hoja carta"
        return False, result
    elif actual_height > height_max:
        result['message'] = "El valor en el eje y es mayor al alto de una hoja carta"
        return False, result

    return is_valid, result

# ************************************** FIN SIGNATURE ASSIGNMENT **************************************


# ************************************** DOCUMENT RESTRICTIONS **************************************
def get_all_document_restrictions(document):
    return ("SELECT"
            " d.id, d.area_level, a.name, d.is_enabled"
            " FROM ds_document_restriction_area d"
            " JOIN area_level a ON a.id=d.area_level"
            " WHERE d.document = {};").format(document)


def get_all_area_level():
    return ("SELECT"
            " id, name"
            " FROM area_level;")


def get_area_level(area_level):
    return ("SELECT"
            " id, name"
            " FROM area_level"
            " WHERE id = {};").format(area_level)


def get_document_restriction(restriction, document):
    return ("SELECT"
            " d.id, d.area_level, a.name, d.is_enabled"
            " FROM ds_document_restriction_area d"
            " JOIN area_level a ON a.id=d.area_level"
            " WHERE d.id = {} AND d.document = {};").format(restriction, document)


def validate_form_document_restrictions(vars_form):
    is_valid = True
    area = vars_form.inputArea.strip()

    #enabled = vars_form.has_key('inputEnabled')
    enabled = 'inputEnabled' in vars_form

    result = {'inputArea': area, 'inputEnabled': enabled}

    if area == "0" or len(area) == 0:
        result['message'] = "Debe ingresar el campo 'Área'"
        is_valid = False
    elif not is_numeric(area):
        result['message'] = "El valor para el campo 'Área' debe ser númerico"
        is_valid = False

    return is_valid, result

# ************************************** FIN DOCUMENT RESTRICTIONS **************************************


# ************************************** DOCUMENT RESTRICTION EXCEPTION **************************************
def get_all_restriction_exceptions(restriction, document):
    return ("SELECT"
            " e.id, e.project, p.name"
            " FROM ds_document_restriction_exception e"
            " JOIN project p ON p.id = e.project"
            " JOIN ds_document_restriction_area a ON a.id = e.document_restriction"
            " WHERE e.document_restriction = {} AND a.document = {};").format(restriction, document)


def get_all_projects(area_level):
    return ("SELECT"
            " id, name"
            " FROM project"
            " WHERE area_level = {};").format(area_level)


def get_project(project, area_level):
    return ("SELECT"
            " id, name"
            " FROM project"
            " WHERE id = {} AND area_level = {};").format(project, area_level)


def get_restriction_exception(res_exception, restriction, document):
    return ("SELECT"
            " e.id, e.project, p.name"
            " FROM ds_document_restriction_exception e"
            " JOIN project p ON p.id = e.project"
            " JOIN ds_document_restriction_area a ON a.id = e.document_restriction"
            " WHERE e.id = {} AND e.document_restriction = {}"
            " AND a.document = {};").format(res_exception, restriction, document)


def validate_form_restriction_exceptions(vars_form):
    is_valid = True
    project = vars_form.inputProject.strip()

    result = {'inputProject': project}

    if project == "0" or len(project) == 0:
        result['message'] = "Debe ingresar el campo 'Proyecto'"
        is_valid = False
    elif not is_numeric(project):
        result['message'] = "El valor para el campo 'Proyecto' debe ser númerico"
        is_valid = False

    return is_valid, result

# ************************************** FIN DOCUMENT RESTRICTION EXCEPTION **************************************


# ************************************** DOCUMENT CONTROL PERIOD **************************************
def get_all_document_control_periods():
    return ("SELECT"
            " dcp.id, py.period, p.name, py.yearp, dcp.period_year"
            " FROM ds_document_control_period dcp"
            " JOIN period_year py ON py.id = dcp.period_year"
            " JOIN period p ON p.id = py.period"
            " ORDER BY py.yearp DESC, py.period DESC;")


def get_all_periods():
    return ("SELECT"
            " py.id, p.name, py.yearp, IFNULL(dcp.id, 0) AS control_period"
            " FROM period_year py"
            " JOIN period p ON p.id = py.period"
            " LEFT JOIN ds_document_control_period dcp ON dcp.period_year = py.id"
            " WHERE (p.name = 'First Semester' OR p.name = 'Second Semester')"
            " AND IFNULL(dcp.id, 0) = 0"
            " ORDER BY py.yearp DESC, py.period DESC;")


def get_period(period_year):
    return ("SELECT"
            " py.id, p.name, py.yearp, IFNULL(dcp.id, 0) AS control_period"
            " FROM period_year py"
            " JOIN period p ON p.id = py.period"
            " LEFT JOIN ds_document_control_period dcp ON dcp.period_year = py.id"
            " WHERE py.id = {} AND"
            " (p.name = 'First Semester' OR p.name = 'Second Semester');").format(period_year)


def get_previous_period(period_year):
    return ("SELECT"
            " py.id, p.name, py.yearp"
            " FROM period_year py"
            " JOIN period p ON p.id = py.period"
            " WHERE py.id < {} AND (p.name = 'First Semester' OR p.name = 'Second Semester')"
            " ORDER BY py.yearp DESC, py.period DESC LIMIT 1;").format(period_year)


def get_document_control_period(id_control):
    return ("SELECT"
            " dcp.id, py.period, p.name, py.yearp"
            " FROM ds_document_control_period dcp"
            " JOIN period_year py ON py.id = dcp.period_year"
            " JOIN period p ON p.id = py.period"
            " WHERE dcp.id={};").format(id_control)


def get_document_control_period_by_period(period_year):
    return ("SELECT *"
            " FROM ds_document_control_period"
            " WHERE period_year = {};").format(period_year)


def get_deliverable_type(deliverable_type):
    if deliverable_type == '0':
        return [deliverable_type, 'Práctica Inicia', 'Practice Start']
    else:
        return [deliverable_type, 'Práctica Finaliza', 'Practice Finished']


def validate_form_document_control_period(vars_form):
    is_valid = True
    period = vars_form.inputPeriod.strip()

    result = {'inputPeriod': period}

    if period == "" or period == "0" or len(period) == 0:
        result['message'] = "Debe seleccionar 'Período'"
        is_valid = False
    elif not is_numeric(period):
        result['message'] = "El valor para el campo 'Período' debe ser númerico"
        is_valid = False

    return is_valid, result

# ************************************** FIN DOCUMENT CONTROL PERIOD **************************************


# ************************************** DOCUMENT DELIVERED **************************************
def get_report_document_delivered(control_period, doc_type, is_director, username):

    query1 = ("SELECT"
              " d.id, d.name, d.is_active, d.signature_required,"
              " SUM((CASE WHEN dd.is_enabled='T' THEN 1 ELSE 0 END)) Enabled,"
              " SUM((CASE WHEN dd.is_enabled='F' THEN 1 ELSE 0 END)) Disabled,"
              " SUM((CASE WHEN dd.status='Pending' THEN 1 ELSE 0 END)) Pending,"
              " SUM((CASE WHEN dd.status!='Pending' THEN 1 ELSE 0 END)) Delivered,"
              " SUM((CASE WHEN dd.status='Rejected' THEN 1 ELSE 0 END)) Rejected,"
              " SUM((CASE WHEN dd.status='Revised' THEN 1 ELSE 0 END)) Revised,"
              " SUM((CASE WHEN dd.status='Signed' THEN 1 ELSE 0 END)) Signed"
              " FROM ds_document_delivered dd"
              " JOIN ds_document d ON d.id = dd.document"
              " WHERE dd.control_period = {}"
              " AND d.doc_type = '{}'").format(control_period, doc_type)

    query2 = (" SELECT 0 AS id, 'Todos' AS name, '' AS is_active, '' AS signature_required, t.*"
              " FROM(SELECT"
              " SUM((CASE WHEN dd.is_enabled='T' THEN 1 ELSE 0 END)) Enabled,"
              " SUM((CASE WHEN dd.is_enabled='F' THEN 1 ELSE 0 END)) Disabled,"
              " SUM((CASE WHEN dd.status='Pending' THEN 1 ELSE 0 END)) Pending,"
              " SUM((CASE WHEN dd.status!='Pending' THEN 1 ELSE 0 END)) Delivered,"
              " SUM((CASE WHEN dd.status='Rejected' THEN 1 ELSE 0 END)) Rejected,"
              " SUM((CASE WHEN dd.status='Revised' THEN 1 ELSE 0 END)) Revised,"
              " SUM((CASE WHEN dd.status='Signed' THEN 1 ELSE 0 END)) Signed"
              " FROM ds_document_delivered dd"
              " JOIN ds_document d ON d.id = dd.document"
              " WHERE dd.control_period = {}"
              " AND d.doc_type = '{}'").format(control_period, doc_type)

    if is_director:
        query_in = (" AND dd.document IN ("
                    " SELECT DISTINCT ds.document"
                    " FROM"
                    " ds_document_signature ds"
                    " JOIN ds_signature s ON s.id = ds.signature AND s.created_by = '{}'"
                    " WHERE ds.is_active = 'T' AND ds.reference_document = 'D')").format(username)

        query = query1 + query_in
        query = query + " GROUP BY d.id, d.name, d.is_active, d.signature_required"
        query = query + " UNION ALL"
        query = query + query2
        query = query + query_in
        query = query + " ) AS t;"
    else:
        query = query1 + " GROUP BY d.id, d.name, d.is_active, d.signature_required"
        query = query + " UNION ALL"
        query = query + query2
        query = query + " ) AS t;"

    return query


def get_call_document_delivered_procedure(id_doc_p, c_period, p_period, status, doc_period):
    return ("CALL spi_ds_document_delivered"
            "({}, {}, {}, {}, '{}');").format(id_doc_p, c_period, p_period, status, doc_period)


def get_all_document_delivered(control_period, is_director, username, document=None):
    query = ("SELECT"
             " dd.id, dd.control_period, dd.is_enabled, au.username,"
             " CONCAT(au.first_name, ' ', au.last_name) AS user, al.name AS area, p.name AS project,"
             " d.name AS deliverable, d.is_active, d.signature_required, dd.file_uploaded, dd.signed_file, dd.comment,"
             " dd.status, dd.notified_mail, dd.date_start, dd.date_finish"
             " FROM ds_document_delivered dd"
             " JOIN ds_document d ON d.id = dd.document"
             " JOIN ds_type_file tf ON tf.id=d.type_file"
             " JOIN user_project up ON up.id=dd.user_project"
             " JOIN auth_user au ON au.id=up.assigned_user"
             " JOIN project p ON p.id=up.project"
             " JOIN area_level al ON al.id=p.area_level"
             " WHERE dd.control_period = {}").format(control_period)

    if document is not None:
        if is_director:
            query2 = (" AND dd.document IN ("
                      " SELECT DISTINCT ds.document"
                      " FROM"
                      " ds_document_signature ds"
                      " JOIN ds_signature s ON s.id = ds.signature AND s.created_by = '{}'"
                      " WHERE ds.is_active = 'T' AND ds.reference_document = 'D'"
                      " AND ds.document = {});").format(username, document)
        else:
            query2 = (" AND"
                      " dd.document = {};").format(document)
        query = query + query2
    else:
        if is_director:
            query_in = (" AND dd.document IN ("
                        " SELECT DISTINCT ds.document"
                        " FROM"
                        " ds_document_signature ds"
                        " JOIN ds_signature s ON s.id = ds.signature AND s.created_by = '{}'"
                        " WHERE ds.is_active = 'T' AND ds.reference_document = 'D')").format(username)
            query = query + query_in
        query = query + ";"

    return query


def get_all_document_delivered_filename(control_period, doc_type, delivered, is_director, username, document=None):

    query = ("SELECT"
             " (CASE WHEN 0 = {} THEN dd.signed_file ELSE dd.file_uploaded END) AS filename"
             " FROM ds_document_delivered dd"
             " JOIN ds_document d ON d.id = dd.document"
             " WHERE dd.control_period = {}"
             " AND d.doc_type = '{}'").format(delivered, control_period, doc_type)

    if delivered == '0':
        query = query + " AND (dd.signed_file IS NOT NULL) AND dd.status = 'Signed'"
    else:
        query = query + " AND (dd.file_uploaded IS NOT NULL)"

    if document is None:
        if is_director:
            query_in = (" AND dd.document IN ("
                        " SELECT DISTINCT ds.document"
                        " FROM"
                        " ds_document_signature ds"
                        " JOIN ds_signature s ON s.id = ds.signature AND s.created_by = '{}'"
                        " WHERE ds.is_active = 'T' AND ds.reference_document = 'D')").format(username)
            query = query + query_in
        query = query + ";"
    else:
        if is_director:
            query2 = (" AND dd.document IN ("
                      " SELECT DISTINCT ds.document"
                      " FROM"
                      " ds_document_signature ds"
                      " JOIN ds_signature s ON s.id = ds.signature AND s.created_by = '{}'"
                      " WHERE ds.is_active = 'T' AND ds.reference_document = 'D'"
                      " AND ds.document = {});").format(username, document)
        else:
            query2 = (" AND"
                      " dd.document = {};").format(document)
        query = query + query2

    return query


def get_all_document_delivered_to_sign(control_period, status, doc_type, is_director, username, document=None):
    query_temp1 = ("SELECT"
                   " dd.id, dd.file_uploaded, dd.signed_file, dd.document, d.name,"
                   " au.username, au.email, CONCAT(au.first_name, ' ', au.last_name) AS user"
                   " FROM ds_document_delivered dd"
                   " JOIN user_project up ON up.id = dd.user_project"
                   " JOIN auth_user au ON au.id = up.assigned_user")

    if doc_type == 'Practice Finished':
        query_temp1 = query_temp1 + " JOIN assignation_status ast ON ast.id = up.assignation_status" \
                                    " AND ast.name = 'Successful'"

    query_temp2 = (" JOIN ds_document d ON d.id=dd.document AND d.is_active = 'T' AND d.signature_required = 'T'"
                   " WHERE dd.control_period = {} AND dd.status = '{}' AND dd.is_enabled = 'T'"
                   " AND d.doc_type = '{}' AND dd.file_uploaded IS NOT NULL").format(control_period, status, doc_type)

    query = query_temp1 + query_temp2

    if document is None:
        if is_director:
            query_in = (" AND dd.document IN ("
                        " SELECT DISTINCT ds.document"
                        " FROM"
                        " ds_document_signature ds"
                        " JOIN ds_signature s ON s.id = ds.signature AND s.created_by = '{}'"
                        " WHERE ds.is_active = 'T' AND ds.reference_document = 'D')").format(username)
            query = query + query_in
        query = query + ";"
    else:
        if is_director:
            query2 = (" AND dd.document IN ("
                      " SELECT DISTINCT ds.document"
                      " FROM"
                      " ds_document_signature ds"
                      " JOIN ds_signature s ON s.id = ds.signature AND s.created_by = '{}'"
                      " WHERE ds.is_active = 'T' AND ds.reference_document = 'D'"
                      " AND ds.document = {});").format(username, document)
        else:
            query2 = (" AND"
                      " dd.document = {};").format(document)
        query = query + query2

    return query


def get_all_document_delivered_to_change(control_period, doc_type, document=None):
    query = ("SELECT"
             " dd.id"
             " FROM ds_document_delivered dd"
             " JOIN ds_document d ON d.id=dd.document AND d.is_active = 'T' AND d.doc_type = '{}'"
             " WHERE dd.control_period = {}").format(doc_type, control_period)

    if document is None:
        query = query + ";"
    else:
        query2 = (" AND"
                  " dd.document = {};").format(document)
        query = query + query2

    return query


def get_signatures_by_document(document):
    return ("SELECT"
            " s.signature_type, s.image, ds.signature_position_x, ds.signature_position_y,"
            " ds.signature_height, ds.signature_width, ds.signature_page"
            " FROM ds_document_signature ds"
            " JOIN ds_signature s ON s.id = ds.signature"
            " WHERE ds.document = {} AND ds.is_active = 'T'"
            " ORDER BY ds.signature_page;").format(document)


def get_document_delivered(id_delivered):
    return ("SELECT"
            " dd.id, dd.document, d.name AS deliverable, d.description, tf.extension, d.max_size,"
            " dd.is_enabled, dd.comment, dd.file_uploaded, dd.uploaded_at, dd.signed_file,"
            " dd.status, dd.date_start, dd.date_finish, d.signature_required,"
            " dcp.period_year, py.yearp, p.name,"
            " au.username, au.email, CONCAT(au.first_name, ' ', au.last_name) AS user"
            " FROM ds_document_delivered dd"
            " JOIN user_project up ON up.id = dd.user_project"
            " JOIN auth_user au ON au.id = up.assigned_user"
            " JOIN ds_document_control_period dcp ON dcp.id=dd.control_period"
            " JOIN ds_document d ON d.id=dd.document"
            " JOIN ds_type_file tf ON tf.id=d.type_file"
            " JOIN period_year py ON py.id = dcp.period_year"
            " JOIN period p ON p.id = py.period"
            " WHERE dd.id = {};").format(id_delivered)


def get_document_delivered_to_sign(id_delivered):
    return ("SELECT"
            " dd.id, dd.document, d.name AS deliverable, dd.file_uploaded, dd.signed_file, dd.status, dd.is_enabled,"
            " d.is_active, d.signature_required, au.username, IFNULL(ast.name, 'Active') AS assignation_status,"
            " d.doc_type"
            " FROM ds_document_delivered dd"
            " JOIN user_project up ON up.id = dd.user_project"
            " JOIN auth_user au ON au.id = up.assigned_user"
            " JOIN ds_document d ON d.id=dd.document"
            " LEFT JOIN assignation_status ast ON ast.id = up.assignation_status"
            " WHERE dd.id = {};").format(id_delivered)


def validate_form_dates_delivered(vars_form):
    import datetime
    is_valid = True
    date_start = vars_form.inputStart.strip()
    date_finish = vars_form.inputFinish.strip()

    result = {'inputStart': date_start, 'inputFinish': date_finish}

    if date_start == "" or len(date_start) == 0:
        result['message'] = "Debe ingresar el campo 'Fecha inicio'"
        is_valid = False
    elif not is_datetime(date_start):
        result['message'] = "Debe ingresar una fecha valida para el campo 'Fecha inicio'"
        is_valid = False
    elif date_finish == "" or len(date_finish) == 0:
        result['message'] = "Debe ingresar el campo 'Fecha finalización'"
        is_valid = False
    elif not is_datetime(date_finish):
        result['message'] = "Debe ingresar una fecha valida para el campo 'Fecha finalización'"
        is_valid = False

    start_date = datetime.datetime.strptime(date_start, "%Y-%m-%d %H:%M:%S")
    start_finish = datetime.datetime.strptime(date_finish, "%Y-%m-%d %H:%M:%S")
    if start_date > start_finish:
        result['message'] = "Fecha inicio no puede ser mayor que fecha finalización"
        is_valid = False

    return is_valid, result


# ************************************** FIN DOCUMENT DELIVERED **************************************


# ******************* RECEPTION STATIONERY ************************
def get_all_assignations_student(student):
    return (f"""
        SELECT
            up.id AS user_project,
            up.project,
            p.name AS project_name,
            al.id AS id_area,
            al.name AS area,
            py.yearp AS practice_year,
            pd.name AS practice_period,
            up.periods,
            up.assignation_status,
            sst.name AS name_status
        FROM user_project AS up
            JOIN project AS p ON p.id = up.project
            JOIN area_level AS al ON al.id = p.area_level
            JOIN period_year AS py ON py.id = up.period
            JOIN period AS pd ON pd.id = py.period
            LEFT JOIN assignation_status AS sst ON sst.id = up.assignation_status
        WHERE up.assigned_user = {student}
        ORDER BY up.id;
    """)

def get_all_assignations_document_control_period(user_project):
    return (f"""
        SELECT
            dcp.id,
            py.yearp AS control_year,
            pd.name AS control_period
        FROM ds_document_control_period AS dcp
            JOIN period_year AS py ON py.id = dcp.period_year
            JOIN period AS pd ON pd.id = py.period
        WHERE dcp.id IN (
                SELECT DISTINCT control_period
                FROM ds_document_delivered AS dd
                WHERE dd.user_project = {user_project}
            )
        ORDER BY py.yearp, py.period;
    """).format(user_project)

def get_doc_type_document_delivered_by_student(control_period, user_project):
    return (f"""
        SELECT DISTINCT
            s.doc_type
        FROM (
            SELECT
                t.doc_type,
                IFNULL(dra.id, 0) AS restriction,
                IFNULL(dre.id, 0) AS exeption
            FROM (
                SELECT
                    dd.document,
                    d.name,
                    d.doc_type,
                    p.id AS project,
                    p.area_level
                FROM ds_document_delivered AS dd
                    JOIN user_project AS up ON up.id = dd.user_project
                    JOIN project AS p ON p.id = up.project
                    JOIN ds_document AS d ON d.id = dd.document
                        AND d.is_active = 'T'
                WHERE 
                    dd.control_period = {control_period}
                    AND dd.user_project = {user_project}
            ) AS t
            LEFT JOIN ds_document_restriction_area AS dra ON dra.area_level = t.area_level
                AND dra.document = t.document
                AND dra.is_enabled = 'T'
            LEFT JOIN ds_document_restriction_exception AS dre ON dre.document_restriction = dra.id
                AND dre.project = t.project
        ) AS s
        WHERE (
            (s.restriction = 0 AND s.exeption = 0)
            OR (s.restriction != 0 AND s.exeption != 0)
        );
    """)

def get_all_documents_delivered_by_user_project(control_period, user_project, doc_type):
    return (f"""
        SELECT
            s.doc_delivered,
            s.deliverable,
            s.description,
            s.is_enabled,
            s.comment,
            s.file_uploaded,
            s.uploaded_at,
            s.signed_file,
            s.status,
            s.date_start,
            s.date_finish
        FROM (
            SELECT
                t.*,
                IFNULL(dra.id, 0) AS restriction,
                IFNULL(dre.id, 0) AS exeption
            FROM (
                SELECT
                    dd.id AS doc_delivered,
                    d.name AS deliverable,
                    d.description,
                    dd.document,
                    p.id AS project,
                    p.area_level,
                    dd.is_enabled,
                    dd.comment,
                    dd.file_uploaded,
                    dd.uploaded_at,
                    dd.signed_file,
                    dd.status,
                    dd.date_start,
                    dd.date_finish
                FROM ds_document_delivered AS dd
                    JOIN user_project AS up ON up.id = dd.user_project
                    JOIN project AS p ON p.id = up.project
                    JOIN ds_document AS d ON d.id = dd.document
                        AND d.is_active = 'T'
                        AND d.doc_type = '{doc_type}'
                WHERE
                    dd.control_period = {control_period}
                    AND dd.user_project = {user_project}
            ) AS t
                LEFT JOIN ds_document_restriction_area dra ON dra.area_level = t.area_level
                    AND dra.document = t.document
                    AND dra.is_enabled = 'T'
                LEFT JOIN ds_document_restriction_exception dre ON dre.document_restriction = dra.id
                    AND dre.project = t.project
        ) AS s
        WHERE (
            (s.restriction = 0 AND s.exeption = 0)
            OR (s.restriction != 0 AND s.exeption != 0)
        );
    """)

def get_document_delivered_by_user(id_delivered, student):
    return (f"""
        SELECT
            s.*
        FROM (
            SELECT
                t.*,
                IFNULL(dra.id, 0) AS restriction,
                IFNULL(dre.id, 0) AS exeption
            FROM (
                SELECT
                    dd.id AS doc_delivered,
                    d.name AS deliverable,
                    d.description,
                    dd.document,
                    p.id AS project,
                    p.area_level,
                    tf.extension,
                    d.max_size,
                    dd.comment,
                    dd.file_uploaded,
                    dd.uploaded_at,
                    dd.signed_file,
                    dd.status,
                    dd.date_start,
                    dd.date_finish,
                    d.signature_required
                FROM ds_document_delivered AS dd
                    JOIN user_project AS up ON up.id = dd.user_project AND up.assigned_user = {student}
                    JOIN project AS p ON p.id = up.project
                    JOIN ds_document AS d ON d.id = dd.document AND d.is_active = 'T'
                    JOIN ds_type_file AS tf ON tf.id = d.type_file
                WHERE
                    dd.id = {id_delivered}
                    AND dd.is_enabled = 'T'
            ) AS t
                LEFT JOIN ds_document_restriction_area AS dra ON dra.area_level = t.area_level
                    AND dra.document = t.document
                    AND dra.is_enabled = 'T'
                LEFT JOIN ds_document_restriction_exception AS dre ON dre.document_restriction = dra.id
                    AND dre.project = t.project
        ) AS s
        WHERE (
            (s.restriction = 0 AND s.exeption = 0)
            OR (s.restriction != 0 AND s.exeption != 0)
        );
    """)

# ******************* FIN RECEPTION STATIONERY ************************


# ******************* VALIDATION FILE ************************
def get_information_student(id_delivered, ref=None):
    if ref is None:
        return ("SELECT"
                " dd.id, au.first_name, au.last_name, au.username, au.cui, au.email, au.phone, au.photo,"
                " p.name AS proyecto, al.name AS area, py.yearp, pd.name AS periodo, up.hours,"
                " up.periods, d.name AS entregable, d.description, d.doc_type, dd.status, dd.comment,"
                " dd.file_uploaded, dd.uploaded_at, dd.signed_file, up.assigned_user, sst.name AS name_status"
                " FROM ds_document_delivered dd"
                " JOIN user_project up ON up.id=dd.user_project"
                " JOIN auth_user au ON au.id = up.assigned_user"
                " JOIN project p ON p.id = up.project"
                " JOIN area_level al ON al.id=p.area_level"
                " JOIN period_year py ON py.id = up.period"
                " JOIN period pd ON pd.id = py.period"
                " JOIN ds_document d ON d.id = dd.document"
                " LEFT JOIN assignation_status sst ON sst.id=up.assignation_status"
                " WHERE dd.id = {};").format(id_delivered)
    else:
        return ("SELECT"
                " itd.id, au.first_name, au.last_name, au.username, au.cui, au.email, au.phone, au.photo,"
                " p.name AS proyecto, al.name AS area, py.yearp, pd.name AS periodo, up.hours,"
                " up.periods, ir.name AS entregable, ir.name AS description, null AS doc_type, itd.status,"
                " i.admin_comment AS comment, i.uploaded_file AS file_uploaded, null AS uploaded_at, itd.signed_file,"
                " up.assigned_user, sst.name AS name_status"
                " FROM ds_item_delivered itd"
                " JOIN item i ON i.id = itd.item"
                " JOIN user_project up ON up.id=i.assignation"
                " JOIN auth_user au ON au.id = up.assigned_user"
                " JOIN project p ON p.id = up.project"
                " JOIN area_level al ON al.id=p.area_level"
                " JOIN period_year py ON py.id = up.period"
                " JOIN period pd ON pd.id = py.period"
                " JOIN item_restriction ir ON ir.id = i.item_restriction"
                " LEFT JOIN assignation_status sst ON sst.id=up.assignation_status"
                " WHERE itd.id = {};").format(id_delivered)


def get_history_assignations(id_user):
    return ("SELECT"
            " DISTINCT up.id, p.name AS proyecto, al.name AS area, py.yearp, pd.name AS periodo,"
            " up.hours, up.periods, sst.name AS name_status"
            " FROM user_project up"
            " JOIN project p ON p.id = up.project"
            " JOIN area_level al ON al.id=p.area_level"
            " JOIN period_year py ON py.id = up.period"
            " JOIN period pd ON pd.id = py.period"
            " LEFT JOIN assignation_status sst ON sst.id=up.assignation_status"
            " WHERE up.assigned_user = {}"
            " ORDER BY py.yearp DESC, py.period DESC;").format(id_user)


def get_history_rejections(id_delivered, ref=None):
    if ref is None:
        return ("SELECT"
                " created_at, comment"
                " FROM ds_document_delivered_log"
                " WHERE ref_delivered = {}"
                " ORDER BY created_at DESC;").format(id_delivered)
    else:
        return ("SELECT"
                " created_at, comment"
                " FROM ds_item_delivered_log"
                " WHERE ref_delivered = {}"
                " ORDER BY created_at DESC;").format(id_delivered)


# ******************* FIN VALIDATION FILE ************************


# ************************************** ITEM CONTROL PERIOD **************************************
def get_all_item_control_periods():
    return ("SELECT"
            " icp.id, py.period, p.name, py.yearp, icp.period_year"
            " FROM ds_item_control_period icp"
            " JOIN period_year py ON py.id = icp.period_year"
            " JOIN period p ON p.id = py.period"
            " ORDER BY py.yearp DESC, py.period DESC;")


def get_all_item_periods():
    return ("SELECT"
            " py.id, p.name, py.yearp, IFNULL(icp.id, 0) AS control_period"
            " FROM period_year py"
            " JOIN period p ON p.id = py.period"
            " LEFT JOIN ds_item_control_period icp ON icp.period_year = py.id"
            " WHERE (p.name = 'First Semester' OR p.name = 'Second Semester')"
            " AND IFNULL(icp.id, 0) = 0"
            " ORDER BY py.yearp DESC, py.period DESC;")


def get_item_period(period_year):
    return ("SELECT"
            " py.id, p.name, py.yearp, IFNULL(icp.id, 0) AS control_period"
            " FROM period_year py"
            " JOIN period p ON p.id = py.period"
            " LEFT JOIN ds_item_control_period icp ON icp.period_year = py.id"
            " WHERE py.id = {} AND"
            " (p.name = 'First Semester' OR p.name = 'Second Semester');").format(period_year)


def get_item_control_period_by_period(period_year):
    return ("SELECT *"
            " FROM ds_item_control_period"
            " WHERE period_year = {};").format(period_year)


def get_item_control_period(id_control):
    return ("SELECT"
            " icp.id, py.period, p.name, py.yearp"
            " FROM ds_item_control_period icp"
            " JOIN period_year py ON py.id = icp.period_year"
            " JOIN period p ON p.id = py.period"
            " WHERE icp.id={};").format(id_control)


# ************************************** FIN ITEM CONTROL PERIOD **************************************


# ************************************** ITEM DELIVERED **************************************
def get_report_item_delivered(control_period):
    return (" SELECT"
            " ir.id, ir.name, ir.is_enabled,"
            " SUM((CASE WHEN i.is_active='T' THEN 1 ELSE 0 END)) Enabled,"
            " SUM((CASE WHEN i.is_active='F' THEN 1 ELSE 0 END)) Disabled,"
            " SUM((CASE WHEN itd.status='Pending' THEN 1 ELSE 0 END)) Pending,"
            " SUM((CASE WHEN itd.status!='Pending' THEN 1 ELSE 0 END)) Delivered,"
            " SUM((CASE WHEN itd.status='Rejected' THEN 1 ELSE 0 END)) Rejected,"
            " SUM((CASE WHEN itd.status='Revised' THEN 1 ELSE 0 END)) Revised,"
            " SUM((CASE WHEN itd.status='Signed' THEN 1 ELSE 0 END)) Signed"
            " FROM ds_item_delivered itd"
            " JOIN item i ON i.id = itd.item"
            " JOIN item_restriction ir ON ir.id = i.item_restriction"
            " WHERE itd.control_period = {}"
            " AND ir.id IN ( SELECT DISTINCT ds.item_restriction"
            " FROM ds_document_signature ds WHERE ds.is_active = 'T' AND ds.reference_document = 'I')"
            " GROUP BY ir.id, ir.name, ir.is_enabled"
            " UNION ALL"
            " SELECT"
            " 0 AS id, 'Todos' AS name, '' AS is_active, t.*"
            " FROM ("
            " SELECT"
            " SUM((CASE WHEN i.is_active='T' THEN 1 ELSE 0 END)) Enabled,"
            " SUM((CASE WHEN i.is_active='F' THEN 1 ELSE 0 END)) Disabled,"
            " SUM((CASE WHEN itd.status='Pending' THEN 1 ELSE 0 END)) Pending,"
            " SUM((CASE WHEN itd.status!='Pending' THEN 1 ELSE 0 END)) Delivered,"
            " SUM((CASE WHEN itd.status='Rejected' THEN 1 ELSE 0 END)) Rejected,"
            " SUM((CASE WHEN itd.status='Revised' THEN 1 ELSE 0 END)) Revised,"
            " SUM((CASE WHEN itd.status='Signed' THEN 1 ELSE 0 END)) Signed"
            " FROM ds_item_delivered itd"
            " JOIN item i ON i.id = itd.item"
            " JOIN item_restriction ir ON ir.id = i.item_restriction"
            " WHERE itd.control_period = {}"
            " AND ir.id IN ( SELECT DISTINCT ds.item_restriction"
            " FROM ds_document_signature ds WHERE ds.is_active = 'T' AND ds.reference_document = 'I'"
            " ) ) AS t;").format(control_period, control_period)


def get_call_item_delivered_procedure(id_control, id_period):
    return ("CALL spi_ds_item_delivered"
            "({}, {});").format(id_control, id_period)


def get_all_item_delivered(control_period, document=None):
    query = ("SELECT"
             " itd.id, itd.control_period, i.is_active, au.username,"
             " CONCAT(au.first_name, ' ', au.last_name) AS user, al.name AS area, p.name AS project,"
             " ir.name AS deliverable, ir.is_enabled, i.uploaded_file, itd.signed_file, i.admin_comment,"
             " itd.status, i.notified_mail, au.id AS id_user, itd.item"
             " FROM ds_item_delivered itd"
             " JOIN item i ON i.id = itd.item"
             " JOIN item_restriction ir ON ir.id = i.item_restriction"
             " JOIN user_project up ON up.id = i.assignation"
             " JOIN auth_user au ON au.id=up.assigned_user"
             " JOIN project p ON p.id=up.project"
             " JOIN area_level al ON al.id=p.area_level"
             " WHERE itd.control_period = {}"
             " AND i.item_restriction IN ( SELECT DISTINCT ds.item_restriction"
             " FROM ds_document_signature ds WHERE ds.is_active = 'T'"
             " AND ds.reference_document = 'I'").format(control_period)

    if document is None:
        query = query + ");"
    else:
        query2 = (" AND ds.item_restriction = {}"
                  ");").format(document)
        query = query + query2

    return query


def get_all_item_delivered_filename(control_period, delivered, document=None):
    query = ("SELECT"
             " (CASE WHEN 0 = {} THEN itd.signed_file ELSE i.uploaded_file END) AS filename"
             " FROM ds_item_delivered itd"
             " JOIN item i ON i.id = itd.item"
             " WHERE itd.control_period = {}").format(delivered, control_period)

    if delivered == '0':
        query = query + " AND (itd.signed_file IS NOT NULL) AND itd.status = 'Signed'"
    else:
        query = query + " AND (i.uploaded_file IS NOT NULL OR i.uploaded_file != '')"

    query2 = (" AND i.item_restriction IN ( SELECT DISTINCT ds.item_restriction"
              " FROM ds_document_signature ds WHERE ds.is_active = 'T'"
              " AND ds.reference_document = 'I'")
    query = query + query2

    if document is None:
        query = query + ");"
    else:
        query2 = (" AND ds.item_restriction = {}"
                  ");").format(document)
        query = query + query2

    return query


def get_all_items_delivered_to_change(control_period, document=None):
    query = ("SELECT"
             " i.id"
             " FROM ds_item_delivered itd"
             " JOIN item i ON i.id = itd.item"
             " JOIN item_restriction ir ON ir.id = i.item_restriction AND ir.is_enabled = 'T'"
             " WHERE itd.control_period = {}"
             " AND i.item_restriction IN ( SELECT DISTINCT ds.item_restriction"
             " FROM ds_document_signature ds WHERE ds.is_active = 'T'"
             " AND ds.reference_document = 'I'").format(control_period)

    if document is None:
        query = query + ");"
    else:
        query2 = (" AND ds.item_restriction = {}"
                  ");").format(document)
        query = query + query2

    return query


def get_all_items_delivered_to_sign(control_period, status, document=None):
    query = ("SELECT"
             " itd.id, i.uploaded_file, itd.signed_file, i.item_restriction, ir.name,"
             " au.username, au.email, CONCAT(au.first_name, ' ', au.last_name) AS user"
             " FROM ds_item_delivered itd"
             " JOIN item i ON i.id = itd.item AND i.is_active = 'T'"
             " JOIN item_restriction ir ON ir.id = i.item_restriction AND ir.is_enabled = 'T'"
             " JOIN user_project up ON up.id = i.assignation"
             " JOIN auth_user au ON au.id=up.assigned_user"
             " WHERE itd.control_period = {} AND itd.status = '{}'"
             " AND (i.uploaded_file IS NOT NULL OR i.uploaded_file != '')"
             " AND i.item_restriction IN ( SELECT DISTINCT ds.item_restriction"
             " FROM ds_document_signature ds WHERE ds.is_active = 'T'"
             " AND ds.reference_document = 'I'").format(control_period, status)

    if document is None:
        query = query + ");"
    else:
        query2 = (" AND ds.item_restriction = {}"
                  ");").format(document)
        query = query + query2

    return query


def get_item_restriction(id_item):
    return ("SELECT"
            " id, name, is_enabled"
            " FROM item_restriction"
            " WHERE id = {};").format(id_item)


def get_signatures_by_item(item):
    return ("SELECT"
            " s.signature_type, s.image, ds.signature_position_x, ds.signature_position_y,"
            " ds.signature_height, ds.signature_width, ds.signature_page"
            " FROM ds_document_signature ds"
            " JOIN ds_signature s ON s.id = ds.signature"
            " WHERE ds.reference_document = 'I' AND ds.item_restriction = {} AND ds.is_active = 'T'"
            " ORDER BY ds.signature_page;").format(item)


def get_item_delivered(id_item):
    return ("SELECT"
            " itd.*, i.is_active, i.admin_comment, i.notified_mail, i.uploaded_file, i.item_restriction,"
            " ir.name AS deliverable, ir.is_enabled, au.username, au.email,"
            " CONCAT(au.first_name, ' ', au.last_name) AS user"
            " FROM ds_item_delivered itd"
            " JOIN item i ON i.id = itd.item"
            " JOIN item_restriction ir ON ir.id = i.item_restriction"
            " JOIN user_project up ON up.id = i.assignation"
            " JOIN auth_user au ON au.id=up.assigned_user"
            " WHERE itd.id = {};").format(id_item)


def get_item_delivered_by_item(id_item):
    return ("SELECT"
            " *"
            " FROM ds_item_delivered"
            " WHERE item = {};").format(id_item)


# ************************************** FIN ITEM DELIVERED **************************************