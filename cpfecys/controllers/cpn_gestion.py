import json as json_parser

#ATRIBUTOS DE idp:*:acttype:*:ida:*  HOJA|NOMBRE|TOTAL|INDICE
"""update; 1=cargar hoja, 2= borrar categoria, 3=modo editar categoria,
			4= actualizar categoria, 5= agregar row parametro, 6 guardar parametro nuevo,
			7= borrar parametro, 8= modo editar parametro, 9 = actualizando parametro
"""

@auth.requires_login()
@auth.requires(auth.has_membership('Student'))
def definicion():
	project = request.vars["project"]
	activity= request.vars["activity"]
	actname= request.vars["actname"]
	acttype= request.vars["acttype"]
	year= request.vars["year"]

	estado_hoja = False
	if (project!=None) & (activity!=None) & (actname!=None) & (acttype!=None) & (year!=None):
		estado_hoja = mtd_get_estado_hoja(year, project, acttype, activity)

	return dict(project=project, activity=activity, actname=actname, acttype=acttype, year=year, estado_hoja= estado_hoja)

@auth.requires_login()
@auth.requires(auth.has_membership('Student'))
def marco_definicion():
	return dict()

@auth.requires_login()
@auth.requires(auth.has_membership('Student'))
def categoria():
	return dict()

@auth.requires_login()
@auth.requires(auth.has_membership('Student'))
def parametros():
	project = request.vars["project"] #ID del proyecto
	acttype= request.vars["acttype"] # Tipo de actividad "Proyectos" | "Practicas"
	activity= request.vars["activity"] #ID de la actividad
	actname= request.vars["actname"] # Nombre de la actividad
	update = request.vars["update"] # Bandera para saber si esta cargando la pagina, o insertando
	year= request.vars["year"] # Periodo
	log_parametros = ""
	idcat=request.vars['idcat']
	idparam=request.vars['idparam']
	value = request.vars["value"]

	if update != None:
		if update == "0":
			pass
		elif update == "1": #Cuando se esta agregando una categoría nueva
			if (project!= None) & (activity!= None) & (actname!= None) & (acttype!= None) & (year!= None) & (value!=None):
				log_parametros=mtd_save_category(year, project, acttype, activity, value, actname)
		elif update == "2": #Cuando se borra una categoria
			if (idcat!=None) & (project!= None) & (acttype!= None) & (activity!= None) & (year!=None):
				mtd_remove_category(year, project, acttype, activity, idcat)
		elif update == "4": #Cuando se va a actualizar parametros de una categoria
			if (idcat!=None) & (project!= None) & (acttype!= None) & (activity!= None) & (value!=None) & (year!=None):
				log_parametros=mtd_update_category(year, project, acttype, activity, value, idcat)
		elif update == "6": #Guradar parametro nuevo
			if (idcat!=None) & (project!= None) & (acttype!= None) & (activity!= None) & (value!=None) & (year!=None):
				log_parametros=mtd_save_parameter(year, idcat, project, acttype, activity, value)
		elif update == "7": #Borrando parametro
			if (idcat!=None) & (project!= None) & (acttype!= None) & (activity!= None) & (idparam!=None) & (year!=None):
				mtd_remove_parameter(year, idcat, project, acttype, activity, idparam)
		elif update == "9": #Actualizando parametro
			if (idcat!=None) & (project!= None) & (acttype!= None) & (activity!= None) & (idparam!=None) & (value!=None) & (year!=None):
				log_parametros=mtd_update_parameter(year, idcat, project, acttype, activity, idparam, value)	

	# Es un arreglo del formato json de la hoja
	array_hoja = sheet_to_array(get_sheet_attribute(year, project, acttype, activity, 'hoja'))
	total_hoja = get_sheet_attribute(year, project, acttype, activity, 'total')
	total_hoja = float(total_hoja) if total_hoja!=None else None

	estado_hoja = mtd_get_estado_hoja(year, project, acttype, activity)

	return dict(array_hoja=array_hoja, total_hoja=total_hoja, log_parametros=log_parametros,\
				update= update, idcat=idcat, idparam=idparam, estado_hoja=estado_hoja)

@auth.requires_login()
@auth.requires(auth.has_membership('Student'))
def mtd_get_estado_hoja(period, project, acttype, activity):
	array_hoja = sheet_to_array(get_sheet_attribute(period, project, acttype, activity, 'hoja'))
	total_hoja = get_sheet_attribute(period, project, acttype, activity, 'total')
	if array_hoja!= None:
		if len(array_hoja)>0:
			for categoria in array_hoja:
				if categoria['estado']=='True':
					pass
				else:
					return False
			if float(total_hoja)==100:
				return True
			else:
				return False
		else:
			return False
	else:
		return False

