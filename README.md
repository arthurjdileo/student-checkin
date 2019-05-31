# student-checkin
A web-app made for my high school to record part-time students' check-in and check-out times. Stores data in SQL db. Uses Golang back-end and mithril.js front-end.

## Dependencies
They are all stored in the /vendor/ folder. I am using Go Modules to ensure dependencies are stored in the project itself.

## SQL
The SQL files are stored in /app/mysql/. Please be sure to run the users.sql file first.
```
source users.sql
source logs.sql
```

## Environment Variables
Create an env file with the following environment vars.
```
touch env //create file
chmod a+x env //make it executable
nano env
```
env
```
DATABASE_USER=''
DATABASE_PW=''
DATABASE_NAME='eca'
```

## Running web server
```
./run
```
