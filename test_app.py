import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import db, Movie, Actor



class CapstoneTestCase(unittest.TestCase):
    def setUp(self):
        """Executed before each test."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = os.environ.get('DATABASE_URL_Test', "postgresql://postgres:1898@localhost:5432/capstone_test")
        # setup_db(self.app, self.database_path)
        
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
# Configure the database
        # with self.app.app_context():
        #     # setup_db(self.app, self.database_path)
        #     # db.drop_all()  # Ensure a clean slate before tests
        #     db.create_all()
        # Test data
        self.movie = {
            "title": "Pek Yakında",
            "release_date": "2020-11-02"
        }
        self.actor = {
            "name": "Cem Yılmaz",
            "age": 45,
            "gender": 'M',
            "movie_id": 2
        }

        # Set up authentication tokens info
        with open('auth_config.json', 'r') as f:
            self.auth = json.loads(f.read())

        self.auth_headers = {
            "Casting Assistant": f'Bearer {self.auth["roles"]["Casting Assistant"]["jwt_token"]}',
            "Casting Director": f'Bearer {self.auth["roles"]["Casting Director"]["jwt_token"]}',
            "Executive Producer": f'Bearer {self.auth["roles"]["Executive Producer"]["jwt_token"]}',
        }

        # Bind the app context
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_movies(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }
        res = self.client().get('/movies', headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(type(data["movies"]), type([]))

    def test_get_actors(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }
        res = self.client().get('/actors', headers=header_obj)
        data = json.loads(res.data)
        print(f'{data}')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(type(data["actors"]), type([]))

    def test_get_actors_by_director(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        res = self.client().get('/actors', headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(type(data["actors"]), type([]))

    def test_get_actor_fail_401(self):
        res = self.client().get('/actors')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(type(data["message"]), type(""))

    def test_create_movies(self):
        header_obj = {
            "Authorization": self.auth_headers["Executive Producer"]
        }
        res = self.client().post(f'/movies',
                                 json=self.movie, headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_create_movies_fail_400(self):
        header_obj = {
            "Authorization": self.auth_headers["Executive Producer"]
        }
        movie_fail = {"title": "Movie"}
        res = self.client().post(f'/movies',
                                 json=movie_fail, headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "Missing field for Movie")

    def test_create_movies_fail_403(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        movie_fail = {"title": "Movie"}
        res = self.client().post(f'/movies',
                                 json=movie_fail, headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

    def test_create_actors(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        res = self.client().post(f'/actors',
                                 json=self.actor, headers=header_obj)
        data = json.loads(res.data)
        print(f'{data}')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_create_actors_fail_400(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        actor_fail = {"name": "Actor"}
        res = self.client().post(f'/actors',
                                 json=actor_fail, headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "Missing field for Actor")

    def test_create_actors_fail_403(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }
        actor_fail = {"name": "Actor"}
        res = self.client().post(f'/actors',
                                 json=actor_fail, headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

    # def test_delete_movie(self):
    #     header_obj = {
    #         "Authorization": self.auth_headers["Executive Producer"]
    #     }
    #     delete_id_movie = 4
    #     res = self.client().delete(
    #         f'/movies/{delete_id_movie}',
    #         headers=header_obj)
    #     data = json.loads(res.data)
    #     print(f'{data}')
    #     self.assertEqual(res.status_code, 200)
    #     self.assertTrue(data['success'])
    #     self.assertEqual(data['deleted'], delete_id_movie)

    #     res = self.client().get('/movies', headers=header_obj)
    #     m_data = json.loads(res.data)

    #     found_deleted = False

    #     for m in m_data["movies"]:
    #         if m["id"] == delete_id_movie:
    #             found_deleted = True
    #             break

    #     self.assertFalse(found_deleted)
    def test_delete_movie(self):
        header_obj = {
            "Authorization": self.auth_headers["Executive Producer"]
        }

        # Step 1: Create a movie to delete later
        movie_data = {
            "title": "Test Movie",
            "release_date": "2024-01-01"
        }
        
        # Create the movie
        res = self.client().post('/movies', json=movie_data, headers=header_obj)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()['success'])
        
        # Get the ID of the created movie
        created_movie_id = res.get_json()['movie']['id']

        # Step 2: Delete the movie
        res = self.client().delete(f'/movies/{created_movie_id}', headers=header_obj)
        data = json.loads(res.data)
        print(f'Delete response: {data}')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], created_movie_id)

        # Step 3: Verify the movie has been deleted
        res = self.client().get('/movies', headers=header_obj)
        m_data = json.loads(res.data)

        found_deleted = False
        for m in m_data["movies"]:
            if m["id"] == created_movie_id:
                found_deleted = True
                break

        self.assertFalse(found_deleted)  # Ensure the movie is not found


    def test_delete_movie_fail_404(self):
        header_obj = {
            "Authorization": self.auth_headers["Executive Producer"]
        }
        m_id = 100
        res = self.client().delete(f'/movies/{m_id}', headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_delete_movie_fail_403(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        m_id = 3
        res = self.client().delete(f'/movies/{m_id}', headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

    def test_delete_actor(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        delete_id_actor = 1
        res = self.client().delete(
            f'/actors/{delete_id_actor}',
            headers=header_obj)
        data = json.loads(res.data)
        print(f'{data}')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], delete_id_actor)

        res = self.client().get('/actors', headers=header_obj)
        a_data = json.loads(res.data)
        print(f'{a_data}')

        found_deleted = False

        for a in a_data["actors"]:
            if a["id"] == delete_id_actor:
                found_deleted = True
                break

        self.assertFalse(found_deleted)

    def test_delete_actor_fail_404(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        a_id = -100
        res = self.client().delete(f'/actors/{a_id}', headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_delete_actor_fail_403(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }
        a_id = 100
        res = self.client().delete(f'/actors/{a_id}', headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

    def test_update_movie_CD(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        update_id_movie = 5
        new_title = "Eyvah eyvah 2"
        res = self.client().patch(
            f'/movies/{update_id_movie}',
            json={
                'title': new_title},
            headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['updated']['id'], update_id_movie)
        self.assertEqual(data['updated']['title'], new_title)

    def test_update_movie_EP(self):
        header_obj = {
            "Authorization": self.auth_headers["Executive Producer"]
        }
        update_id_movie = 5
        new_title = "Eyvah eyvah 2"
        res = self.client().patch(
            f'/movies/{update_id_movie}',
            json={
                'title': new_title},
            headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['updated']['id'], update_id_movie)
        self.assertEqual(data['updated']['title'], new_title)

    def test_update_movie_fail_404(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        update_id_movie = -100
        res = self.client().patch(
            f'/movies/{update_id_movie}',
            headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_update_actor(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        update_id_actor = 5
        new_name = "Tom Hanks"
        new_age = 54
        res = self.client().patch(
            f'/actors/{update_id_actor}',
            json={
                'name': new_name,
                'age': new_age},
            headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['updated']['id'], update_id_actor)
        self.assertEqual(data['updated']['name'], new_name)
        self.assertEqual(data['updated']['age'], new_age)

    def test_update_actor_fail_404(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        update_id_actor = 100
        res = self.client().patch(
            f'/actors/{update_id_actor}',
            headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_update_actor_fail_403(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }
        update_id_actor = 100
        res = self.client().patch(
            f'/actors/{update_id_actor}',
            headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()