@auth.requires_login()
@auth.requires(auth.has_membership('Student'))
def mtd_update_parameter(period, idcat, project, acttype, activity, idparam, updated_parameter):
	array_hoja = sheet_to_array(get_sheet_attribute(period, project, acttype, activity, 'hoja'))
	if (array_hoja!=None):
		i_hoja =0
		for categoria in array_hoja:
			if str(categoria['idcat']) == str(idcat):
				i_param = 0
				for parametro in array_hoja[i_hoja]['parametros']:
					if str(parametro['idparam']) == str(idparam):
						cat_nota= int(array_hoja[i_hoja]['nota'])
						obj_tmp_parameter = sheet_to_array(updated_parameter)
						if array_hoja[i_hoja]['avg'] == 'False':
							if mtd_validar_nota_parametro(array_hoja[i_hoja]['parametros'], cat_nota, obj_tmp_parameter['nota'], parametro['nota']):
								array_hoja[i_hoja]['parametros'][i_param]['parametro'] =  obj_tmp_parameter['parametro']
								array_hoja[i_hoja]['parametros'][i_param]['nota'] =  obj_tmp_parameter['nota']
								#Validar total de las notas de los parametros para cambiar estado de categoría
								if mtd_is_category_ready(array_hoja[i_hoja]['parametros'], cat_nota):
									array_hoja[i_hoja]['estado'] = "True"
								else:
									array_hoja[i_hoja]['estado'] = "False"
								insert_sheet_attribute(period, project, acttype, activity, 'hoja', json_parser.dumps(array_hoja))
								return ""
						#******** Cuando esta activado AVG *******
						elif array_hoja[i_hoja]['avg'] == 'True': 
							array_hoja[i_hoja]['parametros'][i_param]['parametro'] =  obj_tmp_parameter['parametro']
							avg_nota = mtd_get_avg_grade(array_hoja[i_hoja]['parametros'], cat_nota)
							if avg_nota!=None:
								avg_parameters = mtd_set_avg_grade(array_hoja[i_hoja]['parametros'], avg_nota)
								if avg_parameters!=None:
									array_hoja[i_hoja]['parametros'] = avg_parameters
									array_hoja[i_hoja]['estado'] = "True"
									insert_sheet_attribute(period, project, acttype, activity, 'hoja', json_parser.dumps(array_hoja))
									return ""
								else:
									return "No se pudo actualizar el parámetro"
							else:
								return "No se pudo actualizar el parámetro"
						#*****Termina cuando esta activado AVG *******
					i_param+=1
				else:
					return "El total de la ponderación excede la nota de la categoría"
			i_hoja+=1
	else:
		return "ERROR: no existe hoja de calificacion."

	return "No se pudo actualizar el parámetro"

@auth.requires_login()
@auth.requires(auth.has_membership('Student'))
def mtd_remove_parameter(period, idcat, project, acttype, activity, idparam):
	array_hoja = sheet_to_array(get_sheet_attribute(period, project, acttype, activity, 'hoja'))
	if (array_hoja!=None):
		i_hoja=0
		for categoria in array_hoja:
			if str(categoria['idcat']) == str(idcat): #Encontrando la categoría
				cat_nota= int(array_hoja[i_hoja]['nota'])
				i_param = 0
				for parametro in array_hoja[i_hoja]['parametros']:
					if str(parametro['idparam']) == str(idparam): #Encontrando el parametro
						array_hoja[i_hoja]['parametros'].pop(i_param)
						if array_hoja[i_hoja]['avg'] == 'False':
							array_hoja[i_hoja]['estado'] = "False"
							insert_sheet_attribute(period, project, acttype, activity, 'hoja', json_parser.dumps(array_hoja))
							return True
							#Validar cambio de estado para las categorias y hoja completa
						elif array_hoja[i_hoja]['avg'] == 'True': # Promediando notas cuando esta activado AVG
							avg_nota = mtd_get_avg_grade(array_hoja[i_hoja]['parametros'], cat_nota)
							if avg_nota!= None:
								avg_parameters = mtd_set_avg_grade(array_hoja[i_hoja]['parametros'], avg_nota)
								if avg_parameters!=None:
									array_hoja[i_hoja]['parametros'] = avg_parameters
									array_hoja[i_hoja]['estado'] = "True"
									insert_sheet_attribute(period, project, acttype, activity, 'hoja', json_parser.dumps(array_hoja))
									return True
								else:
									return False
							else:
								return False
						else:
							return False
					i_param += 1
			i_hoja+=1
	else:
		return False

	return False
   
