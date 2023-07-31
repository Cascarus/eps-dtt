import cpfecys
from datetime import date
from decimal import Decimal


@auth.requires_login()
@auth.requires(auth.has_membership("Super-Administrator") or auth.has_membership("Evaluator360"))
def evaluation():
    query = db.evaluation
    cperiod = cpfecys.current_year_period()
    db.evaluation.period.default = cperiod.id
    db.evaluation.period.writable = False
    db.evaluation.period.readable = False
    grid = SQLFORM.smartgrid(query, csv=False)
    return dict(grid=grid)

# emarquez


@auth.requires_login()
@auth.requires_membership("Super-Administrator")
def evaluation_period():
    query = db.evaluation_period
    grid = SQLFORM.smartgrid(query, csv=False)
    return dict(grid=grid)


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator") or auth.has_membership("Evaluator360")
)
def template():
    query = db.evaluation_template
    grid = SQLFORM.smartgrid(query, csv=False)
    return dict(grid=grid)


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator") or auth.has_membership("Evaluator360")
)
def evaluation_type():
    query = db.evaluation_type
    grid = SQLFORM.smartgrid(query, csv=False)
    return dict(grid=grid)


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator") or auth.has_membership("evaluator360")
)
def repository_evaluation():
    query = db.repository_evaluation
    grid = SQLFORM.smartgrid(
        query, csv=False, create=False, editable=False, deletable=False
    )
    return dict(grid=grid)


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator") or auth.has_membership("Evaluator360")
)
def answer_type():
    query = db.answer_type
    grid = SQLFORM.smartgrid(query, csv=False)
    return dict(grid=grid)


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator") or auth.has_membership("Evaluator360")
)
def answer():
    query = db.answer
    grid = SQLFORM.grid(query, csv=False)
    return dict(grid=grid)


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator") or auth.has_membership("Evaluator360")
)
def evaluation_question():
    query = db.evaluation_question
    grid = SQLFORM.grid(query, csv=False)
    return dict(grid=grid)


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator") or auth.has_membership("Evaluator360")
)
def question_type():
    query = db.question_type
    grid = SQLFORM.grid(query, csv=False)
    return dict(grid=grid)


