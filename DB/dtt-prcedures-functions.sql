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