@auth.requires_login()
@auth.requires(auth.has_membership('Student'))
def mtd_save_parameter(period, idcat, project, acttype, activity, new_parameter):
	log = ""
	array_hoja = sheet_to_array(get_sheet_attribute(period, project, acttype, activity, 'hoja'))
	#print "***************** imprimiento en mtd_save_parameter *********************"
	if array_hoja!=None:
		if len(array_hoja)>0:
			i_hoja =0
			for categoria in array_hoja:
				if str(categoria['idcat']) == str(idcat):
					cat_nota= int(array_hoja[i_hoja]['nota'])
					cat_indice_nvo = int(array_hoja[i_hoja]['indice']) + 1
					if array_hoja[i_hoja]['avg']== 'False':
						str_tmp_parameter = '{"idparam":"'+str(idcat)+'-'+str(cat_indice_nvo)+'", '+new_parameter
						obj_tmp_parameter = sheet_to_array(str_tmp_parameter)
						if mtd_validar_nota_parametro(array_hoja[i_hoja]['parametros'], cat_nota, obj_tmp_parameter['nota'], 0):
							#print "Listo para guardar parametro"
							array_hoja[i_hoja]['parametros'].append(obj_tmp_parameter)
							array_hoja[i_hoja]['indice'] = cat_indice_nvo						
							#Validar total de las notas de los parametros para cambiar estado de categoría
							if mtd_is_category_ready(array_hoja[i_hoja]['parametros'], cat_nota):
								array_hoja[i_hoja]['estado'] = "True"
							insert_sheet_attribute(period, project, acttype, activity, 'hoja', json_parser.dumps(array_hoja))

							#print array_hoja
							return log
						else:
							#print "La nota no cumple D:"
							return "El total de la ponderación excede la nota de la categoría"
					elif array_hoja[i_hoja]['avg']== 'True':
						#Validar si tiene marcado avg
						str_tmp_parameter = '{"idparam":"'+str(idcat)+'-'+str(cat_indice_nvo)+'", '+new_parameter
						obj_tmp_parameter = sheet_to_array(str_tmp_parameter)
						array_hoja[i_hoja]['parametros'].append(obj_tmp_parameter)
						avg_nota = mtd_get_avg_grade(array_hoja[i_hoja]['parametros'], cat_nota)
						if avg_nota!=None:
							avg_parameters = mtd_set_avg_grade(array_hoja[i_hoja]['parametros'], avg_nota)
							if avg_parameters != None:
								#print "Parametros promediados:"
								#print array_hoja[i_hoja]
								array_hoja[i_hoja]['parametros'] = avg_parameters
								array_hoja[i_hoja]['indice'] = cat_indice_nvo
								array_hoja[i_hoja]['estado'] = "True"
								insert_sheet_attribute(period, project, acttype, activity, 'hoja', json_parser.dumps(array_hoja))
								return log
							else:
								return "Ocurrió un problema al promediar las notas"
						else:
							return "Ocurrió un problema al promediar las notas"
						# ****** Termina validar avg ********
					else:
						return "No se pudo guardar el parámetro"
				i_hoja+=1
			pass
		pass

	return "No se pudo guardar el parámetro."

@auth.requires_login()
@auth.requires(auth.has_membership('Student'))
def mtd_set_avg_grade(array_parametros, avg_nota):
	if array_parametros!= None:
		if len(array_parametros)>0:
			len_parametros = len(array_parametros)
			i_param = 0
			while i_param < len_parametros:
				array_parametros[i_param]['nota'] = avg_nota
				i_param += 1
			return array_parametros
		else:
			return None
	else:
		return None

@auth.requires_login()
@auth.requires(auth.has_membership('Student'))
def mtd_get_avg_grade(array_parametros, cat_nota):
	if array_parametros!=None:
		if len(array_parametros)>0:
			avg_nota = float(cat_nota)/len(array_parametros)
			return round(avg_nota,2)
		else:
			return None
	else:
		return None

#Valida que las notas de los parámetros sumen la nota de la categoria
@auth.requires_login()
@auth.requires(auth.has_membership('Student'))
def mtd_is_category_ready(array_parametros, cat_nota):
	if array_parametros != None:
		if len(array_parametros)>0:
			sum_notas_param = 0
			for parametro in array_parametros:
				sum_notas_param += float(parametro['nota'])
			if sum_notas_param  == float(cat_nota):
				return True
			else:
				return False
		else:
			return False
	else:
		return False

