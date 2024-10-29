TRUNCATE mdtt_parameters;
TRUNCATE mdtt_professor_profile;

insert into mdtt_parameters(mdtt_parameter_name, mdtt_parameter_value_number, tipo)
values('penalizacion por entrega tarde en %', 50.00 , 1);

insert into mdtt_parameters(mdtt_parameter_name, mdtt_parameter_value_number, tipo)
values('id del item para proceso ABC de conferencias', 30, 2);

insert into mdtt_parameters(mdtt_parameter_name, mdtt_parameter_value_number, tipo)
values('tamaño reporte foros en (mb)', 3, 3);

insert into mdtt_parameters(mdtt_parameter_name, mdtt_parameter_value_number, tipo)
values('tamaño reporte conferencias en (mb)', 3, 4);

insert into mdtt_parameters(mdtt_parameter_name, mdtt_parameter_value_number, tipo)
values('tamaño portada conferencia en (mb)', 5, 4);

insert into mdtt_parameters(mdtt_parameter_name, mdtt_parameter_value_number, tipo)
values('tamaño de foto para catedraticos (mb)', 5, 5);

CALL create_current_teacher_directory();
CALL create_current_conference_header();