@auth.requires_login()
@auth.requires(
    auth.has_membership("Student")
    or auth.has_membership("Teacher")
    or auth.has_membership("Academic")
)
def evaluation_reply():
    cperiod = cpfecys.current_year_period()

    project = request.vars["project"]
    period = request.vars["period"]
    evaluation = request.vars["evaluation"]
    evaluated = request.vars["evaluated"]

    if (
        db(
            (db.auth_user.id == auth.user.id)
            & (db.user_project.project == project)
            & (
                (db.user_project.period <= period)
                & ((db.user_project.period.cast('integer') + db.user_project.periods) > period)
            )
        )
        .select()
        .first()
        is None
    ):
        academic_var = db.academic(db.academic.id_auth_user == auth.user.id)
        if (
            db(
                (db.academic_course_assignation.carnet == academic_var.id)
                & (db.academic_course_assignation.semester == period)
                & (db.academic_course_assignation.assignation == project)
            )
            .select()
            .first()
            is None
        ):
            session.flash = T("Not authorized")
            redirect(URL("default", "home"))

    evaluated = (
        db(
            (db.auth_user.id == evaluated)
            & (
                (db.user_project.period <= period)
                & ((db.user_project.period.cast('integer') + db.user_project.periods) > period)
            )
        )
        .select()
        .first()
    )
    if evaluated is None:
        session.flash = T("Not authorized")
        redirect(URL("default", "home"))

    var_evaluation = db((db.evaluation.id == evaluation)).select().first()

    if str(period) != str(cperiod.id):
        session.flash = T("Not authorized")
        redirect(URL("default", "home"))

    user_role = None
    if auth.has_membership("Student") or auth.has_membership("Teacher"):
        try:
            if (
                db(
                    (db.user_project.assigned_user == auth.user.id)
                    & (
                        (db.user_project.period <= period)
                        & ((db.user_project.period.cast('integer') + db.user_project.periods) > period)
                    )
                )
                .select()
                .first()
                is not None
            ):
                if auth.has_membership("Student"):
                    user_role = 2
                else:
                    user_role = 3
        except:
            None
    if auth.has_membership("Academic"):
        try:
            academic_var = db.academic(db.academic.id_auth_user == auth.user.id)
            if (
                db(
                    (db.academic_course_assignation.carnet == academic_var.id)
                    & (db.academic_course_assignation.semester == period)
                )
                .select()
                .first()
                is not None
            ):
                user_role = 5
        except:
            None

    if var_evaluation.repository_evaluation.user_type_evaluator != user_role:
        session.flash = T("Not authorized")
        redirect(URL("default", "home"))

    var_repository_evaluation = (
        db(db.repository_evaluation.id == var_evaluation.repository_evaluation)
        .select()
        .first()
    )
    question_category = db(
        db.question_repository.repository_evaluation
        == var_evaluation.repository_evaluation
    ).select(db.question_repository.question_type_name, distinct=True)

    evaluation_result = (
        db(
            (
                db.evaluation_result.repository_evaluation
                == var_evaluation.repository_evaluation
            )
            & (db.evaluation_result.evaluated == evaluated.auth_user.id)
            & (db.evaluation_result.period == period)
            & (db.evaluation_result.project == project)
        )
        .select()
        .first()
    )

    if (evaluation_result is not None) and (
        db(
            (db.evaluation_auth_user.evaluation_result == evaluation_result.id)
            & (db.evaluation_auth_user.evaluator == auth.user.id)
        )
        .select()
        .first()
        is not None
    ):
        session.flash = T("Not authorized")
        redirect(URL("default", "home"))

    if request.args(0) == "send":

        if evaluation_result is None:
            evaluation_result_id = db.evaluation_result.insert(
                repository_evaluation=var_evaluation.repository_evaluation,
                evaluated=evaluated.auth_user.id,
                period=period,
                project=project,
            )
        else:
            evaluation_result_id = evaluation_result.id

        evaluation_auth_user = (
            db(
                (db.evaluation_auth_user.evaluation_result == evaluation_result_id)
                & (db.evaluation_auth_user.evaluator == auth.user.id)
            )
            .select()
            .first()
        )
        if evaluation_auth_user is None:
            db.evaluation_auth_user.insert(
                evaluation_result=evaluation_result_id, evaluator=auth.user.id
            )

        question_query = db(
            (
                db.question_repository.repository_evaluation
                == var_evaluation.repository_evaluation
            )
        ).select()
        for question in question_query:
            answer_query = db(
                (db.repository_answer.question_repository == question.id)
            ).select()
            if len(answer_query) == 0:
                if (request.vars["group_" + str(question.id)] is not None) & (
                    request.vars["group_" + str(question.id)] != ""
                ):
                    db.evaluation_solve_text.insert(
                        evaluation_result=evaluation_result_id,
                        question_repository=question.id,
                        answer=request.vars["group_" + str(question.id)],
                    )
            else:
                for answer in answer_query:
                    if answer.exclusive_one_answer == True:
                        if request.vars["group_" + str(question.id)] is not None:
                            if str(request.vars["group_" + str(question.id)]) == str(
                                answer.id
                            ):
                                evaluation_solve_detail = (
                                    db(
                                        (
                                            db.evaluation_solve_detail.evaluation_result
                                            == evaluation_result_id
                                        )
                                        & (
                                            db.evaluation_solve_detail.question_repository
                                            == question.id
                                        )
                                        & (
                                            db.evaluation_solve_detail.repository_answer
                                            == answer.id
                                        )
                                    )
                                    .select()
                                    .first()
                                )
                                if evaluation_solve_detail is None:
                                    db.evaluation_solve_detail.insert(
                                        evaluation_result=evaluation_result_id,
                                        question_repository=question.id,
                                        repository_answer=answer.id,
                                        total_count=1,
                                    )
                                else:
                                    db(
                                        db.evaluation_solve_detail.id
                                        == evaluation_solve_detail.id
                                    ).update(
                                        total_count=(
                                            evaluation_solve_detail.total_count + 1
                                        )
                                    )

        session.flash = T("The evaluation has been sent")
        redirect(
            URL(
                "evaluation",
                "evaluation_list",
                vars=dict(period=period, project=project),
            )
        )

    return dict(
        var_evaluation=var_evaluation,
        var_repository_evaluation=var_repository_evaluation,
        question_category=question_category,
        evaluated=evaluated,
    )


