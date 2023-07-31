# coding=utf-8
import os
import uuid

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from PyPDF2 import PdfWriter, PdfReader

# ================================= QUERIES LIST =================================

def get_delivered_document_period():
    return(
        "Select Distinct YEAR(ddd.uploaded_at) as year,"
		" CASE" 
        " WHEN MONTH(ddd.uploaded_at) <= 6 THEN 'Primer Semestre'"
        " WHEN MONTH(ddd.uploaded_at) > 6 THEN 'Segundo Semestre'"
        " END AS Periodo"
        " From dsa_document_delivered ddd"
        " Order By year desc, Periodo desc;"
    )

def get_documents_type_by_period(role, symbol,year):

    return(
        "SELECT ddt.id, ddt.name,"
        " sum(case when ddd.status = 'entregado' then 1 else 0 end) as Entregados,"
        " sum(case when ddd.status = 'firmado' then 1 else 0 end) as Firmado,"
        " sum(case when ddd.status = 'rechazado' then 1 else 0 end) as Rechazado"
        " From dsa_document_type ddt, dsa_document_delivered ddd, dsa_document_assign_role ddar"
        " WHERE MONTH(ddd.uploaded_at) {} 6"
        " AND YEAR(ddd.uploaded_at) = {}"
        " AND ddd.document = ddt.id"
        " AND ddt.id = ddar.document"
        " AND ddar.role = {}"
        " GROUP BY ddt.id, ddt.name"
    ).format(symbol, year, role)

def get_all_documents_from_period(symbol,year,id,condition = None):
    _condition = ""
    if condition is not None:
        _condition = " AND ddd.status = '" + condition + "' ;"
    else:
        _condition = ";"
    return (
        "Select ddd.id, du.username as carnet, du.name, du.last_name, ddt.name as dname, ddt.signature_required as firma, dtf.extension,"
        " (CASE WHEN ddt.complement_type_file IS NULL THEN '-' ELSE (SELECT name FROM dsa_type_file dtf WHERE ddt.complement_type_file = dtf.id ) END) as extension_complemento,"
        " ddd.comment,ddd.status, ddd.file_uploaded as filename, ddd.signed_file, ddd.complement_uploaded as complemento"
        " FROM dsa_document_delivered ddd, dsa_user du, dsa_document_type ddt, dsa_type_file dtf"
        " WHERE du.id = ddd.user_file AND ddd.document = ddt.id"
        " AND ddt.type_file = dtf.id"
        " AND ddt.id = " + id + ""
        " AND MONTH(ddd.uploaded_at) " + symbol + " 6 AND YEAR(ddd.uploaded_at) = " + year + "" + _condition
    )

def get_document_delivered_sign_info(id):
    return (
        "Select dds.*, ds.image, ds.signature_type"
        " From dsa_document_signature dds, dsa_document_type ddt, dsa_document_delivered ddd, ds_signature ds"
        " WHERE ddd.id = " + id + " AND ddd.document = ddt.id AND dds.document = ddt.id AND dds.signature = ds.id;"
    )

def get_document_delivered_to_sign(id_doc):
    return (
        "select *"
        " FROM dsa_document_delivered"
        " WHERE id = {} ;"
    ).format(id_doc)

def get_information_student(id_delivered):
    return (
        "Select du.name as first_name, du.last_name, du.username, du.cui, du.email, ddt.name as name, ddt.description, ddd.status, ddd.uploaded_at,"
		" (CASE WHEN ddd.status = 'firmado' AND ddd.signed_file IS NOT NULL THEN ddd.signed_file ELSE ddd.file_uploaded END) as document"
        " FROM dsa_document_delivered ddd, dsa_user du, dsa_document_type ddt"
        " WHERE ddd.user_file = du.id AND ddd.document = ddt.id AND ddd.id = {};"
    ).format(id_delivered)

def get_complementary_information_student(id_delivered):
    return(
        "Select au.phone, au.photo"
        " FROM auth_user au, dsa_document_delivered ddd, dsa_user du"
        " WHERE ddd.user_file = du.id AND du.username = au.username AND ddd.id = {};"
    ).format(id_delivered)

def get_all_document_delivered(id_type, symbol, year, status):
    return(
        "Select ddd.id, ddd.file_uploaded, ddd.signed_file"
        " From dsa_document_delivered ddd, dsa_document_type ddt"
        " Where ddd.document = ddt.id And Month(ddd.uploaded_at) {} 6"
        " And Year(ddd.uploaded_at) = {}"
        " And ddd.status = '{}' And ddt.id = {};"
    ).format(symbol, year, status, id_type)

