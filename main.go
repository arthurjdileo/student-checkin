package main

import (
	"net/http"
	"log"
)

func router(w http.ResponseWriter, r *http.Request) {
	log.Println("GET ", r.URL.Path)

	if r.URL.Path == "/index.html" {
		http.Redirect(w, r, "/", http.StatusSeeOther)
		return

	} else if len(r.URL.Path) > 8 && r.URL.Path[:9] == "/scripts/" {
		path := "./www" + r.URL.Path
		http.ServeFile(w, r, path)
		return

	} else if len(r.URL.Path) > 1 && r.URL.Path[0] == '/' {
		// allow misc files like favicon and styles
		http.ServeFile(w, r, "./www"+r.URL.Path)
		return

	}
}

func main() {
	http.HandleFunc("/", router)
	port := "8000"
	bindAddress := ":" + port

	log.Println("hosted on ", bindAddress)
	log.Fatal(http.ListenAndServe(bindAddress, nil))
}