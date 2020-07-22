"""
 Implementação de uma base de dados - Diogo Venâncio & André Gonçalves

"""

import hashlib
import os
import sqlite3
import uuid
from datetime import datetime


def hash_password(password):
    salt = uuid.uuid4().hex
    return hashlib.sha3_512(salt.encode() + password.encode()).hexdigest() + ':' + salt


def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha3_512(salt.encode() + user_password.encode()).hexdigest()


class DatabaseController:
    def __init__(self, db_name):
        if not os.path.isfile(db_name):
            self.conn = sqlite3.connect(db_name, check_same_thread=False)
            self.conn.row_factory = self.dict_factory
            self.recreate_db()
        else:
            self.conn = sqlite3.connect(db_name, check_same_thread=False)
            self.conn.row_factory = self.dict_factory

    def recreate_db(self):
        """
        Recria a base de dados
        """
        c = self.conn.cursor()
        # DROPS
        c.execute("DROP TABLE IF EXISTS messages")
        c.execute("DROP TABLE IF EXISTS users_projects")
        c.execute("DROP TABLE IF EXISTS tasks")
        c.execute("DROP TABLE IF EXISTS users")
        c.execute("DROP TABLE IF EXISTS projects")
        # DROPS - FIM

        # TABLES
        c.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL,
                    password TEXT NOT NULL 
                )
            """)
        c.execute("""
                CREATE TABLE projects(
                    id INTEGER PRIMARY KEY,
                    owner INTEGER,
                    title TEXT NOT NULL,
                    creation_date TIMESTAMP NOT NULL,
                    last_update TIMESTAMP NOT NULL,
                    FOREIGN KEY(owner) REFERENCES users(id)
                )    
            """)
        c.execute("""
                CREATE TABLE tasks(
                    id INTEGER PRIMARY KEY,
                    project_id INTEGER,
                    project_order INTEGER,
                    description TEXT NOT NULL,
                    status BIT NOT NULL,
                    creation_date TIMESTAMP NOT NULL,
                    due_date TIMESTAMP,
                    FOREIGN KEY(project_id) REFERENCES projects(id)
                )
            """)
        c.execute("""
                CREATE TABLE messages(
                    id INTEGER PRIMARY KEY,
                    project_id INTEGER,
                    sender INTEGER,
                    username TEXT,
                    content TEXT NOT NULL,
                    creation_date TIMESTAMP NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(id),
                    FOREIGN KEY(sender) REFERENCES users(id)
                )
            """)
        c.execute("""
                CREATE TABLE users_projects(
                    user_id INTEGER,
                    project_id INTEGER,
                    PRIMARY KEY(user_id, project_id),
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(project_id) REFERENCES projects(id)
                )
            """)
        # TABLES - FIM

        # INSERTS
        c.execute("""INSERT INTO users VALUES (null, 'Diogo', 'diogo@gmail.com', ?), 
        (null, 'Andre', 'andre@gmail.com', ?)""",
                  (hash_password('123'), hash_password('123'),))
        c.execute("""INSERT INTO projects VALUES (null, ?, 'Project1', ?, ?),
                  (null, ?, 'Project2', ?, ?)""",
                  (1, datetime.now(), datetime.now(), 2, datetime.now(), datetime.now(),))
        c.execute("""INSERT INTO users_projects VALUES (1,1), (2,2)""")
        # INSERTS - FIM

        self.conn.commit()

    def dict_factory(self, cursor, row):
        """
        Converte a linha da tabela num dicionário.
        """
        res = {}
        for idx, col in enumerate(cursor.description):
            res[col[0]] = row[idx]
        return res

    # GETS
    def get_users(self):
        """
        Retorna todos os clientes.
        """
        res = self.conn.cursor().execute('SELECT id,email,username FROM users')
        return res.fetchall()

    def get_user(self, user_id):
        """
        Retorna um único cliente através do seu id.
        """
        res = self.conn.cursor().execute('SELECT id,email,username FROM users WHERE id=?', (user_id,))
        return res.fetchone()

    def get_user_from_username(self, username):
        """
        Retorna um único cliente através do seu username.
        """
        res = self.conn.cursor().execute('SELECT id,email,username FROM users WHERE username=?', (username,))
        return res.fetchone()

    def get_projects(self):
        """
        Retorna todos os projetos.
        """
        res = self.conn.cursor().execute("SELECT * FROM projects")
        return res.fetchall()

    def get_project(self, project_id):
        """
        Retorna um projeto segundo o seu id.
        """
        res = self.conn.cursor().execute("SELECT * FROM projects where id=?", (project_id,))
        return res.fetchone()

    def get_users_of_project(self, project_id):
        """
        Retorna todos os clientes associados ao projeto.
        """
        res = self.conn.cursor().execute("""SELECT id, username FROM users u JOIN users_projects up 
            ON u.id = up.user_id 
            WHERE up.project_id=?""", (project_id,))
        return res.fetchall()

    def get_projects_of_user(self, user_id):
        """
        Retorna todos os projetos associados a um cliente.
        """
        res = self.conn.cursor().execute("""SELECT * FROM projects p JOIN users_projects up 
        ON p.id = up.project_id 
        WHERE owner=? OR up.user_id=?
        GROUP BY p.id
        ORDER BY last_update DESC""", (user_id, user_id,))
        return res.fetchall()

    def get_user_project_association(self, user_id, project_id):
        """
        Retorna uma associação do projeto a um cliente.
        """
        res = self.conn.cursor().execute("SELECT * FROM users_projects WHERE user_id=? AND project_id=?",
                                         (user_id, project_id,))
        return res.fetchone()

    def get_tasks(self):
        """
        Retorna todas as tarefas.
        """
        res = self.conn.cursor().execute("SELECT * FROM tasks")
        return res.fetchall()

    def get_task(self, task_id):
        """
        Retorna uma tarefa segundo o seu id.
        """
        res = self.conn.cursor().execute("SELECT * FROM tasks WHERE id=?", (task_id,))
        return res.fetchone()

    def get_tasks_of_project(self, project_id):
        """
        Retorna todas as tarefas associadas a um projeto.
        """
        res = self.conn.cursor().execute("SELECT * FROM tasks WHERE project_id=? ORDER BY project_order", (project_id,))
        return res.fetchall()

    def get_messages(self):
        """
        Retorna todas as mensagens.
        """
        res = self.conn.cursor().execute("SELECT * FROM messages")
        return res.fetchall()

    def get_messages_of_project(self, project_id):
        """
        Retorna todas as mensagens dum especifico projeto.
        """
        res = self.conn.cursor().execute("SELECT * FROM messages WHERE project_id=?", (project_id,))
        return res.fetchall()

    # GETS - FIM

    # ADDS
    def add_user(self, user):
        """
        Adiciona um novo cliente.
        """
        c = self.conn.cursor()
        cursor = c.execute("INSERT INTO users VALUES (null, ?, ?, ?)",
                           (user['username'], user['email'], hash_password(user['password']),))
        self.conn.commit()
        return self.get_user(cursor.lastrowid)

    def add_project(self, project):
        """
        Adiciona um novo projeto. O json do projeto deve incluir o ID do cliente que o criou.
        """
        c = self.conn.cursor()
        cursor = c.execute("INSERT INTO projects VALUES (null, ?, ?, ?, ?)", (project['owner'],
                                                                              project['title'],
                                                                              datetime.now(), datetime.now(),))

        self.conn.commit()
        project_id = cursor.lastrowid

        self.conn.cursor().execute("INSERT INTO users_projects VALUES (?,?)", (project['owner'], project_id),)
        self.conn.commit()
        return self.get_project(project_id)

    def add_task(self, task):
        """
        Adiciona uma nova tarefa.
        """
        res = self.conn.cursor().execute("""SELECT count(*) as "order" FROM tasks WHERE project_id=?""",
                                         (task['project_id'],))
        res = res.fetchone()
        order = int(res['order']) + 1
        cursor = self.conn.cursor().execute("INSERT INTO tasks VALUES (null, ?, ?, ?, ?, ?,?)",
                                            (task['project_id'], order, task['description'], 0, datetime.now(), datetime.now(),))
        self.conn.commit()
        self.conn.cursor().execute("UPDATE projects SET last_update=? WHERE id=?",
                                   (datetime.now(), task['project_id'],))
        self.conn.commit()
        return self.get_task(cursor.lastrowid)

    def add_user_project(self, user_id, project_id):
        """
        Associa um cliente a um projeto
        """
        self.conn.cursor().execute("INSERT INTO users_projects VALUES (?, ?)", (user_id, project_id,))
        self.conn.commit()

    def add_message(self, message):
        """
        Cria uma mensagem
        """
        self.conn.cursor().execute("INSERT INTO messages VALUES (null, ?, ?, ?, ?, ?)",
                                   (message['project_id'], message['sender'], message['username'], message['content'],
                                    datetime.now()))
        self.conn.commit()

    # ADDS - FIM

    # UPDATES
    def update_user(self, user_id, data):
        """
        Atualiza um cliente através dos seus novos dados.
        """

        if 'email' in data:
            self.conn.cursor().execute("UPDATE users SET email=? WHERE id=?", (data['email'], user_id,))
        if 'password' in data:
            self.conn.cursor().execute("UPDATE users SET password=? WHERE id=?", (hash_password(data['password']), user_id,))
        self.conn.commit()
        return self.get_user(user_id)

    def update_project(self, project_id, data):
        """
        Atualiza um projeto através dos seus novos dados.
        """

        self.conn.cursor().execute("UPDATE projects SET title=?, description=?, last_update=? WHERE id = ?"
                                   , (data['title'], datetime.now(), project_id,))
        self.conn.commit()
        return self.get_project(project_id)

    def update_task(self, task_id, data):
        """
        Atualiza uma tarefa com os novos dados.
        Também atualiza a data da última atualização do projeto à qual a tarefa pertence.
        """

        self.conn.cursor().execute("UPDATE tasks SET project_order=?, description=?, status=? WHERE id=?"
                                   , (data['project_order'], data['description'], data['status'], task_id,))
        task = self.get_task(task_id)
        self.conn.cursor().execute("UPDATE projects SET last_update=? WHERE id=?", (datetime.now(), task['project_id'],))
        self.conn.commit()
        return self.get_task(task_id)

    # UPDATES - FIM

    # DELETE
    def remove_user(self, user_id):
        """
        Remove um cliente.
        """

        self.conn.cursor().execute("DELETE FROM users_projects WHERE user_id=?", (user_id,))
        self.conn.cursor().execute("DELETE FROM users WHERE id=?", (user_id,))
        self.conn.commit()

    def remove_project(self, project_id):
        """
        Apaga um projeto.
        """

        self.conn.cursor().execute("DELETE FROM users_projects WHERE project_id=?", (project_id,))
        self.conn.cursor().execute("DELETE FROM tasks WHERE project_id=?", (project_id,))
        self.conn.cursor().execute("DELETE FROM projects WHERE id=?", (project_id,))
        self.conn.commit()

    def remove_task(self, task_id):
        """
        Apaga uma tarefa.
        """

        task = self.get_task(task_id)
        self.conn.cursor().execute("DELETE FROM tasks WHERE id=?", (task_id,))
        self.conn.cursor().execute("UPDATE projects SET last_update=? WHERE id=?",
                                   (datetime.now(), task['project_id'],))
        self.conn.commit()

    def remove_user_project(self, user_id, project_id):
        """
        Apaga uma associação de um cliente a um projeto.
        """

        self.conn.cursor().execute("DELETE FROM users_projects WHERE user_id=? AND project_id=?",
                                   (user_id, project_id,))
        self.conn.commit()

    # DELETE - FIM

    # MISCELLANEOUS FUNCTIONS
    def login(self, user):
        """
        Tenta fazer um login.
        """

        res = self.conn.cursor().execute(
            "SELECT id, password FROM users WHERE username=?", (user['username'],)
        )
        self.conn.commit()
        result = res.fetchone()
        if not result:
            return None
        if len(result) == 0:
            return None
        hashed_password = result['password']
        if check_password(hashed_password, user['password']):
            return result['id']
        return None

    def owner_of_project(self, user_id, project_id):
        """
        Retorna true se o id do cliente for o mesmo que o id do criador do projeto.
        """

        res = self.conn.cursor().execute("SELECT * FROM projects WHERE owner=? AND id=?", (user_id, project_id,))
        result = res.fetchone()
        if not result:
            return False
        return True

    # MISCELLANEOUS FUNCTIONS - FIM
