CREATE TABLE mdtt_parameters(
	id INT AUTO_INCREMENT PRIMARY KEY,
    mdtt_parameter_name VARCHAR(500),
    mdtt_parameter_value_string VARCHAR(500),
    mdtt_parameter_value_number DECIMAL(5,2),
    updated_by INT,
    updated_date datetime
);

CREATE TABLE mdtt_forum_semester( -- foro_semestre
	id int auto_increment PRIMARY KEY,
    nombre_foro VARCHAR(500),
    fecha_corte DATETIME, -- fecha en la que se deja de recibir respuestas
    fecha_apertura DATETIME, -- fecha en la que inicia a recibir respuestas
    estado VARCHAR(30), -- activo, finalizado, eliminado
    id_periodo int -- id del periodo 
);

CREATE TABLE mdtt_conference_semester( -- conference_semeste
	id int auto_increment PRIMARY KEY,
    fecha_corte DATETIME, -- fecha en la que se deja de recibir respuestas
    fecha_apertura DATETIME, -- fecha en la que inicia a recibir respuestas
    estado VARCHAR(30), -- activo, finalizado, eliminado
    id_periodo int -- id del periodo 
);

CREATE TABLE mdtt_penalty( -- penalizacion
	id int auto_increment PRIMARY KEY,
    nombre VARCHAR(100),
    descripcion VARCHAR(500),
    tipo VARCHAR(30), -- f->foro, c->conferencias
	penalizacion DECIMAL(5,2),
    estado VARCHAR(30) -- a-> activo, i->inactivo, e->eliminado
);

CREATE TABLE mdtt_rubric( -- rubrica
	id INT AUTO_INCREMENT PRIMARY KEY,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(30), --  a-> activo, i->inactivo, e->eliminado
    tipo VARCHAR(30), -- f->foro, c->conferencias
	id_periodo INT -- id periodo
);

CREATE TABLE mdtt_rubric_section( -- rubrica_detalle
	id INT AUTO_INCREMENT PRIMARY KEY,
    id_rubrica INT,
    seccion VARCHAR(100),
    puntos DECIMAL(5,2),
    estado VARCHAR(30), --  a-> activo, i->inactivo, e->eliminado
    
    CONSTRAINT FK_RUBRICA_SECCION_RUBRICA FOREIGN KEY(id_rubrica) REFERENCES mdtt_rubric(id)
);

CREATE TABLE mdtt_professor_profile( -- perfil_catedratico
	id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    nombre VARCHAR(128),
    apellido VARCHAR(128),
    foto VARCHAR(512),
    correo VARCHAR(512),
    semblanza VARCHAR(1000),
    formacion VARCHAR(1000),
    estado VARCHAR(30) default 'activo',
    id_periodo INT,
    
    CONSTRAINT FK_PEFIL_CATEDRATICO_AUTH_USER FOREIGN KEY(user_id) REFERENCES auth_user(id),
    CONSTRAINT FK_PROF_PROFILE_PERIOD_YEAR FOREIGN KEY(id_periodo) REFERENCES period_year(id)
);

CREATE TABLE mdtt_forum( -- foro
	id INT AUTO_INCREMENT PRIMARY KEY,
    id_proyecto INT,
    id_estudiante INT,
    id_dsi INT,
    id_foro_semestre INT,
    reporte VARCHAR(512),
    nota DECIMAL(5,2) DEFAULT 0,
    estado VARCHAR(30),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_calificacion datetime,
    observaciones VARCHAR(500),
    
    CONSTRAINT FK_FORO_PROYECTO FOREIGN KEY(id_proyecto) REFERENCES project(id),
    CONSTRAINT FK_FORO_ESTUDIANTE FOREIGN KEY(id_estudiante) REFERENCES auth_user(id),
    CONSTRAINT FK_FORO_DSI FOREIGN KEY(id_dsi) REFERENCES auth_user(id),
    CONSTRAINT FK_FORO_SEMESTRE FOREIGN KEY(id_foro_semestre) REFERENCES mdtt_forum_semester(id)
);

