CREATE DATABASE cpfecys;
CREATE DATABASE cpfecys_scheduler;
USE cpfecys;
USE cpfecys_scheduler;
drop database cpfecys;
drop database cpfecys_scheduler;

CREATE TABLE mdtt_forum_semester( -- foro_semestre
	id int auto_increment PRIMARY KEY,
    nombre_foro VARCHAR(500),
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
    id_periodo int, -- id del periodo 
    nombre_video VARCHAR(512),
    reporte VARCHAR(512),
    video VARCHAR(512),
    portada VARCHAR(512),
    nota DECIMAL(5,2) DEFAULT 0,
    estado_calificacion VARCHAR(30),
    estado_video VARCHAR(30),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_calificacion datetime,
    observaciones VARCHAR(500),
    descripcion VARCHAR(1000),
    
    CONSTRAINT FK_CONFERENCIA_PROYECTO FOREIGN KEY(id_proyecto) REFERENCES project(id),
    CONSTRAINT FK_CONFERENCIA_ESTUDIANTE FOREIGN KEY(id_estudiante) REFERENCES auth_user(id),
    CONSTRAINT FK_CONFERENCIA_DSI FOREIGN KEY(id_dsi) REFERENCES auth_user(id)
);

ALTER TABLE mdtt_conference CHANGE COLUMN estado estado_calificacion VARCHAR(30);
ALTER TABLE mdtt_conference ADD COLUMN portada VARCHAR(512);
desc mdtt_conference;

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

DROP TABLE mdtt_forum_extension;
DROP TABLE mdtt_professor_profile;
DROP TABLE mdtt_penalty_detail;
DROP TABLE mdtt_grade_detail;
DROP TABLE mdtt_grade;
DROP TABLE mdtt_conference_tag;
DROP TABLE mdtt_tag;
DROP TABLE mdtt_forum;
DROP TABLE mdtt_conference;
DROP TABLE mdtt_penalty;
DROP TABLE mdtt_rubric_section;
DROP TABLE mdtt_rubric;
DROP TABLE mdtt_forum_semester;

-- ---------------------------------------------------------------------------------------------------------------------
--                    INSERTS
-- ---------------------------------------------------------------------------------------------------------------------
insert into mdtt_forum_semester(nombre_foro, fecha_corte, fecha_apertura,estado, id_periodo)
values('Foro 1', '2024-02-12 23:59:59', '2024-02-11', 'activo', 21);
insert into mdtt_forum_semester(nombre_foro, fecha_corte, fecha_apertura,estado, id_periodo)
values('Foro 2', '2024-02-14 23:59:59', '2024-02-13', 'activo', 21);
insert into mdtt_forum_semester(nombre_foro, fecha_corte, fecha_apertura,estado, id_periodo)
values('Foro 3', '2024-02-16 23:59:59', '2024-02-15', 'activo', 21);
insert into mdtt_forum_semester(nombre_foro, fecha_corte, fecha_apertura,estado, id_periodo)
values('Foro 4', '2024-03-31 23:59:59', '2024-02-15', 'activo', 21);

select * from mdtt_forum_semester;
delete from mdtt_forum_semester where id > 1;

UPDATE mdtt_forum_semester SET estado = 'inactivo' where id = 4;

select * from mdtt_forum;
delete from mdtt_forum where id > 0;
insert into mdtt_forum(id_proyecto, id_estudiante, id_foro_semestre, nombre_foro, reporte, estado)
values(9,3330, 1, 'reporte prueba','PDF reporte de prueba', 'pendiente');
insert into mdtt_forum(id_proyecto, id_estudiante, id_foro_semestre, nombre_foro, reporte, estado)
values(9,3330, 2, 'reporte prueba 2','PDF reporte de prueba 2', 'pendiente');
insert into mdtt_forum(id_proyecto, id_estudiante, id_foro_semestre, nombre_foro, reporte, estado)
values(9,3330, 3, 'reporte prueba 3','PDF reporte de prueba 3', 'pendiente');
insert into mdtt_forum(id_proyecto, id_estudiante, id_foro_semestre, nombre_foro, reporte, estado)
values(89,3371, 1, 'reporte prueba 1 diego','PDF reporte de prueba', 'pendiente');
insert into mdtt_forum(id_proyecto, id_estudiante, id_foro_semestre, nombre_foro, reporte, estado)
values(89,3371, 2, 'reporte prueba 2 diego','PDF reporte de prueba 2', 'pendiente');
insert into mdtt_forum(id_proyecto, id_estudiante, id_foro_semestre, nombre_foro, reporte, estado)
values(89,3371, 3, 'reporte prueba 3 diego','PDF reporte de prueba 3', 'pendiente');