def get_all_document_delivered_filename(id_type, symbol, year, signed, type):
    return(
        "SELECT"
        " (CASE WHEN {} = True THEN (CASE WHEN ddd.status = 'firmado' AND ddd.signed_file is not null THEN ddd.signed_file END)"
        " ELSE (CASE WHEN ddd.file_uploaded is not null AND ddd.status = 'entregado' AND {} = 0 THEN ddd.file_uploaded"
        " ELSE (CASE WHEN {} = 2 AND ddd.complement_uploaded IS NOT NULL THEN ddd.complement_uploaded END) END) END) as filename"
        " FROM dsa_document_delivered ddd, dsa_document_type ddt"
        " WHERE ddd.document = ddt.id And Month(ddd.uploaded_at) {} 6"
        " AND Year(ddd.uploaded_at) = {}"
        " And ddt.id = {}"
        " HAVING filename is not null;"
    ).format(signed, type, type, symbol, year, id_type)

def get_all_documents():
    return (
        "SELECT"
        " ddt.id, ddt.name, ddt.description, ddt.max_size, ddt.complement_size, ddt.signature_required, ddt.complement_required,"
        " (Select name From dsa_type_file Where id=ddt.type_file)as extension,"
        " (Select name From dsa_type_file Where id=ddt.complement_type_file) as complement_extension"
        " FROM dsa_document_type ddt"
    )

def get_document_signatures(id):
    return(
        "SELECT"
        " dds.id, dds.position_x, dds.position_y, dds.height, dds.width, dds.page, ds.name, ds.id AS id_signature"
        " FROM dsa_document_signature dds, ds_signature ds, dsa_document_type ddt"
        " WHERE dds.document = ddt.id and dds.signature = ds.id and ddt.id = {};"
    ).format(id)

def get_document_signature(id):
    return(
        "SELECT dds.id, dds.position_x, dds.position_y, dds.height, dds.width, dds.page, ds.name, ds.id AS id_signature"
        " FROM dsa_document_signature dds, ds_signature ds"
        " WHERE dds.signature = ds.id and dds.id = {};"
    ).format(id)

def get_signatures_available():
    return(
        "SELECT"
        " id, name"
        " FROM ds_signature;"
    )

def get_signature_assignment(id_assignment, document, reference):
    query = ("SELECT"
             " d.id, s.id AS id_signature,s.name AS signature, d.signature_position_x AS x,"
             " d.signature_position_y AS y, d.signature_height AS h, d.signature_width AS w,"
             " d.signature_page AS page, s.image, s.signature_type, d.document AS reference"
             " FROM dsa_document_signature d"
             " JOIN ds_signature s ON s.id = d.signature"
             " WHERE d.id ={} AND d.reference_document = '{}'").format(id_assignment, reference)

    if reference == 'D':
        query2 = (" AND"
                  " d.document = {};").format(document)
    else:
        query2 = (" AND"
                  " d.item_restriction = {};").format(document)

    return query + query2

def get_document(id):
    return ("SELECT"
            " d.id, d.name, d.description, d.type_file, (Select name FROM dsa_type_file WHERE id=d.type_file) as type,"
            " (Select name FROM dsa_type_file WHERE id=d.complement_type_file) as complement_type,"
            " d.max_size, d.signature_required, d.complement_required"
            " FROM dsa_document_type d"
            " WHERE d.id = {};").format(id)

def get_sign_info(id):
    return(
        "SELECT"
        " name, signature_type, image"
        " FROM ds_signature"
        " WHERE id = {};"
    ).format(id)

def get_document_roles(symbol, year):
    return(
        "WITH roles as("
        " SELECT * FROM dsa_role )"
        " SELECT r.id, r.name, COUNT((CASE WHEN ddd.status = 'entregado' THEN 1 END)) as amount"
        " FROM dsa_document_type ddt, dsa_document_assign_role ddar, roles r, dsa_document_delivered ddd"
        " WHERE ddar.role = r.id and ddar.document = ddt.id and ddd.document = ddt.id"
        " And Month(ddd.uploaded_at) {} 6"
        " AND Year(ddd.uploaded_at) = {}"
        " GROUP BY r.id"
    ).format(symbol, year)

def get_document_download(type, id):
    return(
        "SELECT {} as filename"
        " FROM dsa_document_delivered ddd"
        " WHERE ddd.id = {}"
        " HAVING filename is not null;"
    ).format(type, id)


# ================================= FUNCTIONS =================================
def serialize_value(value):
    if isinstance(value, str):
        return "'" + value + "'"
    elif value is None:
        return 'NULL'
    return str(value)

