import m from '../modules/mithril.js';
import {navBar} from '../modules/util.js';
import * as LogMgr from '../services/log-manager.js';

let inputBox = {
	view: function(vnode) {
		return [
				m('.hero-body', {style: 'align-items: start;'},
					m('.container.has-text-centered',
						m('div.column.is-4.is-offset-4',
							m('.box',
								m('h3.title', 'Student ID'),
								m('.field',
									m('.control',
										m('input#student_id.input.is-large.is-fullwidth.has-text-centered',
										{type:'number', placeholder:'2019240', autofocus: 'true', onkeydown: (e) => keyDown(e)})
									)
								),
								m('button.button.is-primary.is-block.is-info-.is-large.is-fullwidth', {type: 'button', onclick: vnode.attrs.clickFunc},'Submit'),
							),
						)
					)
				)
		];
	}
}

function keyDown(e) {
	if (e.key === 'Enter') {
		submit();
	}
}

function submit() {
	LogMgr.LogStudent(document.getElementById("student_id").value); 
	document.getElementById("student_id").value = "";
}

export function view() {
	return [
		m(navBar),
		m(inputBox, {clickFunc: submit})
	];
}

export default {view};