#Valida que la suma del parametro nuevo o actualizado con los parametros existentes no sea mayor a la nota de la categoria
#array_parametros = arreglo de los parametros de la categoria
#cat_nota = nota de la categoria
#param_nota = nota del parametro nuevo o actualizado
#old_param_nota = nota antigua del parametro si está actualizando, de la contrario 0
@auth.requires_login()
@auth.requires(auth.has_membership('Student'))
def mtd_validar_nota_parametro(array_parametros, cat_nota, param_nota, old_param_nota): 
	if array_parametros!=None:
		if len(array_parametros)>0:
			sum_notas_param=0
			for parametro in array_parametros:
				sum_notas_param+= float(parametro['nota'])
			sum_notas_param+=float(param_nota)
			sum_notas_param= sum_notas_param - float(old_param_nota)
			if sum_notas_param<=float(cat_nota):
				return True
			else:
				return False
		else:
			if float(param_nota)<=float(cat_nota):
				return True
			else:
				return False
	else:
		return False

@auth.requires_login()
@auth.requires(auth.has_membership('Student'))
def mtd_save_category(period, project, acttype, activity, new_category, actname):
	log=""
	array_hoja = sheet_to_array(get_sheet_attribute(period, project, acttype, activity, 'hoja'))
	total_hoja = get_sheet_attribute(period, project, acttype, activity, 'total')
	nombre_hoja = get_sheet_attribute(period, project, acttype, activity, 'nombre')
	indice_hoja = get_sheet_attribute(period, project, acttype, activity, 'indice')

	if (array_hoja!=None) & (total_hoja!=None) & (nombre_hoja!= None) & (indice_hoja!=None):
		new_indice=int(indice_hoja)+1
		new_category = '{"idcat":"cat'+str(new_indice)+'", '+new_category
		obj_new_category= sheet_to_array(new_category)
		total_nvo = float(total_hoja)+float(sheet_to_array(new_category)['nota'])
		if (total_nvo>0) & (total_nvo<=100):
			array_hoja.append(obj_new_category)
			insert_sheet_attribute(period, project, acttype, activity, 'hoja', json_parser.dumps(array_hoja))
			insert_sheet_attribute(period, project, acttype, activity, 'total', (total_nvo))
			insert_sheet_attribute(period, project, acttype, activity, 'nombre', (actname))
			insert_sheet_attribute(period, project, acttype, activity, 'indice', new_indice)
			insert_sheet_attribute(period, project, acttype, activity, 'idactividad', activity)
		else:
			log = T('The total weighting exceeds 100 points.')
	else:
		new_category = '[{"idcat":"cat'+str(1)+'", '+new_category+']'
		total_nvo = float(sheet_to_array(new_category)[0]['nota'])
		if (total_nvo>0) & (total_nvo<=100):
			insert_sheet_attribute(period, project, acttype, activity, 'hoja', (new_category))
			insert_sheet_attribute(period, project, acttype, activity, 'total', (total_nvo))
			insert_sheet_attribute(period, project, acttype, activity, 'nombre', (actname))
			insert_sheet_attribute(period, project, acttype, activity, 'indice', 1)
			insert_sheet_attribute(period, project, acttype, activity, 'idactividad', activity)
		else:
			log = T('The total weighting exceeds 100 points.')

	return log	

