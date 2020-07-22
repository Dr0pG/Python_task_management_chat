"""
 Testes Unitários - Diogo Venâncio & André Gonçalves

"""

import json
import unittest

import app


class AppTests(unittest.TestCase):

    def setUp(self):
        app.app.testing = True
        app.app.secret_key = "cd"
        app.db = app.database.DatabaseController('')
        self.app = app.app.test_client()

        self.login('Diogo', '123')

    def login(self, username, password):
        user = {'username': username, 'email': 'diogo@gmail.com', 'password': password}
        return self.app.post('/api/user/login/', data=json.dumps(user),
                             follow_redirects=True, content_type="application/json")

    def add_project(self, name):
        data = json.dumps({'name': name}).encode()
        return self.app.post('/api/projects/', data=data, follow_redirects=True, content_type='application/json')

    def logout(self):
        return self.app.get('/api/user/logout/')

    def test_login_logout(self):
        rv = self.login('Diogo', '123')
        assert 200 == rv.status_code
        rv = self.logout()
        assert 200 == rv.status_code
        rv = self.login('_', '123')
        assert 403 == rv.status_code
        rv = self.login('Diogo', '_')
        assert 403 == rv.status_code

    def test_register(self):
        data = json.dumps({'username': 'test', 'email': 'test@email.com', 'password': 'test'}).encode()
        rv = self.app.post('/api/user/register/', data=data, follow_redirects=True, content_type='application/json')
        assert rv.status_code == 201
        rv = self.app.post('/api/user/register/', data=data, follow_redirects=True, content_type='application/json')
        assert rv.status_code == 409

    def test_access_projects(self):
        rv = self.app.get('/api/projects/')
        assert rv.status_code == 200

    def test_add_project(self):
        rv = self.add_project('test project')
        assert rv.status_code == 201

    def test_delete_project(self):
        rv = self.add_project('delete project')
        project_id = json.loads(rv.data.decode())['id']
        rv = self.app.delete('api/projects/%s' % project_id, follow_redirects=True)
        assert rv.status_code == 200

    def test_access_tasks(self):
        rv = self.add_project('aux project')
        project_id = json.loads(rv.data.decode())['id']
        rv = self.app.get('api/projects/%s/tasks/' % project_id)
        assert rv.status_code == 200

    def test_add_task(self):
        rv = self.add_project('aux project')
        project_id = json.loads(rv.data.decode())['id']
        data = json.dumps({'project_id': int(project_id), 'description': 'test task'}).encode()
        rv = self.app.post('api/projects/%s/tasks/' % project_id, data=data, follow_redirects=True,
                           content_type='application/json')
        assert rv.status_code == 201

    def test_delete_task(self):
        rv = self.add_project('aux project')
        project_id = json.loads(rv.data.decode())['id']
        data = json.dumps({'project_id': int(project_id), 'description': 'test task'}).encode()
        rv = self.app.post('api/projects/%s/tasks/' % project_id, data=data, follow_redirects=True,
                           content_type='application/json')
        task_id = json.loads(rv.data.decode())['id']
        rv = self.app.delete('api/projects/%s/tasks/%s' % (project_id, task_id), follow_redirects=True)
        assert rv.status_code == 200

    def test_access_collaborators(self):
        rv = self.add_project('aux project')
        project_id = json.loads(rv.data.decode())['id']
        rv = self.app.get('api/projects/%s/collaborators/' % project_id)
        assert rv.status_code == 200

    def test_add_collaborator(self):
        rv = self.add_project('aux project')
        project_id = json.loads(rv.data.decode())['id']
        data = json.dumps({'username': 'Andre'}).encode()
        rv = self.app.post('api/projects/%s/collaborators/' % project_id, data=data, follow_redirects=True,
                           content_type='application/json')
        assert rv.status_code == 201

    def test_remove_collaborator(self):
        rv = self.add_project('aux project')
        project_id = json.loads(rv.data.decode())['id']
        data = json.dumps({'username': 'Andre'}).encode()
        rv = self.app.post('api/projects/%s/collaborators/' % project_id, data=data, follow_redirects=True,
                           content_type='application/json')
        collab_id = json.loads(rv.data.decode())['id']
        rv = self.app.delete('api/projects/%s/collaborators/%s/' % (project_id, collab_id), follow_redirects=True)
        assert rv.status_code == 200


if __name__ == '__main__':
    unittest.main()