@auth.requires_login()
@auth.requires(
    auth.has_membership("Student")
    or auth.has_membership("Teacher")
    or auth.has_membership("Academic")
)
def evaluation_list():
    project = request.vars["project"]
    period = request.vars["period"]

    # User information
    first_name = auth.user.first_name
    last_name = auth.user.last_name

    users_project = db(
        (db.user_project.project == project)
        & (
            (db.user_project.period <= period)
            & ((db.user_project.period.cast('integer') + db.user_project.periods) > period)
        )
    ).select()

    user_role = None
    user = None
    if auth.has_membership("Student") or auth.has_membership("Teacher"):
        try:
            user = (
                db(
                    (db.user_project.assigned_user == auth.user.id)
                    & (
                        (db.user_project.period <= period)
                        & ((db.user_project.period.cast('integer') + db.user_project.periods) > period)
                    )
                    & (db.user_project.project == project)
                )
                .select()
                .first()
            )
            if user is not None:
                if auth.has_membership("Student"):
                    user_role = 2
                else:
                    user_role = 3
        except:
            None
    if auth.has_membership("Academic"):
        try:
            if user is None:
                academic_var = db.academic(db.academic.id_auth_user == auth.user.id)
                if (
                    db(
                        (db.academic_course_assignation.carnet == academic_var.id)
                        & (db.academic_course_assignation.semester == period)
                        & (db.academic_course_assignation.assignation == project)
                    )
                    .select()
                    .first()
                    is not None
                ):
                    user_role = 5
                else:
                    session.flash = T("Not authorized")
                    redirect(URL("default", "home"))
        except:
            None

    # RGUARAN: se muestran resultados si fue evaluado y está asignado a ese proyecto
    evaluations = db(db.evaluation.period == period).select()

    is_evaluated = db(db.evaluation_result.evaluated == auth.user.id).select().first()
    is_tutor = (
        db(
            (db.user_project.assigned_user == auth.user.id)
            & (db.user_project.project == project)
        )
        .select()
        .first()
    )
    flag = False

    if is_evaluated != None and is_tutor != None:
        flag = True
    else:
        flag = False

    return dict(
        evaluations=evaluations,
        users_project=users_project,
        project=project,
        user_role=user_role,
        period=period,
        first_name=first_name,
        last_name=last_name,
        flag=flag,
    )


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator") or auth.has_membership("Evaluator360")
)
def question_template():
    question_type = request.vars["question_type"]
    answer_type = request.vars["answer_type"]
    template_id = request.vars["template_id"]
    question_var = request.vars["question"]
    answer_obligate = request.vars["answer_obligate"]

    if str(answer_obligate).lower() == "true":
        answer_obligate_var = True
    else:
        answer_obligate_var = False

    message_var = None
    if request.vars["operation"] == "add_question":
        if (question_var is None) or (question_var == ""):
            message_var = T("The question can not be empty.")
        else:

            var_answer_type = db((db.answer_type.id == answer_type)).select().first()
            var_answer = db((db.answer.answer_type == answer_type)).select()

            add_question_bol = True
            # if var_answer is not None:
            # if var_answer_type.exclusive_one_answer == True:
            # total_grade = 0
            # for answer in var_answer:
            #    total_grade = total_grade + answer.grade
            # pass

            # if total_grade != 100:
            #    message_var = T("No question was not added because the responses in this type of response does not sum up to 100. The sum of the responses are: ")+str(total_grade)
            #    add_question_bol = False

            if add_question_bol == True:
                var_question = (
                    db((db.evaluation_question.question == question_var))
                    .select()
                    .first()
                )
                if var_question is None:
                    db.evaluation_question.insert(question=question_var)
                    var_question = (
                        db((db.evaluation_question.question == question_var))
                        .select()
                        .first()
                    )

                var_question_temp = (
                    db(
                        (
                            db.evaluation_template_detail.evaluation_template
                            == template_id
                        )
                        & (
                            db.evaluation_template_detail.evaluation_question
                            == var_question.id
                        )
                        & (db.evaluation_template_detail.question_type == question_type)
                    )
                    .select()
                    .first()
                )
                if var_question_temp is None:
                    db.evaluation_template_detail.insert(
                        evaluation_template=template_id,
                        evaluation_question=var_question.id,
                        question_type=question_type,
                        obligatory=answer_obligate_var,
                        answer_type=answer_type,
                    )
                    message_var = T("Question has been added.")
                else:
                    message_var = "Error!!! " + T(
                        "The question has already been added."
                    )

    return dict(
        question_type=question_type,
        template_id=template_id,
        answer_type=answer_type,
        message_var=message_var,
    )


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator") or auth.has_membership("Evaluator360")
)
def evaluation_template_detail():
    template_id = request.vars["template_id"]
    if str(template_id) != str("None"):
        list_evaluation_template_detail = db(
            db.evaluation_template_detail.evaluation_template == template_id
        ).select(db.evaluation_template_detail.question_type, distinct=True)
        temp_list = []
        for temporal_var in list_evaluation_template_detail:
            if temporal_var is not None:
                temp_list.append(temporal_var.question_type)
        list_evaluation_template_detail = temp_list
    else:
        list_evaluation_template_detail = []
    return dict(
        list_evaluation_template_detail=list_evaluation_template_detail,
        template_id=template_id,
    )


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator") or auth.has_membership("Evaluator360")
)
def evaluation_template():
    template_id = request.vars["template_id"]
    op_select = request.vars["op_select"]
    ev_type = request.vars["ev_type"]

    if (ev_type is not None) and (template_id is not None):
        db(db.evaluation_template.id == template_id).update(evaluation_type=ev_type)

    select_form = FORM(INPUT(_name="ev_te_de_id", _type="text"))

    if select_form.accepts(request.vars, formname="remove_question"):
        db(db.evaluation_template_detail.id == select_form.vars.ev_te_de_id).delete()
        response.flash = T("Question removed")

    add_to_history = FORM(INPUT(_name="hitory_name", _type="text"))
    if add_to_history.accepts(request.vars, formname="add_to_history"):
        if add_to_history.vars.hitory_name == "":
            response.flash = "Error! " + T("You must enter a name")
        else:
            try:
                var_template = (
                    db(db.evaluation_template.id == template_id).select().first()
                )
                eval_h_id = db.repository_evaluation.insert(
                    name=add_to_history.vars.hitory_name,
                    template_name=var_template.name,
                    evaluation_type_name=var_template.evaluation_type.name,
                    user_type_evaluated=var_template.evaluation_type.user_type_evaluated,
                    user_type_evaluator=var_template.evaluation_type.user_type_evaluator,
                )

                var_template_detail = db(
                    db.evaluation_template_detail.evaluation_template == template_id
                ).select()
                for v_t_d in var_template_detail:
                    question_h_id = db.question_repository.insert(
                        question=v_t_d.evaluation_question.question,
                        question_type_name=v_t_d.question_type.name,
                        obligatory=v_t_d.obligatory,
                        repository_evaluation=eval_h_id,
                    )
                    var_answer_type = db(
                        db.answer.answer_type == v_t_d.answer_type
                    ).select()
                    for v_a_t in var_answer_type:
                        db.repository_answer.insert(
                            answer=v_a_t.answer,
                            answer_type_name=v_a_t.answer_type.name,
                            grade=v_a_t.grade,
                            exclusive_one_answer=v_a_t.answer_type.exclusive_one_answer,
                            question_repository=question_h_id,
                        )

                response.flash = T(
                    "Evaluation has been added to the repository evaluation"
                )
            except:
                response.flash = "Error! " + T(
                    "An assessment already exists in the repository of evaluations with that name"
                )

    add_question_form = FORM(INPUT(_name="question_id", _type="text"))

    if add_question_form.accepts(request.vars, formname="add_question"):
        question_id = request.vars["question_id"]
        if question_id is not None:
            var_question_temp = (
                db(
                    (db.evaluation_template_detail.evaluation_template == template_id)
                    & (db.evaluation_template_detail.evaluation_question == question_id)
                )
                .select()
                .first()
            )
            if var_question_temp is None:
                db.evaluation_template_detail.insert(
                    evaluation_template=template_id, evaluation_question=question_id
                )
                response.flash = T("Question has been added.")
            else:
                response.flash = T("The question has already been added.")

    evaluation_template_list = db(db.evaluation_template).select()
    db.evaluation_template.date_created.writable = False

    form = crud.create(
        db.evaluation_template,
        next=URL("evaluation", "evaluation_template", vars=dict(op_select=2)),
        message=T("Template has been created"),
    )
    if form.errors:
        op_select = "2"
        response.flash = T("Error")

    form_answer_create = crud.create(
        db.answer,
        next=URL("evaluation", "evaluation_template", vars=dict(op_select=3)),
        message=T("Answer has been created"),
    )
    if form_answer_create.errors:
        op_select = "3"
        response.flash = T("Error")

    form_answer_type_create = crud.create(
        db.answer_type,
        next=URL("evaluation", "evaluation_template", vars=dict(op_select=4)),
        message=T("Type answer has been created"),
    )
    if form_answer_type_create.errors:
        op_select = "4"
        response.flash = T("Error")

    form_question_type_create = crud.create(
        db.question_type,
        next=URL("evaluation", "evaluation_template", vars=dict(op_select=5)),
        message=T("Type question has been created"),
    )
    if form_question_type_create.errors:
        op_select = "5"
        response.flash = T("Error")

    form_evaluation_type_create = crud.create(
        db.evaluation_type,
        next=URL("evaluation", "evaluation_template", vars=dict(op_select=6)),
        message=T("Type evaluation has been created"),
    )
    if form_evaluation_type_create.errors:
        op_select = "6"
        response.flash = T("Error")

    return dict(
        evaluation_template_list=evaluation_template_list,
        form=form,
        form_answer_create=form_answer_create,
        form_answer_type_create=form_answer_type_create,
        form_question_type_create=form_question_type_create,
        form_evaluation_type_create=form_evaluation_type_create,
        op_select=op_select,
        template_id=template_id,
    )


