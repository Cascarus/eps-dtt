insert into mdtt_parameters(mdtt_parameter_name, mdtt_parameter_value_number)
values('penalizacion por entrega tarde en %', 50.00);

insert into mdtt_parameters(mdtt_parameter_name, mdtt_parameter_value_string)
values('url_foros', '/static/forums/');

insert into mdtt_parameters(mdtt_parameter_name, mdtt_parameter_value_string)
values('url_conferencias', '/static/conferences/');

insert into mdtt_parameters(mdtt_parameter_name, mdtt_parameter_value_string)
values('url_portadas_conferencias', '/static/conferences/frontpages/');

insert into mdtt_parameters(mdtt_parameter_name, mdtt_parameter_value_string)
values('url_fotos_catedraticos', '/static/teacher_directory/');

CALL create_current_teacher_directory();