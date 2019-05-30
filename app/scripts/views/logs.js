import m from '../modules/mithril.js';
import {navBar, SorTable} from '../modules/util.js';
import * as LogMgr from '../services/log-manager.js';
import {GetStudents} from '../services/student-manager.js';

let recentLogs = [];
let students = [];
let logBody = [];

export async function oninit() {
	recentLogs = await LogMgr.GetRecentLogs();
	students = await GetStudents();
	logBody = LogMgr.getLogBody(recentLogs, students);
	m.redraw();
}

let logTable = {
	view: function(vnode) {
		return [
			m(SorTable, {
				tableAttrs: {class: 'is-striped', style: 'display: inline-block;'},
				headers: [
					{label: 'Student Name', key: 'name', attrs: {style: 'width: 250px;'}},
					{label: 'Status', key: 'action', attrs: {style: 'width: 150px;'}}
				],
				backupKeys: ['name'],
				body: logBody,
				rowMapper(s) {
					return [
						m('td', s.name),
						m('td', s.action)
					];
				}
			})
		];
	}
};

export function view() {
	setInterval(oninit, 1000)
	return [
		m(navBar),
		m('div', {style: 'text-align: center; margin-top: 15px;'},
			m(logTable),
		)
	];
}

export default {oninit, view};
