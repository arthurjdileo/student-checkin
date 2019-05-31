USE eca;

CREATE TABLE logs (
	id int(11) AUTO_INCREMENT PRIMARY KEY,
	created timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
	student_id int(7) NOT NULL,
	action varchar(3) NOT NULL,
	FOREIGN KEY (student_id) REFERENCES users(student_id)
);
