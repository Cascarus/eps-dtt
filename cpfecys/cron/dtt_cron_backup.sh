#!/bin/bash
######################################################
######################################################
### Daniel Alexander Cos Pirir                     ###
### DTT - Desarrollo de Transferencia Tecnologica  ###
### Escuela de Ingenieria en Ciencias y Sistemas   ###
### Universidad de San Carlos de Guatemala         ###
### 2017   CopyRight                               ###
######################################################
######################################################

#DECLARACION DE VARIABLES
database="cpfecys"
db_user="root"
db_pass="-pecysx86" #Para colocar un password anteponerle -p seguido del password, ejemplo: dbpass="-pContraseña"
db_userbkp="bkpuser"
db_passbkp="3cy5b4ckup"
bk_ruta_temp="/temp/mariabackup/"
bk_temp_log="/temp/mariabackup/backup.log"

#LEER LA CONFIGURACION DE LA BASE DE DATOS

i=-1
while read -a row
do
	if (( $i >= 0));
		then
		resultado[0]=${row[0]} #id
		resultado[1]=${row[1]} #fecha_proximio
		resultado[2]=${row[2]} #tipo
		resultado[3]=${row[3]} #ruta
		resultado[4]=${row[4]} #servidor
		resultado[5]=${row[5]} #puerto
		resultado[6]=${row[6]} #usuario
		resultado[7]=${row[7]} #clave
		resultado[8]=${row[8]} #cantidad
	fi	
	i=$((i+1))
done < <(echo "SELECT id, fecha_proximo, tipo, ruta, servidor, puerto, usuario, clave, cantidad FROM backup_configuration WHERE estado='A';" | mysql $database -u $db_user $db_pass)


#VARIABLES PARA CONEXION SSH
bk_id="${resultado[0]}"
bk_fecha="${resultado[1]}"
bk_tipoconf="${resultado[2]}"
ssh_ruta="${resultado[3]}"
ssh_server="${resultado[4]}"
#ssh_server="45.55.151.88"
ssh_port="${resultado[5]}"
#ssh_port="22"
ssh_user="${resultado[6]}"
#ssh_user="root"
ssh_pass="${resultado[7]}"
#ssh_pass="dtt@7887"
bk_cantidad="${resultado[8]}"

if [ -z "$bk_id" ]; #No existe configuración activa
	then
	echo "No existe configuración activa"
	exit 1
fi

now="$(date +'%Y-%m-%d')"
if [ "$bk_fecha" != "$now" ]; #No esite backup configurado para hoy
	then
	echo "No existe backup configurado para hoy"
	exit 1
fi

#CALCULO DE TODAS LAS RUTAS
bk_tipo=""
ssh_raiz=""
ssh_dir=""
ssh_nombre=""
ssh_recover="recover_backup.sh"

if [ "$bk_tipoconf" = "U" ];
	then
	ssh_dir="Backup_Unico_$bk_fecha/"
	ssh_raiz="$ssh_ruta$ssh_dir"
	ssh_nombre="unico"
	bk_tipo="C"
elif [ "$bk_tipoconf" = "I" ];
	then
	dia="$(date +%u)"
	ssh_dir="Backup_Semana_$(date --date="-$((dia-1)) day" +'%Y-%m-%d')/"
	ssh_raiz="$ssh_ruta$ssh_dir"
	#Se verifica si existe algun backup completo realizado anteriormente
	while read -a row
	do
		exist=${row[0]}
	done < <(echo "SELECT id FROM backup_history WHERE ruta='$ssh_raiz' AND estado='E' AND tipo='C' ORDER BY fecha DESC LIMIT 0,1" | mysql $database -u $db_user $db_pass)
	if [ -z "$exist" ];
		then
		ssh_nombre="base"
		bk_tipo="C"
	else
		ssh_nombre="inc$((dia-1))"
		bk_tipo="I"
	fi
fi


