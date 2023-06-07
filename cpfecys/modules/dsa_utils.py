#!/usr/bin/env python
# coding: utf8
from calendar import month
from gluon import *

import datetime
import os
import uuid
import shutil
import zipfile

# Inicio - practicas finales(DSA) - Jose Carlos I Alonzo Colocho
def get_name_and_role_from_document(document):
    return ("SELECT name,"
            " (SELECT name FROM dsa_role WHERE id = "
            " (SELECT role FROM dsa_document_assign_role WHERE document = {})) as role"
            " FROM dsa_document_type WHERE id = {}").format(document, document)

def get_documents_per_student_by_document_type(carnet, document):
    return ("SELECT"
        " id, (SELECT name FROM dsa_document_type WHERE id = document) as document_name,"
        " (SELECT description FROM dsa_document_type WHERE id = document) as document_description,"
        " (SELECT name FROM dsa_user WHERE id = user_file) as student_first_name,"
        " (SELECT last_name FROM dsa_user WHERE id = user_file) as student_last_name,"
        " (SELECT username FROM dsa_user WHERE id = user_file) as carnet, "
        " uploaded_at, status, signed_at, comment"
        " FROM dsa_document_delivered"
        " WHERE user_file = "
        " (SELECT id FROM dsa_user WHERE username = '{}' LIMIT 1)"
        " AND document = {}"        
        " ORDER BY uploaded_at;").format(carnet, document)

def get_init_period_from_delivered_docuemnts():
    return ("SELECT YEAR(uploaded_at) as year FROM dsa_document_delivered"
            " ORDER BY uploaded_at LIMIT 1;")

def get_uploaded_documents_from_document(id):
    return ("SELECT file_uploaded, complement_uploaded"
            " FROM dsa_document_delivered"
            " WHERE id = {};").format(id)

def get_name_and_rol_of_document(id):
    return ("SELECT name FROM dsa_document_type"
            " WHERE id = {};").format(id)

def get_value_document_is_unique(id):
    return ("SELECT validation_required"
            " FROM dsa_document_type"
            " WHERE id = {};").format(id)

def get_full_validation(document, user_file):
    return ("SELECT id FROM dsa_document_delivered"
            " WHERE document = {} AND user_file = {};"
            ).format(document, user_file)

def get_partial_validation(document, user_file, months, year):
    return ("SELECT id FROM dsa_document_delivered"
            " WHERE document = {} AND user_file = {}"
            " AND (MONTH(uploaded_at) BETWEEN {} AND {})"
            " AND YEAR(uploaded_at) = {};"
            ).format(document, user_file, months[0], months[1], year)

def get_documents_per_type_and_student(document, user_file):
    return ("SELECT COUNT(*) as quantity FROM dsa_document_delivered"
            " WHERE document = {} AND user_file = {};").format(document, user_file)
    
def get_all_document_types_admin():
    return ("SELECT ddt.id, ddt.name, ddt.description, ddt.signature_required," 
            " ddt.complement_required, ddt.validation_required, dr.name AS role_name,"
            " (SELECT extension FROM dsa_type_file WHERE id = ddt.type_file) AS extension,"
            " (SELECT extension FROM dsa_type_file WHERE id = ddt.complement_type_file) AS complement_extension,"
            " ddt.max_size, ddt.complement_size"
            " FROM dsa_document_type as ddt"
            " INNER JOIN dsa_document_assign_role as ddar ON ddt.id = ddar.document"
            " INNER JOIN dsa_role as dr ON ddar.role = dr.id;")

def get_document_type_admin(id):
    return ("SELECT ddt.id, ddt.name, ddt.description, ddt.signature_required," 
            " ddt.complement_required, ddt.validation_required, dr.name AS role_name,"
            " (SELECT extension FROM dsa_type_file WHERE id = ddt.type_file) AS extension,"
            " (SELECT extension FROM dsa_type_file WHERE id = ddt.complement_type_file) AS complement_extension,"
            " ddt.max_size, ddt.complement_size"
            " FROM dsa_document_type as ddt"
            " INNER JOIN dsa_document_assign_role as ddar ON ddt.id = ddar.document"
            " INNER JOIN dsa_role as dr ON ddar.role = dr.id"
            " WHERE ddt.id = {};").format(id)

