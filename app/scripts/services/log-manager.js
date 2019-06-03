import m from '../modules/mithril.js';
import {request} from '../modules/util.js';

export async function LogStudent(student_id) {
	await request("POST", `/api/logs/${student_id}`, "")
}

export async function GetRecentLogs() {
	let r = await request("GET", "/api/logs", "");
	for (let l of r) {
		l.created = new Date(l.created);
	}
	return r;
}

export async function GetLogs(student_id) {
	let r = await request("GET", `/api/logs/${student_id}`)
	for (let l of r) {
		l.created = new Date(l.created);
	}
	return r;
}

export function idToName(students, student_id) {
	return students.filter(s => s.student_id == student_id)[0].name;
}

export function populate(recentLogs, students) {
	let defaultDate = new Date();
	defaultDate.setHours(8);
	defaultDate.setMinutes(0);
	defaultDate.setSeconds(0);

	for (let s of students) {
		if (recentLogs.find(r => r.student_id === s.student_id) == undefined) {
			recentLogs.push({action: "out", created: defaultDate, name: s.name, student_id: s.student_id})
		}
	}
}
