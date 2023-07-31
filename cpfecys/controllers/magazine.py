import cv2
import numpy as np

@auth.requires_login()
@auth.requires_membership('Magazine')
def management_magazine():
    def get_image_size(content):
        nparr = np.frombuffer(content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

        # Get the dimensions of the image
        height, width = img.shape[:2]
        return width, height

    def onupdate_magazine(form):
        if request.vars.image_file != b'':
            if not('jpeg' in request.vars.image_file.type or 'png' in request.vars.image_file.type):
                db.rollback()
                session.flash = 'Sólo se aceptan archivos con extensión png|jpg y con dimensiones (320x480)px.'
                redirect(URL('magazine', 'management_magazine'))


            file = request.vars.image_file.file
            file.seek(0)
            content = file.read()
            width, height = get_image_size(content)
            if width > 320 or height > 480:
                db.rollback()
                response.flash = 'Sólo se aceptan archivos con extensión png|jpg y con dimensiones (320x480)px.'
                redirect(URL('magazine', 'management_magazine'))

    def oncreate_magazine(form):

        if request.vars.image_file != b'':
            print(form.vars.id)
            if not('jpeg' in request.vars.image_file.type or 'png' in request.vars.image_file.type):            
                db(db.magazine.id == int(form.vars.id)).delete()
                session.flash = 'Sólo se aceptan archivos con extensión png|jpg y con dimensiones (320x480)px.'
                redirect(URL('magazine', 'management_magazine'))


            file = request.vars.image_file.file
            file.seek(0)
            content = file.read()
            width, height = get_image_size(content)
            if width > 320 or height > 480:
                db(db.magazine.id == int(form.vars.id)).delete()
                response.flash = 'Sólo se aceptan archivos con extensión png|jpg y con dimensiones (320x480)px.'
                redirect(URL('magazine', 'management_magazine'))



    query = db.magazine
    grid = SQLFORM.grid(query, csv=False, onupdate=onupdate_magazine, oncreate=oncreate_magazine)
    #print(grid, dir(grid))
    return dict(grid=grid)

#COVALLE
def view_edicion_revista():
    query = db.magazine_edition
    grid = SQLFORM.smartgrid(query, _class='web2py_grid', ui='web2py')
    return dict(grid=grid)

def public_edicion_revista():
    return dict()

