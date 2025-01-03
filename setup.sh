#!/bin/sh
export AUTH0_DOMAIN="dev-pkprojects.us.auth0.com"
export ALGORITHMS="RS256"
export API_AUDIENCE="capstone"

export DATABASE_URL="postgresql://postgres:1898@localhost:5432/capstone"
export FLASK_APP=flaskr
export FLASK_DEBUG=True
export FLASK_ENVIRONMENT=debug