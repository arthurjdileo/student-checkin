import m from '../modules/mithril.js';
import {navBar, SorTable, formatDate, actionColor} from '../modules/util.js';
import * as LogMgr from '../services/log-manager.js';
import {GetStudents} from '../services/student-manager.js';

let recentLogs = [];
let students = [];
let populated = [];
let today = new Date();

export async function oninit() {
	recentLogs = await LogMgr.GetRecentLogs();
	students = await GetStudents();

	// artificially populate logs so that anyone who has not checked in for the day will be shown as "out"
	LogMgr.populate(recentLogs, students)
	m.redraw();
}

let logTable = {
	view: function(vnode) {
		return [
			m(SorTable, {
				tableAttrs: {class: 'big-table is-striped is-centered', style: 'display: inline-block;'},
				headers: [
					{label: 'Student Name', key: 'name', attrs: {style: 'width: 250px;'}},
					{label: 'Status', key: 'action', attrs: {style: 'width: 150px;'}}
				],
				backupKeys: ['action'],
				body: recentLogs,
				rowMapper(s) {
					return [
						m('td', s.name),
						m('td', {style: `color: ${actionColor(s.action)}`},s.action, " ", s.created.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}))
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
