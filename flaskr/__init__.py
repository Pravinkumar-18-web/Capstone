import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Movie, Actor
from auth.auth import AuthError, requires_auth
from datetime import datetime


"""
Function: create_app
Purpose: Creates and configures the Flask application, including database setup,
         CORS configuration, and error handling.
Parameters:
    - test_config: Optional configuration for testing purposes (default: None).
Returns: The configured Flask app instance.
Setup:
    - Initializes the Flask app.
    - Sets up the database connection, including the test configuration if provided.
    - Configures CORS to allow cross-origin requests from specified origins.
    - Applies middleware for setting CORS headers after every request.
"""

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PUT,POST,DELETE,OPTIONS')
        return response

    
    """
    Root Route
    Path: /
    Method: GET
    Description: Returns a welcome message to the Casting Agency application. 
                 Provides basic information for users accessing the app.
    Response: JSON object with success status and a welcome message.
    """
    @app.route('/')
    def welcome():
        try:
            return jsonify({
                "success": True,
                "message": "Welcome to the Casting Agency Application! Enjoy browsing movies and actors data."
            })
        except Exception as e:
            abort(500, str(e))
            
    """
    Retrieve All Movies
    Path: /movies
    Method: GET
    Authorization: view:movies permission required.
    Description: Retrieves a list of all movies in the database. Each movie is formatted as a 
                 dictionary containing its details.
    Response: JSON object with a success status and a list of movies.

    """
    @app.route('/movies', methods=['GET'])
    @requires_auth('view:movies')
    def retrieve_movies(payload):
        try:
            movies = Movie.query.all()
            movies = list(map(lambda movie: movie.format(), movies))
            return jsonify({
                "success": True,
                "movies": movies
            })
        except Exception as e:
            abort(500, str(e))

    """
    Retrieve All Actors
    Path: /actors
    Method: GET
    Authorization: view:actors permission required.
    Description: Retrieves a list of all actors in the database. Each actor is formatted as a
                 dictionary containing their details.
    Response: JSON object with a success status and a list of actors.
    """
    @app.route('/actors', methods=['GET'])
    @requires_auth('view:actors')
    def retrieve_actors(payload):
        try:
            actors = Actor.query.all()
            actors = list(map(lambda actor: actor.format(), actors))
            return jsonify({
                "success": True,
                "actors": actors
            })
        except Exception as e:
            abort(500, str(e))
    
    """
    Create a New Movie
    Path: /movies
    Method: POST
    Authorization: post:movies permission required.
    Description: Creates a new movie in the database. The request must include the movie's title and release date.
    Request Body: JSON object with title and release_date.
    Response: JSON object with a success status and the created movie's details.
    """
    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movies')
    def create_movie(payload):
        try:
            body = request.get_json()

            if not body:
                abort(400, "Request body is missing")

            title = body.get('title', None)
            release_date = body.get('release_date', None)

            if not title or not release_date:
                abort(400, "Missing fields for movie creation")

            movie = Movie(title=title, release_date=release_date)
            movie.insert()

            return jsonify({
                "success": True,
                "created": movie.format()
            }), 201
        except Exception as e:
            abort(500, str(e))

    """
    Create a New Actor
    Path: /actors
    Method: POST
    Authorization: post:actors permission required.
    Description: Creates a new actor in the database. The request must include the actor's name, age, gender, and
                 associated movie ID.
    Request Body: JSON object with name, age, gender, and movie_id.
    Response: JSON object with a success status and the created actor's details.
    """
    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actors')
    def create_actor(payload):
        try:
            body = request.get_json()

            if not body:
                abort(400, "Request body is missing")

            name = body.get('name', None)
            age = body.get('age', None)
            gender = body.get('gender', None)
            movie_id = body.get('movie_id', None)

            if not all([name, age, gender, movie_id]):
                abort(400, "Missing fields for actor creation")

            actor = Actor(name=name, age=age, gender=gender, movie_id=movie_id)
            actor.insert()

            return jsonify({
                "success": True,
                "created": actor.format()
            }), 201
        except Exception as e:
            abort(500, str(e))

    """
    Delete a Movie
    Path: /movies/<int:movie_id>
    Method: DELETE
    Authorization: delete:movies permission required.
    Description: Deletes a movie from the database based on the provided movie ID.
    Response: JSON object with a success status and the ID of the deleted movie.
    """
    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movie(payload, movie_id):
        try:
            movie = Movie.query.filter(Movie.id == movie_id).one_or_none()

            if not movie:
                abort(404, f"Movie with id {movie_id} not found")

            movie.delete()

            return jsonify({
                "success": True,
                "deleted": movie_id
            })
        except Exception as e:
            abort(500, str(e))

    """
    Delete an Actor
    Path: /actors/<int:actor_id>
    Method: DELETE
    Authorization: delete:actors permission required.
    Description: Deletes an actor from the database based on the provided actor ID.
    Response: JSON object with a success status and the ID of the deleted actor.
    """
    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actor(payload, actor_id):
        try:
            actor = Actor.query.filter(Actor.id == actor_id).one_or_none()

            if not actor:
                abort(404, f"Actor with id {actor_id} not found")

            actor.delete()

            return jsonify({
                "success": True,
                "deleted": actor_id
            })
        except Exception as e:
            abort(500, str(e))

    """
    Update a Movie
    Path: /movies/<int:movie_id>
    Method: PATCH
    Authorization: update:movies permission required.
    Description: Updates the details of an existing movie. The request may include updates 
                 to the title and/or release date.
    Request Body: JSON object with optional title and release_date.
    Response: JSON object with a success status and the updated movie's details.    
    """
    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    @requires_auth('update:movies')
    def update_movie(payload, movie_id):
        try:
            movie = Movie.query.get(movie_id)

            if not movie:
                abort(404, f"Movie with id {movie_id} not found")

            body = request.get_json()

            if not body:
                abort(400, "Request body is missing")

            title = body.get('title', None)
            release_date = body.get('release_date', None)

            if title:
                movie.title = title
            if release_date:
                movie.release_date = release_date

            movie.update()

            return jsonify({
                "success": True,
                "updated": movie.format()
            })
        except Exception as e:
            abort(500, str(e))

    """
    Update an Actor
    Path: /actors/<int:actor_id>
    Method: PATCH
    Authorization: update:actors permission required.
    Description: Updates the details of an existing actor. The request may include updates to 
                 the name, age, gender, and/or associated movie ID.
    Request Body: JSON object with optional name, age, gender, and movie_id.
    Response: JSON object with a success status and the updated actor's details.
    """
    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth('update:actors')
    def update_actor(payload, actor_id):
        try:
            actor = Actor.query.get(actor_id)

            if not actor:
                abort(404, f"Actor with id {actor_id} not found")

            body = request.get_json()

            if not body:
                abort(400, "Request body is missing")

            name = body.get('name', None)
            age = body.get('age', None)
            gender = body.get('gender', None)
            movie_id = body.get('movie_id', None)

            if name:
                actor.name = name
            if age:
                actor.age = age
            if gender:
                actor.gender = gender
            if movie_id:
                actor.movie_id = movie_id

            actor.update()

            return jsonify({
                "success": True,
                "updated": actor.format()
            })
        except Exception as e:
            abort(500, str(e))

    """
    Error Handlers
    400 - Bad Request: Triggered when the request is invalid or missing required data.
    Response: JSON object with an error code (400) and a description of the issue.

    404 - Not Found: Triggered when a resource (movie or actor) is not found in the database.
    Response: JSON object with an error code (404) and a description of the issue.

    422 - Unprocessable Entity: Triggered when the server is unable to process the request.
    Response: JSON object with an error code (422) and a description of the issue.

    500 - Internal Server Error: Triggered for unexpected errors in the application.
    Response: JSON object with an error code (500) and a message describing the issue.

    AuthError: Triggered when there is an authentication or authorization failure.
    Response: JSON object with the relevant error code and description.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": str(error.description)
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": str(error.description)
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": str(error.description)
        }), 422

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "An unexpected error occurred: " + str(error.description)
        }), 500

    @app.errorhandler(AuthError)
    def auth_error(error):
        return jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error['description']
        }), error.status_code

    return app

APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
