from flask_migrate import Migrate
from flask import Flask
from flaskr import create_app
from models import db

# Create the app instance
app = create_app()

# Set up the migration environment
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run()