@auth.requires_login()
@auth.requires(
    auth.has_membership("Student")
    or auth.has_membership("Teacher")
    or auth.has_membership("Super-Administrator")
    or auth.has_membership("Evaluator360")
    or auth.has_membership("Ecys-Administrator")
)
def results():

    first_name = ""
    last_name = ""
    user_id = None
    full_name = ""
    periods = []
    group = ""
    name_period = ""

    if auth.has_membership("Student") or auth.has_membership("Teacher"):
        if auth.has_membership("Ecys-Administrator"):
            first_name = ""
            last_name = ""
            user_id = None
        else:
            # User information
            first_name = auth.user.first_name
            last_name = auth.user.last_name
            user_id = auth.user.id
            full_name = first_name + " " + last_name

            # Obtain the current period of the system and all the register periods
            period = cpfecys.current_year_period()

            periods_temp = db(db.period_year).select(orderby=~db.period_year.id)

            for period_temp in periods_temp:
                try:
                    if (
                        db(
                            (db.user_project.assigned_user == auth.user.id)
                            & (db.user_project.period == db.period_year.id)
                            & (
                                (db.user_project.period <= period_temp.id)
                                & (
                                    (db.user_project.period.cast('integer') + db.user_project.periods)
                                    > period_temp.id
                                )
                            )
                        )
                        .select(db.user_project.ALL)
                        .first()
                        is not None
                    ):
                        periods.append(period_temp)
                except:
                    None

            # Check if the period has changed
            if request.vars["period"] is None:
                None
            else:
                if request.vars["period"] != "":
                    period = request.vars["period"]
                    period = db(db.period_year.id == period).select().first()
                else:
                    session.flash = T("Not valid Action.")
                    redirect(URL("default", "home"))
        pass
    pass

    if first_name == "" and user_id is None:
        if request.vars["period"] is None:
            None
        else:
            if request.vars["period"] != "":
                period = request.vars["period"]
                user_id = request.vars["user"]
                group = request.vars["group"]
                q_full_name = (
                    db(db.auth_user.id == user_id)
                    .select(db.auth_user.first_name, db.auth_user.last_name)
                    .first()
                )
                full_name = q_full_name.first_name + " " + q_full_name.last_name
                name_period = db(db.period_year.id == period).select().first()
            else:
                session.flash = T("Not valid Action.")
                redirect(URL("default", "home"))
    pass

    column_total = (
        (db.answer.grade * db.evaluation_solve_detail.total_count).sum()
        / (db.evaluation_solve_detail.total_count.sum())
    ).with_alias("total")
    evaluetors_column = (db.evaluation_solve_detail.total_count.sum()).with_alias(
        "evaluators"
    )
    rows = db(
        (db.evaluation_solve_detail.evaluation_result == db.evaluation_result.id)
        & (db.evaluation_solve_detail.repository_answer == db.repository_answer.id)
        & (db.evaluation_solve_detail.question_repository == db.question_repository.id)
        & (db.repository_answer.question_repository == db.question_repository.id)
        & (db.evaluation_result.repository_evaluation == db.repository_evaluation.id)
        & (db.repository_answer.answer == db.answer.answer)
        & (db.evaluation_result.evaluated == db.auth_user.id)
        & (db.auth_user.id == user_id)
        & (db.evaluation_result.period == period)
    ).select(
        db.question_repository.question,
        column_total,
        evaluetors_column,
        groupby=db.question_repository.id,
    )
    ##calcular el promedio de los resultados
    suma = Decimal(0)
    promedio = 0
    constant_cien = Decimal(100)
    graph_val = Decimal(0)
    res_graph = []
    evaluators = 0

    if rows.first() is not None:
        for row in rows:
            suma = row.total + suma
            graph_val = row.total / constant_cien
            res_graph.append("%.3f" % (graph_val))
            evaluators = row.evaluators
        pass

        avg = suma / len(rows)
        promedio = int(avg)
    pass

    grid_answer = db(db.answer).select(db.answer.grade, db.answer.answer)
    # grid_answer = SQLFORM.grid(query, fields = [db.answer.grade, db.answer.answer], csv=False,deletable=False,
    # editable=False, details=False, selectable=None, create=False, searchable=False,sortable=False,
    # links_in_grid=False, user_signature=False, showbuttontext=False, ignore_rw = True)

    min_average = 40
    max_average = 60

    return dict(
        periods=periods,
        period=period,
        periodo=period,
        fullname=full_name,
        rows=rows,
        promedio=promedio,
        grid_answer=grid_answer,
        res_graph=res_graph,
        min_average=min_average,
        max_average=max_average,
        group=group,
        nameperiod=name_period,
        evaluators=evaluators,
    )


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator")
    or auth.has_membership("Evaluator360")
    or auth.has_membership("Ecys-Administrator")
)
def results_search():
    if (
        auth.has_membership("Super-Administrator")
        or auth.has_membership("Evaluator360")
        or auth.has_membership("Ecys-Administrator")
    ):
        # User information
        first_name = auth.user.first_name
        last_name = auth.user.last_name
        fullname = first_name + " " + last_name

        # Obtain the current period of the system and all the register periods
        period = cpfecys.current_year_period()
        periods = db(db.period_year).select()

        group = (
            db(
                (db.auth_group.id == 2)
                | (db.auth_group.id == 3)
                | (db.auth_group.id == 6)
            )
            .select(db.auth_group.id)
            .first()
        )

        groups = db(
            (db.auth_group.id == 2) | (db.auth_group.id == 3) | (db.auth_group.id == 6)
        ).select()

        # Check if the period has changed
        if request.vars["period"] is None:
            None
        else:
            if request.vars["period"] != "":
                period = request.vars["period"]
                period = db(db.period_year.id == period).select().first()
            else:
                session.flash = T("Not valid Action.")
                redirect(URL("default", "home"))

        # check for type of rol selected
        if request.vars["group"] is None:
            None
        else:
            if request.vars["group"] != "":
                group = request.vars["group"]
                group = db(db.auth_group.id == group).select().first()
            else:
                session.flash = T("Not valid Action.")
                redirect(URL("default", "home"))

        column_total = (
            (db.answer.grade * db.evaluation_solve_detail.total_count).sum()
            / (db.evaluation_solve_detail.total_count.sum())
        ).with_alias("total")
        evaluators_column = (db.evaluation_solve_detail.total_count.sum()).with_alias(
            "evaluators"
        )
        rows = db(
            (db.auth_membership.user_id == db.auth_user.id)
            & (db.auth_membership.group_id == db.auth_group.id)
            & (db.evaluation_result.evaluated == db.auth_user.id)
            & (db.evaluation_solve_detail.evaluation_result == db.evaluation_result.id)
            & (db.evaluation_solve_detail.repository_answer == db.repository_answer.id)
            & (
                db.evaluation_solve_detail.question_repository
                == db.question_repository.id
            )
            & (db.repository_answer.question_repository == db.question_repository.id)
            & (
                db.evaluation_result.repository_evaluation
                == db.repository_evaluation.id
            )
            & (db.repository_answer.answer == db.answer.answer)
            & (db.repository_evaluation.user_type_evaluated == db.auth_group.id)
            & (db.auth_group.id == group)
            & (db.evaluation_result.period == period)
        ).select(
            db.question_repository.question,
            column_total,
            evaluators_column,
            groupby=db.question_repository.id,
        )

        suma = Decimal(0)
        promedio = 0
        contant_cien = Decimal(100)
        graph_val = Decimal(0)
        res_graph = []
        label_graph = []
        evaluators = 0

        if rows.first() is not None:
            for row in rows:
                suma = row.total + suma
                graph_val = row.total / contant_cien
                res_graph.append("%.3f" % (graph_val))
                label_graph.append(row.question_repository.question)
                evaluators = row.evaluators

            avg = suma / len(rows)
            promedio = int(avg)

        grid_answer = db(db.answer).select(db.answer.grade, db.answer.answer)

    else:
        session.flash = T("Not authorized")
        redirect(URL("default", "home"))

    min_average = 40
    max_average = 60

    return dict(
        periods=periods,
        period=period,
        periodo=period,
        fullname=fullname,
        rows=rows,
        promedio=promedio,
        grid_answer=grid_answer,
        res_graph=res_graph,
        min_average=min_average,
        max_average=max_average,
        group=group,
        groups=groups,
        grupo=group,
        evaluators=evaluators,
    )


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator")
    or auth.has_membership("Evaluator360")
    or auth.has_membership("Ecys-Administrator")
)
def search():
    if (
        auth.has_membership("Super-Administrator")
        or auth.has_membership("Evaluator360")
        or auth.has_membership("Ecys-Administrator")
    ):
        # Obtain the current period of the system and all the register periods
        period = cpfecys.current_year_period()
        periods = db(db.period_year).select()

        # 2=student; 3= teacher; 6=ecys-administrator
        group = (
            db(
                (db.auth_group.id == 2)
                | (db.auth_group.id == 3)
                | (db.auth_group.id == 6)
            )
            .select(db.auth_group.id)
            .first()
        )

        groups = db(
            (db.auth_group.id == 2) | (db.auth_group.id == 3) | (db.auth_group.id == 6)
        ).select()

        # Check if the period has changed
        if request.vars["period"] is None:
            None
        else:
            if request.vars["period"] != "":
                period = request.vars["period"]
                period = db(db.period_year.id == period).select().first()
            else:
                session.flash = T("Not valid Action.")
                redirect(URL("default", "home"))

        # check for type of rol selected
        if request.vars["group"] is None:
            None
        else:
            if request.vars["group"] != "":
                group = request.vars["group"]
                group = db(db.auth_group.id == group).select().first()
            else:
                session.flash = T("Not valid Action.")
                redirect(URL("default", "home"))

        rows = db(
            (db.auth_membership.user_id == db.auth_user.id)
            & (db.auth_membership.group_id == db.auth_group.id)
            & (db.evaluation_result.evaluated == db.auth_user.id)
            & (db.auth_group.id == group)
            & (db.evaluation_result.period == period)
        ).select(
            db.evaluation_result.period,
            db.auth_user.id,
            db.auth_group.id,
            db.auth_user.username,
            db.auth_user.username,
            db.auth_user.first_name,
            db.auth_user.last_name,
            groupby=db.auth_user.id,
        )

    else:
        session.flash = T("Not authorized")
        redirect(URL("default", "home"))

    return dict(
        periods=periods,
        period=period,
        periodo=period,
        rows=rows,
        group=group,
        groups=groups,
        grupo=group,
    )