def retrieve_file(filename, path):
    uploads_path = os.path.join(path, 'uploads')
    file_path = os.path.join(uploads_path, filename)

    return open(file_path, 'rb')

def encode_delivered_id(delivered):
    import string
    import random
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
        import base64

        try:
            base64_cad = base64.b64decode(cad_base64)
        except Exception as e:
            print(str(e))
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


def sign_file(path, filename, url, signatures, username, signed_file=None):
    extension = os.path.splitext(filename)[1]
    if extension.strip().upper() != '.PDF':
        return 'Extension del archivo no es PDF', 0

    #obteniendo el carnet de usuario (algo-carnet)
    user = filename.split('-')[1]
    name = "deliverable-" + user
    uploads_path = os.path.join(path,'uploads')

    if signed_file is None:
        ext = ".pdf" 
        dest_filename = '%s-%s%s' % (name, uuid.uuid4(), ''.join(ext))
        print("dest_filename: " + dest_filename)
    else:
        print("signed_file: " + signed_file)
        dest_filename = signed_file

    dest_path_file = os.path.join(uploads_path, dest_filename)
    print("dest_filename: " + dest_path_file)
    source_path_file = os.path.join(uploads_path,filename)
    qrcode_f = 'qrcode_file_' + username + '.pdf'
    temp_path_file = os.path.join(uploads_path, qrcode_f)
    try:
        input_file = PdfReader(open(source_path_file,"rb"), strict=False)
    except Exception as ex:
        return ex,0
    page_count = len(input_file.pages)
        
    qrcode_img = None
    actual_page = 1
    cont_signature = 0
    c = canvas.Canvas(temp_path_file, pagesize=letter)

    for signature in signatures:
        print(signature['page'])
        if signature['page'] > page_count:
            print('Número de paǵina fuera de rango({}), archivo: {}').format(signature['page'], filename)
            return 'Número de página fuera de rango', 0
        if actual_page < signature['page']:
            if cont_signature > 0:
                c.showPage()
                print('r Se guardaron {} firmas en la página {}'.format(cont_signature, actual_page))
                actual_page = actual_page + 1
                cont_signature = 0

            while actual_page < signature['page']:
                c.showPage()
                actual_page = actual_page + 1
        print(signature['signature_type'])
        if signature['signature_type'] == 'QR Code':
            if qrcode_img is None:
                qrcode_img = generate_qrcode(path, url, username)
            c.drawImage(qrcode_img, signature['position_x'] * cm, signature['position_y'] * cm,
                        signature['width'], signature['height'], mask='auto')

        else:
            if signature['image'] is None:
                print('Firma no tiene asociada una imagen, archivo: {}').format(filename)
                return 'Firma no tiene asociada una imagen', 0
            
            path_image = os.path.join(uploads_path, signature['image'])
            
            try:
                c.drawImage(path_image, signature['position_x'] * cm, signature['position_y'] * cm,
                            signature['width'], signature['height'], mask='auto')
            except Exception as ex:
                print(ex)
                return ex,0
        cont_signature = cont_signature + 1    
        
    # agregando las ultimas hojas, en caso que la última firma agregada este al inicio
    print(cont_signature, actual_page)
    print('a Se guardaron {} firmas en la página {}'.format(cont_signature, actual_page))
    c.save()
    try:
        try:
            output_file = PdfWriter()
            image_temp = PdfReader(open(temp_path_file, "rb"), strict=False)
            page_count_temp = len(image_temp.pages)
            for actual in range(0, page_count):
                input_page = input_file.pages[actual]
                if actual < page_count_temp:
                    input_page.merge_page(image_temp.pages[actual])
                output_file.add_page(input_page)
        except Exception as ex:
            print('No es posible firmar el documento')
            print(ex)
            return 'No es posible firmar el documento', 0
        
        try:
            output_stream = open(dest_path_file, "wb")
            output_file.write(output_stream)
            output_stream.close()
        except Exception as e:
            print(e)
            return str(e), 0
        return dest_filename, 1
    except Exception as e:
        print('error', e)
        

def generate_qrcode(path, url_, username):
    import qrcode
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

