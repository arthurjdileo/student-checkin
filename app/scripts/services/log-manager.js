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

export function getLogBody(recentLogs, students) {
	let logBody = [];
	for (let s of students) {
		let tempObj = {}
		tempObj.name = s.name;
		tempObj.student_id = s.student_id;
		for (let l of recentLogs) {
			if (l.student_id == tempObj.student_id) {
				tempObj.action = l.action;
				tempObj.created = l.created;
				continue;
			}
		}
		logBody.push(tempObj);
	}
	return logBody;
}

export function idToName(students, student_id) {
	return students.filter(s => s.student_id == student_id)[0].name;
}