#VERIFICACION DE LA CONEXION POR SSH
sshpass -p "$ssh_pass" ssh $ssh_user@$ssh_server -p $ssh_port -o "StrictHostKeyChecking no" exit
if [ "$?" = "0" ];
	then

	#CREACION DE TODAS LAS RUTAS Y ARCHIVOS
	#bk_ruta_temp
	if [ -d "$bk_ruta_temp" ];
		then
		rm -r "$bk_ruta_temp"
	fi
	mkdir -p "$bk_ruta_temp"
	#ssh_raiz
	if sshpass -p "$ssh_pass" ssh $ssh_user@$ssh_server -p $ssh_port -o "StrictHostKeyChecking no"  [ ! -d "$ssh_raiz" ];
		then
		sshpass -p "$ssh_pass" ssh $ssh_user@$ssh_server -p $ssh_port -o "StrictHostKeyChecking no" mkdir -p $ssh_raiz &>> $bk_temp_log
	fi
	#ssh_recover
	if sshpass -p "$ssh_pass" ssh $ssh_user@$ssh_server -p $ssh_port -o "StrictHostKeyChecking no" [ ! -f "$ssh_raiz$ssh_recover" ];
		then
		sshpass -p "$ssh_pass" ssh $ssh_user@$ssh_server -p $ssh_port -o "StrictHostKeyChecking no" touch "$ssh_raiz$ssh_recover" &>> $bk_temp_log
		sshpass -p "$ssh_pass" ssh $ssh_user@$ssh_server -p $ssh_port -o "StrictHostKeyChecking no" chmod 777 "$ssh_raiz$ssh_log" &>> $bk_temp_log
	fi

	#CREACION DE BACKUP
	if [ $bk_tipo = "C" ]; #Completo
		then
		mariabackup --user=$db_userbkp --password=$db_passbkp --backup --target-dir="$bk_ruta_temp$ssh_nombre" &>> $bk_temp_log
	elif [ $bk_tipo = "I" ]; #Incremental
		then

		while read -a row
		do
			ssh_base_ruta=${row[0]} #ruta
			ssh_base_nombre=${row[1]} #nombre
			ssh_base_server=${row[2]} #servidor
			ssh_base_port=${row[3]} #puerto
			ssh_base_user=${row[4]} #usuario
			ssh_base_pass=${row[5]} #clave
		done < <(echo "SELECT ruta,nombre, servidor, puerto, usuario, clave FROM backup_history WHERE ruta='$ssh_raiz' AND estado='E' ORDER BY fecha DESC LIMIT 0,1;" | mysql $database -u $db_user $db_pass)

		#COPIAR POR SCP
		sshpass -p "$ssh_base_pass" scp -P $ssh_base_port -o "StrictHostKeyChecking no" $ssh_base_user@$ssh_base_server:"$ssh_base_ruta$ssh_base_nombre".tar.gz "$bk_ruta_temp"  &>> $bk_temp_log
		#DESCOMPRIMIR BACKUP
		tar -xzvf "$bk_ruta_temp$ssh_base_nombre".tar.gz -C "$bk_ruta_temp"

		mariabackup --user=$db_userbkp --password=$db_passbkp --backup --target-dir="$bk_ruta_temp$ssh_nombre" --incremental-basedir="$bk_ruta_temp$ssh_base_nombre" &>> $bk_temp_log

	fi

	#VERIFICACION DE SI FUE EXITOSO O NO EL PROCESO DE CREACION DE BACKUP
	while read line
	do
		value=$line
	done < $bk_temp_log
		val=$(echo $value | cut -c$((${#value}-2))-$((${#value})) )
	if [ "$val" == "OK!" ];	
		then
		bk_exito="E"
	else
		bk_exito="F"
	fi

	#COMPRESION Y ENVIO DEL BACKUP AL SERVIDOR CONFIGURADO
	if [ "$bk_exito" = "E" ];
		then
		#COMPRIMIR BACKUP
		tar -czvf "$bk_ruta_temp$ssh_nombre".tar.gz -C "$bk_ruta_temp" "$ssh_nombre" &>> $bk_temp_log
		bk_full_name="$bk_ruta_temp$ssh_nombre".tar.gz
		bk_result=$(du -s "$bk_full_name")
		bk_tamanio=$(echo $bk_result | cut -c1-$((${#bk_result}-${#bk_full_name}-1)))
		if [ "$?" != "0" ];
			then
			bk_exito="F"
		fi
		if [ "$bk_exito" = "E" ];
			then
			#ENVIAR POR SCP
			sshpass -p "$ssh_pass" scp -P $ssh_port -o "StrictHostKeyChecking no" "$bk_ruta_temp$ssh_nombre".tar.gz $ssh_user@$ssh_server:$ssh_raiz &>> $bk_temp_log
			if [ "$?" != "0" ];
				then
				bk_exito="F"
			fi
		fi	

		#ESCRITURA DEL ARCHIVO DE RECOVER
		if [  $bk_tipo = "C" ]; #Completo
			then
			txt_recover='#!/bin/bash\n
			ruta_mysql=\"/var/lib/mysql/\"\n
			nombre_temp=\"mysqltemp\"\n
			ruta=\"\$1\"\n
			\n
			\n
			tar -xzvf \"\$ruta\"'$ssh_nombre'.tar.gz -C \"\$ruta\" \n
			mariabackup --prepare --apply-log-only --target-dir=\"\$ruta\"'$ssh_nombre'\n
			\n
			\n
			service mysql stop\n
			if [ -d \$ruta\$nombre_temp ];\n
		  	then\n
		  	rm -r \"\$ruta\$nombre_temp\"\n
			fi\n
			mkdir -p \"\$ruta\$nombre_temp\"\n
			mv \"\$ruta_mysql\"* \"\$ruta\$nombre_temp\"/\n
			mariabackup --copy-back --target-dir=\"\$ruta\"'$ssh_nombre'\n
			sudo chown -R mysql: \$ruta_mysql\n
			service mysql start'
			sshpass -p "$ssh_pass" ssh $ssh_user@$ssh_server -p $ssh_port -o "StrictHostKeyChecking no" 'echo -e "'$txt_recover'" > '$ssh_raiz$ssh_recover
		elif [ $bk_tipo = "I" ]; #Incremental
			then
			txt_recover='tar -xzvf \"\$ruta\"'$ssh_nombre'.tar.gz -C \"\$ruta\"\n
			mariabackup --prepare --apply-log-only --target-dir=\"\$ruta\"base --incremental-dir=\"\$ruta\"'$ssh_nombre'\n'
			txt_recover_tam=$(sshpass -p "$ssh_pass" ssh $ssh_user@$ssh_server -p $ssh_port -o "StrictHostKeyChecking no" 'wc -l < '$ssh_raiz$ssh_recover)
			txt_posicion=$((txt_recover_tam-10))
			sshpass -p "$ssh_pass" ssh $ssh_user@$ssh_server -p $ssh_port -o "StrictHostKeyChecking no" 'sed -i "'$txt_posicion'i '$txt_recover'" '$ssh_raiz$ssh_recover' '
		fi
	fi
	logf=$(<$bk_temp_log)
	log="${logf//\"/\'}"
	#log=cat $bk_temp_log | tr ' ' '\n'

else
	bk_exito="F"
	log="No se pudo establecer la conexion al servidor $ssh_server, puerto $ssh_port, usuario $ssh_user:$ssh_pass"
fi

#CALCULO DE PROXIMA FECHA DE COPIA DE SEGURIDAD
if [ "$bk_tipoconf" = "U" ];
	then
	bk_fecha_proximo=""
	bk_estado="I"
elif [ "$bk_tipoconf" = "I" ];
	then
	bk_fecha_proximo="$(date --date='+1 day' +'%Y-%m-%d')"
	bk_estado="A"
fi
#VERIFICACION DEL EXITO DEL PROCESO
if [ "$bk_exito" = "E" ];
	then
	log="Proceso completado exitosamente"
fi

#ACTUALIZACION DE LA CONFIGURACION
echo "UPDATE backup_configuration SET fecha_proximo=STR_TO_DATE('$bk_fecha_proximo', '%Y-%m-%d'),estado='$bk_estado' WHERE id=$bk_id;" | mysql $database -u $db_user $db_pass
#CREACION BITACORA DE COPIAS DE SEGURIDAD
echo "INSERT INTO backup_history (fecha, tipo, tipoconf, servidor, puerto, usuario, clave, ruta, nombre, estado, tamano, procesolog) VALUES (sysdate(),'$bk_tipo','$bk_tipoconf','$ssh_server','$ssh_port','$ssh_user','$ssh_pass','$ssh_raiz','$ssh_nombre','$bk_exito','$bk_tamanio', \"$log\");" | mysql $database -u $db_user $db_pass

echo "**********************"
echo $log
echo "**********************"
#ELIMINACION DE LOS ULTIMOS BACKUPS
while read -a row
do
	bk_cantidad_total=${row[0]} #ruta
done < <(echo "SELECT count(*) FROM (SELECT DISTINCT servidor,ruta FROM backup_history GROUP BY servidor, ruta ) s1;" | mysql $database -u $db_user $db_pass)

bk_cantidad_total=$((bk_cantidad_total+0))
bk_cantidad=$((bk_cantidad+0))

while : ;
do
	echo "BK_CANTIDAD_TOTAL -- $bk_cantidad_total"
	echo "BK_CANTIDAD -- $bk_cantidad"

	if [ "$bk_cantidad_total" -gt "$bk_cantidad" ];
		then

		while read -a row
		do
			resultado[0]=${row[0]} #servidor
			resultado[1]=${row[1]} #puerto
			resultado[2]=${row[2]} #usuario
			resultado[3]=${row[3]} #clave
			resultado[4]=${row[4]} #ruta
		done < <(echo "SELECT DISTINCT servidor,puerto,usuario,clave,ruta FROM backup_history WHERE tipo='C' ORDER BY id asc LIMIT 0,1;" | mysql $database -u $db_user $db_pass)

		ssh_rm_server="${resultado[0]}"
		ssh_rm_port="${resultado[1]}"
		ssh_rm_user="${resultado[2]}"
		ssh_rm_pass="${resultado[3]}"
		ssh_rm_ruta="${resultado[4]}"

		bk_cantidad_total=$((bk_cantidad_total-1))

		sshpass -p "$ssh_rm_pass" ssh $ssh_rm_user@$ssh_rm_server -p $ssh_rm_port -o "StrictHostKeyChecking no" rm -r "$ssh_rm_ruta"
		echo "DELETE FROM backup_history WHERE ruta='$ssh_rm_ruta' AND servidor='$ssh_rm_server';" | mysql $database -u $db_user $db_pass

	else
		echo "Break"
		break
	fi

done

rm $bk_temp_log #eliminación del log temporal
rm -r $bk_ruta_temp	#eliminacion de la carpeta temporal
