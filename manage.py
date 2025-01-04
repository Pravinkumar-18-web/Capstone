from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask import Flask
from flaskr import create_app
from models import db

# Create the app instance
app = create_app()

# Set up the migration environment
migrate = Migrate(app, db)

# Set up the manager for running the commands
manager = Manager(app)

# Add the database migration commands to the manager
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
