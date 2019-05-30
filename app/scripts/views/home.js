import m from '../modules/mithril.js';
import {navBar, inputBox} from '../modules/util.js';
import * as LogMgr from '../services/log-manager.js';

function submit() {
	LogMgr.LogStudent(document.getElementById("student_id").value); 
	document.getElementById("student_id").value = "";
}

function keyDown(e) {
    if (e.key === 'Enter') {
        submit();
    }
}

export function view() {
	return [
		m(navBar),
		m(inputBox, {clickFunc: submit, title: 'Student ID', kd: keyDown})
	];
}

export default {view};
