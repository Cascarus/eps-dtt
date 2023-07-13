CREATE DATABASE cpfecys;
USE cpfecys;

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
    nombre_foro VARCHAR(100),
    reporte VARCHAR(512),
    nota DECIMAL(5,2) DEFAULT 0,
    estado VARCHAR(30),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_calificacion datetime,
    observaciones VARCHAR(500),
    
    CONSTRAINT FK_FORO_PROYECTO FOREIGN KEY(id_proyecto) REFERENCES project(id),
    CONSTRAINT FK_FORO_ESTUDIANTE FOREIGN KEY(id_estudiante) REFERENCES auth_user(id),
    CONSTRAINT FK_FORO_DSI FOREIGN KEY(id_dsi) REFERENCES auth_user(id)
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
);

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
insert into foro(id_proyecto, id_estudiante, nombre_foro, reporte, estado)
values(9,3330, 'reporte prueba','PDF reporte de prueba', 'pendiente');
insert into foro(id_proyecto, id_estudiante, nombre_foro, reporte, estado)
values(9,3330, 'reporte prueba 2','PDF reporte de prueba 2', 'pendiente');
insert into foro(id_proyecto, id_estudiante, nombre_foro, reporte, estado)
values(9,3330, 'reporte prueba 3','PDF reporte de prueba 3', 'pendiente');
insert into foro(id_proyecto, id_estudiante, nombre_foro, reporte, estado)
values(9,3330, 'reporte prueba 4','PDF reporte de prueba 4', 'pendiente');
insert into foro(id_proyecto, id_estudiante, nombre_foro, reporte, estado)
values(9,3330, 'reporte prueba 5','PDF reporte de prueba 5', 'pendiente');
insert into foro(id_proyecto, id_estudiante, nombre_foro, reporte, estado)
values(9,3330, 'reporte prueba 6','PDF reporte de prueba 6', 'pendiente');
insert into foro(id_proyecto, id_estudiante, nombre_foro, reporte, estado)
values(9,3330, 'reporte prueba 7','PDF reporte de prueba 7', 'pendiente');
insert into foro(id_proyecto, id_estudiante, nombre_foro, reporte, estado)
values(9,3330, 'reporte prueba 8','PDF reporte de prueba 8', 'pendiente');
insert into foro(id_proyecto, id_estudiante, nombre_foro, reporte, estado)
values(9,3330, 'reporte prueba 9','PDF reporte de prueba 9', 'pendiente');
insert into foro(id_proyecto, id_estudiante, nombre_foro, reporte, estado)
values(9,3330, 'reporte prueba 10','PDF reporte de prueba 10', 'pendiente');
insert into foro(id_proyecto, id_estudiante, nombre_foro, reporte, estado)
values(9,3330, 'reporte prueba 11','PDF reporte de prueba 11', 'pendiente');
insert into foro(id_proyecto, id_estudiante, nombre_foro, reporte, estado)
values(9,3330, 'reporte prueba 12','PDF reporte de prueba 12', 'pendiente');
insert into foro(id_proyecto, id_estudiante, nombre_foro, reporte, estado)
values(9,3330, 'reporte prueba 13','PDF reporte de prueba 13', 'pendiente');

insert into conferencia(id_proyecto, id_estudiante, nombre_video, reporte, video, estado, descripcion)
values(9,3330, 'video de preuba','PDF reporte de prueba', 'URL video', 'pendiente', 'este es el primer video de prueba por un estudiante');

commit;
select * from foro;
select * from conferencia;

-- ---------------------------------------------------------------------------------------------------------------------
SELECT * FROM foro WHERE id_estudiante = 3330 AND id_proyecto = 9;

select * from project;
SELECT * FROM auth_user WHERE LAST_NAME LIKE '%ordoñez carrillo%';
SELECT * FROM academic WHERE CARNET LIKE '201701187';
select * from auth_user WHERE USERNAME LIKE '201701187';
SELECT * FROM academic_course_assignation asing WHERE CARNET = 5605;
SELECT * FROM user_project WHERE ASSIGNED_USER = 3330;
SELECT * FROM user_project WHERE ASSIGNED_USER = 3917;

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

UPDATE auth_user
SET password = (SELECT password FROM auth_user WHERE id = 3330)
WHERE id = 947;

UPDATE academic
SET email = 'wichocarrillo91@gmail.com'
WHERE CARNET = '201325533';

commit;

SELECT id, id_proyecto, id_estudiante, id_dsi, nombre_foro, reporte, nota, estado, fecha_creacion, fecha_calificacion
FROM foro
WHERE estado = 'pendiente';

SELECT py.id, py.yearp, p.name
FROM period_year py
INNER JOIN user_project uspj ON uspj.period = py.id
INNER JOIN period p on p.id = py.period
GROUP BY py.id, py.yearp, p.name