def get_document_type_admin_edit(id):
    return ("SELECT ddt.id, ddt.name, ddt.description, ddt.signature_required," 
            " ddt.complement_required, ddt.validation_required, ddar.role AS role,"
            " ddt.type_file AS extension,ddt.complement_type_file AS complement_extension,"
            " ddt.max_size, ddt.complement_size"
            " FROM dsa_document_type as ddt"
            " INNER JOIN dsa_document_assign_role as ddar ON ddt.id = ddar.document"
            " WHERE ddt.id = {};").format(id)

def create_document_type(document):
    return ("INSERT INTO"
            " dsa_document_type (name, description, max_size,"
            " complement_size, signature_required, complement_required,"
            " type_file, validation_required, complement_type_file) VALUES ('{}', '{}', {}, {}, {}, {}, {}, {}, {});"
            ).format(document['name'], document['description'], document['max_size'], document['complement_size'],
            document['signature_required'], document['complement_required'], document['type_file'],
            document['validation_required'], document['complement_type_file'])

def update_document_type(document):
    return ("UPDATE dsa_document_type"
            " SET name = '{}', description = '{}',"
            " max_size = {}, complement_size = {},"
            " signature_required = {}, complement_required = {},"
            " type_file = {}, validation_required = {}, complement_type_file = {}" 
            " WHERE id = {};").format(document['name'], document['description'], document['max_size'], document['complement_size'],
            document['signature_required'], document['complement_required'], document['type_file'],
            document['validation_required'], document['complement_type_file'], document['id'])

def update_document_assign_role(role, document):
    return ("UPDATE dsa_document_assign_role"
            " SET role = {}"
            " WHERE document = {};").format(role, document)

def get_last_id_from_document_type():
    return ("SELECT id FROM dsa_document_type ORDER BY id DESC LIMIT 1;")

def create_document_assign_role(assign):
    return ("INSERT INTO"
            " dsa_document_assign_role (document, role)"
            " VALUES ({}, {});").format(assign['document'], assign['role'])

def get_all_file_types():
    return ("SELECT * FROM dsa_type_file;")

def get_file_type(id):
    return ("SELECT *"
            " FROM dsa_type_file"
            " WHERE id = {};").format(id)

def create_file_type(fileType):
    return ("INSERT INTO"
            " dsa_type_file (name, extension)"
            " VALUES ('{}', '{}');").format(fileType['name'], fileType['extension'])

def delete_file_type(id):
    return ("DELETE"
            " FROM dsa_type_file"
            " WHERE id = {};").format(id)

def update_file_type(fileType):
    return ("UPDATE dsa_type_file"
            " SET name = '{}',"
            " extension = '{}'"
            " WHERE id = {};").format(fileType['name'], fileType['extension'], fileType['id'])

def get_roles():
    return ("SELECT * FROM dsa_role;")

def get_role(id):
    return ("SELECT *"
            " FROM dsa_role"
            " WHERE id = {};").format(id)

def delete_role(id):
    return ("DELETE"
            " FROM dsa_role"
            " WHERE id = {};").format(id)

def create_role(role):
    return ("INSERT INTO"
            " dsa_role (name, description)"
            " VALUES ('{}', '{}');").format(role['name'], role['description'])

def update_role(role):
    return ("UPDATE dsa_role"
            " SET name = '{}',"
            " description = '{}'"
            " WHERE id = {};").format(role['name'], role['description'], role['id'])

def get_users_for_dsa_roles():
    return ("SELECT auth_user.id as id, auth_user.first_name as first_name,"
            " auth_user.last_name as last_name, auth_user.username as username"
            " FROM auth_membership"
            " INNER JOIN auth_user ON auth_user.id = auth_membership.user_id"
            " WHERE auth_membership.group_id = (SELECT id FROM auth_group WHERE role = 'Documents-ECYS');")

def get_users_per_dsa_role(role):
    return ("SELECT auth_user.id as id, auth_user.first_name as first_name,"
            " auth_user.last_name as last_name, auth_user.username as username"
            " FROM dsa_user_assign_role"
            " INNER JOIN auth_user ON auth_user.id = dsa_user_assign_role.user"
            " WHERE dsa_user_assign_role.role = {};").format(role)

def insert_user_assign_role(user, role):
    return ("INSERT INTO"
            " dsa_user_assign_role (user, role)"
            " VALUES ({}, {});").format(user, role)

def remove_user_from_role(user, role):
    return ("DELETE"
            " FROM dsa_user_assign_role"
            " WHERE user = {} and role = {};").format(user, role)

