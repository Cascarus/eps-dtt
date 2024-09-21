-- ---------------------------------------------------------------------------------------------------------------------
--                 PROCEDIMIENTOS
-- ---------------------------------------------------------------------------------------------------------------------
-- ---------------------------------------------------------------------------------------------------------------------
--                 PERFIL CATEDRATICO - creacion del perfil de catedratico para cada semestre
-- ---------------------------------------------------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS create_current_teacher_directory;
DELIMITER $$
CREATE PROCEDURE create_current_teacher_directory()
BEGIN
	
    DECLARE cur_period_year, cur_usr_id INT;
    DECLARE cur_name, cur_last_name VARCHAR(128);
	DECLARE cur_email VARCHAR(512);
    DECLARE cursor_List_isdone BOOLEAN DEFAULT FALSE;
    
    DECLARE cursor_List CURSOR FOR
		SELECT distinct usr.id, usr.first_name, usr.last_name, usr.email, py.id
		FROM  auth_user usr
		INNER JOIN auth_membership autm ON usr.id = autm.user_id
		INNER JOIN auth_group aug ON aug.id = autm.group_id
		INNER JOIN user_project usrpj ON usr.id = usrpj.assigned_user 
		INNER JOIN period_year py ON usrpj.period = py.id
		WHERE aug.id = 3 AND py.id = (SELECT (id - 1) FROM period_year ORDER BY id DESC LIMIT 1);
        
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET cursor_List_isdone = TRUE;

    OPEN cursor_List;
    
    loop_list: LOOP
        FETCH cursor_List INTO cur_usr_id, cur_name, cur_last_name, cur_email, cur_period_year;
        IF cursor_List_isdone THEN
			LEAVE loop_List;
		END IF;
        
        IF verify_older_teacher_data(cur_usr_id) THEN
			-- Insercion del ultimo registro que se tenga del catedratico en la tabla mdtt_professor_profile
			INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, id_periodo)
			SELECT user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, (SELECT id FROM period_year ORDER BY id DESC LIMIT 1)
			FROM mdtt_professor_profile
			WHERE user_id = cur_usr_id
			ORDER BY id DESC LIMIT 1;
        ELSE
			-- Insercion de los datos basicos que tenga el catedratico en su usuario
			SET cur_period_year = (SELECT id FROM period_year ORDER BY id DESC LIMIT 1);
			INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, id_periodo)
            VALUES(cur_usr_id, cur_name, cur_last_name, 'Defecto.png', cur_email , 'Pendiente' , 'Pendiente', cur_period_year);
        END IF;
    END LOOP loop_List;
END; $$
DELIMITER ;

-- ---------------------------------------------------------------------------------------------------------------------
--                 RUBRICA - Creacion de rubrica para cada semestre
-- ---------------------------------------------------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS create_current_rubric_forum;
DELIMITER $$
CREATE PROCEDURE create_current_rubric_forum()
BEGIN
    DECLARE current_period_id, current_forum_id INT;
    DECLARE cur_seccion VARCHAR(100);
    DECLARE cur_puntos DECIMAL(5,2);
    DECLARE cur_estado VARCHAR(30);
    DECLARE cursor_List_isdone BOOLEAN DEFAULT FALSE;
	
    -- Cursor para sacar el detalle de la rubrica del foro
    DECLARE cursor_List CURSOR FOR 
        SELECT rs.seccion, rs.puntos, rs.estado
        FROM mdtt_rubric_section rs
        INNER JOIN mdtt_rubric rub ON rs.id_rubrica = rub.id
        WHERE rub.tipo = 'foro' AND rub.estado = 'activo' AND rub.id_periodo = (SELECT (id - 1) FROM period_year ORDER BY id DESC LIMIT 1);

    DECLARE CONTINUE HANDLER FOR NOT FOUND 
    BEGIN
        SET cursor_List_isdone = TRUE;
    END;
	
    -- Variable para el 
    SET current_period_id = (SELECT id FROM period_year ORDER BY id DESC LIMIT 1);

    INSERT INTO mdtt_rubric(fecha_creacion, estado, tipo, id_periodo) 
    VALUES(CURDATE(), 'activo', 'foro', current_period_id);
    SET current_forum_id = (SELECT LAST_INSERT_ID());

    OPEN cursor_List;
    loop_list: LOOP
        FETCH cursor_List INTO cur_seccion, cur_puntos, cur_estado;
        IF cursor_List_isdone THEN
            LEAVE loop_list;
        END IF;
        INSERT INTO mdtt_rubric_section(id_rubrica, seccion, puntos, estado)
        VALUES(current_forum_id, cur_seccion, cur_puntos, cur_estado);
    END LOOP loop_list;
    CLOSE cursor_List;

