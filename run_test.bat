@echo off
REM Drop the existing database
psql -U postgres -c "DROP DATABASE IF EXISTS capstone_test;"

REM Create a new database
psql -U postgres -c "CREATE DATABASE capstone_test;"

REM Import the SQL file into the new database
psql -U postgres -d capstone_test -f capstone.psql
