CREATE DATABASE cpfecys;
CREATE DATABASE cpfecys_scheduler;
USE cpfecys;
USE cpfecys_scheduler;
drop database cpfecys;
drop database cpfecys_scheduler;

select * from foro_semestre;
/*CREATE TABLE foro_semestre(
	id int auto_increment PRIMARY KEY,
    nombre_foro VARCHAR(500),
    fecha_corte DATETIME, -- fecha en la que se deja de recibir respuestas
    fecha_apertura DATETIME, -- fecha en la que inicia a recibir respuestas
    estado VARCHAR(30), -- activo, finalizado, eliminado
    id_periodo int
);

CREATE TABLE penalizacion(
	id int auto_increment PRIMARY KEY,
    nombre VARCHAR(100),
    descripcion VARCHAR(500),
	penalizacion DECIMAL(5,2),
    estado VARCHAR(30) -- a-> activo, i->inactivo, e->eliminado
);

CREATE TABLE rubrica(
	id INT AUTO_INCREMENT PRIMARY KEY,
    fecha_creacion DATE,
    estado VARCHAR(30), --  a-> activo, i->inactivo, e->eliminado
    tipo VARCHAR(30) -- f->foro, c->conferencias
);

CREATE TABLE seccion_rubrica(
	id INT AUTO_INCREMENT PRIMARY KEY,
    seccion VARCHAR(100),
    puntos DECIMAL(5,2),
    estado VARCHAR(30), --  a-> activo, i->inactivo, e->eliminado
    tipo VARCHAR(30) -- f->foro, c->conferencias, a->ambas
);

CREATE TABLE rubrica_detalle(
	id INT AUTO_INCREMENT PRIMARY KEY,
    id_rubrica INT,
    id_seccion INT,
    
    CONSTRAINT FK_RUBRICA_DETALLE_SECCION FOREIGN KEY(id_seccion) REFERENCES seccion_rubrica(id),
    CONSTRAINT FK_RUBRICA_DETALLE_RUBRICA FOREIGN KEY(id_rubrica) REFERENCES rubrica(id)
);

CREATE TABLE perfil_catedratico(
	id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    nombre VARCHAR(128),
    apellido VARCHAR(128),
    foto VARCHAR(512),
    correo VARCHAR(512),
    semblanza VARCHAR(1000),
    formacion VARCHAR(1000),
    estado VARCHAR(30),
    
    CONSTRAINT FK_PEFIL_CATEDRATICO_AUTH_USER FOREIGN KEY(user_id) REFERENCES auth_user(id)
);

CREATE TABLE perfil_clases_impartidas(
	id INT AUTO_INCREMENT PRIMARY KEY,
	id_perfil INT,
    id_proyecto INT,
    estado VARCHAR(30),
    CONSTRAINT FK_PF_CLASES_IMPARTIDAS_PERFIL FOREIGN KEY(id_perfil) REFERENCES perfil_catedratico(id),
    CONSTRAINT FK_PF_CLASES_IMPARTIDAS_PROYECTO FOREIGN KEY(id_proyecto) REFERENCES user_project(id)
);

CREATE TABLE foro(
	id INT AUTO_INCREMENT PRIMARY KEY,
    id_proyecto INT,
    id_estudiante INT,
    id_dsi INT,
    id_foro_semestre INT,
    nombre_foro VARCHAR(100),
    reporte VARCHAR(512),
    nota DECIMAL(5,2) DEFAULT 0,
    estado VARCHAR(30),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_calificacion datetime,
    observaciones VARCHAR(500),
    
    CONSTRAINT FK_FORO_PROYECTO FOREIGN KEY(id_proyecto) REFERENCES project(id),
    CONSTRAINT FK_FORO_ESTUDIANTE FOREIGN KEY(id_estudiante) REFERENCES auth_user(id),
    CONSTRAINT FK_FORO_DSI FOREIGN KEY(id_dsi) REFERENCES auth_user(id),
    CONSTRAINT FK_FORO_SEMESTRE FOREIGN KEY(id_foro_semestre) REFERENCES foro_semestre(id)
);

CREATE TABLE conferencia(
	id INT AUTO_INCREMENT PRIMARY KEY,
    id_proyecto INT,
    id_estudiante INT,
    id_dsi INT,
    nombre_video VARCHAR(512),
    reporte VARCHAR(512),
    video VARCHAR(512),
    nota DECIMAL(5,2) DEFAULT 0,
    estado VARCHAR(30),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_calificacion datetime,
    observaciones VARCHAR(500),
    descripcion VARCHAR(1000),
    
    CONSTRAINT FK_CONFERENCIA_PROYECTO FOREIGN KEY(id_proyecto) REFERENCES project(id),
    CONSTRAINT FK_CONFERENCIA_ESTUDIANTE FOREIGN KEY(id_estudiante) REFERENCES auth_user(id),
    CONSTRAINT FK_CONFERENCIA_DSI FOREIGN KEY(id_dsi) REFERENCES auth_user(id)
);

CREATE TABLE calificacion(
	id INT AUTO_INCREMENT PRIMARY KEY,
    id_conferencia INT,
    id_foro INT,
    id_seccion INT,
    id_penalizacion INT,
    tipo VARCHAR(30),
    nota DECIMAL(5,2),
    nota_completa BOOLEAN,
    
    CONSTRAINT FK_CALIFICACION_CONFERENCIA FOREIGN KEY(id_conferencia) REFERENCES conferencia(id),
    CONSTRAINT FK_CALIFICACION_FORO FOREIGN KEY(id_foro) REFERENCES foro(id),
    CONSTRAINT FK_CALIFICACION_PENALIZACION FOREIGN KEY(id_penalizacion) REFERENCES penalizacion(id)
);

CREATE TABLE tag(
	id INT AUTO_INCREMENT PRIMARY KEY,
    tag VARCHAR(100),
    estado VARCHAR(30)
);

CREATE TABLE conferencia_tag(
	id INT AUTO_INCREMENT PRIMARY KEY,
    id_tag INT,
    id_conferencia INT,
    
    CONSTRAINT FK_CONFERENCIA_TAG_TAG FOREIGN KEY(id_tag) REFERENCES tag(id),
    CONSTRAINT FK_CONFERENCIA_TAG_CONFERENCIA FOREIGN KEY(id_conferencia) REFERENCES conferencia(id)
);*/


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
	penalizacion DECIMAL(5,2),
    estado VARCHAR(30) -- a-> activo, i->inactivo, e->eliminado
);