CREATE TABLE mdtt_conference( -- conferencia
	id INT AUTO_INCREMENT PRIMARY KEY,
    id_proyecto INT,
    id_estudiante INT,
    id_dsi INT,
    id_periodo int, -- id del periodo ,
	id_conference_semester int,
    nombre_video VARCHAR(512),
    reporte VARCHAR(512),
    video VARCHAR(512),
    portada VARCHAR(512),
    nota DECIMAL(5,2) DEFAULT 0,
    estado_calificacion VARCHAR(30),
    estado_video VARCHAR(30),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_realizacion datetime,
    fecha_calificacion datetime,
    observaciones VARCHAR(500),
    descripcion VARCHAR(1000),
    
    CONSTRAINT FK_CONFERENCIA_PROYECTO FOREIGN KEY(id_proyecto) REFERENCES project(id),
    CONSTRAINT FK_CONFERENCIA_ESTUDIANTE FOREIGN KEY(id_estudiante) REFERENCES auth_user(id),
    CONSTRAINT FK_CONFERENCIA_DSI FOREIGN KEY(id_dsi) REFERENCES auth_user(id),
    CONSTRAINT FK_CONFERENCE_SEMESTER FOREIGN KEY(id_conference_semester) REFERENCES mdtt_conference_semester(id)
);


CREATE TABLE mdtt_grade( -- calificacion
	id INT AUTO_INCREMENT PRIMARY KEY,
    id_conferencia INT,
    id_foro INT,
    tipo VARCHAR(30),
    nota DECIMAL(5,2),
    
    CONSTRAINT FK_CALIFICACION_CONFERENCIA FOREIGN KEY(id_conferencia) REFERENCES mdtt_conference(id),
    CONSTRAINT FK_CALIFICACION_FORO FOREIGN KEY(id_foro) REFERENCES mdtt_forum(id)
);

CREATE TABLE mdtt_grade_detail(
	id INT AUTO_INCREMENT PRIMARY KEY,
    id_grade INT,
    id_rubrica_seccion INT,
    nota_seccion DECIMAL(5,2),
    
    CONSTRAINT FK_GRADE_DET_CALIFICACION FOREIGN KEY(id_grade) REFERENCES mdtt_grade(id),
    CONSTRAINT FK_GRADE_DET_RUBRICA_SECCION FOREIGN KEY(id_rubrica_seccion) REFERENCES mdtt_rubric_section(id)
);

CREATE TABLE mdtt_penalty_detail(
	id INT AUTO_INCREMENT PRIMARY KEY,
    id_grade_detail INT,
    id_penalty INT,
    penalty DECIMAL(5,2),
    
    CONSTRAINT FK_PENALTY_DETAIL_GRADE_DET FOREIGN KEY(id_grade_detail) REFERENCES mdtt_grade_detail(id),
    CONSTRAINT FK_PENLATY_DETAIL_PENALTY FOREIGN KEY(id_penalty) REFERENCES mdtt_penalty(id)
);

CREATE TABLE mdtt_tag( -- tag
	id INT AUTO_INCREMENT PRIMARY KEY,
    tag VARCHAR(100),
    estado VARCHAR(30)
);

CREATE TABLE mdtt_conference_tag( -- conferencia_tag
	id INT AUTO_INCREMENT PRIMARY KEY,
    id_tag INT,
    id_conferencia INT,
    
    CONSTRAINT FK_CONFERENCIA_TAG_TAG FOREIGN KEY(id_tag) REFERENCES mdtt_tag(id),
    CONSTRAINT FK_CONFERENCIA_TAG_CONFERENCIA FOREIGN KEY(id_conferencia) REFERENCES mdtt_conference(id)
);

CREATE TABLE mdtt_forum_extension(
	id INT AUTO_INCREMENT PRIMARY KEY,
    id_forum int,
    id_dsi INT,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    extention_date datetime,
    late_delivery_penalty smallint, -- 1 -> se penaliza; 0 --> no se penaliza
    
    CONSTRAINT FK_FORUM_EXTENSION_FORUM FOREIGN KEY(id_forum) REFERENCES mdtt_forum(id),
    CONSTRAINT FK_FORUM_EXTENSION_DSI FOREIGN KEY(id_dsi) REFERENCES auth_user(id)
);

CREATE TABLE mdtt_conference_extension(
	id INT AUTO_INCREMENT PRIMARY KEY,
    id_conference int,
    id_dsi INT,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    extention_date datetime,
    late_delivery_penalty smallint, -- 1 -> se penaliza; 0 --> no se penaliza
    
    CONSTRAINT FK_CONFERENCE_EXTENSION_CONFERENCE FOREIGN KEY(id_conference) REFERENCES mdtt_conference(id),
    CONSTRAINT FK_CONFERENCE_EXTENSION_DSI FOREIGN KEY(id_dsi) REFERENCES auth_user(id)
);