def get_documents_per_student(carnet, user):
    return ("SELECT"
        " id, (SELECT name FROM dsa_document_type WHERE id = document) as document_name,"
        " (SELECT description FROM dsa_document_type WHERE id = document) as document_description,"
        " (SELECT name FROM dsa_user WHERE id = user_file) as student_first_name,"
        " (SELECT last_name FROM dsa_user WHERE id = user_file) as student_last_name,"
        " (SELECT username FROM dsa_user WHERE id = user_file) as carnet, "
        " uploaded_at, status, signed_at, comment"
        " FROM dsa_document_delivered"
        " WHERE user_file = "
        " (SELECT id FROM dsa_user WHERE username = '{}' LIMIT 1)"
        " AND document IN (SELECT id FROM dsa_document_type"
		" WHERE id IN (SELECT document FROM dsa_document_assign_role" 
        " WHERE role IN (SELECT role FROM dsa_user_assign_role WHERE user = {})))"        
        " ORDER BY uploaded_at;").format(carnet, user)

def get_file_and_file_complement(id):
    return ("SELECT file_uploaded, complement_uploaded"
            " FROM dsa_document_delivered"
            " WHERE id = {};").format(id)

def update_document_delivered(file, id):
    return ("UPDATE dsa_document_delivered"
            " SET signed_at = NULL, signed_file = NULL,"
            " comment = NULL, status = 'entregado',"
            " downloaded = false, file_uploaded = '{}',"
            " complement_uploaded = '{}',"
            " uploaded_at = STR_TO_DATE('{}', '%Y-%m-%d %H:%i:%S')"
            " WHERE id = {};").format(file['principal'], file['complement'], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id)

def get_id_document_type_from_document(id):
    return ("SELECT document"
            " FROM dsa_document_delivered"
            " WHERE id = {};").format(id)

def get_signed_file(id):
    return ("SELECT signed_file"
            " FROM dsa_document_delivered"
            " WHERE id = {};").format(id)

def get_signed_files_partial(month, year):
    return ("SELECT id, signed_file"
            " FROM dsa_document_delivered"
            " WHERE MONTH(uploaded_at) = {}"
            " AND YEAR(uploaded_at) = {}"
            " AND downloaded = false"
            " AND status = 'firmado';").format(month, year)

def get_signed_files_total(month, year):
    return ("SELECT id, signed_file"
            " FROM dsa_document_delivered"
            " WHERE MONTH(uploaded_at) = {}"
            " AND YEAR(uploaded_at) = {}"
            " AND status = 'firmado';").format(month, year)

def update_downloaded_status(id):
    return ("UPDATE dsa_document_delivered"
            " SET downloaded = true"
            " WHERE id = {};").format(id)

def get_quantity_of_download(month, year, user):
    return ("SELECT"
            " (SELECT COUNT(*) FROM"
            " dsa_document_delivered WHERE"
            " MONTH(uploaded_at) = {} AND"
            " YEAR(uploaded_at) = {} AND"
            " document in (SELECT id FROM dsa_document_type"
			" WHERE id in (select document from dsa_document_assign_role "
            " where role in (select role from dsa_user_assign_role where user = {})))) as total," # total
            " (SELECT COUNT(*) FROM "
            " dsa_document_delivered WHERE"
            " MONTH(uploaded_at) = {} AND"
            " YEAR(uploaded_at) = {} AND"
            " status = 'rechazado' AND" 
            " document in (SELECT id FROM dsa_document_type"
			" WHERE id in (select document from dsa_document_assign_role" 
            " where role in (select role from dsa_user_assign_role where user = {})))) as rechazados," #rechazados
            " (SELECT COUNT(*) FROM "
            " dsa_document_delivered WHERE"
            " MONTH(uploaded_at) = {} AND"
            " YEAR(uploaded_at) = {} AND"
            " status = 'firmado' AND"
            " document in (SELECT id FROM dsa_document_type"
			" WHERE id in (select document from dsa_document_assign_role"
            " where role in (select role from dsa_user_assign_role where user = {})))) as firmados," # firmados
            " COUNT(*) as descargados FROM"
            " dsa_document_delivered"
            " WHERE MONTH(uploaded_at) = {} AND"
            " YEAR(uploaded_at) = {} AND" # descargados
            " downloaded = true AND"
            " document in (SELECT id FROM dsa_document_type"
			" WHERE id in (select document from dsa_document_assign_role"
            " where role in (select role from dsa_user_assign_role where user = {})));"
            ).format(month, year, user, 
            month, year, user,
            month, year, user,
            month, year, user)