CREATE TABLE mdtt_rubric( -- rubrica
	id INT AUTO_INCREMENT PRIMARY KEY,
    fecha_creacion DATE,
    estado VARCHAR(30), --  a-> activo, i->inactivo, e->eliminado
    tipo VARCHAR(30) -- f->foro, c->conferencias
);

CREATE TABLE mdtt_rubric_seccion( -- seccion_rubrica
	id INT AUTO_INCREMENT PRIMARY KEY,
    seccion VARCHAR(100),
    puntos DECIMAL(5,2),
    estado VARCHAR(30), --  a-> activo, i->inactivo, e->eliminado
    tipo VARCHAR(30) -- f->foro, c->conferencias, a->ambas
);

CREATE TABLE mdtt_rubric_detail( -- rubrica_detalle
	id INT AUTO_INCREMENT PRIMARY KEY,
    id_rubrica INT,
    id_seccion INT,
    
    CONSTRAINT FK_RUBRICA_DETALLE_SECCION FOREIGN KEY(id_seccion) REFERENCES mdtt_rubric_seccion(id),
    CONSTRAINT FK_RUBRICA_DETALLE_RUBRICA FOREIGN KEY(id_rubrica) REFERENCES mdtt_rubric(id)
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
    estado VARCHAR(30),
    period_id INT,
    
    CONSTRAINT FK_PEFIL_CATEDRATICO_AUTH_USER FOREIGN KEY(user_id) REFERENCES auth_user(id),
    CONSTRAINT FK_PROF_PROFILE_PERIOD_YEAR FOREIGN KEY(period_id) REFERENCES period_year(id)
);

