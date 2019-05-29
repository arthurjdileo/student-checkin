package api

import (
	"database/sql"
	"encoding/json"
	_ "github.com/go-sql-driver/mysql"
	"github.com/gorilla/mux"
	"log"
	"net/http"
	"os"
)

var (
	dbUser     = os.Getenv("DATABASE_USER")
	dbPassword = os.Getenv("DATABASE_PW")
	dbName     = os.Getenv("DATABASE_NAME")
	dbConnStr  = dbUser + ":" + dbPassword + "@/" + dbName
)

func Api() {
	db, err := sql.Open("mysql", dbConnStr)
	if err != nil {
		log.Printf("Cannot connect to db: %s", err)
		return
	}

	r := mux.NewRouter()
	router := r.PathPrefix("v1").Subrouter()

	router.Handle("/users", GetUsers(db)).Methods(http.MethodGet)

	log.Println("api started")
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
