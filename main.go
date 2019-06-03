package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"
	"os"

	_ "github.com/go-sql-driver/mysql"
	"github.com/gorilla/mux"
)

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

	err = db.Ping()
	if err != nil {
		log.Printf("Cannot connect to db: %s", err)
		return
	}

	router.Handle("/api/students/", GetStudents(db)).Methods(http.MethodGet)
	router.Handle("/api/students/", NewStudent(db)).Methods(http.MethodPost)
	router.Handle("/api/students/{id}", EditStudent(db)).Methods(http.MethodPost)
	router.Handle("/api/students/{id}", DeleteStudent(db)).Methods(http.MethodDelete)
	router.Handle("/api/logs/{student_id}", LogStudent(db)).Methods(http.MethodPost)
	router.Handle("/api/logs/{student_id}", GetLogs(db)).Methods(http.MethodGet)
	router.Handle("/api/logs/", GetRecentLogs(db)).Methods(http.MethodGet)
	router.PathPrefix(dir).Handler(http.StripPrefix(dir, http.FileServer(http.Dir("./app"+dir))))

	log.Println("api started")

	bindAddress := ":" + "8000"

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
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		dbGetRows(w, r, db, studentQuery)
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
		WHERE
			student_id = ?
		ORDER BY
			logs.created DESC
	`
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)
		student_id := vars["student_id"]

		dbGetRows(w, r, db, logQuery, student_id)
	})
}

func GetRecentLogs(db *sql.DB) http.Handler {
	const recentLogQuery string = `
	SELECT JSON_OBJECT(
			'id', a.id,
			'created', DATE_FORMAT(a.created, '%Y-%m-%dT%TZ'),
			'student_id', a.student_id,
			'action', a.action
		)
	FROM 
		logs a
	LEFT OUTER JOIN 
		logs b
	ON
		a.student_id = b.student_id AND a.created < b.created
	WHERE 
		b.student_id IS NULL
	ORDER BY 
		a.created desc;
	`
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {

		dbGetRows(w, r, db, recentLogQuery)
	})
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

		_, err := db.Exec(editStudentQuery, name, student_id, id)
		if err != nil {
			log.Printf("%s", err)
			sendErrorResponse(w, http.StatusInternalServerError, err.Error())
			return
		}
	})
}

func DeleteStudent(db *sql.DB) http.Handler {
	const delStudentQuery string = `
		DELETE FROM users 
		WHERE id = ?
	`
	const delStudentQuery2 string = `
		DELETE FROM logs
		WHERE student_id = ?
	`
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		r.ParseMultipartForm(1024)

		vars := mux.Vars(r)
		id := vars["id"]
		student_id := r.FormValue("student_id")

		// creating a tx just in case something goes wrong, we can roll back the destructive changes
		tx, err := db.Begin()
		if err != nil {
			log.Printf("%s", err)
			sendErrorResponse(w, http.StatusInternalServerError, err.Error())
			return
		}

		_, err = db.Exec(delStudentQuery2, student_id)
		if err != nil {
			tx.Rollback()
			log.Printf("%s", err)
			sendErrorResponse(w, http.StatusInternalServerError, err.Error())
			return
		}

		_, err = db.Exec(delStudentQuery, id)
		if err != nil {
			tx.Rollback()
			log.Printf("%s", err)
			sendErrorResponse(w, http.StatusInternalServerError, err.Error())
			return
		}

		err = tx.Commit()
		if err != nil {
			log.Printf("%s", err)
			sendErrorResponse(w, http.StatusInternalServerError, err.Error())
			return
		}
	})
}

func LogStudent(db *sql.DB) http.Handler {
	const lastLogQuery string = `
		SELECT action FROM logs WHERE DATE(created)=DATE(NOW()) AND student_id = ? ORDER BY created DESC LIMIT 1;
	`
	const logQuery string = `
		INSERT INTO logs (student_id, action) VALUES (?, ?)
	`
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)
		student_id := vars["student_id"]
		var curAction string
		var nextAction string

		err := db.QueryRow(lastLogQuery, student_id).Scan(&curAction)
		switch {
		case err == sql.ErrNoRows:
			curAction = ""
			nextAction = "in"
		case err != nil:
			log.Printf("%s", err)
			sendErrorResponse(w, http.StatusInternalServerError, err.Error())
			return
		default:
			if curAction == "in" {
				nextAction = "out"
			} else if curAction == "out" {
				nextAction = "in"
			}
		}
		
		_, err = db.Exec(logQuery, student_id, nextAction)
		if err != nil {
			log.Printf("%s", err)
			sendErrorResponse(w, http.StatusInternalServerError, err.Error())
			return
		}
	})
}

func dbGetRows(w http.ResponseWriter, r *http.Request, db *sql.DB, query string, args ...interface{}) {

	rows, err := db.Query(query, args...)
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
