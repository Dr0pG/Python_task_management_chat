"""
 Flask REST application - Diogo Venâncio & André Gonçalves

"""

import sqlite3
import uuid

from flask import Flask, request, jsonify, make_response, session, flash

import db as database
from utilities import validate_json, validate_access

app = Flask(__name__, static_url_path='/static')

db = database.DatabaseController('database.db')


@app.route('/')
def index():
    """
    O index é mostrado ao cliente.
    O index é diferente com base no cliente, se está logado ou não.
    """
    # Verifica se existe login, se não retornar make_response(jsonify(), 440) # 440 Login Time-out
    if 'user_id' in session:
        print("logged in")
        flash('You were logged in')
        # Redireciona para a página inicial

    return app.send_static_file('index.html')


@app.route("/api/user/", methods=['GET', 'PUT'])
def access_user():
    """
    Obtem ou muda informações da conta.
    Verifica para dar log in.
    """
    if 'user_id' not in session:
        return make_response(jsonify(), 401)

    if request.method == 'GET':
        user = db.get_user(session['user_id'])
        return make_response(jsonify(user), 200)
    elif request.method == 'PUT':
        data = request.get_json()
        db.update_user(session['user_id'], data)
        return make_response(jsonify(), 200)


@app.route("/api/user/login/", methods=['POST'])
def login():
    """
    Regista-se na aplicação através do formulário.
    Se o login for válido, o cliente será redirecionado para a página inicial.
    """
    data = request.get_json()
    valid = validate_json(data, 'username', 'password')
    if not valid:
        return make_response(jsonify(), 400)
    user_id = db.login(data)
    if not user_id:
        return make_response(jsonify(), 403)
    else:
        session['user_id'] = user_id
        flash('You were logged in')
        return index()


@app.route("/api/user/logout/", methods=['GET'])
def logout():
    """
    Sai da aplicação e redireciona o cliente para a página inicial.
    """
    session.pop('user_id', None)
    return index()


@app.route("/api/user/register/", methods=['POST'])
def register():
    """
    Tenta se registar.
    """
    try:
        data = request.get_json()
        valid = validate_json(data, 'username', 'email', 'password')
        if not valid:
            return make_response(jsonify(), 400)
        user = db.add_user(data)
        return make_response(jsonify(user), 201)
    except sqlite3.Error as e:
        print(str(e))
        return make_response(jsonify(str(e)), 409)


@app.route("/api/projects/", methods=['GET', 'POST'])
def access_projects():
    """
    Retorna todos os projetos do cliente se o pedido for um GET.
    Tenta criar um projeto se a solicitação for um POST.
    Se a criação for bem sucedida, retorna o novo projeto.
    """
    if 'user_id' not in session:
        return make_response(jsonify(), 401)

    if request.method == 'GET':
        projects = db.get_projects_of_user(session['user_id'])
        return make_response(jsonify(projects), 200)
    elif request.method == 'POST':
        data = request.get_json()
        valid = validate_json(data, 'title')
        if not valid:
            return make_response(jsonify(), 400)
        try:
            data['owner'] = session['user_id']
            project = db.add_project(data)
            return make_response(jsonify(project), 201)
        except sqlite3.Error as e:
            print(e)
            return make_response(jsonify(str(e)), 409)


@app.route("/api/projects/<int:project_id>/tasks/", methods=['GET', 'POST', 'DELETE'])
def project_tasks(project_id):
    """
    O projeto tem de existir.
    O cliente deve pertencer ao projeto.
    Retorna todas as tarefas de um projeto se o pedido for um GET.
    Cria e retorna, se for bem sucedido, uma nova tarefa é criada, se o pedido for POST.
    Remove task se o pedido for um DELETE
    """
    # Verifica se o projeto existe.
    project = db.get_project(project_id)
    if not project:
        return make_response(jsonify(), 404)

    # Valida o login e a associação do cliente ao projeto
    code = validate_access(session, project_id)
    if code is not 200:
        return make_response(jsonify(), code)

    if request.method == 'GET':
        tasks = db.get_tasks_of_project(project_id)
        return make_response(jsonify(tasks), 200)
    elif request.method == 'POST':
        data = request.get_json()
        valid = validate_json(data, 'project_id', 'description')
        if not valid:
            return make_response(jsonify(), 400)
        try:
            task = db.add_task(data)
            return make_response(jsonify(task), 201)
        except sqlite3.Error as e:
            return make_response(jsonify(str(e), 409))
    elif request.method == 'DELETE':
        data = request.get_json()
        try:
            db.remove_task(data['task_id'])
            return make_response(jsonify(), 200)
        except sqlite3.Error as e:
            return make_response(jsonify(str(e)), 404)


@app.route("/api/projects/<int:project_id>/tasks/<int:task_id>/", methods=['GET', 'PUT', 'DELETE'])
def project_single_task(project_id, task_id):
    """
    O cliente tem que estar logado.
    A tarefa tem de existir.
    Retorna a informação da tarefa se o pedido for GET.
    Atualiza e retorna a tarefa atualizada se o pedido for um PUT.
    Remove a tarefa se o pedido for um DELETE.
    """
    # Valida o login e a associação do cliente ao projeto
    code = validate_access(session, project_id)
    if code is not 200:
        return make_response(jsonify(), code)

    # Verifica se a tarefa existe
    task = db.get_task(task_id)
    if not task:
        return make_response(jsonify(), 404)

    if request.method == 'GET':
        return make_response(jsonify(task), 200)
    elif request.method == 'PUT':
        data = request.get_json()
        valid = validate_json(data, 'project_order', 'description', 'status')
        if not valid:
            return make_response(jsonify(), 400)
        task = db.update_task(task_id, data)
        return make_response(jsonify(task), 200)
    elif request.method == 'DELETE':
        db.remove_task(task_id)
        return make_response(jsonify(), 200)