@auth.requires_login()
@auth.requires(auth.has_membership('Student'))
def mtd_update_category(period, project, acttype, activity, updated_category, idcat):
	array_hoja = sheet_to_array(get_sheet_attribute(period, project, acttype, activity, 'hoja'))
	total_hoja = get_sheet_attribute(period, project, acttype, activity, 'total')
	#print "********************Imprimiendo en update_category********************"
	if (array_hoja!=None) & (total_hoja!=None):
		i_hoja =0
		for categoria in array_hoja:
			if str(categoria['idcat']) == str(idcat):
				#old_cat_nota= int(array_hoja[i_hoja]['nota']) --- Verificar !!!
				array_updated_cat = sheet_to_array(updated_category)
				total_nvo = float(total_hoja)-float(categoria['nota']) + float(array_updated_cat['nota'])

				array_hoja[i_hoja]['categoria']= array_updated_cat['categoria']
				array_hoja[i_hoja]['nota']= array_updated_cat['nota']
				array_hoja[i_hoja]['avg']= array_updated_cat['avg']
				cat_nota= int(array_hoja[i_hoja]['nota'])

				if (total_nvo>0) & (total_nvo<=100):
					if array_hoja[i_hoja]['avg']=='False':
						
							if (mtd_validar_suma_parametros(array_hoja[i_hoja]['parametros'], cat_nota)==False):
								return "La nota de la categoría es menor que la sumatoria de los parametros"

							#Cambiando estado si se modifico la nota de la categoría
							if (mtd_validar_misma_suma(array_hoja[i_hoja]['parametros'], cat_nota)==False):
								array_hoja[i_hoja]['estado'] = "False"
							else:
								array_hoja[i_hoja]['estado'] = "True"
							
							#print array_hoja
							insert_sheet_attribute(period, project, acttype, activity, 'total', (total_nvo))
							insert_sheet_attribute(period, project, acttype, activity, 'hoja', json_parser.dumps(array_hoja))
							return ""
					elif array_hoja[i_hoja]['avg']=='True':
						if len(array_hoja[i_hoja]['parametros'])==0: #Cuando la cat no tiene parámetros pero se edita
							array_hoja[i_hoja]['estado'] = "False"
							insert_sheet_attribute(period, project, acttype, activity, 'total', (total_nvo))
							insert_sheet_attribute(period, project, acttype, activity, 'hoja', json_parser.dumps(array_hoja))
							return ""
						else:
							avg_nota = mtd_get_avg_grade(array_hoja[i_hoja]['parametros'], cat_nota)
							if avg_nota!=None:
								avg_parameters = mtd_set_avg_grade(array_hoja[i_hoja]['parametros'], avg_nota)
								if avg_parameters != None:
									array_hoja[i_hoja]['parametros'] = avg_parameters
									array_hoja[i_hoja]['estado'] = "True"
									insert_sheet_attribute(period, project, acttype, activity, 'total', (total_nvo))
									insert_sheet_attribute(period, project, acttype, activity, 'hoja', json_parser.dumps(array_hoja))
									return ""
								else:
									return "ERROR: no se pudo promediar la nota"	
							else:
								return "ERROR: no se pudo promediar la nota"
				else:
						return T('The total weighting exceeds 100 points.')
			i_hoja+=1
	return "ERROR: no existe hoja ni ponderacion total"

@auth.requires_login()
@auth.requires(auth.has_membership('Student'))
def mtd_validar_misma_suma(array_parametros, cat_nota):
	if array_parametros!=None:
		if len(array_parametros)>0:
			sum_notas_param = 0
			for parametro in array_parametros:
				sum_notas_param+= float(parametro['nota'])
			if cat_nota== sum_notas_param:
				return True

	return False

# Valida que  nota de la categoria sea mayor o igual a la suma de sus parámetros
@auth.requires_login()
@auth.requires(auth.has_membership('Student'))
def mtd_validar_suma_parametros(array_parametros, cat_nota):
	if array_parametros!=None:
		if len(array_parametros)>0:
			sum_notas_param = 0
			for parametro in array_parametros:
				sum_notas_param+= float(parametro['nota'])
			if cat_nota>= sum_notas_param:
				return True
		else:
			return True

	return False

@auth.requires_login()
@auth.requires(auth.has_membership('Student'))
def mtd_remove_category(period, project, acttype, activity, idcat):
	array_hoja = sheet_to_array(get_sheet_attribute(period, project, acttype, activity, 'hoja'))
	total_hoja = get_sheet_attribute(period, project, acttype, activity, 'total')
	if (array_hoja!=None) & (total_hoja!=None):
		i_hoja=0
		for categoria in array_hoja:
			if str(categoria['idcat']) == str(idcat):
				total_nvo = float(total_hoja)-float(categoria['nota'])
				array_hoja.pop(i_hoja)
				insert_sheet_attribute(period, project, acttype, activity, 'total', (total_nvo))
				insert_sheet_attribute(period, project, acttype, activity, 'hoja', json_parser.dumps(array_hoja))
				return True
			i_hoja+=1
	else:
		return False

	return False

@auth.requires_login()
@auth.requires(auth.has_membership('Student'))
def sheet_to_array(string_hoja):
	if string_hoja!= None:
		json_hoja = json_parser.loads(string_hoja)
		return json_hoja
	else:
		return None

@auth.requires_login()
@auth.requires(auth.has_membership('Student'))
def get_sheet_attribute(period, project, acttype, activity, attribute):
	attribute_sheet = redis_db_2.hget('per:'+period+':idp:'+project+':tipo:'+acttype+':ida:'+activity, attribute)
	return attribute_sheet

@auth.requires_login()
@auth.requires(auth.has_membership('Student'))
def insert_sheet_attribute(period, project, acttype, activity, attribute, value):
	return redis_db_2.hset('per:'+period+':idp:'+project+':tipo:'+acttype+':ida:'+activity, attribute, value)