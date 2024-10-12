TRUNCATE mdtt_parameters;
TRUNCATE mdtt_professor_profile;

insert into mdtt_parameters(mdtt_parameter_name, mdtt_parameter_value_number)
values('penalizacion por entrega tarde en %', 50.00);

insert into mdtt_parameters(mdtt_parameter_name, mdtt_parameter_value_number)
values('id del item para proceso ABC de conferencias', 30);

CALL create_current_teacher_directory();
CALL create_current_conference_header();