def get_id_from_student(username):
    return ("SELECT"
            " * FROM dsa_user"
            " WHERE username = '{}';").format(username)

def get_documents_per_month(month, year, user):
    return ("SELECT"
            " id, (SELECT name FROM dsa_document_type WHERE id = document) as document_name,"
            " (SELECT description FROM dsa_document_type WHERE id = document) as document_description,"
            " (SELECT  name FROM dsa_user WHERE id = user_file) as student_first_name,"
            " (SELECT  last_name FROM dsa_user WHERE id = user_file) as student_last_name,"
            " (SELECT  username FROM dsa_user WHERE id = user_file) as carnet, "
            " uploaded_at, status, signed_at, comment"
            " FROM dsa_document_delivered"
            " WHERE (MONTH(uploaded_at) = {})"
            " AND (YEAR(uploaded_at) = {})"
            " AND document in (SELECT id FROM dsa_document_type"
			" WHERE id in (select document from dsa_document_assign_role" 
            " where role in (select role from dsa_user_assign_role where user = {})))"
            " ORDER BY uploaded_at;").format(month, year, user)

def get_extensions_of_file(id):
    return (" SELECT"
            " (SELECT extension FROM dsa_type_file WHERE id = ddt.type_file) as extension," 
            " (SELECT extension FROM dsa_type_file WHERE id = ddt.complement_type_file) as complement_extension"
            " FROM dsa_document_type as ddt"
            " WHERE ddt.id = {};").format(id)

def get_document_type(id):
    return (" SELECT *"
            " FROM dsa_document_type"
            " WHERE id = {};").format(id)

def get_complement_or_no(id):
    return (" SELECT"
            " complement_required"
            " FROM dsa_document_type"
            " WHERE id = {};").format(id)

def get_all_document_types(id):
    return ("SELECT ddt.id, ddt.name FROM dsa_document_type as ddt" 
            " INNER JOIN dsa_document_assign_role as ddar ON ddt.id = ddar.document"
            " WHERE ddar.role IN (SELECT role FROM dsa_user_assign_role WHERE user = {});").format(id)

def search_student(carnet):
    return ("SELECT"
            " first_name, last_name,"
            " cui, username, email"
            " FROM auth_user"
            " WHERE username = '{}';").format(carnet)

def get_all_students_list():
    return ("SELECT"
            " id, username, name"
            " FROM dsa_user"
            " ORDER BY username asc;")

def create_student(student, service):
    query = "INSERT INTO dsa_user (name, last_name, cui, username, email) VALUES"
    if service:
        query += " ('" + student['name'] + "', "

        query += "'" + student['last_name'] + "', "

        if student['cui'] == "": query += "NULL, '"
        else: query += "'" + student['cui'] + "', '"

        query += student['username'] + "', "

        if student['email'] == "": query += "NULL);"
        else: query += "'" + student['email'] + "');"
    else:
        query += " ('" + student['name'].encode("utf8") + "', "

        query += "'" + student['last_name'].encode("utf8") + "', "

        if student['cui'] == "": query += "NULL, '"
        else: query += "'" + student['cui'].encode("utf8") + "', '"

        query += student['username'].encode("utf8") + "', "

        if student['email'] == "": query += "NULL);"
        else: query += "'" + student['email'].encode("utf8") + "');"

    return query

def create_csv_period(data, path, fileName):
    uploads_path = os.path.join(path, 'uploads')
    fileName = "{}_{}{}".format("Reporte", fileName, ".csv")
    filePath = os.path.join(uploads_path, fileName)

    try:
        file = open(filePath, "w")
        contenido = "mes,total,firmados,rechazados,descargados\n"
        for element in data:
            contenido += "'{}',{},{},{},{}\n".format(
                element['month'], 
                element['total'], 
                element['firmados'],
                element['rechazados'],
                element['descargados']
            )
        file.write(contenido)
        file.close()
        return fileName
    except Exception as err:
        print(err)
        return None