END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS create_current_rubric_conference;
DELIMITER $$
CREATE PROCEDURE create_current_rubric_conference()
BEGIN
    DECLARE current_period_id, current_conference_id INT;
    DECLARE cur_seccion VARCHAR(100);
    DECLARE cur_puntos DECIMAL(5,2);
    DECLARE cur_estado VARCHAR(30);
    DECLARE cursor_List_isdone BOOLEAN DEFAULT FALSE;

    DECLARE cursor_List CURSOR FOR 
        SELECT rs.seccion, rs.puntos, rs.estado
        FROM mdtt_rubric_section rs
        INNER JOIN mdtt_rubric rub ON rs.id_rubrica = rub.id
        WHERE rub.tipo = 'conferencia' AND rub.estado = 'activo' AND rub.id_periodo = (SELECT (id - 1) FROM period_year ORDER BY id DESC LIMIT 1);

    DECLARE CONTINUE HANDLER FOR NOT FOUND 
    BEGIN
        SET cursor_List_isdone = TRUE;
    END;

    SET current_period_id = (SELECT id FROM period_year ORDER BY id DESC LIMIT 1);

    INSERT INTO mdtt_rubric(fecha_creacion, estado, tipo, id_periodo) 
    VALUES(CURDATE(), 'activo', 'conferencia', current_period_id);
    SET current_conference_id = (SELECT LAST_INSERT_ID());

    OPEN cursor_List;
    loop_list: LOOP
        FETCH cursor_List INTO cur_seccion, cur_puntos, cur_estado;
        IF cursor_List_isdone THEN
            LEAVE loop_list;
        END IF;
        INSERT INTO mdtt_rubric_section(id_rubrica, seccion, puntos, estado)
        VALUES(current_conference_id, cur_seccion, cur_puntos, cur_estado);
    END LOOP loop_list;
    CLOSE cursor_List;

END$$
DELIMITER ;

/* ---------------------------------------------------------------------------------------------------------------------
                 FOROS - Valida las fechas de corte del foro y genera notas
                         automaticas para los que no entreagaron
-- ---------------------------------------------------------------------------------------------------------------------*/
DROP PROCEDURE IF EXISTS validate_date_forums;
DELIMITER $$
CREATE PROCEDURE validate_date_forums()
BEGIN
    DECLARE current_period_id, cur_forum_id INT;
    DECLARE cur_forum_fecha_corte DATETIME;
    DECLARE cur_students_id , cur_students_id_pj INT;
    DECLARE done INT DEFAULT FALSE;
    
    -- primer cursor para obtener foros activos
    DECLARE cursor_active_forums CURSOR FOR 
        SELECT id, fecha_corte FROM mdtt_forum_semester WHERE estado = 'activo' AND id_periodo = current_period_id;
    
    -- segundo cursor para obtener a los estudiantes que no entregaron el foro
    DECLARE cursor_students CURSOR FOR
        SELECT aus.id, pj.id
        FROM auth_membership aum 
        INNER JOIN auth_user aus ON aum.user_id = aus.id
        INNER JOIN auth_group aug ON aum.group_id = aug.id
        INNER JOIN user_project usrp ON usrp.assigned_user = aus.id
        INNER JOIN project pj ON usrp.project = pj.id
        LEFT JOIN mdtt_forum mf ON aus.id = mf.id_estudiante AND mf.id_foro_semestre = cur_forum_id and mf.id_proyecto = pj.id
        WHERE aug.role = 'Student' 
          AND usrp.period = current_period_id 
          AND pj.area_level = 1 
          AND usrp.pro_bono = 'F' 
          AND mf.id_estudiante IS NULL;
    
    -- Un solo handler para ambos cursores
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    SET current_period_id = (SELECT id FROM period_year ORDER BY id DESC LIMIT 1);
    
    OPEN cursor_active_forums;
    active_forums_loop: LOOP
        FETCH cursor_active_forums INTO cur_forum_id, cur_forum_fecha_corte;
        IF done THEN
            LEAVE active_forums_loop;
        END IF;
        
        -- se valida que la fecha de corte ya haya pasado
        IF cur_forum_fecha_corte IS NOT NULL AND cur_forum_fecha_corte < NOW() THEN
            UPDATE mdtt_forum_semester SET estado = 'inactivo' WHERE id = cur_forum_id;
            
            SET done = FALSE;
            OPEN cursor_students;
            
            students_loop: LOOP
                FETCH cursor_students INTO cur_students_id, cur_students_id_pj;
                IF done THEN
                    LEAVE students_loop;
                END IF;
                
                INSERT INTO mdtt_forum(id_foro_semestre, id_estudiante, id_proyecto, estado, nota, fecha_calificacion, observaciones)
                VALUES(cur_forum_id, cur_students_id, cur_students_id_pj, 'sin entrega', 0, NOW(), 'No entrego'); 
            
            END LOOP students_loop;
            CLOSE cursor_students;
        END IF;
        
        SET done = FALSE;
    END LOOP active_forums_loop;
    CLOSE cursor_active_forums;

