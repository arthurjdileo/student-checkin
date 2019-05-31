import m from '../modules/mithril.js';
import {navBar, SorTable, formatDate} from '../modules/util.js';
import * as LogMgr from '../services/log-manager.js';
import {GetStudents} from '../services/student-manager.js';

let recentLogs = [];
let students = [];
let logBody = [];
let today = new Date();

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
				tableAttrs: {class: 'big-table is-striped', style: 'display: inline-block;'},
				headers: [
					{label: 'Student Name', key: 'name', attrs: {style: 'width: 250px;'}},
					{label: 'Status', key: 'action', attrs: {style: 'width: 150px;'}}
				],
				backupKeys: ['action'],
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
	return [
		m(navBar),
		m('h3.has-text-centered.has-text-weight-bold', {style: 'margin-top: 15px;'}, 'Logs for the date of ', formatDate(today, false)),
		m('div', {style: 'text-align: center; margin-top: 15px;'},
			m(logTable),
		)
	];
}

export default {oninit, view};
