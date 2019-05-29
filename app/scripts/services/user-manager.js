import m from '../modules/mithril.js';

async function request(method, hash, data) {
	if (data === "") {
		await m.request({
			method: method,
			url: window.location.origin + hash
		});
	} else {
		await m.request({
			method: method,
			url: window.location.origin + hash,
			data: data
		});
	}
}

export async function getUsers() {
	return await request('GET', '/v1/users', "")
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
