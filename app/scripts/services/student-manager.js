import m from '../modules/mithril.js';

async function request(method, hash, data) {
	if (data === "") {
		return await m.request({
			method: method,
			url: window.location.origin + hash
		});
	} else {
		return await m.request({
			method: method,
			url: window.location.origin + hash,
			data: data
		});
	}
}

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

// export async function SubmitForm(data, edit=false, uuid="") {
// 	if (!edit) {
// 		await m.request({
// 				method: "POST",
// 				url: api.getBaseURL() + "/admin/answerbots",
// 				headers: {
// 					"RKADMINSESSION": cookies.get("RKADMINSESSION")
// 				},
// 				data: data
// 			});
// 	} else if (edit == true && uuid != "") {
// 		await m.request({
// 				method: "POST",
// 				url: api.getBaseURL() + `/admin/answerbots/${uuid}`,
// 				headers: {
// 					"RKADMINSESSION": cookies.get("RKADMINSESSION")
// 				},
// 				data: data
// 			});
// 	} else {
// 		throw "UUID Missing";
// 	}
// }
