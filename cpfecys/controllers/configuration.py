@auth.requires_membership('Super-Administrator')
def allowed_careers():
    grid = SQLFORM.grid(db.validate_career, csv=False, paginate=10,
                        create=True, searchable=True)

    return dict(grid=grid)
