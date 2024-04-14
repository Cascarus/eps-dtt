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
		WHERE aug.id = 3 AND py.id = (SELECT id FROM period_year ORDER BY id DESC LIMIT 1);
        
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET cursor_List_isdone = TRUE;

    OPEN cursor_List;
    
    loop_list: LOOP
        FETCH cursor_List INTO cur_usr_id, cur_name, cur_last_name, cur_email, cur_period_year;
        IF cursor_List_isdone THEN
			LEAVE loop_List;
		END IF;
        
        IF verify_older_teacher_data(cur_usr_id) THEN
			-- Insercion del ultimo registro que se tenga del catedratico en la tabla mdtt_professor_profile
			INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, period_id)
			SELECT user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, (SELECT id FROM period_year ORDER BY id DESC LIMIT 1)
			FROM mdtt_professor_profile
			WHERE user_id = cur_usr_id
			ORDER BY id DESC LIMIT 1;
        ELSE
			-- Insercion de los datos basicos que tenga el catedratico en su usuario
			SET cur_period_year = (SELECT id FROM period_year ORDER BY id DESC LIMIT 1);
			INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, period_id)
            VALUES(cur_usr_id, cur_name, cur_last_name, 'Defecto.png', cur_email , 'Pendiente' , 'Pendiente', cur_period_year);
        END IF;
    END LOOP loop_List;
END; $$
DELIMITER ;


-- ---------------------------------------------------------------------------------------------------------------------
--                 FUNCIONES
-- ---------------------------------------------------------------------------------------------------------------------
-- ---------------------------------------------------------------------------------------------------------------------
--                 PERFIL CATEDRATICO - verifica si el usuario cuenta con data vieja 
-- ---------------------------------------------------------------------------------------------------------------------
DROP FUNCTION verify_older_teacher_data;
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