def create_script_string(table_name, action, values, condition = None, operator = None):
    keys = values.keys()

    query_values = map(lambda key: serialize_value(values[key]),keys)
    if action == 'U' or action == 'D':
        keys2 = condition.keys()
        placeholders = map(lambda key: key + '=' + "{}", keys)
        placeholders_text = ','.join(placeholders)

        if operator is None:
            condition_ = map(lambda key: key + '=' + serialize_value(condition[key]), keys2)
        else:
            condition_ = map(lambda key: key + operator + condition[key], keys2)
        condition_text = ' AND '.join(condition_)

        if action == 'U':
            query = ('UPDATE ' + table_name + ' SET ' + placeholders_text
                    + ' WHERE ' + condition_text).format(*query_values)
        else:
            query = ('DELETE FROM ' + table_name
                     + ' WHERE ' + condition_text).format(*query_values)
    
    elif action == 'I':
        columns_text = '('+', '.join(keys) + ")"
        placeholders = map(lambda key: "{}", keys)
        placeholders_text = '(' + ', '.join(placeholders) + ')'
        query = ('INSERT INTO ' + table_name + ' ' +
                 columns_text + ' VALUES ' + placeholders_text).format(*query_values)

    return query


def retrieve_zip_file(path, list_files, user):
    import zipfile
    uploads_path = os.path.join(path, 'uploads')
    file_zip_name = 'download_deliverables_' + user + '.zip'
    file_zip_path = os.path.join(uploads_path, file_zip_name)

    temp_archive = zipfile.ZipFile(file_zip_path, mode='w', compression=zipfile.ZIP_DEFLATED)

    try:
        for files in list_files:
            file_path = os.path.join(uploads_path, files['filename'])
            temp_archive.write(file_path, os.path.basename(file_path))
    
    except Exception as e:
        file_zip_name = None
        print(str(e))
    finally:
        temp_archive.close()
    
    return file_zip_name

def validate_form_signature_assignment(vars_form):
    signature = vars_form.inputSignature.strip()
    x = vars_form.inputPositionX.strip()
    y = vars_form.inputPositionY.strip()
    h = vars_form.inputHeight.strip()
    w = vars_form.inputWidth.strip()
    page = vars_form.inputPage.strip()

    result = {'inputSignature': signature, 'inputPositionX': x, 'inputPositionY': y, 'inputHeight': h,
              'inputWidth': w, 'inputPage': page}
    
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

    return True, result

def sign_sample(path, signature, values):
    uploads_path = os.path.join(path, 'uploads')

    dest_path = os.path.join(uploads_path, 'type_sample_signed.pdf')
    dest_path_file = os.path.join(uploads_path, 'type_sample_sign.pdf')
    qrcode_f = 'qrcode_file_sample.pdf'

    temp_path_file = os.path.join(uploads_path, qrcode_f)
    input_file = PdfReader(open(dest_path_file, 'rb'))
    page_count = len(input_file.pages)

    qrcode_img = None
    actual_page = 1
    
    c = canvas.Canvas(temp_path_file, pagesize=letter)

    
    if int(values['page']) > page_count:
        print('Número de paǵina fuera de rango)')
        return 'Número de página fuera de rango', 0

    
    if actual_page < int(values['page']):
        
        while actual_page < int(values['page']):
            c.showPage()
            actual_page = actual_page + 1
    
    if signature['signature_type'] == 'QR Code':
        if qrcode_img is None:
            qrcode_img = generate_qrcode(path, 'default','sample')
        try:
            c.drawImage(qrcode_img, values['x'] * cm, values['y'] * cm,
                        values['w'], values['h'], mask='auto')
        except Exception as e:
            return str(e), 0
    
    else:
        if signature['image'] is None:
            print('No existe firma')
            return 'Firma no tiene asociada una imagen', 0
        try:
            path_image = os.path.join(uploads_path, signature['image'])
            c.drawImage(path_image, values['x'] * cm, values['y'] * cm,
                        values['w'], values['h'], mask='auto')
        except Exception as e:
            print(e)
            return str(e), 0
    
    c.save()
    try:
        output_file = PdfWriter()
        image_temp = PdfReader(open(temp_path_file,'rb'))
        page_count_temp = len(image_temp.pages)
    except Exception as e:
        print(e)
        return "Error", 0

    try:
        for actual in range(0, page_count):
            input_page = input_file.pages[actual]
            if actual < page_count_temp:
                input_page.merge_page(image_temp.pages[actual])
            output_file.add_page(input_page)
    except Exception as ex:
        print('No es posible firmar el documento')
        print(ex)
        return 'No es posible firmar el documento', 0

    try:
        output_stream = open(dest_path, "wb")
        output_file.write(output_stream)
        output_stream.close()
    except Exception as e:
        print(e)
        return str(e), 0

    return dest_path_file, 1

def normalize(s):
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s    

def is_decimal(value):
    try:
        num_float = float(value)
    except ValueError:
        num_float = None

    return num_float is not None

def is_numeric(value):
    try:
        num_int = int(value)
    except ValueError:
        num_int = None

    return num_int is not None
