package main

import (
	"database/sql"
	"encoding/json"
	_ "github.com/go-sql-driver/mysql"
	"github.com/gorilla/mux"
	"log"
	"net/http"
	"os"
)

import ()

const dir = "/"

var (
	dbUser     = os.Getenv("DATABASE_USER")
	dbPassword = os.Getenv("DATABASE_PW")
	dbName     = os.Getenv("DATABASE_NAME")
	dbConnStr  = dbUser + ":" + dbPassword + "@/" + dbName
)

func main() {
	router := mux.NewRouter().StrictSlash(true)
	db, err := sql.Open("mysql", dbConnStr)
	if err != nil {
		log.Printf("Cannot connect to db: %s", err)
		return
	}
	router.Handle("/api/users/", GetUsers(db)).Methods(http.MethodGet)
	router.Handle("/api/logs/", GetUsers(db)).Methods(http.MethodGet)
	router.PathPrefix(dir).Handler(http.StripPrefix(dir, http.FileServer(http.Dir("./app"+dir))))

	log.Println("api started")

	port := "8000"
	bindAddress := ":" + port

	srv := &http.Server{
		Addr:    bindAddress,
		Handler: router,
	}

	log.Println("hosted on ", bindAddress)
	log.Fatal(srv.ListenAndServe())
}

func GetUsers(db *sql.DB) http.Handler {
	const userQuery string = `
		SELECT JSON_OBJECT(
			'id', users.id,
			'name', users.name,
			'student_id', users.student_id
		)
		FROM
			users
		ORDER BY
			users.id DESC
	`
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {

		rows, err := db.Query(userQuery)
		if err != nil {
			log.Printf("%s", err)
			return
		}
		defer rows.Close()

		jsonRows := make([]json.RawMessage, 0)

		for rows.Next() {
			var jsonRow string

			if err := rows.Scan(&jsonRow); err != nil {
				log.Printf("%s", err)
				return
			}

			raw := json.RawMessage(jsonRow)
			jsonRows = append(jsonRows, raw)
		}

		if err := rows.Err(); err != nil {
			log.Printf("%s", err)
			return
		}

		ret, err := json.Marshal(jsonRows)
		if err != nil {
			log.Printf("%s", err)
			return
		}

		w.Header().Set("Content-type", "application/json")
		w.Write(ret)
	})
}

func GetLogs(db *sql.DB) http.Handler {
	const logQuery string = `
		SELECT JSON_OBJECT(
			'id', logs.id,
			'created', DATE_FORMAT(logs.created, '%Y-%m-%dT%TZ'),
			'student_id', logs.student_id,
			'action', logs.action
		)
		FROM
			logs
		ORDER BY
			logs.created DESC
	`
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {

		rows, err := db.Query(logQuery)
		if err != nil {
			log.Printf("%s", err)
			return
		}
		defer rows.Close()

		jsonRows := make([]json.RawMessage, 0)

		for rows.Next() {
			var jsonRow string

			if err := rows.Scan(&jsonRow); err != nil {
				log.Printf("%s", err)
				return
			}

			raw := json.RawMessage(jsonRow)
			jsonRows = append(jsonRows, raw)
		}

		if err := rows.Err(); err != nil {
			log.Printf("%s", err)
			return
		}

		ret, err := json.Marshal(jsonRows)
		if err != nil {
			log.Printf("%s", err)
			return
		}

		w.Header().Set("Content-type", "application/json")
		w.Write(ret)
	})
}