insert into mdtt_forum(id_proyecto, id_estudiante, nombre_foro, reporte, estado)
values(9,3330, 'reporte prueba 6','PDF reporte de prueba 6', 'pendiente');
insert into mdtt_forum(id_proyecto, id_estudiante, nombre_foro, reporte, estado)
values(9,3330, 'reporte prueba 7','PDF reporte de prueba 7', 'pendiente');
insert into mdtt_forum(id_proyecto, id_estudiante, nombre_foro, reporte, estado)
values(9,3330, 'reporte prueba 8','PDF reporte de prueba 8', 'pendiente');
insert into mdtt_forum(id_proyecto, id_estudiante, nombre_foro, reporte, estado)
values(9,3330, 'reporte prueba 9','PDF reporte de prueba 9', 'pendiente');
insert into mdtt_forum(id_proyecto, id_estudiante, nombre_foro, reporte, estado)
values(9,3330, 'reporte prueba 10','PDF reporte de prueba 10', 'pendiente');
insert into mdtt_forum(id_proyecto, id_estudiante, nombre_foro, reporte, estado)
values(9,3330, 'reporte prueba 11','PDF reporte de prueba 11', 'pendiente');
insert into mdtt_forum(id_proyecto, id_estudiante, nombre_foro, reporte, estado)
values(9,3330, 'reporte prueba 12','PDF reporte de prueba 12', 'pendiente');
insert into mdtt_forum(id_proyecto, id_estudiante, nombre_foro, reporte, estado)
values(9,3330, 'reporte prueba 13','PDF reporte de prueba 13', 'pendiente');

insert into mdtt_conference(id_proyecto, id_estudiante, id_periodo, nombre_video, reporte, video, estado, descripcion)
values(9,3330, 22, 'video de prueba','conference.Tarea-Temperatura-Grupo-8.pdf', 'URL video', 'pendiente', 'este es el primer video de prueba por un estudiante');

INSERT INTO mdtt_penalty(nombre, descripcion, penalizacion, estado, tipo)
values('penalizacion prueba 1', 'penalizacion que se utiliza para pruebas', 30.0, 'activo', 'foro');
INSERT INTO mdtt_penalty(nombre, descripcion, penalizacion, estado, tipo)
values('penalizacion prueba 2', 'penalizacion que se utiliza para pruebas', 10.0, 'activo', 'conferencia');
INSERT INTO mdtt_penalty(nombre, descripcion, penalizacion, estado, tipo)
values('penalizacion prueba 3', 'esta no se deberia ver xq esta inactiva', 50.0, 'inactivo', 'conferencia');
INSERT INTO mdtt_penalty(nombre, descripcion, penalizacion, estado, tipo)
values('penalizacion prueba 4', 'esta no se deberia ver xq esta eliminada', 55.0, 'eliminado', 'foro');

UPDATE mdtt_penalty
SET tipo = 'conferencia'
WHERE tipo = 'Conferencia';

select * FROM mdtt_penalty;

INSERT INTO mdtt_rubric(fecha_creacion, estado, tipo, id_periodo)
VALUES(CURDATE(), 'activo', 'foro', 21);
INSERT INTO mdtt_rubric(fecha_creacion, estado, tipo, id_periodo)
VALUES('2023-08-17', 'activo', 'foro', 20);
INSERT INTO mdtt_rubric(fecha_creacion, estado, tipo, id_periodo)
VALUES(CURDATE(), 'activo', 'conferencia', 21);

SELECT * FROM mdtt_rubric;

DELETE FROM mdtt_rubric WHERE id = 10;

INSERT INTO mdtt_rubric_section(id_rubrica, seccion, puntos, estado)
values(2,'Seccion 1 de foro', 60.0, 'activo');
INSERT INTO mdtt_rubric_section(id_rubrica, seccion, puntos, estado)
values(2,'Seccion 2 de foro', 40.0, 'activo');
INSERT INTO mdtt_rubric_section(id_rubrica, seccion, puntos, estado)
values(1, 'Seccion 1 de foro', 70.0, 'activo');
INSERT INTO mdtt_rubric_section(id_rubrica, seccion, puntos, estado)
values(1, 'Seccion 2 de foro', 30.0, 'activo');
INSERT INTO mdtt_rubric_section(id_rubrica, seccion, puntos, estado)
values(3, 'Seccion 1 de conferencia', 70.0, 'activo');
INSERT INTO mdtt_rubric_section(id_rubrica, seccion, puntos, estado)
values(3, 'Seccion 2 de conferencia', 30.0, 'activo');

SELECT LAST_INSERT_ID();

SELECT * FROM mdtt_rubric_section;
CALL create_current_rubric_forum();
CALL create_current_rubric_conference();

UPDATE mdtt_rubric
SET estado = 'inactivo'
WHERE id = 2;


UPDATE auth_user
SET password = (SELECT password FROM auth_user WHERE id = 3330)
WHERE id = 947;

UPDATE auth_user
SET password = (SELECT password FROM auth_user WHERE id = 3330)
WHERE id = 1;

UPDATE auth_user
SET password = (SELECT password FROM auth_user WHERE id = 3330)
WHERE id = 1529;

UPDATE auth_user
SET password = (SELECT password FROM auth_user WHERE id = 3330)
WHERE id = 228;

