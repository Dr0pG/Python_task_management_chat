"""
 Validações - Diogo Venâncio & André Gonçalves

"""

import db


def validate_json(json, *keys):
    for key in keys:
        if key not in json:
            return False
    return True


def validate_access(session, project_id):
    # Valida o login
    if 'user_id' not in session:
        return 401
    database = db.DatabaseController('database.db')

    ownership = database.owner_of_project(session['user_id'], project_id)
    association = database.get_user_project_association(session['user_id'], project_id)
    if not ownership and not association:
        return 403

    return 200

