import m from '../modules/mithril.js';
import {navBar, CreaTable} from '../modules/util.js';
import {GetStudents, NewStudent, EditStudent} from '../services/student-manager.js';

let students = [];

export async function oninit() {
	students = await GetStudents();
	m.redraw();
}

var UserTable = {
	view: function() {
		return [
		m(CreaTable, {
			tableAttrs: {class: 'is-striped', style: 'display: inline-block;'},
			headers: [
				{label: 'Student Name', key: 'name', attrs: {style: 'width: 250px;'}},
				{label: 'Student ID', key: 'student_id', attrs: {style: 'width: 150px;'}}
			],
			backupKeys: ['name'],
			body: students,
			rowMapper(s) {
				return [
					m('td', s.name),
					m('td', s.student_id)
				];
			},
			editingRowMapper(s) {
				return [
					m('td', m('input.input', {
						placeholder: "Student Name",
						value: s.name,
						oninput(e) {s.name = e.target.value},
						required: true
					})),
					m('td', m('input.input', {
						placeholder: 'Student ID',
						value: s.student_id,
						oninput(e) {s.student_id = e.target.value},
						required: true
					}))
				];
			},
			newRow: {},
			saveNewFunc(newRows) {
				console.log("new: " + JSON.stringify(newRows))
				for (let r of newRows) {
					if (r.editing) {
						alert("Please finishing editing (press the \"Done\" button next to the selected rows) before saving your changes.");
						return;
					}
					NewStudent(r.name, r.student_id);
					m.redraw();
				}
			},
			saveEditedFunc(editedRows) {
				console.log("edited: " + JSON.stringify(editedRows))
				for (let r of editedRows) {
					if (r.editing) {
						alert("Please finishing editing (press the \"Done\" button next to the selected rows) before saving your changes.");
						return;
					}
					EditStudent(r.name, r.student_id, r.id);
					m.redraw();
				}
			}
		})
		];
	}
}

export function view() {
	return [
		m(navBar),
		m('div', {style: 'text-align: center; margin-top: 15px;'},
			m(UserTable),
		)
	];
}

export default {oninit, view};
