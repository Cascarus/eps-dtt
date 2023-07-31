def level_1_grades_management(period_name, yearp, project, academic):
    extra_condition = f"AND gl.academic like '{academic}'"
    if academic == f'%%':
        extra_condition = ""
    return (f"""
        SELECT
            SUM(CASE WHEN gl.operation_log = 'insert' THEN 1 ELSE 0 END) AS insert_count,
            SUM(CASE WHEN gl.operation_log = 'delete' THEN 1 ELSE 0 END) AS delete_count,
            SUM(CASE WHEN gl.operation_log = 'update' THEN 1 ELSE 0 END) AS update_count
        FROM
            grades_log AS gl
        WHERE
            gl.period = '{period_name}'
            AND gl.yearp = '{yearp}'
            AND gl.project = '{project}'
            {extra_condition}
    """)

def level_2_grades_management(period_name, yearp, project, date_start, date_end, academic):
    extra_condition = f"AND gl.academic like '{academic}'"
    if academic == f'%%':
        extra_condition = ""
    return (f"""
        SELECT
            SUM(CASE WHEN gl.operation_log = 'insert' THEN 1 ELSE 0 END) AS insert_count,
            SUM(CASE WHEN gl.operation_log = 'delete' THEN 1 ELSE 0 END) AS delete_count,
            SUM(CASE WHEN gl.operation_log = 'update' THEN 1 ELSE 0 END) AS update_count
        FROM
            grades_log AS gl
        WHERE
            gl.period = '{period_name}'
            AND gl.yearp = '{yearp}'
            AND gl.project = '{project}'
            AND gl.date_log >= '{date_start}'
            AND gl.date_log < '{date_end}'
            {extra_condition}
    """)

def level_3_grades_management(period_name, yearp, project, date_start, date_end, academic, rol):
    extra_condition = f"AND gl.academic like '{academic}'"
    if academic == f'%%':
        extra_condition = ""
    return (f"""
        SELECT
            SUM(CASE WHEN gl.operation_log = 'insert' THEN 1 ELSE 0 END) AS insert_count,
            SUM(CASE WHEN gl.operation_log = 'delete' THEN 1 ELSE 0 END) AS delete_count,
            SUM(CASE WHEN gl.operation_log = 'update' THEN 1 ELSE 0 END) AS update_count
        FROM
            grades_log AS gl
        WHERE
            gl.period = '{period_name}'
            AND gl.yearp = '{yearp}'
            AND gl.project = '{project}'
            AND gl.date_log >= '{date_start}'
            AND gl.date_log < '{date_end}'
            AND gl.roll = '{rol}'
            {extra_condition}
    """)

def level_4_grades_management(period_name, yearp, project, date_start, date_end, academic, rol, user_name):
    extra_condition = f"AND gl.academic like '{academic}'"
    if academic == f'%%':
        extra_condition = ""
    return (f"""
        SELECT
            SUM(CASE WHEN gl.operation_log = 'insert' THEN 1 ELSE 0 END) AS insert_count,
            SUM(CASE WHEN gl.operation_log = 'delete' THEN 1 ELSE 0 END) AS delete_count,
            SUM(CASE WHEN gl.operation_log = 'update' THEN 1 ELSE 0 END) AS update_count
        FROM
            grades_log AS gl
        WHERE
            gl.period = '{period_name}'
            AND gl.yearp = '{yearp}'
            AND gl.project = '{project}'
            AND gl.date_log >= '{date_start}'
            AND gl.date_log < '{date_end}'
            AND gl.roll = '{rol}'
            AND gl.user_name = '{user_name}'
            {extra_condition}
    """)

def level_1_laboratory_management(validation_type, period_name, yearp, project, academic):
    extra_condition = f"AND vll.academic like '{academic}'"
    if academic == f'%%':
        extra_condition = ""
    return (f"""
        SELECT
            SUM(CASE WHEN vll.operation_log = 'insert' THEN 1 ELSE 0 END) AS insert_count,
            SUM(CASE WHEN vll.operation_log = 'delete' THEN 1 ELSE 0 END) AS delete_count,
            SUM(CASE WHEN vll.operation_log = 'update' THEN 1 ELSE 0 END) AS update_count
        FROM
            validate_laboratory_log AS vll
        WHERE
            vll.period = '{period_name}'
            AND vll.yearp = '{yearp}'
            AND vll.project = '{project}'
            AND vll.validation_type = '{validation_type}'
            {extra_condition}
    """)

def level_2_laboratory_management(validation_type, period_name, yearp, project, date_start, date_end, academic):
    extra_condition = f"AND vll.academic like '{academic}'"
    if academic == f'%%':
        extra_condition = ""
    return (f"""
        SELECT
            SUM(CASE WHEN vll.operation_log = 'insert' THEN 1 ELSE 0 END) AS insert_count,
            SUM(CASE WHEN vll.operation_log = 'delete' THEN 1 ELSE 0 END) AS delete_count,
            SUM(CASE WHEN vll.operation_log = 'update' THEN 1 ELSE 0 END) AS update_count
        FROM
            validate_laboratory_log AS vll
        WHERE
            vll.period = '{period_name}'
            AND vll.yearp = '{yearp}'
            AND vll.project = '{project}'
            AND vll.date_log >= '{date_start}'
            AND vll.date_log < '{date_end}'
            AND vll.validation_type = '{validation_type}'
            {extra_condition}
    """)

def level_3_laboratory_management(validation_type, period_name, yearp, project, date_start, date_end, academic, rol):
    extra_condition = f"AND vll.academic like '{academic}'"
    if academic == f'%%':
        extra_condition = ""
    return (f"""
        SELECT
            SUM(CASE WHEN vll.operation_log = 'insert' THEN 1 ELSE 0 END) AS insert_count,
            SUM(CASE WHEN vll.operation_log = 'delete' THEN 1 ELSE 0 END) AS delete_count,
            SUM(CASE WHEN vll.operation_log = 'update' THEN 1 ELSE 0 END) AS update_count
        FROM
            validate_laboratory_log AS vll
        WHERE
            vll.period = '{period_name}'
            AND vll.yearp = '{yearp}'
            AND vll.project = '{project}'
            AND vll.date_log >= '{date_start}'
            AND vll.date_log < '{date_end}'
            AND vll.roll = '{rol}'
            AND vll.validation_type = '{validation_type}'
            {extra_condition}
    """)

def level_4_laboratory_management(validation_type, period_name, yearp, project, date_start, date_end, academic, rol, user_name):
    extra_condition = f"AND vll.academic like '{academic}'"
    if academic == f'%%':
        extra_condition = ""
    return (f"""
        SELECT
            SUM(CASE WHEN vll.operation_log = 'insert' THEN 1 ELSE 0 END) AS insert_count,
            SUM(CASE WHEN vll.operation_log = 'delete' THEN 1 ELSE 0 END) AS delete_count,
            SUM(CASE WHEN vll.operation_log = 'update' THEN 1 ELSE 0 END) AS update_count
        FROM
            validate_laboratory_log AS vll
        WHERE
            vll.period = '{period_name}'
            AND vll.yearp = '{yearp}'
            AND vll.project = '{project}'
            AND vll.date_log >= '{date_start}'
            AND vll.date_log < '{date_end}'
            AND vll.roll = '{rol}'
            AND vll.user_name = '{user_name}'
            AND vll.validation_type = '{validation_type}'
            {extra_condition}
    """)