def create_csv_detail(data, path, fileName):
    uploads_path = os.path.join(path, 'uploads')
    fileName = "{}_{}{}".format("Reporte", fileName, ".csv")
    filePath = os.path.join(uploads_path, fileName)

    try:
        file = open(filePath, "w")
        contenido = "documento_cargado_nombre,documento_cargado_descripcion,documento_cargado_fecha_de_carga,"
        contenido += "estudiante_asociado_nombres,estudiante_asociado_apellidos,estudiante_asociado_carnet,"
        contenido += "documento_revisado_estado,documento_revisado_ultima_modificacion,documento_revisado_comentario\n"
        for element in data:
            #documento cargado
            contenido += "'{}','{}','{}',".format(
                element['document_name'].encode("utf-8"),
                element['document_description'].encode("utf-8"),
                element['uploaded_at'].strftime('%A, %d %b %Y, %H:%M:%S')
            )
            #estudiante asociado
            contenido += "'{}','{}','{}',".format(
                element['student_first_name'].encode("utf-8"),
                element['student_last_name'].encode("utf-8"),
                element['carnet'].encode("utf-8")
            )
            #documento firmado
            element['signed_at'] = element['signed_at'].strftime('%A, %d %b %Y, %H:%M:%S') if element['signed_at'] is not None else ""
            element['comment'] = element['comment'] if element['comment'] is not None else ""
            
            contenido += "'{}','{}','{}'\n".format(
                element['status'],
                element['signed_at'],
                element['comment'].encode("utf-8")
            )
        file.write(contenido)
        file.close()
        return fileName
    except Exception as err:
        print(err)
        return None 

def save_file(file, filename, path, name):
    uploads_path = os.path.join(path, 'uploads')

    ext = os.path.splitext(filename)[1]
    file_name = '%s-%s%s' % (name, uuid.uuid4(), ''.join(ext))
    file_path = os.path.join(uploads_path, file_name)
    result = file_name

    d_file = open(file_path, 'wb')
    try:
        shutil.copyfileobj(file, d_file)
    except Exception as e:
        result = None
        print('********** Error saving file **********')
        print(str(e))
    finally:
        d_file.close()

    return result

def create_delivered_document(document):
    query = ("INSERT INTO dsa_document_delivered (file_uploaded,"
            " complement_uploaded, uploaded_at, user_file, document, status)"
            " VALUES ('{}', ").format(document['file_uploaded']) 
    query += "NULL, " if document['complement_uploaded'] == "" else "'{}', ".format(document['complement_uploaded'])
    query += ("STR_TO_DATE('{}', '%Y-%m-%d %H:%i:%S'), {}, {}, 'entregado');"
            ).format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), document['user_file'], document['document'])
    return query

def retrieve_zip_file(path, files, month, year):
    uploads_path = os.path.join(path, 'uploads')
    file_zip_name = 'entregables_' + month + "_" + year + '.zip'
    file_zip_path = os.path.join(uploads_path, file_zip_name)

    temp_archive = zipfile.ZipFile(file_zip_path, mode='w', compression=zipfile.ZIP_DEFLATED)
    try:
        for file in files:
            file_path = os.path.join(uploads_path, file['signed_file'])
            temp_archive.write(file_path, os.path.basename(file_path))
    except Exception as e:
        file_zip_name = None
        print(str(e))
    finally:
        temp_archive.close()

    return file_zip_name

def retrieve_zip_file_upload(path, files):
    uploads_path = os.path.join(path, 'uploads')
    name = files[0]['file_uploaded']
    name = name.split("-")
    name[0] = name[0][0:name[0].find("(")]
    file_zip_name = name[0] + '_' + name[1] + '.zip'
    file_zip_path = os.path.join(uploads_path, file_zip_name)

    temp_archive = zipfile.ZipFile(file_zip_path, mode='w', compression=zipfile.ZIP_DEFLATED)
    try:
        for file in files:
            file_path = os.path.join(uploads_path, file['file_uploaded'])
            temp_archive.write(file_path, os.path.basename(file_path))
            if file['complement_uploaded'] is not None:
                file_path = os.path.join(uploads_path, file['complement_uploaded'])
                temp_archive.write(file_path, os.path.basename(file_path))
    except Exception as e:
        file_zip_name = None
        print(str(e))
    finally:
        temp_archive.close()

    return file_zip_name

def retrieve_file(filename, path):
    uploads_path = os.path.join(path, 'uploads')
    file_path = os.path.join(uploads_path, filename)

    return open(file_path, 'rb')

def remove_file(filename, path):
    uploads_path = os.path.join(path, 'uploads')
    file_path = os.path.join(uploads_path, filename)

    if os.path.isfile(file_path):
        try:
            os.remove(file_path)
            return True
        except Exception as ex:
            print('********** Error deleting file **********')
            print(str(ex))
            return False
    else:
        print('No existe el archivo')
        return True
