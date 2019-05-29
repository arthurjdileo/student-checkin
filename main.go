package main

import (
	api "api.go"
	"log"
	"net/http"

	"github.com/gorilla/mux"
)

const dir = "/"

func main() {
	router := mux.NewRouter().StrictSlash(true)
	router.PathPrefix(dir).Handler(http.StripPrefix(dir, http.FileServer(http.Dir("./app"+dir))))

	port := "8000"
	bindAddress := ":" + port

	srv := &http.Server{
		Addr:    bindAddress,
		Handler: router,
	}

	log.Println("hosted on ", bindAddress)
	log.Fatal(srv.ListenAndServe())
	api.Api()
	log.Println("api started")
}