@app.route("/api/projects/<int:project_id>/", methods=['GET', 'PUT', 'DELETE'])
def single_project(project_id):
    """
    O cliente tem que estar logado.
    O projeto tem de existir.
    O cliente tem de pretencer ao projeto
    Retorna a informação do projeto se o pedido for GET.
    Atualiza e retorna o projeto atualizado se o pedido for um PUT.
    Remove o projeto se o pedido for um DELETE.
    """
    # Verifica se o projeto existe
    project = db.get_project(project_id)
    if not project:
        return make_response(jsonify(), 404)

    if 'user_id' not in session:
        return make_response(jsonify(), 401)

    # Valida o login e a associação do cliente ao projeto
    ownership = db.owner_of_project(session['user_id'], project_id)
    association = db.get_user_project_association(session['user_id'], project_id)
    if not ownership and not association:
        return make_response(jsonify(), 403)

    if request.method == 'GET':
        return make_response(jsonify(project), 200)
    elif request.method == 'PUT':
        data = request.get_json()
        valid = validate_json(data, 'title')
        if not valid:
            return make_response(jsonify(), 400)
        project = db.update_project(project_id, data)
        return make_response(jsonify(project), 200)
    elif request.method == 'DELETE':
        if not ownership:
            return make_response(jsonify(), 403)
        db.remove_project(project_id)
        return make_response(jsonify(), 200)


@app.route("/api/projects/<int:project_id>/collaborators/", methods=['GET', 'POST'])
def project_collaborators(project_id):
    """
    O cliente tem que estar logado.
    O projeto tem de existir.
    O cliente deve ser o criador do projeto.
    Retorna todos os colaboradores se o pedido for GET.
    Tenta adicionar um novo colaborador ao projeto se o pedido for um POST.
    """
    # Verifica se o projeto existe
    project = db.get_project(project_id)
    if not project:
        return make_response(jsonify(), 404)

    # Valida o login e a associação do cliente ao projeto
    code = validate_access(session, project_id)
    if code is not 200:
        return make_response(jsonify(), code)
    try:
        if request.method == 'GET':
            collabs = db.get_users_of_project(project_id)
            return make_response(jsonify(collabs), 200)
        elif request.method == 'POST':
            data = request.get_json()
            valid = validate_json(data, 'username')
            if not valid:
                return make_response(jsonify(), 400)

            user = db.get_user_from_username(data['username'])

            if not user:
                return make_response(jsonify(), 404)

            db.add_user_project(user['id'], project_id)
            return make_response(jsonify(), 201)
    except sqlite3.Error as e:
        print(str(e))
        return make_response(jsonify(str(e)), 409)


@app.route("/api/projects/<int:project_id>/collaborators/<int:collab_id>/", methods=['DELETE'])
def project_single_collaborator(project_id, collab_id):
    """
    Remove um colaborador do projeto.
    Somente o criador do projeto pode remover outros colaboradores.
    Um colaborador só pode sair do projeto
    """
    # Verifica se o projeto existe
    project = db.get_project(project_id)
    if not project:
        return make_response(jsonify(), 404)

    ownership = db.owner_of_project(session['user_id'], project_id)
    print(ownership)
    if not ownership and session['user_id'] != collab_id:
        return make_response(jsonify(), 403)

    if request.method == 'DELETE':
        try:
            if project['owner'] == collab_id:
                db.remove_project(project_id)
            else:
                db.remove_user_project(collab_id, project_id)
            return make_response(jsonify(), 200)
        except sqlite3.Error as e:
            return make_response(jsonify(str(e)), 409)


@app.route("/api/projects/<int:project_id>/chat/", methods=['GET', 'POST'])
def project_chat(project_id):
    """
    O cliente tem que estar logado.
    O projeto tem de existir.
    O cliente deve ser o criador ou estar associado ao projeto.
    Retorna todas as mensagens se o pedido for GET.
    Adiciona uma nova mensagem se a solicitação for um POST.
    """
    # Verifica se o projeto existe
    project = db.get_project(project_id)
    if not project:
        return make_response(jsonify(), 404)

    # Valida o login e a associação do cliente ao projeto
    code = validate_access(session, project_id)
    if code is not 200:
        return make_response(jsonify(), code)

    if request.method == 'GET':
        messages = db.get_messages_of_project(project_id)
        return make_response(jsonify(messages), 200)
    elif request.method == 'POST':
        data = request.get_json()

        valid = validate_json(data, 'content', 'project_id')
        if not valid:
            return make_response(jsonify(), 400)

        data['sender'] = session['user_id']
        user = db.get_user(session['user_id'])
        if not user:
            return make_response(jsonify(), 404)

        data['username'] = user['username']
        db.add_message(data)
        return make_response(jsonify(), 200)


if __name__ == '__main__':
    app.secret_key = uuid.uuid4().hex
    app.run(host='0.0.0.0', port=8000, debug=True)