UPDATE auth_user
SET password = (SELECT password FROM auth_user WHERE id = 3330)
WHERE id = 247;

UPDATE auth_user
SET password = (SELECT password FROM auth_user WHERE id = 3330)
WHERE id = 230;

UPDATE auth_user
SET password = (SELECT password FROM auth_user WHERE id = 3330)
WHERE id = 272;

UPDATE auth_user
SET password = (SELECT password FROM auth_user WHERE id = 3330)
WHERE id = 6788;

UPDATE auth_user
SET password = (SELECT password FROM auth_user WHERE id = 3330)
WHERE id = 3371;

UPDATE auth_user
SET password = (SELECT password FROM auth_user WHERE id = 3330)
WHERE id = 6257;

UPDATE auth_user
SET password = (SELECT password FROM auth_user WHERE id = 3330)
WHERE id = 5214;

UPDATE auth_user
SET password = (SELECT password FROM auth_user WHERE id = 3330)
WHERE id = 6286;


select CURDATE();
-- 947 --- 201325533
-- 1529 -- 198830600
-- 6257 -- 20181550
-- 228 --- 17625
-- 247 --- 13858
-- 230 --- 20080862
-- 272 --- 9516463
-- 6788 -- 20050320
-- 3371 --- 201602723
-- 5214 --- 201905743
-- 6286 --- 202002793


select * from auth_user where first_name like '%JOSÉ VALERIO%' and last_name like '%CHOC MIJANGOS%';
-- 13858 6257

INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, id_periodo)
VALUES(228, 'Herman Igor', 'Veliz Linares', 'Defecto.png', 'correo1@prueba.com', 'Esta es una semblanza de prueba la cual debería ocupar un espacio máximo de unas 1000 líneas, para eso me puse a escribir cualquier babosada que se me vino a la cabeza con tal de ocupar todo el espacio
que se pueda ya que no sé si siquiera van
jalar los enters con signo y solo así pero bueno vamos a ver qué ocurre', 'formacion1, formacion 2, formacion 3', 'activo', 19);

INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, id_periodo)
VALUES(6257, 'Álvaro Giovanni', 'Longo', 'Defecto.png', 'correo1@prueba.com', 'Esta es una semblanza de prueba la cual debería ocupar un espacio máximo de unas 1000 líneas, para eso me puse a escribir cualquier babosada que se me vino a la cabeza con tal de ocupar todo el espacio
que se pueda ya que no sé si siquiera van
jalar los enters con signo y solo así pero bueno vamos a ver qué ocurre', 'formacion1, formacion 2, formacion 3', 'activo', 19);

INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, id_periodo)
VALUES(247, 'Otto', 'Escobar Leiva', 'que-hay-que-hacer-para-ser-catedratico-1.jpg', 'correo1@prueba.com', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Proin id lorem sit amet lorem malesuada fermentum. Fusce sed nisi in quam tincidunt condimentum.Quisque ullamcorper, justo eu tempor convallis, lorem justo luctus purus, non commodo odio ligula vel libero. Nulla auctor felis id ex volutpat, ac fringilla nunc tempor. Aliquam eget sapien ac lectus aliquam ullamcorper.

Sed consequat, libero id consequat dapibus, ex urna dapibus velit, id ultricies metus tortor vel velit. Aenean et ante non turpis sodales vehicula. Vivamus nec mi ut erat laoreet accumsan. Vestibulum tincidunt dui velit, non tempor enim pellentesque ut.

Nam venenatis urna vel eros rutrum, sed tempus dui ultrices. Proin fermentum varius ligula, at fermentum lorem commodo ac. Integer id odio quis turpis bibendum vehicula. In hac habitasse platea dictumst. Vivamus sit amet urna a sem finibus luctus.', 'Doctor of Philosophy in Mechanical Engineering - Rice University,
Maestro en Ciencias en Ingeniería Mecánica - University of Washington,
Ingeniero Electronico - USAC', 'activo', 19);

INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, id_periodo)
VALUES(1521, 'Jose Anibal', 'Silva', 'que-hay-que-hacer-para-ser-catedratico-1.jpg', 'correo1@prueba.com', 'Esta es una semblanza de prueba la cual debería ocupar un espacio máximo de unas 1000 líneas, para eso me puse a escribir cualquier babosada que se me vino a la cabeza con tal de ocupar todo el espacio
que se pueda ya que no sé si siquiera van
jalar los enters con signo y solo así pero bueno vamos a ver qué ocurre', 'formacion1, formacion 2, formacion 3', 'activo', 19);


INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, id_periodo)
VALUES(228, 'Herman Igor', 'Veliz Linares', 'que-hay-que-hacer-para-ser-catedratico-1.jpg', 'correo1@prueba.com', 'Esta es una semblanza de prueba la cual debería ocupar un espacio máximo de unas 1000 líneas, para eso me puse a escribir cualquier babosada que se me vino a la cabeza con tal de ocupar todo el espacio
que se pueda ya que no sé si siquiera van
jalar los enters con signo y solo así pero bueno vamos a ver qué ocurre', 'formacion1, formacion 2, formacion 3', 'activo', 20);

INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, id_periodo)
VALUES(6257, 'Álvaro Giovanni', 'Longo', 'Defecto.png', 'correo1@prueba.com', 'Esta es una semblanza de prueba la cual debería ocupar un espacio máximo de unas 1000 líneas, para eso me puse a escribir cualquier babosada que se me vino a la cabeza con tal de ocupar todo el espacio
que se pueda ya que no sé si siquiera van
jalar los enters con signo y solo así pero bueno vamos a ver qué ocurre', 'formacion1, formacion 2, formacion 3', 'activo', 20);

INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, id_periodo)
VALUES(247, 'Otto', 'Escobar Leiva', 'que-hay-que-hacer-para-ser-catedratico-1.jpg', 'correo1@prueba.com', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Proin id lorem sit amet lorem malesuada fermentum. Fusce sed nisi in quam tincidunt condimentum.Quisque ullamcorper, justo eu tempor convallis, lorem justo luctus purus, non commodo odio ligula vel libero. Nulla auctor felis id ex volutpat, ac fringilla nunc tempor. Aliquam eget sapien ac lectus aliquam ullamcorper.

Sed consequat, libero id consequat dapibus, ex urna dapibus velit, id ultricies metus tortor vel velit. Aenean et ante non turpis sodales vehicula. Vivamus nec mi ut erat laoreet accumsan. Vestibulum tincidunt dui velit, non tempor enim pellentesque ut.

Nam venenatis urna vel eros rutrum, sed tempus dui ultrices. Proin fermentum varius ligula, at fermentum lorem commodo ac. Integer id odio quis turpis bibendum vehicula. In hac habitasse platea dictumst. Vivamus sit amet urna a sem finibus luctus.', 'Doctor of Philosophy in Mechanical Engineering - Rice University,
Maestro en Ciencias en Ingeniería Mecánica - University of Washington,
Ingeniero Electronico - USAC', 'activo', 20);

INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, id_periodo)
VALUES(1521, 'Jose Anibal', 'Silva', 'Defecto.png', 'correo1@prueba.com', 'Esta es una semblanza de prueba la cual debería ocupar un espacio máximo de unas 1000 líneas, para eso me puse a escribir cualquier babosada que se me vino a la cabeza con tal de ocupar todo el espacio
que se pueda ya que no sé si siquiera van
jalar los enters con signo y solo así pero bueno vamos a ver qué ocurre', 'formacion1, formacion 2, formacion 3', 'activo', 20);

INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, id_periodo)
VALUES(230, 'Luis Fernando', 'Espino Barrios', 'que-hay-que-hacer-para-ser-catedratico-1.jpg', 'correo1@prueba.com', 'Esta es una semblanza de prueba la cual debería ocupar un espacio máximo de unas 1000 líneas, para eso me puse a escribir cualquier babosada que se me vino a la cabeza con tal de ocupar todo el espacio
que se pueda ya que no sé si siquiera van
jalar los enters con signo y solo así pero bueno vamos a ver qué ocurre', 'formacion1, formacion 2, formacion 3', 'activo', 20);

INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, id_periodo)
VALUES(252, 'Otto Amilcar', 'Rodriguez', 'Defecto.png', 'correo1@prueba.com', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer vitae risus nec nunc fermentum aliquam. Maecenas vitae elit eu urna pharetra iaculis. Quisque auctor, ligula vel efficitur tincidunt, sapien eros pharetra justo, a vulputate felis dui at mi. Sed auctor sagittis quam, at ultricies justo. Nunc feugiat, leo et euismod bibendum, turpis mauris varius velit, vel congue eros lectus vel elit.
Ut nec dui ac ligula lacinia imperdiet. Nam nec nunc eu justo efficitur mattis. Nullam a tellus sit amet libero laoreet venenatis.
Fusce aliquam velit vel quam tristique cursus. Suspendisse potenti. Sed eu nunc velit.', 'formacion1, formacion 2, formacion 3', 'activo', 20);

INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, id_periodo)
VALUES(246, 'Manuel', 'Castillo Reyna', 'que-hay-que-hacer-para-ser-catedratico-1.jpg', 'correo1@prueba.com', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer vitae risus nec nunc fermentum aliquam. Maecenas vitae elit eu urna pharetra iaculis. Quisque auctor, ligula vel efficitur tincidunt, sapien eros pharetra justo, a vulputate felis dui at mi. Sed auctor sagittis quam, at ultricies justo. Nunc feugiat, leo et euismod
bibendum, turpis mauris varius velit, vel congue eros lectus vel elit.
Ut nec dui ac ligula lacinia imperdiet. Nam nec nunc eu justo efficitur mattis. Nullam a tellus sit amet libero laoreet venenatis.
Fusce aliquam velit vel quam tristique cursus. Suspendisse potenti. Sed eu nunc velit.', 'formacion1, formacion 2, formacion 3', 'activo', 20);

INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, id_periodo)
VALUES(245, 'Mario Jose', 'Bautista', 'Defecto.png', 'correo1@prueba.com', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer vitae risus nec nunc fermentum aliquam. Maecenas vitae elit eu urna pharetra iaculis. Quisque auctor, ligula vel efficitur tincidunt, sapien eros pharetra justo, a vulputate felis dui at mi. Sed auctor sagittis quam, at ultricies justo. Nunc feugiat, leo et euismod bibendum, turpis mauris varius velit, vel congue eros lectus vel elit.
Ut nec dui ac ligula lacinia imperdiet. Nam nec nunc eu justo efficitur mattis. Nullam a tellus sit amet libero laoreet venenatis.
Fusce aliquam velit vel quam tristique cursus. Suspendisse potenti. Sed eu nunc velit.', 'formacion1, formacion 2, formacion 3', 'activo', 20);

delete from mdtt_professor_profile where id > 0;
update mdtt_professor_profile
set foto = 'que-hay-que-hacer-para-ser-catedratico-1.jpg'
where id >= 1;
commit;
CALL create_current_teacher_directory();

select * from mdtt_professor_profile;

INSERT INTO mdtt_conference (nombre_video, video, estado, descripcion)
VALUES ('Video 1', 'https://www.youtube.com/embed/bzceaxCKy8I', 'activo', 'Descripción del Video 1.');
INSERT INTO mdtt_conference (nombre_video, video, estado, descripcion)
VALUES ('Video 2', 'https://www.youtube.com/embed/NjlnnTwGd70', 'activo', 'Descripción del Video 2.');
INSERT INTO mdtt_conference (nombre_video, video, estado, descripcion)
VALUES ('Video 3', 'https://www.youtube.com/embed/qelwclMZqn0', 'activo', 'Descripción del Video 3.');
INSERT INTO mdtt_conference (nombre_video, video, estado, descripcion)
VALUES ('Video 4', 'https://www.youtube.com/embed/iPrGhQXPjbE', 'activo', 'Descripción del Video 4.');
INSERT INTO mdtt_conference (nombre_video, video, estado, descripcion)
VALUES ('Video 5', 'https://www.youtube.com/embed/_FlKmcEzMAI', 'activo', 'Descripción del Video 5.');
INSERT INTO mdtt_conference (nombre_video, video, estado, descripcion)
VALUES ('Video 6', 'https://www.youtube.com/embed/uQgFfIiVCc4', 'activo', 'Descripción del Video 6.');
INSERT INTO mdtt_conference (nombre_video, video, estado, descripcion)
VALUES ('Video 7', 'https://www.youtube.com/embed/810T-qdnw44', 'activo', 'Descripción del Video 7.');
INSERT INTO mdtt_conference (nombre_video, video, estado, descripcion)
VALUES ('Video 8', 'https://www.youtube.com/embed/O3MWZCDgM7s', 'activo', 'Descripción del Video 8.');

insert into mdtt_conference(id_proyecto, id_estudiante, nombre_video, reporte, video, estado, descripcion)
values(9,3330, 'video de prueba','PDF reporte de prueba', 'URL video', 'pendiente', 'este es el primer video de prueba por un estudiante');
commit;

INSERT INTO mdtt_tag(tag, estado)
VALUES('Ciberseguridad', 'activo');
INSERT INTO mdtt_tag(tag, estado)
VALUES('Kubernetes', 'activo');
INSERT INTO mdtt_tag(tag, estado)
VALUES('Docker', 'activo');
INSERT INTO mdtt_tag(tag, estado)
VALUES('Oracle', 'activo');
INSERT INTO mdtt_tag(tag, estado)
VALUES('Java Scritp', 'activo');
INSERT INTO mdtt_tag(tag, estado)
VALUES('CI/CD', 'activo');

SELECT * FROM conferencia;



-- ---------------------------------------------------------------------------------------------------------------------
--                 QUERYS DE BUSQUEDA 
-- ---------------------------------------------------------------------------------------------------------------------
-- ---------------------------------------------------------------------------------------------------------------------
--                 BUSQUEDA - filtros para catedraticos por curso
-- ---------------------------------------------------------------------------------------------------------------------
SELECT DISTINCT	
	TRIM(BOTH ' ' FROM 
        CASE 
            WHEN LOCATE('(', p.name) > 0 AND LOCATE(')', p.name) > 0
                THEN CONCAT(SUBSTRING(p.name, 1, LOCATE('(', p.name) - 1), SUBSTRING(p.name, LOCATE(')', p.name) + 1))
            ELSE p.name
        END
    ) AS name
FROM project p 
WHERE p.project_id NOT LIKE 'PV%'
GROUP BY name;

SELECT * FROM project;
-- ---------------------------------------------------------------------------------------------------------------------
--                 BUSQUEDA - busqueda de catedraticos, cursos por periodo de año
-- ---------------------------------------------------------------------------------------------------------------------
SELECT usr.id, usr.first_name, usr.last_name, usr.username, aug.id, aug.role, prj.id, prj.name, prj.area_level, py.id, py.yearp
FROM  auth_user usr
INNER JOIN auth_membership autm ON usr.id = autm.user_id
INNER JOIN auth_group aug ON aug.id = autm.group_id
INNER JOIN user_project usrpj ON usr.id = usrpj.assigned_user 
INNER JOIN project prj ON usrpj.project = prj.id
INNER JOIN period_year py ON usrpj.period = py.id
WHERE aug.id = 3 AND py.id = 21;

-- ---------------------------------------------------------------------------------------------------------------------
--                 BUSQUEDA - busqueda de cursos de los catedraticos para el directorio
-- ---------------------------------------------------------------------------------------------------------------------
SELECT prj.id, prj.name, py.id, py.yearp
FROM  auth_user usr
INNER JOIN auth_membership autm ON usr.id = autm.user_id
INNER JOIN auth_group aug ON aug.id = autm.group_id
INNER JOIN user_project usrpj ON usr.id = usrpj.assigned_user 
INNER JOIN project prj ON usrpj.project = prj.id
INNER JOIN period_year py ON usrpj.period = py.id
WHERE aug.id = 3 AND py.id = 19 AND usr.id = 245;

-- ---------------------------------------------------------------------------------------------------------------------
--                 BUSQUEDA - busqueda de catedraticos por curso para el directorio
-- ---------------------------------------------------------------------------------------------------------------------
SELECT usr.id, usr.first_name, usr.last_name, usr.username, aug.id, aug.role, prj.id, prj.name, prj.area_level, py.id, py.yearp
FROM  auth_user usr
INNER JOIN auth_membership autm ON usr.id = autm.user_id
INNER JOIN auth_group aug ON aug.id = autm.group_id
INNER JOIN user_project usrpj ON usr.id = usrpj.assigned_user 
INNER JOIN project prj ON usrpj.project = prj.id
INNER JOIN period_year py ON usrpj.period = py.id
WHERE aug.id = 3 AND py.id = 19 AND usr.id = 245;



-- ---------------------------------------------------------------------------------------------------------------------
--                 BUSQUEDA - filtros para videos por tags
-- ---------------------------------------------------------------------------------------------------------------------
SELECT DISTINCT t.tag
FROM tag t
WHERE t.estado = 'activo';

select * from foro_semestre;
select * from foro where id_estudiante = 3371;
select * from mdtt_conference;

select * from penalizacion;
select * from seccion_rubrica;
select * from rubrica;
SELECT * FROM perfil_catedratico;

-- ---------------------------------------------------------------------------------------------------------------------
--                 BUSQUEDA - foros para el estudiante
-- ---------------------------------------------------------------------------------------------------------------------
SELECT fs.id, fs.nombre_foro, fs.fecha_apertura, fs.fecha_corte, f.estado, f.nota
FROM mdtt_forum_semester fs
LEFT JOIN mdtt_forum f ON fs.id = f.id_foro_semestre AND f.id_estudiante = 3330
WHERE fs.id_periodo = 21;

-- ---------------------------------------------------------------------------------------------------------------------
--                 BUSQUEDA - muestra unicamente los periodos en los cuales hay rubricas
-- ---------------------------------------------------------------------------------------------------------------------
SELECT DISTINCT py.id, py.yearp, p.name
FROM period_year py
INNER JOIN period p on p.id = py.period
RIGHT JOIN mdtt_rubric rub on rub.id_periodo = py.id
ORDER BY py.id DESC;

select * from mdtt_forum_semester;
SELECT * FROM foro WHERE id_estudiante = 3330 AND id_proyecto = 9;

select * from project where area_level = 1;
SELECT * FROM auth_user WHERE LAST_NAME LIKE '%ordoñez carrillo%';
SELECT * FROM academic WHERE CARNET LIKE '201701187';
select * from auth_user WHERE USERNAME LIKE '201701187';
SELECT * FROM academic_course_assignation asing WHERE CARNET = 5605;
SELECT * FROM user_project WHERE ASSIGNED_USER = 3330;
SELECT * FROM user_project WHERE ASSIGNED_USER = 6257 ORDER BY period DESC;
SELECT * FROM user_project where assigned_user = 228  order by period desc;

SELECT * FROM auth_user WHERE LAST_NAME LIKE '%longo%';
select * FROM project WHERE project_id NOT LIKE 'PV%';
select * FROM project WHERE id = 89;

SELECT * FROM period_year WHERE id = 19;
SELECT * FROM period_year;

SELECT asi.id, asi.ASSIGNED_USER, pj.name
FROM user_project asi
INNER JOIN project pj ON asi.project = pj.id
WHERE asi.assigned_user = 5214;


SELECT *
FROM user_project asi
INNER JOIN project pj ON asi.project = pj.id
WHERE asi.assigned_user = 3330;

SELECT *
FROM user_project asi
INNER JOIN project pj ON asi.project = pj.id
WHERE pj.id = 9  AND asi.period = 21;

SELECT * FROM academic_course_assignation_log;
SELECT * FROM DSA_DOCUMENT_DELIVERED;

-- id auth_user->3330
-- project id -> 9 130

select * from period_year;
-- query para buscar periodos por usuario
SELECT py.id, py.yearp, p.name
FROM period_year py
INNER JOIN user_project uspj ON uspj.period = py.id
INNER JOIN period p on p.id = py.period
WHERE uspj.ASSIGNED_USER = 3330
ORDER BY py.id DESC;

-- query para buscar proyeto por periodos
SELECT *
FROM user_project
WHERE ASSIGNED_USER = 3330 AND period = 18; AND project = 9;

SELECT * FROM foro;

SELECT
            pro.id,
            pro.periodo,
            pro.anio,
            pro.fecha_inicio,
            pro.fecha_fin,
            pro.activo,
            per.id,
            per.name
        FROM cpfecys.rec_proceso AS pro
            INNER JOIN cpfecys.period AS per ON pro.periodo = per.id
        WHERE pro.activo = 'T';
        
        
SELECT * FROM academic WHERE CARNET = '201325533';
SELECT * FROM auth_user WHERE id = 947;
SELECT password FROM auth_user WHERE id = 3330;

SELECT *
FROM mdtt_rubric
WHERE tipo = 'foro' and id_periodo = 21 AND id != 11 and estado = 'inactivo'
ORDER BY fecha_creacion desc;



UPDATE academic
SET email = 'wichocarrillo91@gmail.com'
WHERE CARNET = '201325533';

commit;

SELECT id, id_proyecto, id_estudiante, id_dsi, nombre_foro, reporte, nota, estado, fecha_creacion, fecha_calificacion
FROM foro
WHERE estado = 'pendiente';

SELECT py.id, py.yearp, p.name
FROM period_year py
INNER JOIN period p on p.id = py.period
ORDER BY py.id;

select now();

select * from auth_user where id = 3330;
select * from project where id = 9;

select * from user_project where project = 9;

SELECT *
FROM rubrica
WHERE tipo LIKE 'conferencia' AND estado = 'activo'
ORDER BY fecha_creacion DESC;


SELECT py.id, py.yearp, p.name -- el id que necesito es el del period_year
        FROM period_year py
        INNER JOIN period p on p.id = py.period
        ORDER BY py.id DESC;

select * from area_level;

select * from auth_membership;-- detalle
select * from auth_group; 
select * from auth_user;
select * from user_project where period = 21; -- detalle
select * from project;
select * from period_year;
select * from mdtt_forum;
select * from mdtt_professor_profile;


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

CALL create_current_teacher_directory;

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
SELECT id FROM period_year ORDER BY id DESC;

SELECT user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, (SELECT id FROM period_year ORDER BY id DESC LIMIT 1)
FROM mdtt_professor_profile
WHERE user_id = 6257
ORDER BY id DESC LIMIT 1;
        
SELECT distinct usr.id, usr.first_name, usr.last_name, usr.username, usr.email, aug.id, aug.role, py.id, py.yearp
FROM  auth_user usr
INNER JOIN auth_membership autm ON usr.id = autm.user_id
INNER JOIN auth_group aug ON aug.id = autm.group_id
INNER JOIN user_project usrpj ON usr.id = usrpj.assigned_user 
INNER JOIN period_year py ON usrpj.period = py.id
WHERE aug.id = 3 AND py.id = 22;


SELECT id FROM period_year ORDER BY id DESC LIMIT 1;


SELECT user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, (SELECT (id - 1) FROM period_year ORDER BY id DESC LIMIT 1)
			FROM mdtt_professor_profile
			WHERE user_id = 6257
ORDER BY id DESC LIMIT 1;
            
select * from mdtt_professor_profile;

SELECT distinct usr.id, usr.first_name, usr.last_name, usr.email, py.id
		FROM  auth_user usr
		INNER JOIN auth_membership autm ON usr.id = autm.user_id
		INNER JOIN auth_group aug ON aug.id = autm.group_id
		INNER JOIN user_project usrpj ON usr.id = usrpj.assigned_user 
		INNER JOIN period_year py ON usrpj.period = py.id
		WHERE aug.id = 3 AND py.id = (SELECT (id - 1) FROM period_year ORDER BY id DESC LIMIT 1);
        
        

        
SELECT rs.seccion, rs.puntos, rs.estado
FROM mdtt_rubric_section rs
INNER JOIN (
SELECT id FROM mdtt_rubric WHERE tipo = 'foro' AND estado = 'activo' AND id_periodo = (SELECT (id - 1) FROM period_year ORDER BY id DESC LIMIT 1)
) rub ON rs.id_rubrica = rub.id;

SELECT rs.seccion, rs.puntos, rs.estado
FROM mdtt_rubric_section rs
INNER JOIN mdtt_rubric rub ON rs.id_rubrica = rub.id
WHERE  rub.tipo = 'foro' AND rub.estado = 'activo' AND rub.id_periodo = (SELECT (id - 1) FROM period_year ORDER BY id DESC LIMIT 1);

SELECT rs.seccion, rs.puntos, rs.estado
FROM mdtt_rubric_section rs
INNER JOIN mdtt_rubric rub ON rs.id_rubrica = rub.id
WHERE rub.tipo = 'conferencia' AND rub.estado = 'activo' AND rub.id_periodo = (SELECT (id - 1) FROM period_year ORDER BY id DESC LIMIT 1);

SELECT id FROM mdtt_rubric WHERE tipo = 'foro' AND estado = 'activo' AND id_periodo = (SELECT (id - 1) FROM period_year ORDER BY id DESC LIMIT 1);



-- -----------------------------------------------------------------------------------------------
--                Query para sacar a todos los auxiliares que no han entregado un foro
--       solo se deben de modificar el period
-- -----------------------------------------------------------------------------------------------
SELECT aus.id, aus.username, aus.first_name, aus.last_name,  pj.id ,pj.name, aug.role, usrp.period
FROM auth_membership aum 
INNER JOIN auth_user aus ON aum.user_id = aus.id
INNER JOIN auth_group aug ON aum.group_id = aug.id
INNER JOIN user_project usrp ON usrp.assigned_user = aus.id
INNER JOIN project pj ON usrp.project = pj.id
LEFT JOIN mdtt_forum mf ON aus.id = mf.id_estudiante AND mf.id_foro_semestre = 6
WHERE aug.role = 'Student' 
  AND usrp.period = 22 
  AND pj.area_level = 1 
  AND usrp.pro_bono = 'F' 
  AND mf.id_estudiante IS NULL;
  
  SELECT id, fecha_corte FROM mdtt_forum_semester WHERE estado = 'activo' AND id_periodo = 22;

-- SELECT (id - 1) FROM period_year ORDER BY id DESC LIMIT 1

DROP PROCEDURE IF EXISTS validate_date_forums;
DELIMITER $$
CREATE PROCEDURE validate_date_forums()
BEGIN
    DECLARE current_period_id, cur_forum_id INT;
    DECLARE cur_forum_fecha_corte DATETIME;
    DECLARE cur_students_id , cur_students_id_pj INT;
    DECLARE done1, done2 INT DEFAULT FALSE;

    DECLARE cursor_active_forums CURSOR FOR 
        SELECT id, fecha_corte FROM mdtt_forum_semester WHERE estado = 'activo' AND id_periodo = current_period_id;
	
	DECLARE cursor_students CURSOR FOR
		SELECT aus.id, pj.id
		FROM auth_membership aum 
		INNER JOIN auth_user aus ON aum.user_id = aus.id
		INNER JOIN auth_group aug ON aum.group_id = aug.id
		INNER JOIN user_project usrp ON usrp.assigned_user = aus.id
		INNER JOIN project pj ON usrp.project = pj.id
		LEFT JOIN mdtt_forum mf ON aus.id = mf.id_estudiante AND mf.id_foro_semestre = cur_forum_id
		WHERE aug.role = 'Student' 
		  AND usrp.period = current_period_id 
		  AND pj.area_level = 1 
		  AND usrp.pro_bono = 'F' 
		  AND mf.id_estudiante IS NULL;
	
    DECLARE CONTINUE HANDLER FOR NOT FOUND 
    BEGIN
        SET done1 = TRUE;
        SET done2 = TRUE;
    END;
	
    SET current_period_id = (SELECT id FROM period_year ORDER BY id DESC LIMIT 1);
	
    OPEN cursor_active_forums;
    active_forums_loop: LOOP
        FETCH  cursor_active_forums INTO cur_forum_id, cur_forum_fecha_corte;
        IF done1 THEN
            LEAVE active_forums_loop;
        END IF;
        
        IF cur_forum_fecha_corte IS NOT NULL AND cur_forum_fecha_corte < NOW() THEN
			UPDATE mdtt_forum_semester SET estado = 'inactivo' WHERE id = cur_forum_id;
			OPEN cursor_students;
			
			students_loop: LOOP
			FETCH cursor_students INTO cur_students_id, cur_students_id_pj;
			IF done2 THEN
				LEAVE students_loop;
			END IF;
			
            INSERT INTO mdtt_forum(id_foro_semestre, id_estudiante, id_proyecto, estado, nota, fecha_calificacion, observaciones)
            VALUES(cur_forum_id, cur_students_id, cur_students_id_pj, 'sin entrega', 0, NOW(), 'No entrego'); 
			
			END LOOP students_loop;
			CLOSE cursor_students;
			SET done2 = FALSE;
			END IF;
        
    END LOOP active_forums_loop;
    CLOSE cursor_active_forums;

END$$
DELIMITER ;

CALL validate_date_forums();
CALL validate_extention_date_forums();