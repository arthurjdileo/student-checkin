import {request} from '../modules/util.js';

export async function GetStudents() {
	let r = await request('GET', '/api/students', "");
	return r;
}

export async function NewStudent(name, student_id) {
	let data = new FormData();
	data.append("name", name);
	data.append("student_id", student_id);
	await request('POST', '/api/students/', data);
}

export async function EditStudent(name, student_id, id) {
	let data = new FormData();
	data.append("name", name);
	data.append("student_id", student_id);
	await request('POST', `/api/students/${id}`, data);
}

export async function DeleteStudent(id, student_id) {
	let data = new FormData();
	data.append("student_id", student_id)
	await request('DELETE', `/api/students/${id}`, data);
}
