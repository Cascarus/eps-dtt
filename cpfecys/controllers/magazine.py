@auth.requires_login()
@auth.requires_membership('Magazine')
def management_magazine():
	query = db.magazine
	grid = SQLFORM.grid(query, _class='web2py_grid', ui='web2py')
	return dict(grid=grid)

#COVALLE
def view_edicion_revista():
    query = db.magazine_edition
    grid = SQLFORM.smartgrid(query, _class='web2py_grid', ui='web2py')
    return dict(grid=grid)

def public_edicion_revista():
    return dict()