END$$
DELIMITER ;


/* ---------------------------------------------------------------------------------------------------------------------
                 FOROS - Valida las fechas de corte de las prorrogas de los foros
-- ---------------------------------------------------------------------------------------------------------------------*/
DROP PROCEDURE IF EXISTS validate_extention_date_forums;
DELIMITER $$
CREATE PROCEDURE validate_extention_date_forums()
BEGIN
    DECLARE current_period_id, cur_forum_id INT;
    DECLARE cur_fecha_corte DATETIME;
    DECLARE done1 INT DEFAULT FALSE;
	
    -- cursor para obtener foros con prorroga
    DECLARE cursor_active_extentions CURSOR FOR 
        -- SELECT mf.id, mf.estado, mfs.id_periodo, mfe.extention_date
		SELECT mf.id, mfe.extention_date
        FROM mdtt_forum mf
		INNER JOIN mdtt_forum_semester mfs ON mf.id_foro_semestre = mfs.id
		INNER JOIN (
			SELECT id_forum as id, MAX(extention_date) AS extention_date
			FROM mdtt_forum_extension
			GROUP BY id_forum
		) mfe ON mfe.id = mf.id
		WHERE mf.estado = 'prorroga'
			AND mfs.id_periodo = current_period_id;
	
    DECLARE CONTINUE HANDLER FOR NOT FOUND 
    BEGIN
        SET done1 = TRUE;
    END;
	
    SET current_period_id = (SELECT id FROM period_year ORDER BY id DESC LIMIT 1);
	
    OPEN cursor_active_extentions;
    active_extentions: LOOP
        FETCH  cursor_active_extentions INTO cur_forum_id, cur_fecha_corte;
        IF done1 THEN
            LEAVE active_extentions;
        END IF;
        
        -- se valida que la fecha de corte ya haya pasado
        IF cur_fecha_corte IS NOT NULL AND cur_fecha_corte < NOW() THEN
			UPDATE mdtt_forum 
            SET 
				estado = 'sin entrega',
                fecha_calificacion = NOW(),
                observaciones = 'No entrego'
			WHERE id = cur_forum_id;
		END IF;
        
    END LOOP active_extentions;
    CLOSE cursor_active_extentions;

END$$
DELIMITER ;

-- ---------------------------------------------------------------------------------------------------------------------
--                 FUNCIONES
-- ---------------------------------------------------------------------------------------------------------------------
-- ---------------------------------------------------------------------------------------------------------------------
--                 PERFIL CATEDRATICO - verifica si el usuario cuenta con data vieja 
-- ---------------------------------------------------------------------------------------------------------------------
DROP FUNCTION IF EXISTS verify_older_teacher_data;
DELIMITER //
CREATE FUNCTION verify_older_teacher_data(
    dir_teacher_id INT
)
RETURNS BOOL
BEGIN
    DECLARE res BOOL;
    DECLARE condicion INT;

    SET condicion = (
        SELECT COUNT(id)
        FROM mdtt_professor_profile
        WHERE user_id = dir_teacher_id
    );

    IF condicion > 0 THEN
        SET res = TRUE; -- el usuario si tiene registro en la tabla 
    ELSE
        SET res = FALSE; -- el usuario no tiene ningun registro en la tabla
    END IF;

    RETURN res;
END; //
DELIMITER ;

SELECT verify_older_teacher_data(6257);