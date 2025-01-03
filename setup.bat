@echo off
set AUTH0_DOMAIN=dev-pkprojects.us.auth0.com
set ALGORITHMS=RS256
set API_AUDIENCE=capstone

set DATABASE_URL=postgresql://postgres:1898@localhost:5432/capstone
set DATABASE_URL_Test=postgresql://postgres:1898@localhost:5432/capstone_test
set FLASK_APP=flaskr
set FLASK_DEBUG=True
set FLASK_ENVIRONMENT=debug