@auth.requires_login()
@auth.requires(
    auth.has_membership("Super-Administrator")
    or auth.has_membership("Evaluator360")
    or auth.has_membership("Ecys-Administrator")
)
def graph():
    if (
        auth.has_membership("Super-Administrator")
        or auth.has_membership("Evaluator360")
        or auth.has_membership("Ecys-Administrator")
    ):
        # Obtain the current period of the system and all the register periods
        period = cpfecys.current_year_period()
        periods = db(db.period_year).select()

        # 2=student; 3= teacher; 6=ecys-administrator
        group = (
            db(
                (db.auth_group.id == 2)
                | (db.auth_group.id == 3)
                | (db.auth_group.id == 6)
            )
            .select(db.auth_group.id)
            .first()
        )

        groups = db(
            (db.auth_group.id == 2) | (db.auth_group.id == 3) | (db.auth_group.id == 6)
        ).select()

        # Check if the period has changed
        if request.vars["period"] is None:
            None
        else:
            if request.vars["period"] != "":
                period = request.vars["period"]
                period = db(db.period_year.id == period).select().first()
            else:
                session.flash = T("Not valid Action.")
                redirect(URL("default", "home"))

        # check for type of rol selected
        if request.vars["group"] is None:
            None
        else:
            if request.vars["group"] != "":
                group = request.vars["group"]
                group = db(db.auth_group.id == group).select().first()
            else:
                session.flash = T("Not valid Action.")
                redirect(URL("default", "home"))

        column_total = (
            (db.answer.grade * db.evaluation_solve_detail.total_count).sum()
            / (db.evaluation_solve_detail.total_count.sum())
        ).with_alias("total")
        rows = db(
            (db.auth_membership.user_id == db.auth_user.id)
            & (db.auth_membership.group_id == db.auth_group.id)
            & (db.evaluation_result.evaluated == db.auth_user.id)
            & (db.evaluation_solve_detail.evaluation_result == db.evaluation_result.id)
            & (db.evaluation_solve_detail.repository_answer == db.repository_answer.id)
            & (
                db.evaluation_solve_detail.question_repository
                == db.question_repository.id
            )
            & (db.repository_answer.question_repository == db.question_repository.id)
            & (
                db.evaluation_result.repository_evaluation
                == db.repository_evaluation.id
            )
            & (db.repository_answer.answer == db.answer.answer)
            & (db.repository_evaluation.user_type_evaluated == db.auth_group.id)
            & (db.auth_group.id == group)
            & (db.evaluation_result.period == period)
        ).select(
            db.question_repository.question,
            column_total,
            groupby=db.question_repository.id,
        )

        constant_cien = Decimal(100)
        graph_val = Decimal(0)
        res_graph = []
        label_graph = []

        for row in rows:
            graph_val = row.total / constant_cien
            res_graph.append("%.3f" % (graph_val))
            label_graph.append(row.question_repository.question)
        pass

        grid_answer = db(db.answer).select(db.answer.grade, db.answer.answer)

    else:
        session.flash = T("Not authorized")
        redirect(URL("default", "home"))

    return dict(
        periods=periods,
        period=period,
        periodo=period,
        grid_answer=grid_answer,
        res_graph=res_graph,
        labelGraph=label_graph,
        group=group,
        groups=groups,
        grupo=group,
    )