CREATE TABLE mdtt_proffessor_period(
	id INT AUTO_INCREMENT PRIMARY KEY,
    professor_id INT,
    period_id INT,
    
    CONSTRAINT FK_PROFESOR_PROF_PROFESSOR_PERIOD FOREIGN KEY(period_id) REFERENCES period_year(id),
    CONSTRAINT KF_PROFESSOR_PROF_PROFESSOR_PROFILE FOREIGN KEY(professor_id) REFERENCES mdtt_professor_profile(id)
);

CREATE TABLE mdtt_pro_prof_class_taught( -- perfil_clases_impartidas
	id INT AUTO_INCREMENT PRIMARY KEY,
	id_perfil INT,
    id_proyecto INT,
    estado VARCHAR(30),
    CONSTRAINT FK_PF_CLASES_IMPARTIDAS_PERFIL FOREIGN KEY(id_perfil) REFERENCES mdtt_professor_profile(id),
    CONSTRAINT FK_PF_CLASES_IMPARTIDAS_PROYECTO FOREIGN KEY(id_proyecto) REFERENCES user_project(id)
);

CREATE TABLE mdtt_forum( -- foro
	id INT AUTO_INCREMENT PRIMARY KEY,
    id_proyecto INT,
    id_estudiante INT,
    id_dsi INT,
    id_foro_semestre INT,
    nombre_foro VARCHAR(100),
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
    nombre_video VARCHAR(512),
    reporte VARCHAR(512),
    video VARCHAR(512),
    nota DECIMAL(5,2) DEFAULT 0,
    estado VARCHAR(30),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_calificacion datetime,
    observaciones VARCHAR(500),
    descripcion VARCHAR(1000),
    
    CONSTRAINT FK_CONFERENCIA_PROYECTO FOREIGN KEY(id_proyecto) REFERENCES project(id),
    CONSTRAINT FK_CONFERENCIA_ESTUDIANTE FOREIGN KEY(id_estudiante) REFERENCES auth_user(id),
    CONSTRAINT FK_CONFERENCIA_DSI FOREIGN KEY(id_dsi) REFERENCES auth_user(id)
);

