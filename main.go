package main

import (
	"database/sql"
	"encoding/json"
	_ "github.com/go-sql-driver/mysql"
	"github.com/gorilla/handlers"
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
	router.Handle("/api/students/", GetStudents(db)).Methods(http.MethodGet)
	router.Handle("/api/logs/", GetLogs(db)).Methods(http.MethodGet)
	router.Handle("/api/students/", NewStudent(db)).Methods(http.MethodPost)
	router.Handle("/api/students/{id}", NewStudent(db)).Methods(http.MethodPost)
	router.PathPrefix(dir).Handler(http.StripPrefix(dir, http.FileServer(http.Dir("./app"+dir))))

	// CORS
	router.Use(handlers.CORS(
		handlers.AllowedOrigins([]string{
			"http://localhost:8000"}),
		handlers.AllowedMethods([]string{
			http.MethodOptions,
			http.MethodPut,
			http.MethodPost,
			http.MethodGet,
			http.MethodDelete,
		})))

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

func GetStudents(db *sql.DB) http.Handler {
	const studentQuery string = `
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
	return dbGetRows(db, studentQuery)
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
	return dbGetRows(db, logQuery)
}

func NewStudent(db *sql.DB) http.Handler {
	const newStudentQuery string = `
		INSERT INTO users (name, student_id)
		VALUES (?, ?)
	`
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		r.ParseMultipartForm(1024)

		name := r.FormValue("name")
		student_id := r.FormValue("student_id")

		_, err := db.Exec(newStudentQuery, name, student_id)
		if err != nil {
			log.Printf("%s", err)
			sendErrorResponse(w, http.StatusInternalServerError, err.Error())
			return
		}
	})
}

func EditStudent(db *sql.DB) http.Handler {
	const editStudentQuery string = `
		UPDATE users SET name = ?, student_id = ?
		WHERE id = ?
	`
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		r.ParseMultipartForm(1024)

		vars := mux.Vars(r)
		name := r.FormValue("name")
		student_id := r.FormValue("student_id")
		id := vars["id"]
		log.Println(id)

		_, err := db.Exec(editStudentQuery, name, student_id, id)
		if err != nil {
			log.Printf("%s", err)
			sendErrorResponse(w, http.StatusInternalServerError, err.Error())
			return
		}
	})
}

func dbGetRows(db *sql.DB, query string) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {

		rows, err := db.Query(query)
		if err != nil {
			log.Printf("%s", err)
			sendErrorResponse(w, http.StatusInternalServerError, err.Error())
			return
		}
		defer rows.Close()

		jsonRows := make([]json.RawMessage, 0)

		for rows.Next() {
			var jsonRow string

			if err := rows.Scan(&jsonRow); err != nil {
				log.Printf("%s", err)
				sendErrorResponse(w, http.StatusInternalServerError, err.Error())
				return
			}

			raw := json.RawMessage(jsonRow)
			jsonRows = append(jsonRows, raw)
		}

		if err := rows.Err(); err != nil {
			log.Printf("%s", err)
			sendErrorResponse(w, http.StatusInternalServerError, err.Error())
			return
		}

		ret, err := json.Marshal(jsonRows)
		if err != nil {
			log.Printf("%s", err)
			sendErrorResponse(w, http.StatusInternalServerError, err.Error())
			return
		}

		w.Header().Set("Content-type", "application/json")
		w.Write(ret)
	})
}

type response struct {
	Status  string      `json:"status"`
	Message string      `json:"message"`
	Error   string      `json:"error"`
	Data    interface{} `json:"data"`
}

func sendErrorResponse(w http.ResponseWriter, httpStatus int, message string) {
	response := &response{
		Status:  "failure",
		Message: "An error has occured",
		Error:   message,
		Data:    struct{}{},
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(httpStatus)
	writeJsonResponse(w, response)
}

func writeJsonResponse(w http.ResponseWriter, response interface{}) {
	jsonResponse, err := json.Marshal(response)
	if err != nil {
		log.Printf("cannot encode JSON response: %s", err.Error())
		sendInternalErrorResponse(w)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.Write(jsonResponse)
}

func sendInternalErrorResponse(w http.ResponseWriter) {
	w.Header().Set("Content-Type", "application/json")
	http.Error(w, `{"status":500,"message":"ERROR","error":"Internal server error"}`, 500)
}
