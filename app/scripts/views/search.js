import m from '../modules/mithril.js';
import {navBar, inputBox, SorTable, formatDate, actionColor} from '../modules/util.js';
import {GetLogs, idToName} from '../services/log-manager.js';
import {GetStudents} from '../services/student-manager.js';

let logs = [];
let students = [];
let name = ""

export async function submit() {
	let student_id = document.getElementById("student_id").value;
	logs = await GetLogs(student_id);
	students = await GetStudents();
	name = idToName(students, student_id)
	m.redraw();
}

function keyDown(e) {
    if (e.key === 'Enter') {
        submit();
    }
}

let searchTable = {
	view: function() {
		return [
			m('h3.has-text-weight-bold', {style: 'margin-bottom: 10px'}, name),
			m(SorTable, {
				tableAttrs: {class: 'is-striped', style: 'display: inline-block;'},
				headers: [
					{label: 'Date', key: 'created', attrs: {style: 'width: 300px;'}},
					{label: 'Status', key: 'action', choices: [
						{label: 'in', key: 'in'},
						{label: 'out', key: 'out'}
					],
					attrs: {style: 'width: 300px;',
					}},
				],
				backupKeys: ['created'],
				body: logs,
				rowMapper(l) {
					return [
						m('td', formatDate(l.created)),
						m('td', {style: `color: ${actionColor(l.action)}`}, l.action)
					];
				}
			})
		];
	}
}

export function view() {
	return [
		m(navBar),
		m(inputBox, {clickFunc: submit, title: 'Search Student', kd: keyDown}),
		m('div', {style: 'text-align: center; margin-top: 15px;'},
			m(searchTable),
		)
	];
}

export default {view};