CREATE TABLE mdtt_grade( -- calificacion
	id INT AUTO_INCREMENT PRIMARY KEY,
    id_conferencia INT,
    id_foro INT,
    id_seccion INT,
    id_penalizacion INT,
    tipo VARCHAR(30),
    nota DECIMAL(5,2),
    nota_completa BOOLEAN,
    
    CONSTRAINT FK_CALIFICACION_CONFERENCIA FOREIGN KEY(id_conferencia) REFERENCES mdtt_conference(id),
    CONSTRAINT FK_CALIFICACION_FORO FOREIGN KEY(id_foro) REFERENCES mdtt_forum(id),
    CONSTRAINT FK_CALIFICACION_PENALIZACION FOREIGN KEY(id_penalizacion) REFERENCES mdtt_penalty(id)
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


DROP TABLE mdtt_pro_prof_class_taught;
DROP TABLE mdtt_professor_profile;
DROP TABLE mdtt_rubric_detail;
DROP TABLE mdtt_rubric_seccion;
DROP TABLE mdtt_grade;
DROP TABLE mdtt_conference_tag;
DROP TABLE mdtt_tag;
DROP TABLE mdtt_forum;
DROP TABLE mdtt_conference;
DROP TABLE mdtt_penalty;
DROP TABLE mdtt_rubric;
DROP TABLE mdtt_forum_semester;

DROP TABLE perfil_clases_impartidas;
DROP TABLE perfil_catedratico;
DROP TABLE rubrica_detalle;
DROP TABLE seccion_rubrica;
DROP TABLE calificacion;
DROP TABLE conferencia_tag;
DROP TABLE tag;
DROP TABLE conferencia;
DROP TABLE foro;
DROP TABLE penalizacion;
DROP TABLE rubrica;

-- ---------------------------------------------------------------------------------------------------------------------
--                    INSERTS
-- ---------------------------------------------------------------------------------------------------------------------
insert into mdtt_forum_semester(nombre_foro, fecha_corte, fecha_apertura,estado, id_periodo)
values('Foro 1', '2024-02-12 23:59:59', '2024-02-11', 'activo', 21);
insert into mdtt_forum_semester(nombre_foro, fecha_corte, fecha_apertura,estado, id_periodo)
values('Foro 2', '2024-02-14 23:59:59', '2024-02-13', 'activo', 21);
insert into mdtt_forum_semester(nombre_foro, fecha_corte, fecha_apertura,estado, id_periodo)
values('Foro 3', '2024-02-16 23:59:59', '2024-02-15', 'activo', 21);

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

insert into mdtt_conference(id_proyecto, id_estudiante, nombre_video, reporte, video, estado, descripcion)
values(9,3330, 'video de preuba','PDF reporte de prueba', 'URL video', 'pendiente', 'este es el primer video de prueba por un estudiante');

INSERT INTO mdtt_penalty(nombre, descripcion, penalizacion, estado)
values('penalizacion prueba 1', 'penalizacion que se utiliza para pruebas', 30.0, 'activo');
INSERT INTO mdtt_penalty(nombre, descripcion, penalizacion, estado)
values('penalizacion prueba 2', 'penalizacion que se utiliza para pruebas', 10.0, 'activo');
INSERT INTO mdtt_penalty(nombre, descripcion, penalizacion, estado)
values('penalizacion prueba 3', 'esta no se deberia ver xq esta inactiva', 50.0, 'inactivo');
INSERT INTO mdtt_penalty(nombre, descripcion, penalizacion, estado)
values('penalizacion prueba 4', 'esta no se deberia ver xq esta eliminada', 55.0, 'eliminado');

INSERT INTO mdtt_rubric_seccion(seccion, puntos, estado, tipo)
values('Seccion 1 de foro', 70.0, 'activo', 'foro');
INSERT INTO mdtt_rubric_seccion(seccion, puntos, estado, tipo)
values('Seccion 1 de conferencia', 70.0, 'activo', 'conferencia');
INSERT INTO mdtt_rubric_seccion(seccion, puntos, estado, tipo)
values('Seccion 2 de ambos', 30.0, 'activo', 'ambas');

INSERT INTO mdtt_rubric(fecha_creacion, estado, tipo)
VALUES(CURDATE(), 'activo', 'foro');
INSERT INTO mdtt_rubric(fecha_creacion, estado, tipo)
VALUES('2023-08-17', 'activo', 'foro');
INSERT INTO mdtt_rubric(fecha_creacion, estado, tipo)
VALUES(CURDATE(), 'activo', 'conferencia');

INSERT INTO mdtt_rubric_detail(id_rubrica, id_seccion)
VALUES(1,1);
INSERT INTO mdtt_rubric_detail(id_rubrica, id_seccion)
VALUES(1,3);

INSERT INTO mdtt_rubric_detail(id_rubrica, id_seccion)
VALUES(3,2);
INSERT INTO mdtt_rubric_detail(id_rubrica, id_seccion)
VALUES(3,3);

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

select * from auth_user where first_name like '%mario%' and last_name like '%bautista%';
-- 13858 6257

INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, period_id)
VALUES(228, 'Herman Igor', 'Veliz Linares', 'que-hay-que-hacer-para-ser-catedratico-1.jpg', 'correo1@prueba.com', 'Esta es una semblanza de prueba la cual debería ocupar un espacio máximo de unas 1000 líneas, para eso me puse a escribir cualquier babosada que se me vino a la cabeza con tal de ocupar todo el espacio
que se pueda ya que no sé si siquiera van
jalar los enters con signo y solo así pero bueno vamos a ver qué ocurre', 'formacion1, formacion 2, formacion 3', 'activo', 20);

INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, period_id)
VALUES(6257, 'Álvaro Giovanni', 'Longo', 'que-hay-que-hacer-para-ser-catedratico-1.jpg', 'correo1@prueba.com', 'Esta es una semblanza de prueba la cual debería ocupar un espacio máximo de unas 1000 líneas, para eso me puse a escribir cualquier babosada que se me vino a la cabeza con tal de ocupar todo el espacio
que se pueda ya que no sé si siquiera van
jalar los enters con signo y solo así pero bueno vamos a ver qué ocurre', 'formacion1, formacion 2, formacion 3', 'activo', 20);

INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, period_id)
VALUES(247, 'Otto', 'Escobar Leiva', 'que-hay-que-hacer-para-ser-catedratico-1.jpg', 'correo1@prueba.com', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Proin id lorem sit amet lorem malesuada fermentum. Fusce sed nisi in quam tincidunt condimentum.Quisque ullamcorper, justo eu tempor convallis, lorem justo luctus purus, non commodo odio ligula vel libero. Nulla auctor felis id ex volutpat, ac fringilla nunc tempor. Aliquam eget sapien ac lectus aliquam ullamcorper.

Sed consequat, libero id consequat dapibus, ex urna dapibus velit, id ultricies metus tortor vel velit. Aenean et ante non turpis sodales vehicula. Vivamus nec mi ut erat laoreet accumsan. Vestibulum tincidunt dui velit, non tempor enim pellentesque ut.

Nam venenatis urna vel eros rutrum, sed tempus dui ultrices. Proin fermentum varius ligula, at fermentum lorem commodo ac. Integer id odio quis turpis bibendum vehicula. In hac habitasse platea dictumst. Vivamus sit amet urna a sem finibus luctus.', 'Doctor of Philosophy in Mechanical Engineering - Rice University,
Maestro en Ciencias en Ingeniería Mecánica - University of Washington,
Ingeniero Electronico - USAC', 'activo', 20);

INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, period_id)
VALUES(1521, 'Jose Anibal', 'Silva', 'que-hay-que-hacer-para-ser-catedratico-1.jpg', 'correo1@prueba.com', 'Esta es una semblanza de prueba la cual debería ocupar un espacio máximo de unas 1000 líneas, para eso me puse a escribir cualquier babosada que se me vino a la cabeza con tal de ocupar todo el espacio
que se pueda ya que no sé si siquiera van
jalar los enters con signo y solo así pero bueno vamos a ver qué ocurre', 'formacion1, formacion 2, formacion 3', 'activo', 20);


INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, period_id)
VALUES(228, 'Herman Igor', 'Veliz Linares', 'que-hay-que-hacer-para-ser-catedratico-1.jpg', 'correo1@prueba.com', 'Esta es una semblanza de prueba la cual debería ocupar un espacio máximo de unas 1000 líneas, para eso me puse a escribir cualquier babosada que se me vino a la cabeza con tal de ocupar todo el espacio
que se pueda ya que no sé si siquiera van
jalar los enters con signo y solo así pero bueno vamos a ver qué ocurre', 'formacion1, formacion 2, formacion 3', 'activo', 21);

INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, period_id)
VALUES(6257, 'Álvaro Giovanni', 'Longo', 'que-hay-que-hacer-para-ser-catedratico-1.jpg', 'correo1@prueba.com', 'Esta es una semblanza de prueba la cual debería ocupar un espacio máximo de unas 1000 líneas, para eso me puse a escribir cualquier babosada que se me vino a la cabeza con tal de ocupar todo el espacio
que se pueda ya que no sé si siquiera van
jalar los enters con signo y solo así pero bueno vamos a ver qué ocurre', 'formacion1, formacion 2, formacion 3', 'activo', 21);

INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, period_id)
VALUES(247, 'Otto', 'Escobar Leiva', 'que-hay-que-hacer-para-ser-catedratico-1.jpg', 'correo1@prueba.com', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Proin id lorem sit amet lorem malesuada fermentum. Fusce sed nisi in quam tincidunt condimentum.Quisque ullamcorper, justo eu tempor convallis, lorem justo luctus purus, non commodo odio ligula vel libero. Nulla auctor felis id ex volutpat, ac fringilla nunc tempor. Aliquam eget sapien ac lectus aliquam ullamcorper.

Sed consequat, libero id consequat dapibus, ex urna dapibus velit, id ultricies metus tortor vel velit. Aenean et ante non turpis sodales vehicula. Vivamus nec mi ut erat laoreet accumsan. Vestibulum tincidunt dui velit, non tempor enim pellentesque ut.

Nam venenatis urna vel eros rutrum, sed tempus dui ultrices. Proin fermentum varius ligula, at fermentum lorem commodo ac. Integer id odio quis turpis bibendum vehicula. In hac habitasse platea dictumst. Vivamus sit amet urna a sem finibus luctus.', 'Doctor of Philosophy in Mechanical Engineering - Rice University,
Maestro en Ciencias en Ingeniería Mecánica - University of Washington,
Ingeniero Electronico - USAC', 'activo', 21);

INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, period_id)
VALUES(1521, 'Jose Anibal', 'Silva', 'que-hay-que-hacer-para-ser-catedratico-1.jpg', 'correo1@prueba.com', 'Esta es una semblanza de prueba la cual debería ocupar un espacio máximo de unas 1000 líneas, para eso me puse a escribir cualquier babosada que se me vino a la cabeza con tal de ocupar todo el espacio
que se pueda ya que no sé si siquiera van
jalar los enters con signo y solo así pero bueno vamos a ver qué ocurre', 'formacion1, formacion 2, formacion 3', 'activo', 21);

INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, period_id)
VALUES(230, 'Luis Fernando', 'Espino Barrios', 'que-hay-que-hacer-para-ser-catedratico-1.jpg', 'correo1@prueba.com', 'Esta es una semblanza de prueba la cual debería ocupar un espacio máximo de unas 1000 líneas, para eso me puse a escribir cualquier babosada que se me vino a la cabeza con tal de ocupar todo el espacio
que se pueda ya que no sé si siquiera van
jalar los enters con signo y solo así pero bueno vamos a ver qué ocurre', 'formacion1, formacion 2, formacion 3', 'activo', 21);

INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, period_id)
VALUES(252, 'Otto Amilcar', 'Rodriguez', 'que-hay-que-hacer-para-ser-catedratico-1.jpg', 'correo1@prueba.com', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer vitae risus nec nunc fermentum aliquam. Maecenas vitae elit eu urna pharetra iaculis. Quisque auctor, ligula vel efficitur tincidunt, sapien eros pharetra justo, a vulputate felis dui at mi. Sed auctor sagittis quam, at ultricies justo. Nunc feugiat, leo et euismod bibendum, turpis mauris varius velit, vel congue eros lectus vel elit.
Ut nec dui ac ligula lacinia imperdiet. Nam nec nunc eu justo efficitur mattis. Nullam a tellus sit amet libero laoreet venenatis.
Fusce aliquam velit vel quam tristique cursus. Suspendisse potenti. Sed eu nunc velit.', 'formacion1, formacion 2, formacion 3', 'activo', 21);

INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, period_id)
VALUES(246, 'Manuel', 'Castillo Reyna', 'que-hay-que-hacer-para-ser-catedratico-1.jpg', 'correo1@prueba.com', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer vitae risus nec nunc fermentum aliquam. Maecenas vitae elit eu urna pharetra iaculis. Quisque auctor, ligula vel efficitur tincidunt, sapien eros pharetra justo, a vulputate felis dui at mi. Sed auctor sagittis quam, at ultricies justo. Nunc feugiat, leo et euismod
bibendum, turpis mauris varius velit, vel congue eros lectus vel elit.
Ut nec dui ac ligula lacinia imperdiet. Nam nec nunc eu justo efficitur mattis. Nullam a tellus sit amet libero laoreet venenatis.
Fusce aliquam velit vel quam tristique cursus. Suspendisse potenti. Sed eu nunc velit.', 'formacion1, formacion 2, formacion 3', 'activo', 21);

INSERT INTO mdtt_professor_profile(user_id, nombre, apellido, foto, correo, semblanza, formacion, estado, period_id)
VALUES(245, 'Mario Jose', 'Bautista', 'que-hay-que-hacer-para-ser-catedratico-1.jpg', 'correo1@prueba.com', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer vitae risus nec nunc fermentum aliquam. Maecenas vitae elit eu urna pharetra iaculis. Quisque auctor, ligula vel efficitur tincidunt, sapien eros pharetra justo, a vulputate felis dui at mi. Sed auctor sagittis quam, at ultricies justo. Nunc feugiat, leo et euismod bibendum, turpis mauris varius velit, vel congue eros lectus vel elit.
Ut nec dui ac ligula lacinia imperdiet. Nam nec nunc eu justo efficitur mattis. Nullam a tellus sit amet libero laoreet venenatis.
Fusce aliquam velit vel quam tristique cursus. Suspendisse potenti. Sed eu nunc velit.', 'formacion1, formacion 2, formacion 3', 'activo', 21);

delete from mdtt_professor_profile where id > 0;
update mdtt_professor_profile
set foto = 'que-hay-que-hacer-para-ser-catedratico-1.jpg'
where id >= 1;
commit;

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
values(9,3330, 'video de preuba','PDF reporte de prueba', 'URL video', 'pendiente', 'este es el primer video de prueba por un estudiante');
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
select * from conferencia;
select * from penalizacion;
select * from seccion_rubrica;
select * from rubrica;
SELECT * FROM perfil_catedratico;
-- ---------------------------------------------------------------------------------------------------------------------
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
FROM USER_PROJECT asi
INNER JOIN PROJECT pj ON asi.PROJECT = pj.id
WHERE asi.ASSIGNED_USER = 3330;

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
WHERE uspj.ASSIGNED_USER = 3330;

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

SELECT
	`auth_user`.`id`,
    `auth_user`.`first_name`,
    `auth_user`.`last_name`,
    `auth_user`.`email`,
    `auth_user`.`username`,
    `auth_user`.`password`,
    `auth_user`.`registration_key`,
    `auth_user`.`reset_password_key`,
    `auth_user`.`registration_id`,
    `auth_user`.`phone`,
    `auth_user`.`home_address`,
    `auth_user`.`working`,
    `auth_user`.`company_name`,
    `auth_user`.`work_address`,
    `auth_user`.`work_phone`,
    `auth_user`.`uv_token`,
    `auth_user`.`data_updated`,
    `auth_user`.`load_alerted`,
    `auth_user`.`photo`,
    `auth_user`.`cui`,
    `user_project`.`id`,
    `user_project`.`assignation_status_comment`,
    `user_project`.`assignation_comment`,
    `user_project`.`assignation_ignored`,
    `user_project`.`assignation_status`,
    `user_project`.`assigned_user`,
    `user_project`.`project`,
    `user_project`.`period`,
    `user_project`.`pro_bono`,
    `user_project`.`hours`,
    `user_project`.`periods`,
    `project`.`id`, `project`.`project_id`,
    `project`.`name`, `project`.`area_level`,
    `project`.`description`, `project`.`physical_location`,
    `project`.`semester`,
    `auth_membership`.`id`,
    `auth_membership`.`user_id`,
    `auth_membership`.`group_id`,
    `auth_group`.`id`, `auth_group`.`role`,
    `auth_group`.`description`
FROM 
	`auth_user`, `user_project`, `project`, `auth_membership`, `auth_group`
WHERE 
	(
		(
			(
				(
					(
						(
							(`project`.`id` = 70) AND
                            (`user_project`.`project` = `project`.`id`)
						)
                        AND 
                        (
                        `auth_user`.`id` = `user_project`.`assigned_user`
                        )
					) 
                    AND
                    (
						(`user_project`.`period` <= 21) AND
                        (CAST(user_project.period AS INTEGER) + `user_project`.`periods`) > 21
					)
				)
			) AND (`auth_membership`.`user_id` = `auth_user`.`id`)
		) AND (`auth_membership`.`group_id` = `auth_group`.`id`)) AND (`auth_group`.`role` = 'Teacher'));

select * from auth_membership;-- detalle
select * from auth_group; 
select * from auth_user;
select * from user_project where period = 21; -- detalle
select * from project;
select * from period_year;

